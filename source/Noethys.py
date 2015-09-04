#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import UTILS_Traduction

import wx
import CTRL_Bouton_image
import sys
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
import DLG_Effectifs
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
    

# Constantes g�n�rales
VERSION_APPLICATION = FonctionsPerso.GetVersionLogiciel()
NOM_APPLICATION = u"Noethys"

# ID pour la barre des menus
ID_DERNIER_FICHIER = 700
ID_PREMIERE_PERSPECTIVE = 500
ID_AFFICHAGE_PANNEAUX = 600

# ID pour la barre d'outils
ID_TB_GESTIONNAIRE = wx.NewId()
ID_TB_LISTE_CONSO = wx.NewId()
ID_TB_BADGEAGE = wx.NewId()
ID_TB_REGLER_FACTURE = wx.NewId()
ID_TB_CALCULATRICE = wx.NewId()
ID_TB_UTILISATEUR = wx.NewId()



class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title=_(u"Noethys"), name="general", style=wx.DEFAULT_FRAME_STYLE)
        
##        # Dates en francais
##        wx.Locale(wx.LANGUAGE_FRENCH)
##        try : locale.setlocale(locale.LC_ALL, 'FR')
##        except : pass
        
        # Ic�ne
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
        # V�rifie que le fichier de configuration existe bien
        self.nomFichierConfig = "Data/Config.dat"
        test = os.path.isfile(self.nomFichierConfig) 
        if test == False :
            # Cr�ation du fichier de configuration
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

        # R�cup�ration des fichiers de configuration
        self.userConfig = self.GetFichierConfig(nomFichier=self.nomFichierConfig) # Fichier de config de l'utilisateur
        
        # Gestion des utilisateurs
        self.listeUtilisateurs = [] 
        self.dictUtilisateur = None
        
        # Chargement de la traduction
##        if test == False :
##            self.langue = self.Select_langue()
##            UTILS_Config.SetParametre("langue_interface", self.langue)
##        else :
##            self.langue = UTILS_Config.GetParametre("langue_interface", None)
        self.langue = UTILS_Config.GetParametre("langue_interface", None)
        self.ChargeTraduction() 

        # R�cup�ration du nom du dernier fichier charg�
        self.nomDernierFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = ""
        
        if self.userConfig.has_key("assistant_demarrage") :
            if self.userConfig["assistant_demarrage"] == True :
                self.afficherAssistant = False
            else: self.afficherAssistant = True
        else:
            self.afficherAssistant = True

        # Recherche si une mise � jour internet existe
        self.versionMAJ = None
        if sys.executable.endswith("python.exe") == True :
            self.MAJexiste = False
        else:
            self.MAJexiste = self.RechercheMAJinternet()
        
        if UTILS_Config.GetParametre("propose_maj", defaut=True) == False :
            self.MAJexiste = False

        # R�cup�ration des perspectives de la page d'accueil
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
        
        # Cr�ation du AUI de la fen�tre 
        self._mgr = aui.AuiManager()
        if "linux" not in sys.platform :
            try :
                self._mgr.SetArtProvider(aui.ModernDockArt(self))
            except :
                pass
        self._mgr.SetManagedWindow(self)

        # Barre des t�ches
        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText(_(u"Bienvenue dans %s...") % NOM_APPLICATION)
        
        # Cr�ation de la barre des menus
        self.CreationBarreMenus()
        
        # Cr�ation de la barre d'outils
        self.CreationBarresOutils() 
        
        # Cr�ation des panneaux
        self.CreationPanneaux()
        
        # Cr�ation des Binds
        self.CreationBinds()
        
        # D�termine la taille de la fen�tre
        self.SetMinSize((935, 740))
        if self.userConfig.has_key("taille_fenetre") == False :
            self.userConfig["taille_fenetre"] = (0, 0)
        taille_fenetre = self.userConfig["taille_fenetre"]
        if taille_fenetre == (0, 0) :
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.CenterOnScreen()
        
        # D�sactive les items de la barre de menus
        self.ActiveBarreMenus(False) 
        
        # Binds
        self.Bind(wx.EVT_CLOSE, self.OnClose)
##        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Affiche un Toaster quand une mise � jour du logiciel est disponible
        if self.MAJexiste == True :
            texteToaster = _(u"Une nouvelle version de Noethys est disponible !")
            self.AfficheToaster(titre=_(u"Mise � jour"), texte=texteToaster, couleurFond="#81A8F0") 
    
    def ChargeTraduction(self):
        UTILS_Traduction.ChargeTraduction(self.langue)

    def Select_langue(self):
        # Recherche les fichiers de langues existants
        listeFichiers = os.listdir("Lang/") 
        listeLabels = [u"Fran�ais (fr_FR - par d�faut)",]
        listeCodes = [None,]
        for nomFichier in listeFichiers :
            code, extension = nomFichier.split(".")
            fichier = shelve.open("Lang/" + nomFichier, "r")
            
            # Lecture des caract�ristiques
            dictInfos = fichier["###INFOS###"]
            nom = dictInfos["nom_langue"]
            code = dictInfos["code_langue"]
                    
            # Fermeture du fichier
            fichier.close()
            
            label = u"%s (%s)" % (nom, code)
            if code not in listeCodes :
                listeLabels.append(label)
                listeCodes.append(code)
        
        # DLG
        code = None
        dlg = wx.SingleChoiceDialog(self, u"S�lectionnez la langue de l'interface :", u"Bienvenue dans Noethys", listeLabels, wx.CHOICEDLG_STYLE)
        dlg.SetSize((400, 400))
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            index = dlg.GetSelection()
            code = listeCodes[index]
        dlg.Destroy()
        
        return code


    def SetTitleFrame(self, nomFichier=""):
        if "[RESEAU]" in nomFichier :
            port, hote, user, mdp = nomFichier.split(";")
            nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
            nomFichier = _(u"Fichier r�seau : %s | %s") % (nomFichier, user)
        if nomFichier != "" :
            nomFichier = " - [" + nomFichier + "]"
        titreFrame = NOM_APPLICATION + " v" + VERSION_APPLICATION + nomFichier
        self.SetTitle(titreFrame)

    def GetFichierConfig(self, nomFichier=""):
        """ R�cup�re le dictionnaire du fichier de config """
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
        
        # M�morise l'action dans l'historique
        if self.userConfig["nomFichier"] != "" :
            try :
                UTILS_Historique.InsertActions([{
                    "IDcategorie" : 1, 
                    "action" : _(u"Fermeture du fichier"),
                    },])
            except :
                pass
                
        # M�morisation du param�tre de la taille d'�cran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        self.userConfig["taille_fenetre"] = taille_fenetre
        
        # M�morisation des perspectives
        self.SauvegardePerspectiveActive() 
        self.userConfig["perspectives"] = self.perspectives
        self.userConfig["perspective_active"] = self.perspective_active
        
        self.userConfig["perspective_ctrl_effectifs"] = self.ctrl_remplissage.SavePerspective()
        self.userConfig["page_ctrl_effectifs"] = self.ctrl_remplissage.GetPageActive() 

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)

        # Sauvegarde automatique
        if self.userConfig["nomFichier"] != "" and sauvegardeAuto == True :
            resultat = self.SauvegardeAutomatique() 
            if resultat == wx.ID_CANCEL :
                return False

        # Vidage des r�pertoires Temp
        if videRepertoiresTemp == True :
            FonctionsPerso.VideRepertoireTemp()
            FonctionsPerso.VideRepertoireUpdates()
        
        return True
    
    def SauvegardeAutomatique(self):
        save = UTILS_Sauvegarde_auto.Sauvegarde_auto(self)
        resultat = save.Start() 
        return resultat
        
    def ChargeFichierExemple(self):
        """ Demande � l'utilisateur s'il souhaite charger le fichier Exemple """
        if self.nouveauFichierConfig == True :
            import DLG_Bienvenue
            dlg = DLG_Bienvenue.Dialog(self)
            if dlg.ShowModal() == wx.ID_OK :
                nomFichier = dlg.GetNomFichier()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return
            
            # Charge le fichier Exemple s�lectionn�
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
        self._mgr.AddPane(self.ctrl_individus, aui.AuiPaneInfo().Name("recherche").Caption(_(u"Individus")).
                          CenterPane().PaneBorder(True).CaptionVisible(True) )

        # Panneau Eph�m�ride
        self.ctrl_ephemeride = CTRL_Ephemeride.CTRL(self)
        self._mgr.AddPane(self.ctrl_ephemeride, aui.AuiPaneInfo().Name("ephemeride").Caption(_(u"Eph�m�ride")).
                          Top().Layer(0).Row(1).Position(0).CloseButton(True).MaximizeButton(True).MinimizeButton(True).MinSize((-1, 100)).BestSize((-1, 100)) )

        # Panneau Serveur
        if UTILS_Config.GetParametre("synchro_serveur_activer", defaut=False) == True :
            import CTRL_Serveur_nomade
            self.ctrl_serveur_nomade = CTRL_Serveur_nomade.Panel(self)
            self._mgr.AddPane(self.ctrl_serveur_nomade, aui.AuiPaneInfo().Name("serveur_nomade").Caption(_(u"Serveur Nomadhys")).
                              Top().Layer(0).Row(2).Position(0).CloseButton(False).MaximizeButton(False).MinimizeButton(False).MinSize((-1, 85)).BestSize((-1, 85)) )

        # Panneau Effectifs
        self.ctrl_remplissage = DLG_Effectifs.CTRL(self)
        self._mgr.AddPane(self.ctrl_remplissage, aui.AuiPaneInfo().Name("effectifs").Caption(_(u"Effectifs")).
                          Left().Layer(1).Position(0).CloseButton(True).MaximizeButton(True).MinimizeButton(True).MinSize((200, 200)).BestSize((630, 600)) )
        
        if self.userConfig.has_key("perspective_ctrl_effectifs") == True :
            self.ctrl_remplissage.LoadPerspective(self.userConfig["perspective_ctrl_effectifs"])
        if self.userConfig.has_key("page_ctrl_effectifs") == True :
            self.ctrl_remplissage.SetPageActive(self.userConfig["page_ctrl_effectifs"])
            
        # Panneau Messages
        self.ctrl_messages = CTRL_Messages.Panel(self)
        self._mgr.AddPane(self.ctrl_messages, aui.AuiPaneInfo().Name("messages").Caption(_(u"Messages")).
                          Left().Layer(1).Position(2).CloseButton(True).MinSize((200, 100)).MaximizeButton(True).MinimizeButton(True) )
        pi = self._mgr.GetPane("messages")
        pi.dock_proportion = 50000 # Proportion
        
        # Panneau Accueil
        self.ctrl_accueil = CTRL_Accueil.Panel(self)
        self._mgr.AddPane(self.ctrl_accueil, aui.AuiPaneInfo().Name("accueil").Caption(_(u"Accueil")).
                          Bottom().Layer(0).Position(1).Hide().CaptionVisible(False).CloseButton(False).MaximizeButton(False) )
        
        self._mgr.Update()
        
        # Sauvegarde de la perspective par d�faut
        self.perspective_defaut = self._mgr.SavePerspective()
        
        # Cache tous les panneaux en attendant la saisie du mot de passe utilisateur
        for pane in self._mgr.GetAllPanes() :
            if pane.name != "accueil" :
                pane.Hide()
        self._mgr.GetPane("accueil").Show().Maximize()
        
        self._mgr.Update()
        
    def CreationBarresOutils(self):
        self.listeBarresOutils = []
        self.dictBarresOutils = {}
        
        # Barre raccourcis --------------------------------------------------
        tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT | aui.AUI_TB_HORZ_TEXT)
        tb.SetToolBitmapSize(wx.Size(16, 16))
        tb.AddSimpleTool(ID_TB_GESTIONNAIRE, _(u"Gestionnaire des conso."), wx.Bitmap("Images/16x16/Calendrier.png", wx.BITMAP_TYPE_PNG), _(u"Acc�der au gestionnaire des consommations"))
        tb.AddSimpleTool(ID_TB_LISTE_CONSO, _(u"Liste des conso."), wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG), _(u"Imprimer une liste de consommations"))
        tb.AddSimpleTool(ID_TB_BADGEAGE, _(u"Badgeage"), wx.Bitmap("Images/16x16/Badgeage.png", wx.BITMAP_TYPE_PNG), _(u"Lancer une proc�dure de badgeage"))
        tb.AddSeparator()
        tb.AddSimpleTool(ID_TB_REGLER_FACTURE, _(u"R�gler une facture"), wx.Bitmap("Images/16x16/Reglement.png", wx.BITMAP_TYPE_PNG), _(u"R�gler une facture � partir de son num�ro"))
        self.ctrl_numfacture = CTRL_Numfacture.CTRL(tb, size=(100, -1))
        tb.AddControl(self.ctrl_numfacture)
        tb.AddSeparator()
        tb.AddSimpleTool(ID_TB_CALCULATRICE, _(u"Calculatrice"), wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG), _(u"Ouvrir la calculatrice"))

        tb.Realize()
        code = "barre_raccourcis"
        label = _(u"Barre de raccourcis")
        self.listeBarresOutils.append(code)
        self.dictBarresOutils[code] = {"label" : label, "ctrl" : tb}
        self._mgr.AddPane(tb, aui.AuiPaneInfo().Name(code).Caption(label).ToolbarPane().Top())
        self._mgr.Update()
        
        # Barre Utilisateur --------------------------------------------------
        tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT | aui.AUI_TB_HORZ_TEXT)
        tb.SetToolBitmapSize(wx.Size(16, 16))
        self.ctrl_identification = CTRL_Identification.CTRL(tb, listeUtilisateurs=self.listeUtilisateurs, size=(80, -1))
        tb.AddControl(self.ctrl_identification)
        tb.AddSimpleTool(ID_TB_UTILISATEUR, u"xxxxxxxxxxxxxxxxxxxxxxxxxxxx", wx.Bitmap("Images/16x16/Homme.png", wx.BITMAP_TYPE_PNG), _(u"Utilisateur en cours"))
        tb.AddSpacer(50)
        
        tb.Realize()
        code = "barre_utilisateur"
        label = _(u"Barre Utilisateur")
        self.listeBarresOutils.append(code)
        self.dictBarresOutils[code] = {"label" : label, "ctrl" : tb}
        self._mgr.AddPane(tb, aui.AuiPaneInfo().Name(code).Caption(label).ToolbarPane().Top())
        self._mgr.Update()

        # Barres personnalis�es --------------------------------------------
        if self.userConfig.has_key("barres_outils_perso") == True :
            texteBarresOutils = self.userConfig["barres_outils_perso"]
        else :
            self.userConfig["barres_outils_perso"] = ""
            texteBarresOutils = ""
        if len(texteBarresOutils) > 0 :
            listeBarresOutils = texteBarresOutils.split("@@@@")
        else :
            listeBarresOutils = []
                
        index = 0
        for texte in listeBarresOutils :
            self.CreerBarreOutils(texte, index)
            index += 1
            
    def CreerBarreOutils(self, texte="", index=0, ctrl=None):
        # Analyse du texte (Nom, style, contenu)
        codeBarre, label, observations, style, contenu = texte.split("###")
        listeContenu = contenu.split(";")
        
        # Recherche des infos du menu
        dictItems = self.GetDictItemsMenu() 
        
        # Analyse du style
        if style == "textedroite" :
            agwStyle = aui.AUI_TB_OVERFLOW | aui.AUI_TB_HORZ_TEXT
        elif style == "textedessous" :
            agwStyle = aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT
        elif style == "texteseul" :
            agwStyle = aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT
        elif style == "imageseule" :
            agwStyle = aui.AUI_TB_OVERFLOW
        else :
            agwStyle = aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT
        
        # Init ToolBar
        if ctrl == None :
            tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=agwStyle)
            tb.SetToolBitmapSize(wx.Size(16, 16))
        else :
            tb = ctrl
            tb.Clear() 

        for code in listeContenu :
            if code == "|" :
                tb.AddSeparator()
            elif code == "-" :
                tb.AddStretchSpacer()
            elif code.startswith("label:"):
                # Ne fonctionne pas : Il y a un bug sur agw.aui avec la largeur du label
                label = code.replace("label:", "")
                tb.AddSimpleTool(wx.NewId(), label, wx.NullBitmap, kind=aui.ITEM_LABEL)
            else :
                item = dictItems[code]
                if item.has_key("image") and style != "texteseul" :
                    image = wx.Bitmap(item["image"], wx.BITMAP_TYPE_PNG)
                else :
                    image = wx.NullBitmap
                id = wx.NewId() 
                tb.AddSimpleTool(id, item["infobulle"], image, item["infobulle"])
                self.Bind(wx.EVT_TOOL, item["action"], id=id)
        
        # Finalisation ToolBar
        tb.Realize()
        self.SendSizeEvent() 

        if ctrl == None :
            self.listeBarresOutils.append(codeBarre)
            self.dictBarresOutils[codeBarre] = {"label" : label, "ctrl" : tb, "texte" : texte}
            self._mgr.AddPane(tb, aui.AuiPaneInfo().Layer(index+1).Name(codeBarre).Caption(label).ToolbarPane().Top())
        self._mgr.Update()
    

    def CreationBarreMenus(self):
        """ Construit la barre de menus """
        self.listeItemsMenu = [
        
            # Fichier
            {"code" : "menu_fichier", "label" : _(u"Fichier"), "items" : [
                    {"code" : "nouveau_fichier", "label" : _(u"Cr�er un nouveau fichier"), "infobulle" : _(u"Cr�er un nouveau fichier"), "image" : "Images/16x16/Fichier_nouveau.png", "action" : self.On_fichier_Nouveau},
                    {"code" : "ouvrir_fichier", "label" : _(u"Ouvrir un fichier"), "infobulle" : _(u"Ouvrir un fichier existant"), "image" : "Images/16x16/Fichier_ouvrir.png", "action" : self.On_fichier_Ouvrir},
                    {"code" : "fermer_fichier", "label" : _(u"Fermer le fichier"), "infobulle" : _(u"Fermer le fichier ouvert"), "image" : "Images/16x16/Fichier_fermer.png", "action" : self.On_fichier_Fermer, "actif" : False},
                    "-",
                    {"code" : "fichier_informations", "label" : _(u"Informations sur le fichier"), "infobulle" : _(u"Informations sur le fichier"), "image" : "Images/16x16/Information.png", "action" : self.On_fichier_Informations, "actif" : False},
                    "-",
                    {"code" : "creer_sauvegarde", "label" : _(u"Cr�er une sauvegarde"), "infobulle" : _(u"Cr�er une sauvegarde"), "image" : "Images/16x16/Sauvegarder.png", "action" : self.On_fichier_Sauvegarder},
                    {"code" : "restaurer_sauvegarde", "label" : _(u"Restaurer une sauvegarde"), "infobulle" : _(u"Restaurer une sauvegarde"), "image" : "Images/16x16/Restaurer.png", "action" : self.On_fichier_Restaurer},
                    {"code" : "sauvegardes_auto", "label" : _(u"Sauvegardes automatiques"), "infobulle" : _(u"Param�trage des sauvegardes automatiques"), "image" : "Images/16x16/Sauvegarder_param.png", "action" : self.On_fichier_Sauvegardes_auto},
                    "-",
                    {"code" : "convertir_fichier_reseau", "label" : _(u"Convertir en fichier r�seau"), "infobulle" : _(u"Convertir le fichier en mode r�seau"), "image" : "Images/16x16/Conversion_reseau.png", "action" : self.On_fichier_Convertir_reseau, "actif" : False},
                    {"code" : "convertir_fichier_local", "label" : _(u"Convertir en fichier local"), "infobulle" : _(u"Convertir le fichier en mode local"), "image" : "Images/16x16/Conversion_local.png", "action" : self.On_fichier_Convertir_local, "actif" : False},
                    "-",
                    {"code" : "quitter", "label" : _(u"Quitter"), "infobulle" : _(u"Quitter Noethys"), "image" : "Images/16x16/Quitter.png", "action" : self.On_fichier_Quitter},
                    ],
            },

            # Param�trage
            {"code" : "menu_parametrage", "label" : _(u"Param�trage"), "items" : [
                    {"code" : "preferences", "label" : _(u"Pr�f�rences"), "infobulle" : _(u"Pr�f�rences"), "image" : "Images/16x16/Mecanisme.png", "action" : self.On_param_preferences},
                    {"code" : "enregistrement", "label" : _(u"Enregistrement"), "infobulle" : _(u"Enregistrement"), "image" : "Images/16x16/Cle.png", "action" : self.On_param_enregistrement},
                    "-",
                    {"code" : "utilisateurs", "label" : _(u"Utilisateurs"), "infobulle" : _(u"Param�trage des utilisateurs"), "image" : "Images/16x16/Personnes.png", "action" : self.On_param_utilisateurs},
                    {"code" : "modeles_droits", "label" : _(u"Mod�les de droits"), "infobulle" : _(u"Param�trage des mod�les de droits"), "image" : "Images/16x16/Droits.png", "action" : self.On_param_modeles_droits},
                    {"code" : "acces_reseau", "label" : _(u"Acc�s r�seau"), "infobulle" : _(u"Param�trage des acc�s r�seau"), "image" : "Images/16x16/Utilisateur_reseau.png", "action" : self.On_param_utilisateurs_reseau},
                    "-",
                    {"code" : "organisateur", "label" : _(u"Organisateur"), "infobulle" : _(u"Param�trage des donn�es sur l'organisateur"), "image" : "Images/16x16/Organisateur.png", "action" : self.On_param_organisateur},
                    {"code" : "groupes_activites", "label" : _(u"Groupes d'activit�s"), "infobulle" : _(u"Param�trage des groupes d'activit�s"), "image" : "Images/16x16/Groupe_activite.png", "action" : self.On_param_groupes_activites},
                    {"code" : "activites", "label" : _(u"Activit�s"), "infobulle" : _(u"Param�trage des activit�s"), "image" : "Images/16x16/Activite.png", "action" : self.On_param_activites},
                    {"code" : "types_cotisations", "label" : _(u"Cotisations"), "infobulle" : _(u"Param�trage des types de cotisations"), "image" : "Images/16x16/Identite.png", "action" : self.On_param_types_cotisations},
                    "-",
                    {"code" : "modeles_documents", "label" : _(u"Mod�les de documents"), "infobulle" : _(u"Param�trage des mod�les de documents"), "image" : "Images/16x16/Document.png", "action" : self.On_param_documents},
                    {"code" : "modeles_emails", "label" : _(u"Mod�les d'Emails"), "infobulle" : _(u"Param�trage des mod�les d'Emails"), "image" : "Images/16x16/Emails_modele.png", "action" : self.On_param_modeles_emails},
                    {"code" : "modeles_tickets", "label" : _(u"Mod�les de tickets"), "infobulle" : _(u"Param�trage des mod�les de tickets"), "image" : "Images/16x16/Ticket.png", "action" : self.On_param_modeles_tickets},
                    {"code" : "modeles_contrats", "label" : _(u"Mod�les de contrats"), "infobulle" : _(u"Param�trage des mod�les de contrats"), "image" : "Images/16x16/Contrat.png", "action" : self.On_param_modeles_contrats},
                    {"code" : "modeles_plannings", "label" : _(u"Mod�les de plannings"), "infobulle" : _(u"Param�trage des mod�les de plannings"), "image" : "Images/16x16/Calendrier.png", "action" : self.On_param_modeles_plannings},
                    {"code" : "modeles_aides", "label" : _(u"Mod�les d'aides journali�res"), "infobulle" : _(u"Param�trage des mod�les d'aides journali�res"), "image" : "Images/16x16/Mecanisme.png", "action" : self.On_param_modeles_aides},
                    "-",
                    {"code" : "procedures_badgeage", "label" : _(u"Proc�dures de badgeage"), "infobulle" : _(u"Param�trage des proc�dures de badgeage"), "image" : "Images/16x16/Badgeage.png", "action" : self.On_param_badgeage},
                    {"code" : "synthese_vocale", "label" : _(u"Synth�se vocale"), "infobulle" : _(u"Param�trage de la synth�se vocale"), "image" : "Images/16x16/Vocal.png", "action" : self.On_param_vocal},
                    "-",
                    {"code" : "menu_parametrage_factures", "label" : _(u"Facturation"), "items" : [
                            {"code" : "lots_factures", "label" : _(u"Lots de factures"), "infobulle" : _(u"Param�trage des lots de factures"), "image" : "Images/16x16/Lot_factures.png", "action" : self.On_param_lots_factures},
                            {"code" : "lots_rappels", "label" : _(u"Lots de rappels"), "infobulle" : _(u"Param�trage des lots de rappels"), "image" : "Images/16x16/Lot_factures.png", "action" : self.On_param_lots_rappels},
                            ],
                    },
                    {"code" : "menu_parametrage_reglements", "label" : _(u"Comptabilit�"), "items" : [
                            {"code" : "comptes_bancaires", "label" : _(u"Comptes bancaires"), "infobulle" : _(u"Param�trage des comptes bancaires"), "image" : "Images/16x16/Reglement.png", "action" : self.On_param_comptes},
                            "-",
                            {"code" : "modes_reglements", "label" : _(u"Modes de r�glements"), "infobulle" : _(u"Param�trage des modes de r�glements"), "image" : "Images/16x16/Mode_reglement.png", "action" : self.On_param_modes_reglements},
                            {"code" : "emetteurs", "label" : _(u"Emetteurs de r�glements"), "infobulle" : _(u"Param�trage des �metteurs de r�glements"), "image" : "Images/16x16/Mode_reglement.png", "action" : self.On_param_emetteurs},
                            "-",
                            {"code" : "compta_exercices", "label" : _(u"Exercices comptables"), "infobulle" : _(u"Param�trage des exercices comptables"), "image" : "Images/16x16/Reglement.png", "action" : self.On_param_exercices},
                            {"code" : "compta_analytiques", "label" : _(u"Postes analytiques"), "infobulle" : _(u"Param�trage des postes analytiques"), "image" : "Images/16x16/Reglement.png", "action" : self.On_param_analytiques},
                            {"code" : "compta_categories", "label" : _(u"Cat�gories comptables"), "infobulle" : _(u"Param�trage des cat�gories comptables"), "image" : "Images/16x16/Reglement.png", "action" : self.On_param_categories_comptables},
                            {"code" : "compta_comptes", "label" : _(u"Comptes comptables"), "infobulle" : _(u"Param�trage des comptes comptables"), "image" : "Images/16x16/Reglement.png", "action" : self.On_param_comptes_comptables},
                            {"code" : "compta_tiers", "label" : _(u"Tiers"), "infobulle" : _(u"Param�trage des tiers"), "image" : "Images/16x16/Tiers.png", "action" : self.On_param_tiers},
                            {"code" : "compta_budgets", "label" : _(u"Budgets"), "infobulle" : _(u"Param�trage des budgets"), "image" : "Images/16x16/Tresorerie.png", "action" : self.On_param_budgets},
                            {"code" : "compta_releves", "label" : _(u"Relev�s bancaires"), "infobulle" : _(u"Param�trage des relev�s bancaires"), "image" : "Images/16x16/Document_coches.png", "action" : self.On_param_releves_bancaires},
                            ],
                    },
                    {"code" : "menu_parametrage_prelevements", "label" : _(u"Pr�l�vement automatique"), "items" : [
                            {"code" : "etablissements_bancaires", "label" : _(u"Etablissements bancaires"), "infobulle" : _(u"Param�trage des �tablissements bancaires"), "image" : "Images/16x16/Banque.png", "action" : self.On_param_banques},
                            ],
                    },
                    "-",
                    {"code" : "menu_parametrage_renseignements", "label" : _(u"Renseignements"), "items" : [
                            {"code" : "questionnaires", "label" : _(u"Questionnaires"), "infobulle" : _(u"Param�trage des questionnaires"), "image" : "Images/16x16/Questionnaire.png", "action" : self.On_param_questionnaires},
                            {"code" : "types_pieces", "label" : _(u"Types de pi�ces"), "infobulle" : _(u"Param�trage des types de pi�ces"), "image" : "Images/16x16/Piece.png", "action" : self.On_param_pieces},
                            {"code" : "regimes_sociaux", "label" : _(u"R�gimes sociaux"), "infobulle" : _(u"Param�trage des r�gimes sociaux"), "image" : "Images/16x16/Mecanisme.png", "action" : self.On_param_regimes},
                            {"code" : "caisses", "label" : _(u"Caisses"), "infobulle" : _(u"Param�trage des caisses"), "image" : "Images/16x16/Mecanisme.png", "action" : self.On_param_caisses},
                            {"code" : "categories_travail", "label" : _(u"Cat�gories socio-professionnelles"), "infobulle" : _(u"Param�trage des cat�gories socio-professionnelles"), "image" : "Images/16x16/Camion.png", "action" : self.On_param_categories_travail},
                            {"code" : "villes", "label" : _(u"Villes et codes postaux"), "infobulle" : _(u"Param�trage des villes et codes postaux"), "image" : "Images/16x16/Carte.png", "action" : self.On_param_villes},
                            {"code" : "secteurs", "label" : _(u"Secteurs g�ographiques"), "infobulle" : _(u"Param�trage des secteurs g�ographiques"), "image" : "Images/16x16/Secteur.png", "action" : self.On_param_secteurs},
                            {"code" : "types_sieste", "label" : _(u"Types de sieste"), "infobulle" : _(u"Param�trage des types de sieste"), "image" : "Images/16x16/Reveil.png", "action" : self.On_param_types_sieste},
                            {"code" : "maladies", "label" : _(u"Maladies"), "infobulle" : _(u"Param�trage des maladies"), "image" : "Images/16x16/Medical.png", "action" : self.On_param_maladies},
                            {"code" : "vaccins", "label" : _(u"Vaccins"), "infobulle" : _(u"Param�trage des vaccins"), "image" : "Images/16x16/Seringue.png", "action" : self.On_param_vaccins},
                            {"code" : "medecins", "label" : _(u"M�decins"), "infobulle" : _(u"Param�trage des m�decins"), "image" : "Images/16x16/Medecin.png", "action" : self.On_param_medecins},
                            ],
                    },
                    {"code" : "menu_parametrage_scolarite", "label" : _(u"Scolarit�"), "items" : [
                            {"code" : "niveaux_scolaires", "label" : _(u"Niveaux scolaires"), "infobulle" : _(u"Param�trage des niveaux scolaires"), "image" : "Images/16x16/Niveau_scolaire.png", "action" : self.On_param_niveaux_scolaires},
                            "-",
                            {"code" : "ecoles", "label" : _(u"Ecoles"), "infobulle" : _(u"Param�trage des �coles"), "image" : "Images/16x16/Ecole.png", "action" : self.On_param_ecoles},
                            {"code" : "classes", "label" : _(u"Classes"), "infobulle" : _(u"Param�trage des classes"), "image" : "Images/16x16/Classe.png", "action" : self.On_param_classes},
                            ],
                    },
                    {"code" : "menu_parametrage_transports", "label" : _(u"Transports"), "items" : [
                            {"code" : "menu_parametrage_transports_bus", "label" : _(u"Bus"), "items" : [
                                    {"code" : "compagnies_bus", "label" : _(u"Compagnies de bus"), "infobulle" : _(u"Param�trage des compagnies de bus"), "image" : "Images/16x16/Bus.png", "action" : self.On_param_compagnies_bus},
                                    {"code" : "lignes_bus", "label" : _(u"Lignes de bus"), "infobulle" : _(u"Param�trage des lignes de bus"), "image" : "Images/16x16/Bus.png", "action" : self.On_param_lignes_bus},
                                    {"code" : "arrets_bus", "label" : _(u"Arr�ts de bus"), "infobulle" : _(u"Param�trage des arr�ts de bus"), "image" : "Images/16x16/Bus.png", "action" : self.On_param_arrets_bus},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_car", "label" : _(u"Car"), "items" : [
                                    {"code" : "compagnies_cars", "label" : _(u"Compagnies de cars"), "infobulle" : _(u"Param�trage des compagnies de cars"), "image" : "Images/16x16/Car.png", "action" : self.On_param_compagnies_car},
                                    {"code" : "lignes_cars", "label" : _(u"Lignes de cars"), "infobulle" : _(u"Param�trage des lignes de cars"), "image" : "Images/16x16/Car.png", "action" : self.On_param_lignes_car},
                                    {"code" : "arrets_cars", "label" : _(u"Arr�ts de cars"), "infobulle" : _(u"Param�trage des arr�ts de cars"), "image" : "Images/16x16/Car.png", "action" : self.On_param_arrets_car},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_navette", "label" : _(u"Navette"), "items" : [
                                    {"code" : "compagnies_navettes", "label" : _(u"Compagnies de navettes"), "infobulle" : _(u"Param�trage des compagnies de navettes"), "image" : "Images/16x16/Navette.png", "action" : self.On_param_compagnies_navette},
                                    {"code" : "lignes_navettes", "label" : _(u"Lignes de navettes"), "infobulle" : _(u"Param�trage des lignes de navettes"), "image" : "Images/16x16/Navette.png", "action" : self.On_param_lignes_navette},
                                    {"code" : "arrets_navettes", "label" : _(u"Arr�ts de navettes"), "infobulle" : _(u"Param�trage des arr�ts de navettes"), "image" : "Images/16x16/Navette.png", "action" : self.On_param_arrets_navette},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_taxi", "label" : _(u"Taxi"), "items" : [
                                    {"code" : "compagnies_taxis", "label" : _(u"Compagnies de taxis"), "infobulle" : _(u"Param�trage des compagnies de taxis"), "image" : "Images/16x16/Taxi.png", "action" : self.On_param_compagnies_taxi},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_train", "label" : _(u"Train"), "items" : [
                                    {"code" : "lieux_gares", "label" : _(u"Gares"), "infobulle" : _(u"Param�trage des gares"), "image" : "Images/16x16/Train.png", "action" : self.On_param_lieux_gares},
                                    {"code" : "compagnies_trains", "label" : _(u"Compagnies de trains"), "infobulle" : _(u"Param�trage des compagnies de trains"), "image" : "Images/16x16/Train.png", "action" : self.On_param_compagnies_train},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_avion", "label" : _(u"Avion"), "items" : [
                                    {"code" : "lieux_aeroports", "label" : _(u"A�roports"), "infobulle" : _(u"Param�trage des a�roports"), "image" : "Images/16x16/Avion.png", "action" : self.On_param_lieux_aeroports},
                                    {"code" : "compagnies_avions", "label" : _(u"Compagnies a�riennes"), "infobulle" : _(u"Param�trage des compagnies a�riennes"), "image" : "Images/16x16/Avion.png", "action" : self.On_param_compagnies_avion},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_bateau", "label" : _(u"Bateau"), "items" : [
                                    {"code" : "lieux_ports", "label" : _(u"Ports"), "infobulle" : _(u"Param�trage des ports"), "image" : "Images/16x16/Bateau.png", "action" : self.On_param_lieux_ports},
                                    {"code" : "compagnies_bateaux", "label" : _(u"Compagnies maritimes"), "infobulle" : _(u"Param�trage des compagnies maritimes"), "image" : "Images/16x16/Bateau.png", "action" : self.On_param_compagnies_bateau},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_metro", "label" : _(u"M�tro"), "items" : [
                                    {"code" : "compagnies_metros", "label" : _(u"Compagnies de m�tros"), "infobulle" : _(u"Param�trage des compagnies de m�tros"), "image" : "Images/16x16/Metro.png", "action" : self.On_param_compagnies_metro},
                                    {"code" : "lignes_metros", "label" : _(u"Lignes de m�tros"), "infobulle" : _(u"Param�trage des lignes de m�tros"), "image" : "Images/16x16/Metro.png", "action" : self.On_param_lignes_metro},
                                    {"code" : "arrets_metros", "label" : _(u"Arr�ts de m�tros"), "infobulle" : _(u"Param�trage des arr�ts de m�tros"), "image" : "Images/16x16/Metro.png", "action" : self.On_param_arrets_metro},
                                    ],
                            },
                            {"code" : "menu_parametrage_transports_pedibus", "label" : _(u"P�dibus"), "items" : [
                                    {"code" : "lignes_pedibus", "label" : _(u"Lignes de p�dibus"), "infobulle" : _(u"Param�trage des lignes de p�dibus"), "image" : "Images/16x16/Pedibus.png", "action" : self.On_param_lignes_pedibus},
                                    {"code" : "arrets_pedibus", "label" : _(u"Arr�ts de p�dibus"), "infobulle" : _(u"Param�trage des arr�ts de p�dibus"), "image" : "Images/16x16/Pedibus.png", "action" : self.On_param_arrets_pedibus},
                                    ],
                            },
                            ],
                    },
                    "-",
                    {"code" : "categories_messages", "label" : _(u"Cat�gories de messages"), "infobulle" : _(u"Param�trage des cat�gories de messages"), "image" : "Images/16x16/Mail.png", "action" : self.On_param_categories_messages},
                    {"code" : "restaurateurs", "label" : _(u"Restaurateurs"), "infobulle" : _(u"Param�trage des restaurateurs"), "image" : "Images/16x16/Restaurateur.png", "action" : self.On_param_restaurateurs},
                    {"code" : "adresses_exp_mails", "label" : _(u"Adresses d'exp�dition d'Emails"), "infobulle" : _(u"Param�trage des adresses d'exp�dition d'Emails"), "image" : "Images/16x16/Emails_exp.png", "action" : self.On_param_emails_exp},
                    {"code" : "listes_diffusion", "label" : _(u"Listes de diffusion"), "infobulle" : _(u"Param�trage des listes de diffusion"), "image" : "Images/16x16/Liste_diffusion.png", "action" : self.On_param_listes_diffusion},
                    "-",
                    {"code" : "menu_parametrage_calendrier", "label" : _(u"Calendrier"), "items" : [
                            {"code" : "vacances", "label" : _(u"Vacances"), "infobulle" : _(u"Param�trage des vacances"), "image" : "Images/16x16/Calendrier.png", "action" : self.On_param_vacances},
                            {"code" : "feries", "label" : _(u"Jours f�ri�s"), "infobulle" : _(u"Param�trage des jours f�ri�s"), "image" : "Images/16x16/Jour.png", "action" : self.On_param_feries},
                            ],
                    },
                    ],
            },

            # Affichage
            {"code" : "menu_affichage", "label" : _(u"Affichage"), "items" : [
                    {"code" : "perspective_defaut", "label" : _(u"Disposition par d�faut"), "infobulle" : _(u"Afficher la disposition par d�faut"), "action" : self.On_affichage_perspective_defaut, "genre" : wx.ITEM_CHECK},
                    "-",
                    {"code" : "perspective_save", "label" : _(u"Sauvegarder la disposition actuelle"), "infobulle" : _(u"Sauvegarder la disposition actuelle"), "image" : "Images/16x16/Perspective_ajouter.png", "action" : self.On_affichage_perspective_save},
                    {"code" : "perspective_suppr", "label" : _(u"Supprimer des dispositions"), "infobulle" : _(u"Supprimer des dispositions enregistr�es"), "image" : "Images/16x16/Perspective_supprimer.png", "action" : self.On_affichage_perspective_suppr},
                    "-",
                    "-",
                    {"code" : "affichage_barres_outils", "label" : _(u"Barres d'outils personnelles"), "infobulle" : _(u"Barres d'outils personnelles"), "image" : "Images/16x16/Barre_outils.png", "action" : self.On_affichage_barres_outils},
                    "-",
                    {"code" : "actualiser_affichage", "label" : _(u"Actualiser l'affichage\tF11"), "infobulle" : _(u"Actualiser l'affichage de la page d'accueil"), "image" : "Images/16x16/Actualiser2.png", "action" : self.On_affichage_actualiser},
                    ],
            },

            # Outils
            {"code" : "menu_outils", "label" : _(u"Outils"), "items" : [
                    {"code" : "statistiques", "label" : _(u"Statistiques"), "infobulle" : _(u"Statistiques"), "image" : "Images/16x16/Barres.png", "action" : self.On_outils_stats},
                    "-",
                    {"code" : "nomadhys_synchro", "label" : _(u"Synchroniser Nomadhys"), "infobulle" : _(u"Synchroniser Nomadhys, l'application nomade de Noethys"), "image" : "Images/16x16/Nomadhys.png", "action" : self.On_outils_nomadhys_synchro},
                    "-",
                    {"code" : "editeur_emails", "label" : _(u"Editeur d'Emails"), "infobulle" : _(u"Editeur d'Emails"), "image" : "Images/16x16/Editeur_email.png", "action" : self.On_outils_emails},
                    {"code" : "calculatrice", "label" : _(u"Calculatrice\tF12"), "infobulle" : _(u"Calculatrice"), "image" : "Images/16x16/Calculatrice.png", "action" : self.On_outils_calculatrice},
                    {"code" : "calendrier", "label" : _(u"Calendrier"), "infobulle" : _(u"Calendrier"), "image" : "Images/16x16/Calendrier.png", "action" : self.On_outils_calendrier},
                    "-",
                    {"code" : "villes2", "label" : _(u"Villes et codes postaux"), "infobulle" : _(u"Villes et codes postaux"), "image" : "Images/16x16/Carte.png", "action" : self.On_outils_villes},
                    {"code" : "geolocalisation", "label" : _(u"G�olocalisation GPS"), "infobulle" : _(u"G�olocalisation GPS"), "image" : "Images/16x16/Carte.png", "action" : self.On_outils_gps},
                    {"code" : "meteo", "label" : _(u"Pr�visions m�t�orologiques"), "infobulle" : _(u"Pr�visions m�t�orologiques"), "image" : "Images/16x16/Meteo.png", "action" : self.On_outils_meteo},
                    {"code" : "horaires_soleil", "label" : _(u"Horaires du soleil"), "infobulle" : _(u"Horaires du soleil"), "image" : "Images/16x16/Soleil.png", "action" : self.On_outils_horaires_soleil},
                    "-",
                    {"code" : "connexions_reseau", "label" : _(u"Liste des connexions r�seau"), "infobulle" : _(u"Liste des connexions r�seau"), "image" : "Images/16x16/Connexion.png", "action" : self.On_outils_connexions},
                    "-",
                    {"code" : "messages", "label" : _(u"Messages"), "infobulle" : _(u"Liste des messages"), "image" : "Images/16x16/Mail.png", "action" : self.On_outils_messages},
                    {"code" : "historique", "label" : _(u"Historique"), "infobulle" : _(u"Historique"), "image" : "Images/16x16/Historique.png", "action" : self.On_outils_historique},
                    {"code" : "menu_outils_utilitaires", "label" : _(u"Utilitaires administrateur"), "items" : [
                            {"code" : "correcteur", "label" : _(u"Correcteur d'anomalies"), "infobulle" : _(u"Correcteur d'anomalies"), "image" : "Images/16x16/Depannage.png", "action" : self.On_outils_correcteur},
                            "-",
                            {"code" : "purger_historique", "label" : _(u"Purger l'historique"), "infobulle" : _(u"Purger l'historique"), "image" : "Images/16x16/Poubelle.png", "action" : self.On_outils_purger_historique},
                            {"code" : "purger_journal_badgeage", "label" : _(u"Purger le journal de badgeage"), "infobulle" : _(u"Purger le journal de badgeage"), "image" : "Images/16x16/Poubelle.png", "action" : self.On_outils_purger_journal_badgeage},
                            {"code" : "purger_archives_badgeage", "label" : _(u"Purger les archives des badgeages import�s"), "infobulle" : _(u"Purger les archives des badgeages import�s"), "image" : "Images/16x16/Poubelle.png", "action" : self.On_outils_purger_archives_badgeage},
                            {"code" : "purger_repertoire_updates", "label" : _(u"Purger le r�pertoire Updates"), "infobulle" : _(u"Purger le r�pertoire Updates"), "image" : "Images/16x16/Poubelle.png", "action" : self.On_outils_purger_rep_updates},
                            "-",
                            {"code" : "extensions", "label" : _(u"Extensions"), "infobulle" : _(u"Extensions"), "image" : "Images/16x16/Terminal.png", "action" : self.On_outils_extensions},
                            {"code" : "procedures", "label" : _(u"Proc�dures"), "infobulle" : _(u"Proc�dures"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_procedures},
                            {"code" : "reinitialisation", "label" : _(u"R�initialisation du fichier de configuration"), "infobulle" : _(u"R�initialisation du fichier de configuration"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_reinitialisation},
                            {"code" : "transfert_tables", "label" : _(u"Transf�rer des tables"), "infobulle" : _(u"Transf�rer des tables de donn�es"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_transfert_tables},
                            "-",
                            {"code" : "suppression_prestations_sans_conso", "label" : _(u"Suppression des prestations sans consommations associ�es"), "infobulle" : _(u"Suppression des prestations sans conso. associ�es"), "image" : "Images/16x16/Medecin3.png", "action" : self.On_outils_procedure_e4072},
                            {"code" : "liste_prestations_sans_conso", "label" : _(u"Liste des prestations sans consommations associ�es"), "infobulle" : _(u"Liste des prestations sans conso. associ�es"), "image" : "Images/16x16/Medecin3.png", "action" : self.On_outils_prestations_sans_conso},
                            {"code" : "liste_conso_sans_prestations", "label" : _(u"Liste des consommations sans prestations associ�es"), "infobulle" : _(u"Liste des conso. sans prestations associ�es"), "image" : "Images/16x16/Medecin3.png", "action" : self.On_outils_conso_sans_prestations},
                            {"code" : "deverrouillage_forfaits", "label" : _(u"D�verrouillage des consommations de forfaits"), "infobulle" : _(u"D�verrouillage des consommations de forfaits"), "image" : "Images/16x16/Medecin3.png", "action" : self.On_outils_deverrouillage_forfaits},
                            "-",
                            {"code" : "appliquer_tva", "label" : _(u"Appliquer un taux de TVA � un lot de prestations"), "infobulle" : _(u"Appliquer un taux de TVA � un lot de prestations"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_appliquer_tva},
                            {"code" : "appliquer_code_comptable", "label" : _(u"Appliquer un code comptable � un lot de prestations"), "infobulle" : _(u"Appliquer un code comptable � des prestations"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_appliquer_code_comptable},
                            {"code" : "conversion_rib_sepa", "label" : _(u"Convertir les RIB nationaux en mandats SEPA"), "infobulle" : _(u"Convertir les RIB nationaux en mandats SEPA"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_conversion_rib_sepa},
                            {"code" : "creation_titulaires_helios", "label" : _(u"Cr�ation automatique des titulaires H�lios"), "infobulle" : _(u"Cr�ation automatique des titulaires H�lios"), "image" : "Images/16x16/Outils.png", "action" : self.On_outils_creation_titulaires_helios},
                            "-",
                            {"code" : "console_python", "label" : _(u"Console Python"), "infobulle" : _(u"Console Python"), "image" : "Images/16x16/Python.png", "action" : self.On_outils_console_python},
                            {"code" : "console_sql", "label" : _(u"Console SQL"), "infobulle" : _(u"Console SQL"), "image" : "Images/16x16/Sql.png", "action" : self.On_outils_console_sql},
                            {"code" : "liste_perso", "label" : _(u"Liste personnalis�e SQL"), "infobulle" : _(u"Liste personnalis�e SQL"), "image" : "Images/16x16/Sql.png", "action" : self.On_outils_liste_perso},
                            ],
                    },
                    "-",
                    {"code" : "traductions", "label" : _(u"Traduire le logiciel"), "infobulle" : _(u"Traduire le logiciel"), "image" : "Images/16x16/Traduction.png", "action" : self.On_outils_traductions},
                    {"code" : "updater", "label" : _(u"Rechercher une mise � jour du logiciel"), "infobulle" : _(u"Rechercher une mise � jour du logiciel"), "image" : "Images/16x16/Updater.png", "action" : self.On_outils_updater},
                    ],
            },

            # Individus
            {"code" : "menu_individus", "label" : _(u"Individus"), "items" : [
                    {"code" : "scolarite", "label" : _(u"Inscriptions scolaires"), "infobulle" : _(u"Inscriptions scolaires"), "image" : "Images/16x16/Classe.png", "action" : self.On_individus_scolarite},
                    "-",
                    {"code" : "liste_inscriptions", "label" : _(u"Liste des inscriptions"), "infobulle" : _(u"Editer une liste des inscriptions"), "image" : "Images/16x16/Activite.png", "action" : self.On_individus_inscriptions},
                    {"code" : "saisir_lot_inscriptions", "label" : _(u"Saisir un lot d'inscriptions"), "infobulle" : _(u"Saisir un lot d'inscriptions"), "image" : "Images/16x16/Activite.png", "action" : self.On_individus_saisir_lot_inscriptions},
                    "-",
                    {"code" : "liste_contrats", "label" : _(u"Liste des contrats"), "infobulle" : _(u"Editer une liste des contrats"), "image" : "Images/16x16/Contrat.png", "action" : self.On_individus_contrats},
                    {"code" : "liste_individus", "label" : _(u"Liste des individus"), "infobulle" : _(u"Editer une liste des individus"), "image" : "Images/16x16/Personnes.png", "action" : self.On_individus_individus},
                    {"code" : "liste_familles", "label" : _(u"Liste des familles"), "infobulle" : _(u"Liste des familles"), "image" : "Images/16x16/Famille.png", "action" : self.On_individus_familles},
                    "-",
                    {"code" : "menu_individus_transports", "label" : _(u"Liste des transports"), "items" : [
                            {"code" : "liste_detail_transports", "label" : _(u"Liste r�capitulative"), "infobulle" : _(u"Editer une liste r�capitulative des transports"), "image" : "Images/16x16/Transport.png", "action" : self.On_individus_transports_recap},
                            {"code" : "liste_recap_transports", "label" : _(u"Liste d�taill�e"), "infobulle" : _(u"Editer une liste d�taill�e des transports"), "image" : "Images/16x16/Transport.png", "action" : self.On_individus_transports_detail},
                            ],
                    },
                    "-",
                    {"code" : "liste_anniversaires", "label" : _(u"Liste des anniversaires"), "infobulle" : _(u"Editer une liste des anniversaires"), "image" : "Images/16x16/Anniversaire.png", "action" : self.On_individus_anniversaires},
                    {"code" : "liste_infos_medicales", "label" : _(u"Liste des informations m�dicales"), "infobulle" : _(u"Editer une liste des informations m�dicales"), "image" : "Images/16x16/Medical.png", "action" : self.On_individus_infos_med},
                    {"code" : "liste_pieces_fournies", "label" : _(u"Liste des pi�ces fournies"), "infobulle" : _(u"Editer la liste des pi�ces fournies"), "image" : "Images/16x16/Piece.png", "action" : self.On_individus_pieces_fournies},
                    {"code" : "liste_pieces_fournies", "label" : _(u"Liste des pi�ces manquantes"), "infobulle" : _(u"Editer la liste des pi�ces manquantes"), "image" : "Images/16x16/Piece.png", "action" : self.On_individus_pieces_manquantes},
                    {"code" : "liste_regimes_caisses", "label" : _(u"Liste des r�gimes et caisses des familles"), "infobulle" : _(u"Editer la liste des r�gimes et caisses des familles"), "image" : "Images/16x16/Mecanisme.png", "action" : self.On_individus_regimes_caisses},
                    {"code" : "liste_quotients", "label" : _(u"Liste des quotients familiaux"), "infobulle" : _(u"Editer la liste des quotients familiaux des familles"), "image" : "Images/16x16/Calculatrice.png", "action" : self.On_individus_quotients},
                    {"code" : "liste_mandats_sepa", "label" : _(u"Liste des mandats SEPA"), "infobulle" : _(u"Editer la liste des mandats SEPA"), "image" : "Images/16x16/Prelevement.png", "action" : self.On_individus_mandats},
                    "-",
                    {"code" : "importer_photos", "label" : _(u"Importer des photos individuelles"), "infobulle" : _(u"Importer des photos individuelles"), "image" : "Images/16x16/Photos.png", "action" : self.On_individus_importer_photos},
                    {"code" : "menu_individus_importation", "label" : _(u"Importer des familles ou des individus"), "items" : [
                            {"code" : "importation_individus_csv", "label" : _(u"Importer des individus ou des familles depuis un fichier Excel ou CSV"), "infobulle" : _(u"Importer des individus ou des familles"), "image" : "Images/16x16/Document_import.png", "action" : self.On_individus_importer_csv},
                            {"code" : "importation_individus_fichier", "label" : _(u"Importer des familles depuis un fichier Noethys"), "infobulle" : _(u"Importer des familles depuis un fichier Noethys"), "image" : "Images/16x16/Document_import.png", "action" : self.On_individus_importer_fichier},
                            ],
                    },
                    "-",
                    {"code" : "individus_edition_etiquettes", "label" : _(u"Edition d'�tiquettes et de badges"), "infobulle" : _(u"Edition d'�tiquettes et de badges au format PDF"), "image" : "Images/16x16/Etiquette2.png", "action" : self.On_individus_edition_etiquettes},
                    ],
            },
                    
            # Consommations
            {"code" : "menu_consommations", "label" : _(u"Consommations"), "items" : [
                    {"code" : "liste_consommations", "label" : _(u"Liste des consommations"), "infobulle" : _(u"Editer une liste des consommations"), "image" : "Images/16x16/Imprimante.png", "action" : self.On_imprim_conso_journ},
                    {"code" : "gestionnaire_conso", "label" : _(u"Gestionnaire des consommations"), "infobulle" : _(u"Gestionnaire des consommations"), "image" : "Images/16x16/Calendrier.png", "action" : self.On_conso_gestionnaire},
                    "-",
                    {"code" : "liste_attente", "label" : _(u"Liste d'attente"), "infobulle" : _(u"Liste d'attente"), "image" : "Images/16x16/Liste_attente.png", "action" : self.On_conso_attente},
                    {"code" : "liste_refus", "label" : _(u"Liste des places refus�es"), "infobulle" : _(u"Liste des places refus�es"), "image" : "Images/16x16/Places_refus.png", "action" : self.On_conso_refus},
                    {"code" : "liste_absences", "label" : _(u"Liste des absences"), "infobulle" : _(u"Liste des absences"), "image" : "Images/16x16/absenti.png", "action" : self.On_conso_absences},
                    "-",
                    {"code" : "synthese_conso", "label" : _(u"Synth�se des consommations"), "infobulle" : _(u"Synth�se des consommations"), "image" : "Images/16x16/Diagramme.png", "action" : self.On_conso_synthese_conso},
                    {"code" : "etat_global", "label" : _(u"Etat global"), "infobulle" : _(u"Etat global"), "image" : "Images/16x16/Tableaux.png", "action" : self.On_conso_etat_global},
                    {"code" : "etat_nominatif", "label" : _(u"Etat nominatif"), "infobulle" : _(u"Etat nominatif"), "image" : "Images/16x16/Tableaux.png", "action" : self.On_conso_etat_nominatif},
                    "-",
                    {"code" : "badgeage", "label" : _(u"Badgeage"), "infobulle" : _(u"Badgeage"), "image" : "Images/16x16/Badgeage.png", "action" : self.On_conso_badgeage},
                    ],
            },

            # Facturation
            {"code" : "menu_facturation", "label" : _(u"Facturation"), "items" : [
                    {"code" : "facturation_verification_ventilation", "label" : _(u"V�rifier la ventilation"), "infobulle" : _(u"V�rifier la ventilation des r�glements"), "image" : "Images/16x16/Repartition.png", "action" : self.On_reglements_ventilation},
                    "-",
                    {"code" : "menu_facturation_factures", "label" : _(u"Factures"), "items" : [
                            {"code" : "factures_generation", "label" : _(u"G�n�ration"), "infobulle" : _(u"G�n�ration des factures"), "image" : "Images/16x16/Generation.png", "action" : self.On_facturation_factures_generation},
                            "-",
                            {"code" : "factures_helios", "label" : _(u"Export vers H�lios"), "infobulle" : _(u"Exporter les factures vers H�lios"), "image" : "Images/16x16/Helios.png", "action" : self.On_facturation_factures_helios},
                            {"code" : "factures_prelevement", "label" : _(u"Pr�l�vement automatique"), "infobulle" : _(u"Gestion du pr�l�vement automatique"), "image" : "Images/16x16/Prelevement.png", "action" : self.On_facturation_factures_prelevement},
                            {"code" : "factures_email", "label" : _(u"Transmettre par Email"), "infobulle" : _(u"Transmettre les factures par Email"), "image" : "Images/16x16/Emails_exp.png", "action" : self.On_facturation_factures_email},
                            {"code" : "factures_imprimer", "label" : _(u"Imprimer"), "infobulle" : _(u"Imprimer des factures"), "image" : "Images/16x16/Imprimante.png", "action" : self.On_facturation_factures_imprimer},
                            "-",
                            {"code" : "factures_liste", "label" : _(u"Liste des factures"), "infobulle" : _(u"Liste des factures g�n�r�es"), "image" : "Images/16x16/Facture.png", "action" : self.On_facturation_factures_liste},
                            ],
                    },
                    {"code" : "menu_facturation_rappels", "label" : _(u"Lettres de rappel"), "items" : [
                            {"code" : "rappels_generation", "label" : _(u"G�n�ration"), "infobulle" : _(u"G�n�ration des lettres de rappel"), "image" : "Images/16x16/Generation.png", "action" : self.On_facturation_rappels_generation},
                            "-",
                            {"code" : "rappels_email", "label" : _(u"Transmettre par Email"), "infobulle" : _(u"Transmettre les lettres de rappel par Email"), "image" : "Images/16x16/Emails_exp.png", "action" : self.On_facturation_rappels_email},
                            {"code" : "rappels_imprimer", "label" : _(u"Imprimer"), "infobulle" : _(u"Imprimer des lettres de rappel"), "image" : "Images/16x16/Imprimante.png", "action" : self.On_facturation_rappels_imprimer},
                            "-",
                            {"code" : "rappels_liste", "label" : _(u"Liste des lettres de rappel"), "infobulle" : _(u"Liste des lettres de rappel"), "image" : "Images/16x16/Facture.png", "action" : self.On_facturation_rappels_liste},
                            ],
                    },
                    {"code" : "menu_facturation_attestations", "label" : _(u"Attestations de pr�sence"), "items" : [
                            {"code" : "attestations_generation", "label" : _(u"G�n�ration"), "infobulle" : _(u"G�n�ration des attestations de pr�sence"), "image" : "Images/16x16/Generation.png", "action" : self.On_facturation_attestations_generation},
                            {"code" : "attestations_liste", "label" : _(u"Liste des attestations de pr�sence"), "infobulle" : _(u"Liste des attestations de pr�sence g�n�r�es"), "image" : "Images/16x16/Facture.png", "action" : self.On_facturation_attestations_liste},
                            ],
                    },
                    {"code" : "menu_facturation_attestations_fiscales", "label" : _(u"Attestations fiscales"), "items" : [
                            {"code" : "attestations_fiscales_generation", "label" : _(u"G�n�ration"), "infobulle" : _(u"G�n�ration des attestations fiscales"), "image" : "Images/16x16/Generation.png", "action" : self.On_facturation_attestations_fiscales_generation},
                            ],
                    },
                    "-",
                    {"code" : "liste_prestations", "label" : _(u"Liste des prestations"), "infobulle" : _(u"Liste des prestations"), "image" : "Images/16x16/Euro.png", "action" : self.On_facturation_liste_prestations},
                    "-",
                    {"code" : "liste_deductions", "label" : _(u"Liste des d�ductions"), "infobulle" : _(u"Liste des d�ductions"), "image" : "Images/16x16/Euro.png", "action" : self.On_facturation_liste_deductions},
                    {"code" : "saisir_lot_deductions", "label" : _(u"Saisir un lot de d�ductions"), "infobulle" : _(u"Saisir un lot de d�ductions"), "image" : "Images/16x16/Impayes.png", "action" : self.On_facturation_saisir_deductions},
                    "-",
                    {"code" : "liste_soldes_familles", "label" : _(u"Liste des soldes"), "infobulle" : _(u"Liste des soldes des comptes familles"), "image" : "Images/16x16/Euro.png", "action" : self.On_facturation_soldes},
                    {"code" : "liste_soldes_individus", "label" : _(u"Liste des soldes individuels"), "infobulle" : _(u"Liste des soldes individuels"), "image" : "Images/16x16/Euro.png", "action" : self.On_facturation_soldes_individuels},
                    "-",
                    {"code" : "synthese_impayes", "label" : _(u"Synth�se des impay�s"), "infobulle" : _(u"Synth�se des impay�s"), "image" : "Images/16x16/Diagramme.png", "action" : self.On_facturation_synthese_impayes},
                    {"code" : "solder_impayes", "label" : _(u"Solder les impay�s"), "infobulle" : _(u"Solder les impay�s"), "image" : "Images/16x16/Impayes.png", "action" : self.On_facturation_solder_impayes},
                    "-",
                    {"code" : "synthese_prestations", "label" : _(u"Synth�se des prestations"), "infobulle" : _(u"Synth�se des prestations"), "image" : "Images/16x16/Diagramme.png", "action" : self.On_facturation_synthese_prestations},
                    {"code" : "prestations_villes", "label" : _(u"Liste des prestations par famille"), "infobulle" : _(u"Liste des prestations par famille"), "image" : "Images/16x16/Euro.png", "action" : self.On_facturation_prestations_villes},
                    "-",
                    {"code" : "export_compta", "label" : _(u"Export des �critures comptables"), "infobulle" : _(u"Exporter les �critures comptables"), "image" : "Images/16x16/Export_comptable.png", "action" : self.On_facturation_export_compta},
                    ],
            },
            
            # Cotisations
            {"code" : "menu_cotisations", "label" : _(u"Cotisations"), "items" : [
                    {"code" : "liste_cotisations", "label" : _(u"Liste des cotisations"), "infobulle" : _(u"Liste des cotisations"), "image" : "Images/16x16/Cotisation.png", "action" : self.On_cotisations_recherche},
                    {"code" : "liste_cotisations_manquantes", "label" : _(u"Liste des cotisations manquantes"), "infobulle" : _(u"Liste des cotisations manquantes"), "image" : "Images/16x16/Cotisation.png", "action" : self.On_cotisations_manquantes},
                    "-",
                    {"code" : "cotisations_email", "label" : _(u"Transmettre des cotisations par Email"), "infobulle" : _(u"Transmettre des cotisations par Email"), "image" : "Images/16x16/Emails_exp.png", "action" : self.On_cotisations_email},
                    {"code" : "cotisations_imprimer", "label" : _(u"Imprimer des cotisations"), "infobulle" : _(u"Imprimer une ou plusieurs cotisations"), "image" : "Images/16x16/Imprimante.png", "action" : self.On_cotisations_imprimer},
                    "-",
                    {"code" : "cotisations_depots", "label" : _(u"Gestion des d�p�ts de cotisations"), "infobulle" : _(u"Gestion des d�p�ts de cotisations"), "image" : "Images/16x16/Depot_cotisations.png", "action" : self.On_cotisations_depots},
                    ],
            },
            
            # R�glements
            {"code" : "menu_reglements", "label" : _(u"R�glements"), "items" : [
                    {"code" : "regler_facture", "label" : _(u"R�gler une facture\tF4"), "infobulle" : _(u"R�gler une facture � partir de son num�ro"), "image" : "Images/16x16/Codebarre.png", "action" : self.On_reglements_regler_facture},
                    "-",
                    {"code" : "liste_recus_reglements", "label" : _(u"Liste des re�us de r�glements"), "infobulle" : _(u"Consulter la liste des re�us de r�glements"), "image" : "Images/16x16/Note.png", "action" : self.On_reglements_recus},
                    {"code" : "liste_reglements", "label" : _(u"Liste des r�glements"), "infobulle" : _(u"Consulter la liste des r�glements"), "image" : "Images/16x16/Reglement.png", "action" : self.On_reglements_recherche},
                    "-",
                    {"code" : "reglements_verification_ventilation", "label" : _(u"V�rifier la ventilation"), "infobulle" : _(u"V�rifier la ventilation des r�glements"), "image" : "Images/16x16/Repartition.png", "action" : self.On_reglements_ventilation},
                    {"code" : "analyse_ventilation", "label" : _(u"Tableau d'analyse crois�e ventilation/d�p�ts"), "infobulle" : _(u"Tableau d'analyse crois�e ventilation/d�p�ts"), "image" : "Images/16x16/Diagramme.png", "action" : self.On_reglements_analyse_ventilation},
                    {"code" : "syntheses_modes_reglements", "label" : _(u"Synth�se des modes de r�glements"), "infobulle" : _(u"Synth�se des modes de r�glements"), "image" : "Images/16x16/Diagramme.png", "action" : self.On_reglements_synthese_modes},
                    "-",
                    {"code" : "reglements_prelevement", "label" : _(u"Pr�l�vement automatique"), "infobulle" : _(u"Gestion du pr�l�vement automatique"), "image" : "Images/16x16/Prelevement.png", "action" : self.On_facturation_factures_prelevement},
                    {"code" : "reglements_depots", "label" : _(u"Gestion des d�p�ts"), "infobulle" : _(u"Gestion des d�p�ts de r�glements"), "image" : "Images/16x16/Banque.png", "action" : self.On_reglements_depots},
                    ],
            },

            # Comptabilit�
            {"code" : "menu_comptabilite", "label" : _(u"Comptabilit�"), "items" : [
                    {"code" : "liste_comptes", "label" : _(u"Liste des comptes"), "infobulle" : _(u"Consulter ou modifier la liste des comptes"), "image" : "Images/16x16/Operations.png", "action" : self.On_Comptabilite_comptes},
                    {"code" : "liste_operations_tresorerie", "label" : _(u"Liste des op�rations de tr�sorerie"), "infobulle" : _(u"Consulter ou modifier la liste des op�rations de tr�sorerie"), "image" : "Images/16x16/Operations.png", "action" : self.On_Comptabilite_operations_tresorerie},
                    {"code" : "liste_operations_budgetaires", "label" : _(u"Liste des op�rations budg�taires"), "infobulle" : _(u"Consulter ou modifier la liste des op�rations budg�taires"), "image" : "Images/16x16/Operations.png", "action" : self.On_Comptabilite_operations_budgetaires},
                    {"code" : "liste_virements", "label" : _(u"Liste des virements"), "infobulle" : _(u"Consulter ou modifier la liste des virements"), "image" : "Images/16x16/Operations.png", "action" : self.On_Comptabilite_virements},
                    "-",
                    {"code" : "rapprochement_bancaire", "label" : _(u"Rapprochement bancaire"), "infobulle" : _(u"Rapprochement bancaire"), "image" : "Images/16x16/Document_coches.png", "action" : self.On_Comptabilite_rapprochement},
                    "-",
                    {"code" : "suivi_tresorerie", "label" : _(u"Suivi de la tr�sorerie"), "infobulle" : _(u"Suivre la tr�sorerie"), "image" : "Images/16x16/Tresorerie.png", "action" : self.On_Comptabilite_tresorerie},
                    {"code" : "suivi_budgets", "label" : _(u"Suivi des budgets"), "infobulle" : _(u"Suivre les budgets"), "image" : "Images/16x16/Tresorerie.png", "action" : self.On_Comptabilite_budgets},
                    "-",
                    {"code" : "compta_graphiques", "label" : _(u"Graphiques"), "infobulle" : _(u"Graphiques"), "image" : "Images/16x16/Diagramme.png", "action" : self.On_Comptabilite_graphiques},
                    ],
            },

            # Aide
            {"code" : "menu_aide", "label" : _(u"Aide"), "items" : [
                    {"code" : "aide", "label" : _(u"Consulter l'aide"), "infobulle" : _(u"Consulter l'aide de Noethys"), "image" : "Images/16x16/Aide.png", "action" : self.On_aide_aide},
                    {"code" : "acheter_licence", "label" : _(u"Acheter une licence pour acc�der au manuel de r�f�rence"), "infobulle" : _(u"Acheter une licence"), "image" : "Images/16x16/Acheter_licence.png", "action" : self.On_propos_soutenir},
                    "-",
                    {"code" : "guide_demarrage", "label" : _(u"T�l�charger le guide de d�marrage rapide (PDF)"), "infobulle" : _(u"T�l�charger le guide de d�marrage rapide"), "image" : "Images/16x16/Livre.png", "action" : self.On_aide_guide_demarrage},
                    "-",
                    {"code" : "forum", "label" : _(u"Acc�der au forum d'entraide"), "infobulle" : _(u"Acc�der au forum d'entraide"), "image" : "Images/16x16/Dialogue.png", "action" : self.On_aide_forum},
                    {"code" : "tutoriels_videos", "label" : _(u"Visionner des tutoriels vid�os"), "infobulle" : _(u"Visionner des tutoriels vid�os"), "image" : "Images/16x16/Film.png", "action" : self.On_aide_videos},
                    {"code" : "telechargements_communautaires", "label" : _(u"T�l�charger des ressources communautaires"), "infobulle" : _(u"T�l�charger des ressources communautaires"), "image" : "Images/16x16/Updater.png", "action" : self.On_aide_telechargements},
                    "-",
                    {"code" : "email_auteur", "label" : _(u"Envoyer un Email � l'auteur"), "infobulle" : _(u"Envoyer un Email � l'auteur"), "image" : "Images/16x16/Mail.png", "action" : self.On_aide_auteur},
                    ],
            },

            # A propos
            {"code" : "menu_a_propos", "label" : _(u"A propos"), "items" : [
                    {"code" : "notes_versions", "label" : _(u"Notes de versions"), "infobulle" : _(u"Notes de versions"), "image" : "Images/16x16/Versions.png", "action" : self.On_propos_versions},
                    {"code" : "licence_logiciel", "label" : _(u"Licence"), "infobulle" : _(u"Licence du logiciel"), "image" : "Images/16x16/Licence.png", "action" : self.On_propos_licence},
                    "-",
                    {"code" : "soutenir_noethys", "label" : _(u"Soutenir Noethys"), "infobulle" : _(u"Soutenir Noethys"), "image" : "Images/16x16/Soutenir_noethys.png", "action" : self.On_propos_soutenir},
                    "-",
                    {"code" : "a_propos", "label" : _(u"A propos"), "infobulle" : _(u"A propos"), "image" : "Images/16x16/Information.png", "action" : self.On_propos_propos},
                    ],
            },

        ] 
        

        # Cr�ation du menu
        def CreationItem(menuParent, item):
            id = wx.NewId()
            if item.has_key("genre"):
                genre = item["genre"]
            else :
                genre = wx.ITEM_NORMAL
            itemMenu = wx.MenuItem(menuParent, id, item["label"], item["infobulle"], genre)
            if item.has_key("image") :
                itemMenu.SetBitmap(wx.Bitmap(item["image"], wx.BITMAP_TYPE_PNG))
            menuParent.AppendItem(itemMenu)
            if item.has_key("actif") :
                itemMenu.Enable(item["actif"])
            self.Bind(wx.EVT_MENU, item["action"], id=id)
            self.dictInfosMenu[item["code"]] = {"id" : id, "ctrl" : itemMenu}
            
        def CreationMenu(menuParent, item, sousmenu=False):
            menu = wx.Menu()
            id = wx.NewId()
            for sousitem in item["items"] :
                if sousitem == "-" :
                    menu.AppendSeparator()
                elif sousitem.has_key("items") :
                    CreationMenu(menu, sousitem, sousmenu=True)
                else :
                    CreationItem(menu, sousitem)
            if sousmenu == True :
                menuParent.AppendMenu(id, item["label"], menu)
            else :
                menuParent.Append(menu, item["label"])
            self.dictInfosMenu[item["code"]] = {"id" : id, "ctrl" : menu}

        self.menu = wx.MenuBar()
        self.dictInfosMenu = {}
        for item in self.listeItemsMenu :
            CreationMenu(self.menu, item)
        
        
        # -------------------------- AJOUT DES DERNIERS FICHIERS OUVERTS -----------------------------
        menu_fichier = self.dictInfosMenu["menu_fichier"]["ctrl"]

        # Int�gration des derniers fichiers ouverts :
        listeDerniersFichiersTmp = self.userConfig["derniersFichiers"]
        if len(listeDerniersFichiersTmp) > 0 :
            menu_fichier.AppendSeparator()
            
        # V�rification de la liste
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
                item = wx.MenuItem(menu_fichier, ID_DERNIER_FICHIER + index, u"%d. %s" % (index+1, nomFichier), _(u"Ouvrir le fichier : '%s'") % nomFichier)
                menu_fichier.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.On_fichier_DerniersFichiers, id=ID_DERNIER_FICHIER, id2=ID_DERNIER_FICHIER + index)

        # -------------------------- AJOUT DES PERSPECTIVES dans le menu AFFICHAGE -----------------------------
        if self.perspective_active == None : 
            self.dictInfosMenu["perspective_defaut"]["ctrl"].Check(True)
        
        index = 0
        position = 1
        menu_affichage = self.dictInfosMenu["menu_affichage"]["ctrl"]
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menu_affichage, ID_PREMIERE_PERSPECTIVE + index, label, _(u"Afficher la disposition '%s'") % label, wx.ITEM_CHECK)
            menu_affichage.InsertItem(position, item)
            if self.perspective_active == index : item.Check(True)
            position += 1
            index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=ID_PREMIERE_PERSPECTIVE, id2=ID_PREMIERE_PERSPECTIVE+99 )

        # -------------------------- AJOUT DES ELEMENTS A AFFICHER OU CACHER dans le menu AFFICHAGE -----------------------------
        self.listePanneaux = [
            { "label" : _(u"Effectifs"), "code" : "effectifs", "IDmenu" : None },
            { "label" : _(u"Messages"), "code" : "messages", "IDmenu" : None }, 
            { "label" : _(u"Eph�m�ride"), "code" : "ephemeride", "IDmenu" : None }, 
            { "label" : _(u"Barre de raccourcis"), "code" : "barre_raccourcis", "IDmenu" : None },
            { "label" : _(u"Barre utilisateur"), "code" : "barre_utilisateur", "IDmenu" : None },
            ]
        ID = ID_AFFICHAGE_PANNEAUX
        menu_affichage = self.dictInfosMenu["menu_affichage"]["ctrl"]
        position = self.RechercherPositionItemMenu("menu_affichage", "perspective_suppr") + 2
        for dictPanneau in self.listePanneaux :
            dictPanneau["IDmenu"] = ID
            label = dictPanneau["label"]
            item = wx.MenuItem(menu_affichage, dictPanneau["IDmenu"], label, _(u"Afficher l'�l�ment '%s'") % label, wx.ITEM_CHECK)
            menu_affichage.InsertItem(position, item)
            position += 1
            ID += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_panneau_afficher, id=ID_AFFICHAGE_PANNEAUX, id2=ID_AFFICHAGE_PANNEAUX+len(self.listePanneaux) )
        
        # -------------------------- AJOUT MISE A JOUR INTERNET -----------------------------
        if self.MAJexiste == True :
            id = wx.NewId()
            menu_maj = wx.Menu()
            item = wx.MenuItem(menu_maj, id, _(u"T�l�charger la mise � jour"), _(u"T�l�charger la nouvelle mise � jour"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_PNG))
            menu_maj.AppendItem(item)
            self.menu.Append(menu_maj, _(u"<< T�l�charger la mise � jour >>"))
            self.Bind(wx.EVT_MENU, self.On_outils_updater, id=id)

        # Finalisation Barre de menu
        self.SetMenuBar(self.menu)
        
    
    def GetDictItemsMenu(self):
        """ Renvoie tous les items menu de type action sous forme de dictionnaire """
        dictItems = {}
        def AnalyseItem(listeItems):
            for item in listeItems :
                if type(item) == dict :
                    if item.has_key("action") :
                        dictItems[item["code"]] = item
                    if item.has_key("items") :
                        AnalyseItem(item["items"])
        
        AnalyseItem(self.listeItemsMenu)
        return dictItems


    
    def RechercherPositionItemMenu(self, codeMenu="", codeItem=""):
        menu = self.dictInfosMenu[codeMenu]["ctrl"]
        IDitem = self.dictInfosMenu[codeItem]["id"]
        index = 0
        for item in menu.GetMenuItems() :
            if item.GetId() == IDitem :
                return index
            index +=1
        return 0
    
    def MAJmenuAffichage(self, event):
        """ Met � jour la liste des panneaux ouverts du menu Affichage """
        menuOuvert = event.GetMenu()
        if menuOuvert == self.dictInfosMenu["menu_affichage"]["ctrl"] :
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
        """ Cod� pour le panneau Ephemeride """
        self.ParadeAffichagePanneau(nom)
##        if nom not in self.perspectives[self.perspective_active]["perspective"] :
##            # Affichage forc� du panneau
##            self._mgr.GetPane(nom).Show()
##            self._mgr.Update()
##            # Modification de la perspective sauvegard�e
##            self.perspectives[self.perspective_active]["perspective"] = self._mgr.SavePerspective()
    
    def SauvegardePerspectiveActive(self):
        """ Sauvegarde la perspective active """
        if self.perspective_active != None :
            self.perspectives[self.perspective_active]["perspective"] = self._mgr.SavePerspective()

    def SupprimeToutesPerspectives(self):
        """ Supprime toutes les perspectives et s�lectionne celle par d�faut """
        dlg = wx.MessageDialog(self, _(u"Suite � la mise � jour de Noethys, %d disposition(s) personnalis�e(s) de la page d'accueil sont d�sormais obsol�tes.\n\nPour les besoins de la nouvelle version, elles vont �tre supprim�es. Mais il vous suffira de les recr�er simplement depuis le menu Affichage... Merci de votre compr�hension !") % len(self.perspectives), _(u"Mise � jour"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        # Suppression
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None
        self.perspectives = []
        self.MAJmenuPerspectives() 
        print "Toutes les perspectives ont ete supprimees."
        
    def ParadeAffichagePanneau(self, nom=""):
        """ Supprime toutes les perspectives si le panneau donn� n'apparait pas """
        pb = False
        for perspective in self.perspectives :
            if nom not in perspective["perspective"] :
                pb = True
        if pb == True :
            self.SupprimeToutesPerspectives() 
        
    def CreationBinds(self):        
        # Autres
        self.Bind(wx.EVT_MENU_OPEN, self.MAJmenuAffichage)
        
        # Barre d'outils
        self.Bind(wx.EVT_TOOL, self.On_conso_gestionnaire, id=ID_TB_GESTIONNAIRE)
        self.Bind(wx.EVT_TOOL, self.On_imprim_conso_journ, id=ID_TB_LISTE_CONSO)
        self.Bind(wx.EVT_TOOL, self.On_conso_badgeage, id=ID_TB_BADGEAGE)
        self.Bind(wx.EVT_TOOL, self.On_reglements_regler_facture, id=ID_TB_REGLER_FACTURE)
        self.Bind(wx.EVT_TOOL, self.On_outils_calculatrice, id=ID_TB_CALCULATRICE)
        
    def MAJ(self):
        """ Met � jour la page d'accueil """
        self.ctrl_remplissage.MAJ() 
        self.ctrl_individus.MAJ()
        self.ctrl_messages.MAJ() 
        if hasattr(self, "ctrl_serveur_nomade") :
            self.ctrl_serveur_nomade.MAJ()
        wx.CallAfter(self.ctrl_individus.ctrl_recherche.SetFocus)

    def On_fichier_Nouveau(self, event):
        """ Cr�� une nouvelle base de donn�es """
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
        
        # Affiche d'une fen�tre d'attente
        message = _(u"Cr�ation du nouveau fichier en cours... Veuillez patienter...")
        dlgAttente = PBI.PyBusyInfo(message, parent=None, title=_(u"Cr�ation d'un fichier"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
            
        if "[RESEAU]" in nomFichier :
            self.SetStatusText(_(u"Cr�ation du fichier '%s' en cours...") % nomFichier[nomFichier.index("[RESEAU]"):])
        else:
            self.SetStatusText(_(u"Cr�ation du fichier '%s' en cours...") % nomFichier)
        
        # V�rification de validit� du fichier
        if nomFichier == "" :
            del dlgAttente
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(_(u"Echec de la cr�ation du fichier '%s' : nom du fichier non valide.") % nomFichier)
            return False

        if "[RESEAU]" not in nomFichier :
            # Version LOCAL
            
            # V�rifie si un fichier ne porte pas d�j� ce nom :
            fichier = "Data/" + nomFichier + "_DATA.dat"
            test = os.path.isfile(fichier) 
            if test == True :
                del dlgAttente
                dlg = wx.MessageDialog(self, _(u"Vous poss�dez d�j� un fichier qui porte le nom '") + nomFichier + _(u"'.\n\nVeuillez saisir un autre nom."), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.SetStatusText(_(u"Echec de la cr�ation du fichier '%s' : Le nom existe d�j�.") % nomFichier)
                return False
        
        else:
            # Version RESEAU
            dictResultats = GestionDB.TestConnexionMySQL(typeTest="fichier", nomFichier=u"%s_DATA" % nomFichier)
            
            # V�rifie la connexion au r�seau
            if dictResultats["connexion"][0] == False :
                del dlgAttente
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, _(u"La connexion au r�seau MySQL est impossible. \n\nErreur : %s") % erreur, _(u"Erreur de connexion"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            # V�rifie que le fichier n'est pas d�j� utilis�
            if dictResultats["fichier"][0] == True and modeFichier != "internet" :
                del dlgAttente
                dlg = wx.MessageDialog(self, _(u"Le fichier existe d�j�."), _(u"Erreur de cr�ation de fichier"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        ancienFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = nomFichier 
        
        # Cr�ation de la base DATA
        DB = GestionDB.DB(suffixe="DATA", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, _(u"Erreur dans la cr�ation du fichier de donn�es.\n\nErreur : %s") % erreur, _(u"Erreur de cr�ation de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(_(u"Cr�ation des tables de donn�es..."))
        DB.CreationTables(Tables.DB_DATA, fenetreParente=self)
        self.SetStatusText(_(u"Importation des donn�es par d�faut..."))
        DB.Importation_valeurs_defaut(listeTables)
        DB.Close()
        
        # Cr�ation de la base PHOTOS
        if modeFichier != "internet" :
            DB = GestionDB.DB(suffixe="PHOTOS", modeCreation=True)
            if DB.echec == 1 :
                del dlgAttente
                erreur = DB.erreur
                dlg = wx.MessageDialog(self, _(u"Erreur dans la cr�ation du fichier de photos.\n\nErreur : %s") % erreur, _(u"Erreur de cr�ation de fichier"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.userConfig["nomFichier"] = ancienFichier 
                return False
            self.SetStatusText(_(u"Cr�ation de la table de donn�es des photos..."))
            DB.CreationTables(Tables.DB_PHOTOS)
            DB.Close()
        
        # Cr�ation de la base DOCUMENTS
        if modeFichier != "internet" :
            DB = GestionDB.DB(suffixe="DOCUMENTS", modeCreation=True)
            if DB.echec == 1 :
                del dlgAttente
                erreur = DB.erreur
                dlg = wx.MessageDialog(self, _(u"Erreur dans la cr�ation du fichier de documents.\n\nErreur : %s") % erreur, _(u"Erreur de cr�ation de fichier"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.userConfig["nomFichier"] = ancienFichier 
                return False
            self.SetStatusText(_(u"Cr�ation de la table de donn�es des documents..."))
            DB.CreationTables(Tables.DB_DOCUMENTS)
            DB.Close()
        
        # Cr�ation des index
        self.SetStatusText(_(u"Cr�ation des index des tables..."))
        DB = GestionDB.DB(suffixe="DATA")
        DB.CreationTousIndex() 
        DB.Close() 
        DB = GestionDB.DB(suffixe="PHOTOS")
        DB.CreationTousIndex() 
        DB.Close() 

        # Cr�� un identifiant unique pour ce fichier
        self.SetStatusText(_(u"Cr�ation des informations sur le fichier..."))
        d = datetime.datetime.now()
        IDfichier = d.strftime("%Y%m%d%H%M%S")
        for x in range(0, 3) :
            IDfichier += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        
        # M�morisation des informations sur le fichier
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
                
        # Sauvegarde et chargement de l'identit� Administrateur
        self.SetStatusText(_(u"Cr�ation de l'identit� administrateur..."))
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
        
        # Met � jour l'affichage des panels
        self.MAJ()
        self.SetTitleFrame(nomFichier=nomFichier)
        self.ctrl_ephemeride.Initialisation()
        
        # R�cup�ration de la perspective charg�e
        if self.perspective_active != None :
            self._mgr.LoadPerspective(self.perspectives[self.perspective_active]["perspective"])
            self.ForcerAffichagePanneau("ephemeride")
        else:
            self._mgr.LoadPerspective(self.perspective_defaut)

        # Active les items de la barre de menus
        self.ActiveBarreMenus(True) 

        # Met � jour la liste des derniers fichiers de la barre des menus
        self.MAJlisteDerniersFichiers(nomFichier)
        
        # Met � jour le menu
        self.MAJmenuDerniersFichiers()
                
        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)
        
        # Bo�te de dialogue pour confirmer la cr�ation
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        
        # Fermeture de la fen�tre d'attente
        del dlgAttente
        
        # Affichage d'un confirmation de succ�s de la cr�ation
        self.SetStatusText(_(u"Le fichier '%s' a �t� cr�� avec succ�s.") % nomFichier)
        dlg = wx.MessageDialog(self, _(u"Le fichier '") + nomFichier + _(u"' a �t� cr�� avec succ�s.\n\nVous devez maintenant renseigner les informations concernant l'organisateur."), _(u"Cr�ation d'un fichier"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        # Demande de remplir les infos sur l'organisateur
        self.SetStatusText(_(u"Param�trage des informations sur l'organisateur..."))
        import DLG_Organisateur
        dlg = DLG_Organisateur.Dialog(self, empecheAnnulation=True)
        dlg.ShowModal()
        dlg.Destroy()
        
        self.SetStatusText(u"")
            

    def On_fichier_Ouvrir(self, event):
        """ Ouvrir un fichier """    
        # Bo�te de dialogue pour demander le nom du fichier � ouvrir
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
        # V�rifie qu'un fichier est charg�
        if self.userConfig["nomFichier"] == "" :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucun fichier � fermer !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # M�morise l'action dans l'historique
        UTILS_Historique.InsertActions([{"IDcategorie" : 1, "action" : _(u"Fermeture du fichier")},])
        
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

        # D�sactive la commande FERMER du menu Fichier
        menuBar = self.GetMenuBar()
        self.dictInfosMenu["fermer_fichier"]["ctrl"].Enable(False)
        self.dictInfosMenu["fichier_informations"]["ctrl"].Enable(False) 
        self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(False) 
        self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(False) 

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
            # Ferme le fichier ouvert si c'est celui-ci qui est restaur�
            nomFichier = self.userConfig["nomFichier"]
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
            if nomFichier in listeFichiersRestaures :
                dlg = wx.MessageDialog(self, _(u"Red�marrage du fichier restaur�.\n\nAfin de finaliser la restauration, le fichier de donn�es ouvert va �tre ferm� puis r�-ouvert."), _(u"Red�marrage du fichier restaur�"), wx.OK | wx.ICON_INFORMATION)
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
            dlg = wx.MessageDialog(self, _(u"Cette fonction n'est accessible que si vous utilisez un fichier r�seau !"), _(u"Acc�s non autoris�"), wx.OK | wx.ICON_ERROR)
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
        self.ctrl_remplissage.MAJ() 

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

    def On_param_modeles_contrats(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_contrats", "consulter") == False : return
        import DLG_Modeles_contrats
        dlg = DLG_Modeles_contrats.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_modeles_plannings(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_plannings", "consulter") == False : return
        import DLG_Modeles_plannings
        dlg = DLG_Modeles_plannings.Dialog(self)
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

    def On_param_exercices(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_exercices", "consulter") == False : return
        import DLG_Exercices
        dlg = DLG_Exercices.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_analytiques(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_analytiques", "consulter") == False : return
        import DLG_Analytiques
        dlg = DLG_Analytiques.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_categories_comptables(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_comptables", "consulter") == False : return
        import DLG_Categories_operations
        dlg = DLG_Categories_operations.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_comptes_comptables(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_comptes_comptables", "consulter") == False : return
        import DLG_Comptes_comptables
        dlg = DLG_Comptes_comptables.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_tiers(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_tiers", "consulter") == False : return
        import DLG_Tiers
        dlg = DLG_Tiers.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_budgets(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_budgets", "consulter") == False : return
        import DLG_Budgets
        dlg = DLG_Budgets.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_param_releves_bancaires(self, event):
        import DLG_Releves_compta
        dlg = DLG_Releves_compta.Dialog(self, titre=_(u"Gestion des relev�s bancaires"))
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
        menu_affichage = self.dictInfosMenu["menu_affichage"]["ctrl"]
        item = menu_affichage.FindItemById(ID_PREMIERE_PERSPECTIVE)
        for index in range(0, 99) :
            ID = ID_PREMIERE_PERSPECTIVE + index
            item = menu_affichage.FindItemById(ID)
            if item == None : break
            menu_affichage.Remove(ID)
            self.Disconnect(ID, -1, 10014) 
                            
        # D�coche la disposition par d�faut si n�cessaire
        if self.perspective_active == None : 
            self.dictInfosMenu["perspective_defaut"]["ctrl"].Check(True)
        else:
            self.dictInfosMenu["perspective_defaut"]["ctrl"].Check(False)
            
        # Cr�e les entr�es perspectives dans le menu :
        index = 0
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menu_affichage, ID_PREMIERE_PERSPECTIVE+index, label, _(u"Afficher la disposition '%s'") % label, wx.ITEM_CHECK)
            menu_affichage.InsertItem(index+1, item)
            if self.perspective_active == index : item.Check(True)
            index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=ID_PREMIERE_PERSPECTIVE, id2=ID_PREMIERE_PERSPECTIVE+99 )
    
    def On_affichage_perspective_defaut(self, event):
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None
        self.MAJmenuPerspectives() 
        self._mgr.Update()
        self.Refresh()

    def On_affichage_perspective_perso(self, event):
        index = event.GetId() - ID_PREMIERE_PERSPECTIVE
        self._mgr.LoadPerspective(self.perspectives[index]["perspective"])
        self.perspective_active = index
        self.ForcerAffichagePanneau("ephemeride")
        self.MAJmenuPerspectives() 
        self._mgr.Update()
        self.Refresh()

    def On_affichage_perspective_save(self, event):
        newIDperspective = len(self.perspectives)
        dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir un intitul� pour cette disposition :"), "Sauvegarde d'une disposition")
        dlg.SetValue(_(u"Disposition %d") % (newIDperspective + 1))
        reponse = dlg.ShowModal()
        if reponse != wx.ID_OK:
            dlg.Destroy() 
            return
        label = dlg.GetValue()
        dlg.Destroy() 
        
        # V�rifie que ce nom n'est pas d�j� attribu�
        for dictPerspective in self.perspectives:
            if label == dictPerspective["label"] :
                dlg = wx.MessageDialog(self, _(u"Ce nom est d�j� attribu� � une autre disposition !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
        dlg = wx.MultiChoiceDialog( self, _(u"Cochez les dispositions que vous souhaitez supprimer :"), _(u"Supprimer des dispositions"), listeLabels)
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
    
    def On_affichage_barres_outils(self, event):
        # R�cup�re la liste des codes des barres actuelles
        texteBarres = self.userConfig["barres_outils_perso"]
        if len(texteBarres) > 0 :
            listeTextesBarresActuelles = texteBarres.split("@@@@")
        else :
            listeTextesBarresActuelles = []
        listeCodesBarresActuelles = []
        for texteBarre in listeTextesBarresActuelles :
            code, label, observations, style, contenu = texteBarre.split("###")
            listeCodesBarresActuelles.append(code)
            
        # Charge la DLG de gestion des barres d'outils
        import DLG_Barres_outils
        texte = self.userConfig["barres_outils_perso"]
        dlg = DLG_Barres_outils.Dialog(self, texte=texte)
        dlg.ShowModal() 
        texteBarres = dlg.GetTexte()
        listeBarresAffichees = dlg.GetListeAffichees()
        dlg.Destroy()
        self.userConfig["barres_outils_perso"] = texteBarres
        
        # Met � jour chaque barre d'outils
        if len(texteBarres) > 0 :
            listeTextesBarres = texteBarres.split("@@@@")
        else :
            listeTextesBarres = []
        
        listeCodesBarresNouvelles = []
        for texte in listeTextesBarres :
            code, label, observations, style, contenu = texte.split("###")
            listeCodesBarresNouvelles.append(code)
            panneau = self._mgr.GetPane(code)
            
            if panneau.IsOk() :
                # Si la barre existe d�j� 
                tb = self.dictBarresOutils[code]["ctrl"]
                
                # Modification de la barre
                if self.dictBarresOutils[code]["texte"] != texte :
                    self.CreerBarreOutils(texte, ctrl=tb)
                    panneau.BestSize(tb.DoGetBestSize())
                    self.dictBarresOutils[code]["texte"] = texte
                    
                # Affichage ou masquage
                if code in listeBarresAffichees :
                    panneau.Show()
                else :
                    panneau.Hide() 
                self._mgr.Update()
            else :
                # Si la barre n'existe pas 
                self.CreerBarreOutils(texte)
        
        # Suppression des barres supprim�es
        for code in listeCodesBarresActuelles :
            if code not in listeCodesBarresNouvelles :
                tb = self.dictBarresOutils[code]["ctrl"]
                panneau = self._mgr.GetPane(code)
                self._mgr.ClosePane(panneau)
                self._mgr.Update()
        
##        print "------- Liste des panneaux existants : -------"
##        for panneau in self._mgr.GetAllPanes() :
##            print panneau.name
        
        
    def On_affichage_actualiser(self, event):
        self.MAJ() 

    def On_outils_stats(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_stats", "consulter") == False : return
        import DLG_Stats
        dlg = DLG_Stats.Dialog(self)
        if dlg.ModificationParametres(premiere=True) == True :
            dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_nomadhys_synchro(self, event):
        import DLG_Synchronisation
        dlg = DLG_Synchronisation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        if hasattr(self, "ctrl_serveur_nomade") :
            self.ctrl_serveur_nomade.MAJ()

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
        dlg = wx.MessageDialog(self, _(u"Cette fonction n'est plus accessible pour le moment car Noethys utilisait une API M�t�o que Google vient de supprimer d�finitivement. Je dois donc prendre le temps de trouver une API �quivalente.\n\nMerci de votre compr�hension.\n\nIvan"), _(u"Fonction indisponible"), wx.OK | wx.ICON_EXCLAMATION)
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
        """ Connexions r�seau """
        if "[RESEAU]" not in self.userConfig["nomFichier"] :
            dlg = wx.MessageDialog(self, _(u"Cette fonction n'est accessible que si vous utilisez un fichier r�seau !"), _(u"Acc�s non autoris�"), wx.OK | wx.ICON_ERROR)
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
        """ Purger les archives de badgeage import�s """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import DLG_Badgeage_importation
        DLG_Badgeage_importation.Purger() 

    def On_outils_purger_rep_updates(self, event):
        """ Purger le r�pertoire Updates """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment purger le r�pertoire Updates ?"), _(u"Purger"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            FonctionsPerso.VideRepertoireUpdates(forcer=True) 
        dlg.Destroy()

    def On_outils_extensions(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Extensions
        UTILS_Extensions.Extensions()

    def On_outils_procedures(self, event):
        """ Commande sp�ciale """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        import UTILS_Procedures
        dlg = wx.TextEntryDialog(self, _(u"Entrez le code de proc�dure qui vous �t� communiqu� :"), _(u"Proc�dure"), "")
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
        """ R�initialisation du fichier de configuration """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_utilitaires", "consulter") == False : return
        message = _(u"Pour r�initialiser votre fichier configuration, vous devez quitter Noethys et le relancer en conservant la touche ALT gauche de votre clavier enfonc�e.\n\nCette fonctionnalit� est sans danger : Seront par exemple r�initialis�s la liste des derniers fichiers ouverts, les p�riodes de r�f�rences, les affichages personnalis�s, etc...")
        dlg = wx.MessageDialog(self, message, _(u"R�initialisation"), wx.OK | wx.ICON_INFORMATION)
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

    def On_outils_traductions(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_traductions", "consulter") == False : return
        import DLG_Traductions
        dlg = DLG_Traductions.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ChargeTraduction() 

    def On_outils_updater(self, event):
        """Mises � jour internet """
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
        # V�rification de la ventilation
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_ventilation", "consulter") == False : return
        if self.VerificationVentilation() == False : return
        import DLG_Synthese_ventilation
        dlg = DLG_Synthese_ventilation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_reglements_synthese_modes(self, event):
        # V�rification de la ventilation
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
        # V�rification de la ventilation
        import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification()
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, _(u"Un ou plusieurs r�glements peuvent �tre ventil�s.\n\nSouhaitez-vous le faire maintenant (conseill�) ?"), _(u"Ventilation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
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
        if self.VerificationVentilation() == False : return
        import DLG_Liste_deductions
        dlg = DLG_Liste_deductions.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_facturation_saisir_deductions(self, event):
        if self.VerificationVentilation() == False : return
        import DLG_Saisie_lot_deductions
        dlg = DLG_Saisie_lot_deductions.Dialog(self)
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

    def On_individus_saisir_lot_inscriptions(self, event):
        import DLG_Saisie_lot_inscriptions
        dlg = DLG_Saisie_lot_inscriptions.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_individus_contrats(self, event):
        import DLG_Liste_contrats
        dlg = DLG_Liste_contrats.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_remplissage.MAJ()

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

    def On_Comptabilite_comptes(self, event):
        import DLG_Liste_comptes
        dlg = DLG_Liste_comptes.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_operations_tresorerie(self, event):
        import DLG_Liste_operations_tresorerie
        dlg = DLG_Liste_operations_tresorerie.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_operations_budgetaires(self, event):
        import DLG_Liste_operations_budgetaires
        dlg = DLG_Liste_operations_budgetaires.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_virements(self, event):
        import DLG_Liste_virements
        dlg = DLG_Liste_virements.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_rapprochement(self, event):
        import DLG_Releves_compta
        dlg = DLG_Releves_compta.Dialog(self, titre=_(u"Rapprochement bancaire"))
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_tresorerie(self, event):
        import DLG_Tresorerie
        dlg = DLG_Tresorerie.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_budgets(self, event):
        import DLG_Suivi_budget
        dlg = DLG_Suivi_budget.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_Comptabilite_graphiques(self, event):
        import DLG_Compta_graphiques
        dlg = DLG_Compta_graphiques.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_aide_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide(None)

    def On_aide_guide_demarrage(self, event):
        """ Acc�der � la page de t�l�chargement du guide de d�marrage rapide """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_content&view=article&id=118&Itemid=45")

    def On_aide_forum(self, event):
        """ Acc�der au forum d'entraide """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_kunena&Itemid=7")

    def On_aide_videos(self, event):
        """ Acc�der au tutoriels vid�os """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_content&view=article&id=27&Itemid=16")

    def On_aide_telechargements(self, event):
        """ Acc�der � la plate-forme de t�l�chargements communautaire """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_phocadownload&view=section&id=2&Itemid=21")

    def On_aide_auteur(self, event):
        """ Envoyer un email � l'auteur """
        FonctionsPerso.LanceFichierExterne("http://www.noethys.com/index.php?option=com_contact&view=contact&id=1&Itemid=13")
        
    def On_propos_versions(self, event):
        """ A propos : Notes de versions """
        import  wx.lib.dialogs
        txtLicence = open("Versions.txt", "r")
        msg = txtLicence.read()
        txtLicence.close()
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg.decode("iso-8859-15"), _(u"Notes de versions"), size=(500, 500))
        dlg.ShowModal()
        
    def On_propos_licence(self, event):
        """ A propos : Licence """
        import  wx.lib.dialogs
        txtLicence = open("Licence.txt", "r")
        msg = txtLicence.read()
        txtLicence.close()
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg.decode("iso-8859-15"), _(u"A propos"), size=(500, 500))
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
    
    def PurgeListeDerniersFichiers(self, nbre=1):
        listeFichiers = UTILS_Config.GetParametre("derniersFichiers", [])
        UTILS_Config.SetParametre("derniersFichiers", listeFichiers[:nbre])
        self.MAJmenuDerniersFichiers() 
        
    def MAJlisteDerniersFichiers(self, nomFichier=None) :
        """ MAJ la liste des derniers fichiers ouverts dans le config et la barre des menus """
        
        # MAJ de la liste des derniers fichiers ouverts :
        listeFichiers = UTILS_Config.GetParametre("derniersFichiers", defaut=[])
        nbreFichiersMax = UTILS_Config.GetParametre("nbre_derniers_fichiers", defaut=10)
        
        # Si le nom est d�j� dans la liste, on le supprime :
        if nomFichier in listeFichiers : listeFichiers.remove(nomFichier)
           
        # On ajoute le nom du fichier en premier dans la liste :
        if nomFichier != None :
            listeFichiers.insert(0, nomFichier)
        listeFichiers = listeFichiers[:nbreFichiersMax]
        
        # On enregistre dans le Config :
        UTILS_Config.SetParametre("derniersFichiers", listeFichiers)

    def MAJmenuDerniersFichiers(self):
        """ Met � jour la liste des derniers fichiers dans le menu """
        # Suppression de la liste existante
        menuFichier = self.dictInfosMenu["menu_fichier"]["ctrl"]
        for index in range(ID_DERNIER_FICHIER, ID_DERNIER_FICHIER+10) :
            item = self.menu.FindItemById(index)
            if item == None : 
                break
            else:
                menuFichier.RemoveItem(self.menu.FindItemById(index)) 
                self.Disconnect(index, -1, 10014) # Annule le Bind

        # R�-int�gration des derniers fichiers ouverts :
        listeDerniersFichiers = self.userConfig["derniersFichiers"]
        if len(listeDerniersFichiers) > 0 : 
            index = 0
            for nomFichier in listeDerniersFichiers :
                # Version Reseau
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menuFichier, ID_DERNIER_FICHIER + index, u"%d. %s" % (index+1, nomFichier), _(u"Ouvrir le fichier : '%s'") % nomFichier)
                menuFichier.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.On_fichier_DerniersFichiers, id=ID_DERNIER_FICHIER, id2=ID_DERNIER_FICHIER + index)


    def OuvrirDernierFichier(self):
        # Chargement du dernier fichier charg� si assistant non affich�
        resultat = False
        if self.nomDernierFichier != "" :
            resultat = self.OuvrirFichier(self.nomDernierFichier)
        return resultat
                    
    def OuvrirFichier(self, nomFichier):
        """ Suite de la commande menu Ouvrir """
        self.SetStatusText(_(u"Ouverture d'un fichier en cours..."))
                        
        # V�rifie que le fichier n'est pas d�j� ouvert
        if self.userConfig["nomFichier"] == nomFichier :
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            dlg = wx.MessageDialog(self, _(u"Le fichier '") + nomFichier + _(u"' est d�j� ouvert !"), _(u"Ouverture de fichier"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetStatusText(_(u"Le fichier '%s' est d�j� ouvert.") % nomFichier)
            return False

        # Teste l'existence du fichier :
        if self.TesterUnFichier(nomFichier) == False :
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(_(u"Impossible d'ouvrir le fichier '%s'.") % nomFichier)
            return False
        
        # V�rification du mot de passe
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
        
        # V�rifie si la version du fichier est � jour
        if nomFichier != "" :
            if self.ValidationVersionFichier(nomFichier) == False :
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                self.SetStatusText(_(u"Echec de l'ouverture du fichier '%s'.") % nomFichier)
                self.userConfig["nomFichier"] = ancienFichier
                return False

        # Remplissage de la table DIVERS pour la date de derni�re ouverture
##        if nomFichier != "" :
##            date_jour =  str(datetime.date.today())  
##            listeDonnees = [("date_derniere_ouverture",  date_jour),]
##            db = GestionDB.DB()
##            db.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
##            db.close()

        # V�rifie que le r�pertoire de destination de sauvegarde auto existe vraiment
##        if nomFichier != "" :
##            self.VerifDestinationSaveAuto()
        
        # Met � jour l'affichage 
        self.MAJ()
        self.SetTitleFrame(nomFichier=nomFichier)
        self.ctrl_ephemeride.Initialisation()
        
        # R�cup�ration de la perspective charg�e
        if self.perspective_active != None :
            self._mgr.LoadPerspective(self.perspectives[self.perspective_active]["perspective"])
            self.ForcerAffichagePanneau("ephemeride")
        else:
            self._mgr.LoadPerspective(self.perspective_defaut)

        # Met � jour la liste des derniers fichiers ouverts dans le CONFIG de la page
        self.MAJlisteDerniersFichiers(nomFichier) 

        # Active la commande Fermer du menu Fichier
        menuBar = self.GetMenuBar()
        self.dictInfosMenu["fermer_fichier"]["ctrl"].Enable(True)
        self.dictInfosMenu["fichier_informations"]["ctrl"].Enable(True)
        if "[RESEAU]" in nomFichier :
            self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(False) 
            self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(True) 
        else:
            self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(True) 
            self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(False) 
        
        # Met � jour le menu
        self.MAJmenuDerniersFichiers()
        
        # D�sactive le menu Conversion R�seau s'il s'agit d�j� d'un fichier r�seau
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
        
        # Confirmation de succ�s
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        self.SetStatusText(_(u"Le fichier '%s' a �t� ouvert avec succ�s.") % nomFichier)  
        
        # M�morise dans l'historique l'ouverture du fichier
        UTILS_Historique.InsertActions([{"IDcategorie":1, "action":_(u"Ouverture du fichier %s") % nomFichier},])
        
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
                dlg = wx.MessageDialog(self, _(u"Il est impossible de se connecter au serveur MySQL.\n\nErreur : %s") % erreur, "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if dictResultats["fichier"][0] == False :
                # Ouverture impossible du fichier MySQL demand�
                erreur = dictResultats["fichier"][1]
                dlg = wx.MessageDialog(self, _(u"La connexion avec le serveur MySQL fonctionne mais il est impossible d'ouvrir le fichier MySQL demand�.\n\nErreur : %s") % erreur, "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
        else:
            # Test de validit� du fichier SQLITE :
            fichier = "Data/" + nomFichier + "_DATA.dat"
            test = os.path.isfile(fichier) 
            if test == False :
                dlg = wx.MessageDialog(self, _(u"Il est impossible d'ouvrir le fichier demand� !"), "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else:
                return True
        

    def ConvertVersionTuple(self, texteVersion=""):
        """ Convertit un num�ro de version texte en tuple """
        tupleTemp = []
        for num in texteVersion.split(".") :
            tupleTemp.append(int(num))
        return tuple(tupleTemp)

    def ValidationVersionFichier(self, nomFichier):
        """ V�rifie que la version du fichier est � jour avec le logiciel """
        # R�cup�re les num�ros de version
        versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
        versionFichier = self.ConvertVersionTuple(UTILS_Parametres.Parametres(mode="get", categorie="fichier", nom="version", valeur=VERSION_APPLICATION, nomFichier=nomFichier))
        
        # Compare les deux versions
        if versionFichier < versionLogiciel :
            # Fait la conversion � la nouvelle version
            info = "Lancement de la conversion %s -> %s..." %(".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print info
            
            # Affiche d'une fen�tre d'attente
            try :
                message = _(u"Mise � jour de la base de donn�es en cours... Veuillez patienter...")
                dlgAttente = PBI.PyBusyInfo(message, parent=None, title=_(u"Mise � jour"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
                wx.Yield() 
                
                DB = GestionDB.DB(nomFichier = nomFichier)        
                resultat = DB.ConversionDB(versionFichier)
                DB.Close()
                
                # Fermeture de la fen�tre d'attente
                del dlgAttente

            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(self, _(u"D�sol�, le probl�me suivant a �t� rencontr� dans la mise � jour de la base de donn�es : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

            if resultat != True :
                print resultat
                dlg = wx.MessageDialog(self, _(u"Le logiciel n'arrive pas � convertir le fichier '") + nomFichier + u":\n\nErreur : " + resultat + _(u"\n\nVeuillez contacter le d�veloppeur du logiciel..."), _(u"Erreur de conversion de fichier"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            # M�morisation de la nouvelle version du fichier
            UTILS_Parametres.Parametres(mode="set", categorie="fichier", nom="version", valeur=".".join([str(x) for x in versionLogiciel]), nomFichier=nomFichier)
            info = "Conversion %s -> %s reussie." %(".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print info

            # Messages exceptionnels suite � la mise � jour
            if versionFichier < (1, 1, 0, 3) :
                dlg = wx.MessageDialog(self, _(u"Mise � jour majeure 1.1.0.x.\n\nEn raison des modifications cons�quentes apport�es � cette nouvelle version de Noethys, il est conseill� d'effectuer d�s � pr�sent une sauvegarde de votre fichier de donn�es (Menu Fichier > Cr�er une sauvegarde)."), _(u"Avertissement"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                
            if versionFichier < (1, 1, 1, 3) :
                dlg = wx.MessageDialog(self, _(u"Note de mise � jour \n\nMise � jour des droits utilisateurs : \n\nNoethys propose d�sormais une nouvelle gestion avanc�e des droits utilisateurs. Dans le cadre de cette mise � jour, tous les profils utilisateurs ont �t� r�initialis�s sur 'Administrateur'. Vous pouvez les r�gler de nouveau dans Menu Param�trage > Utilisateurs."), _(u"Information importante"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                
                dlg = wx.MessageDialog(self, _(u"Note de mise � jour \n\nAm�lioration de la gestion des mandats SEPA : \n\nSi vous utilisez le pr�l�vement automatique et que vous avez d�j� saisi les mandats dans Noethys, veuillez lancer le convertisseur de RIB Nationaux en mandats SEPA du menu Outils > Utilitaires admin."), _(u"Information importante"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            
            if versionFichier < (1, 1, 3, 0) :
                texte = u"""
                <CENTER>
                <BR>
                <FONT SIZE=3>
                <B>Astuce</B><BR><BR>
                Personnalisez l'interface de la page d'accueil en fonction de vos besoins !
                <BR><BR>
                <IMG SRC="Images/Special/Astuce_barres_outils.png">
                <BR><BR>
                D�placer ou cachez les cadres et cr�ez de nouvelles barres d'outils personnalis�es pour acc�der plus rapidement � vos fonctions pr�f�r�es.
                <BR><BR>
                (Voir menu Affichage)
                </FONT>
                </CENTER>
                """
                dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"))
                dlg.ShowModal()
                dlg.Destroy()
            
            
            
            
            
            
            
            
            
            
                
                

        return True
    
    def ActiveBarreMenus(self, etat=True):
        """ Active ou non des menus de la barre """
        for numMenu in range(1, 9):
            self.menu.EnableTop(numMenu, etat)
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
        """ R�cup�re la liste des utilisateurs dans la base """
        return UTILS_Utilisateurs.GetListeUtilisateurs(nomFichier) 
    
    def RechargeUtilisateur(self):
        """ A utiliser apr�s un changement des droits par exemple """
        IDutilisateur = self.dictUtilisateur["IDutilisateur"]
        for dictTemp in self.listeUtilisateurs :
            if IDutilisateur == dictTemp["IDutilisateur"] :
                self.dictUtilisateur = dictTemp        
        self.ChargeUtilisateur(self.dictUtilisateur, afficheToaster=False)

    def ChargeUtilisateur(self, dictUtilisateur=None, IDutilisateur=None, afficheToaster=True):
        """Charge un utilisateur � partir de son dictUtilisateur OU de son IDutilisateur """
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
        tb = self.dictBarresOutils["barre_utilisateur"]["ctrl"]
        tb.SetToolBitmap(ID_TB_UTILISATEUR, wx.Bitmap("Images/Avatars/16x16/%s.png" % nomImage, wx.BITMAP_TYPE_PNG))
        tb.SetToolLabel(ID_TB_UTILISATEUR, u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"]))
        tb.Refresh() 
        # Affiche le Toaster
        if afficheToaster == True and PASS == None :
            CTRL_Toaster.ToasterUtilisateur(self, prenom=dictUtilisateur["prenom"], nomImage=nomImage) 
    
    def AfficheMessagesOuverture(self):
        """ Affiche les messages � l'ouverture du fichier """
        listeMessages = self.ctrl_messages.GetMessages()
        for track in listeMessages :
            if track.rappel == 1 :
                texteToaster = track.texte
                if track.priorite == "HAUTE" : 
                    couleurFond="#FFA5A5"
                else:
                    couleurFond="#FDF095"
                self.AfficheToaster(titre=_(u"Message"), texte=texteToaster, couleurFond=couleurFond) 

    def AfficheToaster(self, titre=u"", texte=u"", taille=(200, 100), couleurFond="#F0FBED"):
        """ Affiche une bo�te de dialogue temporaire """
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
        """ Recherche une mise � jour sur internet """
        # R�cup�re la version de l'application
        versionApplication = VERSION_APPLICATION
        # R�cup�re la version de la MAJ sur internet
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
        # Compare les deux versions et renvois le r�sultat
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
        """ Cr�ation une annonce au premier d�marrage du logiciel """
        nomFichier = sys.executable
        if nomFichier.endswith("python.exe") == False :
            versionAnnonce = self.GetVersionAnnonce()
            versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
            if versionAnnonce < versionLogiciel :
                import DLG_Message_accueil
                dlg = DLG_Message_accueil.Dialog(self)
                dlg.ShowModal()
                dlg.Destroy()
                # M�morise le num�ro de version actuel
                self.userConfig["annonce"] = versionLogiciel
                return True
        return False
    
    def EstFichierExemple(self):
        """ V�rifie si c'est un fichier EXEMPLE qui est ouvert actuellement """
        if self.userConfig["nomFichier"] != None :
            if "EXEMPLE_" in self.userConfig["nomFichier"] :
                return True
        return False

    def ProposeMAJ(self):
        """ Propose la MAJ imm�diate """
        if self.MAJexiste == True :
            if self.versionMAJ != None :
                message = _(u"La version %s de Noethys est disponible.\n\nSouhaitez-vous t�l�charger cette mise � jour maintenant ?") % self.versionMAJ
            else :
                message = _(u"Une nouvelle version de Noethys est disponible.\n\nSouhaitez-vous t�l�charger cette mise � jour maintenant ?")
            dlg = wx.MessageDialog(self, message, _(u"Mise � jour disponible"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                self.On_outils_updater(None)
                return True
        return False
    
    def AnnonceTemoignages(self):
        # Se d�clenche uniquement dans 40% des cas
        if random.randrange(1, 100) > 40 :
            return False
        
        # V�rifie si case Ne plus Afficher coch�e ou non
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="temoignages", valeur=False) == True :
            return False

        texte = u"""
<CENTER><IMG SRC="Images/32x32/Information.png">
<BR><BR>
<FONT SIZE=2>
<B>Appel � t�moignages</B>
<BR><BR>
Vous utilisez et appr�ciez Noethys ? 
<BR><BR>
Participez � sa promotion en postant un t�moignage sur le site internet de Noethys. L'occasion de d�crire votre utilisation du logiciel et de donner ainsi envie aux lecteurs int�ress�s de s'y essayer.
<BR><BR>
Merci pour votre participation !
<BR><BR>
<A HREF="http://www.noethys.com/index.php/presentation/2013-09-08-15-48-17/temoignages">Cliquez ici pour acc�der aux t�moignages</A>
</FONT>
</CENTER>
"""
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), nePlusAfficher=True)
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="temoignages", valeur=nePlusAfficher)
        return True


    def AnnonceFinancement(self):
        # V�rifie si identifiant saisi et valide
        identifiant = UTILS_Config.GetParametre("enregistrement_identifiant", defaut=None)
        if identifiant != None :
            # V�rifie nbre jours restants
            code = UTILS_Config.GetParametre("enregistrement_code", defaut=None)
            validite = DLG_Enregistrement.GetValidite(identifiant, code)
            if validite != False :
                date_fin_validite, nbreJoursRestants = validite
                dateDernierRappel = UTILS_Config.GetParametre("enregistrement_dernier_rappel", defaut=None)
                
                if nbreJoursRestants < 0 :
                    # Licence p�rim�e
                    if dateDernierRappel != None :
                        UTILS_Config.SetParametre("enregistrement_dernier_rappel", None)
                    
                elif nbreJoursRestants <= 30 :
                    # Licence bient�t p�rim�e
                    UTILS_Config.SetParametre("enregistrement_dernier_rappel", datetime.date.today())
                    if dateDernierRappel != None :
                        nbreJoursDepuisRappel =  (dateDernierRappel - datetime.date.today()).days
                    else :
                        nbreJoursDepuisRappel = None
                    if nbreJoursDepuisRappel == None or nbreJoursDepuisRappel >= 10 :
                        import wx.lib.dialogs as dialogs
                        image = wx.Bitmap("Images/32x32/Cle.png", wx.BITMAP_TYPE_ANY)
                        message1 = _(u"Votre licence d'acc�s au manuel de r�f�rence en ligne se termine dans %d jours. \n\nSi vous le souhaitez, vous pouvez continuer � b�n�ficier de cet acc�s et prolonger votre soutien financier au projet Noethys en renouvelant votre abonnement Classic ou Premium.") % nbreJoursRestants
                        dlg = dialogs.MultiMessageDialog(self, message1, caption = _(u"Enregistrement"), msg2=None, style = wx.ICON_INFORMATION | wx.YES|wx.CANCEL|wx.CANCEL_DEFAULT, icon=image, btnLabels={wx.ID_YES : _(u"Renouveler mon abonnement"), wx.ID_CANCEL : _(u"Fermer")})
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
                
        # Pub se d�clenche uniquement dans 20% des cas
        if random.randrange(1, 100) <= 20 :
            import UTILS_Financement
            dlg = UTILS_Financement.DLG_Financement(self)
            dlg.ShowModal() 
            dlg.Destroy()
            return True
        else :
            return False

    def AutodetectionAnomalies(self):
        """ Auto-d�tection d'anomalies """
        # Se d�clenche uniquement dans 15% des cas
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
        # Adaptation pour r�trocompatibilit� wx2.8
        if wx.VERSION < (2, 9, 0, 0) :
            wx.InitAllImageHandlers() 
        
        heure_debut = time.time()
        
        # V�rifie l'existence des r�pertoires
        for rep in ("Aide", "Temp", "Updates", "Sync", "Lang") :
            if os.path.isdir(rep) == False :
                os.makedirs(rep)
                print "Creation du repertoire : ", rep
        
        # R�initialisation du fichier des parametres en conservant la touche ALT
        if wx.GetKeyState(307) == True :
            dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment r�initialiser Noethys ?"), _(u"R�initialisation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES :
                os.remove("Data/Config.dat")
            dlg.Destroy()
        
        # Suppression du fichier temporaire s'il existe pour �viter bugs
        if os.path.isfile("Data/__db.Config.dat") :
            os.remove("Data/__db.Config.dat")
        
        # AdvancedSplashScreen
        if PASS == None :
            bmp = wx.Bitmap("Images/Special/Logo_splash.png", wx.BITMAP_TYPE_PNG)
            frame = AS.AdvancedSplash(None, bitmap=bmp, timeout=500, agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_SCREEN)
            anneeActuelle = str(datetime.date.today().year)
            frame.SetText(u"Copyright � 2010-%s Ivan LUCAS" % anneeActuelle[2:])
            frame.SetTextFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
            frame.SetTextPosition((340, 175))
            frame.SetTextColour(wx.Colour(110, 147, 58))
            frame.Refresh()
            frame.Update()
            wx.Yield()

        # Cr�ation de la frame principale
        frame = MainFrame(None)
        self.SetTopWindow(frame)
        frame.Initialisation()
        frame.Show()   

        # Affiche une annonce si c'est un premier d�marrage ou apr�s une mise � jour
        etat_annonce = frame.Annonce()
                
        # Charge le fichier Exemple si l'utilisateur le souhaite
        etat_exemple = frame.ChargeFichierExemple() 
        
        # Charge le dernier fichier
        fichierOuvert = frame.OuvrirDernierFichier()

        # Propose mise � jour imm�diate
        etat_maj = frame.ProposeMAJ()
        
        # Apr�s ouverture d'un fichier :
        if fichierOuvert == True and frame.EstFichierExemple() == False and etat_maj == False :
            
            # T�moignages
            temoignages = frame.AnnonceTemoignages()
            
            # Financement
            if temoignages == False : 
                financement = frame.AnnonceFinancement()
            
                # D�tection d'anomalies
                if financement == False :
                    frame.AutodetectionAnomalies() 
        
        # D�marrage du serveur
        if hasattr(frame, "ctrl_serveur_nomade") :
            frame.ctrl_serveur_nomade.StartServeur()
        
##        print time.time() - heure_debut
        return True




if __name__ == "__main__":
    
    # Crash report
    UTILS_Rapport_bugs.Activer_rapport_erreurs(version=VERSION_APPLICATION)
    
    # Log
    fichierLog = "journal.log"
    
    # Supprime le journal.log si sup�rieur � 10 Mo
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
    
