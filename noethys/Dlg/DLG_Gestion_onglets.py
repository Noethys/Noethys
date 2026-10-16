#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Module :         Boîte de dialogue de gestion des onglets
#-----------------------------------------------------------

import wx
import wx.lib.agw.customtreectrl as CT
import Chemins
from Ctrl import CTRL_Bouton_image
from Utils.UTILS_Traduction import _


class Dialog(wx.Dialog):
    def __init__(self, parent, liste_objets=[]):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Affichage des onglets et rubriques"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.liste_objets = liste_objets

        # Bandeau explicatif
        self.label_intro = wx.StaticText(
            self, -1,
            _(u"Cochez les rubriques et les onglets que vous souhaitez afficher.\n"
              u"Décochez ceux qui ne vous sont pas utiles pour alléger et simplifier votre interface.")
        )

        # Arbre des onglets avec cases à cocher
        self.tree = CT.CustomTreeCtrl(self, -1, style=wx.SUNKEN_BORDER,
                                      agwStyle=wx.TR_HIDE_ROOT | wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                                               CT.TR_AUTO_CHECK_PARENT | CT.TR_AUTO_CHECK_CHILD)
        self.tree.SetBackgroundColour(wx.WHITE)
        self.tree.EnableSelectionVista(True)

        # Boutons de sélection rapide
        self.bouton_tout_cocher = wx.Button(self, -1, _(u"Tout cocher"))
        self.bouton_tout_decocher = wx.Button(self, -1, _(u"Tout décocher"))

        # Boutons du bas
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Valider"), cheminImage="Images/32x32/Valider.png")

        self.__set_properties()
        self.__do_layout()
        self.__init_arbre()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnToutCocher, self.bouton_tout_cocher)
        self.Bind(wx.EVT_BUTTON, self.OnToutDecocher, self.bouton_tout_decocher)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetMinSize((480, 460))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Appliquer l'affichage des onglets sélectionnés")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler les modifications")))

    def __do_layout(self):
        grid_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_base.Add(self.label_intro, 0, wx.ALL, 10)

        # Arbre
        grid_base.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Boutons rapides
        grid_rapide = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=10)
        grid_rapide.Add(self.bouton_tout_cocher, 0, 0, 0)
        grid_rapide.Add(self.bouton_tout_decocher, 0, 0, 0)
        grid_base.Add(grid_rapide, 0, wx.LEFT | wx.RIGHT, 10)

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

    def __init_arbre(self):
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot(_(u"Onglets"))
        self.dictBranchesRubriques = {}
        self.dictBranchesPages = {}

        for dictRubrique in self.liste_objets:
            nomRub = dictRubrique.get("nom", _(u"Rubrique"))
            brancheRubrique = self.tree.AppendItem(self.root, nomRub, ct_type=1)
            self.tree.SetItemBold(brancheRubrique, True)
            self.tree.SetPyData(brancheRubrique, {"type": "rubrique", "code": dictRubrique["code"]})
            self.dictBranchesRubriques[dictRubrique["code"]] = brancheRubrique

            est_rub_visible = dictRubrique.get("visible", True)
            if est_rub_visible:
                brancheRubrique.Check(True)
            else:
                brancheRubrique.Check(False)

            for dictPage in dictRubrique.get("pages", []):
                nomPage = dictPage.get("nom", _(u"Page"))
                branchePage = self.tree.AppendItem(brancheRubrique, nomPage, ct_type=1)
                self.tree.SetPyData(branchePage, {"type": "page", "code": dictPage["code"]})
                self.dictBranchesPages[dictPage["code"]] = branchePage

                est_page_visible = dictPage.get("visible", True)
                if est_page_visible and est_rub_visible:
                    branchePage.Check(True)
                else:
                    branchePage.Check(False)

        self.tree.ExpandAll()

    def OnToutCocher(self, event):
        for code, branche in self.dictBranchesRubriques.items():
            self.tree.CheckItem(branche, True)
        for code, branche in self.dictBranchesPages.items():
            self.tree.CheckItem(branche, True)

    def OnToutDecocher(self, event):
        for code, branche in self.dictBranchesRubriques.items():
            self.tree.CheckItem(branche, False)
        for code, branche in self.dictBranchesPages.items():
            self.tree.CheckItem(branche, False)

    def OnBoutonAnnuler(self, event):
        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.Close()

    def OnBoutonOk(self, event):
        # Vérification qu'au moins un onglet est coché
        nb_coches = 0
        for code, branche in self.dictBranchesPages.items():
            if self.tree.IsItemChecked(branche):
                nb_coches += 1

        if nb_coches == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez conserver au moins un onglet affiché."), _(u"Attention"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Application de la visibilité sur self.liste_objets
        for dictRubrique in self.liste_objets:
            codeRub = dictRubrique["code"]
            brancheRub = self.dictBranchesRubriques.get(codeRub)
            
            # Une rubrique est visible si elle est cochée et a au moins une page cochée
            pages_visibles = 0
            for dictPage in dictRubrique.get("pages", []):
                codePage = dictPage["code"]
                branchePage = self.dictBranchesPages.get(codePage)
                est_visible = self.tree.IsItemChecked(branchePage) if branchePage else True
                dictPage["visible"] = est_visible
                if est_visible:
                    pages_visibles += 1

            dictRubrique["visible"] = (pages_visibles > 0)

        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()
