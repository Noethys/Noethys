#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import FonctionsPerso
import wx
from Dlg import DLG_Noedoc
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro"))
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", _(u"Centime"))

from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import DocAssign, Flowable


TAILLE_PAGE = A4
LARGEUR_PAGE = TAILLE_PAGE[0]
HAUTEUR_PAGE = TAILLE_PAGE[1]
TAILLE_CADRE_CONTENU = (5*cm, 5*cm, 14*cm, 17*cm)
DICT_VALEURS = {}


def Template(canvas, doc):
    """ Première page de l'attestation """
    doc.modeleDoc.DessineFond(canvas)
    doc.modeleDoc.DessineFormes(canvas)


class MyPageTemplate(PageTemplate):
    def __init__(self, id=-1, pageSize=TAILLE_PAGE, doc=None):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]

        ##        # Récupère les coordonnées du cadre principal
        ##        cadre_principal = doc.modeleDoc.FindObjet("cadre_principal")
        ##        x, y, l, h = doc.modeleDoc.GetCoordsObjet(cadre_principal)
        ##        global CADRE_CONTENU
        ##        CADRE_CONTENU = (x, y, l, h)

        x, y, l, h = 0, 0, self.pageWidth, self.pageHeight
        frame1 = Frame(x, y, l, h, id='F1', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
        PageTemplate.__init__(self, id, [frame1], Template)

    def afterDrawPage(self, canvas, doc):
        IDinscription = doc._nameSpace["IDinscription"]
        dictValeur = DICT_VALEURS[IDinscription]

        canvas.saveState()
        doc.modeleDoc.DessineImages(canvas, dictChamps=dictValeur)
        doc.modeleDoc.DessineTextes(canvas, dictChamps=dictValeur)
        canvas.restoreState()



class Bookmark(Flowable):
    """ Utility class to display PDF bookmark. """
    def __init__(self, title, key):
        self.title = title
        self.key = key
        Flowable.__init__(self)

    def wrap(self, availWidth, availHeight):
        """ Doesn't take up any space. """
        return (0, 0)

    def draw(self):
        # set the bookmark outline to show when the file's opened
        self.canv.showOutline()
        # step 1: put a bookmark on the
        self.canv.bookmarkPage(self.key)
        # step 2: put an entry in the bookmark outline
        self.canv.addOutlineEntry(self.title, self.key, 0, 0)


class Impression():
    def __init__(self, dictValeurs={}, dictOptions={}, IDmodele=None, ouverture=True, nomFichier=None):
        """ Impression """
        global DICT_VALEURS, DICT_OPTIONS
        DICT_VALEURS = dictValeurs
        DICT_OPTIONS = dictOptions

        # Initialisation du document
        if nomFichier == None:
            nomDoc = FonctionsPerso.GenerationNomDoc("INSCRIPTIONS", "pdf")
        else:
            nomDoc = nomFichier
        doc = BaseDocTemplate(nomDoc, pagesize=TAILLE_PAGE, showBoundary=False)

        # Mémorise le ID du modèle
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        doc.modeleDoc = modeleDoc

        # Importe le template de la première page
        doc.addPageTemplates(MyPageTemplate(pageSize=TAILLE_PAGE, doc=doc))

        story = []
        styleSheet = getSampleStyleSheet()
        h3 = styleSheet['Heading3']
        styleTexte = styleSheet['BodyText']
        styleTexte.fontName = "Helvetica"
        styleTexte.fontSize = 9
        styleTexte.borderPadding = 9
        styleTexte.leading = 12

        # ----------- Insertion du contenu des frames --------------
        listeLabels = []
        for IDinscription, dictValeur in dictValeurs.items():
            listeLabels.append((dictValeur["{FAMILLE_NOM}"], IDinscription))
        listeLabels.sort()

        for labelDoc, IDinscription in listeLabels:
            dictValeur = dictValeurs[IDinscription]
            if dictValeur["select"] == True:
                story.append(DocAssign("IDinscription", IDinscription))
                nomSansCivilite = dictValeur["{FAMILLE_NOM}"]
                story.append(Bookmark(nomSansCivilite, str(IDinscription)))

                # ----------- Insertion du cadre principal --------------
                cadre_principal = doc.modeleDoc.FindObjet("cadre_principal")
                if cadre_principal != None:

                    if "intro" in DICT_OPTIONS and DICT_OPTIONS["intro"] != None or "tableau" in DICT_OPTIONS and DICT_VALEURS["tableau"] == True:
                        # ------------------- TITRE -----------------
                        dataTableau = []
                        largeursColonnes = [TAILLE_CADRE_CONTENU[2], ]
                        dataTableau.append((_(u"Confirmation d'inscription"),))
                        dataTableau.append((u"",))
                        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONT', (0, 0), (0, 0), "Helvetica-Bold", 19),
                            ('FONT', (0, 1), (0, 1), "Helvetica", 8),
                            ('LINEBELOW', (0, 0), (0, 0), 0.25, colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ])
                        tableau = Table(dataTableau, largeursColonnes)
                        tableau.setStyle(style)
                        story.append(tableau)
                        story.append(Spacer(0, 10))

                        # TEXTE D'INTRODUCTION
                        paraStyleIntro = ParagraphStyle(name="intro",
                                                        fontName="Helvetica",
                                                        fontSize=11,
                                                        leading=14,
                                                        spaceBefore=0,
                                                        spaceafter=0,
                                                        leftIndent=0,
                                                        rightIndent=0,
                                                        alignment=0,
                                                        )

                    if "intro" in DICT_OPTIONS and DICT_OPTIONS["intro"] != None:
                        texteIntro = DICT_VALEURS["intro"]
                        story.append(Paragraph(u"<i>%s</i>" % texteIntro, paraStyleIntro))
                        story.append(Spacer(0, 20))

                    if "tableau" in DICT_OPTIONS and DICT_OPTIONS["tableau"] == True:
                        # ------------------- TABLEAU CONTENU -----------------
                        dataTableau = []
                        largeursColonnes = [80, 280]
                        paraStyle = ParagraphStyle(name="detail",
                                                   fontName="Helvetica-Bold",
                                                   fontSize=9,
                                                   )
                        dataTableau.append((_(u"Nom"), Paragraph(DICT_VALEURS["{INDIVIDU_NOM}"], paraStyle)))
                        dataTableau.append((_(u"Prénom"), Paragraph(DICT_VALEURS["{INDIVIDU_PRENOM}"], paraStyle)))
                        dataTableau.append((_(u"Activité"), Paragraph(DICT_VALEURS["{ACTIVITE_NOM_LONG}"], paraStyle)))
                        dataTableau.append((_(u"Groupe"), Paragraph(DICT_VALEURS["{GROUPE_NOM_LONG}"], paraStyle)))
                        dataTableau.append((_(u"Catégorie"), Paragraph(DICT_VALEURS["{NOM_CATEGORIE_TARIF}"], paraStyle)))

                        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONT', (0, 0), (0, -1), "Helvetica", 9),
                            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                        ])
                        tableau = Table(dataTableau, largeursColonnes)
                        tableau.setStyle(style)
                        story.append(tableau)

                # Saut de page
                story.append(PageBreak())

        # Finalisation du PDF
        doc.build(story)

        # Ouverture du PDF
        if ouverture == True:
            FonctionsPerso.LanceFichierExterne(nomDoc)





if __name__ == u"__main__":
    Impression()
