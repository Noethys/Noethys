#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import datetime
import FonctionsPerso

from Dlg import DLG_Noedoc

from Utils import UTILS_Config
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

TAILLE_CADRE_CONTENU = (5*cm, 5*cm, 14*cm, 17*cm)

##IMAGES = [
##    {
##        "nomFichier" : "Images/Special/Medecin.png",
##        "taille" : (5*cm, 5*cm),
##        "position" : (5*cm, 20*cm),
##        "conserveProportions" : True,
##    }
##]

##TEXTES = [
##    {
##        "texte" : "date",
##        "position" : (10.8*cm, 28*cm),
##        "alignement" : "gauche",
##        "police" : "Helvetica",
##        "taillePolice" : 10,
##    },
##    {
##        "texte" : ("nom", "rue", "ville"),
##        "position" : (10.8*cm, 24.5*cm),
##        "alignement" : "gauche",
##        "police" : "Helvetica",
##        "taillePolice" : 10,
##    },
##    {
##        "texte" : ("numero", "siret", "ape"),
##        "position" : (1.2*cm, 24*cm),
##        "alignement" : "gauche",
##        "police" : "Helvetica",
##        "taillePolice" : 8,
##    },
##]
    
DICT_COMPTES = {}
DICT_OPTIONS = {} 


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete


class MyCanvas(Canvas):
    def __init__(self, filename,
                 pagesize=None,
                 bottomup = 1,
                 pageCompression=1,
                 invariant = None,
                 verbosity=0):
        Canvas.__init__(self, filename, pagesize=pagesize, bottomup=bottomup, pageCompression=pageCompression,
                        invariant=invariant, verbosity=verbosity)
        self.setPageSize(TAILLE_PAGE)


def Template(canvas, doc):
    """ Première page de l'attestation """
    doc.modeleDoc.DessineFond(canvas) 
    doc.modeleDoc.DessineFormes(canvas) 

##class MyBaseDocTemplate(BaseDocTemplate):
##    def __init__(self, filename, **kw):
##        BaseDocTemplate.__init__(self, filename, **kw)
##    
##    def beforePage(self):
##        print self.pageTemplate.__dict__
##        global INFO
##        INFO = "salut"

class MyPageTemplate(PageTemplate):
    def __init__(self, id=-1, pageSize=TAILLE_PAGE, doc=None):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]
        
        # Récupère les coordonnées du cadre principal
        cadre_principal = doc.modeleDoc.FindObjet("cadre_principal")
        x, y, l, h = doc.modeleDoc.GetCoordsObjet(cadre_principal)
        global CADRE_CONTENU
        CADRE_CONTENU = (x, y, l, h)

        frame1 = Frame(x, y, l, h, id='F1', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
        PageTemplate.__init__(self, id, [frame1], Template) 

    def afterDrawPage(self, canvas, doc):
        IDcompte_payeur = doc._nameSpace["IDcompte_payeur"]
        dictCompte = DICT_COMPTES[IDcompte_payeur]
        
        # Dessin du coupon-réponse vertical
        coupon_vertical = doc.modeleDoc.FindObjet("coupon_vertical")
        if DICT_OPTIONS["coupon"] == True and coupon_vertical != None :
            x, y, largeur, hauteur = doc.modeleDoc.GetCoordsObjet(coupon_vertical)
            canvas.saveState() 
            # Ciseaux
            canvas.drawImage(Chemins.GetStaticPath("Images/Special/Ciseaux.png"), x+1*mm, y+hauteur-5*mm, 0.5*cm, 1*cm, preserveAspectRatio=True)
            # Rectangle
            canvas.setDash(3, 3)
            canvas.setLineWidth(0.25)
            canvas.setStrokeColorRGB(0, 0, 0)
            canvas.rect(x, y, largeur, hauteur, fill=0)
            # Textes
            canvas.rotate(90)
            canvas.setFont("Helvetica", 8)
            canvas.drawString(y+2*mm, -x-4*mm, _(u"Merci de joindre ce coupon à votre règlement"))
            canvas.setFont("Helvetica", 7)
            solde = dictCompte["solde_num"]#dictCompte["total"] - dictCompte["ventilation"]
            numero = dictCompte["numero"]
            nom = dictCompte["nomSansCivilite"]
            canvas.drawString(y+2*mm, -x-9*mm, u"%s - %.02f %s" % (numero, solde, SYMBOLE))
            canvas.drawString(y+2*mm, -x-12*mm, u"%s" % nom)
            # Code-barres
            if DICT_OPTIONS["codeBarre"] == True and "{CODEBARRES_NUM_RAPPEL}" in dictCompte :
                barcode = code39.Extended39(dictCompte["{CODEBARRES_NUM_RAPPEL}"], humanReadable=False)
                barcode.drawOn(canvas, y+36*mm, -x-13*mm)
            canvas.restoreState()

        # Dessin du coupon-réponse horizontal
        coupon_horizontal = doc.modeleDoc.FindObjet("coupon_horizontal")
        if DICT_OPTIONS["coupon"] == True and coupon_horizontal != None :
            x, y, largeur, hauteur = doc.modeleDoc.GetCoordsObjet(coupon_horizontal)
            canvas.saveState() 
            # Rectangle
            canvas.setDash(3, 3)
            canvas.setLineWidth(0.25)
            canvas.setStrokeColorRGB(0, 0, 0)
            canvas.rect(x, y, largeur, hauteur, fill=0)
            # Textes
            canvas.setFont("Helvetica", 8)
            canvas.drawString(x+2*mm, y+hauteur-4*mm, _(u"Merci de joindre ce coupon à votre règlement"))
            canvas.setFont("Helvetica", 7)
            solde = dictCompte["solde_num"]#dictCompte["total"] - dictCompte["ventilation"]
            numero = dictCompte["numero"]
            nom = dictCompte["nomSansCivilite"]
            canvas.drawString(x+2*mm, y+hauteur-9*mm, u"%s - %.02f %s" % (numero, solde, SYMBOLE))
            canvas.drawString(x+2*mm, y+hauteur-12*mm, u"%s" % nom)
            # Code-barres
            if DICT_OPTIONS["codeBarre"] == True and "{CODEBARRES_NUM_RAPPEL}" in dictCompte :
                barcode = code39.Extended39(dictCompte["{CODEBARRES_NUM_RAPPEL}"], humanReadable=False)
                barcode.drawOn(canvas, x+36*mm, y+hauteur-13*mm)
            # Ciseaux
            canvas.rotate(-90)
            canvas.drawImage(Chemins.GetStaticPath("Images/Special/Ciseaux.png"), -y-hauteur+1*mm, x+largeur-5*mm, 0.5*cm, 1*cm, preserveAspectRatio=True)
            canvas.restoreState()

        canvas.saveState() 
        
        # Insertion du code39
        if DICT_OPTIONS["codeBarre"] == True :
            doc.modeleDoc.DessineCodesBarres(canvas, dictChamps=dictCompte)
                
        # Insertion des lignes de textes
        doc.modeleDoc.DessineImages(canvas, dictChamps=dictCompte)
        doc.modeleDoc.DessineTextes(canvas, dictChamps=dictCompte)
        
        canvas.restoreState()

        
def Template_PagesSuivantes(canvas, doc):
    """ Première page de l'attestation """
    canvas.saveState()

    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawCentredString(10*cm, cm, str(pageNumber))

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
    def __init__(self, dictComptes={}, dictOptions={}, IDmodele=None, ouverture=True, nomFichier=None):
        """ Impression """
        global DICT_COMPTES, DICT_OPTIONS
        DICT_COMPTES = dictComptes
        DICT_OPTIONS = dictOptions
        
        # Initialisation du document
        if nomFichier == None :
            nomDoc = FonctionsPerso.GenerationNomDoc("RAPPELS", "pdf")
        else :
            nomDoc = nomFichier
        doc = BaseDocTemplate(nomDoc, pagesize=TAILLE_PAGE, showBoundary=False)
        
        # Mémorise le ID du modèle
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        doc.modeleDoc = modeleDoc

        # Vérifie qu'un cadre principal existe bien dans le document
        if doc.modeleDoc.FindObjet("cadre_principal") == None :
            raise Exception("Votre modele de document doit obligatoirement comporter un cadre principal. Retournez dans l'editeur de document et utilisez pour votre modele la commande 'Inserer un objet special > Inserer le cadre principal'.")

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
        
##        # Définit le template des pages suivantes
##        story.append(NextPageTemplate("suivante"))
        
        
        # ----------- Insertion du contenu des frames --------------
        listeNomsSansCivilite = []
        for IDcompte_payeur, dictCompte in dictComptes.items() :
            listeNomsSansCivilite.append((dictCompte["nomSansCivilite"], IDcompte_payeur))
        listeNomsSansCivilite.sort() 
        
        for nomSansCivilite, IDcompte_payeur in listeNomsSansCivilite :
            dictCompte = dictComptes[IDcompte_payeur]
            if dictCompte["select"] == True :
                
                story.append(DocAssign("IDcompte_payeur", IDcompte_payeur))
                nomSansCivilite = dictCompte["nomSansCivilite"]
                story.append(Bookmark(nomSansCivilite, str(IDcompte_payeur)))
                
                # ------------------- TITRE -----------------
                dataTableau = []
                largeursColonnes = [ TAILLE_CADRE_CONTENU[2], ]
                dataTableau.append((dictCompte["titre"],))
                texteDateReference = DateEngFr(str(datetime.date.today()))
                dataTableau.append((_(u"Situation au %s") % texteDateReference,))
                style = TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
                        ('FONT',(0,0),(0,0), "Helvetica-Bold", 19), 
                        ('FONT',(0,1),(0,1), "Helvetica", 8), 
                        ('LINEBELOW', (0,0), (0,0), 0.25, colors.black), 
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
                        ])
                tableau = Table(dataTableau, largeursColonnes)
                tableau.setStyle(style)
                story.append(tableau)
                story.append(Spacer(0,30))
                
                couleurFond = (0.8, 0.8, 1)
                couleurFondActivite = (0.92, 0.92, 1)
                        
                # TEXTE CONTENU
                paraStyle = ParagraphStyle(name="contenu",
                              fontName="Helvetica",
                              fontSize=11,
                              #leading=7,
                              spaceBefore=0,
                              spaceafter=0,
                              leftIndent=6,
                              rightIndent=6,
                            )
                
                texte = dictCompte["texte"]
                listeParagraphes = texte.split("</para>")
                for paragraphe in listeParagraphes :
                    if "<para" in paragraphe :
                        paragraphe = u"%s</para>" % paragraphe
                        textePara = Paragraph(paragraphe, paraStyle)
                        story.append(textePara)
                        if "> </para" in paragraphe :
                            story.append(Spacer(0, 13))
                
                # Saut de page
                story.append(PageBreak())
        
        # Finalisation du PDF
        doc.build(story)
        
        # Ouverture du PDF
        if ouverture == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)





if __name__ == u"__main__":
    Impression()
