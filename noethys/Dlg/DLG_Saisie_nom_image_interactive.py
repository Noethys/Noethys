#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB



class CTRL_Donnees(wx.ListBox):
    def __init__(self, parent, categorie=""):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.categorie = categorie
        self.dictDonnees = {}
        self.MAJ()

    def MAJ(self):
        self.dictDonnees = {}
        DB = GestionDB.DB()
        listeDonnees =[]

        if self.categorie == "produits_categories" :
            req = """SELECT IDcategorie, nom
            FROM produits_categories
            ORDER BY nom
            ;"""
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            self.Enable(False)
        listeLabels = []
        index = 0
        for IDdonnee, nom in listeDonnees :
            self.dictDonnees[index] = IDdonnee
            listeLabels.append(nom)
            index += 1
        self.SetItems(listeLabels)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]





class Dialog(wx.Dialog):
    def __init__(self, parent, categorie=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.categorie = categorie

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Saisissez un nom pour cette image"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")

        # Donnée associée
        self.box_donnee_staticbox = wx.StaticBox(self, -1, _(u"Sélectionnez la donnée associée"))
        self.ctrl_donnee = CTRL_Donnees(self, categorie=categorie)
        self.ctrl_donnee.SetMinSize((450, 250))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une image interactive"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici un nom pour cette image interactive")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_generalites, 1,wx.EXPAND, 0)

        # Donnée
        box_donnee = wx.StaticBoxSizer(self.box_donnee_staticbox, wx.VERTICAL)
        box_donnee.Add(self.ctrl_donnee, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_donnee, 1,wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonOk(self, event):
        # Validation des données
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        IDdonnee = self.ctrl_donnee.GetID()
        if IDdonnee == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une donnée dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.EndModal(wx.ID_OK)

    def GetResultats(self):
        nom = self.ctrl_nom.GetValue()
        IDdonnee = self.ctrl_donnee.GetID()
        return {"nom" : nom, "IDdonnee" : IDdonnee}



                


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, categorie="produits_categories")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
