#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Locations_tableau
from Ctrl import CTRL_Locations_tableau_options
from Utils import UTILS_Dialogs



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Bandeau
        intro = _(u"Vous pouvez ici consulter les locations sous forme de tableau. Pour ajouter une location, vous pouvez double-cliquer sur une ligne ou conserver la touche CTRL du clavier enfoncée tout en cliquant sur le bouton gauche de la souris afin de dessiner la barre directement dans le tableau. Pour modifier une location affichée, double-cliquez sur la barre représentant celle-ci. Il est également possible d'accéder à un menu contextuel avec le bouton droit de la souris.")
        titre = _(u"Tableau des locations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_horizontal.png")
        
        # Tableau
        self.ctrl_tableau = CTRL_Locations_tableau.CTRL(self)
        self.ctrl_options = CTRL_Locations_tableau_options.CTRL(self, ctrl_tableau=self.ctrl_tableau)
        self.ctrl_tableau.ctrl_options = self.ctrl_options
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_apercu = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

        # Init
        self.ctrl_options.AppliquerParametres()
        #self.ctrl_tableau.MAJ()
        
    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le tableau affiché")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression du tableau")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((1100, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Tableau
        grid_sizer_base.Add(self.ctrl_options, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_tableau, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnClose(self, event):
        self.ctrl_options.MemoriseConfig()
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        event.Skip()

    def OnBoutonFermer(self, event):
        self.ctrl_options.MemoriseConfig()
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonImprimer(self, event):
        self.ctrl_tableau.ctrl_tableau.Imprimer(event)

    def OnBoutonApercu(self, event):
        self.ctrl_tableau.ctrl_tableau.Apercu(event)


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
