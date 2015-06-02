#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.combo
import datetime

import GestionDB

import CTRL_Saisie_date
import CTRL_Saisie_heure
import DLG_Saisie_adresse
import UTILS_Jours_speciaux

from DATA_Tables import DB_DATA as DICT_TABLES


DICT_CONTROLES = {

    "generalites" : [
        {"code" : "compagnie_bus", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='bus')" },
        {"code" : "compagnie_car", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='car')" },
        {"code" : "compagnie_navette", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='navette')" },
        {"code" : "compagnie_taxi", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='taxi')" },
        {"code" : "compagnie_train", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='train')" },
        {"code" : "compagnie_avion", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='avion')" },
        {"code" : "compagnie_bateau", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='bateau')" },
        {"code" : "compagnie_metro", "label" : _(u"Compagnie"), "ctrl" : "CTRL_Compagnies(self, categorie='metro')" },
        
        {"code" : "ligne_bus", "label" : _(u"Ligne"), "ctrl" : "CTRL_Lignes(self, categorie='bus')" },
        {"code" : "ligne_car", "label" : _(u"Ligne"), "ctrl" : "CTRL_Lignes(self, categorie='car')" },
        {"code" : "ligne_navette", "label" : _(u"Ligne"), "ctrl" : "CTRL_Lignes(self, categorie='navette')" },
        {"code" : "ligne_bateau", "label" : _(u"Ligne"), "ctrl" : "CTRL_Lignes(self, categorie='bateau')" },
        {"code" : "ligne_metro", "label" : _(u"Ligne"), "ctrl" : "CTRL_Lignes(self, categorie='metro')" },
        {"code" : "ligne_pedibus", "label" : _(u"Ligne"), "ctrl" : "CTRL_Lignes(self, categorie='pedibus')" },
        
        {"code" : "numero_avion", "label" : _(u"N° de vol"), "ctrl" : "CTRL_Numero(self, categorie='avion')" },
        {"code" : "numero_train", "label" : _(u"N° de train"), "ctrl" : "CTRL_Numero(self, categorie='train')" },
        {"code" : "details", "label" : _(u"Détails"), "ctrl" : "CTRL_Details(self)" },
        {"code" : "observations", "label" : _(u"Observ."), "ctrl" : "CTRL_Observations(self)" },
        ],
        
    "depart" : [
        {"code" : "date_heure", "label" : _(u"Heure"), "ctrl" : "CTRL_DateHeure(self)" },
        
        {"code" : "arret_bus", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='bus')" },
        {"code" : "arret_car", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='car')" },
        {"code" : "arret_navette", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='navette')" },
        {"code" : "arret_bateau", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='bateau')" },
        {"code" : "arret_metro", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='metro')" },
        {"code" : "arret_pedibus", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='pedibus')" },
        
        {"code" : "gare", "label" : _(u"Gare"), "ctrl" : "CTRL_Lieux(self, categorie='gare')" },
        {"code" : "aeroport", "label" : _(u"Aéroport"), "ctrl" : "CTRL_Lieux(self, categorie='aeroport')" },
        {"code" : "port", "label" : _(u"Port"), "ctrl" : "CTRL_Lieux(self, categorie='port')" },
        #{"code" : "station", "label" : _(u"Station"), "ctrl" : "CTRL_Lieux(self, categorie='station')" },
        
        {"code" : "localisation", "label" : _(u"Localisation"), "ctrl" : "CTRL_Localisation(self)" },
        ],

    "arrivee" : [
        {"code" : "date_heure", "label" : _(u"Heure"), "ctrl" : "CTRL_DateHeure(self)" },
        
        {"code" : "arret_bus", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='bus')" },
        {"code" : "arret_car", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='car')" },
        {"code" : "arret_navette", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='navette')" },
        {"code" : "arret_bateau", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='bateau')" },
        {"code" : "arret_metro", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='metro')" },
        {"code" : "arret_pedibus", "label" : _(u"Arrêt"), "ctrl" : "CTRL_Arrets(self, categorie='pedibus')" },
        
        {"code" : "gare", "label" : _(u"Gare"), "ctrl" : "CTRL_Lieux(self, categorie='gare')" },
        {"code" : "aeroport", "label" : _(u"Aéroport"), "ctrl" : "CTRL_Lieux(self, categorie='aeroport')" },
        {"code" : "port", "label" : _(u"Port"), "ctrl" : "CTRL_Lieux(self, categorie='port')" },
        #{"code" : "station", "label" : _(u"Station"), "ctrl" : "CTRL_Lieux(self, categorie='station')" },
        
        {"code" : "localisation", "label" : _(u"Localisation"), "ctrl" : "CTRL_Localisation(self)" },
        ],
        
    }


DICT_CATEGORIES = {

    "marche" : {   "label" : _(u"Marche"), "image" : "Marche", "type" : "localisations", "controles" : {
                                    "generalites" : ["observations",],
                                    "depart" : ["date_heure", "localisation",],
                                    "arrivee" : ["date_heure", "localisation",],
                                    },},

    "velo" : {   "label" : _(u"Vélo"), "image" : "Velo", "type" : "localisations", "controles" : {
                                    "generalites" : ["observations",],
                                    "depart" : ["date_heure", "localisation",],
                                    "arrivee" : ["date_heure", "localisation",],
                                    },},

    "voiture" : {   "label" : _(u"Voiture"), "image" : "Voiture", "type" : "localisations", "controles" : {
                                    "generalites" : ["observations",],
                                    "depart" : ["date_heure", "localisation",],
                                    "arrivee" : ["date_heure", "localisation",],
                                    },},

    "bus" : {       "label" : _(u"Bus"), "image" : "Bus", "type" : "lignes", "controles" : {
                                    "generalites" : [ "compagnie_bus", "ligne_bus", "observations"],
                                    "depart" : [ "date_heure", "arret_bus"],
                                    "arrivee" : [ "date_heure", "arret_bus"],
                                    },},

    "car" : {       "label" : _(u"Car"), "image" : "Car", "type" : "lignes", "controles" : {
                                    "generalites" : [ "compagnie_car", "ligne_car", "observations"],
                                    "depart" : [ "date_heure", "arret_car"],
                                    "arrivee" : [ "date_heure", "arret_car"],
                                    },},

    "navette" : {       "label" : _(u"Navette"), "image" : "Navette", "type" : "lignes", "controles" : {
                                    "generalites" : [ "compagnie_navette", "ligne_navette", "observations"],
                                    "depart" : [ "date_heure", "arret_navette"],
                                    "arrivee" : [ "date_heure", "arret_navette"],
                                    },},

    "taxi" : {          "label" : _(u"Taxi"), "image" : "Taxi", "type" : "localisations", "controles" : {
                                    "generalites" : [ "compagnie_taxi", "observations"],
                                    "depart" : [ "date_heure", "localisation"],
                                    "arrivee" : [ "date_heure", "localisation"],
                                    },},

    "avion" : {      "label" : _(u"Avion"), "image" : "Avion", "type" : "lieux", "controles" : {
                                    "generalites" : [ "compagnie_avion", "numero_avion", "details", "observations"],
                                    "depart" : [ "date_heure", "aeroport"],
                                    "arrivee" : [ "date_heure", "aeroport"],
                                    },},

    "bateau" : {      "label" : _(u"Bateau"), "image" : "Bateau", "type" : "lieux", "controles" : {
                                    "generalites" : [ "compagnie_bateau", "details", "observations"],
                                    "depart" : [ "date_heure", "port"],
                                    "arrivee" : [ "date_heure", "port"],
                                    },},

    "train" : {      "label" : _(u"Train"), "image" : "Train", "type" : "lieux", "controles" : {
                                    "generalites" : [ "compagnie_train", "numero_train", "details", "observations"],
                                    "depart" : [ "date_heure", "gare"],
                                    "arrivee" : [ "date_heure", "gare"],
                                    },},

    "metro" : {      "label" : _(u"Métro"), "image" : "Metro", "type" : "lignes", "controles" : {
                                    "generalites" : [ "compagnie_metro", "ligne_metro", "observations"],
                                    "depart" : [ "date_heure", "arret_metro"],
                                    "arrivee" : [ "date_heure", "arret_metro"],
                                    },},

    "pedibus" : {      "label" : _(u"Pédibus"), "image" : "Pedibus", "type" : "lignes", "controles" : {
                                    "generalites" : [ "ligne_pedibus", "observations"],
                                    "depart" : [ "date_heure", "arret_pedibus"],
                                    "arrivee" : [ "date_heure", "arret_pedibus"],
                                    },},

    }



def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class CTRL_Choix_arrets(wx.Choice):
    def __init__(self, parent, categorie="bus", IDligne=0):
        wx.Choice.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
        self.categorie = categorie
        self.IDligne = IDligne
        self.MAJ() 
        self.Select(0)
        self.SetToolTipString(_(u"Sélectionnez ici un arrêt"))
    
    def MAJ(self, IDligne=0):
        if IDligne == None : IDligne = 0
        self.IDligne = IDligne
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDarret, nom
        FROM transports_arrets
        WHERE IDligne=%d
        ORDER BY ordre; """ % self.IDligne
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDarret, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDarret, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]


class CTRL_Arrets(wx.Panel):
    """ Contrôle Choix des arrêts """
    def __init__(self, parent, categorie="bus"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie
        
        self.ctrl_arrets = CTRL_Choix_arrets(self, categorie=categorie)
        self.bouton_gestion = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGestion, self.bouton_gestion)
        self.bouton_gestion.SetToolTipString(_(u"Cliquez ici pour accéder au paramétrage des arrêts"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_arrets, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_gestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnBoutonGestion(self, event): 
        import DLG_Arrets
        dlg = DLG_Arrets.Dialog(self, categorie=self.categorie)
        dlg.ShowModal() 
        dlg.Destroy()
        # MAJ contrôles
        for controle in self.parent.GetControles("arret_%s" % self.categorie) :
            controle.MAJ() 
        for controle in self.parent.GetControles("ligne_%s" % self.categorie) :
            controle.MAJ() 

    def MAJ(self, IDligne=False):
        IDarret = self.ctrl_arrets.GetID()
        if IDligne == False :
            IDligne = self.ctrl_arrets.IDligne
        self.ctrl_arrets.MAJ(IDligne)
        self.ctrl_arrets.SetID(IDarret)
        
    def SetArret(self, IDarret=None):
        self.ctrl_arrets.SetID(IDarret)
        
    def GetArret(self):
        return self.ctrl_arrets.GetID()

    def Validation(self):
        return True
    
    def GetData(self):
        key = "%s_IDarret" % self.rubrique
        valeur = self.GetArret() 
        return {key : valeur}
    
    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "%s_IDarret" % self.rubrique :
                self.SetArret(valeur)

#------------------------------------------------------------------------------------------------------


class CTRL_Choix_lignes(wx.Choice):
    def __init__(self, parent, categorie="bus"):
        wx.Choice.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
        self.categorie = categorie
        self.MAJ() 
        self.Select(0)
        self.SetToolTipString(_(u"Sélectionnez ici une ligne"))
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDligne, nom
        FROM transports_lignes
        WHERE categorie='%s' 
        ORDER BY nom; """ % self.categorie
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDligne, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDligne, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]


class CTRL_Lignes(wx.Panel):
    """ Contrôle Choix de Lignes """
    def __init__(self, parent, categorie="bus"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie
        
        self.ctrl_lignes = CTRL_Choix_lignes(self, categorie=categorie)
        self.bouton_gestion = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_lignes)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGestion, self.bouton_gestion)
        self.bouton_gestion.SetToolTipString(_(u"Cliquez ici pour accéder au paramétrage des lignes"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_lignes, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_gestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnChoix(self, event):
        # MAJ contrôles arrêts
        for controle in self.parent.GetControles("arret_%s" % self.categorie) :
            controle.MAJ(IDligne=self.GetLigne())

    def MAJ(self):
        IDligne = self.ctrl_lignes.GetID()
        self.ctrl_lignes.MAJ()
        self.ctrl_lignes.SetID(IDligne)

    def OnBoutonGestion(self, event): 
        IDligne = self.ctrl_lignes.GetID()
        import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie=self.categorie, mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_lignes.MAJ() 
        if IDligne == None : IDligne = 0
        self.ctrl_lignes.SetID(IDligne)
    
    def SetLigne(self, IDligne=None):
        self.ctrl_lignes.SetID(IDligne)
        
    def GetLigne(self):
        return self.ctrl_lignes.GetID()

    def Validation(self):
        return True

    def GetData(self):
        key = "IDligne"
        valeur = self.GetLigne() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "IDligne" :
                self.SetLigne(valeur)
                self.OnChoix(None)


#------------------------------------------------------------------------------------------------------


class CTRL_Localisation_domicile(wx.Panel):
    """ Contrôle Domicile pour CTRL Localisation """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        rue_resid = u""
        cp_resid = u""
        ville_resid = u""
        
        # Recherche de l'adresse de l'individu
##        DB = GestionDB.DB()
##        req = """SELECT adresse_auto, rue_resid, cp_resid, ville_resid FROM individus WHERE IDindividu=%d;""" % IDindividu
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        if len(listeDonnees) > 0  :
##            adresse_auto, rue_resid, cp_resid, ville_resid = listeDonnees[0]
##            if adresse_auto != None :
##                req = """SELECT rue_resid, cp_resid, ville_resid FROM individus WHERE IDindividu=%d;""" % adresse_auto
##                DB.ExecuterReq(req)
##                listeDonnees = DB.ResultatReq()
##                if len(listeDonnees) > 0  :
##                    rue_resid, cp_resid, ville_resid = listeDonnees[0]
##        DB.Close()
##        
##        if rue_resid == None : rue_resid = u""
##        if cp_resid == None : cp_resid = u""
##        if ville_resid == None : ville_resid = u""
##
##        # Affichage
##        texte = u"%s\n%s %s" % (rue_resid, cp_resid, ville_resid)
##        self.label_heure = wx.StaticText(self, -1, texte)
    
    def GetLocalisation(self):
        return "DOMI"
    
    def SetLocalisation(self, valeur=""):
        pass
        
    def Validation(self):
        return True


class CTRL_Choix_activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
        self.Select(0)
        self.SetToolTipString(_(u"Sélectionnez ici une activité"))
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY date_fin DESC;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : u""}
        index = 1
        for IDactivite, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDactivite, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]



class CTRL_Localisation_activite(wx.Panel):
    """ Contrôle Activité pour CTRL Localisation """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = CTRL_Choix_activite(self)
        
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_activite, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_activite, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def GetLocalisation(self):
        IDactivite = self.ctrl_activite.GetID()
        if IDactivite == None : 
            IDactivite = 0
        return "ACTI;%d" % IDactivite
    
    def SetLocalisation(self, valeur=""):
        code, IDactivite = valeur.split(";")
        self.ctrl_activite.SetID(int(IDactivite))

    def Validation(self):
        if self.ctrl_activite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetFocus()
            return False
        return True




class CTRL_Choix_ecole(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
        self.Select(0)
        self.SetToolTipString(_(u"Sélectionnez ici une école"))
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDecole, nom
        FROM ecoles
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : u""}
        index = 1
        for IDecole, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDecole, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]



class CTRL_Localisation_ecole(wx.Panel):
    """ Contrôle Ecole pour CTRL Localisation """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.label_ecole = wx.StaticText(self, -1, _(u"Ecole :"))
        self.ctrl_ecole = CTRL_Choix_ecole(self)
        
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_ecole, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_ecole, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def GetLocalisation(self):
        IDecole = self.ctrl_ecole.GetID()
        if IDecole == None : 
            IDecole = 0
        return "ECOL;%d" % IDecole
    
    def SetLocalisation(self, valeur=""):
        code, IDecole = valeur.split(";")
        self.ctrl_ecole.SetID(int(IDecole))

    def Validation(self):
        if self.ctrl_ecole.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune école !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetFocus()
            return False
        return True



class CTRL_Localisation_autre(wx.Panel):
    """ Contrôle Autre pour CTRL Localisation """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.nom = u""
        self.rue = u""
        self.cp = u""
        self.ville = u""
        
        self.label_adresse = wx.StaticText(self, -1, _(u"Adresse :"))
        self.ctrl_adresse = wx.TextCtrl(self, -1, u"", style=wx.TE_READONLY)
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour saisir ou modifier l'adresse"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_adresse, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_adresse, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_modifier, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def SetAdresse(self, nom="", rue="", cp="", ville=""):
        self.nom = nom
        self.rue = rue
        self.cp = cp
        self.ville = ville
        if self.nom == None : self.nom = u""
        if self.rue == None : self.rue = u""
        if self.cp == None : self.cp = u""
        if self.ville == None : self.ville = u""
        texte = u"%s %s %s %s" % (self.nom, self.rue, self.cp, self.ville)
        self.ctrl_adresse.SetValue(texte)
    
    def OnBoutonModifier(self, event):
        dlg = DLG_Saisie_adresse.Dialog(self)
        dlg.SetNom(self.nom)
        dlg.SetRue(self.rue) 
        dlg.SetCp(self.cp) 
        dlg.SetVille(self.ville) 
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            rue = dlg.GetRue() 
            cp = dlg.GetCp()
            ville = dlg.GetVille()
            self.SetAdresse(nom, rue, cp, ville) 
        dlg.Destroy()
        
    def GetLocalisation(self):
        return "AUTR;%s;%s;%s;%s" % (self.nom, self.rue, self.cp, self.ville)
    
    def SetLocalisation(self, valeur=""):
        code, nom, rue, cp, ville = valeur.split(";")
        self.SetAdresse(nom, rue, cp, ville)

    def Validation(self):
        return True


class CTRL_Localisation(wx.Choicebook):
    """ Contrôle Localisation """
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent, id=-1)
        self.parent = parent
        self.SetToolTipString(_(u"Sélectionnez ici une localisation"))
        
        self.listePanels = [
            ("DOMI", _(u"Domicile de l'individu"), CTRL_Localisation_domicile(self) ),
            ("ACTI", _(u"Une activité"), CTRL_Localisation_activite(self) ),
            ("ECOL", _(u"Une école"), CTRL_Localisation_ecole(self) ),
            #("CONT", _(u"Contact du carnet d'adresses"), wx.Panel(self, -1) ),
            ("AUTR", _(u"Autre"), CTRL_Localisation_autre(self) ),
            ]
        
        for code, label, ctrl in self.listePanels :
            self.AddPage(ctrl, label)
            
        # Sélection par défaut
        self.SetSelection(3)
    
    def GetLocalisation(self):
        ctrl = self.listePanels[self.GetSelection()][2]
        return ctrl.GetLocalisation()

    def SetLocalisation(self, valeur=""):
        if valeur == None : valeur = u""
        codePage = valeur.split(";")[0]
        index = 0
        for code, label, ctrl in self.listePanels :
            if code == codePage :
                ctrl.SetLocalisation(valeur)
                self.SetSelection(index)
            index += 1

    def Validation(self):
        ctrl = self.listePanels[self.GetSelection()][2]
        return ctrl.Validation()

    def GetData(self):
        key = "%s_localisation" % self.rubrique
        valeur = self.GetLocalisation() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "%s_localisation" % self.rubrique :
                self.SetLocalisation(valeur)
        
#------------------------------------------------------------------------------------------------------

class CTRL_DateHeure(wx.Panel):
    """ Contrôle Date et Heure """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.ctrl_heure = CTRL_Saisie_heure.Heure(self)
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_heure, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add( (5, 5), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.label_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def AffichageDate(self, etat=True):
        """ Affiche ou non le contrôle Date """
        self.label_date.Show(etat)
        self.ctrl_date.Show(etat)
        
    def OnChoixDate(self):
        if self.GetDate() != None and self.rubrique == "depart" :
            ctrl = self.parent.GetControle(code="date_heure", rubrique="arrivee")
            if ctrl.GetDate() == None :
                ctrl.SetDate(self.GetDate())
    
    def SetDateTime(self, datedt=None):
        """ Remplit les contrôles à partir d'un datetime date + heure """
        self.SetDate(datetime.date(datedt.year, datedt.month, datedt.day))
        self.SetHeure("%02d:%02d" % (datedt.hour, datedt.minute))
        
    def SetDate(self, date=None):
        self.ctrl_date.SetDate(date)
        
    def GetDate(self):
        return self.ctrl_date.GetDate()

    def SetHeure(self, heure=None):
        self.ctrl_heure.SetHeure(heure)
        
    def GetHeure(self):
        return self.ctrl_heure.GetHeure()

    def Validation(self):
        if self.rubrique == "depart" : nomTemp = _(u"de départ")
        if self.rubrique == "arrivee" : nomTemp = _(u"d'arrivée")

        if self.GetDate() == None  and self.ctrl_date.IsShown() :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date %s !") % nomTemp, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False
        
        if self.GetDate() != None and self.ctrl_date.Validation() == False and self.ctrl_date.IsEnabled():
            dlg = wx.MessageDialog(self, _(u"Veuillez vérifier la cohérence de la date %s !") % nomTemp, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False
        
        if self.GetHeure() != None and self.ctrl_heure.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Veuillez vérifier la cohérence de l'heure %s !") % nomTemp, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure.SetFocus()
            return False
        return True

    def GetData(self):
        keyDate = "%s_date" % self.rubrique
        valeurDate = self.GetDate() 
        keyHeure = "%s_heure" % self.rubrique
        valeurHeure = self.GetHeure() 
        return {keyDate : valeurDate, keyHeure : valeurHeure}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "%s_date" % self.rubrique :
                self.SetDate(valeur)
            if key == "%s_heure" % self.rubrique :
                self.SetHeure(valeur)

#------------------------------------------------------------------------------------------------------

class CTRL_Details(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
        self.SetToolTipString(_(u"Saisissez ici les détails concernant ce transport (Ex : numéro de place, classe, etc...)"))
    
    def SetDetails(self, details=""):
        if details == None : details = ""
        self.SetValue(details)
    
    def GetDetails(self):
        details = self.GetValue()
        return details
    
    def Validation(self):
        return True

    def GetData(self):
        key = "details"
        valeur = self.GetDetails() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "details" :
                self.SetDetails(valeur)

#------------------------------------------------------------------------------------------------------

class CTRL_Observations(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, size=(170, -1), style=wx.TE_MULTILINE) 
        self.parent = parent
        self.SetToolTipString(_(u"Saisissez ici des observations"))
    
    def SetObservations(self, observations=""):
        if observations == None : observations = ""
        self.SetValue(observations)
    
    def GetObservations(self):
        observations = self.GetValue()
        return observations
    
    def Validation(self):
        return True

    def GetData(self):
        key = "observations"
        valeur = self.GetObservations() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "observations" :
                self.SetObservations(valeur)

#------------------------------------------------------------------------------------------------------

class CTRL_Numero(wx.TextCtrl):
    def __init__(self, parent, categorie="avion"):
        wx.TextCtrl.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
        if categorie == "avion" : self.SetToolTipString(_(u"Saisissez ici le numéro du vol"))
        if categorie == "train" : self.SetToolTipString(_(u"Saisissez ici le numéro du train"))
    
    def SetNumero(self, numero=""):
        if numero == None : numero = ""
        self.SetValue(numero)
    
    def GetNumero(self):
        numero = self.GetValue()
        return numero

    def Validation(self):
        return True

    def GetData(self):
        key = "numero"
        valeur = self.GetNumero() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "numero" :
                self.SetNumero(valeur)

#------------------------------------------------------------------------------------------------------

class CTRL_Choix_compagnies(wx.Choice):
    def __init__(self, parent, categorie="car"):
        wx.Choice.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
        self.categorie = categorie
        self.MAJ() 
        self.Select(0)
        self.SetToolTipString(_(u"Sélectionnez ici une compagnie"))
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDcompagnie, nom, rue, cp, ville, tel, fax, mail
        FROM transports_compagnies
        WHERE categorie='%s' 
        ORDER BY nom; """ % self.categorie
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDcompagnie, nom, rue, cp, ville, tel, fax, mail in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompagnie, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]


class CTRL_Compagnies(wx.Panel):
    """ Contrôle Choix de compagnies """
    def __init__(self, parent, categorie="car"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie
        
        self.ctrl_compagnies = CTRL_Choix_compagnies(self, categorie=categorie)
        self.bouton_gestion = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGestion, self.bouton_gestion)
        self.bouton_gestion.SetToolTipString(_(u"Cliquez ici pour accéder au paramétrage des compagnies"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_compagnies, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_gestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def MAJ(self):
        self.ctrl_compagnies.MAJ(self.ctrl_compagnies.IDcompagnie)

    def OnBoutonGestion(self, event): 
        IDcompagnie = self.ctrl_compagnies.GetID()
        import DLG_Compagnies
        dlg = DLG_Compagnies.Dialog(self, categorie=self.categorie, mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_compagnies.MAJ() 
        if IDcompagnie == None : IDcompagnie = 0
        self.ctrl_compagnies.SetID(IDcompagnie)
    
    def SetCompagnie(self, IDcompagnie=None):
        self.ctrl_compagnies.SetID(IDcompagnie)
        
    def GetCompagnie(self):
        return self.ctrl_compagnies.GetID()

    def Validation(self):
        return True

    def GetData(self):
        key = "IDcompagnie"
        valeur = self.GetCompagnie() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "IDcompagnie" :
                self.SetCompagnie(valeur)


#------------------------------------------------------------------------------------------------------

class CTRL_Choix_lieux(wx.Choice):
    def __init__(self, parent, categorie="gare"):
        wx.Choice.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
        self.categorie = categorie
        self.MAJ() 
        self.Select(0)
        self.SetToolTipString(_(u"Sélectionnez ici un lieu"))
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDlieu, nom, cp, ville
        FROM transports_lieux
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDlieu, nom, cp, ville in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDlieu, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]


class CTRL_Lieux(wx.Panel):
    """ Contrôle Choix de lieux """
    def __init__(self, parent, categorie="gare"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie
        
        self.ctrl_lieux = CTRL_Choix_lieux(self, categorie=categorie)
        self.bouton_gestion = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGestion, self.bouton_gestion)
        self.bouton_gestion.SetToolTipString(_(u"Cliquez ici pour accéder au paramétrages des lieux"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_lieux, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_gestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def MAJ(self):
        self.ctrl_lieux.MAJ(self.ctrl_lieux.IDlieu)

    def OnBoutonGestion(self, event): 
        import DLG_Lieux
        dlg = DLG_Lieux.Dialog(self, categorie=self.categorie, mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()
        # MAJ contrôles
        for controle in self.parent.GetControles(self.categorie) :
            controle.MAJ() 
    
    def MAJ(self, IDlieu=False):
        IDlieu = self.ctrl_lieux.GetID()
        if IDlieu == False :
            IDlieu = self.ctrl_lieux.IDlieu
        self.ctrl_lieux.MAJ()
        self.ctrl_lieux.SetID(IDlieu)

    def SetLieu(self, IDlieu=None):
        self.ctrl_lieux.SetID(IDlieu)
        
    def GetLieu(self):
        return self.ctrl_lieux.GetID()

    def Validation(self):
        return True

    def GetData(self):
        key = "%s_IDlieu" % self.rubrique
        valeur = self.GetLieu() 
        return {key : valeur}

    def SetData(self, listeDonnees=[]):
        for key, valeur in listeDonnees :
            if key == "%s_IDlieu" % self.rubrique :
                self.SetLieu(valeur)


#------------------------------------------------------------------------------------------------------


class CTRL_Categorie(wx.combo.BitmapComboBox):
    def __init__(self, parent, size=(-1,  -1)):
        wx.combo.BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        self.parent = parent
        self.MAJlisteDonnees() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
        self.SetToolTipString(_(u"Sélectionnez ici un moyen de locomotion"))
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.dictDonnees = {}
        index = 0
        for label, bmp, categorie in listeItems :
            self.Append(label, bmp, categorie)
            self.dictDonnees[index] = { "categorie" : categorie }
            index += 1
            
    def GetListeDonnees(self):
        listeItems = []
        for categorie, dictValeurs in DICT_CATEGORIES.iteritems() :
            label = dictValeurs["label"]
            bmp = wx.Bitmap("Images/32x32/%s.png" % dictValeurs["image"], wx.BITMAP_TYPE_ANY)
            listeItems.append((label, bmp, categorie))
        listeItems.sort()
        return listeItems

    def SetCategorie(self, categorie="bus"):
        for index, values in self.dictDonnees.iteritems():
            if values["categorie"] == categorie :
                self.SetSelection(index)

    def GetCategorie(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["categorie"]


# -----------------------------------------------------------------------------------------------------------------------



class CTRL(wx.Panel):
    def __init__(self, parent, IDtransport=None, IDindividu=None, dictDonnees={}, verrouilleBoutons=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDtransport = IDtransport
        self.IDindividu = IDindividu
        self.dictDonnees = dictDonnees
        self.categorie = "avion"
        self.listeDonneesSauvegardees = []
        
        self.grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        self.listeSizers = []
        self.listeControles = []
        
        # Ctrl Choix Catégorie
        self.ctrl_categorie = CTRL_Categorie(self)
        self.ctrl_categorie.SetCategorie(self.categorie)
        self.grid_sizer_base.Add(self.ctrl_categorie, 0, wx.EXPAND|wx.BOTTOM, 10)
        self.Bind(wx.EVT_COMBOBOX, self.OnChoixCategorie, self.ctrl_categorie)
        
        # Généralités
        self.CreationControles(rubrique="generalites", label=_(u"Généralités"))

        # Départ
        self.CreationControles(rubrique="depart", label=_(u"Départ"))
        
        # Arrivée
        self.CreationControles(rubrique="arrivee", label=_(u"Arrivée"))
        
        # Verouillage boutons de gestion
        if verrouilleBoutons == True :
            self.VerrouilleBoutonsGestion() 

        # Finalisation Layout
        self.grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(self.grid_sizer_base)
        self.grid_sizer_base.Fit(self)
        
        self.OnChoixCategorie(None)
        
        # Importation
        if len(self.dictDonnees) > 0 :
            self.ImportationVirtuelle() 
        else :
            if self.IDtransport != None :
                self.Importation() 


    def CreationControles(self, rubrique="generalites", label=_(u"Généralités")):
        box = wx.StaticBox(self, -1, label)
        boxSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(rows=18, cols=2, vgap=10, hgap=10)
        
        for dictControle in DICT_CONTROLES[rubrique] :
            code = dictControle["code"]
            
            # Label
            label = dictControle["label"]
            ctrl_label = wx.StaticText(self, -1, u"%s :" % label)
            grid_sizer.Add(ctrl_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
            
            # contrôle
            nomControle = dictControle["ctrl"]
            exec("ctrl = %s" % nomControle)
            ctrl.SetName(code)
            ctrl.rubrique = rubrique
            grid_sizer.Add(ctrl, 0, wx.EXPAND, 0)
            
            # Mémorisation des 2 contrôles
            self.listeControles.append((code, ctrl, ctrl_label))

        grid_sizer.AddGrowableCol(1)
        boxSizer.Add(grid_sizer, 1, wx.ALL|wx.EXPAND, 10)
        self.grid_sizer_base.Add(boxSizer, 1, wx.EXPAND, 0)
        
        self.listeSizers.append(boxSizer)
        self.listeSizers.append(grid_sizer)

    def OnChoixCategorie(self, event): 
        self.categorie = self.ctrl_categorie.GetCategorie()
        self.MAJaffichage()
    
    def SelectCategorie(self, categorie="avion"):
        self.categorie = categorie
        self.ctrl_categorie.SetCategorie(self.categorie)
        self.OnChoixCategorie(None)
        
    def MAJaffichage(self):
        """ Affiche ou non les contrôles de la catégorie """
        # recherche des contrôles à afficher
        self.Freeze()
        for codeControle, ctrl, ctrl_label in self.listeControles :
            resultat = self.RechercheControle(codeControle, self.categorie)
            ctrl.Show(resultat)  
            ctrl_label.Show(resultat)  
        # Ajustement des sizers
        for sizer in self.listeSizers :
            sizer.Layout()
        self.Layout()
        self.Refresh()
        self.Thaw() 

    def RechercheControle(self, codeControle="", categorie="bus"):
        """ Recherche si un contrôle donnéé est utilisé par la catégorie donnée """
        for rubrique in ("generalites", "depart", "arrivee") :
            listeControlesCategorie = DICT_CATEGORIES[self.categorie]["controles"][rubrique]
            if codeControle in listeControlesCategorie :
                return True
        return False

    def GetControles(self, texteNom="", controleActuel=None):
        """ Retrouve les contrôles du panel dont le nom comporte le texte texteNom """
        listeControlesTrouves = []
        for children in self.GetChildren():
            if texteNom in children.GetName() and children != controleActuel : 
                listeControlesTrouves.append(children)
        return listeControlesTrouves
    
    def GetControle(self, code="date_heure", rubrique="depart"):
        """ Recherche un contrôle particulier d'après son code """
        for codeControle, ctrl, ctrl_label in self.listeControles :
            if codeControle == code and ctrl.rubrique == rubrique :
                return ctrl
        return None

    def AffichageDates(self, etat=True):
        # Départ
        self.GetControle("date_heure", rubrique="depart").AffichageDate(etat) 
        # Arrivée
        self.GetControle("date_heure", rubrique="arrivee").AffichageDate(etat) 

    def Validation(self):
        """ Validation des données """
        # Recherche les contrôles actifs
        for codeControle, ctrl, ctrl_label in self.listeControles :
            resultat = self.RechercheControle(codeControle, self.categorie)
            if resultat == True :
                if ctrl.Validation() == False :
                    print "ca coince sur le contrôle", codeControle, ctrl.rubrique
                    return False
        return True
    
    def GetDictDonnees(self):
        """ Retourne un dict avec toutes les données """
        # Création d'un dict de données vierges d'après la table de champs
        dictDonnees = {}
        for nom, type, info in DICT_TABLES["transports"] :
            if nom not in ("IDtransport", "IDindividu"):
                dictDonnees[nom] = None
        
        # Récupère la valeur des contrôles
        for codeControle, ctrl, ctrl_label in self.listeControles :
            resultat = self.RechercheControle(codeControle, self.categorie)
            if resultat == True :
                dictData = ctrl.GetData()
                for key, data in dictData.iteritems() :
                    dictDonnees[key] = data
        
        # Ajout de la catégorie
        dictDonnees["categorie"] = self.categorie
        
        # Ajout du IDindividu
        dictDonnees["IDindividu"] = self.IDindividu
        
        return dictDonnees
        
    def Sauvegarde(self, mode="unique", parametres=None):
        """ Sauvegarde des données """
        self.listeDonneesSauvegardees = []
        DB = GestionDB.DB()
        
        # Récupère les données
        dictDonnees = self.GetDictDonnees() 
        
        # ----------------------------------------- SAISIE UNIQUE ----------------------------------------
        if mode == "unique" :
            dictDonnees["mode"] = "TRANSP"
            
            # Conversion en liste
            listeDonnees = []
            for key, valeur in dictDonnees.iteritems() :
                listeDonnees.append((key, valeur))
                
            # Sauvegarde
            if self.IDtransport == None :
                self.IDtransport = DB.ReqInsert("transports", listeDonnees)
            else:
                DB.ReqMAJ("transports", listeDonnees, "IDtransport", self.IDtransport)
        
        # ------------------------------------------- SAISIE MULTIPLE -------------------------------------
        if mode == "multiple" :
            dictDonnees["mode"] = "TRANSP"
            type = parametres["mode"]

            # Récupération des jours fériés et de vacances
            joursSpeciaux = UTILS_Jours_speciaux.JoursSpeciaux() 

            if type == "CALENDRIER" :
                date_min = min(parametres["dates"])
                date_max = max(parametres["dates"])
            
            if type == "PLANNING" :
                date_min = parametres["date_debut"]
                date_max = parametres["date_fin"]
            
            # Récupération des jours de présence sur l'activité donnée
            if parametres["activite"] != None :
                req = """SELECT IDconso, date, IDunite
                FROM consommations 
                WHERE IDindividu=%d AND date>='%s' and date <='%s';""" % (self.IDindividu, date_min, date_max)
                DB.ExecuterReq(req)
                listeValeurs = DB.ResultatReq()
                listeDatesPresences = []
                for IDconso, date, IDunite in listeValeurs :
                    date = DateEngEnDateDD(date)
                    if date not in listeDatesPresences :
                        listeDatesPresences.append(date)
            
            # Création de la liste de jours initiale
            if type == "CALENDRIER" :
                liste_dates = parametres["dates"]
                
            if type == "PLANNING" :
                liste_dates = [date_min,]
                date = date_min
                for x in range((date_max - date_min).days) :
                    date = date + datetime.timedelta(days=1) 
                    liste_dates.append(date)
                
            # Recherche des dates de création
            liste_problemes = []
            liste_dates_retenues = []
            
            for date in liste_dates :
                valide = True
                
                # Spécifique au mode Planning
                if type == "PLANNING" :
                    
                    # Vérifie que ce jour de la semaine est bien demandé par l'utilisateur
                    if joursSpeciaux.RechercheJourVacances(date) == True :
                        if date.weekday() not in parametres["jours_vacances"] :
                            print date.weekday(), parametres["jours_vacances"]
                            valide = False
                    else :
                        if date.weekday() not in parametres["jours_scolaires"] :
                            valide = False
                    
                # Fériés
                if parametres["feries"] == False :
                    if joursSpeciaux.RechercheJourFerie(date) == True :
                        liste_problemes.append((date, _(u"Jour férié")))
                        valide = False
                
                # Jour de présence
                if parametres["activite"] != None :
                    if date not in listeDatesPresences :
                        liste_problemes.append((date, _(u"Non inscrit à l'activité spécifiée")))
                        valide = False
                
                if valide == True :
                    liste_dates_retenues.append(date)
            
            if len(liste_dates_retenues) == 0 :
                dlg = wx.MessageDialog(self, _(u"Désolé mais il n'y a aucune date valide avec les paramètres que vous avez spécifié !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Demande de confirmation des dates
            if len(liste_dates_retenues) > 1 :
                label = _(u"dates")
            else :
                label = _(u"date")
            dlg = wx.MessageDialog(self, _(u"Confirmez-vous la saisie de ce transport sur %d %s ?") % (len(liste_dates_retenues), label), _(u"Demande de confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False
            
            # Sauvegarde
            for date in liste_dates_retenues :
                dictDonnees["depart_date"] = date
                dictDonnees["arrivee_date"] = date
            
                # Conversion en liste
                listeDonnees = []
                for key, valeur in dictDonnees.iteritems() :
                    listeDonnees.append((key, valeur))
                    
                # Sauvegarde
                IDtransport = DB.ReqInsert("transports", listeDonnees)
                
                # Mémorisation pour scheduler
                dictTemp = dictDonnees.copy() 
                dictTemp["IDtransport"] = IDtransport
                self.listeDonneesSauvegardees.append(dictTemp)
        
        # ------------------------------------------- SAISIE PROGRAMMATION -------------------------------------
        if mode == "prog" :
            dictDonnees["mode"] = "PROG"
            
            # Insertion des paramètres de la programmation
            dictDonnees["date_debut"] = parametres["date_debut"]
            dictDonnees["date_fin"] = parametres["date_fin"]
            dictDonnees["actif"] = parametres["actif"]
            dictDonnees["jours_scolaires"] = parametres["jours_scolaires"]
            dictDonnees["jours_vacances"] = parametres["jours_vacances"]
            dictDonnees["unites"] = parametres["unites"]
            
            # Conversion en liste
            listeDonnees = []
            for key, valeur in dictDonnees.iteritems() :
                listeDonnees.append((key, valeur))
                
            # Sauvegarde
            if self.IDtransport == None :
                self.IDtransport = DB.ReqInsert("transports", listeDonnees)
            else:
                DB.ReqMAJ("transports", listeDonnees, "IDtransport", self.IDtransport)
            
        DB.Close()
        return True
    
    def GetIDtransport(self):
        return self.IDtransport 
    
    def Importation(self):
        """ Importation des données """
        # Récupère les noms de champs de la table
        listeChamps = []
        for nom, type, info in DICT_TABLES["transports"] :
            listeChamps.append(nom)
        
        # Importation
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM transports 
        WHERE IDtransport=%d;""" % (", ".join(listeChamps), self.IDtransport)
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        DB.Close()
        if len(listeValeurs) == 0 : return
        listeDonnees = []
        index = 0
        for valeur in listeValeurs[0] :
            listeDonnees.append((listeChamps[index], valeur))
            index += 1
        
        # Remplit les champs
        self.RemplitChamps(listeDonnees)
    
    def RemplitChamps(self, listeDonnees=[]):
        # Sélectionne la catégorie
        for key, valeur in listeDonnees :
            if key == "categorie" :
                self.SelectCategorie(valeur)
        
        # Importe les valeurs dans les contrôles
        for codeControle, ctrl, ctrl_label in self.listeControles :
            ctrl.SetData(listeDonnees)
    
    def ImportationVirtuelle(self):
        listeDonnees = []
        for key, valeur in self.dictDonnees.iteritems() :
            listeDonnees.append((key, valeur))
        self.RemplitChamps(listeDonnees)
    
    def VerrouilleBoutonsGestion(self):
        """ Verrouille tous les boutons de gestion """
        for ctrl in self.GetChildren():
            if hasattr(ctrl, 'bouton_gestion'):
                ctrl.bouton_gestion.Show(False)
        
        

#------------------------------------------------------------------------------------------------------


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, IDtransport=1, IDindividu=46)
        self.ctrl.VerrouilleBoutonsGestion() 
        bouton_test = wx.Button(panel, -1, _(u"TEST"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, bouton_test)
    
    def OnBoutonTest(self, event):
        self.ctrl.Importation()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(450, 580))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()