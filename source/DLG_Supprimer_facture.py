#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

import CTRL_Bandeau
import GestionDB



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Supprimer_facture", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
            
        # Bandeau
        titre = _(u"Supprimer ou annuler des factures")
        intro = _(u"S�lectionnez l'action � effectuer. Attention, ces deux types d'actions sont irr�versibles !")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Fermer.png")

        self.bouton_annulation = wx.CommandLinkButton(self, -1, _(u"Annulation"), _("Cette action conservera les traces de la facture annul�e dans la base de donn�es. Les principales\ncaract�ristiques de la facture seront m�moris�es mais il sera impossible par exemple de l'imprimer\nou d'en consulter le d�tail. Cette action permet notamment de faire appara�tre les prestations\nassoci�es sur une nouvelle facture."))
        self.bouton_suppression = wx.CommandLinkButton(self, -1, _(u"Suppression"), _("Cette action supprimera totalement la facture. Seule une trace sera conserv�e dans l'historique.\nLe num�ro est susceptible d'�tre r�utilis� s'il s'agit de la derni�re facture g�n�r�e. Cette action peut\n�tre utilis�e par exemple pour supprimer une ou plusieurs factures qui viennent d'�tre g�n�r�es par\nerreur."))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnulation, self.bouton_annulation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSuppression, self.bouton_suppression)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_annulation.SetToolTipString(_(u"Cliquez ici pour annuler la ou les factures s�lectionn�es"))
        self.bouton_suppression.SetToolTipString(_(u"Cliquez ici pour supprimer totalement la ou les factures s�lectionn�es"))
        self.bouton_aide.SetToolTipString(_(u"Obtenir de l'aide"))
        self.bouton_annuler.SetToolTipString(_(u"Annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu.Add(self.bouton_annulation, 0, wx.EXPAND, 10)
        grid_sizer_contenu.Add(self.bouton_suppression, 0, wx.EXPAND, 10)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAnnulation(self, event): 
        self.EndModal(100)

    def OnBoutonSuppression(self, event): 
        self.EndModal(200)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
