#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx

import OL_Unites
import OL_Unites_remplissage

import GestionDB

try: import psyco; psyco.full()
except: pass



class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panel_unites", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        
        # Unités
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, u"Unités de consommation")
        self.ctrl_unites = OL_Unites.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_unites", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_unites.MAJ()
        self.bouton_unites_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_unites_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_unites_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_unites_monter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_unites_descendre = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        
        # Remplissage
        self.staticbox_remplissage_staticbox = wx.StaticBox(self, -1, u"Unités de remplissage")        
        self.ctrl_remplissage = OL_Unites_remplissage.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_unites", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_remplissage.MAJ() 
        self.bouton_remplissage_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_remplissage_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_remplissage_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_remplissage_monter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_remplissage_descendre = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonUnites_Ajouter, self.bouton_unites_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonUnites_Modifier, self.bouton_unites_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonUnites_Supprimer, self.bouton_unites_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonUnites_Monter, self.bouton_unites_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonUnites_Descendre, self.bouton_unites_descendre)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRemplissage_Ajouter, self.bouton_remplissage_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRemplissage_Modifier, self.bouton_remplissage_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRemplissage_Supprimer, self.bouton_remplissage_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRemplissage_Monter, self.bouton_remplissage_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRemplissage_Descendre, self.bouton_remplissage_descendre)

    def __set_properties(self):
        self.ctrl_unites.SetToolTipString(u"Liste des consommations")
        self.bouton_unites_ajouter.SetToolTipString(u"Cliquez ici pour créer une unité de consommation")
        self.bouton_unites_modifier.SetToolTipString(u"Cliquez ici pour modifier l'unité de consommation sélectionnée dans la liste")
        self.bouton_unites_supprimer.SetToolTipString(u"Cliquez ici pour supprimer l'unité de consommation sélectionnée dans la liste")
        self.bouton_unites_monter.SetToolTipString(u"Cliquez ici pour monter l'unité sélectionnée dans la liste")
        self.bouton_unites_descendre.SetToolTipString(u"Cliquez ici pour descendre l'unité sélectionnée dans la liste")
        self.ctrl_remplissage.SetToolTipString(u"Liste des unités de remplissage")
        self.bouton_remplissage_ajouter.SetToolTipString(u"Cliquez ici pour créer une unité de remplissage")
        self.bouton_remplissage_modifier.SetToolTipString(u"Cliquez ici pour modifier l'unité de remplissage sélectionnée dans la liste")
        self.bouton_remplissage_supprimer.SetToolTipString(u"Cliquez ici pour supprimer l'unité de remplissage selectionnée dans la liste")
        self.bouton_remplissage_monter.SetToolTipString(u"Cliquez ici pour monter l'unité sélectionnée dans la liste")
        self.bouton_remplissage_descendre.SetToolTipString(u"Cliquez ici pour descendre l'unité sélectionnée dans la liste")
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons_ouvertures = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        staticbox_remplissage = wx.StaticBoxSizer(self.staticbox_remplissage_staticbox, wx.VERTICAL)
        grid_sizer_remplissage = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_remplissage = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites_staticbox, wx.VERTICAL)
        grid_sizer_unites = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_unites = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_unites.Add(self.ctrl_unites, 1, wx.EXPAND, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_ajouter, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_modifier, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_supprimer, 0, 0, 0)
        grid_sizer_boutons_unites.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_monter, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_descendre, 0, 0, 0)
        grid_sizer_unites.Add(grid_sizer_boutons_unites, 1, wx.EXPAND, 0)
        grid_sizer_unites.AddGrowableRow(0)
        grid_sizer_unites.AddGrowableCol(0)
        staticbox_unites.Add(grid_sizer_unites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_unites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_remplissage.Add(self.ctrl_remplissage, 1, wx.EXPAND, 0)
        grid_sizer_boutons_remplissage.Add(self.bouton_remplissage_ajouter, 0, 0, 0)
        grid_sizer_boutons_remplissage.Add(self.bouton_remplissage_modifier, 0, 0, 0)
        grid_sizer_boutons_remplissage.Add(self.bouton_remplissage_supprimer, 0, 0, 0)
        grid_sizer_boutons_remplissage.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons_remplissage.Add(self.bouton_remplissage_monter, 0, 0, 0)
        grid_sizer_boutons_remplissage.Add(self.bouton_remplissage_descendre, 0, 0, 0)
        grid_sizer_remplissage.Add(grid_sizer_boutons_remplissage, 1, wx.EXPAND, 0)
        grid_sizer_remplissage.AddGrowableRow(0)
        grid_sizer_remplissage.AddGrowableCol(0)
        staticbox_remplissage.Add(grid_sizer_remplissage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_remplissage, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonUnites_Ajouter(self, event): 
        self.ctrl_unites.Ajouter(None)

    def OnBoutonUnites_Modifier(self, event): 
        self.ctrl_unites.Modifier(None)
        
    def OnBoutonUnites_Supprimer(self, event): 
        self.ctrl_unites.Supprimer(None)

    def OnBoutonUnites_Monter(self, event): 
        self.ctrl_unites.Monter(None)

    def OnBoutonUnites_Descendre(self, event):
        self.ctrl_unites.Descendre(None)
        
    def OnBoutonRemplissage_Ajouter(self, event):
        self.ctrl_remplissage.Ajouter(None)

    def OnBoutonRemplissage_Modifier(self, event):
        self.ctrl_remplissage.Modifier(None)

    def OnBoutonRemplissage_Supprimer(self, event):
        self.ctrl_remplissage.Supprimer(None)

    def OnBoutonRemplissage_Monter(self, event):
        self.ctrl_remplissage.Monter(None)

    def OnBoutonRemplissage_Descendre(self, event):
        self.ctrl_remplissage.Descendre(None)

    def Validation(self):
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
        self.ctrl= Panel(panel, IDactivite=1)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, u"TEST", size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()