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
import wx.propgrid as wxpg
import copy
import random
import time
import codecs
import os.path
import webbrowser

from Dlg import DLG_Message_html

from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
from Ctrl import CTRL_Portail_messages

from Utils import UTILS_Parametres
from Utils import UTILS_Config
from Utils import UTILS_Portail_controle


def GetSecretKey():
    code = ""
    for x in range(0, 40) :
        code += random.choice("abcdefghjkmvwxyz123456789123456789123456789ABCDEFVWXYZ")
    return code

LISTE_THEMES = [("blue", u"Bleu"), ("black", u"Noir"), ("green", u"Vert"), ("purple", u"Violet"), ("red", u"Rouge"), ("yellow", u"Jaune")]
LISTE_DELAIS_SYNCHRO = [(30, u"Toutes les 30 minutes"), (60, u"Toutes les heures"), (120, u"Toutes les 2 heures"), (180, u"Toutes les 3 heures"), (240, u"Toutes les 4 heures"), (300, u"Toutes les 5 heures"), (360, u"Toutes les 6 heures")]
LISTE_AFFICHAGE_HISTORIQUE = [(30, u"1 mois"), (60, u"2 mois"), (90, u"3 mois"), (120, u"4 mois"), (150, u"5 mois"), (180, u"6 mois")]
LISTE_SELECTION_FACTURES = [(0, u"Toutes les factures"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]
LISTE_SELECTION_REGLEMENTS = [(0, u"Tous les règlements"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]


VALEURS_DEFAUT = {
    "portail_activation" : False,
    "client_synchro_portail_activation" : False,
    "client_synchro_portail_delai" : 1,
    "client_synchro_portail_ouverture" : False,
    "client_rechercher_updates" : True,
    "serveur_type": 0,
    "serveur_options": "",
    "serveur_cgi_file": "connecthys.cgi",
    "hebergement_type" : 0,
    "ftp_serveur" : "127.0.0.1",
    "ftp_utilisateur" : "",
    "ftp_mdp" : "",
    "ftp_repertoire" : "/www/connecthys",
    "url_connecthys" : "http://127.0.0.1:5000",
    "accept_all_cert" : False,
    "hebergement_local_repertoire" : "",
    "ssh_serveur" : "127.0.0.1",
    "ssh_port" : "22",
    "ssh_key_file" : "",
    "ssh_utilisateur" : "",
    "ssh_mdp" : "",
    "ssh_repertoire" : "/tmp/connecthys",
    "db_type" : 1,
    "db_serveur" : "",
    "db_utilisateur" : "",
    "db_mdp" : "",
    "db_nom" : "",
    "prefixe_tables" : "",
    "stats_utilisateur": "",
    "stats_mdp": "",
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
    "accueil_bienvenue" : _(u"Bienvenue sur le portail Famille"),
    "accueil_messages_afficher" : True,
    "accueil_etat_dossier_afficher" : True,
    "activites_afficher" : True,
    "activites_intro" : _(u"Vous pouvez consulter ici la liste des inscriptions et demander des inscriptions à d'autres activités."),
    "activites_autoriser_inscription" : True,
    "reservations_afficher" : True,
    "reservations_intro" : _(u"Sélectionnez une activité puis cliquez sur une des périodes disponibles pour accéder au calendrier des réservations correspondant."),
    "planning_intro" : _(u"Cliquez dans les cases pour ajouter ou supprimer des consommations avant de valider l'envoi des données."),
    "factures_afficher" : True,
    "factures_intro" : _(u"Vous pouvez consulter ici la liste des factures et demander des duplicatas."),
    "factures_selection" : 0,
    "factures_demande_facture" : True,
    "reglements_afficher" : True,
    "reglements_intro" : _(u"Vous pouvez consulter ici la liste des règlements et demander des reçus."),
    "reglements_selection" : 0,
    "reglements_demande_recu" : True,
    "pieces_afficher" : True,
    "pieces_intro" : _(u"Vous pouvez consulter ici la liste des pièces à fournir."),
    "pieces_autoriser_telechargement" : True,
    "cotisations_afficher" : True,
    "cotisations_intro" : _(u"Vous pouvez consulter ici la liste des cotisations à fournir."),
    "historique_afficher" : True,
    "historique_intro" : _(u"Vous pouvez consulter ici l'historique de vos demandes."),
    "historique_delai" : 0,
    "contact_afficher" : True,
    "contact_intro" : _(u""),
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
        self.Switch()
        event.Skip()

    def Switch(self):
        dict_switch = {
            "hebergement_type" : {
                # Local
                0 : [
                    {"propriete" : "hebergement_local_repertoire", "obligatoire" : True},
                    ],
                # FTP
                1 : [
                    {"propriete" : "ftp_serveur", "obligatoire" : True},
                    {"propriete" : "ftp_utilisateur", "obligatoire" : True},
                    {"propriete" : "ftp_mdp", "obligatoire" : True},
                    {"propriete" : "ftp_repertoire", "obligatoire" : False},
                    ],
                #SFTP/SSH
                2 : [
                    {"propriete" : "ssh_serveur", "obligatoire" : True},
                    {"propriete" : "ssh_port", "obligatoire" : True},
                    {"propriete" : "ssh_utilisateur", "obligatoire" : True},
                    {"propriete" : "ssh_mdp", "obligatoire" : True},
                    {"propriete" : "ssh_key_file", "obligatoire" : False},
                    {"propriete" : "ssh_repertoire", "obligatoire" : False},
                    ]
                 },

            "db_type" : {
                # SQLITE
                0 : [
                    ],
                # MYSQL
                1 : [
                    {"propriete" : "db_serveur", "obligatoire" : True},
                    {"propriete" : "db_utilisateur", "obligatoire" : True},
                    {"propriete" : "db_mdp", "obligatoire" : True},
                    {"propriete" : "db_nom", "obligatoire" : True},
                    ],
                 },

            "serveur_type" : {
                # Serveur autonome
                0 : [
                    {"propriete" : "serveur_options", "obligatoire" : False},
                    ],
                # CGI
                1 : [
                    {"propriete" : "serveur_cgi_file", "obligatoire" : True},
                    ],
                # WSGI
                2 : [
                    ]
                 },

            }

        for nom_property, dict_conditions in dict_switch.iteritems() :
            propriete = self.GetProperty(nom_property)
            valeur = propriete.GetValue()
            for condition, liste_proprietes in dict_conditions.iteritems() :
                for dict_propriete in liste_proprietes :
                    propriete = self.GetPropertyByName(dict_propriete["propriete"])
                    if valeur == condition :
                        propriete.Hide(False)
                        propriete.SetAttribute("obligatoire", dict_propriete["obligatoire"])
                    else :
                        propriete.Hide(True)
                        propriete.SetAttribute("obligatoire", False)

        self.RefreshGrid()

    def Remplissage(self):

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Activation")) )

        # Activation de la gestion du serveur Connecthys
        nom = "portail_activation"
        propriete = wxpg.BoolProperty(label=_(u"Activer Connecthys"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer Connecthys pour ce fichier"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Type de serveur
        nom = "serveur_type"
        propriete = wxpg.EnumProperty(label=_(u"Type de serveur"), labels=[_(u"Autonome"), _(u"CGI"), _(u"WSGI")], values=[0, 1, 2], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez le type de serveur utilisé : Autonome, CGI ou WSGI"))
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

        # Rechercher des mises à jour
        nom = "client_rechercher_updates"
        propriete = wxpg.BoolProperty(label=_(u"Mises à jour automatiques"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour laisser Connecthys rechercher et appliquer ses propres mises à jour logicielles automatiquement"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Hébergement du portail")) )

        # Type d'hébergement
        nom = "hebergement_type"
        propriete = wxpg.EnumProperty(label=_(u"Type d'hébergement"), labels=[_(u"Local"), _(u"FTP"), _(u"SSH/SFTP")], values=[0, 1, 2], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez le type d'hébergement à utiliser :\nLocal (Connecthys est installé sur l'ordinateur)\nFTP (Connecthys est envoyé sur un répertoire via FTP)\nSSH/SFTP (Connecthys est envoyé sur un répertoire via SSH/SFTP)"))
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

        # Serveur SSH
        nom = "ssh_serveur"
        propriete = wxpg.StringProperty(label=_(u"Adresse du serveur SSH"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'adresse IP du serveur SSH ou son hostname complet (Ex : 192.168.1.15 ou machine.domaine.tld)"))
        self.Append(propriete)

        # Port SSH
        nom = "ssh_port"
        propriete = wxpg.StringProperty(label=_(u"Port du serveur SSH"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le numéro de port SSH (22 par défaut)"))
        self.Append(propriete)

        # SSH key file
        nom = "ssh_key_file"
        propriete = wxpg.StringProperty(label=_(u"Fichier de clé"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"[Optionnel] Saisissez le chemin de la clé (ex : ~/.ssh/id_dsa).\nLe serveur SSH doit connaitre la partie publique de la clé."))
        self.Append(propriete)

        # Utilisateur SSH
        nom = "ssh_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'utilisateur SSH\nUtiliser root est très fortement déconseillé, risqué et dangereux"))
        self.Append(propriete)

        # Mot de passe SSH
        nom = "ssh_mdp"
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe de l utilisateur SSH"))
        self.Append(propriete)

        # R<E9>pertoire SSH
        nom = "ssh_repertoire"
        propriete = wxpg.StringProperty(label=_(u"Répertoire"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le répertoire SSH (ex : /tmp/connecthys)"))
        self.Append(propriete)

        # Repertoire Hebergement Local
        nom = "hebergement_local_repertoire"
        standardPath = wx.StandardPaths.Get()
        defaut = os.path.join(standardPath.GetDocumentsDir(), "connecthys")
        propriete = wxpg.StringProperty(label=_(u"Répertoire local"), name=nom, value=defaut)
        propriete.SetHelpString(_(u"Saisissez le répertoire local (Ex : /home/bogucool/connecthys ou C:/Users/Ivan/Documents/Connecthys)"))
        self.Append(propriete)

        # Url Connecthys
        nom = "url_connecthys"
        propriete = wxpg.StringProperty(label=_(u"URL d'accès à Connecthys "), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'url d'accès à Connecthys (ex : http://127.0.0.1:5000 ou http://www.monsite.com/connecthys)"))
        self.Append(propriete)

        # Accepter tous les certificat en cas d acces par https
        nom = "accept_all_cert"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser tous les certificats"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Autoriser les certificats SSL auto-signés ou les certificats posant problème.\nA utiliser uniquement si vous accédez à Connecthys en https://\nSans effet sinon."))
        propriete.SetAttribute("UseCheckbox", True)
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
        propriete = wxpg.StringProperty(label=_(u"Préfixe des tables"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"[Optionnel] Saisissez un préfixe pour les tables"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Statistiques")) )

        # Utilisateur
        nom = "stats_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le nom d'utilisateur pour accéder aux statistiques [Uniquement pour les abonnés à Connecthys Easy]"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Mot de passe
        nom = "stats_mdp"
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe pour accéder aux statistiques [Uniquement pour les abonnés à Connecthys Easy]"))
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
        propriete = wxpg.BoolProperty(label=_(u"Activer le paiement en ligne (Non fonctionnel)"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer la fonction de paiement en ligne"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Accueil'")) )

        # Texte de bienvenue
        nom = "accueil_bienvenue"
        propriete = wxpg.LongStringProperty(label=_(u"Texte de bienvenue"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte de bienvenue"))
        self.Append(propriete)

        nom = "accueil_messages_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher les messages"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les messages sur la page d'accueil"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        nom = "accueil_etat_dossier_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher l'état du dossier"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher l'état du dossier sur la page d'accueil"))
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

        # Intro de la page activités
        nom = "activites_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
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

        # Intro de la page réservations
        nom = "reservations_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # Intro de la page planning
        nom = "planning_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction du calendrier"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction pour le calendrier"))
        self.Append(propriete)

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Factures'")) )

        # Afficher
        nom = "factures_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page factures
        nom = "factures_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
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

        # Intro de la page règlements
        nom = "reglements_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
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

        # Intro de la page pièces
        nom = "pieces_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
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

        # Intro de la page cotisations
        nom = "cotisations_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)


        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Historique'")) )

        # Afficher
        nom = "historique_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page historique
        nom = "historique_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
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

        # Intro de la page contact
        nom = "contact_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # Afficher la carte
        # nom = "contact_carte_afficher"
        # propriete = wxpg.BoolProperty(label=_(u"Afficher la carte Google Maps"), name=nom, value=VALEURS_DEFAUT[nom])
        # propriete.SetHelpString(_(u"Cochez cette case pour afficher la carte Google Maps"))
        # propriete.SetAttribute("UseCheckbox", True)
        # self.Append(propriete)


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
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % self.GetPropertyLabel(nom), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
        dictParametres["client_rechercher_updates"] = UTILS_Config.GetParametre("client_rechercher_updates", True)
        dictParametres["hebergement_type"] = UTILS_Config.GetParametre("hebergement_type", 0)
        dictParametres["serveur_type"] = UTILS_Config.GetParametre("serveur_type", 0)

        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            propriete.SetValue(valeur)

        # MAJ affichage grille
        self.Switch()

    def Sauvegarde(self):
        """ Mémorisation des valeurs du contrôle """
        # Mémorisation des paramètres dans la base de données
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="portail", dictParametres=dictValeurs)

        # Mémorisation de la config sur cet ordi
        for key in ("client_synchro_portail_activation", "client_synchro_portail_delai", "client_synchro_portail_ouverture", "client_rechercher_updates", "hebergement_type", "serveur_type") :
            UTILS_Config.SetParametre(key, self.GetPropertyByName(key).GetValue())

    def GetValeurs(self) :
        return self.GetPropertyValues()

    def OnPropChange(self, event):
        prop = event.GetProperty()
        pass

    def Importation_config(self, event=None):
        # Demande l'emplacement du fichier
        wildcard = u"Fichier de configuration (*.cfg)|*.cfg|Tous les fichiers (*.*)|*.*"
        standardPath = wx.StandardPaths.Get()
        rep = standardPath.GetDocumentsDir()
        dlg = wx.FileDialog(None, message=_(u"Veuillez sélectionner le fichier de configuration à restaurer"), defaultDir=rep, defaultFile="", wildcard=wildcard, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Lecture du fichier
        fichier = codecs.open(cheminFichier, encoding='utf-8', mode='r')
        liste_lignes = fichier.readlines()
        fichier.close()

        for ligne in liste_lignes :
            if len(ligne) > 0 :
                ligne = ligne.replace("\n", "")
                ligne = ligne.replace("#!#", "\n")
                if len(ligne.split(" = ")) == 2 :
                    cle, valeur = ligne.split(" = ")
                    propriete = self.GetPropertyByName(cle)
                    if propriete != None :
                        type_propriete = type(VALEURS_DEFAUT[cle])
                        if type_propriete in (str, unicode) :
                            valeur = unicode(valeur)
                        if type_propriete == bool :
                            if valeur == "True" :
                                valeur = True
                            else :
                                valeur = False
                        if type_propriete == int :
                            valeur = int(valeur)
                        propriete.SetValue(valeur)

        # MAJ affichage grille
        self.Switch()

        dlg = wx.MessageDialog(None, _(u"Importation de la configuration effectuée."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def Exportation_config(self, event=None):
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "Config_connecthys.cfg"
        wildcard = u"Fichier de configuration (*.cfg)|*.cfg|Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy()
                return False
            else:
                dlg.Destroy()

        # Création du fichier
        fichier = codecs.open(cheminFichier, encoding='utf-8', mode='w')
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        for cle, valeur in dictValeurs.iteritems() :
            if type(valeur) in (str, unicode) :
                valeur = valeur.replace("\n", "#!#")
            ligne = u"%s = %s\n" % (cle, valeur)
            fichier.write(ligne)
        fichier.close()


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

        # Messages
        self.box_messages = wx.StaticBox(self, -1, _(u"Messages"))
        self.ctrl_messages = CTRL_Portail_messages.CTRL(self)
        self.ctrl_messages.SetMinSize((230, -1))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_easy = CTRL_Bouton_image.CTRL(self, texte=_(u"Souscrire à Connecthys Easy"), cheminImage="Images/32x32/Connecthys.png")
        self.bouton_site = CTRL_Bouton_image.CTRL(self, texte=_(u"www.connecthys.com"), cheminImage="Images/32x32/Connecthys.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEasy, self.bouton_easy)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSite, self.bouton_site)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Inits
        self.server_ctrl = None

        # Affichage avertissement
        wx.CallAfter(self.Afficher_avertissement)

    def __set_properties(self):
        self.bouton_easy.SetToolTipString(_(u"Cliquez ici pour souscrire à l'offre Connecthys Easy"))
        self.bouton_site.SetToolTipString(_(u"Cliquez ici pour accéder au site internet www.connecthys.com"))
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour accéder aux outils"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Log
        staticbox_actions = wx.StaticBoxSizer(self.box_log, wx.VERTICAL)
        grid_sizer_actions = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_actions.Add(self.log, 1, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.gauge, 0, wx.EXPAND, 0)
        staticbox_actions.Add(grid_sizer_actions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_actions, 1, wx.EXPAND, 0)

        # Messages
        staticbox_messages = wx.StaticBoxSizer(self.box_messages, wx.VERTICAL)
        staticbox_messages.Add(self.ctrl_messages, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_messages, 1, wx.EXPAND, 0)

        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_easy, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_site, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
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

    def OnBoutonEasy(self, event):
        from Dlg import DLG_Financement
        dlg = DLG_Financement.Dialog(None, code="connecthys")
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonSite(self, event):
        webbrowser.open("https://www.connecthys.com")

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        dict_parametres = self.ctrl_parametres.GetValeurs()

        menu = wx.Menu()

        server_is_running = False
        if dict_parametres["serveur_type"] == 0:
            if self.server_ctrl != None :
                server_is_running = self.server_ctrl.GetServerStatus()
            else :
                if self.ctrl_parametres.Validation() == True :
                    self.server_ctrl = UTILS_Portail_controle.ServeurConnecthys(self)
                    server_is_running = self.server_ctrl.GetServerStatus()


        # Installer
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Installer"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Installer, id=id)

        # Mettre à jour
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Mettre à jour"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Update, id=id)

        # Upgrade DB
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Forcer l'upgrade de la base de données"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Database.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.DemandeUpgradeDB, id=id)

        menu.AppendSeparator()

        # AutoReload WSGI
        if dict_parametres["serveur_type"] == 2 :
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"AutoReload WSGI"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.AutoReloadWSGI, id=id)

        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Consulter le log du portail"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Log.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.LireJournal, id=id)

        menu.AppendSeparator()

        # Importer config
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Importer la configuration"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_import.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_parametres.Importation_config, id=id)

        # Exporter config
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Exporter la configuration"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_export.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_parametres.Exportation_config, id=id)

        menu.AppendSeparator()

        if dict_parametres["serveur_type"] == 0:

            # Démarrer
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"Démarrer le serveur"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Play.png"), wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.server_ctrl.Demarrer_serveur, id=id)
            if dict_parametres["hebergement_type"] == 0 and dict_parametres["serveur_type"] == 0 :
                if server_is_running == True :
                    item.Enable(False)
            elif dict_parametres["hebergement_type"] == 2 and dict_parametres["serveur_type"] == 0 :
                if server_is_running == True :
                    item.Enable(False)
            else :
                item.Enable(False)

            # Arrêter
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"Arrêter le serveur"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Stop.png"), wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.server_ctrl.Arreter_serveur, id=id)
            if dict_parametres["hebergement_type"] == 0 and dict_parametres["serveur_type"] == 0 :
                if server_is_running == False :
                    item.Enable(False)
            elif dict_parametres["hebergement_type"] == 2 and dict_parametres["serveur_type"] == 0 :
                if server_is_running == False :
                    item.Enable(False)
            else :
                item.Enable(False)

            menu.AppendSeparator()

        # Synchroniser
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Synchroniser les données"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Synchroniser, id=id)

        # Synchronisation complète
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Forcer la synchronisation complète"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Synchroniser_full, id=id)

        menu.AppendSeparator()

        # Traiter les données
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Traiter les demandes"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Traiter, id=id)

        menu.AppendSeparator()

        # Ouvrir Connecthys
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Afficher Connecthys dans le navigateur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Planete.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirNavigateur, id=id)

        # Ouvrir les stats de Connecthys Easy
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Afficher les statistiques dans le navigateur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/barres.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirStats, id=id)

        self.PopupMenu(menu)
        menu.Destroy()

    def Installer(self, event):
        # Récupération des paramètres de l'installation
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        server_ctrl = self.server_ctrl

        if dict_parametres["hebergement_type"] == 1 :

            if dict_parametres["ftp_serveur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'adresse du serveur FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ftp_utilisateur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nom de de l'utilisateur FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
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

        elif dict_parametres["hebergement_type"] == 2 :

            if dict_parametres["ssh_serveur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'adresse du serveur SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_port"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le numéro de port du serveur SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_utilisateur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nom de de l'utilisateur SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_mdp"] == "" and dict_parametres["ssh_key_file"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le mot de passe de l utilisateur SSH ou utiliser une connection par clé !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_repertoire"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le répertoire SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
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
        install = UTILS_Portail_installation.Installer(self, dict_parametres, server_ctrl)
        resultat = install.Installer()

    def Update(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.Update()

    def AutoReloadWSGI(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.AutoReloadWSGI()

    def LireJournal(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        self.EcritLog(_(u"Téléchargement du log..."))
        synchro = Synchro(self, dict_parametres)
        contenu_fichier = synchro.ConnectEtTelechargeFichier("debug.log")
        if contenu_fichier == False :
            self.EcritLog(_(u"Le log n'a pas pu être téléchargé."))
            return False

        from Dlg import DLG_Editeur_texte
        dlg = DLG_Editeur_texte.Dialog(self, texte=contenu_fichier)
        dlg.ShowModal()
        dlg.Destroy()

    def DemandeUpgradeDB(self, event):
        if self.ctrl_parametres.Validation() == False:
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        self.EcritLog(_(u"Demande d'upgrade de la base de données..."))
        synchro = Synchro(self, dict_parametres)
        if synchro.Upgrade_application() == True :
            self.EcritLog(_(u"Upgrade effectué."))

    def OuvrirNavigateur(self, event):
        dict_parametres = self.ctrl_parametres.GetValeurs()
        url = dict_parametres["url_connecthys"]
        if url == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner l'URL d'accès à Connecthys !"), _(u"Accès impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if dict_parametres["serveur_type"] == 1 :
            url += "/" + dict_parametres["serveur_cgi_file"] + "/"

        self.EcritLog(_(u"Ouverture dans le navigateur de l'url %s") % url)
        import webbrowser
        webbrowser.open(url)

    def OuvrirStats(self, event):
        dict_parametres = self.ctrl_parametres.GetValeurs()
        url = dict_parametres["url_connecthys"]
        if url == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner l'URL d'accès à Connecthys !"), _(u"Accès impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        stats_utilisateur = dict_parametres["stats_utilisateur"]
        if stats_utilisateur == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner le nom d'utilisateur de la rubrique Statistiques !\n\nAttention, cette fonctionnalité n'est disponible que pour les abonnés Connecthys Easy."), _(u"Accès impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        stats_mdp = dict_parametres["stats_mdp"]
        if stats_mdp == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner le mot de passe de la rubrique Statistiques !\n\nAttention, cette fonctionnalité n'est disponible que pour les abonnés Connecthys Easy."), _(u"Accès impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        url += "/stats/"

        # Mémorisation du mot de passe stats dans le presse-papiers
        clipdata = wx.TextDataObject()
        clipdata.SetText(stats_mdp)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        # Affiche une fenêtre avec les codes
        texte = u"""
        <CENTER><IMG SRC="%s">
        <FONT SIZE=3>
        <BR>
        <B>Accès aux statistiques Connecthys Easy</B>
        <BR><BR>
        Noethys va ouvrir votre navigateur internet pour vous permettre d'accéder aux statistiques Connecthys Easy.
        <BR><BR>
        Les codes d'accès suivants vont vous être demandés :
        <BR><BR>
        <B>
        <UL>
            <LI>Nom d'utilisateur : %s</LI>
            <LI>Mot de passe : %s</LI>
        </UL>
        </B>
        <BR><BR>
        Remarque : Le mot de passe a été copié dans le presse-papiers. Vous pouvez donc utiliser <B>CTRL+V</B> pour le coller dans le champ de saisie.
        </FONT>
        </CENTER>
        """ % (Chemins.GetStaticPath("Images/32x32/Connecthys.png"), stats_utilisateur, stats_mdp)
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Statistiques"), nePlusAfficher=False, size=(200, 380))
        dlg.ShowModal()
        dlg.Destroy()

        self.EcritLog(_(u"Ouverture dans le navigateur de l'url %s") % url)
        import webbrowser
        webbrowser.open(url)

    def Synchroniser(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.Start()

    def Synchroniser_full(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        dict_parametres = self.ctrl_parametres.GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.Start(full_synchro=True)

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
Il facilite également la gestion administrative par les utilisateurs grâce à son
traitement semi-automatisé des demandes.
<BR><BR>
Si vous souhaitez en savoir davantage, vous pouvez consulter le site dédié
<FONT SIZE=5><A HREF="http://www.connecthys.com">www.connecthys.com</A></FONT>.
</FONT>
</CENTER>
""" % Chemins.GetStaticPath("Images/Special/Connecthys_pub.png")

        from Dlg import DLG_Message_html
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), size=(510, 650), nePlusAfficher=True)
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

    def Update(self):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)
        synchro.Update_application()

    def AutoReloadWSGI(self):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)
        synchro.AutoReloadWSGI()

    def Upgrade_application(self):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)
        synchro.Upgrade_application()

    def ConnectEtTelechargeFichier(self, nomFichier="", repFichier=None):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)
        return synchro.ConnectEtTelechargeFichier(nomFichier=nomFichier, repFichier=repFichier)

    def Start(self, full_synchro=False):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)

        # Ouverture de la dlg de progress
        self.dlgprogress = wx.ProgressDialog(_(u"Synchronisation en cours - Veuillez patienter..."), _(u"Lancement de la synchronisation..."), maximum=100, parent=None, style= wx.PD_SMOOTH | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)

        # Lancement de la synchro
        synchro.Synchro_totale(full_synchro=full_synchro)

        self.dlgprogress.Destroy()

    def EcritLog(self, texte=""):
        self.texte_etape = texte
        self.parent.EcritLog(texte)
        self.Update_gauge()

    def SetGauge(self, num=None):
        self.num_etape = num
        self.Update_gauge()

    def Update_gauge(self):
        try :
            keepGoing, skip = self.dlgprogress.Update(self.num_etape, self.texte_etape)
        except :
            pass


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    #app.MainLoop()
