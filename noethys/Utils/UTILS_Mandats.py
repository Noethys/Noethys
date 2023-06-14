#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import GestionDB
import datetime
from Utils import UTILS_Dates
from dateutil import relativedelta


ERREUR1 = _(u"Le mandat n'a pas été utilisé durant plus de 36 mois. Il faut donc refaire un nouveau mandat.")
ERREUR2 = _(u"Ce mandat ponctuel a déjà été utilisé une fois. Il faut refaire un nouveau mandat.")

LISTE_SEQUENCES = [
    (_(u"Automatique"), "auto"),
    (_(u"Prélèvement ponctuel (OOFF)"), "OOFF"),
    (_(u"Premier prélèvement d'une série (FRST)"), "FRST"),
    (_(u"Prélèvement suivant d'une série (RCUR)"), "RCUR"), 
    (_(u"Dernier prélèvement d'une série (FNAL)"), "FNAL"),
    ]




class Mandats():
    """ Récupère les mandats et vérifie leurs validités """
    def __init__(self):
        self.dictMandats, self.dictMandatsFamilles = self.GetMandats() 
        self.dictPrelevements = self.GetPrelevementsMandats() 
        
    
    def GetMandats(self):
        """ Récupération des mandats """
        DB = GestionDB.DB()
        req = """SELECT IDmandat, IDfamille, rum, type, date, IDbanque, mandats.IDindividu, individu_nom, iban, bic, sequence, actif, individus.nom, individus.prenom
        FROM mandats
        LEFT JOIN individus ON individus.IDindividu = mandats.IDindividu
        ORDER BY date;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictMandats = {}
        dictMandatsFamilles = {}
        for IDmandat, IDfamille, rum, type, date, IDbanque, IDindividu, individu_nom, iban, bic, sequence, actif, nomIndividu, prenomIndividu in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if IDindividu == None :
                if individu_nom == None : individu_nom = u""
                titulaire = individu_nom
            else :
                if nomIndividu == None : nomIndividu = u""
                if prenomIndividu == None : prenomIndividu = u""
                titulaire = u"%s %s" % (nomIndividu, prenomIndividu)
            dictTemp = {
                "IDmandat" : IDmandat, "IDfamille" : IDfamille, "rum" : rum, "type" : type, "date" : date, "IDbanque" : IDbanque, 
                "IDindividu" : IDindividu, "individu_nom" : individu_nom, "iban" : iban, "bic" : bic, "sequence" : sequence, "actif" : actif,
                "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu, "titulaire" : titulaire,
                }
            dictMandats[IDmandat] = dictTemp
            if (IDfamille in dictMandatsFamilles) == False :
                dictMandatsFamilles[IDfamille] = []
            dictMandatsFamilles[IDfamille].append(IDmandat)
        return dictMandats, dictMandatsFamilles
    
    def GetPrelevementsMandats(self):
        """ Récupère les prélèvements existants pour chaque mandat """
        DB = GestionDB.DB()
        # Prélèvements
        req = """SELECT IDprelevement, IDfamille, IDmandat, statut, lots_prelevements.date
        FROM prelevements
        LEFT JOIN lots_prelevements ON lots_prelevements.IDlot = prelevements.IDlot
        WHERE IDmandat IS NOT NULL
        ORDER BY lots_prelevements.date
        ;"""
        DB.ExecuterReq(req)
        listePrelevements = DB.ResultatReq()
        # Pièces PES ORMC
        req = """SELECT IDpiece, IDfamille, prelevement_IDmandat, prelevement_statut, pes_lots.date_prelevement
        FROM pes_pieces
        LEFT JOIN pes_lots ON pes_lots.IDlot = pes_pieces.IDlot
        WHERE prelevement_IDmandat IS NOT NULL AND prelevement=1
        ORDER BY pes_lots.date_prelevement
        ;"""
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()
        DB.Close()
        
        dictPrelevements = {}
        for listeDonnees in (listePrelevements, listePieces) :
            for IDprelevement, IDfamille, IDmandat, statut, date in listeDonnees :
                date = UTILS_Dates.DateEngEnDateDD(date)
                if (IDmandat in dictPrelevements) == False :
                    dictPrelevements[IDmandat] = []
                dictPrelevements[IDmandat].append({"IDprelevement":IDprelevement, "IDfamille":IDfamille, "IDmandat":IDmandat, "statut":statut, "date":date})
        return dictPrelevements
    
    def GetDictMandat(self, IDmandat=None):
        if (IDmandat in self.dictMandats) == True :
            return self.dictMandats[IDmandat]
        else :
            return None
        
    def RechercheMandatFamille(self, IDfamille=None):
        """ Recherche le mandat valide d'une famille """
        if (IDfamille in self.dictMandatsFamilles) == True :
            listeMandats = self.dictMandatsFamilles[IDfamille]
            for IDmandat in listeMandats :
                dictAnalyse = self.AnalyseMandat(IDmandat)
                if dictAnalyse["actif"] == True and dictAnalyse["valide"] == True :
                    return IDmandat
        return None
        
    def AnalyseMandat(self, IDmandat=None):
        """ Analyse un mandat """
        valide = True
        prochaineSequence = None
        
        if (IDmandat in self.dictMandats) == False :
            return False
        
        dictMandat = self.dictMandats[IDmandat]
        typeMandat = dictMandat["type"]
        sequence = dictMandat["sequence"]
        dateMandat = dictMandat["date"]
        if dictMandat["actif"] == 1 :
            mandatActif = True
        else :
            mandatActif = False
        
        # Recherche les prélèvements associés à ce mandat
        listePrelevements = []
        nbrePrelevementsValides = 0
        if IDmandat in self.dictPrelevements :
            listePrelevements = self.dictPrelevements[IDmandat]
            for dictPrelevement in listePrelevements :
                if dictPrelevement["statut"] == "valide" : 
                    nbrePrelevementsValides += 1
        nbrePrelevements = len(listePrelevements)
        
        # Vérifie si le mandat a bien été utilisé depuis 36 mois
##        dateJour = datetime.date.today() 
##        dateDerniereUtilisation = dateMandat
##        for dictPrelevement in listePrelevements :
##            if dictPrelevement["date"] > dateDerniereUtilisation : 
##                dateDerniereUtilisation = dictPrelevement["date"]
##        dateMaxMandat = dateDerniereUtilisation + relativedelta.relativedelta(months=+36)
##        if dateJour > dateMaxMandat :
##            valide = ERREUR1
        
        # Si mandat ponctuel : recherche s'il a déjà un prélèvement rattaché
        if typeMandat == "ponctuel" :
            if nbrePrelevementsValides > 0 :
                valide = ERREUR2
        
        # Si mandat ponctuel : recherche de la séquence
        if typeMandat == "ponctuel" :
            prochaineSequence = "OOFF"
        
        # Si mandat récurrent : recherche de la séquence
        if typeMandat == "recurrent" :
            if nbrePrelevementsValides == 0 :
                prochaineSequence = "FRST"
            else :
                prochaineSequence = "RCUR"
        
        # Si la prochaine séquence est spécifiée dans le mandat (si non 'automatique') :
        if sequence != "auto" :
            prochaineSequence = sequence
            
        # Renvoie les résultats
        dictResultat = {"valide" : valide, "actif" : mandatActif, "prochaineSequence" : prochaineSequence, "nbrePrelevements" : nbrePrelevements, "nbrePrelevementsValides" : nbrePrelevementsValides}
        return dictResultat
        


# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Sequence(wx.Choice):
    def __init__(self, parent, afficherAutomatique=True):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.afficherAutomatique = afficherAutomatique
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        listeLabels = []
        self.dictDonnees = {}
        liste_sequences = LISTE_SEQUENCES
        if self.afficherAutomatique == False :
            liste_sequences = LISTE_SEQUENCES[1:]
        index = 0
        for label, code in liste_sequences :
            listeLabels.append(label)
            self.dictDonnees[index] = code
            index += 1
        self.SetItems(listeLabels)
                                        
    def SetCode(self, code="auto"):
        if code == None :
            self.SetSelection(0)
        for index, codeTemp in self.dictDonnees.items():
            if codeTemp == code :
                 self.SetSelection(index)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
            





            
if __name__ == '__main__':
    mandats = Mandats() 
    print(mandats.AnalyseMandat(IDmandat=2))
    