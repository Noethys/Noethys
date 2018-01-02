#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx


def copyDate(value):
	""" Simple method for copy the date (Y,M,D).
	"""
	if 'phoenix' in wx.PlatformInfo:
		date = wx.DateTime.FromDMY(value.GetDay(), value.GetMonth(), value.GetYear())
	else :
		date = wx.DateTimeFromDMY(value.GetDay(), value.GetMonth(), value.GetYear())
	return date
		
def copyDateTime(value):
	""" Return a copy of input wxDateTime object
	"""
	if value.IsValid():
		if 'phoenix' in wx.PlatformInfo:
			fonction = wx.DateTime.FromDMY
		else :
			fonction = wx.DateTimeFromDMY
		return fonction(
			value.GetDay(), 
			value.GetMonth(),
			value.GetYear(),
			value.GetHour(),
			value.GetMinute(),
			value.GetSecond(),
			value.GetMillisecond(),
		)
	else:
		return wx.DateTime()

def setToWeekDayInSameWeek(day, offset, startDay=1):
	"""wxDateTime's    SetToWeekDayInSameWeek   appears    to   be
	buggish. When told that the  week starts on Monday, it results
	in   the  following   'week'  on   Jan,  31st,   2010:  31/01,
	25/01-30/01..."""
	# Loop backwards until we find the start day
	while True:
		if day.GetWeekDay() == startDay:
			break
		if 'phoenix' in wx.PlatformInfo:
			day.Subtract(wx.DateSpan(days=1))
		else :
			day.SubtractDS(wx.DateSpan(days=1))
	if 'phoenix' in wx.PlatformInfo:
		day.Add(wx.DateSpan(days=offset))
	else :
		day.AddDS(wx.DateSpan(days=offset))
	return day
