#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import wx.html as html
import FonctionsPerso


TEXTE = u"""
<CENTER><IMG SRC="Images/80x80/Logo.png">
<BR>
<FONT SIZE=2>
<B>Ceci est un exemple de Titre</B><BR>
<BR><BR>
Ceci est un paragaphe
<BR><BR>
Et ceci est le deuxième paragraphe
<BR>
<A HREF="http://www.noethys.com">Cliquez ici pour accéder au lien</A>.
</FONT>
</CENTER>
"""


class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetPage(texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)
    
    def OnLinkClicked(self, link):
        FonctionsPerso.LanceFichierExterne(link.GetHref())
        
        
class Dialog(wx.Dialog):
    def __init__(self, parent, texte=u"", titre=u"Information", size=(360, 410), nePlusAfficher=False):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME)
        self.SetTitle(titre)
        self.size = size
        
        # Txt HTML
        self.ctrl_html = MyHtml(self, texte=texte, hauteur=30)
        
        # Boutons de commande
        self.check_nePlusAfficher = wx.CheckBox(self, -1, u"Ne plus afficher ce message")
        if nePlusAfficher == False :
            self.check_nePlusAfficher.Show(False) 
            
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY), size=(100, -1))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def __set_properties(self):
        self.check_nePlusAfficher.SetToolTipString(u"Cochez cette case pour ne plus afficher ce message")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour fermer ce message")
        self.SetMinSize(self.size)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_html, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.check_nePlusAfficher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_boutons.Add( (1, 1), 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnClose(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)
    
    def GetEtatNePlusAfficher(self):
        return self.check_nePlusAfficher.GetValue() 


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, texte=TEXTE, titre=u"Message", nePlusAfficher=True)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()