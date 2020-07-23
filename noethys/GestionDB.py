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
import sys
import sqlite3
import wx
import os
import base64
import datetime
import random
import six
from Data import DATA_Tables as Tables
from Utils import UTILS_Fichiers

MODE_TEAMWORKS = False
DICT_CONNEXIONS = {}

# Import MySQLdb
try :
    import MySQLdb
    from MySQLdb.constants import FIELD_TYPE
    from MySQLdb.converters import conversions
    IMPORT_MYSQLDB_OK = True
except Exception as err :
    IMPORT_MYSQLDB_OK = False

# import mysql.connector
try :
    import mysql.connector
    from mysql.connector.constants import FieldType
    from mysql.connector import conversion
    IMPORT_MYSQLCONNECTOR_OK = True
except Exception as err :
    IMPORT_MYSQLCONNECTOR_OK = False


# Interface pour Mysql = "mysql.connector" ou "mysqldb"
# Est modifié automatiquement lors du lancement de Noethys selon les préférences (Menu Paramétrage > Préférences)
# Peut être également modifié manuellement ici dans le cadre de tests sur des fichiers indépendamment de l'interface principale 
INTERFACE_MYSQL = "mysqldb"
POOL_MYSQL = 5

def SetInterfaceMySQL(nom="mysqldb", pool_mysql=5):
    """ Permet de sélectionner une interface MySQL """
    global INTERFACE_MYSQL, POOL_MYSQL
    if nom == "mysqldb" and IMPORT_MYSQLDB_OK == True :
        INTERFACE_MYSQL = "mysqldb"
    if nom == "mysql.connector" and IMPORT_MYSQLCONNECTOR_OK == True :
        INTERFACE_MYSQL = "mysql.connector"
    POOL_MYSQL = pool_mysql

# Vérifie si les certificats SSL sont présents dans le répertoire utilisateur
def GetCertificatsSSL():
    dict_certificats = {}
    liste_fichiers = [("ca", "ca-cert.pem"), ("key", "client-key.pem"), ("cert", "client-cert.pem"),]
    for nom, fichier in liste_fichiers :
        chemin_fichier = UTILS_Fichiers.GetRepUtilisateur(fichier)
        if os.path.isfile(chemin_fichier):
            dict_certificats[nom] = chemin_fichier
    return dict_certificats

CERTIFICATS_SSL = GetCertificatsSSL()




class DB:
    def __init__(self, suffixe="DATA", nomFichier="", modeCreation=False, IDconnexion=None, pooling=True):
        """ Utiliser GestionDB.DB(suffixe="PHOTOS") pour accéder à un fichier utilisateur """
        """ Utiliser GestionDB.DB(nomFichier=Chemins.GetStaticPath("Databases/Geographie.dat"), suffixe=None) pour ouvrir un autre type de fichier """
        self.nomFichier = nomFichier
        self.modeCreation = modeCreation
        self.pooling = pooling
        
        # Mémorisation de l'ouverture de la connexion et des requêtes
        if IDconnexion == None :
            self.IDconnexion = random.randint(0, 1000000)
        else :
            self.IDconnexion = IDconnexion
        DICT_CONNEXIONS[self.IDconnexion] = []
        
        # Si aucun nom de fichier n'est spécifié, on recherche celui par défaut dans le Config
        if self.nomFichier == "" :
            self.nomFichier = self.GetNomFichierDefaut()
        
        # On ajoute le préfixe de type de fichier et l'extension du fichier
        if MODE_TEAMWORKS == True and suffixe not in ("", None):
            if suffixe[0] != "T":
                suffixe = _(u"T%s") % suffixe

        if suffixe != None :
            self.nomFichier += u"_%s" % suffixe
        
        # Est-ce une connexion réseau ?
        if "[RESEAU]" in self.nomFichier :
            self.isNetwork = True
        else:
            self.isNetwork = False
            if suffixe != None :
                self.nomFichier = UTILS_Fichiers.GetRepData(u"%s.dat" % self.nomFichier)
        
        # Ouverture de la base de données
        if self.isNetwork == True :
            self.OuvertureFichierReseau(self.nomFichier, suffixe)
        else:
            self.OuvertureFichierLocal(self.nomFichier)
    
    def GetNomPosteReseau(self):
        if self.isNetwork == False :
            return None
        return self.GetParamConnexionReseau()["user"]
        
    def OuvertureFichierLocal(self, nomFichier):
        """ Version LOCALE avec SQLITE """
        # Vérifie que le fichier sqlite existe bien
        if self.modeCreation == False :
            if os.path.isfile(nomFichier)  == False :
                #print "Le fichier SQLITE demande n'est pas present sur le disque dur."
                self.echec = 1
                return
        # Initialisation de la connexion
        try :
            self.connexion = sqlite3.connect(nomFichier.encode('utf-8'))
            self.cursor = self.connexion.cursor()
        except Exception as err:
            print("La connexion avec la base de donnees SQLITE a echouee : \nErreur detectee :%s" % err)
            self.erreur = err
            self.echec = 1
        else:
            self.echec = 0
    
    def GetParamConnexionReseau(self):
        """ Récupération des paramètres de connexion si fichier MySQL """
        pos = self.nomFichier.index("[RESEAU]")
        paramConnexions = self.nomFichier[:pos]
        port, host, user, passwd = paramConnexions.split(";")
        nomFichier = self.nomFichier[pos:].replace("[RESEAU]", "")
        nomFichier = nomFichier.lower() 
        dictDonnees = {"port":int(port), "hote":host, "host":host, "user":user, "utilisateur":user, "mdp":passwd, "password":passwd, "fichier":nomFichier}
        return dictDonnees

    def OuvertureFichierReseau(self, nomFichier, suffixe):
        """ Version RESEAU avec MYSQL """
        self.echec = 0

        try :
            self.connexion, nomFichier = GetConnexionReseau(nomFichier, self.pooling)
            self.cursor = self.connexion.cursor()
        except Exception as err:
            print("La connexion a MYSQL a echouee. Erreur :")
            print((err,))
            self.erreur = err
            self.echec = 1
            return

        # Création
        if self.modeCreation == True :
            try:
                self.cursor.execute("CREATE DATABASE IF NOT EXISTS %s CHARSET utf8 COLLATE utf8_unicode_ci;" % nomFichier)
            except Exception as err:
                print("La creation de la base MYSQL a echouee. Erreur :")
                print((err,))
                self.erreur = err
                self.echec = 1
                return

        # Utilisation
        if nomFichier not in ("", None, "_data") :
            try:
                self.cursor.execute("USE %s;" % nomFichier)
            except Exception as err:
                print("L'ouverture de la base MYSQL a echouee. Erreur :")
                print((err,))
                self.erreur = err
                self.echec = 1
                self.Close()

    def GetNomFichierDefaut(self):
        nomFichier = ""
        try :
            topWindow = wx.GetApp().GetTopWindow()
            nomWindow = topWindow.GetName()
        except :
            nomWindow = None
        if nomWindow == "general" : 
            # Si la frame 'General' est chargée, on y récupère le dict de config
            nomFichier = topWindow.userConfig["nomFichier"]
        else:
            # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
            from Utils import UTILS_Config
            cfg = UTILS_Config.FichierConfig()
            nomFichier = cfg.GetItemConfig("nomFichier")
        return nomFichier
    
    def GetListeDatabasesMySQL(self):
        # Récupère la liste des databases présentes
        listeDatabases = []
        self.cursor.execute("SHOW DATABASES;")
        listeValeurs = self.cursor.fetchall()
        for valeurs in listeValeurs :
            listeDatabases.append(valeurs[0])
        return listeDatabases

    def GetVersionServeur(self):
        req = """SHOW VARIABLES LIKE "version";"""
        self.ExecuterReq(req)
        listeTemp = self.ResultatReq()
        if len(listeTemp) > 0:
            return listeTemp[0][1]
        return None

    def CreationTables(self, dicoDB={}, fenetreParente=None):
        for table in dicoDB:
            # Affichage dans la StatusBar
            if fenetreParente != None :
                fenetreParente.SetStatusText(_(u"Création de la table de données %s...") % table)
            req = "CREATE TABLE %s (" % table
            pk = ""
            for descr in dicoDB[table]:
                nomChamp = descr[0]
                typeChamp = descr[1]
                # Adaptation à Sqlite
                if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
                if self.isNetwork == False and typeChamp == "BIGINT": typeChamp = "INTEGER"
                # Adaptation à MySQL :
                if self.isNetwork == True and typeChamp == "INTEGER PRIMARY KEY AUTOINCREMENT" : typeChamp = "INTEGER PRIMARY KEY AUTO_INCREMENT"
                if self.isNetwork == True and typeChamp == "FLOAT" : typeChamp = "REAL"
                if self.isNetwork == True and typeChamp == "DATE" : typeChamp = "VARCHAR(10)"
                if self.isNetwork == True and typeChamp.startswith("VARCHAR") :
                    nbreCaract = int(typeChamp[typeChamp.find("(")+1:typeChamp.find(")")])
                    if nbreCaract > 255 :
                        typeChamp = "TEXT(%d)" % nbreCaract
                    if nbreCaract > 20000 :
                        typeChamp = "MEDIUMTEXT"
                # ------------------------------
                req = req + "%s %s, " % (nomChamp, typeChamp)
            req = req[:-2] + ")"
            self.cursor.execute(req)

    def CreationTable(self, nomTable="", dicoDB={}):
        req = "CREATE TABLE %s (" % nomTable
        pk = ""
        for descr in dicoDB[nomTable]:
            nomChamp = descr[0]
            typeChamp = descr[1]
            # Adaptation à Sqlite
            if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
            if self.isNetwork == False and typeChamp == "BIGINT": typeChamp = "INTEGER"
            # Adaptation à MySQL :
            if self.isNetwork == True and typeChamp == "INTEGER PRIMARY KEY AUTOINCREMENT" : typeChamp = "INTEGER PRIMARY KEY AUTO_INCREMENT"
            if self.isNetwork == True and typeChamp == "FLOAT" : typeChamp = "REAL"
            if self.isNetwork == True and typeChamp == "DATE" : typeChamp = "VARCHAR(10)"
            if self.isNetwork == True and typeChamp.startswith("VARCHAR") :
                nbreCaract = int(typeChamp[typeChamp.find("(")+1:typeChamp.find(")")])
                if nbreCaract > 255 :
                    typeChamp = "TEXT(%d)" % nbreCaract
                if nbreCaract > 20000 :
                    typeChamp = "MEDIUMTEXT"

            # ------------------------------
            req = req + "%s %s, " % (nomChamp, typeChamp)
        req = req[:-2] + ")"
        self.cursor.execute(req)
            
    def ExecuterReq(self, req):
        if self.echec == 1 : return False
        # Pour parer le pb des () avec MySQL
        if self.isNetwork == True :
            req = req.replace("()", "(10000000, 10000001)")
        try:
            self.cursor.execute(req)
            DICT_CONNEXIONS[self.IDconnexion].append(req)
        except Exception as err:
            print(_(u"Requete SQL incorrecte :\n%s\nErreur detectee:\n%s") % (req, err))
            return 0
        else:
            return 1

    def ResultatReq(self):
        if self.echec == 1 : return []
        resultat = self.cursor.fetchall()
        try :
            # Pour contrer MySQL qui fournit des tuples alors que SQLITE fournit des listes
            if self.isNetwork == True and type(resultat) == tuple : 
                resultat = list(resultat)
        except : 
            pass
        return resultat

    def Commit(self):
        if self.connexion:
            self.connexion.commit()

    def Close(self):
        try :
            self.connexion.close()
        except Exception as err :
            pass

        if self.IDconnexion in DICT_CONNEXIONS :
            del DICT_CONNEXIONS[self.IDconnexion]
                
    def Executermany(self, req="", listeDonnees=[], commit=True):
        """ Executemany pour local ou réseau """    
        """ Exemple de req : "INSERT INTO table (IDtable, nom) VALUES (?, ?)" """  
        """ Exemple de listeDonnees : [(1, 2), (3, 4), (5, 6)] """     
        # Adaptation réseau/local
        if self.isNetwork == True :
            # Version MySQL
            req = req.replace("?", "%s")
        else:
            # Version Sqlite
            req = req.replace("%s", "?")
        # Executemany
        self.cursor.executemany(req, listeDonnees)
        if commit == True :
            self.connexion.commit()

    def Ajouter(self, table, champs, valeurs):
        # champs et valeurs sont des tuples
        req = "INSERT INTO %s %s VALUES %s" % (table, champs, valeurs)
        self.cursor.execute(req)
        self.connexion.commit()

    def ReqInsert(self, nomTable="", listeDonnees=[], commit=True):
        """ Permet d'insérer des données dans une table """
        # Préparation des données
        champs = "("
        interr = "("
        valeurs = []
        for donnee in listeDonnees:
            champs = champs + donnee[0] + ", "
            if self.isNetwork == True :
                # Version MySQL
                interr = interr + "%s, "
            else:
                # Version Sqlite
                interr = interr + "?, "
            valeurs.append(donnee[1])
        champs = champs[:-2] + ")"
        interr = interr[:-2] + ")"
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, champs, interr)
        
        try:
            # Enregistrement
            self.cursor.execute(req, tuple(valeurs))
            if commit == True :
                self.Commit()
                
            # Récupération de l'ID
            if self.isNetwork == True :
                # Version MySQL
                self.cursor.execute("SELECT LAST_INSERT_ID();")
            else:
                # Version Sqlite
                self.cursor.execute("SELECT last_insert_rowid() FROM %s" % nomTable)
            newID = self.cursor.fetchall()[0][0]
            
        except Exception as err:
            print("Requete sql d'INSERT incorrecte :\n%s\nErreur detectee:\n%s" % (req, err))
        # Retourne l'ID de l'enregistrement créé
        return newID
    
    def InsertPhoto(self, IDindividu=None, blobPhoto=None):
        if self.isNetwork == True :
            # Version MySQL
            if INTERFACE_MYSQL == "mysqldb" :
                blob = MySQLdb.escape_string(blobPhoto)
                sql = "INSERT INTO photos (IDindividu, photo) VALUES (%d, '%s')" % (IDindividu, blob)
                self.cursor.execute(sql)
            if INTERFACE_MYSQL == "mysql.connector" :
                self.cursor.execute("INSERT INTO photos (IDindividu, photo) VALUES (%s, %s)", (IDindividu, blobPhoto))
            self.connexion.commit()
            self.cursor.execute("SELECT LAST_INSERT_ID();")
        else:
            # Version Sqlite
            sql = "INSERT INTO photos (IDindividu, photo) VALUES (?, ?)"
            self.cursor.execute(sql, [IDindividu, sqlite3.Binary(blobPhoto)])
            self.connexion.commit()
            self.cursor.execute("SELECT last_insert_rowid() FROM Photos")
        newID = self.cursor.fetchall()[0][0]
        return newID

    def MAJPhoto(self, IDphoto=None, IDindividu=None, blobPhoto=None):
        if self.isNetwork == True :
            # Version MySQL
            if INTERFACE_MYSQL == "mysqldb" :
                blob = MySQLdb.escape_string(blobPhoto)
                sql = "UPDATE photos SET IDindividu=%d, photo='%s' WHERE IDphoto=%d" % (IDindividu, blob, IDphoto)
                self.cursor.execute(sql)
            if INTERFACE_MYSQL == "mysql.connector" :
                self.cursor.execute("UPDATE photos SET IDindividu=%s, photo=%s WHERE IDphoto=%s", (IDindividu, blobPhoto, IDphoto))
            self.connexion.commit()
        else:
            # Version Sqlite
            sql = "UPDATE photos SET IDindividu=?, photo=? WHERE IDphoto=%d" % IDphoto
            self.cursor.execute(sql, [IDindividu, sqlite3.Binary(blobPhoto)])
            self.connexion.commit()
        return IDphoto

    def MAJimage(self, table=None, key=None, IDkey=None, blobImage=None, nomChampBlob="image"):
        """ Enregistre une image dans les modes de règlement ou emetteurs """
        if self.isNetwork == True :
            # Version MySQL
            if INTERFACE_MYSQL == "mysqldb" :
                if six.PY2:
                    blob = MySQLdb.escape_string(blobImage)
                    sql = "UPDATE %s SET %s='%s' WHERE %s=%d" % (table, nomChampBlob, blob, key, IDkey)
                    self.cursor.execute(sql)
                else:
                    req = "UPDATE %s SET %s=XXBLOBXX WHERE %s=%s" % (table, nomChampBlob, key, IDkey)
                    req = req.replace("XXBLOBXX", "%s")
                    self.cursor.execute(req, (blobImage,))
            # Version Connector
            if INTERFACE_MYSQL == "mysql.connector" :
                req = "UPDATE %s SET %s=XXBLOBXX WHERE %s=%s" % (table, nomChampBlob, key, IDkey)
                req = req.replace("XXBLOBXX", "%s")
                self.cursor.execute(req, (blobImage,))
            self.connexion.commit()
        else:
            # Version Sqlite
            sql = "UPDATE %s SET %s=? WHERE %s=%d" % (table, nomChampBlob, key, IDkey)
            self.cursor.execute(sql, [sqlite3.Binary(blobImage),])
            self.connexion.commit()

    def ReqMAJ(self, nomTable, listeDonnees, nomChampID, ID, IDestChaine=False, commit=True):
        """ Permet d'insérer des données dans une table """
        # Préparation des données
        champs = ""
        valeurs = []
        for donnee in listeDonnees:
            if self.isNetwork == True :
                # Version MySQL
                champs = champs + donnee[0] + "=%s, "
            else:
                # Version Sqlite
                champs = champs + donnee[0] + "=?, "
            valeurs.append(donnee[1])
        champs = champs[:-2]
        if IDestChaine == False :
            req = "UPDATE %s SET %s WHERE %s=%d" % (nomTable, champs, nomChampID, ID)
        else:
            req = "UPDATE %s SET %s WHERE %s='%s'" % (nomTable, champs, nomChampID, ID)

        # Enregistrement
        try:
            self.cursor.execute(req, tuple(valeurs))
            if commit == True :
                self.Commit()
        except Exception as err:
            print(_(u"Requete sql de mise a jour incorrecte :\n%s\nErreur detectee:\n%s") % (req, err))
        
    def ReqDEL(self, nomTable="", nomChampID="", ID="", commit=True, IDestChaine=False):
        """ Suppression d'un enregistrement """
        if IDestChaine == False:
            req = "DELETE FROM %s WHERE %s=%d" % (nomTable, nomChampID, ID)
        else:
            req = "DELETE FROM %s WHERE %s='%s'" % (nomTable, nomChampID, ID)
        try:
            self.cursor.execute(req)
            if commit == True :
                self.Commit()
        except Exception as err:
            print(_(u"Requete sql de suppression incorrecte :\n%s\nErreur detectee:\n%s") % (req, err))
        
    def Modifier(self, table, ID, champs, valeurs, dicoDB, commit=True):
        # champs et valeurs sont des tuples

        # Recherche du nom de champ ID de la table
        nomID = dicoDB[table][0][0]

        # Creation du détail champs/valeurs à modifier
        detail = ""

        # Vérifie s'il y a plusieurs champs à modifier
        if isinstance(champs, tuple):
            x = 0
            while x < len(champs):
                detail = detail + champs[x] + "='" + valeurs[x] + "', "
                x += 1
            detail = detail[:-2]
        else:
            detail = champs + "='" + valeurs + "'"

        req = "UPDATE %s SET %s WHERE %s=%d" % (table, detail, nomID, ID)
        self.cursor.execute(req)
        if commit == True :
            self.connexion.commit()

    def Dupliquer(self, nomTable="", nomChampCle="", conditions="", dictModifications={}, renvoieCorrespondances=False, IDmanuel=False):
        """ Dulpliquer un enregistrement d'une table :
             Ex : nomTable="modeles", nomChampCle="IDmodele", ID=22,
             conditions = "IDmodele=12 AND IDtruc>34",
             dictModifications={"nom" : _(u"Copie de modele"), etc...}
             renvoieCorrespondance = renvoie un dict de type {ancienID : newID, etc...}
             IDmanuel = Attribue le IDprécédent de la table + 1 (pour parer au bug de la table tarifs_ligne
        """
        listeNewID = []
        # Recherche des noms de champs
        listeChamps = []
        for nom, type, info in Tables.DB_DATA[nomTable] :
            listeChamps.append(nom)
            
        # Importation des données
        texteConditions = ""
        if len(conditions) > 0 : 
            texteConditions = "WHERE %s" % conditions
        req = "SELECT * FROM %s %s;" % (nomTable, texteConditions)
        self.ExecuterReq(req)
        listeDonnees = self.ResultatReq()
        if len(listeDonnees) == 0 : 
            return None
            
        # Copie des données
        dictCorrespondances = {}
        for enregistrement in listeDonnees :
            listeTemp = []
            index = 0
            ID = None
            for nomChamp in listeChamps :
                valeur = enregistrement[index]
                if nomChamp in dictModifications:
                    valeur = dictModifications[nomChamp]
                if nomChamp != nomChampCle :
                    listeTemp.append((nomChamp, valeur))
                else:
                    ID = valeur # C'est la clé originale
                    
                    # Si saisie manuelle du nouvel ID
                    if IDmanuel == True :
                        req = """SELECT max(%s) FROM %s;""" % (nomChampCle, nomTable)
                        self.ExecuterReq(req)
                        temp = self.ResultatReq()
                        if temp[0][0] == None : 
                            newIDmanuel = 1
                        else:
                            newIDmanuel = temp[0][0] + 1
                        listeTemp.append((nomChampCle, newIDmanuel))
                        
                index += 1
            newID = self.ReqInsert(nomTable, listeTemp)
            if IDmanuel == True :
                newID = newIDmanuel
            listeNewID.append(newID)
            dictCorrespondances[ID] = newID
            
        # Renvoie les correspondances
        if renvoieCorrespondances == True :
            return dictCorrespondances
        
        # Renvoie les newID
        if len(listeNewID) == 1 :
            return listeNewID[0]
        else:
            return listeNewID

    def GetProchainID(self, nomTable=""):
        if self.isNetwork == False :
            # Version Sqlite
            req = "SELECT seq FROM sqlite_sequence WHERE name='%s';" % nomTable
            self.ExecuterReq(req)
            donnees = self.ResultatReq()

            # Renvoie le prochain ID
            if len(donnees) > 0 :
                return donnees[0][0] + 1

        else:
            # Version MySQL
            # self.ExecuterReq("USE information_schema;")
            # pos = self.nomFichier.index("[RESEAU]")
            # nomFichier = self.nomFichier[pos:].replace("[RESEAU]", "")
            # req = "SELECT auto_increment FROM tables WHERE table_schema='%s' and table_name='%s' ;" % (nomFichier, nomTable)
            # self.ExecuterReq(req)
            # donnees = self.ResultatReq()
            #
            # # Se remet sur le fichier normal
            # if nomFichier not in ("", None, "_data") :
            #     self.ExecuterReq("USE %s;" % nomFichier)

            # 2ème version
            self.ExecuterReq("SHOW TABLE STATUS WHERE name='%s';" % nomTable)
            donnees = self.ResultatReq()
            if len(donnees) > 0 :
                return donnees[0][10]

        return 1
    
    def IsTableExists(self, nomTable=""):
        """ Vérifie si une table donnée existe dans la base """
        tableExists = False
        for (nomTableTmp,) in self.GetListeTables() :
            if nomTableTmp == nomTable :
                tableExists = True
        return tableExists
                        
    def GetListeTables(self):
        if self.isNetwork == False :
            # Version Sqlite
            req = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            self.ExecuterReq(req)
            listeTables = self.ResultatReq()
        else:
            # Version MySQL
            req = "SHOW TABLES;"
            self.ExecuterReq(req)
            listeTables = self.ResultatReq()
        return listeTables

    def GetListeChamps(self):
        """ Affiche la liste des champs de la précédente requête effectuée """
        liste = []
        for fieldDesc in self.cursor.description:
            liste.append(fieldDesc[0])
        return liste

    def GetListeChamps2(self, nomTable=""):
        """ Affiche la liste des champs de la table donnée """
        listeChamps = []
        if self.isNetwork == False :
            # Version Sqlite
            req = "PRAGMA table_info('%s');" % nomTable
            self.ExecuterReq(req)
            listeTmpChamps = self.ResultatReq()
            for valeurs in listeTmpChamps :
                listeChamps.append( (valeurs[1], valeurs[2]) )
        else:
            # Version MySQL
            req = "SHOW COLUMNS FROM %s;" % nomTable
            self.ExecuterReq(req)
            listeTmpChamps = self.ResultatReq()
            for valeurs in listeTmpChamps :
                listeChamps.append( (valeurs[0], valeurs[1]) )
        return listeChamps
    
    def SupprChamp(self, nomTable="", nomChamp = ""):
        """ Suppression d'une colonne dans une table """
        if self.isNetwork == False :
            # Version Sqlite

            # Recherche des noms de champs de la table
    ##        req = """
    ##        SELECT sql FROM sqlite_master
    ##        WHERE name='%s'
    ##        """ % nomTable
    ##        self.ExecuterReq(req)
    ##        reqCreate = self.ResultatReq()[0][0]
    ##        posDebut = reqCreate.index("(")+1
    ##        champs = reqCreate[posDebut:-1]
    ##        listeChamps = champs.split(", ")
            
            listeChamps = self.GetListeChamps2(nomTable)
        
            index = 0
            varChamps = ""
            varNomsChamps = ""
            for nomTmp, typeTmp in listeChamps :
                if nomTmp == nomChamp :
                    listeChamps.pop(index)
                    break
                else:
                    varChamps += "%s %s, " % (nomTmp, typeTmp)
                    varNomsChamps += nomTmp + ", "
                index += 1
            varChamps = varChamps[:-2]
            varNomsChamps = varNomsChamps[:-2]
        
            # Procédure de mise à jour de la table                
            req = ""
            req += "BEGIN TRANSACTION;"
            req += "CREATE TEMPORARY TABLE %s_backup(%s);" % (nomTable, varChamps)
            req += "INSERT INTO %s_backup SELECT %s FROM %s;" % (nomTable, varNomsChamps, nomTable)
            req += "DROP TABLE %s;" % nomTable
            req += "CREATE TABLE %s(%s);" % (nomTable, varChamps)
            req += "INSERT INTO %s SELECT %s FROM %s_backup;" % (nomTable, varNomsChamps, nomTable)
            req += "DROP TABLE %s_backup;" % nomTable
            req += "COMMIT;"
            self.cursor.executescript(req)
        
        else:
            # Version MySQL
            req = "ALTER TABLE %s DROP %s;" % (nomTable, nomChamp)
            self.ExecuterReq(req)
            self.Commit()
            
    def AjoutChamp(self, nomTable = "", nomChamp = "", typeChamp = ""):
        req = "ALTER TABLE %s ADD %s %s;" % (nomTable, nomChamp, typeChamp)
        self.ExecuterReq(req)
        self.Commit()

    def ReparationTable(self, nomTable="", dicoDB=Tables.DB_DATA):
        """ Réparation d'une table (re-création de la table) """
        if self.isNetwork == False :
            # Récupération des noms et types de champs
            listeChamps = []
            listeNomsChamps = []
            for descr in dicoDB[nomTable]:
                nomChamp = descr[0]
                typeChamp = descr[1]
                if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
                if self.isNetwork == False and typeChamp == "BIGINT": typeChamp = "INTEGER"
                listeChamps.append("%s %s" % (nomChamp, typeChamp))
                listeNomsChamps.append(nomChamp)
            varChamps = ", ".join(listeChamps)
##            varNomsChamps = ", ".join(listeNomsChamps)

            # Procédure de mise à jour de la table
##            req = "BEGIN TRANSACTION;"
##            req += "CREATE TEMPORARY TABLE %s_backup(%s);" % (nomTable, varChamps)
##            req += "INSERT INTO %s_backup SELECT %s FROM %s;" % (nomTable, ", ".join(listeNomsChamps[1:]), nomTable)
##            req += "DROP TABLE %s;" % nomTable
##            req += "CREATE TABLE %s(%s);" % (nomTable, varChamps)
##            req += "INSERT INTO %s SELECT %s FROM %s_backup;" % (nomTable, ", ".join(listeNomsChamps[1:]), nomTable)
##            req += "DROP TABLE %s_backup;" % nomTable
##            req += "COMMIT;"
            
            # Création de la table temporaire
            req = "BEGIN TRANSACTION;"
            req += "CREATE TEMPORARY TABLE %s_backup(%s);" % (nomTable, varChamps.replace(" PRIMARY KEY AUTOINCREMENT", ""))
            req += "INSERT INTO %s_backup SELECT %s FROM %s;" % (nomTable, ", ".join(listeNomsChamps), nomTable)
            req += "DROP TABLE %s;" % nomTable
            req += "CREATE TABLE %s(%s);" % (nomTable, varChamps)
            req += "COMMIT;"
            self.cursor.executescript(req)
            
            # Copie des données dans la table temporaire
            req = "SELECT %s FROM %s_backup;" % (", ".join(listeNomsChamps[1:]), nomTable)
            self.cursor.execute(req)
            listeDonnees = self.cursor.fetchall()
            
            for ligne in listeDonnees :
                temp = []
                for x in range(0, len(ligne)) :
                    temp.append("?")
                req = "INSERT INTO %s (%s) VALUES (%s)" % (nomTable, ", ".join(listeNomsChamps[1:]), ", ".join(temp))
                self.cursor.execute(req, ligne)
                self.Commit() 
            
            # Suppression de la table temporaire
            self.cursor.execute("DROP TABLE %s_backup;" % nomTable)
            self.Commit() 
            
            print("Reparation de la table '%s' terminee." % nomTable)

    def Importation_table(self, nomTable="", nomFichierdefault=Chemins.GetStaticPath("Databases/Defaut.dat"), mode="local"):
        """ Importe toutes les données d'une table donnée """
        # Ouverture de la base par défaut
        if mode == "local" :

            if os.path.isfile(nomFichierdefault)  == False :
                print("Le fichier n'existe pas.")
                return (False, _(u"Le fichier n'existe pas"))

            try:
                connexionDefaut = sqlite3.connect(nomFichierdefault.encode('utf-8'))
            except Exception as err:
                print("Echec Importation table. Erreur detectee :%s" % err)
                return (False, "Echec Importation table. Erreur detectee :%s" % err)
            else:
                cursor = connexionDefaut.cursor()

        else :
            
            try :
                connexionDefaut, nomFichier = GetConnexionReseau(nomFichierdefault)
                cursor = connexionDefaut.cursor()
                
                # Ouverture Database
                cursor.execute("USE %s;" % nomFichier)
                
            except Exception as err:
                print("La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err)
                return (False, "La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err)

        # Recherche des noms de champs de la table
        req = "SELECT * FROM %s" % nomTable
        cursor.execute(req)
        listeDonneesTmp = cursor.fetchall()
        listeNomsChamps = []
        for fieldDesc in cursor.description:
            listeNomsChamps.append(fieldDesc[0])
            
        # Préparation des noms de champs pour le transfert
        listeChamps = []
        listeMarks = []
        dictTypesChamps = GetChampsTable(nomTable)
        for nomChamp in listeNomsChamps[0:] :
            if nomChamp in dictTypesChamps:
                listeChamps.append(nomChamp)
                if self.isNetwork == True :
                    # Version MySQL
                    listeMarks.append("%s")
                else:
                    # Version Sqlite
                    listeMarks.append("?")

        # Récupération des données
        req = "SELECT %s FROM %s" % (", ".join(listeChamps), nomTable)
        cursor.execute(req)
        listeDonnees = cursor.fetchall()

        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s (%s) VALUES (%s)" % (nomTable, ", ".join(listeChamps), ", ".join(listeMarks))
        try :
            self.cursor.executemany(req, listeDonnees)
        except Exception as err :
            print("Erreur dans l'importation de la table %s :" % nomTable)
            print(err)
            return (False, "Erreur dans l'importation de la table %s : %s" % (nomTable, err))
        self.connexion.commit()
        return (True, None)

    def Importation_table_reseau(self, nomTable="", nomFichier="", dictTables={}):
        """ Importe toutes les données d'une table donnée dans un fichier réseau """
        # Ouverture de la base réseau
        try :
            connexionDefaut, nomFichier = GetConnexionReseau(nomFichier)
            cursor = connexionDefaut.cursor()

            # Ouverture Database
            cursor.execute("USE %s;" % nomFichier)

        except Exception as err:
            print("La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err)
            return (False, "La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err)

        # Recherche des noms de champs de la table
        req = "SELECT * FROM %s" % nomTable
        cursor.execute(req)
        listeDonneesTmp = cursor.fetchall()

        # Lecture des champs
        listeChamps = []
        req = "SHOW COLUMNS FROM %s;" % nomTable
        cursor.execute(req)
        listeTmpChamps = cursor.fetchall()
        for valeurs in listeTmpChamps:
            listeChamps.append((valeurs[0], valeurs[1]))

        # Préparation des noms de champs pour le transfert
        txtChamps = "(" + ", ".join([nomChamp for nomChamp, typeChamp in listeChamps]) + ")"
        txtQMarks = "(" + ", ".join(["?" for nomChamp, typeChamp in listeChamps]) + ")"

        # Récupération des données
        listeDonnees = []
        for donnees in listeDonneesTmp :
            # Analyse des données pour trouver les champs BLOB
            numColonne = 0
            listeValeurs = []
            for donnee in donnees[0:] :
                nomChamp, typeChamp = listeChamps[numColonne]
                if "BLOB" in typeChamp.upper() :
                    if donnee != None :
                        donnee = sqlite3.Binary(donnee)
                listeValeurs.append(donnee)
                numColonne += 1
            listeDonnees.append(tuple(listeValeurs))

        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, txtChamps, txtQMarks)
        self.cursor.executemany(req, listeDonnees)
        self.connexion.commit()
        connexionDefaut.close()
        return (True, None)

    def Importation_valeurs_defaut(self, listeDonnees=[]):
        """ Importe dans la base de données chargée toutes les valeurs de la base des valeurs par défaut """
        # Récupération du dictionnaire des tables Optionnelles pour l'importation
        if len(listeDonnees) == 0 :
            listeTablesOptionnelles = Tables.TABLES_IMPORTATION_OPTIONNELLES # DICT_TABLES_IMPORTATION
        else:
            listeTablesOptionnelles = listeDonnees
        
        # Importation des tables optionnelles
        for nomCategorie, listeTables, selection in listeTablesOptionnelles :
            if selection == True :
                for nomTable in listeTables :
                    self.Importation_table(nomTable)
        
        # Importation des tables obligatoires
        for nomTable in Tables.TABLES_IMPORTATION_OBLIGATOIRES :
            self.Importation_table(nomTable)

        return True

    def ConversionTypeChamp(self, nomTable="", nomChamp="", typeChamp=""):
        """ Pour convertir le type d'un champ """
        """ Ne fonctionne qu'avec MySQL """
        if self.isNetwork == True :
            req = "ALTER TABLE %s CHANGE %s %s %s;" % (nomTable, nomChamp, nomChamp, typeChamp)
            self.ExecuterReq(req)

    def Exportation_vers_base_defaut(self, nomTable="", nomFichierdefault=Chemins.GetStaticPath("Databases/Defaut.dat")):
        """ Exporte toutes les données d'une table donnée vers la base défaut """
        """ ATTENTION, la TABLE défaut sera supprimée !!! """
        # Ouverture de la base par défaut
        connexionDefaut = sqlite3.connect(nomFichierdefault.encode('utf-8'))
        cursorDefaut = connexionDefaut.cursor()
        
        # Supprime la table
        cursorDefaut.execute("DROP TABLE IF EXISTS %s;" % nomTable)
        
        # Création de la table dans la base DEFAUT si elle n'existe pas
        req = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % nomTable
        cursorDefaut.execute(req)
        listeTemp = cursorDefaut.fetchall()
        if len(listeTemp) == 0 :
            req = "CREATE TABLE %s (" % nomTable
            pk = ""
            for descr in Tables.DB_DATA[nomTable]:
                nomChamp = descr[0]
                typeChamp = descr[1]
                if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
                if self.isNetwork == False and typeChamp == "BIGINT": typeChamp = "INTEGER"
                req = req + "%s %s, " % (nomChamp, typeChamp)
            req = req[:-2] + ")"
            cursorDefaut.execute(req)
        
        # Recherche des noms de champs de la table
        listeChamps = self.GetListeChamps2(nomTable)
        
        # Récupération des données à exporter
        req = "SELECT * FROM %s" % nomTable
        self.ExecuterReq(req)
        listeDonnees = self.ResultatReq()
            
        # Préparation des noms de champs pour le transfert
        txtChamps = "("
        txtQMarks = "("
        for nomChamp, typeChamp in listeChamps :
            txtChamps += nomChamp + ", "
            txtQMarks += "?, "
        txtChamps = txtChamps[:-2] + ")"
        txtQMarks = txtQMarks[:-2] + ")"

        # Récupération des données
        listeDonnees2 = []
        for donnees in listeDonnees :
            listeDonnees2.append(donnees[0:])
        
        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, txtChamps, txtQMarks)
        cursorDefaut.executemany(req, listeDonnees2)
        connexionDefaut.commit()
        connexionDefaut.close() 

    def CreationIndex(self, nomIndex=""):
        """ Création d'un index """
        nomTable = Tables.DB_INDEX[nomIndex]["table"]
        nomChamp = Tables.DB_INDEX[nomIndex]["champ"]
        if self.IsTableExists(nomTable) :
            #print "Creation de l'index : %s" % nomIndex
            req = "CREATE INDEX %s ON %s (%s);" % (nomIndex, nomTable, nomChamp)
            self.ExecuterReq(req)
            self.Commit() 
    
    def CreationTousIndex(self):
        """ Création de tous les index """
        for nomIndex, temp in Tables.DB_INDEX.items() :
            self.CreationIndex(nomIndex)





def GetConnexionReseau(nomFichier="", pooling=True):
    pos = nomFichier.index("[RESEAU]")
    paramConnexions = nomFichier[:pos]
    port, host, user, passwd = paramConnexions.split(";")
    nomFichier = nomFichier[pos:].replace("[RESEAU]", "")
    nomFichier = nomFichier.lower()

    passwd = DecodeMdpReseau(passwd)

    if INTERFACE_MYSQL == "mysqldb":
        my_conv = conversions
        my_conv[FIELD_TYPE.LONG] = int
        connexion = MySQLdb.connect(host=host, user=user, passwd=passwd, port=int(port), use_unicode=True, conv=my_conv, ssl=CERTIFICATS_SSL)
        connexion.set_character_set('utf8')

    if INTERFACE_MYSQL == "mysql.connector":
        if "_" in nomFichier :
            suffixe = nomFichier.split("_")[-1]
        else :
            suffixe = ""

        params = {
            "host": host,
            "user": user,
            "passwd": passwd,
            "port": int(port),
            "use_unicode": True,
        }

        # Activation du SSL
        if "ca" in CERTIFICATS_SSL:
            params["ssl_ca"] = CERTIFICATS_SSL["ca"]

        # Activation du pooling
        if POOL_MYSQL > 0 :#and pooling == True:
            params["pool_name"] = "mypool2%s" % suffixe
            params["pool_size"] = POOL_MYSQL

        connexion = mysql.connector.connect(**params)

    return connexion, nomFichier


def GetChampsTable(nomTable=""):
    for dictTables in (Tables.DB_DATA, Tables.DB_PHOTOS, Tables.DB_DOCUMENTS) :
        if nomTable in dictTables :
            dictChamps = {}
            for nom, typeTable, info in dictTables[nomTable] :
                dictChamps[nom] = typeTable
            return dictChamps
    return {}


def ConvertConditionChaine(liste=[]):
    """ Transforme une liste de valeurs en une condition chaine pour requête SQL """
    if len(liste) == 0 : condition = "()"
    elif len(liste) == 1 : condition = "(%d)" % liste[0]
    else : condition = str(tuple(liste))
    return condition


def ConversionLocalReseau(nomFichier="", nouveauFichier="", fenetreParente=None):
    """ Convertit une DB locale en version RESEAU MySQL """
    print("Lancement de la procedure de conversion local->reseau :")
    
    for suffixe, dictTables in ( ("DATA", Tables.DB_DATA), ("PHOTOS", Tables.DB_PHOTOS), ("DOCUMENTS", Tables.DB_DOCUMENTS) ) :
        
        nomFichierActif = UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (nomFichier, suffixe))
        nouveauNom = nouveauFichier[nouveauFichier.index("[RESEAU]"):].replace("[RESEAU]", "")
        
        dictResultats = TestConnexionMySQL(typeTest="fichier", nomFichier=u"%s_%s" % (nouveauFichier, suffixe) )
        # Vérifie la connexion au réseau
        if dictResultats["connexion"][0] == False :
            erreur = dictResultats["connexion"][1]
            print("connexion reseau MySQL impossible.")
            return (False, _(u"La connexion au réseau MySQL est impossible"))
        
        # Vérifie que le fichier n'est pas déjà utilisé
        if dictResultats["fichier"][0] == True :
            print("le nom existe deja.")
            return (False, _(u"Le fichier existe déjà"))
        
        # Création de la base de données
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création du fichier réseau..."))
        db = DB(suffixe=suffixe, nomFichier=nouveauFichier, modeCreation=True)
        if db.echec == 1 :
            message = _(u"Erreur dans la création du fichier.\n\nErreur : %s") % db.erreur
            return (False, message)
        print("  > Nouveau fichier reseau %s cree..." % suffixe)
        
        # Création des tables
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création des tables de données %s...") % suffixe)
        db.CreationTables(dicoDB=dictTables)
        print("  > Nouvelles tables %s creees..." % suffixe)
        
        # Importation des valeurs
        listeTables = list(dictTables.keys())
        index = 1
        for nomTable in listeTables :
            print("  > Importation de la table '%s' (%d/%d)" % (nomTable, index, len(listeTables)))
            if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Importation de la table %d sur %s...") % (index, len(listeTables)))
            resultat = db.Importation_table(nomTable, nomFichierActif)
            if resultat[0] == False :
                db.Close()
                return resultat
            else :
                print("     -> ok")
            index += 1
        
        db.Close() 
    
    print("  > Conversion terminee avec succes.")
    return (True, None)


def ConversionReseauLocal(nomFichier="", nouveauFichier="", fenetreParente=None):
    """ Convertit une DB RESEAU MySQL en version LOCALE SQLITE """
    print("Lancement de la procedure de conversion reseau->local :")
    
    for suffixe, dictTables in ( ("DATA", Tables.DB_DATA), ("PHOTOS", Tables.DB_PHOTOS), ("DOCUMENTS", Tables.DB_DOCUMENTS) ) :
        
        nomFichierActif = nomFichier[nomFichier.index("[RESEAU]"):].replace("[RESEAU]", "") 
        nouveauNom = UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (nomFichier, suffixe))
        
        # Vérifie que le fichier n'est pas déjà utilisé
        if os.path.isfile(nouveauNom)  == True :
            return (False, _(u"Le fichier existe déjà"))
        
        # Création de la base de données
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création du fichier local..."))
        db = DB(suffixe=suffixe, nomFichier=nouveauFichier, modeCreation=True)
        if db.echec == 1 :
            message = _(u"Erreur dans la création du fichier.\n\nErreur : %s") % db.erreur
            return (False, _(u"Le fichier existe déjà"))
        print("  > Nouveau fichier local %s cree..." % suffixe)
        
        # Création des tables
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création des tables de données %s...") % suffixe)
        db.CreationTables(dicoDB=dictTables)
        print("  > Nouvelles tables %s creees..." % suffixe)
        
        # Importation des valeurs
        listeTables = list(dictTables.keys())
        index = 1
        for nomTable in listeTables :
            print("  > Importation de la table '%s' (%d/%d)" % (nomTable, index, len(listeTables)))
            if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Importation de la table %d sur %s...") % (index, len(listeTables)))
            resultat = db.Importation_table_reseau(nomTable, u"%s_%s" % (nomFichier, suffixe), dictTables)
            if resultat[0] == False :
                db.Close()
                return resultat
            else :
                print("     -> ok")
            index += 1
        
        db.Close() 
    
    print("  > Conversion reseau->local terminee avec succes.")
    return (True, None)


def TestConnexionMySQL(typeTest="fichier", nomFichier=""):
    """ typeTest=fichier ou reseau """
    dictResultats = {}
    cursor = None
    connexion = None

    # Test de connexion au réseau MySQL
    try :
        connexion, nomFichier = GetConnexionReseau(nomFichier, pooling=False)
        cursor = connexion.cursor()
        dictResultats["connexion"] =  (True, None)
        connexion_ok = True
    except Exception as err :
        dictResultats["connexion"] =  (False, err)
        connexion_ok = False

    # Test de connexion à une base de données
    if typeTest == "fichier" and connexion_ok == True :
        try :
            listeDatabases = []
            cursor.execute("SHOW DATABASES;")
            listeValeurs = cursor.fetchall()
            for valeurs in listeValeurs :
                listeDatabases.append(valeurs[0])
            if nomFichier in listeDatabases :
                # Ouverture Database
                cursor.execute("USE %s;" % nomFichier)
                # Vérification des tables
                cursor.execute("SHOW TABLES;")
                listeTables = cursor.fetchall()
                if not listeTables:
                    dictResultats["fichier"] = (False, _(u"La base de données est vide."))
                else:
                    dictResultats["fichier"] =  (True, None)
            else:
                dictResultats["fichier"] =  (False, _(u"Accès au fichier impossible."))
        except Exception as err :
            dictResultats["fichier"] =  (False, err)
    
    if connexion != None :
        connexion.close()
    return dictResultats


# ----------------------------------------------------------------------------------------------------------------------------------------
                                
def ImporterFichierDonnees() :
    db = DB(nomFichier=Chemins.GetStaticPath("Databases/Prenoms.dat"), suffixe=None, modeCreation=True)
    db.CreationTable("prenoms", DB_DATA2)
    db.Close()
    
    txt = open("prenoms.txt", 'r').readlines()
    db = DB(nomFichier=Chemins.GetStaticPath("DatabasesPrenoms.dat"), suffixe=None)
    index = 0
    for ligne in txt :
        ID, prenom, genre = ligne.split(";")
        if six.PY2:
            prenom = prenom.decode("iso-8859-15")
            genre = genre.decode("iso-8859-15")
        listeDonnees = [("prenom", prenom), ("genre", genre),]
        IDprenom = db.ReqInsert("prenoms", listeDonnees)
        index += 1
    db.Close()


def CreationBaseAnnonces():
    """ Création de la base de données sqlite pour les Annonces """
    DB_DATA_ANNONCES = {
            "annonces_aleatoires":[             ("IDannonce", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID Annonce")),
                                                            ("image", "VARCHAR(200)", _(u"Nom de l'image")),
                                                            ("titre", "VARCHAR(300)", _(u"Titre")),
                                                            ("texte_html", "VARCHAR(500)", _(u"Texte HTML")),
                                                            ("texte_xml", "VARCHAR(500)", _(u"texte XML")),
                                                            ],

            "annonces_dates":[                   ("IDannonce", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID Annonce")),
                                                            ("date_debut", "DATE", _(u"Date de début")),
                                                            ("date_fin", "DATE", _(u"Date de fin")),
                                                            ("image", "VARCHAR(200)", _(u"Nom de l'image")),
                                                            ("titre", "VARCHAR(300)", _(u"Titre")),
                                                            ("texte_html", "VARCHAR(500)", _(u"Texte HTML")),
                                                            ("texte_xml", "VARCHAR(500)", _(u"texte XML")),
                                                            ],

            "annonces_periodes":[              ("IDannonce", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID Annonce")),
                                                            ("jour_debut", "INTEGER", _(u"Jour début")),
                                                            ("mois_debut", "INTEGER", _(u"Mois début")),
                                                            ("jour_fin", "INTEGER", _(u"Jour fin")),
                                                            ("mois_fin", "INTEGER", _(u"Mois fin")),
                                                            ("image", "VARCHAR(200)", _(u"Nom de l'image")),
                                                            ("titre", "VARCHAR(300)", _(u"Titre")),
                                                            ("texte_html", "VARCHAR(500)", _(u"Texte HTML")),
                                                            ("texte_xml", "VARCHAR(500)", _(u"texte XML")),
                                                            ],

        }
    db = DB(nomFichier=Chemins.GetStaticPath("Databases/Annonces.dat"), suffixe=None, modeCreation=True)
    db.CreationTable("annonces_aleatoires", DB_DATA_ANNONCES)
    db.CreationTable("annonces_dates", DB_DATA_ANNONCES)
    db.CreationTable("annonces_periodes", DB_DATA_ANNONCES)
    db.Close()
    

def AfficheConnexionOuvertes():
    """ Affiche les connexions non fermées """
    if len(DICT_CONNEXIONS) > 0 :
        print("--------- Attention, il reste %d connexions encore ouvertes : ---------" % len(DICT_CONNEXIONS))
        for IDconnexion, requetes in DICT_CONNEXIONS.items() :
            print(">> IDconnexion = %d (%d requetes) :" % (IDconnexion, len(requetes)))
            for requete in requetes :
                print(requete)


def DecodeMdpReseau(mdp=None):
    if mdp not in (None, "") and mdp.startswith("#64#"):
        try:
            mdp = base64.b64decode(mdp[4:])
            if six.PY3:
                mdp = mdp.decode('utf-8')
        except:
            pass
    return mdp

def EncodeMdpReseau(mdp=None):
    if six.PY3:
        mdp = mdp.encode()
    mdp = base64.b64encode(mdp)
    if six.PY3:
        mdp = mdp.decode('utf-8')
    mdp = u"#64#%s" % mdp
    return mdp

def EncodeNomFichierReseau(nom_fichier=None):
    if "[RESEAU]" in nom_fichier and "#64#" not in nom_fichier:
        pos = nom_fichier.index("[RESEAU]")
        parametres = nom_fichier[:pos]
        port, hote, utilisateur, motdepasse = parametres.split(";")
        fichier = nom_fichier[pos:].replace("[RESEAU]", "")
        nouveau_motdepasse = EncodeMdpReseau(motdepasse)
        nom_fichier = u"%s;%s;%s;%s[RESEAU]%s" % (port, hote, utilisateur, nouveau_motdepasse, fichier)
    return nom_fichier



if __name__ == "__main__":
                
    # Création d'une table données
    # db = DB(suffixe="DATA")
    # listeTables = ("portail_reservations_locations",)
    # for nomTable in listeTables :
    #     db.CreationTable(nomTable, Tables.DB_DATA)
    # db.Close()
    # print("creation tables ok.")

    ## ----------------------------------------------------------------------

##    # Création de toutes les tables
    # db = DB(suffixe="DATA", modeCreation=True)
    # import Tables
    # dicoDB = Tables.DB_DATA
    # db.CreationTables(dicoDB)
    # db.Close()
    # print "creation des tables DATA ok."
    # db = DB(suffixe="PHOTOS", modeCreation=True)
    # import Tables
    # dicoDB = Tables.DB_PHOTOS
    # db.CreationTables(dicoDB)
    # db.Close()
    # print "creation des tables PHOTOS ok."
    
##    db = DB(nomFichier="Prenoms.dat", suffixe=None)
##    for IDprenom in range(1, 12555):
##        req = """SELECT prenom, genre FROM prenoms WHERE IDprenom=%d;""" % IDprenom
##        db.ExecuterReq(req)
##        listePrenoms = db.ResultatReq()
##        genre = listePrenoms[0][1]
##        if genre.endswith("\n") :
##            listeDonnees = [ ("genre", genre[:-1]),]
##            db.ReqMAJ("prenoms", listeDonnees, "IDprenom", IDprenom)
##    db.Close()
        
    # # Ajouter un champ
    # db = DB(suffixe="DATA")
    # db.AjoutChamp("factures", "mention3", "VARCHAR(300)")
    # db.Close()

    # # Exportation d'une table dans la base DEFAUT
    # db = DB(suffixe="DATA")
    # db.Exportation_vers_base_defaut(nomTable="modeles_emails")
    # db.Close()
    
    # Réparation d'une table
##    db = DB(suffixe="DATA")
##    db.ReparationTable("tarifs_lignes")
##    db.Close() 
    
    # Test Conversion d'un champ
##    db = DB(suffixe="DATA")
##    db.ConversionTypeChamp(nomTable="factures", nomChamp="numero", typeChamp="VARCHAR(100)")
##    db.Close() 
    
    # Création de tous les index
##    db = DB(suffixe="DATA")
##    db.CreationTousIndex() 
##    db.Close() 
##    db = DB(suffixe="PHOTOS")
##    db.CreationTousIndex() 
##    db.Close() 
    
    # Test d'une connexion MySQL
##    hote = ""
##    utilisateur = ""
##    motdepasse = ""
##    DB = DB(nomFichier=u"3306;%s;%s;%s[RESEAU]" % (hote, utilisateur, motdepasse))
##    if DB.echec == 1 :
##        print "Echec = ", DB.echec
##    else :
##        print "connexion ok"
##    DB.Close()

    pass