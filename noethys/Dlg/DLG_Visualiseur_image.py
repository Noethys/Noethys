#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image

ID_EXIT = 98
ID_UNDO = 99
ID_PLUS = 100
ID_MOINS = 101

phrase1 = _(u"Ramener l'image à sa taille d'origine")
phrase2 = _(u"Opération interdite")

try :
    if not wx.USE_UNICODE:
        phrase1 = phrase1.encode("iso8859-15", "replace")
        phrase1 = phrase1.encode("iso8859-15", "replace")
except :
    pass

def pil2wx(image):
    """Convert a PIL image to wx image format"""
    imagewx=wx.EmptyImage(image.size[0], image.size[1])
    imagewx.SetData(image.tobytes('raw', 'RGB'))
    return imagewx

##def pil2wx(image):
##    """Convert a PIL image to wx image format"""
##    largeur, hauteur = image.size
##    imagewx = wx.EmptyImage(largeur, hauteur)
##    imagewx.SetData(image.tobytes('raw', 'RGB'))
##    imagewx.SetAlphaData(image.convert("RGBA").tobytes()[3::4])
##    return imagewx        



class Visu(wx.ScrolledWindow):
    def __init__(self, conteneur):
        wx.ScrolledWindow.__init__(self, parent = conteneur)
        self.image = None

    def Affiche(self, bmp, ratio):
        if self.image != None :
            posX, posY = self.GetViewStart()
            self.image.Destroy()
            self.SetScrollRate(0, 0)
        else:
            posX = 0
            posY = 0
            self.bmp = bmp
        self.SetVirtualSize(wx.Size(bmp.GetWidth(), bmp.GetHeight()))
        self.image = wx.StaticBitmap(self, -1, bmp)
        self.SetScrollRate((10*ratio)/100, (10*ratio)/100)
        self.Scroll(posX, posY)
        self.Refresh()

    def Efface(self):
        self.image.Destroy()
        self.SetScrollRate(0, 0)


class MyFrame(wx.Frame):
    def __init__(self, parent, imgPIL=None, imgWX=None):
        wx.Frame.__init__(self, parent, -1, size = (800, 600))
        
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(_(u"Aperçu d'image"))
        
        self.imgORIG = None
        self.imgORIX = 0
        self.imgORIY = 0
        self.bmpRESU = None
        self.ratio = 100
        self.inc = 5

##        menuFichier = UTILS_Adaptations.Menu()
##        menuFichier.Append(wx.ID_OPEN, "&Ouvrir\tCTRL+o", "Ouvrir un fichier image")
##        menuFichier.Append(wx.ID_CLOSE, "&Fermer\tCTRL+f", "Fermer le fichier ouvert")
##        menuFichier.AppendSeparator()
##        menuFichier.Append(wx.ID_EXIT, "&Quitter\tCTRL+q", "Quitter l'application")
##
##        menuAfficher = wx.Menu(style = wx.MENU_TEAROFF)
##        menuAfficher.Append(wx.ID_UNDO,
##                    "&Taille d'origine\tCTRL+t",
##                    phrase1)
##        menuAfficher.Append(ID_PLUS, "&Agrandir\tCTRL+a", "Agrandir l'image")
##        menuAfficher.Append(ID_MOINS, "&Diminuer\tCTRL+a", "Diminuer l'image")
##
##        menuBarre = wx.MenuBar()
##        menuBarre.Append(menuFichier, "&Fichier")
##        menuBarre.Append(menuAfficher, "&Afficher")
##        self.SetMenuBar(menuBarre)

        self.barre = wx.StatusBar(self, -1)
        self.barre.SetFieldsCount(2)
        self.barre.SetStatusWidths([-1, -1])
        self.SetStatusBar(self.barre)

        outils = UTILS_Adaptations.ToolBar(self, -1, style = wx.TB_HORIZONTAL | wx.NO_BORDER)
        outils.AddLabelTool(ID_EXIT, _(u"Fermer l'aperçu"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Fermer.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Fermer"), "")
        outils.AddLabelTool(ID_PLUS, _(u"Agrandir"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_plus.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Agrandir"), "")
        outils.AddLabelTool(ID_UNDO, _(u"Taille originale"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_init.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Taille originale"), "")
        outils.AddLabelTool(ID_MOINS, _(u"Diminuer"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_moins.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Diminuer"), "")
        outils.Realize()
        self.SetToolBar(outils)

        sizer = wx.BoxSizer()
        self.panneau = Visu(self)
        sizer.Add(self.panneau, 1, wx.EXPAND|wx.ALL, 2)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.Retour, id=ID_UNDO)
        self.Bind(wx.EVT_MENU, self.Plus, id=ID_PLUS)
        self.Bind(wx.EVT_MENU, self.Moins, id=ID_MOINS)
        
        self.CenterOnScreen() 
        
        # Chargement de l'image PIL ou WX
        if imgPIL != None :
            self.ChargeImagePIL(imgPIL)
        if imgWX != None :
            self.ChargeImageWX(imgWX)

    def Retour(self, evt):
        if self.imgORIG != None:
            self.ratio = 100
            self.bmpRESU = self.imgORIG.ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX, self.imgORIY, self.ratio), 1)

    def Plus(self, evt):
        if self.imgORIG != None:
            self.ratio = self.ratio + self.inc
            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX, self.imgORIY, self.ratio), 1)

    def Moins(self, evt):
        if self.ratio > 5 and self.imgORIG != None:
            self.ratio = self.ratio - self.inc
            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX, self.imgORIY, self.ratio), 1)

    def OnOpen(self, evt):
        if self.imgORIG != None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord fermer l'image en cours d'utilisation"),
                       phrase2, style = wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.FileDialog(self, _(u"Choisissez un fichier"),
                    wildcard = "*.*",
                    style = wx.FD_OPEN)
            retour = dlg.ShowModal()
            chemin = dlg.GetPath()
            fichier = dlg.GetFilename()
            dlg.Destroy()
            if retour == wx.ID_OK and fichier != "":
                self.imgORIG = wx.Image(chemin, wx.BITMAP_TYPE_ANY)
                self.imgORIX = self.imgORIG.GetWidth()
                self.imgORIY = self.imgORIG.GetHeight()
                self.bmpRESU = self.imgORIG.ConvertToBitmap()
                self.panneau.Affiche(self.bmpRESU, self.ratio)
                self.SetTitle(_(u"Aperçu d'image [%s]")% fichier)
                self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX, self.imgORIY, self.ratio), 1)
    
    def ChargeImagePIL(self, imgPIL=None):
        img = pil2wx(imgPIL)
        self.imgORIG = img #wx.Image(chemin, wx.BITMAP_TYPE_ANY)
        self.imgORIX = self.imgORIG.GetWidth()
        self.imgORIY = self.imgORIG.GetHeight()
        self.bmpRESU = self.imgORIG.ConvertToBitmap()
        self.panneau.Affiche(self.bmpRESU, self.ratio)
        self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX, self.imgORIY, self.ratio), 1)

    def ChargeImageWX(self, imgWX=None):
        self.imgORIG = imgWX
        self.imgORIX = self.imgORIG.GetWidth()
        self.imgORIY = self.imgORIG.GetHeight()
        self.bmpRESU = self.imgORIG.ConvertToBitmap()
        self.panneau.Affiche(self.bmpRESU, self.ratio)
        self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX, self.imgORIY, self.ratio), 1)

    def OnClose(self, evt):
        if self.imgORIG != None :
            self.panneau.Efface()
            self.imgORIG = None
            self.imgORIX = 0
            self.imgORIY = 0
            self.bmpRESU = None
            self.ratio = 100
            self.SetTitle(_(u"Aperçu d'images"))
            self.barre.SetStatusText("", 1)

    def OnExit(self, evt):
        self.Destroy()



class MonApp(wx.App):
    def OnInit(self):
        #wx.InitAllImageHandlers()
        fen = MyFrame(None, imgPIL=None)
        fen.Show(True)
        self.SetTopWindow(fen)
        return True

if __name__ == u"__main__":
    app = MonApp()
    app.MainLoop()
