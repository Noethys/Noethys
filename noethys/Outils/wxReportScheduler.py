#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerPrint import *
import calendar
import wx


class wxReportScheduler( wx.Printout ):
    """
    This is a class which demonstrate how to use the in-memory wxSchedulerPrint() 
    object on wxPython printing framework.
    You can control wxScheduler in the same way on GUI.
    For other info on wxPrintOut class and methods check the wxPython 
    documentation (RTFM for nerds ;-) ).
    """
    def __init__( self, format, style, drawerClass, day, weekstart, periodCount, schedules, joursSpeciaux, reglages):
        self._format	= format
        self._style = style
        self._drawerClass = drawerClass
        self._day		= day
        self._schedules	= schedules
        self._weekstart = weekstart
        self._periodCount = periodCount
        self.pages		= 1
        
        self.joursSpeciaux = joursSpeciaux
        self.reglages = reglages
        
        wx.Printout.__init__(self)

    def _GetScheduler( self, dc, day ):
        """
        Return an in-memory wxSchedulerPrint() object for adding 
        schedules and print on current wxDC
        """

        scheduler = wxSchedulerPrint(dc, self.joursSpeciaux, self.reglages)
        scheduler.SetViewType( self._format )
        scheduler.SetStyle( self._style )
        scheduler.SetDrawer( self._drawerClass )
        scheduler.SetDate( day )
        scheduler.SetWeekStart( self._weekstart )
        scheduler.SetPeriodCount( self._periodCount )

        for schedule in self._schedules:
            scheduler.Add( schedule )
        
        return scheduler

    def OnPrintPage( self, page ):
        """
        This code draw a wxScheduler scaled to fit page using date, format and 
        schedules passed by the user.
        Note there is no difference on manage scheduler and schedules beetwen 
        GUI and printing framework
        """

        dc = self.GetDC()
        scheduler = self._GetScheduler( dc, self._day )

        scheduler.Draw( None )
        scheduler.Draw( page )

        return True

    def HasPage( self, page ):
        return page <= self.pages

    def GetPageInfo( self ):
        dc = self.GetDC()
        scheduler = self._GetScheduler( dc, self._day )

        scheduler.Draw( None )

        self.pages = scheduler.pageCount

        return ( 1, self.pages, 1, 1 )
