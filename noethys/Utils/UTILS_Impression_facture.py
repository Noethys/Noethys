#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Dlg import DLG_Noedoc

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Dates
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
CADRE_CONTENU = (5*cm, 5*cm, 14*cm, 17*cm)
    
DICT_VALEURS = {}
DICT_OPTIONS = {} 


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete

def GetDatesListes(listeDates):
    listeDatesTemp = []
    for dictTemp in listeDates :
        if type(dictTemp) == dict :
            date = dictTemp["date"]
        else :
            date = dictTemp
        if date not in listeDatesTemp :
            listeDatesTemp.append(date)
    return listeDatesTemp
    
def ConvertCouleurWXpourPDF(couleurwx=(0, 0, 0)):
    return (couleurwx[0]/255.0, couleurwx[1]/255.0, couleurwx[2]/255.0)

def ConvertCouleurPDFpourWX(couleurpdf=(0, 0, 0)):
    return (couleurpdf[0]*255.0, couleurpdf[1]*255.0, couleurpdf[2]*255.0)

def Template(canvas, doc):
    """ Première page """
    doc.modeleDoc.DessineFond(canvas) 
    doc.modeleDoc.DessineFormes(canvas) 



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
        dictValeur = DICT_VALEURS[IDcompte_payeur]
        
        # Dessin du coupon-réponse vertical
        coupon_vertical = doc.modeleDoc.FindObjet("coupon_vertical")
        if "afficher_coupon_reponse" in DICT_OPTIONS and DICT_OPTIONS["afficher_coupon_reponse"] == True and coupon_vertical != None :
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
            solde = dictValeur["total"] - dictValeur["ventilation"]
            if DICT_OPTIONS["integrer_impayes"] == True :
                solde += dictValeur["total_reports"]
            numero = dictValeur["numero"]
            nom = dictValeur["nomSansCivilite"]
            canvas.drawString(y+2*mm, -x-9*mm, u"%s - %.02f %s" % (numero, solde, SYMBOLE))
            canvas.drawString(y+2*mm, -x-12*mm, u"%s" % nom)
            # Code-barres
            if DICT_OPTIONS["afficher_codes_barres"] == True and "{CODEBARRES_NUM_FACTURE}" in dictValeur :
                barcode = code39.Extended39(dictValeur["{CODEBARRES_NUM_FACTURE}"], humanReadable=False)
                barcode.drawOn(canvas, y+36*mm, -x-13*mm)
            canvas.restoreState()

        # Dessin du coupon-réponse horizontal
        coupon_horizontal = doc.modeleDoc.FindObjet("coupon_horizontal")
        if "afficher_coupon_reponse" in DICT_OPTIONS and DICT_OPTIONS["afficher_coupon_reponse"] == True and coupon_horizontal != None :
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
            solde = dictValeur["total"] - dictValeur["ventilation"]
            if DICT_OPTIONS["integrer_impayes"] == True :
                solde += dictValeur["total_reports"]
            numero = dictValeur["numero"]
            nom = dictValeur["nomSansCivilite"]
            canvas.drawString(x+2*mm, y+hauteur-9*mm, u"%s - %.02f %s" % (numero, solde, SYMBOLE))
            canvas.drawString(x+2*mm, y+hauteur-12*mm, u"%s" % nom)
            # Code-barres
            if DICT_OPTIONS["afficher_codes_barres"] == True :
                barcode = code39.Extended39(dictValeur["{CODEBARRES_NUM_FACTURE}"], humanReadable=False)
                barcode.drawOn(canvas, x+36*mm, y+hauteur-13*mm)
            # Ciseaux
            canvas.rotate(-90)
            canvas.drawImage(Chemins.GetStaticPath("Images/Special/Ciseaux.png"), -y-hauteur+1*mm, x+largeur-5*mm, 0.5*cm, 1*cm, preserveAspectRatio=True)
            canvas.restoreState()

        canvas.saveState() 
        
        # Insertion du code39
        if "afficher_codes_barres" in DICT_OPTIONS and DICT_OPTIONS["afficher_codes_barres"] == True :
            doc.modeleDoc.DessineCodesBarres(canvas, dictChamps=dictValeur)

        # Insertion des lignes de textes
        doc.modeleDoc.DessineImages(canvas, dictChamps=dictValeur)
        doc.modeleDoc.DessineTextes(canvas, dictChamps=dictValeur)
        
        canvas.restoreState()

        
def Template_PagesSuivantes(canvas, doc):
    """ Première page """
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
    def __init__(self, dictValeurs={}, dictOptions={}, IDmodele=None, mode="facture", ouverture=True, nomFichier=None, titre=None):
        """ Impression """
        global DICT_VALEURS, DICT_OPTIONS
        DICT_VALEURS = dictValeurs
        DICT_OPTIONS = dictOptions
        self.mode = mode
        
        detail = 0
        if dictOptions["affichage_prestations"] != None :
            detail = dictOptions["affichage_prestations"]
        
        # Initialisation du document
        if nomFichier == None :
            nomDoc = FonctionsPerso.GenerationNomDoc(mode + "s", "pdf")
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
        for IDcompte_payeur, dictValeur in dictValeurs.items() :
            listeNomsSansCivilite.append((dictValeur["nomSansCivilite"], IDcompte_payeur))
        listeNomsSansCivilite.sort() 
        
        for nomSansCivilite, IDcompte_payeur in listeNomsSansCivilite :
            dictValeur = dictValeurs[IDcompte_payeur]
            if dictValeur["select"] == True :
                
                story.append(DocAssign("IDcompte_payeur", IDcompte_payeur))
                nomSansCivilite = dictValeur["nomSansCivilite"]
                story.append(Bookmark(nomSansCivilite, str(IDcompte_payeur)))
                
                # ------------------- TITRE -----------------
                if dictOptions["afficher_titre"] == True :
                    if titre == None :
                        if mode == "facture" : titre = _(u"Facture")
                        if mode == "attestation" : titre = _(u"Attestation de présence")
                        if mode == "devis": titre = _(u"Devis")
                        if "texte_titre" in dictValeur : 
                            titre = dictValeur["texte_titre"]
                    dataTableau = []
                    largeursColonnes = [ CADRE_CONTENU[2], ]
                    dataTableau.append((titre,))
                    texteDateDebut = DateEngFr(str(dictValeur["date_debut"]))
                    texteDateFin = DateEngFr(str(dictValeur["date_fin"]))
                    if dictOptions["afficher_periode"] == True :
                        dataTableau.append((_(u"Période du %s au %s") % (texteDateDebut, texteDateFin),))
                    styles = [
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", dictOptions["taille_texte_titre"]), 
                            ('LINEBELOW', (0,0), (0,0), 0.25, colors.black), 
                            ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
                            ]
                    
                    if dictOptions["afficher_periode"] == True :
                        styles.append(('FONT',(0,1),(0,1), "Helvetica", dictOptions["taille_texte_periode"]))
                    tableau = Table(dataTableau, largeursColonnes)
                    tableau.setStyle(TableStyle(styles))
                    story.append(tableau)
                    story.append(Spacer(0,20))

                if dictOptions["texte_introduction"] != "" :
                    paraStyle = ParagraphStyle(name="introduction",
                                          fontName="Helvetica",
                                          fontSize=dictOptions["taille_texte_introduction"],
                                          leading=14,
                                          spaceBefore=0,
                                          spaceafter=0,
                                          leftIndent=5,
                                          rightIndent=5,
                                          alignment=dictOptions["alignement_texte_introduction"],
                                          backColor=ConvertCouleurWXpourPDF(dictOptions["couleur_fond_introduction"]),
                                          borderColor=ConvertCouleurWXpourPDF(dictOptions["couleur_bord_introduction"]),
                                          borderWidth=0.5,
                                          borderPadding=5,
                                        )
                    texte = dictValeur["texte_introduction"].replace("\\n", "<br/>")
                    if dictOptions["style_texte_introduction"] == 0 : texte = u"<para>%s</para>" % texte
                    if dictOptions["style_texte_introduction"] == 1 : texte = u"<para><i>%s</i></para>" % texte
                    if dictOptions["style_texte_introduction"] == 2 : texte = u"<para><b>%s</b></para>" % texte
                    if dictOptions["style_texte_introduction"] == 3 : texte = u"<para><i><b>%s</b></i></para>" % texte
                    story.append(Paragraph(texte, paraStyle))
                    story.append(Spacer(0,20))

                    
                couleurFond = ConvertCouleurWXpourPDF(dictOptions["couleur_fond_1"]) # (0.8, 0.8, 1)
                couleurFondActivite = ConvertCouleurWXpourPDF(dictOptions["couleur_fond_2"]) # (0.92, 0.92, 1)

                # ------------------- TABLEAU CONTENU -----------------
                montantPeriode = FloatToDecimal(0.0)
                montantVentilation = FloatToDecimal(0.0)
                nbre_total_prestations_anterieures = 0

                # Recherche si TVA utilisée
                activeTVA = False
                for IDindividu, dictIndividus in dictValeur["individus"].items() :
                    for IDactivite, dictActivites in dictIndividus["activites"].items() :
                        for date, dictDates in dictActivites["presences"].items() :
                            for dictPrestation in dictDates["unites"] :
                                if dictPrestation["tva"] != None and dictPrestation["tva"] != 0.0 :
                                    activeTVA = True

                # Remplissage
                listeIndividusTemp = []
                for IDindividu, dictIndividus in dictValeur["individus"].items() :
                    listeIndividusTemp.append((dictIndividus["texte"], IDindividu, dictIndividus))
                listeIndividusTemp.sort() 
                
                for texteTemp, IDindividu, dictIndividus in listeIndividusTemp :
                    
                    if dictIndividus["select"] == True :

                        nbre_prestations_anterieures = 0
                        listeIndexActivites = []
                        montantPeriode += dictIndividus["total"]
                        montantVentilation += dictIndividus["ventilation"]
                        total_montantHT = 0.0
                        
                        # Initialisation des largeurs de tableau
                        largeurColonneDate = dictOptions["largeur_colonne_date"]
                        largeurColonneMontantHT = dictOptions["largeur_colonne_montant_ht"]
                        largeurColonneTVA = dictOptions["largeur_colonne_montant_tva"]
                        largeurColonneMontantTTC = dictOptions["largeur_colonne_montant_ttc"]
                        largeurColonneBaseTTC = largeurColonneMontantTTC
                        
                        if activeTVA == True and detail == 0 :
                            largeurColonneIntitule = CADRE_CONTENU[2] - largeurColonneDate - largeurColonneMontantHT - largeurColonneTVA - largeurColonneMontantTTC
                            largeursColonnes = [ largeurColonneDate, largeurColonneIntitule, largeurColonneMontantHT, largeurColonneTVA, largeurColonneMontantTTC]
                        else :
                            if detail != 0 :
                                largeurColonneIntitule = CADRE_CONTENU[2] - largeurColonneDate - largeurColonneBaseTTC - largeurColonneMontantTTC
                                largeursColonnes = [ largeurColonneDate, largeurColonneIntitule, largeurColonneBaseTTC, largeurColonneMontantTTC]
                            else :
                                largeurColonneIntitule = CADRE_CONTENU[2] - largeurColonneDate - largeurColonneMontantTTC
                                largeursColonnes = [ largeurColonneDate, largeurColonneIntitule, largeurColonneMontantTTC]

                        # Recherche de la classe de l'individu
                        nom_classe = ""
                        if "scolarites" in dictIndividus and dictIndividus["scolarites"]:
                            for dict_scolarite in dictIndividus["scolarites"]:
                                if dict_scolarite["date_fin"] >= dictValeur["date_debut"] and dict_scolarite["date_debut"] <= dictValeur["date_fin"]:
                                    nom_classe = u"<font size=7> (%s - %s)</font>" % (dict_scolarite["nom_classe"], dict_scolarite["nom_ecole"])
                                    break

                        # Insertion du nom de l'individu
                        paraStyle = ParagraphStyle(name="individu",
                                              fontName="Helvetica",
                                              fontSize=dictOptions["taille_texte_individu"],
                                              leading=dictOptions["taille_texte_individu"],
                                              spaceBefore=0,
                                              spaceafter=0,
                                            )
                        texteIndividu = Paragraph(dictIndividus["texte"] + nom_classe, paraStyle)
                        dataTableau = []
                        dataTableau.append([texteIndividu,])
                        tableau = Table(dataTableau, [CADRE_CONTENU[2],])
                        listeStyles = [
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('FONT', (0, 0), (-1, -1), "Helvetica", dictOptions["taille_texte_individu"]), 
                                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                                ('BACKGROUND', (0, 0), (-1, 0), couleurFond),
                                ]
                        tableau.setStyle(TableStyle(listeStyles))
                        story.append(tableau)
                        
                        # Insertion du nom de l'activité
                        listeIDactivite = []
                        for IDactivite, dictActivites in dictIndividus["activites"].items() :
                            listeIDactivite.append((dictActivites["texte"], IDactivite, dictActivites))
                        listeIDactivite.sort() 
                        
                        for texteActivite, IDactivite, dictActivites in listeIDactivite :

                            texteActivite = dictActivites["texte"]
                            if texteActivite != None :
                                dataTableau = []
                                dataTableau.append([texteActivite,])
                                tableau = Table(dataTableau, [CADRE_CONTENU[2],])
                                listeStyles = [
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('FONT', (0, 0), (-1, -1), "Helvetica", dictOptions["taille_texte_activite"]),
                                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('BACKGROUND', (0, 0), (-1, 0), couleurFondActivite),
                                    ]
                                tableau.setStyle(TableStyle(listeStyles))
                                story.append(tableau)

                            # Style de paragraphe normal
                            paraStyle = ParagraphStyle(name="prestation",
                                          fontName="Helvetica",
                                          fontSize=dictOptions["taille_texte_prestation"],
                                          leading=dictOptions["taille_texte_prestation"],
                                          spaceBefore=0,
                                          spaceAfter=0,
                                          )

                            paraLabelsColonnes = ParagraphStyle(name="paraLabelsColonnes",
                                          fontName="Helvetica",
                                          fontSize=dictOptions["taille_texte_noms_colonnes"],
                                          leading=dictOptions["taille_texte_noms_colonnes"],
                                          spaceBefore=0,
                                          spaceAfter=0,
                                          )
                                

                            if detail != 0 :
                                
                                # -------------- MODE REGROUPE ----------------
                                
                                # Regroupement par prestations identiques
                                dictRegroupement = {}
                                for date, dictDates in dictActivites["presences"].items() :
                                    total = dictDates["total"]
                                    for dictPrestation in dictDates["unites"] :
                                        label = dictPrestation["label"]
                                        listeDatesUnite = GetDatesListes(dictPrestation["listeDatesConso"])
                                        montant = dictPrestation["montant"]
                                        deductions = dictPrestation["deductions"]
                                        tva = dictPrestation["tva"]

                                        if detail in (1, 3): labelkey = label
                                        if detail in (2, 4): labelkey = label + " P.U. " + "%.2f %s" % (montant, SYMBOLE)

                                        # Si c'est une prestation antérieure
                                        if date < str(dictValeur["date_debut"]) :
                                            nbre_prestations_anterieures += 1
                                            nbre_total_prestations_anterieures += 1
                                            label += u"*"

                                        if (labelkey in dictRegroupement) == False :
                                            dictRegroupement[labelkey] = {"labelpresta" : label, "total" : 0, "nbre" : 0, "base" : 0, "dates_forfait" : None, "dates": []}
                                            dictRegroupement[labelkey]["base"] = montant
                                        
                                        dictRegroupement[labelkey]["total"] += montant
                                        dictRegroupement[labelkey]["nbre"] += 1
                                        dictRegroupement[labelkey]["dates"] += listeDatesUnite
                                        
                                        if detail in (1, 3):
                                            dictRegroupement[labelkey]["base"] = dictRegroupement[labelkey]["total"] / dictRegroupement[labelkey]["nbre"]

                                        if dictPrestation.get("forfait_date_debut"):
                                            dictRegroupement[labelkey]["dates_forfait"] = _(u"<font size=5>Du %s au %s</font>") % (UTILS_Dates.DateDDEnFr(dictPrestation["forfait_date_debut"]), UTILS_Dates.DateDDEnFr(dictPrestation["forfait_date_fin"]))
                                        elif len(listeDatesUnite) > 1 :
                                            listeDatesUnite.sort()
                                            date_debut = listeDatesUnite[0]
                                            date_fin = listeDatesUnite[-1]
                                            nbreDates = len(listeDatesUnite)
                                            dictRegroupement[labelkey]["dates_forfait"] = _(u"<BR/><font size=5>Du %s au %s soit %d jours</font>") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nbreDates)

                                # Insertion des prestations regroupées
                                listeLabels = list(dictRegroupement.keys()) 
                                listeLabels.sort()

                                dataTableau = [(
                                    Paragraph(_(u"<para align='center'>Quantité</para>"), paraLabelsColonnes), 
                                    Paragraph(_(u"<para align='center'>Prestation</para>"), paraLabelsColonnes),
                                    Paragraph(_(u"<para align='center'>Base</para>"), paraLabelsColonnes),
                                    Paragraph(_(u"<para align='center'>Montant</para>"), paraLabelsColonnes), 
                                    ),]

                                for labelkey in listeLabels :
                                    label = dictRegroupement[labelkey]["labelpresta"]
                                    nbre = dictRegroupement[labelkey]["nbre"]
                                    total = dictRegroupement[labelkey]["total"]
                                    base = dictRegroupement[labelkey]["base"]

                                    # Ajout des dates
                                    if detail in (3, 4) and dictRegroupement[labelkey]["dates"]:
                                        dictRegroupement[labelkey]["dates"].sort()
                                        label += u"<br/><font size=5>(%s)</font>" % ", ".join([UTILS_Dates.DateDDEnFr(date) for date in dictRegroupement[labelkey]["dates"]])

                                    # recherche d'un commentaire
                                    if "dictCommentaires" in dictOptions :
                                        key = (label, IDactivite)
                                        if key in dictOptions["dictCommentaires"] :
                                            commentaire = dictOptions["dictCommentaires"][key]
                                            label = u"%s <i><font color='#939393'>%s</font></i>" % (label, commentaire)
                                            
                                    # Formatage du label
                                    intitule = Paragraph(label, paraStyle)
                                    
                                    # Rajout des dates de forfait
                                    #dates_forfait = dictRegroupement[label]["dates_forfait"]
                                    #if dates_forfait != None :
                                    #    intitule = [intitule, Paragraph(dates_forfait, paraStyle)]

                                    dataTableau.append([Paragraph(u"<para align='center'>%d</para>" % nbre, paraStyle), intitule, Paragraph(u"<para align='center'>%.02f %s</para>" % (base, SYMBOLE), paraStyle), Paragraph(u"<para align='center'>%.02f %s</para>" % (total, SYMBOLE), paraStyle)])
 
                            else :
                                
                                # -------------------------------------------------------------- MODE DETAILLE ------------------------------------------------------------------


                                # Insertion de la date
                                listeDates = []
                                for date, dictDates in dictActivites["presences"].items() :
                                    listeDates.append(date)
                                listeDates.sort() 
                                
                                paraStyle = ParagraphStyle(name="prestation",
                                              fontName="Helvetica",
                                              fontSize=dictOptions["taille_texte_prestation"],
                                              leading=dictOptions["taille_texte_prestation"],
                                              spaceBefore=0,
                                              spaceAfter=0,
                                              )

                                dataTableau = []

                                if activeTVA == True :
                                    dataTableau.append([
                                        Paragraph(_(u"<para align='center'>Date</para>"), paraLabelsColonnes), 
                                        Paragraph(_(u"<para align='center'>Prestation</para>"), paraLabelsColonnes), 
                                        Paragraph(_(u"<para align='center'>Montant HT</para>"), paraLabelsColonnes), 
                                        Paragraph(_(u"<para align='center'>Taux TVA</para>"), paraLabelsColonnes), 
                                        Paragraph(_(u"<para align='center'>Montant TTC</para>"), paraLabelsColonnes), 
                                        ])

                                for date in listeDates :
                                    dictDates = dictActivites["presences"][date]

                                    dateFr = dictDates["texte"]
                                    prestations = dictDates["unites"]
                                    
                                    # Insertion des unités de présence
                                    listeIntitules = []
                                    listeMontantsHT = []
                                    listeTVA = []
                                    listeMontantsTTC = []
                                    texteIntitules = u""
                                    texteMontantsHT = u""
                                    texteTVA = u""
                                    texteMontantsTTC = u""
                                    
                                    # Tri par ordre alpha des prestations
                                    listeDictPrestations = []
                                    for dictPrestation in prestations :
                                        listeDictPrestations.append((dictPrestation["label"], dictPrestation))
                                    listeDictPrestations.sort(key=lambda e: e[0])
                                    
                                    for labelTemp, dictPrestation in listeDictPrestations :
                                        label = dictPrestation["label"]
                                        listeDatesUnite = GetDatesListes(dictPrestation["listeDatesConso"])
                                        montant_initial = dictPrestation["montant_initial"]
                                        montant = dictPrestation["montant"]
                                        deductions = dictPrestation["deductions"]
                                        tva = dictPrestation["tva"]

                                        # Date
                                        texteDate = Paragraph("<para align='center'>%s</para>" % dateFr, paraStyle)
                                        
                                        # recherche d'un commentaire
                                        if "dictCommentaires" in dictOptions :
                                            key = (label, IDactivite)
                                            if key in dictOptions["dictCommentaires"] :
                                                commentaire = dictOptions["dictCommentaires"][key]
                                                label = "%s <i><font color='#939393'>%s</font></i>" % (label, commentaire)

                                        # Si c'est une prestation antérieure
                                        if date < str(dictValeur["date_debut"]):
                                            nbre_prestations_anterieures += 1
                                            nbre_total_prestations_anterieures += 1
                                            label += u"*"

                                        # Affiche le Label de la prestation
                                        listeIntitules.append(Paragraph(label, paraStyle)) 
                                        
                                        # Recherche si c'est un forfait
                                        if dictPrestation.get("forfait_date_debut"):
                                            label = _(u"<font size=5>Du %s au %s</font>") % (UTILS_Dates.DateDDEnFr(dictPrestation["forfait_date_debut"]), UTILS_Dates.DateDDEnFr(dictPrestation["forfait_date_fin"]))
                                            listeIntitules.append(Paragraph(label, paraStyle))
                                            listeMontantsTTC.append(Paragraph("&nbsp;", paraStyle))
                                        elif len(listeDatesUnite) > 1 :
                                            listeDatesUnite.sort()
                                            date_debut = listeDatesUnite[0]
                                            date_fin = listeDatesUnite[-1]
                                            nbreDates = len(listeDatesUnite)
                                            label = _(u"<font size=5>Du %s au %s soit %d jours</font>") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nbreDates)
                                            listeIntitules.append(Paragraph(label, paraStyle))
                                            listeMontantsTTC.append(Paragraph("&nbsp;", paraStyle))
                                                                                
                                        # TVA
                                        if activeTVA == True :
                                            if tva == None : tva = 0.0
                                            montantHT = (100.0 * float(montant)) / (100 + float(tva)) #montant - montant * 1.0 * float(tva) / 100
                                            total_montantHT += montantHT
                                            listeMontantsHT.append(Paragraph(u"<para align='center'>%.02f %s</para>" % (montantHT, SYMBOLE), paraStyle))
                                            listeTVA.append(Paragraph(u"<para align='center'>%.02f %%</para>" % tva, paraStyle))
                                        else :
                                            listeMontantsHT.append("")
                                            listeTVA.append("")
                                            
                                        # Affiche total
                                        listeMontantsTTC.append(Paragraph(u"<para align='center'>%.02f %s</para>" % (montant, SYMBOLE), paraStyle)) 
                                    
                                        # Déductions
                                        if len(deductions) > 0 :
                                            for dictDeduction in deductions :
                                                listeIntitules.append(Paragraph(u"<para align='left'><font size=5 color='#939393'>- %.02f %s : %s</font></para>" % (dictDeduction["montant"], SYMBOLE, dictDeduction["label"]), paraStyle))
                                                #listeIntitules.append(Paragraph(u"<para align='left'><font size=5 color='#939393'>%s</font></para>" % dictDeduction["label"], paraStyle))
                                                listeMontantsHT.append(Paragraph("&nbsp;", paraStyle))
                                                listeTVA.append(Paragraph("&nbsp;", paraStyle))
                                                listeMontantsTTC.append(Paragraph("&nbsp;", paraStyle))
                                                #listeMontantsTTC.append(Paragraph(u"<para align='center'><font size=5 color='#939393'>- %.02f %s</font></para>" % (dictDeduction["montant"], SYMBOLE), paraStyle)) 
                                                
                                        
                                    if len(listeIntitules) == 1 :
                                        texteIntitules = listeIntitules[0]
                                        texteMontantsHT = listeMontantsHT[0]
                                        texteTVA = listeTVA[0]
                                        texteMontantsTTC = listeMontantsTTC[0]
                                    if len(listeIntitules) > 1 :
                                        texteIntitules = listeIntitules
                                        texteMontantsHT = listeMontantsHT
                                        texteTVA = listeTVA
                                        texteMontantsTTC = listeMontantsTTC
                                                                        
                                    if activeTVA == True :
                                        dataTableau.append([texteDate, texteIntitules, texteMontantsHT, texteTVA, texteMontantsTTC])
                                    else :
                                        dataTableau.append([texteDate, texteIntitules, texteMontantsTTC])
                                    
                            # Style du tableau des prestations
                            tableau = Table(dataTableau, largeursColonnes)
                            listeStyles = [
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('FONT', (0, 0), (-1, -1), "Helvetica", dictOptions["taille_texte_prestation"]), 
                                ('GRID', (0, 0), (-1,-1), 0.25, colors.black), 
                                ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
                                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                ('TOPPADDING', (0, 0), (-1, -1), 1), 
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 3), 
                                ]
                            tableau.setStyle(TableStyle(listeStyles))
                            story.append(tableau)

                        # Préparation du texet des prestations antérieures
                        if nbre_prestations_anterieures == 0 :
                            texte_prestations_anterieures = ""
                        elif nbre_prestations_anterieures == 1 :
                            texte_prestations_anterieures = _(u"* 1 prestation antérieure reportée")
                        else :
                            texte_prestations_anterieures = _(u"* %d prestations antérieures reportées") % nbre_prestations_anterieures

                        # Insertion des totaux
                        dataTableau = []
                        if activeTVA == True and detail == 0 :
                            dataTableau.append([texte_prestations_anterieures, "", Paragraph("<para align='center'>%.02f %s</para>" % (total_montantHT, SYMBOLE), paraStyle), "", Paragraph("<para align='center'>%.02f %s</para>" % (dictIndividus["total"], SYMBOLE), paraStyle)])
                        else :
                            if detail != 0 :
                                dataTableau.append([texte_prestations_anterieures, "", "", Paragraph("<para align='center'>%.02f %s</para>" % (dictIndividus["total"], SYMBOLE) , paraStyle)])
                            else :
                                dataTableau.append([texte_prestations_anterieures, "", Paragraph("<para align='center'>%.02f %s</para>" % (dictIndividus["total"], SYMBOLE) , paraStyle)])
                        
                        listeStyles = [
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('FONT', (0, 0), (-1, -1), "Helvetica", dictOptions["taille_texte_prestation"]), 
                                ('GRID', (-1, -1), (-1,-1), 0.25, colors.black), 
                                ('ALIGN', (-1, -1), (-1, -1), 'CENTRE'),
                                ('BACKGROUND', (-1, -1), (-1, -1), couleurFond), 
                                ('TOPPADDING', (0, 0), (-1, -1), 1), 
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                                ('SPAN', (0, -1), (1, -1)), # Fusion de la dernière ligne pour le texte_prestations_anterieures
                                ('FONT', (0, -1), (0, -1), "Helvetica", dictOptions["taille_texte_prestations_anterieures"]),
                            ]

                        if activeTVA == True and detail == 0:
                            listeStyles.append(('BACKGROUND', (-3, -1), (-3, -1), couleurFond))
                            listeStyles.append(('GRID', (-3, -1), (-3, -1), 0.25, colors.black))
                            
                        # Création du tableau
                        tableau = Table(dataTableau, largeursColonnes)
                        tableau.setStyle(TableStyle(listeStyles))
                        story.append(tableau)
                        story.append(Spacer(0, 10))
                
                # Intégration des messages, des reports et des qf
                listeMessages = []
                paraStyle = ParagraphStyle(name="message",
                                          fontName="Helvetica",
                                          fontSize=dictOptions["taille_texte_messages"],
                                          leading=dictOptions["taille_texte_messages"],
                                          #spaceBefore=0,
                                          spaceAfter=2,
                                        )
                
                # Date d'échéance
##                if dictOptions["echeance"] != None :
##                    listeMessages.append(Paragraph(dictOptions["echeance"], paraStyle))

                # Texte Prestations antérieures
                texte_prestations_anterieures = dictOptions["texte_prestations_anterieures"]
                if nbre_total_prestations_anterieures > 0 and len(texte_prestations_anterieures) > 0 :
                    texte = _(u"<b>%d prestations antérieures : </b>%s") % (nbre_total_prestations_anterieures, texte_prestations_anterieures)
                    listeMessages.append(Paragraph(texte, paraStyle))

                # QF aux dates de facture
                if mode == "facture" and dictOptions["afficher_qf_dates"] == True :
                    dictQfdates = dictValeur["qfdates"]
                    listeDates = list(dictQfdates.keys()) 
                    listeDates.sort() 
                    if len(listeDates) > 0 :
                        for dates in listeDates :
                            qf = dictQfdates[dates]
                            texteQf = _(u"<b>Votre quotient familial : </b>Votre QF est de %s sur la période %s.") % (qf, dates)
                            listeMessages.append(Paragraph(texteQf, paraStyle))

                # Reports
                if mode == "facture" and dictOptions["afficher_impayes"] == True :
                    dictReports = dictValeur["reports"]
                    listePeriodes = list(dictReports.keys()) 
                    listePeriodes.sort() 
                    if len(listePeriodes) > 0 :
                        if dictOptions["integrer_impayes"] == True :
                            texteReport = _(u"<b>Détail des impayés : </b>")
                        else :
                            texteReport = _(u"<b>Impayés : </b>Merci de bien vouloir nous retourner également le règlement des prestations impayées suivantes : ")
                        for periode in listePeriodes :
                            annee, mois = periode
                            nomPeriode = PeriodeComplete(mois, annee)
                            montant_impaye = dictReports[periode]
                            texteReport += u"%s (%.02f %s), " % (nomPeriode, montant_impaye, SYMBOLE)
                        texteReport = texteReport[:-2] + u"."
                        listeMessages.append(Paragraph(texteReport, paraStyle))
                
                # Règlements
                if mode == "facture" and dictOptions["afficher_reglements"] == True :
                    dictReglements = dictValeur["reglements"]
                    if len(dictReglements) > 0 :
                        listeTextesReglements = []
                        for IDreglement, dictTemp in dictReglements.items() :
                            if dictTemp["emetteur"] not in ("", None) :
                                emetteur = u" (%s) " % dictTemp["emetteur"]
                            else :
                                emetteur = ""
                            if dictTemp["numero"] not in ("", None) :
                                numero = u" n°%s " % dictTemp["numero"]
                            else :
                                numero = ""
                                
                            montantReglement = u"%.02f %s" % (dictTemp["montant"], SYMBOLE)
                            montantVentilation = u"%.02f %s" % (dictTemp["ventilation"], SYMBOLE)
                            if dictTemp["ventilation"] != dictTemp["montant"] :
                                texteMontant = u"%s utilisés sur %s" % (montantVentilation, montantReglement)
                            else :
                                texteMontant = montantReglement
                                
                            texte = u"%s%s%s de %s (%s)" % (dictTemp["mode"], numero, emetteur, dictTemp["payeur"], texteMontant)
                            listeTextesReglements.append(texte)
                        
                        if dictValeur["solde"] > FloatToDecimal(0.0) :
                            intro = u"Période partiellement réglée avec"
                        else :
                            intro = u"Période réglée en intégralité avec"
                            
                        texteReglements = _(u"<b>Règlement : </b> %s %s.") % (intro, " + ".join(listeTextesReglements))
                        listeMessages.append(Paragraph(texteReglements, paraStyle))
                                
                # Messages
                if mode == "facture" :
                    if dictOptions["afficher_messages"] == True :
                        for message in dictOptions["messages"] :
                            listeMessages.append(Paragraph(message, paraStyle))
                        
                        for message_familial in dictValeur["messages_familiaux"] :
                            texte = message_familial["texte"]
                            if len(texte) > 0 and texte[-1] not in ".!?" : 
                                texte = texte + u"."
                            texte = _(u"<b>Message : </b>%s") % texte
                            listeMessages.append(Paragraph(texte, paraStyle))
                            
                if len(listeMessages) > 0 :
                    listeMessages.insert(0, Paragraph(_(u"<u>Informations :</u>"), paraStyle))
                
                # ------------------ CADRE TOTAUX ------------------------
                dataTableau = []
                largeurColonneLabel = 110
                largeursColonnes = [ CADRE_CONTENU[2] - largeurColonneMontantTTC - largeurColonneLabel, largeurColonneLabel, largeurColonneMontantTTC]

                if mode == "devis":
                    dataTableau.append((listeMessages, _(u"Total :"), u"%.02f %s" % (dictValeur["total"], SYMBOLE)))
                else:
                    dataTableau.append((listeMessages, _(u"Total période :"), u"%.02f %s" % (dictValeur["total"], SYMBOLE)))
                    dataTableau.append(("", _(u"Montant déjà réglé :"), u"%.02f %s" % (dictValeur["ventilation"], SYMBOLE)))
                
                    if mode == "facture" and dictOptions["integrer_impayes"] == True and dictValeur["total_reports"] > 0.0 :
                        dataTableau.append(("", _(u"Report impayés :"), u"%.02f %s" % (dictValeur["total_reports"], SYMBOLE) ))
                        dataTableau.append(("", _(u"Reste à régler :"), u"%.02f %s" % (dictValeur["solde"] + dictValeur["total_reports"], SYMBOLE) ))
                        rowHeights=[10, 10, 10, None]
                    else :
                        dataTableau.append(("", _(u"Reste à régler :"), u"%.02f %s" % (dictValeur["solde"], SYMBOLE) ))
                        rowHeights=[18, 18, None]
                    
                style = [
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 

                        # Lignes Période, avoir, impayés
                        ('FONT', (1, 0), (1, -2), "Helvetica", 8),#dictOptions["taille_texte_labels_totaux"]), 
                        ('FONT', (2, 0), (2, -2), "Helvetica-Bold", 8),#dictOptions["taille_texte_montants_totaux"]), 
                        
                        # Ligne Reste à régler
                        ('FONT', (1, -1), (1, -1), "Helvetica-Bold", dictOptions["taille_texte_labels_totaux"]), 
                        ('FONT', (2, -1), (2, -1), "Helvetica-Bold", dictOptions["taille_texte_montants_totaux"]), 
                        
                        ('GRID', (2, 0), (2, -1), 0.25, colors.black),
                        
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('ALIGN', (2, 0), (2, -1), 'CENTRE'), 
                        ('BACKGROUND', (2, -1), (2, -1), couleurFond),
                        
                        ('SPAN', (0, 0), (0, -1)), 
                        ]
                
                if mode == "facture" and len(listeMessages) > 0 :
                    #style.append( ('BACKGROUND', (0, 0), (0, 0), couleurFondActivite) )
                    style.append( ('FONT', (0, 0), (0, -1), "Helvetica", 8)  )
                    style.append( ('VALIGN', (0, 0), (0, -1), 'TOP') )
                    
                tableau = Table(dataTableau, largeursColonnes)#, rowHeights=rowHeights)
                tableau.setStyle(TableStyle(style))
                story.append(tableau)
                
                # ------------------------- PRELEVEMENTS --------------------
                if "afficher_avis_prelevements" in dictOptions and "prelevement" in dictValeur :
                    if dictValeur["prelevement"] != None and dictOptions["afficher_avis_prelevements"] == True :
                        paraStyle = ParagraphStyle(name="intro",
                              fontName="Helvetica",
                              fontSize=8,
                              leading=11,
                              spaceBefore=2,
                              spaceafter=2,
                              alignment=1,
                              backColor=couleurFondActivite,
                            )
                        story.append(Spacer(0,20))
                        story.append(Paragraph(u"<para align='center'><i>%s</i></para>" % dictValeur["prelevement"], paraStyle))
                
                # Texte conclusion
                if dictOptions["texte_conclusion"] != "" :
                    story.append(Spacer(0,20))
                    paraStyle = ParagraphStyle(name="conclusion",
                                          fontName="Helvetica",
                                          fontSize=dictOptions["taille_texte_conclusion"],
                                          leading=14,
                                          spaceBefore=0,
                                          spaceafter=0,
                                          leftIndent=5,
                                          rightIndent=5,
                                          alignment=dictOptions["alignement_texte_conclusion"],
                                          backColor=ConvertCouleurWXpourPDF(dictOptions["couleur_fond_conclusion"]),
                                          borderColor=ConvertCouleurWXpourPDF(dictOptions["couleur_bord_conclusion"]),
                                          borderWidth=0.5,
                                          borderPadding=5,
                                        )
            
                    texte = dictValeur["texte_conclusion"].replace("\\n", "<br/>")
                    if dictOptions["style_texte_conclusion"] == 0 : texte = u"<para>%s</para>" % texte
                    if dictOptions["style_texte_conclusion"] == 1 : texte = u"<para><i>%s</i></para>" % texte
                    if dictOptions["style_texte_conclusion"] == 2 : texte = u"<para><b>%s</b></para>" % texte
                    if dictOptions["style_texte_conclusion"] == 3 : texte = u"<para><i><b>%s</b></i></para>" % texte
                    story.append(Paragraph(texte, paraStyle))
                    
                # Image signature
                if dictOptions["image_signature"] != "" :
                    cheminImage = dictOptions["image_signature"]
                    if os.path.isfile(cheminImage) :
                        img = Image(cheminImage)
                        largeur, hauteur = int(img.drawWidth * 1.0 * dictOptions["taille_image_signature"] / 100.0), int(img.drawHeight * 1.0 * dictOptions["taille_image_signature"] / 100.0)
                        if largeur > CADRE_CONTENU[2] or hauteur > CADRE_CONTENU[3] :
                            raise Exception(_(u"L'image de signature est trop grande. Veuillez diminuer sa taille avec le parametre Taille."))
                        img.drawWidth, img.drawHeight = largeur, hauteur
                        if dictOptions["alignement_image_signature"] == 0 : img.hAlign = "LEFT"
                        if dictOptions["alignement_image_signature"] == 1 : img.hAlign = "CENTER"
                        if dictOptions["alignement_image_signature"] == 2 : img.hAlign = "RIGHT"
                        story.append(Spacer(0,20))
                        story.append(img)
                        


                # Saut de page
                story.append(PageBreak())

        # Finalisation du PDF
##        try :
        doc.build(story)
##        except Exception, err :
##            print "Erreur dans ouverture PDF :", err
##            if "Permission denied" in err :
##                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur d'édition"), wx.OK | wx.ICON_ERROR)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return
        
        # Ouverture du PDF
        if ouverture == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)




if __name__ == u"__main__":
    Impression()
