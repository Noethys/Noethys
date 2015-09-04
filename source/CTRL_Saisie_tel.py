#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.masked as masked
import UTILS_Config

    
class Tel(masked.TextCtrl):
    def __init__(self, parent, intitule="", mask = "##.##.##.##.##."):
        """ intitule = domicile | mobile | fax | travail """
        self.mask = UTILS_Config.GetParametre("mask_telephone", "##.##.##.##.##.")
        masked.TextCtrl.__init__(self, parent, -1, "", style=wx.TE_CENTRE, mask=self.mask)
        self.parent = parent
        self.SetMinSize((125, -1))
        self.SetToolTipString(_(u"Saisissez un num�ro de %s") % intitule)   
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
        # V�rifie si T�l vide
        if text == "" or text == "  .  .  .  .  .":
            return True, None
        # V�rifie si T�l�phone valide
        posChiffres = [0, 1, 3, 4, 6, 7, 9, 10, 12, 13]
        for position in posChiffres:
            if text[position].isdigit() == False:
                message = _(u"Le num�ro que vous avez saisi ne semble pas valide.")
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