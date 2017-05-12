#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Ctrl import CTRL_Bandeau
from Ol import OL_Comptes_internet
from Utils import UTILS_Envoi_email
from dateutil import relativedelta

CHOIX_DELAIS = [
    ("mois", 1, _(u"1 mois")),
    ("mois", 2, _(u"2 mois")),
    ("mois", 3, _(u"3 mois")),
    ("mois", 6, _(u"6 mois")),
    ("annees", 1, _(u"1 an")),
    ("annees", 2, _(u"2 ans")),
    ("annees", 3, _(u"3 ans")),
    ("annees", 4, _(u"4 ans")),
    ("annees", 5, _(u"5 ans")),
    ("annees", 6, _(u"6 ans")),
    ]


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter et imprimer la liste des comptes internet. Vous pouvez utiliser les fonctions Activer et Désactiver disponibles à droite de la liste pour modifier l'activation des comptes cochés.")
        titre = _(u"Liste des comptes internet")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Connecthys.png")

        self.radio_tous = wx.RadioButton(self, -1, _(u"Toutes les familles"), style=wx.RB_GROUP)
        self.radio_sans_activite = wx.RadioButton(self, -1, _(u"Les familles inactives depuis plus de"))
        self.ctrl_date_sans_activite = wx.Choice(self, -1, choices=[x[2] for x in CHOIX_DELAIS])
        self.ctrl_date_sans_activite.Select(0)
        self.radio_avec_activite = wx.RadioButton(self, -1, _(u"Les familles actives depuis"))
        self.ctrl_date_avec_activite = wx.Choice(self, -1, choices=[x[2] for x in CHOIX_DELAIS])
        self.ctrl_date_avec_activite.Select(0)

        self.listviewAvecFooter = OL_Comptes_internet.ListviewAvecFooter(self, kwargs={})
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Comptes_internet.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)
        
        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_actif = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_inactif = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer les codes internet par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_reinit_passwords = CTRL_Bouton_image.CTRL(self, texte=_(u"Réinitialiser les mots de passe"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelection, self.radio_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelection, self.radio_sans_activite)
        self.Bind(wx.EVT_CHOICE, self.OnRadioSelection, self.ctrl_date_sans_activite)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelection, self.radio_avec_activite)
        self.Bind(wx.EVT_CHOICE, self.OnRadioSelection, self.ctrl_date_avec_activite)

        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.OuvrirFicheFamille, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Activer, self.bouton_actif)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Desactiver, self.bouton_inactif)
        self.Bind(wx.EVT_BUTTON, self.EnvoyerEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ReinitPasswords, self.bouton_reinit_passwords)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        self.OnRadioSelection()
        self.ctrl_listview.MAJ()

    def __set_properties(self):
        self.SetTitle(_(u"Liste des comptes internet"))
        self.bouton_ouvrir_fiche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la fiche famille sélectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_actif.SetToolTip(wx.ToolTip(_(u"Cliquez ici activer les comptes cochés dans la liste")))
        self.bouton_inactif.SetToolTip(wx.ToolTip(_(u"Cliquez ici désactiver les comptes cochés dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer un email contenant des codes internet aux familles cochées")))
        self.bouton_reinit_passwords.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser les mots de passe des familles cochées")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_haut.Add(self.radio_tous, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.radio_sans_activite, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.ctrl_date_sans_activite, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.radio_avec_activite, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.ctrl_date_avec_activite, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(grid_sizer_haut, 0, wx.EXPAND, 0)

        grid_sizer_contenu.Add( (10, 10), 1, wx.EXPAND, 0)

        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_actif, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_inactif, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_reinit_passwords, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnRadioSelection(self, event=None):
        date_jour = datetime.date.today()
        self.ctrl_date_sans_activite.Enable(self.radio_sans_activite.GetValue())
        self.ctrl_date_avec_activite.Enable(self.radio_avec_activite.GetValue())

        if self.radio_tous.GetValue() == True :
            filtre = None
        else :
            if self.radio_sans_activite.GetValue() == True :
                index = self.ctrl_date_sans_activite.GetSelection()
                type_filtre = "sans"

            if self.radio_avec_activite.GetValue() == True :
                index = self.ctrl_date_avec_activite.GetSelection()
                type_filtre = "avec"

            type_valeur, valeur, label = CHOIX_DELAIS[index]
            if type_valeur == "mois" :
                date_limite = date_jour - relativedelta.relativedelta(months=+valeur)
            if type_valeur == "annees":
                date_limite = date_jour - relativedelta.relativedelta(years=+valeur)
            filtre = (type_filtre, date_limite)

        self.ctrl_listview.SetFiltre(filtre)

    def EnvoyerEmail(self, event):
        """ Envoi par Email des codes internet """
        # Validation des données saisies
        tracks = self.ctrl_listview.GetTracksCoches()
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération des données
        listeDonnees = []
        listeAnomalies = []
        listeEnvoiNonDemande = []
        for track in tracks :
            adresse = UTILS_Envoi_email.GetAdresseFamille(track.IDfamille, choixMultiple=False, muet=True, nomTitulaires=track.nomTitulaires)

            # Mémorisation des données
            if adresse not in (None, "", []):
                champs = {
                    "{NOM_FAMILLE}" : track.nomTitulaires,
                    "{IDENTIFIANT_INTERNET}" : track.internet_identifiant,
                    "{MOTDEPASSE_INTERNET}" : track.internet_mdp,
                }
                listeDonnees.append({"adresse" : adresse, "pieces" : [], "champs" : champs})
            else :
                listeAnomalies.append(track.nomTitulaires)

        # Annonce les anomalies trouvées
        if len(listeAnomalies) > 0 :
            texte = _(u"%d des familles sélectionnées n'ont pas d'adresse Email.\n\n") % len(listeAnomalies)
            texte += _(u"Souhaitez-vous quand même continuer avec les %d autres familles ?") % len(listeDonnees)
            dlg = wx.MessageDialog(self, texte, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Dernière vérification avant transfert
        if len(listeDonnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il ne reste finalement aucune donnée à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Transfert des données vers DLG Mailer
        import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie="portail")
        dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
        dlg.ChargerModeleDefaut()
        dlg.ShowModal()
        dlg.Destroy()











if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
