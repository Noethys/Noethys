#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Dlg import DLG_Saisie_ventilation_operation
from Utils import UTILS_Dates

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter


class Track(object):
    def __init__(self, donnees):
        self.IDventilation = donnees["IDventilation"]
        self.date_budget = donnees["date_budget"]
        self.IDcategorie = donnees["IDcategorie"]
        self.IDanalytique = donnees["IDanalytique"]
        self.libelle = donnees["libelle"]
        self.montant = donnees["montant"]
        
        self.dictExercices = {}
        self.dictCategories = {}
        self.dictAnalytiques = {}
    
    def MAJ(self):            
        if self.dictCategories.has_key(self.IDcategorie) :
            self.label_categorie = self.dictCategories[self.IDcategorie]
        else :
            self.label_categorie = _(u"Catégorie inconnue")
            
        if self.dictAnalytiques.has_key(self.IDanalytique) :
            self.label_analytique = self.dictAnalytiques[self.IDanalytique]
        else :
            self.label_analytique = _(u"Code analytique inconnu")
            

def Importation(IDoperation=None):
    DB = GestionDB.DB()
    req = """SELECT IDventilation, date_budget, IDcategorie, IDanalytique, libelle, montant
    FROM compta_ventilation 
    WHERE IDoperation=%d;""" % IDoperation
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeTracks = []
    for IDventilation, date_budget, IDcategorie, IDanalytique, libelle, montant in listeDonnees :
        date_budget = UTILS_Dates.DateEngEnDateDD(date_budget)
        dictTemp = {
            "IDventilation" : IDventilation, "date_budget" : date_budget, "IDcategorie" : IDcategorie, 
            "IDanalytique" : IDanalytique, "libelle" : libelle, "montant" : montant, 
            }
        track = Track(dictTemp)
        listeTracks.append(track)
    return listeTracks


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.typeOperation = kwds.pop("typeOperation", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.listeTracks = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def SetTracks(self, tracks=[]):
        self.listeTracks = tracks
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        DB = GestionDB.DB()
                
        # Importation des catégories
        req = """SELECT IDcategorie, nom
        FROM compta_categories ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictCategories = {}
        for IDcategorie, nom in listeDonnees :
            self.dictCategories[IDcategorie] = nom
        
        # Importation des codes analytiques
        req = """SELECT IDanalytique, nom
        FROM compta_analytiques ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictAnalytiques = {}
        for IDanalytique, nom in listeDonnees :
            self.dictAnalytiques[IDanalytique] = nom
        
        DB.Close()

        for track in self.listeTracks :
            track.dictCategories = self.dictCategories
            track.dictAnalytiques = self.dictAnalytiques
            track.MAJ() 
            
        self.donnees = self.listeTracks

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDreleve", typeDonnee="entier"),
            ColumnDefn(_(u"Date budget"), 'left', 100, "date_budget", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Analytique"), "left", 150, "label_analytique", typeDonnee="texte"),
            ColumnDefn(_(u"Catégorie"), "left", 150, "label_categorie", typeDonnee="texte"),
            ColumnDefn(_(u"Libellé"), "left", 120, "libelle", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Montant"), "right", 100, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune ventilation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[5])
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
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDventilation
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des ventilations"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des ventilations"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        if self.GetGrandParent().GetName() == "DLG_Saisie_operation_tresorerie" :
            dateOperation = self.GetGrandParent().ctrl_date.GetDate()
        else :
            dateOperation = None
        dlg = DLG_Saisie_ventilation_operation.Dialog(self, typeOperation=self.typeOperation, track=None, dateOperation=dateOperation)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees() 
            track = Track(dictDonnees)
            self.listeTracks.append(track)
            self.MAJ() 
            self.SelectObject(track)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ventilation à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        index = self.listeTracks.index(track)
        dlg = DLG_Saisie_ventilation_operation.Dialog(self, typeOperation=self.typeOperation, track=track)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees() 
            track = Track(dictDonnees)
            self.listeTracks[index] = track
        dlg.Destroy()
        self.MAJ() 
        self.SelectObject(track)

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ventilation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette ventilation ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listeTracks.remove(track)
            self.MAJ()
        dlg.Destroy()
    
    def GetTracks(self):
        return self.listeTracks
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "label_exercice" : {"mode" : "nombre", "singulier" : _(u"ventilation"), "pluriel" : _(u"ventilations"), "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

# -------------------------------------------------------------------------------------------------------------------------------------------


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        tracks = Importation(IDoperation=1)
        
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.SetTracks(tracks)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
