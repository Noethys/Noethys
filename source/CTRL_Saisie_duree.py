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
from wx.lib.masked import BaseMaskedTextCtrl, TextCtrl
import datetime
import UTILS_Dates


CARACT_AUTORISES = "0123456789-:.hH"

class MyValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
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

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return


#-----------------------------------------------------------------------------------------------------
class CTRL(wx.TextCtrl):
    def __init__(self, parent, font=None, size=(-1, -1), style=wx.TE_PROCESS_ENTER | wx.TE_CENTER):
        wx.TextCtrl.__init__(self, parent, -1, u"0:00", size=size, validator=MyValidator(), style=style)
        self.parent = parent
        self.SetToolTipString(_(u"Saisissez une durée.\n\nExemples de formats acceptés :\n12h45, 6:32, 12.5, 45h, 1725H30"))
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.oldValeur = "0:00"
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
        elif type(duree) in (str, unicode)  :
            td = UTILS_Dates.HeureStrEnDelta(duree)
        elif type(duree) == datetime.timedelta :
            td = duree
        else :
            td = datetime.timedelta(0)
        heures = (td.days*24) + (td.seconds/3600)
        minutes = td.seconds%3600/60
        valeur = "{}:{:0>2}".format(heures, minutes)
        wx.TextCtrl.SetValue(self, valeur)

    def SetValue(self, value=datetime.timedelta(0)):
        self.SetDuree(value)

    def GetValue(self):
        return self.GetDuree()





# class CTRL2(TextCtrl):
#     def __init__( self, parent, id=-1, value = '',
#                   pos = wx.DefaultPosition,
#                   size = wx.DefaultSize,
#                   style = wx.TE_PROCESS_TAB | wx.TE_CENTRE,
#                   validator = wx.DefaultValidator,
#                   name = 'ctrl_duree',
#                   setupEventHandling = True,        ## setup event handling by default
#                   **kwargs):
#
#         if not kwargs.has_key('mask'):
#            kwargs['mask'] = mask = "#{4}:#{2}"
#         if not kwargs.has_key('formatcodes'):
#             kwargs['formatcodes'] = '-Sr<>'
#         if not kwargs.has_key('validRegex'):
#             kwargs['validRegex'] = "[ 0-9][ 0-9][ 0-9][0-9]:[0-5][0-9]"
#
#         TextCtrl.__init__(
#                 self, parent, id=id, value = value,
#                 pos=pos, size=size,
#                 style = style,
#                 validator = validator,
#                 name = name,
#                 setupEventHandling = setupEventHandling,
#                 **kwargs)
#
#         # Binds
#         self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
#
#         # This makes '.' act like tab:
#         self._AddNavKey(':', handler=self.OnDot)
#         self._AddNavKey('h', handler=self.OnDot)
#         self._AddNavKey('.', handler=self.OnDot)
#
#     def OnKillFocus(self, event):
#         valide, messageErreur = self.Validation()
#         if valide == False :
#             wx.MessageBox(messageErreur, "Erreur de saisie")
#         if event != None : event.Skip()
#
#     def Validation(self):
#         try :
#             valeur = self.GetDuree(format=datetime.timedelta)
#         except :
#             message = _(u"La durée que vous avez saisi ne semble pas valide.")
#             return False, message
#         return True, None
#
#     def OnDot(self, event):
#         pos = self._adjustPos(self._GetInsertionPoint(), event.GetKeyCode())
#         oldvalue = TextCtrl.GetValue(self)
#         edit_start, edit_end, slice = self._FindFieldExtent(pos, getslice=True)
#         if not event.ShiftDown():
#             if pos > edit_start and pos < edit_end:
#                 # clip data in field to the right of pos, if adjusting fields
#                 # when not at delimeter; (assumption == they hit '.')
#                 newvalue = oldvalue[:pos] + ' ' * (edit_end - pos) + oldvalue[edit_end:]
#                 self._SetValue(newvalue)
#                 self._SetInsertionPoint(pos)
#         return self._OnChangeField(event)
#
#
#     def GetDuree(self, format=datetime.timedelta):
#         """ format = datetime.timedelta ou str ou float"""
#         valeur = wx.TextCtrl.GetValue(self)
#         valeur = valeur.replace(' ','')
#         if valeur == ":" :
#             valeur = None
#         # Conversion
#         if format == datetime.timedelta :
#             return UTILS_Dates.HeureStrEnDelta(valeur)
#         elif format == float :
#             td = UTILS_Dates.HeureStrEnDelta(valeur)
#             return UTILS_Dates.DeltaEnHeures(td)
#         else :
#             return valeur
#
#
#     def SetDuree(self, duree=None):
#         """ duree = float, str ou timedelta """
#         if type(duree) == float :
#             td = datetime.timedelta(hours=duree)
#         elif type(duree) in (str, unicode)  :
#             td = UTILS_Dates.HeureStrEnDelta(duree)
#         elif type(duree) == datetime.timedelta :
#             td = duree
#         else :
#             td = datetime.timedelta(0)
#         heures = (td.days*24) + (td.seconds/3600)
#         minutes = td.seconds%3600/60
#         valeur = "{: >4}:{:0>2}".format(heures, minutes)
#         BaseMaskedTextCtrl.SetValue(self, valeur)




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
        print self.ctrl.GetValue()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()