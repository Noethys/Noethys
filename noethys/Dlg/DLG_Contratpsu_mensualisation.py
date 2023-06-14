#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ol import OL_Contratspsu_mensualites



class Panel(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_mensualisation", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase

        # Mensualités
        self.staticbox_mensualites_staticbox = wx.StaticBox(self, -1, _(u"Mensualités"))
        self.listviewAvecFooter = OL_Contratspsu_mensualites.ListviewAvecFooter(self, kwargs={})
        self.ctrl_mensualites = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Contratspsu_mensualites.CTRL_Outils(self, listview=self.ctrl_mensualites, afficherCocher=False)
        if self.parent.GetName() == "notebook" :
            self.ctrl_recherche.SetBackgroundColour(self.parent.GetThemeBackgroundColour())

        self.bouton_mensualites_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_mensualites_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_mensualites.Apercu, self.bouton_mensualites_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_mensualites.Imprimer, self.bouton_mensualites_imprimer)


    def __set_properties(self):
        self.bouton_mensualites_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste")))
        self.bouton_mensualites_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Mensualités
        staticbox_mensualites = wx.StaticBoxSizer(self.staticbox_mensualites_staticbox, wx.VERTICAL)
        grid_sizer_mensualites = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_mensualites.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)

        grid_sizer_boutons_mensualites = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_mensualites.Add(self.bouton_mensualites_apercu, 0, 0, 0)
        grid_sizer_boutons_mensualites.Add(self.bouton_mensualites_imprimer, 0, 0, 0)
        grid_sizer_mensualites.Add(grid_sizer_boutons_mensualites, 1, wx.EXPAND, 0)

        grid_sizer_mensualites.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_mensualites.AddGrowableRow(0)
        grid_sizer_mensualites.AddGrowableCol(0)
        staticbox_mensualites.Add(grid_sizer_mensualites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_mensualites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def Validation(self):
        if self.clsbase.Calculer(mode_test=True) == False :
            return False

        return True

    def Sauvegarde(self):
        pass

    def MAJ(self):
        self.clsbase.Calculer()

        tracks = self.clsbase.GetValeur("tracks_mensualites", [])
        self.ctrl_mensualites.SetTracks(tracks)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()