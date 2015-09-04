#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import OL_Transfert_RIB
import wx.lib.agw.hyperlink as Hyperlink


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        if self.URL == "valides" :
            self.parent.ctrl_listview.CocheValides()
        if self.URL == "tout" :
            self.parent.ctrl_listview.CocheTout()
        if self.URL == "rien" :
            self.parent.ctrl_listview.CocheRien()
        self.UpdateLink()
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Utilisez cette fonctionnalité pour convertir les anciens RIB utilisés pour les prélèvements nationaux en mandats SEPA. Noethys a déjà sélectionné les RIB qui peuvent être convertis. Il ne vous reste plus qu'à cliquer sur le bouton VALIDER pour lancer la procédure. Attention, il est conseillé de faire une sauvegarde avant...")
        titre = _(u"Conversion des RIB nationaux en Mandats SEPA")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration.png")
        
        self.ctrl_listview = OL_Transfert_RIB.ListView(self, id=-1, style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_listview.SetMinSize((100, 100))
        self.ctrl_listview.MAJ() 
        self.ctrl_recherche = OL_Transfert_RIB.CTRL_Outils(self, listview=self.ctrl_listview)

        self.hyper_valides = Hyperlien(self, label=_(u"Cocher les valides"), infobulle=_(u"Cliquez ici pour cocher uniquement les valides"), URL="valides")
        self.label_separation1 = wx.StaticText(self, -1, "|")
        self.hyper_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation2 = wx.StaticText(self, -1, "|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Valider"), cheminImage="Images/32x32/Valider.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init
        self.ctrl_listview.CocheValides()

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour lancer la conversion des RIB en mandats SEPA"))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        grid_sizer_contenu.Add(self.ctrl_listview, 0, wx.EXPAND, 0)

        # Options de liste
        grid_sizer_options_liste = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5) 
        grid_sizer_options_liste.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_options_liste.Add((40, 5), 0, wx.EXPAND, 0)
        grid_sizer_options_liste.Add(self.hyper_valides, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_liste.Add(self.label_separation1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_liste.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_liste.Add(self.label_separation2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_liste.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_liste.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_options_liste, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        resultat = self.ctrl_listview.Conversion() 
        if resultat == True :
            self.EndModal(wx.ID_OK)            
        
        
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
