#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import wx.calendar   
import CTRL_Calendrier     

class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        self.ctrl_calendrier = CTRL_Calendrier.CTRL(self, 
                                                afficheBoutonAnnuel=False, 
                                                multiSelections=False,
                                                bordHaut=5, 
                                                bordBas=5, 
                                                bordLateral=5)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_calendrier, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

        self.ctrl_calendrier.Bind(CTRL_Calendrier.EVT_SELECT_DATES, self.OnDateSelected)
        
    def OnDateSelected(self, event):
        self.GetParent().SetDate(self.GetDate())
    
    def GetDate(self):
        selections = self.ctrl_calendrier.GetSelections() 
        if len(selections) > 0 :
            return selections[0]
        else:
            return None
    
    def SetDate(self, date=None):
        self.ctrl_calendrier.SelectJours([date,])
        

###------------------------------------------------------------------------------------------------------------------------------------
##
##
##class CTRL(wx.Panel):
##    def __init__(self, parent):
##        wx.Panel.__init__(self, parent, -1)
##        self.parent = parent
##        
####        self.locale = wx.Locale(wx.LANGUAGE_FRENCH)
##        self.ctrl_calendrier = wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(), 
##                             style = wx.calendar.CAL_SHOW_HOLIDAYS
##                             | wx.calendar.CAL_MONDAY_FIRST
##                             | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
##                             )
##        self.ctrl_calendrier.SetHoliday(3)
##        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
##        grid_sizer_base.Add(self.ctrl_calendrier, 0, wx.EXPAND, 0)
##        grid_sizer_base.AddGrowableRow(0)
##        grid_sizer_base.AddGrowableCol(0)
##        self.SetSizer(grid_sizer_base)
##        self.Layout()
##
##        self.ctrl_calendrier.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.OnDateSelected)
##        
##        
##    def OnDateSelected(self, event):
##        self.GetParent().SetDate(self.GetDate())
##    
##    def GetDate(self):
##        dateTmp = self.ctrl_calendrier.GetDate()
##        jour = dateTmp.GetDay()
##        mois = dateTmp.GetMonth()+1
##        annee = dateTmp.GetYear()
##        date = datetime.date(annee, mois, jour)
##        return date
##    
##    def SetDate(self, date=None):
##        dateWX = wx.DateTime()
##        dateWX.Set(date.day, month=date.month-1, year=date.year)
##        self.ctrl_calendrier.SetDate(dateWX)
##        
##
##
### --------------------------------------------------------------------------------------------------------------------

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
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


