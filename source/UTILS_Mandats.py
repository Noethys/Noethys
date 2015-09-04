#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import UTILS_Dates
from dateutil import relativedelta


ERREUR1 = _(u"Le mandat n'a pas �t� utilis� durant plus de 36 mois. Il faut donc refaire un nouveau mandat.")
ERREUR2 = _(u"Ce mandat ponctuel a d�j� �t� utilis� une fois. Il faut refaire un nouveau mandat.")

LISTE_SEQUENCES = [
    (_(u"Automatique"), "auto"),
    (_(u"Pr�l�vement ponctuel (OOFF)"), "OOFF"),
    (_(u"Premier pr�l�vement d'une s�rie (FRST)"), "FRST"),
    (_(u"Pr�l�vement suivant d'une s�rie (RCUR)"), "RCUR"), 
    (_(u"Dernier pr�l�vement d'une s�rie (FNAL)"), "FNAL"),
    ]




class Mandats():
    """ R�cup�re les mandats et v�rifie leurs validit�s """
    def __init__(self):
        self.dictMandats, self.dictMandatsFamilles = self.GetMandats() 
        self.dictPrelevements = self.GetPrelevementsMandats() 
        
    
    def GetMandats(self):
        """ R�cup�ration des mandats """
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
            if dictMandatsFamilles.has_key(IDfamille) == False :
                dictMandatsFamilles[IDfamille] = []
            dictMandatsFamilles[IDfamille].append(IDmandat)
        return dictMandats, dictMandatsFamilles
    
    def GetPrelevementsMandats(self):
        """ R�cup�re les pr�l�vements existants pour chaque mandat """
        DB = GestionDB.DB()
        # Pr�l�vements
        req = """SELECT IDprelevement, IDfamille, IDmandat, statut, lots_prelevements.date
        FROM prelevements
        LEFT JOIN lots_prelevements ON lots_prelevements.IDlot = prelevements.IDlot
        WHERE IDmandat IS NOT NULL
        ORDER BY lots_prelevements.date
        ;"""
        DB.ExecuterReq(req)
        listePrelevements = DB.ResultatReq()
        # Pi�ces PES ORMC
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
                if dictPrelevements.has_key(IDmandat) == False :
                    dictPrelevements[IDmandat] = []
                dictPrelevements[IDmandat].append({"IDprelevement":IDprelevement, "IDfamille":IDfamille, "IDmandat":IDmandat, "statut":statut, "date":date})
        return dictPrelevements
    
    def GetDictMandat(self, IDmandat=None):
        if self.dictMandats.has_key(IDmandat) == True :
            return self.dictMandats[IDmandat]
        else :
            return None
        
    def RechercheMandatFamille(self, IDfamille=None):
        """ Recherche le mandat valide d'une famille """
        if self.dictMandatsFamilles.has_key(IDfamille) == True :
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
        
        if self.dictMandats.has_key(IDmandat) == False :
            return False
        
        dictMandat = self.dictMandats[IDmandat]
        typeMandat = dictMandat["type"]
        sequence = dictMandat["sequence"]
        dateMandat = dictMandat["date"]
        if dictMandat["actif"] == 1 :
            mandatActif = True
        else :
            mandatActif = False
        
        # Recherche les pr�l�vements associ�s � ce mandat
        listePrelevements = []
        nbrePrelevementsValides = 0
        if self.dictPrelevements.has_key(IDmandat) :
            listePrelevements = self.dictPrelevements[IDmandat]
            for dictPrelevement in listePrelevements :
                if dictPrelevement["statut"] == "valide" : 
                    nbrePrelevementsValides += 1
        nbrePrelevements = len(listePrelevements)
        
        # V�rifie si le mandat a bien �t� utilis� depuis 36 mois
##        dateJour = datetime.date.today() 
##        dateDerniereUtilisation = dateMandat
##        for dictPrelevement in listePrelevements :
##            if dictPrelevement["date"] > dateDerniereUtilisation : 
##                dateDerniereUtilisation = dictPrelevement["date"]
##        dateMaxMandat = dateDerniereUtilisation + relativedelta.relativedelta(months=+36)
##        if dateJour > dateMaxMandat :
##            valide = ERREUR1
        
        # Si mandat ponctuel : recherche s'il a d�j� un pr�l�vement rattach�
        if typeMandat == "ponctuel" :
            if nbrePrelevementsValides > 0 :
                valide = ERREUR2
        
        # Si mandat ponctuel : recherche de la s�quence
        if typeMandat == "ponctuel" :
            prochaineSequence = "OOFF"
        
        # Si mandat r�current : recherche de la s�quence
        if typeMandat == "recurrent" :
            if nbrePrelevementsValides == 0 :
                prochaineSequence = "FRST"
            else :
                prochaineSequence = "RCUR"
        
        # Si la prochaine s�quence est sp�cifi�e dans le mandat (si non 'automatique') :
        if sequence != "auto" :
            prochaineSequence = sequence
            
        # Renvoie les r�sultats
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
        for index, codeTemp in self.dictDonnees.iteritems():
            if codeTemp == code :
                 self.SetSelection(index)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
            





            
if __name__ == '__main__':
    mandats = Mandats() 
    print mandats.AnalyseMandat(IDmandat=2)
    