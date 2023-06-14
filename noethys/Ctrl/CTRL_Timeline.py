#!/usr/bin/env python
# -*- coding: utf8 -*-

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

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _

import logging
import os.path
from datetime import datetime as dt
import six
import wx
import wx.html
import wx.lib.colourselect as colourselect
from wx.lib.masked import TimeCtrl

from Utils.UTILS_TL_data import TimelineIOError
from Utils.UTILS_TL_data import Timeline
from Utils.UTILS_TL_data import Event
from Utils.UTILS_TL_data import Category
from Utils.UTILS_TL_data import TimePeriod
from Utils.UTILS_TL_data import has_nonzero_time
from Utils import UTILS_TL_data as data
from Utils import UTILS_TL_drawing as drawing

if 'phoenix' in wx.PlatformInfo:
    import wx.lib.agw.hyperlink as HL
    from wx.adv import GenericDatePickerCtrl, DP_DROPDOWN, DP_SHOWCENTURY, EVT_DATE_CHANGED
else :
    import wx.lib.hyperlink as HL
    from wx import GenericDatePickerCtrl, DP_DROPDOWN, DP_SHOWCENTURY, EVT_DATE_CHANGED

if six.PY3:
    import functools

# Border, in pixels, between controls in a window (should always be used when
# border is needed)
BORDER = 5
# Used by dialogs as a return code when a TimelineIOError has been raised
ID_ERROR = wx.Window.NewControlId()
# Used by Sizer and Mover classes to detect when to go into action
HIT_REGION_PX_WITH = 5



class ToolBar(UTILS_Adaptations.ToolBar):
    def __init__(self, *args, **kwds):
        UTILS_Adaptations.ToolBar.__init__(self, *args, **kwds)
        self.parent = self.GetParent()

        ID_IMPRIMER = wx.Window.NewControlId()
        ID_APERCU = wx.Window.NewControlId()
        ID_IMAGE = wx.Window.NewControlId()
        ID_GO_TODAY = wx.Window.NewControlId()
        ID_GO_DATE = wx.Window.NewControlId()
        ID_GO_ARRIERE = wx.Window.NewControlId()
        ID_GO_AVANT = wx.Window.NewControlId()
        ID_AFFICHE_ANNEE = wx.Window.NewControlId()
        ID_AFFICHE_MOIS = wx.Window.NewControlId()
        ID_AFFICHE_JOUR = wx.Window.NewControlId()

        # Boutons
        self.AddLabelTool(ID_IMPRIMER,           _(u"Imprimer"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Imprimer"), "")
        self.AddLabelTool(ID_APERCU,              _(u"Aperçu"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Aperçu avant impression"), "")
        self.AddLabelTool(ID_IMAGE,                 _(u"Enreg."), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Exporter au format image"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_GO_TODAY,         _(u"Aujourd."), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Jour.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Atteindre aujourd'hui"), "")
        self.AddLabelTool(ID_GO_DATE,            _(u"Trouver"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Recherche_date.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Atteindre une date"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_AFFICHE_ANNEE, _(u"Année"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Afficher l'année"), "")
        self.AddLabelTool(ID_AFFICHE_MOIS,    _(u"Mois"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Afficher le mois"), "")
        self.AddLabelTool(ID_AFFICHE_JOUR,    _(u"Jour"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Afficher le jour"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_GO_ARRIERE,      _(u"Reculer"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Reculer.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Reculer"), "")
        self.AddLabelTool(ID_GO_AVANT,          _(u"Avancer"), wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Avancer.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Avancer"), "")

        # Binds
        self.Bind(wx.EVT_TOOL, self.parent.Imprimer, id=ID_IMPRIMER)
        self.Bind(wx.EVT_TOOL, self.parent.Apercu, id=ID_APERCU)
        self.Bind(wx.EVT_TOOL, self.parent.ExportImage, id=ID_IMAGE)
        self.Bind(wx.EVT_TOOL, self.parent.GoToday, id=ID_GO_TODAY)
        self.Bind(wx.EVT_TOOL, self.parent.GoDate, id=ID_GO_DATE)
        self.Bind(wx.EVT_TOOL, self.parent.GoArriere, id=ID_GO_ARRIERE)
        self.Bind(wx.EVT_TOOL, self.parent.GoAvant, id=ID_GO_AVANT)
        self.Bind(wx.EVT_TOOL, self.parent.AfficheAnnee, id=ID_AFFICHE_ANNEE)
        self.Bind(wx.EVT_TOOL, self.parent.AfficheMois, id=ID_AFFICHE_MOIS)
        self.Bind(wx.EVT_TOOL, self.parent.AfficheJour, id=ID_AFFICHE_JOUR)
        
        self.SetToolBitmapSize((16, 16))
        self.Realize()
    


class MainFrame(wx.Frame):
    """
    The main frame of the application.

    Can be resized, maximized and minimized. Contains one panel: MainPanel.

    Owns an instance of a timeline that is currently being displayed. When the
    timeline changes, this control will notify sub controls about it.
    """

    def __init__(self):
        wx.Frame.__init__(self, None, size=config.get_window_size(),
                          style=wx.DEFAULT_FRAME_STYLE)
        # To enable translations of wx stock items.
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self._set_initial_values_to_member_variables()
        self._create_gui()
        self.Maximize(config.get_window_maximized())
        self.mnu_view_sidebar.Check(config.get_show_sidebar())
        self.mnu_view_legend.Check(config.get_show_legend())
        self.mnu_view_balloons.Check(config.get_balloon_on_hover())
        self.SetIcons(self._load_icon_bundle())
        self.main_panel.show_welcome_panel()
        self._enable_disable_menus()

    def edit_event(self, event):
        try:
            dialog = EventEditor(self, _("Edit Event"), self.timeline,
                                 event=event)
        except TimelineIOError as e:
            self.handle_timeline_error(e)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self._switch_to_error_view(dialog.error)
            dialog.Destroy()

    def edit_categories(self):
        try:
            dialog = CategoriesEditor(self, self.timeline)
        except TimelineIOError as e:
            self.handle_timeline_error(e)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self._switch_to_error_view(dialog.error)
            dialog.Destroy()



# ---------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    """ 
    PositionToolbar = haut | bas | gauche | droite 
    """
    def __init__(self, parent, afficheSidebar=True, modele=None, 
                                        afficheToolbar=True, positionToolbar="haut",
                                        lectureSeule=False,
                                        ):
        wx.Panel.__init__(self, parent)
        self.afficheSidebar = afficheSidebar
        self.modele = modele
        self.lectureSeule = lectureSeule
        orientationSizer = wx.VERTICAL
        
        if afficheToolbar == True :
            if positionToolbar in ("gauche", "droite") : orientationTB = wx.TB_VERTICAL ; orientationSizer = wx.HORIZONTAL
            if positionToolbar in ("haut", "bas") : orientationTB = wx.TB_HORIZONTAL ; orientationSizer = wx.VERTICAL
            self.toolBar = ToolBar(self, style= orientationTB | wx.TB_FLAT | wx.TB_TEXT)
        self.timeline_panel = TimelinePanel(self, lectureSeule=lectureSeule)

        # Layout
        self.sizer = wx.BoxSizer(orientationSizer)
        if afficheToolbar == True and positionToolbar in ("haut", "gauche") :
            self.sizer.Add(self.toolBar, flag=wx.GROW, proportion=0)
        self.sizer.Add(self.timeline_panel, flag=wx.GROW, proportion=1)
        if afficheToolbar == True and positionToolbar in ("bas", "droite") :
            self.sizer.Add(self.toolBar, 0, wx.ALIGN_CENTER, 0)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        
        # Install variables for backwards compatibility
        self.catbox = self.timeline_panel.sidebar.catbox
        self.drawing_area = self.timeline_panel.drawing_area
        self.show_sidebar = self.timeline_panel.show_sidebar
        self.hide_sidebar = self.timeline_panel.hide_sidebar
        self.get_sidebar_width = self.timeline_panel.get_sidebar_width
    
    def MAJ(self, reimporterdata=False):
        self.timeline = data.get_timeline(self.modele, reimporterdata)
        self.catbox.set_timeline(self.timeline)
        self.drawing_area.set_timeline(self.timeline)
    
    def SetPositionVerticale(self, position=50):
        """ Déplace la ligne verticale (entre 0 et 100 """
        self.timeline_panel.divider_line_slider.SetValue(position)
        
    def Imprimer(self, event):
        self.drawing_area.print_timeline(event)
##        self.drawing_area.print_setup(event)

    def Apercu(self, event):
        self.drawing_area.print_preview(event)

    def ExportImage(self, event):
        extension_map = {"png": wx.BITMAP_TYPE_PNG}
        extensions = list(extension_map.keys())
        wildcard = _create_wildcard("Fichiers images", extensions)
        dialog = wx.FileDialog(self, message=_(u"Exporter au format image"),
                               wildcard=wildcard, style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path, extension = _extend_path(dialog.GetPath(), extensions, "png")
            if os.path.exists(path) :
                reponse = _ask_question(_(u"Le fichier existe déjà. Voulez-vous l'écraser ?"), self) 
                if reponse == False :
                    return
            bitmap = self.drawing_area.bgbuf
            if 'phoenix' in wx.PlatformInfo:
                image = bitmap.ConvertToImage()
            else:
                image = wx.ImageFromBitmap(bitmap)
            image.SaveFile(path, extension_map[extension])
        dialog.Destroy()

    def GoToday(self, event):
        self._navigate_timeline(lambda tp: tp.center(dt.now()))

    def GoDate(self, event):
        dialog = GotoDateDialog(self, self._get_time_period().mean_time())
        if dialog.ShowModal() == wx.ID_OK:
            self._navigate_timeline(lambda tp: tp.center(dialog.time))
        dialog.Destroy()

    def GoArriere(self, event):
        self._navigate_smart_step(-1)

    def GoAvant(self, event):
        self._navigate_smart_step(1)

    def AfficheAnnee(self, event):
        self._navigate_timeline(lambda tp: tp.fit_year())

    def AfficheMois(self, event):
        self._navigate_timeline(lambda tp: tp.fit_month())

    def AfficheJour(self, event):
        self._navigate_timeline(lambda tp: tp.fit_day())

    def _navigate_timeline(self, navigation_fn):
        return self.drawing_area.navigate_timeline(navigation_fn)

    def _get_time_period(self):
        return self.drawing_area.get_time_period()

    def _navigate_smart_step(self, direction):

        def months_to_year_and_month(months):
            years = int(months // 12)
            month = months - years * 12
            if month == 0:
                month = 12
                years -=1
            return years, month

        tp = self._get_time_period()
        start, end = tp.start_time, tp.end_time
        year_diff = end.year - start.year
        start_months = start.year * 12 + start.month
        end_months = end.year * 12 + end.month
        month_diff = end_months - start_months
        whole_years = start.replace(year=start.year + year_diff) == end
        whole_months = start.day == 1 and end.day == 1
        direction_backward = direction < 0
        # Whole years
        if whole_years and year_diff > 0:
            if direction_backward:
                new_start = start.replace(year=start.year-year_diff)
                new_end   = start
            else:
                new_start = end
                new_end   = end.replace(year=new_start.year+year_diff)
            self._navigate_timeline(lambda tp: tp.update(new_start, new_end))
        # Whole months
        elif whole_months and month_diff > 0:
            if direction_backward:
                new_end = start
                new_start_year, new_start_month = months_to_year_and_month(
                                                        start_months -
                                                        month_diff)
                new_start = start.replace(year=new_start_year,
                                          month=new_start_month)
            else:
                new_start = end
                new_end_year, new_end_month = months_to_year_and_month(
                                                        end_months +
                                                        month_diff)
                new_end = end.replace(year=new_end_year, month=new_end_month)
            self._navigate_timeline(lambda tp: tp.update(new_start, new_end))
        # No need for smart delta
        else:
            self._navigate_timeline(lambda tp: tp.move_delta(direction*tp.delta()))



class TimelinePanel(wx.Panel):
    """Showing the drawn timeline and the optional sidebar."""

    def __init__(self, parent, lectureSeule=False):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.lectureSeule = lectureSeule
        self.sidebar_width = 300
        self._create_gui()
        self.show_sidebar()
        
        if parent.afficheSidebar == False :
            self.hide_sidebar()

    def get_sidebar_width(self):
        return self.sidebar_width

    def show_sidebar(self):
        self.splitter.SplitVertically(self.sidebar, self.drawing_area, self.sidebar_width)

    def hide_sidebar(self):
        self.splitter.Unsplit(self.sidebar)

    def _create_gui(self):
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(50)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._splitter_on_splitter_sash_pos_changed, self.splitter)
        self.sidebar = Sidebar(self.splitter)
        self.divider_line_slider = wx.Slider(self, value = 50, size = (20, -1), style = wx.SL_LEFT | wx.SL_VERTICAL)
        self.drawing_area = DrawingArea(self.splitter, self.divider_line_slider, self.lectureSeule)
        globalSizer = wx.BoxSizer(wx.HORIZONTAL)
        globalSizer.Add(self.splitter, 1, wx.EXPAND)
        globalSizer.Add(self.divider_line_slider, 0, wx.EXPAND)
        self.SetSizer(globalSizer)

    def _splitter_on_splitter_sash_pos_changed(self, e):
        self.sidebar_width = self.splitter.GetSashPosition()


class Sidebar(wx.Panel):
    """
    The left part in TimelinePanel.

    Currently only shows the categories with visibility check boxes.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.BORDER_NONE)
        self._create_gui()

    def _create_gui(self):
        self.catbox = CategoriesVisibleCheckListBox(self)
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.catbox, flag=wx.GROW, proportion=1)
        self.SetSizer(sizer)


class CategoriesVisibleCheckListBox(wx.CheckListBox):
    # ClientData can not be used in this control
    # (see http://docs.wxwidgets.org/stable/wx_wxchecklistbox.html)
    # This workaround will not work if items are reordered

    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent)
        self.timeline = None
        self.Bind(wx.EVT_CHECKLISTBOX, self._checklistbox_on_checklistbox, self)

    def set_timeline(self, timeline):
        if self.timeline != None:
            self.timeline.unregister(self._timeline_changed)
        self.timeline = timeline
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            self._update_categories()
        else:
            self.Clear()

    def _checklistbox_on_checklistbox(self, e):
        i = e.GetSelection()
        self.categories[i].visible = self.IsChecked(i)
        try:
            self.timeline.category_edited(self.categories[i])
        except TimelineIOError as e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)

    def _timeline_changed(self, state_change):
        if state_change == Timeline.STATE_CHANGE_CATEGORY:
            self._update_categories()

    def _update_categories(self):
        try:
            self.categories = sort_categories(self.timeline.get_categories())
        except TimelineIOError as e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)
        else:
            self.Clear()
            self.AppendItems([category.name for category in self.categories])
            for i in range(0, self.Count):
                if self.categories[i].visible:
                    self.Check(i)
                self.SetItemBackgroundColour(i, self.categories[i].color)



class EventSizer(object):
    """Objects of this class are used to simplify resizing of events."""

    _singletons = {}
    _initialized = False
    
    def __new__(cls, *args, **kwds):
        """Implement the Singleton pattern for this class."""
        if cls not in cls._singletons:
            cls._singletons[cls] = super(EventSizer, cls).__new__(cls)
        return cls._singletons[cls]    
    
    def __init__(self, drawing_area, m_x = 0, m_y = 0):
        if not EventSizer._initialized:
            self.direction = wx.LEFT
            self.drawing_area = drawing_area
            self.metrics = self.drawing_area.drawing_algorithm.metrics
            self.sizing = False
            self.event = None
            EventSizer._initialized = True
        try :
            self.metrics = self.drawing_area.drawing_algorithm.metrics
        except :
            pass

    def sizing_starts(self, m_x, m_y):
        """
        If it is ok to start a resize... initialize the resize and return True.
        Otherwise return False.
        """
        self.sizing = self._hit(m_x, m_y) and self.event.selected
        if self.sizing:
            self.x = m_x
            self.y = m_y
        return self.sizing

    def is_sizing(self):
        """Return True if we are in a resizing state, otherwise return False."""
        return self.sizing

    def set_cursor(self, m_x, m_y):
        """
        Used in mouse-move events to set the size cursor before the left mouse
        button is pressed, to indicate that a resize is possible (if it is!).
        Return True if the size-indicator-cursor is set, otherwise return False.
        """
        hit = self._hit(m_x, m_y)
        if hit:
            if not self.event.selected:
                return False
            self.drawing_area._set_size_cursor()
        else:
            self.drawing_area._set_default_cursor()
        return hit

    def _hit(self, m_x, m_y):
        """
        Calculate the 'hit-for-resize' coordinates and return True if
        the mouse is within this area. Otherwise return False.
        The 'hit-for-resize' area is the are at the left and right edges of the
        event rectangle with a width of HIT_REGION_PX_WITH.
        """
        event_info = self.drawing_area.drawing_algorithm.event_with_rect_at(m_x, m_y)
        if event_info == None:
            return False
        self.event, rect = event_info
        if abs(m_x - rect.X) < HIT_REGION_PX_WITH:
            self.direction = wx.LEFT
            return True
        elif abs(rect.X + rect.Width - m_x) < HIT_REGION_PX_WITH:
            self.direction = wx.RIGHT
            return True
        return False

    def resize(self, m_x, m_y):
        """
        Resize the event either on the left or the right side.
        The event edge is snapped to the grid.
        """
        time = self.metrics.get_time(m_x)
        time = self.drawing_area.drawing_algorithm.snap(time)
        resized = False
        if self.direction == wx.LEFT:
            resized = self.event.update_start(time)
        else:
            resized = self.event.update_end(time)
        if resized:
            self.drawing_area._redraw_timeline()

class EventMover(object):
    """Objects of this class are used to simplify moving of events."""

    _singletons = {}
    _initialized = False
    
    def __new__(cls, *args, **kwds):
        """Implement the Singleton pattern for this class."""
        if cls not in cls._singletons:
            cls._singletons[cls] = super(EventMover, cls).__new__(cls)
        return cls._singletons[cls]    
    
    def __init__(self, drawing_area):
        """Initialize only the first time the class constructor is called."""
        if not EventMover._initialized:
            self.drawing_area = drawing_area
            self.drawing_algorithm = self.drawing_area.drawing_algorithm
            self.moving = False
            self.event = None
            EventMover._initialized = True

    def move_starts(self, m_x, m_y):
        """
        If it is ok to start a move... initialize the move and return True.
        Otherwise return False.
        """
        self.moving = self._hit(m_x, m_y) and self.event.selected
        if self.moving:
            self.x = m_x
            self.y = m_y
        return self.moving
        
    def is_moving(self):
        """Return True if we are in a moving state, otherwise return False."""
        return self.moving

    def set_cursor(self, m_x, m_y):
        """
        Used in mouse-move events to set the move cursor before the left mouse
        button is pressed, to indicate that a move is possible (if it is!).
        Return True if the move-indicator-cursor is set, otherwise return False.
        """
        hit = self._hit(m_x, m_y)
        if hit:
            if not self.event.selected:
                return False
            self.drawing_area._set_move_cursor()
        else:
            self.drawing_area._set_default_cursor()
        return hit

    def move(self, m_x, m_y):
        """
        Move the event the time distance, difftime, represented by the distance the
        mouse has moved since the last move (m_x - self.x).
        Events found above the center line are snapped to the grid.
        """
        difftime = self.drawing_algorithm.metrics.get_difftime(m_x, self.x)
        # Snap events found above the center line
        start = self.event.time_period.start_time + difftime
        end = self.event.time_period.end_time + difftime
        if not self.drawing_algorithm.event_is_period(self.event.time_period):
            halfperiod = (end - start) / 2
            middletime = self.drawing_algorithm.snap(start + halfperiod)
            start = middletime - halfperiod
            end = middletime + halfperiod
        else:
            width = start - end
            startSnapped = self.drawing_area.drawing_algorithm.snap(start)
            endSnapped = self.drawing_area.drawing_algorithm.snap(end)
            if startSnapped != start:
                # Prefer to snap at left edge (in case end snapped as well)
                start = startSnapped
                end = start - width
            elif endSnapped != end:
                end = endSnapped
                start = end + width
        # Update and redraw the event
        self.event.update_period(start, end)
        self.drawing_area._redraw_timeline()
        # Adjust the coordinates  to get a smooth movement of cursor and event.
        # We can't use event_with_rect_at() method to get hold of the rect since
        # events can jump over each other when moved.
        rect = self.drawing_algorithm.event_rect(self.event)
        if rect != None:
            self.x = rect.X + rect.Width / 2
        else:
            self.x = m_x
        self.y = m_y

    def _hit(self, m_x, m_y):
        """
        Calculate the 'hit-for-move' coordinates and return True if
        the mouse is within this area. Otherwise return False.
        The 'hit-for-move' area is the are at the center of an event
        with a width of 2 * HIT_REGION_PX_WITH.
        """
        event_info = self.drawing_area.drawing_algorithm.event_with_rect_at(m_x, m_y)
        if event_info == None:
            return False
        self.event, rect = event_info
        center = rect.X + rect.Width / 2
        if abs(m_x - center) <= HIT_REGION_PX_WITH:
            return True
        return False

class DrawingArea(wx.Panel):
    """
    The right part in TimelinePanel: a window on which the timeline is drawn.

    This class has information about what timeline and what part of the
    timeline to draw and makes sure that the timeline is redrawn whenever it is
    needed.

    Double buffering is used to avoid flicker while drawing. This is
    accomplished by always drawing to a background buffer: bgbuf. The paint
    method of the control thus only draws the background buffer to the screen.

    Scrolling and zooming of the timeline is implemented in this class. This is
    done whenever the mouse wheel is scrolled (_window_on_mousewheel).
    Moving also takes place when the mouse is dragged while pressing the left
    mouse key (_window_on_motion).

    Selection of a period on the timeline (period = any number of minor strips)
    is also implemented in this class. A selection is done in the following
    way: Press and hold down the Control key on the keyboard, move the mouse to
    the first minor strip to be selected and then press and hold down the left
    mouse key. Now, while moving the mouse over the timeline, the minor strips
    will be selected.

    What happens is that when the left mouse button is pressed
    (_window_on_left_down) the variable self._current_time is set to the
    time on the timeline where the mouse is. This is the anchor point for the
    selection. When the mouse is moved (_window_on_motion) and left mouse button
    is pressed and the Control key is held down the method
    self._mark_selected_minor_strips(evt.m_x) is called. This method marks all
    minor strips between the anchor point and the current point (evt.m_x).
    When the mouse button is released the selection ends.
    """

    def __init__(self, parent, divider_line_slider, lectureSeule=False):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self.divider_line_slider = divider_line_slider
        self.lectureSeule = lectureSeule
        self._create_gui()
        self._set_initial_values_to_member_variables()
        self._set_colors_and_styles()
        self.timeline = None
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printData.SetOrientation(wx.LANDSCAPE)
        logging.debug("Init done in DrawingArea")

    def print_timeline(self, event):
        pdd = wx.PrintDialogData(self.printData)
        pdd.SetToPage(1)
        printer = wx.Printer(pdd)
        printout = drawing.TimelinePrintout(self, False)
        frame = wx.GetApp().GetTopWindow()
        if not printer.Print(frame, printout, True):
            if printer.GetLastError() == wx.PRINTER_ERROR:
                wx.MessageBox(_(u"Problème d'impression. Peut-être votre imprimante n'est-elle pas configurée correctement ?"), "Impression", wx.OK)
        else:
            self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()

    def print_preview(self, event):
        data = wx.PrintDialogData(self.printData)
        printout_preview  = drawing.TimelinePrintout(self, True)
        printout = drawing.TimelinePrintout(self, False)
        self.preview = wx.PrintPreview(printout_preview, printout, data)
        if 'phoenix' in wx.PlatformInfo:
            etat = self.preview.IsOk()
        else:
            etat = self.preview.Ok()
        if not etat:
            logging.debug(_(u"Impossible d'afficher l'aperçu avant impression...\n"))
            return
        frame = wx.GetApp().GetTopWindow()
        pfrm = wx.PreviewFrame(self.preview, frame, _(u"Aperçu avant impression"))
        pfrm.Initialize()
        pfrm.SetPosition(frame.GetPosition())
        pfrm.SetSize(frame.GetSize())
        pfrm.Show(True)

    def print_setup(self, event):
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(self, psdd)
        dlg.ShowModal()
        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        self.printData = wx.PrintData( dlg.GetPageSetupData().GetPrintData() )
        dlg.Destroy()

    def set_timeline(self, timeline):
        """Inform what timeline to draw."""
        if self.timeline != None:
            self.timeline.unregister(self._timeline_changed)
        self.timeline = timeline
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            try:
                self.time_period = timeline.get_preferred_period()
            except TimelineIOError as e:
                wx.GetTopLevelParent(self).handle_timeline_error(e)
                return
            self._redraw_timeline()
            self.Enable()
            self.SetFocus()
        else:
            self.Disable()

    def show_hide_legend(self, show):
        self.show_legend = show
        if self.timeline:
            self._redraw_timeline()

    def get_time_period(self):
        """Return currently displayed time period."""
        if self.timeline == None:
            raise Exception("No timeline set")
        return self.time_period

    def navigate_timeline(self, navigation_fn):
        """
        Perform a navigation operation followed by a redraw.

        The navigation_fn should take one argument which is the time period
        that should be manipulated in order to carry out the navigation
        operation.

        Should the navigation operation fail (max zoom level reached, etc) a
        message will be displayed in the statusbar.

        Note: The time period should never be modified directly. This method
        should always be used instead.
        """
        if self.timeline == None:
            raise Exception("No timeline set")
        try:
            navigation_fn(self.time_period)
            self._redraw_timeline()
        except : pass
        try :
            wx.GetTopLevelParent(self).SetStatusText("")
        except : pass
##        except (ValueError, OverflowError), e:
##            print e.message

    def _create_gui(self):
        self.Bind(wx.EVT_SIZE, self._window_on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._window_on_erase_background)
        self.Bind(wx.EVT_PAINT, self._window_on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._window_on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self._window_on_right_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._window_on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self._window_on_left_up)
        self.Bind(wx.EVT_MOTION, self._window_on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self._window_on_mousewheel)
        self.Bind(wx.EVT_KEY_DOWN, self._window_on_key_down)
        self.Bind(wx.EVT_KEY_UP, self._window_on_key_up)
        self.divider_line_slider.Bind(wx.EVT_SLIDER, self._slider_on_slider)
        self.divider_line_slider.Bind(wx.EVT_CONTEXT_MENU, self._slider_on_context_menu)

    def _window_on_size(self, event):
        """
        Event handler used when the window has been resized.

        Called at the application start and when the frame is resized.

        Here we create a new background buffer with the new size and draw the
        timeline onto it.
        """
        if 'phoenix' in wx.PlatformInfo:
            logging.debug("Resize event in DrawingArea: %s", self.GetSize())
            width, height = self.GetSize()
            self.bgbuf = wx.Bitmap(width, height)
        else :
            logging.debug("Resize event in DrawingArea: %s", self.GetSizeTuple())
            width, height = self.GetSizeTuple()
            self.bgbuf = wx.EmptyBitmap(width, height)
        self._redraw_timeline()

    def _window_on_erase_background(self, event):
        # For double buffering
        pass

    def _window_on_paint(self, event):
        """
        Event handler used when the window needs repainting.

        Called at the application start, after resizing, or when the window
        becomes active.

        Here we just draw the background buffer onto the screen.

        Defining a dc is crucial. Even if it is not used.
        """
        logging.debug("Paint event in DrawingArea")
        dc = wx.AutoBufferedPaintDC(self)
        if 'phoenix' not in wx.PlatformInfo:
            dc.BeginDrawing()
        dc.DrawBitmap(self.bgbuf, 0, 0, True)
        if 'phoenix' not in wx.PlatformInfo:
            dc.EndDrawing()

    def _window_on_left_down(self, evt):
        """
        Event handler used when the left mouse button has been pressed.

        This event establishes a new current time on the timeline.

        If the mouse hits an event that event will be selected.
        """
        try:
            logging.debug("Left mouse pressed event in DrawingArea")
            self._set_new_current_time(evt.GetX()) # (evt.m_x)
            
            if self.lectureSeule == False :
                # If we hit the event resize area of an event, start resizing
                if EventSizer(self).sizing_starts(evt.GetX(), evt.GetY()) : # (evt.m_x, evt.m_y):
                    return
                # If we hit the event move area of an event, start moving
                if EventMover(self).move_starts(evt.GetX(), evt.GetY()) : # (evt.m_x, evt.m_y):
                    return
                
                # No resizing or moving of events...
                posAtEvent = self._toggle_event_selection(evt.GetX(), evt.GetY(), evt.ControlDown()) # (evt.m_x, evt.m_y, evt.m_controlDown)
            else:
                posAtEvent = None
                
            if not posAtEvent:
                if evt.ControlDown() : # evt.m_controlDown:
                    self._set_select_period_cursor()
            evt.Skip()
        except TimelineIOError as e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)

    def _window_on_right_down(self, evt):
        """
        Event handler used when the right mouse button has been pressed.

        If the mouse hits an event the context menu for that event is displayed.
        """
        self.context_menu_event = self.drawing_algorithm.event_at(evt.GetX(), evt.GetY()) # (evt.m_x, evt.m_y)
        if self.context_menu_event == None or self.lectureSeule == True :
            return
        menu_definitions = (
            (_(u"Modifier"), self._context_menu_on_edit_event),
            (_(u"Supprimer"), self._context_menu_on_delete_event),
        )
        menu = UTILS_Adaptations.Menu()
        for menu_definition in menu_definitions:
            text, method = menu_definition
            menu_item = wx.MenuItem(menu, wx.Window.NewControlId(), text)
            self.Bind(wx.EVT_MENU, method, id=menu_item.GetId())
            menu.AppendItem(menu_item)
        self.PopupMenu(menu)
        menu.Destroy()
        
    def _context_menu_on_edit_event(self, evt):
        frame = wx.GetTopLevelParent(self)
        frame.edit_event(self.context_menu_event)
        
    def _context_menu_on_delete_event(self, evt):
        self.context_menu_event.selected = True
        self._delete_selected_events()
    
    def _window_on_left_dclick(self, evt):
        """
        Event handler used when the left mouse button has been double clicked.

        If the mouse hits an event, a dialog opens for editing this event.
        Otherwise a dialog for creating a new event is opened.
        """
        logging.debug("Left Mouse doubleclicked event in DrawingArea")
        # Since the event sequence is, 1. EVT_LEFT_DOWN  2. EVT_LEFT_UP
        # 3. EVT_LEFT_DCLICK we must compensate for the toggle_event_selection
        # that occurs in the handling of EVT_LEFT_DOWN, since we still want
        # the event(s) selected or deselected after a left doubleclick
        # It doesn't look too god but I havent found any other way to do it.
        if self.lectureSeule == True :
            return
        self._toggle_event_selection(evt.GetX(), evt.GetY(), evt.ControlDown()) # (evt.m_x, evt.m_y,evt.m_controlDown)
        event = self.drawing_algorithm.event_at(evt.GetX(), evt.GetY()) # (evt.m_x, evt.m_y)
        if event:
            wx.GetTopLevelParent(self).edit_event(event)
        else:
            wx.GetTopLevelParent(self).create_new_event(self._current_time,
                                                        self._current_time)

    def _window_on_left_up(self, evt):
        """
        Event handler used when the left mouse button has been released.

        If there is an ongoing selection-marking, the dialog for creating an
        event will be opened, and the selection-marking will be ended.
        """
        logging.debug("Left mouse released event in DrawingArea")
        if self.is_selecting:
            self._end_selection_and_create_event(evt.GetX()) # (evt.m_x)
        self.is_selecting = False
        self.is_scrolling = False
        self._set_default_cursor()

    def _window_on_motion(self, evt):
        """
        Event handler used when the mouse has been moved.

        If the mouse is over an event, the name of that event will be printed
        in the status bar.

        If the left mouse key is down one of two things happens depending on if
        the Control key is down or not. If it is down a selection-marking takes
        place and the minor strips passed by the mouse will be selected.  If
        the Control key is up the timeline will scroll.
        """
        logging.debug("Mouse move event in DrawingArea")
        if evt.LeftIsDown() : #evt.m_leftDown:
            self._mouse_drag(evt.GetX(), evt.GetY(), evt.ControlDown() ) #evt.m_x, evt.m_y, evt.m_controlDown)
        else:
            if not evt.ControlDown() : #evt.m_controlDown:
                try :
                    self._mouse_move(evt.GetX(), evt.GetY()) # (evt.m_x, evt.m_y)
                except :
                    pass
                
    def _mouse_drag(self, x, y, ctrl=False):
        """
        The mouse has been moved.
        The left mouse button is depressed
        ctrl indicates if the Ctrl-key is depressed or not
        """
        if self.is_scrolling:
            self._scroll(x)
        elif self.is_selecting:
            self._mark_selected_minor_strips(x)
        elif EventSizer(self).is_sizing():
            EventSizer(self).resize(x, y)
        elif EventMover(self).is_moving():
            EventMover(self).move(x, y)
        else:
            if ctrl:
                self._mark_selected_minor_strips(x)
                self.is_selecting = True
            else:
                self._scroll(x)
                self.is_scrolling = True
    
    def _mouse_move(self, x, y):
        """
        The mouse has been moved.
        The left mouse button is not depressed
        The Ctrl-key is not depressed
        """
        self._display_balloon_on_hoover(x, y)
        self._display_eventinfo_in_statusbar(x, y)
        cursor_set = EventSizer(self).set_cursor(x, y)
        if not cursor_set:
            EventMover(self).set_cursor(x, y)
                
    def _window_on_mousewheel(self, evt):
        """
        Event handler used when the mouse wheel is rotated.

        If the Control key is pressed at the same time as the mouse wheel is
        scrolled the timeline will be zoomed, otherwise it will be scrolled.
        """
        logging.debug("Mouse wheel event in DrawingArea")
        direction = _step_function(evt.GetWheelRotation()) # (evt.m_wheelRotation)
        if evt.ControlDown() : #evt.ControlDown():
            self._zoom_timeline(direction)
        else:
            delta = data.mult_timedelta(self.time_period.delta(),
                                        direction / 10.0)
            self._scroll_timeline(delta)

    def _window_on_key_down(self, evt):
        """
        Event handler used when a keyboard key has been pressed.

        The following keys are handled:
        Key         Action
        --------    ------------------------------------
        Delete      Delete any selected event(s)
        Control     Change cursor
        """
        logging.debug("Key down event in DrawingArea")
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_DELETE:
            self._delete_selected_events()
        evt.Skip()

    def _window_on_key_up(self, evt):
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_CONTROL:
            self._set_default_cursor()

    def _slider_on_slider(self, evt):
        """The divider-line slider has been moved."""
        self._redraw_timeline()

    def _slider_on_context_menu(self, evt):
        """A right click has occured in the divider-line slider."""
        menu = UTILS_Adaptations.Menu()
        menu_item = wx.MenuItem(menu, wx.Window.NewControlId(), "Center")
        self.Bind(wx.EVT_MENU, self._context_menu_on_menu_center,
                  id=menu_item.GetId())
        menu.AppendItem(menu_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_menu_center(self, evt):
        """The 'Center' context menu has been selected."""
        self.divider_line_slider.SetValue(50)
        self._redraw_timeline()

    def _timeline_changed(self, state_change):
        if state_change == Timeline.STATE_CHANGE_ANY:
            self._redraw_timeline()

    def _set_initial_values_to_member_variables(self):
        """
        Instance variables usage:

        _current_time       This variable is set to the time on the timeline
                            where the mouse button is clicked when the left
                            mouse button is used
        _mark_selection     Processing flag indicating ongoing selection of a
                            time period
        timeline            The timeline currently handled by the application
        time_period         The part of the timeline currently displayed in the
                            drawing area
        drawing_algorithm   The algorithm used to draw the timeline
        bgbuf               The bitmap to which the drawing methods draw the
                            timeline. When the EVT_PAINT occurs this bitmap
                            is painted on the screen. This is a buffer drawing
                            approach for avoiding screen flicker.
        is_scrolling        True when scrolling with the mouse takes place.
                            It is set True in mouse_has_moved and set False
                            in left_mouse_button_released.
        is_selecting        True when selecting with the mouse takes place
                            It is set True in mouse_has_moved and set False
                            in left_mouse_button_released.
        show_balloons_on_hover Show ballons on mouse hoover without clicking
        """
        self._current_time = None
        self._mark_selection = False
        self.bgbuf = None
        self.timeline = None
        self.time_period = None
        self.drawing_algorithm = drawing.get_algorithm()
        self.is_scrolling = False
        self.is_selecting = False
####        self.show_legend = config.get_show_legend()
        self.show_legend = True
####        self.show_balloons_on_hover = config.get_balloon_on_hover()
        self.show_balloons_on_hover = True

    def _set_colors_and_styles(self):
        """Define the look and feel of the drawing area."""
        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self._set_default_cursor()
        self.Disable()

    def _redraw_timeline(self, period_selection=None):
        """Draw the timeline onto the background buffer."""
        logging.debug("Draw timeline to bgbuf")
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.bgbuf)
        try:
            if 'phoenix' not in wx.PlatformInfo:
                memdc.BeginDrawing()
            memdc.SetBackground(wx.Brush(wx.WHITE, wx.SOLID))
            memdc.Clear()
            if self.timeline:
                try:
                    current_events = self.timeline.get_events(self.time_period)
                except TimelineIOError as e:
                    wx.GetTopLevelParent(self).handle_timeline_error(e)
                else:
                    self.drawing_algorithm.draw(memdc, self.time_period,
                                                current_events,
                                                period_selection,
                                                self.show_legend,
                                                self.divider_line_slider)
            if 'phoenix' not in wx.PlatformInfo:
                memdc.EndDrawing()
            del memdc
            self.Refresh()
            self.Update()
        except Exception as ex:
            self.bgbuf = None
            logging.fatal("Error in drawing", exc_info=ex)

    def _scroll(self, xpixelpos):
        if self._current_time:
            delta = (self.drawing_algorithm.metrics.get_time(xpixelpos) -
                        self._current_time)
            self._scroll_timeline(delta)

    def _set_new_current_time(self, current_x):
        self._current_time = self.drawing_algorithm.metrics.get_time(current_x)
        logging.debug("Marked time " + self._current_time.isoformat("-"))

    def _toggle_event_selection(self, xpixelpos, ypixelpos, control_down):
        """
        If the given position is within the boundaries of an event that event
        will be selected or unselected depending on the current selection
        state of the event. If the Control key is down all other events
        selection state are preserved. This means that previously selected
        events will stay selected. If the Control keys is not down all other
        events will be unselected.

        If the given position isn't within an event all selected events will
        be unselected.

        Return True if the given position was with an event, otherwise
        return False.
        """
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event:
            selected = event.selected
            if not control_down:
                self.timeline.reset_selected_events()
            self.timeline.select_event(event, not selected)
        else:
            self.timeline.reset_selected_events()
        return event != None

    def _end_selection_and_create_event(self, current_x):
        self._mark_selection = False
        period_selection = self._get_period_selection(current_x)
        start, end = period_selection
        wx.GetTopLevelParent(self).create_new_event(start, end)
        self._redraw_timeline()

    def _display_eventinfo_in_statusbar(self, xpixelpos, ypixelpos):
        """
        If the given position is within the boundaries of an event, the name of
        that event will be displayed in the status bar, otherwise the status
        bar text will be removed.
        """
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event != None:
            self._display_text_in_statusbar(event.get_label())
        else:
            self._reset_text_in_statusbar()
            
    def _display_balloon_on_hoover(self, xpixelpos, ypixelpos):
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if self.show_balloons_on_hover:
            if event and not event.selected:
                self.event_just_hoverd = event    
                self.timer = wx.Timer(self, -1)
                self.Bind(wx.EVT_TIMER, self.on_balloon_timer, self.timer)
                self.timer.Start(milliseconds=500, oneShot=True)
            else:
                self.event_just_hoverd = None
                self.redraw_balloons(None)
                
    def on_balloon_timer(self, event):
        self.redraw_balloons(self.event_just_hoverd)
   
    def redraw_balloons(self, event):
        self.drawing_algorithm.notify_events(
                data.MSG_BALLON_VISIBILITY_CHANGED, event)
        self._redraw_timeline()
        
    def _mark_selected_minor_strips(self, current_x):
        """Selection-marking starts or continues."""
        self._mark_selection = True
        period_selection = self._get_period_selection(current_x)
        self._redraw_timeline(period_selection)

    def _scroll_timeline(self, delta):
        self.navigate_timeline(lambda tp: tp.move_delta(-delta))

    def _zoom_timeline(self, direction=0):
        self.navigate_timeline(lambda tp: tp.zoom(direction))

    def _delete_selected_events(self):
        """After acknowledge from the user, delete all selected events."""
        selected_events = self.drawing_algorithm.get_selected_events()
        nbr_of_selected_events = len(selected_events)
        if nbr_of_selected_events > 1:
            text = _(u"Confirmez-vous la suppression de %d évènements ?") % nbr_of_selected_events
        else:
            text = _(u"Confirmez-vous la suppression de l'évènement ?")
        if _ask_question(text, self) == wx.YES:
            try:
                self.timeline.delete_selected_events()
            except TimelineIOError as e:
                wx.GetTopLevelParent(self).handle_timeline_error(e)

    def _get_period_selection(self, current_x):
        """Return a tuple containing the start and end time of a selection."""
        start = self._current_time
        end   = self.drawing_algorithm.metrics.get_time(current_x)
        if start > end:
            start, end = end, start
        period_selection = self.drawing_algorithm.snap_selection((start,end))
        return period_selection

    def _display_text_in_statusbar(self, text):
        try :
            wx.GetTopLevelParent(self).SetStatusText(text)
        except : 
            pass

    def _reset_text_in_statusbar(self):
        try :
            wx.GetTopLevelParent(self).SetStatusText("")
        except :
            pass

    def _set_select_period_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))

    def _set_drag_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def _set_size_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def _set_move_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))

    def _set_default_cursor(self):
        """
        Set the cursor to it's default shape when it is in the timeline
        drawing area.
        """
        if 'phoenix' in wx.PlatformInfo:
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        else :
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def balloon_visibility_changed(self, visible):
        self.show_balloons_on_hover = visible
        # When display on hovering is disabled we have to make sure 
        # that any visible balloon is removed.
        if not visible:
            self.drawing_algorithm.notify_events(
                            data.MSG_BALLON_VISIBILITY_CHANGED, None)
            self._redraw_timeline()


# ---------------------------------------------------------------------------------------------------------------

class EventEditor(wx.Dialog):
    """Dialog used for creating and editing events."""

    def __init__(self, parent, title, timeline,
                 start=None, end=None, event=None):
        """
        Create a event editor dialog.

        The 'event' argument is optional. If it is given the dialog is used
        to edit this event and the controls are filled with data from
        the event and the arguments 'start' and 'end' are ignored.

        If the 'event' argument isn't given the dialog is used to create a
        new event, and the controls for start and end time are initially
        filled with data from the arguments 'start' and 'end' if they are
        given. Otherwise they will default to today.
        """
        wx.Dialog.__init__(self, parent, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.timeline = timeline
        self.event = event
        self._create_gui()
        self._fill_controls_with_data(start, end)
        self._set_initial_focus()

    def _create_gui(self):
        """Create the controls of the dialog."""
        # Groupbox
        groupbox = wx.StaticBox(self, wx.ID_ANY, "Event Properties")
        groupbox_sizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        # Grid
        grid = wx.FlexGridSizer(rows=4, cols=2, vgap=BORDER, hgap=BORDER)
        grid.AddGrowableCol(1)
        # Grid: When: Label + DateTimePickers
        grid.Add(wx.StaticText(self, label="When:"),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        self.dtp_start = DateTimePicker(self)
        self.lbl_to = wx.StaticText(self, label="to")
        self.dtp_end = DateTimePicker(self)
        when_box = wx.BoxSizer(wx.HORIZONTAL)
        when_box.Add(self.dtp_start, proportion=1)
        when_box.AddSpacer(BORDER)
        when_box.Add(self.lbl_to, flag=wx.ALIGN_CENTER_VERTICAL|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        when_box.AddSpacer(BORDER)
        when_box.Add(self.dtp_end, proportion=1,
                     flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        grid.Add(when_box)
        # Grid: When: Checkboxes
        grid.AddStretchSpacer()
        when_box_props = wx.BoxSizer(wx.HORIZONTAL)
        self.chb_period = wx.CheckBox(self, label="Period")
        self.Bind(wx.EVT_CHECKBOX, self._chb_period_on_checkbox,
                  self.chb_period)
        when_box_props.Add(self.chb_period)
        self.chb_show_time = wx.CheckBox(self, label="Show time")
        self.Bind(wx.EVT_CHECKBOX, self._chb_show_time_on_checkbox,
                  self.chb_show_time)
        when_box_props.Add(self.chb_show_time)
        grid.Add(when_box_props)
        # Grid: Text
        self.txt_text = wx.TextCtrl(self, wx.ID_ANY)
        grid.Add(wx.StaticText(self, label="Text:"),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.txt_text, flag=wx.EXPAND)
        # Grid: Category
        self.lst_category = wx.Choice(self, wx.ID_ANY)
        grid.Add(wx.StaticText(self, label="Category:"),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.lst_category)
        groupbox_sizer.Add(grid, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.Bind(wx.EVT_CHOICE, self._lst_category_on_choice,
                  self.lst_category)
        # Plugins
        self.event_data_plugins = []
        notebook = wx.Notebook(self, style=wx.BK_DEFAULT)
        for plugin in data.get_event_data_plugins():
            panel = wx.Panel(notebook)
            notebook.AddPage(panel, plugin.get_name())
            editor = plugin.create_editor(panel)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(editor, flag=wx.EXPAND, proportion=1)
            panel.SetSizer(sizer)
            self.event_data_plugins.append((plugin, editor))
        groupbox_sizer.Add(notebook, border=BORDER, flag=wx.ALL|wx.EXPAND,
                           proportion=1)
        # Main (vertical layout)
        main_box = wx.BoxSizer(wx.VERTICAL)
        # Main: Groupbox
        main_box.Add(groupbox_sizer, flag=wx.EXPAND|wx.ALL, border=BORDER,
                     proportion=1)
        # Main: Checkbox
        self.chb_add_more = wx.CheckBox(self, label="Add more events after this one")
        main_box.Add(self.chb_add_more, flag=wx.ALL, border=BORDER)
        # Main: Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        main_box.Add(button_box, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Hide if not creating new
        if self.event != None:
            self.chb_add_more.Show(False)
        # Realize
        self.SetSizerAndFit(main_box)

    def _btn_ok_on_click(self, evt):
        """
        Add new or update existing event.

        If the Close-on-ok checkbox is checked the dialog is also closed.
        """
        try:
            logging.debug("_btn_ok_on_click")
            try:
                # Input value retrieval and validation
                start_time = self.dtp_start.get_value()
                end_time = start_time
                if self.chb_period.IsChecked():
                    end_time = self.dtp_end.get_value()
                selection = self.lst_category.GetSelection()
                category = self.lst_category.GetClientData(selection)
                if start_time > end_time:
                    raise TxtException("End must be > Start", self.dtp_start)
                name = _parse_text_from_textbox(self.txt_text, "Text")
                # Update existing event
                if self.updatemode:
                    self.event.update(start_time, end_time, name, category)
                    for plugin, editor in self.event_data_plugins:
                        self.event.set_data(plugin.get_id(),
                                            plugin.get_editor_data(editor))
                    self.timeline.event_edited(self.event)
                # Create new event
                else:
                    self.event = Event(start_time, end_time, name, category)
                    for plugin, editor in self.event_data_plugins:
                        self.event.set_data(plugin.get_id(),
                                            plugin.get_editor_data(editor))
                    self.timeline.add_event(self.event)
                # Close the dialog ?
                if self.chb_add_more.GetValue():
                    self.txt_text.SetValue("")
                    for plugin, editor in self.event_data_plugins:
                        plugin.clear_editor_data(editor)
                else:
                    self._close()
            except TxtException as ex:
                _display_error_message("%s" % ex.error_message)
                _set_focus_and_select(ex.control)
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _chb_period_on_checkbox(self, e):
        self._show_to_time(e.IsChecked())

    def _chb_show_time_on_checkbox(self, e):
        self.dtp_start.show_time(e.IsChecked())
        self.dtp_end.show_time(e.IsChecked())

    def _lst_category_on_choice(self, e):
        new_selection_index = e.GetSelection()
        if new_selection_index > self.last_real_category_index:
            self.lst_category.SetSelection(self.current_category_selection)
            if new_selection_index == self.add_category_item_index:
                self._add_category()
            elif new_selection_index == self.edit_categoris_item_index:
                self._edit_categories()
        else:
            self.current_category_selection = new_selection_index

    def _add_category(self):
        try:
            dialog = CategoryEditor(self, "Add Category",
                                    self.timeline, None)
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            dialog_result = dialog.ShowModal()
            if dialog_result == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            elif dialog_result == wx.ID_OK:
                try:
                    self._update_categories(dialog.get_edited_category())
                except TimelineIOError as e:
                    _display_error_message(e.message, self)
                    self.error = e
                    self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _edit_categories(self):
        try:
            dialog = CategoriesEditor(self, self.timeline)
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            else:
                try:
                    prev_index = self.lst_category.GetSelection()
                    prev_category = self.lst_category.GetClientData(prev_index)
                    self._update_categories(prev_category)
                except TimelineIOError as e:
                    _display_error_message(e.message, self)
                    self.error = e
                    self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _show_to_time(self, show=True):
        self.lbl_to.Show(show)
        self.dtp_end.Show(show)

    def _fill_controls_with_data(self, start=None, end=None):
        """Initially fill the controls in the dialog with data."""
        if self.event == None:
            self.chb_period.SetValue(False)
            self.chb_show_time.SetValue(False)
            text = ""
            category = None
            self.updatemode = False
        else:
            start = self.event.time_period.start_time
            end = self.event.time_period.end_time
            text = self.event.text
            category = self.event.category
            for plugin, editor in self.event_data_plugins:
                data = self.event.get_data(plugin.get_id())
                if data != None:
                    plugin.set_editor_data(editor, data)
            self.updatemode = True
        if start != None and end != None:
            self.chb_show_time.SetValue(has_nonzero_time(start, end))
            self.chb_period.SetValue(start != end)
        self.dtp_start.set_value(start)
        self.dtp_end.set_value(end)
        self.txt_text.SetValue(text)
        self._update_categories(category)
        self.chb_add_more.SetValue(False)
        self._show_to_time(self.chb_period.IsChecked())
        self.dtp_start.show_time(self.chb_show_time.IsChecked())
        self.dtp_end.show_time(self.chb_show_time.IsChecked())

    def _update_categories(self, select_category):
        # We can not do error handling here since this method is also called
        # from the constructor (and then error handling is done by the code
        # calling the constructor).
        self.lst_category.Clear()
        self.lst_category.Append("", None) # The None-category
        selection_set = False
        current_item_index = 1
        for cat in sort_categories(self.timeline.get_categories()):
            self.lst_category.Append(cat.name, cat)
            if cat == select_category:
                self.lst_category.SetSelection(current_item_index)
                selection_set = True
            current_item_index += 1
        self.last_real_category_index = current_item_index - 1
        self.add_category_item_index = self.last_real_category_index + 2
        self.edit_categoris_item_index = self.last_real_category_index + 3
        self.lst_category.Append("", None)
        self.lst_category.Append("Add new", None)
        self.lst_category.Append("Edit categories", None)
        if not selection_set:
            self.lst_category.SetSelection(0)
        self.current_category_selection = self.lst_category.GetSelection()

    def _set_initial_focus(self):
        self.dtp_start.SetFocus()

    def _close(self):
        """
        Close the dialog.

        Make sure that no events are selected after the dialog is closed.
        """
        self.timeline.reset_selected_events()
        self.EndModal(wx.ID_OK)


class CategoriesEditor(wx.Dialog):
    """
    Dialog used to edit categories of a timeline.

    The edits happen immediately. In other words: when the dialog is closing
    all edits have been applied already.
    """

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title="Edit Categories")
        self._create_gui()
        self.timeline = timeline
        # Note: We must unregister before we close this dialog. When we close
        # this dialog it will be disposed and self._timeline_changed will no
        # longer exist. The next time the timeline gets updated it will try to
        # call a method that does not exist.
        self.timeline.register(self._timeline_changed)
        self._update_categories()

    def _create_gui(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        # The list box
        self.lst_categories = wx.ListBox(self, size=(200, 180),
                                         style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self._lst_categories_on_dclick,
                  self.lst_categories)
        # The Add button
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        # The Delete button
        btn_del = wx.Button(self, wx.ID_DELETE)
        self.Bind(wx.EVT_BUTTON, self._btn_del_on_click, btn_del)
        # The close button
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        self.lst_categories.Bind(wx.EVT_KEY_DOWN, self._lst_categories_on_key_down)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.lst_categories, flag=wx.ALL|wx.EXPAND, border=BORDER)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(btn_add, flag=wx.RIGHT, border=BORDER)
        button_box.Add(btn_del, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        self.lst_categories.SetFocus()

    def _window_on_close(self, e):
        # This will always be called before the dialog closes so we can do the
        # unregister here.
        self.timeline.unregister(self._timeline_changed)
        self.EndModal(wx.ID_CLOSE)

    def _lst_categories_on_dclick(self, e):
        try:
            selection = e.GetSelection()
            dialog = CategoryEditor(self, "Edit Category", self.timeline,
                                    e.GetClientData())
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _btn_add_on_click(self, e):
        try:
            dialog = CategoryEditor(self, "Add Category", self.timeline,
                                    None)
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)
        else:
            if dialog.ShowModal() == ID_ERROR:
                self.error = dialog.error
                self.EndModal(ID_ERROR)
            dialog.Destroy()

    def _btn_del_on_click(self, e):
        try:
            self._delete_selected_category()
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _btn_close_on_click(self, e):
        self.Close()

    def _lst_categories_on_key_down(self, e):
        try:
            logging.debug("Key down event in CategoriesEditor")
            keycode = e.GetKeyCode()
            if keycode == wx.WXK_DELETE:
                self._delete_selected_category()
            e.Skip()
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _timeline_changed(self, state_change):
        try:
            if state_change == Timeline.STATE_CHANGE_CATEGORY:
                self._update_categories()
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _delete_selected_category(self):
        selection = self.lst_categories.GetSelection()
        if selection != wx.NOT_FOUND:
            if _ask_question("Are you sure to delete?", self) == wx.YES:
                cat = self.lst_categories.GetClientData(selection)
                self.timeline.delete_category(cat)

    def _update_categories(self):
        self.lst_categories.Clear()
        for category in sort_categories(self.timeline.get_categories()):
            self.lst_categories.Append(category.name, category)


class CategoryEditor(wx.Dialog):
    """
    Dialog used to edit a category.

    The edited category can be fetched with get_edited_category.
    """

    def __init__(self, parent, title, timeline, category):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()
        self.timeline = timeline
        self.category = category
        self.create_new = False
        if self.category == None:
            self.create_new = True
            self.category = Category("", (200, 200, 200), True)
        self.txt_name.SetValue(self.category.name)
        self.colorpicker.SetColour(self.category.color)
        self.chb_visible.SetValue(self.category.visible)

    def get_edited_category(self):
        return self.category

    def _create_gui(self):
        # The name text box
        self.txt_name = wx.TextCtrl(self, size=(150, -1))
        # The color chooser
        self.colorpicker = colourselect.ColourSelect(self)
        # The visible check box
        self.chb_visible = wx.CheckBox(self)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        # Grid for controls
        field_grid = wx.FlexGridSizer(rows=3, cols=2, vgap=BORDER, hgap=BORDER)
        field_grid.Add(wx.StaticText(self, label="Name:"),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.txt_name)
        field_grid.Add(wx.StaticText(self, label="Color:"),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.colorpicker)
        field_grid.Add(wx.StaticText(self, label="Visible:"),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.chb_visible)
        vbox.Add(field_grid, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        _set_focus_and_select(self.txt_name)

    def _btn_ok_on_click(self, e):
        try:
            name = self.txt_name.GetValue().strip()
            if not self._name_valid(name):
                msg = "Category name '%s' not valid. Must be non-empty."
                _display_error_message(msg % name, self)
                return
            if self._name_in_use(name):
                msg = "Category name '%s' already in use."
                _display_error_message(msg % name, self)
                return
            self.category.name = name
            self.category.color = self.colorpicker.GetColour()
            self.category.visible = self.chb_visible.IsChecked()
            if self.create_new:
                self.timeline.add_category(self.category)
            else:
                self.timeline.category_edited(self.category)
            self.EndModal(wx.ID_OK)
        except TimelineIOError as e:
            _display_error_message(e.message, self)
            self.error = e
            self.EndModal(ID_ERROR)

    def _name_valid(self, name):
        return len(name) > 0

    def _name_in_use(self, name):
        for cat in self.timeline.get_categories():
            if cat != self.category and cat.name == name:
                return True
        return False


class GotoDateDialog(wx.Dialog):

    def __init__(self, parent, time):
        wx.Dialog.__init__(self, parent, title=_(u"Atteindre une date"))
        self._create_gui()
        self.dtpc.set_value(time)

    def _create_gui(self):
        self.dtpc = DateTimePicker(self)
        checkbox = wx.CheckBox(self, label=_(u"Afficher l'heure"))
        checkbox.SetValue(False)
        self.dtpc.show_time(checkbox.IsChecked())
        self.Bind(wx.EVT_CHECKBOX, self._chb_show_time_on_checkbox, checkbox)
        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(checkbox, flag=wx.LEFT|wx.TOP|wx.RIGHT,
                 border=BORDER, proportion=1)
        vbox.Add(self.dtpc, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM|wx.LEFT,
                 border=BORDER, proportion=1)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)

    def _chb_show_time_on_checkbox(self, e):
        self.dtpc.show_time(e.IsChecked())

    def _btn_ok_on_click(self, e):
        self.time = self.dtpc.get_value()
        self.EndModal(wx.ID_OK)


class DateTimePicker(wx.Panel):
    """
    Control to pick a Python datetime object.

    The time part will default to 00:00:00 if none is entered.
    """

    def __init__(self, parent, show_time=True):
        wx.Panel.__init__(self, parent)
        self._create_gui()
        self.show_time(show_time)

    def show_time(self, show=True):
        self.time_picker.Show(show)
        self.GetSizer().Layout()

    def get_value(self):
        """Return the selected date time as a Python datetime object."""
        date = self.date_picker.GetValue()
        if 'phoenix' in wx.PlatformInfo:
            date_time = dt(date.year, date.month+1, date.day)
        else:
            date_time = dt(date.Year, date.Month+1, date.Day)
        if self.time_picker.IsShown():
            time = self.time_picker.GetValue(as_wxDateTime=True)
            date_time = date_time.replace(hour=time.Hour, minute=time.Minute)
        return date_time

    def set_value(self, value):
        if value == None:
            now = dt.now()
            value = dt(now.year, now.month, now.day)
        wx_date_time = self._python_date_to_wx_date(value)
        self.date_picker.SetValue(wx_date_time)
        self.time_picker.SetValue(wx_date_time)

    def _create_gui(self):
        self.date_picker = GenericDatePickerCtrl(self, style=DP_DROPDOWN|DP_SHOWCENTURY)
        self.Bind(EVT_DATE_CHANGED, self._date_picker_on_date_changed, self.date_picker)
        self.time_picker = TimeCtrl(self, format="24HHMM")
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.date_picker, proportion=1,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.time_picker, proportion=0,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)

    def _date_picker_on_date_changed(self, e):
        date = self.get_value()
        if date < TimePeriod.MIN_TIME:
            self.set_value(TimePeriod.MIN_TIME)
        if date > TimePeriod.MAX_TIME:
            self.set_value(TimePeriod.MAX_TIME)

    def _python_date_to_wx_date(self, py_date):
        if 'phoenix' in wx.PlatformInfo:
            return wx.DateTime.FromDMY(py_date.day, py_date.month-1, py_date.year, py_date.hour, py_date.minute, py_date.second)
        else:
            return wx.DateTimeFromDMY(py_date.day, py_date.month-1, py_date.year, py_date.hour, py_date.minute, py_date.second)


class HyperlinkButton(HL.HyperLinkCtrl):
    def __init__(self, parent, label, url=""):
        HL.HyperLinkCtrl.__init__(self, parent, wx.ID_ANY, label=label,
                                  url=url,
                                  style=wx.HL_ALIGN_CENTRE|wx.NO_BORDER)
        self.SetVisitedColour(self.GetNormalColour())


class TxtException(ValueError):
    """
    Thrown if a text control contains an invalid value.

    The constructor takes two arguments.

    The first is a text string containing any exception text.
    The seocond is a TextCtrl object.
    """
    def __init__(self, error_message, control):
        ValueError.__init__(self, error_message)
        self.error_message = error_message
        self.control = control


def sort_categories(categories):
    sorted_categories = list(categories)
    if six.PY2:
        sorted_categories.sort(cmp, lambda x: x.name.lower())
    else:
        sorted_categories.sort(key=(lambda x: x.name.lower()))

    return sorted_categories


def _set_focus_and_select(ctrl):
    ctrl.SetFocus()
    if hasattr(ctrl, "SelectAll"):
        ctrl.SelectAll()


def _parse_text_from_textbox(txt, name):
    """
    Return a text control field.

    If the value is an empty string the method raises a ValueError
    exception and sets focus on the control.

    If the value is valid the text in the control is returned
    """
    data = txt.GetValue().strip()
    if len(data) == 0:
        raise TxtException("Field '%s' can't be empty." % name, txt)
    return data


def _display_error_message(message, parent=None):
    """Display an error message in a modal dialog box"""
    dial = wx.MessageDialog(parent, message, "Error", wx.OK | wx.ICON_ERROR)
    dial.ShowModal()


def _ask_question(question, parent=None):
    """Ask a yes/no question and return the reply."""
    return wx.MessageBox(question, _(u"Question"),
                         wx.YES_NO|wx.CENTRE|wx.NO_DEFAULT, parent)


def _step_function(x_value):
    """
    A step function.

            {-1   when x < 0
    F(x) =  { 0   when x = 0
            { 1   when x > 0
    """
    y_value = 0
    if x_value < 0:
        y_value = -1
    elif x_value > 0:
        y_value = 1
    return y_value


def _create_wildcard(text, extensions):
    """
    Create wildcard for use in open/save dialogs.
    """
    return "%s (%s)|%s" % (text,
                           ", ".join(["*." + e for e in extensions]),
                           ";".join(["*." + e for e in extensions]))


def _extend_path(path, valid_extensions, default_extension):
    """Return tuple (path, extension) ensuring that path has extension."""
    for extension in valid_extensions:
        if path.endswith("." + extension):
            return (path, extension)
    return (path + "." + default_extension, default_extension)


def _create_button_box(parent, ok_method, cancel_method=None):
    """
    Convenience method for creating a button box control.

    The control contains one OK button and one Cancel or Close button.
    """
    button_box = wx.StdDialogButtonSizer()
    btn_ok = wx.Button(parent, wx.ID_OK)
    btn_cancel = wx.Button(parent, wx.ID_CANCEL)
    btn_ok.SetDefault()
    button_box.SetCancelButton(btn_cancel)
    button_box.SetAffirmativeButton(btn_ok)
    button_box.Realize()
    parent.Bind(wx.EVT_BUTTON, ok_method, btn_ok)
    if cancel_method != None:
        parent.Bind(wx.EVT_BUTTON, cancel_method, id=wx.ID_CANCEL)
        parent.Bind(wx.EVT_BUTTON, cancel_method, btn_cancel)
    parent.SetEscapeId(btn_cancel.GetId())
    parent.SetDefaultItem(btn_ok)
    parent.SetAffirmativeId(btn_ok.GetId())
    return button_box

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl_timeline = CTRL(panel, afficheSidebar=True)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_timeline, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        
        self.ctrl_timeline.MAJ()
    

    def create_new_event(self, start=None, end=None):
        dialog = EventEditor(self, u"Create Event", self.timeline, start, end)
        dialog.ShowModal() 
        dialog.Destroy()

    def edit_event(self, event):
        dialog = EventEditor(self, _(u"Edit Event"), self.timeline, event=event)
        dialog.ShowModal() 
        dialog.Destroy()


if __name__ == '__main__':
    # Logging
    logger = logging.getLogger()
##    logger.setLevel(logging.DEBUG)
    app = wx.App(0)
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()