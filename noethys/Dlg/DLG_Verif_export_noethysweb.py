#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import io, csv, codecs, six
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils.UTILS_Verif_export_noethysweb import ERREUR, AVERTISSEMENT


COLONNES = [
    (_(u"Gravité"), 90),
    (_(u"Élément concerné"), 230),
    (_(u"Famille / individu"), 200),
    (_(u"Problème"), 450),
    (_(u"Table"), 120),
]


class CTRL_Anomalies(wx.ListCtrl):
    """ Liste virtuelle pour supporter un grand nombre d'anomalies """
    def __init__(self, parent, anomalies=[]):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES)
        self.anomalies = anomalies

        self.imageList = wx.ImageList(16, 16)
        self.img_erreur = self.imageList.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.img_avertissement = self.imageList.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.imageList, wx.IMAGE_LIST_SMALL)

        for index, (label, largeur) in enumerate(COLONNES):
            self.InsertColumn(index, label, width=largeur)
        self.SetItemCount(len(self.anomalies))

    def OnGetItemText(self, item, col):
        anomalie = self.anomalies[item]
        if col == 0:
            return _(u"Erreur") if anomalie.gravite == ERREUR else _(u"Avertissement")
        if col == 1:
            return anomalie.element
        if col == 2:
            return anomalie.contexte
        if col == 3:
            return anomalie.message
        if col == 4:
            return anomalie.table
        return u""

    def OnGetItemImage(self, item):
        return self.img_erreur if self.anomalies[item].gravite == ERREUR else self.img_avertissement


def Get_lignes(anomalies):
    lignes = [[label for label, largeur in COLONNES]]
    for anomalie in anomalies:
        lignes.append([_(u"Erreur") if anomalie.gravite == ERREUR else _(u"Avertissement"),
                       anomalie.element, anomalie.contexte, anomalie.message, anomalie.table])
    return lignes


class Dialog(wx.Dialog):
    def __init__(self, parent, anomalies=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Verif_export_noethysweb", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.parent = parent
        # Erreurs en premier
        self.anomalies = sorted(anomalies, key=lambda a: (a.gravite != ERREUR, a.modele, a.pk if isinstance(a.pk, six.integer_types) else 0))
        self.nbre_erreurs = len([a for a in anomalies if a.gravite == ERREUR])
        self.nbre_avertissements = len(anomalies) - self.nbre_erreurs

        # Bandeau
        titre = _(u"Vérification des données avant export")
        self.SetTitle(titre)
        if self.nbre_erreurs:
            intro = _(u"%d erreur(s) et %d avertissement(s) ont été détectés. Les erreurs bloqueront l'importation dans Noethysweb : corrigez-les dans Noethys puis relancez l'export.") % (self.nbre_erreurs, self.nbre_avertissements)
        else:
            intro = _(u"%d avertissement(s) ont été détectés. Vous pouvez corriger les données concernées ou générer le fichier malgré tout.") % self.nbre_avertissements
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Attention.png")

        # Liste
        self.ctrl_anomalies = CTRL_Anomalies(self, anomalies=self.anomalies)
        self.ctrl_anomalies.SetMinSize((900, 400))

        # Boutons
        self.bouton_exporter = CTRL_Bouton_image.CTRL(self, texte=_(u"Exporter la liste"), cheminImage="Images/32x32/Excel.png")
        self.bouton_copier = CTRL_Bouton_image.CTRL(self, texte=_(u"Copier"), cheminImage="Images/32x32/Texte_ligne.png")
        self.bouton_generer = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer quand même"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler l'export"), cheminImage="Images/32x32/Annuler.png")

        self.bouton_exporter.SetToolTip(wx.ToolTip(_(u"Enregistrer la liste des anomalies dans un fichier CSV (ouvrable avec un tableur)")))
        self.bouton_copier.SetToolTip(wx.ToolTip(_(u"Copier la liste des anomalies dans le presse-papiers")))
        self.bouton_generer.SetToolTip(wx.ToolTip(_(u"Créer le fichier d'export sans corriger les anomalies")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Abandonner la création du fichier pour corriger les données")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_anomalies, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_exporter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_copier, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_generer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonExporter, self.bouton_exporter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCopier, self.bouton_copier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGenerer, self.bouton_generer)
        self.bouton_annuler.SetFocus()

    def Get_texte(self):
        return u"\n".join([u"\t".join(ligne) for ligne in Get_lignes(self.anomalies)])

    def OnBoutonCopier(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.Get_texte()))
            wx.TheClipboard.Close()
            dlg = wx.MessageDialog(self, _(u"La liste des anomalies a été copiée dans le presse-papiers."), _(u"Copier"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def OnBoutonExporter(self, event):
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(self, message=_(u"Enregistrer la liste des anomalies"), defaultDir=sp.GetDocumentsDir(),
                            defaultFile=u"Anomalies_export_noethysweb.csv", wildcard=_(u"Fichier CSV (*.csv)|*.csv"),
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        chemin = dlg.GetPath()
        dlg.Destroy()
        # Point-virgule et BOM UTF-8 pour une ouverture directe dans Excel / LibreOffice
        if six.PY2:
            with open(chemin, "wb") as fichier:
                fichier.write(codecs.BOM_UTF8)
                writer = csv.writer(fichier, delimiter=";")
                for ligne in Get_lignes(self.anomalies):
                    writer.writerow([six.text_type(x).encode("utf-8") for x in ligne])
        else:
            with io.open(chemin, "w", encoding="utf-8-sig", newline="") as fichier:
                writer = csv.writer(fichier, delimiter=";")
                for ligne in Get_lignes(self.anomalies):
                    writer.writerow(ligne)
        dlg = wx.MessageDialog(self, _(u"La liste des anomalies a été enregistrée."), _(u"Exporter"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonGenerer(self, event):
        if self.nbre_erreurs:
            dlg = wx.MessageDialog(self, _(u"%d erreur(s) bloquante(s) subsistent : l'importation dans Noethysweb risque fortement d'échouer.\n\nSouhaitez-vous vraiment générer le fichier sans les corriger ?") % self.nbre_erreurs,
                                   _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return
        self.EndModal(wx.ID_OK)


if __name__ == u"__main__":
    from Utils.UTILS_Verif_export_noethysweb import Anomalie
    app = wx.App(0)
    exemples = [
        Anomalie(gravite=ERREUR, modele="core.Depot", pk=12, champ="date", element=u"Dépôt ID12 « Chèques mars »", message=u"Le champ « Date » est obligatoire mais n'est pas renseigné."),
        Anomalie(gravite=AVERTISSEMENT, modele="core.Inscription", champ="activite", element=u"Inscription (tous)", message=u"Le champ « Activité » fait référence à des éléments « Activité » qui ne sont pas inclus dans l'export."),
    ]
    dialog_1 = Dialog(None, anomalies=exemples)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
