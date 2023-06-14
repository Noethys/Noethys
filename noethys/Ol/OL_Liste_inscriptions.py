#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
import FonctionsPerso

from Utils import UTILS_Titulaires
from Utils import UTILS_Dates
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Questionnaires
from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
DICT_INFOS_INDIVIDUS = {}

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import GroupListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from Utils import UTILS_Infos_individus



LISTE_CHAMPS = [
    {"label":_(u"IDinscription"), "code":"IDinscription", "champ":"inscriptions.IDinscription", "typeDonnee":"entier", "align":"left", "largeur":65, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"IDindividu"), "code":"IDindividu", "champ":"inscriptions.IDindividu", "typeDonnee":"entier", "align":"left", "largeur":65, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Nom complet"), "code":"nomComplet", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":200, "stringConverter":None, "imageGetter":"civilite", "actif":True, "afficher":True},

    {"label":_(u"Activité"), "code": "nomActivite", "champ": "activites.nom", "typeDonnee": "texte", "align": "left", "largeur": 100, "stringConverter": None, "actif": True, "afficher": True},
    {"label":_(u"Groupe"), "code":"nomGroupe", "champ":"groupes.nom", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Catégorie"), "code":"nomCategorie", "champ":"categories_tarifs.nom", "typeDonnee":"texte", "align":"left", "largeur":95, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Date inscrip."), "code":"dateInscription", "champ":"inscriptions.date_inscription", "typeDonnee":"date", "align":"left", "largeur":75, "stringConverter":"date", "actif":True, "afficher":False},
    {"label":_(u"Date désinsc."), "code": "date_desinscription", "champ": "inscriptions.date_desinscription", "typeDonnee": "date", "align": "left", "largeur": 75, "stringConverter": "date", "actif": True, "afficher": False},

    {"label":_(u"Facturé"), "code":"totalFacture", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":65, "stringConverter":"montant", "actif":True, "afficher":True},
    {"label":_(u"Réglé"), "code":"totalRegle", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":65, "stringConverter":"montant", "actif":True, "afficher":True},
    {"label":_(u"Solde"), "code":"totalSolde", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":85, "stringConverter":"solde", "imageGetter":"ventilation", "actif":True, "afficher":True},

    {"label":_(u"IDcivilite"), "code":"IDcivilite", "champ":"IDcivilite", "typeDonnee":"entier", "align":"left", "largeur":65, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Nom"), "code":"nomIndividu", "champ":"individus.nom", "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Prénom"), "code":"prenomIndividu", "champ":"prenom", "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},

    {"label":_(u"Rue"), "code":"rue_resid", "champ":"rue_resid", "typeDonnee":"texte", "align":"left", "largeur":125, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"CP"), "code":"cp_resid", "champ":"cp_resid", "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Ville"), "code":"ville_resid", "champ":"ville_resid", "typeDonnee":"texte", "align":"left", "largeur":110, "stringConverter":None, "actif":True, "afficher":True},

    {"label":_(u"Num. Sécu."), "code":"num_secu", "champ":"num_secu", "typeDonnee":"texte", "align":"left", "largeur":90, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Date naiss."), "code":"date_naiss", "champ":"date_naiss", "typeDonnee":"date", "align":"left", "largeur":75, "stringConverter":"date", "actif":True, "afficher":True},
    {"label":_(u"Age"), "code":"age", "champ":None, "typeDonnee":"entier", "align":"left", "largeur":45, "stringConverter":"age", "actif":True, "afficher":True},
    {"label":_(u"CP naiss."), "code":"cp_naiss", "champ":"cp_naiss", "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Ville naiss."), "code":"ville_naiss", "champ":"ville_naiss", "typeDonnee":"texte", "align":"left", "largeur":85, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"adresse_auto"), "code":"adresse_auto", "champ":"adresse_auto", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Catégorie socio."), "code":"categorie_socio", "champ":"categories_travail.nom", "typeDonnee":"texte", "align":"left", "largeur":95, "stringConverter":None, "actif":True, "afficher":True},

    {"label":_(u"Profession"), "code":"profession", "champ":"profession", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Employeur"), "code":"employeur", "champ":"employeur", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Tél pro."), "code":"travail_tel", "champ":"travail_tel", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Fax pro."), "code":"travail_fax", "champ":"travail_fax", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Email pro."), "code":"travail_mail", "champ":"travail_mail", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Tél dom."), "code":"tel_domicile", "champ":"tel_domicile", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Tél mobile"), "code":"tel_mobile", "champ":"tel_mobile", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Fax dom."), "code":"tel_fax", "champ":"tel_fax", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Email"), "code":"mail", "champ":"individus.mail", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},

    {"label":_(u"Genre"), "code":"genre", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Civilité court"), "code":"civiliteLong", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Civilité long"), "code":"civiliteAbrege", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"nomImage"), "code":"nomImage", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":False, "afficher":False},

    {"label":_(u"IDfamille"), "code":"IDfamille", "champ":"inscriptions.IDfamille", "typeDonnee":"entier", "align":"left", "largeur":45, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Famille"), "code": "nomTitulaires", "champ": None, "typeDonnee": "texte", "align": "left", "largeur": 100, "stringConverter": None, "actif": True, "afficher": True},
]


def GetDictInfosIndividus():
    global DICT_INFOS_INDIVIDUS
    dictInfos = {}
    db = GestionDB.DB()
    req = """SELECT IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid FROM individus;"""
    db.ExecuterReq(req)
    listeDonnees = db.ResultatReq()
    db.Close()
    for IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid in listeDonnees :
        dictInfos[IDindividu] = { "nom" : nom, "prenom" : prenom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid}
    DICT_INFOS_INDIVIDUS = dictInfos


# ---------------------------------------- LISTVIEW  -----------------------------------------------------------------------

class Track(object):
    def __init__(self, listview, donnees):
        for dictChamp in LISTE_CHAMPS :
            setattr(self, dictChamp["code"], donnees[dictChamp["code"]])

        # Récupération des réponses des questionnaires
        for dictQuestion in listview.liste_questions:
            setattr(self, "question_%d" % dictQuestion["IDquestion"], listview.GetReponse(dictQuestion["IDquestion"], self.IDinscription))



class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        self.selectionID = None
        self.selectionTrack = None
        self.IDactivite = None
        self.partis = True
        self.listeGroupes = []
        self.listeCategories = []
        self.regroupement = None
        self.labelParametres = ""
        self.ctrl_regroupement = kwds.pop("ctrl_regroupement", None)
        self.checkColonne = kwds.pop("checkColonne", False)
        self.nomListe = kwds.pop("nomListe", "OL_Liste_inscriptions")
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        GroupListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def OnActivated(self,event):
        pass

    def InitModel(self):
        # Initialisation des questionnaires
        categorie = "inscription"
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

        # Importation des données
        self.donnees = self.GetTracks()

        # Infos individus
        self.infosIndividus = UTILS_Infos_individus.Informations()
        for track in self.donnees :
            self.infosIndividus.SetAsAttributs(parent=track, mode="individu", ID=track.IDindividu)
        for track in self.donnees :
            self.infosIndividus.SetAsAttributs(parent=track, mode="famille", ID=track.IDfamille)

    def GetTracks(self):
        listeListeView = []
        if self.IDactivite == None :
            return listeListeView

        DB = GestionDB.DB()

        conditions = []

        # Condition Activité
        if self.IDactivite != 0 :
            conditions.append("inscriptions.IDactivite=%d" % self.IDactivite)

        # Condition Groupes
        if self.listeGroupes != None :
            if len(self.listeGroupes) == 0 : conditionGroupes = "()"
            elif len(self.listeGroupes) == 1 : conditionGroupes = "(%d)" % self.listeGroupes[0]
            else : conditionGroupes = str(tuple(self.listeGroupes))
            conditions.append("inscriptions.IDgroupe IN %s" % conditionGroupes)

        # Condition Catégories
        if self.listeCategories != None:
            if len(self.listeCategories) == 0 : conditionCategories = "()"
            elif len(self.listeCategories) == 1 : conditionCategories = "(%d)" % self.listeCategories[0]
            else : conditionCategories = str(tuple(self.listeCategories))
            conditions.append("inscriptions.IDcategorie_tarif IN %s" % conditionCategories)

        # Condition Partis
        if self.partis != True :
            conditions.append("(inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s')" % datetime.date.today())
        
        # Infos sur tous les individus
        GetDictInfosIndividus()
        
        # Récupération de la facturation
        dictFacturation = {}

        # Récupère les prestations
        condition = ("WHERE IDactivite=%d" % self.IDactivite) if self.IDactivite != 0 else ""
        req = """SELECT IDfamille, IDindividu, SUM(montant)
        FROM prestations
        %s
        GROUP BY IDfamille, IDindividu
        ;""" % condition
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        for IDfamille, IDindividu, total_prestations in listePrestations :
            if total_prestations == None :
                total_prestations = 0.0
            dictFacturation[(IDfamille, IDindividu)] = {"prestations":total_prestations, "ventilation":0.0}

        # Récupère la ventilation
        condition = ("WHERE prestations.IDactivite=%d" % self.IDactivite) if self.IDactivite != 0 else ""
        req = """SELECT IDfamille, IDindividu, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        %s
        GROUP BY IDfamille, IDindividu
        ;""" % condition
        DB.ExecuterReq(req)
        listeVentilations = DB.ResultatReq()
        for IDfamille, IDindividu, total_ventilation in listeVentilations :
            if (IDfamille, IDindividu) in dictFacturation:
                dictFacturation[(IDfamille, IDindividu)]["ventilation"] = total_ventilation

        # Récupération des données sur les individus
        listeChamps2 = []
        for dictChamp in LISTE_CHAMPS :
            champ = dictChamp["champ"]
            if champ != None :
                listeChamps2.append(champ)

        if len(conditions) > 0 :
            conditions = "AND " + " AND ".join(conditions)
        else :
            conditions = ""

        req = """
        SELECT %s
        FROM inscriptions 
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        LEFT JOIN categories_travail ON categories_travail.IDcategorie = individus.IDcategorie_travail
        WHERE inscriptions.statut='ok' %s
        GROUP BY individus.IDindividu, inscriptions.IDinscription
        ;""" % (",".join(listeChamps2), conditions)
        # LEFT JOIN prestations ON prestations.IDactivite = inscriptions.IDactivite a été supprimé pour accélérer le traitement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        for valeurs in listeDonnees :
            dictTemp = {}
            dictTemp["IDindividu"] = valeurs[0]
            
            # Infos de la table Individus
            index = 0
            for dictChamp in LISTE_CHAMPS :
                if dictChamp["champ"] != None :
                    code = dictChamp["code"]
                    dictTemp[code] = valeurs[index]
                    index += 1
                
            # Infos sur la civilité
            IDcivilite = dictTemp["IDcivilite"]
            if IDcivilite == None :
                IDcivilite = 1
            dictTemp["genre"] = DICT_CIVILITES[IDcivilite]["sexe"]
            dictTemp["categorieCivilite"] = DICT_CIVILITES[IDcivilite]["categorie"]
            dictTemp["civiliteLong"]  = DICT_CIVILITES[IDcivilite]["civiliteLong"]
            dictTemp["civiliteAbrege"] = DICT_CIVILITES[IDcivilite]["civiliteAbrege"] 
            dictTemp["nomImage"] = DICT_CIVILITES[IDcivilite]["nomImage"] 
            
            # Age
            if dictTemp["date_naiss"] == None :
                dictTemp["age"] = None
            else:
                datenaissDD = datetime.date(year=int(dictTemp["date_naiss"][:4]), month=int(dictTemp["date_naiss"][5:7]), day=int(dictTemp["date_naiss"][8:10]))
                datedujour = datetime.date.today()
                age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
                dictTemp["age"] = age
                dictTemp["date_naiss"] = datenaissDD
            
            # Nom Complet
            nomComplet = dictTemp["nomIndividu"]
            if dictTemp["prenomIndividu"] != None :
                nomComplet += ", " + dictTemp["prenomIndividu"]
            dictTemp["nomComplet"] = nomComplet
            
            # Adresse auto ou manuelle
            adresse_auto = dictTemp["adresse_auto"]
            if adresse_auto != None and adresse_auto in DICT_INFOS_INDIVIDUS :
                dictTemp["rue_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["rue_resid"]
                dictTemp["cp_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["cp_resid"]
                dictTemp["ville_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["ville_resid"]
            
            # Facturation
            totalFacture = FloatToDecimal(0.0)
            totalRegle = FloatToDecimal(0.0)
            totalSolde = FloatToDecimal(0.0)
            key = (dictTemp["IDfamille"], dictTemp["IDindividu"])
            if key in dictFacturation :
                totalFacture = FloatToDecimal(dictFacturation[key]["prestations"])
                if totalFacture == None : totalFacture = FloatToDecimal(0.0)
                totalRegle = FloatToDecimal(dictFacturation[key]["ventilation"])
                if totalRegle == None : totalRegle = FloatToDecimal(0.0)
                totalSolde = totalFacture - totalRegle
            dictTemp["totalFacture"] = totalFacture
            dictTemp["totalRegle"] = totalRegle
            dictTemp["totalSolde"] = totalSolde

            # Famille
            dictTemp["nomTitulaires"] = self.dict_titulaires[dictTemp["IDfamille"]]["titulairesSansCivilite"]
            # self.rue = listview.dict_titulaires[self.IDfamille]["adresse"]["rue"]
            # self.cp = listview.dict_titulaires[self.IDfamille]["adresse"]["cp"]
            # self.ville = listview.dict_titulaires[self.IDfamille]["adresse"]["ville"]

            # Formatage sous forme de TRACK
            track = Track(self, dictTemp)
            listeListeView.append(track)

        return listeListeView

    def InitObjectListView(self):
        # Création du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_PNG))

        self.imgVert = self.AddNamedImages("vert", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))

        def GetImageCivilite(track):
            return track.nomImage

        def GetImageVentilation(track):
            if track.totalFacture == track.totalRegle :
                return self.imgVert
            if track.totalRegle == FloatToDecimal(0.0) or track.totalRegle == None :
                return self.imgRouge
            if track.totalRegle < track.totalFacture :
                return self.imgOrange
            return self.imgRouge

        def FormateDate(dateDD):
            if dateDD == None : return ""
            return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateSolde(montant):
            if montant == None : FloatToDecimal(0.0)
            if montant == FloatToDecimal(0.0):
                return u"%.2f %s" % (montant, SYMBOLE)
            elif montant > FloatToDecimal(0.0):
                return u"- %.2f %s" % (montant, SYMBOLE)
            else:
                return u"+ %.2f %s" % (montant, SYMBOLE)

        def FormateAge(age):
            if age == None : return ""
            return _(u"%d ans") % age

        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour(wx.Colour(150, 150, 150))
                
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = "#FFFFFF" # Vert

        # Création des colonnes
        listeColonnes = []
        for dictChamp in LISTE_CHAMPS :
            if dictChamp["afficher"] == True :
                # stringConverter
                if "stringConverter" in dictChamp :
                    stringConverter = dictChamp["stringConverter"]
                    if stringConverter == "date" : stringConverter=FormateDate
                    elif stringConverter == "age" : stringConverter=FormateAge
                    elif stringConverter == "montant" : stringConverter=FormateMontant
                    elif stringConverter == "solde" : stringConverter=FormateSolde
                    else : stringConverter = None
                else:
                    stringConverter = None
                # Image Getter
                if "imageGetter" in dictChamp :
                    imageGetter = dictChamp["imageGetter"]
                    if imageGetter == "civilite" : imageGetter = GetImageCivilite
                    elif imageGetter == "ventilation" : imageGetter = GetImageVentilation
                    else : imageGetter = None
                else:
                    imageGetter = None
                # Création de la colonne
                colonne = ColumnDefn(dictChamp["label"], dictChamp["align"], dictChamp["largeur"], dictChamp["code"], typeDonnee=dictChamp["typeDonnee"], stringConverter=stringConverter, imageGetter=imageGetter)
                listeColonnes.append(colonne)

        # Ajout des questions des questionnaires
        listeColonnes.extend(UTILS_Questionnaires.GetColonnesForOL(self.liste_questions))

        # Ajout des infos individus
        listeChamps = UTILS_Infos_individus.GetNomsChampsPossibles(mode="individu+famille")
        for titre, exemple, code in listeChamps :
            if u"n°" not in titre and "_x_" not in code:
                typeDonnee = UTILS_Infos_individus.GetTypeChamp(code)
                code = code.replace("{", "").replace("}", "")
                listeColonnes.append(ColumnDefn(titre, "left", 100, code, typeDonnee=typeDonnee, visible=False))

        #self.SetColumns(listeColonnes)
        self.SetColumns2(colonnes=listeColonnes, nomListe=self.nomListe)

        # Regroupement
        if self.regroupement != None :
            #self.SetColonneTri(self.regroupement)
            self.SetAlwaysGroupByColumn(self.regroupement)
            self.SetShowGroups(True)
            self.useExpansionColumn = False
        else:
            self.SetShowGroups(False)
            self.useExpansionColumn = False

        # Case à cocher
        if self.checkColonne == True :
            if not self.checkStateColumn:
                self.CreateCheckStateColumn(0)
            if len(self.columns) > 0:
                self.SetSortColumn(self.columns[1])
        else :
            if len(self.columns) > 0:
                self.SetSortColumn(self.columns[0])

        self.SetShowItemCounts(True)
        self.SetEmptyListMsg(_(u"Aucune inscription"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetObjects(self.donnees)

    def GetReponse(self, IDquestion=None, ID=None):
        if IDquestion in self.dict_questionnaires:
            if ID in self.dict_questionnaires[IDquestion]:
                return self.dict_questionnaires[IDquestion][ID]
        return u""

    def GetTitresColonnes(self):
        listeColonnes = []
        for index in range(0, self.GetColumnCount()) :
            listeColonnes.append(self.columns[index].title)
        return listeColonnes
    
    def SetColonneTri(self, label=u""):
        index = 0
        for dictTemp in LISTE_CHAMPS :
            if dictTemp["afficher"] == True :
                if dictTemp["label"] == label :
                    self.SetAlwaysGroupByColumn(index)
                    return
                index += 1
                    
    def MAJ(self, IDindividu=None, IDactivite=None, partis=True, listeGroupes=[], listeCategories=[], regroupement=None, listeColonnes=[], labelParametres=""):
        self.IDactivite = IDactivite
        self.partis = partis
        self.listeGroupes = listeGroupes
        self.listeCategories = listeCategories
        self.regroupement = regroupement
        self.labelParametres = labelParametres
        if IDindividu != None :
            self.selectionID = IDindividu
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        attente = wx.BusyInfo(_(u"Recherche des données..."), self)
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()
        self.InitModel()
        self.InitObjectListView()
        del attente
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def GetListeChamps(self):
        return LISTE_CHAMPS
    
    def SetListeChamps(self, listeChamps=[]):
        global LISTE_CHAMPS
        LISTE_CHAMPS = listeChamps
        
    def SetChampsAffiches(self, listeLabels=[], listeCodes=[]):
        global LISTE_CHAMPS
        index = 0
        for dictTemp in LISTE_CHAMPS :
            if dictTemp["label"] in listeLabels or dictTemp["code"] in listeCodes:
                LISTE_CHAMPS[index]["afficher"] = True
            else:
                LISTE_CHAMPS[index]["afficher"] = False
            index += 1
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        
        menuPop.AppendSeparator()

        # Item Imprimer
        item = wx.MenuItem(menuPop, 91, _(u"Imprimer l'inscription"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ImprimerPDF, id=91)
        if self.Selection() == None : item.Enable(False)

        # Item Envoyer par Email
        item = wx.MenuItem(menuPop, 92, _(u"Envoyer l'inscription par Email"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=92)
        if self.Selection() == None : item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        # Commandes standards
        self.AjouterCommandesMenuContext(menuPop)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Liste des inscriptions"),
            "intro" : self.labelParametres,
            "total" : _(u"> %s individus") % (len(self.GetFilteredObjects()) if self.regroupement else len(self.innerList)),
            "orientation" : wx.PORTRAIT,
            }
        return dictParametres

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDindividu = self.Selection()[0].IDindividu
        IDfamille = self.Selection()[0].IDfamille
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDindividu=IDindividu, IDactivite=self.IDactivite, listeGroupes=self.listeGroupes, listeCategories=self.listeCategories, regroupement=self.regroupement)
        dlg.Destroy()

    def OnConfigurationListe(self):
        if self.ctrl_regroupement != None :
            self.ctrl_regroupement.MAJ()
            self.regroupement = None

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def ImprimerPDF(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune inscription à imprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDinscription = self.Selection()[0].IDinscription
        from Utils import UTILS_Inscriptions
        inscription = UTILS_Inscriptions.Inscription()
        inscription.Impression(listeInscriptions=[IDinscription,])

    def EnvoyerEmail(self, event):
        """ Envoyer l'inscription par Email """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune inscription à envoyer par Email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("INSCRIPTION", "pdf") , categorie="inscription")

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """
        IDinscription = self.Selection()[0].IDinscription
        from Utils import UTILS_Inscriptions
        inscription = UTILS_Inscriptions.Inscription()
        resultat = inscription.Impression(listeInscriptions=[IDinscription,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False :
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDinscription]



# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomComplet" : {"mode" : "nombre", "singulier" : _(u"inscription"), "pluriel" : _(u"inscriptions"), "alignement" : wx.ALIGN_CENTER},
            "totalFacture" : {"mode" : "total"},
            "totalRegle" : {"mode" : "total"},
            "totalSolde" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.myOlv.MAJ(IDactivite=1, listeGroupes=[1, 2], listeCategories=[1, 2], listeColonnes=["nomComplet", "age"]) 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((800, 400))
        self.Layout()




if __name__ == '__main__':
##    GetDictFacturation() 
    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
