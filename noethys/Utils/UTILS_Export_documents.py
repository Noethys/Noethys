#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import six
import GestionDB
from Utils import UTILS_Json
import base64


def Exporter(IDmodele=None, fichier="", depuisFichierDefaut=False):
    """ Exportation d'un modèle de document """
    # Ouverture Base
    if depuisFichierDefaut == False :
        DB = GestionDB.DB()
    else :
        DB = GestionDB.DB(nomFichier=Chemins.GetStaticPath("Databases/Defaut.dat"), suffixe=None)

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
            if "BLOB" in typeChamp.upper() and donnee != None :
                buffer = six.BytesIO(donnee)
                donnee = buffer.read()

            if nomChamp == "image" and donnee != None:
                donnee = base64.b64encode(donnee)

            # Mémorisation
            if nomChamp not in ("IDmodele", "IDobjet") :
                dictObjet[nomChamp] = donnee

            index += 1
        listeObjets.append(dictObjet)

    # Mémorisation dans un dict
    data = {
        "nom": nom,
        "categorie": categorie,
        "largeur": largeur,
        "hauteur": hauteur,
        "IDfond": IDfond,
        "defaut": defaut,
        "objets": listeObjets,
    }

    # Enregistrement dans un fichier Json
    if fichier != "" :
        if six.PY2:
            fichier = fichier.encode("utf8")
        UTILS_Json.Ecrire(nom_fichier=fichier, data=data)

    return data


def InfosFichier(fichier=""):
    """ Récupère les infos principales sur un fichier """
    if six.PY2:
        fichier = fichier.encode("utf8")
    data = UTILS_Json.Lire(fichier)
    return data


def Importer(fichier="", dictDonnees={}, IDfond=None, defaut=0):
    """ Importation d'un modèle de document depuis un fichier JSON ou un DICTIONNAIRE """
    DB = GestionDB.DB()

    if fichier != "" :
        if six.PY2:
            fichier = fichier.encode("utf8")
        data = UTILS_Json.Lire(fichier)
    else :
        data = dictDonnees

    # Saisie dans la table documents_modeles
    listeDonnees = [
            ("nom", data["nom"]),
            ("categorie", data["categorie"]),
            ("supprimable", 1),
            ("largeur", data["largeur"]),
            ("hauteur", data["hauteur"]),
            ("observations", ""),
            ("IDfond", IDfond),
            ("defaut", defaut),
            ]
    IDmodele = DB.ReqInsert("documents_modeles", listeDonnees)

    # Saisie dans la table documents_objets
    listeObjets = data["objets"]
    for dictObjet in listeObjets :
        dictObjet["IDmodele"] = IDmodele

        listeDonnees = []
        for champ, donnee in dictObjet.items() :
            if champ == "image" :
                try :
                    donnee = base64.b64decode(donnee)
                except:
                    pass
                blob = donnee
                donnee = None
            listeDonnees.append((champ, donnee))

        IDobjet = DB.ReqInsert("documents_objets", listeDonnees)

        if blob != None :
            DB.MAJimage(table="documents_objets", key="IDobjet", IDkey=IDobjet, blobImage=blob, nomChampBlob="image")

    DB.Close()
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
    except Exception as err :
        print("Erreur dans l'importation d'un modele depuis le fichier defaut :", err)
        return False



if __name__ == "__main__":
    # Avec un fichier
    Exporter(IDmodele=5, fichier="C:/Users/Test/Desktop/TestExport.ndc")
    # Importer(fichier="Tests/TestExport.ndc")

    # Avec un dictionnaire depuis le fichier defaut.dat
    # ImporterDepuisFichierDefaut(IDmodele=13, nom=None, IDfond=1, defaut=0)

    # Dupliquer un modèle
    # DupliquerModele(IDmodele=5, nom=_(u"Attestation fiscale par défaut 2"), categorie="attestation_fiscale")

    pass
