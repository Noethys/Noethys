#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import os
import os.path
import ftplib
import time
import urllib
import urllib2
import zipfile
import shutil
from Utils import UTILS_Fichiers
from Utils import UTILS_Portail_synchro
import traceback
import sys
import importlib
import json
import stat
import paramiko


LISTE_EXCEPTIONS = ["*.pyc", "*.db", "*.db3", "*.exe"]

def IsException(name):
    if name in LISTE_EXCEPTIONS :
        return True
    for item in LISTE_EXCEPTIONS :
        if "*" in item :
            if name.endswith(item.replace("*", "")) :
                return True
    return False

def GetNbreFichiers(rep="") :
    """ Récupération du nombre des fichiers à transférer """
    def listdirectory(path):
        fichier=[]
        for root, dirs, files in os.walk(path):
            for i in files:
                if IsException(i) == False :
                    fichier.append(os.path.join(root, i))
        return fichier
    return len(listdirectory(rep))

def AffichetailleFichier(url):
    try :
        fichier = urllib2.urlopen(url)
        infoFichier = (fichier.info().getheaders('Content-Length'))
        if len(infoFichier) > 0 :
            tailleFichier = infoFichier[0]
        else :
            tailleFichier = 0
    except IOError :
        tailleFichier = 0
    return int(tailleFichier)

def GetPourcentage(index, taille):
    return int(index*100/taille)

def FormateTailleFichier(taille):
    if 0 <= taille <1000 :
        texte = str(taille) + " octets"
    elif 1000 <= taille < 1000000 :
        texte = str(taille/1000) + " Ko"
    else :
        texte = str(taille/1000000) + " Mo"
    return texte

def GetExclusions(liste_versions=[], version_ancienne=""):
    """ Récupération de la liste des exclusions entre 2 numéros de versions """
    """ Cette astuce permet d'alléger le téléchargement des mises à jour de Connecthys """
    nbre_versions = None
    dict_exclusions = {}
    for dictVersion in liste_versions :

        # Recherche de la version actuelle
        if dictVersion["version"] == version_ancienne :
            nbre_versions = 0

        else :

            # Recherche les exclusions à partir de la version trouvée
            if nbre_versions != None :

                if dictVersion.has_key("exclusions") :
                    for exclusion in dictVersion["exclusions"] :
                        if not dict_exclusions.has_key(exclusion) :
                            dict_exclusions[exclusion] = 0
                        dict_exclusions[exclusion] += 1

                nbre_versions += 1

    liste_exclusions = []
    for exclusion, nbre in dict_exclusions.iteritems() :
        if nbre == nbre_versions :
            liste_exclusions.append(exclusion)

    return liste_exclusions



class Abort(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)



class Installer():
    def __init__(self, parent, dict_parametres={}, server_ctrl=None):
        self.parent = parent
        self.dict_parametres = dict_parametres
        self.server_ctrl = server_ctrl

        self.url_telechargement = "https://github.com/Noethys/Connecthys/archive/master.zip"
        self.nom_fichier_dest = UTILS_Fichiers.GetRepTemp(fichier="connecthys.zip")
        self.index = 0

    def Telecharger(self):
        """ Téléchargement de la source depuis Github """
        self.dlgprogress = wx.ProgressDialog(_(u"Veuillez patienter"), _(u"Lancement de l'installation..."), maximum=100, parent=self.parent, style= wx.PD_SMOOTH | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)

        def _hook(nb_blocs, taille_bloc, taille_fichier):
            if nb_blocs % 5 == 0 :
                pourcentage = GetPourcentage(nb_blocs*taille_bloc, taille_fichier)
                keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"Téléchargement de Connecthys en cours... %s %%") % pourcentage)
                if keepGoing == False :
                    raise Abort(u"Téléchargement interrompu")

        urllib.urlretrieve(self.url_telechargement, self.nom_fichier_dest, _hook)

        return True

    def Dezipper(self, fichier_zip, chemin_dest=""):
        """ Dézippe un fichier ZIP dans un répertoire donné """
        #self.dlgprogress = wx.ProgressDialog(_(u"Veuillez patienter"), _(u"Lancement de l'installation..."), maximum=100, parent=self.parent, style= wx.PD_SMOOTH | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        self.dlgprogress.Raise()

        zfile = zipfile.ZipFile(fichier_zip, 'r')
        liste_fichiers = zfile.namelist()
        nbre_fichiers = len(liste_fichiers)

        index = 0
        for i in liste_fichiers:
            wx.Yield()
            pourcentage = GetPourcentage(index, nbre_fichiers)
            keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"Décompression de Connecthys en cours... %s %%") % pourcentage)
            if os.path.isdir(os.path.join(chemin_dest, i)) or "2.5" in i or "." not in i :
                try: os.makedirs(os.path.join(chemin_dest, i))
                except: pass
            else:
                try: os.makedirs(os.path.join(chemin_dest, os.path.dirname(i)))
                except: pass
                data = zfile.read(i)
                fp = open(os.path.join(chemin_dest, i), "wb")
                fp.write(data)
                fp.close()
            index += 1
        zfile.close()


    def TransfertRepertoire(self, path="", ftp=None, destpath="", nbre_total=0, liste_exclusions=[]):
        for name in os.listdir(path):
            wx.Yield()

            # Envoi des fichiers
            if IsException(name) == False :
                localpath = os.path.join(path, name)
                if os.path.isfile(localpath):
                    self.index += 1

                    # Barre de progression
                    pourcentage = GetPourcentage(self.index, nbre_total)
                    try :
                        keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"Installation : Transfert du fichier %s...") % name)
                    except Exception, err :
                        keepGoing = True

                    # Stoppe la procédure
                    if keepGoing == False :
                        raise Abort(u"Transfert interrompu")

                    # Transfert local
                    if self.dict_parametres["hebergement_type"] == 0 :
                        fulldestpath = os.path.join(destpath, name)
                        #os.renames(localpath, fulldestpath)
                        shutil.move(localpath, fulldestpath)

                    # Transfert FTP
                    if self.dict_parametres["hebergement_type"] == 1 :
                        ftp.storbinary('STOR ' + name, open(localpath, 'rb'))

                        # Permission spéciale
                        # ATTENTION: beaucoup d'hebergements n autorisent pas le chmod/ftp et ftplib ne permet pas de lister les commandes acceptees par le serveur ftp
                        # TODO: boite de dialogue pour indiquer de modifier les droits autrement
                        if self.dict_parametres["serveur_type"] == 1 and name == self.dict_parametres["serveur_cgi_file"] :
                            try :
                                ftp.sendcmd("chmod 0755 %s" % self.dict_parametres["serveur_cgi_file"])
                            except Exception, err :
                                print "CHMOD 755 sur %s impossible :" % self.dict_parametres["serveur_cgi_file"], err

                            if "mode=0755" not in ftp.sendcmd("MLST %s" % self.dict_parametres["serveur_cgi_file"]) :
                                message = u"Attention, le fichier %s n'a pas les bonnes permissions." % self.dict_parametres["serveur_cgi_file"]
                                self.parent.EcritLog(message)
                                print message


                    # Transfert SSH/SFTP
                    if self.dict_parametres["hebergement_type"] == 2 :
                        ftp.put(localpath, os.path.join(destpath, name))

                        # Permission spéciale
                        if self.dict_parametres["serveur_type"] == 1 and name == self.dict_parametres["serveur_cgi_file"] :
                            try :
                                ftp.chmod(os.path.join(destpath, name), mode=0755)
                            except Exception, err :
                                print "CHMOD 0755 sur %s impossible :" % self.dict_parametres["serveur_cgi_file"], err

                            # Vérifie les droits du fichier cgi (connecthys.cgi par défaut)
                            mode = int(oct(stat.S_IMODE(ftp.stat(os.path.join(destpath, name)).st_mode)))
                            if mode != 755 :
                                message = u"Attention, le fichier %s n'a pas les bonnes permissions : %d au lieu de 0755." % (self.dict_parametres["serveur_cgi_file"], mode)
                                self.parent.EcritLog(message)
                                print message

                # Envoi des répertoires
                elif os.path.isdir(localpath):

                    if name not in liste_exclusions :

                        # Création d'un répertoire local
                        if self.dict_parametres["hebergement_type"] == 0 :
                            # Remplissage du répertoire local
                            fulldestpath = os.path.join(destpath, name)
                            try:
                                os.makedirs(fulldestpath)
                            except Exception, err :
                                pass

                            self.TransfertRepertoire(path=localpath, destpath=fulldestpath, nbre_total=nbre_total, liste_exclusions=liste_exclusions)

                        # Création et remplissage d'un répertoire FTP
                        if self.dict_parametres["hebergement_type"] == 1 :
                            try :
                                ftp.mkd(name)
                            except Exception, e:
                                # ignore "directory already exists"
                                if not e.args[0].startswith('550'):
                                    raise

                            # Remplissage du répertoire FTP
                            ftp.cwd(name)
                            self.TransfertRepertoire(path=localpath, ftp=ftp, nbre_total=nbre_total, liste_exclusions=liste_exclusions)
                            ftp.cwd("..")

                        # Création et remplissage d'un répertoire SSH/SFTP
                        if self.dict_parametres["hebergement_type"] == 2 :
                            try :
                                ftp.mkdir(name)
                            except Exception, e:
                                pass
                                # ignore "directory already exists"
                                #if not e.args[0].startswith('550'):
                                #    raise

                            # Remplissage du répertoire SSH/SFTP
                            ftp.chdir(name)
                            self.TransfertRepertoire(path=localpath, ftp=ftp, nbre_total=nbre_total, liste_exclusions=liste_exclusions)
                            ftp.chdir("..")

    def Upload(self, source_repertoire=""):
        # Récupération du nombre de fichiers à transférer
        nbreFichiers = GetNbreFichiers(source_repertoire)

        # Initialisation pour transfert local
        if self.dict_parametres["hebergement_type"] == 0 :
            keepGoing, skip = self.dlgprogress.Update(1, _(u"Préparation de la copie..."))

            # Création du répertoire s'il n'existe pas
            localrep = self.dict_parametres["hebergement_local_repertoire"]
            try:
                os.makedirs(localrep)
            except Exception, e:
                print e

            keepGoing, skip = self.dlgprogress.Update(2, _(u"La copie va commencer..."))
            ftp = None

        # Initialisation pour transfert FTP
        if self.dict_parametres["hebergement_type"] == 1 :
            keepGoing, skip = self.dlgprogress.Update(1, _(u"Connexion FTP en cours..."))
            ftp = ftplib.FTP(self.dict_parametres["ftp_serveur"], self.dict_parametres["ftp_utilisateur"], self.dict_parametres["ftp_mdp"])

            # Création du répertoire s'il n'existe pas
            try:
                ftp.mkd(self.dict_parametres["ftp_repertoire"])
            except Exception, e:
                # ignore "directory already exists"
                if not e.args[0].startswith('550'):
                    raise

            ftp.cwd(self.dict_parametres["ftp_repertoire"])
            keepGoing, skip = self.dlgprogress.Update(2, _(u"Connexion FTP effectuée..."))

        # Initialisation pour un transfert SSH
        if self.dict_parametres["hebergement_type"] == 2 :
            keepGoing, skip = self.dlgprogress.Update(1, _(u"Connexion SSH/SFTP en cours..."))

            try :
                ftp = self.server_ctrl.ssh.open_sftp()
            except Exception, err:
                print err
                self.parent.EcritLog(_(u"[ERREUR] %s") % err)
                raise

            # Création du répertoire s'il n'existe pas
            try:
                ftp.mkdir(self.dict_parametres["ssh_repertoire"])
            except Exception, e:
                pass
                # ignore "directory already exists"
                #if not e.args[0].startswith('550'):
                #    raise

            ftp.chdir(self.dict_parametres["ssh_repertoire"])
            keepGoing, skip = self.dlgprogress.Update(2, _(u"Connexion SSH/SFTP effectuée..."))

        # Recherche le numéro de version de l'application déjà installée
        try :
        # ATTENTION: ne peut fonctionner que si Connecthys est lancé
            if self.dict_parametres["serveur_type"] == 0 :
                url = self.dict_parametres["url_connecthys"]
            if self.dict_parametres["serveur_type"] == 1 :
                url = self.dict_parametres["url_connecthys"] + "/" + self.dict_parametres["serveur_cgi_file"]
            if self.dict_parametres["serveur_type"] == 2 :
                url = self.dict_parametres["url_connecthys"]
            url += "/get_version"

            # Récupération des données au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            data = json.loads(page)
            version_ancienne = data["version_str"]
        except Exception, err :
            version_ancienne = None

        # Recherche des exclusions
        if version_ancienne == None :
            liste_exclusions = []
        else :
            # Importation de la liste des exclusions dans le répertoire source
            nomFichier = "versions.py"
            chemin = os.path.join(source_repertoire, "application")
            sys.path.append(chemin)
            versions = importlib.import_module(nomFichier.replace(".py", ""))
            liste_exclusions = GetExclusions(liste_versions=versions.VERSIONS, version_ancienne=version_ancienne)

        # Envoi des données
        self.index = 0

        # Transfert local
        if self.dict_parametres["hebergement_type"] == 0 :
            dest_repertoire = self.dict_parametres["hebergement_local_repertoire"]
            self.TransfertRepertoire(path=source_repertoire, destpath=dest_repertoire, nbre_total=nbreFichiers+5, liste_exclusions=liste_exclusions)

        # Transfert FTP
        if self.dict_parametres["hebergement_type"] == 1 :
            self.TransfertRepertoire(path=source_repertoire, ftp=ftp, nbre_total=nbreFichiers+5, liste_exclusions=liste_exclusions)

        # Transfert SSH
        if self.dict_parametres["hebergement_type"] == 2 :
            self.TransfertRepertoire(path=source_repertoire, ftp=ftp, nbre_total=nbreFichiers+5, liste_exclusions=liste_exclusions)

        synchro = UTILS_Portail_synchro.Synchro(self.dict_parametres, log=self.parent)

        # Envoi du fichier de config
        keepGoing, skip = self.dlgprogress.Update(97, _(u"Installation du fichier de configuration en cours..."))
        synchro.Upload_config(ftp=ftp)

        time.sleep(4)

        # Démarrage du serveur ici si serveur autonome
        if self.server_ctrl != None and self.dict_parametres["serveur_type"] == 0 and self.server_ctrl.GetServerStatus() == False:
            keepGoing, skip = self.dlgprogress.Update(98, _(u"Tentative de lancement du serveur Connecthys..."))
            self.server_ctrl.Demarrer_serveur(event=None)

        # Demande un upgrade de l'application
        keepGoing, skip = self.dlgprogress.Update(99, _(u"Demande la mise à jour de l'application..."))
        synchro.Upgrade_application()

        # Fermeture du FTP
        if self.dict_parametres["hebergement_type"] == 1 :
            ftp.quit()

        # Fermeture du SFTP
        if self.dict_parametres["hebergement_type"] == 2 :
            ftp.close()

    def Installer(self):
        """ Installation de Connecthys """
        dlg = wx.MessageDialog(None, _(u"Confirmez-vous l'installation du portail internet Connecthys ?\n\nRemarque : Ce processus peut nécessiter plusieurs dizaines de minutes (selon votre connexion internet)"), _(u"Installation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        try :

            # Recherche la taille du fichier à télécharger sur Github
            num_essai = 1
            taille_fichier = 0
            while num_essai < 3 :
                taille_fichier = AffichetailleFichier(self.url_telechargement)
                if taille_fichier > 0 :
                    break
                else :
                    time.sleep(1)

            if taille_fichier == 0 :
                raise Abort(u"Impossible de trouver le source de Connecthys sur internet ! ")

            # Téléchargement de la source sur Github
            self.parent.EcritLog(_(u"Téléchargement des fichiers source Connecthys"))
            self.Telecharger()

            # Dézippage du fichier
            self.parent.EcritLog(_(u"Décompression des fichiers source Connecthys"))
            self.Dezipper(self.nom_fichier_dest, UTILS_Fichiers.GetRepTemp())

            # Envoi des fichiers dans le répertoire d installation
            self.parent.EcritLog(_(u"Upload des fichiers Connecthys"))
            source_repertoire = UTILS_Fichiers.GetRepTemp("Connecthys-master/connecthys")
            self.Upload(source_repertoire)

        except Abort :
            wx.Yield()
            if self.dlgprogress != None :
                self.dlgprogress.Destroy()
                del self.dlgprogress

            time.sleep(2)
            dlg = wx.MessageDialog(None, _(u"Procédure d'installation interrompue."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.Raise()
            dlg.ShowModal()
            dlg.Destroy()
            return False

        except Exception, err :
            wx.Yield()
            if self.dlgprogress != None :
                self.dlgprogress.Destroy()
                del self.dlgprogress

            traceback.print_exc()
            print "Erreur dans l'installation de l'application : "
            print err

            time.sleep(2)
            dlg = wx.MessageDialog(None, _(u"Une erreur a été rencontrée !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.Raise()
            dlg.ShowModal()
            dlg.Destroy()
            return False

        try :
            wx.CallAfter(self.dlgprogress.Destroy)
            del self.dlgprogress
        except :
            pass

        # Message de confirmation
        dlg = wx.MessageDialog(None, _(u"L'installation s'est terminée avec succès.\n\nVous devriez pouvoir maintenant lancer une synchronisation des données."), "Fin de l'installation", wx.OK | wx.ICON_INFORMATION)
        dlg.Raise()
        dlg.ShowModal()
        dlg.Destroy()
        return True



if __name__ == '__main__':
    app = wx.App(0)
    install = Installer()
    install.Installer()
    app.MainLoop()
