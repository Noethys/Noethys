#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import random
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import GestionDB
from Utils import UTILS_Dates
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Texte
from Utils import UTILS_Config
from Ctrl import CTRL_Selection_periode_simple
from Ctrl import CTRL_Saisie_heure
from dateutil import rrule
import wx.lib.agw.supertooltip as STT
import wx.lib.wordwrap as wordwrap

if 'phoenix' in wx.PlatformInfo:
    from wx.grid import GridCellRenderer
else:
    from wx.grid import PyGridCellRenderer as GridCellRenderer




class Track_location(object):
    def __init__(self, grid=None, donnees=None):
        self.grid = grid
        self.IDlocation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDproduit = donnees[2]
        self.observations = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.quantite = donnees[6]
        self.nomProduit = donnees[7]
        self.nomCategorie = donnees[8]

        if self.quantite == None :
            self.quantite = 1

        # Période
        if isinstance(self.date_debut, str) or isinstance(self.date_debut, unicode) :
            self.date_debut = datetime.datetime.strptime(self.date_debut, "%Y-%m-%d %H:%M:%S")

        if self.date_fin == None:
            self.date_fin = datetime.datetime(2999, 1, 1)

        if isinstance(self.date_fin, str) or isinstance(self.date_fin, unicode) :
            self.date_fin = datetime.datetime.strptime(self.date_fin, "%Y-%m-%d %H:%M:%S")

        # Récupération des réponses des questionnaires
        # for dictQuestion in grid.liste_questions :
        #     setattr(self, "question_%d" % dictQuestion["IDquestion"], grid.GetReponse(dictQuestion["IDquestion"], self.IDproduit))

        # Famille
        self.nomTitulaires = grid.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        self.rue = grid.dict_titulaires[self.IDfamille]["adresse"]["rue"]
        self.cp = grid.dict_titulaires[self.IDfamille]["adresse"]["cp"]
        self.ville = grid.dict_titulaires[self.IDfamille]["adresse"]["ville"]

        # Couleur de barre
        if self.grid.dict_couleurs.has_key(self.IDfamille) :
            self.couleur = self.grid.dict_couleurs[self.IDfamille]
        else :
            self.couleur = wx.Colour(random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
            self.grid.dict_couleurs[self.IDfamille] = self.couleur

        # Sousligne
        self.num_sousligne = None
        self.rect_barre = None

    def Modifier(self, event=None):
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self.grid, IDlocation=self.IDlocation, IDfamille=self.IDfamille)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_OK:
            self.grid.MAJ()

    def Supprimer(self, event=None):
        from Ol.OL_Locations import Supprimer_location
        resultat = Supprimer_location(self.grid, IDlocation=self.IDlocation)
        if resultat == True :
            self.grid.MAJ()

    def GetTexteStatusBar(self):
        debut = UTILS_Dates.DatetimeEnFr(self.date_debut)
        if self.date_fin.year == 2999:
            fin = u"\nFin non définie"
        else:
            fin = UTILS_Dates.DatetimeEnFr(self.date_fin)
        texte = _(u"%s -> %s (de %s à %s)") % (self.nomTitulaires, self.nomProduit, debut, fin)
        return texte



class Track_produit(object):
    def __init__(self, grid=None, numLigne=0, donnees=None):
        self.grid = grid
        self.numLigne = numLigne
        self.IDproduit = donnees[0]
        self.nom = donnees[1]
        self.observations = donnees[2]
        self.nomCategorie = donnees[3]

        # Liste des locations associées
        self.locations = []
        self.locations_affichees = []
        self.locations_by_date = {}
        self.souslignes = {}
        self.nbre_chevauchements = 0

    def SetHauteurLigne(self, hauteur=0):
        if self.nbre_chevauchements > 1 :
            hauteur = hauteur * self.nbre_chevauchements
        self.grid.SetRowSize(self.numLigne, hauteur)

    def CalculeSouslignes(self, tracks_dates=[]):
        self.tracks_dates = tracks_dates

        # Recherche les locations pour chaque date
        self.locations_affichees = []
        self.locations_by_date = {}

        for track_date in tracks_dates :
            for track_location in self.locations:
                if track_location.date_debut.date() <= track_date.date and track_location.date_fin.date() >= track_date.date:
                    if self.locations_by_date.has_key(track_date) == False :
                        self.locations_by_date[track_date] = []
                    self.locations_by_date[track_date].append(track_location)

                    if track_location not in self.locations_affichees :
                        self.locations_affichees.append(track_location)

        for track_location in self.locations_affichees :
            for num_sousligne in range(0, len(self.locations_affichees)):
                if self.souslignes.has_key(num_sousligne) == False :
                    self.souslignes[num_sousligne] = None
                date_max = self.souslignes[num_sousligne]
                if date_max == None or track_location.date_debut > date_max :
                    track_location.num_sousligne = num_sousligne
                    self.souslignes[num_sousligne] = track_location.date_fin
                    break

        self.nbre_chevauchements = len(self.souslignes.keys())

    def Draw_cases(self):
        numColonne = 0
        for track_date in self.tracks_dates :

            # Recherche les locations de la date
            if self.locations_by_date.has_key(track_date) :
                tracks_locations = self.locations_by_date[track_date]
            else :
                tracks_locations = []

            # Création de la case
            case = Case(self.grid, numLigne=self.numLigne, numColonne=numColonne, track_produit=self, track_date=track_date, tracks_locations=tracks_locations)
            self.grid.dictCases[(self.numLigne, numColonne)] = case
            numColonne += 1




class Track_date(object):
    def __init__(self, grid=None, numColonne=0, date=None, heure_min=None, heure_max=None):
        self.grid = grid
        self.numColonne = numColonne
        self.date = date
        self.heure_min = heure_min
        self.heure_max = heure_max
        self.largeur_colonne = 0
        self.largeur_graduations = 0

    def HeureEnPos(self, heure):
        self.largeur_graduations = self.GetLargeurGraduations()
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.heure_max, self.heure_min)
        return 1.0 * UTILS_Dates.SoustractionHeures(heure, self.heure_min).seconds / tempsAffichable.seconds * self.largeur_graduations

    def GetLargeurGraduations(self):
        return self.largeur_colonne - self.grid.dict_parametres["padding_horizontal"] * 2




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
    dc.DrawLine(left + 1, top, left + 1, bottom)
    dc.DrawLine(left + 1, top, right, top)




class LabelColonneRenderer(glr.GridLabelRenderer):
    def __init__(self, grid=None, track_date=None):
        self.grid = grid
        self.track_date = track_date

    # def HeureEnPos(self, heure, rect):
    #     tempsAffichable = UTILS_Dates.SoustractionHeures(self.track_date.heure_max, self.track_date.heure_min)
    #     return 1.0 * UTILS_Dates.SoustractionHeures(heure, self.track_date.heure_min).seconds / tempsAffichable.seconds * self.GetLargeurMax(rect)
    #
    # def GetLargeurMax(self, rect=None):
    #     return rect.GetWidth() - self.grid.dict_parametres["padding_horizontal"] * 2

    def GetTailleTexte(self, dc, texte, width):
        lignes = wordwrap.wordwrap(texte, width, dc, True)
        largeur_max = 0
        for ligne in lignes.split("\n") :
            largeur, hauteur, descent, externalLeading = dc.GetFullTextExtent(ligne)
            if largeur > largeur_max :
                largeur_max = largeur
        return lignes, largeur_max, (lignes.count("\n") + 1) * (hauteur + externalLeading)

    def AssembleDateEtHeure(self, date=None, heure=None):
        return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=heure.hour, minute=heure.minute)

    def Draw(self, grid, dc, rect, col):
        self.track_date.largeur_colonne = rect.GetWidth()

        # Bordure de la case
        self.DrawBorder(grid, dc, rect)

        # Graduations
        dc.SetPen(wx.Pen("black"))
        dc.SetTextForeground("black")
        dc.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))

        dtmin = self.AssembleDateEtHeure(self.track_date.date, self.track_date.heure_min)
        dtmax = self.AssembleDateEtHeure(self.track_date.date, self.track_date.heure_max)

        listeGraduations = list(rrule.rrule(rrule.MINUTELY, byminute=(0, 15, 30, 45), dtstart=dtmin, until=dtmax))
        ecartGraduations = 1.0 * self.track_date.GetLargeurGraduations() / len(listeGraduations)

        hauteurGraduations = 0
        if ecartGraduations > 2 :
            index = 0
            for dt in listeGraduations :
                x = self.track_date.HeureEnPos(dt) + self.grid.dict_parametres["padding_horizontal"]
                posY = rect.height - 17
                hautTraitHeures = 4
                if dt.minute == 0:
                    hauteurTrait = hautTraitHeures
                    texte = "%dh" % dt.hour
                    largTexte, hautTexte = dc.GetTextExtent(texte)
                    if ecartGraduations > 5 :
                        dc.DrawText(texte, x - (largTexte / 2) + rect.x, posY + 2)
                        hauteurGraduations = 10
                    else :
                        hauteurGraduations = 4
                elif dt.minute in (15, 45):
                    hauteurTrait = 1
                elif dt.minute == 30:
                    hauteurTrait = 2.5
                dc.DrawLine(x + rect.x, posY + hautTexte + hautTraitHeures - hauteurTrait, x + rect.x, posY + hautTexte + hautTraitHeures)
                index += 1

        # Label
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.SetTextForeground("black")
        if self.track_date.date == datetime.date.today() :
            dc.SetTextForeground("red")

        # Définit le texte du label
        largeurRect = self.track_date.GetLargeurGraduations()
        if largeurRect < 50 :
            texte = str(self.track_date.date.day)
        elif largeurRect < 100 :
            texte = UTILS_Dates.DateEngFr(self.track_date.date)
        elif largeurRect < 150 :
            texte = UTILS_Dates.DateComplete(self.track_date.date, abrege=True)
        else :
            texte = UTILS_Dates.DateComplete(self.track_date.date, abrege=False)

        # Recherche taille du label
        texte, largTexte, hautTexte = self.GetTailleTexte(dc, texte, rect.width)
        x = rect.width / 2.0 - largTexte / 2.0 + rect.x
        y = rect.height / 2.0 - hautTexte / 2.0 - hauteurGraduations
        dc.DrawText(texte, x, y)




class Case():
    def __init__(self, grid=None, numLigne=None, numColonne=None, track_produit=None, track_date=None, tracks_locations=[]):
        self.grid = grid
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.track_produit = track_produit
        self.track_date = track_date
        self.tracks_locations = tracks_locations
        self.dict_barres_case = {}

        # Dessin de la case
        self.renderer = CaseRenderer(self)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

    def GetRect(self):
        return self.grid.CellToRect(self.numLigne, self.numColonne)

    def Refresh(self):
        rect = self.GetRect()
        x, y = self.grid.CalcScrolledPosition(rect.GetX(), rect.GetY())
        rect = wx.Rect(x, y, rect.GetWidth(), rect.GetHeight())
        self.grid.GetGridWindow().Refresh(False, rect)

    def FindLocation(self, x, y):
        for track_location, rect in self.dict_barres_case.iteritems() :
            if 'phoenix' in wx.PlatformInfo:
                contains = rect.Contains(x, y)
            else:
                contains = rect.ContainsXY(x, y)
            if contains == True :
                return track_location
        return None

    def Ajouter(self, x=None):
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self.grid, IDlocation=None, IDfamille=None, IDproduit=self.track_produit.IDproduit)

        dlg.ctrl_date_debut.SetDate(self.track_date.date)
        heure_debut = self.renderer.PosEnHeure(x)
        if heure_debut not in ("", None):
            dlg.ctrl_heure_debut.SetHeure(UTILS_Dates.DatetimeTimeEnStr(heure_debut, separateur=":"))

        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_OK:
            self.grid.MAJ()




class CaseRenderer(GridCellRenderer):
    def __init__(self, case=None):
        GridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def HeureEnPos(self, heure, rect):
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.case.track_date.heure_max, self.case.track_date.heure_min)
        return 1.0 * UTILS_Dates.SoustractionHeures(heure, self.case.track_date.heure_min).seconds / tempsAffichable.seconds * self.GetLargeurGraduations(rect)

    def PosEnHeure(self, x, arrondir=False):
        if self.grid == None :
            return ""
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.case.track_date.heure_max, self.case.track_date.heure_min)
        rect = self.grid.CellToRect(self.case.numLigne, self.case.numColonne)
        pos = x - rect.x - self.grid.dict_parametres["padding_horizontal"]
        temp = datetime.timedelta(seconds=1.0 * pos / self.GetLargeurGraduations(rect) * tempsAffichable.seconds)
        if arrondir == True :
            temp = UTILS_Dates.DeltaEnTime(temp)
            minutes = temp.strftime("%M")
            if int(minutes[1]) < 5 : minutes = "%s%d" % (minutes[0], 0)
            if int(minutes[1]) > 5 : minutes = "%s%d" % (minutes[0], 5)
            temp = datetime.time(int(temp.strftime("%H")), int(minutes))
        heure = UTILS_Dates.AdditionHeures(self.case.track_date.heure_min, temp)
        return UTILS_Dates.DeltaEnTime(heure)

    def GetLargeurGraduations(self, rect):
        return rect.GetWidth() - self.grid.dict_parametres["padding_horizontal"] * 2

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid

        canvas = wx.EmptyBitmap(rect.width, rect.height)
        mdc = wx.MemoryDC()
        mdc.SelectObject(canvas)

        # Dessine le fond
        if self.case.track_date.date.weekday() in (5, 6) :
            couleur_fond = wx.Colour(247, 247, 247)
        else :
            couleur_fond = wx.WHITE

        mdc.SetBackgroundMode(wx.SOLID)
        mdc.SetBrush(wx.Brush(couleur_fond, wx.SOLID))
        mdc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            mdc.DrawRectangle(wx.Rect(0, 0, rect.width, rect.height))
        else:
            mdc.DrawRectangleRect(wx.Rect(0, 0, rect.width, rect.height))

        mdc.SetBackgroundMode(wx.TRANSPARENT)
        mdc.SetFont(attr.GetFont())

        # Dessine les locations
        self.case.dict_barres_case = {}
        for track_location in self.case.tracks_locations :

            # Recherche heure de début
            if track_location.date_debut.date() == self.case.track_date.date :
                x_debut = self.HeureEnPos(track_location.date_debut, rect) + self.grid.dict_parametres["padding_horizontal"]
            else :
                x_debut = 0

            # Recherche heure de fin
            if track_location.date_fin.date() == self.case.track_date.date :
                x_fin = self.HeureEnPos(track_location.date_fin, rect) + self.grid.dict_parametres["padding_horizontal"]
            else :
                x_fin = rect.width + 1

            hauteur = 1.0 * rect.height / self.case.track_produit.nbre_chevauchements + 1
            y = track_location.num_sousligne * hauteur
            largeur = x_fin - x_debut

            # Ecrit le label de la barre
            rect_barre = wx.Rect(x_debut, y, largeur, hauteur)
            couleur = track_location.couleur
            mdc.SetBrush(wx.Brush(couleur))
            mdc.SetPen(wx.TRANSPARENT_PEN)
            mdc.DrawRectangleRect(rect_barre)

            # Mémorise le rect de la barre
            self.case.dict_barres_case[track_location] = wx.Rect(rect_barre.x+rect.x, rect_barre.y+rect.y, rect_barre.width, rect_barre.height)

            # Ecrit le label de la barre
            texte = track_location.nomTitulaires
            lignes = wordwrap.wordwrap(texte, largeur, mdc, True)

            mdc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            mdc.SetTextForeground(wx.Colour(0, 0, 0))
            nbre_lignes_a_afficher = int(hauteur / 15)
            if rect_barre.width < 50 :
                nbre_lignes_a_afficher = 1
            if rect_barre.height < 15 :
                nbre_lignes_a_afficher = 0
            texte = u"\n".join(lignes.split(u"\n")[:nbre_lignes_a_afficher])
            mdc.DrawText(texte, x_debut + 5, y + 2)

        # Double buffering
        dc.SetClippingRegion(rect.x, rect.y, rect.width, rect.height)
        dc.Blit(rect.x, rect.y, rect.width, rect.height, mdc, 0, 0)
        dc.DestroyClippingRegion()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return CaseRenderer()








# ---------------------------------------------------------------------------------------

class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin):
    def __init__(self, parent, ctrl_options=None):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.parent = parent
        self.ctrl_options = ctrl_options

        self.dict_parametres = {
            "padding_horizontal" : 10,
            "padding_vertical": 5,
            }

        self.dictCases = {}
        self.dict_couleurs = {}
        self.moveTo = None
        self.CreateGrid(1, 1)
        self.SetMinSize((100, 100))
        self.SetRowLabelSize(190)
        self.SetColLabelSize(60)
        self.EnableGridLines(True)

        # Pour cacher le curseur
        self.SetCellHighlightPenWidth(0)
        self.SetCellHighlightROPenWidth(0)

        # Init Tooltip
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip après 10 secs
        self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        self.caseSurvolee = None

        # Binds
        self.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.GetGridWindow().Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDoubleClick)

    def EcritStatusbar(self, texte=""):
        try :
            topWindow = wx.GetApp().GetTopWindow()
            topWindow.SetStatusText(texte)
        except :
            pass

    def OnLeaveWindow(self, event):
        self.EcritStatusbar("")
        self.ActiveTooltip(False)

    def OnMouseMotion(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)

        case = None
        texteStatusBar = ""
        if self.dictCases.has_key((numLigne, numColonne)) :
            case = self.dictCases[(numLigne, numColonne)]
            track_location = case.FindLocation(x, y)
            if track_location != None :
                texteStatusBar = track_location.GetTexteStatusBar()
            else :
                texteStatusBar = u"%s - %s" % (UTILS_Dates.DateComplete(case.track_date.date), case.renderer.PosEnHeure(x))
        self.EcritStatusbar(texteStatusBar)

        if case != None :
            if case != self.caseSurvolee :
                self.ActiveTooltip(actif=False)
                self.ActiveTooltip(actif=True, track_location=track_location)
        else:
            self.caseSurvolee = None
            self.ActiveTooltip(actif=False)

    def OnRightClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        self.ActiveTooltip(actif=False)

        if self.dictCases.has_key((numLigne, numColonne)):
            case = self.dictCases[(numLigne, numColonne)]
            track_location = case.FindLocation(x, y)

            menuPop = UTILS_Adaptations.Menu()

            # Item Modifier
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.Ajouter, id=10)

            if track_location != None:

                menuPop.AppendSeparator()

                # Item Ajouter
                item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, track_location.Modifier, id=20)

                # Item Supprimer
                item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, track_location.Supprimer, id=30)

            self.PopupMenu(menuPop)
            menuPop.Destroy()

    def OnLeftDoubleClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        self.ActiveTooltip(actif=False)

        if self.dictCases.has_key((numLigne, numColonne)) :
            case = self.dictCases[(numLigne, numColonne)]
            track_location = case.FindLocation(x, y)
            if track_location != None :
                track_location.Modifier()
            else :
                case.Ajouter(x=x)

    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try:
                self.tipFrame.Destroy()
                del self.tipFrame
            except:
                pass

    def ActiveTooltip(self, actif=True, track_location=None):
        if actif == True:
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False:
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(800)
                self.tip.track_location = track_location
        else:
            # Désactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.track_location = None
            self.CacheTooltip()
            self.caseSurvolee = None

    def AfficheTooltip(self):
        """ Création du supertooltip """
        track_location = self.tip.track_location

        # Paramétrage du tooltip
        font = self.GetFont()
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))

        if track_location != None :
            couleur = track_location.couleur
        else :
            couleur = wx.Colour(255, 255, 255)
        self.tip.SetTopGradientColour(couleur)
        self.tip.SetMiddleGradientColour(wx.Colour(255, 255, 255))
        self.tip.SetBottomGradientColour(wx.Colour(255, 255, 255))
        self.tip.SetTextColor(wx.Colour(76, 76, 76))

        # Titre du tooltip
        # bmp = None
        # if dictDonnees.has_key("bmp"):
        #     bmp = dictDonnees["bmp"]
        # self.tip.SetHeaderBitmap(bmp)

        if track_location != None:
            titre = track_location.nomTitulaires
        else :
            titre = _(u"Aucune location")
        self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetHeader(titre)
        self.tip.SetDrawHeaderLine(True)

        # Corps du message
        if track_location != None:
            texte = u""
            texte += u"Produit : %s" % track_location.nomProduit
            texte += u"\nCatégorie : %s" % track_location.nomCategorie
            texte += u"\n"
            texte += u"\nDébut : %s" % UTILS_Dates.DatetimeEnFr(track_location.date_debut)
            if track_location.date_fin.year == 2999 :
                texte += u"\nFin : Non définie"
            else :
                texte += u"\nFin : %s" % UTILS_Dates.DatetimeEnFr(track_location.date_fin)
            texte += u"\n"
            texte += u"\nQuantité : %s" % track_location.quantite
            if len(self.liste_questions) > 0 :
                texte += u"\n"
                for dictQuestion in self.liste_questions :
                    texte += u"\n%s : %s" % (dictQuestion["label"], self.GetReponse(dictQuestion["IDquestion"], track_location.IDlocation))
        else :
            texte = _(u"Aucune location n'est enregistrée à cette date.\n\n")
        self.tip.SetMessage(texte)

        # Pied du tooltip
        if track_location != None:
            pied = _(u"Double-cliquez pour modifier")
        else :
            pied = _(u"Double-cliquez pour saisir une nouvelle location")
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

    def GetReponse(self, IDquestion=None, ID=None):
        if self.dict_questionnaires.has_key(IDquestion) :
            if self.dict_questionnaires[IDquestion].has_key(ID) :
                return self.dict_questionnaires[IDquestion][ID]
        return u""

    def Importation(self):
        """ Importation des données """
        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Initialisation des questionnaires
        categorie = "location"
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

        # Conditions
        liste_categories = self.ctrl_options.GetCategories()
        if len(liste_categories) == 0: conditionCategories = "()"
        elif len(liste_categories) == 1: conditionCategories = "(%d)" % liste_categories[0]
        else: conditionCategories = str(tuple(liste_categories))

        # Importation des produits
        DB = GestionDB.DB()
        req = """SELECT IDproduit, produits.nom, produits.observations, produits_categories.nom
        FROM produits
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE produits.IDcategorie IN %s
        ORDER BY produits.nom;""" % conditionCategories
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeTracksProduits = []
        dictTracksProduitsByIDproduit = {}
        numLigne = 0
        for item in listeDonnees :
            track_produit = Track_produit(grid=self, numLigne=numLigne, donnees=item)
            listeTracksProduits.append(track_produit)
            dictTracksProduitsByIDproduit[track_produit.IDproduit] = track_produit
            numLigne += 1

        # Importation des locations
        date_debut = self.ctrl_options.GetDateDebut()
        date_fin = self.ctrl_options.GetDateFin()
        if date_debut != None and date_fin != None :
            req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
            locations.observations, locations.date_debut, locations.date_fin, locations.quantite,
            produits.nom, 
            produits_categories.nom
            FROM locations
            LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
            LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
            WHERE produits.IDcategorie IN %s AND locations.date_debut <= '%s' AND (locations.date_fin >= '%s' OR locations.date_fin IS NULL)
            ORDER BY locations.date_debut;""" % (conditionCategories, date_fin, date_debut)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            for item in listeDonnees :
                track_location = Track_location(grid=self, donnees=item)
                dictTracksProduitsByIDproduit[track_location.IDproduit].locations.append(track_location)

        return listeTracksProduits

    def MAJ(self, reinit_scroll=False):
        # Importation
        self.listeTracksProduits = self.Importation()

        # Mémorise la position du scroll
        posScrollH = self.GetScrollPos(wx.HORIZONTAL)
        posScrollV = self.GetScrollPos(wx.VERTICAL)

        # RAZ de la grid
        self.Freeze()
        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0:
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()

        # Création des colonnes
        date_debut = self.ctrl_options.GetDateDebut()
        date_fin = self.ctrl_options.GetDateFin()
        if date_debut == None or date_fin == None :
            self.Thaw()
            return

        heure_min = self.ctrl_options.GetHeureMin()
        heure_max = self.ctrl_options.GetHeureMax()
        if heure_min == None or heure_max == None or heure_min >= heure_max :
            self.Thaw()
            return

        listeDates = list(rrule.rrule(rrule.DAILY, dtstart=date_debut, until=date_fin))
        self.AppendCols(len(listeDates))

        tracks_dates = []
        numColonne = 0
        for date in listeDates :
            track_date = Track_date(grid=self, numColonne=numColonne, date=date.date(), heure_min=UTILS_Dates.HeureStrEnTime(heure_min), heure_max=UTILS_Dates.HeureStrEnTime(heure_max))
            tracks_dates.append(track_date)
            renderer = LabelColonneRenderer(grid=self, track_date=track_date)
            self.SetColLabelRenderer(numColonne, renderer)
            self.SetColSize(numColonne, self.ctrl_options.GetLargeur())
            numColonne += 1

        # Création des lignes
        nbreLignes = len(self.listeTracksProduits)
        self.AppendRows(nbreLignes)

        # Calcule les chevauchements
        for track_produit in self.listeTracksProduits :
            track_produit.CalculeSouslignes(tracks_dates)

        # Création des lignes produits
        self.dictCases = {}
        numLigne = 0
        for track_produit in self.listeTracksProduits :

            # Création de l'entete de ligne
            self.SetRowLabelValue(numLigne, track_produit.nom)
            track_produit.SetHauteurLigne(self.ctrl_options.GetHauteur())

            # Création des cases
            track_produit.Draw_cases()

            numLigne += 1

        # Remet les scrolls à la position précédente
        if reinit_scroll == False :
            self.Scroll(posScrollH, posScrollV)

        self.Thaw()

    def SetLargeurColonne(self, largeur=0):
        for numColonne in range(0, self.GetNumberCols()) :
            self.SetColSize(numColonne, largeur)

    def SetHauteurLigne(self, hauteur=0):
        for track_produit in self.listeTracksProduits :
            track_produit.SetHauteurLigne(hauteur)


# --------------------------------------------------------------------------------

class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((80, 80))
        self.MAJ()

    def MAJ(self):
        self.Importation()

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM produits_categories
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictCategories = {}
        index = 0
        for IDcategorie, nom in listeDonnees:
            self.Append(nom)
            self.dictCategories[index] = IDcategorie
            self.Check(index)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        for index, IDcategorie in self.dictCategories.iteritems():
            if self.IsChecked(index):
                listeIDcoches.append(IDcategorie)
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        if type(listeIDcoches) == str :
            listeIDcoches = UTILS_Texte.ConvertStrToListe(listeIDcoches)
        for index, IDcategorie in self.dictCategories.iteritems():
            if IDcategorie in listeIDcoches:
                self.Check(index)



# -------------------------------------------------------------------------------------

class CTRL_Options(wx.Panel):
    def __init__(self, parent, ctrl_tableau=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.ctrl_tableau = ctrl_tableau

        # Période
        self.staticBox_periode = wx.StaticBox(self, -1, _(u"Sélection de la période"))
        self.ctrl_periode = CTRL_Selection_periode_simple.CTRL(self, callback=self.MAJTableau)

        # Catégories de produits
        self.staticBox_categories = wx.StaticBox(self, -1, _(u"Catégories de produits"))
        self.ctrl_categories = CTRL_Categories(self)

        # Options
        self.staticBox_options = wx.StaticBox(self, -1, _(u"Options d'affichage"))

        # Horaires
        self.label_horaires = wx.StaticText(self, wx.ID_ANY, _(u"Amplitude horaire :"))
        self.ctrl_heure_min = CTRL_Saisie_heure.Heure(self)
        self.label_a = wx.StaticText(self, wx.ID_ANY, _(u"à"))
        self.ctrl_heure_max = CTRL_Saisie_heure.Heure(self)
        self.bouton_appliquer_horaires = wx.Button(self, -1, _(u"Appliquer"))

        # Largeur
        self.img_largeur = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Largeur.png"), wx.BITMAP_TYPE_ANY))
        self.slider_largeur = wx.Slider(self, -1,  value=160, minValue=25, maxValue=1000, size=(-1, -1), style=wx.SL_HORIZONTAL)

        # Haute
        self.img_hauteur = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Hauteur.png"), wx.BITMAP_TYPE_ANY))
        self.slider_hauteur = wx.Slider(self, -1,  value=40, minValue=5, maxValue=200, size=(-1, -1), style=wx.SL_HORIZONTAL)

        # Properties
        self.ctrl_heure_min.SetToolTip(wx.ToolTip(_(u"Saisissez l'heure minimale à afficher")))
        self.ctrl_heure_max.SetToolTip(wx.ToolTip(_(u"Saisissez l'heure maximale à afficher")))
        self.bouton_appliquer_horaires.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider les horaires saisis")))
        self.slider_largeur.SetToolTip(wx.ToolTip(_(u"Ajustez la largeur des colonnes")))
        self.slider_hauteur.SetToolTip(wx.ToolTip(_(u"Ajustez la hauteur des lignes")))

        # Binds
        self.Bind(wx.EVT_SCROLL, self.OnSliderLargeur, self.slider_largeur)
        self.Bind(wx.EVT_SCROLL, self.OnSliderHauteur, self.slider_hauteur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHoraires, self.bouton_appliquer_horaires)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckCategories, self.ctrl_categories)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(1, 3, 10, 10)

        # Période
        staticBox_periode = wx.StaticBoxSizer(self.staticBox_periode, wx.HORIZONTAL)
        staticBox_periode.Add(self.ctrl_periode, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(staticBox_periode, 1, wx.EXPAND, 0)

        # Catégories
        staticBox_categories = wx.StaticBoxSizer(self.staticBox_categories, wx.HORIZONTAL)
        staticBox_categories.Add(self.ctrl_categories, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(staticBox_categories, 1, wx.EXPAND, 0)

        # Options
        staticBox_Options = wx.StaticBoxSizer(self.staticBox_options, wx.HORIZONTAL)
        grid_sizer_options = wx.FlexGridSizer(3, 1, 5, 5)

        # Horaires
        grid_sizer_horaires = wx.FlexGridSizer(1, 6, 5, 5)
        grid_sizer_horaires.Add(self.label_horaires, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_min, 0, wx.EXPAND, 0)
        grid_sizer_horaires.Add(self.label_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_max, 0, wx.EXPAND, 0)
        grid_sizer_horaires.Add(self.bouton_appliquer_horaires, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(grid_sizer_horaires, 1, wx.EXPAND | wx.ALL, 0)

        # Largeur
        sizer_largeur = wx.BoxSizer(wx.HORIZONTAL)
        sizer_largeur.Add(self.img_largeur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_largeur.Add(self.slider_largeur, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 0)
        grid_sizer_options.Add(sizer_largeur, 1, wx.EXPAND, 0)

        # Hauteur
        sizer_hauteur = wx.BoxSizer(wx.HORIZONTAL)
        sizer_hauteur.Add(self.img_hauteur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_hauteur.Add(self.slider_hauteur, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 0)
        grid_sizer_options.Add(sizer_hauteur, 1, wx.EXPAND, 0)

        grid_sizer_options.AddGrowableCol(0)
        staticBox_Options.Add(grid_sizer_options, 1, wx.EXPAND | wx.ALL, 5)

        grid_sizer_base.Add(staticBox_Options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        self.Layout()

        # Init
        self.ctrl_heure_min.SetHeure("08:00")
        self.ctrl_heure_max.SetHeure("22:00")

        # Configuration
        dict_parametres = UTILS_Config.GetParametre("dlg_locations_tableau", {})
        if dict_parametres.has_key("periode") : self.ctrl_periode.SetModePeriode(dict_parametres["periode"])
        if dict_parametres.has_key("heure_min") : self.ctrl_heure_min.SetHeure(dict_parametres["heure_min"])
        if dict_parametres.has_key("heure_max") : self.ctrl_heure_max.SetHeure(dict_parametres["heure_max"])
        if dict_parametres.has_key("largeur") : self.slider_largeur.SetValue(dict_parametres["largeur"])
        if dict_parametres.has_key("hauteur") : self.slider_hauteur.SetValue(dict_parametres["hauteur"])

    def MemoriseConfig(self):
        dictParametres = {
            "periode" : self.ctrl_periode.GetModePeriode(),
            "heure_min": self.ctrl_heure_min.GetHeure(),
            "heure_max": self.ctrl_heure_max.GetHeure(),
            "largeur": self.slider_largeur.GetValue(),
            "hauteur": self.slider_hauteur.GetValue(),
            }
        UTILS_Config.SetParametre("dlg_locations_tableau", dictParametres)

    def MAJTableau(self):
        self.ctrl_tableau.MAJ(reinit_scroll=True)

    def OnCheckCategories(self, event):
        self.ctrl_tableau.MAJ()

    def OnBoutonHoraires(self, event):
        self.ctrl_tableau.MAJ()

    def GetDateDebut(self):
        return self.ctrl_periode.GetDateDebut()

    def GetDateFin(self):
        return self.ctrl_periode.GetDateFin()

    def GetCategories(self):
        return self.ctrl_categories.GetIDcoches()

    def GetHeureMin(self):
        heure = self.ctrl_heure_min.GetHeure()
        if heure == None or " " in heure :
            return None
        return heure

    def GetHeureMax(self):
        heure = self.ctrl_heure_max.GetHeure()
        if heure == None or " " in heure :
            return None
        return heure

    def GetLargeur(self):
        return self.slider_largeur.GetValue()

    def GetHauteur(self):
        return self.slider_hauteur.GetValue()

    def OnSliderLargeur(self, event):
        self.ctrl_tableau.SetLargeurColonne(self.slider_largeur.GetValue())

    def OnSliderHauteur(self, event):
        self.ctrl_tableau.SetHauteurLigne(self.slider_hauteur.GetValue())

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        # Contrôles
        self.ctrl_tableau = CTRL(panel)
        self.ctrl_options = CTRL_Options(panel, ctrl_tableau=self.ctrl_tableau)
        self.ctrl_tableau.ctrl_options = self.ctrl_options

        # Tests
        self.bouton_test = wx.Button(panel, -1, _(u"Bouton de test"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_options, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl_tableau, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((1200, 500))
        self.Layout()
        self.CenterOnScreen()

        # Init
        self.ctrl_tableau.MAJ()

    def OnBoutonTest(self, event):
        """ Bouton de test """
        self.ctrl_tableau.MAJ()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
