#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Inscriptions_attente
from Ctrl import CTRL_Grille_periode



class Dialog(wx.Dialog):
    def __init__(self, parent, liste_activites=[], mode="attente"):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.mode = mode

        if self.mode == "attente" :
            label = _(u"en attente")
        else :
            label = _(u"refusées")
        
        intro = _(u"Vous pouvez ici consulter la liste des inscriptions %s. Si une coche verte apparaît en début de ligne, cela signifie qu'une place s'est libérée pour cet individu. Cliquez alors sur l'individu souhaité avec le bouton droit de la souris puis sélectionnez dans le menu contextuel la commande 'Ouvrir la fiche Famille'...") % label
        titre = _(u"Inscriptions %s") % label
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Liste_attente.png")

        # Périodes
        self.staticbox_periodes_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.ctrl_periodes = CTRL_Grille_periode.CTRL(self)
        self.ctrl_periodes.SetMinSize((220, 230))

        # PROVISOIRE
        self.staticbox_periodes_staticbox.Show(False)
        self.ctrl_periodes.Show(False)

        # Résultats
        self.staticbox_resultats_staticbox = wx.StaticBox(self, -1, titre)
        self.ctrl_attente = CTRL_Inscriptions_attente.CTRL(self, liste_activites=liste_activites, mode=self.mode)
        self.ctrl_attente.SetMinSize((100, 100))

        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_ouvrir_fiche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la fiche famille de l'individu sélectionné dans la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer cette liste (PDF)")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter les résultats au format MS Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((805, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)

        # Période
        staticbox_periodes = wx.StaticBoxSizer(self.staticbox_periodes_staticbox, wx.VERTICAL)
        staticbox_periodes.Add(self.ctrl_periodes, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_contenu.Add(staticbox_periodes, 1, wx.EXPAND, 0)

        # Résultats
        staticbox_resultats = wx.StaticBoxSizer(self.staticbox_resultats_staticbox, wx.VERTICAL)
        grid_sizer_resultats = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_resultats.Add(self.ctrl_attente, 0, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_commandes.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, wx.EXPAND, 0)
        grid_sizer_resultats.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)

        grid_sizer_resultats.AddGrowableRow(0)
        grid_sizer_resultats.AddGrowableCol(0)

        staticbox_resultats.Add(grid_sizer_resultats, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_contenu.Add(staticbox_resultats, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OuvrirFiche(self, event):
        self.ctrl_attente.OuvrirFicheFamille(None)

    def Imprimer(self, event):
        self.ctrl_attente.Imprimer(None)

    def OnBoutonExcel(self, event):
        self.ctrl_attente.ExportExcel()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesinscriptionsenattente")
        
# --------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, liste_activites=[1, 2, 3])
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
