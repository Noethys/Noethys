#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import DLG_Saisie_categorie_budget

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter



class Track(object):
    def __init__(self, donnees):
        self.IDcategorie_budget = donnees["IDcategorie_budget"]
        self.typeCategorie = donnees["typeCategorie"]
        self.IDcategorie = donnees["IDcategorie"]
        self.valeur = donnees["valeur"]
        
        self.dictCategories = {}
    
    def MAJ(self):
        if self.dictCategories.has_key(self.IDcategorie) :
            self.label_categorie = self.dictCategories[self.IDcategorie]
        else :
            self.label_categorie = _(u"Cat�gorie inconnue")
            

def Importation(IDbudget=None, typeCategorie="debit"):
    DB = GestionDB.DB()
    req = """SELECT IDcategorie_budget, IDbudget, type, IDcategorie, valeur
    FROM compta_categories_budget 
    WHERE IDbudget=%d AND type='%s';""" % (IDbudget, typeCategorie)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeTracks = []
    for IDcategorie_budget, IDbudget, typeCategorie, IDcategorie, valeur in listeDonnees :
        dictTemp = {
            "IDcategorie_budget" : IDcategorie_budget, 
            "typeCategorie" : typeCategorie, "IDcategorie" : IDcategorie, "valeur" : valeur,
            }
        track = Track(dictTemp)
        listeTracks.append(track)
    return listeTracks


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.typeCategorie = kwds.pop("typeCategorie", None)
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
        
        # Importation des cat�gories
        req = """SELECT IDcategorie, nom
        FROM compta_categories ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictCategories = {}
        for IDcategorie, nom in listeDonnees :
            self.dictCategories[IDcategorie] = nom
        
        DB.Close()

        for track in self.listeTracks :
            track.dictCategories = self.dictCategories
            track.MAJ() 
            
        self.donnees = self.listeTracks

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateValeur(valeur):
            if valeur == None : return u""
            try :
                montant = float(valeur)
                return u"%.2f %s" % (float(valeur), SYMBOLE)
            except :
                return valeur

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDcategorie_budget", typeDonnee="entier"),
            ColumnDefn(_(u"Cat�gorie"), "left", 250, "label_categorie", typeDonnee="texte"),
            ColumnDefn(_(u"Plafond"), "left", 120, "valeur", typeDonnee="texte", stringConverter=FormateValeur, isSpaceFilling=True),
            ]

        self.SetColumns(liste_Colonnes)
        if self.typeCategorie == "debit" :
            self.SetEmptyListMsg(_(u"Aucune cat�gorie de d�bit"))
        else :
            self.SetEmptyListMsg(_(u"Aucune cat�gorie de cr�dit"))
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
        # S�lection d'un item
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
            ID = self.Selection()[0].IDcategorie_budget
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
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
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des cat�gories budg�taires"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des cat�gories budg�taires"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event=None):
        dlg = DLG_Saisie_categorie_budget.Dialog(self, typeCategorie=self.typeCategorie, track=None)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees() 
            track = Track(dictDonnees)
            self.listeTracks.append(track)
            self.MAJ() 
            self.SelectObject(track)
        dlg.Destroy()

    def Modifier(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune cat�gorie budg�taire � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        index = self.listeTracks.index(track)
        dlg = DLG_Saisie_categorie_budget.Dialog(self, typeCategorie=self.typeCategorie, track=track)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees() 
            track = Track(dictDonnees)
            self.listeTracks[index] = track
        dlg.Destroy()
        self.MAJ() 
        self.SelectObject(track)

    def Supprimer(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune cat�gorie budg�taire � supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette cat�gorie budg�taire ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
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
        
        tracks = Importation(IDbudget=1)
        
        self.myOlv = ListView(panel, id=-1, typeCategorie="debit", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
