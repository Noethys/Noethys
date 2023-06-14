#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Bouton_image
import wx.lib.masked as masked
from Utils import UTILS_Config

    
class Tel(masked.TextCtrl):
    def __init__(self, parent, intitule="", mask = "##.##.##.##.##.", size=(-1, -1)):
        """ intitule = domicile | mobile | fax | travail """
        self.mask = UTILS_Config.GetParametre("mask_telephone", "##.##.##.##.##.")
        masked.TextCtrl.__init__(self, parent, -1, "", size=size, style=wx.TE_CENTRE, mask=self.mask)
        self.parent = parent
        self.SetMinSize((125, -1))
        self.SetToolTip(wx.ToolTip(_(u"Saisissez un numéro de %s") % intitule))
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
    
    def OnKillFocus(self, event):
        valide, messageErreur = self.Validation()
        if valide == False :
            wx.MessageBox(messageErreur, "Erreur de saisie")
        if event != None : event.Skip() 
    
    def Validation(self):
        if self.mask == "" : 
            return True, None
        text = self.GetValue()
        # Vérifie si Tél vide
        if text == "" or text == "  .  .  .  .  .":
            return True, None
        # Vérifie si Téléphone valide
        posChiffres = [0, 1, 3, 4, 6, 7, 9, 10, 12, 13]
        for position in posChiffres:
            if text[position].isdigit() == False:
                message = _(u"Le numéro que vous avez saisi ne semble pas valide.")
                return False, message
        return True, None
    
    def SetNumero(self, numero=""):
        if numero == None : return
        try :
            self.SetValue(numero)
        except : 
            pass
    
    def GetNumero(self):
        tel = self.GetValue() 
        if tel == "  .  .  .  .  ." :
            return None
        else:
            return tel
        
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Tel(panel)
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