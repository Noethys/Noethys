#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# ------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
# ------------------------------------------------------------------------

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
        wx.Dialog.__init__(self, parent,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)

        self.parent = parent
        self.IDinscription = IDinscription
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu

        # Champs de saisie
        self.calendar_desinscription = CTRL_Saisie_date.Date2(self)
        self.ctrl_justification = wx.CheckBox(self, -1, _(u"Départ justifié"))
        self.ctrl_justification.SetValue(1)
        self.ctrl_motif = wx.TextCtrl(self, -1, u"")
        self.ctrl_total = CTRL_Saisie_euros.CTRL(self)
        self.ctrl_nb_seances = wx.TextCtrl(self, -1, u"0", style=wx.TE_RIGHT)
        self.ctrl_prix_seance = CTRL_Saisie_euros.CTRL(self)

        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckboxJustification, self.ctrl_justification)
        self.ctrl_nb_seances.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusSeances)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer la fiche"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la\nsaisie et fermer la fiche"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Champs de saisie
        grid_sizer_fields = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=5)
        grid_sizer_fields.Add(wx.StaticText(self, label=_(u"Date de départ")))
        grid_sizer_fields.Add(self.calendar_desinscription, 0, 0, 0)

        grid_sizer_fields.Add(self.ctrl_justification, 0, 0, 0)
        grid_sizer_fields.Add((20, 20), 0, wx.EXPAND, 0)

        grid_sizer_fields.Add(wx.StaticText(self, label=_(u"Motif")))
        grid_sizer_fields.Add(self.ctrl_motif, 0, 0, 0)

        grid_sizer_fields.Add(wx.StaticText(self, label=_(u"Coût total de l'activité")))
        grid_sizer_fields.Add(self.ctrl_total, 0, 0, 0)

        grid_sizer_fields.Add(wx.StaticText(self, label=_(u"Nombre de séances effectuées")))
        grid_sizer_fields.Add(self.ctrl_nb_seances, 0, 0, 0)

        grid_sizer_fields.Add(wx.StaticText(self, label=_(u"Coût unitaire")))
        grid_sizer_fields.Add(self.ctrl_prix_seance, 0, 0, 0)

        grid_sizer_base.Add(grid_sizer_fields, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        self.Layout()
        self.CenterOnScreen()

    def OnCheckboxJustification(self, event):
        """Sur check, active les champs de justification, sur uncheck les desactive"""
        if self.ctrl_justification.IsChecked():
            self.ctrl_motif.Enable()
            self.ctrl_total.Enable()
            self.ctrl_nb_seances.Enable()
            self.ctrl_prix_seance.Enable()
        else:
            self.ctrl_motif.Disable()
            self.ctrl_total.Disable()
            self.ctrl_nb_seances.Disable()
            self.ctrl_prix_seance.Disable()

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
        # Création d'une prestation négative pour la famille correspondant au remboursement
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
