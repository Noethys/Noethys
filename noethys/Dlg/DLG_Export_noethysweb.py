#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Export_noethysweb
from Ctrl import CTRL_Editeur_email
import os, datetime


class CTRL_Options(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.dictDonnees = {}
        self.dictIndex = {}
        self.listeOptions = [
            ("individus", _(u"Individus et familles")),
            ("questionnaires", _(u"Questionnaires familiaux et individuels")),
            ("pieces", _(u"Pièces et types de pièces")),
            ("cotisations", _(u"Cotisations")),
            ("activites", _(u"Activités")),
            ("inscriptions", _(u"Inscriptions")),
            ("consommations", _(u"Consommations et prestations")),
            ("facturation", _(u"Facturation : factures, attestations, devis...")),
        ]
        self.MAJ()

    def MAJ(self):
        self.Clear()
        self.dictIndex = {}
        index = 0
        for code, label in self.listeOptions:
            self.Append(label)
            self.dictIndex[index] = code
            self.Check(index)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeOptions)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.dictIndex[index])
        return listeIDcoches


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Export_noethysweb", style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        # Bandeau
        intro = _(u"Utilisez cette fonctionnalité pour convertir votre base de données au format Noethysweb. Saisissez un mot de passe deux fois et cliquez sur le bouton Générer.")
        titre = _(u"Exporter les données vers Noethysweb")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document_export.png")

        # Fichier de destination
        self.box_destination_staticbox = wx.StaticBox(self, -1, _(u"Destination"))
        self.label_nom = wx.StaticText(self, -1, u"Nom :")
        nom_fichier = _(u"Noethysweb_%s") % datetime.datetime.now().strftime("%Y%m%d_%H%M")
        self.ctrl_nom = wx.TextCtrl(self, -1, nom_fichier)

        self.label_repertoire = wx.StaticText(self, -1, u"Répertoire :")
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        self.ctrl_repertoire = wx.TextCtrl(self, -1, cheminDefaut)
        self.bouton_repertoire = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Repertoire.png"), wx.BITMAP_TYPE_ANY))

        # Mot de passe
        self.box_cryptage_staticbox = wx.StaticBox(self, -1, _(u"Cryptage"))
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.label_confirmation = wx.StaticText(self, -1, _(u"Confirmation :"))
        self.ctrl_confirmation = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Données à transférer"))
        self.ctrl_options = CTRL_Options(self)
        self.ctrl_options.SetMinSize((-1, 140))

        # CTRL Editeur d'Emails pour récupérer la version HTML d'un texte XML
        self.ctrl_editeur = CTRL_Editeur_email.CTRL(self)
        self.ctrl_editeur.Show(False)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_generer = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer"), cheminImage="Images/32x32/Sauvegarder.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonRepertoire, self.bouton_repertoire)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGenerer, self.bouton_generer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du fichier de sauvegarde")))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Saisissez le mot de passe qui sera utilisée pour crypter la sauvegarde")))
        self.ctrl_confirmation.SetToolTip(wx.ToolTip(_(u"Confirmez le mot de passe")))
        self.ctrl_repertoire.SetMinSize((350, -1))
        self.ctrl_repertoire.SetToolTip(wx.ToolTip(_(u"Saisissez ici le répertoire de destination")))
        self.bouton_repertoire.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un répertoire de destination")))

        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_editeur, 0, wx.EXPAND, 0)

        # Contenu
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Destination
        box_destination = wx.StaticBoxSizer(self.box_destination_staticbox, wx.VERTICAL)
        grid_sizer_destination = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_destination.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_destination.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_destination.Add(self.label_repertoire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_repertoire = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_repertoire.Add(self.ctrl_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.bouton_repertoire, 0, 0, 0)
        grid_sizer_repertoire.AddGrowableCol(0)

        grid_sizer_destination.Add(grid_sizer_repertoire, 1, wx.EXPAND, 0)

        grid_sizer_destination.AddGrowableCol(1)
        box_destination.Add(grid_sizer_destination, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_contenu.Add(box_destination, 1, wx.EXPAND, 0)

        # Cryptage
        box_cryptage = wx.StaticBoxSizer(self.box_cryptage_staticbox, wx.VERTICAL)
        grid_sizer_cryptage = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_cryptage.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_cryptage.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_cryptage.Add(self.label_confirmation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_cryptage.Add(self.ctrl_confirmation, 0, wx.EXPAND, 0)
        grid_sizer_cryptage.AddGrowableCol(1)
        box_cryptage.Add(grid_sizer_cryptage, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_contenu.Add(box_cryptage, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        box_options.Add(self.ctrl_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_generer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonRepertoire(self, event):
        if self.ctrl_repertoire.GetValue != "":
            cheminDefaut = self.ctrl_repertoire.GetValue()
            if os.path.isdir(cheminDefaut) == False :
                cheminDefaut = ""
        else:
            cheminDefaut = ""
        dlg = wx.DirDialog(self, _(u"Veuillez sélectionner un répertoire de destination :"), defaultPath=cheminDefaut, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_repertoire.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnBoutonGenerer(self, event):
        # Nom
        nom = self.ctrl_nom.GetValue()
        if not nom:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        # Mot de passe
        motdepasse = self.ctrl_mdp.GetValue()
        confirmation = self.ctrl_confirmation.GetValue()
        if not motdepasse:
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un mot de passe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_mdp.SetFocus()
            return False
        if motdepasse != confirmation:
            dlg = wx.MessageDialog(self, _(u"Le mot de passe n'a pas été confirmé à l'identique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_confirmation.SetFocus()
            return False
        # if six.PY3:
        #     motdepasse = six.binary_type(motdepasse, "utf-8")
        # motdepasse = base64.b64encode(motdepasse)

        # Répertoire
        repertoire = self.ctrl_repertoire.GetValue()
        if repertoire == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un répertoire de destination !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_repertoire.SetFocus()
            return False
        # Vérifie que le répertoire existe
        if not os.path.isdir(repertoire):
            dlg = wx.MessageDialog(self, _(u"Le répertoire de destination que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_repertoire.SetFocus()
            return False

        # Options
        options = self.ctrl_options.GetIDcoches()

        # Générer du fichier de données
        dlgAttente = wx.BusyInfo(_(u"Cette opération peut prendre quelques minutes. Veuillez patienter..."), self)
        UTILS_Export_noethysweb.Export_all(dlg=self, nom_fichier=os.path.join(repertoire, nom + ".nweb"), mdp=motdepasse, options=options)
        del dlgAttente

        # Confirmation de réussite
        dlg = wx.MessageDialog(self, _(u"Le fichier a été généré avec succès."), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True




if __name__ == u"__main__":
    app = wx.App(0)
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
