#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
from wx.lib.masked import BaseMaskedTextCtrl
import datetime
import UTILS_Dates



class CTRL(BaseMaskedTextCtrl):
    def __init__( self, parent, id=-1, value = '',
                  pos = wx.DefaultPosition,
                  size = wx.DefaultSize,
                  style = wx.TE_PROCESS_TAB | wx.TE_CENTRE,
                  validator = wx.DefaultValidator,
                  name = 'ctrl_duree',
                  setupEventHandling = True,        ## setup event handling by default
                  **kwargs):

        if not kwargs.has_key('mask'):
           kwargs['mask'] = mask = "####:##"
        if not kwargs.has_key('formatcodes'):
            kwargs['formatcodes'] = 'FSr<>'
        if not kwargs.has_key('validRegex'):
            kwargs['validRegex'] = "[ 0-9][ 0-9][ 0-9][0-9]:[0-5][0-9]"

        BaseMaskedTextCtrl.__init__(
                self, parent, id=id, value = value,
                pos=pos, size=size,
                style = style,
                validator = validator,
                name = name,
                setupEventHandling = setupEventHandling,
                **kwargs)

        # Binds
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        # This makes '.' act like tab:
        self._AddNavKey(':', handler=self.OnDot)
        self._AddNavKey('h', handler=self.OnDot)
        self._AddNavKey('.', handler=self.OnDot)

    def OnKillFocus(self, event):
        valide, messageErreur = self.Validation()
        if valide == False :
            wx.MessageBox(messageErreur, "Erreur de saisie")
        if event != None : event.Skip()

    def Validation(self):
        try :
            valeur = self.GetDuree(format=datetime.timedelta)
        except :
            message = _(u"La durée que vous avez saisi ne semble pas valide.")
            return False, message
        return True, None

    def OnDot(self, event):
        pos = self._adjustPos(self._GetInsertionPoint(), event.GetKeyCode())
        oldvalue = self.GetValue()
        edit_start, edit_end, slice = self._FindFieldExtent(pos, getslice=True)
        if not event.ShiftDown():
            if pos > edit_start and pos < edit_end:
                # clip data in field to the right of pos, if adjusting fields
                # when not at delimeter; (assumption == they hit '.')
                newvalue = oldvalue[:pos] + ' ' * (edit_end - pos) + oldvalue[edit_end:]
                self._SetValue(newvalue)
                self._SetInsertionPoint(pos)
        return self._OnChangeField(event)


    def GetDuree(self, format=datetime.timedelta):
        """ format = datetime.timedelta ou str ou float"""
        valeur = BaseMaskedTextCtrl.GetValue(self)
        valeur = valeur.replace(' ','')
        # Conversion
        if format == datetime.timedelta :
            return UTILS_Dates.HeureStrEnDelta(valeur)
        elif format == float :
            td = UTILS_Dates.HeureStrEnDelta(valeur)
            return UTILS_Dates.DeltaEnHeures(td)
        else :
            return valeur


    def SetDuree(self, duree=None):
        """ duree = float, str ou timedelta """
        if type(duree) == float :
            td = datetime.timedelta(hours=duree)
        elif type(duree) in (str, unicode)  :
            td = UTILS_Dates.HeureStrEnDelta(duree)
        elif type(duree) == datetime.timedelta :
            td = duree
        else :
            td = datetime.timedelta(0)
        heures = (td.days*24) + (td.seconds/3600)
        minutes = td.seconds%3600/60
        valeur = "{: >4}:{:0>2}".format(heures, minutes)
        BaseMaskedTextCtrl.SetValue(self, valeur)


        


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
        self.ctrl.SetDuree(12.5)

        # Récupération des données
        #print self.ctrl.GetDuree(format=datetime.timedelta)
        #print self.ctrl.GetDuree(format=str)
        print self.ctrl.GetDuree(format=float)


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()