#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Utils import UTILS_Texte








class Track(object):
    def __init__(self, parent, index=None, item=None):
        self.parent = parent
        self.index = index
        self.nom = item[0]
        self.categories = UTILS_Texte.ConvertStrToListe(item[1])
        self.MAJ()

    def MAJ(self):
        if type(self.categories) == str :
            self.categories = UTILS_Texte.ConvertStrToListe(self.categories)

        # Génération du texte Catégories
        listeTemp = []
        for IDcategorie in self.categories :
            nom = None
            if IDcategorie == 0 :
                nom = _(u"Toutes les catégories inutilisées")
            if IDcategorie in self.parent.dictCategories:
                nom = self.parent.dictCategories[IDcategorie]
            if nom != None :
                listeTemp.append(nom)
        listeTemp.sort()
        self.texte_categories = u", ".join(listeTemp)
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.listeDonnees = []
        self.dictCategories = self.GetCategoriesMedicales()
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def GetCategoriesMedicales(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM categories_medicales;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        dictCategories = {}
        for IDcategorie, nom in listeCategories :
            dictCategories[IDcategorie] = nom
        return dictCategories

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetParametres(self):
        return self.listeDonnees

    def SetParametres(self, listeParametres=[]):
        self.listeDonnees = listeParametres
        self.MAJ()

    def GetTracks(self):
        """ Récupération des données """
        listeListeView = []
        index = 0
        for item in self.listeDonnees :
            track = Track(self, index, item)
            listeListeView.append(track)
            index += 1
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateIndex(index):
            return str(index+1)

        liste_Colonnes = [
            ColumnDefn(_(u""), "left", 0, "", typeDonnee="texte"),
            ColumnDefn(_(u"Ordre"), "center", 70, "index", typeDonnee="entier", stringConverter=FormateIndex),
            ColumnDefn(_(u"Nom de la colonne"), "left", 180, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Catégories associées"), "left", 110, "texte_categories", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune colonne"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, index=None):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if index != None :
            self.SelectObject(self.GetObjectAt(index), deselectOthers=True, ensureVisible=True)
        self._ResizeSpaceFillingColumns()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des colonnes"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des colonnes"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        dlg = DLG_Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            categories = dlg.GetCategories()
            self.listeDonnees.append((nom, categories))
            self.MAJ(len(self.listeDonnees)-1)
        dlg.Destroy()
        
    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune colonne à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie(self, track.nom, track.categories)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            categories = dlg.GetCategories()
            self.listeDonnees[track.index] = (nom, categories)
            self.MAJ(track.index)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune colonne à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette colonne ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listeDonnees.pop(track.index)
            self.MAJ()
        dlg.Destroy()

    def Monter(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune colonne dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        index = track.index
        if track.index > 0 :
            self.listeDonnees.insert(index-1, self.listeDonnees[index])
            self.listeDonnees.pop(index+1)
            self.MAJ(index-1)
    
    def Descendre(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune colonne dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        index = track.index
        if track.index < len(self.listeDonnees)-1 :
            self.listeDonnees.insert(index+2, self.listeDonnees[index])
            self.listeDonnees.pop(index)
            self.MAJ(index+1)


# -------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        self.Importation()

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM categories_medicales
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictCategories = {0 : 0}
        self.Append(_(u"Toutes les catégories inutilisées"))
        index = 1
        for IDcategorie, nom in listeDonnees:
            self.Append(nom)
            self.dictCategories[index] = IDcategorie
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        for index, IDcategorie in self.dictCategories.items():
            if self.IsChecked(index):
                listeIDcoches.append(IDcategorie)
        listeIDcoches = UTILS_Texte.ConvertListeToStr(listeIDcoches)
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        if type(listeIDcoches) == str :
            listeIDcoches = UTILS_Texte.ConvertStrToListe(listeIDcoches)
        index = 0
        for index, IDcategorie in self.dictCategories.items():
            if IDcategorie in listeIDcoches:
                self.Check(index)


class DLG_Saisie(wx.Dialog):
    def __init__(self, parent, nom=None, categories=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        if nom != None :
            self.ctrl_nom.SetValue(nom)
            
        self.label_categories = wx.StaticText(self, -1, _(u"Catégories :"))
        self.ctrl_categories = CTRL_Categories(self)
        self.ctrl_categories.SetMinSize((280, 160))

        if categories != None :
            self.ctrl_categories.SetIDcoches(categories)
            
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nom == None :
            self.SetTitle(_(u"Saisie d'une colonne"))
        else:
            self.SetTitle(_(u"Modification d'une colonne"))
        self.SetMinSize((350, -1))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_categories, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_categories, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        self.SetMinSize(self.GetSize())
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
    
    def GetNom(self):
        return self.ctrl_nom.GetValue()
    
    def GetCategories(self):
        return self.ctrl_categories.GetIDcoches()
        
    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        categories = self.ctrl_categories.GetIDcoches()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour cette colonne !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        if categories == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une catégorie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_categories.SetFocus()
            return

        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesinformationsmdicales")




# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        listeParametres = [
            (u"Infos alimentaires", "1"),
            (u"Infos diverses", "0;2;3;4"),
        ]
        self.myOlv.SetParametres(listeParametres)
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
