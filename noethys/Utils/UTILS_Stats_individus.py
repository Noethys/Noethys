#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

import matplotlib
import matplotlib.pyplot

from numpy import arange 

import UTILS_Stats_modeles as MODELES

try: import psyco; psyco.full()
except: pass


DICT_COMPARATIF_NOMBRE = {"dictParametres" : {}, "dictResultats" : {} }

def GetComparatifNombre(DB, dictParametres) :
    dictResultats = {}
    
    # Vérifie si les données n'existent pas déjà
    global DICT_COMPARATIF_NOMBRE
    if DICT_COMPARATIF_NOMBRE["dictParametres"] == dictParametres :
        return DICT_COMPARATIF_NOMBRE["listeResultats"]
    
    if dictParametres["mode"] == "inscrits" :
        return dictResultats
    
    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)
    
    # Recherche des périodes de comparaison
    req = """SELECT MIN(date), MAX(date) 
    FROM consommations 
    WHERE consommations.etat IN ('reservation', 'present')
    AND IDactivite IN %s
    ;""" % conditionsActivites
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    try :
        if listeDonnees[0][0] == None or listeDonnees[0][1] == None : 
            return dictResultats
        date_min = MODELES.DateEngEnDateDD(listeDonnees[0][0])
        date_max = MODELES.DateEngEnDateDD(listeDonnees[0][1])
    except :
        return dictResultats
    listePeriodes = MODELES.GetPeriodesComparatives(DB, dictParametres, date_min, date_max)
    
    listeLabels = []
    listeValeurs = []
    indexPeriodeReference = 0
    index = 0
    for dictPeriode in listePeriodes :
        req = """SELECT COUNT(IDindividu)
        FROM consommations 
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY IDindividu
        ;""" % (dictPeriode["date_debut"], dictPeriode["date_fin"], conditionsActivites)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        nbreIndividus = len(listeDonnees)
        listeLabels.append(dictPeriode["label"])
        listeValeurs.append(nbreIndividus)
        if dictPeriode["date_debut"] == dictParametres["periode"]["date_debut"] and dictPeriode["date_fin"] == dictParametres["periode"]["date_fin"]:
            indexPeriodeReference = index
        index += 1
        
    dictResultats = {"labels":listeLabels, "valeurs":listeValeurs, "indexPeriodeReference":indexPeriodeReference}
    return dictResultats


DICT_GENRES = {"dictParametres" : {}, "dictResultats" : {} }

def GetDictGenres(DB, dictParametres) :
    # Vérifie si les données n'existent pas déjà
    global DICT_GENRES
    if DICT_GENRES["dictParametres"] == dictParametres :
        return DICT_GENRES["dictResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)

    # Recherche des données par individus
    if dictParametres["mode"] == "presents" :
        req = """SELECT individus.IDindividu, IDcivilite
        FROM individus
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu 
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY individus.IDindividu
        ;""" % (date_debut, date_fin, conditionsActivites)
    else:
        req = """SELECT individus.IDindividu, IDcivilite
        FROM individus
        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu 
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY individus.IDindividu
        ;""" % conditionsActivites
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return {}
    
    from Data import DATA_Civilites
    dictCivilites = DATA_Civilites.GetDictCivilites()
    dictGenres = { 
        "M" : {"quantite" : 0, "label1" : _(u"Garçons"), "label2" : _(u"garçons"), "couleur" : (134, 172, 253) },
        "F" : {"quantite" : 0, "label1" : _(u"Filles"), "label2" : _(u"filles"), "couleur" : (253, 172, 220) },
        "None" : {"quantite" : 0, "label1" : _(u"N.C."), "label2" : _(u"individus dont le genre est inconnu"), "couleur" : (170, 170, 170) },
        }
    for IDindividu, IDcivilite in listeDonnees :
        genre = str(dictCivilites[IDcivilite]["sexe"])
        dictGenres[genre]["quantite"] += 1

    # Mémorisation des résultats
    DICT_GENRES["dictParametres"] = dictParametres
    DICT_GENRES["dictResultats"] = dictGenres
    return dictGenres


DICT_AGES = {"dictParametres" : {}, "dictAges" : {}, "dictAnnees" : {} }

def GetDictAges(DB, dictParametres) :
    # Vérifie si les données n'existent pas déjà
    global DICT_AGES
    if DICT_AGES["dictParametres"] == dictParametres :
        return DICT_AGES["dictAges"], DICT_AGES["dictAnnees"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)
    
    # Recherche des données par individus
    if dictParametres["mode"] == "presents" :
        req = """SELECT individus.IDindividu, date_naiss
        FROM individus
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu 
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY individus.IDindividu
        ;""" % (date_debut, date_fin, conditionsActivites)
    else:
        req = """SELECT individus.IDindividu, date_naiss
        FROM individus
        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu 
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY individus.IDindividu
        ;""" % conditionsActivites
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return {}, {}
    
    dictAges = {}
    dictAnnees = {}
    for IDindividu, date_naiss in listeDonnees :
        if date_naiss != None and date_naiss != "" :
            date_naiss = datetime.date(int(date_naiss[:4]), int(date_naiss[5:7]), int(date_naiss[8:10]))
            if str(date_fin) == "2999-01-01" :
                datedujour = MODELES.GetDateExtremeActivites(DB, listeActivites=dictParametres["listeActivites"], typeDate="date_milieu", mode="max")
            else :
                datedujour = date_fin
            if datedujour == None :
                datedujour = datetime.date.today() 
            age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
            annee = date_naiss.year
        else:
            age = None
            annee = None
        
        if (age in dictAges) == False :
            dictAges[age] = 0
        dictAges[age] += 1

        if (annee in dictAnnees) == False :
            dictAnnees[annee] = 0
        dictAnnees[annee] += 1

    # Mémorisation des résultats
    DICT_AGES["dictParametres"] = dictParametres
    DICT_AGES["dictAges"] = dictAges
    DICT_AGES["dictAnnees"] = dictAnnees
    return dictAges, dictAnnees


DICT_DISTANCES_VILLES = {"dictParametres" : {}, "dictDistances" : {} }

def GetDistancesVilles(dictParametres, origine="", destinations=[]):
    global DICT_DISTANCES_VILLES
    
    # Vérifie si les données n'existent pas déjà
    if DICT_DISTANCES_VILLES["dictParametres"] == dictParametres :
        return DICT_DISTANCES_VILLES["dictDistances"]
    
    # Sinon on les recherche
    import UTILS_Distances_villes
    dictDistances = UTILS_Distances_villes.GetDistances(origine, destinations) 
    
    # Mémorisation des résultats
    DICT_DISTANCES_VILLES["dictParametres"] = dictParametres
    DICT_DISTANCES_VILLES["dictDistances"] = dictDistances
    return dictDistances


DICT_VILLES = {"dictParametres" : {}, "dictResultats" : {} }

def GetDictVilles(DB, dictParametres):
    # Vérifie si les données n'existent pas déjà
    global DICT_VILLES
    if DICT_VILLES["dictParametres"] == dictParametres :
        return DICT_VILLES["dictResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)

    import UTILS_Titulaires
    dictTitulaires = UTILS_Titulaires.GetTitulaires() 
    
    # Récupère les adresses de tous les individus de la base
    req = """SELECT IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid FROM individus;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictInfos = {}
    for IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid in listeDonnees :
        dictInfos[IDindividu] = { "nom" : nom, "prenom" : prenom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid}
    
    # Recherche les individus présents
    if dictParametres["mode"] == "presents" :
        req = """SELECT individus.IDindividu, adresse_auto
        FROM individus
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu 
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY individus.IDindividu
        ;""" % (date_debut, date_fin, conditionsActivites)
    else:
        req = """SELECT individus.IDindividu, adresse_auto
        FROM individus
        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu 
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY individus.IDindividu
        ;""" % conditionsActivites
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return {}

    dictVilles = {}
    destinations = []
    for IDindividu, adresse_auto in listeDonnees :
        
        # Recherche de l'adresse de l'individu
        if adresse_auto != None and adresse_auto in dictInfos :
            rue_resid = dictInfos[adresse_auto]["rue_resid"]
            cp_resid = dictInfos[adresse_auto]["cp_resid"]
            ville_resid = dictInfos[adresse_auto]["ville_resid"]
        else:
            rue_resid = dictInfos[IDindividu]["rue_resid"]
            cp_resid = dictInfos[IDindividu]["cp_resid"]
            ville_resid = dictInfos[IDindividu]["ville_resid"]
    
        # Synthèse des infos
        if ((cp_resid, ville_resid) in dictVilles) == False :
            dictVilles[(cp_resid, ville_resid)] = {"nbreIndividus" : 0, "distance" : "", "distance_metres" : 0}
            if cp_resid != None and ville_resid != None :
                destinations.append((cp_resid, ville_resid))
        dictVilles[(cp_resid, ville_resid)]["nbreIndividus"] += 1
    
    # Récupère les distances entre les villes
    dictDistances = {}
    try :
        req = """SELECT cp, ville FROM organisateur
        WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        cp, ville = listeDonnees[0]
        if  cp != None and cp != "" and ville != None and ville != "" :
            origine = listeDonnees[0]
            dictDistances = GetDistancesVilles(dictParametres, origine, destinations)
    except :
        pass

    for key, valeurs in dictVilles.items() :
        if key in dictDistances and key != origine :
            dictVilles[key]["distance"] = dictDistances[key]["distance_texte"]
            dictVilles[key]["distance_metres"] = dictDistances[key]["distance_metres"]

    # Mémorisation des résultats
    DICT_VILLES["dictParametres"] = dictParametres
    DICT_VILLES["dictResultats"] = dictVilles
    return dictVilles



DICT_ACTI_PRO = {"dictParametres" : {}, "dictResultats" : [] }

def GetListeActivitesPro(DB, dictParametres) :
    # Vérifie si les données n'existent pas déjà
    global DICT_ACTI_PRO
    if DICT_ACTI_PRO["dictParametres"] == dictParametres :
        return DICT_ACTI_PRO["dictResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)

    # Recherche des données par individus
    if dictParametres["mode"] == "presents" :
        req = """SELECT individus.IDcategorie_travail, categories_travail.nom, COUNT(individus.IDindividu)
        FROM individus
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu 
        LEFT JOIN categories_travail ON categories_travail.IDcategorie = individus.IDcategorie_travail
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY IDcategorie_travail, consommations.IDindividu
        ;""" % (date_debut, date_fin, conditionsActivites)
    else :
        req = """SELECT individus.IDcategorie_travail, categories_travail.nom, COUNT(individus.IDindividu)
        FROM individus
        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu 
        LEFT JOIN categories_travail ON categories_travail.IDcategorie = individus.IDcategorie_travail
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY IDcategorie_travail, inscriptions.IDindividu
        ;""" % conditionsActivites
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return []
    
    dictCategories = {}
    for IDcategorie, nomCategorie, IDindividu in listeDonnees :
        if nomCategorie == None :
            nomCategorie = _(u"Catégorie inconnue")
        if (IDcategorie in dictCategories) == False :
            dictCategories[IDcategorie] = {"nom" : nomCategorie, "nbre" : 0}
        dictCategories[IDcategorie]["nbre"] += 1

    listeResultats = []
    for IDcategorie, valeurs in dictCategories.items() :
        listeResultats.append((valeurs["nbre"], valeurs["nom"]))
    listeResultats.sort(reverse=True)

    # Mémorisation des résultats
    DICT_ACTI_PRO["dictParametres"] = dictParametres
    DICT_ACTI_PRO["dictResultats"] = listeResultats
    return listeResultats


DICT_ANCIENNETE = {"dictParametres" : {}, "dictResultats" : {}, "listeMoisPeriode" : [] }

def GetAnciennete(DB, dictParametres):
    # Vérifie si les données n'existent pas déjà
    global DICT_ANCIENNETE
    if DICT_ANCIENNETE["dictParametres"] == dictParametres :
        return DICT_ANCIENNETE["dictResultats"], DICT_ANCIENNETE["listeMoisPeriode"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)
    
    if dictParametres["mode"] != "presents" :
        return {}, []
        
    req = """SELECT IDindividu, MIN(date), MAX(date)
    FROM consommations
    WHERE date<='%s' 
    AND consommations.etat IN ('reservation', 'present')
    AND IDactivite IN %s
    GROUP BY IDindividu
    ;""" % (date_fin, conditionsActivites)
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return {}, []
    
    dictResultats = {}
    for IDindividu, dateMin, dateMax in listeDonnees :
        dateMin = MODELES.DateEngEnDateDD(dateMin)
        dateMax = MODELES.DateEngEnDateDD(dateMax)
        
        # Vérifie si individu présent sur la période de référence
        if dateMax >= date_debut :
            moisArrivee = (dateMin.year, dateMin.month)
            if (moisArrivee in dictResultats) == False :
                dictResultats[moisArrivee] = 0
            dictResultats[moisArrivee] += 1
            
    # Crée tous les mois de la période
    listeMoisPeriode = []
    for annee in range(date_debut.year, date_fin.year+1) :
        for mois in range(1, 13):
            if (annee, mois) >= (date_debut.year, date_debut.month) and (annee, mois) <= (date_fin.year, date_fin.month) :
                listeMoisPeriode.append((annee, mois))

    # Mémorisation des résultats
    DICT_ANCIENNETE["dictParametres"] = dictParametres
    DICT_ANCIENNETE["dictResultats"] = dictResultats
    DICT_ANCIENNETE["listeMoisPeriode"] = listeMoisPeriode
    return dictResultats, listeMoisPeriode


DICT_ECOLES = {"dictParametres" : {}, "listeResultats" : [] }

def GetListeEcoles(DB, dictParametres) :
    # Vérifie si les données n'existent pas déjà
    global DICT_ECOLES
    if DICT_ECOLES["dictParametres"] == dictParametres :
        return DICT_ECOLES["listeResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)

    # Recherche des données par individus
    if dictParametres["mode"] == "presents" :
        req = """SELECT scolarite.IDecole, ecoles.nom, COUNT(individus.IDindividu)
        FROM individus
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu 
        LEFT JOIN scolarite ON scolarite.IDindividu = individus.IDindividu AND scolarite.date_debut <= '%s' AND scolarite.date_fin >= '%s'
        LEFT JOIN ecoles ON scolarite.IDecole = ecoles.IDecole
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY scolarite.IDecole, consommations.IDindividu
        ;""" % (date_debut, date_debut, date_debut, date_fin, conditionsActivites)
    else :
        return []
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return []
    
    dictEcoles = {}
    for IDecole, nomEcole, IDindividu in listeDonnees :
        if nomEcole == None :
            nomEcole = _(u"Ecole inconnue")
        if (IDecole in dictEcoles) == False :
            dictEcoles[IDecole] = {"nom" : nomEcole, "nbre" : 0}
        dictEcoles[IDecole]["nbre"] += 1

    listeResultats = []
    for IDecole, valeurs in dictEcoles.items() :
        listeResultats.append((valeurs["nbre"], valeurs["nom"]))
    listeResultats.sort(reverse=True)

    # Mémorisation des résultats
    DICT_ECOLES["dictParametres"] = dictParametres
    DICT_ECOLES["listeResultats"] = listeResultats
    return listeResultats


DICT_NIVEAUX_SCOLAIRES = {"dictParametres" : {}, "listeResultats" : [] }

def GetListeNiveauxScolaires(DB, dictParametres) :
    # Vérifie si les données n'existent pas déjà
    global DICT_NIVEAUX_SCOLAIRES
    if DICT_NIVEAUX_SCOLAIRES["dictParametres"] == dictParametres :
        return DICT_NIVEAUX_SCOLAIRES["listeResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)

    # Recherche des données par individus
    if dictParametres["mode"] == "presents" :
        req = """SELECT scolarite.IDniveau, niveaux_scolaires.ordre, niveaux_scolaires.abrege, COUNT(individus.IDindividu)
        FROM individus
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu 
        LEFT JOIN scolarite ON scolarite.IDindividu = individus.IDindividu AND scolarite.date_debut <= '%s' AND scolarite.date_fin >= '%s'
        LEFT JOIN niveaux_scolaires ON niveaux_scolaires.IDniveau = scolarite.IDniveau
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY scolarite.IDecole, consommations.IDindividu
        ;""" % (date_debut, date_debut, date_debut, date_fin, conditionsActivites)
    else :
        return []
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return []
    
    dictNiveaux = {}
    for IDniveau, ordre, nomNiveau, IDindividu in listeDonnees :
        if nomNiveau == None :
            nomNiveau = _(u"Niveau inconnu")
        if (IDniveau in dictNiveaux) == False :
            dictNiveaux[IDniveau] = {"nom" : nomNiveau, "nbre" : 0, "ordre": ordre}
        dictNiveaux[IDniveau]["nbre"] += 1

    listeResultats = []
    for IDniveau, valeurs in dictNiveaux.items() :
        listeResultats.append((valeurs["ordre"], valeurs["nbre"], valeurs["nom"]))
    listeResultats.sort()

    # Mémorisation des résultats
    DICT_NIVEAUX_SCOLAIRES["dictParametres"] = dictParametres
    DICT_NIVEAUX_SCOLAIRES["listeResultats"] = listeResultats
    return listeResultats


class Texte_nombre_individus(MODELES.Texte):
    def __init__(self):
        """ Recherche du nombre d'individus présents """
        MODELES.Texte.__init__(self)
        self.nom = _(u"Nombre d'individus")
        self.code = "texte_nombre_individus"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        conditionsActivites = MODELES.GetConditionActivites(dictParametres)
        
        # Recherche du nombre d'individus présents
        if dictParametres["mode"] == "presents" :
            req = """SELECT COUNT(IDindividu)
            FROM consommations 
            WHERE date>='%s' AND date<='%s' 
            AND consommations.etat IN ('reservation', 'present')
            AND IDactivite IN %s
            GROUP BY IDindividu
            ;""" % (date_debut, date_fin, conditionsActivites)
        else :
            req = """SELECT COUNT(IDindividu)
            FROM inscriptions 
            WHERE inscriptions.statut='ok' AND IDactivite IN %s
            GROUP BY IDindividu
            ;""" % conditionsActivites
        
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        if dictParametres["mode"] == "presents" :
            mot = _(u"présent")
        else:
            mot = _(u"inscrit")
            
        if len(listeDonnees) == 0 or listeDonnees[0][0] == 0 : 
            self.texte = _(u"Aucun individu %s.") % mot
        else:
            self.texte = _(u"%d individus %ss.") % (len(listeDonnees), mot)
        
        
class Tableau_nombre_individus(MODELES.Tableau):
    """ Répartition du nombre d'individus par activité """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition du nombre d'individus par activité")
        self.code = "tableau_nombre_individus"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        # Recherche des paramètres
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        conditionsActivites = MODELES.GetConditionActivites(dictParametres)

        # Recherche du nombre d'individus présents
        if dictParametres["mode"] == "presents" :
            req = """SELECT IDactivite, COUNT(IDindividu)
            FROM consommations 
            WHERE date>='%s' AND date<='%s' 
            AND consommations.etat IN ('reservation', 'present')
            AND IDactivite IN %s
            GROUP BY IDactivite, IDindividu
            ;""" % (date_debut, date_fin, conditionsActivites)
        else:
            req = """SELECT IDactivite, COUNT(IDindividu)
            FROM inscriptions 
            WHERE inscriptions.statut='ok' AND IDactivite IN %s
            GROUP BY IDactivite, IDindividu
            ;""" % conditionsActivites
            
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : 
            return
        
        dictActiTemp = {}
        for IDactivite, nbreConso in listeDonnees :
            if (IDactivite in dictActiTemp) == False :
                dictActiTemp[IDactivite] = 0
            dictActiTemp[IDactivite] += 1
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Activité"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
        for IDactivite, listeIndividus in dictActiTemp.items() :
            nomActivite = dictParametres["dictActivites"][IDactivite]
            self.lignes.append((nomActivite, listeIndividus))

class Graphe_nombre_individus(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Comparatif du nombre d'individus")
        self.code = "graphe_nombre_individus"
        self.taille = (470, 360)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictResultats = GetComparatifNombre(DB, dictParametres)
        if dictResultats == None or len(dictResultats) == 0 :
            return figure
        
        listeLabels = dictResultats["labels"]
        listeValeurs = dictResultats["valeurs"]
        indexPeriodeReference = dictResultats["indexPeriodeReference"]
        
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        for x in range(len(listeLabels)) :
            if x == indexPeriodeReference :
                couleur = MODELES.ConvertitCouleur2(MODELES.COULEUR_VERT_POMME)
            else:
                couleur = MODELES.ConvertitCouleur2(MODELES.COULEUR_BLEU_CIEL)
            barre = ax.bar(ind[x], listeValeurs[x], width, color=couleur)
        
        # Axe horizontal
        ind = arange(len(listeLabels)) 
        ax.set_xticks(ind + width) 
        ax.set_xticklabels(listeLabels)
        labelsx = ax.get_xticklabels()
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=9, horizontalalignment='right')
        
        # Axe vertical
        ax.set_ylabel("Nbre d'individus", fontsize=8)
        
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Comparatif du nombre d'individus"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.4, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure


        
class Tableau_repartition_genre(MODELES.Tableau):
    """ Répartition des individus par âge """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition par genre")
        self.code = "tableau_repartition_genre"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictGenres = GetDictGenres(DB, dictParametres)
                
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Genre"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
        
        for IDgenre, dictTemp in dictGenres.items() :
            if dictTemp["quantite"] > 0 :
                self.lignes.append((dictTemp["label1"], dictTemp["quantite"]))




class Graphe_repartition_genre(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition par genre")
        self.code = "graphe_repartition_genre"
        self.taille = (350, 250)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictGenres = GetDictGenres(DB, dictParametres)
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        for IDgenre, dictTemp in dictGenres.items() :
            if dictTemp["quantite"] > 0 :
                listeValeurs.append(dictTemp["quantite"])
                listeLabels.append(dictTemp["label1"])
                listeCouleurs.append(MODELES.ConvertitCouleur2(dictTemp["couleur"]))

        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(_(u"Répartition par genre"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 

        return figure




class Tableau_repartition_ages(MODELES.Tableau):
    """ Répartition des individus par âge """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des individus par âge")
        self.code = "tableau_repartition_ages"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictAges, dictAnnees = GetDictAges(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Age"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
        
        listeAges = list(dictAges.keys()) 
        listeAges.sort() 
        
        for age in listeAges :
            nbreIndividus = dictAges[age]
            if age == None : 
                age = _(u"Date de naissance inconnue")
            else :
                age = str(age)
            self.lignes.append((age, nbreIndividus))




class Graphe_repartition_ages(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition des individus par âge")
        self.code = "graphe_repartition_ages"
        self.taille = (470, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictAges, dictAnnees = GetDictAges(DB, dictParametres)
        
        listeAges = list(dictAges.keys()) 
        listeAges.sort() 
        
        listeLabels = [] 
        listeValeurs = []
        for age in listeAges :
            nbreIndividus = dictAges[age]
            if age == None : 
                age = _(u"N.C.")
            else :
                age = str(age)
            listeLabels.append(age)
            listeValeurs.append(nbreIndividus)
        
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        barres = ax.bar(ind, listeValeurs, width, color=MODELES.ConvertitCouleur2(MODELES.COULEUR_VERT_POMME))
        
        # Axe horizontal
        ax.set_xlabel(_(u"Ages"), fontsize=8)
        ind = arange(len(listeLabels)) 
        ax.set_xticks(ind + width) 
        ax.set_xticklabels(listeLabels)
        labelsx = ax.get_xticklabels()
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=0, fontsize=9, horizontalalignment='center')
        
        # Axe vertical
        ax.set_ylabel("Nbre d'individus", fontsize=8)
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Répartition par âge"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.12, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure



class Tableau_repartition_annees_naiss(MODELES.Tableau):
    """ Répartition des individus par âge """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des individus par année de naissance")
        self.code = "tableau_repartition_annees_naiss"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictAges, dictAnnees = GetDictAges(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Année de naissance"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
        
        listeAnnees = list(dictAnnees.keys()) 
        listeAnnees.sort() 
        
        for annee in listeAnnees :
            nbreIndividus = dictAnnees[annee]
            if annee == None : 
                annee = _(u"Année de naissance inconnue")
            else :
                annee = str(annee)
            self.lignes.append((annee, nbreIndividus))




class Graphe_repartition_annees_naiss(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition des individus par année de naissance")
        self.code = "graphe_repartition_annees_naiss"
        self.taille = (470, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictAges, dictAnnees = GetDictAges(DB, dictParametres)
        
        listeAnnees = list(dictAnnees.keys()) 
        listeAnnees.sort() 
        
        listeLabels = [] 
        listeValeurs = []
        for annee in listeAnnees :
            nbreIndividus = dictAnnees[annee]
            if annee == None : 
                annee = _(u"N.C.")
            else :
                annee = str(annee)
            listeLabels.append(annee)
            listeValeurs.append(nbreIndividus)
        
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        barres = ax.bar(ind, listeValeurs, width, color=MODELES.ConvertitCouleur2(MODELES.COULEUR_BLEU_CIEL))
        
        # Axe horizontal
        ax.set_xlabel(_(u"Années"), fontsize=8)
        
        ind = arange(len(listeLabels)) 
        ax.set_xticks(ind + width) 
        ax.set_xticklabels(listeLabels)
        labelsx = ax.get_xticklabels()
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=9, horizontalalignment='right')
        
        # Axe vertical
        ax.set_ylabel("Nbre d'individus", fontsize=8)
        
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Répartition par année de naissance"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.2, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure
    


class Tableau_repartition_villes(MODELES.Tableau):
    """ Répartition des individus par villes de résidence """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des individus par ville de résidence")
        self.code = "tableau_repartition_villes"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictVilles = GetDictVilles(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Ville de résidence"), "210"), (_(u"Distance"), "70"), (_(u"Nombre d'individus"), "120") ]
        self.lignes = []
        
        # Tri par nbre d'individus
        listeVilles = []
        for key, valeurs in dictVilles.items() :
            cpVille, nomVille = key
            nbreIndividus = valeurs["nbreIndividus"]
            distance = valeurs["distance"]
            listeVilles.append((nbreIndividus, nomVille, distance))
        listeVilles.sort(reverse=True)
        
        for nbreIndividus, nomVille, distance in listeVilles :
            if nomVille == None : 
                nomVille = _(u"Ville inconnue")
            self.lignes.append((nomVille, distance, nbreIndividus))



class Graphe_repartition_villes(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition par ville de résidence")
        self.code = "graphe_repartition_villes"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictVilles = GetDictVilles(DB, dictParametres)
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        # Tri par nbre d'individus
        listeVilles = []
        nbreTotalIndividus = 0
        for key, valeurs in dictVilles.items() :
            cpVille, nomVille = key
            nbreIndividus = valeurs["nbreIndividus"]
            listeVilles.append((nbreIndividus, nomVille))
            nbreTotalIndividus += nbreIndividus
        listeVilles.sort(reverse=True)
        
        # Ne garde que les premiers
        nbreMax = 5
        if len(listeVilles) > nbreMax :
            nbreAutres = 0
            for nbreIndividus, nomVille in listeVilles[nbreMax:] :
                nbreAutres += nbreIndividus
            listeVilles = listeVilles[:nbreMax]
            listeVilles.append((nbreAutres, _(u"Autres")))
        
        index = 1
        for nbreIndividus, nomVille in listeVilles :
            if nomVille == None : 
                nomVille = _(u"N.C.")

            listeValeurs.append(nbreIndividus)
            listeLabels.append(nomVille)
            
            couleur = 1.0 * nbreIndividus / nbreTotalIndividus
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
            
##            couleurRGB = HSVToRGB(couleurHSV)
##            listeCouleurs.append(ConvertitCouleur2(couleurRGB))
##            couleurHSV = (couleurHSV[0], couleurHSV[1]-20, couleurHSV[2])
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(_(u"Répartition par ville"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure





##class Graphe_distances_villes(Graphe):
##    def __init__(self):
##        Graphe.__init__(self)
##        self.nom = _(u"Distances et répartition par ville")
##        self.code = "graphe_distances_villes"
##        self.taille = (450, 280)
##    def MAJ(self, DB=None, dictParametres={}):
##        self.dictParametres = dictParametres
##        # Création du graph
##        self.figure = matplotlib.pyplot.figure()
##        ax = self.figure.add_subplot(111)
##        
##        dictVilles = GetDictVilles(DB, dictParametres)
##        
##        # Tri par distance
##        listeVilles = []
##        nbreTotalIndividus = 0
##        for key, valeurs in dictVilles.iteritems() :
##            cpVille, nomVille = key
##            nbreIndividus = valeurs["nbreIndividus"]
##            distance = valeurs["distance_metres"]
##            listeVilles.append((distance, nomVille, nbreIndividus))
##            nbreTotalIndividus += nbreIndividus
##        listeVilles.sort(reverse=False)
##        
##        listeX = []
##        listeY = []
##        listeCouleurs = []
##        listeVolumes = []
##        listeLabels = []
##        
##        index = 0
##        for distance, nomVille, nbreIndividus in listeVilles :
##            if nomVille != None and distance != None : 
##                
##                if index / 2.0 == index / 2 * 1.0 :
##                    x = 1
##                else:
##                    x = -1
##                    
##                y = distance / 1000.0
##                listeX.append(x)
##                listeY.append(y)
##                
##                couleur = 1.0 * index / len(listeVilles) 
##                couleur = matplotlib.cm.jet(couleur)
##                listeCouleurs.append(couleur)
##            
##                listeLabels.append((x, y, nomVille))
##                listeVolumes.append(nbreIndividus*100)
##                
##                index += 1
##
##        ax.scatter(listeX, listeY, c=listeCouleurs, s=listeVolumes, edgecolors='none', alpha=0.5)
##        
##        for x, y, label in listeLabels :
##            ax.annotate(label, (x, y), va="center", ha="center", size=6)
##
##        title = ax.set_title(_(u"Distances entre les villes"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
##        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
##
##        ax.set_ylabel("Distances", fontsize=8)
##        matplotlib.pyplot.setp(ax.get_yticklabels(), rotation=0, fontsize=9) 
##        matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=0, fontsize=0) 
##            
##        # Mémorise l'image du graphe
##        self.MemoriseImage() 




class Tableau_activites_professionnelles(MODELES.Tableau):
    """ Répartition des individus par activité professionnelle """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des individus par activité professionnelle")
        self.code = "tableau_activites_professionnelles"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        listeCategories = GetListeActivitesPro(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Activité professionnelle"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
                
        for nbreIndividus, nomCategorie in listeCategories :
            self.lignes.append((nomCategorie, nbreIndividus))




class Graphe_activites_professionnelles(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition par activité professionnelle")
        self.code = "graphe_activites_professionnelles"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        listeCategories = GetListeActivitesPro(DB, dictParametres)
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        index = 1
        for nbreIndividus, nomCategorie in listeCategories :
            listeValeurs.append(nbreIndividus)
            listeLabels.append(nomCategorie)
            
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(_(u"Répartition par activité professionnelle"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure




class Tableau_nouveaux_individus(MODELES.Tableau):
    """ Ancienneté """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Nouveaux individus (selon le premier jour de présence)")
        self.code = "tableau_nouveaux_individus"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        dictResultats, listeMoisPeriode = GetAnciennete(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Mois"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
        
        for annee, mois in listeMoisPeriode :
            if (annee, mois) in dictResultats :
                label = u"%s %s" % (MODELES.LISTE_NOMS_MOIS[mois-1], annee)
                self.lignes.append((label, dictResultats[(annee, mois)]))




class Graphe_nouveaux_individus(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Nouveaux individus")
        self.code = "graphe_nouveaux_individus"
        self.taille = (470, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictResultats, listeMoisPeriode = GetAnciennete(DB, dictParametres)
        
        listeLabels = [] 
        listeValeurs = []
        
        for annee, mois in listeMoisPeriode :
            label = u"%s %s" % (MODELES.LISTE_NOMS_MOIS[mois-1], annee)
            if (annee, mois) in dictResultats :
                nbreIndividus = dictResultats[(annee, mois)]
            else :
                nbreIndividus = 0
            listeLabels.append(label)
            listeValeurs.append(nbreIndividus)
        
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        barres = ax.bar(ind, listeValeurs, width, color=MODELES.ConvertitCouleur2(MODELES.COULEUR_VERT_POMME))
        
        # Axe horizontal
        ind = arange(len(listeLabels)) 
        ax.set_xticks(ind + width) 
        ax.set_xticklabels(listeLabels)
        labelsx = ax.get_xticklabels()
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=8, horizontalalignment='right')
        
        # Axe vertical
        ax.set_ylabel(_(u"Nbre d'individus"), fontsize=8)
        
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Nouveaux individus sur la période"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.3, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure



class Graphe_arrivee_individus(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Arrivée des individus présents")
        self.code = "graphe_arrivee_individus"
        self.taille = (470, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictResultats, listeMoisPeriode = GetAnciennete(DB, dictParametres)
        
        listeX = []
        listeY = []
        for annee, mois in listeMoisPeriode :
            if (annee, mois) in dictResultats :
                nbreIndividus = dictResultats[(annee, mois)]
            else :
                nbreIndividus = 0
            
            date = datetime.date(annee, mois, 1)
            listeX.append(date)
            listeY.append(nbreIndividus)
        
        # Création du graph
        ax.plot(listeX, listeY)
        
        # Affiche les grilles
        ax.grid(True)

        # Axe horizontal
        datemin = datetime.date(date_debut.year, 1, 1)
        datemax = datetime.date(date_fin.year+1, 1, 1)
        ax.set_xlim(datemin, datemax)
        labelsx = ax.get_xticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=8, horizontalalignment='right')
        figure.autofmt_xdate()
        
        # Axe vertical
        ax.set_ylabel(_(u"Nbre d'individus"), fontsize=8)
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsy, rotation=0, fontsize=9) 
        
        # Ligne moyenne
##        if len(listeY) > 4 :
##            ligne = MODELES.Ligne_moyenne(listeY, len(listeY) / 4, type='simple')
##            ax.plot(listeX, ligne, color='red', lw=1, label=_(u"Evolution moyenne"))

        # Titre
        title = ax.set_title(_(u"Arrivée des individus présents"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.3, right=None, wspace=None, hspace=None)
        
        return figure


class Tableau_repartition_ecoles(MODELES.Tableau):
    """ Répartition des individus par activité professionnelle """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des individus par école <BR>(au premier jour de la période)")
        self.code = "tableau_repartition_ecoles"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        listeEcoles = GetListeEcoles(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Ecole"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
                
        for nbreIndividus, nomEcole in listeEcoles :
            self.lignes.append((nomEcole, nbreIndividus))




class Graphe_repartition_ecoles(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition des individus par école <BR>(au premier jour de la période)")
        self.code = "graphe_repartition_ecoles"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        listeEcoles = GetListeEcoles(DB, dictParametres)
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        index = 1
        for nbreIndividus, nomEcole in listeEcoles :
            listeValeurs.append(nbreIndividus)
            listeLabels.append(nomEcole)
            
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(_(u"Répartition des individus par école"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure





class Tableau_repartition_niveaux_scolaires(MODELES.Tableau):
    """ Répartition des individus par niveau scolaire """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des individus par niveau scolaire <BR>(au premier jour de la période)")
        self.code = "tableau_repartition_niveaux_scolaires"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        listeNiveaux = GetListeNiveauxScolaires(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Niveau scolaire"), "250"), (_(u"Nombre d'individus"), "150") ]
        self.lignes = []
                
        for ordre, nbreIndividus, nomNiveau in listeNiveaux :
            self.lignes.append((nomNiveau, nbreIndividus))




class Graphe_repartition_niveaux_scolaires(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition des individus par niveau scolaire <BR>(au premier jour de la période)")
        self.code = "graphe_repartition_niveaux_scolaires"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        listeNiveaux = GetListeNiveauxScolaires(DB, dictParametres)
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        index = 1
        for ordre, nbreIndividus, nomNiveau in listeNiveaux :
            listeValeurs.append(nbreIndividus)
            listeLabels.append(nomNiveau)
            
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(_(u"Répartition des individus par niveau scolaire"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure


if __name__ == '__main__':
    """ TEST d'un objet """
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    annee = 2012
    dictParametres = {
        "mode" : "presents",
        "periode" : {"type":"annee", "annee":annee, "date_debut":datetime.date(annee, 1, 1), "date_fin":datetime.date(annee, 12, 31)}, 
        "listeActivites" : [1, 2, 3, 4, 5], 
        "dictActivites" : {1 : _(u"Centre de Loisirs"), 2 : _(u"Action 10-14 ans"), 3 : _(u"Camp 4-6 ans"), 4 : _(u"Camp 6-9 ans"), 5 : _(u"Camp 10-14 ans"), 6 : _(u"Art floral"), 7 : _(u"Yoga")}, 
        }
    frame_1 = MODELES.FrameTest(objet=Graphe_repartition_niveaux_scolaires(), dictParametres=dictParametres)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()



