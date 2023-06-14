#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import sys
import datetime
import GestionDB
import decimal

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")
from Utils import UTILS_Utilisateurs

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils




def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


        
class Track(object):
    def __init__(self, dictDonnee):
        self.valeur = dictDonnee["valeur"]
        self.label = dictDonnee["label"]
        self.typeValeur = dictDonnee["typeValeur"]
        self.position = dictDonnee["position"]
        self.afficher = dictDonnee["afficher"]

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dictDonnees = {}
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
##        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
##        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
##        
##    def OnItemActivated(self,event):
##        self.OuvrirFicheFamille(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        listeID = None
        DB = GestionDB.DB()

        # Pr�paration du dict de donn�es
        self.dictDonnees = {
            "nbrePrestations" : { "valeur" : 0, "label" : _(u"Nbre prestations"), "typeValeur" : "entier", "position" : 10, "afficher" : False } ,
            "totalPrestations" : { "valeur" : decimal.Decimal(str("0.0")), "label" : _(u"Total prestations"), "typeValeur" : "montant", "position" : 20, "afficher" : True } ,
            "totalVentilation" : { "valeur" : decimal.Decimal(str("0.0")), "label" : _(u"Total ventil�"), "typeValeur" : "montant", "position" : 30, "afficher" : True } ,
            "nbreReglements" : { "valeur" : 0, "label" : _(u"Nbre r�glements"), "typeValeur" : "entier", "position" : 40, "afficher" : False } ,
            "totalReglements" : { "valeur" : decimal.Decimal(str("0.0")), "label" : _(u"Total r�glements"), "typeValeur" : "montant", "position" : 50, "afficher" : True } ,
            "soldeJour" : { "valeur" : decimal.Decimal(str("0.0")), "label" : _(u"Solde du jour"), "typeValeur" : "montant", "position" : 60, "afficher" : True } ,
            "soldeFinal" : { "valeur" : decimal.Decimal(str("0.0")), "label" : _(u"Solde final"), "typeValeur" : "montant", "position" : 70, "afficher" : True } ,
            }

        # R�cup�re la ventilation
        req = """SELECT IDprestation, montant
        FROM ventilation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur
        WHERE IDfamille=%d
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeVentilations = DB.ResultatReq()
        dictVentilations = {}
        for IDprestation, montant in listeVentilations :
            if (IDprestation in dictVentilations) == False :
                dictVentilations[IDprestation] = 0.0
            dictVentilations[IDprestation] += montant

        # R�cup�ration des prestations
        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, date, 
        prestations.montant, IDfacture
        FROM prestations
        WHERE IDfamille=%d
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        for IDprestation, IDcompte_payeur, date, montant, IDfacture in listePrestations :
            date = DateEngEnDateDD(date) 
            if IDprestation in dictVentilations :
                montant_ventilation = decimal.Decimal(str(dictVentilations[IDprestation]))
            else :
                montant_ventilation = decimal.Decimal(0.0)
            
            if montant == None : montant = 0.0
            montant = decimal.Decimal(str(montant))
            
            self.dictDonnees["nbrePrestations"]["valeur"] += 1
            self.dictDonnees["totalPrestations"]["valeur"] += montant
            self.dictDonnees["totalVentilation"]["valeur"] += montant_ventilation
            self.dictDonnees["soldeFinal"]["valeur"] += montant
            if date <= datetime.date.today() :
                self.dictDonnees["soldeJour"]["valeur"] += montant
                        
        # R�cup�re les r�glements
        req = """SELECT IDreglement, date, montant
        FROM reglements
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        WHERE comptes_payeurs.IDfamille=%d
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()
        for IDreglement, date, montant in listeReglements :
            date = DateEngEnDateDD(date) 
            self.dictDonnees["nbreReglements"]["valeur"] += 1
            self.dictDonnees["totalReglements"]["valeur"] += decimal.Decimal(str(montant or 0.0))
        
        # Calcul des soldes
        self.dictDonnees["soldeFinal"]["valeur"] = self.dictDonnees["totalReglements"]["valeur"] - self.dictDonnees["soldeFinal"]["valeur"]
        self.dictDonnees["soldeJour"]["valeur"] = self.dictDonnees["totalReglements"]["valeur"] - self.dictDonnees["soldeJour"]["valeur"] 
        
        DB.Close()
        
        # Traitement des donn�es
        listeListeView = []
        for code, dictDonnee in self.dictDonnees.items()  :
            if dictDonnee["afficher"] == True :
                track = Track(dictDonnee)
                listeListeView.append(track)

        return listeListeView
    
    def GetSolde(self):
        if "soldeFinal" in self.dictDonnees :
            solde = self.dictDonnees["soldeFinal"]["valeur"]
            return solde
        else:
            return decimal.Decimal(str("0.0"))
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        def FormateValeur(valeur):
            if type(valeur) == int :
                # Si c'est un nombre :
                return valeur
            if type(valeur) == decimal.Decimal :
                # Si c'est un montant
                if valeur > decimal.Decimal(str("0.0")) :
                    return u"+ %.2f %s" % (valeur, SYMBOLE)
                elif valeur == decimal.Decimal(str("0.0")) :
                    return u"0.00 %s" % SYMBOLE
                else:
                    return u"- %.2f %s" % (-valeur, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"Label"), "left", 115, "label"),
            ColumnDefn(_(u"Valeur"), 'right', 80, "valeur", stringConverter=FormateValeur), #, isSpaceFilling=True),
            ]
        
        if "linux" not in sys.platform :
            liste_Colonnes.insert(0, ColumnDefn(u"", "left", 0, "position"))
            
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune facturation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[0])
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
        # S�lection d'un item
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
            ID = self.Selection()[0].IDfamille
                
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir cette fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
    
        # G�n�ration automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des ventilations"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune fiche famille � ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDfamille)
        dlg.Destroy()




# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un r�glement..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
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
        self.myOlv = ListView(panel, id=-1, IDfamille=14, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    print("Temps de chargement OL_Etat_compte =", time.time() - heure_debut)
    frame_1.Show()
    app.MainLoop()
