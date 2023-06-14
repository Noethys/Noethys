#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
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
from Utils import UTILS_Utilisateurs


class Track(object):
    def __init__(self, donnees):
        self.IDcategorie = donnees[0]
        self.ordre = donnees[1]
        self.nom = donnees[2]

    
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
        req = """SELECT IDcategorie, ordre, nom
        FROM menus_categories
        ORDER BY ordre;"""
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
            ColumnDefn(_(u"ID"), "left", 0, "IDcategorie", typeDonnee="entier"),
            ColumnDefn(_(u"Ordre"), "center", 0, "ordre", typeDonnee="entier"), 
            ColumnDefn(_(u"Nom"), "left", 290, "nom", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune catégorie"))
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
        self._ResizeSpaceFillingColumns() 
    
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
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
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
        
        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 40, _(u"Déplacer vers le haut"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)
        if noSelection == True : item.Enable(False)
        
        # Item Déplacer vers le bas
        item = wx.MenuItem(menuPop, 50, _(u"Déplacer vers le bas"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=60)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=70)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des catégories de menus"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des catégories de menus"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_menus_categories", "creer") == False : return
        # Recherche numéro d'ordre à appliquer
        listeTemp = []
        for track in self.donnees :
            listeTemp.append(track.ordre)
        if len(listeTemp) > 0 :
            ordre = max(listeTemp) + 1
        else :
            ordre = 1
        
        # Demande le nom
        dlg = DLG_Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            DB = GestionDB.DB()
            listeDonnees = [
                ("nom", nom ),
                ("ordre", ordre ),
                ]
            IDcategorie = DB.ReqInsert("menus_categories", listeDonnees)
            DB.Close()
            self.MAJ(IDcategorie)
        dlg.Destroy()
        
    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_menus_categories", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune catégorie à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcategorie = self.Selection()[0].IDcategorie
        nom = self.Selection()[0].nom
        dlg = DLG_Saisie(self, nom)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            DB = GestionDB.DB()
            listeDonnees = [    
                            ("nom", nom),
                            ]
            DB.ReqMAJ("menus_categories", listeDonnees, "IDcategorie", IDcategorie)
            DB.Close()
            self.MAJ(IDcategorie)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_menus_categories", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune catégorie à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcategorie = self.Selection()[0].IDcategorie

        # Vérifie que cette catégorie n'a pas déjà été attribué à un menu
        DB = GestionDB.DB()
        req = """SELECT IDmenu, IDcategorie
        FROM menus
        WHERE IDcategorie=%s;""" % IDcategorie
        DB.ExecuterReq(req)
        listeMenus = DB.ResultatReq()
        DB.Close()
        if len(listeMenus) > 0 :
            dlg = wx.MessageDialog(self, _(u"Cette catégorie a déjà été rattachée à %d menus.\nVous ne pouvez donc la supprimer.") % len(listeMenus), _(u"Avertissement"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette catégorie ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("menus_categories", "IDcategorie", IDcategorie)
            DB.Close() 
            self.MAJordre(IDcategorie)
            self.MAJ()
        dlg.Destroy()

    def MAJordre(self, IDcategorie=None):
        DB = GestionDB.DB()
        ordre = 1
        for index in range(0, len(self.donnees)) :
            objet = self.GetObjectAt(index)
            if objet.IDcategorie != IDcategorie :
                DB.ReqMAJ("menus_categories", [("ordre", ordre),], "IDcategorie", objet.IDcategorie)
                ordre += 1
        DB.Close()

    def Monter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_menus_categories", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune catégorie dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcategorie = self.Selection()[0].IDcategorie
        ordre = self.Selection()[0].ordre
        if ordre == 1 : return
        DB = GestionDB.DB()
        # Modifie catégorie actuelle
        DB.ReqMAJ("menus_categories", [("ordre", ordre-1),], "IDcategorie", IDcategorie)
        self.Selection()[0].ordre = ordre-1
        # Modifie catégorie a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        categorie2 = self.GetObjectAt(index-1)
        IDcategorie2 = categorie2.IDcategorie
        DB.ReqMAJ("menus_categories", [("ordre", ordre),], "IDcategorie", IDcategorie2)
        DB.Close()
        self.MAJ(IDcategorie)
    
    def Descendre(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_menus_categories", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune catégorie dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcategorie = self.Selection()[0].IDcategorie
        ordre = self.Selection()[0].ordre
        if ordre == len(self.donnees) : return
        DB = GestionDB.DB()
        # Modifie catégorie actuelle
        DB.ReqMAJ("menus_categories", [("ordre", ordre+1),], "IDcategorie", IDcategorie)
        self.Selection()[0].ordre = ordre+1
        # Modifie catégorie a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        categorie2 = self.GetObjectAt(index+1)
        IDcategorie2 = categorie2.IDcategorie
        DB.ReqMAJ("menus_categories", [("ordre", ordre),], "IDcategorie", IDcategorie2)
        DB.Close()
        self.MAJ(IDcategorie)


# -------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Saisie(wx.Dialog):
    def __init__(self, parent, nom=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        if nom != None :
            self.ctrl_nom.SetValue(nom)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nom == None :
            self.SetTitle(_(u"Saisie d'une catégorie"))
        else:
            self.SetTitle(_(u"Modification d'une catégorie"))
        self.SetMinSize((350, -1))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
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
    
    def GetNom(self):
        return self.ctrl_nom.GetValue()
    

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun nom de catégorie !\nExemples : 'Midi', 'goûter', 'Dessert', etc..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Categoriesdemenus")



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
