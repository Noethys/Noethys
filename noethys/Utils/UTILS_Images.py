#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from PIL import Image
import Chemins
import wx
import os


def RecadreImg(img=None, taille_image=None):
    tailleMaxi = max(taille_image)
    largeur, hauteur = img.GetSize()
    if max(largeur, hauteur) > tailleMaxi:
        if largeur > hauteur:
            hauteur = hauteur * tailleMaxi / largeur
            largeur = tailleMaxi
        else:
            largeur = largeur * tailleMaxi / hauteur
            hauteur = tailleMaxi
    img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
    position = (((taille_image[0] / 2.0) - (largeur / 2.0)), ((taille_image[1] / 2.0) - (hauteur / 2.0)))
    img.Resize(taille_image, position, 255, 255, 255)
    return img



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
    racine = Chemins.GetStaticPath("Images")
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