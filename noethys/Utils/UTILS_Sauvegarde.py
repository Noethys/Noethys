#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import six
import os
import sys
import base64
import zipfile
import GestionDB
import subprocess
import shutil
import time

import GestionDB
from Utils import UTILS_Fichiers
from Utils import UTILS_Config
from Utils import UTILS_Cryptage_fichier
from Utils import UTILS_Fichiers
from Utils import UTILS_Envoi_email


LISTE_CATEGORIES = [
    (_(u"Données de base"), "DATA"),
    (_(u"Photos individuelles"), "PHOTOS"),
    (_(u"Documents"), "DOCUMENTS"),
    ]

EXTENSIONS = {
    "decrypte" : "nod",
    "crypte" : "noc",
    }




def Sauvegarde(listeFichiersLocaux=[], listeFichiersReseau=[], nom="", repertoire=None, motdepasse=None, listeEmails=None, dictConnexion=None):
    """ Processus de de création du ZIP """
    # Si aucun fichier à sauvegarder
    if len(listeFichiersLocaux) == 0 and len(listeFichiersReseau) == 0 : 
        return False
    
    # Initialisation de la barre de progression
    nbreEtapes = 3
    nbreEtapes += len(listeFichiersLocaux)
    nbreEtapes += len(listeFichiersReseau)
    if motdepasse != None : nbreEtapes += 1
    if repertoire != None : nbreEtapes += 1
    if listeEmails != None : nbreEtapes += 1
    
    # Création du nom du fichier de destination
    if motdepasse != None :
        extension = EXTENSIONS["crypte"]
    else:
        extension = EXTENSIONS["decrypte"]

    # Vérifie si fichier de destination existe déjà
    if repertoire != None :
        fichierDest = u"%s/%s.%s" % (repertoire, nom, extension)
        if os.path.isfile(fichierDest) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier de sauvegarde portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

    # Récupération des paramètres de l'adresse d'expéditeur par défaut
    if listeEmails != None :
        dictAdresse = UTILS_Envoi_email.GetAdresseExpDefaut()
        if dictAdresse == None :
            dlgErreur = wx.MessageDialog(None, _(u"Envoi par Email impossible :\n\nAucune adresse d'expéditeur n'a été définie. Veuillez la saisir dans le menu Paramétrage du logiciel..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False

    # Fenêtre de progression
    dlgprogress = wx.ProgressDialog(_(u"Sauvegarde"), _(u"Lancement de la sauvegarde..."), maximum=nbreEtapes, parent=None, style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
    
    # Création du fichier ZIP temporaire
    nomFichierTemp = u"%s.%s" % (nom, EXTENSIONS["decrypte"])
    fichierZip = zipfile.ZipFile(UTILS_Fichiers.GetRepTemp(fichier=nomFichierTemp), "w", compression=zipfile.ZIP_DEFLATED)
    numEtape = 1
    dlgprogress.Update(numEtape, _(u"Création du fichier de compression..."));numEtape += 1
    
    # Intégration des fichiers locaux
    for nomFichier in listeFichiersLocaux :
        dlgprogress.Update(numEtape, _(u"Compression du fichier %s...") % nomFichier);numEtape += 1
        fichier = UTILS_Fichiers.GetRepData(nomFichier)
        if os.path.isfile(fichier) == True :
            fichierZip.write(fichier, nomFichier)
        else :
            dlgprogress.Destroy()
            dlgErreur = wx.MessageDialog(None, _(u"Le fichier '%s' n'existe plus sur cet ordinateur. \n\nVeuillez ôter ce fichier de la procédure de sauvegarde automatique (Menu Fichier > Sauvegardes automatiques)") % nomFichier, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False
        
    # Intégration des fichiers réseau
    if len(listeFichiersReseau) > 0 and dictConnexion != None :
        
        # Création du répertoire temporaire
        repTemp = UTILS_Fichiers.GetRepTemp(fichier="savetemp")
        if os.path.isdir(repTemp) == True :
            shutil.rmtree(repTemp)
        os.mkdir(repTemp)
        
        # Recherche du répertoire d'installation de MySQL
        repMySQL = GetRepertoireMySQL(dictConnexion) 
        if repMySQL == None :
            dlgprogress.Destroy()
            dlgErreur = wx.MessageDialog(None, _(u"Noethys n'a pas réussi à localiser MySQL sur votre ordinateur.\n\nNotez bien que MySQL doit être installé obligatoirement pour créer une sauvegarde réseau."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False
        
        # Création du fichier de login
        nomFichierLoginTemp = repTemp + "/logintemp.cnf" #os.path.abspath(os.curdir) + "/" + repTemp + "/logintemp.cnf"
        CreationFichierLoginTemp(host=dictConnexion["host"], port=dictConnexion["port"], user=dictConnexion["user"], password=dictConnexion["password"], nomFichier=nomFichierLoginTemp)
        
        # Création du backup pour chaque fichier MySQL
        for nomFichier in listeFichiersReseau :
            dlgprogress.Update(numEtape, _(u"Compression du fichier %s...") % nomFichier);numEtape += 1
            fichierSave = u"%s/%s.sql" % (repTemp, nomFichier)

            args = u""""%sbin/mysqldump" --defaults-extra-file="%s" --single-transaction --opt --databases %s > "%s" """ % (repMySQL, nomFichierLoginTemp, nomFichier, fichierSave)
            print(("Chemin mysqldump =", args))
            if six.PY2:
                args = args.encode('utf8')
            proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            out, temp = proc.communicate()

            if out not in ("", b""):
                print((out,))
                try :
                    if six.PY2:
                        out = str(out).decode("iso-8859-15")
                except :
                    pass
                dlgprogress.Destroy()
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur a été détectée dans la procédure de sauvegarde !\n\nErreur : %s") % out, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                return False

            # Insère le fichier Sql dans le ZIP
            try :
                fichierZip.write(fichierSave.encode('utf8'), u"%s.sql" % nomFichier)
            except Exception as err :
                dlgprogress.Destroy()
                print(("insertion sql dans zip : ", err,))
                try :
                    if six.PY2:
                        err = str(err).decode("iso-8859-15")
                except :
                    pass
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur est survenue dans la sauvegarde !\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                return False

        # Supprime le répertoire temp
        shutil.rmtree(repTemp)

    # Finalise le fichier ZIP
    fichierZip.close()
    
    # Cryptage du fichier
    if motdepasse != None :
        dlgprogress.Update(numEtape, _(u"Cryptage du fichier..."));numEtape += 1
        fichierCrypte = u"%s.%s" % (nom, EXTENSIONS["crypte"])
        motdepasse = base64.b64decode(motdepasse)
        if six.PY3:
            motdepasse = motdepasse.decode('utf8')
        UTILS_Cryptage_fichier.CrypterFichier(UTILS_Fichiers.GetRepTemp(fichier=nomFichierTemp), UTILS_Fichiers.GetRepTemp(fichier=fichierCrypte), motdepasse, ancienne_methode=True)
        nomFichierTemp = fichierCrypte
        extension = EXTENSIONS["crypte"]
    else:
        extension = EXTENSIONS["decrypte"]
    
    # Copie le fichier obtenu dans le répertoire donné
    if repertoire != None :
        dlgprogress.Update(numEtape, _(u"Création du fichier dans le répertoire cible..."));numEtape += 1
        try :
            shutil.copy2(UTILS_Fichiers.GetRepTemp(fichier=nomFichierTemp), fichierDest)
        except :
            print("Le repertoire de destination de sauvegarde n'existe pas.")

    # Préparation du message
    message = UTILS_Envoi_email.Message(destinataires=listeEmails, sujet=_(u"Sauvegarde Noethys : %s") % nom,
                                        texte_html=_(u"Envoi de la sauvegarde de Noethys"),
                                        fichiers=[UTILS_Fichiers.GetRepTemp(fichier=nomFichierTemp),])

    # Envoi par Email
    if listeEmails != None :
        dlgprogress.Update(numEtape, _(u"Expédition de la sauvegarde par Email..."));numEtape += 1
        try :
            messagerie = UTILS_Envoi_email.Messagerie(backend=dictAdresse["moteur"], hote=dictAdresse["smtp"], port=dictAdresse["port"], utilisateur=dictAdresse["utilisateur"],
                                                      motdepasse=dictAdresse["motdepasse"], email_exp=dictAdresse["adresse"], use_tls=dictAdresse["startTLS"],
                                                      timeout=60*3, parametres=dictAdresse["parametres"])
            messagerie.Connecter()
            messagerie.Envoyer(message)
            messagerie.Fermer()
        except Exception as err:
            dlgprogress.Destroy()
            print((err,))
            if six.PY2:
                err = str(err).decode("iso-8859-15")
            dlgErreur = wx.MessageDialog(None, _(u"Une erreur a été détectée dans l'envoi par Email !\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False
    
    # Suppression des répertoires et fichiers temporaires
    dlgprogress.Update(numEtape, _(u"Suppression des fichiers temporaires..."));numEtape += 1
    fichier = UTILS_Fichiers.GetRepTemp(fichier=u"%s.%s" % (nom, EXTENSIONS["decrypte"]))
    if os.path.isfile(fichier) == True :
        os.remove(fichier)
    fichier = UTILS_Fichiers.GetRepTemp(fichier=u"%s.%s" % (nom, EXTENSIONS["crypte"]))
    if os.path.isfile(fichier) == True :
        os.remove(fichier)
    
    # Fin du processus
    dlgprogress.Update(numEtape, _(u"Sauvegarde terminée avec succès !"))
    dlgprogress.Destroy()
    
    return True

def VerificationZip(fichier=""):
    """ Vérifie que le fichier est une archive zip valide """
    return zipfile.is_zipfile(fichier)
    
def GetListeFichiersZIP(fichier):
    """ Récupère la liste des fichiers du ZIP """
    listeFichiers = []
    fichierZip = zipfile.ZipFile(fichier, "r")
    for fichier in fichierZip.namelist() :
        listeFichiers.append(fichier)
    return listeFichiers
    
def Restauration(parent=None, fichier="", listeFichiersLocaux=[], listeFichiersReseau=[], dictConnexion=None):
    """ Restauration à partir des listes de fichiers locaux et réseau """
    listeFichiersRestaures = [] 
    
    # Initialisation de la barre de progression
    fichierZip = zipfile.ZipFile(fichier, "r")
    #fichierZip = MyZipFile(fichier, "r")

    # Restauration des fichiers locaux Sqlite ------------------------------------------------------------------------------
    if len(listeFichiersLocaux) > 0 :

        # Vérifie qu'on les remplace bien
        listeExistantsTemp = []
        for fichier in listeFichiersLocaux :
            if os.path.isfile(UTILS_Fichiers.GetRepData(fichier)) == True :
                listeExistantsTemp.append(fichier)
                
        if len(listeExistantsTemp) > 0 :
            if len(listeExistantsTemp) == 1 :
                message = _(u"Le fichier '%s' existe déjà.\n\nSouhaitez-vous vraiment le remplacer ?") % listeExistantsTemp[0]
            else :
                message = _(u"Les fichiers suivants existent déjà :\n\n   - %s\n\nSouhaitez-vous vraiment les remplacer ?") % "\n   - ".join(listeExistantsTemp)
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
                # buffer = fichierZip.read(fichier)
                # f = open(UTILS_Fichiers.GetRepData(fichier), "wb")
                # f.write(buffer)
                # f.close()
                fichierZip.extract(fichier, UTILS_Fichiers.GetRepData())
            except Exception as err:
                dlgprogress.Destroy()
                print(err)
                dlg = wx.MessageDialog(None, _(u"La restauration du fichier '%s' a rencontré l'erreur suivante : \n%s") % (fichier, err), "Erreur", wx.OK| wx.ICON_ERROR)  
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            listeFichiersRestaures.append(fichier[:-4])

    # Restauration des fichiers réseau MySQL -------------------------------------------------------------------------------------------------------------------------
    if len(listeFichiersReseau) > 0 :
                        
        # Récupération de la liste des fichiers MySQL de l'ordinateur
        listeFichiersExistants = GetListeFichiersReseau(dictConnexion)

        # Recherche du répertoire d'installation de MySQL
        repMySQL = GetRepertoireMySQL(dictConnexion) 
        if repMySQL == None :
            dlgErreur = wx.MessageDialog(None, _(u"Noethys n'a pas réussi à localiser MySQL sur votre ordinateur.\nNotez bien que MySQL doit être installé obligatoirement pour créer une restauration réseau."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            return False

        # Vérifie qu'on les remplace bien
        listeExistantsTemp = []
        for fichier in listeFichiersReseau :
            fichier = fichier[:-4]
            if fichier in listeFichiersExistants :
                listeExistantsTemp.append(fichier)
                
        if len(listeExistantsTemp) > 0 :
            if len(listeExistantsTemp) == 1 :
                message = _(u"Le fichier '%s' existe déjà.\n\nSouhaitez-vous vraiment le remplacer ?") % listeExistantsTemp[0]
            else :
                message = _(u"Les fichiers suivants existent déjà :\n\n   - %s\n\nSouhaitez-vous vraiment les remplacer ?") % "\n   - ".join(listeExistantsTemp)
            dlg = wx.MessageDialog(parent, message, "Attention !", wx.YES_NO | wx.CANCEL |wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Création du répertoire temporaire
        repTemp = UTILS_Fichiers.GetRepTemp(fichier="restoretemp")
        if os.path.isdir(repTemp) == True :
            shutil.rmtree(repTemp)
        os.mkdir(repTemp)

        # Création du fichier de login
        nomFichierLoginTemp = repTemp + "/logintemp.cnf" #os.path.abspath(os.curdir) + "/" + repTemp + "/logintemp.cnf"
        CreationFichierLoginTemp(host=dictConnexion["host"], port=dictConnexion["port"], user=dictConnexion["user"], password=dictConnexion["password"], nomFichier=nomFichierLoginTemp)

        # Restauration
        nbreEtapes = len(listeFichiersReseau)
        dlgprogress = wx.ProgressDialog(_(u"Merci de patienter"), _(u"Lancement de la restauration..."), maximum=nbreEtapes, parent=parent, style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        numEtape = 1

        for fichier in listeFichiersReseau:
            fichier = fichier[:-4]
            
            # Création de la base si elle n'existe pas
            if fichier not in listeFichiersExistants :
                nomFichier = u"%s;%s;%s;%s[RESEAU]%s" % (dictConnexion["port"], dictConnexion["host"], dictConnexion["user"], dictConnexion["password"], fichier)
                DB = GestionDB.DB(suffixe=None, nomFichier=nomFichier, modeCreation=True)
                DB.Close()

            # Copie du fichier SQL dans le répertoire Temp / restoretemp
            # buffer = fichierZip.read(u"%s.sql" % fichier)
            # f = open(fichierRestore, "wb")
            # f.write(buffer)
            # f.close()
            fichierZip.extract(u"%s.sql" % fichier, repTemp)
            fichierRestore = u"%s/%s.sql" % (repTemp, fichier)

            # Importation du fichier SQL dans MySQL
            dlgprogress.Update(numEtape, _(u"Restauration du fichier %s...") % fichier);numEtape += 1

            args = u""""%sbin/mysql" --defaults-extra-file="%s" %s < "%s" """ % (repMySQL, nomFichierLoginTemp, fichier, fichierRestore)
            print(("Chemin mysql =", args))
            if six.PY2:
                args = args.encode("iso-8859-15")
            proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            out, temp = proc.communicate()

            if out not in ("", b"") :
                print(("subprocess de restauration mysql :", out))
                if six.PY2:
                    out = str(out).decode("iso-8859-15")
                dlgprogress.Destroy()
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur a été détectée dans la procédure de restauration !\n\nErreur : %s") % out, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                return False
            
            listeFichiersRestaures.append(fichier)
            
        # Supprime le répertoire temp
        shutil.rmtree(repTemp)

    # Fin de la procédure
    dlgprogress.Destroy()
    fichierZip.close()
    return listeFichiersRestaures
    

def GetListeFichiersReseau(dictValeurs={}):
    """ Récupère la liste des fichiers MySQL existants 
         dictValeurs = valeurs de connexion
    """
    hote = dictValeurs["hote"]
    utilisateur = dictValeurs["utilisateur"]
    motdepasse = dictValeurs["mdp"]
    port = dictValeurs["port"]

    DB = GestionDB.DB(nomFichier=u"%s;%s;%s;%s[RESEAU]" % (port, hote, utilisateur, motdepasse))
    if DB.echec == 1 :
        DB.Close()
        return []
    
    DB.ExecuterReq("SHOW DATABASES;")
    listeValeurs = DB.ResultatReq()
    DB.Close()
    
    listeDatabases = []
    for valeurs in listeValeurs :
        listeDatabases.append(valeurs[0])
    
    return listeDatabases

def GetRepertoireMySQL(dictValeurs={}):
    """ Récupère le répertoire d'installation MySQL 
         dictValeurs = valeurs de connexion
    """
    # Récupération du chemin de MySQL à partir de la base de données
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
        
        # Vérifie le chemin Canon (x86)
        chemin = "C:/Program Files (x86)/Canon/Easy-WebPrint EX/"
        if os.path.isfile(chemin + "bin/mysql.exe") :
            return chemin
        
        # Vérifie le chemin Canon
        chemin = "C:/Program Files/Canon/Easy-WebPrint EX/"
        if os.path.isfile(chemin + "bin/mysql.exe") :
            return chemin
        
        # Vérifie le chemin MySQL classique
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
        
    # 3- Demande le chemin à l'utilisateur
    try :
        if "linux" in sys.platform :
            message = _(u"Pour effectuer la sauvegarde de fichiers réseau, mysqlclient doit être installé. Sélectionnez ici le répertoire où se trouve 'mysqldump' sur votre ordinateur.")
        else :
            message = _(u"Pour effectuer la sauvegarde de fichiers réseau, Noethys \ndoit utiliser les outils de MySQL. Sélectionnez ici le répertoire qui se nomme 'MySQL Server...' sur votre ordinateur.")
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
    password = GestionDB.DecodeMdpReseau(password)
    if os.path.isfile(nomFichier) == True :
        os.remove(nomFichier)
    fichier = open(nomFichier, "w")
    fichier.write(u"[client]\nhost=%s\nuser=%s\nport=%s\npassword=%s" % (host, user, port, password))
    fichier.close()


if __name__ == u"__main__":
    app = wx.App(0)
    from Dlg import DLG_Sauvegarde
    frame_1 = DLG_Sauvegarde.Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
