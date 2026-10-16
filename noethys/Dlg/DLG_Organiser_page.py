#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Module :         Boîte de dialogue d'organisation de page
#-----------------------------------------------------------

import wx
from Ctrl import CTRL_Bouton_image
from Utils.UTILS_Traduction import _


class Dialog(wx.Dialog):
    def __init__(self, parent, page_dict={}):
        titre = _(u"Organiser les tableaux : %s") % page_dict.get("nom", u"")
        wx.Dialog.__init__(self, parent, -1, title=titre, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.page_dict = page_dict

        # Liste de travail d'objets (copies de référence)
        self.liste_objets = list(page_dict.get("objets", []))

        # Bandeau explicatif
        self.label_intro = wx.StaticText(
            self, -1,
            _(u"Cochez les tableaux ou graphiques à afficher sur cette page.\n"
              u"Utilisez les boutons 'Monter' et 'Descendre' pour réorganiser leur ordre d'apparition.")
        )

        # Liste à cocher
        self.check_list = wx.CheckListBox(self, -1, choices=[], style=wx.LB_SINGLE)

        # Boutons latéraux d'organisation
        self.bouton_monter = wx.Button(self, -1, _(u"⬆  Monter"))
        self.bouton_descendre = wx.Button(self, -1, _(u"⬇  Descendre"))
        self.bouton_tout_cocher = wx.Button(self, -1, _(u"Tout afficher"))
        self.bouton_tout_decocher = wx.Button(self, -1, _(u"Tout masquer"))

        # Boutons du bas
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Valider"), cheminImage="Images/32x32/Valider.png")

        self.__set_properties()
        self.__do_layout()
        self.__init_donnees()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnMonter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.OnDescendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.OnToutCocher, self.bouton_tout_cocher)
        self.Bind(wx.EVT_BUTTON, self.OnToutDecocher, self.bouton_tout_decocher)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckItem, self.check_list)
        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.check_list)

    def __set_properties(self):
        self.SetMinSize((520, 430))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Monter l'élément sélectionné vers le haut de la page")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Descendre l'élément sélectionné vers le bas de la page")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Enregistrer l'organisation de cette page")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler les modifications")))

    def __do_layout(self):
        grid_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_base.Add(self.label_intro, 0, wx.ALL, 10)

        # Zone centrale (liste + boutons à droite)
        grid_centre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=10)
        grid_centre.Add(self.check_list, 1, wx.EXPAND, 0)

        grid_actions = wx.FlexGridSizer(rows=5, cols=1, vgap=8, hgap=5)
        grid_actions.Add(self.bouton_monter, 0, wx.EXPAND, 0)
        grid_actions.Add(self.bouton_descendre, 0, wx.EXPAND, 0)
        grid_actions.Add((10, 15), 0, wx.EXPAND, 0)
        grid_actions.Add(self.bouton_tout_cocher, 0, wx.EXPAND, 0)
        grid_actions.Add(self.bouton_tout_decocher, 0, wx.EXPAND, 0)
        grid_centre.Add(grid_actions, 0, wx.TOP, 5)

        grid_centre.AddGrowableRow(0)
        grid_centre.AddGrowableCol(0)
        grid_base.Add(grid_centre, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Boutons du bas
        grid_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_boutons.AddGrowableCol(0)
        grid_base.Add(grid_boutons, 0, wx.EXPAND | wx.ALL, 10)

        grid_base.AddGrowableRow(1)
        grid_base.AddGrowableCol(0)
        self.SetSizer(grid_base)
        grid_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def __init_donnees(self):
        self.check_list.Clear()
        for idx, obj in enumerate(self.liste_objets):
            nom = getattr(obj, "nom", u"").replace("<BR>", " ").replace("<br>", " ").strip()
            if not nom:
                nom = getattr(obj, "code", _(u"Élément sans nom"))
            # Préfixer avec le type (Tableau, Graphe, etc.)
            cat = getattr(obj, "categorie", u"tableau").capitalize()
            label = u"[%s] %s" % (cat, nom)
            self.check_list.Append(label)
            est_visible = getattr(obj, "visible", True)
            self.check_list.Check(idx, est_visible)

        if self.check_list.GetCount() > 0:
            self.check_list.SetSelection(0)
        self.MAJBoutons()

    def OnSelect(self, event):
        self.MAJBoutons()

    def OnCheckItem(self, event):
        idx = event.GetInt()
        if 0 <= idx < len(self.liste_objets):
            self.liste_objets[idx].visible = self.check_list.IsChecked(idx)

    def MAJBoutons(self):
        sel = self.check_list.GetSelection()
        nb = self.check_list.GetCount()
        self.bouton_monter.Enable(sel != wx.NOT_FOUND and sel > 0)
        self.bouton_descendre.Enable(sel != wx.NOT_FOUND and sel < nb - 1)

    def OnMonter(self, event):
        sel = self.check_list.GetSelection()
        if sel == wx.NOT_FOUND or sel <= 0:
            return
        # Swap dans la liste
        self.liste_objets[sel - 1], self.liste_objets[sel] = self.liste_objets[sel], self.liste_objets[sel - 1]
        
        # Mémoriser les états cochés
        etats = [self.check_list.IsChecked(i) for i in range(self.check_list.GetCount())]
        etats[sel - 1], etats[sel] = etats[sel], etats[sel - 1]

        # Réactualiser la liste
        self.__init_donnees()
        for i, etat in enumerate(etats):
            self.check_list.Check(i, etat)
        self.check_list.SetSelection(sel - 1)
        self.MAJBoutons()

    def OnDescendre(self, event):
        sel = self.check_list.GetSelection()
        nb = self.check_list.GetCount()
        if sel == wx.NOT_FOUND or sel >= nb - 1:
            return
        # Swap dans la liste
        self.liste_objets[sel + 1], self.liste_objets[sel] = self.liste_objets[sel], self.liste_objets[sel + 1]

        # Mémoriser les états cochés
        etats = [self.check_list.IsChecked(i) for i in range(self.check_list.GetCount())]
        etats[sel + 1], etats[sel] = etats[sel], etats[sel + 1]

        # Réactualiser la liste
        self.__init_donnees()
        for i, etat in enumerate(etats):
            self.check_list.Check(i, etat)
        self.check_list.SetSelection(sel + 1)
        self.MAJBoutons()

    def OnToutCocher(self, event):
        for i in range(self.check_list.GetCount()):
            self.check_list.Check(i, True)
            if i < len(self.liste_objets):
                self.liste_objets[i].visible = True

    def OnToutDecocher(self, event):
        for i in range(self.check_list.GetCount()):
            self.check_list.Check(i, False)
            if i < len(self.liste_objets):
                self.liste_objets[i].visible = False

    def OnBoutonAnnuler(self, event):
        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.Close()

    def OnBoutonOk(self, event):
        # Mettre à jour la visibilité de chaque objet
        for i in range(self.check_list.GetCount()):
            if i < len(self.liste_objets):
                self.liste_objets[i].visible = self.check_list.IsChecked(i)

        # Réaffecter la liste réordonnée à la page
        self.page_dict["objets"] = self.liste_objets

        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()
