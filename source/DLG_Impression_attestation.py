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
import wx
import CTRL_Bouton_image
import datetime
import  wx.grid as gridlib

import CTRL_Bandeau
import CTRL_Saisie_date

import GestionDB
import DATA_Civilites as Civilites
import UTILS_Historique
import UTILS_Identification
import UTILS_Titulaires
import CTRL_Choix_modele
import UTILS_Config
import UTILS_Questionnaires
import CTRL_Attestations_options
from UTILS_Decimal import FloatToDecimal as FloatToDecimal

SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
DICT_CIVILITES = Civilites.GetDictCivilites()

import UTILS_Infos_individus


LISTE_DONNEES = [
    { "nom" : _(u"Attestation"), "champs" : [ 
        { "code" : "numero", "label" : _(u"Numéro")}, 
        { "code" : "date", "label" : _(u"Date d'édition")}, 
        { "code" : "lieu", "label" : _(u"Lieu d'édition")},
        ] },
    { "nom" : _(u"Destinataire"), "champs" : [ 
        { "code" : "nom", "label" : _(u"Nom")}, 
        { "code" : "rue", "label" : _(u"Rue")}, 
        { "code" : "ville", "label" : _(u"CP + Ville")},
        ] },
    { "nom" : _(u"Organisme"), "champs" : [ 
        { "code" : "siret", "label" : _(u"Numéro SIRET")}, 
        { "code" : "ape", "label" : _(u"Code APE")}, 
        ] },
    ]

TEXTE_INTRO = _(u"Je soussigné{GENRE} {NOM}, {FONCTION}, atteste avoir accueilli {ENFANTS} sur la période du {DATE_DEBUT} au {DATE_FIN} selon le détail suivant :")

DICT_DONNEES = {}


def DateComplete(dateDD):
    u""" Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 u"""
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "-" + str(textDate[3:5]) + "-" + str(textDate[:2])
    return text

def RechercheAgrement(listeAgrements, IDactivite, date):
    for IDactiviteTmp, agrement, date_debut, date_fin in listeAgrements :
        if IDactivite == IDactiviteTmp and date >= date_debut and date <= date_fin :
            return agrement
    return None

# -------------------------------------------------------------------------------------------------------------------------

class CTRL_Individus(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.date_debut = None
        self.date_fin = None
        self.listeIndividus = []
        self.dictIndividus = {}
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetPeriode(self, date_debut=None, date_fin=None):
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeIndividus, self.dictIndividus = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeIndividus = []
        dictIndividus = {}
        if self.date_debut == None or self.date_fin == None :
            return listeIndividus, dictIndividus 
        # Récupération des individus
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, individus.nom, individus.prenom
        FROM individus
        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
        LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu
        WHERE inscriptions.IDfamille=%d
        AND consommations.date>='%s' AND consommations.date<='%s'
        GROUP BY individus.IDindividu
        ;""" % (self.parent.IDfamille, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDindividu, nom, prenom in listeDonnees :
            dictTemp = { "IDindividu" : IDindividu, "nom" : nom, "prenom" : prenom }
            dictIndividus[IDindividu] = dictTemp
            listeIndividus.append((prenom, IDindividu))
        listeIndividus.sort()
        return listeIndividus, dictIndividus

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDindividu in self.listeIndividus :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeIndividus)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeIndividus[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeIndividus)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeIndividus)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        listeIndividus = self.GetIDcoches()
        self.parent.ctrl_activites.SetDonnees(listeIndividus, self.date_debut, self.date_fin)
        listeActivites = self.parent.ctrl_activites.GetListeActivites()
        self.parent.ctrl_unites.SetDonnees(listeIndividus, listeActivites, self.date_debut, self.date_fin)
        self.parent.MAJ_signataires()

    def GetListeIndividus(self):
        return self.GetIDcoches() 
    
    def GetDictIndividus(self):
        return self.dictIndividus
    
    def GetTexteNoms(self):
        """ Récupère les noms sous la forme David DUPOND et Maxime DURAND... """
        listeNoms = []
        listeIDIndividu = self.GetListeIndividus() 
        for IDindividu, dictIndividu in self.dictIndividus.iteritems() :
            nom = dictIndividu["nom"]
            prenom = dictIndividu["prenom"]
            if IDindividu in listeIDIndividu :
                listeNoms.append(u"%s %s" % (prenom, nom))
        
        texteNoms = u""
        nbreIndividus = len(listeNoms)
        if nbreIndividus == 0 : texteNoms = u""
        if nbreIndividus == 1 : texteNoms = listeNoms[0]
        if nbreIndividus == 2 : texteNoms = _(u"%s et %s") % (listeNoms[0], listeNoms[1])
        if nbreIndividus > 2 :
            for texteNom in listeNoms[:-2] :
                texteNoms += u"%s, " % texteNom
            texteNoms += _(u"%s et %s") % (listeNoms[-2], listeNoms[-1])
        
        return texteNoms

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.listeIndividus = []
        self.date_debut = None
        self.date_fin = None
        self.listeActivites = []
        self.dictActivites = {}
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetDonnees(self, listeIndividus=[], date_debut=None, date_fin=None):
        self.listeIndividus = listeIndividus
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeActivites, self.dictActivites = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeActivites = []
        dictActivites = {}
        if len(self.listeIndividus) == 0 or self.date_debut == None or self.date_fin == None :
            return listeActivites, dictActivites 
        # Récupération des activités disponibles
        if len(self.listeIndividus) == 0 : conditionIndividus = "()"
        elif len(self.listeIndividus) == 1 : conditionIndividus = "(%d)" % self.listeIndividus[0]
        else : conditionIndividus = str(tuple(self.listeIndividus))
        DB = GestionDB.DB()
        req = """SELECT consommations.IDactivite, activites.nom, activites.abrege
        FROM consommations
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        WHERE consommations.IDindividu IN %s
        AND consommations.date>='%s' AND consommations.date<='%s'
        GROUP BY consommations.IDactivite
        ;""" % (conditionIndividus, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege in listeDonnees :
            dictTemp = { "nom" : nom, "abrege" : abrege}
            dictActivites[IDactivite] = dictTemp
            listeActivites.append((nom, IDactivite))
        listeActivites.sort()
        return listeActivites, dictActivites

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDactivite in self.listeActivites :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeActivites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeActivites[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeActivites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeActivites)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        listeSelections = self.GetIDcoches()
        self.parent.ctrl_unites.SetDonnees(self.listeIndividus, listeSelections, self.date_debut, self.date_fin)
        self.parent.MAJ_signataires()
    
    def GetListeActivites(self):
        return self.GetIDcoches() 
    
    def GetDictActivites(self):
        return self.dictActivites
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Unites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.listeIndividus = []
        self.date_debut = None
        self.date_fin = None
        self.listeActivites = []
        self.listeUnites = []
        # Binds
##        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetDonnees(self, listeIndividus=[], listeActivites=[], date_debut=None, date_fin=None):
        self.listeIndividus = listeIndividus
        self.listeActivites = listeActivites
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeUnites = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeUnites = []
        if len(self.listeIndividus) == 0 or len(self.listeActivites) == 0 or self.date_debut == None or self.date_fin == None :
            return listeUnites 
        # Récupération des activités disponibles
        if len(self.listeIndividus) == 0 : conditionIndividus = "()"
        elif len(self.listeIndividus) == 1 : conditionIndividus = "(%d)" % self.listeIndividus[0]
        else : conditionIndividus = str(tuple(self.listeIndividus))
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        
        if self.parent.ctrl_afficher_conso.GetValue() == True :
            conditionConso = "AND prestations.categorie='consommation'"
        else :
            conditionConso = ""
        
        DB = GestionDB.DB()
        req = """SELECT prestations.label
        FROM prestations
        WHERE (IDindividu IN %s OR IDindividu IS NULL)
        AND (prestations.IDactivite IN %s or prestations.IDactivite IS NULL)
        AND prestations.date>='%s' AND prestations.date<='%s'
        AND prestations.IDfamille=%d
        %s
        GROUP BY prestations.label
        ;""" % (conditionIndividus, conditionActivites, self.date_debut, self.date_fin, self.parent.IDfamille, conditionConso)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for label, in listeDonnees :
            listeUnites.append(label)
        listeUnites.sort()
        return listeUnites

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for label in self.listeUnites :
            self.Append(label)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeUnites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeUnites[index])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeUnites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeUnites)):
            ID = self.listeUnites[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        listeSelections = self.GetIDcoches()
        return
    
    def GetListeUnites(self):
        return self.GetIDcoches() 
    
    def GetDictUnites(self):
        return self.dictUnites
    
# ----------------------------------------------------------------------------------------------------------------------------------

##class CTRL_Signataires(wx.Choice):
##    def __init__(self, parent):
##        wx.Choice.__init__(self, parent, -1) 
##        self.parent = parent
##        self.listeActivites = []
##        self.MAJ() 
##        if len(self.dictDonnees) > 0 :
##            self.SetSelection(0)
##    
##    def MAJ(self, listeActivites=[] ):
##        self.listeActivites = listeActivites
##        listeItems, indexDefaut = self.GetListeDonnees()
##        if len(listeItems) == 0 :
##            self.Enable(False)
##        else:
##            self.Enable(True)
##        self.SetItems(listeItems)
##        if indexDefaut != None :
##            self.Select(indexDefaut)
##
##        # Recherche le nom de l'utilisateur parmi la liste des signataires
##        dictUtilisateur = UTILS_Identification.GetDictUtilisateur()
##        for index, dictDonnees in self.dictDonnees.iteritems() :
##            if dictUtilisateur != None :
##                texte1 = u"%s %s" % (dictUtilisateur["prenom"], dictUtilisateur["nom"])
##                texte2 = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
##                if dictDonnees["nom"].lower() == texte1.lower() or dictDonnees["nom"].lower() == texte2.lower() :
##                    self.SetSelection(index)
##
##    def GetListeDonnees(self):
##        if len(self.listeActivites) == 0 : conditionActivites = "()"
##        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
##        else : conditionActivites = str(tuple(self.listeActivites))
##        db = GestionDB.DB()
##        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
##        FROM responsables_activite
##        WHERE IDactivite IN %s
##        ORDER BY nom;""" % conditionActivites
##        db.ExecuterReq(req)
##        listeDonnees = db.ResultatReq()
##        db.Close()
##        listeItems = []
##        self.dictDonnees = {}
##        indexDefaut = None
##        index = 0
##        for IDresponsable, IDactivite, nom, fonction, defaut, sexe in listeDonnees :
##            if indexDefaut == None and defaut == 1 : indexDefaut = index
##            self.dictDonnees[index] = { 
##                "ID" : IDresponsable, "IDactivite" : IDactivite,
##                "nom" : nom, "fonction" : fonction,
##                "defaut" : defaut, "sexe" : sexe, 
##                }
##            listeItems.append(nom)
##            index += 1
##        return listeItems, indexDefaut
##
##    def SetID(self, ID=0):
##        for index, values in self.dictDonnees.iteritems():
##            if values["ID"] == ID :
##                 self.SetSelection(index)
##
##    def GetID(self):
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]["ID"]
##    
##    def GetInfos(self):
##        """ Récupère les infos sur le signataire sélectionné """
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Donnees(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, size=(200, 200), style=wx.WANTS_CHARS)
        self.moveTo = None
        self.parent = parent
        self.dictCodes = {}
        
        self.MAJ_CTRL_Donnees() 
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        # Calcul du nbre de lignes
        nbreLignes = 0
        for dictCategorie in LISTE_DONNEES :
            nbreLignes += 1
            for dictChamp in dictCategorie["champs"] :
                nbreLignes += 1
        
        # Création de la grille
        self.CreateGrid(nbreLignes, 2)
        self.SetColSize(0, 150)
        self.SetColSize(1, 300)
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.SetColLabelSize(1)
        
        # Remplissage avec les données
        key = 0
        for dictCategorie in LISTE_DONNEES :
            nomCategorie = dictCategorie["nom"]
            
            # Création d'une ligne CATEGORIE
            self.SetRowLabelValue(key, "")
            self.SetCellFont(key, 0, wx.Font(8, wx.DEFAULT , wx.NORMAL, wx.BOLD))
            self.SetCellBackgroundColour(key, 0, "#C5DDFA")
            self.SetReadOnly(key, 0, True)
            self.SetCellValue(key, 0, nomCategorie)
            self.SetCellAlignment(key, 0, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            self.SetCellValue(key, 1, "")
            self.SetCellBackgroundColour(key, 1, "#C5DDFA")
            self.SetReadOnly(key, 1, True)
            self.SetCellSize(key, 0, 1, 2)
            
            key += 1
            
            # Création d'une ligne de données
            for dictChamp in dictCategorie["champs"] :
                code = dictChamp["code"]
                label = dictChamp["label"]
                if DICT_DONNEES.has_key(code):
                    valeur = DICT_DONNEES[code]
                else:
                    valeur = u""
                
                # Entete de ligne
                self.SetRowLabelValue(key, "")
                
                # Création de la cellule LABEL
                self.SetCellValue(key, 0, label)
                self.SetCellBackgroundColour(key, 0, "#EEF4FB")
                self.SetReadOnly(key, 0, True)
                self.SetCellAlignment(key, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellValue(key, 1, valeur)
            
                # Mémorisation dans le dictionnaire des données
                self.dictCodes[key] = code
                key += 1
            
        # test all the events
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        
        self.moveTo = (1, 1)

    def OnCellChange(self, evt):
        # Modification de la valeur dans le dict de données
        numRow = evt.GetRow()
        valeur = self.GetCellValue(numRow, 1)
        code = self.dictCodes[numRow]
        self.SetValeur(code, valeur)
        
    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        evt.Skip()

    def GetValeur(self, code=""):
        if DICT_DONNEES.has_key(code) :
            return DICT_DONNEES[code]
        else:
            return None

    def SetValeur(self, code="", valeur = u""):
        global DICT_DONNEES
        DICT_DONNEES[code] = valeur

    def MAJ_CTRL_Donnees(self):
        """ Importe les valeurs de base dans le GRID Données """
        DB = GestionDB.DB()
        
        # Récupération des infos sur l'attestation
        dateDuJour = str(datetime.date.today())
        self.SetValeur("date", DateEngFr(dateDuJour))
        
        req = """SELECT MAX(numero)
        FROM attestations
        ;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        if len(listeDonnees) > 0 : 
            numero = listeDonnees[0][0]
            if numero == None :
                numero = 1
            else:
                numero += 1
        self.SetValeur("numero", u"%06d" % numero)
        
        # Récupération des infos sur l'organisme
        req = """SELECT nom, num_siret, code_ape, ville
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        for nom, num_siret, code_ape, ville in listeDonnees :
            if num_siret != None : self.SetValeur("siret", num_siret)
            if code_ape != None : self.SetValeur("ape", code_ape)
            if ville != None : self.SetValeur("lieu", ville.capitalize() )
        
        # Récupération des données sur le destinataire
        req = """SELECT IDrattachement, rattachements.IDindividu, rattachements.IDfamille, IDcategorie, titulaire, nom, prenom, IDcompte_payeur, adresse_auto, rue_resid, cp_resid, ville_resid
        FROM rattachements 
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = rattachements.IDfamille
        WHERE rattachements.IDfamille=%d and titulaire=1 and IDcategorie=1
        ORDER BY IDrattachement;""" % self.parent.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeTitulaires = []
        rue = u""
        ville = u""
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom, IDcompte_payeur, adresse_auto, rue_resid, cp_resid, ville_resid in listeDonnees :
            if rue_resid == None : rue_resid = u""
            if cp_resid == None : cp_resid = u""
            if ville_resid == None : ville_resid = u""
            if adresse_auto == None :
                rue = rue_resid
                ville = u"%s %s" % (cp_resid, ville_resid)
##            nomIndividu = u"%s %s" % (nom, prenom)
##            listeTitulaires.append(nomIndividu)
##        nbreTitulaires = len(listeTitulaires)
##        if nbreTitulaires == 0 : 
##            nomTitulaires = _(u"Pas de titulaires !")
##            IDcompte_payeur = None
##        if nbreTitulaires == 1 : 
##            nomTitulaires = listeTitulaires[0]
##        if nbreTitulaires == 2 : 
##            nomTitulaires = _(u"%s et %s") % (listeTitulaires[0], listeTitulaires[1])
##        if nbreTitulaires > 2 :
##            nomTitulaires = ""
##            for nomTitulaire in listeTitulaires[:-2] :
##                nomTitulaires += u"%s, " % nomTitulaire
##            nomTitulaires += _(u" et %s") % listeTitulaires[-1]
        
        nomTitulaires = UTILS_Titulaires.GetTitulaires([self.parent.IDfamille,]) 
        
        self.SetValeur("nom", nomTitulaires[self.parent.IDfamille]["titulairesAvecCivilite"])
        self.SetValeur("rue", rue)
        self.SetValeur("ville", ville)
        


# --------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, date_debut=None, date_fin=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_attestation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.dictSave = {}
                
        # Bandeau
        intro = _(u"Vous pouvez ici éditer une attestation de présence au format PDF. Saisissez une période, sélectionnez les éléments de votre choix, puis cliquez sur 'Aperçu'.")
        titre = _(u"Edition d'une attestation de présence")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.bouton_date_debut = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Calendrier.png", wx.BITMAP_TYPE_ANY))
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        self.bouton_date_fin = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Calendrier.png", wx.BITMAP_TYPE_ANY))

        # Individus
        self.staticbox_individus_staticbox = wx.StaticBox(self, -1, _(u"Sélection des individus"))
        self.ctrl_individus = CTRL_Individus(self)
        self.ctrl_individus.SetMinSize((170, 60))

        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Sélection des activités"))
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((-1, 80))
        
        # Unités
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, _(u"Sélection des prestations"))
        self.ctrl_unites = CTRL_Unites(self)
        self.ctrl_unites.SetMinSize((-1, 80))
        self.ctrl_afficher_conso = wx.CheckBox(self, -1, _(u"Afficher uniquement les conso"))
        self.ctrl_afficher_conso.SetValue(True) 
        
        # Données
        self.staticbox_donnees_staticbox = wx.StaticBox(self, -1, _(u"Données"))
        self.ctrl_donnees = CTRL_Donnees(self)

        # Options
        self.ctrl_parametres = CTRL_Attestations_options.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnTextDateDebut, self.ctrl_date_debut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateDebut, self.bouton_date_debut)
        self.Bind(wx.EVT_TEXT, self.OnTexteDateFin, self.ctrl_date_fin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateFin, self.bouton_date_fin)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAfficherConso, self.ctrl_afficher_conso)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        # Init contrôles
        if date_debut != None : 
            self.ctrl_date_debut.SetDate(date_debut)
        if date_fin != None : 
            self.ctrl_date_fin.SetDate(date_fin)
        if date_debut != None and date_fin != None :
            self.ctrl_individus.SetPeriode(date_debut, date_fin)
            listeIndividus = self.ctrl_individus.GetListeIndividus()
            self.ctrl_activites.SetDonnees(listeIndividus, date_debut, date_fin)
            listeActivites = self.ctrl_activites.GetListeActivites()
            self.ctrl_unites.SetDonnees(listeIndividus, listeActivites, date_debut, date_fin)
        
        

    def __set_properties(self):
        self.SetTitle(_(u"Edition d'une attestation de présence"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début"))
        self.bouton_date_debut.SetToolTipString(_(u"Cliquez ici pour sélectionner la date de début"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin"))
        self.bouton_date_fin.SetToolTipString(_(u"Cliquez ici pour sélectionner la date de fin"))
        self.ctrl_individus.SetToolTipString(_(u"Cochez les individus"))
        self.ctrl_activites.SetToolTipString(_(u"Cochez les activités"))
        self.ctrl_unites.SetToolTipString(_(u"Cochez les unites"))
        self.ctrl_donnees.SetToolTipString(_(u"Vous pouvez modifier ici les données de base"))
        self.ctrl_afficher_conso.SetToolTipString(_(u"Cochez cette case pour afficher uniquement les consommations dans la liste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_email.SetToolTipString(_(u"Cliquez ici pour envoyer ce document par Email"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour afficher le PDF"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((760, 660))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Période
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_periode.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_date_debut, 0, 0, 0)
        grid_sizer_periode.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_date_fin, 0, 0, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Individus
        staticbox_individus = wx.StaticBoxSizer(self.staticbox_individus_staticbox, wx.VERTICAL)
        staticbox_individus.Add(self.ctrl_individus, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_individus, 1, wx.EXPAND, 0)
        
        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_activites, 1, wx.EXPAND, 0)
        
        # unites
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites_staticbox, wx.VERTICAL)
        staticbox_unites.Add(self.ctrl_unites, 1, wx.ALL|wx.EXPAND, 5)
        staticbox_unites.Add(self.ctrl_afficher_conso, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_unites, 1, wx.EXPAND, 0)
        
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableRow(2)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Données
        staticbox_donnees = wx.StaticBoxSizer(self.staticbox_donnees_staticbox, wx.VERTICAL)
        staticbox_donnees.Add(self.ctrl_donnees, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_donnees, 1, wx.EXPAND, 0)
        
        # Options
        grid_sizer_droit.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
##        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def MAJlistes(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        self.ctrl_individus.SetPeriode(date_debut, date_fin)
        listeIndividus = self.ctrl_individus.GetListeIndividus()
        self.ctrl_activites.SetDonnees(listeIndividus, date_debut, date_fin)
        listeActivites = self.ctrl_activites.GetListeActivites()
        self.ctrl_unites.SetDonnees(listeIndividus, listeActivites, date_debut, date_fin)
        self.MAJ_signataires()
    
    def MAJ_signataires(self):
        # MAJ du contrôle Paramètres
        self.ctrl_parametres.ctrl_parametres.listeActivites = self.ctrl_activites.GetListeActivites()
        self.ctrl_parametres.ctrl_parametres.MAJ_signataires() 
    
    def OnCheckAfficherConso(self, event):
        self.ctrl_unites.MAJ() 
        self.ctrl_unites.CocheTout()
        
    def OnTextDateDebut(self, event): 
        date = self.ctrl_date_debut.GetDate() 
        self.MAJlistes() 

    def OnBoutonDateDebut(self, event):
        import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_debut.SetDate(date)
        dlg.Destroy()

    def OnTexteDateFin(self, event): 
        date = self.ctrl_date_fin.GetDate() 
        self.MAJlistes() 

    def OnBoutonDateFin(self, event):
        import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_fin.SetDate(date)
        dlg.Destroy()        

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Gnreruneattestationdeprsence")

    def Sauvegarder(self):
        """ Sauvegarder la trace de l'attestation """
        if len(self.dictSave) == 0 : 
            return
        
        # Demande la confirmation de sauvegarde
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous mémoriser l'attestation créée ?\n\n(Cliquez NON si c'était juste un test sinon cliquez OUI)"), _(u"Sauvegarde"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        # Sauvegarde de l'attestation
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("numero", self.dictSave["numero"] ), 
            ("IDfamille", self.dictSave["IDfamille"] ), 
            ("date_edition", self.dictSave["date_edition"] ), 
            ("activites", self.dictSave["activites"] ), 
            ("individus", self.dictSave["individus"] ), 
            ("IDutilisateur", self.dictSave["IDutilisateur"] ), 
            ("date_debut", self.dictSave["date_debut"] ), 
            ("date_fin", self.dictSave["date_fin"] ), 
            ("total", self.dictSave["total"] ), 
            ("regle", self.dictSave["regle"] ), 
            ("solde", self.dictSave["solde"] ), 
            ]
        IDattestation = DB.ReqInsert("attestations", listeDonnees)        
        DB.Close()
        
        # Mémorisation de l'action dans l'historique
        UTILS_Historique.InsertActions([{
                "IDfamille" : self.IDfamille,
                "IDcategorie" : 27, 
                "action" : _(u"Edition d'une attestation de présence pour la période du %s au %s pour un total de %.02f € et un solde de %.02f €") % (DateEngFr(self.dictSave["date_debut"]), DateEngFr(self.dictSave["date_fin"]), self.dictSave["total"], self.dictSave["solde"] ),
                },])
        
        # Mémorisation des paramètres
        self.ctrl_parametres.MemoriserParametres() 
        
    
    def OnBoutonAnnuler(self, event):
        self.Sauvegarder() 
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonEmail(self, event): 
        """ Envoi par mail """
        import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc="Temp/Attestation_presence.pdf", categorie="attestation_presence")

    def OnBoutonOk(self, event): 
        self.CreationPDF() 

    def CreationPDF(self, nomDoc="Temp/Attestation_presence.pdf", afficherDoc=True):        
        # Récupération du dictOptions
        dictOptions = self.ctrl_parametres.GetOptions() 
        if dictOptions == False :
            return False
        
        # Récupération du signataire
        infosSignataire = self.ctrl_parametres.ctrl_parametres.GetInfosSignataire() 
        if infosSignataire == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun signataire !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        nomSignataire = infosSignataire["nom"]
        fonctionSignataire = infosSignataire["fonction"]
        sexeSignataire = infosSignataire["sexe"]
        if sexeSignataire == "H" :
            genreSignataire = u""
        else:
            genreSignataire = u"e"


        dictChampsFusion = {}

        # Récupération des valeurs
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        listeIndividus = self.ctrl_individus.GetListeIndividus()
        listeActivites = self.ctrl_activites.GetListeActivites()
        listeUnites = self.ctrl_unites.GetListeUnites()
        
        dictDonnees = DICT_DONNEES
        
        # Récupération des présences
        if len(listeIndividus) == 0 : conditionIndividus = "()"
        elif len(listeIndividus) == 1 : conditionIndividus = "(%d)" % listeIndividus[0]
        else : conditionIndividus = str(tuple(listeIndividus))
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        DB = GestionDB.DB()
        
        # Récupération de tous les individus de la base
        req = """
        SELECT IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid
        FROM individus
        ;""" 
        DB.ExecuterReq(req)
        listeIndividus2 = DB.ResultatReq()  
        dictIndividus = {}
        for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid in listeIndividus2 :
            dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "adresse_auto":adresse_auto, "rue_resid":rue_resid, "cp_resid":cp_resid, "ville_resid":ville_resid}

        if self.ctrl_afficher_conso.GetValue() == True :
            conditionConso = "AND prestations.categorie='consommation'"
        else :
            conditionConso = ""

        # Recherche des prestations
        req = u"""
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.IDfamille, prestations.date, categorie, 
        label, prestations.montant_initial, prestations.montant, prestations.tva,
        prestations.IDactivite, activites.nom, activites.abrege,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, IDfacture, 
        prestations.IDindividu, 
        individus.IDcivilite, individus.nom, individus.prenom, individus.date_naiss, 
        SUM(ventilation.montant) AS montant_ventilation
        FROM prestations
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON tarifs.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        WHERE (prestations.IDindividu IN %s OR prestations.IDindividu IS NULL)
        AND (prestations.IDactivite IN %s or prestations.IDactivite IS NULL)
        AND prestations.date>='%s' AND prestations.date<='%s'
        AND prestations.IDfamille=%d
        %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % (conditionIndividus, conditionActivites, date_debut, date_fin, self.IDfamille, conditionConso)
        DB.ExecuterReq(req)
        listePrestationsTemp = DB.ResultatReq()  
        
        # Filtre des noms de prestations
        listePrestations = []
        for donnees in listePrestationsTemp :
            if donnees[5] in listeUnites :
                listePrestations.append(donnees)
        
        if len(listePrestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'existe aucune prestation avec les paramètres donnés !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Recherche des déductions
        req = u"""
        SELECT IDdeduction, IDprestation, IDfamille, date, montant, label, IDaide
        FROM deductions
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = deductions.IDcompte_payeur
        AND comptes_payeurs.IDfamille=%d
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDeductionsTemp = DB.ResultatReq()  
        dictDeductions = {}
        for IDdeduction, IDprestation, IDfamille, date, montant, label, IDaide in listeDeductionsTemp :
            if dictDeductions.has_key(IDprestation) == False :
                dictDeductions[IDprestation] = []
            dictDeductions[IDprestation].append({"IDdeduction":IDdeduction, "date":date, "montant":montant, "label":label, "IDaide":IDaide})
            
        # Recherche des consommations (sert pour les forfaits)
        req = """
        SELECT IDconso, consommations.date, consommations.IDprestation
        FROM consommations
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        WHERE (consommations.IDindividu IN %s OR consommations.IDindividu IS NULL)
        AND (prestations.IDactivite IN %s or prestations.IDactivite IS NULL)
        AND prestations.date>='%s' AND prestations.date<='%s'
        AND prestations.IDfamille=%d
        AND prestations.categorie='consommation'
        ;""" % (conditionIndividus, conditionActivites, date_debut, date_fin, self.IDfamille)
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()  
        dictConsommations = {}
        for IDconso, date, IDprestation in listeConsommations :
            date = DateEngEnDateDD(date)
            if dictConsommations.has_key(IDprestation) == False :
                dictConsommations[IDprestation] = []
            if date not in dictConsommations[IDprestation] :
                dictConsommations[IDprestation].append(date)
        
        # Recherche des numéros d'agréments
        req = """
        SELECT IDactivite, agrement, date_debut, date_fin
        FROM agrements
        WHERE IDactivite IN %s
        ORDER BY date_debut
        """ % conditionActivites
        DB.ExecuterReq(req)
        listeAgrements = DB.ResultatReq()  

        # Récupération des infos sur l'organisme
        req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        dictOrganisme = {}
        for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees :
            dictOrganisme["nom"] = nom
            dictOrganisme["rue"] = rue
            dictOrganisme["cp"] = cp
            if ville != None : ville = ville.capitalize()
            dictOrganisme["ville"] = ville
            dictOrganisme["tel"] = tel
            dictOrganisme["fax"] = fax
            dictOrganisme["mail"] = mail
            dictOrganisme["site"] = site
            dictOrganisme["num_agrement"] = num_agrement
            dictOrganisme["num_siret"] = num_siret
            dictOrganisme["code_ape"] = code_ape

        DB.Close() 

        # Get noms Titulaires
        dictNomsTitulaires = UTILS_Titulaires.GetTitulaires() 

        # Récupération des questionnaires
        Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")

        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 

        # ----------------------------------------------------------------------------------------------------
        # Analyse et regroupement des données
        dictValeurs = {}
        listeActivitesUtilisees = []
        for IDprestation, IDcompte_payeur, IDfamille, date, categorie, label, montant_initial, montant, tva, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDcivilite, nomIndividu, prenomIndividu, dateNaiss, montant_ventilation in listePrestations :
            montant_initial = FloatToDecimal(montant_initial) 
            montant = FloatToDecimal(montant) 
            montant_ventilation = FloatToDecimal(montant_ventilation) 
            
            # Regroupement par compte payeur
            if dictValeurs.has_key(IDcompte_payeur) == False :
                    
                # Recherche des titulaires
                dictInfosTitulaires = dictNomsTitulaires[IDfamille]
                nomsTitulairesAvecCivilite = dictInfosTitulaires["titulairesAvecCivilite"]
                nomsTitulairesSansCivilite = dictInfosTitulaires["titulairesSansCivilite"]
                rue_resid = dictInfosTitulaires["adresse"]["rue"]
                cp_resid = dictInfosTitulaires["adresse"]["cp"]
                ville_resid = dictInfosTitulaires["adresse"]["ville"]
                
                # Mémorisation des infos                
                dictValeurs[IDcompte_payeur] = {
                    "nomSansCivilite" : nomsTitulairesSansCivilite,
                    "IDfamille" : IDfamille,
                    "{IDFAMILLE}" : str(IDfamille),
                    "individus" : {},
                    "listePrestations" : [],
                    "prestations_familiales" : [],
                    "total" : FloatToDecimal(0.0),
                    "ventilation" : FloatToDecimal(0.0),
                    "solde" : FloatToDecimal(0.0),
                    "num_attestation" : dictDonnees["numero"],
                    "select" : True,
                    "date_debut" : date_debut,
                    "date_fin" : date_fin,

                    "{LIEU_EDITION}" : dictDonnees["lieu"],
                    "{DESTINATAIRE_NOM}" : dictDonnees["nom"],
                    "{DESTINATAIRE_RUE}" : dictDonnees["rue"],
                    "{DESTINATAIRE_VILLE}" : dictDonnees["ville"],
                    
                    "{NUM_ATTESTATION}" : dictDonnees["numero"],
                    "{DATE_EDITION}" : dictDonnees["date"],
                    "{DATE_DEBUT}" : DateEngFr(str(date_debut)),
                    "{DATE_FIN}" : DateEngFr(str(date_fin)),
                    "{NOMS_INDIVIDUS}" : self.ctrl_individus.GetTexteNoms(),

                    "{ORGANISATEUR_NOM}" : dictOrganisme["nom"],
                    "{ORGANISATEUR_RUE}" : dictOrganisme["rue"],
                    "{ORGANISATEUR_CP}" : dictOrganisme["cp"],
                    "{ORGANISATEUR_VILLE}" : dictOrganisme["ville"],
                    "{ORGANISATEUR_TEL}" : dictOrganisme["tel"],
                    "{ORGANISATEUR_FAX}" : dictOrganisme["fax"],
                    "{ORGANISATEUR_MAIL}" : dictOrganisme["mail"],
                    "{ORGANISATEUR_SITE}" : dictOrganisme["site"],
                    "{ORGANISATEUR_AGREMENT}" : dictOrganisme["num_agrement"],
                    "{ORGANISATEUR_SIRET}" : dictOrganisme["num_siret"],
                    "{ORGANISATEUR_APE}" : dictOrganisme["code_ape"],
                    
                    "{SIGNATAIRE_GENRE}" : genreSignataire,
                    "{SIGNATAIRE_NOM}" : nomSignataire,
                    "{SIGNATAIRE_FONCTION}" : fonctionSignataire,
                    }
                
                # Ajoute les infos de base familles
                dictValeurs[IDcompte_payeur].update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))
                
                # Ajoute les réponses des questionnaires
                for dictReponse in Questionnaires.GetDonnees(IDfamille) :
                    dictValeurs[IDcompte_payeur][dictReponse["champ"]] = dictReponse["reponse"]
                    if dictReponse["controle"] == "codebarres" :
                        dictValeurs[IDcompte_payeur]["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

                # Fusion pour textes personnalisés
                dictValeurs[IDcompte_payeur]["texte_titre"] = CTRL_Attestations_options.RemplaceMotsCles(dictOptions["texte_titre"], dictValeurs[IDcompte_payeur])
                dictValeurs[IDcompte_payeur]["texte_introduction"] = CTRL_Attestations_options.RemplaceMotsCles(dictOptions["texte_introduction"], dictValeurs[IDcompte_payeur])
                dictValeurs[IDcompte_payeur]["texte_conclusion"] = CTRL_Attestations_options.RemplaceMotsCles(dictOptions["texte_conclusion"], dictValeurs[IDcompte_payeur])


##        # Récupération et transformation du texte d'intro
##        if self.ctrl_intro.GetValue() == True :
##            textIntro = self.ctrl_texte_intro.GetValue()         
##            textIntro = textIntro.replace("{GENRE}", genreSignataire)
##            textIntro = textIntro.replace("{NOM}", nomSignataire)
##            textIntro = textIntro.replace("{FONCTION}", fonctionSignataire)
##            textIntro = textIntro.replace("{ENFANTS}", self.ctrl_individus.GetTexteNoms() )
##            textIntro = textIntro.replace("{DATE_DEBUT}", DateEngFr(str(date_debut)))
##            textIntro = textIntro.replace("{DATE_FIN}", DateEngFr(str(date_fin)))
##            dictValeurs[self.IDfamille]["intro"] = textIntro
##        else:
##            dictValeurs[self.IDfamille]["intro"] = None


            # Insert les montants pour le compte payeur
            if montant_ventilation == None : montant_ventilation = FloatToDecimal(0.0)
            dictValeurs[IDcompte_payeur]["total"] += montant
            dictValeurs[IDcompte_payeur]["ventilation"] += montant_ventilation
            dictValeurs[IDcompte_payeur]["solde"] = dictValeurs[IDcompte_payeur]["total"] - dictValeurs[IDcompte_payeur]["ventilation"]
            
            dictValeurs[IDcompte_payeur]["{TOTAL_PERIODE}"] = u"%.02f %s" % (dictValeurs[IDcompte_payeur]["total"], SYMBOLE)
            dictValeurs[IDcompte_payeur]["{TOTAL_REGLE}"] = u"%.02f %s" % (dictValeurs[IDcompte_payeur]["ventilation"], SYMBOLE)
            dictValeurs[IDcompte_payeur]["{SOLDE_DU}"] = u"%.02f %s" % (dictValeurs[IDcompte_payeur]["solde"], SYMBOLE)


            # Ajout d'une prestation familiale
            if IDindividu == None : 
                IDindividu = 0
            if IDactivite == None :
                IDactivite = 0
            
            # Ajout d'un individu
            if dictValeurs[IDcompte_payeur]["individus"].has_key(IDindividu) == False :
                if dictIndividus.has_key(IDindividu) :
                    
                    # Si c'est bien un individu
                    IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                    nomIndividu = dictIndividus[IDindividu]["nom"]
                    prenomIndividu = dictIndividus[IDindividu]["prenom"]
                    dateNaiss = dictIndividus[IDindividu]["date_naiss"]
                    if dateNaiss != None : 
                        if DICT_CIVILITES[IDcivilite]["sexe"] == "M" :
                            texteDateNaiss = _(u", né le %s") % DateEngFr(str(dateNaiss))
                        else:
                            texteDateNaiss = _(u", née le %s") % DateEngFr(str(dateNaiss))
                    else:
                        texteDateNaiss = u""
                    texteIndividu = _(u"<b>%s %s</b><font size=7>%s</font>") % (nomIndividu, prenomIndividu, texteDateNaiss)
                    nom = u"%s %s" % (nomIndividu, prenomIndividu)
                    
                else:
                    # Si c'est pour une prestation familiale on créé un individu ID 0 :
                    nom = _(u"Prestations familiales")
                    texteIndividu = u"<b>%s</b>" % nom
                    
                dictValeurs[IDcompte_payeur]["individus"][IDindividu] = { "texte" : texteIndividu, "activites" : {}, "total" : FloatToDecimal(0.0), "ventilation" : FloatToDecimal(0.0), "total_reports" : FloatToDecimal(0.0), "nom" : nom, "select" : True }
            
            # Ajout de l'activité
            if dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"].has_key(IDactivite) == False :
                texteActivite = nomActivite
                agrement = RechercheAgrement(listeAgrements, IDactivite, date)
                if agrement != None :
                    texteActivite += _(u" - n° agrément : %s") % agrement
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite] = { "texte" : texteActivite, "presences" : {} }
            
            # Ajout de la présence
            if dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"].has_key(date) == False :
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date] = { "texte" : DateEngFr(str(date)), "unites" : [], "total" : FloatToDecimal(0.0) }
            
            # Recherche du nbre de dates pour cette prestation
            if dictConsommations.has_key(IDprestation) :
                listeDates = dictConsommations[IDprestation]
            else:
                listeDates = []
            
            # Recherche des déductions
            if dictDeductions.has_key(IDprestation) :
                deductions = dictDeductions[IDprestation]
            else :
                deductions = []
            
            # Adaptation du label
            if dictOptions["intitules"] == 2 and IDtarif != None :
                label = nomTarif
            if dictOptions["intitules"] == 3 and IDtarif != None :
                label = nomActivite
            
            # Mémorisation de la prestation
            dictPrestation = {
                "IDprestation" : IDprestation, "date" : date, "categorie" : categorie, "label" : label,
                "montant_initial" : montant_initial, "montant" : montant, "tva" : tva, 
                "IDtarif" : IDtarif, "nomTarif" : nomTarif, "nomCategorieTarif" : nomCategorieTarif, 
                "montant_ventilation" : montant_ventilation, "listeDatesConso" : listeDates,
                "deductions" : deductions,
                }

            dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["unites"].append(dictPrestation)
            
            # Ajout des totaux
            if montant != None : 
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["total"] += montant
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["total"] += montant
            if montant_ventilation != None : 
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["ventilation"] += montant_ventilation
            
            # Stockage des IDprestation pour saisir le IDfacture après création de la facture
            dictValeurs[IDcompte_payeur]["listePrestations"].append( (IDindividu, IDprestation) )
            
            # Mémorisation des activités concernées
            if IDactivite != None :
                listeActivitesUtilisees.append(IDactivite) 
        
        # --------------------------------------------------------------------------------------------------------------------
        
                
        # Préparation des données pour une sauvegarde de l'attestation
        self.dictSave = {}
        self.dictSave["numero"] = dictDonnees["numero"]
        self.dictSave["IDfamille"] = self.IDfamille
        self.dictSave["date_edition"] = DateFrEng(dictDonnees["date"])
        self.dictSave["activites"] = ";".join([str(IDactivite) for IDactivite in listeActivitesUtilisees]) 
        self.dictSave["individus"] = ";".join([str(IDindividu) for IDindividu in listeIndividus]) 
        self.dictSave["IDutilisateur"] = UTILS_Identification.GetIDutilisateur()
        self.dictSave["date_debut"] = str(date_debut)
        self.dictSave["date_fin"] = str(date_fin)
        self.dictSave["total"] = float(dictValeurs[IDcompte_payeur]["total"])
        self.dictSave["regle"] = float(dictValeurs[IDcompte_payeur]["ventilation"])
        self.dictSave["solde"] = float(dictValeurs[IDcompte_payeur]["ventilation"] - dictValeurs[IDcompte_payeur]["total"])

        # DictOptions
        dictOptions["date_debut"] = date_debut
        dictOptions["date_fin"] = date_fin
        dictOptions["codeBarre"] = True

        # Détail
        if dictOptions["affichage_prestations"] == 0 :
            detail = True
        else:
            detail = False
                
        # Champs pour fusion pour Emails
        dictChampsFusion["{NUMERO_ATTESTATION}"] = self.dictSave["numero"]
        dictChampsFusion["{DATE_DEBUT}"] = DateEngFr(str(date_debut))
        dictChampsFusion["{DATE_FIN}"] = DateEngFr(str(date_fin))
        dictChampsFusion["{DATE_EDITION_ATTESTATION}"] = DateEngFr(str(self.dictSave["date_edition"])) 
        dictChampsFusion["{INDIVIDUS_CONCERNES}"] = self.ctrl_individus.GetTexteNoms()
        dictChampsFusion["{SOLDE}"] = u"%.2f %s" % (self.dictSave["solde"], SYMBOLE)

        # Fabrication du PDF
        import UTILS_Impression_facture
        UTILS_Impression_facture.Impression(dictValeurs, dictOptions, dictOptions["IDmodele"], mode="attestation", ouverture=afficherDoc, nomFichier=nomDoc)#, titre=dictOptions["texte_titre"])
        
        return dictChampsFusion


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=14, date_debut=datetime.date(2013, 7, 1), date_fin=datetime.date(2014, 7, 30))
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
