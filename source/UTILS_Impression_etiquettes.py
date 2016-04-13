#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import datetime
import FonctionsPerso

import DLG_Noedoc

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen.canvas import Canvas

try: import psyco; psyco.full()
except: pass


class Impression():
    """ Impression des étiquettes """
    def __init__(self, 
                    IDmodele=None, 
                    taillePage=(210, 297),
                    listeValeurs=[],
                    margeHaut=10,
                    margeGauche=10,
                    margeBas = 10,
                    margeDroite=10,
                    espaceVertical=5,
                    espaceHorizontal=5,
                    nbre_copies=1,
                    AfficherContourEtiquette=True,
                    AfficherReperesDecoupe=True,
                    ):

        # ----------------------------------------------------------------------------------------------------------------------------------------
        
        def AfficheReperesDecoupe():
            if AfficherReperesDecoupe == True :
                canvas.setStrokeColor( (0.9, 0.9, 0.9) )
                canvas.setLineWidth(0.25)
                # Repères de colonnes
                for y1, y2 in [(hauteurPage*mm-4*mm, hauteurPage*mm-margeHaut*mm+2*mm), (4*mm, margeBas-2*mm)] :
                    x = margeGauche*mm
                    for numColonne in range(0, nbreColonnes):
                        canvas.line(x, y1, x, y2)
                        x += largeurEtiquette*mm
                        canvas.line(x, y1, x, y2)
                        x += espaceHorizontal*mm
                # Repères de lignes
                for x1, x2 in [(4*mm, margeGauche*mm-2*mm), (largeurPage*mm-4*mm, largeurPage*mm-margeDroite*mm+2*mm)] :
                    y = hauteurPage*mm - margeHaut*mm
                    for numLigne in range(0, nbreLignes):
                        canvas.line(x1, y, x2, y)
                        y -= hauteurEtiquette*mm
                        canvas.line(x1, y, x2, y)
                        y -= espaceVertical*mm
        
        # -----------------------------------------------------------------------------------------------------------------------------------------
        
        largeurPage = taillePage[0]
        hauteurPage = taillePage[1]

        # Initialisation du modèle de document
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        largeurEtiquette = modeleDoc.dictInfosModele["largeur"]
        hauteurEtiquette = modeleDoc.dictInfosModele["hauteur"]
        
        # Calcul du nbre de colonnes et de lignes
        nbreColonnes = (largeurPage - margeGauche - margeDroite + espaceHorizontal) / (largeurEtiquette + espaceHorizontal)
        nbreLignes = (hauteurPage - margeHaut - margeBas + espaceVertical) / (hauteurEtiquette + espaceVertical)
        
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("ETIQUETTES", "pdf")
        canvas = Canvas(nomDoc, pagesize=(largeurPage*mm, hauteurPage*mm))
        
        # Création des étiquettes
        numColonne = 0
        numLigne = 0
        for dictValeurs in listeValeurs :
            for num_copie in range(0, nbre_copies) :
                print num_copie, nbre_copies
                x = margeGauche + ((largeurEtiquette + espaceHorizontal) * numColonne)
                y = hauteurPage - margeHaut - hauteurEtiquette - ((hauteurEtiquette + espaceVertical) * numLigne)

                # Positionnement sur la feuille
                canvas.saveState()
                canvas.translate(x*mm, y*mm)

                # Création du clipping
                p = canvas.beginPath()
                canvas.setStrokeColor( (1, 1, 1) )
                canvas.setLineWidth(0.25)
                p.rect(0, 0, largeurEtiquette*mm, hauteurEtiquette*mm)
                canvas.clipPath(p)

                # Dessin de l'étiquette
                modeleDoc.DessineFond(canvas, dictChamps=dictValeurs)
                etat = modeleDoc.DessineTousObjets(canvas, dictChamps=dictValeurs)
                if etat == False :
                    return

                # Dessin du contour de l'étiquette
                if AfficherContourEtiquette == True :
                    canvas.setStrokeColor( (0, 0, 0) )
                    canvas.setLineWidth(0.25)
                    canvas.rect(0, 0, largeurEtiquette*mm, hauteurEtiquette*mm)

                canvas.restoreState()

                # Saut de colonne
                numColonne += 1
                # Saut de ligne
                if numColonne > nbreColonnes - 1 :
                    numLigne += 1
                    numColonne = 0
                # Saut de page
                if numLigne > nbreLignes - 1 :
                    AfficheReperesDecoupe()
                    canvas.showPage()
                    numLigne = 0

        # Affichage des repères de découpe
        AfficheReperesDecoupe()
                    
        # Finalisation du PDF
        canvas.save()
        
        try :
            FonctionsPerso.LanceFichierExterne(nomDoc)
        except :
            print "Probleme dans l'edition des etiquettes"
        






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    # Exemples de valeurs :
    listeValeurs = []
    for x in range(0, 12):
        dictTemp = {
            "{IDINDIVIDU}" : str(3), 
            "{INDIVIDU_NOM}" : _(u"DUPOND"), 
            "{INDIVIDU_PRENOM}" : _(u"Gérard"),
            }
        listeValeurs.append(dictTemp)
    # Lance édition PDF
    Impression(IDmodele=39, taillePage=(210, 297), listeValeurs=listeValeurs)
    app.MainLoop()
