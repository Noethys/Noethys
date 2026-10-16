#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.html
from PIL import Image
import datetime
import calendar
import GestionDB
from Utils import UTILS_Dates
import six

from numpy import arange, sqrt, array, asarray, ones, exp, convolve, linspace

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import copy
import functools


def NouvelleFigure():
    """ Crée une figure hors pyplot : pas de fenêtre GUI cachée, et libérée par le ramasse-miettes """
    figure = Figure()
    FigureCanvasAgg(figure)
    return figure


# Cache des résultats des requêtes statistiques (plusieurs jeux de paramètres, ex : période N et N-1)
DICT_CACHE = {}
TAILLE_MAX_CACHE = 10

def Memoriser(fonction):
    """ Décorateur : mémorise le résultat de fonction(DB, dictParametres, ...) selon les paramètres """
    @functools.wraps(fonction)
    def wrapper(DB, dictParametres, *args, **kwargs):
        cle = (fonction.__module__, fonction.__name__, args, tuple(sorted(kwargs.items())))
        entrees = DICT_CACHE.setdefault(cle, [])
        for parametres, resultat in entrees:
            if parametres == dictParametres:
                return resultat
        resultat = fonction(DB, dictParametres, *args, **kwargs)
        entrees.append((copy.deepcopy(dictParametres), resultat))
        if len(entrees) > TAILLE_MAX_CACHE:
            del entrees[0]
        return resultat
    return wrapper

def ViderCache():
    DICT_CACHE.clear()


_MEMORY_FS_HANDLER = None

def GetMemoryFSHandler():
    """ Un seul handler mémoire enregistré pour toute l'application """
    global _MEMORY_FS_HANDLER
    if _MEMORY_FS_HANDLER is None:
        _MEMORY_FS_HANDLER = wx.MemoryFSHandler()
        wx.FileSystem.AddHandler(_MEMORY_FS_HANDLER)
    return _MEMORY_FS_HANDLER


COULEUR_VERT_POMME = (151, 253, 79)
COULEUR_BLEU_CIEL = (174, 212, 253)
LISTE_NOMS_MOIS = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))


def DateEngEnDateDD(dateEng):
    if type(dateEng) == datetime.date: return dateEng
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def ConvertitCouleur(couleur=(255, 255, 255)):
    """ Convertit une couleur de format (0, 0, 0) au format #000000 """
    return "#%02X%02X%02X" % couleur

def ConvertitCouleur2(RGB) :
    couleur = []
    for valeur in RGB :
        couleur.append(valeur/255.0)
    return couleur

def HSVToRGB(couleurHSV):
    """ Converts a HSV triplet into a RGB triplet. """
    h, s, v = couleurHSV
    maxVal = v
    delta = (maxVal*s)/255.0
    minVal = maxVal - delta
    hue = float(h)

    if h > 300 or h <= 60:
        r = maxVal
        if h > 300:
            g = int(minVal)
            hue = (hue - 360.0)/60.0
            b = int(-(hue*delta - minVal))
        else:
            b = int(minVal)
            hue = hue/60.0
            g = int(hue*delta + minVal)
    elif h > 60 and h < 180:
        g = int(maxVal)
        if h < 120:
            b = int(minVal)
            hue = (hue/60.0 - 2.0)*delta
            r = int(minVal - hue)
        else:
            r = int(minVal)
            hue = (hue/60.0 - 2.0)*delta
            b = int(minVal + hue)
    else:
        b = int(maxVal)
        if h < 240:
            r = int(minVal)
            hue = (hue/60.0 - 4.0)*delta
            g = int(minVal - hue)
        else:
            g = int(minVal)
            hue = (hue/60.0 - 4.0)*delta
            r = int(minVal + hue)
    return (r, g, b)

def RGBToHSV(couleurRGB=(255, 255, 255)):
    """ Converts a RGB triplet into a HSV triplet. """
    r, g, b = couleurRGB
    minVal = float(min(r, min(g, b)))
    maxVal = float(max(r, max(g, b)))
    delta = maxVal - minVal
    v = int(maxVal)
    
    if abs(delta) < 1e-6:
        h = s = 0
    else:
        temp = delta/maxVal
        s = int(temp*255.0)
        if r == int(maxVal):
            temp = float(g-b)/delta
        elif g == int(maxVal):
            temp = 2.0 + (float(b-r)/delta)
        else:
            temp = 4.0 + (float(r-g)/delta)
        temp *= 60
        if temp < 0:
            temp += 360
        elif temp >= 360.0:
            temp = 0
        h = int(temp)
    return (h, s, v)

def Ligne_moyenne(x, n, type='simple'):
    """compute an n period moving average. type is 'simple' | 'exponential'"""
    x = asarray(x)
    if type=='simple':
        weights = ones(n)
    else:
        weights = exp(linspace(-1., 0., n))
    weights /= weights.sum()
    a =  convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a


def GetDatesPeriode(dictParametres={}):
    """ Renvoie les dates de début et de fin de période de référence """
    if "mode" in dictParametres :
        if dictParametres["mode"] == "inscrits" :
            date_debut = datetime.date(1977, 1, 1)
            date_fin = datetime.date(2999, 1, 1)
        else:
            date_debut = dictParametres["periode"]["date_debut"]
            date_fin = dictParametres["periode"]["date_fin"]
    else:
        date_debut = datetime.date(1977, 1, 1)
        date_fin = datetime.date(2999, 1, 1)
    return date_debut, date_fin

def GetConditionActivites(dictParametres={}):
    """ Renvoie les conditions d'activités pour les req SQL """
    conditionsActivites = ""
    if "listeActivites" in dictParametres:
        if len(dictParametres["listeActivites"]) == 0 : 
            conditionsActivites = "()"
        elif len(dictParametres["listeActivites"]) == 1 : 
            conditionsActivites = "(%d)" % dictParametres["listeActivites"][0]
        else : 
            conditionsActivites = str(tuple(dictParametres["listeActivites"]))
    return conditionsActivites

def GetConditionArchives(dictParametres={}):
    """ Renvoie la condition SQL d'exclusion des individus archivés/effacés (si l'option est cochée) """
    if dictParametres.get("exclure_archives", False) == True :
        return "AND (individus.etat IS NULL OR individus.etat NOT IN ('archive', 'efface'))"
    return ""

def GetInfosActivites(DB=None, listeActivites=[]):
    """ Récupération des infos sur les activités souhaitées """
    if len(listeActivites) == 0 : conditionActivites = "()"
    elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
    else : conditionActivites = str(tuple(listeActivites))
    req = _(u"SELECT IDactivite, nom, abrege, date_debut, date_fin FROM activites WHERE IDactivite IN %s ORDER BY date_debut;") % conditionActivites
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeInfosActivites = []
    for IDactivite, nom, abrege, date_debut, date_fin in listeDonnees :
        if date_debut != None : date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
        if date_fin != None : date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
        if date_debut not in (datetime.date(1977, 1, 1), datetime.date(2999, 1, 1), None) and date_fin not in (datetime.date(1977, 1, 1), datetime.date(2999, 1, 1), None) :
            date_milieu = date_debut + ((date_fin - date_debut) / 2)
        else :
            date_milieu = None
        listeInfosActivites.append({"nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "date_milieu" : date_milieu})
    return listeInfosActivites

def GetDateExtremeActivites(DB=None, listeActivites=[], typeDate="date_debut", mode="min"):
    """ Renvoie la date min ou max d'un ensemble d'activités """
    """ typeDate = date_debut, date_fin ou date_milieu """
    listeInfosActivites = GetInfosActivites(DB, listeActivites)
    date = None
    for activite in listeInfosActivites :
        if activite[typeDate] not in (datetime.date(1977, 1, 1), datetime.date(2999, 1, 1), None) :
            if mode == "min" :
                if date == None or activite[typeDate] < date : date = activite[typeDate]
            else :
                if date == None or activite[typeDate] > date : date = activite[typeDate]
    return date


def GetPeriodesComparatives(DB=None, dictParametres={}, date_min=None, date_max=None):
    """ Récupère les périodes pour comparaison """
    listePeriodes = []
    
    # Retourne aucune période
    if dictParametres == None : return listePeriodes
    if dictParametres["mode"] == "inscrits" : return listePeriodes
    if dictParametres["periode"] == None : return listePeriodes
    
    dictPeriode = dictParametres["periode"]

    # Vacances
    if dictPeriode["type"] == "vacances" :
        vacances = dictPeriode["vacances"]
        req = _(u"SELECT nom, annee, date_debut, date_fin FROM vacances ORDER BY date_debut;")
        DB.ExecuterReq(req)
        listeVacances = DB.ResultatReq()
        for nom, annee, date_debut, date_fin in listeVacances :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            if nom == vacances and date_fin >= date_min and date_debut <= date_max :
                label = u"%s %d" % (nom, annee)
                dictTemp = {"vacances":nom, "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":label}
                listePeriodes.append(dictTemp)
            
    # Mois
    if dictPeriode["type"] == "mois" :
        mois = dictPeriode["mois"]
        for annee in range(date_min.year, date_max.year+1) :
            nbreJoursMois = calendar.monthrange(annee, mois)[1]
            date_debut = datetime.date(annee, mois, 1)
            date_fin = datetime.date(annee, mois, nbreJoursMois)
            label = u"%s %d" % (LISTE_NOMS_MOIS[mois-1], annee)
            dictTemp = {"mois":mois, "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":label}
            listePeriodes.append(dictTemp)

    # Année
    if dictPeriode["type"] == "annee" :
        for annee in range(date_min.year, date_max.year+1) :
            date_debut = datetime.date(annee, 1, 1)
            date_fin = datetime.date(annee, 12, 31)
            label = _(u"Année %d") % annee
            dictTemp = {"annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":label}
            listePeriodes.append(dictTemp)

    # Dates
    if dictPeriode["type"] == "dates" :
        date_debut = dictPeriode["date_debut"]
        date_fin = dictPeriode["date_fin"]
        if date_debut.year != date_fin.year :
            return listePeriodes
        for annee in range(date_min.year, date_max.year+1) :
            nbreJoursMois = calendar.monthrange(annee, date_debut.month)[1]
            if date_debut.day < nbreJoursMois :
                date_debut_temp = datetime.date(annee, date_debut.month, date_debut.day)
            else :
                date_debut_temp = datetime.date(annee, date_debut.month, nbreJoursMois)
            nbreJoursMois = calendar.monthrange(annee, date_fin.month)[1]
            if date_fin.day < nbreJoursMois :
                date_fin_temp = datetime.date(annee, date_fin.month, date_fin.day)
            else :
                date_fin_temp = datetime.date(annee, date_fin.month, nbreJoursMois)
            label = _(u"Du %s au %s") % (DateEngFr(str(date_debut_temp)), DateEngFr(str(date_fin_temp)))
            dictTemp = {"date_debut":date_debut_temp, "date_fin":date_fin_temp, "label":label}
            listePeriodes.append(dictTemp)

    return listePeriodes




#--- Classes Modèles --------------------------------------------------------------------------------------------------------------------

class HTML():
    def __init__(self, liste_objets=[]):
        self.liste_objets = liste_objets
        self.dictParametres = {}
        
        # Création du stock d'images
        self.stockImages = GetMemoryFSHandler()
    
    def SetParametres(self, dictParametres={}) :
        self.dictParametres = dictParametres

    def GetObjet(self, code):
        """ Recherche un objet par son code """
        for dictRubrique in self.liste_objets:
            for dictPage in dictRubrique["pages"]:
                for objet in dictPage["objets"]:
                    if getattr(objet, "code", None) == code:
                        return objet
        return None

    def GetPersonnalisations(self):
        """ Récupère toutes les personnalisations des tableaux """
        dictPersonnalisations = {}
        for dictRubrique in self.liste_objets:
            for dictPage in dictRubrique["pages"]:
                for objet in dictPage["objets"]:
                    if hasattr(objet, "dictPersonnalisation") and getattr(objet, "dictPersonnalisation", None):
                        dictPersonnalisations[objet.code] = dict(objet.dictPersonnalisation)
        return dictPersonnalisations

    def SetPersonnalisations(self, dictPersonnalisations={}):
        """ Applique un dictionnaire de personnalisations aux objets """
        for dictRubrique in self.liste_objets:
            for dictPage in dictRubrique["pages"]:
                for objet in dictPage["objets"]:
                    if hasattr(objet, "dictPersonnalisation"):
                        if objet.code in dictPersonnalisations:
                            objet.dictPersonnalisation = dict(dictPersonnalisations[objet.code])
                        else:
                            objet.dictPersonnalisation = {}

    def MAJ(self, rubrique=None, page=None):
        """ MAJ d'une rubrique ou d'une page par le code ou tout """
        if rubrique == None and page == None : 
            tout = True
        else : 
            tout = False
        
        if len(self.dictParametres.get("listeActivites", [])) == 0 : 
            return
        
        DB = GestionDB.DB() 
        for dictRubrique in self.liste_objets :
            for dictPage in dictRubrique["pages"] :
                for objet in dictPage["objets"] :
                    if objet.visible == True and (tout == True or rubrique == dictRubrique["code"] or page == dictPage["code"]) :
                        
                        # Vérifie qu'une mise à jour est nécessaire :
                        maj = False
                        if len(objet.dictParametres) > 0 :
                            if objet.dictParametres != self.dictParametres :
                                maj = True
                        else :
                            maj = True
                        
                        # MAJ de l'objet
                        if maj == True :
                            if objet.categorie == "graphe" :
                                figure = NouvelleFigure()
                                figure = objet.MAJ(figure=figure, DB=DB, dictParametres=self.dictParametres)
                                #figure.clear()
                                objet.MemoriseImage(figure) 
                            else:
                                objet.MAJ(DB=DB, dictParametres=self.dictParametres)
                            
        DB.Close() 
        
    def GetHTML(self, rubrique=None, page=None, mode="affichage", selectionsCodes=[]):
        if rubrique == None and page == None : 
            tout = True
        else : 
            tout = False
        
        if len(self.dictParametres.get("listeActivites", [])) == 0 : 
            return ""
        
        # Mode 'affichage'
        if mode == "affichage" :
            html = u"""<HTML><BODY><FONT SIZE=-1>"""
            for dictRubrique in self.liste_objets :
                for dictPage in dictRubrique["pages"] :
                    if (tout == True or rubrique == dictRubrique["code"] or page == dictPage["code"]) :
                        codeRub = dictRubrique["code"]
                        codePg = dictPage["code"]

                        # Signalement des éléments masqués
                        nb_masques = sum(1 for obj in dictPage["objets"] if getattr(obj, "visible", True) == False)
                        if nb_masques > 0:
                            html += u"""<CENTER><TABLE BORDER=0 CELLSPACING=0 WIDTH="90%%" BGCOLOR="#FEF9E7">
                            <TR><TD ALIGN=CENTER>
                            <FONT SIZE=-2 COLOR="#B7950B"><B>ℹ %d élément(s) masqué(s) sur cette page</B></FONT> &nbsp;
                            <A HREF="organiser_page:%s:%s" STYLE="text-decoration:none; color:#B7950B; font-weight:bold;"><FONT SIZE=-2>[Afficher / Réorganiser]</FONT></A>
                            </TD></TR></TABLE></CENTER><BR>""" % (nb_masques, codeRub, codePg)

                        for objet in dictPage["objets"] :
                            if getattr(objet, "visible", True) == True :
                                html += "<P>%s</P>" % objet.GetObjetHTML(mode="affichage")

                        html += u"""<BR><CENTER><TABLE BORDER=0 CELLSPACING=0 WIDTH="90%%" BGCOLOR="#F4F8FA">
                        <TR><TD ALIGN=CENTER>
                        <A HREF="organiser_page:%s:%s" STYLE="text-decoration:none; color:#2C3E50; font-weight:bold;">
                        <FONT SIZE=-1>📑 Organiser les tableaux</FONT>
                        </A>
                        &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
                        <A HREF="gestion_onglets" STYLE="text-decoration:none; color:#16A085; font-weight:bold;">
                        <FONT SIZE=-1>🗂️ Gérer les onglets</FONT>
                        </A>
                        &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
                        <A HREF="nouveau_tab:%s:%s" STYLE="text-decoration:none; color:#1C4E80; font-weight:bold;">
                        <FONT SIZE=-1>➕ Créer un nouveau tableau</FONT>
                        </A>
                        </TD></TR></TABLE></CENTER><BR>""" % (codeRub, codePg, codeRub, codePg)
            html += u"""</FONT></BODY></HTML>"""

        # Mode 'impression'
        if mode == "impression" :
            html = u"""<HTML><BODY>"""
            numRubrique = 1
            numPage = 0
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            
            # Label de la période
            if self.dictParametres["mode"] == "inscrits" :
                labelPeriode = _(u"Aucune période spécifique")
            else:
                date_debut = DateEngFr(str(self.dictParametres["periode"]["date_debut"]))
                date_fin = DateEngFr(str(self.dictParametres["periode"]["date_fin"]))
                labelPeriode = _(u"Période du %s au %s") % (date_debut, date_fin)
            
            # Label des activités
            listeLabels = []
            for IDactivite in self.dictParametres["listeActivites"] :
                listeLabels.append((self.dictParametres["dictActivites"][IDactivite]))
            labelActivites = _(u"Activités : ") + u", ".join(listeLabels)
            
            # Titre
            html += u"""<CENTER><TABLE bgcolor="%s" CELLSPACING=1 BORDER=0 COLS=1 WIDTH="100%%">
            <TD bgcolor="%s" WIDTH="100%%">
            
            <TABLE CELLSPACING=0 BORDER=0 COLS=2 WIDTH="100%%">
            <TD WIDTH="60%%"><FONT SIZE=+3><B>Statistiques</B></FONT></TD>
            <TD WIDTH="40%%"><FONT SIZE=-2>%s<BR>%s</FONT></TD>
            </TABLE>
            
            </TD>
            </TABLE></CENTER>
            <BR><BR>
            <FONT SIZE=-1>
            """ % (ConvertitCouleur((0, 0, 0)), ConvertitCouleur((255, 255, 255)),
                      labelPeriode, labelActivites)

            # Contenu
            for dictRubrique in self.liste_objets :
                if dictRubrique["code"] in selectionsCodes and (rubrique == None or rubrique == dictRubrique["code"]) :
                    html += u"""<U><B>%d. %s</B></U>""" % (numRubrique, dictRubrique["nom"].upper())
                    numPage = 0
                    for dictPage in dictRubrique["pages"] :
                        self.MAJ(page=dictPage["code"])
                        if dictPage["code"] in selectionsCodes and (page == None or page == dictPage["code"]) :
                            html += u"""<BLOCKQUOTE><U><B>%s. %s</B></U>""" % (alphabet[numPage], dictPage["nom"])
                            for objet in dictPage["objets"] :
                                if objet.code in selectionsCodes and getattr(objet, "visible", True) == True :
                                    html += u"""<P>%s</P>""" % objet.GetObjetHTML(mode="impression") 
                            html += u"""</BLOCKQUOTE>"""
                            numPage += 1
                    numRubrique += 1
                    
            html += """</FONT></BODY></HTML>"""
        
        return html
                    
    def GetFigure(self, code=""):
        """ Retourne la figure d'un graphe à partir de son code """
        DB = GestionDB.DB() 
        for dictRubrique in self.liste_objets :
            for dictPage in dictRubrique["pages"] :
                for objet in dictPage["objets"] :
                    if objet.code == code :
                        figure = NouvelleFigure()
                        figure = objet.MAJ(figure=figure, DB=DB, dictParametres=self.dictParametres)
                        DB.Close()
                        return figure
        DB.Close() 
        return None
        
                    
        
        
    
class Objet(HTML):
    def __init__(self):
        HTML.__init__(self)
        self.nom = u""
        self.code = ""
        self.visible = True
        self.dictParametres = {}
    def GetObjetHTML(self):
        return None
    def GetObjetPDF(self):
        return None
    
    
class Texte(Objet):
    def __init__(self):
        Objet.__init__(self) 
        self.texte = u""
        self.categorie = "texte"
        
    def GetObjetHTML(self, mode="affichage"):
        return self.texte


class Tableau(Objet):
    def __init__(self):
        Objet.__init__(self) 
        self.categorie = "tableau"
        self.largeur = None
        self.colonnes = [] # (label, largeur)
        self.lignes = [] # (1, 2, 3)
        self.totaux = [] # (32, 34, 54) 
        self.dictParametres = {}
        self.dictPersonnalisation = {}

    def GetObjetHTML(self, mode="affichage"):
        html = u""

        # Init Couleurs
        couleurCadre = ConvertitCouleur((0, 0, 0))
        couleurFondTitre = ConvertitCouleur((130, 130, 130))
        couleurFondLabel = ConvertitCouleur((190, 190, 190))
        couleurFondLigne = ConvertitCouleur((255, 255, 255))
        couleurFondTotaux = ConvertitCouleur((190, 190, 190))
        
        # Création du tableau
        if len(self.lignes) == 0 :
            return html

        # Application des personnalisations si présentes
        perso = getattr(self, "dictPersonnalisation", {}) or {}
        nomTableau = perso.get("titre") or self.nom

        indicesColonnes = list(range(len(self.colonnes)))
        if "colonnes_visibles" in perso and len(perso["colonnes_visibles"]) > 0:
            indicesColonnes = [i for i in perso["colonnes_visibles"] if i < len(self.colonnes)]

        dictColsLibelles = perso.get("colonnes_libelles", {})
        colonnesAffichees = []
        for idx in indicesColonnes:
            lblOriginal, lrg = self.colonnes[idx]
            lblFinal = dictColsLibelles.get(str(idx), dictColsLibelles.get(idx, lblOriginal))
            colonnesAffichees.append((lblFinal, lrg))

        if len(colonnesAffichees) == 0:
            colonnesAffichees = self.colonnes
            indicesColonnes = list(range(len(self.colonnes)))

        lignesMasquees = set(perso.get("lignes_masquees", []))
        dictLignesLibelles = perso.get("lignes_libelles", {})
        lignesAffichees = []
        for idxLigne, ligne in enumerate(self.lignes):
            if idxLigne in lignesMasquees:
                continue
            ligneModifiee = list(ligne)
            cleLigne = str(idxLigne)
            if cleLigne in dictLignesLibelles or idxLigne in dictLignesLibelles:
                ligneModifiee[0] = dictLignesLibelles.get(cleLigne, dictLignesLibelles.get(idxLigne))
            ligneFiltree = [ligneModifiee[i] for i in indicesColonnes if i < len(ligneModifiee)]
            lignesAffichees.append(ligneFiltree)

        if len(lignesAffichees) == 0:
            return html

        totauxAffiches = []
        if len(self.totaux) > 0:
            totauxAffiches = [self.totaux[i] for i in indicesColonnes if i < len(self.totaux)]

        if self.largeur == None :
            largeurTableau = "100%"
        else:
            largeurTableau = str(self.largeur)

        # Liens d'actions et d'organisation (en mode affichage uniquement)
        if mode == "affichage":
            estPerso = bool(perso)
            badgePerso = u""" <FONT SIZE=-2 COLOR="#A04000"><B>(Personnalisé)</B></FONT>""" if estPerso else u""
            html += u"""<CENTER><TABLE BORDER=0 CELLSPACING=0 WIDTH="%s"><TR><TD ALIGN=RIGHT><FONT SIZE=-2><A HREF="monter_tab:%s" STYLE="text-decoration:none; color:#2C3E50;">[⬆ Monter]</A> &nbsp; <A HREF="descendre_tab:%s" STYLE="text-decoration:none; color:#2C3E50;">[⬇ Descendre]</A> &nbsp; <A HREF="masquer_tab:%s" STYLE="text-decoration:none; color:#7F8C8D;">[👁 Masquer]</A> &nbsp; <A HREF="custom_tab:%s" STYLE="text-decoration:none; color:#1C4E80;"><B>[⚙ Personnaliser]</B></A>%s</FONT></TD></TR></TABLE></CENTER>""" % (largeurTableau, self.code, self.code, self.code, self.code, badgePerso)

        html += u"""<CENTER><TABLE bgcolor="%s" CELLSPACING=1 BORDER=0 COLS=%d WIDTH="%s">""" % (couleurCadre, len(colonnesAffichees), largeurTableau)
        
        # Création du titre
        if nomTableau != u"" :
            html += """<TR bgcolor="%s" ALIGN=CENTER><TD COLSPAN="%d"><B>%s</B></TD></TR>""" % (couleurFondTitre, len(colonnesAffichees), nomTableau)
        
        # Création de la ligne des entêtes
        if len(colonnesAffichees) > 0 :
            html += u"""<TR ALIGN=CENTER>"""
            for label, largeur in colonnesAffichees :
                html += u"""<TD bgcolor="%s" WIDTH="%s"><I>%s</I></TD>""" % (couleurFondLabel, largeur, label)
            html += u""""""
        
        # Création des lignes
        for ligne in lignesAffichees :
            html += u"""<TR ALIGN=CENTER>"""
            for label in ligne :
                html += u"""<TD bgcolor="%s">%s</TD>""" % (couleurFondLigne, label)
            html += u"""</TR>"""

        # Création des totaux
        if len(totauxAffiches) > 0 :
            html += u"""<TR ALIGN=CENTER>"""
            for label in totauxAffiches :
                html += u"""<TD bgcolor="%s"><B>%s</B></TD>""" % (couleurFondTotaux, label)
            html += u"""</TR>"""
        
        html += u"""</TABLE></CENTER>"""

        # Note / Observation éventuelle sous le tableau
        note = perso.get("note", "").strip()
        if note != "":
            note_html = note.replace("\n", "<BR>")
            html += u"""<CENTER><TABLE BORDER=0 CELLSPACING=0 WIDTH="%s"><TR><TD ALIGN=LEFT><FONT SIZE=-2 COLOR="#444444"><I><B>Note :</B> %s</I></FONT></TD></TR></TABLE></CENTER>""" % (largeurTableau, note_html)

        return html
    


class Graphe(Objet):
    def __init__(self):
        Objet.__init__(self) 
        self.categorie = "graphe"
        self.taille = (300, 300)
        self.bitmap = None
        if six.PY2:
            self.decalage_x = 0.25
        else:
            self.decalage_x = 0.5

    def MemoriseImage(self, figure=None):
        self.nomImage = "image-%s" % self.code
        if self.bitmap != None :
            try :
                self.stockImages.RemoveFile(self.nomImage)
            except : pass
        
        # Mémorise l'image dans le stockImages
        self.bitmap = self.ConvertMPLtoBMP(figure)
        self.stockImages.AddFile(self.nomImage, self.bitmap , wx.BITMAP_TYPE_PNG)
        
    def GetObjetHTML(self, mode="affichage"):
        if self.bitmap == None : return u""
        # Création Html
        html = """<CENTER><A HREF='%s'><img src="memory:%s"></A></CENTER>""" % (self.code, self.nomImage)
        return html

    def ConvertMPLtoBMP(self, figure=None):
        dpi = 90
        inchesH = 1.0 * self.taille[0] / dpi
        inchesV = 1.0 * self.taille[1] / dpi
        
        # Convert figure matplotlib to python.Image object 
        imgdata = six.BytesIO()
        figure.set_size_inches(inchesH, inchesV)
        figure.savefig(imgdata, format='png', dpi=dpi)#, facecolor='r')
        imgdata.seek(0)
        im = Image.open(imgdata)
        # Convert to wx.Image Object and then to wx.Bitmap
        if 'phoenix' in wx.PlatformInfo:
            self.wximage = wx.Image(im.size[0], im.size[1])
        else :
            self.wximage = wx.EmptyImage(im.size[0], im.size[1])
        self.wximage.SetData(im.convert("RGB").tobytes())
        if 'phoenix' in wx.PlatformInfo:
            self.wximbmp = wx.Bitmap(self.wximage)
        else :
            self.wximbmp = wx.BitmapFromImage(self.wximage)
        return self.wximbmp



#--- Liste des donnees ----------------------------------------------------------------------------------------------------------------------------

##LISTE_DONNEES = [
##
##    {"nom" : _(u"Individus"), "code" : "individus", "image" : None, "visible" : True, "pages" : [
##    
##            {"nom" : _(u"Nombre"), "code" : "nombre", "image" : None, "visible" : True, "objets" : [
##                    Texte_nombre_individus(),
##                    Tableau_nombre_individus(),
##                    Graphe_repartition_genre(),
##                    Graphe_test_2(),
##                    ]},
##
##            {"nom" : _(u"Nouveaux"), "code" : "nouveaux", "image" : None, "visible" : True, "objets" : [
##                    Graphe_repartition_genre(),
##                    Graphe_test_2(),
##                    Texte_nombre_individus(),
##                    ]},
##            
##            ]},
##            
##    ]



# -------------------------------------------------------------------------------------------------------------------------------------------

class FrameTest(wx.Frame):
    """ Frame de test d'un objet """
    def __init__(self, objet=None, dictParametres={}):
        wx.Frame.__init__(self, None, id=-1)
        self.SetMinSize((550, 300))
        panel = wx.Panel(self, -1, name="test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = wx.html.HtmlWindow(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CenterOnScreen() 
        
        # MAJ du contenu
        DB = GestionDB.DB() 
        if objet.categorie == "graphe" :
            figure = matplotlib.pyplot.figure()
            figure = objet.MAJ(figure=figure, DB=DB, dictParametres=dictParametres)
            objet.MemoriseImage(figure) 
        else:
            objet.MAJ(DB=DB, dictParametres=dictParametres)
        DB.Close() 
        
        # Création de la page HTML
        html = u"""<HTML><BODY><FONT SIZE=-1><P>%s</P></FONT></BODY></HTML>""" % objet.GetObjetHTML()
        self.ctrl.SetPage(html)



#--- Tests ----------------------------------------------------------------------------------------------------------------------------

##def TESTS():
##    """ Zone de tests """
##    date_debut = datetime.date(2011, 1, 1)
##    date_fin = datetime.date(2011, 12, 31)
##    conditionsActivites = "(1)"
##    
##    DB = GestionDB.DB() 
##    
##    # Recherche des données par individus
##    req = """SELECT IDindividu, MIN(date), MAX(date)
##    FROM consommations
##    WHERE date<='%s' 
##    AND etat IN ('reservation', 'present')
##    AND IDactivite IN %s
##    GROUP BY IDindividu
##    ;""" % (date_fin, conditionsActivites)
##        
##    DB.ExecuterReq(req)
##    listeDonnees = DB.ResultatReq()
##    if len(listeDonnees) == 0 : 
##        return {}
##    
##    dictResultats = {}
##    for IDindividu, dateMin, dateMax in listeDonnees :
##        dateMin = DateEngEnDateDD(dateMin)
##        dateMax = DateEngEnDateDD(dateMax)
##        
##        # Vérifie si individu présent sur la période de référence
##        if dateMax >= date_debut :
##            moisArrivee = (dateMin.year, dateMin.month)
##            if dictResultats.has_key(moisArrivee) == False :
##                dictResultats[moisArrivee] = 0
##            dictResultats[moisArrivee] += 1
##            
##    # Crée tous les mois de la période
##    listeMois = []
##    for annee in range(date_debut.year, date_fin.year+1) :
##        for mois in range(1, 13):
##            if (annee, mois) >= (date_debut.year, date_debut.month) and (annee, mois) <= (date_fin.year, date_fin.month) :
##                listeMois.append((annee, mois))
##
##    print listeMois
##    
##    DB.Close() 

    

if __name__ == "__main__":
    DB = GestionDB.DB() 
    dictParametres = {"mode":"presents", "periode" : {"type":"dates", "date_debut":datetime.date(2012, 2, 1), "date_fin":datetime.date(2012, 2, 12)}}
    date_min = datetime.date(2010, 1, 1)
    date_max = datetime.date(2015, 1, 1)
    
    # Test des périodes
##    listePeriodes = GetPeriodesComparatives(DB, dictParametres, date_min, date_max) 
##    for periode in listePeriodes :
##        print periode
    
    # Test des dates de début et de fin des activités
    for x in GetInfosActivites(DB, listeActivites=[1, 2, 3, 4]) :
        print(x)
    
    # Tests de dates extremes d'un ensemble d'activités
    print(GetDateExtremeActivites(DB, listeActivites=[1, 2, 3, 4], typeDate="date_milieu", mode="max"))
    
        
    DB.Close() 
