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
Custom data types.
"""


from datetime import timedelta
from datetime import datetime as dt
from datetime import time
import calendar
import base64
import StringIO
import os.path
import locale

import wx


# To save computation power (used by `delta_to_microseconds`)
US_PER_SEC = 1000000
US_PER_DAY = 24 * 60 * 60 * US_PER_SEC

# Notification messages
MSG_BALLON_VISIBILITY_CHANGED   = 1


class Observable(object):
    """
    Base class for objects that would like to be observable.

    The function registered should take one argument which represent the state
    change. It can be any object.
    """

    def __init__(self):
        self.observers = []

    def register(self, fn):
        self.observers.append(fn)

    def unregister(self, fn):
        if fn in self.observers:
            self.observers.remove(fn)

    def _notify(self, state_change):
        for fn in self.observers:
            fn(state_change)


class TimelineIOError(Exception):
    """
    Raised from a Timeline if a read/write error occurs.

    The constructor and any of the public methods can raise this exception.

    Also raised by the get_timeline method if loading of a timeline failed.
    """
    pass


class Timeline(Observable):
    """
    Base class that represents the interface for a timeline.

    A possible implementation could be for a timeline stored in a flat file or
    in a SQL database.

    In order to get an implementation, the `get_timeline` factory method should
    be used.

    All methods that modify the timeline should automatically save it.

    A timeline is observable so that GUI components can update themselves when
    it changes. The two types of state changes are given as constants below.
    """

    # A category was added, edited, or deleted
    STATE_CHANGE_CATEGORY = 1
    # Something happened that changed the state of the timeline
    STATE_CHANGE_ANY = 2

    def __init__(self):
        Observable.__init__(self)

    def get_events(self, time_period):
        """Return a list of all events visible within the time period whose
        category is visible."""
        raise NotImplementedError()

    def add_event(self, event):
        """Add `event` to the timeline."""
        raise NotImplementedError()

    def event_edited(self, event):
        """Notify that `event` has been modified so that it can be saved."""
        raise NotImplementedError()

    def select_event(self, event, selected=True):
        """
        Notify that event should be marked as selected.

        Must ensure that subsequent calls to get_events maintains this selected
        state.
        """
        raise NotImplementedError()

    def delete_selected_events(self):
        """Delete all events that have been marked as selected."""
        raise NotImplementedError()

    def reset_selected_events(self):
        """Mark all selected events as unselected."""
        raise NotImplementedError()

    def get_categories(self):
        """Return a list of all available categories."""
        raise NotImplementedError()

    def add_category(self, category):
        """Add `category` to the timeline."""
        raise NotImplementedError()

    def category_edited(self, category):
        """Notify that `category` has been modified so that it can be saved."""
        raise NotImplementedError()

    def delete_category(self, category):
        """Delete `category` and remove it from all events."""
        raise NotImplementedError()

    def get_preferred_period(self):
        """Return the preferred period to display of this timeline."""
        raise NotImplementedError()

    def set_preferred_period(self, period):
        """Set the preferred period to display of this timeline."""
        raise NotImplementedError()


class EventDataPlugin(object):
    """
    Base class for plugins that extend events by adding additional data fields.

    Access an event's additional data like this:

      data_object = event.get_data("plugin_id")
      event.set_data("plugin_id", data_object)

    Available plugins must be configured in get_event_data_plugins.
    """

    def get_id(self):
        """
        Return a string [a-z]+.

        Must be unique among all plugins configured in get_event_data_plugins.
        """
        raise NotImplementedError()

    def get_name(self):
        """
        Return an internationalized string.

        Displayed on the tabs of the notebook in the event editor dialog.
        """
        raise NotImplementedError()

    def encode(self, data):
        """
        Encode data to string.

        Used to save data to file.

        For convenience, string data is assumed.
        """
        return data

    def decode(self, string):
        """
        Decode string to data.

        Used to load data from file.

        For convenience, string data is assumed.
        """
        return string

    def create_editor(self, parent):
        """
        Create and return a wx control with the given parent.

        Used in the event editor dialog to edit the data objects that this
        plugin handles.
        """
        raise NotImplementedError()

    def get_editor_data(self, editor):
        """
        Return data object given the editor created in create_editor or None if
        no data has been entered in the editor control.
        """
        raise NotImplementedError()

    def set_editor_data(self, editor, data):
        """
        Configure the editor created in create_editor with the given data
        object.
        """
        raise NotImplementedError()

    def clear_editor_data(self, editor):
        """
        Configure the editor created in create_editor so that get_editor_data
        will return None.
        """
        raise NotImplementedError()


class DescriptionEventDataPlugin(EventDataPlugin):

    def get_id(self):
        return "description"

    def get_name(self):
        return "Description"

    def create_editor(self, parent):
        ctrl = wx.TextCtrl(parent, style=wx.TE_MULTILINE)
        return ctrl

    def get_editor_data(self, editor):
        description = editor.GetValue()
        if description.strip() != "":
            return description
        return None

    def set_editor_data(self, editor, description):
        editor.SetValue(description)

    def clear_editor_data(self, editor):
        editor.SetValue("")


class IconEventDataPlugin(EventDataPlugin):

    class IconEditor(wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent)
            self.MAX_SIZE = (128, 128)
            # Controls
            self.img_icon = wx.StaticBitmap(self, size=self.MAX_SIZE)
            description = wx.StaticText(self, label="Images will be scaled to fit inside a %ix%i box." % self.MAX_SIZE)
            btn_select = wx.Button(self, wx.ID_OPEN)
            btn_clear = wx.Button(self, wx.ID_CLEAR)
            self.Bind(wx.EVT_BUTTON, self._btn_select_on_click, btn_select)
            self.Bind(wx.EVT_BUTTON, self._btn_clear_on_click, btn_clear)
            # Layout
            sizer = wx.GridBagSizer(5, 5)
            sizer.Add(description, wx.GBPosition(0, 0), wx.GBSpan(1, 2))
            sizer.Add(btn_select, wx.GBPosition(1, 0), wx.GBSpan(1, 1))
            sizer.Add(btn_clear, wx.GBPosition(1, 1), wx.GBSpan(1, 1))
            sizer.Add(self.img_icon, wx.GBPosition(0, 2), wx.GBSpan(2, 1))
            self.SetSizerAndFit(sizer)
            # Data
            self.bmp = None
        def set_icon(self, bmp):
            self.bmp = bmp
            if self.bmp == None:
                self.img_icon.SetBitmap(wx.EmptyBitmap(1, 1))
            else:
                self.img_icon.SetBitmap(bmp)
            self.GetSizer().Layout()
        def get_icon(self):
            return self.bmp
        def _btn_select_on_click(self, evt):
            dialog = wx.FileDialog(self, message="Select Icon",
                                   wildcard="*", style=wx.FD_OPEN)
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                if os.path.exists(path):
                    image = wx.EmptyImage(0, 0)
                    success = image.LoadFile(path)
                    # LoadFile will show error popup if not successful
                    if success:
                        # Resize image if too large
                        (w, h) = image.GetSize()
                        (W, H) = self.MAX_SIZE
                        if w > W:
                            factor = float(W) / float(w)
                            w = w * factor
                            h = h * factor
                        if h > H:
                            factor = float(H) / float(h)
                            w = w * factor
                            h = h * factor
                        image = image.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
                        self.set_icon(image.ConvertToBitmap())
            dialog.Destroy()
        def _btn_clear_on_click(self, evt):
            self.set_icon(None)

    def get_id(self):
        return "icon"

    def get_name(self):
        return "Icon"

    def encode(self, data):
        """Data is wx.Bitmap."""
        output = StringIO.StringIO()
        image = wx.ImageFromBitmap(data)
        image.SaveStream(output, wx.BITMAP_TYPE_PNG)
        return base64.b64encode(output.getvalue())

    def decode(self, string):
        """Return is wx.Bitmap."""
        input = StringIO.StringIO(base64.b64decode(string))
        image = wx.ImageFromStream(input, wx.BITMAP_TYPE_PNG)
        return image.ConvertToBitmap()

    def create_editor(self, parent):
        ctrl = IconEventDataPlugin.IconEditor(parent)
        return ctrl

    def get_editor_data(self, editor):
        return editor.get_icon()

    def set_editor_data(self, editor, bmp):
        editor.set_icon(bmp)

    def clear_editor_data(self, editor):
        editor.set_icon(None)


class Event(object):
    """Represents an event on a timeline."""

    def __init__(self, start_time, end_time, text, category=None):
        """
        Create an event.

        `start_time` and `end_time` should be of the type datetime.
        """
        self.selected = False
        self.draw_ballon = False
        self.update(start_time, end_time, text, category)
        self.data = {}

    def update(self, start_time, end_time, text, category=None):
        """Change the event data."""
        self.time_period = TimePeriod(start_time, end_time)
        self.text = text
        self.category = category

    def update_period(self, start_time, end_time):
        """Change the event period."""
        self.time_period = TimePeriod(start_time, end_time)
        
    def update_start(self, start_time):
        """Change the event data."""
        if start_time <= self.time_period.end_time:
            self.time_period = TimePeriod(start_time, self.time_period.end_time)
            return True
        return False            

    def update_end(self, end_time):
        """Change the event data."""
        if end_time >= self.time_period.start_time:
            self.time_period = TimePeriod(self.time_period.start_time, end_time)
            return True
        return False            

    def inside_period(self, time_period):
        """Wrapper for time period method."""
        return self.time_period.overlap(time_period)

    def is_period(self):
        """Wrapper for time period method."""
        return self.time_period.is_period()

    def mean_time(self):
        """Wrapper for time period method."""
        return self.time_period.mean_time()

    def get_data(self, plugin_id):
        return self.data.get(plugin_id, None)

    def set_data(self, plugin_id, data):
        self.data[plugin_id] = data

    def has_data(self):
        """Return True if the event has associated data, or False if not."""
        for id in self.data:
            if self.data[id] != None:
                return True
        return False

    def get_label(self):
        """Returns a unicode label describing the event."""
        return u"%s (%s)" % (self.text, self.time_period.get_label())

    def notify(self, notification, data):
        """A notification has been sent to the event."""
        if notification == MSG_BALLON_VISIBILITY_CHANGED:
            if data == self:
                self.draw_ballon = True
            else:    
                self.draw_ballon = False
                
class Category(object):
    """Represents a category that an event belongs to."""

    def __init__(self, name, color, visible):
        """
        Create a category with the given name and color.

        name = string
        color = (r, g, b)
        """
        self.name = name
        self.color = color
        self.visible = visible


class TimePeriod(object):
    """
    Represents a period in time using a start and end time.

    This is used both to store the time period for an event and for storing the
    currently displayed time period in the GUI.
    """

    MIN_TIME = dt(10, 1, 1)
    MAX_TIME = dt(9990, 1, 1)

    def __init__(self, start_time, end_time):
        """
        Create a time period.

        `start_time` and `end_time` should be of the type datetime.
        """
        self.update(start_time, end_time)

    def update(self, start_time, end_time,
               start_delta=timedelta(0), end_delta=timedelta(0)):
        """
        Change the time period data.

        Optionally add the deltas to the times like this: time + delta.

        If data is invalid, it will not be set, and a ValueError will be raised
        instead.

        Data is invalid if time + delta is not within the range [MIN_TIME,
        MAX_TIME] or if the start time is larger than the end time.
        """
        pos_error = "Start time can't be after year 9989"
        neg_error = "Start time can't be before year 10"
        new_start = self._ensure_within_range(start_time, start_delta,
                                              pos_error, neg_error)
        pos_error = "End time can't be after year 9989"
        neg_error = "End time can't be before year 10"
        new_end = self._ensure_within_range(end_time, end_delta,
                                            pos_error, neg_error)
        if new_start > new_end:
            raise ValueError("Start time can't be after end time")
        self.start_time = new_start
        self.end_time = new_end

    def inside(self, time):
        """
        Return True if the given time is inside this period or on the border,
        otherwise False.
        """
        return time >= self.start_time and time <= self.end_time

    def overlap(self, time_period):
        """Return True if this time period has any overlap with the given."""
        return not (time_period.end_time < self.start_time or
                    time_period.start_time > self.end_time)

    def is_period(self):
        """
        Return True if this time period is longer than just a point in time,
        otherwise False.
        """
        return self.start_time != self.end_time

    def mean_time(self):
        """
        Return the time in the middle if this time period is longer than just a
        point in time, otherwise the point in time for this time period.
        """
        return self.start_time + self.delta() / 2

    def zoom(self, times):
        MAX_ZOOM_DELTA = timedelta(days=120*365)
        MIN_ZOOM_DELTA = timedelta(hours=1)
        delta = mult_timedelta(self.delta(), times / 10.0)
        new_delta = self.delta() - 2 * delta
        if new_delta > MAX_ZOOM_DELTA:
            raise ValueError(_("Can't zoom wider than 120 years"))
        if new_delta < MIN_ZOOM_DELTA:
            raise ValueError(_("Can't zoom deeper than 1 hour"))
        self.update(self.start_time, self.end_time, delta, -delta)

    def move(self, direction):
        """
        Move this time period one 10th to the given direction.

        Direction should be -1 for moving to the left or 1 for moving to the
        right.
        """
        delta = mult_timedelta(self.delta(), direction / 10.0)
        self.move_delta(delta)

    def move_delta(self, delta):
        self.update(self.start_time, self.end_time, delta, delta)

    def delta(self):
        """Return the length of this time period as a timedelta object."""
        return self.end_time - self.start_time

    def center(self, time):
        """
        Center time period around time keeping the length.

        If we can't center because we are on the edge, we do as good as we can.
        """
        delta = time - self.mean_time()
        start_overflow = self._calculate_overflow(self.start_time, delta)[1]
        end_overflow = self._calculate_overflow(self.end_time, delta)[1]
        if start_overflow == -1:
            delta = TimePeriod.MIN_TIME - self.start_time
        elif end_overflow == 1:
            delta = TimePeriod.MAX_TIME - self.end_time
        self.move_delta(delta)

    def fit_year(self):
        mean = self.mean_time()
        start = dt(mean.year, 1, 1)
        end = dt(mean.year + 1, 1, 1)
        self.update(start, end)

    def fit_month(self):
        mean = self.mean_time()
        start = dt(mean.year, mean.month, 1)
        end = dt(mean.year, mean.month + 1, 1)
        self.update(start, end)

    def fit_day(self):
        mean = self.mean_time()
        start = dt(mean.year, mean.month, mean.day)
        end = dt(mean.year, mean.month, mean.day + 1)
        self.update(start, end)

    def _ensure_within_range(self, time, delta, pos_error, neg_error):
        """
        Return new time (time + delta) or raise ValueError if it is not within
        the range [MIN_TIME, MAX_TIME].
        """
        new_time, overflow = self._calculate_overflow(time, delta)
        if overflow > 0:
            raise ValueError(pos_error)
        elif overflow < 0:
            raise ValueError(neg_error)
        else:
            return new_time

    def _calculate_overflow(self, time, delta):
        """
        Return a tuple (new time, overflow flag).

        Overflow flag can be -1 (overflow to the left), 0 (no overflow), or 1
        (overflow to the right).

        If overflow flag is 0 new time is time + delta, otherwise None.
        """
        try:
            new_time = time + delta
            if new_time < TimePeriod.MIN_TIME:
                return (None, -1)
            if new_time > TimePeriod.MAX_TIME:
                return (None, 1)
            return (new_time, 0)
        except OverflowError:
            if delta > timedelta(0):
                return (None, 1)
            else:
                return (None, -1)

    def get_label(self):
        """Returns a unicode string describing the time period."""
        def label_with_time(time):
            return u"%s %s" % (label_without_time(time), time_label(time))
        def label_without_time(time):
            return u"%s %s %s" % (time.day, local_to_unicode(calendar.month_abbr[time.month]), time.year)
        def time_label(time):
            return time.time().isoformat()[0:5]
        if self.is_period():
            if has_nonzero_time(self.start_time, self.end_time):
                label = u"%s to %s" % (label_with_time(self.start_time),
                                      label_with_time(self.end_time))
            else:
                label = u"%s to %s" % (label_without_time(self.start_time),
                                      label_without_time(self.end_time))
        else:
            if has_nonzero_time(self.start_time, self.end_time):
                label = u"%s" % label_with_time(self.start_time)
            else:
                label = u"%s" % label_without_time(self.start_time)
        return label


def local_to_unicode(local_string):
    """Try to convert a local string to unicode."""
    encoding = locale.getlocale()[1]
    if encoding is None:
        # TODO: What should we do here?
        return u"ERROR"
    else:
        try:
            return local_string.decode(encoding)
        except Exception:
            # TODO: What should we do here?
            return u"ERROR"


def has_nonzero_time(start_time, end_time):
    nonzero_time = (start_time.time() != time(0, 0, 0) or
                    end_time.time()   != time(0, 0, 0))
    return nonzero_time


def get_event_data_plugin(id):
    """Return an instance of the event data plugin with the given id."""
    for plugin in get_event_data_plugins():
        if plugin.get_id() == id:
            return plugin
    return None


def get_event_data_plugins():
    """
    Configure event data plugins to use.

    Configure by returning a list of instances of event data plugins.
    """
    return [DescriptionEventDataPlugin(), IconEventDataPlugin()]


def delta_to_microseconds(delta):
    """Return the number of microseconds that the timedelta represents."""
    return (delta.days * US_PER_DAY +
            delta.seconds * US_PER_SEC +
            delta.microseconds)


def microseconds_to_delta(microsecs):
    """Return a timedelta representing the given number of microseconds."""
    return timedelta(microseconds=microsecs)


def mult_timedelta(delta, num):
    """Return a new timedelta that is `num` times larger than `delta`."""
    days = delta.days * num
    seconds = delta.seconds * num
    microseconds = delta.microseconds * num
    return timedelta(days, seconds, microseconds)


def div_timedeltas(delta1, delta2):
    """Return how many times delta2 fit in delta1."""
    # Since Python can handle infinitely large numbers, this solution works. It
    # might however not be optimal. If you are clever, you should be able to
    # treat the different parts individually. But this is simple.
    total_us1 = delta_to_microseconds(delta1)
    total_us2 = delta_to_microseconds(delta2)
    # Make sure that the result is a floating point number
    return total_us1 / float(total_us2)


def time_period_center(time, length):
    """
    TimePeriod factory method.

    Return a time period with the given length (represented as a timedelta)
    centered around `time`.
    """
    half_length = mult_timedelta(length, 0.5)
    start_time = time - half_length
    end_time = time + half_length
    return TimePeriod(start_time, end_time)


def get_timeline(modele=None):
    if modele != None :
        return modele
    
    from UTILS_TL_db import TimelinePerso
    return TimelinePerso()
