#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _

import shelve
import cStringIO
import GestionDB

    
def Exporter(IDmodele=None, fichier="", depuisFichierDefaut=False):
    """ Exportation d'un modèle de document """
    # Ouverture Base
    if depuisFichierDefaut == False :
        DB = GestionDB.DB()
    else :
        DB = GestionDB.DB(nomFichier="Defaut.dat", suffixe=None)
    
    # Récupération des infos sur le modèle
    req = """SELECT nom, categorie, largeur, hauteur, IDfond, defaut
    FROM documents_modeles
    WHERE IDmodele=%d
    ;""" % IDmodele
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    nom, categorie, largeur, hauteur, IDfond, defaut = listeDonnees[0]

    # Récupération des champs de la table des objets
    listeColonnes = DB.GetListeChamps2("documents_objets")
    listeChamps = []
    for nomChamp, typeChamp in listeColonnes :
        listeChamps.append(nomChamp) 
    
    # Récupération des données à exporter
    req = """SELECT %s
    FROM documents_objets
    WHERE IDmodele=%d
    ;""" % (", ".join(listeChamps), IDmodele)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    
    # Fermeture Base
    DB.Close() 
    
    # Mémorisation des objets
    listeObjets = []
    for donnees in listeDonnees :
        dictObjet = {} 
        index = 0
        for donnee in donnees :
            nomChamp = listeColonnes[index][0]
            typeChamp = listeColonnes[index][1]
            
            # Pour les champs BLOB
            if (typeChamp == "BLOB" or typeChamp == "LONGBLOB") and donnee != None :
                buffer = cStringIO.StringIO(donnee)
                donnee = buffer.read()
            
            # Mémorisation
            if nomChamp not in ("IDmodele", "IDobjet") :
                dictObjet[nomChamp] = donnee
                
            index += 1
        listeObjets.append(dictObjet)
    
    # Enregistrement dans un fichier Shelve
    if fichier != "" :
        doc = shelve.open(fichier, "n")
        doc["nom"] = nom
        doc["categorie"] = categorie
        doc["largeur"] = largeur
        doc["hauteur"] = hauteur
        doc["IDfond"] = IDfond
        doc["defaut"] = defaut
        doc["objets"] = listeObjets
        doc.close()
    
    # Mémorise également les résultats dans un dictionnaire
    dictDonnees = {}
    dictDonnees["nom"] = nom
    dictDonnees["categorie"] = categorie
    dictDonnees["largeur"] = largeur
    dictDonnees["hauteur"] = hauteur
    dictDonnees["IDfond"] = IDfond
    dictDonnees["defaut"] = defaut
    dictDonnees["objets"] = listeObjets
    
    return dictDonnees
    

def InfosFichier(fichier=""):
    """ Récupère les infos principales sur un fichier """
    dictInfos = {}
    fichier = shelve.open(fichier, "r")
    for key, valeur in fichier.iteritems() :
        dictInfos[key] = valeur
    fichier.close()
    return dictInfos

    
def Importer(fichier="", dictDonnees={}, IDfond=None, defaut=0):
    """ Importation d'un modèle de document depuis un fichier SHELVE ou un DICTIONNAIRE """
    DB = GestionDB.DB()
    
    if fichier != "" :
        doc = shelve.open(fichier, "r")
    else :
        doc = dictDonnees
    
    # Saisie dans la table documents_modeles
    listeDonnees = [    
            ("nom", doc["nom"]),
            ("categorie", doc["categorie"]),
            ("supprimable", 1),
            ("largeur", doc["largeur"]),
            ("hauteur", doc["hauteur"]),
            ("observations", ""),
            ("IDfond", IDfond),
            ("defaut", defaut),
            ]
    IDmodele = DB.ReqInsert("documents_modeles", listeDonnees)
    
    # Saisie dans la table documents_objets
    listeObjets = doc["objets"]
    for dictObjet in listeObjets :
        dictObjet["IDmodele"] = IDmodele
        
        listeDonnees = []
        for champ, donnee in dictObjet.iteritems() :
            if champ == "image" :
                blob = donnee
                donnee = None
            listeDonnees.append((champ, donnee))
            
        IDobjet = DB.ReqInsert("documents_objets", listeDonnees)
        
        if blob != None :
            DB.MAJimage(table="documents_objets", key="IDobjet", IDkey=IDobjet, blobImage=blob, nomChampBlob="image")
    
    DB.Close()
    
    if fichier != "" :
        doc.close()
    
    return IDmodele




# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def DupliquerModele(IDmodele=None, nom="", categorie=None) :
    """ Dupliquer un modèle de doc """
    DB = GestionDB.DB()
    
    # Duplication du modèle
    conditions = "IDmodele=%d" % IDmodele
    dictModifications = {"nom" : nom}
    if categorie != None :
        dictModifications["categorie"] = categorie
    newIDmodele = DB.Dupliquer("documents_modeles", "IDmodele", conditions, dictModifications)
    
    # Duplication des objets
    conditions = "IDmodele=%d" % IDmodele
    dictModifications = {"IDmodele" : newIDmodele}
    newIDobjet = DB.Dupliquer("documents_objets", "IDobjet", conditions, dictModifications)

    DB.Close() 



# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def ImporterDepuisFichierDefaut(IDmodele=None, nom=None, IDfond=1, defaut=0):
    """ Importer un modèle de document depuis le fichier defaut.dat """
    try :
        dictDonnees = Exporter(IDmodele=IDmodele, depuisFichierDefaut=True)
        if nom != None : dictDonnees["nom"] = nom
        Importer(dictDonnees=dictDonnees, IDfond=IDfond, defaut=defaut)
    except Exception, err :
        print "Erreur dans l'importation d'un modele depuis le fichier defaut :", err
        return False



if __name__ == "__main__":
    # Avec un fichier
##    Exporter(IDmodele=5, fichier="Temp/TestExport.ndc")
##    Importer(fichier="Temp/TestExport.ndc")
    
    # Avec un dictionnaire depuis le fichier defaut.dat
    ImporterDepuisFichierDefaut(IDmodele=13, nom=None, IDfond=1, defaut=0)
    
    # Dupliquer un modèle
##    DupliquerModele(IDmodele=5, nom=_(u"Attestation fiscale par défaut 2"), categorie="attestation_fiscale")

    
