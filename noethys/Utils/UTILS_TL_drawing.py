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
Defines the interface for drawing algorithms and provides common utilities for
drawing.
"""
import Chemins
from UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import logging

from UTILS_TL_data import div_timedeltas
from UTILS_TL_data import microseconds_to_delta
from UTILS_TL_data import delta_to_microseconds


class DrawingAlgorithm(object):
    """
    Base class for timeline drawing algorithms.

    In order to get an implementation, the `get_algorithm` factory method
    should be used.
    """

    def draw(self, dc, time_period, events, period_selection=None,
             legend=False, divider_line_slider=None):
        """
        This is the interface.

        - dc: used to do the actual drawing
        - time_period: what period of the timeline should be visible
        - events: events inside time_period that should be drawn
        - period_selection: tuple with start and end time indicating selection
        - legend: draw a legend for the categories

        When the dc is temporarily stored in a class variable such as self.dc,
        this class variable must be deleted before the draw method ends.
        """
        pass

    def event_is_period(self, time_period):
        """
        Return True if the event time_period will make the event appear
        below the center line, as a period event.
        """
        return None
     
    def snap(self, time, snap_region=10):
        """Snap time to minor strip if within snap_region pixels."""
        return time

    def snap_selection(self, period_selection):
        """
        Return a tuple where the selection has been stretched to fit to minor
        strip.

        period_selection: (start, end)
        Return: (new_start, new_end)
        """
        return period_selection

    def event_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) or None if no event there.
        """
        return None

    def event_with_rect_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) and its rect in a tuple
        (event, rect) or None if no event there.
        """
        return None

    def event_rect_at(self, event):
        """
        Return the rect for the given event or None if no event isn't found.
        """
        return None
    
    def notify_events(self, notification, data):
        """
        Send notification to all visible events
        """
        
    def get_selected_events(self):
        """Return a list with all selected events."""
        return []
            
class Metrics(object):
    """Helper class that can calculate coordinates."""

    def __init__(self, dc, time_period, divider_line_slider):
        if 'phoenix' in wx.PlatformInfo:
            self.width, self.height = dc.GetSize()
        else :
            self.width, self.height = dc.GetSizeTuple()
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.half_height = divider_line_slider.GetValue() * self.height / 100
        self.time_period = time_period

    def calc_exact_x(self, time):
        """Return the x position in pixels as a float for the given time."""
        delta1 = div_timedeltas(time - self.time_period.start_time,
                                self.time_period.delta())
        float_res = self.width * delta1
        return float_res

    def calc_x(self, time):
        """Return the x position in pixels as an integer for the given time."""
        return int(round(self.calc_exact_x(time)))

    def calc_exact_width(self, time_period):
        """Return the with in pixels as a float for the given time_period."""
        return (self.calc_exact_x(time_period.end_time) -
                self.calc_exact_x(time_period.start_time))

    def calc_width(self, time_period):
        """Return the with in pixels as an integer for the given time_period."""
        return (self.calc_x(time_period.end_time) -
                self.calc_x(time_period.start_time)) + 1

    def get_time(self, x):
        """Return the time at pixel `x`."""
        microsecs = delta_to_microseconds(self.time_period.delta())
        microsecs = microsecs * float(x) / self.width
        return self.time_period.start_time + microseconds_to_delta(microsecs)

    def get_difftime(self, x1, x2):
        """Return the time length between two x positions."""
        return self.get_time(x1) - self.get_time(x2)
    


def get_default_font(size, bold=False):
    if bold:
        weight = wx.FONTWEIGHT_BOLD
    else:
        weight = wx.FONTWEIGHT_NORMAL
    return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight)


def darken_color(color, factor=0.7):
    r, g, b = color
    new_r = int(r * factor)
    new_g = int(g * factor)
    new_b = int(b * factor)
    return (new_r, new_g, new_b)


def get_algorithm():
    """
    Factory method.

    Return the drawing algorithm that should be used by the application.
    """
    from UTILS_TL_drawing_default import DefaultDrawingAlgorithm
    return DefaultDrawingAlgorithm()




class TimelinePrintout(wx.Printout):
    """
    This class has the functionality of printing out a Timeline document.
    Responds to calls such as OnPrintPage and HasPage.
    Instances of this class are passed to wx.Printer.Print() or a
    wx.PrintPreview object to initiate printing or previewing.
    """

    def __init__(self, panel, preview=False):
        wx.Printout.__init__(self)
        self.panel   = panel
        self.preview = preview

    def OnBeginDocument(self, start, end):
        logging.debug("TimelinePrintout.OnBeginDocument")
        return super(TimelinePrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        logging.debug("TimelinePrintout.OnEndDocument")
        super(TimelinePrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        logging.debug("TimelinePrintout.OnBeginPrinting")
        super(TimelinePrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        logging.debug("TimelinePrintout.OnEndPrinting")
        super(TimelinePrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        logging.debug("TimelinePrintout.OnPreparePrinting")
        super(TimelinePrintout, self).OnPreparePrinting()

    def HasPage(self, page):
        logging.debug("TimelinePrintout.HasPage")
        if page <= 1:
            return True
        else:
            return False

    def GetPageInfo(self):
        logging.debug("TimelinePrintout.GetPageInfo")
        minPage  = 1
        maxPage  = 1
        pageFrom = 1
        pageTo   = 1
        return (minPage, maxPage, pageFrom, pageTo)

    def OnPrintPage(self, page):

        def SetScaleAndDeviceOrigin(dc):
            (panel_width, panel_height) = self.panel.GetSize()
            # Let's have at least 50 device units margin
            x_margin = 50
            y_margin = 50
            # Add the margin to the graphic size
            x_max = panel_width  + (2 * x_margin)
            y_max = panel_height + (2 * y_margin)
            # Get the size of the DC in pixels
            (dc_width, dc_heighth) = dc.GetSizeTuple()
            # Calculate a suitable scaling factor
            x_scale = float(dc_width) / x_max
            y_scale = float(dc_heighth) / y_max
            # Use x or y scaling factor, whichever fits on the DC
            scale = min(x_scale, y_scale)
            # Calculate the position on the DC for centering the graphic
            x_pos = (dc_width - (panel_width  * scale)) / 2.0
            y_pos = (dc_heighth - (panel_height * scale)) / 2.0
            dc.SetUserScale(scale, scale)
            dc.SetDeviceOrigin(int(x_pos), int(y_pos))

        logging.debug("TimelinePrintout.OnPrintPage: %d\n" % page)
        dc = self.GetDC()
        SetScaleAndDeviceOrigin(dc)
        dc.BeginDrawing()
        dc.DrawBitmap(self.panel.bgbuf, 0, 0, True)
        dc.EndDrawing()
        return True
