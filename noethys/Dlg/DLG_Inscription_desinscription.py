#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# ------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activitÃ©s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
# ------------------------------------------------------------------------

import Chemins
import datetime
import wx

import GestionDB
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Utils.UTILS_Traduction import _
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        self.staticbox_remboursement_staticbox = wx.StaticBox(self, -1, _(u"Remboursement"))
        self.ctrl_remboursement = wx.CheckBox(self, -1, _(u"Générer un remboursement"))
        self.ctrl_remboursement.SetValue(0)

        self.label_motif = wx.StaticText(self, label=_(u"Motif du départ :"))
        self.ctrl_motif = wx.TextCtrl(self, -1, u"")
        self.label_total = wx.StaticText(self, label=_(u"Coût total de l'activité :"))
        self.ctrl_total = CTRL_Saisie_euros.CTRL(self)
        self.label_nb_seances = wx.StaticText(self, label=_(u"Nb séances effectuées :"))
        self.ctrl_nb_seances = wx.TextCtrl(self, -1, u"0", style=wx.TE_RIGHT)
        self.label_prix_seance = wx.StaticText(self, label=_(u"Coût unitaire séance :"))
        self.ctrl_prix_seance = CTRL_Saisie_euros.CTRL(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckboxJustification, self.ctrl_remboursement)
        self.ctrl_nb_seances.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusSeances)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init
        self.OnCheckboxJustification(None)

    def __set_properties(self):
        self.SetTitle(_(u"Générer un remboursement"))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie et fermer")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Remboursement
        staticbox_remboursement = wx.StaticBoxSizer(self.staticbox_remboursement_staticbox, wx.VERTICAL)
        staticbox_remboursement.Add(self.ctrl_remboursement, 0, wx.ALL, 10)

        grid_sizer_remboursement = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)
        grid_sizer_remboursement.Add(self.label_motif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_remboursement.Add(self.ctrl_motif, 0, wx.EXPAND, 0)
        grid_sizer_remboursement.Add(self.label_total, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_remboursement.Add(self.ctrl_total, 0, wx.EXPAND, 0)
        grid_sizer_remboursement.Add(self.label_nb_seances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_remboursement.Add(self.ctrl_nb_seances, 0, wx.EXPAND, 0)
        grid_sizer_remboursement.Add(self.label_prix_seance, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_remboursement.Add(self.ctrl_prix_seance, 0, wx.EXPAND, 0)
        grid_sizer_remboursement.AddGrowableCol(1)
        staticbox_remboursement.Add(grid_sizer_remboursement, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_remboursement, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnCheckboxJustification(self, event):
        """Sur check, active les champs de justification, sur uncheck les desactive"""
        self.label_motif.Enable(self.ctrl_remboursement.IsChecked())
        self.ctrl_motif.Enable(self.ctrl_remboursement.IsChecked())
        self.label_total.Enable(self.ctrl_remboursement.IsChecked())
        self.ctrl_total.Enable(self.ctrl_remboursement.IsChecked())
        self.label_nb_seances.Enable(self.ctrl_remboursement.IsChecked())
        self.ctrl_nb_seances.Enable(self.ctrl_remboursement.IsChecked())
        self.label_prix_seance.Enable(self.ctrl_remboursement.IsChecked())
        self.ctrl_prix_seance.Enable(self.ctrl_remboursement.IsChecked())

    def OnKillFocusSeances(self, event):
        """Le nombre de séances doit être un entier"""
        try:
            nb_seances = int(self.ctrl_nb_seances.GetValue())
        except ValueError:
            wx.MessageBox(_(u"Le nombre de séances doit être un entier"))
        event.Skip()

    def OnBoutonAnnuler(self, event):
        self.Destroy()

    def OnBoutonOk(self, event):
        if self.ctrl_remboursement.IsChecked():
            if (self.ctrl_motif.IsEmpty() or self.ctrl_total.IsEmpty() or self.ctrl_nb_seances.IsEmpty() or self.ctrl_prix_seance.IsEmpty()):
                dlg = wx.MessageDialog(self, _(u"Tous les champs doivent être remplis !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            montant = self.GetMontant()
            dlg = wx.MessageDialog(None, _(u"Confirmez-vous la génération d'un remboursement de %.2f %s ?") % (montant, SYMBOLE), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetMontant(self):
        montant = self.ctrl_total.GetMontant() - (int(self.ctrl_nb_seances.GetValue()) * self.ctrl_prix_seance.GetMontant())
        return montant

    def GetDonnees(self):
        if self.ctrl_remboursement.IsChecked():
            return {
                "motif" : self.ctrl_motif.GetValue(),
                "total" : self.ctrl_total.GetMontant(),
                "nb_seances" : self.ctrl_nb_seances.GetValue(),
                "prix_seance" : self.ctrl_prix_seance.GetMontant(),
                "montant": self.GetMontant(),
                }
        else :
            return None

    def SetDonnees(self, dict_remboursement={}):
        if dict_remboursement != None :
            self.ctrl_remboursement.SetValue(True)
            self.ctrl_motif.SetValue(dict_remboursement["motif"])
            self.ctrl_total.SetMontant(dict_remboursement["total"])
            self.ctrl_nb_seances.SetValue(dict_remboursement["nb_seances"])
            self.ctrl_prix_seance.SetMontant(dict_remboursement["prix_seance"])
            self.OnCheckboxJustification(None)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
