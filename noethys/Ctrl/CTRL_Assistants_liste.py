#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import sys
if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC

# Import des assistants pour pouvoir les inclure dans la compilation windows
from Ctrl import CTRL_Assistant_annuelle
from Ctrl import CTRL_Assistant_sejour
from Ctrl import CTRL_Assistant_stage
from Ctrl import CTRL_Assistant_cantine
from Ctrl import CTRL_Assistant_sorties


LISTE_ASSISTANTS = [
    {"code": "nouveau", "image": "Generation.png", "nom": _(u"Créer une nouvelle activité"),
     "description": _(u"Personnalisez votre nouvelle activité de A à Z")},

    {"code": "annuelle", "image": "Basket.png", "nom": _(u"Une activité culturelle ou sportive annuelle"),
     "description": _(u"Assistant pour créer une activité annuelle : club de gym, danse, couture, etc...")},

    {"code": "sejour", "image": "Camping.png", "nom": _(u"Un séjour"),
     "description": _(u"Assistant pour créer un séjour, un camp, un mini-camp...")},

    {"code": "stage", "image": "Guitare.png", "nom": _(u"Un stage"),
     "description": _(u"Assistant pour créer un stage de théâtre, de danse, de guitare, etc...")},

    {"code": "cantine", "image": "Repas.png", "nom": _(u"Une cantine"),
     "description": _(u"Assistant pour créer une cantine avec un ou plusieurs services")},

    {"code": "sorties", "image": "Bus.png", "nom": _(u"Des sorties familiales"),
     "description": _(u"Assistant pour créer une activité de gestion de sorties familiales...")},

]


class FirstColumnRenderer(object):
    def __init__(self, parent, dictItem={}):
        self.parent = parent

        self.normalFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.normalFont.SetPointSize(self.normalFont.GetPointSize() + 2)        
        self.smallerFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.greyColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

        self.code = dictItem["code"]
        self.icon = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % dictItem["image"]))
        self.text = dictItem["nom"]
        self.description = dictItem["description"]
        

    def DrawSubItem(self, dc, rect, line, highlighted, enabled):
        # Icone
        bmpWidth, bmpHeight = self.icon.GetWidth(), self.icon.GetHeight()
        dc.DrawBitmap(self.icon, rect.x+8, rect.y+(rect.height-bmpHeight)/2)

        # Titre
        dc.SetFont(self.normalFont)
        textWidth, textHeight = dc.GetTextExtent(self.text)
        dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT))
        dc.DrawText(self.text, rect.x+bmpWidth+18, rect.y+(rect.height - textHeight)/4)

        # Description
        if self.description:
            dc.SetFont(self.smallerFont)
            textWidth, textHeight = dc.GetTextExtent(self.description)
            dc.SetTextForeground(self.greyColour)
            dc.DrawText(self.description, rect.x+bmpWidth+18, rect.y+3*(rect.height - textHeight)/4)
        

    def GetLineHeight(self):
        dc = wx.MemoryDC()
        if 'phoenix' in wx.PlatformInfo:
            dc.SelectObject(wx.Bitmap(100, 20))
        else :
            dc.SelectObject(wx.EmptyBitmap(100, 20))
        
        bmpWidth, bmpHeight = self.icon.GetWidth(), self.icon.GetHeight()

        dc.SetFont(self.normalFont)
        
        textWidth, textHeight = dc.GetTextExtent(self.text)

        dc.SetFont(self.smallerFont)
        textWidth, textHeight = dc.GetTextExtent(self.description)

        dc.SelectObject(wx.NullBitmap)

        return max(2*textHeight, bmpHeight) + 20
    

    def GetSubItemWidth(self):
        return 250
    



        
        
class CTRL(ULC.UltimateListCtrl):
    def __init__(self, parent):
        ULC.UltimateListCtrl.__init__(self, parent, -1, style=wx.BORDER_THEME, agwStyle=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.EnableSelectionVista()
        self.Remplissage()

    def Remplissage(self):
        """ Remplissage du contrôle """
        self.ClearAll()
        self.InsertColumn(0, "Column 1") 

        for dictItem in LISTE_ASSISTANTS:
            index = self.InsertStringItem(sys.maxint, "")

            klass = FirstColumnRenderer(self, dictItem)
            self.SetItemCustomRenderer(index, 0, klass)
            self.SetItemPyData(index, dictItem)

        self.SetColumnWidth(0, ULC.ULC_AUTOSIZE_FILL)

        self.SendSizeEvent()



        
# ----------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl = CTRL(panel)
        self.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.OnSelection, self.ctrl)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
    
    def OnSelection(self, event):
        index = self.ctrl.GetFirstSelected()
        print(self.ctrl.GetItemPyData(index))
        
        

if __name__ == '__main__':
    app = wx.App(0)
    frame_1 = MyFrame(None, -1, "TEST", size=(600, 600))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()