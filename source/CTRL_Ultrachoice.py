#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.combo
import wx.lib.wordwrap as wordwrap


class CTRL(wx.combo.OwnerDrawnComboBox):
    def __init__(self, parent, donnees=[], nbreLignesDescription=1, wrap=False, hauteur=None, style=wx.CB_READONLY) :
        self.donnees = donnees
        self.nbreLignesDescription = nbreLignesDescription
        if hauteur == None :
            self.hauteurItem = 33 + (self.nbreLignesDescription*14)
        else :
            self.hauteurItem = hauteur
        self.wrap = wrap
        self.selection = None
            
        # Init du contrôle
        listeLabels = []
        for donnee in self.donnees :
            listeLabels.append(donnee["label"])

        wx.combo.OwnerDrawnComboBox.__init__(self, parent, -1, choices=listeLabels, size=(-1, self.hauteurItem), style=style)

        self.Bind(wx.EVT_COMBOBOX, self.OnSelection)

    def OnSelection(self, event):
        self.selection = event.GetSelection() 
        event.Skip() 

    def SetDonnees(self, donnees):
        self.donnees = donnees
        listeLabels = []
        for donnee in self.donnees :
            listeLabels.append(donnee["label"])
        self.SetItems(listeLabels)
    
    def GetSelection2(self):
        return self.selection
    
    def SetSelection2(self, index=None):
        if index != None :
            self.Select(index)
            self.selection = index
        
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            self.selection = None
            return

        r = wx.Rect(*rect)  # make a copy
        r.Deflate(5, 5)
        
        if len(self.donnees) > 0 :
            dictItem = self.donnees[item]
            if flags & wx.combo.ODCB_PAINTING_CONTROL:
                # for painting the control itself
                self.selection = item
                self.DessineItemActif(dc, r, dictItem)
            else:
                # for painting the items in the popup
                self.DessineItem(dc, r, dictItem)
           
    def DessineItemActif(self, dc, r, dictItem):
        """ Dessine le contrôle """        
        self.DessineItem(dc, r, dictItem)
        
    def DessineItem(self, dc, r, dictItem):
        """ Dessine un item dans la liste popup """
        # Image
        if dictItem.has_key("image") == False or dictItem["image"] == None :
            tailleImage = (0, 0)
        else :
            tailleImage = dictItem["image"].GetSize()
            dc.DrawBitmap(dictItem["image"], r.x, (r.y + 0) + ( (r.height/2) - dc.GetCharHeight() )/2)
        
        # Dessin du label
        dc.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        dc.DrawText(dictItem["label"], r.x + tailleImage[0] + 4, (r.y + 0) + ( (r.height/2) - dc.GetCharHeight() )/2)
        
        # Dessin de la ligne
##        pen = wx.Pen(dc.GetTextForeground(), 0.5, wx.SOLID)
##        dc.SetPen(pen)
##        dc.DrawLine( r.x+5+ tailleImage[0], r.y+((r.height/4)*3)-8, r.x+r.width - 5, r.y+((r.height/4)*3)-8)
        
        # Dessin de la description
        description = dictItem["description"]
        dc.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        largeur = r.width - tailleImage[0] - 4
        description = wordwrap.wordwrap(description, largeur, dc)
        if self.wrap == False :
            if "\n" in description :
                description = u"%s..." % description[0:description.index("\n")-1]
            
            dc.DrawText(description, r.x + tailleImage[0] + 4, (r.y + 16) + ( (r.height/2) - dc.GetCharHeight() )/2)
        else :
            dc.DrawLabel(description, wx.Rect(r.x + tailleImage[0] + 4, (r.y + 16) + ( (r.height/2) - dc.GetCharHeight() )/2, r.width - tailleImage[0], self.nbreLignesDescription*15))
        
    
    def OnDrawBackground(self, dc, rect, item, flags):
        # If the item is selected, or its item # iseven, or we are painting the
        # combo control itself, then use the default rendering.
        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, rect, item, flags)
            return

        # Otherwise, draw every other background with different colour.
        bgCol = wx.Colour(240, 240, 250)
        dc.SetBrush(wx.Brush(bgCol))
        dc.SetPen(wx.Pen(bgCol))
        dc.DrawRectangleRect(rect);

    # Overridden from OwnerDrawnComboBox, should return the height
    # needed to display an item in the popup, or -1 for default
    def OnMeasureItem(self, item):
        # Simply demonstrate the ability to have variable-height items
        return self.hauteurItem

    # Overridden from OwnerDrawnComboBox.  Callback for item width, or
    # -1 for default/undetermined
    def OnMeasureItemWidth(self, item):
        return -1; # default - will be measured from text width
    

        

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        donnees = [
            {"image" : wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_ANY), "label" : _(u"Item 1"), "description" : _(u"Ceci est la description de l'item 1 qui est vraiment un texte très long qui devrait normalement dépasser.")} ,
            {"image" : wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_ANY), "label" : _(u"Item 2"), "description" : _(u"Ceci est la description de l'item 2")} ,
            {"image" : None, "label" : _(u"Item 3"), "description" : _(u"Ceci est la description de l'item 3")} ,
            {"label" : _(u"Item 4"), "description" : _(u"Ceci est la description de l'item 4")} ,
            ]
        self.ctrl1 = CTRL(panel, donnees=donnees, nbreLignesDescription=1)
        self.ctrl1.Select(0)
        
        donnees = []
        for x in range(1, 100) :
            donnees.append({"image" : wx.Bitmap("Images/32x32/Loupe.png", wx.BITMAP_TYPE_ANY), "label" : _(u"Item %d") % x, "description" : _(u"Ceci est la description de l'item %d") % x})
        self.ctrl2 = CTRL(panel, donnees=donnees)
##        self.ctrl2.Select(0)

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl1, 0, wx.ALL | wx.EXPAND, 10)
        sizer_2.Add(self.ctrl2, 0, wx.ALL | wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        
        self.Bind(wx.EVT_COMBOBOX, self.OnSelection2, self.ctrl2)

    def OnSelection2(self, event):
        print "Selection =", self.ctrl2.GetSelection2() 
        


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
