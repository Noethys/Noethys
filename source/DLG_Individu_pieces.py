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
import OL_Pieces
import CTRL_Pieces_obligatoires
import OL_Liste_cotisations


class Panel(wx.Panel):
    def __init__(self, parent, IDindividu=None, dictFamillesRattachees={}):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Individu_pieces", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees

        # Pièces à fournir
        self.staticbox_pieces_obligatoires = wx.StaticBox(self, -1, _(u"Pièces à fournir"))
        self.ctrl_pieces_obligatoires = CTRL_Pieces_obligatoires.CTRL(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees, largeurColonne=140)
        self.ctrl_pieces_obligatoires.SetBackgroundColour("#F0FBED")
        self.ctrl_pieces_obligatoires.SetMinSize((150, 50))
        
        # Pièces fournies
        self.staticbox_pieces = wx.StaticBox(self, -1, _(u"Pièces fournies"))
        self.ctrl_pieces = OL_Pieces.ListView(self, IDindividu=IDindividu, dictFamillesRattachees=self.dictFamillesRattachees, id=-1, name="OL_pieces", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_pieces.SetMinSize((150, 50))
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Cotisations individuelles
        self.staticbox_cotisations = wx.StaticBox(self, -1, _(u"Cotisations familiales et individuelles"))
        codesColonnes = ["IDcotisation", "date_debut", "date_fin", "beneficiaires", "nom", "numero", "date_creation_carte", "depot_nom"]
        checkColonne = True
        triColonne = "date_debut"
        self.ctrl_cotisations = OL_Liste_cotisations.ListView(self, IDindividu=IDindividu, dictFamillesRattachees=self.dictFamillesRattachees, mode="individu", codesColonnes=codesColonnes, checkColonne=checkColonne, triColonne=triColonne, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        
        self.bouton_ajouter_cotisation = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_cotisation = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_cotisation = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter_Cotisation, self.bouton_ajouter_cotisation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier_Cotisation, self.bouton_modifier_cotisation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer_Cotisation, self.bouton_supprimer_cotisation)

        # Propriétés
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour saisir une pièce"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la pièce sélectionnée"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la pièce sélectionnée"))
        self.bouton_ajouter_cotisation.SetToolTipString(_(u"Cliquez ici pour saisir une cotisation individuelle"))
        self.bouton_modifier_cotisation.SetToolTipString(_(u"Cliquez ici pour modifier la cotisation individuelle sélectionnée"))
        self.bouton_supprimer_cotisation.SetToolTipString(_(u"Cliquez ici pour supprimer la cotisation individuelle sélectionnée"))

        # --- Layout ---
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Pièces à fournir
        staticbox_pieces_obligatoires = wx.StaticBoxSizer(self.staticbox_pieces_obligatoires, wx.VERTICAL)
        grid_sizer_pieces_obligatoires = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_pieces_obligatoires.Add(self.ctrl_pieces_obligatoires, 1, wx.EXPAND, 0)
        grid_sizer_pieces_obligatoires.AddGrowableCol(0)
        grid_sizer_pieces_obligatoires.AddGrowableRow(0)
        staticbox_pieces_obligatoires.Add(grid_sizer_pieces_obligatoires, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut.Add(staticbox_pieces_obligatoires, 0, wx.EXPAND, 0)
        
        # Pièces à fournir
        staticbox_pieces = wx.StaticBoxSizer(self.staticbox_pieces, wx.VERTICAL)
        grid_sizer_pieces = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_pieces.Add(self.ctrl_pieces, 1, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_pieces.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        grid_sizer_pieces.AddGrowableCol(0)
        grid_sizer_pieces.AddGrowableRow(0)
        staticbox_pieces.Add(grid_sizer_pieces, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut.Add(staticbox_pieces, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_haut.AddGrowableRow(0)

        # Cotisations
        staticbox_cotisations = wx.StaticBoxSizer(self.staticbox_cotisations, wx.VERTICAL)
        grid_sizer_cotisations = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_cotisations.Add(self.ctrl_cotisations, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter_cotisation, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier_cotisation, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer_cotisation, 0, wx.ALL, 0)
        grid_sizer_cotisations.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        
        grid_sizer_cotisations.AddGrowableCol(0)
        grid_sizer_cotisations.AddGrowableRow(0)
        staticbox_cotisations.Add(grid_sizer_cotisations, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_cotisations, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout() 
    
    def OnAjoutExpress(self, IDfamille=None, IDtype_piece=None, IDindividu=None):
        self.ctrl_pieces.AjoutExpress(IDfamille, IDtype_piece, IDindividu)
    
    def OnBoutonAjouter(self, event):
        self.ctrl_pieces.Ajouter(None)

    def OnBoutonModifier(self, event):
        self.ctrl_pieces.Modifier(None)

    def OnBoutonSupprimer(self, event):
        self.ctrl_pieces.Supprimer(None)

    def OnBoutonAjouter_Cotisation(self, event):
        self.ctrl_cotisations.Ajouter(None)

    def OnBoutonModifier_Cotisation(self, event):
        self.ctrl_cotisations.Modifier(None)

    def OnBoutonSupprimer_Cotisation(self, event):
        self.ctrl_cotisations.Supprimer(None)

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.IDindividu == None :
            self.IDindividu = self.GetGrandParent().IDindividu
        self.ctrl_pieces_obligatoires.MAJ() 
        self.ctrl_pieces.MAJ() 
        self.ctrl_cotisations.MAJ() 
        self.Refresh()
        
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        pass
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel, IDindividu=937)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()