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
import wx
import CTRL_Bouton_image
import wx.lib.colourselect as csel
import wx.richtext as rt
import sys
import copy
import datetime
import cStringIO
import os
import wx.lib.agw.hyperlink as Hyperlink

import FonctionsPerso
import GestionDB
from Utils import UTILS_Identification


CATEGORIES = [
    ("saisie_libre", _(u"Saisie libre")),
    ("releve_prestations", _(u"Relevé des prestations")),
    ("reglement", _(u"Règlement")),
    ("recu_reglement", _(u"Reçu de règlement")),
    ("recu_don_oeuvres", _(u"Reçu de don aux oeuvres")),
    ("facture", _(u"Facture")),
    ("rappel", _(u"Rappel")),
    ("attestation_presence", _(u"Attestation de présence")), 
    ("attestation_fiscale", _(u"Attestation fiscale")), 
    ("reservations", _(u"Liste des réservations")), 
    ("cotisation", _(u"Cotisation")),
    ("rappel_pieces_manquantes", _(u"Rappel pièces manquantes")),
    ("portail", _(u"Rappel des données du compte internet")),
    ("portail_demande_inscription", _(u"Portail - Demande d'une inscription")),
    ("portail_demande_reservation", _(u"Portail - Demande d'une réservation")),
    ("portail_demande_facture", _(u"Portail - Demande d'une facture")),
    ("portail_demande_recu_reglement", _(u"Portail - Demande d'un reçu de règlement")),
    ]


MOTSCLES_STANDARDS = [
                ( "{UTILISATEUR_NOM_COMPLET}", _(u"Nom complet de l'utilisateur") ),
                ( "{UTILISATEUR_NOM}", _(u"Nom de famille de l'utilisateur") ),
                ( "{UTILISATEUR_PRENOM}", _(u"Prénom de l'utilisateur") ),
                ( "{DATE_COURTE}", _(u"Date du jour courte") ),
                ( "{DATE_LONGUE}", _(u"Date du jour longue") ),
                ]
    
MOTSCLES = {
    
    "saisie_libre" : [
                ],
    
    "releve_prestations" : [
                ( "{DATE_EDITION_RELEVE}", _(u"Date de l'édition du relevé") ),
                ( "{RESTE_DU}", _(u"Reste dû indiqué par le relevé") ),
                ],

    "reglement" : [
                ( "{ID_REGLEMENT}", _(u"ID du règlement") ),
                ( "{DATE_REGLEMENT}", _(u"Date du règlement") ),
                ( "{MODE_REGLEMENT}", _(u"Mode de règlement") ),
                ( "{NOM_EMETTEUR}", _(u"Nom de l'émetteur") ),
                ( "{NUM_PIECE}", _(u"Numéro de la pièce") ),
                ( "{MONTANT_REGLEMENT}", _(u"Montant du règlement") ),
                ( "{NOM_PAYEUR}", _(u"Nom du payeur") ),
                ( "{NUM_QUITTANCIER}", _(u"Numéro de quittancier") ),
                ( "{DATE_SAISIE}", _(u"Date de saisie du règlement") ),
                ],

    "recu_reglement" : [
                ( "{DATE_EDITION_RECU}", _(u"Date d'édition du reçu") ),
                ( "{NUMERO_RECU}", _(u"Numéro du reçu") ),
                ( "{ID_REGLEMENT}", _(u"ID du règlement") ),
                ( "{DATE_REGLEMENT}", _(u"Date du règlement") ),
                ( "{MODE_REGLEMENT}", _(u"Mode de règlement") ),
                ( "{NOM_EMETTEUR}", _(u"Nom de l'émetteur") ),
                ( "{NUM_PIECE}", _(u"Numéro de la pièce") ),
                ( "{MONTANT_REGLEMENT}", _(u"Montant du règlement") ),
                ( "{NOM_PAYEUR}", _(u"Nom du payeur") ),
                ( "{NUM_QUITTANCIER}", _(u"Numéro de quittancier") ),
                ( "{DATE_SAISIE}", _(u"Date de saisie du règlement") ),
                ],

    "recu_don_oeuvres" : [
                ( "{DATE_EDITION}", _(u"Date d'édition du reçu") ),
                ( "{NUMERO_RECU}", _(u"Numéro du reçu") ),
                ( "{NOM_DONATEUR}", _(u"Nom du donateur") ),
                ( "{ADRESSE_DONATEUR}", _(u"Adresse du donateur") ),
                ( "{DATE_REGLEMENT}", _(u"Date du règlement") ),
                ( "{MODE_REGLEMENT}", _(u"Mode du règlement") ),
                ( "{MONTANT_CHIFFRES}", _(u"Montant en chiffres") ),
                ( "{MONTANT_LETTRES}", _(u"Montant en lettres") ),
                ],

    "facture" : [
                ( "{DATE_EDITION_FACTURE}", _(u"Date d'édition de la facture") ),
                ( "{NUMERO_FACTURE}", _(u"Numéro de facture") ),
                ( "{DATE_DEBUT}", _(u"Date de début de la période de facturation") ),
                ( "{DATE_FIN}", _(u"Date de fin de la période de facturation") ),
                ( "{DATE_ECHEANCE}", _(u"Date d'échance du règlement") ),
                ( "{SOLDE}", _(u"Solde de la facture") ),
                ( "{SOLDE_AVEC_REPORTS}", _(u"Solde de la facture (reports inclus)") ),
                ],

    "rappel" : [
                ( "{DATE_EDITION_RAPPEL}", _(u"Date d'édition de la lettre de rappel") ),
                ( "{NUMERO_RAPPEL}", _(u"Numéro de le lattre de rappel") ),
                ( "{DATE_MIN}", _(u"Date de début des impayés") ),
                ( "{DATE_MAX}", _(u"Date de fin des impayés") ),
                ( "{DATE_REFERENCE}", _(u"Date de référence") ),
                ( "{SOLDE_CHIFFRES}", _(u"Solde du rappel en chiffres") ),
                ( "{SOLDE_LETTRES}", _(u"Solde du rappel en lettres") ),
                ],

    "attestation_presence" : [
                ( "{DATE_EDITION_ATTESTATION}", _(u"Date d'édition de l'attestation") ),
                ( "{NUMERO_ATTESTATION}", _(u"Numéro de l'attestation") ),
                ( "{DATE_DEBUT}", _(u"Date de début de la période") ),
                ( "{DATE_FIN}", _(u"Date de fin de la période") ),
                ( "{INDIVIDUS_CONCERNES}", _(u"Liste des individus concernés") ),
                ( "{SOLDE}", _(u"Solde de l'attestation") ),
                ],

    "reservations" : [
                ( "{SOLDE}", _(u"Solde du document") ),
                ],

    "mandat_sepa" : [
                ( "{REFERENCE_UNIQUE_MANDAT}", _(u"RUM (Référence Unique du Mandat)") ),
                ( "{DATE_SIGNATURE}", _(u"Date de signature du mandat") ),
                ],

    "cotisation" : [
                ( "{NUMERO_CARTE}", _(u"Numéro de la carte") ),
                ( "{DATE_DEBUT}", _(u"Date de début de validité de la cotisation") ),
                ( "{DATE_FIN}", _(u"Date de fin de validité de la cotisation") ),
                ( "{NOM_TYPE_COTISATION}", _(u"Nom du type de cotisation") ),
                ( "{NOM_UNITE_COTISATION}", _(u"Nom de l'unité de cotisation") ),
                ( "{NOM_COTISATION}", _(u"Nom de la cotisation (type + unité)") ),
                ( "{DATE_CREATION_CARTE}", _(u"Date de création de la carte") ),
                ( "{MONTANT_FACTURE}", _(u"Montant facturé") ),
                ( "{MONTANT_REGLE}", _(u"Montant réglé") ),
                ( "{SOLDE_ACTUEL}", _(u"Solde actuel") ),
                ( "{ACTIVITES}", _(u"Activités associées") ),
                ( "{NOTES}", _(u"Notes") ),
                ],

    "attestation_fiscale" : [
                ("{DATE_EDITION_COURT}", _(u"Date d'édition court")),
                ("{DATE_EDITION_LONG}", _(u"Date d'édition long")),
                ("{DATE_DEBUT}", _(u"Date de début de la période")),
                ("{DATE_FIN}", _(u"Date de fin de la période")),
                ("{MONTANT_FACTURE}", _(u"Montant total facturé")),
                ("{MONTANT_REGLE}", _(u"Montant réglé")),
                ("{MONTANT_IMPAYE}", _(u"Montant impayé")),
                ("{MONTANT_FACTURE_LETTRES}", _(u"Montant total facturé en lettres")),
                ("{MONTANT_REGLE_LETTRES}", _(u"Montant réglé en lettres")),
                ("{MONTANT_IMPAYE_LETTRES}", _(u"Montant impayé en lettres")),
                ],

    "rappel_pieces_manquantes" : [
                ("{NOM_FAMILLE}", _(u"Nom de la famille")),
                ("{LISTE_PIECES_MANQUANTES}", _(u"Liste des pièces manquantes")),
                ],

    "portail" : [
                ( "{NOM_FAMILLE}", _(u"Nom de la famille")),
                ( "{IDENTIFIANT_INTERNET}", _(u"Identifiant du compte internet") ),
                ( "{MOTDEPASSE_INTERNET}", _(u"Mot de passe du compte internet") ),
                ],

    "portail_demande_inscription" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"Réponse à la demande") ),
                ],

    "portail_demande_reservation" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"Réponse à la demande") ),
                ( "{PERIODE_NOM}", _(u"Nom de la période") ),
                ( "{PERIODE_DATE_DEBUT}", _(u"Date de début de la période") ),
                ( "{PERIODE_DATE_FIN}", _(u"Date de fin de la période") ),
                ( "{SOLDE}", _(u"Solde du document") ),
                ],

    "portail_demande_facture" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"Réponse à la demande") ),
                ],

    "portail_demande_recu_reglement" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"Réponse à la demande") ),
                ],

    }




def GetMotscles(categorie=""):
    listeTemp = copy.deepcopy(MOTSCLES_STANDARDS)
    if MOTSCLES.has_key(categorie) :
        listeTemp.extend(MOTSCLES[categorie])
    return listeTemp

def GetChampsStandards():
    dictTemp  = {}
    
    # Utilisateur en cours
    dictUtilisateur = UTILS_Identification.GetDictUtilisateur()
    if dictUtilisateur != None :
        dictTemp["{UTILISATEUR_NOM_COMPLET}"] = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
        dictTemp["{UTILISATEUR_NOM}"] = dictUtilisateur["nom"]
        dictTemp["{UTILISATEUR_PRENOM}"] = dictUtilisateur["prenom"]
    
    # Dates
    dictTemp["{DATE_COURTE}"] = DateEngFr(str(datetime.date.today()))
    dictTemp["{DATE_LONGUE}"] = DateComplete(datetime.date.today())
    
    
    return dictTemp
        
    
    
# ------------------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, label="", infobulle=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id=-1, label=label, URL="")
        self.parent = parent
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        self.UpdateLink()
        
        


class Hyperlien_inserer_motcle(Hyperlien):
    def __init__(self, parent, label="", infobulle="", listeMotscles=[], editeur=None):
        Hyperlien.__init__(self, parent, label=label, infobulle=infobulle)
        self.parent = parent
        self.listeMotscles = listeMotscles
        self.editeur = editeur

    def OnLeftLink(self, event):
        menuPop = wx.Menu()
        id = 10000
        for motcle in self.listeMotscles :
            menuPop.AppendItem(wx.MenuItem(menuPop, id, motcle))
            self.Bind(wx.EVT_MENU, self.InsererMotcle, id=id)
            id += 1
        self.PopupMenu(menuPop)
        menuPop.Destroy()
        self.UpdateLink()
        
    def InsererMotcle(self, event):
        motcle = self.listeMotscles[10000 - event.GetId() ]
        self.editeur.EcritTexte(motcle)


class Hyperlien_inserer_modele(Hyperlien):
    def __init__(self, parent, label="", infobulle="", categorie="", editeur=None):
        Hyperlien.__init__(self, parent, label=label, infobulle=infobulle)
        self.parent = parent
        self.categorie = categorie
        self.editeur = editeur

    def OnLeftLink(self, event):
        # Récupération des modèles
        DB = GestionDB.DB()
        req = """SELECT IDmodele, categorie, nom, description, objet, texte_xml, IDadresse, defaut
        FROM modeles_emails
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Création du menu contextuel
        menuPop = wx.Menu()
        id = 10000
        for IDmodele, categorie, nom, description, objet, texte_xml, IDadresse, defaut in self.listeMotscles :
            menuPop.AppendItem(wx.MenuItem(menuPop, id, nom))
            self.Bind(wx.EVT_MENU, self.InsererMotcle, id=id)
            id += 1
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def InsererMotcle(self, event):
        motcle = self.listeMotscles[10000 - event.GetId() ]
        self.editeur.EcritTexte(motcle)



def FormateCouleur(texte):
    pos1 = texte.index(",")
    pos2 = texte.index(",", pos1+1)
    r = int(texte[1:pos1])
    v = int(texte[pos1+2:pos2])
    b = int(texte[pos2+2:-1])
    return (r, v, b)

def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete


ID_SAUVEGARDER = wx.NewId()
ID_OUVRIR = wx.NewId()
ID_IMPRIMER = wx.NewId()
ID_APERCU = wx.NewId()
ID_GRAS = wx.NewId()
ID_ITALIQUE = wx.NewId()
ID_SOULIGNE = wx.NewId()
ID_COULEUR_POLICE = wx.NewId()
ID_ALIGNER_GAUCHE = wx.NewId()
ID_ALIGNER_CENTRE = wx.NewId()
ID_ALIGNER_DROIT = wx.NewId()
ID_RETRAIT_GAUCHE = wx.NewId()
ID_RETRAIT_DROIT = wx.NewId()
ID_PARA_MOINS = wx.NewId()
ID_PARA_PLUS = wx.NewId()
ID_INTER_SIMPLE = wx.NewId()
ID_INTER_DEMI = wx.NewId()
ID_INTER_DOUBLE = wx.NewId()
ID_URL = wx.NewId()
ID_IMAGE = wx.NewId()
ID_GOMME = wx.NewId()


class CTRL_Expediteur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
                                        
    def MAJ(self):
        selectionActuelle = self.GetID() 
        self.listeAdresses = []
        self.dictAdresses = {}
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        sel = None
        index = 0
        for IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS in listeDonnees :
            self.listeAdresses.append(adresse)
            self.dictAdresses[index] = {"IDadresse" : IDadresse, "adresse": adresse, "smtp" : smtp, "port" : port, "defaut" : defaut, "auth" : connexionAuthentifiee, "startTLS":startTLS, "motdepasse" : motdepasse}
            if defaut == 1 : 
                sel = index
            index += 1
        self.SetItems(self.listeAdresses)
        if sel != None : 
            self.SetSelection(sel)
        if selectionActuelle != None :
            self.SetSelection(selectionActuelle)
        if len(self.listeAdresses) == 0 :
            self.Enable(False)

    def SetID(self, ID=0):
        for index, values in self.dictAdresses.iteritems():
            if values["IDadresse"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictAdresses[index]["IDadresse"]
    
    def GetDonnees(self):
        if self.GetID() == None :
            return None
        else :
            return self.dictAdresses[self.GetSelection()]


class Panel_Expediteur(wx.Panel):
    def __init__(self, parent, size=(-1, -1)):
        wx.Panel.__init__(self, parent, id=-1, size=size, style=wx.TAB_TRAVERSAL)
        
        # Contrôles
        self.ctrl_exp = CTRL_Expediteur(self)
        self.bouton_exp = self.bouton_exp = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        # Propriétés
        self.ctrl_exp.SetToolTipString(_(u"Sélectionnez l'adresse d'expéditeur"))
        self.bouton_exp.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des adresses d'expédition"))
        
        # Layout
        grid_sizer = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_exp, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.bouton_exp, 0, wx.EXPAND, 0)
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
        self.Layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExp, self.bouton_exp)
        
    def OnBoutonExp(self, event): 
        from Dlg import DLG_Emails_exp
        dlg = DLG_Emails_exp.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_exp.MAJ() 
    
    def MAJ(self):
        self.ctrl_exp.MAJ() 
        
    def SetID(self, ID=0):
        self.ctrl_exp.SetID(ID)

    def GetID(self):
        return self.ctrl_exp.GetID()
    
    def GetDonnees(self):
        return self.ctrl_exp.GetDonnees()


# --------------------------------------------------------------------------------------------------------------------------------------------------------



class BarreOutils1(wx.ToolBar):
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.parent = parent
        
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        doBind( self.AddTool(ID_SAUVEGARDER, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/sauvegarder.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Sauvegarder le texte")), self.parent.OnFileSave)
        doBind( self.AddTool(ID_OUVRIR, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/ouvrir.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Ouvrir un texte sauvegardé")), self.parent.OnFileOpen)
        self.AddSeparator()
        doBind( self.AddTool(ID_IMPRIMER, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/imprimer.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Imprimer ce texte")), self.parent.OnPrint)
        doBind( self.AddTool(ID_APERCU, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/Apercu.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Aperçu avant impression de ce texte")), self.parent.OnPreview)
        self.AddSeparator()
        doBind( self.AddTool(ID_ALIGNER_GAUCHE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/aligner_gauche.png"), wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Aligner à gauche")), self.parent.OnAlignLeft, self.parent.OnUpdateAlignLeft)
        doBind( self.AddTool(ID_ALIGNER_CENTRE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/aligner_centre.png"), wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Centrer")), self.parent.OnAlignCenter, self.parent.OnUpdateAlignCenter)
        doBind( self.AddTool(ID_ALIGNER_DROIT, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/aligner_droit.png"), wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Aligner à droite")), self.parent.OnAlignRight, self.parent.OnUpdateAlignRight)
        self.AddSeparator()
        doBind( self.AddTool(ID_GRAS, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/gras.png"), wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Gras")), self.parent.OnBold, self.parent.OnUpdateBold)
        doBind( self.AddTool(ID_ITALIQUE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/italique.png"), wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Italique")), self.parent.OnItalic, self.parent.OnUpdateItalic)
        doBind( self.AddTool(ID_SOULIGNE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/souligne.png"), wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Souligné")), self.parent.OnUnderline, self.parent.OnUpdateUnderline)
        self.AddSeparator()
        doBind( self.AddTool(ID_COULEUR_POLICE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/police_couleur.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Couleur de la police")), self.parent.OnColour)
        self.AddSeparator()
        doBind( self.AddTool(wx.ID_UNDO, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/annuler.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Annuler")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        doBind( self.AddTool(wx.ID_REDO, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/repeter.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Répéter")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        self.AddSeparator()
        doBind( self.AddTool(ID_GOMME, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Effacer tout le texte")), self.parent.OnGomme)

        self.SetToolBitmapSize((16, 16))
        self.Realize()


class BarreOutils2(wx.ToolBar):
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.parent = parent
        
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        doBind( self.AddTool(wx.ID_CUT, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/couper.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Couper")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        doBind( self.AddTool(wx.ID_COPY, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/copier.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Copier")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        doBind( self.AddTool(wx.ID_PASTE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/coller.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Coller")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        self.AddSeparator()
        doBind( self.AddTool(ID_RETRAIT_GAUCHE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/retrait_gauche.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Diminuer le retrait")), self.parent.OnIndentLess)
        doBind( self.AddTool(ID_RETRAIT_DROIT, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/retrait_droit.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Augmenter le retrait")), self.parent.OnIndentMore)
        self.AddSeparator()
        doBind( self.AddTool(ID_PARA_MOINS, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/espaceParagrapheMoins.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Diminuer l'espacement des paragraphes")), self.parent.OnParagraphSpacingLess)
        doBind( self.AddTool(ID_PARA_PLUS, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/espaceParagraphePlus.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Augmenter l'espacement des paragraphes")), self.parent.OnParagraphSpacingMore)
        self.AddSeparator()
        doBind( self.AddTool(ID_INTER_SIMPLE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/interligne_simple.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Interligne simple")), self.parent.OnLineSpacingSingle)
        doBind( self.AddTool(ID_INTER_DEMI, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/interligne_demi.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Interligne 1.5")), self.parent.OnLineSpacingHalf)
        doBind( self.AddTool(ID_INTER_DOUBLE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/interligne_double.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Interligne double")), self.parent.OnLineSpacingDouble)
        
        self.AddSeparator()
        doBind( self.AddTool(ID_URL, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/url.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Insérer une url")), self.parent.OnInsererURL)
        doBind( self.AddTool(ID_IMAGE, wx.Bitmap(Chemins.GetStaticPath("Images/Teamword/importer_image.png"), wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Insérer une image")), self.parent.OnImporterImage)

        self.SetToolBitmapSize((16, 16))
        self.Realize()

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Editeur(rt.RichTextCtrl):
    def __init__(self, parent, id=-1, style=wx.VSCROLL|wx.HSCROLL|wx.WANTS_CHARS ):
        rt.RichTextCtrl.__init__(self, parent, id=id, style=style)

    def GetXML(self):
        out = cStringIO.StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.GetBuffer()
        handler.SaveStream(buffer, out)
        out.seek(0)
        content = out.read()
        return content
    
    def SetXML(self, texteXml=""):
        out = cStringIO.StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.GetBuffer()
        buffer.AddHandler(handler)
        out.write(texteXml.encode("utf8"))
        out.seek(0)
        handler.LoadStream(buffer, out)
        self.Refresh()


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, size=(-1, -1)):
        wx.Panel.__init__(self, parent, id=-1, size=size, style=wx.TAB_TRAVERSAL)
        
        # Contrôles
        self.barre_outils1 = BarreOutils1(self)
        self.barre_outils2 = BarreOutils2(self)
        self.AddRTCHandlers()
        self.ctrl_editeur = Editeur(self)

        # Layout
        grid_sizer = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer.Add(self.barre_outils1, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.barre_outils2, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.ctrl_editeur, 0, wx.EXPAND, 0)
        grid_sizer.AddGrowableRow(2)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
        self.Layout()


    def OnFileOpen(self, evt):
        """ Ouvrir un texte """
        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
        dlg = wx.FileDialog(self, _(u"Choisissez un fichier à ouvrir"), wildcard=wildcard, style=wx.OPEN)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                fileType = types[dlg.GetFilterIndex()]
                self.ctrl_editeur.LoadFile(path, type=wx.richtext.RICHTEXT_TYPE_ANY)
                wx.CallAfter(self.ctrl_editeur.SetFocus)
        dlg.Destroy()

    def OnFileSave(self, evt):
        """ Sauvegarder dans un fichier """
        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)
        dlg = wx.FileDialog(self, _(u"Sauvegardez le texte"), wildcard=wildcard, style=wx.SAVE)
        dlg.SetFilterIndex(3)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            if cheminFichier :
                fileType = types[dlg.GetFilterIndex()]
                ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
                if not cheminFichier.endswith(ext):
                    cheminFichier += '.' + ext
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False            
        self.ctrl_editeur.SaveFile(cheminFichier, wx.richtext.RICHTEXT_TYPE_ANY)

    def OnPreview(self, event):
        xml = self.GetXML()
        printout1 = wx.richtext.RichTextPrintout()
        printout1.SetRichTextBuffer(self.ctrl_editeur.GetBuffer()) 
        printout2 = wx.richtext.RichTextPrintout()
        printout2.SetRichTextBuffer(self.ctrl_editeur.GetBuffer()) 
        data = wx.PrintDialogData() 
        data.SetAllPages(True)
        data.SetCollate(True) # Pour assembler les pages
        # définit les paramètres de l'impression
        datapr = wx.PrintData()
        data.SetPrintData(datapr)
        # Impression
        preview = wx.PrintPreview(printout1, printout2, data)
        if not preview.Ok():
            print "Probleme dans le preview du richTextCtrl."
            return
        
        from Utils import UTILS_Printer
        pfrm = UTILS_Printer.FramePreview(self, _(u"Aperçu avant impression"), preview)
        pfrm.SetPosition(self.GetPosition())
        pfrm.SetSize(self.GetSize())
        pfrm.Show(True)     
        # Pour éviter le bug des marges qui se rajoutent après l'aperçu
        self.SetXML(xml)  
            
    def OnPrint(self, event):
        xml = self.GetXML()
        printout = wx.richtext.RichTextPrintout() #wx.html.HtmlPrintout() 
        printout.SetRichTextBuffer(self.ctrl_editeur.GetBuffer()) 
        data = wx.PrintDialogData() 
        data.SetAllPages(True)
        data.SetCollate(True) # Pour assembler les pages
        # définit les paramètres de l'impression
        datapr = wx.PrintData()
        data.SetPrintData(datapr)
        # Impression
        printer = wx.Printer(data) 
        printer.Print(self, printout, True) 
        # Pour éviter le bug des marges qui se rajoutent après l'aperçu
        self.SetXML(xml)  

    def OnBold(self, evt):
        self.ctrl_editeur.ApplyBoldToSelection()
        
    def OnItalic(self, evt): 
        self.ctrl_editeur.ApplyItalicToSelection()
        
    def OnUnderline(self, evt):
        self.ctrl_editeur.ApplyUnderlineToSelection()
        
    def OnAlignLeft(self, evt):
        self.ctrl_editeur.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_LEFT)
        
    def OnAlignRight(self, evt):
        self.ctrl_editeur.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_RIGHT)
        
    def OnAlignCenter(self, evt):
        self.ctrl_editeur.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_CENTRE)
        
    def OnIndentMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.ctrl_editeur.SetStyle(r, attr)
        
    def OnIndentLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.ctrl_editeur.SetStyle(r, attr)
        
    def OnParagraphSpacingMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
            self.ctrl_editeur.SetStyle(r, attr)
        
    def OnParagraphSpacingLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
                self.ctrl_editeur.SetStyle(r, attr)
        
    def OnLineSpacingSingle(self, evt): 
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.ctrl_editeur.SetStyle(r, attr)
                
    def OnLineSpacingHalf(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.ctrl_editeur.SetStyle(r, attr)
        
    def OnLineSpacingDouble(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.ctrl_editeur.GetInsertionPoint()
        if self.ctrl_editeur.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_editeur.HasSelection():
                r = self.ctrl_editeur.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.ctrl_editeur.SetStyle(r, attr)

    def OnFont(self, evt):
        if not self.ctrl_editeur.HasSelection():
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un texte."), _(u"Police"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        r = self.ctrl_editeur.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_FONT)
        if self.ctrl_editeur.GetStyle(self.ctrl_editeur.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(wx.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.ctrl_editeur.SetStyle(r, attr)
        dlg.Destroy()

    def OnColour(self, evt):
        colourData = wx.ColourData()
        attr = rt.RichTextAttr() #wx.TextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        if self.ctrl_editeur.GetStyle(self.ctrl_editeur.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.ctrl_editeur.HasSelection():
                    self.ctrl_editeur.BeginTextColour(colour)
                else:
                    r = self.ctrl_editeur.GetSelectionRange()
                    attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.ctrl_editeur.SetStyle(r, attr)
        dlg.Destroy()

    def OnUpdateBold(self, evt):
        if self.ctrl_editeur == None : return
        evt.Check(self.ctrl_editeur.IsSelectionBold())
    
    def OnUpdateItalic(self, evt):
        if self.ctrl_editeur == None : return
        evt.Check(self.ctrl_editeur.IsSelectionItalics())
    
    def OnUpdateUnderline(self, evt): 
        if self.ctrl_editeur == None : return
        evt.Check(self.ctrl_editeur.IsSelectionUnderlined())
    
    def OnUpdateAlignLeft(self, evt):
        if self.ctrl_editeur == None : return
        evt.Check(self.ctrl_editeur.IsSelectionAligned(wx.TEXT_ALIGNMENT_LEFT))
        
    def OnUpdateAlignCenter(self, evt):
        if self.ctrl_editeur == None : return
        evt.Check(self.ctrl_editeur.IsSelectionAligned(wx.TEXT_ALIGNMENT_CENTRE))
        
    def OnUpdateAlignRight(self, evt):
        if self.ctrl_editeur == None : return
        evt.Check(self.ctrl_editeur.IsSelectionAligned(wx.TEXT_ALIGNMENT_RIGHT))
    
    def ForwardEvent(self, evt):
        if self.ctrl_editeur == None : return
        self.ctrl_editeur.ProcessEvent(evt)
    
    def OnGomme(self, event):
        self.ctrl_editeur.Clear()
        self.ctrl_editeur.SetFocus()
        
    def OnInsererURL(self, event):
        from Dlg import DLG_Saisie_url
        dlg = DLG_Saisie_url.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetLabel()
            URL = dlg.GetURL()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        urlStyle = rt.RichTextAttr()
        urlStyle.SetTextColour(wx.BLUE)
        urlStyle.SetFontUnderlined(True)
        self.ctrl_editeur.BeginStyle(urlStyle)
        self.ctrl_editeur.BeginURL(URL)
        self.ctrl_editeur.WriteText(label)
        self.ctrl_editeur.EndURL()
        self.ctrl_editeur.EndStyle()

    def OnImporterImage(self, event):
        # Sélection d'une image
        self.repCourant = os.getcwd()
        wildcard = "Toutes les images|*.jpg;*.png;*.gif|" \
                        "Images JPEG (*.jpg)|*.jpg|"     \
                        "Images PNG (*.png)|*.png|"     \
                        "Images GIF (*.gif)|*.gif|"     \
                        "Tous les fichiers (*.*)|*.*"
        # Récupération du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture de la fenêtre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une image"),
            defaultDir=cheminDefaut, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # Recadre la photo
        bmp = wx.Bitmap(Chemins.GetStaticPath(nomFichierLong), wx.BITMAP_TYPE_ANY)
##        from Dlg import DLG_Editeur_photo_2
##        dlg = DLG_Editeur_photo_2.MyDialog(self, image=nomFichierLong, titre=_(u"Redimensionnez l'image si vous le souhaitez"))
##        if dlg.ShowModal() == wx.ID_OK:
##            bmp = dlg.GetBmp()
##            dlg.Destroy()
##        else:
##            dlg.Destroy()
##            return 
        # Insère l'image dans l'éditeur
        if nomFichierLong.lower().endswith(".jpg") : typeBMP = wx.BITMAP_TYPE_JPEG
        if nomFichierLong.lower().endswith(".png") : typeBMP = wx.BITMAP_TYPE_PNG
        if nomFichierLong.lower().endswith(".gif") : typeBMP = wx.BITMAP_TYPE_GIF
        self.ctrl_editeur.WriteBitmap(bmp, bitmapType=typeBMP)

    def AddRTCHandlers(self):
        # make sure we haven't already added them.
        if rt.RichTextBuffer.FindHandlerByType(rt.RICHTEXT_TYPE_HTML) is not None:
            return
        # This would normally go in your app's OnInit method.  I'm
        # not sure why these file handlers are not loaded by
        # default by the C++ richtext code, I guess it's so you
        # can change the name or extension if you wanted...
        rt.RichTextBuffer.AddHandler(rt.RichTextHTMLHandler())
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler())
        # ...like this
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler(name="Noetext", ext="ntx", type=99))
        # This is needed for the view as HTML option since we tell it
        # to store the images in the memory file system.
        wx.FileSystem.AddHandler(wx.MemoryFSHandler())

    def OnFileViewHTML(self):
        # Get an instance of the html file handler, use it to save the
        # document to a StringIO stream, and then display the
        # resulting html text in a dialog with a HtmlWindow.
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])

        import cStringIO
        stream = cStringIO.StringIO()
        if not handler.SaveStream(self.ctrl_editeur.GetBuffer(), stream):
            return
        
        source = stream.getvalue()
        head = """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
</head>
        """
        source = source.replace("<head></head>", head)
        source = source.decode("utf-8")
        print source
        
        import wx.html
        dlg = wx.Dialog(self, title="HTML", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        html = wx.html.HtmlWindow(dlg, size=(500,400), style=wx.BORDER_SUNKEN)
        html.SetPage(source)
        btn = wx.Button(dlg, wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 10)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)

        dlg.ShowModal()

        handler.DeleteTemporaryImages()

    def GetHTML(self, imagesIncluses=True):
        # Récupération de la source HTML
        handler = rt.RichTextHTMLHandler()
        if imagesIncluses == True : 
##            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_FILES)
        else:
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])
        import cStringIO
        stream = cStringIO.StringIO()
        if not handler.SaveStream(self.ctrl_editeur.GetBuffer(), stream):
            return False
        source = stream.getvalue() 
##        source = source.replace("<head></head>", head)
        source = source.decode("utf-8")
        listeImages = handler.GetTemporaryImageLocations()
        return source, listeImages, handler
    
    def GetValue(self):
        return self.ctrl_editeur.GetValue() 
    
    def GetXML(self):
        return self.ctrl_editeur.GetXML()
    
    def SetXML(self, texteXml=""):
        self.ctrl_editeur.SetXML(texteXml)
        
    def EcritTexte(self, texte=""):
        """ Ecrit un texte à l'emplacement du focus """
        self.ctrl_editeur.WriteText(texte)
        self.ctrl_editeur.SetFocus()



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
