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
        req = """SELECT COUNT(IDfamille)
        FROM consommations 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY comptes_payeurs.IDfamille
        ;""" % (dictPeriode["date_debut"], dictPeriode["date_fin"], conditionsActivites)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        nbreFamilles = len(listeDonnees)
        listeLabels.append(dictPeriode["label"])
        listeValeurs.append(nbreFamilles)
        if dictPeriode["date_debut"] == dictParametres["periode"]["date_debut"] and dictPeriode["date_fin"] == dictParametres["periode"]["date_fin"]:
            indexPeriodeReference = index
        index += 1
        
    dictResultats = {"labels":listeLabels, "valeurs":listeValeurs, "indexPeriodeReference":indexPeriodeReference}
    return dictResultats



DICT_CAISSES = {"dictParametres" : {}, "dictResultats" : {} }

def GetDictCaisses(DB, dictParametres):
    # Vérifie si les données n'existent pas déjà
    global DICT_CAISSES
    if DICT_CAISSES["dictParametres"] == dictParametres :
        return DICT_CAISSES["dictResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)
    
    req = """SELECT IDcaisse, nom FROM caisses;"""
    DB.ExecuterReq(req)
    listeCaisses = DB.ResultatReq()
    dictCaisses = {}
    for IDcaisse, nom in listeCaisses :
        dictCaisses[IDcaisse] = nom

    if dictParametres["mode"] == "presents" :
        req = """SELECT IDcaisse, COUNT(familles.IDfamille)
        FROM familles
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        LEFT JOIN consommations ON consommations.IDcompte_payeur = comptes_payeurs.IDcompte_payeur
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY IDcaisse, familles.IDfamille
        ;""" % (date_debut, date_fin, conditionsActivites)
    else:
        req = """SELECT IDcaisse, COUNT(familles.IDfamille)
        FROM familles
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        LEFT JOIN inscriptions ON inscriptions.IDcompte_payeur = comptes_payeurs.IDcompte_payeur
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY IDcaisse, familles.IDfamille
        ;""" % conditionsActivites
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return {}
    
    dictResultats = {}
    for IDcaisse, IDfamille in listeDonnees :
        if dictResultats.has_key(IDcaisse) == False :
            if dictCaisses.has_key(IDcaisse) :
                nom = dictCaisses[IDcaisse] 
            else :
                nom = _(u"Caisse inconnue")
            dictResultats[IDcaisse] = {"nom" : nom, "nbreFamilles" : 0}
        dictResultats[IDcaisse]["nbreFamilles"] += 1

    # Mémorisation des résultats
    DICT_CAISSES["dictParametres"] = dictParametres
    DICT_CAISSES["dictResultats"] = dictResultats
    return dictResultats


DICT_MEMBRES = {"dictParametres" : {}, "dictResultats" : {} }

def GetDictMembres(DB, dictParametres):
    # Vérifie si les données n'existent pas déjà
    global DICT_MEMBRES
    if DICT_MEMBRES["dictParametres"] == dictParametres :
        return DICT_MEMBRES["dictResultats"]

    # Recherche des paramètres
    date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)
    
    # Recherche du nombre d'individus présents
    if dictParametres["mode"] == "presents" :
        req = """SELECT IDfamille, consommations.IDindividu
        FROM consommations 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY IDfamille, consommations.IDindividu
        ;""" % (date_debut, date_fin, conditionsActivites)
    else:
        req = """SELECT comptes_payeurs.IDfamille, inscriptions.IDindividu
        FROM inscriptions 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = inscriptions.IDcompte_payeur
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY comptes_payeurs.IDfamille, inscriptions.IDindividu
        ;""" % conditionsActivites
        
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        return {}
    
    dictFamilles = {}
    for IDfamille, IDindividu in listeDonnees :
        if dictFamilles.has_key(IDfamille) == False :
            dictFamilles[IDfamille] = 0
        dictFamilles[IDfamille] += 1
    
    dictResultats = {}
    for IDfamille, nbreMembres in dictFamilles.iteritems() :
        if dictResultats.has_key(nbreMembres) == False :
            dictResultats[nbreMembres] = 0
        dictResultats[nbreMembres] += 1

    # Mémorisation des résultats
    DICT_MEMBRES["dictParametres"] = dictParametres
    DICT_MEMBRES["dictResultats"] = dictResultats
    return dictResultats


# --------------------------------------------------------------------------------------------------------------------------------------------------------------

DICT_QUOTIENTS = {"dictParametres" : {}, "dictResultats" : {} }

def GetDictQuotients(DB, dictParametres):
    # Vérifie si les données n'existent pas déjà
    global DICT_QUOTIENTS
    if DICT_QUOTIENTS["dictParametres"] == dictParametres :
        return DICT_QUOTIENTS["dictResultats"]

    # Recherche des paramètres
    conditionsActivites = MODELES.GetConditionActivites(dictParametres)
    
    if True : #dictParametres["mode"] == "presents" :
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        req = """SELECT familles.IDfamille, IDquotient, date_debut, date_fin, quotient
        FROM familles
        LEFT JOIN quotients ON quotients.IDfamille = familles.IDfamille
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        LEFT JOIN consommations ON consommations.IDcompte_payeur = comptes_payeurs.IDcompte_payeur
        WHERE date>='%s' AND date<='%s' 
        AND consommations.etat IN ('reservation', 'present')
        AND IDactivite IN %s
        GROUP BY familles.IDfamille, IDquotient
        ;""" % (date_debut, date_fin, conditionsActivites)
    else:
        date_debut = MODELES.GetDateExtremeActivites(DB, listeActivites=dictParametres["listeActivites"], typeDate="date_debut", mode="min")
        date_fin = MODELES.GetDateExtremeActivites(DB, listeActivites=dictParametres["listeActivites"], typeDate="date_fin", mode="max")
        req = """SELECT familles.IDfamille, IDquotient, date_debut, date_fin, quotient
        FROM familles
        LEFT JOIN quotients ON quotients.IDfamille = familles.IDfamille
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        LEFT JOIN inscriptions ON inscriptions.IDcompte_payeur = comptes_payeurs.IDcompte_payeur
        WHERE inscriptions.statut='ok' AND IDactivite IN %s
        GROUP BY familles.IDfamille, IDquotient
        ;""" % conditionsActivites

    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictQuotients = {}
    for IDfamille, IDquotient, date_debut_qf, date_fin_qf, quotient in listeDonnees :
        if IDquotient == None or (date_debut_qf <= str(date_fin) and date_fin_qf >= str(date_debut)) :
            dictQuotients[IDfamille] = quotient
        else :
            dictQuotients[IDfamille] = None
    
    # Recherche des tranches de QF existantes
    req = """SELECT IDligne, qf_min, qf_max
    FROM tarifs_lignes
    WHERE IDactivite IN %s
    AND qf_min IS NOT NULL AND qf_max IS NOT NULL
    ;""" % conditionsActivites
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictTranchesTarifs = {"pasqf" : 0, "autre" : 0}
    for IDligne, qf_min, qf_max in listeDonnees : 
        tranche = (qf_min, qf_max)
        if dictTranchesTarifs.has_key(tranche) == False :
            dictTranchesTarifs[tranche] = 0
    
    # Création des tranches de 100
    dictTranchesDefaut = {"pasqf" : 0, "autre" : 0}
    for x in range(0, 3000, 100) :
        tranche = (x+1, x+100)
        if x == 0 : tranche = (0, 100)
        dictTranchesDefaut[tranche] = 0    
    dictTranchesDefaut[(3001, 99999)] = 0
    
    # Répartition des QF par tranche
    for IDfamille, quotient in dictQuotients.iteritems() :
        for dictTranches in (dictTranchesDefaut, dictTranchesTarifs) :
            if quotient == None :
                dictTranches["pasqf"] += 1
            else :
                found = False
                for tranche in dictTranches.keys() :
                    if tranche not in ("pasqf", "autre") and quotient >= tranche[0] and quotient <= tranche[1] :
                        dictTranches[tranche] += 1
                        found = True
                if found == False :
                    dictTranches["autre"] += 1

    # Mémorisation des résultats
    DICT_QUOTIENTS["dictParametres"] = dictParametres
    DICT_QUOTIENTS["dictResultats"] = {"dictTranchesTarifs" : dictTranchesTarifs, "dictTranchesDefaut" : dictTranchesDefaut}
    return DICT_QUOTIENTS["dictResultats"]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------


class Texte_nombre_familles(MODELES.Texte):
    def __init__(self):
        """ Recherche du nombre de familles dont les individus sont présents """
        MODELES.Texte.__init__(self)
        self.nom = _(u"Nombre de familles")
        self.code = "texte_nombre_familles"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        conditionsActivites = MODELES.GetConditionActivites(dictParametres)
        
        # Recherche du nombre d'individus présents
        if dictParametres["mode"] == "presents" :
            req = """SELECT COUNT(IDfamille)
            FROM consommations 
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
            WHERE date>='%s' AND date<='%s' 
            AND consommations.etat IN ('reservation', 'present')
            AND IDactivite IN %s
            GROUP BY comptes_payeurs.IDfamille
            ;""" % (date_debut, date_fin, conditionsActivites)
        else :
            req = """SELECT COUNT(comptes_payeurs.IDfamille)
            FROM inscriptions 
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = inscriptions.IDcompte_payeur
            WHERE inscriptions.statut='ok' AND IDactivite IN %s
            GROUP BY comptes_payeurs.IDfamille
            ;""" % conditionsActivites
        
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        if dictParametres["mode"] == "presents" :
            mot = _(u"présent")
        else:
            mot = _(u"inscrit")
            
        if len(listeDonnees) == 0 or listeDonnees[0][0] == 0 : 
            self.texte = _(u"Aucune famille dont les membres sont %ss.") % mot
        else:
            self.texte = _(u"%d familles dont les membres sont %ss.") % (len(listeDonnees), mot)




class Tableau_nombre_familles(MODELES.Tableau):
    """ Répartition du nombre de familles par activité """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition du nombre de familles par activité")
        self.code = "tableau_nombre_familles"
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
            req = """SELECT IDactivite, COUNT(IDfamille)
            FROM consommations 
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
            WHERE date>='%s' AND date<='%s' 
            AND consommations.etat IN ('reservation', 'present')
            AND IDactivite IN %s
            GROUP BY IDactivite, IDfamille
            ;""" % (date_debut, date_fin, conditionsActivites)
        else:
            req = """SELECT IDactivite, COUNT(comptes_payeurs.IDfamille)
            FROM inscriptions 
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = inscriptions.IDcompte_payeur
            WHERE inscriptions.statut='ok' AND IDactivite IN %s
            GROUP BY IDactivite, comptes_payeurs.IDfamille
            ;""" % conditionsActivites
            
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : 
            return
        
        dictActiTemp = {}
        for IDactivite, nbreConso in listeDonnees :
            if dictActiTemp.has_key(IDactivite) == False :
                dictActiTemp[IDactivite] = 0
            dictActiTemp[IDactivite] += 1
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Activité"), "250"), (_(u"Nombre de familles"), "150") ]
        self.lignes = []
        for IDactivite, listeFamilles in dictActiTemp.iteritems() :
            nomActivite = dictParametres["dictActivites"][IDactivite]
            self.lignes.append((nomActivite, listeFamilles))



class Graphe_nombre_familles(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Comparatif du nombre de familles")
        self.code = "graphe_nombre_familles"
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
        ax.set_ylabel("Nbre de familles", fontsize=8)
        
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Comparatif du nombre de familles"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.4, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure



class Tableau_repartition_caisses(MODELES.Tableau):
    """ Répartition des familles par caisse """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Répartition des familles par caisse")
        self.code = "tableau_repartition_caisses"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictCaisses = GetDictCaisses(DB, dictParametres)
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Caisse"), "250"), (_(u"Nombre de familles"), "150") ]
        self.lignes = []
        
        # Tri par nbre de familles
        listeCaisses = []
        for IDcaisse, valeurs in dictCaisses.iteritems() :
            nbreFamilles = valeurs["nbreFamilles"]
            nomCaisse = valeurs["nom"]
            listeCaisses.append((nbreFamilles, nomCaisse))
        listeCaisses.sort(reverse=True)
        
        for nbreFamilles, nomCaisse in listeCaisses :
            self.lignes.append((nomCaisse, nbreFamilles))



class Graphe_repartition_caisses(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Répartition par caisse")
        self.code = "graphe_repartition_caisses"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictCaisses = GetDictCaisses(DB, dictParametres)
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        # Tri par nbre de familles
        listeCaisses = []
        nbreTotalFamilles = 0
        for IDcaisse, valeurs in dictCaisses.iteritems() :
            nbreFamilles = valeurs["nbreFamilles"]
            nomCaisse = valeurs["nom"]
            listeCaisses.append((nbreFamilles, nomCaisse))
            nbreTotalFamilles += nbreFamilles
        listeCaisses.sort(reverse=True)
                
        index = 1
        for nbreFamilles, nomCaisse in listeCaisses :
            listeValeurs.append(nbreFamilles)
            listeLabels.append(nomCaisse)
            
            couleur = 1.0 * nbreFamilles / nbreTotalFamilles
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(_(u"Répartition par caisse"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure




class Tableau_nombre_membres(MODELES.Tableau):
    """ Répartition du nombre de membres présents ou inscrits sur l'activité """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Nombre de membres présents")
        self.code = "tableau_nombre_membres"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        # Recherche des paramètres
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        conditionsActivites = MODELES.GetConditionActivites(dictParametres)
        dictResultats = GetDictMembres(DB, dictParametres) 
        
        if dictParametres["mode"] == "presents" :
            self.nom = _(u"Nombre de membres présents")
        else:
            self.nom = _(u"Nombre de membres inscrits")

        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Nombre de membres"), "250"), (_(u"Nombre de familles"), "150") ]
        self.lignes = []
        for nbreMembres, nbreFamilles in dictResultats.iteritems() :
            self.lignes.append((nbreMembres, nbreFamilles))
        self.lignes.sort() 




class Graphe_nombre_membres(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Nombre de membres présents")
        self.code = "graphe_nombre_membres"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        # Recherche des paramètres
        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        conditionsActivites = MODELES.GetConditionActivites(dictParametres)
        dictResultats = GetDictMembres(DB, dictParametres) 
        
        if dictParametres["mode"] == "presents" :
            self.nom = _(u"Nombre de membres présents")
        else:
            self.nom = _(u"Nombre de membres inscrits")
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        listeResultats = []
        nbreTotalFamilles = 0
        for nbreMembres, nbreFamilles in dictResultats.iteritems() :
            listeResultats.append((nbreMembres, nbreFamilles))
            nbreTotalFamilles += nbreFamilles
        listeResultats.sort() 
            
        index = 1
        for nbreMembres, nbreFamilles in listeResultats :
            listeValeurs.append(nbreFamilles)
            if nbreMembres == 1 :
                label = _(u"1 membre")
            else:
                label = _(u"%d membres") % nbreMembres
            listeLabels.append(label)
            
            couleur = 1.0 * nbreFamilles / nbreTotalFamilles
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(self.nom, weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure


class Tableau_qf_tarifs(MODELES.Tableau):
    """ QF par tranches de tarifs """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Quotients familiaux par tranches de tarifs")
        self.code = "tableau_qf_tarifs"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictTranches = GetDictQuotients(DB, dictParametres)["dictTranchesTarifs"]
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Tranche QF"), "250"), (_(u"Nombre de familles"), "150") ]
        self.lignes = []
        
        # Tri des tranches par ordre croissant
        listeTranches = []
        listeTranches = dictTranches.keys()
        listeTranches.sort() 
        
        # Création du tableau des valeurs
        for tranche in listeTranches :
            if tranche == "autre" : 
                label = _(u"Autre")
                if dictTranches[tranche] == 0 : 
                    label = None
            elif tranche == "pasqf" :
                label = _(u"Sans QF")
            else :
                label = u"%d - %d" % tranche
            if label != None :
                self.lignes.append((label, dictTranches[tranche]))
            

class Graphe_qf_tarifs(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Quotients familiaux par tranches de tarifs")
        self.code = "graphe_qf_tarifs"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictTranches = GetDictQuotients(DB, dictParametres)["dictTranchesTarifs"]
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        # Tri des tranches par ordre croissant
        listeTranches = []
        listeTranches = dictTranches.keys()
        listeTranches.sort() 
        
        nbreTotal = 0
        for tranche in listeTranches :
            nbreTotal += dictTranches[tranche]
        
        # Création du tableau des valeurs
        index = 1
        if nbreTotal > 0 :
            for tranche in listeTranches :
                valeur = dictTranches[tranche]
                if tranche == "autre" : 
                    label = _(u"Autre")
                    if dictTranches[tranche] == 0 : 
                        label = None
                elif tranche == "pasqf" :
                    label = _(u"Sans QF")
                else :
                    label = u"%d - %d" % tranche
                if label != None :
                    # Mémorisation des valeurs
                    listeValeurs.append(valeur)
                    listeLabels.append(label)
                    # Couleur
                    couleur = 1.0 * valeur / nbreTotal
                    couleur = matplotlib.cm.hsv(index * 0.1)
                    listeCouleurs.append(couleur)
                    index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(self.nom, weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure


class Tableau_qf_defaut(MODELES.Tableau):
    """ QF par tranches de tarifs """
    def __init__(self):
        MODELES.Tableau.__init__(self)
        self.nom = _(u"Quotients familiaux par tranches de 100")
        self.code = "tableau_qf_defaut"
    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []
        
        dictTranches = GetDictQuotients(DB, dictParametres)["dictTranchesDefaut"]
        
        # Création du tableau
        self.largeur = "400"
        self.colonnes = [ (_(u"Tranche QF"), "250"), (_(u"Nombre de familles"), "150") ]
        self.lignes = []
        
        # Tri des tranches par ordre croissant
        listeTranches = []
        listeTranches = dictTranches.keys()
        listeTranches.sort() 
        
        # Création du tableau des valeurs
        for tranche in listeTranches :
            if tranche == "autre" : 
                label = _(u"Autre")
                if dictTranches[tranche] == 0 : 
                    label = None
            elif tranche == "pasqf" :
                label = _(u"Sans QF")
            else :
                label = u"%d - %d" % tranche
            if label != None :
                self.lignes.append((label, dictTranches[tranche]))
            

class Graphe_qf_defaut2(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Quotients familiaux par tranches de 100")
        self.code = "graphe_qf_defaut"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictTranches = GetDictQuotients(DB, dictParametres)["dictTranchesDefaut"]
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        # Tri des tranches par ordre croissant
        listeTranches = []
        listeTranches = dictTranches.keys()
        listeTranches.sort() 
        
        nbreTotal = 0
        for tranche in listeTranches :
            nbreTotal += dictTranches[tranche]
        
        # Création du tableau des valeurs
        index = 1
        for tranche in listeTranches :
            valeur = dictTranches[tranche]
            if tranche == "autre" : 
                label = _(u"Autre")
                if dictTranches[tranche] == 0 : 
                    label = None
            elif tranche == "pasqf" :
                label = _(u"Sans QF")
            else :
                label = u"%d - %d" % tranche
            if label != None and valeur != 0 :
                # Mémorisation des valeurs
                listeValeurs.append(valeur)
                listeLabels.append(label)
                # Couleur
                couleur = 1.0 * valeur / nbreTotal
                couleur = matplotlib.cm.hsv(index * 0.1)
                listeCouleurs.append(couleur)
                index += 1
        
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(self.nom, weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 
    
        return figure


class Graphe_qf_defaut(MODELES.Graphe):
    def __init__(self):
        MODELES.Graphe.__init__(self)
        self.nom = _(u"Quotients familiaux par tranches de 100")
        self.code = "graphe_qf_defaut"
        self.taille = (450, 280)
    def MAJ(self, figure=None, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        # Création du graph
        ax = figure.add_subplot(111)
        
        dictTranches = GetDictQuotients(DB, dictParametres)["dictTranchesDefaut"]

        listeValeurs = []
        listeLabels = []
        
        # Tri des tranches par ordre croissant
        listeTranches = []
        listeTranches = dictTranches.keys()
        listeTranches.sort() 
        
        # Création du tableau des valeurs
        index = 1
        for tranche in listeTranches :
            valeur = dictTranches[tranche]
            if tranche == "autre" : 
                label = None
            elif tranche == "pasqf" :
                label = None
            else :
                label = u"%d - %d" % tranche
            if label != None and valeur != 0 :
                #if index % 2 == 0 : label = ""
                # Mémorisation des valeurs
                listeValeurs.append(valeur)
                listeLabels.append(label)
                index += 1
                        
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        barres = ax.bar(ind, listeValeurs, width, color=MODELES.ConvertitCouleur2(MODELES.COULEUR_VERT_POMME))
        
        # Axe horizontal
        ax.set_xlabel(_(u"Tranches"), fontsize=8)
        ind = arange(len(listeLabels)) 
        ax.set_xticks(ind + width) 
        ax.set_xticklabels(listeLabels)
        labelsx = ax.get_xticklabels()
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=8, horizontalalignment='right')
        
        # Axe vertical
        ax.set_ylabel("Nbre de familles", fontsize=8)
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(self.nom, weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.28, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure










if __name__ == '__main__':
    """ TEST d'un objet """
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    annee = 2014
    dictParametres = {
        "mode" : "presents",
        "periode" : {"type":"annee", "annee":annee, "date_debut":datetime.date(annee, 1, 1), "date_fin":datetime.date(annee, 12, 31)}, 
        "listeActivites" : [1, 2, 3, 4, 5], 
        "dictActivites" : {1 : _(u"Centre de Loisirs"), 2 : _(u"Action 10-14 ans"), 3 : _(u"Camp 4-6 ans"), 4 : _(u"Camp 6-9 ans"), 5 : _(u"Camp 10-14 ans"), 6 : _(u"Art floral"), 7 : _(u"Yoga")}, 
        }
    frame_1 = MODELES.FrameTest(objet=Graphe_qf_defaut(), dictParametres=dictParametres)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    
##    listeActivites = (1,)
##    conditionsActivites = "(1)"
##
##
##    DB = GestionDB.DB() 
##
##
##    if True : #dictParametres["mode"] == "presents" :
##        date_debut = datetime.date(2014, 7, 7)
##        date_fin = datetime.date(2014, 7, 7)
##        req = """SELECT familles.IDfamille, IDquotient, date_debut, date_fin, quotient
##        FROM familles
##        LEFT JOIN quotients ON quotients.IDfamille = familles.IDfamille
##        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
##        LEFT JOIN consommations ON consommations.IDcompte_payeur = comptes_payeurs.IDcompte_payeur
##        WHERE date>='%s' AND date<='%s' 
##        AND etat IN ('reservation', 'present')
##        AND IDactivite IN %s
##        GROUP BY familles.IDfamille, IDquotient
##        ;""" % (date_debut, date_fin, conditionsActivites)
##    else:
##        date_debut = MODELES.GetDateExtremeActivites(DB, listeActivites=dictParametres["listeActivites"], typeDate="date_debut", mode="min")
##        date_fin = MODELES.GetDateExtremeActivites(DB, listeActivites=dictParametres["listeActivites"], typeDate="date_fin", mode="max")
##        req = """SELECT familles.IDfamille, IDquotient, date_debut, date_fin, quotient
##        FROM familles
##        LEFT JOIN quotients ON quotients.IDfamille = familles.IDfamille
##        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
##        LEFT JOIN inscriptions ON inscriptions.IDcompte_payeur = comptes_payeurs.IDcompte_payeur
##        WHERE IDactivite IN %s
##        GROUP BY familles.IDfamille, IDquotient
##        ;""" % conditionsActivites
##
##    DB.ExecuterReq(req)
##    listeDonnees = DB.ResultatReq()
##    dictQuotients = {}
##    for IDfamille, IDquotient, date_debut_qf, date_fin_qf, quotient in listeDonnees :
##        if IDquotient == None or (date_debut_qf <= str(date_fin) and date_fin_qf >= str(date_debut)) :
##            dictQuotients[IDfamille] = quotient
##        else :
##            dictQuotients[IDfamille] = None
##    
##    # Recherche des tranches de QF existantes
##    req = """SELECT IDligne, qf_min, qf_max
##    FROM tarifs_lignes
##    WHERE IDactivite IN %s
##    AND qf_min IS NOT NULL AND qf_max IS NOT NULL
##    ;""" % conditionsActivites
##    DB.ExecuterReq(req)
##    listeDonnees = DB.ResultatReq()
##    dictTranchesTarifs = {"pasqf" : 0, "autre" : 0}
##    for IDligne, qf_min, qf_max in listeDonnees : 
##        tranche = (qf_min, qf_max)
##        if dictTranchesTarifs.has_key(tranche) == False :
##            dictTranchesTarifs[tranche] = 0
##    
##    # Création des tranches de 100
##    dictTranchesDefaut = {"pasqf" : 0, "autre" : 0}
##    for x in range(0, 3000, 100) :
##        tranche = (x+1, x+100)
##        if x == 0 : tranche = (0, 100)
##        dictTranchesDefaut[tranche] = 0    
##    dictTranchesDefaut[(3001, 99999)] = 0
##    
##    # Répartition des QF par tranche
##    for IDfamille, quotient in dictQuotients.iteritems() :
##        if quotient == None :
##            dictTranchesTarifs["pasqf"] += 1
##        else :
##            found = False
##            for dictTranches in (dictTranchesDefaut, dictTranchesTarifs) :
##                for tranche in dictTranches.keys() :
##                    if tranche not in ("pasqf", "autre") and quotient >= tranche[0] and quotient <= tranche[1] :
##                        dictTranches[tranche] += 1
##                        found = True
##                if found == False :
##                    dictTranches["autre"] += 1
##    
##    print dictTranchesDefaut
##    print dictTranchesTarifs
##    DB.Close() 
    
    
    