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
import sys
import FonctionsPerso
import datetime

from Utils import UTILS_Organisateur
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


def Impression(dictDonnees={}, nomDoc=FonctionsPerso.GenerationNomDoc("RESERVATIONS", "pdf"), afficherDoc=True):
    # Création du PDF
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
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
    
    # Initialisation du document
    if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
    doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30, pagesize=TAILLE_PAGE, showBoundary=False)
    story = []
    dictChampsFusion = {}
    
    largeurContenu = 520
    couleurFond = (0.8, 0.8, 1)
    couleurFondActivite = (0.92, 0.92, 1)
            
    # Création du titre du document
    def Header():
        dataTableau = []
        largeursColonnes = ( (420, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Réservations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
        style = TableStyle([
                ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                ('ALIGN', (0,0), (0,0), 'LEFT'), 
                ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                ('FONT',(1,0),(1,0), "Helvetica", 6), 
                ])
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))       
    
    # Insère un header
    Header()

    # Texte si aucune réservation
    if len(dictDonnees) == 0 :
        paraStyle = ParagraphStyle(name="defaut", fontName="Helvetica", fontSize=11)
        story.append(Paragraph("&nbsp;", paraStyle))
        story.append(Paragraph("&nbsp;", paraStyle))
        story.append(Paragraph(_(u"<para align='centre'><b>Aucune réservation</b></para>"), paraStyle))
    
    # Tableau NOM INDIVIDU
    totalFacturationFamille = 0.0
    for IDindividu, dictIndividu in dictDonnees.items() :
        nom = dictIndividu["nom"]
        prenom = dictIndividu["prenom"]
        date_naiss = dictIndividu["date_naiss"]
        sexe = dictIndividu["sexe"]
        if date_naiss != None :
            if sexe == "M" : 
                texteNaiss = _(u", né le %s") % DateEngFr(str(date_naiss))
            else : 
                texteNaiss = _(u", née le %s") % DateEngFr(str(date_naiss))
        else:
            texteNaiss = u""
        texteIndividu = u"%s %s%s" % (nom, prenom, texteNaiss)
        
        totalFacturationIndividu = 0.0
        
        # Insertion du nom de l'individu
        paraStyle = ParagraphStyle(name="individu",
                              fontName="Helvetica",
                              fontSize=9,
                              #leading=7,
                              spaceBefore=0,
                              spaceafter=0,
                            )
        texteIndividu = Paragraph(texteIndividu, paraStyle)
        dataTableau = []
        dataTableau.append([texteIndividu,])
        tableau = Table(dataTableau, [largeurContenu,])
        listeStyles = [
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONT', (0, 0), (-1, -1), "Helvetica", 8), 
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), couleurFond),
                ]
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
    
        # Tableau NOM ACTIVITE
        listePrestationsUtilisees = []
        for IDactivite, dictActivite in dictIndividu["activites"].items() :
            texteActivite = dictActivite["nom"]
            if dictActivite["agrement"] != None :
                texteActivite += dictActivite["agrement"]
            
            if texteActivite != None :
                dataTableau = []
                dataTableau.append([texteActivite,])
                tableau = Table(dataTableau, [largeurContenu,])
                listeStyles = [
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONT', (0, 0), (-1, -1), "Helvetica", 6),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('BACKGROUND', (0, 0), (-1, 0), couleurFondActivite),
                    ]
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)
            
            # Colonnes : Date, Consos, Etat, Prestations, Montant
            dataTableau = []
            largeursColonnes = [55, 165, 80, 160, 60]
            dataTableau.append([_(u"Date"), _(u"Consommations"), _(u"Etat"), _(u"Prestations"), _(u"Total")])
            
            paraStyle = ParagraphStyle(name="standard",
                      fontName="Helvetica",
                      fontSize=8,
                      leading=10,
                      #spaceBefore=8,
                      spaceAfter=0,
                    )
                            
            # lignes DATES
            listeDates = []
            for date, dictDates in dictActivite["dates"].items() :
                listeDates.append(date)
            listeDates.sort() 
            
            for date in listeDates :
                dictDate = dictActivite["dates"][date]
                listeLigne = []
                
                # Insertion de la date
                texteDate = Paragraph(DateEngFr(str(date)), paraStyle)
                
                # Insertion des consommations
                listeEtats = []
                listeConso = []
                listePrestations = []
                for IDunite, liste_unites in dictDate["unites"].items():
                    for dictUnite in liste_unites:
                        etat = dictUnite["etat"]
                        nomUnite = dictUnite["nomUnite"]
                        if dictUnite["evenement"]:
                            nomUnite = dictUnite["evenement"].nom

                        if etat != None :
                            labelUnite = nomUnite
                            if dictUnite["type"] == "Horaire" or (dictUnite["type"] == "Evenement" and dictUnite["heure_debut"] and dictUnite["heure_fin"]and dictUnite["heure_debut"] != "00:00" and dictUnite["heure_fin"] != "00:00"):
                                heure_debut = dictUnite["heure_debut"]
                                if heure_debut == None : heure_debut = u"?"
                                heure_debut = heure_debut.replace(":", "h")
                                heure_fin = dictUnite["heure_fin"]
                                if heure_fin == None : heure_fin = u"?"
                                heure_fin = heure_fin.replace(":", "h")
                                labelUnite += _(u" (%s-%s)") % (heure_debut, heure_fin)
                            listeConso.append(labelUnite)

                            if etat not in listeEtats :
                                listeEtats.append(etat)

                            IDprestation = dictUnite["IDprestation"]
                            if dictUnite["prestation"] != None and IDprestation not in listePrestationsUtilisees :
                                listePrestations.append(dictUnite["prestation"])
                                listePrestationsUtilisees.append(IDprestation)
                    
                texteConsos = Paragraph("<br/>".join(listeConso), paraStyle)
                
                # Insertion de l'état
                texteEtat = Paragraph("<br/>".join(listeEtats), paraStyle)
                
                # Insertion des prestations et montants
                textePrestations = []
                texteMontants = []
                for dictPrestation in listePrestations :
                    montant = dictPrestation["montant"]
                    label = dictPrestation["label"]
                    paye = dictPrestation["paye"]
                    textePrestations.append(Paragraph(label, paraStyle))
                    texteMontants.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (montant, SYMBOLE), paraStyle))
                    
                    # Pour le total par individu :
                    if montant != None :
                        totalFacturationIndividu += montant
                        totalFacturationFamille += montant
                
                if len(listeConso) > 0 :
                    dataTableau.append([texteDate, texteConsos, texteEtat, textePrestations, texteMontants])
            
            if len(dataTableau) == 1 :
                dlg = wx.MessageDialog(None, _(u"Il n'y a aucune consommation à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
                
            tableau = Table(dataTableau, largeursColonnes)
            listeStyles = [
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1,-1), 0.25, colors.black), 
                
                ('FONT', (0, 0), (-1, 0), "Helvetica", 6), 
                ('ALIGN', (0, 0), (-1, 0), 'CENTRE'),
                
                ('FONT', (0, 1), (-1, 1), "Helvetica", 8), 
                ]
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)

        # Insertion du total par individu
        dataTableau = []
        montantIndividu = Paragraph(u"<para align='right'>%.02f %s</para>" % (totalFacturationIndividu, SYMBOLE), paraStyle)
        dataTableau.append([Paragraph(_(u"<para align='right'>Total :</para>"), paraStyle), montantIndividu])
        
        listeStyles = [
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONT', (0, 0), (-1, -1), "Helvetica", 8), 
                ('GRID', (-1, -1), (-1,-1), 0.25, colors.black), 
                ('ALIGN', (-1, -1), (-1, -1), 'CENTRE'),
                ('BACKGROUND', (-1, -1), (-1, -1), couleurFond), 
                ]
            
        # Création du tableau
        largeursColonnesTotal = [460, 60]
        tableau = Table(dataTableau, largeursColonnesTotal)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
        story.append(Spacer(0, 12))

    # Total facturation Famille
    nbreIndividus = len(dictDonnees)
    if nbreIndividus > 1 :
        dataTableau = []
        montantFamille = Paragraph(u"<para align='right'>%.02f %s</para>" % (totalFacturationFamille, SYMBOLE), paraStyle)
        dataTableau.append([Paragraph(_(u"<para align='right'>TOTAL :</para>"), paraStyle), montantFamille])
        largeursColonnesTotal = [460, 60]
        tableau = Table(dataTableau, largeursColonnesTotal)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
    
    # Champs pour fusion Email
    dictChampsFusion["{SOLDE}"] = u"%.02f %s" % (totalFacturationFamille, SYMBOLE)
    
    # Enregistrement et ouverture du PDF
    try :
        doc.build(story)
    except Exception as err :
        print("Erreur dans ouverture PDF :", err)
        if "Permission denied" in err :
            dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur d'édition"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    if afficherDoc == True :
        FonctionsPerso.LanceFichierExterne(nomDoc)

    return dictChampsFusion
