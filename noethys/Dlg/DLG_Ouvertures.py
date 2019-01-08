#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import sys
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import datetime
import calendar
import traceback
import copy
import GestionDB
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Dates
from Utils import UTILS_Parametres
import wx.lib.agw.supertooltip as STT

if 'phoenix' in wx.PlatformInfo:
    from wx.grid import GridCellRenderer
    CURSOR = wx.Cursor
else :
    from wx.grid import PyGridCellRenderer as GridCellRenderer
    CURSOR = wx.StockCursor

from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES



class Track():
    def __init__(self):
        self.liste_variables = []
        self.champ_cle = ""
        self.dirty = False

    def Importer_variables(self, dictDonnees, liste_variables):
        for attribut in liste_variables:
            if dictDonnees.has_key(attribut):
                valeur = dictDonnees[attribut]
            else:
                valeur = None
            setattr(self, attribut, valeur)

    def GetValeurCle(self):
        return getattr(self, self.champ_cle)

    def GetVariables(self, avecCle=False):
        return [variable for variable in self.liste_variables if variable != self.champ_cle or avecCle == True]

    def Get_variables_pour_db(self):
        return [getattr(self, variable) for variable in self.GetVariables()]

    def Get_champs_pour_db(self):
        return ", ".join(self.GetVariables())

    def Get_interrogations_pour_db(self):
        return ", ".join(["?" for variable in self.GetVariables()])

    def Get_interrogations_et_variables_pour_db(self):
        return ", ".join(["%s=?" % variable for variable in self.GetVariables()])

    def Get_listedonnees_pour_db(self):
        return [(variable, getattr(self, variable)) for variable in self.GetVariables()]

    def MAJ(self, donnees=None):
        # Si on reçoit un dict
        if type(donnees) == dict :
            for key, valeur in donnees.iteritems() :
                setattr(self, key, valeur)
        # Si on reçoit une liste
        if type(donnees) == list :
            for key, valeur in donnees :
                setattr(self, key, valeur)



# --------------------------------------------------------------------------------------

class Track_ligne(Track):
    def __init__(self, dictDonnees={}):
        Track.__init__(self)
        self.liste_variables = CHAMPS_TABLE_LIGNES
        self.champ_cle = "IDligne"
        self.nom_table = "tarifs_lignes"
        self.Importer_variables(dictDonnees, self.liste_variables)

    def GetLigne(self):
        listeLignes = []
        for variable in self.liste_variables :
            listeLignes.append(getattr(self, variable))
        return listeLignes

# --------------------------------------------------------------------------------------

class Track_filtre(Track):
    def __init__(self, dictDonnees={}):
        Track.__init__(self)
        self.liste_variables = ["IDfiltre", "IDquestion", "categorie", "choix", "criteres", "IDtarif"]
        self.champ_cle = "IDfiltre"
        self.nom_table = "questionnaire_filtres"
        self.Importer_variables(dictDonnees, self.liste_variables)

    def GetFiltre(self):
        listeFiltres = []
        for variable in self.liste_variables:
            listeFiltres.append(getattr(self, variable))
        return listeFiltres


# --------------------------------------------------------------------------------------

class Track_tarif(Track):
    def __init__(self, dictDonnees={}):
        Track.__init__(self)
        self.liste_variables = ["IDtarif", "IDactivite", "date_debut", "date_fin", "methode", "type", "categories_tarifs", "groupes",
                           "etiquettes", "cotisations", "caisses", "description", "jours_scolaires",
                           "jours_vacances", "observations", "tva", "code_compta", "IDtype_quotient",
                           "label_prestation", "IDevenement", "IDproduit", "IDnom_tarif", "options",
                            "forfait_saisie_manuelle", "forfait_saisie_auto", "forfait_suppression_auto",
                            "etats",]
        self.Importer_variables(dictDonnees, self.liste_variables)
        self.champ_cle = "IDtarif"
        self.nom_table = "tarifs"

        # Autres données
        self.filtres = []
        if dictDonnees.has_key("filtres"):
            for dictFiltre in dictDonnees["filtres"] :
                self.filtres.append(Track_filtre(dictFiltre))

        self.lignes = []
        if dictDonnees.has_key("lignes"):
            for dictLigne in dictDonnees["lignes"] :
                self.lignes.append(Track_ligne(dictLigne))


    def GetDictTarif(self):
        dictTarif = {}
        for variable in self.liste_variables :
            dictTarif[variable] = getattr(self, variable)
        return dictTarif

    def GetFiltres(self):
        listeFiltres = []
        for filtre in self.filtres:
            listeFiltres.append(filtre.GetFiltre())
        return listeFiltres

    def SetFiltres(self, listeDonnees=[]):
        self.filtres = []
        for ligne in listeDonnees :
            dictDonnees = {}
            for key, valeur in ligne:
                dictDonnees[key] = valeur
            track_filtre = Track_filtre(dictDonnees)
            track_filtre.dirty = True
            self.filtres.append(track_filtre)

    def GetLignes(self):
        liste_lignes = []
        for track_ligne in self.lignes :
            liste_lignes.append(track_ligne.GetLigne())
        return liste_lignes

    def SetLignes(self, listeDonnees=[]):
        self.lignes = []
        for ligne in listeDonnees :
            dictDonnees = {}
            for key, valeur in ligne:
                dictDonnees[key] = valeur
            track_ligne = Track_ligne(dictDonnees)
            track_ligne.dirty = True
            self.lignes.append(track_ligne)


# --------------------------------------------------------------------------------------

class Track_evenement(Track):
    def __init__(self, dictDonnees={}):
        Track.__init__(self)
        self.liste_variables = ["IDevenement", "IDactivite", "IDunite", "IDgroupe", "date", "nom",
                           "description", "capacite_max", "heure_debut", "heure_fin", "montant"]
        self.Importer_variables(dictDonnees, self.liste_variables)
        self.champ_cle = "IDevenement"
        self.nom_table = "evenements"

        # Stockage des tarifs au format track
        self.tarifs = []
        for dictTarif in dictDonnees["tarifs"] :
            self.tarifs.append(Track_tarif(dictTarif))

    def Reinit(self, date=None, IDunite=None, IDgroupe=None):
        """ Réinitialise l'évènement, les tarifs, lignes, filtres avec une nouvelle date (sert pour le copier/coller) """
        # Evènement
        self.IDevenement = None
        self.date = date
        if IDunite != None :
            self.IDunite = IDunite
        if IDgroupe != None :
            self.IDgroupe = IDgroupe

        # Tarifs
        for track_tarif in self.tarifs :
            track_tarif.IDtarif = None
            track_tarif.date_debut = date
            track_tarif.date_fin = date

            # Lignes
            for track_ligne in track_tarif.lignes :
                track_ligne.IDligne = None

            # Filtres
            for track_filtre in track_tarif.filtres :
                track_filtre.IDfiltre = None







COULEUR_DATE = "#C0C0C0"
COULEUR_OUVERTURE = "#FFE900" #(0, 230, 0)
COULEUR_FERMETURE = "#8EA0AA" #"#F7ACB2"
COULEUR_VACANCES = "#F3FD89"
COULEUR_FERIE = "#828282"


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def CreationImage(largeur, hauteur, couleur=None):
    """ couleur peut être RGB ou HEXA """
    if type(couleur) == str : r, v, b = hex_to_rgb(couleur)
    if type(couleur) == tuple : r, v, b = couleur
    if 'phoenix' in wx.PlatformInfo:
        bmp = wx.Image(largeur, hauteur, True)
        bmp.SetRGB((0, 0, largeur, hauteur), r, v, b)
    else :
        bmp = wx.EmptyImage(largeur, hauteur, True)
        bmp.SetRGBRect((0, 0, largeur, hauteur), r, v, b)
    return bmp.ConvertToBitmap()

def DrawBorder(grid, dc, rect):
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









class CaseOuverture():
    def __init__(self, grid=None, numLigne=None, numColonne=None, typeCase="ouverture", date=None, typeUnite="", actif=False, IDgroupe=None, nomGroupe=None, IDunite=None, nbre_conso=0, liste_evenements=[]):
        self.grid = grid
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.date = date
        self.typeUnite = typeUnite
        self.typeCase = typeCase
        self.IDgroupe = IDgroupe
        self.nomGroupe = nomGroupe
        self.IDunite = IDunite
        self.actif = actif
        self.nbre_conso = nbre_conso
        self.liste_evenements = liste_evenements
        self.survol = False
        self.survolEvenement = False

        # Dessin de la case
        self.renderer = CaseOuvertureRenderer(self)
        self.grid.SetCellValue(self.numLigne, self.numColonne, u"")
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

    def GetRect(self):
        return self.grid.CellToRect(self.numLigne, self.numColonne)

    def Refresh(self):
        rect = self.GetRect()
        x, y = self.grid.CalcScrolledPosition(rect.GetX(), rect.GetY())
        rect = wx.Rect(x, y, rect.GetWidth(), rect.GetHeight())
        self.grid.GetGridWindow().Refresh(False, rect)

    def GetCoordsBoutonEvenements(self):
        return self.renderer.coordsBoutonEvenements

    def SetSurvol(self, x=None, y=None, etat=False):
        etat = False
        survolEvenement = False

        # Vérifie si case survolée
        if x != None and y != None :
            numLigne, numColonne = self.grid.YToRow(y), self.grid.XToCol(x)
            if numLigne == self.numLigne and numColonne == self.numColonne :
                etat = True

            # Vérifie si bouton Evènement survolé
            rect = self.renderer.coordsBoutonEvenements
            if rect != None :
                if 'phoenix' in wx.PlatformInfo:
                    contains = rect.Contains(x, y)
                else:
                    contains = rect.ContainsXY(x, y)
                if contains == True :
                    survolEvenement = True

        if self.survol != etat or self.survolEvenement != survolEvenement :
            self.survol = etat
            self.survolEvenement = survolEvenement
            self.Refresh()

        return etat

    def GetTexteInfobulle(self):
        if self.ouvert == False :
            pied = _(u"Cliquez pour ouvrir cette unité")
            texte = _(u"Cette unité est fermée.\n")
        else :
            texte = _(u"Cette unité est ouverte.\n")
            pied = _(u"Cliquez pour fermer cette unité")

            # Conso associées
            if self.nbre_conso > 0 :
                texte += _(u"Vous ne pouvez pas la fermer car %d consommations y ont déjà été associées\n") % self.nbre_conso

            # Evènements
            if self.typeUnite == "Evenement" :
                if len(self.liste_evenements) > 0 :
                    texte += _(u"\nEvènements associés :\n")
                    for track in self.liste_evenements :
                        texte += u"  - %s\n" % track.nom
                else :
                    texte += _(u"\nAucun évènement associé.\n\nCliquez sur le + pour ajouter des évènements.")

        # Titre
        if self.date == datetime.date(2998, 12, 1) :
            label_date = _(u"Modèle de schéma")
        else :
            label_date = DateComplete(self.date)

        try :
            couleur = self.renderer.GetCouleur()
        except :
            couleur = wx.Colour(255, 255, 255)

        dictDonnees = {
            "couleur" : couleur,
            "titre" : u"%s - %s" % (label_date, self.nomGroupe),
            "texte" : texte + "\n",
            "pied" : pied,
            }
        return dictDonnees



class CaseOuvertureRenderer(GridCellRenderer):
    def __init__(self, case=None):
        GridCellRenderer.__init__(self)
        self.case = case
        self.grid = None
        self.coordsBoutonEvenements = None

    def GetCouleur(self):
        if self.case.actif == False :
            return COULEUR_DATE
        if self.case.ouvert == True :
            return COULEUR_OUVERTURE
        if self.case.ouvert == False :
            return COULEUR_FERMETURE

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid

        # Dessine le fond
        couleur_fond = self.GetCouleur()
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(couleur_fond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else:
            dc.DrawRectangleRect(rect)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())

        # Ecrit le nombre de conso
        if self.case.nbre_conso > 0 :
            dc.SetTextForeground(wx.Colour(100, 100, 100))
            dc.SetFont(wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            quantite = str(self.case.nbre_conso)
            dc.DrawText(quantite, rect[0] + 5, rect[1] + 2)

        # Dessine les évènements
        if self.case.typeUnite == "Evenement" and self.case.ouvert == True :
            taille = (20, 16)
            x = rect.x + rect.width -2 - taille[0]
            y = rect.y + 2
            if len(self.case.liste_evenements) > 0 :
                texte = str(len(self.case.liste_evenements))
            else :
                texte = "+"

            if self.case.survol == True and self.case.survolEvenement == True :
                if len(self.case.liste_evenements) > 0 :
                    couleur_texte = wx.RED
                    couleur_rond = wx.WHITE
                else :
                    couleur_texte = wx.WHITE
                    couleur_rond = wx.RED
            else :
                if len(self.case.liste_evenements) > 0:
                    couleur_texte = wx.WHITE
                    couleur_rond = wx.RED
                else :
                    couleur_texte = couleur_fond
                    couleur_rond = wx.WHITE

            image = self.GetImageEvement(texte=texte, taille=taille, couleur_texte=couleur_texte, couleur_fond=couleur_fond, couleur_rond=couleur_rond)
            dc.DrawBitmap(image, x, y)

            self.coordsBoutonEvenements = wx.Rect(x, y, taille[0], taille[1])

        else :
            self.coordsBoutonEvenements = None

    def GetImageEvement(self, texte="", taille=(16, 16), couleur_texte=wx.BLACK, couleur_fond=wx.Colour(0, 0, 0), couleur_rond=wx.RED, alignement="droite-bas", padding=0, taille_police=9):
        """ Ajoute un texte sur une image bitmap """
        # Création du bitmap
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(taille[0], taille[1])
        else :
            bmp = wx.EmptyBitmap(taille[0], taille[1])
        mdc = wx.MemoryDC(bmp)
        dc = wx.GCDC(mdc)
        mdc.SetBackground(wx.Brush(couleur_fond))
        mdc.Clear()

        # Paramètres
        dc.SetBrush(wx.Brush(couleur_rond))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        dc.SetTextForeground(couleur_texte)

        # Calculs
        largeurTexte, hauteurTexte = dc.GetTextExtent(texte)

        # Rond rouge
        hauteurRond = hauteurTexte + padding * 2
        largeurRond = largeurTexte + padding * 2 + hauteurRond / 2.0
        if largeurRond < hauteurRond:
            largeurRond = hauteurRond

        if "gauche" in alignement: xRond = 1
        if "droite" in alignement: xRond = taille[0] - largeurRond - 1
        if "haut" in alignement: yRond = 1
        if "bas" in alignement: yRond = taille[1] - hauteurRond - 1

        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRoundedRectangle(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)
        else :
            dc.DrawRoundedRectangle(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)

        # Texte
        xTexte = xRond + largeurRond / 2.0 - largeurTexte / 2.0
        yTexte = yRond + hauteurRond / 2.0 - hauteurTexte / 2.0 - 1
        dc.DrawText(texte, xTexte, yTexte)

        mdc.SelectObject(wx.NullBitmap)
        bmp.SetMaskColour("black")
        return bmp




    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()




# ----------------------------------------------------------------------------------------------------------------------

class MyRowLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, row):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
            dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
            dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)



class Calendrier(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent, IDactivite=None):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.parent = parent
        self.moveTo = None
        self.IDactivite = IDactivite
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(180)
        self.DisableDragColSize()
        self.DisableDragRowSize()
        
        self.dictOuvertures = {}
        self.dictRemplissage = {}
        self.dictConso = {}
        self.dict_donnees_initiales = {"ouvertures" : [], "evenements" : [], "tarifs" : [], "questionnaire_filtres" : [], "tarifs_lignes" : []}

        DB = GestionDB.DB()
        self.listeVacances = self.GetListeVacances(DB)
        self.listeFeries = self.GetListeFeries(DB)
        self.datesValiditeActivite = self.GetValiditeActivite(DB)
        self.dictUnitesGroupes = self.GetDictUnitesGroupes(DB)
        DB.Close()

        self.clipboard = None # Date à copier pour  la fonction copier-coller
        self.annee = None
        self.mois = None
        self.afficherTousGroupes = None

        # Init Tooltip
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip après 10 secs

        self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        self.caseSurvolee = None

        self.GetGridWindow().Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseOver)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.OnCellLeftClick)
        #self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        if 'phoenix' in wx.PlatformInfo:
            self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        else :
            self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
    
    def Sauvegarde(self):
        # ---- Nouvelle version optimisée ----

        DB = GestionDB.DB()
        
        # Ouvertures
        listeAjoutsOuvertures = []
        listeSuppressionsOuvertures = []
        listeFinaleEvenements = []

        for dateDD, dictGroupes in self.dictOuvertures.iteritems() :
            for IDgroupe, dictUnites in dictGroupes.iteritems() :
                for IDunite, dictValeurs in dictUnites.iteritems() :
                    etat = dictValeurs["etat"]
                    initial = dictValeurs["initial"]
                    IDouverture = dictValeurs["IDouverture"]
                    liste_evenements = dictValeurs["liste_evenements"]

                    # Ouverture
                    if etat != initial :
                        # Si la valeur a été modifiée :
                        if IDouverture == None and etat == True :
                            listeAjoutsOuvertures.append((self.IDactivite, IDunite, IDgroupe, str(dateDD)))
                        elif IDouverture != None and etat == False :
                            listeSuppressionsOuvertures.append(IDouverture)
                        else:
                            pass

                    # Evenements
                    for track_evenement in liste_evenements :
                        if etat == True :
                            if track_evenement.IDevenement == None :
                                listeFinaleEvenements.append(("ajout", track_evenement))
                            else :
                                listeFinaleEvenements.append(("modification", track_evenement))

        # Ajouts ouverture
        if len(listeAjoutsOuvertures) > 0 :
            DB.Executermany("INSERT INTO ouvertures (IDactivite, IDunite, IDgroupe, date) VALUES (?, ?, ?, ?)", listeAjoutsOuvertures, commit=False)
        # Suppression ouverture
        if len(listeSuppressionsOuvertures) > 0 :
            if len(listeSuppressionsOuvertures) == 1 :
                conditionSuppression = "(%d)" % listeSuppressionsOuvertures[0]
            else : 
                conditionSuppression = str(tuple(listeSuppressionsOuvertures))
            DB.ExecuterReq("DELETE FROM ouvertures WHERE IDouverture IN %s" % conditionSuppression)
        # Confirmation
        DB.Commit()

        # Récupération des prochains ID
        prochainIDevenement = DB.GetProchainID("evenements")
        prochainIDtarif = DB.GetProchainID("tarifs")

        # Pour contrer bug sur table tarifs_lignes
        if DB.isNetwork == False:
            req = """SELECT max(IDligne) FROM tarifs_lignes;"""
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if listeTemp[0][0] == None:
                prochainIDligne = 1
            else:
                prochainIDligne = listeTemp[0][0] + 1


        # ------------- Evenements ---------------
        dict_suppressions = {
            "evenements" : {"champ_cle" : "IDevenement", "listeID" : []},
            "tarifs" : {"champ_cle" : "IDtarif", "listeID" : []},
            "questionnaire_filtres" : {"champ_cle" : "IDfiltre", "listeID" : []},
            "tarifs_lignes" : {"champ_cle" : "IDligne", "listeID" : []},
            }

        dict_requetes = {
            "evenements": {"ajout" : [], "modification" : []},
            "tarifs": {"ajout" : [], "modification" : []},
            "questionnaire_filtres": {"ajout" : [], "modification" : []},
            "tarifs_lignes": {"ajout" : [], "modification" : []},
            }

        for mode, track_evenement in listeFinaleEvenements :
            dict_suppressions["evenements"]["listeID"].append(track_evenement.IDevenement)

            # Ajout
            if mode == "ajout" :
                track_evenement.MAJ({"IDevenement" : int(prochainIDevenement)})
                prochainIDevenement += 1
                dict_requetes[track_evenement.nom_table]["ajout"].append(track_evenement)
                #print "ajouter", track_evenement, "avec ID", track_evenement.IDevenement

            # Modification
            if mode == "modification" :
                if track_evenement.dirty == True:
                    dict_requetes[track_evenement.nom_table]["modification"].append(track_evenement)
                    #print "modifier", track_evenement

            # ---------------- Tarifs --------------------
            for track_tarif in track_evenement.tarifs :
                dict_suppressions["tarifs"]["listeID"].append(track_tarif.IDtarif)

                # Ajout
                if track_tarif.IDtarif == None :
                    track_tarif.MAJ({"IDevenement": track_evenement.IDevenement, "IDtarif" : int(prochainIDtarif)})
                    prochainIDtarif += 1
                    dict_requetes[track_tarif.nom_table]["ajout"].append(track_tarif)
                    #print "ajouter", track_tarif, "avec ID", track_tarif.IDtarif

                # Modification
                else :
                    if track_tarif.dirty == True:
                        dict_requetes[track_tarif.nom_table]["modification"].append(track_tarif)
                        #print "modifier", track_tarif

                # ---------------- Lignes --------------------
                for track_ligne in track_tarif.lignes :
                    dict_suppressions["tarifs_lignes"]["listeID"].append(track_ligne.IDligne)

                    # Ajout
                    if track_ligne.IDligne == None:
                        track_ligne.MAJ({"IDtarif" : track_tarif.IDtarif})
                        if DB.isNetwork == False:
                            track_ligne.MAJ({"IDligne": int(prochainIDligne)})
                            prochainIDligne += 1
                        dict_requetes[track_ligne.nom_table]["ajout"].append(track_ligne)
                        #print "ajouter", track_ligne

                    # Modification
                    else:
                        if track_ligne.dirty == True:
                            track_ligne.MAJ({"IDtarif": track_tarif.IDtarif})
                            dict_requetes[track_ligne.nom_table]["modification"].append(track_ligne)
                            #print "modifier", track_ligne

                # ---------------- Filtres --------------------
                for track_filtre in track_tarif.filtres :
                    dict_suppressions["questionnaire_filtres"]["listeID"].append(track_filtre.IDfiltre)

                    # Ajout
                    if track_filtre.IDfiltre == None:
                        track_filtre.MAJ({"IDtarif" : track_tarif.IDtarif})
                        dict_requetes[track_filtre.nom_table]["ajout"].append(track_filtre)
                        #print "ajouter", track_filtre

                    # Modification
                    else:
                        if track_filtre.dirty == True:
                            track_filtre.MAJ({"IDtarif": track_tarif.IDtarif})
                            dict_requetes[track_filtre.nom_table]["modification"].append(track_filtre)
                            #print "modifier", track_filtre

        for nom_table in ("evenements", "tarifs", "questionnaire_filtres", "tarifs_lignes") :

            # Ajout
            if len(dict_requetes[nom_table]["ajout"]) > 0 :
                listeDonnees = []
                for track in dict_requetes[nom_table]["ajout"] :
                    ligne = track.Get_variables_pour_db()
                    if DB.isNetwork == False and nom_table == "tarifs_lignes":
                        ligne.append(track.IDligne)
                    listeDonnees.append(ligne)

                liste_champs = track.Get_champs_pour_db()
                liste_interro = track.Get_interrogations_pour_db()
                if DB.isNetwork == False and nom_table == "tarifs_lignes":
                    liste_champs += ", IDligne"
                    liste_interro += ", ?"

                DB.Executermany("INSERT INTO %s (%s) VALUES (%s)" % (track.nom_table, liste_champs, liste_interro), listeDonnees, commit=False)

            # Modification
            if len(dict_requetes[nom_table]["modification"]) > 0 :
                listeDonnees = []
                for track in dict_requetes[nom_table]["modification"] :
                    listeTemp = track.Get_variables_pour_db()
                    listeTemp.append(track.GetValeurCle())
                    listeDonnees.append(listeTemp)
                DB.Executermany("UPDATE %s SET %s WHERE %s=?" % (track.nom_table, track.Get_interrogations_et_variables_pour_db(), track.champ_cle), listeDonnees, commit=False)

        # Recherche les suppressions à effectuer
        for nom_table, dictTemp in dict_suppressions.iteritems() :
            liste_suppressions = []
            for ID in self.dict_donnees_initiales[nom_table] :
                if ID not in dictTemp["listeID"] :
                    liste_suppressions.append(ID)
                    #print "Suppression ID", ID, "de la table", nom_table
            if len(liste_suppressions) > 0 :
                if len(liste_suppressions) == 1 :
                    condition = "(%d)" % liste_suppressions[0]
                else :
                    condition = str(tuple(liste_suppressions))
                DB.ExecuterReq("DELETE FROM %s WHERE %s IN %s" % (nom_table, dictTemp["champ_cle"], condition))

        DB.Commit()


        # Remplissage
        listeAjouts = []
        listeModifications = []
        listeSuppressions = []
        for dateDD, dictGroupes in self.dictRemplissage.iteritems() :
            for IDgroupe, dictUnites in dictGroupes.iteritems() :
                for IDunite_remplissage, dictValeurs in dictUnites.iteritems() :
                    places = dictValeurs["places"]
                    initial = dictValeurs["initial"]
                    IDremplissage = dictValeurs["IDremplissage"]
                    if places != initial :
                        # Si la valeur a été modifiée :
                        if IDremplissage == None and places != 0 :
                            listeAjouts.append((self.IDactivite, IDunite_remplissage, IDgroupe, str(dateDD), places))
                        elif IDremplissage != None and places != 0 :
                            listeModifications.append((self.IDactivite, IDunite_remplissage, IDgroupe, str(dateDD), places, IDremplissage))
                        elif IDremplissage != None and places == 0 :
                            listeSuppressions.append(IDremplissage)
                        else:
                            pass

        # Ajouts
        if len(listeAjouts) > 0 :
            DB.Executermany("INSERT INTO remplissage (IDactivite, IDunite_remplissage, IDgroupe, date, places) VALUES (?, ?, ?, ?, ?)", listeAjouts, commit=False)
        # Modifications
        if len(listeModifications) > 0 :
            DB.Executermany("UPDATE remplissage SET IDactivite=?, IDunite_remplissage=?, IDgroupe=?, date=?, places=? WHERE IDremplissage=?", listeModifications, commit=False)
        # Suppression
        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 : 
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else : 
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM remplissage WHERE IDremplissage IN %s" % conditionSuppression)
        # Confirmation
        DB.Commit() 
        
        DB.Close() 

        
    def MAJ(self, annee=None, mois=None, modele=False):
        self.annee = annee
        self.mois = mois
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitGrid(annee=annee, mois=mois, modele=modele)
        self.Refresh()
        
    def InitGrid(self, annee=None, mois=None, modele=False):
        DB = GestionDB.DB()
        if modele == True :
            listeDates = [datetime.date.today(),]
        else :
            listeDates = self.GetListeDates(annee, mois)

        self.listeUnites = self.GetListeUnites(DB, listeDates[0], listeDates[-1])
        self.listeUnitesRemplissage = self.GetListeUnitesRemplissage(DB, listeDates[0], listeDates[-1])
        self.listeGroupes = self.GetListeGroupes(DB)

        if modele == True :
            listeDates = [datetime.date(2998, 12, 1),]
        else :
            listeDates = self.GetListeDates(annee, mois)

        self.GetDictOuvertures(DB, listeDates[0], listeDates[-1])
        self.GetDictRemplissage(DB, listeDates[0], listeDates[-1])
        self.GetDictConso(DB, listeDates[0], listeDates[-1])

        DB.Close()

        nbreColonnes = len(self.listeUnites) + len(self.listeUnitesRemplissage) + 1
        self.AppendCols(nbreColonnes)
        
        dictCases = {}
        
        # ----------------- Création des colonnes -------------------------------------------------------
        largeurColonneOuverture = 50
        largeurColonneEvenement = 70
        largeurColonneRemplissage = 60
        numColonne = 0
        
        # Colonnes Unités
        for dictUnite in self.listeUnites :
            self.SetColLabelValue(numColonne, dictUnite["abrege"])
            largeur = largeurColonneOuverture
            if dictUnite["type"] == "Evenement" :
                largeur = largeurColonneEvenement
            self.SetColSize(numColonne, largeur)
            numColonne += 1
        # Colonne de séparation
        self.SetColLabelValue(numColonne, "")
        self.SetColSize(numColonne, 15)
        numColonne += 1
        # Colonnes Unités de remplissage
        for dictUniteRemplissage in self.listeUnitesRemplissage :
            self.SetColLabelValue(numColonne, dictUniteRemplissage["abrege"])
            self.SetColSize(numColonne, largeurColonneRemplissage)
            numColonne += 1
        
        
        # ------------------ Création des lignes -------------------------------------------------------
        
        nbreLignes = (len(self.listeGroupes)+1) * len(listeDates)
        self.AppendRows(nbreLignes)
        
        self.listeLignesDates = {}
        numLigne = 0
        for dateDD in listeDates :
            
            # Ligne DATE
            hauteurLigne = 20
            if dateDD == datetime.date(2998, 12, 1) :
                label = _(u"Modèle de schéma")
            else :
                label = DateComplete(dateDD)
            self.SetRowLabelValue(numLigne, label)
            self.SetRowSize(numLigne, hauteurLigne)
            self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_DATE))
            self.listeLignesDates[numLigne] = dateDD
            
            numColonne = 0
            for dictUnite in self.listeUnites :
                self.SetReadOnly(numLigne, numColonne, True)
                self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                numColonne += 1
            self.SetReadOnly(numLigne, numColonne, True)
            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
            numColonne += 1
            for dictUniteRemplissage in self.listeUnitesRemplissage :
                self.SetReadOnly(numLigne, numColonne, True)
                self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                numColonne += 1
                        
            numLigne += 1
            
            # Lignes GROUPES
            hauteurLigne = 25
            for dictGroupe in self.listeGroupes :
                IDgroupe = dictGroupe["IDgroupe"]
                self.SetRowLabelValue(numLigne, dictGroupe["nom"])
                self.SetRowSize(numLigne, hauteurLigne)
                self.SetRowLabelRenderer(numLigne, None)
                # Si vacances : entete en jaune
                if self.EstEnVacances(dateDD) == True :
                    self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_VACANCES))
                # Si vacances : entete en gris foncé
                if self.EstFerie(dateDD) == True :
                    self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_FERIE))

                numColonne = 0
                for dictUnite in self.listeUnites :

                    # Recherche une ouverture
                    IDunite = dictUnite["IDunite"]
                    date_debut = dictUnite["date_debut"]
                    date_fin = dictUnite["date_fin"]
                    typeUnite = dictUnite["type"]
                    if self.dictUnitesGroupes.has_key(IDunite) == False :
                        self.dictUnitesGroupes[IDunite] = []

                    liste_evenements = []
                    if (IDgroupe in self.dictUnitesGroupes[IDunite] or len(self.dictUnitesGroupes[IDunite]) == 0) and(str(dateDD) >= date_debut and str(dateDD) <= date_fin) and (str(dateDD) >= self.datesValiditeActivite[0] and str(dateDD) <= self.datesValiditeActivite[1]) :
                        actif = True

                        dictOuverture = self.RechercheOuverture(dateDD, IDgroupe, IDunite)
                        if dictOuverture != None and dictOuverture["etat"] == True :
                            ouvert = True
                            liste_evenements = dictOuverture["liste_evenements"]
                        else :
                            ouvert = False

                    else:
                        actif = False
                        ouvert = False

                    # Si c'est une ligne 'Tous les groupes'
                    if IDgroupe == None :
                        actif = False

                    # Ecrit le nombre de consommations dans la case
                    nbreConso = 0
                    if self.dictConso.has_key(dateDD) :
                        if self.dictConso[dateDD].has_key(IDgroupe) :
                            if self.dictConso[dateDD][IDgroupe].has_key(IDunite) :
                                nbreConso = self.dictConso[dateDD][IDgroupe][IDunite]

                    # Création de la case
                    case = CaseOuverture(self, numLigne=numLigne, numColonne=numColonne, date=dateDD, typeUnite=typeUnite, actif=actif, IDgroupe=IDgroupe, nomGroupe=dictGroupe["nom"], IDunite=IDunite, nbre_conso=nbreConso, liste_evenements=liste_evenements)
                    case.ouvert = ouvert
                    case.Refresh()

                    dictCases[(numLigne, numColonne)] = { "type" : "ouverture", "case" : case, "actif" : actif, "date" : dateDD, "IDgroupe" : IDgroupe, "IDunite" : IDunite }

                    numColonne += 1
                    
                self.SetReadOnly(numLigne, numColonne, True)
                self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                numColonne += 1
                
                for dictUniteRemplissage in self.listeUnitesRemplissage :
                    self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetCellEditor(numLigne, numColonne, gridlib.GridCellNumberEditor(0, 999))
                    
                    # Recherche un remplissage
                    IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                    date_debut = dictUniteRemplissage["date_debut"]
                    date_fin = dictUniteRemplissage["date_fin"]
                    if str(dateDD) >= date_debut and str(dateDD) <= date_fin and (str(dateDD) >= self.datesValiditeActivite[0] and str(dateDD) <= self.datesValiditeActivite[1]) :
                        # Si date valide pour cette unité de remplissage
                        nbrePlaces = self.RechercheRemplissage(dateDD, IDgroupe, IDunite_remplissage)
                        if nbrePlaces > 0 :
                            self.SetCellValue(numLigne, numColonne, str(nbrePlaces))
                        else:
                            self.SetCellValue(numLigne, numColonne, "")
                        actif = True
                    else:
                        # Hors période de validité
                        self.SetReadOnly(numLigne, numColonne, True)
                        self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                        actif = False
                        
                    dictCases[(numLigne, numColonne)] = { "type" : "remplissage", "actif" : actif, "date" : dateDD, "IDgroupe" : IDgroupe, "IDunite_remplissage" : IDunite_remplissage }
                        
                    numColonne += 1
                    
                numLigne += 1
                
                self.dictCases = dictCases
    
    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False
    
    def EstFerie(self, dateDD):
        jour = dateDD.day
        mois = dateDD.month
        annee = dateDD.year        
        for type, nom, jourTmp, moisTmp, anneeTmp in self.listeFeries :
            jourTmp = int(jourTmp)
            moisTmp = int(moisTmp)
            anneeTmp = int(anneeTmp)
            if type == "fixe" :
                if jourTmp == jour and moisTmp == mois :
                    return True
            else:
                if jourTmp == jour and moisTmp == mois and anneeTmp == annee :
                    return True
        return False

    def OnLabelRightClick(self, event):
        numLigne = event.GetRow()
        if numLigne == -1 or self.listeLignesDates.has_key(numLigne) == False : return
        dateDD = self.listeLignesDates[numLigne]
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        item = wx.MenuItem(menuPop, 10, self.GetRowLabelValue(numLigne))
        menuPop.AppendItem(item)
        item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Copier
        item = wx.MenuItem(menuPop, 2000+numLigne, _(u"Copier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Copier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Copier, id=2000+numLigne)
        
        # Item Coller
        item = wx.MenuItem(menuPop, 3000+numLigne, _(u"Coller"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Coller.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Coller, id=3000+numLigne)
        if self.clipboard == None or self.clipboard == dateDD : 
            item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Reinitialiser
        item = wx.MenuItem(menuPop, 4000+numLigne, _(u"Réinitialiser cette date"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ReInitDate, id=4000+numLigne)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Copier(self, event):
        numLigne = event.GetId() - 2000
        dateDD = self.listeLignesDates[numLigne]
        self.clipboard = dateDD
    
    def Coller(self, event):
        numLigne = event.GetId() - 3000
        dateDD = self.listeLignesDates[numLigne]
        numLigne += 1
        
        # Parcours les groupes
        for dictGroupe in self.listeGroupes :
            IDgroupe = dictGroupe["IDgroupe"]
            numColonne = 0
            
            # Parcours les unités
            for dictUnite in self.listeUnites :
                IDunite = dictUnite["IDunite"]
                try :
                    etat = self.dictOuvertures[self.clipboard][IDgroupe][IDunite]["etat"]
                except :
                    etat = False

                try :
                    liste_temp = self.dictOuvertures[self.clipboard][IDgroupe][IDunite]["liste_evenements"]
                    liste_evenements = []
                    for track in liste_temp :
                        track = copy.deepcopy(track)
                        track.Reinit(date=dateDD)
                        liste_evenements.append(track)
                except :
                    liste_evenements = []
                self.OnChangeOuverture(numLigne, numColonne, etat, liste_evenements)
                numColonne += 1
            
            # Parcours les unités de remplissage
            numColonne += 1
            for dictUniteRemplissage in self.listeUnitesRemplissage :
                IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                try :
                    nbrePlaces = self.dictRemplissage[self.clipboard][IDgroupe][IDunite_remplissage]["places"]
                    self.SetCellValue(numLigne, numColonne, str(nbrePlaces))
                    self.OnChangeRemplissage(numLigne, numColonne, nbrePlaces)
                except : 
                    pass
                numColonne += 1
                
            numLigne += 1
    
    def SaisieLot(self):
        import DLG_Saisie_lot_ouvertures2
        dlg = DLG_Saisie_lot_ouvertures2.Dialog(self, IDactivite=self.IDactivite, ctrl_calendrier=self)
        if self.clipboard != None :
            dlg.SetDate(self.clipboard)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees()
            try :
                dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant l'opération..."), None)
                wx.Yield() 
                self.TraitementLot(dictDonnees)
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg2 = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans le traitement par lot : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg2.ShowModal()
                dlg2.Destroy()
        dlg.Destroy()
    
    def TraitementLot(self, dictDonnees={}):
        """ Test de duplication """
        mode = dictDonnees["mode"]
        action = dictDonnees["action"]
        date_debut = dictDonnees["date_debut"]
        date_fin = dictDonnees["date_fin"]
        jours_vacances = dictDonnees["jours_vacances"]
        jours_scolaires = dictDonnees["jours_scolaires"]
        semaines = dictDonnees["semaines"]
        feries = dictDonnees["feries"]

        # Init calendrier
        date_debut_temp = date_debut
        date_fin_temp = date_fin

        if dictDonnees.has_key("date") :
            date = dictDonnees["date"]
            if date < date_debut_temp :
                date_debut_temp = date
            if date > date_fin_temp :
                date_fin_temp = date

        DB = GestionDB.DB()
        self.GetDictOuvertures(DB, date_debut_temp, date_fin_temp)
        self.GetDictRemplissage(DB, date_debut_temp, date_fin_temp)
        self.GetDictConso(DB, date_debut_temp, date_fin_temp)
        DB.Close()

        # Liste dates
        listeDates = [date_debut,]
        tmp = date_debut
        while tmp < date_fin:
            tmp += datetime.timedelta(days=1)
            listeDates.append(tmp)

        date = date_debut
        numSemaine = copy.copy(semaines)
        dateTemp = date
        for date in listeDates :
            
            # Vérifie période et jour
            valide = False
            if self.EstEnVacances(date) :
                if date.weekday() in jours_vacances :
                    valide = True
            else :
                if date.weekday() in jours_scolaires :
                    valide = True

            # Calcul le numéro de semaine
            if len(listeDates) > 0:
                if date.weekday() < dateTemp.weekday():
                    numSemaine += 1

            # Fréquence semaines
            if semaines in (2, 3, 4):
                if numSemaine % semaines != 0:
                    valide = False

            # Semaines paires et impaires
            if valide == True and semaines in (5, 6):
                numSemaineAnnee = date.isocalendar()[1]
                if numSemaineAnnee % 2 == 0 and semaines == 6:
                    valide = False
                if numSemaineAnnee % 2 != 0 and semaines == 5:
                    valide = False

            # Vérifie si férié
            if feries == False and self.EstFerie(date) == True :
                valide = False
                
            # Application
            if valide == True :
                
                for dictGroupe in self.listeGroupes :
                    IDgroupe = dictGroupe["IDgroupe"]
                    
                    # Ouvertures
                    if action in ("date", "schema", "reinit") and (action != "date" or "ouvertures" in dictDonnees["elements"]) :
                        
                        for dictUnite in self.listeUnites :
                            IDunite = dictUnite["IDunite"]
                            if action in ("date", "schema") :
                                try :
                                    if action == "date" :
                                        etat = self.dictOuvertures[dictDonnees["date"]][IDgroupe][IDunite]["etat"]
                                    if action == "schema":
                                        etat = dictDonnees["dictOuvertures"][IDgroupe][IDunite]["etat"]
                                except :
                                    etat = False
                            else :
                                # Mode réinit
                                etat = False
                            
                            # Vérifie si pas de conso
                            try :
                                nbreConso = self.dictConso[date][IDgroupe][IDunite]
                            except :
                                nbreConso = 0

                            if nbreConso == 0 :
                                # Mémorise ouverture
                                dictTemp = self.GetOuverture(date, IDgroupe, IDunite)
                                if dictTemp == None :
                                    IDouverture = None
                                    initial = None
                                else :
                                    IDouverture = dictTemp["IDouverture"]
                                    initial = dictTemp["initial"]
                                self.MemoriseOuverture(date, IDouverture, IDunite, IDgroupe, etat, initial, forcer=True)

                    # Evènements
                    if action in ("date", "schema", "reinit", "ajouter", "supprimer") and (action != "date" or "evenements" in dictDonnees["elements"]):

                        for dictUnite in self.listeUnites:
                            IDunite = dictUnite["IDunite"]

                            try:
                                nbreConso = self.dictConso[date][IDgroupe][IDunite]
                            except:
                                nbreConso = 0

                            liste_evenements = None

                            if action in ("date", "schema") and nbreConso == 0 :
                                try:
                                    if action == "date":
                                        liste_temp = self.dictOuvertures[dictDonnees["date"]][IDgroupe][IDunite]["liste_evenements"]
                                    if action == "schema":
                                        liste_temp = dictDonnees["dictOuvertures"][IDgroupe][IDunite]["liste_evenements"]
                                    if action == "ajouter":
                                        liste_temp = dictDonnees["liste_evenements"]
                                    if action == "supprimer":
                                        liste_temp = []
                                    liste_evenements = []
                                    for track in liste_temp:
                                        track = copy.deepcopy(track)
                                        track.Reinit(date=date)
                                        liste_evenements.append(track)
                                except:
                                    liste_evenements = []

                            if action == "reinit" and nbreConso == 0 :
                                # Mode réinit
                                liste_evenements = []

                            # Mémorisation des évènements
                            if liste_evenements != None:
                                try:
                                    self.dictOuvertures[date][IDgroupe][IDunite]["liste_evenements"] = liste_evenements
                                except:
                                    self.MemoriseOuverture(date, IDouverture=None, IDunite=IDunite, IDgroupe=IDgroupe, etat=True, initial=False, liste_evenements=liste_evenements, forcer=True)

                            # Ajout des évènements
                            if (action == "ajouter" and IDunite== dictDonnees["IDunite"] and IDgroupe == dictDonnees["IDgroupe"]) or action == "supprimer" :
                                try:
                                    liste_evenements = self.dictOuvertures[date][IDgroupe][IDunite]["liste_evenements"]
                                except:
                                    liste_evenements = []

                                if action == "ajouter" :
                                    liste_temp = dictDonnees["liste_evenements"]
                                    for track in liste_temp:
                                        track = copy.deepcopy(track)
                                        track.Reinit(date=date, IDunite=dictDonnees["IDunite"], IDgroupe=dictDonnees["IDgroupe"])
                                        liste_evenements.append(track)

                                        # Mémorisation des évènements
                                        if liste_evenements != None:
                                            try:
                                                self.dictOuvertures[date][IDgroupe][IDunite]["liste_evenements"] = liste_evenements
                                            except:
                                                self.MemoriseOuverture(date, IDouverture=None, IDunite=IDunite, IDgroupe=IDgroupe, etat=True, initial=False, liste_evenements=liste_evenements, forcer=True)

                                if action == "supprimer" :
                                    liste_temp = []
                                    for track in liste_evenements :
                                        if track not in dictDonnees["tracks_a_supprimer"] :
                                            liste_temp.append(track)
                                    liste_evenements = liste_temp
                                    try :
                                        self.dictOuvertures[date][IDgroupe][IDunite]["liste_evenements"] = liste_evenements
                                    except :
                                        pass


                    # Remplissage
                    if action in ("date", "schema", "reinit") and (action != "date" or "places" in dictDonnees["elements"]) :

                        for dictUniteRemplissage in self.listeUnitesRemplissage :
                            IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                            if action in ("date", "schema") :
                                try :
                                    if action == "date" :
                                        nbrePlaces = self.dictRemplissage[dictDonnees["date"]][IDgroupe][IDunite_remplissage]["places"]
                                    if action == "schema" :
                                        nbrePlaces = dictDonnees["dictRemplissage"][IDgroupe][IDunite_remplissage]["places"]
                                except : 
                                    nbrePlaces = 0
                            else :
                                # Mode réinit
                                nbrePlaces = 0
                            
                            # Mémorise remplissage
                            dictTemp = self.GetRemplissage(date, IDgroupe, IDunite_remplissage)
                            if dictTemp == None :
                                IDremplissage = None
                                initial = None
                            else :
                                IDremplissage = dictTemp["IDremplissage"]
                                initial = dictTemp["initial"]
                            self.MemoriseRemplissage(date, IDremplissage, IDunite_remplissage, IDgroupe, nbrePlaces, initial, True)

            dateTemp = date

        # MAJ grille
        self.MAJ(self.annee, self.mois)

    def ReInitDate(self, event):
        numLigne = event.GetId() - 4000
        dateDD = self.listeLignesDates[numLigne]
        # Demande de confirmation
        # dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment réinitialiser les paramètres de la date du %s ?") % DateComplete(dateDD), _(u"Réinitialisation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        # if dlg.ShowModal() != wx.ID_YES :
        #     dlg.Destroy()
        #     return
        # dlg.Destroy()

        numLigne += 1
        
        # Parcours les groupes
        for dictGroupe in self.listeGroupes :
            IDgroupe = dictGroupe["IDgroupe"]
            numColonne = 0
            
            # Parcours les unités
            for dictUnite in self.listeUnites :
                IDunite = dictUnite["IDunite"]
                etat = False
                self.OnChangeOuverture(numLigne, numColonne, etat)
                numColonne += 1
            
            # Parcours les unités de remplissage
            numColonne += 1
            for dictUniteRemplissage in self.listeUnitesRemplissage :
                IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                self.SetCellValue(numLigne, numColonne, "")
                self.OnChangeRemplissage(numLigne, numColonne, 0)
                numColonne += 1
                
            numLigne += 1

    def OnCellChange(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        nbrePlaces = self.GetCellValue(numLigne, numColonne)
        self.OnChangeRemplissage(numLigne, numColonne, nbrePlaces)
        event.Skip()
    
    def OnChangeRemplissage(self, numLigne, numColonne, nbrePlaces) :
        if self.dictCases.has_key((numLigne, numColonne)) :
            infoCase = self.dictCases[(numLigne, numColonne)]
            if infoCase["type"] == "remplissage" and infoCase["actif"] == True :
                nbrePlaces = int(nbrePlaces)
                self.ModifieRemplissage(numLigne, numColonne, infoCase["date"], infoCase["IDgroupe"], infoCase["IDunite_remplissage"], nbrePlaces)
                if nbrePlaces == 0 :
                    self.SetCellValue(numLigne, numColonne, "")

    def ModifieRemplissage(self, numLigne, numColonne, dateDD, IDgroupe, IDunite_remplissage, nbrePlaces):        
        # Modifie le dictionnaire de données
        if self.dictRemplissage.has_key(dateDD) == False :
            self.dictRemplissage[dateDD] = {}
        if self.dictRemplissage[dateDD].has_key(IDgroupe) == False :
            self.dictRemplissage[dateDD][IDgroupe] = {}
        if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) == False :
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = { "IDremplissage" : None, "places" : nbrePlaces, "initial" : None}
        else:
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]["places"] = nbrePlaces

    def OnLeaveWindow(self, event):
        self.SetCursor(CURSOR(wx.CURSOR_DEFAULT))
        # Annule Tooltip
        self.ActiveTooltip(False)

    def OnMouseOver(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)

        caseSurvolee = None
        for coords, infoCase in self.dictCases.iteritems() :
            if infoCase["type"] == "ouverture" and infoCase["actif"] == True :
                case = infoCase["case"]
                if case.SetSurvol(x, y) == True :
                    caseSurvolee = case

        if caseSurvolee != None :
            if caseSurvolee != self.caseSurvolee :
                self.ActiveTooltip(actif=False)
                self.ActiveTooltip(actif=True, case=caseSurvolee)
                self.caseSurvolee = caseSurvolee
                self.SetCursor(CURSOR(wx.CURSOR_HAND))
        else:
            self.caseSurvolee = None
            self.ActiveTooltip(actif=False)
            self.SetCursor(CURSOR(wx.CURSOR_DEFAULT))



    def OnCellLeftClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        self.ActiveTooltip(actif=False)
        case = self.RechercheCaseOuverture(numLigne, numColonne)
        if case != None :
            if case.survolEvenement == True :
                case.SetSurvol(etat=False)
                self.OuvrirEvenements(case)
            else :
                self.OnChangeOuverture(numLigne, numColonne, etat=None, liste_evenements=[])
        event.Skip()

    def OuvrirEvenements(self, case=None):
        liste_evenements = self.dictOuvertures[case.date][case.IDgroupe][case.IDunite]["liste_evenements"]
        from Dlg import DLG_Evenements
        dlg = DLG_Evenements.Dialog(self, grid=self, IDactivite=self.IDactivite, date=case.date, IDunite=case.IDunite, IDgroupe=case.IDgroupe, nomGroupe=case.nomGroupe, liste_evenements=liste_evenements)
        if dlg.ShowModal() == wx.ID_OK:
            liste_evenements = dlg.GetListeEvenements()
            # self.liste_evenements_supprimes.extend(dlg.GetListeEvenementsSupprimes())
            # Mémorisation
            self.dictOuvertures[case.date][case.IDgroupe][case.IDunite]["liste_evenements"] = liste_evenements
            case.liste_evenements = liste_evenements
            case.Refresh()
        dlg.Destroy()


    def RechercheCaseOuverture(self, numLigne, numColonne):
        if self.dictCases.has_key((numLigne, numColonne)) :
            infoCase = self.dictCases[(numLigne, numColonne)]
            if infoCase["type"] == "ouverture" and infoCase["actif"] == True :
                case = infoCase["case"]
                return case
        return None

    def OnChangeOuverture(self, numLigne, numColonne, etat=None, liste_evenements=[], silencieux=False):
        if self.dictCases.has_key((numLigne, numColonne)) :
            infoCase = self.dictCases[(numLigne, numColonne)]
            if infoCase["type"] == "ouverture" and infoCase["actif"] == True :
                case = infoCase["case"]
                # Recherche la valeur actuelle
                if etat == None :
                    dictOuverture = self.RechercheOuverture(case.date, case.IDgroupe, case.IDunite)
                    if dictOuverture != None and dictOuverture["etat"] == True :
                        etat = False
                    else:
                        etat = True

                if case.nbre_conso > 0 :
                    # Interdit la modification si des conso existent
                    if silencieux == False :
                        dlg = wx.MessageDialog(self, _(u"Impossible de supprimer cette ouverture !\n\n%s consommation(s) existent déjà...") % case.nbre_conso, "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                    return False

                if len(case.liste_evenements) > 0 :
                    if silencieux == False :
                        dlg = wx.MessageDialog(None, _(u"%s évènement(s) sont déjà associé(s) à cette unité de consommation.\n\nConfirmez-vous leur suppression ?") % len(case.liste_evenements), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
                        reponse = dlg.ShowModal()
                        dlg.Destroy()
                        if reponse != wx.ID_YES:
                            return False


                    # # Interdit la modification si des évènements existent
                    # dlg = wx.MessageDialog(self, _(u"Impossible de supprimer cette ouverture !\n\n%s évènements(s) y sont déjà associés...") % len(case.liste_evenements), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                    # dlg.ShowModal()
                    # dlg.Destroy()
                    # return False

                # Modification
                self.ModifieOuverture(case=case, ouvert=etat, liste_evenements=liste_evenements)
                self.ClearSelection()
                self.Refresh() 
                return False
    
    def ModifieOuverture(self, case=None, ouvert=False, liste_evenements=[]):
        # Modifie le dictionnaire de données
        if self.dictOuvertures.has_key(case.date) == False :
            self.dictOuvertures[case.date] = {}
        if self.dictOuvertures[case.date].has_key(case.IDgroupe) == False :
            self.dictOuvertures[case.date][case.IDgroupe] = {}
        if self.dictOuvertures[case.date][case.IDgroupe].has_key(case.IDunite) == False :
            self.dictOuvertures[case.date][case.IDgroupe][case.IDunite] = {}
        if self.dictOuvertures[case.date][case.IDgroupe][case.IDunite].has_key("etat") == False :
            self.dictOuvertures[case.date][case.IDgroupe][case.IDunite] = { "IDouverture" : None, "etat" : ouvert, "initial" : None, "liste_evenements" : liste_evenements}
        else:
            self.dictOuvertures[case.date][case.IDgroupe][case.IDunite]["etat"] = ouvert
            self.dictOuvertures[case.date][case.IDgroupe][case.IDunite]["liste_evenements"] = liste_evenements

        # Modifie case du tableau
        case.ouvert = ouvert
        case.liste_evenements = liste_evenements
        case.Refresh()

    def RechercheOuverture(self, dateDD, IDgroupe, IDunite):
        if self.dictOuvertures.has_key(dateDD) :
            if self.dictOuvertures[dateDD].has_key(IDgroupe) :
                if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) :
                    return self.dictOuvertures[dateDD][IDgroupe][IDunite]
        return None

    def GetOuverture(self, dateDD, IDgroupe, IDunite):
        if self.dictOuvertures.has_key(dateDD) :
            if self.dictOuvertures[dateDD].has_key(IDgroupe) :
                if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) :
                    return self.dictOuvertures[dateDD][IDgroupe][IDunite]
        return None

    def RechercheRemplissage(self, dateDD, IDgroupe, IDunite_remplissage):
        if self.dictRemplissage.has_key(dateDD) :
            if self.dictRemplissage[dateDD].has_key(IDgroupe) :
                if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) :
                    if self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]["places"] > 0 :
                        return self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]["places"]
        return 0

    def GetRemplissage(self, dateDD, IDgroupe, IDunite_remplissage):
        if self.dictRemplissage.has_key(dateDD) :
            if self.dictRemplissage[dateDD].has_key(IDgroupe) :
                if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) :
                    return self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]
        return None

    def GetListeDates(self, annee, mois) :
        tmp, nbreJours = calendar.monthrange(annee, mois)
        listeDates = []
        for numJour in range(1, nbreJours+1):
            date = datetime.date(annee, mois, numJour)
            listeDates.append(date)
        return listeDates
        
    def GetListeUnites(self, DB, date_debut, date_fin):
        req = """SELECT IDunite, nom, abrege, type, date_debut, date_fin, ordre
        FROM unites 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeUnites = []
        for IDunite, nom, abrege, type, date_debut, date_fin, ordre in listeDonnees :
            dictTemp = { "IDunite" : IDunite, "nom" : nom, "abrege" : abrege, "type" : type, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre }
            listeUnites.append(dictTemp)
        return listeUnites

    def GetDictUnitesGroupes(self, DB):
        req = """SELECT IDunite_groupe, IDunite, IDgroupe
        FROM unites_groupes; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDonnees = {}
        for IDunite_groupe, IDunite, IDgroupe in listeDonnees :
            if dictDonnees.has_key(IDunite) == False :
                dictDonnees[IDunite] = [IDgroupe,]
            else:
                dictDonnees[IDunite].append(IDgroupe)
        return dictDonnees

    def GetListeUnitesRemplissage(self, DB, date_debut, date_fin):
        req = """SELECT IDunite_remplissage, nom, abrege, date_debut, date_fin, seuil_alerte
        FROM unites_remplissage
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeUnites = []
        for IDunite_remplissage, nom, abrege, date_debut, date_fin, seuil_alerte in listeDonnees :
            dictTemp = { "IDunite_remplissage" : IDunite_remplissage, "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "seuil_alerte" : seuil_alerte }
            listeUnites.append(dictTemp)
        return listeUnites
    
    def GetListeGroupes(self, DB):
        req = """SELECT IDgroupe, nom
        FROM groupes 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeGroupes = []
        for IDgroupe, nom in listeDonnees :
            listeGroupes.append({ "IDgroupe" : IDgroupe, "nom" : nom })
        # Si aucun groupe :
        if len(listeGroupes) == 0 :
            listeGroupes.append({ "IDgroupe" : 0, "nom" : _(u"Sans groupe") })
        # Tous les groupes
        if self.afficherTousGroupes == True :
            listeGroupes.append({ "IDgroupe" : None, "nom" : _(u"Total max.") })
        return listeGroupes
    
    def GetListeVacances(self, DB):
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        return listeDonnees

    def GetListeFeries(self, DB):
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries 
        ; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        return listeDonnees

    def GetDictOuvertures(self, DB, date_debut, date_fin):
        # Importation des ouvertures
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        DB.ExecuterReq(req)
        listeOuvertures = DB.ResultatReq()

        # Importation des évènements
        req = """SELECT IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, capacite_max, heure_debut, heure_fin, montant
        FROM evenements 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date, heure_debut; """ % (self.IDactivite, date_debut, date_fin)
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        liste_evenements = []
        listeIDevenements = []
        for IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, capacite_max, heure_debut, heure_fin, montant in listeTemp :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dict_evenement = {"IDevenement" : IDevenement, "IDactivite" : IDactivite, "IDunite" : IDunite, "IDgroupe" : IDgroupe,
                              "date": date, "nom" : nom, "description" : description, "capacite_max" : capacite_max,
                              "heure_debut": heure_debut, "heure_fin" : heure_fin, "montant" : montant, "tarifs" : []}
            liste_evenements.append(dict_evenement)
            listeIDevenements.append(IDevenement)
            self.dict_donnees_initiales["evenements"].append(IDevenement)

        # Importation des tarifs des évènements
        dict_tarifs = {}
        if len(listeIDevenements) > 0 :

            # Importation des tarifs
            if len(listeIDevenements) == 0 : condition = "()"
            elif len(listeIDevenements) == 1: condition = "(%d)" % listeIDevenements[0]
            else: condition = str(tuple(listeIDevenements))

            req = """SELECT IDtarif, IDactivite, date_debut, date_fin, methode, type, categories_tarifs, groupes, etiquettes, cotisations, 
            caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, 
            IDtype_quotient, label_prestation, IDevenement
            FROM tarifs WHERE IDevenement IN %s;""" % condition
            DB.ExecuterReq(req)
            listeDonneesTarifs = DB.ResultatReq()
            listeIDtarif = []
            for temp in listeDonneesTarifs :
                listeIDtarif.append(temp[0])
                self.dict_donnees_initiales["tarifs"].append(temp[0])

            # Importation des filtres de questionnaire
            if len(listeIDtarif) == 0 : condition = "()"
            elif len(listeIDtarif) == 1: condition = "(%d)" % listeIDtarif[0]
            else: condition = str(tuple(listeIDtarif))

            req = """SELECT IDtarif, IDfiltre, IDquestion, categorie, choix, criteres FROM questionnaire_filtres WHERE IDtarif IN %s;""" % condition
            DB.ExecuterReq(req)
            listeDonneesFiltres = DB.ResultatReq()
            dictFiltres = {}
            for IDtarif, IDfiltre, IDquestion, categorie, choix, criteres in listeDonneesFiltres :
                if dictFiltres.has_key(IDtarif) == False :
                    dictFiltres[IDtarif] = []
                dictTemp = {"IDfiltre" : IDfiltre, "IDquestion" : IDquestion, "categorie" : categorie, "choix" : choix, "criteres" : criteres, "IDtarif" : IDtarif}
                dictFiltres[IDtarif].append(dictTemp)
                self.dict_donnees_initiales["questionnaire_filtres"].append(IDfiltre)

            # Importation des lignes de tarifs
            req = """SELECT %s FROM tarifs_lignes WHERE IDtarif IN %s ORDER BY num_ligne;""" % (", ".join(CHAMPS_TABLE_LIGNES), condition)
            DB.ExecuterReq(req)
            listeDonneesLignes = DB.ResultatReq()
            dictLignes = {}
            for ligne in listeDonneesLignes :
                index = 0
                dictLigne = {}
                for valeur in ligne :
                    dictLigne[CHAMPS_TABLE_LIGNES[index]] = valeur
                    index += 1
                if dictLignes.has_key(dictLigne["IDtarif"]) == False :
                    dictLignes[dictLigne["IDtarif"]] = []
                dictLignes[dictLigne["IDtarif"]].append(dictLigne)
                self.dict_donnees_initiales["tarifs_lignes"].append(dictLigne["IDligne"])

            # Mémorisation des tarifs
            for IDtarif, IDactivite, date_debut, date_fin, methode, type, categories_tarifs, groupes, etiquettes, cotisations, caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, IDtype_quotient, label_prestation, IDevenement in listeDonneesTarifs :

                # Récupération des filtres du tarif
                if dictFiltres.has_key(IDtarif):
                    liste_filtres = dictFiltres[IDtarif]
                else :
                    liste_filtres = []

                # Récupération des lignes du tarif
                if dictLignes.has_key(IDtarif):
                    liste_lignes = dictLignes[IDtarif]
                else :
                    liste_lignes = []

                dictTemp = {
                    "IDtarif": IDtarif, "IDactivite":IDactivite, "date_debut" : date_debut, "date_fin" : date_fin, "methode" : methode, "type" : type, "categories_tarifs" : categories_tarifs,
                    "groupes": groupes,"etiquettes" : etiquettes, "cotisations" : cotisations, "caisses" : caisses, "description" : description,
                    "jours_scolaires": jours_scolaires, "jours_vacances" : jours_vacances, "observations" : observations, "tva" : tva,
                    "code_compta" : code_compta, "IDtype_quotient": IDtype_quotient,"label_prestation" : label_prestation, "IDevenement" : IDevenement,
                    "filtres" : liste_filtres, "lignes" : liste_lignes,
                    }

                if dict_tarifs.has_key(IDevenement) == False :
                    dict_tarifs[IDevenement] = []
                dict_tarifs[IDevenement].append(dictTemp)

        # Mémorise les évènements sous forme de tracks
        dictEvenements = {}
        for dictEvenement in liste_evenements :

            # Récupération des tarifs associé à l'évènement
            if dict_tarifs.has_key(dictEvenement["IDevenement"]) :
                dictEvenement["tarifs"] = dict_tarifs[dictEvenement["IDevenement"]]

            # Stockage des l'évènement
            track_evenement = Track_evenement(dictEvenement)
            key = (dictEvenement["IDunite"], dictEvenement["IDgroupe"], dictEvenement["date"])
            if dictEvenements.has_key(key) == False :
                dictEvenements[key] = []
            dictEvenements[key].append(track_evenement)

        # Mémorisation des données
        for IDouverture, IDunite, IDgroupe, date in listeOuvertures :
            date = DateEngEnDateDD(date)

            # Recherche des évènements associés
            key = (IDunite, IDgroupe, date)

            if dictEvenements.has_key(key):
                liste_evenements = dictEvenements[key]
            else :
                liste_evenements = []

            self.MemoriseOuverture(date, IDouverture, IDunite, IDgroupe, True, True, liste_evenements)
            self.dict_donnees_initiales["ouvertures"].append(IDouverture)
            
    def MemoriseOuverture(self, dateDD=None, IDouverture=None, IDunite=None, IDgroupe=None, etat=True, initial=True, liste_evenements=[], forcer=False) :
            dictValeurs = { "IDouverture" : IDouverture, "etat" : etat, "initial" : initial, "liste_evenements" : liste_evenements}
            if self.dictOuvertures.has_key(dateDD) == False :
                self.dictOuvertures[dateDD] = {}
            if self.dictOuvertures[dateDD].has_key(IDgroupe) == False :
                self.dictOuvertures[dateDD][IDgroupe] = {}
            if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) == False :
                self.dictOuvertures[dateDD][IDgroupe][IDunite] = {}
            if self.dictOuvertures[dateDD][IDgroupe][IDunite] == {} or forcer == True :
                self.dictOuvertures[dateDD][IDgroupe][IDunite] = dictValeurs

    def GetDictRemplissage(self, DB, date_debut, date_fin):
        req = """SELECT IDremplissage, IDunite_remplissage, IDgroupe, date, places
        FROM remplissage 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDremplissage, IDunite_remplissage, IDgroupe, date, places in listeDonnees :
            dateDD = DateEngEnDateDD(date)
            self.MemoriseRemplissage(dateDD, IDremplissage, IDunite_remplissage, IDgroupe, places, places)
            if IDgroupe == None and self.afficherTousGroupes == None :
                self.parent.SetAfficherTousGroupes(True) 
    
    def MemoriseRemplissage(self, dateDD=None, IDremplissage=None, IDunite_remplissage=None, IDgroupe=None, places=None, initial=None, forcer=False):
        dictValeurs = { "IDremplissage" : IDremplissage, "places" : places, "initial" : initial}
        if self.dictRemplissage.has_key(dateDD) == False :
            self.dictRemplissage[dateDD] = {}
        if self.dictRemplissage[dateDD].has_key(IDgroupe) == False :
            self.dictRemplissage[dateDD][IDgroupe] = {}
        if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) == False :
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = {}
        if self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] == {} or forcer == True :
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = dictValeurs
        
    def GetDictConso(self, DB, date_debut, date_fin):
        req = """SELECT date, IDgroupe, IDunite, COUNT(IDconso)
        FROM consommations 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        GROUP BY date, IDgroupe, IDunite
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for date, IDgroupe, IDunite, nbreConso in listeDonnees :
            date = DateEngEnDateDD(date)
            if self.dictConso.has_key(date) == False :
                self.dictConso[date] = {}
            if self.dictConso[date].has_key(IDgroupe) == False :
                self.dictConso[date][IDgroupe] = {}
            if self.dictConso[date][IDgroupe].has_key(IDunite) == False :
                self.dictConso[date][IDgroupe][IDunite] = {}
            self.dictConso[date][IDgroupe][IDunite] = nbreConso

    def GetValiditeActivite(self, DB):
        req = """SELECT date_debut, date_fin
        FROM activites 
        WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return (None, None)
        return (listeDonnees[0][0], listeDonnees[0][1])

    def AfficheTooltip(self):
        """ Création du supertooltip """
        case = self.tip.case

        # Récupération des données du tooltip
        dictDonnees = case.GetTexteInfobulle()
        if dictDonnees == None or type(dictDonnees) != dict:
            self.ActiveTooltip(actif=False)
            return

        # Paramétrage du tooltip
        font = self.GetFont()
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))

        if dictDonnees.has_key("couleur"):
            couleur = dictDonnees["couleur"]
            self.tip.SetTopGradientColour(couleur)
            self.tip.SetMiddleGradientColour(wx.Colour(255, 255, 255))
            self.tip.SetBottomGradientColour(wx.Colour(255, 255, 255))
            self.tip.SetTextColor(wx.Colour(76, 76, 76))
        else:
            styleTooltip = "Office 2007 Blue"
            self.tip.ApplyStyle(styleTooltip)

        # Titre du tooltip
        bmp = None
        if dictDonnees.has_key("bmp"):
            bmp = dictDonnees["bmp"]
        self.tip.SetHeaderBitmap(bmp)

        titre = None
        if dictDonnees.has_key("titre"):
            titre = dictDonnees["titre"]
            self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
            self.tip.SetHeader(titre)
            self.tip.SetDrawHeaderLine(True)

        # Corps du message
        texte = dictDonnees["texte"]
        self.tip.SetMessage(texte)

        # Pied du tooltip
        pied = None
        if dictDonnees.has_key("pied") and dictDonnees["pied"] != None :
            pied = dictDonnees["pied"]
            self.tip.SetDrawFooterLine(True)
            self.tip.SetFooterBitmap(wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
            self.tip.SetFooterFont(wx.Font(7, font.GetFamily(), font.GetStyle(), wx.LIGHT, font.GetUnderlined(), font.GetFaceName()))
            self.tip.SetFooter(pied)

        # Affichage du Frame tooltip
        self.tipFrame = STT.ToolTipWindow(self, self.tip)
        self.tipFrame.CalculateBestSize()
        x, y = wx.GetMousePosition()
        self.tipFrame.SetPosition((x + 15, y + 17))
        self.tipFrame.DropShadow(True)
        self.tipFrame.StartAlpha(True)  # ou .Show() pour un affichage immédiat

        # Arrêt du timer
        self.timerTip.Stop()
        del self.timerTip

    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try:
                self.tipFrame.Destroy()
                del self.tipFrame
            except:
                pass

    def ActiveTooltip(self, actif=True, case=None):
        if actif == True:
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False:
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(1500)
                self.tip.case = case
        else:
            # Désactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.case = None
            self.CacheTooltip()
            self.caseSurvolee = None


class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDactivite = IDactivite
        
        intro = _(u"Ce calendrier vous permet de définir les jours d'ouverture de l'activité et le nombre maximal de places. Cliquez sur les cases pour indiquer que l'unité est fonctionnelle et saisissez directement les effectifs maximals en double-cliquant sur les cases blanches. <U>Important :</U> Cliquez avec le bouton droit de la souris sur les cases Dates pour utiliser le Copier-Coller.")
        titre = _(u"Calendrier des ouvertures et des évènements")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier.png")
        
        # Selection Mois
        self.staticbox_mois_staticbox = wx.StaticBox(self, -1, _(u"Sélection du mois"))
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.ctrl_mois = wx.Choice(self, -1, choices=[_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")])
        self.spin_mois = wx.SpinButton(self, -1, size=(18, 20),  style=wx.SP_VERTICAL)
        self.spin_mois.SetRange(-1, 1)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", min=1977, max=2999)
        dateDuJour = datetime.date.today()
        self.ctrl_annee.SetValue(dateDuJour.year)
        self.ctrl_mois.SetSelection(dateDuJour.month-1)
        
        # Légende
        self.staticbox_legende_staticbox = wx.StaticBox(self, -1, _(u"Légende"))
        self.listeLegende = [
            { "label" : _(u"Ouvert"), "couleur" : COULEUR_OUVERTURE, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Fermé"), "couleur" : COULEUR_FERMETURE, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Vacances"), "couleur" : COULEUR_VACANCES, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Férié"), "couleur" : COULEUR_FERIE, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Effectifs max."), "couleur" : (255, 255, 255), "ctrl_label" : None, "ctrl_img" : None },
            ]
        index = 0
        for dictTemp in self.listeLegende :
            img = wx.StaticBitmap(self, -1, CreationImage(12, 12, dictTemp["couleur"]))
            label = wx.StaticText(self, -1, dictTemp["label"]) 
            self.listeLegende[index]["ctrl_img"] = img
            self.listeLegende[index]["ctrl_label"] = label
            index += 1

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.check_tous_groupes = wx.CheckBox(self, -1, _(u"Afficher Total max."))

        # Calendrier
        self.staticbox_calendrier_staticbox = wx.StaticBox(self, -1, _(u"Calendrier"))
        self.ctrl_calendrier = Calendrier(self, self.IDactivite)
                
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_saisie_lot = CTRL_Bouton_image.CTRL(self, texte=_(u"Saisie et suppression par lot"), cheminImage="Images/32x32/Magique.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_SPIN, self.OnSpinMois, self.spin_mois)
        self.Bind(wx.EVT_CHOICE, self.OnMois, self.ctrl_mois)
        self.Bind(wx.EVT_SPINCTRL, self.OnAnnee, self.ctrl_annee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSaisieLot, self.bouton_saisie_lot)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAfficherTousGroupes, self.check_tous_groupes)

        # Init
        afficher_tous_groupes = UTILS_Parametres.Parametres(mode="get", categorie="dlg_ouvertures", nom="afficher_tous_groupes", valeur=False)
        self.check_tous_groupes.SetValue(afficher_tous_groupes)
        self.ctrl_calendrier.afficherTousGroupes = afficher_tous_groupes

        self.MAJCalendrier()

    def __set_properties(self):
        self.SetTitle(_(u"Calendrier des ouvertures"))
        self.ctrl_mois.SetToolTip(wx.ToolTip(_(u"Sélectionnez un mois")))
        self.ctrl_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetToolTip(wx.ToolTip(_(u"Sélectionnez une année")))
        self.check_tous_groupes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les lignes 'Total max.' afin de saisir des limitations d'effectifs globales")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_saisie_lot.SetToolTip(wx.ToolTip(_(u"Cliquez ici saisir ou supprimer un lot d'ouvertures")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.ctrl_calendrier.SetMinSize((100, 100))
        self.SetMinSize((890, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        
        # Selection Mois
        staticbox_mois = wx.StaticBoxSizer(self.staticbox_mois_staticbox, wx.VERTICAL)
        grid_sizer_mois = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_mois.Add(self.label_mois, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois.Add(self.ctrl_mois, 0, wx.LEFT, 5)
        grid_sizer_mois.Add(self.spin_mois, 0, wx.EXPAND, 0)
        grid_sizer_mois.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_mois.Add(self.ctrl_annee, 0, wx.LEFT, 5)
        staticbox_mois.Add(grid_sizer_mois, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticbox_mois, 1, wx.EXPAND, 0)
        
        # Légende
        staticbox_legende = wx.StaticBoxSizer(self.staticbox_legende_staticbox, wx.VERTICAL)
        grid_sizer_legende = wx.FlexGridSizer(rows=1, cols=len(self.listeLegende)*3, vgap=4, hgap=4)
        for dictTemp in self.listeLegende :
            grid_sizer_legende.Add(dictTemp["ctrl_img"], 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_legende.Add(dictTemp["ctrl_label"], 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_legende.Add( (5, 5), 0, 0, 0)
        staticbox_legende.Add(grid_sizer_legende, 1, wx.ALL|wx.EXPAND, 6)
        grid_sizer_haut.Add(staticbox_legende, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        staticbox_options.Add(self.check_tous_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticbox_options, 1, wx.EXPAND, 0)


        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
    
        # Calendrier
        staticbox_calendrier = wx.StaticBoxSizer(self.staticbox_calendrier_staticbox, wx.VERTICAL)
        staticbox_calendrier.Add(self.ctrl_calendrier, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_calendrier, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_saisie_lot, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnSpinMois(self, event):
        x = event.GetPosition()
        mois = self.ctrl_mois.GetSelection()+x
        if mois != -1 and mois < 12 :
            self.ctrl_mois.SetSelection(mois)
            self.MAJCalendrier()
        self.spin_mois.SetValue(0)

    def OnMois(self, event): 
        self.MAJCalendrier()

    def OnAnnee(self, event):
        self.MAJCalendrier()

    def MAJCalendrier(self):
        annee = int(self.ctrl_annee.GetValue())
        mois = self.ctrl_mois.GetSelection()+1
        self.Freeze()
        self.ctrl_calendrier.MAJ(annee, mois)
        self.Thaw() 
    
    def OnCheckAfficherTousGroupes(self, event):
        self.ctrl_calendrier.afficherTousGroupes = self.check_tous_groupes.GetValue() 
        self.MAJCalendrier()
    
    def SetAfficherTousGroupes(self, etat=True):
        self.check_tous_groupes.SetValue(etat) 
        self.ctrl_calendrier.afficherTousGroupes = etat

    def OnBoutonCancel(self, event):
        # Suppression des évènements créés
        # listeSuppressions = []
        # for track in self.ctrl_calendrier.liste_evenements_crees :
        #     if track.IDevenement != None :
        #         listeSuppressions.append(track.IDevenement)
        #
        # if len(listeSuppressions) > 0 :
        #     DB = GestionDB.DB()
        #     if len(listeSuppressions) == 1 :
        #         condition = "(%d)" % listeSuppressions[0]
        #     else :
        #         condition = str(tuple(listeSuppressions))
        #     DB.ExecuterReq("DELETE FROM evenements WHERE IDevenement IN %s" % condition)
        #     DB.ExecuterReq("DELETE FROM tarifs WHERE IDevenement IN %s" % condition)
        #     DB.Close()

        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        # Mémoriser paramètres
        UTILS_Parametres.Parametres(mode="set", categorie="dlg_ouvertures", nom="afficher_tous_groupes", valeur=self.check_tous_groupes.GetValue())

        # Mémoriser calendrier
        try :
            dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant la sauvegarde des données..."), None) # .PyBusyInfo(_(u"Veuillez patienter durant la sauvegarde des données..."), parent=None, title=_(u"Enregistrement"), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            self.ctrl_calendrier.Sauvegarde()
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la sauvegarde des ouvertures : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Calendrier")

    def OnBoutonSaisieLot(self, event): 
        self.ctrl_calendrier.SaisieLot() 
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
