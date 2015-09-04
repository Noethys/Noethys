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
import wx.lib.agw.aui as aui
from wx.lib.floatcanvas import FloatCanvas, GUIMode
import wx.lib.colourselect as csel
import wx.combo
import wx.grid
import wx.lib.agw.floatspin as FloatSpin
import wx.lib.agw.pybusyinfo as PBI

import Image
import numpy
import sys
import os
import copy
import cStringIO
import StringIO
import random
import traceback
import GestionDB
import datetime
import re

import DLG_Saisie_formule
import UTILS_Questionnaires
import UTILS_Codesbarres
import UTILS_Dates
import UTILS_Infos_individus

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

import UTILS_Impressions
UTILS_Impressions.AjouterPolicesPDF() 
        
import FonctionsPerso
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm as mmPDF
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen.canvas import Canvas as CanvasPDF
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.platypus import Paragraph 

from reportlab.graphics.barcode.common import Codabar, Code11, I2of5, MSI
from reportlab.graphics.barcode.code128 import Code128
from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget, Ean8BarcodeWidget
from reportlab.graphics.barcode.code39 import Extended39, Standard39
from reportlab.graphics.barcode.code93 import Extended93, Standard93
from reportlab.graphics.barcode.usps import FIM, POSTNET
from reportlab.graphics.barcode.usps4s import USPS_4State
from reportlab.graphics.barcode import createBarcodeDrawing 

import DLG_Saisie_texte_doc



class Fond():
    def __init__(self):
        self.nom = _(u"Fond")
        self.code = "fond"
        self.photosIndividuelles = False
        self.champs = [ 
            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),
            ]
        self.codesbarres = []
        self.speciaux = []


class Facture():
    def __init__(self):
        self.nom = _(u"Facture")
        self.code = "facture"
        
        self.photosIndividuelles = False
                        
        self.champs = [ 
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires de dossier"), _(u"M. DUPOND G�rard"), "{FAMILLE_NOM}"),
            (_(u"Rue de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            
            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Num�ro de facture"), u"1234567", "{NUM_FACTURE}"),
            (_(u"Code-barres - Num�ro de facture"), u"F123456", "{CODEBARRES_NUM_FACTURE}"),
            (_(u"Nom du lot"), _(u"Mars 2014"), "{NOM_LOT}"),
            (_(u"Date d'�ch�ance de paiement (long)"), _(u"Lundi 10 janvier 2011"), "{DATE_ECHEANCE_LONG}"),
            (_(u"Date d'�ch�ance de paiement (court)"), u"10/01/2011", "{DATE_ECHEANCE_COURT}"),
            (_(u"Texte �ch�ance de paiement"), _(u"Date d'�ch�ance : 10/01/2011"), "{TEXTE_ECHEANCE}"),
            (_(u"Date d'�dition de la facture (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'�dition de la facture (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            
            (_(u"Total des prestations de la p�riode"), u"10.00 �", "{TOTAL_PERIODE}"),
            (_(u"Total d�j� r�gl� pour la p�riode"), u"6.00 �", "{TOTAL_REGLE}"),
            (_(u"Solde d� pour la p�riode"), u"4.00 �", "{SOLDE_DU}"),
            (_(u"Total des reports des p�riodes pr�c�dentes"), u"134.50 �", "{TOTAL_REPORTS}"),
            (_(u"Total des d�ductions"), u"20.50 �", "{TOTAL_DEDUCTIONS}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="famille"))
        
        self.codesbarres = [ 
            (_(u"Num�ro de facture"), u"1234567", "{CODEBARRES_NUM_FACTURE}"),
            ]
            
        self.speciaux = [ 
                {
                    "nom" : _(u"Cadre principal"),
                    "champ" : _(u"cadre_principal"),
                    "obligatoire" : True,
                    "nbreMax" : 1,
                    "x" : None,
                    "y" : None,
                    "verrouillageX" : False,
                    "verrouillageY" : False,
                    "Xmodifiable" : True,
                    "Ymodifiable" : True,
                    "largeur" : 100,
                    "hauteur" : 150,
                    "largeurModifiable" : True,
                    "hauteurModifiable" : True,
                    "largeurMin" : 80,
                    "largeurMax" : 1000,
                    "hauteurMin" : 80,
                    "hauteurMax" : 1000,
                    "verrouillageLargeur" : False,
                    "verrouillageHauteur" : False,
                    "verrouillageProportions" : False,
                    "interditModifProportions" : False,
                },
                {
                    "nom" : _(u"Coupon-r�ponse vertical"),
                    "champ" : _(u"coupon_vertical"),
                    "obligatoire" : False,
                    "x" : None,
                    "y" : None,
                    "largeur" : 15,
                    "hauteur" : 70,
                    "largeurModifiable" : False,
                    "hauteurModifiable" : False,
                    "verrouillageLargeur" : True,
                    "verrouillageHauteur" : True,
                    "interditModifProportions" : True,
                },
                {
                    "nom" : _(u"Coupon-r�ponse horizontal"),
                    "champ" : _(u"coupon_horizontal"),
                    "obligatoire" : False,
                    "x" : None,
                    "y" : None,
                    "largeur" : 70,
                    "hauteur" : 15,
                    "largeurModifiable" : False,
                    "hauteurModifiable" : False,
                    "verrouillageLargeur" : True,
                    "verrouillageHauteur" : True,
                    "interditModifProportions" : True,
                },

            ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Attestation():
    def __init__(self):
        self.nom = _(u"Attestation")
        self.code = "attestation"
        
        self.photosIndividuelles = False

        self.champs = [ 
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            
            (_(u"Nom du destinataire"), _(u"M. DUPOND G�rard"), "{DESTINATAIRE_NOM}"),
            (_(u"Rue de l'adresse du destinataire"), _(u"10 rue des oiseaux"), "{DESTINATAIRE_RUE}"),
            (_(u"Ville de l'adresse du destinataire"), _(u"29000 QUIMPER"), "{DESTINATAIRE_VILLE}"),
            
            (_(u"Nom des individus concern�s"), u"Xavier DUPOND et Lucie DUPOND", "{NOMS_INDIVIDUS}"),
            (_(u"Date de d�but de la p�riode"), u"01/01/2011", "{DATE_DEBUT}"),
            (_(u"Date de fin de la p�riode"), u"31/01/2011", "{DATE_FIN}"),
            
            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Num�ro de l'attestation"), u"1234567", "{NUM_ATTESTATION}"),
            (_(u"Date d'�dition de l'attestation (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'�dition de l'attestation (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            
            (_(u"Total des prestations de la p�riode"), u"10.00 �", "{TOTAL_PERIODE}"),
            (_(u"Total d�j� r�gl� pour la p�riode"), u"6.00 �", "{TOTAL_REGLE}"),
            (_(u"Solde d� pour la p�riode"), u"4.00 �", "{SOLDE_DU}"),
            (_(u"Total des d�ductions"), u"20.50 �", "{TOTAL_DEDUCTIONS}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="famille"))
        
        self.codesbarres = []
            
        self.speciaux = [ 
                {
                    "nom" : _(u"Cadre principal"),
                    "champ" : _(u"cadre_principal"),
                    "obligatoire" : True,
                    "nbreMax" : 1,
                    "x" : None,
                    "y" : None,
                    "verrouillageX" : False,
                    "verrouillageY" : False,
                    "Xmodifiable" : True,
                    "Ymodifiable" : True,
                    "largeur" : 100,
                    "hauteur" : 150,
                    "largeurModifiable" : True,
                    "hauteurModifiable" : True,
                    "largeurMin" : 80,
                    "largeurMax" : 1000,
                    "hauteurMin" : 80,
                    "hauteurMax" : 1000,
                    "verrouillageLargeur" : False,
                    "verrouillageHauteur" : False,
                    "verrouillageProportions" : False,
                    "interditModifProportions" : False,
                }
                ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Rappel():
    def __init__(self):
        self.nom = _(u"Rappel")
        self.code = "rappel"
        
        self.photosIndividuelles = False
                        
        self.champs = [ 
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires de dossier"), _(u"M. DUPOND G�rard"), "{FAMILLE_NOM}"),
            (_(u"Rue de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            
            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Num�ro de rappel"), u"1234567", "{NUM_RAPPEL}"),
            (_(u"Code-barres - Num�ro de rappel"), u"F123456", "{CODEBARRES_NUM_RAPPEL}"),
            (_(u"Nom du lot"), _(u"Mars 2014"), "{NOM_LOT}"),
            (_(u"Date d'�dition du rappel (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'�dition du rappel (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            (_(u"Date de d�but"), u"10/07/2011", "{DATE_DEBUT}"),
            (_(u"Date de fin"), u"21/12/2011", "{DATE_FIN}"),
            
            (_(u"Solde"), u"12.00 �", "{SOLDE}"),
            (_(u"Solde en lettres"), _(u"Douze Euros"), "{SOLDE_LETTRES}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="famille"))
        
        self.codesbarres = [ 
            (_(u"Num�ro de rappel"), u"1234567", "{CODEBARRES_NUM_RAPPEL}"),
            ]
            
        self.speciaux = [ 
                {
                    "nom" : _(u"Cadre principal"),
                    "champ" : _(u"cadre_principal"),
                    "obligatoire" : True,
                    "nbreMax" : 1,
                    "x" : None,
                    "y" : None,
                    "verrouillageX" : False,
                    "verrouillageY" : False,
                    "Xmodifiable" : True,
                    "Ymodifiable" : True,
                    "largeur" : 100,
                    "hauteur" : 150,
                    "largeurModifiable" : True,
                    "hauteurModifiable" : True,
                    "largeurMin" : 80,
                    "largeurMax" : 1000,
                    "hauteurMin" : 80,
                    "hauteurMax" : 1000,
                    "verrouillageLargeur" : False,
                    "verrouillageHauteur" : False,
                    "verrouillageProportions" : False,
                    "interditModifProportions" : False,
                },
                {
                    "nom" : _(u"Coupon-r�ponse vertical"),
                    "champ" : _(u"coupon_vertical"),
                    "obligatoire" : False,
                    "x" : None,
                    "y" : None,
                    "largeur" : 15,
                    "hauteur" : 70,
                    "largeurModifiable" : False,
                    "hauteurModifiable" : False,
                    "verrouillageLargeur" : True,
                    "verrouillageHauteur" : True,
                    "interditModifProportions" : True,
                },
                {
                    "nom" : _(u"Coupon-r�ponse horizontal"),
                    "champ" : _(u"coupon_horizontal"),
                    "obligatoire" : False,
                    "x" : None,
                    "y" : None,
                    "largeur" : 70,
                    "hauteur" : 15,
                    "largeurModifiable" : False,
                    "hauteurModifiable" : False,
                    "verrouillageLargeur" : True,
                    "verrouillageHauteur" : True,
                    "interditModifProportions" : True,
                },

            ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Reglement():
    def __init__(self):
        self.nom = _(u"R�glement")
        self.code = "reglement"
        
        self.photosIndividuelles = False

        self.champs = [ 
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            
            (_(u"Nom du destinataire"), _(u"M. DUPOND G�rard"), "{DESTINATAIRE_NOM}"),
            (_(u"Rue de l'adresse du destinataire"), _(u"10 rue des oiseaux"), "{DESTINATAIRE_RUE}"),
            (_(u"Ville de l'adresse du destinataire"), _(u"29000 QUIMPER"), "{DESTINATAIRE_VILLE}"),
            
            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Num�ro du re�u"), u"1234567", "{NUM_RECU}"),
            (_(u"Date d'�dition du re�u (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'�dition du re�u (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            
            (_(u"ID du r�glement"), u"11234567", "{IDREGLEMENT}"),
            (_(u"Date du r�glement"), u"21/03/2011", "{DATE_REGLEMENT}"),
            (_(u"Mode de r�glement"), _(u"Ch�que"), "{MODE_REGLEMENT}"),
            (_(u"Nom de l'�metteur"), _(u"Caisse d'�pargne"), "{NOM_EMETTEUR}"),
            (_(u"Num�ro de pi�ce"), u"0001243", "{NUM_PIECE}"),
            (_(u"Montant du r�glement"), u"10.00 �", "{MONTANT_REGLEMENT}"),
            (_(u"Nom du payeur"), _(u"DUPOND G�rard"), "{NOM_PAYEUR}"),
            (_(u"Num�ro de quittancier"), u"246", "{NUM_QUITTANCIER}"),
            (_(u"Date de saisie du r�glement"), u"23/03/2011", "{DATE_SAISIE}"),
            (_(u"Observations"), _(u"Observations"), "{OBSERVATIONS}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="famille"))
        
        self.codesbarres = []
            
        self.speciaux = [ 
                {
                    "nom" : _(u"Cadre principal"),
                    "champ" : _(u"cadre_principal"),
                    "obligatoire" : True,
                    "nbreMax" : 1,
                    "x" : None,
                    "y" : None,
                    "verrouillageX" : False,
                    "verrouillageY" : False,
                    "Xmodifiable" : True,
                    "Ymodifiable" : True,
                    "largeur" : 100,
                    "hauteur" : 150,
                    "largeurModifiable" : True,
                    "hauteurModifiable" : True,
                    "largeurMin" : 80,
                    "largeurMax" : 1000,
                    "hauteurMin" : 80,
                    "hauteurMax" : 1000,
                    "verrouillageLargeur" : False,
                    "verrouillageHauteur" : False,
                    "verrouillageProportions" : False,
                    "interditModifProportions" : False,
                }
                ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ---------------------------------------------------------------------------------------------------------------------------------------

class Individu():
    def __init__(self):
        self.nom = _(u"Individu")
        self.code = "individu"
        self.photosIndividuelles = True
        
        self.champs = [ 
            (_(u"Num�ro ID de l'individu"), u"2582", "{IDINDIVIDU}"),
            (_(u"Civilit� de l'individu (long)"), _(u"Mademoiselle"), "{INDIVIDU_CIVILITE_LONG}"),
            (_(u"Civilit� de l'individu (court)"), _(u"Melle"), "{INDIVIDU_CIVILITE_COURT}"),
            (_(u"Genre de l'individu (M ou F)"), u"M", "{INDIVIDU_GENRE}"),
            (_(u"Nom de l'individu"), _(u"DUPOND"), "{INDIVIDU_NOM}"),
            (_(u"Pr�nom de l'individu"), _(u"Lucie"), "{INDIVIDU_PRENOM}"),
            (_(u"Date de naissance de l'individu"), u"12/04/1998", "{INDIVIDU_DATE_NAISS}"),
            (_(u"Age de l'individu"), u"12", "{INDIVIDU_AGE}"),
            (_(u"Code postal de la ville de naissance"), u"29200", "{INDIVIDU_CP_NAISS}"),
            (_(u"Nom de la ville de naissance"), _(u"BREST"), "{INDIVIDU_VILLE_NAISS}"),
            (_(u"Rue de l'adresse de l'individu"), _(u"10 rue des oiseaux"), "{INDIVIDU_RUE}"),
            (_(u"Code postal de l'adresse de l'individu"), u"29200", "{INDIVIDU_CP}"),
            (_(u"Ville de l'adresse de l'individu"), _(u"BREST"), "{INDIVIDU_VILLE}"),
            (_(u"Profession de l'individu"), _(u"Menuisier"), "{INDIVIDU_PROFESSION}"),
            (_(u"Employeur de l'individu"), _(u"SARL DUPOND"), "{INDIVIDU_EMPLOYEUR}"),
            (_(u"T�l�phone fixe de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_TEL_DOMICILE}"),
            (_(u"T�l�phone mobile de l'individu"), u"06.01.02.03.04.", "{INDIVIDU_TEL_MOBILE}"),
            (_(u"Fax de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_FAX}"),
            (_(u"Adresse internet de l'individu"), _(u"moi@test.com"), "{INDIVIDU_EMAIL}"),
            (_(u"T�l�phone fixe pro de l'individu"), u"01.04.05.04.05.", "{INDIVIDU_TEL_PRO}"),
            (_(u"Fax pro de l'individu"), u"06.03.04.05.04.", "{INDIVIDU_FAX_PRO}"),
            (_(u"Adresse internet pro"), _(u"montravail@test.com"), "{INDIVIDU_EMAIL_PRO}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="individu"))
        
        self.codesbarres = [ 
            (_(u"ID de l'individu"), u"1234567", "{CODEBARRES_ID_INDIVIDU}"),
            ]
        
        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("individu"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("individu"))

# ---------------------------------------------------------------------------------------------------------------------------------------

class Famille():
    def __init__(self):
        self.nom = _(u"famille")
        self.code = "famille"
        self.photosIndividuelles = False
        
        self.champs = [ 
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND G�rard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"R�gime social de la famille"), _(u"R�gime g�n�ral"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Num�ro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="famille"))
        
        self.codesbarres = [ 
            (_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"),
            ]
        
        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))

# ---------------------------------------------------------------------------------------------------------------------------------------

class Inscription():
    def __init__(self):
        self.nom = _(u"Inscription")
        self.code = "inscription"
        self.photosIndividuelles = True
        
        self.champs = [ 
            (_(u"Num�ro ID de l'individu"), u"2582", "{IDINDIVIDU}"),
            (_(u"Civilit� de l'individu (long)"), _(u"Mademoiselle"), "{INDIVIDU_CIVILITE_LONG}"),
            (_(u"Civilit� de l'individu (court)"), _(u"Melle"), "{INDIVIDU_CIVILITE_COURT}"),
            (_(u"Genre de l'individu (M ou F)"), u"M", "{INDIVIDU_GENRE}"),
            (_(u"Nom de l'individu"), _(u"DUPOND"), "{INDIVIDU_NOM}"),
            (_(u"Pr�nom de l'individu"), _(u"Lucie"), "{INDIVIDU_PRENOM}"),
            (_(u"Date de naissance de l'individu"), u"12/04/1998", "{INDIVIDU_DATE_NAISS}"),
            (_(u"Age de l'individu"), u"12", "{INDIVIDU_AGE}"),
            (_(u"Code postal de la ville de naissance"), u"29200", "{INDIVIDU_CP_NAISS}"),
            (_(u"Nom de la ville de naissance"), _(u"BREST"), "{INDIVIDU_VILLE_NAISS}"),
            (_(u"Rue de l'adresse de l'individu"), _(u"10 rue des oiseaux"), "{INDIVIDU_RUE}"),
            (_(u"Code postal de l'adresse de l'individu"), u"29200", "{INDIVIDU_CP}"),
            (_(u"Ville de l'adresse de l'individu"), _(u"BREST"), "{INDIVIDU_VILLE}"),
            (_(u"Profession de l'individu"), _(u"Menuisier"), "{INDIVIDU_PROFESSION}"),
            (_(u"Employeur de l'individu"), _(u"SARL DUPOND"), "{INDIVIDU_EMPLOYEUR}"),
            (_(u"T�l�phone fixe de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_TEL_DOMICILE}"),
            (_(u"T�l�phone mobile de l'individu"), u"06.01.02.03.04.", "{INDIVIDU_TEL_MOBILE}"),
            (_(u"Fax de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_FAX}"),
            (_(u"Adresse internet de l'individu"), _(u"moi@test.com"), "{INDIVIDU_EMAIL}"),
            (_(u"T�l�phone fixe pro de l'individu"), u"01.04.05.04.05.", "{INDIVIDU_TEL_PRO}"),
            (_(u"Fax pro de l'individu"), u"06.03.04.05.04.", "{INDIVIDU_FAX_PRO}"),
            (_(u"Adresse internet pro"), _(u"montravail@test.com"), "{INDIVIDU_EMAIL_PRO}"),

            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND G�rard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"R�gime social de la famille"), _(u"R�gime g�n�ral"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Num�ro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Num�ro ID de l'inscription"), u"003", "{IDINSCRIPTION}"),
            (_(u"Date de l'inscription"), u"01/01/2013", "{DATE_INSCRIPTION}"),
            (_(u"Est parti"), _(u"Oui"), "{EST_PARTI}"),

            (_(u"Num�ro ID de l'activit�"), u"003", "{IDACTIVITE}"),
            (_(u"Nom de l'activit� (long)"), _(u"Accueil de Loisirs"), "{ACTIVITE_NOM_LONG}"),
            (_(u"Nom de l'activit� (abr�g�)"), _(u"ALSH"), "{ACTIVITE_NOM_COURT}"),

            (_(u"Num�ro ID du groupe"), u"001", "{IDGROUPE}"),
            (_(u"Nom du groupe (long)"), _(u"Accueil de Loisirs"), "{GROUPE_NOM_LONG}"),
            (_(u"Nom du groupe (abr�g�)"), _(u"ALSH"), "{GROUPE_NOM_COURT}"),

            (_(u"Num�ro ID de la cat�gorie de tarif"), u"004", "{IDCATEGORIETARIF}"),
            (_(u"Nom de la cat�gorie de tarif"), _(u"Hors commune"), "{NOM_CATEGORIE_TARIF}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="individu+famille"))
        
        self.codesbarres = [ 
            (_(u"ID de l'individu"), u"1234567", "{CODEBARRES_ID_INDIVIDU}"),
            ]
        
        self.speciaux = [ 
                {
                    "nom" : _(u"Cadre principal"),
                    "champ" : _(u"cadre_principal"),
                    "obligatoire" : False,
                    "nbreMax" : 1,
                    "x" : None,
                    "y" : None,
                    "verrouillageX" : False,
                    "verrouillageY" : False,
                    "Xmodifiable" : True,
                    "Ymodifiable" : True,
                    "largeur" : 100,
                    "hauteur" : 150,
                    "largeurModifiable" : True,
                    "hauteurModifiable" : True,
                    "largeurMin" : 80,
                    "largeurMax" : 1000,
                    "hauteurMin" : 80,
                    "hauteurMax" : 1000,
                    "verrouillageLargeur" : False,
                    "verrouillageHauteur" : False,
                    "verrouillageProportions" : False,
                    "interditModifProportions" : False,
                }
                ]

        # Questionnaires
        self.champs.extend(GetQuestions("individu"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("individu"))

# ---------------------------------------------------------------------------------------------------------------------------------------

class Cotisation():
    def __init__(self):
        self.nom = _(u"Cotisation")
        self.code = "cotisation"
        self.photosIndividuelles = False
        
        self.champs = [ 
            (_(u"Num�ro ID de la cotisation"), u"13215", "{IDCOTISATION}"),
            (_(u"Num�ro ID du type de cotisation"), u"034", "{IDTYPE_COTISATION}"),
            (_(u"Num�ro ID de l'unit� de cotisation"), u"31", "{IDUNITE_COTISATION}"),
            (_(u"Num�ro ID de l'utilisateur qui a saisi la cotisation"), u"023", "{IDUTILISATEUR}"),
            (_(u"Date de saisie de la cotisation"), u"01/01/2014", "{DATE_SAISIE}"),
            (_(u"Date de cr�ation de la carte"), u"10/01/2014", "{DATE_CREATION_CARTE}"),
            (_(u"Num�ro de la carte"), u"0123321", "{NUMERO_CARTE}"),
            (_(u"Num�ro ID du d�p�t de cotisation"), u"064", "{IDDEPOT_COTISATION}"),
            (_(u"Date de d�but de validit�"), u"01/01/2014", "{DATE_DEBUT}"),
            (_(u"Date de fin de validit�"), u"31/12/2014", "{DATE_FIN}"),
            (_(u"Num�ro ID de la prestation"), u"31211", "{IDPRESTATION}"),
            (_(u"Nom du type de cotisation"), _(u"Carte d'adh�rent"), "{NOM_TYPE_COTISATION}"),
            (_(u"Nom de l'unit� de cotisation"), u"2014", "{NOM_UNITE_COTISATION}"),
            (_(u"Cotisation familiale ou individuelle"), _(u"Cotisation familiale"), "{COTISATION_FAM_IND}"),
            (_(u"Nom de la cotisation (Type + unit�)"), _(u"Carte d'adh�rent - 2014"), "{NOM_COTISATION}"),
            (_(u"Nom de d�p�t de cotisations"), _(u"D�p�t Janvier 2014"), "{NOM_DEPOT}"),
            (_(u"Montant factur�"), u"20.00 �", "{MONTANT_FACTURE}"),
            (_(u"Montant r�gl�"), u"20.00 �", "{MONTANT_REGLE}"),
            (_(u"Solde actuel"), u"20.00 �", "{SOLDE_ACTUEL}"),
            (_(u"Montant factur� en lettres"), _(u"Vingt Euros"), "{MONTANT_FACTURE_LETTRES}"),
            (_(u"Montant r�gl� en lettres"), _(u"Vingt Euros"), "{MONTANT_REGLE_LETTRES}"),
            (_(u"Solde actuel en lettres"), _(u"Vingt Euros"), "{SOLDE_ACTUEL_LETTRES}"),
            (_(u"Date du r�glement"), u"01/01/2014", "{DATE_REGLEMENT}"),
            (_(u"Mode de r�glement"), _(u"Ch�que"), "{MODE_REGLEMENT}"),
            
            (_(u"Num�ro ID de l'individu b�n�ficiaire"), u"4654", "{IDINDIVIDU}"),
            (_(u"Num�ro ID de la famille b�n�ficiare"), u"13211", "{BENEFICIAIRE_NOM}"),
            (_(u"Adresse du b�n�ficiaire - Rue"), _(u"10 rue des oiseaux"), "{BENEFICIAIRE_RUE}"),
            (_(u"Adresse du b�n�ficiaire - CP"), u"29200", "{BENEFICIAIRE_CP}"),
            (_(u"Adresse du b�n�ficiaire - Ville"), _(u"BREST"), "{BENEFICIAIRE_VILLE}"),
            
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND G�rard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"R�gime social de la famille"), _(u"R�gime g�n�ral"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Num�ro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Date d'�dition (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'�dition (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="individu+famille"))
        
        self.codesbarres = [ 
            (_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"),
            ]
        
        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))

# ----------------------------------------------------------------------------------------------------------------------------------

class Attestation_fiscale():
    def __init__(self):
        self.nom = _(u"Attestation fiscale")
        self.code = "attestation_fiscale"
        
        self.photosIndividuelles = False
                        
        self.champs = [ 
            (_(u"Num�ro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires de dossier"), _(u"M. DUPOND G�rard"), "{FAMILLE_NOM}"),
            (_(u"Rue de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            
            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"T�l�phone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Num�ro d'agr�ment de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Num�ro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Date d'�dition (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'�dition (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            (_(u"Date de d�but"), u"10/07/2011", "{DATE_DEBUT}"),
            (_(u"Date de fin"), u"21/12/2011", "{DATE_FIN}"),

            (_(u"Montant factur�"), u"20.00 �", "{MONTANT_FACTURE}"),
            (_(u"Montant r�gl�"), u"20.00 �", "{MONTANT_REGLE}"),
            (_(u"Montant impay�"), u"20.00 �", "{MONTANT_IMPAYE}"),
            (_(u"Montant factur� en lettres"), _(u"Vingt Euros"), "{MONTANT_FACTURE_LETTRES}"),
            (_(u"Montant r�gl� en lettres"), _(u"Vingt Euros"), "{MONTANT_REGLE_LETTRES}"),
            (_(u"Montant impay� en lettres"), _(u"Vingt Euros"), "{MONTANT_IMPAYE_LETTRES}"),
            
            (_(u"Texte d'introduction"), _(u"Veuillez trouver ici le montant..."), "{INTRO}"),
            
            (_(u"D�tail enfant 1"), _(u"10.00 � pour Lucie DUPOND n�e le 01/02/2005"), "{TXT_ENFANT_1}"),
            (_(u"D�tail enfant 2"), _(u"10.00 � pour Lucie DUPOND n�e le 01/02/2005"), "{TXT_ENFANT_2}"),
            (_(u"D�tail enfant 3"), _(u"10.00 � pour Lucie DUPOND n�e le 01/02/2005"), "{TXT_ENFANT_3}"),
            (_(u"D�tail enfant 4"), _(u"10.00 � pour Lucie DUPOND n�e le 01/02/2005"), "{TXT_ENFANT_4}"),
            (_(u"D�tail enfant 5"), _(u"10.00 � pour Lucie DUPOND n�e le 01/02/2005"), "{TXT_ENFANT_5}"),
            (_(u"D�tail enfant 6"), _(u"10.00 � pour Lucie DUPOND n�e le 01/02/2005"), "{TXT_ENFANT_6}"),
            
            ]
        
        self.champs.extend(UTILS_Infos_individus.GetNomsChampsPossibles(mode="famille"))
        
        self.speciaux = [ 
                {
                    "nom" : _(u"Cadre principal"),
                    "champ" : _(u"cadre_principal"),
                    "obligatoire" : False, # Cadre principal non obligatoire !!!!!!!!!!!!!!!!!
                    "nbreMax" : 1,
                    "x" : None,
                    "y" : None,
                    "verrouillageX" : False,
                    "verrouillageY" : False,
                    "Xmodifiable" : True,
                    "Ymodifiable" : True,
                    "largeur" : 100,
                    "hauteur" : 150,
                    "largeurModifiable" : True,
                    "hauteurModifiable" : True,
                    "largeurMin" : 80,
                    "largeurMax" : 1000,
                    "hauteurMin" : 80,
                    "hauteurMax" : 1000,
                    "verrouillageLargeur" : False,
                    "verrouillageHauteur" : False,
                    "verrouillageProportions" : False,
                    "interditModifProportions" : False,
                },
            ]

        self.codesbarres = [ 
            (_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"),
            ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------








def GetQuestions(type):
    Q = UTILS_Questionnaires.Questionnaires()
    listeQuestions = Q.GetQuestions(type)
    listeTemp = []
    for dictQuestion in listeQuestions :
        defaut = Q.FormatageReponse(dictQuestion["defaut"], dictQuestion["controle"])
        listeTemp.append((dictQuestion["label"], defaut, "{QUESTION_%d}" % dictQuestion["IDquestion"]))
    return listeTemp


def GetCodesBarresQuestionnaires(type="individu"):
    DB = GestionDB.DB()
    req = """SELECT IDquestion, questionnaire_questions.label, questionnaire_questions.options
    FROM questionnaire_questions
    LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
    WHERE controle='codebarres' AND type='%s'
    ORDER BY questionnaire_questions.ordre;""" % type
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeCodes = []
    for IDquestion, label, options in listeDonnees :
        listeCodes.append((label, u"1234567", "{CODEBARRES_QUESTION_%d}" % IDquestion))
    return listeCodes


# ---------------------------------------------------------------------------------------------------------------------------------------

NOM_APPLICATION = _(u"Noedoc")

# Couleurs
COULEUR_ZONE_TRAVAIL = (100, 200, 0)
COULEUR_FOND_PAGE = (255, 255, 255)
EPAISSEUR_OMBRE = 2
COULEUR_OMBRE_PAGE = (0, 0, 0)
COULEUR_CADRE_SELECTION = (255, 0, 0)
COULEUR_DEFAUT_OBJET = (193, 222, 245)

# Menu contextuel Objet
ID_MENU_MODIFIER_TEXTE = wx.NewId()
ID_MENU_ROTATION_GAUCHE = wx.NewId()
ID_MENU_ROTATION_DROITE = wx.NewId()
ID_MENU_RECULER = wx.NewId()
ID_MENU_AVANCER = wx.NewId()
ID_MENU_ARRIEREPLAN = wx.NewId()
ID_MENU_AVANTPLAN = wx.NewId()
ID_MENU_DUPLIQUER = wx.NewId()
ID_MENU_SUPPRIMER = wx.NewId()

# Menu contextuel Poign�e
ID_MENU_SUPPRIMER_POINT = wx.NewId()

# Menu contextuel Ligne
ID_MENU_AJOUTER_POINT = wx.NewId()

# Barre d'outils 1
ID_OUTIL_CURSEUR = wx.NewId()
ID_OUTIL_DEPLACER = wx.NewId()
ID_OUTIL_ZOOM_IN = wx.NewId()
ID_OUTIL_ZOOM_OUT = wx.NewId()
ID_OUTIL_ZOOM_AJUSTER = wx.NewId()

# Barre d'outils 2
ID_OUTIL_OBJET_RECTANGLE = wx.NewId()
ID_OUTIL_OBJET_LIGNE = wx.NewId()
ID_OUTIL_OBJET_CERCLE = wx.NewId()
ID_OUTIL_OBJET_POLYGONE = wx.NewId()
ID_OUTIL_OBJET_ELLIPSE = wx.NewId()
ID_OUTIL_OBJET_IMAGE = wx.NewId()
ID_OUTIL_OBJET_IMAGE_DROPDOWN = wx.NewId()
ID_OUTIL_OBJET_CODEBARRES = wx.NewId()
ID_OUTIL_OBJET_BARCODE_DROPDOWN = wx.NewId()
ID_OUTIL_OBJET_SPECIAL = wx.NewId()
ID_OUTIL_OBJET_SPECIAL_DROPDOWN = wx.NewId()
ID_OUTIL_OBJET_TEXTE_LIGNE = wx.NewId()
ID_OUTIL_OBJET_TEXTE_BLOC = wx.NewId()

# Barre d'outils 3
ID_OUTIL_AFFICHAGE_GRILLE = wx.NewId()
ID_OUTIL_AFFICHAGE_APERCU = wx.NewId()

# Astuces
ASTUCES = [
    _(u"Astuce : Restez appuyer sur la touche CTRL pour conserver les proportions lors d'un redimensionnement avec les poign�es"),
    _(u"Astuce : Effectuez un clic droit sur un objet pour acc�der au menu contextuel"),
    _(u"Astuce : Effectuez un clic droit sur l'une des poign�es d'un polygone pour supprimer le point correspondant"),
    _(u"Astuce : Effectuez un clic droit sur la ligne d'un polygone pour y ajouter un point"),
    _(u"Astuce : Vous pouvez attribuer � chaque objet le nom de votre choix"),
    _(u"Astuce : Vous pouvez verrouiller les positions ou dimensions des objets en cliquant sur les cadenas"),
    _(u"Astuce : Appuyez sur la touche SUPPR ou DEL pour supprimer l'objet s�lectionn�"),
    _(u"Astuce : Vous pouvez utiliser les touches fl�ches du clavier pour d�placer pr�cis�ment l'objet s�lectionn�"),
    ]

# -----------------------------------------------------------------------------------------------------------------------------

def AjouterRectangle(xy, taille, nom=_(u"Rectangle"), champ=None,
                                        couleurTrait=(0, 0, 0), styleTrait="Solid", epaissTrait=1, 
                                        coulRemplis=None, styleRemplis="Solid", IDobjet=None, 
                                        InForeground=True):
    """ Cr�ation d'un rectangle """
    objet = MovingRectangle(xy, taille, couleurTrait, styleTrait, epaissTrait, coulRemplis, styleRemplis, InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "rectangle"
    objet.IDobjet = IDobjet
    return objet

def AjouterLigne(points=[], nom=_(u"Ligne"), champ=None,
                                    couleurTrait=(0, 0, 0), styleTrait="Solid", epaissTrait=1, IDobjet=None,
                                    InForeground=True):
    """ Cr�ation d'une ligne """
    objet = MovingLine(points, couleurTrait, styleTrait, epaissTrait, InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "ligne"
    objet.IDobjet = IDobjet
    return objet

def AjouterEllipse(xy, taille, nom=_(u"Ellipse"), champ=None,
                                        couleurTrait=(0, 0, 0), styleTrait="Solid", epaissTrait=1, 
                                        coulRemplis=None, styleRemplis="Solid", IDobjet=None,
                                        InForeground=True):
    """ Cr�ation d'une ellipse """
    objet = MovingEllipse(xy, taille, couleurTrait, styleTrait, epaissTrait, coulRemplis, styleRemplis, InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "ellipse"
    objet.IDobjet = IDobjet
    return objet

def AjouterPolygone( points=[], nom=_(u"Polygone"), champ=None,
                                        couleurTrait=(0, 0, 0), styleTrait="Solid", epaissTrait=1, 
                                        coulRemplis=None, styleRemplis="Solid", IDobjet=None,
                                        InForeground=True):
    """ Cr�ation d'un polygone """
    objet = MovingPolygon(points, couleurTrait, styleTrait, epaissTrait, coulRemplis, styleRemplis, InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "polygone"
    objet.IDobjet = IDobjet
    return objet

def AjouterImage(bmp, xy, hauteur=None, nom=_(u"Image"), champ=None, typeImage="fichier", IDobjet=None, InForeground=True):
    """ Cr�ation d'une image """
    objet = MovingScaledBitmap(bmp, xy, Height=hauteur, Position="bl", InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "image"
    objet.IDobjet = IDobjet
    objet.typeImage = typeImage
    return objet

def AjouterLigneTexte(texte, xy, tailleFont=10, taillePolicePDF=8, nom=_(u"Ligne de texte"), champ=None,
                                        couleurTexte=(0, 0, 0), couleurFond=None, 
                                        family = wx.MODERN, style=wx.NORMAL,
                                        weight=wx.NORMAL, underlined=False,
                                        font=None, IDobjet=None, InForeground=True):
    """ Cr�ation d'une ligne de texte """
    if font != None :
        tailleFont = font.GetPointSize()
    objet = MovingScaledText(texte, xy, tailleFont, couleurTexte, couleurFond, family, style, weight, 
                                    underlined, "bl", font, InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "ligne_texte"
    objet.IDobjet = IDobjet
    objet.SetTaillePolicePDF(taillePolicePDF)
    return objet

def AjouterBlocTexte(texte, xy, tailleFont=10, taillePolicePDF=8, nom=_(u"Bloc de texte"), champ=None,
                                        couleurTexte=(0, 0, 0), couleurFond=None, 
                                        couleurTrait=None, styleTrait="Solid", epaissTrait=1, 
                                        largeur=None, padding=0,
                                        family = wx.MODERN, style=wx.NORMAL,
                                        weight=wx.NORMAL, souligne=False, alignement="left",
                                        font=None, interligne = 1.0, IDobjet=None, InForeground=True):
    """ Cr�ation d'un bloc de texte """
    objet = MovingScaledTextBox(texte, xy, tailleFont, couleurTexte, couleurFond, 
                        couleurTrait, styleTrait, epaissTrait, largeur, padding,
                        family, style, weight, souligne, "tl", alignement, font, interligne, InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "bloc_texte"
    objet.IDobjet = IDobjet
    objet.SetTaillePolicePDF(taillePolicePDF)
    return objet

def AjouterBarcode(xy, largeur=None, hauteur=None, nom=_(u"Code-barres"), champ=None, norme="Extended39", afficheNumero=False, IDobjet=None, InForeground=True):
    """ Cr�ation d'une image """
    objet = AjouterSpecial(xy, largeur, hauteur, nom, couleurFond=(250, 250, 50), InForeground=InForeground)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "barcode"
    if norme == None :
        norme="Extended39"
    objet.norme = norme
    objet.IDobjet = IDobjet
    if afficheNumero == 1 or afficheNumero == True : 
        afficheNumero = True
    else :
        afficheNumero = False
    objet.afficheNumero = afficheNumero
    objet.verrouillageLargeur = True
    objet.hauteurMin = 5
    objet.proprietes.append("barcode")
    return objet

def AjouterSpecial(xy, largeur, hauteur, nom=_(u"Special"), champ=None, couleurFond=(170, 250, 50), IDobjet=None, InForeground=True):
    position = numpy.array([xy[0], xy[1]])
    taille = numpy.array([largeur, hauteur])
    positionCentre = position+(taille/2.0)
    listeObjets = [
        MovingRectangle(position, taille, FillColor=couleurFond, FillStyle="BiDiagonalHatch", InForeground=InForeground),
        MovingLine(numpy.array([position, position+taille]), InForeground=InForeground),
        MovingLine((numpy.array([position[0], position[1]+taille[1]]), numpy.array([position[0]+taille[0], position[1]])), InForeground=InForeground),
        ]
    objet = MovingGroup(InForeground=InForeground)
    objet.AddObjects(listeObjets)
    objet.nom = nom
    objet.champ = champ
    objet.categorie = "special"
    objet.IDobjet = IDobjet
    return objet

# ----------------------------------------------------------------------------------------------------------------------------------
        
class Panel_commandes(wx.Panel):
    def __init__(self, parent):
        """ Boutons de commande en bas de la fen�tre """
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
##        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
##        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_base.Add(self.bouton_aide, 0, 0, 0)
##        grid_sizer_base.Add(self.bouton_options, 0, 0, 0)
##        grid_sizer_base.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_base.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(1)
        sizer_base.Add(grid_sizer_base, 0, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        self.SetMinSize((-1, 50))
        self.Layout()
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
##        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
##        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def OnBoutonOk(self, event):
        # Sauvegarde
        etat = self.parent.Sauvegarde()
        if etat == False : 
            return
        # Fermeture de la fen�tre
        self.parent.EndModal(wx.ID_OK)        

    def OnBoutonAnnuler(self, event):
        self.parent.EndModal(wx.ID_CANCEL)        
        
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Lditeurdedocuments")
    
    def OnBoutonOutils(self, event):
        self.parent.MenuOutils() 


# ------------------------------------------------------------------------------------------------------------------

class Panel_infos(wx.Panel):
    def __init__(self, parent):
        """ Affichage des coords de la souris et autre infos """
        wx.Panel.__init__(self, parent, id=-1, size=(-1, 15), style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.SetBackgroundColour((213, 252, 186))
        self.ctrl_coords = wx.StaticText(self, -1, u"", (10, 1))
        self.ctrl_info = wx.StaticText(self, -1, u"", (120, 1))
        
    def SetCoords(self, x, y):
        if x != None and y != None : 
            texte = u"x = %d   y = %d" % (x, y)
            self.ctrl_coords.SetLabel(texte)
    
    def EffaceCoords(self):
        self.ctrl_coords.SetLabel("")
        
    def SetInfo(self, info=None):
        if info != None : 
            self.ctrl_info.SetLabel(info)

# ------------------------------------------------------------------------------------------------------------------

    
class CTRL_Style(wx.combo.OwnerDrawnComboBox):
    """ ComboBox pour s�lectionner le style de trait """
    def __init__(self, parent, categorie="trait", choices=[], style=0):
        self.parent = parent
        self.categorie = categorie
        self.selection = 0
        
        if self.categorie == "trait" :
            choices = [
                _(u"Plein"),
                _(u"Transparent"),
                _(u"Pointill�s"),
                _(u"Traits longs"),
                _(u"Traits courts"),
                _(u"Pointill�s/traits"),
                ]
            self.dictStyles = {
                0 : "Solid",
                1 : "Transparent",
                2 : "Dot",
                3 : "LongDash",
                4 : "ShortDash",
                5 : "DotDash",
                }
        else :
            choices = [
                _(u"Solide"),
                _(u"Transparent"),
                _(u"Hachures diagonales asc."),
                _(u"Hachures diagonales crois�es"),
                _(u"Hachures diagonales desc."),
                _(u"Grille"),
                _(u"Hachures horizontales"),
                _(u"Hachures verticales"),
                ]
            self.dictStyles = {
                0 : "Solid",
                1 : "Transparent",
                2 : "BiDiagonalHatch",
                3 : "CrossDiagHatch",
                4 : "FDiagonal_Hatch",
                5 : "CrossHatch",
                6 : "HorizontalHatch",
                7 : "VerticalHatch",
                }

        wx.combo.OwnerDrawnComboBox.__init__(self, parent, choices=choices, style=style)

        self.Bind(wx.EVT_COMBOBOX, self.OnSelection)

    def OnSelection(self, event):
        self.selection = event.GetSelection() 
        event.Skip() 

    def GetValeur(self):
        index = self.selection 
        return self.dictStyles[index]

    def SetValeur(self, valeur="Solid"):
        for index, code in self.dictStyles.iteritems() :
            if code == valeur :
                self.Select(index)
                self.selection = index
                break
        
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            self.selection = None
            return
        r = wx.Rect(*rect) 
        r.Deflate(3, 5)

        penStyle = wx.SOLID
        if self.categorie == "trait" :
            if item == 1 : penStyle = wx.TRANSPARENT
            elif item == 2 : penStyle = wx.DOT
            elif item == 3 : penStyle = wx.LONG_DASH
            elif item == 4 : penStyle = wx.SHORT_DASH
            elif item == 5 : penStyle = wx.DOT_DASH
        else:
            if item == 1 : penStyle = wx.TRANSPARENT
            elif item == 2 : penStyle = wx.BDIAGONAL_HATCH
            elif item == 3 : penStyle = wx.CROSSDIAG_HATCH
            elif item == 4 : penStyle = wx.FDIAGONAL_HATCH
            elif item == 5 : penStyle = wx.CROSS_HATCH
            elif item == 6 : penStyle = wx.HORIZONTAL_HATCH
            elif item == 7 : penStyle = wx.VERTICAL_HATCH
            
        pen = wx.Pen(dc.GetTextForeground(), 3, penStyle)
        dc.SetPen(pen)

        if flags & wx.combo.ODCB_PAINTING_CONTROL:
            # for painting the control itself
            dc.DrawLine( r.x+5, r.y+r.height/2, r.x+r.width - 5, r.y+r.height/2 )
            self.selection = item
        else:
            # for painting the items in the popup
            dc.DrawText(self.GetString( item ),
                        r.x + 3,
                        (r.y + 0) + ( (r.height/2) - dc.GetCharHeight() )/2
                        )
            dc.DrawLine( r.x+5, r.y+((r.height/4)*3)+1, r.x+r.width - 5, r.y+((r.height/4)*3)+1 )
           
    def OnDrawBackground(self, dc, rect, item, flags):
        # If the item is selected, or its item # iseven, or we are painting the
        # combo control itself, then use the default rendering.
        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, rect, item, flags)
            return

        # Otherwise, draw every other background with different colour.
        bgCol = wx.Colour(240,240,250)
        dc.SetBrush(wx.Brush(bgCol))
        dc.SetPen(wx.Pen(bgCol))
        dc.DrawRectangleRect(rect);

    # Overridden from OwnerDrawnComboBox, should return the height
    # needed to display an item in the popup, or -1 for default
    def OnMeasureItem(self, item):
        # Simply demonstrate the ability to have variable-height items
        if item & 1:
            return 36
        else:
            return 24

    # Overridden from OwnerDrawnComboBox.  Callback for item width, or
    # -1 for default/undetermined
    def OnMeasureItemWidth(self, item):
        return -1; # default - will be measured from text width
        

#----------------------------------------------------------------------------------------------------------------


class CTRL_Verrou(wx.StaticBitmap):
    def __init__(self, parent, id=-1, lienControle=None, type="x", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        # Variables
        self.parent = parent
        self.lienControle = lienControle
        self.type = type
        self.verrouillage = False
        self.bmpVerrouON = wx.Bitmap("Images/16x16/Cadenas_ferme.png", wx.BITMAP_TYPE_ANY)
        self.bmpVerrouOFF = wx.Bitmap("Images/16x16/Cadenas.png", wx.BITMAP_TYPE_ANY)
        self.bmpVerrouOFF_SURVOL = wx.Bitmap("Images/16x16/Cadenas_survol.png", wx.BITMAP_TYPE_ANY)
        self.bmpVerrouON_SURVOL = wx.Bitmap("Images/16x16/Cadenas_ferme_survol.png", wx.BITMAP_TYPE_ANY)
        # Init Bitmap
        wx.StaticBitmap.__init__(self, parent, id, bitmap=self.bmpVerrouOFF, pos=pos, size=size, style=style)
        self.SetToolTipString(_(u"Cliquez ici pour verrouiller ce param�tre"))
        # Binds
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    def OnMotion(self, event):
        if self.verrouillage : self.SetBitmap(self.bmpVerrouON_SURVOL)
        else: self.SetBitmap(self.bmpVerrouOFF_SURVOL)

    def OnLeave(self, event):
        if self.verrouillage : self.SetBitmap(self.bmpVerrouON)
        else: self.SetBitmap(self.bmpVerrouOFF)

    def OnLeftDown(self, event):
        self.SetEtat()
    
    def SetEtat(self, etat=None):
        if etat != None :
            self.verrouillage = not etat
        if self.verrouillage : 
            self.verrouillage = False
            self.SetBitmap(self.bmpVerrouOFF)
            self.SetToolTipString(_(u"Cliquez ici pour verrouiller ce param�tre"))
        else: 
            self.verrouillage = True
            self.SetBitmap(self.bmpVerrouON)
            self.SetToolTipString(_(u"Cliquez ici pour d�verrouiller ce param�tre"))
        # Modifie le contr�le li� du param�tre
        if self.lienControle != None :
            self.lienControle.Enable(not self.verrouillage)
            if self.type == "x" : self.parent.objet.verrouillageX = self.verrouillage
            if self.type == "y" : self.parent.objet.verrouillageY = self.verrouillage
            if self.type == "largeur" : self.parent.objet.verrouillageLargeur = self.verrouillage
            if self.type == "hauteur" : self.parent.objet.verrouillageHauteur = self.verrouillage
    
    def GetEtat(self):
        return self.verrouillage

# ---------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Fond(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        listeItems = ["Aucun",]
        self.dictDonnees = { 0 : None}
        
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, largeur, hauteur
        FROM documents_modeles
        WHERE categorie='fond'
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDmodele, nom, largeur, hauteur in listeDonnees :
            listeItems.append(nom)
            self.dictDonnees[index] = {"ID" : IDmodele}
            index += 1
        return listeItems

    def SetID(self, ID=None):
        if ID == None : 
            self.SetSelection(0)
            return
        for index, values in self.dictDonnees.iteritems():
            if values != None and values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == 0 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfosFond(self):
        """ R�cup�re les infos sur le fond s�lectionn� """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class Panel_proprietes_doc(wx.Panel):
    def __init__(self, parent, canvas, categorie=""):
        wx.Panel.__init__(self, parent, id=-1, name="panel_proprietes_doc", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie

        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_taille = wx.StaticText(self, -1, _(u"Taille :"))
        self.label_largeur = wx.StaticText(self, -1, u"L")
        self.ctrl_largeur = wx.SpinCtrl(self, -1, u"", min=10, max=1000)
        self.label_x = wx.StaticText(self, -1, u"x", style=wx.ALIGN_CENTRE)
        self.label_hauteur = wx.StaticText(self, -1, u"H")
        self.ctrl_hauteur = wx.SpinCtrl(self, -1, u"", min=10, max=1000)
        self.label_mm = wx.StaticText(self, -1, u"  (mm)")
        self.label_observations = wx.StaticText(self, -1, _(u"Obs. :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_fond = wx.StaticText(self, -1, _(u"Fond :"))
        self.ctrl_fond = CTRL_Fond(self)
        
        if categorie == "fond" :
            self.label_fond.Show(False)
            self.ctrl_fond.Show(False)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnChangeNom, self.ctrl_nom)
        self.Bind(wx.EVT_SPINCTRL, self.OnChangeLargeur, self.ctrl_largeur)
        self.Bind(wx.EVT_SPINCTRL, self.OnChangeHauteur, self.ctrl_hauteur)
        self.Bind(wx.EVT_CHOICE, self.OnChangeFond, self.ctrl_fond)

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez le nom du fond"))
        self.ctrl_largeur.SetToolTipString(_(u"Saisissez ici la largeur du document"))
        self.ctrl_hauteur.SetToolTipString(_(u"Saisissez ici la hauteur du document"))
        self.ctrl_observations.SetToolTipString(_(u"Saisissez ici d'�ventuelles observations"))
        self.ctrl_fond.SetToolTipString(_(u"Vous pouvez s�lectionner ici un fond de page"))
        self.ctrl_largeur.SetMinSize((60, -1))
        self.label_x.SetMinSize((20, -1))
        self.ctrl_hauteur.SetMinSize((60, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_taille = wx.FlexGridSizer(rows=1, cols=6, vgap=2, hgap=2)
        grid_sizer_base.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT, 10)
        grid_sizer_base.Add(self.ctrl_nom, 0, wx.EXPAND|wx.RIGHT|wx.TOP, 10)
        grid_sizer_base.Add(self.label_taille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_taille.Add(self.label_largeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_taille.Add(self.ctrl_largeur, 0, 0, 0)
        grid_sizer_taille.Add(self.label_x, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_taille.Add(self.label_hauteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_taille.Add(self.ctrl_hauteur, 0, 0, 0)
        grid_sizer_taille.Add(self.label_mm, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_taille, 1, wx.EXPAND|wx.RIGHT, 10)
        if self.categorie == "fond" :
            grid_sizer_base.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.BOTTOM, 10)
            grid_sizer_base.Add(self.ctrl_observations, 0, wx.EXPAND|wx.RIGHT|wx.BOTTOM, 10)
        else:
            grid_sizer_base.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
            grid_sizer_base.Add(self.ctrl_observations, 0, wx.EXPAND|wx.RIGHT, 10)
        grid_sizer_base.Add(self.label_fond, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.BOTTOM, 10)
        grid_sizer_base.Add(self.ctrl_fond, 0, wx.EXPAND|wx.RIGHT|wx.BOTTOM, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(1)
        
    def SetNom(self, nom=u""):
        if nom == None or nom == u"" :
            nom = _(u"Sans nom")
        self.ctrl_nom.SetValue(nom)
    
    def GetNom(self):
        return self.ctrl_nom.GetValue()
    
    def SetObservations(self, observations=u""):
        self.ctrl_observations.SetValue(observations)
    
    def GetObservations(self):
        return self.ctrl_observations.GetValue() 
    
    def SetFond(self, IDfond=None):
        self.ctrl_fond.SetID(IDfond)
    
    def GetFond(self):
        return self.ctrl_fond.GetID() 
    
    def SetTaille(self, taille=(210, 297)):
        self.ctrl_largeur.SetValue(taille[0])
        self.ctrl_hauteur.SetValue(taille[1])
    
    def GetTaille(self):
        return (int(self.ctrl_largeur.GetValue()), int(self.ctrl_hauteur.GetValue())) 
    
    def ChangeTaille(self):
        taille = self.GetTaille()
        self.parent.ChangeTaillePage(taille)
    
    def OnChangeNom(self, event): 
        nom = self.ctrl_nom.GetValue()
        self.parent.SetNomDoc(nom)

    def OnChangeLargeur(self, event): 
        self.ChangeTaille() 

    def OnChangeHauteur(self, event): 
        self.ChangeTaille() 

    def OnChangeFond(self, event): 
        IDmodele = self.GetFond()
        self.parent.ctrl_canvas.SetFond(IDmodele)

# -------------------------------------------------------------------------------------------------------------------------------------------

class Panel_proprietes_objet(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_proprietes", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        
        # Contr�les
        self.ctrl_nom = Proprietes_nom(self, canvas)
        self.ctrl_points = Proprietes_points(self, canvas)
        self.ctrl_position = Proprietes_position(self, canvas)
        self.ctrl_taille = Proprietes_taille(self, canvas)
        self.ctrl_trait = Proprietes_trait(self, canvas)
        self.ctrl_remplissage = Proprietes_remplissage(self, canvas)
        self.ctrl_texte = Proprietes_texte(self, canvas)
        self.ctrl_codebarres = Proprietes_codebarres(self, canvas)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add( (1, 1), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_nom, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_points, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_position, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_taille, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_trait, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_remplissage, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_texte, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.Add(self.ctrl_codebarres, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        
        self.SetObjet(None)
    
    def SetObjet(self, objet):
        self.objet = objet
        # Si aucun objet s�lectionn�
        if objet == None : 
            etat = False
        else: 
            etat = True
        # Activation des panneaux de propri�t�s
        self.Freeze()
        if objet != None and "nom" in objet.proprietes :
            self.ctrl_nom.Show(True)
            self.ctrl_nom.SetObjet(objet)
        else:
            self.ctrl_nom.Show(False)
        if objet != None and "points" in objet.proprietes :
            self.ctrl_points.Show(True)
            self.ctrl_points.SetObjet(objet)
        else:
            self.ctrl_points.Show(False)
        if objet != None and "position" in objet.proprietes :
            self.ctrl_position.Show(True)
            self.ctrl_position.SetObjet(objet)
        else:
            self.ctrl_position.Show(False)
        if objet != None and "taille" in objet.proprietes :
            self.ctrl_taille.Show(True)
            self.ctrl_taille.SetObjet(objet)
        else:
            self.ctrl_taille.Show(False)
        if objet != None and "trait" in objet.proprietes :
            self.ctrl_trait.Show(True)
            self.ctrl_trait.SetObjet(objet)
        else:
            self.ctrl_trait.Show(False)
        if objet != None and "remplissage" in objet.proprietes :
            self.ctrl_remplissage.Show(True)
            self.ctrl_remplissage.SetObjet(objet)
        else:
            self.ctrl_remplissage.Show(False)
        if objet != None and "texte" in objet.proprietes :
            self.ctrl_texte.Show(True)
            self.ctrl_texte.SetObjet(objet)
        else:
            self.ctrl_texte.Show(False)
        if objet != None and "barcode" in objet.proprietes :
            self.ctrl_codebarres.Show(True)
            self.ctrl_codebarres.SetObjet(objet)
        else:
            self.ctrl_codebarres.Show(False)

        self.Layout()
        self.Thaw() 

# -------------------------------------------------------------------------------------------------------------------------------

class Proprietes_nom(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_nom", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Nom"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")         
        self.Bind(wx.EVT_TEXT, self.OnSaisieNom, self.ctrl_nom)

        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        staticbox.Add(self.ctrl_nom, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)

    def OnSaisieNom(self, event): 
        if self.stopEvent == False :
            self.objet.nom = self.GetNom()
            self.objet.dirty = True
    
    def SetNom(self, nom):
        self.stopEvent = True
        self.ctrl_nom.SetValue(nom)
        self.stopEvent = False
    
    def GetNom(self):
        valeur = self.ctrl_nom.GetValue()
        return valeur
    
    def SetObjet(self, objet):
        self.objet = objet
        if objet == None :
            return
        self.SetNom(objet.nom)


# -------------------------------------------------------------------------------------------------------------------------------

class Proprietes_position(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_position", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Position"))
        self.label_x = wx.StaticText(self, -1, u"X :")
        self.ctrl_x = wx.TextCtrl(self, -1, u"") # wx.SpinCtrl(self, -1, "", min=-10000, max=10000)
        self.ctrl_verr_x = CTRL_Verrou(self, lienControle=self.ctrl_x, type="x")
        self.label_y = wx.StaticText(self, -1, u"Y :")
        self.ctrl_y = wx.TextCtrl(self, -1, u"") # wx.SpinCtrl(self, -1, "", min=-10000, max=10000)
        self.ctrl_verr_y = CTRL_Verrou(self, lienControle=self.ctrl_y, type="y")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_TEXT, self.OnChoixX, self.ctrl_x)
        self.Bind(wx.EVT_TEXT, self.OnChoixY, self.ctrl_y)
        
##        self.Bind(wx.EVT_SPINCTRL, self.OnChoixX, self.ctrl_x)
##        self.Bind(wx.EVT_SPINCTRL, self.OnChoixY, self.ctrl_y)

    def __set_properties(self):
        self.ctrl_x.SetMinSize((60, -1))
        self.ctrl_y.SetMinSize((60, -1))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=5)
        grid_sizer_base.Add(self.label_x, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_x, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_verr_x, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_y, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_y, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_verr_y, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)

    def OnChoixX(self, event): 
        if self.stopEvent == False :
            self.canvas.DeplacerObjet(self.objet, newPosition=numpy.array([self.GetX(), self.GetY() ]))
            self.objet.dirty = True

    def OnChoixY(self, event): 
        if self.stopEvent == False :
            self.canvas.DeplacerObjet(self.objet, newPosition=numpy.array([self.GetX() , self.GetY() ]))
            self.objet.dirty = True
    
    def SetX(self, x):
        self.stopEvent = True
        self.ctrl_x.SetValue(str(int(x)))
        self.ctrl_x.Update() 
        self.stopEvent = False
        
    def SetY(self, y):
        self.stopEvent = True
        self.ctrl_y.SetValue(str(int(y)))
        self.ctrl_y.Update() 
        self.stopEvent = False
    
    def GetX(self):
        valeur = self.ctrl_x.GetValue()
        if valeur == "" : valeur = 0
        try : valeur = int(valeur)
        except : valeur = 0
        return int(valeur)
    
    def GetY(self):
        valeur = self.ctrl_y.GetValue()
        if valeur == "" : valeur = 0
        try : valeur = int(valeur)
        except : valeur = 0
        return int(valeur) 

    def VerrouX(self, etat=False):
        self.ctrl_verr_x.SetEtat(etat)

    def VerrouY(self, etat=False):
        self.ctrl_verr_y.SetEtat(etat)
    
    def SetObjet(self, objet):
        self.objet = objet
        if objet == None :
            return
        x, y = objet.GetXY() 
        self.SetX(x)
        self.SetY(y)
        self.VerrouX(objet.verrouillageX)
        self.VerrouY(objet.verrouillageY)
        self.ctrl_verr_x.Enable(objet.Xmodifiable)
        self.ctrl_verr_y.Enable(objet.Ymodifiable)

# -------------------------------------------------------------------------------------------------------------------------------

class Proprietes_taille(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_taille", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Dimensions"))
        self.label_largeur = wx.StaticText(self, -1, _(u"L :"))
        self.ctrl_largeur = wx.TextCtrl(self, -1, u"") # wx.SpinCtrl(self, -1, "", min=-10000, max=10000)
        self.ctrl_verr_largeur = CTRL_Verrou(self, lienControle=self.ctrl_largeur, type="largeur")
        self.label_hauteur = wx.StaticText(self, -1, _(u"H :"))
        self.ctrl_hauteur = wx.TextCtrl(self, -1, u"") # wx.SpinCtrl(self, -1, "", min=-10000, max=10000)
        self.ctrl_verr_hauteur = CTRL_Verrou(self, lienControle=self.ctrl_hauteur, type="hauteur")
        self.ctrl_proportions = wx.CheckBox(self, -1, _(u"Conserver les proportions"))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_TEXT, self.OnChoixLargeur, self.ctrl_largeur)
        self.Bind(wx.EVT_TEXT, self.OnChoixHauteur, self.ctrl_hauteur)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckProportions, self.ctrl_proportions)
        
##        self.Bind(wx.EVT_SPINCTRL, self.OnChoixX, self.ctrl_x)
##        self.Bind(wx.EVT_SPINCTRL, self.OnChoixY, self.ctrl_y)

    def __set_properties(self):
        self.ctrl_largeur.SetMinSize((60, -1))
        self.ctrl_hauteur.SetMinSize((60, -1))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        grid_sizer_taille = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=5)
        grid_sizer_taille.Add(self.label_largeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_taille.Add(self.ctrl_largeur, 0, 0, 0)
        grid_sizer_taille.Add(self.ctrl_verr_largeur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_taille.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_taille.Add(self.label_hauteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_taille.Add(self.ctrl_hauteur, 0, 0, 0)
        grid_sizer_taille.Add(self.ctrl_verr_hauteur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_taille, 1, wx.EXPAND, 5)
        
        grid_sizer_base.Add(self.ctrl_proportions, 1, wx.LEFT|wx.EXPAND, 18)
        
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)

    def OnChoixLargeur(self, event): 
        if self.stopEvent == False :
            largeur, hauteur = self.GetLargeur(), self.GetHauteur()
            if self.objet.verrouillageProportions == True :
                largeurInit, hauteurInit = self.objet.GetTaille()
                hauteur = int(1.0 * hauteurInit / largeurInit * largeur)
            self.MAJtailleObjet(largeur, hauteur)
            self.objet.dirty = True

    def OnChoixHauteur(self, event): 
        if self.stopEvent == False :
            largeur, hauteur = self.GetLargeur(), self.GetHauteur()
            if self.objet.verrouillageProportions == True :
                largeurInit, hauteurInit = self.objet.GetTaille()
                largeur = int(1.0 * largeurInit / hauteurInit * hauteur)
            self.MAJtailleObjet(largeur, hauteur)
            self.objet.dirty = True
            
    def MAJtailleObjet(self, largeur, hauteur):
        self.objet.SetTaille(largeur, hauteur)
        self.objet.CalcBoundingBox()
        self.canvas.Selection(self.objet, forceDraw=False)
        self.canvas.canvas.Draw(True)
    
    def OnCheckProportions(self, event):
        valeur = self.ctrl_proportions.GetValue() 
        self.objet.verrouillageProportions = valeur
        
    def SetLargeur(self, largeur):
        self.stopEvent = True
        self.ctrl_largeur.SetValue(str(int(largeur)))
        self.ctrl_largeur.Update() 
        self.stopEvent = False
        
    def SetHauteur(self, hauteur):
        self.stopEvent = True
        self.ctrl_hauteur.SetValue(str(int(hauteur)))
        self.ctrl_hauteur.Update() 
        self.stopEvent = False
    
    def GetLargeur(self):
        valeur = self.ctrl_largeur.GetValue()
        if valeur == "" : valeur = self.objet.largeurMin
        try : valeur = int(valeur)
        except : valeur = self.objet.largeurMin
        if valeur < self.objet.largeurMin : valeur = self.objet.largeurMin
        return int(valeur)
    
    def GetHauteur(self):
        valeur = self.ctrl_hauteur.GetValue()
        if valeur == "" : valeur = self.objet.hauteurMin
        try : valeur = int(valeur)
        except : valeur = self.objet.hauteurMin
        if valeur < self.objet.hauteurMin : valeur = self.objet.hauteurMin
        return int(valeur) 

    def VerrouLargeur(self, etat=False):
        self.ctrl_verr_largeur.SetEtat(etat)

    def VerrouHauteur(self, etat=False):
        self.ctrl_verr_hauteur.SetEtat(etat)
    
    def SetObjet(self, objet):
        self.objet = objet
        if objet == None :
            return
        largeur, hauteur = objet.GetTaille() 
        self.SetLargeur(largeur)
        self.SetHauteur(hauteur)
        self.VerrouLargeur(objet.verrouillageLargeur)
        self.VerrouHauteur(objet.verrouillageHauteur)
        self.ctrl_proportions.SetValue(objet.verrouillageProportions)
        self.ctrl_proportions.Enable(not objet.interditModifProportions)
        self.ctrl_verr_largeur.Enable(objet.largeurModifiable)
        self.ctrl_verr_hauteur.Enable(objet.hauteurModifiable)

# -------------------------------------------------------------------------------------------------------------------------------

class Proprietes_trait(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_trait", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Trait"))
        self.label_afficher = wx.StaticText(self, -1, _(u"Afficher :"))
        self.ctrl_afficher = wx.CheckBox(self, -1, u"")
        self.label_couleur = wx.StaticText(self, -1, _(u"Couleur :"))
        self.ctrl_couleur = csel.ColourSelect(self, -1, u"", (0, 0, 0), size=(60, 18))
        self.label_style = wx.StaticText(self, -1, _(u"Style :"))
        self.ctrl_style = CTRL_Style(self, categorie="trait", style=wx.CB_READONLY)
        self.label_epaisseur = wx.StaticText(self, -1, _(u"Epaisseur :"))
##        self.ctrl_epaisseur = wx.SpinCtrl(self, -1, "", min=1, max=100, size=(60, -1))
        self.ctrl_epaisseur = FloatSpin.FloatSpin(self, -1, min_val=0.25, max_val=100, increment=0.25, value=0.1, size=(60, -1), agwStyle=FloatSpin.FS_LEFT)
        self.ctrl_epaisseur.SetFormat("%f")
        self.ctrl_epaisseur.SetDigits(2)
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAfficher, self.ctrl_afficher)
        self.Bind(csel.EVT_COLOURSELECT, self.OnSelectCouleur, self.ctrl_couleur)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectStyle, self.ctrl_style)
        self.Bind(wx.EVT_SPINCTRL, self.OnSaisieEpaisseur, self.ctrl_epaisseur)
        
        # Layout
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        
        grid_sizer_base.Add(self.label_afficher, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_L1 = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_L1.Add(self.ctrl_afficher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_L1.Add( (5, 5), 0, 0, 0)
        grid_sizer_L1.Add(self.label_couleur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_L1.Add(self.ctrl_couleur, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_L1, 1, wx.EXPAND, 5)
        
        grid_sizer_base.Add(self.label_style, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_style, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.label_epaisseur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_epaisseur, 0, 0, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def OnCheckAfficher(self, event):
        etat = self.ctrl_afficher.GetValue() 
        if etat == True :
            self.objet.LineColor = self.GetCouleur()
            self.SetStyle("Solid")
            self.OnSelectStyle(None)
        else:
            self.objet.LineColor = None
        self.MAJtrait() 
        self.SetAfficher(etat) 
        
    def SetAfficher(self, etat=True):
        self.ctrl_afficher.SetValue(etat)
        self.ctrl_couleur.Enable(etat)
        self.ctrl_style.Enable(etat)
        self.ctrl_epaisseur.Enable(etat)
        
    def OnSelectCouleur(self, event):
        couleur  = self.ctrl_couleur.GetColour() 
        self.objet.LineColor = couleur
        self.MAJtrait() 
    
    def GetCouleur(self):
        return self.ctrl_couleur.GetColour()
    
    def SetCouleur(self, couleur):
        self.ctrl_couleur.SetColour(couleur)
    
    def OnSelectStyle(self, event):
        style  = self.ctrl_style.GetValeur() 
        self.objet.LineStyle = style
        self.MAJtrait() 
    
    def GetStyle(self):
        return self.ctrl_style.GetValeur() 
    
    def SetStyle(self, style="Solid"):
        self.ctrl_style.SetValeur(style) 
        
    def OnSaisieEpaisseur(self, event):
        if self.stopEvent == False :
            epaisseur = self.ctrl_epaisseur.GetValue() 
            self.objet.LineWidth = epaisseur
            self.MAJtrait() 
        
    def SetEpaisseur(self, epaisseur):
        self.stopEvent = True
        self.ctrl_epaisseur.SetValue(epaisseur)
        self.stopEvent = False
    
    def GetEpaisseur(self):
        valeur = self.ctrl_epaisseur.GetValue()
        if valeur == "" : valeur = 0
        try : valeur = valeur
        except : valeur = 0
        if valeur < 0 : valeur = 0
        return valeur
    
    def MAJtrait(self):
        self.objet.SetPen(self.objet.LineColor, self.objet.LineStyle, self.objet.LineWidth)
        self.canvas.canvas.Draw(True)
    
    def SetObjet(self, objet):
        self.objet = objet
        if objet == None :
            return
        if objet.LineColor == None :
            self.SetAfficher(etat=False)
        else:
            self.SetAfficher(etat=True)
            self.SetCouleur(objet.LineColor)
            self.SetStyle(objet.LineStyle)
            self.SetEpaisseur(objet.LineWidth)

# -------------------------------------------------------------------------------------------------------------------------------

class Proprietes_remplissage(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_remplissage", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Remplissage"))
        self.label_afficher = wx.StaticText(self, -1, _(u"Afficher :"))
        self.ctrl_afficher = wx.CheckBox(self, -1, u"")
        self.label_couleur = wx.StaticText(self, -1, _(u"Couleur :"))
        self.ctrl_couleur = csel.ColourSelect(self, -1, u"", (0, 0, 0), size=(60, 18))
        self.label_style = wx.StaticText(self, -1, _(u"Style :"))
        self.ctrl_style = CTRL_Style(self, categorie="remplissage", style=wx.CB_READONLY)
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAfficher, self.ctrl_afficher)
        self.Bind(csel.EVT_COLOURSELECT, self.OnSelectCouleur, self.ctrl_couleur)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectStyle, self.ctrl_style)
        
        # Layout
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        
        grid_sizer_base.Add(self.label_afficher, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_L1 = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_L1.Add(self.ctrl_afficher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_L1.Add( (5, 5), 0, 0, 0)
        grid_sizer_L1.Add(self.label_couleur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_L1.Add(self.ctrl_couleur, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_L1, 1, wx.EXPAND, 5)
        
        grid_sizer_base.Add(self.label_style, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_style, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
            
    def OnCheckAfficher(self, event):
        etat = self.ctrl_afficher.GetValue() 
        if etat == True :
            self.SetAfficher(True) 
            self.objet.FillColor = self.GetCouleur()
            self.SetStyle("Solid")
            self.objet.FillStyle = "Solid"
        else:
            self.SetAfficher(False)
            self.objet.FillColor = None
        self.MAJremplissage() 
        
    def SetAfficher(self, etat=True):
        self.ctrl_afficher.SetValue(etat)
        self.ctrl_couleur.Enable(etat)
        self.ctrl_style.Enable(etat)
        
    def OnSelectCouleur(self, event):
        couleur  = self.ctrl_couleur.GetColour() 
        self.couleurActive = couleur
        self.objet.FillColor = couleur
        self.MAJremplissage() 
    
    def GetCouleur(self):
        return self.ctrl_couleur.GetColour()
    
    def SetCouleur(self, couleur):
        self.ctrl_couleur.SetColour(couleur)
    
    def OnSelectStyle(self, event):
        style  = self.ctrl_style.GetValeur() 
        self.objet.FillStyle = style
        self.MAJremplissage() 
    
    def GetStyle(self):
        return self.ctrl_style.GetValeur() 
    
    def SetStyle(self, style="Solid"):
        self.ctrl_style.SetValeur(style) 
            
    def MAJremplissage(self):
        self.objet.SetBrush(self.objet.FillColor, self.objet.FillStyle)
        self.canvas.canvas.Draw(True)
    
    def SetObjet(self, objet):
        self.objet = objet
        if objet == None :
            return
        if objet.FillColor == None :
            self.SetAfficher(etat=False)
        else:
            self.SetAfficher(etat=True)
            self.SetCouleur(objet.FillColor)
            self.SetStyle(objet.FillStyle)

# -------------------------------------------------------------------------------------------------------------------------------


class CTRL_Points(wx.grid.Grid): 
    def __init__(self, parent, canvas):
        wx.grid.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.parent = parent
        self.objet = None
        self.canvas = canvas
        self.stopEvent = False
        
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(45)
        self.SetColLabelSize(17)
        self.DisableDragColSize()
        self.DisableDragRowSize()
        
        # Cr�ation des colonnes
        self.AppendCols(2)
        self.SetColSize(0, 70)
        self.SetColLabelValue(0, u"X")
        self.SetColSize(1, 70)
        self.SetColLabelValue(1, u"Y")
        
        # Binds
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnChangeValeur)
    
    def OnChangeValeur(self, event):
        indexPoint = event.GetRow()
        x = self.GetCellValue(indexPoint, 0)
        y = self.GetCellValue(indexPoint, 1)
        if self.stopEvent == False :
            point = numpy.array((int(x), int(y)))
            self.objet.Points[indexPoint] = point
            self.objet.CalcBoundingBox()
            self.canvas.Selection(self.objet, forceDraw=False, MAJpanel_proprietes=False)
            self.canvas.canvas.Draw(True)
                        
    def MAJ_affichage(self):
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        self.ClearGrid()
        self.InitGrid()
        self.Refresh()
    
    def SetObjet(self, objet):
        if self.objet == objet :
            self.RemplissageSimple() 
        else:
            self.objet = objet
            self.MAJ_affichage()
        
    def InitGrid(self):
        if self.objet == None : return
        self.AppendRows(len(self.objet.Points))
        
        numLigne = 0
        for point in self.objet.Points :
            self.SetRowSize(numLigne, 21)
            self.SetCellEditor(numLigne, 0, wx.grid.GridCellNumberEditor(-1000, 1000))
            self.SetCellAlignment(numLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetCellValue(numLigne, 0, str(int(point[0])))
            self.SetCellEditor(numLigne, 1, wx.grid.GridCellNumberEditor(-1000, 1000))
            self.SetCellAlignment(numLigne, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetCellValue(numLigne, 1, str(int(point[1])))
            numLigne += 1
    
    def RemplissageSimple(self):
        numLigne = 0
        # Modifie si besoin le nombre de lignes de la grid
        diff = len(self.objet.Points) - self.GetNumberRows()
        if diff > 0 : 
            self.AppendRows(diff)
            for numLigneTemp in range(0, self.GetNumberRows()+1) :
                self.SetCellAlignment(numLigneTemp, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellAlignment(numLigneTemp, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        if diff < 0 : self.DeleteRows(0, -diff)
        # Modifie uniquement le contenu des lignes
        for point in self.objet.Points :
            self.SetCellValue(numLigne, 0, str(int(point[0])))
            self.SetCellValue(numLigne, 1, str(int(point[1])))
            numLigne += 1
        
    def SetXY(self, indexPoint=None, point=None):
        self.stopEvent = True
        if point != None : 
            self.SetCellValue(indexPoint, 0, str(int(point[0])))
            self.SetCellValue(indexPoint, 1, str(int(point[1])))
        self.stopEvent = False


class Proprietes_points(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_points", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Points"))
        self.ctrl_points = CTRL_Points(self, canvas)
        self.ctrl_points.SetMinSize((-1, 80)) 
        
        # Layout
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_points, 1, wx.EXPAND, 5)
        grid_sizer_base.AddGrowableCol(0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
            
    
    def SetObjet(self, objet):
        self.objet = objet
        self.ctrl_points.SetObjet(objet) 

# -------------------------------------------------------------------------------------------------------------------------------

class Proprietes_texte(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_texte", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Texte"))
##        self.label_police = wx.StaticText(self, -1, _(u"Police :"))
##        self.ctrl_police = wx.FontPickerCtrl(self, style=wx.FNTP_FONTDESC_AS_LABEL)
        
        self.label_taille = wx.StaticText(self, -1, _(u"Police :"))
        self.ctrl_taille = wx.SpinCtrl(self, -1, u"", size=(40, -1), min=1, max=300)
        
        self.ctrl_couleur = csel.ColourSelect(self, -1, u"", (0, 0, 0), size=(-1, self.ctrl_taille.GetSize()[1]+4))
        
        self.ctrl_gras = wx.ToggleButton(self, -1, u"G", size=(25, -1))
        self.ctrl_italique = wx.ToggleButton(self, -1, u"I", size=(25, -1))
        self.ctrl_souligne = wx.ToggleButton(self, -1, u"S", size=(25, -1))
        self.ctrl_souligne.Show(False) 
        
        # Binds
        self.Bind(csel.EVT_COLOURSELECT, self.OnSelectCouleur, self.ctrl_couleur)
##        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.OnSelectPolice, self.ctrl_police)
        self.Bind(wx.EVT_SPINCTRL, self.OnChangeTaille, self.ctrl_taille)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnChangeGras, self.ctrl_gras)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnChangeItalique, self.ctrl_italique)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnChangeSouligne, self.ctrl_souligne)
        
        # Layout
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        
##        grid_sizer_base.Add(self.label_police, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_L2 = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
##        grid_sizer_L2.Add(self.ctrl_police, 1, wx.EXPAND, 0)
##        grid_sizer_L2.AddGrowableCol(0)
##        grid_sizer_base.Add(grid_sizer_L2, 1, wx.EXPAND, 5)
        
        grid_sizer_base.Add(self.label_taille, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_L2 = wx.FlexGridSizer(rows=1, cols=7, vgap=2, hgap=2)
        grid_sizer_L2.Add(self.ctrl_taille, 0, wx.EXPAND, 0)
        grid_sizer_L2.Add( (6, 6), 0, 0, 0)
        grid_sizer_L2.Add(self.ctrl_couleur, 0, 0, 0)
        grid_sizer_L2.Add( (6, 6), 0, 0, 0)
        grid_sizer_L2.Add(self.ctrl_gras, 0, wx.EXPAND, 0)
        grid_sizer_L2.Add(self.ctrl_italique, 0, wx.EXPAND, 0)
        grid_sizer_L2.Add(self.ctrl_souligne, 0, wx.EXPAND, 0)
        grid_sizer_L2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_L2, 1, wx.EXPAND, 5)

        grid_sizer_base.AddGrowableCol(1)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
                    
    def OnSelectCouleur(self, event):
        if self.stopEvent == False :
            couleur  = self.ctrl_couleur.GetColour() 
            self.couleurActive = couleur
            self.objet.Color = couleur
            self.objet.SetColor(self.objet.Color)
            self.canvas.canvas.Draw(True)
    
    def GetCouleur(self):
        return self.ctrl_couleur.GetColour()
    
    def OnSelectPolice(self, event):
        if self.stopEvent == False :
            font = self.ctrl_police.GetSelectedFont()
            self.objet.FaceName =  font.GetFaceName()
            self.objet.Family =  font.GetFamily()
            self.objet.Style =  font.GetStyle()
            self.objet.Underlined =  font.GetUnderlined()
            self.objet.Weight =  font.GetWeight()
            self.objet.Size = font.GetPointSize()
            self.objet.Font = font
            self.objet.SetFont(self.objet.Size, self.objet.Family, self.objet.Style, self.objet.Weight, self.objet.Underlined, self.objet.FaceName)
            self.objet.LayoutText()
            self.canvas.Selection(self.objet, forceDraw=False)
            self.canvas.canvas.Draw(True)
        
    def SetPolice(self, font):
        self.stopEvent = True
        self.ctrl_police.SetSelectedFont(font)
        self.stopEvent = False

    def SetCouleur(self, couleur):
        self.stopEvent = True
        self.ctrl_couleur.SetColour(couleur)
        self.stopEvent = False

    def SetObjet(self, objet):
        if objet == self.objet :
            return
        self.objet = objet
        if objet == None :
            return
##        self.SetPolice(objet.Font) 
        self.SetCouleur(objet.Color)
        self.SetTaillePolice(objet.taillePolicePDF)
        self.InitBoutonsStyle()
    
    def GetTaillePolice(self):
        return int(self.ctrl_taille.GetValue())

    def SetTaillePolice(self, taille):
        self.stopEvent = True
        self.ctrl_taille.SetValue(taille)
        self.stopEvent = False

    def OnChangeTaille(self, event):
        taille = self.GetTaillePolice() 
        self.objet.SetTaillePolicePDF(taille)
        self.canvas.Selection(self.objet, forceDraw=False, MAJpanel_proprietes=False)
        self.canvas.canvas.Draw(True)
    
    def InitBoutonsStyle(self):
        if self.objet.Weight == wx.BOLD : self.ctrl_gras.SetValue(True)
        if self.objet.Style == wx.ITALIC : self.ctrl_italique.SetValue(True)
        if self.objet.Underlined == True : self.ctrl_souligne.SetValue(True)
        
    def OnChangeGras(self, event):
        self.SetGras(self.ctrl_gras.GetValue())
        self.objet.LayoutText()
        self.canvas.Selection(self.objet, forceDraw=False, MAJpanel_proprietes=False)
        self.canvas.canvas.Draw(True)
    
    def SetGras(self, gras=False):
        if gras == True :
            self.objet.Weight = wx.BOLD
        else:
            self.objet.Weight = wx.NORMAL
        
    def OnChangeItalique(self, event):
        self.SetItalique(self.ctrl_italique.GetValue())
        self.objet.LayoutText()
        self.canvas.Selection(self.objet, forceDraw=False, MAJpanel_proprietes=False)
        self.canvas.canvas.Draw(True)

    def SetItalique(self, italique=False):
        if italique == True :
            self.objet.Style = wx.ITALIC
        else:
            self.objet.Style = wx.NORMAL

    def OnChangeSouligne(self, event):
        self.SetSouligne(self.ctrl_souligne.GetValue())
        self.objet.LayoutText()
        self.canvas.Selection(self.objet, forceDraw=False, MAJpanel_proprietes=False)
        self.canvas.canvas.Draw(True)

    def SetSouligne(self, souligne=False):
        self.objet.Underlined = souligne
        


# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Normes(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent

        # Remplissage
        index = 0
        listeItems = []
        self.dictDonnees = {}
        for dictNorme in UTILS_Codesbarres.LISTE_NORMES :
            self.dictDonnees[index] = dictNorme["code"]
            listeItems.append(dictNorme["label"])
            index += 1
        self.SetItems(listeItems)
        self.SetNorme("Extended39")

    def SetNorme(self, code=""):
        if code == "" or code == None :
            code = "Extended39"
        for index, codeTemp in self.dictDonnees.iteritems():
            if code == codeTemp :
                 self.SetSelection(index)

    def GetNorme(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]


class Proprietes_codebarres(wx.Panel):
    def __init__(self, parent, canvas):
        wx.Panel.__init__(self, parent, id=-1, name="panel_codebarres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.canvas = canvas
        self.objet = None
        self.stopEvent = False
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Code-barres"))
        self.label_norme = wx.StaticText(self, -1, _(u"Norme :"))
        self.ctrl_norme = CTRL_Normes(self)
        self.label_numero = wx.StaticText(self, -1, _(u"Num�ro :"))
        self.ctrl_numero = wx.CheckBox(self, -1, _(u"Afficher"))
        
        self.ctrl_norme.SetToolTipString(_(u"S�lectionnez une norme pour ce code-barres"))
        self.ctrl_numero.SetToolTipString(_(u"Cochez cette case pour afficher la valeur sous le code-barres"))

        # Layout
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_norme, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_norme, 1, wx.EXPAND, 5)
        grid_sizer_base.Add(self.label_numero, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_numero, 1, wx.EXPAND, 5)
        grid_sizer_base.AddGrowableCol(1)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChangeNorme, self.ctrl_norme)
        self.Bind(wx.EVT_CHECKBOX, self.OnChangeAfficheNumero, self.ctrl_numero)

    def SetObjet(self, objet):
        if objet == self.objet :
            return
        self.objet = objet
        if objet == None :
            return
        self.SetNorme(objet.norme)    
        self.SetAfficheNumero(objet.afficheNumero)

    def GetNorme(self):
        return self.ctrl_norme.GetNorme()
    
    def SetNorme(self, norme):
        self.stopEvent = True
        self.ctrl_norme.SetNorme(norme)
        self.stopEvent = False

    def OnChangeNorme(self, event):
        self.objet.norme = self.GetNorme()

    def GetAfficheNumero(self):
        return self.ctrl_numero.GetValue()
    
    def SetAfficheNumero(self, valeur):
        self.stopEvent = True
        self.ctrl_numero.SetValue(valeur)
        self.stopEvent = False

    def OnChangeAfficheNumero(self, event):
        self.objet.afficheNumero = self.GetAfficheNumero()

# -------------------------------------------------------------------------------------------------------------------------------

class MovingObjectMixin:
    """ Methods required for a Moving object """
    def __init__(self, *args, **kwds):
        self.nom = ""
        self.categorie = ""
        self.champ = None
        self.IDobjet = None
        self.obligatoire = False
        self.nbreMax = None
        
        self.dirty = False
        
        self.largeurMin = 1
        self.hauteurMin = 1
        self.largeurMax = 10000
        self.hauteurMax = 10000

        self.verrouillageX = False
        self.verrouillageY = False
        self.Xmodifiable = True
        self.Ymodifiable = True
        
        self.verrouillageLargeur = False
        self.verrouillageHauteur = False
        self.largeurModifiable = True
        self.hauteurModifiable = True
        self.verrouillageProportions = False
        self.interditModifProportions = False

    def GetOutlinePoints(self):
        BB = self.BoundingBox
        OutlinePoints = numpy.array( ( (BB[0,0], BB[0,1]), (BB[0,0], BB[1,1]), (BB[1,0], BB[1,1]), (BB[1,0], BB[0,1]),) )
        return OutlinePoints
    
    def GetTaille2(self):
        """ R�cup�re la taille pour la sauvegarde uniquement """
        if self.categorie in ("bloc_texte", "ligne") :
            return (None, None)
        elif self.categorie == "image" :
            return (None, self.GetTaille()[1])
        else:
            return self.GetTaille()
        
    def GetTexte(self):
        if hasattr(self, "String"): 
            return self.String
        else: 
            return None
        
    def GetImageBuffer(self):
        if hasattr(self, "Image"): 
            # Logo de l'organisateur
            if self.typeImage == "logo":
                return None
            # Image d'un fichier
            if self.typeImage.startswith("fichier"):
                image = self.Image
                buffer = cStringIO.StringIO()
                if "png" in self.typeImage : 
                    handler = wx.BITMAP_TYPE_PNG
                else:
                    handler = wx.BITMAP_TYPE_JPEG
                image.SaveStream(buffer, handler)
                buffer.seek(0)
                blob = buffer.read()
                return blob
        else: 
            return None
        
    def GetCouleurTrait(self):
        if hasattr(self, "LineColor"): 
            if self.LineColor != None : return str(self.LineColor)
            else : return None
        else:
            return None

    def GetStyleTrait(self):
        if hasattr(self, "LineStyle"): 
            return self.LineStyle
        else:
            return None

    def GetEpaissTrait(self):
        if hasattr(self, "LineWidth"): 
            return self.LineWidth
        else:
            return None

    def GetCoulRemplis(self):
        if self.categorie == "special" :
            couleur = self.ObjectList[0].FillColor
            if couleur != None : return str(couleur)
            else : return None
        if hasattr(self, "FillColor"): 
            if self.FillColor != None : return str(self.FillColor)
            else : return None
        else:
            return None

    def GetStyleRemplis(self):
        if hasattr(self, "FillStyle"): 
            return self.FillStyle
        else:
            return None

    def GetCouleurTexte(self):
        if hasattr(self, "Color"): 
            if self.Color != None : return str(self.Color)
            else : return None
        else:
            return None

    def GetCouleurFond(self):
        if hasattr(self, "BackgroundColor"): 
            if self.BackgroundColor != None : return str(self.BackgroundColor)
            return None
        else:
            return None
        
    def GetPadding(self):
        if hasattr(self, "PadSize"): 
            return self.PadSize
        else:
            return None

    def GetInterligne(self):
        if hasattr(self, "LineSpacing"): 
            return self.LineSpacing
        else:
            return None

    def GetTaillePolice(self):
        if hasattr(self, "taillePolicePDF"): 
            return self.taillePolicePDF 
        else:
            return None


    def GetNomPolice(self):
        if hasattr(self, "FaceName"): 
            return self.FaceName
        else:
            return None

    def GetFamilyPolice(self):
        if hasattr(self, "Family"): 
            return self.Family
        else:
            return None

    def GetStylePolice(self):
        if hasattr(self, "Style"): 
            return self.Style
        else:
            return None

    def GetWeightPolice(self):
        if hasattr(self, "Weight"): 
            return self.Weight
        else:
            return None

    def GetSoulignePolice(self):
        if hasattr(self, "Underlined"): 
            return self.Underlined
        else:
            return None

    def GetAlignement(self):
        if hasattr(self, "Alignment"): 
            return self.Alignment
        else:
            return None

    def GetLargeurTexte(self):
        if self.categorie == "bloc_texte" and hasattr(self, "Width"): 
            return self.Width
        else:
            return None
    
    def GetPoints(self):
        if hasattr(self, "Points") and "texte" not in self.categorie : 
            str = ""
            for x, y in self.Points :
                str += "%d,%d;" % (x, y)
            return str
        else:
            return None
    
    def GetTypeImage(self):
        if self.categorie == "image" :
            return self.typeImage
        else:
            return None
            
    def GetNorme(self):
        if hasattr(self, "norme"): 
            return self.norme
        else:
            return None
    
    def GetAfficheNumero(self):
        if hasattr(self, "afficheNumero"): 
            if self.afficheNumero == True :
                return 1
            else :
                return 0
        else:
            return None



class MovingScaledBitmap(FloatCanvas.ScaledBitmap, MovingObjectMixin):
    """ ScaledBitmap Object that can be moved"""
    def __init__(self, *args, **kwds):
        FloatCanvas.ScaledBitmap.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.verrouillageProportions = True
        self.interditModifProportions = True
        self.proprietes = ["nom", "position", "taille"]
    
    def GetXY(self):
        return self.XY
    
    def SetXY(self, xy):
        self.XY = xy

    def GetTaille(self) :
        return (self.Width, self.Height)

    def SetTaille(self, largeur, hauteur):
        self.Width = largeur
        self.Height = hauteur
    
    def Rotation(self, sensHorloge=True):
        """ vers gauche ou droite """
        self.Image = self.Image.Rotate90(sensHorloge)
        Height, Width, bmpWidth, bmpHeight = self.Height, self.Width, self.bmpWidth, self.bmpHeight
        self.Height = Width
        self.Width = Height
        self.bmpWidth = bmpHeight
        self.bmpHeight = bmpWidth
        self.CalcBoundingBox()
        
                
class MovingCircle(FloatCanvas.Circle, MovingObjectMixin):
    """ ScaledCircle Object that can be moved """
    def __init__(self, *args, **kwds):
        FloatCanvas.Circle.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.verrouillageProportions = True
        self.interditModifProportions = True
        self.proprietes = ["nom", "position", "taille", "trait", "remplissage"]
    
    def GetXY(self):
        return self.XY
    
    def SetXY(self, xy):
        self.XY = xy

    def GetTaille(self) :
        return self.WH

    def SetTaille(self, largeur, hauteur):
        self.WH = numpy.array((largeur, hauteur))

class MovingEllipse(FloatCanvas.Ellipse, MovingObjectMixin):
    """ ScaledCircle Object that can be moved """
    def __init__(self, *args, **kwds):
        FloatCanvas.Ellipse.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.proprietes = ["nom", "position", "taille", "trait", "remplissage"]
    
    def GetXY(self):
        return self.XY
    
    def SetXY(self, xy):
        self.XY = xy

    def GetTaille(self) :
        return self.WH

    def SetTaille(self, largeur, hauteur):
        self.WH = numpy.array((largeur, hauteur))


##class MovingArc(FloatCanvas.Arc, MovingObjectMixin):
##    """ ScaledBitmap Object that can be moved """
##    def __init__(self, *args, **kwds):
##        FloatCanvas.Arc.__init__(self, *args, **kwds)
##        MovingObjectMixin.__init__(self, *args, **kwds)
##        self.proprietes = ["nom", "position", "taille", "trait", "remplissage"]

class MovingScaledText(FloatCanvas.ScaledText, MovingObjectMixin):
    """ ScaledText Object that can be moved """
    def __init__(self, *args, **kwds):
        FloatCanvas.ScaledText.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.verrouillageProportions = True
        self.interditModifProportions = True
        self.proprietes = ["nom", "position", "taille", "texte"]

    def GetTexte(self):
        return self.String
    
    def SetTexte(self, texte):
        self.SetText(texte)

    def GetXY(self):
        return self.XY
    
    def SetXY(self, xy):
        self.XY = xy

    def GetTaille(self) :
        return self.BoundingBox[1] - self.BoundingBox[0]
    
    def SetTaillePolicePDF(self, taille=8):
        self.taillePolicePDF = taille
        self.Size = taille / 3.7
        self.LayoutText()
            
    def GetTaillePolicePDF(self):
        return self.taillePolicePDF


class MovingScaledTextBox(FloatCanvas.ScaledTextBox, MovingObjectMixin):
    """ ScaledTextBox Object that can be moved """
    def __init__(self, *args, **kwds):
        FloatCanvas.ScaledTextBox.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.proprietes = ["nom", "position","trait", "texte"]
        self.SetTexte(self.String)
        
    def GetTexte(self):
        return self.texte
    
    def SetTexte(self, texte):
        self.texte = texte
        # Remplace les formules par [[FORMULE]]
        formules = DLG_Saisie_formule.DetecteFormule(texte)
        for formule in formules :
            texte = texte.replace(formule, u"[[FORMULE]]")
        self.SetText(texte)
    
    def GetXY(self):
        return self.XY
    
    def SetXY(self, xy):
        self.XY = xy
        self.LayoutText()
        self.CalcBoundingBox()

    def GetTaille(self) :
        return self.BoundingBox[1] - self.BoundingBox[0]

    def SetTaille(self, largeur, hauteur):
        self.Width = largeur
        self.LayoutText()
        self.CalcBoundingBox()

    def SetTaillePolicePDF(self, taille=8):
        self.taillePolicePDF = taille
        self.Size = taille / 3.7
        self.LayoutText()
            
    def GetTaillePolicePDF(self):
        return self.taillePolicePDF


class MovingPolygon(FloatCanvas.Polygon, MovingObjectMixin):
    """ Polygon Object that can be moved """
    def __init__(self, *args, **kwds):
        FloatCanvas.Polygon.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.proprietes = ["nom", "points", "trait", "remplissage"]
    
    def GetXY(self):
        return self.Points[0]
    
    def GetTaille(self):
        return (None, None)


class MovingRectangle(FloatCanvas.Rectangle, MovingObjectMixin):
    """ Rectangle Object that can be moved"""
    def __init__(self, *args, **kwds):
        FloatCanvas.Rectangle.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.proprietes = ["nom", "position", "taille", "trait", "remplissage"]
    
    def GetXY(self):
        return self.XY
    
    def SetXY(self, xy):
        self.XY = xy

    def GetTaille(self) :
        return self.WH

    def SetTaille(self, largeur, hauteur):
        self.WH = numpy.array((largeur, hauteur))

class MovingLine(FloatCanvas.Line, MovingObjectMixin):
    """ Line Object that can be moved"""
    def __init__(self, *args, **kwds):
        FloatCanvas.Line.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.proprietes = ["nom", "points", "trait"]
    
    def GetXY(self):
        return self.Points[0]
    
    def SetXY(self, xy):
        self.Points[0] = numpy.array((xy[0], xy[1]))
        
    def GetTaille(self) :
        return self.Points[1] - self.Points[0]

    def SetTaille(self, largeur, hauteur):
        self.WH = numpy.array((largeur, hauteur))

class MovingGroup(FloatCanvas.Group, MovingObjectMixin):
    """ Group Object that can be moved"""
    def __init__(self, *args, **kwds):
        FloatCanvas.Group.__init__(self, *args, **kwds)
        MovingObjectMixin.__init__(self, *args, **kwds)
        self.proprietes = ["nom", "position", "taille"]
    
    def GetXY(self):
        objetRect = self.ObjectList[0]
        return objetRect.XY
    
    def SetXY(self, xy):
        objetRect = self.ObjectList[0]
        objetRect.SetXY(xy)
        objetRect.CalcBoundingBox()        
        BB = objetRect.GetOutlinePoints()
        
        objetLigne1 = self.ObjectList[1]
        objetLigne1.SetXY(xy)
        objetLigne1.CalcBoundingBox()
        
        objetLigne2 = self.ObjectList[2]
        objetLigne2.SetXY(numpy.array([objetLigne1.Points[0][0], objetLigne1.Points[1][1] ]) )
        objetLigne2.CalcBoundingBox()
        
##        positionCentre = objetRect.GetXY()+(objetRect.GetTaille()/2.0)
##        objetTexte = self.ObjectList[3]
##        objetTexte.SetXY(positionCentre)
##        objetTexte.CalcBoundingBox()

    def GetTaille(self) :
        objetRect = self.ObjectList[0]
        return objetRect.WH

    def SetTaille(self, largeur, hauteur):
        objetRect = self.ObjectList[0]
        objetRect.SetTaille(largeur, hauteur)
        objetRect.CalcBoundingBox()        
        BB = objetRect.GetOutlinePoints()
        
        objetLigne1 = self.ObjectList[1]
        objetLigne1.Points[0] = BB[0]
        objetLigne1.Points[1] = BB[2]
        objetLigne1.CalcBoundingBox()
        
        objetLigne2 = self.ObjectList[2]
        objetLigne2.Points[0] = BB[1]
        objetLigne2.Points[1] = BB[3]
        objetLigne2.CalcBoundingBox()
                
##        positionCentre = objetRect.GetXY()+(objetRect.GetTaille()/2.0)
##        objetTexte = self.ObjectList[3]
##        objetTexte.SetXY(positionCentre)
##        objetTexte.CalcBoundingBox()

        

# --------------------------------------------------------------------------------------------------------------------------------------

class Panel_canvas(wx.Panel):
    def __init__(self, parent, infosCategorie=None, taille_page=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_canvas")
        self.parent = parent
        self.ctrl_proprietes = None
        self.listeObjetsFond = []
        self.IDfond = None
        
        self.infosCategorie = infosCategorie
        self.taille_page = taille_page
        
        # FloatCanvas
        self.canvas = FloatCanvas.FloatCanvas(self, Debug=0, BackgroundColor=COULEUR_ZONE_TRAVAIL, style=wx.WANTS_CHARS)
        
        # Propri�t�s
        self.SetMinSize((800, 700)) 
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.canvas, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        
        # Variables
        self.Moving = False
        self.dictSelection = None
        self.resizing = False
        self.startResizing = None
        self.lastPosition = None
        self.grille = None
        self.affichageGrille = True
        
        # Binds
        self.canvas.Bind(FloatCanvas.EVT_MOTION, self.OnMove ) 
        self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.OnLeftUp ) 
        self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.OnLeftDownCanvas ) 
        self.canvas.Bind(FloatCanvas.EVT_RIGHT_DOWN, self.OnRightDownCanvas ) 
        self.canvas.Bind(wx.EVT_KEY_UP, self.OnKeyUp ) 
        self.canvas.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow ) 
    
    def Init_canvas(self):
        self.Init_page() 
        self.Init_fond() 
        self.Init_grille() 
        self.canvas.ZoomToBB()
    
    def Reinit_canvas(self):
        self.canvas.RemoveObject(self.page)
        self.SupprimerFond()
        self.canvas.RemoveObject(self.grille)
        self.Init_canvas() 

    def Init_page(self):
        """ Dessine le fond de page """
        # Ombre de la page
        ombre1 = FloatCanvas.Rectangle( (self.taille_page[0]-1, -EPAISSEUR_OMBRE), (EPAISSEUR_OMBRE+1, self.taille_page[1]), LineWidth=0, LineColor=COULEUR_OMBRE_PAGE, FillColor=COULEUR_OMBRE_PAGE, InForeground=False)
        ombre2 = FloatCanvas.Rectangle( (EPAISSEUR_OMBRE, -EPAISSEUR_OMBRE), (self.taille_page[0]-1, EPAISSEUR_OMBRE+1), LineWidth=0, LineColor=COULEUR_OMBRE_PAGE, FillColor=COULEUR_OMBRE_PAGE, InForeground=False)
        # Fond de page
        rect = FloatCanvas.Rectangle( (0, 0), self.taille_page, LineWidth=1, FillColor=COULEUR_FOND_PAGE, InForeground=False)
        self.page = self.canvas.AddGroup([ombre1, ombre2, rect], InForeground=False)
        
    def Init_grille(self, espace=10, couleur=(240, 240, 240)):
        """ Dessine une grille de fond de page """
        listeLignes = []
        # Dessin des lignes
        for y in range(espace, self.taille_page[1], espace) :
            L = FloatCanvas.Line([(2, y), (self.taille_page[0]-2, y)], LineWidth=1, LineColor=couleur, InForeground=False)
            listeLignes.append(L)
        # Dessin des colonnes
        for x in range(espace, self.taille_page[0], espace) :
            L = FloatCanvas.Line([(x, 2), (x, self.taille_page[1]-2)], LineWidth=1, LineColor=couleur, InForeground=False)
            listeLignes.append(L)
        self.grille = self.canvas.AddGroup(listeLignes, InForeground=False)
        self.affichageGrille = True
    
    def Affiche_grille(self):
        self.affichageGrille = True
        self.grille.Show()
        self.canvas.Draw(True)

    def Cache_grille(self):
        self.affichageGrille = False
        self.grille.Hide()
        self.canvas.Draw(True)
                        
    def AjouterObjet(self, objet):
        """ Ajoute un objet dans le canvas """
        objet.dirty = True
        self.canvas.AddObject(objet)
        if objet.InForeground == True :
            objet.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnClicGaucheObjet)
            objet.Bind(FloatCanvas.EVT_FC_RIGHT_DOWN, self.OnClicDroitObjet)
            if "texte" in objet.categorie :
                objet.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, self.OnModifierTexte)
        
    def OnModifierTexte(self, objet):
        """ Modifier texte sur double-clic """
        dlg = DLG_Saisie_texte_doc.Dialog(self, texte=objet.GetTexte(), listeChamps=self.infosCategorie.champs)
        if dlg.ShowModal() == wx.ID_OK:
            texte = dlg.GetTexte()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        if texte == "" :
            return
        objet.SetTexte(texte)
        objet.dirty = True
        self.Selection(objet, forceDraw=True)

    def OnLeftDownCanvas(self, event):
        self.Deselection() 
    
    def OnRightDownCanvas(self, event):
        pass

    def OnClicGaucheObjet(self, objet):
        """ Clic gauche sur un objet """
        # Activation du d�placement
        if not self.Moving:
            self.Moving = True
            self.decalage = objet.HitCoordsPixel - self.canvas.WorldToPixel(objet.GetXY())
            self.MovingObject = objet
        
        # D�s�lection si autre objet d�j� s�lectionn�
        if self.dictSelection != None :
            if self.dictSelection["objet"] != objet :
                self.Deselection() 
        
        # S�lection de l'objet
        if self.dictSelection == None :
            self.Selection(objet) 
        else:
            if self.dictSelection["objet"] != objet :
                self.Selection(objet) 

    def OnClicDroitObjet(self, objet):
        """ Clic droit sur objet """
        if self.dictSelection == None :
            self.Selection(objet) 
        else:
            if self.dictSelection["objet"] != objet :
                self.Selection(objet) 
        self.MenuContextuel(objet)

    def OnClicPoignee(self, objet):
        if not self.resizing :
            self.resizing = objet.nom
            self.startResizing = objet.HitCoordsPixel
            self.decalage = objet.HitCoordsPixel - self.canvas.WorldToPixel(self.dictSelection["objet"].GetXY())
    
    def OnClicDroitPoignee(self, objet):
        """ Cr�ation du menu contextuel - Poign�e"""
        menu = wx.Menu()
        self.point = objet
        # Supprimer la poign�e
        item = wx.MenuItem(menu, ID_MENU_SUPPRIMER_POINT, _(u"Supprimer ce point"), _(u"Supprimer ce point"), wx.ITEM_NORMAL)
##        item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
        item.SetMarginWidth(16)
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_supprimer_point, id=ID_MENU_SUPPRIMER_POINT)
        # Finalisation du menu
        self.PopupMenu(menu)           
        menu.Destroy()

    def OnMenu_supprimer_point(self, event):
        """ Supprimer le point s�lectionn� """
        objet = self.dictSelection["objet"]
        if len(objet.Points) == 2 :
            dlg = wx.MessageDialog(self, _(u"Un polygone doit disposer d'au moins 2 points !"), _(u"Suppression impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        indexPoint = int(self.point.nom)
        objet.Points = numpy.delete(objet.Points, indexPoint, axis=0)
        objet.dirty = True
        objet.CalcBoundingBox()
        self.Selection(objet, forceDraw=False)
        self.canvas.Draw(True)
    
    def OnClicLignePolygone(self, objet):
        menu = wx.Menu()
        self.coords = objet.HitCoords
        # Supprimer la poign�e
        item = wx.MenuItem(menu, ID_MENU_AJOUTER_POINT, _(u"Ajouter un point ici"), _(u"Ajouter un point ici"), wx.ITEM_NORMAL)
##        item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
        item.SetMarginWidth(16)
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_ajouter_point, id=ID_MENU_AJOUTER_POINT)
        # Finalisation du menu
        self.PopupMenu(menu)           
        menu.Destroy()

    def OnMenu_ajouter_point(self, event):
        """ Ajouter un point sur le polygone """
        objet = self.dictSelection["objet"]
        x, y = self.coords
        resultat = None
        for index in range(0, len(objet.Points)):
            if index < len(objet.Points) - 1 :
                indexSup = index + 1
            else:
                indexSup = 0
            if (objet.Points[index][0] >= x and objet.Points[indexSup][0] <= x) or (objet.Points[indexSup][0] >= x and objet.Points[index][0] <= x):
                if (objet.Points[index][1] >= y and objet.Points[indexSup][1] <= y) or (objet.Points[indexSup][1] >= y and objet.Points[index][1] <= y):
                    resultat = index + 1
        if resultat == None :
            objet.Points = numpy.append(objet.Points, [self.coords,], axis=0 )
        else:
            objet.Points = numpy.insert(objet.Points, resultat, self.coords,axis=0 )
        objet.CalcBoundingBox()
        objet.dirty = True
        self.Selection(objet, forceDraw=False)
        self.canvas.Draw(True)

    def OnMove(self, event):
        """ D�placement """
        # Magn�tisme
        coordsCurseur = event.Coords
        coordsCurseur = (round(coordsCurseur[0]), round(coordsCurseur[1]))
        
##        dc = wx.ScreenDC()
##        x, y = event.GetPosition()
##        print dc.GetPixel(x, y)
        
        # Affichage des coords
##        self.parent.SetStatusText(u"    X : %d mm   Y : %d mm" % coordsCurseur)
        self.afficheStatusBarPerso(x=coordsCurseur[0], y=coordsCurseur[1])
         
        # D�placement
        if self.Moving :
            objet = self.MovingObject
            objet.dirty = True
            nouvellePos = coordsCurseur - self.canvas.ScalePixelToWorld(self.decalage)
            nouvellePos = numpy.array([int(nouvellePos[0]), int(nouvellePos[1])])
            self.DeplacerObjet(objet, newPosition=nouvellePos)
            
        # Redimensionnement
        if self.resizing :
            nomPoignee = self.resizing
            objet = self.dictSelection["objet"]
            objet.dirty = True
            
            # Calcul du delta
            dx = coordsCurseur[0] - self.lastPosition[0]
            dy = coordsCurseur[1] - self.lastPosition[1]
             
            # Redimensionnement d'une LIGNE ou d'un POLYGONE
            if objet.categorie in ("ligne", "polygone") :
                indexPoint = int(nomPoignee)
                point = numpy.array((event.Coords[0], coordsCurseur[1]))
                objet.Points[indexPoint] = point
                objet.CalcBoundingBox()
            
            # Redimensionnement d'un autre type d'objet
            else:
                
                # R�cup�ration des dimensions
                x, y = objet.GetXY()
                largeur, hauteur = objet.GetTaille()
                
                # Conservation des proportions
                if objet.verrouillageProportions == True or wx.GetKeyState(wx.WXK_CONTROL) == True or wx.GetKeyState(wx.WXK_SHIFT)  == True : 
                    if nomPoignee in ("HG", "BD") :
                        dx = -dy * (largeur/hauteur)
                    else:
                        dx = dy * (largeur/hauteur)
                
                # Bord Droit
                if "D" in nomPoignee and objet.verrouillageLargeur == False :
                    if largeur + dx >= objet.largeurMin and largeur + dx <= objet.largeurMax :
                        largeur += dx

                # Bord Haut
                if "H" in nomPoignee and objet.verrouillageHauteur == False :
                    if hauteur + dy >= objet.hauteurMin and hauteur + dy <= objet.hauteurMax :
                        hauteur += dy
                    
                # Bord Gauche
                if "G" in nomPoignee and objet.verrouillageLargeur == False  :
                    if largeur - dx >= objet.largeurMin and largeur - dx <= objet.largeurMax :
                        largeur -= dx
                        x += dx
                
                # Bord Bas
                if "B" in nomPoignee and objet.verrouillageHauteur == False :
                    if hauteur - dy >= objet.hauteurMin and hauteur - dy <= objet.hauteurMax :
                        hauteur -= dy
                        y += dy
                                        
                # Application des modifications
                objet.SetXY(numpy.array((x, y)))
                objet.SetTaille(largeur, hauteur)
                objet.CalcBoundingBox()
            
            self.ResizeCadreSelection(objet)
##            self.Selection(objet, forceDraw=False)
                
            # MAJ du canvas
            self.canvas.Draw(True)
        
        self.lastPosition = coordsCurseur

    def OnLeftUp(self, event):
        if self.Moving:
            self.Moving = False
        if self.resizing :
            self.resizing = False
            # Pour �viter le bug des poign�es qui disparaissent
            self.Selection(self.dictSelection["objet"], forceDraw=True)
    
    def OnKeyUp(self, event):
        if self.dictSelection != None :
            objet = self.dictSelection["objet"]
            codeTouche = event.GetKeyCode()
            # Suppression avec Del et Suppr
            if codeTouche == 8 or codeTouche == 127 :
                self.OnMenu_supprimer(None)
            # D�placement de l'objet avec les fl�ches
            if codeTouche == 314 : self.DeplacerObjet(objet, "gauche")
            if codeTouche == 316 : self.DeplacerObjet(objet, "droite")
            if codeTouche == 315 : self.DeplacerObjet(objet, "haut")
            if codeTouche == 317 : self.DeplacerObjet(objet, "bas")
    
    def DeplacerObjet(self, objet, sens=None, newPosition=None):
        """ D�placement d'un objet avec les touches """
        # D�placement selon un sens
        if sens != None :
            if sens == "haut" : delta = numpy.array([0, 1])
            if sens == "bas" : delta = numpy.array([0, -1])
            if sens == "gauche" : delta = numpy.array([-1, 0])
            if sens == "droite" : delta = numpy.array([1, 0])
        # D�placement selon une nouvelle position
        if newPosition != None :
            delta = newPosition - objet.GetXY() 
        # V�rification si verrouillage de la position
        if objet.verrouillageX == True : delta[0] = 0
        if objet.verrouillageY == True : delta[1] = 0
        # D�placement
        objet.Move(delta)
        objet.dirty = True
##        objet.CalcBoundingBox()
        # Affichage dans le panneau prori�t�s
        if objet.categorie in ("ligne", "polygone") :
            self.ctrl_proprietes.SetObjet(objet)
        else:
            x, y = objet.GetXY() 
            self.ctrl_proprietes.ctrl_position.SetX(x)
            self.ctrl_proprietes.ctrl_position.SetY(y)
        # D�placement du cadre de s�lection
        if self.dictSelection != None :
            self.dictSelection["cadre"].Move(delta)
            for poignee in self.dictSelection["poignees"] :
                poignee.Move(delta)
        # MAJ du canvas
        self.canvas.Draw(True)

    def ResizeCadreSelection(self, objet):
        """ Redimensionnement du cadre de s�lection """
        cadre = self.dictSelection["cadre"]
        poignees = self.dictSelection["poignees"]
                
        if objet.categorie in ("ligne", "polygone") :
            # ----- ligne ou d'un polygone -----
            index = 0
            for point in objet.Points :
                xy = numpy.array([point[0], point[1]])
                cadre.Points[index] = xy
                poignees[index].XY = xy
                index += 1
            cadre.Points[index] = poignees[0].XY

        else:
            # ----- S�lection rectangulaire -----
            points = objet.GetOutlinePoints()
            index = 0
            for point in points :
                cadre.Points[index] = point
                index += 1
            
            # Poign�es du milieu
            if objet.verrouillageProportions != True :
                poignees[4].XY = numpy.array((points[0][0],  points[0][1] + ((points[1][1] - points[0][1] ) / 2.0)))
                poignees[5].XY = numpy.array((points[2][0] - (points[2][0] - points[1][0]) / 2.0, points[1][1])) 
                poignees[6].XY = numpy.array((points[2][0], points[0][1] + ((points[1][1] - points[0][1] ) / 2.0) )) 
                poignees[7].XY = numpy.array((points[2][0] - (points[2][0] - points[1][0]) / 2.0, points[0][1])) 
            
            # Poign�es des coins
            if objet.categorie not in ["ligne_texte", "bloc_texte"] :
                for index in range(0, 4) :
                    poignees[index].XY = points[index]
        
        # MAJ du panneau propri�t�s
        self.ctrl_proprietes.SetObjet(objet)
        
    def Selection(self, objet, forceDraw=True, MAJpanel_proprietes=True):
        """ Cr�ation du cadre de s�lection """
        self.Deselection(forceDraw=False, MAJpanel_proprietes=False)
        self.dictSelection = {}
        
        # M�morisation de l'objet s�lectionn�
        self.dictSelection["objet"] = objet
        self.dictSelection["poignees"] = []
        
        if objet.categorie in ("ligne", "polygone") :
            # ----- S�lection d'une ligne ou d'un polygone -----
            points = numpy.copy(objet.Points)
            points = numpy.append(points, [points[0]],axis=0 )
            ligne = MovingLine(points, LineWidth=1, LineColor=COULEUR_CADRE_SELECTION, LineStyle="Dot", InForeground=True) 
            self.canvas.AddObject(ligne)
            self.dictSelection["cadre"] = ligne
            
            if objet.categorie == "polygone" :
                    ligne.Bind(FloatCanvas.EVT_FC_RIGHT_DOWN, self.OnClicLignePolygone)
                    
            index = 0
            for point in objet.Points :
                poignee = self.canvas.AddSquarePoint(point, Color=COULEUR_CADRE_SELECTION, Size=6, InForeground=True)
                poignee.nom = u"%d" % index
                poignee.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnClicPoignee)
                if objet.categorie == "polygone" :
                    poignee.Bind(FloatCanvas.EVT_FC_RIGHT_DOWN, self.OnClicDroitPoignee)
                self.dictSelection["poignees"].append(poignee)
                index += 1

        else:
            
            # ----- S�lection rectangulaire -----
            points = objet.GetOutlinePoints()
            cadre = MovingPolygon(points, LineWidth=1, LineColor=COULEUR_CADRE_SELECTION, LineStyle="Dot", FillStyle = "Transparent", InForeground=True) 
            self.canvas.AddObject(cadre)
            self.dictSelection["cadre"] = cadre
            # Dessin des poign�es d'agrandissement
            listeNoms = ["BG", "HG", "HD", "BD"]
            
            # Cr�ation des poign�es du milieu
            if objet.verrouillageProportions != True :
                points = numpy.append(points, [numpy.array((points[0][0],  points[0][1] + ((points[1][1] - points[0][1] ) / 2.0))) ],axis=0 ) # MG
                points = numpy.append(points, [numpy.array((points[2][0] - (points[2][0] - points[1][0]) / 2.0, points[1][1])) ],axis=0 ) # MH
                points = numpy.append(points, [numpy.array((points[2][0], points[0][1] + ((points[1][1] - points[0][1] ) / 2.0) )) ],axis=0 ) # MD
                points = numpy.append(points, [numpy.array((points[2][0] - (points[2][0] - points[1][0]) / 2.0, points[0][1])) ],axis=0 )  # MB
                listeNoms.extend(["MG", "MH", "MD", "MB"])
            
            # Cr�ation des poign�es des coins
            index = 0
            if objet.categorie not in ["ligne_texte", "bloc_texte"] :
                for point in points :
                    nom = listeNoms[index]
                    poignee = self.canvas.AddSquarePoint(point, Color=COULEUR_CADRE_SELECTION, Size=6, InForeground=True)
                    poignee.nom = nom
                    poignee.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnClicPoignee)
                    self.dictSelection["poignees"].append(poignee)
                    index += 1
                
        # MAJ du canvas
        if forceDraw == True :
            self.canvas.Draw(True)
            self.AfficheAstuce() # Affiche une astuce
            
        # MAJ du panel Propri�t�s
        if MAJpanel_proprietes == True :
            self.ctrl_proprietes.SetObjet(objet)

    def Deselection(self, forceDraw=True, MAJpanel_proprietes=True):
        """ D�s�lection d'un objet """
        if self.dictSelection != None :
            self.canvas.RemoveObject(self.dictSelection["cadre"])
            for poignee in self.dictSelection["poignees"] :
                self.canvas.RemoveObject(poignee)
            self.dictSelection = None

##        self.parent.SetStatusText(u"", 1) 
        self.afficheStatusBarPerso(info=u"")
        
        if forceDraw == True :
            self.canvas.Draw(False)
        
        if MAJpanel_proprietes == True :
            self.ctrl_proprietes.SetObjet(None)
        
##        self.parent.SetStatusText(u"", 1) 
        self.afficheStatusBarPerso(info=u"")

    def AfficheAstuce(self):
        """ Affiche une astuce dans la statusBar """
        index = random.randint(0, len(ASTUCES)-1)
##        self.parent.SetStatusText(ASTUCES[index], 1) 
        self.afficheStatusBarPerso(info=ASTUCES[index])
        
    def MenuContextuel(self, objet=None):
        """ Cr�ation du menu contextuel """
        menu = wx.Menu()
        
        if "texte" in objet.categorie :
            # Modifier le texte
            item = wx.MenuItem(menu, ID_MENU_MODIFIER_TEXTE, _(u"Modifier le texte"), _(u"Modifier le texte"), wx.ITEM_NORMAL)
            item.SetBitmap(wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnMenu_modifier_texte, id=ID_MENU_MODIFIER_TEXTE)
            
            menu.AppendSeparator()

        if objet.categorie == "image" :
            if objet.typeImage.startswith("fichier"):
                # Rotation Gauche
                item = wx.MenuItem(menu, ID_MENU_ROTATION_GAUCHE, _(u"Rotation vers la gauche"), _(u"Rotation vers la gauche"), wx.ITEM_NORMAL)
                item.SetBitmap(wx.Bitmap("Images/16x16/Rotation_gauche.png", wx.BITMAP_TYPE_PNG))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnMenu_rotationGauche, id=ID_MENU_ROTATION_GAUCHE)

                # Rotation Droite
                item = wx.MenuItem(menu, ID_MENU_ROTATION_DROITE, _(u"Rotation vers la droite"), _(u"Rotation vers la droite"), wx.ITEM_NORMAL)
                item.SetBitmap(wx.Bitmap("Images/16x16/Rotation_droite.png", wx.BITMAP_TYPE_PNG))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnMenu_rotationDroite, id=ID_MENU_ROTATION_DROITE)
                
                menu.AppendSeparator()

        # Avancer l'objet
        item = wx.MenuItem(menu, ID_MENU_AVANCER, _(u"Avancer"), _(u"Reculer l'objet"), wx.ITEM_NORMAL)
        item.SetBitmap(wx.Bitmap("Images/16x16/Avancer_objet.png", wx.BITMAP_TYPE_PNG))
        item.SetMarginWidth(16)
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_avancer, id=ID_MENU_AVANCER)

        # Reculer objet
        item = wx.MenuItem(menu, ID_MENU_RECULER, _(u"Reculer"), _(u"Reculer l'objet"), wx.ITEM_NORMAL)
        item.SetBitmap(wx.Bitmap("Images/16x16/Reculer_objet.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_reculer, id=ID_MENU_RECULER)
        
        menu.AppendSeparator()

        # Mettre en avant-plan
        item = wx.MenuItem(menu, ID_MENU_AVANTPLAN, _(u"Mettre � l'avant-plan"), _(u"Mettre � l'avant-plan l'objet"), wx.ITEM_NORMAL)
        item.SetBitmap(wx.Bitmap("Images/16x16/Avant-plan.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_avantplan, id=ID_MENU_AVANTPLAN)

        # Mettre en arri�re-plan
        item = wx.MenuItem(menu, ID_MENU_ARRIEREPLAN, _(u"Mettre en arri�re-plan"), _(u"Mettre en arri�re-plan l'objet"), wx.ITEM_NORMAL)
        item.SetBitmap(wx.Bitmap("Images/16x16/Arriere-plan.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_arriereplan, id=ID_MENU_ARRIEREPLAN)

        menu.AppendSeparator()

        # Dupliquer l'objet
##        item = wx.MenuItem(menu, ID_MENU_DUPLIQUER, _(u"Dupliquer"), _(u"Dupliquer l'objet"), wx.ITEM_NORMAL)
##        item.SetBitmap(wx.Bitmap("Images/16x16/Copier.png", wx.BITMAP_TYPE_PNG))
##        menu.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.OnMenu_dupliquer, id=ID_MENU_DUPLIQUER)

        # Supprimer objet
        item = wx.MenuItem(menu, ID_MENU_SUPPRIMER, _(u"Supprimer"), _(u"Supprimer l'objet"), wx.ITEM_NORMAL)
        item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenu_supprimer, id=ID_MENU_SUPPRIMER)
        if objet.obligatoire == True :
            item.Enable(False)

        # Finalisation du menu
        self.PopupMenu(menu)           
        menu.Destroy()
    
    def OnMenu_rotationGauche(self, event):
        objet = self.dictSelection["objet"]
        objet.Rotation(False)
        self.Selection(objet, forceDraw=True)

    def OnMenu_rotationDroite(self, event):
        objet = self.dictSelection["objet"]
        objet.Rotation(True)
        self.Selection(objet, forceDraw=True)

    def OnMenu_modifier_texte(self, event):
        objet = self.dictSelection["objet"]
        self.OnModifierTexte(objet)
        
    def OnMenu_arriereplan(self, event):
        """ Mettre objet � l'arri�re-plan """
        objet = self.dictSelection["objet"]
        objet.dirty = True
        self.canvas._ForeDrawList.remove(objet)
        self.canvas._ForeDrawList.insert(0, objet)
        self.canvas.Draw(True)
        
    def OnMenu_avantplan(self, event):
        """ Mettre objet � l'avant-plan """
        objet = self.dictSelection["objet"]
        objet.dirty = True
        self.canvas._ForeDrawList.remove(objet)
        newIndex = len(self.canvas._ForeDrawList) - len(self.dictSelection["poignees"]) - 1
        self.canvas._ForeDrawList.insert(newIndex, objet)
        self.canvas.Draw(True)

    def OnMenu_reculer(self, event):
        """ Reculer l'objet """
        objet = self.dictSelection["objet"]
        objet.dirty = True
        index = self.canvas._ForeDrawList.index(objet)
        if index > 0 :
            self.canvas._ForeDrawList.remove(objet)
            self.canvas._ForeDrawList.insert(index-1, objet)
            self.canvas.Draw(True)

    def OnMenu_avancer(self, event):
        """ Avancer l'objet """
        objet = self.dictSelection["objet"]
        objet.dirty = True
        index = self.canvas._ForeDrawList.index(objet)
        if index < (len(self.canvas._ForeDrawList) - len(self.dictSelection["poignees"]) - 2) :
            self.canvas._ForeDrawList.remove(objet)
            self.canvas._ForeDrawList.insert(index+1, objet)
            self.canvas.Draw(True)

    def OnMenu_dupliquer(self, event):
        """ Dupliquer l'objet """
##        objet = self.dictSelection["objet"]
##        self.Deselection(forceDraw=False)
##        newObjet = copy.deepcopy(objet)
##        self.AjouterObjet(newObjet)
##        delta = numpy.array([5, 5])
##        newObjet.Move(delta)
##        self.Selection(newObjet, forceDraw=True)

    def OnMenu_supprimer(self, event):
        """ Supprimer l'objet """
        objet = self.dictSelection["objet"]
        objet.dirty = True
        if objet.obligatoire == True :
            dlg = wx.MessageDialog(self, _(u"Cet objet est obligatoire. Vous ne pouvez donc pas le supprimer !"), _(u"Suppression impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.Deselection(forceDraw=False)
        self.canvas.RemoveObject(objet)
        self.canvas.Draw(True)
    
    def Imprimer(self):
        """ Test d'impression PDF """
        self.Deselection(forceDraw=True)
        listeObjets = self.canvas._ForeDrawList
        listeObjetsFond = self.listeObjetsFond
        Impression(taille_page=self.taille_page, listeObjets=listeObjets, listeObjetsFond=listeObjetsFond)
    
    def OnLeaveWindow(self, event):
        self.parent.ctrl_infos.EffaceCoords()
        
    def afficheStatusBarPerso(self, x=None, y=None, info=None):
        # Affichage des coordonn�es de la souris
        self.parent.ctrl_infos.SetCoords(x, y)
        self.parent.ctrl_infos.SetInfo(info)
    
    def GetObjets(self):
        self.Deselection(forceDraw=True)
        listeObjets = self.canvas._ForeDrawList
        return listeObjets
    
    def GetPhotoPage(self):
        """ Prend une photo de la page """
        self.Deselection(forceDraw=False)
        self.canvas.ZoomToBB()
        self.Cache_grille()
        objetPage = self.page.ObjectList[2]
        BB = objetPage.BoundingBox
        OutlinePoints = numpy.array( ( (BB[0,0], BB[0,1]), (BB[0,0], BB[1,1]), (BB[1,0], BB[1,1]), (BB[1,0], BB[0,1]),) )
        x, y = self.canvas.WorldToPixel(OutlinePoints[1]) 
        largeur, hauteur = self.canvas.ScaleWorldToPixel(objetPage.WH)
        bmp = self.canvas._ForegroundBuffer
        bmp = bmp.GetSubBitmap(wx.Rect(x, y, largeur, -hauteur))
        return bmp
    
    def SupprimerFond(self):
        # Suppression du fond actuel
        for objet in self.listeObjetsFond :
            self.canvas.RemoveObject(objet)
        self.listeObjetsFond = []
    
    def SetFond(self, IDmodele=None):
        self.IDfond = IDmodele
        self.SupprimerFond() 
        self.Reinit_canvas()
    
    def Init_fond(self):
        if self.IDfond != None :
            self.listeObjetsFond = self.parent.Importation(self.IDfond, InForeground=False)
        self.canvas.Draw(True)

##class MyFrame(wx.Frame):
##    def __init__(self, parent, nom="", observations=u"", IDfond=None, categorie=None, taille_page=(210, 297), size=(800, 600)):
##        wx.Frame.__init__(self, parent, -1, title=_(u"designer"), name="designer", size=size, style=wx.DEFAULT_FRAME_STYLE|wx.CLIP_CHILDREN)

class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None, nom="", observations=u"", IDfond=None, categorie=None, taille_page=(210, 297), size=(800, 600)):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent     
        self.IDmodele = IDmodele
        self.categorie = categorie
        self.taille_page = taille_page
        
        self.listeInitialeObjets = []
        
        # DLG Attente
        dlgAttente = PBI.PyBusyInfo(_(u"Veuillez patienter durant l'initialisation de Noedoc..."), parent=None, title=_(u"Initialisation de Noedoc"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 

        # Recherche des donn�es de la cat�gorie
        if self.categorie == "fond" : self.infosCategorie = Fond()
        if self.categorie == "facture" : self.infosCategorie = Facture()
        if self.categorie == "rappel" : self.infosCategorie = Rappel()
        if self.categorie == "attestation" : self.infosCategorie = Attestation()
        if self.categorie == "reglement" : self.infosCategorie = Reglement()
        if self.categorie == "individu" : self.infosCategorie = Individu()
        if self.categorie == "famille" : self.infosCategorie = Famille()
        if self.categorie == "inscription" : self.infosCategorie = Inscription()
        if self.categorie == "cotisation" : self.infosCategorie = Cotisation()
        if self.categorie == "attestation_fiscale" : self.infosCategorie = Attestation_fiscale()

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        # Propri�t�s
        self.SetMinSize((920, 740))

        # Barres d'outils
        self.toolbar1 = self.MakeToolBar1()
        self.toolbar2 = self.MakeToolBar2()
        self.toolbar3 = self.MakeToolBar3()
            
        # Cr�ation des widgets
        self.ctrl_canvas = Panel_canvas(self, infosCategorie=self.infosCategorie, taille_page=taille_page)
                
        # Cr�ation des panels d�tachables
        self.ctrl_infos = Panel_infos(self)
        self.ctrl_commandes = Panel_commandes(self)
        self.ctrl_proprietes_doc = Panel_proprietes_doc(self, self.ctrl_canvas, categorie=categorie)
        self.ctrl_proprietes_objet = Panel_proprietes_objet(self, self.ctrl_canvas)
        self.ctrl_canvas.ctrl_proprietes = self.ctrl_proprietes_objet
        
        # Cr�ation des panels amovibles
        self._mgr.AddPane(self.ctrl_infos, aui.AuiPaneInfo().
                          Name("infos").Caption(_(u"Infos")).
                          Bottom().Layer(0).Position(1).CaptionVisible(False).CloseButton(False).MaximizeButton(False).MinSize((-1, 10)))

        self._mgr.AddPane(self.ctrl_commandes, aui.AuiPaneInfo().
                          Name("commandes").Caption(_(u"Commandes")).
                          Bottom().Layer(1).Position(2).CaptionVisible(False).CloseButton(False).MaximizeButton(False).MinSize((-1, 50)))

        self._mgr.AddPane(self.ctrl_proprietes_doc, aui.AuiPaneInfo().
                          Name("proprietes_doc").Caption(_(u"Propri�t�s du mod�le")).
                          Right().Layer(1).Position(1).Fixed().CloseButton(False).MaximizeButton(False))
                        
        self._mgr.AddPane(self.ctrl_proprietes_objet, aui.AuiPaneInfo().
                          Name("proprietes_objet").Caption(_(u"Propri�t�s de l'objet")).
                          Right().Layer(1).Position(2).CloseButton(False).MaximizeButton(False).MinSize((160, -1)))
        
        # Cr�ation du panel central
        self._mgr.AddPane(self.ctrl_canvas, aui.AuiPaneInfo().Name("canvas").
                          CenterPane())
        
        # Cr�ation des barres d'outils
        self._mgr.AddPane(self.toolbar1, aui.AuiPaneInfo().
                          Name("barreOutil_modes").Caption("Modes").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))
        
        self._mgr.AddPane(self.toolbar2, aui.AuiPaneInfo().
                          Name("barreOutils_objets").Caption("Objets").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))
        
        self._mgr.AddPane(self.toolbar3, aui.AuiPaneInfo().
                          Name("barreOutils_options").Caption("Options").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))

        self._mgr.Update()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Logo
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        # Remplit propri�t�s doc
        self.ctrl_proprietes_doc.SetNom(nom)
        self.ctrl_proprietes_doc.SetObservations(observations)
        self.ctrl_proprietes_doc.SetFond(IDfond)
        self.ctrl_proprietes_doc.SetTaille(taille_page)
                
        # Init Canvas
        self.ctrl_canvas.IDfond = IDfond
        self.CenterOnScreen()
        self.ctrl_canvas.Init_canvas()
        
        del dlgAttente
        
        # Importation
        if self.IDmodele != None :
            self.Importation(self.IDmodele)
        else:
            self.CreationObjetsObligatoires()
            # Demande le nom du nouveau mod�le
            dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir un nom pour ce nouveau mod�le :"), _(u"Nouveau mod�le"))
            if dlg.ShowModal() == wx.ID_OK:
                self.ctrl_proprietes_doc.SetNom(dlg.GetValue())
            dlg.Destroy()
        
        self.CenterOnScreen()
        

    def CreationObjetsObligatoires(self):
        for objet in self.infosCategorie.speciaux :
            if objet["obligatoire"] == True :
                self.AjouterSpecial(objet)
        
    def MakeToolBar1(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))
        
        tbar.AddSimpleTool(ID_OUTIL_CURSEUR, _(u"Curseur"), wx.Bitmap("Images/32x32/Curseur.png", wx.BITMAP_TYPE_ANY), _(u"Curseur"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.OnOutil_curseur, id=ID_OUTIL_CURSEUR)
        tbar.ToggleTool(ID_OUTIL_CURSEUR, True)
        
        tbar.AddSimpleTool(ID_OUTIL_DEPLACER, _(u"D�placer"), wx.Bitmap("Images/32x32/Main.png", wx.BITMAP_TYPE_ANY), _(u"D�placer"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.OnOutil_deplacer, id=ID_OUTIL_DEPLACER)
        
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_OUT, _(u"Zoom arri�re"), wx.Bitmap("Images/32x32/zoom_moins.png", wx.BITMAP_TYPE_ANY), _(u"Zoom arri�re"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.OnOutil_zoom_moins, id=ID_OUTIL_ZOOM_OUT)

        tbar.AddSimpleTool(ID_OUTIL_ZOOM_IN, _(u"Zoom avant"), wx.Bitmap("Images/32x32/zoom_plus.png", wx.BITMAP_TYPE_ANY), _(u"Zoom avant"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.OnOutil_zoom_plus, id=ID_OUTIL_ZOOM_IN)

        tbar.AddSeparator()
        
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_AJUSTER, _(u"Ajuster et centrer l'affichage"), wx.Bitmap("Images/32x32/Ajuster.png", wx.BITMAP_TYPE_ANY), _(u"Ajuster et centrer l'affichage"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_ajuster, id=ID_OUTIL_ZOOM_AJUSTER)
        
        tbar.AddSeparator()
        
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_APERCU, _(u"Afficher un aper�u PDF"), wx.Bitmap("Images/32x32/Apercu.png", wx.BITMAP_TYPE_ANY), _(u"Afficher un aper�u PDF"))
        self.Bind(wx.EVT_TOOL, self.OnAffichage_apercu, id=ID_OUTIL_AFFICHAGE_APERCU)

        tbar.Realize()
        return tbar

    def MakeToolBar2(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))
        
##        tbar.AddSimpleTool(ID_OUTIL_OBJET_TEXTE_LIGNE, _(u"Ins�rer une ligne de texte"), wx.Bitmap("Images/32x32/Texte_ligne.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer une ligne de texte"))
##        self.Bind(wx.EVT_TOOL, self.OnOutil_texteLigne, id=ID_OUTIL_OBJET_TEXTE_LIGNE)

        tbar.AddSimpleTool(ID_OUTIL_OBJET_TEXTE_BLOC, _(u"Ins�rer un bloc de texte multi-lignes"), wx.Bitmap("Images/32x32/Texte_ligne.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer un bloc de texte multi-lignes"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_texteBloc, id=ID_OUTIL_OBJET_TEXTE_BLOC)

        tbar.AddSimpleTool(ID_OUTIL_OBJET_RECTANGLE, _(u"Ins�rer un rectangle"), wx.Bitmap("Images/32x32/Rectangle.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer un rectangle"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_rectangle, id=ID_OUTIL_OBJET_RECTANGLE)
        
        tbar.AddSimpleTool(ID_OUTIL_OBJET_LIGNE, _(u"Ins�rer une ligne"), wx.Bitmap("Images/32x32/Ligne.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer une ligne"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_ligne, id=ID_OUTIL_OBJET_LIGNE)
        
        tbar.AddSimpleTool(ID_OUTIL_OBJET_CERCLE, _(u"Ins�rer une ellipse"), wx.Bitmap("Images/32x32/Cercle.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer une ellipse"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_cercle, id=ID_OUTIL_OBJET_CERCLE)
        
        tbar.AddSimpleTool(ID_OUTIL_OBJET_POLYGONE, _(u"Ins�rer un polygone"), wx.Bitmap("Images/32x32/Polygone.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer un polygone"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_polygone, id=ID_OUTIL_OBJET_POLYGONE)

        tbar.AddSimpleTool(ID_OUTIL_OBJET_IMAGE_DROPDOWN, _(u"Ins�rer une image"), wx.Bitmap("Images/32x32/Image.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer une image"))
        self.Bind(wx.EVT_TOOL, self.OnOutil_image, id=ID_OUTIL_OBJET_IMAGE)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnDropDownImage, id=ID_OUTIL_OBJET_IMAGE_DROPDOWN)
        tbar.SetToolDropDown(ID_OUTIL_OBJET_IMAGE_DROPDOWN, True)
        
        if len(self.infosCategorie.codesbarres) > 0 :
            tbar.AddSimpleTool(ID_OUTIL_OBJET_BARCODE_DROPDOWN, _(u"Ins�rer un code-barres"), wx.Bitmap("Images/32x32/Codebarres.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer un code-barres"))
            self.Bind(wx.EVT_TOOL, self.OnOutil_codebarres, id=ID_OUTIL_OBJET_CODEBARRES)
            self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnDropDownBarcode, id=ID_OUTIL_OBJET_BARCODE_DROPDOWN)
            tbar.SetToolDropDown(ID_OUTIL_OBJET_BARCODE_DROPDOWN, True)

        if len(self.infosCategorie.speciaux) > 0 :
            tbar.AddSimpleTool(ID_OUTIL_OBJET_SPECIAL_DROPDOWN, _(u"Ins�rer un objet sp�cial"), wx.Bitmap("Images/32x32/Special.png", wx.BITMAP_TYPE_ANY), _(u"Ins�rer un objet sp�cial"))
            self.Bind(wx.EVT_TOOL, self.OnOutil_special, id=ID_OUTIL_OBJET_SPECIAL)
            self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnDropDownSpecial, id=ID_OUTIL_OBJET_SPECIAL_DROPDOWN)
            tbar.SetToolDropDown(ID_OUTIL_OBJET_SPECIAL_DROPDOWN, True)
                
        tbar.Realize()
        return tbar

    def MakeToolBar3(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))

        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_GRILLE, _(u"Afficher la grille"), wx.Bitmap("Images/32x32/Grille.png", wx.BITMAP_TYPE_ANY), _(u"Afficher la grille"), aui.ITEM_CHECK)
        self.Bind(wx.EVT_TOOL, self.OnAffichage_grille, id=ID_OUTIL_AFFICHAGE_GRILLE)
        tbar.ToggleTool(ID_OUTIL_AFFICHAGE_GRILLE, True)
        
        tbar.Realize()
        return tbar

    def MenuOutils(self):
        # Cr�ation du menu Outils
        menuPop = wx.Menu()
            
        item = wx.MenuItem(menuPop, 10, _(u"Ins�rer un texte"), _(u"Ins�rer un texte"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Forfait.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnOutil_texteBloc, id=10)
                
        menuPop.AppendSeparator()
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnOutil_curseur(self, event):
        self.ctrl_canvas.canvas.SetMode(GUIMode.GUIMouse())
    
    def OnOutil_deplacer(self, event):
        self.ctrl_canvas.canvas.SetMode(GUIMode.GUIMove())

    def OnOutil_zoom_moins(self, event):
        self.ctrl_canvas.canvas.SetMode(GUIMode.GUIZoomOut())

    def OnOutil_zoom_plus(self, event):
        self.ctrl_canvas.canvas.SetMode(GUIMode.GUIZoomIn())
        
    def OnOutil_ajuster(self,Event):
        self.ctrl_canvas.canvas.ZoomToBB()
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_rectangle(self, event):
        """ Insertion d'un rectangle """
        taille = (100, 60)
        
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - taille[0]/2), int(y - taille[1]/2)
        
        # Insertion
        objet = AjouterRectangle(xy=(x, y), taille=taille, 
                    couleurTrait=(0, 0, 0), epaissTrait=0.25, 
                    coulRemplis=COULEUR_DEFAUT_OBJET)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_ligne(self, event):
        """ Insertion d'une ligne """
        longueurLigne = 100
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x = x - longueurLigne/2
        x, y = int(x), int(y)
        points = [(x, y), (x+longueurLigne, y)]
        # Insertion
        objet = AjouterLigne(points, couleurTrait=(0, 0, 0), epaissTrait=0.25)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_cercle(self, event):
        """ Insertion d'une ellipse """
        taille = (80, 80)
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - taille[0]/2), int(y - taille[1]/2)
        # Insertion
        objet = AjouterEllipse(xy=(x, y), taille=taille, 
                    couleurTrait=(0, 0, 0), epaissTrait=0.25, 
                    coulRemplis=COULEUR_DEFAUT_OBJET)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_polygone(self, event):
        """ Insertion d'un polygone """
        taille = (90, 80)
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - taille[0]/2), int(y + 12)
        points = [(x, y), (x+45, y+30), (x+90, y), (x+70, y-50), (x+20, y-50)]
        # Insertion
        objet = AjouterPolygone(points, 
                    couleurTrait=(0, 0, 0), epaissTrait=0.25, 
                    coulRemplis=COULEUR_DEFAUT_OBJET)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 
    
    def OnOutil_image(self, event):
        self.OnDropDownImage(None)

    def OnDropDownImage(self, event):
        if 1 == 1 :#event.IsDropDownClicked():
            tb = event.GetEventObject()
            tb.SetToolSticky(event.GetId(), True)

            # create the popup menu
            menuPopup = wx.Menu()
            
            # Importation d'une image
            item = wx.MenuItem(menuPopup, 10001, _(u"Importer une image"), _(u"Importer une image"), wx.ITEM_NORMAL)
            item.SetBitmap(wx.Bitmap("Images/32x32/Image_charger.png", wx.BITMAP_TYPE_PNG))
            item.SetMarginWidth(32)
            menuPopup.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnOutil_image_charger, id=10001)

            # Importation du logo de l'organisateur
            img, exists = GetLogo_organisateur() 
            if img != None :
                tailleMaxi = 32
                largeur, hauteur = img.GetSize()
                if max(largeur, hauteur) > tailleMaxi :
                    if largeur > hauteur :
                        hauteur = hauteur * tailleMaxi / largeur
                        largeur = tailleMaxi
                    else:
                        largeur = largeur * tailleMaxi / hauteur
                        hauteur = tailleMaxi
                img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
                bmp = wx.BitmapFromImage(img)
            else:
                bmp = wx.Bitmap("Images/32x32/Image_absente.png", wx.BITMAP_TYPE_PNG)
            item = wx.MenuItem(menuPopup, 10002, _(u"Ins�rer le logo de l'organisateur"), _(u"Ins�rer le logo de l'organisateur"), wx.ITEM_NORMAL)
            item.SetBitmap(bmp)
            menuPopup.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnOutil_image_logo, id=10002)

            # Importation d'une photo individuelle
            if self.infosCategorie.photosIndividuelles == True :
                item = wx.MenuItem(menuPopup, 10003, _(u"Ins�rer une photo individuelle"), _(u"Ins�rer une photo individuelle"), wx.ITEM_NORMAL)
                item.SetBitmap(wx.Bitmap("Images/32x32/Personnes.png", wx.BITMAP_TYPE_PNG))
                menuPopup.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnOutil_image_photo, id=10003)

            # line up our menu with the button
            rect = tb.GetToolRect(event.GetId())
            pt = tb.ClientToScreen(rect.GetBottomLeft())
            pt = self.ScreenToClient(pt)

            self.PopupMenu(menuPopup, pt)

            # Pour �viter que les menus suivants soient d�form�s 
            item.SetMarginWidth(16)

            # make sure the button is "un-stuck"
            tb.SetToolSticky(event.GetId(), False)

    def OnOutil_image_charger(self, event):
        """ Insertion d'une image """
        # S�lection d'une image
        self.repCourant = os.getcwd()
        wildcard = "Toutes les images (*.bmp; *.gif; *.jpg; *.png)|*.bmp; *.gif; *.jpg; *.png|Image JPEG (*.jpg)|*.jpg|Image PNG (*.png)|*.png|Image GIF (*.gif)|*.gif|Tous les fichiers (*.*)|*.*"
        # R�cup�ration du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture de la fen�tre de dialogue
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
        
##        # Recadre la photo
##        import DLG_Editeur_photo_2
##        dlg = DLG_Editeur_photo_2.MyDialog(self, image=nomFichierLong, titre=_(u"Redimensionnez l'image si vous le souhaitez"))
##        if dlg.ShowModal() == wx.ID_OK:
##            bmp = dlg.GetBmp()
##            dlg.Destroy()
##        else:
##            dlg.Destroy()
##            return 
        
        # D�termine la taille de l'image
        taille = os.path.getsize(nomFichierLong)
        if taille > 999999 :
            dlg = wx.MessageDialog(self, _(u"La taille de cette image est sup�rieure � 1 Mo !\nVous devez donc la compresser avant de l'importer..."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Charge l'image
        img = wx.Image(nomFichierLong)
        
        # D�termine le type d'image
        if nomFichierLong.endswith("png"):
            typeImage = "fichier-png"
        else:
            typeImage = "fichier-jpg"
            
##        # Test de calcul de la taille de l'image
##        buffer = cStringIO.StringIO()
##        img.SaveStream(buffer, wx.BITMAP_TYPE_ANY) 
##        print "Taille de l'image =", FonctionsPerso.Formate_taille_octets(buffer.tell())
        
        # Conversion de la taille px en mm
        largeur, hauteur = img.GetSize()
        largeur, hauteur = int(largeur * 0.264583333), int(hauteur * 0.264583333)
        
        # Recadre l'image
        tailleMaxi = max(self.taille_page)
        if max(largeur, hauteur) > tailleMaxi :
            if largeur > hauteur :
                hauteur = hauteur * tailleMaxi / largeur
                largeur = tailleMaxi
            else:
                largeur = largeur * tailleMaxi / hauteur
                hauteur = tailleMaxi
##            img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)        
        
        bmp = wx.BitmapFromImage(img)
        
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - largeur/2), int(y - hauteur/2)
        
        # Insertion
        objet = AjouterImage(bmp, (x, y), hauteur, typeImage=typeImage)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 
    
    def OnOutil_image_logo(self, event):
        """ Importer le logo de l'organisateur """
        img, exists = GetLogo_organisateur() 
        bmp = wx.BitmapFromImage(img)
        
        # Conversion de la taille px en mm
        largeur, hauteur = bmp.GetSize()
        largeur, hauteur = int(largeur * 0.264583333), int(hauteur * 0.264583333)
        
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - largeur/2), int(y - hauteur/2)

         # Insertion
        objet = AjouterImage(bmp, (x, y), hauteur, nom=_(u"Logo de l'organisateur"), typeImage="logo")
        objet.exists = exists
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 
    
    def OnOutil_image_photo(self, event):
        bmp = wx.Bitmap("Images/128x128/Femme.png", wx.BITMAP_TYPE_ANY)
        
        # Conversion de la taille px en mm
        largeur, hauteur = bmp.GetSize()
        largeur, hauteur = int(largeur * 0.264583333), int(hauteur * 0.264583333)
        
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - largeur/2), int(y - hauteur/2)

        objet = AjouterImage(bmp, (x, y), hauteur, nom=_(u"Photo individuelle"), typeImage="photo")
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_codebarres(self, event):
        self.OnDropDownBarcode(None)

    def OnDropDownBarcode(self, event):
        if 1 == 1 :#event.IsDropDownClicked():
            tb = event.GetEventObject()
            tb.SetToolSticky(event.GetId(), True)

            # create the popup menu
            menuPopup = wx.Menu()
            
            # Importation d'une image
            index = 0
            for nom, exemple, code in self.infosCategorie.codesbarres :
                id = 10000 + index
                item = wx.MenuItem(menuPopup, id, _(u"Ins�rer le code-barres '%s'") % nom, _(u"Ins�rer le code-barres '%s'") % nom, wx.ITEM_NORMAL)
                item.SetBitmap(wx.Bitmap("Images/32x32/Codebarres.png", wx.BITMAP_TYPE_PNG))
                item.SetMarginWidth(32)
                menuPopup.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnOutil_inserer_barcode, id=id)
                index += 1

            # line up our menu with the button
            rect = tb.GetToolRect(event.GetId())
            pt = tb.ClientToScreen(rect.GetBottomLeft())
            pt = self.ScreenToClient(pt)

            self.PopupMenu(menuPopup, pt)
            
            # Pour �viter que les menus suivants soient d�form�s 
            item.SetMarginWidth(16)

            # make sure the button is "un-stuck"
            tb.SetToolSticky(event.GetId(), False)

    def OnOutil_inserer_barcode(self, event):
        index = event.GetId() - 10000
        nom, exemple, champ = self.infosCategorie.codesbarres[index]
        nom = _(u"Code-barres - %s") % nom
        
        # Conversion de la taille px en mm
        largeur, hauteur = (109, 60)
        largeur, hauteur = int(largeur * 0.264583333), int(hauteur * 0.264583333)
        
        # Recherche le centre de l'objet
        tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - largeur/2), int(y - hauteur/2)
        
        objet = AjouterBarcode((x, y), largeur, hauteur, nom=nom, champ=champ, afficheNumero=False)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 
    
    def OnOutil_texteLigne(self, event):
        """ Insertion d'une ligne de texte """
        dlg = DLG_Saisie_texte_doc.Dialog(self, texte=u"", listeChamps=self.infosCategorie.champs)
        if dlg.ShowModal() == wx.ID_OK:
            texte = dlg.GetTexte()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        if texte == "" :
            return
        
        # Police
        tailleFont = 12
        font = wx.Font(tailleFont, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL, underline=False, face="Arial")
        
        # Recherche le centre de l'objet
        dc = wx.ClientDC(self.ctrl_canvas.canvas)
        tailleDC = dc.GetSize() 
        dc.SetFont(font)
        tailleTexte = dc.GetTextExtent(texte)
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = x - tailleTexte[0]/2, y - tailleTexte[1]/2
                    
        # Insertion
        objet = AjouterLigneTexte(texte, (x, y), taillePolicePDF=tailleFont, font=font)
        self.ctrl_canvas.AjouterObjet(objet)
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_texteBloc(self, event):
        """ Insertion d'un bloc de texte """
        dlg = DLG_Saisie_texte_doc.Dialog(self, texte=u"", listeChamps=self.infosCategorie.champs)
        if dlg.ShowModal() == wx.ID_OK:
            texte = dlg.GetTexte()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        if texte == "" :
            return
        
        # Police
        tailleFont = 12
        font = wx.Font(tailleFont, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL, underline=False, face="Arial")

        # Insertion
        objet = AjouterBlocTexte(texte, (0, 0), taillePolicePDF=tailleFont, font=font)
        self.ctrl_canvas.AjouterObjet(objet)
        
        # Centrer
        dc = wx.ClientDC(self.ctrl_canvas.canvas)
        dc.SetFont(font)
        tailleDC = dc.GetSize() 
        largeurTexte = objet.BoxWidth
        x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
        x, y = int(x - objet.BoxWidth/2), int(y - objet.BoxHeight/2)
        objet.SetXY(numpy.array([x, y]))
        
        # MAJ Affichage
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnOutil_special(self, event):
        self.OnDropDownSpecial(None)

    def OnDropDownSpecial(self, event):
        if 1 == 1 :#event.IsDropDownClicked():
            tb = event.GetEventObject()
            tb.SetToolSticky(event.GetId(), True)

            # create the popup menu
            menuPopup = wx.Menu()
            
            # Importation d'une image
            index = 0
            for dictSpecial in self.infosCategorie.speciaux :
                id = 20000 + index
                label = _(u"Ins�rer l'objet '%s'") % dictSpecial["nom"]
                item = wx.MenuItem(menuPopup, id, label, label, wx.ITEM_NORMAL)
                item.SetBitmap(wx.Bitmap("Images/32x32/Special.png", wx.BITMAP_TYPE_PNG))
                item.SetMarginWidth(32)
                menuPopup.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnOutil_inserer_special, id=id)
                index += 1
                
                # Disable si nbre max d'objets de ce type atteint
                if dictSpecial.has_key("nbreMax") :
                    if dictSpecial["nbreMax"] != None :
                        listeObjets = self.ctrl_canvas.canvas._ForeDrawList
                        nbre = 0
                        for objetTemp in listeObjets :
                            if hasattr(objetTemp, 'champ'):
                                if objetTemp.champ == dictSpecial["champ"] :
                                    nbre += 1
                        if nbre >= dictSpecial["nbreMax"] :
                            item.Enable(False)

            # line up our menu with the button
            rect = tb.GetToolRect(event.GetId())
            pt = tb.ClientToScreen(rect.GetBottomLeft())
            pt = self.ScreenToClient(pt)

            self.PopupMenu(menuPopup, pt)
            
            # Pour �viter que les menus suivants soient d�form�s 
            item.SetMarginWidth(16)
            
            # make sure the button is "un-stuck"
            tb.SetToolSticky(event.GetId(), False)

    def OnOutil_inserer_special(self, event):
        index = event.GetId() - 20000
        dictSpecial = self.infosCategorie.speciaux[index]
        self.AjouterSpecial(dictSpecial)

    def AjouterSpecial(self, dictSpecial={}):
        """ Ajouter un objet sp�cial """
        # Position et taille par d�faut
        x = dictSpecial["x"]
        y = dictSpecial["y"]
        largeur = dictSpecial["largeur"]
        hauteur = dictSpecial["hauteur"]
        
        # Place l'objet au centre si la position est None
        if largeur == None : largeur = dictSpecial["largeurMin"] + 100
        if hauteur == None : hauteur = dictSpecial["hauteurMin"] + 100
        if x == None or y == None :
            tailleDC = wx.ClientDC(self.ctrl_canvas.canvas).GetSize() 
            x, y = self.ctrl_canvas.canvas.PixelToWorld((tailleDC[0]/2, tailleDC[1]/2))
            x, y = int(x - largeur/2), int(y - hauteur/2)
        
        # Insertion
        objet = AjouterSpecial(numpy.array([x, y]), largeur, hauteur, dictSpecial["nom"], dictSpecial["champ"], couleurFond=(250, 250, 50))
        if dictSpecial.has_key("obligatoire") : objet.obligatoire = dictSpecial["obligatoire"]
        if dictSpecial.has_key("nbreMax") : objet.nbreMaxe = dictSpecial["nbreMax"]
        if dictSpecial.has_key("Xmodifiable") : objet.Xmodifiable = dictSpecial["Xmodifiable"]
        if dictSpecial.has_key("Ymodifiable") : objet.Ymodifiable = dictSpecial["Ymodifiable"]
        if dictSpecial.has_key("verrouillageX") : objet.verrouillageX = dictSpecial["verrouillageX"]
        if dictSpecial.has_key("verrouillageY") : objet.verrouillageY = dictSpecial["verrouillageY"]
        if dictSpecial.has_key("largeurModifiable") : objet.largeurModifiable = dictSpecial["largeurModifiable"]
        if dictSpecial.has_key("hauteurModifiable") : objet.hauteurModifiable = dictSpecial["hauteurModifiable"]
        if dictSpecial.has_key("largeurMin") : objet.largeurMin = dictSpecial["largeurMin"]
        if dictSpecial.has_key("largeurMax") : objet.largeurMax = dictSpecial["largeurMax"]
        if dictSpecial.has_key("hauteurMin") : objet.hauteurMin = dictSpecial["hauteurMin"]
        if dictSpecial.has_key("hauteurMax") : objet.hauteurMax = dictSpecial["hauteurMax"]
        if dictSpecial.has_key("verrouillageLargeur") : objet.verrouillageLargeur = dictSpecial["verrouillageLargeur"]
        if dictSpecial.has_key("verrouillageHauteur") : objet.verrouillageHauteur = dictSpecial["verrouillageHauteur"]
        if dictSpecial.has_key("verrouillageProportions") : objet.verrouillageProportions = dictSpecial["verrouillageProportions"]
        if dictSpecial.has_key("interditModifProportions") : objet.interditModifProportions = dictSpecial["interditModifProportions"]
        self.ctrl_canvas.AjouterObjet(objet)
        
        # MAJ Canvas
        self.ctrl_canvas.Selection(objet, forceDraw=True)
        self.ctrl_canvas.canvas.SetFocus() 

    def OnAffichage_grille(self, event):
        if self.ctrl_canvas.affichageGrille == False :
            self.ctrl_canvas.Affiche_grille() 
        else:
            self.ctrl_canvas.Cache_grille()

    def OnAffichage_apercu(self, event):
        self.ctrl_canvas.Imprimer() 

    def OnClose(self, event):
        self.Quitter()
    
    def Quitter(self, enregistrer=True):
##        # Ferme tous les fichiers ouverts
##        for index in range(0, self.nb.GetPageCount()) :
##            rtc = self.nb.GetPage(index)
##            if enregistrer == True :
##                self.CloseFile(rtc)
        # Quitter
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()
        
    def OnAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Lditeurdedocuments")
    
    def SetNomDoc(self, nom=u""):
        if nom == None or nom == u"" :
            nom = _(u"Sans nom")
        self.nom = nom
        titre = u"%s - %s" % (NOM_APPLICATION, nom)
        self.SetTitle(titre)
    
    def ChangeTaillePage(self, taille=(210, 297)):
        self.taille_page = taille
        self.ctrl_canvas.taille_page = taille
        self.ctrl_canvas.Reinit_canvas()
    
    def GetBufferPhotoPage(self):
        bmp = self.ctrl_canvas.GetPhotoPage()
        img = bmp.ConvertToImage()
        buffer = cStringIO.StringIO()
        img.SaveStream(buffer, wx.BITMAP_TYPE_PNG)
        buffer.seek(0)
        blob = buffer.read()
        return blob
        
    def GetIDmodele(self, IDmodele=None):
        return self.IDmodele
    
    def Importation(self, IDmodele=None, InForeground=True):
        """ Importation des objets d'un mod�le """
        listeObjets = ImportationObjets(IDmodele=IDmodele, InForeground=InForeground)
        for objet in listeObjets :
            self.ctrl_canvas.AjouterObjet(objet)
            if InForeground==True :
                self.listeInitialeObjets.append(objet.IDobjet)
        # Si c'est un fond
        if InForeground == False :
            return listeObjets
        
        self.ctrl_canvas.SetFocus() 
    
    def Sauvegarde(self):
        """ Sauvegarde des donn�es """
        # Sauvegarde des propri�t�s du document
        nom = self.ctrl_proprietes_doc.GetNom()
        observations = self.ctrl_proprietes_doc.GetObservations()
        taille = self.ctrl_proprietes_doc.GetTaille()
        IDfond = self.ctrl_proprietes_doc.GetFond()
        
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce mod�le !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_proprietes_doc.ctrl_nom.SetFocus()
            return False
                                            
        DB = GestionDB.DB()
        listeDonnees = [    
                ("nom", nom),
                ("categorie", self.categorie),
                ("supprimable", 1),
                ("largeur", taille[0]),
                ("hauteur", taille[1]),
                ("observations", observations),
                ("IDfond", IDfond),
                ]
                
        if self.IDmodele == None :
            # Recherche s'il faut mettre defaut
            req = """SELECT IDmodele, defaut
            FROM documents_modeles
            WHERE categorie='%s' AND defaut = 1
            ;""" % self.categorie
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if len(listeTemp) == 0 :
                listeDonnees.append(("defaut", 1))
            # Insert
            self.IDmodele = DB.ReqInsert("documents_modeles", listeDonnees)
        else:
            # MAJ
            DB.ReqMAJ("documents_modeles", listeDonnees, "IDmodele", self.IDmodele)
        
##        # Sauvegarde de la photo de la page
##        bmp = self.GetBufferPhotoPage()
##        DB.MAJimage(table="documents_modeles", key="IDmodele", IDkey=self.IDmodele, blobImage=bmp, nomChampBlob="image")
                
        # Sauvegarde des objets
        listeObjetsSauves = []
        listeObjets = self.ctrl_canvas.GetObjets()
        index = 0
        for objet in listeObjets :
            IDobjet = objet.IDobjet
            listeObjetsSauves.append(IDobjet) 
            
            listeDonnees = [    
                ("IDmodele", self.IDmodele),
                ("nom", objet.nom),
                ("categorie", objet.categorie),
                ("champ", objet.champ),
                ("ordre", index),
                ("obligatoire", objet.obligatoire),
                ("nbreMax", objet.nbreMax),
                ("texte", objet.GetTexte()),
                ("points", objet.GetPoints()),
                ("typeImage", objet.GetTypeImage()),
                ("x", float(objet.GetXY()[0])),
                ("y", float(objet.GetXY()[1])),
                ("verrouillageX", int(objet.verrouillageX)),
                ("verrouillageY", int(objet.verrouillageY)),
                ("Xmodifiable", int(objet.Xmodifiable)),
                ("Ymodifiable", int(objet.Ymodifiable)),
                ("largeur", objet.GetTaille2()[0]),
                ("hauteur", objet.GetTaille2()[1]),
                ("largeurModifiable", int(objet.largeurModifiable)),
                ("hauteurModifiable", int(objet.hauteurModifiable)),
                ("largeurMin", objet.largeurMin),
                ("largeurMax", objet.largeurMax),
                ("hauteurMin", objet.hauteurMin),
                ("hauteurMax", objet.hauteurMax),
                ("verrouillageLargeur", int(objet.verrouillageLargeur)),
                ("verrouillageHauteur", int(objet.verrouillageHauteur)),
                ("verrouillageProportions", int(objet.verrouillageProportions)),
                ("interditModifProportions", int(objet.interditModifProportions)),
                ("couleurTrait", objet.GetCouleurTrait()),
                ("styleTrait", objet.GetStyleTrait()),
                ("epaissTrait", objet.GetEpaissTrait()),
                ("coulRemplis", objet.GetCoulRemplis()),
                ("styleRemplis", objet.GetStyleRemplis()),
                ("couleurTexte", objet.GetCouleurTexte()),
                ("couleurFond", objet.GetCouleurFond()),
                ("padding", objet.GetPadding()),
                ("interligne", objet.GetInterligne()),
                ("taillePolice", objet.GetTaillePolice()),
                ("nomPolice", objet.GetNomPolice()),
                ("familyPolice", objet.GetFamilyPolice()),
                ("stylePolice", objet.GetStylePolice()),
                ("weightPolice", objet.GetWeightPolice()),
                ("soulignePolice", objet.GetSoulignePolice()),
                ("alignement", objet.GetAlignement()),
                ("largeurTexte", objet.GetLargeurTexte()),
                ("norme", objet.GetNorme()),
                ("afficheNumero", objet.GetAfficheNumero()),
                ]
            
            # Sauvegarde de l'objet
            if IDobjet == None :
                nouvelObjet = True
                IDobjet = DB.ReqInsert("documents_objets", listeDonnees)
            else:
                nouvelObjet = False
                DB.ReqMAJ("documents_objets", listeDonnees, "IDobjet", IDobjet)

            # Sauvegarde de l'image
            bmp = objet.GetImageBuffer() 
            if bmp != None :
                DB.MAJimage(table="documents_objets", key="IDobjet", IDkey=IDobjet, blobImage=bmp, nomChampBlob="image")
            
            index += 1
        
        # Effacement des objets supprim�s
        for IDobjet in self.listeInitialeObjets :
            if IDobjet not in listeObjetsSauves :
                DB.ReqDEL("documents_objets", "IDobjet", IDobjet)
        
        DB.Close()

def GetLogo_organisateur():
    # Charge le logo
    DB = GestionDB.DB()
    req = """SELECT logo FROM organisateur WHERE IDorganisateur=1;"""
    DB.ExecuterReq(req)
    buffer = DB.ResultatReq()[0][0]
    DB.Close()
    if buffer == None : 
        # Si aucun logo, renvoie une image vide
        return wx.Image("Images/Special/Logo_nb.png", wx.BITMAP_TYPE_ANY), False
    io = cStringIO.StringIO(buffer)
    img = wx.ImageFromStream(io, wx.BITMAP_TYPE_PNG)
    return img, True


def ImportationInfosModele(IDmodele=None):
    """ Importation des infos d'un mod�le """
    # Importation des donn�es
    DB = GestionDB.DB()
    req = "SELECT nom, categorie, largeur, hauteur, IDfond FROM documents_modeles WHERE IDmodele=%d;" % IDmodele 
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return {}
    nom, categorie, largeur, hauteur, IDfond = listeDonnees[0]
    dictInfos = { "nom": nom, "categorie":categorie, "largeur":largeur, "hauteur":hauteur, "IDfond":IDfond}
    return dictInfos

def ImportationObjets(IDmodele=None, InForeground=True):
    """ Importation des objets d'un mod�le """
    # Recherche des noms de champs
    from DATA_Tables import DB_DATA as dictChamps
    listeChamps = []
    for nom, type, info in dictChamps["documents_objets"] :
        listeChamps.append(nom)
        
    # Importation des donn�es
    DB = GestionDB.DB()
    req = "SELECT * FROM documents_objets WHERE IDmodele=%d ORDER BY ordre;" % IDmodele 
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return []
    listeObjets = []
    for objet in listeDonnees :
        dictTemp = {}
        for index in range(0, len(listeChamps)):
            dictTemp[listeChamps[index]] = objet[index]
        listeObjets.append(dictTemp)
    
    def ConvertCouleur(couleur=None):
        if couleur == None or len(couleur) == 0 : return None
        couleur = couleur[1:-1].split(",")
        couleur = (int(couleur[0]), int(couleur[1]), int(couleur[2]) )
        return couleur

    def ConvertPoints(pointsStr=[]):
        listePoints = []
        listeTemp = pointsStr.split(";")
        for point in listeTemp :
            if len(point) > 0 :
                x, y = point.split(",")
                listePoints.append(numpy.array([int(x), int(y)]))
        return listePoints
    
    listeObjetsCanvas = []
            
    # Cr�ation des objets
    for objet in listeObjets :
        
        # Rectangle
        if objet["categorie"] == "rectangle" :
            objetCanvas = AjouterRectangle(
                    numpy.array([objet["x"], objet["y"]]), 
                    taille = numpy.array([objet["largeur"], objet["hauteur"]]), 
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurTrait=ConvertCouleur(objet["couleurTrait"]),
                    styleTrait=objet["styleTrait"], 
                    epaissTrait=objet["epaissTrait"], 
                    coulRemplis=ConvertCouleur(objet["coulRemplis"]),
                    styleRemplis=objet["styleRemplis"], 
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )

        # Ligne
        if objet["categorie"] == "ligne" :
            objetCanvas = AjouterLigne(
                    points=ConvertPoints(objet["points"]), 
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurTrait=ConvertCouleur(objet["couleurTrait"]),
                    styleTrait=objet["styleTrait"], 
                    epaissTrait=objet["epaissTrait"], 
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )

        # Ligne
        if objet["categorie"] == "ellipse" :
            objetCanvas = AjouterEllipse(
                    numpy.array([objet["x"], objet["y"]]),
                    numpy.array([objet["largeur"], objet["hauteur"]]), 
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurTrait=ConvertCouleur(objet["couleurTrait"]),
                    styleTrait=objet["styleTrait"], 
                    epaissTrait=objet["epaissTrait"], 
                    coulRemplis=ConvertCouleur(objet["coulRemplis"]),
                    styleRemplis=objet["styleRemplis"], 
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )

        # Polygone
        if objet["categorie"] == "polygone" :
            objetCanvas = AjouterPolygone(
                    points=ConvertPoints(objet["points"]), 
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurTrait=ConvertCouleur(objet["couleurTrait"]),
                    styleTrait=objet["styleTrait"], 
                    epaissTrait=objet["epaissTrait"], 
                    coulRemplis=ConvertCouleur(objet["coulRemplis"]),
                    styleRemplis=objet["styleRemplis"], 
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )

        # Image
        if objet["categorie"] == "image" :
            bmp = None
            
            # Logo
            if objet["typeImage"] == "logo" :
                img, exists = GetLogo_organisateur() 
                bmp = wx.BitmapFromImage(img)
            # Fichier
            if objet["typeImage"].startswith("fichier") :
                if objet["image"] != None :
                    io = cStringIO.StringIO(objet["image"])
                    bmp = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
            # Photo
            if objet["typeImage"] == "photo" :
                bmp = wx.Bitmap("Images/128x128/Femme.png", wx.BITMAP_TYPE_ANY)
            
            if bmp != None :
                objetCanvas = AjouterImage(
                        bmp, 
                        numpy.array([objet["x"], objet["y"]]),
                        objet["hauteur"],
                        nom=objet["nom"], 
                        champ=objet["champ"],
                        typeImage=objet["typeImage"], 
                        IDobjet=objet["IDobjet"],
                        InForeground=InForeground,
                        )
                
                if objet["typeImage"] == "logo" :
                    objetCanvas.exists = exists
                
        # Code-barres
        if objet["categorie"] == "barcode" :
            objetCanvas = AjouterBarcode(
                    numpy.array([objet["x"], objet["y"]]),
                    largeur=objet["largeur"],
                    hauteur=objet["hauteur"],
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    norme=objet["norme"],
                    afficheNumero=objet["afficheNumero"],
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )

        # Sp�cial
        if objet["categorie"] == "special" :
            objetCanvas = AjouterSpecial(
                    numpy.array([objet["x"], objet["y"]]),
                    largeur=objet["largeur"],
                    hauteur=objet["hauteur"],
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurFond=ConvertCouleur(objet["coulRemplis"]),
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )
        
        # Ligne de texte
        if objet["categorie"] == "ligne_texte" :
            objetCanvas = AjouterLigneTexte(
                    objet["texte"], 
                    numpy.array([objet["x"], objet["y"]]),
                    taillePolicePDF=objet["taillePolice"],
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurTexte=ConvertCouleur(objet["couleurTexte"]),
                    couleurFond=ConvertCouleur(objet["couleurFond"]),
                    family = objet["familyPolice"],
                    style=objet["stylePolice"],
                    weight=objet["weightPolice"],
                    underlined=objet["soulignePolice"],
                    font=None,
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )
        
        # Ligne de texte
        if objet["categorie"] == "bloc_texte" :
            objetCanvas = AjouterBlocTexte(
                    objet["texte"], 
                    numpy.array([objet["x"], objet["y"]]),
                    taillePolicePDF=objet["taillePolice"],
                    nom=objet["nom"], 
                    champ=objet["champ"],
                    couleurTexte=ConvertCouleur(objet["couleurTexte"]),
                    couleurFond=ConvertCouleur(objet["couleurFond"]),
                    couleurTrait=ConvertCouleur(objet["couleurTrait"]),
                    styleTrait=objet["styleTrait"], 
                    epaissTrait=objet["epaissTrait"], 
                    largeur=objet["largeurTexte"], 
                    padding=objet["padding"], 
                    family = objet["familyPolice"],
                    style=objet["stylePolice"],
                    weight=objet["weightPolice"],
                    souligne=objet["soulignePolice"],
                    alignement=objet["alignement"],
                    font=None, 
                    interligne = objet["interligne"],
                    IDobjet=objet["IDobjet"],
                    InForeground=InForeground,
                    )
        
        listeObjetsCanvas.append(objetCanvas) 
    
    return listeObjetsCanvas


# ------------------------------------------------------------------------------------------------------------------------------

class ModeleDoc():
    """ Importation d'un mod�le pour un PDF """
    def __init__(self, IDmodele=None):
        self.IDmodele = IDmodele
        
        # Importation infos sur organisateur pour le fond
        self.dictOrganisateur = self.ImportationOrganisateur() 
        
        # Importation des infos sur ce mod�le
        self.dictInfosModele = ImportationInfosModele(IDmodele=IDmodele)
        
        # Importation des objets
        self.listeObjets = ImportationObjets(IDmodele=IDmodele)
    
    def ImportationOrganisateur(self):
        """ R�cup�ration des infos sur l'organisme """
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


    def FindObjet(self, champ=""):
        for objet in self.listeObjets :
            if objet.champ == champ :
                return objet
        return None
    
    def GetCoordsObjet(self, objet=None):
        xy = objet.GetXY()
        x, y = xy[0]*mmPDF, xy[1]*mmPDF
        taille = objet.GetTaille()
        largeur, hauteur = taille[0]*mmPDF, taille[1]*mmPDF
        return x, y, largeur, hauteur
        
    def DessineFond(self, canvas, dictChamps={}):
        """ Dessine les objets du fond """
        if len(dictChamps) == 0 :
            dictChamps = self.dictOrganisateur
        IDfond = self.dictInfosModele["IDfond"]
        if IDfond != None :
            listeObjetsFond = ImportationObjets(IDmodele=IDfond)
            for objet in listeObjetsFond :
                valeur = self.GetValeur(objet, dictChamps)
                if valeur != False :
                    DessineObjetPDF(objet, canvas, valeur=valeur)

    def DessineTousObjets(self, canvas, dictChamps={}):
        """ Dessine tous les objets """
        for objet in self.listeObjets :
            valeur = self.GetValeur(objet, dictChamps)
            if valeur != False :
                etat = DessineObjetPDF(objet, canvas, valeur=valeur)
                if etat == False :
                    return False

    def GetValeur(self, objet=None, dictChamps={}):
        valeur = None
        # -------- CODE-BARRES -------
        if objet.categorie == "barcode" :
            if dictChamps.has_key(objet.champ) :
                valeur = dictChamps[objet.champ]
                if len(valeur) == 0 :
                    valeur = None
                    
        # -------- TEXTE ----------
        if "texte" in objet.categorie :
            texte = objet.GetTexte() 
            for nomChamp, valeur in dictChamps.iteritems() :
                # Traitement d'une formule
                texte = DLG_Saisie_formule.ResolveurTexte(texte=texte, listeChamps=dictChamps.keys(), dictValeurs=dictChamps)
                # Remplacement des mos-cl�s par les valeurs
                if type(nomChamp) in (str, unicode) and nomChamp.startswith("{") :
                    if valeur == None : valeur = ""
                    if type(valeur) == int : valeur = str(valeur)
                    if type(valeur) == float : valeur = u"%.02f %s" % (valeur, SYMBOLE)
                    if type(valeur) == datetime.date : valeur = UTILS_Dates.DateDDEnFr(valeur)
                    if nomChamp in texte :
                        texte = texte.replace(nomChamp, valeur)
            # Remplace �galement les mots-cl�s non utilis�s par des cha�nes vides
            texte = re.sub(r"\{[A-Za-z0-9_-]*?\}", "", texte)
            
            valeur=texte
                        
        # -------- IMAGE -------
        if objet.categorie == "image" :
            if objet.typeImage == "logo" :
                # Type Logo
                if objet.exists == False :
                    valeur = False
            elif objet.typeImage == "photo" :
                # Type Photo
                if dictChamps.has_key("{IDINDIVIDU}") :
                    IDindividu = dictChamps["{IDINDIVIDU}"]
                    DB = GestionDB.DB(suffixe="PHOTOS")
                    req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%s;" % IDindividu 
                    DB.ExecuterReq(req)
                    listeDonnees = DB.ResultatReq()
                    DB.Close()
                    if len(listeDonnees) > 0 :
                        IDphoto, bufferPhoto = listeDonnees[0]
                        io = cStringIO.StringIO(bufferPhoto)
                        img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
                        valeur=img
                    else:
                        # Image par d�faut
                        if dictChamps.has_key("nomImage") :
                            nomImage = dictChamps["nomImage"]
                            bmp = wx.Bitmap("Images/128x128/%s" % nomImage, wx.BITMAP_TYPE_ANY)
                            img = bmp.ConvertToImage()
                            valeur=img
            else:
                valeur=None
        return valeur

    def DessineFormes(self, canvas):
        """ Dessine les formes """
        for objet in self.listeObjets :
            if objet.categorie in ("rectangle", "ligne", "ellipse", "polygone") :
                DessineObjetPDF(objet, canvas)

    def DessineCodesBarres(self, canvas, dictChamps={}):
        """ Dessine les codes-barres """
        for objet in self.listeObjets :
            if objet.categorie == "barcode" :
                valeur = self.GetValeur(objet, dictChamps)
                if valeur != None :
                    DessineObjetPDF(objet, canvas, valeur=valeur)

    def DessineTextes(self, canvas, dictChamps={}):
        """ Dessine les textes """
        for objet in self.listeObjets :
            if "texte" in objet.categorie :
                valeur = self.GetValeur(objet, dictChamps)
                DessineObjetPDF(objet, canvas, valeur=valeur)

    def DessineImages(self, canvas, dictChamps={}):
        """ Dessine les images """
        for objet in self.listeObjets :
            if objet.categorie == "image" :
                valeur = self.GetValeur(objet, dictChamps)
                if valeur != False :
                    DessineObjetPDF(objet, canvas, valeur=valeur)



# ------------------------------------------------------------------------------------------------------------------------------
        
def DessineObjetPDF(objet, canvas, valeur=None):
    """ objet = objetNoedoc | canvas = canvas Reportlab """
    
    def ConvertCouleurPourPDF(couleur=(0, 0, 0)):
        r, g, b = couleur[0]/255.0, couleur[1]/255.0, couleur[2]/255.0
        return r, g, b
    
    def GetXY(objet):
        xy = objet.GetXY()
        return xy[0]*mmPDF, xy[1]*mmPDF
    
    def GetTaille(objet):
        taille = objet.GetTaille()
        return taille[0]*mmPDF, taille[1]*mmPDF
    
    def GetTrait(objet):
        if objet.LineColor == None :
            return 0
        else:
            r, g, b = ConvertCouleurPourPDF(objet.LineColor)
            canvas.setStrokeColorRGB(r, g, b)
            canvas.setLineWidth(objet.LineWidth)
            if objet.LineStyle == "Dot" : canvas.setDash(1, 2)
            if objet.LineStyle == "LongDash" : canvas.setDash(6, 3)
            if objet.LineStyle == "ShortDash" : canvas.setDash(6, 3)
            if objet.LineStyle == "DotDash" : canvas.setDash([6, 2, 3])
            return 1
    
    def GetRemplissage(objet):
        if objet.FillColor == None :
            return 0
        else:
            r, g, b = ConvertCouleurPourPDF(objet.FillColor)
            canvas.setFillColorRGB(r, g, b)
            return 1
    
    def GetCouleurPolice(objet):
        r, g, b = ConvertCouleurPourPDF(objet.Color)
        canvas.setFillColorRGB(r, g, b)
    
    def GetPolice(objet):
        police = "Arial"
        if objet.Weight == wx.BOLD : police = "Arial-Bold"
        if objet.Style == wx.ITALIC : police = "Arial-Oblique"
        if objet.Style == wx.ITALIC and objet.Weight == wx.BOLD : police = "Arial-BoldOblique"
##        police = "Helvetica"
##        if objet.Weight == wx.BOLD : police = "Helvetica-Bold"
##        if objet.Style == wx.ITALIC : police = "Helvetica-Oblique"
##        if objet.Style == wx.ITALIC and objet.Weight == wx.BOLD : police = "Helvetica-BoldOblique"
        return police

    canvas.saveState() 
    
    # ------- RECTANGLE ------
    if objet.categorie == "rectangle" :
        x, y = GetXY(objet)
        largeur, hauteur = GetTaille(objet)
        trait = GetTrait(objet)
        remplissage = GetRemplissage(objet)
        canvas.rect(x, y, largeur, hauteur, trait, remplissage)

    # ------- ELLIPSE ------
    if objet.categorie == "ellipse" :
        x, y = GetXY(objet)
        largeur, hauteur = GetTaille(objet)
        trait = GetTrait(objet)
        remplissage = GetRemplissage(objet)
        canvas.ellipse(x, y, x+largeur, y+hauteur, trait, remplissage)

    # ------- LIGNE ------
    if objet.categorie == "ligne" :
        x1, y1 = objet.Points[0]
        x2, y2 = objet.Points[1]
        trait = GetTrait(objet)
        canvas.line(x1*mmPDF, y1*mmPDF, x2*mmPDF, y2*mmPDF)

    # ------- POLYGONE ------
    if objet.categorie == "polygone" :
        listePoints = objet.Points
        trait = GetTrait(objet)
        remplissage = GetRemplissage(objet)
        p = canvas.beginPath()
        p.moveTo(listePoints[0][0]*mmPDF, listePoints[0][1]*mmPDF)
        for x, y in listePoints[1:] :
            p.lineTo(x*mmPDF, y*mmPDF)
        p.lineTo(listePoints[0][0]*mmPDF, listePoints[0][1]*mmPDF)
        canvas.drawPath(p, trait, remplissage)

    # ------- LIGNE DE TEXTE ------
    if objet.categorie == "ligne_texte" :
        x, y = GetXY(objet)
        GetCouleurPolice(objet)
        if valeur == None :
            valeur = objet.String
        famillePolice = objet.Family
        stylePolice = objet.Style
        soulignPolice = objet.Underlined
        epaisseurPolice = objet.Weight
        taillePolice = objet.taillePolicePDF
        canvas.setFont(GetPolice(objet), taillePolice)
        GetCouleurPolice(objet)
        canvas.drawString(x, y + taillePolice * 0.2, valeur)

    # ------- BLOC DE TEXTE ------
    if objet.categorie == "bloc_texte" :
        x, y = GetXY(objet)
        if valeur == None :
            valeur = objet.String
        taillePolice = objet.taillePolicePDF
        textObject = canvas.beginText()
        textObject.setFont(GetPolice(objet), taillePolice)
        textObject.setTextOrigin(x, y - taillePolice + (taillePolice*0.1) )#textObject._leading * 0.5)
        GetCouleurPolice(objet)
        textObject.textLines(valeur)
        canvas.drawText(textObject)
        
    # ------- IMAGE ------
    if objet.categorie == "image" :
        x, y = GetXY(objet)
        largeur, hauteur = GetTaille(objet)
        imgwx = objet.Image
        if valeur != None :
            imgwx = valeur
        file = StringIO.StringIO()
        imgwx.SaveStream(file, wx.BITMAP_TYPE_PNG)
        gif = file.getvalue()
        file.close()                 
        buf = StringIO.StringIO(gif)
        canvas.drawImage(ImageReader(buf), x, y, largeur, hauteur, mask="auto", preserveAspectRatio=objet.verrouillageProportions)
        
    # ------- BARCODE ------
    if objet.categorie == "barcode" :
        x, y = GetXY(objet)
        largeur, hauteur = GetTaille(objet)
        if valeur != None :   
            # V�rifie que uniquement des chiffres dans certains codes-barres
            if objet.norme in ("EAN8", "EAN13") :
                for caract in valeur :
                    if caract not in "0123456789" :
                        dlg = wx.MessageDialog(None, _(u"G�n�ration du PDF impossible.\n\nErreur : Un code-barres %s doit comporter uniquement des chiffres. Cette erreur appara�t donc si une lettre se trouve dans la valeur du code-barres (Ce qui est le cas pour certains codes-barres standards de Noethys). Vous pouvez contourner le probl�me en cr�ant des Codes-barres manuels avec les QUESTIONNAIRES de Noethys.") % objet.norme, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False
            
            if objet.norme == None : objet.norme = "Extended39"
            if objet.norme == "Codabar" : barcode = Codabar(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "Code11" : barcode = Code11(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "I2of5" : barcode = I2of5(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "MSI" : barcode = MSI(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "Code128" : barcode = Code128(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "EAN13" : barcode = createBarcodeDrawing("EAN13", value="{:0>12}".format(valeur), barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "EAN8" : barcode = createBarcodeDrawing("EAN8", value="{:0>7}".format(valeur), barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "Extended39" : barcode = Extended39(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "Standard39" : barcode = Standard39(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "Extended93" : barcode = Extended93(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "Standard93" : barcode = Standard93(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            if objet.norme == "POSTNET" : barcode = POSTNET(valeur, barHeight=hauteur, humanReadable=objet.afficheNumero)
            
            barcode.drawOn(canvas, x-18, y)

    # ------- SPECIAL ------
    if objet.categorie == "special" :
        x, y = GetXY(objet)
        largeur, hauteur = GetTaille(objet)
        canvas.setStrokeColorRGB(0, 0, 0)
        r, g, b = ConvertCouleurPourPDF(objet.ObjectList[0].FillColor)
        canvas.setFillColorRGB(r, g, b)
        canvas.rect(x, y, largeur, hauteur, 1, 1)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(x+4, y+4, objet.nom)
            
    canvas.restoreState()

        
        
class Impression():
    def __init__(self, taille_page=None, listeObjets=[], listeObjetsFond=[]):
        self.taille_page = taille_page
        self.listeObjets = listeObjets
        self.listeObjetsFond = listeObjetsFond
                    
        # -------- Initialisation du document ----------
        nomDoc = "Temp/DocumentPDF_%s.pdf" % FonctionsPerso.GenerationIDdoc()
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        canvas = CanvasPDF(nomDoc, pagesize=(self.taille_page[0]*mmPDF, self.taille_page[1]*mmPDF) )
        
        # Cr�ation des objets du fond
        for objet in self.listeObjetsFond :
            DessineObjetPDF(objet, canvas)
            
        # Cr�ation des objets du premier plan
        for objet in listeObjets :
            DessineObjetPDF(objet, canvas)
        
        # Affichage du PDF
        canvas.showPage() 
        canvas.save()
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=1,
            nom="test", observations=u"", 
            IDfond=None, categorie="fond", taille_page=(210, 297))
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
