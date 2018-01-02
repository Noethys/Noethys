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
import wx.lib.masked as masked
import datetime



    
class Heure(masked.TextCtrl):
    def __init__(self, parent, heure_max=24, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TE_CENTRE):
        masked.TextCtrl.__init__(self, parent, id=id, value="", pos=pos, size=size, style=style, mask="##:##", validRegex="[0-2][0-9]:[0-5][0-9]") # formatcodes="T",
        self.parent = parent
        self.heure_max = heure_max
        self.SetMinSize((60, -1))
        self.SetToolTip(wx.ToolTip(_(u"Saisissez une heure")))   
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
    
    def StrEnDatetime(self, texteHeure):
        texteHeure = texteHeure[:5]
        posTemp = texteHeure.index(":")
        heuresTemp = int(texteHeure[:posTemp])
        minutesTemp =  int(texteHeure[posTemp+1:])
        heure = datetime.time(heuresTemp, minutesTemp)
        return heure
    
    def Validation(self):
        texteBrut = self.GetPlainValue()
        if len(texteBrut) != 4 :
            return False
        try :
            if texteBrut == "":
                return False
            # Vérifie chaque chiffre
            for chiffre in texteBrut:
                if chiffre != " ":
                    if not (0 <= int(chiffre) <=9):
                        return False
                else:
                    return False
            # Vérification de l'ensemble de la date
            if not (0<= int(texteBrut[:2]) <=self.heure_max):
                return False
            if not (0<= int(texteBrut[-2:]) <=59):
                return False
            return True
        except :
            return False

    def SetHeure(self, heure):
        if heure == None :
            return
        self.SetValue(heure)
    
    def GetHeure(self):
        heure = self.GetValue()
        if heure == "  :  " :
            return None
        else:
            return heure
        
    def OnKillFocus(self, event):
        self.Validation()
        event.Skip()


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl1 = Heure(panel)
        self.ctrl2 = Heure(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl1, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl2, 1, wx.ALL|wx.EXPAND, 4)
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