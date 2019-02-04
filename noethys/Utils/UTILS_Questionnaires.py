#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import GestionDB
import datetime
from Utils import UTILS_Dates
from Ctrl.CTRL_Questionnaire import LISTE_CONTROLES
from Ctrl.CTRL_ObjectListView import ColumnDefn



def DateEngEnDateDD(date):
    if date in (None, "") : return None
    if type(date) == datetime.date :
        return UTILS_Dates.DateDDEnFr(date)
    return datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))

def FormateStr(valeur=u""):
    try :
        if valeur == None : return u""
        elif type(valeur) == int : return str(valeur)
        elif type(valeur) == float : return str(valeur)
        else : return valeur
    except : 
        return u""

def GetReponse(dictReponses={}, IDquestion=None, ID=None):
    if IDquestion in dictReponses :
        if ID in dictReponses[IDquestion] :
            return dictReponses[IDquestion][ID]
    return u""

def FormateDate(date):
    if date in (None, "") : return ""
    if type(date) == datetime.date :
        return UTILS_Dates.DateDDEnFr(date)
    return datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))

def GetColonnesForOL(liste_questions=[]):
    """ Ajout des questions des questionnaires aux colonnes d'un OL """
    liste_colonnes = []
    for dictQuestion in liste_questions:
        Formatter = None
        filtre = dictQuestion["filtre"]
        if filtre == "texte":
            typeDonnee = "texte"
        elif filtre == "entier":
            typeDonnee = "entier"
        elif filtre == "montant":
            typeDonnee = "montant"
        elif filtre == "choix":
            typeDonnee = "texte"
        elif filtre == "coche":
            typeDonnee = "texte"
        elif filtre == "date":
            typeDonnee = "date"
            Formatter = FormateDate
        else:
            typeDonnee = "texte"
        liste_colonnes.append(ColumnDefn(dictQuestion["label"], "left", 150, "question_%d" % dictQuestion["IDquestion"], stringConverter=Formatter, typeDonnee=typeDonnee))
    return liste_colonnes




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
        if filtre == "entier" : texteReponse = int(reponse)
        if filtre == "montant" : texteReponse = float(reponse)#decimal.Decimal(reponse)
        if filtre == "choix" :
            if reponse != None :
                listeTemp = reponse.split(";")
                listeTemp2 = []
                for IDchoix in listeTemp :
                    try :
                        IDchoix = int(IDchoix)
                        if IDchoix in self.dictChoix :
                            listeTemp2.append(self.dictChoix[IDchoix])
                    except :
                        pass
                texteReponse = ", ".join(listeTemp2)
        if filtre == "coche" : 
            if reponse == 1 : 
                texteReponse = _(u"Oui")
            else :
                texteReponse = _(u"Non")
        if filtre == "date" : texteReponse = DateEngEnDateDD(reponse)
        return texteReponse


    def GetQuestions(self, type="individu", avec_filtre=True):
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
            if avec_filtre == False or self.GetFiltre(controle) != None :
                listeResultats.append({"IDquestion":IDquestion, "label":label, "type":type, "controle":controle, "defaut":defaut, "filtre":self.GetFiltre(controle)})
        return listeResultats


    def GetReponses(self, type="individu"):
        """ Récupération des réponses des questionnaires """
        # Importation des questions
        DB = GestionDB.DB()        
        req = """SELECT IDreponse, questionnaire_reponses.IDquestion, IDindividu, IDfamille, reponse, 
        questionnaire_reponses.type, questionnaire_reponses.IDdonnee, controle
        FROM questionnaire_reponses
        LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_reponses.IDquestion
        LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
        WHERE questionnaire_categories.type='%s'
        ;""" % type
        DB.ExecuterReq(req)
        listeReponses = DB.ResultatReq()
        DB.Close() 
        
        dictReponses = {}
        for IDreponse, IDquestion, IDindividu, IDfamille, reponse, typeDonnee, IDdonnee, controle in listeReponses :
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
                elif IDfamille != None :
                    ID = IDfamille
                else :
                    ID = IDdonnee
                if (IDquestion in dictReponses) == False :
                    dictReponses[IDquestion] = {}
                if (ID in dictReponses[IDquestion]) == False :
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

    def GetDonnees(self, ID, formatStr=True):
        listeDonnees = []
        for dictQuestion in self.listeQuestions :
            reponse = GetReponse(self.dictReponses, dictQuestion["IDquestion"], ID)
            if formatStr == True :
                reponse = FormateStr(reponse)
            champ = "{QUESTION_%d}" % dictQuestion["IDquestion"]
            dictReponse = {
                "champ":champ, "reponse":reponse, "IDquestion":dictQuestion["IDquestion"], "label":dictQuestion["label"], 
                "type":dictQuestion["type"], "controle":dictQuestion["controle"], "defaut":dictQuestion["defaut"]
                }
            listeDonnees.append(dictReponse)
        return listeDonnees





if __name__ == '__main__':
    pass
    
    