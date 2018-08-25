#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from UTILS_Traduction import _
import wx
import datetime
import calendar
import FonctionsPerso
import GestionDB
import random
import copy
from dateutil import rrule

from Utils import UTILS_Dates

from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.platypus.flowables import Image





def ColorWxToPdf(couleur=(0, 0, 0), alpha=1):
    r, g, b = couleur[0] / 255.0, couleur[1] / 255.0, couleur[2] / 255.0
    return Color(r, g, b, alpha=alpha)

def MixCouleurs():
    couleur = random.choice([(154, 200, 100), (253, 162, 92), (216, 83, 86), (32, 155, 215), (252, 195, 0), (160, 110, 173)])
    return couleur

def Get_week_days(year, week):
    d = datetime.date(year, 1, 1)
    if (d.weekday() > 3):
        d = d + datetime.timedelta(7 - d.weekday())
    else:
        d = d - datetime.timedelta(d.weekday())
    dlt = datetime.timedelta(days=(week - 1) * 7)
    return d + dlt, d + dlt + datetime.timedelta(days=6)



class Titre():
    def __init__(self, parent=None, texte=u"", canvas=None, largeur=None):
        self.parent = parent
        self.canvas = canvas
        self.largeur = largeur

        # Préparation du dessin
        self.canvas.saveState()
        self.canvas.translate(0, self.canvas._pagesize[1] - self.parent.dictDonnees["titre_hauteur"])

        # Dessine la case
        self.Dessine_titre(texte=texte)

        self.canvas.restoreState()

    def Dessine_titre(self, texte=""):
        """ Dessine un titre en haut de la page """
        # Dessine le rectangle de fond
        self.canvas.setStrokeColor(ColorWxToPdf(self.parent.dictDonnees["titre_bord_couleur"], alpha=1))
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["titre_fond_couleur"], alpha=1))
        self.canvas.rect(x=0, y=0, width=self.largeur, height=self.parent.dictDonnees["titre_hauteur"], stroke=True, fill=True)

        # Dessine le mot MENUS
        afficher_mot_menu = False

        if afficher_mot_menu == True :

            # Calcule la hauteur du texte
            taille_police = 30
            face = pdfmetrics.getFont(self.parent.dictDonnees["titre_nom_police"]).face
            hauteur_font = face.ascent * taille_police / 1000.0

            largeur_box = 200
            hauteur_box = 40
            x_box = 35
            y_box = -10

            self.canvas.rotate(2)
            self.canvas.setStrokeColor(ColorWxToPdf(wx.BLACK, alpha=1))
            self.canvas.setFillColor(ColorWxToPdf(wx.WHITE, alpha=1))
            self.canvas.rect(x=x_box, y=y_box, width=largeur_box, height=hauteur_box, stroke=True, fill=True)

            self.canvas.setFont(self.parent.dictDonnees["titre_nom_police"], size=taille_police)
            self.canvas.setFillColor(ColorWxToPdf(wx.BLACK, alpha=1))
            self.canvas.drawCentredString(x_box + largeur_box / 2.0, y_box + hauteur_box / 2.0 - hauteur_font / 2.0, _(u"MENUS"))
            self.canvas.rotate(-2)

        # Ecrit la période

        # Calcule la hauteur du texte
        face = pdfmetrics.getFont(self.parent.dictDonnees["titre_nom_police"]).face
        hauteur_font = face.ascent * self.parent.dictDonnees["titre_taille_police"] / 1000.0

        # Ecrit le texte
        x = self.largeur / 2.0
        if afficher_mot_menu == True :
            x += (largeur_box + 30) / 2.0
        self.canvas.setFont(self.parent.dictDonnees["titre_nom_police"], size=self.parent.dictDonnees["titre_taille_police"])
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["titre_texte_couleur"], alpha=1))
        self.canvas.drawCentredString(x, self.parent.dictDonnees["titre_hauteur"] - (self.parent.dictDonnees["titre_hauteur"] / 2.0 + hauteur_font / 2.0), texte)


# ------------------------------------------------------------------------------------------------------------------



class Pied():
    def __init__(self, parent=None, texte=u"", canvas=None, x=None, y=None, largeur=None):
        self.parent = parent
        self.canvas = canvas
        self.x = x
        self.y = y
        self.largeur = largeur

        # Préparation du dessin
        self.canvas.saveState()
        self.canvas.translate(x, y)

        # Création du clipping
        p = self.canvas.beginPath()
        self.canvas.setStrokeColor(ColorWxToPdf(wx.WHITE, alpha=0))
        self.canvas.setLineWidth(0)
        p.roundRect(x=0, y=0, width=self.largeur, height=self.parent.dictDonnees["pied_hauteur"], radius=self.parent.dictDonnees["pied_radius"])
        self.canvas.clipPath(p)

        # Dessine la case
        self.Dessine_pied(texte=texte)

        self.canvas.restoreState()


    def Dessine_pied(self, texte=""):
        """ Dessine un titre en haut de la page """
        # Dessine le rectangle de fond
        self.canvas.setStrokeColor(ColorWxToPdf(self.parent.dictDonnees["pied_bord_couleur"], alpha=self.parent.dictDonnees["pied_bord_alpha"]/100.0))
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["pied_fond_couleur"], alpha=self.parent.dictDonnees["pied_fond_alpha"]/100.0))
        self.canvas.setLineWidth(0.25)
        self.canvas.roundRect(x=0, y=0, width=self.largeur, height=self.parent.dictDonnees["pied_hauteur"], radius=self.parent.dictDonnees["pied_radius"], stroke=True, fill=True)

        # Calcule la hauteur du texte
        face = pdfmetrics.getFont(self.parent.dictDonnees["pied_nom_police"]).face
        hauteur_font = face.ascent * self.parent.dictDonnees["pied_taille_police"] / 1000.0

        # Ecrit le texte
        self.canvas.setFont(self.parent.dictDonnees["pied_nom_police"], size=self.parent.dictDonnees["pied_taille_police"])
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["pied_texte_couleur"], alpha=1))
        self.canvas.drawCentredString(self.largeur / 2.0, self.parent.dictDonnees["pied_hauteur"] - (self.parent.dictDonnees["pied_hauteur"] / 2.0 + hauteur_font / 2.0), texte)







# ------------------------------------------------------------------------------------------------------------------

class Entete():
    def __init__(self, parent=None, texte=u"", canvas=None, x=None, y=None, largeur_case=None):
        self.parent = parent
        self.canvas = canvas
        self.x = x
        self.y = y
        self.largeur_case = largeur_case

        # Préparation du dessin
        self.canvas.saveState()
        self.canvas.translate(x, y)

        # Création du clipping
        p = self.canvas.beginPath()
        self.canvas.setStrokeColor(ColorWxToPdf(wx.WHITE, alpha=0))
        self.canvas.setLineWidth(0)
        p.roundRect(x=0, y=0, width=largeur_case, height=self.parent.dictDonnees["entete_hauteur"], radius=self.parent.dictDonnees["entete_radius"])
        self.canvas.clipPath(p)

        # Dessine la case
        self.Dessine_titre(texte=texte)

        self.canvas.restoreState()

    def Dessine_titre(self, texte=""):
        """ Dessine un titre en haut de la case """
        # Dessine le rectangle de fond
        if self.parent.dictDonnees["entete_mix_couleurs"] == False :
            entete_bord_couleur = self.parent.dictDonnees["entete_bord_couleur"]
            entete_fond_couleur = self.parent.dictDonnees["entete_fond_couleur"]
        else :
            # Mix de couleur
            couleur = MixCouleurs()
            entete_bord_couleur = wx.Colour(*couleur)
            entete_fond_couleur = wx.Colour(*couleur)
        self.canvas.setStrokeColor(ColorWxToPdf(entete_bord_couleur, alpha=self.parent.dictDonnees["entete_bord_alpha"]/100.0))
        self.canvas.setFillColor(ColorWxToPdf(entete_fond_couleur, alpha=self.parent.dictDonnees["entete_fond_alpha"]/100.0))
        self.canvas.roundRect(x=0, y=self.parent.dictDonnees["entete_hauteur"] - self.parent.dictDonnees["entete_hauteur"], width=self.largeur_case, height=self.parent.dictDonnees["entete_hauteur"], radius=self.parent.dictDonnees["entete_radius"], stroke=True, fill=True)

        # Calcule la hauteur du texte
        face = pdfmetrics.getFont(self.parent.dictDonnees["entete_nom_police"]).face
        hauteur_font = face.ascent * self.parent.dictDonnees["entete_taille_police"] / 1000.0

        # Ecrit le texte
        self.canvas.setFont(self.parent.dictDonnees["entete_nom_police"], size=self.parent.dictDonnees["entete_taille_police"])
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["entete_texte_couleur"], alpha=self.parent.dictDonnees["entete_texte_alpha"]/100.0))
        self.canvas.drawCentredString(self.largeur_case / 2.0, self.parent.dictDonnees["entete_hauteur"] - (self.parent.dictDonnees["entete_hauteur"] / 2.0 + hauteur_font / 2.0), texte)









# ------------------------------------------------------------------------------------------------------------------

class Case():
    def __init__(self, parent=None, date=None, dictTextes={}, canvas=None, x=None, y=None, largeur_case=None, hauteur_case=None):
        self.parent = parent
        self.date = date
        self.canvas = canvas
        self.x = x
        self.y = y
        self.largeur_case = largeur_case
        self.hauteur_case = hauteur_case

        # Préparation du dessin
        self.canvas.saveState()
        self.canvas.translate(x, y)

        # Rotation aléatoire
        if self.parent.dictDonnees["case_rotation_aleatoire"] == True :
            self.canvas.rotate(random.randint(-3, 3))

        # Création du clipping
        p = self.canvas.beginPath()
        self.canvas.setStrokeColor(ColorWxToPdf(wx.WHITE, alpha=0))
        self.canvas.setLineWidth(0)
        p.roundRect(x=0, y=0, width=largeur_case, height=hauteur_case, radius=self.parent.dictDonnees["case_radius"])
        self.canvas.clipPath(p)

        # Dessine le rectangle arrondi pour le fond de la case
        if date != None :
            fond_alpha = self.parent.dictDonnees["case_fond_alpha"]/100.0
            bord_alpha = self.parent.dictDonnees["case_bord_alpha"]/100.0
        else :
            fond_alpha = self.parent.dictDonnees["case_fond_alpha_vide"]/100.0
            bord_alpha = self.parent.dictDonnees["case_bord_alpha_vide"]/100.0

        self.canvas.setStrokeColor(ColorWxToPdf(self.parent.dictDonnees["case_bord_couleur"], alpha=bord_alpha))
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["case_fond_couleur"], alpha=fond_alpha))
        self.canvas.setLineWidth(1)
        self.canvas.roundRect(x=0, y=0, width=largeur_case, height=hauteur_case, radius=self.parent.dictDonnees["case_radius"], stroke=True, fill=True)

        if date != None :

            # Dessine le texte
            if len(dictTextes) > 0 :

                # Calcule hauteur de la case
                if self.parent.dictDonnees["case_hauteur"] == 0:
                    hauteur = self.hauteur_case
                else:
                    hauteur = self.parent.dictDonnees["case_hauteur"]

                # Calcule position y
                y = 0
                if self.parent.dictDonnees["case_titre_afficher"] == True:
                    y = self.parent.dictDonnees["case_titre_hauteur"]
                    hauteur -= self.parent.dictDonnees["case_titre_hauteur"]

                # Recherche les catégories et textes à afficher
                hauteur_categorie = 1.0 * hauteur / len(self.parent.dictDonnees["categories"])

                for dictCategorie in self.parent.dictDonnees["categories"] :
                    nom_categorie = dictCategorie["nom"]
                    if len(self.parent.dictDonnees["categories"]) == 1 :
                        nom_categorie = None

                    texte = None
                    if dictTextes.has_key(dictCategorie["IDcategorie"]):
                        texte = dictTextes[dictCategorie["IDcategorie"]]["texte"]
                    self.Dessine_texte(texte=texte, nom_categorie=nom_categorie, y=y, hauteur=hauteur_categorie)
                    y += hauteur_categorie

            # Dessine le macaron
            if self.parent.dictDonnees["case_macaron_afficher"] == True :
                self.Dessine_macaron(texte=str(date.day))

            # Dessine le titre
            if self.parent.dictDonnees["case_titre_afficher"] == True :
                self.Dessine_titre(texte=UTILS_Dates.DateComplete(date))

        self.canvas.restoreState()

    def GetParagraphes(self, texte="", taille_police=None):
        style = ParagraphStyle(name="style", fontName=self.parent.dictDonnees["case_nom_police"], fontSize=taille_police,
                               spaceBefore=0, spaceafter=0, leftIndent=0, rightIndent=0, alignment=1, leading=taille_police,
                               textColor=ColorWxToPdf(self.parent.dictDonnees["case_texte_couleur"]))

        liste_paragraphes = []
        hauteur_paragraphes = 0
        for texte_paragraphe in texte.split("\n") :
            paragraphe = Paragraph(texte_paragraphe, style=style)
            largeur_paragraphe, hauteur_paragraphe = paragraphe.wrapOn(self.canvas, self.largeur_case, self.hauteur_case)
            hauteur_paragraphes += hauteur_paragraphe
            liste_paragraphes.append((hauteur_paragraphe, paragraphe))
        return liste_paragraphes, hauteur_paragraphes

    def Dessine_texte(self, texte="", nom_categorie=None, y=0, hauteur=0):
        """ Dessine le texte de la case """
        if texte == None :
            texte = ""

        # Dessine le nom de la catégorie
        if nom_categorie != None :
            self.canvas.saveState()
            self.canvas.setStrokeColor(ColorWxToPdf(self.parent.dictDonnees["case_titre_texte_couleur"], alpha=1))
            self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["case_titre_texte_couleur"], alpha=1))
            self.canvas.setLineWidth(0.5)
            self.canvas.setDash(0.5, 4)
            self.canvas.line(0, self.hauteur_case - y +1, self.largeur_case, self.hauteur_case - y +1)

            self.canvas.setFont(self.parent.dictDonnees["case_titre_nom_police"], size=self.parent.dictDonnees["case_titre_taille_police"]-2)
            self.canvas.drawString(4, self.hauteur_case - y - 10, nom_categorie)
            self.canvas.restoreState()


        # Propriétés
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["case_texte_couleur"], alpha=1))

        # Création des paragraphes
        taille_police = self.parent.dictDonnees["case_taille_police"]
        espace_vertical = self.parent.dictDonnees["case_espace_vertical"]
        liste_paragraphes, hauteur_paragraphes = self.GetParagraphes(texte, taille_police)
        ratio_depassement = (hauteur_paragraphes + (len(liste_paragraphes) - 1) * espace_vertical) / hauteur

        # Vérifie si le texte ne dépasse pas de la case
        if ratio_depassement > 1 :
            taille_police = taille_police / ratio_depassement
            liste_paragraphes, hauteur_paragraphes = self.GetParagraphes(texte, taille_police)

        # Calcule l'espace vertical et la marge supérieure
        if self.parent.dictDonnees["case_repartition_verticale"] == True :
            # marge_haut = self.parent.dictDonnees["case_marge_haut"]
            # espace_vertical = (hauteur - hauteur_paragraphes - marge_haut * 2) / (len(liste_paragraphes) - 1)
            bordure = 4
            espace_vertical = (hauteur - hauteur_paragraphes - bordure*2) / (len(liste_paragraphes) - 1 + 2)
            marge_haut = espace_vertical + bordure
        else :
            espace_vertical = self.parent.dictDonnees["case_espace_vertical"]
            marge_haut = (hauteur - (hauteur_paragraphes + (len(liste_paragraphes) - 1) * espace_vertical)) / 2.0

        # Préparation des images
        if self.parent.dictDonnees["case_separateur_type"] == "image" and self.parent.dictDonnees["case_separateur_image"] != "aucune":
            img = wx.Image(Chemins.GetStaticPath("Images/Menus/%s" % self.parent.dictDonnees["case_separateur_image"]), wx.BITMAP_TYPE_ANY)
            ratio_image = 1.0 * img.GetWidth() / img.GetHeight()
            largeur_image = self.largeur_case / 1.5
            hauteur_image = largeur_image / ratio_image
            separateur_image = Image(Chemins.GetStaticPath("Images/Menus/%s" % self.parent.dictDonnees["case_separateur_image"]), width=largeur_image, height=hauteur_image)

        # Dessine les lignes
        y_paragraphe = self.hauteur_case - y - marge_haut
        index = 0
        for hauteur_paragraphe, paragraphe in liste_paragraphes:
            y_paragraphe -= hauteur_paragraphe
            paragraphe.drawOn(self.canvas, 0, y_paragraphe)

            # Dessine l'image de séparation
            if self.parent.dictDonnees["case_separateur_type"] != "aucun" and index < len(liste_paragraphes) - 1:
                if self.parent.dictDonnees["case_separateur_type"] == "image" :
                    separateur_image.drawOn(self.canvas, self.largeur_case / 2.0 - separateur_image._width / 2.0, y_paragraphe - espace_vertical / 2.0 - separateur_image._height / 2.0)
                elif self.parent.dictDonnees["case_separateur_type"] == "ligne":
                    largeur_separateur = self.largeur_case / 3.5
                    x_separateur = (self.largeur_case - largeur_separateur) / 2.0
                    self.canvas.setStrokeColor(ColorWxToPdf(wx.WHITE, alpha=0.2))
                    self.canvas.setLineWidth(0.25)
                    self.canvas.line(x_separateur, y_paragraphe - espace_vertical / 2.0, x_separateur + largeur_separateur, y_paragraphe - espace_vertical / 2.0)

            y_paragraphe -= espace_vertical
            index += 1

    def Dessine_titre(self, texte=""):
        """ Dessine un titre en haut de la case """
        # Dessine le rectangle de fond
        if self.parent.dictDonnees["case_titre_mix_couleurs"] == False :
            case_titre_fond_couleur = self.parent.dictDonnees["case_titre_fond_couleur"]
        else :
            # Mix de couleur
            couleur = MixCouleurs()
            case_titre_fond_couleur = wx.Colour(*couleur)

        self.canvas.setStrokeColor(ColorWxToPdf(case_titre_fond_couleur, alpha=1))
        self.canvas.setFillColor(ColorWxToPdf(case_titre_fond_couleur, alpha=1))
        self.canvas.rect(x=0, y=self.hauteur_case - self.parent.dictDonnees["case_titre_hauteur"], width=self.largeur_case, height=self.parent.dictDonnees["case_titre_hauteur"], stroke=True, fill=True)

        # Calcule la hauteur du texte
        face = pdfmetrics.getFont(self.parent.dictDonnees["case_titre_nom_police"]).face
        hauteur_font = face.ascent * self.parent.dictDonnees["case_titre_taille_police"] / 1000.0

        # Ecrit le texte
        self.canvas.setFont(self.parent.dictDonnees["case_titre_nom_police"], size=self.parent.dictDonnees["case_titre_taille_police"])
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["case_titre_texte_couleur"], alpha=1))
        self.canvas.drawCentredString(self.largeur_case / 2.0, self.hauteur_case - (self.parent.dictDonnees["case_titre_hauteur"] / 2.0 + hauteur_font / 2.0), texte)


    def Dessine_macaron(self, texte="", rond=False):
        """ Dessine un cadre arrondi et un texte dans le coin haut droit de la case """
        # Dessine le rectangle de fond
        if self.parent.dictDonnees["case_macaron_mix_couleurs"] == False :
            case_macaron_bord_couleur = self.parent.dictDonnees["case_macaron_bord_couleur"]
            case_macaron_fond_couleur = self.parent.dictDonnees["case_macaron_fond_couleur"]
        else :
            # Mix de couleur
            couleur = MixCouleurs()
            case_macaron_bord_couleur = wx.Colour(*couleur)
            case_macaron_fond_couleur = wx.Colour(*couleur)

        self.canvas.setStrokeColor(ColorWxToPdf(case_macaron_bord_couleur, alpha=self.parent.dictDonnees["case_macaron_bord_alpha"]/100.0))
        self.canvas.setFillColor(ColorWxToPdf(case_macaron_fond_couleur, alpha=self.parent.dictDonnees["case_macaron_fond_alpha"]/100.0))

        if self.parent.dictDonnees["case_macaron_type"] == "rond" :
            self.canvas.circle(x_cen=self.largeur_case - self.parent.dictDonnees["case_macaron_largeur"] / 2.0 -5, y_cen=self.hauteur_case - self.parent.dictDonnees["case_macaron_hauteur"] / 2.0 -5, r=self.parent.dictDonnees["case_macaron_taille_police"]-3, stroke=True, fill=True)
            largeur, hauteur = self.parent.dictDonnees["case_macaron_largeur"] + 10, self.parent.dictDonnees["case_macaron_hauteur"] + 10
        else :
            self.canvas.roundRect(x=self.largeur_case - self.parent.dictDonnees["case_macaron_largeur"], y=self.hauteur_case - self.parent.dictDonnees["case_macaron_hauteur"], width=self.parent.dictDonnees["case_macaron_largeur"] + self.parent.dictDonnees["case_macaron_radius"], height=self.parent.dictDonnees["case_macaron_hauteur"] + self.parent.dictDonnees["case_macaron_radius"], radius=self.parent.dictDonnees["case_macaron_radius"], stroke=True, fill=True)
            largeur, hauteur = self.parent.dictDonnees["case_macaron_largeur"], self.parent.dictDonnees["case_macaron_hauteur"]

        # Calcule la hauteur du texte
        face = pdfmetrics.getFont(self.parent.dictDonnees["case_macaron_nom_police"]).face
        hauteur_font = face.ascent * self.parent.dictDonnees["case_macaron_taille_police"] / 1000.0

        # Ecrit le texte
        self.canvas.setFont(self.parent.dictDonnees["case_macaron_nom_police"], size=self.parent.dictDonnees["case_macaron_taille_police"])
        self.canvas.setFillColor(ColorWxToPdf(self.parent.dictDonnees["case_macaron_texte_couleur"], alpha=1))
        self.canvas.drawCentredString(self.largeur_case - largeur + largeur / 2.0, self.hauteur_case - (hauteur / 2.0 + hauteur_font / 2.0), texte)



# ---------------------------------------------------------------------------------------------------------------





# ---------------------------------------------------------------------------------------------------------------

class Impression():
    def __init__(self, dictDonnees={}):
        self.dictDonnees = dictDonnees

        # Importation des données
        DB = GestionDB.DB()

        # Catégories de menus
        if 0 not in dictDonnees["categories_menus"]:
            if len(dictDonnees["categories_menus"]) == 0 :
                conditions = "WHERE IDcategorie IN ()"
            elif len(dictDonnees["categories_menus"]) == 1 :
                conditions = "WHERE IDcategorie=%d" % dictDonnees["categories_menus"][0]
            else :
                conditions = "WHERE IDcategorie IN %s" % (str(tuple(dictDonnees["categories_menus"])))
        else :
            conditions = ""
        req = """SELECT IDcategorie, nom
        FROM menus_categories 
        %s
        ORDER BY ordre;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictDonnees["categories"] = []
        for IDcategorie, nom in listeDonnees:
            self.dictDonnees["categories"].append({"IDcategorie": IDcategorie, "nom": nom})

        # Menus
        req = """SELECT IDmenu, IDcategorie, date, texte
        FROM menus 
        WHERE date>='%s' AND date<='%s' AND IDrestaurateur=%d
        ;""" % (dictDonnees["date_debut"], dictDonnees["date_fin"], dictDonnees["IDrestaurateur"])
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictDonnees["menus"] = {}
        for IDmenu, IDcategorie, date, texte in listeDonnees:
            date = UTILS_Dates.DateEngEnDateDD(date)
            if self.dictDonnees["menus"].has_key(date) == False:
                self.dictDonnees["menus"][date] = {}
            if texte != None and len(texte) == 0:
                texte = None
            self.dictDonnees["menus"][date][IDcategorie] = {"IDmenu": IDmenu, "texte": texte}

        DB.Close()

        # Paramètres
        if dictDonnees["page_format"] == "paysage" :
            hauteur_page, largeur_page = A4
        else :
            largeur_page, hauteur_page = A4

        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("MENU", "pdf")
        canvas = Canvas(nomDoc, pagesize=(largeur_page, hauteur_page))

        # Calcule les pages
        if dictDonnees["type"] == "mensuel" :
            liste_pages = [{"annee" : date.year, "mois" : date.month} for date in list(rrule.rrule(rrule.MONTHLY, dtstart=dictDonnees["date_debut"], until=dictDonnees["date_fin"]))]
        if dictDonnees["type"] == "hebdomadaire" :
            liste_pages = [{"date" : date} for date in list(rrule.rrule(rrule.WEEKLY, dtstart=dictDonnees["date_debut"], until=dictDonnees["date_fin"]))]
        if dictDonnees["type"] == "quotidien" :
            liste_pages = [{"date" : date} for date in list(rrule.rrule(rrule.DAILY, dtstart=dictDonnees["date_debut"], until=dictDonnees["date_fin"]))]

        num_page = 0
        for dict_page in liste_pages :

            # Calcule le nombre de lignes et de colonnes
            if dictDonnees["type"] == "mensuel":
                calendrier = self.GetCalendrierMois(annee=dict_page["annee"], mois=dict_page["mois"], jours_semaine=dictDonnees["jours_semaine"])
                nbre_lignes = len(calendrier)
                nbre_colonnes = len(dictDonnees["jours_semaine"])
                texte_titre = UTILS_Dates.PeriodeComplete(mois=dict_page["mois"], annee=dict_page["annee"])

            if dictDonnees["type"] == "hebdomadaire":
                calendrier = self.GetCalendrierSemaine(date=dict_page["date"], jours_semaine=dictDonnees["jours_semaine"])
                nbre_lignes = 1
                nbre_colonnes = len(dictDonnees["jours_semaine"])
                texte_titre = self.GetLabelSemaine(calendrier[0], calendrier[-1])

            if dictDonnees["type"] == "quotidien":
                nbre_lignes = 1
                nbre_colonnes = 1
                texte_titre = UTILS_Dates.DateComplete(dict_page["date"])

            # Préparation
            marge_haut = copy.copy(dictDonnees["page_marge_haut"])
            marge_bas = copy.copy(dictDonnees["page_marge_bas"])

            # Calcule la largeur des cases
            largeur_case = ((largeur_page - dictDonnees["page_marge_gauche"] - dictDonnees["page_marge_droite"]) - dictDonnees["page_espace_horizontal"] * (nbre_colonnes - 1)) / nbre_colonnes

            # Dessine l'image de fond
            if dictDonnees["page_fond_image"] != "aucune" :
                canvas.drawImage(Chemins.GetStaticPath("Images/%s" % dictDonnees["page_fond_image"]), 0, 0, largeur_page, hauteur_page, preserveAspectRatio=False)

            # Dessine le titre
            if dictDonnees["titre_afficher"] == True:
                if dictDonnees["titre_texte"] != "" :
                    texte_titre = u"%s - %s" % (dictDonnees["titre_texte"], texte_titre)
                titre = Titre(parent=self, texte=texte_titre, canvas=canvas, largeur=largeur_page)
                marge_haut += dictDonnees["titre_hauteur"]

            # Dessine les entêtes
            if dictDonnees["entete_afficher"] == True:
                for num_colonne in range(0, nbre_colonnes):
                    # Calcule la position de la case
                    x_entete = dictDonnees["page_marge_gauche"] + ((largeur_case + dictDonnees["page_espace_horizontal"]) * num_colonne)
                    y_entete = hauteur_page - marge_haut - dictDonnees["entete_hauteur"]

                    # Dessine l'entête
                    texte = UTILS_Dates.LISTE_JOURS[dictDonnees["jours_semaine"][num_colonne]]
                    entete = Entete(parent=self, texte=texte, canvas=canvas, x=x_entete, y=y_entete, largeur_case=largeur_case)

                marge_haut += dictDonnees["entete_hauteur"] + dictDonnees["page_espace_vertical"]

            # Dessine le pied
            if dictDonnees["pied_afficher"] == True :
                pied = Pied(parent=self, texte=dictDonnees["pied_texte"], canvas=canvas, x=dictDonnees["page_marge_gauche"], y=marge_bas, largeur=largeur_page - dictDonnees["page_marge_gauche"] - dictDonnees["page_marge_droite"])
                marge_bas += dictDonnees["pied_hauteur"] + dictDonnees["page_espace_vertical"]

            # Calcul la hauteur des cases
            hauteur_case = ((hauteur_page - marge_haut - marge_bas) - dictDonnees["page_espace_vertical"] * (nbre_lignes - 1)) / nbre_lignes

            # Dessine les cases
            for num_colonne in range(0, nbre_colonnes):
                for num_ligne in range(0, nbre_lignes):

                    # Calcule la position de la case
                    x_case = dictDonnees["page_marge_gauche"] + ((largeur_case + dictDonnees["page_espace_horizontal"]) * num_colonne)
                    y_case = hauteur_page - marge_haut - hauteur_case - ((hauteur_case + dictDonnees["page_espace_vertical"]) * num_ligne)

                    # Recherche la date
                    date = None

                    if dictDonnees["type"] == "mensuel" and calendrier[num_ligne][num_colonne] != 0 :
                        date = datetime.date(dict_page["annee"], dict_page["mois"], calendrier[num_ligne][num_colonne])
                    if dictDonnees["type"] == "hebdomadaire":
                        date = calendrier[num_colonne]
                    if dictDonnees["type"] == "quotidien" :
                        date = datetime.date(dict_page["date"].year, dict_page["date"].month, dict_page["date"].day)

                    # Dessine la case
                    dictTextes = {}
                    if dictDonnees["menus"].has_key(date) :
                        dictTextes = dictDonnees["menus"][date]

                    case = Case(parent=self, date=date, dictTextes=dictTextes, canvas=canvas, x=x_case, y=y_case, largeur_case=largeur_case, hauteur_case=hauteur_case)

            # Dessine la grille
            if dictDonnees["page_grille"] == True :
                canvas.setStrokeColor(ColorWxToPdf(wx.LIGHT_GREY, alpha=0.5))
                canvas.setFillColor(ColorWxToPdf(wx.LIGHT_GREY, alpha=0.5))
                canvas.setLineWidth(0.25)
                canvas.grid(range(0, int(largeur_page)+50, 50), range(0, int(hauteur_page)+50, 50))
                canvas.setFont("Helvetica", 8)
                canvas.drawString(10, 10, _(u"Largeur carreau=50"))

            # Saut de page
            if num_page < len(liste_pages) - 1:
                canvas.showPage()


        # Finalisation du PDF
        canvas.save()

        try:
            FonctionsPerso.LanceFichierExterne(nomDoc)
        except:
            print "Probleme dans l'edition du menu"

    def GetCalendrierMois(self, annee=2018, mois=0, jours_semaine=[0, 1, 2, 3, 4, 5, 6]):
        calendrier = calendar.monthcalendar(annee, mois)
        liste_semaines = []
        for semaine in calendrier :
            semaine_temp = [semaine[num_jour] for num_jour in jours_semaine]
            if sum(semaine_temp) > 0 :
                liste_semaines.append(semaine_temp)
        return liste_semaines

    def GetCalendrierSemaine(self, date=None, jours_semaine=[0, 1, 2, 3, 4, 5, 6]):
        liste_dates = []
        num_semaine = date.isocalendar()[1]
        listeTemp = list(rrule.rrule(rrule.DAILY, byweekno=num_semaine, dtstart=date-datetime.timedelta(date.weekday()), count=7))
        for date_temp in listeTemp:
            if date_temp.weekday() in jours_semaine:
                date_temp = datetime.date(date_temp.year, date_temp.month, date_temp.day)
                liste_dates.append(date_temp)
        return liste_dates

    def GetLabelSemaine(self, date_debut=None, date_fin=None):
        if date_debut.year == date_fin.year and date_debut.month == date_fin.month :
            debut = date_debut.day
            fin = u"%d %s %d" % (date_fin.day, UTILS_Dates.LISTE_MOIS[date_fin.month-1], date_fin.year)
        elif date_debut.year == date_fin.year :
            debut = u"%d %s" % (date_debut.day, UTILS_Dates.LISTE_MOIS[date_debut.month-1])
            fin = u"%d %s %d" % (date_fin.day, UTILS_Dates.LISTE_MOIS[date_fin.month-1], date_fin.year)
        else :
            debut = UTILS_Dates.DateDDEnFr(date_debut)
            fin = UTILS_Dates.DateDDEnFr(date_fin)
        return _(u"Semaine du %s au %s") % (debut, fin)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    # Données test
    dictDonnees = {
        "date_debut": datetime.date(2018, 7, 1),
        "date_fin": datetime.date(2018, 7, 31),
        "IDrestaurateur": 1,
        "type": "hebdomadaire",  # mensuel, hebdomadaire, quotidien
        "jours_semaine": [0, 1, 2, 3, 4, 5, 6],
        "categories_menus" : [0,],

        # Page
        "page_fond_image" : "Interface/Bleu/Fond.jpg",
        "page_format" : "paysage",
        "page_marge_gauche" : 20,
        "page_marge_droite" : 20,
        "page_marge_haut" : 20,
        "page_marge_bas" : 20,
        "page_espace_horizontal" : 10,
        "page_espace_vertical" : 10,
        "page_grille" : False,

        # Entete
        "entete_afficher" : True,
        "entete_fond_couleur" : wx.Colour(254, 178, 0),
        "entete_fond_alpha" : 1*100,
        "entete_bord_couleur" : wx.Colour(254, 178, 0),
        "entete_bord_alpha" : 1*100,
        "entete_texte_couleur" : wx.WHITE,
        "entete_texte_alpha" : 1*100,
        "entete_hauteur" : 25,
        "entete_nom_police" : "Helvetica-Bold",
        "entete_taille_police" : 15,
        "entete_radius" : 5,
        "entete_mix_couleurs" : False,

        # Case
        "case_hauteur" : 0,
        "case_radius" : 5,
        "case_rotation_aleatoire" : False,
        "case_bord_couleur" : wx.WHITE,
        "case_bord_alpha" : 0.6*100,
        "case_bord_alpha_vide": 0.2*100,
        "case_fond_couleur" : wx.WHITE,
        "case_fond_alpha" : 0.6*100,
        "case_fond_alpha_vide": 0.2*100,
        "case_repartition_verticale" : True,
        "case_nom_police" : "Helvetica",
        "case_taille_police" : 10,
        "case_texte_couleur" : wx.BLACK,
        "case_marge_haut": 15,
        "case_espace_vertical": 5,
        "case_separateur_type" : "aucun",
        "case_separateur_image" : "aucune",
        "case_separateur_texte" : u"-------",

        # Titre
        "case_titre_afficher" : True,
        "case_titre_hauteur" : 15,
        "case_titre_fond_couleur" : wx.Colour(254, 178, 0),
        "case_titre_texte_couleur": wx.WHITE,
        "case_titre_nom_police" : "Helvetica-Bold",
        "case_titre_taille_police" : 8,
        "case_titre_mix_couleurs" : False,

        # Macaron
        "case_macaron_afficher" : False,
        "case_macaron_type" : "carre", # ou rond
        "case_macaron_radius" : 5,
        "case_macaron_largeur" : 25,
        "case_macaron_hauteur" : 20,
        "case_macaron_bord_couleur": wx.Colour(254, 178, 0),
        "case_macaron_bord_alpha": 1*100,
        "case_macaron_fond_couleur" : wx.Colour(254, 178, 0),
        "case_macaron_fond_alpha": 1*100,
        "case_macaron_nom_police" : "Helvetica-Bold",
        "case_macaron_taille_police" : 13,
        "case_macaron_texte_couleur" : wx.WHITE,
        "case_macaron_mix_couleurs" : False,

        # Titre
        "titre_afficher" : True,
        "titre_hauteur" : 50,
        "titre_bord_couleur" : wx.Colour(254, 178, 0),
        "titre_fond_couleur": wx.Colour(254, 178, 0),
        "titre_nom_police" : "Helvetica-Bold",
        "titre_taille_police" : 25,
        "titre_texte_couleur" : wx.WHITE,
        "titre_texte" : u"Test",

        # Pied
        "pied_afficher" : True,
        "pied_texte" : u"Informations...",
        "pied_hauteur" : 50,
        "pied_radius" : 5,
        "pied_bord_couleur" : wx.WHITE,
        "pied_bord_alpha" : 0.2*100,
        "pied_fond_couleur" : wx.WHITE,
        "pied_fond_alpha" : 0.05*100,
        "pied_nom_police" : "Helvetica",
        "pied_taille_police" : 10,
        "pied_texte_couleur" : wx.BLACK,
        }


    Impression(dictDonnees=dictDonnees)



