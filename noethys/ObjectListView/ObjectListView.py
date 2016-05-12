# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         ObjectListView.py
# Author:       Phillip Piper
# Created:      29 February 2008
# Copyright:    (c) 2008 Phillip Piper
# SVN-ID:       $Id$
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/09/02  JPP   - Added BatchedUpdate adaptor
#                   - Improved speed of selecting and refreshing by keeping a map
#                     of objects to indicies
#                   - Added GetIndexOf()
#                   - Removed flicker from FastObjectListView.AddObjects() and RefreshObjects()
# 2008/08/27  JPP   - Implemented filtering
#                   - Added GetObjects() and GetFilteredObjects()
#                   - Added resortNow parameter to SetSortColumn()
# 2008/08/23  JPP   - Added AddObjects()/RemoveObjects() and friends
#                   - Removed duplicate code when building/refreshing/adding objects
#                   - One step closer to secondary sort column support
# 2008/08/18  JPP   - Handle model objects that cannot be hashed
#                   - Added CELL_EDIT_STARTED and CELL_EDIT_FINISHED events
# 2008/08/16  JPP   - Added ensureVisible parameter to SelectObject()
# 2008/08/05  JPP   - GroupListView is now implemented as a virtual list. Much faster!
# v1.1
# 2008/07/19  JPP   - Added GroupListView
#                   - Broke common virtual list behaviour into AbstractVirtualListView
# 2008/07/13  JPP   - Added CopySelectionToClipboard and CopyObjectsToClipboard
# 2008/07/08  JPP   - Fixed several Linux specific bugs/limits
# 2008/07/03  JPP   - Allow headers to have images
# v1.0.1
# 2008/06/22  JPP   - Allowed for custom sorting, even on virtual lists
#                   - Fixed bug where an imageGetter that returned 0 was treated
#                     as if it returned -1 (i.e. no image)
# 2008/06/17  JPP   - Use binary searches when searching on sorted columns
# 2008/06/16  JPP   - Search by sorted column works, even on virtual lists
# 2008/06/12  JPP   - Added sortable parameter
#                   - Renamed sortColumn to be sortColumnIndex to make it clear
#                   - Allow returns in multiline cell editors
# v1.0
# 2008/05/29  JPP   Used named images internally
# 2008/05/26  JPP   Fixed pyLint annoyances
# 2008/05/24  JPP   Images can be referenced by name
# 2008/05/17  JPP   Checkboxes supported
# 2008/04/18  JPP   Cell editing complete
# 2008/03/31  JPP   Added space filling columns
# 2008/03/29  JPP   Added minimum, maximum and fixed widths for columns
# 2008/03/22  JPP   Added VirtualObjectListView and FastObjectListView
# 2008/02/29  JPP   Version converted from wax
# 2006/11/03  JPP   First version under wax
#----------------------------------------------------------------------------
# To do:
# - selectable columns, triggered on right click on header
# - secondary sort column
# - optionally preserve selection on RepopulateList
# - get rid of scrollbar when editing label in icon view
# - need a ChangeView() method to help when switching between views

"""
An `ObjectListView` provides a more convienent and powerful interface to a ListCtrl.

The major features of an `ObjectListView` are:

    * Automatically transforms a collection of model objects into a ListCtrl.
    * Automatically sorts rows by their data type.
    * Easily edits the values shown in the ListCtrl.
    * Supports all ListCtrl views (report, list, large and small icons).
    * Columns can be fixed-width, have a minimum and/or maximum width, or be space-filling.
    * Displays a "list is empty" message when the list is empty (obviously).
    * Supports custom formatting of rows
    * Supports alternate rows background colors.
    * Supports checkbox columns
    * Supports searching (by typing) on the sorted column -- even on virtual lists.
    * Supports filtering of rows
    * The `FastObjectListView` version can build a list of 10,000 objects in less than 0.1 seconds.
    * The `VirtualObjectListView` version supports millions of rows through ListCtrl's virtual mode.
    * The `GroupListView` version partitions it's rows into collapsible groups.

An `ObjectListView` works in a declarative manner: the programmer configures how it should
work, then gives it the list of objects to display. The primary configuration is in the
definitions of the columns. Columns are configured to know which aspect of their model
they should display, how it should be formatted, and even how new values should be written
back into the model. See `ColumnDefn` for more information.

"""

__author__ = "Phillip Piper"
__date__ = "18 June 2008"
__version__ = "1.1"

import Chemins

import wx
import datetime
import itertools
import locale
import operator
import string
import time
import copy
import sys

import CellEditor
import OLVEvent
import Footer
import Filter

import sys
sys.path.append("..")

import UTILS_Dates



class ObjectListView(wx.ListCtrl):
    """
    An object list displays various aspects of a list of objects in a multi-column list control.

    To use an ObjectListView, the programmer defines what columns are in the control and which
    bits of information each column should display. The programmer then calls `SetObjects` with
    the list of objects that the ObjectListView should display. The ObjectListView then builds
    the control.

    Columns hold much of the intelligence of this control. Columns define both the format
    (width, alignment), the aspect to be shown in the column, and the columns behaviour.
    See `ColumnDefn` for full details.

    These are public instance variables. (All other variables should be considered private.)

    * cellEditMode
        This control whether and how the cells of the control are editable. It can be
        set to one of the following values:

        CELLEDIT_NONE
           Cell editing is not allowed on the control This is the default.

        CELLEDIT_SINGLECLICK
           Single clicking on any subitem cell begins an edit operation on that cell.
           Single clicking on the primaru cell does *not* start an edit operation.
           It simply selects the row. Pressing F2 edits the primary cell.

        CELLEDIT_DOUBLECLICK
           Double clicking any cell starts an edit operation on that cell, including
           the primary cell. Pressing F2 edits the primary cell.

        CELLEDIT_F2ONLY
           Pressing F2 edits the primary cell. Tab/Shift-Tab can be used to edit other
           cells. Clicking does not start any editing.

    * evenRowsBackColor
        When `useAlternateBackColors` is true, even numbered rows will have this
        background color.

    * handleStandardKeys
        When this is True (the default), several standard keys will be handled as
        commands by the ObjectListView. If this is False, they will be ignored.

        Ctrl-A
            Select all model objects

        Ctrl-C
            Put a text version of the selected rows onto the clipboard (on Windows,
            this is will also put a HTML version into the clipboard)

        Left-Arrow, Right-Arrow
            [GroupListView only] This will collapse/expand all selected groups.

    * oddRowsBackColor
        When `useAlternateBackColors` is true, odd numbered rows will have this
        background color.

    * rowFormatter
        To further control the formatting of individual rows, this property
        can be set to a callable that expects two parameters: the listitem whose
        characteristics are to be set, and the model object being displayed on that row.

        The row formatter is called after the alternate back colours (if any) have been
        set.

        Remember: the background and text colours are overridden by system defaults
        while a row is selected.

    * typingSearchesSortColumn
        If this boolean is True (the default), when the user types into the list, the
        control will try to find a prefix match on the values in the sort column. If this
        is False, or the list is unsorted or if the sorted column is marked as not
        searchable (via `isSearchable` attribute), the primary column will be matched.

    * useAlternateBackColors
        If this property is true, even and odd rows will be given different
        background. The background colors are controlled by the properties
        `evenRowsBackColor` and `oddRowsBackColor`. This is true by default.
    """

    CELLEDIT_NONE = 0
    CELLEDIT_SINGLECLICK = 1
    CELLEDIT_DOUBLECLICK = 2
    CELLEDIT_F2ONLY = 3

    """Names of standard images used within the ObjectListView. If you want to use your
    own image in place of a standard one, simple register it with AddNamedImages() using
    one of the following names."""
    NAME_DOWN_IMAGE = "objectListView.downImage"
    NAME_UP_IMAGE = "objectListView.upImage"
    NAME_CHECKED_IMAGE = "objectListView.checkedImage"
    NAME_UNCHECKED_IMAGE = "objectListView.uncheckedImage"
    NAME_UNDETERMINED_IMAGE = "objectListView.undeterminedImage"
    NAME_EXPANDED_IMAGE = "objectListView.expandedImage"
    NAME_COLLAPSED_IMAGE = "objectListView.collapsedImage"

    """When typing into the list, a delay between keystrokes greater than this (in seconds)
    will be interpretted as a new search and any previous search text will be cleared"""
    SEARCH_KEYSTROKE_DELAY = 0.75

    """When typing into a list and searching on an unsorted column, we don't even try to search
    if there are more than this many rows."""
    MAX_ROWS_FOR_UNSORTED_SEARCH = 100000

    def __init__(self, *args, **kwargs):
        """
        Create an ObjectListView.

        Apart from the normal ListCtrl parameters, this constructor looks for any of the
        following optional parameters:

            * `cellEditMode`
            * `rowFormatter`
            * `sortable`
            * `useAlternateBackColors`

        The behaviour of these properties are described in the class documentation, except
        for `sortable.`

        `sortable` controls whether the rows of the control will be sorted when the user
        clicks on the header. This is true by default. If it is False, clicking the header
        will be nothing, and no images will be registered in the image lists. This
        parameter only has effect at creation time -- it has no impact after creation.

        """

        # We have two collections of objects: our model objects and our working list
        # ("innerList"). The model objects are those given to use by the user; the working
        # list is what is actually used to populate the control. This separation let us
        # modify what is presented to the user without losing our base data. This allows
        # to (in the future) implement filtering or some other view-like capabilities.
        # Currently, for ObjectListView, these collections will be identical, but for a
        # GroupListView they are different.
        self.modelObjects = []
        self.innerList = []
        self.columns = []
        self.sortColumnIndex = -1
        self.sortAscending = True
        self.smallImageList = None
        self.normalImageList = None
        self.cellEditor = None
        self.cellBeingEdited = None
        self.selectionBeforeCellEdit = []
        self.checkStateColumn = None
        self.handleStandardKeys = True
        self.searchPrefix = u""
        self.whenLastTypingEvent = 0
        self.filter = None
        self.objectToIndexMap = None
        
        self.listeColonnes = [] 
        self.listeFiltresColonnes = []
        self.nomListe = None
        self.ctrl_footer = None
        self.barreRecherche = None

        self.rowFormatter = kwargs.pop("rowFormatter", None)
        self.useAlternateBackColors = kwargs.pop("useAlternateBackColors", True)
        self.sortable = kwargs.pop("sortable", True)
        self.cellEditMode = kwargs.pop("cellEditMode", self.CELLEDIT_NONE)
        self.typingSearchesSortColumn = kwargs.pop("typingSearchesSortColumn", True)

        self.evenRowsBackColor = wx.Colour(240, 248, 255) # ALICE BLUE
        self.oddRowsBackColor = wx.Colour(255, 250, 205) # LEMON CHIFFON
        
        wx.ListCtrl.__init__(self, *args, **kwargs)

        if self.sortable:
            self.EnableSorting()

        # NOTE: On Windows, ListCtrl's don't trigger EVT_LEFT_UP :(

        self.Bind(wx.EVT_CHAR, self._HandleChar)
        self.Bind(wx.EVT_LEFT_DOWN, self._HandleLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self._HandleLeftClickOrDoubleClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self._HandleLeftClickOrDoubleClick)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self._HandleColumnBeginDrag)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self._HandleColumnEndDrag)
        self.Bind(wx.EVT_MOUSEWHEEL, self._HandleMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self._HandleScroll)
        self.Bind(wx.EVT_SIZE, self._HandleSize)

        self.Bind(wx.EVT_LIST_COL_DRAGGING, self._HandleColumnDragging)
        self.Bind(wx.EVT_SCROLL, self.OnScroll)

        # For some reason under Linux, the default wx.StaticText always appears
        # behind the ListCtrl. The GenStaticText class appears as it should.
        if wx.Platform == "__WXGTK__":
            from wx.lib.stattext import GenStaticText as StaticText
        else:
            StaticText = wx.StaticText

        self.stEmptyListMsg = StaticText(self, -1, "This list is empty",
            wx.Point(0, 0), wx.Size(0, 0), wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE | wx.FULL_REPAINT_ON_RESIZE)
        self.stEmptyListMsg.Hide()
        self.stEmptyListMsg.SetForegroundColour(wx.LIGHT_GREY)
        self.couleurBackgroundDefaut = self.stEmptyListMsg.GetBackgroundColour()
        self.stEmptyListMsg.SetBackgroundColour(self.GetBackgroundColour())
        self.stEmptyListMsg.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
    
    def Activation(self, etat=True):
        """ Active ou desactive l'etat du controle """
        if etat == True :
            self.Enable(True)
            self.stEmptyListMsg.SetBackgroundColour(self.GetBackgroundColour())
        else :
            self.Enable(False)
            self.stEmptyListMsg.SetBackgroundColour(self.couleurBackgroundDefaut)
        self.stEmptyListMsg.Refresh() 
        
    #--------------------------------------------------------------#000000#FFFFFF
    # Setup

    def SetColumns(self, columns, repopulate=True):
        """
        Set the list of columns that will be displayed.

        The elements of the list can be either ColumnDefn objects or a tuple holding the values
        to be given to the ColumnDefn constructor.

        The first column is the primary column -- this will be shown in the the non-report views.

        This clears any preexisting CheckStateColumn. The first column that is a check state
        column will be installed as the CheckStateColumn for this listview.
        """
        self.listeColonnes = columns
        sortCol = self.GetSortColumn()
        wx.ListCtrl.ClearAll(self)
        self.checkStateColumn = None
        self.columns = []
        for x in columns:
            if x.visible == True :
                if isinstance(x, ColumnDefn):
                    self.AddColumnDefn(x)
                else:
                    self.AddColumnDefn(ColumnDefn(*x))
        # Try to preserve the column column
        self.SetSortColumn(sortCol)
        if repopulate:
            self.RepopulateList()


    def AddColumnDefn(self, defn):
        """
        Append the given ColumnDefn object to our list of active columns.

        If this method is called directly, you must also call RepopulateList()
        to populate the new column with data.
        """
        self.columns.append(defn)

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT
        if isinstance(defn.headerImage, basestring) and self.smallImageList is not None:
            info.m_image = self.smallImageList.GetImageIndex(defn.headerImage)
        else:
            info.m_image = defn.headerImage
        if info.m_image != -1:
            info.m_mask = info.m_mask | wx.LIST_MASK_IMAGE
        info.m_format = defn.GetAlignment()
        info.m_text = defn.title
        info.m_width = defn.width
        self.InsertColumnInfo(len(self.columns)-1, info)

        # Under Linux, the width doesn't take effect without this call
        self.SetColumnWidth(len(self.columns)-1, defn.width)

        # The first checkbox column becomes the check state column for the control
        if defn.HasCheckState() and self.checkStateColumn is None:
            self.InstallCheckStateColumn(defn)


    def _InitializeCheckBoxImages(self):
        """
        Initialize some checkbox images for use by this control.
        """
        def _makeBitmap(state, size):
            bitmap = wx.EmptyBitmap(size, size)
            dc = wx.MemoryDC(bitmap)
            dc.Clear()

            # On Linux, the Renderer draws the checkbox too low
            if wx.Platform == "__WXGTK__":
                yOrigin = -1
            else:
                yOrigin = 0
            wx.RendererNative.Get().DrawCheckBox(self, dc, (0, yOrigin, size, size), state)
            dc.SelectObject(wx.NullBitmap)
            return bitmap

        def _makeBitmaps(name, state):
            self.AddNamedImages(name, _makeBitmap(state, 16), _makeBitmap(state, 32))

        # If there isn't a small image list, make one
        if self.smallImageList is None:
            self.SetImageLists()

        _makeBitmaps(ObjectListView.NAME_CHECKED_IMAGE, wx.CONTROL_CHECKED)
        _makeBitmaps(ObjectListView.NAME_UNCHECKED_IMAGE, wx.CONTROL_CURRENT)
        _makeBitmaps(ObjectListView.NAME_UNDETERMINED_IMAGE, wx.CONTROL_UNDETERMINED)


    def CreateCheckStateColumn(self, columnIndex=0):
        """
        Create a fixed width column at the given index to show the checkedness
        of objects in this list.

        If this is installed at column 0 (which is the default), the listview
        should only be used in Report view.

        This should be called after SetColumns() has been called, since
        SetColumns() removed any previous check state column.

        RepopulateList() or SetObjects() must be called after this.
        """
        col = ColumnDefn("", fixedWidth=24, isEditable=False)
        col.valueGetter = col.GetCheckState # Install a value getter so sorting works
        col.stringConverter = lambda x: "" # We don't want any string for the value
        col.isInternal = True # This is an autocreated column
        self.columns.insert(columnIndex, col)
        self.SetColumns(self.columns, False)
        self.InstallCheckStateColumn(col)


    def InstallCheckStateColumn(self, column):
        """
        Configure the given column so that it shows the check state of each row in this
        control.

        This column's checkbox will be toggled when the user pressed space when a row is
        selected.

        `RepopulateList()` or `SetObjects()` must be called after a new check state column is
        installed for the check state column to be visible.

        Set to None to remove the check state column.
        """
        self.checkStateColumn = column
        if column is None:
            return

        if self.smallImageList == None or \
           not self.smallImageList.HasName(ObjectListView.NAME_CHECKED_IMAGE):
            self._InitializeCheckBoxImages()

        # Is the column already configured to handle check state?
        if column.HasCheckState():
            return

        # The column isn't managing it's own check state, so install handlers
        # that will manage the state. This is useful when the checkedness is
        # related to the view and is not an attribute of the model.
        checkState = dict()
        def _handleGetCheckState(modelObject):
            return checkState.get(modelObject, False) # objects are not checked by default

        def _handleSetCheckState(modelObject, newValue):
            checkState[modelObject] = newValue
            return newValue

        column.checkStateGetter = _handleGetCheckState
        column.checkStateSetter = _handleSetCheckState


    def RegisterSortIndicators(self, sortUp=None, sortDown=None):
        """
        Register the bitmaps that should be used to indicated which column is being sorted
        These bitmaps must be the same dimensions as the small image list (not sure
        why that should be so, but it is)

        If no parameters are given, 16x16 default images will be registered
        """
        self.AddNamedImages(ObjectListView.NAME_DOWN_IMAGE, sortDown or _getSmallDownArrowBitmap())
        self.AddNamedImages(ObjectListView.NAME_UP_IMAGE, sortUp or _getSmallUpArrowBitmap())


    def SetImageLists(self, smallImageList=None, normalImageList=None):
        """
        Remember the image lists to be used for this control.

        Call this without parameters to create reasonable default image lists.

        Use this to change the size of images shown by the list control.
        """
        if isinstance(smallImageList, NamedImageList):
            self.smallImageList = smallImageList
        else:
            self.smallImageList = NamedImageList(smallImageList, 16)
        self.SetImageList(self.smallImageList.imageList, wx.IMAGE_LIST_SMALL)

        if isinstance(normalImageList, NamedImageList):
            self.normalImageList = normalImageList
        else:
            self.normalImageList = NamedImageList(normalImageList, 32)
        self.SetImageList(self.normalImageList.imageList, wx.IMAGE_LIST_NORMAL)


    #--------------------------------------------------------------#000000#FFFFFF
    # Commands

    def AddImages(self, smallImage=None, normalImage=None):
        """
        Add the given images to the list of available images. Return the index of the image.
        """
        return self.AddNamedImages(None, smallImage, normalImage)


    def AddObject(self, modelObject):
        """
        Add the given object to our collection of objects.

        The object will appear at its sorted location, or at the end of the list if
        the list is unsorted
        """
        self.AddObjects([modelObject])


    def AddObjects(self, modelObjects):
        """
        Add the given collections of objects to our collection of objects.

        The objects will appear at their sorted locations, or at the end of the list if
        the list is unsorted
        """
        if len(self.innerList) == 0:
            return self.SetObjects(modelObjects)

        try:
            self.Freeze()
            originalSize = len(self.innerList)
            self.modelObjects.extend(modelObjects)
            self._BuildInnerList()
            item = wx.ListItem()
            item.SetColumn(0)
            for (i, x) in enumerate(self.innerList[originalSize:]):
                item.Clear()
                self._InsertUpdateItem(item, originalSize+i, x, True)
            self._SortItemsNow()
        finally:
            self.Thaw()

        # MAJ Footer
        if self.ctrl_footer :
            self.MAJ_footer()


    def AddNamedImages(self, name, smallImage=None, normalImage=None):
        """
        Add the given images to the list of available images. Return the index of the image.

        If a name is given, that name can later be used to refer to the images rather
        than having to use the returned index.
        """
        if isinstance(smallImage, basestring):
            smallImage = wx.Bitmap(smallImage)
        if isinstance(normalImage, basestring):
            normalImage = wx.Bitmap(normalImage)

        # We must have image lists for images to be added to them
        if self.smallImageList is None or self.normalImageList is None:
            self.SetImageLists()

        # There must always be the same number of small and normal bitmaps,
        # so if we aren't given one, we have to make an empty one of the right size
        smallImage = smallImage or wx.EmptyBitmap(*self.smallImageList.GetSize(0))
        normalImage = normalImage or wx.EmptyBitmap(*self.normalImageList.GetSize(0))

        self.smallImageList.AddNamedImage(name, smallImage)
        return self.normalImageList.AddNamedImage(name, normalImage)


    def AutoSizeColumns(self):
        """
        Resize our auto sizing columns to match the data
        """
        for (iCol, col) in enumerate(self.columns):
            if col.width == wx.LIST_AUTOSIZE:
                self.SetColumnWidth(iCol, wx.LIST_AUTOSIZE)

                # The new width must be within our minimum and maximum
                colWidth = self.GetColumnWidth(iCol)
                boundedWidth = col.CalcBoundedWidth(colWidth)
                if colWidth != boundedWidth:
                    self.SetColumnWidth(iCol, boundedWidth)


    def Check(self, modelObject):
        """
        Mark the given model object as checked.
        """
        self.SetCheckState(modelObject, True)


    def ClearAll(self):
        """
        Remove all items and columns
        """
        wx.ListCtrl.ClearAll(self)
        self.SetObjects(list())


    def CopyObjectsToClipboard(self, objects):
        """
        Put a textual representation of the given objects onto the clipboard.

        This will be one line per object and tab-separated values per line.
        Under windows there will be a HTML table version put on the clipboard as well.
        """
        if objects is None or len(objects) == 0:
            return

        # Get all the values of the given rows into multi-list
        rows = self._GetValuesAsMultiList(objects)

        # Make a text version of the values
        lines = [ "\t".join(x) for x in rows ]
        txt = "\n".join(lines) + "\n"

        # Make a html version on Windows
        try:
            lines = [ "<td>" + "</td><td>".join(x) + "</td>" for x in rows ]
            html = "<table><tr>" + "</tr><tr>".join(lines) + "</tr></table>"
            self._PutTextAndHtmlToClipboard(txt, html)
        except ImportError:
            cb = wx.Clipboard()
            if cb.Open():
                cb.SetData(wx.TextDataObject(txt))
                cb.Flush()
                cb.Close()

    def _GetValuesAsMultiList(self, objects):
        """
        Return a list of lists of the string of the aspects of the given objects
        """
        cols = self.columns[:]
        if self.checkStateColumn is not None:
            cols.remove(self.checkStateColumn)
        return [[column.GetStringValue(x) for column in cols] for x in objects]


    def _PutTextAndHtmlToClipboard(self, txt, fragment):
        """
        Put the given text and html into the windows clipboard.

        The html will be written in accordance with strange "HTML Format" as specified
        in http://msdn.microsoft.com/library/en-us/winui/winui/windowsuserinterface/dataexchange/clipboard/htmlclipboardformat.asp
        """
        import win32clipboard

        MARKER_BLOCK_OUTPUT = \
            "Version:1.0\r\n" \
            "StartHTML:%09d\r\n" \
            "EndHTML:%09d\r\n" \
            "StartFragment:%09d\r\n" \
            "EndFragment:%09d\r\n" \
            "StartSelection:%09d\r\n" \
            "EndSelection:%09d\r\n" \
            "SourceURL:%s\r\n"

        DEFAULT_HTML_BODY = \
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">" \
            "<HTML><HEAD></HEAD><BODY><!--StartFragment-->%s<!--EndFragment--></BODY></HTML>"

        html = DEFAULT_HTML_BODY % fragment
        source = "http://objectlistview.sourceforge.net/python"

        fragmentStart = selectionStart = html.index(fragment)
        fragmentEnd = selectionEnd = fragmentStart + len(fragment)

        # How long is the prefix going to be?
        dummyPrefix = MARKER_BLOCK_OUTPUT % (0, 0, 0, 0, 0, 0, source)
        lenPrefix = len(dummyPrefix)

        prefix = MARKER_BLOCK_OUTPUT % (lenPrefix, len(html)+lenPrefix,
                        fragmentStart+lenPrefix, fragmentEnd+lenPrefix,
                        selectionStart+lenPrefix, selectionEnd+lenPrefix,
                        source)
        htmlForClipboard = (prefix + html)

        try:
            win32clipboard.OpenClipboard(0)
            win32clipboard.EmptyClipboard()
            cfText = 1
            win32clipboard.SetClipboardData(cfText, txt)
            cfHtml = win32clipboard.RegisterClipboardFormat("HTML Format")
            win32clipboard.SetClipboardData(cfHtml, htmlForClipboard)
        finally:
            win32clipboard.CloseClipboard()


    def CopySelectionToClipboard(self):
        """
        Copy the selected objects to the clipboard
        """
        self.CopyObjectsToClipboard(self.GetSelectedObjects())


    def DeleteAllItems(self):
        """
        Remove all items
        """
        wx.ListCtrl.DeleteAllItems(self)
        self.SetObjects(list())


    def EnsureCellVisible(self, rowIndex, subItemIndex):
        """
        Make sure the user can see all of the given cell, scrolling if necessary.
        Return the bounds to the cell calculated after the cell has been made visible.
        Return None if the cell cannot be made visible (non-Windows platforms can't scroll
        the listview horizontally)

        If the cell is bigger than the ListView, the top left of the cell will be visible.
        """
        self.EnsureVisible(rowIndex)
        bounds = self.GetSubItemRect(rowIndex, subItemIndex, wx.LIST_RECT_BOUNDS)
        boundsRight = bounds[0]+bounds[2]
        if bounds[0] < 0 or boundsRight > self.GetSize()[0]:
            if bounds[0] < 0:
                horizDelta = bounds[0] - (self.GetSize()[0] / 4)
            else:
                horizDelta = boundsRight - self.GetSize()[0] + (self.GetSize()[0] / 4)
            if wx.Platform == "__WXMSW__":
                self.ScrollList(horizDelta, 0)
            else:
                return None

        return self.GetSubItemRect(rowIndex, subItemIndex, wx.LIST_RECT_LABEL)


    def _FormatAllRows(self):
        """
        Set up the required formatting on all rows
        """
        for i in range(self.GetItemCount()):
            item = self.GetItem(i)
            self._FormatOneItem(item, i, self.GetObjectAt(i))
            self.SetItem(item)


    def _FormatOneItem(self, item, index, model):
        """
        Give the given row it's correct background color
        """
        if self.useAlternateBackColors and self.InReportView():
            if index & 1:
                item.SetBackgroundColour(self.oddRowsBackColor)
            else:
                item.SetBackgroundColour(self.evenRowsBackColor)

        if self.rowFormatter is not None:
            self.rowFormatter(item, model)


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        self._SortObjects()
        self._BuildInnerList()
        self.Freeze()
        try:
            wx.ListCtrl.DeleteAllItems(self)
            if len(self.innerList) == 0 or len(self.columns) == 0:
                self.Refresh()
                self.stEmptyListMsg.Show()
                return

            self.stEmptyListMsg.Hide()

            # Insert all the rows
            item = wx.ListItem()
            item.SetColumn(0)
            for (i, x) in enumerate(self.innerList):
                item.Clear()
                self._InsertUpdateItem(item, i, x, True)

            # Auto-resize once all the data has been added
            self.AutoSizeColumns()
        finally:
            self.Thaw()

        # MAJ Footer
        if self.ctrl_footer :
            self.MAJ_footer()

    def RefreshIndex(self, index, modelObject):
        """
        Refresh the item at the given index with data associated with the given object
        """
        self._InsertUpdateItem(self.GetItem(index), index, modelObject, False)


    def _InsertUpdateItem(self, listItem, index, modelObject, isInsert):
        if isInsert:
            listItem.SetId(index)
            listItem.SetData(index)

        listItem.SetText(self.GetStringValueAt(modelObject, 0))
        listItem.SetImage(self.GetImageAt(modelObject, 0))
        self._FormatOneItem(listItem, index, modelObject)

        if isInsert:
            self.InsertItem(listItem)
        else:
            self.SetItem(listItem)

        for iCol in range(1, len(self.columns)):
            self.SetStringItem(index, iCol, self.GetStringValueAt(modelObject, iCol),
                               self.GetImageAt(modelObject, iCol))


    def RefreshObject(self, modelObject):
        """
        Refresh the display of the given model
        """
        idx = self.GetIndexOf(modelObject)
        if idx != -1:
            self.RefreshIndex(self._MapModelIndexToListIndex(idx), modelObject)

        # MAJ Footer
        if self.ctrl_footer :
            self.MAJ_footer()


    def RefreshObjects(self, aList):
        """
        Refresh all the objects in the given list
        """
        try:
            self.Freeze()
            for x in aList:
                self.RefreshObject(x)
        finally:
            self.Thaw()


    def RemoveObject(self, modelObject):
        """
        Remove the given object from our collection of objects.
        """
        self.RemoveObjects([modelObject])


    def RemoveObjects(self, modelObjects):
        """
        Remove the given collections of objects from our collection of objects.
        """
        # Unlike AddObjects(), there is no clever way to do this -- we have to simply
        # remove the objects and rebuild the whole list. We can't just remove the rows
        # because every wxListItem holds the index of its matching model object. If we
        # remove the first model object, the index of every object will change.
        selection = self.GetSelectedObjects()

        # Use sets to quickly remove objects from self.modelObjects
        # For large collections, this is MUCH faster.
        try:
            s1 = set(self.modelObjects)
            s2 = set(modelObjects)
            self.modelObjects = list(s1 - s2)
        except TypeError:
            # Not every object can be hashed, so some model objects cannot be placed in sets.
            # For such objects, we have to resort to the slow method.
            for x in modelObjects:
                self.modelObjects.remove(x)

        self.RepopulateList()
        self.SelectObjects(selection)


    def _ResizeSpaceFillingColumns(self):
        """
        Change the width of space filling columns so that they fill the
        unoccupied width of the listview
        """
        # If the list isn't in report view or there are no space filling columns, just return
        if not self.InReportView():
            return

        # Don't do anything if there are no space filling columns
        if True not in set(x.isSpaceFilling for x in self.columns):
            return

        # Calculate how much free space is available in the control
        totalFixedWidth = sum(self.GetColumnWidth(i) for (i, x) in enumerate(self.columns)
                              if not x.isSpaceFilling)
        freeSpace = max(0, self.GetClientSizeTuple()[0] - totalFixedWidth)

        # Calculate the total number of slices the free space will be divided into
        totalProportion = sum(x.freeSpaceProportion for x in self.columns if x.isSpaceFilling)

        # Space filling columns that would escape their boundary conditions
        # are treated as fixed size columns
        columnsToResize = []
        for (i, col) in enumerate(self.columns):
            if col.isSpaceFilling:
                newWidth = freeSpace * col.freeSpaceProportion / totalProportion
                boundedWidth = col.CalcBoundedWidth(newWidth)
                if newWidth == boundedWidth:
                    columnsToResize.append((i, col))
                else:
                    freeSpace -= boundedWidth
                    totalProportion -= col.freeSpaceProportion
                    if self.GetColumnWidth(i) != boundedWidth:
                        self.SetColumnWidth(i, boundedWidth)

        # Finally, give each remaining space filling column a proportion of the free space
        for (i, col) in columnsToResize:
            newWidth = freeSpace * col.freeSpaceProportion / totalProportion
            boundedWidth = col.CalcBoundedWidth(newWidth)
            if self.GetColumnWidth(i) != boundedWidth:
                try :
                    self.SetColumnWidth(i, boundedWidth)
                except :
                    pass


    def SetCheckState(self, modelObject, state):
        """
        Set the check state of the given model object.

        'state' can be True, False or None (which means undetermined)
        """
        if self.checkStateColumn is None:
            return None
        else:
            return self.checkStateColumn.SetCheckState(modelObject, state)


    def SetColumnFixedWidth(self, colIndex, width):
        """
        Make the given column to be fixed width
        """
        if 0 <= colIndex < self.GetColumnCount():
            self.SetColumnWidth(colIndex, width)
            self.columns[colIndex].SetFixedWidth(width)


    def SetEmptyListMsg(self, msg):
        """
        When there are no objects in the list, show this message in the control
        """
        self.stEmptyListMsg.SetLabel(msg)


    def SetEmptyListMsgFont(self, font):
        """
        In what font should the empty list msg be rendered?
        """
        self.stEmptyListMsg.SetFont(font)


    def SetObjects(self, modelObjects, preserveSelection=False):
        """
        Set the list of modelObjects to be displayed by the control.
        """
        if preserveSelection:
            selection = self.GetSelectedObjects()

        if modelObjects is None:
            self.modelObjects = list()
        else:
            self.modelObjects = modelObjects[:]

        self.RepopulateList()

        if preserveSelection:
            self.SelectObjects(selection)
        
    # Synonym as per many wxWindows widgets
    SetValue = SetObjects


    def _BuildInnerList(self):
        """
        Build the list that will actually populate the control
        """
        # This is normally just the list of model objects
        if self.filter:
            self.innerList = self.filter(self.modelObjects)
        else:
            self.innerList = self.modelObjects

        # Our map isn't valid after doing this
        self.objectToIndexMap = None


    def ToggleCheck(self, modelObject):
        """
        Toggle the "checkedness" of the given model.

        Checked becomes unchecked; unchecked or undetermined becomes checked.
        """
        self.SetCheckState(modelObject, not self.IsChecked(modelObject))


    def Uncheck(self, modelObject):
        """
        Mark the given model object as unchecked.
        """
        self.SetCheckState(modelObject, False)

    #--------------------------------------------------------------#000000#FFFFFF
    # Accessing

    def GetCheckedObjects(self):
        """
        Return a collection of the modelObjects that are checked in this control.
        """
        if self.checkStateColumn is None:
            return list()
        else:
            return [x for x in self.innerList if self.IsChecked(x)]


    def GetCheckState(self, modelObject):
        """
        Return the check state of the given model object.

        Returns a boolean or None (which means undetermined)
        """
        if self.checkStateColumn is None:
            return None
        else:
            return self.checkStateColumn.GetCheckState(modelObject)


    def GetFilter(self):
        """
        Return the filter that is currently operating on this control.
        """
        return self.filter


    def GetFilteredObjects(self):
        """
        Return the model objects that are actually displayed in the control.

        If no filter is in effect, this is the same as GetObjects().
        """
        return self.innerList


    def GetFocusedRow(self):
        """
        Return the index of the row that has the focus. -1 means no focus
        """
        return self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_FOCUSED)


    def GetIndexOf(self, modelObject):
        """
        Return the index of the given modelObject in the list.

        This method works on the visible item in the control. If a filter
        is in place, not all model object given to SetObjects() are visible.
        """
        # Rebuild our index map if it has been invalidated. The TypeError
        # exceptions are for objects that cannot be hashed (like lists)
        if self.objectToIndexMap is None:
            self.objectToIndexMap = dict()
            for (i, x) in enumerate(self.innerList):
                try:
                    self.objectToIndexMap[x] = i
                except TypeError:
                    pass

        # Use our map to find the object (but fall back to simple search
        # for non-hashable objects)
        try:
            return self.objectToIndexMap.get(modelObject, -1)
        except TypeError:
            try:
                return self.innerList.index(modelObject)
            except ValueError:
                return -1


    def GetImageAt(self, modelObject, columnIndex):
        """
        Return the index of the image that should be display at the given column of the given modelObject
        """
        column = self.columns[columnIndex]

        # If the column is a checkbox column, return the image appropriate to the check
        # state
        if column.HasCheckState():
            name = {
                True: ObjectListView.NAME_CHECKED_IMAGE,
                False: ObjectListView.NAME_UNCHECKED_IMAGE,
                None: ObjectListView.NAME_UNDETERMINED_IMAGE
            }.get(column.GetCheckState(modelObject))
            return self.smallImageList.GetImageIndex(name)

        # Not a checkbox column, so just return the image
        imageIndex = column.GetImage(modelObject)
        if isinstance(imageIndex, basestring):
            return self.smallImageList.GetImageIndex(imageIndex)
        else:
            return imageIndex


    def GetObjectAt(self, index):
        """
        Return the model object at the given row of the list.
        """
        # Because of sorting, index can't be used directly, which is
        # why we set the item data to be the real index
        return self.innerList[self.GetItemData(index)]


    def __getitem__(self, index):
        """
        Synactic sugar over GetObjectAt()
        """
        return self.GetObjectAt(index)


    def GetObjects(self):
        """
        Return the model objects that are available to the control.

        If no filter is in effect, this is the same as GetFilteredObjects().
        """
        return self.modelObjects


    def GetPrimaryColumn(self):
        """
        Return the primary column or None there is no primary column.

        The primary column is the first column given by the user.
        This column is edited when F2 is pressed.
        """
        i = self.GetPrimaryColumnIndex()
        if i == -1:
            return None
        else:
            return self.columns[i]


    def GetPrimaryColumnIndex(self):
        """
        Return the index of the primary column. Returns -1 when there is no primary column.

        The primary column is the first column given by the user.
        This column is edited when F2 is pressed.
        """
        for (i, x) in enumerate(self.columns):
            if not x.isInternal:
                return i

        return -1


    def GetSelectedObject(self):
        """
        Return the selected modelObject or None if nothing is selected or if more than one is selected.
        """
        model = None
        for (i, x) in enumerate(self.YieldSelectedObjects()):
            if i == 0:
                model = x
            else:
                model = None
                break
        return model


    def GetSelectedObjects(self):
        """
        Return a list of the selected modelObjects
        """
        return list(self.YieldSelectedObjects())


    def GetSortColumn(self):
        """
        Return the column by which the rows of this control should be sorted
        """
        if self.sortColumnIndex < 0 or self.sortColumnIndex >= len(self.columns):
            return None
        else:
            return self.columns[self.sortColumnIndex]


    def GetStringValueAt(self, modelObject, columnIndex):
        """
        Return a string representation of the value that should be display at the given column of the given modelObject
        """
        column = self.columns[columnIndex]
        return column.GetStringValue(modelObject)


    def GetValueAt(self, modelObject, columnIndex):
        """
        Return the value that should be display at the given column of the given modelObject
        """
        column = self.columns[columnIndex]
        return column.GetValue(modelObject)


    def IsCellEditing(self):
        """
        Is some cell currently being edited?
        """
        return self.cellEditor and self.cellEditor.IsShown()


    def IsChecked(self, modelObject):
        """
        Return a boolean indicating if the given modelObject is checked.
        """
        return self.GetCheckState(modelObject) == True


    def IsObjectSelected(self, modelObject):
        """
        Is the given modelObject selected?
        """
        return modelObject in self.GetSelectedObjects()


    def SetFilter(self, filter):
        """
        Remember the filter that is currently operating on this control.
        Set this to None to clear the current filter.

        A filter is a callable that accepts one parameter: the original list
        of model objects. The filter chooses which of these model objects should
        be visible to the user, and returns a collection of only those objects.

        The Filter module has some useful standard filters.

        You must call RepopulateList() for changes to the filter to be visible.
        """
        self.filter = filter


    def SetSortColumn(self, column, resortNow=False):
        """
        Set the column by which the rows should be sorted.

        'column' can be None (which makes the list be unsorted), a ColumnDefn,
        or the index of the column desired
        """
        if column is None:
            self.sortColumnIndex = -1
        elif isinstance(column, ColumnDefn):
            try:
                self.sortColumnIndex = self.columns.index(column)
            except ValueError:
                self.sortColumnIndex = -1
        else:
            self.sortColumnIndex = column
        if resortNow:
            self.SortBy(self.sortColumnIndex)
        else:
            self._UpdateColumnSortIndicators()


    def YieldSelectedObjects(self):
        """
        Progressively yield the selected modelObjects
        """
        i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while i != -1:
            yield self.GetObjectAt(i)
            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)


    #----------------------------------------------------------------------------
    # Calculating

    def GetSubItemRect(self, rowIndex, subItemIndex, flag):
        """
        Poor mans replacement for missing wxWindows method.

        The rect returned takes scroll position into account, so negative x and y are
        possible.
        """
        #print "GetSubItemRect(self, %d, %d, %d):" % (rowIndex, subItemIndex, flag)

        # Linux doesn't handle wx.LIST_RECT_LABEL flag. So we always get
        # the whole bounds then par it down to the cell we want
        rect = self.GetItemRect(rowIndex, wx.LIST_RECT_BOUNDS)

        if self.InReportView():
            rect = [0-self.GetScrollPos(wx.HORIZONTAL), rect.Y, 0, rect.Height]
            for i in range(subItemIndex+1):
                rect[0] += rect[2]
                rect[2] = self.GetColumnWidth(i)

        # If we want only the label rect for sub items, we have to manually
        # adjust for any image the subitem might have
        if flag == wx.LIST_RECT_LABEL:
            lvi = self.GetItem(rowIndex, subItemIndex)
            if lvi.GetImage() != -1:
                if self.HasFlag(wx.LC_ICON):
                    imageWidth = self.normalImageList.GetSize(0)[0]
                    rect[1] += imageWidth
                    rect[3] -= imageWidth
                else:
                    imageWidth = self.smallImageList.GetSize(0)[0] + 1
                    rect[0] += imageWidth
                    rect[2] -= imageWidth

        #print "rect=%s" % rect
        return rect


    def HitTestSubItem(self, pt):
        """
        Return a tuple indicating which (item, subItem) the given pt (client coordinates) is over.

        This uses the buildin version on Windows, and poor mans replacement on other platforms.
        """
        # The buildin version works on Windows
        if wx.Platform == "__WXMSW__":
            return wx.ListCtrl.HitTestSubItem(self, pt)

        (rowIndex, flags) = self.HitTest(pt)

        # Did the point hit any item?
        if (flags & wx.LIST_HITTEST_ONITEM) == 0:
            return (-1, 0, -1)

        # If it did hit an item and we are not in report mode, it must be the primary cell
        if not self.InReportView():
            return (rowIndex, wx.LIST_HITTEST_ONITEM, 0)

        # Find which subitem is hit
        if self.smallImageList is None:
            self.SetImageLists()
        right = 0
        scrolledX = self.GetScrollPos(wx.HORIZONTAL) + pt.x
        for i in range(self.GetColumnCount()):
            left = right
            right += self.GetColumnWidth(i)
            if scrolledX < right:
                if (scrolledX - left) < self.smallImageList.GetSize(0)[0]:
                    flag = wx.LIST_HITTEST_ONITEMICON
                else:
                    flag = wx.LIST_HITTEST_ONITEMLABEL
                return (rowIndex, flag, i)

        return (rowIndex, 0, -1)


    #----------------------------------------------------------------------------
    # Event handling

    def _HandleChar(self, evt):
        if evt.GetKeyCode() == wx.WXK_F2 and not self.IsCellEditing():
            return self._PossibleStartCellEdit(self.GetFocusedRow(), self.GetPrimaryColumnIndex())

        # We have to catch Return/Enter/Escape here since some types of controls
        # (e.g. ComboBox, UserControl) don't trigger key events that we can listen for.
        # Treat Return or Enter as committing the current edit operation unless the control
        # is a multiline text control, in which case we treat it as data
        if evt.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and self.IsCellEditing():
            if self.cellEditor and self.cellEditor.HasFlag(wx.TE_MULTILINE):
                return evt.Skip()
            else:
                return self.FinishCellEdit()

        # Treat Escape as cancel the current edit operation
        if evt.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL) and self.IsCellEditing():
            return self.CancelCellEdit()

        # Tab to the next editable column
        if evt.GetKeyCode() == wx.WXK_TAB and self.IsCellEditing():
            return self._HandleTabKey(evt.ShiftDown())

        # Space bar with a selection on a listview with checkboxes toggles the checkboxes
        if (evt.GetKeyCode() == wx.WXK_SPACE and
            not self.IsCellEditing() and
            self.checkStateColumn is not None and
            self.GetSelectedItemCount() > 0):
            return self._ToggleCheckBoxForSelection()

        if not self.IsCellEditing():
            if self._HandleTypingEvent(evt):
                return

        if not self.IsCellEditing() and self.handleStandardKeys:
            # Copy selection on Ctrl-C
            # Why is Ctrl-C represented by 3?! Is this Windows only?
            if (evt.GetKeyCode() == 3):
                self.CopySelectionToClipboard()
                return
            # Select All on Ctrl-A
            if (evt.GetKeyCode() == 1):
                self.SelectAll()
                return

        evt.Skip()


    def _HandleTypingEvent(self, evt):
        """
        """
        if self.GetItemCount() == 0 or self.GetColumnCount() == 0:
            return False

        if evt.GetModifiers() != 0 and evt.GetModifiers() != wx.MOD_SHIFT:
            return False

        if evt.GetKeyCode() > wx.WXK_START:
            return False

        if evt.GetKeyCode() in (wx.WXK_BACK, wx.WXK_DELETE):
            self.searchPrefix = u""
            return True

        # On which column are we going to compare values? If we should search on the
        # sorted column, and there is a sorted column and it is searchable, we use that
        # one, otherwise we fallback to the primary column
        if self.typingSearchesSortColumn and self.GetSortColumn() and self.GetSortColumn().isSearchable:
            searchColumn = self.GetSortColumn()
        else:
            searchColumn = self.GetPrimaryColumn()

        # On Linux, GetUnicodeKey() always returns 0 -- on my 2.8.7.1 (gtk2-unicode)
        if evt.GetUnicodeKey() == 0:
            uniChar = chr(evt.GetKeyCode())
        else:
            uniChar = unichr(evt.GetUnicodeKey())
        if uniChar not in string.printable:
            return False

        # On Linux, evt.GetTimestamp() isn't reliable so use time.time() instead
        timeNow = time.time()
        if (timeNow - self.whenLastTypingEvent) > self.SEARCH_KEYSTROKE_DELAY:
            self.searchPrefix = uniChar
        else:
            self.searchPrefix += uniChar
        self.whenLastTypingEvent = timeNow

        #self.__rows = 0
        self._FindByTyping(searchColumn, self.searchPrefix)
        #print "Considered %d rows in %2f secs" % (self.__rows, time.time() - timeNow)

        return True

    def _FindByTyping(self, searchColumn, prefix):
        """
        Select the first row passed the currently focused row that has a string representation
        that begins with 'prefix' in the given column
        """
        start = max(self.GetFocusedRow(), 0)

        # If the user is starting a new search, we don't want to consider the current row
        if len(prefix) == 1:
            start = (start + 1) % self.GetItemCount()

        # If we are searching on a sorted column, use a binary search
        if self._CanUseBisect(searchColumn):
            if self._FindByBisect(searchColumn, prefix, start, self.GetItemCount()):
                return
            if self._FindByBisect(searchColumn, prefix, 0, start):
                return
        else:
            # A binary search on a sorted column can handle any number of rows. A linear
            # search cannot. So we impose an arbitrary limit on the number of rows to
            # consider. Above that, we don't even try
            if self.GetItemCount() > self.MAX_ROWS_FOR_UNSORTED_SEARCH:
                self._SelectAndFocus(0)
                return

            # Do a linear, wrapping search to find the next match. To wrap, we consider
            # the rows in two partitions: start to the end of the collection, and then
            # from the beginning to the start position. Expressing this in other languages
            # is a pain, but it's elegant in Python. I just love Python :)
            for i in itertools.chain(range(start, self.GetItemCount()), range(0, start)):
                #self.__rows += 1
                model = self.GetObjectAt(i)
                if model is not None:
                    strValue = searchColumn.GetStringValue(model)
                    if strValue.lower().startswith(prefix):
                        self._SelectAndFocus(i)
                        return
        wx.Bell()

    def _CanUseBisect(self, searchColumn):
        """
        Return True if we can use binary search on the given column
        """
        # If the list isn't sorted or if it's sorted by some other column, we can't
        if self.GetSortColumn() != searchColumn:
            return False

        # If the column doesn't knows whether it should or not, make a guess based on the
        # type of data in the column (strings and booleans are probably safe). We already
        # know that the list isn't empty.
        if searchColumn.useBinarySearch is None:
            aspect = searchColumn.GetValue(self.GetObjectAt(0))
            searchColumn.useBinarySearch = isinstance(aspect, (basestring, bool))

        return searchColumn.useBinarySearch

    def _FindByBisect(self, searchColumn, prefix, start, end):
        """
        Use a binary search to look for rows that match the given prefix between the rows given.

        If a match was found, select/focus/reveal that row and return True.
        """

        # If the sorting is ascending, we use less than to find the first match
        # If the sort is descending, we have to use greater-equal, and suffix the
        # search string to make sure we find the first match (without the suffix
        # we always find the last match)
        if self.sortAscending:
            cmpFunc = operator.lt
            searchFor = prefix
        else:
            cmpFunc = operator.ge
            searchFor = prefix + "z"

        # Adapted from bisect std module
        lo = start
        hi = end
        while lo < hi:
            mid = (lo + hi) // 2
            strValue = searchColumn.GetStringValue(self.GetObjectAt(mid))
            if cmpFunc(searchFor, strValue.lower()):
                hi = mid
            else:
                lo = mid+1

        if lo < start or lo >= end:
            return False

        strValue = searchColumn.GetStringValue(self.GetObjectAt(lo))
        if strValue.lower().startswith(prefix):
            self._SelectAndFocus(lo)
            return True

        return False

    def _SelectAndFocus(self, rowIndex):
        """
        Select and focus on the given row.
        """
        self.DeselectAll()
        self.Select(rowIndex)
        self.Focus(rowIndex)

    def _ToggleCheckBoxForSelection(self):
        """
        Toggles the checkedness of the selected modelObjects.
        """
        selection = self.GetSelectedObjects()
        newValue = not self.IsChecked(selection[0])
        for x in selection:
            self.SetCheckState(x, newValue)
        self.RefreshObjects(selection)

    def _HandleColumnBeginDrag(self, evt):
        """
        Handle when the user begins to resize a column
        """
        self._PossibleFinishCellEdit()
        colIndex = evt.GetColumn()
        if 0 > colIndex >= len(self.columns):
            evt.Skip()
        else:
            col = self.columns[colIndex]
            if col.IsFixedWidth() or col.isSpaceFilling:
                evt.Veto()
            else:
                evt.Skip()


    def _HandleColumnClick(self, evt):
        """
        The user has clicked on a column title
        """
        evt.Skip()
        self._PossibleFinishCellEdit()

        # Toggle the sort column on the second click
        if evt.GetColumn() == self.sortColumnIndex:
            self.sortAscending = not self.sortAscending
        else:
            self.sortAscending = True

        self.SortBy(evt.GetColumn(), self.sortAscending)
        self._FormatAllRows()


    def _HandleColumnDragging(self, evt):
        """
        A column is being dragged
        """
        # When is this triggered?        
        self.MAJ_footer()
        
        # The processing should be the same processing as Dragged
        evt.Skip()


    def _HandleColumnEndDrag(self, evt):
        """
        The user has finished resizing a column. Make sure that it is not
        bigger than it should be, then resize any space filling columns.
        """
        colIndex = evt.GetColumn()
        if 0 > colIndex >= len(self.columns):
            evt.Skip()
        else:
            currentWidth = self.GetColumnWidth(colIndex)
            col = self.columns[colIndex]
            newWidth = col.CalcBoundedWidth(currentWidth)
            if currentWidth != newWidth:
                wx.CallAfter(self._SetColumnWidthAndResize, colIndex, newWidth)
            else:
                evt.Skip()
                wx.CallAfter(self._ResizeSpaceFillingColumns)
        
    def _SetColumnWidthAndResize(self, colIndex, newWidth):
        self.SetColumnWidth(colIndex, newWidth)
        self._ResizeSpaceFillingColumns()

    def _HandleLeftDown(self, evt):
        """
        Handle a left down on the ListView
        """
        evt.Skip()

        # Test for a mouse down on the image of the check box column
        if self.InReportView():
            (row, flags, subitem) = self.HitTestSubItem(evt.GetPosition())
        else:
            (row, flags) = self.HitTest(evt.GetPosition())
            subitem = 0

        if flags == wx.LIST_HITTEST_ONITEMICON:
            self._HandleLeftDownOnImage(row, subitem)


    def _HandleLeftDownOnImage(self, rowIndex, subItemIndex):
        """
        Handle a left click on the image at the given cell
        """
        column = self.columns[subItemIndex]
        if not column.HasCheckState():
            return

        self._PossibleFinishCellEdit()
        modelObject = self.GetObjectAt(rowIndex)
        if modelObject is not None:
            column.SetCheckState(modelObject, not column.GetCheckState(modelObject))
            self.RefreshIndex(rowIndex, modelObject)
            self.OnCheck(modelObject)
    
    def OnCheck(self, modelObject=None):
        """ Fonction perso a surcharger """
        pass

    def _HandleLeftClickOrDoubleClick(self, evt):
        """
        Handle a left click or left double click on the ListView
        """
        evt.Skip()
        
        # IF any modifiers are down, OR
        #    the listview isn't editable, OR
        #    we should edit on double click and this is a single click, OR
        #    we should edit on single click and this is a double click,
        # THEN we don't try to start a cell edit operation        
##        if evt.m_altDown or evt.m_controlDown or evt.m_shiftDown:
##        if evt.AltDown or evt.ControlDown or evt.ShiftDown:
##            return
        if self.cellEditMode == self.CELLEDIT_NONE:
            return
        if evt.LeftUp() and self.cellEditMode == self.CELLEDIT_DOUBLECLICK:
            return
        if evt.LeftDClick() and self.cellEditMode == self.CELLEDIT_SINGLECLICK:
            return
        
        # Which item did the user click?
        (rowIndex, flags, subItemIndex) = self.HitTestSubItem(evt.GetPosition())
        if (flags & wx.LIST_HITTEST_ONITEM) == 0 or subItemIndex == -1:
            return

        # A single click on column 0 doesn't start an edit
        if subItemIndex == 0 and self.cellEditMode == self.CELLEDIT_SINGLECLICK:
            return

        self._PossibleStartCellEdit(rowIndex, subItemIndex)


    def _HandleMouseWheel(self, evt):
        """
        The user spun the mouse wheel
        """
        self._PossibleFinishCellEdit()
        evt.Skip()


    def _HandleScroll(self, evt):
        """
        The ListView is being scrolled
        """
        self._PossibleFinishCellEdit()
        self.MAJ_footer()
        evt.Skip()

    def OnScroll(self, evt):
        self.MAJ_footer()
        evt.Skip()


    def _HandleSize(self, evt):
        """
        The ListView is being resized
        """
        self._PossibleFinishCellEdit()
        evt.Skip()
        self._ResizeSpaceFillingColumns()
        # Make sure our empty msg is reasonably positioned
        sz = self.GetClientSize()
        if self.HasFlag(wx.LC_NO_HEADER) :
            proportion = 3
        else :
            proportion = 2
        self.stEmptyListMsg.SetDimensions(0, sz.GetHeight()/proportion, sz.GetWidth(), sz.GetHeight()) # J'ai mis 2 a la place de 3
        #self.stEmptyListMsg.Wrap(sz.GetWidth())


    def _HandleTabKey(self, isShiftDown):
        """
        Handle a Tab key during a cell edit operation
        """
        (rowBeingEdited, subItem) = self.cellBeingEdited

        # Prevent a nasty flicker when tabbing between fields where the selected rows
        # are restored at the end of one cell edit, and removed at the start of the next
        shadowSelection = self.selectionBeforeCellEdit
        self.selectionBeforeCellEdit = []
        self.FinishCellEdit()

        # If we are in report view, move to the next (or previous) editable subitem,
        # wrapping at the edges
        if self.HasFlag(wx.LC_REPORT):
            columnCount = self.GetColumnCount()
            for ignored in range(columnCount-1):
                if isShiftDown:
                    subItem = (columnCount + subItem - 1) % columnCount
                else:
                    subItem = (subItem + 1) % columnCount
                if self.columns[subItem].isEditable and self.GetColumnWidth(subItem) > 0:
                    self.StartCellEdit(rowBeingEdited, subItem)
                    break

        self.selectionBeforeCellEdit = shadowSelection


    #--------------------------------------------------------------#000000#FFFFFF
    # Sorting

    def EnableSorting(self):
        """
        Enable automatic sorting when the user clicks on a column title
        """
        self.Bind(wx.EVT_LIST_COL_CLICK, self._HandleColumnClick)

        # Install sort indicators if they don't already exist
        if self.smallImageList is None:
            self.SetImageLists()
        if (not self.smallImageList.HasName(ObjectListView.NAME_DOWN_IMAGE) and
            self.smallImageList.GetSize(0) == (16,16)):
            self.RegisterSortIndicators()


    def SortBy(self, newColumnIndex, ascending=True):
        """
        Sort the items by the given column
        """
        oldSortColumnIndex = self.sortColumnIndex
        self.sortColumnIndex = newColumnIndex
        self.sortAscending = ascending

        # Let the world have a chance to sort the items
        evt = OLVEvent.SortEvent(self, self.sortColumnIndex, self.sortAscending, self.IsVirtual())
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed():
            return

        if not evt.wasHandled:
            self._SortItemsNow()

        self._UpdateColumnSortIndicators(self.sortColumnIndex, oldSortColumnIndex)


    def _SortItemsNow(self):
        """
        Sort the actual items in the list now, according to the current column and order
        """
        sortColumn = self.GetSortColumn()
        if not sortColumn:
            return

        secondarySortColumn = None # self.GetSecondarySortColumn()

        def _singleObjectComparer(col, object1, object2):
            value1 = col.GetValue(object1)
            value2 = col.GetValue(object2)
            try:
                return locale.strcoll(value1.lower(), value2.lower())
            except:
                return cmp(value1, value2)

        def _objectComparer(object1, object2):
            result = _singleObjectComparer(sortColumn, object1, object2)
            if secondarySortColumn and result == 0:
                result = _singleObjectComparer(secondarySortColumn, object1, object2)
            return result

        self.SortListItemsBy(_objectComparer)


    def SortListItemsBy(self, cmpFunc, ascending=None):
        """
        Sort the existing list items using the given comparison function.

        The comparison function must accept two model objects as parameters.

        The primary users of this method are handlers of the SORT event that want
        to sort the items by their own special function.
        """
        if ascending is None:
            ascending = self.sortAscending

        def _sorter(key1, key2):
            cmpVal = cmpFunc(self.innerList[key1], self.innerList[key2])
            if ascending:
                return cmpVal
            else:
                return -cmpVal

        self.SortItems(_sorter)


    def _SortObjects(self, modelObjects=None, sortColumn=None, secondarySortColumn=None):
        """
        Sort the given modelObjects in place.

        This does not change the information shown in the control itself.
        """
        if modelObjects is None:
            modelObjects = self.modelObjects
        if sortColumn is None:
            sortColumn = self.GetSortColumn()
        if secondarySortColumn == sortColumn:
            secondarySortColumn = None

        # If we don't have a sort column, we can't sort -- duhh
        if sortColumn is None:
            return

        # Let the world have a chance to sort the model objects
        evt = OLVEvent.SortEvent(self, self.sortColumnIndex, self.sortAscending, True)
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed() or evt.wasHandled:
            return

        # When sorting large groups, this is called a lot. Make it efficent.
        # It is more efficient (by about 30%) to try to call lower() and catch the
        # exception than it is to test for the class
        def _getSortValue(x):
            primary = sortColumn.GetValue(x)
            if type(primary) == datetime.date :
                primary = str(primary)
            try:
                primary = primary.lower()
            except AttributeError:
                pass
            if secondarySortColumn:
                secondary = secondarySortColumn.GetValue(x)
                if type(secondary) == datetime.date :
                    secondary = str(secondary)
                try:
                    secondary = secondary.lower()
                except AttributeError:
                    pass
                return (primary, secondary)
            else:
                return primary

        modelObjects.sort(key=_getSortValue, reverse=(not self.sortAscending))

        # Sorting invalidates our object map
        self.objectToIndexMap = None


    def _UpdateColumnSortIndicators(self, sortColumnIndex=None, oldSortColumnIndex=-1):
        """
        Change the column that is showing a sort indicator
        """
        if sortColumnIndex is None:
            sortColumnIndex = self.sortColumnIndex
        # Remove the sort indicator from the old sort column
        if oldSortColumnIndex >= 0:
            headerImage = self.columns[oldSortColumnIndex].headerImage
            if isinstance(headerImage, basestring) and self.smallImageList is not None:
                headerImage = self.smallImageList.GetImageIndex(headerImage)
            self.SetColumnImage(oldSortColumnIndex, headerImage)

        if sortColumnIndex >= 0 and self.smallImageList is not None:
            if self.sortAscending:
                imageIndex = self.smallImageList.GetImageIndex(ObjectListView.NAME_UP_IMAGE)
            else:
                imageIndex = self.smallImageList.GetImageIndex(ObjectListView.NAME_DOWN_IMAGE)

            if imageIndex != -1:
                self.SetColumnImage(sortColumnIndex, imageIndex)


    #--------------------------------------------------------------#000000#FFFFFF
    # Selecting

    def SelectAll(self):
        """
        Selected all rows in the control
        """
        # -1 indicates 'all items'
        self.SetItemState(-1, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def DeselectAll(self):
        """
        De-selected all rows in the control
        """
        # -1 indicates 'all items'
        self.SetItemState(-1, 0, wx.LIST_STATE_SELECTED)


    def SelectObject(self, modelObject, deselectOthers=True, ensureVisible=False):
        """
        Select the given modelObject. If deselectOthers is True, all other rows will be deselected
        """
        i = self.GetIndexOf(modelObject)
        if i == -1:
            return

        if deselectOthers:
            self.DeselectAll()

        realIndex = self._MapModelIndexToListIndex(i)
        self.SetItemState(realIndex, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        if ensureVisible:
            self.EnsureVisible(realIndex)


    def SelectObjects(self, modelObjects, deselectOthers=True):
        """
        Select all of the given modelObjects. If deselectOthers is True, all other rows will be deselected
        """
        if deselectOthers:
            self.DeselectAll()

        for x in modelObjects:
            self.SelectObject(x, False)


    def _MapModelIndexToListIndex(self, modelIndex):
        """
        Return the index in the list where the given model index lives
        """
        return self.FindItemData(-1, modelIndex)

    #----------------------------------------------------------------------------
    # Cell editing

    def _PossibleStartCellEdit(self, rowIndex, subItemIndex):
        """
        Start an edit operation on the given cell after performing some sanity checks
        """
        if 0 > rowIndex >= self.GetItemCount():
            return

        if 0 > subItemIndex >= self.GetColumnCount():
            return

        if self.cellEditMode == self.CELLEDIT_NONE:
            return

        if not self.columns[subItemIndex].isEditable:
            return

        if self.GetObjectAt(rowIndex) is None:
            return

        self.StartCellEdit(rowIndex, subItemIndex)


    def _PossibleFinishCellEdit(self):
        """
        If a cell is being edited, finish and commit an edit operation on the given cell.
        """
        if self.IsCellEditing():
            self.FinishCellEdit()


    def _PossibleCancelCellEdit(self):
        """
        If a cell is being edited, cancel the edit operation.
        """
        if self.IsCellEditing():
            self.CancelCellEdit()


    def StartCellEdit(self, rowIndex, subItemIndex):
        """
        Begin an edit operation on the given cell.
        """

        # Collect the information we need for the StartingEditEvent
        modelObject = self.GetObjectAt(rowIndex)
        cellValue = self.GetValueAt(modelObject, subItemIndex)

        # Make sure the user can see where the editor is going to be. If the bounds are
        # null, this means we needed to scroll horizontally but were unable (this can only
        # happen on non-Windows platforms). In that case we can't let the edit happen
        # since the user won't be able to see the cell
        cellBounds = self.EnsureCellVisible(rowIndex, subItemIndex)
        if cellBounds is None:
            wx.Bell()
            return

        # Give the world the chance to veto the edit, or to change its characteristics
        defaultEditor = self._MakeDefaultCellEditor(rowIndex, subItemIndex, cellValue)
        evt = OLVEvent.CellEditStartingEvent(self, rowIndex, subItemIndex, modelObject,
                                             cellValue, cellBounds, defaultEditor)
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed():
            defaultEditor.Destroy()
            return

        # Remember that we are editing something (and make sure we can see it)
        self.selectionBeforeCellEdit = self.GetSelectedObjects()
        self.DeselectAll()
        self.cellEditor = evt.newEditor or evt.editor
        self.cellBeingEdited = (rowIndex, subItemIndex)

        # If we aren't using the default editor, destroy it
        if self.cellEditor != defaultEditor:
            defaultEditor.Destroy()

        # If the event handler hasn't already configured the editor, do it now.
        if evt.shouldConfigureEditor:
            self.cellEditor.SetFocus()
            self.cellEditor.SetValue(evt.cellValue)
            self._ConfigureCellEditor(self.cellEditor, evt.cellBounds, rowIndex, subItemIndex)

        # Let the world know the cell editing has started
        evt = OLVEvent.CellEditStartedEvent(self, rowIndex, subItemIndex, modelObject,
                                             cellValue, cellBounds, defaultEditor)
        self.GetEventHandler().ProcessEvent(evt)

        self.cellEditor.Show()
        self.cellEditor.Raise()


    def _ConfigureCellEditor(self, editor, bounds, rowIndex, subItemIndex):
        """
        Perform the normal configuration on the cell editor.
        """
        editor.SetDimensions(*bounds)

        colour = self.GetItemBackgroundColour(rowIndex)
        if colour.IsOk():
            editor.SetBackgroundColour(colour)
        else:
            editor.SetBackgroundColour(self.GetBackgroundColour())

        colour = self.GetItemTextColour(rowIndex)
        if colour.IsOk():
            editor.SetForegroundColour(colour)
        else:
            editor.SetForegroundColour(self.GetTextColour())

        font = self.GetItemFont(rowIndex)
        if font.IsOk():
            editor.SetFont(font)
        else:
            editor.SetFont(self.GetFont())

        if hasattr(self.cellEditor, "SelectAll"):
            self.cellEditor.SelectAll()

        editor.Bind(wx.EVT_CHAR, self._Editor_OnChar)
        editor.Bind(wx.EVT_COMMAND_ENTER, self._Editor_OnChar)
        editor.Bind(wx.EVT_KILL_FOCUS, self._Editor_KillFocus)


    def _MakeDefaultCellEditor(self, rowIndex, subItemIndex, value):
        """
        Return an editor that can edit the value of the given cell.
        """

        # The column could have editor creation function registered.
        # Otherwise, we have to guess the editor from the type of the value.
        # If the given cell actually holds None, we can't decide what editor to use.
        # So we try to find any non-null value in the same column.
        # If all else fails, we use a string editor.
        creatorFunction = self.columns[subItemIndex].cellEditorCreator
        if creatorFunction is None:
            value = value or self._CalcNonNullValue(subItemIndex)
            creatorFunction = CellEditor.CellEditorRegistry().GetCreatorFunction(value)
            if creatorFunction is None:
                creatorFunction = CellEditor.CellEditorRegistry().GetCreatorFunction("")
        return creatorFunction(self, rowIndex, subItemIndex)


    def _CalcNonNullValue(self, colIndex, maxRows=1000):
        """
        Return the first non-null value in the given column, processing
        at most maxRows rows
        """
        column = self.columns[colIndex]
        for i in range(min(self.GetItemCount(), maxRows)):
            model = self.GetObjectAt(i)
            if model is not None:
                value = column.GetValue(model)
                if value is not None:
                    return value
        return None


    def _Editor_OnChar(self, evt):
        """
        A character has been pressed in a cell editor
        """
        self._HandleChar(evt)


    def _Editor_KillFocus(self, evt):
        evt.Skip()

        # Some control trigger FocusLost events even when they still have focus
        focusWindow = wx.Window.FindFocus()
        #if focusWindow is not None and self.cellEditor != focusWindow:
        if self.cellEditor != focusWindow:
            self._PossibleFinishCellEdit()


    def FinishCellEdit(self):
        """
        Finish and commit an edit operation on the given cell.
        """
        (rowIndex, subItemIndex) = self.cellBeingEdited

        # Give the world the chance to veto the edit, or to change its characteristics
        rowModel = self.GetObjectAt(rowIndex)
        evt = OLVEvent.CellEditFinishingEvent(self, rowIndex, subItemIndex, rowModel,
                                              self.cellEditor.GetValue(), self.cellEditor, False)
        self.GetEventHandler().ProcessEvent(evt)
        if not evt.IsVetoed() and evt.cellValue is not None:
            self.columns[subItemIndex].SetValue(rowModel, evt.cellValue)
            self.RefreshIndex(rowIndex, rowModel)

        evt = OLVEvent.CellEditFinishedEvent(self, rowIndex, subItemIndex, rowModel, False)
        self.GetEventHandler().ProcessEvent(evt)

        self._CleanupCellEdit()


    def CancelCellEdit(self):
        """
        Cancel an edit operation on the given cell.
        """
        # Tell the world that the user cancelled the edit
        (rowIndex, subItemIndex) = self.cellBeingEdited
        evt = OLVEvent.CellEditFinishingEvent(self, rowIndex, subItemIndex,
                                              self.GetObjectAt(rowIndex),
                                              self.cellEditor.GetValue(),
                                              self.cellEditor,
                                              True)
        self.GetEventHandler().ProcessEvent(evt)

        evt = OLVEvent.CellEditFinishedEvent(self, rowIndex, subItemIndex, rowModel, True)
        self.GetEventHandler().ProcessEvent(evt)

        self._CleanupCellEdit()


    def _CleanupCellEdit(self):
        """
        Cleanup after finishing a cell edit operation
        """
        self.SelectObjects(self.selectionBeforeCellEdit)
        if self.cellEditor:
            self.cellEditor.Hide()
            self.cellEditor = None
        self.cellBeingEdited = None
        self.SetFocus()

    def SetColumns2(self, colonnes=[], nomListe=None):
        """ Pour une liste avec possibilités de configuration """
        self.nomListe = nomListe
        if self.listeColonnes == [] :
            import DLG_Configuration_listes
            self.listeColonnesDefaut = copy.deepcopy(colonnes)
            self.listeColonnes = DLG_Configuration_listes.RestaurationConfiguration(nomListe=nomListe, listeColonnesDefaut=colonnes)
        self.SetColumns(self.listeColonnes)

    def AjouterCommandesMenuContext(self, menu=None):
        # Séparation
        menu.AppendSeparator()
        
        # Item Configurer la liste
        item = wx.MenuItem(menu, 8601, u"Configurer la liste")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuConfigurerListe, id=8601)

        # Séparation
        menu.AppendSeparator()
        
        # Statistiques de la liste
        nbreLignes = len(self.innerList)
        if nbreLignes == 0 :
            label = u"Liste vide"
        elif nbreLignes == 1 :
            label = u"1 ligne"
        else :
            label = u"%d lignes" % nbreLignes
        label += u" et %d colonnes" % len(self.columns) 
        item = wx.MenuItem(menu, 8602, label)
        menu.AppendItem(item)
        item.Enable(False)
    
    def MenuConfigurerListe(self, event=None):
        # Préparation de la liste
        listeDonnees = []
        dictColonnes = {}
        for col in self.listeColonnes :
            listeDonnees.append((col.valueGetter, col.visible))
            dictColonnes[col.valueGetter] = col
            
        listeDonneesDefaut = []
        for col in self.listeColonnesDefaut :
            listeDonneesDefaut.append((col.valueGetter, col.visible))
            
        # DLG de la configuration de listes
        import DLG_Configuration_listes
        dlg = DLG_Configuration_listes.Dialog(self, listeDonnees=listeDonnees, listeDonneesDefaut=listeDonneesDefaut)      
        if dlg.ShowModal() == wx.ID_OK:
            listeDonnees = dlg.GetListeDonnees()
            dlg.Destroy() 
        else :
            dlg.Destroy() 
            return
        
        # Analyse des résultats
        self.listeColonnes = []
        for nom, visible in listeDonnees :
            col = dictColonnes[nom]
            col.visible = visible
            self.listeColonnes.append(col)
            
        # Sauvegarde
        self.SauvegardeConfiguration()
        
        # Mise à jour de la liste
        attente = wx.BusyInfo(u"Configuration de la liste en cours...", self)
        self.InitModel()
        self.InitObjectListView()
        attente.Destroy()
    
    def SauvegardeConfiguration(self, event=None):
        """ Sauvegarde de la configuration """
        if self.nomListe != None :
            import DLG_Configuration_listes
            DLG_Configuration_listes.SauvegardeConfiguration(nomListe=self.nomListe, listeColonnes=self.listeColonnes)
    
        
    def AjouteLigneTotal(self, listeNomsColonnes=[]):
        return
        for (iCol, col) in enumerate(self.columns):
            print col, col.__dict__
            colWidth = self.GetColumnWidth(iCol)
            boundedWidth = col.CalcBoundedWidth(colWidth)
            print colWidth, boundedWidth


        # Récupération des totaux des colonnes souhaitées
        dictTotaux = {}
        nbreLignes = 0
        for track in self.modelObjects :
            for nomColonne in listeNomsColonnes :
                valeur = getattr(track, nomColonne)
                if dictTotaux.has_key(nomColonne) == False :
                    dictTotaux[nomColonne] = 0
                else :
                    dictTotaux[nomColonne] += valeur
            nbreLignes += 1
        
        track = Track(dictTotaux)
##        self.modelObjects.append(track)
        self.AddObject(track)
    
    def SetFooter(self, ctrl=None, dictColonnes={}):
        self.ctrl_footer = ctrl
        self.ctrl_footer.listview = self
        self.ctrl_footer.dictColonnes = dictColonnes
    
    def MAJ_footer(self):
        if self.ctrl_footer != None :
            self.ctrl_footer.MAJ()
    
    def GetListview(self):
        return self
        
    def DefileDernier(self):
        """ Defile jusqu'au dernier item de la liste """
        largeur, hauteur = self.GetSize()
        if largeur > 0 and hauteur > 0 :
            if self.GetFilter() != None :
                listeObjets = self.GetFilteredObjects()
            else :
                listeObjets = self.GetObjects()
            if len(listeObjets) > 0 :
                dernierTrack = listeObjets[-1]
                index = self.GetIndexOf(dernierTrack)
                self.EnsureCellVisible(index, 0)
            
    def Filtrer(self, texteRecherche=None):
        listeFiltres = []
        
        # Filtre barre de recherche
        if texteRecherche != None :
            filtre = Filter.TextSearch(self, self.columns[0:self.GetColumnCount()])
            filtre.SetText(texteRecherche)
            listeFiltres.append(filtre)
        
        # Filtres de colonnes
        for texteFiltre in self.formatageFiltres(self.listeFiltresColonnes) :
            exec("filtre = Filter.Predicate(lambda track: %s)" % texteFiltre)
            listeFiltres.append(filtre)
            
        self.SetFilter(Filter.Chain(*listeFiltres))
        self.RepopulateList()
        self.Refresh() 
        self.OnCheck(None) 
    
    def SetFiltresColonnes(self, listeFiltresColonnes=[]):
        self.listeFiltresColonnes = listeFiltresColonnes
        if self.barreRecherche != None :
            self.barreRecherche.Cancel()
        self.Filtrer() 
    
    def formatageFiltres(self, listeFiltres=[]):
        # Formatage du filtre
        listeFiltresFinale = []
        for dictFiltre in listeFiltres :
            code = dictFiltre["code"]
            choix = dictFiltre["choix"]
            criteres = dictFiltre["criteres"]
            typeDonnee = dictFiltre["typeDonnee"]
            
            # Texte
            if typeDonnee == "texte" :
                if choix == "EGAL" :
                    filtre = "track.%s != None and track.%s.lower() == '%s'.lower()" % (code, code, criteres)
                if choix == "DIFFERENT" :
                    filtre = "track.%s != None and track.%s.lower() != '%s'.lower()" % (code, code, criteres)
                if choix == "CONTIENT" :
                    filtre = "track.%s != None and '%s'.lower() in track.%s.lower()" % (code, criteres, code)
                if choix == "CONTIENTPAS" :
                    filtre = "track.%s != None and '%s'.lower() not in track.%s.lower()" % (code, criteres, code)
                if choix == "VIDE" :
                    filtre = "track.%s == '' or track.%s == None" % (code, code)
                if choix == "PASVIDE" :
                    filtre = "track.%s != '' and track.%s != None" % (code, code)
            
            # Entier, montant
            if typeDonnee in ("entier", "montant") :
                
                if choix == "COMPRIS" :
                    min = str(criteres.split(";")[0])
                    max = str(criteres.split(";")[1])
                else :
                    criteres = str(criteres)
                        
                if choix == "EGAL" :
                    filtre = "track.%s == %s" % (code, criteres)
                if choix == "DIFFERENT" :
                    filtre = "track.%s != %s" % (code, criteres)
                if choix == "SUP" :
                    filtre = "track.%s > %s" % (code, criteres)
                if choix == "SUPEGAL" :
                    filtre = "track.%s >= %s" % (code, criteres)
                if choix == "INF" :
                    filtre = "track.%s < %s" % (code, criteres)
                if choix == "INFEGAL" :
                    filtre = "track.%s <= %s" % (code, criteres)
                if choix == "COMPRIS" :
                    filtre = "track.%s >= %s and track.%s <= %s" % (code, min, code, max)

            # Date
            if typeDonnee == "date" :
                        
                if choix == "EGAL" :
                    filtre = "track.%s != None and str(track.%s) == '%s'" % (code, code, criteres)
                if choix == "DIFFERENT" :
                    filtre = "track.%s != None and str(track.%s) != '%s'" % (code, code, criteres)
                if choix == "SUP" :
                    filtre = "track.%s != None and str(track.%s) > '%s'" % (code, code, criteres)
                if choix == "SUPEGAL" :
                    filtre = "track.%s != None and str(track.%s) >= '%s'" % (code, code, criteres)
                if choix == "INF" :
                    filtre = "track.%s != None and str(track.%s) < '%s'" % (code, code, criteres)
                if choix == "INFEGAL" :
                    filtre = "track.%s != None and str(track.%s) <= '%s'" % (code, code, criteres)
                if choix == "COMPRIS" :
                    min = criteres.split(";")[0]
                    max = criteres.split(";")[1]
                    filtre = "track.%s != None and str(track.%s) >= '%s' and str(track.%s) <= '%s'" % (code, code, min, code, max)
            
            # Inscrits
            if typeDonnee == "inscrits" :
                if choix == "INSCRITS" :
                    filtre = "track.ID%s in %s" % (code, self.GetInscrits(mode=code, listeActivites=criteres["listeActivites"], listeGroupes=criteres["listeGroupes"]))
                if choix == "PRESENTS" :
                    filtre = "track.ID%s in %s" % (code, self.GetInscrits(mode=code, listeActivites=criteres["listeActivites"], listeGroupes=criteres["listeGroupes"], periode=(criteres["date_debut"], criteres["date_fin"])))
                    
            # Mémorisation
            listeFiltresFinale.append(filtre) 
        
        return listeFiltresFinale

    def GetInscrits(self, mode="individu", listeActivites=[], listeGroupes=[], periode=None):
        """ Récupération de la liste des individus inscrits et présents """        
        # Conditions Activites
        if listeActivites == None or listeActivites == [] :
            conditionActivites = ""
        else:
            if len(listeActivites) == 1 :
                conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
            else:
                conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

        # Conditions Groupes
        if listeGroupes == None or listeGroupes == [] :
            conditionGroupes = ""
        else:
            if len(listeGroupes) == 1 :
                conditionGroupes = " AND inscriptions.IDgroupe=%d" % listeGroupes[0]
            else:
                conditionGroupes = " AND inscriptions.IDgroupe IN %s" % str(tuple(listeGroupes))
            if periode != None :
                conditionGroupes = conditionGroupes.replace("inscriptions", "consommations")
                
        # Conditions Présents
        conditionPresents = ""
        jointurePresents = ""
        if periode != None :
            conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s')" % (str(periode[0]), str(periode[1]))
            jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = inscriptions.IDindividu"
        
        # Choix de la key
        if mode == "individu" :
            key = "inscriptions.IDindividu"
        if mode == "famille" :
            key = "inscriptions.IDfamille"
        
        import GestionDB
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM inscriptions 
        %s
        WHERE (inscriptions.parti=0 OR inscriptions.parti IS NULL)  %s %s %s
        GROUP BY %s
        ;""" % (key, jointurePresents, conditionActivites, conditionGroupes, conditionPresents, key)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        
        listeID = []
        for donnees in listeDonnees :
            listeID.append(donnees[0])
        return listeID

    def SetBarreRecherche(self, ctrl=None):
        self.barreRecherche = ctrl

    def CocheListeTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        self.OnCheck(None)
        
    def CocheListeRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)
        self.OnCheck(None)

########################################################################

class Track():
    def __init__(self, dictTotaux):
        for nomColonne, total in dictTotaux.iteritems() :
            setattr(self, nomColonne, total)


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, listview, texteDefaut=u"Rechercher..."):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.listview = listview
        self.rechercheEnCours = False
        
        # Assigne cette barre de recherche au listview
        self.listview.SetBarreRecherche(self)
        
        self.SetDescriptiveText(texteDefaut)
        self.ShowSearchButton(True)
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
    
    def Cancel(self):
        self.OnCancel(None)
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listview.Filtrer(txtSearch)

        
class CTRL_Outils(wx.Panel):
    def __init__(self, parent, listview=None, texteDefaut=u"Rechercher...", afficherCocher=False, style=wx.NO_BORDER | wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=-1, style=style)
        self.listview = listview
        
        # Contrôles
        self.barreRecherche = BarreRecherche(self, listview=listview, texteDefaut=texteDefaut)
##        self.bouton_filtrage = wx.Button(self, -1, u"Filtrage avancé", size=(-1, 20))
##        self.bouton_filtrage = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Filtrer_liste_2.png", wx.BITMAP_TYPE_ANY))
        
        import wx.lib.platebtn as platebtn
        
        # Bouton Filtrer
        self.bouton_filtrer = platebtn.PlateButton(self, -1, u" Filtrer", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Filtre.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_filtrer.SetToolTipString(u"Cliquez ici pour filtrer cette liste")
        
        menu = wx.Menu()
        item = wx.MenuItem(menu, 10, u"Ajouter, modifier ou supprimer des filtres", u"Cliquez ici pour accéder à la gestion des filtres de listes")
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Filtre.png"), wx.BITMAP_TYPE_ANY))
        menu.AppendItem(item)
        menu.AppendSeparator()
        item = wx.MenuItem(menu, 11, u"Supprimer tous les filtres", u"Cliquez ici pour supprimer tous les filtres")
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Filtre_supprimer.png"), wx.BITMAP_TYPE_ANY))
        menu.AppendItem(item)        
        self.bouton_filtrer.SetMenu(menu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFiltrer, self.bouton_filtrer) 
        
        # Bouton Cocher
        if afficherCocher == True :
            self.bouton_cocher = platebtn.PlateButton(self, -1, u" Cocher", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_ANY))
            self.bouton_cocher.SetToolTipString(u"Cliquez ici pour cocher ou décocher rapidement tous les éléments de cette liste")
            
            menu = wx.Menu()
            item = wx.MenuItem(menu, 20, u"Tout cocher", u"Cliquez ici pour cocher tous les éléments de la liste")
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_ANY))
            menu.AppendItem(item)
            item = wx.MenuItem(menu, 21, u"Tout décocher", u"Cliquez ici pour décocher tous les éléments de la liste")
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Decocher.png"), wx.BITMAP_TYPE_ANY))
            menu.AppendItem(item)        
            self.bouton_cocher.SetMenu(menu)
            self.Bind(wx.EVT_BUTTON, self.OnBoutonCocher, self.bouton_cocher) 

        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        # Layout
        sizerbase = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(self.barreRecherche, 1, wx.ALL|wx.EXPAND, 0)
        sizerbase.Add(self.bouton_filtrer, 0, wx.LEFT|wx.EXPAND, 5)
        if afficherCocher == True :
            sizerbase.Add(self.bouton_cocher, 0, wx.LEFT|wx.EXPAND, 5)
        self.SetSizer(sizerbase)
        self.Layout()
    
    def OnSize(self, event):
        self.Refresh() 
        event.Skip() 
        
    def MAJ_ctrl_filtrer(self):
        """ Met à jour l'image du bouton Filtrage """
        nbreFiltres = len(self.listview.listeFiltresColonnes)
        
        # Modifie l'image selon le nbre de filtres activés
        if nbreFiltres == 0 :
            nomImage = "Filtre"
        elif nbreFiltres < 10 :
            nomImage = "Filtre_%d" % nbreFiltres
        else :
            nomImage = "Filtre_10"
        self.bouton_filtrer.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s.png" % nomImage), wx.BITMAP_TYPE_ANY))
        self.bouton_filtrer.Refresh() 
        
        # Modifie le tip en fonction des filtres activés
        if nbreFiltres == 0 :
            texte = u"Cliquez ici pour filtrer cette liste"
        else :
            if nbreFiltres == 1 :
                texte = u"Cliquez ici pour filtrer cette liste\n> 1 filtre activé"
            else :
                texte = u"Cliquez ici pour filtrer cette liste\n> %d filtres activés" % nbreFiltres        
        self.bouton_filtrer.SetToolTipString(texte)
        
    def OnBoutonFiltrer(self, event):
        listeFiltres = []
        import DLG_Filtres_listes
        dlg = DLG_Filtres_listes.Dialog(self, ctrl_listview=self.listview)
        if dlg.ShowModal() == wx.ID_OK :
            listeFiltres = dlg.GetDonnees()                 
            self.listview.SetFiltresColonnes(listeFiltres)
            self.listview.Filtrer() 
            self.MAJ_ctrl_filtrer() 
        dlg.Destroy()
    
    def SetFiltres(self, listeFiltres=[]):
        self.listview.SetFiltresColonnes(listeFiltres)
        self.listview.Filtrer() 
        self.MAJ_ctrl_filtrer() 
    
    def OnBoutonCocher(self, event):
        self.bouton_cocher.ShowMenu() 
        
    def OnMenu(self, event):
        ID = event.GetId()
        # Accéder à la gestion des filtres
        if ID == 10 : 
            self.OnBoutonFiltrer(None)
        # Supprimer tous les filtres
        if ID == 11 : 
            self.listview.SetFiltresColonnes([])
            self.listview.Filtrer() 
            self.MAJ_ctrl_filtrer() 
        # Tout cocher
        if ID == 20 :
            self.listview.CocheListeTout()
        # Tout décocher
        if ID == 21 :
            self.listview.CocheListeRien()
            
            
            
    

        
class AbstractVirtualObjectListView(ObjectListView):
    """
    This class holds the behaviour that is common to all virtual lists.

    A virtual list must be given an "object getter", which is a callable that accepts the
    index of the model object required and returns the model. This can be set via the
    SetObjectGetter() method, or passed into the constructor as the "getter" parameter.

    Due to the vagarities of virtual lists, rowFormatters must operate in a slightly
    different manner for virtual lists. Instead of being passed a ListItem, rowFormatters
    are passed a ListItemAttr instance. This supports the same formatting methods as a
    ListItem -- SetBackgroundColour(), SetTextColour(), SetFont() -- but no other ListItem
    methods. Obviously, being a virtual list, the rowFormatter cannot call any SetItem*
    method on the ListView itself.

    """

    def __init__(self, *args, **kwargs):
        self.lastGetObjectIndex = -1
        self.lastGetObject = None
        self.objectGetter = None
        self.listItemAttr = None
        #self.cacheHit = 0
        #self.cacheMiss = 0

        self.SetObjectGetter(kwargs.pop("getter", None))

        # We have to set the item count after the list has been created
        if "count" in kwargs:
            wx.CallAfter(self.SetItemCount, kwargs.pop("count"))

        # Virtual lists have to be in report format
        kwargs["style"] = kwargs.get("style", 0) | wx.LC_REPORT | wx.LC_VIRTUAL

        ObjectListView.__init__(self, *args, **kwargs)


    #----------------------------------------------------------------------------
    # Commands

    def ClearAll(self):
        """
        Remove all items and columns
        """
        ObjectListView.ClearAll(self)
        self.lastGetObjectIndex = -1
        # Should this call SetItemCount()?


    def DeleteAllItems(self):
        """
        Remove all items
        """
        ObjectListView.DeleteAllItems(self)
        self.lastGetObjectIndex = -1
        # Should this call SetItemCount()?


    def RefreshIndex(self, index, modelObject):
        """
        Refresh the item at the given index with data associated with the given modelObject
        """
        self.lastGetObjectIndex = -1
        self.RefreshItem(index)


    def RefreshObject(self, modelObject):
        """
        Refresh the display of the given modelObject
        """
        # We only have a hammer so everything looks like a nail
        self.RefreshObjects()


    def RefreshObjects(self, aList=None):
        """
        Refresh all the objects in the given list
        """
        # We can only refresh everything
        self.lastGetObjectIndex = -1
        #self.RefreshItems(0, self.GetItemCount()-1)
        if self.GetItemCount() > 0:
            self.RefreshItems(0, self.GetItemCount()-1)
        #self.Refresh()


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        # Virtual lists never need to rebuild -- they simply redraw
        self.RefreshObjects()


    def SetItemCount(self, count):
        """
        Change the number of items visible in the list
        """
        wx.ListCtrl.SetItemCount(self, count)
        self.stEmptyListMsg.Show(count == 0)
        self.lastGetObjectIndex = -1


    def SetObjectGetter(self, aCallable):
        """
        Remember the callback that will be used to fetch the objects being displayed in
        this list
        """
        self.objectGetter = aCallable


    def _FormatAllRows(self):
        """
        Set up the required formatting on all rows
        """
        # This is handled within OnGetItemAttr()
        pass

    #----------------------------------------------------------------------------
    # Virtual list callbacks.
    # These are called a lot! Keep them efficient

    def OnGetItemText(self, itemIdx, colIdx):
        """
        Return the text that should be shown at the given cell
        """
        return self.GetStringValueAt(self.GetObjectAt(itemIdx), colIdx)


    def OnGetItemImage(self, itemIdx):
        """
        Return the image index that should be shown on the primary column of the given item
        """
        return self.GetImageAt(self.GetObjectAt(itemIdx), 0)


    def OnGetItemColumnImage(self, itemIdx, colIdx):
        """
        Return the image index at should be shown at the given cell
        """
        return self.GetImageAt(self.GetObjectAt(itemIdx), colIdx)


    def OnGetItemAttr(self, itemIdx):
        """
        Return the display attributes that should be used for the given row
        """
        if not self.useAlternateBackColors and self.rowFormatter is None:
            return None

        # We have to keep a reference to the ListItemAttr or the garbage collector
        # will clear it up immeditately, before the ListCtrl has time to process it.
        self.listItemAttr = wx.ListItemAttr()
        self._FormatOneItem(self.listItemAttr, itemIdx, self.GetObjectAt(itemIdx))

        return self.listItemAttr


    #----------------------------------------------------------------------------
    # Accessing

    def GetObjectAt(self, index):
        """
        Return the model modelObject at the given row of the list.

        This method is called a lot! Keep it as efficient as possible.
        """

        # For reasons of performance, it may even be worthwhile removing this test and
        # ensure/assume that objectGetter is never None
        if self.objectGetter is None:
            return None

        #if index == self.lastGetObjectIndex:
        #    self.cacheHit += 1
        #else:
        #    self.cacheMiss += 1
        #print "hit: %d / miss: %d" % (self.cacheHit, self.cacheMiss)

        # Cache the last result (the hit rate is normally good: 5-10 hits to 1 miss)
        if index != self.lastGetObjectIndex:
            self.lastGetObjectIndex = index
            self.lastGetObject = self.objectGetter(index)

        return self.lastGetObject



########################################################################

class VirtualObjectListView(AbstractVirtualObjectListView):
    """
    A virtual object list displays various aspects of an unlimited numbers of objects in a
    multi-column list control.

    By default, a VirtualObjectListView cannot sort its rows when the user click on a header.
    If you have a back store that can sort the data represented in the virtual list, you
    can listen for the EVT_SORT events, and then order your model objects accordingly.

    Due to the vagarities of virtual lists, rowFormatters must operate in a slightly
    different manner for virtual lists. Instead of being passed a ListItem, rowFormatters
    are passed a ListItemAttr instance. This supports the same formatting methods as a
    ListItem -- SetBackgroundColour(), SetTextColour(), SetFont() -- but no other ListItem
    methods. Obviously, being a virtual list, the rowFormatter cannot call any SetItem*
    method on the ListView itself.

    """

    def __init__(self, *args, **kwargs):

        # By default, virtual lists aren't sortable
        if "sortable" not in kwargs:
            kwargs["sortable"] = False

        AbstractVirtualObjectListView.__init__(self, *args, **kwargs)

    #----------------------------------------------------------------------------
    # Commands

    def AddObjects(self, modelObjects):
        """
        Add the given collections of objects to our collection of objects.

        This cannot work for virtual lists since the source of model objects is not
        under the control of the VirtualObjectListView.
        """
        pass


    def RemoveObjects(self, modelObjects):
        """
        Remove the given collections of objects from our collection of objects.

        This cannot work for virtual lists since the source of model objects is not
        under the control of the VirtualObjectListView.
        """
        pass


    def SelectObject(self, modelObject, deselectOthers=True):
        """
        Select the given modelObject. If deselectOthers is True, all other objects will be deselected

        This doesn't work for virtual lists, since the virtual list has no way
        of knowing where 'modelObject' is within the list.
        """
        pass


    def SelectObjects(self, modelObjects, deselectOthers=True):
        """
        Select all of the given modelObjects. If deselectOthers is True, all other modelObjects will be deselected

        This doesn't work for virtual lists, since the virtual list has no way
        of knowing where any of the modelObjects are within the list.
        """
        pass


    #----------------------------------------------------------------------------
    #  Sorting

    def _SortItemsNow(self):
        """
        Sort the items by our current settings.

        VirtualObjectListView can't sort anything by themselves, so this is a no-op.
        """
        pass

########################################################################

class FastObjectListView(AbstractVirtualObjectListView):
    """
    A fast object list view is a nice compromise between the functionality of an ObjectListView
    and the speed of a VirtualObjectListView.

    This class codes around the limitations of a virtual list. Specifically, it allows
    sorting and selection by object.
    """

    def __init__(self, *args, **kwargs):

        AbstractVirtualObjectListView.__init__(self, *args, **kwargs)

        self.SetObjectGetter(lambda index: self.innerList[index])

    #----------------------------------------------------------------------------
    # Commands

    def AddObjects(self, modelObjects):
        """
        Add the given collections of objects to our collection of objects.
        """
        self.modelObjects.extend(modelObjects)
        # We don't want to call RepopulateList() here since that makes the whole
        # control redraw, which flickers slightly, which I *really* hate! So we
        # most of the work of RepopulateList() but only redraw from the first
        # added object down.
        self._SortObjects()
        self._BuildInnerList()
        self.SetItemCount(len(self.innerList))

        # Find where the first added object appears and make that and everything
        # after it redraw
        first = self.GetItemCount()
        for x in modelObjects:
            # Because of filtering the added objects may not be in the list
            idx = self.GetIndexOf(x)
            if idx != -1:
                first = min(first, idx)
                if first == 0:
                    break

        if first < self.GetItemCount():
            self.RefreshItems(first, self.GetItemCount() - 1)

        # MAJ Footer
        if self.ctrl_footer :
            self.MAJ_footer()


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        self.lastGetObjectIndex = -1
        self._SortObjects()
        self._BuildInnerList()
        self.SetItemCount(len(self.innerList))
        self.RefreshObjects()
        
        # Auto-resize once all the data has been added
        self.AutoSizeColumns()
        
        # MAJ Footer
        if self.ctrl_footer :
            self.MAJ_footer()

    def RefreshObjects(self, aList=None):
        """
        Refresh all the objects in the given list
        """
        self.lastGetObjectIndex = -1
        # If no list is given, refresh everything
        if aList:
            for x in aList:
                idx = self.GetIndexOf(x)
                if idx != -1:
                    self.RefreshItem(idx)
        else:
            #self.RefreshItems(0, self.GetItemCount() - 1)
            if self.GetItemCount() > 0:
                self.RefreshItems(0, self.GetItemCount() - 1)

        # MAJ Footer
        if self.ctrl_footer :
            self.MAJ_footer()

    #----------------------------------------------------------------------------
    #  Accessing

    def _MapModelIndexToListIndex(self, modelIndex):
        """
        Return the index in the list where the given model index lives
        """

        # In a FastListView, the model index is the same as the list index
        return modelIndex

    #----------------------------------------------------------------------------
    #  Sorting

    def _SortItemsNow(self):
        """
        Sort the items by our current settings.

        FastObjectListView don't sort the items, they sort the model objects themselves.
        """
        selection = self.GetSelectedObjects()
        self._SortObjects()

        self.SelectObjects(selection)
        self.RefreshObjects()


class PanelAvecFooter(wx.Panel):
    def __init__(self, parent, listview=None, kwargs={}, dictColonnes={}, style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=-1, style=style)
        
        # Contrôles
        kwargs["parent"] = self
##        if kwargs.has_key("parent") == False : kwargs["parent"] = self # BUG ICI
        if kwargs.has_key("id") == False : kwargs["id"] = -1
        if kwargs.has_key("style") == False : kwargs["style"] = wx.LC_REPORT|wx.NO_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES
        
        self.ctrl_listview = listview(**kwargs)
        self.ctrl_listview.SetMinSize((10, 10)) 
        self.ctrl_footer = Footer.Footer(self)
        self.ctrl_listview.SetFooter(ctrl=self.ctrl_footer, dictColonnes=dictColonnes)
        
        # Layout
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add(self.ctrl_listview, 1, wx.ALL|wx.EXPAND, 0)
        sizerbase.Add(self.ctrl_footer, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(sizerbase)
        self.Layout()
        
    def GetListview(self):
        return self.ctrl_listview
        
    
#######################################################################

class GroupListView(FastObjectListView):
    """
    An ObjectListView that allows model objects to be organised into collapsable groups.

    GroupListView only work in report view.

    The appearance of the group headers are controlled by the 'groupFont', 'groupTextColour',
    and 'groupBackgroundColour' public variables.

    The images used for expanded and collapsed groups can be controlled by changing
    the images name 'ObjectListView.NAME_EXPANDED_IMAGE' and 'ObjectListView.NAME_COLLAPSED_IMAGE'
    respectfully. Like this::

        self.AddNamedImages(ObjectListView.NAME_EXPANDED_IMAGE, myOtherImage1)
        self.AddNamedImages(ObjectListView.NAME_COLLAPSED_IMAGE, myOtherImage2)

    Public variables:

    * putBlankLineBetweenGroups
        When this is True (the default), the list will be built so there is a blank
        line between groups.

    """

    #----------------------------------------------------------------------------
    # Creation

    def __init__(self, *args, **kwargs):
        """
        Create a GroupListView.

        Parameters:

        * showItemCounts

            If this is True (the default) Group title will include the count of the items
            that are within that group.

        * useExpansionColumn

            If this is True (the default), the expansion/contraction icon will have its
            own column at position 0. If this is false, the expand/contract icon will be
            in the first user specified column. This must be set before SetColumns() is called.
            If it is changed, SetColumns() must be called again.
        """
        self.groups = list()
        self.showGroups = True
        self.putBlankLineBetweenGroups = True
        self.alwaysGroupByColumnIndex = -1
        self.useExpansionColumn = kwargs.pop("useExpansionColumn", True)
        self.showItemCounts = kwargs.pop("showItemCounts", True)
        FastObjectListView.__init__(self, *args, **kwargs)

        # Setup default group characteristics
        font = self.GetFont()
        self.groupFont = wx.FFont(font.GetPointSize(), font.GetFamily(), wx.FONTFLAG_BOLD, font.GetFaceName())
        self.groupTextColour = wx.Colour(33, 33, 33, 255)
        self.groupBackgroundColour = wx.Colour(159, 185, 250, 249)

        self._InitializeImages()


    def _InitializeImages(self):
        """
        Initialize the images used to indicate expanded/collapsed state of groups.
        """
        def _makeBitmap(state, size):
            bitmap = wx.EmptyBitmap(size, size)
            dc = wx.MemoryDC(bitmap)
            dc.SetBackground(wx.Brush(self.groupBackgroundColour))
            dc.Clear()
            (x, y) = (0, 0)
            # The image under Linux is smaller and needs to be offset somewhat to look reasonable
            if wx.Platform == "__WXGTK__":
                (x, y) = (4, 4)
            wx.RendererNative.Get().DrawTreeItemButton(self, dc, (x, y, size, size), state)
            dc.SelectObject(wx.NullBitmap)
            return bitmap

        # If there isn't a small image list, make one
        if self.smallImageList is None:
            self.SetImageLists()

        size = self.smallImageList.GetSize()[0]
        self.AddNamedImages(ObjectListView.NAME_EXPANDED_IMAGE, _makeBitmap(wx.CONTROL_EXPANDED, size))
        self.AddNamedImages(ObjectListView.NAME_COLLAPSED_IMAGE, _makeBitmap(0, size))


    #----------------------------------------------------------------------------
    # Accessing

    def GetShowGroups(self):
        """
        Return whether or not this control is showing groups of objects or a straight list
        """
        return self.showGroups


    def SetShowGroups(self, showGroups=True):
        """
        Set whether or not this control is showing groups of objects or a straight list
        """
        if showGroups == self.showGroups:
            return

        self.showGroups = showGroups
        if not len(self.columns):
            return

        if showGroups:
            self.SetColumns(self.columns, False)
        else:
            if self.useExpansionColumn:
                self.SetColumns(self.columns[1:], False)

        self.SetObjects(self.modelObjects)


    def GetShowItemCounts(self):
        """
        Return whether or not the number of items in a groups should be included in the title
        """
        return self.showItemCounts


    def SetShowItemCounts(self, showItemCounts=True):
        """
        Set whether or not the number of items in a groups should be included in the title
        """
        if showItemCounts != self.showItemCounts:
            self.showItemCounts = showItemCounts
            self._BuildGroupTitles(self.groups, self.GetGroupByColumn())
            self._SetGroups(self.groups)


    def GetGroupByColumn(self):
        """
        Return the column by which the rows should be grouped
        """
        if self.alwaysGroupByColumnIndex >= 0:
            return self.GetAlwaysGroupByColumn()
        elif self.GetSortColumn() is None:
            return self.GetPrimaryColumn()
        else:
            return self.GetSortColumn()


    def GetAlwaysGroupByColumn(self):
        """
        Get the column by which the rows should be always be grouped.
        """
        try:
            return self.columns[self.alwaysGroupByColumnIndex]
        except IndexError:
            return None


    def SetAlwaysGroupByColumn(self, column):
        """
        Set the column by which the rows should be always be grouped.

        'column' can be None (which clears the setting), a ColumnDefn,
        or the index of the column desired
        """
        if column is None:
            self.alwaysGroupByColumnIndex = -1
        elif isinstance(column, ColumnDefn):
            try:
                self.alwaysGroupByColumnIndex = self.columns.index(column)
            except ValueError:
                self.alwaysGroupByColumnIndex = -1
        else:
            self.alwaysGroupByColumnIndex = column


    #----------------------------------------------------------------------------
    # Commands

    def AddObjects(self, modelObjects):
        """
        Add the given collections of objects to our collection of objects.
        """
        self.groups = None
        FastObjectListView.AddObjects(self, modelObjects)


    def CreateCheckStateColumn(self, columnIndex=0):
        """
        Create a fixed width column at the given index to show the checkedness
        of objects in this list.
        """
        # If the control is configured to have a separate expansion column,
        # the check state column has to come after that
        if self.useExpansionColumn and columnIndex == 0:
            columnIndex = 1
        FastObjectListView.CreateCheckStateColumn(self, columnIndex)


    def RemoveObjects(self, modelObjects):
        """
        Remove the given collections of objects from our collection of objects.
        """
        self.groups = None
        FastObjectListView.RemoveObjects(self, modelObjects)


    def SetColumns(self, columns, repopulate=True):
        """
        Set the columns for this control.
        """
        newColumns = columns[:]
        # Insert the column used for expansion and contraction (if one isn't already there)
        if self.showGroups and self.useExpansionColumn and len(newColumns) > 0:
            if not isinstance(newColumns[0], ColumnDefn) or not newColumns[0].isInternal:
                newColumns.insert(0, ColumnDefn("", fixedWidth=24, isEditable=False))
                newColumns[0].isInternal = True
        FastObjectListView.SetColumns(self, newColumns, repopulate)


    def SetGroups(self, groups):
        """
        Present the collection of ListGroups in this control.

        Calling this automatically put the control into ShowGroup mode
        """
        self.modelObjects = list()
        self.SetShowGroups(True)
        self._SetGroups(groups)


    def SetObjects(self, modelObjects, preserveSelection=False):
        """
        Set the list of modelObjects to be displayed by the control.
        """
        # Force our groups to be rebuilt, if we are supposd to be showing them
        if self.showGroups:
            self.groups = None
        else:
            self.groups = list()
        FastObjectListView.SetObjects(self, modelObjects, preserveSelection)


    #----------------------------------------------------------------------------
    # Building

    def _SetGroups(self, groups):
        """
        Present the collection of ListGroups in this control.
        """
        self.groups = groups
        self.RepopulateList()


    def RebuildGroups(self):
        """
        Completely rebuild our groups from our current list of model objects.

        Only use this if SetObjects() has been called. If you have specifically created
        your groups and called SetGroups(), do not use this method.
        """
        groups = self._BuildGroups()
        self.SortGroups(groups)
        self._SetGroups(groups)


    def _BuildGroups(self, modelObjects=None):
        """
        Partition the given list of objects into ListGroups depending on the given groupBy column.

        Returns the created collection of ListGroups
        """
        if modelObjects is None:
            modelObjects = self.modelObjects
        if self.filter:
            modelObjects = self.filter(modelObjects)

        groupingColumn = self.GetGroupByColumn()

        groupMap = {}
        for model in modelObjects:
            key = groupingColumn.GetGroupKey(model)
            group = groupMap.get(key)
            if group is None:
                groupMap[key] = group = ListGroup(key, groupingColumn.GetGroupKeyAsString(key))
            group.Add(model)

        groups = groupMap.values()

        if self.GetShowItemCounts():
            self._BuildGroupTitles(groups, groupingColumn)

        # Let the world know that we are creating the given groups
        evt = OLVEvent.GroupCreationEvent(self, groups)
        self.GetEventHandler().ProcessEvent(evt)

        return evt.groups


    def _BuildGroupTitles(self, groups, groupingColumn):
        """
        Rebuild the titles of the given groups
        """
        for x in groups:
            x.title = groupingColumn.GetGroupTitle(x, self.GetShowItemCounts())


    def _BuildInnerList(self):
        """
        Build the list that will be used to populate the ListCtrl.

        This internal list is an amalgum of model objects, ListGroups
        and None (which are blank rows).
        """
        self.objectToIndexMap = None
        if not self.showGroups:
            return ObjectListView._BuildInnerList(self)

        if not self.modelObjects:
            self.groups = list()
            self.innerList = list()
            return

        if self.groups is None:
            self.groups = self._BuildGroups()
            self.SortGroups()

        self.innerList = list()
        for grp in self.groups:
            if len(self.innerList) and self.putBlankLineBetweenGroups:
                self.innerList.append(None)
            self.innerList.append(grp)
            if grp.isExpanded:
                self.innerList.extend(grp.modelObjects)

    #----------------------------------------------------------------------------
    # Virtual list callbacks.
    # These are called a lot! Keep them efficient

    def OnGetItemText(self, itemIdx, colIdx):
        """
        Return the text that should be shown at the given cell
        """
        modelObject = self.innerList[itemIdx]

        if modelObject is None:
            return ""

        if isinstance(modelObject, ListGroup):
            if self.GetPrimaryColumnIndex() == colIdx:
                return modelObject.title
            else:
                return ""

        return self.GetStringValueAt(modelObject, colIdx)


    def OnGetItemImage(self, itemIdx):
        """
        Return the image index that should be shown on the primary column of the given item
        """
        # I don't think this method is ever called. Maybe in non-details views.
        modelObject = self.innerList[itemIdx]

        if modelObject is None:
            return -1

        if isinstance(modelObject, ListGroup):
            if modelObject.isExpanded:
                imageKey = ObjectListView.NAME_EXPANDED_IMAGE
            else:
                imageKey = ObjectListView.NAME_COLLAPSED_IMAGE
            return self.smallImageList.GetImageIndex(imageKey)

        return self.GetImageAt(modelObject, 0)


    def OnGetItemColumnImage(self, itemIdx, colIdx):
        """
        Return the image index at should be shown at the given cell
        """
        modelObject = self.innerList[itemIdx]

        if modelObject is None:
            return -1

        if isinstance(modelObject, ListGroup):
            if colIdx == 0:
                if modelObject.isExpanded:
                    imageKey = ObjectListView.NAME_EXPANDED_IMAGE
                else:
                    imageKey = ObjectListView.NAME_COLLAPSED_IMAGE
                return self.smallImageList.GetImageIndex(imageKey)
            else:
                return -1

        return self.GetImageAt(modelObject, colIdx)


    def OnGetItemAttr(self, itemIdx):
        """
        Return the display attributes that should be used for the given row
        """
        self.listItemAttr = wx.ListItemAttr()

        modelObject = self.innerList[itemIdx]

        if modelObject is None:
            return self.listItemAttr

        if isinstance(modelObject, ListGroup):
            # We have to keep a reference to the ListItemAttr or the garbage collector
            # will clear it up immeditately, before the ListCtrl has time to process it.
            if self.groupFont is not None:
                self.listItemAttr.SetFont(self.groupFont)
            if self.groupTextColour is not None:
                self.listItemAttr.SetTextColour(self.groupTextColour)
            if self.groupBackgroundColour is not None:
                self.listItemAttr.SetBackgroundColour(self.groupBackgroundColour)
            return self.listItemAttr

        return FastObjectListView.OnGetItemAttr(self, itemIdx)

    #----------------------------------------------------------------------------
    # Commands

    def ToggleExpansion(self, group):
        """
        Toggle the expanded/collapsed state of the given group and redisplay the list
        """
        self._DoExpandCollapse([group], not group.isExpanded)


    def Expand(self, group):
        """
        Expand the given group and redisplay the list
        """
        self._DoExpandCollapse([group], True)


    def Collapse(self, group):
        """
        Collapse the given group and redisplay the list
        """
        self._DoExpandCollapse([group], False)


    def ExpandAll(self, groups=None):
        """
        Expand the given groups (or all groups) and redisplay the list
        """
        if groups is None:
            groups = self.groups
        self._DoExpandCollapse(groups, True)


    def CollapseAll(self, groups=None):
        """
        Collapse the given groups (or all groups) and redisplay the list
        """
        if groups is None:
            groups = self.groups
        self._DoExpandCollapse(groups, False)


    def _DoExpandCollapse(self, groups, isExpanding):
        """
        Do the real work of expanding/collapsing the given groups
        """
        # Cull groups that aren't going to change
        groups = [x for x in groups if x.isExpanded != isExpanding]
        if not groups:
            return

        # Let the world know that the given groups are about to be expanded/collapsed
        evt = OLVEvent.ExpandingCollapsingEvent(self, groups, isExpanding)
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed():
            return

        # Expand/contract the groups, then put those changes into effect
        for x in evt.groups:
            x.isExpanded = isExpanding
        self._BuildInnerList()
        self.SetItemCount(len(self.innerList))

        # Refresh eveything from the first group down
        i = min([self.GetIndexOf(x) for x in evt.groups])
        self.RefreshItems(i, len(self.innerList)-1)

        # Let the world know that the given groups have been expanded/collapsed
        evt = OLVEvent.ExpandedCollapsedEvent(self, evt.groups, isExpanding)
        self.GetEventHandler().ProcessEvent(evt)


    def Reveal(self, modelObject):
        """
        Ensure that the given modelObject is visible, expanding the group it belongs to,
        if necessary
        """
        # If it is already there, just make sure it is visible
        i = self.GetIndexOf(modelObject)
        if i != -1:
            self.EnsureVisible(i)
            return True

        # Find which group (if any) the object belongs to, and
        # expand it and then try to reveal it again
        for group in self.groups:
            if not group.isExpanded and modelObject in group.modelObjects:
                self.Expand(group)
                return self.Reveal(modelObject)

        return False


    def SelectAll(self):
        """
        Selected all model objects in the control.

        In a GroupListView, this does not select blank lines or groups
        """
        self.SetItemState(-1, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        for (i, x) in enumerate(self.innerList):
            if x is None or isinstance(x, ListGroup):
                self.SetItemState(i, 0, wx.LIST_STATE_SELECTED)

    # With the current implemetation, these are synonyms
    SelectGroup = ObjectListView.SelectObject
    SelectGroups = ObjectListView.SelectObjects


    #----------------------------------------------------------------------------
    # Accessing

    def FindGroupFor(self, modelObject):
        """
        Return the group that contains the given object or None if the given
        object is not found
        """
        for group in self.groups:
            if modelObject in group.modelObjects:
                return group
        return None


    def GetSelectedGroups(self):
        """
        Return a list of the groups that are selected
        """
        selectedGroups = list()
        i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while i != -1:
            model = self.innerList[i]
            if isinstance(model, ListGroup):
                selectedGroups.append(model)
            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        return selectedGroups


    def GetFilteredObjects(self):
        """
        Return the model objects that are actually displayed in the control.
        """
        objects = list()
        for x in self.groups:
            objects.extend(x.modelObjects)
        return objects


    def GetObjectAt(self, index):
        """
        Return the model object at the given row of the list.

        With GroupListView, this method can return None, since the given
        index may be a blank row or a group header. These do not have
        corresponding model objects.
        """
        try:
            model = self.innerList[index]
            if isinstance(model, ListGroup):
                model = None
        except IndexError:
            model = None

        return model


    def YieldSelectedObjects(self):
        """
        Progressively yield the selected modelObjects.

        Only return model objects, not blank lines or ListGroups
        """
        i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while i != -1:
            model = self.GetObjectAt(i)
            if model is not None:
                yield model
            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)


    def _CanUseBisect(self, searchColumn):
        """
        Return True if we can use binary search on the given column.

        A GroupListView can never use binary search since its rows aren't sorted.
        """
        return not self.showGroups


    def _GetValuesAsMultiList(self, objects):
        """
        Return a list of lists of the string of the aspects of the given objects
        """
        cols = self.columns[self.GetPrimaryColumnIndex():] # We don't want to copy the expand icon columns
        objects = [x for x in objects if x is not None and not isinstance(x, ListGroup)]
        return [[column.GetStringValue(x) for column in cols] for x in objects]


    #----------------------------------------------------------------------------
    # Event handlers

    def _HandleChar(self, evt):

        if not self.IsCellEditing() and self.handleStandardKeys:
            if (evt.GetKeyCode() == wx.WXK_LEFT):
                self.CollapseAll(self.GetSelectedGroups())
                return
            if (evt.GetKeyCode() == wx.WXK_RIGHT):
                self.ExpandAll(self.GetSelectedGroups())
                return

        FastObjectListView._HandleChar(self, evt)


    def _HandleColumnClick(self, evt):
        """
        The user has clicked on a column title
        """

        # If they click on a new column, we have to rebuild our groups
        if evt.GetColumn() != self.sortColumnIndex:
            self.groups = None

        FastObjectListView._HandleColumnClick(self, evt)


    def _HandleLeftDownOnImage(self, rowIndex, subItemIndex):
        """
        Handle a left click on the image at the given cell
        """
        self._PossibleFinishCellEdit()

        listObject = self.innerList[rowIndex]
        if subItemIndex == 0 and isinstance(listObject, ListGroup):
            self.ToggleExpansion(listObject)
        else:
            FastObjectListView._HandleLeftDownOnImage(self, rowIndex, subItemIndex)


    #---Sorting-------------------------------------------------------#000000#FFFFFF

    def SortGroups(self, groups=None, ascending=None):
        """
        Sort the given collection of groups in the given direction (defaults to ascending).

        The model objects within each group will be sorted as well
        """
        if groups is None:
            groups = self.groups
        if ascending is None:
            ascending = self.sortAscending

        # If the groups are locked, we sort by the sort column, otherwise by the grouping column.
        # The primary column is always used as a secondary sort key.
        if self.GetAlwaysGroupByColumn():
            sortCol = self.GetSortColumn()
        else:
            sortCol = self.GetGroupByColumn()

        # Let the world have a change to sort the items
        evt = OLVEvent.SortGroupsEvent(self, groups, sortCol, ascending)
        self.GetEventHandler().ProcessEvent(evt)
        if evt.wasHandled:
            return

        # Sorting event wasn't handled, so we do the default sorting
        def _getLowerCaseKey(group):
            try:
                return group.key.lower()
            except:
                return group.key

        groups.sort(key=_getLowerCaseKey, reverse=(not ascending))

        # Sort the model objects within each group.
        for x in groups:
            self._SortObjects(x.modelObjects, sortCol, self.GetPrimaryColumn())


    def _SortItemsNow(self):
        """
        Sort the items by our current settings.

        GroupListViews don't sort the items directly. We have to sort the groups
        and then rebuild the list.
        """
        if not self.showGroups:
            return FastObjectListView._SortItemsNow(self)

        if self.groups is None:
            self.groups = self._BuildGroups()
        self.SortGroups(self.groups)
        self._SetGroups(self.groups)


    #def _FormatAllRows(self):
    #    """
    #    GroupListViews don't need this method.
    #    """
    #    pass



#######################################################################

class ListGroup(object):
    """
    A ListGroup is a partition of model objects that can be presented
    under a collapsible heading in a GroupListView.
    """

    def __init__(self, key, title, isExpanded=True):
        self.key = key
        self.title = title

        self.isExpanded = isExpanded
        self.modelObjects = list()


    def Add(self, model):
        """
        Add the given model to those that belong to this group.
        """
        self.modelObjects.append(model)


#######################################################################

class ColumnDefn(object):
    """
    A ColumnDefn controls how one column of information is sourced and formatted.

    Much of the intelligence and ease of use of an ObjectListView comes from the column
    definitions. It is worthwhile gaining an understanding of the capabilities of this class.

    Public Attributes (alphabetically):

    * align
        How will the title and the cells of the this column be aligned. Possible
        values: 'left', 'centre', 'right'

    * cellEditorCreator
        This is a callable that will be invoked to create an editor for value in this
        column. The callable should accept three parameters: the objectListView starting
        the edit, the rowIndex and the subItemIndex. It should create and return a Control
        that is capable of editing the value.

        If this is None, a cell editor will be chosen based on the type of objects in this
        column (See CellEditor.EditorRegistry).

    * freeSpaceProportion
        If the column is space filling, this attribute controls what proportion of the
        space should be given to this column. By default, all spacing filling column share
        the free space equally. By changing this attribute, a column can be given a larger
        proportion of the space.

    * groupKeyConverter
        The groupKeyConverter converts a group key into the string that can be presented
        to the user. This string will be used as part of the title for the group.

        Its behaviour is the same as "stringConverter."

    * groupKeyGetter
        When this column is used to group the model objects, what groupKeyGetter extracts
        the value from each model that will be used to partition the model objects into
        groups.

        Its behaviour is the same as "valueGetter."

        If this is None, the value returned by valueGetter will be used.

    * groupTitleSingleItem
        When a group is created that contains a single item, and the GroupListView
        has "showItemCounts" turned on, this string will be used to create the title
        of the group. The string should contain two placeholder: %(title)s and %(count)d.
        Example: "%(title)s [only %(count)d song]"

    * groupTitlePluralItems
        When a group is created that contains 0 items or >1 items, and the GroupListView
        has "showItemCounts" turned on, this string will be used to create the title
        of the group. The string should contain two placeholder: %(title)s and %(count)d.
        Example: "%(title)s [%(count)d songs]"

    * headerImage
        The index or name of the image that will be shown against the column header.
        Remember, a column header can only show one image at a time, so if the column
        is the sort column, it will show the sort indicator -- not this headerImage.

    * imageGetter
        A string, callable or integer that is used to get a index of the image to be
        shown in a cell.

        Strings and callable are used as for the `valueGetter` attribute.

        Integers are treated as constants (that is, all rows will have the same
        image).

    * isEditable
        Can the user edit cell values in this column? Default is True

    * isSearchable
        If this column is the sort column, when the user types into the ObjectListView,
        will a match be looked for using values from this column? If this is False,
        values from column 0 will be used.
        Default is True.

    * isSpaceFilling
        Is this column a space filler? Space filling columns resize to occupy free
        space within the listview. As the listview is expanded, space filling columns
        expand as well. Conversely, as the control shrinks these columns shrink too.

        Space filling columns can disappear (i.e. have a width of 0) if the control
        becomes too small. You can set `minimumWidth` to prevent them from
        disappearing.

    * maximumWidth
        An integer indicate the number of pixels above which this column will not resize.
        Default is -1, which means there is no limit.

    * minimumWidth
        An integer indicate the number of pixels below which this column will not resize.
        Default is -1, which means there is no limit.

    * useBinarySearch
        If isSearchable and useBinarySearch are both True, the ObjectListView will use a
        binary search algorithm to locate a match. If useBinarySearch is False, a simple
        linear search will be done.

        The binary search can quickly search large numbers of rows (10,000,000 in about 25
        comparisons), which makes them ideal for virtual lists. However, there are two
        constraints:

            - the ObjectListView must be sorted by this column

            - sorting by string representation must give the same ordering as sorting
              by the aspect itself.

        The second constraint is necessary because the user types characters expecting
        them to match the string representation of the data. The binary search will make
        its decisions using the string representation, but the rows ordered
        by aspect value. This will only work if sorting by string representation
        would give the same ordering as sorting by the aspect value.

        In general, binary searches work with strings, YYYY-MM-DD dates, and booleans.
        They do not work with numerics or other date formats.

        If either of these constrains are not true, you must set
        useBinarySearch to False and be content with linear searches. Otherwise, the
        searching will not work correctly.

    * stringConverter
        A string or a callable that will used to convert a cells value into a presentation
        string.

        If it is a callble, it will be called with the value for the cell and must return
        a string.

        If it is a string, it will be used as a format string with the % operator, e.g.
        "self.stringConverter % value." For dates and times, the stringConverter will be
        passed as the first parameter to the strftime() method on the date/time.

    * title
        A string that will be used as the title of the column in the listview

    * valueGetter
        A string, callable or integer that is used to get the value to be displayed in
        a cell. See _Munge() for details on how this attribute is used.

        A callable is simply called and the result is the value for the cell.

        The string can be the name of a method to be invoked, the name of an attribute
        to be fetched, or (for dictionary like objects) an index into the dictionary.

        An integer can only be used for list-like objects and is used as an index into
        the list.

    * valueSetter
        A string, callable or integer that is used to write an edited value back into the
        model object.

        A callable is called with the model object and the new value. Example::

            myCol.valueSetter(modelObject, newValue)

        An integer can only be used if the model object is a mutable sequence. The integer
        is used as an index into the list. Example::

            modelObject[myCol.valueSetter] = newValue

        The string can be:

        * the name of a method to be invoked, in which case the method should accept the
          new value as its parameter. Example::

            method = getattr(modelObject, myCol.valueSetter)
            method(newValue)

        * the name of an attribute to be updated. This attribute will not be created: it
          must already exist. Example::

            setattr(modelObject, myCol.valueSetter, newValue)

        * for dictionary like model objects, an index into the dictionary. Example::

            modelObject[myCol.valueSetter] = newValue

    * useInitialLetterForGroupKey
        When this is true and the group key for a row is a string, only the first letter of
        the string will be considered as the group key. This is often useful for grouping
        row when the column contains a name.

    * width
        How many pixels wide will the column be? -1 means auto size to contents. For a list with
        thousands of items, autosize can be noticably slower than specifically setting the size.


    The `title`, `align` and `width` attributes are only references when the column definition is given to the
    ObjectListView via the `SetColumns()` or `AddColumnDefn()` methods. The other attributes are referenced
    intermittently -- changing them will change the behaviour of the `ObjectListView`.

    Without a string converter, None will be converted to an empty string. Install a string converter ('%s'
    will suffice) if you want to see the 'None' instead.

    BUG: Double-clicking on a divider (under Windows) can resize a column beyond its minimum and maximum widths.
    """

    def __init__(self, title="title", align="left", width=-1,
                 valueGetter=None, imageGetter=None, stringConverter=None, valueSetter=None, isEditable=True,
                 fixedWidth=None, minimumWidth=-1, maximumWidth=-1, isSpaceFilling=False,
                 cellEditorCreator=None, autoCompleteCellEditor=False, autoCompleteComboBoxCellEditor=False,
                 checkStateGetter=None, checkStateSetter=None,
                 isSearchable=True, useBinarySearch=None, headerImage=-1,
                 groupKeyGetter=None, groupKeyConverter=None, useInitialLetterForGroupKey=False,
                 groupTitleSingleItem=None, groupTitlePluralItems=None, visible=True, typeDonnee=None):
        """
        Create a new ColumnDefn using the given attributes.

        The attributes behave as described in the class documentation, except for:

        * fixedWidth
            An integer which indicates that this column has the given width and is not resizable.
            Useful for column that always display fixed with data (e.g. a single icon). Setting this
            parameter overrides the width, minimumWidth and maximumWidth parameters.

        * autoCompleteCellEditor
            If this is True, the column will use an autocomplete TextCtrl when
            values of this column are edited. This overrules the cellEditorCreator parameter.

        * autoCompleteComboBoxCellEditor
            If this is True, the column will use an autocomplete ComboBox when
            values of this column are edited. This overrules the cellEditorCreator parameter.
        """
        self.title = title
        self.align = align
        self.valueGetter = valueGetter
        self.imageGetter = imageGetter
        self.stringConverter = stringConverter
        self.valueSetter = valueSetter
        self.isSpaceFilling = isSpaceFilling
        self.cellEditorCreator = cellEditorCreator
        self.freeSpaceProportion = 1
        self.isEditable = isEditable
        self.isSearchable = isSearchable
        self.useBinarySearch = useBinarySearch
        self.headerImage = headerImage
        self.groupKeyGetter = groupKeyGetter
        self.groupKeyConverter = groupKeyConverter
        self.useInitialLetterForGroupKey = useInitialLetterForGroupKey
        self.groupTitleSingleItem = groupTitleSingleItem or "%(title)s (%(count)d item)"
        self.groupTitlePluralItems = groupTitlePluralItems or "%(title)s (%(count)d items)"
        self.isInternal = False # was this column created internally by ObjectListView?
        self.visible = visible
        self.typeDonnee = typeDonnee

        self.minimumWidth = minimumWidth
        self.maximumWidth = maximumWidth
        self.width = self.CalcBoundedWidth(width)
        
        # Adaptation pour linux
        if self.width <= 22 and "linux" in sys.platform :
            self.width += 30
        
        if fixedWidth is not None:
            self.SetFixedWidth(fixedWidth)

        if autoCompleteCellEditor:
            self.cellEditorCreator = lambda olv, row, col: CellEditor.MakeAutoCompleteTextBox(olv, col)

        if autoCompleteComboBoxCellEditor:
            self.cellEditorCreator = lambda olv, row, col: CellEditor.MakeAutoCompleteComboBox(olv, col)

        self.checkStateGetter = checkStateGetter
        self.checkStateSetter = checkStateSetter

    #-------------------------------------------------------------------------------
    # Column properties

    def GetAlignment(self):
        """
        Return the alignment that this column uses
        """
        alignment = {
            "l": wx.LIST_FORMAT_LEFT,
            "c": wx.LIST_FORMAT_CENTRE,
            "r": wx.LIST_FORMAT_RIGHT
        }.get(self.align[:1], wx.LIST_FORMAT_LEFT)

        return alignment

    def GetAlignmentForText(self):
        """
        Return the alignment of this column in a form that can be used as
        a style flag on a text control
        """
        return {
            "l": wx.TE_LEFT,
            "c": wx.TE_CENTRE,
            "r": wx.TE_RIGHT,
        }.get(self.align[:1], wx.TE_LEFT)

    #-------------------------------------------------------------------------------
    # Value accessing

    def GetValue(self, modelObject):
        """
        Return the value for this column from the given modelObject
        """
        return self._Munge(modelObject, self.valueGetter)


    def GetStringValue(self, modelObject):
        """
        Return a string representation of the value for this column from the given modelObject
        """
        value = self.GetValue(modelObject)
        return self._StringToValue(value, self.stringConverter)


    def _StringToValue(self, value, converter):
        """
        Convert the given value to a string, using the given converter
        """
        try:
            return converter(value)
        except TypeError:
            pass

        if converter and isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value.strftime(self.stringConverter)

        # By default, None is changed to an empty string.
        if not converter and not value:
            return ""

        fmt = converter or "%s"
        try:
            return fmt % value
        except UnicodeError:
            return unicode(fmt) % value


    def GetGroupKey(self, modelObject):
        """
        Return the group key for this column from the given modelObject
        """
        if self.groupKeyGetter is None:
            key = self.GetValue(modelObject)
        else:
            key = self._Munge(modelObject, self.groupKeyGetter)
        if self.useInitialLetterForGroupKey:
            try:
                return key[:1].upper()
            except TypeError:
                return key
        else:
            return key


    def GetGroupKeyAsString(self, groupKey):
        """
        Return the given group key as a human readable string
        """
        # If there is no group key getter, we must have the normal aspect value. So if
        # there isn't a special key converter, use the normal aspect to string converter.
        if self.groupKeyGetter is None and self.groupKeyConverter is None:
            return self._StringToValue(groupKey, self.stringConverter)
        else:
            return self._StringToValue(groupKey, self.groupKeyConverter)


    def GetGroupTitle(self, group, useItemCount):
        """
        Return a title of the group
        """
        title = self.GetGroupKeyAsString(group.key)
        if useItemCount:
            objectCount = len(group.modelObjects)
            if objectCount == 1:
                fmt = self.groupTitleSingleItem
            else:
                fmt = self.groupTitlePluralItems
            title = fmt % {"title":title, "count":objectCount}
        return title


    def GetImage(self, modelObject):
        """
        Return the image index for this column from the given modelObject. -1 means no image.
        """
        if self.imageGetter is None:
            return -1

        if isinstance(self.imageGetter, int):
            return self.imageGetter

        idx = self._Munge(modelObject, self.imageGetter)
        if idx is None:
            return -1
        else:
            return idx


    def SetValue(self, modelObject, value):
        """
        Set this columns aspect of the given modelObject to have the given value.
        """
        if self.valueSetter is None:
            return self._SetValueUsingMunger(modelObject, value, self.valueGetter, False)
        else:
            return self._SetValueUsingMunger(modelObject, value, self.valueSetter, True)


    def _SetValueUsingMunger(self, modelObject, value, munger, shouldInvokeCallable):
        """
        Look for ways to update modelObject with value using munger. If munger finds a
        callable, it will be called if shouldInvokeCallable == True.
        """
        # If there isn't a munger, we can't do anything
        if munger is None:
            return

        # Is munger a function?
        if callable(munger):
            if shouldInvokeCallable:
                munger(modelObject, value)
            return

        # Try indexed access for dictionary or list like objects
        try:
            modelObject[munger] = value
            return
        except:
            pass

        # Is munger the name of some slot in the modelObject?
        try:
            attr = getattr(modelObject, munger)
        except TypeError:
            return
        except AttributeError:
            return

        # Is munger the name of a method?
        if callable(attr):
            if shouldInvokeCallable:
                attr(value)
            return

        # If we get to here, it seems that munger is the name of an attribute or
        # property on modelObject. Try to set, realising that many things could still go wrong.
        try:
            setattr(modelObject, munger, value)
        except:
            pass


    def _Munge(self, modelObject, munger):
        """
        Wrest some value from the given modelObject using the munger.
        With a description like that, you know this method is going to be obscure :-)

        'munger' can be:

        1) a callable.
           This method will return the result of executing 'munger' with 'modelObject' as its parameter.

        2) the name of an attribute of the modelObject.
           If that attribute is callable, this method will return the result of executing that attribute.
           Otherwise, this method will return the value of that attribute.

        3) an index (string or integer) onto the modelObject.
           This allows dictionary-like objects and list-like objects to be used directly.
        """
        if munger is None:
            return None

        # THINK: The following code treats an instance variable with the value of None
        # as if it doesn't exist. Is that best?

        # Try attribute access
        try:
            attr = getattr(modelObject, munger, None)
            if attr is not None:
                try:
                    return attr()
                except TypeError:
                    return attr
        except TypeError:
            # Happens when munger is not a string
            pass

        # Use the callable directly, if possible.
        # In accordance with Guido's rules for Python 3, we just call it and catch the
        # exception
        try:
            return munger(modelObject)
        except TypeError:
            pass

        # Try dictionary-like indexing
        try:
            return modelObject[munger]
        except:
            return None

    #-------------------------------------------------------------------------------
    # Width management

    def CalcBoundedWidth(self, width):
        """
        Calculate the given width bounded by the (optional) minimum and maximum column widths
        """

        # Values of < 0 have special meanings, so just return them
        if width < 0:
            return width

        if self.maximumWidth >= 0:
            width = min(self.maximumWidth, width)
        return max(self.minimumWidth, width)


    def IsFixedWidth(self):
        """
        Is this column fixed width?
        """
        return self.minimumWidth != -1 and \
               self.maximumWidth != -1 and \
               (self.minimumWidth >= self.maximumWidth)


    def SetFixedWidth(self, width):
        """
        Make this column fixed width
        """
        self.width = self.minimumWidth = self.maximumWidth = width

    #----------------------------------------------------------------------------
    # Check state

    def HasCheckState(self):
        """
        Return if this column is showing a check box?
        """
        return self.checkStateGetter is not None


    def GetCheckState(self, modelObject):
        """
        Return the check state of the given model object
        """
        if self.checkStateGetter is None:
            return None
        else:
            return self._Munge(modelObject, self.checkStateGetter)


    def SetCheckState(self, modelObject, state):
        """
        Set the check state of the given model object
        """
        if self.checkStateSetter is None:
            return self._SetValueUsingMunger(modelObject, state, self.checkStateGetter, False)
        else:
            return self._SetValueUsingMunger(modelObject, state, self.checkStateSetter, True)

#======================================================================

class NamedImageList(object):
    """
    A named image list is an Adaptor that gives a normal image list
    the ability to reference images by name, rather than just index
    """

    def __init__(self, imageList=None, imageSize=16):
        """
        """
        self.imageList = imageList or wx.ImageList(imageSize, imageSize)
        self.imageSize = imageSize
        self.nameToImageIndexMap = {}


    def GetSize(self, ignored=None):
        """
        Return a pair that represents the size of the image in this list
        """
        # Mac and Linux have trouble getting the size of empty image lists
        if self.imageList.GetImageCount() == 0:
            return (self.imageSize, self.imageSize)
        else:
            return self.imageList.GetSize(0)


    def AddNamedImage(self, name, image):
        """
        Add the given image to our list, and remember its name.
        Returns the images index.
        """
        imageIndex = self.imageList.Add(image)
        if name is not None:
            self.nameToImageIndexMap[name] = imageIndex
        return imageIndex


    def HasName(self, name):
        """
        Does this list have an image with the given name?"
        """
        return name in self.nameToImageIndexMap


    def GetImageIndex(self, name):
        """
        Return the image with the given name, or -1 if it doesn't exist
        """
        return self.nameToImageIndexMap.get(name, -1)

#======================================================================

class BatchedUpdate(object):
    """
    This class is an *Adapter* around an ``ObjectListView`` which ensure that the list is updated, at most,
    once every *N* seconds.

    Usage::

        self.olv2 = BatchedUpdate(self.olv, 3)
        # Now use olv2 in place of olv, and the list will only be updated at most once
        # every 3 second, no many how many calls are made to it.

    This is useful for a certain class of problem where model objects are update frequently -- more
    frequently than you wish to update the control. A backup program may be able to backup several
    files a second, but does not wish to update the list ctrl that often. A packet sniffer will
    receive hundreds of packets per second, but should not try to update the list ctrl for each
    packet. A batched update adapter solves situations like these in a trivial manner.

    This class only intercepts the following messages:
        * ``AddObject()``, ``AddObjects()``
        * ``RefreshObject()``, ``RefreshObjects()``
        * ``RemoveObject()``, ``RemoveObjects()``
        * ``RepopulateList()``
        * ``SetObjects()``

    All other message are passed directly to the ``ObjectListView`` and are thus unbatched. This means
    that sorting and changes to columns are unbatched and will take effect immediately.

    You need to be a little careful when using batched updates. There are at least two things
    you need to avoid, or at least be careful about:

    1) Don't mix batched and unbatched updates. If you go behind the back of the batched update
       wrapper and make direct changes to the underlying control, you will probably get bitten by
       difficult-to-reproduce bugs. For example::

            self.olvBatched.SetObjects(objects) # Batched update
            self.olvBatched.objectlistView.AddObject(aModel) # unbatched update

       This will almost certainly not do what you expect, or at best, will only sometimes do
       what you want.

    2) You cannot assume that objects will immediately appear in the list and
       thus be available for further operations. For example::

            self.olv.AddObject(aModel)
            self.olv.Check(aModel)

       If *self.olv* is a batched update adapter, this code *may* not work since the
       ``AddObject()`` might not have yet taken effect, so the ``Check()`` will not find
       *aModel* in the control. Worse, it may work most of the time and fail only occassionally.

       If you need to be able to do further processing on objects just added, it would be better
       not to use a batched adapter.

    """

    # For SetObjects(), None and empty list are both possible valid values so we need a
    # non-valid value that indicates that SetObjects() has not been called
    NOT_SET = -1

    def __init__(self, objectListView, updatePeriod=0):
        self.objectListView = objectListView # Must not be None
        self.updatePeriod = updatePeriod

        self.objectListView.Bind(wx.EVT_IDLE, self._HandleIdle)

        self.newModelObjects = BatchedUpdate.NOT_SET
        self.objectsToAdd = list()
        self.objectsToRefresh = list()
        self.objectsToRemove = list()
        self.freezeUntil = 0


    def __getattr__(self, name):
        """
        Forward any unknown references to the original objectListView.

        This is what allows us to pretend to be an ObjectListView.
        """
        return getattr(self.objectListView, name)


    def RepopulateList(self):
        """
        Remember the given model objects so that they can be displayed when the next update cycle occurs
        """
        if self.freezeUntil < time.clock():
            self.objectListView.RepopulateList()
            self.freezeUntil = time.clock() + self.updatePeriod
            return

        self.newModelObjects = self.objectListView.modelObjects
        self.objectsToRefresh = list()

        # Unlike SetObjects(), refreshing the list does NOT invalidate the objects to be added/removed


    def SetObjects(self, modelObjects):
        """
        Remember the given model objects so that they can be displayed when the next update cycle occurs
        """
        if self.freezeUntil < time.clock():
            self.objectListView.SetObjects(modelObjects)
            self.freezeUntil = time.clock() + self.updatePeriod
            return

        self.newModelObjects = modelObjects
        # Explicitly setting the objects to be shown renders void any previous Add/Refresh/Remove commands
        self.objectsToAdd = list()
        self.objectsToRefresh = list()
        self.objectsToRemove = list()


    def AddObject(self, modelObject):
        """
        Add the given object to our collection of objects.

        The object will appear at its sorted location, or at the end of the list if
        the list is unsorted
        """
        self.AddObjects([modelObject])


    def AddObjects(self, modelObjects):
        """
        Remember the given model objects so that they can be added when the next update cycle occurs
        """
        if self.freezeUntil < time.clock():
            self.objectListView.AddObjects(modelObjects)
            self.freezeUntil = time.clock() + self.updatePeriod
            return

        # TODO: We should check that none of the model objects is already in the list
        self.objectsToAdd.extend(modelObjects)

        # Since we are adding these objects, we must no longer remove them
        if self.objectsToRemove:
            for x in modelObjects:
                self.objectsToRemove.remove(x)


    def RefreshObject(self, modelObject):
        """
        Refresh the display of the given model
        """
        self.RefreshObjects([modelObject])


    def RefreshObjects(self, modelObjects):
        """
        Refresh the information displayed about the given model objects
        """
        if self.freezeUntil < time.clock():
            self.objectListView.RefreshObjects(modelObjects)
            self.freezeUntil = time.clock() + self.updatePeriod
            return

        self.objectsToRefresh.extend(modelObjects)


    def RemoveObject(self, modelObjects):
        """
        Remember the given model objects so that they can be removed when the next update cycle occurs
        """
        self.RemoveObjects([modelObject])


    def RemoveObjects(self, modelObjects):
        """
        Remember the given model objects so that they can be removed when the next update cycle occurs
        """
        if self.freezeUntil < time.clock():
            self.objectListView.RemoveObjects(modelObjects)
            self.freezeUntil = time.clock() + self.updatePeriod
            return

        self.objectsToRemove.extend(modelObjects)

        # Since we are removing these objects, we must no longer add them
        if self.objectsToAdd:
            for x in modelObjects:
                self.objectsToAdd.remove(x)

    #----------------------------------------------------------------------------
    # Event processing

    def _HandleIdle(self, evt):
        """
        The app is idle. Process any outstanding requests
        """
        if (self.newModelObjects != BatchedUpdate.NOT_SET or
            self.objectsToAdd or
            self.objectsToRefresh or
            self.objectsToRemove):
            if self.freezeUntil < time.clock():
                self._ApplyChanges()
            else:
                evt.RequestMore()

    def _ApplyChanges(self):
        """
        Apply any batched changes to the list
        """
        if self.newModelObjects != BatchedUpdate.NOT_SET:
            self.objectListView.SetObjects(self.newModelObjects)

        if self.objectsToAdd:
            self.objectListView.AddObjects(self.objectsToAdd)

        if self.objectsToRemove:
            self.objectListView.RemoveObjects(self.objectsToRemove)

        if self.objectsToRefresh:
            self.objectListView.RefreshObjects(self.objectsToRefresh)

        self.newModelObjects = BatchedUpdate.NOT_SET
        self.objectsToAdd = list()
        self.objectsToRemove = list()
        self.objectsToRefresh = list()
        self.freezeUntil = time.clock() + self.updatePeriod

#----------------------------------------------------------------------------
# Built in images so clients don't have to do the same

import cStringIO, zlib

def _getSmallUpArrowData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4[z\xba8\x86X\xf4&\
\xa7\xa4$\xa5-`1\x08\\R\xcd"\x11\x10\x1f\xfe{~\x0es\xc2,N\xc9\xa6\xab\x0c%\
\xbe?x\x0e\x1a0LO\x8ay\xe4sD\xe3\x90\xfay\x8bYB\xec\x8d\x8c\x0c\xc1\x01b9\
\xe1\xbc\x8fw\x01\ra\xf0t\xf5sY\xe7\x94\xd0\x04\x00\xb7\x89#\xbb' )

def _getSmallUpArrowBitmap():
    stream = cStringIO.StringIO(_getSmallUpArrowData())
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

def _getSmallDownArrowData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4\x07x\xba8\x86X\xf4\
&\xa7\xa4$\xa5-`1\x08\\R}\x85\x81\r\x04\xc4R\xfcjc\xdf\xd6;II\xcd\x9e%Y\xb8\
\x8b!v\xd2\x844\x1e\xe6\x0f\x92M\xde2\xd9\x12\x0b\xb4\x8f\xbd6rSK\x9b\xb3c\
\xe1\xc2\x87\xf6v\x95@&\xdb\xb1\x8bK|v22,W\x12\xd0\xdb-\xc4\xe4\x044\x9b\xc1\
\xd3\xd5\xcfe\x9dSB\x13\x00$1+:' )

def _getSmallDownArrowBitmap():
    stream = cStringIO.StringIO(_getSmallDownArrowData())
    return wx.BitmapFromImage(wx.ImageFromStream(stream))


#
#######################################################################
# TESTING ONLY

if __name__ == '__main__':
    pass
