#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""

import wx
import CTRL_Bouton_image
import wx.grid as gridlib
import wx.lib.wordwrap as wordwrap
import Outils.gridlabelrenderer as glr
import datetime
import math
import FonctionsPerso
import sys
import traceback

import GestionDB
import UTILS_Config
import UTILS_Organisateur
import UTILS_Infos_individus
import wx.lib.agw.pybusyinfo as PBI

LISTE_MOIS = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + LISTE_MOIS[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def FormateMois((annee, mois)):
    return u"%s %d" % (LISTE_MOIS[mois-1].capitalize(), annee)
    
def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0)
    heures, minutes = heureStr.split(":")
    return datetime.time(int(heures), int(minutes))
    
##def FormateValeur(valeur, mode="quantite"):
##    if mode == "quantite" :
##        return str(valeur)
##    if "temps" in mode :
##        if "." not in str(valeur) :
##            valeur = float(valeur)
##        hr, dec = str(valeur).split(".")
##        if len(dec) == 1 : 
##            mn = int(dec) * 0.1
##        else:
##            mn = int(dec) * 0.01
##        mn = mn * 60 #int(dec)*60/100.0
##        mn = math.ceil(mn)
##        return u"%sh%02d" % (hr, mn)

def FormateValeur(valeur, mode="quantite"):
    if mode == "quantite" :
        return str(valeur)
    if "temps" in mode :
        heures = (valeur.days*24) + (valeur.seconds/3600)
        minutes = valeur.seconds%3600/60
        return "%dh%02d" % (heures, minutes)


    
class MyRowLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, row):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        else:
            pass
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)
    
    def MAJ(self, couleur):
        self._bgcolor = couleur
        

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, typeColonne=None, bgcolor=None):
        self.typeColonne = typeColonne
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        if self.typeColonne == "unite" :
            text = wordwrap.wordwrap(text, LARGEUR_COLONNE_UNITE, dc)
        if self.typeColonne == "unite" :
            self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)



class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.moveTo = None
        self.GetGridWindow().SetToolTipString("")
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(200)
        self.SetColLabelSize(45)
        self.DisableDragColSize()
        self.DisableDragRowSize()
        
        # Paramètres par défaut
        self.date_debut = None
        self.date_fin = None
        self.IDactivite = []
        self.detail_groupes = False
        self.affichage_regroupement = "jour"
        self.affichage_donnees = "quantite"
        self.affichage_mode = "reservation"
        self.affichage_etat = ["reservation", "present"]
        self.labelParametres = ""
                

    def MAJ(self, date_debut=None, date_fin=None, IDactivite=None, listeGroupes=[], detail_groupes=False, affichage_donnees="quantite", 
                        affichage_regroupement="jour", affichage_mode="reservation", affichage_etat=["reservation", "present"], labelParametres=u""):     

        # Chargement des informations individuelles
        if self.date_debut != date_debut :
            self.infosIndividus = UTILS_Infos_individus.Informations(date_reference=date_debut, qf=True, inscriptions=True, messages=False, infosMedicales=False, cotisationsManquantes=False, piecesManquantes=False, questionnaires=True, scolarite=True)
            self.dictInfosIndividus = self.infosIndividus.GetDictValeurs(mode="individu", ID=None, formatChamp=False)
            self.dictInfosFamilles = self.infosIndividus.GetDictValeurs(mode="famille", ID=None, formatChamp=False)

        # Mémorisation des paramètres
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.IDactivite = IDactivite
        self.listeGroupes = listeGroupes
        self.detail_groupes = detail_groupes
        self.affichage_donnees = affichage_donnees
        self.affichage_regroupement = affichage_regroupement
        self.affichage_mode = affichage_mode
        self.affichage_etat = affichage_etat
        self.labelParametres = labelParametres
        
        # init grid
        try :
            dlgAttente = PBI.PyBusyInfo(_(u"Veuillez patienter durant la recherche des données..."), parent=None, title=_(u"Calcul en cours"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            self.InitGrid() 
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la recherche des données de la synthèse des consommations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def Importation(self):
        DB = GestionDB.DB()

        if len(self.listeGroupes) == 0 : conditionGroupes = "()"
        elif len(self.listeGroupes) == 1 : conditionGroupes = "(%d)" % self.listeGroupes[0]
        else : conditionGroupes = str(tuple(self.listeGroupes))
        
        if self.affichage_mode == "reservation" :
            if len(self.affichage_etat) == 0 : 
                conditionEtat = "()"
            elif len(self.affichage_etat) == 1 : 
                conditionEtat = "('%s')" % self.affichage_etat[0]
            else : 
                conditionEtat = str(tuple(self.affichage_etat))
        elif self.affichage_mode == "attente" :
            conditionEtat = "('attente')"
        elif self.affichage_mode == "refus" :
            conditionEtat = "('refus')"
        else :
            conditionEtat = "()"
        
        # Unités
        req = """SELECT IDunite, nom, abrege
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        
        # Groupes
        req = """SELECT IDgroupe, nom, abrege
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        
        # Consommations
        req = """SELECT IDconso, consommations.date, consommations.IDindividu, consommations.IDunite, consommations.IDgroupe, consommations.IDactivite,
        heure_debut, heure_fin, etat, quantite, consommations.IDprestation, prestations.temps_facture,
        comptes_payeurs.IDfamille,  
        activites.nom,
        groupes.nom,
        categories_tarifs.nom
        FROM consommations
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = consommations.IDcategorie_tarif
        WHERE consommations.IDactivite=%d AND consommations.IDgroupe IN %s 
        AND consommations.date>='%s' AND consommations.date<='%s'
        AND etat IN %s
        ;""" % (self.IDactivite, conditionGroupes, self.date_debut, self.date_fin, conditionEtat)
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()
        DB.Close() 
        
        # Calcul des données
        dictResultats = {}
        listePrestationsTraitees = []
        for IDconso, date, IDindividu, IDunite, IDgroupe, IDactivite, heure_debut, heure_fin, etat, quantite, IDprestation, tempsFacture, IDfamille, nomActivite, nomGroupe, nomCategorie in listeConsommations :
            date = DateEngEnDateDD(date)
            mois = date.month
            annee = date.year           

            # Recherche du regroupement
            try :
                if self.affichage_regroupement == "jour" : regroupement = date
                if self.affichage_regroupement == "mois" : regroupement = (annee, mois)
                if self.affichage_regroupement == "annee" : regroupement = annee
                if self.affichage_regroupement == "activite" : regroupement = nomActivite
                if self.affichage_regroupement == "groupe" : regroupement = nomGroupe
                if self.affichage_regroupement == "categorie_tarif" : regroupement = nomCategorie
                if self.affichage_regroupement == "ville_residence" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE"]
                if self.affichage_regroupement == "secteur" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_SECTEUR"]
                if self.affichage_regroupement == "genre" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_SEXE"]
                if self.affichage_regroupement == "age" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_AGE_INT"]
                if self.affichage_regroupement == "ville_naissance" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE_NAISS"]
                if self.affichage_regroupement == "nom_ecole" : regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_ECOLE"]
                if self.affichage_regroupement == "nom_classe" : regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_CLASSE"]
                if self.affichage_regroupement == "nom_niveau_scolaire" : regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_NIVEAU"]
                if self.affichage_regroupement == "famille" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM"]
                if self.affichage_regroupement == "individu" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_NOM_COMPLET"]
                if self.affichage_regroupement == "regime" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_REGIME"]
                if self.affichage_regroupement == "caisse" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_CAISSE"]
                if self.affichage_regroupement == "categorie_travail" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_CATEGORIE_TRAVAIL"]
                if self.affichage_regroupement == "categorie_travail_pere" : regroupement = self.dictInfosIndividus[IDindividu]["PERE_CATEGORIE_TRAVAIL"]
                if self.affichage_regroupement == "categorie_travail_mere" : regroupement = self.dictInfosIndividus[IDindividu]["MERE_CATEGORIE_TRAVAIL"]
                
                # QF
                if self.affichage_regroupement == "qf" :
                    regroupement = None
                    qf = self.dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL_INT"]
                    for x in range(0, 10000, 100) :
                        min, max = x, x+99
                        if qf >= min and qf <= max :
                            regroupement = (min, max)
                
                # Questionnaires
                if self.affichage_regroupement.startswith("question_") and "famille" in self.affichage_regroupement : regroupement = self.dictInfosFamilles[IDfamille]["QUESTION_%s" % self.affichage_regroupement[17:]]
                if self.affichage_regroupement.startswith("question_") and "individu" in self.affichage_regroupement : regroupement = self.dictInfosIndividus[IDindividu]["QUESTION_%s" % self.affichage_regroupement[18:]]
                
            except :
                regroupement = None
            
            if regroupement in ("", None) :
                regroupement = _(u"- non renseigné -")

            # Quantité
            if quantite == None :
                quantite = 1
            
            # Formatage des heures
            if heure_debut != None and heure_debut != "" : 
                h, m = heure_debut.split(":")
                heure_debut = datetime.time(int(h), int(m))
            if heure_fin != None and heure_fin != "" : 
                h, m = heure_fin.split(":")
                heure_fin = datetime.time(int(h), int(m))
            
            # Calcul du temps
            temps_presence = datetime.timedelta(hours=0, minutes=0)
            if heure_debut != None and heure_debut != "" and heure_fin != None and heure_fin != "" : 
                valeur = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute) - datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
##                hr, mn, sc = str(valeur).split(":")
##                minDecimal = int(mn)*100/60
##                temps_presence = float("%s.%s" % (hr, minDecimal))
                temps_presence += valeur
            
            # Si c'est en fonction du temps facturé
            temps_facture = datetime.timedelta(hours=0, minutes=0)
            if tempsFacture != None and tempsFacture != "" : 
                if IDprestation not in listePrestationsTraitees :
                    hr, mn = tempsFacture.split(":")
                    temps_facture += datetime.timedelta(hours=int(hr), minutes=int(mn))
                    listePrestationsTraitees.append(IDprestation)

                
            if self.detail_groupes == True :
                groupe = IDgroupe
            else :
                groupe = None
                
            if self.affichage_donnees == "quantite" : valeur = quantite
            if self.affichage_donnees == "temps_presence" : valeur = temps_presence
            if self.affichage_donnees == "temps_facture" : valeur = temps_facture
            
            if self.affichage_donnees == "quantite" :
                defaut = 0
            else :
                defaut = datetime.timedelta(hours=0, minutes=0)
            
            if dictResultats.has_key(groupe) == False :
                dictResultats[groupe] = {}
            if dictResultats[groupe].has_key(IDunite) == False :
                dictResultats[groupe][IDunite] = {}
            if dictResultats[groupe][IDunite].has_key(regroupement) == False :
                dictResultats[groupe][IDunite][regroupement] = defaut
            dictResultats[groupe][IDunite][regroupement] += valeur
                
        return dictResultats, listeUnites, listeGroupes
    
    def ResetGrid(self):
        # Reset grille
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        
    def InitGrid(self):
        self.ResetGrid() 
        
        # Récupération des données
        dictResultats, listeUnites, listeGroupes = self.Importation() 
        
        if self.affichage_donnees == "quantite" :
            defaut = 0
        else :
            defaut = datetime.timedelta(hours=0, minutes=0)

        listeGroupesUtilises = []
        listeUnitesUtilises = []
        listeRegroupement = []
        dictTotaux = { "lignes" : {}, "colonnes" : {} }
        for IDgroupe, dictGroupe in dictResultats.iteritems() :
            if IDgroupe not in listeGroupesUtilises :
                listeGroupesUtilises.append(IDgroupe)
            for IDunite, dictUnite in dictGroupe.iteritems() :
                if IDunite not in listeUnitesUtilises :
                    listeUnitesUtilises.append(IDunite)
                for regroupement, valeur in dictUnite.iteritems() :
                    if regroupement not in listeRegroupement :
                        listeRegroupement.append(regroupement)
                    
                    # Calcul des totaux
                    if dictTotaux["lignes"].has_key((IDgroupe, IDunite)) == False :
                        dictTotaux["lignes"][(IDgroupe, IDunite)] = defaut
                    dictTotaux["lignes"][(IDgroupe, IDunite)] += valeur
                    if dictTotaux["colonnes"].has_key(regroupement) == False :
                        dictTotaux["colonnes"][regroupement] = defaut
                    dictTotaux["colonnes"][regroupement] += valeur
        
        # Création des colonnes
        largeur_colonne = 80
        dictColonnes = {}
        if self.detail_groupes == True :
            self.AppendCols(len(listeGroupes) * len(listeUnites))
            index = 0
            for IDunite, nomUnite, abregeUnite in listeUnites :
                for IDgroupe, nomGroupe, abregeGroupe in listeGroupes :
                    self.SetColSize(index, largeur_colonne)
                    if abregeGroupe == "" or abregeGroupe == None : abregeGroupe = nomGroupe
                    if abregeUnite == "" or abregeUnite == None : abregeUnite = nomUnite
                    self.SetColLabelValue(index, u"%s\n%s" % (abregeGroupe, abregeUnite))
                    dictColonnes[(IDgroupe, IDunite)] = index
                    index += 1
        else :
            self.AppendCols(len(listeUnites))
            index = 0
            for IDunite, nomUnite, abregeUnite in listeUnites :
                if abregeUnite == "" or abregeUnite == None : abregeUnite = nomUnite
                self.SetColSize(index, largeur_colonne)
                self.SetColLabelValue(index, u"%s" % abregeUnite)
                dictColonnes[(None, IDunite)] = index
                index += 1
        
        # Colonne Total
        self.AppendCols(1)
        self.SetColSize(index, largeur_colonne)
        self.SetColLabelValue(index, _(u"TOTAL"))
        dictColonnes["total"] = index

        # Création des lignes
        listeRegroupement.sort()
        self.AppendRows(len(listeRegroupement))
        
        index = 0
        dictLignes = {}
        for regroupement in listeRegroupement :
            if self.affichage_regroupement == "jour" : 
                label = DateComplete(regroupement)
            elif self.affichage_regroupement == "mois" : 
                label = FormateMois(regroupement)
            elif self.affichage_regroupement == "annee" : 
                label = str(regroupement)
            elif self.affichage_regroupement == "qf" and type(regroupement) == tuple : 
                label = u"%d-%d" % regroupement
            else :
                label = unicode(regroupement)
            
            self.SetRowLabelValue(index, label)
            self.SetRowSize(index, 30)
            dictLignes[regroupement] = index
            index += 1
        
        # Ligne Total
        self.AppendRows(1)
        self.SetRowLabelValue(index, _(u"TOTAL"))
        self.SetRowSize(index, 30)
        dictLignes["total"] = index
        
        # Remplissage des valeurs
        for IDgroupe, dictGroupe in dictResultats.iteritems() :
            for IDunite, dictUnite in dictGroupe.iteritems() :
                for regroupement, valeur in dictUnite.iteritems() :
                    label = FormateValeur(valeur, self.affichage_donnees)
                    numLigne = dictLignes[regroupement]
                    numColonne = dictColonnes[(IDgroupe, IDunite)]
                    self.SetCellValue(numLigne, numColonne, label)
                    self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(numLigne, numColonne, True)
        
        # Remplissage des totaux        
        for (IDgroupe, IDunite), valeur in dictTotaux["lignes"].iteritems() :
            label = FormateValeur(valeur, self.affichage_donnees)
            numLigne = dictLignes["total"]
            numColonne = dictColonnes[(IDgroupe, IDunite)]
            self.SetCellValue(numLigne, numColonne, label)
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
        
        total_general = defaut
        for regroupement, valeur in dictTotaux["colonnes"].iteritems() :
            total_general += valeur
            label = FormateValeur(valeur, self.affichage_donnees)
            numLigne = dictLignes[regroupement]
            numColonne = dictColonnes["total"]
            self.SetCellValue(numLigne, numColonne, label)
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
        
        # Total général
        label = FormateValeur(total_general, self.affichage_donnees)
        numLigne = dictLignes["total"]
        numColonne = dictColonnes["total"]
        self.SetCellValue(numLigne, numColonne, label)
        self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetReadOnly(numLigne, numColonne, True)
        
        # Coloration des TOTAUX
        couleurFond = (240, 240, 240)
        for x in range(0, numLigne+1):
            self.SetCellBackgroundColour(x, numColonne, couleurFond)
        for y in range(0, numColonne):
            self.SetCellBackgroundColour(numLigne, y, couleurFond)
                
    def Apercu(self):
        """ Impression tableau de données """
        if self.GetNumberRows() == 0 or self.GetNumberCols() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a rien à imprimer !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return None

        avecCouleurs = True
        
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        def ConvertCouleur(couleur):
            r, g, b = couleur
            return r/255.0, g/255.0, b/255.0
        
        # Récupération des données du tableau
        tableau = self
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()
        
        # Initialisation du tableau
        story = []
        dataTableau = []
        listeCouleurs = []
        
        # Création des colonnes
        largeursColonnes = []
        largeurColonne = 33
        largeurColonneLabel = 90
        for col in range(0, nbreColonnes+1) :
            if col == 0 : largeursColonnes.append(largeurColonneLabel)
            else: largeursColonnes.append(largeurColonne)
        
        listeStyles = [
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                            ('ALIGN', (0, 0), (-1, 0), 'CENTRE'), # Centre les labels de colonne
                            ('ALIGN', (1, 1), (-1,- 1), 'CENTRE'), # Valeurs à gauche
                            ('ALIGN', (0, 1), (0, -1), 'CENTRE'), # Colonne Label Ligne centrée
                            ('FONT',(0, 0),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police de la ligne de total
                            ('FONT',(0, 0),(-1,0), "Helvetica-Bold", 6), # Donne la police de caract. + taille de police de la ligne de total
                            ]
        
        # Création de l'entete
        valeursLigne = ["",]
        for numColonne in range(0, nbreColonnes) :
            labelColonne = tableau.GetColLabelValue(numColonne)
            valeursLigne.append(labelColonne)
        dataTableau.append(valeursLigne)
        
        # Création des lignes
        for numLigne in range(0, nbreLignes) :
            labelLigne = tableau.GetRowLabelValue(numLigne)
            valeursLigne = [labelLigne,]
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                couleurCase = tableau.GetCellBackgroundColour(numLigne, numCol)
                if couleurCase != (255, 255, 255, 255) and avecCouleurs == True :
                    r, g, b = ConvertCouleur(couleurCase)
                    listeStyles.append( ('BACKGROUND', (numCol+1, numLigne+1), (numCol+1, numLigne+1), (r, g, b) ) )
                if numLigne == 0 :
                    valeurCase = valeurCase.replace(" ", "\n")
                valeursLigne.append(valeurCase)
            dataTableau.append(valeursLigne)
    
        # Style du tableau
        style = TableStyle(listeStyles)
        
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes,  hAlign='LEFT')
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
        
        # Calcul du format de la page
        tailleMarge = 20
        if sum(largeursColonnes) > A4[0] - (tailleMarge*2) :
            hauteur, largeur = A4
        else :
            largeur, hauteur = A4

        # Création du titre du document
        dataTableau = []
        largeurContenu = largeur - (tailleMarge*2)
        largeursColonnes = ( (largeurContenu-100, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Synthèse des consommations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        story.insert(0, tableau)
        story.insert(1, Spacer(0, 10))       
        
        # Insertion du label Paramètres
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        story.insert(2, Paragraph(self.labelParametres, styleA))       

        # Enregistrement du PDF
        nomDoc = "Temp/Synthese_conso_%s.pdf" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur, hauteur), leftMargin=tailleMarge, rightMargin=tailleMarge, topMargin=tailleMarge, bottomMargin=tailleMarge)
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(grid=self, titre=_(u"Synthèse des consommations"))
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(grid=self, titre=_(u"Synthèse des consommations"))


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.grille = CTRL(panel)
        self.grille.MAJ(IDactivite=1, date_debut=datetime.date(2012, 9, 5), date_fin=datetime.date(2014, 9, 5), listeGroupes=[1, 2],
                                detail_groupes=False, affichage_donnees="temps_presence", affichage_regroupement="qf") 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.grille, 1, wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.SetSize((750, 400))
        self.Layout()
        
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", name="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
