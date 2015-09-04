#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import GestionDB
import datetime

import UTILS_Titulaires

try: import psyco; psyco.full() 
except: pass


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


def GetListeCotisationsManquantes(dateReference=None, listeActivites=None, presents=None, concernes=False):
    if dateReference == None : 
        dateReference = datetime.date.today()

    # Récupération des données
    dictItems = {}

    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

    # Conditions Présents
    if presents == None :
        conditionPresents = ""
        jonctionPresents = ""
    else:
        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s')" % (str(presents[0]), str(presents[1]))
        jonctionPresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"
    
    # Récupération des cotisations à fournir pour la famille ou l'individu
    DB = GestionDB.DB()
    req = """
    SELECT 
    inscriptions.IDfamille, cotisations_activites.IDactivite, cotisations_activites.IDtype_cotisation, types_cotisations.nom, types_cotisations.type, individus.prenom, individus.IDindividu
    FROM cotisations_activites 
    LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations_activites.IDtype_cotisation
    LEFT JOIN inscriptions ON inscriptions.IDactivite = cotisations_activites.IDactivite
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    %s
    WHERE inscriptions.parti=0 %s %s
    GROUP BY inscriptions.IDfamille, cotisations_activites.IDtype_cotisation, individus.IDindividu;
    """ % (jonctionPresents, conditionActivites, conditionPresents)
    DB.ExecuterReq(req)
    listeCotisationsObligatoires = DB.ResultatReq()
    
    dictCotisationObligatoires = {}
    for IDfamille, IDactivite, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsObligatoires :
        if dictCotisationObligatoires.has_key(IDfamille) == False :
            dictCotisationObligatoires[IDfamille] = {}
        if dictCotisationObligatoires[IDfamille].has_key(IDactivite) == False :
            dictCotisationObligatoires[IDfamille][IDactivite] = []
        dictCotisationObligatoires[IDfamille][IDactivite].append((IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu))
    
    # Recherche des cotisations déjà fournies
    req = """
    SELECT IDcotisation, cotisations.IDtype_cotisation, IDindividu, IDfamille, date_debut, date_fin, type
    FROM cotisations 
    LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
    WHERE date_debut <= '%s' AND date_fin >= '%s'
    ORDER BY date_fin
    """ % (str(dateReference), str(dateReference))
    DB.ExecuterReq(req)
    listeCotisationsFournies = DB.ResultatReq()
    DB.Close()
    dictCotisationsFournies = {}
    for IDcotisation, IDtype_cotisation, IDindividu, IDfamille, date_debut, date_fin, typeCotisation in listeCotisationsFournies :
        # Pour les cotisations familiales :
        if typeCotisation == "famille" : IDindividu = None
        
        date_debut = DateEngEnDateDD(date_debut)
        date_fin = DateEngEnDateDD(date_fin)
        dictCotisationsFournies[ (IDfamille, IDtype_cotisation, IDindividu) ] = (date_debut, date_fin)
    
    # Comparaison de la liste des cotisations à fournir et la liste des cotisations fournies
    dictDonnees = {}
    for IDfamille, dictCotisationsFamille in dictCotisationObligatoires.iteritems() :
        for IDactivite, listeCotisationsActivite in dictCotisationsFamille.iteritems() :
            activiteValide = False
            
            listeTemp = []
            for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsActivite :
                
##                # Pour les cotisations familiales :
##                if typeCotisation == "famille" : 
##                    IDindividu = None
##                else:
##                    # Pour les cotisations qui sont indépendantes de la famille
##                    IDfamilleTemp = None
                
                # Préparation du label
                if typeCotisation == "famille" or IDindividu == None :
                    label = nomCotisation
                else:
                    label = _(u"%s de %s") % (nomCotisation, prenom)
                
                if dictCotisationsFournies.has_key((None, IDtype_cotisation, IDindividu)) or dictCotisationsFournies.has_key((IDfamille, IDtype_cotisation, None)) :
                    if dictCotisationsFournies.has_key((None, IDtype_cotisation, IDindividu)) :
                        date_debut, date_fin = dictCotisationsFournies[(None, IDtype_cotisation, IDindividu)]
                    if dictCotisationsFournies.has_key((IDfamille, IDtype_cotisation, None)) :
                        date_debut, date_fin = dictCotisationsFournies[(IDfamille, IDtype_cotisation, None)]
                    nbreJoursRestants = (date_fin - datetime.date.today()).days
                    if nbreJoursRestants > 15 :
                        valide = "ok"
                    else:
                        valide = "attention"
                else:
                    valide = "pasok"
                
                if valide == "ok" :
                    activiteValide = True
                    
                listeTemp.append((IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label))
                
            # Mémorisation
            for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label in listeTemp :
                if activiteValide == True :
                    valide = "ok"
                dictDonnees[(IDfamille, IDtype_cotisation, IDindividu)] = (IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label)
                
##                if IDfamille == 57 or IDindividu == 107 :
##                    print (IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label)
                    
    # Comparaison de la liste des cotisations à fournir et la liste des cotisations fournies
##    dictDonnees = {}
##    for IDfamille, IDactivite, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, nbreConso in listeCotisationsObligatoires :
##        
##        # Pour les cotisations familiales :
##        if typeCotisation == "famille" : 
##            IDindividu = None
##        else:
##            # Pour les cotisations qui sont indépendantes de la famille
##            IDfamille = None
##        
##        # Préparation du label
##        if typeCotisation == "famille" or IDindividu == None :
##            label = nomCotisation
##        else:
##            label = _(u"%s de %s") % (nomCotisation, prenom)
##
##        if dictCotisationsFournies.has_key( (IDfamille, IDtype_cotisation, IDindividu) ) :
##            date_debut, date_fin = dictCotisationsFournies[(IDfamille, IDtype_cotisation, IDindividu)]
##            nbreJoursRestants = (date_fin - datetime.date.today()).days
##            if nbreJoursRestants > 15 :
##                valide = "ok"
##            else:
##                valide = "attention"
##        else:
##            valide = "pasok"
##            
##        dictDonnees[(IDfamille, IDtype_cotisation, IDindividu)] = (IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide, label)
    
    # Répartition par famille
    dictCotisations = {}
    nbreFamilles = 0
    nbreCotisations = len(dictDonnees)
    for key, valeurs in dictDonnees.iteritems() :
        IDfamille = valeurs[0]
        if dictCotisations.has_key(IDfamille) == False :
            dictCotisations[IDfamille] = []
            if IDfamille != None : 
                nbreFamilles += 1
        dictCotisations[IDfamille].append(valeurs)
        dictCotisations[IDfamille].sort()
    
    # Formatage des données
    dictFinal = {}
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, dictTemp in dictCotisations.iteritems() :
##        print IDfamille
##        for cotisation in dictTemp :
##            print "  >", cotisation
        if IDfamille != None and titulaires.has_key(IDfamille) :
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
        else :
            nomTitulaires = _(u"Aucun titulaire")
        listeCotisations = []
        for cotisation in dictTemp :
            labelCotisation = cotisation[7]
            if cotisation[6] != "ok" and labelCotisation not in listeCotisations :
                listeCotisations.append(labelCotisation)
        texteCotisations = ", ".join(listeCotisations)
        
        if concernes == False or (concernes == True and len(listeCotisations) > 0) :
            dictFinal[IDfamille] = {"titulaires" : nomTitulaires, "cotisations" : texteCotisations, "nbre" : len(listeCotisations)}
    
    return dictFinal
    
    
    
            
            
if __name__ == '__main__':
    print GetListeCotisationsManquantes(dateReference=datetime.date(2012, 11, 16), listeActivites=None, presents=None, concernes=False)