#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.toasterbox as Toaster


def ToasterUtilisateur(parent, titre=u"", prenom=_(u"Philippe"), nomImage="Femme", taille=(200, 100), couleurFond="#000000"):
    """ Affiche une boîte de dialogue temporaire """
    largeur, hauteur = (400, 148) #taille
    tb = Toaster.ToasterBox(parent, Toaster.TB_COMPLEX, Toaster.TB_DEFAULT_STYLE, Toaster.TB_ONTIME) # TB_CAPTION
    tb.SetTitle(titre)
    tb.SetPopupSize((largeur, hauteur))
    largeurEcran, hauteurEcran = wx.ScreenDC().GetSizeTuple()
    tb.SetPopupPosition((largeurEcran-largeur-10, hauteurEcran-hauteur-50))
    tb.SetPopupPauseTime(3000)
    tb.SetPopupScrollSpeed(4)
    tb.SetPopupBackgroundColour(couleurFond)
    tb.SetPopupTextColour("#000000")
    
    tbpanel = tb.GetToasterBoxWindow()
    panel = wx.Panel(tbpanel, -1)
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizerHoriz = wx.BoxSizer(wx.HORIZONTAL)
    sizerTexte = wx.BoxSizer(wx.VERTICAL)
    
    # Image
    bmp = wx.StaticBitmap(panel, -1, wx.Bitmap("Images/Avatars/128x128/%s.png" % nomImage, wx.BITMAP_TYPE_PNG))
    sizerHoriz.Add(bmp, 0, wx.ALL, 10)
    
    # Texte1
    texte1 = _(u"Bonjour")
    label1 = wx.StaticText(panel, -1, texte1, style=wx.ALIGN_CENTER)
    label1.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
    label1.SetForegroundColour('Grey')
    sizerTexte.Add(label1, 1, wx.TOP | wx.EXPAND, 40)
    
    # Texte 2
    texte2 = prenom
    label2 = wx.StaticText(panel, -1, texte2, style=wx.ALIGN_CENTER)
    label2.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
    label2.SetForegroundColour('White')
    sizerTexte.Add(label2, 1, wx.TOP | wx.EXPAND, 0)
    
    sizerHoriz.Add(sizerTexte, 1, wx.EXPAND, 0)
    sizer.Add(sizerHoriz, 0, wx.EXPAND)
    panel.SetSizer(sizer)
    panel.Layout()
    
    tb.AddPanel(panel)
    
    tb.Play()


        

if __name__ == '__main__':
    app = wx.App(0)
    ToasterUtilisateur(None)
    app.MainLoop()
