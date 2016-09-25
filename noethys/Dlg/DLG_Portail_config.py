#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import os
import shutil
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy
import random
import time
import psutil
import subprocess

import GestionDB
from Utils import UTILS_Parametres
from Utils import UTILS_Config


def GetSecretKey():
    code = ""
    for x in range(0, 40) :
        code += random.choice("abcdefghjkmvwxyz123456789123456789123456789ABCDEFVWXYZ")
    return code

LISTE_THEMES = [("blue", u"Bleu"), ("black", u"Noir"), ("green", u"Vert"), ("purple", u"Violet"), ("red", u"Rouge"), ("yellow", u"Jaune")]
LISTE_DELAIS_SYNCHRO = [(15, u"Toutes les 15 minutes"), (30, u"Toutes les 30 minutes"), (60, u"Toutes les heures"), (120, u"Toutes les 2 heures"), (180, u"Toutes les 3 heures"), (240, u"Toutes les 4 heures"), (300, u"Toutes les 5 heures")]
LISTE_AFFICHAGE_HISTORIQUE = [(30, u"1 mois"), (60, u"2 mois"), (90, u"3 mois"), (120, u"4 mois"), (150, u"5 mois"), (180, u"6 mois")]
LISTE_SELECTION_FACTURES = [(0, u"Toutes les factures"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]
LISTE_SELECTION_REGLEMENTS = [(0, u"Tous les règlements"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]

VALEURS_DEFAUT = {
    "portail_activation" : False,
    "client_synchro_portail_activation" : False,
    "client_synchro_portail_delai" : 2,
    "client_synchro_portail_ouverture" : False,
    "serveur_type": 0,
    "serveur_options": "",
    "serveur_cgi_file": "connecthys.cgi",
    "hebergement_type" : 0,
    "ftp_serveur" : "127.0.0.1",
    "ftp_utilisateur" : "",
    "ftp_mdp" : "",
    "ftp_repertoire" : "/www/connecthys",
    "url_connecthys" : "http://127.0.0.1:5000",
    "hebergement_local_repertoire" : "/tmp/connecthys",
    "db_type" : 1,
    "db_serveur" : "",
    "db_utilisateur" : "",
    "db_mdp" : "",
    "db_nom" : "",
    "prefixe_tables" : "",
    "secret_key" : GetSecretKey(),
    "mode_debug" : False,
    "crypter_transferts" : True,
    "image_identification" : "",
    "theme" : 0,
    "cadre_logo" : 0,
    "recevoir_document_email" : True,
    "recevoir_document_courrier" : True,
    "recevoir_document_site" : True,
    "recevoir_document_site_lieu" : _(u"à l'accueil de la structure"),
    "paiement_ligne_actif" : False,
    "activites_afficher" : True,
    "activites_autoriser_inscription" : True,
    "reservations_afficher" : True,
    "factures_afficher" : True,
    "factures_selection" : 0,
    "factures_demande_facture" : True,
    "reglements_afficher" : True,
    "reglements_selection" : 0,
    "reglements_demande_recu" : True,
    "pieces_afficher" : True,
    "pieces_autoriser_telechargement" : True,
    "cotisations_afficher" : True,
    "historique_afficher" : True,
    "historique_delai" : 0,
    "contact_afficher" : True,
    "contact_carte_afficher" : True,
    "mentions_afficher" : True,
    "aide_afficher" : True,
    }



class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)
        self.parent = parent
        self.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    def OnPropGridChange(self, event):
        if event.GetPropertyName() == "portail_activation" :
            value = event.GetPropertyValue()
            self.parent.SetActivation(value)
        elif event.GetPropertyName() == "hebergement_type" :
            value = event.GetPropertyValue()
            if value == 0 :
                self.SwitchHostingToLocal()
            elif value == 1 :
                self.SwitchHostingToFTP()
            else :
                raise
        elif event.GetPropertyName() == "db_type" :
            value = event.GetPropertyValue()
            if value == 0 :
                self.SwitchDatabaseToLocal()
            elif value == 1 :
                self.SwitchDatabaseToNetwork()
            else :
                raise
        elif event.GetPropertyName() == "serveur_type" :
            value = event.GetPropertyValue()
            if property is not None :
                if value == 1 :
                    self.SwitchServerToCgi()
                elif value == 0 :
                    self.SwitchServerToStandalone()
                else :
                    raise
        self.RefreshGrid()
        event.Skip()

    def SwitchHostingToLocal(self):
        property = self.GetProperty("ftp_serveur")
        property.SetAttribute("obligatoire", False)
        property.Hide(True)
        property = self.GetProperty("ftp_utilisateur")
        property.SetAttribute("obligatoire", False)
        property.Hide(True)
        property = self.GetProperty("ftp_mdp")
        property.SetAttribute("obligatoire", False)
        property.Hide(True)
        property = self.GetProperty("ftp_repertoire")
        property.SetAttribute("obligatoire", False)
        property.Hide(True)
        property = self.GetProperty("hebergement_local_repertoire")
        property.SetAttribute("obligatoire", True)
        property.Hide(False)

    def SwitchHostingToFTP(self):
        property = self.GetProperty("ftp_serveur")
        property.SetAttribute("obligatoire", True)
        property.Hide(False)
        property = self.GetProperty("ftp_utilisateur")
        property.SetAttribute("obligatoire", True)
        property.Hide(False)
        property = self.GetProperty("ftp_mdp")
        property.SetAttribute("obligatoire", True)
        property.Hide(False)
        property = self.GetProperty("ftp_repertoire")
        property.SetAttribute("obligatoire", True)
        property.Hide(False)
        property = self.GetProperty("hebergement_local_repertoire")
        property.SetAttribute("obligatoire", False);
        property.Hide(True);

    def SwitchDatabaseToLocal(self):
        property = self.GetProperty("db_serveur")
        property.Hide(True)
        property = self.GetProperty("db_utilisateur")
        property.Hide(True)
        property = self.GetProperty("db_mdp")
        property.Hide(True)
        property = self.GetProperty("db_nom")
        property.Hide(True)

    def SwitchDatabaseToNetwork(self):
        property = self.GetProperty("db_serveur")
        property.Hide(False)
        property = self.GetProperty("db_utilisateur")
        property.Hide(False)
        property = self.GetProperty("db_mdp")
        property.Hide(False)
        property = self.GetProperty("db_nom")
        property.Hide(False)

    def SwitchServerToStandalone(self):
        property = self.GetProperty("serveur_options")
        property.Hide(False)
        property = self.GetProperty("serveur_cgi_file")
        property.Hide(True)

    def SwitchServerToCgi(self):
        property = self.GetProperty("serveur_cgi_file")
        property.Hide(False)
        property = self.GetProperty("serveur_options")
        property.Hide(True)

    def Remplissage(self):

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Activation")) )

        # Activation du serveur de synchronisation
        nom = "portail_activation"
        propriete = wxpg.BoolProperty(label=_(u"Activer Connecthys"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer Connecthys pour ce fichier"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Type de serveur
        nom = "serveur_type"
        propriete = wxpg.EnumProperty(label=_(u"Type de serveur"), labels=[_(u"Autonome"), _(u"CGI")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez le type de serveur utilisé : Autonome ou CGI"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Serveur autonome
        nom = "serveur_options"
        propriete = wxpg.StringProperty(label=_(u"Options pour le serveur autonome"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez les options du serveur autonome (Ex : -s tornado)"))
        self.Append(propriete)

        # Serveur CGI
        nom = "serveur_cgi_file"
        propriete = wxpg.StringProperty(label=_(u"Nom du fichier CGI"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le nom du fichier CGI (Ex : connecthys.cgi)"))
        self.Append(propriete)

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Client de synchronisation")) )

        # Activation du client de synchronisation
        nom = "client_synchro_portail_activation"
        propriete = wxpg.BoolProperty(label=_(u"Activer sur cet ordinateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer le client de synchronisation sur la page d'accueil de Noethys sur cet ordinateur"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Délai de synchronisation du client
        nom = "client_synchro_portail_delai"
        propriete = wxpg.EnumProperty(label=_(u"Délai de synchronisation"), labels=[y for x, y in LISTE_DELAIS_SYNCHRO], values=range(0, len(LISTE_DELAIS_SYNCHRO)), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez un délai pour la synchronisation"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Synchroniser à l'ouverture de Noethys
        nom = "client_synchro_portail_ouverture"
        propriete = wxpg.BoolProperty(label=_(u"Synchroniser à l'ouverture"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour synchroniser automatiquement à l'ouverture de Noethys sur cet ordinateur"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Hébergement du portail")) )

        # Type d'hébergement
        nom = "hebergement_type"
        propriete = wxpg.EnumProperty(label=_(u"Type d'hébergement"), labels=[_(u"Local"), _(u"FTP")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
	propriete.SetHelpString(_(u"Sélectionnez le type d'hébergement à utiliser : Local (Connecthys est installé sur l'ordinateur) ou FTP (Connecthys est envoyé sur un répertoire FTP)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Serveur FTP
        nom = "ftp_serveur"
        propriete = wxpg.StringProperty(label=_(u"Adresse du serveur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'adresse du serveur FTP (Ex : ftp.monsite.com)"))
        self.Append(propriete)

        # Utilisateur
        nom = "ftp_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'utilisateur FTP"))
        self.Append(propriete)

        # Mot de passe
        nom = "ftp_mdp"
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe FTP"))
        self.Append(propriete)

        # Répertoire FTP
        nom = "ftp_repertoire"
        propriete = wxpg.StringProperty(label=_(u"Répertoire"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le répertoire FTP (ex : www/connecthys)"))
        self.Append(propriete)


        # Repertoire Hebergement Local
        nom = "hebergement_local_repertoire"
        propriete = wxpg.StringProperty(label=_(u"Répertoire local"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le répertoire local (Ex : /home/bogucool/connecthys)"))
        self.Append(propriete)

        # Url Connecthys
        nom = "url_connecthys"
        propriete = wxpg.StringProperty(label=_(u"URL d'accès à Connecthys "), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'url d'accès à Connecthys (ex : http://127.0.0.1:5000 ou http://www.monsite.com/connecthys)"))
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Base de données")) )

        # Type base de données
        nom = "db_type"
        propriete = wxpg.EnumProperty(label=_(u"Type de base"), labels=[_(u"Locale (Sqlite)"), _(u"Réseau (MySQL)")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez le type de base de données à utiliser (locale ou réseau). MySQL est fortement conseillé afin d'éviter les conflits d'écriture en cas d'accès simultanés d'internautes."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Serveur SQL
        nom = "db_serveur"
        propriete = wxpg.StringProperty(label=_(u"Adresse du serveur MySQL"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'adresse du serveur MySQL"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Utilisateur
        nom = "db_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'utilisateur"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Mot de passe
        nom = "db_mdp"
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Nom de la base
        nom = "db_nom"
        propriete = wxpg.StringProperty(label=_(u"Nom de la base"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le nom de la base de données à utiliser"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Préfixe des tables
        nom = "prefixe_tables"
        propriete = wxpg.StringProperty(label=_(u"Préfixe des tables (optionnel)"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un préfixe pour les tables (optionnel)"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Sécurité")) )

        # Clé secrète
        nom = "secret_key"
        propriete = wxpg.StringProperty(label=_(u"Clé de sécurité"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une clé secrète (générée automatiquement par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Cryptage des transferts
        nom = "crypter_transferts"
        propriete = wxpg.BoolProperty(label=_(u"Crypter les données lors des transferts"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour crypter les données lors des transferts"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Mode debug
        nom = "mode_debug"
        propriete = wxpg.BoolProperty(label=_(u"Mode debug"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer le mode debug (Ne surtout pas utiliser en production !)"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Affichage")) )

        # Image de fond du login
        nom = "image_identification"
        propriete = wxpg.ImageFileProperty(label=_(u"Image de fond de la page d'identification"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une image pour la page d'identification"))
        self.Append(propriete)

        # Thème
        nom = "theme"
        propriete = wxpg.EnumProperty(label=_(u"Thème"), labels=[y for x, y in LISTE_THEMES], values=range(0, len(LISTE_THEMES)), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez un thème pour l'affichage"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Cadre logo organisateur
        nom = "cadre_logo"
        propriete = wxpg.EnumProperty(label=_(u"Cadre du logo de l'organisateur"), labels=[_(u"Carré"), _(u"Rond")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez le type de cadre du logo de l'organisateur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Recevoir un document")) )

        # Recevoir par Email
        nom = "recevoir_document_email"
        propriete = wxpg.BoolProperty(label=_(u"Recevoir par Email"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer la fonction Recevoir un document par Email"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Recevoir par courrier
        nom = "recevoir_document_courrier"
        propriete = wxpg.BoolProperty(label=_(u"Recevoir par courrier"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer la fonction Recevoir un document par courrier"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Retirer sur le site
        nom = "recevoir_document_site"
        propriete = wxpg.BoolProperty(label=_(u"Retirer sur un site"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer la fonction Retirer un document sur site"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Lieu pour retraite sur site
        nom = "recevoir_document_site_lieu"
        propriete = wxpg.StringProperty(label=_(u"Lieu du retrait sur site"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un nom de lieux pour le retrait du document (ex: à l'accueil de la structure)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Paiement en ligne")) )

        # Activer le paiement en ligne
        nom = "paiement_ligne_actif"
        propriete = wxpg.BoolProperty(label=_(u"Activer le paiement en ligne"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer la fonction de paiement en ligne"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Activités'")) )

        # Afficher
        nom = "activites_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Incription à une activité
        nom = "activites_autoriser_inscription"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser l'inscription à des activités"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser l'inscription à des activités"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Réservations'")) )

        # Afficher
        nom = "reservations_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Factures'")) )

        # Afficher
        nom = "factures_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Sélection des factures à afficher
        nom = "factures_selection"
        propriete = wxpg.EnumProperty(label=_(u"Sélection des factures à afficher"), labels=[y for x, y in LISTE_SELECTION_FACTURES], values=[x for x, y in LISTE_SELECTION_FACTURES], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez un critère d'ancienneté pour les factures à afficher"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Demande d'une facture
        nom = "factures_demande_facture"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser la demande de factures"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser la demande de factures"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Règlements'")) )

        # Afficher
        nom = "reglements_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Sélection des règlements à afficher
        nom = "reglements_selection"
        propriete = wxpg.EnumProperty(label=_(u"Sélection des règlements à afficher"), labels=[y for x, y in LISTE_SELECTION_REGLEMENTS], values=[x for x, y in LISTE_SELECTION_REGLEMENTS], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez un critère d'ancienneté pour les règlements à afficher"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Demande d'un reçu
        nom = "reglements_demande_recu"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser la demande de reçus"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser la demande de reçus de règlements"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Pièces'")) )

        # Afficher
        nom = "pieces_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Téléchargements de pièces
        nom = "pieces_autoriser_telechargement"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser le téléchargement de pièces"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser le téléchargement de pièces"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Cotisations'")) )

        # Afficher
        nom = "cotisations_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Historique'")) )

        # Afficher
        nom = "historique_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Délai d'affichage de l'historique
        nom = "historique_delai"
        propriete = wxpg.EnumProperty(label=_(u"Temps d'affichage de l'historique"), labels=[y for x, y in LISTE_AFFICHAGE_HISTORIQUE], values=range(0, len(LISTE_AFFICHAGE_HISTORIQUE)), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez un délai pour l'affichage de l'historique : Au-delà  l'historique sera caché."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Contact'")) )

        # Afficher
        nom = "contact_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher la carte
        nom = "contact_carte_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la carte Google Maps"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher la carte Google Maps"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Mentions légales'")) )

        # Afficher
        nom = "mentions_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Aide'")) )

        # Afficher
        nom = "aide_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)




    def Validation(self):
        """ Validation des données saisies """
        for nom, valeur in self.GetPropertyValues().iteritems() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True :
                if valeur == "" or valeur == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % nom, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        return True

    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())

        # Recherche les paramètres mémorisés dans la base de données
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="portail", dictParametres=dictValeurs)

        # Recherche des config mémorisés sur cet ordi
        dictParametres["client_synchro_portail_activation"] = UTILS_Config.GetParametre("client_synchro_portail_activation", False)
        dictParametres["client_synchro_portail_delai"] = UTILS_Config.GetParametre("client_synchro_portail_delai", 2)
        dictParametres["client_synchro_portail_ouverture"] = UTILS_Config.GetParametre("client_synchro_portail_ouverture", True)
        dictParametres["hebergement_type"] = UTILS_Config.GetParametre("hebergement_type", 0)
        dictParametres["serveur_type"] = UTILS_Config.GetParametre("serveur_type", 0)

        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue()
            propriete.SetValue(valeur)

        property = self.GetProperty("hebergement_type")
        if property is not None :
            value = property.GetValue()
            if value == 1 :
                self.SwitchHostingToFTP()
            elif value == 0 :
                self.SwitchHostingToLocal()
            else :
                raise

        property = self.GetProperty("db_type")
        if property is not None :
            value = property.GetValue()
            if value == 1 :
                self.SwitchDatabaseToNetwork()
            elif value == 0 :
                self.SwitchDatabaseToLocal()
            else :
                raise

        property = self.GetProperty("serveur_type")
        if property is not None :
            value = property.GetValue()
        if value == 1 :
            self.SwitchServerToCgi()
        elif value == 0 :
            self.SwitchServerToStandalone()
        else :
            raise

    def Sauvegarde(self):
        """ Mémorisation des valeurs du contrôle """
        # Mémorisation des paramètres dans la base de données
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="portail", dictParametres=dictValeurs)

        # Mémorisation de la config sur cet ordi
        for key in ("client_synchro_portail_activation", "client_synchro_portail_delai", "client_synchro_portail_ouverture", "hebergement_type", "serveur_type") :
            UTILS_Config.SetParametre(key, self.GetPropertyByName(key).GetValue())

    def GetValeurs(self) :
        return self.GetPropertyValues()

    def OnPropChange(self, event):
        prop = event.GetProperty()
        if prop :
            if prop.GetName() == "portail_activation" :
                self.parent.SetActivation(prop.GetValue())





class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        # Bandeau
        intro = _(u"Connecthys est le portail internet de Noethys. Vous devez au préalable disposer d'un hébergement internet compatible. Utilisez les fonctionnalités ci-dessous pour installer et synchroniser le portail avec votre fichier de données Noethys.")
        titre = _(u"Connecthys")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Connecthys.png")

        # Paramètres
        self.box_parametres = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)

        # Log
        self.box_log = wx.StaticBox(self, -1, _(u"Journal"))
        self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.log.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.log.SetMinSize((-1, 55))
        self.gauge = wx.Gauge(self, -1, range=100, size=(-1, 8))
        self.gauge.Show(False)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Inits
        self.SetActivation(self.ctrl_parametres.GetPropertyByName("portail_activation").GetValue())

        # Affichage avertissement
        wx.CallAfter(self.Afficher_avertissement)

    def __set_properties(self):
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour accéder aux outils"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((750, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Log
        staticbox_actions = wx.StaticBoxSizer(self.box_log, wx.VERTICAL)
        grid_sizer_actions = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_actions.Add(self.log, 1, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.gauge, 0, wx.EXPAND, 0)
        staticbox_actions.Add(grid_sizer_actions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_actions, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        self.SetSize((self.GetMinSize()))

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        self.MemoriseParametres()
        self.EndModal(wx.ID_CANCEL)

    def OnClose(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        self.MemoriseParametres()
        event.Skip()

    def MemoriseParametres(self):
        self.ctrl_parametres.Sauvegarde()

    def SetActivation(self, activation=False):
        self.bouton_outils.Enable(activation)

    def EcritLog(self, message=""):
        horodatage = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        if len(self.log.GetValue()) > 0 :
            texte = u"\n"
        else :
            texte = u""
        try :
            texte += u"[%s] %s" % (horodatage, message)
        except :
            texte += u"[%s] %s" % (horodatage, str(message).decode('iso-8859-1'))
        self.log.AppendText(texte)

    def SetGauge(self, valeur=0):
        try:
            if valeur == 0 :
                if self.gauge.IsShown() :
                    self.gauge.Show(False)
            else :
                if not self.gauge.IsShown() :
                    self.gauge.Show(True)
            self.Layout()
            self.gauge.SetValue(valeur)
        except Exception as e:
            pass

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        dict_parametres = self.ctrl_parametres.GetValeurs()

        menu = wx.Menu()

        # Installer / Mettre à jour
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Installer / Mettre à jour"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Installer, id=id)

        menu.AppendSeparator()

        # Démarrer
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Démarrer le serveur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Play.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Demarrer_serveur, id=id)
        if dict_parametres["hebergement_type"] == 0 and dict_parametres["serveur_type"] == 0 :
            if len(self.GetListeProcess()) > 0 :
                item.Enable(False)
        else :
            item.Enable(False)

        # Arrêter
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Arrêter le serveur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Stop.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Arreter_serveur, id=id)
        if dict_parametres["hebergement_type"] == 0 and dict_parametres["serveur_type"] == 0 :
            if len(self.GetListeProcess()) == 0 :
                item.Enable(False)
        else :
            item.Enable(False)

        menu.AppendSeparator()

        # Ouvrir
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Ouvrir Connecthys dans le navigateur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Planete.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirNavigateur, id=id)

        menu.AppendSeparator()

        # Synchroniser
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Synchroniser les données"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Synchroniser, id=id)

        # Traiter les données
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Traiter les données"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Traiter, id=id)



        self.PopupMenu(menu)
        menu.Destroy()

    def Installer(self, event):
        # Récupération des paramètres de l'installation
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()

        if dict_parametres["hebergement_type"] == 1 :

            if dict_parametres["ftp_serveur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'adresse du serveur FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ftp_utilisateur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nomde de l'utilisateur FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ftp_mdp"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le mot de passe FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ftp_repertoire"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le répertoire FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        elif dict_parametres["hebergement_type"] == 0 :

            if dict_parametres["hebergement_local_repertoire"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le répertoire local !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        elif dict_parametres["serveur_type"] == 1 :

            if dict_parametres["serveur_cgi_file"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nom du fichier CGI !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        else :
            raise

        if dict_parametres["url_connecthys"] == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'url d'accès à Connecthys !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Procédure d'installation
        from Utils import UTILS_Portail_installation
        install = UTILS_Portail_installation.Installer(self, dict_parametres)
        resultat = install.Installer()

    def GetListeProcess(self):
        """ Recherche les process ouverts du portail """
        listeProcess = []
        for p in psutil.process_iter():
            if "python" in p.name() :
                cmdline = p.cmdline()
                if len(cmdline) > 0 and "run.py" in cmdline[1] :
                    listeProcess.append(p)
        return listeProcess

    def Demarrer_serveur(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()

        # Récupération des paramètres
        rep = dict_parametres["hebergement_local_repertoire"]
        options = dict_parametres["serveur_options"]
        chemin_executable = os.path.join(rep, "run.py")

        if rep == "" or os.path.isfile(chemin_executable) == False :
            dlg = wx.MessageDialog(None, _(u"Le chemin du répertoire d'installation de Connecthys n'est pas valide !"), _(u"Accès impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        args = ["python", chemin_executable]
        for arg in options.split(" ") :
            if arg != "" :
                args.append(arg)

        # Créé un nouveau process
        self.EcritLog(_(u"Lancement du serveur Connecthys..."))
        self.EcritLog(_(u"Chemin : ") + " ".join(args))

        p = subprocess.Popen(args, shell=False, cwd=rep)

        # Vérifie si le process est bien lancé
        time.sleep(0.5)
        if len(self.GetListeProcess()) > 0 :
            self.EcritLog(_(u"Serveur démarré"))
            dlg = wx.MessageDialog(None, _(u"Le serveur Connecthys a bien été démarré !"), _(u"Serveur Connecthys"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else :
            self.EcritLog(_(u"[ERREUR] Le serveur n'a pas pu être démarré"))
            dlg = wx.MessageDialog(None, _(u"Le serveur Connecthys n'a pas pu être démarré !"), _(u"Serveur Connecthys"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()


    def Arreter_serveur(self, event):
        """ Kill les process déjà ouverts """
        self.EcritLog(_(u"Arrêt du serveur"))
        for p in self.GetListeProcess() :
            p.kill()

    def OuvrirNavigateur(self, event):
        dict_parametres = self.ctrl_parametres.GetValeurs()
        url = dict_parametres["url_connecthys"]
        if url == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner l'URL d'accès à Connecthys !"), _(u"Accès impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.EcritLog(_(u"Ouverture dans le navigateur de l'url %s") % url)
        import webbrowser
        webbrowser.open(url)

    def Synchroniser(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.Start()

    def Traiter(self, event):
        from Dlg import DLG_Portail_demandes
        dlg = DLG_Portail_demandes.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def Afficher_avertissement(self):
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="portail", valeur=False) == True :
            return

        texte = u"""
<CENTER><IMG SRC="%s">
<BR><BR>
<FONT SIZE=3>
Connecthys est le portail internet de Noethys. Il permet par exemple à vos usagers de
consulter l'état de leur dossier ou de demander des réservations à des activités.
Si vous souhaitez en apprendre davantage sur son utilisation et son installation, consultez
la rubrique dédiée dans le forum de Noethys.
<BR><BR>
<B>Attention, Connecthys est actuellement en version Beta. Il n'est distribué qu'à des fins de tests
et reste fortement déconseillé pour une utilisation en production. Merci de signaler tout bug rencontré
sur le forum.</B>
</FONT>
</CENTER>
""" % Chemins.GetStaticPath("Images/Special/Connecthys.png")

        from Dlg import DLG_Message_html
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), size=(510, 670), nePlusAfficher=True)
        dlg.CenterOnScreen()
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="portail", valeur=nePlusAfficher)
        return True


class Synchro():
    def __init__(self, parent=None, dict_parametres=None):
        self.dict_parametres = dict_parametres
        self.parent = parent
        self.num_etape = 0
        self.texte_etape = ""

    def Start(self):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)

        # Ouverture de la dlg de progress
        self.dlgprogress = wx.ProgressDialog(_(u"Synchronisation en cours - Veuillez patienter..."), _(u"Lancement de la synchronisation..."), maximum=100, parent=None, style= wx.PD_SMOOTH | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)

        # Lancement de la synchro
        synchro.Synchro_totale()

        self.dlgprogress.Destroy()

    def EcritLog(self, texte=""):
        self.texte_etape = texte
        self.parent.EcritLog(texte)
        self.Update_gauge()

    def SetGauge(self, num=None):
        self.num_etape = num
        self.Update_gauge()

    def Update_gauge(self):
        keepGoing, skip = self.dlgprogress.Update(self.num_etape, self.texte_etape)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    #app.MainLoop()
