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
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs


class Track(object):
    def __init__(self, donnees):
        self.IDarret = donnees[0]
        self.ordre = donnees[1]
        self.nom = donnees[2]
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDligne = kwds.pop("IDligne", 0) 
        self.categorie = kwds.pop("categorie", "") # bus, car, train, etc...
        self.categorieSingulier = kwds.pop("categorieSingulier", u"") # "arrêt de bus"
        self.categoriePluriel = kwds.pop("categoriePluriel", u"") # "arrêts de bus"
        self.mode = kwds.pop("mode", "gestion") # Selection ou gestion
        
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
        if self.mode == "selection" :
            self.GetParent().OnBouton_ok(None)
            return
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT IDarret, ordre, nom
        FROM transports_arrets
        WHERE IDligne=%d
        ORDER BY ordre; """ % self.IDligne
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
            ColumnDefn(_(u"ID"), "left", 0, "IDarret", typeDonnee="entier"),
            ColumnDefn(_(u"Ordre"), "center", 0, "ordre", typeDonnee="entier"), 
            ColumnDefn(_(u"Nom"), 'left', 430, "nom", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun %s") % self.categorieSingulier)
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None, IDligne=0):
        self.IDligne = IDligne
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
            ID = self.Selection()[0].IDarret
                
        # Création du menu contextuel
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
        
        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 40, _(u"Déplacer vers le haut"))
        bmp = wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)
        if noSelection == True : item.Enable(False)
        
        # Item Déplacer vers le bas
        item = wx.MenuItem(menuPop, 50, _(u"Déplacer vers le bas"))
        bmp = wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 80, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=80)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 90, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=90)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des %s") % self.categoriePluriel, format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des %s") % self.categoriePluriel, format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "creer") == False : return
        # Recherche numéro d'ordre à appliquer
        listeTemp = []
        for track in self.donnees :
            listeTemp.append(track.ordre)
        if len(listeTemp) > 0 :
            ordre = max(listeTemp) + 1
        else :
            ordre = 1

        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouvel %s :") % self.categorieSingulier, _(u"Saisie d'un nouvel %s") % self.categorieSingulier, u"")
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("IDligne", self.IDligne), ("nom", nom), ("ordre", ordre ) ]
                IDarret = DB.ReqInsert("transports_arrets", listeDonnees)
                DB.Close()
                self.MAJ(IDarret, IDligne=self.IDligne)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun %s à modifier !") % self.categorieSingulier, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDarret = self.Selection()[0].IDarret
        nom = self.Selection()[0].nom
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le nom de l'%s :") % self.categorieSingulier, _(u"Modification d'un %s") % self.categorieSingulier, nom)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("nom", nom), ]
                DB.ReqMAJ("transports_arrets", listeDonnees, "IDarret", IDarret)
                DB.Close()
                self.MAJ(IDarret, IDligne=self.IDligne)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun %s à supprimer !") % self.categorieSingulier, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cet %s ?") % self.categorieSingulier, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDarret = self.Selection()[0].IDarret
            DB = GestionDB.DB()
            DB.ReqDEL("transports_arrets", "IDarret", IDarret)
            DB.Close() 
            self.MAJordre(IDarret)
            self.MAJ(IDligne=self.IDligne)
        dlg.Destroy()

    def MAJordre(self, IDarret=None):
        DB = GestionDB.DB()
        ordre = 1
        for index in range(0, len(self.donnees)) :
            objet = self.GetObjectAt(index)
            if objet.IDarret != IDarret :
                DB.ReqMAJ("transports_arrets", [("ordre", ordre),], "IDarret", objet.IDarret)
                ordre += 1
        DB.Close()

    def Monter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun arrêt dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDarret = self.Selection()[0].IDarret
        ordre = self.Selection()[0].ordre
        if ordre == 1 : return
        DB = GestionDB.DB()
        # Modifie unite actuelle
        DB.ReqMAJ("transports_arrets", [("ordre", ordre-1),], "IDarret", IDarret)
        self.Selection()[0].ordre = ordre-1
        # Modifie unite a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        arret2 = self.GetObjectAt(index-1)
        IDarret2 = arret2.IDarret
        DB.ReqMAJ("transports_arrets", [("ordre", ordre),], "IDarret", IDarret2)
        DB.Close()
        self.MAJ(IDarret, IDligne=self.IDligne)
    
    def Descendre(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun arrêt dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDarret = self.Selection()[0].IDarret
        ordre = self.Selection()[0].ordre
        if ordre == len(self.donnees) : return
        DB = GestionDB.DB()
        # Modifie unite actuelle
        DB.ReqMAJ("transports_arrets", [("ordre", ordre+1),], "IDarret", IDarret)
        self.Selection()[0].ordre = ordre+1
        # Modifie unite a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        arret2 = self.GetObjectAt(index+1)
        IDarret2 = arret2.IDarret
        DB.ReqMAJ("transports_arrets", [("ordre", ordre),], "IDarret", IDarret2)
        DB.Close()
        self.MAJ(IDarret, IDligne=self.IDligne)

# -----------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un arrêt..."))
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
        self.myOlv = ListView(panel, id=-1, categorie="bus", IDligne=8, categorieSingulier=_(u"arrêt de bus"), categoriePluriel=_(u"arrêts de bus"), name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
