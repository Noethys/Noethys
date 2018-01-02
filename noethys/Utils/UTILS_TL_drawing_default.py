#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


"""
Implements the default algorithm for drawing a timeline.

The drawing interface is implemented in the `DefaultDrawingAlgorithm` class in
the `draw` method.
"""

import Chemins
from UTILS_Traduction import _

import math
import logging
import calendar
from datetime import timedelta
from datetime import datetime

import wx
from Ctrl import CTRL_Bouton_image

from Ctrl.CTRL_Timeline import sort_categories
import UTILS_TL_drawing as drawing
from UTILS_TL_drawing import DrawingAlgorithm
from UTILS_TL_drawing import Metrics
from UTILS_TL_data import TimePeriod

OUTER_PADDING = 2      # Space between event boxes (pixels)  >>>>> 5 PAR DEFAUT
INNER_PADDING = 3      # Space inside event box to text (pixels)
BASELINE_PADDING = 15  # Extra space to move events away from baseline (pixels)
PERIOD_THRESHOLD = 1  # Periods smaller than this are drawn as events (pixels)
BALLOON_RADIUS = 12
DATA_INDICATOR_SIZE = 10


LISTE_JOURS = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
LISTE_JOURS_ABREGE = (_(u"Lun"), _(u"Mar"), _(u"Mer"), _(u"Jeu"), _(u"Ven"), _(u"Sam"), _(u"Dim"))
LISTE_MOIS = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
LISTE_MOIS_ABREGE = (_(u"Jan."), _(u"Fév."), _(u"Mars"), _(u"Avr."), _(u"Mai"), _(u"Juin"), _(u"Juil."), _(u"Août"), _(u"Sept."), _(u"Oct."), _(u"Nov."), _(u"Déc."))


class Strip(object):
    """
    An interface for strips.

    The different strips are implemented in subclasses below.

    The timeline is divided in major and minor strips. The minor strip might
    for example be days, and the major strip months. Major strips are divided
    with a solid line and minor strips with dotted lines. Typically maximum
    three major strips should be shown and the rest will be minor strips.
    """

    def label(self, time, major=False):
        """
        Return the label for this strip at the given time when used as major or
        minor strip.
        """

    def start(self, time):
        """
        Return the start time for this strip and the given time.

        For example, if the time is 2008-08-31 and the strip is month, the
        start would be 2008-08-01.
        """

    def increment(self, time):
        """
        Increment the given time so that it points to the start of the next
        strip.
        """


class StripDecade(Strip):

    def label(self, time, major=False):
        if major:
            # TODO: This only works for English. Possible to localize?
            return str(self._decade_start_year(time.year)) + "s"
        return ""

    def start(self, time):
        return datetime(self._decade_start_year(time.year), 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+10)

    def _decade_start_year(self, year):
        return (int(year) / 10) * 10


class StripYear(Strip):

    def label(self, time, major=False):
        return str(time.year)

    def start(self, time):
        return datetime(time.year, 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+1)


class StripMonth(Strip):

    def label(self, time, major=False):
        if major:
            return u"%s %s" % (LISTE_MOIS[time.month-1], time.year)
        return LISTE_MOIS_ABREGE[time.month-1]
    
    def start(self, time):
        return datetime(time.year, time.month, 1)

    def increment(self, time):
        return time + timedelta(calendar.monthrange(time.year, time.month)[1])


class StripWeek(Strip):

    def label(self, time, major=False):
        if major:
            # Example: Week 23 (1-7 Jan 2009)
            first_weekday = self.start(time)
            next_first_weekday = self.increment(first_weekday)
            last_weekday = next_first_weekday - timedelta(days=1)
            range_string = self._time_range_string(first_weekday, last_weekday)
            return (_(u"Semaine %s (%s)")) % (time.isocalendar()[1], range_string)
        # This strip should never be used as minor
        return ""

    def start(self, time):
        stripped_date = datetime(time.year, time.month, time.day)
        return stripped_date - timedelta(stripped_date.weekday())

    def increment(self, time):
        return time + timedelta(7)

    def _time_range_string(self, time1, time2):
        """
        Examples:

        * 1-7 Jun 2009
        * 28 Jun-3 Jul 2009
        * 28 Jun 08-3 Jul 2009
        """
        if time1.year == time2.year:
            if time1.month == time2.month:
                return u"%s-%s %s %s" % (time1.day, time2.day, LISTE_MOIS[time1.month-1], time1.year)
            return u"%s %s-%s %s %s" % (time1.day, LISTE_MOIS_ABREGE[time1.month-1], time2.day, LISTE_MOIS_ABREGE[time2.month-1], time1.year)
        return u"%s %s %s-%s %s %s" % (time1.day, LISTE_MOIS_ABREGE[time1.month-1], time1.year, time2.day, LISTE_MOIS_ABREGE[time2.month-1], time2.year)


class StripDay(Strip):

    def label(self, time, major=False):
        if major:
            return u"%s %s %s" % (time.day, LISTE_MOIS[time.month-1], time.year)
        return str(time.day)

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)


class StripWeekday(Strip):

    def label(self, time, major=False):
        if major:
            return u"%s %s %s %s" % (LISTE_JOURS[time.weekday()-1], time.day, LISTE_MOIS[time.month-1], time.year)
        return LISTE_JOURS_ABREGE[time.weekday()-1]

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)


class StripHour(Strip):

    def label(self, time, major=False):
        if major:
            return u"%s %s %s %s" % (time.day, LISTE_MOIS[time.month-1], time.year, time.hour)
        return str(time.hour)

    def start(self, time):
        return datetime(time.year, time.month, time.day, time.hour)

    def increment(self, time):
        return time + timedelta(hours=1)


class DefaultDrawingAlgorithm(DrawingAlgorithm):

    def __init__(self):
        # Fonts and pens we use when drawing
        self.header_font = drawing.get_default_font(12, True)
        self.small_text_font = drawing.get_default_font(8)
        self.red_solid_pen = wx.Pen(wx.Colour(255,0, 0), 1, wx.SOLID)
        self.black_solid_pen = wx.Pen(wx.Colour(0, 0, 0), 1, wx.SOLID)
        self.darkred_solid_pen = wx.Pen(wx.Colour(200, 0, 0), 1, wx.SOLID)
        self.black_dashed_pen = wx.Pen(wx.Colour(200, 200, 200), 1, wx.USER_DASH)
        self.black_dashed_pen.SetDashes([2, 2])
        self.black_dashed_pen.SetCap(wx.CAP_BUTT)
        self.grey_solid_pen = wx.Pen(wx.Colour(200, 200, 200), 1, wx.SOLID)
        self.white_solid_brush = wx.Brush(wx.Colour(255, 255, 255), wx.SOLID)
        self.black_solid_brush = wx.Brush(wx.Colour(0, 0, 0), wx.SOLID)
        self.lightgrey_solid_brush = wx.Brush(wx.Colour(230, 230, 230), wx.SOLID)
        self.DATA_ICON_WIDTH = 5

    def event_is_period(self, time_period):
        ew = self.metrics.calc_width(time_period)
        return ew > PERIOD_THRESHOLD
    
    def draw(self, dc, time_period, events, period_selection=None,
             legend=False,  divider_line_slider=None):
        """
        Implement the drawing interface.

        The drawing is done in a number of steps: First positions of all events
        and strips are calculated and then they are drawn. Positions can also
        be used later to answer questions like what event is at position (x, y).
        """
        # Store data so we can use it in other functions
        self.dc = dc
        self.time_period = time_period
        self.metrics = Metrics(dc, time_period, divider_line_slider)
        # Data
        self.event_data = []       # List of tuples (event, rect)
        self.major_strip_data = [] # List of time_period
        self.minor_strip_data = [] # List of time_period
        # Calculate stuff later used for drawing
        self._calc_rects(events)
        self._calc_strips()
        # Perform the actual drawing
        if period_selection:
            self._draw_period_selection(period_selection)
        self._draw_bg()
        self._draw_events()
        if legend:
            self._draw_legend(self._extract_categories(events))
        self._draw_ballons()
        # Make sure to delete this one
        del self.dc

    def snap(self, time, snap_region=10):
        major_strip, minor_strip = self._choose_strip()
        time_x = self.metrics.calc_exact_x(time)
        left_strip_time = minor_strip.start(time)
        right_strip_time = minor_strip.increment(left_strip_time)
        left_diff = abs(time_x - self.metrics.calc_exact_x(left_strip_time))
        right_diff = abs(time_x - self.metrics.calc_exact_x(right_strip_time))
        if left_diff < snap_region:
            return left_strip_time
        elif right_diff < snap_region:
            return right_strip_time
        else:
            return time

    def snap_selection(self, period_selection):
        start, end = period_selection
        return (self.snap(start), self.snap(end))

    def event_at(self, x, y):
        for (event, rect) in self.event_data:
            if rect.Contains(wx.Point(x, y)):
                return event
        return None

    def event_with_rect_at(self, x, y):
        for (event, rect) in self.event_data:
            if rect.Contains(wx.Point(x, y)):
                return (event, rect)
        return None

    def event_rect(self, evt):
        for (event, rect) in self.event_data:
            if evt == event:
                return rect
        return None

    def get_selected_events(self):
        selected_events = []
        for (event, rect) in self.event_data:
            if event.selected:
                selected_events.append(event)
        return selected_events
 
    def _calc_rects(self, events):
        """
        Calculate rectangles for all events.

        The rectangles define the areas in which the events can draw
        themselves.

        During the calculations, the outer padding is part of the rectangles to
        make the calculations easier. Outer padding is removed in the end.
        """
        self.dc.SetFont(self.small_text_font)
        for event in events:
            tw, th = self.dc.GetTextExtent(event.text)
            ew = self.metrics.calc_width(event.time_period)
            if ew > PERIOD_THRESHOLD:
                # Treat as period (periods are placed below the baseline, with
                # indicates length of period)
                rw = ew + 2 * OUTER_PADDING
                rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
                rx = (self.metrics.calc_x(event.time_period.start_time) -
                      OUTER_PADDING)
                ry = self.metrics.half_height + BASELINE_PADDING
                movedir = 1
            else:
                # Treat as event (events are placed above the baseline, with
                # indicates length of text)
                rw = tw + 2 * INNER_PADDING + 2 * OUTER_PADDING
                rh = th + 2 * INNER_PADDING + 2 * OUTER_PADDING
                if event.has_data():
                    rw += DATA_INDICATOR_SIZE / 3
                rx = self.metrics.calc_x(event.mean_time()) - rw / 2
                ry = self.metrics.half_height - rh - BASELINE_PADDING
                movedir = -1
            rect = wx.Rect(rx, ry, rw, rh)
            self._prevent_overlap(rect, movedir)
            self.event_data.append((event, rect))
        for (event, rect) in self.event_data:
            # Remove outer padding
            rect.Deflate(OUTER_PADDING, OUTER_PADDING)
#            # Make sure rectangle are not far outside the screen
#            if rect.X < -1:
#                move = -rect.X - 1
#                rect.X += move
#                rect.Width -= move
#            if rect.Width > self.metrics.width:
#                rect.Width = self.metrics.width + 2

    def _prevent_overlap(self, rect, movedir):
        """
        Prevent rect from overlapping with any rectangle by moving it.
        """
        while True:
            h = self._intersection_height(rect)
            if h > 0:
                rect.Y += movedir * h
            else:
                break

    def _intersection_height(self, rect):
        """
        Calculate height of first intersection with rectangle.
        """
        for (event, r) in self.event_data:
            if rect.Intersects(r):
                # Calculate height of intersection only if there is any
                r_copy = wx.Rect(*r) # Because `Intersect` modifies rect
                intersection = r_copy.Intersect(rect)
                return intersection.Height
        return 0

    def _calc_strips(self):
        """Fill the two arrays `minor_strip_data` and `major_strip_data`."""
        def fill(list, strip):
            """Fill the given list with the given strip."""
            current_start = strip.start(self.time_period.start_time)
            while current_start < self.time_period.end_time:
                next_start = strip.increment(current_start)
                list.append(TimePeriod(current_start, next_start))
                current_start = next_start
        major_strip, minor_strip = self._choose_strip()
        fill(self.major_strip_data, major_strip)
        fill(self.minor_strip_data, minor_strip)

    def _choose_strip(self):
        """
        Return a tuple (major_strip, minor_strip) for current time period and
        window size.
        """
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        day_period = TimePeriod(today, tomorrow)
        one_day_width = self.metrics.calc_exact_width(day_period)
        if one_day_width > 600:
            return (StripDay(), StripHour())
        elif one_day_width > 45:
            return (StripWeek(), StripWeekday())
        elif one_day_width > 25:
            return (StripMonth(), StripDay())
        elif one_day_width > 1.5:
            return (StripYear(), StripMonth())
        elif one_day_width > 0.12:
            return (StripDecade(), StripYear())
        else:
            return (StripDecade(), StripDecade())

    def _draw_period_selection(self, period_selection):
        start, end = period_selection
        start_x = self.metrics.calc_x(start)
        end_x = self.metrics.calc_x(end)
        self.dc.SetBrush(self.lightgrey_solid_brush)
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawRectangle(start_x, 0,
                              end_x - start_x + 1, self.metrics.height)

    def _draw_bg(self):
        """
        Draw major and minor strips, lines to all event boxes and baseline.

        Both major and minor strips have divider lines and labels.
        """
        major_strip, minor_strip = self._choose_strip()
        # Minor strips
        self.dc.SetFont(self.small_text_font)
        self.dc.SetPen(self.black_dashed_pen)
        for tp in self.minor_strip_data:
            # Divider line
            x = self.metrics.calc_x(tp.end_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)
            # Label
            label = minor_strip.label(tp.start_time)
            (tw, th) = self.dc.GetTextExtent(label)
            middle = self.metrics.calc_x(tp.mean_time())
            middley = self.metrics.half_height
            self.dc.DrawText(label, middle - tw / 2, middley - th)
        # Major strips
        self.dc.SetFont(self.header_font)
        self.dc.SetPen(self.grey_solid_pen)
        for tp in self.major_strip_data:
            # Divider line
            x = self.metrics.calc_x(tp.end_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)
            # Label
            label = major_strip.label(tp.start_time, True)
            (tw, th) = self.dc.GetTextExtent(label)
            x = self.metrics.calc_x(tp.mean_time()) - tw / 2
            # If the label is not visible when it is positioned in the middle
            # of the period, we move it so that as much of it as possible is
            # visible without crossing strip borders.
            if x - INNER_PADDING < 0:
                x = INNER_PADDING
                right = self.metrics.calc_x(tp.end_time)
                if x + tw + INNER_PADDING > right:
                    x = right - tw - INNER_PADDING
            elif x + tw + INNER_PADDING > self.metrics.width:
                x = self.metrics.width - tw - INNER_PADDING
                left = self.metrics.calc_x(tp.start_time)
                if x < left:
                    x = left + INNER_PADDING
            self.dc.DrawText(label, x, INNER_PADDING)
        # Main divider line
        self.dc.SetPen(self.black_solid_pen)
        self.dc.DrawLine(0, self.metrics.half_height, self.metrics.width,
                         self.metrics.half_height)
        # Lines to all events
        self.dc.SetBrush(self.black_solid_brush)
        for (event, rect) in self.event_data:
            if rect.Y < self.metrics.half_height:
                x = self.metrics.calc_x(event.mean_time())
                y = rect.Y + rect.Height / 2
                self.dc.DrawLine(x, y, x, self.metrics.half_height)
                self.dc.DrawCircle(x, self.metrics.half_height, 2)
        # Now line
        now_time = datetime.now()
        if self.time_period.inside(now_time):
            self.dc.SetPen(self.darkred_solid_pen)
            x = self.metrics.calc_x(now_time)
            self.dc.DrawLine(x, 0, x, self.metrics.height)

    def _extract_categories(self, events):
        categories = []
        for event in events:
            cat = event.category
            if cat and not cat in categories:
                categories.append(cat)
        return sort_categories(categories)

    def _draw_legend(self, categories):
        """
        Draw legend for the given categories.

        Box in lower left corner:

          +----------+
          | Name   O |
          | Name   O |
          +----------+
        """
        num_categories = len(categories)
        if num_categories == 0:
            return
        def calc_sizes(dc):
            """Return (width, height, item_height)."""
            width = 0
            height = INNER_PADDING
            item_heights = 0
            for cat in categories:
                tw, th = self.dc.GetTextExtent(cat.name)
                height = height + th + INNER_PADDING
                item_heights += th
                if tw > width:
                    width = tw
            item_height = item_heights / num_categories
            return (width + 4 * INNER_PADDING + item_height, height,
                    item_height)
        self.dc.SetFont(self.small_text_font)
        self.dc.SetTextForeground((0, 0, 0))
        width, height, item_height = calc_sizes(self.dc)
        # Draw big box
        self.dc.SetBrush(self.white_solid_brush)
        self.dc.SetPen(self.black_solid_pen)
        box_rect = (OUTER_PADDING,
                    self.metrics.height - height - OUTER_PADDING,
                    width, height)
        if 'phoenix' in wx.PlatformInfo:
            self.dc.DrawRectangle(box_rect)
        else :
            self.dc.DrawRectangleRect(box_rect)
        # Draw text and color boxes
        cur_y = self.metrics.height - height - OUTER_PADDING + INNER_PADDING
        for cat in categories:
            base_color = cat.color
            border_color = drawing.darken_color(base_color)
            self.dc.SetBrush(wx.Brush(base_color, wx.SOLID))
            self.dc.SetPen(wx.Pen(border_color, 1, wx.SOLID))
            color_box_rect = (OUTER_PADDING + width - item_height -
                              INNER_PADDING,
                              cur_y, item_height, item_height)
            if 'phoenix' in wx.PlatformInfo:
                self.dc.DrawRectangle(color_box_rect)
            else :
                self.dc.DrawRectangleRect(color_box_rect)
            self.dc.DrawText(cat.name, OUTER_PADDING + INNER_PADDING, cur_y)
            cur_y = cur_y + item_height + INNER_PADDING

    def _draw_events(self):
        """Draw all event boxes and the text inside them."""
        self.dc.SetFont(self.small_text_font)
        self.dc.SetTextForeground((0, 0, 0))
        for (event, rect) in self.event_data:
            # Ensure that we can't draw outside rectangle
            self.dc.DestroyClippingRegion()
            if 'phoenix' in wx.PlatformInfo:
                self.dc.SetClippingRegion(rect)
            else :
                self.dc.SetClippingRect(rect)
            # Draw the box
            self.dc.SetBrush(self._get_box_brush(event))
            self.dc.SetPen(self._get_box_pen(event))
            if 'phoenix' in wx.PlatformInfo:
                self.dc.DrawRectangle(rect)
            else :
                self.dc.DrawRectangleRect(rect)
            # Ensure that we can't draw content outside inner rectangle
            self.dc.DestroyClippingRegion()
            rect_copy = wx.Rect(*rect)
            rect_copy.Deflate(INNER_PADDING, INNER_PADDING)

            if 'phoenix' in wx.PlatformInfo:
                self.dc.SetClippingRegion(rect_copy)
            else :
                self.dc.SetClippingRect(rect_copy)

            if rect_copy.Width > 0:
                # Draw the text (if there is room for it)
                text_x = rect.X + INNER_PADDING
                text_y = rect.Y + INNER_PADDING
                if text_x < INNER_PADDING:
                    text_x = INNER_PADDING
                self.dc.DrawText(event.text, text_x, text_y)
            # Draw data contents indicator
            self.dc.DestroyClippingRegion()
            if 'phoenix' in wx.PlatformInfo:
                self.dc.SetClippingRegion(rect)
            else :
                self.dc.SetClippingRect(rect)
            if event.has_data():
                self._draw_contents_indicator(event, rect)
            # Draw selection and handles
            if event.selected:
                small_rect = wx.Rect(*rect)
                small_rect.Deflate(1, 1)
                border_color = self._get_border_color(event)
                border_color = drawing.darken_color(border_color)
                pen = wx.Pen(border_color, 1, wx.SOLID)
                self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
                self.dc.SetPen(pen)

                if 'phoenix' in wx.PlatformInfo:
                    self.dc.DrawRectangle(small_rect)
                else:
                    self.dc.DrawRectangleRect(small_rect)

                self._draw_handles(rect)
        # Reset this when we are done
        self.dc.DestroyClippingRegion()

    def _draw_handles(self, rect):
        SIZE = 4
        big_rect = wx.Rect(rect.X - SIZE, rect.Y - SIZE, rect.Width + 2 * SIZE, rect.Height + 2 * SIZE)
        self.dc.DestroyClippingRegion()
        if 'phoenix' in wx.PlatformInfo:
            self.dc.SetClippingRegion(big_rect)
        else:
            self.dc.SetClippingRect(big_rect)
        y = rect.Y + rect.Height/2 - SIZE/2
        x = rect.X - SIZE / 2
        west_rect   = wx.Rect(x + 1             , y, SIZE, SIZE)
        center_rect = wx.Rect(x + rect.Width / 2, y, SIZE, SIZE)
        east_rect   = wx.Rect(x + rect.Width - 1, y, SIZE, SIZE)
        self.dc.SetBrush(wx.Brush("BLACK", wx.SOLID))
        self.dc.SetPen(wx.Pen("BLACK", 1, wx.SOLID))
        if 'phoenix' in wx.PlatformInfo:
            self.dc.DrawRectangle(east_rect)
            self.dc.DrawRectangle(west_rect)
            self.dc.DrawRectangle(center_rect)
        else :
            self.dc.DrawRectangleRect(east_rect)
            self.dc.DrawRectangleRect(west_rect)
            self.dc.DrawRectangleRect(center_rect)

    def _draw_contents_indicator(self, event, rect):
        """
        The data contents indicator is a small icon added to the end of
        the event rectangle.
        The icon is a rectangle with LIGHT_GRAY background and a RED
        triangle.
        """
        corner_x = rect.X + rect.Width
        if corner_x > self.metrics.width:
            corner_x = self.metrics.width
        points = (
            wx.Point(corner_x - DATA_INDICATOR_SIZE, rect.Y),
            wx.Point(corner_x, rect.Y),
            wx.Point(corner_x, rect.Y + DATA_INDICATOR_SIZE),
        )
        self.dc.SetBrush(self._get_box_indicator_brush(event))
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawPolygon(points)

    def _get_base_color(self, event):
        if event.category:
            base_color = event.category.color
        else:
            base_color = (200, 200, 200)
        return base_color

    def _get_border_color(self, event):
        base_color = self._get_base_color(event)
        border_color = drawing.darken_color(base_color)
        return border_color

    def _get_box_pen(self, event):
        border_color = self._get_border_color(event)
        pen = wx.Pen(border_color, 1, wx.SOLID)
        return pen

    def _get_box_brush(self, event):
        base_color = self._get_base_color(event)
        brush = wx.Brush(base_color, wx.SOLID)
        return brush

    def _get_box_indicator_brush(self, event):
        base_color = self._get_base_color(event)
        darker_color = drawing.darken_color(base_color, 0.6)
        brush = wx.Brush(darker_color, wx.SOLID)
        return brush

    def _get_selected_box_brush(self, event):
        border_color = self._get_border_color(event)
        brush = wx.Brush(border_color, wx.BDIAGONAL_HATCH)
        return brush

    def _draw_ballons(self):
        """Draw ballons on selected events that has 'description' data."""
        for (event, rect) in self.event_data:
            if (event.get_data("description") != None or
                event.get_data("icon") != None):
                if event.draw_ballon:
                    self._draw_ballon(event, rect)

    def _draw_ballon(self, event, event_rect):
        """Draw one ballon on a selected event that has 'description' data."""
        # Constants
        MAX_TEXT_WIDTH = 200
        MIN_WIDTH = 100
        inner_rect_w = 0
        inner_rect_h = 0
        # Icon
        (iw, ih) = (0, 0)
        icon = event.get_data("icon")
        if icon != None:
            (iw, ih) = icon.Size
            inner_rect_w = iw
            inner_rect_h = ih
        # Text
        self.dc.SetFont(drawing.get_default_font(8))
        font_h = self.dc.GetCharHeight()
        (tw, th) = (0, 0)
        description = event.get_data("description")
        lines = None
        if description != None:
            lines = break_text(description, self.dc, MAX_TEXT_WIDTH)
            th = len(lines) * self.dc.GetCharHeight()
            for line in lines:
                (lw, lh) = self.dc.GetTextExtent(line)
                tw = max(lw, tw)
            if icon != None:
                inner_rect_w += BALLOON_RADIUS
            inner_rect_w += min(tw, MAX_TEXT_WIDTH)
            inner_rect_h = max(inner_rect_h, th)
        inner_rect_w = max(MIN_WIDTH, inner_rect_w)
        x, y = self._draw_balloon_bg(self.dc, (inner_rect_w, inner_rect_h),
                              (event_rect.X + event_rect.Width / 2,
                               event_rect.Y),
                              True)
        if icon != None:
            self.dc.DrawBitmap(icon, x, y, False)
            x += iw + BALLOON_RADIUS
        if lines != None:
            ty = y
            for line in lines:
                self.dc.DrawText(line, x, ty)
                ty += font_h
            x += tw

    def _draw_balloon_bg(self, dc, inner_size, tip_pos, above):
        """
        Draw the balloon background leaving inner_size for content.

        tip_pos determines where the tip of the ballon should be.

        above determines if the balloon should be above the tip (True) or below
        (False). This is not currently implemented.

                    W
           |----------------|
             ______________           _
            /              \          |             R = Corner Radius
           |                |         |            AA = Left Arrow-leg angle
           |  W_ARROW       |         |  H     MARGIN = Text margin
           |     |--|       |         |             * = Starting point
            \____    ______/          _
                /  /                  |
               /_/                    |  H_ARROW
              *                       -
           |----|
           ARROW_OFFSET
    
        Calculation of points starts at the tip of the arrow and continues
        clockwise around the ballon.

        Return (x, y) which is at top of inner region.
        """
        # Prepare path object
        gc = wx.GraphicsContext.Create(self.dc)
        path = gc.CreatePath()
        # Calculate path
        R = BALLOON_RADIUS
        W = 1 * R + inner_size[0]
        H = 1 * R + inner_size[1]
        H_ARROW = 14
        W_ARROW = 15
        W_ARROW_OFFSET = R + 25
        AA = 20
        # Starting point at the tip of the arrow
        (tipx, tipy) = tip_pos
        p0 = wx.Point(tipx, tipy)
        path.MoveToPoint(p0.x, p0.y)
        # Next point is the left base of the arrow
        p1 = wx.Point(p0.x + H_ARROW * math.tan(math.radians(AA)),
                      p0.y - H_ARROW)
        path.AddLineToPoint(p1.x, p1.y)
        # Start of lower left rounded corner
        p2 = wx.Point(p1.x - W_ARROW_OFFSET + R, p1.y)
        bottom_y = p2.y
        path.AddLineToPoint(p2.x, p2.y)
        # The lower left rounded corner. p3 is the center of the arc
        p3 = wx.Point(p2.x, p2.y - R)
        path.AddArc(p3.x, p3.y, R, math.radians(90), math.radians(180))
        # The left side
        p4 = wx.Point(p3.x - R, p3.y - H + R)
        left_x = p4.x
        path.AddLineToPoint(p4.x, p4.y)
        # The upper left rounded corner. p5 is the center of the arc
        p5 = wx.Point(p4.x + R, p4.y)
        path.AddArc(p5.x, p5.y, R, math.radians(180), math.radians(-90))
        # The upper side
        p6 = wx.Point(p5.x + W - R, p5.y - R)
        top_y = p6.y
        path.AddLineToPoint(p6.x, p6.y)
        # The upper right rounded corner. p7 is the center of the arc
        p7 = wx.Point(p6.x, p6.y + R)
        path.AddArc(p7.x, p7.y, R, math.radians(-90), math.radians(0))
        # The right side
        p8 = wx.Point(p7.x + R , p7.y + H - R)
        right_x = p8.x
        path.AddLineToPoint(p8.x, p8.y)
        # The lower right rounded corner. p9 is the center of the arc
        p9 = wx.Point(p8.x - R, p8.y)
        path.AddArc(p9.x, p9.y, R, math.radians(0), math.radians(90))
        # The lower side
        p10 = wx.Point(p9.x - W + W_ARROW +  W_ARROW_OFFSET, p9.y + R)
        path.AddLineToPoint(p10.x, p10.y)
        path.CloseSubpath()
        # Draw sharp lines on GTK which uses Cairo
        # See: http://www.cairographics.org/FAQ/#sharp_lines
        gc.Translate(0.5, 0.5)
        # Draw the ballon
        BORDER_COLOR = wx.Colour(127, 127, 127)
        BG_COLOR = wx.Colour(255, 255, 231)
        PEN = wx.Pen(BORDER_COLOR, 1, wx.SOLID)
        BRUSH = wx.Brush(BG_COLOR, wx.SOLID)
        gc.SetPen(PEN)
        gc.SetBrush(BRUSH)
        gc.DrawPath(path)
        # Return
        return (left_x + BALLOON_RADIUS, top_y + BALLOON_RADIUS)

    def notify_events(self, notification, data):
        """
        Send notification to all visible events
        """
        for (event, rect) in self.event_data:
            event.notify(notification, data)


def break_text(text, dc, max_width_in_px):
    """ Break the text into lines so that they fits within the given width."""
    sentences = text.split("\n")
    lines = []
    for sentence in sentences:
        w, h = dc.GetTextExtent(sentence)
        if w <= max_width_in_px:
            lines.append(sentence)
        # The sentence is too long. Break it.
        else:
            break_sentence(dc, lines, sentence, max_width_in_px);
    return lines


def break_sentence(dc, lines, sentence, max_width_in_px):
    """Break a sentence into lines."""
    line = []
    max_word_len_in_ch = get_max_word_length(dc, max_width_in_px)
    words = break_line(dc, sentence, max_word_len_in_ch)
    for word in words:
        w, h = dc.GetTextExtent("".join(line) + word + " ")
        # Max line length reached. Start a new line
        if w > max_width_in_px:
            lines.append("".join(line))
            line = []
        line.append(word + " ")
        # Word edning with '-' is a broken word. Start a new line
        if word.endswith('-'):
            lines.append("".join(line))
            line = []
    if len(line) > 0:
        lines.append("".join(line))


def break_line(dc, sentence, max_word_len_in_ch):
    """Break a sentence into words."""
    words = sentence.split(" ")
    new_words = []
    for word in words:
        broken_words = break_word(dc, word, max_word_len_in_ch)
        for broken_word in broken_words:
            new_words.append(broken_word)
    return new_words


def break_word(dc, word, max_word_len_in_ch):
    """
    Break words if they are too long.

    If a single word is too long to fit we have to break it.
    If not we just return the word given.
    """
    words = []
    while len(word) > max_word_len_in_ch:
        word1 = word[0:max_word_len_in_ch] + "-"
        word =  word[max_word_len_in_ch:]
        words.append(word1)
    words.append(word)
    return words


def get_max_word_length(dc, max_width_in_px):
    TEMPLATE_CHAR = 'K'
    word = [TEMPLATE_CHAR]
    w, h = dc.GetTextExtent("".join(word))
    while w < max_width_in_px:
        word.append(TEMPLATE_CHAR)
        w, h = dc.GetTextExtent("".join(word))
    return len(word) - 1
