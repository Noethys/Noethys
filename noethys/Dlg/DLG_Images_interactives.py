#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Images_interactives

LISTE_CATEGORIES = [
    ("produits_categories", _(u"Catégorie de produits")),
    ] # Code, label


class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        listeItems = []
        index = 0
        for code, label in LISTE_CATEGORIES :
            listeItems.append(label)
            index += 1
        return listeItems

    def SetCategorie(self, categorie=""):
        index = 0
        for code, label in LISTE_CATEGORIES :
            if code == categorie :
                 self.SetSelection(index)
            index += 1

    def GetCategorie(self):
        index = self.GetSelection()
        return LISTE_CATEGORIES[index][0]
    
# ------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Images_interactives", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        titre = _(u"Images interactives")
        intro = _(u"Vous pouvez ici paramétrer des images interactives. Noethys dispose d'un outil de mise en page qui vous permet de créer facilement ces images et de les associer à des données.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Image_interactive.png")
        
        # Catégorie
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"Catégorie"))
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self)
        if categorie != None :
            self.ctrl_categorie.SetCategorie(categorie)
        
        # Modèles
        self.staticbox_modeles_staticbox = wx.StaticBox(self, -1, _(u"Images interactives disponibles"))
        self.ctrl_modeles = OL_Images_interactives.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_dupliquer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_importer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_import.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_exporter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_export.png"), wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorie, self.ctrl_categorie)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Visualiser, self.bouton_visualiser)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Dupliquer, self.bouton_dupliquer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Importer, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_modeles.Exporter, self.bouton_exporter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init contrôle
        self.OnChoixCategorie(None)

    def __set_properties(self):
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une catégorie")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une nouvelle image")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'image sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'image sélectionnée dans la liste")))
        self.bouton_visualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser l'image interactive")))
        self.bouton_dupliquer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour dupliquer l'image sélectionnée dans la liste")))
        self.bouton_importer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer une image interactive (.ndi)")))
        self.bouton_exporter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter l'image sélectionnée dans la liste (.ndi)")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((680, 590))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Catégorie
        staticbox_categorie = wx.StaticBoxSizer(self.staticbox_categorie_staticbox, wx.VERTICAL)
        grid_sizer_categorie = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_categorie.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_categorie.AddGrowableCol(1)
        staticbox_categorie.Add(grid_sizer_categorie, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_categorie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Modèles
        staticbox_modeles = wx.StaticBoxSizer(self.staticbox_modeles_staticbox, wx.VERTICAL)
        grid_sizer_modeles = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_modeles.Add(self.ctrl_modeles, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=11, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_visualiser, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_dupliquer, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_importer, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_exporter, 0, 0, 0)
        grid_sizer_modeles.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)

        grid_sizer_modeles.AddGrowableRow(0)
        grid_sizer_modeles.AddGrowableCol(0)
        staticbox_modeles.Add(grid_sizer_modeles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_modeles, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnChoixCategorie(self, event): 
        categorie = self.ctrl_categorie.GetCategorie()
        self.ctrl_modeles.MAJ(categorie=categorie)
    
    def SelectCategorie(self, categorie=""):
        self.ctrl_categorie.SetCategorie(categorie)
        self.OnChoixCategorie(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Imagesinteractives")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
