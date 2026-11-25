#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Module :         Dialogue de création d'un tableau croisé
#-----------------------------------------------------------

import wx
import datetime
from Ctrl import CTRL_Bouton_image
from Utils.UTILS_Traduction import _
from Utils import UTILS_Stats_croise as CROISE


class Dialog(wx.Dialog):
    def __init__(self, parent, rubrique="individus", page="individus_nombre"):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Créer un nouveau tableau statistique"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.rubrique = rubrique
        self.page = page

        # Titre
        self.box_titre_staticbox = wx.StaticBox(self, -1, _(u"1. Titre du tableau"))
        self.ctrl_titre = wx.TextCtrl(self, -1, _(u"Répartition personnalisée"))

        # Indicateur
        self.box_indicateur_staticbox = wx.StaticBox(self, -1, _(u"2. Donnée à compter (Indicateur)"))
        self.liste_indicateurs = CROISE.INDICATEURS_DISPONIBLES
        choices_indicateurs = [lbl for code, lbl in self.liste_indicateurs]
        self.ctrl_indicateur = wx.Choice(self, -1, choices=choices_indicateurs)
        self.ctrl_indicateur.SetSelection(0)

        # Axes
        self.box_axes_staticbox = wx.StaticBox(self, -1, _(u"3. Dimensions du tableau croisé"))
        self.liste_dimensions = CROISE.DIMENSIONS_DISPONIBLES

        choices_lignes = [lbl for code, lbl in self.liste_dimensions]
        self.label_lignes = wx.StaticText(self, -1, _(u"Lignes (Dimension 1) :"))
        self.ctrl_axe_lignes = wx.Choice(self, -1, choices=choices_lignes)
        self.ctrl_axe_lignes.SetSelection(0)

        choices_cols = [_(u"(Aucun - tableau simple à 1 dimension)")] + [lbl for code, lbl in self.liste_dimensions]
        self.label_cols = wx.StaticText(self, -1, _(u"Colonnes (Dimension 2 - Optionnel) :"))
        self.ctrl_axe_colonnes = wx.Choice(self, -1, choices=choices_cols)
        self.ctrl_axe_colonnes.SetSelection(2)  # Activités par défaut

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"4. Options d'affichage"))
        self.check_total_lignes = wx.CheckBox(self, -1, _(u"Afficher une ligne Total (en bas)"))
        self.check_total_lignes.SetValue(True)

        self.check_total_colonnes = wx.CheckBox(self, -1, _(u"Afficher une colonne Total (à droite)"))
        self.check_total_colonnes.SetValue(True)

        self.check_pourcentages = wx.CheckBox(self, -1, _(u"Afficher une colonne Pourcentages (%)"))
        self.check_pourcentages.SetValue(False)

        # Note
        self.box_note_staticbox = wx.StaticBox(self, -1, _(u"5. Note ou observation sous le tableau (facultatif)"))
        self.ctrl_note = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.ctrl_note.SetMinSize((-1, 55))

        # Boutons
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Créer le tableau"), cheminImage="Images/32x32/Valider.png")

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChangementAxeCols, self.ctrl_axe_colonnes)

        self.OnChangementAxeCols(None)

    def __set_properties(self):
        self.SetMinSize((580, 560))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Créer et insérer ce tableau dans la page courante")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler la création")))

    def __do_layout(self):
        grid_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)

        # Titre
        box_titre = wx.StaticBoxSizer(self.box_titre_staticbox, wx.VERTICAL)
        box_titre.Add(self.ctrl_titre, 0, wx.EXPAND | wx.ALL, 5)
        grid_base.Add(box_titre, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Indicateur
        box_ind = wx.StaticBoxSizer(self.box_indicateur_staticbox, wx.VERTICAL)
        box_ind.Add(self.ctrl_indicateur, 0, wx.EXPAND | wx.ALL, 5)
        grid_base.Add(box_ind, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Axes
        box_axes = wx.StaticBoxSizer(self.box_axes_staticbox, wx.VERTICAL)
        grid_axes = wx.FlexGridSizer(rows=2, cols=2, vgap=8, hgap=10)
        grid_axes.Add(self.label_lignes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_axes.Add(self.ctrl_axe_lignes, 0, wx.EXPAND, 0)
        grid_axes.Add(self.label_cols, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_axes.Add(self.ctrl_axe_colonnes, 0, wx.EXPAND, 0)
        grid_axes.AddGrowableCol(1)
        box_axes.Add(grid_axes, 1, wx.EXPAND | wx.ALL, 5)
        grid_base.Add(box_axes, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Options
        box_opt = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        box_opt.Add(self.check_total_lignes, 0, wx.BOTTOM, 4)
        box_opt.Add(self.check_total_colonnes, 0, wx.BOTTOM, 4)
        box_opt.Add(self.check_pourcentages, 0, 0, 0)
        grid_base.Add(box_opt, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Note
        box_note = wx.StaticBoxSizer(self.box_note_staticbox, wx.VERTICAL)
        box_note.Add(self.ctrl_note, 1, wx.EXPAND | wx.ALL, 5)
        grid_base.Add(box_note, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Boutons
        grid_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_boutons.AddGrowableCol(0)
        grid_base.Add(grid_boutons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        grid_base.AddGrowableCol(0)
        grid_base.AddGrowableRow(4)
        self.SetSizer(grid_base)
        grid_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def OnChangementAxeCols(self, event):
        est_croise = (self.ctrl_axe_colonnes.GetSelection() > 0)
        self.check_total_colonnes.Enable(est_croise)
        self.check_pourcentages.Enable(not est_croise)

    def OnBoutonAnnuler(self, event):
        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.Close()

    def OnBoutonOk(self, event):
        titre = self.ctrl_titre.GetValue().strip()
        if not titre:
            dlg = wx.MessageDialog(self, _(u"Veuillez indiquer un titre pour le tableau."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        idx_ind = self.ctrl_indicateur.GetSelection()
        code_indicateur = self.liste_indicateurs[idx_ind][0]

        idx_lig = self.ctrl_axe_lignes.GetSelection()
        code_axe_lignes = self.liste_dimensions[idx_lig][0]

        idx_col = self.ctrl_axe_colonnes.GetSelection()
        code_axe_colonnes = "aucun" if idx_col == 0 else self.liste_dimensions[idx_col - 1][0]

        if code_axe_colonnes != "aucun" and code_axe_colonnes == code_axe_lignes:
            dlg = wx.MessageDialog(self, _(u"L'axe des lignes et l'axe des colonnes doivent être différents."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        code_unique = "custom_tab_%s" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        self.definition = {
            "code": code_unique,
            "titre": titre,
            "rubrique": self.rubrique,
            "page": self.page,
            "indicateur": code_indicateur,
            "axe_lignes": code_axe_lignes,
            "axe_colonnes": code_axe_colonnes,
            "afficher_total_lignes": self.check_total_lignes.GetValue(),
            "afficher_total_colonnes": self.check_total_colonnes.GetValue(),
            "afficher_pourcentages": self.check_pourcentages.GetValue(),
            "note": self.ctrl_note.GetValue().strip(),
            "date_creation": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Sauvegarder la définition
        CROISE.SauvegarderNouveauTableauPerso(self.definition)

        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    def GetDefinition(self):
        return getattr(self, "definition", None)
