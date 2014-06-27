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
import datetime

import OL_Cotisations_depots

import GestionDB


class Dialog(wx.Dialog):
    def __init__(self, parent, tracks=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_depot_cotisation_ajouter", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.tracks= tracks
        
        self.label_intro = wx.StaticText(self, -1, u"Double-cliquez sur une cotisation pour l'affecter ou non au dépôt.", style=wx.ALIGN_CENTER)
        
        self.label_tri = wx.StaticText(self, -1, u"Tri par :")
        self.ctrl_tri = wx.Choice(self, -1, choices = (u"Ordre de saisie", u"Date de début de validité", u"Date de fin de validité", u"Nom des titulaires", u"Type de cotisation", u"Nom de cotisation", u"Numéro de carte", u"Date de dépôt"))
        self.ctrl_tri.Select(0) 
        
        self.label_ordre = wx.StaticText(self, -1, u"Ordre :")
        self.ctrl_ordre = wx.Choice(self, -1, choices = (u"Ascendant", u"Descendant"))
        self.ctrl_ordre.Select(1) 

        # Cotisations disponibles
        self.staticbox_cotisations_disponibles_staticbox = wx.StaticBox(self, -1, u"Cotisations disponibles")
        self.ctrl_cotisations_disponibles = OL_Cotisations_depots.ListView(self, id=-1, inclus=False, name="OL_cotisations_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        # Commandes
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut_rouge.png", wx.BITMAP_TYPE_ANY))

        # Reglements du dépôt
        self.staticbox_cotisations_depot_staticbox = wx.StaticBox(self, -1, u"Cotisations du dépôt")
        self.ctrl_cotisations_depot = OL_Cotisations_depots.ListView(self, id=-1, inclus=True, name="OL_cotisations_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonBas, self.bouton_bas)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHaut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoixTri, self.ctrl_tri)
        self.Bind(wx.EVT_CHOICE, self.OnChoixOrdre, self.ctrl_ordre)

        # Initialisation des contrôles
        self.MAJListes(tracks=self.tracks) 
        

    def __set_properties(self):
        self.SetTitle(u"Ajouter ou retirer des cotisations")
        self.ctrl_tri.SetToolTipString(u"Sélectionnez le critère de tri")
        self.ctrl_ordre.SetToolTipString(u"Sélectionnez l'ordre de tri")
        self.bouton_bas.SetToolTipString(u"Cliquez ici pour ajouter la cotisation disponible selectionné dans le dépôt")
        self.bouton_bas.SetMinSize((100, -1))
        self.bouton_haut.SetMinSize((100, -1))
        self.bouton_haut.SetToolTipString(u"Cliquez ici pour retirer la cotisation sélectionnée du dépôt")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((950, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Intro
        grid_sizer_intro = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_intro.Add(self.label_intro, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        grid_sizer_intro.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_intro.Add(self.label_tri, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.Add(self.ctrl_tri, 0, 0, 0)
        grid_sizer_intro.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_intro.Add(self.label_ordre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.Add(self.ctrl_ordre, 0, 0, 0)
        grid_sizer_intro.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Cotisations disponibles
        staticbox_reglements_disponibles = wx.StaticBoxSizer(self.staticbox_cotisations_disponibles_staticbox, wx.VERTICAL)
        staticbox_reglements_disponibles.Add(self.ctrl_cotisations_disponibles, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reglements_disponibles, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Commandes de transfert
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_commandes.AddGrowableCol(4)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Cotisations déposées
        staticbox_reglements_depot = wx.StaticBoxSizer(self.staticbox_cotisations_depot_staticbox, wx.VERTICAL)
        staticbox_reglements_depot.Add(self.ctrl_cotisations_depot, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reglements_depot, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def MAJListes(self, tracks=None, selectionTrack=None, nextTrack=None):
        self.tracks = tracks
        self.ctrl_cotisations_disponibles.MAJ(tracks, selectionTrack=selectionTrack, nextTrack=nextTrack) 
        self.ctrl_cotisations_depot.MAJ(tracks, selectionTrack=selectionTrack, nextTrack=nextTrack) 
    
    def GetTracks(self):
        return self.tracks

    def OnChoixTri(self, event):
        selection = self.ctrl_tri.GetSelection() 
        self.ctrl_cotisations_disponibles.numColonneTri = selection
        self.ctrl_cotisations_depot.numColonneTri = selection
        self.MAJListes()

    def OnChoixOrdre(self, event):
        selection = self.ctrl_ordre.GetSelection() 
        self.ctrl_cotisations_disponibles.ordreAscendant = selection
        self.ctrl_cotisations_depot.ordreAscendant = selection
        self.MAJListes()

    def OnBoutonBas(self, event): 
        self.ctrl_cotisations_disponibles.Deplacer()

    def OnBoutonHaut(self, event):
        self.ctrl_cotisations_depot.Deplacer()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Gestiondesdptsdecotisations")

    def OnBoutonOk(self, event): 
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
