#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import datetime
import FonctionsPerso

import DLG_Noedoc
import UTILS_Dates

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.platypus.frames import Frame, ShowBoundaryValue
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.barcode import code39, qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import DocAssign, Flowable


TAILLE_PAGE = A4
LARGEUR_PAGE = TAILLE_PAGE[0]
HAUTEUR_PAGE = TAILLE_PAGE[1]
    
DICT_COMPTES = {}
DICT_OPTIONS = {} 



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
        IDcotisation = doc._nameSpace["IDcotisation"]
        dictValeur = DICT_VALEURS[IDcotisation]

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
        if nomFichier == None :
            nomDoc = "Temp/Cotisations_%s.pdf" % FonctionsPerso.GenerationIDdoc()
        else :
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
        for IDcotisation, dictValeur in dictValeurs.iteritems() :
            listeLabels.append((dictValeur["{FAMILLE_NOM}"], IDcotisation))
        listeLabels.sort() 
        
        for labelDoc, IDcotisation in listeLabels :
            dictValeur = dictValeurs[IDcotisation]
            if dictValeur["select"] == True :
                
                story.append(DocAssign("IDcotisation", IDcotisation))
                nomSansCivilite = dictValeur["{FAMILLE_NOM}"]
                story.append(Bookmark(nomSansCivilite, str(IDcotisation)))
                
##                # ------------------- TITRE -----------------
##                dataTableau = []
##                largeursColonnes = [ TAILLE_CADRE_CONTENU[2], ]
##                dataTableau.append((dictCompte["titre"],))
##                texteDateReference = UTILS_Dates.DateEngFr(str(datetime.date.today()))
##                dataTableau.append((_(u"Situation au %s") % texteDateReference,))
##                style = TableStyle([
##                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
##                        ('FONT',(0,0),(0,0), "Helvetica-Bold", 19), 
##                        ('FONT',(0,1),(0,1), "Helvetica", 8), 
##                        ('LINEBELOW', (0,0), (0,0), 0.25, colors.black), 
##                        ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
##                        ])
##                tableau = Table(dataTableau, largeursColonnes)
##                tableau.setStyle(style)
##                story.append(tableau)
##                story.append(Spacer(0,30))
##                
##                    
##                couleurFond = (0.8, 0.8, 1)
##                couleurFondActivite = (0.92, 0.92, 1)
##                        
##                # TEXTE CONTENU
##                paraStyle = ParagraphStyle(name="contenu",
##                              fontName="Helvetica",
##                              fontSize=11,
##                              #leading=7,
##                              spaceBefore=0,
##                              spaceafter=0,
##                              leftIndent=6,
##                              rightIndent=6,
##                            )
##                
##                texte = dictCompte["texte"]
##                listeParagraphes = texte.split("</para>")
##                for paragraphe in listeParagraphes :
##                    textePara = Paragraph(u"%s</para>" % paragraphe, paraStyle)
##                    story.append(textePara)
                
                # Saut de page
                story.append(PageBreak())
        
        # Finalisation du PDF
        doc.build(story)
        
        # Ouverture du PDF
        if ouverture == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)





if __name__ == u"__main__":
    Impression()
