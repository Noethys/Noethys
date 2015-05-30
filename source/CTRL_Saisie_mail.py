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

    
class Mail(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, "")
        self.parent = parent
        self.SetToolTipString(_(u"Saisissez une adresse mail"))   
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
    
    def OnKillFocus(self, event):
        valide, messageErreur = self.Validation()
        if valide == False :
            dlg = wx.MessageDialog(self, messageErreur, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        if event != None : event.Skip() 
    
    def Validation(self):
        # Vérifie si Email vide
        text = self.GetValue()
        if text != "":
            posAt = text.find("@")
            if posAt == -1:
                message = _(u"L'adresse Email que vous avez saisie n'est pas valide !")
                return False, message
            posPoint = text.rfind(".")
            if posPoint < posAt :
                message = _(u"L'adresse Email que vous avez saisie n'est pas valide !")
                return False, message
        return True, None
    
    def SetMail(self, mail=""):
        if mail == None : return
        self.SetValue(mail)
    
    def GetMail(self):
        mail = self.GetValue() 
        if mail == "" :
            return None
        else:
            return mail
        
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Mail(panel)
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