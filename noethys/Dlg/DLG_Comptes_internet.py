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





class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter et imprimer la liste des comptes internet. Vos pouvez utiliser les fonctions Activer et Désactiver disponibles à droite de la liste pour modifier l'activation des comptes cochés.")
        titre = _(u"Liste des comptes internet")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Connecthys.png")
        
        self.ctrl_listview = OL_Comptes_internet.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((100, 100))
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

        self.ctrl_listview.MAJ()

    def __set_properties(self):
        self.SetTitle(_(u"Liste des comptes internet"))
        self.bouton_ouvrir_fiche.SetToolTipString(_(u"Cliquez ici pour ouvrir la fiche famille sélectionnée dans la liste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Texte"))
        self.bouton_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.bouton_actif.SetToolTipString(_(u"Cliquez ici activer les comptes cochés dans la liste"))
        self.bouton_inactif.SetToolTipString(_(u"Cliquez ici désactiver les comptes cochés dans la liste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_email.SetToolTipString(_(u"Cliquez ici pour envoyer un email contenant des codes internet aux familles cochées"))
        self.bouton_reinit_passwords.SetToolTipString(_(u"Cliquez ici pour réinitialiser les mots de passe des familles cochées"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
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
        
        grid_sizer_contenu.AddGrowableRow(0)
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
