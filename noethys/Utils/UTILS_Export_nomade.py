#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import sqlite3
import six
import time
import traceback
import sys
import os
import base64
import zipfile
import shutil
import ftplib
from Utils import UTILS_Cryptage_fichier
from Utils import UTILS_Config
from Utils import UTILS_Titulaires
from Utils import UTILS_Fichiers
from Utils import UTILS_Customize

from Data import DATA_Tables as TABLES

EXTENSION_CRYPTE = ".nsc"
EXTENSION_DECRYPTE = ".nsd"


class Export():
    def __init__(self):
        self.dictTables = {

            "parametres":[      ("IDparametre", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID du paramètre")),
                                            ("nom", "VARCHAR(400)", _(u"Nom du paramètre")),
                                            ("valeur", "VARCHAR(400)", _(u"Valeur du paramètre")),
                                            ],

            "individus":[            ("IDindividu", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID de la personne")),
                                            ("IDcivilite", "INTEGER", _(u"Civilité de la personne")),
                                            ("nom", "VARCHAR(100)", _(u"Nom de famille de la personne")),
                                            ("prenom", "VARCHAR(100)", _(u"Prénom de la personne")),
                                            ("photo", "BLOB", _(u"Photo de la personne")),
                                            ],

            "titulaires":[           ("IDtitulaires", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID de la ligne")),
                                            ("IDfamille", "INTEGER", _(u"ID de la famille")),
                                            ("nom", "VARCHAR(450)", _(u"Nom des titulaires")),
                                            ],

            "informations":[      ("IDinfo", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID de la ligne")),
                                            ("IDindividu", "INTEGER", _(u"ID de la personne")),
                                            ("champ", "VARCHAR(500)", _(u"Nom du champ")),
                                            ("valeur", "VARCHAR(500)", _(u"Valeur du champ")),
                                            ],
                                            
            "organisateur":[      ("IDorganisateur", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID de l'organisateur")),
                                            ("nom", "VARCHAR(200)", _(u"Nom de l'organisateur")),
                                            ("logo", "BLOB", _(u"Logo de l'organisateur")),
                                            ],

            }

    def Enregistrer(self, db, nomTable, listeChamps, listeDonnees):
        txtChamps = ", ".join(listeChamps)
        txtQMarks = ", ".join(["?" for x in listeChamps])
        req = "INSERT INTO %s (%s) VALUES (%s)" % (nomTable, txtChamps, txtQMarks)
        db.cursor.executemany(req, listeDonnees)
    
    def GetChampsTable(self, nomTable=""):
        listeChamps = []
        for listeInfos in TABLES.DB_DATA[nomTable] :
            listeChamps.append(listeInfos)
        return listeChamps
    
    def CopieTable(self, dbdest, nomTable=""):
        DB = GestionDB.DB()
        
        # Création de la table
        dbdest.CreationTable(nomTable=nomTable, dicoDB=TABLES.DB_DATA)

        # Préparation des champs
        listeChamps = []
        liste_champs_blob = []
        index = 0
        for nom, type_champ, info in TABLES.DB_DATA[nomTable] :
            if "BLOB" in type_champ :
                liste_champs_blob.append(index)
            listeChamps.append(nom)
            index += 1
        
        # Lecture des données
        req = """SELECT %s FROM %s;""" % (", ".join(listeChamps), nomTable)
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        listeDonnees = []
        for listeValeurs in listeTemp :
            liste_temp = []
            index = 0
            for valeur in listeValeurs :
                if valeur != None and index in liste_champs_blob :
                    valeur = sqlite3.Binary(valeur)
                liste_temp.append(valeur)
                index += 1
            listeDonnees.append(liste_temp)

        self.Enregistrer(dbdest, nomTable=nomTable, listeChamps=listeChamps, listeDonnees=listeDonnees)
    
    def CopieTables(self, dbdest, listeTables=[]):
        for nomTable in listeTables :
            self.CopieTable(dbdest, nomTable=nomTable)
    
    def GetParametres(self):
        # Recherche des paramètres
        DB = GestionDB.DB()
        req = """SELECT IDparametre, nom, parametre 
        FROM parametres;"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close() 
        dictParametres = {}
        for IDparametre, nom, valeur in listeTemp :
            dictParametres[nom] = valeur
        dictParametres["horodatage"] = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        return dictParametres

    def Run(self, afficherDlgAttente=False):
        dictParametres = self.GetParametres() 
        
        # Ouverture dlg d'attente
        if afficherDlgAttente == True :
            dlgAttente = wx.BusyInfo(_(u"Génération du fichier de données..."), None)
        
        try :
            
            # Génération du nom de fichier
            self.nomFichier = UTILS_Fichiers.GetRepTemp(fichier=u"data_%s" % dictParametres["IDfichier"])

            # Vérifie si le fichier existe déjà
            nomFichierTemp = self.nomFichier + ".dat"
            if os.path.isfile(nomFichierTemp) :
                os.remove(nomFichierTemp) 
                
            # Création des tables
            dbdest = GestionDB.DB(suffixe=None, nomFichier=nomFichierTemp, modeCreation=True)
            dbdest.CreationTables(dicoDB=self.dictTables)

            # Enregistrement des paramètres
            listeParametres = [
                ("IDfichier", dictParametres["IDfichier"]),
                ("horodatage", dictParametres["horodatage"]),
                ("type", "donnees"),
                ]
            self.Enregistrer(dbdest, nomTable="parametres", listeChamps=["nom", "valeur"], listeDonnees=listeParametres)
            
            # Données du dictIndividus
            from Utils import UTILS_Infos_individus
            infos = UTILS_Infos_individus.Informations()
            dictValeurs = infos.GetDictValeurs(mode="individu", formatChamp=False)
            listeDonnees = []
            for ID, dictTemp in dictValeurs.items() :
                for champ, valeur in dictTemp.items() :
                    if type(valeur) in (str, six.text_type) and valeur not in ("", None) :
                        listeDonnees.append((ID, champ, valeur))
            
            self.Enregistrer(dbdest, nomTable="informations", listeChamps=["IDindividu", "champ", "valeur"], listeDonnees=listeDonnees)
            
            # Données individus
            db = GestionDB.DB(suffixe="PHOTOS")
            req = """SELECT IDindividu, photo FROM photos;"""
            db.ExecuterReq(req)
            listePhotos = db.ResultatReq()
            db.Close()
            dictPhotos = {}
            for IDindividu, photo in listePhotos :
                dictPhotos[IDindividu] = photo

            db = GestionDB.DB()
            req = """SELECT IDindividu, IDcivilite, nom, prenom FROM individus;"""
            db.ExecuterReq(req)
            listeIndividus = db.ResultatReq()
            db.Close()
            listeDonnees = []
            for IDindividu, IDcivilite, nom, prenom in listeIndividus :
                if IDindividu in dictPhotos :
                    photo = sqlite3.Binary(dictPhotos[IDindividu])
                else :
                    photo = None
                listeDonnees.append((IDindividu, IDcivilite, nom, prenom, photo))

            self.Enregistrer(dbdest, nomTable="individus", listeChamps=["IDindividu", "IDcivilite", "nom", "prenom", "photo"], listeDonnees=listeDonnees)
            
            # Données Titulaires de dossier
            dictTitulaires = UTILS_Titulaires.GetTitulaires()
            listeDonnees = []
            for IDfamille, dictTemp in dictTitulaires.items() :
                nom = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                listeDonnees.append((IDfamille, nom))
            
            self.Enregistrer(dbdest, nomTable="titulaires", listeChamps=["IDfamille", "nom"], listeDonnees=listeDonnees)

            # Données organisateur
            db = GestionDB.DB()
            req = """SELECT IDorganisateur, nom, logo FROM organisateur;"""
            db.ExecuterReq(req)
            listeTemp = db.ResultatReq()
            db.Close()
            listeDonnees = []
            for IDorganisateur, nom, logo in listeTemp :
                if logo != None :
                    logo = sqlite3.Binary(logo)
                listeDonnees.append((IDorganisateur, nom, logo))
            
            self.Enregistrer(dbdest, nomTable="organisateur", listeChamps=["IDorganisateur", "nom", "logo"], listeDonnees=listeDonnees)
            
            # Tables à copier en intégralité
            listeTables = [
                "vacances", "jours_feries", "activites", "groupes", "unites", "unites_groupes", "unites_incompat", "unites_remplissage", "unites_remplissage_unites", "ouvertures", "remplissage",
                "inscriptions", "consommations", "memo_journee", "comptes_payeurs", "familles", "utilisateurs", "nomade_archivage",
                "niveaux_scolaires", "ecoles", "classes", "scolarite",
                ]
            self.CopieTables(dbdest, listeTables)
            
            # Cloture de la base
            dbdest.connexion.commit()
            dbdest.Close() 
            
            # Compression
            fichierZip = zipfile.ZipFile(self.nomFichier + EXTENSION_DECRYPTE, "w", compression=zipfile.ZIP_DEFLATED)
            fichierZip.write(self.nomFichier + ".dat", "database.dat")
            fichierZip.close()
            os.remove(self.nomFichier + ".dat")
            
            # Cryptage
            cryptage_actif = UTILS_Config.GetParametre("synchro_cryptage_activer", defaut=False)
            cryptage_mdp = base64.b64decode(UTILS_Config.GetParametre("synchro_cryptage_mdp", defaut=""))
            if six.PY3:
                cryptage_mdp = cryptage_mdp.decode()
            if cryptage_actif == True and cryptage_mdp != "" :
                ancienne_methode = UTILS_Customize.GetValeur("version_cryptage", "nomadhys", "1", ajouter_si_manquant=False) in ("1", None)
                UTILS_Cryptage_fichier.CrypterFichier(self.nomFichier + EXTENSION_DECRYPTE, self.nomFichier + EXTENSION_CRYPTE, cryptage_mdp, ancienne_methode=ancienne_methode)
                os.remove(self.nomFichier + EXTENSION_DECRYPTE)
                nomFichierFinal = self.nomFichier + EXTENSION_CRYPTE
            else :
                nomFichierFinal = self.nomFichier + EXTENSION_DECRYPTE
        
        except Exception as err :
            print("Erreur dans UTILS_Export_nomade.Run :", err)
            traceback.print_exc(file=sys.stdout)
            if afficherDlgAttente == True :
                del dlgAttente
            dlg = wx.MessageDialog(None, _(u"Désolé, l'erreur suivante a été rencontrée : ") + str(err), "Erreur ", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return None

        if afficherDlgAttente == True :
            del dlgAttente
        return nomFichierFinal
        
    def EnvoyerVersRepertoire(self, nomFichier=""):
        standardPath = wx.StandardPaths.Get()
        wildcard = _(u"Fichiers de synchronisation Noethys (*%s, *%s)|*%s;*%s|Tous les fichiers (*.*)|*.*") % (EXTENSION_CRYPTE, EXTENSION_DECRYPTE, EXTENSION_CRYPTE, EXTENSION_DECRYPTE)
        dlg = wx.FileDialog(None, message=_(u"Choisissez un emplacement"), defaultDir=standardPath.GetDocumentsDir(),  defaultFile=os.path.basename(nomFichier), wildcard=wildcard, style=wx.FD_SAVE)
        chemin = None
        if dlg.ShowModal() == wx.ID_OK:
            chemin = dlg.GetPath()
        dlg.Destroy()
        if chemin != None :
            shutil.copyfile(nomFichier, chemin)
            
    def EnvoyerVersFTP(self, nomFichier=""):
        # Récupération des paramètres
        hote = UTILS_Config.GetParametre("synchro_ftp_hote", defaut="")
        identifiant = UTILS_Config.GetParametre("synchro_ftp_identifiant", defaut="")
        mdp = base64.b64decode(UTILS_Config.GetParametre("synchro_ftp_mdp", defaut=""))
        repertoire = UTILS_Config.GetParametre("synchro_ftp_repertoire", defaut="")
        if six.PY3:
            mdp = mdp.decode("utf-8")

        # Envoyer le fichier
        dlgAttente = wx.BusyInfo(_(u"Envoi du fichier de données vers un répertoire FTP..."), None)
        try :
            ftp = ftplib.FTP(hote, identifiant, mdp)
            ftp.cwd(repertoire)
            fichier = open(nomFichier, "rb")
            ftp.storbinary("STOR %s" % os.path.basename(nomFichier), fichier)
            fichier.close()
            ftp.quit()
        except Exception as err :
            print(err)
            del dlgAttente
            dlg = wx.MessageDialog(None, _(u"Le fichier n'a pas pu être envoyé !\n\nVérifiez les paramètres de connexion FTP dans les paramètres de synchronisation."), "Erreur ", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        del dlgAttente
        dlg = wx.MessageDialog(None, _(u"Le fichier a été envoyé avec succès !"), u"Succès", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True
    

        
if __name__ == '__main__':
    app = wx.App(0)
    export = Export()
    nomFichier = export.Run(afficherDlgAttente=False)
    print("nomFichier =", nomFichier)
    print("fini")
    # Envoi vers un répertoire
##    export.EnvoyerVersRepertoire(nomFichier) 
##    export.EnvoyerVersFTP(nomFichier)
    app.MainLoop()
    