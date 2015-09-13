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

import CTRL_Saisie_date
import CTRL_Saisie_euros

import GestionDB
import UTILS_Historique
import UTILS_Identification


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class Choix_type(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.indexDefaut = None
        self.MAJ() 
    
    def MAJ(self):
        listeDonnees = self.GetListeDonnees()
        if len(listeDonnees) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeDonnees)
        if self.indexDefaut != None :
            self.Select(self.indexDefaut)
    
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        DB = GestionDB.DB()
        conditionType = ""
##        if self.parent.IDfamille != None : conditionType = "famille"
##        if self.parent.IDindividu != None : conditionType = "individu"
        req = """
        SELECT IDtype_cotisation, nom, type, carte, defaut
        FROM types_cotisations
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 0
        for IDtype_cotisation, nom, type, carte, defaut in listeDonnees :
            self.dictDonnees[index] = { 
                "ID" : IDtype_cotisation,
                "nom" : nom,
                "type" : type,
                "carte" : carte,
                }
            listeItems.append(nom)
            if defaut == 1 :
                self.indexDefaut = index
            index += 1
        return listeItems

    def GetDetailDonnees(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
            
# -------------------------------------------------------------------------------------------------------

class Choix_unite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDtype_cotisation = None
        self.indexDefaut = None
    
    def MAJ(self, IDtype_cotisation=None):
        self.IDtype_cotisation = IDtype_cotisation
        listeDonnees = self.GetListeDonnees()
        if len(listeDonnees) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeDonnees)
        if self.indexDefaut != None :
            self.Select(self.indexDefaut)

    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        if self.IDtype_cotisation == None :
            return []
        DB = GestionDB.DB()
        req = """
        SELECT IDunite_cotisation, nom, date_debut, date_fin, montant, label_prestation, defaut
        FROM unites_cotisations
        WHERE IDtype_cotisation=%d
        ORDER BY nom;""" % self.IDtype_cotisation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 0
        for IDunite_cotisation, nom, date_debut, date_fin, montant, label_prestation, defaut in listeDonnees :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            self.dictDonnees[index] = { 
                "ID" : IDunite_cotisation, 
                "nom" : nom, 
                "date_debut" : date_debut, 
                "date_fin" : date_fin, 
                "montant" : montant, 
                "label_prestation" : label_prestation, 
                "defaut" : defaut, 
                }
            listeItems.append(nom)
            if defaut == 1 :
                self.indexDefaut = index
            index += 1
        return listeItems
    
    def GetDetailDonnees(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
            

# -------------------------------------------------------------------------------------------------------

class Choix_beneficiaire(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeDonnees = []
    
    def SetListeDonnees(self, type=""):
        self.listeNoms = []
        self.listeDonnees = []
        
        # Si c'est une cotisation individuelle :
        if type == "individu" :
            
            if self.parent.IDfamille != None :
                # Si on vient d'une fiche familiale : on affiche tous les membres de la famille
                DB = GestionDB.DB()
                req = """SELECT IDrattachement, rattachements.IDindividu, rattachements.IDfamille, IDcategorie, titulaire, nom, prenom
                FROM rattachements 
                LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
                WHERE IDfamille=%d and IDcategorie IN (1, 2)
                ORDER BY nom, prenom;""" % self.parent.IDfamille
                DB.ExecuterReq(req)
                listeTitulaires = DB.ResultatReq()
                DB.Close()
                for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom in listeTitulaires :
                    nomIndividu = u"%s %s" % (nom, prenom)
                    self.listeNoms.append(nomIndividu)
                    self.listeDonnees.append(IDindividu)
            else:
                # Si on vient d'une fiche individuelle : on affiche uniquement le nom de l'individu en cours
                DB = GestionDB.DB()
                req = """SELECT nom, prenom
                FROM individus 
                WHERE IDindividu=%d
                ;""" % self.parent.IDindividu
                DB.ExecuterReq(req)
                listeIndividus = DB.ResultatReq()
                DB.Close()
                if len(listeIndividus) == 0 : 
                    print "Erreur dans ctrl_beneficiaire : pas d'individu trouve."
                    return
                nom, prenom = listeIndividus[0]
                nomIndividu = u"%s %s" % (nom, prenom)
                self.listeNoms.append(nomIndividu)
                self.listeDonnees.append(self.parent.IDindividu)
        
        # Si c'est une cotisation familiale :
        if type == "famille" :
            
            if self.parent.IDfamille != None :
                # Si on vient d'une fiche familiale : On affiche uniquement la famille en cours
                DB = GestionDB.DB()
                req = """SELECT IDrattachement, rattachements.IDindividu, rattachements.IDfamille, IDcategorie, titulaire, nom, prenom
                FROM rattachements 
                LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
                WHERE IDfamille=%d and titulaire=1 and IDcategorie=1
                ORDER BY IDrattachement;""" % self.parent.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                DB.Close()
                listeTitulaires = []
                for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom in listeDonnees :
                    nomIndividu = u"%s %s" % (nom, prenom)
                    listeTitulaires.append(nomIndividu)
                nbreTitulaires = len(listeTitulaires)
                if nbreTitulaires == 0 : 
                    nomTitulaires = _(u"Pas de titulaires !")
                if nbreTitulaires == 1 : 
                    nomTitulaires = listeTitulaires[0]
                if nbreTitulaires == 2 : 
                    nomTitulaires = _(u"%s et %s") % (listeTitulaires[0], listeTitulaires[1])
                if nbreTitulaires > 2 :
                    nomTitulaires = ""
                    for nomTitulaire in listeTitulaires[:-1] :
                        nomTitulaires += u"%s, " % nomTitulaire
                    nomTitulaires = _(u"%s et %s") % (nomTitulaires[:-2], listeTitulaires[-1])
                self.listeNoms.append(_(u"Famille de %s") % nomTitulaires)
                self.listeDonnees.append(self.parent.IDfamille)
                
            else:
                # Si on vient d'une fiche individuelle : on affiche les familles rattachées
                IDindividu = self.parent.IDindividu
                if self.parent.dictFamillesRattachees != None :
                    for IDfamille, dictFamille in self.parent.dictFamillesRattachees.iteritems() :
                        if dictFamille["IDcategorie"] in (1, 2) :
                            nomTitulaires = dictFamille["nomsTitulaires"]
                            self.listeNoms.append(_(u"Famille de %s") % nomTitulaires)
                            self.listeDonnees.append(IDfamille)

        # Remplissage du contrôle
        self.SetItems(self.listeNoms)
        
        if len(self.listeNoms) > 0 :
            self.Select(0)

        if len(self.listeNoms) < 2 :
            self.Enable(False)
        else:
            self.Enable(True)
    
    def SetID(self, ID=None):
        index = 0
        for IDfamille in self.listeDonnees :
            if IDfamille == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]

# ------------------------------------------------------------------------------------------------------------------------------------------


class Choix_payeur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeDonnees = []
        self.SetListeDonnees() 
    
    def SetListeDonnees(self):
        self.listeNoms = []
        self.listeDonnees = []

        # Si on vient d'une fiche INDIVIDU :
        if self.parent.IDindividu != None :
                        
            for IDfamille, dictFamille in self.parent.dictFamillesRattachees.iteritems() :
                nomTitulaires = dictFamille["nomsTitulaires"]
                IDcompte_payeur = dictFamille["IDcompte_payeur"]
                self.listeNoms.append(nomTitulaires)
                self.listeDonnees.append((IDcompte_payeur, IDfamille))
        
        # Si on vient d'une fiche familiale :
        if self.parent.IDfamille != None :
            DB = GestionDB.DB()
            req = """SELECT IDrattachement, rattachements.IDindividu, rattachements.IDfamille, IDcategorie, titulaire, nom, prenom, IDcompte_payeur
            FROM rattachements 
            LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = rattachements.IDfamille
            WHERE rattachements.IDfamille=%d and titulaire=1 and IDcategorie=1
            ORDER BY IDrattachement;""" % self.parent.IDfamille
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            listeTitulaires = []
            for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom, IDcompte_payeur in listeDonnees :
                nomIndividu = u"%s %s" % (nom, prenom)
                listeTitulaires.append(nomIndividu)
            nbreTitulaires = len(listeTitulaires)
            if nbreTitulaires == 0 : 
                nomTitulaires = _(u"Pas de titulaires !")
                IDcompte_payeur = None
            if nbreTitulaires == 1 : 
                nomTitulaires = listeTitulaires[0]
            if nbreTitulaires == 2 : 
                nomTitulaires = _(u"%s et %s") % (listeTitulaires[0], listeTitulaires[1])
            if nbreTitulaires > 2 :
                nomTitulaires = ""
                for nomTitulaire in listeTitulaires[:-1] :
                    nomTitulaires += u"%s, " % nomTitulaire
                nomTitulaires = _(u"%s et %s") % (nomTitulaires[:-2], listeTitulaires[-1])
            self.listeNoms.append(nomTitulaires)
            self.listeDonnees.append((IDcompte_payeur, self.parent.IDfamille))
                
        # Remplissage du contrôle
        self.SetItems(self.listeNoms)
        
        if len(self.listeNoms) > 0 :
            self.Select(0)
        
        if len(self.listeNoms) < 2 :
            self.Enable(False)
        else:
            self.Enable(True)
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte_payeur, IDfamille in self.listeDonnees :
            if IDcompte_payeur == ID :
                 self.SetSelection(index)
            index += 1

    def GetIDcompte_payeur(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index][0]
    
    def GetIDfamille(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index][1]
        

# ------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcotisation=None, IDfamille=None, IDindividu=None, dictFamillesRattachees={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDcotisation = IDcotisation
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        # Variables pour importation
        self.IDprestation = None
        self.date_saisie = datetime.date.today() 
        self.IDutilisateur = UTILS_Identification.GetIDutilisateur()
        
        # Cotisation
        self.staticbox_cotisation_staticbox = wx.StaticBox(self, -1, _(u"Cotisation"))
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.ctrl_type = Choix_type(self)
        self.label_unite = wx.StaticText(self, -1, _(u"Unité :"))
        self.ctrl_unite = Choix_unite(self)
        self.label_beneficiaire = wx.StaticText(self, -1, _(u"Bénéfic. :"))
        self.ctrl_beneficiaire = Choix_beneficiaire(self)
        self.label_validite = wx.StaticText(self, -1, _(u"Validité :"))
        self.label_du = wx.StaticText(self, -1, u"du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        self.label_observations = wx.StaticText(self, -1, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        # Carte
        self.staticbox_carte_staticbox = wx.StaticBox(self, -1, _(u"Carte d'adhérent"))
        self.label_creation = wx.StaticText(self, -1, _(u"Création :"))
        self.ctrl_creation = wx.CheckBox(self, -1, "")
        self.label_numero = wx.StaticText(self, -1, _(u"Numéro :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, u"")
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date_creation = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_creation.SetDate(datetime.date.today())
        self.label_depot = wx.StaticText(self, -1, _(u"Dépôt :"))
        self.ctrl_depot = wx.TextCtrl(self, -1, u"")
        
        # Prestation
        self.staticbox_prestation_staticbox = wx.StaticBox(self, -1, _(u"Facturation"))
        self.label_facturer = wx.StaticText(self, -1, _(u"Facturer :"))
        self.ctrl_facturer = wx.CheckBox(self, -1, "")
        self.label_date_prestation = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date_prestation = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_prestation.SetDate(datetime.date.today())
        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.label_payeur = wx.StaticText(self, -1, _(u"Payeur :"))
        self.ctrl_payeur = Choix_payeur(self)
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixType, self.ctrl_type)
        self.Bind(wx.EVT_CHOICE, self.OnChoixUnite, self.ctrl_unite)
        self.Bind(wx.EVT_CHECKBOX, self.OnChoixCreation, self.ctrl_creation)
        self.Bind(wx.EVT_CHECKBOX, self.OnChoixFacturer, self.ctrl_facturer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDcotisation == None :
            self.SetTitle(_(u"Saisie d'une cotisation"))
            self.SetProchainIDcotisation() 
            self.OnChoixCreation(None)
            self.OnChoixFacturer(None) 
            self.OnChoixType(None)
            self.OnChoixUnite(None)
        else:
            self.SetTitle(_(u"Modification d'une cotisation"))
            self.Importation() 
        
        # Init contrôles
        self.ctrl_depot.Enable(False)
        
        self.bouton_ok.SetFocus() 
        
    def __set_properties(self):
        self.ctrl_type.SetToolTipString(_(u"Sélectionnez ici le type de cotisation"))
        self.ctrl_unite.SetToolTipString(_(u"Sélectionnez ici l'unité de cotisation"))
        self.ctrl_beneficiaire.SetToolTipString(_(u"Sélectionnez ici la famille ou l'individu qui bénéficie de cette cotisation"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez ici la date de début de validité"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici la date de fin de validité"))
        self.ctrl_observations.SetToolTipString(_(u"Saisissez un texte libre (optionnel)"))
        self.ctrl_creation.SetToolTipString(_(u"Selectionnez OUI si une carte d'adhérent a ete créee"))
        self.ctrl_numero.SetMinSize((70, -1))
        self.ctrl_numero.SetToolTipString(_(u"Saisissez ici le numéro de la carte d'adhérent"))
        self.ctrl_date_creation.SetToolTipString(_(u"Saisissez ici la date de création de la carte d'adhérent"))
        self.ctrl_depot.SetMinSize((70, -1))
        self.ctrl_depot.SetToolTipString(_(u"Numero et date du dépôt"))
        self.ctrl_facturer.SetToolTipString(_(u"Selectionnez OUI si la carte doit etre facturée"))
        self.ctrl_date_prestation.SetToolTipString(_(u"Saisissez ici la date de la prestation à facturer"))
        self.ctrl_montant.SetMinSize((70, -1))
        self.ctrl_montant.SetToolTipString(_(u"Saisissez ici le montant a facturer"))
        self.ctrl_label.SetToolTipString(_(u"Saisissez ici le label de la prestation a créer"))
        self.ctrl_payeur.SetToolTipString(_(u"Sélectionnez la famille à facturer"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((450, 437))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Cotisation
        staticbox_cotisation = wx.StaticBoxSizer(self.staticbox_cotisation_staticbox, wx.VERTICAL)
        grid_sizer_cotisation = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
        grid_sizer_validite = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_cotisation.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_cotisation.Add(self.ctrl_type, 0, wx.EXPAND, 0)
        grid_sizer_cotisation.Add(self.label_unite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_cotisation.Add(self.ctrl_unite, 0, wx.EXPAND, 0)
        grid_sizer_cotisation.Add(self.label_beneficiaire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_cotisation.Add(self.ctrl_beneficiaire, 0, wx.EXPAND, 0)
        grid_sizer_cotisation.Add(self.label_validite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.label_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_validite.Add(self.label_au, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_cotisation.Add(grid_sizer_validite, 1, wx.EXPAND, 0)
        grid_sizer_cotisation.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.TOP, 3)
        grid_sizer_cotisation.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_cotisation.AddGrowableCol(1)
        grid_sizer_cotisation.AddGrowableRow(4)
        staticbox_cotisation.Add(grid_sizer_cotisation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_cotisation, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Carte
        staticbox_carte = wx.StaticBoxSizer(self.staticbox_carte_staticbox, wx.VERTICAL)
        grid_sizer_carte = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        
        # Création
        grid_sizer_carte.Add(self.label_creation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creation = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_creation.Add(self.ctrl_creation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creation.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_creation.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creation.Add(self.ctrl_date_creation, 0, 0, 0)
        grid_sizer_creation.AddGrowableCol(3)
        grid_sizer_carte.Add(grid_sizer_creation, 1, wx.EXPAND, 0)
        
        grid_sizer_carte.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_carte.Add(self.ctrl_numero, 0, wx.EXPAND, 0)

        grid_sizer_carte.Add(self.label_depot, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_carte.Add(self.ctrl_depot, 0, wx.EXPAND, 0)
        
        grid_sizer_carte.AddGrowableCol(1)
        staticbox_carte.Add(grid_sizer_carte, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_carte, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Prestation
        staticbox_prestation = wx.StaticBoxSizer(self.staticbox_prestation_staticbox, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_facturer = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_prestation.Add(self.label_facturer, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturer.Add(self.ctrl_facturer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturer.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_facturer.Add(self.label_date_prestation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturer.Add(self.ctrl_date_prestation, 0, 0, 0)
        grid_sizer_facturer.AddGrowableCol(3)
        grid_sizer_prestation.Add(grid_sizer_facturer, 1, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_payeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_payeur, 0, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_montant, 0, wx.EXPAND, 0)
        grid_sizer_prestation.AddGrowableCol(1)
        staticbox_prestation.Add(grid_sizer_prestation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_prestation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 
    
    def SetProchainIDcotisation(self):
        # Méthode 1
##        DB = GestionDB.DB()
##        prochainID = DB.GetProchainID("cotisations")
##        DB.Close()
##        if prochainID == None : 
##            prochainID = 1
##        numero = u"%06d" % prochainID
##        self.ctrl_numero.SetValue(numero)
        # Méthode 2 :
        DB = GestionDB.DB()
        req = """SELECT MAX(numero) FROM cotisations;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            if listeDonnees[0][0] == None :
                prochainID = 1
            else:
                try :
                    prochainID = int(listeDonnees[0][0]) + 1
                except :
                    return
        else:
            prochainID = 1
        numero = u"%06d" % prochainID
        self.ctrl_numero.SetValue(numero)
        
    def OnChoixType(self, event):
        IDtype_cotisation = self.ctrl_type.GetID() 
        self.ctrl_unite.MAJ(IDtype_cotisation)
        self.OnChoixUnite(None)
        

    def OnChoixUnite(self, event): 
        # Récupère les données sur le type
        dictDonneesType = self.ctrl_type.GetDetailDonnees()
        if dictDonneesType != None :
            carte = dictDonneesType["carte"]
            nomType = dictDonneesType["nom"]
            type = dictDonneesType["type"]
            if carte == 1 : 
                self.ctrl_creation.SetValue(True)
                
        # Récupère les données sur l'unité
        dictDonneesUnite = self.ctrl_unite.GetDetailDonnees()
        if dictDonneesUnite != None :
            nomUnite = dictDonneesUnite["nom"]
            date_debut = dictDonneesUnite["date_debut"]
            date_fin = dictDonneesUnite["date_fin"]
            montant = dictDonneesUnite["montant"]
            label_prestation = dictDonneesUnite["label_prestation"]
            # Insertion des valeurs
            self.ctrl_date_debut.SetDate(date_debut)
            self.ctrl_date_fin.SetDate(date_fin)
            self.ctrl_montant.SetMontant(montant)
            if label_prestation != None :
                # Label personnalisé
                self.ctrl_label.SetValue(label_prestation)
            else:
                # Label automatique
                label = u"%s - %s" % (nomType, nomUnite)
                self.ctrl_label.SetValue(label)
            self.ctrl_facturer.SetValue(True)
        
            # MAJ ctrl bénéficiaires
            if dictDonneesType != None :
                self.ctrl_beneficiaire.SetListeDonnees(type)
            
        # MAJ contrôles
        self.OnChoixCreation(None)
        self.OnChoixFacturer(None) 

    def OnChoixCreation(self, event):
        if self.ctrl_creation.GetValue() == 1 :
            self.ctrl_numero.Enable(True)
            self.ctrl_date_creation.Enable(True)
            self.ctrl_date_creation.SetFocus() 
            wx.CallAfter(self.ctrl_date_creation.SetInsertionPoint, 0)
        else:
            self.ctrl_numero.Enable(False)
            self.ctrl_date_creation.Enable(False)

    def OnChoixFacturer(self, event): 
        if self.ctrl_facturer.GetValue() == 1 and self.ctrl_facturer.IsEnabled() == True :
            self.ctrl_date_prestation.Enable(True)
            self.ctrl_montant.Enable(True)
            self.ctrl_label.Enable(True)
            if self.ctrl_payeur.GetCount() > 1 :
                self.ctrl_payeur.Enable(True)
        else:
            self.ctrl_date_prestation.Enable(False)
            self.ctrl_montant.Enable(False)
            self.ctrl_label.Enable(False)
            self.ctrl_payeur.Enable(False)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Cotisations1")

    def OnBoutonOk(self, event): 
        # Vérification des données saisies
        
        # Type
        if self.ctrl_type.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un type de cotisation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Unité
        if self.ctrl_unite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une unité de cotisation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Validation de la date de début
        if self.ctrl_date_debut.FonctionValiderDate() == False or self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        # Validation de la date de fin
        if self.ctrl_date_fin.FonctionValiderDate() == False or self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        # Si la case CREATION est cochée
        if self.ctrl_creation.GetValue() == True :
            
            # Vérifie la date de création
            if self.ctrl_date_creation.FonctionValiderDate() == False or self.ctrl_date_creation.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de création de carte valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_creation.SetFocus()
                return False

            # Vérifie qu'un numéro de carte a été saisi
            if self.ctrl_numero.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas saisir de numéro d'adhérent ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    return False
        
        # Si la case PRESTATION est cochée
        if self.ctrl_facturer.GetValue() == True :

            # Vérifie la date de facturation
            if self.ctrl_date_prestation.FonctionValiderDate() == False or self.ctrl_date_prestation.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de facturation valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_prestation.SetFocus()
                return False

            # Vérifie le montant
            if self.ctrl_montant.GetMontant() == 0.00 :
                dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir saisir de montant ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    return False

            # Vérifie le label de prestation
            if self.ctrl_label.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un label pour la facturation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_label_prestation.SetFocus()
                return False
        
        else:
            
            # Demande la confirmation de la suppression de la prestation
            if self.IDprestation != None :
                dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la prestation qui a déjà été créée pour cette cotisation ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                if dlg.ShowModal() != wx.ID_YES :
                    return False
                dlg.Destroy()
        
        # Sauvegarde
        self.Sauvegarde()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDcotisation(self):
        return self.IDcotisation 
    
    def Sauvegarde(self):
        """ Sauvegarde """
        
        # Récupération des données
        donneesType = self.ctrl_type.GetDetailDonnees()
        if donneesType["type"] == "famille" :
            # Si c'est une cotisation famille
            IDfamille = self.ctrl_beneficiaire.GetID() 
            IDindividu = None
        else:
            # Si c'est une cotisation individuelle
            IDfamille = None
            IDindividu = self.ctrl_beneficiaire.GetID() 
        IDtype_cotisation = self.ctrl_type.GetID() 
        IDunite_cotisation = self.ctrl_unite.GetID() 
        date_saisie = self.date_saisie
        IDutilisateur = self.IDutilisateur
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        observations = self.ctrl_observations.GetValue() 
        
        # Création de la carte
        if self.ctrl_creation.GetValue() == True :
            date_creation_carte = self.ctrl_date_creation.GetDate() 
            numero = self.ctrl_numero.GetValue() 
        else:
            date_creation_carte = None
            numero = None
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("IDfamille", IDfamille),
                ("IDindividu", IDindividu),
                ("IDtype_cotisation", IDtype_cotisation),
                ("IDunite_cotisation", IDunite_cotisation),
                ("date_saisie", date_saisie),
                ("IDutilisateur", IDutilisateur),
                ("date_creation_carte", date_creation_carte),
                ("numero", numero),
                ("date_debut", date_debut),
                ("date_fin", date_fin),
                ("observations", observations),
            ]
        if self.IDcotisation == None :
            nouvelleCotisation = True
            self.IDcotisation = DB.ReqInsert("cotisations", listeDonnees)
        else:
            nouvelleCotisation = False
            DB.ReqMAJ("cotisations", listeDonnees, "IDcotisation", self.IDcotisation)
        
        # Sauvegarde de la prestation
        facturer = self.ctrl_facturer.GetValue() 
        date_facturation = self.ctrl_date_prestation.GetDate()
        montant = self.ctrl_montant.GetMontant() 
        label_prestation = self.ctrl_label.GetValue()
        IDcompte_payeur = self.ctrl_payeur.GetIDcompte_payeur()
        IDfamille_payeur = self.ctrl_payeur.GetIDfamille() 
        IDprestation = self.IDprestation
        
        if facturer == True :
            
            # Création d'une prestation
            listeDonnees = [    
                    ("IDcompte_payeur", IDcompte_payeur),
                    ("date", date_facturation),
                    ("categorie", "cotisation"),
                    ("label", label_prestation),
                    ("montant_initial", montant),
                    ("montant", montant),
                    ("IDfamille", IDfamille_payeur),
                    ("IDindividu", IDindividu),
                ]
            if IDprestation == None :
                IDprestation = DB.ReqInsert("prestations", listeDonnees)
            else:
                DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)
                
                # Recherche si cette prestation a déjà été ventilée sur un règlement
                req = """SELECT IDventilation, ventilation.montant
                FROM ventilation
                LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
                WHERE IDprestation=%d
                ORDER BY reglements.date;""" % IDprestation
                DB.ExecuterReq(req)
                listeVentilations = DB.ResultatReq()
                montantVentilation = 0.0
                for IDventilation, montantTmp in listeVentilations :
                    montantVentilation += montantTmp
                if montantVentilation > montant :
                    # Si le montant total ventilé est supérieur au montant de la prestation :
                    montantVentilationTmp = 0.0
                    for IDventilation, montantTmp in listeVentilations :
                        montantVentilationTmp += montantTmp
                        if montantVentilationTmp > montant :
                            nouveauMontant = montantTmp - (montantVentilationTmp - montant)
                            if nouveauMontant > 0.0 :
                                DB.ReqMAJ("ventilation", [("montant", nouveauMontant),], "IDventilation", IDventilation)
                                montantVentilationTmp =  (montantVentilationTmp - montantTmp) + nouveauMontant
                            else:
                                DB.ReqDEL("ventilation", "IDventilation", IDventilation)

        
        else:
            
            # Suppression d'une prestation précédemment créée
            if IDprestation != None :
                DB.ReqDEL("prestations", "IDprestation", IDprestation)
                DB.ReqDEL("ventilation", "IDprestation", IDprestation)
                IDprestation = None
        
        # Insertion du IDprestation dans la cotisation
        DB.ReqMAJ("cotisations", [("IDprestation", IDprestation),], "IDcotisation", self.IDcotisation)
        
        DB.Close()
        
        # Mémorise l'action dans l'historique
        date_debut_periode = DateEngFr(str(date_debut))
        date_fin_periode = DateEngFr(str(date_fin))
        if nouvelleCotisation == True :
            type = "Saisie"
            IDcategorie = 21
        else:
            type = "Modification"
            IDcategorie = 22
        UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : IDcategorie, 
                "action" : _(u"%s de la cotisation ID%d '%s' pour la période du %s au %s") % (type, self.IDcotisation, label_prestation, date_debut_periode, date_fin_periode),
                },])
        

    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT
        IDfamille, IDindividu, IDtype_cotisation, IDunite_cotisation,
        date_saisie, IDutilisateur, date_creation_carte, numero,
        IDdepot_cotisation, date_debut, date_fin, IDprestation, observations
        FROM cotisations 
        WHERE IDcotisation=%d;""" % self.IDcotisation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        
        IDfamille, IDindividu, IDtype_cotisation, IDunite_cotisation, date_saisie, IDutilisateur, date_creation_carte, numero, IDdepot_cotisation, date_debut, date_fin, IDprestation, observations = listeDonnees[0]
        
        self.date_saisie = date_saisie
        self.IDutilisateur = IDutilisateur
        self.IDprestation = IDprestation
        
        # Cotisation
        self.ctrl_type.SetID(IDtype_cotisation)
        self.OnChoixType(None)
        self.ctrl_unite.SetID(IDunite_cotisation)
        self.OnChoixUnite(None)
        if IDfamille != None : self.ctrl_beneficiaire.SetID(IDfamille)
        if IDindividu != None : self.ctrl_beneficiaire.SetID(IDindividu)
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        if observations != None :
            self.ctrl_observations.SetValue(observations) 
            
        # Carte
        if date_creation_carte == None :
            self.ctrl_creation.SetValue(False) 
            self.SetProchainIDcotisation() 
        else:
            self.ctrl_creation.SetValue(True) 
            self.ctrl_date_creation.SetDate(date_creation_carte)
            self.ctrl_numero.SetValue(numero)
            
        if IDdepot_cotisation == None :
            self.ctrl_depot.SetValue(_(u"Non déposée"))
        else:
            self.ctrl_depot.SetValue(_(u"Déposée sur le dépôt n°%d") % IDdepot_cotisation)
            self.ctrl_creation.Enable(False)
            self.ctrl_date_creation.Enable(False)
            self.ctrl_numero.Enable(False)
            
        # Facturation
        if IDprestation == None :
            self.ctrl_facturer.SetValue(False)
        else:
            self.ctrl_facturer.SetValue(True)
            
            # Importation des données de la prestation
            DB = GestionDB.DB()
            req = """SELECT
            IDcompte_payeur, label, montant, date, IDfacture
            FROM prestations 
            WHERE IDprestation=%d;""" % IDprestation
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            DB.Close()
            if len(listePrestations) > 0 :
                IDcompte_payeur, label, montant, date_facturation, IDfacture = listePrestations[0]
                self.ctrl_date_prestation.SetDate(date_facturation)
                self.ctrl_montant.SetMontant(montant)
                self.ctrl_label.SetLabel(label)
                self.ctrl_payeur.SetID(IDcompte_payeur)
                
                if IDfacture != None :
                    self.ctrl_facturer.Enable(False)
                
            else:
                self.IDprestation = None
                self.ctrl_facturer.SetValue(False)
        
        # Init contrôles
        self.OnChoixCreation(None)
        self.OnChoixFacturer(None) 
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcotisation=1, IDfamille=4)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
