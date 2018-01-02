#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Locations_demandes
from Utils import UTILS_Dialogs


class Panel(wx.Panel):
    def __init__(self, parent, bordure=0):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.bordure = bordure

        # Filtres
        self.check_attente_avec_possibilites = wx.CheckBox(self, -1, _(u"Avec disponibilités"))
        self.check_attente_sans_possibilites = wx.CheckBox(self, -1, _(u"Sans disponibilités"))
        self.check_attente_refusees = wx.CheckBox(self, -1, _(u"Refusées"))
        self.check_attente_attribuees = wx.CheckBox(self, -1, _(u"Attribuées"))

        self.check_attente_avec_possibilites.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.check_attente_sans_possibilites.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.check_attente_refusees.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.check_attente_attribuees.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))

        # Liste des demandes de locations
        self.ctrl_listview = OL_Locations_demandes.ListView(self, id=-1, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((50, 50))
        self.ctrl_recherche = OL_Locations_demandes.CTRL_Outils(self, listview=self.ctrl_listview)
        self.ctrl_recherche.SetMinSize((10, -1))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.check_attente_avec_possibilites)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.check_attente_sans_possibilites)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.check_attente_refusees)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.check_attente_attribuees)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Supprimer, self.bouton_supprimer)

        self.__set_properties()
        self.__do_layout()

        # Init
        self.check_attente_avec_possibilites.SetValue(True)
        self.check_attente_sans_possibilites.SetValue(True)

    def __set_properties(self):
        self.check_attente_avec_possibilites.SetToolTip(wx.ToolTip(_(u"Inclure les demandes en attente avec disponibilités")))
        self.check_attente_sans_possibilites.SetToolTip(wx.ToolTip(_(u"Inclure les demandes en attente sans disponibilités")))
        self.check_attente_refusees.SetToolTip(wx.ToolTip(_(u"Inclure les demandes refusées")))
        self.check_attente_attribuees.SetToolTip(wx.ToolTip(_(u"Inclure les demandes déjà attribuées")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une demande de location")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la demande de location sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la demande de location sélectionnée dans la liste")))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)

        # Filtres
        grid_sizer_filtres = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_filtres.Add(self.check_attente_avec_possibilites, 0, 0, 0)
        grid_sizer_filtres.Add(self.check_attente_sans_possibilites, 0, 0, 0)
        grid_sizer_filtres.Add(self.check_attente_refusees, 0, 0, 0)
        grid_sizer_filtres.Add(self.check_attente_attribuees, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_filtres, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)

        # Liste des demandes
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Commandes de liste
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.EXPAND, 0)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, self.bordure)

        self.SetSizer(sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()

    def OnCheckOptions(self, event=None):
        liste_options = []
        if self.check_attente_avec_possibilites.GetValue() == True :
            liste_options.append("disponibilite")
        if self.check_attente_sans_possibilites.GetValue() == True :
            liste_options.append("attente")
        if self.check_attente_refusees.GetValue() == True :
            liste_options.append("refusee")
        if self.check_attente_attribuees.GetValue() == True :
            liste_options.append("attribuee")
        self.ctrl_listview.SetOptions(liste_options)
        self.ctrl_listview.MAJ()

    def MAJ(self):
        self.OnCheckOptions(None)



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici visualiser, saisir, modifier ou supprimer des demandes de locations.")
        titre = _(u"Liste des demandes de locations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Location_demande.png")

        self.panel = Panel(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)

        # Init
        self.panel.MAJ()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((940, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Panel contenu
        grid_sizer_base.Add(self.panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

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
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
