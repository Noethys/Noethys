#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, donnees):
        self.IDprofil = donnees[0]
        self.label = donnees[1]
        self.defaut = donnees[2]

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.categorie = kwds.pop("categorie", "")
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dernierProfilCree = None
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
        req = """SELECT IDprofil, label, defaut
        FROM profils
        WHERE categorie='%s'
        ;""" % self.categorie
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

        # Préparation de la listeImages
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))

        def GetImageDefaut(track):
            if track.defaut == 1:
                return "defaut"
            else:
                return None

        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDprofil", typeDonnee="entier", imageGetter=GetImageDefaut),
            ColumnDefn(_(u"Nom"), "left", 460, "label", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun profil"))
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

        # Item Dupliquer
        item = wx.MenuItem(menuPop, 60, _(u"Dupliquer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Dupliquer, id=60)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Item Par défaut
        item = wx.MenuItem(menuPop, 70, _(u"Définir comme profil par défaut"))
        if noSelection == False :
            if self.Selection()[0].defaut == 1 :
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SetDefaut, id=70)
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Listes des profils de configuration"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Listes des profils de configuration"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouveau profil de configuration :"), _(u"Saisie d'un profil de configuration"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetValue()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False
        if label == "":
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        else:
            DB = GestionDB.DB()
            if len(self.donnees) == 0 :
                defaut = 1
            else :
                defaut = 0
            listeDonnees = [("label", label), ("categorie", self.categorie), ("defaut", defaut)]
            IDprofil = DB.ReqInsert("profils", listeDonnees)
            self.dernierProfilCree = IDprofil
            DB.Close()
            self.MAJ(IDprofil)

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil à modifier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprofil = self.Selection()[0].IDprofil
        label = self.Selection()[0].label
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le profil de configuration :"), _(u"Modification d'un profil"), label)
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetValue()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False
        if label == "":
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        else:
            DB = GestionDB.DB()
            listeDonnees = [("label", label),]
            DB.ReqMAJ("profils", listeDonnees, "IDprofil", IDprofil)
            DB.Close()
            self.MAJ(IDprofil)

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil à supprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        texte = u""
        dlg = wx.MessageDialog(self, _(u"%sSouhaitez-vous vraiment supprimer ce profil?") % texte, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDprofil = self.Selection()[0].IDprofil
            DB = GestionDB.DB()
            # Suppression
            DB.ReqDEL("profils", "IDprofil", IDprofil)
            DB.ReqDEL("profils_parametres", "IDprofil", IDprofil)
            # Réattribution du défaut
            defaut = None
            for track in self.donnees :
                if track.IDprofil != IDprofil :
                    defaut = track.IDprofil
                    if track.defaut == 1 :
                        defaut == False
                        break
            if defaut not in (False, None) :
                DB.ReqMAJ("profils", [("defaut", 1), ], "IDprofil", defaut)
            DB.Close()
            self.MAJ()
        dlg.Destroy()

    def Dupliquer(self, event):
        """ Dupliquer un modèle """
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil à dupliquer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprofil = self.Selection()[0].IDprofil
        label = self.Selection()[0].label

        DB = GestionDB.DB()

        # Duplication du profil
        conditions = "IDprofil=%d" % IDprofil
        dictModifications = {"label": _(u"Copie de %s") % label, "defaut" : 0}
        newIDprofil = DB.Dupliquer("profils", "IDprofil", conditions, dictModifications)

        # Duplication des paramètres
        conditions = "IDprofil=%d" % IDprofil
        dictModifications = {"IDprofil": newIDprofil}
        newIDparametre = DB.Dupliquer("profils_parametres", "IDparametre", conditions, dictModifications)

        DB.Close()
        self.MAJ(newIDprofil)

    def SetDefaut(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprofil = self.Selection()[0].IDprofil
        DB = GestionDB.DB()
        for track in self.donnees :
            if track.defaut == 1 :
                DB.ReqMAJ("profils", [("defaut", 0),], "IDprofil", track.IDprofil)
        DB.ReqMAJ("profils", [("defaut", 1),], "IDprofil", IDprofil)
        DB.Close()
        self.MAJ()




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
