#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Calendrier_ouvertures

import GestionDB

try: import psyco; psyco.full()
except: pass



class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panel_unites", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
                
        # Ouvertures
        self.staticbox_ouvertures_staticbox = wx.StaticBox(self, -1, _(u"Calendrier des ouvertures"))
        self.ctrl_ouvertures = CTRL_Calendrier_ouvertures.Calendrier(self, IDactivite=self.IDactivite)
        self.ctrl_ouvertures.Initialisation() 
        self.bouton_ouvertures_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOuvertures_Modifier, self.bouton_ouvertures_modifier)

    def __set_properties(self):
        self.ctrl_ouvertures.SetToolTipString(_(u"Calendrier des ouvertures et du nombre de places"))
        self.bouton_ouvertures_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le calendrier des ouvertures et du nombre de places"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        staticbox_ouvertures = wx.StaticBoxSizer(self.staticbox_ouvertures_staticbox, wx.VERTICAL)
        grid_sizer_ouvertures = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_ouvertures = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_ouvertures.Add(self.ctrl_ouvertures, 1, wx.EXPAND, 0)
        grid_sizer_boutons_ouvertures.Add(self.bouton_ouvertures_modifier, 0, 0, 0)
        grid_sizer_ouvertures.Add(grid_sizer_boutons_ouvertures, 1, wx.EXPAND, 0)
        grid_sizer_ouvertures.AddGrowableRow(0)
        grid_sizer_ouvertures.AddGrowableCol(0)
        staticbox_ouvertures.Add(grid_sizer_ouvertures, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_ouvertures, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonOuvertures_Modifier(self, event):
        import DLG_Ouvertures
        dlg = DLG_Ouvertures.Dialog(self, IDactivite=self.IDactivite)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_ouvertures.MAJ()
        dlg.Destroy()

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
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()