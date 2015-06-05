#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import os
import datetime
import time
import random
import GestionDB
import wx.lib.agw.pybusyinfo as PBI
import traceback

import DATA_Civilites
import CTRL_Badgeage_objets as OBJETS
import CTRL_Badgeage_controles as CONTROLES
import DLG_Badgeage_dlg as DIALOGUES
import DLG_Badgeage_grille
import UTILS_Titulaires
import UTILS_Filtres_questionnaires
import UTILS_Vocal
import UTILS_Ticket

from DATA_Tables import DB_DATA as DICT_TABLES

DICT_CIVILITES = DATA_Civilites.GetDictCivilites()


LISTE_STYLES = [
    {"code" : "crystal", "label" : _(u"Crystal")},
    ]
    
LISTE_THEMES = [
    {"code" : "defaut", "label" : _(u"Défaut"), "image" : "Theme_defaut.png", "dlg" : {"couleurClaire" : wx.Colour(206, 196, 190), "couleurFoncee" : wx.Colour(169, 156, 146)}, },
    {"code" : "newyork", "label" : _(u"New-York"), "image" : "Theme_newyork.jpg", "dlg" : {"couleurClaire" : wx.Colour(186, 186, 186), "couleurFoncee" : wx.Colour(60, 60, 60)}, },
    {"code" : "ocean", "label" : _(u"Océan"), "image" : "Theme_ocean.jpg", "dlg" : {"couleurClaire" : wx.Colour(229, 195, 149), "couleurFoncee" : wx.Colour(2, 134, 183)}, },
    {"code" : "bleu", "label" : _(u"Bleu métal"), "image" : "Theme_bleu.jpg", "dlg" : {"couleurClaire" : wx.Colour(164, 182, 193), "couleurFoncee" : wx.Colour(63, 79, 94)}, },
    {"code" : "vert", "label" : _(u"Vert pomme"), "image" : "Theme_vert.jpg", "dlg" : {"couleurClaire" : wx.Colour(212, 238, 115), "couleurFoncee" : wx.Colour(71, 85, 24)}, },
    {"code" : "sommets", "label" : _(u"Sommets enneigés"), "image" : "Theme_sommets.jpg", "dlg" : {"couleurClaire" : wx.Colour(186, 186, 186), "couleurFoncee" : wx.Colour(60, 60, 60)}, },
    {"code" : "hiver", "label" : _(u"Ciel d'hiver "), "image" : "Theme_hiver.jpg", "dlg" : {"couleurClaire" : wx.Colour(111, 151, 255), "couleurFoncee" : wx.Colour(36, 67, 148)}, },
    {"code" : "noel", "label" : _(u"Noël "), "image" : "Theme_noel.jpg", "dlg" : {"couleurClaire" : wx.Colour(255, 98, 89), "couleurFoncee" : wx.Colour(120, 7, 15)}, },
    {"code" : "personnalise", "label" : _(u"Personnalisé"), "dlg" : {"couleurClaire" : wx.Colour(206, 196, 190), "couleurFoncee" : wx.Colour(169, 156, 146)}, },
    ]


def GetTheme(code=""):
    """ Récupère un thème d'après son code """
    for dictTemp in LISTE_THEMES :
        if dictTemp["code"] == code :
            return dictTemp
    return None

def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None or texte == "None" :
        return []
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def GetInfosActivite(IDactivite=None, date=None):
    """ Récupération des infos sur une activité """
    dictActivite = {} 
    DB = GestionDB.DB()
    
    # Recherche des infos sur l'activité
    req = """SELECT nom, abrege, date_debut, date_fin 
    FROM activites
    WHERE IDactivite=%d;""" % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    nom, abrege, date_debut, date_fin = listeDonnees[0]
    dictActivite = {"nom":nom, "abrege":abrege, "date_debut":date_debut, "date_fin":date_fin}
    
    # Recherche des unités de l'activités
    req = """SELECT IDunite, ordre, nom, abrege, type, heure_debut, heure_debut_fixe, heure_fin, heure_fin_fixe
    FROM unites
    WHERE IDactivite=%d;""" % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictUnites = {}
    for IDunite, ordre, nom, abrege, type, heure_debut, heure_debut_fixe, heure_fin, heure_fin_fixe in listeDonnees :
        dictUnites[IDunite] = {"ordre":ordre, "nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, 
                                        "heure_debut_fixe":heure_debut_fixe, "heure_fin":heure_fin_fixe}

    # Recherche des groupes de l'activités
    req = """SELECT IDgroupe, nom, abrege, ordre
    FROM groupes
    WHERE IDactivite=%d;""" % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictGroupes = {}
    for IDgroupe, nom, abrege, ordre in listeDonnees :
        dictGroupes[IDgroupe] = {"ordre":ordre, "nom":nom, "abrege":abrege}

    # Recherche des ouvertures des unités
    req = """SELECT IDouverture, IDunite, IDgroupe
    FROM ouvertures 
    WHERE IDactivite=%d AND date='%s'; """ % (IDactivite, str(date))
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeOuvertures = []
    for IDouverture, IDunite, IDgroupe in listeDonnees :
        listeOuvertures.append((IDunite, IDgroupe))
    DB.Close()
    
    return dictActivite, dictUnites, listeOuvertures, dictGroupes


class InfosIndividus():
    def __init__(self, ):
        self.dictIndividus = self.Importation() 
        self.dictCodesbarres = self.GetCodebarres()
        
    def RechercheIndividu(self, IDindividu=None):
        """ Recherche un individu d'après son IDindividu """
        if self.dictIndividus.has_key(IDindividu) == False :
            return None
        # Renvoie les informations
        return self.dictIndividus[IDindividu]

    def Importation(self):
        """ Importation de tous les individus de la base de données """
        DB = GestionDB.DB()
        req = """SELECT IDindividu, IDcivilite, nom, prenom FROM individus;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictTemp = {}
        for IDindividu, IDcivilite, nom, prenom in listeDonnees :
            genre = DICT_CIVILITES[IDcivilite]["sexe"]
            dictTemp[IDindividu] = {"nom":nom, "prenom":prenom, "genre":genre}
        return dictTemp
    
    def IdentificationCodebarre(self, cb=""):
        # Recherche le code-barres dans les questionnaires
        if self.dictCodesbarres["questionnaire"].has_key(cb) :
            return self.dictCodesbarres["questionnaire"][cb]
        # Recherche un code-barres dans le dict Standard
        if len(cb) > 7 : cb = cb[:7]
        if self.dictCodesbarres["standard"].has_key(cb) :
            return self.dictCodesbarres["standard"][cb]
        # Si aucun résultat
        return None

    def GetCodebarres(self):
        """ Récupère les codes-barres des individus """
        dictCodesbarres = {"standard" : {}, "questionnaire" : {} }
        
        # Récupère les codes-barres des questionnaires
        DB = GestionDB.DB()
        req = """SELECT questionnaire_reponses.IDquestion, IDindividu, reponse, controle
        FROM questionnaire_reponses
        LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_reponses.IDquestion
        WHERE controle IN ('codebarres', 'rfid') AND IDindividu IS NOT NULL
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDquestion, IDindividu, reponse, controle in listeDonnees :
            dictCodesbarres["questionnaire"][reponse] = IDindividu
            
        # Création des codesbarres des individus
        for IDindividu, dictTemp in self.dictIndividus.iteritems() :
            cb = "I%06d" % IDindividu
            dictCodesbarres["standard"][cb] = IDindividu
        
        return dictCodesbarres        

    def IdentificationRFID(self, rfid=""):
        # Recherche le RFID dans les questionnaires
        if self.dictCodesbarres["questionnaire"].has_key(rfid) :
            return self.dictCodesbarres["questionnaire"][rfid]
        return None

    def GetInscriptions(self, IDindividu=None):
        """ Renvoie les inscriptions aux activités de l'individu donné """
        DB = GestionDB.DB()
        req = """SELECT IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, parti
        FROM inscriptions
        WHERE IDindividu=%d AND parti=0
        ;""" % IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeInscriptions = []
        for IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, parti in listeDonnees :
            listeInscriptions.append({"IDfamille":IDfamille, "IDactivite":IDactivite, "IDgroupe":IDgroupe, "IDcategorie_tarif":IDcategorie_tarif, "parti":parti})
        return listeInscriptions
                        
    def GetNomsTitulaires(self, IDfamille=None):
        dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille=[IDfamille,])
        noms = dictTitulaires[IDfamille]["titulairesSansCivilite"]
        return noms
    


# ---------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Interface(wx.Panel):
    def __init__(self, parent, log=None, IDprocedure=None, date=None, dateauto=False, importationManuelle=False, montrerGrille=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.log = log
        self.IDprocedure = IDprocedure
        self.date = date
        self.dateauto = dateauto
        self.importationManuelle = importationManuelle
        
        # Initialisation du moteur vocal
        try :
            self.vocal = UTILS_Vocal.Vocal() 
        except Exception, err:
            self.vocal = None
            
        # Importation de la procédure
        self.dictProcedure = self.ImportationProcedure() 
        
        # Choix du système d'identification
        self.nomControleActif = self.dictProcedure["parametres"]["systeme"]
        if importationManuelle != False :
            self.nomControleActif = "importation"
        
        # Initialisation de la liste des individus
        self.infosIndividus = InfosIndividus()
        
        # Création des contrôles
        self.ctrl_grille = DLG_Badgeage_grille.CTRL(self)
        self.ctrl_grille.SetSize((800, 120))
        self.ctrl_grille.SetPosition((20, 20))
        self.ctrl_grille.Show(montrerGrille) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ICI AFFICHAGE DU CTRL_GRILLE
        self.ctrl_barre_numerique = CONTROLES.CTRL_Barre_numerique(self)
        self.ctrl_barre_numerique.Show(False)
        self.ctrl_liste_individus = CONTROLES.CTRL_Liste_individus(self) 
        self.ctrl_liste_individus.Show(False) 
        if self.nomControleActif == "liste_individus" :
            self.ctrl_liste_individus.Initialisation() 
        self.ctrl_importation = CONTROLES.CTRL_Importation(self) 
        self.ctrl_importation.Show(False) 

        # Importation image de fond
        theme = self.dictProcedure["parametres"]["theme"]
        self.bmp_fond = None
        if theme == "personnalise" :
            chemin = self.dictProcedure["parametres"]["image"]
            if os.path.isfile(chemin) == True :
                self.bmp_fond = chemin
        else :
            self.bmp_fond = "Images/Badgeage/%s" % GetTheme(theme)["image"]
        if self.bmp_fond != None :
            self.bmp_fond = wx.Bitmap(self.bmp_fond)
        else :
            self.bmp_fond = wx.Bitmap("Images/Badgeage/Theme_defaut.png")

        # Initialisation du PseudoDC
        self.pdc = wx.PseudoDC()
        self.dictObjets = {}
        self.DoDrawing(self.pdc)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        # Changement de date automatique
        if self.dateauto == True :
            self.Bind(wx.EVT_TIMER, self.OnTimer)
            self.timer = wx.Timer(self)
            self.timer.Start(600000) # = 10 minutes
        else :
            self.timer = None
            
        # Init contrôles
        self.AfficherControleActif() 
        
        # Importation manuelle de badgeages
        if importationManuelle != False :
            self.ImportationBadgeage()

            
    def OnTimer(self, event):
        """ Changement de date automatique """
        if self.date != datetime.date.today() :
            self.date = datetime.date.today()
            self.log.AjouterAction(action=_(u"Changement de date automatique : %s") % DateEngFr(str(self.date)))
    
    def StopTimer(self):
        if self.timer != None :
            self.timer.Stop()
        
    def GetStyle(self):
        return self.dictProcedure["parametres"]["style"]

    def GetTheme(self):
        theme = self.dictProcedure["parametres"]["theme"]
        return GetTheme(theme)

    def OnSize(self, event):
        for objet in self.listeObjets :
            objet.Centrer() 
    
    def MAJ(self):
        self.DoDrawing(self.pdc)
        self.Refresh()

    def OnMouse(self, event):
        # Actions sur souris
        x,y = event.GetX(), event.GetY()
        objets = self.pdc.FindObjects(x, y, 5)
        for id in objets :
            if self.dictObjets.has_key(id) :
                objet = self.dictObjets[id]
                if event.Moving() : objet.OnMotion()
                if event.LeftDown() : objet.OnLeftDown()
                if event.LeftUp() : objet.OnLeftUp()

        # Supprime les images de survol
        maj = False
        for id, objet in self.dictObjets.iteritems() :
            if id not in objets :
                if objet.objetImageSurvol != None : objet.EffaceSurvol()
                if objet.objetImageEnfonce != None : objet.EffaceEnfonce()
                maj = True
        if maj == True :
            self.Refresh() 

    def OnPaint(self, event):
        """ Préparation du DC """
        dc = wx.BufferedPaintDC(self)
        if wx.VERSION < (2, 9, 0, 0) :
            self.PrepareDC(dc)
        bg = wx.Brush(self.GetBackgroundColour())
        dc.SetBackground(bg)
        dc.Clear()
        
        # Redimensionne l'image à la taille de l'écran
        largeur, hauteur = self.bmp_fond.GetSize()
        tailleDC = self.GetSize()
        x, y = (tailleDC[0]-largeur)/2.0, (tailleDC[1]-hauteur)/2.0
        dc.DrawBitmap(self.bmp_fond, x, y)
        
        # Update de la zone modifiée
        rgn = self.GetUpdateRegion()
        r = rgn.GetBox()
        self.pdc.DrawToDCClipped(dc, r)

    def DoDrawing(self, dc):
        """ Creation du dessin dans le PseudoDC """
        self.dictObjets = {}
        dc.RemoveAll()
        
        # --------------- Dessin des objets de l'interface ----------------
        positionHaute = 140
        self.barreNum = OBJETS.Groupe_barre_numerique(self, position=(100, positionHaute))
        self.clavierNum = OBJETS.Groupe_clavier_numerique(self, position=(200, positionHaute+100))
        self.listeIndividus = OBJETS.Groupe_liste_individus(self, position=(500, positionHaute))
        self.importation = OBJETS.Groupe_importation(self, position=(500, positionHaute))
        
        self.listeObjets = (self.barreNum, self.clavierNum, self.listeIndividus, self.importation)
    
    def AfficherControleActif(self):
        """ Affiche le contrôle actif """
        # Cache tous les contrôles
        self.CacherControleActif() 
        # Affiche le contrôle actif
        if self.nomControleActif == "barre_numerique" :
            self.barreNum.Afficher() 
            self.ctrl_barre_numerique.SetFocus()
        if self.nomControleActif == "clavier_numerique" :
            self.barreNum.Afficher() 
            self.clavierNum.Afficher() 
            self.ctrl_barre_numerique.SetFocus()
        if self.nomControleActif == "liste_individus" :
            self.listeIndividus.Afficher() 
        if self.nomControleActif == "importation" :
            self.importation.Afficher() 
            self.ctrl_importation.SetFocus()

    def CacherControleActif(self):
        self.listeIndividus.Cacher() 
        self.barreNum.Cacher() 
        self.clavierNum.Cacher() 
        self.importation.Cacher()
    
    def ValidationIdentification(self, IDindividu=None):
        """ Vérifie qu'un IDindividu est correct """
        infos = self.infosIndividus.RechercheIndividu(IDindividu)
        if infos == None :
            return False
        else :
            return True
    
    def IdentificationCodebarre(self, cb=""):
        return self.infosIndividus.IdentificationCodebarre(cb)

    def IdentificationRFID(self, rfid=""):
        return self.infosIndividus.IdentificationRFID(rfid)

    def ImportationProcedure(self):
        """ Importation de la procédure """
        dictProcedure = {} 
        DB = GestionDB.DB()
        
        # Paramètres de la procédure
        req = """SELECT nom, style, theme, image, systeme, activites, confirmation, vocal, tutoiement
        FROM badgeage_procedures
        WHERE IDprocedure=%d;
        """ % self.IDprocedure
        DB.ExecuterReq(req)
        listeProcedures = DB.ResultatReq()
        
        if len(listeProcedures) == 0 : return {}
        nom, style, theme, image, systeme, activites, confirmation, vocal, tutoiement = listeProcedures[0]
        if activites != None :
            listeActivites = []
            for IDactivite in activites.split(";") :
                listeActivites.append(int(IDactivite))
            activites = listeActivites
        
        dictProcedure["parametres"] = {"nom":nom, "style":style, "theme":theme, "image":image, "systeme":systeme, "activites":activites, "confirmation":confirmation, "vocal":vocal, "tutoiement":tutoiement} 
        
        # Actions
        listeChamps = []
        for nom, type, info in DICT_TABLES["badgeage_actions"] :
            listeChamps.append(nom)
        req = """SELECT %s
        FROM badgeage_actions 
        WHERE IDprocedure=%d
        ORDER BY ordre
        ;""" % (", ".join(listeChamps), self.IDprocedure)
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        
        listeDonnees = []
        ordre = 1
        for ligne in listeActions :
            index = 0
            dictTemp = {}
            for valeur in ligne :
                nomChamp = listeChamps[index]
                dictTemp[nomChamp] = valeur
                index += 1
            dictTemp["ordre"] = ordre
            
            # Importation des messages
            if dictTemp["action"] == "message" :
                req = """SELECT IDmessage, message
                FROM badgeage_messages
                WHERE IDaction=%d
                ;""" % dictTemp["IDaction"]
                DB.ExecuterReq(req)
                listeTemp = DB.ResultatReq()
                listeMessages = []
                for IDmessage, message in listeTemp :
                    listeMessages.append((IDmessage, message))
                dictTemp["action_messages"] = listeMessages
            
            listeDonnees.append(dictTemp)
            ordre += 1
        
        dictProcedure["actions"] = listeDonnees
        
        DB.Close()
        return dictProcedure
        
    def Procedure(self, IDindividu=None, date=None, heure=None):
        """ Lance une procédure pour l'individu donné """
        if date == None : date = self.date
        if heure == None : heure = time.strftime('%H:%M', time.localtime())
                
        # Cache le contrôle de saisie
        self.CacherControleActif()
        
        # Recherche le nom de l'individu
        infos = self.infosIndividus.RechercheIndividu(IDindividu)
        nom = infos["nom"]
        prenom = infos["prenom"]
        nomIndividu = u"%s %s" % (nom, prenom)
        
        # Demande de confirmation de l'identité
        if self.dictProcedure["parametres"]["confirmation"] == 1 and self.importationManuelle == False :
            if self.dictProcedure["parametres"]["tutoiement"] == 1 :
                message = _(u"Confirmes-tu être %s %s ?") % (prenom, nom)
            else :
                message = _(u"Confirmez-vous être %s %s ?") % (prenom, nom)
            dlg = DIALOGUES.DLG_Question(self, message=message, icone="question")
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                self.AfficherControleActif()
                return

        # Envoi de l'info d'identification vers le log
        self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=_(u"Identification de %s (ID%d)") % (nomIndividu, IDindividu), resultat=True)
        
        # Lancement des actions
        for dictAction in self.dictProcedure["actions"] :
            # Vérifie les conditions
            if self.VerificationConditionsAction(dictAction, IDindividu, date, heure) == True :
                if dictAction["action"] == "message" : self.Procedure_message(dictAction, IDindividu, date, heure)
                if dictAction["action"] == "enregistrer" : self.Procedure_enregistrer(dictAction, IDindividu, date, heure)
                if dictAction["action"] == "reserver" : self.Procedure_reserver(dictAction, IDindividu, date, heure)
                        
        # Ré-affiche le contrôle de saisie
        self.AfficherControleActif()
    
    def VerificationConditionsAction(self, dictAction, IDindividu, date, heure):
        """ Vérification si les conditions de l'action sont bonnes """
        # Condition individu inscrit aux activités données
        if dictAction["condition_activite"] != None :
            listeActivites = ConvertStrToListe(dictAction["condition_activite"])
            valide = False
            for dictInscription in self.infosIndividus.GetInscriptions(IDindividu) :
                if dictInscription["IDactivite"] in listeActivites :
                    valide = True
            if valide == False :
                return False
        
        # Condition heure de badgeage
        if dictAction["condition_heure"] != None :
            choix, criteres = dictAction["condition_heure"].split(";")
            valide = False
            if choix == "EGAL" : 
                if str(heure) == str(criteres) : valide = True
            if choix == "DIFFERENT" : 
                if str(heure) != str(criteres) : valide = True
            if choix == "SUP" : 
                if str(heure) > str(criteres) : valide = True
            if choix == "SUPEGAL" : 
                if str(heure) >= str(criteres) : valide = True
            if choix == "INF" : 
                if str(heure) < str(criteres) : valide = True
            if choix == "INFEGAL" : 
                if str(heure) <= str(criteres) : valide = True
            if choix == "COMPRIS" : 
                if str(heure) >= str(criteres.split("-")[0]) and str(heure) <= str(criteres.split("-")[1]) : valide = True
            if valide == False :
                return False

        # Condition jours période scolaires ou vacances
        if dictAction["condition_periode"] != None :
            
            # Recherche des périodes de vacances
            DB = GestionDB.DB()
            req = """SELECT date_debut, date_fin, nom, annee
            FROM vacances 
            ORDER BY date_debut; """
            DB.ExecuterReq(req)
            listeVacances = DB.ResultatReq()
            DB.Close()
            # Vérifie si la date est en vacances ou non
            estEnVacances = False
            for valeurs in listeVacances :
                date_debut = valeurs[0]
                date_fin = valeurs[1]
                if str(date) >= date_debut and str(date) <= date_fin :
                    estEnVacances = True
            # Analyse la condition
            joursScolaires, joursVacances = dictAction["condition_periode"].split("-")
            valide = False
            if estEnVacances == False :
                if date.weekday() in ConvertStrToListe(joursScolaires) :
                    valide = True
            if estEnVacances == True :
                if date.weekday() in ConvertStrToListe(joursVacances) :
                    valide = True
            if valide == False :
                return False

        # Condition Poste réseau
        if dictAction["condition_poste"] != None :
            listePostes = dictAction["condition_poste"].split(";")
            DB = GestionDB.DB()
            nomPosteActuel = DB.GetNomPosteReseau() 
            DB.Close()
            if nomPosteActuel not in listePostes :
                return False
        
        # Condition Questionnaire
        if dictAction["condition_questionnaire"] != None :
            listeFiltres = dictAction["condition_questionnaire"].split("##")
            DB = GestionDB.DB()
            
            # Recherche des contrôles et des types
            req = """SELECT IDquestion,type, controle
            FROM questionnaire_questions
            LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie;"""
            DB.ExecuterReq(req)
            listeQuestions = DB.ResultatReq()
            dictQuestions = {}
            for IDquestion, type, controle in listeQuestions :
                dictQuestions[IDquestion] = {"type":type, "controle":controle}

            valide = True
            for filtre in listeFiltres :
                IDquestion, choix, criteres = filtre.split(";;")
                IDquestion = int(IDquestion) 
                
                # Recherche les réponses
                if dictQuestions[IDquestion]["type"] == "individu" :
                    req = """SELECT IDreponse, reponse
                    FROM questionnaire_reponses
                    WHERE IDquestion=%d AND IDindividu=%d;""" % (IDquestion, IDindividu)
                    DB.ExecuterReq(req)
                    listeReponses = DB.ResultatReq()     

##                if dictQuestions[IDquestion]["type"] == "famille" :
##                    req = """SELECT IDreponse, reponse
##                    FROM questionnaire_reponses
##                    WHERE IDquestion=%d AND IDfamille=%d;""" % (IDquestion, IDfamille)
##                    DB.ExecuterReq(req)
##                    listeReponses = DB.ResultatReq()     
                
                # Compare le filtre avec les réponses
                for IDreponse, reponse in listeReponses :
                    resultat = UTILS_Filtres_questionnaires.Filtre(controle=dictQuestions[IDquestion]["controle"], choix=choix, criteres=criteres, reponse=reponse)
                    if resultat == False :
                        valide = False

            DB.Close() 
            if valide == False :
                return False
            
        # Si toutes les conditions sont ok
        return True
        
        
    def Procedure_message(self, dictAction, IDindividu, date, heure):
        """ Procédure message """
        messageUnique = dictAction["action_message"]
        listeMessages = dictAction["action_messages"]
        icone = dictAction["action_icone"]
        duree = int(dictAction["action_duree"])
        frequence = int(dictAction["action_frequence"])
        vocal = int(dictAction["action_vocal"])
        
        # Décide si affichage en fonction de la fréquence demandée
        if 1 <= random.randrange(1, 100)  <= frequence :
            # Sélectionne le texte
            if len(listeMessages) == 0 :
                texte = messageUnique
            else :
                texte = random.choice(listeMessages)[1]
            # Remplacement des variables
            texte = self.RemplacementVariablesMessages(texte, heure, IDindividu)
            # Affiche le message
            DIALOGUES.DLG_Message(self, message=texte, icone=icone, secondes=duree)
            
        return True
    
    def RemplacementVariablesMessages(self, texte="", heure=None, IDindividu=None, date=datetime.date.today()):
        texte = texte.replace("{NOM}", self.infosIndividus.RechercheIndividu(IDindividu)["nom"])
        texte = texte.replace("{PRENOM}", self.infosIndividus.RechercheIndividu(IDindividu)["prenom"])
        texte = texte.replace("{HEURE}", heure.replace(":", "h"))
        texte = texte.replace("{DATE}", DateComplete(date))
        if self.infosIndividus.RechercheIndividu(IDindividu)["genre"] == "F" :
            feminin = u"e"
        else :
            feminin = u""
        texte = texte.replace("{FEMININ}", feminin)
        return texte
    
    def RechercheInscription(self, IDindividu, nomIndividu, IDactivite, dictActivite, nomAction=u""):
        """ Récupère IDfamille et IDgroupe """
        listeInscriptions = self.infosIndividus.GetInscriptions(IDindividu)
        listeIDfamille = []
        for dictInscription in listeInscriptions :
            if dictInscription["IDactivite"] == IDactivite :
                listeIDfamille.append((dictInscription["IDfamille"], dictInscription["IDgroupe"]))
        
        if len(listeIDfamille) == 0 :
            # Individu pas inscrit à cette activité
            self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=_(u"Individu non inscrit à l'activité"))
            if self.infosIndividus.RechercheIndividu(IDindividu)["genre"] == "F" :
                feminin = "e"
            else :
                feminin = ""
            if self.dictProcedure["parametres"]["tutoiement"] == 1 :
                message = _(u"Tu n'es pas inscrit%s à l'activité '%s' !") % (feminin, dictActivite["nom"])
            else :
                message = _(u"Vous n'êtes pas inscrit%s à l'activité '%s' !") % (feminin, dictActivite["nom"])
            DIALOGUES.DLG_Message(self, message=message, icone="erreur")
            return False, False
        
        elif len(listeIDfamille) > 1 :
            # Rattaché à plusieurs familles sur cette activité
            listeNomsTitulaires = []
            for IDfamille, IDgroupe in listeIDfamille :
                listeNomsTitulaires.append(self.infosIndividus.GetNomsTitulaires(IDfamille))
            dlg = DIALOGUES.DLG_Choix(self, message=_(u"Sur quel dossier faut-il facturer l'activité '%s' ?") % dictActivite["nom"], listeItems=listeNomsTitulaires, multiSelection=False)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                index = dlg.GetSelections()[0]
                IDfamille, IDgroupe = listeIDfamille[index]
                self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=_(u"Choix d'une famille à facturer sur l'activité '%s' : %s.") % (dictActivite["nom"], listeNomsTitulaires[index]), resultat=True)
            else :
                self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=_(u"Choix d'une famille à facturer sur l'activité '%s'.") % dictActivite["nom"], resultat=_(u"Annulation lors du choix de la famille rattachée."))
                return False, False

        else :
            # 1 seule famille rattachée sur cette activité
            IDfamille, IDgroupe = listeIDfamille[0]
        
        return IDfamille, IDgroupe

    def Procedure_enregistrer(self, dictAction, IDindividu, date, heure):
        """ Procédure enregistrer """
        IDactivite = int(dictAction["action_activite"])
        IDunite = int(dictAction["action_unite"])
        etat = dictAction["action_etat"]
        demande = int(dictAction["action_demande"])
        heure_debut = dictAction["action_heure_debut"]
        heure_fin = dictAction["action_heure_fin"]
        message = dictAction["action_message"]
        vocal = int(dictAction["action_vocal"])
        ticket = dictAction["action_ticket"]
        
        # Récupération des infos sur l'activité et sur l'individu
        dictActivite, dictUnites, listeOuvertures, dictGroupes = GetInfosActivite(IDactivite, date) 
        nomIndividu = u"%s %s" % (self.infosIndividus.RechercheIndividu(IDindividu)["nom"], self.infosIndividus.RechercheIndividu(IDindividu)["prenom"])
        nomAction = _(u"Enregistrement d'une consommation '%s'") % dictUnites[IDunite]["nom"]
        
        # Recherche si l'individu est bien inscrit à l'activité
        IDfamille, IDgroupe = self.RechercheInscription(IDindividu, nomIndividu, IDactivite, dictActivite, nomAction)
        if IDfamille == False :
            return False
        
        # Recherche si l'unité est ouverte pour ce groupe à cette date
        if (IDunite, IDgroupe) not in listeOuvertures :
            self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=_(u"Unité '%s' fermée le %s") % (dictUnites[IDunite]["nom"], DateEngFr(str(date))))
            return False
        
        # Initialisation de la grille des conso
        self.ctrl_grille.InitGrille(IDindividu=IDindividu, IDfamille=IDfamille, IDactivite=IDactivite, date=date)
        
        # Si demande début ou fin
        if demande == 1 :
            if self.dictProcedure["parametres"]["tutoiement"] == 1 :
                texte = _(u"Est-ce que tu arrives ? Ou est-ce que tu pars ?")
            else :
                texte = _(u"Est-ce que vous arrivez ? Ou est-ce que vous partez ?")
            listeChoix = [_(u"J'arrive"), _(u"Je pars")]
            dlg = DIALOGUES.DLG_Choix(self, message=texte, listeItems=listeChoix, multiSelection=False)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                selection = dlg.GetSelections()[0]
                if selection == 0 :
                    # J'arrive
                    heureDebut = heure
                    if heure_fin == "defaut" : 
                        heureFin = "defaut"
                    else :
                        heureFin = heure_fin
                else :
                    # Je pars
                    heureDebut = None
                    heureFin = heure
            else :
                return False
            
        else :
            # Calcul des heures
            if heure_debut == "defaut" : heureDebut = "defaut"
            elif heure_debut == "pointee" : heureDebut = heure
            else : heure_debut = heureDebut
            
            if heure_fin == "defaut" : heureFin = "defaut"
            elif heure_fin == "pointee" : heureFin = heure
            else : heure_fin = heureFin
        
##            case = self.ctrl_grille.GetCase(IDunite)
##            print case.heure_debut, case.heure_fin, case.etat
        
        # Saisie de la consommation
        resultat = self.ctrl_grille.SaisieConso(IDunite=IDunite, mode="reservation", etat=etat, heure_debut=heureDebut, heure_fin=heureFin)
        self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=resultat)
        
        # Impression ticket
        if ticket not in (None, "") :
            IDmodele = int(ticket)
            dictValeurs = {
                "{ID_INDIVIDU}" : str(IDindividu),
                "{NOM_INDIVIDU}" : nomIndividu,
                "{NOM_ACTIVITE}" : dictActivite["nom"],
                "{ACTION}" : nomAction,
                "{NOM_UNITE}" : dictUnites[IDunite]["nom"],
                "{DATE}" : DateEngFr(str(date)),
                "{HEURE}" : heure.replace(":", "h"),
                "{NOM_GROUPE}" : dictGroupes[IDgroupe]["nom"],
                }
            
            UTILS_Ticket.ImpressionModele(IDmodele=IDmodele, dictValeurs=dictValeurs)
                    
        if resultat == True :
            # Sauvegarde de la grille des conso
            self.ctrl_grille.Sauvegarde()
            # Affichage du message de confirmation
            if message != None :
                texte = self.RemplacementVariablesMessages(message, heure, IDindividu, date)
                DIALOGUES.DLG_Message(self, message=texte, icone="information")
            return True
        else :
            return False
    
    def RechercheProchaineOuverture(self, IDactivite=None, date=None):
        """ Recherche la prochaine date d'ouverture de l'activité """
        DB = GestionDB.DB()
        req = """SELECT IDouverture, date
        FROM ouvertures 
        WHERE IDactivite=%d AND date>'%s'
        ORDER BY date; """ % (IDactivite, str(date))
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            return None
        IDouverture, dateTmp = listeDonnees[0]
        DB.Close()
        return DateEngEnDateDD(dateTmp)
        
    def Procedure_reserver(self, dictAction, IDindividu, date, heure):
        """ Procédure Réserver """
        IDactivite = int(dictAction["action_activite"])
        listeUnites = ConvertStrToListe(dictAction["action_unite"])
        etat = dictAction["action_etat"]
        attente = int(dictAction["action_attente"])
        dateTmp = dictAction["action_date"]
        question = dictAction["action_question"]
        confirmation = dictAction["action_message"]
        vocal = int(dictAction["action_vocal"])
        
        # Recherche la date proposée
        if dateTmp == "date_actuelle" :
            dateTmp = date
        elif dateTmp == "prochaine_ouverture" :
            dateTmp = self.RechercheProchaineOuverture(IDactivite, date)
            if dateTmp == None :
                self.log.AjouterAction(action=_(u"Réservation de consommations"), resultat=_(u"Pas d'ouvertures futures pour cette activité"))
                return False
        else :
            return False
        
        # Récupération des infos sur l'activité et sur l'individu
        dictActivite, dictUnites, listeOuvertures, dictGroupes = GetInfosActivite(IDactivite, dateTmp) 
        nomIndividu = u"%s %s" % (self.infosIndividus.RechercheIndividu(IDindividu)["nom"], self.infosIndividus.RechercheIndividu(IDindividu)["prenom"])
        nomAction = _(u"Réservation de consommations '%s'") % dictActivite["nom"]
        
        # Recherche si l'individu est bien inscrit à l'activité
        IDfamille, IDgroupe = self.RechercheInscription(IDindividu, nomIndividu, IDactivite, dictActivite, nomAction)
        if IDfamille == False :
            return False
        
        # Recherche si l'unité est ouverte pour ce groupe à cette date
        listeUnitesOuvertes = []
        for IDunite in listeUnites :
            if (IDunite, IDgroupe) in listeOuvertures :
                listeUnitesOuvertes.append(IDunite)
        if len(listeUnitesOuvertes) == 0 :
            self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=_(u"Aucune unité ouverte le %s") % DateEngFr(str(dateTmp)))
            return False
        
        # Proposition à l'individu
        if len(listeUnitesOuvertes) == 1 :
            
            # Si une seule unité à proposer
            texte = self.RemplacementVariablesMessages(question, heure, IDindividu, dateTmp)
            dlg = DIALOGUES.DLG_Question(self, message=texte, icone="question")
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False
            listeUnitesChoisies = listeUnitesOuvertes
        
        else :
            # Si plusieurs unités à proposer
            listeLabelsUnites = []
            for IDunite in listeUnitesOuvertes :
                listeLabelsUnites.append(dictUnites[IDunite]["nom"])
            texte = self.RemplacementVariablesMessages(question, heure, IDindividu, dateTmp)
            dlg = DIALOGUES.DLG_Choix(self, message=texte, listeItems=listeLabelsUnites, multiSelection=True)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                listeUnitesChoisies = []
                for index in dlg.GetSelections() :
                    listeUnitesChoisies.append(listeUnitesOuvertes[index])
                self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=True)
            else :
                self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=_(u"Annulation par l'individu"))
                return False
            
        # Initialisation de la grille des conso
        self.ctrl_grille.InitGrille(IDindividu=IDindividu, IDfamille=IDfamille, IDactivite=IDactivite, date=dateTmp)
        
        # Vérifie qu'il y a des places disponibles
        listeUnitesCompletes = []
        for IDunite in listeUnitesChoisies :
            placeDispo = self.ctrl_grille.HasPlacesDisponibles(IDunite) 
            if placeDispo == False :
                listeUnitesCompletes.append(dictUnites[IDunite][nom]) 
                    
        if len(listeUnitesCompletes) > 0 :
            texte = _(u"Désolé mais il est possible qu'il n'y ait plus de places. Contactez un responsable.")
            DIALOGUES.DLG_Message(self, message=texte, icone="exclamation")
            self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=_(u"Plus de places sur les unités %s") % u", ".join(listeUnitesCompletes))
            return False
            
        # Saisie de la consommation
        for IDunite in listeUnitesChoisies :
            resultat = self.ctrl_grille.SaisieConso(IDunite=IDunite, mode="reservation", etat=etat, heure_debut="defaut", heure_fin="defaut")
            self.log.AjouterAction(individu=nomIndividu, IDindividu=IDindividu, action=nomAction, resultat=resultat)
        
        # Sauvegarde de la grille des conso
        self.ctrl_grille.Sauvegarde()
        # Affichage du message de confirmation
        if confirmation != None :
            texte = self.RemplacementVariablesMessages(confirmation, heure, IDindividu, dateTmp)
            DIALOGUES.DLG_Message(self, message=texte, icone="information")
        return True

    def ImportationBadgeage(self):
        """ Analyse de badgeages importés """
        # Traitement
        for track in self.importationManuelle :
            IDindividu = self.IdentificationCodebarre(track.codebarres)
            if IDindividu == None :
                self.log.AjouterAction(individu="", IDindividu=None, action=_(u"Identification d'un code-barres"), resultat=_(u"Code-barres inconnu ('%s')") % track.codebarres)
            else :
                self.Procedure(IDindividu, track.date, track.heure)

        wx.CallAfter(self.parent.Fermer)
        
        

# ---------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, log=None, IDprocedure=None, date=None, dateauto=False, importationManuelle=False, style=wx.BORDER_NONE):
        wx.Dialog.__init__(self, parent, -1, style=style)
        self.parent = parent
        self.importationManuelle = importationManuelle
        
        # Création d'une dlg d'attente durant l'initialisation
        try :
            if importationManuelle == False :
                texte = _(u"Veuillez patienter durant l'initialisation de l'interface de badgeage...")
            else :
                texte = _(u"Veuillez patienter durant l'importation des badgeages...")
            dlgAttente = PBI.PyBusyInfo(texte, parent=None, title=_(u"Initialisation"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            
            if wx.GetKeyState(307) == True :
                montrerGrille = True
            else :
                montrerGrille = False

            # Initialisation de l'interface
            self.interface = CTRL_Interface(self, log=log, IDprocedure=IDprocedure, date=date, dateauto=dateauto, importationManuelle=importationManuelle, montrerGrille=montrerGrille)
            
            # Layout
            self.SetMinSize((1300, 700))
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.interface, 1, wx.EXPAND, 0)
            self.SetSizer(sizer)
            self.Layout()
            self.CentreOnScreen()
            
            # Touches de raccourcis
            ID_FERMER = wx.NewId()
            self.Bind(wx.EVT_MENU, self.Fermer, id=ID_FERMER)
            accel_tbl = wx.AcceleratorTable([
                (wx.ACCEL_CTRL|wx.ACCEL_SHIFT,  ord('Q'), ID_FERMER),
                ])
            self.SetAcceleratorTable(accel_tbl)
            
            # Fin de la dlg d'attente
            del dlgAttente

        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans l'initialisation de l'interface de badgeage : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.Destroy()

        # Binds
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.interface.StopTimer()
        event.Skip()

    def Fermer(self, event=None):
        # Fermeture
        self.EndModal(wx.ID_OK)
        
        
        
class LogTest():
    """ Une déviation du log pour les tests uniquement """
    def __init__(self):
        pass
    def AjouterAction(self, individu=u"", IDindividu=None, action=u"", resultat=True):
        print "LOG =", (action, individu, resultat)
        
        
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None, log=LogTest(), IDprocedure=6, date=datetime.date.today(), dateauto=True, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()