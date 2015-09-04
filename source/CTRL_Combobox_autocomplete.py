#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image



class CTRL(wx.ComboBox) :
    def __init__(self, parent):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY)
        self.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.Bind(wx.EVT_KILL_FOCUS, self.EvtFillFocus)
        self.ignoreEvtText = False

    def EvtCombobox(self, event):
        self.ignoreEvtText = True
        event.Skip()

    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def EvtText(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        found = False
        for index in range(0, self.GetCount()) :
            choice = self.GetString(index)
            if choice.lower().startswith(currentText.lower()):
                self.ignoreEvtText = True
                self.SetValue(choice)
                self.SetInsertionPoint(len(currentText))
                self.SetMark(len(currentText), len(choice))
                found = True
                break
        if not found:
            event.Skip()

    def EvtFillFocus(self, event):
        choice = self.GetValue() 
        self.SetStringSelection(choice)
        if self.FindString(choice) == -1 :
            self.SetValue("")#self.SetSelection(0)
        if event != None : 
            event.Skip()
    
    def GetValeur(self):
        """ Permet d'obtenir la valeur en cours de saisie avec wx.EVT_TEXT """
        choice = self.GetValue() 
        for index in range(0, self.GetCount()) :
            if self.GetString(index) == choice :
                return index
        return -1


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="panel_test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl1 = CTRL(panel)
        self.ctrl1.SetItems([_(u"Bonjour"), _(u"Maison"), _(u"Voiture")])
        self.ctrl2 = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl1, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl2, 0, wx.ALL|wx.EXPAND, 4)
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