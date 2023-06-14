#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import GestionDB
import wx
import six


def GetNom():
    DB = GestionDB.DB()
    req = """SELECT nom, rue, cp, ville
    FROM organisateur WHERE IDorganisateur=1;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return ""
    nom = listeDonnees[0][0]
    if nom == None :
        nom = ""
    return nom

def RecadreImg(img=None, tailleImage=(40, 40)):
    # Recadre l'image en fonction de la taille du staticBitmap
    tailleMaxi = max(tailleImage)
    largeur, hauteur = img.GetSize()
    if max(largeur, hauteur) > tailleMaxi :
        if largeur > hauteur :
            hauteur = hauteur * tailleMaxi / largeur
            largeur = tailleMaxi
        else:
            largeur = largeur * tailleMaxi / hauteur
            hauteur = tailleMaxi
    img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
    position = (((tailleImage[0]/2.0) - (largeur/2.0)), ((tailleImage[1]/2.0) - (hauteur/2.0)))
    img.Resize(tailleImage, position, 255, 255, 255)
    return img

def GetDonnees(tailleLogo=(40, 40)) :
    DB = GestionDB.DB()
    req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape, logo, logo_update
    FROM organisateur WHERE IDorganisateur=1;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape, logo, logo_update = listeDonnees[0]
    if nom == None : nom = u""
    if rue == None : rue = u""
    if cp == None : cp = u""
    if ville == None : ville = u""
    if tel == None : tel = u""
    if fax == None : fax = u""
    if mail == None : mail = u""
    if site == None : site = u""
    if num_agrement == None : num_agrement = u""
    if num_siret == None : num_siret = u""
    if code_ape == None : code_ape = u""
    if logo != None :
        io = six.BytesIO(logo)
        if 'phoenix' in wx.PlatformInfo:
            img = wx.Image(io, wx.BITMAP_TYPE_ANY)
        else :
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
        img = RecadreImg(img, tailleLogo)
        logo = img.ConvertToBitmap()
    dictDonnees = {
        "nom":nom, "rue":rue, "cp":cp, "ville":ville, "tel":tel, "fax":fax, "mail":mail, "site":site, 
        "num_agrement":num_agrement, "num_siret":num_siret, "code_ape":code_ape, "logo":logo, "logo_update":logo_update,
        }
    return dictDonnees




if __name__ == '__main__':
    print(GetNom())