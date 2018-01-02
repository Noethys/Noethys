#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.html as html
import FonctionsPerso
import datetime


VERSION_LOGICIEL = FonctionsPerso.GetVersionLogiciel()
anneeActuelle = str(datetime.date.today().year)

TEXTE_ACCUEIL = u"""
<BR>
<B><FONT SIZE=6>NOETHYS</B></FONT><BR>
<B><FONT SIZE=4>Logiciel de gestion multi-activités</B></FONT><BR>
<FONT SIZE=2>
<B>Version %s</B><BR><BR>
<B>Copyright © 2010-%s Ivan LUCAS</B><BR>
<BR><BR>
<U>Remerciements :</U>
<BR><BR>
- Aurélie, pour son soutien et son aide technique<BR>
- Jacques Delage pour les beta-tests et les suggestions<BR>
- Robin Dunn, pour ses travaux et son aide sur wxPython<BR>
- Les communautés Python et wxPython<BR>
- Tous les beta-testeurs pour leur suggestions et leurs remarques<BR>
<BR>
Et en vrac : 
Guido van Rossum (Python), Gerhard Häring (pysqlite), <BR>
reportLab team (reportlab), Mark Hammond (pywin32), <BR>
Phillip Piper (ObjectListView), Armin Rigo (Psycho)...<BR>
</FONT>
""" % (VERSION_LOGICIEL,  anneeActuelle[2:])


class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetPage(texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)
    
    def OnLinkClicked(self, link):
        FonctionsPerso.LanceFichierExterne(_(u"http://www.noethys.com"))
        

class MargeGauche(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="marge_gauche", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.SetBackgroundColour("#548410")
        
        # Image de gauche
        self.image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Special/LogoMargeGauche.png"), wx.BITMAP_TYPE_ANY))


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        
        # Marge gauche
        self.margeGauche = MargeGauche(self)
        
        # Txt HTML
        texte = TEXTE_ACCUEIL
        self.ctrl_html = MyHtml(self, texte=texte, hauteur=30)
        
        # Boutons de commande
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def __set_properties(self):
        self.SetTitle(_(u"A propos"))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer cette fenêtre")))
        self.SetMinSize((600, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        
        # Marge gauche
        grid_sizer_base.Add(self.margeGauche, 1, wx.EXPAND, 0)
        
        # Grid sizer droit
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_droit.Add(self.ctrl_html, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(self.bouton_ok, 1, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 20)
        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
    
    
    def OnClose(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)
    


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()