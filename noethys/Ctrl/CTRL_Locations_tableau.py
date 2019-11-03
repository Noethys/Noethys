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
import logging
import GestionDB
from dateutil import rrule
import six
import wx.lib.wordwrap as wordwrap
import wx.lib.agw.supertooltip as STT

from Utils import UTILS_Dates
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Couleurs




def GetTailleTexte(dc, texte, width):
    lignes = wordwrap.wordwrap(texte, width, dc, True)
    largeur_max = 0
    for ligne in lignes.split("\n") :
        largeur, hauteur, descent, externalLeading = dc.GetFullTextExtent(ligne)
        if largeur > largeur_max :
            largeur_max = largeur
    return lignes, largeur_max, (lignes.count("\n") + 1) * (hauteur + externalLeading)



class Barre(object):
    def __init__(self, parent=None, donnees=None):
        self.parent = parent

        liste_champs =["IDlocation", "IDfamille", "IDproduit", "observations",
                       "date_debut", "date_fin", "quantite"]

        for champ in liste_champs:
            if champ in donnees:
                setattr(self, champ, donnees[champ])
            else :
                setattr(self, champ, None)

        # Quantité
        if self.quantite == None :
            self.quantite = 1

        # Période
        if isinstance(self.date_debut, str) or isinstance(self.date_debut, six.text_type) :
            self.date_debut = datetime.datetime.strptime(self.date_debut, "%Y-%m-%d %H:%M:%S")

        if self.date_fin == None:
            self.date_fin = datetime.datetime(2999, 1, 1)

        if isinstance(self.date_fin, str) or isinstance(self.date_fin, six.text_type) :
            self.date_fin = datetime.datetime.strptime(self.date_fin, "%Y-%m-%d %H:%M:%S")

        # Récupération des réponses des questionnaires
        # for dictQuestion in grid.liste_questions :
        #     setattr(self, "question_%d" % dictQuestion["IDquestion"], grid.GetReponse(dictQuestion["IDquestion"], self.IDproduit))

        # Famille
        self.SetIDfamille(self.IDfamille)

        # Sousligne
        self.num_sousligne = 0
        self.rect = None
        self.poignees = None

    def SetIDfamille(self, IDfamille=None):
        self.IDfamille = IDfamille
        if self.IDfamille != None :
            self.nomTitulaires = self.parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.nomTitulaires = _(" ")


    def Modifier(self, event=None):
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self.parent, IDlocation=self.IDlocation, IDfamille=self.IDfamille)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_OK:
            self.parent.MAJ(select_location=self.IDlocation)

    def Supprimer(self, event=None):
        from Ol.OL_Locations import Supprimer_location
        resultat = Supprimer_location(self.parent, IDlocation=self.IDlocation)
        if resultat == True :
            self.parent.MAJ()

    def Dupliquer(self, event=None):
        DB = GestionDB.DB()

        # Duplication de la location
        conditions = "IDlocation=%d" % self.IDlocation
        dictModifications = {"date_saisie": datetime.date.today(),}
        newIDlocation = DB.Dupliquer("locations", "IDlocation", conditions, dictModifications)

        # Duplication de la prestation
        conditions = "IDdonnee=%d" % self.IDlocation
        dictModifications = {"IDdonnee": newIDlocation}
        newIDprestation = DB.Dupliquer("prestations", "IDlocation", conditions, dictModifications)

        DB.Close()
        self.parent.MAJ(select_location=newIDlocation)

    def Recopier(self, event=None):
        from Dlg import DLG_Saisie_lot_locations
        dlg = DLG_Saisie_lot_locations.Dialog(self.parent, IDlocation=self.IDlocation, periode=(self.parent.dict_options["date_debut"], self.parent.dict_options["date_fin"]))
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_OK:
            self.parent.MAJ(select_location=self.IDlocation)

    def GetTexteStatusBar(self):
        debut = UTILS_Dates.DatetimeEnFr(self.date_debut)
        if self.date_fin.year == 2999:
            fin = u"\nFin non définie"
        else:
            fin = UTILS_Dates.DatetimeEnFr(self.date_fin)
        texte = _(u"%s -> %s (de %s à %s)") % (self.nomTitulaires, self.parent.dict_produits[self.IDproduit]["nom"], debut, fin)
        return texte

    def Draw(self, dc=None, num_sousligne=1, rect_fenetre=None):

        # Recherche position left
        if self.date_debut.date() < self.parent.dict_options["date_debut"]:
            left = 0
        else :
            colonne = self.parent.dict_colonnes[self.date_debut.date()]
            left = colonne.num_colonne * self.parent.dict_options["case_largeur"]
            left += colonne.HeureEnPos(self.date_debut)

        # Recherche position right
        if self.date_fin.date() > self.parent.dict_options["date_fin"]:
            right = len(self.parent.dict_colonnes) * self.parent.dict_options["case_largeur"]
        else :
            colonne = self.parent.dict_colonnes[self.date_fin.date()]
            right = colonne.num_colonne * self.parent.dict_options["case_largeur"]
            right += colonne.HeureEnPos(self.date_fin)

        # Recherche position y
        hauteur = self.parent.dict_options["case_hauteur"]
        ligne = self.parent.dict_lignes[self.IDproduit]

        self.rect = None
        self.poignees = None

        if ligne.rect != None and ligne in self.parent.liste_lignes_affichees :

            y = ligne.rect.y + ((num_sousligne - 1) * hauteur)

            if left != None and right != None and y != None :
                largeur = right - left
                rect = wx.Rect(left + self.parent.delta[0], y, largeur, hauteur)
                rect.Deflate(0, 6)

                # Recherche si l'event doit apparaître dans le cadre
                if rect.Intersects(rect_fenetre) == True :

                    # Sélection de la couleur de barre
                    if self.IDfamille in self.parent.dict_couleurs:
                        self.couleur_barre = self.parent.dict_couleurs[self.IDfamille]
                    else:
                        self.couleur_barre = wx.Colour(random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
                        self.parent.dict_couleurs[self.IDfamille] = self.couleur_barre

                    # Application des couleurs
                    if self.parent.barre_selectionnee == self:
                        dc.SetPen(wx.Pen(wx.BLACK))
                    else :
                        dc.SetPen(wx.Pen(self.couleur_barre))
                    dc.SetBrush(wx.Brush(self.couleur_barre))
                    if 'phoenix' not in wx.PlatformInfo:
                        dc.DrawRectangleRect(rect)
                    else :
                        dc.DrawRectangle(rect)

                    # Affiche le nom de la barre
                    dc.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    dc.SetTextForeground((0, 0, 0))

                    texte = self.nomTitulaires

                    texte_largeur_max = rect.width
                    padding_h = 3
                    texte_x = rect.x + padding_h
                    if texte_x < rect_fenetre.x :
                        texte_x = rect_fenetre.x + padding_h
                        texte_largeur_max = rect.width + rect.x - rect_fenetre.x

                    texte, texte_largeur, texte_hauteur = GetTailleTexte(dc, texte, texte_largeur_max)
                    if "\n" in texte :
                        texte = texte.split("\n")[0]
                    dc.DrawText(texte, texte_x, rect.y)

                    # Affiche les heures
                    dc.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    couleur_heure = UTILS_Couleurs.ModifierLuminosite(self.couleur_barre, -70)

                    if self.parent.dict_options["date_debut"] <= self.date_debut.date() <= self.parent.dict_options["date_fin"]:
                        texte_debut = self.date_debut.strftime("%Hh%M")
                    else :
                        texte_debut = ""

                    texte_debut_largeur, texte_hauteur, descent, externalLeading = dc.GetFullTextExtent(texte_debut)
                    #texte_debut, texte_debut_largeur, texte_hauteur = GetTailleTexte(dc, texte_debut, texte_largeur_max)
                    texte_fin = self.date_fin.strftime("%Hh%M")
                    if self.date_fin.year == 2999:
                        texte_fin = _(u"Illimitée")
                    else :
                        if self.parent.dict_options["date_debut"] <= self.date_fin.date() <= self.parent.dict_options["date_fin"]:
                            texte_fin = self.date_fin.strftime("%Hh%M")
                        else:
                            texte_fin = ""

                    texte_fin_largeur, texte_hauteur, descent, externalLeading = dc.GetFullTextExtent(texte_fin)
                    #texte_fin, texte_fin_largeur, texte_hauteur = GetTailleTexte(dc, texte_fin, texte_largeur_max)

                    if texte_debut_largeur + texte_fin_largeur + padding_h * 3 < texte_largeur_max :

                        dc.SetTextForeground(couleur_heure)
                        dc.DrawText(texte_debut, rect.x + padding_h, rect.bottom - texte_hauteur)

                        dc.SetTextForeground(couleur_heure)
                        dc.DrawText(texte_fin, rect.right - texte_fin_largeur - padding_h, rect.bottom - texte_hauteur)


                    # Poignées
                    if self.parent.barre_selectionnee == self :
                        dc.SetPen(wx.Pen(wx.BLACK))
                        dc.SetBrush(wx.Brush(wx.BLACK))
                        taille_poignee = 5

                        y = rect.y + rect.height/2.0 - taille_poignee / 2.0
                        x = rect.X
                        self.poignees = {}

                        if self.parent.dict_options["date_debut"] <= self.date_debut.date() <= self.parent.dict_options["date_fin"]:
                            self.poignees["gauche"] = wx.Rect(x, y, taille_poignee, taille_poignee)
                        if self.parent.dict_options["date_debut"] <= self.date_fin.date() <= self.parent.dict_options["date_fin"] :
                            self.poignees["centre"] = wx.Rect(x + rect.Width / 2, y, taille_poignee, taille_poignee)
                            self.poignees["droite"] = wx.Rect(x + rect.Width - taille_poignee, y, taille_poignee, taille_poignee)

                        dc.SetBrush(wx.Brush("BLACK", wx.SOLID))
                        dc.SetPen(wx.Pen("BLACK", 1, wx.SOLID))
                        for nom, rect_poignee in self.poignees.items() :
                            radius = 0
                            if 'phoenix' in wx.PlatformInfo:
                                dc.DrawRoundedRectangle(rect_poignee, radius)
                            else:
                                dc.DrawRoundedRectangleRect(rect_poignee, radius)

                self.rect = rect

    def FindPoignee(self, x=None, y=None):
        if self.poignees != None :
            for nom, rect_poignee in self.poignees.items():
                rect_poignee.Inflate(5, 5)
                if 'phoenix' in wx.PlatformInfo:
                    contains = rect_poignee.Contains(x, y)
                else:
                    contains = rect_poignee.ContainsXY(x, y)
                if contains == True :
                    return nom
        return None






class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.dict_options = {
            "entete_colonne_hauteur" : 50,
            "entete_ligne_largeur" : 200,
            "case_hauteur" : 50,
            "case_largeur" : 440,
            "date_debut" : datetime.date(2018, 1, 1),
            "date_fin": datetime.date(2018, 1, 31),
            "heure_min" : UTILS_Dates.HeureStrEnTime("14:00"),
            "heure_max": UTILS_Dates.HeureStrEnTime("18:00"),
            "categories" : [1, 2, 3, 4, 5, 6],
            "couleur_bordure" : wx.Colour(200, 200, 200),
            "temps_arrondi" : UTILS_Dates.HeureStrEnTime("00:30"),
            "barre_duree_minimale" : UTILS_Dates.HeureStrEnTime("00:30"),
            "autoriser_changement_ligne" : True,
        }

        # Contrôles
        self.ctrl_tableau = CTRL_Tableau(self)
        self.ctrl_infos_1 = CTRL_Infos(self, titre=_(u"POSITION"), min_size=(-1, 20), style=wx.BORDER_THEME)
        self.ctrl_infos_2 = CTRL_Infos(self, titre=_(u"SELECTION"), min_size=(-1, 20), style=wx.BORDER_THEME)
        self.image_zoom_moins = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_moins.png"), wx.BITMAP_TYPE_ANY))
        self.slider_largeur = wx.Slider(self, -1,  value=self.dict_options["case_largeur"], minValue=25, maxValue=1000, size=(-1, -1), style=wx.SL_HORIZONTAL)
        self.image_zoom_plus = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_plus.png"), wx.BITMAP_TYPE_ANY))

        self.slider_largeur.SetMinSize((200, -1))
        self.Bind(wx.EVT_SCROLL, self.OnSliderLargeur, self.slider_largeur)

        self.scrollbar_h = wx.ScrollBar(self, -1, size=(-1, -1), style=wx.SB_HORIZONTAL)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.OnScrollH, self.scrollbar_h)

        self.scrollbar_v = wx.ScrollBar(self, -1, size=(-1, -1), style=wx.SB_VERTICAL)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.OnScrollV, self.scrollbar_v)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)

        grid_sizer_haut = wx.FlexGridSizer(rows=2, cols=2, vgap=0, hgap=0)
        grid_sizer_haut.Add(self.ctrl_tableau, 1, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.scrollbar_v, 1, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.scrollbar_h, 1, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=0)
        grid_sizer_bas.Add(self.ctrl_infos_1, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.ctrl_infos_2, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add((10, 5), 1, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.image_zoom_moins, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        grid_sizer_bas.Add(self.slider_largeur, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.image_zoom_plus, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_bas.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.EXPAND | wx.TOP, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnSliderLargeur(self, event=None):
        self.SetOption("case_largeur", self.slider_largeur.GetValue())
        self.ctrl_tableau.MAJ(reinit_scroll_h=True)

    def SetOption(self, option="", valeur=None, maj=False):
        if option in ("heure_min", "heure_max", "temps_arrondi", "barre_duree_minimale"):
            valeur = UTILS_Dates.HeureStrEnTime(valeur)
        self.dict_options[option] = valeur

        if maj == True :
            self.ctrl_tableau.MAJ(reinit_scroll_h=True, reinit_scroll_v=True)

    def OnScrollH(self, event=None):
        valeur = self.scrollbar_h.GetThumbPosition() * self.dict_options["case_largeur"]
        self.ctrl_tableau.SetDelta(h=-valeur)
        self.ctrl_tableau.Redraw()

    def OnScrollV(self, event=None):
        valeur = self.scrollbar_v.GetThumbPosition() * self.dict_options["case_hauteur"]
        self.ctrl_tableau.SetDelta(v=-valeur)
        self.ctrl_tableau.Redraw()

    def AjusteScrollbars(self, h=True, v=True):
        largeur_reelle, hauteur_reelle = self.ctrl_tableau.GetSize()

        if h == True :
            self.ctrl_tableau.SetDelta(h=0)
            nbre_colonnes = (1 + len(self.ctrl_tableau.liste_colonnes))
            nbre_colonnes_visibles = 1 + largeur_reelle / self.dict_options["case_largeur"]
            self.scrollbar_h.SetScrollbar(0, nbre_colonnes_visibles, nbre_colonnes, nbre_colonnes_visibles)

        if v == True :
            self.ctrl_tableau.SetDelta(v=0)

            nbre_lignes_total = 0
            for ligne in self.ctrl_tableau.liste_lignes:
                # Recherche s'il existe des souslignes
                if ligne.dict_produit["IDproduit"] in self.ctrl_tableau.dict_lignes_barres:
                    nbre = len(self.ctrl_tableau.dict_lignes_barres[ligne.dict_produit["IDproduit"]])
                else:
                    nbre = 1
                nbre_lignes_total += nbre

            nbre_lignes_visibles = (hauteur_reelle / self.dict_options["case_hauteur"])
            self.scrollbar_v.SetScrollbar(0, nbre_lignes_visibles, nbre_lignes_total+1, nbre_lignes_visibles)

    def SetWheel(self, valeur=0):
        position_actuelle = self.scrollbar_v.GetThumbPosition()
        step = self.dict_options["case_hauteur"] * 0.05
        self.scrollbar_v.SetThumbPosition(position_actuelle - step * valeur)
        self.OnScrollV()

    def MAJ(self, reinit_scroll_h=False, reinit_scroll_v=False):
        self.ctrl_tableau.MAJ(reinit_scroll_h, reinit_scroll_v)

    def Redraw(self):
        self.ctrl_tableau.Redraw()


class Colonne(object):
    def __init__(self, parent=None, num_colonne=None, date=None):
        self.parent = parent
        self.num_colonne = num_colonne
        self.date = date
        self.dict_options = self.parent.dict_options
        self.rect = None

    def HeureEnPos(self, heure):
        if heure.time() < self.dict_options["heure_min"] :
            return 0
        if heure.time() > self.dict_options["heure_max"] :
            return 1.0 * self.dict_options["case_largeur"]
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.dict_options["heure_max"], self.dict_options["heure_min"])
        return 1.0 * UTILS_Dates.SoustractionHeures(heure, self.dict_options["heure_min"]).seconds / tempsAffichable.seconds * self.dict_options["case_largeur"]

    def PosEnHeure(self, x):
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.dict_options["heure_max"], self.dict_options["heure_min"])
        pos = x - self.rect.x
        temp = datetime.timedelta(seconds=1.0 * pos / self.dict_options["case_largeur"] * tempsAffichable.seconds)
        heure = UTILS_Dates.AdditionHeures(self.dict_options["heure_min"], temp)
        time = UTILS_Dates.DeltaEnTime(heure)
        return datetime.datetime(self.date.year, self.date.month, self.date.day, time.hour, time.minute)

    def AssembleDateEtHeure(self, date=None, heure=None):
        return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=heure.hour, minute=heure.minute)

    def Draw(self, dc=None, rect=None):
        self.rect = rect

        # Bordure de la case
        dc.SetPen(wx.Pen(self.dict_options["couleur_bordure"]))
        dc.DrawLine(rect.right, rect.top, rect.right, rect.bottom)
        dc.DrawLine(rect.left, rect.top, rect.right, rect.top)
        dc.DrawLine(rect.left, rect.bottom, rect.right + 1, rect.bottom)

        # Graduations
        dc.SetPen(wx.Pen("black"))
        dc.SetTextForeground("black")
        dc.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))

        dtmin = self.AssembleDateEtHeure(self.date, self.dict_options["heure_min"])
        dtmax = self.AssembleDateEtHeure(self.date, self.dict_options["heure_max"])

        listeGraduations = list(rrule.rrule(rrule.MINUTELY, byminute=(0, 15, 30, 45), dtstart=dtmin, until=dtmax))
        ecartGraduations = 1.0 * self.dict_options["case_largeur"] / len(listeGraduations)

        hauteurGraduations = 0
        if ecartGraduations > 2 :
            index = 0
            for dt in listeGraduations :
                x = self.HeureEnPos(dt)
                posY = rect.height - 17
                hautTraitHeures = 4
                hautTexte = 12
                if dt.minute == 0:
                    hauteurTrait = hautTraitHeures
                    texte = "%dh" % dt.hour
                    largTexte, hautTexte = dc.GetTextExtent(texte)
                    if ecartGraduations > 5 :
                        x_texte = x - (largTexte / 2) + rect.x
                        if x_texte - largTexte > rect.x and x_texte + largTexte < rect.right :
                            dc.DrawText(texte, x_texte, posY + 2)
                        hauteurGraduations = 10
                    else :
                        hauteurGraduations = 4
                elif dt.minute in (15, 45):
                    hauteurTrait = 1
                elif dt.minute == 30:
                    hauteurTrait = 2.5
                if x > 2 and x < rect.width - 2 :
                    dc.DrawLine(x + rect.x, posY + hautTexte + hautTraitHeures - hauteurTrait, x + rect.x, posY + hautTexte + hautTraitHeures)
                index += 1

        # Label
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.SetTextForeground("black")
        if self.date == datetime.date.today() :
            dc.SetTextForeground("red")

        # Définit le texte du label
        if self.dict_options["case_largeur"] < 80 :
            texte = str(self.date.day)
        elif self.dict_options["case_largeur"] < 120 :
            texte = UTILS_Dates.DateEngFr(self.date)
        elif self.dict_options["case_largeur"] < 170 :
            texte = UTILS_Dates.DateComplete(self.date, abrege=True)
        else :
            texte = UTILS_Dates.DateComplete(self.date, abrege=False)

        # Recherche taille du label
        texte, largTexte, hautTexte = GetTailleTexte(dc, texte, rect.width)
        x = rect.width / 2.0 - largTexte / 2.0 + rect.x
        y = rect.height / 2.0 - hautTexte / 2.0 - hauteurGraduations
        dc.DrawText(texte, x, y)


class Ligne(object):
    def __init__(self, parent, num_ligne=None, dict_produit=None):
        self.parent = parent
        self.num_ligne = num_ligne
        self.dict_produit = dict_produit
        self.dict_options = self.parent.dict_options
        self.rect = None

    def Draw(self, dc=None, rect=None):
        self.rect = rect

        # Bordure de la case
        dc.SetPen(wx.Pen(self.dict_options["couleur_bordure"]))
        dc.DrawLine(rect.left, rect.top, rect.left, rect.bottom+1)
        dc.DrawLine(rect.right, rect.top, rect.right, rect.bottom)
        dc.DrawLine(rect.right, rect.bottom, rect.left, rect.bottom)

        # Label
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.SetTextForeground("black")

        # Recherche taille du label
        texte = self.dict_produit["nom"]
        texte, largTexte, hautTexte = GetTailleTexte(dc, texte, rect.width)
        x = rect.x + rect.width / 2.0 - largTexte / 2.0
        y = rect.y + rect.height / 2.0 - hautTexte / 2.0
        dc.DrawText(texte, x, y)







# --------------------------------------------------------------------------------

class CTRL_Tableau(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1)
        self.parent = parent
        self.delta = [0, 0]

        self.liste_barres = []
        self.liste_colonnes = []
        self.dict_colonnes = {}
        self.dict_couleurs = {}
        self.liste_lignes = []
        self.dict_options = self.parent.dict_options

        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.CreateBuffer()

        # Pour impression
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printData.SetOrientation(wx.LANDSCAPE)

        # Init Tooltip
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip après 10 secs
        self.SetToolTip(wx.ToolTip(""))

        # Variables
        self.barre_selectionnee = None
        self.barre_survolee = None
        self.dragging = None

        # Binds
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDoubleClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)


    def GetReponse(self, IDquestion=None, ID=None):
        if IDquestion in self.dict_questionnaires :
            if ID in self.dict_questionnaires[IDquestion] :
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
        liste_categories = self.dict_options["categories"]
        if len(liste_categories) == 0: conditionCategories = "()"
        elif len(liste_categories) == 1: conditionCategories = "(%d)" % liste_categories[0]
        else: conditionCategories = str(tuple(liste_categories))

        # Importation des produits
        DB = GestionDB.DB()
        req = """SELECT IDproduit, produits.nom, produits_categories.nom
        FROM produits
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE produits.IDcategorie IN %s
        ORDER BY produits.nom;""" % conditionCategories
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.liste_produits = []
        self.dict_produits = {}
        for item in listeDonnees :
            dict_temp = {"IDproduit" : item[0], "nom" : item[1], "nom_categorie" : item[2]}
            self.liste_produits.append(dict_temp)
            self.dict_produits[item[0]] = dict_temp

        # Importation des locations
        date_debut = self.dict_options["date_debut"]
        date_fin = self.dict_options["date_fin"]
        if date_debut == None or date_fin == None :
            return

        req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin, locations.quantite
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE produits.IDcategorie IN %s AND locations.date_debut <= '%s 23:55:00' AND (locations.date_fin >= '%s' OR locations.date_fin IS NULL)
        ORDER BY locations.date_debut;""" % (conditionCategories, date_fin, date_debut)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.liste_barres = []

        for IDlocation, IDfamille, IDproduit, observations, date_debut, date_fin, quantite in listeDonnees :
            item = {"IDlocation" : IDlocation, "IDfamille" : IDfamille, "IDproduit" : IDproduit, "observations" : observations,
                    "date_debut" : date_debut, "date_fin": date_fin, "quantite" : quantite}

            barre = Barre(self, donnees=item)
            self.liste_barres.append(barre)

    def MAJ(self, reinit_scroll_h=False, reinit_scroll_v=False, select_location=None):
        # Importation
        self.Importation()

        # Mémorise la position du scroll
        # posScrollH = self.parent.scrollbar_h.GetScrollPos(wx.HORIZONTAL)
        # posScrollV = self.parent.scrollbar_v.GetScrollPos(wx.VERTICAL)

        # Création des colonnes
        date_debut = self.dict_options["date_debut"]
        date_fin = self.dict_options["date_fin"]
        if date_debut == None or date_fin == None :
            return

        heure_min = self.dict_options["heure_min"]
        heure_max = self.dict_options["heure_max"]
        if heure_min == None or heure_max == None or heure_min >= heure_max :
            return

        self.MAJ_colonnes()
        self.MAJ_lignes()

        # self.parent.scrollbar_h.SetScrollPos(wx.HORIZONTAL, posScrollH)
        # self.parent.scrollbar_v.SetScrollPos(wx.VERTICAL, posScrollV)

        self.parent.ctrl_infos_2.SetTexte("")

        # Sélection selon IDlocation
        if select_location != None:
            for barre in self.liste_barres:
                if barre.IDlocation == select_location:
                    self.barre_selectionnee = barre
                    self.MajTexteInfos2()
                    break

        # Ajustement des scrollbars
        self.dict_lignes_barres = self.CalcSouslignes()
        self.parent.AjusteScrollbars(h=reinit_scroll_h, v=reinit_scroll_v)

        # Redessine le tableau
        self.Redraw()

    def CreateBuffer(self):
        if 'phoenix' in wx.PlatformInfo:
            width, height = self.GetSize()
            self.bgbuf = wx.Bitmap(width, height)
        else :
            width, height = self.GetSizeTuple()
            self.bgbuf = wx.EmptyBitmap(width, height)

    def OnLeaveWindow(self, event):
        self.SetCurseur(None)
        self.dragging = None
        self.parent.ctrl_infos_1.SetTexte("")
        self.ActiveTooltip(False)

    def OnLeftUp(self, event):
        if self.dragging != None :
            barre = self.dragging["barre"]

            if self.dragging["nouvelle_barre"] == True:
                # Si nouvelle barre
                from Dlg import DLG_Saisie_location
                dlg = DLG_Saisie_location.Dialog(self, IDproduit=barre.IDproduit)
                dlg.SetDebut(barre.date_debut)
                dlg.SetFin(barre.date_fin)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_OK:
                    self.MAJ()
                else :
                    del self.liste_barres[-1]
                    self.Redraw()
            else:
                # Si barre existante
                self.SaveBarre(barre)

        # Stoppe le dragging
        self.dragging = None

    def OnLeftClick(self, event):
        x, y = self.ScreenToClient(wx.GetMousePosition())
        self.ActiveTooltip(actif=False)

        # Recherche la barre survolée
        barre = self.FindBarre(x, y)

        texte_infos = ""
        if barre != None :
            self.barre_selectionnee = barre
        else :
            self.barre_selectionnee = None

        self.MajTexteInfos2()

        self.Redraw()

    def MajTexteInfos2(self):
        if self.barre_selectionnee != None:
            date_debut = self.barre_selectionnee.date_debut.strftime("%d/%m/%Y %Hh%M")
            if self.barre_selectionnee.date_fin.year == 2999 :
                date_fin = _(u"Illimitée")
                duree = ""
            else :
                date_fin = self.barre_selectionnee.date_fin.strftime("%d/%m/%Y %Hh%M")
                duree = u"(%s) " % UTILS_Dates.FormatDelta(self.barre_selectionnee.date_fin - self.barre_selectionnee.date_debut)
            if self.barre_selectionnee.IDproduit in self.dict_produits:
                nom_produit = self.dict_produits[self.barre_selectionnee.IDproduit]["nom"]
            else :
                nom_produit = ""

            texte_infos = u"%s > %s %s: %s" % (date_debut, date_fin, duree, nom_produit)
        else :
            texte_infos = ""
        self.parent.ctrl_infos_2.SetTexte(texte_infos)


    def OnRightClick(self, event):
        x, y = self.ScreenToClient(wx.GetMousePosition())
        self.ActiveTooltip(actif=False)

        case = self.FindCase(x, y)

        if case != None :

            menuPop = UTILS_Adaptations.Menu()

            # Item Ajouter
            self.memoire = {"IDproduit" : case[0].dict_produit["IDproduit"], "heure_debut" : case[1].PosEnHeure(x)}

            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

            barre = self.FindBarre(x, y)
            if barre != None:

                menuPop.AppendSeparator()

                # Item Ajouter
                item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, barre.Modifier, id=20)

                # Item Supprimer
                item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, barre.Supprimer, id=30)

                menuPop.AppendSeparator()

                # Item Dupliquer
                item = wx.MenuItem(menuPop, 40, _(u"Dupliquer"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, barre.Dupliquer, id=40)

                menuPop.AppendSeparator()

                # Item Recopier
                item = wx.MenuItem(menuPop, 50, _(u"Recopier sur plusieurs dates"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, barre.Recopier, id=50)

            self.PopupMenu(menuPop)
            menuPop.Destroy()

    def OnLeftDoubleClick(self, event):
        x, y = self.ScreenToClient(wx.GetMousePosition())
        self.ActiveTooltip(actif=False)

        case = self.FindCase(x, y)
        barre = self.FindBarre(x, y)
        if barre != None :
            barre.Modifier()
        else :
            if case != None:
                IDproduit = case[0].dict_produit["IDproduit"]
                heure = case[1].PosEnHeure(x)
                self.Ajouter(IDproduit=IDproduit, heure_debut=heure)

    def Ajouter(self, event=None, IDproduit=None, heure_debut=None):
        if event != None :
            IDproduit = self.memoire["IDproduit"]
            heure_debut = self.memoire["heure_debut"]

        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDproduit=IDproduit)
        dlg.SetDebut(heure_debut)
        reponse = dlg.ShowModal()
        IDlocation = dlg.GetIDlocation()
        dlg.Destroy()
        if reponse == wx.ID_OK:
            self.MAJ(select_location=IDlocation)

    def SetCurseur(self, region=None):
        """ Change la forme du curseur lors d'un dragging """
        if 'phoenix' in wx.PlatformInfo:
            cursor = wx.Cursor
        else :
            cursor = wx.StockCursor
        if region == "gauche" or region == "droite" :
            self.SetCursor(cursor(wx.CURSOR_SIZEWE))
        elif region == "centre":
            self.SetCursor(cursor(wx.CURSOR_SIZING))
        else :
            self.SetCursor(cursor(wx.CURSOR_ARROW))

    def OnMotion(self, event=None):
        x, y = self.ScreenToClient(wx.GetMousePosition())

        if self.dragging != None and self.dragging["region"] in ("gauche", "droite"):
            x += self.dragging["ecart"]

        # Recherche la case survolée
        heure = None
        IDproduit = None
        texte_infos = ""
        case = self.FindCase(x, y)
        if case != None :
            IDproduit = case[0].dict_produit["IDproduit"]
            nomProduit = case[0].dict_produit["nom"]
            heure = case[1].PosEnHeure(x)
            heure = UTILS_Dates.ArrondirDT(heure, UTILS_Dates.TimeEnDelta(self.dict_options["temps_arrondi"]))
            texte_infos = u"%s : %s" % (heure.strftime("%d/%m/%Y %Hh%M"), nomProduit)
        self.parent.ctrl_infos_1.SetTexte(texte_infos)

        # Recherche la barre survolée
        barre = self.FindBarre(x, y)

        # Tooltip
        if barre != None and self.dragging == None :
            if barre != self.barre_survolee :
                self.ActiveTooltip(actif=False)
                self.ActiveTooltip(actif=True, barre=barre)
        else:
            self.ActiveTooltip(actif=False)

        # Mémorise la barre survolée
        region = None
        if barre != None :
            self.barre_survolee = barre
            region = barre.FindPoignee(x, y)
        else :
            self.barre_survolee = None

        # Création d'une nouvelle barre
        nouvelle_barre = False
        if self.barre_selectionnee == None and heure != None and wx.GetKeyState(wx.WXK_CONTROL) and wx.GetMouseState().LeftIsDown():
            barre = Barre(self, donnees={"IDproduit": IDproduit, "date_debut": heure, "date_fin": heure + datetime.timedelta(minutes=10)})
            self.liste_barres.append(barre)
            region = "droite"
            self.barre_selectionnee = barre
            nouvelle_barre = True
            self.Redraw()
            # Déplace la souris vers la poignée droite
            x_poignee_droite = barre.poignees["droite"].left + barre.poignees["droite"].width / 2
            y_poignee_droite = barre.poignees["droite"].bottom + barre.poignees["droite"].height / 2
            self.WarpPointer(x_poignee_droite, y_poignee_droite)

        # Dragging
        if heure != None and wx.GetMouseState().LeftIsDown():

            # Arrondir l'heure
            # heure = UTILS_Dates.ArrondirDT(heure, datetime.timedelta(minutes=self.dict_options["arrondi_minutes"]))

            # Appliquer dragging
            if self.dragging != None :
                region = self.dragging["region"]

                if region == "gauche" and self.dragging["barre"].date_fin - heure >= UTILS_Dates.TimeEnDelta(self.dict_options["barre_duree_minimale"]):
                    self.dragging["barre"].date_debut = heure

                if region == "droite"  and heure - self.dragging["barre"].date_debut >= UTILS_Dates.TimeEnDelta(self.dict_options["barre_duree_minimale"]):
                    self.dragging["barre"].date_fin = heure

                if region == "centre" :
                    # Déplacement latéral
                    self.dragging["barre"].date_debut = heure - self.dragging["delta_heure"]
                    self.dragging["barre"].date_fin = self.dragging["barre"].date_debut + self.dragging["duree"]

                    # Déplacement vertical : Changement de ligne (de produit)
                    if self.dict_options["autoriser_changement_ligne"] == True :
                        self.dragging["barre"].IDproduit = IDproduit

            # Initialisation du dragging
            if self.dragging == None and barre != None :
                delta_heure = heure - barre.date_debut
                duree = barre.date_fin - barre.date_debut
                if region == "gauche":
                    ecart = barre.rect.left - x
                elif region == "droite":
                    ecart = barre.rect.right - x
                else:
                    ecart = 0
                self.dragging = {"barre" : barre, "nouvelle_barre" : nouvelle_barre, "region" : region, "ecart" : ecart, "delta_heure" : delta_heure, "duree" : duree, "rect" : barre.rect}

        if self.barre_selectionnee != None:
            self.MajTexteInfos2()

        # Applique le curseur
        self.SetCurseur(region)

        self.Redraw()

    def FindCase(self, x=None, y=None):
        # Recherche la colonnne
        colonne = None
        if x > self.dict_options["entete_ligne_largeur"]:
            for col in self.liste_colonnes_affichees:
                if col.rect.left < x < col.rect.right :
                    colonne = col
                    break

        # Recherche la ligne
        ligne = None
        if y > self.dict_options["entete_colonne_hauteur"]:
            for li in self.liste_lignes_affichees:
                if li.rect.top < y < li.rect.bottom :
                    ligne = li
                    break

        if ligne != None and colonne != None :
            return (ligne, colonne)
        return None

    def FindBarre(self, x=None, y=None):
        for barre in self.liste_barres:
            if barre.rect != None :
                if 'phoenix' in wx.PlatformInfo:
                    contains = barre.rect.Contains(x, y)
                else:
                    contains = barre.rect.ContainsXY(x, y)
                if contains == True :
                    return barre
        return None

    def OnSize(self, event):
        self.parent.AjusteScrollbars()
        self.CreateBuffer()
        self.Redraw()

    def OnMouseWheel(self, event):
        valeur = event.GetWheelRotation() / 120.0
        self.parent.SetWheel(valeur)
        self.OnMotion()

    def OnEraseBackground(self, event):
        pass

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self.bgbuf, 0, 0, True)
        event.Skip()

    def Redraw(self):
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.bgbuf)
        memdc.SetBackground(wx.Brush(wx.WHITE, wx.SOLID))
        memdc.Clear()
        self.DoDrawing(memdc)
        del memdc
        self.Refresh()
        self.Update()

    def SetDelta(self, h=None, v=None):
        if h != None :
            self.delta[0] = h + self.dict_options["entete_ligne_largeur"]
        if v != None :
            self.delta[1] = v + self.dict_options["entete_colonne_hauteur"]

    def CalcSouslignes(self):
        # Regroupe les barres par produit
        dict_barres_par_produit = {}
        for barre in self.liste_barres :
            if (barre.IDproduit in dict_barres_par_produit) == False :
                dict_barres_par_produit[barre.IDproduit] = []
            dict_barres_par_produit[barre.IDproduit].append(barre)

        # Place les barres sur chaque ligne
        dict_barres = {}
        for IDproduit, liste_barres in dict_barres_par_produit.items() :
            dict_barres[IDproduit] = {}
            liste_barres_traitees = []
            for num_ligne in range(1, len(liste_barres)+1):
                for barre in liste_barres:
                    if barre not in liste_barres_traitees:
                        overlap = False
                        if num_ligne in dict_barres[IDproduit]:
                            for barre_temp in dict_barres[IDproduit][num_ligne]:
                                if barre.date_debut < barre_temp.date_fin and barre.date_fin > barre_temp.date_debut:
                                    overlap = True
                        if overlap == False:
                            if (num_ligne in dict_barres[IDproduit]) == False:
                                dict_barres[IDproduit][num_ligne] = []
                            dict_barres[IDproduit][num_ligne].append(barre)
                            liste_barres_traitees.append(barre)

        return dict_barres


    def DoDrawing(self, dc):
        # Calcule les sous-lignes
        self.dict_lignes_barres = self.CalcSouslignes()

        # Dessine les entetes
        self.Draw_entetes_colonnes(dc)
        self.Draw_entetes_lignes(dc)

        # Calcule la taille de la fenetre affichée
        if 'phoenix' not in wx.PlatformInfo:
            taille_fenetre = self.GetClientSizeTuple()
        else :
            taille_fenetre = self.GetClientSize()
        x_fenetre = self.dict_options["entete_ligne_largeur"]
        y_fenetre = self.dict_options["entete_colonne_hauteur"]
        largeur_fenetre = taille_fenetre[0] - x_fenetre
        hauteur_fenetre = taille_fenetre[1] - y_fenetre
        rect_cadre_central = wx.Rect(x_fenetre, y_fenetre, largeur_fenetre, hauteur_fenetre)

        if 'phoenix' in wx.PlatformInfo:
            dc.SetClippingRegion(rect_cadre_central)
        else:
            dc.SetClippingRect(rect_cadre_central)

        # Dessine la grille de fond
        liste_traits_grille = []

        if len(self.liste_lignes_affichees) > 0 :
            for colonne in self.liste_colonnes_affichees :
                liste_traits_grille.append((colonne.rect.right, 0, colonne.rect.right, max([ligne.rect.bottom for ligne in self.liste_lignes_affichees])))

        if len(self.liste_colonnes_affichees) > 0 :
            for ligne in self.liste_lignes_affichees :
                liste_traits_grille.append((0, ligne.rect.bottom, max([colonne.rect.right for colonne in self.liste_colonnes_affichees]), ligne.rect.bottom))

        dc.SetPen(wx.Pen(self.dict_options["couleur_bordure"]))
        dc.DrawLineList(liste_traits_grille)

        # Dessine les barres
        #for barre in self.parent.liste_barres :
        for IDproduit, dict_souslignes in self.dict_lignes_barres.items():
            for num_sousligne, liste_barres in dict_souslignes.items():
                for barre in liste_barres :
                    barre.Draw(dc, num_sousligne, rect_cadre_central)

        dc.DestroyClippingRegion()


    def MAJ_colonnes(self):
        # Création des colonnes
        self.liste_colonnes = []
        self.dict_colonnes = {}
        liste_dates = list(rrule.rrule(rrule.DAILY, dtstart=self.dict_options["date_debut"], until=self.dict_options["date_fin"]))
        num_colonne = 0
        for date in liste_dates:
            colonne = Colonne(self, num_colonne=num_colonne, date=date.date())
            self.liste_colonnes.append(colonne)
            self.dict_colonnes[date.date()] = colonne
            num_colonne += 1


    def Draw_entetes_colonnes(self, dc):
        taille_fenetre = self.GetSize()
        fenetre_x = self.dict_options["entete_ligne_largeur"]
        fenetre_y = 0
        fenetre_largeur = taille_fenetre[0] - fenetre_x
        fenetre_hauteur = self.dict_options["entete_colonne_hauteur"]

        rect_fenetre = wx.Rect(fenetre_x, fenetre_y, fenetre_largeur+2, fenetre_hauteur)

        if 'phoenix' in wx.PlatformInfo:
            dc.SetClippingRegion(rect_fenetre)
        else:
            dc.SetClippingRect(rect_fenetre)

        dc.SetPen(wx.Pen(self.dict_options["couleur_bordure"]))
        dc.DrawLine(rect_fenetre.left, rect_fenetre.top, rect_fenetre.left, rect_fenetre.bottom)

        self.liste_colonnes_affichees = []
        num_colonne = 0
        for colonne in self.liste_colonnes :
            x = (num_colonne * self.dict_options["case_largeur"]) + self.delta[0]
            y = 0
            rect = wx.Rect(x, y, self.dict_options["case_largeur"], self.dict_options["entete_colonne_hauteur"])

            # Dessin de la colonne
            if rect.Intersects(rect_fenetre):
                colonne.Draw(dc, rect)
                self.liste_colonnes_affichees.append(colonne)
            num_colonne += 1

        dc.DestroyClippingRegion()


    def MAJ_lignes(self):
        # Création des lignes
        self.liste_lignes = []
        self.dict_lignes = {}
        num_ligne = 0
        for dict_produit in self.liste_produits:
            ligne = Ligne(self, num_ligne=num_ligne, dict_produit=dict_produit)
            self.liste_lignes.append(ligne)
            self.dict_lignes[dict_produit["IDproduit"]] = ligne
            num_ligne += 1

    def Draw_entetes_lignes(self, dc):
        taille_fenetre = self.GetSize()
        fenetre_x = 0
        fenetre_y = self.dict_options["entete_colonne_hauteur"]
        fenetre_largeur = self.dict_options["entete_ligne_largeur"]
        fenetre_hauteur = taille_fenetre[1] - fenetre_y

        rect_fenetre = wx.Rect(fenetre_x, fenetre_y, fenetre_largeur, fenetre_hauteur)

        if 'phoenix' in wx.PlatformInfo:
            dc.SetClippingRegion(rect_fenetre)
        else:
            dc.SetClippingRect(rect_fenetre)

        dc.SetPen(wx.Pen(self.dict_options["couleur_bordure"]))
        dc.DrawLine(rect_fenetre.left, rect_fenetre.top, rect_fenetre.right, rect_fenetre.top)

        self.liste_lignes_affichees = []

        y = self.delta[1]
        for ligne in self.liste_lignes :
            # Recherche s'il existe des souslignes
            if ligne.dict_produit["IDproduit"] in self.dict_lignes_barres:
                nbre_souslignes = len(self.dict_lignes_barres[ligne.dict_produit["IDproduit"]])
            else :
                nbre_souslignes = 1

            x = 0
            hauteur = self.parent.dict_options["case_hauteur"] * nbre_souslignes
            rect = wx.Rect(x, y, self.dict_options["entete_ligne_largeur"], hauteur)

            # Dessin de la colonne
            if rect.Intersects(rect_fenetre):
                ligne.Draw(dc, rect)
                self.liste_lignes_affichees.append(ligne)

            # Prépare prochaine ligne
            y += hauteur

        dc.DestroyClippingRegion()


    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try:
                self.tipFrame.Destroy()
                del self.tipFrame
            except:
                pass

    def ActiveTooltip(self, actif=True, barre=None):
        if actif == True:
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False:
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(800)
                self.tip.barre = barre
        else:
            # Désactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.track_location = None
            self.CacheTooltip()
            self.barre_survolee = None

    def AfficheTooltip(self):
        """ Création du supertooltip """
        barre = self.tip.barre

        # Paramétrage du tooltip
        font = self.GetFont()
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))

        if barre != None :
            couleur = barre.couleur_barre
        else :
            couleur = wx.Colour(255, 255, 255)
        self.tip.SetTopGradientColour(couleur)
        self.tip.SetMiddleGradientColour(wx.Colour(255, 255, 255))
        self.tip.SetBottomGradientColour(wx.Colour(255, 255, 255))
        self.tip.SetTextColor(wx.Colour(76, 76, 76))

        # Image du tooltip
        # bmp = None
        # if dictDonnees.has_key("bmp"):
        #     bmp = dictDonnees["bmp"]
        # self.tip.SetHeaderBitmap(bmp)

        if barre != None:
            titre = barre.nomTitulaires
        else :
            titre = _(u"Aucune location")
        self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetHeader(titre)
        self.tip.SetDrawHeaderLine(True)

        # Corps du message
        if barre != None:
            texte = u""
            texte += u"Produit : %s" % self.dict_produits[barre.IDproduit]["nom"]
            texte += u"\nCatégorie : %s" % self.dict_produits[barre.IDproduit]["nom_categorie"]
            texte += u"\n"
            texte += u"\nDébut : %s" % UTILS_Dates.DatetimeEnFr(barre.date_debut)
            if barre.date_fin.year == 2999 :
                texte += u"\nFin : Non définie"
            else :
                texte += u"\nFin : %s" % UTILS_Dates.DatetimeEnFr(barre.date_fin)
            texte += u"\n"
            texte += u"\nQuantité : %s" % barre.quantite
            if len(self.liste_questions) > 0 :
                texte += u"\n"
                for dictQuestion in self.liste_questions :
                    texte += u"\n%s : %s" % (dictQuestion["label"], self.GetReponse(dictQuestion["IDquestion"], barre.IDlocation))
        else :
            texte = _(u"Aucune location n'est enregistrée à cette date.\n\n")
        self.tip.SetMessage(texte)

        # Pied du tooltip
        if barre != None:
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
        self.tipFrame.Show()
        #self.tipFrame.StartAlpha(True)  # ou .Show() pour un affichage immédiat

        # Arrêt du timer
        self.timerTip.Stop()
        del self.timerTip

    def SaveBarre(self, barre=None):
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDproduit", barre.IDproduit),
            ("date_debut", barre.date_debut),
            ("date_fin", barre.date_fin),
            ]
        DB.ReqMAJ("locations", listeDonnees, "IDlocation", barre.IDlocation)
        DB.Close()

    def Imprimer(self, event):
        pdd = wx.PrintDialogData(self.printData)
        pdd.SetToPage(1)
        printer = wx.Printer(pdd)
        printout = TableauPrintout(self, False)
        frame = wx.GetApp().GetTopWindow()
        if not printer.Print(frame, printout, True):
            if printer.GetLastError() == wx.PRINTER_ERROR:
                wx.MessageBox(_(u"Problème d'impression. Peut-être votre imprimante n'est-elle pas configurée correctement ?"), "Impression", wx.OK)
        else:
            self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()

    def Apercu(self, event):
        data = wx.PrintDialogData(self.printData)
        printout_preview  = TableauPrintout(self, True)
        printout = TableauPrintout(self, False)
        self.preview = wx.PrintPreview(printout_preview, printout, data)
        if not self.preview.IsOk():
            logging.debug(_(u"Impossible d'afficher l'aperçu avant impression...\n"))
            return
        frame = wx.GetApp().GetTopWindow()
        pfrm = wx.PreviewFrame(self.preview, frame, _(u"Aperçu avant impression"))
        pfrm.Initialize()
        pfrm.SetPosition(frame.GetPosition())
        pfrm.SetSize(frame.GetSize())
        pfrm.Show(True)


class CTRL_Infos(wx.Panel):
    def __init__(self, parent, titre=None, min_size=(-1, -1), style=None):
        wx.Panel.__init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=style)
        self.parent = parent
        self.titre = titre
        self.texte = ""

        # Propriétés
        self.SetMinSize(min_size)
        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.OnSize(None)

        # Binds
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnSize(self, event):
        if 'phoenix' in wx.PlatformInfo:
            width, height = self.GetSize()
            self.bgbuf = wx.Bitmap(width, height)
        else :
            width, height = self.GetSizeTuple()
            self.bgbuf = wx.EmptyBitmap(width, height)
        self.MAJ_affichage()

    def OnEraseBackground(self, event):
        pass

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawBitmap(self.bgbuf, 0, 0, True)
        else :
            dc.BeginDrawing()
            dc.DrawBitmap(self.bgbuf, 0, 0, True)
            dc.EndDrawing()

    def MAJ_affichage(self):
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.bgbuf)
        if 'phoenix' not in wx.PlatformInfo:
            memdc.BeginDrawing()
        memdc.SetBackground(wx.Brush(wx.WHITE, wx.SOLID))
        memdc.Clear()
        self.Draw(memdc)
        if 'phoenix' not in wx.PlatformInfo:
            memdc.EndDrawing()
        del memdc
        self.Refresh()
        self.Update()

    def SetTexte(self, texte=""):
        if self.texte != texte :
            self.texte = texte
            self.MAJ_affichage()

    def Draw(self, dc):
        rect = wx.Rect(0, 0, self.GetSize()[0], self.GetSize()[1])

        # Clipping
        if 'phoenix' in wx.PlatformInfo:
            dc.SetClippingRegion(rect)
        else:
            dc.SetClippingRect(rect)

        # Affiche le titre
        x_texte = 4
        if self.titre != None :
            couleur_fond_titre = wx.Colour(200, 200, 200)
            dc.SetBrush(wx.Brush(couleur_fond_titre))
            dc.SetPen(wx.Pen(couleur_fond_titre))
            dc.SetTextForeground((255, 255, 255))
            dc.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            padding_titre = 2
            tmp, largTitre, hautTitre = GetTailleTexte(dc, self.titre, rect.width)
            if 'phoenix' not in wx.PlatformInfo:
                dc.DrawRectangleRect(wx.Rect(0, 0, largTitre + padding_titre*4, rect.height-padding_titre*2))
            else :
                dc.DrawRectangle(wx.Rect(0, 0, largTitre + padding_titre * 4, rect.height - padding_titre * 2))
            y = rect.height / 2.0 - hautTitre / 2.0
            dc.DrawText(self.titre, padding_titre*2, y-2)
            x_texte = largTitre + 12

        # Affiche le texte
        dc.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        dc.SetTextForeground((0, 0, 0))
        largTexte, hautTexte, descent, externalLeading = dc.GetFullTextExtent(self.texte)
        y = rect.height / 2.0 - hautTexte / 2.0
        dc.DrawText(self.texte, x_texte, y-2)

        dc.DestroyClippingRegion()




class TableauPrintout(wx.Printout):
    """
    This class has the functionality of printing out a Timeline document.
    Responds to calls such as OnPrintPage and HasPage.
    Instances of this class are passed to wx.Printer.Print() or a
    wx.PrintPreview object to initiate printing or previewing.
    """

    def __init__(self, panel, preview=False):
        wx.Printout.__init__(self)
        self.panel   = panel
        self.preview = preview

    def OnBeginDocument(self, start, end):
        return super(TableauPrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(TableauPrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(TableauPrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(TableauPrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(TableauPrintout, self).OnPreparePrinting()

    def HasPage(self, page):
        if page <= 1:
            return True
        else:
            return False

    def GetPageInfo(self):
        minPage  = 1
        maxPage  = 1
        pageFrom = 1
        pageTo   = 1
        return (minPage, maxPage, pageFrom, pageTo)

    def OnPrintPage(self, page):

        def SetScaleAndDeviceOrigin(dc):
            (panel_width, panel_height) = self.panel.GetSize()
            # Let's have at least 50 device units margin
            x_margin = 50
            y_margin = 50
            # Add the margin to the graphic size
            x_max = panel_width  + (2 * x_margin)
            y_max = panel_height + (2 * y_margin)
            # Get the size of the DC in pixels
            if 'phoenix' not in wx.PlatformInfo:
                (dc_width, dc_heighth) = dc.GetSizeTuple()
            else :
                (dc_width, dc_heighth) = dc.GetSize()
            # Calculate a suitable scaling factor
            x_scale = float(dc_width) / x_max
            y_scale = float(dc_heighth) / y_max
            # Use x or y scaling factor, whichever fits on the DC
            scale = min(x_scale, y_scale)
            # Calculate the position on the DC for centering the graphic
            x_pos = (dc_width - (panel_width  * scale)) / 2.0
            y_pos = (dc_heighth - (panel_height * scale)) / 2.0
            dc.SetUserScale(scale, scale)
            dc.SetDeviceOrigin(int(x_pos), int(y_pos))

        dc = self.GetDC()
        SetScaleAndDeviceOrigin(dc)
        if 'phoenix' not in wx.PlatformInfo:
            dc.BeginDrawing()
        dc.DrawBitmap(self.panel.bgbuf, 0, 0, True)
        if 'phoenix' not in wx.PlatformInfo:
            dc.EndDrawing()
        return True

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

        # Tests
        self.bouton_test = wx.Button(panel, -1, _(u"Bouton de test"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
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
    logger = logging.getLogger()
    #logger.setLevel(logging.DEBUG)

    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
