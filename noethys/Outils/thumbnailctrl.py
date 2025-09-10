#!/usr/bin/env python
# -*- coding: utf-8 -*-

# THUMBNAILCTRL Control wxPython IMPLEMENTATION
# Python Code By:
#
# Andrea Gavana And Peter Damoc, @ 12 Dec 2005
# Latest Revision: 01 Dec 2009, 10.00 GMT
#
#
# TODO List/Caveats
#
# 1. Thumbnail Creation/Display May Be Somewhat Improved From The Execution
#    Speed Point Of View;
#
# 2. The Implementation For wx.HORIZONTAL Style Is Still To Be Written;
#
# 3. I Have No Idea On How To Implement Thumbnails For Audio, Video And Other Files.
#
# 4. Other Ideas?
#
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To Me At:
#
# andrea.gavana@gmail.com
# gavana@kpo.kz
#
# Or, Obviously, To The wxPython Mailing List!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------- #


"""
Thumbnailctrl is a widget that can be used to display a series of images in
a "thumbnail" format.


Description
===========

Thumbnailctrl is a widget that can be used to display a series of images in
a "thumbnail" format; it mimics, for example, the windows explorer behavior
when you select the "view thumbnails" option.
Basically, by specifying a folder that contains some image files, the files
in the folder are displayed as miniature versions of the actual images in
a `wx.ScrolledWindow`.

The code is partly based on wxVillaLib, a wxWidgets implementation of this
control. However, ThumbnailCtrl wouldn't have been so fast and complete
without the suggestions and hints from Peter Damoc. So, if he accepts the
mention, this control is his as much as mine.


Usage
=====

Sample construction::

    ThumbnailCtrl.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                           size=wx.DefaultSize, thumboutline=THUMB_OUTLINE_RECT,
                           thumbfilter=THUMB_FILTER_IMAGES)


Methods and Settings
====================

With ThumbnailCtrl you can:

- Create different thumbnail outlines (none, images only, full, etc...);
- Highlight thumbnails on mouse hovering;
- Show/hide file names below thumbnails;
- Change thumbnail caption font;
- Zoom in/out thumbnails (done via ``Ctrl`` key + mouse wheel or with ``+`` and ``-`` chars,
  with zoom factor value customizable);
- Rotate thumbnails with these specifications:

  a) ``d`` key rotates 90 degrees clockwise;
  b) ``s`` key rotates 90 degrees counter-clockwise;
  c) ``a`` key rotates 180 degrees.
  
- Delete files/thumbnails (via the ``del`` key);
- Drag and drop thumbnails from ThumbnailCtrl to whatever application you want;
- Use local (when at least one thumbnail is selected) or global (no need for
  thumbnail selection) popup menus;
- Show/hide a `wx.ComboBox` at the top of ThumbnailCtrl: this combobox contains
  working directory information and it has history entries;
- possibility to show tooltips on thumbnails, which display file information
  (like file name, size, last modification date and thumbnail size).


:note: Using highlight thumbnails on mouse hovering may be slow on slower
 computers.


Window Styles
=============

`No particular window styles are available for this class.`


Events Processing
=================

This class processes the following events:

================================== ==================================================
Event Name                         Description
================================== ==================================================
``EVT_THUMBNAILS_CAPTION_CHANGED`` The thumbnail caption has been changed. Not used at present.
``EVT_THUMBNAILS_DCLICK``          The user has double-clicked on a thumbnail.
``EVT_THUMBNAILS_POINTED``         The mouse cursor is hovering over a thumbnail.
``EVT_THUMBNAILS_SEL_CHANGED``     The user has changed the selected thumbnail.
``EVT_THUMBNAILS_THUMB_CHANGED``   The thumbnail of an image has changed. Used internally.
================================== ==================================================


License And Version
===================

ThumbnailCtrl is distributed under the wxPython license.

Latest revision: Andrea Gavana @ 01 Dec 2009, 10.00 GMT

Version 0.9

"""


#----------------------------------------------------------------------
# Beginning Of ThumbnailCtrl wxPython Code
#----------------------------------------------------------------------

import wx
import os
import time
import zlib

import six
if six.PY3:
    import _thread as thread
else:
    import thread
from math import pi

import PIL.Image as Image



#----------------------------------------------------------------------
# Get Default Icon/Data
#----------------------------------------------------------------------

def GetMondrianData():
    return \
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\
\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00qID\
ATX\x85\xed\xd6;\n\x800\x10E\xd1{\xc5\x8d\xb9r\x97\x16\x0b\xad$\x8a\x82:\x16\
o\xda\x84pB2\x1f\x81Fa\x8c\x9c\x08\x04Z{\xcf\xa72\xbcv\xfa\xc5\x08 \x80r\x80\
\xfc\xa2\x0e\x1c\xe4\xba\xfaX\x1d\xd0\xde]S\x07\x02\xd8>\xe1wa-`\x9fQ\xe9\
\x86\x01\x04\x10\x00\\(Dk\x1b-\x04\xdc\x1d\x07\x14\x98;\x0bS\x7f\x7f\xf9\x13\
\x04\x10@\xf9X\xbe\x00\xc9 \x14K\xc1<={\x00\x00\x00\x00IEND\xaeB`\x82' 

def GetMondrianBitmap():
    return wx.BitmapFromImage(GetMondrianImage())

def GetMondrianImage():
    stream = six.BytesIO(GetMondrianData())
    return wx.ImageFromStream(stream)


def getDataSH():
    return zlib.decompress(
b'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2_A\x98\x83\rHvl\
\xdc\x9c\n\xa4X\x8a\x9d<C8\x80\xa0\x86#\xa5\x83\x81\x81y\x96\xa7\x8bcH\xc5\
\x9c\xb7\xd7\xd7\xf6\x85D2\xb4^\xbc\x1b\xd0\xd0p\xa6\x85\x9d\xa1\xf1\xc0\xc7\
\x7f\xef\x8d\x98\xf89_:p]\xaew\x0c\xe9\x16[\xbc\x8bSt\xdf\x9aT\xad\xef\xcb\
\x8e\x98\xc5\xbf\xb3\x94\x9ePT\xf8\xff\xf7\xfbm\xf5\xdb\xfeZ<\x16{\xf01o[l\
\xee\xee\xbd7\xbe\x95\xdd\xde\x9d+\xbf\xfdo\xf9\xb9\xd0\x03\x8be\xb7\xc7\xe6\
Y\xcb\xbd\x8b\xdfs\xe3[\xd6\xed\xe5\x9b}\x99\xe6=:\xbd\xed\xfc\xedu|\xfcq\
\xfb\xec/K<\xf8\xfec\xd7\xdb\xdb\x87W\xec\xcf\xfd]\xb0\xcc\xf0\xc0\xe5=\xf7^\
\x1e\xf9\xfb\xe6\xe6\xce\xe9\x0c\xfb\xa7\xafPt\xbb"\xa0\x9c\xd5!hz\xa4C*\xc9\
\x85\xd7pQ\x9bD\xa0s\xcf\xa8\xf0\xa8\xf0\x00\x0b\x9fyX\x7fo\xef\xdf\xc7\xda\
\r\xcbw\xd4\xfcx\xe0\xcdk\xd8\x9e[~{\xdd\xf6\xbfw\xbe\xfd\xddS\xdc\xe0\xfec_\
\xf0\xfe\xeb\xb7\xdf\xf1\xdd\xce\xdb&\xbb\xbdv\xe7\xff\xc3\xaf\x8dy\x99\xe5\
\x9e?\xf7\xfb+\xb7\xfdnLN\xf5\xc6\xb7g\xfd\xca_\x9a\x7f?\x7f\xe0\xfe\xe3\xaa\
\xe5\x0b\xf4\xb7\xcb\xea\x97\xed\n\xb7\xbf\xff\xadh\xf9\xe3\x1d\xd5f\x7fb\
\xdf\x95Y\x15\xc6\xe7\xee\xfe\xcbz7Y\xbd\xde[\xf3y\x1f0\xd72x\xba\xfa\xb9\
\xacsJh\x02\x00\xc4i\x8dN' )

def getDataBL():
    return zlib.decompress(
b"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xac \xcc\xc1\
\x06${\xf3\xd5\x9e\x02)\x96b'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2\xed=]\x1cC8f\
\xea\x9e\xde\xcb\xd9` \xc2\xf0P\xdf~\xc9y\xaeu\x0f\xfe1\xdf\xcc\x14\x1482A\
\xe9\xfd\x83\x1d\xaf\x84\xac\xf8\xe6\\\x8c3\xfc\x98\xf8\xa0\xb1\xa9K\xec\x9f\
\xc4\xd1\xb4GG{\xb5\x15\x8f_|t\x8a[a\x1fWzG\xa9\xc4,\xa0Q\x0c\x9e\xae~.\xeb\
\x9c\x12\x9a\x00\x7f1,7" )

def getDataTR():
    return zlib.decompress(
b'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xac \xcc\xc1\
\x06${\xf3\xd5\x9e\x02)\x96b\'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2m=]\x1cC8f\
\xe6\x9e\xd9\xc8\xd9` \xc2p\x91\xbd\xaei\xeeL\x85\xdcUo\xf6\xf7\xd6\xb2\x88\
\x0bp\x9a\x89i\x16=-\x94\xe16\x93\xb9!\xb8y\xcd\t\x0f\x89\n\xe6\xb7\xfcV~6\
\x8dFo\xf5\xee\xc8\x1fOaw\xc9\x88\x0c\x16\x05\x1a\xc4\xe0\xe9\xea\xe7\xb2\
\xce)\xa1\t\x00"\xf9$\x83' )

def getShadow():
    if 'phoenix' in wx.PlatformInfo:
        fonction = wx.Image
    else :
        fonction = wx.ImageFromStream
    sh_tr = fonction(six.BytesIO(getDataTR())).ConvertToBitmap()
    sh_bl = fonction(six.BytesIO(getDataBL())).ConvertToBitmap()
    sh_sh = fonction(six.BytesIO(getDataSH())).Rescale(500, 500, wx.IMAGE_QUALITY_HIGH)
    return (sh_tr, sh_bl, sh_sh.ConvertToBitmap())


#-----------------------------------------------------------------------------
# PATH & FILE FILLING (OS INDEPENDENT)
#-----------------------------------------------------------------------------

def opj(path):
    """
    Convert paths to the platform-specific separator.

    :param `path`: the path to convert.
    """

    strs = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        strs = '/' + strs

    return strs

#-----------------------------------------------------------------------------

# Different Outline On Thumb Selection:
# THUMB_OUTLINE_NONE: No Outline Drawn On Selection
# THUMB_OUTLINE_FULL: Full Outline Drawn On Selection
# THUMB_OUTLINE_RECT: Only Maximum Image Rect Outlined On Selection
# THUMB_OUTLINE_IMAGE: Only Image Rect Outlined On Selection

THUMB_OUTLINE_NONE = 0
THUMB_OUTLINE_FULL = 1
THUMB_OUTLINE_RECT = 2
THUMB_OUTLINE_IMAGE = 4

# Options For Filtering Files
THUMB_FILTER_IMAGES = 1
# THUMB_FILTER_VIDEOS = 2  Don't Know How To Create Thumbnails For Videos!!!

# ThumbnailCtrl Orientation: Not Fully Implemented Till Now
THUMB_HORIZONTAL = wx.HORIZONTAL
THUMB_VERTICAL = wx.VERTICAL

# Image File Name Extensions: Am I Missing Some Extensions Here?
extensions = [".jpeg", ".jpg", ".bmp", ".png", ".ico", ".tiff", ".ani", ".cur", ".gif",
              ".iff", ".icon", ".pcx", ".tif", ".xpm", ".xbm", ".mpeg", ".mpg", ".mov"]

# ThumbnailCtrl Events:
# wxEVT_THUMBNAILS_SEL_CHANGED: Event Fired When You Change Thumb Selection
# wxEVT_THUMBNAILS_POINTED: Event Fired When You Point A Thumb
# wxEVT_THUMBNAILS_DCLICK: Event Fired When You Double-Click A Thumb
# wxEVT_THUMBNAILS_CAPTION_CHANGED: Not Used At Present
# wxEVT_THUMBNAILS_THUMB_CHANGED: Used Internally

wxEVT_THUMBNAILS_SEL_CHANGED = wx.NewEventType()
wxEVT_THUMBNAILS_POINTED = wx.NewEventType()
wxEVT_THUMBNAILS_DCLICK = wx.NewEventType()
wxEVT_THUMBNAILS_CAPTION_CHANGED = wx.NewEventType()
wxEVT_THUMBNAILS_THUMB_CHANGED = wx.NewEventType()

#-----------------------------------#
#        ThumbnailCtrlEvent
#-----------------------------------#

EVT_THUMBNAILS_SEL_CHANGED = wx.PyEventBinder(wxEVT_THUMBNAILS_SEL_CHANGED, 1)
""" The user has changed the selected thumbnail. """
EVT_THUMBNAILS_POINTED = wx.PyEventBinder(wxEVT_THUMBNAILS_POINTED, 1)
""" The mouse cursor is hovering over a thumbnail. """
EVT_THUMBNAILS_DCLICK = wx.PyEventBinder(wxEVT_THUMBNAILS_DCLICK, 1)
""" The user has double-clicked on a thumbnail. """
EVT_THUMBNAILS_CAPTION_CHANGED = wx.PyEventBinder(wxEVT_THUMBNAILS_CAPTION_CHANGED, 1)
""" The thumbnail caption has been changed. Not used at present. """
EVT_THUMBNAILS_THUMB_CHANGED = wx.PyEventBinder(wxEVT_THUMBNAILS_THUMB_CHANGED, 1)
""" The thumbnail of an image has changed. Used internally"""

TN_USE_PIL = 0

TIME_FMT = '%d %b %Y, %H:%M:%S'


def CmpThumb(first, second):
    """
    Compares two thumbnails in terms of file names and ids.

    :param `first`: an instance of L{Thumb};
    :param `second`: another instance of L{Thumb}.
    """
    
    if first.GetFileName() < second.GetFileName():
        return -1
    elif first.GetFullFileName() == second.GetFullFileName():
        return first.GetId() - second.GetId()
    
    return 1


def SortFiles(items, sorteditems, filenames):
    """
    Sort files in alphabetical order.

    :param `sorteditems`: a list of L{Thumb} objects;
    :param `filenames`: a list of image filenames.
    """
    
    newfiles = []
    for item in sorteditems:
        newfiles.append(filenames[items.index(item)])
        
    return newfiles

# ---------------------------------------------------------------------------- #
# Class PILImageHandler, handles loading and highlighting images with PIL
# ---------------------------------------------------------------------------- #

class PILImageHandler(object):
    """
    This image handler loads and manipulates the thumbnails with the help
    of PIL (the Python Imaging Library).
    """
    
    def __init__(self):
        """
        Default class constructor.
        
        Check if the PIL is installed, if not throw an exception.
        """

        try:

            import PIL.Image as Image
            import PIL.ImageEnhance as ImageEnhance

        except ImportError:
            
            errstr = ("\nThumbnailCtrl *requires* PIL (Python Imaging Library).\n"
                     "You can get it at:\n\n"
                     "http://www.pythonware.com/products/pil/\n\n"
                     "ThumbnailCtrl can not continue. Exiting...\n")
            
            raise Exception(errstr)


    def LoadThumbnail(self, imgPIL, thumbnailsize):
        """
        Load the file and rescale it.

        :param `filename`: a file containing an image;
        :param `thumbnailsize`: the desired size of the thumbnail.
        """

        pil = imgPIL.copy()
        originalsize = pil.size
        
        pil.thumbnail(thumbnailsize)
        if 'phoenix' in wx.PlatformInfo:
            img = wx.Image(pil.size[0], pil.size[1])
        else :
            img = wx.EmptyImage(pil.size[0], pil.size[1])

        img.SetData(pil.convert("RGB").tobytes())

        alpha = False
        if "A" in pil.getbands():
            if 'phoenix' in wx.PlatformInfo:
                img.SetAlpha(pil.convert("RGBA").tobytes()[3::4])
            else :
                img.SetAlphaData(pil.convert("RGBA").tobytes()[3::4])
            alpha = True

        return img, originalsize, alpha



# ---------------------------------------------------------------------------- #
# Class ThumbnailEvent
# ---------------------------------------------------------------------------- #

class ThumbnailEvent(wx.PyCommandEvent):
    """
    This class is used to send events when a thumbnail is hovered, selected,
    double-clicked or when its caption has been changed.
    """
    def __init__(self, evtType, evtId=-1):
        """
        Default class constructor.

        :param `evtType`: the event type;
        :param `evtId`: the event identifier.
        """
        
        wx.PyCommandEvent.__init__(self, evtType, evtId)
        self._eventType = evtType


# ---------------------------------------------------------------------------- #
# Class Thumb
# Auxiliary Class, To Handle Single Thumb Information For Every Thumb.
# Used Internally.
# ---------------------------------------------------------------------------- #

class Thumb(object):
    """
    This is an auxiliary class, to handle single thumbnail information for every thumb.

    Used internally.
    """
    
    def __init__(self, parent, track=None):
        self._id = 0
        if parent.afficheLabels == True :
            self._caption = track.label
        else :
            self._caption = ""
        self._filesize = None
        self._parent = parent
        self._captionbreaks = []
        if 'phoenix' in wx.PlatformInfo:
            self._bitmap = wx.Bitmap(1,1)
            self._image = wx.Image(1,1)
        else :
            self._bitmap = wx.EmptyBitmap(1,1)
            self._image = wx.EmptyImage(1,1)
        self._rotation = 0
        self._alpha = None
        
        self.track = track
        
    def GetImgPIL(self) :
        return self.track.image

    def GetImage(self):
        """ Returns the thumbnail image. """
        
        return self._image

    
    def SetImage(self, image):
        """
        Sets the thumbnail image.

        :param `image`: a `wx.Image` object.
        """
        
        self._image = image        


    def SetBitmap(self, bmp):
        """
        Sets the thumbnail bitmap.

        :param `bmp`: a `wx.Bitmap` object.
        """
        
        self._bitmap = bmp

    def GetId(self):
        """ Returns the thumbnail identifier. """
        
        return self._id


    def SetId(self, id=-1):
        """
        Sets the thumbnail identifier.

        :param `id`: an integer specifying the thumbnail identifier.
        """

        self._id = id
        

    def SetRotatedImage(self, image):
        """
        Sets the image as rotated (fast).

        :param `image`: the rotated image, an instance of `wx.Image`.        
        """
        
        self._rotatedimage = image


    def GetRotatedImage(self):
        """ Returns a rotated image. """
        
        return self._rotatedimage
    

    def GetBitmap(self, width, height):
        """
        Returns the associated bitmap.

        :param `width`: the associated bitmap width;
        :param `height`: the associated bitmap height.
        """
        
        if self.GetRotation() % (2*pi) < 1e-6:
            if 'phoenix' in wx.PlatformInfo:
                isOk = self._bitmap.IsOk()
            else :
                isOk = self._bitmap.Ok()
            if not isOk:
                if not hasattr(self, "_threadedimage"):
                    img = GetMondrianImage()
                else:
                    img = self._threadedimage
                
            else:
                if not hasattr(self, "_threadedimage"):
                    img = GetMondrianImage()
                else:
                    img = self._threadedimage
                
        else:

            img = self.GetRotatedImage()

        if hasattr(self, "_originalsize"):
            imgwidth, imgheight = self._originalsize
        else:
            imgwidth, imgheight = (img.GetWidth(), img.GetHeight())
            
        if width < imgwidth or height < imgheight:
            scale = float(width)/imgwidth

            if scale > float(height)/imgheight:
                scale = float(height)/imgheight

            img = img.Scale(int(imgwidth*scale), int(imgheight*scale))
            
        bmp = img.ConvertToBitmap()
                        
        self._image = img

        return bmp


    def GetOriginalImage(self):
        """ Returns the bitmap associated to a thumbnail, as a file name. """

        original = opj((self._dir + "/" + self._filename))

        return original


    def GetFullFileName(self):
        """ Returns the full filename of the thumbnail. """

        return self._dir + "/" + self._filename

                
    def GetCaption(self, line):
        """
        Returns the caption associated to a thumbnail.

        :param `line`: the caption line we wish to retrieve (useful for multilines
         caption strings).
        """
        
        if line + 1 >= len(self._captionbreaks):
            return ""
        
        strs = self._caption

        return strs        


    def GetCaptionLinesCount(self, width):
        """
        Returns the number of lines for the caption.

        :param `width`: the maximum width, in pixels, available for the caption text.
        """
        
        self.BreakCaption(width)
        return len(self._captionbreaks) - 1


    def BreakCaption(self, width):
        """
        Breaks the caption in several lines of text (if needed).

        :param `width`: the maximum width, in pixels, available for the caption text.
        """
        
        if len(self._captionbreaks) > 0 or width < 16:
            return
        
        self._captionbreaks.append(0)

        if len(self._caption) == 0:
            return

        pos = width//16
        beg = 0
        end = 0

        dc = wx.MemoryDC()
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(10,10)
        else :
            bmp = wx.EmptyBitmap(10, 10)
        dc.SelectObject(bmp)
        
        while 1:
  
            if pos >= len(self._caption):

                self._captionbreaks.append(len(self._caption))
                break

            sw, sh = dc.GetTextExtent(self._caption[beg:pos-beg])
            
            if  sw > width:

                if end > 0:
              
                    self._captionbreaks.append(end)
                    beg = end
              
                else:
              
                    self._captionbreaks.append(pos)
                    beg = pos
              
                pos = beg + width/16
                end = 0

            if pos < len(self._caption) and self._caption[pos] in [" ", "-", ",", ".", "_"]:
                end = pos + 1

            pos = pos + 1


        dc.SelectObject(wx.NullBitmap)
        

    def SetRotation(self, angle=0):
        """
        Sets the thumbnail rotation.

        :param `angle`: the thumbnail rotation, in radians.    
        """
        
        self._rotation = angle


    def GetRotation(self):
        """ Returns the thumbnail rotation, in radians. """
        
        return self._rotation
    

# ---------------------------------------------------------------------------- #
# Class ThumbnailCtrl
# Auxiliary Class, All Useful Methods Are Defined On ScrolledThumbnail Class.
# ---------------------------------------------------------------------------- #        

class ThumbnailCtrl(wx.Panel):
    """
    Thumbnailctrl is a widget that can be used to display a series of images in
    a "thumbnail" format.
    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, thumboutline=THUMB_OUTLINE_IMAGE,
                 thumbfilter=THUMB_FILTER_IMAGES, imagehandler=PILImageHandler, style=0, afficheLabels=True):
        """
        Default class constructor.

        :param `parent`: parent window. Must not be ``None``;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `thumboutline`: outline style for L{ThumbnailCtrl}, which may be:

         =========================== ======= ==================================
         Outline Flag                 Value  Description
         =========================== ======= ==================================
         ``THUMB_OUTLINE_NONE``            0 No outline is drawn on selection
         ``THUMB_OUTLINE_FULL``            1 Full outline (image+caption) is drawn on selection
         ``THUMB_OUTLINE_RECT``            2 Only thumbnail bounding rectangle is drawn on selection (default)
         ``THUMB_OUTLINE_IMAGE``           4 Only image bounding rectangle is drawn.
         =========================== ======= ==================================

        :param `thumbfilter`: filter for image/video/audio files. Actually only
         ``THUMB_FILTER_IMAGES`` is implemented;
        :param `imagehandler`: can be L{PILImageHandler} if PIL is installed (faster), or
         L{NativeImageHandler} which only uses wxPython image methods.
        """
        
        wx.Panel.__init__(self, parent, id, pos, size, style=style)     

        self._sizer = wx.BoxSizer(wx.VERTICAL)

        self._combo = wx.ComboBox(self, -1, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self._scrolled = ScrolledThumbnail(self, -1, thumboutline=thumboutline,
                                           thumbfilter=thumbfilter, imagehandler = imagehandler, afficheLabels=afficheLabels)

        subsizer = wx.BoxSizer(wx.HORIZONTAL)
        subsizer.Add((3, 0), 0)
        subsizer.Add(self._combo, 0, wx.EXPAND | wx.TOP, 3)
        subsizer.Add((3, 0), 0)
        self._sizer.Add(subsizer, 0, wx.EXPAND | wx.ALL, 3)
        self._sizer.Add(self._scrolled, 1, wx.EXPAND)

        self.SetSizer(self._sizer)

        self._sizer.Show(0, False)        
        self._sizer.Layout()

        methods = ["GetSelectedItem", "GetPointed", "GetHighlightPointed", "SetHighlightPointed",
                   "SetThumbOutline", "GetThumbOutline", "GetPointedItem", "GetItem",
                   "GetItemCount", "GetThumbWidth", "GetThumbHeight", "GetThumbBorder",
                   "ShowFileNames", "SetPopupMenu", "GetPopupMenu", "SetGlobalPopupMenu",
                   "GetGlobalPopupMenu", "SetSelectionColour", "GetSelectionColour",
                   "EnableDragging", "SetThumbSize", "GetThumbSize", "ShowThumbs", "AfficheImages",
                   "SetSelection", "GetSelection", "SetZoomFactor",
                   "GetZoomFactor", "SetCaptionFont", "GetCaptionFont", "GetItemIndex",
                   "InsertItem", "RemoveItemAt", "IsSelected", "Rotate", "ZoomIn", "ZoomOut",
                   "EnableToolTips", "GetThumbInfo", "GetOriginalImage"]

        for method in methods:
            setattr(self, method, getattr(self._scrolled, method))

        self._combochoices = []
        self._showcombo = False
        self._subsizer = subsizer
        
        self._combo.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        

    def ShowComboBox(self, show=True):
        """
        Shows/Hide the top folder `wx.ComboBox`.

        :param `show`: ``True`` to show the combobox, ``False`` otherwise.
        """
        
        if show:
            self._showcombo = True
            self._sizer.Show(0, True)
            self._sizer.Layout()
        else:
            self._showcombo = False
            self._sizer.Show(0, False)
            self._sizer.Layout()

        self._scrolled.Refresh()


    def GetShowComboBox(self):
        """ Returns whether the folder combobox is shown. """
        
        return self._showcombo
    

    def OnComboBox(self, event):
        """
        Handles the ``wx.EVT_COMBOBOX`` for the folder combobox.

        :param `event`: a `wx.CommandEvent` event to be processed.
        """
        
        dirs = self._combo.GetValue()

        if os.path.isdir(opj(dirs)):
            self._scrolled.ShowDir(opj(dirs))
            
        event.Skip()


    def RecreateComboBox(self, newdir):
        """
        Recreates the folder combobox every time a new directory is explored.

        :param `newdir`: the new folder to be explored.
        """
        
        newdir = newdir.strip()
        
        if opj(newdir) in self._combochoices:
            return

        self.Freeze()

        self._sizer.Detach(0)
        self._subsizer.Detach(1)
        self._subsizer.Destroy()
        self._combo.Destroy()

        subsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self._combochoices.insert(0, opj(newdir))
        
        self._combo = wx.ComboBox(self, -1, value=newdir, choices=self._combochoices,
                                  style=wx.CB_DROPDOWN | wx.CB_READONLY)

        subsizer.Add((3, 0), 0)
        subsizer.Add(self._combo, 1, wx.EXPAND | wx.TOP, 3)
        subsizer.Add((3, 0), 0)
        self._sizer.Insert(0, subsizer, 0, wx.EXPAND | wx.ALL, 3)

        self._subsizer = subsizer
    
        self._subsizer.Layout()

        if not self.GetShowComboBox():
            self._sizer.Show(0, False)
            
        self._sizer.Layout()

        self._combo.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        
        self.Thaw()
        
        
# ---------------------------------------------------------------------------- #
# Class ScrolledThumbnail
# This Is The Main Class Implementation
# ---------------------------------------------------------------------------- #        

class ScrolledThumbnail(wx.ScrolledWindow):
    """ This is the main class implementation of L{ThumbnailCtrl}. """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, thumboutline=THUMB_OUTLINE_IMAGE,
                 thumbfilter=THUMB_FILTER_IMAGES, imagehandler=PILImageHandler, afficheLabels=True):
        """
        Default class constructor.

        :param `parent`: parent window. Must not be ``None``;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `thumboutline`: outline style for L{ScrolledThumbnail}, which may be:

         =========================== ======= ==================================
         Outline Flag                 Value  Description
         =========================== ======= ==================================
         ``THUMB_OUTLINE_NONE``            0 No outline is drawn on selection
         ``THUMB_OUTLINE_FULL``            1 Full outline (image+caption) is drawn on selection
         ``THUMB_OUTLINE_RECT``            2 Only thumbnail bounding rectangle is drawn on selection (default)
         ``THUMB_OUTLINE_IMAGE``           4 Only image bounding rectangle is drawn.
         =========================== ======= ==================================

        :param `thumbfilter`: filter for image/video/audio files. Actually only
         ``THUMB_FILTER_IMAGES`` is implemented;
        :param `imagehandler`: can be L{PILImageHandler} if PIL is installed (faster), or
         L{NativeImageHandler} which only uses wxPython image methods.
        """
        
        wx.ScrolledWindow.__init__(self, parent, id, pos, size)

        self.SetThumbSize(96, 80)
        self._tOutline = thumboutline
        self._filter = thumbfilter
        self._imageHandler = imagehandler()
        self._selected = -1
        self._pointed = -1
        self._labelcontrol = None
        self._pmenu = None
        self._gpmenu = None
        self._dragging = False
        self._checktext = False
        self._orient = THUMB_VERTICAL

        self._tCaptionHeight = []
        self._selectedarray = []
        self._tTextHeight = 16
        self._tCaptionBorder = 8
        self._tOutlineNotSelected = True
        self._mouseeventhandled = False
        self._highlight = False
        self._zoomfactor = 1.4
        self.SetCaptionFont()
        self._items = []

        self.afficheLabels = afficheLabels

        self._enabletooltip = False
        
        self._parent = parent
        
        self._selectioncolour = "#009EFF"
        self.grayPen = wx.Pen("#A2A2D2", 1, wx.SHORT_DASH)
        self.grayPen.SetJoin(wx.JOIN_MITER)
        if 'phoenix' in wx.PlatformInfo:
            self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
        else :
            self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))
        t, b, s = getShadow()
        self.shadow = wx.MemoryDC()
        self.shadow.SelectObject(s)
        
        self.ShowFileNames(True)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.Bind(EVT_THUMBNAILS_THUMB_CHANGED, self.OnThumbChanged)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def GetSelectedItem(self, index):
        """
        Returns the selected thumbnail.

        :param `index`: the thumbnail index (i.e., the selection).
        """

        return self.GetItem(self.GetSelection(index))


    def GetPointed(self):
        """ Returns the pointed thumbnail index. """
        
        return self._pointed


    def GetHighlightPointed(self):
        """
        Returns whether the thumbnail pointed should be highlighted or not.
        
        :note: Please be aware that this functionality may be slow on slower computers.
        """
        
        return self._highlight


    def SetHighlightPointed(self, highlight=True):
        """
        Sets whether the thumbnail pointed should be highlighted or not.

        :param `highlight`: ``True`` to enable highlight-on-point with the mouse,
         ``False`` otherwise.
         
        :note: Please be aware that this functionality may be slow on slower computers.
        """
        
        self._highlight = highlight


    def SetThumbOutline(self, outline):
        """
        Sets the thumbnail outline style on selection.

        :param `outline`: the outline to use on selection. This can be one of the following
         bits:

         =========================== ======= ==================================
         Outline Flag                 Value  Description
         =========================== ======= ==================================
         ``THUMB_OUTLINE_NONE``            0 No outline is drawn on selection
         ``THUMB_OUTLINE_FULL``            1 Full outline (image+caption) is drawn on selection
         ``THUMB_OUTLINE_RECT``            2 Only thumbnail bounding rectangle is drawn on selection (default)
         ``THUMB_OUTLINE_IMAGE``           4 Only image bounding rectangle is drawn.
         =========================== ======= ==================================
         
        """

        if outline not in [THUMB_OUTLINE_NONE, THUMB_OUTLINE_FULL, THUMB_OUTLINE_RECT,
                           THUMB_OUTLINE_IMAGE]:
            return
        
        self._tOutline = outline        


    def GetThumbOutline(self):
        """ Returns the thumbnail outline style on selection. """
        
        return self._tOutline
    

    def GetPointedItem(self):
        """ Returns the pointed thumbnail. """
        
        return self.GetItem(self._pointed)
        

    def GetItem(self, index):
        """
        Returns the item at position `index`.

        :param `index`: the thumbnail index position.
        """

        return index >= 0 and (index < len(self._items) and [self._items[index]] or [None])[0]


    def GetItemCount(self):
        """ Returns the number of thumbnails. """

        return len(self._items)


    def SortItems(self):
        """ Sorts the items accordingly to the L{CmpThumb} function. """

        self._items.sort(CmpThumb)        


    def GetThumbWidth(self):
        """ Returns the thumbnail width. """

        return self._tWidth


    def GetThumbHeight(self):
        """ Returns the thumbnail height. """

        return self._tHeight


    def GetThumbBorder(self):
        """ Returns the thumbnail border. """

        return self._tBorder
    
 
    def GetCaption(self):
        """ Returns the thumbnail caption. """

        return self._caption

    
    def SetLabelControl(self, statictext):
        """
        Sets the thumbnail label as `wx.StaticText`.

        :param `statictext`: an instance of `wx.StaticText`.
        """
        
        self._labelcontrol = statictext
        

    def ShowFileNames(self, show=True):
        """
        Sets whether the user wants to show file names under the thumbnails or not.

        :param `show`: ``True`` to show file names under the thumbnails, ``False`` otherwise.
        """
        
        self._showfilenames = show
        self.Refresh()
        

    def SetOrientation(self, orient=THUMB_VERTICAL):
        """
        Set the L{ThumbnailCtrl} orientation (partially implemented).

        :param `orient`: one of ``THUMB_VERTICAL``, ``THUMB_HORIZONTAL``.

        :todo: Correctly implement the ``THUMB_HORIZONTAL`` orientation.        
        """
        
        self._orient = orient


    def SetPopupMenu(self, menu):
        """
        Sets the thumbnails popup menu when at least one thumbnail is selected.

        :param `menu`: an instance of `wx.Menu`.
        """
        
        self._pmenu = menu


    def GetPopupMenu(self):
        """ Returns the thumbnails popup menu when at least one thumbnail is selected. """
        
        return self._pmenu        


    def SetGlobalPopupMenu(self, gpmenu):
        """
        Sets the global thumbnails popup menu (no need of thumbnail selection).

        :param `gpmenu`: an instance of `wx.Menu`.
        """
        
        self._gpmenu = gpmenu


    def GetGlobalPopupMenu(self):
        """ Returns the global thumbnailss popup menu (no need of thumbnail selection). """
        
        return self._gpmenu
    

    def GetSelectionColour(self):
        """ Returns the colour used to indicate a selected thumbnail. """
        
        return self._selectioncolour


    def SetSelectionColour(self, colour=None):
        """
        Sets the colour used to indicate a selected thumbnail.

        :param `colour`: a valid `wx.Colour` object. If defaulted to ``None``, it
         will be taken from the system settings.
        """
        
        if colour is None:
            colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)

        self._selectioncolour = colour
        

    def EnableDragging(self, enable=True):
        """
        Enables/disables thumbnails drag and drop.

        :param `enable`: ``True`` to enable drag and drop, ``False`` to disable it.
        """
        
        self._dragging = enable


    def EnableToolTips(self, enable=True):
        """
        Globally enables/disables thumbnail file information.

        :param `enable`: ``True`` to enable thumbnail file information, ``False`` to disable it.
        """

        self._enabletooltip = enable
        
        if not enable and hasattr(self, "_tipwindow"):
            self._tipwindow.Enable(False)
        

    def GetThumbInfo(self, thumb=-1):
        """
        Returns the thumbnail information.
        :param `thumb`: the index of the thumbnail for which we are collecting information.
        """
        thumbinfo = None
        if thumb >= 0:
            track = self._items[thumb].track
            thumbinfo = track.GetInfobulle()
        return thumbinfo
    

    def SetThumbSize(self, width, height, border=6):
        """
        Sets the thumbnail size as width, height and border.

        :param `width`: the desired thumbnail width;
        :param `height`: the desired thumbnail height;
        :param `border`: the spacing between thumbnails.
        """
        
        if width > 350 or height > 280:
            return
        
        self._tWidth = width 
        self._tHeight = height
        self._tBorder = border
        self.SetScrollRate(int((self._tWidth + self._tBorder)/4),
                           int((self._tHeight + self._tBorder)/4))
        self.SetSizeHints(self._tWidth + self._tBorder*2 + 16,
                          self._tHeight + self._tBorder*2 + 8)


    def GetThumbSize(self):
        """ Returns the thumbnail size as width, height and border. """
        
        return self._tWidth, self._tHeight, self._tBorder


    def Clear(self):
        """ Clears L{ThumbnailCtrl}. """
        
        self._items = []
        self._selected = -1
        self._selectedarray = []
        self.UpdateProp()
        self.Refresh()


##    def ListDirectory(self, directory, fileExtList):
##        """
##        Returns list of file info objects for files of particular extensions.
##
##        :param `directory`: the folder containing the images to thumbnail;
##        :param `fileExtList`: a Python list of file extensions to consider.
##        """
##
##        fileList = [os.path.normcase(f) for f in os.listdir(directory)]               
##        fileList = [f for f in fileList \
##                    if os.path.splitext(f)[1] in fileExtList]                          
##
##        return fileList


    def ThreadImage(self, listeImages):
        """
        Threaded method to load images. Used internally.

        :param `filenames`: a Python list of file names containing images.
        """
        
        count = 0
        
        while count < len(listeImages):

            if not self._isrunning:
                self._isrunning = False
                thread.exit()
                return
            
            self.LoadImages(listeImages[count], count)
            if count < 4:
                self.Refresh()
            elif count%4 == 0:
                self.Refresh()
                
            count = count + 1

        self._isrunning = False            
        thread.exit()
        

    def LoadImages(self, imgPIL, imagecount):
        """
        Threaded method to load images. Used internally.

        :param `newfile`: a file name containing an image to thumbnail;
        :param `imagecount`: the number of images loaded until now.
        """

        if not self._isrunning:
            thread.exit()
            return
        
        img, originalsize, alpha = self._imageHandler.LoadThumbnail(imgPIL, (300, 240))
        try:
            self._items[imagecount]._threadedimage = img
            self._items[imagecount]._originalsize = originalsize
            self._items[imagecount]._bitmap = img
            self._items[imagecount]._alpha = alpha
        except:
            return

        
    def ShowThumbs(self, thumbs):
        """
        Shows all the thumbnails.
        
        :param `thumbs`: should be a sequence with instances of L{Thumb};
        :param `caption`: the caption text for the current selected thumbnail.
        """

        self._isrunning = False
       
        # update items
        self._items = thumbs
        listeImages = [thumb.GetImgPIL() for thumb in thumbs]
        
##        items = self._items[:]
##        self._items.sort(CmpThumb)

        self._isrunning = True
        
        thread.start_new_thread(self.ThreadImage, (listeImages,))
        wx.MilliSleep(20)

        self._selectedarray = []
        self.UpdateProp()
        self.Refresh()
        
    def AfficheImages(self, listeImages=[], filter=THUMB_FILTER_IMAGES):
        if filter >= 0:
            self._filter = filter
                    
        # update items
        thumbs = []
        
        for track in listeImages:
            if self._filter & THUMB_FILTER_IMAGES:
                thumbs.append(Thumb(self, track=track))
        
        return self.ShowThumbs(thumbs)    

    def SetSelection(self, value=-1):
        """
        Sets thumbnail selection.

        :param `value`: the thumbnail index to select.
        """
        
        self._selected = value

        if value != -1:
            self._selectedarray = [value]
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)
            self.ScrollToSelected()
            self.Refresh()

        
    def SetZoomFactor(self, zoom=1.4):
        """
        Sets the zoom factor.

        :param `zoom`: a floating point number representing the zoom factor. Must be
         greater than or equal to 1.0.
        """
        
        if zoom <= 1.0:
            raise Exception("\nERROR: Zoom Factor Must Be Greater Than 1.0")
        
        self._zoomfactor = zoom        


    def GetZoomFactor(self):
        """ Returns the zoom factor. """
        
        return self._zoomfactor
    

    def IsAudioVideo(self, fname):
        """
        Returns ``True`` if a file contains either audio or video data.
        Currently unused as L{ThumbnailCtrl} recognizes only image files.

        :param `fname`: a file name.
        
        :todo: Find a way to create thumbnails of video, audio and other formats.
        """

        return os.path.splitext(fname)[1].lower() in \
               [".mpg", ".mpeg", ".vob"]


    def IsVideo(self, fname):
        """
        Returns ``True`` if a file contains video data.
        Currently unused as L{ThumbnailCtrl} recognizes only image files.

        :param `fname`: a file name.

        :todo: Find a way to create thumbnails of video, audio and other formats.
        """

        return os.path.splitext(fname)[1].lower() in \
               [".m1v", ".m2v"]


    def IsAudio(self, fname):
        """
        Returns ``True`` if a file contains audio data.
        Currently unused as L{ThumbnailCtrl} recognizes only image files.

        :param `fname`: a file name.

        :todo: Find a way to create thumbnails of video, audio and other formats.
        """

        return os.path.splitext(fname)[1].lower() in \
               [".mpa", ".mp2", ".mp3", ".ac3", ".dts", ".pcm"]
    

    def UpdateItems(self):
        """ Updates thumbnail items. """
        
        selected = self._selectedarray
        selectedfname = []
        selecteditemid = []
        
        for ii in range(len(self._selectedarray)):
            selectedfname.append(self.GetSelectedItem(ii).GetFileName())
            selecteditemid.append(self.GetSelectedItem(ii).GetId())
            
        self.UpdateShow()
        
        if len(selected) > 0:
            self._selectedarray = []            
            for ii in range(len(self._items)):
                for jj in range(len(selected)):
                    if self._items[ii].GetFileName() == selectedfname[jj] and \
                       self._items[ii].GetId() == selecteditemid[jj]:
                  
                        self._selectedarray.append(ii)
                        if len(self._selectedarray) == 1:
                            self.ScrollToSelected()

            if len(self._selectedarray) > 0:
                self.Refresh()
                eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
                self.GetEventHandler().ProcessEvent(eventOut)
  

    def SetCaption(self, caption=""):
        """
        Sets the current caption string.

        :param `caption`: the current caption string.
        """
        
        self._caption = caption
        if self._labelcontrol:

            maxWidth = self._labelcontrol.GetSize().GetWidth()/8
            if len(caption) > maxWidth:
                caption = "..." + caption[len(caption) + 3 - maxWidth]

            self._labelcontrol.SetLabel(caption)

        eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_CAPTION_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(eventOut)


    def SetCaptionFont(self, font=None):
        """
        Sets the font for all the thumbnail captions.

        :param `font`: a valid `wx.Font` object. If defaulted to ``None``, a standard
         font will be generated.
        """
        
        if font is None:
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False)

        self._captionfont = font


    def GetCaptionFont(self):
        """ Returns the font for all the thumbnail captions. """
        
        return self._captionfont
    

    def UpdateShow(self):
        """ Updates thumbnail items. """
        
        self.ShowThumbs(self._items)


    def GetCaptionHeight(self, begRow, count=1):
        """
        Returns the height for the file name caption.

        :param `begRow`: the caption line at which we start measuring the height;
        :param `count`: the number of lines to measure.
        """
        
        capHeight = 0
        for ii in range(int(begRow), int(begRow + count)):
            if ii < len(self._tCaptionHeight):
                capHeight = capHeight + self._tCaptionHeight[ii]

        return capHeight*self._tTextHeight 


    def GetItemIndex(self, x, y):
        """
        Returns the thumbnail index at position (x, y).

        :param `x`: the mouse x position;
        :param `y`: the mouse y position.
        """
        
        col = (x - self._tBorder)//(self._tWidth + self._tBorder)

        if col >= self._cols:
            col = self._cols - 1
        
        row = -1
        y = y - self._tBorder
        
        while y > 0:

            row = row + 1
            y = y - (self._tHeight + self._tBorder + self.GetCaptionHeight(row))

        if row < 0:
            row = 0

        index = row*self._cols + col
        
        if index >= len(self._items):
            index = -1

        return index


    def UpdateProp(self, checkSize=True):
        """
        Updates L{ThumbnailCtrl} and its visible thumbnails.

        :param `checkSize`: ``True`` to update the items visibility if the window
         size has changed.
        """

        width = self.GetClientSize().GetWidth()
        self._cols = (width - self._tBorder)//(self._tWidth + self._tBorder)
        
        if self._cols == 0:
            self._cols = 1

        tmpvar = (len(self._items)%self._cols and [1] or [0])[0]
        self._rows = len(self._items)//self._cols + tmpvar
        
        self._tCaptionHeight = []

        for row in range(self._rows):

            capHeight = 0
            
            for col in range(self._cols):

                ii = row*self._cols + col

                if len(self._items) > ii and \
                   self._items[ii].GetCaptionLinesCount(self._tWidth - self._tCaptionBorder) > capHeight:
                    
                    capHeight = self._items[ii].GetCaptionLinesCount(self._tWidth - self._tCaptionBorder)

            self._tCaptionHeight.append(capHeight)

        self.SetVirtualSize((self._cols*(self._tWidth + self._tBorder) + self._tBorder,
                            self._rows*(self._tHeight + self._tBorder) + \
                            self.GetCaptionHeight(0, self._rows) + self._tBorder))
        
        self.SetSizeHints(self._tWidth + 2*self._tBorder + 16,
                          self._tHeight + 2*self._tBorder + 8 + \
                          (self._rows and [self.GetCaptionHeight(0)] or [0])[0])
        
        if checkSize and width != self.GetClientSize().GetWidth():
            self.UpdateProp(False)


    def InsertItem(self, thumb, pos):
        """
        Inserts a thumbnail in the specified position.

        :param `pos`: the index at which we wish to insert the new thumbnail.
        """
        
        if pos < 0 or pos > len(self._items):
            self._items.append(thumb)
        else:
            self._items.insert(pos, thumb)
            
        self.UpdateProp()


    def RemoveItemAt(self, pos):
        """
        Removes a thumbnail at the specified position.

        :param `pos`: the index at which we wish to remove the thumbnail.
        """        

        del self._items[pos]
        
        self.UpdateProp()


    def GetPaintRect(self):
        """ Returns the paint bounding rect for the L{OnPaint} method. """
        
        size = self.GetClientSize()
        paintRect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
        paintRect.x, paintRect.y = self.GetViewStart()
        xu, yu = self.GetScrollPixelsPerUnit()
        paintRect.x = paintRect.x*xu
        paintRect.y = paintRect.y*yu
        
        return paintRect


    def IsSelected(self, indx):
        """
        Returns whether a thumbnail is selected or not.

        :param `indx`: the index of the thumbnail to check for selection.
        """

        return self._selectedarray.count(indx) != 0
    

    def GetSelection(self, selIndex=-1):
        """
        Returns the selected thumbnail.

        :param `selIndex`: if not equal to -1, the index of the selected thumbnail.
        """
        
        return (selIndex == -1 and [self._selected] or \
                [self._selectedarray[selIndex]])[0]


    def GetOriginalImage(self, index=None):
        """
        Returns the original image associated to a thumbnail.

        :param `index`: the index of the thumbnail. If defaulted to ``None``, the current
         selection is used.
        """

        if index is None:
            index = self.GetSelection()
            
        return self._items[index].GetOriginalImage()


    def ScrollToSelected(self):
        """ Scrolls the `wx.ScrolledWindow` to the selected thumbnail. """
        
        if self.GetSelection() == -1:
            return

        # get row
        row = self.GetSelection()/self._cols
        # calc position to scroll view
        
        paintRect = self.GetPaintRect()
        y1 = row*(self._tHeight + self._tBorder) + self.GetCaptionHeight(0, row)
        y2 = y1 + self._tBorder + self._tHeight + self.GetCaptionHeight(row)

        if y1 < paintRect.GetTop():
            sy = y1 # scroll top
        elif y2 > paintRect.GetBottom():
            sy = y2 - paintRect.height # scroll bottom
        else:
            return
        
        # scroll view
        xu, yu = self.GetScrollPixelsPerUnit()
        sy = sy/yu + (sy%yu and [1] or [0])[0] # convert sy to scroll units
        x, y = self.GetViewStart()
        
        self.Scroll(x,sy)


    def CalculateBestCaption(self, dc, caption, sw, width):
        """
        Calculates the best caption string to show based on the actual zoom factor.

        :param `dc`: an instance of `wx.DC`;
        :param `caption`: the original caption string;
        :param `sw`: the maximum width allowed for the caption string, in pixels;
        :param `width`: the caption string width, in pixels.
        """

        caption = caption + "..."
        
        while sw > width:
            caption = caption[1:]
            sw, sh = dc.GetTextExtent(caption)
            
        return "..." + caption[0:-3]
  

    def DrawThumbnail(self, bmp, thumb, index):
        """
        Draws a visible thumbnail.

        :param `bmp`: the thumbnail version of the original image;
        :param `thumb`: an instance of L{Thumb};
        :param `index`: the index of the thumbnail to draw.
        """

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        if 'phoenix' not in wx.PlatformInfo:
            dc.BeginDrawing()
        
        x = self._tBorder/2
        y = self._tBorder/2

        # background
        dc.SetPen(wx.Pen(wx.BLACK, 0, wx.TRANSPARENT))
        dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        dc.DrawRectangle(0, 0, bmp.GetWidth(), bmp.GetHeight())
        
        # image
        img = thumb.GetBitmap(self._tWidth, self._tHeight)
        ww = img.GetWidth()
        hh = img.GetHeight()

        if index == self.GetPointed() and self.GetHighlightPointed():
            factor = 1.5
            img = self._imageHandler.HighlightImage(img.ConvertToImage(), factor).ConvertToBitmap()
        
        imgRect = wx.Rect(int(x + (self._tWidth - img.GetWidth())/2),
                          int(y + (self._tHeight - img.GetHeight())/2),
                          int(img.GetWidth()), int(img.GetHeight()))

        if not thumb._alpha:
            dc.Blit(imgRect.x+5, imgRect.y+5, imgRect.width, imgRect.height, self.shadow, 500-ww, 500-hh)        
        dc.DrawBitmap(img, int(imgRect.x), int(imgRect.y), True)

        colour = self.GetSelectionColour()
        selected = self.IsSelected(index)
 
        colour = self.GetSelectionColour()

        # draw caption
        sw, sh = 0, 0
        if self._showfilenames:
            textWidth = 0
            dc.SetFont(self.GetCaptionFont())
            mycaption = thumb.GetCaption(0)
            sw, sh = dc.GetTextExtent(mycaption)

            if sw > self._tWidth:
                mycaption = self.CalculateBestCaption(dc, mycaption, sw, self._tWidth)
                sw = self._tWidth
            
            textWidth = sw + 8
            tx = x + (self._tWidth - textWidth)/2
            ty = y + self._tHeight

            txtcolour = "#7D7D7D"
            dc.SetTextForeground(txtcolour) 
            
            tx = x + (self._tWidth - sw)/2
            if hh >= self._tHeight:
                ty = y + self._tHeight + (self._tTextHeight - sh)/2 + 3
            else:
                ty = y + hh + (self._tHeight-hh)/2 + (self._tTextHeight - sh)/2 + 3

            dc.DrawText(mycaption, int(tx), int(ty))
            
        # outline
        if self._tOutline != THUMB_OUTLINE_NONE and (self._tOutlineNotSelected or self.IsSelected(index)):

            dotrect = wx.Rect()
            dotrect.x = int(x) - 2
            dotrect.y = int(y) - 2
            dotrect.width = bmp.GetWidth() - self._tBorder + 4
            dotrect.height = bmp.GetHeight() - self._tBorder + 4
        
            dc.SetPen(wx.Pen((self.IsSelected(index) and [colour] or [wx.LIGHT_GREY])[0],
                             0, wx.SOLID))       
            dc.SetBrush(wx.Brush(wx.BLACK, wx.TRANSPARENT))
        
            if self._tOutline == THUMB_OUTLINE_FULL or self._tOutline == THUMB_OUTLINE_RECT:

                imgRect.x = x
                imgRect.y = y
                imgRect.width = bmp.GetWidth() - self._tBorder
                imgRect.height = bmp.GetHeight() - self._tBorder

                if self._tOutline == THUMB_OUTLINE_RECT:
                    imgRect.height = self._tHeight             

            dc.SetBrush(wx.TRANSPARENT_BRUSH)

            if selected:

                dc.SetPen(self.grayPen)

                if 'phoenix' in wx.PlatformInfo:
                    dc.DrawRoundedRectangle(dotrect, 2)
                else :
                    dc.DrawRoundedRectangleRect(dotrect, 2)
                
                dc.SetPen(wx.Pen(wx.WHITE))
                dc.DrawRectangle(imgRect.x, imgRect.y,
                                 imgRect.width, imgRect.height)

                pen = wx.Pen((selected and [colour] or [wx.LIGHT_GREY])[0], 2)
                pen.SetJoin(wx.JOIN_MITER)
                dc.SetPen(pen)
                if self._tOutline == THUMB_OUTLINE_FULL:
                    dc.DrawRoundedRectangle(imgRect.x - 1, imgRect.y - 1,
                                            imgRect.width + 3, imgRect.height + 3, 2)
                else:
                    dc.DrawRectangle(imgRect.x - 1, imgRect.y - 1,
                                     imgRect.width + 3, imgRect.height + 3)
            else:
                dc.SetPen(wx.Pen(wx.LIGHT_GREY))

                dc.DrawRectangle(imgRect.x - 1, imgRect.y - 1,
                                 imgRect.width + 2, imgRect.height + 2)

        if 'phoenix' not in wx.PlatformInfo:
            dc.EndDrawing()
        dc.SelectObject(wx.NullBitmap)


    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.PaintEvent` event to be processed.
        """
        
        paintRect = self.GetPaintRect()
        
        dc = wx.BufferedPaintDC(self)
        self.PrepareDC(dc)

        dc.SetPen(wx.Pen(wx.BLACK, 0, wx.TRANSPARENT))
        dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.SOLID))

        w, h = self.GetClientSize()        

        # items
        row = -1
        xwhite = self._tBorder

        for ii in range(len(self._items)):

            col = ii%self._cols
            if col == 0:
                row = row + 1
                
            xwhite = ((w - self._cols*(self._tWidth + self._tBorder)))/(self._cols+1)
            tx = xwhite + col*(self._tWidth + self._tBorder)

            ty = self._tBorder/2 + row*(self._tHeight + self._tBorder) + \
                 self.GetCaptionHeight(0, row)
            tw = self._tWidth + self._tBorder
            th = self._tHeight + self.GetCaptionHeight(row) + self._tBorder
            # visible?
            if not paintRect.Intersects(wx.Rect(int(tx), int(ty), int(tw), int(th))):
                continue

            if 'phoenix' in wx.PlatformInfo:
                thmb = wx.Bitmap(tw, th)
            else :
                thmb = wx.EmptyBitmap(tw, th)

            self.DrawThumbnail(thmb, self._items[ii], ii)
            dc.DrawBitmap(thmb, int(tx), int(ty))
  
        rect = wx.Rect(int(xwhite), int(self._tBorder/2),
                       self._cols*(self._tWidth + self._tBorder),
                       self._rows*(self._tHeight + self._tBorder) + \
                       self.GetCaptionHeight(0, self._rows))
        
        w = max(self.GetClientSize().GetWidth(), rect.width)
        h = max(self.GetClientSize().GetHeight(), rect.height)
        dc.DrawRectangle(0, 0, w, rect.y)
        dc.DrawRectangle(0, 0, rect.x, h)
        dc.DrawRectangle(rect.GetRight(), 0, w - rect.GetRight(), h + 50)
        dc.DrawRectangle(0, rect.GetBottom(), w, h - rect.GetBottom() + 50)
       
        col = len(self._items)%self._cols

        if col > 0:
            rect.x = rect.x + col*(self._tWidth + self._tBorder)
            rect.y = rect.y + (self._rows - 1)*(self._tHeight + self._tBorder) + \
                     self.GetCaptionHeight(0, self._rows - 1)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
                dc.DrawRectangleRect(rect)


    def OnResize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.SizeEvent` event to be processed.
        """
        
        self.UpdateProp()
        self.ScrollToSelected()
        self.Refresh()


    def OnMouseDown(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN`` and ``wx.EVT_RIGHT_DOWN`` events for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.
        """
        
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)
        # get item number to select
        lastselected = self._selected
        self._selected = self.GetItemIndex(x, y)
        
        self._mouseeventhandled = False
        update = False

        if event.ControlDown():
            if self._selected == -1:
                self._mouseeventhandled = True
            elif not self.IsSelected(self._selected):
                self._selectedarray.append(self._selected)
                update = True
                self._mouseeventhandled = True

        elif event.ShiftDown():
            if self._selected != -1:
                begindex = self._selected
                endindex = lastselected
                if lastselected < self._selected:
                    begindex = lastselected
                    endindex = self._selected
                self._selectedarray = []

                for ii in range(begindex, endindex+1):
                    self._selectedarray.append(ii)

                update = True
                
            self._selected = lastselected
            self._mouseeventhandled = True
                    
        else:

            if self._selected == -1:
                update = len(self._selectedarray) > 0
                self._selectedarray = []
                self._mouseeventhandled = True
            elif len(self._selectedarray) <= 1:
                try:
                    update = len(self._selectedarray)== 0 or self._selectedarray[0] != self._selected
                except:
                    update = True
                self._selectedarray = []
                self._selectedarray.append(self._selected)
                self._mouseeventhandled = True
        
        if update:
            self.ScrollToSelected()
            self.Refresh()
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)

        self.SetFocus()
        

    def OnMouseUp(self, event):
        """
        Handles the ``wx.EVT_LEFT_UP`` and ``wx.EVT_RIGHT_UP`` events for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.
        """
        
        # get item number to select
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)
        lastselected = self._selected
        self._selected = self.GetItemIndex(x,y)

        if not self._mouseeventhandled:
            # set new selection
            if event.ControlDown():
                if self._selected in self._selectedarray:
                    self._selectedarray.remove(self._selected)
                    
                self._selected = -1
            else:
                self._selectedarray = []
                self._selectedarray.append(self._selected)

            self.ScrollToSelected()
            self.Refresh()
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)

        # Popup menu
        if event.RightUp():
            if self._selected >= 0 and self._pmenu:
                self.PopupMenu(self._pmenu, event.GetPosition())
            elif self._selected >= 0 and not self._pmenu and self._gpmenu:
                self.PopupMenu(self._gpmenu, event.GetPosition())
            elif self._selected == -1 and self._gpmenu:
                self.PopupMenu(self._gpmenu, event.GetPosition())

        if event.ShiftDown():
            self._selected = lastselected


    def OnMouseDClick(self, event):
        """
        Handles the ``wx.EVT_LEFT_DCLICK`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.
        """
        
        eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_DCLICK, self.GetId())
        self.GetEventHandler().ProcessEvent(eventOut)


    def OnMouseMove(self, event):
        """
        Handles the ``wx.EVT_MOTION`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.
        """
        
        # -- drag & drop --
        if self._dragging and event.Dragging() and len(self._selectedarray) > 0:

            files = wx.FileDataObject()
            for ii in range(len(self._selectedarray)):
                files.AddFile(opj(self.GetSelectedItem(ii).GetFullFileName()))
                
            source = wx.DropSource(self)
            source.SetData(files)
            source.DoDragDrop(wx.Drag_DefaultMove)

        # -- light-effect --
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)

        # get item number
        sel = self.GetItemIndex(x, y)

        if sel == self._pointed:
            if self._enabletooltip and sel >= 0:
                if not hasattr(self, "_tipwindow"):
                    self._tipwindow = wx.ToolTip(self.GetThumbInfo(sel))
                    self._tipwindow.SetDelay(1000)
                    self.SetToolTip(self._tipwindow)
                else:
                    self._tipwindow.SetDelay(1000)
                    self._tipwindow.SetTip(self.GetThumbInfo(sel))
                    
            event.Skip()
            return

        if self._enabletooltip:
            if hasattr(self, "_tipwindow"):
                self._tipwindow.Enable(False)
                
        # update thumbnail
        self._pointed = sel

        if self._enabletooltip and sel >= 0:
            if not hasattr(self, "_tipwindow"):
                self._tipwindow = wx.ToolTip(self.GetThumbInfo(sel))
                self._tipwindow.SetDelay(1000)
                self._tipwindow.Enable(True)
                self.SetToolTip(self._tipwindow)
            else:
                self._tipwindow.SetDelay(1000)
                self._tipwindow.Enable(True)
                self._tipwindow.SetTip(self.GetThumbInfo(sel))
            
        self.Refresh()
        eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_POINTED, self.GetId())
        self.GetEventHandler().ProcessEvent(eventOut)
        event.Skip()
        

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.
        """

        if self._pointed != -1:

            self._pointed = -1
            self.Refresh()
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_POINTED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)
  

    def OnThumbChanged(self, event):
        """
        Handles the ``EVT_THUMBNAILS_THUMB_CHANGED`` event for L{ThumbnailCtrl}.

        :param `event`: a L{ThumbnailEvent} event to be processed.
        """
        
        for ii in range(len(self._items)):
            if self._items[ii].GetFileName() == event.GetString():

                self._items[ii].SetFilename(self._items[ii].GetFileName())
                if event.GetClientData():

                    img = wx.Image(event.GetClientData())
                    self._items[ii].SetImage(img)

        self.Refresh()


    def OnChar(self, event):
        """
        Handles the ``wx.EVT_CHAR`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.KeyEvent` event to be processed.

        :note: You have these choices:

         (1) ``d`` key rotates 90 degrees clockwise the selected thumbnails;
         (2) ``s`` key rotates 90 degrees counter-clockwise the selected thumbnails;
         (3) ``a`` key rotates 180 degrees the selected thumbnails;
         (4) ``Del`` key deletes the selected thumbnails;
         (5) ``+`` key zooms in;
         (6) ``-`` key zooms out.
        """

        if event.m_keyCode == ord("s"):
            self.Rotate()
        elif event.m_keyCode == ord("d"):
            self.Rotate(270)
        elif event.m_keyCode == ord("a"):
            self.Rotate(180)
        elif event.m_keyCode == wx.WXK_DELETE:
            self.DeleteFiles()
        elif event.m_keyCode in [wx.WXK_ADD, wx.WXK_NUMPAD_ADD]:
            self.ZoomIn()
        elif event.m_keyCode in [wx.WXK_SUBTRACT, wx.WXK_NUMPAD_SUBTRACT]:
            self.ZoomOut()
            
        event.Skip()
                            

    def Rotate(self, angle=90):
        """
        Rotates the selected thumbnails by the angle specified by `angle`.

        :param `angle`: the rotation angle for the thumbnail, in degrees.
        """
        
        wx.BeginBusyCursor()

        count = 0
        selected = []
        
        for ii in range(len(self._items)):
            if self.IsSelected(ii):
                selected.append(self._items[ii])

        dlg = wx.ProgressDialog("Thumbnail Rotation",
                                "Rotating Thumbnail... Please Wait",
                                maximum = len(selected)+1,
                                parent=None)

        for thumb in selected:
            count = count + 1
            if TN_USE_PIL:
                newangle = thumb.GetRotation()*180/pi + angle
                fil = opj(thumb.GetFullFileName())
                pil = Image.open(fil).rotate(newangle)
                img = wx.EmptyImage(pil.size[0], pil.size[1])
                img.SetData(pil.convert('RGB').tobytes())
                thumb.SetRotation(newangle*pi/180)
            else:
                img = thumb._threadedimage
                newangle = thumb.GetRotation() + angle*pi/180
                thumb.SetRotation(newangle)
                img = img.Rotate(newangle, (img.GetWidth()/2, img.GetHeight()/2), True)
                
            thumb.SetRotatedImage(img)
            dlg.Update(count)

        wx.EndBusyCursor()
        dlg.Destroy()
        
        if self.GetSelection() != -1:
            self.Refresh()                


    def DeleteFiles(self):
        """
        Deletes the selected thumbnails and their associated files.

        :warning: This method deletes the original files too.
        """

        dlg = wx.MessageDialog(self, 'Are you sure you want to delete the files?',
                               'Confirmation',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            errordelete = []
            count = 0

            dlg.Destroy()
            
            wx.BeginBusyCursor()
            
            for ii in range(len(self._items)):
                if self.IsSelected(ii):
                    thumb = self._items[ii]
                    files = self._items[ii].GetFullFileName()
                    filename = opj(files)
                    try:
                        os.remove(filename)
                        count = count + 1
                    except:
                        errordelete.append(files)                        

            wx.EndBusyCursor()

            if errordelete:
                strs = "Unable to remove the following files:\n\n"
                for fil in errordelete:
                    strs = strs + fil + "\n"
                strs = strs + "\n"
                strs = strs + "Please check your privileges and file permissions."
                dlg = wx.MessageDialog(self, strs,
                                       'Error in removing files',
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

            if count:
                self.UpdateShow()


    def OnMouseWheel(self, event):
        """
        Handles the ``wx.EVT_MOUSEWHEEL`` event for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.

        :note: If you hold down the ``Ctrl`` key, you can zoom in/out with the mouse wheel.
        """
        
        if event.ControlDown():
            if event.GetWheelRotation() > 0:
                self.ZoomIn()
            else:
                self.ZoomOut()
        else:
            event.Skip()


    def ZoomOut(self):
        """ Zooms the thumbnails out. """
        
        w, h, b = self.GetThumbSize()

        if w < 40 or h < 40:
            return
        
        zoom = self.GetZoomFactor()
        neww = float(w)/zoom
        newh = float(h)/zoom

        self.SetThumbSize(int(neww), int(newh))
        self.OnResize(None)
        self._checktext = True
        
        self.Refresh()


    def ZoomIn(self):
        """ Zooms the thumbnails in. """
        
        size = self.GetClientSize()
        w, h, b = self.GetThumbSize()
        zoom = self.GetZoomFactor()
        
        if w*zoom + b > size.GetWidth() or h*zoom + b > size.GetHeight():
            if w*zoom + b > size.GetWidth():
                neww = size.GetWidth() - 2*self._tBorder
                newh = (float(h)/w)*neww
            else:
                newh = size.GetHeight() - 2*self._tBorder
                neww = (float(w)/h)*newh

        else:
            neww = float(w)*zoom
            newh = float(h)*zoom

        self.SetThumbSize(int(neww), int(newh))
        self.OnResize(None)
        self._checktext = True

        self.Refresh()



