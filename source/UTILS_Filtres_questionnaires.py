#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from CTRL_Questionnaire import LISTE_CONTROLES 



def GetDictControles():
    dictControles = {}
    for dictControle in LISTE_CONTROLES :
        dictControles[dictControle["code"]] = dictControle
    return dictControles

def Filtre(controle=None, choix="", criteres="", reponse=""):
    """ Compare un filtre avec une réponse """
    # Recherche le type de filtre
    filtre = GetDictControles()[controle]["filtre"]
    
    # TEXTE
    if filtre == "texte" :
        if choix == "EGAL" : 
            if reponse == criteres : return True
        if choix == "DIFFERENT" : 
            if reponse != criteres : return True
        if choix == "CONTIENT" : 
            if criteres in reponse : return True
        if choix == "CONTIENTPAS" : 
            if criteres not in reponse : return True
        if choix == "VIDE" : 
            if reponse == "" : return True
        if choix == "PASVIDE" : 
            if reponse != "" : return True
    
    # ENTIER
    if filtre == "entier" :
        if choix == "EGAL" : 
            if int(reponse) == int(criteres) : return True
        if choix == "DIFFERENT" : 
            if int(reponse) != int(criteres) : return True
        if choix == "SUP" : 
            if int(reponse) > int(criteres) : return True
        if choix == "SUPEGAL" : 
            if int(reponse) >= int(criteres) : return True
        if choix == "INF" : 
            if int(reponse) < int(criteres) : return True
        if choix == "INFEGAL" : 
            if int(reponse) <= int(criteres) : return True
        if choix == "COMPRIS" : 
            if int(reponse) >= int(criteres.split(";")[0]) and int(reponse) <= int(criteres.split(";")[1]) : return True

    # DATE
    if filtre == "date" :
        if choix == "EGAL" : 
            if str(reponse) == str(criteres) : return True
        if choix == "DIFFERENT" : 
            if str(reponse) != str(criteres) : return True
        if choix == "SUP" : 
            if str(reponse) > str(criteres) : return True
        if choix == "SUPEGAL" : 
            if str(reponse) >= str(criteres) : return True
        if choix == "INF" : 
            if str(reponse) < str(criteres) : return True
        if choix == "INFEGAL" : 
            if str(reponse) <= str(criteres) : return True
        if choix == "COMPRIS" : 
            if str(reponse) >= str(criteres.split(";")[0]) and str(reponse) <= str(criteres.split(";")[1]) : return True

    # COCHE
    if filtre == "coche" :
        if choix == "COCHE" : 
            if int(reponse) == 1 : return True
        if choix == "DECOCHE" : 
            if int(reponse) == 0 : return True

    # CHOIX
    if filtre == "choix" :
        listeIDchoix = criteres.split(";")
        listeIDreponses = reponse.split(";")
        for ID in listeIDreponses :
            if ID in listeIDchoix :
                return True
    
    return False



            
            
if __name__ == '__main__':
    print Filtre(controle="ligne_texte", choix="EGAL", criteres="bonjour", reponse="bonjour")
    