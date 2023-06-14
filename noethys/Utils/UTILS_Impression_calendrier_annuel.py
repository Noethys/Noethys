#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import calendar
import FonctionsPerso
import GestionDB
import sys

from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable



DICT_CATEGORIES = {}
LISTE_VACANCES = {}
LISTE_FERIES = {}

COULEUR_WE = (230, 230, 230)  
COULEUR_VACANCES = (255, 255, 220)
COULEUR_FERIES = (180, 180, 180)

AFFICHER_WE = True
AFFICHER_VACANCES = True
AFFICHER_FERIES = True
AFFICHER_HEURES = True
AFFICHER_COULEUR_CATEGORIES = True
AFFICHER_LEGENDE = True
AFFICHER_HEURES_MOIS = True


def StrEnDatetimeDate(texteDate):
    annee = texteDate[:4]
    mois = texteDate[5:7]
    jour = texteDate[8:10]
    date = datetime.date(int(annee), int(mois), int(jour))
    return date

def HeureStrEnDatetime(texteHeure):
    texteHeure = texteHeure[:5]
    posTemp = texteHeure.index(":")
    heuresTemp = int(texteHeure[:posTemp])
    minutesTemp =  int(texteHeure[posTemp+1:])
    heure = datetime.time(heuresTemp, minutesTemp)
    return heure

def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr

def FormateCouleur(texte):
    pos1 = texte.index(",")
    pos2 = texte.index(",", pos1+1)
    r = int(texte[1:pos1])
    v = int(texte[pos1+2:pos2])
    b = int(texte[pos2+2:-1])
    return (r, v, b)
    
def ConvertCouleur(couleur):
    r, g, b = couleur
    return r/255.0, g/255.0, b/255.0

def minutesEnHeures(dureeMinutes) :
    if dureeMinutes != 0 :
        nbreHeures = dureeMinutes/60
        nbreMinutes = dureeMinutes-(nbreHeures*60)
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        duree = str(nbreHeures) + "h" + str(nbreMinutes)
    else:
        duree = ""
    return duree


class Impression():
    def __init__(self, titre="", annee=2009,
                        afficher_we=True, afficher_vacances=True, afficher_feries=True,
                        afficher_heures=True, afficher_couleurs_categories=True,
                        afficher_legende=True, afficher_heures_mois=True):
        
        self.titre = titre
        self.annee = annee
        
        global AFFICHER_WE, AFFICHER_VACANCES, AFFICHER_FERIES, AFFICHER_HEURES, AFFICHER_COULEUR_CATEGORIES, AFFICHER_LEGENDE, AFFICHER_HEURES_MOIS
        AFFICHER_WE = afficher_we
        AFFICHER_VACANCES = afficher_vacances
        AFFICHER_FERIES = afficher_feries
        AFFICHER_HEURES = afficher_heures
        AFFICHER_COULEUR_CATEGORIES = afficher_couleurs_categories
        AFFICHER_LEGENDE = afficher_legende
        AFFICHER_HEURES_MOIS = afficher_heures_mois

        largeurMois = 55
        espaceMois = 5
        
        # Paramètres du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("CALENDRIER_ANNUEL", "pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")        
        taillePage = landscape(A4)
        HAUTEUR_PAGE = defaultPageSize[0]
        LARGEUR_PAGE = defaultPageSize[1]
        
        doc = SimpleDocTemplate(nomDoc, pagesize=taillePage, topMargin=50, bottomMargin=50)
        story = []
        
        # Création du titre du document
        largeursColonnesTitre = ( (615, 100) )
        dateDuJour = DatetimeDateEnStr(datetime.date.today())
        dataTableauTitre = [(_(u"Planning %d de %s") % (self.annee, self.titre), _(u"Edité le %s") % dateDuJour ),]
        styleTitre = TableStyle([
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                            ('ALIGN', (0,0), (0,0), 'LEFT'), 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                            ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                            ('FONT',(1,0),(1,0), "Helvetica", 6), 
                            ])
        tableauTitre = Table(dataTableauTitre, largeursColonnesTitre)
        tableauTitre.setStyle(styleTitre)
        story.append(tableauTitre)
        story.append(Spacer(0,20))  
        
        # Récupération des données
        self.dictPresences, self.dictTotauxCategories = {}, {}#self.ImportPresences(self.IDpersonne, self.annee)
        
        global DICT_CATEGORIES, LISTE_VACANCES, LISTE_FERIES
        DICT_CATEGORIES = self.ImportCategories()
        LISTE_VACANCES = self.Importation_Vacances()
        LISTE_FERIES = self.Importation_Feries()
        
        # Création du tableau
        dataTableau = []
        enteteTableau = []
        largeursColonnes = []
        styleTableau = []
        
        listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
        listeJours = (u"L", u"M", u"M", u"J", u"V", u"S", u"D")
        
        # Création de l'entete du tableau
        index = 1
        for nomMois in listeMois :
            largeursColonnes.append(largeurMois)
            if index != 12 : largeursColonnes.append(espaceMois)
            enteteTableau.append(nomMois)
            if index != 12 : enteteTableau.append("")
            index += 1
        dataTableau.append(enteteTableau)
        styleTableau.append(('ALIGN', (0, 0), (-1, 0), 'CENTRE')) 
        styleTableau.append(('FONT', (0, 0), (-1, 0), "Helvetica-Bold", 8))
        
        # Création des lignes vides
        for x in range(1, 33) :
            ligne = []
            for case in range (0, 23):
                ligne.append(None)
            dataTableau.append(ligne)
        
        # Style général du tableau
        styleTableau.append(('FONT', (0, 1), (-1, -1), "Helvetica", 7))
        styleTableau.append(('LEFTPADDING', (0, 1), (-1, -1), 0))
        styleTableau.append(('RIGHTPADDING', (0, 1), (-1, -1), 0))
        styleTableau.append(('TOPPADDING', (0, 1), (-1, -1), 0))
        styleTableau.append(('BOTTOMPADDING', (0, 1), (-1, -1), 0))
        
        # Remplissage du tableau
        numMois = 1
        for nomMois in listeMois :
            # Création d'un mois
            totalMinutesMois = 0
            numWeekDay, nbreJoursMois = calendar.monthrange(self.annee, numMois)
            numCol = (numMois*2)-2
            
            for numJour in range(1, nbreJoursMois+1) :
                # Création des labels des dates
                dateDD = datetime.date(year=self.annee, month=numMois, day=numJour)
                nomJour = listeJours[dateDD.weekday()]
                labelDate = u"%s %d" % (nomJour, numJour)
                
                # Création du contenu de chaque case
                if dateDD in self.dictPresences :
                    dictBarres = self.dictPresences[dateDD]
                else:
                    dictBarres = {}
                case = CaseDate(xoffset=0, hauteurCase=10, largeurCase=largeurMois, dateDD=dateDD, labelDate=labelDate, dictBarres=dictBarres )
                dataTableau[numJour][numCol] = case
                
                # Calcule le nbre d'heures du mois
                if dateDD in self.dictPresences :
                    totalMinutesMois += self.dictPresences[dateDD]["totalJour"]
            
            # Ecrit le nombre d'heures du mois
            if AFFICHER_HEURES_MOIS == True and totalMinutesMois != 0 :
                numJour += 1
                dataTableau[numJour][numCol] = minutesEnHeures(totalMinutesMois)
                styleTableau.append(('FONT', (numCol, numJour), (numCol, numJour), "Helvetica", 5))
                styleTableau.append(('ALIGN', (numCol, numJour), (numCol, numJour), "RIGHT"))
                styleTableau.append(('VALIGN', (numCol, numJour), (numCol, numJour), "TOP"))
                
            # Définit le style du tableau
            styleTableau.append(('GRID', (numCol, 0), (numCol, nbreJoursMois), 0.25, colors.black))
        
            numMois += 1
        
        
        
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(TableStyle(styleTableau))
        story.append(tableau)
        story.append(Spacer(0, 25))

        # Légendes des catégories
        dataTableauLegende = []
        largeursColonnesLegende = []
        styleTableauLegende = []
        
        # Création des lignes vides du tableau des légendes
        nbreLignesLegendes = 5
        nbreColonnesLegendes = 4
        largeurColonneLegende = 178.75
        
        for numLigne in range(0, nbreLignesLegendes) :
            ligne = []
            for numCol in range (0, nbreColonnesLegendes):
                ligne.append(None)
            dataTableauLegende.append(ligne)
        
        # Création de la liste des largeurs des colonnes
        for x in range(0, nbreColonnesLegendes):
            largeursColonnesLegende.append(largeurColonneLegende)
            
        # Remplissage du tableau des légendes
        nbre_legendes = 0
        total_heures = 0
        numLigne = 0
        numCol = 0
        
        if AFFICHER_VACANCES == True :
            dataTableauLegende[numLigne][numCol] = CaseLegende(0, 10, _(u"Vacances"), COULEUR_VACANCES, None)
            numLigne += 1
        if AFFICHER_WE == True :
            dataTableauLegende[numLigne][numCol] = CaseLegende(0, 10, _(u"Week-ends"), COULEUR_WE, None)
            numLigne += 1
        if AFFICHER_FERIES == True :
            dataTableauLegende[numLigne][numCol] = CaseLegende(0, 10, _(u"Jours fériés"), COULEUR_FERIES, None)
            numLigne += 1
        
        for IDcategorie, nbreHeures in self.dictTotauxCategories.items() :
            if IDcategorie != "totalAnnee" :
                nom_categorie, ordre, couleur = DICT_CATEGORIES[IDcategorie]
                legende = CaseLegende(0, 10, nom_categorie, couleur, nbreHeures)
                dataTableauLegende[numLigne][numCol] = legende
                nbre_legendes += 1
                total_heures += nbreHeures
                
                numLigne += 1
                if numLigne == nbreLignesLegendes :
                    numLigne = 0
                    numCol += 1

        if nbre_legendes > 1 :
            # Ajoute un total d'heures pour l'année
            legende = CaseLegende(0, 10, _(u"Total pour l'année"), None, total_heures)
            dataTableauLegende[numLigne][numCol] = legende
        
        styleTableauLegende.append(('FONT', (0, 1), (-1, -1), "Helvetica", 6))
        styleTableauLegende.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        styleTableauLegende.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))
        styleTableauLegende.append(('TOPPADDING', (0, 0), (-1, -1), 0))
        styleTableauLegende.append(('BOTTOMPADDING', (0, 0), (-1, -1), 0))
        
        tableauLegende = Table(dataTableauLegende, largeursColonnesLegende)
        tableauLegende.setStyle(TableStyle(styleTableauLegende))
        if AFFICHER_LEGENDE == True :
            story.append(tableauLegende)
        
        # Enregistrement du PDF
        doc.build(story)
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
        
    def ImportPresences(self, IDpersonne, annee):
        date_debut = "%d-01-01" % annee
        date_fin = "%d-12-31" % annee
        DB = GestionDB.DB()
        req = """
        SELECT IDpresence, date, heure_debut, heure_fin, IDcategorie 
        FROM presences 
        WHERE IDpersonne=%d AND date>='%s' AND date<='%s'
        ORDER BY date;""" % (IDpersonne, date_debut, date_fin)
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        DB.Close()
        # Création des dict de données
        dictPresences = {}
        dictTotalHeures = {}
        for IDpresence, date, heure_debut, heure_fin, IDcategorie in listePresences :
            # Création du dict des présences
            dateDD = StrEnDatetimeDate(date)
            heure_debut = HeureStrEnDatetime(heure_debut)
            heure_fin = HeureStrEnDatetime(heure_fin)
            HMin = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
            HMax = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
            duree = ((HMax - HMin).seconds)/60
            if dateDD in dictPresences:
                if IDcategorie in dictPresences[dateDD]:
                    dictPresences[dateDD][IDcategorie] = dictPresences[dateDD][IDcategorie] + duree
                    dictPresences[dateDD]["totalJour"] = dictPresences[dateDD]["totalJour"] + duree
                else:
                    dictPresences[dateDD][IDcategorie] = duree
                    dictPresences[dateDD]["totalJour"] = dictPresences[dateDD]["totalJour"] + duree
            else:
                dictPresences[dateDD] = { IDcategorie : duree, "totalJour" : duree }
            # Création du dict des totaux par categories
            if IDcategorie in dictTotalHeures:
                dictTotalHeures[IDcategorie] = dictTotalHeures[IDcategorie] + duree
            else:
                dictTotalHeures[IDcategorie] = duree
            if "totalAnnee" in dictTotalHeures:
                dictTotalHeures["totalAnnee"] = dictTotalHeures["totalAnnee"] + duree
            else:
                dictTotalHeures["totalAnnee"] = duree
            
        return dictPresences, dictTotalHeures
    
    def ImportCategories(self):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie, nom_categorie, ordre, couleur FROM cat_presences"
        DB.ExecuterReq(req)
        listecategories = DB.ResultatReq()
        DB.Close()
        dictCategories = {}
        for IDcategorie, nom_categorie, ordre, couleur in listecategories :
            dictCategories[IDcategorie] = (nom_categorie, ordre, couleur) 
        return dictCategories

    def Importation_Vacances(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM periodes_vacances ORDER BY date_debut;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeVacances1 = DB.ResultatReq()
        DB.Close()
        listeVacances2 = []
        for id, nom, annee, date_debut, date_fin in listeVacances1 :
            datedebut = datetime.date(int(date_debut[:4]), int(date_debut[5:7]), int(date_debut[8:10]))
            datefin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            listeVacances2.append(datedebut)
            for x in range((datefin-datedebut).days) :
                datedebut = datedebut + datetime.timedelta(days=1) 
                listeVacances2.append(datedebut)
        return listeVacances2
    
    def Importation_Feries(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM jours_feries WHERE (annee=0 OR annee=%d);" % self.annee
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        listeFeries = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = datetime.date(self.annee, mois, jour)
            else:
                date = datetime.date(annee, mois, jour)
            listeFeries.append(date)
        return listeFeries

class CaseDate(Flowable) :
    """ Flowable Case d'une date """
    def __init__(self, xoffset=0, hauteurCase=None, largeurCase=0, dateDD=None, labelDate="", dictBarres={} ):
        self.xoffset = xoffset
        self.size = hauteurCase
        self.hauteurCase = hauteurCase
        self.largeurCase = largeurCase
        self.dateDD = dateDD
        self.labelDate = labelDate
        self.dictBarres = dictBarres
        
    def wrap(self, *args):
        return (self.xoffset, self.size)
    
    def draw(self):
        canvas = self.canv
        couleurDate = None
        positionSeparation = 20
        
        # Couleur de la case Date de la journée
        if AFFICHER_VACANCES == True and self.dateDD in LISTE_VACANCES : couleurDate = COULEUR_VACANCES
        if AFFICHER_WE == True and (self.dateDD.weekday() == 5 or self.dateDD.weekday() == 6) : couleurDate = COULEUR_WE
        if AFFICHER_FERIES == True and self.dateDD in LISTE_FERIES : couleurDate = COULEUR_FERIES
        
        if couleurDate != None :
            r, g, b = ConvertCouleur(couleurDate)
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(0, 0, positionSeparation, self.hauteurCase, fill=1, stroke=False)
        
        # Texte date
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(positionSeparation-2, 2, self.labelDate)
        
        # Trait séparation Date et Heures
        canvas.setLineWidth(0.25)
        canvas.line(positionSeparation, 0, positionSeparation, self.hauteurCase)
        
        # Si aucune présence ce jour -là
        if len(self.dictBarres) == 0 : return

        # Récup du nbre total d'heure de la journée
        totalJour = self.dictBarres["totalJour"]
        
        # Transformation du nombre d'heures par catégorie en pourcentage
        listeCategories = []
        for IDcategorie, nbreHeures in self.dictBarres.items():
            if IDcategorie != "totalJour" :
                largeurBarre = nbreHeures * 1.0 * (self.largeurCase-positionSeparation-0.25) / totalJour
                listeCategories.append( (largeurBarre, IDcategorie) )
        listeCategories.sort()
        
        # Création des graphes
        if AFFICHER_COULEUR_CATEGORIES == True :
            positionTemp = positionSeparation+0.25
            for largeurBarre, IDcategorie in listeCategories :
                r, g, b = ConvertCouleur(FormateCouleur(DICT_CATEGORIES[IDcategorie][2]))
                canvas.setFillColorRGB(r, g, b)
                canvas.rect(positionTemp, 0, largeurBarre, self.hauteurCase, fill=1, stroke=False)
                positionTemp += largeurBarre
        
        # Label Total Heure de la journée
        if AFFICHER_HEURES == True :
            canvas.setFillColorRGB(0, 0, 0)
            canvas.setFont("Helvetica", 7)
            canvas.drawRightString(self.largeurCase-2, 2, "%s" % minutesEnHeures(totalJour))


class CaseLegende(Flowable) :
    """ Flowable Ligne de légende """
    def __init__(self, xoffset=0, hauteurCase=None, label="", couleur=None, totalHeures=0):
        self.xoffset = xoffset
        self.size = hauteurCase
        self.hauteurCase = hauteurCase
        self.label = label
        self.couleur = couleur
        self.totalHeures = totalHeures
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        canvas = self.canv
        # Texte label
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 8)
        if self.totalHeures == None :
            canvas.drawString(15, 2, self.label)
        else:
            canvas.drawString(15, 2, "%s : %s" % (self.label, minutesEnHeures(self.totalHeures)))
        # Carré de couleur
        if self.couleur != None :
            if type(self.couleur) == tuple :
                r, g, b = ConvertCouleur(self.couleur)
            else:
                r, g, b = ConvertCouleur(FormateCouleur(self.couleur))
            canvas.setLineWidth(0.25)
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(0, 0, 10, 10, fill=1)

        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    Impression(titre="test", annee=2016,
                    afficher_we=True,
                    afficher_vacances=True,
                    afficher_feries=True,
                    afficher_heures=True,
                    afficher_couleurs_categories=True,
                    afficher_legende=True,
                    afficher_heures_mois=True
                    )

