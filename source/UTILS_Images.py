#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Image
import wx
import os


def ConvertirImagePNG(fichier="") :
    # Chargement de l'image à convertir
    image = Image.open(fichier)
    image.load() 
    profile = image.info.get("icc_profile")
    
    if profile != None :
        # Créée une image sans icc_profile
        nouvelleImage = Image.new("RGBA", image.size)
        nouvelleImage.paste(image) 
        
        # Supprime l'image ancienne
        os.remove(fichier)
        
        # Sauvegarde la nouvelle image
        nouveauFichier = fichier
        nouvelleImage.save(nouveauFichier, format="png")
        return True
    
    return False


def ConvertirToutesImagesPNG():
    """ Convertit toutes les images PNG du répertoire Noethys """
    racine = "Images"
    # Recherche les PNG présents
    tree = os.walk(racine)
    listeFichiersPNG = []
    for repertoire, listeRepertoires, listeFichiers in tree :
        for fichier in listeFichiers :
            if fichier.endswith(".png") :
                listeFichiersPNG.append(repertoire.replace("\\", "/") + "/" + fichier)
    print "Nbre fichiers PNG trouvees :", len(listeFichiersPNG)
    # Convertit les PNG
    nbreConversions = 0
    for fichier in listeFichiersPNG :
        resultat = ConvertirImagePNG(fichier)
        if resultat == True :
            nbreConversions += 1
    print "%d images PNG ont ete converties" % nbreConversions
    

if __name__ == "__main__":
    app = wx.App(0)
    ConvertirToutesImagesPNG()