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
import base64
import zipfile
import shutil
import json
import urllib2
import sys
import importlib

import GestionDB
import UTILS_Dates
import UTILS_Parametres
import UTILS_Fichiers
import UTILS_Titulaires
import UTILS_Pieces_manquantes
import UTILS_Cotisations_manquantes
import UTILS_Organisateur
import UTILS_Cryptage_fichier
import FonctionsPerso

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Dlg.DLG_Portail_config import VALEURS_DEFAUT as VALEURS_DEFAUT_CONFIG
from Dlg.DLG_Portail_config import LISTE_THEMES

from Crypto.Hash import SHA256




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

    def Pulse_gauge(self, num=None):
        if num == None :
            self.num_etape += 1
        else :
            self.num_etape = num
        num = 100 * self.num_etape / self.nbre_etapes
        self.log.SetGauge(num)

    def Synchro_totale(self):
        self.nbre_etapes = 24
        self.log.EcritLog(_(u"Lancement de la synchronisation..."))
        self.Download_data()
        resultat = self.Upload_data()
        if resultat == False :
            self.log.EcritLog(_(u"Synchronisation arrêtée."))
        else :
            self.log.EcritLog(_(u"Synchronisation terminée."))
        self.log.EcritLog(_(u"Serveur prêt"))
        self.log.SetGauge(0)

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
            liste_lignes.append(Ecrit_ligne("SQLALCHEMY_DATABASE_URI", "mysql://%s:%s@%s/%s" % (db_utilisateur, db_mdp, db_serveur, db_nom), type_valeur=str))

        liste_lignes.append(Ecrit_ligne("SQLALCHEMY_TRACK_MODIFICATIONS", True, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("SQLALCHEMY_ECHO", False, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("SECRET_KEY", self.dict_parametres["secret_key"], type_valeur=str))
        liste_lignes.append(Ecrit_ligne("WTF_CSRF_ENABLED", True, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("DEBUG", self.dict_parametres["mode_debug"], type_valeur=bool))

        # Valeurs Utilisateur
        liste_lignes.append("\nclass Config_utilisateur(object):\n")

        # IDfichier
        IDfichier = FonctionsPerso.GetIDfichier()
        liste_lignes.append(Ecrit_ligne("IDfichier", IDfichier, type_valeur=str))

        # Thème
        index = 0
        for code, label in LISTE_THEMES :
            if index == self.dict_parametres["theme"] :
                theme = "skin-%s" % code
            index += 1
        liste_lignes.append(Ecrit_ligne("SKIN", theme, type_valeur=str))

        # Image de fond identification
        if self.dict_parametres["image_identification"] != "" :
            image = os.path.basename(self.dict_parametres["image_identification"])
        else :
            image = ""
        liste_lignes.append(Ecrit_ligne("IMAGE_FOND", image, type_valeur=unicode))


        # Cadre logo organisateur
        if self.dict_parametres["cadre_logo"] == 0 :
            rond = False
        else :
            rond = True
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_IMAGE_ROND", rond, type_valeur=bool))

        # Données organisateur
        dict_organisateur = UTILS_Organisateur.GetDonnees(tailleLogo=(200, 200))

        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_NOM", dict_organisateur["nom"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_RUE", dict_organisateur["rue"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_CP", dict_organisateur["cp"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_VILLE", dict_organisateur["ville"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_TEL", dict_organisateur["tel"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_FAX", dict_organisateur["fax"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_EMAIL", dict_organisateur["mail"], type_valeur=unicode))

        # Logo organisateur
        logo = dict_organisateur["logo"]
        if logo != None :
            nomFichier = "logo.png"
            cheminLogo = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
            logo.SaveFile(cheminLogo, type=wx.BITMAP_TYPE_PNG)
            liste_lignes.append(Ecrit_ligne("ORGANISATEUR_IMAGE", nomFichier, type_valeur=unicode))

            # Envoi du logo par FTP
            if ftp != None :
                try :
                    ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application/static")
                    fichier = open(cheminLogo, "rb")
                    ftp.storbinary('STOR ' + nomFichier, fichier)
                except Exception, err :
                    print str(err)
                    return False

        else :
            liste_lignes.append(Ecrit_ligne("ORGANISATEUR_IMAGE", None, type_valeur=None))

        # Autres
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_EMAIL", self.dict_parametres["recevoir_document_email"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_POSTE", self.dict_parametres["recevoir_document_courrier"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_RETIRER", self.dict_parametres["recevoir_document_site"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_RETIRER_LIEU", self.dict_parametres["recevoir_document_site_lieu"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("PAIEMENT_EN_LIGNE_ACTIF", self.dict_parametres["paiement_ligne_actif"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("ACTIVITES_AFFICHER", self.dict_parametres["activites_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("ACTIVITES_AUTORISER_INSCRIPTION", self.dict_parametres["activites_autoriser_inscription"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RESERVATIONS_AFFICHER", self.dict_parametres["reservations_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("FACTURES_AFFICHER", self.dict_parametres["factures_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("FACTURES_DEMANDE_FACTURE", self.dict_parametres["factures_demande_facture"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("REGLEMENTS_AFFICHER", self.dict_parametres["reglements_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("REGLEMENTS_DEMANDE_RECU", self.dict_parametres["reglements_demande_recu"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("PIECES_AFFICHER", self.dict_parametres["pieces_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("PIECES_AUTORISER_TELECHARGEMENT", self.dict_parametres["pieces_autoriser_telechargement"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("COTISATIONS_AFFICHER", self.dict_parametres["cotisations_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("HISTORIQUE_AFFICHER", self.dict_parametres["historique_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("HISTORIQUE_DELAI", self.dict_parametres["historique_delai"], type_valeur=int))
        liste_lignes.append(Ecrit_ligne("CONTACT_AFFICHER", self.dict_parametres["contact_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("MENTIONS_AFFICHER", self.dict_parametres["mentions_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("AIDE_AFFICHER", self.dict_parametres["aide_afficher"], type_valeur=bool))

        # Génération du fichier
        nomFichier = "config.py"
        nomFichierComplet = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
        fichier = codecs.open(nomFichierComplet, 'w', encoding='utf8')
        for ligne in liste_lignes :
            fichier.write(ligne)
        fichier.close()

        # Envoi du fichier par FTP
        if ftp != None :
            ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application/data")
            fichier = open(nomFichierComplet, "rb")#codecs.open(nomFichierComplet, 'rb', encoding='utf8')
            ftp.storbinary('STOR ' + nomFichier, fichier)

        return True

    def CopieToLocal_config(self, destdir=""):
        """ Copie le fichier de config vers un repertoire local"""
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
            liste_lignes.append(Ecrit_ligne("SQLALCHEMY_DATABASE_URI", "mysql://%s:%s@%s/%s" % (db_utilisateur, db_mdp, db_serveur, db_nom), type_valeur=str))

        liste_lignes.append(Ecrit_ligne("SQLALCHEMY_TRACK_MODIFICATIONS", True, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("SQLALCHEMY_ECHO", False, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("SECRET_KEY", self.dict_parametres["secret_key"], type_valeur=str))
        liste_lignes.append(Ecrit_ligne("WTF_CSRF_ENABLED", True, type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("DEBUG", self.dict_parametres["mode_debug"], type_valeur=bool))

        # Valeurs Utilisateur
        liste_lignes.append("\nclass Config_utilisateur(object):\n")

        # Thème
        index = 0
        for code, label in LISTE_THEMES :
            if index == self.dict_parametres["theme"] :
                theme = "skin-%s" % code
            index += 1
        liste_lignes.append(Ecrit_ligne("SKIN", theme, type_valeur=str))

        # Image de fond identification
        if self.dict_parametres["image_identification"] != "" :
            image = os.path.basename(self.dict_parametres["image_identification"])
        else :
            image = ""
        liste_lignes.append(Ecrit_ligne("IMAGE_FOND", image, type_valeur=unicode))


        # Cadre logo organisateur
        if self.dict_parametres["cadre_logo"] == 0 :
            rond = False
        else :
            rond = True
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_IMAGE_ROND", rond, type_valeur=bool))

        # Données organisateur
        dict_organisateur = UTILS_Organisateur.GetDonnees(tailleLogo=(200, 200))

        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_NOM", dict_organisateur["nom"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_RUE", dict_organisateur["rue"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_CP", dict_organisateur["cp"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_VILLE", dict_organisateur["ville"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_TEL", dict_organisateur["tel"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_FAX", dict_organisateur["fax"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("ORGANISATEUR_EMAIL", dict_organisateur["mail"], type_valeur=unicode))

        # Logo organisateur
        logo = dict_organisateur["logo"]
        if logo != None :
            nomFichier = "logo.png"
            cheminLogo = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
            logo.SaveFile(cheminLogo, type=wx.BITMAP_TYPE_PNG)
            liste_lignes.append(Ecrit_ligne("ORGANISATEUR_IMAGE", nomFichier, type_valeur=unicode))

            # Copie du logo vers le repertoire local
            if self.dict_parametres["hebergement_local_repertoire"] != None:
                try :
                    #ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application/static")
                    #fichier = open(cheminLogo, "rb")
                    #ftp.storbinary('STOR ' + nomFichier, fichier)
		    destfilepath = os.path.join(self.dict_parametres["hebergement_local_repertoire"], "/application/static")
		    shutil.copy2(cheminLogo, destfilepath)
                except Exception, err :
                    print str(err)
                    return False

        else :
            liste_lignes.append(Ecrit_ligne("ORGANISATEUR_IMAGE", None, type_valeur=None))

        # Autres
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_EMAIL", self.dict_parametres["recevoir_document_email"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_POSTE", self.dict_parametres["recevoir_document_courrier"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_RETIRER", self.dict_parametres["recevoir_document_site"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RECEVOIR_DOCUMENT_RETIRER_LIEU", self.dict_parametres["recevoir_document_site_lieu"], type_valeur=unicode))
        liste_lignes.append(Ecrit_ligne("PAIEMENT_EN_LIGNE_ACTIF", self.dict_parametres["paiement_ligne_actif"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("ACTIVITES_AFFICHER", self.dict_parametres["activites_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("ACTIVITES_AUTORISER_INSCRIPTION", self.dict_parametres["activites_autoriser_inscription"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("RESERVATIONS_AFFICHER", self.dict_parametres["reservations_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("FACTURES_AFFICHER", self.dict_parametres["factures_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("FACTURES_DEMANDE_FACTURE", self.dict_parametres["factures_demande_facture"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("REGLEMENTS_AFFICHER", self.dict_parametres["reglements_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("REGLEMENTS_DEMANDE_RECU", self.dict_parametres["reglements_demande_recu"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("PIECES_AFFICHER", self.dict_parametres["pieces_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("PIECES_AUTORISER_TELECHARGEMENT", self.dict_parametres["pieces_autoriser_telechargement"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("COTISATIONS_AFFICHER", self.dict_parametres["cotisations_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("HISTORIQUE_AFFICHER", self.dict_parametres["historique_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("CONTACT_AFFICHER", self.dict_parametres["contact_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("MENTIONS_AFFICHER", self.dict_parametres["mentions_afficher"], type_valeur=bool))
        liste_lignes.append(Ecrit_ligne("AIDE_AFFICHER", self.dict_parametres["aide_afficher"], type_valeur=bool))

        # Génération du fichier
        nomFichier = "config.py"
        nomFichierComplet = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)
        fichier = codecs.open(nomFichierComplet, 'w', encoding='utf8')
        for ligne in liste_lignes :
            fichier.write(ligne)
        fichier.close()

        # Deplacement du fichier dans le repertoire local
        if self.dict_parametres["hebergement_local_repertoire"] != None :
            #ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application/data")
            #fichier = open(nomFichierComplet, "rb")#codecs.open(nomFichierComplet, 'rb', encoding='utf8')
            #ftp.storbinary('STOR ' + nomFichier, fichier)
	    destfile = os.path.join(self.dict_parametres["hebergement_local_repertoire"], "/application/data")
	    os.renames(nomFichierComplet,destfile)

        return True


    def Upload_data(self) :
        self.log.EcritLog(_(u"Lancement de la procédure de mise en ligne des données..."))

        # Connexion FTP
        self.log.EcritLog(_(u"Connexion FTP..."))
        self.Pulse_gauge()

        try :
            ftp = ftplib.FTP(self.dict_parametres["ftp_serveur"], self.dict_parametres["ftp_utilisateur"], self.dict_parametres["ftp_mdp"])
        except Exception, err :
            print "Connexion FTP du serveur", str(err)
            self.log.EcritLog(_(u"[ERREUR] Connexion FTP impossible."))
            return False

        # Envoi du fichier de config par FTP
        self.log.EcritLog(_(u"Envoi du fichier de configuration..."))
        self.Pulse_gauge()
        resultat = self.Upload_config(ftp=ftp)
        if resultat == False :
            self.log.EcritLog(_(u"[ERREUR] Envoi impossible."))
            return False

        # Récupération du fichier models par FTP
        self.log.EcritLog(_(u"Téléchargement des modèles de données..."))
        resultat = self.TelechargeModels(ftp)
        if resultat == False :
            self.log.EcritLog(_(u"[ERREUR] Téléchargement impossible."))
            ftp.quit()
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

        # Récupération des totaux des prestations pour chaque facture
        req = """
        SELECT
        prestations.IDfacture, SUM(prestations.montant)
        FROM prestations
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        GROUP BY prestations.IDfacture
        ;"""
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
        ORDER BY factures.date_edition
        ;"""
        DB.ExecuterReq(req)
        listeFactures = DB.ResultatReq()

        # Récupération de la ventilation
        req = """
        SELECT prestations.IDfacture, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = prestations.IDcompte_payeur
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        GROUP BY prestations.IDfacture
        ;"""
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

        req = """SELECT
        reglements.IDreglement, comptes_payeurs.IDfamille, reglements.date, modes_reglements.label,
        reglements.numero_piece, reglements.montant, depots.date
        FROM reglements
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        GROUP BY reglements.IDreglement
        ;"""
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

                    # Envoi du fichier par FTP
                    ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application/static/pieces")
                    fichier = open(cheminFichier, "rb")
                    ftp.storbinary('STOR ' + nomFichier, fichier)
                    fichier.close()

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
            #inscriptions_date_debut = UTILS_Dates.DateEngEnDateDD(inscriptions_date_debut)
            #inscriptions_date_fin = UTILS_Dates.DateEngEnDateDD(inscriptions_date_fin)

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
            #affichage_date_debut = UTILS_Dates.DateEngEnDateDD(affichage_date_debut)
            #affichage_date_fin = UTILS_Dates.DateEngEnDateDD(affichage_date_fin)

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

        # Création des actions
        self.Pulse_gauge()

        req = """SELECT IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique
        FROM portail_actions
        WHERE horodatage>='%s';""" % (datetime.datetime.now() - datetime.timedelta(days=(self.dict_parametres["historique_delai"]+1)*30))
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        for IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique in listeActions :
            traitement_date = UTILS_Dates.DateEngEnDateDD(traitement_date)
            m = models.Action(horodatage=horodatage, IDfamille=IDfamille, IDindividu=IDindividu, categorie=categorie, action=action, description=description, commentaire=commentaire, parametres=parametres, etat=etat, traitement_date=traitement_date, IDperiode=IDperiode, ref_unique=ref_unique)
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
        os.remove(nomFichierDB)

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
        content = content.replace(b"Utils.UTILS_Cryptage_fichier", b"cryptage")
        fichier2.close()

        fichier3 = open(nomFichierCRYPT, "wb")
        fichier3.write(content)
        fichier3.close()

        # Envoi du fichier de données par FTP
        self.log.EcritLog(_(u"Envoi du fichier de données..."))
        self.Pulse_gauge()

        ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application/data")
        fichier = open(nomFichierCRYPT, "rb")
        ftp.storbinary("STOR %s" % os.path.basename(nomFichierCRYPT), fichier)
        fichier.close()

        self.log.EcritLog(_(u"Fermeture de la connexion FTP..."))
        self.Pulse_gauge()
        ftp.quit()

        # Envoi de la requête de traitement du fichier d'import
        self.log.EcritLog(_(u"Envoi de la requête de traitement du fichier d'export..."))
        self.Pulse_gauge()

        page = None
        try :
            url = self.dict_parametres["url_repertoire"] + "/portail.cgi/syncup/%d" % secret
            print "URL syncup =", url
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()

        except Exception, err :
            print err
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le traitement du fichier : %s") % err)

        # Suppression du fichier
        #ftp = ftplib.FTP(hote, identifiant, mdp)
        #ftp.cwd(repertoire)
        #ftp.delete(os.path.basename(nomFichierDB))
        #ftp.quit()

        if page != None and page != "True" :
            print "Erreur dans le traitement du fichier :", page
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le traitement du fichier. Réponse reçue : %s") % page)

        self.log.EcritLog(_(u"Mise en ligne des données terminée"))
        self.Pulse_gauge(0)

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
        SELECT horodatage, IDfamille, ref_unique
        FROM portail_actions
        ORDER BY IDaction DESC
        LIMIT 1
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            horodatage, IDfamille, ref_unique = listeDonnees[0]
            last = int(ref_unique)
        else :
            last = 0

        # Envoi de la requête pour obtenir le XML
        try :

            # Création de l'url de syncdown
            url = self.dict_parametres["url_repertoire"] + "/portail.cgi/syncdown/%d/%d" % (int(secret), last)
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
            else :
                self.log.EcritLog(_(u"%s demandes non traitées trouvées...") % len(liste_actions))

        except Exception, err :
            print err
            err = str(err).decode("iso-8859-15")
            self.log.EcritLog(_(u"[ERREUR] Erreur dans le téléchargement : %s") % err)
            return False

        # Sauvegarde des actions
        if liste_actions != None and len(liste_actions) > 0 :

            # Recherche la réservation la plus récente pour chaque période
            dict_dernieres_reservations = {}
            for action in liste_actions :
                if action["categorie"] == "reservations" :
                    if not dict_dernieres_reservations.has_key(action["IDperiode"]) or (action["horodatage"] > dict_dernieres_reservations[action["IDperiode"]]["horodatage"] and action["etat"] != "suppression") :
                        dict_dernieres_reservations[action["IDperiode"]] = action

            # Recherche le prochain IDaction
            DB = GestionDB.DB()
            prochainIDaction = DB.GetProchainID("portail_actions")

            listeActions = []
            listeReservations = []

            for action in liste_actions :

                # Ecrase les réservations les plus anciennes pour chaque période
                etat = action["etat"]
                if action["categorie"] == "reservations" :
                    if dict_dernieres_reservations[action["IDperiode"]] != action :
                        etat = "suppression"

                # Mémorisation des actions
                listeActions.append([
                        prochainIDaction, action["horodatage"], action["IDfamille"], action["IDindividu"],
                        action["categorie"], action["action"], action["description"],
                        action["commentaire"], action["parametres"], etat,
                        action["traitement_date"], action["IDperiode"], action["ref_unique"]
                        ])

                # Mémorisation des réservations
                if len(action["reservations"]) > 0 :

                    for reservation in action["reservations"] :
                        listeReservations.append([
                                reservation["date"], reservation["IDinscription"],
                                reservation["IDunite"], prochainIDaction,
                                ])

                prochainIDaction += 1

            # Enregistrement des actions
            if len(listeActions) > 0 :
                DB.Executermany("INSERT INTO portail_actions (IDaction, horodatage, IDfamille, IDindividu, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, ref_unique) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", listeActions, commit=False)
            if len(listeReservations) > 0 :
                DB.Executermany("INSERT INTO portail_reservations (date, IDinscription, IDunite, IDaction) VALUES (?, ?, ?, ?)", listeReservations, commit=False)
            DB.Commit()
            DB.Close()

        self.log.EcritLog(_(u"Téléchargement terminé"))
        return True


    def Upgrade_application(self):
        """ Demande un upgrade de l'application """
        # Codage de la clé de sécurité
        secret = self.GetSecretInteger()

        liste_actions = []
        try :

            # Création de l'url de syncdown
            url = self.dict_parametres["url_repertoire"] + "/portail.cgi/upgrade/%d" % int(secret)

            # Récupération des données au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            data = json.loads(page)

            print "Resultat :", data

        except Exception, err :
            print "Erreur dans la demande d'upgrade :", str(err)
            return False

        return True

    def TelechargeModels(self, ftp=None):
        """ Télécharge le module des models sur internet """
        nomFichier = "models.py"

        # Création d'un répertoire temporaire
        rep = UTILS_Fichiers.GetRepTemp("portail_models")
        try :
            os.mkdir(rep)
        except :
            pass

        # Téléchargement du fichier vers le répertoire temporaire
        try :
            ftp.cwd("/" + self.dict_parametres["ftp_repertoire"] + "/application")
            fichier = open(os.path.join(rep, nomFichier), 'wb')
            ftp.retrbinary('RETR ' + nomFichier, fichier.write)
            fichier.close()
        except Exception, err :
            print str(err)
            return False

        return rep, nomFichier


if __name__ == '__main__':
    pass