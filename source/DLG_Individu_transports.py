#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import OL_Transports
import OL_Transports_prog


class Panel(wx.Panel):
    def __init__(self, parent, IDindividu=None, dictFamillesRattachees={}):
        wx.Panel.__init__(self, parent, id=-1, name="panel_transports", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        # Transports programmés
        self.staticbox_prog = wx.StaticBox(self, -1, _(u"Programmation de transports"))
        self.ctrl_prog_transports = OL_Transports_prog.ListView(self, IDindividu=IDindividu, id=-1, name="OL_prog_transports", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_prog_transports.SetMinSize((150, 20))
        
        self.bouton_prog_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_prog_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_prog_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Liste des transports
        self.staticbox_liste = wx.StaticBox(self, -1, _(u"Transports"))
        self.ctrl_liste_transports = OL_Transports.ListView(self, IDindividu=IDindividu, id=-1, name="OL_liste_transports", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_liste_transports.SetMinSize((150, 20))
        
        self.bouton_liste_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_liste_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_liste_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_liste_calendrier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Calendrier.png", wx.BITMAP_TYPE_ANY))
        
        self.ctrl_recherche = OL_Transports.CTRL_Outils(self, listview=self.ctrl_liste_transports, afficherCocher=True)
        self.ctrl_recherche.SetBackgroundColour((255, 255, 255)) 
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouterProg, self.bouton_prog_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifierProg, self.bouton_prog_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimerProg, self.bouton_prog_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouterListe, self.bouton_liste_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifierListe, self.bouton_liste_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimerListe, self.bouton_liste_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrier, self.bouton_liste_calendrier)

        # Propriétés
        self.bouton_prog_ajouter.SetToolTipString(_(u"Cliquez ici pour programmer un transport"))
        self.bouton_prog_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la programmation sélectionnée dans la liste"))
        self.bouton_prog_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la programmation sélectionnée dans la liste"))
        self.bouton_liste_ajouter.SetToolTipString(_(u"Cliquez ici pour saisir un ou plusieurs transports"))
        self.bouton_liste_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le transport sélectionné dans la liste"))
        self.bouton_liste_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le transport sélectionné ou les transports cochés dans la liste"))
        self.bouton_liste_calendrier.SetToolTipString(_(u"Cliquez ici pour afficher le planning des transports"))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        # Transports programmés
        staticbox_prog_transports = wx.StaticBoxSizer(self.staticbox_prog, wx.VERTICAL)
        grid_sizer_prog = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_prog.Add(self.ctrl_prog_transports, 1, wx.EXPAND, 0)
        grid_sizer_boutons_prog = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_prog.Add(self.bouton_prog_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons_prog.Add(self.bouton_prog_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons_prog.Add(self.bouton_prog_supprimer, 0, wx.ALL, 0)
        grid_sizer_prog.Add(grid_sizer_boutons_prog, 1, wx.ALL, 0)
        grid_sizer_prog.AddGrowableCol(0)
        grid_sizer_prog.AddGrowableRow(0)
        staticbox_prog_transports.Add(grid_sizer_prog, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_prog_transports, 1, wx.EXPAND|wx.ALL, 5)

        # Liste des transports
        staticbox_liste_transports = wx.StaticBoxSizer(self.staticbox_liste, wx.VERTICAL)
        grid_sizer_liste = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_liste.Add(self.ctrl_liste_transports, 1, wx.EXPAND, 0)
        grid_sizer_boutons_liste = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_liste.Add(self.bouton_liste_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons_liste.Add(self.bouton_liste_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons_liste.Add(self.bouton_liste_supprimer, 0, wx.ALL, 0)
        grid_sizer_boutons_liste.Add( (5, 5), 0, wx.ALL, 0)
        grid_sizer_boutons_liste.Add(self.bouton_liste_calendrier, 0, wx.ALL, 0)
        grid_sizer_liste.Add(grid_sizer_boutons_liste, 1, wx.ALL, 0)
        grid_sizer_liste.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_liste.AddGrowableCol(0)
        grid_sizer_liste.AddGrowableRow(0)
        staticbox_liste_transports.Add(grid_sizer_liste, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_liste_transports, 1, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)

    def OnBoutonAjouterProg(self, event):
        self.ctrl_prog_transports.Ajouter(None)

    def OnBoutonModifierProg(self, event):
        self.ctrl_prog_transports.Modifier(None)

    def OnBoutonSupprimerProg(self, event):
        self.ctrl_prog_transports.Supprimer(None)

    def OnBoutonAjouterListe(self, event):
        self.ctrl_liste_transports.Ajouter(None)

    def OnBoutonModifierListe(self, event):
        self.ctrl_liste_transports.Modifier(None)

    def OnBoutonSupprimerListe(self, event):
        self.ctrl_liste_transports.Supprimer(None)

    def OnBoutonCalendrier(self, event):
        self.ctrl_liste_transports.Calendrier(None)
        
    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.IDindividu = self.GetGrandParent().IDindividu
        if self.IDindividu == None :
            print "pas de IDindividu !"
            return
        self.ctrl_prog_transports.MAJ() 
        self.ctrl_liste_transports.MAJ() 
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
        self.IDindividu = 46
        self.ctrl = Panel(panel, IDindividu=self.IDindividu)
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