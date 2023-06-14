#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.richtext as rt
import six
import copy
import datetime
import os
import wx.lib.agw.hyperlink as Hyperlink
import GestionDB
from Utils import UTILS_Identification


CATEGORIES = [
    ("saisie_libre", _(u"Saisie libre")),
    ("releve_prestations", _(u"Relev� des prestations")),
    ("reglement", _(u"R�glement")),
    ("recu_reglement", _(u"Re�u de r�glement")),
    ("recu_don_oeuvres", _(u"Re�u de don aux oeuvres")),
    ("facture", _(u"Facture")),
    ("rappel", _(u"Rappel")),
    ("attestation_presence", _(u"Attestation de pr�sence")),
    ("attestation_fiscale", _(u"Attestation fiscale")), 
    ("reservations", _(u"Liste des r�servations")), 
    ("cotisation", _(u"Cotisation")),
    ("rappel_pieces_manquantes", _(u"Rappel pi�ces manquantes")),
    ("portail", _(u"Rappel des donn�es du compte internet")),
    ("portail_demande_inscription", _(u"Portail - Demande d'une inscription")),
    ("portail_demande_reservation", _(u"Portail - Demande d'une r�servation")),
    ("portail_demande_renseignement", _(u"Portail - Demande de modification d'un renseignement")),
    ("portail_demande_facture", _(u"Portail - Demande d'une facture")),
    ("portail_demande_recu_reglement", _(u"Portail - Demande d'un re�u de r�glement")),
    ("portail_demande_location", _(u"Portail - Demande d'une location")),
    ("portail_demande_piece", _(u"Portail - Demande de saisie d'une pi�ce")),
    ("location", _(u"Location")),
    ("location_demande", _(u"Demande de location")),
    ("commande_repas", _(u"Commande de repas")),
    ("inscription", _(u"Inscription")),
    ("devis", _(u"Devis")),
]


MOTSCLES_STANDARDS = [
                ( "{UTILISATEUR_NOM_COMPLET}", _(u"Nom complet de l'utilisateur") ),
                ( "{UTILISATEUR_NOM}", _(u"Nom de famille de l'utilisateur") ),
                ( "{UTILISATEUR_PRENOM}", _(u"Pr�nom de l'utilisateur") ),
                ( "{DATE_COURTE}", _(u"Date du jour courte") ),
                ( "{DATE_LONGUE}", _(u"Date du jour longue") ),
                ]
    
MOTSCLES = {
    
    "saisie_libre" : [
                ],
    
    "releve_prestations" : [
                ( "{DATE_EDITION_RELEVE}", _(u"Date de l'�dition du relev�") ),
                ( "{RESTE_DU}", _(u"Reste d� indiqu� par le relev�") ),
                ],

    "reglement" : [
                ( "{ID_REGLEMENT}", _(u"ID du r�glement") ),
                ( "{DATE_REGLEMENT}", _(u"Date du r�glement") ),
                ( "{MODE_REGLEMENT}", _(u"Mode de r�glement") ),
                ( "{NOM_EMETTEUR}", _(u"Nom de l'�metteur") ),
                ( "{NUM_PIECE}", _(u"Num�ro de la pi�ce") ),
                ( "{MONTANT_REGLEMENT}", _(u"Montant du r�glement") ),
                ( "{NOM_PAYEUR}", _(u"Nom du payeur") ),
                ( "{NUM_QUITTANCIER}", _(u"Num�ro de quittancier") ),
                ( "{DATE_SAISIE}", _(u"Date de saisie du r�glement") ),
                ( "{DATE_DIFFERE}", _(u"Date d'encaissement diff�r�") ),
                ],

    "recu_reglement" : [
                ( "{DATE_EDITION_RECU}", _(u"Date d'�dition du re�u") ),
                ( "{NUMERO_RECU}", _(u"Num�ro du re�u") ),
                ( "{ID_REGLEMENT}", _(u"ID du r�glement") ),
                ( "{DATE_REGLEMENT}", _(u"Date du r�glement") ),
                ( "{MODE_REGLEMENT}", _(u"Mode de r�glement") ),
                ( "{NOM_EMETTEUR}", _(u"Nom de l'�metteur") ),
                ( "{NUM_PIECE}", _(u"Num�ro de la pi�ce") ),
                ( "{MONTANT_REGLEMENT}", _(u"Montant du r�glement") ),
                ( "{NOM_PAYEUR}", _(u"Nom du payeur") ),
                ( "{NUM_QUITTANCIER}", _(u"Num�ro de quittancier") ),
                ( "{DATE_SAISIE}", _(u"Date de saisie du r�glement") ),
                ("{DATE_DIFFERE}", _(u"Date d'encaissement diff�r�")),
                ],

    "recu_don_oeuvres" : [
                ( "{DATE_EDITION}", _(u"Date d'�dition du re�u") ),
                ( "{NUMERO_RECU}", _(u"Num�ro du re�u") ),
                ( "{NOM_DONATEUR}", _(u"Nom du donateur") ),
                ( "{ADRESSE_DONATEUR}", _(u"Adresse du donateur") ),
                ( "{DATE_REGLEMENT}", _(u"Date du r�glement") ),
                ( "{MODE_REGLEMENT}", _(u"Mode du r�glement") ),
                ( "{MONTANT_CHIFFRES}", _(u"Montant en chiffres") ),
                ( "{MONTANT_LETTRES}", _(u"Montant en lettres") ),
                ],

    "facture" : [
                ( "{DATE_EDITION_FACTURE}", _(u"Date d'�dition de la facture") ),
                ( "{NUMERO_FACTURE}", _(u"Num�ro de facture") ),
                ( "{DATE_DEBUT}", _(u"Date de d�but de la p�riode de facturation") ),
                ( "{DATE_FIN}", _(u"Date de fin de la p�riode de facturation") ),
                ( "{DATE_ECHEANCE}", _(u"Date d'�chance du r�glement") ),
                ( "{SOLDE}", _(u"Solde de la facture") ),
                ( "{SOLDE_AVEC_REPORTS}", _(u"Solde de la facture (reports inclus)") ),
                ( "{SOLDE_COMPTE}", _(u"Solde du compte famille") ),
                ],

    "rappel" : [
                ( "{DATE_EDITION_RAPPEL}", _(u"Date d'�dition de la lettre de rappel") ),
                ( "{NUMERO_RAPPEL}", _(u"Num�ro de le lattre de rappel") ),
                ( "{DATE_MIN}", _(u"Date de d�but des impay�s") ),
                ( "{DATE_MAX}", _(u"Date de fin des impay�s") ),
                ( "{DATE_REFERENCE}", _(u"Date de r�f�rence") ),
                ( "{SOLDE_CHIFFRES}", _(u"Solde du rappel en chiffres") ),
                ( "{SOLDE_LETTRES}", _(u"Solde du rappel en lettres") ),
                ],

    "attestation_presence" : [
                ( "{DATE_EDITION_ATTESTATION}", _(u"Date d'�dition de l'attestation") ),
                ( "{NUMERO_ATTESTATION}", _(u"Num�ro de l'attestation") ),
                ( "{DATE_DEBUT}", _(u"Date de d�but de la p�riode") ),
                ( "{DATE_FIN}", _(u"Date de fin de la p�riode") ),
                ( "{INDIVIDUS_CONCERNES}", _(u"Liste des individus concern�s") ),
                ( "{SOLDE}", _(u"Solde de l'attestation") ),
                ],

    "reservations" : [
                ( "{SOLDE}", _(u"Solde du document") ),
                ],

    "mandat_sepa" : [
                ( "{REFERENCE_UNIQUE_MANDAT}", _(u"RUM (R�f�rence Unique du Mandat)") ),
                ( "{DATE_SIGNATURE}", _(u"Date de signature du mandat") ),
                ],

    "cotisation" : [
                ( "{NUMERO_CARTE}", _(u"Num�ro de la carte") ),
                ( "{DATE_DEBUT}", _(u"Date de d�but de validit� de la cotisation") ),
                ( "{DATE_FIN}", _(u"Date de fin de validit� de la cotisation") ),
                ( "{NOM_TYPE_COTISATION}", _(u"Nom du type de cotisation") ),
                ( "{NOM_UNITE_COTISATION}", _(u"Nom de l'unit� de cotisation") ),
                ( "{NOM_COTISATION}", _(u"Nom de la cotisation (type + unit�)") ),
                ( "{DATE_CREATION_CARTE}", _(u"Date de cr�ation de la carte") ),
                ( "{MONTANT_FACTURE}", _(u"Montant factur�") ),
                ( "{MONTANT_REGLE}", _(u"Montant r�gl�") ),
                ( "{SOLDE_ACTUEL}", _(u"Solde actuel") ),
                ( "{ACTIVITES}", _(u"Activit�s associ�es") ),
                ( "{NOTES}", _(u"Notes") ),
                ],

    "attestation_fiscale" : [
                ("{DATE_EDITION_COURT}", _(u"Date d'�dition court")),
                ("{DATE_EDITION_LONG}", _(u"Date d'�dition long")),
                ("{DATE_DEBUT}", _(u"Date de d�but de la p�riode")),
                ("{DATE_FIN}", _(u"Date de fin de la p�riode")),
                ("{MONTANT_FACTURE}", _(u"Montant total factur�")),
                ("{MONTANT_REGLE}", _(u"Montant r�gl�")),
                ("{MONTANT_IMPAYE}", _(u"Montant impay�")),
                ("{MONTANT_FACTURE_LETTRES}", _(u"Montant total factur� en lettres")),
                ("{MONTANT_REGLE_LETTRES}", _(u"Montant r�gl� en lettres")),
                ("{MONTANT_IMPAYE_LETTRES}", _(u"Montant impay� en lettres")),
                ],

    "rappel_pieces_manquantes" : [
                ("{NOM_FAMILLE}", _(u"Nom de la famille")),
                ("{LISTE_PIECES_MANQUANTES}", _(u"Liste des pi�ces manquantes")),
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
                ( "{DEMANDE_REPONSE}", _(u"R�ponse � la demande") ),
                ],

    "portail_demande_renseignement": [
        ("{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande")),
        ("{DEMANDE_DESCRIPTION}", _(u"Description de la demande")),
        ("{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande")),
        ("{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement")),
        ("{DEMANDE_REPONSE}", _(u"R�ponse � la demande")),
    ],

    "portail_demande_location": [
        ("{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande")),
        ("{DEMANDE_DESCRIPTION}", _(u"Description de la demande")),
        ("{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande")),
        ("{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement")),
        ("{DEMANDE_REPONSE}", _(u"R�ponse � la demande")),
    ],

    "portail_demande_piece": [
        ("{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande")),
        ("{DEMANDE_DESCRIPTION}", _(u"Description de la demande")),
        ("{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande")),
        ("{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement")),
        ("{DEMANDE_REPONSE}", _(u"R�ponse � la demande")),
    ],

    "portail_demande_reservation" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"R�ponse � la demande") ),
                ( "{PERIODE_NOM}", _(u"Nom de la p�riode") ),
                ( "{PERIODE_DATE_DEBUT}", _(u"Date de d�but de la p�riode") ),
                ( "{PERIODE_DATE_FIN}", _(u"Date de fin de la p�riode") ),
                ( "{TOTAL}", _(u"Total des prestations de la p�riode") ),
                ( "{REGLE}", _(u"Total d�j� r�gl� pour la p�riode") ),
                ( "{SOLDE}", _(u"Solde de la p�riode") ),
                ( "{SOLDE_FAMILLE}", _(u"Solde de la fiche famille") ),
                ],

    "portail_demande_facture" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"R�ponse � la demande") ),
                ],

    "portail_demande_recu_reglement" : [
                ( "{DEMANDE_HORODATAGE}", _(u"Date et heure de la demande") ),
                ( "{DEMANDE_DESCRIPTION}", _(u"Description de la demande") ),
                ( "{DEMANDE_COMMENTAIRE}", _(u"Commentaire de la demande") ),
                ( "{DEMANDE_TRAITEMENT_DATE}", _(u"Date de traitement") ),
                ( "{DEMANDE_REPONSE}", _(u"R�ponse � la demande") ),
                ],

    "location": [
                ("{IDLOCATION}", _(u"ID de la location")),
                ("{IDPRODUIT}", _(u"ID du produit")),
                ("{DATE_DEBUT}", _(u"Date de d�but")),
                ("{DATE_FIN}", _(u"Date de fin")),
                ("{HEURE_DEBUT}", _(u"Heure de d�but")),
                ("{HEURE_FIN}", _(u"Heure de fin")),
                ("{NOM_PRODUIT}", _(u"Nom du produit")),
                ("{NOM_CATEGORIE}", _(u"Nom de la cat�gorie")),
                ("{NOTES}", _(u"Observations")),
                ],

    "location_demande": [
                ("{IDDEMANDE}", _(u"ID de la demande")),
                ("{DATE}", _(u"Date de la demande")),
                ("{HEURE}", _(u"Heure de la demande")),
                ("{CATEGORIES}", _(u"Cat�gories demand�es")),
                ("{PRODUITS}", _(u"Produits demand�s")),
                ("{NOTES}", _(u"Observations")),
                ],

    "commande_repas": [
                ("{NOM_COMMANDE}", _(u"Nom de la commande")),
                ("{DATE_DEBUT}", _(u"Date de d�but de la p�riode")),
                ("{DATE_FIN}", _(u"Date de fin de la p�riode")),
                ],

    "inscription": [
                ("{IDINSCRIPTION}", _(u"ID de l'inscription")),
                ("{DATE_INSCRIPTION}", _(u"Date de l'inscription")),
                ("{EST_PARTI}", _(u"L'individu est parti")),
                ("{ACTIVITE_NOM_LONG}", _(u"Nom de l'activit� long")),
                ("{ACTIVITE_NOM_COURT}", _(u"Nom de l'activit� abr�g�")),
                ("{GROUPE_NOM_LONG}", _(u"Nom du groupe long")),
                ("{GROUPE_NOM_COURT}", _(u"Nom du groupe abr�g�")),
                ("{NOM_CATEGORIE_TARIF}", _(u"Nom de la cat�gorie de tarif")),
                ("{INDIVIDU_NOM}", _(u"Nom de famille de l'individu")),
                ("{INDIVIDU_PRENOM}", _(u"Pr�nom de l'individu")),
                ("{INDIVIDU_DATE_NAISS}", _(u"Date de naissance de l'individu")),
                ],

    "devis": [
        ("{DATE_EDITION_DEVIS}", _(u"Date d'�dition du devis")),
        ("{NUMERO_DEVIS}", _(u"Num�ro du devis")),
        ("{DATE_DEBUT}", _(u"Date de d�but de la p�riode")),
        ("{DATE_FIN}", _(u"Date de fin de la p�riode")),
        ("{INDIVIDUS_CONCERNES}", _(u"Liste des individus concern�s")),
        ("{SOLDE}", _(u"Solde du devis")),
        ],

}


def GetMotscles(categorie=""):
    listeTemp = copy.deepcopy(MOTSCLES_STANDARDS)
    if categorie in MOTSCLES :
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
        menuPop = UTILS_Adaptations.Menu()
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
        # R�cup�ration des mod�les
        DB = GestionDB.DB()
        req = """SELECT IDmodele, categorie, nom, description, objet, texte_xml, IDadresse, defaut
        FROM modeles_emails
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
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
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete




class CTRL_Expediteur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
                                        
    def MAJ(self):
        selectionActuelle = self.GetID() 
        self.listeAdresses = []
        self.dictAdresses = {}
        # R�cup�ration des donn�es
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur, moteur, parametres
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        sel = None
        index = 0
        for IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur, moteur, parametres in listeDonnees :
            self.listeAdresses.append(adresse)
            self.dictAdresses[index] = {"IDadresse" : IDadresse, "moteur": moteur, "adresse": adresse, "nom_adresse": nom_adresse,
                                        "smtp" : smtp, "port" : port, "defaut" : defaut, "auth" : connexionAuthentifiee, "startTLS":startTLS,
                                        "motdepasse" : motdepasse, "utilisateur" : utilisateur, "parametres": parametres}
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
        else :
            self.Enable(True)

    def SetID(self, ID=0):
        for index, values in self.dictAdresses.items():
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
        
        # Contr�les
        self.ctrl_exp = CTRL_Expediteur(self)
        self.bouton_exp = self.bouton_exp = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        # Propri�t�s
        self.ctrl_exp.SetToolTip(wx.ToolTip(_(u"S�lectionnez l'adresse d'exp�diteur")))
        self.bouton_exp.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der � la gestion des adresses d'exp�dition")))
        
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
        ID = self.GetID()
        from Dlg import DLG_Emails_exp
        dlg = DLG_Emails_exp.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_exp.MAJ()
        self.SetID(ID)
    
    def MAJ(self):
        self.ctrl_exp.MAJ() 
        
    def SetID(self, ID=0):
        self.ctrl_exp.SetID(ID)

    def GetID(self):
        return self.ctrl_exp.GetID()
    
    def GetDonnees(self):
        return self.ctrl_exp.GetDonnees()


# --------------------------------------------------------------------------------------------------------------------------------------------------------

def AddTool(barre=None, ID=None, chemin_image=None, kind=wx.ITEM_NORMAL, label="", handler=None, updateUI=None):
    if 'phoenix' in wx.PlatformInfo:
        item = barre.AddTool(toolId=ID, label=label, bitmap=wx.Bitmap(Chemins.GetStaticPath(chemin_image), wx.BITMAP_TYPE_ANY), shortHelp=label, kind=kind)
    else :
        if kind == wx.ITEM_CHECK :
            isToggle = True
        else :
            isToggle = False
        item = barre.AddTool(id=ID, bitmap=wx.Bitmap(Chemins.GetStaticPath(chemin_image), wx.BITMAP_TYPE_ANY), shortHelpString=label, isToggle=isToggle)
    barre.Bind(wx.EVT_TOOL, handler, item)
    if updateUI is not None:
        barre.Bind(wx.EVT_UPDATE_UI, updateUI, item)


class BarreOutils1(wx.ToolBar):
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.parent = parent

        ID_SAUVEGARDER = wx.Window.NewControlId()
        ID_OUVRIR = wx.Window.NewControlId()
        ID_IMPRIMER = wx.Window.NewControlId()
        ID_APERCU = wx.Window.NewControlId()
        ID_GRAS = wx.Window.NewControlId()
        ID_ITALIQUE = wx.Window.NewControlId()
        ID_SOULIGNE = wx.Window.NewControlId()
        ID_COULEUR_POLICE = wx.Window.NewControlId()
        ID_ALIGNER_GAUCHE = wx.Window.NewControlId()
        ID_ALIGNER_CENTRE = wx.Window.NewControlId()
        ID_ALIGNER_DROIT = wx.Window.NewControlId()
        ID_GOMME = wx.Window.NewControlId()

        AddTool(self, ID_SAUVEGARDER, "Images/Teamword/sauvegarder.png", label=_(u"Sauvegarder le texte"), handler=self.parent.OnFileSave)
        AddTool(self, ID_OUVRIR, "Images/Teamword/ouvrir.png", label=_(u"Ouvrir un texte sauvegard�"), handler=self.parent.OnFileOpen)
        self.AddSeparator()
        AddTool(self, ID_IMPRIMER, "Images/Teamword/imprimer.png", label=_(u"Imprimer ce texte"), handler=self.parent.OnPrint)
        AddTool(self, ID_APERCU, "Images/Teamword/Apercu.png", label=_(u"Aper�u avant impression de ce texte"), handler=self.parent.OnPreview)
        self.AddSeparator()
        AddTool(self, ID_ALIGNER_GAUCHE, "Images/Teamword/aligner_gauche.png", kind=wx.ITEM_CHECK, label=_(u"Aligner � gauche"), handler=self.parent.OnAlignLeft, updateUI=self.parent.OnUpdateAlignLeft)
        AddTool(self, ID_ALIGNER_CENTRE, "Images/Teamword/aligner_centre.png", kind=wx.ITEM_CHECK, label=_(u"Centrer"), handler=self.parent.OnAlignCenter, updateUI=self.parent.OnUpdateAlignCenter)
        AddTool(self, ID_ALIGNER_DROIT, "Images/Teamword/aligner_droit.png", kind=wx.ITEM_CHECK, label=_(u"Aligner � droite"), handler=self.parent.OnAlignRight, updateUI=self.parent.OnUpdateAlignRight)
        self.AddSeparator()
        AddTool(self, ID_GRAS, "Images/Teamword/gras.png", kind=wx.ITEM_CHECK, label=_(u"Gras"), handler=self.parent.OnBold, updateUI=self.parent.OnUpdateBold)
        AddTool(self, ID_ITALIQUE, "Images/Teamword/italique.png", kind=wx.ITEM_CHECK, label=_(u"Italique"), handler=self.parent.OnItalic, updateUI=self.parent.OnUpdateItalic)
        AddTool(self, ID_SOULIGNE, "Images/Teamword/souligne.png", kind=wx.ITEM_CHECK, label=_(u"Soulign�"), handler=self.parent.OnUnderline, updateUI=self.parent.OnUpdateUnderline)
        self.AddSeparator()
        AddTool(self, ID_COULEUR_POLICE, "Images/Teamword/police_couleur.png", label=_(u"Couleur de la police"), handler=self.parent.OnColour)
        self.AddSeparator()
        AddTool(self, wx.ID_UNDO, "Images/Teamword/annuler.png", label=_(u"Annuler"), handler=self.parent.ForwardEvent, updateUI=self.parent.ForwardEvent)
        AddTool(self, wx.ID_REDO, "Images/Teamword/repeter.png", label=_(u"R�p�ter"), handler=self.parent.ForwardEvent, updateUI=self.parent.ForwardEvent)
        self.AddSeparator()
        AddTool(self, ID_GOMME, "Images/16x16/Gomme.png", label=_(u"Effacer tout le texte"), handler=self.parent.OnGomme)

        self.SetToolBitmapSize((16, 16))
        self.Realize()


class BarreOutils2(wx.ToolBar):
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.parent = parent

        ID_RETRAIT_GAUCHE = wx.Window.NewControlId()
        ID_RETRAIT_DROIT = wx.Window.NewControlId()
        ID_PARA_MOINS = wx.Window.NewControlId()
        ID_PARA_PLUS = wx.Window.NewControlId()
        ID_INTER_SIMPLE = wx.Window.NewControlId()
        ID_INTER_DEMI = wx.Window.NewControlId()
        ID_INTER_DOUBLE = wx.Window.NewControlId()
        ID_URL = wx.Window.NewControlId()
        ID_IMAGE = wx.Window.NewControlId()

        AddTool(self, wx.ID_CUT, "Images/Teamword/couper.png", label=_(u"Couper"), handler=self.parent.ForwardEvent, updateUI=self.parent.ForwardEvent)
        AddTool(self, wx.ID_COPY, "Images/Teamword/copier.png", label=_(u"Copier"), handler=self.parent.ForwardEvent, updateUI=self.parent.ForwardEvent)
        AddTool(self, wx.ID_PASTE, "Images/Teamword/coller.png", label=_(u"Coller"), handler=self.parent.ForwardEvent, updateUI=self.parent.ForwardEvent)
        self.AddSeparator()
        AddTool(self, ID_RETRAIT_GAUCHE, "Images/Teamword/retrait_gauche.png", label=_(u"Diminuer le retrait"), handler=self.parent.OnIndentLess)
        AddTool(self, ID_RETRAIT_DROIT, "Images/Teamword/retrait_droit.png", label=_(u"Augmenter le retrait"), handler=self.parent.OnIndentMore)
        self.AddSeparator()
        AddTool(self, ID_PARA_MOINS, "Images/Teamword/espaceParagrapheMoins.png", label=_(u"Diminuer l'espacement des paragraphes"), handler=self.parent.OnParagraphSpacingLess)
        AddTool(self, ID_PARA_PLUS, "Images/Teamword/espaceParagraphePlus.png", label=_(u"Augmenter l'espacement des paragraphes"), handler=self.parent.OnParagraphSpacingMore)
        self.AddSeparator()
        AddTool(self, ID_INTER_SIMPLE, "Images/Teamword/interligne_simple.png", label=_(u"Interligne simple"), handler=self.parent.OnLineSpacingSingle)
        AddTool(self, ID_INTER_DEMI, "Images/Teamword/interligne_demi.png", label=_(u"Interligne 1.5"), handler=self.parent.OnLineSpacingHalf)
        AddTool(self, ID_INTER_DOUBLE, "Images/Teamword/interligne_double.png", label=_(u"Interligne double"), handler=self.parent.OnLineSpacingDouble)
        
        self.AddSeparator()
        AddTool(self, ID_URL, "Images/Teamword/url.png", label=_(u"Ins�rer une url"), handler=self.parent.OnInsererURL)
        AddTool(self, ID_IMAGE, "Images/Teamword/importer_image.png", label=_(u"Ins�rer une image"), handler=self.parent.OnImporterImage)

        self.SetToolBitmapSize((16, 16))
        self.Realize()

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Editeur(rt.RichTextCtrl):
    def __init__(self, parent, id=-1, style=wx.VSCROLL|wx.HSCROLL|wx.WANTS_CHARS ):
        rt.RichTextCtrl.__init__(self, parent, id=id, style=style)

    def GetXML(self):
        out = six.BytesIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.GetBuffer()
        if 'phoenix' in wx.PlatformInfo:
            handler.SaveFile(buffer, out)
        else :
            handler.SaveStream(buffer, out)
        out.seek(0)
        content = out.read()
        return content
    
    def SetXML(self, texteXml=""):
        out = six.BytesIO()
        handler = wx.richtext.RichTextXMLHandler()
        buf = self.GetBuffer()
        buf.AddHandler(handler)
        if (six.PY3 and not isinstance(texteXml, bytes)) or (six.PY2 and not isinstance(texteXml, buffer)):
            texteXml = texteXml.encode("utf8")
        out.write(texteXml)
        out.seek(0)
        if 'phoenix' in wx.PlatformInfo:
            handler.LoadFile(buf, out)
        else :
            handler.LoadStream(buf, out)
        self.Refresh()


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, size=(-1, -1)):
        wx.Panel.__init__(self, parent, id=-1, size=size, style=wx.TAB_TRAVERSAL)
        
        # Contr�les
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
        dlg = wx.FileDialog(self, _(u"Choisissez un fichier � ouvrir"), wildcard=wildcard, style=wx.FD_OPEN)
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
        dlg = wx.FileDialog(self, _(u"Sauvegardez le texte"), wildcard=wildcard, style=wx.FD_SAVE)
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
        # d�finit les param�tres de l'impression
        datapr = wx.PrintData()
        data.SetPrintData(datapr)
        # Impression
        preview = wx.PrintPreview(printout1, printout2, data)
        if not preview.Ok():
            print("Probleme dans le preview du richTextCtrl.")
            return
        
        from Utils import UTILS_Printer
        pfrm = UTILS_Printer.FramePreview(self, _(u"Aper�u avant impression"), preview)
        pfrm.SetPosition(self.GetPosition())
        pfrm.SetSize(self.GetSize())
        pfrm.Show(True)     
        # Pour �viter le bug des marges qui se rajoutent apr�s l'aper�u
        self.SetXML(xml)  
            
    def OnPrint(self, event):
        xml = self.GetXML()
        printout = wx.richtext.RichTextPrintout() #wx.html.HtmlPrintout() 
        printout.SetRichTextBuffer(self.ctrl_editeur.GetBuffer()) 
        data = wx.PrintDialogData() 
        data.SetAllPages(True)
        data.SetCollate(True) # Pour assembler les pages
        # d�finit les param�tres de l'impression
        datapr = wx.PrintData()
        data.SetPrintData(datapr)
        # Impression
        printer = wx.Printer(data) 
        printer.Print(self, printout, True) 
        # Pour �viter le bug des marges qui se rajoutent apr�s l'aper�u
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
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord s�lectionner un texte."), _(u"Police"), wx.OK | wx.ICON_INFORMATION)
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
        # S�lection d'une image
        self.repCourant = os.getcwd()
        wildcard = "Toutes les images|*.jpg;*.png;*.gif|" \
                        "Images JPEG (*.jpg)|*.jpg|"     \
                        "Images PNG (*.png)|*.png|"     \
                        "Images GIF (*.gif)|*.gif|"     \
                        "Tous les fichiers (*.*)|*.*"
        # R�cup�ration du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture de la fen�tre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une image"),
            defaultDir=cheminDefaut, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN
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
        # Ins�re l'image dans l'�diteur
        if nomFichierLong.lower().endswith(".jpg") : typeBMP = wx.BITMAP_TYPE_JPEG
        elif nomFichierLong.lower().endswith(".png") : typeBMP = wx.BITMAP_TYPE_PNG
        elif nomFichierLong.lower().endswith(".gif") : typeBMP = wx.BITMAP_TYPE_GIF
        elif nomFichierLong.lower().endswith(".bmp"): typeBMP = wx.BITMAP_TYPE_BMP
        else: typeBMP = wx.BITMAP_TYPE_ANY

        if 'phoenix' in wx.PlatformInfo:
            self.ctrl_editeur.WriteImage(bmp, bitmapType=typeBMP)
        else:
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

        stream = six.BytesIO()
        if not handler.SaveStream(self.ctrl_editeur.GetBuffer(), stream):
            return
        
        source = stream.getvalue()
        head = """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
</head>
        """
        source = source.replace("<head></head>", head)
        if six.PY2:
            source = source.decode("utf-8")

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

    def GetHTML(self, imagesIncluses=True, base64=False):
        # R�cup�ration de la source HTML
        handler = rt.RichTextHTMLHandler()
        if imagesIncluses == True :
            if base64 == True :
                handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
            else :
                handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_FILES)
        else:
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])
        stream = six.BytesIO()
        if 'phoenix' in wx.PlatformInfo:
            if not handler.SaveFile(self.ctrl_editeur.GetBuffer(), stream):
                return False
        else :
            if not handler.SaveStream(self.ctrl_editeur.GetBuffer(), stream):
                return False
        source = stream.getvalue()
        source = source.decode("utf-8")
        listeImages = handler.GetTemporaryImageLocations()
        return source, listeImages, handler

    def GetHTML_base64(self):
        # R�cup�ration de la source HTML
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
        handler.SetFontSizeMapping([7, 9, 11, 12, 14, 22, 100])
        stream = six.BytesIO()

        if 'phoenix' in wx.PlatformInfo:
            if not handler.SaveFile(self.ctrl_editeur.GetBuffer(), stream):
                return False
        else:
            if not handler.SaveStream(self.ctrl_editeur.GetBuffer(), stream):
                return False

        source = stream.getvalue()
        if six.PY2:
            source = source.decode("utf-8")
        for balise in (u"<html>", u"</html>", u"<head>", u"</head>", u"<body>", u"</body>"):
            if six.PY3 and isinstance(balise, str):
                balise = balise.encode("utf-8")
                source = source.replace(balise, b"")
            else:
                source = source.replace(balise, "")
        return source

    def GetValue(self):
        return self.ctrl_editeur.GetValue() 
    
    def GetXML(self):
        return self.ctrl_editeur.GetXML()
    
    def SetXML(self, texteXml=""):
        self.ctrl_editeur.SetXML(texteXml)
        
    def EcritTexte(self, texte=""):
        """ Ecrit un texte � l'emplacement du focus """
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
        self.bouton_test = wx.Button(panel, -1, "Test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL | wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)

    def OnBoutonTest(self, event):
        print(self.ctrl.GetHTML(base64=True)[0])
        self.ctrl.OnFileViewHTML()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
