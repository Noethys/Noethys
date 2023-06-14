#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Site internet :  www.noethys.com
# Auteur:           Noethys
# Copyright:       (c) 2012 Noethys
# Licence:         Licence wxWidgets
# Based on wx.lib.ticker by Chris Mellon
#-----------------------------------------------------------


import wx
from Ctrl import CTRL_Bouton_image
from wx.lib.wordwrap import wordwrap

if 'phoenix' in wx.PlatformInfo:
    from wx import Control
else :
    from wx import PyControl as Control


class Newsticker(Control):
    def __init__(self, 
            parent, 
            id=-1, 
            pages=[],                             # list of pages or a text
            fgcolor = wx.BLACK,             # text/foreground color
            bgcolor = None,                     # background color
            start=True,                             # if True, the newsticker starts immediately
            ppf=2,                                  # pixels per frame
            fps=20,                                 # frames per second
            pauseTime = 2000,              # Pause time (in milliseconds)
            headingStyle = 5,                 # Style of heading  : 1, 2, 3, 4 ou 5 or None for no heading
            pos=wx.DefaultPosition, 
            size=wx.DefaultSize, 
            style=wx.NO_BORDER, 
            name="Newsticker"
        ):
        Control.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)
        self.timer = wx.Timer(self, -1)
        self.timerPause = wx.Timer(self, -1)
        self.textSize = (-1, -1) 
        self.decalage = 0
        self._fps = fps  
        self._ppf = ppf 
        self.pauseTime = pauseTime
        self.pause = False 
        self.pauseTemp = False
        self.indexPage = 0
        self.headingStyle = headingStyle
        self.headingHeight = 0
        self.SetPages(pages)
        self.SetInitialSize(size)
        
        if fgcolor != None :
            self.SetForegroundColour(fgcolor)
        if bgcolor != None :
            self.SetBackgroundColour(bgcolor)
            
        self.Bind(wx.EVT_TIMER, self.OnTick, self.timer)
        self.Bind(wx.EVT_TIMER, self.OnPause, self.timerPause)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        if start:
            self.Start()

    def SetPages(self, pages=[], restart=False):
        """ Set Pages to display """
        if restart == True :
            self.Restart() 
        self.indexPage = 0
        self.listePages = []
        if type(pages) in (list, tuple) :
            if len(pages) == 0 :
                pages = [wx.EmptyString,]
            self.listePages = pages
        else :
             self.listePages = [pages,]
        self.SetText(self.listePages[0])

    def OnEnter(self, event):
        """ When mouse enters control """
        if self.timerPause.IsRunning() :
            self.timerPause.Stop()
        self.pause = True
        
    def OnLeave(self, event):
        """ When mouse leaves control """
        if self.timerPause.IsRunning() == False :
            self.pause = False
            
    def Stop(self):
        """Stop moving the text"""
        self.timer.Stop()
        
    def Start(self):
        """Starts the text moving"""
        if not self.timer.IsRunning():
            self.timer.Start(int(1000 / self._fps))
    
    def IsTicking(self):
        """Is the ticker ticking? ie, is the text moving?"""
        return self.timer.IsRunning()
        
    def SetFPS(self, fps):
        """Adjust the update speed of the ticker"""
        self._fps = fps
        self.Stop()
        self.Start()
        
    def GetFPS(self):
        """Update speed of the ticker"""
        return self._fps
        
    def SetPPF(self, ppf):
        """Set the number of pixels per frame the ticker moves - ie, how "jumpy" it is"""
        self._ppf = ppf
        
    def GetPPF(self):
        """Pixels per frame"""
        return self._ppf
        
    def SetFont(self, font):
        """ Set Font """
        self.textSize = (-1, -1)
        wx.Control.SetFont(self, font)
    
    def SetPauseTime(self, milliseconds=2000):
        """ Set pause time in milliseconds """
        self.pauseTime = milliseconds
    
    def SetHeadingStyle(self, num=5):
        """ Set heading style : None, 1, 2, 3, 4, or 5 """
        self.headingStyle = num
        
    def SetText(self, text):
        """Set the ticker text."""
        self._text = text
        self.textSize = (-1, -1)
        if not self._text:
            self.Refresh() 
            
    def GetText(self):
        """ Return actual page """
        return self._text
        
    def GetNextPage(self):
        """ Get the next page to display """
        if self.indexPage == len(self.listePages) - 1 :
            self.indexPage = 0
        else :
            self.indexPage += 1
        return self.listePages[self.indexPage]
        
    def UpdateExtent(self, dc, texte=""):
        """Updates the cached text extent if needed"""
        if not texte:
            self.textSize = (-1, -1)
            return
        if 'phoenix' in wx.PlatformInfo:
            largeurBloc, hauteurBloc, hauteurLigne = dc.GetFullMultiLineTextExtent(texte, dc.GetFont())
        else :
            largeurBloc, hauteurBloc, hauteurLigne = dc.GetMultiLineTextExtent(texte, dc.GetFont())
        self.textSize = (largeurBloc, hauteurBloc)
            
    def DrawText(self, dc):
        """Draws the ticker text at the current offset using the provided DC"""
        defaultFont = self.GetFont()
        dc.SetFont(defaultFont)
        
        # Extrait le titre s'il y en a un
        titre = u""
        try :
            if self._text.startswith("<t>") and "</t>" in self._text :
                position = self._text.index("</t>")
                titre = self._text[3:position]
                texte = self._text[position+4:]
            else :
                texte = self._text
        except :
            texte = ""
            
        # Adapte la longueur du texte
        texte = wordwrap(texte, self.GetSize()[0], dc, breakLongWords=True)
        self.UpdateExtent(dc, texte)
        
        # Calcule le dÃ©calage Ã  appliquer
        y = self.GetSize()[1] - self.decalage
        
        # Titre
        self.headingHeight = 0
        if len(titre) > 0 :
            
            # Titre - Style 1
            if self.headingStyle == 1 :
                dc.SetBrush(wx.Brush((200, 200, 200)))
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.DrawRectangle(0, y+8, dc.GetTextExtent(titre)[0] + 20, 10)
                dc.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                dc.SetTextForeground(self.GetBackgroundColour())
                dc.DrawText(titre, 10, y+6)
                self.headingHeight = 21

            # Titre - Style 2
            if self.headingStyle == 2 :
                dc.SetBrush(wx.Brush((200, 200, 200)))
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                dc.DrawRectangle(0, y+13, dc.GetTextExtent(titre)[0] + 15, 1)
                dc.SetTextForeground((200, 200, 200))
                dc.DrawText(titre, 0, y)
                self.headingHeight = 16

            # Titre - Style 3
            if self.headingStyle == 3 :
                dc.SetBrush(wx.Brush((200, 200, 200)))
                dc.SetPen(wx.Pen((200, 200, 200)))
                dc.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                largeurTitre, hauteurTitre = dc.GetTextExtent(titre)
                yTitre = 7
                dc.DrawLine(0, y+yTitre, 10, y+yTitre) 
                dc.DrawLine(largeurTitre + 14, y+yTitre, largeurTitre + 24, y+yTitre) 
                dc.SetTextForeground((200, 200, 200))
                dc.DrawText(titre, 12, y)
                self.headingHeight = 14

            # Titre - Style 4
            if self.headingStyle == 4 :
                dc.SetBrush(wx.Brush((200, 200, 200)))
                dc.SetPen(wx.Pen((200, 200, 200)))
                dc.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                dc.DrawRectangle(2, y+5, 3, 3)
                dc.SetTextForeground((200, 200, 200))
                dc.DrawText(titre, 7, y)
                self.headingHeight = 12

            # Titre - Style 5
            if self.headingStyle == 5 :
                dc.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                dc.SetTextForeground((200, 200, 200))
                dc.DrawText(titre, 0, y)
                self.headingHeight = 13
        
        # Texte
        dc.SetTextForeground(self.GetForegroundColour())
        dc.SetFont(defaultFont)
        dc.DrawLabel(texte, wx.Rect(x=0, y=y+self.headingHeight, width=self.GetSize()[0], height=self.GetSize()[1]))
    
    def OnPause(self, event):
        self.pause = False
        self.pauseTemp = True
        self.timerPause.Stop()
    
    def Restart(self):
        """ Restart the loop """
        self.timerPause.Stop()
        self.decalage = 0
        self.pauseTemp = False
        self.pause = False
        
    def OnTick(self, evt):
        """ Calcul du dÃ©calage """  
        # DÃ©filement continu
        if self.pause == False :
            self.decalage += self._ppf
            yHautBloc = self.GetSize()[1] - self.decalage + self.headingHeight
            yBasBloc = yHautBloc + self.textSize[1]
            if yBasBloc < 0 :
                self.decalage = 0
                self.pauseTemp = False
                # Changement de texte
                self.SetText(self.GetNextPage())
        
        # Calcul du dÃ©calage
        yHautBloc = self.GetSize()[1] - self.decalage
        yBasBloc = yHautBloc + self.textSize[1] + self.headingHeight

        # Pause
        if self.pauseTime > 0  and yHautBloc < 2 and self.pause == False and self.pauseTemp == False :
            self.pause = True
            self.pauseTemp = True
            self.timerPause.Start(self.pauseTime)

        self.Refresh()
        
    def OnPaint(self, evt):
        try :
            dc = wx.BufferedPaintDC(self)
            brush = wx.Brush(self.GetBackgroundColour())
            dc.SetBackground(brush)
            dc.Clear()
            self.DrawText(dc)
        except :
            pass
        
    def OnErase(self, evt):
        """Noop because of double buffering"""
        pass

    def AcceptsFocus(self):
        """Non-interactive, so don't accept focus"""
        return False
        
    def DoGetBestSize(self):
        """Width we don't care about, height is either -1, or the character
        height of our text with a little extra padding
        """
        return (100, 50)

    def ShouldInheritColours(self): 
        """Don't get colours from our parent..."""
        return False
        


if __name__ == '__main__':
    """ DEMO FRAME"""
    app = wx.App()
    f = wx.Frame(None)
    p = wx.Panel(f)
    pages = ["<t>PAGE 1</t>This is the first page.", "<t>PAGE 2</t>This is the second page\nwith multiline text.", "This page is without heading"] 
    t = Newsticker(p, pages=pages)
    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(t, flag=wx.GROW, proportion=1)
    p.SetSizer(s)
    f.Show()
    app.MainLoop()
    
    
