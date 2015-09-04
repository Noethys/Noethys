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
import decimal

import UTILS_Dates
import UTILS_Utilisateurs
import UTILS_Titulaires
import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

DICT_INFOS_INDIVIDUS = {}

from ObjectListView import GroupListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter



LISTE_CHAMPS = [
    {"label":_(u"IDindividu"), "code":"IDindividu", "champ":"inscriptions.IDindividu", "typeDonnee":"entier", "align":"left", "largeur":65, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Nom complet"), "code":"nomComplet", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":200, "stringConverter":None, "imageGetter":"civilite", "actif":True, "afficher":True},

    {"label":_(u"Groupe"), "code":"nomGroupe", "champ":"groupes.nom", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Cat�gorie"), "code":"nomCategorie", "champ":"categories_tarifs.nom", "typeDonnee":"texte", "align":"left", "largeur":95, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Date inscrip."), "code":"dateInscription", "champ":"inscriptions.date_inscription", "typeDonnee":"date", "align":"left", "largeur":75, "stringConverter":"date", "actif":True, "afficher":False},
    
    {"label":_(u"Factur�"), "code":"totalFacture", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":65, "stringConverter":"montant", "actif":True, "afficher":True},
    {"label":_(u"R�gl�"), "code":"totalRegle", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":65, "stringConverter":"montant", "actif":True, "afficher":True},
    {"label":_(u"Solde"), "code":"totalSolde", "champ":None, "typeDonnee":"montant", "align":"right", "largeur":85, "stringConverter":"solde", "imageGetter":"ventilation", "actif":True, "afficher":True},

    {"label":_(u"IDcivilite"), "code":"IDcivilite", "champ":"IDcivilite", "typeDonnee":"entier", "align":"left", "largeur":65, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Nom"), "code":"nomIndividu", "champ":"individus.nom", "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Pr�nom"), "code":"prenomIndividu", "champ":"prenom", "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    
    {"label":_(u"Rue"), "code":"rue_resid", "champ":"rue_resid", "typeDonnee":"texte", "align":"left", "largeur":125, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"CP"), "code":"cp_resid", "champ":"cp_resid", "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Ville"), "code":"ville_resid", "champ":"ville_resid", "typeDonnee":"texte", "align":"left", "largeur":110, "stringConverter":None, "actif":True, "afficher":True},
    
    {"label":_(u"Num. S�cu."), "code":"num_secu", "champ":"num_secu", "typeDonnee":"texte", "align":"left", "largeur":90, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Date naiss."), "code":"date_naiss", "champ":"date_naiss", "typeDonnee":"date", "align":"left", "largeur":75, "stringConverter":"date", "actif":True, "afficher":True},
    {"label":_(u"Age"), "code":"age", "champ":None, "typeDonnee":"entier", "align":"left", "largeur":45, "stringConverter":"age", "actif":True, "afficher":True},
    {"label":_(u"CP naiss."), "code":"cp_naiss", "champ":"cp_naiss", "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Ville naiss."), "code":"ville_naiss", "champ":"ville_naiss", "typeDonnee":"texte", "align":"left", "largeur":85, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"adresse_auto"), "code":"adresse_auto", "champ":"adresse_auto", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":False, "afficher":False},
    {"label":_(u"Cat�gorie socio."), "code":"categorie_socio", "champ":"categories_travail.nom", "typeDonnee":"texte", "align":"left", "largeur":95, "stringConverter":None, "actif":True, "afficher":True},
    
    {"label":_(u"Profession"), "code":"profession", "champ":"profession", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Employeur"), "code":"employeur", "champ":"employeur", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"T�l pro."), "code":"travail_tel", "champ":"travail_tel", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Fax pro."), "code":"travail_fax", "champ":"travail_fax", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Email pro."), "code":"travail_mail", "champ":"travail_mail", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"T�l dom."), "code":"tel_domicile", "champ":"tel_domicile", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"T�l mobile"), "code":"tel_mobile", "champ":"tel_mobile", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    {"label":_(u"Fax dom."), "code":"tel_fax", "champ":"tel_fax", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Email"), "code":"mail", "champ":"mail", "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":True},
    
    {"label":_(u"Genre"), "code":"genre", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Civilit� court"), "code":"civiliteLong", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":65, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"Civilit� long"), "code":"civiliteAbrege", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":75, "stringConverter":None, "actif":True, "afficher":False},
    {"label":_(u"nomImage"), "code":"nomImage", "champ":None, "typeDonnee":"texte", "align":"left", "largeur":45, "stringConverter":None, "actif":False, "afficher":False},
    
    {"label":_(u"IDfamille"), "code":"IDfamille", "champ":"inscriptions.IDfamille", "typeDonnee":"entier", "align":"left", "largeur":45, "stringConverter":None, "actif":False, "afficher":False},
    
    ]


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
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
##            exec("""self.%s = donnees["%s"]""" % (dictChamp["code"], dictChamp["code"]))
            setattr(self, dictChamp["code"], donnees[dictChamp["code"]])
            
        
class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        GroupListView.__init__(self, *args, **kwds)
        self.selectionID = None
        self.selectionTrack = None
        self.IDactivite = None
        self.partis = True
        self.listeGroupes = []
        self.listeCategories = []
        self.regroupement = None
        self.listeColonnes = []
        self.labelParametres = ""
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def OnActivated(self,event):
        pass

    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def GetTracks(self):
        listeListeView = []
        if self.IDactivite == None :
            return listeListeView
        
        DB = GestionDB.DB()
                
        # Condition Groupes
        if len(self.listeGroupes) == 0 : conditionGroupes = "()"
        elif len(self.listeGroupes) == 1 : conditionGroupes = "(%d)" % self.listeGroupes[0]
        else : conditionGroupes = str(tuple(self.listeGroupes))

        # Condition Cat�gories
        if len(self.listeCategories) == 0 : conditionCategories = "()"
        elif len(self.listeCategories) == 1 : conditionCategories = "(%d)" % self.listeCategories[0]
        else : conditionCategories = str(tuple(self.listeCategories))
        
        # Condition Partis
        if self.partis == True : 
            conditionPartis = "(0, 1)"
        else : 
            conditionPartis = "(0)"
        
        # Infos sur tous les individus
        GetDictInfosIndividus()
        
        # R�cup�ration de la facturation
        dictFacturation = {}

        # R�cup�re les prestations
        req = """SELECT IDfamille, IDindividu, SUM(montant)
        FROM prestations
        WHERE IDactivite=%d
        GROUP BY IDfamille, IDindividu
        ;""" % self.IDactivite
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        for IDfamille, IDindividu, total_prestations in listePrestations :
            dictFacturation[(IDfamille, IDindividu)] = {"prestations":total_prestations, "ventilation":0.0}
        
        # R�cup�re la ventilation
        req = """SELECT IDfamille, IDindividu, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        WHERE prestations.IDactivite=%d
        GROUP BY IDfamille, IDindividu
        ;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeVentilations = DB.ResultatReq()
        for IDfamille, IDindividu, total_ventilation in listeVentilations :
            dictFacturation[(IDfamille, IDindividu)]["ventilation"] = total_ventilation

        # R�cup�ration des donn�es sur les individus
        listeChamps2 = []
        for dictChamp in LISTE_CHAMPS :
            champ = dictChamp["champ"]
            if champ != None :
                listeChamps2.append(champ)
        
        DB = GestionDB.DB()
        req = """
        SELECT %s
        FROM inscriptions 
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        LEFT JOIN categories_travail ON categories_travail.IDcategorie = individus.IDcategorie_travail
        LEFT JOIN prestations ON prestations.IDactivite = inscriptions.IDactivite
        WHERE inscriptions.IDactivite=%d
        AND inscriptions.IDgroupe IN %s
        AND inscriptions.IDcategorie_tarif IN %s
        AND inscriptions.parti IN %s
        GROUP BY individus.IDindividu
        ;""" % (",".join(listeChamps2), self.IDactivite, conditionGroupes, conditionCategories, conditionPartis)
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
                
            # Infos sur la civilit�
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
            if adresse_auto != None and DICT_INFOS_INDIVIDUS.has_key(adresse_auto) :
                dictTemp["rue_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["rue_resid"]
                dictTemp["cp_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["cp_resid"]
                dictTemp["ville_resid"] = DICT_INFOS_INDIVIDUS[adresse_auto]["ville_resid"]
            
            # Facturation
            totalFacture = decimal.Decimal(str(0.0))
            totalRegle = decimal.Decimal(str(0.0))
            totalSolde = decimal.Decimal(str(0.0))
            key = (dictTemp["IDfamille"], dictTemp["IDindividu"])
            if dictFacturation.has_key(key) :
                totalFacture = decimal.Decimal(str(dictFacturation[key]["prestations"]))
                if totalFacture == None : totalFacture = decimal.Decimal(str(0.0))
                totalRegle = decimal.Decimal(str(dictFacturation[key]["ventilation"]))
                if totalRegle == None : totalRegle = decimal.Decimal(str(0.0))
                totalSolde = totalFacture - totalRegle
            dictTemp["totalFacture"] = totalFacture
            dictTemp["totalRegle"] = totalRegle
            dictTemp["totalSolde"] = totalSolde
            
            # Formatage sous forme de TRACK
            track = Track(dictTemp)
            listeListeView.append(track)

        return listeListeView

    def InitObjectListView(self):
        # Cr�ation du imageList
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
            if montant == None : decimal.Decimal("0.0")
            if montant == decimal.Decimal("0.0") :
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
        self.oddRowsBackColor = wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = "#F0FBED" # Vert
        
        # Filtre des colonnes
        self.SetChampsAffiches(self.listeColonnes)
        
        # Cr�ation des colonnes
        listeColonnes = []
        for dictChamp in LISTE_CHAMPS :
            if dictChamp["afficher"] == True :
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
                # Cr�ation de la colonne
                colonne = ColumnDefn(dictChamp["label"], dictChamp["align"], dictChamp["largeur"], dictChamp["code"], typeDonnee=dictChamp["typeDonnee"], stringConverter=stringConverter, imageGetter=imageGetter)
                listeColonnes.append(colonne)
        self.SetColumns(listeColonnes)
        
        # Regroupement
        if self.regroupement != None :
            self.SetColonneTri(self.regroupement)
            self.SetShowGroups(True)
            self.useExpansionColumn = False
        else:
            self.SetShowGroups(False)
            self.useExpansionColumn = False
            
        self.SetShowItemCounts(True)
        if len(self.columns) > 0 :
            self.SetSortColumn(self.columns[0])
        self.SetEmptyListMsg(_(u"Aucune inscription"))
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
                    
    def MAJ(self, IDindividu=None, IDactivite=None, partis=True, listeGroupes=[], listeCategories=[], regroupement=None, listeColonnes=[], labelParametres=""):
        self.IDactivite = IDactivite
        self.partis = partis
        self.listeGroupes = listeGroupes
        self.listeCategories = listeCategories
        self.regroupement = regroupement
        self.listeColonnes = listeColonnes
        self.labelParametres = labelParametres
        if IDindividu != None :
            self.selectionID = IDindividu
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        attente = wx.BusyInfo(_(u"Recherche des donn�es..."), self)
        self.InitModel()
        self.InitObjectListView()
        attente.Destroy() 
        # S�lection d'un item
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
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        
        menuPop.AppendSeparator()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune fiche famille � ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDindividu = self.Selection()[0].IDindividu
        IDfamille = self.Selection()[0].IDfamille
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDindividu=IDindividu, IDactivite=self.IDactivite, listeGroupes=self.listeGroupes, listeCategories=self.listeCategories, regroupement=self.regroupement, listeColonnes=self.listeColonnes)
        dlg.Destroy()
        
    def Apercu(self, event):
        nbreIndividus = len(self.donnees) 
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des inscriptions"), intro=self.labelParametres, total=_(u"> %d individus") % nbreIndividus, format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        nbreIndividus = len(self.donnees) 
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des inscriptions"), intro=self.labelParametres, total=_(u"> %d individus") % nbreIndividus, format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des inscriptions"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des inscriptions"), autoriseSelections=False)


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



def GetDictFacturation():
    DB = GestionDB.DB()
    
    # R�cup�re les prestations
    req = """SELECT IDfamille, IDindividu, SUM(montant)
    FROM prestations
    WHERE IDactivite=%d
    GROUP BY IDindividu, IDfamille
    ;""" % 1
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    dictPrestations = {}
    for IDfamille, IDindividu, total_prestations in listePrestations :
        dictPrestations[(IDfamille, IDindividu)] = {"prestations":total_prestations, "ventilation":0.0}
    

    # R�cup�re la ventilation
    req = """SELECT IDfamille, IDindividu, SUM(ventilation.montant)
    FROM ventilation
    LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
    WHERE prestations.IDactivite=%d
    GROUP BY IDfamille, IDindividu
    ;""" % 1
    DB.ExecuterReq(req)
    listeVentilations = DB.ResultatReq()
    dictVentilations = {}
    for IDfamille, IDindividu, total_ventilation in listeVentilations :
        dictPrestations[(IDfamille, IDindividu)]["ventilation"] = total_ventilation
    
    DB.Close()

if __name__ == '__main__':
##    GetDictFacturation() 
    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
