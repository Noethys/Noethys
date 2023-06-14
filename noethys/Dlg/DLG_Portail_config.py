#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.propgrid as wxpg
import copy
import random
import time
import datetime
import codecs
import os.path
import webbrowser
import GestionDB
import wx.richtext as rt
import six

from Dlg import DLG_Message_html

from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
from Ctrl import CTRL_Portail_messages
from Ctrl import CTRL_Portail_pages

from Utils import UTILS_Parametres
from Utils import UTILS_Config
from Utils import UTILS_Portail_controle


def GetSecretKey():
    code = ""
    for x in range(0, 40) :
        code += random.choice("abcdefghjkmvwxyz123456789123456789123456789ABCDEFVWXYZ")
    return code

LISTE_THEMES = [("blue", u"Bleu"), ("black", u"Noir"), ("green", u"Vert"), ("purple", u"Violet"), ("red", u"Rouge"), ("yellow", u"Jaune")]
LISTE_DELAIS_SYNCHRO = [(60, u"Toutes les heures"), (120, u"Toutes les 2 heures"), (180, u"Toutes les 3 heures"), (240, u"Toutes les 4 heures"), (300, u"Toutes les 5 heures"), (360, u"Toutes les 6 heures"), (420, u"Toutes les 7 heures")]
LISTE_AFFICHAGE_HISTORIQUE = [(30, u"1 mois"), (60, u"2 mois"), (90, u"3 mois"), (120, u"4 mois"), (150, u"5 mois"), (180, u"6 mois")]
LISTE_SELECTION_FACTURES = [(0, u"Toutes les factures"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]
LISTE_SELECTION_REGLEMENTS = [(0, u"Tous les r�glements"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]
LISTE_SELECTION_COTISATIONS = [(0, u"Toutes les cotisations"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]
LISTE_SELECTION_RENSEIGNEMENTS = [("masquer", u"Ne pas afficher"), ("consultation", u"Consultation uniquement"), ("modification", u"Consultation et modification autoris�es")]
LISTE_SELECTION_LOCATIONS = [(0, u"Toutes les locations"), (3, u"Datant de moins de 3 mois"), (6, u"Datant de moins de 6 mois"), (12, u"Datant de moins de 1 an"), (24, u"Datant de moins de 2 ans"), (36, u"Datant de moins de 3 ans"), (60, u"Datant de moins de 5 ans")]
LISTE_SAISIE_LOCATIONS = [(0, u"Jamais"), (2, u"2 mois avant"), (3, u"3 mois avant"), (4, u"4 mois avant"), (5, u"5 mois avant"),(6, u"6 mois avant"), (12, u"1 an avant"), (24, u"2 ans avant"), (36, u"3 ans avant"), (60, u"5 ans avant")]
HEURES = [("%02d:00" % x, "%02d:00" % x) for x in range(0, 25)]


VALEURS_DEFAUT = {
    "portail_activation" : False,
    "client_synchro_portail_activation" : False,
    "client_synchro_portail_delai" : 2,
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
    "db_type" : 0,
    "db_serveur" : "",
    "db_utilisateur" : "",
    "db_mdp" : "",
    "db_nom" : "",
    "prefixe_tables" : "",
    "stats_utilisateur": "",
    "stats_mdp": "",
    "secret_key" : GetSecretKey(),
    "mode_debug" : False,
    "talisman": True,
    "captcha": 1,
    "crypter_transferts" : True,
    "image_identification" : "",
    "theme" : 0,
    "cadre_logo" : 0,
    "recevoir_document_email" : True,
    "recevoir_document_courrier" : True,
    "recevoir_document_site" : True,
    "recevoir_document_site_lieu" : _(u"� l'accueil de la structure"),
    "mdp_forcer_modification": True,
    "mdp_autoriser_modification": True,
    "mdp_autoriser_reinitialisation": False,
    "email_type_adresse" : 0,
    "email_serveur": "",
    "email_adresse": "",
    "email_port": "",
    "email_tls": False,
    "email_ssl": False,
    "email_utilisateur": "",
    "email_password": "",
    "paiement_ligne_actif" : False,
    "paiement_ligne_systeme" : 0,
    "paiement_ligne_mode_reglement" : 0,
    "paiement_ligne_tipi_saisie" : 0,
    "paiement_ligne_multi_factures" : False,
    "paiement_ligne_montant_minimal" : 0.0,
    "payzen_site_id" : "",
    "payzen_mode" : "TEST",
    "payzen_certificat_test" : "",
    "payzen_certificat_production" : "",
    "payzen_echelonnement" : False,
    "paiement_off_si_prelevement": False,
    "accueil_titre" : u"Le <strong>Portail</strong> Famille",
    "accueil_bienvenue" : _(u"Bienvenue sur le portail Famille"),
    "accueil_messages_afficher" : True,
    "accueil_etat_dossier_afficher" : True,
    "renseignements_afficher": True,
    "renseignements_intro": _(u"Vous pouvez consulter et modifier ici les renseignements sur votre famille."),
    "renseignements_modifier": True,
    "renseignements_adulte_nom": "modification",
    "renseignements_enfant_nom": "modification",
    "renseignements_adulte_naissance": "modification",
    "renseignements_enfant_naissance": "modification",
    "renseignements_adresse": "modification",
    "renseignements_adulte_coords": "modification",
    "renseignements_enfant_coords": "modification",
    "renseignements_adulte_profession": "modification",
    "activites_afficher" : True,
    "activites_intro" : _(u"Vous pouvez consulter ici la liste des inscriptions et demander des inscriptions � d'autres activit�s."),
    "activites_autoriser_inscription" : True,
    "activites_bloquer_complet" : True,
    "reservations_afficher" : True,
    "reservations_intro" : _(u"S�lectionnez une activit� puis cliquez sur une des p�riodes disponibles pour acc�der au calendrier des r�servations correspondant."),
    "planning_intro" : _(u"Cliquez dans les cases pour ajouter ou supprimer des consommations avant de valider l'envoi des donn�es."),
    "factures_afficher" : True,
    "factures_intro" : _(u"Vous pouvez consulter ici la liste des factures et demander des duplicatas."),
    "factures_selection" : 0,
    "factures_demande_facture" : True,
    "factures_prefacturation" : True,
    "factures_afficher_solde_total" : True,
    "factures_afficher_solde_detail" : True,
    "factures_afficher_solde_famille" : False,
    "reglements_afficher" : True,
    "reglements_intro" : _(u"Vous pouvez consulter ici la liste des r�glements et demander des re�us."),
    "reglements_selection" : 0,
    "reglements_demande_recu" : True,
    "pieces_afficher" : True,
    "pieces_intro" : _(u"Vous pouvez consulter ici la liste des pi�ces � fournir."),
    "pieces_autoriser_telechargement" : True,
    "pieces_autoriser_upload" : False,
    "cotisations_afficher" : True,
    "cotisations_intro" : _(u"Vous pouvez consulter ici la liste des cotisations."),
    "cotisations_selection" : 0,
    "locations_afficher": False,
    "locations_intro": _(u"Vous pouvez consulter ici la liste des locations et emprunts."),
    "locations_selection": 3,
    "locations_periode_saisie": 6,
    "planning_locations_intro" : _(u"Saisissez des r�servations avec la souris directement dans le calendrier avant de valider l'envoi des demandes."),
    "locations_heure_min": "00:00",
    "locations_heure_max": "24:00",
    "locations_afficher_autres_loueurs": False,
    "historique_afficher" : True,
    "historique_intro" : _(u"Vous pouvez consulter ici l'historique de vos demandes."),
    "historique_delai" : 0,
    "contact_afficher" : True,
    "contact_intro" : _(u""),
    "contact_carte_afficher" : True,
    "mentions_afficher" : True,
    "aide_afficher" : True,
    }


def GetDefaut(nom="", defaut=None):
    if nom in VALEURS_DEFAUT :
        return VALEURS_DEFAUT[nom]
    else :
        return defaut





class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)
        self.parent = parent
        self.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    def OnPropGridChange(self, event):
        self.Switch()
        event.Skip()

    def Switch(self):
        liste_conditions = [
            ("hebergement_local_repertoire", "p('hebergement_type') == 0"),
            ("ftp_serveur", "p('hebergement_type') == 1"),
            ("ftp_utilisateur", "p('hebergement_type') == 1"),
            ("ftp_mdp", "p('hebergement_type') == 1"),
            ("ftp_repertoire", "p('hebergement_type') == 1"),
            ("ssh_serveur", "p('hebergement_type') == 2"),
            ("ssh_port", "p('hebergement_type') == 2"),
            ("ssh_utilisateur", "p('hebergement_type') == 2"),
            ("ssh_mdp", "p('hebergement_type') == 2"),
            ("ssh_key_file", "p('hebergement_type') == 2"),
            ("ssh_repertoire", "p('hebergement_type') == 2"),

            ("db_serveur", "p('db_type') == 1"),
            ("db_utilisateur", "p('db_type') == 1"),
            ("db_mdp", "p('db_type') == 1"),
            ("db_nom", "p('db_type') == 1"),

            ("serveur_options", "p('serveur_type') == 0"),
            ("serveur_cgi_file", "p('serveur_type') == 1"),

            ("paiement_ligne_systeme", "p('paiement_ligne_actif') == True"),
            ("paiement_ligne_mode_reglement", "p('paiement_ligne_actif') == True"),
            ("paiement_ligne_multi_factures", "p('paiement_ligne_actif') == True"),
            ("paiement_ligne_montant_minimal", "p('paiement_ligne_actif') == True"),
            ("paiement_off_si_prelevement", "p('paiement_ligne_actif') == True"),

            ("payzen_site_id", "p('paiement_ligne_systeme') == 3"),
            ("payzen_mode", "p('paiement_ligne_systeme') == 3"),
            ("payzen_certificat_test", "p('paiement_ligne_systeme') == 3"),
            ("payzen_certificat_production", "p('paiement_ligne_systeme') == 3"),
            ("payzen_echelonnement", "p('paiement_ligne_systeme') == 3"),

            ("paiement_ligne_tipi_saisie", "p('paiement_ligne_systeme') == 1"),
        ]

        # V�rifie les conditions d'affichage des propri�t�s d'affichage
        def p(nom=''):
            propriete = self.GetProperty(nom)
            valeur = propriete.GetValue()
            return valeur

        for nom, condition in liste_conditions:
            propriete = self.GetProperty(nom)
            if eval(condition) == True :
                propriete.Hide(False)
                propriete.SetAttribute("obligatoire", self.GetPropertyAttribute(propriete, "obligatoire"))
            else:
                propriete.Hide(True)
                propriete.SetAttribute("obligatoire", False)

        # email_type_adresse
        propriete = self.GetPropertyByName("email_type_adresse")
        if propriete.GetValue() == 999 :
            visible, obligatoire = True, True
        else :
            visible, obligatoire = False, False
        for nom in ["email_serveur", "email_adresse", "email_port", "email_tls", "email_ssl", "email_utilisateur", "email_password"] :
            propriete = self.GetPropertyByName(nom)
            propriete.Hide(not visible)
            propriete.SetAttribute("obligatoire", obligatoire)

        # MAJ affichage
        if 'phoenix' in wx.PlatformInfo:
            self.Refresh()
        else :
            self.RefreshGrid()

    def Remplissage(self):
        # Cat�gorie
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
        propriete.SetHelpString(_(u"S�lectionnez le type de serveur utilis� : Autonome, CGI ou WSGI"))
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

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Client de synchronisation")) )

        # Activation du client de synchronisation
        nom = "client_synchro_portail_activation"
        propriete = wxpg.BoolProperty(label=_(u"Activer sur cet ordinateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer le client de synchronisation sur la page d'accueil de Noethys sur cet ordinateur"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # D�lai de synchronisation du client
        nom = "client_synchro_portail_delai"
        propriete = wxpg.EnumProperty(label=_(u"D�lai de synchronisation"), labels=[y for x, y in LISTE_DELAIS_SYNCHRO], values=range(0, len(LISTE_DELAIS_SYNCHRO)), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un d�lai pour la synchronisation"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Synchroniser � l'ouverture de Noethys
        nom = "client_synchro_portail_ouverture"
        propriete = wxpg.BoolProperty(label=_(u"Synchroniser � l'ouverture"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour synchroniser automatiquement � l'ouverture de Noethys sur cet ordinateur"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Rechercher des mises � jour
        nom = "client_rechercher_updates"
        propriete = wxpg.BoolProperty(label=_(u"Mises � jour automatiques"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour laisser Connecthys rechercher et appliquer ses propres mises � jour logicielles automatiquement"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"H�bergement du portail")) )

        # Type d'h�bergement
        nom = "hebergement_type"
        propriete = wxpg.EnumProperty(label=_(u"Type d'h�bergement"), labels=[_(u"Local"), _(u"FTP"), _(u"SSH/SFTP")], values=[0, 1, 2], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez le type d'h�bergement � utiliser :\nLocal (Connecthys est install� sur l'ordinateur)\nFTP (Connecthys est envoy� sur un r�pertoire via FTP)\nSSH/SFTP (Connecthys est envoy� sur un r�pertoire via SSH/SFTP)"))
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
        propriete.SetAttribute("Password", True)

        # R�pertoire FTP
        nom = "ftp_repertoire"
        propriete = wxpg.StringProperty(label=_(u"R�pertoire"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le r�pertoire FTP (ex : www/connecthys)"))
        self.Append(propriete)

        # Serveur SSH
        nom = "ssh_serveur"
        propriete = wxpg.StringProperty(label=_(u"Adresse du serveur SSH"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'adresse IP du serveur SSH ou son hostname complet (Ex : 192.168.1.15 ou machine.domaine.tld)"))
        self.Append(propriete)

        # Port SSH
        nom = "ssh_port"
        propriete = wxpg.StringProperty(label=_(u"Port du serveur SSH"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le num�ro de port SSH (22 par d�faut)"))
        self.Append(propriete)

        # SSH key file
        nom = "ssh_key_file"
        propriete = wxpg.StringProperty(label=_(u"Fichier de cl�"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"[Optionnel] Saisissez le chemin de la cl� (ex : ~/.ssh/id_dsa).\nLe serveur SSH doit connaitre la partie publique de la cl�."))
        self.Append(propriete)

        # Utilisateur SSH
        nom = "ssh_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'utilisateur SSH\nUtiliser root est tr�s fortement d�conseill�, risqu� et dangereux"))
        self.Append(propriete)

        # Mot de passe SSH
        nom = "ssh_mdp"
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe de l utilisateur SSH"))
        self.Append(propriete)
        propriete.SetAttribute("Password", True)

        # R�pertoire SSH
        nom = "ssh_repertoire"
        propriete = wxpg.StringProperty(label=_(u"R�pertoire"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le r�pertoire SSH (ex : /tmp/connecthys)"))
        self.Append(propriete)

        # Repertoire Hebergement Local
        nom = "hebergement_local_repertoire"
        standardPath = wx.StandardPaths.Get()
        defaut = os.path.join(standardPath.GetDocumentsDir(), "connecthys")
        propriete = wxpg.StringProperty(label=_(u"R�pertoire local"), name=nom, value=defaut)
        propriete.SetHelpString(_(u"Saisissez le r�pertoire local (Ex : /home/bogucool/connecthys ou C:/Users/Ivan/Documents/Connecthys)"))
        self.Append(propriete)

        # Url Connecthys
        nom = "url_connecthys"
        propriete = wxpg.StringProperty(label=_(u"URL d'acc�s � Connecthys "), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'url d'acc�s � Connecthys (ex : http://127.0.0.1:5000 ou http://www.monsite.com/connecthys)"))
        self.Append(propriete)

        # Accepter tous les certificat en cas d acces par https
        nom = "accept_all_cert"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser tous les certificats"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Autoriser les certificats SSL auto-sign�s ou les certificats posant probl�me.\nA utiliser uniquement si vous acc�dez � Connecthys en https://\nSans effet sinon."))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Base de donn�es")) )

        # Type base de donn�es
        nom = "db_type"
        propriete = wxpg.EnumProperty(label=_(u"Type de base"), labels=[_(u"Locale (Sqlite)"), _(u"R�seau (MySQL)")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez le type de base de donn�es � utiliser (locale ou r�seau). MySQL est fortement conseill� afin d'�viter les conflits d'�criture en cas d'acc�s simultan�s d'internautes."))
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
        propriete.SetAttribute("Password", True)

        # Nom de la base
        nom = "db_nom"
        propriete = wxpg.StringProperty(label=_(u"Nom de la base"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le nom de la base de donn�es � utiliser"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Pr�fixe des tables
        nom = "prefixe_tables"
        propriete = wxpg.StringProperty(label=_(u"Pr�fixe des tables"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"[Optionnel] Saisissez un pr�fixe pour les tables"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Statistiques")) )

        # Utilisateur
        nom = "stats_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le nom d'utilisateur pour acc�der aux statistiques [Uniquement pour les abonn�s � Connecthys Easy]"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Mot de passe
        nom = "stats_mdp"
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe pour acc�der aux statistiques [Uniquement pour les abonn�s � Connecthys Easy]"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)
        propriete.SetAttribute("Password", True)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"S�curit�")) )

        # Cl� secr�te
        nom = "secret_key"
        propriete = wxpg.StringProperty(label=_(u"Cl� de s�curit�"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une cl� secr�te (g�n�r�e automatiquement par d�faut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Cryptage des transferts
        nom = "crypter_transferts"
        propriete = wxpg.BoolProperty(label=_(u"Crypter les donn�es lors des transferts"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour crypter les donn�es lors des transferts"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Mode debug
        nom = "mode_debug"
        propriete = wxpg.BoolProperty(label=_(u"Mode debug"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer le mode debug (Ne surtout pas utiliser en production !)"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # S�curit� avanc�e
        nom = "talisman"
        propriete = wxpg.BoolProperty(label=_(u"S�curit� avanc�e"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer les param�tres de s�curit� avanc�s"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Captcha
        nom = "captcha"
        # propriete = wxpg.EnumProperty(label=_(u"Captcha"), labels=[_(u"Aucun"), _(u"Captcha par d�faut"), _(u"Google Recaptcha")], values=[0, 1, 2], name=nom, value=VALEURS_DEFAUT[nom])
        propriete = wxpg.EnumProperty(label=_(u"Captcha"), labels=[_(u"Aucun"), _(u"Captcha par d�faut")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Choisissez un captcha pour la page de connexion afin de r�duire l'impact des attaques automatis�es de robots"))
        self.Append(propriete)

        # Gestion des mots de passe
        self.Append( wxpg.PropertyCategory(_(u"Mots de passe")) )

        # Forcer modification mot de passe
        nom = "mdp_forcer_modification"
        propriete = wxpg.BoolProperty(label=_(u"Forcer la modification du mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour obliger l'utilisateur � modifier son mot de passe lors de sa premi�re utilisation du portail"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Autoriser modification mot de passe
        nom = "mdp_autoriser_modification"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser la modification du mot de passe par l'utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour permettre � l'utilisateur de modifier lui-m�me son mot de passe quand il le souhaite"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Autoriser mot de passe oubli�
        nom = "mdp_autoriser_reinitialisation"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser r�initialisation du mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser l'utilisateur � r�initialiser lui-m�me son mot de passe en cas d'oubli"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Adresse d'exp�dition d'emails
        nom = "email_type_adresse"
        labels = [(u"Aucune"), _(u"L'adresse suivante...")]
        valeurs = [0, 999]
        DB = GestionDB.DB()
        req = """SELECT IDadresse, adresse FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDadresse, adresse in listeDonnees :
            labels.insert(len(labels)-1, adresse)
            valeurs.insert(len(valeurs)-1, IDadresse)
        DB.Close()
        propriete = wxpg.EnumProperty(label=_(u"Adresse d'exp�dition d'emails"), labels=labels, values=valeurs, name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez une adresse d'exp�dition d'emails qui sera utilis�e pour envoyer les emails de r�initialisation des mots de passe"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse email : serveur
        nom = "email_serveur"
        propriete = wxpg.StringProperty(label=_(u"Email : Serveur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'adresse du serveur d'emails"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse email : adresse
        nom = "email_adresse"
        propriete = wxpg.StringProperty(label=_(u"Email : Adresse"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'adresse d'exp�dition"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse email : port
        nom = "email_port"
        propriete = wxpg.StringProperty(label=_(u"Email : Port"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le num�ro de port"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse email : TLS
        nom = "email_tls"
        propriete = wxpg.BoolProperty(label=_(u"Email : TLS"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Active le protocole TLS"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Adresse email : SSL
        nom = "email_ssl"
        propriete = wxpg.BoolProperty(label=_(u"Email : SSL"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Active le protocole SSL"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Adresse email : utilisateur
        nom = "email_utilisateur"
        propriete = wxpg.StringProperty(label=_(u"Email : Utilisateur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le nom d'utilisateur (Est souvent identique � l'adresse email)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse email : Mot de passe
        nom = "email_password"
        propriete = wxpg.StringProperty(label=_(u"Email : Mot de passe"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le mot de passe s'il s'agit d'une connexion authentifi�e"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        propriete.SetAttribute("Password", True)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Affichage")) )

        # Image de fond du login
        nom = "image_identification"
        propriete = wxpg.ImageFileProperty(label=_(u"Image de fond de la page d'identification"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez une image pour la page d'identification"))
        self.Append(propriete)

        # Th�me
        nom = "theme"
        propriete = wxpg.EnumProperty(label=_(u"Th�me"), labels=[y for x, y in LISTE_THEMES], values=range(0, len(LISTE_THEMES)), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un th�me pour l'affichage"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Cadre logo organisateur
        nom = "cadre_logo"
        propriete = wxpg.EnumProperty(label=_(u"Cadre du logo de l'organisateur"), labels=[_(u"Carr�"), _(u"Rond")], values=[0, 1], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez le type de cadre du logo de l'organisateur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # Cat�gorie
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
        propriete.SetHelpString(_(u"Saisissez un nom de lieu pour le retrait du document (ex: � l'accueil de la structure)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Paiement en ligne")) )

        # Activer le paiement en ligne
        nom = "paiement_ligne_actif"
        propriete = wxpg.BoolProperty(label=_(u"Activer le paiement en ligne"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer la fonction de paiement en ligne\n(ATTENTION: en test / d�veloppement)"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Choix du systeme de paiement en ligne
        nom = "paiement_ligne_systeme"
        # _(u"TIPI Formulaire (Non actif)"),
        propriete = wxpg.EnumProperty(label=_(u"Syst�me / Partenaire"), labels=[_(u"Aucun"), _(u"TIPI R�gie"), _(u"Payzen"), _(u"Mode d�mo")], values=[0, 1, 3, 4], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Choisissez le syst�me / partenaire � utiliser pour le paiement en ligne"))
        self.Append(propriete)

        # Choix du mode de r�glement pour les paiements en ligne
        DB = GestionDB.DB()
        req = """SELECT IDmode, label
        FROM modes_reglements
        ORDER BY IDmode;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        liste_reglements = [(0, u"Aucun")]
        for IDmode, label in listeDonnees:
            liste_reglements.append((IDmode, label))

        nom = "paiement_ligne_mode_reglement"
        propriete = wxpg.EnumProperty(label=_(u"Mode de r�glement"), labels=[y for x, y in liste_reglements], values=[x for x, y in liste_reglements], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Choisissez le mode de r�glement � associer aux paiements en ligne des factures"))
        self.Append(propriete)

        # Autoriser le paiement en ligne de plusieurs factures sur la meme transaction
        nom = "paiement_ligne_multi_factures"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser le paiement en ligne multi factures"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser le paiement en ligne de plusieurs factures en une fois"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Montant minimal pour le paiement en ligne
        nom = "paiement_ligne_montant_minimal"
        propriete = wxpg.FloatProperty(label=_(u"Montant minimal autoris�"), name="paiement_ligne_montant_minimal", value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Indiquez le montant minimal autoris� pour le paiement en ligne"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # TIPI : Type de saisie ( Test / Validation / Production )
        nom = "paiement_ligne_tipi_saisie"
        propriete = wxpg.EnumProperty(label=_(u"Mode de saisie TIPI"), labels=[_(u"Test"), _(u"Validation"), _(u"Production")], values=[0, 1, 2], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Choisissez le type de saisie TIPI.\nATTENTION !!!\n(A modifier uniquement si vous savez ce que vous faites.)"))
        self.Append(propriete)

        # PAYZEN : ID de la boutique
        nom = "payzen_site_id"
        propriete = wxpg.StringProperty(label=_(u"Identifiant boutique"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez l'identifiant boutique attribu� par Payzen"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # PAYZEN : Mode test ou production
        nom = "payzen_mode"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Mode de fonctionnement"), name=nom, liste_choix=[("TEST", _(u"Test")), ("PRODUCTION", _(u"Production"))], valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode de saisie des paiements. Attention, ne passez en mode production qu'apr�s avoir effectu� des essais en mode test."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # PAYZEN : Certificat de test
        nom = "payzen_certificat_test"
        propriete = wxpg.StringProperty(label=_(u"Certificat de test"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le certificat de test attribu� par Payzen"))
        self.Append(propriete)

        # PAYZEN : Certificat de production
        nom = "payzen_certificat_production"
        propriete = wxpg.StringProperty(label=_(u"Certificat de production"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le certificat de production attribu� par Payzen"))
        self.Append(propriete)

        # Paiement �chelonn�
        nom = "payzen_echelonnement"
        propriete = wxpg.BoolProperty(label=_(u"Proposer le paiement en 3 fois"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour activer le paiement en 3 fois. Cette option doit �galement �tre activ�e sur votre compte Payzen (Contacter service client Payzen)."))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # D�sactiver le paiement en ligne pour les familles abonn�es au pr�l�vement automatique
        nom = "paiement_off_si_prelevement"
        propriete = wxpg.BoolProperty(label=_(u"D�sactiver paiement en ligne si pr�l�vement auto."), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour d�sactiver le paiement en ligne pour les familles abonn�es au pr�l�vement automatique"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Accueil'")) )

        # Titre du portail
        nom = "accueil_titre"
        propriete = wxpg.LongStringProperty(label=_(u"Titre du portail"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez le titre du portail (les balises HTML sont accept�es)"))
        self.Append(propriete)

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
        propriete = wxpg.BoolProperty(label=_(u"Afficher l'�tat du dossier"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher l'�tat du dossier sur la page d'accueil"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Renseignements'")) )

        # Afficher
        nom = "renseignements_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page renseignements
        nom = "renseignements_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # Modifier
        nom = "renseignements_modifier"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser la modification"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher le bouton Modifier"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Noms
        nom = "renseignements_adulte_nom"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Nom et pr�nom des adultes"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        nom = "renseignements_enfant_nom"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Nom et pr�nom des enfants"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Naissance
        nom = "renseignements_adulte_naissance"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Date et lieu de naissance des adultes"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        nom = "renseignements_enfant_naissance"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Date et lieu de naissance des enfants"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse
        nom = "renseignements_adresse"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Adresse des adultes et enfants"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Coordonn�es
        nom = "renseignements_adulte_coords"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"T�l�phones et Email des adultes"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        nom = "renseignements_enfant_coords"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"T�l�phones et Email des enfants"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Profession
        nom = "renseignements_adulte_profession"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Profession des adultes"), name=nom, liste_choix=LISTE_SELECTION_RENSEIGNEMENTS, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le mode d'affichage de ce champ (ne pas afficher ou modification ou suppression)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)





        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Activit�s'")) )

        # Afficher
        nom = "activites_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page activit�s
        nom = "activites_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # Incription � une activit�
        nom = "activites_autoriser_inscription"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser l'inscription � des activit�s"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser l'inscription � des activit�s"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Bloquer l'incription � une activit� si complet
        nom = "activites_bloquer_complet"
        propriete = wxpg.BoolProperty(label=_(u"Bloquer l'inscription si activit� compl�te"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour bloquer l'inscription si l'activit� est compl�te"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'R�servations'")) )

        # Afficher
        nom = "reservations_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page r�servations
        nom = "reservations_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # Intro de la page planning
        nom = "planning_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction du calendrier"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction pour le calendrier"))
        self.Append(propriete)

        # Cat�gorie
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

        # S�lection des factures � afficher
        nom = "factures_selection"
        propriete = wxpg.EnumProperty(label=_(u"S�lection des factures � afficher"), labels=[y for x, y in LISTE_SELECTION_FACTURES], values=[x for x, y in LISTE_SELECTION_FACTURES], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un crit�re d'anciennet� pour les factures � afficher"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Demande d'une facture
        nom = "factures_demande_facture"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser la demande de factures"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser la demande de factures"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher la pr�facturation
        nom = "factures_prefacturation"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la pr�facturation"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher la pr�facturation"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher le solde total des factures
        nom = "factures_afficher_solde_total"
        propriete = wxpg.BoolProperty(label=_(u"Afficher le solde total � r�gler"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher le solde total � r�gler"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher le solde pour chaque facture
        nom = "factures_afficher_solde_detail"
        propriete = wxpg.BoolProperty(label=_(u"Afficher le solde � r�gler pour chaque facture"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher le solde � r�gler pour chaque facture"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher le solde de la famille
        nom = "factures_afficher_solde_famille"
        propriete = wxpg.BoolProperty(label=_(u"Afficher le solde de la famille"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher le solde total de la famille"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'R�glements'")) )

        # Afficher
        nom = "reglements_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page r�glements
        nom = "reglements_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # S�lection des r�glements � afficher
        nom = "reglements_selection"
        propriete = wxpg.EnumProperty(label=_(u"S�lection des r�glements � afficher"), labels=[y for x, y in LISTE_SELECTION_REGLEMENTS], values=[x for x, y in LISTE_SELECTION_REGLEMENTS], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un crit�re d'anciennet� pour les r�glements � afficher"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Demande d'un re�u
        nom = "reglements_demande_recu"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser la demande de re�us"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser la demande de re�us de r�glements"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Pi�ces'")) )

        # Afficher
        nom = "pieces_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page pi�ces
        nom = "pieces_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # T�l�chargements de pi�ces
        nom = "pieces_autoriser_telechargement"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser le t�l�chargement de pi�ces"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser le t�l�chargement de pi�ces"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Envoi de pi�ces
        nom = "pieces_autoriser_upload"
        propriete = wxpg.BoolProperty(label=_(u"Autoriser l'envoi de pi�ces"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser les familles � envoyer des pi�ces par le portail"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Cat�gorie
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

        # S�lection des cotisations � afficher
        nom = "cotisations_selection"
        propriete = wxpg.EnumProperty(label=_(u"S�lection des cotisations � afficher"), labels=[y for x, y in LISTE_SELECTION_COTISATIONS], values=[x for x, y in LISTE_SELECTION_COTISATIONS], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un crit�re d'anciennet� pour les cotisations � afficher"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Locations'")) )

        # Afficher
        nom = "locations_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Intro de la page locations
        nom = "locations_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction"))
        self.Append(propriete)

        # S�lection des locations � afficher
        nom = "locations_selection"
        propriete = wxpg.EnumProperty(label=_(u"S�lection des locations � afficher"), labels=[y for x, y in LISTE_SELECTION_LOCATIONS], values=[x for x, y in LISTE_SELECTION_LOCATIONS], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un crit�re d'anciennet� pour les locations � afficher"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Ouverture des r�servations
        nom = "locations_periode_saisie"
        propriete = wxpg.EnumProperty(label=_(u"Ouverture de la saisie des locations"), labels=[y for x, y in LISTE_SAISIE_LOCATIONS], values=[x for x, y in LISTE_SAISIE_LOCATIONS], name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez une p�riode d'ouverture des r�servations des locations"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Intro de la page planning
        nom = "planning_locations_intro"
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction du calendrier des locations"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction pour le calendrier des locations"))
        self.Append(propriete)

        # Heure affich�e min
        nom = "locations_heure_min"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Heure affich�e minimale"), name=nom, liste_choix=HEURES, valeur=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez l'heure minimale affich�e dans le planning des locations"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Heure affich�e max
        nom = "locations_heure_max"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Heure affich�e maximale"), name=nom, liste_choix=HEURES, valeur=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez l'heure maximale affich�e dans le planning des locations"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Afficher
        nom = "locations_afficher_autres_loueurs"
        propriete = wxpg.BoolProperty(label=_(u"Afficher le nom des autres loueurs"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher le nom des autres loueurs dans le planning des locations"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Cat�gorie
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

        # D�lai d'affichage de l'historique
        nom = "historique_delai"
        propriete = wxpg.EnumProperty(label=_(u"Temps d'affichage de l'historique"), labels=[y for x, y in LISTE_AFFICHAGE_HISTORIQUE], values=range(0, len(LISTE_AFFICHAGE_HISTORIQUE)), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"S�lectionnez un d�lai pour l'affichage de l'historique : Au-del� l'historique sera cach�."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Cat�gorie
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


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Mentions l�gales'")) )

        # Afficher
        nom = "mentions_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Cat�gorie
        self.Append( wxpg.PropertyCategory(_(u"Page 'Aide'")) )

        # Afficher
        nom = "aide_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Cochez cette case pour afficher cette page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)




    def Validation(self):
        """ Validation des donn�es saisies """
        for nom, valeur in self.GetPropertyValues().items() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True :
                if valeur == "" or valeur == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le param�tre '%s' !") % self.GetPropertyLabel(nom), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        if self.GetPropertyByName("mdp_autoriser_reinitialisation").GetValue() == True :
            if self.GetPropertyByName("email_type_adresse").GetValue() == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous avez coch� l'activation de la fonction de r�initialisation des mots de passe. Vous devez donc obligatoirement s�lectionner ou saisir une adresse d'exp�dition d'email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def Importation(self):
        """ Importation des valeurs dans le contr�le """
        # R�cup�ration des noms et valeurs par d�faut du contr�le
        dictValeurs = copy.deepcopy(self.GetPropertyValues())

        # Recherche les param�tres m�moris�s dans la base de donn�es
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="portail", dictParametres=dictValeurs)

        # Recherche des config m�moris�s sur cet ordi
        dictParametres["client_synchro_portail_activation"] = UTILS_Config.GetParametre("client_synchro_portail_activation", False)
        dictParametres["client_synchro_portail_delai"] = UTILS_Config.GetParametre("client_synchro_portail_delai", 2)
        dictParametres["client_synchro_portail_ouverture"] = UTILS_Config.GetParametre("client_synchro_portail_ouverture", True)
        dictParametres["client_rechercher_updates"] = UTILS_Config.GetParametre("client_rechercher_updates", True)
        #dictParametres["hebergement_type"] = UTILS_Config.GetParametre("hebergement_type", 0)
        #dictParametres["serveur_type"] = UTILS_Config.GetParametre("serveur_type", 0)

        # Envoie les param�tres dans le contr�le
        for nom, valeur in dictParametres.items() :
            propriete = self.GetPropertyByName(nom)
            type_propriete = type(VALEURS_DEFAUT[nom])
            if type_propriete == int and valeur != None :
                valeur = int(valeur)
            propriete.SetValue(valeur)

        # MAJ affichage grille
        self.Switch()

    def Sauvegarde(self):
        """ M�morisation des valeurs du contr�le """
        # M�morisation des param�tres dans la base de donn�es
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="portail", dictParametres=dictValeurs)

        # M�morisation de la config sur cet ordi
        for key in ("client_synchro_portail_activation", "client_synchro_portail_delai", "client_synchro_portail_ouverture", "client_rechercher_updates") :#, "hebergement_type", "serveur_type") :
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
        dlg = wx.FileDialog(None, message=_(u"Veuillez s�lectionner le fichier de configuration � restaurer"), defaultDir=rep, defaultFile="", wildcard=wildcard, style=wx.FD_OPEN)
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
                        if type_propriete in (str, six.text_type) :
                            valeur = six.text_type(valeur)
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

        dlg = wx.MessageDialog(None, _(u"Importation de la configuration effectu�e."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def Exportation_config(self, event=None):
        # Demande � l'utilisateur le nom de fichier et le r�pertoire de destination
        nomFichier = "Config_connecthys.cfg"
        wildcard = u"Fichier de configuration (*.cfg)|*.cfg|Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez s�lectionner le r�pertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.FD_SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe d�j� :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy()
                return False
            else:
                dlg.Destroy()

        # Cr�ation du fichier
        fichier = codecs.open(cheminFichier, encoding='utf-8', mode='w')
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        for cle, valeur in dictValeurs.items() :
            if type(valeur) in (str, six.text_type) :
                valeur = valeur.replace("\n", "#!#")
            ligne = u"%s = %s\n" % (cle, valeur)
            fichier.write(ligne)
        fichier.close()





# -------------------------------------------------------------------------------------------------------------------------


class Page_Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.ctrl_parametres = CTRL_Parametres(self)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_parametres, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def Validation(self):
        return self.ctrl_parametres.Validation()

    def Sauvegarde(self):
        return self.ctrl_parametres.Sauvegarde()



class Page_Conditions(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = "conditions_utilisation"

        self.ctrl_html = rt.RichTextCtrl(self, id=-1, style=wx.VSCROLL | wx.HSCROLL | wx.WANTS_CHARS)#wx.html.HtmlWindow(self, style=wx.BORDER_SUNKEN)
        self.ctrl_html.SetEditable(False)

        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))

        self.ctrl_infos = wx.html.HtmlWindow(self, style=wx.BORDER_THEME)
        self.ctrl_infos.SetMinSize((-1, 50))
        self.ctrl_infos.SetBorders(4)
        self.ctrl_infos.SetPage(u"""
        <FONT SIZE=2><IMG SRC="%s"><B>Astuce</B> : Vous pouvez utiliser les mots-cl�s suivants pour int�grer les donn�es de l'organisateur dans le texte : {ORGANISATEUR_NOM}, 
        {ORGANISATEUR_RUE}, {ORGANISATEUR_CP}, {ORGANISATEUR_VILLE}, {ORGANISATEUR_TEL}, {ORGANISATEUR_FAX}, {ORGANISATEUR_EMAIL}.</FONT>
        """ % Chemins.GetStaticPath(u"Images/16x16/Astuce.png"))
        self.ctrl_infos.SetBackgroundColour(wx.SystemSettings.GetColour(30))

        self.Bind(wx.EVT_BUTTON, self.OnModifier, self.bouton_modifier)
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour �diter le texte")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_html, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        sizer_base.Add(self.ctrl_infos, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.MAJ()
        self.bouton_modifier.SetFocus()

    def MAJ(self):
        # Importation du texte
        DB = GestionDB.DB()
        req = """SELECT IDelement, texte_xml
        FROM portail_elements
        WHERE categorie='%s';""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDelement, texte_xml = listeDonnees[0]

        # Insertion du texte
        out = six.BytesIO()
        handler = wx.richtext.RichTextXMLHandler()
        buf = self.ctrl_html.GetBuffer()
        buf.AddHandler(handler)
        if (six.PY3 and not isinstance(texte_xml, bytes)) or (six.PY2 and not isinstance(texte_xml, buffer)):
            texte_xml = texte_xml.encode("utf8")
        out.write(texte_xml)
        out.seek(0)
        if 'phoenix' in wx.PlatformInfo:
            handler.LoadFile(buf, out)
        else:
            handler.LoadStream(buf, out)
        self.ctrl_html.Refresh()

    def OnModifier(self, event):
        from Dlg import DLG_Saisie_texte_html
        dlg = DLG_Saisie_texte_html.Dialog(self, categorie=self.categorie)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
            UTILS_Parametres.Parametres(mode="set", categorie="portail", nom="last_update_pages", valeur=str(datetime.datetime.now()))
        dlg.Destroy()





class Page_Pages(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_pages = CTRL_Portail_pages.CTRL(self)

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.Descendre, self.bouton_descendre)

        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une page ou un bloc")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'�l�ment s�lectionn� dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'�l�ment s�lectionn� dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter l'�l�ment s�lectionn� dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre l'�l�ment s�lectionn� dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_pages, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.ctrl_pages.MAJ()





class CTRL_Notebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}

        self.listePages = [
            {"code": "parametres", "ctrl": Page_Parametres(self), "label": _(u"Param�tres g�n�raux"), "image": "Mecanisme.png"},
            {"code": "conditions", "ctrl": Page_Conditions(self), "label": _(u"Conditions d'utilisation"), "image": "Questionnaire.png"},
            {"code": "pages", "ctrl": Page_Pages(self), "label": _(u"Pages personnalis�es"), "image": "Copier.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Cr�ation des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def GetCtrl(self, codePage=""):
        return self.dictPages[codePage]

    def GetCtrlParametres(self):
        return self.dictPages["parametres"].ctrl_parametres

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    # def OnPageChanged(self, event):
    #     """ Quand une page du notebook est s�lectionn�e """
    #     if event.GetOldSelection() == -1: return
    #     indexPage = event.GetSelection()
    #     page = self.GetPage(indexPage)
    #     self.Freeze()
    #     wx.CallLater(1, page.Refresh)
    #     self.Thaw()
    #     event.Skip()

    def Validation(self):
        for dictPage in self.listePages :
            if hasattr(dictPage["ctrl"], "Validation"):
                if dictPage["ctrl"].Validation() == False :
                    return False
        return True
    
    def Sauvegarde(self):
        for dictPage in self.listePages :
            if hasattr(dictPage["ctrl"], "Sauvegarde"):
                dictPage["ctrl"].Sauvegarde()



# -------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Bandeau
        intro = _(u"Connecthys est le portail internet de Noethys. Vous devez au pr�alable disposer d'un h�bergement internet compatible. Utilisez les fonctionnalit�s ci-dessous pour installer et synchroniser le portail avec votre fichier de donn�es Noethys.")
        titre = _(u"Connecthys")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Connecthys.png")

        # Param�tres
        self.box_parametres = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.ctrl_notebook = CTRL_Notebook(self)

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
        self.bouton_easy = CTRL_Bouton_image.CTRL(self, texte=_(u"Souscrire � Connecthys Easy"), cheminImage="Images/32x32/Connecthys.png")
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
        self.bouton_easy.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour souscrire � l'offre Connecthys Easy")))
        self.bouton_site.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der au site internet www.connecthys.com")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der aux outils")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Param�tres
        box_parametres = wx.StaticBoxSizer(self.box_parametres, wx.VERTICAL)
        box_parametres.Add(self.ctrl_notebook, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Log
        staticbox_actions = wx.StaticBoxSizer(self.box_log, wx.VERTICAL)
        grid_sizer_actions = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_actions.Add(self.log, 1, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.gauge, 0, wx.EXPAND, 0)
        staticbox_actions.Add(grid_sizer_actions, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(staticbox_actions, 1, wx.EXPAND, 0)

        # Messages
        staticbox_messages = wx.StaticBoxSizer(self.box_messages, wx.VERTICAL)
        staticbox_messages.Add(self.ctrl_messages, 1, wx.ALL|wx.EXPAND, 5)
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
        UTILS_Aide.Aide("Connecthys")

    def OnBoutonFermer(self, event):
        if self.ctrl_notebook.Validation() == False :
            return False
        self.MemoriseParametres()
        self.EndModal(wx.ID_CANCEL)

    def OnClose(self, event):
        if self.ctrl_notebook.Validation() == False :
            return False
        self.MemoriseParametres()
        event.Skip()

    def MemoriseParametres(self):
        self.ctrl_notebook.Sauvegarde()

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
        # Cr�ation du menu contextuel
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()

        menu = UTILS_Adaptations.Menu()

        server_is_running = False
        if dict_parametres["serveur_type"] == 0:
            if self.server_ctrl != None :
                server_is_running = self.server_ctrl.GetServerStatus()
            else :
                if self.ctrl_notebook.Validation() == True :
                    self.server_ctrl = UTILS_Portail_controle.ServeurConnecthys(self)
                    server_is_running = self.server_ctrl.GetServerStatus()


        # Installer
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Installer"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Installer, id=id)

        # Mettre � jour
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Mettre � jour"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Update, id=id)

        # Upgrade DB
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Forcer l'upgrade de la base de donn�es"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Database.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.DemandeUpgradeDB, id=id)

        # Repair DB
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"R�parer la base de donn�es"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Database.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.DemandeRepairDB, id=id)

        # Clear DB
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Vider la base de donn�es"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Database.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.DemandeClearDB, id=id)

        menu.AppendSeparator()

        # AutoReload WSGI
        if dict_parametres["serveur_type"] == 2 :
            id = wx.Window.NewControlId()
            item = wx.MenuItem(menu, id, _(u"AutoReload WSGI"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.AutoReloadWSGI, id=id)

        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Consulter le log du portail"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Log.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.LireJournal, id=id)

        menu.AppendSeparator()

        # Importer config
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Importer la configuration"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_import.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_notebook.GetCtrlParametres().Importation_config, id=id)

        # Exporter config
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Exporter la configuration"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_export.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_notebook.GetCtrlParametres().Exportation_config, id=id)

        menu.AppendSeparator()

        if dict_parametres["serveur_type"] == 0 and self.server_ctrl != None :

            # D�marrer
            id = wx.Window.NewControlId()
            item = wx.MenuItem(menu, id, _(u"D�marrer le serveur"))
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

            # Arr�ter
            id = wx.Window.NewControlId()
            item = wx.MenuItem(menu, id, _(u"Arr�ter le serveur"))
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
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Synchroniser les donn�es"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Synchroniser, id=id)

        # Synchronisation compl�te
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Forcer la synchronisation compl�te"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Synchroniser_full, id=id)

        menu.AppendSeparator()

        # Traiter les donn�es
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Traiter les demandes"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Traiter, id=id)

        menu.AppendSeparator()

        # Ouvrir Connecthys
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Afficher Connecthys dans le navigateur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Planete.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirNavigateur, id=id)

        # Ouvrir les stats de Connecthys Easy
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menu, id, _(u"Afficher les statistiques dans le navigateur"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Barres.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirStats, id=id)

        self.PopupMenu(menu)
        menu.Destroy()

    def Installer(self, event):
        # R�cup�ration des param�tres de l'installation
        if self.ctrl_notebook.Validation() == False :
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
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
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le r�pertoire FTP !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
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
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le num�ro de port du serveur SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_utilisateur"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nom de de l'utilisateur SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_mdp"] == "" and dict_parametres["ssh_key_file"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le mot de passe de l utilisateur SSH ou utiliser une connection par cl� !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if dict_parametres["ssh_repertoire"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le r�pertoire SSH !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        elif dict_parametres["hebergement_type"] == 0 :

            if dict_parametres["hebergement_local_repertoire"] == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir le r�pertoire local !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
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
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'url d'acc�s � Connecthys !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Proc�dure d'installation
        from Utils import UTILS_Portail_installation
        install = UTILS_Portail_installation.Installer(self, dict_parametres, server_ctrl)
        resultat = install.Installer()

    def Update(self, event):
        if self.ctrl_notebook.Validation() == False :
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.Update()

    def AutoReloadWSGI(self, event):
        if self.ctrl_notebook.Validation() == False :
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.AutoReloadWSGI()

    def LireJournal(self, event):
        if self.ctrl_notebook.Validation() == False :
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        self.EcritLog(_(u"T�l�chargement du log..."))
        synchro = Synchro(self, dict_parametres)
        contenu_fichier = synchro.ConnectEtTelechargeFichier("debug.log")
        if contenu_fichier == False :
            self.EcritLog(_(u"Le log n'a pas pu �tre t�l�charg�."))
            return False

        from Dlg import DLG_Editeur_texte
        dlg = DLG_Editeur_texte.Dialog(self, texte=contenu_fichier)
        dlg.ShowModal()
        dlg.Destroy()

    def DemandeUpgradeDB(self, event):
        if self.ctrl_notebook.Validation() == False:
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        self.EcritLog(_(u"Demande d'upgrade de la base de donn�es..."))
        synchro = Synchro(self, dict_parametres)
        if synchro.Upgrade_application() == True :
            self.EcritLog(_(u"Upgrade effectu�."))

    def DemandeRepairDB(self, event):
        if self.ctrl_notebook.Validation() == False:
            return False
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment ex�cuter cette op�ration ?\n\nAttention, cette op�ration peut �tre risqu�e ! "), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        self.EcritLog(_(u"Demande de r�paration de la base de donn�es..."))
        synchro = Synchro(self, dict_parametres)
        if synchro.Repair_application() == True :
            self.EcritLog(_(u"R�paration effectu�e."))

    def DemandeClearDB(self, event):
        if self.ctrl_notebook.Validation() == False:
            return False
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment vider la base de donn�es du portail ?\n\nLes donn�es seront effac�es des tables !"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        dlg = wx.MessageDialog(self, _(u"Vous �tes vraiment s�r de vouloir vider la base de donn�es du portail ?\n\nAttention, cette op�ration est irr�versible !"), _(u"Dernier avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        self.EcritLog(_(u"Demande d'effacement de la base de donn�es..."))
        synchro = Synchro(self, dict_parametres)
        if synchro.Clear_application() == True :
            self.EcritLog(_(u"Effacement effectu�."))

    def OuvrirNavigateur(self, event):
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        url = dict_parametres["url_connecthys"]
        if url == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner l'URL d'acc�s � Connecthys !"), _(u"Acc�s impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if dict_parametres["serveur_type"] == 1 :
            url += "/" + dict_parametres["serveur_cgi_file"] + "/"

        self.EcritLog(_(u"Ouverture dans le navigateur de l'url %s") % url)
        import webbrowser
        webbrowser.open(url)

    def OuvrirStats(self, event):
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        url = dict_parametres["url_connecthys"]
        if url == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner l'URL d'acc�s � Connecthys !"), _(u"Acc�s impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        stats_utilisateur = dict_parametres["stats_utilisateur"]
        if stats_utilisateur == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner le nom d'utilisateur de la rubrique Statistiques !\n\nAttention, cette fonctionnalit� n'est disponible que pour les abonn�s Connecthys Easy."), _(u"Acc�s impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        stats_mdp = dict_parametres["stats_mdp"]
        if stats_mdp == "" :
            dlg = wx.MessageDialog(None, _(u"Vous devez renseigner le mot de passe de la rubrique Statistiques !\n\nAttention, cette fonctionnalit� n'est disponible que pour les abonn�s Connecthys Easy."), _(u"Acc�s impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        url += "/stats/index.html"

        # M�morisation du mot de passe stats dans le presse-papiers
        clipdata = wx.TextDataObject()
        clipdata.SetText(stats_mdp)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        # Affiche une fen�tre avec les codes
        texte = u"""
        <CENTER><IMG SRC="%s">
        <FONT SIZE=3>
        <BR>
        <B>Acc�s aux statistiques Connecthys Easy</B>
        <BR><BR>
        Noethys va ouvrir votre navigateur internet pour vous permettre d'acc�der aux statistiques Connecthys Easy.
        <BR><BR>
        Les codes d'acc�s suivants vont vous �tre demand�s :
        <BR><BR>
        <B>
        <UL>
            <LI>Nom d'utilisateur : %s</LI>
            <LI>Mot de passe : %s</LI>
        </UL>
        </B>
        <BR><BR>
        Remarque : Le mot de passe a �t� copi� dans le presse-papiers. Vous pouvez donc utiliser <B>CTRL+V</B> pour le coller dans le champ de saisie.
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
        if self.ctrl_notebook.Validation() == False :
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
        synchro = Synchro(self, dict_parametres)
        synchro.Start()

    def Synchroniser_full(self, event):
        if self.ctrl_notebook.Validation() == False :
            return False
        dict_parametres = self.ctrl_notebook.GetCtrlParametres().GetValeurs()
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
Connecthys est le portail internet de Noethys. Il permet par exemple � vos usagers de
consulter l'�tat de leur dossier ou de demander des r�servations � des activit�s.
Il facilite �galement la gestion administrative par les utilisateurs gr�ce � son
traitement automatis� des demandes.
<BR><BR>
Si vous souhaitez en savoir davantage, allez dans le menu Outils ou visitez le site d�di�
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

    def Repair_application(self):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)
        synchro.Repair_application()

    def Clear_application(self):
        from Utils import UTILS_Portail_synchro
        synchro = UTILS_Portail_synchro.Synchro(dict_parametres=self.dict_parametres, log=self)
        synchro.Clear_application()

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
