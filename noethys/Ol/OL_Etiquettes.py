#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import FonctionsPerso
import GestionDB
import datetime
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Infos_individus
from Utils import UTILS_Internet
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


DICT_INFOS_INDIVIDUS = {}


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def GetDictInfosIndividus():
    global DICT_INFOS_INDIVIDUS
    dictInfos = {}
    db = GestionDB.DB()
    req = """SELECT IDindividu, individus.nom, prenom, rue_resid, cp_resid, ville_resid, secteurs.nom
    FROM individus
    LEFT JOIN secteurs ON secteurs.IDsecteur = individus.IDsecteur;"""
    db.ExecuterReq(req)
    listeDonnees = db.ResultatReq()
    db.Close()
    for IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid, nom_secteur in listeDonnees :
        dictInfos[IDindividu] = { "nom" : nom, "prenom" : prenom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid, "nom_secteur": nom_secteur}
    DICT_INFOS_INDIVIDUS = dictInfos

def GetInfosOrganisme():
    # Récupération des infos sur l'organisme
    DB = GestionDB.DB()
    req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
    FROM organisateur
    WHERE IDorganisateur=1;""" 
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()  
    DB.Close()     
    dictOrganisme = {}
    for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees :
        if ville != None : ville = ville.capitalize()
        dictOrganisme["{ORGANISATEUR_NOM}"] = nom
        dictOrganisme["{ORGANISATEUR_RUE}"] = rue
        dictOrganisme["{ORGANISATEUR_CP}"] = cp
        dictOrganisme["{ORGANISATEUR_VILLE}"] = ville
        dictOrganisme["{ORGANISATEUR_TEL}"] = tel
        dictOrganisme["{ORGANISATEUR_FAX}"] = fax
        dictOrganisme["{ORGANISATEUR_MAIL}"] = mail
        dictOrganisme["{ORGANISATEUR_SITE}"] = site
        dictOrganisme["{ORGANISATEUR_AGREMENT}"] = num_agrement
        dictOrganisme["{ORGANISATEUR_SIRET}"] = num_siret
        dictOrganisme["{ORGANISATEUR_APE}"] = code_ape
    return dictOrganisme


def FormateStr(valeur=u""):
    try :
        if valeur == None : return u""
        elif type(valeur) == int : return str(valeur)
        elif type(valeur) == float : return str(valeur)
        else : return valeur
    except : 
        return u""


def FormateDate(dateStr):
    if dateStr == "" or dateStr == None : return ""
    date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
    text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
    return text





#-----------INDIVIDUS-----------

class TrackIndividu(object):
    def __init__(self, listview, donnees, infosIndividus):
        self.listview = listview
        self.infosIndividus = infosIndividus
        self.IDindividu = donnees["IDindividu"]
        self.IDcivilite = donnees["IDcivilite"]
        self.nom = donnees["individus.nom"]
        self.prenom = donnees["prenom"]
        self.IDnationalite = donnees["IDnationalite"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        self.IDpays_naiss = donnees["IDpays_naiss"]
        self.cp_naiss = donnees["cp_naiss"]
        self.ville_naiss = donnees["ville_naiss"]
        self.adresse_auto = donnees["adresse_auto"]
        self.date_creation = donnees["date_creation"]

        # Adresse auto ou manuelle
        if self.adresse_auto != None and self.adresse_auto in DICT_INFOS_INDIVIDUS :
            self.rue_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["rue_resid"]
            self.cp_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["cp_resid"]
            self.ville_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["ville_resid"]
            self.secteur = DICT_INFOS_INDIVIDUS[self.adresse_auto]["nom_secteur"]
        else:
            self.rue_resid = donnees["rue_resid"]
            self.cp_resid = donnees["cp_resid"]
            self.ville_resid = donnees["ville_resid"]
            self.secteur = donnees["secteurs.nom"]
        
        self.profession = donnees["profession"]
        self.employeur = donnees["employeur"]
        self.travail_tel = donnees["travail_tel"]
        self.travail_fax = donnees["travail_fax"]
        self.travail_mail = donnees["travail_mail"]
        self.tel_domicile = donnees["tel_domicile"]
        self.tel_mobile = donnees["tel_mobile"]
        self.tel_fax = donnees["tel_fax"]
        self.mail = donnees["mail"]
        self.tel_fax = donnees["tel_fax"]
        self.genre = donnees["genre"]
        self.categorieCivilite = donnees["categorieCivilite"]
        self.civiliteLong = donnees["civiliteLong"]
        self.civiliteAbrege = donnees["civiliteAbrege"]
        self.nomImage = donnees["nomImage"]     
        
        # Récupération des réponses des questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], self.listview.GetReponse(dictQuestion["IDquestion"], self.IDindividu))


    def GetDict(self):
        dictTemp = {
            "{IDINDIVIDU}" : str(self.IDindividu),
            "{CODEBARRES_ID_INDIVIDU}" : "I%06d" % self.IDindividu,
            "{INDIVIDU_CIVILITE_LONG}" : FormateStr(self.civiliteLong),
            "{INDIVIDU_CIVILITE_COURT}" : FormateStr(self.civiliteAbrege),
            "{INDIVIDU_GENRE}" : self.genre,
            "{INDIVIDU_NOM}" : FormateStr(self.nom),
            "{INDIVIDU_PRENOM}" : FormateStr(self.prenom),
            "{INDIVIDU_DATE_NAISS}" : FormateDate(self.date_naiss),
            "{INDIVIDU_AGE}" : FormateStr(self.age),
            "{INDIVIDU_CP_NAISS}" : FormateStr(self.cp_naiss),
            "{INDIVIDU_VILLE_NAISS}" : FormateStr(self.ville_naiss),
            "{INDIVIDU_RUE}" : FormateStr(self.rue_resid),
            "{INDIVIDU_CP}" : FormateStr(self.cp_resid),
            "{INDIVIDU_VILLE}" : FormateStr(self.ville_resid),
            "{INDIVIDU_PROFESSION}" : FormateStr(self.profession),
            "{INDIVIDU_EMPLOYEUR}" : FormateStr(self.employeur),
            "{INDIVIDU_TEL_DOMICILE}" : FormateStr(self.tel_domicile),
            "{INDIVIDU_TEL_MOBILE}" : FormateStr(self.tel_mobile),
            "{INDIVIDU_FAX}" : FormateStr(self.tel_fax),
            "{INDIVIDU_EMAIL}" : FormateStr(self.mail),
            "{INDIVIDU_TEL_PRO}" : FormateStr(self.travail_tel),
            "{INDIVIDU_FAX_PRO}" : FormateStr(self.travail_fax),
            "{INDIVIDU_EMAIL_PRO}" : FormateStr(self.travail_mail),
            "nomImage" : self.nomImage,
            }
        
        # Questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            dictTemp["{QUESTION_%d}" % dictQuestion["IDquestion"]] = FormateStr(getattr(self, "question_%d" % dictQuestion["IDquestion"]))
            if dictQuestion["controle"] == "codebarres" :
                dictTemp["{CODEBARRES_QUESTION_%d}" % dictQuestion["IDquestion"]] = FormateStr(getattr(self, "question_%d" % dictQuestion["IDquestion"]))

        # Infos de base individus
        dictTemp.update(self.infosIndividus.GetDictValeurs(mode="individu", ID=self.IDindividu, formatChamp=True))
        
        return dictTemp

def GetListeIndividus(listview=None, listeActivites=None, presents=None, IDindividu=None, infosIndividus=None):
    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d AND inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') " % (listeActivites[0], datetime.date.today())
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s AND inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') " % (str(tuple(listeActivites)), datetime.date.today())

    # Conditions Présents
    conditionPresents = ""
    jointurePresents = ""
    if presents != None :
        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s' AND consommations.etat IN ('reservation', 'present'))" % (str(presents[0]), str(presents[1]))
        jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"
    
    # Condition Individu donné
    conditionIndividus = ""
    if IDindividu != None :
        conditionIndividus = " AND individus.IDindividu=%d" % IDindividu
        
    # Récupération des individus
    listeChamps = (
        "individus.IDindividu", "IDcivilite", "individus.nom", "prenom", "num_secu","IDnationalite",
        "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
        "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
        "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
        "tel_domicile", "tel_mobile", "tel_fax", "mail", "secteurs.nom", "date_creation",
        )
    DB = GestionDB.DB()
    req = """
    SELECT %s
    FROM individus 
    LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
    LEFT JOIN secteurs ON secteurs.IDsecteur = individus.IDsecteur
    %s
    WHERE individus.IDindividu>0 AND individus.deces != 1 AND individus.etat IS NULL %s %s %s
    GROUP BY individus.IDindividu
    ;""" % (",".join(listeChamps), jointurePresents, conditionActivites, conditionPresents, conditionIndividus)
    
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 

    # Récupération des civilités
    dictCivilites = Civilites.GetDictCivilites()
    
    # Récupération des adresses auto
    GetDictInfosIndividus()
        
    listeListeView = []
    for valeurs in listeDonnees :
        dictTemp = {}
        dictTemp["IDindividu"] = valeurs[0]
        # Infos de la table Individus
        for index in range(0, len(listeChamps)) :
            nomChamp = listeChamps[index]
            dictTemp[nomChamp] = valeurs[index]
        # Infos sur la civilité
        if dictTemp["IDcivilite"] == None or dictTemp["IDcivilite"] == "" :
            IDcivilite = 1
        else :
            IDcivilite = dictTemp["IDcivilite"]
        dictTemp["genre"] = dictCivilites[IDcivilite]["sexe"]
        dictTemp["categorieCivilite"] = dictCivilites[IDcivilite]["categorie"]
        dictTemp["civiliteLong"]  = dictCivilites[IDcivilite]["civiliteLong"]
        dictTemp["civiliteAbrege"] = dictCivilites[IDcivilite]["civiliteAbrege"] 
        dictTemp["nomImage"] = dictCivilites[IDcivilite]["nomImage"] 
        
        if not dictTemp["date_naiss"]:
            dictTemp["age"] = None
        else:
            datenaissDD = datetime.date(year=int(dictTemp["date_naiss"][:4]), month=int(dictTemp["date_naiss"][5:7]), day=int(dictTemp["date_naiss"][8:10]))
            datedujour = datetime.date.today()
            age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
            dictTemp["age"] = age
                    
        # Formatage sous forme de TRACK
        track = TrackIndividu(listview, dictTemp, infosIndividus)
        listeListeView.append(track)
        
    return listeListeView


#-----------FAMILLES-----------

class TrackFamille(object):
    def __init__(self, listview, donnees, infosIndividus):
        self.listview = listview
        self.infosIndividus = infosIndividus
        self.IDfamille = donnees["IDfamille"]
        self.nomTitulaires = donnees["titulaires"]
        self.rue = donnees["rue"]
        self.cp = donnees["cp"]
        self.ville = donnees["ville"]
        self.secteur = donnees["secteur"]
        self.regime = donnees["nomRegime"]
        self.caisse = donnees["nomCaisse"]
        self.numAlloc = donnees["numAlloc"]

        self.internet_identifiant = donnees["internet_identifiant"]
        self.internet_mdp = donnees["internet_mdp"]
        if self.internet_mdp and self.internet_mdp.startswith("custom"):
            self.internet_mdp = "********"
        if self.internet_mdp and self.internet_mdp.startswith("#@#"):
            self.internet_mdp = UTILS_Internet.DecrypteMDP(self.internet_mdp, IDfichier=donnees["IDfichier"])

        # Ajout des adresses Emails des titulaires
        self.listeMails = donnees["listeMails"]
        if len(self.listeMails) > 0 :
            self.mail = self.listeMails[0]
        else :
            self.mail = None
        
        # Récupération des réponses des questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], self.listview.GetReponse(dictQuestion["IDquestion"], self.IDfamille))

    def GetDict(self):
        dictTemp = {
            "{IDFAMILLE}" : str(self.IDfamille),
            "{CODEBARRES_ID_FAMILLE}" : "A%06d" % self.IDfamille,
            "{FAMILLE_NOM}" : FormateStr(self.nomTitulaires),
            "{FAMILLE_RUE}" : FormateStr(self.rue),
            "{FAMILLE_CP}" : FormateStr(self.cp),
            "{FAMILLE_VILLE}" : FormateStr(self.ville),
            "{FAMILLE_SECTEUR}": FormateStr(self.secteur),
            "{FAMILLE_REGIME}" : FormateStr(self.regime),
            "{FAMILLE_CAISSE}" : FormateStr(self.caisse),
            "{FAMILLE_NUMALLOC}" : FormateStr(self.numAlloc),
            "{FAMILLE_INTERNET_IDENTIFIANT}": FormateStr(self.internet_identifiant),
            "{FAMILLE_INTERNET_MDP}": FormateStr(self.internet_mdp),
            }
        
        # Questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            dictTemp["{QUESTION_%d}" % dictQuestion["IDquestion"]] = FormateStr(getattr(self, "question_%d" % dictQuestion["IDquestion"]))
            if dictQuestion["controle"] == "codebarres" :
                dictTemp["{CODEBARRES_QUESTION_%d}" % dictQuestion["IDquestion"]] = FormateStr(getattr(self, "question_%d" % dictQuestion["IDquestion"]))

        # Infos de base individus
        dictTemp.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=self.IDfamille, formatChamp=True))

        return dictTemp

def GetListeFamilles(listview=None, listeActivites=None, presents=None, IDfamille=None, infosIndividus=None):
    """ Récupération des infos familles """
    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

    # Conditions Présents
    conditionPresents = ""
    jointurePresents = ""
    if presents != None :
        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s' AND consommations.etat IN ('reservation', 'present'))" % (str(presents[0]), str(presents[1]))
        jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"

    # Condition Famille donnée
    conditionFamilles = ""
    if IDfamille != None :
        conditionFamilles = " AND familles.IDfamille=%d" % IDfamille

    # Récupération des régimes et num d'alloc pour chaque famille
    DB = GestionDB.DB()
    req = """
    SELECT 
    familles.IDfamille, regimes.nom, caisses.nom, num_allocataire, internet_identifiant, internet_mdp
    FROM familles 
    LEFT JOIN inscriptions ON inscriptions.IDfamille = familles.IDfamille
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    %s
    AND inscriptions.IDfamille = familles.IDfamille
    LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
    LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
    WHERE familles.etat IS NULL AND inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') %s %s %s
    GROUP BY familles.IDfamille
    ;""" % (jointurePresents, datetime.date.today(), conditionActivites, conditionPresents, conditionFamilles)

    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()
    DB.Close()

    IDfichier = FonctionsPerso.GetIDfichier()
    
    # Formatage des données
    listeListeView = []
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, nomRegime, nomCaisse, numAlloc, internet_identifiant, internet_mdp in listeFamilles :
        dictTemp = {}
        if IDfamille != None and IDfamille in titulaires :
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
            rue = titulaires[IDfamille]["adresse"]["rue"]
            cp = titulaires[IDfamille]["adresse"]["cp"]
            ville = titulaires[IDfamille]["adresse"]["ville"]
            listeMails = titulaires[IDfamille]["listeMails"]
            secteur = titulaires[IDfamille]["adresse"]["nomSecteur"]
        else :
            nomTitulaires = _(u"Aucun titulaire")
            rue = u""
            cp = u""
            ville = u""
            listeMails = []
        dictTemp = {
            "IDfamille" : IDfamille, "titulaires" : nomTitulaires, "nomRegime" : nomRegime, 
            "nomCaisse" : nomCaisse, "numAlloc" : numAlloc, "secteur": secteur,
            "rue" : rue, "cp" : cp, "ville" : ville, "listeMails" : listeMails, "IDfichier": IDfichier,
            "internet_identifiant": internet_identifiant, "internet_mdp": internet_mdp,
            }
    
        # Formatage sous forme de TRACK
        track = TrackFamille(listview, dictTemp, infosIndividus)
        listeListeView.append(track)
        
    return listeListeView


#-----------LISTVIEW-----------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.categorie = kwds.pop("categorie", "individus")
        self.IDindividu = kwds.pop("IDindividu", None)
        self.IDfamille = kwds.pop("IDfamille", None)
        self.listeActivites = None
        self.presents = None
        # Infos organisme
        self.dictOrganisme = GetInfosOrganisme()
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        # Récupération des questions
        self.LISTE_QUESTIONS = self.UtilsQuestionnaires.GetQuestions(type=self.categorie[:-1])
        
        # Récupération des questionnaires
        self.DICT_QUESTIONNAIRES = self.UtilsQuestionnaires.GetReponses(type=self.categorie[:-1])

        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 
        
        # Récupération des tracks
        if self.categorie == "individus" :
            self.donnees = GetListeIndividus(self, self.listeActivites, self.presents, self.IDindividu, self.infosIndividus)
        else:
            self.donnees = GetListeFamilles(self, self.listeActivites, self.presents, self.IDfamille, self.infosIndividus)

    def InitObjectListView(self):
        # Création du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_PNG))
        
        def GetImageCivilite(track):
            return track.nomImage

        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def FormateAge(age):
            if age == None : return ""
            return _(u"%d ans") % age
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        if self.categorie == "individus" :
            # INDIVIDUS
            liste_Colonnes = [
                ColumnDefn(u"", "left", 22, "IDindividu", typeDonnee="entier", imageGetter=GetImageCivilite),
                ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Prénom"), "left", 100, "prenom", typeDonnee="texte"),
                ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
                ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
                ColumnDefn(_(u"Rue"), "left", 150, "rue_resid", typeDonnee="texte"),
                ColumnDefn(_(u"C.P."), "left", 50, "cp_resid", typeDonnee="texte"),
                ColumnDefn(_(u"Ville"), "left", 120, "ville_resid", typeDonnee="texte"),
                ColumnDefn(_(u"Secteur"), "left", 120, "secteur", typeDonnee="texte"),
                ColumnDefn(_(u"Date création"), "left", 72, "date_creation", typeDonnee="date", stringConverter=FormateDate),
##                ColumnDefn(_(u"Tél. domicile"), "left", 100, "tel_domicile"),
##                ColumnDefn(_(u"Tél. mobile"), "left", 100, "tel_mobile"),
                ColumnDefn(_(u"Email"), "left", 150, "mail", typeDonnee="texte"),
##                ColumnDefn(_(u"Profession"), "left", 150, "profession"),
##                ColumnDefn(_(u"Employeur"), "left", 150, "employeur"),
##                ColumnDefn(_(u"Tél pro."), "left", 100, "travail_tel"),
##                ColumnDefn(_(u"Email pro."), "left", 150, "travail_mail"),
                ]
        
        else:
            # FAMILLES
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
                ColumnDefn(_(u"Famille"), 'left', 200, "nomTitulaires", typeDonnee="texte"),
                ColumnDefn(_(u"Rue"), "left", 160, "rue", typeDonnee="texte"),
                ColumnDefn(_(u"C.P."), "left", 45, "cp", typeDonnee="texte"),
                ColumnDefn(_(u"Ville"), "left", 120, "ville", typeDonnee="texte"),
                ColumnDefn(_(u"Secteur"), "left", 120, "secteur", typeDonnee="texte"),
                ColumnDefn(_(u"Email"), "left", 100, "mail", typeDonnee="texte"),
                ColumnDefn(_(u"Régime"), "left", 130, "regime", typeDonnee="texte"),
                ColumnDefn(_(u"Caisse"), "left", 130, "caisse", typeDonnee="texte"),
                ColumnDefn(_(u"Numéro Alloc."), "left", 120, "numAlloc", typeDonnee="texte"),
                ]        
        
        # Ajout des questions des questionnaires
        liste_Colonnes.extend(UTILS_Questionnaires.GetColonnesForOL(self.LISTE_QUESTIONS))

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        
        if self.categorie == "individus" :
            self.SetEmptyListMsg(_(u"Aucun individu"))
        else:
            self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, categorie=None, listeActivites=None, presents=None):
        if categorie != None :
            if categorie =="individu" : self.categorie = "individus"
            if categorie =="famille" : self.categorie = "familles"
        if listeActivites != None : self.listeActivites = listeActivites
        if presents != None : self.presents = presents
        self.InitModel()
        self.InitObjectListView()

    def GetReponse(self, IDquestion=None, ID=None):
        if IDquestion in self.DICT_QUESTIONNAIRES :
            if ID in self.DICT_QUESTIONNAIRES[IDquestion] :
                return self.DICT_QUESTIONNAIRES[IDquestion][ID]
        return u""

    def Selection(self):
        return self.GetSelectedObjects()
    
    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def GetInfosCoches(self):
        listeDonnees = []
        for track in self.GetTracksCoches() :
            dictTemp = track.GetDict()
            for code, valeur in self.dictOrganisme.items() :
                dictTemp[code] = valeur
            listeDonnees.append(dictTemp)
        return listeDonnees
    
    def SetIDcoches(self, listeID=[]):
        for track in self.donnees :
            if self.categorie == "individus" :
                ID = track.IDindividu
            else :
                ID = track.IDfamille
            if ID in listeID :
                self.Check(track)
                self.RefreshObject(track)
    
    def OnCheck(self, track=None):
        try :
            self.GetParent().OnCheck(track)
        except :
            pass

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Tout sélectionner
        item = wx.MenuItem(menuPop, 20, _(u"Tout cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeTout, id=20)

        # Tout dé-sélectionner
        item = wx.MenuItem(menuPop, 30, _(u"Tout décocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeRien, id=30)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donnée à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des %s") % self.categorie, intro="", total="", format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des %s") % self.categorie)
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des %s") % self.categorie)


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
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
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(categorie="individu", listeActivites=None, presents=None)
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
