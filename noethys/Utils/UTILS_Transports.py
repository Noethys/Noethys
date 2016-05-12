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
from UTILS_Traduction import _
import GestionDB


class AnalyseLocalisation():
    """ Renvoie les noms des lieux de départ et d'arrivée """
    def __init__(self):
        self.MAJ()
    
    
    def MAJ(self):
        """ Récupère les données dans la base """
        DB = GestionDB.DB()
        
        # Arrêts
        req = """SELECT IDarret, nom FROM transports_arrets;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dict_arrets = {}
        for IDarret, nom in listeDonnees :
            self.dict_arrets[IDarret] = nom
            
        # Lieux
        req = """SELECT IDlieu, nom FROM transports_lieux;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dict_lieux = {}
        for IDlieu, nom in listeDonnees :
            self.dict_lieux[IDlieu] = nom
        
        # Activités
        req = """SELECT IDactivite, nom FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dict_activites = {}
        for IDactivite, nom in listeDonnees :
            self.dict_activites[IDactivite] = nom

        # Ecoles
        req = """SELECT IDecole, nom FROM ecoles;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dict_ecoles = {}
        for IDecole, nom in listeDonnees :
            self.dict_ecoles[IDecole] = nom

        DB.Close()
    
    def Analyse(self, IDarret=None, IDlieu=None, localisation=None):
        # Analyse du départ ou de l'arrivée
        nom = u""
        if IDarret != None and self.dict_arrets.has_key(IDarret) :
            nom = self.dict_arrets[IDarret]
        if IDlieu != None and self.dict_lieux.has_key(IDlieu) :
            nom = self.dict_lieux[IDlieu]
        if localisation != None :
            nom = self.Localisation(localisation)
        return nom
        
    def Localisation(self, texte=""):
        # Analyse des localisations
        code = texte.split(";")[0]
        if code == "DOMI" :
            return _(u"Domicile")
        if code == "ECOL" :
            IDecole = int(texte.split(";")[1])
            if self.dict_ecoles.has_key(IDecole):
                return self.dict_ecoles[IDecole]
        if code == "ACTI" :
            IDactivite = int(texte.split(";")[1])
            if self.dict_activites.has_key(IDactivite):
                return self.dict_activites[IDactivite]
        if code == "AUTR" :
            code, nom, rue, cp, ville = texte.split(";")
            return u"%s %s %s %s" % (nom, rue, cp, ville)
        return u""

            
if __name__ == '__main__':
    pass
    