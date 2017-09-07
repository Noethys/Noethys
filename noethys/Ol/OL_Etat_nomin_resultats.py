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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import time
import decimal
import GestionDB


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Ctrl.CTRL_Questionnaire import LISTE_CONTROLES

from Utils import UTILS_Titulaires
from Data import DATA_Civilites as Civilites


def ArrondirHeureSup(heures, minutes, pas): 
    """ Arrondi l'heure au pas supérieur """
    for x in range(0, 60, pas):
        if x >= minutes :
            return (heures, x)
    return (heures+1, 0)

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    if textDate == None or textDate == "" : return ""
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def FormateValeur(valeur, mode="decimal"):
    if mode == "decimal" :
        return valeur
    if mode == "heure" :
        hr, dec = str(valeur).split(".")
        if len(dec) == 1 : 
            mn = int(dec) * 0.1
        else:
            mn = int(dec) * 0.01
        mn = mn * 60 #int(dec)*60/100.0
        mn = math.ceil(mn)
        return u"%sh%02d" % (hr, mn)

def DeltaEnStr(varTimedelta) :
    """ Transforme une variable TIMEDELTA en heure datetime.time """
    # Si sup à une journée :
    if varTimedelta.total_seconds() >= 86400 :
        hours, remainder = divmod(varTimedelta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return "%02d:%02d" % (hours, minutes)
    else :
        heure = time.strftime("%H:%M", time.gmtime(varTimedelta.seconds))
    return heure



DICT_INDIVIDUS = {}
DICT_TITULAIRES = {}
DICT_FAMILLES = {}
DICT_QUESTIONNAIRES = {}


def GetDictIndividus():
    """ Récupération des infos sur les individus """
    # Récupération des adresses
    DB = GestionDB.DB()
    req = """SELECT IDindividu, individus.nom, prenom, rue_resid, cp_resid, ville_resid, secteurs.nom 
    FROM individus
    LEFT JOIN secteurs ON secteurs.IDsecteur = individus.IDsecteur
    ;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictAdresses = {}
    for IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid, secteur in listeDonnees :
        if secteur == None : secteur = ""
        dictAdresses[IDindividu] = { "nom" : nom, "prenom" : prenom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid, "secteur" : secteur}
    
    # Récupération des individus
    listeChamps = (
        "IDindividu", "IDcivilite", "nom", "prenom", "num_secu","IDnationalite", 
        "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
        "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
        "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
        "tel_domicile", "tel_mobile", "tel_fax", "mail"
        )
    req = """
    SELECT %s FROM individus;""" % ",".join(listeChamps)
    DB.ExecuterReq(req)
    listeIndividus= DB.ResultatReq()
    DB.Close() 
    
    # Récupération des civilités
    dictCivilites = Civilites.GetDictCivilites()
        
    dictResultats = {}
    for valeurs in listeIndividus :
        dictTemp = {}
        
        IDindividu = valeurs[0]
        dictTemp["IDindividu"] = IDindividu
        
        # Infos de la table Individus
        for index in range(0, len(listeChamps)) :
            nomChamp = listeChamps[index]
            dictTemp[nomChamp] = valeurs[index]
            
        # Infos sur la civilité
        dictTemp["genre"] = dictCivilites[dictTemp["IDcivilite"]]["sexe"]
        dictTemp["categorieCivilite"] = dictCivilites[dictTemp["IDcivilite"]]["categorie"]
        dictTemp["civiliteLong"]  = dictCivilites[dictTemp["IDcivilite"]]["civiliteLong"]
        dictTemp["civiliteAbrege"] = dictCivilites[dictTemp["IDcivilite"]]["civiliteAbrege"] 
        dictTemp["nomImage"] = dictCivilites[dictTemp["IDcivilite"]]["nomImage"] 
        
        # Age
        if dictTemp["date_naiss"] == None :
            dictTemp["age"] = None
        else:
            datenaissDD = datetime.date(year=int(dictTemp["date_naiss"][:4]), month=int(dictTemp["date_naiss"][5:7]), day=int(dictTemp["date_naiss"][8:10]))
            datedujour = datetime.date.today()
            age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
            dictTemp["date_naiss"] = datenaissDD
            dictTemp["age"] = age

        # Secteur
        dictTemp["secteur"] = dictAdresses[IDindividu]["secteur"]

        # Adresse auto ou manuelle
        if dictTemp["adresse_auto"] != None and dictAdresses.has_key(dictTemp["adresse_auto"]) :
            dictTemp["rue_resid"] = dictAdresses[dictTemp["adresse_auto"]]["rue_resid"]
            dictTemp["cp_resid"] = dictAdresses[dictTemp["adresse_auto"]]["cp_resid"]
            dictTemp["ville_resid"] = dictAdresses[dictTemp["adresse_auto"]]["ville_resid"]
            dictTemp["secteur"] = dictAdresses[dictTemp["adresse_auto"]]["secteur"]
        
        
        dictResultats[dictTemp["IDindividu"]] = dictTemp
        
    return dictResultats


def GetQuestionnaires():
    """ Récupération des questions des questionnaires """
    # Importation des questions
    dictControles = {}
    for dictControle in LISTE_CONTROLES :
        dictControles[dictControle["code"]] = dictControle

    DB = GestionDB.DB()
    
    req = """SELECT IDchoix, IDquestion, label
    FROM questionnaire_choix;"""
    DB.ExecuterReq(req)
    listeChoix = DB.ResultatReq()
    dictChoix = {}
    for IDchoix, IDquestion, label in listeChoix :
        dictChoix[IDchoix] = label
    
    req = """SELECT IDreponse, questionnaire_reponses.IDquestion, IDindividu, IDfamille, reponse, controle
    FROM questionnaire_reponses
    LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_reponses.IDquestion
    ;"""
    DB.ExecuterReq(req)
    listeReponses = DB.ResultatReq()
    DB.Close() 
    
    dictReponses = {}
    for IDreponse, IDquestion, IDindividu, IDfamille, reponse, controle in listeReponses :
        if controle != None :
            filtre = dictControles[controle]["filtre"]
            if filtre != None :
                
                if reponse == None :
                    texteReponse = u""
                    
                else :
                    # Formatage de la réponse
                    texteReponse = u""
                    if filtre == "texte" : texteReponse = reponse
                    if filtre == "entier" : texteReponse = reponse
                    if filtre == "montant" : texteReponse = float(reponse)#decimal.Decimal(reponse)
                    if filtre == "choix" :
                        listeTemp = reponse.split(";")
                        listeTemp2 = []
                        for IDchoix in listeTemp :
                            try :
                                if dictChoix.has_key(int(IDchoix)) :
                                    listeTemp2.append(dictChoix[int(IDchoix)])
                            except :
                                pass
                        texteReponse = ", ".join(listeTemp2)
                    if filtre == "coche" : 
                        if reponse == "1" : 
                            texteReponse = _(u"Oui")
                        else :
                            texteReponse = _(u"Non")
                    if filtre == "date" : texteReponse = DateEngEnDateDD(reponse)

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

def GetReponse(IDquestion=None, ID=None):
    if DICT_QUESTIONNAIRES.has_key(IDquestion) :
        if DICT_QUESTIONNAIRES[IDquestion].has_key(ID) :
            return DICT_QUESTIONNAIRES[IDquestion][ID]
    return u""





class Track(object):
    def __init__(self, IDindividu=None, IDfamille=None, listeConso=[], listeChamps=[]):
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.listeConso = listeConso
        self.listeChamps = listeChamps
        self.listeErreurs = [] 
        
        # Infos sur l'individu
        self.INDIVIDU_ID = IDindividu
        self.INDIVIDU_GENRE = DICT_INDIVIDUS[IDindividu]["genre"]
        self.INDIVIDU_CIVILITE_LONG = DICT_INDIVIDUS[IDindividu]["civiliteLong"]
        self.INDIVIDU_CIVILITE_COURT = DICT_INDIVIDUS[IDindividu]["civiliteAbrege"]
        self.INDIVIDU_NOM = DICT_INDIVIDUS[IDindividu]["nom"]
        self.INDIVIDU_PRENOM = DICT_INDIVIDUS[IDindividu]["prenom"]
        self.INDIVIDU_NOM_COMPLET = u"%s %s" % (self.INDIVIDU_NOM, self.INDIVIDU_PRENOM)
        self.INDIVIDU_DATE_NAISS = DICT_INDIVIDUS[IDindividu]["date_naiss"]
        self.INDIVIDU_AGE = DICT_INDIVIDUS[IDindividu]["age"]
        self.INDIVIDU_NUM_SECU = DICT_INDIVIDUS[IDindividu]["num_secu"]
        self.INDIVIDU_RUE = DICT_INDIVIDUS[IDindividu]["rue_resid"]
        self.INDIVIDU_CP = DICT_INDIVIDUS[IDindividu]["cp_resid"]
        self.INDIVIDU_VILLE = DICT_INDIVIDUS[IDindividu]["ville_resid"]
        self.INDIVIDU_SECTEUR = DICT_INDIVIDUS[IDindividu]["secteur"]
        self.INDIVIDU_NOM = DICT_INDIVIDUS[IDindividu]["nom"]
        
        # Infos sur la famille
        self.FAMILLE_ID = IDfamille
        self.FAMILLE_TITULAIRES = DICT_TITULAIRES[IDfamille]["titulairesSansCivilite"]
        self.FAMILLE_RUE = DICT_TITULAIRES[IDfamille]["adresse"]["rue"]
        self.FAMILLE_CP = DICT_TITULAIRES[IDfamille]["adresse"]["cp"]
        self.FAMILLE_VILLE = DICT_TITULAIRES[IDfamille]["adresse"]["ville"]
        self.FAMILLE_SECTEUR = DICT_TITULAIRES[IDfamille]["adresse"]["secteur"]
        self.FAMILLE_CAISSE = DICT_FAMILLES[IDfamille]["nomCaisse"]
        self.FAMILLE_NUM_ALLOCATAIRE = DICT_FAMILLES[IDfamille]["num_allocataire"]
        self.FAMILLE_ALLOCATAIRE = DICT_FAMILLES[IDfamille]["nomAllocataire"]
        self.FAMILLE_QF = DICT_FAMILLES[IDfamille]["qf"]

        # Questionnaires
        for champ in listeChamps :
            if champ.type == "QUESTION" :
                IDquestion = int(champ.code[len(champ.type):])
                if champ.categorie == "Individu" : IDtemp = "IDindividu"
                if champ.categorie == "Famille" : IDtemp = "IDfamille"
                exec(u"self.%s = GetReponse(IDquestion, %s)" % (champ.code, IDtemp))
        
        # Regroupement des conso par UNITE puis PERIODE
        dictConso = {}
        for dictTemp in listeConso :
            IDunite = dictTemp["IDunite"]
            quantite = dictTemp["quantite"]
            if dictConso.has_key(IDunite) == False :
                dictConso[IDunite] = {
                    "NBRE_UNITE":0, "NBRE_HV_UNITE":0, "NBRE_PV_UNITE":0, "NBRE_GV_UNITE":0,
                    "TEMPS_UNITE":datetime.timedelta(hours=0, minutes=0), "TEMPS_HV_UNITE":datetime.timedelta(hours=0, minutes=0), "TEMPS_PV_UNITE":datetime.timedelta(hours=0, minutes=0), "TEMPS_GV_UNITE":datetime.timedelta(hours=0, minutes=0),
                    }
                    
            # Nbre
            dictConso[IDunite]["NBRE_UNITE"] += quantite
            if dictTemp["periode"] == "HV" : dictConso[IDunite]["NBRE_HV_UNITE"] += quantite
            if dictTemp["periode"] == "PV" : dictConso[IDunite]["NBRE_PV_UNITE"] += quantite
            if dictTemp["periode"] == "GV" : dictConso[IDunite]["NBRE_GV_UNITE"] += quantite
            
            # Temps
            dictConso[IDunite]["TEMPS_UNITE"] += dictTemp["temps"]
            if dictTemp["periode"] == "HV" : dictConso[IDunite]["TEMPS_HV_UNITE"] += dictTemp["temps"]
            if dictTemp["periode"] == "PV" : dictConso[IDunite]["TEMPS_PV_UNITE"] += dictTemp["temps"]
            if dictTemp["periode"] == "GV" : dictConso[IDunite]["TEMPS_GV_UNITE"] += dictTemp["temps"]
            
        # Unités
        for prefixe in ("NBRE", "TEMPS") :
            for champ in listeChamps :
                if champ.type == "%s_UNITE" % prefixe :
                    for categorie in ("%s_UNITE" % prefixe, "%s_HV_UNITE" % prefixe, "%s_PV_UNITE" % prefixe, "%s_GV_UNITE" % prefixe) :
                        if champ.code.startswith(categorie):
                            IDunite = int(champ.code[len(categorie):])
                            if dictConso.has_key(IDunite) :
                                valeur = dictConso[IDunite][categorie]
                            else :
                                if prefixe == "NBRE" : valeur = 0
                                if prefixe == "TEMPS" : valeur = datetime.timedelta(hours=0, minutes=0)
                            exec(u"self.%s = valeur" % champ.code)
                
        # Champs PERSONNALISES
        listeChampsAbsents = []
        for champ in listeChamps :
            if champ.type == "PERSO" :
                etat = self.CalcChampPerso(champ)
                
                # Si un des champs de la formule est absent
                if "has no attribute" in str(etat) :
                    listeChampsAbsents.append(champ)

        # Recalcule les champs absents
        for x in range(0, 10):
            for champ in listeChampsAbsents :
                etat = self.CalcChampPerso(champ)
                if etat == "ok" : 
                    break
        
        # AIDES CAISSES
##        for champ in listeChamps :
##            if champ.type == "AIDE_CAISSE" :
##                IDcaisse = int(champ.code[len(champ.type):])
##                
##                try :
##                    exec("""self.%s = %s""" % (champ.code, formule))
##                except :
##                    exec("self.%s = None" % champ.code)
                
        
    def CalcChampPerso(self, champ):
        def SI(condition, sivrai=None, sifaux=None):
            if condition :
                return sivrai
            else :
                return sifaux
        
        formule = champ.formule
        formule = formule.replace("{", "self.")
        formule = formule.replace("}", "")
        
        try :
            exec("""self.%s = %s""" % (champ.code, formule))
            return "ok"
        except Exception, err :
            if champ.code != "" :
                exec("self.%s = None" % champ.code)
                self.listeErreurs.append("Probleme dans le champ %s : %s" % (champ.code, err))
                return err


# ----------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.dictParametres = kwds.pop("dictParametres", {})
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        self.SetMinSize((20, 20))
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.donnees = self.GetTracks()
        
    def GetTracks(self):
        """ Création des lignes """
        DB = GestionDB.DB()

        # Récupération de tous les individus
        global DICT_INDIVIDUS
        DICT_INDIVIDUS = GetDictIndividus()
    
        # Récupération des titulaires
        global DICT_TITULAIRES
        DICT_TITULAIRES = UTILS_Titulaires.GetTitulaires()
        
        # Récupération des questionnaires
        global DICT_QUESTIONNAIRES
        DICT_QUESTIONNAIRES = GetQuestionnaires()
        
        # Récupération des QF
        req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient
        FROM quotients
        ORDER BY date_debut
        ;"""
        DB.ExecuterReq(req)
        listeQuotients = DB.ResultatReq()     
        dictQuotients = {}
        for IDquotient, IDfamille, date_debut, date_fin, quotient in listeQuotients :
            if dictQuotients.has_key(IDfamille) == False :
                dictQuotients[IDfamille] = []
            dictQuotients[IDfamille].append({"IDquotient":IDquotient, "date_debut":DateEngEnDateDD(date_debut), "date_fin":DateEngEnDateDD(date_fin), "quotient":quotient})

        # Récupération des déductions
##        req = """SELECT IDdeduction, IDprestation, date, montant, label, IDaide
##        FROM deductions
##        WHERE date>='%s' AND date <='%s'
##        ;""" % (self.dictParametres["date_debut"], self.dictParametres["date_fin"])
##        DB.ExecuterReq(req)
##        listeDeductions = DB.ResultatReq()     
##        dictDeductions = {}
##        for IDdeduction, IDprestation, date, montant, label, IDaide in listeDeductions :
##            if dictDeductions.has_key(IDprestation) == False :
##                dictDeductions[IDprestation] = []
##            dictDeductions[IDprestation].append({"IDdeduction":IDdeduction, "IDprestation":IDprestation, "date":date, "montant":montant, "label":label, "IDaide":IDaide})

        # Récupération des familles
        req = """SELECT IDfamille, familles.IDcaisse, caisses.nom, num_allocataire, allocataire
        FROM familles
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        ;"""
        DB.ExecuterReq(req)
        listeFamilles = DB.ResultatReq()     
        global DICT_FAMILLES
        for IDfamille, IDcaisse, nomCaisse, num_allocataire, allocataire in listeFamilles :
            
            # Nom allocataire
            if allocataire != None and DICT_INDIVIDUS.has_key(allocataire) :
                nomAllocataire = u"%s %s" % (DICT_INDIVIDUS[allocataire]["nom"], DICT_INDIVIDUS[allocataire]["prenom"])
            else :
                nomAllocataire = None
            
            # Recherche des QF
            qf = None
            if dictQuotients.has_key(IDfamille) :
                listeQuotients = dictQuotients[IDfamille]
                for dictQF in listeQuotients :
                    if dictQF["date_debut"] <= self.dictParametres["date_fin"] and dictQF["date_fin"] >= self.dictParametres["date_debut"] :
                        qf = dictQF["quotient"]
            else :
                listeQuotients = []
                        
            # Mémorisation
            DICT_FAMILLES[IDfamille] = {"IDfamille":IDfamille, "IDcaisse":IDcaisse, "nomCaisse":nomCaisse, "num_allocataire":num_allocataire, "nomAllocataire":nomAllocataire, "listeQuotients":listeQuotients, "qf":qf}

        # Récupération des périodes de vacances
        req = """SELECT IDvacance, nom, annee, date_debut, date_fin
        FROM vacances
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        listeVacances = []
        for IDvacance, nom, annee, date_debut_Tmp, date_fin_Tmp in listeDonnees :
            date_debut_Tmp = DateEngEnDateDD(date_debut_Tmp)
            date_fin_Tmp = DateEngEnDateDD(date_fin_Tmp)
            if date_debut_Tmp.month in (6, 7, 8, 9) or date_fin_Tmp.month in (6, 7, 8, 9) :
                grandesVacs = True
            else:
                grandesVacs = False
            listeVacances.append( {"date_debut" : date_debut_Tmp, "date_fin" : date_fin_Tmp, "grandesVacs" : grandesVacs} )

        # Création des conditions
        if len(self.dictParametres["caisses"]) == 0 : conditionCaisses = "AND familles.IDcaisse IN ()"
        elif len(self.dictParametres["caisses"]) == 1 : conditionCaisses = "AND familles.IDcaisse IN (%d)" % self.dictParametres["caisses"][0]
        else : conditionCaisses = "AND familles.IDcaisse IN %s" % str(tuple(self.dictParametres["caisses"]))
        
        if 0 in self.dictParametres["caisses"] :
            conditionCaisses = "AND (%s OR familles.IDcaisse IS NULL)" % conditionCaisses[4:]
            
        if len(self.dictParametres["groupes"]) == 0 : conditionGroupes = "AND consommations.IDgroupe IN ()"
        elif len(self.dictParametres["groupes"]) == 1 : conditionGroupes = "AND consommations.IDgroupe IN (%d)" % self.dictParametres["groupes"][0]
        else : conditionGroupes = "AND consommations.IDgroupe IN %s" % str(tuple(self.dictParametres["groupes"]))

        if len(self.dictParametres["categories"]) == 0 : conditionCategories = "AND consommations.IDcategorie_tarif IN ()"
        elif len(self.dictParametres["categories"]) == 1 : conditionCategories = "AND consommations.IDcategorie_tarif IN (%d)" % self.dictParametres["categories"][0]
        else : conditionCategories = "AND consommations.IDcategorie_tarif IN %s" % str(tuple(self.dictParametres["categories"]))

        # Récupération des consommations
        req = """SELECT 
        consommations.IDconso, consommations.IDindividu, consommations.IDactivite, 
        consommations.date, consommations.IDunite, consommations.IDgroupe,
        consommations.heure_debut, consommations.heure_fin, consommations.etat,
        consommations.IDcategorie_tarif, consommations.IDprestation, consommations.quantite,
        prestations.montant_initial, prestations.montant, prestations.temps_facture,
        comptes_payeurs.IDfamille, familles.IDcaisse, familles.num_allocataire, familles.allocataire,
        individus.date_naiss
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        WHERE consommations.date >='%s' AND consommations.date <='%s'
        AND etat NOT IN ('attente', 'refus')
        %s %s %s
        ;""" % (self.dictParametres["date_debut"], self.dictParametres["date_fin"], conditionCaisses, conditionGroupes, conditionCategories)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        
        listeFamillesSansQF = []
        dictResultats = {}
        for IDconso, IDindividu, IDactivite, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, IDcategorie_tarif, IDprestation, quantite, montantInitial, montant, temps_facture, IDfamille, IDcaisse, numAllocataire, allocataire, date_naiss in listeDonnees :
            date = DateEngEnDateDD(date)
            if date_naiss != None : 
                date_naiss = DateEngEnDateDD(date_naiss)
                age = (date.year - date_naiss.year) - int((date.month, date.day) < (date_naiss.month, date_naiss.day))
            else :
                age = None
            
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
        
            # Calcul de la durée
            if heure_debut != None and heure_fin != None :
                temps = (datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute) - datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)) * quantite
            else:
                temps = datetime.timedelta(seconds=0)
                
            # Recherche la période
            periode = None
            for dictVac in listeVacances :
                if date >= dictVac["date_debut"] and date <= dictVac["date_fin"] :
                    if dictVac["grandesVacs"] == True :
                        periode = "GV"
                    else:
                        periode = "PV"
            if periode == None :
                # C'est hors vacances :
                periode = "HV"
            
            # Recherche des déductions
##            if dictDeductions.has_key(IDprestation) :
##                deductions = dictDeductions[IDprestation]
##            else :
##                deductions = []
            
            # Vérifie que cette consommation répond bien aux paramètres conditionnels
            valide = True
            
            if self.dictParametres["age"] != None :
                paramAge = self.dictParametres["age"]
                if paramAge[0] == "AGES" :
                    ageMin, ageMax = paramAge[1], paramAge[2]
                    if age < ageMin or age > ageMax :
                        valide = False
                if paramAge[0] == "DATES" :
                    dateNaissMin, dateNaissMax = paramAge[1], paramAge[2]
                    if date_naiss == None :
                        date_naiss = ""
                    if str(date_naiss) < str(dateNaissMin) or str(date_naiss) > str(dateNaissMax) :
                        valide = False
            
            if self.dictParametres["qf"] != None :
                QFfamille = DICT_FAMILLES[IDfamille]["qf"]
                if self.dictParametres["qf"] == "SANS" :
                    if QFfamille != None :
                        valide = False
                else :
                    QFmin, QFmax = self.dictParametres["qf"]
                    if QFfamille == None and valide == True :
                        if IDfamille not in listeFamillesSansQF :
                            listeFamillesSansQF.append(IDfamille)
                    if QFfamille < QFmin or QFfamille > QFmax :
                        valide = False
            
            # Mémorisation de la consommation
            if valide == True :
                if dictResultats.has_key((IDindividu, IDfamille)) == False :
                    dictResultats[(IDindividu, IDfamille)] = []
                dictTemp = {"IDconso":IDconso, "IDactivite":IDactivite, "date":date, "IDunite":IDunite, "IDgroupe":IDgroupe, "heure_debut":heure_debut, 
                                "heure_fin":heure_fin, "etat":etat, "IDcategorie_tarif":IDcategorie_tarif, "IDprestation":IDprestation, "montantInitial":montantInitial, 
                                "montant":montant, "temps_facture":temps_facture, "IDfamille":IDfamille, "IDcaisse":IDcaisse, "numAllocataire":numAllocataire, 
                                "allocataire":allocataire, "IDindividu":IDindividu, "periode":periode, "temps":temps, "quantite":quantite,
                                }
                dictResultats[(IDindividu, IDfamille)].append(dictTemp)
                
        # Création des tracks
        listeListeView = []
        for (IDindividu, IDfamille), listeConso in dictResultats.iteritems() :
            listeListeView.append(Track(IDindividu, IDfamille, listeConso, self.dictParametres["champsDispo"]))

        # Avertissement au sujet des familles sans QF
        if len(listeFamillesSansQF) > 0 :
            dlg = wx.MessageDialog(self, _(u"Attention, veuillez noter que %d familles ne disposant de quotient familial sur la période sélectionnée ont été exclus des résultats !") % len(listeFamillesSansQF), _(u"Avertissement"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

        return listeListeView

    def InitObjectListView(self):           
        """ Init liste """
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormatageValeur(valeur):
            if valeur == None : return ""
            # Texte
            if isinstance(valeur, str) : 
                return valeur
            if isinstance(valeur, unicode) : 
                return valeur
            # Nombre
            if isinstance(valeur, int) : 
                if valeur == 0 : valeur = ""
                return str(valeur)
            if isinstance(valeur, float) : 
                if valeur == 0.0 : valeur = ""
                return str(valeur)
            # Heure
            if isinstance(valeur, datetime.timedelta) : 
                valeur = DeltaEnStr(valeur)
                if valeur == "00:00" : return ""
                return valeur
            # Date
            if isinstance(valeur, datetime.date) : 
                valeur = DateEngFr(str(valeur))
                return valeur
            # Autre
            return None
        
        def RechercheTypeDonnee(champ):
            """ Pour les filtres de liste """
            for track in self.donnees :
                try :
                    valeur = getattr(track, champ.code)
                except :
                    valeur = None
                # Entier
                if isinstance(valeur, int) : 
                    return "entier"
                # Date
                if isinstance(valeur, datetime.date) : 
                    return "date"
            # Autre
            return "texte"
            
            
        # Création des colonnes
        liste_Colonnes = [ColumnDefn("", "left", 0, "IDindividu", typeDonnee="entier"), ]
        for champ in self.dictParametres["champs"] :
            if champ.type != None :
                liste_Colonnes.append(ColumnDefn(champ.titre, "left", champ.largeur, champ.code, typeDonnee=RechercheTypeDonnee(champ), stringConverter=FormatageValeur))
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune donnée"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
        
        self.AfficheTotaux()

    def AfficheTotaux(self):
        """ Affiche les totaux """
        # Récupère les labels de colonnes
        listeColonnes = []
        for colonne in self.columns :
            listeColonnes.append((colonne.title, colonne.align, colonne.width, colonne.valueGetter))
        
        # Récupère les valeurs
        dictValeurs = {}
        listeTracks = self.innerList # listview.GetFilteredObjects()
        for track in listeTracks :
            for indexCol in range(0, self.GetColumnCount() ) :
                codeChamp = listeColonnes[indexCol][3]
                labelChamp = listeColonnes[indexCol][0]
                valeur = self.GetValueAt(track, indexCol)

                # Entier
                if isinstance(valeur, int) : 
                    pass
                # Float
                elif isinstance(valeur, float) : 
                    pass
                # Heure
                elif isinstance(valeur, datetime.timedelta) : 
                    pass
                else :
                    valeur = None
                
                # Mémorisation
                if valeur != None and codeChamp not in ("IDindividu", "INDIVIDU_ID", "FAMILLE_ID", "INDIVIDU_AGE", "FAMILLE_QF") :
                    if dictValeurs.has_key(codeChamp) == False :
                        dictValeurs[codeChamp] = {"valeur":valeur, "label" : labelChamp}
                    else :
                        dictValeurs[codeChamp]["valeur"] += valeur

        # Affichage des résultats
        def FormateValeur(valeur):
            # Nombre
            if isinstance(valeur, int) : 
                if valeur == 0 : return None
                return str(valeur)
            if isinstance(valeur, float) : 
                if valeur == 0.0 : return None
                return str(valeur)
            # Heure
            if isinstance(valeur, datetime.timedelta) : 
                valeur = DeltaEnStr(valeur)
                if valeur == "00:00" : 
                    return None
                return valeur
            return None

        listeTextes = []
        for codeChamp, dictTemp in dictValeurs.iteritems() :
            label = dictTemp["label"]
            valeur = dictTemp["valeur"]
            
            valeur = FormateValeur(valeur)
            if valeur != None :
                listeTextes.append(u"%s = %s" % (label, valeur))
        
        try :
            texte = _(u"---- TOTAUX pour les %d individus de la liste ----\n%s") % (len(listeTracks), ", ".join(listeTextes))
            self.GetParent().ctrl_totaux.SetValue(texte)
        except :
            pass
            
        
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """    
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        txtTotal = self.GetParent().ctrl_totaux.GetValue()
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Etat nominatif des consommations"), total=txtTotal, format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        txtTotal = self.GetParent().ctrl_totaux.GetValue()
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Etat nominatif des consommations"), total=txtTotal, format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des champs"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des champs"))
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une information..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        self.listView.AfficheTotaux()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((600, 600))
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        # Paramètres de tests
        IDprofil = 10
        listeActivites = [1, 2, 3, 4]
        dateMin = datetime.date(2012, 9, 1)
        dateMax = datetime.date(2012, 9, 30)
        
        # Récupération de tous les champs disponibles
        import OL_Etat_nomin_champs
        champs = OL_Etat_nomin_champs.Champs(listeActivites=listeActivites, dateMin=dateMin, dateMax=dateMax)
        dictChamps = champs.GetDictChamps() 
        listeChampsDispo = champs.GetChamps() 
        
        # Récupération des champs sélectionnés du profil
        DB = GestionDB.DB()
        req = """SELECT IDselection, IDprofil, code, ordre
        FROM etat_nomin_selections
        WHERE IDprofil=%d
        ORDER BY ordre
        ;""" % IDprofil
        DB.ExecuterReq(req)
        listeSelectionChamps = DB.ResultatReq()     
        DB.Close() 
        listeChamps = []
        import OL_Etat_nomin_selections
        for IDselection, IDprofil, code, ordre in listeSelectionChamps :
            if dictChamps.has_key(code) :
                # Champ disponible
                trackInfo = dictChamps[code]
                dictTemp = {"IDselection":IDselection, "IDprofil":IDprofil, "code":code, "ordre":ordre, "label":trackInfo.label, "type":trackInfo.type, "categorie":trackInfo.categorie, "formule":trackInfo.formule, "titre":trackInfo.titre, "largeur":trackInfo.largeur}
            else :
                # Champ indisponible
                dictTemp = {"IDselection":IDselection, "IDprofil":IDprofil, "code":code, "ordre":ordre, "label":_(u"Non disponible"), "type":None, "categorie":None, "titre":None, "formule":None}
            listeChamps.append(OL_Etat_nomin_selections.Track(dictTemp))
            
        # Création des paramètres
        dictParametres = {
            "caisses" : [1, 2],
            "champs" : listeChamps,
            "champsDispo" : listeChampsDispo,
            "groupes" : [1, 2, 6, 7, 8, 9, 5, 3, 4, 10],
            "age" : None,
            "date_debut" : dateMin,
            "date_fin" : dateMax,
            "activites" : [1, 2, 3, 4],
            "qf" : None,
            "categories" : [6, 5, 1, 3, 2, 4],
            }
        
        self.myOlv = ListView(panel, id=-1, dictParametres=dictParametres, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
