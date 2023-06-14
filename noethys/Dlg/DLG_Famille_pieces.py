#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ol import OL_Pieces
from Ctrl import CTRL_Pieces_obligatoires
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Interface


class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Famille_pieces", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille

        # Pièces à fournir
        self.staticbox_pieces_obligatoires = wx.StaticBox(self, -1, _(u"Pièces à fournir"))
        self.ctrl_pieces_obligatoires = CTRL_Pieces_obligatoires.CTRL(self, IDfamille=IDfamille, size=(-1, 200))
        self.ctrl_pieces_obligatoires.SetMinSize((280, 100))
        couleur_fond = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.ctrl_pieces_obligatoires.SetBackgroundColour(couleur_fond)
        
        # Pièces fournies
        self.staticbox_pieces = wx.StaticBox(self, -1, _(u"Pièces fournies"))
        self.ctrl_pieces = OL_Pieces.ListView(self, IDfamille=IDfamille, id=-1, name="OL_pieces", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une pièce")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la pièce sélectionnée")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la pièce sélectionnée")))

        # --- Layout ---
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        
        # Pièces à fournir
        staticbox_pieces_obligatoires = wx.StaticBoxSizer(self.staticbox_pieces_obligatoires, wx.VERTICAL)
        grid_sizer_pieces_obligatoires = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_pieces_obligatoires.Add(self.ctrl_pieces_obligatoires, 1, wx.EXPAND, 0)
        grid_sizer_pieces_obligatoires.AddGrowableCol(0)
        grid_sizer_pieces_obligatoires.AddGrowableRow(0)
        staticbox_pieces_obligatoires.Add(grid_sizer_pieces_obligatoires, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_pieces_obligatoires, 0, wx.EXPAND|wx.ALL, 5)
        
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
        grid_sizer_base.Add(staticbox_pieces, 1, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(1)
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

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_pieces", "consulter", afficheMessage=False) == False : 
            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.ctrl_pieces_obligatoires.MAJ() 
        self.ctrl_pieces.MAJ() 
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
        self.ctrl = Panel(panel, IDfamille=3)
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