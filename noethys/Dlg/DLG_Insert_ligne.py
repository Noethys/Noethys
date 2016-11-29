#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image




class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        # Nbre de lignes
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Lignes"))
        self.label_nbre_lignes = wx.StaticText(self, -1, u"Saisissez le nombre de lignes à insérer :")
        self.ctrl_nbre_lignes = wx.SpinCtrl(self, -1, "1", size=(60, -1), style=wx.TE_PROCESS_ENTER)

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.radio_debut = wx.RadioButton(self, -1, _(u"Au début du tableau"), style=wx.RB_GROUP)
        self.radio_avant = wx.RadioButton(self, -1, _(u"Avant la ligne sélectionnée"))
        self.radio_apres = wx.RadioButton(self, -1, _(u"Après la ligne sélectionnée"))
        self.radio_fin = wx.RadioButton(self, -1, _(u"A la fin du tableau"))

        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.ctrl_nbre_lignes.Bind(wx.EVT_TEXT_ENTER, self.OnBoutonOk)

        self.ctrl_nbre_lignes.SetFocus()
        self.ctrl_nbre_lignes.SetSelection(-1, -1)
        self.radio_apres.SetValue(True)

    def __set_properties(self):
        self.SetTitle(_(u"Insérer des lignes"))
        self.ctrl_nbre_lignes.SetToolTipString(_(u"Saisissez le nombre de lignes à insérer"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nbre_lignes, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nbre_lignes, 0, 0, 0)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_options.Add(self.radio_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.radio_avant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.radio_apres, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.radio_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetMinSize((self.GetSize()))
        self.Layout()
        self.CenterOnScreen()

    def GetNbreLignes(self):
        return int(self.ctrl_nbre_lignes.GetValue())

    def GetOption(self):
        if self.radio_debut.GetValue() == True : return "debut"
        if self.radio_avant.GetValue() == True : return "avant"
        if self.radio_apres.GetValue() == True : return "apres"
        if self.radio_fin.GetValue() == True : return "fin"

    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
