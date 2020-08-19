#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""

import wx
from Ctrl import CTRL_Bouton_image
import wx.grid as gridlib
import wx.lib.wordwrap as wordwrap
#import Outils.gridlabelrenderer as glr
import wx.lib.mixins.gridlabelrenderer as glr
import datetime
import math
import FonctionsPerso
import sys
import traceback
import six
import GestionDB
from Utils import UTILS_Config
from Utils import UTILS_Organisateur
from Utils import UTILS_Infos_individus
from Utils import UTILS_Texte
from Utils import UTILS_Dates

LISTE_MOIS = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + LISTE_MOIS[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def FormateMois(donnee):
    if donnee in ("", None):
        return ""
    else:
        annee, mois = donnee
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
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
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
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
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
        self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(200)
        self.SetColLabelSize(50)
        self.DisableDragColSize()
        self.DisableDragRowSize()
        
        # Paramètres par défaut
        self.date_debut = None
        self.date_fin = None
        self.IDactivite = []
        self.affichage_lignes = "jour"
        self.affichage_valeurs = "quantite"
        self.affichage_colonnes = "unites"
        self.affichage_mode = "reservation"
        self.affichage_etat = ["reservation", "present"]
        self.labelParametres = ""
                

    def MAJ(self, date_debut=None, date_fin=None, IDactivite=None, listeGroupes=[], affichage_valeurs="quantite",  affichage_lignes="jour",
            affichage_colonnes="unites", affichage_mode="reservation", affichage_etat=["reservation", "present"], labelParametres=u""):

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
        self.affichage_valeurs = affichage_valeurs
        self.affichage_lignes = affichage_lignes
        self.affichage_colonnes = affichage_colonnes
        self.affichage_mode = affichage_mode
        self.affichage_etat = affichage_etat
        self.labelParametres = labelParametres
        
        # init grid
        try :
            dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant la recherche des données..."), None)
            if 'phoenix' not in wx.PlatformInfo:
                wx.Yield()
            self.InitGrid() 
            del dlgAttente
        except Exception as err:
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

        # Evènements
        self.dictEvenements = {}
        req = """SELECT IDevenement, nom, date, IDunite
        FROM evenements
        WHERE IDactivite=%d
        AND date>='%s' AND date<='%s'
        ;""" % (self.IDactivite, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDevenement, nom, date, IDunite in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            self.dictEvenements[IDevenement] = {"nom" : nom, "date" : date, "IDunite": IDunite}

        # Etiquettes
        self.dictEtiquettes = {}
        req = """SELECT IDetiquette, label, IDactivite, parent, ordre, couleur
        FROM etiquettes;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDetiquette, label, IDactivite, parent, ordre, couleur in listeDonnees :     
            couleurTemp = couleur[1:-1].split(",")
            couleur = wx.Colour(int(couleurTemp[0]), int(couleurTemp[1]), int(couleurTemp[2]))
            self.dictEtiquettes[IDetiquette] = {"label" : label, "IDactivite" : IDactivite, "parent" : parent, "ordre" : ordre, "couleur" : couleur}

        # Consommations
        req = """SELECT IDconso, consommations.date, consommations.IDindividu, consommations.IDunite, consommations.IDgroupe, consommations.IDactivite, consommations.etiquettes,
        heure_debut, heure_fin, consommations.etat, quantite, IDevenement, consommations.IDprestation, prestations.temps_facture,
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
        AND consommations.etat IN %s
        ;""" % (self.IDactivite, conditionGroupes, self.date_debut, self.date_fin, conditionEtat)
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()
        DB.Close() 
        
        # Calcul des données
        dictResultats = {}
        listePrestationsTraitees = []
        for IDconso, date, IDindividu, IDunite, IDgroupe, IDactivite, etiquettes, heure_debut, heure_fin, etat, quantite, IDevenement, IDprestation, tempsFacture, IDfamille, nomActivite, nomGroupe, nomCategorie in listeConsommations :
            date = DateEngEnDateDD(date)
            mois = date.month
            annee = date.year           
            
            # Recherche du regroupement
            try :
                if self.affichage_lignes == "jour" : regroupement = date
                if self.affichage_lignes == "mois" : regroupement = (annee, mois)
                if self.affichage_lignes == "annee" : regroupement = annee
                if self.affichage_lignes == "activite" : regroupement = nomActivite
                if self.affichage_lignes == "groupe" : regroupement = nomGroupe
                if self.affichage_lignes == "evenement" : regroupement = IDevenement
                if self.affichage_lignes == "evenement_date": regroupement = IDevenement
                if self.affichage_lignes == "categorie_tarif" : regroupement = nomCategorie
                if self.affichage_lignes == "ville_residence" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE"]
                if self.affichage_lignes == "secteur" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_SECTEUR"]
                if self.affichage_lignes == "genre" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_SEXE"]
                if self.affichage_lignes == "age" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_AGE_INT"]
                if self.affichage_lignes == "ville_naissance" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE_NAISS"]
                if self.affichage_lignes == "nom_ecole" : regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_ECOLE"]
                if self.affichage_lignes == "nom_classe" : regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_CLASSE"]
                if self.affichage_lignes == "nom_niveau_scolaire" : regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_NIVEAU"]
                if self.affichage_lignes == "famille" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM"]
                if self.affichage_lignes == "individu" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_NOM_COMPLET"]
                if self.affichage_lignes == "regime" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_REGIME"]
                if self.affichage_lignes == "caisse" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_CAISSE"]
                if self.affichage_lignes == "categorie_travail" : regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_CATEGORIE_TRAVAIL"]
                if self.affichage_lignes == "categorie_travail_pere" : regroupement = self.dictInfosIndividus[IDindividu]["PERE_CATEGORIE_TRAVAIL"]
                if self.affichage_lignes == "categorie_travail_mere" : regroupement = self.dictInfosIndividus[IDindividu]["MERE_CATEGORIE_TRAVAIL"]
                
                # QF
                if self.affichage_lignes == "qf" :
                    regroupement = None
                    qf = self.dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL_INT"]
                    for x in range(0, 10000, 100) :
                        min, max = x, x+99
                        if qf >= min and qf <= max :
                            regroupement = (min, max)
                
                # Etiquettes
                if self.affichage_lignes == "etiquette" :
                    etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
                    if len(etiquettes) > 0 :
                        temp = []
                        for IDetiquette in etiquettes :
                            if IDetiquette in self.dictEtiquettes :
                                temp.append(self.dictEtiquettes[IDetiquette]["label"])
                        regroupement = temp
                    else :
                        regroupement = _(u"- Aucune étiquette -")
                    
                # Questionnaires
                if self.affichage_lignes.startswith("question_") and "famille" in self.affichage_lignes : regroupement = self.dictInfosFamilles[IDfamille]["QUESTION_%s" % self.affichage_lignes[17:]]
                if self.affichage_lignes.startswith("question_") and "individu" in self.affichage_lignes : regroupement = self.dictInfosIndividus[IDindividu]["QUESTION_%s" % self.affichage_lignes[18:]]
                
            except :
                regroupement = None
            
            if regroupement in ("", None):
                regroupement = _(u"- Non renseigné -")
            
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
                temps_presence += valeur
            
            # Si c'est en fonction du temps facturé
            temps_facture = datetime.timedelta(hours=0, minutes=0)
            if tempsFacture != None and tempsFacture != "" : 
                if IDprestation not in listePrestationsTraitees :
                    hr, mn = tempsFacture.split(":")
                    temps_facture += datetime.timedelta(hours=int(hr), minutes=int(mn))
                    listePrestationsTraitees.append(IDprestation)

            # Colonnes
            if self.affichage_colonnes == "unites_groupes" :
                groupe = IDgroupe
            elif self.affichage_colonnes == "unites_evenements" :
                groupe = IDevenement
            else:
                groupe = None

            # Valeurs
            if self.affichage_valeurs == "quantite" : valeur = quantite
            if self.affichage_valeurs == "temps_presence" : valeur = temps_presence
            if self.affichage_valeurs == "temps_facture" : valeur = temps_facture
            if self.affichage_valeurs == "quantite" :
                defaut = 0
            else :
                defaut = datetime.timedelta(hours=0, minutes=0)

            # En cas de regroupements multiples :
            if type(regroupement) == list :
                listeRegroupements = regroupement
            else :
                listeRegroupements = [regroupement,]
            
            for regroupement in listeRegroupements :
                if (groupe in dictResultats) == False :
                    dictResultats[groupe] = {}
                if (IDunite in dictResultats[groupe]) == False :
                    dictResultats[groupe][IDunite] = {}
                if (regroupement in dictResultats[groupe][IDunite]) == False :
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
        
        if self.affichage_valeurs == "quantite" :
            defaut = 0
        else :
            defaut = datetime.timedelta(hours=0, minutes=0)

        listeGroupesUtilises = []
        listeUnitesUtilises = []
        listeRegroupement = []
        dictTotaux = { "lignes" : {}, "colonnes" : {} }
        for IDgroupe, dictGroupe in dictResultats.items() :
            if IDgroupe not in listeGroupesUtilises :
                listeGroupesUtilises.append(IDgroupe)
            for IDunite, dictUnite in dictGroupe.items() :
                if IDunite not in listeUnitesUtilises :
                    listeUnitesUtilises.append(IDunite)
                for regroupement, valeur in dictUnite.items() :
                    if regroupement not in listeRegroupement :
                        listeRegroupement.append(regroupement)
                    
                    # Calcul des totaux
                    if ((IDgroupe, IDunite) in dictTotaux["lignes"]) == False :
                        dictTotaux["lignes"][(IDgroupe, IDunite)] = defaut
                    dictTotaux["lignes"][(IDgroupe, IDunite)] += valeur
                    if (regroupement in dictTotaux["colonnes"]) == False :
                        dictTotaux["colonnes"][regroupement] = defaut
                    dictTotaux["colonnes"][regroupement] += valeur

        # Création des colonnes
        largeur_colonne = 80
        dictColonnes = {}
        if self.affichage_colonnes == "unites_groupes":
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

        elif self.affichage_colonnes == "unites_evenements":
            index = 0
            for IDunite, nomUnite, abregeUnite in listeUnites:
                liste_events = [(dict_evenement["date"], dict_evenement["nom"], IDevenement) for IDevenement, dict_evenement in self.dictEvenements.items() if dict_evenement["IDunite"] == IDunite]
                if liste_events:
                    liste_events.sort()
                    self.AppendCols(len(liste_events))
                    for date, nomEvent, IDevenement in liste_events:
                        if len(nomEvent) > 15:
                            nomEvent = nomEvent[:15] + "."
                        self.SetColSize(index, largeur_colonne + 25)
                        self.SetColLabelValue(index, u"%s\n%s\n%s" % (nomEvent, UTILS_Dates.DateEngFr(date), abregeUnite))
                        dictColonnes[(IDevenement, IDunite)] = index
                        index += 1
                else:
                    self.AppendCols(1)
                    self.SetColLabelValue(index, u"%s" % abregeUnite)
                    dictColonnes[(None, IDunite)] = index
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
            if self.affichage_lignes == "jour" :
                label = DateComplete(regroupement)
            elif self.affichage_lignes == "mois" :
                label = FormateMois(regroupement)
            elif self.affichage_lignes == "annee" :
                label = str(regroupement)
            elif self.affichage_lignes == "evenement" and regroupement in self.dictEvenements :
                label = self.dictEvenements[regroupement]["nom"]
            elif self.affichage_lignes == "evenement_date" and regroupement in self.dictEvenements :
                label = u"%s (%s)" % (self.dictEvenements[regroupement]["nom"], UTILS_Dates.DateDDEnFr(self.dictEvenements[regroupement]["date"]))
            elif self.affichage_lignes == "qf" and type(regroupement) == tuple :
                label = u"%d-%d" % regroupement
            else :
                label = six.text_type(regroupement)
            
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
        for IDgroupe, dictGroupe in dictResultats.items() :
            for IDunite, dictUnite in dictGroupe.items() :
                for regroupement, valeur in dictUnite.items():
                    label = FormateValeur(valeur, self.affichage_valeurs)
                    numLigne = dictLignes[regroupement]
                    numColonne = dictColonnes[(IDgroupe, IDunite)]
                    self.SetCellValue(numLigne, numColonne, label)
                    self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(numLigne, numColonne, True)
        
        # Remplissage des totaux        
        for (IDgroupe, IDunite), valeur in dictTotaux["lignes"].items() :
            label = FormateValeur(valeur, self.affichage_valeurs)
            numLigne = dictLignes["total"]
            numColonne = dictColonnes[(IDgroupe, IDunite)]
            self.SetCellValue(numLigne, numColonne, label)
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
        
        total_general = defaut
        for regroupement, valeur in dictTotaux["colonnes"].items() :
            total_general += valeur
            label = FormateValeur(valeur, self.affichage_valeurs)
            numLigne = dictLignes[regroupement]
            numColonne = dictColonnes["total"]
            self.SetCellValue(numLigne, numColonne, label)
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
        
        # Total général
        label = FormateValeur(total_general, self.affichage_valeurs)
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
        nomDoc = FonctionsPerso.GenerationNomDoc("SYNTHESE_CONSO", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur, hauteur), leftMargin=tailleMarge, rightMargin=tailleMarge, topMargin=tailleMarge, bottomMargin=tailleMarge)
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def ExportTexte(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(grid=self, titre=_(u"Synthèse des consommations"))
        
    def ExportExcel(self, event=None):
        from Utils import UTILS_Export
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
        self.grille.MAJ(IDactivite=1, date_debut=datetime.date(2015, 11, 1), date_fin=datetime.date(2015, 12, 20), listeGroupes=[1,2],
                        affichage_valeurs="temps_presence", affichage_colonnes="unites", affichage_lignes="individu")
        self.bouton_test = wx.Button(panel, -1, u"Test export Excel")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.grille, 1, wx.EXPAND, 0)
        sizer_2.Add(self.bouton_test, 0, wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.SetSize((750, 400))
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)

    def OnBoutonTest(self, event):
        self.grille.ExportExcel()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", name="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
