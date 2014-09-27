#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import GestionDB
import datetime

from CTRL_Questionnaire import LISTE_CONTROLES


def DateEngEnDateDD(dateEng):
    if dateEng == None : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def FormateStr(valeur=u""):
    try :
        if valeur == None : return u""
        elif type(valeur) == int : return str(valeur)
        elif type(valeur) == float : return str(valeur)
        else : return valeur
    except : 
        return u""

def GetReponse(dictReponses={}, IDquestion=None, ID=None):
    if dictReponses.has_key(IDquestion) :
        if dictReponses[IDquestion].has_key(ID) :
            return dictReponses[IDquestion][ID]
    return u""


class Questionnaires():
    def __init__(self):
        self.dictControles = self.GetControles() 
        self.InitDonnees()
    
    def InitDonnees(self):
        self.dictChoix = self.GetChoix()
    
    def GetControles(self):
        dictControles = {}
        for dictControle in LISTE_CONTROLES :
            dictControles[dictControle["code"]] = dictControle
        return dictControles
    
    def GetChoix(self):
        DB = GestionDB.DB()
        req = """SELECT IDchoix, IDquestion, label
        FROM questionnaire_choix;"""
        DB.ExecuterReq(req)
        listeChoix = DB.ResultatReq()
        dictChoix = {}
        for IDchoix, IDquestion, label in listeChoix :
            dictChoix[IDchoix] = label
        DB.Close() 
        return dictChoix
    
    def GetFiltre(self, controle=""):
        filtre = self.dictControles[controle]["filtre"]
        return filtre

    def FormatageReponse(self, reponse="", controle=""):
        filtre = self.GetFiltre(controle)
        texteReponse = u""
        if filtre == "texte" : texteReponse = reponse
        if filtre == "entier" : texteReponse = reponse
        if filtre == "montant" : texteReponse = float(reponse)#decimal.Decimal(reponse)
        if filtre == "choix" :
            if reponse != None :
                listeTemp = reponse.split(";")
                listeTemp2 = []
                for IDchoix in listeTemp :
                    try :
                        IDchoix = int(IDchoix)
                        if self.dictChoix.has_key(IDchoix) :
                            listeTemp2.append(self.dictChoix[IDchoix])
                    except :
                        pass
                texteReponse = ", ".join(listeTemp2)
        if filtre == "coche" : 
            if reponse == 1 : 
                texteReponse = u"Oui"
            else :
                texteReponse = u"Non"
        if filtre == "date" : texteReponse = DateEngEnDateDD(reponse)
        return texteReponse


    def GetQuestions(self, type="individu"):
        """ Type = None (tout) ou 'individu' ou 'famille' """
        if type == None :
            condition = ""
        else :
            condition = "WHERE questionnaire_categories.type = '%s'" % type
        # Importation des questions
        DB = GestionDB.DB()
        req = """SELECT IDquestion, questionnaire_questions.label, type, controle, defaut
        FROM questionnaire_questions
        LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
        %s
        ORDER BY questionnaire_questions.ordre
        ;""" % condition
        DB.ExecuterReq(req)
        listeQuestions = DB.ResultatReq()
        DB.Close()
        listeResultats = []
        for IDquestion, label, type, controle, defaut in listeQuestions :
            if self.GetFiltre(controle) != None :
                listeResultats.append({"IDquestion":IDquestion, "label":label, "type":type, "controle":controle, "defaut":defaut})
            
        return listeResultats


    def GetReponses(self, type="individu"):
        """ Récupération des réponses des questionnaires """
        # Importation des questions
        DB = GestionDB.DB()        
        req = """SELECT IDreponse, questionnaire_reponses.IDquestion, IDindividu, IDfamille, reponse, controle
        FROM questionnaire_reponses
        LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_reponses.IDquestion
        LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
        WHERE questionnaire_categories.type='%s'
        ;""" % type
        DB.ExecuterReq(req)
        listeReponses = DB.ResultatReq()
        DB.Close() 
        
        dictReponses = {}
        for IDreponse, IDquestion, IDindividu, IDfamille, reponse, controle in listeReponses :
            filtre = self.GetFiltre(controle)
            if filtre != None :
                
                # Formatage de la réponse
                if reponse == None :
                    texteReponse = u""
                else :
                    texteReponse = self.FormatageReponse(reponse, controle)

                # Mémorisation
                if IDindividu != None :
                    ID = IDindividu
                else :
                    ID = IDfamille
                if dictReponses.has_key(IDquestion) == False :
                    dictReponses[IDquestion] = {}
                if dictReponses[IDquestion].has_key(ID) == False :
                    dictReponses[IDquestion][ID] = texteReponse
            
        return dictReponses

    def GetReponse(self, IDquestion=None, IDfamille=None, IDindividu=None):
        DB = GestionDB.DB()        
        req = """SELECT IDreponse, IDindividu, IDfamille, reponse, controle
        FROM questionnaire_reponses
        LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_reponses.IDquestion
        WHERE questionnaire_reponses.IDquestion=%d AND (IDindividu=%d OR IDfamille=%d)
        ;""" % (IDquestion, IDindividu, IDfamille)
        DB.ExecuterReq(req)
        listeReponses = DB.ResultatReq()
        DB.Close() 
        if len(listeReponses) == 0 :
            return None
        dictReponses = {}
        IDreponse, IDindividu, IDfamille, reponse, controle = listeReponses[0]
        filtre = self.GetFiltre(controle)
        texteReponse = None
        if filtre != None :
            # Formatage de la réponse
            if reponse == None :
                texteReponse = u""
            else :
                texteReponse = self.FormatageReponse(reponse, controle)
        return texteReponse
        

class ChampsEtReponses():
    """ Retourne une donnée de type "{QUESTION_24}" = valeur """
    def __init__(self, type="individu"):
        Q = Questionnaires()
        self.listeQuestions = Q.GetQuestions(type=type)
        self.dictReponses = Q.GetReponses(type=type)

    def GetDonnees(self, ID):
        listeDonnees = []
        for dictQuestion in self.listeQuestions :
            reponse = FormateStr(GetReponse(self.dictReponses, dictQuestion["IDquestion"], ID))
            champ = "{QUESTION_%d}" % dictQuestion["IDquestion"]
            dictReponse = {
                "champ":champ, "reponse":reponse, "IDquestion":dictQuestion["IDquestion"], "label":dictQuestion["label"], 
                "type":dictQuestion["type"], "controle":dictQuestion["controle"], "defaut":dictQuestion["defaut"]
                }
            listeDonnees.append(dictReponse)
        return listeDonnees





if __name__ == '__main__':
    pass
    
    