#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image

from Ol import OL_Messages


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Messages
        self.ctrl_messages = OL_Messages.ListView(self, -1, style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
        
        # Commandes
        self.bouton_messages_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_messages_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_messages_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        
        self.bouton_messages_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un message")))
        self.bouton_messages_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le message sélectionné dans la liste")))
        self.bouton_messages_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le message sélectionné dans la liste")))
        
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnAjouterMessage, self.bouton_messages_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnModifierMessage, self.bouton_messages_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerMessage, self.bouton_messages_supprimer)

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_messages = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_messages = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_messages.Add(self.ctrl_messages, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, 10)
        grid_sizer_boutons_messages.Add(self.bouton_messages_ajouter, 0, 0, 0)
        grid_sizer_boutons_messages.Add(self.bouton_messages_modifier, 0, 0, 0)
        grid_sizer_boutons_messages.Add(self.bouton_messages_supprimer, 0, 0, 0)
        grid_sizer_messages.Add(grid_sizer_boutons_messages, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 10)
        grid_sizer_messages.AddGrowableRow(0)
        grid_sizer_messages.AddGrowableCol(0)
        self.SetSizer(grid_sizer_messages)
        self.Layout()
    
    def MAJ(self):
        self.ctrl_messages.MAJ() 

    def OnAjouterMessage(self, event):
        self.ctrl_messages.Ajouter(None)
        
    def OnModifierMessage(self, event):
        self.ctrl_messages.Modifier(None)
        
    def OnSupprimerMessage(self, event):
        self.ctrl_messages.Supprimer(None)
    
    def GetMessages(self):
        return self.ctrl_messages.donnees



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()