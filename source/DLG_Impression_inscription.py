#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import os


import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import CTRL_Bandeau
import CTRL_Choix_modele

import GestionDB
import DATA_Civilites as Civilites
import UTILS_Historique
import UTILS_Identification
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Parametres
import UTILS_Infos_individus

from UTILS_Decimal import FloatToDecimal as FloatToDecimal


DICT_CIVILITES = Civilites.GetDictCivilites()

LISTE_DONNEES = [
    { "nom" : u"Reçu", "champs" : [ 
        { "code" : "numero", "label" : "Numéro"}, 
        { "code" : "date", "label" : "Date d'édition"}, 
        { "code" : "lieu", "label" : "Lieu d'édition"},
        ] },
    { "nom" : u"Destinataire", "champs" : [ 
        { "code" : "nom", "label" : "Nom"}, 
        { "code" : "rue", "label" : "Rue"}, 
        { "code" : "ville", "label" : "CP + Ville"},
        ] },
    { "nom" : u"Organisme", "champs" : [ 
        { "code" : "siret", "label" : "Numéro SIRET"}, 
        { "code" : "ape", "label" : "Code APE"}, 
        ] },
    ]

TEXTE_INTRO = u"Je soussigné{SIGNATAIRE_GENRE} {SIGNATAIRE_NOM}, {SIGNATAIRE_FONCTION}, atteste avoir inscrit pour la famille de {FAMILLE_NOM} l'enfant {INDIVIDU_PRENOM} à l'activité {ACTIVITE_NOM_LONG}."

DICT_DONNEES = {}


def DateComplete(dateDD):
    u""" Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 u"""
    if dateDD == None or dateDD == "" : return ""
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return ""
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    if textDate == None or textDate == "" : return ""
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    if textDate == None or textDate == "" : return ""
    text = str(textDate[6:10]) + "-" + str(textDate[3:5]) + "-" + str(textDate[:2])
    return text

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

def FormateBool(valeur):
    if valeur == 1 or valeur == "1" :
        return "Oui"
    else :
        return "Non"


class CTRL_Signataires(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
    
    def MAJ(self, listeActivites=[] ):
        listeItems, indexDefaut = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        if indexDefaut != None :
            self.Select(indexDefaut)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
        FROM responsables_activite
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        indexDefaut = None
        index = 0
        for IDresponsable, IDactivite, nom, fonction, defaut, sexe in listeDonnees :
            if indexDefaut == None and defaut == 1 : indexDefaut = index
            self.dictDonnees[index] = { 
                "ID" : IDresponsable, "IDactivite" : IDactivite,
                "nom" : nom, "fonction" : fonction,
                "defaut" : defaut, "sexe" : sexe, 
                }
            listeItems.append(nom)
            index += 1
        return listeItems, indexDefaut

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfos(self):
        """ Récupère les infos sur le signataire sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        


# --------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDinscription=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_inscription", style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDinscription = IDinscription
        self.dictSave = {}
        self.listeAdresses = []
        
        # Importation des données
        self.dictInscription = self.Importation()
        self.IDfamille = self.dictInscription["IDFAMILLE"]
                
        # Bandeau
        intro = u"Vous pouvez ici éditer une confirmation d'inscription. Sélectionnez un modèle de document puis cliquez tout simplement sur 'Aperçu' ou sur 'Envoyer Par Email'."
        titre = u"Edition d'une confirmation d'inscription"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, u"Options")
        self.label_modele = wx.StaticText(self, -1, u"Modèle :")
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie="inscription")
        self.bouton_gestion_modeles = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.label_signataire = wx.StaticText(self, -1, u"Signataire :")
        self.ctrl_signataire = CTRL_Signataires(self)
        
        self.label_intro = wx.StaticText(self, -1, u"Intro :")
        self.ctrl_intro = wx.CheckBox(self, -1, u"")
        self.ctrl_intro.SetValue(True)
        self.ctrl_texte_intro = wx.TextCtrl(self, -1, TEXTE_INTRO, style=wx.TE_MULTILINE)
        self.ctrl_texte_intro.SetMinSize((400, 120))
        self.label_tableau = wx.StaticText(self, -1, u"Tableau :")
        self.ctrl_tableau = wx.CheckBox(self, -1, u"Afficher un tableau comportant les caractéristiques de l'inscription")

        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Envoyer_par_email.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Apercu_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_gestion_modeles)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckIntro, self.ctrl_intro)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        # Init contrôles
        self.OnCheckIntro(None) 
        self.ctrl_texte_intro.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="edition_confirmation_inscription", nom="intro", valeur=TEXTE_INTRO))
        self.ctrl_intro.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="edition_confirmation_inscription", nom="check_intro", valeur=True))
        self.ctrl_tableau.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="edition_confirmation_inscription", nom="check_tableau", valeur=True))
        self.OnCheckIntro(None)
        wx.CallLater(0, self.Layout)

    def __set_properties(self):
        self.ctrl_modele.SetToolTipString(u"Selectionnez un modèle de documents")
        self.ctrl_signataire.SetToolTipString(u"Sélectionnez ici le signataire du document")
        self.ctrl_intro.SetToolTipString(u"Cochez cette case pour inclure le texte d'introduction : 'Je soussigné... atteste...' ")
        listeMotsCles = []
        for mot in self.dictInscription.keys() :
            listeMotsCles.append(u"{%s}" % mot)
        self.ctrl_texte_intro.SetToolTipString(u"Vous pouvez modifier ici le texte d'introduction. \n\nVous pouvez utiliser les mots-clés suivants : %s" % ", ".join(listeMotsCles))
        self.ctrl_tableau.SetToolTipString(u"Afficher un tableau comportant les caractéristiques de l'inscription")
        self.bouton_gestion_modeles.SetToolTipString(u"Cliquez ici pour accéder à la gestion des modèles de documents")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_email.SetToolTipString(u"Cliquez ici pour envoyer ce document par Email")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour afficher le PDF")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((570, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        
        # Modèle
        grid_sizer_options.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.Add(self.bouton_gestion_modeles, 0, 0, 0)
        grid_sizer_modele.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_modele, 1, wx.EXPAND, 0)
        
        # Signataire
        grid_sizer_options.Add(self.label_signataire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_signataire, 1, wx.EXPAND, 0)
        
        # Intro
        grid_sizer_options.Add(self.label_intro, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_intro = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_intro.Add(self.ctrl_intro, 0, 0, 0)
        grid_sizer_intro.Add(self.ctrl_texte_intro, 1,wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.AddGrowableCol(1)
        grid_sizer_options.Add(grid_sizer_intro, 1, wx.EXPAND, 0)
        
        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_options, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)

        # Prestations
        grid_sizer_options.Add(self.label_tableau, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_tableau, 1, wx.EXPAND, 0)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
    def OnCheckIntro(self, event):
        if self.ctrl_intro.GetValue() == True :
            self.ctrl_texte_intro.Enable(True)
        else:
            self.ctrl_texte_intro.Enable(False)

    def OnBoutonModeles(self, event): 
        import DLG_Modeles_docs
        dlg = DLG_Modeles_docs.Dialog(self, categorie="inscription")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_modele.MAJ() 
    
    def Importation(self):
        # Récupération des informations sur l'inscription
        dictChamps = {
            "inscriptions.IDinscription" : "IDINSCRIPTION",
            "inscriptions.date_inscription" : "DATE_INSCRIPTION",
            "inscriptions.parti" : "EST_PARTI", 
            
            "activites.IDactivite" : "IDACTIVITE",
            "activites.nom" : "ACTIVITE_NOM_LONG",
            "activites.abrege" : "ACTIVITE_NOM_COURT", 
            
            "groupes.IDgroupe" : "IDGROUPE",
            "groupes.nom" : "GROUPE_NOM_LONG",
            "groupes.abrege" : "GROUPE_NOM_COURT", 
            
            "categories_tarifs.IDcategorie_tarif" : "IDCATEGORIETARIF",
            "categories_tarifs.nom" : "NOM_CATEGORIE_TARIF",
            
            "individus.IDindividu" : "IDINDIVIDU",
            "individus.IDcivilite" : "IDCIVILITE",
            "individus.nom" : "INDIVIDU_NOM",
            "individus.prenom" : "INDIVIDU_PRENOM",
            "individus.date_naiss" : "INDIVIDU_DATE_NAISS",
            "individus.cp_naiss" : "INDIVIDU_CP_NAISS",
            "individus.ville_naiss" : "INDIVIDU_VILLE_NAISS",
            "individus.adresse_auto" : "INDIVIDU_ADRESSE_AUTO",
            "individus.rue_resid" : "INDIVIDU_RUE",
            "individus.cp_resid" : "INDIVIDU_CP",
            "individus.ville_resid" : "INDIVIDU_VILLE",
            "individus.profession" : "INDIVIDU_PROFESSION",
            "individus.employeur" : "INDIVIDU_EMPLOYEUR",
            "individus.tel_domicile" : "INDIVIDU_TEL_DOMICILE",
            "individus.tel_mobile" : "INDIVIDU_TEL_MOBILE",
            "individus.tel_fax" : "INDIVIDU_FAX",
            "individus.mail" : "INDIVIDU_EMAIL",
            "individus.travail_tel" : "INDIVIDU_TEL_PRO",
            "individus.travail_fax" : "INDIVIDU_FAX_PRO",
            "individus.travail_mail" : "INDIVIDU_EMAIL_PRO",
            
            "familles.IDfamille" : "IDFAMILLE",
            "caisses.nom" : "FAMILLE_CAISSE",
            "regimes.nom" : "FAMILLE_REGIME",
            "familles.num_allocataire" : "FAMILLE_NUMALLOC",
            }
        
        listeChamps = dictChamps.keys()
        
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM inscriptions
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN familles ON familles.IDfamille = inscriptions.IDfamille
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
        WHERE IDinscription=%d
        """ % (", ".join(listeChamps), self.IDinscription)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()  
        if len(listeDonnees) == 0 : return None
        
        dictInscription = {}
        index = 0
        for nomChamp in listeChamps :
            code = dictChamps[nomChamp]
            valeur = listeDonnees[0][index]
            dictInscription[code] = valeur
            index += 1

        return dictInscription

    def OnBoutonAnnuler(self, event):
        # Historique
        self.Sauvegarder() 
        # Parametres
        UTILS_Parametres.Parametres(mode="set", categorie="edition_confirmation_inscription", nom="intro", valeur=self.ctrl_texte_intro.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="edition_confirmation_inscription", nom="check_intro", valeur=self.ctrl_intro.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="edition_confirmation_inscription", nom="check_tableau", valeur=self.ctrl_tableau.GetValue())
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide()

    def Sauvegarder(self, demander=True):
        """ Sauvegarder la trace du reçu """
        if len(self.dictSave) == 0 : 
            return
        
        # Demande la confirmation de sauvegarde
        if demander == True :
            dlg = wx.MessageDialog(self, u"Souhaitez-vous mémoriser dans l'historique le document édité ?\n\n(Cliquez NON si c'était juste un test sinon cliquez OUI)", u"Sauvegarde", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
                
        # Mémorisation de l'action dans l'historique
        UTILS_Historique.InsertActions([{
                "IDfamille" : self.IDfamille,
                "IDindividu" : self.IDindividu,
                "IDcategorie" : 34, 
                "action" : u"Edition d'une confirmation d'inscription pour l'activité '%s'" % self.dictSave["activite"],
                },])

    def OnBoutonOk(self, event): 
        self.CreationPDF() 

    def OnBoutonEmail(self, event): 
        """ Envoi par mail """
        import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc="Temp/Inscription.pdf", categorie="inscription", listeAdresses=self.listeAdresses)
    
    def CreationPDF(self, nomDoc="Temp/Inscription.pdf", afficherDoc=True):        
        dictChampsFusion = {}
        
        # Récupération des valeurs de base
        dictDonnees = DICT_DONNEES
        
        # Récupération des infos sur l'organisme
        DB = GestionDB.DB()
        req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        dictOrganisme = {}
        for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees :
            dictOrganisme["nom"] = nom
            dictOrganisme["rue"] = rue
            dictOrganisme["cp"] = cp
            if ville != None : ville = ville.capitalize()
            dictOrganisme["ville"] = ville
            dictOrganisme["tel"] = tel
            dictOrganisme["fax"] = fax
            dictOrganisme["mail"] = mail
            dictOrganisme["site"] = site
            dictOrganisme["num_agrement"] = num_agrement
            dictOrganisme["num_siret"] = num_siret
            dictOrganisme["code_ape"] = code_ape
        DB.Close() 
        
        date_editionDD = datetime.date.today() 
        
        # Adresse
        self.IDindividu = self.dictInscription["IDINDIVIDU"]
        individus = UTILS_Titulaires.GetIndividus() 
        self.dictInscription["INDIVIDU_RUE"] = individus[self.IDindividu]["rue"]
        self.dictInscription["INDIVIDU_CP"] = individus[self.IDindividu]["cp"]
        self.dictInscription["INDIVIDU_VILLE"] = individus[self.IDindividu]["ville"]
        
        # Nom Titulaires
        dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille=[self.IDfamille,])
        self.dictInscription["FAMILLE_NOM"] = dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        
        # Civilité
        dictCivilites = Civilites.GetDictCivilites()
        if self.dictInscription["IDCIVILITE"] == None or self.dictInscription["IDCIVILITE"] == "" :
            IDcivilite = 1
        else :
            IDcivilite = self.dictInscription["IDCIVILITE"]
        self.dictInscription["INDIVIDU_GENRE"] = dictCivilites[IDcivilite]["sexe"]
        self.dictInscription["INDIVIDU_CIVILITE_LONG"]  = dictCivilites[IDcivilite]["civiliteLong"]
        self.dictInscription["INDIVIDU_CIVILITE_COURT"] = dictCivilites[IDcivilite]["civiliteAbrege"] 
        
        # Date de naissance
        if self.dictInscription["INDIVIDU_DATE_NAISS"] == None :
            self.dictInscription["INDIVIDU_AGE"] = None
        else:
            datenaissDD = datetime.date(year=int(self.dictInscription["INDIVIDU_DATE_NAISS"][:4]), month=int(self.dictInscription["INDIVIDU_DATE_NAISS"][5:7]), day=int(self.dictInscription["INDIVIDU_DATE_NAISS"][8:10]))
            datedujour = datetime.date.today()
            age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
            self.dictInscription["INDIVIDU_AGE"] = age

        # Insertion des données de base dans le dictValeurs
        IDfamille = self.IDfamille
        dictValeurs = {
            "IDfamille" : self.IDfamille,
            "{IDFAMILLE}" : str(self.IDfamille),
            
            "{DATE_EDITION}" : DateEngFr(str(date_editionDD)),
            "{DATE_EDITION_LONG}" : DateComplete(date_editionDD),
            "{DATE_EDITION_COURT}" : DateEngFr(str(date_editionDD)),

            "{ORGANISATEUR_NOM}" : dictOrganisme["nom"],
            "{ORGANISATEUR_RUE}" : dictOrganisme["rue"],
            "{ORGANISATEUR_CP}" : dictOrganisme["cp"],
            "{ORGANISATEUR_VILLE}" : dictOrganisme["ville"],
            "{ORGANISATEUR_TEL}" : dictOrganisme["tel"],
            "{ORGANISATEUR_FAX}" : dictOrganisme["fax"],
            "{ORGANISATEUR_MAIL}" : dictOrganisme["mail"],
            "{ORGANISATEUR_SITE}" : dictOrganisme["site"],
            "{ORGANISATEUR_AGREMENT}" : dictOrganisme["num_agrement"],
            "{ORGANISATEUR_SIRET}" : dictOrganisme["num_siret"],
            "{ORGANISATEUR_APE}" : dictOrganisme["code_ape"],
            
            "{IDINSCRIPTION}" : FormateStr(self.dictInscription["IDINSCRIPTION"]),
            "{DATE_INSCRIPTION}" : FormateDate(self.dictInscription["DATE_INSCRIPTION"]),
            "{EST_PARTI}" : FormateBool(self.dictInscription["EST_PARTI"]),
            
            "{IDACTIVITE}" : FormateStr(self.dictInscription["IDACTIVITE"]),
            "{ACTIVITE_NOM_LONG}" : FormateStr(self.dictInscription["ACTIVITE_NOM_LONG"]),
            "{ACTIVITE_NOM_COURT}" : FormateStr(self.dictInscription["ACTIVITE_NOM_COURT"]),
            
            "{IDGROUPE}" : FormateStr(self.dictInscription["IDGROUPE"]),
            "{GROUPE_NOM_LONG}" : FormateStr(self.dictInscription["GROUPE_NOM_LONG"]),
            "{GROUPE_NOM_COURT}" : FormateStr(self.dictInscription["GROUPE_NOM_COURT"]),
            
            "{IDCATEGORIETARIF}" : FormateStr(self.dictInscription["IDCATEGORIETARIF"]),
            "{NOM_CATEGORIE_TARIF}" : FormateStr(self.dictInscription["NOM_CATEGORIE_TARIF"]),
            
            "{IDINDIVIDU}" : FormateStr(self.dictInscription["IDINDIVIDU"]),
            "{INDIVIDU_CIVILITE_LONG}" : FormateStr(self.dictInscription["INDIVIDU_CIVILITE_LONG"]),
            "{INDIVIDU_CIVILITE_COURT}" : FormateStr(self.dictInscription["INDIVIDU_CIVILITE_COURT"]),
            "{INDIVIDU_GENRE}" : FormateStr(self.dictInscription["INDIVIDU_GENRE"]),
            "{INDIVIDU_NOM}" : FormateStr(self.dictInscription["INDIVIDU_NOM"]),
            "{INDIVIDU_PRENOM}" : FormateStr(self.dictInscription["INDIVIDU_PRENOM"]),
            "{INDIVIDU_DATE_NAISS}" : FormateDate(self.dictInscription["INDIVIDU_DATE_NAISS"]),
            "{INDIVIDU_AGE}" : FormateStr(self.dictInscription["INDIVIDU_AGE"]),
            "{INDIVIDU_CP_NAISS}" : FormateStr(self.dictInscription["INDIVIDU_CP_NAISS"]),
            "{INDIVIDU_VILLE_NAISS}" : FormateStr(self.dictInscription["INDIVIDU_VILLE_NAISS"]),
            "{INDIVIDU_RUE}" : FormateStr(self.dictInscription["INDIVIDU_RUE"]),
            "{INDIVIDU_CP}" : FormateStr(self.dictInscription["INDIVIDU_CP"]),
            "{INDIVIDU_VILLE}" : FormateStr(self.dictInscription["INDIVIDU_VILLE"]),
            "{INDIVIDU_PROFESSION}" : FormateStr(self.dictInscription["INDIVIDU_PROFESSION"]),
            "{INDIVIDU_EMPLOYEUR}" : FormateStr(self.dictInscription["INDIVIDU_EMPLOYEUR"]),
            "{INDIVIDU_TEL_DOMICILE}" : FormateStr(self.dictInscription["INDIVIDU_TEL_DOMICILE"]),
            "{INDIVIDU_TEL_MOBILE}" : FormateStr(self.dictInscription["INDIVIDU_TEL_MOBILE"]),
            "{INDIVIDU_FAX}" : FormateStr(self.dictInscription["INDIVIDU_FAX"]),
            "{INDIVIDU_EMAIL}" : FormateStr(self.dictInscription["INDIVIDU_EMAIL"]),
            "{INDIVIDU_TEL_PRO}" : FormateStr(self.dictInscription["INDIVIDU_TEL_PRO"]),
            "{INDIVIDU_FAX_PRO}" : FormateStr(self.dictInscription["INDIVIDU_FAX_PRO"]),
            "{INDIVIDU_EMAIL_PRO}" : FormateStr(self.dictInscription["INDIVIDU_EMAIL_PRO"]),
            
            "{FAMILLE_NOM}" : FormateStr(self.dictInscription["FAMILLE_NOM"]),
            "{FAMILLE_CAISSE}" : FormateStr(self.dictInscription["FAMILLE_CAISSE"]),
            "{FAMILLE_REGIME}" : FormateStr(self.dictInscription["FAMILLE_REGIME"]),
            "{FAMILLE_NUMALLOC}" : FormateStr(self.dictInscription["FAMILLE_NUMALLOC"]),
            }

        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 
        dictValeurs.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))
        dictValeurs.update(self.infosIndividus.GetDictValeurs(mode="individu", ID=self.dictInscription["IDINDIVIDU"], formatChamp=True))

        # Récupération des questionnaires
        Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")
        for dictReponse in Questionnaires.GetDonnees(IDfamille) :
            dictValeurs[dictReponse["champ"]] = dictReponse["reponse"]
            if dictReponse["controle"] == "codebarres" :
                dictValeurs["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

        # Récupération du signataire
        infosSignataire = self.ctrl_signataire.GetInfos()
        if infosSignataire == None :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun signataire !", u"Annulation", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        nomSignataire = infosSignataire["nom"]
        fonctionSignataire = infosSignataire["fonction"]
        sexeSignataire = infosSignataire["sexe"]
        if sexeSignataire == "H" :
            genreSignataire = u""
        else:
            genreSignataire = u"e"
        
        # Récupération et transformation du texte d'intro
        if self.ctrl_intro.GetValue() == True :
            textIntro = self.ctrl_texte_intro.GetValue()         
            textIntro = textIntro.replace("{SIGNATAIRE_GENRE}", genreSignataire)
            textIntro = textIntro.replace("{SIGNATAIRE_NOM}", nomSignataire)
            textIntro = textIntro.replace("{SIGNATAIRE_FONCTION}", fonctionSignataire)
            for key, valeur in dictValeurs.iteritems() :
                if key.startswith("{") :
                    if valeur == None : valeur = ""
                    if type(valeur) == int : valeur = str(valeur)
                    textIntro = textIntro.replace(key, valeur)
            dictValeurs["intro"] = textIntro
        else:
            dictValeurs["intro"] = None

        # Tableau
        dictValeurs["tableau"] = self.ctrl_tableau.GetValue()

        for key, valeur in dictValeurs.iteritems() :
            if valeur == None : valeur = ""
            dictChampsFusion[key] = valeur
                        
        # Préparation des données pour une sauvegarde dans l'historique
        self.dictSave = {}
        self.dictSave["activite"] = self.dictInscription["ACTIVITE_NOM_LONG"]
        self.dictSave["groupe"] = self.dictInscription["GROUPE_NOM_LONG"]
        
        # Récupération du modèle
        IDmodele = self.ctrl_modele.GetID() 
        if IDmodele == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un modèle !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
                
        # Fabrication du PDF
        import UTILS_Impression_inscription
        UTILS_Impression_inscription.Impression(dictValeurs, IDmodele=IDmodele, nomDoc=nomDoc, afficherDoc=afficherDoc)
        
        return dictChampsFusion
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDinscription=1)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
