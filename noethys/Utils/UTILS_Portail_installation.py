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
import UTILS_Fichiers
import UTILS_Portail_synchro
import traceback


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



class Abort(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Installer():
    def __init__(self, dict_parametres={}):
        self.dict_parametres = dict_parametres

        self.url_telechargement = "https://github.com/Noethys/Connecthys/archive/master.zip"
        self.nom_fichier_dest = UTILS_Fichiers.GetRepTemp(fichier="connecthys.zip")
        self.index = 0

    def Telecharger(self):
        """ Téléchargement de la source depuis Github """
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
        zfile = zipfile.ZipFile(fichier_zip, 'r')
        liste_fichiers = zfile.namelist()
        nbre_fichiers = len(liste_fichiers)

        index = 0
        for i in liste_fichiers:
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

    def EnvoiRepertoire(self, path, ftp, nbre_total):
        for name in os.listdir(path):

            self.index += 1

            # Barre de progression
            pourcentage = GetPourcentage(self.index, nbre_total)
            keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"Installation : Transfert du fichier %s...") % name)

            # Stoppe la procédure
            if keepGoing == False :
                raise Abort(u"Transfert interrompu")

            # Envoi des fichiers
            if IsException(name) == False :
                localpath = os.path.join(path, name)
                if os.path.isfile(localpath):
                    ftp.storbinary('STOR ' + name, open(localpath, 'rb'))

                    # Permission spéciale
                    if name == "portail.cgi" :
                        ftp.sendcmd("chmod 0755 portail.cgi")

                # Envoi des répertoires
                elif os.path.isdir(localpath):
                    try:
                        ftp.mkd(name)
                    except Exception, e:
                        # ignore "directory already exists"
                        if not e.args[0].startswith('550'):
                            raise

                    ftp.cwd(name)
                    self.EnvoiRepertoire(localpath, ftp, nbre_total)

                    ftp.cwd("..")

    def Upload(self, source_repertoire=""):
        # Récupération du nombre de fichiers à transférer
        nbreFichiers = GetNbreFichiers(source_repertoire)

        # Ouverture du FTP
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

        # Envoi des données
        self.index = 0
        #self.EnvoiRepertoire(source_repertoire, ftp, nbre_total=nbreFichiers+4)

        synchro = UTILS_Portail_synchro.Synchro(self.dict_parametres)

        # Envoi du fichier de config
        keepGoing, skip = self.dlgprogress.Update(98, _(u"Installation du fichier de configuration en cours..."))
        synchro.Upload_config(ftp=ftp)

        # Demande un upgrade de l'application
        keepGoing, skip = self.dlgprogress.Update(99, _(u"Demande la mise à jour de l'application..."))
        synchro.Upgrade_application()

        # Fermeture du FTP
        ftp.quit()


    def Installer(self):
        """ Installation de Connecthys """
        self.dlgprogress = wx.ProgressDialog(_(u"Veuillez patienter"), _(u"Lancement de l'installation..."), maximum=100, parent=None, style= wx.PD_SMOOTH | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)

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
            self.Telecharger()

            # Dézippage du fichier
            self.Dezipper(self.nom_fichier_dest, UTILS_Fichiers.GetRepTemp())

            # Envoi des fichiers par FTP
            source_repertoire = UTILS_Fichiers.GetRepTemp("Connecthys-master/connecthys")
            self.Upload(source_repertoire)

            # Fermeture dlgprogress
            self.dlgprogress.Destroy()

            return True

        except Abort as err:
            if self.dlgprogress != None :
                self.dlgprogress.Destroy()
            self.dlgprogress = None

            time.sleep(3)
            dlg = wx.MessageDialog(None, _(u"L'erreur suivante a été rencontrée : %s") % unicode(err), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        except Exception, err :
            if self.dlgprogress != None :
                self.dlgprogress.Destroy()

            traceback.print_exc()
            print "Erreur dans l'installation de l'application : ", err

            time.sleep(3)
            dlg = wx.MessageDialog(None, _(u"L'erreur suivante a été rencontrée : " + str(err)), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False




if __name__ == '__main__':
    app = wx.App(0)
    install = Installer()
    install.Installer()
    app.MainLoop()