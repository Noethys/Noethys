#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""

import wx
import wx.grid as gridlib
import wx.lib.wordwrap as wordwrap
##import Outils.gridlabelrenderer as glr
import wx.lib.mixins.gridlabelrenderer as glr
import CTRL_Grille
import datetime

import UTILS_Dates
import UTILS_Couleurs
from CTRL_Saisie_transport import DICT_CATEGORIES as DICT_CATEGORIES_TRANSPORTS

PADDING_MULTIHORAIRES = {"vertical" : 5, "horizontal" : 10}



def TriTransports(dictTransports={}):
    """ Tri les transports en fonction de l'heure de départ """
    listeID = []
    listeTemp = []
    for IDtransport, dictTransport in dictTransports.iteritems() :
        listeTemp.append((dictTransport["depart_heure"], IDtransport))
    listeTemp.sort() 
    for depart_heure, IDtransport in listeTemp :
        listeID.append(IDtransport)
    return listeID


def DrawBorder(grid, dc, rect):
    """
    Draw a standard border around the label, to give a simple 3D
    effect like the stock wx.grid.Grid labels do.
    """
    top = rect.top
    bottom = rect.bottom
    left = rect.left
    right = rect.right        
    dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
    dc.DrawLine(right, top, right, bottom)
    dc.DrawLine(left, top, left, bottom)
    dc.DrawLine(left, bottom, right, bottom)
    dc.SetPen(wx.WHITE_PEN)
    dc.DrawLine(left+1, top, left+1, bottom)
    dc.DrawLine(left+1, top, right, top)






class CaseStandard(gridlib.PyGridCellRenderer):
    def __init__(self, case):
        gridlib.PyGridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.GetCouleur(), wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        text = grid.GetCellValue(row, col)
        if self.case.ouvert == True :
            DrawBorder(grid, dc, rect)
        dc.DrawText(text, rect[0], rect[1])
        
        conso = self.case.conso
        
        # Dessin du cadenas VERROUILLAGE
        if self.case.etat == None and self.case.verrouillage == 1 :
            dc.SetBrush(wx.Brush( (100, 100, 100), wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
            dc.SetBrush(wx.Brush(self.GetCouleur(), wx.SOLID))
        
        if self.case.verrouillage == 1 :
            tailleImage = 8
            paddingImage = 3
            bmp = wx.Bitmap("Images/Special/Cadenas_ferme.png", wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, rect[0]+tailleImage-paddingImage, rect[1]+paddingImage)
        
        # Dessin de l'image PRESENT (Coche verte)
        if self.case.etat == "present" :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, rect[0]+rect[2]-tailleImage-paddingImage, rect[1]+paddingImage)
            
        # Dessin de l'image ABSENT JUSTIFIEE (Croix rouge)
        if self.case.etat == "absentj" :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap("Images/16x16/absentj.png", wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, rect[0]+rect[2]-tailleImage-paddingImage, rect[1]+paddingImage)
        
        # Dessin de l'image ABSENT INJUSTIFIEE (Croix rouge)
        if self.case.etat == "absenti" :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap("Images/16x16/absenti.png", wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, rect[0]+rect[2]-tailleImage-paddingImage, rect[1]+paddingImage)
            
        # Dessin de l'image SANS PRESTATION (Alerte)
        if self.case.etat in ("reservation", "present", "absenti", "absentj") and self.case.IDprestation == None and grid.afficheSansPrestation == True :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap("Images/16x16/Gratuit.png", wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, rect[0]+paddingImage, rect[1]+paddingImage)

        # Dessin de l'image FORFAIT CREDIT
        if self.case.etat in ("reservation", "present", "absenti", "absentj") and self.case.IDprestation in self.grid.dictForfaits.keys() :
            couleurForfait = self.grid.dictForfaits[self.case.IDprestation]["couleur"]
            dc.SetBrush(wx.Brush(couleurForfait, wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            #dc.DrawCircle(rect[0]+10, rect[1]+10, 4)
            dc.DrawPolygon([(0, 0), (7, 0), (0, 7)], xoffset=rect[0]+2, yoffset=rect[1]+1)

        # Ecrit les horaires si c'est une conso HORAIRE
        if self.grid.dictUnites[self.case.IDunite]["type"] == "Horaire" and self.case.etat in ("reservation", "present", "absenti", "absentj", "attente", "refus") :
            dc.SetTextForeground("BLACK")
            tailleFont = 7
            dc.SetFont(wx.Font(tailleFont, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            
            heure_debut = str(self.case.heure_debut)
            largeurFinaleTexte = dc.GetTextExtent(heure_debut)[0]
            xTexte = rect[0] + ((rect[2] - largeurFinaleTexte) / 2.0)
            dc.DrawText(heure_debut, xTexte-6, rect[1]+5)
            
            heure_fin = str(self.case.heure_fin)
            largeurFinaleTexte = dc.GetTextExtent(heure_fin)[0]
            xTexte = rect[0] + ((rect[2] - largeurFinaleTexte) / 2.0)
            dc.DrawText(heure_fin, xTexte-6, rect[1]+3 + tailleFont + 5)

        # Ecrit la quantité si c'est une conso QUANTITE
        if self.grid.dictUnites[self.case.IDunite]["type"] == "Quantite" and self.case.etat in ("reservation", "present", "absenti", "absentj", "attente", "refus") :
            dc.SetTextForeground("BLACK")
            tailleFont = 8
            dc.SetFont(wx.Font(tailleFont, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            quantite = str(self.case.quantite)
            largeurFinaleTexte = dc.GetTextExtent(quantite)[0]
            dc.DrawText(quantite, rect[0]+5, rect[1]+2)

        # Ecrit le nom du groupe
        if CTRL_Grille.AFFICHE_NOM_GROUPE == True and self.grid.dictUnites[self.case.IDunite]["type"] != "Horaire":
            if self.case.IDgroupe != None and self.case.IDgroupe != 0 and self.case.etat in ("reservation", "present", "absenti", "absentj", "attente", "refus") :
                nomGroupe = self.grid.dictGroupes[self.case.IDgroupe]["nom"]
                dc.SetTextForeground("#949494")
                dc.SetFont(wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
                nomGroupe = self.AdapteTailleTexte(dc, nomGroupe, rect[2]-6)
                largeurFinaleTexte = dc.GetTextExtent(nomGroupe)[0]
                xTexte = rect[0] + ((rect[2] - largeurFinaleTexte) / 2.0)
                dc.DrawText(nomGroupe, xTexte, rect.y + rect.height - 12)
                dc.SetTextForeground("BLACK")
        
            
    def MAJ(self):
        if self.grid != None :
            self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()
    
    def AdapteTailleTexte(self, dc, texte, tailleMaxi):
        """ Raccourcit le texte de l'intitulé en fonction de la taille donnée """
        # Pas de retouche nécessaire
        if dc.GetTextExtent(texte)[0] < tailleMaxi : return texte
        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= dc.GetTextExtent("W...")[0] : return "..."
        # Retouche nécessaire
        tailleTexte = dc.GetTextExtent(texte)[0]
        texteTemp = ""
        texteTemp2 = ""
        for lettre in texte :
            texteTemp += lettre
            if dc.GetTextExtent(texteTemp +"...")[0] < tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..." 

    def GetCouleur(self, conso=None):
        """ Obtient la couleur à appliquer à la case """        
        # Si fermée
        if self.case.ouvert == False : return CTRL_Grille.COULEUR_FERME
            
        # Si la case est sélectionnée
        if self.case.etat in ("reservation", "present", "absenti", "absentj") : return CTRL_Grille.COULEUR_RESERVATION
        if self.case.etat == "attente" : return CTRL_Grille.COULEUR_ATTENTE
        if self.case.etat == "refus" : return CTRL_Grille.COULEUR_REFUS
        
        # Si non sélectionnée
        dictInfosPlaces = self.case.GetInfosPlaces() 
        if dictInfosPlaces != None :
            nbrePlacesRestantes = None
            for IDunite_remplissage in self.grid.dictUnitesRemplissage[self.case.IDunite] :
                if (nbrePlacesRestantes == None or dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"] < nbrePlacesRestantes) and dictInfosPlaces[IDunite_remplissage]["nbrePlacesInitial"] not in (0, None) :
                    nbrePlacesRestantes = dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"]
                    seuil_alerte = dictInfosPlaces[IDunite_remplissage]["seuil_alerte"]
            
            if nbrePlacesRestantes != None :
                if nbrePlacesRestantes > seuil_alerte : return CTRL_Grille.COULEUR_DISPONIBLE
                if nbrePlacesRestantes > 0 and nbrePlacesRestantes <= seuil_alerte : return CTRL_Grille.COULEUR_ALERTE
                if nbrePlacesRestantes <= 0 : return CTRL_Grille.COULEUR_COMPLET
        
        return CTRL_Grille.COULEUR_NORMAL
        





class CaseMemo(gridlib.PyGridCellRenderer):
    def __init__(self, case):
        gridlib.PyGridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush("WHITE", wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
    
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        text = grid.GetCellValue(row, col)
        text = self.AdapteTailleTexte(dc, text, rect[2]-6)
        DrawBorder(grid, dc, rect)
        dc.DrawText(text, rect[0]+5, rect[1] + 6)
                    
    def MAJ(self):
        self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()
    
    def AdapteTailleTexte(self, dc, texte, tailleMaxi):
        """ Raccourcit le texte de l'intitulé en fonction de la taille donnée """
        # Pas de retouche nécessaire
        if dc.GetTextExtent(texte)[0] < tailleMaxi : return texte
        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= dc.GetTextExtent("W...")[0] : return "..."
        # Retouche nécessaire
        tailleTexte = dc.GetTextExtent(texte)[0]
        texteTemp = ""
        texteTemp2 = ""
        for lettre in texte :
            texteTemp += lettre
            if dc.GetTextExtent(texteTemp +"...")[0] < tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..." 






class CaseTransports(gridlib.PyGridCellRenderer):
    def __init__(self, case):
        gridlib.PyGridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.case.couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
    
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        DrawBorder(grid, dc, rect)
        
        # Affichage des transports
        padding = 6
        positionGauche = rect.left + padding
        for IDtransport in TriTransports(self.case.dictTransports) :
            dictTemp = self.case.dictTransports[IDtransport]
            categorie = dictTemp["categorie"]
            bmp = wx.Bitmap("Images/16x16/%s.png" % DICT_CATEGORIES_TRANSPORTS[categorie]["image"], wx.BITMAP_TYPE_ANY)
            dc.DrawBitmap(bmp, positionGauche, rect.top+padding)
            positionGauche += 20
                    
    def MAJ(self):
        if self.grid != None :
            self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()

    


class CaseActivite(gridlib.PyGridCellRenderer):
    def __init__(self, case):
        gridlib.PyGridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.case.couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        text = grid.GetCellValue(row, col)
##        dc.DrawText(text, rect[0], rect[1])
        if row == 0 :
            largeurTexte, hauteurTexte = dc.GetTextExtent(text)
            dc.DrawRotatedText(text, rect[0], rect[1]+largeurTexte+10, 90)
                    
    def MAJ(self):
        self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()


class CaseMultihoraires(gridlib.PyGridCellRenderer):
    def __init__(self, case):
        gridlib.PyGridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        # Préparation du buffer Image
        dcGrid = dc
        bmp = wx.EmptyBitmap(rect.GetWidth(), rect.GetHeight())
        image = wx.MemoryDC()
        image.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(image)
        gc.PushState() 
        
        rectCase = wx.Rect(0, 0, rect.GetWidth(), rect.GetHeight())
        x, y, largeur, hauteur = rectCase.x, rectCase.y, rectCase.width, rectCase.height
        
        # Dessin du fond
        if self.case.ouvert == True :
            self.couleurFond = wx.Colour(255, 255, 255)
        else :
            self.couleurFond = CTRL_Grille.COULEUR_FERME
        gc.SetBrush(wx.Brush(self.couleurFond, wx.SOLID))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(x, y, largeur, hauteur)

        if self.case.ouvert == True :
            # Dessin de la bordure 3D pour faire effet Case grid
            self.DrawBorder(grid, gc, rectCase)

            # Dessin du remplissage
            dictInfosPlaces = self.case.GetInfosPlaces() 
            if dictInfosPlaces != None :
                for IDunite_remplissage, valeurs in dictInfosPlaces.iteritems() :
                    
                    heure_min = UTILS_Dates.HeureStrEnTime(grid.dictRemplissage[IDunite_remplissage]["heure_min"])
                    if heure_min < self.case.heure_min :
                        heure_min = self.case.heure_min
                    heure_max = UTILS_Dates.HeureStrEnTime(grid.dictRemplissage[IDunite_remplissage]["heure_max"])
                    if heure_max > self.case.heure_max :
                        heure_max = self.case.heure_max
                        
                    nbrePlacesRestantes = valeurs["nbrePlacesRestantes"]
                    nbrePlacesInitial = valeurs["nbrePlacesInitial"]
                    nbrePlacesPrises = valeurs["nbrePlacesPrises"]
                    seuil_alerte = valeurs["seuil_alerte"]
                    nbreAttente = valeurs["nbreAttente"]
                
                    couleur = None
                    if nbrePlacesRestantes > seuil_alerte : couleur = CTRL_Grille.COULEUR_DISPONIBLE
                    if nbrePlacesRestantes > 0 and nbrePlacesRestantes <= seuil_alerte : couleur = CTRL_Grille.COULEUR_ALERTE
                    if nbrePlacesRestantes <= 0 : couleur = CTRL_Grille.COULEUR_COMPLET
                    
                    if couleur != None :
                        gc.SetBrush(wx.Brush(couleur, wx.SOLID))
                        gc.SetPen(wx.TRANSPARENT_PEN)
                        posG = self.case.HeureEnPos(heure_min) 
                        posD = self.case.HeureEnPos(heure_max) - posG
                        gc.DrawRectangle(posG + PADDING_MULTIHORAIRES["horizontal"], 1, posD, rectCase.height-2)

                                     
            # Dessin des graduations
            gc.SetPen(wx.Pen((230, 230, 230), 1, wx.SOLID))
            graduationStep = 25
            listeGraduations = range(UTILS_Dates.HeuresEnDecimal(self.case.heure_min), UTILS_Dates.HeuresEnDecimal(self.case.heure_max)+graduationStep, graduationStep)
##            if listeGraduations == [0] :
##                listeGraduations = [0, 1]
            step = 1.0 * (rect.width - PADDING_MULTIHORAIRES["horizontal"] * 2) / (len(listeGraduations) - 1)
            if step > 3.0 :
                x = PADDING_MULTIHORAIRES["horizontal"]
                for temp in listeGraduations :
                    gc.StrokeLine(x, 1, x, rect.height-2)
                    x += step


        # Dessin des barres
        for barre in self.case.listeBarres :
            conso = barre.conso
            
            # Calcul des coordonnées de la barre
            barre.UpdateRect()
            rectBarre = barre.GetRect("case")
            
            # get Couleur barre
            couleurBarre = self.GetCouleurBarre(conso)
            
            # Dessin du cadre
            gc.SetFont(attr.GetFont())
            gc.SetBrush(wx.Brush( (couleurBarre.Red(), couleurBarre.Green(), couleurBarre.Blue(), 180), wx.SOLID)) # 128 = demi-transparence
            
            couleurTexte = UTILS_Couleurs.ModifierLuminosite(couleurBarre, -50)
            couleur = (couleurTexte[0], couleurTexte[1], couleurTexte[2], 255)
            if barre.readOnly == True :
                gc.SetPen(wx.TRANSPARENT_PEN)
            else :
                gc.SetPen(wx.Pen(couleur, 1, wx.SOLID)) # 128 = demi-transparence
            gc.DrawRoundedRectangle(rectBarre.x, rectBarre.y, rectBarre.width, rectBarre.height, 5)
            
            # Dessin des horaires
            heure_debut_x, heure_debut_y, heure_debut_largeur, heure_debut_hauteur = self.DrawTexte(gc, rectBarre, barre.heure_debut.strftime("%Hh%M"), couleur=couleurTexte, position="gauche")
            heure_fin_x, heure_fin_y, heure_fin_largeur, heure_fin_hauteur = self.DrawTexte(gc, rectBarre, barre.heure_fin.strftime("%Hh%M"), couleur=couleurTexte, position="droite")
            
            # Dessin du cadenas VERROUILLAGE
            if conso.verrouillage == 1 :
                imageTemp = wx.Bitmap("Images/Special/Cadenas_ferme.png", wx.BITMAP_TYPE_ANY)
                largeurBmp, hauteurBmp = imageTemp.GetSize()
                gc.DrawBitmap(imageTemp, 2, rect.height-10, largeurBmp, hauteurBmp)

            # Dessin de l'image FORFAIT CREDIT
            if conso.etat in ("reservation", "present", "absenti", "absentj") and conso.IDprestation in grid.dictForfaits.keys() :
                couleurForfait = grid.dictForfaits[conso.IDprestation]["couleur"]
                gc.SetBrush(wx.Brush(couleurForfait, wx.SOLID))
                gc.SetPen(wx.TRANSPARENT_PEN)
                path = gc.CreatePath()
                path.AddLineToPoint(8, 0)
                path.AddLineToPoint(1, 8)
                path.AddLineToPoint(1, 0)
                gc.DrawPath(path)

            # Dessin des images
            listeImages = []

            # Dessin de l'image PRESENT (Coche verte)
            if conso.etat == "present" :
                listeImages.append(wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_ANY))
                
            # Dessin de l'image ABSENT JUSTIFIEE (Croix rouge)
            if conso.etat == "absentj" :
                listeImages.append(wx.Bitmap("Images/16x16/absentj.png", wx.BITMAP_TYPE_ANY))
            
            # Dessin de l'image ABSENT INJUSTIFIEE (Croix rouge)
            if conso.etat == "absenti" :
                listeImages.append(wx.Bitmap("Images/16x16/absenti.png", wx.BITMAP_TYPE_ANY))
                
            # Dessin de l'image SANS PRESTATION (Alerte)
            if conso.etat in ("reservation", "present", "absenti", "absentj") and conso.IDprestation == None and grid.afficheSansPrestation == True :
                listeImages.append(wx.Bitmap("Images/16x16/Gratuit.png", wx.BITMAP_TYPE_ANY))

            paddingImage = 3
            if heure_fin_x == 0 : 
                heure_fin_x = rectBarre.x + rectBarre.width
            xImage = heure_fin_x - paddingImage # heure_debut_x + heure_debut_largeur + paddingImage
            if rectBarre.width > len(listeImages) * 19 :
                for imageTemp in listeImages :
                    largeurBmp, hauteurBmp = imageTemp.GetSize()
                    gc.DrawBitmap(imageTemp, xImage - largeurBmp, rectBarre.y+1, largeurBmp, hauteurBmp)
                    xImage -= largeurBmp + paddingImage
            
            # Ecrit le nom du groupe
            if CTRL_Grille.AFFICHE_NOM_GROUPE == True and rectBarre.height > 22 :
                if conso.IDgroupe != None and conso.IDgroupe != 0 and conso.etat in ("reservation", "present", "absenti", "absentj", "attente", "refus") :
                    couleurTexteGroupe = UTILS_Couleurs.ModifierLuminosite(couleurBarre, -30)
                    gc.SetFont(wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'), couleurTexteGroupe)
                    nomGroupe = grid.dictGroupes[conso.IDgroupe]["nom"]
                    largeurNomGroupe, hauteurNomGroupe = gc.GetTextExtent(nomGroupe)
                    if rectBarre.width > largeurNomGroupe :
                        gc.DrawText(nomGroupe, rectBarre.x+4, rectBarre.y + rectBarre.height - 10)
                

        gc.PopState() 
        
        # Envoi du buffer au DC
        dcGrid.Blit(rect.x, rect.y, bmp.GetWidth(), bmp.GetHeight(), image, 0, 0)
        
    def DrawTexte(self, gc, rectBarre, texte="07h30", couleur=(0, 0, 0), position="gauche"):
        largeurTexte, hauteurTexte = gc.GetTextExtent(texte)
        if (largeurTexte*2.5) > rectBarre.width :
            return 0, 0, 0, 0
        gc.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL), couleur)
        if position == "gauche" : x = rectBarre.x + 3
        if position == "droite" : x = rectBarre.width + rectBarre.x - largeurTexte - 3
        y = rectBarre.y + 1
        gc.DrawText(texte, x, y)
        return x, y, largeurTexte, hauteurTexte

    def DrawBorder(self, grid, gc, rect):
        """
        Draw a standard border around the label, to give a simple 3D
        effect like the stock wx.grid.Grid labels do.
        """
        top = rect.top
        bottom = rect.bottom
        left = rect.left
        right = rect.right        
        gc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        gc.StrokeLine(right, top, right, bottom)
        gc.StrokeLine(left, top, left, bottom)
        gc.StrokeLine(left, bottom, right, bottom)
        gc.SetPen(wx.WHITE_PEN)
        gc.StrokeLine(left+1, top, left+1, bottom)
        gc.StrokeLine(left+1, top, right, top)

        
    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()

    def GetCouleurBarre(self, conso=None):
        """ Obtient la couleur à appliquer à la case """        
        # Si la case est sélectionnée
        if conso.etat in ("reservation", "present", "absenti", "absentj") :
            return CTRL_Grille.COULEUR_RESERVATION
        if conso.etat == "attente" : 
            return CTRL_Grille.COULEUR_ATTENTE
        if conso.etat == "refus" : 
            return CTRL_Grille.COULEUR_REFUS
    
    def GetCouleur(self, conso):
        return self.GetCouleurBarre(conso)

    
class LabelLigneStandard(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None, date=None):
        self._bgcolor = bgcolor
        self.date = date
        
    def Draw(self, grid, dc, rect, row):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

        # Indicateur date du jour
        if self.date == datetime.date.today() :
            dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0), wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawPolygon([(0, 0), (-7, 0), (0, 7)], xoffset=rect[2]-2, yoffset=rect[1]+1)
    
    def MAJ(self, couleur):
        self._bgcolor = couleur




class LabelLigneSeparation(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None, date=None):
        self._bgcolor = bgcolor
        self.date = date
        
    def Draw(self, grid, dc, rect, row):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        else:
            couleurSeparation = (255, 255, 255)
            dc.SetBrush(wx.Brush(couleurSeparation))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

        # Indicateur date du jour
        if self.date == datetime.date.today() :
            dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0), wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawPolygon([(0, 0), (-7, 0), (0, 7)], xoffset=rect[2]-2, yoffset=rect[1]+1)

    def MAJ(self, couleur):
        self._bgcolor = couleur




class LabelColonneStandard(glr.GridLabelRenderer):
    def __init__(self, typeColonne=None, bgcolor=None):
        self.typeColonne = typeColonne
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        if self.typeColonne == "unite" :
            text = wordwrap.wordwrap(text, CTRL_Grille.LARGEUR_COLONNE_UNITE, dc)
        if self.typeColonne == "unite" :
            DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)




class LabelColonneMultihoraires(glr.GridLabelRenderer):
    def __init__(self, heure_min=None, heure_max=None, couleurFond=None):
        self.heure_min = heure_min
        self.heure_max = heure_max
        self.couleurFond = couleurFond
        self.font = None
        
    def Draw(self, grid, dc, rect, col):
        # Couleur de fond
        if self.couleurFond != None :
            dc.SetBrush(wx.Brush(self.couleurFond))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        
        # Label
##        if self.font == None :
##            self.font = dc.GetFont()
##            dc.SetFont(self.font)
        dc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        hAlign, vAlign = grid.GetColLabelAlignment()
        texte = grid.GetColLabelValue(col)
        texte = wordwrap.wordwrap(texte, rect.width, dc)
        self.DrawBorder(grid, dc, rect)
        largTexte, hautTexte = dc.GetTextExtent(texte)
        x = rect.width / 2.0 - largTexte / 2.0 + rect.x
        dc.DrawText(texte, x, 2)
        
        # Graduations
        padding = PADDING_MULTIHORAIRES["horizontal"]
    
        graduationMin = UTILS_Dates.HeuresEnDecimal(self.heure_min)
        graduationMax = UTILS_Dates.HeuresEnDecimal(self.heure_max)
        graduationStep = 25
        hautTraitHeures = 4
        hautTraitDHeures = 2.5
        hautTraitQHeures = 1

        if graduationMax == 0 : graduationMax = 2400

        # Initialisation pour la graduation
        listeGraduations = range(graduationMin, graduationMax+graduationStep, graduationStep)
        nbreGraduations = len(listeGraduations)
        largeurDc = rect.width - padding * 2
        step = largeurDc / round(nbreGraduations-1, 1)
        
        # Création de la graduation
        j = k = etape = 0
        i = rect.x
        
        posY = rect.height - 17

        dc.SetPen(wx.Pen("black"))
        dc.SetTextForeground("black")
        dc.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        for etape in range(nbreGraduations):
            
            if k== 4 : k = 0
            if k == 1 or k == 3: hauteurTrait = hautTraitQHeures    # 1/4 d'heures
            if k == 2 : hauteurTrait = hautTraitDHeures    # Demi-Heures
            if k == 0 :
                hauteurTrait = hautTraitHeures
                texte = str(listeGraduations[j]/100)+"h"
                largTexte, hautTexte = dc.GetTextExtent(texte)
                # Dessin du texte
                if step >= 4.0 :
                    dc.DrawText(texte, i-(largTexte/2) + padding, posY+2)
            # Dessin du trait
            dc.DrawLine(i + padding, posY+hautTexte+hautTraitHeures-hauteurTrait, i + padding, posY+hautTexte+hautTraitHeures)
            i = i + step
            j = j + 1
            k = k + 1





if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=14, selectionIndividus=[46,])
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
