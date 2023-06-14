#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import six
import datetime
from Utils import UTILS_Dates

if 'phoenix' in wx.PlatformInfo:
    validator = wx.Validator
    IsSilent = wx.Validator.IsSilent
else :
    validator = wx.PyValidator
    IsSilent = wx.Validator_IsSilent


CARACT_AUTORISES = "0123456789-:.hH"

class MyValidator(validator):
    def __init__(self):
        validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return MyValidator()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            if x not in CARACT_AUTORISES :
                return False

        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in CARACT_AUTORISES:
            event.Skip()
            return

        if not IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

    def TransferToWindow(self):
        return True

    def TransfertFromWindow(self):
        return True


#-----------------------------------------------------------------------------------------------------
class CTRL(wx.TextCtrl):
    def __init__(self, parent, separateur="h", font=None, size=(-1, -1), style=wx.TE_PROCESS_ENTER | wx.TE_CENTER):
        wx.TextCtrl.__init__(self, parent, -1, "", size=size, validator=MyValidator(), style=style)
        self.parent = parent
        self.separateur = separateur
        self.SetToolTip(wx.ToolTip(_(u"Saisissez une durée.\n\nExemples de formats acceptés :\n12h45, 6:32, 12.5, 45h, 1725H30")))
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.SetValue(datetime.timedelta(0))
        self.oldValeur = self.GetValue()
        if font != None :
            self.SetFont(font)

    def OnKillFocus(self, event):
        valide, messageErreur = self.Validation()
        if valide == False :
            wx.MessageBox(messageErreur, "Erreur de saisie")
            self.SetDuree(self.oldValeur)
        else:
            self.SetDuree(self.GetDuree())
            self.oldValeur = self.GetDuree()
        if event != None : event.Skip()

    def Validation(self):
        try :
            valeur = self.GetDuree()
        except :
            message = _(u"La durée que vous avez saisi ne semble pas valide.")
            return False, message
        return True, None

    def GetDuree(self, format=datetime.timedelta):
        """ format = datetime.timedelta ou str ou float"""
        valeur = wx.TextCtrl.GetValue(self)
        valeur = valeur.replace(' ','')
        valeur = valeur.replace('h',':')
        valeur = valeur.replace('H',':')
        if valeur == ":" :
            valeur = None

        # Vérifie si c'est un float
        try :
            valeur = float(valeur)
            format = float
        except:
            pass

        # Conversion
        if format == datetime.timedelta :
            return UTILS_Dates.HeureStrEnDelta(valeur)
        elif format == float :
            return datetime.timedelta(hours=valeur)
        else :
            return valeur

    def SetDuree(self, duree=None):
        """ duree = float, str ou timedelta """
        if type(duree) == float :
            td = datetime.timedelta(hours=duree)
        elif type(duree) in (str, six.text_type):
            td = UTILS_Dates.HeureStrEnDelta(duree)
        elif type(duree) == datetime.timedelta :
            td = duree
        else :
            td = datetime.timedelta(0)
        valeur = UTILS_Dates.DeltaEnStr(td, separateur=self.separateur)
        wx.TextCtrl.SetValue(self, valeur)

    def SetValue(self, value=datetime.timedelta(0)):
        self.SetDuree(value)

    def GetValue(self):
        return self.GetDuree()





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.bouton = wx.Button(panel, -1, "TEST")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton, self.bouton)

    def OnBouton(self, event):
        """ Test des formats possibles """
        # Importation des données
        #self.ctrl.SetDuree(datetime.timedelta(hours=123, minutes=0))
        #self.ctrl.SetDuree("12:45")
        #self.ctrl.SetDuree(12.5)
        self.ctrl.SetValue(13.5)

        # Récupération des données
        #print self.ctrl.GetDuree(format=datetime.timedelta)
        #print self.ctrl.GetDuree(format=str)
        #print self.ctrl.GetDuree(format=float)
        print(self.ctrl.GetValue())


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()