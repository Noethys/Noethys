#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import sys
import sqlite3
import wx
import CTRL_Bouton_image
import os
import traceback
import time
import random
import DATA_Tables as Tables

DICT_CONNEXIONS = {}

# Import MySQLdb
try :
    import MySQLdb
    from MySQLdb.constants import FIELD_TYPE
    from MySQLdb.converters import conversions
    IMPORT_MYSQLDB_OK = True
except Exception, err :
    IMPORT_MYSQLDB_OK = False

# import mysql.connector
try :
    import mysql.connector
    from mysql.connector.constants import FieldType
    from mysql.connector import conversion
    IMPORT_MYSQLCONNECTOR_OK = True
except Exception, err :
    IMPORT_MYSQLCONNECTOR_OK = False


# Interface pour Mysql = "mysql.connector" ou "mysqldb"
# Est modifié automatiquement lors du lancement de Noethys selon les préférences (Menu Paramétrage > Préférences)
# Peut être également modifié manuellement ici dans le cadre de tests sur des fichiers indépendamment de l'interface principale 
INTERFACE_MYSQL = "mysqldb"

def SetInterfaceMySQL(nom="mysqldb"):
    """ Permet de sélectionner une interface MySQL """
    global INTERFACE_MYSQL
    if nom == "mysqldb" and IMPORT_MYSQLDB_OK == True :
        INTERFACE_MYSQL = "mysqldb"
    if nom == "mysql.connector" and IMPORT_MYSQLCONNECTOR_OK == True :
        INTERFACE_MYSQL = "mysql.connector"
    

class DB:
    def __init__(self, suffixe="DATA", nomFichier="", modeCreation=False, IDconnexion=None):
        """ Utiliser GestionDB.DB(suffixe="PHOTOS") pour accéder à un fichier utilisateur """
        """ Utiliser GestionDB.DB(nomFichier="Geographie.dat", suffixe=None) pour ouvrir un autre type de fichier """
        self.nomFichier = nomFichier
        self.modeCreation = modeCreation
        
        # Mémorisation de l'ouverture de la connexion et des requêtes
        if IDconnexion == None :
            self.IDconnexion = random.randint(0, 1000000)
        else :
            self.IDconnexion = IDconnexion
        DICT_CONNEXIONS[self.IDconnexion] = []
        
        # Si aucun nom de fichier n'est spécifié, on recherche celui par défaut dans le Config.dat
        if self.nomFichier == "" :
            self.nomFichier = self.GetNomFichierDefaut()
        
        # On ajoute le préfixe de type de fichier et l'extension du fichier
        if suffixe != None :
            self.nomFichier += u"_%s" % suffixe
        
        # Est-ce une connexion réseau ?
        if "[RESEAU]" in self.nomFichier :
            self.isNetwork = True
        else:
            self.isNetwork = False
            if suffixe != None :
                self.nomFichier = u"Data/%s.dat" % self.nomFichier
        
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
        except Exception, err:
            print "La connexion avec la base de donnees SQLITE a echouee : \nErreur detectee :%s" % err
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
        try :
            # Récupération des paramètres de connexion
            pos = nomFichier.index("[RESEAU]")
            paramConnexions = nomFichier[:pos]
            port, host, user, passwd = paramConnexions.split(";")
            nomFichier = nomFichier[pos:].replace("[RESEAU]", "")
            nomFichier = nomFichier.lower() 
            
            # Info sur connexion MySQL
            #print "IDconnexion=", self.IDconnexion, "Interface MySQL =", INTERFACE_MYSQL
            
            # Connexion MySQL
            if INTERFACE_MYSQL == "mysqldb" :
                my_conv = conversions
                my_conv[FIELD_TYPE.LONG] = int
                self.connexion = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True, conv=my_conv) # db=dbParam, 
                self.connexion.set_character_set('utf8')
                
            if INTERFACE_MYSQL == "mysql.connector" :
                self.connexion = mysql.connector.connect(host=host, user=user, passwd=passwd, port=int(port), use_unicode=True, pool_name="mypool2%s" % suffixe, pool_size=3)
    
            self.cursor = self.connexion.cursor()
            
            # Ouverture ou création de la base MySQL
##            listeDatabases = self.GetListeDatabasesMySQL()
##            if nomFichier in listeDatabases :
##                # Ouverture Database
##                self.cursor.execute("USE %s;" % nomFichier)
##            else:
##                # Création Database
##                if self.modeCreation == True :
##                    self.cursor.execute("CREATE DATABASE IF NOT EXISTS %s CHARSET utf8 COLLATE utf8_unicode_ci;" % nomFichier)
##                    self.cursor.execute("USE %s;" % nomFichier)
##                else :
##                    #print "La base de donnees '%s' n'existe pas." % nomFichier
##                    self.echec = 1
##                    return
            
            # Création
            if self.modeCreation == True :
                self.cursor.execute("CREATE DATABASE IF NOT EXISTS %s CHARSET utf8 COLLATE utf8_unicode_ci;" % nomFichier)
            
            # Utilisation
            if nomFichier not in ("", None, "_data") :
                self.cursor.execute("USE %s;" % nomFichier)
            
        except Exception, err:
            print "La connexion avec la base de donnees MYSQL a echouee. Erreur :"
            print (err,)
            self.erreur = err
            self.echec = 1
            #AfficheConnexionOuvertes() 
        else:
            self.echec = 0
    
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
            import UTILS_Config
            nomFichierConfig = "Data/Config.dat"
            cfg = UTILS_Config.FichierConfig(nomFichierConfig)
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
            # Adaptation à MySQL :
            if self.isNetwork == True and typeChamp == "INTEGER PRIMARY KEY AUTOINCREMENT" : typeChamp = "INTEGER PRIMARY KEY AUTO_INCREMENT"
            if self.isNetwork == True and typeChamp == "FLOAT" : typeChamp = "REAL"
            if self.isNetwork == True and typeChamp == "DATE" : typeChamp = "VARCHAR(10)"
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
        except Exception, err:
            print _(u"Requete SQL incorrecte :\n%s\nErreur detectee:\n%s") % (req, err)
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
            del DICT_CONNEXIONS[self.IDconnexion]
            #print "Fermeture connexion ID =", self.IDconnexion
        except :
            pass
                
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
            
        except Exception, err:
            print "Requete sql d'INSERT incorrecte :\n%s\nErreur detectee:\n%s" % (req, err)
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
                blob = MySQLdb.escape_string(blobImage)
                sql = "UPDATE %s SET %s='%s' WHERE %s=%d" % (table, nomChampBlob, blob, key, IDkey)
                self.cursor.execute(sql)
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

    def ReqMAJ(self, nomTable, listeDonnees, nomChampID, ID, IDestChaine=False):
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
            self.Commit()
        except Exception, err:
            print _(u"Requete sql de mise a jour incorrecte :\n%s\nErreur detectee:\n%s") % (req, err)
        
    def ReqDEL(self, nomTable="", nomChampID="", ID="", commit=True):
        """ Suppression d'un enregistrement """
        req = "DELETE FROM %s WHERE %s=%d" % (nomTable, nomChampID, ID)
        try:
            self.cursor.execute(req)
            if commit == True :
                self.Commit()
        except Exception, err:
            print _(u"Requete sql de suppression incorrecte :\n%s\nErreur detectee:\n%s") % (req, err)
        
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
                if dictModifications.has_key(nomChamp):
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
        else:
            # Version MySQL
            self.ExecuterReq("USE information_schema;")
            pos = self.nomFichier.index("[RESEAU]")
            nomFichier = self.nomFichier[pos:].replace("[RESEAU]", "")
            req = "SELECT auto_increment FROM tables WHERE table_schema='%s' and table_name='%s' ;" % (nomFichier, nomTable)
            self.ExecuterReq(req)
            donnees = self.ResultatReq()
        if len(donnees) > 0 :
            ID = donnees[0][0] + 1
            return ID
        else:
            return None
    
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
            
            print "Reparation de la table '%s' terminee." % nomTable

    def Importation_table(self, nomTable="", nomFichierdefault="Defaut.dat", mode="local"):
        """ Importe toutes les données d'une table donnée """
        # Ouverture de la base par défaut
        if mode == "local" :
            
            try:
                connexionDefaut = sqlite3.connect(nomFichierdefault.encode('utf-8'))
            except Exception, err:
                print "Echec Importation table. Erreur detectee :%s" % err
                echec = 1
            else:
                cursor = connexionDefaut.cursor()
                echec = 0
        
        else :
            
            try :
                # Récupération des paramètres de connexion
                pos = nomFichierdefault.index("[RESEAU]")
                paramConnexions = nomFichierdefault[:pos]
                port, host, user, passwd = paramConnexions.split(";")
                nomFichier = nomFichierdefault[pos:].replace("[RESEAU]", "")
                nomFichier = nomFichier.lower() 
                
                # Connexion MySQL
                if INTERFACE_MYSQL == "mysqldb" :
                    my_conv = conversions
                    my_conv[FIELD_TYPE.LONG] = int
                    connexionDefaut = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True, conv=my_conv) # db=dbParam, 
                    connexionDefaut.set_character_set('utf8')
                    
                if INTERFACE_MYSQL == "mysql.connector" :
                    connexionDefaut = mysql.connector.connect(host=host, user=user, passwd=passwd, port=int(port), use_unicode=True, pool_name="mypool3%s" % suffixe, pool_size=3)

                cursor = connexionDefaut.cursor()
                
                # Ouverture Database
                cursor.execute("USE %s;" % nomFichier)
                
            except Exception, err:
                print "La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err
                erreur = err
                echec = 1
            else:
                echec = 0
        
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
        champsExistants = GetChampsTable(nomTable)
        for nomChamp in listeNomsChamps[0:] :
            if nomChamp in champsExistants :
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
        except Exception, err :
            print "Erreur dans l'importation de la table %s :" % nomTable
            print err
        self.connexion.commit()

    def Importation_table_reseau(self, nomTable="", nomFichier="", dictTables={}):
        """ Importe toutes les données d'une table donnée dans un fichier réseau """
        import cStringIO
        
        # Ouverture de la base réseau
        try :
            # Récupération des paramètres de connexion
            pos = nomFichier.index("[RESEAU]")
            paramConnexions = nomFichier[:pos]
            port, host, user, passwd = paramConnexions.split(";")
            nomFichier = nomFichier[pos:].replace("[RESEAU]", "")
            nomFichier = nomFichier.lower() 
            
            # Connexion MySQL
            if INTERFACE_MYSQL == "mysqldb" :
                my_conv = conversions
                my_conv[FIELD_TYPE.LONG] = int
                connexionDefaut = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True, conv=my_conv) # db=dbParam, 
                connexionDefaut.set_character_set('utf8')
                
            if INTERFACE_MYSQL == "mysql.connector" :
                connexionDefaut = mysql.connector.connect(host=host, user=user, passwd=passwd, port=int(port), use_unicode=True, pool_name="mypool4%s" % suffixe, pool_size=3)
                
            cursor = connexionDefaut.cursor()
            
            # Ouverture Database
            cursor.execute("USE %s;" % nomFichier)
            
        except Exception, err:
            print "La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err
            erreur = err
            echec = 1
        else:
            echec = 0

        # Recherche des noms de champs de la table
        req = "SELECT * FROM %s" % nomTable
        cursor.execute(req)
        listeDonneesTmp = cursor.fetchall()
        listeChamps = []
        for fieldDesc in cursor.description:
            listeChamps.append(fieldDesc[0])
        
        # Préparation des noms de champs pour le transfert
        txtChamps = "("
        txtQMarks = "("
        for nomChamp in listeChamps[0:] :
            txtChamps += nomChamp + ", "
            txtQMarks += "?, "
        txtChamps = txtChamps[:-2] + ")"
        txtQMarks = txtQMarks[:-2] + ")"

        # Récupération des données
        listeDonnees = []
        for donnees in listeDonneesTmp :
            # Analyse des données pour trouver les champs BLOB
            numColonne = 0
            listeValeurs = []
            for donnee in donnees[0:] :
                typeChamp = dictTables[nomTable][numColonne][1]
                if typeChamp == "BLOB" or typeChamp == "LONGBLOB" :
                    if donnee != None :
                        donnee = sqlite3.Binary(donnee)
                listeValeurs.append(donnee)
                numColonne += 1
            listeDonnees.append(tuple(listeValeurs))
        
        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, txtChamps, txtQMarks)
        self.cursor.executemany(req, listeDonnees)
        self.connexion.commit()

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

    def Exportation_vers_base_defaut(self, nomTable="", nomFichierdefault="Defaut.dat"):
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
        for nomIndex, temp in Tables.DB_INDEX.iteritems() :
            self.CreationIndex(nomIndex)


# ------------- Fonctions de MAJ de la base de données ---------------------------------------------------------------
        
    def ConversionDB(self, versionFichier=(0, 0, 0, 0) ) :
        """ Adapte un fichier obsolète à la version actuelle du logiciel """
        
        # Filtres de conversion
        
        # =============================================================
        
        versionFiltre = (1, 0, 1, 1)
        if versionFichier < versionFiltre :   
            try :
                self.CreationTable("historique", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 1, 2)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("historique") == False :
                    self.CreationTable("historique", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 1, 3)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("attestations") == False :
                    self.CreationTable("attestations", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 1, 7)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("recus") == False :
                    self.CreationTable("recus", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 2, 1)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("adresses_mail") == False :
                    self.CreationTable("adresses_mail", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
                
        versionFiltre = (1, 0, 3, 3)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("listes_diffusion") == False : self.CreationTable("listes_diffusion", Tables.DB_DATA)
                if self.IsTableExists("abonnements") == False : self.CreationTable("abonnements", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
                
        versionFiltre = (1, 0, 3, 9)
        if versionFichier < versionFiltre :   
            try :
                self.SupprChamp("tarifs_lignes", "heure_max")
                self.SupprChamp("tarifs_lignes", "heure_min")
                self.AjoutChamp("tarifs_lignes", "heure_debut_min", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "heure_debut_max", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "heure_fin_min", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "heure_fin_max", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_min", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_max", "VARCHAR(10)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 4, 2)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "date", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "label", "VARCHAR(300)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 4, 6)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("documents_modeles") == False : self.CreationTable("documents_modeles", Tables.DB_DATA)
                if self.IsTableExists("documents_objets") == False : self.CreationTable("documents_objets", Tables.DB_DATA)
                self.Importation_valeurs_defaut([[u"", ("documents_modeles", "documents_objets"), True],])
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 4, 8)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("prestations", "temps_facture", "VARCHAR(10)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 4, 9)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "temps_facture", "VARCHAR(10)")
                self.AjoutChamp("tarifs", "categories_tarifs", "VARCHAR(300)")
                self.AjoutChamp("tarifs", "groupes", "VARCHAR(300)")
                self.AjoutChamp("prestations", "IDcategorie_tarif", "INTEGER")
                import UTILS_Procedures
                UTILS_Procedures.S1290()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 5, 1)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("questionnaire_questions") == False : self.CreationTable("questionnaire_questions", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_categories") == False : self.CreationTable("questionnaire_categories", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_choix") == False : self.CreationTable("questionnaire_choix", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_reponses") == False : self.CreationTable("questionnaire_reponses", Tables.DB_DATA)
                if self.isNetwork == True :
                    typeChamp = "TEXT(2000)"
                else:
                    typeChamp = "VARCHAR(2000)"
                self.AjoutChamp("familles", "memo", typeChamp)
                import UTILS_Procedures
                UTILS_Procedures.D1051()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 5, 3)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "unite_horaire", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_seuil", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_plafond", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "taux", "FLOAT")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 5, 4)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "ajustement", "FLOAT")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 5, 5)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("niveaux_scolaires") == False : self.CreationTable("niveaux_scolaires", Tables.DB_DATA)
                if self.IsTableExists("ecoles") == False : self.CreationTable("ecoles", Tables.DB_DATA)
                if self.IsTableExists("classes") == False : self.CreationTable("classes", Tables.DB_DATA)
                if self.IsTableExists("scolarite") == False : self.CreationTable("scolarite", Tables.DB_DATA)
                self.Importation_valeurs_defaut([[u"", ("niveaux_scolaires",), True],])
                self.AjoutChamp("unites_remplissage", "heure_min", "VARCHAR(10)")
                self.AjoutChamp("unites_remplissage", "heure_max", "VARCHAR(10)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 5, 9)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("combi_tarifs", "quantite_max", "INTEGER")
                self.AjoutChamp("tarifs", "forfait_duree", "VARCHAR(50)")
                self.AjoutChamp("tarifs", "forfait_beneficiaire", "VARCHAR(50)")
                self.AjoutChamp("prestations", "forfait_date_debut", "VARCHAR(10)")
                self.AjoutChamp("prestations", "forfait_date_fin", "VARCHAR(10)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("transports_compagnies") == False : self.CreationTable("transports_compagnies", Tables.DB_DATA)
                if self.IsTableExists("transports_lieux") == False : self.CreationTable("transports_lieux", Tables.DB_DATA)
                if self.IsTableExists("transports_lignes") == False : self.CreationTable("transports_lignes", Tables.DB_DATA)
                if self.IsTableExists("transports_arrets") == False : self.CreationTable("transports_arrets", Tables.DB_DATA)
                if self.IsTableExists("transports") == False : self.CreationTable("transports", Tables.DB_DATA)
                self.AjoutChamp("tarifs", "cotisations", "VARCHAR(300)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("groupes", "abrege", "VARCHAR(100)")
                self.AjoutChamp("groupes", "ordre", "INTEGER")
                import UTILS_Procedures
                UTILS_Procedures.G2345()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 8)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("questionnaire_filtres") == False : self.CreationTable("questionnaire_filtres", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 9)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("organisateur", "gps", "VARCHAR(200)")
##                import UTILS_Procedures
##                UTILS_Procedures.A4567()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("familles", "allocataire", "INTEGER")
                if self.IsTableExists("etat_nomin_champs") == False : self.CreationTable("etat_nomin_champs", Tables.DB_DATA)
                if self.IsTableExists("etat_nomin_selections") == False : self.CreationTable("etat_nomin_selections", Tables.DB_DATA)
                if self.IsTableExists("etat_nomin_profils") == False : self.CreationTable("etat_nomin_profils", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "caisses", "VARCHAR(300)")
                self.AjoutChamp("tarifs", "description", "VARCHAR(450)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 5)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "jours_scolaires", "VARCHAR(100)")
                self.AjoutChamp("tarifs", "jours_vacances", "VARCHAR(100)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("badgeage_actions") == False : self.CreationTable("badgeage_actions", Tables.DB_DATA)
                if self.IsTableExists("badgeage_messages") == False : self.CreationTable("badgeage_messages", Tables.DB_DATA)
                if self.IsTableExists("badgeage_procedures") == False : self.CreationTable("badgeage_procedures", Tables.DB_DATA)
                if self.IsTableExists("badgeage_journal") == False : self.CreationTable("badgeage_journal", Tables.DB_DATA)
                if self.IsTableExists("corrections_phoniques") == False : self.CreationTable("corrections_phoniques", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 8)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("consommations", "quantite", "INTEGER")
                self.AjoutChamp("documents_objets", "norme", "VARCHAR(100)")
                self.AjoutChamp("documents_objets", "afficheNumero", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 9)
        if versionFichier < versionFiltre :
            try :
                if self.isNetwork == True :
                    self.ExecuterReq("ALTER TABLE documents_objets MODIFY COLUMN image LONGBLOB;")
                    self.Commit()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 8, 0)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("corrections_villes") == False : self.CreationTable("corrections_villes", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "options", "VARCHAR(450)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 4)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("badgeage_archives") == False : self.CreationTable("badgeage_archives", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 6)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("messages", "afficher_facture", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 7)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("modeles_emails") == False : self.CreationTable("modeles_emails", Tables.DB_DATA)
                self.AjoutChamp("prestations", "reglement_frais", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 8)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("banques") == False : self.CreationTable("banques", Tables.DB_DATA)
                if self.IsTableExists("lots_factures") == False : self.CreationTable("lots_factures", Tables.DB_DATA)
                if self.IsTableExists("lots_rappels") == False : self.CreationTable("lots_rappels", Tables.DB_DATA)
                self.AjoutChamp("factures", "IDlot", "INTEGER")
                self.AjoutChamp("factures", "prestations", "VARCHAR(500)")
                self.AjoutChamp("rappels", "IDlot", "INTEGER")
                self.AjoutChamp("rappels", "prestations", "VARCHAR(500)")
                self.AjoutChamp("rappels", "date_min", "DATE")
                self.AjoutChamp("rappels", "date_max", "DATE")
                self.AjoutChamp("familles", "prelevement_activation", "INTEGER")
                self.AjoutChamp("familles", "prelevement_etab", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_guichet", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_numero", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_cle", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_banque", "INTEGER")
                self.AjoutChamp("familles", "prelevement_individu", "INTEGER")
                self.AjoutChamp("familles", "prelevement_nom", "VARCHAR(200)")
                self.AjoutChamp("familles", "prelevement_rue", "VARCHAR(400)")
                self.AjoutChamp("familles", "prelevement_cp", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_ville", "VARCHAR(400)") 
                self.AjoutChamp("familles", "email_factures", "VARCHAR(450)") 

            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 9)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("prelevements") == False : self.CreationTable("prelevements", Tables.DB_DATA)
                if self.IsTableExists("lots_prelevements") == False : self.CreationTable("lots_prelevements", Tables.DB_DATA)
                self.AjoutChamp("comptes_bancaires", "raison", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_etab", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_guichet", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_nne", "VARCHAR(400)")
                self.AjoutChamp("reglements", "IDprelevement", "INTEGER")

            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)


        # =============================================================

        versionFiltre = (1, 0, 9, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "observations", "VARCHAR(450)")
                self.AjoutChamp("tarifs", "tva", "FLOAT")
                self.AjoutChamp("tarifs", "code_compta", "VARCHAR(200)")
                self.AjoutChamp("prestations", "tva", "FLOAT")
                self.AjoutChamp("prestations", "code_compta", "VARCHAR(200)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 9, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("combi_tarifs", "IDgroupe", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 9, 3)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("modeles_tickets") == False : self.CreationTable("modeles_tickets", Tables.DB_DATA)
                self.AjoutChamp("badgeage_actions", "action_ticket", "VARCHAR(450)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 9, 4)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("modeles_tickets", "taille", "INTEGER")
                self.AjoutChamp("modeles_tickets", "interligne", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("modeles_tickets", "imprimante", "VARCHAR(450)")
                self.AjoutChamp("unites", "largeur", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("unites_remplissage", "afficher_page_accueil", "INTEGER")
                self.AjoutChamp("unites_remplissage", "afficher_grille_conso", "INTEGER")
                self.AjoutChamp("tarifs", "date_facturation", "VARCHAR(450)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("activites", "nbre_inscrits_max", "INTEGER")
                self.AjoutChamp("familles", "email_recus", "VARCHAR(450)")
                self.AjoutChamp("familles", "email_depots", "VARCHAR(450)")
                self.AjoutChamp("reglements", "avis_depot", "DATE")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("sauvegardes_auto") == False : self.CreationTable("sauvegardes_auto", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 0, 8)
        if versionFichier < versionFiltre :
            try :
                import UTILS_Procedures
                UTILS_Procedures.A5300()
                UTILS_Procedures.A5400()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 1, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("comptes_bancaires", "cle_rib", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "cle_iban", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "iban", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "bic", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_ics", "VARCHAR(400)")
                self.AjoutChamp("familles", "prelevement_cle_iban", "VARCHAR(10)")
                self.AjoutChamp("familles", "prelevement_iban", "VARCHAR(100)")
                self.AjoutChamp("familles", "prelevement_bic", "VARCHAR(100)")
                self.AjoutChamp("familles", "prelevement_reference_mandat", "VARCHAR(300)")
                self.AjoutChamp("familles", "prelevement_date_mandat", "DATE")
                self.AjoutChamp("familles", "prelevement_memo", "VARCHAR(450)")
                self.AjoutChamp("prelevements", "prelevement_iban", "VARCHAR(100)")
                self.AjoutChamp("prelevements", "prelevement_bic", "VARCHAR(100)")
                self.AjoutChamp("prelevements", "prelevement_reference_mandat", "VARCHAR(300)")
                self.AjoutChamp("prelevements", "prelevement_date_mandat", "DATE")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 1, 3)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("droits") == False : self.CreationTable("droits", Tables.DB_DATA)
                if self.IsTableExists("modeles_droits") == False : self.CreationTable("modeles_droits", Tables.DB_DATA)
                if self.IsTableExists("mandats") == False : self.CreationTable("mandats", Tables.DB_DATA)
                self.AjoutChamp("lots_prelevements", "type", "VARCHAR(100)")
                self.AjoutChamp("prelevements", "IDmandat", "INTEGER")
                self.AjoutChamp("prelevements", "sequence", "VARCHAR(100)")
                self.AjoutChamp("utilisateurs", "image", "VARCHAR(200)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 1, 4)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("pes_pieces") == False : self.CreationTable("pes_pieces", Tables.DB_DATA)
                if self.IsTableExists("pes_lots") == False : self.CreationTable("pes_lots", Tables.DB_DATA)
                self.AjoutChamp("reglements", "IDpiece", "INTEGER")
                self.AjoutChamp("familles", "titulaire_helios", "INTEGER")
                self.AjoutChamp("familles", "code_comptable", "VARCHAR(450)")
                import UTILS_Procedures
                UTILS_Procedures.A7650() # Création auto des titulaires Hélios
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 1, 5)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("pes_lots", "prelevement_libelle", "VARCHAR(450)")
                self.AjoutChamp("modes_reglements", "type_comptable", "VARCHAR(200)")
                self.AjoutChamp("activites", "code_comptable", "VARCHAR(450)")
                self.AjoutChamp("types_cotisations", "code_comptable", "VARCHAR(450)")
                import UTILS_Procedures
                UTILS_Procedures.A8120() # Création auto type_comptable dans table modes_règlements
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 1, 6)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("pes_lots", "objet_piece", "VARCHAR(450)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 2)
        if versionFichier < versionFiltre :
            try :
                import UTILS_Export_documents
                UTILS_Export_documents.ImporterDepuisFichierDefaut(IDmodele=12, nom=None, IDfond=0, defaut=1) # import modèle doc reçu don aux oeuvres
                UTILS_Export_documents.ImporterDepuisFichierDefaut(IDmodele=13, nom=None, IDfond=1, defaut=1) # import modèle doc attestation fiscale
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 2, 3)
        if versionFichier < versionFiltre :
            try :
                import UTILS_Procedures
                UTILS_Procedures.A8260() 
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("unites", "coeff", "VARCHAR(50)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 8)
        if versionFichier < versionFiltre :   
            try :
                if self.isNetwork == True :
                    self.ExecuterReq("ALTER TABLE parametres MODIFY COLUMN parametre TEXT;")
                    self.Commit()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 9)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("modes_reglements", "code_compta", "VARCHAR(200)")
                self.AjoutChamp("depots", "code_compta", "VARCHAR(200)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 3, 5)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "montant_questionnaire", "INTEGER")
                self.AjoutChamp("prestations", "IDcontrat", "INTEGER")
                if self.IsTableExists("contrats") == False : self.CreationTable("contrats", Tables.DB_DATA) 
                if self.IsTableExists("modeles_contrats") == False : self.CreationTable("modeles_contrats", Tables.DB_DATA)
                if self.IsTableExists("modeles_plannings") == False : self.CreationTable("modeles_plannings", Tables.DB_DATA)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 3, 6)
        if versionFichier < versionFiltre :   
            try :
                if self.isNetwork == True :
                    self.ExecuterReq("ALTER TABLE parametres MODIFY COLUMN parametre MEDIUMTEXT;")
                    self.Commit()
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 3, 9)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("compta_operations") == False : self.CreationTable("compta_operations", Tables.DB_DATA) 
                if self.IsTableExists("compta_virements") == False : self.CreationTable("compta_virements", Tables.DB_DATA) 
                if self.IsTableExists("compta_ventilation") == False : self.CreationTable("compta_ventilation", Tables.DB_DATA) 
                if self.IsTableExists("compta_exercices") == False : self.CreationTable("compta_exercices", Tables.DB_DATA) 
                if self.IsTableExists("compta_analytiques") == False : self.CreationTable("compta_analytiques", Tables.DB_DATA) 
                if self.IsTableExists("compta_categories") == False : self.CreationTable("compta_categories", Tables.DB_DATA) 
                if self.IsTableExists("compta_comptes_comptables") == False : self.CreationTable("compta_comptes_comptables", Tables.DB_DATA) 
                if self.IsTableExists("compta_tiers") == False : self.CreationTable("compta_tiers", Tables.DB_DATA) 
                if self.IsTableExists("compta_budgets") == False : self.CreationTable("compta_budgets", Tables.DB_DATA) 
                if self.IsTableExists("compta_categories_budget") == False : self.CreationTable("compta_categories_budget", Tables.DB_DATA) 
                if self.IsTableExists("compta_releves") == False : self.CreationTable("compta_releves", Tables.DB_DATA) 
                try :
                    self.Importation_valeurs_defaut([[u"", ("compta_comptes_comptables",), True],])
                except :
                    print "Table 'compta_comptes_comptables' impossible a remplir : Elle a deja ete remplie !"
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 4, 0)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("familles", "idtiers_helios", "VARCHAR(200)")
                self.AjoutChamp("familles", "natidtiers_helios", "INTEGER")
                self.AjoutChamp("familles", "reftiers_helios", "VARCHAR(200)")
                self.AjoutChamp("familles", "cattiers_helios", "INTEGER")
                self.AjoutChamp("familles", "natjur_helios", "INTEGER")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 4, 2)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("compta_ventilation", "date_budget", "DATE")
                if self.IsTableExists("compta_operations_budgetaires") == False : self.CreationTable("compta_operations_budgetaires", Tables.DB_DATA) 
                self.AjoutChamp("compta_budgets", "date_debut", "DATE")
                self.AjoutChamp("compta_budgets", "date_fin", "DATE")
                import UTILS_Procedures
                UTILS_Procedures.A8623() 
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 4, 4)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("nomade_archivage") == False : self.CreationTable("nomade_archivage", Tables.DB_DATA) 
                import UTILS_Procedures
                UTILS_Procedures.A8733() 
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 4, 9)
        if versionFichier < versionFiltre :   
            try :
                import UTILS_Procedures
                UTILS_Procedures.A8823() 
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 5, 0)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("factures", "etat", "VARCHAR(100)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 5, 1)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("cotisations", "observations", "VARCHAR(1000)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 5, 2)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("cotisations", "activites", "VARCHAR(450)")
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 5, 4)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("etiquettes") == False : self.CreationTable("etiquettes", Tables.DB_DATA) 
                self.AjoutChamp("consommations", "etiquettes", "VARCHAR(100)")
                self.AjoutChamp("tarifs", "etiquettes", "VARCHAR(450)")
                self.AjoutChamp("tarifs", "etats", "VARCHAR(150)")
                self.AjoutChamp("unites_remplissage", "etiquettes", "VARCHAR(450)")
                import UTILS_Procedures
                UTILS_Procedures.A8941() 
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================






        return True

def GetChampsTable(nomTable=""):
    for dictTables in (Tables.DB_DATA, Tables.DB_PHOTOS, Tables.DB_DOCUMENTS) :
        if dictTables.has_key(nomTable) :
            listeChamps = []
            for nom, typeTable, info in dictTables[nomTable] :
                listeChamps.append(nom)
            return listeChamps
    return []

def ConvertConditionChaine(liste=[]):
    """ Transforme une liste de valeurs en une condition chaine pour requête SQL """
    if len(liste) == 0 : condition = "()"
    elif len(liste) == 1 : condition = "(%d)" % liste[0]
    else : condition = str(tuple(liste))
    return condition

def ConversionLocalReseau(nomFichier="", nouveauFichier="", fenetreParente=None):
    """ Convertit une DB locale en version RESEAU MySQL """
    print "Lancement de la procedure de conversion local->reseau :"
    
    for suffixe, dictTables in ( ("DATA", Tables.DB_DATA), ("PHOTOS", Tables.DB_PHOTOS), ("DOCUMENTS", Tables.DB_DOCUMENTS) ) :
        
        nomFichierActif = u"Data/%s_%s.dat" % (nomFichier, suffixe)
        nouveauNom = nouveauFichier[nouveauFichier.index("[RESEAU]"):].replace("[RESEAU]", "")
        
        dictResultats = TestConnexionMySQL(typeTest="fichier", nomFichier=u"%s_%s" % (nouveauFichier, suffixe) )
        # Vérifie la connexion au réseau
        if dictResultats["connexion"][0] == False :
            erreur = dictResultats["connexion"][1]
            dlg = wx.MessageDialog(None, _(u"La connexion au réseau MySQL est impossible. \n\nErreur : %s") % erreur, "Erreur de connexion", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            print "connexion reseau MySQL impossible."
            return False
        
        # Vérifie que le fichier n'est pas déjà utilisé
        if dictResultats["fichier"][0] == True :
            dlg = wx.MessageDialog(None, _(u"Le fichier existe déjà."), "Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            print "le nom existe deja."
            return False
        
        # Création de la base de données
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création du fichier réseau..."))
        db = DB(suffixe=suffixe, nomFichier=nouveauFichier, modeCreation=True)
        if db.echec == 1 :
            erreur = db.erreur
            dlg = wx.MessageDialog(None, _(u"Erreur dans la création du fichier.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        print "  > Nouveau fichier reseau %s cree..." % suffixe
        
        # Création des tables
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création des tables de données %s...") % suffixe)
        db.CreationTables(dicoDB=dictTables)
        print "  > Nouvelles tables %s creees..." % suffixe
        
        # Importation des valeurs
        listeTables = dictTables.keys()
        index = 1
        for nomTable in listeTables :
            print "  > Importation de la table '%s' (%d/%d)" % (nomTable, index, len(listeTables))
            if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Importation de la table %d sur %s...") % (index, len(listeTables)))
            db.Importation_table(nomTable, nomFichierActif)
            print "     -> ok"
            index += 1
        
        db.Close() 
    
    print "  > Conversion terminee avec succes."
            

def ConversionReseauLocal(nomFichier="", nouveauFichier="", fenetreParente=None):
    """ Convertit une DB RESEAU MySQL en version LOCALE SQLITE """
    print "Lancement de la procedure de conversion reseau->local :"
    
    for suffixe, dictTables in ( ("DATA", Tables.DB_DATA), ("PHOTOS", Tables.DB_PHOTOS), ("DOCUMENTS", Tables.DB_DOCUMENTS) ) :
        
        nomFichierActif = nomFichier[nomFichier.index("[RESEAU]"):].replace("[RESEAU]", "") 
        nouveauNom = u"Data/%s_%s.dat" % (nomFichier, suffixe)
        
        # Vérifie que le fichier n'est pas déjà utilisé
        if os.path.isfile(nouveauNom)  == True :
            dlg = wx.MessageDialog(None, _(u"Le fichier existe déjà."), "Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            print "le nom existe deja."
            return False
        
        # Création de la base de données
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création du fichier local..."))
        db = DB(suffixe=suffixe, nomFichier=nouveauFichier, modeCreation=True)
        if db.echec == 1 :
            erreur = db.erreur
            dlg = wx.MessageDialog(None, _(u"Erreur dans la création du fichier.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        print "  > Nouveau fichier local %s cree..." % suffixe
        
        # Création des tables
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création des tables de données %s...") % suffixe)
        db.CreationTables(dicoDB=dictTables)
        print "  > Nouvelles tables %s creees..." % suffixe
        
        # Importation des valeurs
        listeTables = dictTables.keys()
        index = 1
        for nomTable in listeTables :
            print "  > Importation de la table '%s' (%d/%d)" % (nomTable, index, len(listeTables))
            if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Importation de la table %d sur %s...") % (index, len(listeTables)))
            db.Importation_table_reseau(nomTable, u"%s_%s" % (nomFichier, suffixe), dictTables)
            print "     -> ok"
            index += 1
        
        db.Close() 
    
    print "  > Conversion reseau->local terminee avec succes."


def TestConnexionMySQL(typeTest="fichier", nomFichier=""):
    """ typeTest=fichier ou reseau """
    dictResultats = {}
    
    pos = nomFichier.index("[RESEAU]")
    paramConnexions = nomFichier[:pos]
    port, host, user, passwd = paramConnexions.split(";")
    nomFichier = nomFichier[pos+8:]
    nomFichier = nomFichier.lower() 
    
    cursor = None
    connexion = None
    
    # Test de connexion au réseau MySQL
    try :
        if INTERFACE_MYSQL == "mysqldb" :
            connexion = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True) # db=dbParam, 
            connexion.set_character_set('utf8')
        if INTERFACE_MYSQL == "mysql.connector" :
            connexion = mysql.connector.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True, pool_name="mypool", pool_size=1) 
        cursor = connexion.cursor()
        dictResultats["connexion"] =  (True, None)
        connexion_ok = True
    except Exception, err :
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
                dictResultats["fichier"] =  (True, None)
            else:
                dictResultats["fichier"] =  (False, _(u"Accès au fichier impossible."))
        except Exception, err :
            dictResultats["fichier"] =  (False, err)
    
    if connexion != None :
        connexion.close()
    return dictResultats


# ----------------------------------------------------------------------------------------------------------------------------------------
                                
def ImporterFichierDonnees() :
    db = DB(nomFichier="Prenoms.dat", suffixe=None, modeCreation=True)
    db.CreationTable("prenoms", DB_DATA2)
    db.Close()
    
    txt = open("prenoms.txt", 'r').readlines()
    db = DB(nomFichier="Prenoms.dat", suffixe=None)
    index = 0
    for ligne in txt :
        ID, prenom, genre = ligne.split(";")
        listeDonnees = [("prenom", prenom.decode("iso-8859-15") ), ("genre", genre.decode("iso-8859-15")),]
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
    db = DB(nomFichier="Annonces.dat", suffixe=None, modeCreation=True)
    db.CreationTable("annonces_aleatoires", DB_DATA_ANNONCES)
    db.CreationTable("annonces_dates", DB_DATA_ANNONCES)
    db.CreationTable("annonces_periodes", DB_DATA_ANNONCES)
    db.Close()
    

def AfficheConnexionOuvertes():
    """ Affiche les connexions non fermées """
    if len(DICT_CONNEXIONS) > 0 :
        print "--------- Attention, il reste %d connexions encore ouvertes : ---------" % len(DICT_CONNEXIONS)
        for IDconnexion, requetes in DICT_CONNEXIONS.iteritems() :
            print ">> IDconnexion = %d (%d requetes) :" % (IDconnexion, len(requetes))
            for requete in requetes :
                print requete



if __name__ == "__main__":
                
    # Création d'une table données
##    db = DB(suffixe="DATA")
##    listeTables = ("etiquettes",)
##    for nomTable in listeTables :
##        db.CreationTable(nomTable, Tables.DB_DATA)
##    db.Close()
##    print "creation tables ok."                
    
    # Création des tables COMPTA
##    db = DB(suffixe="DATA")
##    listeTables = (
##        "compta_virements", "compta_categories_budget", "compta_budgets",
##        )
##    for nomTable in listeTables :
##        try :
##            db.CreationTable(nomTable, Tables.DB_DATA)
##        except :
##            pass
##    db.Close()
##    print "creation tables ok."                


## ----------------------------------------------------------------------

##    # Création de toutes les tables
##    db = DB(suffixe="DATA", modeCreation=True)
##    import Tables
##    dicoDB = Tables.DB_DATA
##    db.CreationTables(dicoDB)
##    db.Close()
##    print "creation des tables DATA ok."
##    db = DB(suffixe="PHOTOS", modeCreation=True)
##    import Tables
##    dicoDB = Tables.DB_PHOTOS
##    db.CreationTables(dicoDB)
##    db.Close()
##    print "creation des tables PHOTOS ok."
    
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
        
    # Ajouter un champ
##    db = DB(suffixe="DATA")
##    db.AjoutChamp("tarifs", "etats", "VARCHAR(150)")
##    db.Close()

    # Exportation d'une table dans la base DEFAUT
##    db = DB(suffixe="DATA")
##    db.Exportation_vers_base_defaut(nomTable="compta_comptes_comptables")
##    db.Close()
    
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
    