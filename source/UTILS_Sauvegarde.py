#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import sys
import base64
import zipfile
import GestionDB
import subprocess
import shutil
import time

import UTILS_Config
import UTILS_Cryptage_fichier
import UTILS_Envoi_email


LISTE_CATEGORIES = [
    (_(u"Donn�es de base"), "DATA"),
    (_(u"Photos individuelles"), "PHOTOS"),
    (_(u"Documents"), "DOCUMENTS"),
    ]

EXTENSIONS = {
    "decrypte" : "nod",
    "crypte" : "noc",
    }



def Sauvegarde(listeFichiersLocaux=[], listeFichiersReseau=[], nom="", repertoire=None, motdepasse=None, listeEmails=None, dictConnexion=None):
    """ Processus de de cr�ation du ZIP """
    # Si aucun fichier � sauvegarder
    if len(listeFichiersLocaux) == 0 and len(listeFichiersReseau) == 0 : 
        return False
    
    # Initialisation de la barre de progression
    nbreEtapes = 3
    nbreEtapes += len(listeFichiersLocaux)
    nbreEtapes += len(listeFichiersReseau)
    if motdepasse != None : nbreEtapes += 1
    if repertoire != None : nbreEtapes += 1
    if listeEmails != None : nbreEtapes += 1
    
    # Cr�ation du nom du fichier de destination
    if motdepasse != None :
        extension = EXTENSIONS["crypte"]
    else:
        extension = EXTENSIONS["decrypte"]

    # V�rifie si fichier de destination existe d�j�
    if repertoire != None :
        fichierDest = u"%s/%s.%s" % (repertoire, nom, extension)
        if os.path.isfile(fichierDest) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier de sauvegarde portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

    # R�cup�ration des param�tres de l'adresse d'exp�diteur par d�faut
    if listeEmails != None :
        dictAdresse = UTILS_Envoi_email.GetAdresseExpDefaut()
        if dictAdresse == None :
            dlgErreur = wx.MessageDialog(None, _(u"Envoi par Email impossible :\n\nAucune adresse d'exp�diteur n'a �t� d�finie. Veuillez la saisir dans le menu Param�trage du logiciel..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False

    # Fen�tre de progression
    dlgprogress = wx.ProgressDialog(_(u"Sauvegarde"), _(u"Lancement de la sauvegarde..."), maximum=nbreEtapes, parent=None, style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
    
    # Cr�ation du fichier ZIP temporaire
    nomFichierTemp = u"%s.%s" % (nom, EXTENSIONS["decrypte"])
    fichierZip = zipfile.ZipFile(_(u"Temp/%s") % nomFichierTemp, "w", compression=zipfile.ZIP_DEFLATED)
    numEtape = 1
    dlgprogress.Update(numEtape, _(u"Cr�ation du fichier de compression..."));numEtape += 1
    
    # Int�gration des fichiers locaux
    for nomFichier in listeFichiersLocaux :
        dlgprogress.Update(numEtape, _(u"Compression du fichier %s...") % nomFichier);numEtape += 1
        fichier = u"Data/%s" % nomFichier
        if os.path.isfile(fichier) == True :
            fichierZip.write(fichier, nomFichier)
        else :
            dlgprogress.Destroy()
            dlgErreur = wx.MessageDialog(None, _(u"Le fichier '%s' n'existe plus sur cet ordinateur. \n\nVeuillez �ter ce fichier de la proc�dure de sauvegarde automatique (Menu Fichier > Sauvegardes automatiques)") % nomFichier, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False
        
    # Int�gration des fichiers r�seau
    if len(listeFichiersReseau) > 0 and dictConnexion != None :
        
        # Cr�ation du r�pertoire temporaire
        repTemp = _(u"Temp/savetemp")
        if os.path.isdir(repTemp) == True :
            shutil.rmtree(repTemp)
        os.mkdir(repTemp)
        
        # Recherche du r�pertoire d'installation de MySQL
        repMySQL = GetRepertoireMySQL(dictConnexion) 
        if repMySQL == None :
            dlgprogress.Destroy()
            dlgErreur = wx.MessageDialog(None, _(u"Noethys n'a pas r�ussi � localiser MySQL sur votre ordinateur.\n\nNotez bien que MySQL doit �tre install� obligatoirement pour cr�er une sauvegarde r�seau."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False
        
        # Cr�ation du fichier de login
        nomFichierLoginTemp = os.path.abspath(os.curdir) + "/" + repTemp + "/logintemp.cnf"
        CreationFichierLoginTemp(host=dictConnexion["host"], port=dictConnexion["port"], user=dictConnexion["user"], password=dictConnexion["password"], nomFichier=nomFichierLoginTemp)
        
        # Cr�ation du backup pour chaque fichier MySQL
        for nomFichier in listeFichiersReseau :
            dlgprogress.Update(numEtape, _(u"Compression du fichier %s...") % nomFichier);numEtape += 1
            fichierSave = u"%s/%s.sql" % (repTemp, nomFichier)
                
##            args = [
##                "%sbin/mysqldump" % repMySQL,
##                "--host=%s" % dictConnexion["host"],
##                "--port=%s" % dictConnexion["port"],
##                "--user=%s" % dictConnexion["user"],
##                "--password=%s" % dictConnexion["password"],
##                "--single-transaction", 
##                "--opt", 
##                "--databases",
##                nomFichier,
##                ">",
##                fichierSave,
##                ]

            if "linux" in sys.platform :
                args = "%sbin/mysqldump --defaults-extra-file=%s --single-transaction --opt --databases %s > %s" % (repMySQL, nomFichierLoginTemp, nomFichier, fichierSave)
            else :
                args = [
                    "%sbin/mysqldump" % repMySQL,
                    "--defaults-extra-file=%s" % nomFichierLoginTemp,
                    "--single-transaction", 
                    "--opt", 
                    "--databases",
                    nomFichier,
                    ">",
                    fichierSave,
                    ]
            
            proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            out, temp = proc.communicate()
            
            if out != "" :
                print (out,)
                try :
                    out = str(out).decode("iso-8859-15")
                except :
                    pass
                dlgprogress.Destroy()
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur a �t� d�tect�e dans la proc�dure de sauvegarde !\n\nErreur : %s") % out, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                return False
            
            # Ins�re le fichier Sql dans le ZIP
            try :
                fichierZip.write(fichierSave, u"%s.sql" % nomFichier) #.decode("iso-8859-15")
            except Exception, err :
                dlgprogress.Destroy()
                print (err,)
                try :
                    err = str(err).decode("iso-8859-15")
                except :
                    pass
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur est survenue dans la sauvegarde !\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                return False
            
        # Supprime le r�pertoire temp
        shutil.rmtree(repTemp)
        
    # Finalise le fichier ZIP
    fichierZip.close()
    
    # Cryptage du fichier
    if motdepasse != None :
        dlgprogress.Update(numEtape, _(u"Cryptage du fichier..."));numEtape += 1
        fichierCrypte = u"%s.%s" % (nom, EXTENSIONS["crypte"])
        UTILS_Cryptage_fichier.CrypterFichier(_(u"Temp/%s") % nomFichierTemp, "Temp/%s" % fichierCrypte, base64.b64decode(motdepasse))
        nomFichierTemp = fichierCrypte
        extension = EXTENSIONS["crypte"]
    else:
        extension = EXTENSIONS["decrypte"]
    
    # Copie le fichier obtenu dans le r�pertoire donn�
    if repertoire != None :
        dlgprogress.Update(numEtape, _(u"Cr�ation du fichier dans le r�pertoire cible..."));numEtape += 1
        try :
            shutil.copy2(_(u"Temp/%s") % nomFichierTemp, fichierDest) 
        except :
            print "Le repertoire de destination de sauvegarde n'existe pas."
    
    # Envoi par Email
    if listeEmails != None :
        dlgprogress.Update(numEtape, _(u"Exp�dition de la sauvegarde par Email..."));numEtape += 1
        try :
            etat = UTILS_Envoi_email.Envoi_mail( 
                adresseExpediteur=dictAdresse["adresse"], 
                listeDestinataires=listeEmails, 
                #listeDestinatairesCCI=[], 
                sujetMail=_(u"Sauvegarde Noethys : %s") % nom, 
                texteMail=_(u"Envoi de la sauvegarde de Noethys"), 
                listeFichiersJoints=["Temp/%s" % nomFichierTemp,], 
                serveur=dictAdresse["smtp"], 
                port=dictAdresse["port"], 
                ssl=dictAdresse["connexionssl"], 
                motdepasse=dictAdresse["motdepasse"], 
                #listeImages=listeImages,
                )
        except Exception, err:
            dlgprogress.Destroy()
            print (err,)
            err = str(err).decode("iso-8859-15")
            dlgErreur = wx.MessageDialog(None, _(u"Une erreur a �t� d�tect�e dans l'envoi par Email !\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False
    
    # Suppression des r�pertoires et fichiers temporaires
    dlgprogress.Update(numEtape, _(u"Suppression des fichiers temporaires..."));numEtape += 1
    fichier = _(u"Temp/%s.%s") % (nom, EXTENSIONS["decrypte"])
    if os.path.isfile(fichier) == True :
        os.remove(fichier)
    fichier = _(u"Temp/%s.%s") % (nom, EXTENSIONS["crypte"])
    if os.path.isfile(fichier) == True :
        os.remove(fichier)
    
    # Fin du processus
    dlgprogress.Update(numEtape, _(u"Sauvegarde termin�e avec succ�s !"))
    dlgprogress.Destroy()
    
    return True

def VerificationZip(fichier=""):
    """ V�rifie que le fichier est une archive zip valide """
    return zipfile.is_zipfile(fichier)
    
def GetListeFichiersZIP(fichier):
    """ R�cup�re la liste des fichiers du ZIP """
    listeFichiers = []
    fichierZip = zipfile.ZipFile(fichier, "r")
    for fichier in fichierZip.namelist() :
        listeFichiers.append(fichier)
    return listeFichiers
    
def Restauration(parent=None, fichier="", listeFichiersLocaux=[], listeFichiersReseau=[], dictConnexion=None):
    """ Restauration � partir des listes de fichiers locaux et r�seau """
    listeFichiersRestaures = [] 
    
    # Initialisation de la barre de progression
    fichierZip = zipfile.ZipFile(fichier, "r")
    
    # Restauration des fichiers locaux Sqlite --------------------------------------------------------------------------------------------------------------------------------------
    if len(listeFichiersLocaux) > 0 :

        # V�rifie qu'on les remplace bien
        listeExistantsTemp = []
        for fichier in listeFichiersLocaux :
            if os.path.isfile(u"Data/%s" % fichier) == True :
                listeExistantsTemp.append(fichier)
                
        if len(listeExistantsTemp) > 0 :
            if len(listeExistantsTemp) == 1 :
                message = _(u"Le fichier '%s' existe d�j�.\n\nSouhaitez-vous vraiment le remplacer ?") % listeExistantsTemp[0]
            else :
                message = _(u"Les fichiers suivants existent d�j� :\n\n   - %s\n\nSouhaitez-vous vraiment les remplacer ?") % "\n   - ".join(listeExistantsTemp)
            dlg = wx.MessageDialog(parent, message, "Attention !", wx.YES_NO | wx.CANCEL |wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False
        
        # Restauration
        nbreEtapes = len(listeFichiersLocaux)
        dlgprogress = wx.ProgressDialog(_(u"Merci de patienter"), _(u"Lancement de la restauration..."), maximum=nbreEtapes, parent=parent, style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        numEtape = 1

        for fichier in listeFichiersLocaux :
            dlgprogress.Update(numEtape, _(u"Restauration du fichier %s...") % fichier);numEtape += 1
            try :
                buffer = fichierZip.read(fichier)
                f = open(u"Data/%s" % fichier, "wb")
                f.write(buffer)
                f.close()
            except Exception, err:
                dlgprogress.Destroy()
                print err
                dlg = wx.MessageDialog(None, _(u"La restauration du fichier '%s' a rencontr� l'erreur suivante : \n%s") % (fichier, err), "Erreur", wx.OK| wx.ICON_ERROR)  
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            listeFichiersRestaures.append(fichier[:-4])

    # Restauration des fichiers r�seau MySQL -------------------------------------------------------------------------------------------------------------------------
    if len(listeFichiersReseau) > 0 :
                        
        # R�cup�ration de la liste des fichiers MySQL de l'ordinateur
        listeFichiersExistants = GetListeFichiersReseau(dictConnexion)

        # Recherche du r�pertoire d'installation de MySQL
        repMySQL = GetRepertoireMySQL(dictConnexion) 
        if repMySQL == None :
            dlgErreur = wx.MessageDialog(None, _(u"Noethys n'a pas r�ussi � localiser MySQL sur votre ordinateur.\nNotez bien que MySQL doit �tre install� obligatoirement pour cr�er une restauration r�seau."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            dlgprogress.Destroy()
            return False

        # V�rifie qu'on les remplace bien
        listeExistantsTemp = []
        for fichier in listeFichiersReseau :
            fichier = fichier[:-4]
            if fichier in listeFichiersExistants :
                listeExistantsTemp.append(fichier)
                
        if len(listeExistantsTemp) > 0 :
            if len(listeExistantsTemp) == 1 :
                message = _(u"Le fichier '%s' existe d�j�.\n\nSouhaitez-vous vraiment le remplacer ?") % listeExistantsTemp[0]
            else :
                message = _(u"Les fichiers suivants existent d�j� :\n\n   - %s\n\nSouhaitez-vous vraiment les remplacer ?") % "\n   - ".join(listeExistantsTemp)
            dlg = wx.MessageDialog(parent, message, "Attention !", wx.YES_NO | wx.CANCEL |wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Cr�ation du r�pertoire temporaire
        repTemp = "Temp/restoretemp"
        if os.path.isdir(repTemp) == True :
            shutil.rmtree(repTemp)
        os.mkdir(repTemp)

        # Cr�ation du fichier de login
        nomFichierLoginTemp = os.path.abspath(os.curdir) + "/" + repTemp + "/logintemp.cnf"
        CreationFichierLoginTemp(host=dictConnexion["host"], port=dictConnexion["port"], user=dictConnexion["user"], password=dictConnexion["password"], nomFichier=nomFichierLoginTemp)

        # Restauration
        nbreEtapes = len(listeFichiersReseau)
        dlgprogress = wx.ProgressDialog(_(u"Merci de patienter"), _(u"Lancement de la restauration..."), maximum=nbreEtapes, parent=parent, style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        numEtape = 1

        for fichier in listeFichiersReseau :
            fichier = fichier[:-4]
            
            # Cr�ation de la base si elle n'existe pas
            if fichier not in listeFichiersExistants :
                nomFichier = u"%s;%s;%s;%s[RESEAU]%s" % (dictConnexion["port"], dictConnexion["host"], dictConnexion["user"], dictConnexion["password"], fichier)
                DB = GestionDB.DB(suffixe=None, nomFichier=nomFichier, modeCreation=True)
                DB.Close()
            
            fichierRestore = u"%s/%s.sql" % (repTemp, fichier)
            
            # Copie du fichier SQL dans le r�pertoire Temp/restoretemp
            buffer = fichierZip.read(u"%s.sql" % fichier)
            f = open(fichierRestore, "wb")
            f.write(buffer)
            f.close()
            
            # Importation du fichier SQL dans MySQL
            dlgprogress.Update(numEtape, _(u"Restauration du fichier %s...") % fichier);numEtape += 1
                        
##            args = [
##                "%sbin/mysql" % repMySQL,
##                "--host=%s" % dictConnexion["host"],
##                "--port=%s" % dictConnexion["port"],
##                "--user=%s" % dictConnexion["user"],
##                "--password=%s" % dictConnexion["password"],
##                fichier,
##                "<",
##                fichierRestore,
##                ]
            
            if "linux" in sys.platform :
                args = "%sbin/mysql --defaults-extra-file=%s %s < %s" % (repMySQL, nomFichierLoginTemp, fichier, fichierRestore)
            else :
                args = [
                    "%sbin/mysql" % repMySQL,
                    "--defaults-extra-file=%s" % nomFichierLoginTemp,
                    fichier,
                    "<",
                    fichierRestore,
                    ]
            
            proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            out, temp = proc.communicate()

            if out != "" :
                print (out,)
                out = str(out).decode("iso-8859-15")
                dlgprogress.Destroy()
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur a �t� d�tect�e dans la proc�dure de restauration !\n\nErreur : %s") % out, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                return False
            
            listeFichiersRestaures.append(fichier)
            
        # Supprime le r�pertoire temp
        shutil.rmtree(repTemp)

    # Fin de la proc�dure
    dlgprogress.Destroy()
    fichierZip.close()
    return listeFichiersRestaures
    

def GetListeFichiersReseau(dictValeurs={}):
    """ R�cup�re la liste des fichiers MySQL existants 
         dictValeurs = valeurs de connexion
    """
    import MySQLdb
    connexion = MySQLdb.connect(host=dictValeurs["hote"],user=dictValeurs["utilisateur"], passwd=dictValeurs["mdp"], port=dictValeurs["port"], use_unicode=True) 
    connexion.set_character_set('utf8')
    cursor = connexion.cursor()
    listeDatabases = []
    cursor.execute("SHOW DATABASES;")
    listeValeurs = cursor.fetchall()
    for valeurs in listeValeurs :
        listeDatabases.append(valeurs[0])
    connexion.close()
    return listeDatabases

def GetRepertoireMySQL(dictValeurs={}):
    """ R�cup�re le r�pertoire d'installation MySQL 
         dictValeurs = valeurs de connexion
    """
    # R�cup�ration du chemin de MySQL � partir de la base de donn�es
##    import MySQLdb
##    connexion = MySQLdb.connect(host=dictValeurs["hote"],user=dictValeurs["utilisateur"], passwd=dictValeurs["mdp"], port=dictValeurs["port"], use_unicode=True) 
##    connexion.set_character_set('utf8')
##    cursor = connexion.cursor()
##    cursor.execute("SELECT @@basedir;")
##    donnees = cursor.fetchall()
##    if len(donnees) == 0 : 
##        return None
##    return donnees[0][0]

    # 1- Recherche automatique
    if "linux" in sys.platform :
        if os.path.isfile(u"/usr/bin/mysqldump") and os.path.isfile(u"/usr/bin/mysql") :
            return u"/usr/"
    else :
        
        # V�rifie le chemin Canon (x86)
        chemin = "C:/Program Files (x86)/Canon/Easy-WebPrint EX/"
        if os.path.isfile(chemin + "bin/mysql.exe") :
            return chemin
        
        # V�rifie le chemin Canon
        chemin = "C:/Program Files/Canon/Easy-WebPrint EX/"
        if os.path.isfile(chemin + "bin/mysql.exe") :
            return chemin
        
        # V�rifie le chemin MySQL classique
        try :
            listeFichiers1 = os.listdir(u"C:/")
            for fichier1 in listeFichiers1 :
                
                if "Program" in fichier1 :
                    listeFichiers2 = os.listdir(u"C:/%s" % fichier1)
                    for fichier2 in listeFichiers2 :
                        if "MySQL" in fichier2 :
                            listeFichiers3 = os.listdir(u"C:/%s/%s" % (fichier1, fichier2))
                            listeFichiers3.sort(reverse=True)
                            for fichier3 in listeFichiers3 :
                                if "MySQL Server" in fichier3 :
                                    chemin = u"C:/%s/%s/%s/" % (fichier1, fichier2, fichier3)
                                    if os.path.isfile(chemin + "bin/mysql.exe") :
                                        return chemin
        except :
            pass
        
    # 2- Recherche dans le fichier Config
    try :
        chemin = UTILS_Config.GetParametre("sauvegarde_cheminmysql", defaut=None)
        if chemin != None :
            if os.path.isdir(chemin) :
                return chemin
    except :
        pass
        
    # 3- Demande le chemin � l'utilisateur
    try :
        if "linux" in sys.platform :
            message = _(u"Pour effectuer la sauvegarde de fichiers r�seau, mysqlclient doit �tre install�. S�lectionnez ici le r�pertoire o� se trouve 'mysqldump' sur votre ordinateur.")
        else :
            message = _(u"Pour effectuer la sauvegarde de fichiers r�seau, Noethys \ndoit utiliser les outils de MySQL. S�lectionnez ici le r�pertoire qui se nomme 'MySQL Server...' sur votre ordinateur.")
        dlg = wx.DirDialog(None, message, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            chemin = dlg.GetPath() + u"/"
            dlg.Destroy()    
        else:
            dlg.Destroy()    
            return None
    except :
        pass
    
    try :
        if os.path.isdir(chemin + _(u"bin/")) :
            UTILS_Config.SetParametre("sauvegarde_cheminmysql", chemin)
            return chemin
    except :
        pass
        
    return None

def CreationFichierLoginTemp(host="", user="", port="3306", password="", nomFichier=""):
    if os.path.isfile(nomFichier) == True :
        os.remove(nomFichier)
    fichier = open(nomFichier, "w")
    fichier.write(u"[client]\nhost=%s\nuser=%s\nport=%s\npassword=%s" % (host, user, port, password))
    fichier.close()


if __name__ == u"__main__":
    app = wx.App(0)
    import DLG_Sauvegarde
    frame_1 = DLG_Sauvegarde.Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
