#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import calendar
import GestionDB
from Utils import UTILS_Dialogs
from Utils import UTILS_Images
from Ctrl import CTRL_Menus
from Ctrl import CTRL_Bandeau


class CTRL_Restaurateur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJlisteDonnees()

    def MAJlisteDonnees(self):
        self.SetItems(self.GetListeDonnees())
        if len(self.GetListeDonnees()) > 0 :
            self.Select(0)
            self.Enable(True)
        else :
            self.Enable(False)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDrestaurateur, nom
        FROM restaurateurs
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDrestaurateur, nom in listeDonnees:
            self.dictDonnees[index] = {"ID": IDrestaurateur}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["ID"]


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Menus", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Bandeau
        intro = _(u"Vous pouvez ici saisir les menus de votre restaurateur. Sélectionnez un restaurateur et un mois puis double-cliquez sur une case pour saisir un menu. Si vous n'avez paramétré aucun restaurateur, vous pouvez le faire directement en cliquant sur le bouton 'Gestion des restaurateurs' à droite de la liste déroulante restaurateur.")
        titre = _(u"Gestion des menus")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Menu.png")

        # Selection période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.ctrl_mois = wx.Choice(self, -1, choices=[_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")])
        self.spin_mois = wx.SpinButton(self, -1, size=(18, 20),  style=wx.SP_VERTICAL)
        self.spin_mois.SetRange(-1, 1)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", min=1977, max=2999)
        dateDuJour = datetime.date.today()
        self.ctrl_annee.SetValue(dateDuJour.year)
        self.ctrl_mois.SetSelection(dateDuJour.month-1)

        # Restaurateur
        self.staticbox_restaurateur_staticbox = wx.StaticBox(self, -1, _(u"Restaurateur"))
        self.label_restaurateur = wx.StaticText(self, -1, _(u"Restaurateur :"))
        self.ctrl_restaurateur = CTRL_Restaurateur(self)
        self.bouton_restaurateur = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Menus
        self.box_menus_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Menus"))
        self.ctrl_menus = CTRL_Menus.CTRL(self)
        self.ctrl_menus.SetMinSize((100, 380))

        # Légende
        self.listeLegende = [
            {"label": _(u"Cases avec contenu"), "couleur": CTRL_Menus.COULEUR_CASES_OUVERTES, "ctrl_label": None, "ctrl_img": None},
            {"label": _(u"Cases vides"), "couleur": CTRL_Menus.COULEUR_CASES_FERMEES, "ctrl_label": None, "ctrl_img": None},
            ]
        index = 0
        for dictTemp in self.listeLegende :
            img = wx.StaticBitmap(self, -1, UTILS_Images.CreationCarreCouleur(12, 12, dictTemp["couleur"], contour=True))
            label = wx.StaticText(self, -1, dictTemp["label"])
            label.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.listeLegende[index]["ctrl_img"] = img
            self.listeLegende[index]["ctrl_label"] = label
            index += 1

        self.image_info = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Astuce.png"), wx.BITMAP_TYPE_ANY))
        self.label_info = wx.StaticText(self, -1, _(u"Double-cliquez pour modifier ou faites un clic droit pour ouvrir le menu contextuel ou utilisez le copier-coller (Ctrl+C puis Ctrl+V)"))
        self.label_info.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_SPIN, self.OnSpinMois, self.spin_mois)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_mois)
        self.Bind(wx.EVT_SPINCTRL, self.MAJ, self.ctrl_annee)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_restaurateur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRestaurateur, self.bouton_restaurateur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        self.MAJ()

    def __set_properties(self):
        self.ctrl_mois.SetToolTip(wx.ToolTip(_(u"Sélectionnez un mois")))
        self.ctrl_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetToolTip(wx.ToolTip(_(u"Sélectionnez une année")))
        self.bouton_restaurateur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des restaurateurs")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la commande au format PDF")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)

        # Selection Mois
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
        grid_sizer_periode.Add(self.label_mois, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_mois, 0, wx.LEFT, 5)
        grid_sizer_periode.Add(self.spin_mois, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_annee, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        grid_sizer_periode.Add(self.ctrl_annee, 0, wx.LEFT, 5)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_periode, 1, wx.EXPAND, 0)

        # Restaurateur
        box_restaurateur = wx.StaticBoxSizer(self.staticbox_restaurateur_staticbox, wx.HORIZONTAL)
        grid_sizer_restaurateur = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_restaurateur.Add(self.label_restaurateur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_restaurateur.Add(self.ctrl_restaurateur, 1, wx.EXPAND)
        grid_sizer_restaurateur.Add(self.bouton_restaurateur, 0, 0, 0)
        grid_sizer_restaurateur.AddGrowableCol(1)
        box_restaurateur.Add(grid_sizer_restaurateur, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_restaurateur, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(1)

        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Menus
        box_menus = wx.StaticBoxSizer(self.box_menus_staticbox, wx.VERTICAL)
        grid_sizer_menus = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_menus.Add(self.ctrl_menus, 1, wx.EXPAND, 0)

        # Légende
        grid_sizer_legende = wx.FlexGridSizer(rows=1, cols=len(self.listeLegende)*3 + 3, vgap=4, hgap=4)

        grid_sizer_legende.Add(self.image_info, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_legende.Add(self.label_info, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        for dictTemp in self.listeLegende :
            grid_sizer_legende.Add((5, 5), 0, 0, 0)
            grid_sizer_legende.Add(dictTemp["ctrl_img"], 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_legende.Add(dictTemp["ctrl_label"], 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_legende.AddGrowableCol(2)
        grid_sizer_menus.Add(grid_sizer_legende, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)

        grid_sizer_menus.AddGrowableRow(0)
        grid_sizer_menus.AddGrowableCol(0)
        box_menus.Add(grid_sizer_menus, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_menus, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def OnSpinMois(self, event):
        x = event.GetPosition()
        mois = self.ctrl_mois.GetSelection()+x
        if mois != -1 and mois < 12 :
            self.ctrl_mois.SetSelection(mois)
            self.MAJ()
        self.spin_mois.SetValue(0)

    def OnBoutonRestaurateur(self, event):
        IDrestaurateur = self.ctrl_restaurateur.GetID()
        from Dlg import DLG_Restaurateurs
        dlg = DLG_Restaurateurs.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_restaurateur.MAJlisteDonnees()
        self.ctrl_restaurateur.SetID(IDrestaurateur)
        self.MAJ()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def GetPeriode(self):
        return {"mois" : self.ctrl_mois.GetSelection()+1, "annee" : self.ctrl_annee.GetValue()}

    def MAJ(self, event=None):
        periode = self.GetPeriode()
        IDrestaurateur = self.ctrl_restaurateur.GetID()
        self.ctrl_menus.MAJ(periode=periode, IDrestaurateur=IDrestaurateur)

    def OnClose(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        event.Skip()

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def Imprimer(self, event=None):
        if self.ctrl_restaurateur.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un restaurateur dans la liste !"), _(u"Avertissement"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération des dates extrêmes affichées
        annee = self.ctrl_annee.GetValue()
        mois = self.ctrl_mois.GetSelection()+1
        tmp, nbreJours = calendar.monthrange(annee, mois)
        date_min = datetime.date(annee, mois, 1)
        date_max = datetime.date(annee, mois, nbreJours)
        periode = (date_min, date_max)

        # Ouvre la fenêtre des options
        from Dlg import DLG_Options_impression_menu
        dlg = DLG_Options_impression_menu.Dialog(self, periode=periode, IDrestaurateur=self.ctrl_restaurateur.GetID())
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
        else :
            dlg.Destroy()
            return





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
