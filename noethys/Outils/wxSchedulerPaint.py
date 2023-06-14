#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedule import wxSchedule
from wxDrawer import wxBaseDrawer, wxFancyDrawer
from wxSchedulerCore import *
import calendar
import math
import sys
import wx
import wxScheduleUtils as utils
from six.moves import range as xrange
import six
if six.PY3:
    import functools

if sys.version.startswith( "2.3" ):
	from sets import Set as set

if 'phoenix' in wx.PlatformInfo:
	Sizer = wx.Sizer
else :
	Sizer = wx.PySizer

# Events 
wxEVT_COMMAND_SCHEDULE_ACTIVATED = wx.NewEventType()
EVT_SCHEDULE_ACTIVATED = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_ACTIVATED )

wxEVT_COMMAND_SCHEDULE_RIGHT_CLICK = wx.NewEventType()
EVT_SCHEDULE_RIGHT_CLICK = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_RIGHT_CLICK )

wxEVT_COMMAND_SCHEDULE_DCLICK = wx.NewEventType()
EVT_SCHEDULE_DCLICK = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_DCLICK )

wxEVT_COMMAND_SCHEDULE_MOTION = wx.NewEventType()
EVT_SCHEDULE_MOTION = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_MOTION)

class wxSchedulerSizer(Sizer):
	def __init__(self, minSizeCallback):
		super(wxSchedulerSizer, self).__init__()

		self._minSizeCallback = minSizeCallback

	def CalcMin(self):
		return self._minSizeCallback()

	def RecalcSizes(self, *args, **kwds):
		""" J'ai rajoute cette fonction pour contrer bug avec phoenix """
		pass


# Main class
class wxSchedulerPaint( object ):
	
	def __init__( self, *args, **kwds ):
		super( wxSchedulerPaint, self ).__init__( *args, **kwds )

		self._resizable		= False
		self._style = wxSCHEDULER_VERTICAL

		self._drawerClass = wxBaseDrawer
		self._headerPanel = None

		self._schedulesCoords = list()
		self._schedulesPages = dict()

		self._datetimeCoords = []

		self._bitmap = None
		self._minSize = None
		self._drawHeaders = True

		self.pageNumber = None
		self.pageCount = 1

		if isinstance(self, wx.ScrolledWindow):
			self.SetSizer(wxSchedulerSizer(self.CalcMinSize))

	def _doClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_ACTIVATED, point )

	def _doRightClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_RIGHT_CLICK, point )
		
	def _doDClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_DCLICK, point )

	def _doMotionControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_MOTION, point )

	def _findSchedule( self, point ):
		"""
		Check if the point is on a schedule and return the schedule
		"""
		sched = None
		for schedule, pointMin, pointMax in self._schedulesCoords:
			inX = ( pointMin.x <= point.x ) & ( point.x <= pointMax.x )
			inY = ( pointMin.y <= point.y ) & ( point.y <= pointMax.y )
			
			if inX & inY:
				sched = schedule.GetClientData()

		datet = None
		dateExacte = None
		for dt, pointMin, pointMax in self._datetimeCoords:
			inX = ( pointMin.x <= point.x ) & ( point.x <= pointMax.x )
			inY = ( pointMin.y <= point.y ) & ( point.y <= pointMax.y )
			
			if inX & inY:
				datet = utils.copyDateTime(dt)
				minutes = int(30.0 * (point.y - pointMin.y) / (pointMax.y - pointMin.y)) 
				minutes = minutes - (minutes % 5)
				if 'phoenix' in wx.PlatformInfo:
					dateExacte = datet.Add(wx.TimeSpan(hours=0, min=minutes))
				else :
					dateExacte = datet.AddTS(wx.TimeSpan(minutes=minutes))

		return sched, datet, dateExacte

	def _getSchedInPeriod( schedules, start, end):
		"""
		Returns a list of copied schedules that intersect with
		the  period  defined by	 'start'  and 'end'.  Schedule
		start and end are trimmed so as to lie between 'start'
		and 'end'.
		"""
		results = []

		for schedule in schedules:
			schedule.bounds = None

			if schedule.start.IsLaterThan(end):
				continue
			if start.IsLaterThan(schedule.end):
				continue

			newSchedule = schedule.Clone()
			# This is used to find the original schedule object in _findSchedule.
			newSchedule.clientdata	= schedule

			if start.IsLaterThan(schedule.start):
				newSchedule.start = utils.copyDateTime(start)
			if schedule.end.IsLaterThan(end):
				newSchedule.end = utils.copyDateTime(end)

			results.append(newSchedule)

		return results

	_getSchedInPeriod = staticmethod(_getSchedInPeriod)

	def _splitSchedules( self, schedules ):
		"""
		Returns	 a list	 of lists  of schedules.  Schedules in
		each list are guaranteed not to collide.
		"""
		results = []
		current = []

		schedules = schedules[:] # Don't alter original list
		def compare(a, b):
			if a.start.IsEqualTo(b.start):
				return cmp(a.description, b.description)
			if a.start.IsEarlierThan(b.start):
				return -1
			return 1
		if six.PY2:
			schedules.sort(cmp=(compare))
		else:
			schedules.sort(key=functools.cmp_to_key(compare))

		def findNext(schedule):
			# Among schedules that start after this one ends, find the "nearest".
			candidateSchedule = None
			minDelta = None
			for sched in schedules:
				if sched.start.IsLaterThan(schedule.end) or sched.start.IsEqualTo(schedule.end):
					delta = sched.start.Subtract(schedule.end)
					if minDelta is None or minDelta > delta:
						minDelta = delta
						candidateSchedule = sched
			return candidateSchedule

		while schedules:
			schedule = schedules[0]
			while schedule:
				current.append(schedule)
				schedules.remove(schedule)
				schedule = findNext(schedule)
			results.append(current)
			current = []

		return results

	def _paintPeriod(self, drawer, start, daysCount, x, y, width, height):
		end = utils.copyDateTime(start)
		if 'phoenix' in wx.PlatformInfo:
			end.Add(wx.DateSpan(days=daysCount))
		else :
			end.AddDS(wx.DateSpan(days=daysCount))

		blocks = self._splitSchedules(self._getSchedInPeriod(self._schedules, start, end))
		offsetY = 0

		if self._showOnlyWorkHour:
			workingHours = [(self._startingHour, self._startingPauseHour),
					(self._endingPauseHour, self._endingHour)]
		else:
			workingHours = [(self._startingHour, self._endingHour)]

		if not self.pageNumber:
			self.pageCount = 1
			self.pageLimits = [0]

			pageHeight = self.GetSize().GetHeight() - 20
			currentPageHeight = y

		for dayN in xrange(daysCount):
			theDay = utils.copyDateTime(start)
			if 'phoenix' in wx.PlatformInfo:
				theDay.Add(wx.DateSpan(days=dayN))
			else :
				theDay.AddDS(wx.DateSpan(days=dayN))

			# Recherche la couleur par dÃ©faut pour le jour
			highlight = False
			if self._viewType != wxSCHEDULER_DAILY :
				highlight = theDay.IsSameDate( wx.DateTime.Now() )

			# Recherche si c'est un jour fÃ©riÃ© ou un jour de vacances
			if self.joursSpeciaux != None and self._viewType != wxSCHEDULER_DAILY and highlight == False :
				couleur = self.joursSpeciaux.GetCouleur(theDay)
				if couleur != None :
					highlight = couleur

			drawer.DrawDayBackground( x + 1.0 * width / daysCount * dayN, y, 1.0 * width / daysCount, height, highlight=highlight)

		if blocks:
			dayWidth = width / len(blocks)

			for idx, block in enumerate(blocks):
				maxDY = 0

				for schedule in block:
					show = True
					if self.pageNumber is not None:
						if self._schedulesPages.get(schedule.GetId(), None) != self.pageNumber:
							show = False

					if show:
						if self._style == wxSCHEDULER_VERTICAL:
							xx, yy, w, h = drawer.DrawScheduleVertical(schedule, start, workingHours,
												   x + dayWidth * idx, y,
												   dayWidth, height)
						elif self._style == wxSCHEDULER_HORIZONTAL:
							xx, yy, w, h = drawer.DrawScheduleHorizontal(schedule, start, daysCount, workingHours,
												     x, y + offsetY, width, height)
							maxDY = max(maxDY, h)

						if self.pageNumber is None:
							if currentPageHeight + h >= pageHeight:
								pageNo = self.pageCount + 1
							else:
								pageNo = self.pageCount

							self._schedulesPages[schedule.GetId()] = pageNo

						self._schedulesCoords.append((schedule, wx.Point(xx, yy), wx.Point(xx + w, yy + h)))

				offsetY += maxDY

				if not self.pageNumber:
					currentPageHeight += maxDY
					if currentPageHeight >= pageHeight:
						self.pageLimits.append(currentPageHeight - maxDY)
						currentPageHeight = maxDY
						self.pageCount += 1

		for dayN in xrange(daysCount):
			theDay = utils.copyDateTime(start)
			if 'phoenix' in wx.PlatformInfo:
				theDay.Add(wx.DateSpan(days=dayN))
			else :
				theDay.AddDS(wx.DateSpan(days=dayN))
			theDay.SetSecond(0)

			nbHours = len(self._lstDisplayedHours)

			for idx, hour in enumerate(self._lstDisplayedHours):
				theDay.SetHour(hour.GetHour())
				theDay.SetMinute(hour.GetMinute())

				if self._style == wxSCHEDULER_VERTICAL:
					self._datetimeCoords.append((utils.copyDateTime(theDay),
								     wx.Point(x + 1.0 * width * dayN / daysCount,
									      y + 1.0 * height * idx / nbHours),
								     wx.Point(x + 1.0 * width * (dayN + 1) / daysCount,
									      y + 1.0 * height * (idx + 1) / nbHours)))
				else:
					self._datetimeCoords.append((utils.copyDateTime(theDay),
								     wx.Point(x + 1.0 * width * (nbHours * dayN + idx) / (nbHours * daysCount),
									      y),
								     wx.Point(x + 1.0 * width * (nbHours * dayN + idx + 1) / (nbHours * daysCount),
									      y + height)))

		if self._style == wxSCHEDULER_VERTICAL:
			return max(width, DAY_SIZE_MIN.width), max(height, DAY_SIZE_MIN.height)
		else:
			return max(width, DAY_SIZE_MIN.width), offsetY

	def _paintDay( self, drawer, day, x, y, width, height ):
		"""
		Draw column schedules
		"""

		start = utils.copyDateTime(day)
		start.SetHour(0)
		start.SetMinute(0)
		start.SetSecond(0)

		return self._paintPeriod(drawer, start, 1, x, y, width, height)

	def _paintDailyHeaders( self, drawer, day, x, y, width, height, includeText=True ):
		if includeText:
			w, h = drawer.DrawDayHeader(day, x, y, width, height)
		else:
			w, h = width, 0

		if not (self._style == wxSCHEDULER_VERTICAL or self._drawHeaders):
			hw, hh = drawer.DrawHours(x, y + h, width, height - h, self._style, includeText=includeText)
			h += hh

		return w, h

	def _paintDaily( self, drawer, day, x, y, width, height ):
		"""
		Display day schedules
		"""

		minWidth = minHeight = 0

		if self._style == wxSCHEDULER_VERTICAL:
			x += LEFT_COLUMN_SIZE
			width -= LEFT_COLUMN_SIZE

		theDay = utils.copyDateTime(day)

		if self._drawHeaders:
			maxDY = 0
			for idx in xrange(self._periodCount):
				w, h = self._paintDailyHeaders( drawer, theDay, x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, height)
				maxDY = max(maxDY, h)
				if 'phoenix' in wx.PlatformInfo:
					theDay.Add(wx.DateSpan(days=1))
				else :
					theDay.AddDS(wx.DateSpan(days=1))
			minHeight += maxDY
			y += maxDY
			height -= maxDY
		else:
			for idx in xrange(self._periodCount):
				self._paintDailyHeaders( drawer, theDay, x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, height, includeText=False )
				if 'phoenix' in wx.PlatformInfo:
					theDay.Add(wx.DateSpan(days=1))
				else :
					theDay.AddDS(wx.DateSpan(days=1))

		if self._style == wxSCHEDULER_VERTICAL:
			x -= LEFT_COLUMN_SIZE
			width += LEFT_COLUMN_SIZE

		if self._style == wxSCHEDULER_VERTICAL or self._drawHeaders:
			if self._style == wxSCHEDULER_VERTICAL:
				w, h = drawer.DrawHours(x, y, width, height, self._style)
			else:
				maxDY = 0
				for idx in xrange(self._periodCount):
					_, h = drawer.DrawHours(x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, height, self._style)
					maxDY = max(maxDY, h)
				w = 0
				h = maxDY
		else:
			w, h = 0, 0

		if self._style == wxSCHEDULER_VERTICAL:
			minWidth += w
			x += w
			width -= w
		else:
			minHeight += h
			y += h
			height -= h

		if self._style == wxSCHEDULER_HORIZONTAL:
			# Use directly paintPeriod or pagination fails
			w, h = self._paintPeriod(drawer, day, self._periodCount, x, y, width, height)
		else:
			w = 0
			maxDY = 0
			theDay = utils.copyDateTime(day)
			for idx in xrange(self._periodCount):
				dw, dh = self._paintDay( drawer, theDay, x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, height )
				w += dw
				maxDY = max(maxDY, dh)
				if 'phoenix' in wx.PlatformInfo:
					theDay.Add(wx.DateSpan(days=1))
				else :
					theDay.AddDS(wx.DateSpan(days=1))

		minWidth += w
		minHeight += h

		return minWidth, minHeight

	def _paintWeeklyHeaders( self, drawer, day, x, y, width, height ):
		firstDay = utils.setToWeekDayInSameWeek( day, 0, self._weekstart )
		firstDay.SetHour(0)
		firstDay.SetMinute(0)
		firstDay.SetSecond(0)

		maxDY = 0

		for weekday in xrange(7):
			theDay = utils.setToWeekDayInSameWeek(utils.copyDateTime(firstDay), weekday, self._weekstart)

			# Recherche la couleur par dÃ©faut pour le jour
			highlight = theDay.IsSameDate( wx.DateTime.Now() )
			if self.joursSpeciaux != None and highlight == False :
				couleur = self.joursSpeciaux.GetCouleur(theDay)
				if couleur != None : highlight = couleur

			w, h = drawer.DrawDayHeader(theDay, x + weekday * 1.0 * width / 7, y, 1.0 * width / 7, height, highlight=highlight)
			maxDY = max(maxDY, h)

		return maxDY

	def _paintWeekly( self, drawer, day, x, y, width, height ):
		"""
		Display weekly schedule
		"""

		firstDay = utils.setToWeekDayInSameWeek( day, 0, self._weekstart )
		firstDay.SetHour(0)
		firstDay.SetMinute(0)
		firstDay.SetSecond(0)

		minWidth = minHeight = 0

		if self._style == wxSCHEDULER_VERTICAL:
			x += LEFT_COLUMN_SIZE
			width -= LEFT_COLUMN_SIZE

		maxDY = 0

		if self._drawHeaders:
			theDay = utils.copyDateTime(day)
			for idx in xrange(self._periodCount):
				maxDY = max(maxDY, self._paintWeeklyHeaders( drawer, theDay, x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, height ))
				if 'phoenix' in wx.PlatformInfo:
					theDay.Add(wx.DateSpan(weeks=1))
				else :
					theDay.AddDS(wx.DateSpan(weeks=1))

		if self._style == wxSCHEDULER_VERTICAL:
			x -= LEFT_COLUMN_SIZE
			width += LEFT_COLUMN_SIZE

		minHeight += maxDY
		y += maxDY
		height -= maxDY

		if self._style == wxSCHEDULER_VERTICAL:
			w, h = drawer.DrawHours(x, y, width, height, self._style)

			minWidth += w
			x += w
			width -= w

			day = utils.copyDateTime(firstDay)

			for idx in xrange(self._periodCount):
				for weekday in xrange(7):
					theDay = utils.setToWeekDayInSameWeek(utils.copyDateTime(day), weekday, self._weekstart)
					self._paintDay(drawer, theDay, x + (weekday + 7 * idx) * 1.0 * width / 7 / self._periodCount, y, 1.0 * width / 7 / self._periodCount, height)
				if 'phoenix' in wx.PlatformInfo:
					day.Add(wx.DateSpan(weeks=1))
				else :
					day.AddDS(wx.DateSpan(weeks=1))

			return max(WEEK_SIZE_MIN.width * self._periodCount + LEFT_COLUMN_SIZE, width), max(WEEK_SIZE_MIN.height, height)
		else:
			w, h = self._paintPeriod(drawer, firstDay, 7 * self._periodCount, x, y, width, height)

			minWidth += w
			minHeight += h

			return max(WEEK_SIZE_MIN.width * self._periodCount + LEFT_COLUMN_SIZE, minWidth), minHeight

	def _paintMonthlyHeaders( self, drawer, day, x, y, width, height ):
		w, h = drawer.DrawMonthHeader(day, x, y, width, height)

		if self._style == wxSCHEDULER_HORIZONTAL:
			day.SetDay(1)
			day.SetHour(0)
			day.SetMinute(0)
			day.SetSecond(0)

			daysCount = wx.DateTime.GetNumberOfDaysInMonth(day.GetMonth())

			maxDY = 0
			for idx in xrange(daysCount):
				theDay = utils.copyDateTime(day)
				if 'phoenix' in wx.PlatformInfo:
					theDay.Add(wx.DateSpan(days=idx))
				else :
					theDay.AddDS(wx.DateSpan(days=idx))

				# Recherche la couleur par dÃ©faut pour le jour
				highlight = theDay.IsSameDate( wx.DateTime.Now() )
				if self.joursSpeciaux != None and highlight == False :
					couleur = self.joursSpeciaux.GetCouleur(theDay)
					if couleur != None : highlight = couleur

				w, h = drawer.DrawSimpleDayHeader(theDay, x + 1.0 * idx * width / daysCount,
								  y + h, 1.0 * width / daysCount, height, highlight)
				maxDY = max(maxDY, h)

			h += maxDY

		return w, h

	def _paintMonthly( self, drawer, day, x, y, width, height):
		"""
		Draw month's calendar using calendar module functions
		"""

		if self._drawHeaders:
			w, h = self._paintMonthlyHeaders( drawer, day, x, y, width, height)
		else:
			w, h = width, 0

		y += h
		height -= h

		if self._style == wxSCHEDULER_VERTICAL:
			month = calendar.monthcalendar( day.GetYear(), day.GetMonth() + 1 )

			for w, monthWeek in enumerate( month ):
				for d, monthDay in enumerate( monthWeek ):
					cellW, cellH = 1.0 * width / 7, 1.0 * height / len(month)

					if monthDay == 0:
						theDay = None
						schedules = []
						highlight = False
					else:
						theDay = day
						theDay.SetDay(monthDay)
						theDay.SetHour(0)
						theDay.SetMinute(0)
						theDay.SetSecond(0)

						end = utils.copyDateTime(theDay)
						if 'phoenix' in wx.PlatformInfo:
							end.Add(wx.DateSpan(days=1))
						else :
							end.AddDS(wx.DateSpan(days=1))

						schedules = self._getSchedInPeriod(self._schedules, theDay, end)


						# Recherche la couleur par dÃ©faut pour le jour
						highlight = theDay.IsSameDate( wx.DateTime.Now() )
						if self.joursSpeciaux != None and highlight == False :
							couleur = self.joursSpeciaux.GetCouleur(theDay)
							if couleur != None : highlight = couleur

						self._datetimeCoords.append((utils.copyDateTime(theDay),
									     wx.Point(d * cellW, w * cellH),
									     wx.Point(d * cellW + cellW, w * cellH + cellH)))

					self._schedulesCoords.extend(drawer.DrawSchedulesCompact(theDay, schedules, d * cellW, w * cellH + y, cellW, cellH, highlight))

			return (max(MONTH_CELL_SIZE_MIN.width * 7, width),
				max(MONTH_CELL_SIZE_MIN.height * (w + 1), height))
		else:
			day.SetDay(1)
			day.SetHour(0)
			day.SetMinute(0)
			day.SetSecond(0)

			daysCount = wx.DateTime.GetNumberOfDaysInMonth(day.GetMonth())

			minHeight = h

			w, h = self._paintPeriod(drawer, day, daysCount, x, y, width, height)
			minHeight += h

			return w, minHeight

	def _processEvt( self, commandEvent, point ):
		""" 
		Process the command event passed at the given point
		"""
		evt = wx.PyCommandEvent( commandEvent )
		mySch, myDate, dateExacte = self._findSchedule( point )
		evt.schedule = mySch
		evt.date = myDate
		evt.dateExacte = dateExacte
		evt.SetEventObject( self )
		self.ProcessEvent( evt ) 

	def DoPaint(self, drawer, x, y, width, height):
		self._schedulesCoords = list()
		self._datetimeCoords = list()

		day = utils.copyDate(self.GetDate())

		if self._viewType == wxSCHEDULER_DAILY:
			return self._paintDaily(drawer, day, x, y, width, height)
		elif self._viewType == wxSCHEDULER_WEEKLY:
			return self._paintWeekly(drawer, day, x, y, width, height)
		elif self._viewType == wxSCHEDULER_MONTHLY:
			return self._paintMonthly(drawer, day, x, y, width, height)

	def GetViewSize(self):
		# Used by wxSchedulerReport

		size = self.GetSize()
		minSize = self.CalcMinSize()

		return wx.Size(max(size.width, minSize.width), max(size.height, minSize.height))

	def _CalcMinSize(self):
		if self._viewType == wxSCHEDULER_DAILY:
			minW, minH = DAY_SIZE_MIN.width, DAY_SIZE_MIN.height
		elif self._viewType == wxSCHEDULER_WEEKLY:
			minW, minH = WEEK_SIZE_MIN.width, WEEK_SIZE_MIN.height
		elif self._viewType == wxSCHEDULER_MONTHLY:
			minW, minH = MONTH_CELL_SIZE_MIN.width * 7, 0 # will be computed

		if self._viewType == wxSCHEDULER_MONTHLY or self._style == wxSCHEDULER_HORIZONTAL:
			memDC = wx.MemoryDC()
			if 'phoenix' in wx.PlatformInfo:
				bmp = wx.Bitmap(1, 1)
			else :
				bmp = wx.EmptyBitmap(1, 1)
			memDC.SelectObject(bmp)
			try:
				if self._drawerClass.use_gc:
					context = wx.GraphicsContext.Create(memDC)
					context.SetFont(wx.NORMAL_FONT, wx.BLACK)
				else:
					context = memDC

				if isinstance(self, wx.ScrolledWindow):
					size = self.GetVirtualSize()
				else:
					size = self.GetSize()

				# XXXFIXME: find a better way not to alter coordinates...
				tmpCoords = self._datetimeCoords[:]

				# Actually, only the min height may vary...
				_, minH = self.DoPaint(self._drawerClass(context, self._lstDisplayedHours),
						       0, 0, size.GetWidth(), 0)

				self._datetimeCoords = tmpCoords

				if self._style == wxSCHEDULER_HORIZONTAL:
					if self._viewType == wxSCHEDULER_WEEKLY:
						minW = 200 * 7
					elif self._viewType == wxSCHEDULER_MONTHLY:
						return wx.Size(200 * wx.DateTime.GetNumberOfDaysInMonth(self.GetDate().GetMonth()), minH)
				elif self._viewType == wxSCHEDULER_MONTHLY:
					return wx.Size(minW, minH)
			finally:
				memDC.SelectObject(wx.NullBitmap)
		elif self._style == wxSCHEDULER_VERTICAL:
			return wx.Size(minW * self._periodCount + LEFT_COLUMN_SIZE, minH)

		return wx.Size(minW * self._periodCount, minH)

	def CalcMinSize(self):
		if self._minSize is None:
			self._minSize = self._CalcMinSize()
		return self._minSize

	def InvalidateMinSize(self):
		self._minSize = None

	def DrawBuffer( self ):
		if isinstance(self, wx.ScrolledWindow):
			if self._resizable:
				size = self.GetVirtualSize()
			else:
				size = self.CalcMinSize()
		else:
			size = self.GetSize()

		if 'phoenix' in wx.PlatformInfo:
			self._bitmap = wx.Bitmap(size.GetWidth(), size.GetHeight())
		else :
			self._bitmap = wx.EmptyBitmap(size.GetWidth(), size.GetHeight())
		memDC = wx.MemoryDC()
		memDC.SelectObject(self._bitmap)
		try:
			if 'phoenix' not in wx.PlatformInfo:
				memDC.BeginDrawing()
			try:
				memDC.SetBackground( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )
				memDC.SetPen( FOREGROUND_PEN )
				memDC.Clear()
				memDC.SetFont(wx.NORMAL_FONT)

				if self._drawerClass.use_gc:
					context = wx.GraphicsContext.Create(memDC)
				else:
					context = memDC

				width, height = self.DoPaint(self._drawerClass(context, self._lstDisplayedHours),
							     0, 0, size.GetWidth(), size.GetHeight())
			finally:
				if 'phoenix' not in wx.PlatformInfo:
					memDC.EndDrawing()
		finally:
			memDC.SelectObject(wx.NullBitmap)

		# Bad things may happen here from time to time.
		if isinstance(self, wx.ScrolledWindow):
			if self._resizable:
				if int(width) > size.GetWidth() or int(height) > size.GetHeight():
					self.SetVirtualSize(wx.Size(int(width), int(height)))
					self.DrawBuffer()

	def RefreshSchedule( self, schedule ):
		if schedule.bounds is not None:
			memDC = wx.MemoryDC()
			memDC.SelectObject(self._bitmap)
			try:
				if 'phoenix' not in wx.PlatformInfo:
					memDC.BeginDrawing()
				memDC.SetBackground( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )
				memDC.SetPen( FOREGROUND_PEN )
				memDC.SetFont(wx.NORMAL_FONT)

				if self._drawerClass.use_gc:
					context = wx.GraphicsContext.Create(memDC)
				else:
					context = memDC

				self._drawerClass(context, self._lstDisplayedHours)._DrawSchedule(schedule, *schedule.bounds)
			finally:
				memDC.SelectObject(wx.NullBitmap)

			originX, originY = self.GetViewStart()
			unitX, unitY = self.GetScrollPixelsPerUnit()
			x, y, w, h = schedule.bounds
			self.RefreshRect(wx.Rect(math.floor(x - originX * unitX) - 1, math.floor(y - originY * unitY) - 1,
						 math.ceil(w) + 2, math.ceil(h) + 2))

	def OnPaint( self, evt = None ):
		# Do the draw

		if self._dc:
			dc = self._dc
		else:
			dc = wx.PaintDC(self)
			self.PrepareDC(dc)

		if 'phoenix' not in wx.PlatformInfo:
			dc.BeginDrawing()
		try:
			dc.DrawBitmap(self._bitmap, 0, 0, False)
		finally:
			if 'phoenix' not in wx.PlatformInfo:
				dc.EndDrawing()

	def SetResizable( self, value ):
		"""
		Draw proportionally of actual space but not down on minimun sizes
		The actual sze is retrieved by GetSize() method of derived object
		"""
		self._resizable = bool( value )

	def SetStyle(self, style):
		"""
		Sets  the drawing  style.  Values  for 'style'	may be
		wxSCHEDULER_VERTICAL	   (the	      default)	    or
		wxSCHEDULER_HORIZONTAL.
		"""
		self._style = style
		self.InvalidateMinSize()
		self.Refresh()

	def GetStyle( self ):
		"""
		Returns the current drawing style.
		"""
		return self._style

	def SetDrawer(self, drawerClass):
		"""
		Sets the drawer class.
		"""
		self._drawerClass = drawerClass
		self.InvalidateMinSize()
		self.Refresh()

	def GetDrawer(self):
		return self._drawerClass

	def Refresh( self ):
		self.DrawBuffer()
		super( wxSchedulerPaint, self ).Refresh()
		if self._headerPanel is not None:
			self._headerPanel.Refresh()

	def SetHeaderPanel( self, panel ):
		"""
		Call this with an instance of wx.Panel. The headers
		will then be painted on this panel, and thus will be
		unaffected by vertical scrolling. The panel will be
		resized as needed.
		"""

		self._drawHeaders = False
		self._headerPanel = panel

		panel.Bind( wx.EVT_PAINT, self._OnPaintHeaders )
		panel.SetSize(wx.Size(-1, 1))
		self.Bind(wx.EVT_SCROLLWIN, self._OnScroll)

		panel.Refresh()

	# Headers stuff

	def _OnPaintHeaders( self, evt ):
		dc = wx.PaintDC( self._headerPanel )
		if 'phoenix' not in wx.PlatformInfo:
			dc.BeginDrawing()
		try:
			dc.SetBackground( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )
			dc.SetPen( FOREGROUND_PEN )
			dc.Clear()
			dc.SetFont( wx.NORMAL_FONT )

			if self._drawerClass.use_gc:
				context = wx.GraphicsContext.Create(dc)
			else:
				context = dc

			drawer = self._drawerClass(context, self._lstDisplayedHours)

			if self._resizable:
				width, _ = self.GetVirtualSize()
			else:
				width, _ = self.CalcMinSize()

			day = utils.copyDate(self.GetDate())

			x, y = 0, 0

			# Take horizontal scrolling into account
			x0, _ = self.GetViewStart()
			xu, _ = self.GetScrollPixelsPerUnit()
			x0 *= xu
			x -= x0

			if self._viewType == wxSCHEDULER_DAILY:
				if self._style == wxSCHEDULER_VERTICAL:
					x += LEFT_COLUMN_SIZE
					width -= LEFT_COLUMN_SIZE
				theDay = utils.copyDateTime(day)
				maxDY = 0
				for idx in xrange(self._periodCount):
					_, h = self._paintDailyHeaders(drawer, theDay, x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, 36)
					maxDY = max(maxDY, h)
					theDay.AddDS(wx.DateSpan(days=1))
				h = maxDY
			elif self._viewType == wxSCHEDULER_WEEKLY:
				if self._style == wxSCHEDULER_VERTICAL:
					x += LEFT_COLUMN_SIZE
					width -= LEFT_COLUMN_SIZE
				theDay = utils.copyDateTime(day)
				maxDY = 0
				for idx in xrange(self._periodCount):
					h = self._paintWeeklyHeaders(drawer, theDay, x + 1.0 * width / self._periodCount * idx, y, 1.0 * width / self._periodCount, 36)
					maxDY = max(maxDY, h)
					theDay.AddDS(wx.DateSpan(weeks=1))
				h = maxDY
			elif self._viewType == wxSCHEDULER_MONTHLY:
				_, h = self._paintMonthlyHeaders(drawer, day, x, y, width, 36)

			minW, minH = self._headerPanel.GetMinSize()
			if minH != h:
				self._headerPanel.SetMinSize(wx.Size(-1, h))
				self._headerPanel.GetParent().Layout()
		finally:
			if 'phoenix' not in wx.PlatformInfo:
				dc.EndDrawing()

	def _OnScroll( self, evt ):
		self._headerPanel.Refresh()
		evt.Skip()
