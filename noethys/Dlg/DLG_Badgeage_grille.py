#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import datetime

from Ctrl import CTRL_Grille
from Utils import UTILS_Dates



class CTRL_Activites():
    def __init__(self, parent):
        self.parent = parent
        
    def GetIDgroupe(self, IDactivite=None, IDindividu=None):
        return None


class Panel_Activites():
    def __init__(self, parent):
        self.parent = parent
        self.ctrl_activites = CTRL_Activites(self)


class Panel_Facturation():
    def __init__(self, parent):
        pass
        
    def RAZ(self):
        pass
    
    def SaisiePrestation(self, *args, **kwds):
        pass

    def ModifiePrestation(self, *args, **kwds):
        pass
    
    
class Panel_Etiquettes():
    def __init__(self, parent):
        self.parent = parent
    
    def GetCoches(self, IDactivite=None):
        return []

    
class PanelGrille(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_grille", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.grille = CTRL_Grille.CTRL(self, "individu", IDfamille=0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grille, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
    
    def GetMode(self):
        return self.parent.mode



class CTRL_Titre(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.SetForegroundColour((255, 255, 255))
        self.SetBackgroundColour((0, 0, 0))
        
        # Labels
        self.label_individu = wx.StaticText(self, -1, u"")
        self.label_individu.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial'))
        
        self.label_information = wx.StaticText(self, -1, u"")
        self.label_information.SetFont(wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.label_individu, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.label_information, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.SetSizer(sizer)
        self.Layout()
    
    def SetNom(self, nom=u""):
        self.label_individu.SetLabel(nom)
    
    def SetInformation(self, information=u""):
        self.label_information.SetLabel(information)

# ------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.mode = "reservation"
        
        # Labels
        self.ctrl_titre = CTRL_Titre(self)
        
        # Contrôles Grille des conso
        self.panel_activites = Panel_Activites(self)
        self.panel_facturation = Panel_Facturation(self) 
        self.panel_etiquettes = Panel_Etiquettes(self) 
        self.panel_grille = PanelGrille(self)
        self.grille = self.panel_grille.grille
        
        # Layout
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.ctrl_titre, 0, wx.ALL|wx.EXPAND)
        sizer1.Add(self.panel_grille, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer1)
        self.Layout()

    def InitGrille(self, IDindividu=None, IDfamille=None, IDactivite=None, date=None, periode=None):
        """ Initialisation de la grille """
        # Initialisation de la grille
        self.grille.IDfamille = IDfamille
        self.grille.InitDonnees() 
        if periode == None :
            date_debut, date_fin = date, date
        else :
            date_debut, date_fin = periode
        self.grille.SetModeIndividu([IDactivite,], [IDindividu,], [IDindividu,], [(date_debut, date_fin),], modeSilencieux=True)
        
        # Récupération des informations
        self.dictInfosIndividu = self.grille.dictInfosIndividus[IDindividu]
        self.dictInfosInscriptions = self.grille.dictInfosInscriptions[IDindividu][IDactivite]
        
        # Ecrit le nom dans le titre
        self.ctrl_titre.SetNom(u"%s %s" % (self.dictInfosIndividu["nom"], self.dictInfosIndividu["prenom"]))

    def Sauvegarde(self):
        """ Sauvegarde de la grille """
        self.grille.Sauvegarde()
    
    def GetCase(self, IDunite=None, date=None, memo=False):
        """ Récupère une case d'après un IDunite """
        for numLigne, ligne in self.grille.dictLignes.iteritems() :
            for numColonne, case in ligne.dictCases.iteritems() :
                if case.typeCase == "consommation" :
                    if case.IDunite == IDunite and (case.date == date or date == None) :
                        return case
                if case.typeCase == "memo" :
                    if case.date == date or date == None :
                        return case
        return None
    
    def HasPlacesDisponibles(self, IDunite=None, date=None):
        case = self.GetCase(IDunite, date)
        return case.HasPlaceDisponible() 
        
    def SaisieConso(self, IDunite=None, mode="reservation", etat="reservation", heure_debut="defaut", heure_fin="defaut", date=None, quantite=None):
        """ Crée ou modifie une conso pour l'unité indiquée """
        case = self.GetCase(IDunite, date)
        if case == None :
            return _(u"Cette case est inexistante.")
        
        # Vérifie que cette unité est ouverte
        if case.ouvert == False :
            return _(u"Cette unité est fermée.")

        # Recherche Heures par défaut
        heure_debut_defaut = self.grille.dictUnites[IDunite]["heure_debut"]
        heure_fin_defaut = self.grille.dictUnites[IDunite]["heure_fin"]
        typeUnite = self.grille.dictUnites[IDunite]["type"]
        
        if heure_debut == "defaut" : heure_debut = heure_debut_defaut
        if heure_fin == "defaut" : heure_fin = heure_fin_defaut

        # Vérifie qu'il reste des places disponibles
        if case.HasPlaceDisponible(heure_debut, heure_fin) == False :
            return _(u"Il n'y a plus de place à cette date.")
        
        # Vérifie la compatibilité avec les autres unités
        incompatibilite = case.VerifieCompatibilitesUnites()
        if incompatibilite != None :
            nomUniteIncompatible = self.grille.dictUnites[incompatibilite]["nom"]
            return _(u"Action impossible car il existe déjà à cette date une réservation sur l'unité '%s'.") %  nomUniteIncompatible
            
        # Définit le mode
        self.mode = mode
                
        # Si la conso n'existe pas déjà :
        if case.IsCaseDisponible(heure_debut, heure_fin) == True :
            if typeUnite == "Quantite" :
                quantiteTmp = 1
            else :
                quantiteTmp = None
            if quantite != None :
                quantiteTmp = quantite
            if typeUnite == "Multihoraires" :
                barre = case.SaisieBarre(UTILS_Dates.HeureStrEnTime(heure_debut), UTILS_Dates.HeureStrEnTime(heure_fin))
                case.ModifieEtat(barre.conso, etat)
            else :
                case.OnClick(saisieHeureDebut=heure_debut, saisieHeureFin=heure_fin, saisieQuantite=quantiteTmp, modeSilencieux=True)
                case.ModifieEtat(None, etat)


        # Si la conso existe déjà :
        else :
            
            # Type Horaire
            if typeUnite == "Horaire" :
                case.OnClick(saisieHeureDebut=heure_debut, saisieHeureFin=heure_fin, modeSilencieux=True)
                case.ModifieEtat(None, etat)
            else :
                if heure_debut != None : case.heure_debut = heure_debut
                if heure_fin != None : case.heure_fin = heure_fin
            
            # Type Quantité
            if typeUnite == "Quantite" :
                quantiteTmp = case.quantite
                if quantite != None :
                    quantiteTmp = quantite
                else :
                    if quantiteTmp == None :
                        quantiteTmp = 1
                    quantiteTmp += 1
                case.OnClick(saisieHeureDebut=heure_debut, saisieHeureFin=heure_fin, saisieQuantite=quantiteTmp, modeSilencieux=True)
                case.ModifieEtat(None, etat)
            
            if typeUnite == "Unitaire" :
                case.ModifieEtat(None, etat)
            
        return True
    
    def SupprimeConso(self, IDunite=None, date=None):
        """ Supprime la conso d'une unité donnée """
        case = self.GetCase(IDunite, date)
        if case == None : 
            return _(u"Cette case est inexistante.")
        if case.etat == None :
            return _(u"Il n'existe aucune consommation à cette date et pour cette unité.")
        if case.IDfacture != None :
            return _(u"Interdit de supprimer une consommation déjà facturée.")
        if case.etat in ("present", "absenti", "absentj") :
            return _(u"Interdit de supprimer une consommation déjà pointée.")
        case.OnClick(modeSilencieux=True)
        return True

    def ModifieEtat(self, IDunite=None, etat="reservation", date=None):
        """ Modifie l'état de l'unité donnée """
        case = self.GetCase(IDunite, date)
        if case == None :
            return _(u"Cette case est inexistante.")
        for conso in case.GetListeConso() :
            if conso.etat == None :
                return _(u"Il n'existe aucune consommation à cette date et pour cette unité.")
            if conso.etat != etat :
                case.ModifieEtat(None, etat)
        return True
    
    def ModifieMemo(self, date=None, texte=""):
        case = self.GetCase(date=date, memo=True)
        if case == None :
            return _(u"La case mémo journalier est inexistante.")
        case.SetTexte(texte)
        return True        
    
    def RecalculerToutesPrestations(self):
        self.grille.RecalculerToutesPrestations(modeSilencieux=True) 
    
    def TraitementLot_processus(self, resultats={}):
        return self.grille.TraitementLot_processus(resultats=resultats)
        
# FONCTIONS DISPONIBLES :
# Sauvegarde() : Pour sauvegarder
# SaisieConso() : Pour ajouter une conso
# SupprimeConso() : Pour Supprimer une conso
# ModifieMemo(): Pour modifier le mémo journalier
# RecalculerToutesPrestations : Recalculer toutes les conso affichées
# TraitementLot_processus : Effectuer un traitement par lot global


class Dialog(wx.Dialog):
    def __init__(self, parent, ):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Contrôle
        self.ctrl = CTRL(self)
        
        # Boutons de test
        bouton1 = wx.Button(self, -1, _(u"TEST 1 - fam 1 - Date unique"))
        bouton2 = wx.Button(self, -1, _(u"TEST 2 - fam 2- Plusieurs dates"))
        bouton3 = wx.Button(self, -1, _(u"TEST 3 - Sauvegarde "))
        bouton4 = wx.Button(self, -1, _(u"TEST 4 - saisie conso"))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest1, bouton1)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest2, bouton2)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest3, bouton3)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest4, bouton4)
        
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.ctrl, 1, wx.ALL|wx.EXPAND)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(bouton1, 1, wx.ALL|wx.EXPAND)
        sizer2.Add(bouton2, 1, wx.ALL|wx.EXPAND)
        sizer2.Add(bouton3, 1, wx.ALL|wx.EXPAND)
        sizer2.Add(bouton4, 1, wx.ALL|wx.EXPAND)
        sizer1.Add(sizer2, 0, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer1)
        self.Layout()
        self.SetSize((1100, -1))

    def OnBoutonTest1(self, event):
        """ TEST 1 """
        self.ctrl.InitGrille(IDindividu=46, IDfamille=14, IDactivite=3, date=datetime.date(2013, 6, 19))

    def OnBoutonTest2(self, event):
        """ TEST 2 """
        self.ctrl.InitGrille(IDindividu=3, IDfamille=1, IDactivite=1, periode=(datetime.date(2013, 6, 19), datetime.date(2013, 7, 1)) )
        
    def OnBoutonTest3(self, event):
        """ TEST 3 """
        self.ctrl.Sauvegarde()
        
    def OnBoutonTest4(self, event):
        """ TEST 4 """
        # Saisie d'une journée
##        resultat = self.ctrl.SaisieConso(IDunite=1, mode="reservation", etat="present", heure_debut="17:30", heure_fin="defaut")
##        print ("Test saisie Unité 1 :", resultat)
##        resultat = self.ctrl.SaisieConso(IDunite=9, mode="reservation", etat="present", heure_debut="17:30", heure_fin="defaut")
##        print ("Test saisie Unité 9 :", resultat)
        
        # Saisie d'un repas
##        resultat = self.ctrl.SaisieConso(IDunite=2, mode="reservation", etat="present", heure_debut="12:05", heure_fin="defaut")
##        print ("Test saisie repas :", resultat)
        
        # Modification de l'état uniquement
##        resultat = self.ctrl.ModifieEtat(IDunite=2, etat="present")
##        print ("Test modifie etat sur PRESENT :", resultat)

        # Saisie d'une garderie du matin
##        resultat = self.ctrl.SaisieConso(IDunite=7, mode="reservation", etat="present", heure_debut="14:35", heure_fin="defaut")
##        print ("Test saisie Garderie du Matin :", resultat)

        # Saisie d'une journée avec repas sur une date donnée
        resultat = self.ctrl.SaisieConso(IDunite=1, mode="reservation", etat="refus", date=datetime.date(2013, 6, 20) )
        print ("Test saisie Unité 1 :", resultat)
        resultat = self.ctrl.SaisieConso(IDunite=2, mode="reservation", etat="refus", date=datetime.date(2013, 6, 20) )
        print ("Test saisie Unité 2 :", resultat)
        resultat = self.ctrl.SaisieConso(IDunite=5, mode="reservation", etat="refus", date=datetime.date(2013, 6, 21) )
        print ("Test saisie Unité 2 :", resultat)

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
