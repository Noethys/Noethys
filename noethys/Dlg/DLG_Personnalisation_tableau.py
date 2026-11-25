#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Module :         Boîte de dialogue de personnalisation d'un tableau statistique
# Licence :        Licence GNU GPL
#------------------------------------------------------------------------

import wx
from Utils.UTILS_Traduction import _
from Ctrl import CTRL_Bouton_image


class Dialog(wx.Dialog):
    def __init__(self, parent, objet=None):
        wx.Dialog.__init__(
            self,
            parent,
            -1,
            title=_(u"Personnalisation du tableau : %s") % (objet.nom if objet else u""),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX
        )
        self.parent = parent
        self.objet = objet
        self.dictPerso = dict(objet.dictPersonnalisation) if hasattr(objet, "dictPersonnalisation") and objet.dictPersonnalisation else {}

        # Mémorisation des libellés modifiés
        self.dictColsLibelles = dict(self.dictPerso.get("colonnes_libelles", {}))
        self.dictLignesLibelles = dict(self.dictPerso.get("lignes_libelles", {}))

        # --- Titre du tableau ---
        self.box_titre_staticbox = wx.StaticBox(self, -1, _(u"Titre du tableau"))
        titre_actuel = self.dictPerso.get("titre") or getattr(self.objet, "nom", u"")
        self.ctrl_titre = wx.TextCtrl(self, -1, titre_actuel)

        # --- Colonnes ---
        self.box_cols_staticbox = wx.StaticBox(self, -1, _(u"Colonnes à afficher"))
        self.liste_cols_originales = []
        for c in getattr(self.objet, "colonnes", []):
            if isinstance(c, (list, tuple)) and len(c) > 0:
                self.liste_cols_originales.append(str(c[0]))
            elif isinstance(c, dict):
                self.liste_cols_originales.append(str(c.get("label", "")))
            else:
                self.liste_cols_originales.append(str(c))

        self.check_colonnes = wx.CheckListBox(self, -1, choices=[], style=wx.LB_SINGLE)
        self.bouton_renommer_colonne = wx.Button(self, -1, _(u"Renommer la colonne sélectionnée..."))
        self.hyper_toutes_cols = wx.Button(self, -1, _(u"Tout cocher"))
        self.hyper_aucune_col = wx.Button(self, -1, _(u"Tout décocher"))

        # --- Lignes ---
        self.box_lignes_staticbox = wx.StaticBox(self, -1, _(u"Lignes à afficher"))
        self.liste_lignes_originales = []
        for idx, l in enumerate(getattr(self.objet, "lignes", [])):
            if isinstance(l, (list, tuple)) and len(l) > 0:
                self.liste_lignes_originales.append(str(l[0]))
            elif isinstance(l, dict):
                self.liste_lignes_originales.append(str(l.get("label", u"Ligne %d" % (idx + 1))))
            else:
                self.liste_lignes_originales.append(str(l))

        self.check_lignes = wx.CheckListBox(self, -1, choices=[], style=wx.LB_SINGLE)
        self.bouton_renommer_ligne = wx.Button(self, -1, _(u"Renommer la ligne sélectionnée..."))
        self.hyper_toutes_lignes = wx.Button(self, -1, _(u"Tout cocher"))
        self.hyper_aucune_ligne = wx.Button(self, -1, _(u"Tout décocher"))

        # --- Note / Commentaire ---
        self.box_note_staticbox = wx.StaticBox(self, -1, _(u"Note ou observation sous le tableau"))
        self.ctrl_note = wx.TextCtrl(self, -1, self.dictPerso.get("note", u""), style=wx.TE_MULTILINE)
        self.ctrl_note.SetMinSize((-1, 60))

        # --- Boutons du bas ---
        self.bouton_reinitialiser = wx.Button(self, -1, _(u"Réinitialiser aux valeurs d'origine"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Valider"), cheminImage="Images/32x32/Valider.png")

        self.__set_properties()
        self.__do_layout()
        self.__init_donnees()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnRenommerColonne, self.bouton_renommer_colonne)
        self.Bind(wx.EVT_BUTTON, self.OnToutCocherCols, self.hyper_toutes_cols)
        self.Bind(wx.EVT_BUTTON, self.OnToutDecocherCols, self.hyper_aucune_col)

        self.Bind(wx.EVT_BUTTON, self.OnRenommerLigne, self.bouton_renommer_ligne)
        self.Bind(wx.EVT_BUTTON, self.OnToutCocherLignes, self.hyper_toutes_lignes)
        self.Bind(wx.EVT_BUTTON, self.OnToutDecocherLignes, self.hyper_aucune_ligne)

        self.Bind(wx.EVT_BUTTON, self.OnReinitialiser, self.bouton_reinitialiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetMinSize((650, 680))
        self.SetSize((720, 720))
        self.CentreOnScreen()
        self.ctrl_titre.SetToolTip(wx.ToolTip(_(u"Personnalisez le titre affiché au-dessus de ce tableau")))
        self.bouton_reinitialiser.SetToolTip(wx.ToolTip(_(u"Efface toutes les personnalisations et rétablit le tableau par défaut")))

    def __do_layout(self):
        grid_base = wx.BoxSizer(wx.VERTICAL)

        # 1. Titre
        box_titre = wx.StaticBoxSizer(self.box_titre_staticbox, wx.VERTICAL)
        box_titre.Add(self.ctrl_titre, 0, wx.ALL | wx.EXPAND, 5)
        grid_base.Add(box_titre, 0, wx.ALL | wx.EXPAND, 8)

        # 2. Milieu : Deux colonnes (Colonnes à gauche, Lignes à droite)
        sizer_milieu = wx.BoxSizer(wx.HORIZONTAL)

        # Boîte Colonnes
        box_cols = wx.StaticBoxSizer(self.box_cols_staticbox, wx.VERTICAL)
        box_cols.Add(self.check_colonnes, 1, wx.ALL | wx.EXPAND, 5)
        sizer_actions_cols = wx.BoxSizer(wx.HORIZONTAL)
        sizer_actions_cols.Add(self.hyper_toutes_cols, 0, wx.RIGHT, 5)
        sizer_actions_cols.Add(self.hyper_aucune_col, 0, wx.RIGHT, 5)
        sizer_actions_cols.Add(self.bouton_renommer_colonne, 1, wx.EXPAND, 0)
        box_cols.Add(sizer_actions_cols, 0, wx.ALL | wx.EXPAND, 5)
        sizer_milieu.Add(box_cols, 1, wx.RIGHT | wx.EXPAND, 4)

        # Boîte Lignes
        box_lignes = wx.StaticBoxSizer(self.box_lignes_staticbox, wx.VERTICAL)
        box_lignes.Add(self.check_lignes, 1, wx.ALL | wx.EXPAND, 5)
        sizer_actions_lignes = wx.BoxSizer(wx.HORIZONTAL)
        sizer_actions_lignes.Add(self.hyper_toutes_lignes, 0, wx.RIGHT, 5)
        sizer_actions_lignes.Add(self.hyper_aucune_ligne, 0, wx.RIGHT, 5)
        sizer_actions_lignes.Add(self.bouton_renommer_ligne, 1, wx.EXPAND, 0)
        box_lignes.Add(sizer_actions_lignes, 0, wx.ALL | wx.EXPAND, 5)
        sizer_milieu.Add(box_lignes, 1, wx.LEFT | wx.EXPAND, 4)

        grid_base.Add(sizer_milieu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)

        # 3. Note
        box_note = wx.StaticBoxSizer(self.box_note_staticbox, wx.VERTICAL)
        box_note.Add(self.ctrl_note, 1, wx.ALL | wx.EXPAND, 5)
        grid_base.Add(box_note, 0, wx.ALL | wx.EXPAND, 8)

        # 4. Boutons du bas
        sizer_boutons = wx.BoxSizer(wx.HORIZONTAL)
        sizer_boutons.Add(self.bouton_reinitialiser, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_boutons.AddStretchSpacer(1)
        sizer_boutons.Add(self.bouton_annuler, 0, wx.RIGHT, 5)
        sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_base.Add(sizer_boutons, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(grid_base)
        self.Layout()

    def __init_donnees(self):
        """ Initialise les CheckListBox avec les données du tableau et les sélections """
        # Colonnes
        self.check_colonnes.Clear()
        for idx, lbl in enumerate(self.liste_cols_originales):
            label_affiche = self.dictColsLibelles.get(str(idx), self.dictColsLibelles.get(idx, lbl))
            self.check_colonnes.Append(label_affiche)

        # Coche des colonnes
        cols_visibles = self.dictPerso.get("colonnes_visibles")
        for idx in range(len(self.liste_cols_originales)):
            if cols_visibles is None or idx in cols_visibles:
                self.check_colonnes.Check(idx, True)
            else:
                self.check_colonnes.Check(idx, False)

        # Lignes
        self.check_lignes.Clear()
        for idx, lbl in enumerate(self.liste_lignes_originales):
            label_affiche = self.dictLignesLibelles.get(str(idx), self.dictLignesLibelles.get(idx, lbl))
            self.check_lignes.Append(label_affiche)

        # Coche des lignes (coché = visible)
        lignes_masquees = set(self.dictPerso.get("lignes_masquees", []))
        for idx in range(len(self.liste_lignes_originales)):
            self.check_lignes.Check(idx, idx not in lignes_masquees)

    def OnRenommerColonne(self, event):
        sel = self.check_colonnes.GetSelection()
        if sel == wx.NOT_FOUND:
            dlg = wx.MessageDialog(self, _(u"Veuillez sélectionner une colonne dans la liste."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        label_actuel = self.check_colonnes.GetString(sel)
        dlg = wx.TextEntryDialog(self, _(u"Nouveau libellé pour la colonne :"), _(u"Renommer la colonne"), value=label_actuel)
        if dlg.ShowModal() == wx.ID_OK:
            nouveau = dlg.GetValue().strip()
            if nouveau != "":
                self.dictColsLibelles[str(sel)] = nouveau
                etat = self.check_colonnes.IsChecked(sel)
                self.check_colonnes.SetString(sel, nouveau)
                self.check_colonnes.Check(sel, etat)
        dlg.Destroy()

    def OnToutCocherCols(self, event):
        for i in range(self.check_colonnes.GetCount()):
            self.check_colonnes.Check(i, True)

    def OnToutDecocherCols(self, event):
        for i in range(self.check_colonnes.GetCount()):
            self.check_colonnes.Check(i, False)

    def OnRenommerLigne(self, event):
        sel = self.check_lignes.GetSelection()
        if sel == wx.NOT_FOUND:
            dlg = wx.MessageDialog(self, _(u"Veuillez sélectionner une ligne dans la liste."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        label_actuel = self.check_lignes.GetString(sel)
        dlg = wx.TextEntryDialog(self, _(u"Nouveau libellé pour la ligne :"), _(u"Renommer la ligne"), value=label_actuel)
        if dlg.ShowModal() == wx.ID_OK:
            nouveau = dlg.GetValue().strip()
            if nouveau != "":
                self.dictLignesLibelles[str(sel)] = nouveau
                etat = self.check_lignes.IsChecked(sel)
                self.check_lignes.SetString(sel, nouveau)
                self.check_lignes.Check(sel, etat)
        dlg.Destroy()

    def OnToutCocherLignes(self, event):
        for i in range(self.check_lignes.GetCount()):
            self.check_lignes.Check(i, True)

    def OnToutDecocherLignes(self, event):
        for i in range(self.check_lignes.GetCount()):
            self.check_lignes.Check(i, False)

    def OnReinitialiser(self, event):
        dlg = wx.MessageDialog(
            self,
            _(u"Voulez-vous vraiment réinitialiser toutes les personnalisations de ce tableau ?"),
            _(u"Confirmation"),
            wx.YES_NO | wx.ICON_QUESTION
        )
        if dlg.ShowModal() == wx.ID_YES:
            self.dictPerso = {}
            self.dictColsLibelles = {}
            self.dictLignesLibelles = {}
            self.ctrl_titre.SetValue(getattr(self.objet, "nom", u""))
            self.ctrl_note.SetValue(u"")
            self.__init_donnees()
        dlg.Destroy()

    def OnBoutonAnnuler(self, event):
        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.Close()

    def OnBoutonOk(self, event):
        # Vérification qu'au moins une colonne est cochée
        cols_visibles = [i for i in range(self.check_colonnes.GetCount()) if self.check_colonnes.IsChecked(i)]
        if len(cols_visibles) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez afficher au moins une colonne dans le tableau."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Construction du dictionnaire de personnalisation
        perso = {}
        nouveau_titre = self.ctrl_titre.GetValue().strip()
        if nouveau_titre != "" and nouveau_titre != getattr(self.objet, "nom", u""):
            perso["titre"] = nouveau_titre

        # Colonnes visibles (seulement si pas toutes cochées)
        if len(cols_visibles) < self.check_colonnes.GetCount():
            perso["colonnes_visibles"] = cols_visibles

        # Colonnes renommées
        if self.dictColsLibelles:
            perso["colonnes_libelles"] = self.dictColsLibelles

        # Lignes masquées (décochées)
        lignes_masquees = [i for i in range(self.check_lignes.GetCount()) if not self.check_lignes.IsChecked(i)]
        if len(lignes_masquees) > 0:
            perso["lignes_masquees"] = lignes_masquees

        # Lignes renommées
        if self.dictLignesLibelles:
            perso["lignes_libelles"] = self.dictLignesLibelles

        # Note
        note = self.ctrl_note.GetValue().strip()
        if note != "":
            perso["note"] = note

        if hasattr(self.objet, "dictPersonnalisation"):
            self.objet.dictPersonnalisation = perso

        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()
