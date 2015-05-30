#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.html
import wx.lib.filebrowsebutton as filebrowse

if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC
    
import wx.lib.agw.hyperlink as Hyperlink

import xlrd
from Outils import unicodecsv as csv
import os
import datetime
import GestionDB
import CTRL_Bandeau

import CTRL_Saisie_adresse
import DLG_Famille
import UTILS_Parametres

from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils

TYPES_IMPORTATION = [
    {"code":"familles", "label":_(u"Familles"), "infos":_(u"Sélectionnez ce type d'importation si votre fichier de données comporte une famille par ligne.\nNoethys créera alors une fiche famille pour chaque ligne ainsi que les fiches individuelles correspondantes.")},
    {"code":"individus", "label":_(u"Individus"), "infos":_(u"Sélectionnez ce type d'importation si votre fichier de données comporte un individu par ligne.\nNoethys créera alors pour chaque individu une fiche individuelle non rattachée.")},
    ]


DICT_COLONNES = {

    "familles" : [

                        {"code":"famille_rue_resid", "label":_(u"Rue de résidence de la famille"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : 10 rue des oiseaux.")},
                        {"code":"famille_cp_resid", "label":_(u"CP ville de résidence de la famille"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"famille_ville_resid", "label":_(u"Ville de résidence de la famille"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"famille_secteur", "label":_(u"Secteur de résidence de la famille"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Brest Nord...")},
                        {"code":"famille_tel_domicile", "label":_(u"Numéro de tél. du domicile famille"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"famille_caisse", "label":_(u"Nom de caisse de la famille"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : CAF, MSA (Doit être présent dans base).")},
                        {"code":"famille_num_allocataire", "label":_(u"Numéro d'allocataire de la famille"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : 7798769X.")},
                        {"code":"famille_allocataire", "label":_(u"Allocataire titulaire de la famille"), "format":"texte", "obligatoire":False, "infos":_(u"Valeurs possibles = Père, P, Mère, M.")},
                        {"code":"famille_memo", "label":_(u"Mémo de la famille"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},

                        {"code":"pere_nom", "label":_(u"Nom de famille du père"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"pere_prenom", "label":_(u"Prénom du père"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Gérard, Xavier...")},
                        {"code":"pere_date_naiss", "label":_(u"Date de naissance du père"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 01/02/2003)")},
                        {"code":"pere_cp_naiss", "label":_(u"CP de la ville de naissance du père"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"pere_ville_naiss", "label":_(u"Ville de naissance du père"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"pere_tel_mobile", "label":_(u"Numéro de mobile du père"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"pere_email", "label":_(u"Email du père"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"pere_categorie", "label":_(u"Catégorie socio-pro. du père"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : Employé (Doit être présent dans base)")},
                        {"code":"pere_profession", "label":_(u"Profession du père"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Charpentier, Secrétaire...")},
                        {"code":"pere_employeur", "label":_(u"Employeur du père"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : SNCF, France Télécom...")},
                        {"code":"pere_tel_travail", "label":_(u"Numéro de travail du père"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"pere_memo", "label":_(u"Mémo du père"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},

                        {"code":"mere_nom", "label":_(u"Nom de famille de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"mere_nom_jfille", "label":_(u"Nom de jeune fille de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"mere_prenom", "label":_(u"Prénom de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Marie, Sophie...")},
                        {"code":"mere_date_naiss", "label":_(u"Date de naissance de la mère"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 01/02/2003)")},
                        {"code":"mere_cp_naiss", "label":_(u"CP de la ville de naissance de la mère"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"mere_ville_naiss", "label":_(u"Ville de naissance de la mère"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"mere_tel_mobile", "label":_(u"Numéro de mobile de la mère"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"mere_email", "label":_(u"Email de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"mere_categorie", "label":_(u"Catégorie socio-pro. de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : Employé (Doit être présent dans base)")},
                        {"code":"mere_profession", "label":_(u"Profession de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Charpentier, Secrétaire...")},
                        {"code":"mere_employeur", "label":_(u"Employeur de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : SNCF, France Télécom...")},
                        {"code":"mere_tel_travail", "label":_(u"Numéro de travail de la mère"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"mere_memo", "label":_(u"Mémo de la mère"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},
                        
                        {"code":"enfant1_civilite", "label":_(u"Civilité de l'enfant 1"), "format":"texte", "obligatoire":False, "infos":_(u"Garçon = M, m, Mr, M., Masculin, H, h, Homme, G, g, Garçon.<BR>Fille = F, f, Féminin, Femme, Fille.")},
                        {"code":"enfant1_nom", "label":_(u"Nom de famille de l'enfant 1"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"enfant1_prenom", "label":_(u"Prénom de l'enfant 1"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Kévin, Sophie...")},
                        {"code":"enfant1_date_naiss", "label":_(u"Date de naissance de l'enfant 1"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 01/02/2003)")},
                        {"code":"enfant1_cp_naiss", "label":_(u"CP de la ville de naiss. de l'enfant 1"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"enfant1_ville_naiss", "label":_(u"Ville de naissance de l'enfant 1"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"enfant1_tel_mobile", "label":_(u"Numéro de mobile de l'enfant 1"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"enfant1_email", "label":_(u"Email de l'enfant 1"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"enfant1_memo", "label":_(u"Mémo de l'enfant 1"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},

                        {"code":"enfant2_civilite", "label":_(u"Civilité de l'enfant 2"), "format":"texte", "obligatoire":False, "infos":_(u"Garçon = M, m, Mr, M., Masculin, H, h, Homme, G, g, Garçon.<BR>Fille = F, f, Féminin, Femme, Fille.")},
                        {"code":"enfant2_nom", "label":_(u"Nom de famille de l'enfant 2"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"enfant2_prenom", "label":_(u"Prénom de l'enfant 2"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Kévin, Sophie...")},
                        {"code":"enfant2_date_naiss", "label":_(u"Date de naissance de l'enfant 2"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 02/02/2003)")},
                        {"code":"enfant2_cp_naiss", "label":_(u"CP de la ville de naiss. de l'enfant 2"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"enfant2_ville_naiss", "label":_(u"Ville de naissance de l'enfant 2"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"enfant2_tel_mobile", "label":_(u"Numéro de mobile de l'enfant 2"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 02.02.03.04.05.)")},
                        {"code":"enfant2_email", "label":_(u"Email de l'enfant 2"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"enfant2_memo", "label":_(u"Mémo de l'enfant 2"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},

                        {"code":"enfant3_civilite", "label":_(u"Civilité de l'enfant 3"), "format":"texte", "obligatoire":False, "infos":_(u"Garçon = M, m, Mr, M., Masculin, H, h, Homme, G, g, Garçon.<BR>Fille = F, f, Féminin, Femme, Fille.")},
                        {"code":"enfant3_nom", "label":_(u"Nom de famille de l'enfant 3"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"enfant3_prenom", "label":_(u"Prénom de l'enfant 3"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Kévin, Sophie...")},
                        {"code":"enfant3_date_naiss", "label":_(u"Date de naissance de l'enfant 3"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 03/02/2003)")},
                        {"code":"enfant3_cp_naiss", "label":_(u"CP de la ville de naiss. de l'enfant 3"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"enfant3_ville_naiss", "label":_(u"Ville de naissance de l'enfant 3"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"enfant3_tel_mobile", "label":_(u"Numéro de mobile de l'enfant 3"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 03.02.03.04.05.)")},
                        {"code":"enfant3_email", "label":_(u"Email de l'enfant 3"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"enfant3_memo", "label":_(u"Mémo de l'enfant 3"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},

                        {"code":"enfant4_civilite", "label":_(u"Civilité de l'enfant 4"), "format":"texte", "obligatoire":False, "infos":_(u"Garçon = M, m, Mr, M., Masculin, H, h, Homme, G, g, Garçon.<BR>Fille = F, f, Féminin, Femme, Fille.")},
                        {"code":"enfant4_nom", "label":_(u"Nom de famille de l'enfant 4"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"enfant4_prenom", "label":_(u"Prénom de l'enfant 4"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Kévin, Sophie...")},
                        {"code":"enfant4_date_naiss", "label":_(u"Date de naissance de l'enfant 4"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 04/02/2003)")},
                        {"code":"enfant4_cp_naiss", "label":_(u"CP de la ville de naiss. de l'enfant 4"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"enfant4_ville_naiss", "label":_(u"Ville de naissance de l'enfant 4"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"enfant4_tel_mobile", "label":_(u"Numéro de mobile de l'enfant 4"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 04.02.03.04.05.)")},
                        {"code":"enfant4_email", "label":_(u"Email de l'enfant 4"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"enfant4_memo", "label":_(u"Mémo de l'enfant 4"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},

                        ],

    "individus" : [
                        {"code":"individu_civilite", "label":_(u"Civilité"), "format":"texte", "obligatoire":True, "infos":_(u"Monsieur = M, m, Mr, M., Monsieur, H, h, homme.<BR>Melle = Melle, Mademoiselle.<BR>Mme = Mme, Madame, Femme.<BR>Garçon = G, g, Garçon.<BR>Fille = F, f, Fille.<BR>Autres = Collectivité, Association, Organisme, Entreprise.")},
                        {"code":"individu_nom", "label":_(u"Nom de famille"), "format":"texte", "obligatoire":True, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"individu_nom_jfille", "label":_(u"Nom de jeune fille"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : DUPOND, DURAND...")},
                        {"code":"individu_prenom", "label":_(u"Prénom"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Kévin, Sophie...")},
                        {"code":"individu_date_naiss", "label":_(u"Date de naissance"), "format":"date", "obligatoire":False, "infos":_(u"Format : jj/mm/aaa (Exemple : 01/02/2003)")},
                        {"code":"individu_cp_naiss", "label":_(u"Code postal de la ville de naissance"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"individu_ville_naiss", "label":_(u"Ville de naissance"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"individu_rue_resid", "label":_(u"Rue de résidence"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : 10 rue des oiseaux.")},
                        {"code":"individu_cp_resid", "label":_(u"Code postal de la ville de résidence"), "format":"codepostal", "obligatoire":False, "infos":_(u"Format : xxxxx (Exemple : 29870)")},
                        {"code":"individu_ville_resid", "label":_(u"Ville de résidence"), "format":"ville", "obligatoire":False, "infos":_(u"Exemples : LANNILIS, BREST...")},
                        {"code":"individu_secteur", "label":_(u"Secteur de résidence"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Brest Nord...")},
                        {"code":"individu_tel_domicile", "label":_(u"Numéro de domicile"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"individu_tel_mobile", "label":_(u"Numéro de mobile"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"individu_email", "label":_(u"Email"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : monadressemail@test.com.")},
                        {"code":"individu_categorie", "label":_(u"Catégorie socio-professionnelle"), "format":"texte", "obligatoire":False, "infos":_(u"Exemple : Employé (Doit être présent dans base)")},
                        {"code":"individu_profession", "label":_(u"Profession"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : Charpentier, Secrétaire...")},
                        {"code":"individu_employeur", "label":_(u"Employeur"), "format":"texte", "obligatoire":False, "infos":_(u"Exemples : SNCF, France Télécom...")},
                        {"code":"individu_tel_travail", "label":_(u"Numéro de travail"), "format":"telephone", "obligatoire":False, "infos":_(u"Format xx.xx.xx.xx.xx. (Exemple : 01.02.03.04.05.)")},
                        {"code":"individu_memo", "label":_(u"Mémo"), "format":"texte", "obligatoire":False, "infos":_(u"Texte libre.")},
                        ],

    }



def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text



class Importation_Excel() :
    def __init__(self, nomFichier=""):
        self.fichierValide = True
        try :
            self.classeur = xlrd.open_workbook(nomFichier)
        except :
            self.fichierValide = False
        self.feuille = self.SelectionFeuille() 
    
    def SelectionFeuille(self):
        """ Sélection de la feuille qui comporte les données """
        feuille = None
        feuilles = self.classeur.sheet_names()
        if len(feuilles) == 1 :
            feuille = self.classeur.sheet_by_index(0)
        else :
            # Demande la feuille à ouvrir
            dlg = wx.SingleChoiceDialog(None, _(u"Veuillez sélectionner la feuille du classeur qui comporte les données à importer :"), _(u"Sélection d'une feuille"), feuilles, wx.CHOICEDLG_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                feuille = self.classeur.sheet_by_index(dlg.GetSelection())
            dlg.Destroy()
        return feuille
    
    def GetDonnees(self, colonnes=[]):
        """ Récupération des données de la feuille """
        listeDonnees = []
        if self.feuille == None : return listeDonnees
        try :
            for num_ligne in range(self.feuille.nrows):
                ligne = []
                for num_colonne in range(self.feuille.ncols):
                    # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                    case = self.feuille.cell(rowx=num_ligne, colx=num_colonne)
                    valeur = case.value
                    # Date
                    if case.ctype == 3 :
                        dateTuple = xlrd.xldate_as_tuple(case.value, self.classeur.datemode)
                        valeur = datetime.date(*dateTuple[:3])
                    # Nombre
                    if case.ctype == 2 :
                        valeur = unicode(valeur)[:-2]
                    ligne.append(valeur)
                listeDonnees.append(ligne)
        except :
            listeDonnees = None
        return listeDonnees



class Importation_CSV() :
    def __init__(self, nomFichier=""):
        self.fichierValide = True
        
        # Demande le caractère de séparation
        listeLabels = [_(u"Virgule (,)"), _(u"Point-virgule (;)"), _(u"Tabulation")]
        listeSeparations = [",", ";", "\t"]
        dlg = wx.SingleChoiceDialog(None, _(u"Veuillez sélectionner le caractère de séparation utilisé dans ce fichier :"), _(u"Sélection du caractère de séparation"), listeLabels, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            separation = listeSeparations[dlg.GetSelection()]
        else :
            self.fichierValide = False
        dlg.Destroy()
        
        # Ouverture du fichier
        if self.fichierValide == True :
            try :
                self.fichier = csv.reader(open(nomFichier,"rb"), encoding="iso-8859-15", delimiter=separation)
            except :
                self.fichierValide = False
                
    def GetDonnees(self, colonnes=[]):
        """ Récupération des données de la feuille """
        listeDonnees = []
        try :
            for donnees_ligne in self.fichier :
                ligne = []
                for valeur in donnees_ligne :
                    # Date
                    if len(valeur) == 10 :
                        if valeur[2] == "/" and valeur[5] == "/" :
                            try :
                                valeur = datetime.date(int(valeur[6:10]), int(valeur[3:5]), int(valeur[:2]))
                            except :
                                pass
                    
                    ligne.append(valeur)
                listeDonnees.append(ligne)
        except :
            listeDonnees = None
        return listeDonnees

# -------------------------------------------------------------------------------------------------------------------------------- 

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        self.URL = URL
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
        if self.URL == "tout" : self.parent.CocherTout()
        if self.URL == "rien" : self.parent.CocherRien()
        self.UpdateLink()
        
# -------------------------------------------------------------------------------------------------------------------------------- 

class CTRL_Type_donnee(wx.Choice):
    def __init__(self, parent, largeur=-1):
        wx.Choice.__init__(self, parent, id=-1, size=(largeur, -1)) 
        self.parent = parent

        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.MAJ()
        self.SetToolTipString(_(u"Sélectionnez le type de donnée qui se trouve dans cette colonne"))
        
    def MAJ(self):
        index = 0
        typeImportation = self.parent.parent.parent.dictDonnees["typeImportation"]
        for dictColonne in DICT_COLONNES[typeImportation] :
            self.Append(dictColonne["label"], dictColonne["code"])
            index += 1
                                
    def GetCode(self):
        if self.GetSelection() == -1 :
            return None
        else:
            typeImportation = self.parent.parent.parent.dictDonnees["typeImportation"]
            return DICT_COLONNES[typeImportation][self.GetSelection()]["code"]
    

class CTRL_Colonnes(ULC.UltimateListCtrl):
    def __init__(self, parent, listeDonnees=[], supprimerEntetes=False):
        ULC.UltimateListCtrl.__init__(self, parent, -1, agwStyle=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES| ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.parent = parent
        self.SetDonnees(listeDonnees, supprimerEntetes)

        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Binds
        self.Bind(ULC.EVT_LIST_ITEM_CHECKED, self.OnCheck)

        self.MAJ()
    
    def SetDonnees(self, listeDonnees=[], supprimerEntetes=False):
        self.listeDonnees = listeDonnees
        self.supprimerEntetes = supprimerEntetes
        # Supprimer première ligne du fichier
        if self.supprimerEntetes == True :
            self.listeDonnees = self.listeDonnees[1:]
        # Transformation du listeDonnees en colonnes
        if len(self.listeDonnees) > 0 :
            self.listeColonnes = [[row[i] for row in self.listeDonnees] for i in range(len(self.listeDonnees[0]))]
        else :
            self.listeColonnes = []

    def MAJ(self):
        self.ClearAll()
        self.Remplissage()
        self.MAJaffichage() 
        self.CocherTout()
    
    def Remplissage(self):
        """ Remplissage """
        self.dictControles = {}
        if len(self.listeDonnees) == 0 :
            return
        
        # Création des colonnes
        largeurColonneDonnee = 300
        self.InsertColumn(0, _(u"Colonne"), width=100)
        self.InsertColumn(1, _(u"Aperçu des données"), width=250)
        self.InsertColumn(2, _(u"Type de donnée"), width=largeurColonneDonnee)

        # Création des lignes
        index = 0
        for colonne in self.listeColonnes :
            
            # Colonne Nom de colonne
            label = _(u" Colonne %d") % (index+1)
            self.InsertStringItem(index, label, it_kind=1)
            self.SetItemPyData(index, index)
            
            # Aperçu des données
            listeTemp = []
            for valeur in colonne[:20] :
                if type(valeur) == datetime.date :
                    valeur = DateEngFr(str(valeur))
                listeTemp.append(valeur)
            apercu = ", ".join(listeTemp)
            self.SetStringItem(index, 1, label=u"%s..." % apercu[:100])

            # Type de donnée
            item = self.GetItem(index, 2)
            ctrl = CTRL_Type_donnee(self, largeur=largeurColonneDonnee-4)
            item.SetWindow(ctrl)
            self.SetItem(item)
            self.dictControles[index] = {"ctrl":ctrl, "item":item}

            index += 1
        
    
    def MAJaffichage(self):
        # Correction du bug d'affichage du ultimatelistctrl
        self._mainWin.RecalculatePositions()
        self.Layout() 

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        index = event.m_itemIndex
        self.SetEtatCtrl(index)
        
    def SetEtatCtrl(self, index=None):
        item = self.GetItem(index, 0)
        if item.IsChecked() :
            self.dictControles[index]["ctrl"].Enable(True)
        else :
            self.dictControles[index]["ctrl"].Enable(False)
        # Déselectionne l'item après la coche
        self.Select(index, False)

    def CocherTout(self):
        self.Cocher(etat=True)
        
    def CocherRien(self):
        self.Cocher(etat=False)
    
    def Cocher(self, etat):
        for index in range(0, len(self.listeColonnes)):
            item = self.GetItem(index, 0)
            item.Check(etat)
            self.SetItem(item)
            self.SetEtatCtrl(index)
        
    def GetCoches(self):
        listeResultats = []
        for index in range(0, len(self.listeColonnes)):
            item = self.GetItem(index, 0)
            if item.IsChecked() :
                ctrl = self.dictControles[index]["ctrl"]
                listeResultats.append({"colonne":index, "donnee":ctrl.GetCode()})
        return listeResultats

# -----------------------------------------------------------------------------------------------------------------------------------

class Track(object):
    def __init__(self, dictLigne={}, ligneValide=True):
        self.dictLigne = dictLigne
        self.ligneValide = ligneValide
        for code, dictValeurs in dictLigne.iteritems() :
            valeur = dictValeurs["valeur"]
            anomalie = dictValeurs["anomalie"]
            label = dictValeurs["label"]    
            exec("self.%s = label" % code)

class CTRL_Donnees(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """        
        # Récupération des paramètres
        dictDonnees = self.GetGrandParent().dictDonnees
        self.typeImportation = dictDonnees["typeImportation"]
        supprimerEntetes = dictDonnees["supprimerEntetes"]
        colonnes = dictDonnees["colonnes"]
        donnees = dictDonnees["donnees"]

        self.validation = ValidationDonnees(self.typeImportation) 

        # Récupération des colonnes
        self.listeColonnesImportation = []
        self.listeColonnesDonnees = []
        dictColonnes = {}
        for colonne in colonnes :
            self.listeColonnesImportation.append(colonne["colonne"])
            self.listeColonnesDonnees.append(colonne["donnee"])
            dictColonnes[colonne["colonne"]] = colonne["donnee"]
        
        # Récupération des données
        if supprimerEntetes == True :
            donnees = donnees[1:]
        
        listeListeView = []
        for ligne in donnees :
            index = 0
            dictTemp = {}
            valide = True
            for valeur in ligne :
                if index in self.listeColonnesImportation :
                    code = dictColonnes[index]
                    
                    # Validation et formatage des données
                    ligneValide, code, valeur, anomalie, label = self.validation.Validation(code, valeur)
                    dictTemp[code] = {"valeur":valeur, "anomalie":anomalie, "label":label}
                    if ligneValide == False :
                        valide = False
                
                if self.typeImportation == "familles" :
                    valide = True

                    if dictTemp.has_key("pere_nom") == False and dictTemp.has_key("mere_nom") == False :
                        valide = False

                    if dictTemp.has_key("pere_nom") == True and dictTemp.has_key("mere_nom") == False :
                        if dictTemp["pere_nom"]["anomalie"] != None :
                            valide = False
                        
                    if dictTemp.has_key("mere_nom") == True and dictTemp.has_key("pere_nom") == False :
                        if dictTemp["mere_nom"]["anomalie"] != None :
                            valide = False

                    if dictTemp.has_key("mere_nom") == True and dictTemp.has_key("pere_nom") == True :
                        if dictTemp["mere_nom"]["anomalie"] != None and dictTemp["pere_nom"]["anomalie"] != None :
                            valide = False
                    
                index += 1
            listeListeView.append(Track(dictTemp, valide))
        return listeListeView

    def InitObjectListView(self):
        self.imgOk = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imgNon = self.AddNamedImages("erreur", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.imgAttention = self.AddNamedImages("attention", wx.Bitmap("Images/16x16/Attention.png", wx.BITMAP_TYPE_PNG))

        def GetImage(track):
            if track.ligneValide == False :
                return self.imgNon
            # Vérifie s'il ya une anomalie dans le track
            for code, dictValeurs in track.dictLigne.iteritems() :
                if dictValeurs["anomalie"] != None :
                    return self.imgAttention
            return self.imgOk

        def Formate_texte(valeur):
            return valeur
        
        def Formate_date(valeur):
            return valeur

        def Formate_telephone(valeur):
            return valeur
        
        def Formate_cp(valeur):
            return valeur
        
        def Formate_ville(valeur):
            return valeur

        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Création des colonnes
        dictColonnesTemp = {}
        for dictColonne in DICT_COLONNES[self.typeImportation] :
            dictColonnesTemp[dictColonne["code"]] = dictColonne
        
        listeColonnes = []
        listeColonnes.append(ColumnDefn("", 'left', 20, None, imageGetter=GetImage))
        for code in self.listeColonnesDonnees :
            label = dictColonnesTemp[code]["label"]
            format = dictColonnesTemp[code]["format"]
            if format == "texte" : converter = Formate_texte
            if format == "date" : converter = Formate_date
            if format == "telephone" : converter = Formate_telephone
            if format == "cp" : converter = Formate_cp
            if format == "ville" : converter = Formate_ville
            listeColonnes.append(ColumnDefn(label, 'left', 150, code, stringConverter=converter))
        
        self.SetColumns(listeColonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune donnée"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[0])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        # MAJ
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
        self.CocherTout()

    def Selection(self):
        return self.GetSelectedObjects()
    
    def CocherTout(self, event=None):
        for track in self.donnees :
            if track.ligneValide == True :
                self.Check(track)
            else :
                self.Uncheck(track)
            self.RefreshObject(track)
        
    def CocherRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)
    
    def GetTracksCoches(self):
        listeCoches = []
        index = 0
        for track in self.donnees :
            if self.GetCheckState(track) == True :
                listeCoches.append(track)
            index += 1
        return listeCoches
        
# -------------------------------------------------------------------------------------------------------------------------------------

class Page_intro(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="page_intro", style=wx.TAB_TRAVERSAL)
        self.parent = parent
                
        # Création du texte d'intro HTML
        TEXTE_INTRO = u"""
            Cette fonctionnalité vous permet d'importer des individus ou des familles dans votre fichier de données Noethys depuis un fichier EXCEL ou CSV.
            Vous devrez sélectionner l'un des types d'importation proposés ci-dessous puis formater les données de votre fichier en fonction des formats exigés.
            <BR><BR>
            Utilisez le mode "Familles" pour créer une ou plusieurs fiches individuelles et les rattacher automatiquement à une fiche famille (Une ligne par famille, qui doit comporter au moins un adulte : le père ou la mère).      
            Ou utilisez le mode "Individus" pour créer uniquement des fiches individuelles non rattachées (Une ligne par individu, qui doit comporter au moins la civilité et le nom de famille).      
            <BR><BR>
            """
        
        index = 0
        for dictType in TYPES_IMPORTATION :
            typeImportation = dictType["code"]
            label = dictType["label"]
            infos = dictType["infos"]
            
            TEXTE_INTRO += u"""
                <FONT SIZE=+1><B><U>%d. %s</U></B></FONT>
                <BR>
                <I>%s</I>
                <BR><BR>
                <TABLE CELLSPACING=2 BORDER=0 COLS=2 WIDTH="100%%">
                """ % (index+1, label, infos)
            
            for dictColonne in DICT_COLONNES[typeImportation] :
                
                TEXTE_INTRO += u"""
                    <TR>
                    <TD ALIGN='right' VALIGN='top' WIDTH="40%%"><B>%s</B></TD>
                    <TD ALIGN='left' WIDTH="30%%">%s</TD>
                    </TR>
                    """ % (dictColonne["label"], dictColonne["infos"])
                    # BGCOLOR="#ffffff" 
                    
            TEXTE_INTRO += u"""</TABLE><BR><BR>"""
            index += 1
                
        # Contrôles
        self.ctrl_intro = wx.html.HtmlWindow(self, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.SUNKEN_BORDER)
        self.ctrl_intro.SetPage(u"<FONT SIZE=-1>%s</FONT>" % TEXTE_INTRO)
        self.ctrl_intro.SetBackgroundColour(wx.Colour(240, 251, 237))
        
        # Layout
        box = wx.BoxSizer()
        box.Add(self.ctrl_intro, 1, wx.EXPAND, 0)
        self.SetSizer(box)
    
    def MAJ(self):
        pass
        
    def Validation(self):
        return True

# ----------------------------------------------------------------------------------------------------------------------------------------------

class Page_fichier(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="page_fichier", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.box_type_staticbox = wx.StaticBox(self, -1, _(u"1. Type d'importation"))
        
        index = 0
        for dictType in TYPES_IMPORTATION :
            code = dictType["code"]
            label = dictType["label"]
            infos = dictType["infos"]
            if index == 0 :
                style = ", style=wx.RB_GROUP"
            else :
                style = ""
            exec(u"""self.radio_type_%d = wx.RadioButton(self, %d, label %s)""" % (index, 10000 + index, style))
            exec(u"""self.label_type_%d = wx.StaticText(self, -1, infos)""" % index)
            exec(u"""self.label_type_%d.SetForegroundColour(wx.Colour(128, 128, 128))""" % index)
            index += 1
        
        self.box_fichier_staticbox = wx.StaticBox(self, -1, _(u"2. Sélection du fichier"))
        self.label_fichier = wx.StaticText(self, -1, _(u"Cliquez sur le bouton 'Sélectionner' pour sélectionner le fichier de données :"))
        wildcard = _(u"Fichiers Excel ou csv|*.xls;*.csv|Fichiers Excel (*.xls)|*.xls|Fichiers csv (*.csv)|*.csv|All files (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        self.ctrl_fichier = filebrowse.FileBrowseButton(self, -1, labelText=_(u"Fichier à importer :"), buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier de données"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard, startDirectory=cheminDefaut)
        self.label_fichier2 = wx.StaticText(self, -1, _(u"Formats acceptés :\n   - Fichiers Excel (.xls - versions 2003, 2002, XP, 2000, 97, 95, 5.0, 4.0, 3.0) \n   - Fichiers CSV (.csv)"))
        self.label_fichier2.SetForegroundColour(wx.Colour(128, 128, 128))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=10, cols=1, vgap=10, hgap=10)
        box_fichier = wx.StaticBoxSizer(self.box_fichier_staticbox, wx.VERTICAL)
        sizer_fichier = wx.BoxSizer(wx.VERTICAL)
        box_type = wx.StaticBoxSizer(self.box_type_staticbox, wx.VERTICAL)
        sizer_type = wx.BoxSizer(wx.VERTICAL)

        index = 0
        for dictType in TYPES_IMPORTATION :
            exec("""sizer_type.Add(self.radio_type_%d, 0, wx.TOP, 10)""" % index)
            exec("""sizer_type.Add(self.label_type_%d, 0, wx.LEFT, 22)""" % index)
            index += 1
            
        box_type.Add(sizer_type, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_type, 1, wx.EXPAND, 0)
        sizer_fichier.Add(self.label_fichier, 0, wx.EXPAND, 0)
        sizer_fichier.Add(self.ctrl_fichier, 0, wx.TOP|wx.EXPAND, 10)
        sizer_fichier.Add(self.label_fichier2, 0, wx.TOP|wx.EXPAND, 10)
        box_fichier.Add(sizer_fichier, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_fichier, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
    
    def GetTypeImportation(self):
        index = 0
        reponse = None
        for dictType in TYPES_IMPORTATION :
            code = dictType["code"]
            exec("""if self.radio_type_%d.GetValue() == True : reponse = code """ % index)
            index += 1
        return reponse
        
    def MAJ(self):
        pass

    def Validation(self):
        nomFichier = self.ctrl_fichier.GetValue()
        if len(nomFichier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un fichier de données à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if os.path.isfile(nomFichier) == False :
            dlg = wx.MessageDialog(self, _(u"L'emplacement fichier que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Lecture du fichier :
        if nomFichier.endswith("xls") : 
            importation = Importation_Excel(nomFichier)
        elif nomFichier.endswith("csv") : 
            importation = Importation_CSV(nomFichier)
        else :
            importation = None
        
        if importation == None or importation.fichierValide == False :
            dlg = wx.MessageDialog(self, _(u"Le fichier ne semble pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Récupération des données
        donnees = importation.GetDonnees()
        if donnees == None :
            dlg = wx.MessageDialog(self, _(u"Noethys n'a pas réussi à lire les données !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        self.parent.dictDonnees["typeImportation"] = self.GetTypeImportation() 
        self.parent.dictDonnees["nomFichier"] = nomFichier
        self.parent.dictDonnees["donnees"] = donnees
        return True


# ----------------------------------------------------------------------------------------------------------------------------------------------

class Page_colonnes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="page_colonnes", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.label_colonnes = wx.StaticText(self, -1, _(u"Sélectionnez les colonnes à importer et indiquez pour chacune d'entre elles le type de donnée qu'elle contient :"))
        self.ctrl_colonnes = CTRL_Colonnes(self)
        self.check_supprimerEntetes = wx.CheckBox(self, -1, _(u"Enlever la première ligne du fichier (Titres de colonnes)"))
        self.check_supprimerEntetes.SetToolTipString(_(u"Cochez cette case si le fichier de données contient une première ligne d'entêtes de colonnes"))
        self.hyper_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")
        
        # Layout
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.label_colonnes, 0, 0, 0)
        box.Add(self.ctrl_colonnes, 1, wx.EXPAND|wx.TOP, 10)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=5)
        grid_sizer_options.Add(self.check_supprimerEntetes, 0, wx.EXPAND, 0)
        grid_sizer_options.Add( (2, 2), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_options.Add(self.label_separation, 0, 0, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(0)
        box.Add(grid_sizer_options, 0, wx.EXPAND|wx.TOP, 10)
        self.SetSizer(box)
        
        # Events
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEntetes, self.check_supprimerEntetes)
    
    def OnCheckEntetes(self, event):
        self.MAJ() 
    
    def CocherTout(self):
        self.ctrl_colonnes.CocherTout() 

    def CocherRien(self):
        self.ctrl_colonnes.CocherRien() 

    def MAJ(self):
        self.ctrl_colonnes.SetDonnees(self.parent.dictDonnees["donnees"], supprimerEntetes=self.check_supprimerEntetes.GetValue())
        self.ctrl_colonnes.MAJ() 

    def Validation(self):
        listeColonnes = self.ctrl_colonnes.GetCoches() 
        
        # Vérifie que le type de donnée à été renseigné pour chaque colonne cochée
        listeTemp = []
        dictTemp = {}
        for colonne in listeColonnes :
            if dictTemp.has_key(colonne["donnee"]) == False :
                dictTemp[colonne["donnee"]] = 1
            else :
                dictTemp[colonne["donnee"]] += 1
            if colonne["donnee"] == None :
                listeTemp.append(colonne["colonne"])
        if len(listeTemp) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné le type de donnée pour %d colonnes cochées !") % len(listeTemp), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Vérifie si pas de doublons dans les types de données
        for code, nbre in dictTemp.iteritems() :
            if nbre > 1 :
                dlg = wx.MessageDialog(self, _(u"Un type de donnée ne peut pas être sélectionné plus d'une fois !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Vérifie si les colonnes obligatoires sont présentes :
        listeOublis = []
        typeImportation = self.parent.dictDonnees["typeImportation"]
        for dictColonne in DICT_COLONNES[typeImportation] :
            code = dictColonne["code"]
            if dictColonne["obligatoire"] == True :
                if dictTemp.has_key(code) == False :
                    listeOublis.append(u"   - %s\n" % dictColonne["label"])
        if len(listeOublis) > 0 :
            texte = "".join(listeOublis)
            dlg = wx.MessageDialog(self, _(u"Votre fichier n'est pas valide car il manque les colonnes obligatoires suivantes : \n\n%s") % texte, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Mémorisation des données
        self.parent.dictDonnees["supprimerEntetes"] = self.check_supprimerEntetes.GetValue()
        self.parent.dictDonnees["colonnes"] = listeColonnes
        return True


# ----------------------------------------------------------------------------------------------------------------------------------------------


class Page_analyse(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="page_analyse", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.label_donnees = wx.StaticText(self, -1, _(u"Cochez les données à importer et cliquez sur le bouton VALIDER pour lancer l'importation."))
        self.ctrl_donnees = CTRL_Donnees(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.image_ok = wx.StaticBitmap(self, -1, wx.Bitmap(u"Images/16x16/Ok.png", wx.BITMAP_TYPE_ANY))
        self.label_ok = wx.StaticText(self, -1, _(u"Ligne valide"))
        self.image_attention = wx.StaticBitmap(self, -1, wx.Bitmap(u"Images/16x16/Attention.png", wx.BITMAP_TYPE_ANY))
        self.label_attention = wx.StaticText(self, -1, _(u"Ligne valide mais des données non valides"))
        self.image_non = wx.StaticBitmap(self, -1, wx.Bitmap(u"Images/16x16/Interdit.png", wx.BITMAP_TYPE_ANY))
        self.label_non = wx.StaticText(self, -1, _(u"Ligne non valide"))
        
        self.hyper_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        # Layout
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.label_donnees, 0, 0, 0)
        box.Add(self.ctrl_donnees, 1, wx.EXPAND|wx.TOP, 10)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=11, vgap=0, hgap=5)
        grid_sizer_options.Add(self.image_ok, 0, 0, 0)
        grid_sizer_options.Add(self.label_ok, 0, 0, 0)
        grid_sizer_options.Add(self.image_non, 0, 0, 0)
        grid_sizer_options.Add(self.label_non, 0, 0, 0)
        grid_sizer_options.Add(self.image_attention, 0, 0, 0)
        grid_sizer_options.Add(self.label_attention, 0, 0, 0)
        grid_sizer_options.Add( (2, 2), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_options.Add(self.label_separation, 0, 0, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(6)
        box.Add(grid_sizer_options, 0, wx.EXPAND|wx.TOP, 10)

        self.SetSizer(box)

    def CocherTout(self):
        self.ctrl_donnees.CocherTout() 

    def CocherRien(self):
        self.ctrl_donnees.CocherRien() 

    def MAJ(self):
        self.ctrl_donnees.MAJ() 

    def Validation(self):
        tracks = self.ctrl_donnees.GetTracksCoches()
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        nbreInvalides = 0
        for track in tracks :
            if track.ligneValide == False :
                nbreInvalides += 1
        if nbreInvalides > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas sélectionner des lignes non valides !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
            
        self.parent.dictDonnees["tracks"] = tracks
        return True


# ----------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.dictDonnees = {}
        
        intro = _(u"Cet assistant permet d'importer facilement depuis un fichier Excel ou CSV des individus ou des familles dans votre fichier de données Noethys.")
        titre = _(u"Assistant d'importation d'individus")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document_import.png")
        
        self.listePages = (
            "Page_intro", 
            "Page_fichier",
            "Page_colonnes",
            "Page_analyse",
            )
        
        self.static_line = wx.StaticLine(self, -1)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_retour = CTRL_Bouton_image.CTRL(self, texte=_(u"Retour"), cheminImage="Images/32x32/Fleche_gauche.png")
        self.bouton_suite = CTRL_Bouton_image.CTRL(self, texte=_(u"Suite"), cheminImage="Images/32x32/Fleche_droite.png", margesImage=(0, 0, 4, 0), positionImage=wx.RIGHT)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 1
                        
        # Création des pages
        self.Creation_Pages()
        
        wx.CallAfter(self.AfficheAvertissement)
            
    def Creation_Pages(self):
        """ Creation des pages """
        for numPage in range(1, self.nbrePages+1) :
            exec( "self.page" + str(numPage) + " = " + self.listePages[numPage-1] + "(self)" )
            exec( "self.sizer_pages.Add(self.page" + str(numPage) + ", 1, wx.EXPAND, 0)" )
            self.sizer_pages.Layout()
            exec( "self.page" + str(numPage) + ".Show(False)" )
        self.page1.Show(True)
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_retour.SetToolTipString(_(u"Cliquez ici pour revenir à la page précédente"))
        self.bouton_suite.SetToolTipString(_(u"Cliquez ici pour passer à l'étape suivante"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler"))
        self.SetMinSize((730, 620))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        
        self.sizer_pages = sizer_pages
    
    def Onbouton_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Importerdesindividus")

    def Onbouton_retour(self, event):
        # rend invisible la page affichée
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible -= 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on quitte l'avant-dernière page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage("Images/32x32/Valider.png")
            self.bouton_suite.SetTexte(_(u"Valider"))
        else:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage("Images/32x32/Fleche_droite.png")
            self.bouton_suite.SetTexte(_(u"Suite"))
        # Si on revient à la première page, on désactive le bouton Retour
        if self.pageVisible == 1 :
            self.bouton_retour.Enable(False)
        # On active le bouton annuler
        self.bouton_annuler.Enable(True)

    def Onbouton_suite(self, event):
        # Vérifie que les données de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est déjà sur la dernière page : on termine
        if self.pageVisible == self.nbrePages :
            self.Terminer()
            return
        # Rend invisible la page affichée
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible += 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(True)
        pageCible.MAJ()
        self.sizer_pages.Layout()
        # Si on arrive à la dernière page, on désactive le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.SetImage("Images/32x32/Valider.png")
            self.bouton_suite.SetTexte(_(u"Valider"))
            self.bouton_annuler.Enable(False)
        # Si on quitte la première page, on active le bouton Retour
        if self.pageVisible > 1 :
            self.bouton_retour.Enable(True)

    def OnClose(self, event):
        self.Annuler()

    def OnBoutonAnnuler(self, event):
        self.Annuler()

    def Annuler(self):
        self.EndModal(wx.ID_CANCEL)

    def ValidationPages(self) :
        """ Validation des données avant changement de pages """
        exec( "validation = self.page" + str(self.pageVisible) + ".Validation()" )
        return validation
    
    def Terminer(self):
        # Lancement de l'importation
        etat = self.Importation()
        # Fermeture
        if etat == True :
            self.EndModal(wx.ID_OK)
    
    def Importation(self):
        """ Importation des données """
        # Récupération des paramètres
        typeImportation = self.dictDonnees["typeImportation"]
        validation = ValidationDonnees(typeImportation) 
        
        # Récupération des codes des colonnes
        listeCodesColonnes = []
        for dictColonne in self.dictDonnees["colonnes"] :
            listeCodesColonnes.append(dictColonne["donnee"])
                
        # Lecture des données
        listeAnomalies = []
        listeValeurs = []
        index = 0
        for track in self.dictDonnees["tracks"] :
            dictValeurs = {}
            ligneValide = True
            
            for dictColonne in DICT_COLONNES[typeImportation] :
                code = dictColonne["code"]
                
                # Récupération de la valeur
                if track.dictLigne.has_key(code) :
                    valeur = track.dictLigne[code]["valeur"]
                else :
                    ligneValideTmp, code, valeur, anomalie, label = validation.Validation(code, None)
                
                # Mémorisation de la valeur
                dictValeurs[code] = valeur
                
            # Mémorise la ligne si elle est valide
            if ligneValide == True :
                listeValeurs.append(dictValeurs)
            index += 1
        
        # Enregistrement des données
        DB = GestionDB.DB()

        def CreationIndividu(dictValeurs):
            # Vérification des données
            valide = True
            if dictValeurs.has_key("individu_nom") == True :
                if dictValeurs["individu_nom"] in ("", None) :
                    valide = False
            else :
                valide = False
            if dictValeurs.has_key("individu_civilite") == True :
                if dictValeurs["individu_civilite"] not in (1, 2, 3, 4, 5, 6, 7, 8, 9) :
                    valide = False
            else :
                valide = False
                
            if valide == False :
                return None
            
            # Sauvegarde
            listeDonnees = [
                ("IDcivilite", dictValeurs["individu_civilite"]), 
                ("nom", dictValeurs["individu_nom"]), 
                ("IDnationalite", 73), 
                ("IDpays_naiss", 73), 
                ("deces", 0), 
                ("date_creation", str(datetime.date.today())), 
                ]
            
            def AjouteChamp(key, champ, defaut):
                if dictValeurs.has_key(key) :
                    valeur = dictValeurs[key]
                else :
                    valeur = defaut
                listeDonnees.append((champ, valeur))
            
            AjouteChamp("individu_nom_jfille", "nom_jfille", "")
            AjouteChamp("individu_prenom", "prenom", "")
            AjouteChamp("individu_date_naiss", "date_naiss", None)
            AjouteChamp("individu_cp_naiss", "cp_naiss", None)
            AjouteChamp("individu_ville_naiss", "ville_naiss", None)
            AjouteChamp("individu_adresse_auto", "adresse_auto", None)
            AjouteChamp("individu_rue_resid", "rue_resid", "")
            AjouteChamp("individu_cp_resid", "cp_resid", None)
            AjouteChamp("individu_ville_resid", "ville_resid", None)
            AjouteChamp("individu_secteur", "IDsecteur", None)
            AjouteChamp("individu_tel_domicile", "tel_domicile", None)
            AjouteChamp("individu_tel_mobile", "tel_mobile", None)
            AjouteChamp("individu_email", "mail", None)
            AjouteChamp("individu_categorie", "IDcategorie_travail", None)
            AjouteChamp("individu_profession", "profession", "")
            AjouteChamp("individu_employeur", "employeur", "")
            AjouteChamp("individu_tel_travail", "travail_tel", None)
            AjouteChamp("individu_memo", "memo", "")

            IDindividu = DB.ReqInsert("individus", listeDonnees)
            return IDindividu

        index = 0
        for dictValeurs in listeValeurs :

            # Type d'importation : individus
            if typeImportation == "individus" :
                
                IDindividu = CreationIndividu(dictValeurs)
                
            # Type d'importation : individus
            if typeImportation == "familles" :

                dictIDindividus = {}

                # Famille
                IDfamille = DLG_Famille.CreateIDfamille(DB)
    
                def EnregistreRattachement(IDindividu=None, IDcategorie=1, titulaire=0) :
                    listeDonnees = [
                        ("IDindividu", IDindividu), 
                        ("IDfamille", IDfamille), 
                        ("IDcategorie", IDcategorie), 
                        ("titulaire", titulaire), 
                        ]
                    IDrattachement = DB.ReqInsert("rattachements", listeDonnees)
            

                # Père
                dictTemp = {}
                dictTemp["individu_civilite"] = 1
                dictTemp["individu_nom"] = dictValeurs["pere_nom"]
                dictTemp["individu_prenom"] = dictValeurs["pere_prenom"]
                dictTemp["individu_date_naiss"] = dictValeurs["pere_date_naiss"]
                dictTemp["individu_cp_naiss"] = dictValeurs["pere_cp_naiss"]
                dictTemp["individu_ville_naiss"] = dictValeurs["pere_ville_naiss"]
                dictTemp["individu_tel_mobile"] = dictValeurs["pere_tel_mobile"]
                dictTemp["individu_email"] = dictValeurs["pere_email"]
                dictTemp["individu_categorie"] = dictValeurs["pere_categorie"]
                dictTemp["individu_profession"] = dictValeurs["pere_profession"]
                dictTemp["individu_employeur"] = dictValeurs["pere_employeur"]
                dictTemp["individu_tel_travail"] = dictValeurs["pere_tel_travail"]
                dictTemp["individu_memo"] = dictValeurs["pere_memo"]
                
                dictTemp["individu_tel_domicile"] = dictValeurs["famille_tel_domicile"]
                dictTemp["individu_rue_resid"] = dictValeurs["famille_rue_resid"]
                dictTemp["individu_cp_resid"] = dictValeurs["famille_cp_resid"]
                dictTemp["individu_ville_resid"] = dictValeurs["famille_ville_resid"]
                dictTemp["individu_secteur"] = dictValeurs["famille_secteur"]

                dictIDindividus["pere"] = CreationIndividu(dictTemp)
                if dictIDindividus["pere"] != None :
                    EnregistreRattachement(IDindividu=dictIDindividus["pere"], IDcategorie=1, titulaire=1)
                                
                # Mère
                dictTemp = {}
                dictTemp["individu_civilite"] = 3
                dictTemp["individu_nom"] = dictValeurs["mere_nom"]
                dictTemp["individu_nom_jfille"] = dictValeurs["mere_nom_jfille"]
                dictTemp["individu_prenom"] = dictValeurs["mere_prenom"]
                dictTemp["individu_date_naiss"] = dictValeurs["mere_date_naiss"]
                dictTemp["individu_cp_naiss"] = dictValeurs["mere_cp_naiss"]
                dictTemp["individu_ville_naiss"] = dictValeurs["mere_ville_naiss"]
                dictTemp["individu_tel_mobile"] = dictValeurs["mere_tel_mobile"]
                dictTemp["individu_email"] = dictValeurs["mere_email"]
                dictTemp["individu_categorie"] = dictValeurs["mere_categorie"]
                dictTemp["individu_profession"] = dictValeurs["mere_profession"]
                dictTemp["individu_employeur"] = dictValeurs["mere_employeur"]
                dictTemp["individu_tel_travail"] = dictValeurs["mere_tel_travail"]
                dictTemp["individu_memo"] = dictValeurs["mere_memo"]
                
                dictTemp["individu_tel_domicile"] = dictValeurs["famille_tel_domicile"]
                if dictIDindividus["pere"] != None :
                    dictTemp["individu_adresse_auto"] = dictIDindividus["pere"]
                    dictTemp["individu_secteur"] = dictValeurs["famille_secteur"]
                else :
                    dictTemp["individu_rue_resid"] = dictValeurs["famille_rue_resid"]
                    dictTemp["individu_cp_resid"] = dictValeurs["famille_cp_resid"]
                    dictTemp["individu_ville_resid"] = dictValeurs["famille_ville_resid"]
                    dictTemp["individu_secteur"] = dictValeurs["famille_secteur"]

                dictIDindividus["mere"] = CreationIndividu(dictTemp)
                if dictIDindividus["mere"] != None :
                    EnregistreRattachement(IDindividu=dictIDindividus["mere"], IDcategorie=1, titulaire=1)
                    
                # Récupération de l'adresse auto
                if dictIDindividus["pere"] != None :
                    adresse_auto = dictIDindividus["pere"]
                else :
                    adresse_auto = dictIDindividus["mere"]
                
                # Enfants
                dictTemp = {}
                
                for numEnfant in (1, 2, 3, 4) :

                    dictTemp["individu_civilite"] = dictValeurs["enfant%d_civilite" % numEnfant]
                    dictTemp["individu_nom"] = dictValeurs["enfant%d_nom" % numEnfant]
                    dictTemp["individu_prenom"] = dictValeurs["enfant%d_prenom" % numEnfant]
                    dictTemp["individu_date_naiss"] = dictValeurs["enfant%d_date_naiss" % numEnfant]
                    dictTemp["individu_cp_naiss"] = dictValeurs["enfant%d_cp_naiss" % numEnfant]
                    dictTemp["individu_ville_naiss"] = dictValeurs["enfant%d_ville_naiss" % numEnfant]
                    dictTemp["individu_tel_mobile"] = dictValeurs["enfant%d_tel_mobile" % numEnfant]
                    dictTemp["individu_email"] = dictValeurs["enfant%d_email" % numEnfant]
                    dictTemp["individu_memo"] = dictValeurs["enfant%d_memo" % numEnfant]
                    
                    dictTemp["individu_tel_domicile"] = dictValeurs["famille_tel_domicile"]
                    dictTemp["individu_adresse_auto"] = adresse_auto

                    dictIDindividus["enfant%d" % numEnfant] = CreationIndividu(dictTemp)
                    if dictIDindividus["enfant%d" % numEnfant] != None :
                        EnregistreRattachement(IDindividu=dictIDindividus["enfant%d" % numEnfant], IDcategorie=2, titulaire=0)
                
                # Autres infos de la fiche FAMILLE
                def AjouteChamp2(key, champ, defaut):
                    if dictValeurs.has_key(key) :
                        valeur = dictValeurs[key]
                        
                        # Spécificité de l'allocataire titulaire
                        if key == "famille_allocataire" :
                            valeur = None
                            if dictValeurs[key] == "pere" and dictIDindividus["pere"] != None :
                                valeur = dictIDindividus["pere"]
                            if dictValeurs[key] == "mere" and dictIDindividus["mere"] != None :
                                valeur = dictIDindividus["mere"]
                                
                    else :
                        valeur = defaut
                    listeDonnees.append((champ, valeur))

                listeDonnees = []
                AjouteChamp2("famille_caisse", "IDcaisse", None)
                AjouteChamp2("famille_num_allocataire", "num_allocataire", None)
                AjouteChamp2("famille_allocataire", "allocataire", None)
                AjouteChamp2("famille_memo", "memo", None)
                DB.ReqMAJ("familles", listeDonnees, "IDfamille", IDfamille)

            index += 1
        
        DB.Close()
        
        # Message de confirmation
        dlg = wx.MessageDialog(self, _(u"%d lignes ont été importées avec succès !") % index, _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        return True

    def AfficheAvertissement(self):
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="infos_importation_individus", valeur=False) == True :
            return

        import DLG_Message_html
        texte = u"""
<CENTER><IMG SRC="Images/32x32/Information.png">
<BR><BR>
<FONT SIZE=2>
<B>Avertissement</B>
<BR><BR>
Cette nouvelle fonctionnalité est expérimentale.
<BR><BR>
Il est conseillé de tester son efficacité et sa stabilité dans un fichier test avant de l'utiliser dans votre fichier de données. 
<BR><BR>
Merci de signaler tout bug rencontré dans la rubrique "Signaler un bug " du forum de Noethys.
</FONT>
</CENTER>
"""
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), nePlusAfficher=True)
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="infos_importation_individus", valeur=nePlusAfficher)

# -----------------------------------------------------------------------------------------------------------------------

class ValidationDonnees():
    def __init__(self, typeImportation=""):
        self.typeImportation = typeImportation
        
        # Récupération des villes
        listeNomsVilles, self.listeVilles, dictRegions, dictDepartements = CTRL_Saisie_adresse.Importation_donnees()
        
        DB = GestionDB.DB()

        # Récupération des secteurs géographiques
        req = """SELECT IDsecteur, nom FROM secteurs ORDER BY nom;"""
        DB.ExecuterReq(req)
        self.listeSecteurs = DB.ResultatReq()

        # Récupération des catégories de travail
        req = """SELECT IDcategorie, nom FROM categories_travail ORDER BY nom;"""
        DB.ExecuterReq(req)
        self.listeCategories = DB.ResultatReq()
        
        # Récupération des caisses
        req = """SELECT IDcaisse, nom FROM caisses ORDER BY nom;"""
        DB.ExecuterReq(req)
        self.listeCaisses = DB.ResultatReq()

        DB.Close()
    
    def Validation(self, code="", valeur=""):
        """ Vérifie et formate une valeur """
        anomalie = None
        ligneValide = True
        label = valeur
        
        # Civilité
        if code.endswith("_civilite") :
            if "enfant" in code and valeur in (u"M", u"m", _(u"Mr"), "M.", _(u"Monsieur"), _(u"Masculin"), u"H", u"h", _(u"Homme"), u"G", u"g", _(u"Garçon")) :
                valeur = 4
                label = _(u"Garçon")
            elif "enfant" in code and valeur in (u"F", u"f", _(u"Madame"), _(u"Mme"), _(u"Féminin"), _(u"Femme"), _(u"Fille")) :
                valeur = 5
                label = _(u"Fille")
            elif "individu" in code and valeur in (u"M", u"m", _(u"Mr"), "M.", _(u"Monsieur"), _(u"Masculin"), u"H", u"h", _(u"Homme")) :
                valeur = 1
                label = _(u"Monsieur")
            elif "individu" in code and valeur in (_(u"Mlle"), _(u"Melle"), _(u"Mademoiselle")) :
                valeur = 2
                label = _(u"Mademoiselle")
            elif "individu" in code and valeur in (_(u"Madame"), _(u"Mme"), _(u"Femme")) :
                valeur = 3
                label = _(u"Madame")
            elif "individu" in code and valeur in (u"G", u"g", _(u"Garçon")) :
                valeur = 4
                label = _(u"Garçon")
            elif "individu" in code and valeur in (u"F", u"f", _(u"Fille")) :
                valeur = 5
                label = _(u"Fille")
            elif "individu" in code and valeur == _(u"Collectivité") :
                valeur = 6
                label = _(u"Collectivité")
            elif "individu" in code and valeur == _(u"Association") :
                valeur = 7
                label = _(u"Association")
            elif "individu" in code and valeur == _(u"Organisme") :
                valeur = 8
                label = _(u"Organisme")
            elif "individu" in code and valeur == _(u"Entreprise") :
                valeur = 9
                label = _(u"Entreprise")
            else :
                anomalie = _(u"Anomalie : Civilité non valide")
                if valeur == "" :
                    label = u""
                else :
                    label = anomalie
                ligneValide = False
                valeur = None
                
            
        # Nom de famille
        if code.endswith("_nom") :
            if valeur == None or valeur == "" :
                anomalie = _(u"Anomalie : Nom de famille non valide")
                ligneValide = False
                valeur = None
                label = ""
            else :
                valeur = valeur.upper()
                label = valeur

        # Nom de jeune fille
        if code.endswith("_nom_jfille") :
            if valeur == None : 
                valeur = ""
            label = valeur

        # Prénom
        if code.endswith("_prenom") :
            if valeur == None : valeur = ""
            label = valeur

        # Date de naissance
        if code.endswith("_date_naiss") :
            if valeur == "" : valeur = None
            if valeur == None :
                anomalie = _(u"Anomalie : Date non valide")
                label = ""
                valeur = None
            elif valeur != None and type(valeur) != datetime.date : 
                anomalie = _(u"Anomalie : Date non valide")
                label = anomalie
                valeur = None
            else :
                if valeur != None :
                    label = DateEngFr(str(valeur))
                else :
                    label = ""
            
        # Rue
        if "_rue_" in code :
            if valeur == None : 
                valeur = ""
            label = valeur

        # Code Postal
        if "_cp_" in code :
            label = valeur
            if valeur == "" : 
                valeur = None
            else :
                valide = False
                for ville, cp in self.listeVilles :
                    if cp == valeur :
                        valide = True
                        break
                if valide == False :
                    anomalie = _(u"Anomalie : Code postal absent de la base de données")
                    valeur = None
                    label = anomalie
    
        # Ville
        if "_ville_" in code :
            label = u""
            if valeur == "" : 
                valeur = None
            else :
                if valeur != None :
                    valeur = valeur.upper()
                    label = valeur
                valide = False
                for ville, cp in self.listeVilles :
                    if ville == valeur :
                        valide = True
                        break
                if valide == False :
                    anomalie = _(u"Anomalie : Ville absente de la base de données")
                    valeur = None
                    label = anomalie

        # Secteur
        if code.endswith("_secteur") :
            label = valeur
            if valeur == "" : 
                valeur = None
            else :
                valide = False
                for IDsecteur, nom in self.listeSecteurs :
                    if nom == valeur :
                        valeur = IDsecteur
                        valide = True
                if valide == False :
                    anomalie = _(u"Anomalie : Secteur géographique absent de la base de données")
                    valeur = None
                    label = anomalie

        # Catégorie
        if code.endswith("_categorie") :
            label = valeur
            if valeur == "" : 
                valeur = None
            else :
                valide = False
                for IDcategorie, nom in self.listeCategories :
                    if nom == valeur :
                        valeur = IDcategorie
                        valide = True
                if valide == False :
                    anomalie = _(u"Anomalie : Catégorie socioprofessionnelle absente de la base de données")
                    valeur = None
                    label = anomalie
    
        # Profession
        if code.endswith("_profession") :
            if valeur == None : 
                valeur = ""
            label = valeur

        # Employeur
        if code.endswith("_employeur") :
            if valeur == None : valeur = ""
            label = valeur

        # Téléphone
        if "_tel_" in code :
            label = valeur
            valide = True
            if valeur == "" :
                label = ""
            else :
                if valeur != None :
                    if len(valeur) != 15 :
                        valide = False
                    for c in valeur :
                        if c not in (".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9") :
                            valide = False
                if valide == False :
                    anomalie = _(u"Anomalie : Numéro de téléphone non valide")
                    valeur = None
                    label = anomalie

        # Email
        if code.endswith("_email") :
            if valeur == "" : 
                valeur = None
            label = valeur

        # Mémo
        if code.endswith("_memo") :
            if valeur == None : 
                valeur = ""
            label = label

        # Caisse
        if code.endswith("_caisse") :
            label = valeur
            if valeur == "" : 
                valeur = None
            else :
                valide = False
                for IDcaisse, nom in self.listeCaisses :
                    if nom == valeur :
                        valeur = IDcaisse
                        valide = True
                if valide == False :
                    anomalie = _(u"Anomalie : Caisse absente de la base de données")
                    valeur = None
                    label = anomalie
        
        # Allocataire titulaire
        if code.endswith("famille_allocataire") :
            if code in (_(u"Père"), _(u"père"), u"P") :
                valeur = "pere"
                label = _(u"Père")
            elif code in (_(u"Mère"), _(u"mère"), u"M") :
                valeur = "mere"
                label = _(u"Mère")
            else :
                anomalie = _(u"Anomalie : Allocataire titulaire non valide")
                if valeur == "" :
                    label = u""
                else :
                    label = anomalie
                valeur = None
        
        
        
        return ligneValide, code, valeur, anomalie, label
        
        
        
        
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        listeDonnees = [
            [_(u"DUPOND"), _(u"Gérard"), datetime.date(1999, 12, 25), _(u"Rue des étés ensoleillés"), u"29870", _(u"LANNILIS")],
            [_(u"DUPOND"), _(u"Sophie"), datetime.date(1999, 12, 24), _(u"Rue des étés ensoleillés"), u"29870", _(u"LANNILIS")],
            ]
        self.ctrl= CTRL_Colonnes(panel, listeDonnees)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

##if __name__ == '__main__':
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None) 
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
