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
from Utils.UTILS_Traduction import _
import GestionDB
import datetime

from Utils import UTILS_Titulaires


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
        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s' AND consommations.etat IN ('reservation', 'present'))" % (str(presents[0]), str(presents[1]))
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
    LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
    %s
    WHERE inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') %s %s AND activites.date_fin>='%s'
    GROUP BY inscriptions.IDfamille, cotisations_activites.IDtype_cotisation, individus.IDindividu;
    """ % (jonctionPresents, dateReference, conditionActivites, conditionPresents, dateReference)
    DB.ExecuterReq(req)
    listeCotisationsObligatoires = DB.ResultatReq()
    
    dictCotisationObligatoires = {}
    for IDfamille, IDactivite, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsObligatoires :
        if (IDfamille in dictCotisationObligatoires) == False :
            dictCotisationObligatoires[IDfamille] = {}
        if (IDactivite in dictCotisationObligatoires[IDfamille]) == False :
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
    for IDfamille, dictCotisationsFamille in dictCotisationObligatoires.items() :
        for IDactivite, listeCotisationsActivite in dictCotisationsFamille.items() :
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
                
                if (None, IDtype_cotisation, IDindividu) in dictCotisationsFournies or (IDfamille, IDtype_cotisation, None) in dictCotisationsFournies :
                    if (None, IDtype_cotisation, IDindividu) in dictCotisationsFournies :
                        date_debut, date_fin = dictCotisationsFournies[(None, IDtype_cotisation, IDindividu)]
                    if (IDfamille, IDtype_cotisation, None) in dictCotisationsFournies :
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
    for key, valeurs in dictDonnees.items() :
        IDfamille = valeurs[0]
        if (IDfamille in dictCotisations) == False :
            dictCotisations[IDfamille] = []
            if IDfamille != None : 
                nbreFamilles += 1
        dictCotisations[IDfamille].append(valeurs)
        dictCotisations[IDfamille].sort()
    
    # Formatage des données
    dictFinal = {}
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, dictTemp in dictCotisations.items() :
##        print IDfamille
##        for cotisation in dictTemp :
##            print "  >", cotisation
        if IDfamille != None and IDfamille in titulaires :
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
        else :
            nomTitulaires = _(u"Aucun titulaire")
        listeCotisations = []
        listeDetailCotisations = []
        for cotisation in dictTemp :
            labelCotisation = cotisation[7]
            if cotisation[6] != "ok" and labelCotisation not in listeCotisations :
                listeCotisations.append(labelCotisation)
        listeDetailCotisations.append(cotisation)
        texteCotisations = ", ".join(listeCotisations)
        
        if concernes == False or (concernes == True and len(listeCotisations) > 0) :
            dictFinal[IDfamille] = {"titulaires" : nomTitulaires, "cotisations" : texteCotisations, "nbre" : len(listeCotisations), "liste" : listeDetailCotisations}
    
    return dictFinal
    
    
    
            
            
if __name__ == '__main__':
    print(GetListeCotisationsManquantes(dateReference=datetime.date(2012, 11, 16), listeActivites=None, presents=None, concernes=False))