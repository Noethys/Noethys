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
import wx.grid as gridlib
import datetime
import CTRL_Saisie_heure
import CTRL_Saisie_date
import GestionDB
import UTILS_Questionnaires
import wx.lib.wordwrap as wordwrap


LISTE_METHODES = [
    { "code" : "montant_unique", "label" : _(u"Montant unique"), "type" : "unitaire", "nbre_lignes_max" : 1, "entete" : None, "champs" : ("montant_unique", "montant_questionnaire"), "champs_obligatoires" : ("montant_unique",) },
    { "code" : "qf", "label" : _(u"En fonction du quotient familial"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : "tranche", "champs" : ("qf_min", "qf_max", "montant_unique"), "champs_obligatoires" : ("qf_min", "qf_max", "montant_unique") },
    
    { "code" : "horaire_montant_unique", "label" : _(u"Montant unique en fonction d'une tranche horaire"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "temps_facture", "montant_unique", "montant_questionnaire", "label"), "champs_obligatoires" : ("heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "montant_unique") },
    { "code" : "horaire_qf", "label" : _(u"En fonction d'une tranche horaire et du quotient familial"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("qf_min", "qf_max", "heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "temps_facture", "montant_unique", "label"), "champs_obligatoires" : ("qf_min", "qf_max", "heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "montant_unique") },
    
    { "code" : "duree_montant_unique", "label" : _(u"Montant unique en fonction d'une durée"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("duree_min", "duree_max", "temps_facture", "montant_unique", "montant_questionnaire", "label"), "champs_obligatoires" : ("duree_min", "duree_max", "montant_unique") },
    { "code" : "duree_qf", "label" : _(u"En fonction d'une durée et du quotient familial"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("qf_min", "qf_max", "duree_min", "duree_max", "temps_facture", "montant_unique", "label"), "champs_obligatoires" : ("qf_min", "qf_max", "duree_min", "duree_max", "montant_unique") },
    
    { "code" : "montant_unique_date", "label" : _(u"Montant unique en fonction de la date"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("date", "montant_unique", "label"), "champs_obligatoires" : ("date", "montant_unique") },
    { "code" : "qf_date", "label" : _(u"En fonction de la date et du quotient familial"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("date", "qf_min", "qf_max", "montant_unique", "label"), "champs_obligatoires" : ("date", "qf_min", "qf_max", "montant_unique") },
    
    { "code" : "variable", "label" : _(u"Tarif libre (Saisi par l'utilisateur)"), "type" : "unitaire", "nbre_lignes_max" : 0, "entete" : None, "champs" : (), "champs_obligatoires" : () },
    { "code" : "choix", "label" : _(u"Tarif au choix (Sélectionné par l'utilisateur)"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("montant_unique", "label"), "champs_obligatoires" : ("montant_unique",) },
    
    { "code" : "montant_unique_nbre_ind", "label" : _(u"Montant unique en fonction du nombre d'individus de la famille présents"), "type" : "unitaire", "nbre_lignes_max" : 1, "entete" : "tranche", "champs" : ("montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", ), "champs_obligatoires" : ("montant_enfant_1") },
    { "code" : "qf_nbre_ind", "label" : _(u"En fonction du quotient familial et du nombre d'individus de la famille présents"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : "tranche", "champs" : ("qf_min", "qf_max", "montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", ), "champs_obligatoires" : ("qf_min", "qf_max", "montant_enfant_1") },
    { "code" : "horaire_montant_unique_nbre_ind", "label" : _(u"Montant unique en fonction du nombre d'individus de la famille présents et de la tranche horaire"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : "tranche", "champs" : ("heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "temps_facture", "montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", "label"), "champs_obligatoires" : ("heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "montant_enfant_1") },
    { "code" : "montant_unique_nbre_ind_degr", "label" : _(u"Montant dégressif en fonction du nombre d'individus de la famille présents"), "type" : "unitaire", "nbre_lignes_max" : 1, "entete" : "tranche", "champs" : ("montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", ), "champs_obligatoires" : ("montant_enfant_1") },
    { "code" : "qf_nbre_ind_degr", "label" : _(u"Montant dégressif en fonction du quotient familial et du nombre d'individus de la famille présents"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : "tranche", "champs" : ("qf_min", "qf_max", "montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", ), "champs_obligatoires" : ("qf_min", "qf_max", "montant_enfant_1") },
    { "code" : "horaire_montant_unique_nbre_ind_degr", "label" : _(u"Montant dégressif en fonction du nombre d'individus de la famille présents et de la tranche horaire"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : "tranche", "champs" : ("heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "temps_facture", "montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", "label"), "champs_obligatoires" : ("heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "montant_enfant_1") },
    
    { "code" : "duree_coeff_montant_unique", "label" : _(u"Montant au prorata d'une durée"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("duree_min", "duree_max", "duree_seuil", "duree_plafond", "unite_horaire", "montant_unique", "montant_questionnaire", "ajustement", "label"), "champs_obligatoires" : ("unite_horaire", "montant_unique") },
    { "code" : "duree_coeff_qf", "label" : _(u"Montant au prorata d'une durée et selon le quotient familial"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("qf_min", "qf_max", "duree_min", "duree_max", "duree_seuil", "duree_plafond", "unite_horaire", "montant_unique", "ajustement", "label"), "champs_obligatoires" : ("qf_min", "qf_max", "unite_horaire", "montant_unique") },

    { "code" : "taux_montant_unique", "label" : _(u"Par taux d'effort"), "type" : "unitaire", "nbre_lignes_max" : 1, "entete" : None, "champs" : ("taux", "montant_min", "montant_max", "ajustement", "label"), "champs_obligatoires" : ("taux",) },
    { "code" : "taux_qf", "label" : _(u"Par taux d'effort et par tranches de QF"), "type" : "unitaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("qf_min", "qf_max", "taux", "montant_min", "montant_max", "ajustement", "label"), "champs_obligatoires" : ("qf_min", "qf_max", "taux",) },
    { "code" : "duree_taux_montant_unique", "label" : _(u"Par taux d'effort et en fonction d'une durée"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("duree_min", "duree_max", "temps_facture", "taux", "montant_min", "montant_max", "ajustement", "label"), "champs_obligatoires" : ("duree_min", "duree_max", "taux") },
    { "code" : "duree_taux_qf", "label" : _(u"Par taux d'effort et par tranches de QF en fonction d'une durée"), "type" : "horaire", "nbre_lignes_max" : None, "entete" : None, "champs" : ("qf_min", "qf_max", "duree_min", "duree_max", "temps_facture", "taux", "montant_min", "montant_max", "ajustement", "label"), "champs_obligatoires" : ("qf_min", "qf_max", "duree_min", "duree_max", "taux") },

]

LISTE_COLONNES = [
    { "code" : "tranche", "label" : _(u"Tranche"), "largeur" : 60, "editeur" : None, "infobulle" : _(u"Tranche") },
    { "code" : "qf_min", "label" : _(u"QF\nmin >="), "largeur" : 70, "editeur" : "decimal", "infobulle" : _(u"Quotient familial minimal") },
    { "code" : "qf_max", "label" : _(u"QF\nmax <="), "largeur" : 70, "editeur" : "decimal", "infobulle" : _(u"Quotient familial maximal") },
    { "code" : "montant_unique", "label" : _(u"Tarif"), "largeur" : 70, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "montant_questionnaire", "label" : _(u"Tarif questionnaire"), "largeur" : 130, "editeur" : "questionnaire", "infobulle" : _(u"Montant renseigné dans les questionnaires familiaux ou individuels") },
    { "code" : "montant_enfant_1", "label" : _(u"Tarif\n1 ind."), "largeur" : 60, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "montant_enfant_2", "label" : _(u"Tarif\n2 ind."), "largeur" : 60, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "montant_enfant_3", "label" : _(u"Tarif\n3 ind."), "largeur" : 60, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "montant_enfant_4", "label" : _(u"Tarif\n4 ind."), "largeur" : 60, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "montant_enfant_5", "label" : _(u"Tarif\n5 ind."), "largeur" : 60, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "montant_enfant_6", "label" : _(u"Tarif\n6 ind."), "largeur" : 60, "editeur" : "decimal4", "infobulle" : _(u"Montant") },
    { "code" : "nbre_enfants", "label" : _(u"Nb enfants"), "largeur" : 70, "editeur" : None, "infobulle" : _(u"Nombre d'enfants") },
    { "code" : "coefficient", "label" : _(u"Coefficient"), "largeur" : 70, "editeur" : "decimal", "infobulle" : _(u"Coefficient") },
    { "code" : "montant_min", "label" : _(u"Montant\nmin"), "largeur" : 70, "editeur" : "decimal4", "infobulle" : _(u"Montant minimal") },
    { "code" : "montant_max", "label" : _(u"Montant\nmax"), "largeur" : 70, "editeur" : "decimal4", "infobulle" : _(u"Montant maximal") },
    { "code" : "heure_debut_min", "label" : _(u"Heure Début\nmin >="), "largeur" : 77, "editeur" : "heure", "infobulle" : _(u"Heure de début minimale") },
    { "code" : "heure_debut_max", "label" : _(u"Heure Début\nmax <="), "largeur" : 77, "editeur" : "heure", "infobulle" : _(u"Heure de début maximale") },
    { "code" : "heure_fin_min", "label" : _(u"Heure Fin\nmin >="), "largeur" : 75, "editeur" : "heure", "infobulle" : _(u"Heure de fin minimale") },
    { "code" : "heure_fin_max", "label" : _(u"Heure Fin\nmax <="), "largeur" : 75, "editeur" : "heure", "infobulle" : _(u"Heure de fin maximale") },
    { "code" : "duree_min", "label" : _(u"Durée\nmin >="), "largeur" : 70, "editeur" : "heure", "infobulle" : _(u"Durée minimale") },
    { "code" : "duree_max", "label" : _(u"Durée\nmax <="), "largeur" : 70, "editeur" : "heure", "infobulle" : _(u"Durée maximale") },
    { "code" : "date", "label" : _(u"Date"), "largeur" : 80, "editeur" : "date", "infobulle" : _(u"Date") },
    { "code" : "label", "label" : _(u"Label de la prestation (Optionnel)"), "largeur" : 220, "editeur" : None, "infobulle" : _(u"Label de la prestation. Variables disponibles :\n{QUANTITE}, {TEMPS_REALISE}, {TEMPS_FACTURE}, {HEURE_DEBUT}, {HEURE_FIN}.") },
    { "code" : "temps_facture", "label" : _(u"Temps facturé\n(pour la CAF)"), "largeur" : 90, "editeur" : "heure", "infobulle" : _(u"Temps facturé") },
    { "code" : "unite_horaire", "label" : _(u"Unité\nhoraire"), "largeur" : 70, "editeur" : "heure", "infobulle" : _(u"Unité horaire de base") },
    { "code" : "duree_seuil", "label" : _(u"Durée\nseuil"), "largeur" : 70, "editeur" : "heure", "infobulle" : _(u"Durée seuil") },
    { "code" : "duree_plafond", "label" : _(u"Durée\nplafond"), "largeur" : 70, "editeur" : "heure", "infobulle" : _(u"Durée plafond") },
    { "code" : "taux", "label" : _(u"Taux"), "largeur" : 70, "editeur" : "decimal6", "infobulle" : _(u"Taux d'effort") },
    { "code" : "ajustement", "label" : _(u"Majoration/\nDéduction"), "largeur" : 75, "editeur" : "decimal4", "infobulle" : _(u"Montant à majorer ou à déduire sur le tarif") },
]

CHAMPS_TABLE_LIGNES = [
    "IDligne", "IDactivite", "IDtarif", "code", "num_ligne", "tranche", "qf_min", "qf_max", "montant_unique", "montant_questionnaire",
    "montant_enfant_1", "montant_enfant_2", "montant_enfant_3", "montant_enfant_4", "montant_enfant_5", "montant_enfant_6", 
    "nbre_enfants", "coefficient", "montant_min", "montant_max", "heure_debut_min", "heure_debut_max", "heure_fin_min", "heure_fin_max", "duree_min", "duree_max",
    "date", "label", "temps_facture", "unite_horaire", "duree_seuil", "duree_plafond", "taux", "ajustement",
    ]

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

COULEUR_FOND_CASE = (241, 241, 241)


def DateFrEnDateDD(dateFr):
    if dateFr == None or dateFr == "" or dateFr == "  /  /    " : 
        return None
    return datetime.date(int(dateFr[6:10]), int(dateFr[3:5]), int(dateFr[:2]))

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class EditeurHeure(gridlib.PyGridCellEditor):
    def __init__(self):
        gridlib.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        self._tc = CTRL_Saisie_heure.Heure(parent)
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

##    def PaintBackground(self, rect, attr):
##        pass

    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()
        # For this example, select the text
        self._tc.SetSelection(0, self._tc.GetLastPosition())

##    def EndEdit(self, row, col, grid, oldVal):
##        changed = False
##        val = self._tc.GetHeure()
##        if self._tc.Validation() == False :
##            val = None
##        if val == None : val = ""
##        if val != self.startValue and val != None :
##            changed = True
##            grid.GetTable().SetValue(row, col, val) # update the table
##        self.startValue = ''
##        self._tc.SetValue('')
##        return changed

    def EndEdit(self, row, col, grid, oldVal):
        changed = False
        val = self._tc.GetHeure()
        if self._tc.Validation() == False :
            val = None
        if val != oldVal:  
            return val
        else:
            return None
    
    def ApplyEdit(self, row, col, grid):
        val = self._tc.GetHeure()
        grid.GetTable().SetValue(row, col, val) 
        self.startValue = ''
        self._tc.SetValue('')
    
    def Reset(self):
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()

    def Destroy(self):
        super(EditeurHeure, self).Destroy()

    def Clone(self):
        return EditeurHeure()

# -------------------------------------------------------------------------------------------------------------------------------------

class EditeurDate(gridlib.PyGridCellEditor):
    def __init__(self):
        gridlib.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        self._tc = CTRL_Saisie_date.Date(parent)
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

##    def PaintBackground(self, rect, attr):
##        pass

    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetDate(self.startValue)
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()
        # For this example, select the text
        self._tc.SetSelection(0, self._tc.GetLastPosition())

##    def EndEdit(self, row, col, grid):
##        changed = False
##        val = self._tc.GetDate(FR=True)
##        if val != self.startValue and val != None :
##            changed = True
##            grid.GetTable().SetValue(row, col, val) # update the table
##        self.startValue = ''
##        self._tc.SetValue('')
##        return changed

    def EndEdit(self, row, col, grid, oldVal):
        changed = False
        val = self._tc.GetDate(FR=True)
        if val != oldVal: 
            return val
        else:
            return None
    
    def ApplyEdit(self, row, col, grid):
        val = self._tc.GetDate(FR=True)
        grid.GetTable().SetValue(row, col, val) 
        self.startValue = ''
        self._tc.SetValue('')

    def Reset(self):
        self._tc.SetDate(self.startValue)
        self._tc.SetInsertionPointEnd()

    def Destroy(self):
        super(EditeurDate, self).Destroy()

    def Clone(self):
        return EditeurDate()


# -------------------------------------------------------------------------------------------------------------------------------------

class EditeurChoix(gridlib.PyGridCellEditor):
    def __init__(self, listeValeurs=[]):
        """ listeValeurs = [(ID, label), (ID, label), ...] """
        self.listeID = []
        self.listeLabels = []
        for ID, label in listeValeurs :
            self.listeID.append(ID)
            self.listeLabels.append(label)
        gridlib.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        self._tc = wx.Choice(parent, -1, choices=self.listeLabels)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def BeginEdit(self, row, col, grid):
        try :
            id = int(grid.GetTable().GetValue(row, col))
            index = 0
            for idTemp in self.listeID :
                if id == idTemp :
                    self._tc.SetSelection(index)
                index += 1
        except :
            pass

    def EndEdit(self, row, col, grid, oldVal):
        changed = False
        val = self._tc.GetSelection() 
        if val != oldVal: 
            return val
        else:
            return None
    
    def ApplyEdit(self, row, col, grid):
        index = self._tc.GetSelection() 
        id = self.listeID[index]
        grid.GetTable().SetValue(row, col, str(id))

    def Reset(self):
        self._tc.SetSelection(0)

    def Destroy(self):
        super(EditeurDate, self).Destroy()

    def Clone(self):
        return EditeurChoix()


class RendererChoix(gridlib.PyGridCellRenderer):
    def __init__(self, listeValeurs=[]):
        self.listeValeurs = listeValeurs
        gridlib.PyGridCellRenderer.__init__(self)
    
    def GetTexte(self, grid, row, col):
        texte = ""
        try :
            id = int(grid.GetCellValue(row, col))
            idx = 0
            for idTemp, label in self.listeValeurs :
                if id == idTemp :
                    texte = label
                idx += 1
        except :
            pass
        return texte
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        texte = self.GetTexte(grid, row, col) 
        
        # Dessin
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(COULEUR_FOND_CASE, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        largeurTexte, hauteurTexte = dc.GetTextExtent(texte)
        y = rect.height / 2.0 - hauteurTexte / 2.0
        
        # Ajuste largeur texte
        if largeurTexte > rect.width :
            for index in range(len(texte), 0, -1) :
                texteTemp = texte[:index]
                largeurTexte, h = dc.GetTextExtent(texteTemp)
                if largeurTexte < rect.width - 1 :
                    texte = texteTemp
                    break
        
        dc.DrawText(texte, rect.x+2, y)
    
    def GetBestSize(self, grid, attr, dc, row, col):
        texte = self.GetTexte(grid, row, col) 
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(texte)
        return wx.Size(w, h)
    
    def Clone(self):
        return RendererChoix() 
        
# -------------------------------------------------------------------------------------------------------------------------------------


class Tableau(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.moveTo = None
        self.parent = parent
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(40)
        
        self.SetLabelBackgroundColour((255, 255, 255))
        
        self.caseSurvolee = None
        self.dictInfobulles = {}
        self.code = None
        self.entete = None
        self.champs = []
        self.champs_obligatoires = []
        self.listeColonnes = []
        self.dictDonnees = {}
        self.listeInitialeID = []

        # Pour avoir les montants avec un point au lieu d'une virgule
        li = wx.Locale.FindLanguageInfo('en_US')
        self.__locale = wx.Locale(li.Language)
##        import locale
##        locale.setlocale(locale.LC_ALL, 'C')
        
        # Importation des questions des questionnaires
        self.listeQuestions = self.GetQuestionnaires() 
        
        # Binds
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseOver)
        
    def MAJ(self, code=None, entete=None, champs=[], champs_obligatoires=[]):
        self.code = code
        self.entete = entete
        self.champs = champs
        self.champs_obligatoires = champs_obligatoires
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitGrid()
        self.Remplissage()
        self.Refresh()
        
    def InitGrid(self):        
        """ Création des colonnes """
        nbreColonnes = len(self.champs)
        self.AppendCols(nbreColonnes)
        numColonne = 0
        self.listeColonnes = []
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER) 
        for codeChamp in self.champs :
            dictColonne, index = self.RechercherChamp(codeChamp)
            self.SetColLabelValue(numColonne, dictColonne["label"])
            self.SetColSize(numColonne, dictColonne["largeur"])
            self.listeColonnes.append(index)
            self.dictInfobulles[numColonne] = dictColonne["infobulle"]
            numColonne += 1
    
    def GetQuestionnaires(self):
        """ Recherche les questions des questionnaires """
        Questionnaires = UTILS_Questionnaires.Questionnaires() 
        listeQuestions = []
        for dictQuestion in Questionnaires.GetQuestions(None) :
            listeQuestions.append(dictQuestion)
        return listeQuestions
        
    def RechercherChamp(self, codeChamp):
        index = 0
        for dictColonne in LISTE_COLONNES :
            if dictColonne["code"] == codeChamp :
                return dictColonne, index
            index += 1
        
    def Remplissage(self):
        if self.dictDonnees.has_key(self.code) : 
            # Création des lignes
            dictLignes = self.dictDonnees[self.code]
            for numLigne in dictLignes.keys() :
                self.CreationLigne()
                # Remplissage des lignes
                dictColonnes = self.dictDonnees[self.code][numLigne]
                for numColonne in dictColonnes.keys() :
                    if numColonne != "IDligne" :
                        valeur = dictColonnes[numColonne]
                        valeur = unicode(valeur)
                        self.SetCellValue(numLigne, numColonne, valeur)

        else:
            self.CreationLigne()
        
    def CreationLigne(self):
        """ Création d'une ligne """
        numLigne = self.GetNumberRows()-1
##        if numLigne > 24 :
##            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez saisir qu'un maximum de 26 lignes !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
        # Création de la ligne
        self.AppendRows(1)
        numLigne += 1
        self.SetRowLabelValue(numLigne, str(numLigne+1)) #self.SetRowLabelValue(numLigne, ALPHABET[numLigne])
        self.SetRowSize(numLigne, 20)
        # Mémorisation de la ligne
        if self.dictDonnees.has_key(self.code) == False : 
            self.dictDonnees[self.code] = {}
        if self.dictDonnees[self.code].has_key(numLigne) == False : 
            self.dictDonnees[self.code][numLigne] = {}
        # Configuration des cases
        numColonne = 0
        for indexColonne in self.listeColonnes :
            codeEditeur = LISTE_COLONNES[indexColonne]["editeur"]
            if codeEditeur == "decimal" :
                renderer = gridlib.GridCellFloatRenderer(6, 2)
                editor = gridlib.GridCellFloatEditor(6, 2)
            elif codeEditeur == "decimal3" :
                renderer = gridlib.GridCellFloatRenderer(6, 3)
                editor = gridlib.GridCellFloatEditor(6, 3)
            elif codeEditeur == "decimal4" :
                renderer = gridlib.GridCellFloatRenderer(6, 4)
                editor = gridlib.GridCellFloatEditor(6, 4)
            elif codeEditeur == "decimal6" :
                renderer = gridlib.GridCellFloatRenderer(6, 6)
                editor = gridlib.GridCellFloatEditor(6, 6)
            elif codeEditeur == "entier" :
                renderer = gridlib.GridCellNumberRenderer()
                editor = gridlib.GridCellNumberEditor(0, 100)
            elif codeEditeur == "heure" :
                renderer = None
                editor = EditeurHeure()
            elif codeEditeur == "date" :
                renderer = None
                editor = EditeurDate()
            elif codeEditeur == "questionnaire" :
                listeChoix = [(0, ""),]
                for dictQuestion in self.listeQuestions :
                    if dictQuestion["controle"] in ("montant", "decimal") :
                        label = dictQuestion["label"] + " (%s)" % dictQuestion["type"].capitalize()
                        listeChoix.append((dictQuestion["IDquestion"], label))
                renderer = RendererChoix(listeChoix)
                editor = EditeurChoix(listeChoix)
            else:
                renderer = None
                editor = None
            if renderer != None : self.SetCellRenderer(numLigne, numColonne, renderer)
            if editor != None : self.SetCellEditor(numLigne, numColonne, editor)
            
            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_FOND_CASE)
            
            numColonne += 1
    
    def SuppressionLigne(self):
        numLigne = self.GetNumberRows() -1
        # Confirmation de suppression si données existantes
        if self.dictDonnees.has_key(self.code)  : 
            if self.dictDonnees[self.code].has_key(numLigne) : 
                if len(self.dictDonnees[self.code][numLigne])> 0 :
                    dlg = wx.MessageDialog(self, _(u"Cette ligne comporte des valeurs. Souhaitez-vous vraiment la supprimer ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                    if dlg.ShowModal() != wx.ID_YES :
                        dlg.Destroy()
                        return
                    else:
                        dlg.Destroy()
        self.DeleteRows(numLigne, numLigne)
        # Suppression de la ligne du dictionnaire de données
        if self.dictDonnees.has_key(self.code)  : 
            if self.dictDonnees[self.code].has_key(numLigne) : 
                del self.dictDonnees[self.code][numLigne]
                    
    def OnCellChange(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        self.MemoriseValeur(numLigne, numColonne)
        
    def MemoriseValeur(self, numLigne, numColonne, valeur=False, IDligne=None):
        if valeur == False :
            valeur = self.GetCellValue(numLigne, numColonne)
        if self.dictDonnees.has_key(self.code) == False : 
            self.dictDonnees[self.code] = {}
        if self.dictDonnees[self.code].has_key(numLigne) == False : 
            self.dictDonnees[self.code][numLigne] = {}
        if self.dictDonnees[self.code][numLigne].has_key(numColonne) == False : 
            self.dictDonnees[self.code][numLigne][numColonne] = None
        # Formatage de la valeur
        editeur = None
        for methode in LISTE_METHODES :
            if methode["code"] == self.code :
                champs = methode["champs"]
                codeColonne =  champs[numColonne]
                for colonne in LISTE_COLONNES :
                    if colonne["code"] == codeColonne :
                        editeur = colonne["editeur"]
                        
##        print (codeColonne, numLigne, numColonne, valeur, editeur)
        
        if "," in valeur :
            valeur = valeur.replace(",", ".")
        if editeur != None :
            if editeur.startswith("decimal") and valeur != "" : valeur = float(valeur) 
            if editeur == "entier" and valeur != "" : valeur = int(valeur) 
            if editeur == "questionnaire" and valeur != "" : valeur = int(valeur) 
 
       # Mémorisation
        if IDligne != None : self.dictDonnees[self.code][numLigne]["IDligne"] = IDligne
        if valeur == None or valeur == "" :
            del self.dictDonnees[self.code][numLigne][numColonne]
        else:
            self.dictDonnees[self.code][numLigne][numColonne] = valeur
        
        return valeur

    def Importation(self, IDtarif=None):
        if IDtarif == None : return
        db = GestionDB.DB()
        champsTable = ", ".join(CHAMPS_TABLE_LIGNES)
        req = """SELECT %s
        FROM tarifs_lignes
        WHERE IDtarif=%d
        ORDER BY num_ligne;""" % (champsTable, IDtarif)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        # Sélection de la méthode
        code = listeDonnees[0][3]
        index = 0
        for dictMethode in LISTE_METHODES :
            if dictMethode["code"] == code :
                self.parent.ctrl_methode.SetSelection(index)
                self.parent.OnChoiceMethode(None)
                champs = dictMethode["champs"]
            index += 1
        # Création des lignes du tableau
        for index in range(1, len(listeDonnees)) :
            self.CreationLigne()
        # Remplissage du tableau
        numLigne = 0
        self.listeInitialeID = []
        for valeurs in listeDonnees :
            dictValeurs = {}
            # Récupération des valeurs de la base
            self.listeInitialeID.append(valeurs[0])
            indexValeur = 0
            for valeur in valeurs :
                if valeur == "None" : valeur = None
                dictValeurs[CHAMPS_TABLE_LIGNES[indexValeur]] = valeur
                indexValeur += 1
            # Remplissage de la ligne
            numColonne = 0
            for codeChamp in champs :
                valeur = dictValeurs[codeChamp]
                if type(valeur) == int or type(valeur) == float :
                    valeur = str(valeur)
                if valeur == "None" : valeur = ""
                if codeChamp == "date" and valeur != None :
                    valeur = DateEngFr(valeur)
                if valeur == None : valeur = ""
                self.SetCellValue(numLigne, numColonne, valeur)
                self.MemoriseValeur(numLigne, numColonne, valeur=valeur, IDligne=dictValeurs["IDligne"])
                numColonne += 1
            numLigne += 1
    
    def Validation(self):
        """ Vérification des donnéees """
        if self.dictDonnees.has_key(self.code) == False : 
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une méthode de calcul !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        for numLigne, dictColonnes in self.dictDonnees[self.code].iteritems() :
            numColonne = 0
            for indexChamp in self.listeColonnes :
                codeChamp = LISTE_COLONNES[indexChamp]["code"]
                label = LISTE_COLONNES[indexChamp]["label"]
                if codeChamp in self.champs_obligatoires :
                    # Vérifie la valeur
                    if dictColonnes.has_key(numColonne) == False :
                        dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la colonne '%s' de la ligne %d !") % (label, numLigne+1), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False
                    else:
                        valeur = dictColonnes[numColonne]
                        # ICI, PEUT-ETRE PROGRAMMER UNE VERIF DE LA VALEUR PLUS PRECISE...
                numColonne += 1
                
        return True
            
            
            
    def Sauvegarde(self):
        # Recherche des noms de champ du code
        for dictMethode in LISTE_METHODES :
            if dictMethode["code"] == self.code :
                champs = dictMethode["champs"]
        # Attribution des champs aux valeurs
        DB = GestionDB.DB()
        listeFinaleID = []
        if self.dictDonnees.has_key(self.code) == False : return False
        for numLigne, dictColonnes in self.dictDonnees[self.code].iteritems() :
            dictValeurs = {
                "IDactivite" : self.parent.IDactivite,
                "IDtarif" : self.parent.IDtarif,
                "code" : self.code,
                "num_ligne" : numLigne,
                "tranche" : str(numLigne+1),
                }
            numColonne = 0
            for indexChamp in self.listeColonnes :
                codeChamp = LISTE_COLONNES[indexChamp]["code"]
                if dictColonnes.has_key(numColonne) :
                    valeur = dictColonnes[numColonne]
                else:
                    valeur = None
                if valeur == "" : valeur = None
                if codeChamp == "date" and valeur != None :
                    valeur = DateFrEnDateDD(valeur)
                #print numLigne, numColonne, codeChamp, valeur
                dictValeurs[codeChamp] = valeur
                numColonne += 1
            
            # Création de la liste de champs pour la sauvegarde
            listeDonnees = []
            for codeChamp in CHAMPS_TABLE_LIGNES[1:] :
                if codeChamp in dictValeurs.keys() :
                    valeur = dictValeurs[codeChamp]
                else:
                    valeur = None
                champ = (codeChamp, valeur)
                listeDonnees.append(champ)
            
            # Sauvegarde
            if dictColonnes.has_key("IDligne") :
                IDligne = dictColonnes["IDligne"]
                listeFinaleID.append(IDligne)
            else:
                IDligne = None
            
            if IDligne == None :
                # Nouvelle ligne
                
                # Ci-dessous pour parer bug de Last_row_id de Sqlite
                if DB.isNetwork == False :
                    req = """SELECT max(IDligne) FROM tarifs_lignes;"""
                    DB.ExecuterReq(req)
                    listeTemp = DB.ResultatReq()
                    if listeTemp[0][0] == None : 
                        newID = 1
                    else:
                        newID = listeTemp[0][0] + 1
                    listeDonnees.append(("IDligne", newID))
                    DB.ReqInsert("tarifs_lignes", listeDonnees)
                else:
                    # Version MySQL
                    newID = DB.ReqInsert("tarifs_lignes", listeDonnees)
            else:
                # Modification
                DB.ReqMAJ("tarifs_lignes", listeDonnees, "IDligne", IDligne)
        
        # Suppressions
        for IDligne in self.listeInitialeID :
            if IDligne not in listeFinaleID :
                DB.ReqDEL("tarifs_lignes", "IDligne", IDligne)
                
        DB.Close() 

    def OnMouseOver(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        if numLigne != -1 and numColonne != -1 : 
            case = (numLigne, numColonne)
            if case != self.caseSurvolee :
                # Attribue une info-bulle
                texteInfobulle = self.dictInfobulles[numColonne]
                self.GetGridWindow().SetToolTip(wx.ToolTip(texteInfobulle))
                tooltip = self.GetGridWindow().GetToolTip()
                tooltip.SetDelay(1500)
                self.caseSurvolee = case
        else:
            self.caseSurvolee = None
            self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        event.Skip()


# -----------------------------------------------------------------------------------------------------------------------------


class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        
        self.nbre_lignes_max = None

        self.label_methode = wx.StaticText(self, -1, _(u"Méthode :"))
        listeLabels = []
        for dictValeurs in LISTE_METHODES :
            listeLabels.append(dictValeurs["label"])
        self.ctrl_methode = wx.Choice(self, -1, choices=listeLabels)
        self.label_parametres = wx.StaticText(self, -1, _(u"Paramètres :"))
        self.ctrl_parametres = Tableau(self)
        
        self.bouton_ajouter_ligne = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter_ligne.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_ligne = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer_ligne.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoiceMethode, self.ctrl_methode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter_ligne)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer_ligne)
        
        self.ctrl_parametres.Importation(IDtarif)

    def __set_properties(self):
        self.ctrl_methode.SetToolTipString(_(u"Sélectionnez une méthode de calcul dans la liste"))
        self.bouton_ajouter_ligne.SetToolTipString(_(u"Cliquez ici pour ajouter une ligne dans le tableau"))
        self.bouton_supprimer_ligne.SetToolTipString(_(u"Cliquez ici pour supprimer la dernière ligne du tableau"))
        self.ctrl_parametres.SetMinSize((100, 50))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        
        grid_sizer_contenu.Add(self.label_methode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_methode, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_parametres, 0, wx.ALIGN_RIGHT, 0)
        
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_parametres = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
##        grid_sizer_boutons_parametres.Add((10, 26), 0, 0, 0)
        grid_sizer_boutons_parametres.Add(self.bouton_ajouter_ligne, 0, 0, 0)
        grid_sizer_boutons_parametres.Add(self.bouton_supprimer_ligne, 0, 0, 0)
        grid_sizer_parametres.Add(grid_sizer_boutons_parametres, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_parametres, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(1)

        sizer_base.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 10)
        
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
    
    def Validation(self):
        return self.ctrl_parametres.Validation()
    
    def Sauvegarde(self):
        self.ctrl_parametres.Sauvegarde()
        
    def OnChoiceMethode(self, event): 
        indexSelection = self.ctrl_methode.GetSelection()
        code = LISTE_METHODES[indexSelection]["code"]
        entete = LISTE_METHODES[indexSelection]["entete"]
        champs = LISTE_METHODES[indexSelection]["champs"]
        champs_obligatoires = LISTE_METHODES[indexSelection]["champs_obligatoires"]
        self.nbre_lignes_max = LISTE_METHODES[indexSelection]["nbre_lignes_max"]
        self.ctrl_parametres.MAJ(code, entete, champs, champs_obligatoires)
    
    def GetCodeMethode(self):
        indexSelection = self.ctrl_methode.GetSelection()
        if indexSelection == -1 : return None
        code = LISTE_METHODES[indexSelection]["code"]
        return code
        
    def OnBoutonAjouter(self, event): 
        if self.ctrl_methode.GetSelection() == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une méthode de calcul !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.nbre_lignes_max != None :
            if self.nbre_lignes_max <= self.ctrl_parametres.GetNumberRows() :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas saisir d'autres lignes !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        self.ctrl_parametres.CreationLigne() 


    def OnBoutonSupprimer(self, event): 
        if self.ctrl_methode.GetSelection() == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une méthode de calcul !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.ctrl_parametres.SuppressionLigne() 
        








class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=9, IDtarif=29)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()