#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


        
class Track(object):
    def __init__(self, donnees):
        self.IDdeduction = donnees["IDdeduction"]
        self.IDprestation = donnees["IDprestation"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.date = donnees["date"]
        self.montant = donnees["montant"]
        self.label = donnees["label"]
        self.IDaide = donnees["IDaide"]
        self.nomIndividu= donnees["nomIndividu"]
        self.prenomIndividu = donnees["prenomIndividu"]
        self.labelPrestation = donnees["labelPrestation"]
        self.montantPrestation = donnees["montantPrestation"]
        self.montantInitialPrestation = donnees["montantInitialPrestation"]
        if self.labelPrestation != None and self.montantPrestation != None and self.montantInitialPrestation != None :
            self.textePrestation = _(u"%s (initial : %.2f %s - final : %.2f %s)") % (self.labelPrestation, self.montantInitialPrestation, SYMBOLE, self.montantPrestation, SYMBOLE)
        else:
            self.textePrestation = u""
        
        self.etat = donnees["etat"]
                        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDaide = kwds.pop("IDaide", None)
        self.modificationsVirtuelles = kwds.pop("modificationsVirtuelles", True)
        self.dictDeductions = self.Importation_deductions() 
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.prochainIDdeduction = -1
        self.init = True
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        # Modification 
        self.Modifier(None)
                
    def InitModel(self):
        if self.modificationsVirtuelles == False or self.init == True:
            self.dictDeductions = self.Importation_deductions() 
        self.init = False
        self.donnees = self.GetTracks()
    
    def Importation_deductions(self):
        dictDeductions = {}
        db = GestionDB.DB()
        req = """SELECT 
        IDdeduction, deductions.IDprestation, deductions.IDcompte_payeur, deductions.date, deductions.montant, deductions.label, IDaide, 
        individus.nom, individus.prenom, prestations.label, prestations.montant, prestations.montant_initial
        FROM deductions
        LEFT JOIN prestations ON prestations.IDprestation = deductions.IDprestation
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE IDaide=%d
        """ % self.IDaide
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close() 
        for IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide, nomIndividu, prenomIndividu, labelPrestation, montantPrestation, montantInitialPrestation in listeDonnees :
            date = DateEngEnDateDD(date)
            dictTemp = {
                "IDdeduction" : IDdeduction, "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, 
                "date" : date, "montant" : montant, "label" : label, "IDaide" : IDaide, 
                "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu, 
                "labelPrestation" : labelPrestation, "montantPrestation" : montantPrestation, "montantInitialPrestation" : montantInitialPrestation,
                "etat" : None
                }
            dictDeductions[IDdeduction] = dictTemp
        return dictDeductions

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        listeListeView = []
        for IDdeduction, item in self.dictDeductions.iteritems() :
            valide = True
            
            if item["etat"] == "SUPPR" : valide = False
            
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == IDdeduction :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDateLong(dateDD):
            return DateComplete(dateDD)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDdeduction", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'centre', 160, "date", typeDonnee="date", stringConverter=FormateDateLong), 
            ColumnDefn(_(u"Individu"), 'centre', 90, "prenomIndividu", typeDonnee="texte"), 
            ColumnDefn(_(u"Montant"), 'centre', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant), 
            ColumnDefn(_(u"Label"), 'left', 160, "label", typeDonnee="texte"),
            ColumnDefn(_(u"Prestation"), 'left', 300, "textePrestation", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune déduction"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        if ID == None :
            self.DefileDernier() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDdeduction
                
        # Création du menu contextuel
        menuPop = wx.Menu()

##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
##        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
##            
##        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des déductions"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des déductions"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune déduction à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdeduction = self.Selection()[0].IDdeduction
        label = self.Selection()[0].label
        montant = self.Selection()[0].montant
        IDprestation = self.Selection()[0].IDprestation
        
        import DLG_Saisie_deduction
        dlg = DLG_Saisie_deduction.Dialog(self, IDdeduction=IDdeduction)
        dlg.SetLabel(label)
        dlg.SetMontant(montant)
        if dlg.ShowModal() == wx.ID_OK:
            newLabel = dlg.GetLabel()
            newMontant = dlg.GetMontant()
            if self.modificationsVirtuelles == False :
                # Modification directes dans la base de données
                DB = GestionDB.DB()
                listeDonnees = [    
                    ("label", newLabel),
                    ("montant", newMontant),
                    ]
                DB.ReqMAJ("deductions", listeDonnees, "IDdeduction", IDdeduction)
                DB.Close()
            else:
                # Modifications virtuelles
                self.dictDeductions[IDdeduction]["label"] = newLabel
                self.dictDeductions[IDdeduction]["montant"] = newMontant
                self.dictDeductions[IDdeduction]["etat"] = "MODIF"
            
            # MAJ du montant de la prestation
            self.MAJ_montant_prestation(montant-newMontant, IDprestation)
            
        dlg.Destroy() 
        
        # MAJ du contrôle
        self.MAJ(IDdeduction)

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune déduction à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdeduction = self.Selection()[0].IDdeduction
        montant = self.Selection()[0].montant
        IDprestation = self.Selection()[0].IDprestation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette déduction ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            if self.modificationsVirtuelles == False :
                # Suppression dans la base de données
                DB = GestionDB.DB()
                DB.ReqDEL("deductions", "IDdeduction", IDdeduction)
                DB.Close() 
            else:
                # Suppression virtuelle
                self.dictDeductions[IDdeduction]["etat"] = "SUPPR"
            self.MAJ()
            # MAJ du montant de la prestation
            self.MAJ_montant_prestation(montant, IDprestation)
        dlg.Destroy()
    
    def MAJ_montant_prestation(self, montantDiff, IDprestation=None):
        """ Modification du montant dans la DLG_Saisie_prestation """
        if self.GetParent().GetName() == "DLG_Saisie_prestation" :
            ctrl_montant = self.GetParent().ctrl_montant
            montantPrestation = ctrl_montant.GetMontant() 
            montantPrestation += montantDiff
            ctrl_montant.SetMontant(montantPrestation)
        # Modification directe dans la base de données
        if self.modificationsVirtuelles == False and IDprestation != None :
            DB = GestionDB.DB()
            req = """SELECT montant
            FROM prestations
            WHERE IDprestation=%d
            """ % IDprestation
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) == 0 : return
            montantPrestation = listeDonnees[0][0]
            montantPrestation += montantDiff
            DB.ReqMAJ("prestations", [("montant", montantPrestation),], "IDprestation", IDprestation)
            DB.Close() 
    
    def GetTotalDeductions(self):
        """ Est utilisée par la DLG_Saisie_prestation pour connaître le montant total des déductions """
        total = 0.0
        for IDdeduction, dictDeduction in self.dictDeductions.iteritems() :
            total += dictDeduction["montant"]
        return total
        
    
    def Sauvegarde(self, IDprestation=None):
        """ Effectue une sauvegarde des données SI on est en mode MODIFICATIONS VIRTUELLES """
        DB = GestionDB.DB()
        
        for IDdeduction, dictDeduction in self.dictDeductions.iteritems() :
            IDcompte_payeur = dictDeduction["IDcompte_payeur"]
            date = dictDeduction["date"]
            label = dictDeduction["label"]
            montant = dictDeduction["montant"]
            IDaide = dictDeduction["IDaide"]
            
            listeDonnees = [    
                    ("IDprestation", IDprestation),
                    ("IDcompte_payeur", IDcompte_payeur),
                    ("date", date ),
                    ("label", label),
                    ("montant", montant),
                    ("IDaide", IDaide),
                    ]
                    
            # Ajout
            if dictDeduction["etat"] == "AJOUT" :
                IDdeduction = DB.ReqInsert("deductions", listeDonnees)
            
            # Modification
            if dictDeduction["etat"] == "MODIF" :
                DB.ReqMAJ("deductions", listeDonnees, "IDdeduction", IDdeduction)
            
            # Suppression
            if dictDeduction["etat"] == "SUPPR" :
                DB.ReqDEL("deductions", "IDdeduction", IDdeduction)
        
        DB.Close()


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une déduction..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
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
        self.myOlv = ListView(panel, id=-1, IDaide=2, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
