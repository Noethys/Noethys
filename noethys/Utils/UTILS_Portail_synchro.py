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
import datetime
import random
import os.path
import codecs
import ftplib
import zipfile
import shutil
import json
import six
from six.moves.urllib.request import Request, urlopen
import sys
import importlib
import platform
import time
from dateutil import relativedelta
import paramiko

from Utils import UTILS_Dates
from Utils import UTILS_Parametres
from Utils import UTILS_Fichiers
from Utils import UTILS_Titulaires
from Utils import UTILS_Pieces_manquantes
from Utils import UTILS_Cotisations_manquantes
from Utils import UTILS_Organisateur
from Utils import UTILS_Cryptage_fichier
from Utils import UTILS_Config
from Utils import UTILS_Customize
from Utils import UTILS_Internet
import FonctionsPerso
import GestionDB

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Dlg.DLG_Portail_config import VALEURS_DEFAUT as VALEURS_DEFAUT_CONFIG
from Dlg.DLG_Portail_config import LISTE_THEMES

from Crypto.Hash import SHA256


def patch_crypto_be_discovery():
    """ Patch pour Paramiko contre bug backends missing lors de la compilation sur Windows """
    from cryptography.hazmat import backends

    try:
        from cryptography.hazmat.backends.commoncrypto.backend import backend as be_cc
    except ImportError:
        be_cc = None

    try:
        from cryptography.hazmat.backends.openssl.backend import backend as be_ossl
    except ImportError:
        be_ossl = None

    backends._available_backends_list = [
        be for be in (be_cc, be_ossl) if be is not None
    ]

if platform.system() != 'Linux' :
    patch_crypto_be_discovery()


class Synchro():
    def __init__(self, dict_parametres=None, log=None):
        # Récupération des données de config du portail si besoin
        if dict_parametres == None :
            self.dict_parametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="portail", dictParametres=VALEURS_DEFAUT_CONFIG)
        else :
            self.dict_parametres = dict_parametres

        self.log = log
        self.num_etape = 0
        self.nbre_etapes = 25

        if self.dict_parametres["accept_all_cert"] == True :
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context


    def Pulse_gauge(self, num=None):
        if num == None :
            self.num_etape += 1
        else :
            self.num_etape = num
        num = 100 * self.num_etape / self.nbre_etapes
        try :
            self.log.SetGauge(num)
        except :
            pass

    def Synchro_totale(self, full_synchro=False):
        t1 = time.time()
        self.nbre_etapes = 26
        self.log.EcritLog(_(u"Lancement de la synchronisation..."))

        # Téléchargement des données en ligne
        self.Download_data(full_synchro=full_synchro)

        # Recherche de mises à jours logicielles Connecthys
        if self.dict_parametres["client_rechercher_updates"] == True :

            # Vérifie si une update n'a pas été faite aujourd'hui avec la même version de Noethys
            last_update = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="last_update", valeur=None)
            version_noethys = FonctionsPerso.GetVersionLogiciel()
            data = "%s#%s" % (str(datetime.date.today()), version_noethys)
            if data != last_update :
                resultat = self.Update_application()
                # Mémorise la demande d'update
                if resultat == True :
                    UTILS_Parametres.Parametres(mode="set", categorie="portail", nom="last_update", valeur=data)

        # Upload des données locales
        resultat = self.Upload_data(full_synchro=full_synchro)
        if resultat == False :
            self.log.EcritLog(_(u"Synchronisation arrêtée."))
        else :
            secondes = time.time() - t1
            self.log.EcritLog(_(u"Synchronisation effectuée en %d secondes.") % secondes)
        self.log.EcritLog(_(u"Client de synchronisation prêt"))
        try :
            self.log.SetGauge(0)
        except :
            pass

    # FTP mode
    def Upload_config(self, ftp=None):
        """ Met en ligne le fichier de config """
        liste_lignes = [
            u"#!/usr/bin/env python\n",
            u"# -*- coding: utf-8 -*-\n",
            u"\n",
            u"import os\n",
            u"basedir = os.path.abspath(os.path.dirname(__file__))\n",
            u"\n",
            u"class Config_application(object):\n"
        ]

        def Ecrit_ligne(key="", valeur="", type_valeur=None):
            if type_valeur == six.text_type :
                valeur = u'u"%s"' % valeur
            elif type_valeur == str :
                valeur = u'"%s"' % valeur
            elif type_valeur == None :
                valeur = valeur
            else :
                valeur = str(valeur)
            return u"     %s = %s\n" % (key, valeur)

        # Valeurs Application
        if self.dict_parametres["db_type"] == 0 :
            # Base Sqlite
            liste_lignes.append(Ecrit_ligne("SQLALCHEMY_DATABASE_URI", "'sqlite:///' + os.path.join(basedir, 'data.db')", type_valeur=None))
        else :
            # Base MySQL
            db_serveur = self.dict_parametres["db_serveur"]
            db_utilisateur = self.dict_parametres["db_utilisateur"]
            db_mdp = self.dict_parametres["db_mdp"]
            db_nom = self.dict_parametres["db_nom"]
            liste_lignes.append(Ecrit_ligne("SQLALCHEMY_DATABASE_URI", "mysql://%s:%s@%s/%s?charset=utf8" % (db_utilisateur, db_mdp, db_serveur, db_nom), type_valeur=str))

        liste_lignes.append(Ecrit_ligne("SQLALCHEMY_TRACK_MODIFICATIONS", True, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("SQLALCHEMY_ECHO", False, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("SECRET_KEY", self.dict_parametres["secret_key"], type_valeur=str))
        liste_lignes.append(Ecrit_ligne("WTF_CSRF_ENABLED", True, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("PREFIXE_TABLES", self.dict_parametres["prefixe_tables"], type_valeur=str))
        liste_lignes.append(Ecrit_ligne("DEBUG", self.dict_parametres["mode_debug"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("TALISMAN", self.dict_parametres["talisman"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("CAPTCHA", self.dict_parametres["captcha"], type_valeur=int))

        # Paramètres SMTP pour Flask-mail
        if self.dict_parametres["email_type_adresse"] > 0 :
            adresse_valide = False

            if self.dict_parametres["email_type_adresse"] == 999:
                MAIL_SERVER = self.dict_parametres["email_serveur"]
                MAIL_DEFAULT_SENDER = self.dict_parametres["email_adresse"]
                MAIL_PORT = self.dict_parametres["email_port"]
                MAIL_USE_TLS = self.dict_parametres["email_tls"]
                MAIL_USE_SSL = self.dict_parametres["email_ssl"]
                MAIL_USERNAME = self.dict_parametres["email_utilisateur"]
                MAIL_PASSWORD = self.dict_parametres["email_password"]
                adresse_valide = True

            else :
                DB = GestionDB.DB()
                req = """SELECT smtp, adresse, port, startTLS, connexionAuthentifiee, utilisateur, motdepasse
                FROM adresses_mail WHERE IDadresse=%d;""" % self.dict_parametres["email_type_adresse"]
                DB.ExecuterReq(req)
                listeAdresses = DB.ResultatReq()
                DB.Close()
                if len(listeAdresses) > 0:
                    MAIL_SERVER, MAIL_DEFAULT_SENDER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD = listeAdresses[0]
                    adresse_valide = True

            # Mémorisation des paramètres emails
            if adresse_valide == True :
                liste_lignes.append(Ecrit_ligne("MAIL_SERVER", MAIL_SERVER, type_valeur=str))
                liste_lignes.append(Ecrit_ligne("MAIL_DEFAULT_SENDER", MAIL_DEFAULT_SENDER, type_valeur=str))
                try:
                    MAIL_PORT = int(MAIL_PORT)
                except:
                    MAIL_PORT = None
                liste_lignes.append(Ecrit_ligne("MAIL_PORT", MAIL_PORT))

                if MAIL_USE_TLS in (1, True):
                    MAIL_USE_TLS = True
                else :
                    MAIL_USE_TLS = False
                liste_lignes.append(Ecrit_ligne("MAIL_USE_TLS", MAIL_USE_TLS))

                if MAIL_USE_SSL in (1, True):
                    MAIL_USE_SSL = True
                else :
                    MAIL_USE_SSL = False
                liste_lignes.append(Ecrit_ligne("MAIL_USE_SSL", MAIL_USE_SSL))


                if MAIL_USERNAME in ("", None):
                    liste_lignes.append(Ecrit_ligne("MAIL_USERNAME", None))
                else :
                    liste_lignes.append(Ecrit_ligne("MAIL_USERNAME", MAIL_USERNAME, type_valeur=str))

                if MAIL_PASSWORD in ("", None):
                    liste_lignes.append(Ecrit_ligne("MAIL_PASSWORD", None))
                else :
                    liste_lignes.append(Ecrit_ligne("MAIL_PASSWORD", MAIL_PASSWORD, type_valeur=six.text_type))

            else :
                self.dict_parametres["mdp_autoriser_reinitialisation"] = False

        # Génération du fichier
        nomFichier = "config.py"
        nomFichierComplet = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
        fichier = codecs.open(nomFichierComplet, 'w', encoding='utf8')
        for ligne in liste_lignes :
            fichier.write(ligne)
        fichier.close()

        # Mode WSGI : Comparaison des 2 fichiers de config
        dirty_config = True
        #if self.dict_parametres["serveur_type"] == 2 :
        self.log.EcritLog(_(u"Téléchargement du fichier de config"))
        resultat = self.TelechargeFichier(ftp=ftp, nomFichier="config.py", repFichier="application/data")
        if resultat != False :
            fichier_online = open(os.path.join(resultat[0], resultat[1]), "r")
            liste_lignes_online = fichier_online.readlines()
            fichier_online.close()

            # Comparaison du fichier en ligne et du fichier généré
            if liste_lignes_online == liste_lignes :
                dirty_config = False

        if dirty_config == True :
            # Upload du fichier de config
            self.UploadFichier(ftp=ftp, nomFichierComplet=nomFichierComplet, repDest="application/data")

            # Auto reload WSGI
            if self.dict_parametres["serveur_type"] == 2 :
                self.AutoReloadWSGI(ftp)

        return True

    def AutoReloadWSGI(self, ftp=None):
        if ftp == None :
            resultats = self.Connexion()
            if resultats == False :
                return False
            else :
                ftp, ssh = resultats
            connexion_provisoire = True
        else :
            connexion_provisoire = False

        self.log.EcritLog(_(u"Mise à jour du fichier WSGI pour auto reload"))

        # Téléchargement du fichier wsgi
        resultat = self.TelechargeFichier(ftp=ftp, nomFichier="connecthys.wsgi", repFichier=None)
        if resultat == False :
            return False
        fichier_wsgi = open(os.path.join(resultat[0], resultat[1]), "r")
        liste_lignes_wsgi = fichier_wsgi.readlines()
        fichier_wsgi.close()

        # Création du nouveau fichier wsgi
        nomFichierComplet = UTILS_Fichiers.GetRepTemp(fichier="connecthys.wsgi")
        fichier_wsgi = codecs.open(nomFichierComplet, 'w')
        for ligne in liste_lignes_wsgi :
            if "lastupdate" in ligne :
                ligne = "# lastupdate = %s" % datetime.datetime.now()
            fichier_wsgi.write(ligne)
        fichier_wsgi.close()

        # Envoi du nouveau fichier wsgi
        self.UploadFichier(ftp=ftp, nomFichierComplet=nomFichierComplet, repDest="")

        # Si connexion provisoire
        if connexion_provisoire == True :
            self.Deconnexion(ftp)

    def Connexion(self):
        ftp = None
        ssh = None

        # Avance gauge si local
        if self.dict_parametres["hebergement_type"] == 0 :
            self.Pulse_gauge()
            ftp = None

        # Connexion FTP
        if self.dict_parametres["hebergement_type"] == 1 :
            self.log.EcritLog(_(u"Connexion FTP..."))
            self.Pulse_gauge()

            try :
                ftp = ftplib.FTP(self.dict_parametres["ftp_serveur"], self.dict_parametres["ftp_utilisateur"], self.dict_parametres["ftp_mdp"])
            except Exception as err :
                print("Connexion FTP du serveur", str(err))
                self.log.EcritLog(_(u"[ERREUR] Connexion FTP impossible."))
                return False

        # Connexion SSH/SFTP
        if self.dict_parametres["hebergement_type"] == 2 :
            self.log.EcritLog(_(u"Connexion SSH/SFTP..."))
            self.Pulse_gauge()

            try :
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.dict_parametres["ssh_serveur"], port=int(self.dict_parametres["ssh_port"]), username=self.dict_parametres["ssh_utilisateur"], password=self.dict_parametres["ssh_mdp"])
                ftp = ssh.open_sftp()
                ftp.chdir("/" + self.dict_parametres["ssh_repertoire"])
            except Exception as err :
                print("Erreur connexion SSH/SFTP au serveur : ", str(err))
                self.log.EcritLog(_(u"[ERREUR] Connexion SSH/SFTP impossible."))
                try:
                    self.log.EcritLog(_(u"[ERREUR] err: %s") % err.encode('ascii', 'ignore'))
                except:
                    self.log.EcritLog(_(u"[ERREUR] err: %s") % err)
                return False

        return ftp, ssh


    def Deconnexion(self, ftp=None):
        if self.dict_parametres["hebergement_type"] == 1 :
            self.log.EcritLog(_(u"Fermeture de la connexion FTP..."))
            ftp.quit()
        elif self.dict_parametres["hebergement_type"] == 2 :
            self.log.EcritLog(_(u"Fermeture de la connexion SSH/SFTP..."))
            ftp.close()
        else :
            pass

    def Upload_data(self, full_synchro=False) :
        self.log.EcritLog(_(u"Lancement de la synchronisation des données..."))
        t1 = time.time()

        last_synchro = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="last_synchro", valeur="")

        resultats = self.Connexion()
        if resultats == False :
            return False
        else :
            ftp, ssh = resultats

        # Envoi du fichier de config
        self.log.EcritLog(_(u"Synchro du fichier de configuration..."))
        self.Pulse_gauge()
        resultat = self.Upload_config(ftp=ftp)
        if resultat == False :
            self.log.EcritLog(_(u"[ERREUR] Synchro du fichier de configuration impossible."))
            self.Deconnexion(ftp)
            return False

        # Récupération du fichier models
        self.log.EcritLog(_(u"Récupération des modèles de données..."))
        resultat = self.TelechargeFichier(ftp=ftp, nomFichier="models.py", repFichier="application")
        if resultat == False :
            self.log.EcritLog(_(u"[ERREUR] Récupération des modèles de données impossible."))
            self.Deconnexion(ftp)
            return False

        chemin, nomFichier = resultat
        if "models" in sys.modules:
            del sys.modules["models"]

        # Import du fichier models.py
        sys.path.append(chemin)
        models = importlib.import_module(nomFichier.replace(".py", ""))

        # Génération d'un nombre secret pour le nom de fichier des données
        secret = ""
        for x in range(0, 20) :
            secret += random.choice("1234567890")
        secret = int(secret)

        # Initialisation de la base de données
        nomFichierDB = UTILS_Fichiers.GetRepTemp(fichier="import_%d.db" % secret)
        engine = models.create_engine("sqlite:///%s" % nomFichierDB, echo=False)

        # Création des tables
        models.Base.metadata.drop_all(engine)
        models.Base.metadata.create_all(engine)

        # Création d'une session
        Session = models.sessionmaker(bind=engine)
        session = Session()

        # Liste des tables modifiées à importer dans Connecthys
        liste_tables_modifiees =[]

        # Ouverture de la base Noethys
        DB = GestionDB.DB()

        self.log.EcritLog(_(u"Récupération des données à exporter..."))
        self.Pulse_gauge()

        # Préparation du cryptage des valeurs
        cryptage = UTILS_Cryptage_fichier.AESCipher(self.dict_parametres["secret_key"][10:20], bs=16, prefixe=u"#@#")

        # Création des paramètres

        # IDfichier
        IDfichier = FonctionsPerso.GetIDfichier()
        session.add(models.Parametre(nom="IDfichier", parametre=IDfichier))

        # Thème
        index = 0
        for code, label in LISTE_THEMES :
            if index == self.dict_parametres["theme"] :
                theme = "skin-%s" % code
            index += 1
        session.add(models.Parametre(nom="SKIN", parametre=theme))

        # Image de fond identification
        last_fond = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="last_fond", valeur="")
        if self.dict_parametres["image_identification"] != "" :
            chemin_image = self.dict_parametres["image_identification"]
            nom_fichier = os.path.basename(chemin_image)

            # Upload du fichier image de fond
            if nom_fichier != last_fond or full_synchro == True :
                self.UploadFichier(ftp=ftp, nomFichierComplet=chemin_image, repDest="application/static/fonds")

        else :
            nom_fichier = ""

        if last_fond != nom_fichier :
            UTILS_Parametres.Parametres(mode="set", categorie="portail", nom="last_fond", valeur=nom_fichier)

        session.add(models.Parametre(nom="IMAGE_FOND", parametre=nom_fichier))

        # Cadre logo organisateur
        if self.dict_parametres["cadre_logo"] == 0 :
            rond = False
        else :
            rond = True
        session.add(models.Parametre(nom="ORGANISATEUR_IMAGE_ROND", parametre=str(rond)))

        # Données organisateur
        dict_organisateur = UTILS_Organisateur.GetDonnees(tailleLogo=(200, 200))

        session.add(models.Parametre(nom="ORGANISATEUR_NOM", parametre=dict_organisateur["nom"]))
        session.add(models.Parametre(nom="ORGANISATEUR_RUE", parametre=dict_organisateur["rue"].replace("\n", "")))
        session.add(models.Parametre(nom="ORGANISATEUR_CP", parametre=dict_organisateur["cp"]))
        session.add(models.Parametre(nom="ORGANISATEUR_VILLE", parametre=dict_organisateur["ville"]))
        session.add(models.Parametre(nom="ORGANISATEUR_TEL", parametre=dict_organisateur["tel"]))
        session.add(models.Parametre(nom="ORGANISATEUR_FAX", parametre=dict_organisateur["fax"]))
        session.add(models.Parametre(nom="ORGANISATEUR_EMAIL", parametre=dict_organisateur["mail"]))

        # Logo organisateur
        logo = dict_organisateur["logo"]
        if logo != None :
            nomFichier = "logo.png"
            session.add(models.Parametre(nom="ORGANISATEUR_IMAGE", parametre=nomFichier))

            # Upload du logo
            if dict_organisateur["logo_update"] > last_synchro or full_synchro == True :
                cheminLogo = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
                logo.SaveFile(cheminLogo, type=wx.BITMAP_TYPE_PNG)
                print("Upload du logo")
                self.UploadFichier(ftp=ftp, nomFichierComplet=cheminLogo, repDest="application/static")

        else :
            session.add(models.Parametre(nom="ORGANISATEUR_IMAGE", parametre=""))

        # Autres
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_EMAIL", parametre=str(self.dict_parametres["recevoir_document_email"])))
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_POSTE", parametre=str(self.dict_parametres["recevoir_document_courrier"])))
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_RETIRER", parametre=str(self.dict_parametres["recevoir_document_site"])))
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_RETIRER_LIEU", parametre=self.dict_parametres["recevoir_document_site_lieu"]))
        session.add(models.Parametre(nom="PAIEMENT_EN_LIGNE_ACTIF", parametre=str(self.dict_parametres["paiement_ligne_actif"])))
        session.add(models.Parametre(nom="MDP_FORCER_MODIFICATION", parametre=str(self.dict_parametres["mdp_forcer_modification"])))
        session.add(models.Parametre(nom="MDP_AUTORISER_MODIFICATION", parametre=str(self.dict_parametres["mdp_autoriser_modification"])))
        session.add(models.Parametre(nom="MDP_AUTORISER_REINITIALISATION", parametre=str(self.dict_parametres["mdp_autoriser_reinitialisation"])))

        if self.dict_parametres["paiement_ligne_actif"] == 1 :
            session.add(models.Parametre(nom="PAIEMENT_EN_LIGNE_SYSTEME", parametre=str(self.dict_parametres["paiement_ligne_systeme"])))
            session.add(models.Parametre(nom="PAIEMENT_EN_LIGNE_MULTI_FACTURES", parametre=str(self.dict_parametres["paiement_ligne_multi_factures"])))
            session.add(models.Parametre(nom="PAIEMENT_EN_LIGNE_MONTANT_MINIMAL", parametre=str(self.dict_parametres["paiement_ligne_montant_minimal"])))
            session.add(models.Parametre(nom="PAIEMENT_OFF_SI_PRELEVEMENT", parametre=str(self.dict_parametres["paiement_off_si_prelevement"])))
            if "paiement_ligne_tipi_saisie" in self.dict_parametres:
                session.add(models.Parametre(nom="PAIEMENT_EN_LIGNE_TIPI_SAISIE", parametre=str(self.dict_parametres["paiement_ligne_tipi_saisie"])))
            if "payzen_site_id" in self.dict_parametres:
                session.add(models.Parametre(nom="PAYZEN_SITE_ID", parametre=str(self.dict_parametres["payzen_site_id"])))
            if "payzen_mode" in self.dict_parametres:
                session.add(models.Parametre(nom="PAYZEN_MODE", parametre=str(self.dict_parametres["payzen_mode"])))
            if "payzen_certificat_test" in self.dict_parametres:
                session.add(models.Parametre(nom="PAYZEN_CERTIFICAT_TEST", parametre=str(self.dict_parametres["payzen_certificat_test"])))
            if "payzen_certificat_production" in self.dict_parametres:
                session.add(models.Parametre(nom="PAYZEN_CERTIFICAT_PRODUCTION", parametre=str(self.dict_parametres["payzen_certificat_production"])))
            if "payzen_echelonnement" in self.dict_parametres:
                session.add(models.Parametre(nom="PAYZEN_ECHELONNEMENT", parametre=str(self.dict_parametres["payzen_echelonnement"])))

        session.add(models.Parametre(nom="ACCUEIL_TITRE", parametre=self.dict_parametres["accueil_titre"]))
        session.add(models.Parametre(nom="ACCUEIL_BIENVENUE", parametre=self.dict_parametres["accueil_bienvenue"]))
        session.add(models.Parametre(nom="ACCUEIL_MESSAGES_AFFICHER", parametre=str(self.dict_parametres["accueil_messages_afficher"])))
        session.add(models.Parametre(nom="ACCUEIL_ETAT_DOSSIER_AFFICHER", parametre=str(self.dict_parametres["accueil_etat_dossier_afficher"])))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_AFFICHER", parametre=str(self.dict_parametres["renseignements_afficher"])))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_INTRO", parametre=self.dict_parametres["renseignements_intro"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_MODIFIER", parametre=str(self.dict_parametres["renseignements_modifier"])))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ADULTE_NOM", parametre=self.dict_parametres["renseignements_adulte_nom"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ENFANT_NOM", parametre=self.dict_parametres["renseignements_enfant_nom"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ADULTE_NAISSANCE", parametre=self.dict_parametres["renseignements_adulte_naissance"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ENFANT_NAISSANCE", parametre=self.dict_parametres["renseignements_enfant_naissance"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ADRESSE", parametre=self.dict_parametres["renseignements_adresse"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ADULTE_COORDS", parametre=self.dict_parametres["renseignements_adulte_coords"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ENFANT_COORDS", parametre=self.dict_parametres["renseignements_enfant_coords"]))
        session.add(models.Parametre(nom="RENSEIGNEMENTS_ADULTE_PROFESSION", parametre=self.dict_parametres["renseignements_adulte_profession"]))
        session.add(models.Parametre(nom="ACTIVITES_AFFICHER", parametre=str(self.dict_parametres["activites_afficher"])))
        session.add(models.Parametre(nom="ACTIVITES_INTRO", parametre=self.dict_parametres["activites_intro"]))
        session.add(models.Parametre(nom="ACTIVITES_AUTORISER_INSCRIPTION", parametre=str(self.dict_parametres["activites_autoriser_inscription"])))
        session.add(models.Parametre(nom="ACTIVITES_BLOQUER_COMPLET", parametre=str(self.dict_parametres["activites_bloquer_complet"])))
        session.add(models.Parametre(nom="RESERVATIONS_AFFICHER", parametre=str(self.dict_parametres["reservations_afficher"])))
        session.add(models.Parametre(nom="RESERVATIONS_INTRO", parametre=self.dict_parametres["reservations_intro"]))
        session.add(models.Parametre(nom="PLANNING_INTRO", parametre=self.dict_parametres["planning_intro"]))
        session.add(models.Parametre(nom="FACTURES_AFFICHER", parametre=str(self.dict_parametres["factures_afficher"])))
        session.add(models.Parametre(nom="FACTURES_INTRO", parametre=self.dict_parametres["factures_intro"]))
        session.add(models.Parametre(nom="FACTURES_DEMANDE_FACTURE", parametre=str(self.dict_parametres["factures_demande_facture"])))
        session.add(models.Parametre(nom="FACTURES_PREFACTURATION", parametre=str(self.dict_parametres["factures_prefacturation"])))
        session.add(models.Parametre(nom="FACTURES_AFFICHER_SOLDE_TOTAL", parametre=str(self.dict_parametres["factures_afficher_solde_total"])))
        session.add(models.Parametre(nom="FACTURES_AFFICHER_SOLDE_DETAIL", parametre=str(self.dict_parametres["factures_afficher_solde_detail"])))
        session.add(models.Parametre(nom="REGLEMENTS_AFFICHER", parametre=str(self.dict_parametres["reglements_afficher"])))
        session.add(models.Parametre(nom="REGLEMENTS_INTRO", parametre=self.dict_parametres["reglements_intro"]))
        session.add(models.Parametre(nom="REGLEMENTS_DEMANDE_RECU", parametre=str(self.dict_parametres["reglements_demande_recu"])))
        session.add(models.Parametre(nom="PIECES_AFFICHER", parametre=str(self.dict_parametres["pieces_afficher"])))
        session.add(models.Parametre(nom="PIECES_INTRO", parametre=self.dict_parametres["pieces_intro"]))
        session.add(models.Parametre(nom="PIECES_AUTORISER_TELECHARGEMENT", parametre=str(self.dict_parametres["pieces_autoriser_telechargement"])))
        session.add(models.Parametre(nom="PIECES_AUTORISER_UPLOAD", parametre=str(self.dict_parametres["pieces_autoriser_upload"])))
        session.add(models.Parametre(nom="COTISATIONS_AFFICHER", parametre=str(self.dict_parametres["cotisations_afficher"])))
        session.add(models.Parametre(nom="COTISATIONS_INTRO", parametre=self.dict_parametres["cotisations_intro"]))
        session.add(models.Parametre(nom="LOCATIONS_AFFICHER", parametre=str(self.dict_parametres["locations_afficher"])))
        session.add(models.Parametre(nom="LOCATIONS_INTRO", parametre=self.dict_parametres["locations_intro"]))
        session.add(models.Parametre(nom="LOCATIONS_PERIODE_SAISIE", parametre=self.dict_parametres["locations_periode_saisie"]))
        session.add(models.Parametre(nom="PLANNING_LOCATIONS_INTRO", parametre=self.dict_parametres["planning_locations_intro"]))
        session.add(models.Parametre(nom="LOCATIONS_HEURE_MIN", parametre=self.dict_parametres["locations_heure_min"]))
        session.add(models.Parametre(nom="LOCATIONS_HEURE_MAX", parametre=self.dict_parametres["locations_heure_max"]))
        session.add(models.Parametre(nom="LOCATIONS_AFFICHER_AUTRES_LOUEURS", parametre=str(self.dict_parametres["locations_afficher_autres_loueurs"])))
        session.add(models.Parametre(nom="HISTORIQUE_AFFICHER", parametre=str(self.dict_parametres["historique_afficher"])))
        session.add(models.Parametre(nom="HISTORIQUE_INTRO", parametre=self.dict_parametres["historique_intro"]))
        session.add(models.Parametre(nom="HISTORIQUE_DELAI", parametre=str(self.dict_parametres["historique_delai"])))
        session.add(models.Parametre(nom="CONTACT_AFFICHER", parametre=str(self.dict_parametres["contact_afficher"])))
        session.add(models.Parametre(nom="CONTACT_INTRO", parametre=self.dict_parametres["contact_intro"]))
        session.add(models.Parametre(nom="CONTACT_CARTE_AFFICHER", parametre=str(False))) #self.dict_parametres["contact_carte_afficher"])))
        session.add(models.Parametre(nom="MENTIONS_AFFICHER", parametre=str(self.dict_parametres["mentions_afficher"])))
        session.add(models.Parametre(nom="AIDE_AFFICHER", parametre=str(self.dict_parametres["aide_afficher"])))


        # Recherche des adresses emails des familles
        req = """SELECT rattachements.IDindividu, rattachements.IDfamille, mail
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDcategorie=1 AND titulaire=1 AND etat IS NULL AND deces<>1 AND mail IS NOT NULL;"""
        DB.ExecuterReq(req)
        listeEmails = DB.ResultatReq()
        dictEmailsFamilles = {}
        for IDindividu, IDfamille, mail in listeEmails:
            if (IDfamille in dictEmailsFamilles) == False :
                dictEmailsFamilles[IDfamille] = []
            dictEmailsFamilles[IDfamille].append(mail)

        # Création des users
        dictTitulaires = UTILS_Titulaires.GetTitulaires()

        req = """SELECT IDfamille, internet_actif, internet_identifiant, internet_mdp, email_recus, etat, prelevement_activation
        FROM familles;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeFamilles = []
        for IDfamille, internet_actif, internet_identifiant, internet_mdp, email_recus, etat, prelevement_activation in listeDonnees:
            listeFamilles.append({"ID" : IDfamille, "internet_actif" : internet_actif, "internet_identifiant" : internet_identifiant,
                                  "internet_mdp" : internet_mdp, "email_recus" : email_recus, "etat" : etat,
                                  "prelevement_activation": prelevement_activation})

        req = """SELECT IDutilisateur, internet_actif, internet_identifiant, internet_mdp, nom, prenom
        FROM utilisateurs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeUtilisateurs = []
        for IDutilisateur, internet_actif, internet_identifiant, internet_mdp, nom, prenom in listeDonnees:
            listeUtilisateurs.append({"ID": IDutilisateur, "internet_actif": internet_actif, "internet_identifiant": internet_identifiant,
                                  "internet_mdp": internet_mdp, "nom": nom, "prenom" : prenom, "etat" : None})


        listeIDfamille = []
        for profil, listeDonnees in [("famille", listeFamilles), ("utilisateur", listeUtilisateurs)]:
            for dictDonnee in listeDonnees :
                if dictDonnee["internet_identifiant"] not in ("", None) and dictDonnee["internet_mdp"] not in ("", None) :

                    if profil == "famille" :
                        IDfamille = dictDonnee["ID"]
                        IDutilisateur = None
                    if profil == "utilisateur" :
                        IDutilisateur = dictDonnee["ID"]
                        IDfamille = None

                    # Recherche du nom complet
                    if profil == "famille" :
                        nomDossier = cryptage.encrypt(dictTitulaires[IDfamille]["titulairesSansCivilite"])
                    if profil == "utilisateur" :
                        nomDossier = u"%s %s" % (dictDonnee["prenom"], dictDonnee["nom"])

                    # Cryptage du mot de passe
                    if "custom" not in dictDonnee["internet_mdp"]:
                        mdp = dictDonnee["internet_mdp"]
                        if mdp.startswith("#@#"):
                            mdp = UTILS_Internet.DecrypteMDP(mdp, IDfichier=IDfichier)
                        dictDonnee["internet_mdp"] = SHA256.new(mdp.encode('utf-8')).hexdigest()

                    # Génération du session_token
                    session_token = "%s-%d-%s-%s-%d" % (profil, dictDonnee["ID"], dictDonnee["internet_identifiant"], dictDonnee["internet_mdp"][:20], dictDonnee["internet_actif"])

                    # Récupération de l email de recu
                    email = ""
                    if IDfamille in dictEmailsFamilles:
                        # Sélectionne les 3 premières adresses email de la famille
                        email = ";".join(dictEmailsFamilles[IDfamille][:3])
                        email = cryptage.encrypt(email)

                    # Autre paramètres
                    liste_parametres = []
                    if profil == "famille":
                        prelevement_auto = dictDonnee.get("prelevement_activation", 0)
                        if not prelevement_auto:
                            prelevement_auto = 0
                        liste_parametres.append("prelevement_auto==%d" % prelevement_auto)
                    parametres = "##".join(liste_parametres)

                    # Si famille archivée ou effacée
                    if dictDonnee["etat"] != None:
                        dictDonnee["internet_actif"] = 0

                    if profil == "famille" and dictDonnee["internet_actif"] == 1 :
                        listeIDfamille.append(IDfamille)
                        
                    if dictDonnee["internet_actif"] == 0 :
                        # Anonymise les infos des comptes désactivés
                        nomDossier = "XXX"
                        email = ""

                    # Création du user
                    m = models.User(IDuser=None, identifiant=dictDonnee["internet_identifiant"], cryptpassword=dictDonnee["internet_mdp"],
                                    nom=nomDossier, email=email, role=profil, IDfamille=IDfamille, IDutilisateur=IDutilisateur, actif=dictDonnee["internet_actif"],
                                    session_token=session_token)
                    if hasattr(models.User, "parametres"):
                        m.parametres = parametres
                    session.add(m)


        # Création des factures
        self.Pulse_gauge()

        if self.dict_parametres["factures_selection"] == 0 :
            conditions_factures = ""
        else :
            nbre_mois = self.dict_parametres["factures_selection"]
            date_limite = datetime.date.today() + relativedelta.relativedelta(months=-nbre_mois)
            conditions_factures = "WHERE factures.date_edition >= '%s'" % date_limite

        # Récupération des totaux des prestations pour chaque facture
        req = """
        SELECT
        prestations.IDfacture, SUM(prestations.montant)
        FROM prestations
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        %s
        GROUP BY prestations.IDfacture
        ;""" % conditions_factures
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPrestations = {}
        for IDfacture, totalPrestations in listeDonnees :
            if IDfacture != None :
                dictPrestations[IDfacture] = totalPrestations

        # Récupération des factures
        req = """
        SELECT factures.IDfacture, factures.IDprefixe, factures_prefixes.prefixe, factures.numero, factures.IDcompte_payeur,
        factures.date_edition, factures.date_echeance, factures.IDutilisateur,
        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
        factures.IDregie,
        comptes_payeurs.IDfamille, factures.etat
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        %s
        ORDER BY factures.date_edition
        ;""" % conditions_factures
        DB.ExecuterReq(req)
        listeFactures = DB.ResultatReq()

        # Récupération de la ventilation
        req = """
        SELECT prestations.IDfacture, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = prestations.IDcompte_payeur
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        %s
        GROUP BY prestations.IDfacture
        ;""" % conditions_factures
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()
        dictVentilation = {}
        for IDfacture, montantVentilation in listeVentilation :
            if IDfacture != None :
                dictVentilation[IDfacture] = montantVentilation

        for IDfacture, IDprefixe, prefixe, numero, IDcompte_payeur, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, IDregie, IDfamille, etat in listeFactures :
            if IDfamille in listeIDfamille :
                if numero == None : numero = 0
                if IDprefixe != None :
                    # On supprime le tiret séparateur du préfixe et du numéro de facture pour TIPI (le tiret est proscrit)
                    if "paiement_ligne_systeme" in self.dict_parametres and (self.dict_parametres["paiement_ligne_systeme"] == 1 or self.dict_parametres["paiement_ligne_systeme"] == 2) :
                        numero = u"%s%06d" % (prefixe, numero)
                    else :
                        numero = u"%s-%06d" % (prefixe, numero)
                else :
                    numero = u"%06d" % numero

                date_edition = UTILS_Dates.DateEngEnDateDD(date_edition)
                date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
                date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
                date_echeance = UTILS_Dates.DateEngEnDateDD(date_echeance)
                total = FloatToDecimal(total)
                if IDfacture in dictVentilation :
                    totalVentilation = FloatToDecimal(dictVentilation[IDfacture])
                else :
                    totalVentilation = FloatToDecimal(0.0)
                if IDfacture in dictPrestations :
                    totalPrestations = FloatToDecimal(dictPrestations[IDfacture])
                else :
                    totalPrestations = FloatToDecimal(0.0)
                solde_actuel = totalPrestations - totalVentilation

                m = models.Facture(IDfacture=IDfacture, IDfamille=IDfamille, numero=numero, date_edition=date_edition, date_debut=date_debut,\
                            date_fin=date_fin, montant=float(totalPrestations), montant_regle=float(totalVentilation), montant_solde=float(solde_actuel), IDregie=IDregie)
                session.add(m)

        liste_tables_modifiees.append("factures")

        # Création des règlements
        self.Pulse_gauge()

        if self.dict_parametres["reglements_selection"] == 0 :
            conditions_reglements = ""
        else :
            nbre_mois = self.dict_parametres["reglements_selection"]
            date_limite = datetime.date.today() + relativedelta.relativedelta(months=-nbre_mois)
            conditions_reglements = "WHERE reglements.date >= '%s'" % date_limite

        req = """SELECT
        reglements.IDreglement, comptes_payeurs.IDfamille, reglements.date, modes_reglements.label,
        reglements.numero_piece, reglements.montant, depots.date
        FROM reglements
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        %s
        GROUP BY reglements.IDreglement
        ;""" % conditions_reglements
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()

        for IDreglement, IDfamille, date, mode, numero, montant, date_encaissement in listeReglements :
            if IDfamille in listeIDfamille :
                date = UTILS_Dates.DateEngEnDateDD(date)
                date_encaissement = UTILS_Dates.DateEngEnDateDD(date_encaissement)
                if numero not in ("", None) :
                    numero = "****%s" % numero[3:]
                m = models.Reglement(IDreglement=IDreglement, IDfamille=IDfamille, date=date, mode=mode,
                                numero=numero, montant=montant, date_encaissement=date_encaissement)
                session.add(m)

        liste_tables_modifiees.append("reglements")

        # Création des pièces manquantes
        self.Pulse_gauge()

        dictPieces = UTILS_Pieces_manquantes.GetListePiecesManquantes(dateReference=datetime.date.today(), concernes=True)
        for IDfamille, dictValeurs in dictPieces.items() :
            for IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide, label in dictValeurs["liste"] :
                m = models.Piece_manquante(IDfamille=IDfamille, IDtype_piece=IDtype_piece, IDindividu=IDindividu, nom=cryptage.encrypt(label))
                session.add(m)

        liste_tables_modifiees.append("pieces_manquantes")

        # Création des types de pièces
        self.Pulse_gauge()

        # Recherche des documents associées aux types de pièces
        DB2 = GestionDB.DB(suffixe="DOCUMENTS")
        req = "SELECT IDdocument, IDtype_piece, document, type, label, last_update FROM documents WHERE IDtype_piece IS NOT NULL AND document IS NOT NULL;"
        DB2.ExecuterReq(req)
        listeDocuments = DB2.ResultatReq()
        DB2.Close()
        dictDocuments = {}
        for IDdocument, IDtype_piece, document, extension, label, last_update in listeDocuments :
            if IDtype_piece not in dictDocuments :
                dictDocuments[IDtype_piece] = []
            dictDocuments[IDtype_piece].append({"IDdocument" : IDdocument, "document" : document, "extension" : extension, "label" : label, "last_update" : last_update})

        # Recherche des types de pièces
        req = """
        SELECT IDtype_piece, nom, public
        FROM types_pieces;"""
        DB.ExecuterReq(req)
        listeTypesPieces = DB.ResultatReq()
        for IDtype_piece, nom, public in listeTypesPieces :

            # Recherche de documents associés
            fichiers = []
            if IDtype_piece in dictDocuments :
                for dict_document in dictDocuments[IDtype_piece] :

                    nomFichier = "document%d.%s" % (dict_document["IDdocument"], dict_document["extension"])
                    fichiers.append(u"%s;%s" % (dict_document["label"], nomFichier))

                    if dict_document["last_update"] > last_synchro or full_synchro == True :
                        cheminFichier = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
                        buffer = dict_document["document"]
                        fichier = open(cheminFichier, "wb")
                        fichier.write(buffer)
                        fichier.close()

                        # Upload de la pièce
                        print("Upload du fichier", nomFichier)
                        self.UploadFichier(ftp=ftp, nomFichierComplet=cheminFichier, repDest="application/static/pieces")

            m = models.Type_piece(IDtype_piece=IDtype_piece, nom=nom, public=public, fichiers=u"##".join(fichiers))
            session.add(m)

        liste_tables_modifiees.append("types_pieces")

        # Création des cotisations manquantes
        self.Pulse_gauge()

        dictCotisations = UTILS_Cotisations_manquantes.GetListeCotisationsManquantes(dateReference=datetime.date.today(), concernes=True)
        for IDfamille, dictValeurs in dictCotisations.items() :
            for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label in dictValeurs["liste"] :
                m = models.Cotisation_manquante(IDfamille=IDfamille, IDindividu=IDindividu, IDtype_cotisation=IDtype_cotisation, nom=label)
                session.add(m)

        liste_tables_modifiees.append("cotisations_manquantes")

        # Création de la liste des cotisations
        if self.dict_parametres["cotisations_selection"] == 0 :
            conditions_cotisations = ""
        else :
            nbre_mois = self.dict_parametres["cotisations_selection"]
            date_limite = datetime.date.today() + relativedelta.relativedelta(months=-nbre_mois)
            conditions_cotisations = "WHERE cotisations.date_fin >= '%s'" % date_limite

        req = """SELECT IDcotisation, IDfamille, cotisations.IDindividu, cotisations.numero, cotisations.date_debut, cotisations.date_fin, 
        types_cotisations.nom, unites_cotisations.nom, individus.prenom
        FROM cotisations 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        LEFT JOIN individus ON individus.IDindividu = cotisations.IDindividu
        %s
        ;""" % conditions_cotisations
        DB.ExecuterReq(req)
        listeCotisations = DB.ResultatReq()
        for IDcotisation, IDfamille, IDindividu, numero, date_debut, date_fin, nom_cotisation, nom_unite, prenom_individu in listeCotisations:
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            if prenom_individu != None :
                prenom_individu = cryptage.encrypt(prenom_individu)
            m = models.Cotisation(IDcotisation=IDcotisation, IDfamille=IDfamille, IDindividu=IDindividu, numero=numero, date_debut=date_debut,
                                  date_fin = date_fin, nom_cotisation=nom_cotisation, nom_unite=nom_unite, prenom_individu=prenom_individu)
            session.add(m)

        liste_tables_modifiees.append("cotisations")


        # Création des locations
        self.Pulse_gauge()

        if self.dict_parametres["locations_afficher"]:

            # Création de la liste des catégories de produits
            req = """SELECT IDcategorie, nom FROM produits_categories;"""
            DB.ExecuterReq(req)
            listeCatProduits = DB.ResultatReq()
            for IDcategorie, nom in listeCatProduits:
                m = models.Categorie_produit(IDcategorie=IDcategorie, nom=nom)
                session.add(m)

            liste_tables_modifiees.append("categories_produits")

            # Création de la liste des produits
            req = """SELECT IDproduit, produits.IDcategorie, produits.nom, quantite, montant, produits_categories.nom, activation_partage
            FROM produits
            LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
            ;"""
            DB.ExecuterReq(req)
            listeProduits = DB.ResultatReq()
            for IDproduit, IDcategorie, nom, quantite, montant, nom_categorie, activation_partage in listeProduits:
                m = models.Produit(IDproduit=IDproduit, IDcategorie=IDcategorie, nom=nom, quantite=quantite, montant=montant, nom_categorie=nom_categorie, activation_partage=activation_partage)
                session.add(m)

            liste_tables_modifiees.append("produits")

            # Création de la liste des locations
            if self.dict_parametres["locations_selection"] == 0 :
                conditions_locations = ""
            else :
                nbre_mois = self.dict_parametres["locations_selection"]
                date_limite = datetime.date.today() + relativedelta.relativedelta(months=-nbre_mois)
                conditions_locations = "WHERE locations.date_fin >= '%s'" % date_limite

            req = """SELECT IDlocation, IDfamille, IDproduit, date_saisie, date_debut, date_fin, quantite, partage, description
            FROM locations 
            %s
            ;""" % conditions_locations
            DB.ExecuterReq(req)
            listeLocations = DB.ResultatReq()
            for IDlocation, IDfamille, IDproduit, date_saisie, date_debut, date_fin, quantite, partage, description in listeLocations:
                date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
                date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
                m = models.Location(IDlocation=IDlocation, IDfamille=IDfamille, IDproduit=IDproduit, date_debut=date_debut, date_fin=date_fin, quantite=quantite, partage=partage, description=description)
                session.add(m)

            liste_tables_modifiees.append("locations")

        # Création des activités
        self.Pulse_gauge()

        req = """
        SELECT IDactivite, nom, portail_inscriptions_affichage, portail_inscriptions_date_debut,
        portail_inscriptions_date_fin, portail_reservations_affichage, portail_unites_multiples,
        portail_reservations_limite, portail_reservations_absenti, nbre_inscrits_max
        FROM activites;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        dict_activites = {}
        for IDactivite, nom, inscriptions_affichage, inscriptions_date_debut, inscriptions_date_fin, reservations_affichage, unites_multiples, portail_reservations_limite, portail_reservations_absenti, nbre_inscrits_max in listeActivites :
            inscriptions_date_debut = UTILS_Dates.DateEngEnDateDDT(inscriptions_date_debut)
            inscriptions_date_fin = UTILS_Dates.DateEngEnDateDDT(inscriptions_date_fin)

            m = models.Activite(IDactivite=IDactivite, nom=nom, inscriptions_affichage=inscriptions_affichage, \
                         inscriptions_date_debut=inscriptions_date_debut, inscriptions_date_fin=inscriptions_date_fin, \
                         reservations_affichage=reservations_affichage, unites_multiples=unites_multiples, \
                         reservations_limite=portail_reservations_limite, reservations_absenti=portail_reservations_absenti,
                         nbre_inscrits_max=nbre_inscrits_max,
                         )
            session.add(m)

            dict_activites[IDactivite] = {
                "IDactivite" : IDactivite, "nom" : nom, "inscriptions_affichage" : inscriptions_affichage, \
                 "inscriptions_date_debut" : inscriptions_date_debut, "inscriptions_date_fin" : inscriptions_date_fin, \
                 "reservations_affichage" : reservations_affichage, "unites_multiples" : unites_multiples, \
                 "reservations_limite" : portail_reservations_limite, "reservations_absenti" : portail_reservations_absenti,
                 "nbre_inscrits_max" : nbre_inscrits_max,
                }

        liste_tables_modifiees.append("activites")

        # Création des groupes
        self.Pulse_gauge()

        req = """
        SELECT IDgroupe, IDactivite, nom, ordre, nbre_inscrits_max
        FROM groupes;"""
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()

        for IDgroupe, IDactivite, nom, ordre, nbre_inscrits_max in listeGroupes :
            m = models.Groupe(IDgroupe=IDgroupe, nom=nom, IDactivite=IDactivite, ordre=ordre, nbre_inscrits_max=nbre_inscrits_max)
            session.add(m)

        liste_tables_modifiees.append("groupes")

        # Création des individus
        self.Pulse_gauge()

        champs_individus = ["IDrattachement", "rattachements.IDindividu", "rattachements.IDfamille", "titulaire", "IDcategorie",
                            "IDcivilite", "nom", "prenom", "date_naiss", "cp_naiss", "ville_naiss", "adresse_auto", "rue_resid", "cp_resid", "ville_resid",
                            "tel_domicile", "tel_mobile", "mail", "profession", "employeur", "travail_tel", "travail_mail"]
        req = """SELECT %s
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE (IDcategorie=2 OR (IDcategorie=1 AND titulaire=1)) AND etat IS NULL AND deces<>1;""" % ", ".join(champs_individus)
        DB.ExecuterReq(req)
        listeRattachements = DB.ResultatReq()
        for donnees in listeRattachements :
            dictTemp = {}
            for index in range(0, len(champs_individus)) :
                champ = champs_individus[index]
                valeur = donnees[index]

                # Formatage date de naissance
                if champ == "date_naiss" :
                    valeur = UTILS_Dates.DateEngEnDateDD(valeur)
                    if valeur != None :
                        valeur = str(valeur)

                # Renseignements à masquer
                if champ == "nom" and dictTemp["IDcategorie"] == 1 and (self.dict_parametres["renseignements_adulte_nom"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ == "nom" and dictTemp["IDcategorie"] == 2 and (self.dict_parametres["renseignements_enfant_nom"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ in ("cp_naiss", "ville_naiss") and dictTemp["IDcategorie"] == 1 and (self.dict_parametres["renseignements_adulte_naissance"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ in ("cp_naiss", "ville_naiss") and dictTemp["IDcategorie"] == 2 and (self.dict_parametres["renseignements_enfant_naissance"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ in ("tel_domicile", "tel_mobile", "mail") and dictTemp["IDcategorie"] == 1 and (self.dict_parametres["renseignements_adulte_coords"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ in ("tel_domicile", "tel_mobile", "mail") and dictTemp["IDcategorie"] == 2 and (self.dict_parametres["renseignements_enfant_coords"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ in ("adresse_auto", "rue_resid", "cp_resid", "ville_resid") and (self.dict_parametres["renseignements_adresse"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False) :
                    valeur = None
                if champ in ("profession", "employeur", "travail_tel", "travail_mail") and (self.dict_parametres["renseignements_adulte_profession"] == "masquer" or self.dict_parametres["renseignements_afficher"] == False):
                    valeur = None

                # Cryptage des données
                if champ in ("nom", "prenom", "date_naiss", "cp_naiss", "ville_naiss", "tel_domicile", "tel_mobile", "mail", "rue_resid","cp_resid", "ville_resid", "profession", "employeur", "travail_tel", "travail_mail"):
                    valeur = cryptage.encrypt(valeur)

                dictTemp[champ] = valeur

            if dictTemp["rattachements.IDfamille"] in listeIDfamille :
                m = models.Individu(IDindividu=dictTemp["rattachements.IDindividu"], IDfamille=dictTemp["rattachements.IDfamille"], IDcategorie=dictTemp["IDcategorie"],
                                    nom=dictTemp["nom"], prenom=dictTemp["prenom"], IDcivilite=dictTemp["IDcivilite"],
                                    date_naiss=dictTemp["date_naiss"], cp_naiss=dictTemp["cp_naiss"], ville_naiss=dictTemp["ville_naiss"],
                                    adresse_auto=dictTemp["adresse_auto"], rue_resid=dictTemp["rue_resid"], cp_resid=dictTemp["cp_resid"], ville_resid=dictTemp["ville_resid"],
                                    tel_domicile=dictTemp["tel_domicile"], tel_mobile=dictTemp["tel_mobile"], mail=dictTemp["mail"],
                                    profession=dictTemp["profession"], employeur=dictTemp["employeur"],
                                    travail_tel=dictTemp["travail_tel"], travail_mail=dictTemp["travail_mail"],
                                    )
                session.add(m)

        liste_tables_modifiees.append("individus")

        # Création des inscriptions
        self.Pulse_gauge()

        req = """SELECT IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, date_desinscription
        FROM inscriptions
        WHERE inscriptions.statut='ok';"""
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        for IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, date_desinscription in listeInscriptions :
            if True :#IDfamille in listeIDfamille : Modifié pour connaître le nombre d'inscrits par activité
                date_desinscription = UTILS_Dates.DateEngEnDateDD(date_desinscription)
                m = models.Inscription(IDinscription=IDinscription, IDindividu=IDindividu, IDfamille=IDfamille, IDactivite=IDactivite, IDgroupe=IDgroupe, date_desinscription=date_desinscription)
                session.add(m)

        liste_tables_modifiees.append("inscriptions")

        # Création des unités
        self.Pulse_gauge()

        req = """SELECT IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre
        FROM portail_unites
        ORDER BY IDactivite, ordre;"""
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        for IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre in listeUnites :
            if IDactivite in dict_activites:
                m = models.Unite(IDunite=IDunite, nom=nom, IDactivite=IDactivite, unites_principales=unites_principales, \
                          unites_secondaires=unites_secondaires, ordre=ordre)
                session.add(m)

        liste_tables_modifiees.append("unites")

        # Création des périodes
        self.Pulse_gauge()

        req = """SELECT IDperiode, IDactivite, nom, date_debut, date_fin, affichage, affichage_date_debut, affichage_date_fin, introduction, prefacturation
        FROM portail_periodes
        WHERE affichage=1;"""
        DB.ExecuterReq(req)
        listePeriodes = DB.ResultatReq()
        dict_dates_activites = {}
        dict_periodes = {}
        for IDperiode, IDactivite, nom, date_debut, date_fin, affichage, affichage_date_debut, affichage_date_fin, introduction, prefacturation in listePeriodes :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            affichage_date_debut = UTILS_Dates.DateEngEnDateDDT(affichage_date_debut)
            affichage_date_fin = UTILS_Dates.DateEngEnDateDDT(affichage_date_fin)

            m = models.Periode(IDperiode=IDperiode, IDactivite=IDactivite, nom=nom, date_debut=date_debut, date_fin=date_fin, \
                                affichage_date_debut=affichage_date_debut, affichage_date_fin=affichage_date_fin, introduction=introduction,
                                prefacturation=prefacturation)
            session.add(m)

            # Mémorise les activités pour lesquelles il y a des périodes...
            if affichage_date_fin == None or date_fin >= datetime.date.today() or affichage_date_fin >= datetime.datetime.now():
                if IDactivite not in dict_dates_activites :
                    dict_dates_activites[IDactivite] = {"date_min" : None, "date_max" : None}
                if dict_dates_activites[IDactivite]["date_min"] == None or dict_dates_activites[IDactivite]["date_min"] > date_debut :
                    dict_dates_activites[IDactivite]["date_min"] = date_debut
                if dict_dates_activites[IDactivite]["date_max"] == None or dict_dates_activites[IDactivite]["date_max"] < date_fin :
                    dict_dates_activites[IDactivite]["date_max"] = date_fin

            # Mémorise période pour préfacturation
            if prefacturation == 1 :
                if (IDactivite in dict_periodes) == False :
                    dict_periodes[IDactivite] = []
                dict_periodes[IDactivite].append({"date_debut": date_debut, "date_fin": date_fin, "IDperiode": IDperiode})

        liste_tables_modifiees.append("periodes")

        # Création de la condition pour les ouvertures et les consommations
        listeConditions = []
        for IDactivite, periode in dict_dates_activites.items() :
            listeConditions.append("(IDactivite=%d AND date>='%s' AND date<='%s')" % (IDactivite, periode["date_min"], periode["date_max"]))
        texteConditions = "(%s)" % " OR ".join(listeConditions)

        # Création des ouvertures
        self.Pulse_gauge()

        if len(listeConditions) > 0 :

            req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe, date
            FROM ouvertures
            WHERE %s;""" % texteConditions
            DB.ExecuterReq(req)
            listeOuvertures = DB.ResultatReq()
            for IDouverture, IDactivite, IDunite, IDgroupe, date in listeOuvertures :
                date = UTILS_Dates.DateEngEnDateDD(date)
                m = models.Ouverture(date=date, IDunite=IDunite, IDgroupe=IDgroupe)
                session.add(m)

            liste_tables_modifiees.append("ouvertures")

            # req = """SELECT IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, heure_debut, heure_fin
            # FROM evenements
            # WHERE %s;""" % texteConditions
            # DB.ExecuterReq(req)
            # listeEvenements = DB.ResultatReq()
            # for IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, heure_debut, heure_fin in listeEvenements :
            #     date = UTILS_Dates.DateEngEnDateDD(date)
            #     try :
            #         m = models.Evenement(IDevenement=IDevenement, IDactivite=IDactivite, date=date, IDunite=IDunite, IDgroupe=IDgroupe, nom=nom,
            #                              description=description, heure_debut=heure_debut, heure_fin=heure_fin)
            #         session.add(m)
            #     except Exception, err:
            #         print (err,)

            req = """SELECT type, nom, jour, mois, annee
            FROM jours_feries ;"""
            DB.ExecuterReq(req)
            listeFeries = DB.ResultatReq()
            for typeFerie, nom, jour, mois, annee in listeFeries:
                m = models.Ferie(type=typeFerie, nom=nom, jour=jour, mois=mois, annee=annee)
                session.add(m)

            liste_tables_modifiees.append("feries")

        # Création des consommations
        self.Pulse_gauge()

        if len(listeConditions) > 0 :

            req = """SELECT IDconso, date, IDunite, IDinscription, etat, IDevenement
            FROM consommations
            WHERE %s;""" % texteConditions
            DB.ExecuterReq(req)
            listeConsommations = DB.ResultatReq()
            for IDconso, date, IDunite, IDinscription, etat, IDevenement in listeConsommations :
                date = UTILS_Dates.DateEngEnDateDD(date)
                try :
                    m = models.Consommation(date=date, IDunite=IDunite, IDinscription=IDinscription, etat=etat, IDevenement=IDevenement)
                except Exception as err:
                    print((err,))
                    m = models.Consommation(date=date, IDunite=IDunite, IDinscription=IDinscription, etat=etat)
                session.add(m)

            liste_tables_modifiees.append("consommations")


            # Création de la pré-facturation

            # Récupère la ventilation
            req = """SELECT ventilation.IDprestation, SUM(ventilation.montant)
            FROM ventilation
            LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
            WHERE IDfacture IS NULL AND %s
            GROUP BY prestations.IDPrestation;""" % texteConditions
            DB.ExecuterReq(req)
            listeVentilations = DB.ResultatReq()
            dict_ventilation = {}
            for IDprestation, montant in listeVentilations:
                dict_ventilation[IDprestation] = FloatToDecimal(montant)

            # Récupère les prestations
            req = """SELECT IDprestation, IDfamille, IDactivite, date, montant
            FROM prestations
            WHERE IDfacture IS NULL AND %s;""" % texteConditions
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            dict_prestations = {}
            for IDprestation, IDfamille, IDactivite, date, montant in listePrestations:
                date = UTILS_Dates.DateEngEnDateDD(date)
                montant = FloatToDecimal(montant)
                if (IDfamille in dict_prestations) == False :
                    dict_prestations[IDfamille] = {}

                # Recherche la période correspondante
                IDperiode = None
                if IDactivite in dict_periodes:
                    for dictPeriode in dict_periodes[IDactivite]:
                        if date >= dictPeriode["date_debut"] and date <= dictPeriode["date_fin"]:
                            IDperiode = dictPeriode["IDperiode"]

                if IDperiode != None :
                    if (IDperiode in dict_prestations[IDfamille]) == False :
                        dict_prestations[IDfamille][IDperiode] = {"montant" : FloatToDecimal(0.0), "montant_regle" : FloatToDecimal(0.0), "montant_solde" : FloatToDecimal(0.0)}
                    dict_prestations[IDfamille][IDperiode]["montant"] += montant
                    dict_prestations[IDfamille][IDperiode]["montant_regle"] += dict_ventilation.get(IDprestation, FloatToDecimal(0.0))
                    dict_prestations[IDfamille][IDperiode]["montant_solde"] = dict_prestations[IDfamille][IDperiode]["montant"] - dict_prestations[IDfamille][IDperiode]["montant_regle"]

            # Enregistrement de la table prefacturation
            for IDfamille, dictPeriode in dict_prestations.items():
                for IDperiode, dict_montants in dictPeriode.items():
                    m = models.Prefacturation(IDfamille=IDfamille, IDperiode=IDperiode, montant=float(dict_montants["montant"]),
                                              montant_regle=float(dict_montants["montant_regle"]), montant_solde=float(dict_montants["montant_solde"]))
                    session.add(m)

            liste_tables_modifiees.append("prefacturation")

        # Création des actions
        self.Pulse_gauge()

        req = """SELECT IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique, reponse, IDpaiement, ventilation
        FROM portail_actions
        WHERE horodatage>='%s';""" % (datetime.datetime.now() - datetime.timedelta(days=(self.dict_parametres["historique_delai"]+1)*30))
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        for IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique, reponse, IDpaiement, ventilation in listeActions :
            if IDfamille in listeIDfamille :
                traitement_date = UTILS_Dates.DateEngEnDateDD(traitement_date)
                horodatage = UTILS_Dates.DateEngEnDateDDT(horodatage)
                m = models.Action(horodatage=horodatage, IDfamille=IDfamille, IDindividu=IDindividu, categorie=categorie, action=action, description=description,
                                  commentaire=commentaire, parametres=parametres, etat=etat, traitement_date=traitement_date, IDperiode=IDperiode, ref_unique=ref_unique,
                                  reponse=reponse, IDpaiement=IDpaiement, ventilation=ventilation)
                session.add(m)

        liste_tables_modifiees.append("actions")

        # Création des messages
        req = """SELECT IDmessage, titre, texte, affichage_date_debut, affichage_date_fin
        FROM portail_messages
        ORDER BY titre;"""
        DB.ExecuterReq(req)
        listeMessages = DB.ResultatReq()
        for IDmessage, titre, texte, affichage_date_debut, affichage_date_fin in listeMessages :
            affichage_date_debut = UTILS_Dates.DateEngEnDateDDT(affichage_date_debut)
            affichage_date_fin = UTILS_Dates.DateEngEnDateDDT(affichage_date_fin)

            m = models.Message(IDmessage=IDmessage, titre=titre, texte=texte, \
                               affichage_date_debut=affichage_date_debut, affichage_date_fin=affichage_date_fin)
            session.add(m)

        liste_tables_modifiees.append("messages")

        # Création des régies
        req = """SELECT IDregie, nom, numclitipi, email_regisseur
        FROM factures_regies;"""
        DB.ExecuterReq(req)
        listeRegies = DB.ResultatReq()
        for IDregie, nom, numclitipi, email_regisseur in listeRegies :
            m = models.Regie(IDregie=IDregie, nom=nom, numclitipi=numclitipi, email_regisseur=email_regisseur)
            session.add(m)

        liste_tables_modifiees.append("regies")

        # Recherche des pages
        last_update_pages = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="last_update_pages")
        if last_update_pages == None or last_update_pages > last_synchro or full_synchro == True:

            req = """SELECT IDpage, titre, couleur, ordre
            FROM portail_pages;"""
            DB.ExecuterReq(req)
            listePages = DB.ResultatReq()
            for IDpage, titre, couleur, ordre in listePages :
                m = models.Page(IDpage=IDpage, titre=titre, couleur=couleur, ordre=ordre)
                session.add(m)

            liste_tables_modifiees.append("pages")

            req = """SELECT IDbloc, IDpage, titre, couleur, categorie, ordre, parametres
            FROM portail_blocs;"""
            DB.ExecuterReq(req)
            listeBlocs = DB.ResultatReq()
            for IDbloc, IDpage, titre, couleur, categorie, ordre, parametres in listeBlocs :
                m = models.Bloc(IDbloc=IDbloc, IDpage=IDpage, titre=titre, couleur=couleur, categorie=categorie, ordre=ordre, parametres=parametres)
                session.add(m)

            liste_tables_modifiees.append("blocs")

            req = """SELECT IDelement, IDbloc, ordre, titre, categorie, date_debut, date_fin, parametres, texte_html
            FROM portail_elements;"""
            DB.ExecuterReq(req)
            listeElements = DB.ResultatReq()
            for IDelement, IDbloc, ordre, titre, categorie, date_debut, date_fin, parametres, texte_html in listeElements :
                date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
                date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
                if texte_html != None :
                    if six.PY3:
                        if isinstance(texte_html, str):
                            texte_html = texte_html.encode('utf-8')
                        texte_html = texte_html.replace(b"<img ", b"<img class='img-responsive' ")
                    else:
                        texte_html = texte_html.replace("<img ", "<img class='img-responsive' ")
                m = models.Element(IDelement=IDelement, IDbloc=IDbloc, ordre=ordre, titre=titre, categorie=categorie, date_debut=date_debut, date_fin=date_fin,
                                parametres=parametres, texte_html=texte_html)
                session.add(m)

            liste_tables_modifiees.append("elements")




        # Mémorise les tables modifiées qui seront à importées dans Connecthys
        texte_tables_modifiees = ";".join(liste_tables_modifiees)
        session.add(models.Parametre(nom="tables_modifiees_synchro", parametre=texte_tables_modifiees))

        # Fermeture de la base de données Noethys
        DB.Close()

        # Commit
        self.log.EcritLog(_(u"Enregistrement des données à exporter..."))
        self.Pulse_gauge()
        session.commit()

        # Compression du fichier
        self.log.EcritLog(_(u"Compression du fichier d'export..."))
        self.Pulse_gauge()

        nomFichierZIP = nomFichierDB.replace(".db", ".zip")
        fichierZip = zipfile.ZipFile(nomFichierZIP, "w", compression=zipfile.ZIP_DEFLATED)
        fichierZip.write(nomFichierDB, os.path.basename(nomFichierDB))
        fichierZip.close()
        #os.remove(nomFichierDB)

        # Cryptage du fichier
        self.log.EcritLog(_(u"Cryptage du fichier d'export..."))
        self.Pulse_gauge()

        cryptage_mdp = self.dict_parametres["secret_key"][:10] #base64.b64decode(password)
        nomFichierCRYPT = nomFichierZIP.replace(".zip", ".crypt")
        ancienne_methode = UTILS_Customize.GetValeur("version_cryptage", "connecthys", "1", ajouter_si_manquant=False) in ("1", None)
        UTILS_Cryptage_fichier.CrypterFichier(nomFichierZIP, nomFichierCRYPT, cryptage_mdp, ancienne_methode=ancienne_methode)
        os.remove(nomFichierZIP)

        # Pour contrer le bug de Pickle dans le cryptage
        fichier2 = open(nomFichierCRYPT, "rb")
        content = fichier2.read()
        # TODO: comprendre pourquoi quand appele via synchro arrrière plan ou vian synchro du bouton outils du panel c'est Utils.UTILS_Cryptage
        #       et via le DLG et le bouton Synchroniser maintenant c'est UTILS_Cryptage
        #       WTF !!!!!
        content = content.replace(b"Utils.UTILS_Cryptage_fichier", b"cryptage")
        content = content.replace(b"UTILS_Cryptage_fichier", b"cryptage")
        fichier2.close()

        fichier3 = open(nomFichierCRYPT, "wb")
        fichier3.write(content)
        fichier3.close()

        # Envoi du fichier de données
        self.log.EcritLog(_(u"Envoi du fichier de données..."))
        self.Pulse_gauge()
        time.sleep(0.5)

        self.UploadFichier(ftp=ftp, nomFichierComplet=nomFichierCRYPT, repDest="application/data")

        # Fermeture connexion FTP ou SFTP
        self.Deconnexion(ftp)

        # Envoi de la requête de traitement du fichier d'import
        self.log.EcritLog(_(u"Envoi de la requête de traitement du fichier d'export..."))
        self.Pulse_gauge()
        time.sleep(0.5)

        page = None
        try :
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if url[-1] == "/" else "/") + "syncup/%d" % secret
            print("URL syncup =", url)

            req = Request(url)
            reponse = urlopen(req)
            page = reponse.read()

        except Exception as err :
            print(err)
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le traitement du fichier"))

        # Suppression du fichier
        #ftp = ftplib.FTP(hote, identifiant, mdp)
        #ftp.cwd(repertoire)
        #ftp.delete(os.path.basename(nomFichierDB))
        #ftp.quit()

        if page != None and page != "True" and page != b"True" :
            # Affichage erreur
            print("Erreur dans le traitement du fichier :", page)
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le traitement du fichier. Réponse reçue :"))
            self.log.EcritLog(page)

        else :
            # Mémorisation horodatage synchro
            UTILS_Parametres.Parametres(mode="set", categorie="portail", nom="last_synchro", valeur=str(datetime.datetime.now()))

        print("Temps upload_data = ", time.time() - t1)
        self.Pulse_gauge(0)
        time.sleep(0.5)

    def GetSecretInteger(self):
        secret = str(datetime.datetime.now().strftime("%Y%m%d"))
        for caract in self.dict_parametres["secret_key"] :
            if caract in "0123456789" :
                secret += caract
        return secret

    def Download_data(self, full_synchro=False):
        """ Téléchargement des demandes """
        self.log.EcritLog(_(u"Téléchargement des demandes..."))
        self.Pulse_gauge()

        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

        # Préparation du décryptage des valeurs
        cryptage = UTILS_Cryptage_fichier.AESCipher(self.dict_parametres["secret_key"][10:20], bs=16, prefixe=u"#@#")

        # Recherche la dernière demande téléchargée
        DB = GestionDB.DB()
        req = """
        SELECT ref_unique
        FROM portail_actions
        ORDER BY IDaction DESC
        LIMIT 1
        ;"""
        DB.ExecuterReq(req)
        result = DB.ResultatReq()
        listeDonnees = [x[0] for x in result]
        if len(listeDonnees) > 0 :
            last = int(listeDonnees[0])
        else :
            last = 0

        # Téléchargement des demandes non enregistrées
        if full_synchro == True :
            # Demande à récupérer toutes les actions du portail
            last = 0
            # Lit toutes les ref_unique de la base
            req = """
            SELECT IDaction, ref_unique
            FROM portail_actions;"""
            DB.ExecuterReq(req)
            result = DB.ResultatReq()
            listeRefExistantes = [x[1] for x in result]

        DB.Close()

        # Envoi de la requête pour obtenir le XML
        try :

            # Création de l'url de syncdown
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if url[-1] == "/" else "/") + "syncdown/%d/%d" % (int(secret), last)
            print("URL syncdown =", url)

            # Récupération des données au format json
            req = Request(url)
            reponse = urlopen(req)
            page = reponse.read()
            liste_actions = json.loads(page)

            if len(liste_actions) == 0 :
                self.log.EcritLog(_(u"Aucune demande non traitée trouvée..."))
            elif len(liste_actions) == 1 :
                self.log.EcritLog(_(u"1 demande non traitée trouvée..."))
            else :
                self.log.EcritLog(_(u"%s demandes non traitées trouvées...") % len(liste_actions))

        except Exception as err :
            print(err)
            self.log.EcritLog(_(u"Téléchargement des demandes impossible"))
            liste_actions = []

        # Sauvegarde des actions
        if liste_actions != None and len(liste_actions) > 0 :

            # Recherche la réservation la plus récente pour chaque période
            # dict_dernieres_reservations = {}
            # for action in liste_actions :
            #     if action["categorie"] == "reservations" :
            #         if not dict_dernieres_reservations.has_key(action["IDperiode"]) or (action["horodatage"] > dict_dernieres_reservations[action["IDperiode"]]["horodatage"] and action["etat"] != "suppression") :
            #             dict_dernieres_reservations[action["IDperiode"]] = action

            # Recherche le prochain IDaction
            DB = GestionDB.DB()
            #prochainIDaction = DB.GetProchainID("portail_actions")
            req = """SELECT max(IDaction) FROM portail_actions;"""
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if listeTemp[0][0] == None:
                prochainIDaction = 1
            else:
                prochainIDaction = listeTemp[0][0] + 1

            listeActions = []
            listeReservations = []
            listeRenseignements = []
            listeLocations = []
            listePasswordsFamilles = []
            listePasswordsUtilisateurs = []

            for action in liste_actions :
                valide = True

                # Télécharge uniquement les demandes non enregistrées dans la base
                if full_synchro == True:
                    if action["ref_unique"] in listeRefExistantes :
                        valide = False

                if valide == True :

                    if "IDutilisateur" not in action :
                        action["IDutilisateur"] = None

                    # Modification de compte
                    if action["categorie"] == "compte" :

                        # Si modification de mot de passe
                        if action["action"] == "maj_password" :
                            action["etat"] = "validation"
                            action["traitement_date"] = str(datetime.date.today())
                            if action["IDfamille"] != None :
                                listePasswordsFamilles.append((action["parametres"], action["IDfamille"]))
                            if action["IDutilisateur"] != None :
                                listePasswordsUtilisateurs.append((action["parametres"], action["IDutilisateur"]))

                    # Mémorisation des actions
                    listeActions.append([
                            prochainIDaction, action["horodatage"], action["IDfamille"], action["IDindividu"],
                            action["IDutilisateur"], action["categorie"], action["action"], action["description"],
                            action["commentaire"], action["parametres"], action["etat"],
                            action["traitement_date"], action["IDperiode"], action["ref_unique"], action["reponse"],
                            action.get("IDpaiement", None), action.get("ventilation", None),
                            ])

                    # Mémorisation des réservations
                    if len(action["reservations"]) > 0 :
                        for reservation in action["reservations"] :
                            listeReservations.append([reservation["date"], reservation["IDinscription"], reservation["IDunite"], prochainIDaction, reservation["etat"]])

                    # Mémorisation des renseignements
                    if "renseignements" in action and len(action["renseignements"]) > 0:
                        for renseignement in action["renseignements"] :
                            try:
                                valeur = cryptage.decrypt(renseignement["valeur"])
                                listeRenseignements.append([renseignement["champ"], valeur, prochainIDaction])
                            except:
                                pass

                    # Mémorisation des locations
                    if "locations" in action and len(action["locations"]) > 0:
                        for location in action["locations"] :
                            listeLocations.append([location["date_debut"], location["date_fin"], location["IDlocation"], location["IDproduit"], prochainIDaction, location["etat"], location["partage"], location["description"]])

                    prochainIDaction += 1

            # Enregistrement des actions
            if len(listeActions) > 0 :
                DB.Executermany("INSERT INTO portail_actions (IDaction, horodatage, IDfamille, IDindividu, IDutilisateur, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique, reponse, IDpaiement, ventilation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", listeActions, commit=False)
            if len(listeReservations) > 0 :
                DB.Executermany("INSERT INTO portail_reservations (date, IDinscription, IDunite, IDaction, etat) VALUES (?, ?, ?, ?, ?)", listeReservations, commit=False)
            if len(listeRenseignements) > 0 :
                DB.Executermany("INSERT INTO portail_renseignements (champ, valeur, IDaction) VALUES (?, ?, ?)", listeRenseignements, commit=False)
            if len(listeLocations) > 0 :
                DB.Executermany("INSERT INTO portail_reservations_locations (date_debut, date_fin, IDlocation, IDproduit, IDaction, etat, partage, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", listeLocations, commit=False)
            if len(listePasswordsFamilles) > 0 :
                DB.Executermany("UPDATE familles SET internet_mdp=? WHERE IDfamille=?", listePasswordsFamilles, commit=False)
                if len(listePasswordsFamilles) == 1:
                    self.log.EcritLog(_(u"1 mot de passe famille modifié..."))
                else:
                    self.log.EcritLog(_(u"%d mots de passe familles modifiés...") % len(listePasswordsFamilles))
            if len(listePasswordsUtilisateurs) > 0 :
                DB.Executermany("UPDATE utilisateurs SET internet_mdp=? WHERE IDutilisateur=?", listePasswordsUtilisateurs, commit=False)
                if len(listePasswordsUtilisateurs) == 1:
                    self.log.EcritLog(_(u"1 mot de passe administrateur modifié..."))
                else:
                    self.log.EcritLog(_(u"%d mots de passe administrateurs modifiés...") % len(listePasswordsUtilisateurs))

            DB.Commit()
            DB.Close()

            self.log.EcritLog(_(u"Téléchargement terminé"))

        return True

    def Valide_reception_demande(self, IDaction=None):
        self.log.EcritLog(_(u"COMING SOON:Validation de la reception de la demande %s") % IDaction)
        pass

    def Traitement_demandes(self):
        pass

    def Update_application(self):
        """ Demande une update de l'application """
        self.log.EcritLog(_(u"Recherche d'une mise à jour..."))

        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

        liste_actions = []
        try :

            # Création de l'url de syncdown
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + "/" + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["url_connecthys"][-1] != "/" :
                url += "/"
            version_noethys = FonctionsPerso.GetVersionLogiciel().replace(".", "")
            mode = self.dict_parametres["serveur_type"]
            url += "update/%d/%d/%d" % (int(secret), int(version_noethys), mode)
            print("URL update =", url)

            # Récupération des données au format json
            req = Request(url)
            reponse = urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            if data["resultat"] != False :
                self.log.EcritLog(data["resultat"])

        except Exception as err :
            self.log.EcritLog(_(u"[Erreur] Erreur dans la demande d'update"))
            self.log.EcritLog(str(err))
            print("Erreur dans la demande d'update :", str(err))
            return False

        return True

    def Upgrade_application(self):
        """ Demande un upgrade de l'application """
        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

        liste_actions = []
        try :

            # Création de l'url de syncdown
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if url[-1] == "/" else "/") + "upgrade/%d" % int(secret)
            print("URL upgrade =", url)

            # Récupération des données au format json
            req = Request(url)
            reponse = urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            print("Resultat :", data)

        except Exception as err :
            self.log.EcritLog(_(u"[Erreur] Erreur dans la demande d'upgrade"))
            print("Erreur dans la demande d'upgrade :", err)
            self.log.EcritLog(err)
            print("Erreur dans la demande d'upgrade :", str(err))
            return False

        return True

    def Repair_application(self):
        """ Demande un repair de la base de données """
        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

        try :

            # Création de l'url de syncdown
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if url[-1] == "/" else "/") + "repairdb/%d" % int(secret)
            print("URL repair =", url)

            # Récupération des données au format json
            req = Request(url)
            reponse = urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            print("Resultat :", data)

        except Exception as err :
            self.log.EcritLog(_(u"[Erreur] Erreur dans la demande de réparation DB"))
            print("Erreur dans la demande de repairdb :", err)
            self.log.EcritLog(err)
            print("Erreur dans la demande de repairdb :", str(err))
            return False

        return True

    def Clear_application(self):
        """ Demande un effacement total des tables de la base de données """
        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

        try :

            # Création de l'url de syncdown
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if url[-1] == "/" else "/") + "cleardb/%d" % int(secret)
            print("URL repair =", url)

            # Récupération des données au format json
            req = Request(url)
            reponse = urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            print("Resultat :", data)

        except Exception as err :
            self.log.EcritLog(_(u"[Erreur] Erreur dans la demande d'effacement de la DB"))
            print("Erreur dans la demande de cleardb :", err)
            self.log.EcritLog(err)
            print("Erreur dans la demande de cleardb :", str(err))
            return False

        return True

    def TelechargeFichier(self, ftp=None, nomFichier="models.py", repFichier=None):
        """ Télécharge un fichier sur internet """

        # Création d'un répertoire temporaire
        repDestination = UTILS_Fichiers.GetRepTemp("portail_temp")
        try :
            os.mkdir(repDestination)
        except :
            pass

        # Téléchargement du fichier vers le répertoire temporaire
        if self.dict_parametres["hebergement_type"] == 0 :
            infilepath = self.dict_parametres["hebergement_local_repertoire"]
            if repFichier != None :
                if self.dict_parametres["hebergement_local_repertoire"][-1] == "/" :
                    infilepath += repFichier
                else :
                    infilepath += "/" + repFichier
            infile = os.path.join(infilepath, nomFichier)
            try :
                shutil.copy2(infile, repDestination)
            except Exception as err :
                self.log.EcritLog(_(u"Récupération locale impossible du fichier '%s'") % nomFichier)
                self.log.EcritLog(_(u"err: %s") % err)
                print("Erreur dans telechargement du fichier '%s' : %s" % (nomFichier, str(err)))
                return False

        elif self.dict_parametres["hebergement_type"] == 1 :
            try :
                rep = "/" + self.dict_parametres["ftp_repertoire"]
                if repFichier != None :
                    if self.dict_parametres["ftp_repertoire"][-1] == "/" :
                        rep += repFichier
                    else :
                        rep += "/" + repFichier
                ftp.cwd(rep)
                fichier = open(os.path.join(repDestination, nomFichier), 'wb')
                ftp.retrbinary('RETR ' + nomFichier, fichier.write)
                fichier.close()
            except Exception as err :
                self.log.EcritLog(_(u"Téléchargement FTP impossible du fichier '%s'") % nomFichier)
                self.log.EcritLog(_(u"err: %s") % err)
                print(u"Erreur dans telechargement du fichier '%s' : %s" % (nomFichier, str(err)))
                return False

        elif self.dict_parametres["hebergement_type"] == 2 :
            try :
                # infilepath = "/" + self.dict_parametres["ssh_repertoire"]
                # if repFichier != None :
                #     if self.dict_parametres["ssh_repertoire"][-1] == "/" :
                #         infilepath += repFichier
                #     else :
                #         infilepath += "/" + repFichier
                # ftp.chdir(repFichier)
                if repFichier != None :
                    ftp.chdir(repFichier)
                ftp.get(nomFichier, os.path.join(repDestination, nomFichier))
                if repFichier != None and "/" in repFichier :
                    ftp.chdir("../" * len(repFichier.split("/")))
            except Exception as err :
                if nomFichier == "config.py" :
                    self.log.EcritLog(_(u"Aucun fichier de configuration à télécharger"))
                else :
                    self.log.EcritLog(_(u"Téléchargement SSH/SFTP impossible du fichier '%s'") % nomFichier)
                    self.log.EcritLog(_(u"err: %s") % err)
                    print("Erreur dans telechargement du fichier '%s' : %s" % (nomFichier, str(err)))
                return False
        else:
            raise()
        return repDestination, nomFichier


    def UploadFichier(self, ftp=None, nomFichierComplet="", repDest=""):
        nomFichier = os.path.basename(nomFichierComplet)
        repFichier = os.path.dirname(nomFichierComplet)

        # Envoi local
        if self.dict_parametres["hebergement_type"] == 0 :
            if self.dict_parametres["hebergement_local_repertoire"] != None:
                try :
                    destfilepath = os.path.join(self.dict_parametres["hebergement_local_repertoire"], repDest)
                    shutil.copy2(os.path.join(repFichier, nomFichier), destfilepath)
                except Exception as err :
                    print("Erreur upload fichier '%s' en local : %s" % (nomFichier, str(err)))
                    self.log.EcritLog(_(u"[ERREUR] Envoi du fichier '%s' par copie locale impossible.") % nomFichier)
                    return False

        # Envoi par FTP
        if self.dict_parametres["hebergement_type"] == 1 :
            if ftp != None :
                try :
                    rep = "/" + self.dict_parametres["ftp_repertoire"]
                    if repDest not in ("", None):
                        if self.dict_parametres["ftp_repertoire"][-1] == '/' :
                            rep += repDest
                        else :
                            rep += "/" + repDest
                    ftp.cwd(rep)
                    fichier = open(os.path.join(repFichier, nomFichier), "rb")
                    ftp.storbinary('STOR ' + nomFichier, fichier)
                    fichier.close()
                except Exception as err :
                    print("Erreur upload fichier par FTP :")
                    print(err)
                    self.log.EcritLog(_(u"[ERREUR] Envoi du fichier '%s' par FTP impossible.") % nomFichier)
                    return False

        # Envoi par SSH/SFTP
        if self.dict_parametres["hebergement_type"] == 2 :
            if ftp != None :
                try :
                    rep = "/" + self.dict_parametres["ssh_repertoire"]
                    if repDest not in ("", None):
                        if self.dict_parametres["ssh_repertoire"][-1] == '/' :
                            rep += repDest
                        else :
                            rep += "/" + repDest
                    ftp.chdir(rep)
                    ftp.put(os.path.join(repFichier, nomFichier), nomFichier)
                    if "/" in repDest :
                        ftp.chdir("../" * len(repDest.split("/")))
                except Exception as err :
                    print(u"Erreur upload fichier '%s' par SSH/SFTP :" % nomFichier)
                    print(err)
                    self.log.EcritLog(_(u"[ERREUR] Envoi du fichier '%s' par SSH/SFTP impossible.") % nomFichier)
                    return False

                try:
                    ftp.chmod(rep + "/" + nomFichier, mode=0o644)
                except Exception as err:
                    print("CHMOD 0644 sur %s impossible :" % nomFichier, err)

        return True


    def ConnectEtTelechargeFichier(self, nomFichier="", repFichier=None, lecture=True):
        resultats = self.Connexion()
        if resultats == False :
            return False
        else :
            ftp, ssh = resultats

        # Téléchargement du fichier
        resultat = self.TelechargeFichier(ftp=ftp, nomFichier=nomFichier, repFichier=repFichier)
        if resultat == False :
            return False
        self.Deconnexion(ftp)
        cheminFichier = os.path.join(resultat[0], resultat[1])

        if lecture:
            fichier = codecs.open(cheminFichier, encoding='utf-8', mode='r')
            contenu_fichier = fichier.read()
            fichier.close()
            return contenu_fichier

        return cheminFichier


if __name__ == '__main__':
    pass