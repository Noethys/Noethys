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
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter

import UTILS_Utilisateurs


class Track(object):
    def __init__(self, donnees):
        self.IDcategorie = donnees[0]
        self.nom = donnees[1]
        self.nbreTitulaires = donnees[2]
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT categories_travail.IDcategorie, categories_travail.nom, Count(individus.IDindividu) AS nbreTitulaires
        FROM categories_travail
        LEFT JOIN individus ON categories_travail.IDcategorie = individus.IDcategorie_travail
        GROUP BY categories_travail.IDcategorie;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                    
        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDcategorie"),
            ColumnDefn(u"Nom", "left", 290, "nom"), 
            ColumnDefn(u"Nbre de titulaires", "left", 110, "nbreTitulaires"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucune catégorie socio-professionnelle")
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
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDcategorie
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des catégories socio-professionnelles", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des catégories socio-professionnelles", format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_travail", "creer") == False : return
        dlg = wx.TextEntryDialog(self, u"Saisissez le nom de la nouvelle catégorie socio-professionnelle :", u"Saisie d'une nouvelle catégorie", u"")
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, u"Le nom que vous avez saisi n'est pas valide.", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("nom", nom ), ]
                IDcategorie = DB.ReqInsert("categories_travail", listeDonnees)
                DB.Close()
                self.MAJ(IDcategorie)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_travail", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune catégorie à modifier dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcategorie = self.Selection()[0].IDcategorie
        nom = self.Selection()[0].nom
        dlg = wx.TextEntryDialog(self, u"Modifiez le nom de la catégorie socio-professionnelle :", u"Modification d'une catégorie", nom)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, u"Le nom que vous avez saisi n'est pas valide.", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("nom", nom ), ]
                DB.ReqMAJ("categories_travail", listeDonnees, "IDcategorie", IDcategorie)
                DB.Close()
                self.MAJ(IDcategorie)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_travail", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune catégorie à supprimer dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.Selection()[0].nbreTitulaires > 0 :
            dlg = wx.MessageDialog(self, u"Il est impossible de supprimer une catégorie déjà assignée à un ou plusieurs individus !", u"Suppression impossible", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer cette catégorie ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDcategorie = self.Selection()[0].IDcategorie
            DB = GestionDB.DB()
            DB.ReqDEL("categories_travail", "IDcategorie", IDcategorie)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher une catégorie socio-professionnelle...")
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
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
