#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import sys
import wx
import platform
import os
import datetime
import traceback
from time import sleep 

import UTILS_Linux
if "linux" in sys.platform :
    UTILS_Linux.AdaptationsDemarrage()

import time
HEUREDEBUT = time.time()

import UTILS_Config
import UTILS_Historique
import UTILS_Sauvegarde_auto
import UTILS_Rapport_bugs
import UTILS_Utilisateurs

import GestionDB

import UTILS_Parametres

import FonctionsPerso
import CTRL_Accueil
import CTRL_Messages
import CTRL_Identification
import CTRL_Numfacture
import CTRL_Recherche_individus
import CTRL_Ephemeride
##import CTRL_Meteo
import DLG_Remplissage
import DLG_Message_html
import DLG_Enregistrement
import CTRL_Toaster

import shelve
import dbhash
import anydbm
import random
import urllib
import urllib2

import wx.lib.agw.aui as aui
import wx.lib.agw.advancedsplash as AS
import wx.lib.agw.toasterbox as Toaster
import wx.lib.agw.pybusyinfo as PBI



if os.path.isfile("nologin.txt") :
    fichier = open("nologin.txt", "r")
    PASS = fichier.readline()
    fichier.close() 
else :
    PASS = None
    

# Constantes générales
VERSION_APPLICATION = FonctionsPerso.GetVersionLogiciel()
NOM_APPLICATION = u"Noethys"

# ID pour la barre des menus
ID_ASSISTANT_DEMARRAGE = wx.NewId()
ID_NOUVEAU_FICHIER = wx.NewId()
ID_OUVRIR_FICHIER = wx.NewId()
ID_FERMER_FICHIER = wx.NewId()
ID_FICHIER_INFORMATIONS = wx.NewId()
ID_CREER_SAUVEGARDE = wx.NewId()
ID_RESTAURER_SAUVEGARDE = wx.NewId()
ID_SAUVEGARDES_AUTO = wx.NewId()
ID_CONVERSION_RESEAU = wx.NewId()
ID_CONVERSION_LOCAL = wx.NewId()
ID_QUITTER = wx.NewId()
ID_DERNIER_FICHIER = 700

ID_PARAM_MENU_FACTURATION = wx.NewId()
ID_PARAM_MENU_REGLEMENTS = wx.NewId()
ID_PARAM_MENU_PRELEVEMENTS = wx.NewId()
ID_PARAM_MENU_RENSEIGNEMENTS = wx.NewId()
ID_PARAM_MENU_SCOLAIRE = wx.NewId()
ID_PARAM_MENU_TRANSPORTS = wx.NewId()

ID_PARAM_MENU_TRANSPORTS_BUS = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_CAR = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_NAVETTE = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_TAXI = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_TRAIN = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_AVION = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_BATEAU = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_METRO = wx.NewId()
ID_PARAM_MENU_TRANSPORTS_PEDIBUS = wx.NewId()

ID_PARAM_PREFERENCES = wx.NewId()
ID_PARAM_ENREGISTREMENT = wx.NewId()
ID_PARAM_UTILISATEURS = wx.NewId()
ID_PARAM_MODELES_DROITS = wx.NewId()
ID_PARAM_UTILISATEURS_RESEAU = wx.NewId()
ID_PARAM_ORGANISATEUR = wx.NewId()
ID_PARAM_ACTIVITES = wx.NewId()
ID_PARAM_DOCUMENTS = wx.NewId()
ID_PARAM_MODELES_EMAILS = wx.NewId()
ID_PARAM_MODELES_TICKETS = wx.NewId()
ID_PARAM_BADGEAGE = wx.NewId()
ID_PARAM_VOCAL = wx.NewId()
ID_PARAM_PIECES = wx.NewId()
ID_PARAM_CATEGORIES_TRAVAIL = wx.NewId()
ID_PARAM_MALADIES = wx.NewId()
ID_PARAM_VACCINS = wx.NewId()
ID_PARAM_MEDECINS = wx.NewId()
ID_PARAM_RESTAURATEURS = wx.NewId()
ID_PARAM_MODES_REGLEMENTS = wx.NewId()
ID_PARAM_EMETTEURS = wx.NewId()
ID_PARAM_COMPTES = wx.NewId()
ID_PARAM_BANQUES = wx.NewId()
ID_PARAM_LOTS_FACTURES = wx.NewId()
ID_PARAM_LOTS_RAPPELS = wx.NewId()
ID_PARAM_REGIMES = wx.NewId()
ID_PARAM_CAISSES = wx.NewId()
ID_PARAM_MODELES_AIDES = wx.NewId()
ID_PARAM_TYPES_COTISATIONS = wx.NewId()
ID_PARAM_GROUPES_ACTIVITES = wx.NewId()
ID_PARAM_SECTEURS = wx.NewId()
ID_PARAM_VILLES = wx.NewId()
ID_PARAM_TYPES_SIESTE = wx.NewId()
ID_PARAM_CATEGORIES_MESSAGES = wx.NewId()
ID_PARAM_EMAILS_EXP = wx.NewId()
ID_PARAM_LISTE_DIFFUSION = wx.NewId()
ID_PARAM_QUESTIONNAIRES = wx.NewId()
ID_PARAM_NIVEAUX_SCOLAIRES = wx.NewId()
ID_PARAM_ECOLES = wx.NewId()
ID_PARAM_CLASSES = wx.NewId()

ID_PARAM_COMPAGNIES_BUS = wx.NewId()
ID_PARAM_COMPAGNIES_CAR = wx.NewId()
ID_PARAM_COMPAGNIES_NAVETTE = wx.NewId()
ID_PARAM_COMPAGNIES_TAXI = wx.NewId()
ID_PARAM_COMPAGNIES_AVION = wx.NewId()
ID_PARAM_COMPAGNIES_BATEAU = wx.NewId()
ID_PARAM_COMPAGNIES_TRAIN = wx.NewId()
ID_PARAM_COMPAGNIES_METRO = wx.NewId()

ID_PARAM_LIEUX_GARES = wx.NewId()
ID_PARAM_LIEUX_AEROPORTS = wx.NewId()
ID_PARAM_LIEUX_PORTS = wx.NewId()
ID_PARAM_LIEUX_STATIONS = wx.NewId()

ID_PARAM_LIGNES_BUS = wx.NewId()
ID_PARAM_LIGNES_CAR = wx.NewId()
ID_PARAM_LIGNES_NAVETTE = wx.NewId()
ID_PARAM_LIGNES_BATEAU = wx.NewId()
ID_PARAM_LIGNES_METRO = wx.NewId()
ID_PARAM_LIGNES_PEDIBUS = wx.NewId()

ID_PARAM_ARRETS_BUS = wx.NewId()
ID_PARAM_ARRETS_CAR = wx.NewId()
ID_PARAM_ARRETS_NAVETTE = wx.NewId()
ID_PARAM_ARRETS_BATEAU = wx.NewId()
ID_PARAM_ARRETS_METRO = wx.NewId()
ID_PARAM_ARRETS_PEDIBUS = wx.NewId()

ID_PARAM_VACANCES = wx.NewId()
ID_PARAM_FERIES = wx.NewId()
ID_PARAM_MENU_CALENDRIER = wx.NewId()

ID_AFFICHAGE_PERSPECTIVE_DEFAUT = wx.NewId()
ID_PREMIERE_PERSPECTIVE = 500
ID_AFFICHAGE_PERSPECTIVE_SAVE = wx.NewId()
ID_AFFICHAGE_PERSPECTIVE_SUPPR = wx.NewId()
ID_AFFICHAGE_PANNEAUX = 600
ID_AFFICHAGE_ACTUALISER = wx.NewId()

ID_INDIVIDUS_SCOLARITE = wx.NewId()
ID_INDIVIDUS_INSCRIPTIONS = wx.NewId()
ID_INDIVIDUS_INDIVIDUS = wx.NewId()
ID_INDIVIDUS_FAMILLES = wx.NewId()
ID_INDIVIDUS_TRANSPORTS = wx.NewId()
ID_INDIVIDUS_TRANSPORTS_RECAP = wx.NewId()
ID_INDIVIDUS_TRANSPORTS_DETAIL = wx.NewId()
ID_INDIVIDUS_ANNIVERSAIRES = wx.NewId()
ID_INDIVIDUS_INFOS_MED = wx.NewId()
ID_INDIVIDUS_PIECES_FOURNIES = wx.NewId()
ID_INDIVIDUS_PIECES_MANQUANTES = wx.NewId()
ID_INDIVIDUS_REGIMES_CAISSES = wx.NewId()
ID_INDIVIDUS_QUOTIENTS = wx.NewId()
ID_INDIVIDUS_MANDATS = wx.NewId()
ID_INDIVIDUS_IMPORTER_PHOTOS = wx.NewId()
ID_INDIVIDUS_IMPORTER = wx.NewId()
ID_INDIVIDUS_IMPORTER_CSV = wx.NewId()
ID_INDIVIDUS_IMPORTER_FICHIER = wx.NewId()
ID_INDIVIDUS_EDITION_ETIQUETTES = wx.NewId()

ID_OUTILS_STATS = wx.NewId()
ID_OUTILS_VILLES = wx.NewId()
ID_OUTILS_CALCULATRICE = wx.NewId()
ID_OUTILS_CALENDRIER = wx.NewId()
ID_OUTILS_ENVOI_EMAILS = wx.NewId()
ID_OUTILS_METEO = wx.NewId()
ID_OUTILS_GPS = wx.NewId()
ID_OUTILS_HORAIRES_SOLEIL = wx.NewId()
ID_OUTILS_CONNEXIONS = wx.NewId()
ID_OUTILS_MESSAGES = wx.NewId()
ID_OUTILS_HISTORIQUE = wx.NewId()
ID_OUTILS_UTILITAIRES = wx.NewId()
ID_OUTILS_CORRECTEUR = wx.NewId()
ID_OUTILS_PURGER_HISTORIQUE = wx.NewId()
ID_OUTILS_PURGER_JOURNAL_BADGEAGE = wx.NewId()
ID_OUTILS_PURGER_ARCHIVES_BADGEAGE = wx.NewId()
ID_OUTILS_PURGER_REP_UPDATES = wx.NewId()
ID_OUTILS_UPDATER = wx.NewId()
ID_OUTILS_PROCEDURES = wx.NewId()
ID_OUTILS_PROCEDURE_E4072 = wx.NewId()
ID_OUTILS_EXTENSIONS = wx.NewId()
ID_OUTILS_REINITIALISATION = wx.NewId()
ID_OUTILS_TRANSFERT_TABLES = wx.NewId()
ID_OUTILS_CONSO_SANS_PRESTATIONS = wx.NewId()
ID_OUTILS_PRESTATIONS_SANS_CONSO = wx.NewId()
ID_OUTILS_DEVERROUILLAGE_FORFAITS = wx.NewId()
ID_OUTILS_CONSOLE_PYTHON = wx.NewId()
ID_OUTILS_CONSOLE_SQL = wx.NewId()
ID_OUTILS_LISTE_PERSO = wx.NewId()
ID_OUTILS_APPLIQUER_TVA = wx.NewId()
ID_OUTILS_APPLIQUER_CODE_COMPTABLE = wx.NewId()
ID_OUTILS_CONVERSION_RIB_SEPA = wx.NewId()
ID_OUTILS_CREATION_TITULAIRES_HELIOS = wx.NewId()

ID_REGLEMENTS_REGLER_FACTURE = wx.NewId()
ID_REGLEMENTS_RECUS = wx.NewId()
ID_REGLEMENTS_LISTE = wx.NewId()
ID_REGLEMENTS_VENTILATION = wx.NewId()
ID_REGLEMENTS_ANALYSE_VENTILATION = wx.NewId()
ID_REGLEMENTS_SYNTHESE_MODES = wx.NewId()
ID_REGLEMENTS_PRELEVEMENT = wx.NewId()
ID_REGLEMENTS_DEPOTS = wx.NewId()

ID_FACTURATION_VENTILATION = wx.NewId()
ID_FACTURATION_MENU_FACTURES = wx.NewId()
ID_FACTURATION_FACTURES_GENERATION = wx.NewId()
ID_FACTURATION_FACTURES_LISTE = wx.NewId()
ID_FACTURATION_FACTURES_PRELEVEMENT = wx.NewId()
ID_FACTURATION_FACTURES_HELIOS = wx.NewId()
ID_FACTURATION_FACTURES_EMAIL = wx.NewId()
ID_FACTURATION_FACTURES_IMPRIMER = wx.NewId()
ID_FACTURATION_MENU_RAPPELS= wx.NewId()
ID_FACTURATION_RAPPELS_GENERATION = wx.NewId()
ID_FACTURATION_RAPPELS_EMAIL = wx.NewId()
ID_FACTURATION_RAPPELS_IMPRIMER = wx.NewId()
ID_FACTURATION_RAPPELS_LISTE = wx.NewId()
ID_FACTURATION_MENU_ATTESTATIONS = wx.NewId()
ID_FACTURATION_ATTESTATIONS_GENERATION = wx.NewId()
ID_FACTURATION_ATTESTATIONS_LISTE = wx.NewId()
ID_FACTURATION_MENU_ATTESTATIONS_FISCALES = wx.NewId()
ID_FACTURATION_ATTESTATIONS_FISCALES_GENERATION = wx.NewId()
ID_FACTURATION_LISTE_DEDUCTIONS = wx.NewId()
ID_FACTURATION_LISTE_PRESTATIONS = wx.NewId()
ID_FACTURATION_SOLDES = wx.NewId()
ID_FACTURATION_SOLDES_INDIVIDUELS = wx.NewId()
ID_FACTURATION_SOLDER_IMPAYES = wx.NewId()
ID_FACTURATION_PRESTATIONS_VILLES = wx.NewId()
ID_FACTURATION_SYNTHESE_PRESTATIONS = wx.NewId()
ID_FACTURATION_SYNTHESE_IMPAYES = wx.NewId()
ID_FACTURATION_EXPORT_COMPTA = wx.NewId()

ID_COTISATIONS_LISTE = wx.NewId()
ID_COTISATIONS_MANQUANTES = wx.NewId()
ID_COTISATIONS_DEPOTS = wx.NewId()
ID_COTISATIONS_EMAIL = wx.NewId()
ID_COTISATIONS_IMPRIMER = wx.NewId()

ID_IMPRIM_LISTE_CONSO_JOURN = wx.NewId()
ID_CONSO_GESTIONNAIRE = wx.NewId()
ID_CONSO_ATTENTE = wx.NewId()
ID_CONSO_REFUS = wx.NewId()
ID_CONSO_ABSENCES = wx.NewId()
ID_CONSO_SYNTHESE_CONSO = wx.NewId()
ID_CONSO_ETAT_GLOBAL = wx.NewId()
ID_CONSO_ETAT_NOMINATIF = wx.NewId()
ID_CONSO_BADGEAGE = wx.NewId()

ID_AIDE_AIDE = wx.NewId()
ID_AIDE_ACHETER_LICENCE = wx.NewId()
ID_AIDE_GUIDE_DEMARRAGE = wx.NewId()
ID_AIDE_FORUM = wx.NewId()
ID_AIDE_VIDEOS = wx.NewId()
ID_AIDE_TELECHARGEMENTS = wx.NewId()
ID_AIDE_AUTEUR = wx.NewId()

ID_PROPOS_VERSIONS = wx.NewId()
ID_PROPOS_LICENCE = wx.NewId()
ID_PROPOS_SOUTENIR = wx.NewId()
ID_PROPOS_PROPOS = wx.NewId()

ID_OUTILS_UPDATER_2 = wx.NewId()

# ID pour la barre d'outils
ID_TB_GESTIONNAIRE = wx.NewId()
ID_TB_LISTE_CONSO = wx.NewId()
ID_TB_BADGEAGE = wx.NewId()
ID_TB_REGLER_FACTURE = wx.NewId()
ID_TB_CALCULATRICE = wx.NewId()
ID_TB_UTILISATEUR = wx.NewId()



class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title=u"Noethys", name="general", style=wx.DEFAULT_FRAME_STYLE)
        
##        # Dates en francais
##        wx.Locale(wx.LANGUAGE_FRENCH)
##        try : locale.setlocale(locale.LC_ALL, 'FR')
##        except : pass
        
        # Icône
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        # Ecrit la date et l'heure dans le journal.log
        dateDuJour = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        systeme = u"%s %s %s %s" % (sys.platform, platform.system(), platform.release(), platform.machine())
        print "------------ %s | %s | %s ------------" % (dateDuJour, VERSION_APPLICATION, systeme)
        
        # Diminution de la taille de la police sous linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
    
    def Initialisation(self):
        # Vérifie que le fichier de configuration existe bien
        self.nomFichierConfig = "Data/Config.dat"
        test = os.path.isfile(self.nomFichierConfig) 
        if test == False :
            # Création du fichier de configuration
            cfg = UTILS_Config.FichierConfig(nomFichier=self.nomFichierConfig)
            cfg.SetDictConfig(dictConfig={ 
                "nomFichier" : "", 
                "derniersFichiers" : [], 
                "taille_fenetre" : (0, 0),
                "dict_selection_periodes_activites" : {
                        'listeActivites': [], 
                        'listeSelections': (), 
                        'listePeriodes': [], 
                        'modeAffichage': 'nbrePlacesPrises', 
                        'dateDebut': None, 
                        'dateFin': None, 
                        'annee': 2011, 
                        'page': 0,
                        },
                "assistant_demarrage" : False,
                "perspectives" : [],
                "perspective_active" : None,
                "annonce" : None,
                 },)
            self.nouveauFichierConfig = True
        else:
            self.nouveauFichierConfig = False

        # Récupération des fichiers de configuration
        self.userConfig = self.GetFichierConfig(nomFichier=self.nomFichierConfig) # Fichier de config de l'utilisateur
        
        # Gestion des utilisateurs
        self.listeUtilisateurs = [] 
        self.dictUtilisateur = None

        # Récupération du nom du dernier fichier chargé
        self.nomDernierFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = ""
        
        if self.userConfig.has_key("assistant_demarrage") :
            if self.userConfig["assistant_demarrage"] == True :
                self.afficherAssistant = False
            else: self.afficherAssistant = True
        else:
            self.afficherAssistant = True

        # Recherche si une mise à jour internet existe
        self.versionMAJ = None
        if sys.executable.endswith("python.exe") == True :
            self.MAJexiste = False
        else:
            self.MAJexiste = self.RechercheMAJinternet()
        
        if UTILS_Config.GetParametre("propose_maj", defaut=True) == False :
            self.MAJexiste = False

        # Récupération des perspectives de la page d'accueil
        if self.userConfig.has_key("perspectives") == True :
            self.perspectives = self.userConfig["perspectives"]
        else:
            self.perspectives = []
        if self.userConfig.has_key("perspective_active") == True :
            self.perspective_active = self.userConfig["perspective_active"]
        else:
            self.perspective_active = None

        # Affiche le titre du fichier en haut de la frame
        self.SetTitleFrame(nomFichier="")
        
        # Création du AUI de la fenêtre 
        self._mgr = aui.AuiManager()
##        self._mgr.SetArtProvider(aui.ModernDockArt(self))
        self._mgr.SetManagedWindow(self)

        # Barre des tâches
        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText(u"Bienvenue dans %s..." % NOM_APPLICATION)
        
        # Création de la barre des menus
        self.CreationBarreMenus()
        
        # Création de la barre d'outils
        self.CreationBarreOutils() 
        
        # Création des panneaux
        self.CreationPanneaux()
        
        # Création des Binds
        self.CreationBinds()
        
        # Détermine la taille de la fenêtre
        self.SetMinSize((935, 740))
        if self.userConfig.has_key("taille_fenetre") == False :
            self.userConfig["taille_fenetre"] = (0, 0)
        taille_fenetre = self.userConfig["taille_fenetre"]
        if taille_fenetre == (0, 0) :
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.CenterOnScreen()
        
        # Désactive les items de la barre de menus
        self.ActiveBarreMenus(False) 
        
        # Binds
        self.Bind(wx.EVT_CLOSE, self.OnClose)
##        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Affiche un Toaster quand une mise à jour du logiciel est disponible
        if self.MAJexiste == True :
            texteToaster = u"Une nouvelle version de Noethys est disponible !"
            self.AfficheToaster(titre=u"Mise à jour", texte=texteToaster, couleurFond="#81A8F0") 
            

    def SetTitleFrame(self, nomFichier=""):
        if "[RESEAU]" in nomFichier :
            port, hote, user, mdp = nomFichier.split(";")
            nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
            nomFichier = u"Fichier réseau : %s | %s" % (nomFichier, user)
        if nomFichier != "" :
            nomFichier = " - [" + nomFichier + "]"
        titreFrame = NOM_APPLICATION + " v" + VERSION_APPLICATION + nomFichier
        self.SetTitle(titreFrame)

    def GetFichierConfig(self, nomFichier=""):
        """ Récupère le dictionnaire du fichier de config """
        cfg = UTILS_Config.FichierConfig(nomFichier)
        return cfg.GetDictConfig()

    def SaveFichierConfig(self, nomFichier):
        """ Sauvegarde le dictionnaire du fichier de config """
        cfg = UTILS_Config.FichierConfig(nomFichier)
        cfg.SetDictConfig(dictConfig=self.userConfig )
    
    def OnSize(self, event):
        self.SetTitle(str(self.GetSize()))
        
    def OnClose(self, event):
        if self.Quitter() == False :
            return
        event.Skip()
        
    def Quitter(self, videRepertoiresTemp=True, sauvegardeAuto=True):
        """ Fin de l'application """
        
        # Mémorise l'action dans l'historique
        if self.userConfig["nomFichier"] != "" :
            try :
                UTILS_Historique.InsertActions([{
                    "IDcategorie" : 1, 
                    "action" : u"Fermeture du fichier",
                    },])
            except :
                pass
                
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        self.userConfig["taille_fenetre"] = taille_fenetre
        
        # Mémorisation des perspectives
        self.SauvegardePerspectiveActive() 
        self.userConfig["perspectives"] = self.perspectives
        self.userConfig["perspective_active"] = self.perspective_active
        
        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)

        # Sauvegarde automatique
        if self.userConfig["nomFichier"] != "" and sauvegardeAuto == True :
            resultat = self.SauvegardeAutomatique() 
            if resultat == wx.ID_CANCEL :
                return False

        # Vidage des répertoires Temp
        if videRepertoiresTemp == True :
            FonctionsPerso.VideRepertoireTemp()
            FonctionsPerso.VideRepertoireUpdates()
        
        return True
    
    def SauvegardeAutomatique(self):
        save = UTILS_Sauvegarde_auto.Sauvegarde_auto(self)
        resultat = save.Start() 
        return resultat
        
    def ChargeFichierExemple(self):
        """ Demande à l'utilisateur s'il souhaite charger le fichier Exemple """
        if self.nouveauFichierConfig == True :
            import DLG_Bienvenue
            dlg = DLG_Bienvenue.Dialog(self)
            if dlg.ShowModal() == wx.ID_OK :
                nomFichier = dlg.GetNomFichier()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return
            
            # Charge le fichier Exemple sélectionné
            self.nomDernierFichier = nomFichier
                
            import calendar
            annee = datetime.date.today().year
            numMois = datetime.date.today().month
            listeSelections = []
            listePeriodes = []
            for index in range(0, 3) :
                nbreJoursMois = calendar.monthrange(annee, numMois)[1]
                date_debut = datetime.date(annee, numMois, 1)
                date_fin = datetime.date(annee, numMois, nbreJoursMois)
                listeSelections.append(numMois - 1)
                listePeriodes.append((date_debut, date_fin))
                numMois += 1
                if numMois > 12 :
                    numMois = 1
        
            donnees = {
                    'listeActivites': [1,], 
                    'listeSelections': listeSelections, 
                    'listePeriodes': listePeriodes, 
                    'modeAffichage': 'nbrePlacesPrises', 
                    'dateDebut': None, 
                    'dateFin': None, 
                    'annee': annee, 
                    'page': 0,
                    }
            
            self.ctrl_remplissage.SetDictDonnees(donnees)
            return True
        return False
    
    def CreationPanneaux(self):
        # Panneau Rechercher un individu
        self.ctrl_individus = CTRL_Recherche_individus.Panel(self)
        self._mgr.AddPane(self.ctrl_individus, aui.AuiPaneInfo().Name("recherche").Caption(u"Individus").
                          CenterPane().PaneBorder(True).CaptionVisible(True) )

        # Panneau Ephéméride
        self.ctrl_ephemeride = CTRL_Ephemeride.CTRL(self)
        self._mgr.AddPane(self.ctrl_ephemeride, aui.AuiPaneInfo().Name("ephemeride").Caption(u"Ephéméride").
                          Top().Layer(0).Row(1).Position(0).CloseButton(True).MaximizeButton(True).MinSize((-1, 100)).BestSize((-1, 100)) )

        # Panneau Remplissage
        self.ctrl_remplissage = DLG_Remplissage.Panel(self)
        self._mgr.AddPane(self.ctrl_remplissage, aui.AuiPaneInfo().Name("effectifs").Caption(u"Effectifs").
                          Left().Layer(1).Position(0).CloseButton(True).MaximizeButton(True).MinSize((200, 200)).BestSize((630, 600)) )
        
        # Panneau Messages
        self.ctrl_messages = CTRL_Messages.Panel(self)
        self._mgr.AddPane(self.ctrl_messages, aui.AuiPaneInfo().Name("messages").Caption(u"Messages").
                          Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True) )
        pi = self._mgr.GetPane("messages")
        pi.dock_proportion = 50000 # Proportion
        
        # Panneau Accueil
        self.ctrl_accueil = CTRL_Accueil.Panel(self)
        self._mgr.AddPane(self.ctrl_accueil, aui.AuiPaneInfo().Name("accueil").Caption(u"Accueil").
                          Bottom().Layer(0).Position(1).Hide().CaptionVisible(False).CloseButton(False).MaximizeButton(False) )
        
        # Sauvegarde de la perspective par défaut
        self.perspective_defaut = self._mgr.SavePerspective()
        
        # Cache tous les panneaux en attendant la saisie du mot de passe utilisateur
        for pane in self._mgr.GetAllPanes() :
            if pane.name != "accueil" :
                pane.Hide()
        self._mgr.GetPane("accueil").Show().Maximize()
        
        self._mgr.Update()
        
    def CreationBarreOutils(self):
        # Barre raccourcis
        self.toolBar1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW |
                             aui.AUI_TB_TEXT | aui.AUI_TB_HORZ_TEXT)
        self.toolBar1.SetToolBitmapSize(wx.Size(16, 16))
        self.toolBar1.AddSimpleTool(ID_TB_GESTIONNAIRE, u"Gestionnaire des conso.", wx.Bitmap("Images/16x16/Calendrier.png", wx.BITMAP_TYPE_PNG), u"Accéder au gestionnaire des consommations")
        self.toolBar1.AddSimpleTool(ID_TB_LISTE_CONSO, u"Liste des conso.", wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG), u"Imprimer une liste de consommations")
        self.toolBar1.AddSimpleTool(ID_TB_BADGEAGE, u"Badgeage", wx.Bitmap("Images/16x16/Badgeage.png", wx.BITMAP_TYPE_PNG), u"Lancer une procédure de badgeage")
        self.toolBar1.AddSeparator()
        self.toolBar1.AddSimpleTool(ID_TB_REGLER_FACTURE, u"Régler une facture", wx.Bitmap("Images/16x16/Reglement.png", wx.BITMAP_TYPE_PNG), u"Régler une facture à partir de son numéro")
        self.ctrl_numfacture = CTRL_Numfacture.CTRL(self.toolBar1, size=(100, -1))
        self.toolBar1.AddControl(self.ctrl_numfacture)
        self.toolBar1.AddSeparator()
        self.toolBar1.AddSimpleTool(ID_TB_CALCULATRICE, u"Calculatrice", wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG), u"Ouvrir la calculatrice")

        self.toolBar1.Realize()
        self._mgr.AddPane(self.toolBar1, aui.AuiPaneInfo().Name("barre_raccourcis").Caption(u"Barre de raccourcis").
                          ToolbarPane().Top())
        
        self._mgr.Update()
        
        # Barre Utilisateur
        self.toolBar2 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW |
                             aui.AUI_TB_TEXT | aui.AUI_TB_HORZ_TEXT)
        self.toolBar2.SetToolBitmapSize(wx.Size(16, 16))
        self.ctrl_identification = CTRL_Identification.CTRL(self.toolBar2, listeUtilisateurs=self.listeUtilisateurs, size=(80, -1))
        self.toolBar2.AddControl(self.ctrl_identification)
        self.toolBar2.AddSimpleTool(ID_TB_UTILISATEUR, u"xxxxxxxxxxxxxxxxxxxxxxxxxxxx", wx.Bitmap("Images/16x16/Homme.png", wx.BITMAP_TYPE_PNG), u"Utilisateur en cours")
        self.toolBar2.AddSpacer(50)
        
        self.toolBar2.Realize()
        
        self._mgr.AddPane(self.toolBar2, aui.AuiPaneInfo().Name("barre_utilisateur").Caption(u"Barre Utilisateur").
                          ToolbarPane().Top())
                
        self._mgr.Update()
        
    def CreationBarreMenus(self):
        """ Construit la barre de menus """
        menubar = wx.MenuBar()
        
        # Menu Fichier -------------------------------------
        menu_fichier = wx.Menu()
        
##        item = wx.MenuItem(menu_fichier, ID_ASSISTANT_DEMARRAGE, u"Assistant Démarrage", u"Ouvrir l'assistant démarrage")
##        item.SetBitmap(wx.Bitmap("Images/16x16/Assistant.png", wx.BITMAP_TYPE_PNG))
##        menu_fichier.AppendItem(item)
##        menu_fichier.AppendSeparator()
        item = wx.MenuItem(menu_fichier, ID_NOUVEAU_FICHIER, u"Créer un nouveau fichier\tCtrl+N", u"Créer un nouveau fichier")
        item.SetBitmap(wx.Bitmap("Images/16x16/Fichier_nouveau.png", wx.BITMAP_TYPE_PNG))
        menu_fichier.AppendItem(item)
        item = wx.MenuItem(menu_fichier, ID_OUVRIR_FICHIER, u"Ouvrir un fichier\tCtrl+O", u"Ouvrir un fichier existant")
        item.SetBitmap(wx.Bitmap("Images/16x16/Fichier_ouvrir.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item = wx.MenuItem(menu_fichier, ID_FERMER_FICHIER, u"Fermer le fichier\tCtrl+F", u"Fermer le fichier ouvert")
        item.SetBitmap(wx.Bitmap("Images/16x16/Fichier_fermer.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item.Enable(False)
        menu_fichier.AppendSeparator()
        item = wx.MenuItem(menu_fichier, ID_FICHIER_INFORMATIONS, u"Informations sur le fichier", u"Informations sur le fichier ouvert")
        item.SetBitmap(wx.Bitmap("Images/16x16/Information.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item.Enable(False)
        menu_fichier.AppendSeparator()
        item = wx.MenuItem(menu_fichier, ID_CREER_SAUVEGARDE, u"Créer une sauvegarde\tCtrl+S", u"Créer une sauvegarde globale des données")
        item.SetBitmap(wx.Bitmap("Images/16x16/Sauvegarder.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item = wx.MenuItem(menu_fichier, ID_RESTAURER_SAUVEGARDE, u"Restaurer une sauvegarde\tCtrl+R", u"Restaurer une sauvegarde")
        item.SetBitmap(wx.Bitmap("Images/16x16/Restaurer.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item = wx.MenuItem(menu_fichier, ID_SAUVEGARDES_AUTO, u"Sauvegardes automatiques", u"Paramétrer des sauvegardes automatiques")
        item.SetBitmap(wx.Bitmap("Images/16x16/Sauvegarder_param.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        menu_fichier.AppendSeparator()
        item = wx.MenuItem(menu_fichier, ID_CONVERSION_RESEAU, u"Convertir en fichier réseau", u"Convertir le fichier ouvert en fichier réseau")
        item.SetBitmap(wx.Bitmap("Images/16x16/Conversion_reseau.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item.Enable(False)
        item = wx.MenuItem(menu_fichier, ID_CONVERSION_LOCAL, u"Convertir en fichier local", u"Convertir le fichier ouvert en fichier local")
        item.SetBitmap(wx.Bitmap("Images/16x16/Conversion_local.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        item.Enable(False)
        menu_fichier.AppendSeparator()
        item = wx.MenuItem(menu_fichier, ID_QUITTER, u"Quitter\tCtrl+Q", u"Quitter l'application")
        item.SetBitmap(wx.Bitmap("Images/16x16/Quitter.png", wx.BITMAP_TYPE_PNG)) 
        menu_fichier.AppendItem(item)
        
        # Intégration des derniers fichiers ouverts :
        listeDerniersFichiersTmp = self.userConfig["derniersFichiers"]
        if len(listeDerniersFichiersTmp) > 0 :
            menu_fichier.AppendSeparator()
            
        # Vérification de la liste
        listeDerniersFichiers = []
        for nomFichier in listeDerniersFichiersTmp :
            
            if "[RESEAU]" in nomFichier :
                # Version RESEAU
                listeDerniersFichiers.append(nomFichier)
            else:
                # VERSION LOCAL
                fichier = "Data/" + nomFichier + "_DATA.dat"
                test = os.path.isfile(fichier)
                if test == True : 
                    listeDerniersFichiers.append(nomFichier)
        self.userConfig["derniersFichiers"] = listeDerniersFichiers
        
        if len(listeDerniersFichiers) > 0 : 
            index = 0
            for nomFichier in listeDerniersFichiers :
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menu_fichier, ID_DERNIER_FICHIER + index, u"%d. %s" % (index+1, nomFichier), u"Ouvrir le fichier : '%s'" % nomFichier)
                menu_fichier.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.On_fichier_DerniersFichiers, id=ID_DERNIER_FICHIER, id2=ID_DERNIER_FICHIER + index)

        menubar.Append(menu_fichier, u"Fichier")
        
        # Menu Paramétrage -------------------------------------
        menu_param = wx.Menu()

        item = wx.MenuItem(menu_param, ID_PARAM_PREFERENCES, u"Préférences", u"Préférences")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_ENREGISTREMENT, u"Enregistrement", u"Enregistrement")
        item.SetBitmap(wx.Bitmap("Images/16x16/Cle.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        menu_param.AppendSeparator()
        
        item = wx.MenuItem(menu_param, ID_PARAM_UTILISATEURS, u"Utilisateurs", u"Paramétrage des utilisateurs")
        item.SetBitmap(wx.Bitmap("Images/16x16/Personnes.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_MODELES_DROITS, u"Modèles de droits", u"Paramétrage des modèles de droits")
        item.SetBitmap(wx.Bitmap("Images/16x16/Droits.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_UTILISATEURS_RESEAU, u"Accès réseau", u"Paramétrage des accès réseau")
        item.SetBitmap(wx.Bitmap("Images/16x16/Utilisateur_reseau.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        menu_param.AppendSeparator()
        
        item = wx.MenuItem(menu_param, ID_PARAM_ORGANISATEUR, u"Organisateur", u"Paramétrage des données sur l'organisateur")
        item.SetBitmap(wx.Bitmap("Images/16x16/Organisateur.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_GROUPES_ACTIVITES, u"Groupes d'activités", u"Paramétrage des groupes d'activités")
        item.SetBitmap(wx.Bitmap("Images/16x16/Groupe_activite.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_ACTIVITES, u"Activités", u"Paramétrage des activités")
        item.SetBitmap(wx.Bitmap("Images/16x16/Activite.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_TYPES_COTISATIONS, u"Cotisations", u"Paramétrage des types de cotisations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Identite.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        menu_param.AppendSeparator()
        
        item = wx.MenuItem(menu_param, ID_PARAM_DOCUMENTS, u"Modèles de documents", u"Paramétrage des modèles de documents")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_MODELES_EMAILS, u"Modèles d'Emails", u"Paramétrage des modèles d'Emails")
        item.SetBitmap(wx.Bitmap("Images/16x16/Emails_modele.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_MODELES_TICKETS, u"Modèles de tickets", u"Paramétrage des modèles de tickets")
        item.SetBitmap(wx.Bitmap("Images/16x16/Ticket.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        menu_param.AppendSeparator()
        
        item = wx.MenuItem(menu_param, ID_PARAM_BADGEAGE, u"Procédures de badgeage", u"Paramétrage des procédures de badgeage")
        item.SetBitmap(wx.Bitmap("Images/16x16/Badgeage.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_VOCAL, u"Synthèse vocale", u"Paramétrage de la synthèse vocale")
        item.SetBitmap(wx.Bitmap("Images/16x16/Vocal.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        menu_param.AppendSeparator()
        
        sousMenuFacturation = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_LOTS_FACTURES, u"Lots de factures", u"Paramétrage des lots de factures")
        item.SetBitmap(wx.Bitmap("Images/16x16/Lot_factures.png", wx.BITMAP_TYPE_PNG))
        sousMenuFacturation.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_LOTS_RAPPELS, u"Lots de rappels", u"Paramétrage des lots de rappels")
        item.SetBitmap(wx.Bitmap("Images/16x16/Lot_factures.png", wx.BITMAP_TYPE_PNG))
        sousMenuFacturation.AppendItem(item)
        
        item = menu_param.AppendMenu(ID_PARAM_MENU_FACTURATION, u"Facturation", sousMenuFacturation)
        
        sousMenuReglements = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPTES, u"Comptes bancaires", u"Paramétrage des comptes bancaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Reglement.png", wx.BITMAP_TYPE_PNG))
        sousMenuReglements.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_MODES_REGLEMENTS, u"Modes de règlements", u"Paramétrage des modes de règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mode_reglement.png", wx.BITMAP_TYPE_PNG))
        sousMenuReglements.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_EMETTEURS, u"Emetteurs de règlements", u"Paramétrage des émetteurs de règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mode_reglement.png", wx.BITMAP_TYPE_PNG))
        sousMenuReglements.AppendItem(item)
        
        item = menu_param.AppendMenu(ID_PARAM_MENU_REGLEMENTS, u"Règlements", sousMenuReglements)

        sousMenuPrelevements = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_BANQUES, u"Etablissements bancaires", u"Paramétrage des établissements bancaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Banque.png", wx.BITMAP_TYPE_PNG))
        sousMenuPrelevements.AppendItem(item)
        
        item = menu_param.AppendMenu(ID_PARAM_MENU_PRELEVEMENTS, u"Prélèvement automatique", sousMenuPrelevements)

        menu_param.AppendSeparator()

        item = wx.MenuItem(menu_param, ID_PARAM_REGIMES, u"Régimes sociaux", u"Paramétrage des régimes sociaux")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_CAISSES, u"Caisses", u"Paramétrage des caisses")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_MODELES_AIDES, u"Modèles d'aides journalières", u"Paramétrage des modèles d'aides journalières")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        menu_param.AppendSeparator()
        
        sousMenuRenseignements = wx.Menu()

        item = wx.MenuItem(menu_param, ID_PARAM_QUESTIONNAIRES, u"Questionnaires", u"Paramétrage des questionnaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Questionnaire.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_PIECES, u"Types de pièces", u"Paramétrage des types de pièces")
        item.SetBitmap(wx.Bitmap("Images/16x16/Piece.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_CATEGORIES_TRAVAIL, u"Catégories socio-professionnelles", u"Paramétrage des catégories socio-professionnelles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Camion.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_VILLES, u"Villes et codes postaux", u"Paramétrage des villes et codes postaux")
        item.SetBitmap(wx.Bitmap("Images/16x16/Carte.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_SECTEURS, u"Secteurs géographiques", u"Paramétrage des secteurs géographiques")
        item.SetBitmap(wx.Bitmap("Images/16x16/Secteur.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_TYPES_SIESTE, u"Types de sieste", u"Paramétrage des types de sieste")
        item.SetBitmap(wx.Bitmap("Images/16x16/Reveil.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_MALADIES, u"Maladies", u"Paramétrage des maladies")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medical.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_VACCINS, u"Vaccins", u"Paramétrage des vaccins")
        item.SetBitmap(wx.Bitmap("Images/16x16/Seringue.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_MEDECINS, u"Médecins", u"Paramétrage des médecins")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medecin.png", wx.BITMAP_TYPE_PNG))
        sousMenuRenseignements.AppendItem(item)

        item = menu_param.AppendMenu(ID_PARAM_MENU_RENSEIGNEMENTS, u"Renseignements", sousMenuRenseignements)
                
        
        sousMenuScolaire = wx.Menu()

        item = wx.MenuItem(menu_param, ID_PARAM_NIVEAUX_SCOLAIRES, u"Niveaux scolaires", u"Paramétrage des niveaux scolaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Niveau_scolaire.png", wx.BITMAP_TYPE_PNG))
        sousMenuScolaire.AppendItem(item)
        
        sousMenuScolaire.AppendSeparator()

        item = wx.MenuItem(menu_param, ID_PARAM_ECOLES, u"Ecoles", u"Paramétrage des écoles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Ecole.png", wx.BITMAP_TYPE_PNG))
        sousMenuScolaire.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_CLASSES, u"Classes", u"Paramétrage des classes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Classe.png", wx.BITMAP_TYPE_PNG))
        sousMenuScolaire.AppendItem(item)
        
        item = menu_param.AppendMenu(ID_PARAM_MENU_SCOLAIRE, u"Scolarité", sousMenuScolaire)

        sousMenuTransports = wx.Menu()
        
        
        # Sous-menu Bus
        sousMenuTransportsBus = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_BUS, u"Compagnies de bus", u"Compagnies de bus")
        item.SetBitmap(wx.Bitmap("Images/16x16/Bus.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsBus.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_LIGNES_BUS, u"Lignes de bus", u"Lignes de bus")
        item.SetBitmap(wx.Bitmap("Images/16x16/Bus.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsBus.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_ARRETS_BUS, u"Arrêts de bus", u"Arrêts de bus")
        item.SetBitmap(wx.Bitmap("Images/16x16/Bus.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsBus.AppendItem(item)

        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_BUS, u"Bus", sousMenuTransportsBus)
        
        # Sous-menu Car
        sousMenuTransportsCar = wx.Menu()
                
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_CAR, u"Compagnies de cars", u"Compagnies de cars")
        item.SetBitmap(wx.Bitmap("Images/16x16/Car.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsCar.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_LIGNES_CAR, u"Lignes de cars", u"Lignes de cars")
        item.SetBitmap(wx.Bitmap("Images/16x16/Car.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsCar.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_ARRETS_CAR, u"Arrêts de cars", u"Arrêts de cars")
        item.SetBitmap(wx.Bitmap("Images/16x16/Car.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsCar.AppendItem(item)
        
        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_CAR, u"Car", sousMenuTransportsCar)
        
        # Sous-menu Navette
        sousMenuTransportsNavette = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_NAVETTE, u"Compagnies de navettes", u"Compagnies de navettes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Navette.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsNavette.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_LIGNES_NAVETTE, u"Lignes de navettes", u"Lignes de navettes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Navette.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsNavette.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_ARRETS_NAVETTE, u"Arrêts de navettes", u"Arrêts de navettes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Navette.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsNavette.AppendItem(item)
        
        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_NAVETTE, u"Navette", sousMenuTransportsNavette)
        
        # Sous-menu Taxi
        sousMenuTransportsTaxi = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_TAXI, u"Compagnies de taxis", u"Compagnies de taxis")
        item.SetBitmap(wx.Bitmap("Images/16x16/Taxi.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsTaxi.AppendItem(item)
        
        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_TAXI, u"Taxi", sousMenuTransportsTaxi)
        
        # Sous-menu Train
        sousMenuTransportsTrain = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_LIEUX_GARES, u"Gares", u"Paramétrage des gares")
        item.SetBitmap(wx.Bitmap("Images/16x16/Train.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsTrain.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_TRAIN, u"Compagnies ferroviaires", u"Compagnies ferroviaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Train.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsTrain.AppendItem(item)
        
        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_TRAIN, u"Train", sousMenuTransportsTrain)
        
        # Sous-menu Avion
        sousMenuTransportsAvion = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_LIEUX_AEROPORTS, u"Aéroports", u"Paramétrage des aéroports")
        item.SetBitmap(wx.Bitmap("Images/16x16/Avion.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsAvion.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_AVION, u"Compagnies aériennes", u"Compagnies aériennes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Avion.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsAvion.AppendItem(item)

        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_AVION, u"Avion", sousMenuTransportsAvion)

        # Sous-menu Bateau
        sousMenuTransportsBateau = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_LIEUX_PORTS, u"Ports", u"Paramétrage des ports")
        item.SetBitmap(wx.Bitmap("Images/16x16/Bateau.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsBateau.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_BATEAU, u"Compagnies maritimes", u"Compagnies maritimes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Bateau.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsBateau.AppendItem(item)
        
##        item = wx.MenuItem(menu_param, ID_PARAM_LIGNES_BATEAU, u"Lignes maritimes", u"Lignes maritimes")
##        item.SetBitmap(wx.Bitmap("Images/16x16/Bateau.png", wx.BITMAP_TYPE_PNG))
##        sousMenuTransportsBateau.AppendItem(item)
##        
##        item = wx.MenuItem(menu_param, ID_PARAM_ARRETS_BATEAU, u"Arrêts maritimes", u"Arrêts maritimes")
##        item.SetBitmap(wx.Bitmap("Images/16x16/Bateau.png", wx.BITMAP_TYPE_PNG))
##        sousMenuTransportsBateau.AppendItem(item)
        
        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_BATEAU, u"Bateau", sousMenuTransportsBateau)

        # Sous-menu Métro
        sousMenuTransportsMetro = wx.Menu()

##        item = wx.MenuItem(menu_param, ID_PARAM_LIEUX_STATIONS, u"Stations de métro", u"Paramétrage des stations de métro")
##        item.SetBitmap(wx.Bitmap("Images/16x16/Metro.png", wx.BITMAP_TYPE_PNG))
##        sousMenuTransportsMetro.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_COMPAGNIES_METRO, u"Compagnies de métros", u"Compagnies de métros")
        item.SetBitmap(wx.Bitmap("Images/16x16/Metro.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsMetro.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_LIGNES_METRO, u"Lignes de métros", u"Lignes de métros")
        item.SetBitmap(wx.Bitmap("Images/16x16/Metro.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsMetro.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_ARRETS_METRO, u"Arrêts de métros", u"Arrêts de métros")
        item.SetBitmap(wx.Bitmap("Images/16x16/Metro.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsMetro.AppendItem(item)

        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_METRO, u"Métro", sousMenuTransportsMetro)

        # Sous-menu Pédibus
        sousMenuTransportsPedibus = wx.Menu()

        item = wx.MenuItem(menu_param, ID_PARAM_LIGNES_PEDIBUS, u"Lignes de pédibus", u"Lignes de pédibus")
        item.SetBitmap(wx.Bitmap("Images/16x16/Pedibus.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsPedibus.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_ARRETS_PEDIBUS, u"Arrêts de pédibus", u"Arrêts de pédibus")
        item.SetBitmap(wx.Bitmap("Images/16x16/Pedibus.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransportsPedibus.AppendItem(item)

        item = sousMenuTransports.AppendMenu(ID_PARAM_MENU_TRANSPORTS_PEDIBUS, u"Pédibus", sousMenuTransportsPedibus)

        item = menu_param.AppendMenu(ID_PARAM_MENU_TRANSPORTS, u"Transports", sousMenuTransports)

        menu_param.AppendSeparator()


        item = wx.MenuItem(menu_param, ID_PARAM_CATEGORIES_MESSAGES, u"Catégories de messages", u"Paramétrage des catégories de messages")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_RESTAURATEURS, u"Restaurateurs", u"Paramétrage des restaurateurs")
        item.SetBitmap(wx.Bitmap("Images/16x16/Restaurateur.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_EMAILS_EXP, u"Adresses d'expédition d'Emails", u"Paramétrage des adresses d'expédition d'Emails")
        item.SetBitmap(wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)
        
        item = wx.MenuItem(menu_param, ID_PARAM_LISTE_DIFFUSION, u"Listes de diffusion", u"Paramétrage des listes de diffusion")
        item.SetBitmap(wx.Bitmap("Images/16x16/Liste_diffusion.png", wx.BITMAP_TYPE_PNG))
        menu_param.AppendItem(item)

        menu_param.AppendSeparator()
        
        sousMenuCalendrier = wx.Menu()
        
        item = wx.MenuItem(menu_param, ID_PARAM_VACANCES, u"Vacances", u"Paramétrage des vacances")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calendrier.png", wx.BITMAP_TYPE_PNG))
        sousMenuCalendrier.AppendItem(item)

        item = wx.MenuItem(menu_param, ID_PARAM_FERIES, u"Jours fériés", u"Paramétrage des jours fériés")
        item.SetBitmap(wx.Bitmap("Images/16x16/Jour.png", wx.BITMAP_TYPE_PNG))
        sousMenuCalendrier.AppendItem(item)

        item = menu_param.AppendMenu(ID_PARAM_MENU_CALENDRIER, u"Calendrier", sousMenuCalendrier)

        menubar.Append(menu_param, u"Paramétrage")

        # Menu AFFICHAGE -------------------------------------
        menu_affichage = wx.Menu()
        
        item = wx.MenuItem(menu_affichage, ID_AFFICHAGE_PERSPECTIVE_DEFAUT, u"Disposition par défaut", u"Afficher la disposition par défaut", wx.ITEM_CHECK)
        menu_affichage.AppendItem(item)
        if self.perspective_active == None : item.Check(True)
        
        index = 0
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menu_affichage, ID_PREMIERE_PERSPECTIVE + index, label, u"Afficher la disposition '%s'" % label, wx.ITEM_CHECK)
            menu_affichage.AppendItem(item)
            if self.perspective_active == index : item.Check(True)
            index += 1
        
        menu_affichage.AppendSeparator()
        
        item = wx.MenuItem(menu_affichage, ID_AFFICHAGE_PERSPECTIVE_SAVE, u"Sauvegarder la disposition actuelle", u"Sauvegarder la disposition actuelle de la page d'accueil")
        item.SetBitmap(wx.Bitmap("Images/16x16/Perspective_ajouter.png", wx.BITMAP_TYPE_PNG))
        menu_affichage.AppendItem(item)
        
        item = wx.MenuItem(menu_affichage, ID_AFFICHAGE_PERSPECTIVE_SUPPR, u"Supprimer des dispositions", u"Supprimer des dispositions de page d'accueil sauvegardée")
        item.SetBitmap(wx.Bitmap("Images/16x16/Perspective_supprimer.png", wx.BITMAP_TYPE_PNG))
        menu_affichage.AppendItem(item)
        
        menu_affichage.AppendSeparator()
        
        self.listePanneaux = [
            { "label" : u"Effectifs", "code" : "effectifs", "IDmenu" : None },
            { "label" : u"Messages", "code" : "messages", "IDmenu" : None }, 
            { "label" : u"Ephéméride", "code" : "ephemeride", "IDmenu" : None }, 
            { "label" : u"Barre de raccourcis", "code" : "barre_raccourcis", "IDmenu" : None },
            { "label" : u"Barre utilisateur", "code" : "barre_utilisateur", "IDmenu" : None },
            ]
        ID = ID_AFFICHAGE_PANNEAUX
        for dictPanneau in self.listePanneaux :
            dictPanneau["IDmenu"] = ID
            label = dictPanneau["label"]
            item = wx.MenuItem(menu_affichage, dictPanneau["IDmenu"], label, u"Afficher le panneau '%s'" % label, wx.ITEM_CHECK)
            menu_affichage.AppendItem(item)
            ID += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_panneau_afficher, id=ID_AFFICHAGE_PANNEAUX, id2=ID_AFFICHAGE_PANNEAUX+len(self.listePanneaux) )
        
        menubar.Append(menu_affichage, u"Affichage")
        
        menu_affichage.AppendSeparator()
        
        item = wx.MenuItem(menu_affichage, ID_AFFICHAGE_ACTUALISER, u"Actualiser l'affichage\tF11", u"Actualiser les données de la page d'accueil")
        item.SetBitmap(wx.Bitmap("Images/16x16/Actualiser2.png", wx.BITMAP_TYPE_PNG))
        menu_affichage.AppendItem(item)

        # Menu OUTILS -------------------------------------
        menu_outils = wx.Menu()

        item = wx.MenuItem(menu_outils, ID_OUTILS_STATS, u"Statistiques", u"Afficher les statistiques pour une période donnée")
        item.SetBitmap(wx.Bitmap("Images/16x16/Barres.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        menu_outils.AppendSeparator()

        
        item = wx.MenuItem(menu_outils, ID_OUTILS_ENVOI_EMAILS, u"Editeur d'Emails", u"Envoyer des Emails depuis l'éditeur d'Emails")
        item.SetBitmap(wx.Bitmap("Images/16x16/Editeur_email.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        item = wx.MenuItem(menu_outils, ID_OUTILS_CALCULATRICE, u"Calculatrice\tF12", u"Utiliser la calculatrice installée par défaut sur votre système d'exploitation")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        item = wx.MenuItem(menu_outils, ID_OUTILS_CALENDRIER, u"Calendrier", u"Afficher un calendrier avec vacances et jours fériés")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calendrier.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        menu_outils.AppendSeparator()
        
        item = wx.MenuItem(menu_outils, ID_OUTILS_VILLES, u"Villes et codes postaux", u"Rechercher une ville ou un code postal")
        item.SetBitmap(wx.Bitmap("Images/16x16/Carte.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        item = wx.MenuItem(menu_outils, ID_OUTILS_GPS, u"Géolocalisation GPS", u"Trouvez les coordonnées GPS d'un lieu")
        item.SetBitmap(wx.Bitmap("Images/16x16/Carte.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        item = wx.MenuItem(menu_outils, ID_OUTILS_METEO, u"Prévisions météorologiques", u"Prévisions météorologiques")
        item.SetBitmap(wx.Bitmap("Images/16x16/Meteo.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        item = wx.MenuItem(menu_outils, ID_OUTILS_HORAIRES_SOLEIL, u"Horaires du soleil", u"Affiche les horaires du soleil pour une ville et un mois donnés")
        item.SetBitmap(wx.Bitmap("Images/16x16/Soleil.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        menu_outils.AppendSeparator()
        
        item = wx.MenuItem(menu_outils, ID_OUTILS_CONNEXIONS, u"Liste des connexions réseau", u"Liste des connexions réseau")
        item.SetBitmap(wx.Bitmap("Images/16x16/Connexion.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)
        
        menu_outils.AppendSeparator()

        item = wx.MenuItem(menu_outils, ID_OUTILS_MESSAGES, u"Messages", u"Consulter la liste des messages")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)

        item = wx.MenuItem(menu_outils, ID_OUTILS_HISTORIQUE, u"Historique", u"Consulter l'historique des actions effectuées dans le logiciel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Historique.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)
        
        sousMenuUtilitaires = wx.Menu()

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_CORRECTEUR, u"Correcteur d'anomalies", u"Correcteur d'anomalies")
        item.SetBitmap(wx.Bitmap("Images/16x16/Depannage.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        sousMenuUtilitaires.AppendSeparator()

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PURGER_HISTORIQUE, u"Purger l'historique", u"Purger l'historique")
        item.SetBitmap(wx.Bitmap("Images/16x16/Poubelle.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PURGER_JOURNAL_BADGEAGE, u"Purger le journal de badgeage", u"Purger le journal de badgeage")
        item.SetBitmap(wx.Bitmap("Images/16x16/Poubelle.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PURGER_ARCHIVES_BADGEAGE, u"Purger les archives des badgeages importés", u"Purger les archives des badgeages importés")
        item.SetBitmap(wx.Bitmap("Images/16x16/Poubelle.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PURGER_REP_UPDATES, u"Purger le répertoire Updates", u"Purger le répertoire Updates")
        item.SetBitmap(wx.Bitmap("Images/16x16/Poubelle.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        sousMenuUtilitaires.AppendSeparator()

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_EXTENSIONS, u"Extensions", u"Extensions")
        item.SetBitmap(wx.Bitmap("Images/16x16/Terminal.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PROCEDURES, u"Procédures", u"Procédures")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_REINITIALISATION, u"Réinitialisation du fichier de configuration", u"Réinitialisation du fichier de configuration")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_TRANSFERT_TABLES, u"Transférer des tables", u"Transférer des tables de données")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        sousMenuUtilitaires.AppendSeparator()
        
        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PROCEDURE_E4072, u"Suppression des prestations sans consommations associées", u"Suppression des prestations sans consommations associées")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medecin3.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_PRESTATIONS_SANS_CONSO, u"Liste des prestations sans consommations associées", u"Liste des prestations sans consommations associées")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medecin3.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_CONSO_SANS_PRESTATIONS, u"Liste des consommations sans prestations associées", u"Liste des consommations sans prestations associées")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medecin3.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_DEVERROUILLAGE_FORFAITS, u"Déverrouillage des consommations de forfaits", u"Déverrouiller des consommations de forfaits")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medecin3.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        sousMenuUtilitaires.AppendSeparator()

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_APPLIQUER_TVA, u"Appliquer un taux de TVA à un lot de prestations", u"Appliquer un taux de TVA à un lot de prestations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_APPLIQUER_CODE_COMPTABLE, u"Appliquer un code comptable à un lot de prestations", u"Appliquer un code comptable à un lot de prestations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_CONVERSION_RIB_SEPA, u"Convertir les RIB nationaux en mandats SEPA", u"Convertir les RIB nationaux en mandats SEPA")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_CREATION_TITULAIRES_HELIOS, u"Création automatique des titulaires Hélios", u"Création automatique des titulaires Hélios")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        sousMenuUtilitaires.AppendSeparator()
        
        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_CONSOLE_PYTHON, u"Console Python", u"Console Python")
        item.SetBitmap(wx.Bitmap("Images/16x16/Python.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_CONSOLE_SQL, u"Console SQL", u"Console SQL")
        item.SetBitmap(wx.Bitmap("Images/16x16/Sql.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = wx.MenuItem(sousMenuUtilitaires, ID_OUTILS_LISTE_PERSO, u"Liste personnalisée", u"Liste personnalisée SQL")
        item.SetBitmap(wx.Bitmap("Images/16x16/Sql.png", wx.BITMAP_TYPE_PNG))
        sousMenuUtilitaires.AppendItem(item)

        item = menu_outils.AppendMenu(ID_OUTILS_UTILITAIRES, u"Utilitaires administrateur", sousMenuUtilitaires)
        
        menu_outils.AppendSeparator()
        
        item = wx.MenuItem(menu_outils, ID_OUTILS_UPDATER, u"Rechercher une mise à jour du logiciel", u"Rechercher une mise à jour du logiciel sur internet")
        item.SetBitmap(wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_PNG))
        menu_outils.AppendItem(item)
        
        menubar.Append(menu_outils, u"Outils")
        
        # Menu INDIVIDUS -------------------------------------
        menu_individus = wx.Menu()
        
        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_SCOLARITE, u"Inscriptions scolaires", u"Gestion des inscriptions scolaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Classe.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)
        
        menu_individus.AppendSeparator()

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_INSCRIPTIONS, u"Liste des inscriptions", u"Editer une liste des inscriptions")
        item.SetBitmap(wx.Bitmap("Images/16x16/Activite.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_INDIVIDUS, u"Liste des individus", u"Editer une liste des individus")
        item.SetBitmap(wx.Bitmap("Images/16x16/Personnes.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)
        
        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_FAMILLES, u"Liste des familles", u"Editer une liste des familles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)
        
        menu_individus.AppendSeparator()
        
        sousMenuTransports = wx.Menu()
        
        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_TRANSPORTS_RECAP, u"Liste récapitulative", u"Editer une liste récapitulative des transports")
        item.SetBitmap(wx.Bitmap("Images/16x16/Transport.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransports.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_TRANSPORTS_DETAIL, u"Liste détaillée", u"Editer une liste détaillée des transports")
        item.SetBitmap(wx.Bitmap("Images/16x16/Transport.png", wx.BITMAP_TYPE_PNG))
        sousMenuTransports.AppendItem(item)
        
        item = menu_individus.AppendMenu(ID_INDIVIDUS_TRANSPORTS, u"Liste des transports", sousMenuTransports)

        menu_individus.AppendSeparator()

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_ANNIVERSAIRES, u"Liste des anniversaires", u"Editer une liste des anniversaires")
        item.SetBitmap(wx.Bitmap("Images/16x16/Anniversaire.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)
        
        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_INFOS_MED, u"Liste des informations médicales", u"Editer une liste des informations médicales")
        item.SetBitmap(wx.Bitmap("Images/16x16/Medical.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_PIECES_FOURNIES, u"Liste des pièces fournies", u"Editer la liste des pièces fournies")
        item.SetBitmap(wx.Bitmap("Images/16x16/Piece.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_PIECES_MANQUANTES, u"Liste des pièces manquantes", u"Editer la liste des pièces manquantes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Piece.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)
        
        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_REGIMES_CAISSES, u"Liste des régimes et caisses des familles", u"Editer la liste des régimes et caisses des familles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_QUOTIENTS, u"Liste des quotients familiaux", u"Editer la liste des quotients familiaux des familles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_MANDATS, u"Liste des mandats SEPA", u"Editer la liste des mandats SEPA")
        item.SetBitmap(wx.Bitmap("Images/16x16/Prelevement.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        menu_individus.AppendSeparator()

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_IMPORTER_PHOTOS, u"Importer des photos individuelles", u"Importer des photos individuelles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Photos.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        sousMenuImporter = wx.Menu()
        
        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_IMPORTER_CSV, u"Importer des individus ou des familles depuis un fichier Excel ou CSV", u"Importer des individus ou des familles depuis un fichier Excel ou CSV")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document_import.png", wx.BITMAP_TYPE_PNG))
        sousMenuImporter.AppendItem(item)

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_IMPORTER_FICHIER, u"Importer des familles depuis un fichier Noethys", u"Importer des familles depuis un autre fichier de données Noethys")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document_import.png", wx.BITMAP_TYPE_PNG))
        sousMenuImporter.AppendItem(item)
        
        item = menu_individus.AppendMenu(ID_INDIVIDUS_IMPORTER, u"Importer des familles ou des individus", sousMenuImporter)
        
        menu_individus.AppendSeparator()

        item = wx.MenuItem(menu_individus, ID_INDIVIDUS_EDITION_ETIQUETTES, u"Edition d'étiquettes et de badges", u"Edition d'étiquettes et de badges au format PDF")
        item.SetBitmap(wx.Bitmap("Images/16x16/Etiquette2.png", wx.BITMAP_TYPE_PNG))
        menu_individus.AppendItem(item)

        menubar.Append(menu_individus, u"Individus")

        # Menu CONSOMMATIONS -------------------------------------
        menu_consommations = wx.Menu()
        
        item = wx.MenuItem(menu_consommations, ID_IMPRIM_LISTE_CONSO_JOURN, u"Liste des consommations", u"Editer une liste journalière ou périodique des consommations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)

        item = wx.MenuItem(menu_consommations, ID_CONSO_GESTIONNAIRE, u"Gestionnaire des consommations", u"Gestionnaire des consommations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calendrier.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)

        menu_consommations.AppendSeparator()
        
        item = wx.MenuItem(menu_consommations, ID_CONSO_ATTENTE, u"Liste d'attente", u"Consulter la liste d'attente pour la période sélectionnée")
        item.SetBitmap(wx.Bitmap("Images/16x16/Liste_attente.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)
        
        item = wx.MenuItem(menu_consommations, ID_CONSO_REFUS, u"Liste des places refusées", u"Consulter la liste des places refusées pour la période sélectionnée")
        item.SetBitmap(wx.Bitmap("Images/16x16/Places_refus.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)

        item = wx.MenuItem(menu_consommations, ID_CONSO_ABSENCES, u"Liste des absences", u"Consulter la liste des absences injustifiées ou justifiées pour la période sélectionnée")
        item.SetBitmap(wx.Bitmap("Images/16x16/absenti.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)

        menu_consommations.AppendSeparator()

        item = wx.MenuItem(menu_consommations, ID_CONSO_SYNTHESE_CONSO, u"Synthèse des consommations", u"Consulter la synthèse des consommations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Diagramme.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)

        item = wx.MenuItem(menu_consommations, ID_CONSO_ETAT_GLOBAL, u"Etat global", u"Générer un état global des consommations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Tableaux.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)

        item = wx.MenuItem(menu_consommations, ID_CONSO_ETAT_NOMINATIF, u"Etat nominatif", u"Générer un état nominatif des consommations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Tableaux.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)
        
        menu_consommations.AppendSeparator()
        
        item = wx.MenuItem(menu_consommations, ID_CONSO_BADGEAGE, u"Badgeage", u"Lancement d'un procédure de badgeage")
        item.SetBitmap(wx.Bitmap("Images/16x16/Badgeage.png", wx.BITMAP_TYPE_PNG))
        menu_consommations.AppendItem(item)
                
        menubar.Append(menu_consommations, u"Consommations")

        # Menu FACTURATION -------------------------------------
        menu_facturation = wx.Menu()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_VENTILATION, u"Vérifier la ventilation", u"Vérifier la ventilation des règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Repartition.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)
        
        menu_facturation.AppendSeparator()
        
        sousMenuFactures = wx.Menu()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_FACTURES_GENERATION, u"Génération", u"Génération des factures")
        item.SetBitmap(wx.Bitmap("Images/16x16/Generation.png", wx.BITMAP_TYPE_PNG))
        sousMenuFactures.AppendItem(item)
        
        sousMenuFactures.AppendSeparator()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_FACTURES_HELIOS, u"Export vers Hélios", u"Exporter les factures vers Hélios")
        item.SetBitmap(wx.Bitmap("Images/16x16/Helios.png", wx.BITMAP_TYPE_PNG))
        sousMenuFactures.AppendItem(item)

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_FACTURES_PRELEVEMENT, u"Prélèvement automatique", u"Gestion du prélèvement automatique")
        item.SetBitmap(wx.Bitmap("Images/16x16/Prelevement.png", wx.BITMAP_TYPE_PNG))
        sousMenuFactures.AppendItem(item)
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_FACTURES_EMAIL, u"Transmettre par Email", u"Transmettre les factures par Email")
        item.SetBitmap(wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG))
        sousMenuFactures.AppendItem(item)
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_FACTURES_IMPRIMER, u"Imprimer", u"Imprimer une ou plusieurs factures")
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        sousMenuFactures.AppendItem(item)
        
        sousMenuFactures.AppendSeparator()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_FACTURES_LISTE, u"Liste des factures", u"Liste des factures générées")
        item.SetBitmap(wx.Bitmap("Images/16x16/Facture.png", wx.BITMAP_TYPE_PNG))
        sousMenuFactures.AppendItem(item)
        
        item = menu_facturation.AppendMenu(ID_FACTURATION_MENU_FACTURES, u"Factures", sousMenuFactures)
        
        sousMenuRappels = wx.Menu()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_RAPPELS_GENERATION, u"Génération", u"Génération des lettres de rappel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Generation.png", wx.BITMAP_TYPE_PNG))
        sousMenuRappels.AppendItem(item)
        
        sousMenuRappels.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_RAPPELS_EMAIL, u"Transmettre par Email", u"Transmettre les lettres de rappel par Email")
        item.SetBitmap(wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG))
        sousMenuRappels.AppendItem(item)
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_RAPPELS_IMPRIMER, u"Imprimer", u"Imprimer une ou plusieurs lettres de rappel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        sousMenuRappels.AppendItem(item)
        
        sousMenuRappels.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_RAPPELS_LISTE, u"Liste des lettres de rappels", u"Liste des lettres de rappel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Facture.png", wx.BITMAP_TYPE_PNG))
        sousMenuRappels.AppendItem(item)
        
        item = menu_facturation.AppendMenu(ID_FACTURATION_MENU_RAPPELS, u"Lettres de rappels", sousMenuRappels)

        sousMenuAttestations = wx.Menu()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_ATTESTATIONS_GENERATION, u"Génération", u"Génération des attestations de présence par lot")
        item.SetBitmap(wx.Bitmap("Images/16x16/Generation.png", wx.BITMAP_TYPE_PNG))
        sousMenuAttestations.AppendItem(item)
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_ATTESTATIONS_LISTE, u"Liste des attestations de présence", u"Liste des attestations de présence générées")
        item.SetBitmap(wx.Bitmap("Images/16x16/Facture.png", wx.BITMAP_TYPE_PNG))
        sousMenuAttestations.AppendItem(item)
        
        item = menu_facturation.AppendMenu(ID_FACTURATION_MENU_ATTESTATIONS, u"Attestations de présence", sousMenuAttestations)

        sousMenuAttestationsFiscales = wx.Menu()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_ATTESTATIONS_FISCALES_GENERATION, u"Génération", u"Génération des attestations fiscales par lot")
        item.SetBitmap(wx.Bitmap("Images/16x16/Generation.png", wx.BITMAP_TYPE_PNG))
        sousMenuAttestationsFiscales.AppendItem(item)
                
        item = menu_facturation.AppendMenu(ID_FACTURATION_MENU_ATTESTATIONS_FISCALES, u"Attestations fiscales", sousMenuAttestationsFiscales)

        menu_facturation.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_LISTE_PRESTATIONS, u"Liste des prestations", u"Liste des prestations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Euro.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_LISTE_DEDUCTIONS, u"Liste des déductions", u"Liste des déductions")
        item.SetBitmap(wx.Bitmap("Images/16x16/Euro.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)

        menu_facturation.AppendSeparator()
        
        item = wx.MenuItem(menu_facturation, ID_FACTURATION_SOLDES, u"Liste des soldes", u"Liste des soldes des comptes familles")
        item.SetBitmap(wx.Bitmap("Images/16x16/Euro.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_SOLDES_INDIVIDUELS, u"Liste des soldes individuels", u"Liste des soldes individuels")
        item.SetBitmap(wx.Bitmap("Images/16x16/Euro.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)
        
        menu_facturation.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_SOLDER_IMPAYES, u"Solder les impayés", u"Solder les impayés")
        item.SetBitmap(wx.Bitmap("Images/16x16/Impayes.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_SYNTHESE_IMPAYES, u"Synthèse des impayés", u"Synthèse des impayés")
        item.SetBitmap(wx.Bitmap("Images/16x16/Diagramme.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)
        
        menu_facturation.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_PRESTATIONS_VILLES, u"Liste des prestations par famille", u"Liste des prestations par famille")
        item.SetBitmap(wx.Bitmap("Images/16x16/Euro.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_SYNTHESE_PRESTATIONS, u"Synthèse des prestations", u"Synthèse des prestations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Diagramme.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)
        
        menu_facturation.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_FACTURATION_EXPORT_COMPTA, u"Export des écritures comptables", u"Exporter les écritures comptables vers des logiciels de comptabilité")
        item.SetBitmap(wx.Bitmap("Images/16x16/Export_comptable.png", wx.BITMAP_TYPE_PNG))
        menu_facturation.AppendItem(item)

        menubar.Append(menu_facturation, u"Facturation")
        
        # Menu COTISATIONS -------------------------------------
        menu_cotisations = wx.Menu()
        
        item = wx.MenuItem(menu_cotisations, ID_COTISATIONS_LISTE, u"Liste des cotisations", u"Consulter la liste des cotisations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Cotisation.png", wx.BITMAP_TYPE_PNG))
        menu_cotisations.AppendItem(item)
        
        item = wx.MenuItem(menu_cotisations, ID_COTISATIONS_MANQUANTES, u"Liste des cotisations manquantes", u"Editer la liste des cotisations manquantes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Cotisation.png", wx.BITMAP_TYPE_PNG))
        menu_cotisations.AppendItem(item)
        
        menu_cotisations.AppendSeparator()

        item = wx.MenuItem(menu_cotisations, ID_COTISATIONS_EMAIL, u"Transmettre des cotisations par Email", u"Transmettre des cotisations par Email")
        item.SetBitmap(wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG))
        menu_cotisations.AppendItem(item)
        
        item = wx.MenuItem(menu_cotisations, ID_COTISATIONS_IMPRIMER, u"Imprimer des cotisations", u"Imprimer une ou plusieurs cotisations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menu_cotisations.AppendItem(item)

        menu_cotisations.AppendSeparator()

        item = wx.MenuItem(menu_cotisations, ID_COTISATIONS_DEPOTS, u"Gestion des dépôts de cotisations", u"Gestion des dépôts de cotisations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Depot_cotisations.png", wx.BITMAP_TYPE_PNG))
        menu_cotisations.AppendItem(item)
                
        menubar.Append(menu_cotisations, u"Cotisations")

        # Menu REGLEMENTS -------------------------------------
        menu_reglements = wx.Menu()
        
        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_REGLER_FACTURE, u"Régler une facture\tF4", u"Régler une facture à partir de son numéro")
        item.SetBitmap(wx.Bitmap("Images/16x16/Codebarre.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)
        
        menu_reglements.AppendSeparator()
        
        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_RECUS, u"Liste des reçus de règlements", u"Consulter la liste des reçus de règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Note.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)
        
        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_LISTE, u"Liste des règlements", u"Consulter la liste des règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Reglement.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)
        
        menu_reglements.AppendSeparator()
        
        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_VENTILATION, u"Vérifier la ventilation", u"Vérifier la ventilation des règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Repartition.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)

        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_ANALYSE_VENTILATION, u"Tableau d'analyse croisée ventilation/dépôts", u"Tableau d'analyse croisée ventilation/dépôts")
        item.SetBitmap(wx.Bitmap("Images/16x16/Diagramme.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)

        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_SYNTHESE_MODES, u"Synthèse des modes de règlements", u"Synthèse des modes de règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Diagramme.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)

        menu_reglements.AppendSeparator()

        item = wx.MenuItem(menu_facturation, ID_REGLEMENTS_PRELEVEMENT, u"Prélèvement automatique", u"Gestion du prélèvement automatique")
        item.SetBitmap(wx.Bitmap("Images/16x16/Prelevement.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)

        item = wx.MenuItem(menu_reglements, ID_REGLEMENTS_DEPOTS, u"Gestion des dépôts", u"Gestion des dépôts")
        item.SetBitmap(wx.Bitmap("Images/16x16/Banque.png", wx.BITMAP_TYPE_PNG))
        menu_reglements.AppendItem(item)
                
        menubar.Append(menu_reglements, u"Règlements")
        
        # Menu AIDE -------------------------------------
        menu_aide = wx.Menu()
        
        item = wx.MenuItem(menu_aide, ID_AIDE_AIDE, u"Consulter l'aide", u"Consulter l'aide de Noethys")
        item.SetBitmap(wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)
    
        item = wx.MenuItem(menu_aide, ID_AIDE_ACHETER_LICENCE, u"Acheter une licence pour accéder au manuel de référence", u"Acheter une licence pour accéder au manuel de référence de Noethys")
        item.SetBitmap(wx.Bitmap("Images/16x16/Acheter_licence.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)

        menu_aide.AppendSeparator()

        item = wx.MenuItem(menu_aide, ID_AIDE_GUIDE_DEMARRAGE, u"Télécharger le guide de démarrage rapide (PDF)", u"Télécharger le guide de démarrage rapide (PDF)")
        item.SetBitmap(wx.Bitmap("Images/16x16/Livre.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)

        menu_aide.AppendSeparator()

        item = wx.MenuItem(menu_aide, ID_AIDE_FORUM, u"Accéder au forum d'entraide", u"Accéder au forum d'entraide")
        item.SetBitmap(wx.Bitmap("Images/16x16/Dialogue.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)

        item = wx.MenuItem(menu_aide, ID_AIDE_VIDEOS, u"Visionner des tutoriels vidéos", u"Visionner des tutoriels vidéos")
        item.SetBitmap(wx.Bitmap("Images/16x16/Film.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)

        item = wx.MenuItem(menu_aide, ID_AIDE_TELECHARGEMENTS, u"Télécharger des ressources communautaires", u"Accéder à la plate-forme de téléchargements communautaire")
        item.SetBitmap(wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)
        
        menu_aide.AppendSeparator()

        item = wx.MenuItem(menu_aide, ID_AIDE_AUTEUR, u"Envoyer un Email à l'auteur", u"Envoyer un Email à l'auteur")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menu_aide.AppendItem(item)
        
        menubar.Append(menu_aide, u"Aide")
        
        # Menu A PROPOS -------------------------------------
        menu_propos = wx.Menu()
        
        item = wx.MenuItem(menu_propos, ID_PROPOS_VERSIONS, u"Notes de versions", u"Notes de versions")
        item.SetBitmap(wx.Bitmap("Images/16x16/Versions.png", wx.BITMAP_TYPE_PNG))
        menu_propos.AppendItem(item)
        
        item = wx.MenuItem(menu_propos, ID_PROPOS_LICENCE, u"Licence", u"Licence du logiciel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Licence.png", wx.BITMAP_TYPE_PNG))
        menu_propos.AppendItem(item)
        
        menu_propos.AppendSeparator()
        
        item = wx.MenuItem(menu_propos, ID_PROPOS_SOUTENIR, u"Soutenir Noethys", u"Soutenir Noethys")
        item.SetBitmap(wx.Bitmap("Images/16x16/Soutenir_noethys.png", wx.BITMAP_TYPE_PNG))
        menu_propos.AppendItem(item)

        menu_propos.AppendSeparator()
        
        item = wx.MenuItem(menu_propos, ID_PROPOS_PROPOS, u"A propos", u"A propos")
        item.SetBitmap(wx.Bitmap("Images/16x16/Information.png", wx.BITMAP_TYPE_PNG))
        menu_propos.AppendItem(item)
                
        menubar.Append(menu_propos, u"A propos")
        
        # Menu MISE A JOUR INTERNET -------------------------------------
        if self.MAJexiste == True :
            menu_maj = wx.Menu()
            item = wx.MenuItem(menu_maj, ID_OUTILS_UPDATER_2, u"Télécharger la mise à jour", u"Télécharger la nouvelle mise à jour")
            item.SetBitmap(wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_PNG))
            menu_maj.AppendItem(item)
            menubar.Append(menu_maj, u"<< Télécharger la mise à jour >>")
            self.Bind(wx.EVT_MENU, self.On_outils_updater, id=ID_OUTILS_UPDATER_2)

        # Finalisation Barre de menu
        self.SetMenuBar(menubar)
        self.menubar = menubar

        
    
    def MAJmenuAffichage(self, event):
        """ Met à jour la liste des panneaux ouverts du menu Affichage """
        menuOuvert = event.GetMenu()
        itemTemp = self.GetMenuBar().FindItemById(ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        if menuOuvert == itemTemp.GetMenu() :
            for dictPanneau in self.listePanneaux :
                IDmenuItem = dictPanneau["IDmenu"]
                item = menuOuvert.FindItemById(IDmenuItem)
                panneau = self._mgr.GetPane(dictPanneau["code"])
                if panneau.IsShown() == True :
                    item.Check(True)
                else:
                    item.Check(False)

    def ForcerAffichagePanneau(self, nom="ephemeride"):
        """ Force l'affichage d'un panneau dans la perspective s'il n'y est pas. """
        """ Codé pour le panneau Ephemeride """
        self.ParadeAffichagePanneau(nom)
##        if nom not in self.perspectives[self.perspective_active]["perspective"] :
##            # Affichage forcé du panneau
##            self._mgr.GetPane(nom).Show()
##            self._mgr.Update()
##            # Modification de la perspective sauvegardée
##            self.perspectives[self.perspective_active]["perspective"] = self._mgr.SavePerspective()
    
    def SauvegardePerspectiveActive(self):
        """ Sauvegarde la perspective active """
        if self.perspective_active != None :
            self.perspectives[self.perspective_active]["perspective"] = self._mgr.SavePerspective()

    def SupprimeToutesPerspectives(self):
        """ Supprime toutes les perspectives et sélectionne celle par défaut """
        dlg = wx.MessageDialog(self, u"Suite à la mise à jour de Noethys, %d disposition(s) personnalisée(s) de la page d'accueil sont désormais obsolètes.\n\nPour les besoins de la nouvelle version, elles vont être supprimées. Mais il vous suffira de les recréer simplement depuis le menu Affichage... Merci de votre compréhension !" % len(self.perspectives), u"Mise à jour", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        # Suppression
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None
        self.perspectives = []
        self.MAJmenuPerspectives() 
        print "Toutes les perspectives ont ete supprimees."
        
    def ParadeAffichagePanneau(self, nom=""):
        """ Supprime toutes les perspectives si le panneau donné n'apparait pas """
        pb = False
        for perspective in self.perspectives :
            if nom not in perspective["perspective"] :
                pb = True
        if pb == True :
            self.SupprimeToutesPerspectives() 
        
    def CreationBinds(self):
        # Menu Fichier
        self.Bind(wx.EVT_MENU, self.On_fichier_AssistantDemarrage, id=ID_ASSISTANT_DEMARRAGE)
        self.Bind(wx.EVT_MENU, self.On_fichier_Nouveau, id=ID_NOUVEAU_FICHIER)
        self.Bind(wx.EVT_MENU, self.On_fichier_Ouvrir, id=ID_OUVRIR_FICHIER)
        self.Bind(wx.EVT_MENU, self.On_fichier_Fermer, id=ID_FERMER_FICHIER)
        self.Bind(wx.EVT_MENU, self.On_fichier_Informations, id=ID_FICHIER_INFORMATIONS)
        self.Bind(wx.EVT_MENU, self.On_fichier_Sauvegarder, id=ID_CREER_SAUVEGARDE)
        self.Bind(wx.EVT_MENU, self.On_fichier_Restaurer, id=ID_RESTAURER_SAUVEGARDE)
        self.Bind(wx.EVT_MENU, self.On_fichier_Sauvegardes_auto, id=ID_SAUVEGARDES_AUTO)
        self.Bind(wx.EVT_MENU, self.On_fichier_Convertir_reseau, id=ID_CONVERSION_RESEAU)
        self.Bind(wx.EVT_MENU, self.On_fichier_Convertir_local, id=ID_CONVERSION_LOCAL)
        self.Bind(wx.EVT_MENU, self.On_fichier_Quitter, id=ID_QUITTER)
        
        # Menu Paramétrage
        self.Bind(wx.EVT_MENU, self.On_param_preferences, id=ID_PARAM_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.On_param_enregistrement, id=ID_PARAM_ENREGISTREMENT)
        self.Bind(wx.EVT_MENU, self.On_param_utilisateurs, id=ID_PARAM_UTILISATEURS)
        self.Bind(wx.EVT_MENU, self.On_param_modeles_droits, id=ID_PARAM_MODELES_DROITS)
        self.Bind(wx.EVT_MENU, self.On_param_utilisateurs_reseau, id=ID_PARAM_UTILISATEURS_RESEAU)
        self.Bind(wx.EVT_MENU, self.On_param_organisateur, id=ID_PARAM_ORGANISATEUR)
        self.Bind(wx.EVT_MENU, self.On_param_comptes, id=ID_PARAM_COMPTES)
        self.Bind(wx.EVT_MENU, self.On_param_activites, id=ID_PARAM_ACTIVITES)
        self.Bind(wx.EVT_MENU, self.On_param_documents, id=ID_PARAM_DOCUMENTS)
        self.Bind(wx.EVT_MENU, self.On_param_modeles_emails, id=ID_PARAM_MODELES_EMAILS)
        self.Bind(wx.EVT_MENU, self.On_param_modeles_tickets, id=ID_PARAM_MODELES_TICKETS)
        self.Bind(wx.EVT_MENU, self.On_param_badgeage, id=ID_PARAM_BADGEAGE)
        self.Bind(wx.EVT_MENU, self.On_param_vocal, id=ID_PARAM_VOCAL)
        self.Bind(wx.EVT_MENU, self.On_param_pieces, id=ID_PARAM_PIECES)
        self.Bind(wx.EVT_MENU, self.On_param_categories_travail, id=ID_PARAM_CATEGORIES_TRAVAIL)
        self.Bind(wx.EVT_MENU, self.On_param_vacances, id=ID_PARAM_VACANCES)
        self.Bind(wx.EVT_MENU, self.On_param_feries, id=ID_PARAM_FERIES)
        self.Bind(wx.EVT_MENU, self.On_param_maladies, id=ID_PARAM_MALADIES)
        self.Bind(wx.EVT_MENU, self.On_param_vaccins, id=ID_PARAM_VACCINS)
        self.Bind(wx.EVT_MENU, self.On_param_medecins, id=ID_PARAM_MEDECINS)
        self.Bind(wx.EVT_MENU, self.On_param_restaurateurs, id=ID_PARAM_RESTAURATEURS)
        self.Bind(wx.EVT_MENU, self.On_param_modes_reglements, id=ID_PARAM_MODES_REGLEMENTS)
        self.Bind(wx.EVT_MENU, self.On_param_emetteurs, id=ID_PARAM_EMETTEURS)
        self.Bind(wx.EVT_MENU, self.On_param_banques, id=ID_PARAM_BANQUES)
        self.Bind(wx.EVT_MENU, self.On_param_lots_factures, id=ID_PARAM_LOTS_FACTURES)
        self.Bind(wx.EVT_MENU, self.On_param_lots_rappels, id=ID_PARAM_LOTS_RAPPELS)
        self.Bind(wx.EVT_MENU, self.On_param_questionnaires, id=ID_PARAM_QUESTIONNAIRES)
        self.Bind(wx.EVT_MENU, self.On_param_regimes, id=ID_PARAM_REGIMES)
        self.Bind(wx.EVT_MENU, self.On_param_caisses, id=ID_PARAM_CAISSES)
        self.Bind(wx.EVT_MENU, self.On_param_modeles_aides, id=ID_PARAM_MODELES_AIDES)
        self.Bind(wx.EVT_MENU, self.On_param_types_cotisations, id=ID_PARAM_TYPES_COTISATIONS)
        self.Bind(wx.EVT_MENU, self.On_param_groupes_activites, id=ID_PARAM_GROUPES_ACTIVITES)
        self.Bind(wx.EVT_MENU, self.On_param_villes, id=ID_PARAM_VILLES)
        self.Bind(wx.EVT_MENU, self.On_param_secteurs, id=ID_PARAM_SECTEURS)
        self.Bind(wx.EVT_MENU, self.On_param_types_sieste, id=ID_PARAM_TYPES_SIESTE)
        self.Bind(wx.EVT_MENU, self.On_param_categories_messages, id=ID_PARAM_CATEGORIES_MESSAGES)
        self.Bind(wx.EVT_MENU, self.On_param_emails_exp, id=ID_PARAM_EMAILS_EXP)
        self.Bind(wx.EVT_MENU, self.On_param_listes_diffusion, id=ID_PARAM_LISTE_DIFFUSION)
        self.Bind(wx.EVT_MENU, self.On_param_niveaux_scolaires, id=ID_PARAM_NIVEAUX_SCOLAIRES)
        self.Bind(wx.EVT_MENU, self.On_param_ecoles, id=ID_PARAM_ECOLES)
        self.Bind(wx.EVT_MENU, self.On_param_classes, id=ID_PARAM_CLASSES)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_bus, id=ID_PARAM_COMPAGNIES_BUS)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_car, id=ID_PARAM_COMPAGNIES_CAR)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_navette, id=ID_PARAM_COMPAGNIES_NAVETTE)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_taxi, id=ID_PARAM_COMPAGNIES_TAXI)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_avion, id=ID_PARAM_COMPAGNIES_AVION)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_bateau, id=ID_PARAM_COMPAGNIES_BATEAU)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_train, id=ID_PARAM_COMPAGNIES_TRAIN)
        self.Bind(wx.EVT_MENU, self.On_param_compagnies_metro, id=ID_PARAM_COMPAGNIES_METRO)
        self.Bind(wx.EVT_MENU, self.On_param_lieux_gares, id=ID_PARAM_LIEUX_GARES)
        self.Bind(wx.EVT_MENU, self.On_param_lieux_aeroports, id=ID_PARAM_LIEUX_AEROPORTS)
        self.Bind(wx.EVT_MENU, self.On_param_lieux_ports, id=ID_PARAM_LIEUX_PORTS)
        self.Bind(wx.EVT_MENU, self.On_param_lieux_stations, id=ID_PARAM_LIEUX_STATIONS)

        self.Bind(wx.EVT_MENU, self.On_param_lignes_bus, id=ID_PARAM_LIGNES_BUS)
        self.Bind(wx.EVT_MENU, self.On_param_lignes_car, id=ID_PARAM_LIGNES_CAR)
        self.Bind(wx.EVT_MENU, self.On_param_lignes_navette, id=ID_PARAM_LIGNES_NAVETTE)
        self.Bind(wx.EVT_MENU, self.On_param_lignes_bateau, id=ID_PARAM_LIGNES_BATEAU)
        self.Bind(wx.EVT_MENU, self.On_param_lignes_metro, id=ID_PARAM_LIGNES_METRO)
        self.Bind(wx.EVT_MENU, self.On_param_lignes_pedibus, id=ID_PARAM_LIGNES_PEDIBUS)
        
        self.Bind(wx.EVT_MENU, self.On_param_arrets_bus, id=ID_PARAM_ARRETS_BUS)
        self.Bind(wx.EVT_MENU, self.On_param_arrets_car, id=ID_PARAM_ARRETS_CAR)
        self.Bind(wx.EVT_MENU, self.On_param_arrets_navette, id=ID_PARAM_ARRETS_NAVETTE)
        self.Bind(wx.EVT_MENU, self.On_param_arrets_bateau, id=ID_PARAM_ARRETS_BATEAU)
        self.Bind(wx.EVT_MENU, self.On_param_arrets_metro, id=ID_PARAM_ARRETS_METRO)
        self.Bind(wx.EVT_MENU, self.On_param_arrets_pedibus, id=ID_PARAM_ARRETS_PEDIBUS)

        # Menu Affichage
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_defaut, id=ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=ID_PREMIERE_PERSPECTIVE, id2=ID_PREMIERE_PERSPECTIVE+99 )
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_save, id=ID_AFFICHAGE_PERSPECTIVE_SAVE)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_suppr, id=ID_AFFICHAGE_PERSPECTIVE_SUPPR)
        self.Bind(wx.EVT_MENU, self.On_affichage_actualiser, id=ID_AFFICHAGE_ACTUALISER)
        
        # Menu Outils
        self.Bind(wx.EVT_MENU, self.On_outils_stats, id=ID_OUTILS_STATS)
        self.Bind(wx.EVT_MENU, self.On_outils_villes, id=ID_OUTILS_VILLES)
        self.Bind(wx.EVT_MENU, self.On_outils_calculatrice, id=ID_OUTILS_CALCULATRICE)
        self.Bind(wx.EVT_MENU, self.On_outils_calendrier, id=ID_OUTILS_CALENDRIER)
        self.Bind(wx.EVT_MENU, self.On_outils_emails, id=ID_OUTILS_ENVOI_EMAILS)
        self.Bind(wx.EVT_MENU, self.On_outils_meteo, id=ID_OUTILS_METEO)
        self.Bind(wx.EVT_MENU, self.On_outils_horaires_soleil, id=ID_OUTILS_HORAIRES_SOLEIL)
        self.Bind(wx.EVT_MENU, self.On_outils_gps, id=ID_OUTILS_GPS)
        self.Bind(wx.EVT_MENU, self.On_outils_connexions, id=ID_OUTILS_CONNEXIONS) 
        self.Bind(wx.EVT_MENU, self.On_outils_messages, id=ID_OUTILS_MESSAGES)
        self.Bind(wx.EVT_MENU, self.On_outils_historique, id=ID_OUTILS_HISTORIQUE)
        self.Bind(wx.EVT_MENU, self.On_outils_correcteur, id=ID_OUTILS_CORRECTEUR)
        self.Bind(wx.EVT_MENU, self.On_outils_purger_historique, id=ID_OUTILS_PURGER_HISTORIQUE)
        self.Bind(wx.EVT_MENU, self.On_outils_purger_journal_badgeage, id=ID_OUTILS_PURGER_JOURNAL_BADGEAGE)
        self.Bind(wx.EVT_MENU, self.On_outils_purger_archives_badgeage, id=ID_OUTILS_PURGER_ARCHIVES_BADGEAGE)
        self.Bind(wx.EVT_MENU, self.On_outils_purger_rep_updates, id=ID_OUTILS_PURGER_REP_UPDATES)
        self.Bind(wx.EVT_MENU, self.On_outils_extensions, id=ID_OUTILS_EXTENSIONS)
        self.Bind(wx.EVT_MENU, self.On_outils_procedures, id=ID_OUTILS_PROCEDURES)
        self.Bind(wx.EVT_MENU, self.On_outils_procedure_e4072, id=ID_OUTILS_PROCEDURE_E4072)
        self.Bind(wx.EVT_MENU, self.On_outils_reinitialisation, id=ID_OUTILS_REINITIALISATION)
        self.Bind(wx.EVT_MENU, self.On_outils_transfert_tables, id=ID_OUTILS_TRANSFERT_TABLES)
        self.Bind(wx.EVT_MENU, self.On_outils_prestations_sans_conso, id=ID_OUTILS_PRESTATIONS_SANS_CONSO)
        self.Bind(wx.EVT_MENU, self.On_outils_conso_sans_prestations, id=ID_OUTILS_CONSO_SANS_PRESTATIONS)
        self.Bind(wx.EVT_MENU, self.On_outils_deverrouillage_forfaits, id=ID_OUTILS_DEVERROUILLAGE_FORFAITS)
        self.Bind(wx.EVT_MENU, self.On_outils_appliquer_tva, id=ID_OUTILS_APPLIQUER_TVA)
        self.Bind(wx.EVT_MENU, self.On_outils_appliquer_code_comptable, id=ID_OUTILS_APPLIQUER_CODE_COMPTABLE)
        self.Bind(wx.EVT_MENU, self.On_outils_conversion_rib_sepa, id=ID_OUTILS_CONVERSION_RIB_SEPA)
        self.Bind(wx.EVT_MENU, self.On_outils_creation_titulaires_helios, id=ID_OUTILS_CREATION_TITULAIRES_HELIOS)
        self.Bind(wx.EVT_MENU, self.On_outils_updater, id=ID_OUTILS_UPDATER) 
        self.Bind(wx.EVT_MENU, self.On_outils_console_python, id=ID_OUTILS_CONSOLE_PYTHON) 
        self.Bind(wx.EVT_MENU, self.On_outils_console_sql, id=ID_OUTILS_CONSOLE_SQL) 
        self.Bind(wx.EVT_MENU, self.On_outils_liste_perso, id=ID_OUTILS_LISTE_PERSO) 

        # Menu Individus
        self.Bind(wx.EVT_MENU, self.On_individus_scolarite, id=ID_INDIVIDUS_SCOLARITE)
        self.Bind(wx.EVT_MENU, self.On_individus_inscriptions, id=ID_INDIVIDUS_INSCRIPTIONS)
        self.Bind(wx.EVT_MENU, self.On_individus_individus, id=ID_INDIVIDUS_INDIVIDUS)
        self.Bind(wx.EVT_MENU, self.On_individus_familles, id=ID_INDIVIDUS_FAMILLES)
        self.Bind(wx.EVT_MENU, self.On_individus_transports_recap, id=ID_INDIVIDUS_TRANSPORTS_RECAP)
        self.Bind(wx.EVT_MENU, self.On_individus_transports_detail, id=ID_INDIVIDUS_TRANSPORTS_DETAIL)
        self.Bind(wx.EVT_MENU, self.On_individus_anniversaires, id=ID_INDIVIDUS_ANNIVERSAIRES)
        self.Bind(wx.EVT_MENU, self.On_individus_infos_med, id=ID_INDIVIDUS_INFOS_MED)
        self.Bind(wx.EVT_MENU, self.On_individus_pieces_fournies, id=ID_INDIVIDUS_PIECES_FOURNIES)
        self.Bind(wx.EVT_MENU, self.On_individus_pieces_manquantes, id=ID_INDIVIDUS_PIECES_MANQUANTES)
        self.Bind(wx.EVT_MENU, self.On_individus_regimes_caisses, id=ID_INDIVIDUS_REGIMES_CAISSES)
        self.Bind(wx.EVT_MENU, self.On_individus_quotients, id=ID_INDIVIDUS_QUOTIENTS)
        self.Bind(wx.EVT_MENU, self.On_individus_mandats, id=ID_INDIVIDUS_MANDATS)
        self.Bind(wx.EVT_MENU, self.On_individus_importer_photos, id=ID_INDIVIDUS_IMPORTER_PHOTOS)
        self.Bind(wx.EVT_MENU, self.On_individus_importer_csv, id=ID_INDIVIDUS_IMPORTER_CSV)
        self.Bind(wx.EVT_MENU, self.On_individus_importer_fichier, id=ID_INDIVIDUS_IMPORTER_FICHIER)
        self.Bind(wx.EVT_MENU, self.On_individus_edition_etiquettes, id=ID_INDIVIDUS_EDITION_ETIQUETTES)
        
        # Menu Règlements
        self.Bind(wx.EVT_MENU, self.On_reglements_regler_facture, id=ID_REGLEMENTS_REGLER_FACTURE)
        self.Bind(wx.EVT_MENU, self.On_reglements_recus, id=ID_REGLEMENTS_RECUS)
        self.Bind(wx.EVT_MENU, self.On_reglements_recherche, id=ID_REGLEMENTS_LISTE)
        self.Bind(wx.EVT_MENU, self.On_reglements_ventilation, id=ID_REGLEMENTS_VENTILATION)
        self.Bind(wx.EVT_MENU, self.On_reglements_analyse_ventilation, id=ID_REGLEMENTS_ANALYSE_VENTILATION)
        self.Bind(wx.EVT_MENU, self.On_reglements_synthese_modes, id=ID_REGLEMENTS_SYNTHESE_MODES)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_prelevement, id=ID_REGLEMENTS_PRELEVEMENT)
        self.Bind(wx.EVT_MENU, self.On_reglements_depots, id=ID_REGLEMENTS_DEPOTS)
        
        # Menu Cotisations
        self.Bind(wx.EVT_MENU, self.On_cotisations_recherche, id=ID_COTISATIONS_LISTE)
        self.Bind(wx.EVT_MENU, self.On_cotisations_manquantes, id=ID_COTISATIONS_MANQUANTES)
        self.Bind(wx.EVT_MENU, self.On_cotisations_depots, id=ID_COTISATIONS_DEPOTS)
        self.Bind(wx.EVT_MENU, self.On_cotisations_email, id=ID_COTISATIONS_EMAIL)
        self.Bind(wx.EVT_MENU, self.On_cotisations_imprimer, id=ID_COTISATIONS_IMPRIMER)

        # Menu Facturation
        self.Bind(wx.EVT_MENU, self.On_reglements_ventilation, id=ID_FACTURATION_VENTILATION)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_generation, id=ID_FACTURATION_FACTURES_GENERATION)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_liste, id=ID_FACTURATION_FACTURES_LISTE)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_prelevement, id=ID_FACTURATION_FACTURES_PRELEVEMENT)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_helios, id=ID_FACTURATION_FACTURES_HELIOS)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_email, id=ID_FACTURATION_FACTURES_EMAIL)
        self.Bind(wx.EVT_MENU, self.On_facturation_factures_imprimer, id=ID_FACTURATION_FACTURES_IMPRIMER)
        self.Bind(wx.EVT_MENU, self.On_facturation_rappels_generation, id=ID_FACTURATION_RAPPELS_GENERATION)
        self.Bind(wx.EVT_MENU, self.On_facturation_rappels_email, id=ID_FACTURATION_RAPPELS_EMAIL)
        self.Bind(wx.EVT_MENU, self.On_facturation_rappels_imprimer, id=ID_FACTURATION_RAPPELS_IMPRIMER)
        self.Bind(wx.EVT_MENU, self.On_facturation_rappels_liste, id=ID_FACTURATION_RAPPELS_LISTE)
        self.Bind(wx.EVT_MENU, self.On_facturation_attestations_generation, id=ID_FACTURATION_ATTESTATIONS_GENERATION) 
        self.Bind(wx.EVT_MENU, self.On_facturation_attestations_liste, id=ID_FACTURATION_ATTESTATIONS_LISTE) 
        self.Bind(wx.EVT_MENU, self.On_facturation_attestations_fiscales_generation, id=ID_FACTURATION_ATTESTATIONS_FISCALES_GENERATION) 
        self.Bind(wx.EVT_MENU, self.On_facturation_liste_prestations, id=ID_FACTURATION_LISTE_PRESTATIONS)
        self.Bind(wx.EVT_MENU, self.On_facturation_liste_deductions, id=ID_FACTURATION_LISTE_DEDUCTIONS)
        self.Bind(wx.EVT_MENU, self.On_facturation_soldes, id=ID_FACTURATION_SOLDES)
        self.Bind(wx.EVT_MENU, self.On_facturation_soldes_individuels, id=ID_FACTURATION_SOLDES_INDIVIDUELS)
        self.Bind(wx.EVT_MENU, self.On_facturation_solder_impayes, id=ID_FACTURATION_SOLDER_IMPAYES)
        self.Bind(wx.EVT_MENU, self.On_facturation_prestations_villes, id=ID_FACTURATION_PRESTATIONS_VILLES)
        self.Bind(wx.EVT_MENU, self.On_facturation_synthese_prestations, id=ID_FACTURATION_SYNTHESE_PRESTATIONS)
        self.Bind(wx.EVT_MENU, self.On_facturation_synthese_impayes, id=ID_FACTURATION_SYNTHESE_IMPAYES)
        self.Bind(wx.EVT_MENU, self.On_facturation_export_compta, id=ID_FACTURATION_EXPORT_COMPTA)
        
        # Menu Consommations
        self.Bind(wx.EVT_MENU, self.On_imprim_conso_journ, id=ID_IMPRIM_LISTE_CONSO_JOURN)
        self.Bind(wx.EVT_MENU, self.On_conso_gestionnaire, id=ID_CONSO_GESTIONNAIRE)
        self.Bind(wx.EVT_MENU, self.On_conso_attente, id=ID_CONSO_ATTENTE)
        self.Bind(wx.EVT_MENU, self.On_conso_refus, id=ID_CONSO_REFUS)
        self.Bind(wx.EVT_MENU, self.On_conso_absences, id=ID_CONSO_ABSENCES)
        self.Bind(wx.EVT_MENU, self.On_conso_synthese_conso, id=ID_CONSO_SYNTHESE_CONSO)
        self.Bind(wx.EVT_MENU, self.On_conso_etat_global, id=ID_CONSO_ETAT_GLOBAL)
        self.Bind(wx.EVT_MENU, self.On_conso_etat_nominatif, id=ID_CONSO_ETAT_NOMINATIF)
        self.Bind(wx.EVT_MENU, self.On_conso_badgeage, id=ID_CONSO_BADGEAGE)

        # Menu Aide
        self.Bind(wx.EVT_MENU, self.On_aide_aide, id=ID_AIDE_AIDE)
        self.Bind(wx.EVT_MENU, self.On_propos_soutenir, id=ID_AIDE_ACHETER_LICENCE)
        self.Bind(wx.EVT_MENU, self.On_aide_guide_demarrage, id=ID_AIDE_GUIDE_DEMARRAGE)
        self.Bind(wx.EVT_MENU, self.On_aide_forum, id=ID_AIDE_FORUM)
        self.Bind(wx.EVT_MENU, self.On_aide_videos, id=ID_AIDE_VIDEOS)
        self.Bind(wx.EVT_MENU, self.On_aide_telechargements, id=ID_AIDE_TELECHARGEMENTS)
        self.Bind(wx.EVT_MENU, self.On_aide_auteur, id=ID_AIDE_AUTEUR)
        
        # Menu A propos
        self.Bind(wx.EVT_MENU, self.On_propos_versions, id=ID_PROPOS_VERSIONS)
        self.Bind(wx.EVT_MENU, self.On_propos_licence, id=ID_PROPOS_LICENCE)
        self.Bind(wx.EVT_MENU, self.On_propos_soutenir, id=ID_PROPOS_SOUTENIR)
        self.Bind(wx.EVT_MENU, self.On_propos_propos, id=ID_PROPOS_PROPOS)
        
        # Autres
        self.Bind(wx.EVT_MENU_OPEN, self.MAJmenuAffichage)
        
        # Barre d'outils
        self.Bind(wx.EVT_TOOL, self.On_conso_gestionnaire, id=ID_TB_GESTIONNAIRE)
        self.Bind(wx.EVT_TOOL, self.On_imprim_conso_journ, id=ID_TB_LISTE_CONSO)
        self.Bind(wx.EVT_TOOL, self.On_conso_badgeage, id=ID_TB_BADGEAGE)
        self.Bind(wx.EVT_TOOL, self.On_reglements_regler_facture, id=ID_TB_REGLER_FACTURE)
        self.Bind(wx.EVT_TOOL, self.On_outils_calculatrice, id=ID_TB_CALCULATRICE)
        
    def MAJ(self):
        """ Met à jour la page d'accueil """
        self.ctrl_remplissage.MAJ() 
        self.ctrl_individus.MAJ()
        self.ctrl_messages.MAJ() 
        wx.CallAfter(self.ctrl_individus.ctrl_recherche.SetFocus)
##        self.ctrl_individus.ctrl_recherche.SetFocus()

    def On_fichier_AssistantDemarrage(self, event):
        print "ok"

    def On_fichier_Nouveau(self, event):
        """ Créé une nouvelle base de données """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_fichier", "creer") == False : return
        # Demande le nom du fichier
        import DLG_Nouveau_fichier
        import DATA_Tables as Tables
        dlg = DLG_Nouveau_fichier.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            modeFichier = dlg.GetMode() 
            nomFichier = dlg.GetNomFichier()
            listeTables = dlg.GetListeTables()
            dictAdministrateur = dlg.GetIdentiteAdministrateur() 
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # Affiche d'une fenêtre d'attente
        message = u"Création du nouveau fichier en cours... Veuillez patienter..."
        dlgAttente = PBI.PyBusyInfo(message, parent=None, title=u"Création d'un fichier", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
            
        if "[RESEAU]" in nomFichier :
            self.SetStatusText(u"Création du fichier '%s' en cours..." % nomFichier[nomFichier.index("[RESEAU]"):])
        else:
            self.SetStatusText(u"Création du fichier '%s' en cours..." % nomFichier)
        
        # Vérification de validité du fichier
        if nomFichier == "" :
            del dlgAttente
            dlg = wx.MessageDialog(self, u"Le nom que vous avez saisi n'est pas valide !", "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(u"Echec de la création du fichier '%s' : nom du fichier non valide." % nomFichier)
            return False

        if "[RESEAU]" not in nomFichier :
            # Version LOCAL
            
            # Vérifie si un fichier ne porte pas déjà ce nom :
            fichier = "Data/" + nomFichier + "_DATA.dat"
            test = os.path.isfile(fichier) 
            if test == True :
                del dlgAttente
                dlg = wx.MessageDialog(self, u"Vous possédez déjà un fichier qui porte le nom '" + nomFichier + u"'.\n\nVeuillez saisir un autre nom.", "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.SetStatusText(u"Echec de la création du fichier '%s' : Le nom existe déjà." % nomFichier)
                return False
        
        else:
            # Version RESEAU
            dictResultats = GestionDB.TestConnexionMySQL(typeTest="fichier", nomFichier=u"%s_DATA" % nomFichier)
            
            # Vérifie la connexion au réseau
            if dictResultats["connexion"][0] == False :
                del dlgAttente
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, u"La connexion au réseau MySQL est impossible. \n\nErreur : %s" % erreur, u"Erreur de connexion", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            # Vérifie que le fichier n'est pas déjà utilisé
            if dictResultats["fichier"][0] == True and modeFichier != "internet" :
                del dlgAttente
                dlg = wx.MessageDialog(self, u"Le fichier existe déjà.", u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        ancienFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = nomFichier 
        
        # Création de la base DATA
        DB = GestionDB.DB(suffixe="DATA", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier de données.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(u"Création des tables de données...")
        DB.CreationTables(Tables.DB_DATA, fenetreParente=self)
        self.SetStatusText(u"Importation des données par défaut...")
        DB.Importation_valeurs_defaut(listeTables)
        DB.Close()
        
        # Création de la base PHOTOS
        if modeFichier != "internet" :
            DB = GestionDB.DB(suffixe="PHOTOS", modeCreation=True)
            if DB.echec == 1 :
                del dlgAttente
                erreur = DB.erreur
                dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier de photos.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.userConfig["nomFichier"] = ancienFichier 
                return False
            self.SetStatusText(u"Création de la table de données des photos...")
            DB.CreationTables(Tables.DB_PHOTOS)
            DB.Close()
        
        # Création de la base DOCUMENTS
        if modeFichier != "internet" :
            DB = GestionDB.DB(suffixe="DOCUMENTS", modeCreation=True)
            if DB.echec == 1 :
                del dlgAttente
                erreur = DB.erreur
                dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier de documents.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.userConfig["nomFichier"] = ancienFichier 
                return False
            self.SetStatusText(u"Création de la table de données des documents...")
            DB.CreationTables(Tables.DB_DOCUMENTS)
            DB.Close()
                
        # Créé un identifiant unique pour ce fichier
        self.SetStatusText(u"Création des informations sur le fichier...")
        d = datetime.datetime.now()
        IDfichier = d.strftime("%Y%m%d%H%M%S")
        for x in range(0, 3) :
            IDfichier += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        
        # Mémorisation des informations sur le fichier
        listeDonnees = [
            ( "date_creation", str(datetime.date.today()) ),
            ( "version", VERSION_APPLICATION ),
            ( "IDfichier", IDfichier ),
            ]
        DB = GestionDB.DB()
        for nom, valeur in listeDonnees :
            donnees = [("categorie",  "fichier"), ("nom",  nom), ("parametre",  valeur),]
            DB.ReqInsert("parametres", donnees)
        DB.Close()
                
        # Sauvegarde et chargement de l'identité Administrateur
        self.SetStatusText(u"Création de l'identité administrateur...")
        DB = GestionDB.DB()
        listeDonnees = [    
                ("sexe", dictAdministrateur["sexe"]),
                ("nom", dictAdministrateur["nom"]),
                ("prenom", dictAdministrateur["prenom"]),
                ("mdp", dictAdministrateur["mdp"]),
                ("profil", dictAdministrateur["profil"]),
                ("actif", dictAdministrateur["actif"]),
                ("image", dictAdministrateur["image"]),
            ]
        IDutilisateur = DB.ReqInsert("utilisateurs", listeDonnees)
        DB.Close()
        
        # Chargement liste utilisateurs
        self.listeUtilisateurs = self.GetListeUtilisateurs() 
        self.ChargeUtilisateur(IDutilisateur=IDutilisateur)
        
        # Met à jour l'affichage des panels
        self.MAJ()
        self.SetTitleFrame(nomFichier=nomFichier)
        self.ctrl_ephemeride.Initialisation()
        
        # Récupération de la perspective chargée
        if self.perspective_active != None :
            self._mgr.LoadPerspective(self.perspectives[self.perspective_active]["perspective"])
            self.ForcerAffichagePanneau("ephemeride")
        else:
            self._mgr.LoadPerspective(self.perspective_defaut)

        # Active les items de la barre de menus
        self.ActiveBarreMenus(True) 

        # Met à jour la liste des derniers fichiers de la barre des menus
        self.MAJlisteDerniersFichiers(nomFichier)
        
        # Met à jour le menu
        self.MAJmenuDerniersFichiers()
                
        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)
        
        # Boîte de dialogue pour confirmer la création
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        
        # Fermeture de la fenêtre d'attente
        del dlgAttente
        
        # Affichage d'un confirmation de succès de la création
        self.SetStatusText(u"Le fichier '%s' a été créé avec succès." % nomFichier)
        dlg = wx.MessageDialog(self, u"Le fichier '" + nomFichier + u"' a été créé avec succès.\n\nVous devez maintenant renseigner les informations concernant l'organisateur.", u"Création d'un fichier", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        # Demande de remplir les infos sur l'organisateur
        self.SetStatusText(u"Paramétrage des informations sur l'organisateur...")
        import DLG_Organisateur
        dlg = DLG_Organisateur.Dialog(self, empecheAnnulation=True)
        dlg.ShowModal()
        dlg.Destroy()
        
        self.SetStatusText(u"")
            

    def On_fichier_Ouvrir(self, event):
        """ Ouvrir un fichier """    
        # Boîte de dialogue pour demander le nom du fichier à ouvrir
        fichierOuvert = self.userConfig["nomFichier"]
        import DLG_Ouvrir_fichier
        dlg = DLG_Ouvrir_fichier.MyDialog(self, fichierOuvert=fichierOuvert)
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetNomFichier()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Ouverture du fichier
        self.OuvrirFichier(nomFichier)

    def On_fichier_Fermer(self, event):
        """ Fermer le fichier ouvert """
        self.Fermer() 
    
    def Fermer(self, sauvegarde_auto=True):
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "" :
            dlg = wx.MessageDialog(self, u"Il n'y a aucun fichier à fermer !", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Mémorise l'action dans l'historique
        UTILS_Historique.InsertActions([{"IDcategorie" : 1, "action" : u"Fermeture du fichier"},])
        
        # Sauvegarde automatique
        if sauvegarde_auto == True :
            resultat = self.SauvegardeAutomatique() 
            if resultat == wx.ID_CANCEL :
                return
        
        # change le nom de fichier
        self.userConfig["nomFichier"] = ""
        self.SetTitleFrame()
        
        # Cache tous les panneaux
        for pane in self._mgr.GetAllPanes() :
            if pane.name != "accueil" :
                pane.Hide()
        self._mgr.GetPane("accueil").Show().Maximize()
        self._mgr.Update()
            
        # Active les items de la barre de menus
        self.ActiveBarreMenus(False) 

        # Désactive la commande FERMER du menu Fichier
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindItemById(ID_FERMER_FICHIER)
        menuItem.Enable(False)
        menuItem = menuBar.FindItemById(ID_FICHIER_INFORMATIONS)
        menuItem.Enable(False) 
        menuItem = menuBar.FindItemById(ID_CONVERSION_RESEAU)
        menuItem.Enable(False) 
        menuItem = menuBar.FindItemById(ID_CONVERSION_LOCAL)
        menuItem.Enable(False) 


    def On_fichier_Informations(self, event):
        """ Fichier : Informations sur le fichier """
        import DLG_Infos_fichier
        dlg = DLG_Infos_fichier.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_fichier_Sauvegarder(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_sauvegarde_manuelle", "creer") == False : return
        import DLG_Sauvegarde
        dlg = DLG_Sauvegarde.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_fichier_Restaurer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_restauration", "creer") == False : return
        import DLG_Restauration
        fichier = DLG_Restauration.SelectionFichier()
        if fichier != None :
            listeFichiersRestaures = []
            dlg = DLG_Restauration.Dialog(self, fichier=fichier)
            if dlg.ShowModal() == wx.ID_OK :
                listeFichiersRestaures = dlg.GetFichiersRestaures()
            dlg.Destroy()
            # Ferme le fichier ouvert si c'est celui-ci qui est restauré
            nomFichier = self.userConfig["nomFichier"]
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
            if nomFichier in listeFichiersRestaures :
                dlg = wx.MessageDialog(self, u"Redémarrage du fichier restauré.\n\nAfin de finaliser la restauration, le fichier de données ouvert va être fermé puis ré-ouvert.", u"Redémarrage du fichier restauré", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.Fermer(sauvegarde_auto=False) 
                self.OuvrirDernierFichier() 

    def On_fichier_Sauvegardes_auto(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_sauvegardes_auto", "consulter") == False : return
        import DLG_Sauvegardes_auto
        dlg = DLG_Sauvegardes_auto.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_fichier_Convertir_reseau(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_conversions", "creer") == False : return
        nomFichier = self.userConfig["nomFichier"]
        import UTILS_Conversion_fichier
        resultat = UTILS_Conversion_fichier.ConversionLocalReseau(self, nomFichier)
        print "Succes de la procedure : ", resultat

    def On_fichier_Convertir_local(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_conversions", "creer") == False : return
        nomFichier = self.userConfig["nomFichier"]
        import UTILS_Conversion_fichier
        resultat = UTILS_Conversion_fichier.ConversionReseauLocal(self, nomFichier)
        print "Succes de la procedure : ", resultat

    def On_fichier_Quitter(self, event):
        if self.Quitter() == False :
            return
        self.Destroy()
    
    def On_fichier_DerniersFichiers(self, event):
        """ Ouvre un des derniers fichiers ouverts """
        idMenu = event.GetId()
        nomFichier = self.userConfig["derniersFichiers"][idMenu - ID_DERNIER_FICHIER]
        self.OuvrirFichier(nomFichier)

    def On_param_preferences(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_preferences", "consulter") == False : return
        import DLG_Preferences
        dlg = DLG_Preferences.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_enregistrement(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_enregistrement", "consulter") == False : return
        import DLG_Enregistrement
        dlg = DLG_Enregistrement.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_utilisateurs(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs", "consulter") == False : return
        import DLG_Utilisateurs
        dlg = DLG_Utilisateurs.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.listeUtilisateurs = self.GetListeUtilisateurs()
        self.RechargeUtilisateur() 

    def On_param_modeles_droits(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_droits", "consulter") == False : return
        import DLG_Droits
        dlg = DLG_Droits.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.listeUtilisateurs = self.GetListeUtilisateurs()
        self.RechargeUtilisateur() 

    def On_param_utilisateurs_reseau(self, event):
        if "[RESEAU]" not in self.userConfig["nomFichier"] :
            dlg = wx.MessageDialog(self, u"Cette fonction n'est accessible que si vous utilisez un fichier réseau !", u"Accès non autorisé", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs_reseau", "consulter") == False : return
        import DLG_Utilisateurs_reseau
        dlg = DLG_Utilisateurs_reseau.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_param_organisateur(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_organisateur", "consulter") == False : return
        import DLG_Organisateur
        dlg = DLG_Organisateur.Dialog(self)
        dlg.ShowModal() 
        try :
            dlg.Destroy()
        except :
            pass
        self.ctrl_ephemeride.Initialisation()

    def On_param_groupes_activites(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_groupes_activites", "consulter") == False : return
        import DLG_Groupes_activites
        dlg = DLG_Groupes_activites.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_activites(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "consulter") == False : return
        import DLG_Activites
        dlg = DLG_Activites.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_remplissage.MAJ() 

    def On_param_documents(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "consulter") == False : return
        import DLG_Modeles_docs
        dlg = DLG_Modeles_docs.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_modeles_emails(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_emails", "consulter") == False : return
        import DLG_Modeles_emails
        dlg = DLG_Modeles_emails.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_modeles_tickets(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_tickets", "consulter") == False : return
        import DLG_Modeles_tickets
        dlg = DLG_Modeles_tickets.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_badgeage(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_procedures_badgeage", "consulter") == False : return
        import DLG_Badgeage_procedures
        dlg = DLG_Badgeage_procedures.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_vocal(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vocal", "consulter") == False : return
        import DLG_Vocal
        dlg = DLG_Vocal.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_categories_messages(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_messages", "consulter") == False : return
        import DLG_Categories_messages
        dlg = DLG_Categories_messages.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_messages.MAJ() 
        
    def On_param_pieces(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_types_pieces", "consulter") == False : return
        import DLG_Types_pieces
        dlg = DLG_Types_pieces.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_param_categories_travail(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_travail", "consulter") == False : return
        import DLG_Categories_travail
        dlg = DLG_Categories_travail.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_villes(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_villes", "consulter") == False : return
        import DLG_Villes
        dlg = DLG_Villes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_secteurs(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_secteurs", "consulter") == False : return
        import DLG_Secteurs
        dlg = DLG_Secteurs.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_types_sieste(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_types_siestes", "consulter") == False : return
        import DLG_Types_sieste
        dlg = DLG_Types_sieste.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_vacances(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vacances", "consulter") == False : return
        import DLG_Vacances
        dlg = DLG_Vacances.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_remplissage.MAJ() 

    def On_param_feries(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_feries", "consulter") == False : return
        import DLG_Feries
        dlg = DLG_Feries.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_remplissage.MAJ() 
            
    def On_param_maladies(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_maladies", "consulter") == False : return
        import DLG_Types_maladies
        dlg = DLG_Types_maladies.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_vaccins(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vaccins", "consulter") == False : return
        import DLG_Types_vaccins
        dlg = DLG_Types_vaccins.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_param_medecins(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_medecins", "consulter") == False : return
        import DLG_Medecins
        dlg = DLG_Medecins.Dialog(self, mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_restaurateurs(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_restaurateurs", "consulter") == False : return
        import DLG_Restaurateurs
        dlg = DLG_Restaurateurs.Dialog(self, mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_comptes(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_comptes_bancaires", "consulter") == False : return
        import DLG_Comptes_bancaires
        dlg = DLG_Comptes_bancaires.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_modes_reglements(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modes_reglements", "consulter") == False : return
        import DLG_Modes_reglements
        dlg = DLG_Modes_reglements.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_emetteurs(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emetteurs", "consulter") == False : return
        import DLG_Emetteurs
        dlg = DLG_Emetteurs.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_banques(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_banques", "consulter") == False : return
        import DLG_Banques
        dlg = DLG_Banques.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lots_factures(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lots_factures", "consulter") == False : return
        import DLG_Lots_factures
        dlg = DLG_Lots_factures.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lots_rappels(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lots_rappels", "consulter") == False : return
        import DLG_Lots_rappels
        dlg = DLG_Lots_rappels.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_regimes(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_regimes", "consulter") == False : return
        import DLG_Regimes
        dlg = DLG_Regimes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_caisses(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_caisses", "consulter") == False : return
        import DLG_Caisses
        dlg = DLG_Caisses.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_modeles_aides(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_aides", "consulter") == False : return
        import DLG_Modeles_aides
        dlg = DLG_Modeles_aides.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_types_cotisations(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_types_cotisations", "consulter") == False : return
        import DLG_Types_cotisations
        dlg = DLG_Types_cotisations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_emails_exp(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emails_exp", "consulter") == False : return
        import DLG_Emails_exp
        dlg = DLG_Emails_exp.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_listes_diffusion(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_listes_diffusion", "consulter") == False : return
        import DLG_Listes_diffusion
        dlg = DLG_Listes_diffusion.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_param_questionnaires(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_questionnaires", "consulter") == False : return
        import DLG_Questionnaires
        dlg = DLG_Questionnaires.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_niveaux_scolaires(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_niveaux_scolaires", "consulter") == False : return
        import DLG_Niveaux_scolaires
        dlg = DLG_Niveaux_scolaires.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_ecoles(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_ecoles", "consulter") == False : return
        import DLG_Ecoles
        dlg = DLG_Ecoles.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_classes(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_classes", "consulter") == False : return
        import DLG_Classes
        dlg = DLG_Classes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_bus(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="bus", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_car(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="car", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_navette(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="navette", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_taxi(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="taxi", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_avion(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="avion", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_bateau(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="bateau", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_train(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="train", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_compagnies_metro(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_compagnies", "consulter") == False : return
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie="metro", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lieux_gares(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lieux", "consulter") == False : return
        import DLG_Lieux
        dlg = DLG_Lieux.Dialog(self, categorie="gare", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lieux_aeroports(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lieux", "consulter") == False : return
        import DLG_Lieux
        dlg = DLG_Lieux.Dialog(self, categorie="aeroport", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lieux_ports(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lieux", "consulter") == False : return
        import DLG_Lieux
        dlg = DLG_Lieux.Dialog(self, categorie="port", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lieux_stations(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lieux", "consulter") == False : return
        import DLG_Lieux
        dlg = DLG_Lieux.Dialog(self, categorie="station", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lignes_bus(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lignes", "consulter") == False : return
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie="bus", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lignes_car(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lignes", "consulter") == False : return
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie="car", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_param_lignes_navette(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lignes", "consulter") == False : return
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie="navette", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lignes_bateau(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lignes", "consulter") == False : return
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie="bateau", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lignes_metro(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lignes", "consulter") == False : return
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie="metro", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_lignes_pedibus(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_lignes", "consulter") == False : return
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie="pedibus", mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_arrets_bus(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "consulter") == False : return
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie="bus")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_arrets_navette(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "consulter") == False : return
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie="navette")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_arrets_car(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "consulter") == False : return
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie="car")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_arrets_bateau(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "consulter") == False : return
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie="bateau")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_arrets_metro(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "consulter") == False : return
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie="metro")
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_arrets_pedibus(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_arrets", "consulter") == False : return
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie="pedibus")
        dlg.ShowModal() 
        dlg.Destroy()

    def MAJmenuPerspectives(self):
        
        # Supprime les perspectives perso dans le menu
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindItemById(ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        menu_affichage = menuItem.GetMenu()
        item = menu_affichage.FindItemById(ID_PREMIERE_PERSPECTIVE)
        for index in range(0, 99) :
            ID = ID_PREMIERE_PERSPECTIVE + index
            item = menu_affichage.FindItemById(ID)
            if item == None : break
            menu_affichage.Remove(ID)
            self.Disconnect(ID, -1, 10014) 
                            
        # Décoche la disposition par défaut si nécessaire
        item = menuBar.FindItemById(ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        if self.perspective_active == None : 
            item.Check(True)
        else:
            item.Check(False)
            
        # Crée les entrées perspectives dans le menu :
        index = 0
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menu_affichage, ID_PREMIERE_PERSPECTIVE+index, label, u"Afficher la disposition '%s'" % label, wx.ITEM_CHECK)
            menu_affichage.InsertItem(index+1, item)
            if self.perspective_active == index : item.Check(True)
            index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=ID_PREMIERE_PERSPECTIVE, id2=ID_PREMIERE_PERSPECTIVE+99 )
    
    def On_affichage_perspective_defaut(self, event):
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None
        self.MAJmenuPerspectives() 

    def On_affichage_perspective_perso(self, event):
        index = event.GetId() - ID_PREMIERE_PERSPECTIVE
        self._mgr.LoadPerspective(self.perspectives[index]["perspective"])
        self.perspective_active = index
        self.ForcerAffichagePanneau("ephemeride")
        self.MAJmenuPerspectives() 

    def On_affichage_perspective_save(self, event):
        newIDperspective = len(self.perspectives)
        dlg = wx.TextEntryDialog(self, u"Veuillez saisir un intitulé pour cette disposition :", "Sauvegarde d'une disposition")
        dlg.SetValue(u"Disposition %d" % (newIDperspective + 1))
        reponse = dlg.ShowModal()
        if reponse != wx.ID_OK:
            dlg.Destroy() 
            return
        label = dlg.GetValue()
        dlg.Destroy() 
        
        # Vérifie que ce nom n'est pas déjà attribué
        for dictPerspective in self.perspectives:
            if label == dictPerspective["label"] :
                dlg = wx.MessageDialog(self, u"Ce nom est déjà attribué à une autre disposition !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Sauvegarde de la perspective
        self.perspectives.append( {"label" : label, "perspective" : self._mgr.SavePerspective() } )
        self.perspective_active = newIDperspective
        
        # MAJ Menu Affichage
        self.MAJmenuPerspectives() 
        
        
    def On_affichage_perspective_suppr(self, event):
        listeLabels = []
        for dictPerspective in self.perspectives :
            listeLabels.append(dictPerspective["label"])
        dlg = wx.MultiChoiceDialog( self, u"Cochez les dispositions que vous souhaitez supprimer :", u"Supprimer des dispositions", listeLabels)
        if dlg.ShowModal() == wx.ID_OK :
            selections = dlg.GetSelections()
            selections.sort(reverse=True)
            for index in selections :
                self.perspectives.pop(index)
            if self.perspective_active in selections :
                self._mgr.LoadPerspective(self.perspective_defaut)
            self.perspective_active = None
            self.MAJmenuPerspectives() 
        dlg.Destroy()
    
    def On_affichage_panneau_afficher(self, event):
        index = event.GetId() - ID_AFFICHAGE_PANNEAUX
        panneau = self._mgr.GetPane(self.listePanneaux[index]["code"])
        if panneau.IsShown() :
            panneau.Hide()
        else:
            panneau.Show()
        self._mgr.Update()
    
    def On_affichage_actualiser(self, event):
        self.MAJ() 

    def On_outils_stats(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_stats", "consulter") == False : return
        import DLG_Stats
        dlg = DLG_Stats.Dialog(self)
        if dlg.ModificationParametres(premiere=True) == True :
            dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_villes(self, event):
        import DLG_Villes
        dlg = DLG_Villes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_calculatrice(self, event):
        FonctionsPerso.OuvrirCalculatrice() 

    def On_outils_calendrier(self, event):
        import DLG_Calendrier
        dlg = DLG_Calendrier.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_meteo(self, event):
        dlg = wx.MessageDialog(self, u"Cette fonction n'est plus accessible pour le moment car Noethys utilisait une API Météo que Google vient de supprimer définitivement. Je dois donc prendre le temps de trouver une API équivalente.\n\nMerci de votre compréhension.\n\nIvan", u"Fonction indisponible", wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
##        import DLG_Meteo
##        dlg = DLG_Meteo.Dialog(self)
##        dlg.ShowModal() 
##        dlg.Destroy()

    def On_outils_horaires_soleil(self, event):
        import DLG_Horaires_soleil
        dlg = DLG_Horaires_soleil.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_gps(self, event):
        import DLG_Geolocalisation
        dlg = DLG_Geolocalisation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def On_outils_emails(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_editeur_emails", "consulter") == False : return
        import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_outils_connexions(self, event):
        """ Connexions réseau """
        if "[RESEAU]" not in self.userConfig["nomFichier"] :
            dlg = wx.MessageDialog(self, u"Cette fonction n'est accessible que si vous utilisez un fichier réseau !", u"Accès non autorisé", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import DLG_Connexions
        dlg = DLG_Connexions.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_messages(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_messages", "consulter") == False : return
        import DLG_Liste_messages
        dlg = DLG_Liste_messages.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_messages.MAJ() 

    def On_outils_historique(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_historique", "consulter") == False : return
        import DLG_Historique
        dlg = DLG_Historique.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_correcteur(self, event):
        """ Purger l'historique """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Depannage
        dlg = DLG_Depannage.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_purger_historique(self, event):
        """ Purger l'historique """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Purge_Historique
        dlg = DLG_Purge_Historique.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_purger_journal_badgeage(self, event):
        """ Purger le journal de badgeage """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import OL_Badgeage_log
        OL_Badgeage_log.Purger() 

    def On_outils_purger_archives_badgeage(self, event):
        """ Purger les archives de badgeage importés """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Badgeage_importation
        DLG_Badgeage_importation.Purger() 

    def On_outils_purger_rep_updates(self, event):
        """ Purger le répertoire Updates """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment purger le répertoire Updates ?", u"Purger", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            FonctionsPerso.VideRepertoireUpdates(forcer=True) 
        dlg.Destroy()

    def On_outils_extensions(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Extensions
        UTILS_Extensions.Extensions()

    def On_outils_procedures(self, event):
        """ Commande spéciale """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Procedures
        dlg = wx.TextEntryDialog(self, u"Entrez le code de procédure qui vous été communiqué :", u"Procédure", "")
        if dlg.ShowModal() == wx.ID_OK:
            code = dlg.GetValue()
            UTILS_Procedures.Procedure(code)
        dlg.Destroy()
    
    def On_outils_procedure_e4072(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Procedures
        UTILS_Procedures.E4072()

    def On_outils_creation_titulaires_helios(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Procedures
        UTILS_Procedures.A7650()

    def On_outils_reinitialisation(self, event):
        """ Réinitialisation du fichier de configuration """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        message = u"Pour réinitialiser votre fichier configuration, vous devez quitter Noethys et le relancer en conservant la touche ALT gauche de votre clavier enfoncée.\n\nCette fonctionnalité est sans danger : Seront par exemple réinitialisés la liste des derniers fichiers ouverts, les périodes de références, les affichages personnalisés, etc..."
        dlg = wx.MessageDialog(self, message, u"Réinitialisation", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_transfert_tables(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Transfert_tables
        dlg = DLG_Transfert_tables.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_prestations_sans_conso(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Prestations_sans_conso
        dlg = DLG_Prestations_sans_conso.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_conso_sans_prestations(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Conso_sans_prestations
        dlg = DLG_Conso_sans_prestations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_deverrouillage_forfaits(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Deverrouillage_forfaits
        dlg = DLG_Deverrouillage_forfaits.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_appliquer_tva(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Appliquer_tva
        UTILS_Appliquer_tva.Appliquer()

    def On_outils_appliquer_code_comptable(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Appliquer_code_compta
        UTILS_Appliquer_code_compta.Appliquer()

    def On_outils_conversion_rib_sepa(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Transfert_RIB
        dlg = DLG_Transfert_RIB.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_console_python(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Console_python
        dlg = DLG_Console_python.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_console_sql(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Console_sql
        dlg = DLG_Console_sql.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_liste_perso(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Liste_perso
        dlg = DLG_Liste_perso.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_updater(self, event):
        """Mises à jour internet """
        import DLG_Updater
        dlg = DLG_Updater.Dialog(self)
        dlg.ShowModal() 
        installation = dlg.GetEtat() 
        dlg.Destroy()
        if installation == True :
            self.Quitter(videRepertoiresTemp=False, sauvegardeAuto=False)
            sleep(2)
            self.Destroy()

    def On_reglements_regler_facture(self, event):
        dlg = CTRL_Numfacture.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_reglements_recus(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("reglements_recus", "consulter") == False : return
        import DLG_Liste_recus
        dlg = DLG_Liste_recus.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_reglements_recherche(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("reglements_liste", "consulter") == False : return
        import DLG_Liste_reglements
        dlg = DLG_Liste_reglements.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_reglements_ventilation(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_ventilation", "consulter") == False : return
        import DLG_Verification_ventilation
        dlg = DLG_Verification_ventilation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_reglements_analyse_ventilation(self, event):
        # Vérification de la ventilation
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_ventilation", "consulter") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Synthese_ventilation
        dlg = DLG_Synthese_ventilation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_reglements_synthese_modes(self, event):
        # Vérification de la ventilation
        if self.VerificationVentilation() == False : return
        import DLG_Synthese_modes_reglements
        dlg = DLG_Synthese_modes_reglements.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_reglements_depots(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("reglements_depots", "consulter") == False : return
        import DLG_Depots
        dlg = DLG_Depots.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def On_facturation_attestations(self, event):
        import DLG_Liste_attestations
        dlg = DLG_Liste_attestations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def VerificationVentilation(self):
        # Vérification de la ventilation
        import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification()
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, u"Un ou plusieurs règlements peuvent être ventilés.\n\nSouhaitez-vous le faire maintenant (conseillé) ?", u"Ventilation", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                dlg = DLG_Verification_ventilation.Dialog(self) #, tracks=tracks)
                dlg.ShowModal() 
                dlg.Destroy()
            if reponse == wx.ID_CANCEL :
                return False
        return True

    def On_facturation_factures_generation(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Factures_generation
        dlg = DLG_Factures_generation.Dialog(self)
        dlg.ShowModal() 
        try : dlg.Destroy()
        except : pass
        
    def On_facturation_factures_liste(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_factures", "consulter") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Liste_factures
        dlg = DLG_Liste_factures.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_facturation_factures_prelevement(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_prelevements", "consulter") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Lots_prelevements
        dlg = DLG_Lots_prelevements.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_factures_helios(self, event):
        if self.VerificationVentilation() == False : return
        import UTILS_Pes
        choix = UTILS_Pes.DemanderChoix(self)
        
        if choix == "rolmre" :
            import DLG_Export_helios
            dlg = DLG_Export_helios.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()

        if choix == "pes" :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "consulter") == False : return
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "creer") == False : return
            import DLG_Lots_pes
            dlg = DLG_Lots_pes.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()

    def On_facturation_factures_email(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Factures_email
        dlg = DLG_Factures_email.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_factures_imprimer(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Factures_impression
        dlg = DLG_Factures_impression.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_rappels_generation(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Rappels_generation
        dlg = DLG_Rappels_generation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_rappels_email(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Rappels_email
        dlg = DLG_Rappels_email.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_rappels_imprimer(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Rappels_impression
        dlg = DLG_Rappels_impression.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_rappels_liste(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_rappels", "consulter") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Liste_rappels
        dlg = DLG_Liste_rappels.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_attestations_generation(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_attestations", "creer") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Attestations_annuelles
        dlg = DLG_Attestations_annuelles.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_attestations_liste(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_attestations", "consulter") == False : return
        import DLG_Liste_attestations
        dlg = DLG_Liste_attestations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_attestations_fiscales_generation(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_attestations", "creer") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Attestations_fiscales_generation
        dlg = DLG_Attestations_fiscales_generation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_liste_prestations(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Liste_prestations
        dlg = DLG_Liste_prestations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_liste_deductions(self, event):
        import DLG_Liste_deductions
        dlg = DLG_Liste_deductions.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_soldes(self, event):
        if self.VerificationVentilation() == False :
            return
        import DLG_Soldes
        dlg = DLG_Soldes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_soldes_individuels(self, event):
        if self.VerificationVentilation() == False :
            return
        import DLG_Liste_nominative_soldes
        dlg = DLG_Liste_nominative_soldes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_solder_impayes(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_solder_impayes", "creer") == False : return
        if self.VerificationVentilation() == False :
            return
        import DLG_Solder_impayes
        dlg = DLG_Solder_impayes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_prestations_villes(self, event):
        if self.VerificationVentilation() == False :
            return
        import DLG_Liste_prestations_villes
        dlg = DLG_Liste_prestations_villes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_synthese_prestations(self, event):
        if self.VerificationVentilation() == False :
            return
        import DLG_Synthese_prestations
        dlg = DLG_Synthese_prestations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_synthese_impayes(self, event):
        if self.VerificationVentilation() == False :
            return
        import DLG_Synthese_impayes
        dlg = DLG_Synthese_impayes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_export_compta(self, event):
        if self.VerificationVentilation() == False :
            return
        import DLG_Export_compta
        dlg = DLG_Export_compta.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_cotisations_recherche(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("cotisations_liste", "consulter") == False : return
        import DLG_Liste_cotisations
        dlg = DLG_Liste_cotisations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_cotisations_manquantes(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("cotisations_manquantes", "consulter") == False : return
        import DLG_Cotisations_manquantes
        dlg = DLG_Cotisations_manquantes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_cotisations_imprimer(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Cotisations_impression
        dlg = DLG_Cotisations_impression.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_cotisations_email(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Cotisations_email
        dlg = DLG_Cotisations_email.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_cotisations_depots(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("cotisations_depots", "consulter") == False : return
        import DLG_Depots_cotisations
        dlg = DLG_Depots_cotisations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_imprim_conso_journ(self, event):
        import DLG_Impression_conso
        dlg = DLG_Impression_conso.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_conso_gestionnaire(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "consulter") == False : return
        import DLG_Gestionnaire_conso
        dlg = DLG_Gestionnaire_conso.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_remplissage.MAJ()
        
    def On_conso_attente(self, event):
        self.ctrl_remplissage.OuvrirListeAttente() 

    def On_conso_refus(self, event):
        self.ctrl_remplissage.OuvrirListeRefus() 

    def On_conso_absences(self, event):
        import DLG_Liste_absences
        dlg = DLG_Liste_absences.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_conso_synthese_conso(self, event):
        import DLG_Synthese_conso
        dlg = DLG_Synthese_conso.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_conso_etat_global(self, event):
        import DLG_Etat_global
        dlg = DLG_Etat_global.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_conso_etat_nominatif(self, event):
        import DLG_Etat_nomin
        dlg = DLG_Etat_nomin.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def On_conso_badgeage(self, event):
        import DLG_Badgeage
        dlg = DLG_Badgeage.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_remplissage.MAJ()

    def On_individus_scolarite(self, event):
        import DLG_Inscriptions_scolaires
        dlg = DLG_Inscriptions_scolaires.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_inscriptions(self, event):
        import DLG_Liste_inscriptions
        dlg = DLG_Liste_inscriptions.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_individus(self, event):
        import DLG_Liste_individus
        dlg = DLG_Liste_individus.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_familles(self, event):
        import DLG_Liste_familles
        dlg = DLG_Liste_familles.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_transports_recap(self, event):
        import DLG_Liste_transports_recap
        dlg = DLG_Liste_transports_recap.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_transports_detail(self, event):
        import DLG_Liste_transports_detail
        dlg = DLG_Liste_transports_detail.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_anniversaires(self, event):
        import DLG_Anniversaires
        dlg = DLG_Anniversaires.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_infos_med(self, event):
        import DLG_Impression_infos_medicales
        dlg = DLG_Impression_infos_medicales.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_pieces_fournies(self, event):
        import DLG_Pieces_fournies
        dlg = DLG_Pieces_fournies.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_pieces_manquantes(self, event):
        import DLG_Pieces_manquantes
        dlg = DLG_Pieces_manquantes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def On_individus_regimes_caisses(self, event):
        import DLG_Liste_regimes
        dlg = DLG_Liste_regimes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_quotients(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_quotients", "consulter") == False : return
        import DLG_Liste_quotients
        dlg = DLG_Liste_quotients.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_mandats(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_mandats", "consulter") == False : return
        import DLG_Liste_mandats
        dlg = DLG_Liste_mandats.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_importer_photos(self, event):
        import DLG_Importation_photos
        dlg = DLG_Importation_photos.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_importer_csv(self, event):
        import DLG_Importation_individus
        dlg = DLG_Importation_individus.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_individus.MAJ()

    def On_individus_importer_fichier(self, event):
        import DLG_Importation_fichier
        dlg = DLG_Importation_fichier.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_individus.MAJ()

    def On_individus_edition_etiquettes(self, event):
        import DLG_Impression_etiquettes
        dlg = DLG_Impression_etiquettes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_aide_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide(None)

    def On_aide_guide_demarrage(self, event):
        """ Accéder à la page de téléchargement du guide de démarrage rapide """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_content&view=article&id=118&Itemid=45")

    def On_aide_forum(self, event):
        """ Accéder au forum d'entraide """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_kunena&Itemid=7")

    def On_aide_videos(self, event):
        """ Accéder au tutoriels vidéos """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_content&view=article&id=27&Itemid=16")

    def On_aide_telechargements(self, event):
        """ Accéder à la plate-forme de téléchargements communautaire """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_phocadownload&view=section&id=2&Itemid=21")

    def On_aide_auteur(self, event):
        """ Envoyer un email à l'auteur """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_contact&view=contact&id=1&Itemid=13")
        
    def On_propos_versions(self, event):
        """ A propos : Notes de versions """
        import  wx.lib.dialogs
        txtLicence = open("Versions.txt", "r")
        msg = txtLicence.read()
        txtLicence.close()
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg.decode("iso-8859-15"), u"Notes de versions", size=(500, 500))
        dlg.ShowModal()
        
    def On_propos_licence(self, event):
        """ A propos : Licence """
        import  wx.lib.dialogs
        txtLicence = open("Licence.txt", "r")
        msg = txtLicence.read()
        txtLicence.close()
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg.decode("iso-8859-15"), u"A propos", size=(500, 500))
        dlg.ShowModal()

    def On_propos_soutenir(self, event):
        """ A propos : Soutenir Noethys """
        import UTILS_Financement
        dlg = UTILS_Financement.DLG_Financement(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_propos_propos(self, event):
        """ A propos : A propos """
        import DLG_A_propos
        dlg = DLG_A_propos.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def MAJlisteDerniersFichiers(self, nomFichier) :
        """ MAJ la liste des derniers fichiers ouverts dans le config et la barre des menus """
        
        # MAJ de la liste des derniers fichiers ouverts :
        listeFichiers = self.userConfig["derniersFichiers"]
        nbreFichiersMax = 10 # Valeur à changer en fonction des souhaits
        
        # Si le nom est déjà dans la liste, on le supprime :
        if nomFichier in listeFichiers : listeFichiers.remove(nomFichier)
           
        # On ajoute le nom du fichier en premier dans la liste :
        listeFichiers.insert(0, nomFichier)
        listeFichiers = listeFichiers[:nbreFichiersMax]
        
        # On enregistre dans le Config :
        self.userConfig["derniersFichiers"] = listeFichiers

    def MAJmenuDerniersFichiers(self):
        """ Met à jour la liste des derniers fichiers dans le menu """
        # Met à jour la liste des derniers fichiers dans la BARRE DES MENUS
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindItemById(ID_QUITTER)
        # Suppression de la liste existante
        menu = menuItem.GetMenu()
        for index in range(ID_DERNIER_FICHIER, ID_DERNIER_FICHIER+10) :
            item = menuBar.FindItemById(index)
            if item == None : 
                break
            else:
                menu.RemoveItem(menuBar.FindItemById(index)) 
                self.Disconnect(index, -1, 10014) # Annule le Bind

        # Ré-intégration des derniers fichiers ouverts :
        listeDerniersFichiers = self.userConfig["derniersFichiers"]
        if len(listeDerniersFichiers) > 0 : 
            index = 0
            for nomFichier in listeDerniersFichiers :
                # Version Reseau
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menu, ID_DERNIER_FICHIER + index, u"%d. %s" % (index+1, nomFichier), u"Ouvrir le fichier : '%s'" % nomFichier)
                menu.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.On_fichier_DerniersFichiers, id=ID_DERNIER_FICHIER, id2=ID_DERNIER_FICHIER + index)


    def OuvrirDernierFichier(self):
        # Chargement du dernier fichier chargé si assistant non affiché
        resultat = False
        if self.nomDernierFichier != "" :
            resultat = self.OuvrirFichier(self.nomDernierFichier)
        return resultat
                    
    def OuvrirFichier(self, nomFichier):
        """ Suite de la commande menu Ouvrir """
        self.SetStatusText(u"Ouverture d'un fichier en cours...")
                        
        # Vérifie que le fichier n'est pas déjà ouvert
        if self.userConfig["nomFichier"] == nomFichier :
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            dlg = wx.MessageDialog(self, u"Le fichier '" + nomFichier + u"' est déjà ouvert !", u"Ouverture de fichier", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetStatusText(u"Le fichier '%s' est déjà ouvert." % nomFichier)
            return False

        # Teste l'existence du fichier :
        if self.TesterUnFichier(nomFichier) == False :
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(u"Impossible d'ouvrir le fichier '%s'." % nomFichier)
            return False
        
        # Vérification du mot de passe
        listeUtilisateursFichier = self.GetListeUtilisateurs(nomFichier)
        if "[RESEAU]" in nomFichier :
            nomFichierTmp = nomFichier[nomFichier.index("[RESEAU]"):]
        else:
            nomFichierTmp = nomFichier
        if self.Identification(listeUtilisateursFichier, nomFichierTmp) == False :
            return False
        self.listeUtilisateurs = listeUtilisateursFichier
        
        # Applique le changement de fichier en cours
        ancienFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = nomFichier
        
        # Vérifie si la version du fichier est à jour
        if nomFichier != "" :
            if self.ValidationVersionFichier(nomFichier) == False :
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                self.SetStatusText(u"Echec de l'ouverture du fichier '%s'." % nomFichier)
                self.userConfig["nomFichier"] = ancienFichier
                return False

        # Remplissage de la table DIVERS pour la date de dernière ouverture
##        if nomFichier != "" :
##            date_jour =  str(datetime.date.today())  
##            listeDonnees = [("date_derniere_ouverture",  date_jour),]
##            db = GestionDB.DB()
##            db.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
##            db.close()

        # Vérifie que le répertoire de destination de sauvegarde auto existe vraiment
##        if nomFichier != "" :
##            self.VerifDestinationSaveAuto()
        
        # Met à jour l'affichage 
        self.MAJ()
        self.SetTitleFrame(nomFichier=nomFichier)
        self.ctrl_ephemeride.Initialisation()
        
        # Récupération de la perspective chargée
        if self.perspective_active != None :
            self._mgr.LoadPerspective(self.perspectives[self.perspective_active]["perspective"])
            self.ForcerAffichagePanneau("ephemeride")
        else:
            self._mgr.LoadPerspective(self.perspective_defaut)
        
        # Met à jour la liste des derniers fichiers ouverts dans le CONFIG de la page
        self.MAJlisteDerniersFichiers(nomFichier) 
        
        # Active la commande Fermer du menu Fichier
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindItemById(ID_FERMER_FICHIER)
        menuItem.Enable(True)
        menuItem = menuBar.FindItemById(ID_FICHIER_INFORMATIONS)
        menuItem.Enable(True)
        if "[RESEAU]" in nomFichier :
            menuItem = menuBar.FindItemById(ID_CONVERSION_RESEAU)
            menuItem.Enable(False) 
            menuItem = menuBar.FindItemById(ID_CONVERSION_LOCAL)
            menuItem.Enable(True) 
        else:
            menuItem = menuBar.FindItemById(ID_CONVERSION_RESEAU)
            menuItem.Enable(True) 
            menuItem = menuBar.FindItemById(ID_CONVERSION_LOCAL)
            menuItem.Enable(False) 
        
        # Met à jour le menu
        self.MAJmenuDerniersFichiers()
        
        # Désactive le menu Conversion Réseau s'il s'agit déjà d'un fichier réseau
##        if "[RESEAU]" in nomFichier :
##            etatMenu = False
##        else:
##            etatMenu = True
##        menuBar = self.GetMenuBar()
##        menuItem = menuBar.FindItemById(107)
##        menuItem.Enable(etatMenu)

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)
        
        # Active les items de la barre de menus
        self.ActiveBarreMenus(True) 
        
        # Confirmation de succès
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        self.SetStatusText(u"Le fichier '%s' a été ouvert avec succès." % nomFichier)  
        
        # Mémorise dans l'historique l'ouverture du fichier
        UTILS_Historique.InsertActions([{"IDcategorie":1, "action":u"Ouverture du fichier %s" % nomFichier},])
        
        # Affiche les messages importants
        wx.CallLater(2000, self.AfficheMessagesOuverture)
        
        return True


    def TesterUnFichier(self, nomFichier):
        """ Fonction pour tester l'existence d'un fichier """
        if "[RESEAU]" in nomFichier :
            # Version RESEAU
            dictResultats = GestionDB.TestConnexionMySQL(typeTest='fichier', nomFichier=u"%s_DATA" % nomFichier)
            if dictResultats["connexion"][0] == False :
                # Connexion impossible au serveur MySQL
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, u"Il est impossible de se connecter au serveur MySQL.\n\nErreur : %s" % erreur, "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if dictResultats["fichier"][0] == False :
                # Ouverture impossible du fichier MySQL demandé
                erreur = dictResultats["fichier"][1]
                dlg = wx.MessageDialog(self, u"La connexion avec le serveur MySQL fonctionne mais il est impossible d'ouvrir le fichier MySQL demandé.\n\nErreur : %s" % erreur, "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
        else:
            # Test de validité du fichier SQLITE :
            fichier = "Data/" + nomFichier + "_DATA.dat"
            test = os.path.isfile(fichier) 
            if test == False :
                dlg = wx.MessageDialog(self, u"Il est impossible d'ouvrir le fichier demandé !", "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else:
                return True
        

    def ConvertVersionTuple(self, texteVersion=""):
        """ Convertit un numéro de version texte en tuple """
        tupleTemp = []
        for num in texteVersion.split(".") :
            tupleTemp.append(int(num))
        return tuple(tupleTemp)

    def ValidationVersionFichier(self, nomFichier):
        """ Vérifie que la version du fichier est à jour avec le logiciel """
        # Récupère les numéros de version
        versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
        versionFichier = self.ConvertVersionTuple(UTILS_Parametres.Parametres(mode="get", categorie="fichier", nom="version", valeur=VERSION_APPLICATION, nomFichier=nomFichier))
        
        # Compare les deux versions
        if versionFichier < versionLogiciel :
            # Fait la conversion à la nouvelle version
            info = "Lancement de la conversion %s -> %s..." %(".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print info
            
            # Affiche d'une fenêtre d'attente
            try :
                message = u"Mise à jour de la base de données en cours... Veuillez patienter..."
                dlgAttente = PBI.PyBusyInfo(message, parent=None, title=u"Mise à jour", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
                wx.Yield() 
                
                DB = GestionDB.DB(nomFichier = nomFichier)        
                resultat = DB.ConversionDB(versionFichier)
                DB.Close()
                
                # Fermeture de la fenêtre d'attente
                del dlgAttente

            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(self, u"Désolé, le problème suivant a été rencontré dans la mise à jour de la base de données : \n\n%s" % err, u"Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

            if resultat != True :
                print resultat
                dlg = wx.MessageDialog(self, u"Le logiciel n'arrive pas à convertir le fichier '" + nomFichier + u":\n\nErreur : " + resultat + u"\n\nVeuillez contacter le développeur du logiciel...", u"Erreur de conversion de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            # Mémorisation de la nouvelle version du fichier
            UTILS_Parametres.Parametres(mode="set", categorie="fichier", nom="version", valeur=".".join([str(x) for x in versionLogiciel]), nomFichier=nomFichier)
            info = "Conversion %s -> %s reussie." %(".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print info

            # Messages exceptionnels suite à la mise à jour
            if versionFichier < (1, 1, 0, 3) :
                dlg = wx.MessageDialog(self, u"Mise à jour majeure 1.1.0.x.\n\nEn raison des modifications conséquentes apportées à cette nouvelle version de Noethys, il est conseillé d'effectuer dès à présent une sauvegarde de votre fichier de données (Menu Fichier > Créer une sauvegarde).", u"Avertissement", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                
            if versionFichier < (1, 1, 1, 3) :
                dlg = wx.MessageDialog(self, u"Note de mise à jour \n\nMise à jour des droits utilisateurs : \n\nNoethys propose désormais une nouvelle gestion avancée des droits utilisateurs. Dans le cadre de cette mise à jour, tous les profils utilisateurs ont été réinitialisés sur 'Administrateur'. Vous pouvez les régler de nouveau dans Menu Paramétrage > Utilisateurs.", u"Information importante", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                
                dlg = wx.MessageDialog(self, u"Note de mise à jour \n\nAmélioration de la gestion des mandats SEPA : \n\nSi vous utilisez le prélèvement automatique et que vous avez déjà saisi les mandats dans Noethys, veuillez lancer le convertisseur de RIB Nationaux en mandats SEPA du menu Outils > Utilitaires admin.", u"Information importante", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            
            
            
            
            
            
            
            
            
            
            
            
            
                
                

        return True
    
    def ActiveBarreMenus(self, etat=True):
        """ Active ou non des menus de la barre """
        for numMenu in range(1, 9):
            self.menubar.EnableTop(numMenu, etat)
        self._mgr.GetPane("panel_recherche").Show(etat)

    def Identification(self, listeUtilisateurs=[], nomFichier=None):
        if PASS != None :
            for dictTemp in listeUtilisateurs :
                if dictTemp["mdp"] == PASS :
                    self.ChargeUtilisateur(dictTemp)
                    return True
        dlg = CTRL_Identification.Dialog(self, listeUtilisateurs=listeUtilisateurs, nomFichier=nomFichier)
        reponse = dlg.ShowModal() 
        dictUtilisateur = dlg.GetDictUtilisateur()
        dlg.Destroy()
        if reponse == wx.ID_OK:
            self.ChargeUtilisateur(dictUtilisateur)
            return True
        else:
            return False

    def GetListeUtilisateurs(self, nomFichier=""):
        """ Récupère la liste des utilisateurs dans la base """
        return UTILS_Utilisateurs.GetListeUtilisateurs(nomFichier) 
    
    def RechargeUtilisateur(self):
        """ A utiliser après un changement des droits par exemple """
        IDutilisateur = self.dictUtilisateur["IDutilisateur"]
        for dictTemp in self.listeUtilisateurs :
            if IDutilisateur == dictTemp["IDutilisateur"] :
                self.dictUtilisateur = dictTemp        
        self.ChargeUtilisateur(self.dictUtilisateur, afficheToaster=False)

    def ChargeUtilisateur(self, dictUtilisateur=None, IDutilisateur=None, afficheToaster=True):
        """Charge un utilisateur à partir de son dictUtilisateur OU de son IDutilisateur """
        # Modifie utilisateur en cours
        if dictUtilisateur != None :
            self.dictUtilisateur = dictUtilisateur
        else:
            for dictTemp in self.listeUtilisateurs :
                if IDutilisateur == dictTemp["IDutilisateur"] :
                    dictUtilisateur = dictTemp
                    self.dictUtilisateur = dictTemp
        # Modifie Barre outils
        if dictUtilisateur["image"] == None or dictUtilisateur["image"] == "Automatique" :
            if dictUtilisateur["sexe"] == "M" : 
                nomImage = "Homme"
            else:
                nomImage = "Femme"
        else :
            nomImage = dictUtilisateur["image"]
        # Affichage de l'image utilisateur dans la barre d'outils
        self.toolBar2.SetToolBitmap(ID_TB_UTILISATEUR, wx.Bitmap("Images/Avatars/16x16/%s.png" % nomImage, wx.BITMAP_TYPE_PNG))
        self.toolBar2.SetToolLabel(ID_TB_UTILISATEUR, u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"]))
        self.toolBar2.Refresh() 
        # Affiche le Toaster
        if afficheToaster == True and PASS == None :
            CTRL_Toaster.ToasterUtilisateur(self, prenom=dictUtilisateur["prenom"], nomImage=nomImage) 
    
    def AfficheMessagesOuverture(self):
        """ Affiche les messages à l'ouverture du fichier """
        listeMessages = self.ctrl_messages.GetMessages()
        for track in listeMessages :
            if track.rappel == 1 :
                texteToaster = track.texte
                if track.priorite == "HAUTE" : 
                    couleurFond="#FFA5A5"
                else:
                    couleurFond="#FDF095"
                self.AfficheToaster(titre=u"Message", texte=texteToaster, couleurFond=couleurFond) 

    def AfficheToaster(self, titre=u"", texte=u"", taille=(200, 100), couleurFond="#F0FBED"):
        """ Affiche une boîte de dialogue temporaire """
        largeur, hauteur = taille
        tb = Toaster.ToasterBox(self, Toaster.TB_SIMPLE, Toaster.TB_DEFAULT_STYLE, Toaster.TB_ONTIME) # TB_CAPTION
        tb.SetTitle(titre)
        tb.SetPopupSize((largeur, hauteur))
        largeurEcran, hauteurEcran = wx.ScreenDC().GetSizeTuple()
        tb.SetPopupPosition((largeurEcran-largeur-10, hauteurEcran-hauteur-50))
        tb.SetPopupPauseTime(2000)
        tb.SetPopupScrollSpeed(8)
        tb.SetPopupBackgroundColour(couleurFond)
        tb.SetPopupTextColour("#000000")
        tb.SetPopupText(texte)
        tb.Play()

    def RechercheMAJinternet(self):
        """ Recherche une mise à jour sur internet """
        # Récupère la version de l'application
        versionApplication = VERSION_APPLICATION
        # Récupère la version de la MAJ sur internet
        try :
            if "linux" in sys.platform :
                # Version Debian
                fichierVersions = urllib2.urlopen('https://raw.githubusercontent.com/Noethys/Noethys/master/source/Versions.txt', timeout=5)
            else:
                # Version Windows
                fichierVersions = urllib2.urlopen('http://www.noethys.com/fichiers/windows/Versions.txt', timeout=5)
            texteNouveautes= fichierVersions.read()
            fichierVersions.close()
            pos_debut_numVersion =texteNouveautes.find("n")
            pos_fin_numVersion = texteNouveautes.find("(")
            versionMaj = texteNouveautes[pos_debut_numVersion+1:pos_fin_numVersion].strip()
        except :
            print "Recuperation du num de version de la MAJ sur internet impossible."
            versionMaj = "0.0.0.0"
        # Compare les deux versions et renvois le résultat
        try :
            if self.ConvertVersionTuple(versionMaj) > self.ConvertVersionTuple(VERSION_APPLICATION) :
                self.versionMAJ = versionMaj
                return True
            else:
                return False
        except :
            return False

    def GetVersionAnnonce(self):
        if self.userConfig.has_key("annonce") :
            versionAnnonce = self.userConfig["annonce"]
            if versionAnnonce != None :
                return versionAnnonce
        return (0, 0, 0, 0)
        
    def Annonce(self):
        """ Création une annonce au premier démarrage du logiciel """
        nomFichier = sys.executable
        if nomFichier.endswith("python.exe") == False :
            versionAnnonce = self.GetVersionAnnonce()
            versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
            if versionAnnonce < versionLogiciel :
                import DLG_Message_accueil
                dlg = DLG_Message_accueil.Dialog(self)
                dlg.ShowModal()
                dlg.Destroy()
                # Mémorise le numéro de version actuel
                self.userConfig["annonce"] = versionLogiciel
                return True
        return False
    
    def EstFichierExemple(self):
        """ Vérifie si c'est un fichier EXEMPLE qui est ouvert actuellement """
        if self.userConfig["nomFichier"] != None :
            if "EXEMPLE_" in self.userConfig["nomFichier"] :
                return True
        return False

    def ProposeMAJ(self):
        """ Propose la MAJ immédiate """
        if self.MAJexiste == True :
            if self.versionMAJ != None :
                message = u"La version %s de Noethys est disponible.\n\nSouhaitez-vous télécharger cette mise à jour maintenant ?" % self.versionMAJ
            else :
                message = u"Une nouvelle version de Noethys est disponible.\n\nSouhaitez-vous télécharger cette mise à jour maintenant ?"
            dlg = wx.MessageDialog(self, message, u"Mise à jour disponible", wx.YES_NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                self.On_outils_updater(None)
                return True
        return False
    
    def AnnonceTemoignages(self):
        # Se déclenche uniquement dans 40% des cas
        if random.randrange(1, 100) > 40 :
            return False
        
        # Vérifie si case Ne plus Afficher cochée ou non
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="temoignages", valeur=False) == True :
            return False

        texte = u"""
<CENTER><IMG SRC="Images/32x32/Information.png">
<BR><BR>
<FONT SIZE=2>
<B>Appel à témoignages</B>
<BR><BR>
Vous utilisez et appréciez Noethys ? 
<BR><BR>
Participez à sa promotion en postant un témoignage sur le site internet de Noethys. L'occasion de décrire votre utilisation du logiciel et de donner ainsi envie aux lecteurs intéressés de s'y essayer.
<BR><BR>
Merci pour votre participation !
<BR><BR>
<A HREF="http://www.noethys.com/index.php/presentation/2013-09-08-15-48-17/temoignages">Cliquez ici pour accéder aux témoignages</A>
</FONT>
</CENTER>
"""
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=u"Information", nePlusAfficher=True)
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="temoignages", valeur=nePlusAfficher)
        return True


    def AnnonceFinancement(self):
        # Vérifie si identifiant saisi et valide
        identifiant = UTILS_Config.GetParametre("enregistrement_identifiant", defaut=None)
        if identifiant != None :
            # Vérifie nbre jours restants
            code = UTILS_Config.GetParametre("enregistrement_code", defaut=None)
            validite = DLG_Enregistrement.GetValidite(identifiant, code)
            if validite != False :
                date_fin_validite, nbreJoursRestants = validite
                dateDernierRappel = UTILS_Config.GetParametre("enregistrement_dernier_rappel", defaut=None)
                
                if nbreJoursRestants < 0 :
                    # Licence périmée
                    if dateDernierRappel != None :
                        UTILS_Config.SetParametre("enregistrement_dernier_rappel", None)
                    
                elif nbreJoursRestants <= 30 :
                    # Licence bientôt périmée
                    UTILS_Config.SetParametre("enregistrement_dernier_rappel", datetime.date.today())
                    if dateDernierRappel != None :
                        nbreJoursDepuisRappel =  (dateDernierRappel - datetime.date.today()).days
                    else :
                        nbreJoursDepuisRappel = None
                    if nbreJoursDepuisRappel == None or nbreJoursDepuisRappel >= 7 :
                        import wx.lib.dialogs as dialogs
                        image = wx.Bitmap("Images/32x32/Cle.png", wx.BITMAP_TYPE_ANY)
                        message1 = u"Votre licence d'accès au manuel de référence en ligne se termine dans %d jours. \n\nSi vous le souhaitez, vous pouvez continuer à bénéficier de cet accès et prolonger votre soutien financier au projet Noethys en renouvelant votre abonnement Classic ou Premium." % nbreJoursRestants
                        dlg = dialogs.MultiMessageDialog(self, message1, caption = u"Enregistrement", msg2=None, style = wx.ICON_INFORMATION | wx.YES|wx.CANCEL|wx.CANCEL_DEFAULT, icon=image, btnLabels={wx.ID_YES : u"Renouveler mon abonnement", wx.ID_CANCEL : u"Fermer"})
                        reponse = dlg.ShowModal() 
                        dlg.Destroy() 
                        if reponse == wx.ID_YES :
                            FonctionsPerso.LanceFichierExterne("Images/Special/Bon_commande.pdf")
                        return True
                    return False
                
                else :
                    # Licence valide
                    if dateDernierRappel != None :
                        UTILS_Config.SetParametre("enregistrement_dernier_rappel", None)
                    return False
                
        # Pub se déclenche uniquement dans 20% des cas
        if random.randrange(1, 100) <= 20 :
            import UTILS_Financement
            dlg = UTILS_Financement.DLG_Financement(self)
            dlg.ShowModal() 
            dlg.Destroy()
            return True
        else :
            return False

    def AutodetectionAnomalies(self):
        """ Auto-détection d'anomalies """
        # Se déclenche uniquement dans 15% des cas
        if random.randrange(1, 100) > 15 :
            return False

        import DLG_Depannage
        resultat = DLG_Depannage.Autodetection(self)
        if resultat == None :
            return False
        else :
            return True
            

# -----------------------------------------------------------------------------------------------------------------

class MyApp(wx.App):
    def OnInit(self):
        # Adaptation pour rétrocompatibilité wx2.8
        if wx.VERSION < (2, 9, 0, 0) :
            wx.InitAllImageHandlers() 
        
        heure_debut = time.time()
        
        # Vérifie l'existence des répertoires
        for rep in ("Aide", "Temp", "Updates") :
            if os.path.isdir(rep) == False :
                os.makedirs(rep)
                print "Creation du repertoire : ", rep
        
        # Réinitialisation du fichier des parametres en conservant la touche ALT
        if wx.GetKeyState(307) == True :
            dlg = wx.MessageDialog(None, u"Souhaitez-vous vraiment réinitialiser Noethys ?", u"Réinitialisation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES :
                os.remove("Data/Config.dat")
            dlg.Destroy()
        
        # Suppression du fichier temporaire s'il existe pour éviter bugs
        if os.path.isfile("Data/__db.Config.dat") :
            os.remove("Data/__db.Config.dat")
        
        # AdvancedSplashScreen
        if PASS == None :
            bmp = wx.Bitmap("Images/Special/Logo_splash.png", wx.BITMAP_TYPE_PNG)
            frame = AS.AdvancedSplash(None, bitmap=bmp, timeout=500, agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_SCREEN)
            anneeActuelle = str(datetime.date.today().year)
            frame.SetText(u"Copyright © 2010-%s Ivan LUCAS" % anneeActuelle[2:])
            frame.SetTextFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
            frame.SetTextPosition((340, 175))
            frame.SetTextColour(wx.Colour(110, 147, 58))
            frame.Refresh()
            frame.Update()
            wx.Yield()

        # Création de la frame principale
        frame = MainFrame(None)
        self.SetTopWindow(frame)
        frame.Initialisation()
        frame.Show()   

        # Affiche une annonce si c'est un premier démarrage ou après une mise à jour
        etat_annonce = frame.Annonce()
                
        # Charge le fichier Exemple si l'utilisateur le souhaite
        etat_exemple = frame.ChargeFichierExemple() 
        
        # Charge le dernier fichier
        fichierOuvert = frame.OuvrirDernierFichier()

        # Propose mise à jour immédiate
        etat_maj = frame.ProposeMAJ()
        
        # Après ouverture d'un fichier :
        if fichierOuvert == True and frame.EstFichierExemple() == False and etat_maj == False :
            
            # Témoignages
            temoignages = frame.AnnonceTemoignages()
            
            # Financement
            if temoignages == False : 
                financement = frame.AnnonceFinancement()
            
                # Détection d'anomalies
                if financement == False :
                    frame.AutodetectionAnomalies() 
        
##        print time.time() - heure_debut
        return True




if __name__ == "__main__":
    
    # Crash report
    UTILS_Rapport_bugs.Activer_rapport_erreurs(version=VERSION_APPLICATION)
    
    # Log
    fichierLog = "journal.log"
    
    # Supprime le journal.log si supérieur à 10 Mo
    if os.path.isfile(fichierLog) :
        taille = os.path.getsize(fichierLog)
        if taille > 5000000 :
            os.remove(fichierLog)

    # Lancement de l'application
    nomFichier = sys.executable
    if nomFichier.endswith("python.exe") or os.path.isfile("nolog.txt") :
        app = MyApp(redirect=False)
    else :
        app = MyApp(redirect=True, filename=fichierLog)
    app.MainLoop()
    
