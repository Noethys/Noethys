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


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


def GetListePiecesManquantes(dateReference=None, listeActivites=None, presents=None, concernes=False):
    if dateReference == None : 
        dateReference = datetime.date.today()

    # Récupération des données
    dictItems = {}
    
    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND consommations.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND consommations.IDactivite IN %s" % str(tuple(listeActivites))
            
    # Conditions Présents
##    if presents == None :
##        conditionPresents = ""
##        jonctionPresents = ""
##    else:
##        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s')" % (str(presents[0]), str(presents[1]))
##        jonctionPresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"
    
    DB = GestionDB.DB()
    
    # Récupération des pièces à fournir

## # Ancienne Version moins rapide :
##    req = """
##    SELECT 
##    inscriptions.IDfamille, pieces_activites.IDtype_piece, types_pieces.nom, types_pieces.public, types_pieces.valide_rattachement, individus.prenom, individus.IDindividu
##    FROM pieces_activites 
##    LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces_activites.IDtype_piece
##    LEFT JOIN inscriptions ON inscriptions.IDactivite = pieces_activites.IDactivite
##    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
##    %s
##    WHERE inscriptions.parti=0 %s %s
##    GROUP BY inscriptions.IDfamille, pieces_activites.IDtype_piece, individus.IDindividu
##    ;""" % (jonctionPresents, conditionActivites, conditionPresents)
##    DB.ExecuterReq(req)
##    listePiecesObligatoires = DB.ResultatReq()

    # Récupération des individus présents
    listePresents = []
    if presents != None :
        req = """
        SELECT IDindividu, IDinscription
        FROM consommations
        WHERE date>='%s' AND date<='%s' %s
        GROUP BY IDindividu
        ;"""  % (str(presents[0]), str(presents[1]), conditionActivites)
        DB.ExecuterReq(req)
        listeIndividusPresents = DB.ResultatReq()
        for IDindividu, IDinscription in listeIndividusPresents :
            listePresents.append(IDindividu)


    req = """
    SELECT 
    inscriptions.IDfamille, pieces_activites.IDtype_piece, types_pieces.nom, types_pieces.public, types_pieces.valide_rattachement, individus.prenom, individus.IDindividu
    FROM pieces_activites 
    LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces_activites.IDtype_piece
    LEFT JOIN inscriptions ON inscriptions.IDactivite = pieces_activites.IDactivite
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    WHERE inscriptions.parti=0 %s
    GROUP BY inscriptions.IDfamille, pieces_activites.IDtype_piece, individus.IDindividu
    ;""" % conditionActivites.replace("consommations", "inscriptions")
    DB.ExecuterReq(req)
    listePiecesObligatoires = DB.ResultatReq()


    # Recherche des pièces déjà fournies
    req = """
    SELECT IDpiece, pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
    FROM pieces 
    LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
    WHERE date_debut <= '%s' AND date_fin >= '%s'
    ORDER BY date_fin
    """ % (str(dateReference), str(dateReference))
    DB.ExecuterReq(req)
    listePiecesFournies = DB.ResultatReq()
    DB.Close()
    dictPiecesFournies = {}
    for IDpiece, IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, publicPiece in listePiecesFournies :
        # Pour les pièces familiales :
        if publicPiece == "famille" : IDindividu = None
        
        date_debut = DateEngEnDateDD(date_debut)
        date_fin = DateEngEnDateDD(date_fin)
        dictPiecesFournies[ (IDfamille, IDtype_piece, IDindividu) ] = (date_debut, date_fin)
    
    # Comparaison de la liste des pièces à fournir et la liste des pièces fournies
    dictDonnees = {}
    for IDfamille, IDtype_piece, nomPiece, publicPiece, rattachementPiece, prenom, IDindividu in listePiecesObligatoires :
        
        if presents == None or (presents != None and IDindividu in listePresents) :
            
            # Pour les pièces familiales :
            if publicPiece == "famille" : IDindividu = None
            # Pour les pièces qui sont indépendantes de la famille
            if rattachementPiece == 1 :
                IDfamilleTemp = None
            else:
                IDfamilleTemp = IDfamille
                
            # Préparation du label
            if publicPiece == "famille" or IDindividu == None :
                label = nomPiece
            else:
                label = _(u"%s de %s") % (nomPiece, prenom)
                        
            if dictPiecesFournies.has_key( (IDfamilleTemp, IDtype_piece, IDindividu) ) :
                date_debut, date_fin = dictPiecesFournies[(IDfamilleTemp, IDtype_piece, IDindividu)]
                nbreJoursRestants = (date_fin - datetime.date.today()).days
                if nbreJoursRestants > 15 :
                    valide = "ok"
                else:
                    valide = "attention"
            else:
                valide = "pasok"
                
            dictDonnees[(IDfamille, IDtype_piece, IDindividu)] = (IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide, label)
        
    # Répartition par famille
    dictPieces = {}
    nbreFamilles = 0
    for key, valeurs in dictDonnees.iteritems() :
        IDfamille = valeurs[0]
        if dictPieces.has_key(IDfamille) == False :
            dictPieces[IDfamille] = []
            if IDfamille != None : 
                nbreFamilles += 1
        dictPieces[IDfamille].append(valeurs)
        dictPieces[IDfamille].sort()
    
    # Formatage des données
    dictFinal = {}
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, dictTemp in dictPieces.iteritems() :
        if IDfamille != None and titulaires.has_key(IDfamille) :
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
        else :
            nomTitulaires = _(u"Aucun titulaire")
        listePieces = []
        for piece in dictTemp :
            if piece[6] != "ok" :
                listePieces.append(piece[7])
        textePieces = ", ".join(listePieces)
        
        if concernes == False or (concernes == True and len(listePieces) > 0) :
            dictFinal[IDfamille] = {"titulaires" : nomTitulaires, "pieces" : textePieces, "nbre" : len(listePieces) }
    
    return dictFinal
    
    
    
            
            
if __name__ == '__main__':
    print len(GetListePiecesManquantes(dateReference=datetime.date.today(), listeActivites=[1,], presents=(datetime.date(2015, 8, 13), datetime.date(2015, 8, 13)), concernes=True))