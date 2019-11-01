#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx

try :
    from wx import TaskBarIcon as TaskBarIcon
except :
    from wx.adv import TaskBarIcon as TaskBarIcon


class CustomTaskBarIcon():
    def __init__(self, parent=None):
        self.tbicon = TaskBarIcon()

        # Binds
        # wx.EVT_TASKBAR_LEFT_DCLICK(self.tbicon, self.OnTaskBarLeftDClick)
        # wx.EVT_TASKBAR_RIGHT_UP(self.tbicon, self.OnTaskBarRightClick)

    def Cacher(self):
        try :
            self.tbicon.RemoveIcon()
        except :
            pass

    def Detruire(self):
        try :
            self.tbicon.Destroy()
        except :
            pass

    def Connecthys(self, nbre=None, texte=""):
        if nbre not in (None, 0) :
            chemin_logo = Chemins.GetStaticPath("Images/16x16/Nomadhys.png")
            bmp = wx.Bitmap(chemin_logo, wx.BITMAP_TYPE_ANY)
            bmp = self.AjouteTexteImage(bmp, str(nbre), taille_police=6)
            self.SetIcone(bmp=bmp, texte=texte)
        else :
            self.Cacher()

    def SetIcone(self, bmp=None, texte=""):
        if 'phoenix' in wx.PlatformInfo:
            icon = wx.Icon()
        else:
            icon = wx.EmptyIcon()
        icon.CopyFromBitmap(bmp)
        self.tbicon.SetIcon(icon, texte)

    def AjouteTexteImage(self, image=None, texte="", alignement="droite-bas", padding=0, taille_police=9):
        """ Ajoute un texte sur une image bitmap """
        # Création du bitmap
        largeurImage, hauteurImage = image.GetSize()
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(largeurImage, hauteurImage)
        else:
            bmp = wx.EmptyBitmap(largeurImage, hauteurImage)
        mdc = wx.MemoryDC(bmp)
        dc = wx.GCDC(mdc)
        mdc.SetBackground(wx.Brush("black"))
        mdc.Clear()

        # Paramètres
        dc.SetBrush(wx.Brush(wx.RED))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        dc.SetTextForeground(wx.WHITE)

        # Calculs
        largeurTexte, hauteurTexte = dc.GetTextExtent(texte)

        # Image
        mdc.DrawBitmap(image, 0, 0)

        # Rond rouge
        hauteurRond = hauteurTexte + padding * 2
        largeurRond = largeurTexte + padding * 2 + hauteurRond/2.0
        if largeurRond < hauteurRond :
            largeurRond = hauteurRond

        if "gauche" in alignement : xRond = 1
        if "droite" in alignement : xRond = largeurImage - largeurRond - 1
        if "haut" in alignement : yRond = 1
        if "bas" in alignement : yRond = hauteurImage - hauteurRond - 1

        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRoundedRectangle(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)
        else:
            dc.DrawRoundedRectangleRect(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)

        # Texte
        xTexte = xRond + largeurRond / 2.0 - largeurTexte / 2.0
        yTexte = yRond + hauteurRond / 2.0 - hauteurTexte / 2.0 - 1
        dc.DrawText(texte, xTexte, yTexte)

        mdc.SelectObject(wx.NullBitmap)
        bmp.SetMaskColour("black")
        return bmp



        

if __name__ == u"__main__":
    app = wx.App(0)
    taskBarIcon = CustomTaskBarIcon()
    taskBarIcon.Connecthys(2, "2 demandes")
    app.MainLoop()
