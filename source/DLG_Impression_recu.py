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
import datetime
import os
import  wx.grid as gridlib

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import CTRL_Bandeau
import CTRL_Choix_modele
import FonctionsPerso

import GestionDB
import DATA_Civilites as Civilites
import UTILS_Historique
import UTILS_Identification
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Infos_individus

from UTILS_Decimal import FloatToDecimal as FloatToDecimal


DICT_CIVILITES = Civilites.GetDictCivilites()

LISTE_DONNEES = [
    { "nom" : _(u"Reçu"), "champs" : [ 
        { "code" : "numero", "label" : "Numéro"}, 
        { "code" : "date", "label" : "Date d'édition"}, 
        { "code" : "lieu", "label" : "Lieu d'édition"},
        ] },
    { "nom" : _(u"Destinataire"), "champs" : [ 
        { "code" : "nom", "label" : "Nom"}, 
        { "code" : "rue", "label" : "Rue"}, 
        { "code" : "ville", "label" : "CP + Ville"},
        ] },
    { "nom" : _(u"Organisme"), "champs" : [ 
        { "code" : "siret", "label" : "Numéro SIRET"}, 
        { "code" : "ape", "label" : "Code APE"}, 
        ] },
    ]

TEXTE_INTRO = _(u"Je soussigné{GENRE} {NOM}, {FONCTION}, certifie avoir reçu pour la famille de {FAMILLE} la somme de {MONTANT}.")

DICT_DONNEES = {}


def DateComplete(dateDD):
    u""" Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 u"""
    if dateDD == None or dateDD == "" : return ""
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
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



class CTRL_Signataires(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, listeActivites=[] ):
        listeItems, indexDefaut = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        if indexDefaut != None :
            self.Select(indexDefaut)
        
        # Recherche le nom de l'utilisateur parmi la liste des signataires
        dictUtilisateur = UTILS_Identification.GetDictUtilisateur()
        for index, dictDonnees in self.dictDonnees.iteritems() :
            if dictUtilisateur != None :
                texte1 = u"%s %s" % (dictUtilisateur["prenom"], dictUtilisateur["nom"])
                texte2 = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
                if dictDonnees["nom"].lower() == texte1.lower() or dictDonnees["nom"].lower() == texte2.lower() :
                    self.SetSelection(index)
                                        
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
            if nom not in listeItems :
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
        
    

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Donnees(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, size=(200, 200), style=wx.WANTS_CHARS)
        self.moveTo = None
        self.SetMinSize((100, 100))
        self.parent = parent
        self.dictCodes = {}
        
        self.MAJ_CTRL_Donnees() 
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        # Calcul du nbre de lignes
        nbreLignes = 0
        for dictCategorie in LISTE_DONNEES :
            nbreLignes += 1
            for dictChamp in dictCategorie["champs"] :
                nbreLignes += 1
        
        # Création de la grille
        self.CreateGrid(nbreLignes, 2)
        self.SetColSize(0, 150)
        self.SetColSize(1, 330)
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.SetColLabelSize(1)
        
        # Remplissage avec les données
        key = 0
        for dictCategorie in LISTE_DONNEES :
            nomCategorie = dictCategorie["nom"]
            
            # Création d'une ligne CATEGORIE
            self.SetRowLabelValue(key, "")
            self.SetCellFont(key, 0, wx.Font(8, wx.DEFAULT , wx.NORMAL, wx.BOLD))
            self.SetCellBackgroundColour(key, 0, "#C5DDFA")
            self.SetReadOnly(key, 0, True)
            self.SetCellValue(key, 0, nomCategorie)
            self.SetCellAlignment(key, 0, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            self.SetCellValue(key, 1, "")
            self.SetCellBackgroundColour(key, 1, "#C5DDFA")
            self.SetReadOnly(key, 1, True)
            self.SetCellSize(key, 0, 1, 2)
            
            key += 1
            
            # Création d'une ligne de données
            for dictChamp in dictCategorie["champs"] :
                code = dictChamp["code"]
                label = dictChamp["label"]
                if DICT_DONNEES.has_key(code):
                    valeur = DICT_DONNEES[code]
                else:
                    valeur = u""
                
                # Entete de ligne
                self.SetRowLabelValue(key, "")
                
                # Création de la cellule LABEL
                self.SetCellValue(key, 0, label)
                self.SetCellBackgroundColour(key, 0, "#EEF4FB")
                self.SetReadOnly(key, 0, True)
                self.SetCellAlignment(key, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellValue(key, 1, valeur)
            
                # Mémorisation dans le dictionnaire des données
                self.dictCodes[key] = code
                key += 1
            
        # test all the events
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        
        self.moveTo = (1, 1)

    def OnCellChange(self, evt):
        # Modification de la valeur dans le dict de données
        numRow = evt.GetRow()
        valeur = self.GetCellValue(numRow, 1)
        code = self.dictCodes[numRow]
        self.SetValeur(code, valeur)
        
    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        evt.Skip()

    def GetValeur(self, code=""):
        if DICT_DONNEES.has_key(code) :
            return DICT_DONNEES[code]
        else:
            return None

    def SetValeur(self, code="", valeur = u""):
        global DICT_DONNEES
        DICT_DONNEES[code] = valeur

    def MAJ_CTRL_Donnees(self):
        """ Importe les valeurs de base dans le GRID Données """
        DB = GestionDB.DB()
        
        # Récupération des infos sur l'attestation
        dateDuJour = str(datetime.date.today())
        self.SetValeur("date", DateEngFr(dateDuJour))
        
        req = """SELECT MAX(numero)
        FROM recus
        ;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        if len(listeDonnees) > 0 : 
            numero = listeDonnees[0][0]
            if numero == None :
                numero = 1
            else:
                numero += 1
        else:
            numero = 0
        self.SetValeur("numero", u"%06d" % numero)
        
        # Récupération des infos sur l'organisme
        req = """SELECT nom, num_siret, code_ape, ville
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        for nom, num_siret, code_ape, ville in listeDonnees :
            if num_siret != None : 
                self.SetValeur("siret", num_siret)
            else :
                self.SetValeur("siret", "")
            if code_ape != None : 
                self.SetValeur("ape", code_ape)
            else :
                self.SetValeur("ape", "")
            if ville != None : 
                self.SetValeur("lieu", ville.capitalize() )
            else :
                self.SetValeur("lieu", "")
        
        # Récupération des données sur le destinataire
        dictNomsTitulaires = UTILS_Titulaires.GetTitulaires([self.parent.IDfamille,]) 
        dictInfosTitulaires = dictNomsTitulaires[self.parent.IDfamille]
        nomsTitulairesAvecCivilite = dictInfosTitulaires["titulairesAvecCivilite"]
        rue_resid = dictInfosTitulaires["adresse"]["rue"]
        cp_resid = dictInfosTitulaires["adresse"]["cp"]
        ville_resid = dictInfosTitulaires["adresse"]["ville"]
        
        if rue_resid == None : rue_resid = u""
        if cp_resid == None : cp_resid = u""
        if ville_resid == None : ville_resid = u""

        self.SetValeur("nom", nomsTitulairesAvecCivilite)
        self.SetValeur("rue", rue_resid)
        self.SetValeur("ville", cp_resid + " " + ville_resid)
        


# --------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDreglement=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_recu", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDreglement = IDreglement
        self.dictSave = {}
        self.listeAdresses = []
        
        # Importation des données
        self.dictReglement = self.Importation()
        self.IDfamille = self.dictReglement["IDfamille"]
                
        # Bandeau
        intro = _(u"Vous pouvez ici éditer un reçu de règlement au format PDF. Pour un reçu standard, cliquez tout simplement sur 'Aperçu' ou sur 'Envoyer Par Email'.")
        titre = _(u"Edition d'un reçu de règlement")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Données
        self.staticbox_donnees_staticbox = wx.StaticBox(self, -1, _(u"Données"))
        self.ctrl_donnees = CTRL_Donnees(self)

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie="reglement")
        self.bouton_gestion_modeles = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.label_signataire = wx.StaticText(self, -1, _(u"Signataire :"))
        self.ctrl_signataire = CTRL_Signataires(self)
        
        self.label_intro = wx.StaticText(self, -1, _(u"Intro :"))
        self.ctrl_intro = wx.CheckBox(self, -1, u"")
        self.ctrl_intro.SetValue(True)
        self.ctrl_texte_intro = wx.TextCtrl(self, -1, TEXTE_INTRO)
        self.label_prestations = wx.StaticText(self, -1, _(u"Prestations :"))
        self.ctrl_prestations = wx.CheckBox(self, -1, _(u"Afficher la liste des prestations payées avec ce règlement"))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

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

    def __set_properties(self):
        self.SetTitle(_(u"Edition d'un reçu de règlement"))
        self.ctrl_donnees.SetToolTipString(_(u"Vous pouvez modifier ici les données de base"))
        self.ctrl_modele.SetToolTipString(_(u"Selectionnez un modèle de documents"))
        self.ctrl_signataire.SetToolTipString(_(u"Sélectionnez ici le signataire du document"))
        self.ctrl_intro.SetToolTipString(_(u"Cochez cette case pour inclure le texte d'introduction : 'Je soussigné... atteste...' "))
        self.ctrl_texte_intro.SetToolTipString(_(u"Vous pouvez modifier ici le texte d'introduction. \n\nUtilisez les mots-clés {GENRE}, {NOM}, {FONCTION}, {ENFANTS}, \n{DATE_DEBUT} et {DATE_FIN} pour inclure dynamiquement les \nvaleurs correspondantes."))
        self.ctrl_prestations.SetToolTipString(_(u"Afficher la liste des prestations payées avec ce règlement"))
        self.bouton_gestion_modeles.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des modèles de documents"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_email.SetToolTipString(_(u"Cliquez ici pour envoyer ce document par Email"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour afficher le PDF"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((570, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Données
        staticbox_donnees = wx.StaticBoxSizer(self.staticbox_donnees_staticbox, wx.VERTICAL)
        staticbox_donnees.Add(self.ctrl_donnees, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_donnees, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=10)
        
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
        grid_sizer_options.Add(self.label_intro, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_intro.Add(self.ctrl_intro, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.Add(self.ctrl_texte_intro, 1,wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.AddGrowableCol(1)
        grid_sizer_options.Add(grid_sizer_intro, 1, wx.EXPAND, 0)
        
        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_options, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)

        # Prestations
        grid_sizer_options.Add(self.label_prestations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_prestations, 1, wx.EXPAND, 0)

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
        dlg = DLG_Modeles_docs.Dialog(self, categorie="reglement")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_modele.MAJ() 
    
    def Importation(self):
        # Récupération des informations sur le règlement
        DB = GestionDB.DB()
        req = """SELECT 
        reglements.IDreglement, 
        reglements.IDcompte_payeur, comptes_payeurs.IDfamille,
        reglements.date, 
        reglements.IDmode, modes_reglements.label, 
        reglements.IDemetteur, emetteurs.nom, 
        reglements.numero_piece, reglements.montant, 
        payeurs.IDpayeur, payeurs.nom, 
        reglements.observations, numero_quittancier, IDprestation_frais, reglements.IDcompte, date_differe, 
        encaissement_attente, 
        date_saisie, IDutilisateur
        FROM reglements
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        WHERE IDreglement=%d
        """ % self.IDreglement
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()  
        if len(listeReglements) == 0 : return None
        
        IDreglement, IDcompte_payeur, IDfamille, date,  IDmode, nomMode, IDemetteur, nomEmetteur, \
        numPiece, montant, IDpayeur, nomPayeur, observations, numQuittancier, \
        IDprestation_frais, IDcompteDepot, date_differe, encaissement_attente, \
        date_saisie, IDutilisateur = listeReglements[0]
        
        dictReglements = {}
        dictReglements["IDreglement"] = IDreglement
        dictReglements["IDcompte_payeur"] = IDcompte_payeur
        dictReglements["IDfamille"] = IDfamille
        dictReglements["dateReglement"] = date
        dictReglements["IDmode"] = IDmode
        dictReglements["nomMode"] = nomMode
        dictReglements["IDemetteur"] = IDemetteur
        dictReglements["nomEmetteur"] = nomEmetteur
        dictReglements["numPiece"] = numPiece
        dictReglements["montant"] = montant
        dictReglements["IDpayeur"] = IDpayeur
        dictReglements["nomPayeur"] = nomPayeur
        dictReglements["observations"] = observations
        dictReglements["numQuittancier"] = numQuittancier
        dictReglements["IDprestation_frais"] = IDprestation_frais
        dictReglements["IDcompteDepot"] = IDcompteDepot
        dictReglements["date_differe"] = date_differe
        dictReglements["encaissement_attente"] = encaissement_attente
        dictReglements["date_saisie"] = date_saisie
        dictReglements["IDutilisateur"] = IDutilisateur
        
        return dictReglements

    def OnBoutonAnnuler(self, event):
        self.Sauvegarder() 
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Rglements1")

    def Sauvegarder(self, demander=True):
        """ Sauvegarder la trace du reçu """
        if len(self.dictSave) == 0 : 
            return
        
        # Demande la confirmation de sauvegarde
        if demander == True :
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous mémoriser le reçu édité ?\n\n(Cliquez NON si c'était juste un test sinon cliquez OUI)"), _(u"Sauvegarde"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Sauvegarde de l'attestation
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("numero", self.dictSave["numero"] ), 
            ("IDfamille", self.dictSave["IDfamille"] ), 
            ("date_edition", self.dictSave["date_edition"] ), 
            ("IDutilisateur", self.dictSave["IDutilisateur"] ), 
            ("IDreglement", self.dictSave["IDreglement"] ), 
            ]
        IDrecu = DB.ReqInsert("recus", listeDonnees)        
        DB.Close()
        
        # Mémorisation de l'action dans l'historique
        UTILS_Historique.InsertActions([{
                "IDfamille" : self.IDfamille,
                "IDcategorie" : 28, 
                "action" : _(u"Edition d'un reçu pour le règlement ID%d") % self.dictSave["IDreglement"],
                },])

    def OnBoutonOk(self, event): 
        self.GetPrestations() 
        self.CreationPDF() 

    def OnBoutonEmail(self, event): 
        """ Envoi par mail """
        import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc="Temp/RECUREGLEMENT.pdf" % FonctionsPerso.GenerationIDdoc(), categorie="recu_reglement", listeAdresses=self.listeAdresses)
    
    def GetPrestations(self):
        DB = GestionDB.DB()
        req = """SELECT prestations.IDprestation, date, categorie, label, 
        activites.IDactivite, activites.nom, activites.abrege,
        individus.nom, individus.prenom,
        prestations.montant, SUM(ventilation.montant) AS total_ventilation
        FROM prestations
        LEFT JOIN ventilation ON ventilation.IDprestation = prestations.IDprestation
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE IDreglement=%d
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date;""" % self.IDreglement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        listePrestations = []
        for IDprestation, date, categorie, label, IDactivite, nomActivite, abregeActivite, nomIndividu, prenomIndividu, montant, ventilation in listeDonnees :
            dateDD = DateEngEnDateDD(date)
            if nomActivite == None : nomActivite = ""
            if abregeActivite == None : abregeActivite = ""
            if prenomIndividu == None : prenomIndividu = u""
            montant = FloatToDecimal(montant)
            ventilation = FloatToDecimal(ventilation)
            dictTemp = {
                "IDprestation" : IDprestation, "date" : dateDD, "categorie" : categorie, "label" : label, "IDactivite" : IDactivite, 
                "nomActivite" : nomActivite, "abregeActivite" : abregeActivite, "prenomIndividu" : prenomIndividu, "montant" : montant, "ventilation" : ventilation,
                }
            listePrestations.append(dictTemp)
        return listePrestations
    

    def CreationPDF(self, nomDoc="Temp/Recu_reglement.pdf", afficherDoc=True):        
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
        
        date_edition = dictDonnees["date"]
        try :
            date_editionDD = DateEngEnDateDD(DateFrEng(date_edition))
        except :
            date_editionDD = ""
                
        # Insertion des données de base dans le dictValeurs
        IDfamille = self.IDfamille
        dictValeurs = {
            "IDfamille" : self.IDfamille,
            "{IDFAMILLE}" : str(self.IDfamille),
            "num_recu" : dictDonnees["numero"],

            "{DATE_EDITION}": dictDonnees["date"],
            "{LIEU_EDITION}" : dictDonnees["lieu"],
            "{DESTINATAIRE_NOM}" : dictDonnees["nom"],
            "{DESTINATAIRE_RUE}" : dictDonnees["rue"],
            "{DESTINATAIRE_VILLE}" : dictDonnees["ville"],
            
            "{NUM_RECU}" : dictDonnees["numero"],
            "{DATE_EDITION}" : date_edition,
            "{DATE_EDITION_LONG}" : DateComplete(date_editionDD),
            "{DATE_EDITION_COURT}" : date_edition,

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
            }

        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 
        dictValeurs.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

        # Récupération des questionnaires
        Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")
        for dictReponse in Questionnaires.GetDonnees(IDfamille) :
            dictValeurs[dictReponse["champ"]] = dictReponse["reponse"]
            if dictReponse["controle"] == "codebarres" :
                dictValeurs["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

        # Récupération du signataire
        infosSignataire = self.ctrl_signataire.GetInfos()
        if infosSignataire == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun signataire !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
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
            textIntro = textIntro.replace("{GENRE}", genreSignataire)
            textIntro = textIntro.replace("{NOM}", nomSignataire)
            textIntro = textIntro.replace("{FONCTION}", fonctionSignataire)
            textIntro = textIntro.replace("{FAMILLE}", dictDonnees["nom"] )
            textIntro = textIntro.replace("{MONTANT}", u"<b>%.2f %s</b>" % (self.dictReglement["montant"], SYMBOLE))
            dictValeurs["intro"] = textIntro
        else:
            dictValeurs["intro"] = None
    
        # Envoi des informations sur le règlement
        for key, valeur in self.dictReglement.iteritems() :
            dictValeurs[key] = valeur
        
        dictValeurs["{IDREGLEMENT}"] = str(dictValeurs["IDreglement"])
        dictValeurs["{DATE_REGLEMENT}"] = DateEngFr(dictValeurs["dateReglement"])
        dictValeurs["{MODE_REGLEMENT}"] = dictValeurs["nomMode"]
        if dictValeurs["nomEmetteur"] != None :
            dictValeurs["{NOM_EMETTEUR}"] = dictValeurs["nomEmetteur"]
        else:
            dictValeurs["{NOM_EMETTEUR}"] = ""
        dictValeurs["{NUM_PIECE}"] = dictValeurs["numPiece"]
        dictValeurs["{MONTANT_REGLEMENT}"] = u"%.2f %s" % (dictValeurs["montant"], SYMBOLE)
        dictValeurs["{NOM_PAYEUR}"] = dictValeurs["nomPayeur"]
        dictValeurs["{NUM_QUITTANCIER}"] = str(dictValeurs["numQuittancier"])
        dictValeurs["{DATE_SAISIE}"] = DateEngFr(dictValeurs["date_saisie"])
        dictValeurs["{OBSERVATIONS}"] = u"%s" % dictValeurs["observations"]
        
        # Récupération liste des prestations
        if self.ctrl_prestations.GetValue() == True :
            dictValeurs["prestations"] = self.GetPrestations() 
        else :
            dictValeurs["prestations"] = []
        
        # Préparation des données pour une sauvegarde de l'attestation
        self.dictSave = {}
        self.dictSave["numero"] = dictDonnees["numero"]
        self.dictSave["IDfamille"] = self.IDfamille
        self.dictSave["date_edition"] = DateFrEng(dictDonnees["date"])
        self.dictSave["IDutilisateur"] = UTILS_Identification.GetIDutilisateur()
        self.dictSave["IDreglement"] = self.IDreglement
        
        # Récupération du modèle
        IDmodele = self.ctrl_modele.GetID() 
        if IDmodele == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        dictChampsFusion["{DATE_EDITION_RECU}"] = DateFrEng(dictDonnees["date"])
        dictChampsFusion["{NUMERO_RECU}"] = dictDonnees["numero"]
        dictChampsFusion["{ID_REGLEMENT}"] = str(dictValeurs["{IDREGLEMENT}"])
        dictChampsFusion["{DATE_REGLEMENT}"] = dictValeurs["{DATE_REGLEMENT}"]
        dictChampsFusion["{MODE_REGLEMENT}"] = dictValeurs["{MODE_REGLEMENT}"]
        dictChampsFusion["{NOM_EMETTEUR}"] = dictValeurs["{NOM_EMETTEUR}"]
        dictChampsFusion["{NUM_PIECE}"] = dictValeurs["{NUM_PIECE}"]
        dictChampsFusion["{MONTANT_REGLEMENT}"] = dictValeurs["{MONTANT_REGLEMENT}"]
        dictChampsFusion["{NOM_PAYEUR}"] = dictValeurs["{NOM_PAYEUR}"]
        dictChampsFusion["{NUM_QUITTANCIER}"] = dictValeurs["{NUM_QUITTANCIER}"]
        dictChampsFusion["{DATE_SAISIE}"] = dictValeurs["{DATE_SAISIE}"]
        
        # Fabrication du PDF
        import UTILS_Impression_recu
        UTILS_Impression_recu.Impression(dictValeurs, IDmodele=IDmodele, nomDoc=nomDoc, afficherDoc=afficherDoc)
        
        return dictChampsFusion
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDreglement=2)
    app.SetTopWindow(dlg)
    dlg.ctrl_prestations.SetValue(True)
    dlg.ShowModal()
    app.MainLoop()
