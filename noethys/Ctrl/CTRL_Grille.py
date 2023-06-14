#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""


import wx
from Ctrl import CTRL_Bouton_image
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import datetime
import decimal
import six
import copy
import time
import math
import random
import re
import wx.lib.agw.supertooltip as STT
import pdb, traceback, sys

if six.PY3:
    import functools

import GestionDB
from Data import DATA_Touches as Touches
from Utils import UTILS_Identification
from Utils import UTILS_Historique
from Utils import UTILS_Filtres_questionnaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Divers
from Utils import UTILS_Parametres
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Gestion
import FonctionsPerso

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES
from Data.DATA_Tables import DB_DATA as DICT_TABLES
from Utils import UTILS_Dates
from Ctrl import CTRL_Grille_cases
from Ctrl import CTRL_Grille_renderers
from Utils import UTILS_Texte


# Param�tres personnalisables
AFFICHE_NOM_GROUPE = True
AFFICHE_COLONNE_MEMO = True
AFFICHE_COLONNE_TRANSPORTS = True
FORMAT_LABEL_LIGNE = "nom_prenom"
MASQUER_UNITES_FERMEES = False

# Colonnes unit�s
HAUTEUR_LIGNE = 30
LARGEUR_COLONNE_UNITE = 50
LARGEUR_COLONNE_MEMO = 170
LARGEUR_COLONNE_TRANSPORTS = 100
LARGEUR_COLONNE_MULTIHORAIRES = 200
LARGEUR_COLONNE_EVENEMENT = 200

# Colonnes Activit�s
LARGEUR_COLONNE_ACTIVITE = 18
COULEUR_COLONNE_ACTIVITE = wx.Colour(205, 144, 233)

# Cases
COULEUR_RESERVATION = wx.Colour(252, 213, 0) # ancien vert : "#A6FF9F"
COULEUR_ATTENTE = wx.Colour(255, 255, 0)
COULEUR_REFUS = wx.Colour(255, 0, 0)
COULEUR_DISPONIBLE = wx.Colour(227, 254, 219)
COULEUR_ALERTE = wx.Colour(254, 252, 219)
COULEUR_COMPLET = wx.Colour(247, 172, 178)
COULEUR_NORMAL = wx.Colour(255, 255, 255)
COULEUR_FERME = wx.Colour(220, 220, 220)

# Transports
DICT_ARRETS = {}
DICT_LIEUX = {}
DICT_ACTIVITES = {}
DICT_ECOLES = {}



def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng in (None, "", "None") : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0)
    heures, minutes = heureStr.split(":")
    return datetime.time(int(heures), int(minutes))

def HeureStrEnDelta(heureStr):
    if heureStr == None or heureStr == "" : return datetime.timedelta(0)
    heures, minutes = heureStr.split(":")
    return datetime.timedelta(minutes= int(heures)*60 + int(minutes))

def TimeEnDelta(heureTime):
    hr = heureTime.hours
    mn = heureTime.minutes
    return datetime.timedelta(hours=hr, minutes=mn)

def DeltaEnTime(varTimedelta) :
    """ Transforme une variable TIMEDELTA en heure datetime.time """
    heureStr = time.strftime("%H:%M", time.gmtime(varTimedelta.seconds))
    heure = HeureStrEnTime(heureStr)
    return heure

def DeltaEnStr(heureDelta, separateur="h"):
    texte = time.strftime("%Hh%M", time.gmtime(heureDelta.seconds))
    texte = texte.replace("h", separateur)
    return texte

def TimeEnStr(heure, separateur="h"):
    texte = heure.strftime("%Hh%M")
    texte = texte.replace("h", separateur)
    return texte


def Additionne_intervalles_temps(intervals=[]):
    def tparse(timestring):
##        heures, minutes = timestring.split(":")
##        return datetime.datetime(1900, 1, 1, int(heures), int(minutes), 0)
        return datetime.datetime.strptime(timestring, '%H:%M')
    
    START, END = range(2)
    times = []
    for interval in intervals:
        times.append((tparse(interval[START]), START))
        times.append((tparse(interval[END]), END))
    times.sort()

    started = 0
    result = datetime.timedelta()
    for t, categorie in times:
        if categorie == START:
            if not started:
                start_time = t
            started += 1
        elif categorie == END:
            started -= 1
            if not started:
               result += (t - start_time) 
    return result

def SoustractionHeures(heure_max, heure_min):
    """ Effectue l'op�ration heure_max - heure_min. Renvoi un timedelta """
    h_max = datetime.timedelta(hours=heure_max.hour, minutes=heure_max.minute)
    h_min =  datetime.timedelta(hours=heure_min.hour, minutes=heure_min.minute)
    return h_max - h_min

def ConvertStrToListe(texte=None, siVide=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte in (None, "") :
        return siVide
    listeResultats = []
    if type(texte) == int:
        temp = [texte,]
    else:
        temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats

def ConvertListeToStr(liste=[]):
    if liste == None : liste = []
    return ";".join([str(x) for x in liste])

def CompareDict(dict1={}, dict2={}, keys=[]):
    """ Compare les valeurs de 2 dictionnaires selon les cl�s donn�es """
    isIdem = True
    for key in keys:
        if dict1[key] != dict2[key] :
            isIdem = False
    return isIdem

def CreationImage(largeur, hauteur, couleur=None):
    """ couleur peut �tre RGB ou HEXA """
    if 'phoenix' in wx.PlatformInfo:
        b = wx.Bitmap(largeur, hauteur)
    else :
        b = wx.EmptyBitmap(largeur, hauteur)
    dc = wx.MemoryDC() 
    dc.SelectObject(b) 
    dc.SetBackground(wx.Brush("black")) 
    dc.Clear() 
    dc.SetBrush(wx.Brush(couleur)) 
    y = hauteur / 2.0 - largeur / 2.0
    dc.DrawRectangle(0, y, largeur, largeur)
    dc.SelectObject(wx.NullBitmap) 
    b.SetMaskColour("black") 
    return b

def sub(g):
    heures = int(g.group(1))
    minutes = int(g.group(2))
    resultat = datetime.timedelta(minutes= int(heures)*60 + int(minutes))
    return resultat.__repr__()


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, ctrl_grille=None, size=(-1,20)):
        wx.SearchCtrl.__init__(self, parent, size=size, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.ctrl_grille = ctrl_grille
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

        # HACK pour avoir le EVT_CHAR
        for child in self.GetChildren(): 
            if isinstance(child, wx.TextCtrl): 
                child.Bind(wx.EVT_CHAR, self.OnKeyDown) 
                break 

    def OnKeyDown(self, event):
        """ Efface tout si touche ECHAP """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE :
            self.OnCancel(None) 
        event.Skip()

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.ctrl_grille.RechercheTexteLigne(txtSearch)
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------


class Conso():
    def __init__(self):
        self.IDconso = None
        self.IDactivite = None
        self.IDinscription = None
        self.IDgroupe = None
        self.heure_debut = None
        self.heure_fin = None
        self.etat = None
        self.verrouillage = None
        self.date_saisie = None
        self.IDutilisateur = None
        self.IDcategorie_tarif = None
        self.IDfamille = None
        self.IDcompte_payeur = None
        self.IDprestation = None
        self.forfait = None
        self.IDfacture = None
        self.quantite = None
        self.statut = None
        self.case = None
        self.etiquettes = []
        self.IDevenement = None
        self.badgeage_debut = None
        self.badgeage_fin = None


    
class Ligne():
    def __init__(self, grid, numLigne=None, IDindividu=None, IDfamille=None, date=None, modeLabel="nom", estSeparation=False):
        self.grid = grid
        self.estSeparation = estSeparation
        self.numLigne = numLigne
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.date = date
        self.modeLabel = modeLabel
        self.coche = False

##        self.listeConso = []
        if self.IDindividu != None :
            self.dictInfosIndividu = grid.dictInfosIndividus[self.IDindividu]
        
        # Label de la ligne
        if modeLabel == "date" : 
            self.labelLigne = DateComplete(self.date)
        if modeLabel == "nom" : 
            if FORMAT_LABEL_LIGNE == "nom_prenom" :
                nomIndividu = u"%s %s" % (self.dictInfosIndividu["nom"], self.dictInfosIndividu["prenom"])
            if FORMAT_LABEL_LIGNE == "prenom_nom" :
                nomIndividu = u"%s %s" % (self.dictInfosIndividu["prenom"], self.dictInfosIndividu["nom"])
            if FORMAT_LABEL_LIGNE == "nom_prenom_id" :
                nomIndividu = u"%s %s (%s)" % (self.dictInfosIndividu["nom"], self.dictInfosIndividu["prenom"], self.IDindividu)
            if FORMAT_LABEL_LIGNE == "prenom_nom_id" :
                nomIndividu = u"%s %s (%s)" % (self.dictInfosIndividu["prenom"], self.dictInfosIndividu["nom"], self.IDindividu)

            self.labelLigne = nomIndividu
        
        # Couleurs de label
        couleurLigneDate = "#C0C0C0"
        self.couleurOuverture = (0, 230, 0)
        self.couleurFermeture = "#F7ACB2"
        couleurVacances = "#F3FD89"
        
        # Cr�ation du label de ligne
        if self.estSeparation == True :
            hauteurLigne = 18
        else:
            hauteurLigne = self.grid.dictParametres["hauteur"]
        self.grid.SetRowLabelValue(numLigne, self.labelLigne)
        if hauteurLigne != None :
            self.grid.SetRowSize(numLigne, hauteurLigne)
        if self.EstEnVacances(self.date) == True :
            couleurCase = couleurVacances
        else:
            couleurCase = None
            
        if modeLabel == "date" : 
            dateTemp = self.date
        else :
            dateTemp = None

        if self.estSeparation == True :
            couleurCase = (150, 150, 150)
        if self.estSeparation == True :
            self.renderer_label = CTRL_Grille_renderers.LabelLigneSeparation(couleurCase, dateTemp)
        else :
            self.renderer_label = CTRL_Grille_renderers.LabelLigneStandard(couleurCase, dateTemp, self)
        self.grid.SetRowLabelRenderer(numLigne, self.renderer_label)
        self.grid.dictLignes[numLigne] = self.renderer_label
        
        # Cr�ation des cases
        self.dictCases = {}
        numColonne = 0
        for IDactivite in self.grid.listeActivites :
            # Cr�ation de la colonne activit�
            if len(self.grid.listeActivites) > 1 and IDactivite in self.grid.dictListeUnites :
                case = CTRL_Grille_cases.CaseSeparationActivite(self, self.grid, self.numLigne, numColonne, IDactivite)
                self.dictCases[numColonne] = case
                numColonne += 1
                
            # V�rifie s'il faut verrouiller la ligne            
            IDfamilleConso = None
            if self.IDindividu in self.grid.dictConsoIndividus :
                if self.date in self.grid.dictConsoIndividus[self.IDindividu] :
                    for IDunite, listeConso in self.grid.dictConsoIndividus[self.IDindividu][self.date].items() :
                        for conso in listeConso :
                            IDfamilleConso = conso.IDfamille
                            break
                        
            # Cr�ation des cases unit�s
            if IDactivite in self.grid.dictListeUnites :
                for dictUnite in self.grid.dictListeUnites[IDactivite] :
                    IDunite = dictUnite["IDunite"]
                    IDactivite = dictUnite["IDactivite"]
                    typeUnite = dictUnite["type"]
                    if self.estSeparation == True :
                        case = CTRL_Grille_cases.CaseSeparationDate(self, self.grid, self.numLigne, numColonne, couleurCase)
                    else:
                        # Recherche du IDfamille
                        IDfamille = None
                        if self.grid.IDfamille != None :
                            IDfamille = self.grid.IDfamille
                        else:
                            if IDindividu in self.grid.dictInfosInscriptions :
                                if IDactivite in self.grid.dictInfosInscriptions[IDindividu] :
                                    IDfamille = self.grid.dictInfosInscriptions[IDindividu][IDactivite]["IDfamille"]

                        # Verrouillage si parti de l'activit�
                        verrouillage = 0
                        if IDindividu in self.grid.dictInfosInscriptions :
                            if IDactivite in self.grid.dictInfosInscriptions[IDindividu] :
                                date_desinscription = self.grid.dictInfosInscriptions[IDindividu][IDactivite]["date_desinscription"]
                                if date_desinscription != None and self.date > date_desinscription :
                                    verrouillage = 1

                        # S'il y a des conso rattach�es � une autre famille, on verrouille la ligne
                        if IDfamilleConso != None :
                            if IDfamille != IDfamilleConso :
                                verrouillage = 1
                                IDfamille = IDfamilleConso
                        
                        # Cr�ation de la case
                        if typeUnite in ("Unitaire", "Horaire", "Quantite") :
                            case = CTRL_Grille_cases.CaseStandard(self, self.grid, self.numLigne, numColonne, self.IDindividu, IDfamille, self.date, IDunite, IDactivite, verrouillage)

                        if typeUnite == "Multihoraires" :
                            heure_min = self.grid.dictColonnesMultihoraires[IDunite]["min"]
                            heure_max = self.grid.dictColonnesMultihoraires[IDunite]["max"]

                            if heure_min == None :
                                heure_min = datetime.time(0, 0)
                            if heure_max == None or heure_max == datetime.time(0, 0) :
                                heure_max = datetime.time(23, 0)

                            case = CTRL_Grille_cases.CaseMultihoraires(self, self.grid, self.numLigne, numColonne, self.IDindividu, IDfamille, self.date, IDunite, IDactivite, verrouillage, heure_min, heure_max)

                        if typeUnite == "Evenement" :
                            case = CTRL_Grille_cases.CaseEvenement(self, self.grid, self.numLigne, numColonne, self.IDindividu, IDfamille, self.date, IDunite, IDactivite, verrouillage)

                        case.IDunite = IDunite
                        self.dictCases[numColonne] = case
                    numColonne += 1
        
        # M�mo journalier
        if AFFICHE_COLONNE_MEMO == True :
            if len(self.grid.listeActivites) > 1 :
                case = CTRL_Grille_cases.CaseSeparationActivite(self, self.grid, self.numLigne, numColonne, None, estMemo=True)
                self.dictCases[numColonne] = case
                numColonne += 1
            if (self.IDindividu, self.date) in self.grid.dictMemos :
                texteMemo = self.grid.dictMemos[(self.IDindividu, self.date)]["texte"]
                IDmemo = self.grid.dictMemos[(self.IDindividu, self.date)]["IDmemo"]
                couleur = self.grid.dictMemos[(self.IDindividu, self.date)]["couleur"]
            else:
                texteMemo = ""
                IDmemo = None
                couleur = None
            if self.estSeparation == True :
                case = CTRL_Grille_cases.CaseSeparationDate(self, self.grid, self.numLigne, numColonne, couleurCase)
            else:
                case = CTRL_Grille_cases.CaseMemo(self, self.grid, self.numLigne, numColonne, self.IDindividu, self.date, texteMemo, IDmemo, couleur)
            self.dictCases[numColonne] = case
            numColonne += 1

        # Transports
        if AFFICHE_COLONNE_TRANSPORTS == True :
            if self.estSeparation == True :
                case = CTRL_Grille_cases.CaseSeparationDate(self, self.grid, self.numLigne, numColonne, couleurCase)
            else:
                case = CTRL_Grille_cases.CaseTransports(self, self.grid, self.numLigne, numColonne, self.IDindividu, self.date)
            self.dictCases[numColonne] = case
    
    def MAJcouleurCases(self, saufCase=None):
        """ MAJ la couleur des cases de la ligne en fonction du remplissage """
        # MAJ toute la ligne
        for numColonne, case in self.dictCases.items() :
            if case != saufCase and case.typeCase == "consommation" :
                case.Refresh()

    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.grid.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def OnLeftClick(self):
        if self.estSeparation == True :
            return
        self.coche = not self.coche
        self.renderer_label.MAJCase()

    def OnContextMenu(self):
        return
    
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item IDENTIFICATION DE LA LIGNE
        item = wx.MenuItem(menuPop, 10, self.labelLigne)
        menuPop.AppendItem(item)
        item.Enable(False)
        
        menuPop.AppendSeparator()

##        # Item Verrouillage
##        item = wx.MenuItem(menuPop, 10, _(u"Verrouiller toutes les consommations"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas_ferme.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.grid.Bind(wx.EVT_MENU, self.Verrouillage, id=10)
##        
##        item = wx.MenuItem(menuPop, 20, _(u"D�verrouiller toutes les consommations"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.grid.Bind(wx.EVT_MENU, self.Deverrouillage, id=20)
        
        # Etat des consommations de la ligne
        nbreCasesReservations = 0
        for numColonne, case in self.dictCases.items() :
            if case.typeCase == "consommation" :
                for conso in case.GetListeConso () :
                    if conso.etat in ("reservation", "present", "absenti", "absentj") :
                        nbreCasesReservations += 1
                    
        if nbreCasesReservations > 0 :
            
            item = wx.MenuItem(menuPop, 30, _(u"D�finir toutes les pointages de la ligne comme 'Pointage en attente'"))
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=30)
            
            item = wx.MenuItem(menuPop, 40, _(u"Pointer toutes les consommations de la ligne sur 'Pr�sent'"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok5.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=40)
            
            item = wx.MenuItem(menuPop, 50, _(u"Pointer toutes les consommations de la ligne sur 'Absence justifi�e'"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absentj.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=50)
            
            item = wx.MenuItem(menuPop, 60, _(u"Pointer toutes les consommations de la ligne sur 'Absence injustifi�e'"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absenti.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=60)
            
        self.grid.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def SetPresentAbsent(self, event):
        ID = event.GetId()
        for numColonne, case in self.dictCases.items() :
            if case.typeCase == "consommation" :
                if ID == 30 and case.etat in ("reservation", "present", "absenti", "absentj") :
                    if case.etat in ("absenti", "absentj"):
                        case.ModifierTotaux(1)
                    case.etat = "reservation"
                if ID == 40 and case.etat in ("reservation", "present", "absenti", "absentj") :
                    if case.etat in ("absenti", "absentj"):
                        case.ModifierTotaux(1)
                    case.etat = "present"
                if ID == 50 and case.etat in ("reservation", "present", "absenti", "absentj") :
                    if case.etat in ("reservation", "present"):
                        case.ModifierTotaux(-1)
                    case.etat = "absentj"
                if ID == 60 and case.etat in ("reservation", "present", "absenti", "absentj") :
                    if case.etat in ("reservation", "present"):
                        case.ModifierTotaux(-1)
                    case.etat = "absenti"
                case.MemoriseValeurs()
                case.renderer.MAJ()
        self.MAJctrl_totaux()
        self.grid.listeHistorique.append((self.IDindividu, self.date, None, _(u"Modification de l'�tat de toutes les consommations de la ligne")))
                
    
    def Verrouillage(self, event):
        for numColonne, case in self.dictCases.items() :
            if case.typeCase == "consommation" :
                if case.etat != None :
                    case.Verrouillage(None)

    def Deverrouillage(self, event):
        for numColonne, case in self.dictCases.items() :
            if case.typeCase == "consommation" :
                if case.etat != None :
                    case.Deverrouillage(None)
        
    def MAJctrl_totaux(self):
        if self.grid.mode == "date" :
            self.grid.GetGrandParent().MAJ_totaux_contenu()
    
    def RechercheCase(self, typeCase=""):
        """ Retourne une case selon son type """
        for index, case in self.dictCases.items() :
            if case.typeCase == typeCase :
                return case
        return None

    def Flash(self, couleur="#316AC5"):
        """ Met en surbrillance la case quelques instants """
        wx.CallLater(1, self.renderer_label.Flash, couleur)
        
##        wx.CallLater(1, self.SetCouleurFondLabel, couleur)
##        couleurInitiale = self.renderer_label.couleurFond
##        wx.CallLater(1000, self.SetCouleurFondLabel, couleurInitiale)
    
##    def SetCouleurFondLabel(self, couleur):
##        self.renderer_label.MAJ(couleur)
##        self.grid.Refresh() 
        

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent, mode="individu", IDfamille=None):
        gridlib.Grid.__init__(self, parent, -1, size=(1, 1), style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.mode = mode
        self.IDfamille = IDfamille
        
        # Utilisateur en cours
        self.IDutilisateur = UTILS_Identification.GetIDutilisateur()

        # P�riodes de gestion
        self.gestion = UTILS_Gestion.Gestion(self)
        
        # Init Tooltip
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip apr�s 10 secs

        # Cr�ation initiale de la grille
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(180)
        self.EnableGridLines(False)
##        self.DisableDragColSize()
##        self.DisableDragRowSize()

        # Pour cacher le curseur
        self.SetCellHighlightPenWidth(0)
        self.SetCellHighlightROPenWidth(0)

        self.SetDefaultCellBackgroundColour(self.GetBackgroundColour())
        
        # R�cup�ration des param�tres
        global AFFICHE_COLONNE_MEMO, AFFICHE_COLONNE_TRANSPORTS, FORMAT_LABEL_LIGNE, MASQUER_UNITES_FERMEES
        
        parametresDefaut = {
            "affiche_colonne_memo" : AFFICHE_COLONNE_MEMO,
            "affiche_colonne_transports" : AFFICHE_COLONNE_TRANSPORTS,
            "format_label_ligne" : FORMAT_LABEL_LIGNE,
            "affiche_sans_prestation" : True,
            "blocage_si_complet" : True,
            "hauteur_lignes" : HAUTEUR_LIGNE,
            "largeur_colonne_memo" : LARGEUR_COLONNE_MEMO,
            "largeur_colonne_transports" : LARGEUR_COLONNE_TRANSPORTS,
            "masquer_unites_fermees": MASQUER_UNITES_FERMEES,
            }
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="parametres_grille_conso", dictParametres=parametresDefaut)
        
        # Param�tres divers
        AFFICHE_COLONNE_MEMO = dictParametres["affiche_colonne_memo"]
        AFFICHE_COLONNE_TRANSPORTS = dictParametres["affiche_colonne_transports"]
        FORMAT_LABEL_LIGNE = dictParametres["format_label_ligne"]
        self.blocageSiComplet = dictParametres["blocage_si_complet"]
        self.afficheSansPrestation = dictParametres["affiche_sans_prestation"]
        MASQUER_UNITES_FERMEES = dictParametres["masquer_unites_fermees"]

        # Hauteur lignes et largeurs colonne
        self.dictParametres = { 
            "hauteur" : dictParametres["hauteur_lignes"], 
            "largeurs" : { 
                "unites" : {}, 
                "memo" : dictParametres["largeur_colonne_memo"], 
                "transports" : dictParametres["largeur_colonne_transports"],
            } }

        # Binds
        self.barreMoving = None
        self.casesSurvolees = None

        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        if 'phoenix' in wx.PlatformInfo:
            self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.OnModificationMemo)
        else :
            self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnModificationMemo)
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnChangeRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnChangeColSize)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseOver)
        self.GetGridWindow().Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.GetGridWindow().Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDoubleClick)

        # Init Donn�es
        self.InitDonnees()
        
    def InitDonnees(self):
        self.tarifsForfaitsCreditsPresents = False
        self.afficherListeEtiquettes = False
        
        self.DB = GestionDB.DB()
        self.dictActivites = self.Importation_activites()
        self.dictIndividus = self.Importation_individus() 
        self.dictGroupes = self.GetDictGroupes()
        self.dictComptesPayeurs = self.GetComptesPayeurs()
        self.dictQuotientsFamiliaux = self.GetQuotientsFamiliaux()
        self.dictAides = self.GetAides() 
        self.dictEtiquettes = self.GetDictEtiquettes()
        self.DB.Close() 
        
        self.listePeriodes = []
        self.dictPrestations = {}
        self.dictDeductions = {}
        self.dictConsoIndividus = {}
        self.listeSelectionIndividus = []
        self.listeIndividusFamille = []
        self.listePrestationsSupprimees = []
        self.listePrestationsModifiees = []
        self.listeConsoSupprimees = []
        self.prochainIDprestation = -1
        self.prochainIDdeduction = -1
        self.prochainIDtransport = -1
        self.listeTransportsInitiale = []
        self.moveTo = None
        try:
            self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        except:
            pass
        self.caseSurvolee = None
        self.listeHistorique = []
        self.dictLignes = {}
        self.memoireHoraires = {}
        self.dictForfaits = {}
        self.dict_transports_prog = {}
        self.dict_transports = {}
        
                        
        
    def SetModeIndividu(self, listeActivites=[], listeSelectionIndividus=[], listeIndividusFamille=[], listePeriodes=[], modeSilencieux=False):
        if modeSilencieux == False :
            attente = wx.BusyInfo(_(u"Recherche des donn�es..."), self)
        self.mode = "individu"
        self.listeActivites = listeActivites
        self.listeSelectionIndividus = listeSelectionIndividus
        self.listeIndividusFamille = listeIndividusFamille
        self.listePeriodes = listePeriodes
        self.DB = GestionDB.DB()
        self.Importation_deductions(listeComptesPayeurs=[self.dictComptesPayeurs[self.IDfamille],])
        self.Importation_prestations(listeComptesPayeurs=[self.dictComptesPayeurs[self.IDfamille],]) 
        self.Importation_forfaits(listeComptesPayeurs=[self.dictComptesPayeurs[self.IDfamille],]) 
        self.Importation_transports()
        self.DB.Close()
        self.MAJ()
        if modeSilencieux == False :
            del attente

    def SetModeDate(self, listeActivites=[], listeSelectionIndividus=[], date=None, modeSilencieux=False):
        if modeSilencieux == False :
            attente = wx.BusyInfo(_(u"Recherche des donn�es..."), self)
        self.mode = "date"
        self.listeActivites = listeActivites
        self.date = date
        self.listeSelectionIndividus = listeSelectionIndividus
        self.listeIndividusFamille = []
        self.IDgroupe = None
        self.listePeriodes = [(self.date, self.date),]
        self.DB = GestionDB.DB()
        self.Importation_prestations()
        self.Importation_forfaits()
        self.Importation_transports()
        self.DB.Close()
        self.MAJ()
        if modeSilencieux == False :
            del attente

    def MAJ(self):
        self.MAJ_donnees()
        self.MAJ_affichage()
        self.SetFocus()

    def MAJ_donnees(self):
        # R�cup�ration des donn�es
        self.DB = GestionDB.DB()
        self.dictOuvertures, self.listeUnitesOuvertes = self.GetDictOuvertures(self.listeActivites, self.listePeriodes)
        self.dictListeUnites, self.dictUnites = self.GetListeUnites(self.listeUnitesOuvertes)
        self.listeTouchesRaccourcis = self.GetListeTouchesRaccourcis()
        self.listeVacances = self.GetListeVacances() 
        self.listeFeries = self.GetListeFeries() 
        self.dictRemplissage, self.dictUnitesRemplissage, self.dictConsoIndividus = self.GetDictRemplissage(self.listeActivites, self.listePeriodes, self.listeIndividusFamille)
        if self.mode == "individu" :
            listeIndividus = self.listeSelectionIndividus
        else:
            listeIndividus = self.listeSelectionIndividus #self.dictConsoIndividus.keys()
        self.dictInfosInscriptions = self.GetInfosInscriptions(listeIndividus)
        self.dictInfosIndividus = self.GetInfosIndividus(listeIndividus)
        self.dictMemos = self.GetDictMemoJournee(self.listeActivites, self.listePeriodes, self.listeIndividusFamille)
        self.DB.Close()
        
        self.CalcRemplissage() 
        
    def MAJ_affichage(self):
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitGrid()
        self.Refresh()
        self.MAJ_facturation()
    
    def MAJcouleurCases(self, saufLigne=None):
        for numLigne, ligne in self.dictLignes.items() :
            if ligne.estSeparation == False and ligne != saufLigne :
                ligne.MAJcouleurCases()
    
    def CalcRemplissage(self):
        """ Calcule tout le remplissage """
        self.dictRemplissage2 = {}
        self.dictRemplissageEvenements = {}
        self.dictConsoUnites = {}
        for IDindividu, dictDates in self.dictConsoIndividus.items() :
            for date, dictUnites in dictDates.items() :
                for IDunite, listeConso in dictUnites.items() :
                    quantite = None
                    
                    for conso in listeConso :
                        if conso.etat in ["reservation", "present", "attente"] :

                            # M�morisation sp�ciale si c'est un �v�nement
                            if conso.IDevenement != None :
                                if (conso.IDevenement in self.dictRemplissageEvenements) == False :
                                    self.dictRemplissageEvenements[conso.IDevenement] = {"reservation" : 0, "present" : 0, "attente" : 0}
                                self.dictRemplissageEvenements[conso.IDevenement][conso.etat] += 1

                            # Quantit�
                            if conso.quantite != None :
                                quantite = conso.quantite
                            else :
                                quantite = 1

                            # M�morisation par unit� de remplissage
                            if conso.IDunite in self.dictUnitesRemplissage :
                                for IDunite_remplissage in self.dictUnitesRemplissage[conso.IDunite] :
                                    if IDunite_remplissage in self.dictRemplissage :
                                        valide = True
                                        
                                        # V�rifie s'il y a une plage horaire conditionnelle :
                                        if "heure_min" in self.dictRemplissage[IDunite_remplissage] :
                                            heure_min = self.dictRemplissage[IDunite_remplissage]["heure_min"]
                                            heure_max = self.dictRemplissage[IDunite_remplissage]["heure_max"]
                                        else :
                                            heure_min, heure_max = None, None
                                        if heure_min != None and heure_max != None and conso.heure_debut != None and conso.heure_fin != None :
                                            try :
                                                if UTILS_Dates.HeureStrEnTime(conso.heure_debut) <= UTILS_Dates.HeureStrEnTime(heure_max) and UTILS_Dates.HeureStrEnTime(conso.heure_fin) >= UTILS_Dates.HeureStrEnTime(heure_min) :
                                                    valide = True
                                                else:
                                                    valide = False
                                            except :
                                                 valide = True

                                        # V�rifie si condition �tiquettes
                                        if "etiquettes" in self.dictRemplissage[IDunite_remplissage]:
                                            etiquettes = self.dictRemplissage[IDunite_remplissage]["etiquettes"]
                                        else :
                                            etiquettes = []
                                        if len(etiquettes) > 0 :
                                            etiquettesCommunes = set(etiquettes) & set(conso.etiquettes)
                                            if len(etiquettesCommunes) == 0 :
                                                valide = False

                                        # M�morisation de la place prise
                                        self.dictRemplissage2 = UTILS_Divers.DictionnaireImbrique(dictionnaire=self.dictRemplissage2, cles=[IDunite_remplissage, date, conso.IDgroupe, conso.etat], valeur=0)
                                        if valide == True :
                                            self.dictRemplissage2[IDunite_remplissage][date][conso.IDgroupe][conso.etat] += quantite

                            # M�morisation pour les totaux du gestionnaire de conso
                            if conso.etat in ["reservation", "present"] and self.mode == "date" and quantite != None and date == self.date :
                                self.dictConsoUnites = UTILS_Divers.DictionnaireImbrique(dictionnaire=self.dictConsoUnites, cles=[conso.IDunite, conso.IDgroupe], valeur=0)
                                self.dictConsoUnites[conso.IDunite][conso.IDgroupe] += quantite


    def GetInfosColonnesMultihoraires(self):
        dictColonnesMultihoraires = {}
        
        for IDactivite, listeUnites in self.dictListeUnites.items() :
            for dictUnite in listeUnites :
                if dictUnite["type"] == "Multihoraires" :
                    dictColonnesMultihoraires[dictUnite["IDunite"]] = {"min" : HeureStrEnTime(dictUnite["heure_debut"]), "max" : HeureStrEnTime(dictUnite["heure_fin"])}
            
        # Recherche horaires min et max
        if len(dictColonnesMultihoraires) > 0 :
            for IDindividu, dictIndividu in self.dictConsoIndividus.items() :
                for date, dictDate in dictIndividu.items() :
                    for IDunite, listeConso in dictDate.items() :
                        if IDunite in dictColonnesMultihoraires :
                            for conso in listeConso :
                                if conso.heure_debut != None and conso.heure_fin != None :
                                    if dictColonnesMultihoraires[IDunite]["min"] == None or HeureStrEnTime(conso.heure_debut) < dictColonnesMultihoraires[IDunite]["min"] :
                                        heure = HeureStrEnTime(conso.heure_debut)
                                        if heure.minute > 0 :
                                            heure = datetime.time(heure.hour, 0)
                                        dictColonnesMultihoraires[IDunite]["min"] = heure
                                    if dictColonnesMultihoraires[IDunite]["max"] == None or HeureStrEnTime(conso.heure_fin) > dictColonnesMultihoraires[IDunite]["max"] :
                                        dictColonnesMultihoraires[IDunite]["max"] = HeureStrEnTime(conso.heure_fin)

        return dictColonnesMultihoraires
        

    def InitGrid(self):
        # ----------------- Cr�ation des colonnes -------------------------
        nbreColonnes = 0
        for IDactivite in self.listeActivites :
            if len(self.listeActivites) > 1 and IDactivite in self.dictListeUnites :
                nbreColonnes += 1
            if IDactivite in self.dictListeUnites :
                for dictUnite in self.dictListeUnites[IDactivite] :
                    nbreColonnes += 1
        # Ajout colonne M�mo
        if AFFICHE_COLONNE_MEMO == True :
            if len(self.listeActivites) > 1 :
                nbreColonnes += 2
            else:
                nbreColonnes += 1
        # Ajout Colonne transports
        if AFFICHE_COLONNE_TRANSPORTS == True :
            nbreColonnes += 1
        self.AppendCols(nbreColonnes)
        
        # GetInfosMultihoraires
        self.dictColonnesMultihoraires = self.GetInfosColonnesMultihoraires()
        
        # Colonnes Unit�s
        numColonne = 0
        listeColonnesActivites = []
        for IDactivite in self.listeActivites :
            # Cr�ation de la colonne activit�
            if len(self.listeActivites) > 1 and IDactivite in self.dictListeUnites :
                renderer = CTRL_Grille_renderers.LabelColonneStandard("activite", COULEUR_COLONNE_ACTIVITE)
                self.SetColLabelRenderer(numColonne, renderer)
                self.SetColSize(numColonne, LARGEUR_COLONNE_ACTIVITE)
                self.SetColLabelValue(numColonne, "")
                listeColonnesActivites.append(numColonne)
                numColonne += 1
            # Cr�ation des colonnes unit�s
            if IDactivite in self.dictListeUnites:
                for dictUnite in self.dictListeUnites[IDactivite] :
                    IDunite = dictUnite["IDunite"]
                    if dictUnite["type"] == "Multihoraires" :
                        dictInfos = self.dictColonnesMultihoraires[dictUnite["IDunite"]]
                        renderer = CTRL_Grille_renderers.LabelColonneMultihoraires(heure_min=dictInfos["min"], heure_max=dictInfos["max"])
                    else :
                        renderer = CTRL_Grille_renderers.LabelColonneStandard("unite", None)
                    largeur = self.dictParametres["largeurs"]["unites"][IDunite]
                    if largeur == None :
                        if dictUnite["type"] == "Multihoraires" :
                            largeur = LARGEUR_COLONNE_MULTIHORAIRES
                        elif dictUnite["type"] == "Evenement" :
                            largeur = LARGEUR_COLONNE_EVENEMENT
                        else :
                            largeur = LARGEUR_COLONNE_UNITE
                    self.SetColLabelRenderer(numColonne, renderer)
                    labelColonne = dictUnite["abrege"]
                    self.SetColSize(numColonne, largeur)
                    self.SetColLabelValue(numColonne, labelColonne)
                    numColonne += 1
        
        # Cr�ation de la colonne M�mo
        if AFFICHE_COLONNE_MEMO == True :
            if len(self.listeActivites) > 1 :
                renderer = CTRL_Grille_renderers.LabelColonneStandard("activite", COULEUR_COLONNE_ACTIVITE)
                self.SetColLabelRenderer(numColonne, renderer)
                self.SetColLabelValue(numColonne, "")
                self.SetColSize(numColonne, LARGEUR_COLONNE_ACTIVITE)
                listeColonnesActivites.append(numColonne)
                numColonne += 1
            self.SetColLabelRenderer(numColonne, None)
            self.SetColSize(numColonne, self.dictParametres["largeurs"]["memo"])
            self.SetColLabelValue(numColonne, _(u"M�mo journalier"))
            numColonne += 1
            
        # Cr�ation de la colonne Transports
        if AFFICHE_COLONNE_TRANSPORTS == True :
            self.SetColLabelRenderer(numColonne, None)
            self.SetColSize(numColonne, LARGEUR_COLONNE_TRANSPORTS)
            self.SetColLabelValue(numColonne, _(u"Transports"))
        
        
        # ------------------ Cr�ation des lignes -----------------------------
        
        if self.mode == "individu" :
            
            # Tri des individus par nom
            listeNomsIndividus = []
            for IDindividu, dictInfos in self.dictInfosIndividus.items() :
                if IDindividu in self.listeSelectionIndividus :
                    nomIndividu = u"%s %s" % (dictInfos["nom"], dictInfos["prenom"])
                    listeNomsIndividus.append( (nomIndividu, IDindividu) )
            listeNomsIndividus.sort()
            nbreIndividusSelection = len(listeNomsIndividus)
            if nbreIndividusSelection == 0 : return
            
            # Tri des dates
            listeDatesTmp = list(self.dictOuvertures.keys())
            listeDates = []
            for dateDD in listeDatesTmp :
                listeDates.append(dateDD)
            listeDates.sort()
            nbreDates = len(listeDates)
            
            # Calcul du nombre de lignes
            if nbreIndividusSelection == 1 :
                nbreLignes = nbreDates
            else:
                nbreLignes = nbreDates * (nbreIndividusSelection+1)
            self.AppendRows(nbreLignes)
            
            # Span des colonnes Activit�s
            if nbreLignes > 0 :
                for numColonneActivite in listeColonnesActivites :
                    self.SetCellSize(0, numColonneActivite, nbreLignes, 1)
            
            # Cr�ation des lignes
            self.dictLignes = {}
            numLigne = 0
            for dateDD in listeDates :
                if nbreIndividusSelection == 1 :
                    # Individu unique
                    IDindividu = self.listeSelectionIndividus[0]
                    ligne = Ligne(self, numLigne=numLigne, IDindividu=IDindividu, date=dateDD, modeLabel="date")
                    self.dictLignes[numLigne] = ligne
                    numLigne += 1
                else :
                    # Ligne de s�paration
                    ligne = Ligne(self, numLigne=numLigne, IDindividu=None, date=dateDD, modeLabel="date", estSeparation=True)
                    self.dictLignes[numLigne] = ligne
                    numLigne += 1
                    # Multiples individus
                    for nomIndividu, IDindividu in listeNomsIndividus :
                        ligne = Ligne(self, numLigne=numLigne, IDindividu=IDindividu, date=dateDD, modeLabel="nom")
                        self.dictLignes[numLigne] = ligne
                        numLigne += 1
                        
                        
        if self.mode == "date" :
            
            listeNomsIndividus = []
            for IDindividu, dictInfos in self.dictInfosIndividus.items() :
                if FORMAT_LABEL_LIGNE.startswith("nom_prenom") : 
                    nomIndividu = u"%s %s" % (dictInfos["nom"], dictInfos["prenom"])
                if FORMAT_LABEL_LIGNE.startswith("prenom_nom") : 
                    nomIndividu = u"%s %s" % (dictInfos["prenom"], dictInfos["nom"])
                listeNomsIndividus.append( (nomIndividu, IDindividu) )
            listeNomsIndividus.sort()
            nbreLignes = len(listeNomsIndividus)
            self.AppendRows(nbreLignes)
            
            self.dictLignes = {}
            numLigne = 0
            for nomIndividu, IDindividu in listeNomsIndividus :
                ligne = Ligne(self, numLigne=numLigne, IDindividu=IDindividu, date=self.date)
                self.dictLignes[numLigne] = ligne
                numLigne += 1
            

####IMPORTATION DONNEES

    def Importation_individus(self):
        dictIndividus = {}

        if self.mode == "individu" :
            
            # -------------------------- MODE INDIVIDU --------------------------
        
            # Recherche les individus de la famille
            req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss, IDcategorie, titulaire
            FROM individus
            LEFT JOIN rattachements ON individus.IDindividu = rattachements.IDindividu
            WHERE rattachements.IDfamille = %d AND IDcategorie IN (1, 2)
            ORDER BY nom, prenom;""" % self.IDfamille
            self.DB.ExecuterReq(req)
            listeIndividus = self.DB.ResultatReq()
            for IDindividu, IDcivilite, nom, prenom, date_naiss, IDcategorie, titulaire in listeIndividus :
                civiliteAbrege = DICT_CIVILITES[IDcivilite]["civiliteAbrege"]
                if date_naiss != None :
                    date_naiss = DateEngEnDateDD(date_naiss)
                    age = UTILS_Dates.CalculeAge(datetime.date.today(), date_naiss)
                else:
                    age = None
                dictTemp = { 
                    "IDcivilite" : IDcivilite, "civiliteAbrege" : civiliteAbrege, "nom" : nom, "prenom" : prenom, 
                    "date_naiss" : date_naiss, "age" : age, "IDcategorie" : IDcategorie, "titulaire" : titulaire,
                    "inscriptions" : [],
                }
                dictIndividus[IDindividu] = dictTemp 
            
            # Recherche des inscriptions pour chaque membre de la famille
            req = """SELECT inscriptions.IDinscription, IDindividu, inscriptions.IDactivite, IDgroupe, inscriptions.IDcategorie_tarif, categories_tarifs.nom, date_desinscription
            FROM inscriptions 
            LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
            WHERE inscriptions.statut='ok' AND IDfamille = %d ;""" % self.IDfamille
            self.DB.ExecuterReq(req)
            listeInscriptions = self.DB.ResultatReq()
            for IDinscription, IDindividu, IDactivite, IDgroupe, IDcategorie_tarif, nomCategorie_tarif, date_desinscription in listeInscriptions :
                date_desinscription = UTILS_Dates.DateEngEnDateDD(date_desinscription)
                dictTemp = { 
                    "IDinscription" : IDinscription, "IDactivite" : IDactivite, "IDgroupe" : IDgroupe, 
                    "IDcategorie_tarif" : IDcategorie_tarif, "nomCategorie_tarif" : nomCategorie_tarif,
                    "date_desinscription" : date_desinscription,
                    }
                if IDindividu in dictIndividus:
                    dictIndividus[IDindividu]["inscriptions"].append(dictTemp)

        else:
            
            # -------------------------- MODE DATE --------------------------
            
            # Recherche les individus 
            req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss, IDcategorie, titulaire
            FROM individus
            LEFT JOIN rattachements ON individus.IDindividu = rattachements.IDindividu
            WHERE IDcategorie IN (1, 2)
            ORDER BY nom, prenom;"""
            self.DB.ExecuterReq(req)
            listeIndividus = self.DB.ResultatReq()
            for IDindividu, IDcivilite, nom, prenom, date_naiss, IDcategorie, titulaire in listeIndividus :
                if IDcivilite == None : IDcivilite = 1
                civiliteAbrege = DICT_CIVILITES[IDcivilite]["civiliteAbrege"]
                if date_naiss != None :
                    date_naiss = DateEngEnDateDD(date_naiss)
                    age = UTILS_Dates.CalculeAge(datetime.date.today(), date_naiss)
                else:
                    age = None
                dictTemp = { 
                    "IDcivilite" : IDcivilite, "civiliteAbrege" : civiliteAbrege, "nom" : nom, "prenom" : prenom, 
                    "date_naiss" : date_naiss, "age" : age, "IDcategorie" : IDcategorie, "titulaire" : titulaire,
                    "inscriptions" : [],
                }
                dictIndividus[IDindividu] = dictTemp 
            
            # Recherche des inscriptions
            req = """SELECT inscriptions.IDinscription, IDindividu, inscriptions.IDactivite, IDgroupe, inscriptions.IDcategorie_tarif, categories_tarifs.nom, date_desinscription
            FROM inscriptions 
            LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
            WHERE inscriptions.statut='ok';"""
            self.DB.ExecuterReq(req)
            listeInscriptions = self.DB.ResultatReq()
            for IDinscription, IDindividu, IDactivite, IDgroupe, IDcategorie_tarif, nomCategorie_tarif, date_desinscription in listeInscriptions :
                date_desinscription = UTILS_Dates.DateEngEnDateDD(date_desinscription)
                dictTemp = { 
                    "IDinscription" : IDinscription, "IDactivite" : IDactivite, "IDgroupe" : IDgroupe, 
                    "IDcategorie_tarif" : IDcategorie_tarif, "nomCategorie_tarif" : nomCategorie_tarif,
                    "date_desinscription": date_desinscription,
                    }
                if IDindividu in dictIndividus :
                    dictIndividus[IDindividu]["inscriptions"].append(dictTemp)
            
        return dictIndividus

    def GetListeVacances(self):
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        return listeDonnees

    def GetListeFeries(self):
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries 
        ; """
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        return listeDonnees

    def GetListeTouchesRaccourcis(self):
        listeTouchesRaccourcis = []
        for IDunite, dictUnite in self.dictUnites.items() :
            touche_raccourci = dictUnite["touche_raccourci"]
            if touche_raccourci != None :
                listeTouchesRaccourcis.append( (touche_raccourci, IDunite) )
        return listeTouchesRaccourcis
        
    def GetListeUnites(self, listeUnitesOuvertes=None):
        dates_extremes = self.GetDatesExtremes(self.listePeriodes)
        dictListeUnites = {}
        dictUnites = {}
        # R�cup�re la liste des unit�s
        req = """SELECT IDunite, IDactivite, nom, abrege, type, heure_debut, heure_debut_fixe, heure_fin, heure_fin_fixe, date_debut, date_fin, ordre, touche_raccourci, largeur, autogen_active, autogen_conditions, autogen_parametres
        FROM unites 
        ORDER BY ordre; """ 
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDunite, IDactivite, nom, abrege, type, heure_debut, heure_debut_fixe, heure_fin, heure_fin_fixe, date_debut, date_fin, ordre, touche_raccourci, largeur, autogen_active, autogen_conditions, autogen_parametres in listeDonnees :
            dictTemp = { "unites_incompatibles" : [], "IDunite" : IDunite, "IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "type" : type, "heure_debut" : heure_debut, "heure_debut_fixe" : heure_debut_fixe, 
            "heure_fin" : heure_fin, "heure_fin_fixe" : heure_fin_fixe, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre, "touche_raccourci" : touche_raccourci, "largeur" : largeur,
            "autogen_active" : autogen_active, "autogen_conditions" : autogen_conditions, "autogen_parametres" : autogen_parametres}

            # M�morisation des unit�s
            dictUnites[IDunite] = dictTemp

            if IDunite in listeUnitesOuvertes or MASQUER_UNITES_FERMEES == False:
                if date_fin == None or (date_debut <= str(dates_extremes[1]) and date_fin >= str(dates_extremes[0])):
                    if (IDactivite in dictListeUnites) == False :
                        dictListeUnites[IDactivite] = []
                    dictListeUnites[IDactivite].append(dictTemp)

            # M�morisation des largeurs
            if (IDunite in self.dictParametres["largeurs"]["unites"]) == False :
                if largeur == None :
                    if type == "Multihoraires" :
                        largeur = LARGEUR_COLONNE_MULTIHORAIRES
                    elif type == "Evenement" :
                        largeur = LARGEUR_COLONNE_EVENEMENT
                    else :
                        largeur = LARGEUR_COLONNE_UNITE
                self.dictParametres["largeurs"]["unites"][IDunite] = largeur            
            
        # R�cup�re les incompatibilit�s entre unit�s
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if IDunite in dictUnites : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if IDunite_incompatible in dictUnites : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)
        return dictListeUnites, dictUnites
        
    def GetDictOuvertures(self, listeActivites=[], listePeriodes=[]):
        dictOuvertures = {}
        listeUnitesOuvertes = []
        # Get Conditions
        conditions = self.GetSQLdates(listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))

        # Importation des �v�nements
        req = """SELECT IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, capacite_max, heure_debut, heure_fin, montant
        FROM evenements 
        WHERE IDactivite IN %s %s
        ORDER BY date, heure_debut;""" % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeTemp = self.DB.ResultatReq()
        dictEvenements = {}
        for IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, capacite_max, heure_debut, heure_fin, montant in listeTemp :
            date = UTILS_Dates.DateEngEnDateDD(date)
            heure_debut = UTILS_Dates.HeureStrEnTime(heure_debut)
            heure_fin = UTILS_Dates.HeureStrEnTime(heure_fin)
            dict_evenement = {"IDevenement" : IDevenement, "IDactivite" : IDactivite, "IDunite" : IDunite, "IDgroupe" : IDgroupe,
                              "date": date, "nom" : nom, "description" : description, "capacite_max" : capacite_max,
                              "heure_debut": heure_debut, "heure_fin" : heure_fin, "montant" : montant}

            key = (IDunite, IDgroupe, date)
            if (key in dictEvenements) == False:
                dictEvenements[key] = []
            dictEvenements[key].append(dict_evenement)

        # Importation des ouvertures
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite IN %s %s
        ORDER BY date; """ % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            if IDunite not in listeUnitesOuvertes :
                listeUnitesOuvertes.append(IDunite)
            date = DateEngEnDateDD(date)

            key = (IDunite, IDgroupe, date)
            if key in dictEvenements:
                liste_evenements = dictEvenements[key]
            else :
                liste_evenements = []

            dictValeurs = { "IDouverture" : IDouverture, "etat" : True, "initial" : True, "liste_evenements" : liste_evenements}
            if (date in dictOuvertures) == False :
                dictOuvertures[date] = {}
            if (IDgroupe in dictOuvertures[date]) == False :
                dictOuvertures[date][IDgroupe] = {}
            if (IDunite in dictOuvertures[date][IDgroupe]) == False :
                dictOuvertures[date][IDgroupe][IDunite] = dictValeurs
        return dictOuvertures, listeUnitesOuvertes

    def GetDictRemplissage(self, listeActivites=[], listePeriodes=[], listeIndividus=[]):
        dictRemplissage = {}
        dictUnitesRemplissage = {}
        try :
            dictConsoIndividus = self.dictConsoIndividus
        except :
            dictConsoIndividus = {}
        
        # Get Conditions
        conditions = self.GetSQLdates(listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        # R�cup�ration des unit�s de remplissage
        req = """SELECT IDunite_remplissage_unite, unites_remplissage_unites.IDunite_remplissage, IDunite
        FROM unites_remplissage_unites
        LEFT JOIN unites_remplissage ON unites_remplissage.IDunite_remplissage = unites_remplissage_unites.IDunite_remplissage
        WHERE afficher_grille_conso IS NULL OR afficher_grille_conso=1
        ;""" 
        self.DB.ExecuterReq(req)
        listeUnites = self.DB.ResultatReq()
        for IDunite_remplissage_unite, IDunite_remplissage, IDunite in listeUnites :
            if (IDunite in dictUnitesRemplissage) == False :
                dictUnitesRemplissage[IDunite] = [IDunite_remplissage,]
            else:
                dictUnitesRemplissage[IDunite].append(IDunite_remplissage)

        # R�cup�ration des unit�s de remplissage
        req = """SELECT IDunite_remplissage, IDactivite, ordre, nom, abrege, date_debut, date_fin, seuil_alerte, heure_min, heure_max, etiquettes
        FROM unites_remplissage 
        WHERE IDactivite IN %s
        AND (afficher_grille_conso IS NULL OR afficher_grille_conso=1)
        ;""" % conditionActivites
        self.DB.ExecuterReq(req)
        listeUnitesRemplissage = self.DB.ResultatReq()
        for IDunite_remplissage, IDactivite, ordre, nom, abrege, date_debut, date_fin, seuil_alerte, heure_min, heure_max, etiquettes in listeUnitesRemplissage :
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
            dictRemplissage[IDunite_remplissage] = {"IDactivite" : IDactivite,
                                                                        "ordre" : ordre,
                                                                        "nom" : nom,
                                                                        "abrege" : abrege,
                                                                        "date_debut" : DateEngEnDateDD(date_debut),
                                                                        "date_fin" : DateEngEnDateDD(date_fin),
                                                                        "seuil_alerte" : seuil_alerte,
                                                                        "heure_min" : heure_min,
                                                                        "heure_max" : heure_max,
                                                                        "etiquettes" : etiquettes,
                                                                        }
        
        # R�cup�ration des param�tres de remplissage
        req = """SELECT IDremplissage, IDactivite, IDunite_remplissage, IDgroupe, date, places
        FROM remplissage 
        WHERE IDactivite IN %s %s
        ORDER BY date;""" % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeRemplissage = self.DB.ResultatReq()
        for IDremplissage, IDactivite, IDunite_remplissage, IDgroupe, date, places in listeRemplissage :
            if places == 0 : 
                places = None
            dateDD = DateEngEnDateDD(date)
            
            dictRemplissage = UTILS_Divers.DictionnaireImbrique(dictionnaire=dictRemplissage, cles=[IDunite_remplissage, dateDD, IDgroupe], valeur=places)
                
        # R�cup�ration des consommations existantes 
        req = """SELECT IDconso, consommations.IDindividu, IDactivite, IDinscription, date, IDunite, 
        IDgroupe, heure_debut, heure_fin, consommations.etat, verrouillage, date_saisie, IDutilisateur, 
        IDcategorie_tarif, consommations.IDcompte_payeur, IDprestation, forfait, quantite, etiquettes,
        comptes_payeurs.IDfamille, IDevenement, badgeage_debut, badgeage_fin
        FROM consommations 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE IDactivite IN %s %s
        ORDER BY date; """ % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeConso = self.DB.ResultatReq()
        for IDconso, IDindividu, IDactivite, IDinscription, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, verrouillage, date_saisie, IDutilisateur, IDcategorie_tarif, IDcompte_payeur, IDprestation, forfait, quantite, etiquettes, IDfamille, IDevenement, badgeage_debut, badgeage_fin in listeConso :
            dateDD = DateEngEnDateDD(date)
            date_saisieDD = DateEngEnDateDD(date_saisie)
            etiquettes = ConvertStrToListe(etiquettes, siVide=[]) 

            # Quantit�
            if quantite == None :
                quantiteTemp = 1
            else :
                quantiteTemp = quantite
                        
            # M�morisation des conso des individus s�lectionn�s
            if IDindividu in listeIndividus or self.mode == "date" or True :
                
                conso = Conso() 
                conso.IDconso = IDconso
                conso.IDactivite = IDactivite
                conso.IDinscription = IDinscription
                conso.IDgroupe = IDgroupe
                conso.heure_debut = heure_debut
                conso.heure_fin = heure_fin
                conso.etat = etat
                conso.verrouillage = verrouillage
                conso.IDfamille = IDfamille
                conso.IDcompte_payeur = IDcompte_payeur
                conso.date_saisie = date_saisieDD
                conso.IDutilisateur = IDutilisateur
                conso.IDcategorie_tarif = IDcategorie_tarif
                conso.IDprestation = IDprestation
                conso.forfait = forfait
                conso.quantite = quantite
                conso.IDunite = IDunite
                conso.etiquettes = etiquettes
                conso.IDevenement = IDevenement
                conso.badgeage_debut = UTILS_Dates.DateEngEnDateDDT(badgeage_debut)
                conso.badgeage_fin = UTILS_Dates.DateEngEnDateDDT(badgeage_fin)
                
                dictConsoIndividus = UTILS_Divers.DictionnaireImbrique(dictionnaire=dictConsoIndividus, cles=[IDindividu, dateDD, IDunite], valeur=[])
                    
                # Recherche si la consommation n'est pas d�j� dans la liste
                consoExists = False
                for consoTemp in dictConsoIndividus[IDindividu][dateDD][IDunite] :
                    if consoTemp.IDconso == IDconso :
                        consoExists = True
                
                # Recherche si la consommation n'a pas �t� supprim�e
                for consoTemp in self.listeConsoSupprimees :
                    if consoTemp.IDconso == IDconso :
                        consoExists = True
                        
                if consoExists == False :
                    dictConsoIndividus[IDindividu][dateDD][IDunite].append(conso)
                
        return dictRemplissage, dictUnitesRemplissage, dictConsoIndividus
    
    def GetInfosIndividus(self, listeIndividus=[]):
        dictInfosIndividus = {}
        if len(listeIndividus) == 0 : return dictInfosIndividus
        # Get Conditions
        if len(listeIndividus) == 1 : condition = "(%d)" % listeIndividus[0]
        else : condition = str(tuple(listeIndividus))
        req = """SELECT IDindividu, nom, prenom, date_naiss
        FROM individus
        WHERE IDindividu IN %s;""" % condition
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDindividu, nom, prenom, date_naiss in listeDonnees :
            if date_naiss != None : date_naiss = DateEngEnDateDD(date_naiss)
            dictInfosIndividus[IDindividu] = { "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss }
        return dictInfosIndividus

    def GetInfosInscriptions(self, listeIndividus=[]):
        dictInfosInscriptions = {}
        if len(listeIndividus) == 0 : return dictInfosInscriptions
        # Get Conditions
        if len(listeIndividus) == 1 : condition = "(%d)" % listeIndividus[0]
        else : condition = str(tuple(listeIndividus))
        if self.IDfamille != None :
            req = """SELECT IDinscription, IDindividu, IDfamille, inscriptions.IDactivite, IDgroupe, inscriptions.IDcategorie_tarif, categories_tarifs.nom, date_inscription, IDcompte_payeur, date_desinscription
            FROM inscriptions
            LEFT JOIN categories_tarifs ON inscriptions.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
            WHERE inscriptions.statut='ok' AND IDindividu IN %s AND IDfamille=%d;""" % (condition, self.IDfamille)
        else:
            req = """SELECT IDinscription, IDindividu, IDfamille, inscriptions.IDactivite, IDgroupe, inscriptions.IDcategorie_tarif, categories_tarifs.nom, date_inscription, IDcompte_payeur, date_desinscription
            FROM inscriptions
            LEFT JOIN categories_tarifs ON inscriptions.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
            WHERE inscriptions.statut='ok' AND IDindividu IN %s;""" % condition
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, nom_categorie_tarif, date_inscription, IDcompte_payeur, date_desinscription in listeDonnees :
            dictInfos = { "IDinscription" : IDinscription, "IDfamille" : IDfamille, "IDgroupe" : IDgroupe, "IDcategorie_tarif" : IDcategorie_tarif, "nom_categorie_tarif" : nom_categorie_tarif, "date_inscription" : date_inscription, "IDcompte_payeur" : IDcompte_payeur, "date_desinscription" : UTILS_Dates.DateEngEnDateDD(date_desinscription)}
            if (IDindividu in dictInfosInscriptions) == False :
                dictInfosInscriptions[IDindividu] = {}
            if (IDactivite in dictInfosInscriptions[IDindividu]) == False :
                dictInfosInscriptions[IDindividu][IDactivite] = {}
            dictInfosInscriptions[IDindividu][IDactivite] = dictInfos 
        return dictInfosInscriptions

    def GetDictGroupes(self):
        dictGroupes = {}
        req = """SELECT IDgroupe, IDactivite, nom, ordre
        FROM groupes
        ORDER BY ordre;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        dictGroupes[0] = { "IDactivite" : 0, "nom" : _(u"Sans groupe"), "ordre" : 0 }
        dictTemp = {}
        # M�morise le groupe
        for IDgroupe, IDactivite, nom, ordre in listeDonnees :
            dictGroupes[IDgroupe] = { "IDactivite" : IDactivite, "nom" : nom, "ordre" : ordre, "nbreGroupesActivite" : 0}
            if (IDactivite in dictTemp) == False :
                dictTemp[IDactivite] = 0
            dictTemp[IDactivite] += 1
        # Pour compter le nombre de groupes par activit�
        for IDgroupe, dictTempGroupe in dictGroupes.items() :
            IDactivite = dictTempGroupe["IDactivite"]
            if IDactivite in dictTemp :
                dictGroupes[IDgroupe]["nbreGroupesActivite"] = dictTemp[IDactivite]
        return dictGroupes

    def GetDictEtiquettes(self):
        dictEtiquettes = {}
        req = """SELECT IDetiquette, label, IDactivite, parent, ordre, couleur
        FROM etiquettes;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDetiquette, label, IDactivite, parent, ordre, couleur in listeDonnees :     
            couleurTemp = couleur[1:-1].split(",")
            couleur = wx.Colour(int(couleurTemp[0]), int(couleurTemp[1]), int(couleurTemp[2]))
            dictEtiquettes[IDetiquette] = {"label" : label, "IDactivite" : IDactivite, "parent" : parent, "ordre" : ordre, "couleur" : couleur}
        if len(dictEtiquettes) > 0 :
            self.afficherListeEtiquettes = True
        else :
            self.afficherListeEtiquettes = False
        return dictEtiquettes
    
    def GetDictMemoJournee(self, listeActivites=[], listePeriodes=[], listeIndividus=[]):
        try :
            dictMemos = self.dictMemos
        except :
            dictMemos = {} 
        # Get Conditions
        conditions = self.GetSQLdates(listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        # R�cup�ration des m�mos
        req = """SELECT IDmemo, IDindividu, date, texte, couleur
        FROM memo_journee; """ 
        self.DB.ExecuterReq(req)
        listeMemos = self.DB.ResultatReq()
        for IDmemo, IDindividu, date, texte, couleur in listeMemos :
            if date != None and date != "None" : date = DateEngEnDateDD(date)
            if ((IDindividu, date) in dictMemos) == False :
                dictMemos[(IDindividu, date)] = {"texte" : texte, "IDmemo" : IDmemo, "statut" : None, "couleur": couleur}
        return dictMemos
    
    def GetSQLdates(self, listePeriodes=[]):
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "(" + texteSQL[:-4] + ")"
        else:
            texteSQL = "date='3000-01-01'"
        return texteSQL

    def GetDatesExtremes(self, listePeriodes=[]):
        listeTemp = []
        for date_debut, date_fin in listePeriodes :
            listeTemp.append(date_debut)
            listeTemp.append(date_fin)
        if len(listeTemp) > 0 and listeTemp[0]:
            return min(listeTemp), max(listeTemp)
        else :
            return datetime.date(1970, 1, 1), datetime.date(1970, 1, 1)

    def GetTexteHistorique(self):
        texte = u""
        for IDindividu, date, IDunite, action in self.listeHistorique :
            nomIndividu = self.dictInfosIndividus[IDindividu]["nom"]
            prenomIndividu = self.dictInfosIndividus[IDindividu]["prenom"]
            if IDunite != None :
                nomUnite = self.dictUnites[IDunite]["nom"]
            else:
                nomUnite = u""
            if date != None :
                dateStr = DateComplete(date)
            else:
                dateStr = u""
            texte += u"%s %s : %s (%s, %s)\n" % (nomIndividu, prenomIndividu, action, nomUnite, dateStr)
        return texte


    def Importation_activites(self):
        
        # Recherche les activites disponibles
        dictActivites = {}
        req = """SELECT activites.IDactivite, activites.nom, abrege, date_debut, date_fin
        FROM activites
        ORDER BY activites.nom;"""
        self.DB.ExecuterReq(req)
        listeActivites = self.DB.ResultatReq()      
        for IDactivite, nom, abrege, date_debut, date_fin in listeActivites :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            dictTemp = { "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "tarifs" : {} }
            dictActivites[IDactivite] = dictTemp
        
        # Recherche les combinaisons d'unit�s des tarifs
        req = """SELECT combi_tarifs_unites.IDcombi_tarif_unite, combi_tarifs_unites.IDcombi_tarif, 
        combi_tarifs_unites.IDtarif, combi_tarifs_unites.IDunite, date, type, combi_tarifs.quantite_max
        FROM combi_tarifs_unites
        LEFT JOIN combi_tarifs ON combi_tarifs.IDcombi_tarif = combi_tarifs_unites.IDcombi_tarif
        WHERE type='JOURN' OR type='CREDIT';"""
        self.DB.ExecuterReq(req)
        listeUnites = self.DB.ResultatReq()
        dictCombiUnites = {}
        dictQuantiteMax = {} 
        for IDcombi_tarif_unite, IDcombi_tarif, IDtarif, IDunite, date, type, quantite_max in listeUnites :
            if (IDtarif in dictCombiUnites) == False :
                dictCombiUnites[IDtarif] = {IDcombi_tarif : [IDunite,] }
            else:
                if (IDcombi_tarif in dictCombiUnites[IDtarif]) == False :
                    dictCombiUnites[IDtarif][IDcombi_tarif] = [IDunite,]
                else:
                    dictCombiUnites[IDtarif][IDcombi_tarif].append(IDunite)
            # M�morisation des quantit�s max pour les forfaits cr�dits
            if quantite_max != None :
                if (IDcombi_tarif in dictQuantiteMax) == False :
                    dictQuantiteMax[IDcombi_tarif] = {"quantite_max" : quantite_max, "listeUnites" : [] }
                dictQuantiteMax[IDcombi_tarif]["listeUnites"].append(IDunite)
            
        # Recherche des lignes de calcul
        champsTable = ", ".join(CHAMPS_TABLE_LIGNES)
        req = """SELECT %s
        FROM tarifs_lignes
        WHERE IDmodele IS NULL
        ORDER BY num_ligne;""" % champsTable
        self.DB.ExecuterReq(req)
        listeLignes = self.DB.ResultatReq()
        dictLignesCalcul = {}
        for valeurs in listeLignes :
            dictTemp = {}
            indexValeur = 0
            for valeur in valeurs :
                if valeur == "None" : valeur = None
                dictTemp[CHAMPS_TABLE_LIGNES[indexValeur]] = valeur
                indexValeur += 1
            if (dictTemp["IDtarif"] in dictLignesCalcul) == False :
                dictLignesCalcul[dictTemp["IDtarif"]] = [dictTemp,]
            else:
                dictLignesCalcul[dictTemp["IDtarif"]].append(dictTemp)

        # Recherche les filtres de questionnaires
        req = """SELECT IDfiltre, questionnaire_filtres.IDquestion, choix, criteres, IDtarif, 
        questionnaire_categories.type, controle, questionnaire_questions.defaut
        FROM questionnaire_filtres
        LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_filtres.IDquestion
        LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
        WHERE categorie='TARIF';"""
        self.DB.ExecuterReq(req)
        listeFiltres = self.DB.ResultatReq()
        dictFiltres = {}
        for IDfiltre, IDquestion, choix, criteres, IDtarif, type, controle, defaut in listeFiltres :
            if (IDtarif in dictFiltres) == False :
                dictFiltres[IDtarif] = []
            dictFiltres[IDtarif].append({"IDfiltre":IDfiltre, "IDquestion":IDquestion, "choix":choix, "criteres":criteres, "type":type, "controle":controle, "defaut":defaut})
        
        # Recherche des tarifs pour chaque activit�
        req = """SELECT 
        IDtarif, tarifs.IDactivite, tarifs.IDnom_tarif, nom, date_debut, date_fin, 
        condition_nbre_combi, condition_periode, condition_nbre_jours, condition_conso_facturees,
        condition_dates_continues, methode, categories_tarifs, groupes, etiquettes, type, forfait_duree, forfait_beneficiaire, cotisations, caisses, jours_scolaires, jours_vacances,
        code_compta, code_produit_local, tva, date_facturation, etats, IDtype_quotient, description, label_prestation, options, IDevenement
        FROM tarifs
        LEFT JOIN noms_tarifs ON noms_tarifs.IDnom_tarif = tarifs.IDnom_tarif
        ORDER BY date_debut;"""
        self.DB.ExecuterReq(req)
        listeTarifs = self.DB.ResultatReq()      
        for IDtarif, IDactivite, IDnom_tarif, nom, date_debut, date_fin, condition_nbre_combi, condition_periode, condition_nbre_jours, condition_conso_facturees, condition_dates_continues, methode, categories_tarifs, groupes, etiquettes, type, forfait_duree, forfait_beneficiaire, cotisations, caisses, jours_scolaires, jours_vacances, code_compta, code_produit_local, tva, date_facturation, etats, IDtype_quotient, description, label_prestation, options, IDevenement in listeTarifs :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            if options == None : options=""
            listeCategoriesTarifs = ConvertStrToListe(categories_tarifs)
            listeGroupes = ConvertStrToListe(groupes)
            listeEtiquettes = ConvertStrToListe(etiquettes)
            listeCotisations = ConvertStrToListe(cotisations)
            listeCaisses = ConvertStrToListe(caisses)
            jours_scolaires = ConvertStrToListe(jours_scolaires)
            jours_vacances = ConvertStrToListe(jours_vacances)
            listeEtats = UTILS_Texte.ConvertStrToListe(etats, typeDonnee="texte")
            
            dictTemp = {
                "IDtarif" : IDtarif, "IDactivite" : IDactivite, 
                "IDnom_tarif" : IDnom_tarif, "nom_tarif" : nom, "date_debut" : date_debut, "date_fin" : date_fin, 
                "condition_nbre_combi" : condition_nbre_combi, "condition_periode" : condition_periode, 
                "condition_nbre_jours" : condition_nbre_jours, "condition_conso_facturees" : condition_conso_facturees,
                "condition_dates_continues" : condition_dates_continues, "methode" : methode, 
                "categories_tarifs" : listeCategoriesTarifs, "groupes" : listeGroupes, "etiquettes" : listeEtiquettes,
                "combinaisons_unites" : [], "nbre_max_unites_combi" : 0,
                "lignes_calcul" : [], "type":type, "forfait_duree":forfait_duree, "forfait_beneficiaire":forfait_beneficiaire, 
                "cotisations" : listeCotisations, "filtres" : [], "caisses" : listeCaisses, 
                "jours_scolaires" : jours_scolaires, "jours_vacances" : jours_vacances,
                "code_compta" : code_compta, "code_produit_local": code_produit_local, "tva" : tva, "date_facturation" : date_facturation,
                "quantitesMax" : [], "etats" : listeEtats, "IDtype_quotient" : IDtype_quotient, "description_tarif" : description,
                "label_prestation" : label_prestation, "options" : options, "IDevenement" : IDevenement,
                }
                
            # Recherche si ce tarif a des combinaisons d'unit�s
            if IDtarif in dictCombiUnites :
                listeCombinaisons = []
                nbre_max_unites_combi = 0
                for IDcombi, listeCombis in dictCombiUnites[IDtarif].items() :
                    listeCombinaisons.append(tuple(listeCombis))
                    if len(listeCombis) > nbre_max_unites_combi :
                        nbre_max_unites_combi = len(listeCombis)
                    # M�morisation des quantit�s max
                    if IDcombi in dictQuantiteMax :
                        dictTemp["quantitesMax"].append(dictQuantiteMax[IDcombi])
                dictTemp["combinaisons_unites"] = listeCombinaisons
            
            # Recherche si ce tarif a des lignes de calcul
            if IDtarif in dictLignesCalcul:
                dictTemp["lignes_calcul"] = dictLignesCalcul[IDtarif]
            
            # Recherche si ce tarif a des filtres de questionnaires :
            if IDtarif in dictFiltres:
                dictTemp["filtres"] = dictFiltres[IDtarif]
            
            # M�morisation de ce tarif
            if (IDactivite in dictActivites) == True :
                if listeCategoriesTarifs == None :
                    listeCategoriesTarifs = [None,]
                for IDcategorie_tarif in listeCategoriesTarifs :
                    if (IDcategorie_tarif in dictActivites[IDactivite]["tarifs"]) == False:
                        dictActivites[IDactivite]["tarifs"][IDcategorie_tarif] = []
                    dictActivites[IDactivite]["tarifs"][IDcategorie_tarif].append(dictTemp)
            
            # V�rifie s'il y a des forfaits au cr�dit dedans :
            if type == "CREDIT" :
                self.tarifsForfaitsCreditsPresents = True
                
        return dictActivites
    
    def Importation_prestations(self, listeComptesPayeurs=[]):
        
        # R�cup�re le dictPrestations
        for IDprestation in list(self.dictPrestations.keys()) :
            if IDprestation > 0 and IDprestation not in self.listePrestationsModifiees :
                del self.dictPrestations[IDprestation]
        
        # Recherche les activites disponibles
        conditions = self.GetSQLdates(self.listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
            
        if len(listeComptesPayeurs) == 0 : conditionComptes = "()"
        elif len(listeComptesPayeurs) == 1 : conditionComptes = "(%d)" % listeComptesPayeurs[0]
        else : conditionComptes = str(tuple(listeComptesPayeurs))
        
        if self.mode == "individu" :
            conditions = "WHERE prestations.IDcompte_payeur IN %s %s" % (conditionComptes, conditionDates)
        else:
            conditions = "WHERE %s" % self.GetSQLdates(self.listePeriodes)

        # Importation de la ventilation
        req = """SELECT ventilation.IDprestation, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        %s
        GROUP BY ventilation.IDprestation
        ;""" % conditions
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        dictVentilation = {}
        for IDprestation, montant in listeDonnees :
            dictVentilation[IDprestation] = montant

        # Importation des prestations
        req = """SELECT prestations.IDprestation, prestations.IDcompte_payeur, date, categorie, label, 
        prestations.montant_initial, prestations.montant, IDactivite, IDtarif, IDfacture, IDfamille, IDindividu, forfait, temps_facture, IDcategorie_tarif,
        forfait_date_debut, forfait_date_fin, code_compta, code_produit_local, tva
        FROM prestations
        %s;""" % conditions
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()

        for IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, IDactivite, IDtarif, IDfacture, IDfamille, IDindividu, forfait, temps_facture, IDcategorie_tarif, forfait_date_debut, forfait_date_fin, code_compta, code_produit_local, tva in listeDonnees:
            date = DateEngEnDateDD(date)
            forfait_date_debut = DateEngEnDateDD(forfait_date_debut)
            forfait_date_fin = DateEngEnDateDD(forfait_date_fin)

            if IDindividu != None and IDindividu != 0 and IDindividu in self.dictIndividus:
                nomIndividu = u"%s %s" % (self.dictIndividus[IDindividu]["nom"], self.dictIndividus[IDindividu]["prenom"])
            else:
                nomIndividu = u""

            if IDprestation in dictVentilation :
                montantVentilation = dictVentilation[IDprestation]
            else :
                montantVentilation = 0.0

            dictTemp = {
                "IDprestation": IDprestation, "IDcompte_payeur": IDcompte_payeur, "date": date, "categorie": categorie,
                "label": label, "montant_initial": montant_initial, "montant": montant, "IDactivite": IDactivite, "IDtarif": IDtarif, "IDfacture": IDfacture,
                "IDfamille": IDfamille, "IDindividu": IDindividu, "nomIndividu": nomIndividu, "forfait": forfait,
                "montantVentilation": montantVentilation, "temps_facture": temps_facture, "IDcategorie_tarif": IDcategorie_tarif,
                "forfait_date_debut": forfait_date_debut, "forfait_date_fin": forfait_date_fin, "code_compta": code_compta, "tva": tva,
                "code_produit_local": code_produit_local,
            }

            if IDprestation not in self.listePrestationsSupprimees and IDprestation not in self.listePrestationsModifiees:
                self.dictPrestations[IDprestation] = dictTemp

    def Importation_forfaits(self, listeComptesPayeurs=[]):
        if self.tarifsForfaitsCreditsPresents == False :
            return
        
        # R�cup�re le dictPrestations
        for IDprestation in list(self.dictForfaits.keys()) :
            if IDprestation > 0 and IDprestation not in self.listePrestationsModifiees :
                del self.dictForfaits[IDprestation]
        
        # Recherche les dates extr�mes affich�es
        if len(self.listePeriodes) == 0 :
            return
        date_min = None
        date_max = None
        for date1, date2 in self.listePeriodes :
            if date_min == None or date1 < date_min :
                date_min = date1
            if date_max == None or date2 > date_min :
                date_max = date2
                    
        if len(listeComptesPayeurs) == 0 : conditionComptes = "()"
        elif len(listeComptesPayeurs) == 1 : conditionComptes = "(%d)" % listeComptesPayeurs[0]
        else : conditionComptes = str(tuple(listeComptesPayeurs))
        
        if self.mode == "individu" :
            conditions = "WHERE prestations.IDcompte_payeur IN %s AND forfait_date_debut<='%s' AND forfait_date_fin>='%s' " % (conditionComptes, date_max, date_min)
        else:
            conditions = "WHERE forfait_date_debut<='%s' AND forfait_date_fin>='%s' " % (date_max, date_min)
        
        req = """SELECT prestations.IDprestation, prestations.IDcompte_payeur, date, categorie, label, 
        prestations.montant_initial, prestations.montant, IDactivite, IDtarif, IDfacture, IDfamille, IDindividu, forfait, temps_facture, IDcategorie_tarif,
        SUM(ventilation.montant), forfait_date_debut, forfait_date_fin, code_compta, code_produit_local, tva
        FROM prestations
        LEFT JOIN ventilation ON ventilation.IDprestation = prestations.IDprestation
        %s
        GROUP BY prestations.IDprestation;""" % conditions
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()     
        
        index = 0
        for IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, IDactivite, IDtarif, IDfacture, IDfamille, IDindividu, forfait, temps_facture, IDcategorie_tarif, montantVentilation, forfait_date_debut, forfait_date_fin, code_compta, code_produit_local, tva in listeDonnees :
            date = DateEngEnDateDD(date)
            forfait_date_debut = DateEngEnDateDD(forfait_date_debut)
            forfait_date_fin = DateEngEnDateDD(forfait_date_fin)
            
            # Attribution d'une couleur au forfait
            couleur = self.CreationCouleurForfait(index)
            
            # Cr�ation du dictTemp
            if IDindividu != None and IDindividu != 0 :
                nomIndividu = u"%s %s" % (self.dictIndividus[IDindividu]["nom"], self.dictIndividus[IDindividu]["prenom"])
            else:
                nomIndividu = u""
            dictTemp = {
                "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, "date" : date, "categorie" : categorie,
                "label" : label, "montant_initial" : montant_initial, "montant" : montant, "IDactivite" : IDactivite, "IDtarif" : IDtarif, "IDfacture" : IDfacture, 
                "IDfamille" : IDfamille, "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "forfait" : forfait,
                "montantVentilation" : montantVentilation, "temps_facture":temps_facture, "IDcategorie_tarif":IDcategorie_tarif,
                "forfait_date_debut":forfait_date_debut, "forfait_date_fin":forfait_date_fin, "couleur":couleur, "code_compta":code_compta, "tva":tva,
                "code_produit_local": code_produit_local, "dict_conso" : {},
                }
            
            # M�morisation dans le dict des forfaits
            if IDprestation not in self.listePrestationsSupprimees and IDprestation not in self.listePrestationsModifiees :
                self.dictForfaits[IDprestation] = dictTemp
            
            # M�morisation dans le dict des prestations
            if IDprestation not in list(self.dictPrestations.keys()) and IDprestation not in self.listePrestationsSupprimees and IDprestation not in self.listePrestationsModifiees :
                self.dictPrestations[IDprestation] = dictTemp

            index += 1

        # Importation des conso d�j� associ�es aux forfaits import�s
        listeIDprestation = list(self.dictPrestations.keys())
        if len(listeIDprestation) == 0 : conditionForfaits = "()"
        elif len(listeIDprestation) == 1 : conditionForfaits = "(%d)" % listeIDprestation[0]
        else : conditionForfaits = str(tuple(listeIDprestation))

        req = """SELECT IDconso, date, IDunite, IDprestation
        FROM consommations
        WHERE IDprestation IN %s;""" % conditionForfaits
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDconso, date, IDunite, IDprestation in listeDonnees :
            if IDprestation in self.dictForfaits :
                date = DateEngEnDateDD(date)
                if ("dict_conso" in self.dictForfaits[IDprestation]) == False:
                    self.dictForfaits[IDprestation]["dict_conso"] = {}
                if (date in self.dictForfaits[IDprestation]["dict_conso"]) == False :
                    self.dictForfaits[IDprestation]["dict_conso"][date] = []
                self.dictForfaits[IDprestation]["dict_conso"][date].append(IDunite)

        # MAJ du contr�le Forfaits
        try :
            self.GetGrandParent().panel_forfaits.MAJ(self.dictForfaits, self.listeSelectionIndividus)
        except : 
            pass


    def Importation_transports(self):
        """ Importation des transports et des transports programm�s """
        global DICT_ARRETS, DICT_LIEUX, DICT_ACTIVITES, DICT_ECOLES
        

        if len(self.listeSelectionIndividus) == 0 : conditionIndividus = "()"
        elif len(self.listeSelectionIndividus) == 1 : conditionIndividus = "(%d)" % self.listeSelectionIndividus[0]
        else : conditionIndividus = str(tuple(self.listeSelectionIndividus))
        
        dates_extremes = self.GetDatesExtremes(self.listePeriodes)

        # R�cup�re les noms de champs de la table
        listeChamps = []
        for nom, type, info in DICT_TABLES["transports"] :
            listeChamps.append(nom)
        
        def ConvertChaineEnListe(chaine=""):
            if chaine == "" :
                return []
            liste1 = chaine.split(";")
            liste2 = []
            for valeur in liste1 :
                liste2.append(int(valeur))
            return liste2
            
        # Importation des transports programm�s
        req = """SELECT %s
        FROM transports
        WHERE mode='PROG' AND IDindividu IN %s
        ORDER BY depart_heure;""" % (", ".join(listeChamps), conditionIndividus)
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()     
        for donnees in listeDonnees :
            dictTemp = {}
            index = 0
            for donnee in donnees :
                nomChamp = listeChamps[index]
                if "date" in nomChamp : donnee = DateEngEnDateDD(donnee)
                if nomChamp in ("jours_scolaires", "jours_vacances", "unites") : donnee = ConvertChaineEnListe(donnee)
                dictTemp[nomChamp] = donnee
                index += 1
            if (dictTemp["IDindividu"] in self.dict_transports_prog) == False :
                self.dict_transports_prog[dictTemp["IDindividu"]] = {}
            if self.RechercheTransportsIndividu(self.dict_transports_prog, dictTemp["IDindividu"], dictTemp["IDtransport"]) == False :
                self.dict_transports_prog[dictTemp["IDindividu"]][dictTemp["IDtransport"]] = dictTemp
        
        # Importation des transports
        req = """SELECT %s
        FROM transports
        WHERE mode='TRANSP' AND IDindividu IN %s
        AND (depart_date>='%s' AND depart_date<='%s' OR arrivee_date>='%s' AND arrivee_date<='%s')
        ORDER BY depart_date, depart_heure;""" % (", ".join(listeChamps), conditionIndividus, dates_extremes[0], dates_extremes[1], dates_extremes[0], dates_extremes[1])
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()     
        for donnees in listeDonnees :
            dictTemp = {}
            index = 0
            for donnee in donnees :
                nomChamp = listeChamps[index]
                if "date" in nomChamp : 
                    donnee = DateEngEnDateDD(donnee)
                dictTemp[nomChamp] = donnee
                index += 1
            dictTemp["etat"] = None
            
            if dictTemp["IDtransport"] not in self.listeTransportsInitiale :
                
                if (dictTemp["IDindividu"] in self.dict_transports) == False :
                    self.dict_transports[dictTemp["IDindividu"]] = {}
                if self.RechercheTransportsIndividu(self.dict_transports, dictTemp["IDindividu"], dictTemp["IDtransport"]) == False :
                    self.dict_transports[dictTemp["IDindividu"]][dictTemp["IDtransport"]] = dictTemp
                
                self.listeTransportsInitiale.append(dictTemp["IDtransport"])
            
        # Arr�ts
        req = """SELECT IDarret, nom FROM transports_arrets;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        DICT_ARRETS = {}
        for IDarret, nom in listeDonnees :
            DICT_ARRETS[IDarret] = nom
            
        # Lieux
        req = """SELECT IDlieu, nom FROM transports_lieux;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        DICT_LIEUX = {}
        for IDlieu, nom in listeDonnees :
            DICT_LIEUX[IDlieu] = nom
        
        # Activit�s
        req = """SELECT IDactivite, nom FROM activites;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        DICT_ACTIVITES = {}
        for IDactivite, nom in listeDonnees :
            DICT_ACTIVITES[IDactivite] = nom

        # Ecoles
        req = """SELECT IDecole, nom FROM ecoles;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        DICT_ECOLES = {}
        for IDecole, nom in listeDonnees :
            DICT_ECOLES[IDecole] = nom


    def Importation_deductions(self, listeComptesPayeurs=[]):
        
        # R�cup�re le dictPrestations
        for IDdeduction in list(self.dictDeductions.keys()) :
            if IDdeduction > 0 :
                del self.dictDeductions[IDdeduction]
        
        # Recherche les activites disponibles
        conditions = self.GetSQLdates(self.listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
            
        if len(listeComptesPayeurs) == 0 : conditionComptes = "()"
        elif len(listeComptesPayeurs) == 1 : conditionComptes = "(%d)" % listeComptesPayeurs[0]
        else : conditionComptes = str(tuple(listeComptesPayeurs))
        
##        req = """SELECT
##        IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide
##        FROM deductions
##        WHERE IDcompte_payeur IN %s %s
##        ;""" % (conditionComptes, conditionDates)
        # J'ai enlev� la conditionDates ci-dessous pour qu'il importe toutes les d�ductions (pour tenir compte des montants ou nbre max des aides)
        req = """SELECT
        IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide
        FROM deductions
        WHERE IDcompte_payeur IN %s
        ;""" % conditionComptes

        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()     
        
        for IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide in listeDonnees :
            date = DateEngEnDateDD(date)
            dictTemp = {
                "IDdeduction" : IDdeduction, "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur,
                "date" : date, "montant" : montant, "label" : label, "IDaide" : IDaide,
                }
                
            if IDprestation not in self.listePrestationsSupprimees :
                if (IDprestation in self.dictDeductions) == False :
                    self.dictDeductions[IDprestation] = []
                self.dictDeductions[IDprestation].append(dictTemp)


    def GetAides(self):
        """ R�cup�re les aides journali�res de la famille """
        dictAides = {}
        
        # Importation des aides
        if self.mode == "individu" :
            req = """SELECT IDaide, IDfamille, IDactivite, aides.nom, date_debut, date_fin, caisses.IDcaisse, caisses.nom, montant_max, nbre_dates_max, jours_scolaires, jours_vacances
            FROM aides
            LEFT JOIN caisses ON caisses.IDcaisse = aides.IDcaisse
            WHERE IDfamille=%d
            ORDER BY date_debut;""" % self.IDfamille
        else:
            req = """SELECT IDaide, IDfamille, IDactivite, aides.nom, date_debut, date_fin, caisses.IDcaisse, caisses.nom, montant_max, nbre_dates_max, jours_scolaires, jours_vacances
            FROM aides
            LEFT JOIN caisses ON caisses.IDcaisse = aides.IDcaisse
            ORDER BY date_debut;"""
        self.DB.ExecuterReq(req)
        listeAides = self.DB.ResultatReq()
        if len(listeAides) == 0 : 
            return dictAides
        listeIDaides = []
        for IDaide, IDfamille, IDactivite, nomAide, date_debut, date_fin, IDcaisse, nomCaisse, montant_max, nbre_dates_max, jours_scolaires, jours_vacances in listeAides :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            jours_scolaires = ConvertStrToListe(jours_scolaires)
            jours_vacances = ConvertStrToListe(jours_vacances)
            dictTemp = {
                "IDaide" : IDaide, "IDfamille" : IDfamille, "IDactivite" : IDactivite, "nomAide" : nomAide, "date_debut" : date_debut, "date_fin" : date_fin, 
                "IDcaisse" : IDcaisse, "nomCaisse" : nomCaisse, "montant_max" : montant_max, "nbre_dates_max" : nbre_dates_max, "jours_scolaires" : jours_scolaires,
                "jours_vacances" : jours_vacances, "beneficiaires" : [], "montants" : {} }
            dictAides[IDaide] = dictTemp
            listeIDaides.append(IDaide)
        
        if len(listeIDaides) == 0 : conditionAides = "()"
        elif len(listeIDaides) == 1 : conditionAides = "(%d)" % listeIDaides[0]
        else : conditionAides = str(tuple(listeIDaides))
        
        # Importation des b�n�ficiaires
        req = """SELECT IDaide_beneficiaire, IDaide, IDindividu
        FROM aides_beneficiaires
        WHERE IDaide IN %s;""" % conditionAides
        self.DB.ExecuterReq(req)
        listeBeneficiaires = self.DB.ResultatReq()
        for IDaide_beneficiaire, IDaide, IDindividu in listeBeneficiaires :
            if IDaide in dictAides :
                dictAides[IDaide]["beneficiaires"].append(IDindividu)
        
        # Importation des montants, combinaisons et unit�s de combi
        req = """SELECT 
        aides_montants.IDaide, aides_combi_unites.IDaide_combi_unite, aides_combi_unites.IDaide_combi, aides_combi_unites.IDunite,
        aides_combinaisons.IDaide_montant, aides_montants.montant
        FROM aides_combi_unites
        LEFT JOIN aides_combinaisons ON aides_combinaisons.IDaide_combi = aides_combi_unites.IDaide_combi
        LEFT JOIN aides_montants ON aides_montants.IDaide_montant = aides_combinaisons.IDaide_montant
        WHERE aides_montants.IDaide IN %s;""" % conditionAides
        self.DB.ExecuterReq(req)
        listeUnites = self.DB.ResultatReq()
        
        for IDaide, IDaide_combi_unite, IDaide_combi, IDunite, IDaide_montant, montant in listeUnites :
            if IDaide in dictAides :
                # M�morisation du montant
                if (IDaide_montant in dictAides[IDaide]["montants"]) == False :
                    dictAides[IDaide]["montants"][IDaide_montant] = {"montant":montant, "combinaisons":{}}
                # M�morisation de la combinaison
                if (IDaide_combi in dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"]) == False :
                    dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"][IDaide_combi] = []
                # M�morisation des unit�s de combinaison
                dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"][IDaide_combi].append(IDunite)
        
        return dictAides


    def GetComptesPayeurs(self):
        dictComptesPayeurs = {}
        # R�cup�re le compte_payeur des ou de la famille
        if self.mode == "individu" :
            req = """SELECT IDfamille, IDcompte_payeur
            FROM comptes_payeurs
            WHERE IDfamille=%d;""" % self.IDfamille
        else:
            req = """SELECT IDfamille, IDcompte_payeur
            FROM comptes_payeurs;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq() 
        for IDfamille, IDcompte_payeur in listeDonnees :
            dictComptesPayeurs[IDfamille] = IDcompte_payeur
        return dictComptesPayeurs
    
    def GetQuotientsFamiliaux(self):
        dictQuotientsFamiliaux = {}
        # R�cup�re le QF de la famille
        if self.mode == "individu" :
            req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient
            FROM quotients
            WHERE IDfamille=%d
            ORDER BY date_debut
            ;""" % self.IDfamille
        else:
            req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient
            FROM quotients
            ORDER BY date_debut
            ;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient in listeDonnees :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            if (IDfamille in dictQuotientsFamiliaux) == False :
                dictQuotientsFamiliaux[IDfamille] = []
            dictQuotientsFamiliaux[IDfamille].append((date_debut, date_fin, quotient, IDtype_quotient))
        return dictQuotientsFamiliaux










####CLAVIER ET SOURIS


    def OnLeftClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        self.ActiveTooltip(actif=False)
        self.SetFocus() 
        if numColonne == -1 or numLigne == -1 :
            return
        ligne = self.dictLignes[numLigne]
        if ligne.estSeparation == True :
            return
        case = ligne.dictCases[numColonne]
        if case.typeCase in ("date", "activite") :
            return 
        
        # Si case multihoraires
        if case.GetTypeUnite() == "Multihoraires" :
            barre = case.RechercheBarre(x, y, readOnlyInclus=False)
            if barre != None :
                barre, region, x, y, ecart = barre
                # Recherche si des touches raccourcis sont enfonc�es
                if wx.GetKeyState(97) or wx.GetKeyState(112) or wx.GetKeyState(105) or wx.GetKeyState(106) or wx.GetKeyState(99) or wx.GetKeyState(115) :
                    case.ToucheRaccourci(barre)
                else :
                    # Protections anti modification et suppression
                    if case.ProtectionsModifSuppr(barre.conso) == False :
                        return
                    # Sinon d�clenche le moving de la barre
                    self.barreMoving = {"barre" : barre, "region" : region, "x" : x, "y" : y, "ecart" : ecart, "heure_debut" : barre.heure_debut, "heure_fin" : barre.heure_fin}
                    self.SetCurseur(region)

        # Si case standard
        else :
            case.OnClick()

            # M�morise la case enfonc�e
            if self.casesSurvolees == None:
                self.casesSurvolees = [case,]

        try :
            wx.CallAfter(self.ClearSelection)
        except :
            pass



    def OnLeftDoubleClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        self.ActiveTooltip(actif=False)
        if numColonne == -1 or numLigne == -1 :
            return
        ligne = self.dictLignes[numLigne]
        if ligne.estSeparation == True :
            return
        case = ligne.dictCases[numColonne]
        if case.GetTypeUnite() == "Multihoraires" and case.ouvert :
            barre = case.RechercheBarre(x, y, readOnlyInclus=False)
            if barre == None :
                case.AjouterBarre(position=(x, y))
            else :
                barre, region, x, y, ecart = barre
                case.ModifierBarre(barre)
        
        if case.GetTypeUnite() == "memo" :
            case.OnDoubleClick() 
        
        
    def OnCellRightClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        self.ActiveTooltip(actif=False)
        ligne = self.dictLignes[numLigne]
        if ligne.estSeparation == True :
            return
        case = ligne.dictCases[numColonne]
        case.OnContextMenu()
        event.Skip()

    def OnLabelRightClick(self, event):
        # Annule moving barre
        self.barreMoving = None
        self.SetCurseur(None)
        # Context Menu
        numLigne = event.GetRow()
        if numLigne == -1 : return
        ligne = self.dictLignes[numLigne]
        ligne.OnContextMenu()
        event.Skip()

    def OnLabelLeftClick(self, event):
        # Annule moving barre
        self.barreMoving = None
        self.SetCurseur(None)
        # Context Menu
        numLigne = event.GetRow()
        if numLigne == -1 : return
        ligne = self.dictLignes[numLigne]
        ligne.OnLeftClick()
        event.Skip()

    def OnModificationMemo(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        ligne = self.dictLignes[numLigne]
        case = ligne.dictCases[numColonne]
        if case.typeCase == "memo" :
            case.MemoriseValeurs()
        event.Skip() 
        
    def OnMouseOver(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        case = None
        if numLigne != -1 and numColonne != -1 : 
            if numLigne in self.dictLignes :
                ligne = self.dictLignes[numLigne]
                if numColonne in ligne.dictCases :
                    case = ligne.dictCases[numColonne]

        # Click gauche souris enfonc�
        if self.casesSurvolees != None and case != None:
            if case not in self.casesSurvolees and case.GetTypeUnite() in ("Unitaire", "Horaire", "Quantite"):
                self.casesSurvolees.append(case)
                if wx.GetMouseState().LeftIsDown():
                    self.OnLeftClick(event)

        # Recherche si c'est une case �v�nementielle : si oui, consid�re l'�v�nement au lieu de la case
        if case != None and hasattr(case, "CategorieCase") and case.CategorieCase == "evenement":
            case = case.RechercheEvenement(x, y)

        # Dragging barre
        if self.barreMoving != None :
            barre = self.barreMoving["barre"]
            rectCase = barre.case.GetRect()
            if x >= rectCase.x and x <= rectCase.x + rectCase.width :
                
                if self.barreMoving["region"] == "gauche" : 
                    heure_debut = barre.case.PosEnHeure(x - self.barreMoving["ecart"], arrondir=True)
                    heure_fin = barre.heure_fin
                    if heure_debut < barre.case.heure_min or heure_debut >= barre.heure_fin :
                        heure_debut = barre.heure_debut
                        
                if self.barreMoving["region"] == "droite" : 
                    heure_debut = barre.heure_debut
                    heure_fin = barre.case.PosEnHeure(x + self.barreMoving["ecart"], arrondir=True)
                    if heure_fin > barre.case.heure_max or heure_fin <= barre.heure_debut :
                        heure_fin = barre.heure_fin
                        
                if self.barreMoving["region"] == "milieu" : 
                    heure_debut = barre.case.PosEnHeure(x - self.barreMoving["ecart"], arrondir=True)
                    heure_fin = DeltaEnTime(UTILS_Dates.AdditionHeures(heure_debut, UTILS_Dates.SoustractionHeures(self.barreMoving["heure_fin"], self.barreMoving["heure_debut"])))
                    if (heure_debut < heure_fin) and (heure_debut < barre.case.heure_min or heure_fin > barre.case.heure_max) :
                        heure_debut = barre.heure_debut
                        heure_fin = barre.heure_fin
                        
                if barre.case.ContraintesCalque(barre, heure_debut, heure_fin) == True :
                    heure_debut = barre.heure_debut
                    heure_fin = barre.heure_fin

                barre.SetHeures(heure_debut=heure_debut, heure_fin=heure_fin)
                barre.Refresh()
            

        # Actions standards
        else :
            if case != None :
                if case != self.caseSurvolee :
                    self.ActiveTooltip(actif=False)
                    # Attribue une info-bulle
                    self.ActiveTooltip(actif=True, case=case)
                    self.caseSurvolee = case
            else:
                self.caseSurvolee = None
                self.ActiveTooltip(actif=False)

        # StatusBar
        self.EcritStatusbar(case, x, y)
        

    def OnLeftUp(self, event):
        if self.barreMoving !=None :
            barre = self.barreMoving["barre"]
            barre.MAJ_facturation() 
            barre.case.MAJremplissage()
            barre.case.Refresh()
            # Autog�n�ration
            self.Autogeneration(ligne=barre.case.ligne, IDactivite=barre.case.IDactivite, IDunite=barre.case.IDunite)

        self.barreMoving = None
        self.casesSurvolees = None
        self.SetCurseur(None)
        
    def OnLeaveWindow(self, event):
        # Annule Tooltip
        self.ActiveTooltip(False) 
        # Annule moving barre
        self.barreMoving = None
        self.SetCurseur(None)
        # StatusBar
        self.EcritStatusbar(None)

    def SetCurseur(self, region=None):
        """ Change la forme du curseur lors d'un dragging """
        if 'phoenix' in wx.PlatformInfo:
            cursor = wx.Cursor
        else :
            cursor = wx.StockCursor
        if region == "gauche" or region == "droite" :
            self.SetCursor(cursor(wx.CURSOR_SIZEWE))
        elif region == "milieu":
            self.SetCursor(cursor(wx.CURSOR_SIZING))
        else :
            self.SetCursor(cursor(wx.CURSOR_ARROW))




####TOOLTIP

    def AfficheTooltip(self):
        """ Cr�ation du supertooltip """
        case = self.tip.case
        
        # R�cup�ration des donn�es du tooltip
        dictDonnees = case.GetTexteInfobulle()
        if dictDonnees == None or type(dictDonnees) != dict :
            self.ActiveTooltip(actif=False)
            return
        
        # Param�trage du tooltip
        font = self.GetFont()
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        if "couleur" in dictDonnees :
            couleur = dictDonnees["couleur"]
            self.tip.SetTopGradientColour(couleur)
            self.tip.SetMiddleGradientColour(wx.Colour(255,255,255))
            self.tip.SetBottomGradientColour(wx.Colour(255,255,255))
            self.tip.SetTextColor(wx.Colour(76,76,76))
        else :
            styleTooltip = "Office 2007 Blue"
            self.tip.ApplyStyle(styleTooltip)
            
        # Titre du tooltip
        bmp = None
        if "bmp" in dictDonnees :
            bmp = dictDonnees["bmp"]
        self.tip.SetHeaderBitmap(bmp)
        
        titre = None
        if "titre" in dictDonnees :
            titre = dictDonnees["titre"]
            self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
            self.tip.SetHeader(titre)
            self.tip.SetDrawHeaderLine(True)

        # Corps du message
        texte = dictDonnees["texte"]
        self.tip.SetMessage(texte)

        # Pied du tooltip
        pied = None
        if "pied" in dictDonnees :
            pied = dictDonnees["pied"]
        self.tip.SetDrawFooterLine(True)
        self.tip.SetFooterBitmap(wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
        self.tip.SetFooterFont(wx.Font(7, font.GetFamily(), font.GetStyle(), wx.LIGHT, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetFooter(pied)

        # Affichage du Frame tooltip
        self.tipFrame = STT.ToolTipWindow(self, self.tip)
        self.tipFrame.CalculateBestSize()
        x, y = wx.GetMousePosition()
        self.tipFrame.SetPosition((x+15, y+17))
        self.tipFrame.DropShadow(True)
        self.tipFrame.Show()
        #self.tipFrame.StartAlpha(True) # ou .Show() pour un affichage imm�diat
        
        # Arr�t du timer
        self.timerTip.Stop()
        del self.timerTip

    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try :
                self.tipFrame.Destroy()
                del self.tipFrame
            except :
                pass

    def ActiveTooltip(self, actif=True, case=None):
        if actif == True :
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False :
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(1500)
                self.tip.case = case
        else:
            # D�sactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.case = None
            self.CacheTooltip() 
            self.caseSurvolee = None






####FACTURATION

    def GetEvenementsUnites(self, liste_unites=[], date=None, dictTarif=None, IDindividu=None):
        liste_evenements = []
        for numLigne, ligne in self.dictLignes.items() :
            if ligne.IDindividu == IDindividu :
                for numColonne, case in ligne.dictCases.items() :
                    if hasattr(case, "CategorieCase") and case.CategorieCase == "evenement" and case.IDunite in liste_unites and case.date == date :
                        # return case.liste_evenements
                        for evenement in case.liste_evenements :
                            if dictTarif["type"] == "JOURN":
                                if evenement.conso != None and evenement.conso.etat in dictTarif["etats"] :
                                    liste_evenements.append(evenement)
        return liste_evenements

    def GetIDfacture(self, conso=None):
        IDfacture = None
        if conso.IDprestation in self.dictPrestations :
            IDfacture = self.dictPrestations[conso.IDprestation]["IDfacture"]
        return IDfacture

    def Facturation(self, IDactivite, IDindividu, IDfamille, date, IDcategorie_tarif, numIndividu=None, IDgroupe=None, case=None, modeSilencieux=False, etiquettes=[], action="saisie"):
        # 1 - Recherche les unit�s de la ligne
        try :
            dictUnites = self.dictConsoIndividus[IDindividu][date]
        except :
            return

        dictUnitesUtilisees = {}
        dictQuantites = {}
        for IDunite, listeConso in dictUnites.items() :
            for conso in listeConso :
                if conso.IDactivite == IDactivite and conso.forfait == None : # and dictUnitesUtilisees.has_key(IDunite) == False  # and conso.etat in ("reservation", "present", "absenti")
                    if (IDunite in dictUnitesUtilisees) == False or dictUnitesUtilisees[IDunite] in (None, "attente", "refus"):#== None :
                        dictUnitesUtilisees[IDunite] = conso.etat

                    dictQuantites[IDunite] = conso.quantite

        # 2 - Recherche un tarif valable � cette date
        if (IDactivite in self.dictActivites) == False : return None
        if (IDcategorie_tarif in self.dictActivites[IDactivite]["tarifs"]) == False : return None
        
        listeTarifsValides1 = []
        for dictTarif in self.dictActivites[IDactivite]["tarifs"][IDcategorie_tarif] :
            if self.RechercheTarifValide(dictTarif, IDgroupe, date, IDindividu, IDfamille, etiquettes) == True :
                listeTarifsValides1.append(dictTarif)
        
        # 3 - On recherche si des combinaisons sont pr�sentes sur cette ligne
        listeTarifsValides2 = []
        for dictTarif in listeTarifsValides1 :
            dictTarif = copy.deepcopy(dictTarif)
            combinaisons_unites = dictTarif["combinaisons_unites"]
            for combinaison in combinaisons_unites :
                resultat = self.RechercheCombinaisonDict(dictUnitesUtilisees, combinaison, dictTarif)
                if resultat == True :
                    if len(combinaison) > dictTarif["nbre_max_unites_combi"] : # Ceci est une ligne rajout�e pour le souci des 3 unites de conso non d�tect�es
                        dictTarif["nbre_max_unites_combi"] = len(combinaison)
                        dictTarif["combi_retenue"] = combinaison
                        listeTarifsValides2.append(dictTarif)

        # 4 - Tri des tarifs par date de d�but
        if six.PY2:
            listeTarifsValides2.sort(cmp=self.TriTarifs2)
        else:
            listeTarifsValides2.sort(key=functools.cmp_to_key(self.TriTarifs2))
        # Tri des tarifs par nombre d'unit�s
        if six.PY2:
            listeTarifsValides2.sort(cmp=self.TriTarifs)
        else :
            listeTarifsValides2.sort(key=functools.cmp_to_key(self.TriTarifs))


        #-----------------------------------------------------------
        # Si forfaits au cr�dits pr�sents dans les tarifs
        nbreTarifsForfait = 0
        for dictTarif in listeTarifsValides2 :
            if dictTarif["type"] == "CREDIT" :
                nbreTarifsForfait += 1

        if nbreTarifsForfait > 0 :
            listeTarifsValides3 = []
            for dictTarif in listeTarifsValides2 :
                if dictTarif["type"] == "CREDIT" :
                    # tarif cr�dit
                    IDprestationForfait, dictTarifForfait = self.RechercheForfaitCredit(IDtarif=dictTarif["IDtarif"], date=date, IDfamille=IDfamille, IDindividu=IDindividu)

                    # V�rification des quantit�s max
                    if len(dictTarif["quantitesMax"]) > 0 :

                        combiRetenue = list(dictTarif["combi_retenue"])
                        combiRetenue.sort()
                        quantite_max = None
                        for dictQuantitesMax in dictTarif["quantitesMax"] :
                            quantite_max_temp = dictQuantitesMax["quantite_max"]
                            combiUnite = dictQuantitesMax["listeUnites"]
                            combiUnite.sort()
                            if combiUnite == combiRetenue :
                                quantite_max = quantite_max_temp

                        if quantite_max != None :

                            # Recherche la quantit� de conso dans la grille affich�e
                            nbre = 0
                            liste_dates = []
                            for dateTemp, dictUnitesTemp in self.dictConsoIndividus[IDindividu].items():
                                listeUnitesTemp = []
                                if dateTemp not in liste_dates :
                                    liste_dates.append(dateTemp)
                                for IDuniteTemp, listeConso in dictUnitesTemp.items():
                                    for conso in listeConso:
                                        if conso.IDprestation == IDprestationForfait and conso.etat in ("reservation", "present", "absenti") :
                                            listeUnitesTemp.append(conso.IDunite)
                                if self.RechercheCombinaisonTuple(listeUnitesTemp, combiRetenue) == True:
                                    nbre += 1

                            # Recherche la quantit� de conso d�j� enregistr�e dans la DB
                            if IDprestationForfait in self.dictForfaits :
                                if "dict_conso" in self.dictForfaits[IDprestationForfait] :
                                    for dateTemp, listeUnitesTemp in self.dictForfaits[IDprestationForfait]["dict_conso"].items() :
                                        if dateTemp not in liste_dates:
                                            if self.RechercheCombinaisonTuple(listeUnitesTemp, combiRetenue) == True:
                                                nbre += 1


                            # Si max conso atteint
                            if case.CategorieCase == "standard":
                                IDprestationTemp = case.IDprestation
                            elif case.CategorieCase == "multihoraires":
                                barre = conso.barre
                                IDprestationTemp = barre.conso.IDprestation
                            elif case.CategorieCase == "evenement":
                                evenement = conso.evenement
                                IDprestationTemp = evenement.conso.IDprestation

                            if IDprestationTemp != IDprestationForfait and case.IDunite in combiRetenue and nbre + 1 > quantite_max :
                                IDprestationForfait = None
                                #print "PLAFOND ATTEINT !"

                                if "blocage_plafond" in dictTarif["options"] :
                                    # Blocage de la saisie
                                    case.Supprimer()
                                    if modeSilencieux == False :
                                        dlg = wx.MessageDialog(self, _(u"Il n'y a plus de cr�dit disponible dans le forfait !"), _(u"Cr�dit �puis�"), wx.OK | wx.ICON_EXCLAMATION)
                                        dlg.ShowModal()
                                        dlg.Destroy()
                                        return



                    if IDprestationForfait != None :
                        dictTarif["CREDIT"] = IDprestationForfait
                        listeTarifsValides3.append(dictTarif)
                else :
                    # Tarif normal
                    listeTarifsValides3.append(dictTarif)
            # Met les forfaits cr�dit en premier
            if six.PY2:
                listeTarifsValides3.sort(cmp=self.TriTarifs3)
            else:
                listeTarifsValides3.sort(key=functools.cmp_to_key(self.TriTarifs3))

            listeTarifsValides2 = listeTarifsValides3
        #-----------------------------------------------------------

        # 5 - On conserve les tarifs qui ont plus grand nombre d'unit�s dans la combi
        listeTarifsRetenus = []
        listeIDunitesTraitees = []
        for dictTarif in listeTarifsValides2 :
            combinaisons_unites = dictTarif["combi_retenue"]
            # Recherche des unit�s non trait�es
            valide = True
            for IDunite in combinaisons_unites :
                if IDunite in listeIDunitesTraitees :
                    valide = False
            # Si le tarif est finalement retenu
            if valide == True :
                listeTarifsRetenus.append(dictTarif)
                for IDunite in combinaisons_unites :
                    listeIDunitesTraitees.append(IDunite)

        # 6 - On calcule les tarifs des prestations
        dictUnitesPrestations = {}     
        listeNouvellesPrestations = []   
        for dictTarif in listeTarifsRetenus :
            IDtarif = dictTarif["IDtarif"]
            combinaisons_unites = dictTarif["combi_retenue"]

            # Recherche des �v�nements dans une des cases de la combinaison
            liste_evenements = [None,]
            if "evenement" in dictTarif["methode"] :

                # Recherche les �v�nements pour lesquels une conso est saisie
                liste_evenements = []
                for evenement in self.GetEvenementsUnites(combinaisons_unites, date, dictTarif, IDindividu):
                    if evenement.conso != None :
                        liste_evenements.append(evenement)

            # M�morise le tarif initial pour les �v�nements
            mem_dictTarif = copy.copy(dictTarif)
            for evenement in liste_evenements :
                # Recherche un tarif sp�cial �v�nement
                if evenement != None and IDactivite in self.dictActivites and IDcategorie_tarif in self.dictActivites[IDactivite]["tarifs"]:
                    dictTarif = copy.copy(mem_dictTarif)
                    for dictTarifEvent in self.dictActivites[IDactivite]["tarifs"][IDcategorie_tarif] :
                        if dictTarifEvent["IDevenement"] == evenement.IDevenement and self.RechercheTarifValide(dictTarifEvent, IDgroupe, date, IDindividu, IDfamille, etiquettes) == True:
                            dictTarif = dictTarifEvent
                            dictTarif["nom_tarif"] = evenement.nom

                # Forfait cr�dit
                if "CREDIT" in dictTarif:
                    forfait_credit = dictTarif["CREDIT"]
                else:
                    forfait_credit = False

                # Recherche du temps factur� par d�faut
                liste_temps = []
                for IDunite in combinaisons_unites :
                    if IDunite in dictUnites :
                        for conso in dictUnites[IDunite] :
                            heure_debut = conso.heure_debut
                            heure_fin = conso.heure_fin
                            if heure_debut not in (None, "") and heure_fin not in (None, "")  :
                                liste_temps.append((heure_debut, heure_fin))
                if len(liste_temps) > 0 :
                    temps_facture = Additionne_intervalles_temps(liste_temps)
                else :
                    temps_facture = None

                # Recherche de la quantit�
                quantite = 0
                for IDunite in combinaisons_unites :
                    if IDunite in dictQuantites :
                        if dictQuantites[IDunite] != None :
                            quantite += dictQuantites[IDunite]
                if quantite == 0 :
                    quantite = None

                # Calcul du tarif
                resultat = self.CalculeTarif(dictTarif, combinaisons_unites, date, temps_facture, IDfamille, IDindividu, quantite, case, modeSilencieux, evenement, action)
                if resultat == False :
                    return False
                elif resultat == "break" :
                    break
                else :
                    montant_tarif, nom_tarif, temps_facture = resultat


                # -------------------------------------------------------------------------
                # ------------ D�duction d'une aide journali�re --------------------
                # -------------------------------------------------------------------------

                # Recherche si une aide est valable � cette date et pour cet individu et pour cette activit�
                listeAidesRetenues = []
                for IDaide, dictAide in self.dictAides.items() :
                    IDfamilleTemp = dictAide["IDfamille"]
                    listeBeneficiaires = dictAide["beneficiaires"]
                    IDactiviteTemp = dictAide["IDactivite"]
                    dateDebutTemp = dictAide["date_debut"]
                    dateFinTemp = dictAide["date_fin"]

                    # V�rifie si date est dans jours scolaires ou de vacances
                    date_ok = True
                    if dictAide["jours_scolaires"] != None and dictAide["jours_scolaires"] != None :
                        date_ok = self.VerificationPeriodes(dictAide["jours_scolaires"], dictAide["jours_vacances"], date)

                    if date_ok == True and IDfamille == IDfamilleTemp and date >= dateDebutTemp and date <= dateFinTemp and IDindividu in listeBeneficiaires and IDactiviteTemp == IDactivite :
                        # Une aide valide a �t� trouv�e...
                        listeCombiValides = []

                        # On recherche si des combinaisons sont pr�sentes sur cette ligne
                        dictMontants = dictAide["montants"]
                        for IDaide_montant, dictMontant in dictMontants.items() :
                            montant = dictMontant["montant"]
                            for IDaide_combi, combinaison in dictMontant["combinaisons"].items() :
                                resultat = self.RechercheCombinaisonTuple(combinaisons_unites, combinaison)

                                # Regarde si la combinaison est bonne
                                combiAideTemp = combinaison
                                combiAideTemp.sort()
                                combiActuelleTemp = list(combinaisons_unites)
                                combiActuelleTemp.sort()
                                if combiAideTemp != combiActuelleTemp :
                                    resultat = False

                                if resultat == True :
                                    dictTmp = {
                                        "nbre_max_unites_combi": len(combinaison),
                                        "combi_retenue" : combinaison,
                                        "montant" : montant,
                                        "IDaide" : IDaide,
                                        }
                                    listeCombiValides.append(dictTmp)

                        # Tri des combinaisons par nombre d'unit�s max dans les combinaisons
                        if six.PY2:
                            listeCombiValides.sort(cmp=self.TriTarifs)
                        else:
                            listeCombiValides.sort(key=functools.cmp_to_key(self.TriTarifs))

                        # On conserve le combi qui a le plus grand nombre d'unit�s dedans
                        aideRetenue = None
                        if len(listeCombiValides) > 0 :
                            aideRetenue = listeCombiValides[0]

                        # V�rifie que le montant max ou le nbre de dates max n'est pas d�j� atteint avant application
                        listeDatesAide = []
                        montantMaxAide = 0.0
                        if aideRetenue != None :
                            for IDprestaTemp, listeDeductionsTemp in self.dictDeductions.items() :
                                for dictDeductionTemp in listeDeductionsTemp :
                                    if IDprestaTemp not in self.listePrestationsSupprimees and dictDeductionTemp["IDaide"] == IDaide :
                                        if dictDeductionTemp["date"] not in listeDatesAide :
                                            listeDatesAide.append(dictDeductionTemp["date"])
                                        montantMaxAide += dictDeductionTemp["montant"]

                        if aideRetenue != None and dictAide["nbre_dates_max"] != None :
                            if len(listeDatesAide) >= dictAide["nbre_dates_max"] :
                                aideRetenue = None

                        if aideRetenue != None and dictAide["montant_max"] != None :
                            if (montantMaxAide + aideRetenue["montant"]) > dictAide["montant_max"] :
                                aideRetenue = None

                        # M�morisation de l'aide retenue
                        if aideRetenue != None and montant_tarif > 0:
                            listeAidesRetenues.append(aideRetenue)


                if forfait_credit == False :
                    # Application de la d�duction
                    montant_initial = montant_tarif
                    montant_final = montant_initial
                    for aideRetenue in listeAidesRetenues :
                        montant_final = montant_final - aideRetenue["montant"]

                    # Formatage du temps factur�
                    if temps_facture != None :
                        temps_facture = time.strftime("%H:%M", time.gmtime(temps_facture.seconds))

                    # -------------------------M�morisation de la prestation ---------------------------------------------
                    IDcompte_payeur = self.dictComptesPayeurs[IDfamille]
                    IDprestation = self.MemorisePrestation(IDcompte_payeur, date, IDactivite, IDtarif, nom_tarif, montant_initial, montant_final, IDfamille, IDindividu, listeDeductions=listeAidesRetenues, temps_facture=temps_facture, IDcategorie_tarif=IDcategorie_tarif, dictTarif=dictTarif, evenement=evenement)
                    if IDprestation < 0 :
                        listeNouvellesPrestations.append(IDprestation)

                else :
                    IDprestation = forfait_credit

                # Attribue � chaque unit� un IDprestation
                for IDunite in combinaisons_unites :
                    if evenement != None :
                        IDevenement = evenement.IDevenement
                    else :
                        IDevenement = None
                    dictUnitesPrestations[(IDunite, IDevenement)] = IDprestation

        # 7 - Parcours de toutes les unit�s de la date pour modifier le IDprestation
        listeAnciennesPrestations = []
        for IDunite, listeConso in self.dictConsoIndividus[IDindividu][date].items() :
            for conso in listeConso :
                if conso.IDactivite == IDactivite and conso.forfait == None :
                    case = conso.case

                    # Retrouve le IDprestation
                    if (IDunite, conso.IDevenement) in list(dictUnitesPrestations.keys()) :
                        IDprestation = dictUnitesPrestations[(IDunite, conso.IDevenement)]

                    elif (IDunite, None) in list(dictUnitesPrestations.keys()) :
                        IDprestation = dictUnitesPrestations[(IDunite, None)]
                    else:
                        IDprestation = None

                    # Supprime si n�cessaire l'ancienne prestation
                    valeur = (conso.IDprestation, "consommation")
                    if (IDprestation == None or IDprestation < 0) or IDprestation in list(self.dictForfaits.keys()) :
                        if conso.IDprestation != None and valeur not in listeAnciennesPrestations and conso.IDprestation not in list(self.dictForfaits.keys()) :
                            listeAnciennesPrestations.append(valeur)

                    if case != None :
                        if case.CategorieCase == "standard" :
                            case.IDprestation = IDprestation
                            case.MemoriseValeurs()
                        elif case.CategorieCase == "multihoraires" :
                            barre = conso.barre
                            barre.conso.IDprestation = IDprestation
                            barre.MemoriseValeurs()
                        elif case.CategorieCase == "evenement":
                            evenement = conso.evenement
                            evenement.conso.IDprestation = IDprestation
                            evenement.MemoriseValeurs()
                        else :
                            pass

        # 7A - V�rifie que la prestation supprim�e n'est pas un tarif SELON NBRE INDIVIDUS FAMILLE
        for IDprestationAncienne, categorie in listeAnciennesPrestations :
            if IDprestationAncienne in self.dictPrestations:
                IDtarifPrestationSupprimee = self.dictPrestations[IDprestationAncienne]["IDtarif"]

                # Recherche le tarif de la prestation supprim�e
                for IDactiviteTmp, dictActiviteTmp in self.dictActivites.items() :
                    for IDnom_tarifTmp, listeTarifsTmp in dictActiviteTmp["tarifs"].items() :
                        for dictTarif in listeTarifsTmp :
                            IDtarifTmp = dictTarif["IDtarif"]
                            
                            if IDtarifTmp == IDtarifPrestationSupprimee :
                                methode_calcul = dictTarif["methode"]
                                lignes_calcul = dictTarif["lignes_calcul"]
                                
                                # Si c'est un tarif selon nbre individus...
                                if "nbre_ind" in methode_calcul :
                                    if "montant_unique" in methode_calcul :
                                        # Montant unique
                                        montant_enfant_1 = lignes_calcul[0]["montant_enfant_1"]
                                        montant_enfant_2 = lignes_calcul[0]["montant_enfant_2"]
                                        montant_enfant_3 = lignes_calcul[0]["montant_enfant_3"]
                                        montant_enfant_4 = lignes_calcul[0]["montant_enfant_4"]
                                        montant_enfant_5 = lignes_calcul[0]["montant_enfant_5"]
                                        montant_enfant_6 = lignes_calcul[0]["montant_enfant_6"]
                                    else:
                                        # Selon QF
                                        tarifFound = False
                                        for ligneCalcul in lignes_calcul :
                                            qf_min = ligneCalcul["qf_min"]
                                            qf_max = ligneCalcul["qf_max"]
                                            montant_enfant_1 = ligneCalcul["montant_enfant_1"]
                                            montant_enfant_2 = ligneCalcul["montant_enfant_2"]
                                            montant_enfant_3 = ligneCalcul["montant_enfant_3"]
                                            montant_enfant_4 = ligneCalcul["montant_enfant_4"]
                                            montant_enfant_5 = ligneCalcul["montant_enfant_5"]
                                            montant_enfant_6 = ligneCalcul["montant_enfant_6"]

                                            QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                                            if QFfamille != None :
                                                if QFfamille >= qf_min and QFfamille <= qf_max :
                                                    break

                                            # if self.dictQuotientsFamiliaux.has_key(IDfamille) :
                                            #     listeQuotientsFamiliaux = self.dictQuotientsFamiliaux[IDfamille]
                                            # else:
                                            #     listeQuotientsFamiliaux = []
                                            # for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                                            #     if date >= date_debut and date <= date_fin and quotient >= qf_min and quotient <= qf_max :
                                            #         tarifFound = True
                                            #     if tarifFound == True :
                                            #         break
                                            # if tarifFound == True :
                                            #     break

                                    # Recherche combien d'individus de la famille sont d�j� pr�sents ce jour-l�
                                    listeIndividusPresents = []
                                    listePrestationsConcernees = []
                                    for IDprestation, dictValeurs in self.dictPrestations.items() :
                                        if IDprestation != IDtarifPrestationSupprimee and dictValeurs["date"] == date and dictValeurs["IDfamille"] == IDfamille and dictValeurs["IDtarif"] == IDtarifTmp and dictValeurs["IDindividu"] != IDindividu :
                                            if dictValeurs["IDindividu"] not in listeIndividusPresents :
                                                listeIndividusPresents.append(dictValeurs["IDindividu"])
                                    nbreIndividus = len(listeIndividusPresents)
                                    
                                    # Recherche le tarif � appliquer � chaque individu
                                    if "degr" in methode_calcul :
                                        # Si tarif d�gressif diff�rent pour chaque individu
                                        tarifsDegr = []
                                        if montant_enfant_1 != None and montant_enfant_1 != 0.0 : tarifsDegr.append(montant_enfant_1)
                                        if montant_enfant_2 != None and montant_enfant_2 != 0.0 : tarifsDegr.append(montant_enfant_2)
                                        if montant_enfant_3 != None and montant_enfant_3 != 0.0 : tarifsDegr.append(montant_enfant_3)
                                        if montant_enfant_4 != None and montant_enfant_4 != 0.0 : tarifsDegr.append(montant_enfant_4)
                                        if montant_enfant_5 != None and montant_enfant_5 != 0.0 : tarifsDegr.append(montant_enfant_5)
                                        if montant_enfant_6 != None and montant_enfant_6 != 0.0 : tarifsDegr.append(montant_enfant_6)
                                        for x in range(0, 20) : tarifsDegr.append(0.0)
                                        montant_tarif = tarifsDegr[nbreIndividus-1]
                                    else:
                                        # Si tarif unique pour chacun des individus
                                        if nbreIndividus == 1 and montant_enfant_1 != None and montant_enfant_1 != 0.0 : montant_tarif_tmp = montant_enfant_1
                                        if nbreIndividus == 2 and montant_enfant_2 != None and montant_enfant_2 != 0.0 : montant_tarif_tmp = montant_enfant_2
                                        if nbreIndividus == 3 and montant_enfant_3 != None and montant_enfant_3 != 0.0 : montant_tarif_tmp = montant_enfant_3
                                        if nbreIndividus == 4 and montant_enfant_4 != None and montant_enfant_4 != 0.0 : montant_tarif_tmp = montant_enfant_4
                                        if nbreIndividus == 5 and montant_enfant_5 != None and montant_enfant_5 != 0.0 : montant_tarif_tmp = montant_enfant_5
                                        if nbreIndividus >= 6 and montant_enfant_6 != None and montant_enfant_6 != 0.0 : montant_tarif_tmp = montant_enfant_6

                                    # Modifie le tarif des autres individus de la famille
                                    index = 0
                                    for IDprestation, dictValeurs in self.dictPrestations.items() :
                                        if IDprestation != IDtarifPrestationSupprimee and dictValeurs["date"] == date and dictValeurs["IDfamille"] == IDfamille and dictValeurs["IDtarif"] == IDtarifTmp and dictValeurs["IDindividu"] != IDindividu :
                                            
                                            # Recherche du tarif � appliquer aux autres individus de la famille
                                            if "degr" in methode_calcul :
                                                montantTmp = 0.0
                                                try :
                                                    montantTmp = tarifsDegr[index]
                                                    if montantTmp == None or montantTmp == "" : 
                                                        montantTmp = 0.0
                                                except : pass
                                            else:
                                                montantTmp = montant_tarif_tmp
                                                
                                            montantInitial = self.dictPrestations[IDprestation]["montant_initial"]
                                            montantDeduction = montantInitial - self.dictPrestations[IDprestation]["montant"]
                                            montantFinal = montantTmp - montantDeduction
                                            self.dictPrestations[IDprestation]["montant_initial"] = montantTmp
                                            self.dictPrestations[IDprestation]["montant"] = montantFinal
                                            
                                            self.listePrestationsModifiees.append(IDprestation)

                                            # Modifie le montant affich� dans le volet Facturation
                                            if self.mode == "individu" :
                                                self.GetGrandParent().panel_facturation.ModifiePrestation(
                                                                date=date, 
                                                                IDindividu=dictValeurs["IDindividu"], 
                                                                IDprestation=IDprestation, 
                                                                montantVentilation=dictValeurs["montantVentilation"], 
                                                                nouveauMontant=montantFinal,
                                                                )

                                            index += 1

        # 8 - Suppression des anciennes prestations
        for IDprestationAncienne, categorie in listeAnciennesPrestations :
            if (IDprestationAncienne in self.dictPrestations) == True :
                del self.dictPrestations[IDprestationAncienne]
            self.listePrestationsSupprimees.append(IDprestationAncienne)

        # 9 - Met � jour le controle d'affichage des prestations
        if self.mode == "individu" :
            self.GetGrandParent().panel_facturation.SaisiePrestation(
                    self.dictPrestations,
                    self.dictDeductions,
                    listeNouvellesPrestations,
                    listeAnciennesPrestations,
                    self.listeSelectionIndividus,
                    self.listeActivites,
                    self.listePeriodes,
                    )
    
    
    
    
    def MAJ_facturation(self):
        if self.GetGrandParent().GetName() == "test" or self.mode == "date" : return
        
        self.GetGrandParent().panel_facturation.RAZ()
        self.GetGrandParent().panel_facturation.SaisiePrestation(
                self.dictPrestations,
                self.dictDeductions,
                list(self.dictPrestations.keys()),
                [],
                self.listeSelectionIndividus,
                self.listeActivites,
                self.listePeriodes,
                )
            
    def MAJ_ctrl_facturation(self, regroupement="date"):
        """ regroupement = 'date' ou 'individu' """    
        texte = ""
        listeDates = []
        listeIndividus = []
        dictPrestation = {}
        for prestation in self.dictPrestations :
            date = prestation["date"]
            IDindividu = prestation["IDindividu"]
            if IDindividu in self.listeSelectionIndividus :
                # Recherche des dates
                if date not in listeDates :
                    listeDates.append(date)
                # Recherche des individus
                if IDindividu not in listeIndividus :
                    listeIndividus.append(IDindividu)
                # Place la prestation dans un dictionnaire
                if (date in dictPrestation) == False :
                    dictPrestation[date] = {}
                if (IDindividu in dictPrestation[date]) == False :
                    dictPrestation[date][IDindividu] = []
                dictPrestation[date][IDindividu].append(prestation)
        
        listeDates.sort() 
        listeIndividus.sort() 

        # Met en forme l'affichage
        if regroupement == "date" :
            for date in listeDates :
                if len(dictPrestation[date]) > 0 :
                    # Affichage de la date
                    texte += u"---- %s --------------- \n" % DateComplete(date)
                    for IDindividu in listeIndividus :
                        # Affichage du nom de l'individu
                        if IDindividu in dictPrestation[date] : 
                            nom = self.dictIndividus[IDindividu]["nom"]
                            prenom = self.dictIndividus[IDindividu]["prenom"]
                            texte += u"   %s %s : \n" % (nom, prenom)
                            # Affichage des prestations
                            for prestation in dictPrestation[date][IDindividu] :
                                label = prestation["label"]
                                montant = prestation["montant"]
                                texte += u"      - %s : %s �\n" % (label, montant)
                texte += u"\n"
        
        if regroupement == "individu" :
            for IDindividu in listeIndividus :
                # Affichage du nom de l'individu
                nom = self.dictInfosIndividus[IDindividu]["nom"]
                prenom = self.dictInfosIndividus[IDindividu]["prenom"]
                texte += u"   %s %s : \n" % (nom, prenom)
                for date in listeDates :
                    # Affichage de la date
                    if IDindividu in dictPrestation[date] : 
                        texte += u"%s \n" % DateComplete(date)
                        # Affichage des prestations
                        for prestation in dictPrestation[date][IDindividu] :
                            label = prestation["label"]
                            montant = prestation["montant"]
                            texte += u"      - %s : %s �\n" % (label, montant)
                    texte += u"\n"
        
        # Ecrit dans la fen�tre de TEST
        try : self.GetGrandParent().ctrl_facturation.SetValue(texte)
        except : pass
        
        # Ecrit dans la fen�tre AUI
        try : self.GetGrandParent().panel_facturation.SetValue(texte)
        except : pass
        
        
    def RechercheCombinaisonDict(self, dictUnitesUtilisees={}, combinaison=[], dictTarif={}):
        """ Recherche une combinaison donn�e dans une ligne de la grille """
        for IDunite_combi in combinaison :
            # V�rifie si chaque unit� est dans la combinaison
            if (IDunite_combi in dictUnitesUtilisees) == False :
                return False
            if dictUnitesUtilisees[IDunite_combi] == None :
                return False
            # V�rifie si l'�tat est valide
            if dictTarif["type"] == "JOURN" :
                etats = dictTarif["etats"]
                etat = dictUnitesUtilisees[IDunite_combi]
                if etat not in etats :
                    return False
        return True

    def RechercheCombinaisonTuple(self, combinaisons_unites=[], combinaison=[]):
        """ Recherche une combinaison donn�e dans une ligne de la grille """
        for IDunite_combi in combinaison :
            if IDunite_combi not in combinaisons_unites :
                return False
        return True
    
    def GetTarifsForfaitsCreditDisponibles(self, date=datetime.date(2012, 1, 10)):
        """ Fonction utilisation pour la cr�ation d'un forfait au cr�dit """
        # Recherche des tarifs disponibles pour chaque individu
        dictDonnees = {}
        listeActivites = []
        for IDindividu, dictIndividu in self.dictInfosInscriptions.items() :
            for IDactivite, dictInscription in dictIndividu.items() :
                IDfamille = dictInscription["IDfamille"]
                IDgroupe = dictInscription["IDgroupe"]
                IDcategorie_tarif = dictInscription["IDcategorie_tarif"]
                
                if IDactivite not in listeActivites :
                    listeActivites.append(IDactivite)
                
                # Cr�ation de dict de r�sultats
                if (IDfamille in dictDonnees) == False :
                    dictDonnees[IDfamille] = { "individus":{}, "forfaits":[] }
                if (IDindividu in dictDonnees[IDfamille]["individus"]) == False :
                    nom = self.dictInfosIndividus[IDindividu]["nom"]
                    prenom = self.dictInfosIndividus[IDindividu]["prenom"]
                    dictDonnees[IDfamille]["individus"][IDindividu] = { "nom":nom, "prenom":prenom, "forfaits":[]}
                
                # Recherche de forfaits individuels valides pour cette inscription
                if "tarifs" in self.dictActivites[IDactivite] :
                    if IDcategorie_tarif in self.dictActivites[IDactivite]["tarifs"]:
                        for dictTarif in self.dictActivites[IDactivite]["tarifs"][IDcategorie_tarif] :
                            if dictTarif["type"] == "CREDIT" and dictTarif["forfait_beneficiaire"] == "individu" :
                                if self.RechercheTarifValide(dictTarif, IDgroupe=IDgroupe, date=date, IDindividu=IDindividu, IDfamille=IDfamille) == True :
                                    # Calcul du montant du forfait
                                    resultat = self.CalculeTarif(dictTarif, date=date, IDfamille=IDfamille, IDindividu=IDindividu)
                                    if resultat != False :
                                        montant_tarif, nom_tarif, temps_facture = resultat
                                        dictTarif["resultat"] = {"IDindividu":IDindividu, "montant_tarif":montant_tarif, "nom_tarif":nom_tarif, "temps_facture":temps_facture, "IDcategorie_tarif":IDcategorie_tarif, "nomActivite":self.dictActivites[IDactivite]["abrege"]}
                                        dictDonnees[IDfamille]["individus"][IDindividu]["forfaits"].append(dictTarif.copy())
        
        # Recherche des tarifs disponibles pour chaque famille
        for IDfamille in list(dictDonnees.keys()) :
            for IDactivite in listeActivites :
                if "tarifs" in self.dictActivites[IDactivite] :
                    for IDcategorie_tarif, listeTarifs in self.dictActivites[IDactivite]["tarifs"].items() :
                        for dictTarif in listeTarifs :
                            if dictTarif["type"] == "CREDIT" and dictTarif["forfait_beneficiaire"] == "famille" :
                                if self.RechercheTarifValide(dictTarif, date=date, IDindividu=IDindividu, IDfamille=IDfamille) == True :
                                    # Calcul du montant du forfait
                                    resultat = self.CalculeTarif(dictTarif, date=date, IDfamille=IDfamille)
                                    if resultat != False :
                                        montant_tarif, nom_tarif, temps_facture = resultat
                                        dictTarif["resultat"] = {"IDindividu":None, "montant_tarif":montant_tarif, "nom_tarif":nom_tarif, "temps_facture":temps_facture, "IDcategorie_tarif":None, "nomActivite":self.dictActivites[IDactivite]["abrege"]}
                                        if dictTarif not in dictDonnees[IDfamille]["forfaits"] :
                                            dictDonnees[IDfamille]["forfaits"].append(dictTarif.copy())
        
        # Affichage pour DEBUG
##        for IDfamille, dictFamille in dictDonnees.iteritems() :
##            print "----- FAMILLE %d -----" % IDfamille
##            print "forfaits famille =", dictFamille["forfaits"]
##            
##            for IDindividu, dictIndividu in dictFamille["individus"].iteritems() :
##                print "INDIVIDU %d" % IDindividu
##                for dictTarif in dictIndividu["forfaits"]:
##                    print "    >", dictTarif

        return dictDonnees
        
    def GetFamillesAffichees(self):
        listeFamilles = []
        for IDindividu, dictIndividu in self.dictInfosInscriptions.items() :
            for IDactivite, dictInscription in dictIndividu.items() :
                IDfamille = dictInscription["IDfamille"]
                if IDfamille not in listeFamilles :
                    listeFamilles.append(IDfamille)
        return listeFamilles

    def CreationCouleurForfait(self, index=0):
        listeCouleurs = [
            (77, 133, 255), (155, 255, 105), (255, 148, 82), (255, 133, 255), (149, 131, 255),
            (92, 255, 230), (156, 255, 57), (255, 69, 168), (218, 187, 255), (49, 255, 114),
            (18, 144, 255), (150, 67, 37), (150, 40, 142), (43, 52, 150), (34, 150, 144),
            (30, 150, 63), (132, 150, 43), (93, 35, 87), (79, 66, 93), (0, 93, 31),
            ]
        if index < len(listeCouleurs) -1 :
            return listeCouleurs[index]
        else :
            return (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))



    def MemorisePrestation(self, IDcompte_payeur, date, IDactivite, IDtarif, nom_tarif, montant_initial, montant_final, IDfamille, IDindividu, categorie="consommation", listeDeductions=[], 
                                                temps_facture=None, IDcategorie_tarif=None, forfait_date_debut=None, forfait_date_fin=None, dictTarif=None, evenement=None):
        """ M�morisation de la prestation """

        # Pr�paration des valeurs � m�moriser
        if IDindividu != None :
            nomIndividu = u"%s %s" % (self.dictIndividus[IDindividu]["nom"], self.dictIndividus[IDindividu]["prenom"])
        else:
            nomIndividu = u""
            
        dictPrestation = {
                "IDcompte_payeur" : IDcompte_payeur, 
                "date" : date, 
                "categorie" : categorie,
                "label" : nom_tarif, 
                "montant_initial" : montant_initial, 
                "montant" : montant_final, 
                "IDactivite" : IDactivite,
                "IDtarif" : IDtarif, 
                "IDfacture" : None, 
                "IDfamille" : IDfamille, 
                "IDindividu" : IDindividu,
                "nomIndividu" : nomIndividu,
                "temps_facture" : temps_facture,
                "IDcategorie_tarif" : IDcategorie_tarif,
                "forfait_date_debut" : forfait_date_debut,
                "forfait_date_fin" : forfait_date_fin,
                "code_compta" : dictTarif["code_compta"],
                "code_produit_local": dictTarif["code_produit_local"],
                "tva" : dictTarif["tva"],
                "forfait" : None,
                }

        # Recherche si une prestation identique existe d�j� en m�moire
        for IDprestation, dictTemp1 in self.dictPrestations.items() :
            if IDprestation > 0 :
                dictTemp2 = dictTemp1.copy()

                # Renvoie prestation existante si la prestation appara�t d�j� sur une facture m�me si le montant est diff�rent
                keys = ["date", "IDindividu", "IDtarif", "IDcompte_payeur"]
                if evenement:
                    keys.append("label")
                if dictTemp2["IDfacture"] != None and CompareDict(dictPrestation, dictTemp2, keys=keys) == True :
                    return IDprestation

                # Renvoie prestation existante si la prestation semble identique avec montants identiques
                keys = ["date", "IDindividu", "IDtarif", "montant_initial", "montant", "IDcategorie_tarif", "IDcompte_payeur", "label", "temps_facture"]
                if CompareDict(dictPrestation, dictTemp2, keys=keys) == True :
                    return IDprestation

        # Recherche le prochain num�ro dans la liste des prestations
        IDprestation = self.prochainIDprestation
        self.prochainIDprestation -= 1
        
        # M�morisation de la prestation
        dictPrestation["IDprestation"] = IDprestation
        dictPrestation["montantVentilation"] = 0.0
        self.dictPrestations[IDprestation] = dictPrestation
        
        # Cr�ation des d�ductions pour les aides journali�res
        self.CreationDeductions(listeDeductions=listeDeductions, IDprestation=IDprestation, IDcompte_payeur=IDcompte_payeur, date=date)

        return IDprestation


    def CreationDeductions(self, listeDeductions=[], IDprestation=None, IDcompte_payeur=None, date=None):
        # Cr�ation des d�ductions pour les aides journali�res
        for deduction in listeDeductions :
            IDdeduction = self.prochainIDdeduction
            self.prochainIDdeduction -= 1
            IDaide = deduction["IDaide"]
            dictTemp = {
                "IDdeduction" : IDdeduction, "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur,
                "date" : date, "montant" : deduction["montant"], "label" : self.dictAides[IDaide]["nomAide"], "IDaide" : IDaide,
                }
            if (IDprestation in self.dictDeductions) == False :
                self.dictDeductions[IDprestation] = []

            # Recherche si cette aide existe d�j�
            index_exist = None
            index = 0
            for deduction_temp in self.dictDeductions[IDprestation]:
                if deduction_temp["IDaide"] == IDaide and deduction_temp["IDprestation"] == IDprestation and deduction_temp["date"] == date :
                    index_exist = index
                index += 1

            if index_exist == None :
                self.dictDeductions[IDprestation].append(dictTemp)
            else :
                self.dictDeductions[IDprestation][index_exist] = dictTemp


    def RechercheForfaitCredit(self, IDtarif=None, date=None, IDfamille=None, IDindividu=None):
        """ Recherche un forfait dans la liste des forfaits disponibles pour une consommation donn�e """
        for IDprestation, dictTarif in self.dictForfaits.items() :
            if dictTarif["IDtarif"] == IDtarif and dictTarif["forfait_date_debut"] <= date and dictTarif["forfait_date_fin"] >= date :
                if dictTarif["IDfamille"] == IDfamille :
                    if dictTarif["IDindividu"] == IDindividu or dictTarif["IDindividu"] == 0 or dictTarif["IDindividu"] == None :
                        return IDprestation, dictTarif
        return None, None
    
    def RechercheTarifValide(self, dictTarif={}, IDgroupe=None, date=None, IDindividu=None, IDfamille=None, etiquettes=[]):
        """ Pour Facturation """
        # V�rifie si dates validit� ok
        date_debut = dictTarif["date_debut"]
        date_fin = dictTarif["date_fin"]
        if date_fin == None : date_fin = datetime.date(2999, 1, 1)
        if date_debut == None or date < date_debut or date > date_fin :
            return False

        # V�rifie si groupe ok
        listeGroupes = dictTarif["groupes"]
        if listeGroupes != None :
            if IDgroupe not in listeGroupes :
                return False

        # V�rifie si �tiquette ok
        listeEtiquettes = dictTarif["etiquettes"]
        if listeEtiquettes != None :
            valide = False
            for IDetiquette in etiquettes :
                if IDetiquette in listeEtiquettes :
                    valide = True
            if valide == False :
                return False
            
        # V�rifie si cotisation � jour
        if dictTarif["cotisations"] != None :
            cotisationsValide = self.VerificationCotisations(listeCotisations=dictTarif["cotisations"], date=date, IDindividu=IDindividu, IDfamille=IDfamille)
            if cotisationsValide == False :
                return False

        # V�rifie si caisse � jour
        if dictTarif["caisses"] != None :
            caissesValide = self.VerificationCaisses(listeCaisses=dictTarif["caisses"], IDfamille=IDfamille)
            if caissesValide == False :
                return False

        # V�rifie si p�riode ok
        if dictTarif["jours_scolaires"] != None or dictTarif["jours_vacances"] != None :
            if self.VerificationPeriodes(dictTarif["jours_scolaires"], dictTarif["jours_vacances"], date) == False :
                return False
                
        # V�rifie si filtres de questionnaires ok
        if len(dictTarif["filtres"]) > 0 :
            filtresValide = self.VerificationFiltres(listeFiltres=dictTarif["filtres"], date=date, IDindividu=IDindividu, IDfamille=IDfamille)
            if filtresValide == False :
                return False
            
        return True


    def RechercheQF(self, dictTarif=None, IDfamille=None, date=None):
        """ Pour Facturation Recherche du QF de la famille """
        # Si la famille a un QF :
        if IDfamille in self.dictQuotientsFamiliaux :
            listeQuotientsFamiliaux = self.dictQuotientsFamiliaux[IDfamille]
            for date_debut, date_fin, quotient, IDtype_quotient in listeQuotientsFamiliaux :
                if date >= date_debut and date <= date_fin and (dictTarif["IDtype_quotient"] == None or dictTarif["IDtype_quotient"] == IDtype_quotient) :
                    return quotient

        # Si la famille n'a pas de QF, on attribue le QF le plus �lev� :
        listeQF = []
        for ligneCalcul in dictTarif["lignes_calcul"] :
            qf = ligneCalcul["qf_max"]
            if qf:
                qf = float(qf)
            listeQF.append(qf)
        listeQF.sort()
        if len(listeQF) > 0 :
            if listeQF[-1] != None :
                return listeQF[-1]

        return None
    
    def CalculeDuree(self, IDindividu=None, datePrestation=None, combinaisons_unites=[]):
        """ Pour Facturation """
        liste_temps = []
        heure_min = None
        heure_max = None
        for IDunite, listeConso in self.dictConsoIndividus[IDindividu][datePrestation].items() :
            if IDunite in combinaisons_unites :
                for conso in listeConso :
                    if conso.statut != "suppression" and conso.etat in ("reservation", "present", "absenti") :
                        heure_debut = conso.heure_debut
                        heure_fin = conso.heure_fin
                        if heure_debut not in (None, "") and heure_fin not in (None, "") :
                            liste_temps.append((heure_debut, heure_fin))
                            if heure_min == None or HeureStrEnDelta(heure_debut)  < heure_min :
                                heure_min = HeureStrEnDelta(heure_debut)
                            if heure_max == None or HeureStrEnDelta(heure_fin)  > heure_max :
                                heure_max = HeureStrEnDelta(heure_fin)

        if heure_min == None :
            heure_min = datetime.timedelta(hours=0, minutes=0)
        if heure_max == None :
            heure_max = datetime.timedelta(hours=0, minutes=0)

        if len(liste_temps) > 0 :
            duree = Additionne_intervalles_temps(liste_temps)
        else :
            duree = None
        return duree, heure_min, heure_max
    
    def GetQuestionnaire(self, IDquestion=None, IDfamille=None, IDindividu=None):
        if IDquestion in (None, "", 0):
            return None
        q = UTILS_Questionnaires.Questionnaires() 
        reponse = q.GetReponse(IDquestion, IDfamille, IDindividu)
        return reponse
        
    def CalculeTarif(self, dictTarif={}, combinaisons_unites=[], date=None, temps_facture=None, IDfamille=None, IDindividu=None, quantite=None, case=None, modeSilencieux=False, evenement=None, action="saisie"):
        IDtarif = dictTarif["IDtarif"]
        IDactivite = dictTarif["IDactivite"]
        nom_tarif = dictTarif["nom_tarif"]
        description_tarif = dictTarif["description_tarif"]
        montant_tarif = 0.0
        methode_calcul = dictTarif["methode"]
        label_prestation = dictTarif["label_prestation"]

        # Label de la prestation personnalis�
        if label_prestation != None and label_prestation == "description_tarif" :
            nom_tarif = description_tarif
        if label_prestation != None and label_prestation.startswith("autre:"):
            nom_tarif = label_prestation[6:]

        # Recherche du montant du tarif : MONTANT UNIQUE
        if methode_calcul == "montant_unique" :
            lignes_calcul = dictTarif["lignes_calcul"]
            montant_tarif = lignes_calcul[0]["montant_unique"]
            
            montant_questionnaire = self.GetQuestionnaire(lignes_calcul[0]["montant_questionnaire"], IDfamille, IDindividu)
            if montant_questionnaire not in (None, 0.0) :
                montant_tarif = montant_questionnaire
            
        # Recherche du montant � appliquer : QUOTIENT FAMILIAL
        if methode_calcul == "qf" :
            montant_tarif = 0.0
            tarifFound = False
            lignes_calcul = dictTarif["lignes_calcul"]
            for ligneCalcul in lignes_calcul :
                qf_min = float(ligneCalcul["qf_min"])
                qf_max = float(ligneCalcul["qf_max"])
                montant_tarif = ligneCalcul["montant_unique"]

                QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                if QFfamille != None :
                    if QFfamille >= qf_min and QFfamille <= qf_max :
                        break

                # if self.dictQuotientsFamiliaux.has_key(IDfamille) :
                #     listeQuotientsFamiliaux = self.dictQuotientsFamiliaux[IDfamille]
                #     for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                #         if date >= date_debut and date <= date_fin and quotient >= qf_min and quotient <= qf_max :
                #             tarifFound = True
                #             break
                #     if tarifFound == True :
                #             break
        
        # Recherche du montant du tarif : HORAIRE - MONTANT UNIQUE
        if methode_calcul == "horaire_montant_unique" :
            montant_tarif = 0.0
            tarifFound = False
            lignes_calcul = dictTarif["lignes_calcul"]

            # Recherche des heures debut et fin des unit�s coch�es
            heure_debut = None
            heure_fin = None
            for IDunite, listeConso in self.dictConsoIndividus[IDindividu][date].items() :
                if IDunite in combinaisons_unites :
                    for conso in listeConso :
                        heure_debut_temp = HeureStrEnTime(conso.heure_debut)
                        heure_fin_temp = HeureStrEnTime(conso.heure_fin)
                        
                        if heure_debut == None or heure_debut_temp < heure_debut : 
                            heure_debut = heure_debut_temp
                            
                        if heure_fin == None or heure_fin_temp > heure_fin : 
                            heure_fin = heure_fin_temp
            
            for ligneCalcul in lignes_calcul :
                heure_debut_min = HeureStrEnTime(ligneCalcul["heure_debut_min"])
                heure_debut_max = HeureStrEnTime(ligneCalcul["heure_debut_max"])
                heure_fin_min = HeureStrEnTime(ligneCalcul["heure_fin_min"])
                heure_fin_max = HeureStrEnTime(ligneCalcul["heure_fin_max"])
                montant_tarif_ligne = ligneCalcul["montant_unique"]

                montant_questionnaire = self.GetQuestionnaire(ligneCalcul["montant_questionnaire"], IDfamille, IDindividu)
                if montant_questionnaire not in (None, 0.0) :
                    montant_tarif_ligne = montant_questionnaire

                if heure_debut_min <= heure_debut <= heure_debut_max and heure_fin_min <= heure_fin <= heure_fin_max :
                    montant_tarif = montant_tarif_ligne
                    if ligneCalcul["temps_facture"] != None and ligneCalcul["temps_facture"] != "" :
                        temps_facture = HeureStrEnTime(ligneCalcul["temps_facture"]) 
                        temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                    else :
                        temps_facture = SoustractionHeures(heure_fin_max, heure_debut_min)
                        
                    heure_debut_delta = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
                    heure_fin_delta = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
                    duree_delta = heure_fin_delta - heure_debut_delta
                    
                    # Cr�ation du label personnalis�
                    label = ligneCalcul["label"]
                    if label != None and label != "" :
                        if "{TEMPS_REALISE}" in label : 
                            label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree_delta))
                        if "{TEMPS_FACTURE}" in label : 
                            label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                        if "{HEURE_DEBUT}" in label : 
                            label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                        if "{HEURE_FIN}" in label : 
                            label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                        nom_tarif = label

                    break

        
        # Recherche du montant du tarif : HORAIRE - QF
        if methode_calcul == "horaire_qf" :
            montant_tarif = 0.0
            tarifFound = False
            lignes_calcul = dictTarif["lignes_calcul"]

            # Recherche des heures debut et fin des unit�s coch�es
            heure_debut = None
            heure_fin = None
            for IDunite, listeConso in self.dictConsoIndividus[IDindividu][date].items() :
                if IDunite in combinaisons_unites :
                    for conso in listeConso :
                        heure_debut_temp = HeureStrEnTime(conso.heure_debut)
                        heure_fin_temp = HeureStrEnTime(conso.heure_fin)
                        
                        if heure_debut == None or heure_debut_temp < heure_debut : 
                            heure_debut = heure_debut_temp
                            
                        if heure_fin == None or heure_fin_temp > heure_fin : 
                            heure_fin = heure_fin_temp

            for ligneCalcul in lignes_calcul :
                qf_min = ligneCalcul["qf_min"]
                qf_max = ligneCalcul["qf_max"]
                heure_debut_min = HeureStrEnTime(ligneCalcul["heure_debut_min"])
                heure_debut_max = HeureStrEnTime(ligneCalcul["heure_debut_max"])
                heure_fin_min = HeureStrEnTime(ligneCalcul["heure_fin_min"])
                heure_fin_max = HeureStrEnTime(ligneCalcul["heure_fin_max"])
                montant_tarif_ligne = ligneCalcul["montant_unique"]
                
                if heure_debut_min <= heure_debut <= heure_debut_max and heure_fin_min <= heure_fin <= heure_fin_max :
                    montant_tarif = montant_tarif_ligne
                    
                    # Recherche le QF de la famille
                    QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            montant_tarif = montant_tarif_ligne
                            if ligneCalcul["temps_facture"] != None and ligneCalcul["temps_facture"] != "" :
                                temps_facture = HeureStrEnTime(ligneCalcul["temps_facture"])
                                temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                            else :
                                temps_facture = SoustractionHeures(heure_fin_max, heure_debut_min)

                            heure_debut_delta = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
                            heure_fin_delta = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
                            duree_delta = heure_fin_delta - heure_debut_delta

                            # Cr�ation du label personnalis�
                            label = ligneCalcul["label"]
                            if label != None and label != "" :
                                if "{TEMPS_REALISE}" in label :
                                    label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree_delta))
                                if "{TEMPS_FACTURE}" in label :
                                    label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                                if "{HEURE_DEBUT}" in label :
                                    label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                                if "{HEURE_FIN}" in label :
                                    label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                                nom_tarif = label
                            break



                    # if self.dictQuotientsFamiliaux.has_key(IDfamille) :
                    #     listeQuotientsFamiliaux = self.dictQuotientsFamiliaux[IDfamille]
                    #     for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                    #         if date >= date_debut and date <= date_fin and quotient >= qf_min and quotient <= qf_max :
                    #             montant_tarif = montant_tarif_ligne
                    #             if ligneCalcul["temps_facture"] != None and ligneCalcul["temps_facture"] != "" :
                    #                 temps_facture = HeureStrEnTime(ligneCalcul["temps_facture"])
                    #                 temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                    #             else :
                    #                 temps_facture = SoustractionHeures(heure_fin_max, heure_debut_min)
                    #
                    #             heure_debut_delta = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
                    #             heure_fin_delta = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
                    #             duree_delta = heure_fin_delta - heure_debut_delta
                    #
                    #             # Cr�ation du label personnalis�
                    #             label = ligneCalcul["label"]
                    #             if label != None and label != "" :
                    #                 if "{TEMPS_REALISE}" in label :
                    #                     label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree_delta))
                    #                 if "{TEMPS_FACTURE}" in label :
                    #                     label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                    #                 if "{HEURE_DEBUT}" in label :
                    #                     label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                    #                 if "{HEURE_FIN}" in label :
                    #                     label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                    #                 nom_tarif = label
                    #
                    #             tarifFound = True
                    #             break
                    #     if tarifFound == True :
                    #         break
                
        
        # Recherche du montant du tarif : DUREE - MONTANT UNIQUE
        if methode_calcul == "duree_montant_unique" :
            montant_tarif = 0.0
            tarifFound = False
            lignes_calcul = dictTarif["lignes_calcul"]

            # Recherche des heures debut et fin des unit�s coch�es
            duree, heure_debut_delta, heure_fin_delta = self.CalculeDuree(IDindividu, date, combinaisons_unites)
            duree_delta = heure_fin_delta - heure_debut_delta

            for ligneCalcul in lignes_calcul :
                duree_min = HeureStrEnDelta(ligneCalcul["duree_min"])
                duree_max = HeureStrEnDelta(ligneCalcul["duree_max"])
                montant_tarif_ligne = ligneCalcul["montant_unique"]

                montant_questionnaire = self.GetQuestionnaire(ligneCalcul["montant_questionnaire"], IDfamille, IDindividu)
                if montant_questionnaire not in (None, 0.0) :
                    montant_tarif_ligne = montant_questionnaire

                if duree_min <= duree <= duree_max :
                    montant_tarif = montant_tarif_ligne
                    if ligneCalcul["temps_facture"] != None and ligneCalcul["temps_facture"] != "" :
                        temps_facture = HeureStrEnTime(ligneCalcul["temps_facture"]) 
                        temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                    else :
                        temps_facture = duree_max
                                
                    # Cr�ation du label personnalis�
                    label = ligneCalcul["label"]
                    if label != None and label != "" :
                        if "{TEMPS_REALISE}" in label : 
                            label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree_delta))
                        if "{TEMPS_FACTURE}" in label : 
                            label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                        if "{HEURE_DEBUT}" in label : 
                            label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                        if "{HEURE_FIN}" in label : 
                            label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                        nom_tarif = label

                    break
        
        
        # Recherche du montant du tarif : DUREE - QF
        if methode_calcul == "duree_qf" :
            montant_tarif = 0.0
            tarifFound = False
            lignes_calcul = dictTarif["lignes_calcul"]

            # Recherche de la dur�e totale des unit�s coch�es
##            heure_debut = None
##            heure_fin = None
##            for IDunite, listeConso in self.dictConsoIndividus[IDindividu][date].iteritems() :
##                if IDunite in combinaisons_unites :
##                    for conso in listeConso :
##                    case = self.dictConsoIndividus[IDindividu][date][IDunite]
##                    heure_debut_temp = HeureStrEnTime(case.heure_debut)
##                    heure_fin_temp = HeureStrEnTime(case.heure_fin)
##                    
##                    if heure_debut == None or heure_debut_temp < heure_debut : 
##                        heure_debut = heure_debut_temp
##                        
##                    if heure_fin == None or heure_fin_temp > heure_fin : 
##                        heure_fin = heure_fin_temp
##            
##            # Calcul de la dur�e
##            heure_debut_delta = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
##            heure_fin_delta = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
##            duree_delta = heure_fin_delta - heure_debut_delta
##            duree = DeltaEnTime(heure_fin_delta - heure_debut_delta)
            
            liste_temps = []
            for IDunite, listeConso in self.dictConsoIndividus[IDindividu][date].items() :
                if IDunite in combinaisons_unites :
                    for conso in listeConso :
                        heure_debut = conso.heure_debut
                        heure_fin = conso.heure_fin
                        if heure_debut != None and heure_fin != None :
                            liste_temps.append((heure_debut, heure_fin))
            if len(liste_temps) > 0 :
                duree = Additionne_intervalles_temps(liste_temps)
            else :
                duree = None


            for ligneCalcul in lignes_calcul :
                qf_min = ligneCalcul["qf_min"]
                qf_max = ligneCalcul["qf_max"]
                duree_min = HeureStrEnDelta(ligneCalcul["duree_min"])
                duree_max = HeureStrEnDelta(ligneCalcul["duree_max"])
                montant_tarif_ligne = ligneCalcul["montant_unique"]
                
                # Recherche le QF de la famille
                if duree_min <= duree <= duree_max :
                    montant_tarif = montant_tarif_ligne

                    # Temps factur�
                    if ligneCalcul["temps_facture"] != None and ligneCalcul["temps_facture"] != "" :
                        temps_facture = HeureStrEnTime(ligneCalcul["temps_facture"])
                        temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                    else :
                        temps_facture = duree_max

                    # Cr�ation du label personnalis�
                    label = ligneCalcul["label"]
                    if label != None and label != "" :
                        if "{TEMPS_REALISE}" in label :
                            label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree))
                        if "{TEMPS_FACTURE}" in label :
                            label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                        if "{HEURE_DEBUT}" in label :
                            label = label.replace("{HEURE_DEBUT}", heure_debut.replace(":", "h"))
                        if "{HEURE_FIN}" in label :
                            label = label.replace("{HEURE_FIN}", heure_fin.replace(":", "h"))
                        nom_tarif = label

                    # Recherche le QF
                    QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            break

                    # if self.dictQuotientsFamiliaux.has_key(IDfamille) :
                    #     listeQuotientsFamiliaux = self.dictQuotientsFamiliaux[IDfamille]
                    #     for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                    #         if date >= date_debut and date <= date_fin and quotient >= qf_min and quotient <= qf_max :
                    #             tarifFound = True
                    #             break
                    # if tarifFound == True :
                    #     break

        # Recherche du montant du tarif : MONTANT UNIQUE EN FONCTION DE LA DATE
        if methode_calcul == "montant_unique_date" :
            montant_tarif = 0.0
            lignes_calcul = dictTarif["lignes_calcul"]

            for ligneCalcul in lignes_calcul :
                dateLigne = DateEngEnDateDD(ligneCalcul["date"])
                montant_tarif_ligne = ligneCalcul["montant_unique"]
                label = ligneCalcul["label"]
                
                if date == dateLigne :
                    montant_tarif = montant_tarif_ligne
                    if label != None and label != "" :
                        nom_tarif = label
            
        # Recherche du montant � appliquer : EN FONCTION DE LA DATE ET DU QUOTIENT FAMILIAL
        if methode_calcul == "qf_date" :
            montant_tarif = 0.0
            tarifFound = False
            dateFound = False
            lignes_calcul = dictTarif["lignes_calcul"]
            for ligneCalcul in lignes_calcul :
                qf_min = ligneCalcul["qf_min"]
                qf_max = ligneCalcul["qf_max"]
                montant_tarif = ligneCalcul["montant_unique"]
                dateLigne = DateEngEnDateDD(ligneCalcul["date"])
                label = ligneCalcul["label"]
                
                if date == dateLigne : 
                    dateFound = True

                    # Recherche le QF
                    QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            break

                    # if self.dictQuotientsFamiliaux.has_key(IDfamille) :
                    #     listeQuotientsFamiliaux = self.dictQuotientsFamiliaux[IDfamille]
                    #     for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                    #         if date >= date_debut and date <= date_fin and quotient >= qf_min and quotient <= qf_max :
                    #             tarifFound = True
                    #             break
                    #     if tarifFound == True :
                    #         break
            
            if dateFound == False : 
                montant_tarif = 0.0

        # Recherche du montant du tarif : MONTANT DE L'EVENEMENT
        if methode_calcul == "montant_evenement":
            if evenement != None :
                montant_tarif = evenement.montant
                nom_tarif = evenement.nom

        # Recherche du montant du tarif : VARIABLE (MONTANT ET LABEL SAISIS PAR L'UTILISATEUR)
        if methode_calcul == "variable" :
            if action == "saisie" and case.IDunite in combinaisons_unites and modeSilencieux == False :
                # Nouvelle saisie si clic sur la case
                from Dlg import DLG_Saisie_montant_prestation
                dlg = DLG_Saisie_montant_prestation.Dialog(self, label=nom_tarif, montant=0.0)
                dlg.ShowModal()
                nom_tarif = dlg.GetLabel()
                montant_tarif = dlg.GetMontant()
                dlg.Destroy()
            else :
                # Sinon pas de nouvelle saisie : on cherche l'ancienne prestation d�j� saisie
                for IDprestation, dictValeurs in self.dictPrestations.items() :
                    if dictValeurs["date"] == date and dictValeurs["IDfamille"] == IDfamille and dictValeurs["IDindividu"] == IDindividu and dictValeurs["IDtarif"] == IDtarif :
                        nom_tarif = dictValeurs["label"]
                        montant_tarif = dictValeurs["montant"]

        # Recherche du montant du tarif : CHOIX (MONTANT ET LABEL SELECTIONNES PAR L'UTILISATEUR)
        if methode_calcul == "choix" :
            if case != None and action == "saisie" and case.IDunite in combinaisons_unites and modeSilencieux == False :
                # Nouvelle saisie si clic sur la case
                lignes_calcul = dictTarif["lignes_calcul"]
                from Dlg import DLG_Selection_montant_prestation
                dlg = DLG_Selection_montant_prestation.Dialog(self, lignes_calcul=lignes_calcul, label=nom_tarif, montant=0.0)
                dlg.ShowModal()
                nom_tarif = dlg.GetLabel()
                montant_tarif = dlg.GetMontant()
                dlg.Destroy()
            else :
                # Sinon pas de nouvelle saisie : on cherche l'ancienne prestation d�j� saisie
                for IDprestation, dictValeurs in self.dictPrestations.items() :
                    if dictValeurs["date"] == date and dictValeurs["IDfamille"] == IDfamille and dictValeurs["IDindividu"] == IDindividu and dictValeurs["IDtarif"] == IDtarif :
                        nom_tarif = dictValeurs["label"]
                        montant_tarif = dictValeurs["montant"]
                
        # Recherche du montant du tarif : EN FONCTION DU NBRE D'INDIVIDUS
        if "nbre_ind" in methode_calcul :
            montant_tarif = 0.0
            lignes_calcul = dictTarif["lignes_calcul"]
            
            if "montant_unique" in methode_calcul  :
                # Montant unique
                montant_enfant_1 = lignes_calcul[0]["montant_enfant_1"]
                montant_enfant_2 = lignes_calcul[0]["montant_enfant_2"]
                montant_enfant_3 = lignes_calcul[0]["montant_enfant_3"]
                montant_enfant_4 = lignes_calcul[0]["montant_enfant_4"]
                montant_enfant_5 = lignes_calcul[0]["montant_enfant_5"]
                montant_enfant_6 = lignes_calcul[0]["montant_enfant_6"]
                
            if "qf" in methode_calcul  :
                # Selon QF
                tarifFound = False
                for ligneCalcul in lignes_calcul :
                    qf_min = ligneCalcul["qf_min"]
                    qf_max = ligneCalcul["qf_max"]
                    montant_enfant_1 = ligneCalcul["montant_enfant_1"]
                    montant_enfant_2 = ligneCalcul["montant_enfant_2"]
                    montant_enfant_3 = ligneCalcul["montant_enfant_3"]
                    montant_enfant_4 = ligneCalcul["montant_enfant_4"]
                    montant_enfant_5 = ligneCalcul["montant_enfant_5"]
                    montant_enfant_6 = ligneCalcul["montant_enfant_6"]

                    QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            break

            if "horaire" in methode_calcul  :
                tarifFound = False

                # Recherche des heures debut et fin des unit�s coch�es
                heure_debut = None
                heure_fin = None
                for IDunite, listeConso in self.dictConsoIndividus[IDindividu][date].items() :
                    if IDunite in combinaisons_unites :
                        for conso in listeConso :
                            heure_debut_temp = HeureStrEnTime(conso.heure_debut)
                            heure_fin_temp = HeureStrEnTime(conso.heure_fin)
                            
                            if heure_debut == None or heure_debut_temp < heure_debut : 
                                heure_debut = heure_debut_temp
                                
                            if heure_fin == None or heure_fin_temp > heure_fin : 
                                heure_fin = heure_fin_temp

                for ligneCalcul in lignes_calcul :
                    heure_debut_min = HeureStrEnTime(ligneCalcul["heure_debut_min"])
                    heure_debut_max = HeureStrEnTime(ligneCalcul["heure_debut_max"])
                    heure_fin_min = HeureStrEnTime(ligneCalcul["heure_fin_min"])
                    heure_fin_max = HeureStrEnTime(ligneCalcul["heure_fin_max"])
                    montant_tarif_ligne = ligneCalcul["montant_unique"]

                    montant_questionnaire = self.GetQuestionnaire(ligneCalcul["montant_questionnaire"], IDfamille, IDindividu)
                    if montant_questionnaire not in (None, 0.0) :
                        montant_tarif_ligne = montant_questionnaire

                    if heure_debut_min <= heure_debut <= heure_debut_max and heure_fin_min <= heure_fin <= heure_fin_max :
                        montant_enfant_1 = ligneCalcul["montant_enfant_1"]
                        montant_enfant_2 = ligneCalcul["montant_enfant_2"]
                        montant_enfant_3 = ligneCalcul["montant_enfant_3"]
                        montant_enfant_4 = ligneCalcul["montant_enfant_4"]
                        montant_enfant_5 = ligneCalcul["montant_enfant_5"]
                        montant_enfant_6 = ligneCalcul["montant_enfant_6"]

                        if ligneCalcul["temps_facture"] != None and ligneCalcul["temps_facture"] != "" :
                            temps_facture = HeureStrEnTime(ligneCalcul["temps_facture"]) 
                            temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                        else :
                            temps_facture = SoustractionHeures(heure_fin_max, heure_debut_min)

                        heure_debut_delta = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
                        heure_fin_delta = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
                        duree_delta = heure_fin_delta - heure_debut_delta
                        
                        # Cr�ation du label personnalis�
                        label = ligneCalcul["label"]
                        if label != None and label != "" :
                            if "{TEMPS_REALISE}" in label : 
                                label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree_delta))
                            if "{TEMPS_FACTURE}" in label : 
                                label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                            if "{HEURE_DEBUT}" in label : 
                                label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                            if "{HEURE_FIN}" in label : 
                                label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                            nom_tarif = label
                        break


            # Recherche combien d'individus de la famille sont d�j� pr�sents
            # ce jour-l� ou au d�but du forfait
            listeIndividusPresents = set()
            listePrestationsConcernees = []
            for IDprestation, dictValeurs in self.dictPrestations.items() :
                if (dictValeurs["IDfamille"] == IDfamille and
                    dictValeurs["IDtarif"] == IDtarif and
                    dictValeurs["IDindividu"] != IDindividu and (
                        dictValeurs["date"] == date or (
                            dictValeurs["forfait_date_debut"] and
                            dictValeurs["forfait_date_debut"] >= date and
                            dictValeurs["forfait_date_fin"] < date))):
                    listeIndividusPresents.add(dictValeurs["IDindividu"])
            nbreIndividus = len(listeIndividusPresents) + 1

            # Recherche le tarif � appliquer � chaque individu
            if "degr" in methode_calcul :
                # Si tarif d�gressif diff�rent pour chaque individu
                tarifsDegr = []
                if montant_enfant_1 != None and montant_enfant_1 != 0.0 : tarifsDegr.append(montant_enfant_1)
                if montant_enfant_2 != None and montant_enfant_2 != 0.0 : tarifsDegr.append(montant_enfant_2)
                if montant_enfant_3 != None and montant_enfant_3 != 0.0 : tarifsDegr.append(montant_enfant_3)
                if montant_enfant_4 != None and montant_enfant_4 != 0.0 : tarifsDegr.append(montant_enfant_4)
                if montant_enfant_5 != None and montant_enfant_5 != 0.0 : tarifsDegr.append(montant_enfant_5)
                if montant_enfant_6 != None and montant_enfant_6 != 0.0 : tarifsDegr.append(montant_enfant_6)
                for x in range(0, 20) : tarifsDegr.append(0.0)
                montant_tarif = tarifsDegr[nbreIndividus-1]
            else:
                # Si tarif unique pour chacun des individus
                if nbreIndividus == 1 and montant_enfant_1 != None and montant_enfant_1 != 0.0 : montant_tarif = montant_enfant_1
                if nbreIndividus == 2 and montant_enfant_2 != None and montant_enfant_2 != 0.0 : montant_tarif = montant_enfant_2
                if nbreIndividus == 3 and montant_enfant_3 != None and montant_enfant_3 != 0.0 : montant_tarif = montant_enfant_3
                if nbreIndividus == 4 and montant_enfant_4 != None and montant_enfant_4 != 0.0 : montant_tarif = montant_enfant_4
                if nbreIndividus == 5 and montant_enfant_5 != None and montant_enfant_5 != 0.0 : montant_tarif = montant_enfant_5
                if nbreIndividus >= 6 and montant_enfant_6 != None and montant_enfant_6 != 0.0 : montant_tarif = montant_enfant_6

            # Modifie le tarif des autres individus de la famille
            index = 0
            for IDprestation, dictValeurs in self.dictPrestations.items() :
                if dictValeurs["date"] == date and dictValeurs["IDtarif"] == IDtarif and dictValeurs["IDfamille"] == IDfamille : #and dictValeurs["IDindividu"] != IDindividu :
                    
                    # Recherche du tarif � appliquer aux autres individus de la famille
                    if "degr" in methode_calcul :
                        montantTmp = 0.0
                        try :
                            montantTmp = tarifsDegr[index]
                            if montantTmp == None or montantTmp == "" : 
                                montantTmp = 0.0
                        except : pass
                    else:
                        montantTmp = montant_tarif

                    montantInitial = self.dictPrestations[IDprestation]["montant_initial"]
                    montantDeduction = montantInitial - self.dictPrestations[IDprestation]["montant"]
                    montantFinal = montantTmp - montantDeduction
                    self.dictPrestations[IDprestation]["montant_initial"] = montantTmp
                    self.dictPrestations[IDprestation]["montant"] = montantFinal

                    self.listePrestationsModifiees.append(IDprestation)
                    
                    # Modifie le montant affich� dans le volet Facturation
                    if self.mode == "individu" :
                        self.GetGrandParent().panel_facturation.ModifiePrestation(
                                        date=date, 
                                        IDindividu=dictValeurs["IDindividu"], 
                                        IDprestation=IDprestation, 
                                        montantVentilation=dictValeurs["montantVentilation"], 
                                        nouveauMontant=montantFinal,
                                        )
                    
                    index += 1
            


        # Recherche du montant du tarif : AU PRORATA DE LA DUREE (Montant unique + QF)
        if methode_calcul in ("duree_coeff_montant_unique", "duree_coeff_qf") :
            montant_tarif = 0.0
            tarifFound = False
            lignes_calcul = dictTarif["lignes_calcul"]

            # Recherche des heures debut et fin des unit�s coch�es
            duree, heure_debut_delta, heure_fin_delta = self.CalculeDuree(IDindividu, date, combinaisons_unites)
            duree_delta = heure_fin_delta - heure_debut_delta
            
            for ligneCalcul in lignes_calcul :
                qf_min = ligneCalcul["qf_min"]
                qf_max = ligneCalcul["qf_max"]
                duree_min = HeureStrEnDelta(ligneCalcul["duree_min"])
                duree_max = HeureStrEnDelta(ligneCalcul["duree_max"])
                duree_seuil = HeureStrEnDelta(ligneCalcul["duree_seuil"])
                duree_plafond = HeureStrEnDelta(ligneCalcul["duree_plafond"])
                unite_horaire = HeureStrEnDelta(ligneCalcul["unite_horaire"])
                montant_tarif_ligne = ligneCalcul["montant_unique"]
                montant_min = ligneCalcul["montant_min"]
                montant_max = ligneCalcul["montant_max"]

                montant_questionnaire = self.GetQuestionnaire(ligneCalcul["montant_questionnaire"], IDfamille, IDindividu)
                if montant_questionnaire not in (None, 0.0) :
                    montant_tarif_ligne = montant_questionnaire

                ajustement = ligneCalcul["ajustement"]

                if duree_min == None : 
                    duree_min = datetime.timedelta(0)
                if duree_max == None or duree_max == datetime.timedelta(0) : 
                    duree_max = datetime.timedelta(hours=23, minutes=59)
                
                # Condition QF
                conditionQF = True
                if methode_calcul == "duree_coeff_qf" :
                    QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            conditionQF = True
                        else:
                            conditionQF = False

                if duree_min <= duree <= duree_max and conditionQF == True :        
                    duree_temp = duree
                    # V�rifie dur�es seuil et plafond
                    if duree_seuil != None :
                        if duree_temp < duree_seuil : duree_temp = duree_seuil
                    if duree_plafond != None and duree_plafond.seconds > 0 :
                        if duree_temp > duree_plafond : duree_temp = duree_plafond
                    
                    # Calcul du tarif
                    nbre = int(math.ceil(1.0 * duree_temp.seconds / unite_horaire.seconds)) # Arrondi � l'entier sup�rieur
                    montant_tarif = nbre * montant_tarif_ligne
                    montant_tarif = float(decimal.Decimal(str(montant_tarif)))

                    # Montants seuil et plafond
                    if montant_min != None :
                        if montant_tarif < montant_min :
                            montant_tarif = montant_min
                    if montant_max != None :
                        if montant_tarif > montant_max :
                            montant_tarif = montant_max

                    # Application de l'ajustement (majoration ou d�duction)
                    if ajustement != None :
                        montant_tarif = montant_tarif + ajustement
                        if montant_tarif < 0.0 :
                            montant_tarif = 0.0

                    # Calcul du temps factur�
                    temps_facture = unite_horaire * nbre
                    
                    # Cr�ation du label personnalis�
                    label = ligneCalcul["label"]
                    if label != None and label != "" :
                        if "{QUANTITE}" in label : 
                            label = label.replace("{QUANTITE}", str(nbre))
                        if "{TEMPS_REALISE}" in label : 
                            label = label.replace("{TEMPS_REALISE}", DeltaEnStr(duree_temp))
                        if "{TEMPS_FACTURE}" in label : 
                            label = label.replace("{TEMPS_FACTURE}", DeltaEnStr(temps_facture))
                        if "{HEURE_DEBUT}" in label : 
                            label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                        if "{HEURE_FIN}" in label : 
                            label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                        nom_tarif = label
                                                
                    break


        # Recherche du montant du tarif : TAUX D'EFFORT
        if methode_calcul in ("taux_montant_unique", "taux_qf", "taux_date") :
            montant_tarif = 0.0
            lignes_calcul = dictTarif["lignes_calcul"]
            
            # Recherche QF de la famille
            QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
            
            for ligneCalcul in lignes_calcul :
                qf_min = ligneCalcul["qf_min"]
                qf_max = ligneCalcul["qf_max"]
                taux = ligneCalcul["taux"]
                montant_min = ligneCalcul["montant_min"]
                montant_max = ligneCalcul["montant_max"]
                ajustement = ligneCalcul["ajustement"]
                
                # V�rifie si QF ok pour le calcul bas� �galement sur paliers de QF
                conditions = True
                if methode_calcul == "taux_qf" :
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            conditions = True
                        else:
                            conditions = False

                if methode_calcul == "taux_date":
                    dateLigne = DateEngEnDateDD(ligneCalcul["date"])
                    if dateLigne != date :
                        conditions = False

                if conditions == True :
                
                    # Calcul du tarif
                    if QFfamille != None :
                        montant_tarif = QFfamille * taux
                        montant_tarif = float(decimal.Decimal(str(montant_tarif)))
                    else:
                        if montant_max != None :
                            montant_tarif = montant_max
                        
                    # Montants seuil et plafond
                    if montant_min != None :
                        if montant_tarif < montant_min :
                            montant_tarif = montant_min
                    if montant_max != None :
                        if montant_tarif > montant_max :
                            montant_tarif = montant_max

                    # Application de l'ajustement (majoration ou d�duction)
                    if ajustement != None :
                        montant_tarif = montant_tarif + ajustement
                        if montant_tarif < 0.0 :
                            montant_tarif = 0.0

                    # Cr�ation du label personnalis�
                    label = ligneCalcul["label"]
                    if label != None and label != "" :
                        if "{TAUX}" in label : 
                            label = label.replace("{TAUX}", str(taux))
                        nom_tarif = label
                        
                    break
            


        # Recherche du montant du tarif : PAR TAUX D'EFFORT ET PAR DUREE (+ QF)
        if methode_calcul in ("duree_taux_montant_unique", "duree_taux_qf") :
            montant_tarif = 0.0
            lignes_calcul = dictTarif["lignes_calcul"]
            
            # Recherche QF de la famille
            QFfamille = self.RechercheQF(dictTarif, IDfamille, date)
            
            # Recherche de la dur�e
            duree, heure_debut_delta, heure_fin_delta = self.CalculeDuree(IDindividu, date, combinaisons_unites)
            
            for ligneCalcul in lignes_calcul :
                qf_min = ligneCalcul["qf_min"]
                qf_max = ligneCalcul["qf_max"]
##                duree_min = HeureStrEnTime(ligneCalcul["duree_min"])
##                duree_max = HeureStrEnTime(ligneCalcul["duree_max"])
                duree_min = HeureStrEnDelta(ligneCalcul["duree_min"])
                duree_max = HeureStrEnDelta(ligneCalcul["duree_max"])
                temps_facture_ligne = ligneCalcul["temps_facture"]
                taux = ligneCalcul["taux"]
                montant_min = ligneCalcul["montant_min"]
                montant_max = ligneCalcul["montant_max"]
                ajustement = ligneCalcul["ajustement"]

##                if duree_min == None : duree_min = datetime.time(0, 0)
##                if duree_max == None or duree_max == datetime.time(0, 0) : duree_max = datetime.time(23, 59)

                if duree_min == None : 
                    duree_min = datetime.timedelta(0)
                if duree_max == None or duree_max == datetime.timedelta(0) : 
                    duree_max = datetime.timedelta(hours=23, minutes=59)

                # V�rifie si QF ok pour le calcul bas� �galement sur paliers de QF
                conditionQF = True
                if methode_calcul == "duree_taux_qf" :
                    if QFfamille != None :
                        if QFfamille >= qf_min and QFfamille <= qf_max :
                            conditionQF = True
                        else:
                            conditionQF = False
                
                if duree_min <= duree <= duree_max and conditionQF == True :
                
                    # Calcul du tarif
                    if QFfamille != None :
                        montant_tarif = QFfamille * taux
                        montant_tarif = float(decimal.Decimal(str(montant_tarif)))
                    else:
                        if montant_max != None :
                            montant_tarif = montant_max
                        
                    # Montants seuil et plafond
                    if montant_min != None :
                        if montant_tarif < montant_min :
                            montant_tarif = montant_min
                    if montant_max != None :
                        if montant_tarif > montant_max :
                            montant_tarif = montant_max

                    # Application de l'ajustement (majoration ou d�duction)
                    if ajustement != None :
                        montant_tarif = montant_tarif + ajustement
                        if montant_tarif < 0.0 :
                            montant_tarif = 0.0

                    # Calcul du temps factur�
                    if temps_facture_ligne != None and temps_facture_ligne != "" :
                        temps_facture = HeureStrEnTime(temps_facture_ligne) 
                        temps_facture = datetime.timedelta(hours=temps_facture.hour, minutes=temps_facture.minute)
                    else :
                        temps_facture = duree_max #datetime.timedelta(hours=duree_max.hour, minutes=duree_max.minute)

                    # Cr�ation du label personnalis�
                    label = ligneCalcul["label"]
                    if label != None and label != "" :
                        if "{TAUX}" in label : 
                            label = label.replace("{TAUX}", str(taux))
                        if "{HEURE_DEBUT}" in label : 
                            label = label.replace("{HEURE_DEBUT}", DeltaEnStr(heure_debut_delta))
                        if "{HEURE_FIN}" in label : 
                            label = label.replace("{HEURE_FIN}", DeltaEnStr(heure_fin_delta))
                        nom_tarif = label
                        
                    break

        # Si unit� de type QUANTITE
        if quantite != None :
            montant_tarif = montant_tarif * quantite
            nom_tarif = u"%d %s" % (quantite, nom_tarif)
        
        # Arrondit le montant � pour enlever les d�cimales en trop. Ex : 3.05678 -> 3.05
        montant_tarif = float(FloatToDecimal(montant_tarif, plusProche=True))

        # if montant_tarif == 0.0 :
        #     return False

        return montant_tarif, nom_tarif, temps_facture
                            
                        
    def TriTarifs(self, dictTarif1, dictTarif2, key="nbre_max_unites_combi") :
        """ Effectue un tri DECROISSANT des tarifs en fonction du nbre_max_unites_combi """
        if dictTarif1[key] < dictTarif2[key] : return 1
        elif dictTarif1[key] > dictTarif2[key] : return -1
        else: return 0

    def TriTarifs2(self, dictTarif1, dictTarif2, key="date_debut") :
        """ Effectue un tri DECROISSANT des tarifs en fonction du nbre_max_unites_combi """
        if dictTarif1[key] < dictTarif2[key] : return 1
        elif dictTarif1[key] > dictTarif2[key] : return -1
        else: return 0

    def TriTarifs3(self, dictTarif1, dictTarif2, key="type") :
        """ Effectue un tri sur le type pour FORFAIT """
        if dictTarif1[key] < dictTarif2[key] : return -1
        elif dictTarif1[key] > dictTarif2[key] : return 1
        else: return 0

    def ModifierPrestation(self, IDprestation=None):
        print(IDprestation)
        
    def SupprimerPrestation(self, IDprestation=None, categorie=""):
        del self.dictPrestations[IDprestation]
        self.listePrestationsSupprimees.append(IDprestation)
        
        try :
            if (IDprestation in self.GetGrandParent().panel_facturation.dictBranchesPrestations) == False :
                return
        except :
            pass
            
        try :
            self.GetGrandParent().panel_facturation.SaisiePrestation(
                    self.dictPrestations,
                    self.dictDeductions,
                    [],
                    [(IDprestation, categorie)],
                    self.listeSelectionIndividus,
                    self.listeActivites,
                    self.listePeriodes,
                    )
        except :
            pass
    

    
    def Imprimer(self, event=None):
        """ Impression des consommations """
        self.CreationPDF() 
        
    def CreationPDF(self, nomDoc=FonctionsPerso.GenerationNomDoc("RESERVATIONS", "pdf"), afficherDoc=True):
        # Recherche des num�ros d'agr�ments
        DB = GestionDB.DB() 
        req = """
        SELECT IDactivite, agrement, date_debut, date_fin
        FROM agrements
        ORDER BY date_debut
        """
        DB.ExecuterReq(req)
        listeAgrements = DB.ResultatReq()  
        DB.Close() 
        
        def isDateValide(date):
            for dateDebut, dateFin in self.listePeriodes :
                if date >= dateDebut and date <= dateFin :
                    return True
            return False
        
        def RechercheAgrement(IDactivite, date):
            for IDactiviteTmp, agrement, date_debut, date_fin in listeAgrements :
                if IDactivite == IDactiviteTmp and str(date) >= date_debut and str(date) <= date_fin :
                    return agrement
            return None

        # ---- Cr�ation d'un dict au format Individu>Activite>Date>Conso
        dictDonnees = {}

        # Parcours des individus
        for IDindividu, dictDates in self.dictConsoIndividus.items() :
            if IDindividu in self.listeSelectionIndividus :
                nom = self.dictIndividus[IDindividu]["nom"]
                prenom = self.dictIndividus[IDindividu]["prenom"]
                date_naiss = self.dictIndividus[IDindividu]["date_naiss"]
                sexe = DICT_CIVILITES[self.dictIndividus[IDindividu]["IDcivilite"]]["sexe"]
                
                # Parcours des dates
                for date, dictUnites in dictDates.items() :
                    if isDateValide(date) == True :
                        
                        # Parcours des conso
                        for IDunite, listeConso in dictUnites.items() :
                            for conso in listeConso :
                                IDactivite = conso.IDactivite
                                if IDactivite in self.listeActivites and conso.IDfamille == self.IDfamille:
                                    nomActivite = self.dictActivites[IDactivite]["nom"]
                                    agrement = RechercheAgrement(IDactivite, date)
                                    if agrement != None :
                                        agrement = _(u" - n� agr�ment : %s") % agrement
                    
                                    # M�morisation des donn�es
                                    if IDindividu not in dictDonnees:
                                        dictDonnees[IDindividu] = { "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "sexe":sexe, "activites":{}}
                                    if IDactivite not in dictDonnees[IDindividu]["activites"]:
                                        dictDonnees[IDindividu]["activites"][IDactivite] = {"nom":nomActivite, "agrement":agrement, "dates":{}}
                                    if date not in dictDonnees[IDindividu]["activites"][IDactivite]["dates"]:
                                        dictDonnees[IDindividu]["activites"][IDactivite]["dates"][date] = {"unites": {}}
                                    if not IDunite in dictDonnees[IDindividu]["activites"][IDactivite]["dates"][date]["unites"]:
                                        dictDonnees[IDindividu]["activites"][IDactivite]["dates"][date]["unites"][IDunite] = []

                                    # R�cup�ration des consommations
                                    nomUnite = self.dictUnites[IDunite]["nom"]
                                    ordreUnite = self.dictUnites[IDunite]["ordre"]
                                    typeUnite = self.dictUnites[IDunite]["type"]
                                    etat = conso.etat
                                    if etat == "reservation" : etat = _(u"R�servation")
                                    if etat == "absenti" : etat = _(u"Absence injustifi�e")
                                    if etat == "absentj" : etat = _(u"Absence justifi�e")
                                    if etat == "present" : etat = _(u"Pr�sent")
                                    if etat == "attente" : etat = _(u"Attente")
                                    if etat == "refus" : etat = _(u"Refus")
                                    IDgroupe = conso.IDgroupe
                                    IDprestation = conso.IDprestation
                                    heure_debut = conso.heure_debut
                                    heure_fin = conso.heure_fin
                                    
                                    # Recherche de la prestation associ�e � la conso
                                    if IDprestation != None and IDprestation in self.dictPrestations :
                                        prestation = {
                                            "montant": self.dictPrestations[IDprestation]["montant"],
                                            "label" : self.dictPrestations[IDprestation]["label"],
                                            "paye" : self.dictPrestations[IDprestation]["montantVentilation"],
                                            }
                                    else:
                                        prestation = None
                                    
                                    dictTemp = {
                                        "nomUnite":nomUnite, "ordreUnite":ordreUnite, "etat":etat, 
                                        "IDgroupe":IDgroupe, "IDprestation":IDprestation, "prestation":prestation,
                                        "type":typeUnite, "heure_debut":heure_debut, "heure_fin":heure_fin,
                                        "evenement": getattr(conso, "evenement", None),
                                    }
                                    dictDonnees[IDindividu]["activites"][IDactivite]["dates"][date]["unites"][IDunite].append(dictTemp)

        # Lancement de la cr�ation du PDF
        from Utils import UTILS_Impression_reservations
        dictChamps = UTILS_Impression_reservations.Impression(dictDonnees, nomDoc=nomDoc, afficherDoc=afficherDoc)
        return dictChamps
    
    def EnvoyerEmail(self, event=None):
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("CONSOMMATIONS", "pdf"), categorie="reservations")
        
        
        
##    def Modification_lot(self, dictParametres={}):
##        """ Modification par lot """
##        def TestDates(date):
##            for date_debut, date_fin
##        # Parcours les lignes
##        for numLigne, ligne in self.dictLignes.iteritems() :
##            # Parcours les cases
##            for numColonne, case in ligne.dictCases.iteritems() :
##                if case.typeCase == "consommation" :
##                    # V�rifie que les cases font partie de la s�lection
##                    valide = True
##                    if case.IDactivite != dictParametres["selection"]["activite"] : valide = False
##                    if case.IDgroupe not in dictParametres["selection"]["groupes"] : valide = False
##                    if case.IDunite not in dictParametres["selection"]["unites"] : valide = False
##                    if case.etat not in dictParametres["selection"]["modes"] : valide = False
##                    if case.IDgroupe not in dictParametres["selection"]["etats"] : valide = False
##                    
##        
##            "groupes" : selectionGroupes,
##            "unites" : selectionUnites,
##            "modes" : selectionModes,
##            "etats" : selectionEtats,
##            }
    
    def ConvertirEtat(self, event=None):
        """ Convertit toutes les conso selon les souhaits """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") == False : return

        # Demande les param�tres de la conversion
        from Dlg import DLG_Conversion_etat
        dlg = DLG_Conversion_etat.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            dictDonnees = dlg.GetDonnees()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        # Recherche les cases concern�es
        listeConso = []
        listeDates = []
        for numLigne, ligne in self.dictLignes.items() :
            if dictDonnees["option_lignes"] == "lignes_affichees" or (dictDonnees["option_lignes"] == "lignes_selectionnees" and ligne.coche == True):
                for numColonne, case in ligne.dictCases.items() :
                    if case.typeCase == "consommation" :
                        for conso in case.GetListeConso() :
                            if conso.etat == dictDonnees["code_etat_avant"] :
                                listeConso.append((case, conso))
                                listeDates.append(case.date)

        if len(listeConso) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune consommation ayant cet �tat !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que des dates ne sont pas dans une p�riode de gestion
        if self.gestion.Verification("consommations", listeDates) == False: return False

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous le changement d'�tat '%s' en '%s' pour %d consommations ?") % (dictDonnees["label_etat_avant"], dictDonnees["label_etat_apres"], len(listeConso)), _(u"Changement d'�tat"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Conversion
        for case, conso in listeConso :
            case.ModifieEtat(conso, dictDonnees["code_etat_apres"])

    
    def GetNbreDatesEtat(self, etat="refus"):
        nbre = 0
        for numLigne, ligne in self.dictLignes.items() :
            for numColonne, case in ligne.dictCases.items() :
                if case.typeCase == "consommation" :
                    for conso in case.GetListeConso() :
                        if conso.etat == etat :
                            nbre += 1
        return nbre
    
    def GetHistorique(self):
        return self.listeHistorique
    
    def RecalculerToutesPrestations(self, modeSilencieux=True, inclure_dates_fermees=False):
        """ Recalcule les prestations de toutes les cases """
        # V�rifie que la p�riode s�lectionn�e n'est pas dans une p�riode de gestion
        date_debut, date_fin = self.GetDatesExtremes(self.listePeriodes)
        if self.gestion.IsPeriodeinPeriodes("consommations", date_debut, date_fin) == False: return False

        listeDejaFactures = []
        for numLigne, ligne in self.dictLignes.items() :
            for numColonne, case in ligne.dictCases.items() :
                if case.typeCase == "consommation" and (case.ouvert == True or inclure_dates_fermees == True) :
                    dejaFacture = False
                    verrouillee = False
                    for conso in case.GetListeConso() :
                        if conso.IDprestation != None and conso.forfait == None :
                            if conso.IDfacture != None :
                                dejaFacture = True
                            if case.verrouillage == True or conso.verrouillage == True :
                                verrouillee = True
                    
                    if dejaFacture == True or verrouillee == True :
                        listeDejaFactures.append(case.IDprestation)
                    else :
                        case.MAJ_facturation(modeSilencieux=modeSilencieux)
                        case.Refresh() 
                    
        if len(listeDejaFactures) > 0 and modeSilencieux == False :
            dlg = wx.MessageDialog(self, _(u"Notez que %d prestations n'ont pas �t� recalcul�s car \ncelles-ci apparaissent d�j� sur des factures ou sont verrouill�es !") % len(listeDejaFactures), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
    
    
    def RechercheTransportsIndividu(self, dictionnaire={}, IDindividu=None, IDtransport=None):
        """ Recherche si un transport a d�j� �t� import� dans le dictionnaire donn� """
        if IDindividu in dictionnaire :
            for IDtransp, dictTemp in dictionnaire[IDindividu].items() :
                if IDtransp == IDtransport :
                    return True
        return False
    
    def RechercheTransports(self, IDindividu=None, date=None):
        """ Recherche les transports pour une date et un individu """
        dictTransports = {}
        if IDindividu in self.dict_transports :
            for IDtransp, dictTemp in self.dict_transports[IDindividu].items() :
                if dictTemp["depart_date"] == date or dictTemp["arrivee_date"] == date :
                    dictTransports[IDtransp] = dictTemp
        return dictTransports
    
    def ProgrammeTransports(self, IDindividu, date, ligne):
        """ Programme un transport """
        try :
            dictUnites = self.dictConsoIndividus[IDindividu][date]
        except :
            return
        
        # Recherche les unit�s de la ligne
        listeUnitesUtilisees = []
        for IDunite, listeConso in dictUnites.items() :
            for conso in listeConso :
                if conso.etat in ("reservation", "present", "absenti") : # ici, le 'absenti' permet de facturer aussi si absence injustifi�e
                    listeUnitesUtilisees.append(IDunite)
        
        def RechercheProgValide(dictProg):
            """ Recherche une prog valide """
            # Validation si actif
            if dictProg["actif"] == 0 :
                return False
            
            # Validation des dates
            if date < dictProg["date_debut"] or date > dictProg["date_fin"] :
                return False
            
            # Jours scolaires / vacances
            if self.EstEnVacances(date) == True :
                if date.weekday() not in dictProg["jours_vacances"] :
                    return False
            else :
                if date.weekday() not in dictProg["jours_scolaires"] :
                    return False
            
            # Unit�s
            valide = False
            for IDunite in listeUnitesUtilisees :
                if IDunite in dictProg["unites"] :
                    valide = True
            if valide == False : return False
            
            return True
        
        def RechercheTransportExistant(IDprog=None, date=None):
            if IDindividu in self.dict_transports :
                for IDtransport, dictTemp in self.dict_transports[IDindividu].items() :
                    if dictTemp["prog"] == IDprog and dictTemp["depart_date"] == date :
                        return True
            return False
            
        # Recherche si une programmation existe pour cet individu, cette date et ces unit�s
        if IDindividu in self.dict_transports_prog:
            for IDprog, dictProg in self.dict_transports_prog[IDindividu].items() :

                # Cr�ation
                if RechercheProgValide(dictProg) == True and RechercheTransportExistant(dictProg["IDtransport"], date) == False :
                    self.CreationTransportProg(dictProg, date)
                
                # Suppression
                if RechercheProgValide(dictProg) == False and RechercheTransportExistant(dictProg["IDtransport"], date) == True :
                    self.SuppressionTransportProg(dictProg, date)
                    
        # MAJ de l'affichage
        caseTransports = ligne.RechercheCase("transports")
        if caseTransports != None :
            caseTransports.MAJ() 
                    
    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def EstFerie(self, dateDD):
        jour = dateDD.day
        mois = dateDD.month
        annee = dateDD.year        
        for type, nom, jourTmp, moisTmp, anneeTmp in self.listeFeries :
            jourTmp = int(jourTmp)
            moisTmp = int(moisTmp)
            anneeTmp = int(anneeTmp)
            if type == "fixe" :
                if jourTmp == jour and moisTmp == mois :
                    return True
            else:
                if jourTmp == jour and moisTmp == mois and anneeTmp == annee :
                    return True
        return False

    def CreationTransportProg(self, dictProg={}, date=None):
        """ Cr�ation d'un transport """
        dictTemp = copy.deepcopy(dictProg)
        IDtransport = self.RechercheProchainIDtransport() 
        IDindividu = dictProg["IDindividu"]
        dictTemp["mode"] = "TRANSP"
        dictTemp["prog"] = dictTemp["IDtransport"]
        dictTemp["IDtransport"] = IDtransport
        dictTemp["depart_date"] = date
        dictTemp["arrivee_date"] = date
        dictTemp["etat"] = None
        if (IDindividu in self.dict_transports) == False :
            self.dict_transports[IDindividu] = {}
        self.dict_transports[IDindividu][IDtransport] = dictTemp
    
    def RechercheProchainIDtransport(self):
        ID = self.prochainIDtransport 
        self.prochainIDtransport -= 1
        return ID

    def SuppressionTransportProg(self, dictProg={}, date=None):
        """ Suppression d'un transport """
        listeSuppression = []
        for IDtransport, dictTemp in self.dict_transports[dictProg["IDindividu"]].items() :
            if dictTemp["prog"] == dictProg["IDtransport"] and dictTemp["depart_date"] == date :
                listeSuppression.append(IDtransport)
        for IDtransport in listeSuppression :
            del self.dict_transports[dictTemp["IDindividu"]][IDtransport]
            

    def VerificationCotisations(self, listeCotisations=[], date=None, IDindividu=None, IDfamille=None):
        """ V�rifie si l'individu a l'une des cotisations indiqu�es � jour � la date donn�e """
        # Recherche des cotisations valides pour l'individu ou la famille
        DB = GestionDB.DB()
        req = """SELECT IDcotisation, IDtype_cotisation, date_debut, date_fin
        FROM cotisations 
        WHERE date_debut<='%s' AND date_fin>='%s'
        AND ( (IDfamille=%d AND IDindividu IS NULL) OR (IDindividu=%d AND IDfamille IS NULL) )
        ;""" % (date, date, IDfamille, IDindividu)
        DB.ExecuterReq(req)
        listeCotisationsValides = DB.ResultatReq()
        DB.Close()
        
        # Analyse
        for IDcotisation, IDtype_cotisation, date_debut, date_fin in listeCotisationsValides :
            if IDtype_cotisation in listeCotisations :
                return True
        return False

    def VerificationCaisses(self, listeCaisses=[], IDfamille=None):
        """ V�rifie si la famille a l'une des caisses donn�es """
        # Recherche de la caisse de la famille
        DB = GestionDB.DB()
        req = """SELECT IDfamille, IDcaisse
        FROM familles 
        WHERE IDfamille=%d
        ;""" % IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Analyse
        for IDfamille, IDcaisse in listeDonnees :
            if IDcaisse == None : IDcaisse = 0
            if IDcaisse in listeCaisses :
                return True
        return False

    def VerificationFiltres(self, listeFiltres=[], date=None, IDindividu=None, IDfamille=None):
        """ V�rifie si l'individu ou la famille a les filtres valides """
        DB = GestionDB.DB()
        
        validation = True
        for dictFiltre in listeFiltres :
            IDquestion = dictFiltre["IDquestion"]
            defaut = dictFiltre["defaut"]
            listeReponses = []

            # Recherche les r�ponses
            if dictFiltre["type"] == "individu" :
                req = """SELECT IDreponse, reponse
                FROM questionnaire_reponses
                WHERE IDquestion=%d AND IDindividu=%d;""" % (IDquestion, IDindividu)
                DB.ExecuterReq(req)
                listeReponses = DB.ResultatReq()     

            if dictFiltre["type"] == "famille" :
                req = """SELECT IDreponse, reponse
                FROM questionnaire_reponses
                WHERE IDquestion=%d AND IDfamille=%d;""" % (IDquestion, IDfamille)
                DB.ExecuterReq(req)
                listeReponses = DB.ResultatReq()     

            # Si aucune r�ponse enregistr�e, on r�cup�re la valeur par d�faut
            if len(listeReponses) == 0 :
                listeReponses = [(None, defaut)]

            # Compare le filtre avec les r�ponses
            for IDreponse, reponse in listeReponses :
                resultat = UTILS_Filtres_questionnaires.Filtre(controle=dictFiltre["controle"], choix=dictFiltre["choix"], criteres=dictFiltre["criteres"], reponse=reponse)
                if resultat == False :
                    validation = False

        DB.Close() 

        return validation

    def VerificationPeriodes(self, jours_scolaires, jours_vacances, date):
        """ V�rifier si jour scolaire ou vacances """
        valide = False
        # Jours scolaires
        if jours_scolaires != None :
            if self.EstEnVacances(date) == False :
                if date.weekday() in jours_scolaires :
                    valide = True
        # Jours vacances
        if jours_vacances != None :
            if self.EstEnVacances(date) == True :
                if date.weekday() in jours_vacances :
                    valide = True
        return valide
        
    def TraitementLot(self):
        """ Traitement par lot """
        # R�cup�ration des donn�es par d�faut
        listeIndividus = self.listeIndividusFamille
        date_debut = None
        date_fin = None
        dates_extremes = self.GetDatesExtremes(self.listePeriodes)
        if dates_extremes[0] != datetime.date(1970, 1, 1) :
            date_debut, date_fin = dates_extremes
        
        # Fen�tre de saisie
        from Dlg import DLG_Saisie_lot_conso
        dlg = DLG_Saisie_lot_conso.Dialog(self, listeIndividus=listeIndividus, date_debut=date_debut, date_fin=date_fin)
        if dlg.ShowModal() == wx.ID_OK :
            resultats = dlg.GetResultats() 
        else :
            resultats = None
        dlg.Destroy()
        if resultats == None :
            return

        # V�rifie que la p�riode s�lectionn�e n'est pas dans une p�riode de gestion
        if self.gestion.IsPeriodeinPeriodes("consommations", resultats["date_debut"], resultats["date_fin"]) == False: return False

        # ------ Processus du traitement par lot -----
        dlg_grille = self.GetGrandParent()
        
        try :
            # dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant la proc�dure..."), None)
            # wx.Yield()

            # S�lection des individus
            listeIndividus = []
            dictIndividus = {}
            for dictIndividu in resultats["individus"] :
                listeIndividus.append(dictIndividu["IDindividu"])
                dictIndividus[dictIndividu["IDindividu"]] = dictIndividu
            
            dlg_grille.panel_individus.DeselectTout()
            dlg_grille.panel_individus.SetSelections(listeIndividus)
            dlg_grille.SetListeSelectionIndividus(listeIndividus)
            
            # S�lection de la p�riode
            date_debut = resultats["date_debut"]
            date_fin = resultats["date_fin"]
            dictPeriode = {
                "page" : 3,
                "listeSelections" : [],
                "annee" : None,
                "dateDebut" : date_debut,
                "dateFin" : date_fin,
                "listePeriodes" : [(date_debut, date_fin),],
                }
            dlg_grille.panel_periode.SetDictDonnees(dictPeriode)
            dlg_grille.SetListesPeriodes([(date_debut, date_fin),])

            # MAJ de la grille
            dlg_grille.MAJ_grille()
            
            # Processus
            journal = self.TraitementLot_processus(resultats=resultats) 
            
            # del dlgAttente

        except Exception as err:
            # del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"D�sol�, le probl�me suivant a �t� rencontr� dans le traitement par lot des consommations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Formatage du texte de r�sultats
        texte = _(u"<B>La proc�dure de traitement par lot est termin�e mais les incidents suivants ont �t� rencontr�s :</B><BR><BR>")
        
        afficher = False
        for IDindividu, listeActions in journal.items() :
            if len(listeActions) > 0 :
                afficher = True
                
                nomIndividu = dictIndividus[IDindividu]["label"]
                texte += u"<U>%s :</U><BR><BR>" % nomIndividu
                
                texte += "<UL>"
                for date, nomUnite, action in listeActions :
                    texte += u"<LI>%s - %s : %s.</LI>" % (DateEngFr(str(date)), nomUnite, action)
                texte += "</UL><BR><BR>"
            
        # Affichage des r�sultats
        if afficher == True :
            from Dlg import DLG_Message_html
            dlg = DLG_Message_html.Dialog(self, texte=u"<FONT SIZE=2>%s</FONT>" % texte, titre=_(u"R�sultats du traitement par lot"), size=(630, 450))
            dlg.ShowModal()
            dlg.Destroy()


    def TraitementLot_processus(self, resultats={}):
        """ Processus du traitement par lot """
        journal = {}

        # Recherche les individus impact�s
        listeIndividus = []
        for dictIndividu in resultats["individus"] :
            listeIndividus.append(dictIndividu["IDindividu"])

        # Parcours les lignes
        for numLigne, ligne in self.dictLignes.items() :
            for numColonne, case in ligne.dictCases.items() :
                if case.typeCase == "consommation" :
                    
                    # V�rifie si ouvert
                    if case.ouvert == True :
                        
                        if (case.IDindividu in journal) == False :
                            journal[case.IDindividu] = []
                            
                        # V�rifie si la date est valide selon les crit�res
                        if case.date in resultats["dates"] and case.IDindividu in listeIndividus :
                            valide = True
                        else :
                            valide = False

                        if valide == True :

                            # -------------------- Saisie -------------------
                            if resultats["action"] == "saisie" :
                                for dictUnite in resultats["unites"] :

                                    if dictUnite["IDunite"] == case.IDunite :
                                        IDunite = dictUnite["IDunite"]
                                        nomUnite = dictUnite["nom"]
                                        heure_debut = None
                                        heure_fin = None
                                        quantite = None
                                        
                                        # if dictUnite["type"] in ("Horaire", "Multihoraires") :
                                        #     heure_debut = dictUnite["options"]["heure_debut"]
                                        #     heure_fin = dictUnite["options"]["heure_fin"]
                                        #
                                        # if dictUnite["type"] == "Quantite" :
                                        #     quantite = dictUnite["options"]["quantite"]

                                        heure_debut_defaut = self.dictUnites[IDunite]["heure_debut"]
                                        heure_fin_defaut = self.dictUnites[IDunite]["heure_fin"]

                                        if "heure_debut" in dictUnite["options"] :
                                            heure_debut = dictUnite["options"]["heure_debut"]

                                            if heure_debut != None and heure_debut_defaut != None :
                                                if heure_debut < heure_debut_defaut  or heure_debut > heure_fin_defaut :
                                                    heure_debut = heure_debut_defaut

                                        if "heure_fin" in dictUnite["options"] :
                                            heure_fin = dictUnite["options"]["heure_fin"]

                                            if heure_fin != None and heure_fin_defaut != None :
                                                if heure_fin > heure_fin_defaut or heure_fin < heure_debut_defaut :
                                                    heure_fin = heure_fin_defaut

                                            if heure_debut != None and heure_fin != None and heure_debut > heure_debut :
                                                heure_debut = heure_fin

                                        if "quantite" in dictUnite["options"] :
                                            quantite = dictUnite["options"]["quantite"]

                                        valide = True

                                        # V�rifie qu'il est possible de placer une conso dans cette case
                                        if dictUnite["type"] != "Evenement" and case.IsCaseDisponible(heure_debut, heure_fin) == False :
                                            journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Une consommation est d�j� enregistr�e")))
                                            valide = False

                                        # V�rifie qu'il reste des places disponibles
                                        if dictUnite["type"] != "Evenement" and case.HasPlaceDisponible(heure_debut, heure_fin) == False :
                                            journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Plus de places")))
                                            valide = False

                                        # V�rifie la compatibilit� avec les autres unit�s
                                        incompatibilite = case.VerifieCompatibilitesUnites()
                                        if incompatibilite != None :
                                            nomUniteIncompatible = self.dictUnites[incompatibilite]["nom"]
                                            journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Incompatibilit� avec l'unit� '%s' d�j� enregistr�e") %  nomUniteIncompatible))
                                            valide = False

                                        # Saisie d'une conso
                                        if valide == True :

                                            if dictUnite["type"] == "Multihoraires" :
                                                barre = case.SaisieBarre(UTILS_Dates.HeureStrEnTime(heure_debut), UTILS_Dates.HeureStrEnTime(heure_fin), etiquettes=resultats["etiquettes"])
                                                # Modifie �tat
                                                if resultats["etat"] != None and barre.conso.etat != resultats["etat"] :
                                                    case.ModifieEtat(barre.conso, resultats["etat"])

                                            elif dictUnite["type"] == "Evenement":
                                                for evenement in case.liste_evenements :
                                                    if resultats["expression"] == None or resultats["expression"].lower() in evenement.nom.lower():
                                                        if case.IsCaseDisponible(evenement) :
                                                            if case.HasPlaceDisponible(evenement) :
                                                                case.Ajouter_evenement(evenement=evenement, etiquettes=resultats["etiquettes"])
                                                                # Modifie �tat
                                                                if resultats["etat"] != None and evenement.conso.etat != resultats["etat"]:
                                                                    case.ModifieEtat(evenement.conso, resultats["etat"])

                                            else :
                                                case.OnClick(saisieHeureDebut=heure_debut, saisieHeureFin=heure_fin, saisieQuantite=quantite, modeSilencieux=True, etiquettes=resultats["etiquettes"])
                                                # Modifie �tat
                                                if resultats["etat"] != None and case.etat != resultats["etat"] :
                                                    case.ModifieEtat(None, resultats["etat"])

            
                            # -------------------- Modification -------------------
                            if resultats["action"] == "modification" :
                                
                                index = 0
                                for dictUnite in resultats["unites"] :
                                    if dictUnite["IDunite"] == case.IDunite :
                                        listeConso = case.GetListeConso()
                                        if index <= len(listeConso) - 1 :
                                            conso = listeConso[index]

                                            if conso.etat != None :
                                                
                                                if conso.IDfacture != None :
                                                    journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Interdit de modifier une consommation d�j� factur�e")))
                                                    
                                                elif conso.etat in ("present", "absentj", "absenti") :
                                                    journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Interdit de modifier une consommation d�j� point�e")))
                                                
                                                elif conso.forfait != None :
                                                    journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Interdit de modifier un forfait")))
                                                    
                                                else :
                                                    # Modifie les heures 
                                                    if dictUnite["type"] == "Horaire" :
                                                        heure_debut = dictUnite["options"]["heure_debut"]
                                                        heure_fin = dictUnite["options"]["heure_fin"]
                                                        case.OnClick(saisieHeureDebut=heure_debut, saisieHeureFin=heure_fin, modeSilencieux=True, etiquettes=resultats["etiquettes"])
                                                    
                                                    # Modifie Quantit� si unit� de type Quantit�
                                                    if dictUnite["type"] == "Quantite" :
                                                        quantite = conso.quantite
                                                        if conso.quantite == None :
                                                            quantite = 1
                                                        quantite += 1
                                                        case.OnClick(saisieQuantite=quantite, modeSilencieux=True, etiquettes=resultats["etiquettes"])

                                                    # Modifie Multihoraires
                                                    if dictUnite["type"] == "Multihoraires" :
                                                        heure_debut = dictUnite["options"]["heure_debut"]
                                                        heure_fin = dictUnite["options"]["heure_fin"]
                                                        conso.case.ModifierBarre(conso.barre, horaires=(heure_debut, heure_fin), etiquettes=resultats["etiquettes"])

                                        index += 1
        
                            # -------------------- Suppression -------------------
                            if resultats["action"] == "suppression" :
                                for dictUnite in resultats["unites"] :
                                    if dictUnite["IDunite"] == case.IDunite :
                                        for conso in case.GetListeConso() :
                                            
                                            if len(resultats["etiquettes"]) == 0 or len(set(conso.etiquettes) & set(resultats["etiquettes"])) > 0 :
                                                
                                                if conso.IDfacture != None :
                                                    journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Interdit de modifier une consommation d�j� factur�e")))
                                                elif conso.etat in ("present", "absentj", "absenti") :
                                                    journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Interdit de modifier une consommation d�j� point�e")))
                                                elif conso.forfait != None :
                                                    journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Impossible de modifier un forfait")))
                                                else :
                                                    if dictUnite["type"] == "Multihoraires" :
                                                        case.SupprimerBarre(conso.barre)
                                                    elif dictUnite["type"] == "Evenement" :
                                                        if "expression" in resultats and (resultats["expression"] == None or resultats["expression"].lower() in conso.evenement.nom.lower()):
                                                            case.Supprimer_evenement(conso.evenement)
                                                    else :
                                                        if conso.etat != None :
                                                            case.OnClick(modeSilencieux=True, ForcerSuppr=True)
                    
                            # -------------------- Changement d'�tat -------------------
                            if resultats["action"] == "etat" :
                                for dictUnite in resultats["unites"] :
                                    if dictUnite["IDunite"] == case.IDunite :
                                        for conso in case.GetListeConso() :
                                            
                                            if len(resultats["etiquettes"]) == 0 or len(set(conso.etiquettes) & set(resultats["etiquettes"])) > 0 :
                                                
                                                if conso.etat != None :
                                                    if resultats["etat"] != None and conso.etat != resultats["etat"] :
                                                        if conso.IDfacture != None :
                                                            journal[case.IDindividu].append((case.date, dictUnite["nom"], _(u"Impossible de supprimer une consommation d�j� factur�e")))
                                                        else :
                                                            if dictUnite["type"] != "Evenement" or ("expression" in resultats and (resultats["expression"] == None or resultats["expression"].lower())) in conso.evenement.nom.lower() :
                                                                case.ModifieEtat(conso, resultats["etat"])
        
        # Renvoie le journal
        return journal

    def ResolveFormule(self, formule="", dictVariables={}):
        # Remplacement de variables pr�d�finies
        #print formule
        for variable, valeur in dictVariables.items() :
            formule = formule.replace(variable, valeur.__repr__())
        # Replacement des variables utilisateurs
        formule = re.sub(r'\"([0-9][0-9]):([0-9][0-9])\"', sub, formule)
        # R�solution de la formule
        try :
            resultat = eval(formule)
        except Exception as err :
            resultat = None
        #print "Formule : ", formule, " -> resultat =", resultat
        return resultat

    def Autogeneration(self, ligne=None, IDactivite=None, IDunite=None):
        """ Autog�n�ration de consommations """
        #print "------ Recherche d'unites autogenerees"

        # Recherche s'il existe des unit�s auto-g�n�r�es
        listeUnitesAuto = []
        for dictUnite in self.dictListeUnites[IDactivite] :
            if dictUnite["autogen_active"] == 1 :
                listeUnitesAuto.append(dictUnite)

                # V�rifie que l'unit� qui fait l'appel n'est pas elle-m�me auto-g�n�r�e
                if IDunite == dictUnite["IDunite"] :
                    return

        if len(listeUnitesAuto) == 0 :
            return

        #print "------ Application de l'unite autogeneree"

        # Recherche les cases de la ligne
        dictCasesUnites = {}
        for numColonne, case in ligne.dictCases.items() :
            if case.typeCase == "consommation" and case.IDactivite == IDactivite :
                dictCasesUnites[case.IDunite] = case

        # Calcule les variables
        dictVariables = {}
        for IDunite, case in dictCasesUnites.items():
            heure_debut = HeureStrEnDelta("00:00")
            heure_fin = HeureStrEnDelta("00:00")
            duree = HeureStrEnDelta("00:00")
            etat = None

            for conso in case.GetListeConso() :
                if conso.etat != None :
                    heure_debut_conso = HeureStrEnDelta(conso.heure_debut)
                    heure_fin_conso = HeureStrEnDelta(conso.heure_fin)
                    duree_conso = heure_fin_conso - heure_debut_conso

                    # Heure min
                    if heure_debut_conso < heure_debut or heure_debut == HeureStrEnDelta("00:00"):
                        heure_debut = heure_debut_conso

                    # Heure_max
                    if heure_fin_conso > heure_fin :
                        heure_fin = heure_fin_conso

                    # Dur�e
                    duree += duree_conso

                    # Etat
                    etat = conso.etat

            # M�morisation des r�sultats
            dictVariables["{HEUREDEBUT_UNITE%d}" % IDunite] = heure_debut
            dictVariables["{HEUREFIN_UNITE%d}" % IDunite] = heure_fin
            dictVariables["{DUREE_UNITE%d}" % IDunite] = duree
            dictVariables["{ETAT_UNITE%d}" % IDunite] = etat

        # Traite chaque unit� auto-g�n�r�e
        for dictUnite in listeUnitesAuto :

            # V�rifie si les conditions sont r�unies
            conditions = dictUnite["autogen_conditions"]
            if conditions != None :
                listeConditions = conditions.split(";")
            else :
                listeConditions = []

            valide = True
            if len(listeConditions) == 0 :
                valide = False

            for condition in listeConditions :
                # V�rifie que la condition est valide
                if self.ResolveFormule(condition, dictVariables) != True :
                    valide = False

            # Pr�pare les param�tres de la conso � saisir ou � supprimer
            dictParametres = {
                "dates" : [ligne.date,],
                "description" : u"Auto-g�n�ration",
                "IDactivite" : IDactivite,
                "date_fin" : [ligne.date,],
                "date_debut" : [ligne.date,],
                "jours_scolaires" : [0, 1, 2, 3, 4, 5, 6],
                "jours_vacances" : [0, 1, 2, 3, 4, 5, 6],
                "semaines" : 1,
                "feries" : True,
                "individus" : [{"selection" : True, "IDindividu" : ligne.IDindividu},],
                "unites" : [{"nom" : dictUnite["nom"],"type" : dictUnite["type"],"IDunite" : dictUnite["IDunite"],"options" : {}},],
            }

            # V�rifie si une conso existe d�j� :
            consoExists = dictVariables["{ETAT_UNITE%d}" % dictUnite["IDunite"]] != None
            #print "consoExists=", consoExists

            # Si toutes les conditions sont valides
            if valide == True :

                # R�cup�ration des param�tres de l'unit� auto-g�n�r�e
                parametres = dictUnite["autogen_parametres"]
                if parametres not in ("", None) :

                    listeDonnees = parametres.split("##")
                    for donnee in listeDonnees :
                        champ, valeur = donnee.split(":=")

                        if champ == "ETIQUETTES" and valeur != None :
                            etiquettes = UTILS_Texte.ConvertStrToListe(valeur)
                            dictParametres["etiquettes"] = etiquettes

                        if champ == "ETAT" and valeur != None :
                            dictParametres["etat"] = valeur

                        if champ == "QUANTITE" and valeur != None :
                            if valeur != "1" :
                                dictParametres["unites"][0]["options"]["quantite"] = int(valeur)

                        if champ == "HEUREDEBUT" and valeur != None :
                            if "FORMULE:" in valeur :
                                formule = valeur.replace("FORMULE:", "")
                                heure_debut = self.ResolveFormule(formule, dictVariables)
                            else :
                                heure_debut = HeureStrEnDelta(valeur)
                            #print "heure_debut=", DeltaEnStr(heure_debut, separateur=":")
                            dictParametres["unites"][0]["options"]["heure_debut"] = DeltaEnStr(heure_debut, separateur=":")

                        if champ == "HEUREFIN" and valeur != None :
                            if "FORMULE:" in valeur :
                                formule = valeur.replace("FORMULE:", "")
                                heure_fin = self.ResolveFormule(formule, dictVariables)
                            else :
                                heure_fin = HeureStrEnDelta(valeur)
                            #print "heure_fin=", DeltaEnStr(heure_fin, separateur=":")
                            dictParametres["unites"][0]["options"]["heure_fin"] = DeltaEnStr(heure_fin, separateur=":")

                    # Action
                    if consoExists :
                        dictParametres["action"] = "modification"
                    else :
                        dictParametres["action"] = "saisie"

                    # Traitement par lot
                    journal = self.TraitementLot_processus(dictParametres)
                    #print "journal =", journal

            if valide == False and consoExists :
                dictParametres["action"] = "suppression"
                dictParametres["etiquettes"] = []
                journal = self.TraitementLot_processus(dictParametres)
                #print "journal =", journal


####SAUVEGARDE

    def Sauvegarde(self):
        """ Sauvegarde des donn�es """
        DB = GestionDB.DB()

        # -------------- Sauvegarde du DictPrestations ----------------

        # Version optimis�e de la saisie des nouvelles prestations
        prochainID = DB.GetProchainID("prestations")

        dictNewIDprestation = {}
        listeAjoutsPrestations = []
        listeChampsPrestations = []
        listeAjoutsDeductions = []
        listeChampsDeductions = []
        for IDprestation, dictValeurs in self.dictPrestations.items() :
            if IDprestation < 0 :
                listeDonnees = [
                    ("IDcompte_payeur", dictValeurs["IDcompte_payeur"]),
                    ("date", str(dictValeurs["date"])),
                    ("categorie", dictValeurs["categorie"]),
                    ("label", dictValeurs["label"]),
                    ("montant_initial", dictValeurs["montant_initial"]),
                    ("montant", dictValeurs["montant"]),
                    ("IDactivite", dictValeurs["IDactivite"]),
                    ("IDtarif", dictValeurs["IDtarif"]),
                    ("IDfacture", dictValeurs["IDfacture"]),
                    ("IDfamille", dictValeurs["IDfamille"]),
                    ("IDindividu", dictValeurs["IDindividu"]),
                    ("temps_facture", dictValeurs["temps_facture"]),
                    ("IDcategorie_tarif", dictValeurs["IDcategorie_tarif"]),
                    ("forfait_date_debut", dictValeurs["forfait_date_debut"]),
                    ("forfait_date_fin", dictValeurs["forfait_date_fin"]),
                    ("code_compta", dictValeurs["code_compta"]),
                    ("code_produit_local", dictValeurs["code_produit_local"]),
                    ("tva", dictValeurs["tva"]),
                    ("date_valeur", str(datetime.date.today())),
                    ]

                # M�morisation de la prestation � ajouter
                listeValeurs = []
                for key, valeur in listeDonnees :
                    if key not in listeChampsPrestations :
                        listeChampsPrestations.append(key)
                    listeValeurs.append(valeur)

                listeAjoutsPrestations.append(listeValeurs)
                newIDprestation = copy.copy(prochainID)
                dictNewIDprestation[IDprestation] = newIDprestation

                # Sauvegarde des d�ductions
                if IDprestation in self.dictDeductions :
                    for dictDeduction in self.dictDeductions[IDprestation] :
                        listeDonnees = [
                            ("IDprestation", newIDprestation),
                            ("IDcompte_payeur", dictValeurs["IDcompte_payeur"]),
                            ("date", str(dictValeurs["date"])),
                            ("montant", dictDeduction["montant"]),
                            ("label", dictDeduction["label"]),
                            ("IDaide", dictDeduction["IDaide"]),
                            ]

                        # M�morisation de la d�duction � ajouter
                        listeValeurs = []
                        for key, valeur in listeDonnees :
                            if key not in listeChampsDeductions :
                                listeChampsDeductions.append(key)
                            listeValeurs.append(valeur)

                        listeAjoutsDeductions.append(listeValeurs)

                # Passe au prochain IDprestation
                prochainID += 1

        # Ajout optimis� des prestations
        if len(listeAjoutsPrestations) > 0 :
            texteChampsTemp = ", ".join(listeChampsPrestations)
            listeInterrogations = []
            for champ in listeChampsPrestations :
                listeInterrogations.append("?")
            texteInterrogations = ", ".join(listeInterrogations)
            DB.Executermany("INSERT INTO prestations (%s) VALUES (%s)" % (texteChampsTemp, texteInterrogations), listeAjoutsPrestations, commit=False)

        # Ajout optimis� des d�ductions
        if len(listeAjoutsDeductions) > 0 :
            texteChampsTemp = ", ".join(listeChampsDeductions)
            listeInterrogations = []
            for champ in listeChampsDeductions :
                listeInterrogations.append("?")
            texteInterrogations = ", ".join(listeInterrogations)
            DB.Executermany("INSERT INTO deductions (%s) VALUES (%s)" % (texteChampsTemp, texteInterrogations), listeAjoutsDeductions, commit=False)


        # ------------- Sauvegarde des prestations modifi�es ------------------
        listeModifications = []
        listeSuppressions = []
        for IDPrestationModif in self.listePrestationsModifiees :
            if IDPrestationModif > 0 and IDPrestationModif in self.dictPrestations :
                # Sauvegarde de la prestation
                dictValeurs = self.dictPrestations[IDPrestationModif]                
                # Version optimis�e
                listeModifications.append((dictValeurs["label"], dictValeurs["montant_initial"], dictValeurs["montant"], dictValeurs["forfait_date_debut"], dictValeurs["forfait_date_fin"], dictValeurs["code_compta"], dictValeurs["code_produit_local"], dictValeurs["tva"], IDPrestationModif))
                listeSuppressions.append(IDPrestationModif)

        # Modifications
        if len(listeModifications) > 0 :
            DB.Executermany("UPDATE prestations SET label=?, montant_initial=?, montant=?, forfait_date_debut=?, forfait_date_fin=?, code_compta=?, code_produit_local=?, tva=? WHERE IDprestation=?", listeModifications, commit=False)

        # Suppression
        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 : 
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else : 
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM ventilation WHERE IDprestation IN %s" % conditionSuppression)


        # ------------- Suppression des prestations et d�ductions � supprimer ------------------
        
        # Version optimis�e
        if len(self.listePrestationsSupprimees) > 0 :
            if len(self.listePrestationsSupprimees) == 1 : 
                conditionSuppression = "(%d)" % self.listePrestationsSupprimees[0]
            else : 
                conditionSuppression = str(tuple(self.listePrestationsSupprimees))
            DB.ExecuterReq("DELETE FROM prestations WHERE IDprestation IN %s" % conditionSuppression)
            DB.ExecuterReq("DELETE FROM ventilation WHERE IDprestation IN %s" % conditionSuppression)
            DB.ExecuterReq("DELETE FROM deductions WHERE IDprestation IN %s" % conditionSuppression)

        # --------------- Sauvegarde du DictConso --------------------
        listeAjouts = []
        listeModifications = []
        listeSuppressions = []
        listeChamps = []
        dictHistorique = {}
        for IDindividu, dictDates in self.dictConsoIndividus.items() :
            for date, dictUnites in dictDates.items() :
                for IDunite, listeConso in dictUnites.items() :
                    for conso in listeConso :

                        # Recherche s'il y a une prestation
                        IDprestation = conso.IDprestation
                        if (IDprestation == None or IDprestation < 0) and (IDprestation in dictNewIDprestation) == True :
                            IDprestation = dictNewIDprestation[IDprestation]

                        # R�cup�ration des donn�es
                        listeDonnees = [
                            ("IDindividu", IDindividu),
                            ("IDinscription", conso.IDinscription),
                            ("IDactivite", conso.IDactivite),
                            ("date", str(date)),
                            ("IDunite", IDunite),
                            ("IDgroupe", conso.IDgroupe),
                            ("heure_debut", conso.heure_debut),
                            ("heure_fin", conso.heure_fin),
                            ("etat", conso.etat),
                            ("verrouillage", 0), #dictValeurs["verrouillage"]),
                            ("date_saisie", str(conso.date_saisie)),
                            ("IDutilisateur", conso.IDutilisateur),
                            ("IDcategorie_tarif", conso.IDcategorie_tarif),
                            ("IDcompte_payeur", conso.IDcompte_payeur),
                            ("IDprestation", IDprestation),
                            ("quantite", conso.quantite),
                            ("etiquettes", ConvertListeToStr(conso.etiquettes)),
                            ("IDevenement", conso.IDevenement),
                            ("badgeage_debut", conso.badgeage_debut),
                            ("badgeage_fin", conso.badgeage_fin),
                        ]

                        # Pour version optimis�e :
                        listeValeurs = []
                        for key, valeur in listeDonnees :
                            if key not in listeChamps :
                                listeChamps.append(key)
                            listeValeurs.append(valeur)

                        # Pr�paration pour historique
                        IDfamille = conso.IDfamille
                        if (IDfamille in dictHistorique) == False :
                            dictHistorique[IDfamille] = {}
                        if (IDindividu in dictHistorique[IDfamille]) == False :
                            dictHistorique[IDfamille][IDindividu] = { "suppr" : {}, "modif" : {}, "ajout" : {} }

                        # Recherche de l'abr�g� de l'unit�
                        if IDunite in self.dictUnites :
                            abregeUnite = self.dictUnites[IDunite]["abrege"]
                        else :
                            abregeUnite = u"---"

                        # Interception erreur conso corrompue
                        # if conso.IDinscription == None :
                        #     print conso.__dict__
                        #     raise Exception("Erreur : IDinscription a 0")

                        # Ajout
                        if conso.statut == "ajout" :
                            # Version optimis�e
                            listeAjouts.append(listeValeurs)

                            if (date in dictHistorique[IDfamille][IDindividu]["ajout"]) == False :
                                dictHistorique[IDfamille][IDindividu]["ajout"][date] = []
                            dictHistorique[IDfamille][IDindividu]["ajout"][date].append(abregeUnite)

                        # Modification
                        if conso.statut == "modification" :

                            # Version optimis�e
                            listeValeursTemp = listeValeurs
                            listeValeursTemp.append(conso.IDconso)
                            listeModifications.append(listeValeursTemp)

                            if (date in dictHistorique[IDfamille][IDindividu]["modif"]) == False :
                                dictHistorique[IDfamille][IDindividu]["modif"][date] = []
                            dictHistorique[IDfamille][IDindividu]["modif"][date].append(abregeUnite)

                        # Suppression
                        if conso.statut == "suppression" or (conso.etat == None and conso.IDconso != None) :

                            # Version optimis�e
                            listeSuppressions.append(conso.IDconso)

                            if (date in dictHistorique[IDfamille][IDindividu]["suppr"]) == False :
                                dictHistorique[IDfamille][IDindividu]["suppr"][date] = []
                            dictHistorique[IDfamille][IDindividu]["suppr"][date].append(abregeUnite)



        # Suppression des consommations multihoraires
        for conso in self.listeConsoSupprimees :
            listeSuppressions.append(conso.IDconso) 

            if conso.case.IDunite in self.dictUnites :
                abregeUnite = self.dictUnites[conso.case.IDunite]["abrege"]
            else :
                abregeUnite = u"---"

            # Pr�paration pour historique
            IDfamille = conso.IDfamille
            IDindividu = conso.case.IDindividu
            if (IDfamille in dictHistorique) == False :
                dictHistorique[IDfamille] = {}
            if (IDindividu in dictHistorique[IDfamille]) == False :
                dictHistorique[IDfamille][IDindividu] = { "suppr" : {}, "modif" : {}, "ajout" : {} }

            if (conso.case.date in dictHistorique[IDfamille][IDindividu]["suppr"]) == False :
                dictHistorique[IDfamille][IDindividu]["suppr"][conso.case.date] = []
            dictHistorique[IDfamille][IDindividu]["suppr"][conso.case.date].append(abregeUnite)
        
        
        # Ajouts
        if len(listeAjouts) > 0 :
            texteChampsTemp = ", ".join(listeChamps)
            listeInterrogations = []
            for champ in listeChamps :
                listeInterrogations.append("?")
            texteInterrogations = ", ".join(listeInterrogations)
            DB.Executermany("INSERT INTO consommations (%s) VALUES (%s)" % (texteChampsTemp, texteInterrogations), listeAjouts, commit=False)

        # Modifications
        if len(listeModifications) > 0 :
            listeChampsTemp = []
            for champ in listeChamps :
                listeChampsTemp.append(("%s=?" % champ))
            DB.Executermany("UPDATE consommations SET %s WHERE IDconso=?" % ", ".join(listeChampsTemp), listeModifications, commit=False)

        # Suppression
        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 : 
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else : 
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM consommations WHERE IDconso IN %s" % conditionSuppression)

        # Application des modifications dans la base de donn�es
        DB.Commit()

        # ---------------- Sauvegarde des m�mos journaliers -------------------
        for key, valeurs in self.dictMemos.items() :
            IDindividu = key[0]
            date = key[1]
            IDmemo = valeurs["IDmemo"]
            texte = valeurs["texte"]
            couleur = valeurs["couleur"]
            statut = valeurs["statut"]
        
            listeDonnees = [
                    ("IDindividu", IDindividu), 
                    ("date", str(date)),
                    ("texte", texte),
                    ("couleur", couleur),
                    ]
            # Ajout
            if statut == "ajout" :
                IDmemo = DB.ReqInsert("memo_journee", listeDonnees, commit=False)
            # Modification
            if statut == "modification" :
                DB.ReqMAJ("memo_journee", listeDonnees, "IDmemo", IDmemo, commit=False)
            # Suppression
            if statut == "suppression" :
                DB.ReqDEL("memo_journee", "IDmemo", IDmemo, commit=False)

        # ----------------- M�morisation de l'action dans l'historique g�n�ral -------------------
        listeAjoutsHistorique = []
        for IDfamille, dictIndividus in dictHistorique.items() :
            for IDindividu, dictCategories in dictIndividus.items() :
                for codeCategorie in ("suppr", "modif", "ajout") :
                    dictDates = dictCategories[codeCategorie]
                    if len(dictDates) > 0 :
                        listeDates = list(dictDates.keys())
                        listeDates.sort()
                        listeTextes = []
                        for date in listeDates :
                            listeUnites = dictDates[date]
                            dateFr = u"%s/%s/%s" % (str(date)[8:10], str(date)[5:7], str(date)[2:4])
                            listeTextes.append(u"%s(%s)" % (dateFr, "+".join(listeUnites) ))
                        texte = u", ".join(listeTextes)

                        if codeCategorie == "ajout" : IDcategorie = 9
                        if codeCategorie == "modif" : IDcategorie = 29
                        if codeCategorie == "suppr" : IDcategorie = 10

                        listeAjoutsHistorique.append({
                            "IDfamille" : IDfamille,
                            "IDindividu" : IDindividu,
                            "IDcategorie" : IDcategorie,
                            "action" : texte,
                            })

        if len(listeAjoutsHistorique) > 0 :
            UTILS_Historique.InsertActions(listeAjoutsHistorique, DB=DB)


        # Application des modifications dans la base de donn�es
        DB.Commit()

        # Cloture de la DB
        DB.Close()


    def SauvegardeTransports(self):
        """ Sauvegarde des transports """
        DB = GestionDB.DB()
        
        for IDindividu, dictTransports in self.dict_transports.items() :
            # AJOUTS et MODIFICATIONS
            listeNewID = {}
            for IDtransport, dictTransport in dictTransports.items() :

                # Cr�ation de la liste de donn�es
                listeDonnees = [
                    ("IDindividu", dictTransport["IDindividu"]),
                    ("mode", dictTransport["mode"]),
                    ("categorie", dictTransport["categorie"]),
                    ("IDcompagnie", dictTransport["IDcompagnie"]),
                    ("IDligne", dictTransport["IDligne"]),
                    ("numero", dictTransport["numero"]),
                    ("details", dictTransport["details"]),
                    ("observations", dictTransport["observations"]),
                    ("depart_date", dictTransport["depart_date"]),
                    ("depart_heure", dictTransport["depart_heure"]),
                    ("depart_IDarret", dictTransport["depart_IDarret"]),
                    ("depart_IDlieu", dictTransport["depart_IDlieu"]),
                    ("depart_localisation", dictTransport["depart_localisation"]),
                    ("arrivee_date", dictTransport["arrivee_date"]),
                    ("arrivee_heure", dictTransport["arrivee_heure"]),
                    ("arrivee_IDarret", dictTransport["arrivee_IDarret"]),
                    ("arrivee_IDlieu", dictTransport["arrivee_IDlieu"]),
                    ("arrivee_localisation", dictTransport["arrivee_localisation"]),
                    ("prog", dictTransport["prog"]),
                    ]
                
                # Ajout
                if IDtransport < 0 :
                    newID = DB.ReqInsert("transports", listeDonnees)
                    listeNewID[IDtransport] = newID
                
                # Modification
                else :
                    if dictTransport["etat"] == "MODIF" :
                        DB.ReqMAJ("transports", listeDonnees, "IDtransport", IDtransport)
        
        # SUPPRESSIONS
        for IDtransport in self.listeTransportsInitiale :
            supprimer = True
            for IDindividu, dictTransports in self.dict_transports.items() :
                if IDtransport in list(dictTransports.keys()) :
                    supprimer = False
            if supprimer == True :
                DB.ReqDEL("transports", "IDtransport", IDtransport)
                    
        # Cloture de la DB
        DB.Close()
    
    def MemoriseParametres(self):
        """ M�morisation des param�tres """
        dictValeurs = {
            "affiche_colonne_memo" : AFFICHE_COLONNE_MEMO,
            "affiche_colonne_transports" : AFFICHE_COLONNE_TRANSPORTS,
            "format_label_ligne" : FORMAT_LABEL_LIGNE,
            "affiche_sans_prestation" : self.afficheSansPrestation,
            "blocage_si_complet" : self.blocageSiComplet,
            "hauteur_lignes" : self.dictParametres["hauteur"],
            "largeur_colonne_memo" : self.dictParametres["largeurs"]["memo"],
            "largeur_colonne_transports" : self.dictParametres["largeurs"]["transports"],
            "masquer_unites_fermees": MASQUER_UNITES_FERMEES,
            }
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="set", categorie="parametres_grille_conso", dictParametres=dictValeurs)

        # Largeurs colonnes
        listeDonnees = []
        for IDunite, largeur in self.dictParametres["largeurs"]["unites"].items() :
            if IDunite in self.dictUnites :
                ancienneLargeur = self.dictUnites[IDunite]["largeur"]
                if largeur != ancienneLargeur : 
                    listeDonnees.append((IDunite, largeur))
                    
        if len(listeDonnees) > 0 :
            DB = GestionDB.DB()
            for IDunite, largeur in listeDonnees :
                DB.ReqMAJ("unites", [("largeur", largeur),], "IDunite", IDunite)
            DB.Close() 
        
        
####AFFICHAGE

    def OnChangeRowSize(self, event):
        numLigne = event.GetRowOrCol() 
        if self.dictLignes[numLigne].estSeparation == True :
            self.SetRowSize(numLigne, 18)
            return
        hauteur = self.GetRowSize(numLigne)
        for numLigne in range(0, self.GetNumberRows()) :
            if self.dictLignes[numLigne].estSeparation == False :
                self.SetRowSize(numLigne, hauteur)
        
        self.dictParametres["hauteur"] = hauteur
        
    def OnChangeColSize(self, event):
        numColonne = event.GetRowOrCol() 
        largeur = self.GetColSize(numColonne)
        if len(self.dictLignes) == 0 : return
        ligne = self.dictLignes[0]
        case = ligne.dictCases[numColonne]
        
        if case.GetTypeUnite() == "separationActivite" :
            self.SetColSize(numColonne, LARGEUR_COLONNE_ACTIVITE)
        
        if case.GetTypeUnite() in ("Unitaire", "Multihoraires") :
            self.dictParametres["largeurs"]["unites"][case.IDunite] = largeur
        
        if case.GetTypeUnite() == "memo" :
            self.dictParametres["largeurs"]["memo"] = largeur
        
        if case.GetTypeUnite() == "transports" :
            self.dictParametres["largeurs"]["transports"] = largeur
        
    
    def GetAfficheColonneTransports(self):
        return AFFICHE_COLONNE_TRANSPORTS
    
    def SetAfficheColonneTransports(self, etat=True):
        global AFFICHE_COLONNE_TRANSPORTS
        AFFICHE_COLONNE_TRANSPORTS = etat
        self.MAJ_affichage() 
    
    def GetAfficheColonneMemo(self):
        return AFFICHE_COLONNE_MEMO
    
    def SetAfficheColonneMemo(self, etat=True):
        global AFFICHE_COLONNE_MEMO
        AFFICHE_COLONNE_MEMO = etat
        self.MAJ_affichage()

    def GetMasquerUnitesFermees(self):
        return MASQUER_UNITES_FERMEES

    def SetMasquerUnitesFermees(self, etat=True):
        global MASQUER_UNITES_FERMEES
        MASQUER_UNITES_FERMEES = etat
        self.MAJ()

    def GetFormatLabelLigne(self):
        return FORMAT_LABEL_LIGNE
    
    def SetFormatLabelLigne(self, format="nom_prenom"):
        global FORMAT_LABEL_LIGNE
        FORMAT_LABEL_LIGNE = format
        self.MAJ_affichage() 
    
    def Parametres(self):
        listeDonnees = []
        
        # Hauteur
        listeDonnees.append(
            (_(u"Hauteur de ligne"), [{"label" : _(u"Hauteur"), "code" : "hauteur", "valeur" : self.dictParametres["hauteur"], "defaut" : HAUTEUR_LIGNE},] )
            )
        listeActivites = []
        
        for IDactivite in self.listeActivites :
            nomActivite = self.dictActivites[IDactivite]["nom"]
            listeUnites = []
            if IDactivite in self.dictListeUnites:
                for dictUnite in self.dictListeUnites[IDactivite] :
                    IDunite = dictUnite["IDunite"]
                    nomUnite = u"%s (%s)" % (dictUnite["nom"], dictUnite["abrege"])
                    if dictUnite["type"] == "Multihoraires" :
                        defaut = LARGEUR_COLONNE_MULTIHORAIRES
                    elif dictUnite["type"] == "Evenement" :
                        defaut = LARGEUR_COLONNE_EVENEMENT
                    else :
                        defaut = LARGEUR_COLONNE_UNITE
                    listeUnites.append( {"label" : nomUnite, "code" : str(IDunite), "valeur" : self.dictParametres["largeurs"]["unites"][IDunite], "defaut" : defaut} )
            listeDonnees.append((_(u"Colonnes %s") % nomActivite, listeUnites))

        listeDonnees.append(
            (_(u"Autres colonnes"), [
                {"label" : _(u"M�mo journalier"), "code" : "memo", "valeur" : self.dictParametres["largeurs"]["memo"], "defaut" : LARGEUR_COLONNE_MEMO},
                {"label" : _(u"Transports"), "code" : "transports", "valeur" : self.dictParametres["largeurs"]["transports"], "defaut" : LARGEUR_COLONNE_TRANSPORTS},
                ] )
            )

        from Dlg import DLG_Grille_parametres
        dlg = DLG_Grille_parametres.Dialog(self, listeDonnees)
        if dlg.ShowModal() == wx.ID_OK :
            dictDonnees = dlg.GetDonnees()
            self.dictParametres["hauteur"] = dictDonnees["hauteur"]
            self.dictParametres["largeurs"]["memo"] = dictDonnees["memo"]
            self.dictParametres["largeurs"]["transports"] = dictDonnees["transports"]
            for key, valeur in dictDonnees.items() :
                if key not in ("hauteur", "memo", "transports") :
                    IDunite = int(key)
                    self.dictParametres["largeurs"]["unites"][IDunite] = valeur
            self.MAJ_affichage() 
        dlg.Destroy()
    
    def EcritStatusbar(self, case=None, x=None, y=None):
        if case == None :
            texte = u""
        else :
            texte = case.GetStatutTexte(x, y)
            if texte == None : texte = u""
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass
        

    def RechercheTexteLigne(self, texte=""):
        """ Recherche un texte sur une ligne et l'affiche """
        # Parcours les lignes
        if texte == "" :
            return
        for numLigne, ligne in self.dictLignes.items() :
            if texte.lower() in ligne.labelLigne.lower() :
                self.MakeCellVisible(numLigne, 1)
##                ligne.Flash()
                return True
        return False

    def SelectionnerLignes(self, event=None):
        for numLigne, ligne in self.dictLignes.items() :
            if ligne.estSeparation == False :
                ligne.coche = True
        self.Refresh()

    def DeselectionnerLignes(self, event=None):
        for numLigne, ligne in self.dictLignes.items() :
            if ligne.estSeparation == False :
                ligne.coche = False
        self.Refresh()

    def Recopier(self, event=None):
        """ Recopiage des conso d'une unit� vers une autre unit� """

        # Demande les param�tres de la conversion
        from Dlg import DLG_Recopiage_conso
        dlg = DLG_Recopiage_conso.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            dictDonnees = dlg.GetDonnees()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        # Recherche les cases � recopier
        listeCasesOriginales = []
        for numLigne, ligne in self.dictLignes.items() :
            if dictDonnees["option_lignes"] == "lignes_affichees" or (dictDonnees["option_lignes"] == "lignes_selectionnees" and ligne.coche == True):
                for numColonne, case in ligne.dictCases.items() :
                    if case.typeCase == "consommation" and case.IDunite == dictDonnees["ID_unite_origine"] :
                        listeCasesOriginales.append(case)

        # Traitement
        listeJournaux = []
        for case in listeCasesOriginales :
            for conso in case.GetListeConso() :
                if conso.etat != None :

                    # Pr�pare les param�tres de la conso � saisir ou � supprimer
                    dictParametres = {
                        "action" : "saisie",
                        "dates" : [case.ligne.date,],
                        "description" : u"Recopiage",
                        "IDactivite" : case.IDactivite,
                        "date_fin" : [case.ligne.date,],
                        "date_debut" : [case.ligne.date,],
                        "jours_scolaires" : [0, 1, 2, 3, 4, 5, 6],
                        "jours_vacances" : [0, 1, 2, 3, 4, 5, 6],
                        "semaines" : 1,
                        "feries" : True,
                        "individus" : [{"selection" : True, "IDindividu" : case.ligne.IDindividu},],
                        "etiquettes" : [],
                        "etat" : "reservation",
                        "unites" : [{
                                "nom" : self.dictUnites[dictDonnees["ID_unite_destination"]]["nom"],
                                "type" : self.dictUnites[dictDonnees["ID_unite_destination"]]["type"],
                                "IDunite" : dictDonnees["ID_unite_destination"],
                                "options" : {},}],
                        }

                    # Informations optionnelles
                    if dictDonnees["param_etat"] == True :
                        dictParametres["etat"] = conso.etat

                    if dictDonnees["param_etiquettes"] == True :
                        dictParametres["etiquettes"] = conso.etiquettes

                    if dictDonnees["param_horaires"] == True :
                        dictParametres["unites"][0]["options"]["heure_debut"] = conso.heure_debut
                        dictParametres["unites"][0]["options"]["heure_fin"] = conso.heure_fin

                    if dictDonnees["param_quantite"] == True :
                        dictParametres["unites"][0]["options"]["quantite"] = conso.quantite

                    # Traitement par lot pour recopier
                    journal = self.TraitementLot_processus(dictParametres)
                    listeJournaux.append((case, conso, journal))

        # Formatage du texte de r�sultats
        texte = _(u"<B>La proc�dure de recopiage est termin�e mais les incidents suivants ont �t� rencontr�s :</B><BR><BR>")

        afficher = False
        texte += u"<UL>"
        for case, conso, journal in listeJournaux :
            for IDindividu, listeActions in journal.items() :
                if len(listeActions) > 0 :
                    afficher = True
                    for date, nomUnite, action in listeActions :
                        texte += u"<LI>%s - %s : %s.</LI>" % (case.ligne.labelLigne, nomUnite, action)
        texte += "</UL><BR><BR>"

        # Affichage des r�sultats
        if afficher == True :
            from Dlg import DLG_Message_html
            dlg = DLG_Message_html.Dialog(self, texte=u"<FONT SIZE=2>%s</FONT>" % texte, titre=_(u"R�sultats du recopiage"), size=(630, 450))
            dlg.ShowModal()
            dlg.Destroy()




        # # Calcule les variables
        # dictVariables = {}
        # for IDunite, case in dictCasesUnites.iteritems():
        #     heure_debut = HeureStrEnDelta("00:00")
        #     heure_fin = HeureStrEnDelta("00:00")
        #     duree = HeureStrEnDelta("00:00")
        #     etat = None
        #
        #     for conso in case.GetListeConso() :
        #         if conso.etat != None :
        #             heure_debut_conso = HeureStrEnDelta(conso.heure_debut)
        #             heure_fin_conso = HeureStrEnDelta(conso.heure_fin)
        #             duree_conso = heure_fin_conso - heure_debut_conso
        #
        #             # Heure min
        #             if heure_debut_conso < heure_debut or heure_debut == HeureStrEnDelta("00:00"):
        #                 heure_debut = heure_debut_conso
        #
        #             # Heure_max
        #             if heure_fin_conso > heure_fin :
        #                 heure_fin = heure_fin_conso
        #
        #             # Dur�e
        #             duree += duree_conso
        #
        #             # Etat
        #             etat = conso.etat
        #
        #     # M�morisation des r�sultats
        #     dictVariables["{HEUREDEBUT_UNITE%d}" % IDunite] = heure_debut
        #     dictVariables["{HEUREFIN_UNITE%d}" % IDunite] = heure_fin
        #     dictVariables["{DUREE_UNITE%d}" % IDunite] = duree
        #     dictVariables["{ETAT_UNITE%d}" % IDunite] = etat
        #
        # # Traite chaque unit� auto-g�n�r�e
        # for dictUnite in listeUnitesAuto :
        #
        #     # V�rifie si les conditions sont r�unies
        #     conditions = dictUnite["autogen_conditions"]
        #     listeConditions = conditions.split(";")
        #
        #     valide = True
        #     if len(listeConditions) == 0 :
        #         valide = False
        #
        #     for condition in listeConditions :
        #         # V�rifie que la condition est valide
        #         if self.ResolveFormule(condition, dictVariables) != True :
        #             valide = False
        #
        #     # Pr�pare les param�tres de la conso � saisir ou � supprimer
        #     dictParametres = {
        #         "dates" : [ligne.date,],
        #         "description" : u"Auto-g�n�ration",
        #         "IDactivite" : IDactivite,
        #         "date_fin" : [ligne.date,],
        #         "date_debut" : [ligne.date,],
        #         "jours_scolaires" : [0, 1, 2, 3, 4, 5, 6],
        #         "jours_vacances" : [0, 1, 2, 3, 4, 5, 6],
        #         "semaines" : 1,
        #         "feries" : True,
        #         "individus" : [{"selection" : True, "IDindividu" : ligne.IDindividu},],
        #         "unites" : [{"nom" : dictUnite["nom"],"type" : dictUnite["type"],"IDunite" : dictUnite["IDunite"],"options" : {}},],
        #     }
        #
        #     # V�rifie si une conso existe d�j� :
        #     consoExists = dictVariables["{ETAT_UNITE%d}" % dictUnite["IDunite"]] != None
        #     #print "consoExists=", consoExists
        #
        #     # Si toutes les conditions sont valides
        #     if valide == True :
        #
        #         # R�cup�ration des param�tres de l'unit� auto-g�n�r�e
        #         parametres = dictUnite["autogen_parametres"]
        #         if parametres not in ("", None) :
        #
        #             listeDonnees = parametres.split("##")
        #             for donnee in listeDonnees :
        #                 champ, valeur = donnee.split(":=")
        #
        #                 if champ == "ETIQUETTES" and valeur != None :
        #                     etiquettes = UTILS_Texte.ConvertStrToListe(valeur)
        #                     dictParametres["etiquettes"] = etiquettes
        #
        #                 if champ == "ETAT" and valeur != None :
        #                     dictParametres["etat"] = valeur
        #
        #                 if champ == "QUANTITE" and valeur != None :
        #                     if valeur != "1" :
        #                         dictParametres["unites"][0]["options"]["quantite"] = int(valeur)
        #
        #                 if champ == "HEUREDEBUT" and valeur != None :
        #                     if "FORMULE:" in valeur :
        #                         formule = valeur.replace("FORMULE:", "")
        #                         heure_debut = self.ResolveFormule(formule, dictVariables)
        #                     else :
        #                         heure_debut = HeureStrEnDelta(valeur)
        #                     #print "heure_debut=", DeltaEnStr(heure_debut, separateur=":")
        #                     dictParametres["unites"][0]["options"]["heure_debut"] = DeltaEnStr(heure_debut, separateur=":")
        #
        #                 if champ == "HEUREFIN" and valeur != None :
        #                     if "FORMULE:" in valeur :
        #                         formule = valeur.replace("FORMULE:", "")
        #                         heure_fin = self.ResolveFormule(formule, dictVariables)
        #                     else :
        #                         heure_fin = HeureStrEnDelta(valeur)
        #                     #print "heure_fin=", DeltaEnStr(heure_fin, separateur=":")
        #                     dictParametres["unites"][0]["options"]["heure_fin"] = DeltaEnStr(heure_fin, separateur=":")
        #
        #             # Action
        #             if consoExists :
        #                 dictParametres["action"] = "modification"
        #             else :
        #                 dictParametres["action"] = "saisie"
        #
        #             # Traitement par lot
        #             journal = self.TraitementLot_processus(dictParametres)
        #             #print "journal =", journal
        #
        #     if valide == False and consoExists :
        #         dictParametres["action"] = "suppression"
        #         dictParametres["etiquettes"] = []
        #         journal = self.TraitementLot_processus(dictParametres)
        #         #print "journal =", journal

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.grille = CTRL(panel, IDfamille=203)
        self.grille.SetModeIndividu(listeActivites=[16, ], listeSelectionIndividus=[1437,], listeIndividusFamille=[1437,], listePeriodes=[(datetime.date(2015, 7, 1), datetime.date(2015, 7, 10)),])
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.ctrl_facturation = wx.TextCtrl(panel, -1, "", size=(-1, 60), style=wx.TE_MULTILINE)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.grille, 1, wx.EXPAND, 0)
        sizer_2.Add(self.bouton_ok, 0, wx.EXPAND, 0)
        sizer_2.Add(self.ctrl_facturation, 0, wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.SetSize((990, 700))
        self.Layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
    def OnBoutonOk(self, event):
        self.grille.Sauvegarde()
        print("Sauvegarde ok")
        

##if __name__ == '__main__':
##    app = wx.App(0)
##    from Dlg import DLG_Grille2 as DLG_Grille
##    frame= MyFrame(None, name="test")
##    app.SetTopWindow(frame)
##    frame.Show()
##    app.MainLoop()

if __name__ == '__main__':
    app = wx.App(0)
    heure_debut = time.time()
    from Dlg import DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=14, selectionIndividus=[46,])
    app.SetTopWindow(frame_1)
    print("Temps de chargement CTRL_Grille =", time.time() - heure_debut)
    frame_1.ShowModal()
    app.MainLoop()