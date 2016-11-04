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
import urllib2
import sys
import importlib
import platform
import time
from dateutil import relativedelta
import paramiko

import UTILS_Dates
import UTILS_Parametres
import UTILS_Fichiers
import UTILS_Titulaires
import UTILS_Pieces_manquantes
import UTILS_Cotisations_manquantes
import UTILS_Organisateur
import UTILS_Cryptage_fichier
import UTILS_Config
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

    def Synchro_totale(self):
        t1 = time.time()
        self.nbre_etapes = 25
        self.log.EcritLog(_(u"Lancement de la synchronisation..."))

        # Téléchargement des données en ligne
        self.Download_data()

        # Recherche de mises à jours logicielles Connecthys
        if self.dict_parametres["client_rechercher_updates"] == True :

            # Vérifie si une update n'a pas été faite aujourd'hui avec la même version de Noethys
            last_update = UTILS_Config.GetParametre("connecthys_last_update", None)
            version_noethys = FonctionsPerso.GetVersionLogiciel()
            data = "%s#%s" % (str(datetime.date.today()), version_noethys)
            if data != last_update :
                self.Update_application()
                # Mémorise la demande d'update
                UTILS_Config.SetParametre("connecthys_last_update", data)

        # Upload des données locales
        resultat = self.Upload_data()
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
            if type_valeur == unicode :
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
            except Exception, err :
                print "Connexion FTP du serveur", str(err)
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
            except Exception, err :
                print "Erreur connexion SSH/SFTP au serveur : ", str(err)
                self.log.EcritLog(_(u"[ERREUR] Connexion SSH/SFTP impossible."))
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

    def Upload_data(self) :
        self.log.EcritLog(_(u"Lancement de la synchronisation des données..."))

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

        # Ouverture de la base Noethys
        DB = GestionDB.DB()

        self.log.EcritLog(_(u"Récupération des données à exporter..."))
        self.Pulse_gauge()

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
        if self.dict_parametres["image_identification"] != "" :
            chemin_image = self.dict_parametres["image_identification"]
            nom_fichier = os.path.basename(chemin_image)

            # Upload du fichier image de fond
            self.UploadFichier(ftp=ftp, nomFichierComplet=chemin_image, repDest="application/static/fonds")

        else :
            nom_fichier = ""

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
            cheminLogo = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
            logo.SaveFile(cheminLogo, type=wx.BITMAP_TYPE_PNG)
            session.add(models.Parametre(nom="ORGANISATEUR_IMAGE", parametre=nomFichier))

            # Upload du logo
            self.UploadFichier(ftp=ftp, nomFichierComplet=cheminLogo, repDest="application/static")

        else :
            session.add(models.Parametre(nom="ORGANISATEUR_IMAGE", parametre=""))

        # Autres
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_EMAIL", parametre=str(self.dict_parametres["recevoir_document_email"])))
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_POSTE", parametre=str(self.dict_parametres["recevoir_document_courrier"])))
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_RETIRER", parametre=str(self.dict_parametres["recevoir_document_site"])))
        session.add(models.Parametre(nom="RECEVOIR_DOCUMENT_RETIRER_LIEU", parametre=self.dict_parametres["recevoir_document_site_lieu"]))
        session.add(models.Parametre(nom="PAIEMENT_EN_LIGNE_ACTIF", parametre=str(self.dict_parametres["paiement_ligne_actif"])))
        session.add(models.Parametre(nom="ACCUEIL_BIENVENUE", parametre=self.dict_parametres["accueil_bienvenue"]))
        session.add(models.Parametre(nom="ACCUEIL_ETAT_DOSSIER_AFFICHER", parametre=str(self.dict_parametres["accueil_etat_dossier_afficher"])))
        session.add(models.Parametre(nom="ACTIVITES_AFFICHER", parametre=str(self.dict_parametres["activites_afficher"])))
        session.add(models.Parametre(nom="ACTIVITES_INTRO", parametre=self.dict_parametres["activites_intro"]))
        session.add(models.Parametre(nom="ACTIVITES_AUTORISER_INSCRIPTION", parametre=str(self.dict_parametres["activites_autoriser_inscription"])))
        session.add(models.Parametre(nom="RESERVATIONS_AFFICHER", parametre=str(self.dict_parametres["reservations_afficher"])))
        session.add(models.Parametre(nom="RESERVATIONS_INTRO", parametre=self.dict_parametres["reservations_intro"]))
        session.add(models.Parametre(nom="PLANNING_INTRO", parametre=self.dict_parametres["planning_intro"]))
        session.add(models.Parametre(nom="FACTURES_AFFICHER", parametre=str(self.dict_parametres["factures_afficher"])))
        session.add(models.Parametre(nom="FACTURES_INTRO", parametre=self.dict_parametres["factures_intro"]))
        session.add(models.Parametre(nom="FACTURES_DEMANDE_FACTURE", parametre=str(self.dict_parametres["factures_demande_facture"])))
        session.add(models.Parametre(nom="REGLEMENTS_AFFICHER", parametre=str(self.dict_parametres["reglements_afficher"])))
        session.add(models.Parametre(nom="REGLEMENTS_INTRO", parametre=self.dict_parametres["reglements_intro"]))
        session.add(models.Parametre(nom="REGLEMENTS_DEMANDE_RECU", parametre=str(self.dict_parametres["reglements_demande_recu"])))
        session.add(models.Parametre(nom="PIECES_AFFICHER", parametre=str(self.dict_parametres["pieces_afficher"])))
        session.add(models.Parametre(nom="PIECES_INTRO", parametre=self.dict_parametres["pieces_intro"]))
        session.add(models.Parametre(nom="PIECES_AUTORISER_TELECHARGEMENT", parametre=str(self.dict_parametres["pieces_autoriser_telechargement"])))
        session.add(models.Parametre(nom="COTISATIONS_AFFICHER", parametre=str(self.dict_parametres["cotisations_afficher"])))
        session.add(models.Parametre(nom="COTISATIONS_INTRO", parametre=self.dict_parametres["cotisations_intro"]))
        session.add(models.Parametre(nom="HISTORIQUE_AFFICHER", parametre=str(self.dict_parametres["historique_afficher"])))
        session.add(models.Parametre(nom="HISTORIQUE_INTRO", parametre=self.dict_parametres["historique_intro"]))
        session.add(models.Parametre(nom="HISTORIQUE_DELAI", parametre=str(self.dict_parametres["historique_delai"])))
        session.add(models.Parametre(nom="CONTACT_AFFICHER", parametre=str(self.dict_parametres["contact_afficher"])))
        session.add(models.Parametre(nom="CONTACT_INTRO", parametre=self.dict_parametres["contact_intro"]))
        session.add(models.Parametre(nom="CONTACT_CARTE_AFFICHER", parametre=str(False))) #self.dict_parametres["contact_carte_afficher"])))
        session.add(models.Parametre(nom="MENTIONS_AFFICHER", parametre=str(self.dict_parametres["mentions_afficher"])))
        session.add(models.Parametre(nom="AIDE_AFFICHER", parametre=str(self.dict_parametres["aide_afficher"])))


        # Création des users
        dictTitulaires = UTILS_Titulaires.GetTitulaires()

        req = """SELECT IDfamille, internet_actif, internet_identifiant, internet_mdp
        FROM familles;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        for IDfamille, internet_actif, internet_identifiant, internet_mdp in listeDonnees :
            if internet_actif == 1 :
                nomsTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                # Cryptage du mot de passe
                internet_mdp = SHA256.new(internet_mdp).hexdigest()

                m = models.User(IDuser=None, identifiant=internet_identifiant, cryptpassword=internet_mdp, nom=nomsTitulaires, role="famille", IDfamille=IDfamille)
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

        for IDfacture, IDprefixe, prefixe, numero, IDcompte_payeur, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, IDfamille, etat in listeFactures :
            if numero == None : numero = 0
            if IDprefixe != None :
                numero = u"%s-%06d" % (prefixe, numero)
            else :
                numero = u"%06d" % numero

            date_edition = UTILS_Dates.DateEngEnDateDD(date_edition)
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            date_echeance = UTILS_Dates.DateEngEnDateDD(date_echeance)
            total = FloatToDecimal(total)
            if dictVentilation.has_key(IDfacture) :
                totalVentilation = FloatToDecimal(dictVentilation[IDfacture])
            else :
                totalVentilation = FloatToDecimal(0.0)
            if dictPrestations.has_key(IDfacture) :
                totalPrestations = FloatToDecimal(dictPrestations[IDfacture])
            else :
                totalPrestations = FloatToDecimal(0.0)
            solde_actuel = totalPrestations - totalVentilation

            m = models.Facture(IDfacture=IDfacture, IDfamille=IDfamille, numero=numero, date_edition=date_edition, date_debut=date_debut,\
                        date_fin=date_fin, montant=float(totalPrestations), montant_regle=float(totalVentilation), montant_solde=float(solde_actuel))
            session.add(m)


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
            date = UTILS_Dates.DateEngEnDateDD(date)
            date_encaissement = UTILS_Dates.DateEngEnDateDD(date_encaissement)
            if numero not in ("", None) :
                numero = "****%s" % numero[3:]
            m = models.Reglement(IDreglement=IDreglement, IDfamille=IDfamille, date=date, mode=mode,
                            numero=numero, montant=montant, date_encaissement=date_encaissement)
            session.add(m)

        # Création des pièces manquantes
        self.Pulse_gauge()

        dictPieces = UTILS_Pieces_manquantes.GetListePiecesManquantes(dateReference=datetime.date.today(), concernes=True)
        for IDfamille, dictValeurs in dictPieces.iteritems() :
            for IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide, label in dictValeurs["liste"] :
                m = models.Piece_manquante(IDfamille=IDfamille, IDtype_piece=IDtype_piece, IDindividu=IDindividu, nom=label)
                session.add(m)

        # Création des types de pièces
        self.Pulse_gauge()

        # Recherche des documents associées aux types de pièces
        DB2 = GestionDB.DB(suffixe="DOCUMENTS")
        req = "SELECT IDdocument, IDtype_piece, document, type, label FROM documents WHERE IDtype_piece IS NOT NULL AND document IS NOT NULL;"
        DB2.ExecuterReq(req)
        listeDocuments = DB2.ResultatReq()
        DB2.Close()
        dictDocuments = {}
        for IDdocument, IDtype_piece, document, extension, label in listeDocuments :
            if not dictDocuments.has_key(IDtype_piece) :
                dictDocuments[IDtype_piece] = []
            dictDocuments[IDtype_piece].append({"IDdocument" : IDdocument, "document" : document, "extension" : extension, "label" : label})

        # Recherche des types de pièces
        req = """
        SELECT IDtype_piece, nom, public
        FROM types_pieces;"""
        DB.ExecuterReq(req)
        listeTypesPieces = DB.ResultatReq()
        for IDtype_piece, nom, public in listeTypesPieces :

            # Recherche de documents associés
            fichiers = []
            if dictDocuments.has_key(IDtype_piece) :
                for dict_document in dictDocuments[IDtype_piece] :
                    nomFichier = "document%d.%s" % (dict_document["IDdocument"], dict_document["extension"])
                    cheminFichier = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
                    buffer = dict_document["document"]
                    fichier = open(cheminFichier, "wb")
                    fichier.write(buffer)
                    fichier.close()

                    # Upload de la pièce
                    self.UploadFichier(ftp=ftp, nomFichierComplet=cheminFichier, repDest="application/static/pieces")

                    fichiers.append(u"%s;%s" % (dict_document["label"], nomFichier))

            m = models.Type_piece(IDtype_piece=IDtype_piece, nom=nom, public=public, fichiers=u"##".join(fichiers))
            session.add(m)


        # Création des cotisations manquantes
        self.Pulse_gauge()

        dictCotisations = UTILS_Cotisations_manquantes.GetListeCotisationsManquantes(dateReference=datetime.date.today(), concernes=True)
        for IDfamille, dictValeurs in dictCotisations.iteritems() :
            for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label in dictValeurs["liste"] :
                m = models.Cotisation_manquante(IDfamille=IDfamille, IDindividu=IDindividu, IDtype_cotisation=IDtype_cotisation, nom=label)
                session.add(m)

        # Création des activités
        self.Pulse_gauge()

        req = """
        SELECT IDactivite, nom, portail_inscriptions_affichage, portail_inscriptions_date_debut,
        portail_inscriptions_date_fin, portail_reservations_affichage, portail_unites_multiples,
        portail_reservations_limite, portail_reservations_absenti
        FROM activites;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        dict_activites = {}
        for IDactivite, nom, inscriptions_affichage, inscriptions_date_debut, inscriptions_date_fin, reservations_affichage, unites_multiples, portail_reservations_limite, portail_reservations_absenti in listeActivites :
            inscriptions_date_debut = UTILS_Dates.DateEngEnDateDDT(inscriptions_date_debut)
            inscriptions_date_fin = UTILS_Dates.DateEngEnDateDDT(inscriptions_date_fin)

            m = models.Activite(IDactivite=IDactivite, nom=nom, inscriptions_affichage=inscriptions_affichage, \
                         inscriptions_date_debut=inscriptions_date_debut, inscriptions_date_fin=inscriptions_date_fin, \
                         reservations_affichage=reservations_affichage, unites_multiples=unites_multiples, \
                         reservations_limite=portail_reservations_limite, reservations_absenti=portail_reservations_absenti,
                         )
            session.add(m)

            dict_activites[IDactivite] = {
                "IDactivite" : IDactivite, "nom" : nom, "inscriptions_affichage" : inscriptions_affichage, \
                 "inscriptions_date_debut" : inscriptions_date_debut, "inscriptions_date_fin" : inscriptions_date_fin, \
                 "reservations_affichage" : reservations_affichage, "unites_multiples" : unites_multiples, \
                 "reservations_limite" : portail_reservations_limite, "reservations_absenti" : portail_reservations_absenti,
                }

        # Création des groupes
        self.Pulse_gauge()

        req = """
        SELECT IDgroupe, IDactivite, nom, ordre
        FROM groupes;"""
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()

        for IDgroupe, IDactivite, nom, ordre in listeGroupes :
            m = models.Groupe(IDgroupe=IDgroupe, nom=nom, IDactivite=IDactivite, ordre=ordre)
            session.add(m)


        # Création des individus
        self.Pulse_gauge()

        req = """SELECT IDrattachement, rattachements.IDindividu, rattachements.IDfamille,
        IDcivilite, nom, prenom, date_naiss
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDcategorie IN (1, 2);"""
        DB.ExecuterReq(req)
        listeRattachements = DB.ResultatReq()
        for IDrattachement, IDindividu, IDfamille, IDcivilite, nom, prenom, date_naiss in listeRattachements :
            date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            m = models.Individu(IDindividu=IDindividu, IDfamille=IDfamille, prenom=prenom, date_naiss=date_naiss, IDcivilite=IDcivilite)
            session.add(m)


        # Création des inscriptions
        self.Pulse_gauge()

        req = """SELECT IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe
        FROM inscriptions;"""
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        for IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe in listeInscriptions :
            m = models.Inscription(IDinscription=IDinscription, IDindividu=IDindividu, IDfamille=IDfamille, IDactivite=IDactivite, IDgroupe=IDgroupe)
            session.add(m)

        # Création des unités
        self.Pulse_gauge()

        req = """SELECT IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre
        FROM portail_unites
        ORDER BY IDactivite, ordre;"""
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        for IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre in listeUnites :
            m = models.Unite(IDunite=IDunite, nom=nom, IDactivite=IDactivite, unites_principales=unites_principales, \
                      unites_secondaires=unites_secondaires, ordre=ordre)
            session.add(m)

        # Création des périodes
        self.Pulse_gauge()

        req = """SELECT IDperiode, IDactivite, nom, date_debut, date_fin, affichage, affichage_date_debut, affichage_date_fin
        FROM portail_periodes
        WHERE affichage=1;"""
        DB.ExecuterReq(req)
        listePeriodes = DB.ResultatReq()
        dict_dates_activites = {}
        for IDperiode, IDactivite, nom, date_debut, date_fin, affichage, affichage_date_debut, affichage_date_fin in listePeriodes :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            affichage_date_debut = UTILS_Dates.DateEngEnDateDDT(affichage_date_debut)
            affichage_date_fin = UTILS_Dates.DateEngEnDateDDT(affichage_date_fin)

            m = models.Periode(IDperiode=IDperiode, IDactivite=IDactivite, nom=nom, date_debut=date_debut, date_fin=date_fin, \
                        affichage_date_debut=affichage_date_debut, affichage_date_fin=affichage_date_fin)
            session.add(m)

            # Mémorise les activités pour lesquelles il y a des périodes...
            if not dict_dates_activites.has_key(IDactivite) :
                dict_dates_activites[IDactivite] = {"date_min" : None, "date_max" : None}
            if dict_dates_activites[IDactivite]["date_min"] == None or dict_dates_activites[IDactivite]["date_min"] > date_debut :
                dict_dates_activites[IDactivite]["date_min"] = date_debut
            if dict_dates_activites[IDactivite]["date_max"] == None or dict_dates_activites[IDactivite]["date_max"] < date_fin :
                dict_dates_activites[IDactivite]["date_max"] = date_fin

        # Création de la condition pour les ouvertures et les consommations
        listeConditions = []
        for IDactivite, periode in dict_dates_activites.iteritems() :
            listeConditions.append("(IDactivite=%d AND date>='%s' AND date<='%s')" % (IDactivite, periode["date_min"], periode["date_max"]))
        texteConditions = " OR ".join(listeConditions)

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

        # Création des consommations
        self.Pulse_gauge()

        if len(listeConditions) > 0 :

            req = """SELECT IDconso, date, IDunite, IDinscription, etat
            FROM consommations
            WHERE %s;""" % texteConditions
            DB.ExecuterReq(req)
            listeConsommations = DB.ResultatReq()
            for IDconso, date, IDunite, IDinscription, etat in listeConsommations :
                date = UTILS_Dates.DateEngEnDateDD(date)
                m = models.Consommation(date=date, IDunite=IDunite, IDinscription=IDinscription, etat=etat)
                session.add(m)

        # CrÃ©ation des actions
        self.Pulse_gauge()

        req = """SELECT IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique, reponse
        FROM portail_actions
        WHERE horodatage>='%s';""" % (datetime.datetime.now() - datetime.timedelta(days=(self.dict_parametres["historique_delai"]+1)*30))
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        for IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique, reponse in listeActions :
            traitement_date = UTILS_Dates.DateEngEnDateDD(traitement_date)
            horodatage = UTILS_Dates.DateEngEnDateDDT(horodatage)
            m = models.Action(horodatage=horodatage, IDfamille=IDfamille, IDindividu=IDindividu, categorie=categorie, action=action, description=description, commentaire=commentaire, parametres=parametres, etat=etat, traitement_date=traitement_date, IDperiode=IDperiode, ref_unique=ref_unique, reponse=reponse)
            session.add(m)

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
        UTILS_Cryptage_fichier.CrypterFichier(nomFichierZIP, nomFichierCRYPT, cryptage_mdp)
        os.remove(nomFichierZIP)

        # Pour contrer le bug de Pickle dans le cryptage
        fichier2 = open(nomFichierCRYPT, "rb")
        content = fichier2.read()
        # TODO: comprendre pourquoi quand appele via synchro arrriÃšre plan ou vian synchro du bouton outils du panel c'est Utils.UTILS_Cryptage
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
                url = self.dict_parametres["url_connecthys"] + "/" + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + "syncup/%d" % secret
            print "URL syncup =", url

            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()

        except Exception, err :
            print err
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le traitement du fichier"))

        # Suppression du fichier
        #ftp = ftplib.FTP(hote, identifiant, mdp)
        #ftp.cwd(repertoire)
        #ftp.delete(os.path.basename(nomFichierDB))
        #ftp.quit()

        if page != None and page != "True" :
            print "Erreur dans le traitement du fichier :", page
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le traitement du fichier. Réponse reçue :"))
            self.log.EcritLog(page)

        self.Pulse_gauge(0)
        time.sleep(0.5)

    def GetSecretInteger(self):
        secret = str(datetime.datetime.now().strftime("%Y%m%d"))
        for caract in self.dict_parametres["secret_key"] :
            if caract in "0123456789" :
                secret += caract
        return secret

    def Download_data(self):
        """ Téléchargement des demandes """
        self.log.EcritLog(_(u"Téléchargement des demandes..."))
        self.Pulse_gauge()

        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

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
        DB.Close()
        if len(listeDonnees) > 0 :
            last = int(listeDonnees[0])
        else :
            last = 0

        # Envoi de la requête pour obtenir le XML
        try :

            # Création de l'url de syncdown
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + "/" + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + "syncdown/%d/%d" % (int(secret), last)
            print "URL syncdown =", url

            # Récupération des données au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            liste_actions = json.loads(page)

            if len(liste_actions) == 0 :
                self.log.EcritLog(_(u"Aucune demande non traitée trouvée..."))
            elif len(liste_actions) == 1 :
                self.log.EcritLog(_(u"1 demande non traitée trouvée..."))
                self.log.EcritLog(_(u"Enregistrement de la demande non traitee"))
            else :
                self.log.EcritLog(_(u"%s demandes non traitées trouvées...") % len(liste_actions))
                self.log.EcritLog(_(u"Enregistrement des demandes non traitees"))

        except Exception, err :
            print err
            self.log.EcritLog(_(u"[ERREUR] Téléchargement des demandes impossible"))
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
            prochainIDaction = DB.GetProchainID("portail_actions")

            listeActions = []
            listeReservations = []

            for action in liste_actions :

                # Mémorisation des actions
                listeActions.append([
                        prochainIDaction, action["horodatage"], action["IDfamille"], action["IDindividu"],
                        action["categorie"], action["action"], action["description"],
                        action["commentaire"], action["parametres"], action["etat"],
                        action["traitement_date"], action["IDperiode"], action["ref_unique"], action["reponse"]
                        ])

                # Mémorisation des réservations
                if len(action["reservations"]) > 0 :

                    for reservation in action["reservations"] :
                        listeReservations.append([
                                reservation["date"], reservation["IDinscription"],
                                reservation["IDunite"], prochainIDaction, reservation["etat"],
                                ])

                prochainIDaction += 1

            # Enregistrement des actions
            if len(listeActions) > 0 :
                DB.Executermany("INSERT INTO portail_actions (IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique, reponse) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", listeActions, commit=False)
            if len(listeReservations) > 0 :
                DB.Executermany("INSERT INTO portail_reservations (date, IDinscription, IDunite, IDaction, etat) VALUES (?, ?, ?, ?, ?)", listeReservations, commit=False)
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
            print "URL update =", url

            # Récupération des données au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            if data["resultat"] != False :
                self.log.EcritLog(data["resultat"])

        except Exception, err :
            self.log.EcritLog(_(u"[Erreur] Erreur dans la demande d'update"))
            self.log.EcritLog(str(err))
            print "Erreur dans la demande d'update :", str(err)
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
                url = self.dict_parametres["url_connecthys"] + "/" + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += ("" if self.dict_parametres["url_connecthys"][-1] == "/" else "/") + "upgrade/%d" % int(secret)
            print "URL upgrade =", url

            # Récupération des données au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            print "Resultat :", data

        except Exception, err :
            self.log.EcritLog(_(u"[Erreur] Erreur dans la demande d'upgrade"))
            print "Erreur dans la demande d'upgrade :", err
            self.log.EcritLog(err)
            print "Erreur dans la demande d'upgrade :", str(err)
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
            except Exception, err :
                self.log.EcritLog(_(u"Récupération locale impossible du fichier '%s'") % nomFichier)
                self.log.EcritLog(_(u"err: %s") % err)
                print "Erreur dans telechargement du fichier '%s' : %s" % (nomFichier, str(err))
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
            except Exception, err :
                self.log.EcritLog(_(u"Téléchargement FTP impossible du fichier '%s'") % nomFichier)
                self.log.EcritLog(_(u"err: %s") % err)
                print u"Erreur dans telechargement du fichier '%s' : %s" % (nomFichier, str(err))
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
            except Exception, err :
                self.log.EcritLog(_(u"Téchargement SSH/SFTP impossible du fichier '%s'") % nomFichier)
                self.log.EcritLog(_(u"err: %s") % err)
                print "Erreur dans telechargement du fichier '%s' : %s" % (nomFichier, str(err))
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
                except Exception, err :
                    print "Erreur upload fichier '%s' en local : %s" % (nomFichier, str(err))
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
                except Exception, err :
                    print "Erreur upload fichier '%s' par FTP : %s" % (nomFichier, str(err))
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
                except Exception, err :
                    print "Erreur upload fichier '%s' par SSH/SFTP : %s" % (nomFichier, str(err))
                    self.log.EcritLog(_(u"[ERREUR] Envoi du fichier '%s' par SSH/SFTP impossible.") % nomFichier)
                    return False

        return True




if __name__ == '__main__':
    pass
