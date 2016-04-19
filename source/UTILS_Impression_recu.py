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
import os
import FonctionsPerso
import UTILS_Conversion
import UTILS_Dates
import wx
import CTRL_Bouton_image

import DLG_Noedoc

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro"))
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", _(u"Centime"))

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

TAILLE_PAGE = A4
LARGEUR_PAGE = TAILLE_PAGE[0]
HAUTEUR_PAGE = TAILLE_PAGE[1]
TAILLE_CADRE_CONTENU = (5*cm, 5*cm, 14*cm, 17*cm)
DICT_VALEURS = {}


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text


def Template(canvas, doc):
    """ Première page de l'attestation """
    doc.modeleDoc.DessineFond(canvas) 
    doc.modeleDoc.DessineFormes(canvas) 
    doc.modeleDoc.DessineImages(canvas, dictChamps=DICT_VALEURS)
    doc.modeleDoc.DessineTextes(canvas, dictChamps=DICT_VALEURS)


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
        doc.modeleDoc.DessineImages(canvas, dictChamps=DICT_VALEURS)
        doc.modeleDoc.DessineTextes(canvas, dictChamps=DICT_VALEURS)
        doc.modeleDoc.DessineCodesBarres(canvas, dictChamps=DICT_VALEURS)

        
        
class Impression():
    def __init__(self, dictValeurs={}, IDmodele=None, nomDoc=FonctionsPerso.GenerationNomDoc("RECU_REGLEMENT", "pdf"), afficherDoc=True):
        """ Impression """
        global DICT_VALEURS
        DICT_VALEURS = dictValeurs
        
        # Initialisation du document
        doc = BaseDocTemplate(nomDoc, pagesize=TAILLE_PAGE, showBoundary=False)

        # Mémorise le ID du modèle
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        doc.modeleDoc = modeleDoc

        # Vérifie qu'un cadre principal existe bien dans le document
        if doc.modeleDoc.FindObjet("cadre_principal") == None :
            raise Exception("Votre modele de document doit obligatoirement comporter un cadre principal. Retournez dans l'editeur de document et utilisez pour votre modele la commande 'Inserer un objet special > Inserer le cadre principal'.")

        # Mémorise le ID du modèle
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        doc.modeleDoc = modeleDoc
        
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
        
        # ------------------- TITRE -----------------
        dataTableau = []
        largeursColonnes = [ TAILLE_CADRE_CONTENU[2], ]
        dataTableau.append((_(u"Reçu de règlement"),))
        dataTableau.append((u"",))
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

        if DICT_VALEURS["intro"] != None :
            texteIntro = DICT_VALEURS["intro"]
            story.append(Paragraph(u"<i>%s</i>" % texteIntro, paraStyleIntro))
            story.append(Spacer(0,20))
            
            
        couleurFond = (0.8, 0.8, 1)
                
        # ------------------- TABLEAU CONTENU -----------------
        
        dataTableau = []
        largeursColonnes = [ 120, 280]
        
        paraStyle = ParagraphStyle(name="detail",
                                  fontName="Helvetica-Bold",
                                  fontSize=9,
                                )
        dataTableau.append( (_(u"Caractéristiques du règlement"), "") )
        montantEnLettres = UTILS_Conversion.trad(DICT_VALEURS["montant"], MONNAIE_SINGULIER, MONNAIE_DIVISION).strip() 
        dataTableau.append( (_(u"Montant du règlement :"), Paragraph(montantEnLettres.capitalize(), paraStyle) ) )
        dataTableau.append( (_(u"Mode de règlement :"), Paragraph(DICT_VALEURS["nomMode"], paraStyle) ) )
        dataTableau.append( (_(u"Nom du payeur :"), Paragraph(DICT_VALEURS["nomPayeur"], paraStyle) ) )
        if DICT_VALEURS["nomEmetteur"] != None : dataTableau.append( (_(u"Nom de l'émetteur :"), Paragraph(DICT_VALEURS["nomEmetteur"], paraStyle) ) )
        if DICT_VALEURS["numPiece"] not in ("", None) : dataTableau.append( (_(u"Numéro de pièce :"), Paragraph(DICT_VALEURS["numPiece"], paraStyle) ) )
        
        style = TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
                ('FONT', (0, 0), (0, -1), "Helvetica", 9), 
                ('FONT', (1, 0), (1, -1), "Helvetica-Bold", 9), 
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'), 
                
                ('FONT', (0, 0), (0, 0), "Helvetica", 7), 
                ('SPAN', (0, 0), (-1, 0)), 
                ('BACKGROUND', (0, 0), (-1, 0), couleurFond),
                
                ])
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        
        # --------------------- LISTE DES PRESTATIONS ----------------
        listePrestations = dictValeurs["prestations"]
        if len(listePrestations) > 0 :
            
            story.append(Spacer(0,20))
            textePrestations = _(u"En paiement des prestations suivantes :")
            story.append(Paragraph(u"<i>%s</i>" % textePrestations, paraStyleIntro))
            story.append(Spacer(0,20))

            dataTableau = [(_(u"Date"), _(u"Activité"), _(u"Individu"), _(u"Intitulé"), _(u"Part utilisée")),]
            largeursColonnes = [50, 95, 70, 135, 50]

            paraStyle = ParagraphStyle(name="detail",
                                      fontName="Helvetica",
                                      fontSize=7,
                                      leading=7,
                                      spaceBefore=0,
                                      spaceAfter=0,
                                      )

            for dictPrestation in listePrestations :
                date = UTILS_Dates.DateDDEnFr(dictPrestation["date"])
                activite = dictPrestation["nomActivite"]
                individu = dictPrestation["prenomIndividu"]
                label = dictPrestation["label"]
                montant = dictPrestation["montant"]
                ventilation = dictPrestation["ventilation"]
                
                dataTableau.append((
                    Paragraph(u"<para align='center'>%s</para>"% date, paraStyle), 
                    Paragraph(activite, paraStyle),  
                    Paragraph(individu, paraStyle),  
                    Paragraph(label, paraStyle), 
                    Paragraph(u"<para align='right'>%.2f %s</para>" % (ventilation, SYMBOLE), paraStyle), 
                    ))
                        
            style = TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('FONT', (0, 0), (-1, -1), "Helvetica", 7), 

                    ('TOPPADDING', (0, 1), (-1, -1), 1), 
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 3), 
        
                    # Ligne Entetes
                    ('FONT', (0, 0), (-1, 0), "Helvetica", 7), 
                    ('BACKGROUND', (0, 0), (-1, 0), couleurFond),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)

        
        # Enregistrement et ouverture du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur d'édition"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        if afficherDoc == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)


if __name__ == u"__main__":
    Impression()
