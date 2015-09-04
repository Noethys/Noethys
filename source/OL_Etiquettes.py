#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import UTILS_Titulaires
import UTILS_Questionnaires
import DATA_Civilites as Civilites
import UTILS_Infos_individus

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


DICT_INFOS_INDIVIDUS = {}


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

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

def GetInfosOrganisme():
    # R�cup�ration des infos sur l'organisme
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
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.IDnationalite = donnees["IDnationalite"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        self.IDpays_naiss = donnees["IDpays_naiss"]
        self.cp_naiss = donnees["cp_naiss"]
        self.ville_naiss = donnees["ville_naiss"]
        self.adresse_auto = donnees["adresse_auto"]
        
        # Adresse auto ou manuelle
        if self.adresse_auto != None and DICT_INFOS_INDIVIDUS.has_key(self.adresse_auto) :
            self.rue_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["rue_resid"]
            self.cp_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["cp_resid"]
            self.ville_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["ville_resid"]
        else:
            self.rue_resid = donnees["rue_resid"]
            self.cp_resid = donnees["cp_resid"]
            self.ville_resid = donnees["ville_resid"]
        
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
        
        # R�cup�ration des r�ponses des questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            exec(u"self.question_%d = self.listview.GetReponse(%d, %s)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"], self.IDindividu))
            

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
            exec(u"dictTemp['{QUESTION_%d}'] = FormateStr(self.question_%d)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"]))
            if dictQuestion["controle"] == "codebarres" :
                exec(u"dictTemp['{CODEBARRES_QUESTION_%d}'] = FormateStr(self.question_%d)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"]))
        
        # Infos de base individus
        dictTemp.update(self.infosIndividus.GetDictValeurs(mode="individu", ID=self.IDindividu, formatChamp=True))
        
        return dictTemp

def GetListeIndividus(listview=None, listeActivites=None, presents=None, IDindividu=None, infosIndividus=None):
    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

    # Conditions Pr�sents
    conditionPresents = ""
    jointurePresents = ""
    if presents != None :
        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s')" % (str(presents[0]), str(presents[1]))
        jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"
    
    # Condition Individu donn�
    conditionIndividus = ""
    if IDindividu != None :
        conditionIndividus = " AND individus.IDindividu=%d" % IDindividu
        
    # R�cup�ration des individus
    listeChamps = (
        "individus.IDindividu", "IDcivilite", "nom", "prenom", "num_secu","IDnationalite", 
        "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
        "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
        "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
        "tel_domicile", "tel_mobile", "tel_fax", "mail"
        )
    DB = GestionDB.DB()
    req = """
    SELECT %s
    FROM individus 
    LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
    %s
    WHERE (inscriptions.parti=0 OR inscriptions.parti IS NULL) %s %s %s
    GROUP BY individus.IDindividu
    ;""" % (",".join(listeChamps), jointurePresents, conditionActivites, conditionPresents, conditionIndividus)
    
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 

    # R�cup�ration des civilit�s
    dictCivilites = Civilites.GetDictCivilites()
    
    # R�cup�ration des adresses auto
    GetDictInfosIndividus()
        
    listeListeView = []
    for valeurs in listeDonnees :
        dictTemp = {}
        dictTemp["IDindividu"] = valeurs[0]
        # Infos de la table Individus
        for index in range(0, len(listeChamps)) :
            nomChamp = listeChamps[index]
            dictTemp[nomChamp] = valeurs[index]
        # Infos sur la civilit�
        if dictTemp["IDcivilite"] == None or dictTemp["IDcivilite"] == "" :
            IDcivilite = 1
        else :
            IDcivilite = dictTemp["IDcivilite"]
        dictTemp["genre"] = dictCivilites[IDcivilite]["sexe"]
        dictTemp["categorieCivilite"] = dictCivilites[IDcivilite]["categorie"]
        dictTemp["civiliteLong"]  = dictCivilites[IDcivilite]["civiliteLong"]
        dictTemp["civiliteAbrege"] = dictCivilites[IDcivilite]["civiliteAbrege"] 
        dictTemp["nomImage"] = dictCivilites[IDcivilite]["nomImage"] 
        
        if dictTemp["date_naiss"] == None :
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
        self.regime = donnees["nomRegime"]
        self.caisse = donnees["nomCaisse"]
        self.numAlloc = donnees["numAlloc"]
        
        # Ajout des adresses Emails des titulaires
        self.listeMails = donnees["listeMails"]
        if len(self.listeMails) > 0 :
            self.mail = self.listeMails[0]
        else :
            self.mail = None
        
        # R�cup�ration des r�ponses des questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            exec(u"self.question_%d = self.listview.GetReponse(%d, %s)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"], self.IDfamille))

    def GetDict(self):
        dictTemp = {
            "{IDFAMILLE}" : str(self.IDfamille),
            "{CODEBARRES_ID_FAMILLE}" : "A%06d" % self.IDfamille,
            "{FAMILLE_NOM}" : FormateStr(self.nomTitulaires),
            "{FAMILLE_RUE}" : FormateStr(self.rue),
            "{FAMILLE_CP}" : FormateStr(self.cp),
            "{FAMILLE_VILLE}" : FormateStr(self.ville),
            "{FAMILLE_REGIME}" : FormateStr(self.regime),
            "{FAMILLE_CAISSE}" : FormateStr(self.caisse),
            "{FAMILLE_NUMALLOC}" : FormateStr(self.numAlloc),
            }
        
        # Questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            exec(u"dictTemp['{QUESTION_%d}'] = FormateStr(self.question_%d)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"]))
            if dictQuestion["controle"] == "codebarres" :
                exec(u"dictTemp['{CODEBARRES_QUESTION_%d}'] = FormateStr(self.question_%d)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"]))
        
        # Infos de base individus
        dictTemp.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=self.IDfamille, formatChamp=True))

        return dictTemp

def GetListeFamilles(listview=None, listeActivites=None, presents=None, IDfamille=None, infosIndividus=None):
    """ R�cup�ration des infos familles """
    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

    # Conditions Pr�sents
    conditionPresents = ""
    jointurePresents = ""
    if presents != None :
        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s')" % (str(presents[0]), str(presents[1]))
        jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"

    # Condition Famille donn�e
    conditionFamilles = ""
    if IDfamille != None :
        conditionFamilles = " AND familles.IDfamille=%d" % IDfamille

    # R�cup�ration des r�gimes et num d'alloc pour chaque famille
    DB = GestionDB.DB()
    req = """
    SELECT 
    familles.IDfamille, regimes.nom, caisses.nom, num_allocataire
    FROM familles 
    LEFT JOIN inscriptions ON inscriptions.IDfamille = familles.IDfamille
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    %s
    AND inscriptions.IDfamille = familles.IDfamille
    LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
    LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
    WHERE (inscriptions.parti=0 or inscriptions.parti IS NULL) %s %s %s
    GROUP BY familles.IDfamille
    ;""" % (jointurePresents, conditionActivites, conditionPresents, conditionFamilles)

    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()
    DB.Close() 
    
    # Formatage des donn�es
    listeListeView = []
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, nomRegime, nomCaisse, numAlloc in listeFamilles :
        dictTemp = {}
        if IDfamille != None and titulaires.has_key(IDfamille) :
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
            rue = titulaires[IDfamille]["adresse"]["rue"]
            cp = titulaires[IDfamille]["adresse"]["cp"]
            ville = titulaires[IDfamille]["adresse"]["ville"]
            listeMails = titulaires[IDfamille]["listeMails"]
        else :
            nomTitulaires = _(u"Aucun titulaire")
            rue = u""
            cp = u""
            ville = u""
            listeMails = []
        dictTemp = {
            "IDfamille" : IDfamille, "titulaires" : nomTitulaires, "nomRegime" : nomRegime, 
            "nomCaisse" : nomCaisse, "numAlloc" : numAlloc,
            "rue" : rue, "cp" : cp, "ville" : ville, "listeMails" : listeMails,
            }
    
        # Formatage sous forme de TRACK
        track = TrackFamille(listview, dictTemp, infosIndividus)
        listeListeView.append(track)
        
    return listeListeView


#-----------LISTVIEW-----------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.categorie = kwds.pop("categorie", "individus")
        self.IDindividu = kwds.pop("IDindividu", None)
        self.IDfamille = kwds.pop("IDfamille", None)
        self.listeActivites = None
        self.presents = None
        # Infos organisme
        self.dictOrganisme = GetInfosOrganisme()
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        # R�cup�ration des questions
        self.LISTE_QUESTIONS = self.UtilsQuestionnaires.GetQuestions(type=self.categorie[:-1])
        
        # R�cup�ration des questionnaires
        self.DICT_QUESTIONNAIRES = self.UtilsQuestionnaires.GetReponses(type=self.categorie[:-1])

        # R�cup�ration des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 
        
        # R�cup�ration des tracks
        if self.categorie == "individus" :
            self.donnees = GetListeIndividus(self, self.listeActivites, self.presents, self.IDindividu, self.infosIndividus)
        else:
            self.donnees = GetListeFamilles(self, self.listeActivites, self.presents, self.IDfamille, self.infosIndividus)

    def InitObjectListView(self):
        # Cr�ation du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap("Images/16x16/%s" % nomImage, wx.BITMAP_TYPE_PNG))
        
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
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        if self.categorie == "individus" :
            # INDIVIDUS
            liste_Colonnes = [
                ColumnDefn(u"", "left", 22, "IDindividu", typeDonnee="entier", imageGetter=GetImageCivilite),
                ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Pr�nom"), "left", 100, "prenom", typeDonnee="texte"),
                ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
                ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
                ColumnDefn(_(u"Rue"), "left", 150, "rue_resid", typeDonnee="texte"),
                ColumnDefn(_(u"C.P."), "left", 50, "cp_resid", typeDonnee="texte"),
                ColumnDefn(_(u"Ville"), "left", 120, "ville_resid", typeDonnee="texte"),
##                ColumnDefn(_(u"T�l. domicile"), "left", 100, "tel_domicile"),
##                ColumnDefn(_(u"T�l. mobile"), "left", 100, "tel_mobile"),
                ColumnDefn(_(u"Email"), "left", 150, "mail", typeDonnee="texte"),
##                ColumnDefn(_(u"Profession"), "left", 150, "profession"),
##                ColumnDefn(_(u"Employeur"), "left", 150, "employeur"),
##                ColumnDefn(_(u"T�l pro."), "left", 100, "travail_tel"),
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
                ColumnDefn(_(u"Email"), "left", 100, "mail", typeDonnee="texte"),
                ColumnDefn(_(u"R�gime"), "left", 130, "regime", typeDonnee="texte"),
                ColumnDefn(_(u"Caisse"), "left", 130, "caisse", typeDonnee="texte"),
                ColumnDefn(_(u"Num�ro Alloc."), "left", 120, "numAlloc", typeDonnee="texte"),
                ]        
        
        # Ajout des questions des questionnaires
        for dictQuestion in self.LISTE_QUESTIONS :
            nomChamp = "question_%d" % dictQuestion["IDquestion"]
            #typeDonnee = UTILS_Infos_individus.GetTypeChamp(nomChamp)
            filtre = dictQuestion["filtre"]
            if filtre == "texte" : typeDonnee = "texte"
            elif filtre == "entier" : typeDonnee = "entier"
            elif filtre == "montant" : typeDonnee = "montant"
            elif filtre == "choix" : typeDonnee = "texte"
            elif filtre == "coche" : typeDonnee = "texte"
            elif filtre == "date" : typeDonnee = "date"
            else : typeDonnee = "texte"
            liste_Colonnes.append(ColumnDefn(dictQuestion["label"], "left", 150, "question_%d" % dictQuestion["IDquestion"], typeDonnee=typeDonnee))

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        
        if self.categorie == "individus" :
            self.SetEmptyListMsg(_(u"Aucun individu"))
        else:
            self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
        if self.DICT_QUESTIONNAIRES.has_key(IDquestion) :
            if self.DICT_QUESTIONNAIRES[IDquestion].has_key(ID) :
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
            for code, valeur in self.dictOrganisme.iteritems() :
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
        
##    def FiltrerPresents(self, event=None):
##        import DLG_Selection_individus
##        dlg = DLG_Selection_individus.Dialog(self)
##        if dlg.ShowModal() == wx.ID_OK:
##            self.listeActivites = dlg.GetActivites() 
##            self.presents = dlg.GetPeriodePresents() 
##            self.MAJ() 
##            self.CocheTout() 
##            dlg.Destroy()
##        else:
##            dlg.Destroy()
##            return
    
    def OnCheck(self, track):
        try :
            self.GetParent().OnCheck(track)
        except :
            pass
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()
        
        # Tout s�lectionner
        item = wx.MenuItem(menuPop, 20, _(u"Tout cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeTout, id=20)

        # Tout d�-s�lectionner
        item = wx.MenuItem(menuPop, 30, _(u"Tout d�cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeRien, id=30)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donn�e � imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import UTILS_Printer
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
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des %s") % self.categorie)
        
    def ExportExcel(self, event):
        import UTILS_Export
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
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
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
