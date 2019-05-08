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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
import sys 
from time import sleep 
from threading import Thread 
from six.moves.urllib.request import Request, urlopen, urlretrieve
import os
import six
import zipfile
import glob

from Ctrl import CTRL_Bandeau
from Utils import UTILS_Fichiers



#------------------------------------------------------------------------------------------
# Pour les tests, mettre sur True
DEBUG = False
#------------------------------------------------------------------------------------------





def AffichetailleFichier(fichierURL):
    tailleFichier = 0
    try :
        fichier = urlopen(fichierURL)
        if six.PY3:
            tailleFichier = fichier.headers['Content-Length']
        else:
            infoFichier = (fichier.info().getheaders('Content-Length'))
            if len(infoFichier) > 0 :
                tailleFichier = infoFichier[0]
    except IOError :
        tailleFichier = 0
    return tailleFichier

def AffichePourcentage(stade, taille):
    pourcent = int(stade*100/taille)
    pourcent = str(pourcent) + " %"
    return pourcent
    
def FormateTailleFichier(taille):
    if 0 <= taille <1000 :
        texte = str(taille) + " octets"
    elif 1000 <= taille < 1000000 :
        texte = str(taille//1000) + " Ko"
    else :
        texte = str(taille//1000000) + " Mo"
    return texte


    
##def zipdirectory(journal, filezip, pathzip):
##    """ Sauvegarde globale """
##    lenpathparent = len(pathzip)+1
##    
##    def _zipdirectory(zfile, path):
##        for i in glob.glob(path+'/*'):
##            if os.path.isdir(i): 
##                if i.endswith("Updates") == False : # On sauvegarde pas le dossier Updates
##                    _zipdirectory(zfile, i )
##            else:
##                nomFichier = os.path.split(i)[1]
##                journal.WriteText("..." + nomFichier + "\n")
##                zfile.write(i, i[lenpathparent:]) 
##    zfile = zipfile.ZipFile(filezip,'w',compression=zipfile.ZIP_DEFLATED)
##    _zipdirectory(zfile, pathzip)
##    zfile.close()
    


class zipdirectory(Thread):
    def __init__(self, parent, journal, filezip, pathzip):
        Thread.__init__(self)
        self.parent = parent
        self.journal = journal
        self.filezip = filezip
        self.pathzip = pathzip
        self.lenpathparent = len(pathzip)+1
        self.Terminated = False
        self.nbreFichiers = 0
        
    def run(self):
        def _zipdirectory(zfile, path):
            for i in glob.glob(path+'/*'):
                if os.path.isdir(i): 
                    if i.endswith("Updates") == False : # On sauvegarde pas le dossier Updates
                        _zipdirectory(zfile, i )
                else:
                    nomFichier = os.path.split(i)[1]
                    if "linux" not in sys.platform :
                        self.journal.WriteText("..." + nomFichier + "\n")
                    zfile.write(i, i[self.lenpathparent:]) 
                    self.nbreFichiers += 1
        
        zfile = zipfile.ZipFile(self.filezip,'w',compression=zipfile.ZIP_DEFLATED)
        _zipdirectory(zfile, self.pathzip)
        zfile.close()
        self.journal.WriteText(str(self.nbreFichiers) + _(u" fichiers ont été sauvegardés avec succès."))
        
        # Lance la suite de l'installation
        self.parent._Installation()
        
    def stop(self):
        self.Terminated = True    
    



class Abort(Exception): 
    pass 

class Download(Thread): 

    def __init__(self, parent, fichierURL, fichierDest, progressBar, zoneTexte): 
        Thread.__init__(self) 
        self.parent = parent
        self.succes = False
        self.fichierURL = fichierURL 
        self.stop = False 
        self.fichierDest = fichierDest
        self.progressBar = progressBar
        self.zoneTexte = zoneTexte
        self.frameParente = self.parent.GetParent()
        #print "Telechargement de la nouvelle version : etape 4"

    def _hook(self, nb_blocs, taille_bloc, taille_fichier):
        #print "Telecharge=", nb_blocs*taille_bloc, _(u"/ total="), taille_fichier
        if nb_blocs*taille_bloc >= taille_fichier:
            #print "Le telechargement est termine !"
            self.succes = True
            self.zoneTexte.SetLabel(_(u"Le téléchargement est terminé. Veuillez patienter..."))
            self.frameParente.SetTitle(_(u"Mises à jour Internet"))
            raise Abort
        if self.stop: 
            raise Abort
        count = int(nb_blocs*taille_bloc)
        self.progressBar.SetValue(count+1)
        #print "Telechargement de la nouvelle version : etape 6"
        if nb_blocs % 5 == 0 :
            if "linux" not in sys.platform :
                texteInfo = _(u"Téléchargement en cours...  ") + FormateTailleFichier(nb_blocs*taille_bloc)+" / "+FormateTailleFichier(taille_fichier)
                if texteInfo != self.zoneTexte.GetLabel() :
                    self.zoneTexte.SetLabel(texteInfo)
                self.frameParente.SetTitle(AffichePourcentage(nb_blocs*taille_bloc, taille_fichier) + _(u" | Téléchargement d'une mise à jour"))

    def run(self): 
        #print "Telechargement de la nouvelle version : etape 5"
        try: 
            if "linux" in sys.platform :
                self.zoneTexte.SetLabel(_(u"Téléchargement en cours..."))
            urlretrieve(self.fichierURL, self.fichierDest, self._hook)
        except Abort as KeyBoardInterrupt: 
            #print 'Aborted ici !' 
            if self.succes == True :
                # Téléchargement réussi
                self.parent.Suite(succes=True)
            else:
                # Téléchargement non complet
                self.parent.Suite(succes=False)
        except: 
            self.stop = True 
            raise 

    def abort(self): 
        self.stop = True
        
        
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE RECHERCHE DE MAJ INTERNET
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_recherche(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_recherche", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Création des widgets
        texteIntro = _(u"Cliquez sur le bouton 'Rechercher' pour lancer la recherche.")
        self.label_introduction = wx.StaticText(self, -1, texteIntro) #FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.gauge = wx.Gauge(self, -1)
        
        # Règlages pour la gauge
        self.count = 0
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
                
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Rechercher"), cheminImage="Images/32x32/Loupe.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1
        if self.count >= 50:
            self.count = 0
        self.gauge.Pulse()
        
    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.gauge, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add((5, 5), 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        self.parent.Fermer()
        
    def Onbouton_ok(self, event):
        self.Recherche()

    def Activation(self):
        if self.parent.afficher_page_recherche == False :
            self.Recherche()
        
    def GetVersionLogiciel(self):
        """ Recherche du numéro de version du logiciel """
        fichierVersion = open(Chemins.GetMainPath("Versions.txt"), "r")
        txtVersion = fichierVersion.readlines()[0]
        fichierVersion.close() 
        pos_debut_numVersion = txtVersion.find("n")
        pos_fin_numVersion = txtVersion.find("(")
        numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
        return numVersion

    def ConvertVersionTuple(self, texteVersion=""):
        """ Convertit un numéro de version texte en tuple """
        tupleTemp = []
        for num in texteVersion.split(".") :
            tupleTemp.append(int(num))
        return tuple(tupleTemp)

    def Recherche(self):
        """ Recherche internet """
        texteIntro = _(u"Recherche d'une mise à jour internet en cours...")
        self.label_introduction.SetLabel(texteIntro)
        
        # Active la gauge
        self.timer.Start(20)
        
        # Recherche si le fichier de versions est présent sur internet
        try :
            if "linux" in sys.platform :
                # Version Debian
                fichierVersions = urlopen('https://raw.githubusercontent.com/Noethys/Noethys/master/noethys/Versions.txt', timeout=10)
            else:
                # Version Windows
                fichierVersions = urlopen('http://www.noethys.com/fichiers/windows/Versions.txt', timeout=10)
            self.texteNouveautes= fichierVersions.read()
            fichierVersions.close()
        except :
            self.Suite(etat="erreur") 
            return

        # Recherche du numéro de version
        if six.PY3:
            self.texteNouveautes = self.texteNouveautes.decode("iso-8859-15")
        pos_debut_numVersion = self.texteNouveautes.find("n")
        pos_fin_numVersion = self.texteNouveautes.find("(")
        self.versionFichier = self.texteNouveautes[pos_debut_numVersion+1:pos_fin_numVersion].strip()
        
        # Si la mise à jour n'est pas nécessaire :
        versionLogiciel = self.ConvertVersionTuple(self.GetVersionLogiciel())
        versionInternet = self.ConvertVersionTuple(self.versionFichier)
        
##        print "versionLogiciel=", versionLogiciel, " | versionInternet=", versionInternet
        if versionInternet <= versionLogiciel and DEBUG == False :
            self.Suite(etat="aucune")
            return

        # Recherche la taille du fichier à télécharger
        taille = int(AffichetailleFichier(self.parent.fichierURL))
        self.tailleFichier = FormateTailleFichier(taille)
        self.parent.tailleFichier = taille
        if self.tailleFichier == 0 :
            self.Suite(etat="erreur")
        
        # Si le fichier est bien trouvé, on passe à la suite...
        self.Suite(etat="trouvee")
        
        
    def Suite(self, etat):
        """ Après la recherche passe à la suite """
        # Recherche terminée
        if etat == "erreur" :
            # Problème de recherche internet
            self.label_introduction.SetLabel(_(u"Connexion au serveur de mise à jour impossible."))
            self.timer.Stop()
            self.Layout()
        if etat == "aucune" :
            # Aucune mise à jour n'a été trouvée
            self.label_introduction.SetLabel(_(u"Vous disposez déjà de la dernière version du logiciel."))
            self.timer.Stop()
            self.bouton_ok.Show(True)
            self.Layout()
        if etat == "trouvee" :
            # Une mise à jour a été trouvée !
            self.parent.versionFichier = self.versionFichier
            self.parent.fichierDest = UTILS_Fichiers.GetRepUpdates(fichier=self.parent.versionFichier)
            if sys.platform.startswith("win") : self.parent.fichierDest = self.parent.fichierDest.replace("/", "\\")
            # Vérifie qu'elle n'a pas déjà été téléchargée sur le disque dur
            fichierAverifier = self.parent.fichierDest+ "/" + self.parent.nomFichier
            if sys.platform.startswith("win") : fichierAverifier = fichierAverifier.replace("/", "\\")
            if os.path.isfile(fichierAverifier) == True :
                tailleFichierAverifier = os.path.getsize(fichierAverifier)  
                tailleFichierOrigin = self.parent.tailleFichier
                if tailleFichierAverifier == tailleFichierOrigin :
                    # Ok le fichier existe bien déjà
                    texteIntro1 = _(u"La mise à jour ") + self.versionFichier + _(u" a déjà été téléchargée précédemment.")
                    self.parent.GetPage("page_fin_telechargement").label_introduction1.SetLabel(texteIntro1)
                    self.parent.Active_page("page_fin_telechargement")
            else:
                # Sinon, on la télécharge...
                texteIntro1 = _(u"La version ") + self.versionFichier + " de Noethys est disponible (" + self.tailleFichier + ")."
                self.parent.GetPage("page_disponible").label_introduction1.SetLabel(texteIntro1)
                texteNouveautes = self.texteNouveautes
                if six.PY2:
                    texteNouveautes = texteNouveautes.decode("iso-8859-15")
                self.parent.GetPage("page_disponible").textCtrl_nouveautes.SetValue(texteNouveautes)
                self.parent.Active_page("page_disponible")
              

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE MAJ DISPONIBLE
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_disponible(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_disponible", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Création des widgets
        texteIntro1 = ""
        self.label_introduction1 = wx.StaticText(self, -1, texteIntro1) # FonctionsPerso.StaticWrapText(self, -1, texteIntro1)
        texteIntro2 = _(u"Souhaitez-vous la télécharger maintenant ?")
        self.label_introduction2 = wx.StaticText(self, -1, texteIntro2) # FonctionsPerso.StaticWrapText(self, -1, texteIntro2)
        self.textCtrl_nouveautes = wx.TextCtrl(self, -1,"", size=(-1, 50), style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Télécharger"), cheminImage="Images/32x32/Telecharger.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.label_introduction2, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.textCtrl_nouveautes, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        self.grid_sizer_base = grid_sizer_base
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        # Fermeture
        #print "annuler"
        self.parent.Fermer()
        
    def Onbouton_ok(self, event):
        # Télécharger
        self.parent.Active_page("page_telechargement")

    def Activation(self):
        # Pour contrer bug de Layout
        self.SetSize((500, 700))
        
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE TELECHARGEMENT
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_telechargement(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_telechargement", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Création des widgets
        texteIntro = _(u"Le téléchargement va commencer dans quelques instants...")
        self.label_introduction = wx.StaticText(self, -1, texteIntro) # FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.gauge = wx.Gauge(self, -1)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Télécharger"), cheminImage="Images/32x32/Telecharger.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_ok.Show(False)
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer le téléchargement")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.gauge, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add((5, 5), 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        self.Arreter_telechargement()
        
    def Onbouton_ok(self, event):
        self.Lancer_telechargement()

    def Activation(self):
        # Crée une petite attente avant le début du téléchargement
        self.count = 0
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(1)

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1
        if self.count == 10 :
            self.timer.Stop()
            # Lance le téléchargement
            #print "Telechargement de la nouvelle version : etape 1"
            self.Lancer_telechargement()
            
    def Suite(self, succes):
        """ Après le téléchargement passe à la suite """
        # Vérifie que le fichier est bien entier :
        tailleFichierDest = os.path.getsize(self.parent.fichierDest+ "/" + self.parent.nomFichier)  
        tailleFichierOrigin = self.parent.tailleFichier
        if tailleFichierDest != tailleFichierOrigin :
            succes = False
        
        # Téléchargement terminé
        if succes == True :
            # On attribue un ID unique qui permet de compter les téléchargements
            IDfichier = FonctionsPerso.GetIDfichier()
            if len(IDfichier) > 7 :
                id = IDfichier[-7:]
            else :
                id = ""
            # On envoie le signal pour le compteur de téléchargement
            if "linux" in sys.platform :
                typeFichier = "linux"
            else:
                typeFichier = "windows"
            try :
                versionFichier = self.parent.versionFichier
                fichier = "%s-%s-%s" % (typeFichier, versionFichier, id)
                req = Request("http://www.noethys.com/fichiers/telechargement.cgi?fichier=%s" % fichier)
                handle = urlopen(req)
            except :
                pass
            # Si téléchargement complet, on passe à la page de fin de téléchargement
            sleep(1) # Attend 2 secondes avant de continuer
            self.parent.Active_page("page_fin_telechargement")
        else:
            # Vidage du rep Updates
            FonctionsPerso.VideRepertoireUpdates(forcer=True)
            # Le téléchargement n'est pas complet, demande à l'utilisateur de recommencer
            self.label_introduction.SetLabel(_(u"Le téléchargement n'est pas complet. Voulez-vous recommencer ?"))
            self.bouton_ok.Show(True)
            self.Layout()
        
    def Lancer_telechargement(self):
        """ Lance le thread de téléchargement """
        #print "Telechargement de la nouvelle version : etape 2"
        # Création du répertoire de destination
        if os.path.isdir(self.parent.fichierDest) == False :
            os.mkdir(self.parent.fichierDest)
        # Téléchargement
        max = int(AffichetailleFichier(self.parent.fichierURL))
        self.gauge.SetRange(max)
        self.downloader = Download(self, self.parent.fichierURL, self.parent.fichierDest + "/" + self.parent.nomFichier, self.gauge, self.label_introduction) 
        self.downloader.start()
        #print "Telechargement de la nouvelle version : etape 3"
        self.bouton_ok.Show(False)
        

    def Arreter_telechargement(self):
        """ Arrete le téléchargement """
        # On vérifie si le thread n'a jamais été lancé avant :
        try:
            downloadEnCours = self.downloader.isAlive()
        except AttributeError :
            downloadEnCours = False

        if downloadEnCours:
            # Demande la confirmation de l'arrêt
            dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment arrêter le téléchargement ?"), _(u"Confirmation d'arrêt"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
            # Si le téléchargement est en cours, on le stoppe :
            self.downloader.abort()
            self.label_introduction.SetLabel(_(u"Vous avez interrompu le téléchargement."))
            self.bouton_ok.Show(True)

            # Pour le debug, passe à la page suivante
            if DEBUG :
                self.parent.Active_page("page_fin_telechargement")
                return

        else:
            # Si le téléchargement n'est pas en cours, on ferme la fenêtre
            self.parent.Fermer()




# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE FIN TELECHARGEMENT
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_fin_telechargement(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_fin_telechargement", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Création des widgets
        texteIntro1 = _(u"La mise à jour a été téléchargée avec succès.")
        self.label_introduction1 = wx.StaticText(self, -1, texteIntro1) # FonctionsPerso.StaticWrapText(self, -1, texteIntro1)
        texteIntro2 = _(u"Souhaitez-vous l'installer maintenant ?")
        self.label_introduction2 = wx.StaticText(self, -1, texteIntro2) # FonctionsPerso.StaticWrapText(self, -1, texteIntro2)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Installer"), cheminImage="Images/32x32/Installation.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.label_introduction2, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add((5, 5), 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        # Fermeture
        #print "annuler"
        self.parent.Fermer()
        
    def Onbouton_ok(self, event):
        # Téléchargement terminée avec succès
        self.parent.Active_page("page_installation")

    def Activation(self):
        self.SetSize((500, 600))
        #self.SendSizeEvent()
        self.Refresh()
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE INSTALLATION
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_installation(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_installation", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Création des widgets
        texteIntro = _(u"Installation de la mise à jour en cours...")
        self.label_introduction = wx.StaticText(self, -1, texteIntro) # FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.journal = wx.TextCtrl(self, -1,"", size=(-1, 10), style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Installer"), cheminImage="Images/32x32/Installation.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.journal, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        # Fermeture
        pass
        
    def Onbouton_ok(self, event):
        # Fermeture
        print("ok")

    def Activation(self):
        # Pour contrer bug de Layout
        self.SetSize((500, 700))
        self.Refresh()
        self.Installation()
    
    def Installation(self):
        """ Procédure d'installation """
        # Sauvegarde globale du répertoire teamWorks
        self.bouton_ok.Enable(False)
        self.bouton_annuler.Enable(False)
        
        # Lancement de la sauvegarde
        #self._Sauvegarde()

        wx.CallLater(5, self._Installation)
        
    def _Sauvegarde(self):
        """ Procédure de sauvegarde globale du répertoire """
        self.label_introduction.SetLabel(_(u"Sauvegarde des données locales en cours..."))
        if "linux" not in sys.platform :
            self.journal.WriteText(_(u"> Sauvegarde des données locales :\n\n"))
        
        fichierDest = self.parent.fichierDest + "/global_save.zip"
        if sys.platform.startswith("win") : fichierDest = fichierDest.replace("/", "\\")
        repApplication = os.getcwd()
        
        save = zipdirectory(self, self.journal, fichierDest, repApplication + "/Data")
        save.start()
        
    def _Installation(self):
        """ Procédure d'installation """
        self.label_introduction.SetLabel(_(u"Chargement de l'installeur..."))
        self.journal.WriteText(_(u"Installeur en cours de chargement. Veuillez patienter..."))

        sleep(1)

        # Lancement de l'installeur
        fichierMAJ = self.parent.fichierDest + "/" + self.parent.nomFichier
        if "linux" in sys.platform :
            dirTemp = UTILS_Fichiers.GetRepTemp()
            self.journal.WriteText(_(u"\n\nExtraction des fichiers. Veuillez patienter..."))
            os.system("unzip -d " + dirTemp + " " + fichierMAJ)
            self.journal.WriteText(_(u"\n\nCopie des fichiers. Veuillez patienter..."))
            os.system("cp -a " + dirTemp +"/Noethys-master/noethys/* .")
            self.journal.WriteText(_(u"\n\nEffacement fichiers temporaires. Veuillez patienter..."))
            os.system("rm -rf " + dirTemp +"/Noethys-master")
        else :
            try :
                FonctionsPerso.LanceFichierExterne(fichierMAJ)
            except :
                self.journal.WriteText(_(u"\nErreur : Impossible d'ouvrir l'installeur."))
                dlg = wx.MessageDialog(self, _(u"Noethys n'a pas réussi à ouvrir l'installeur.\n\nCe blocage peut peut-être venir de votre antivirus. Essayez éventuellement de le désactiver le temps de l'installation de la mise à jour."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Fermeture de Noethys
        try :
            topWindow = wx.GetApp().GetTopWindow()
            nomWindow = topWindow.GetName()
        except :
            nomWindow = None
        if nomWindow == "general" : 
            # Si la frame 'General' est chargée, on sauvegarde et on ferme le logiciel
            self.parent.installation = True
        # Fermeture de la dlg
        sleep(2)
        self.parent.Fermer()

        
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Updater", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.installation = False
        
        intro = _(u"Vous pouvez ici télécharger et installer une mise à jour pour Noethys. Ces mises à jour vous permettent bien-sûr de gagner en stabilité et en fonctionnalités.")
        titre = _(u"Mise à jour du logiciel")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Telecharger.png")
        
        self.page_active = ""
        
        # Changer ci-dessous pour ne pas afficher la page de recherche (1ere page)
        self.afficher_page_recherche = True 

        # Vider répertoire Updates
        FonctionsPerso.VideRepertoireUpdates(forcer=True)

        # Met en pause le serveur Connecthys si besoin
        try :
            self.parent.ctrl_serveur_portail.PauseServeur()
        except:
            pass

        # Fichiers
        if "linux" in sys.platform :
            # Version Debian
            self.nomFichier = "master.zip"
            self.fichierURL = "https://github.com/Noethys/Noethys/archive/" + self.nomFichier
        else:
            # Version Windows
            self.nomFichier = "Noethys.exe"
            self.fichierURL = "http://www.noethys.com/fichiers/windows/" + self.nomFichier
            
        self.fichierDest = ""
        self.tailleFichier = 0
        self.versionFichier = ""
        
        # Création du sizer
        self.sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        self.sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        self.sizer_base.AddGrowableCol(0)
        
        # Création des pages dans le sizer
        self.dictPages = {}
        self.Creation_page("page_recherche", Page_recherche)
        self.Creation_page("page_disponible", Page_disponible)
        self.Creation_page("page_telechargement", Page_telechargement)
        self.Creation_page("page_fin_telechargement", Page_fin_telechargement)
        self.Creation_page("page_installation", Page_installation)

        self.sizer_base.AddGrowableRow(1)
        self.sizer_base.AddGrowableRow(2)
        self.sizer_base.AddGrowableRow(3)
        self.sizer_base.AddGrowableRow(4)
        self.sizer_base.AddGrowableRow(5)
        
        # Chois de la page ouverte au démarrage
        self.Active_page("page_recherche")
        
        # Finalisation du sizer
        self.SetSizer(self.sizer_base)
        self.Layout()
        
        self.SetMinSize((600, 500))
        self.SetSize((600, 500))
        self.CentreOnScreen()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def GetEtat(self):
        return self.installation
    
    def Creation_page(self, nomPage="", classe=None):
        """ Création d'une page """
        page = classe(self)
        self.sizer_base.Add(page, 1, wx.EXPAND, 0)
        page.Show(False)
        self.dictPages[nomPage] = page

    def GetPage(self, nomPage=""):
        return self.dictPages[nomPage]

    def Active_page(self, choixPage=""):
        """ Active une page choisie """
        # Faire disparaître la page actuelle
        if self.page_active != "" :
            self.dictPages[self.page_active].Show(False)
        # Faire apparaître et active la page choisie
        if choixPage != "" :
            self.page_active = choixPage
            self.dictPages[self.page_active].Show(True)
            self.dictPages[self.page_active].Activation()
            self.Layout()
    
    def Aide(self):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Rechercherunemisejourdulogiciel")

    def SurFermeture(self):
        # Relance serveur Connecthys si besoin
        if self.GetEtat() == False :
            try :
                self.parent.ctrl_serveur_portail.RepriseServeur()
            except:
                pass

    def Fermer(self):
        self.SurFermeture()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnClose(self, event):
        self.SurFermeture()

        if self.page_active == "page_telechargement" :
            self.GetPage("page_telechargement").Arreter_telechargement()
        elif self.page_active == "page_installation" :
            pass
        else:
            self.Fermer()


               
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    DEBUG = True
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
