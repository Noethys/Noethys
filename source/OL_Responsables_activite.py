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


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


class Track(object):
    def __init__(self, donnees):
        self.IDresponsable = donnees[0]
        self.IDactivite = donnees[1]
        self.nom = donnees[2]
        self.fonction = donnees[3]
        self.defaut = donnees[4]
        self.sexe = donnees[5]

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDactivite = kwds.pop("IDactivite", None)
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
        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
        FROM responsables_activite 
        WHERE IDactivite=%d
        ORDER BY nom; """ % self.IDactivite
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
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        imgHomme = self.AddNamedImages("homme", wx.Bitmap("Images/16x16/Homme.png", wx.BITMAP_TYPE_PNG))
        imgFemme = self.AddNamedImages("femme", wx.Bitmap("Images/16x16/Femme.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageDefaut(track):
            if track.defaut == 1 : return "defaut"
            else: return None 
        
        def GetImageSexe(track):
            if track.sexe == "H" : 
                return "homme"
            else: 
                return "femme" 

        liste_Colonnes = [
            ColumnDefn(u"", "left", 21, "IDresponsable", imageGetter=GetImageDefaut),
            ColumnDefn(_(u"Nom du responsable"), 'left', 158, "nom", imageGetter=GetImageSexe),
            ColumnDefn(_(u"Fonction"), "left", 120, "fonction"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun responsable"))
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
            ID = self.Selection()[0].IDresponsable
                
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

        # Item Par défaut
        item = wx.MenuItem(menuPop, 40, _(u"Définir comme responsable par défaut"))
        if noSelection == False :
            if self.Selection()[0].defaut == 1 :
                bmp = wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SetDefaut, id=40)
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des responsables d'activités"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des responsables d'activités"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        dlg = Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            sexe = dlg.GetSexe()
            nom = dlg.GetNom()
            fonction = dlg.GetFonction()
            if len(self.donnees) == 0 :
                defaut = 1 
            else:
                defaut = 0
            listeDonnees = [
                ("IDactivite", self.IDactivite ),
                ("sexe", sexe ),
                ("nom", nom ),
                ("fonction", fonction),
                ("defaut", defaut),
                ]
            DB = GestionDB.DB()
            IDresponsable = DB.ReqInsert("responsables_activite", listeDonnees)
            DB.Close()
            self.MAJ(IDresponsable)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun responsable dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDresponsable = self.Selection()[0].IDresponsable
        sexe = self.Selection()[0].sexe
        nom = self.Selection()[0].nom
        fonction = self.Selection()[0].fonction
        dlg = Saisie(self, sexe, nom, fonction)
        if dlg.ShowModal() == wx.ID_OK:
            sexe = dlg.GetSexe()
            nom = dlg.GetNom()
            fonction = dlg.GetFonction()
            DB = GestionDB.DB()
            listeDonnees = [
                ("sexe", sexe ),
                ("nom", nom ),
                ("fonction", fonction),
                ]
            DB.ReqMAJ("responsables_activite", listeDonnees, "IDresponsable", IDresponsable)
            DB.Close()
            self.MAJ(IDresponsable)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun responsable dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce responsable ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDresponsable = self.Selection()[0].IDresponsable
            DB = GestionDB.DB()
            # Suppression de l'identité
            DB.ReqDEL("responsables_activite", "IDresponsable", IDresponsable)
            # Attribue le Défaut à un autre responsable
            if self.Selection()[0].defaut == 1 :
                req = """SELECT IDresponsable, defaut
                FROM responsables_activite
                WHERE IDactivite=%d
                ORDER BY nom
                ; """ % self.IDactivite
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) > 0 :
                    DB.ReqMAJ("responsables_activite", [("defaut", 1 ),], "IDresponsable", listeDonnees[0][0])
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    def SetDefaut(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun responsable dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDresponsableDefaut = self.Selection()[0].IDresponsable
        DB = GestionDB.DB()
        req = """SELECT IDresponsable, defaut
        FROM responsables_activite
        WHERE IDactivite=%d; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDresponsable, defaut in listeDonnees :
            if IDresponsable == IDresponsableDefaut :
                DB.ReqMAJ("responsables_activite", [("defaut", 1 ),], "IDresponsable", IDresponsable)
            else:
                DB.ReqMAJ("responsables_activite", [("defaut", 0 ),], "IDresponsable", IDresponsable)
        DB.Close()
        self.MAJ()


# -------------------------------------------------------------------------------------------------------------------------------------------

class Saisie(wx.Dialog):
    def __init__(self, parent, sexe="H", nom=None, fonction=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        self.label_sexe = wx.StaticText(self, -1, _(u"Genre du responsable :"))
        self.ctrl_sexe = wx.Choice(self, -1, choices=[_(u"Homme"), _(u"Femme")])
        if sexe == "H" :
            self.ctrl_sexe.Select(0)
        else:
            self.ctrl_sexe.Select(1)
        self.label_nom = wx.StaticText(self, -1, _(u"Nom du responsable :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        if nom != None :
            self.ctrl_nom.SetValue(nom)
        self.label_fonction = wx.StaticText(self, -1, _(u"Fonction :"))
        self.ctrl_fonction = wx.TextCtrl(self, -1, "")
        if fonction !=None :
            self.ctrl_fonction.SetValue(fonction)
            
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nom == None :
            self.SetTitle(_(u"Saisie d'un responsable"))
        else:
            self.SetTitle(_(u"Modification d'un responsable"))
        self.SetMinSize((400, -1))
        
        self.ctrl_sexe.SetToolTipString(_(u"Sélectionnez ici le genre du responsable."))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom du responsable. Ex.: 'David DUPOND' "))
        self.ctrl_fonction.SetToolTipString(_(u"Saisissez ici la fonction du responsable. Ex. : 'Directeur'"))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_sexe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_sexe, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_fonction, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_fonction, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
    
    def GetSexe(self):
        selection = self.ctrl_sexe.GetSelection()
        if selection == 0 : 
            return "H"
        else:
            return "F"
        
    def GetNom(self):
        return self.ctrl_nom.GetValue()
    
    def GetFonction(self):
        return self.ctrl_fonction.GetValue()
        
    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        fonction = self.ctrl_fonction.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de responsable !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        if fonction == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une fonction pour ce responsable !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_fonction.SetFocus()
            return
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Gnralits")


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un responsable..."))
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
        self.myOlv = ListView(panel, IDactivite=1, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
