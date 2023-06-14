#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB




class JoursSpeciaux() :
    def __init__(self):
        # Définit les couleurs
        self.couleur_feries = wx.Colour(180, 180, 180)
        self.couleur_vacances = wx.Colour(255, 255, 187)
        
        # Récupère les données dans la base
        self.listeVacances = self.Importation_Vacances() 
        self.listeFeriesFixes, self.listeFeriesVariables = self.Importation_Feries() 
        
        
    def Importation_Vacances(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM vacances ORDER BY date_debut;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        listeVacances = []
        for id, nom, annee, date_debut, date_fin in listeDonnees :
            datedebut = datetime.date(int(date_debut[:4]), int(date_debut[5:7]), int(date_debut[8:10]))
            datefin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            listeVacances.append(datedebut)
            listeTemp = []
            for x in range((datefin-datedebut).days) :
                datedebut = datedebut + datetime.timedelta(days=1)        
                listeVacances.append(datedebut)

        return listeVacances
    
    def Importation_Feries(self):
        """ Importation des dates des jours fériés """
        req = "SELECT * FROM jours_feries;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        
        listeFeriesFixes = []
        listeFeriesVariables = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = (jour, mois)
                listeFeriesFixes.append(date)
            else:
                date = datetime.date(annee, mois, jour)
                listeFeriesVariables.append(date)
        return listeFeriesFixes, listeFeriesVariables

    def RechercheJourFerie(self, date=None):
        """ Recherche si une date est un jour férié """
        if (date.day, date.month) in self.listeFeriesFixes :
            return True
        else:
            if date in self.listeFeriesVariables :
                return True
        return False
    
    def RechercheJourVacances(self, date=None):
        """ Recherche si une date est un jour de vacances """
        if date in self.listeVacances :
            return True
        else :
            return False
        
    def GetCouleur(self, date=None):
        """ Renvoie la couleur """
        if self.RechercheJourFerie(date) :
            return self.couleur_feries
        if self.RechercheJourVacances(date) :
            return self.couleur_vacances
        return None
        
    

if __name__ == '__main__':
    joursSpeciaux = JoursSpeciaux() 
    
    
    