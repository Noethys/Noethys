#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB

LIB_CHARGEES = True
try :
    import win32ui
    import win32print
except :
    LIB_CHARGEES = False


def GetListeImprimantes():
    listeImprimantes = []
    try : 
        for a, b, nom, c in win32print.EnumPrinters(2) :
            listeImprimantes.append(nom)
    except Exception as err :
        print("Erreur dans recuperation de la liste des imprimantes : ", err)
    return listeImprimantes


def Impression(lignes=[], imprimante=None, titre=_(u"Ticket"), nomPolice="Arial", taillePolice=15, interligne=5) :    
    if len(lignes) == 0 : 
        return

    # Vérifie que les librairies windows ont bien été chargées
    if LIB_CHARGEES == False :
        dlg = wx.MessageDialog(None, _(u"L'outil d'impression de ticket ne peut pas être chargé. Ce problème sera sûrement résolu en téléchargeant le Package redistribuable Microsoft Visual C++ 2008 (x86) de Microsoft. Rendez-vous sur http://www.microsoft.com/fr-fr/download/details.aspx?id=29."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return

    # Sélection de l'imprimante
    if imprimante != None :
        if imprimante not in GetListeImprimantes() :
            imprimante = None
    if imprimante == None :
        imprimante = win32print.GetDefaultPrinter()
    
    # Initialisation du document
    dc = win32ui.CreateDC() 
    try :
        dc.CreatePrinterDC(imprimante) 
    except Exception as err :
        print("Erreur dans l'impression du ticket :", err)
        print("Test sur l'imprimante par defaut...")
        dc.CreatePrinterDC() 
    dc.StartDoc(titre)
    dc.StartPage() 
    
    # Création des lignes
    y = 0
    for ligne in lignes :
        font = win32ui.CreateFont({"name" : nomPolice, "height" : taillePolice})
        dc.SelectObject(font)
        dc.TextOut(0, y, ligne)
        y += taillePolice + interligne
    
    # Finalisation du document
    dc.EndPage() 
    dc.EndDoc() 
    del dc
    




def ImpressionModele(IDmodele=None, dictValeurs={}, titre=_(u"Ticket")):
    if IDmodele == None : 
        return []
    
    # Importation du modèle
    DB = GestionDB.DB()
    req = """SELECT categorie, nom, description, lignes, defaut, taille, interligne, imprimante
    FROM modeles_tickets
    WHERE IDmodele=%d;
    """ % IDmodele
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return []
    categorie, nom, description, lignes, defaut, taille, interligne, imprimante = listeDonnees[0]
    lignes = lignes.split("@@@")
    if taille == None : taille = 15
    if interligne == None : interligne = 5

    # Remplacement des valeurs
    lignesFinales = []
    for ligne in lignes :
        for motcle, valeur in dictValeurs.items() :
            ligne = ligne.replace(motcle, valeur)
        lignesFinales.append(ligne)
        
    # Impression
    Impression(lignes=lignesFinales, imprimante=imprimante, titre=titre, taillePolice=taille, interligne=interligne)
        
        


if __name__ == "__main__":
    lignes = [
        _(u"Ceci est la ligne 1"),
        _(u"Ceci est la ligne 2"),
        _(u"Ceci est la ligne 3"),
        _(u"Ceci est la ligne 4"),
        _(u"Ceci est la ligne 5"),
        ]
    Impression(lignes=lignes, imprimante=None, titre=_(u"Ticket"))
