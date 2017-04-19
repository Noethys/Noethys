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
import wx.calendar

import GestionDB
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Utils.UTILS_Traduction import _


class Dialog(wx.Dialog):
    def __init__(self, parent, IDinscription=None, IDfamille=None, IDindividu=None):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE)

        self.parent = parent
        self.IDinscription = IDinscription
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu

        # Champs de saisie
        self.staticbox_date_staticbox = wx.StaticBox(self, -1, _(u"Départ"))
        self.calendar_desinscription = CTRL_Saisie_date.Date2(self)
        self.calendar_desinscription.SetDate(datetime.date.today())
        self.staticbox_remboursement_staticbox = wx.StaticBox(self, -1, _(u"Remboursement"))
        self.ctrl_justification = wx.CheckBox(self, -1, _(u"Générer un remboursement"))
        self.ctrl_justification.SetValue(0)

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

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckboxJustification, self.ctrl_justification)
        self.ctrl_nb_seances.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusSeances)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init
        self.OnCheckboxJustification(None)

    def __set_properties(self):
        self.SetTitle(_(u"Départ de l'activité"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer la fiche"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie et fermer la fiche"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Date
        staticbox_date = wx.StaticBoxSizer(self.staticbox_date_staticbox, wx.VERTICAL)
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_date.Add(wx.StaticText(self, label=_(u"Date de départ :")), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.calendar_desinscription, 1, wx.EXPAND, 0)
        staticbox_date.Add(grid_sizer_date, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_date, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Remboursement
        staticbox_remboursement = wx.StaticBoxSizer(self.staticbox_remboursement_staticbox, wx.VERTICAL)
        staticbox_remboursement.Add(self.ctrl_justification, 0, wx.ALL, 10)

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
        grid_sizer_base.Add(staticbox_remboursement, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        self.label_motif.Enable(self.ctrl_justification.IsChecked())
        self.ctrl_motif.Enable(self.ctrl_justification.IsChecked())
        self.label_total.Enable(self.ctrl_justification.IsChecked())
        self.ctrl_total.Enable(self.ctrl_justification.IsChecked())
        self.label_nb_seances.Enable(self.ctrl_justification.IsChecked())
        self.ctrl_nb_seances.Enable(self.ctrl_justification.IsChecked())
        self.label_prix_seance.Enable(self.ctrl_justification.IsChecked())
        self.ctrl_prix_seance.Enable(self.ctrl_justification.IsChecked())

    def OnKillFocusSeances(self, event):
        """Le nombre de séances doit être un entier"""
        try:
            nb_seances = int(self.ctrl_nb_seances.GetValue())
        except ValueError:
            wx.MessageBox(_(u"Le nombre de séances doit être un entier"))

    def OnBoutonAnnuler(self, event):
        self.Destroy()

    def OnBoutonOk(self, event):
        date_desinscription = self.calendar_desinscription.GetDate()

        # Controles de saisie
        # La date doit etre saisie
        if date_desinscription is None:
            wx.MessageBox(_(u"Vous devez selectionner une date de départ"))
            return
        # Dans le cas d'un départ motivé
        if self.ctrl_justification.IsChecked():
            # Tous les champs doivent être saisis
            if (self.ctrl_motif.IsEmpty() or self.ctrl_total.IsEmpty()
                    or self.ctrl_nb_seances.IsEmpty() or self.ctrl_prix_seance.IsEmpty()):
                wx.MessageBox(_(u"Tous les champs doivent être remplis"))
                return
            else:
                # Calcul du remboursement
                montant = self.ctrl_total.GetMontant() - (int(self.ctrl_nb_seances.GetValue()) * self.ctrl_prix_seance.GetMontant())

            DB = GestionDB.DB()
            # Modification de la date de desinscription
            DB.ReqMAJ('inscriptions', [('date_desinscription', str(date_desinscription))], 'IDinscription', self.IDinscription)
            # CrÃ©ation d'une prestation négative pour la famille correspondant au remboursement
            req = "SELECT IDcompte_payeur FROM familles WHERE IDfamille=%d" % self.IDfamille
            IDcompte_payeur = DB.ExecuterReq(req)

            listeDonnees = [
                ("IDcompte_payeur", IDcompte_payeur),
                ("date", str(datetime.date.today())),
                ("label", self.ctrl_motif.GetValue()),
                ("montant_initial", -montant),
                ("montant", -montant),
                ("IDactivite", self.parent.dictActivite["IDactivite"]),
                ("IDfamille", self.IDfamille),
                ("IDindividu", self.IDindividu),
                ("date_valeur", str(datetime.date.today())),
            ]
            DB.ReqInsert("prestations", listeDonnees)
            DB.Close()

        self.Destroy()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
