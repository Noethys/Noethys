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
    print("Nbre fichiers PNG trouvees :", len(listeFichiersPNG))
    # Convertit les PNG
    nbreConversions = 0
    for fichier in listeFichiersPNG :
        resultat = ConvertirImagePNG(fichier)
        if resultat == True :
            nbreConversions += 1
    print("%d images PNG ont ete converties" % nbreConversions)
    

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def rgb_to_hex(value):
    return '#%02x%02x%02x' % (value[0], value[1], value[2])

def CouleurStrToTuple(texte=None):
    if texte == None or len(texte) == 0 : return None
    couleur = texte[1:-1].split(",")
    couleur = (int(couleur[0]), int(couleur[1]), int(couleur[2]) )
    return couleur

def ConvertToRVB(couleur=None):
    if type(couleur) == str :
        r, v, b = hex_to_rgb(couleur)
    if type(couleur) == tuple :
        r, v, b = couleur[0], couleur[1], couleur[2]
    if type(couleur) == wx.Colour :
        col = couleur.Get()
        r, v, b = col[0], col[1], col[2]
    return (r, v, b)

def CreationCarreCouleur(largeur, hauteur, couleur=None, contour=False):
    """ couleur peut être RGB ou HEXA """
    if 'phoenix' in wx.PlatformInfo:
        bmp = wx.Image(largeur, hauteur, True)
        # Dessin du contour
        if contour == True :
            r, v, b = ConvertToRVB(wx.Colour(0, 0, 0))
        else :
            r, v, b = ConvertToRVB(couleur)
        bmp.SetRGB((0, 0, largeur, hauteur), r, v, b)
        # Dessin du carré intérieur
        r, v, b = ConvertToRVB(couleur)
        bmp.SetRGB((1, 1, largeur-2, hauteur-2), r, v, b)
    else :
        bmp = wx.EmptyImage(largeur, hauteur, True)
        # Dessin du contour
        if contour == True :
            r, v, b = ConvertToRVB(wx.Colour(0, 0, 0))
        else :
            r, v, b = ConvertToRVB(couleur)
        bmp.SetRGBRect((0, 0, largeur, hauteur), r, v, b)
        # Dessin du carré intérieur
        r, v, b = ConvertToRVB(couleur)
        bmp.SetRGBRect((1, 1, largeur-2, hauteur-2), r, v, b)
    return bmp.ConvertToBitmap()



def PILtoWx(image):
    """Convert a PIL image to wx image format"""
    largeur, hauteur = image.size
    if 'phoenix' in wx.PlatformInfo:
        imagewx = wx.Image(largeur, hauteur)
        imagewx.SetData(image.tobytes('raw', 'RGB'))
        imagewx.SetAlpha(image.convert("RGBA").tobytes()[3::4])
    else :
        imagewx = wx.EmptyImage(largeur, hauteur)
        imagewx.SetData(image.tobytes('raw', 'RGB'))
        imagewx.SetAlphaData(image.convert("RGBA").tobytes()[3::4])
    return imagewx


if __name__ == "__main__":
    app = wx.App(0)
    ConvertirToutesImagesPNG()