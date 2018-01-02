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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image


class CTRL(wx.TextCtrl):
    def __init__(self, parent, font=None, size=(-1, -1), style=wx.TE_RIGHT):
        wx.TextCtrl.__init__(self, parent, -1, u"0.00", size=size, style=style)
        self.parent = parent
        self.SetToolTip(wx.ToolTip(_(u"Saisissez un montant")))   
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        if font != None :
            self.SetFont(font)
    
    def OnKillFocus(self, event):
        valide, messageErreur = self.Validation()
        if valide == False :
            wx.MessageBox(messageErreur, "Erreur de saisie")
        else:
            montant = float(self.GetValue())
            self.SetValue(u"%.2f" % montant)
        if event != None : event.Skip() 
    
    def Validation(self):
        # Vérifie si montant vide
        montantStr = self.GetValue()
        try :
            test = float(montantStr)
        except :
            message = _(u"Le montant que vous avez saisi n'est pas valide.")
            return False, message
        return True, None
    
    def SetMontant(self, montant=0.0):
        if montant == None : montant = 0.0
        self.SetValue(u"%.2f" % montant)
    
    def GetMontant(self):
        validation, erreur = self.Validation()
        if validation == True :
            montant = float(self.GetValue()) 
            return montant
        else:
            return None
        
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= CTRL(panel)
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