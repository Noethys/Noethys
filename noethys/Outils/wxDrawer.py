#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerConstants import *
from wxScheduleUtils import copyDateTime
from six.moves import range
import wx


class wxDrawer(object):
	"""
	This class handles the actual painting of headers and schedules.
	"""

	# Set this to True if you want your methods to be passed a
	# wx.GraphicsContext instead of wx.DC.
	use_gc = False

	def __init__(self, context, displayedHours):
		self.context = context
		self.displayedHours = displayedHours

	def DrawDayHeader(self, day, x, y, w, h, highlight=False):
		"""
		Draws the header for a day. Returns the header's size.
		"""
		raise NotImplementedError

	def DrawDayBackground(self, x, y, w, h, highlight=False):
		"""
		Draws the background for a day.
		"""
		raise NotImplementedError

	def DrawMonthHeader(self, day, x, y, w, h):
		"""
		Draws the header for a month. Returns the header's size.
		"""
		raise NotImplementedError

	def DrawSimpleDayHeader(self, day, x, y, w, h, highlight=False):
		"""
		Draws the header for a day, in compact form. Returns
		the header's size.
		"""
		raise NotImplementedError

	def DrawHours(self, x, y, w, h, direction, includeText=True):
		"""
		Draws hours of the day on the left of the specified
		rectangle. Returns the days column size.
		"""
		raise NotImplementedError

	def DrawSchedulesCompact(self, day, schedules, x, y, width, height, highlight):
		"""
		Draws a set of schedules in compact form (vertical
		month). Returns a list of (schedule, point, point).
		"""
		raise NotImplementedError

	def _DrawSchedule(self, schedule, x, y, w, h):
		"""
		Draws a schedule in the specified rectangle.
		"""

		if self.use_gc:
			pen = wx.Pen(schedule.color)
			self.context.SetPen(self.context.CreatePen(pen))

			brush = self.context.CreateLinearGradientBrush(x, y, x + w, y + h, schedule.color, SCHEDULER_BACKGROUND_BRUSH)
			self.context.SetBrush(brush)
			self.context.DrawRoundedRectangle(x, y, w, h, SCHEDULE_INSIDE_MARGIN)

			offsetY = SCHEDULE_INSIDE_MARGIN

			if schedule.complete is not None:
				self.context.SetPen(self.context.CreatePen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_SCROLLBAR))))
				self.context.SetBrush(self.context.CreateBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_SCROLLBAR))))
				self.context.DrawRoundedRectangle(x + 5, y + offsetY, w - 10, 10, 5)

				if schedule.complete:
					self.context.SetBrush(self.context.CreateLinearGradientBrush(x + 5, y + offsetY,
												     x + (w - 10) * schedule.complete,
												     y + offsetY + 10,
												     wx.Colour(0, 0, 255),
												     wx.Colour(0, 255, 255)))
					self.context.DrawRoundedRectangle(x + 5, y + offsetY, (w - 10) * schedule.complete, 10, 5)

				offsetY += 10 + 2 * SCHEDULE_INSIDE_MARGIN

			if schedule.icons:
				offsetX = 5
				for icon in schedule.icons:
					bitmap = wx.ArtProvider.GetBitmap( icon, wx.ART_FRAME_ICON, (16, 16) )
					self.context.DrawBitmap( bitmap, x + offsetX, y + offsetY, 16, 16 )
					offsetX += 20
					if offsetX > w - SCHEDULE_INSIDE_MARGIN:
						break
				offsetY += 20

			font = schedule.font
			self.context.SetFont(font, schedule.foreground)

			description = self._shrinkText( self.context, schedule.description, w - 2 * SCHEDULE_INSIDE_MARGIN, h )

			for line in description:
				self.context.DrawText( line, x + SCHEDULE_INSIDE_MARGIN, y + offsetY )
				offsetY += self.context.GetTextExtent( line )[1]
				if offsetY + SCHEDULE_INSIDE_MARGIN >= h:
					break
		else:
			self.context.SetBrush(wx.Brush(schedule.color))
			self.context.DrawRectangle(x, y, w, h)

			offsetY = SCHEDULE_INSIDE_MARGIN

			if schedule.complete is not None:
				self.context.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_SCROLLBAR)))
				self.context.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_SCROLLBAR)))
				self.context.DrawRectangle(x + 5, y + offsetY, w - 10, 10)
				if schedule.complete:
					self.context.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)))
					self.context.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)))
					self.context.DrawRectangle(x + 5, y + offsetY, int((w - 10) * schedule.complete), 10)

				offsetY += 10 + 2 * SCHEDULE_INSIDE_MARGIN

			if schedule.icons:
				offsetX = 5
				for bitmap in schedule.icons:
					#bitmap = wx.ArtProvider.GetBitmap( icon, wx.ART_FRAME_ICON, (16, 16) )
					self.context.DrawBitmap( bitmap, x + offsetX, y + offsetY, True )
					offsetX += 20
					if offsetX > w - SCHEDULE_INSIDE_MARGIN:
						break
				offsetY += 20

			font = schedule.font
			self.context.SetFont(font)

			self.context.SetTextForeground( schedule.foreground )
			description = self._shrinkText( self.context, schedule.description, w - 2 * SCHEDULE_INSIDE_MARGIN, h )

			for line in description:
				self.context.DrawText( line, x + SCHEDULE_INSIDE_MARGIN, y + offsetY )
				offsetY += self.context.GetTextExtent( line )[1]
				if offsetY + SCHEDULE_INSIDE_MARGIN >= h:
					break

		if schedule.clientdata != None : schedule.clientdata.bounds = (x, y, w, h)

	def DrawScheduleVertical(self, schedule, day, workingHours, x, y, width, height):
		"""Draws a schedule vertically."""

		size, position, total = self.ScheduleSize(schedule, workingHours, day, 1)

		if self.use_gc:
			font = schedule.font
			self.context.SetFont(font, schedule.color)
		else:
			font = schedule.font
			self.context.SetTextForeground( schedule.foreground )
			self.context.SetFont(font)

		y = y + position * height / total + SCHEDULE_OUTSIDE_MARGIN
		x += SCHEDULE_OUTSIDE_MARGIN
		height = height * size / total - 2 * SCHEDULE_OUTSIDE_MARGIN
		width -= 2 * SCHEDULE_OUTSIDE_MARGIN

		self._DrawSchedule(schedule, x, y, width, height)
		return (x - SCHEDULE_OUTSIDE_MARGIN, y - SCHEDULE_OUTSIDE_MARGIN,
			width + 2 * SCHEDULE_OUTSIDE_MARGIN, height + 2 * SCHEDULE_OUTSIDE_MARGIN)

	def DrawScheduleHorizontal(self, schedule, day, daysCount, workingHours, x, y, width, height):
		"""Draws a schedule horizontally."""

		size, position, total = self.ScheduleSize(schedule, workingHours, day, daysCount)

		if self.use_gc:
			font = schedule.font
			self.context.SetFont(font, schedule.color)
		else:
			font = schedule.font
			self.context.SetTextForeground( schedule.color )
			self.context.SetFont(font)

		# Height is variable

		actualHeight = SCHEDULE_INSIDE_MARGIN * 2

		if schedule.complete is not None:
			actualHeight += 10 + 2 * SCHEDULE_INSIDE_MARGIN

		if schedule.icons:
			actualHeight += 20

		x = x + position * width / total + SCHEDULE_OUTSIDE_MARGIN
		width = width * size / total - 2 * SCHEDULE_OUTSIDE_MARGIN

		lines = self._shrinkText( self.context, schedule.description, width - 2 * SCHEDULE_INSIDE_MARGIN, 65536 )
		for line in lines:
			textW, textH = self.context.GetTextExtent(line)
			if actualHeight + textH >= SCHEDULE_MAX_HEIGHT:
				break
			actualHeight += textH

		height = actualHeight

		self._DrawSchedule(schedule, x, y, width, height)

		return (x - SCHEDULE_OUTSIDE_MARGIN, y - SCHEDULE_OUTSIDE_MARGIN,
			width + 2 * SCHEDULE_OUTSIDE_MARGIN, height + 2 * SCHEDULE_OUTSIDE_MARGIN)

	def ScheduleSize(schedule, workingHours, firstDay, dayCount):
		"""
		This convenience  static method computes  the position
		and size  size of the  schedule in the  direction that
		represent time,  according to a set  of working hours.
		The workingHours  parameter is  a list of  2-tuples of
		wx.DateTime  objects   defining  intervals  which  are
		indeed worked.  startPeriod and endPeriod  delimit the
		period.
		"""

		totalSpan = 0
		scheduleSpan = 0
		position = 0

		totalTime = 0
		for startHour, endHour in workingHours:
			totalTime += copyDateTime(endHour).Subtract(startHour).GetMinutes() / 60.0

		for dayNumber in range(dayCount):
			currentDay = copyDateTime(firstDay)
			currentDay.AddDS(wx.DateSpan(days=dayNumber))

			for startHour, endHour in workingHours:
				startHourCopy = wx.DateTimeFromDMY(currentDay.GetDay(),
								   currentDay.GetMonth(),
								   currentDay.GetYear(),
								   startHour.GetHour(),
								   startHour.GetMinute(),
								   0)
				endHourCopy = wx.DateTimeFromDMY(currentDay.GetDay(),
								 currentDay.GetMonth(),
								 currentDay.GetYear(),
								 endHour.GetHour(),
								 endHour.GetMinute(),
								 0)

				totalSpan += endHourCopy.Subtract(startHourCopy).GetMinutes()

				localStart = copyDateTime(schedule.start)

				if localStart.IsLaterThan(endHourCopy):
					position += endHourCopy.Subtract(startHourCopy).GetMinutes()
					continue

				if startHourCopy.IsLaterThan(localStart):
					localStart = startHourCopy

				localEnd = copyDateTime(schedule.end)

				if startHourCopy.IsLaterThan(localEnd):
					continue

				position += localStart.Subtract(startHourCopy).GetMinutes()

				if localEnd.IsLaterThan(endHourCopy):
					localEnd = endHourCopy

				scheduleSpan += localEnd.Subtract(localStart).GetMinutes()

		return dayCount * totalTime * scheduleSpan / totalSpan, dayCount * totalTime * position / totalSpan, totalTime * dayCount

	ScheduleSize = staticmethod(ScheduleSize)

	def _shrinkText( self, dc, text, width, height ):
		"""
		Truncate text at desired width
		"""
		MORE_SIGNAL		 = '...'
		SEPARATOR		 = " "

		textlist	 = list()	# List returned by this method
		words	 = list()	# Wordlist for itermediate elaboration

		# Split text in single words and split words when yours width is over 
		# available width
		text = text.replace( "\n", " " ).split()

		for word in text:
			if dc.GetTextExtent( word )[0] > width:
				# Cycle trought every char until word width is minor or equal
				# to available width
				partial = ""
				
				for char in word:
					if dc.GetTextExtent( partial + char )[0] > width:
						words.append( partial )
						partial = char
					else:
						partial += char
			else:
				words.append( word )

		# Create list of text lines for output
		textline = list()

		for word in words:
			if dc.GetTextExtent( SEPARATOR.join( textline + [word] ) )[0] > width:
				textlist.append( SEPARATOR.join( textline ) )
				textline = [word]

				# Break if there's no vertical space available
				if ( len( textlist ) * dc.GetTextExtent( SEPARATOR )[0] ) > height:
					# Must exists almost one line of description
					if len( textlist ) > 1:
						textlist = textlist[: - 1]

					break
			else:
				textline.append( word )

		# Add remained words to text list
		if len( textline ) > 0:
			textlist.append( SEPARATOR.join( textline ) )

		return textlist


class BackgroundDrawerDCMixin(object):
	"""
	Mixin to draw day background with a DC.
	"""

	def DrawDayBackground(self, x, y, w, h, highlight=False):
		# Fond par défaut
		if highlight == False or highlight == None :
			brush = wx.TRANSPARENT_BRUSH
		# Fond pour Aujourd'hui
		elif highlight == True :
			brush = wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
		# Fond d'une aurte couleur (ferie ou vacances)
		else :
			brush = wx.Brush(highlight)
		# Application de la couleur de fond
		self.context.SetBrush(brush)

##		if highlight:
##			self.context.SetBrush( wx.Brush( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) ) )
##		else:
##			self.context.SetBrush( wx.TRANSPARENT_BRUSH )

		self.context.SetPen( FOREGROUND_PEN )

		self.context.DrawRectangle(x, y - 1, w, h + 1)


class HeaderDrawerDCMixin(object):
	"""
	A mixin to draw headers with a regular DC.
	"""

	def _DrawHeader(self, text, x, y, w, h, pointSize=8, weight=wx.FONTWEIGHT_BOLD,
			alignRight=False, highlight=False):
		font = self.context.GetFont()
		font.SetPointSize( pointSize )
		font.SetWeight( weight )
		self.context.SetFont( font )

		textW, textH = self.context.GetTextExtent( text )

		# Fond par défaut
		if highlight == False or highlight == None :
			brush = wx.TRANSPARENT_BRUSH
		# Fond pour Aujourd'hui
		elif highlight == True :
			brush = wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
		# Fond d'une aurte couleur (ferie ou vacances)
		else :
			brush = wx.Brush(highlight)
		# Application de la couleur de fond
		self.context.SetBrush(brush)

##		if highlight:
##			self.context.SetBrush( wx.Brush( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) ) )
##		else:
##			self.context.SetBrush( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )

		self.context.DrawRectangle(int(x), int(y), int(w), int(textH * 1.5))

		self.context.SetTextForeground( wx.BLACK )

		if alignRight:
			self.context.DrawText( text, x + w - textW * 1.5, y + textH * .25)
		else:
			self.context.DrawText( text, int(x + ( w - textW ) / 2), int(y + textH * .25 ))

		return w, textH * 1.5

	def DrawSchedulesCompact(self, day, schedules, x, y, width, height, highlight):
		if day is None:
			self.context.SetBrush(wx.LIGHT_GREY_BRUSH)
		else:
			self.context.SetBrush(wx.Brush(DAY_BACKGROUND_BRUSH))

		self.context.DrawRectangle(x, y, width, height)

		results = []
####JE SUIS ICI !
		if day is not None:
			# Fond par défaut
			if highlight == False or highlight == None : brush = wx.TRANSPARENT_BRUSH
			# Fond pour Aujourd'hui
			elif highlight == True : brush = wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
			# Fond d'une aurte couleur (ferie ou vacances)
			else : brush = wx.Brush(highlight)
			# Application de la couleur de fond
			self.context.SetBrush(brush)

			headerW, headerH = self.DrawSimpleDayHeader(day, x, y, width, height, highlight)
			y += headerH
			height -= headerH

			x += SCHEDULE_OUTSIDE_MARGIN
			width -= 2 * SCHEDULE_OUTSIDE_MARGIN

			y += SCHEDULE_OUTSIDE_MARGIN
			height -= 2 * SCHEDULE_OUTSIDE_MARGIN

			self.context.SetPen(FOREGROUND_PEN)

			totalHeight = 0

			for schedule in schedules:
				description = '%s %s' % (schedule.start.Format('%H:%M'), schedule.description)
				description = self._shrinkText(self.context, description, width - 2 * SCHEDULE_INSIDE_MARGIN, headerH)[0]

				textW, textH = self.context.GetTextExtent(description)
				if totalHeight + textH > height:
					break

				self.context.SetBrush(wx.Brush(schedule.color))
				self.context.DrawRectangle(x, y, width, textH * 1.2)
				results.append((schedule, wx.Point(x, y), wx.Point(x + width, y + textH * 1.2)))

				self.context.SetTextForeground(schedule.foreground)
				self.context.DrawText(description, x + SCHEDULE_INSIDE_MARGIN, y + textH * 0.1)

				y += textH * 1.2
				totalHeight += textH * 1.2

		return results


class BackgroundDrawerGCMixin(object):
	"""
	Mixin to draw day background with a GC.
	"""

	def DrawDayBackground(self, x, y, w, h, highlight=False):
		if highlight:
			hlcol = wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT )
			self.context.SetBrush( self.context.CreateLinearGradientBrush( x, y, x + w, y + h,
										       wx.Colour(128, 128, 128, 128),
										       wx.Colour(hlcol.Red(), hlcol.Green(), hlcol.Blue(), 128) ) )
		else:
			self.context.SetBrush( self.context.CreateBrush( wx.TRANSPARENT_BRUSH ) )

		self.context.SetPen( self.context.CreatePen( FOREGROUND_PEN ) )

		self.context.DrawRectangle(x, y - 1, w, h + 1)


class HeaderDrawerGCMixin(object):
	"""
	A mixin to draw headers with a GraphicsContext.
	"""

	def _DrawHeader(self, text, x, y, w, h, pointSize=10, weight=wx.FONTWEIGHT_BOLD,
			alignRight=False, highlight=False):
		font = wx.NORMAL_FONT
		fsize = font.GetPointSize()
		fweight = font.GetWeight()

		try:
			font.SetPointSize( pointSize )
			font.SetWeight( weight )
			self.context.SetFont(font, wx.BLACK)

			textW, textH = self.context.GetTextExtent( text )

			x1 = x
			y1 = y
			x2 = x + w
			y2 = y + textH * 1.5

			if highlight:
				self.context.SetBrush(self.context.CreateLinearGradientBrush(x1, y1, x2, y2, wx.Colour(128, 128, 128),
											     wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT )))
			else:
				self.context.SetBrush(self.context.CreateLinearGradientBrush(x1, y1, x2, y2, wx.Colour(128, 128, 128),
											     SCHEDULER_BACKGROUND_BRUSH))
			self.context.DrawRectangle(x1, y1, x2 - x1, y2 - y1)

			if alignRight:
				self.context.DrawText(text, x + w - 1.5 * textW, y + textH * .25)
			else:
				self.context.DrawText(text, int(x + (w - textW) / 2), int(y + textH * .25))

			return w, textH * 1.5
		finally:
			font.SetPointSize(fsize)
			font.SetWeight(fweight)

	def DrawSchedulesCompact(self, day, schedules, x, y, width, height, highlight):
		if day is None:
			brush = self.context.CreateLinearGradientBrush(x, y, x + width, y + height, wx.BLACK, SCHEDULER_BACKGROUND_BRUSH)
		else:
			brush = self.context.CreateLinearGradientBrush(x, y, x + width, y + height, wx.LIGHT_GREY, DAY_BACKGROUND_BRUSH)

		self.context.SetBrush(brush)
		self.context.DrawRectangle(x, y, width, height)

		font = wx.NORMAL_FONT
		fsize = font.GetPointSize()
		fweight = font.GetWeight()

		try:
			font.SetPointSize(10)
			font.SetWeight(wx.FONTWEIGHT_NORMAL)

			results = []

			if day is not None:
				headerW, headerH = self.DrawSimpleDayHeader(day, x, y, width, height,
									    highlight=day.IsSameDate(wx.DateTime.Now()))
				y += headerH
				height -= headerH

				x += SCHEDULE_OUTSIDE_MARGIN
				width -= 2 * SCHEDULE_OUTSIDE_MARGIN

				y += SCHEDULE_OUTSIDE_MARGIN
				height -= 2 * SCHEDULE_OUTSIDE_MARGIN

				self.context.SetPen(FOREGROUND_PEN)

				totalHeight = 0

				for schedule in schedules:
					description = '%s %s' % (schedule.start.Format('%H:%M'), schedule.description)
					description = self._shrinkText(self.context, description, width - 2 * SCHEDULE_INSIDE_MARGIN, headerH)[0]

					textW, textH = self.context.GetTextExtent(description)
					if totalHeight + textH > height:
						break

					brush = self.context.CreateLinearGradientBrush(x, y, x + width, y + height, schedule.color, DAY_BACKGROUND_BRUSH)
					self.context.SetBrush(brush)
					self.context.DrawRoundedRectangle(x, y, width, textH * 1.2, 1.0 * textH / 2)
					results.append((schedule, wx.Point(x, y), wx.Point(x + width, y + textH * 1.2)))

					self.context.SetFont(schedule.font, schedule.foreground)
					self.context.DrawText(description, x + SCHEDULE_INSIDE_MARGIN, y + textH * 0.1)

					y += textH * 1.2
					totalHeight += textH * 1.2

			return results
		finally:
			font.SetPointSize(fsize)
			font.SetWeight(fweight)

LISTE_JOURS = (u"lun.", u"mar.", u"mer.", u"jeu.", u"ven.", u"sam.", u"dim.")
LISTE_MOIS = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")

class HeaderDrawerMixin(object):
	"""
	A mixin that draws header using the _DrawHeader method.
	"""

	def DrawDayHeader(self, day, x, y, width, height, highlight=False):
		return self._DrawHeader('%s %s %s' % ( LISTE_JOURS[day.GetWeekDay()-1].capitalize(),
						       day.GetDay(), LISTE_MOIS[day.GetMonth()] ),
					x, y, width, height, highlight=highlight)

	def DrawMonthHeader(self, day, x, y, w, h):
		return self._DrawHeader('%s %s' % ( LISTE_MOIS[day.GetMonth()].capitalize(), day.GetYear() ),
					x, y, w, h)

	def DrawSimpleDayHeader(self, day, x, y, w, h, highlight=False):
		return self._DrawHeader('%d' % day.GetDay(), x, y, w, h,
					weight=wx.FONTWEIGHT_NORMAL, alignRight=True,
					highlight=highlight)


class wxBaseDrawer(BackgroundDrawerDCMixin, HeaderDrawerDCMixin, HeaderDrawerMixin, wxDrawer):
	"""
	Concrete subclass of wxDrawer; regular style.
	"""

	def DrawHours(self, x, y, w, h, direction, includeText=True):
		if direction == wxSCHEDULER_VERTICAL:
			self.context.SetBrush(wx.Brush(SCHEDULER_BACKGROUND_BRUSH))
			self.context.DrawRectangle(x, y, LEFT_COLUMN_SIZE, h)

		font = self.context.GetFont()
		font.SetPointSize( 12 )
		font.SetWeight( wx.FONTWEIGHT_NORMAL )
		self.context.SetFont( font )
		self.context.SetTextForeground( wx.BLACK )
		hourW, hourH = self.context.GetTextExtent( " 24" )

		if direction == wxSCHEDULER_VERTICAL:
			if h > len(self.displayedHours) * hourH:
				hourH = 1.0 * h / len(self.displayedHours)
		else:
			hourW = 1.0 * w / len(self.displayedHours)

		if not includeText:
			hourH = 0

		for i, hour in enumerate( self.displayedHours ):
			if hour.GetMinute() == 0:
				if direction == wxSCHEDULER_VERTICAL:
					self.context.DrawLine(int(x + LEFT_COLUMN_SIZE - hourW / 2), int(y + i * hourH), int(x + w), int(y + i * hourH))
					if includeText:
						self.context.DrawText(hour.Format(' %H'), x + LEFT_COLUMN_SIZE - hourW - 5, y + i * hourH)
				else:
					self.context.DrawLine(x + i * hourW, y + hourH * 1.25, x + i * hourW, y + h)
					if includeText:
						self.context.DrawText(hour.Format('%H'), x + i * hourW + 5, y + hourH * .25)
			else:
				if direction == wxSCHEDULER_VERTICAL:
					self.context.DrawLine(x + LEFT_COLUMN_SIZE, y + i * hourH, x + w, y + i * hourH)
				else:
					self.context.DrawLine(x + i * hourW, y + hourH * 1.4, x + i * hourW, y + h)

		if direction == wxSCHEDULER_VERTICAL:
			self.context.DrawLine(x + LEFT_COLUMN_SIZE - 1, y, x + LEFT_COLUMN_SIZE - 1, y + h)
			return LEFT_COLUMN_SIZE, max(h, DAY_SIZE_MIN.height)
		else:
			self.context.DrawLine(x, y + hourH * 1.5 - 1, x + w, y + hourH * 1.5 - 1)
			return max(w, DAY_SIZE_MIN.width), hourH * 1.5


class wxFancyDrawer(BackgroundDrawerGCMixin, HeaderDrawerGCMixin, HeaderDrawerMixin, wxDrawer):
	"""
	Concrete subclass of wxDrawer; fancy eye-candy using wx.GraphicsContext.
	"""

	use_gc = True

	def DrawHours(self, x, y, w, h, direction, includeText=True):
		if direction == wxSCHEDULER_VERTICAL:
			brush = self.context.CreateLinearGradientBrush(x, y, x + w, y + h, SCHEDULER_BACKGROUND_BRUSH, DAY_BACKGROUND_BRUSH)
			self.context.SetBrush(brush)
			self.context.DrawRectangle(x, y, LEFT_COLUMN_SIZE, h)

		font = wx.NORMAL_FONT
		fsize = font.GetPointSize()
		fweight = font.GetWeight()

		try:
			font.SetPointSize(16)
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
			self.context.SetFont(font, wx.BLACK)
			hourW, hourH = self.context.GetTextExtent( " 24" )

			self.context.SetPen(FOREGROUND_PEN)

			if direction == wxSCHEDULER_VERTICAL:
				if h > len(self.displayedHours) * hourH:
					hourH = 1.0 * h / len(self.displayedHours)
			else:
				hourW = 1.0 * w / len(self.displayedHours)

			if not includeText:
				hourH = 0

			for i, hour in enumerate( self.displayedHours ):
				if hour.GetMinute() == 0:
					if direction == wxSCHEDULER_VERTICAL:
						self.context.DrawLines([int((x + LEFT_COLUMN_SIZE - hourW / 2), int(y + i * hourH)),
									int((x + w, y + i * hourH))])
						if includeText:
							self.context.DrawText(hour.Format(' %H'), x + LEFT_COLUMN_SIZE - hourW - 10, y + i * hourH)
					else:
						self.context.DrawLines([(x + i * hourW, y + hourH * 1.25),
									(x + i * hourW, y + h + 10)])
						if includeText:
							self.context.DrawText(hour.Format('%H'), x + i * hourW + 5, y + hourH * .25)
				else:
					if direction == wxSCHEDULER_VERTICAL:
						self.context.DrawLines([(x + LEFT_COLUMN_SIZE, y + i * hourH), (x + w, y + i * hourH)])
					else:
						self.context.DrawLines([(x + i * hourW, y + hourH * 1.4), (x + i * hourW, y + h)])

			if direction == wxSCHEDULER_VERTICAL:
				self.context.DrawLines([(x + LEFT_COLUMN_SIZE - 1, y),
							(x + LEFT_COLUMN_SIZE - 1, y + h)])
				return LEFT_COLUMN_SIZE, max(h, DAY_SIZE_MIN.height)
			else:
				self.context.DrawLines([(x, y + hourH * 1.5 - 1), (x + w, y + hourH * 1.5 - 1)])
				return max(w, DAY_SIZE_MIN.width), hourH * 1.5
		finally:
			font.SetPointSize(fsize)
			font.SetWeight(fweight)
