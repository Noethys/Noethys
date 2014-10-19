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
import sys
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import GestionDB
import CTRL_Selection_activites
import wx.lib.agw.supertooltip as STT
import textwrap 


LISTE_CATEGORIES = [

    u"Gestion des fichiers",
    { "label" : u"Fichier de données", "code" : "fichier_fichier", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Sauvegarde manuelle", "code" : "fichier_sauvegarde_manuelle", "actions" : ["creer",], "restriction" : False },
    { "label" : u"Restauration de sauvegarde", "code" : "fichier_restauration", "actions" : ["creer",], "restriction" : False },
    { "label" : u"Sauvegardes automatiques", "code" : "fichier_sauvegardes_auto", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Conversions local/réseau", "code" : "fichier_conversions", "actions" : ["creer",], "restriction" : False },

    u"Paramétrage",
    { "label" : u"Préférences", "code" : "parametrage_preferences", "actions" : ["consulter", "modifier"], "restriction" : False },
    { "label" : u"Enregistrement", "code" : "parametrage_enregistrement", "actions" : ["consulter", "modifier"], "restriction" : False },
    { "label" : u"Utilisateurs", "code" : "parametrage_utilisateurs", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modèles de droits", "code" : "parametrage_modeles_droits", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Utilisateurs réseau", "code" : "parametrage_utilisateurs_reseau", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Organisateur", "code" : "parametrage_organisateur", "actions" : ["consulter", "modifier"], "restriction" : False },
    { "label" : u"Comptes bancaires", "code" : "parametrage_comptes_bancaires", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Groupes d'activités", "code" : "parametrage_groupes_activites", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Activités", "code" : "parametrage_activites", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : True },
    { "label" : u"Modèles de documents", "code" : "parametrage_modeles_docs", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modèles d'Emails", "code" : "parametrage_modeles_emails", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modèles de tickets", "code" : "parametrage_modeles_tickets", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modèles de plannings", "code" : "parametrage_modeles_plannings", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modèles de contrats", "code" : "parametrage_modeles_contrats", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Procédures de badgeage", "code" : "parametrage_procedures_badgeage", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Synthèse vocale", "code" : "parametrage_vocal", "actions" : ["consulter", "modifier"], "restriction" : False },
    { "label" : u"Catégories de messages", "code" : "parametrage_categories_messages", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Types de pièces", "code" : "parametrage_types_pieces", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Catégories sociopro.", "code" : "parametrage_categories_travail", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Villes et codes postaux", "code" : "parametrage_villes", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Secteurs géographiques", "code" : "parametrage_secteurs", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Types de sieste", "code" : "parametrage_types_siestes", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Vacances", "code" : "parametrage_vacances", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Jours fériés", "code" : "parametrage_feries", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Maladies", "code" : "parametrage_maladies", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Vaccins", "code" : "parametrage_vaccins", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Médecins", "code" : "parametrage_medecins", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Restaurateurs", "code" : "parametrage_restaurateurs", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modes de règlements", "code" : "parametrage_modes_reglements", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Emetteurs de règlements", "code" : "parametrage_emetteurs", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Etablissements bancaires", "code" : "parametrage_banques", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Lots de factures", "code" : "parametrage_lots_factures", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Lots de rappels", "code" : "parametrage_lots_rappels", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Régimes sociaux", "code" : "parametrage_regimes", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Caisses", "code" : "parametrage_caisses", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Modèles d'aides journalières", "code" : "parametrage_modeles_aides", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Types de cotisations", "code" : "parametrage_types_cotisations", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Adresses d'expédition d'Emails", "code" : "parametrage_emails_exp", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Listes de diffusion", "code" : "parametrage_listes_diffusion", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Questionnaires", "code" : "parametrage_questionnaires", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Niveaux scolaires", "code" : "parametrage_niveaux_scolaires", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Ecoles", "code" : "parametrage_ecoles", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Classes", "code" : "parametrage_classes", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Compagnies de transports", "code" : "parametrage_compagnies", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Lieux de transports", "code" : "parametrage_lieux", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Lignes de transports", "code" : "parametrage_lignes", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Arrêts de transports", "code" : "parametrage_arrets", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    
    u"Outils",
    { "label" : u"Statistiques", "code" : "outils_stats", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Editeur d'Emails", "code" : "outils_editeur_emails", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Messages", "code" : "outils_messages", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Historique", "code" : "outils_historique", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Utilitaires administrateur", "code" : "outils_utilitaires", "actions" : ["consulter",], "restriction" : False },
    
    u"Gestion des consommations",
    { "label" : u"Consommations", "code" : "consommations_conso", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : True },
    
    u"Gestion des familles",
    { "label" : u"Fiche familiale", "code" : "familles_fiche", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Messages", "code" : "familles_messages", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Questionnaires", "code" : "familles_questionnaires", "actions" : ["consulter", "modifier",], "restriction" : False },
    { "label" : u"Pièces", "code" : "familles_pieces", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Cotisations", "code" : "familles_cotisations", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Aides journalières", "code" : "familles_aides", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Caisse", "code" : "familles_caisse", "actions" : ["consulter", "modifier",], "restriction" : False },
    { "label" : u"Quotients familiaux", "code" : "familles_quotients", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Prestations", "code" : "familles_prestations", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Factures", "code" : "familles_factures", "actions" : ["consulter", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Param. factures par Email", "code" : "familles_factures_email", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Règlements", "code" : "familles_reglements", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Param. prélèvement", "code" : "familles_prelevement", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Mandats SEPA", "code" : "familles_mandats", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Param. reçu par Email", "code" : "familles_recu_email", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Param. avis dépôt par Email", "code" : "familles_depot_email", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Compte internet", "code" : "familles_compte_internet", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Relevé des prestations", "code" : "familles_releve_prestations", "actions" : ["creer",], "restriction" : False },
    { "label" : u"Attestation de présence", "code" : "familles_attestation_presences", "actions" : ["creer",], "restriction" : False },
    { "label" : u"Lettre de rappel", "code" : "familles_lettre_rappel", "actions" : ["creer",], "restriction" : False },
    { "label" : u"Historique", "code" : "familles_historique", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Chronologie", "code" : "familles_chronologie", "actions" : ["consulter",], "restriction" : False },

    u"Gestion des individus",
    { "label" : u"Fiche individuelle", "code" : "individus_fiche", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Photo", "code" : "individus_photo", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Messages", "code" : "individus_messages", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Identité", "code" : "individus_identite", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Liens", "code" : "individus_liens", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Questionnaires", "code" : "individus_questionnaires", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Coordonnées", "code" : "individus_coordonnees", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Inscriptions", "code" : "individus_inscriptions", "actions" : ["modifier", "creer", "supprimer"], "restriction" : True },
    { "label" : u"Scolarité", "code" : "individus_scolarite", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Pièces", "code" : "individus_pieces", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Cotisations", "code" : "individus_cotisations", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Transports", "code" : "individus_transports", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Transports programmés", "code" : "individus_prog_transports", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Vaccins", "code" : "individus_vaccins", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Informations médicales", "code" : "individus_pb_sante", "actions" : ["modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Médecin traitant", "code" : "individus_medecin", "actions" : ["modifier",], "restriction" : False },
    { "label" : u"Historique", "code" : "individus_historique", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Chronologie", "code" : "individus_chronologie", "actions" : ["consulter",], "restriction" : False },

    u"Gestion de la facturation",
    { "label" : u"Vérification ventilation", "code" : "facturation_ventilation", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Factures", "code" : "facturation_factures", "actions" : ["consulter", "creer", "supprimer"], "restriction" : True },
    { "label" : u"Rappels", "code" : "facturation_rappels", "actions" : ["consulter", "creer", "supprimer"], "restriction" : True },
    { "label" : u"Attestations", "code" : "facturation_attestations", "actions" : ["consulter", "creer", "supprimer"], "restriction" : True },
    { "label" : u"Prélèvements auto.", "code" : "facturation_prelevements", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Export Hélios", "code" : "facturation_helios", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    { "label" : u"Solder impayés", "code" : "facturation_solder_impayes", "actions" : ["creer",], "restriction" : False },

    u"Gestion des cotisations",
    { "label" : u"Liste des cotisations", "code" : "cotisations_liste", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Cotisations manquantes", "code" : "cotisations_manquantes", "actions" : ["consulter", ], "restriction" : False },
    { "label" : u"Dépôts de cotisations", "code" : "cotisations_depots", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },

    u"Gestion des règlements",
    { "label" : u"Liste des reçus", "code" : "reglements_recus", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Liste des règlements", "code" : "reglements_liste", "actions" : ["consulter",], "restriction" : False },
    { "label" : u"Dépôts de règlements", "code" : "reglements_depots", "actions" : ["consulter", "modifier", "creer", "supprimer"], "restriction" : False },
    
    ]


##x = 0
##for item in LISTE_CATEGORIES :
##    if type(item) == dict :
##        x += len(item["actions"])
##print "%d verrous" % x


LISTE_ACTIONS = [
    
    { "label" : u"Consulter", "code" : "consulter"},
    { "label" : u"Modifier", "code" : "modifier"},
    { "label" : u"Créer", "code" : "creer"},
    { "label" : u"Supprimer", "code" : "supprimer"},

    ]

COULEUR_CASE_AUTORISATION = wx.Colour(156, 218, 0) 
COULEUR_CASE_RESTRICTION = wx.Colour(255, 198, 45) 
COULEUR_CASE_INTERDICTION = wx.Colour(249, 66, 66) 
COULEUR_CASE_INACTIVE = wx.Colour(215, 215, 215)
COULEUR_CASE_GROUPE = wx.Colour(192, 192, 192)
COULEUR_CASE_DISABLE = wx.Colour(230, 230, 230)



class MyRowLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, row):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
##        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)






class Case():
    def __init__(self, grid, numLigne=None, numColonne=None, dictCategorie=None, dictAction=None, numGroupe=None, nomGroupe="", etat=None):
        self.grid = grid
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.dictCategorie = dictCategorie
        self.dictAction = dictAction
        self.numGroupe = numGroupe
        self.nomGroupe = nomGroupe
        if type(self.dictCategorie) == dict :
            self.typeLigne = "categorie"
        else :
            self.typeLigne = "groupe"
            
        self.etat = etat # états possibles = groupe, inactif, autorisation, interdiction, restriction
        
        # Dessin de la case
        self.renderer = RendererCase(self)
        self.grid.SetCellValue(self.numLigne, self.numColonne, u"")
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

    def GetRect(self):
        return self.grid.CellToRect(self.numLigne, self.numColonne)

    def Refresh(self):
        rect = self.GetRect()
        x, y = self.grid.CalcScrolledPosition(rect.GetX(), rect.GetY())
        rect = wx.Rect(x, y, rect.GetWidth(), rect.GetHeight())
        self.grid.GetGridWindow().Refresh(False, rect)

    def OnClickGauche(self):
        # Si inactif
        if self.etat == "inactif" : 
            return
        # Si autorisation, interdiction ou restriction
        if self.etat == "autorisation" : 
            self.SetEtat("interdiction")
        elif self.etat == "interdiction" : 
            self.SetEtat("autorisation")
        elif self.etat.startswith("restriction") : 
            self.SetEtat("autorisation")
    
    def SetEtat(self, etat=""):
        if etat.startswith("restriction") and self.dictCategorie["restriction"] == False :
            return
        self.etat = etat
        self.Refresh() 

    def GetStatutTexte(self, x, y):
        try :
            texte = u"%s - %s" % (self.dictCategorie["label"], self.dictAction["label"])
        except :
            texte = ""
        return texte

    def GetTexteInfobulle(self):
        """ Renvoie le texte pour l'infobulle de la case """
        if self.etat in ("inactif", "groupe") :
            return None
        
        dictDonnees = {}
        # Titre
        dictDonnees["titre"] = self.dictCategorie["label"]
        # Image
        dictDonnees["bmp"] = self.renderer.bmp
        # Texte
        texte = ""
        if self.dictAction["code"] == "consulter" : texte = u"Consultation"
        if self.dictAction["code"] == "modifier" : texte = u"Modification"
        if self.dictAction["code"] == "creer" : texte = u"Création"
        if self.dictAction["code"] == "supprimer" : texte = u"Suppression"
        
        if self.etat == "autorisation" : texte += u" autorisée"
        if self.etat == "interdiction" : texte += u" interdite"
        if self.etat.startswith("restriction") : 
            code = self.etat.replace("restriction_", "")
            mode, listeID = code.split(":")
            listeID = [int(x) for x in listeID.split(";")]
            labelRestriction = self.grid.GetNomsActivites(mode, listeID)
            texte += u" autorisée mais restreinte %s" % labelRestriction

        dictDonnees["texte"] = "\n".join(textwrap.wrap(texte, 50)) + u"\n\n\n"
        # Pied
        dictDonnees["pied"] = u"Cliquez sur le bouton droit pour afficher le menu contextuel"
        # Couleur
        dictDonnees["couleur"] = self.renderer.couleurFond
        return dictDonnees

        
class RendererCase(gridlib.PyGridCellRenderer):
    def __init__(self, case):
        gridlib.PyGridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        
        # Recherche couleur case
        bmp = None
        
        if self.case.etat == "groupe" :
            couleurFond = COULEUR_CASE_GROUPE
        elif self.case.etat == "inactif" :
            couleurFond = COULEUR_CASE_INACTIVE
        elif self.case.etat == "autorisation" :
            couleurFond = COULEUR_CASE_AUTORISATION
            bmp = wx.Bitmap("Images/16x16/Ok4.png", wx.BITMAP_TYPE_ANY) 
            if self.grid.modeDisable == True : couleurFond = COULEUR_CASE_DISABLE
        elif self.case.etat == "interdiction" :
            couleurFond = COULEUR_CASE_INTERDICTION
            bmp = wx.Bitmap("Images/16x16/Interdit2.png", wx.BITMAP_TYPE_ANY) 
            if self.grid.modeDisable == True : couleurFond = COULEUR_CASE_DISABLE
        else :
            couleurFond = COULEUR_CASE_RESTRICTION
            bmp = wx.Bitmap("Images/16x16/Ok4_orange.png", wx.BITMAP_TYPE_ANY) 
            if self.grid.modeDisable == True : couleurFond = COULEUR_CASE_DISABLE
        
        # Dessin du fond de couleur
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        
        # Dessin d'une image
        if bmp != None :
            tailleImage = 16
            paddingImage = 3
            dc.DrawBitmap(bmp, rect[0] + ((rect[2] - tailleImage) / 2.0), rect[1] + ((rect[3] - tailleImage) / 2.0))
        
        # Mémorisation pour infobulle
        self.bmp = bmp
        self.couleurFond = couleurFond
        
        # Ecrit les restrictions
##        dc.SetBackgroundMode(wx.TRANSPARENT)
##        dc.SetFont(attr.GetFont())
##        hAlign, vAlign = grid.GetCellAlignment(row, col)
##        if self.case.etat.startswith("restriction") :
##            texte = u"Uniquement pour le centre de loisirs"
##            texte = self.AdapteTailleTexte(dc, texte, rect[2]-6)
##            largeur, hauteur = dc.GetTextExtent(texte)
##            x = rect[0] + ((rect[2] - largeur) / 2.0)
##            y = rect[1] + ((rect[3] - hauteur) / 2.0)
##            dc.DrawText(texte, x, y)

        
        
    def DrawBorder(self, grid, dc, rect):
        """
        Draw a standard border around the label, to give a simple 3D
        effect like the stock wx.grid.Grid labels do.
        """
        top = rect.top
        bottom = rect.bottom
        left = rect.left
        right = rect.right        
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(right, top, right, bottom)
        dc.DrawLine(left, top, left, bottom)
        dc.DrawLine(left, bottom, right, bottom)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawLine(left+1, top, left+1, bottom)
        dc.DrawLine(left+1, top, right, top)

            
    def MAJ(self):
        if self.grid != None :
            self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()
    
    def AdapteTailleTexte(self, dc, texte, tailleMaxi):
        """ Raccourcit le texte de l'intitulé en fonction de la taille donnée """
        # Pas de retouche nécessaire
        if dc.GetTextExtent(texte)[0] < tailleMaxi : return texte
        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= dc.GetTextExtent("W...")[0] : return "..."
        # Retouche nécessaire
        tailleTexte = dc.GetTextExtent(texte)[0]
        texteTemp = ""
        texteTemp2 = ""
        for lettre in texte :
            texteTemp += lettre
            if dc.GetTextExtent(texteTemp +"...")[0] < tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..." 










class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent, IDutilisateur=None, IDmodele=None):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.parent = parent
        self.IDutilisateur = IDutilisateur
        self.IDmodele = IDmodele
        
        self.SetMinSize((10, 10))
        self.moveTo = None
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(180)
        self.DisableDragColSize()
        self.DisableDragRowSize()
        self.ImportationActivites() 
        self.modeDisable = False

        # Init Tooltip
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip après 10 secs
        
        # Binds
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClick)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseOver)
        self.GetGridWindow().Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
    
    def SetModeDisable(self, etat=True):
        self.modeDisable = etat
        self.MAJ() 
        
    def ImportationActivites(self):
        """ Importation des activités et groupes d'activités """
        DB = GestionDB.DB()
        
        req = """SELECT IDactivite, nom FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictActivites = {}
        for IDactivite, nom in listeDonnees :
            self.dictActivites[IDactivite] = nom
        
        req = """SELECT IDtype_groupe_activite, nom FROM types_groupes_activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictGroupesActivites = {}
        for IDtype_groupe_activite, nom in listeDonnees :
            self.dictGroupesActivites[IDtype_groupe_activite] = nom
        
        DB.Close()
    
    def GetNomsActivites(self, mode="", listeID=[]):
        listeNoms = []
        texte = u""
        if mode == "groupes" :
            for ID in listeID :
                if self.dictGroupesActivites.has_key(ID) :
                    listeNoms.append(self.dictGroupesActivites[ID])
            if len(listeNoms) == 0 : texte = u""
            if len(listeNoms) == 1 : texte = u"au groupe d'activités %s" % listeNoms[0]
            if len(listeNoms) == 2 : texte = u"aux groupes d'activités %s et %s" % (listeNoms[0], listeNoms[1])
            if len(listeNoms) > 2 : texte = u"aux groupes d'activités %s et %s" % (", ".join(listeNoms[:-1]), listeNoms[-1])
        if mode == "activites" :
            for ID in listeID :
                if self.dictActivites.has_key(ID) :
                    listeNoms.append(self.dictActivites[ID])
            if len(listeNoms) == 0 : texte = u""
            if len(listeNoms) == 1 : texte = u"à l'activité %s" % listeNoms[0]
            if len(listeNoms) == 2 : texte = u"aux activités %s et %s" % (listeNoms[0], listeNoms[1])
            if len(listeNoms) > 2 : texte = u"aux activités %s et %s" % (", ".join(listeNoms[:-1]), listeNoms[-1])
        return texte
    
    def Importation(self):
        """ Importation des droits """
        self.dictDroits = {}
        
        # EXEMPLE DE DONNEES
##        self.dictDroits = {
##            ("parametrage_utilisateurs", "consulter") : {"etat" : "autorisation", "IDdroit" : None"},
##            ("parametrage_utilisateurs", "modifier") : {"etat" : "autorisation", "IDdroit" : None"},
##            ("parametrage_utilisateurs", "creer") : {"etat" : ""restriction_groupes:1"", "IDdroit" : None"},
##            ("parametrage_utilisateurs", "supprimer") : {"etat" : "interdiction", "IDdroit" : None"},
##            ("parametrage_modes_reglements", "supprimer") : {"etat" : "autorisation", "IDdroit" : None"},
##            }
        
        # Condition
        if self.IDutilisateur != None :
            condition = "IDutilisateur=%d" % self.IDutilisateur
        elif self.IDmodele != None :
            condition = "IDmodele=%d" % self.IDmodele
        else :
            return
        
        # Consultation de la base
        DB = GestionDB.DB()
        req = """SELECT IDdroit, categorie, action, etat
        FROM droits
        WHERE %s;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        # Mémorisation dans le dictDroits
        for IDdroit, categorie, action, etat in listeDonnees :
            self.dictDroits[(categorie, action)] = {"etat" : etat, "IDdroit" : IDdroit}
    
    def Sauvegarde(self, IDmodele=None, IDutilisateur=None):
        """ Sauvegarde des droits dans la base """
        if IDmodele != None : self.IDmodele = IDmodele
        if IDutilisateur != None : self.IDutilisateur = IDutilisateur
        
        DB = GestionDB.DB()
        
        listeValeurs = self.GetValeurs()
        
        listeAjouts = []
        for categorie, action, etat in listeValeurs :
            key = (categorie, action)
            listeDonnees = [("IDutilisateur", self.IDutilisateur), ("IDmodele", self.IDmodele), ("categorie", categorie), ("action", action), ("etat", etat)]
            
            if self.dictDroits.has_key(key) :
                # Modification d'un état existant
                ancienEtat = self.dictDroits[key]["etat"]
                IDdroit = self.dictDroits[key]["IDdroit"]
                if etat != ancienEtat :
                    DB.ReqMAJ("droits", listeDonnees, "IDdroit", IDdroit)
            else :
                # Saisie d'un nouvel état
                listeAjouts.append((self.IDutilisateur, self.IDmodele, categorie, action, etat))
        
        # Ajout optimisé
        if len(listeAjouts) > 0 :
            DB.Executermany("INSERT INTO droits (IDutilisateur, IDmodele, categorie, action, etat) VALUES (?, ?, ?, ?, ?)", listeAjouts, commit=False)
            DB.Commit() 
        
        # Recherche des suppressions à réaliser
        for key, dictValeurs in self.dictDroits.iteritems() :
            found = False
            for categorie, action, etat in listeValeurs :
                if categorie == key[0] and action == key[1] : 
                    found = True
            if found == False :
                DB.ReqDEL("droits", "IDdroit", dictValeurs["IDdroit"])
        
        DB.Close()
    
    def GetValeurs(self):
        """ Récupère les valeurs des cases """
        listeValeurs = []
        for coords, case in self.dictCases.iteritems() :
            if case.typeLigne == "categorie" :
                codeCategorie = case.dictCategorie["code"]
                codeAction = case.dictAction["code"]
                etat = case.etat
                if etat != "inactif" :
                    listeValeurs.append((codeCategorie, codeAction, etat))
        return listeValeurs
        
        
    def MAJ(self):
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.caseSurvolee = None
        self.Importation() 
        self.InitGrid()
        self.Refresh()
        
    def InitGrid(self):
        self.dictCases = {}
        
        # ----------------- Création des colonnes --------------------------
        nbreColonnes = len(LISTE_ACTIONS)
        largeurColonneAction = 100
        self.AppendCols(nbreColonnes)
        numColonne = 0
        
        for dictAction in LISTE_ACTIONS :
            self.SetColLabelValue(numColonne, dictAction["label"])
            self.SetColSize(numColonne, largeurColonneAction)
            numColonne += 1
        
        # ------------------ Création des lignes -------------------------------------------------------
        nbreLignes = len(LISTE_CATEGORIES)
        self.AppendRows(nbreLignes)
        
        numLigne = 0
        numGroupe = -1
        nomGroupe = ""
        for dictCategorie in LISTE_CATEGORIES :
            
            # Groupe de catégorie
            if type(dictCategorie) != dict :
                typeLigne = "groupe"
                nomGroupe = dictCategorie
                hauteurLigne = 20
                self.SetRowLabelValue(numLigne, nomGroupe)
                self.SetRowSize(numLigne, hauteurLigne)
                self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_CASE_GROUPE))
                numGroupe += 1
            
            
            # Catégorie
            if type(dictCategorie) == dict :
                typeLigne = "categorie"
                hauteurLigne = 30
                label = dictCategorie["label"]
                if dictCategorie["restriction"] == True :
                    label += u"*"
                self.SetRowLabelValue(numLigne, label)
                self.SetRowSize(numLigne, hauteurLigne)
                self.SetRowLabelRenderer(numLigne, None)
            
            # Cases
            numColonne = 0
            for dictAction in LISTE_ACTIONS :
                
                # Recherche de l'état de la case
                if typeLigne == "groupe" :
                    etat = "groupe"
                    
                if typeLigne == "categorie" :
                    if dictAction["code"] not in dictCategorie["actions"] :
                        etat = "inactif"
                    else :
                        etat = "autorisation"
                        key = (dictCategorie["code"], dictAction["code"])
                        if self.dictDroits.has_key(key) :
                            etat = self.dictDroits[key]["etat"]
                
                # Création de la case
                case = Case(self, numLigne, numColonne, dictCategorie, dictAction, numGroupe, nomGroupe, etat)
                self.dictCases[(numLigne, numColonne)] = case
                numColonne += 1
                        
            numLigne += 1    

    def OnLeaveWindow(self, event):
        self.ActiveTooltip(False) 
        self.EcritStatusbar(None)

    def OnMouseOver(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        if self.dictCases.has_key((numLigne, numColonne)) :
            case = self.dictCases[(numLigne, numColonne)]
        else :
            case = None
        if case != None :
            if case != self.caseSurvolee :
                self.ActiveTooltip(actif=False)
                # Attribue une info-bulle
                self.ActiveTooltip(actif=True, case=case)
                self.caseSurvolee = case
        else:
            self.caseSurvolee = None
            self.ActiveTooltip(actif=False)
        self.EcritStatusbar(case, x, y)
        event.Skip()

    def OnLeftClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        self.ActiveTooltip(actif=False)
        if self.dictCases.has_key((numLigne, numColonne)) :
            case = self.dictCases[(numLigne, numColonne)]
            case.OnClickGauche()
        event.Skip()

    def OnRightClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        self.ActiveTooltip(actif=False)
        self.case_selection = None
        if self.dictCases.has_key((numLigne, numColonne)) :
            case = self.dictCases[(numLigne, numColonne)]
            if case.typeLigne == "categorie" and case.etat != "inactif" :
                self.case_selection = case
        if self.case_selection == None :
            return
        
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        nomCategorie = self.GetRowLabelValue(numLigne)
        nomAction = self.GetColLabelValue(numColonne)
        nomGroupe = case.nomGroupe
        
        # Titre
        titre = u"%s - %s" % (nomCategorie, nomAction)
        item = wx.MenuItem(menuPop, 10, titre)
        menuPop.AppendItem(item)
        item.Enable(False)
        
        menuPop.AppendSeparator()
        
        listeItems = [
            (100, u"Autoriser"),
            (200, u"Interdire"),
            (300, u"Restreindre"),
            ]
            
        listeSousItems = [
            (1, u"La case", u"Uniquement sur la case", "Images/16x16/Tableau_case.png"),
            (2, u"Toute la ligne", u"Sur toute la ligne", "Images/16x16/Tableau_ligne.png"),
            (3, u"Toute la colonne", u"Sur toute la colonne", "Images/16x16/Tableau_colonne.png"),
            (4, u"Tout le tableau", u"Sur toutes les lignes du tableau", "Images/16x16/Tableau_zone.png"),
            (5, u"Toutes les cases du groupe '%s'" % nomGroupe, u"Sur toutes les cases du groupe '%s'" % nomGroupe, "Images/16x16/Tableau_zone.png"),
            (6, u"Toute la colonne du groupe '%s'" % nomGroupe, u"Sur toute la colonne du groupe '%s'" % nomGroupe, "Images/16x16/Tableau_colonne.png"),
            ]           

        for IDitem, labelItem in listeItems :
            sousMenu = wx.Menu()
            for IDsousItem, labelSousItem, tip, bmp in listeSousItems :
                ID = IDitem+IDsousItem
                item = wx.MenuItem(menuPop, ID, labelSousItem, tip)
                item.SetBitmap(wx.Bitmap(bmp, wx.BITMAP_TYPE_PNG))
                sousMenu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnActionMenuContextuel, id=ID)
            item = menuPop.AppendMenu(IDitem, labelItem, sousMenu)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def OnActionMenuContextuel(self, event):
        ID = event.GetId() 
        
        # Sélectionne l'état à appliquer
        if str(ID)[0] == "1" : 
            etat = "autorisation"
            IDcommande = ID-100
        if str(ID)[0] == "2" : 
            etat = "interdiction"
            IDcommande = ID-200
        if str(ID)[0] == "3" : 
            etat = "restriction"
            IDcommande = ID-300
            etat = self.DemanderRestrictions()
            
        if etat == None :
            return
        
        # Appliquer
        for case in self.RechercherCases(IDcommande, self.case_selection) :
            case.SetEtat(etat)
    
    def DemanderRestrictions(self):
        code = None
        dlg = DLG_Restrictions(self)
        if dlg.ShowModal() == wx.ID_OK :
            code = "restriction_" + dlg.GetCode() 
        dlg.Destroy()
        return code
        
    def RechercherCases(self, IDcommande=None, caseReference=None):
        """ Rechercher les cases par case, ligne, colonne, ligne du groupe, etc... """
        listeCases = []
        # La case
        if IDcommande == 1 :
            if caseReference.etat not in ("inactif", "groupe") :
                listeCases.append(caseReference)
        # Toute la ligne
        if IDcommande == 2 :
            for coords, case in self.dictCases.iteritems() :
                if caseReference.numLigne == case.numLigne and case.etat not in ("inactif", "groupe") :
                    listeCases.append(case)
        # Toute la colonne
        if IDcommande == 3 :
            for coords, case in self.dictCases.iteritems() :
                if caseReference.numColonne == case.numColonne and case.etat not in ("inactif", "groupe") :
                    listeCases.append(case)
        # Toute le tableau
        if IDcommande == 4 :
            for coords, case in self.dictCases.iteritems() :
                if case.etat not in ("inactif", "groupe") :
                    listeCases.append(case)
        # Toute les lignes du groupe
        if IDcommande == 5 :
            for coords, case in self.dictCases.iteritems() :
                if caseReference.numGroupe == case.numGroupe and case.etat not in ("inactif", "groupe") :
                    listeCases.append(case)
        # Toute la colonne du groupe
        if IDcommande == 6 :
            for coords, case in self.dictCases.iteritems() :
                if caseReference.numColonne == case.numColonne and caseReference.numGroupe == case.numGroupe and case.etat not in ("inactif", "groupe") :
                    listeCases.append(case)
        return listeCases
        
    def AfficheTooltip(self):
        """ Création du supertooltip """
        case = self.tip.case
        
        # Récupération des données du tooltip
        dictDonnees = case.GetTexteInfobulle()
        if dictDonnees == None :
            self.ActiveTooltip(actif=False)
            return
        
        # Paramétrage du tooltip
        font = self.GetFont()
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        if dictDonnees.has_key("couleur") :
            couleur = dictDonnees["couleur"]
            self.tip.SetTopGradientColour(couleur)
            self.tip.SetMiddleGradientColour(wx.Colour(255,255,255))
            self.tip.SetBottomGradientColour(wx.Colour(255,255,255))
            self.tip.SetTextColor(wx.Colour(76,76,76))
        else :
            styleTooltip = "Office 2007 Blue"
            self.tip.ApplyStyle(styleTooltip)
            
        # Titre du tooltip
        bmp = None
        if dictDonnees.has_key("bmp") :
            bmp = dictDonnees["bmp"]
        self.tip.SetHeaderBitmap(bmp)
        
        titre = None
        if dictDonnees.has_key("titre") :
            titre = dictDonnees["titre"]
            self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
            self.tip.SetHeader(titre)
            self.tip.SetDrawHeaderLine(True)

        # Corps du message
        texte = dictDonnees["texte"]
        self.tip.SetMessage(texte)

        # Pied du tooltip
        pied = None
        if dictDonnees.has_key("pied") :
            pied = dictDonnees["pied"]
        self.tip.SetDrawFooterLine(True)
        self.tip.SetFooterBitmap(wx.Bitmap(u"Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        self.tip.SetFooterFont(wx.Font(7, font.GetFamily(), font.GetStyle(), wx.LIGHT, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetFooter(pied)

        # Affichage du Frame tooltip
        self.tipFrame = STT.ToolTipWindow(self, self.tip)
        self.tipFrame.CalculateBestSize()
        x, y = wx.GetMousePosition()
        self.tipFrame.SetPosition((x+15, y+17))
        self.tipFrame.DropShadow(True)
        self.tipFrame.StartAlpha(True) # ou .Show() pour un affichage immédiat
        
        # Arrêt du timer
        self.timerTip.Stop()
        del self.timerTip

    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try :
                self.tipFrame.Destroy()
                del self.tipFrame
            except :
                pass

    def ActiveTooltip(self, actif=True, case=None):
        if actif == True :
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False :
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(1500)
                self.tip.case = case
        else:
            # Désactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.case = None
            self.CacheTooltip() 
            self.caseSurvolee = None

    def EcritStatusbar(self, case=None, x=None, y=None):
        if case == None : 
            texte = u""
        else :
            texte = case.GetStatutTexte(x, y)
            if texte == None : texte = u""
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass
        






# -------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Restrictions(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        self.label_intro = wx.StaticText(self, wx.ID_ANY, u"Vous pouvez sélectionner des activités ou des groupes d'activités :")
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        self.bouton_aide = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        # Propriétés
        self.SetTitle(u"Appliquer des restrictions")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((500, 500))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALL, 10)
        grid_sizer_base.Add(self.ctrl_activites, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):  
        if self.ctrl_activites.Validation() == False :
            return
        self.EndModal(wx.ID_OK)
        
    def GetCode(self):
        mode, listeID = self.ctrl_activites.GetValeurs() 
        code = "%s:%s" % (mode, ";".join([str(x) for x in listeID]))
        return code
    
    def SetCode(self, code=""):
        mode, listeID = code.split(":")
        listeID = [int(x) for x in listeID]
        self.ctrl_activites.SetValeurs(mode, listeID)
        


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ() 
        self.bouton1 = wx.Button(panel, -1, u"Test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton1, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((800, 500))
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton1)
    
    def OnBouton1(self, event):
        for x in self.ctrl.GetValeurs() :
            print x
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
##    frame_1 = DLG_Restrictions(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    
