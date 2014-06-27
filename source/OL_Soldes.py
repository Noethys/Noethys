#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import decimal
import GestionDB
import UTILS_Titulaires
from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import UTILS_Utilisateurs
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter

try: import psyco; psyco.full()
except: pass



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

# ----------------------------------------------------------------------------------------------------------------------------------------

def Importation(date=None, afficherDebit=True, afficherCredit=True, afficherNul=True):
    DB = GestionDB.DB()    
    # Récupère les comptes payeurs
    req = """SELECT IDcompte_payeur, IDfamille
    FROM comptes_payeurs
    ORDER BY IDcompte_payeur
    ;"""
    DB.ExecuterReq(req)
    listeComptes = DB.ResultatReq()
    
    # Récupère la ventilation
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_ventilations
    FROM ventilation
    GROUP BY IDcompte_payeur
    ORDER BY IDcompte_payeur
    ;"""
    DB.ExecuterReq(req)
    listeVentilations = DB.ResultatReq()
    dictVentilations = {}
    for IDcompte_payeur, total_ventilations in listeVentilations :
        dictVentilations[IDcompte_payeur] = total_ventilations
    
    # Récupère les prestations
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_prestations
    FROM prestations
    WHERE date<='%s'
    GROUP BY IDcompte_payeur
    ORDER BY IDcompte_payeur
    ;""" % date
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    dictPrestations = {}
    for IDcompte_payeur, total_prestations in listePrestations :
        dictPrestations[IDcompte_payeur] = total_prestations
        
    # Récupère les règlements
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_reglements
    FROM reglements
    WHERE date<='%s'
    GROUP BY IDcompte_payeur
    ORDER BY IDcompte_payeur
    ;""" % date
    DB.ExecuterReq(req)
    listeReglements = DB.ResultatReq()
    dictReglements = {}
    for IDcompte_payeur, total_reglements in listeReglements :
        dictReglements[IDcompte_payeur] = total_reglements
    
    DB.Close()
    
    # Récupération des titulaires de familles
    dictTitulaires = UTILS_Titulaires.GetTitulaires() 
    
    # Traitement des données
    listeListeView = []
    for IDcompte_payeur, IDfamille in listeComptes :
        if dictVentilations.has_key(IDcompte_payeur) :
            total_ventilations = FloatToDecimal(dictVentilations[IDcompte_payeur])
        else:
            total_ventilations = FloatToDecimal(0.0)
        if dictPrestations.has_key(IDcompte_payeur) :
            total_prestations = FloatToDecimal(dictPrestations[IDcompte_payeur])
        else:
            total_prestations = FloatToDecimal(0.0)
        if dictReglements.has_key(IDcompte_payeur) :
            total_reglements = FloatToDecimal(dictReglements[IDcompte_payeur])
        else:
            total_reglements = FloatToDecimal(0.0)
        # Calculs
        solde = total_reglements - total_prestations
        total_a_ventiler = min(total_reglements, total_prestations)
        reste_a_ventiler = total_a_ventiler - total_ventilations
        
        # Mémorisation
        item = {"IDcompte_payeur" : IDcompte_payeur, "IDfamille" : IDfamille, 
                    "total_ventilations" : total_ventilations, "total_reglements" : total_reglements,
                    "total_prestations" : total_prestations, "solde" : solde, 
                    "total_a_ventiler" : total_a_ventiler, "reste_a_ventiler" : reste_a_ventiler}
        track = Track(dictTitulaires, item)
        
        valide = False
        if afficherDebit == True and solde < FloatToDecimal(0.0) :
            valide = True
        if afficherCredit == True and solde > FloatToDecimal(0.0) :
            valide = True
        if afficherNul == True and solde == FloatToDecimal(0.0) :
            valide = True
        if valide == True :
            listeListeView.append(track)
            
    return listeListeView
                
                
class Track(object):
    def __init__(self, dictTitulaires, donnees):
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.IDfamille = donnees["IDfamille"]
        self.total_ventilations = donnees["total_ventilations"]
        self.total_reglements = donnees["total_reglements"]
        self.total_prestations = donnees["total_prestations"]
        self.solde = donnees["solde"]
        self.total_a_ventiler = donnees["total_a_ventiler"]
        self.reste_a_ventiler = donnees["reste_a_ventiler"]

        if dictTitulaires.has_key(self.IDfamille) :
            self.nomsTitulaires =  dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else:
            self.nomsTitulaires = u"Sans titulaires"

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.date = None
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.InitObjectListView()

    def OnItemActivated(self,event):
        self.OuvrirFicheFamille(None)
                
    def InitModel(self, date=None, afficherDebit=True, afficherCredit=True, afficherNul=True):
        self.donnees = Importation(date, afficherDebit, afficherCredit, afficherNul)
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        self.imgVentilation = self.AddNamedImages("ventilation", wx.Bitmap("Images/16x16/Attention.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageVentilation(track):
            if track.reste_a_ventiler > FloatToDecimal(0.0) :
                return self.imgVentilation

        def FormateMontant(montant):
            if montant == None or montant == FloatToDecimal(0.0) : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateSolde(montant):
            if montant == None :
                return u""
            if montant == 0.0 : 
                return u"%.2f %s" % (montant, SYMBOLE)
            if montant > FloatToDecimal(0.0) :
                return u"+ %.2f %s" % (montant, SYMBOLE)
            if montant < FloatToDecimal(0.0) :
                return u"- %.2f %s" % (-montant, SYMBOLE)
        
        liste_Colonnes = [
            ColumnDefn(u"IDfamille", "left", 0, "IDfamille"),
            ColumnDefn(u"Famille", 'left', 300, "nomsTitulaires"),
            ColumnDefn(u"Solde", 'right', 110, "solde", stringConverter=FormateSolde),
            ColumnDefn(u"Prestations", 'right', 110, "total_prestations", stringConverter=FormateMontant),
            ColumnDefn(u"Règlements", 'right', 110, "total_reglements", stringConverter=FormateMontant),
##            ColumnDefn(u"Ventilé", 'right', 80, "total_ventilations", stringConverter=FormateMontant),
##            ColumnDefn(u"A ventiler", 'right', 80, "reste_a_ventiler", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun solde")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(1)
        
    def MAJ(self, date=None, afficherDebit=True, afficherCredit=True, afficherNul=True):
        self.date = date
        self.InitModel(date, afficherDebit, afficherCredit, afficherNul)
        self.SetObjects(self.donnees)

    def DefileDernier(self):
        """ Defile jusqu'au dernier item de la liste """
        if len(self.GetObjects()) > 0 :
            dernierTrack = self.GetObjects()[-1]
            index = self.GetIndexOf(dernierTrack)
            self.EnsureCellVisible(index, 0)

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, u"Ouvrir la fiche famille")
        bmp = wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        
        menuPop.AppendSeparator()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def GetDateStr(self):
        if self.date == None :
            return ""
        else :
            return u"> Situation au %s." % DateEngFr(str(self.date))
        
    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des soldes", intro=self.GetDateStr() , format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des soldes", intro=self.GetDateStr() , format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune fiche famille à ouvrir !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des soldes", autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des soldes", autoriseSelections=False)


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_soldes
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
