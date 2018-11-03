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
import GestionDB

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()


def GetTitulaires(listeIDfamille=[], mode_adresse_facturation=False, inclure_telephones=False):
    """ si listeIDfamille == [] alors renvoie toutes les familles """
    dictFamilles = {}
    
    # Condition
    if len(listeIDfamille) == 0 : conditionFamilles = ""
    elif len(listeIDfamille) == 1 :
        if listeIDfamille[0] != None :
            conditionFamilles = "WHERE IDfamille=%d" % listeIDfamille[0]
        else :
            conditionFamilles = "WHERE IDfamille=0"
    else : conditionFamilles = "WHERE IDfamille IN %s" % str(tuple(listeIDfamille))
    
    DB = GestionDB.DB()

    # Récupération de toutes les familles de la base
    req = """
    SELECT IDfamille, IDcompte_payeur, autre_adresse_facturation
    FROM familles
    %s;""" % conditionFamilles
    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()  
    for IDfamille, IDcompte_payeur, autre_adresse_facturation in listeFamilles :
        dictFamilles[IDfamille] = {"IDcompte_payeur":IDcompte_payeur, "autre_adresse_facturation":autre_adresse_facturation}

    if inclure_telephones == True :
        champs_telephones = ", travail_tel, travail_tel_sms, tel_domicile, tel_domicile_sms, tel_mobile, tel_mobile_sms"
    else :
        champs_telephones = ""

    # Récupération de tous les individus de la base
    req = """
    SELECT IDindividu, IDcivilite, individus.nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, mail, individus.IDsecteur, secteurs.nom %s
    FROM individus
    LEFT JOIN secteurs ON secteurs.IDsecteur = individus.IDsecteur
    ;""" % champs_telephones
    DB.ExecuterReq(req)
    listeIndividus = DB.ResultatReq()  
    dictIndividus = {}
    for valeurs in listeIndividus :
        dictIndividus[valeurs[0]] = {"IDcivilite":valeurs[1], "nom":valeurs[2], "prenom":valeurs[3], "date_naiss":valeurs[4], "adresse_auto":valeurs[5], "rue_resid":valeurs[6], "cp_resid":valeurs[7], "ville_resid":valeurs[8], "mail":valeurs[9], "IDsecteur":valeurs[10], "nomSecteur":valeurs[11]}

        if inclure_telephones == True :
            dictIndividus[valeurs[0]]["telephones"] = {
                "travail_tel" : valeurs[12],
                "travail_tel_sms" : bool(valeurs[13]),
                "tel_domicile" : valeurs[14],
                "tel_domicile_sms" : bool(valeurs[15]),
                "tel_mobile" : valeurs[16],
                "tel_mobile_sms" : bool(valeurs[17]),
                }

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
        nbreTitulaires = 0

        if dictRattachements.has_key(IDfamille):
            listeIndividusFamilles = dictRattachements[IDfamille]
            listeTitulaires = []
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
                        if inclure_telephones == True:
                            dictTemp["telephones"] = dictIndividus[IDindividuTmp]["telephones"]
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

            if nbreTitulaires > 0:
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

                # Noms des titulaires
                titulairesAvecCivilite = nomsTitulaires["avecCivilite"]
                titulairesSansCivilite = nomsTitulaires["sansCivilite"]

                # Autre adresse de facturation
                autre_adresse_facturation = dictFamille["autre_adresse_facturation"]
                if mode_adresse_facturation == True and autre_adresse_facturation not in (None, ""):
                    valeurs_autre_adresse = autre_adresse_facturation.split("##")
                    titulairesAvecCivilite = valeurs_autre_adresse[0]
                    titulairesSansCivilite = valeurs_autre_adresse[0]
                    dictAdresse = {"rue": valeurs_autre_adresse[1], "cp": valeurs_autre_adresse[2], "ville": valeurs_autre_adresse[3], "IDsecteur": None, "nomSecteur": "", "secteur": ""}

                # Définit les noms des titulaires
                dictFamilles[IDfamille]["titulairesAvecCivilite"] = titulairesAvecCivilite
                dictFamilles[IDfamille]["titulairesSansCivilite"] = titulairesSansCivilite
                dictFamilles[IDfamille]["listeTitulaires"] = listeTitulaires
                dictFamilles[IDfamille]["adresse"] = dictAdresse
                dictFamilles[IDfamille]["listeMails"] = listeMails

        if nbreTitulaires== 0:
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
            
    
def GetFamillesRattachees(IDindividu=None):
    # Recherche des familles rattachées
    db = GestionDB.DB()
    req = """SELECT IDrattachement, rattachements.IDfamille, IDcategorie, titulaire, IDcompte_payeur
    FROM rattachements
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = rattachements.IDfamille
    WHERE rattachements.IDindividu=%d
    ORDER BY IDcategorie;""" % IDindividu
    db.ExecuterReq(req)
    listeRattachements = db.ResultatReq()
    dictFamilles = {}
    for IDrattachement, IDfamille, IDcategorie, titulaire, IDcompte_payeur in listeRattachements :
        if IDcategorie == 1 : nomCategorie = _(u"représentant")
        if IDcategorie == 2 : nomCategorie = _(u"enfant")
        if IDcategorie == 3 : nomCategorie = _(u"contact")
        dictFamilles[IDfamille] = {"nomsTitulaires" : u"", "listeNomsTitulaires" : [], "IDcategorie" : IDcategorie, "nomCategorie" : nomCategorie, "IDcompte_payeur" : IDcompte_payeur }
    # Recherche des noms des titulaires
    if len(dictFamilles) == 0 : condition = "()"
    if len(dictFamilles) == 1 : condition = "(%d)" % dictFamilles.keys()[0]
    else : condition = str(tuple(dictFamilles))
    req = """SELECT IDrattachement, individus.IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom
    FROM rattachements
    LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
    WHERE IDfamille IN %s AND titulaire=1;""" % condition
    db.ExecuterReq(req)
    listeTitulaires = db.ResultatReq()
    db.Close()
    for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom in listeTitulaires :
        nomIndividu = u"%s %s" % (nom, prenom)
        dictFamilles[IDfamille]["listeNomsTitulaires"].append(nomIndividu)
        nbreTitulaires = len(dictFamilles[IDfamille]["listeNomsTitulaires"])
        if nbreTitulaires == 1 :
            dictFamilles[IDfamille]["nomsTitulaires"] = nomIndividu
        if nbreTitulaires == 2 :
            dictFamilles[IDfamille]["nomsTitulaires"] = _(u"%s et %s") % (dictFamilles[IDfamille]["listeNomsTitulaires"][0], dictFamilles[IDfamille]["listeNomsTitulaires"][1])
        if nbreTitulaires > 2 :
            texteNoms = ""
            for nomTitulaire in dictFamilles[IDfamille]["listeNomsTitulaires"][:-1] :
                texteNoms += u"%s, " % nomTitulaire
            texteNoms = _(u"%s et %s") % (dictFamilles[IDfamille]["listeNomsTitulaires"][-2], dictFamilles[IDfamille]["listeNomsTitulaires"][-1])
            dictFamilles[IDfamille]["nomsTitulaires"] = texteNoms
    return dictFamilles


def GetCoordsIndividu(IDindividu=None):
    if IDindividu == None :
        return None

    DB = GestionDB.DB()
    req = """SELECT adresse_auto, rue_resid, cp_resid, ville_resid,
    travail_tel, travail_fax, travail_mail, tel_domicile, tel_mobile, tel_fax, mail
    FROM individus WHERE IDindividu=%d;""" % IDindividu
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 :
        DB.Close()
        return None

    adresse_auto, rue_resid, cp_resid, ville_resid, travail_tel, travail_fax, travail_mail, tel_domicile, tel_mobile, tel_fax, mail = listeDonnees[0]

    # Recherche d'une adresse associée
    if adresse_auto != None :
        req = """SELECT rue_resid, cp_resid, ville_resid
        FROM individus WHERE IDindividu=%d;""" % adresse_auto
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            rue_resid, cp_resid, ville_resid = listeDonnees[0]

    DB.Close()

    # Renvoi des résultats
    dict_coords = {
        "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid,
        "travail_tel" : travail_tel, "travail_fax" : travail_fax, "travail_mail" : travail_mail,
        "tel_domicile" : tel_domicile, "tel_mobile" : tel_mobile, "tel_fax" : tel_fax, "mail" : mail,
        }

    return dict_coords



if __name__ == '__main__':
    print GetCoordsIndividu(IDindividu=100)