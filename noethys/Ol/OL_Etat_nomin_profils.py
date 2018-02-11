#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
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
import GestionDB


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, donnees):
        self.IDprofil = donnees[0]
        self.label = donnees[1]
        self.nbreChamps = donnees[2]
    
    
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
        self.nom_fichier_liste = __file__
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
        req = """SELECT etat_nomin_profils.IDprofil, etat_nomin_profils.label, Count(etat_nomin_selections.IDselection) AS nbreChamps
        FROM etat_nomin_profils
        LEFT JOIN etat_nomin_selections ON etat_nomin_profils.IDprofil = etat_nomin_selections.IDprofil
        GROUP BY etat_nomin_profils.IDprofil;"""
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
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                    
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDprofil", typeDonnee="entier"),
            ColumnDefn(_(u"Nom"), "left", 350, "label", typeDonnee="texte"), 
            ColumnDefn(_(u"Nbre de champs"), "left", 130, "nbreChamps", typeDonnee="entier"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun profil de liste"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
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
            ID = self.Selection()[0].IDprofil
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Listes des profils de liste"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Listes des profils de liste"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouveau profil de liste :"), _(u"Saisie d'un profil"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetValue()
            if label == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("label", label ), ]
                IDprofil = DB.ReqInsert("etat_nomin_profils", listeDonnees)
                DB.Close()
                self.MAJ(IDprofil)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil à modifier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprofil = self.Selection()[0].IDprofil
        label = self.Selection()[0].label
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le profil de liste :"), _(u"Modification d'un profil"), label)
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetValue()
            if label == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("label", label ), ]
                DB.ReqMAJ("etat_nomin_profils", listeDonnees, "IDprofil", IDprofil)
                DB.Close()
                self.MAJ(IDprofil)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil à supprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        texte = u""
        if self.Selection()[0].nbreChamps > 0 :
            texte = _(u"Ce profil comporte déjà %d champs. ") % self.Selection()[0].nbreChamps
        dlg = wx.MessageDialog(self, _(u"%sSouhaitez-vous vraiment supprimer ce profil?") % texte, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDprofil = self.Selection()[0].IDprofil
            DB = GestionDB.DB()
            DB.ReqDEL("etat_nomin_profils", "IDprofil", IDprofil)
            DB.ReqDEL("etat_nomin_selections", "IDprofil", IDprofil)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un profil..."))
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
