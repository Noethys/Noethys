#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import CTRL_Bouton_image
import GestionDB




def ParametresCategorie(mode="get", categorie="", dictParametres={}, nomFichier=""):
    """ Pour m�moriser ou r�cup�rer des param�tres dans la base de donn�es """
    """ Renseigner categorie et dictParametres obligatoirement !!!  (pour avoir les valeurs par d�faut et deviner les types de valeur) """
    """ dictParametres = {nom:valeur, nom:valeur, ....} """
    # Recherche du parametre
    DB = GestionDB.DB(nomFichier=nomFichier)
    
    # Si aucun fichier n'est charg�, on renvoie la valeur par d�faut :
    if DB.echec == 1 :
        return dictParametres
    
    req = u"""SELECT IDparametre, nom, parametre FROM parametres WHERE categorie="%s";""" % categorie
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictDonnees = {}
    for IDparametre, nom, parametre in listeDonnees :
        dictDonnees[nom] = parametre
    
    listeAjouts = []
    listeModifications = []
    dictFinal = {}
    
    # On boucle sur chaque valeur
    for nom, valeur in dictParametres.iteritems() :

        # Pr�paration de la valeur par d�faut
        type_parametre = type(valeur)
        if type_parametre == int : valeurTmp = str(valeur)
        elif type_parametre == float : valeurTmp = str(valeur)
        elif type_parametre == str : valeurTmp = valeur
        elif type_parametre == unicode : valeurTmp = valeur
        elif type_parametre == tuple : valeurTmp = str(valeur)
        elif type_parametre == list : valeurTmp = str(valeur)
        elif type_parametre == dict : valeurTmp = str(valeur)
        elif type_parametre == bool : valeurTmp = str(valeur)
        elif type_parametre == wx._gdi.Colour : valeurTmp = str(valeur)
        else : valeurTmp = ""

        if dictDonnees.has_key(nom) :
            
            if mode == "get" :
                # Un parametre existe :
                valeur = dictDonnees[nom]
                # On le formate pour le r�cup�rer sous son vrai format
                try :
                    if type_parametre == int : valeur = int(valeur)
                    if type_parametre == float : valeur = float(valeur)
                    if type_parametre == str : valeur = valeur
                    if type_parametre == unicode : valeur = valeur
                    if type_parametre == tuple : exec("valeur = " + valeur)
                    if type_parametre == list : exec("valeur = " + valeur)
                    if type_parametre == dict : exec("valeur = " + valeur)
                    if type_parametre == bool : exec("valeur = " + valeur)
                    if type_parametre == wx._gdi.Colour and valeur != "" : exec("valeur = " + valeur)
                except :
                    valeur = None
                dictFinal[nom] = valeur
                
            if mode == "set" :
                # On modifie la valeur du param�tre
                dictFinal[nom] = valeur
                if dictDonnees[nom] != valeurTmp :
                    listeModifications.append((valeurTmp, categorie, nom))
                
        else:
            # Le parametre n'existe pas, on le cr�� :
            listeAjouts.append((categorie, nom, valeurTmp))
            dictFinal[nom] = valeur

    # Sauvegarde des modifications
    if len(listeModifications) > 0 :
        DB.Executermany("UPDATE parametres SET parametre=? WHERE categorie=? and nom=?", listeModifications, commit=False)

    # Sauvegarde des ajouts
    if len(listeAjouts) > 0 :
        DB.Executermany("INSERT INTO parametres (categorie, nom, parametre) VALUES (?, ?, ?)", listeAjouts, commit=False)
        
    # Commit et fermeture de la DB
    if len(listeModifications) > 0 or len(listeAjouts) > 0 :
        DB.Commit() 
    DB.Close()
    return dictFinal




# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
def Parametres(mode="get", categorie="", nom="", valeur=None, nomFichier=""):
    """ M�morise ou r�cup�re un param�tre quelconque dans la base de donn�es """
    """ Le param�tre doit �tre str ou unicode obligatoirement """
    """ si mode = 'get' : valeur est la valeur par d�faut | si mode = 'set' : valeur est la valeur � donner au param�tre """
   
    # Pr�paration de la valeur par d�faut
    type_parametre = type(valeur)
    if type_parametre == int : valeurTmp = str(valeur)
    elif type_parametre == float : valeurTmp = str(valeur)
    elif type_parametre == str : valeurTmp = valeur
    elif type_parametre == unicode : valeurTmp = valeur
    elif type_parametre == tuple : valeurTmp = str(valeur)
    elif type_parametre == list : valeurTmp = str(valeur)
    elif type_parametre == dict : valeurTmp = str(valeur)
    elif type_parametre == bool : valeurTmp = str(valeur)
    else : valeurTmp = ""
    
    # Recherche du parametre
    DB = GestionDB.DB(nomFichier=nomFichier)
    
    # Si aucun fichier n'est charg�, on renvoie la valeur par d�faut :
    if DB.echec == 1 :
        return valeur

    req = u"""SELECT IDparametre, parametre FROM parametres WHERE categorie="%s" AND nom="%s" ;""" % (categorie, nom)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) != 0 :
        if mode == "get" :
            # Un parametre existe :
            valeurTmp = listeDonnees[0][1]
            # On le formate pour le r�cup�rer sous son vrai format
            if type_parametre == int : valeurTmp = int(valeurTmp)
            if type_parametre == float : valeurTmp = float(valeurTmp)
            if type_parametre == str : valeurTmp = valeurTmp
            if type_parametre == unicode : valeurTmp = valeurTmp
            if type_parametre == tuple : exec("valeurTmp = " + valeurTmp)
            if type_parametre == list : exec("valeurTmp = " + valeurTmp)
            if type_parametre == dict : exec("valeurTmp = " + valeurTmp)
            if type_parametre == bool : exec("valeurTmp = " + valeurTmp)
        else:
            # On modifie la valeur du param�tre
            IDparametre = listeDonnees[0][0]
            listeDonnees = [("categorie",  categorie), ("nom",  nom), ("parametre",  valeurTmp),]
            DB.ReqMAJ("parametres", listeDonnees, "IDparametre", IDparametre)
            valeurTmp = valeur
    else:
        # Le parametre n'existe pas, on le cr�� :
        listeDonnees = [("categorie",  categorie), ("nom",  nom), ("parametre",  valeurTmp),]
        newID = DB.ReqInsert("parametres", listeDonnees)
        valeurTmp = valeur
    DB.Close()
    return valeurTmp


def TestParametre(categorie="", nom="", valeur=None, nomFichier=""):
    """ V�rifie si un param�tre existe dans le fichier """
    DB = GestionDB.DB(nomFichier=nomFichier)
    req = u"""SELECT IDparametre, parametre FROM parametres WHERE categorie="%s" AND nom="%s" ;""" % (categorie, nom)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    if len(listeDonnees) == 0 :
        return False
    else:
        return True


# ----------------------- TESTS --------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == u"__main__":
    print ParametresCategorie(mode="get", categorie="parametres_grille_conso", dictParametres={"affiche_colonne_memo":True, "test":u"�a marche !"}, nomFichier="")
    
    
    