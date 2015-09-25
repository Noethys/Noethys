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

import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()


def GetTitulaires(listeIDfamille=[]):
    """ si listeIDfamille == [] alors renvoie toutes les familles """
    dictFamilles = {}
    
    # Condition
    if len(listeIDfamille) == 0 : conditionFamilles = ""
    elif len(listeIDfamille) == 1 : conditionFamilles = "WHERE IDfamille=%d" % listeIDfamille[0]
    else : conditionFamilles = "WHERE IDfamille IN %s" % str(tuple(listeIDfamille))
    
    DB = GestionDB.DB()

    # Récupération de toutes les familles de la base
    req = """
    SELECT IDfamille, IDcompte_payeur
    FROM familles
    %s;""" % conditionFamilles
    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()  
    for IDfamille, IDcompte_payeur in listeFamilles :
        dictFamilles[IDfamille] = {"IDcompte_payeur":IDcompte_payeur,}
    
    # Récupération de tous les individus de la base
    req = """
    SELECT IDindividu, IDcivilite, individus.nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, mail, individus.IDsecteur, secteurs.nom
    FROM individus
    LEFT JOIN secteurs ON secteurs.IDsecteur = individus.IDsecteur
    ;""" 
    DB.ExecuterReq(req)
    listeIndividus = DB.ResultatReq()  
    dictIndividus = {}
    for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, mail, IDsecteur, nomSecteur in listeIndividus :
        dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "adresse_auto":adresse_auto, "rue_resid":rue_resid, "cp_resid":cp_resid, "ville_resid":ville_resid, "mail":mail, "IDsecteur":IDsecteur, "nomSecteur":nomSecteur}
    
    # Récupération des rattachements
    req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
    FROM rattachements
    %s;""" % conditionFamilles
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    dictRattachements = {}
    for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in listeDonnees :
        if dictRattachements.has_key(IDfamille) == False :
            dictRattachements[IDfamille] = [(IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire),]
        else:
            dictRattachements[IDfamille].append((IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire))
    
    # Recherche des noms des titulaires
    for IDfamille, dictFamille in dictFamilles.iteritems() :
        if dictRattachements.has_key(IDfamille):
            listeIndividusFamilles = dictRattachements[IDfamille]
            listeTitulaires = []
            nbreTitulaires = 0
            for IDrattachement, IDindividuTmp, IDfamilleTmp, IDcategorie, titulaire in listeIndividusFamilles :
                if dictIndividus.has_key(IDindividuTmp) :
                    if titulaire == 1 :
                        nom = dictIndividus[IDindividuTmp]["nom"]
                        prenom = dictIndividus[IDindividuTmp]["prenom"]
                        if prenom == None : prenom = u""
                        IDcivilite = dictIndividus[IDindividuTmp]["IDcivilite"]
                        if IDcivilite != None and DICT_CIVILITES[IDcivilite]["civiliteAbrege"] != None :
                            nomCivilite = u"%s " % DICT_CIVILITES[IDcivilite]["civiliteAbrege"]
                        else:
                            nomCivilite = u""
                        mail = dictIndividus[IDindividuTmp]["mail"]
                        dictTemp = {
                        "IDindividu":IDindividuTmp, "IDcivilite":IDcivilite,"nom":nom, "prenom":prenom, "mail":mail,
                        "nomSansCivilite": u"%s %s" % (nom, prenom),
                        "nomAvecCivilite": u"%s%s %s" % (nomCivilite, nom, prenom),
                        }
                        listeTitulaires.append(dictTemp)
                        nbreTitulaires += 1
                    
            if nbreTitulaires == 1 : 
                nomsTitulaires = {
                    "sansCivilite" : listeTitulaires[0]["nomSansCivilite"],
                    "avecCivilite" : listeTitulaires[0]["nomAvecCivilite"],
                    }
            if nbreTitulaires == 2 : 
                if listeTitulaires[0]["nom"] == listeTitulaires[1]["nom"] :
                    nomsTitulaires = {
                        "sansCivilite" : _(u"%s %s et %s") % (listeTitulaires[0]["nom"], listeTitulaires[0]["prenom"], listeTitulaires[1]["prenom"]),
                        "avecCivilite" : _(u"%s %s et %s") % (listeTitulaires[0]["nom"], listeTitulaires[0]["prenom"], listeTitulaires[1]["prenom"]),
                        }
                else:
                    nomsTitulaires = {
                    "sansCivilite" : _(u"%s et %s") % (listeTitulaires[0]["nomSansCivilite"], listeTitulaires[1]["nomSansCivilite"]),
                    "avecCivilite" : _(u"%s et %s") % (listeTitulaires[0]["nomAvecCivilite"], listeTitulaires[1]["nomAvecCivilite"]),
                    }
            if nbreTitulaires > 2 :
                nomsSansCivilite = u""
                nomsAvecCivilite = u""
                for dictTemp in listeTitulaires[:-2] :
                    nomsAvecCivilite += u"%s, " % dictTemp["nomAvecCivilite"]
                    nomsSansCivilite += u"%s, " % dictTemp["nomSansCivilite"]
                nomsAvecCivilite += _(u"%s et %s") % (listeTitulaires[-2]["nomAvecCivilite"], listeTitulaires[-1]["nomAvecCivilite"])
                nomsSansCivilite += _(u"%s et %s") % (listeTitulaires[-2]["nomSansCivilite"], listeTitulaires[-1]["nomSansCivilite"])
                nomsTitulaires = {
                    "sansCivilite" : nomsSansCivilite,
                    "avecCivilite" : nomsAvecCivilite,
                    }
            
            # Recherche de l'adresse de la famille
            IDindividuTitulaire = listeTitulaires[0]["IDindividu"]
            adresse_auto = dictIndividus[IDindividuTitulaire]["adresse_auto"]
            if adresse_auto != None and dictIndividus.has_key(adresse_auto) :
                rue_resid = dictIndividus[adresse_auto]["rue_resid"]
                cp_resid = dictIndividus[adresse_auto]["cp_resid"]
                ville_resid = dictIndividus[adresse_auto]["ville_resid"]
                IDsecteur = dictIndividus[adresse_auto]["IDsecteur"]
                nomSecteur = dictIndividus[adresse_auto]["nomSecteur"]
            else:
                rue_resid = dictIndividus[IDindividuTitulaire]["rue_resid"]
                cp_resid = dictIndividus[IDindividuTitulaire]["cp_resid"]
                ville_resid = dictIndividus[IDindividuTitulaire]["ville_resid"]
                IDsecteur = dictIndividus[IDindividuTitulaire]["IDsecteur"]
                nomSecteur = dictIndividus[IDindividuTitulaire]["nomSecteur"]
            dictAdresse = {"rue":rue_resid, "cp":cp_resid, "ville":ville_resid, "IDsecteur":IDsecteur, "nomSecteur":nomSecteur, "secteur":nomSecteur}
            
            # Recherche des adresses Emails des titulaires
            listeMails = []
            for dictTemp in listeTitulaires :
                if dictTemp["mail"] not in (None, ""):
                    listeMails.append(dictTemp["mail"])
            
            # Définit les noms des titulaires
            dictFamilles[IDfamille]["titulairesAvecCivilite"] = nomsTitulaires["avecCivilite"]
            dictFamilles[IDfamille]["titulairesSansCivilite"] = nomsTitulaires["sansCivilite"]
            dictFamilles[IDfamille]["listeTitulaires"] = listeTitulaires
            dictFamilles[IDfamille]["adresse"] = dictAdresse
            dictFamilles[IDfamille]["listeMails"] = listeMails
        
        else:
            # Définit les noms des titulaires
            dictFamilles[IDfamille]["titulairesAvecCivilite"] = _(u"Sans titulaires")
            dictFamilles[IDfamille]["titulairesSansCivilite"] = _(u"Sans titulaires")
            dictFamilles[IDfamille]["listeTitulaires"] = []
            dictFamilles[IDfamille]["adresse"] = {"rue":"", "cp":"", "ville":"", "IDsecteur":None, "nomSecteur":"", "secteur":""}
            dictFamilles[IDfamille]["listeMails"] = []
    
    return dictFamilles


def GetIndividus():
    """ Importe tous les individus et recherche leurs noms et adresses """
    DB = GestionDB.DB()
    req = """
    SELECT IDindividu, IDcivilite, individus.nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, mail, individus.IDsecteur, secteurs.nom
    FROM individus
    LEFT JOIN secteurs ON secteurs.IDsecteur = individus.IDsecteur
    ;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()  
    DB.Close()
    dictTemp = {}
    for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, mail, IDsecteur, nomSecteur in listeDonnees :
        if nomSecteur == None : nomSecteur = ""
        dictTemp[IDindividu] = {
            "IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, 
            "adresse_auto":adresse_auto, "rue":rue_resid, "cp":cp_resid, "ville":ville_resid, "mail":mail,
            "IDsecteur":IDsecteur, "nomSecteur":nomSecteur, "secteur":nomSecteur}
    
    # Recherche les noms et adresses de chaque individu
    dictIndividus = {}
    for IDindividu, dictIndividu in dictTemp.iteritems() :
        
        # Civilité
        IDcivilite = dictIndividu["IDcivilite"]
        if IDcivilite == None :
            IDcivilite = 1
        dictIndividu["civiliteAbrege"] = DICT_CIVILITES[IDcivilite]["civiliteAbrege"] 
        dictIndividu["civiliteLong"] = DICT_CIVILITES[IDcivilite]["civiliteLong"] 
        dictIndividu["sexe"] = DICT_CIVILITES[IDcivilite]["sexe"] 
        
        # Nom complet
        if dictIndividu["prenom"] != None :
            dictIndividu["nom_complet"] = u"%s %s" % (dictIndividu["nom"], dictIndividu["prenom"])
        else :
            dictIndividu["nom_complet"] = dictIndividu["nom"]
            
        # Adresse 
        adresse_auto = dictIndividu["adresse_auto"]
        if adresse_auto != None and dictTemp.has_key(adresse_auto) :
            dictIndividu["rue"] = dictTemp[adresse_auto]["rue"]
            dictIndividu["cp"] = dictTemp[adresse_auto]["cp"]
            dictIndividu["ville"] = dictTemp[adresse_auto]["ville"]
            dictIndividu["IDsecteur"] = dictTemp[adresse_auto]["IDsecteur"]
            dictIndividu["nomSecteur"] = dictTemp[adresse_auto]["nomSecteur"]
            dictIndividu["secteur"] = dictTemp[adresse_auto]["nomSecteur"]
            
        dictIndividus[IDindividu] = dictIndividu
    
    return dictIndividus
            
    
    
    
            
if __name__ == '__main__':
    print GetTitulaires()[10]
    print GetIndividus() 