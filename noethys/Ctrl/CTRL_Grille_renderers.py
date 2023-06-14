#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activitï¿œs
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

import Chemins
from Utils import UTILS_Adaptations
import wx
from Ctrl import CTRL_Bouton_image
import wx.grid as gridlib
import wx.lib.wordwrap as wordwrap
##import Outils.gridlabelrenderer as glr
import wx.lib.mixins.gridlabelrenderer as glr
#from Ctrl import CTRL_Grille
CTRL_Grille = UTILS_Adaptations.Import("Ctrl.CTRL_Grille")
import datetime

if 'phoenix' in wx.PlatformInfo:
    from wx.grid import GridCellRenderer
else :
    from wx.grid import PyGridCellRenderer as GridCellRenderer

from Utils import UTILS_Dates
from Utils import UTILS_Couleurs
from Ctrl.CTRL_Saisie_transport import DICT_CATEGORIES as DICT_CATEGORIES_TRANSPORTS

PADDING_MULTIHORAIRES = {"vertical" : 5, "horizontal" : 10}



def TriTransports(dictTransports={}):
    """ Tri les transports en fonction de l'heure de dï¿œpart """
    listeID = []
    listeTemp = []
    for IDtransport, dictTransport in dictTransports.items() :
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






class CaseStandard(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.GetCouleur(), wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
            dc.DrawRectangleRect(rect)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        text = grid.GetCellValue(row, col)
        if self.case.ouvert == True :
            DrawBorder(grid, dc, rect)
        dc.DrawText(text, rect[0], rect[1])
        
        conso = self.case.conso

        # Affiche provisoirement l'IDfamille dans la case
        #dc.DrawText(str(self.case.IDfamille), rect[0]+4, rect[1] + 5)

        # Dessin du cadenas VERROUILLAGE
        if self.case.etat == None and self.case.verrouillage == 1 :
            dc.SetBrush(wx.Brush( (100, 100, 100), wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else :
                dc.DrawRectangleRect(rect)
            dc.SetBrush(wx.Brush(self.GetCouleur(), wx.SOLID))
        
        if self.case.verrouillage == 1 :
            tailleImage = 8
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, int(rect[0]+tailleImage-paddingImage), int(rect[1]+paddingImage))
        
        # Dessin de l'image PRESENT (Coche verte)
        if self.case.etat == "present" :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok5.png"), wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, int(rect[0]+rect[2]-tailleImage-paddingImage), int(rect[1]+paddingImage))
            
        # Dessin de l'image ABSENT JUSTIFIEE (Croix rouge)
        if self.case.etat == "absentj" :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absentj.png"), wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, int(rect[0]+rect[2]-tailleImage-paddingImage), int(rect[1]+paddingImage))
        
        # Dessin de l'image ABSENT INJUSTIFIEE (Croix rouge)
        if self.case.etat == "absenti" :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absenti.png"), wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, int(rect[0]+rect[2]-tailleImage-paddingImage), int(rect[1]+paddingImage))
            
        # Dessin de l'image SANS PRESTATION (Alerte)
        if self.case.etat in ("reservation", "present", "absenti", "absentj") and self.case.IDprestation == None and grid.afficheSansPrestation == True :
            tailleImage = 16
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gratuit.png"), wx.BITMAP_TYPE_ANY) 
            dc.DrawBitmap(bmp, int(rect[0]+paddingImage), int(rect[1]+paddingImage))

        # Dessin de l'image FORFAIT CREDIT
        if self.case.etat in ("reservation", "present", "absenti", "absentj") and self.case.IDprestation in list(self.grid.dictForfaits.keys()) :
            couleurForfait = self.grid.dictForfaits[self.case.IDprestation]["couleur"]
            dc.SetBrush(wx.Brush(couleurForfait, wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            #dc.DrawCircle(rect[0]+10, rect[1]+10, 4)
            dc.DrawPolygon([(0, 0), (7, 0), (0, 7)], xoffset=rect.x+2, yoffset=rect.y+1) # Version en haut ï¿œ gauche
##            dc.DrawPolygon([(0, 0), (-7, 0), (0, 7)], xoffset=rect.x+rect.width-1, yoffset=rect.y+1) # Version en haut ï¿œ droite
            
            
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

        # Ecrit la quantitï¿œ si c'est une conso QUANTITE
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
                if self.case.IDgroupe in self.grid.dictGroupes :
                    nomGroupe = self.grid.dictGroupes[self.case.IDgroupe]["nom"]
                    nbreGroupesActivite = self.grid.dictGroupes[self.case.IDgroupe]["nbreGroupesActivite"]
                else :
                    nomGroupe = u"Groupe inconnu"
                    nbreGroupesActivite = 999
                if nbreGroupesActivite > 1 :
                    dc.SetTextForeground("#949494")
                    dc.SetFont(wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
                    nomGroupe = self.AdapteTailleTexte(dc, nomGroupe, rect[2]-6)
                    largeurFinaleTexte = dc.GetTextExtent(nomGroupe)[0]
                    xTexte = rect[0] + ((rect[2] - largeurFinaleTexte) / 2.0)
                    dc.DrawText(nomGroupe, xTexte, rect.y + rect.height - 12)
                    dc.SetTextForeground("BLACK")
        
        # Ecrit les ï¿œtiquettes
        nbreEtiquettes = len(conso.etiquettes)
        if self.case.etat != None and nbreEtiquettes > 0 :
            largeurEtiquette = (rect.width - 3) / nbreEtiquettes * 1.0
            index = 0
            for IDetiquette in conso.etiquettes :
                if IDetiquette in self.grid.dictEtiquettes :
                    dictEtiquette = self.grid.dictEtiquettes[IDetiquette]
                    # Dessine l'ï¿œtiquette
                    dc.SetBrush(wx.Brush(dictEtiquette["couleur"], wx.SOLID))
                    dc.SetPen(wx.TRANSPARENT_PEN)
##                    dc.DrawRectangle(rect.x+2 + largeurEtiquette * index, rect.y + rect.height - 3, largeurEtiquette, 2) # Barre horizontale infï¿œrieure
                    dc.DrawCircle(rect.x + rect.width - 4 - (5 * index), rect.y + 4, 2) # En haut ï¿œ droite
                    index += 1
                
                
                
        
        
            
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
        """ Raccourcit le texte de l'intitulï¿œ en fonction de la taille donnï¿œe """
        # Pas de retouche nï¿œcessaire
        if dc.GetTextExtent(texte)[0] < tailleMaxi : return texte
        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= dc.GetTextExtent("W...")[0] : return "..."
        # Retouche nï¿œcessaire
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
        """ Obtient la couleur ï¿œ appliquer ï¿œ la case """        
        # Si fermï¿œe
        if self.case.ouvert == False : return CTRL_Grille.COULEUR_FERME
            
        # Si la case est sï¿œlectionnï¿œe
        if self.case.etat in ("reservation", "present", "absenti", "absentj") : return CTRL_Grille.COULEUR_RESERVATION
        if self.case.etat == "attente" : return CTRL_Grille.COULEUR_ATTENTE
        if self.case.etat == "refus" : return CTRL_Grille.COULEUR_REFUS
        
        # Si non sï¿œlectionnï¿œe
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
        





class CaseMemo(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush("WHITE", wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
            dc.DrawRectangleRect(rect)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        text = grid.GetCellValue(row, col)
        text = self.AdapteTailleTexte(dc, text, rect[2]-6)
        DrawBorder(grid, dc, rect)
        dc.SetTextForeground(wx.BLACK)
        if self.case.couleur:
            dc.SetTextForeground(self.case.couleur)
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
        """ Raccourcit le texte de l'intitulï¿œ en fonction de la taille donnï¿œe """
        # Pas de retouche nï¿œcessaire
        if dc.GetTextExtent(texte)[0] < tailleMaxi : return texte
        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= dc.GetTextExtent("W...")[0] : return "..."
        # Retouche nï¿œcessaire
        tailleTexte = dc.GetTextExtent(texte)[0]
        texteTemp = ""
        texteTemp2 = ""
        for lettre in texte :
            texteTemp += lettre
            if dc.GetTextExtent(texteTemp +"...")[0] < tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..." 






class CaseTransports(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.case.couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
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
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s.png" % DICT_CATEGORIES_TRANSPORTS[categorie]["image"]), wx.BITMAP_TYPE_ANY)
            dc.DrawBitmap(bmp, int(positionGauche), int(rect.top+padding))
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

    


class CaseActivite(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.case.couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
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


class CaseMultihoraires(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        # Prï¿œparation du buffer Image
        dcGrid = dc
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(rect.GetWidth(), rect.GetHeight())
        else :
            bmp = wx.EmptyBitmap(rect.GetWidth(), rect.GetHeight())
        image = wx.MemoryDC()
        image.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(image)
        gc.PushState() 
        
        rectCase = wx.Rect(0, 0, int(rect.GetWidth()), int(rect.GetHeight()))
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
                for IDunite_remplissage, valeurs in dictInfosPlaces.items() :
                    
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
                    
                    if nbrePlacesInitial > 0 and couleur != None :
                        gc.SetBrush(wx.Brush(couleur, wx.SOLID))
                        gc.SetPen(wx.TRANSPARENT_PEN)
                        posG = self.case.HeureEnPos(heure_min) 
                        posD = self.case.HeureEnPos(heure_max) - posG
                        gc.DrawRectangle(posG + PADDING_MULTIHORAIRES["horizontal"], 1, posD, rectCase.height-2)

                                     
            # Dessin des graduations
            gc.SetPen(wx.Pen((230, 230, 230), 1, wx.SOLID))

            try:
                nbre_quarts_heures = UTILS_Dates.SoustractionHeures(self.case.heure_max, self.case.heure_min).seconds / 900.0
                largeur = rect.width - PADDING_MULTIHORAIRES["horizontal"] * 2
                largeur_quarts_heures = largeur / nbre_quarts_heures
            except:
                largeur_quarts_heures = 99

            h = datetime.timedelta(minutes=0)
            for x in range(0, 96) :
                htime = UTILS_Dates.DeltaEnTime(h)
                if htime >= self.case.heure_min and htime <= self.case.heure_max :
                    x = self.case.HeureEnPos(h) + PADDING_MULTIHORAIRES["horizontal"]
                    if htime.minute == 0 or largeur_quarts_heures > 4:
                        gc.StrokeLine(x, 1, x, rect.height-2)
                h += datetime.timedelta(minutes=15)


        # Dessin des barres
        for barre in self.case.listeBarres :
            conso = barre.conso
            
            # Calcul des coordonnï¿œes de la barre
            barre.UpdateRect()
            rectBarre = barre.GetRect("case")

            # get Couleur barre
            couleurBarre = self.GetCouleurBarre(conso)
            
            # Dessin du cadre
            if 'phoenix' in wx.PlatformInfo:
                gc.SetFont(attr.GetFont(), wx.Colour(0, 0, 0))
            else:
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
                imageTemp = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY)
                largeurBmp, hauteurBmp = imageTemp.GetSize()
                gc.DrawBitmap(imageTemp, 2, rect.height-10, largeurBmp, hauteurBmp)

            # Dessin de l'image FORFAIT CREDIT
            if conso.etat in ("reservation", "present", "absenti", "absentj") and conso.IDprestation in list(grid.dictForfaits.keys()) :
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
                listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok5.png"), wx.BITMAP_TYPE_ANY))
                
            # Dessin de l'image ABSENT JUSTIFIEE (Croix rouge)
            if conso.etat == "absentj" :
                listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absentj.png"), wx.BITMAP_TYPE_ANY))
            
            # Dessin de l'image ABSENT INJUSTIFIEE (Croix rouge)
            if conso.etat == "absenti" :
                listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absenti.png"), wx.BITMAP_TYPE_ANY))
                
            # Dessin de l'image SANS PRESTATION (Alerte)
            if conso.etat in ("reservation", "present", "absenti", "absentj") and conso.IDprestation == None and grid.afficheSansPrestation == True :
                listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gratuit.png"), wx.BITMAP_TYPE_ANY))

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
                    nbreGroupesActivite = grid.dictGroupes[conso.IDgroupe]["nbreGroupesActivite"]
                    if rectBarre.width > largeurNomGroupe and nbreGroupesActivite > 1 :
                        gc.DrawText(nomGroupe, rectBarre.x+4, rectBarre.y + rectBarre.height - 10)
                
            # Ecrit les ï¿œtiquettes
            nbreEtiquettes = len(conso.etiquettes)
            if conso.etat != None and nbreEtiquettes > 0 :
                index = 0
                for IDetiquette in conso.etiquettes :
                    if IDetiquette in grid.dictEtiquettes :
                        dictEtiquette = grid.dictEtiquettes[IDetiquette]
                        # Dessine l'ï¿œtiquette
                        gc.SetBrush(wx.Brush(dictEtiquette["couleur"], wx.SOLID))
                        gc.SetPen(wx.TRANSPARENT_PEN)
                        gc.DrawEllipse(rectBarre.x + rectBarre.width - 7 - (5 * index), rectBarre.y + rectBarre.height - 7, 4, 4) # En haut ï¿œ droite
                        index += 1

        # Dessin du cadenas VERROUILLAGE
        if self.case.verrouillage == 1:
            gc.SetBrush(wx.Brush((100, 100, 100), wx.SOLID))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(*rectCase)
            tailleImage = 8
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY)
            largeurBmp, hauteurBmp = bmp.GetSize()
            gc.DrawBitmap(bmp, rectCase[0] + tailleImage - paddingImage, rectCase[1] + paddingImage, largeurBmp, hauteurBmp)

        gc.PopState() 
        
        # Envoi du buffer au DC
        dcGrid.Blit(rect.x, rect.y, rect.GetWidth(), rect.GetHeight(), image, 0, 0)
        
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
        """ Obtient la couleur ï¿œ appliquer ï¿œ la case """        
        # Si la case est sï¿œlectionnï¿œe
        if conso.etat in ("reservation", "present", "absenti", "absentj") :
            return CTRL_Grille.COULEUR_RESERVATION
        if conso.etat == "attente" : 
            return CTRL_Grille.COULEUR_ATTENTE
        if conso.etat == "refus" : 
            return CTRL_Grille.COULEUR_REFUS
        return wx.WHITE
    
    def GetCouleur(self, conso):
        return self.GetCouleurBarre(conso)




# -------------------------------------------------------------------------------------------

class CaseEvenement(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case
        self.dict_boutons = {}

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid

        # Prï¿œparation du buffer Image
        dcGrid = dc
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(rect.GetWidth(), rect.GetHeight())
        else :
            bmp = wx.EmptyBitmap(rect.GetWidth(), rect.GetHeight())
        image = wx.MemoryDC()
        image.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(image)
        gc.PushState()
        if 'phoenix' in wx.PlatformInfo:
            gc.SetFont(attr.GetFont(), wx.Colour(0, 0, 0))
        else :
            gc.SetFont(attr.GetFont())

        rectCase = wx.Rect(0, 0, int(rect.GetWidth()), int(rect.GetHeight()))
        x, y, largeur, hauteur = rectCase.x, rectCase.y, rectCase.width, rectCase.height

        if self.case.ouvert == True:
            self.couleurFond = self.grid.GetBackgroundColour() #CTRL_Grille.COULEUR_FERME
        else :
            self.couleurFond = CTRL_Grille.COULEUR_FERME
        gc.SetBrush(wx.Brush(self.couleurFond, wx.SOLID))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(x, y, largeur, hauteur)

        # Calcul de la largeur d'un bouton
        nbre_evenements = len(self.case.liste_evenements)
        marge = 2
        if len(self.case.liste_evenements) :
            largeur_bouton = (1.0 * (rectCase.width - marge -1) / nbre_evenements) - marge*2

        # Dessin de boutons
        self.dict_boutons = {}
        x = 1
        for evenement in self.case.liste_evenements :

            # Calcul de la taille du rectangle
            rectEvenement = wx.Rect(int(x + marge), int(rectCase.y + marge), int(largeur_bouton), int(rectCase.height - marge*2 -marge))

            # Dessin du rectangle
            couleur = evenement.GetCouleur()
            gc.SetBrush(wx.Brush(couleur, wx.SOLID))
            gc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
            gc.DrawRoundedRectangle(rectEvenement.x, rectEvenement.y, rectEvenement.width, rectEvenement.height, 5)

            # Dessin du nom de l'ï¿œvï¿œnement
            couleur_nom = wx.Colour(150, 150, 150)
            rect_texte = self.DrawTexte(gc, rectEvenement, evenement.nom, couleur=couleur_nom, position=(4, 2), font=wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

            # Dessin des horaires
            if evenement.heure_debut != None and evenement.heure_fin != None :
                heure_debut = UTILS_Dates.DatetimeTimeEnStr(evenement.heure_debut, "h")
                heure_fin = UTILS_Dates.DatetimeTimeEnStr(evenement.heure_fin, "h")
                if heure_debut != "00h00" and heure_fin != "00h00":
                    texte = u"%s - %s" % (heure_debut, heure_fin)
                    couleur_horaires = wx.Colour(200, 200, 200)
                    rect_texte = self.DrawTexte(gc, rectEvenement, texte, couleur=couleur_horaires, position=(4, rect_texte.height + 5), font=wx.Font(6, wx.SWISS, wx.NORMAL, wx.NORMAL))

            if evenement.conso != None :
                conso = evenement.conso

                # Dessin du cadenas VERROUILLAGE
                if conso.verrouillage == 1:
                    imageTemp = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY)
                    largeurBmp, hauteurBmp = imageTemp.GetSize()
                    gc.DrawBitmap(imageTemp, 2, rectEvenement.height - 10, largeurBmp, hauteurBmp)

                # Dessin de l'image FORFAIT CREDIT
                if conso.etat in ("reservation", "present", "absenti", "absentj") and conso.IDprestation in list(grid.dictForfaits.keys()):
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
                if conso.etat == "present":
                    listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok5.png"), wx.BITMAP_TYPE_ANY))

                # Dessin de l'image ABSENT JUSTIFIEE (Croix rouge)
                if conso.etat == "absentj":
                    listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absentj.png"), wx.BITMAP_TYPE_ANY))

                # Dessin de l'image ABSENT INJUSTIFIEE (Croix rouge)
                if conso.etat == "absenti":
                    listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absenti.png"), wx.BITMAP_TYPE_ANY))

                # Dessin de l'image SANS PRESTATION (Alerte)
                if conso.etat in ("reservation", "present", "absenti", "absentj") and conso.IDprestation == None and grid.afficheSansPrestation == True:
                    listeImages.append(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gratuit.png"), wx.BITMAP_TYPE_ANY))

                paddingImage = 3
                xImage = rectEvenement.x + rectEvenement.width - paddingImage
                if rectEvenement.height > 12 and rectEvenement.width > len(listeImages) * 19:
                    for imageTemp in listeImages:
                        largeurBmp, hauteurBmp = imageTemp.GetSize()
                        gc.DrawBitmap(imageTemp, xImage - largeurBmp, rectEvenement.y + 1, largeurBmp, hauteurBmp)
                        xImage -= largeurBmp + paddingImage

                # Ecrit les ï¿œtiquettes
                nbreEtiquettes = len(conso.etiquettes)
                if conso.etat != None and nbreEtiquettes > 0:
                    index = 0
                    for IDetiquette in conso.etiquettes:
                        if IDetiquette in grid.dictEtiquettes:
                            dictEtiquette = grid.dictEtiquettes[IDetiquette]
                            # Dessine l'ï¿œtiquette
                            gc.SetBrush(wx.Brush(dictEtiquette["couleur"], wx.SOLID))
                            gc.SetPen(wx.TRANSPARENT_PEN)
                            if rectEvenement.height > 10 and (len(listeImages) == 0 or rectEvenement.height > 25) :
                                gc.DrawEllipse(rectEvenement.x + rectEvenement.width - 7 - (5 * index), rectEvenement.y + rectEvenement.height - 7, 4, 4)  # En haut ï¿œ droite
                            index += 1

            # Mï¿œmorisation des coordonnï¿œes du bouton
            self.dict_boutons[evenement] = rectEvenement

            # Calcul de la position x suivante
            x += rectEvenement.width + marge*2

        # Dessin du cadenas VERROUILLAGE
        if self.case.verrouillage == 1:
            gc.SetBrush(wx.Brush((100, 100, 100), wx.SOLID))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(*rectCase)
            tailleImage = 8
            paddingImage = 3
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY)
            largeurBmp, hauteurBmp = bmp.GetSize()
            gc.DrawBitmap(bmp, rectCase[0] + tailleImage - paddingImage, rectCase[1] + paddingImage, largeurBmp, hauteurBmp)

        gc.PopState()

        # Envoi du buffer au DC
        dcGrid.Blit(rect.x, rect.y, rect.GetWidth(), rect.GetHeight(), image, 0, 0)

    def DrawTexte(self, gc, rect, texte="Texte", couleur=wx.Colour(0, 0, 0), position=(0, 0), font=None):
        # Ajuste la font
        if font == None :
            font = wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL)
        gc.SetFont(font, couleur)

        # Calcul la largeur du texte
        largeurTexte, hauteurTexte = gc.GetTextExtent(texte)

        # Raccourci le texte si besoin
        if largeurTexte > (rect.width - position[0] -2) :
            texte = wordwrap.wordwrap(texte, rect.width-10, gc).split("\n")[0] + "..."
            largeurTexte, hauteurTexte = gc.GetTextExtent(texte)

        # Calcul le rect du texte
        rect_texte = wx.Rect(int(rect.x + position[0]), int(rect.y + position[1]), int(largeurTexte), int(hauteurTexte))

        # Dessin du texte
        if 'phoenix' in wx.PlatformInfo:
            if rect.Contains(rect_texte):
                gc.DrawText(texte, rect_texte.x, rect_texte.y)
        else :
            if rect.ContainsRect(rect_texte):
                gc.DrawText(texte, rect_texte.x, rect_texte.y)

        return rect_texte

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()

















# -------------------------------------------------------------------------------------------
class LabelLigneStandard(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None, date=None, ligne=None):
        self.couleurFond = bgcolor
        self.couleurInitiale = bgcolor
        self.rect = None
        self.date = date
        self.ligne = ligne
        
    def Draw(self, grid, dc, rect, row):
        self.rect = rect
        self.grid = grid
        if self.couleurFond != None :
            dc.SetBrush(wx.Brush(self.couleurFond))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else :
                dc.DrawRectangleRect(rect)
##        self.couleurFond = dc.GetBackground().GetColour() 
        DrawBorder(grid, dc, rect)

        dc.SetTextForeground(wx.BLACK)
        if self.ligne.coche == True :
            dc.SetTextForeground(wx.RED)

        texte = grid.GetRowLabelValue(row)
        # hAlign, vAlign = grid.GetRowLabelAlignment()
        # self.DrawText(grid, dc, rect, texte, hAlign, vAlign)

        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        tailleTexte = dc.GetTextExtent(texte)
        x = rect.x + rect.width/2.0 - tailleTexte[0]/2.0
        y = rect.y + rect.height/2.0 - tailleTexte[1]/2.0
        dc.DrawText(texte, x, y)

        # Indicateur date du jour
        if self.date == datetime.date.today() :
            dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0), wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawPolygon([(0, 0), (-7, 0), (0, 7)], xoffset=rect[2]-2, yoffset=rect[1]+1)

        # Coche
        # if self.ligne.coche == True :
        #     tailleImage = 16
        #     bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY)
        #     dc.DrawBitmap(bmp, rect.x +3, rect.y + rect.height/2.0 - tailleImage/2.0)

    
    def MAJ(self, couleur):
        self.couleurFond = couleur
        self.MAJCase() #self.grid.Refresh()

    def MAJCase(self):
        rect = wx.Rect()
        rect.width = self.grid.GetRowLabelSize()
        rect.height = self.grid.GetRowSize(self.ligne.numLigne)
        rect.x = self.grid.GetGridRowLabelWindow().GetPosition()[0]
        rect.y = self.grid.CellToRect(self.ligne.numLigne, 1).y
        # Adaptation au scrolling
        xView, yView = self.grid.GetViewStart()
        xDelta, yDelta = self.grid.GetScrollPixelsPerUnit()
        if 'phoenix' in wx.PlatformInfo:
            rect.Offset(0,-(yView*yDelta))
        else :
            rect.OffsetXY(0,-(yView*yDelta))
        self.grid.GetGridRowLabelWindow().RefreshRect(rect)

    def Flash(self, couleur=None):
        self.MAJ(couleur)
        wx.CallLater(1000, self.MAJ, self.couleurInitiale)



class LabelLigneSeparation(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None, date=None):
        self._bgcolor = bgcolor
        self.date = date
        
    def Draw(self, grid, dc, rect, row):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else :
                dc.DrawRectangleRect(rect)
        else:
            couleurSeparation = (255, 255, 255)
            dc.SetBrush(wx.Brush(couleurSeparation))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else :
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
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else :
                dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        if self.typeColonne == "unite" :
            text = wordwrap.wordwrap(text, rect.width, dc)
        if self.typeColonne == "unite" :
            DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)



class LabelColonneMultihoraires(glr.GridLabelRenderer):
    def __init__(self, heure_min=None, heure_max=None, couleurFond=None):
        self.heure_min = heure_min
        self.heure_max = heure_max
        self.couleurFond = couleurFond
        self.font = None

    def HeureEnPos(self, heure, rect):
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.heure_max, self.heure_min)
        return 1.0 * UTILS_Dates.SoustractionHeures(heure, self.heure_min).seconds / tempsAffichable.seconds * self.GetLargeurMax(rect)

    def GetLargeurMax(self, rect=None):
        return rect.GetWidth() - PADDING_MULTIHORAIRES["horizontal"] * 2

    def Draw(self, grid, dc, rect, col):
        # Couleur de fond
        if self.couleurFond != None :
            dc.SetBrush(wx.Brush(self.couleurFond))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else :
                dc.DrawRectangleRect(rect)
        
        # Label
        dc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        hAlign, vAlign = grid.GetColLabelAlignment()
        texte = grid.GetColLabelValue(col)
        texte = wordwrap.wordwrap(texte, rect.width, dc).split("\n")[0]
        self.DrawBorder(grid, dc, rect)
        largTexte, hautTexte = dc.GetTextExtent(texte)
        x = rect.width / 2.0 - largTexte / 2.0 + rect.x
        dc.DrawText(texte, x, 2)
        
        # Graduations
        dc.SetPen(wx.Pen("black"))
        dc.SetTextForeground("black")
        dc.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))

        try :
            nbre_quarts_heures = UTILS_Dates.SoustractionHeures(self.heure_max, self.heure_min).seconds / 900.0
            largeur = rect.width - PADDING_MULTIHORAIRES["horizontal"] * 2
            largeur_quarts_heures = largeur / nbre_quarts_heures
        except:
            largeur_quarts_heures = 99

        h = datetime.timedelta(minutes=0)
        chiffre_pair = 0
        for x in range(0, 96) :
            htime = UTILS_Dates.DeltaEnTime(h)
            if htime >= self.heure_min and htime <= self.heure_max :
                x = self.HeureEnPos(h, rect) + PADDING_MULTIHORAIRES["horizontal"]
                posY = rect.height - 17
                hautTraitHeures = 4
                hauteurTrait = None
                if htime.minute == 0 :
                    hauteurTrait = hautTraitHeures
                    texte = "%dh" % htime.hour
                    largTexte, hautTexte = dc.GetTextExtent(texte)
                    affiche_heure = False
                    if largeur_quarts_heures > 4:
                        affiche_heure = True
                    if largeur_quarts_heures > 2 and largeur_quarts_heures < 4 and chiffre_pair % 2 == 0:
                        affiche_heure = True
                    if largeur_quarts_heures > 1 and largeur_quarts_heures < 2 and chiffre_pair % 3 == 0:
                        affiche_heure = True
                    if affiche_heure == True :
                        dc.DrawText(texte, x-(largTexte/2)+rect.x , posY+2)
                    chiffre_pair += 1
                elif htime.minute in (15, 45) and largeur_quarts_heures > 4 :
                    hauteurTrait = 1
                elif htime.minute == 30 and largeur_quarts_heures > 4 :
                    hauteurTrait = 2.5
                if hauteurTrait != None :
                    dc.DrawLine(x+rect.x, posY+hautTexte+hautTraitHeures-hauteurTrait, x+rect.x, posY+hautTexte+hautTraitHeures)

            h += datetime.timedelta(minutes=15)









if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    from Dlg import DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=1, selectionIndividus=[2,])
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
