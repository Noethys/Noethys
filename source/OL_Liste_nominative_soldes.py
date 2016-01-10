#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
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
import decimal

import wx.lib.agw.pybusyinfo as PBI
import UTILS_Titulaires
import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()
import UTILS_Utilisateurs
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

DICT_INFOS_INDIVIDUS = {}


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter



LISTE_CHAMPS = [
    {"label":_(u"IDindividu"), "code":"IDindividu", "champ":"inscriptions.IDindividu", "typeDonnee":"entier", "align":"left", "largeur":0, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Nom complet"), "code":"nomComplet", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":200, "stringConverter":None, "imageGetter":"civilite", "actif":True, "afficher":True},

    {"label":_(u"Groupe"), "code":"nomGroupe", "champ":"groupes.nom", "typeDonnee":"texte", "align":"left", "largeur":85, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Catégorie"), "code":"nomCategorie", "champ":"categories_tarifs.nom", "typeDonnee":"texte", "align":"left", "largeur":95, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Date inscrip."), "code":"dateInscription", "champ":"inscriptions.date_inscription", "typeDonnee":"date", "align":"left", "largeur":75, "stringConverter":"date", "actif":True, "afficher":False},
    
    {"label":_(u"Facturé"), "code":"totalFacture", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":65, "stringConverter":"montant", "actif":True, "afficher":True},
    {"label":_(u"Réglé"), "code":"totalRegle", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":65, "stringConverter":"montant", "actif":True, "afficher":True},
    {"label":_(u"Solde"), "code":"totalSolde", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":95, "stringConverter":"solde", "imageGetter":"ventilation", "actif":True, "afficher":True},

    {"label":_(u"IDcivilite"), "code":"IDcivilite", "champ":"IDcivilite", "typeDonnee":"entier", "align":"left", "largeur":65, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Nom"), "code":"nomIndividu", "champ":"individus.nom", "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Prénom"), "code":"prenomIndividu", "champ":"prenom", "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    
    {"label":_(u"Rue"), "code":"rue_resid", "champ":"rue_resid", "typeDonnee":"texte", "align":"left", "largeur":125, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"CP"), "code":"cp_resid", "champ":"cp_resid", "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Ville"), "code":"ville_resid", "champ":"ville_resid", "typeDonnee":"texte", "align":"left", "largeur":110, "stringConverter":None, "actif":True, "afficher":True},
    
    {"label":_(u"Num. Sécu."), "code":"num_secu", "champ":"num_secu", "typeDonnee":"texte", "align":"left", "largeur":90, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Date naiss."), "code":"date_naiss", "champ":"date_naiss", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":"date", "actif":True, "afficher":True},
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
    {"label":_(u"Email"), "code":"mail", "champ":"mail", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    
    {"label":_(u"Genre"), "code":"genre", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Civilité court"), "code":"civiliteLong", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Civilité long"), "code":"civiliteAbrege", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"nomImage"), "code":"nomImage", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":False, "afficher":False},
    
    {"label":_(u"IDfamille"), "code":"IDfamille", "champ":"inscriptions.IDfamille", "typeDonnee":"entier", "align":"left", "largeur":45, "stringConverter":None, "actif":False, "afficher":False},
    
    ]


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

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


# ---------------------------------------- LISTVIEW  -----------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees):
        for dictChamp in LISTE_CHAMPS :
            exec("""self.%s = donnees["%s"]""" % (dictChamp["code"], dictChamp["code"]))
            
        
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        FastObjectListView.__init__(self, *args, **kwds)
        self.selectionID = None
        self.selectionTrack = None
        self.listeActivites = []
        self.listeGroupes = []
        self.listeCategories = []
        self.presents = None
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def OnActivated(self,event):
        pass

    def InitModel(self):
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des prestations en cours..."), parent=None, title=_(u"Patientez"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        self.donnees = self.GetTracks()
        del dlgAttente
    
    def GetTracks(self):
        listeListeView = []
        
        DB = GestionDB.DB()

        # Condition Activités
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        # Condition Groupes
        if len(self.listeGroupes) == 0 : conditionGroupes = "()"
        elif len(self.listeGroupes) == 1 : conditionGroupes = "(%d)" % self.listeGroupes[0]
        else : conditionGroupes = str(tuple(self.listeGroupes))

        # Condition Catégories
        if len(self.listeCategories) == 0 : conditionCategories = "()"
        elif len(self.listeCategories) == 1 : conditionCategories = "(%d)" % self.listeCategories[0]
        else : conditionCategories = str(tuple(self.listeCategories))
        
        # Condition dates de présences
        if self.presents != None :
            conditionPresents = "AND prestations.date>='%s' AND prestations.date <='%s' " % (self.presents[0], self.presents[1])
        else :
            conditionPresents = ""
            
        # Infos sur tous les individus
        GetDictInfosIndividus()
        
        # Récupération de la facturation
        dictFacturation = {}

        # Récupère les prestations
        req = """SELECT IDfamille, IDindividu, SUM(montant)
        FROM prestations
        WHERE IDactivite IN %s %s
        GROUP BY IDfamille, IDindividu
        ;""" % (conditionActivites, conditionPresents)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        for IDfamille, IDindividu, total_prestations in listePrestations :
            if dictFacturation.has_key(IDindividu) == False :
                dictFacturation[IDindividu] = {"prestations":0.0, "ventilation":0.0}
            dictFacturation[IDindividu]["prestations"] += total_prestations
            
        # Récupère la ventilation
        req = """SELECT IDfamille, IDindividu, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        WHERE prestations.IDactivite IN %s %s
        GROUP BY IDfamille, IDindividu
        ;""" % (conditionActivites, conditionPresents)
        DB.ExecuterReq(req)
        listeVentilations = DB.ResultatReq()
        for IDfamille, IDindividu, total_ventilation in listeVentilations :
            if dictFacturation.has_key(IDindividu) == True :
                dictFacturation[IDindividu]["ventilation"] = total_ventilation

        # Récupération des données sur les individus
        listeChamps2 = []
        for dictChamp in LISTE_CHAMPS :
            champ = dictChamp["champ"]
            if champ != None :
                listeChamps2.append(champ)
        
        req = """
        SELECT %s
        FROM individus 
        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        LEFT JOIN categories_travail ON categories_travail.IDcategorie = individus.IDcategorie_travail
        LEFT JOIN prestations ON prestations.IDindividu = inscriptions.IDindividu
        WHERE prestations.IDactivite IN %s %s
        AND inscriptions.IDgroupe IN %s
        AND inscriptions.IDcategorie_tarif IN %s
        GROUP BY individus.IDindividu
        ;""" % (",".join(listeChamps2), conditionActivites, conditionPresents, conditionGroupes, conditionCategories)
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
            dictTemp["genre"] = DICT_CIVILITES[dictTemp["IDcivilite"]]["sexe"]
            dictTemp["categorieCivilite"] = DICT_CIVILITES[dictTemp["IDcivilite"]]["categorie"]
            dictTemp["civiliteLong"]  = DICT_CIVILITES[dictTemp["IDcivilite"]]["civiliteLong"]
            dictTemp["civiliteAbrege"] = DICT_CIVILITES[dictTemp["IDcivilite"]]["civiliteAbrege"] 
            dictTemp["nomImage"] = DICT_CIVILITES[dictTemp["IDcivilite"]]["nomImage"] 
            
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
            if adresse_auto != None and DICT_INFOS_INDIVIDUS.has_key(adresse_auto) :
                dictTemp["rue_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["rue_resid"]
                dictTemp["cp_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["cp_resid"]
                dictTemp["ville_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["ville_resid"]
            
            # Facturation
            totalFacture = 0.0
            totalRegle = 0.0 
            totalSolde = 0.0 
##            key = (dictTemp["IDfamille"], dictTemp["IDindividu"])
            key = dictTemp["IDindividu"]
            if dictFacturation.has_key(key) :
                totalFacture = decimal.Decimal(str(dictFacturation[key]["prestations"]))
                if totalFacture == None : totalFacture = 0.0
                totalRegle = decimal.Decimal(str(dictFacturation[key]["ventilation"]))
                if totalRegle == None : totalRegle = 0.0 
                totalSolde = totalFacture - totalRegle
            dictTemp["totalFacture"] = totalFacture
            dictTemp["totalRegle"] = totalRegle
            dictTemp["totalSolde"] = totalSolde
            
            # Formatage sous forme de TRACK
            track = Track(dictTemp)
            listeListeView.append(track)

        return listeListeView

    def InitObjectListView(self):
        # Création du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap("Images/16x16/%s" % nomImage, wx.BITMAP_TYPE_PNG))

        self.imgVert = self.AddNamedImages("vert", wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))

        def GetImageCivilite(track):
            return track.nomImage

        def GetImageVentilation(track):
            if track.totalFacture == track.totalRegle :
                return self.imgVert
            if track.totalRegle == 0.0 or track.totalRegle == None :
                return self.imgRouge
            if track.totalRegle < track.totalFacture :
                return self.imgOrange
            return self.imgRouge

        def FormateDate(dateDD):
            if dateDD == None : return ""
            return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateSolde(montant):
            if montant == None : montant = decimal.Decimal("0.0")
            if montant == decimal.Decimal(str("0.0")) :
                return u"%.2f %s" % (montant, SYMBOLE)
            elif montant > decimal.Decimal(str("0.0")) :
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
        
        # Champs à afficher : 
        selection_champs = ["IDindividu", "nomComplet", "nomGroupe", "nomCategorie", "totalFacture", "totalRegle", "totalSolde"]
        
        # Création des colonnes
        listeColonnes = []
        for dictChamp in LISTE_CHAMPS :
            if dictChamp["code"] in selection_champs :
                # stringConverter
                if dictChamp.has_key("stringConverter") :
                    stringConverter = dictChamp["stringConverter"]
                    if stringConverter == "date" : stringConverter=FormateDate
                    elif stringConverter == "age" : stringConverter=FormateAge
                    elif stringConverter == "montant" : stringConverter=FormateMontant
                    elif stringConverter == "solde" : stringConverter=FormateSolde
                    else : stringConverter = None
                else:
                    stringConverter = None
                # Image Getter
                if dictChamp.has_key("imageGetter") :
                    imageGetter = dictChamp["imageGetter"]
                    if imageGetter == "civilite" : imageGetter = GetImageCivilite
                    elif imageGetter == "ventilation" : imageGetter = GetImageVentilation
                    else : imageGetter = None
                else:
                    imageGetter = None
                # Création de la colonne
                colonne = ColumnDefn(dictChamp["label"], dictChamp["align"], dictChamp["largeur"], dictChamp["code"], typeDonnee=dictChamp["typeDonnee"], stringConverter=stringConverter, imageGetter=imageGetter)
                listeColonnes.append(colonne)
        self.SetColumns(listeColonnes)

        self.SetSortColumn(self.columns[1])
        self.SetEmptyListMsg(_(u"Aucun individu"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetObjects(self.donnees)
        
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
                    
    def MAJ(self, IDindividu=None, listeActivites=[], listeGroupes=[], listeCategories=[], presents=None):
        self.listeActivites = listeActivites
        self.listeGroupes = listeGroupes
        self.listeCategories = listeCategories
        self.presents = presents
        if IDindividu != None :
            self.selectionID = IDindividu
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
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
        
    def SetChampsAffiches(self, listeLabels=[]):
        global LISTE_CHAMPS
        index = 0
        for dictTemp in LISTE_CHAMPS :
            if dictTemp["label"] in listeLabels :
                LISTE_CHAMPS[index]["afficher"] = True
            else:
                LISTE_CHAMPS[index]["afficher"] = False
            index += 1
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        
        menuPop.AppendSeparator()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDindividu = self.Selection()[0].IDindividu
        IDfamille = self.Selection()[0].IDfamille
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDindividu=IDindividu, listeActivites=self.listeActivites, listeGroupes=self.listeGroupes, listeCategories=self.listeCategories, presents=self.presents)
        dlg.Destroy()
        
    def Apercu(self, event):
        nbreIndividus = len(self.donnees) 
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des soldes individuels"), intro=_(u"> %d individus") % nbreIndividus, format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        nbreIndividus = len(self.donnees) 
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des soldes individuels"), intro=_(u"> %d individus") % nbreIndividus, format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des soldes individuels"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des soldes individuels"), autoriseSelections=False)


# -------------------------------------------------------------------------------------------------------------------------------------------


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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomComplet" : {"mode" : "nombre", "singulier" : _(u"individu"), "pluriel" : _(u"individus"), "alignement" : wx.ALIGN_CENTER},
            "totalFacture" : {"mode" : "total"},
            "totalRegle" : {"mode" : "total"},
            "totalSolde" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

# ----------------- FRAME DE TEST ----------------------------------------------------------------

##class MyFrame(wx.Frame):
##    def __init__(self, *args, **kwds):
##        wx.Frame.__init__(self, *args, **kwds)
##        panel = wx.Panel(self, -1)
##        sizer_1 = wx.BoxSizer(wx.VERTICAL)
##        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
##        self.SetSizer(sizer_1)
##        self.myOlv = ListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
##        self.myOlv.MAJ(IDactivite=1, listeGroupes=[1, 2], listeCategories=[1, 2], listeColonnes=["nomComplet", "age"]) 
##        sizer_2 = wx.BoxSizer(wx.VERTICAL)
##        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
##        panel.SetSizer(sizer_2)
##        self.SetSize((800, 400))
##        self.Layout()



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((600, 600))
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(IDindividu=None, listeActivites=[1,], listeGroupes=[1, 2], listeCategories=[1, 2], presents=(datetime.date(2012, 1, 4), datetime.date(2015, 1, 4)))
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
