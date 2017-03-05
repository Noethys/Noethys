#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
from Ctrl import CTRL_Saisie_date
from Ol import OL_Contrats_periodes
from Ctrl import CTRL_Ultrachoice
import GestionDB
from Utils import UTILS_Dates
import copy
from Utils import UTILS_Identification
from Ol import OL_Activites
import cPickle
import wx.lib.dialogs as dialogs



def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None :
        return None
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats



class CTRL_Tarif(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent, donnees=[], IDactivite=None, IDcategorie_tarif=None):
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees) 
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDcategorie_tarif = IDcategorie_tarif
        self.listeTarifs= []
        self.MAJ() 
        if len(self.listeTarifs) > 0 :
            self.SetSelection2(0)

    def Importation(self):
        if self.IDactivite == None :
            return []

        DB = GestionDB.DB()
        
        # Recherche des catégories de tarifs
        dictCategoriesTarifs = {}
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDcategorie_tarif, nom in listeDonnees :
            dictCategoriesTarifs[IDcategorie_tarif] = nom

        # Recherche les tarifs
        dictIndividus = {}
        req = """SELECT IDtarif, tarifs.IDactivite, 
        tarifs.IDnom_tarif, noms_tarifs.nom, 
        date_debut, date_fin, methode, categories_tarifs, groupes, description
        FROM tarifs
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        WHERE type='CREDIT' AND forfait_beneficiaire='individu' AND tarifs.IDactivite=%d
        ORDER BY noms_tarifs.nom, date_debut;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeTarifs = []
        for IDtarif, IDactivite, IDnom_tarif, nomTarif, date_debut, date_fin, methode, categories_tarifs, groupes, description in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            listeCategoriesTarifs = ConvertStrToListe(categories_tarifs)
            listeNomsCategories = []
            for IDcategorie_tarif in listeCategoriesTarifs :
                nomCategorieTarif = _(u"Categorie de tarif inconnue")
                if dictCategoriesTarifs.has_key(IDcategorie_tarif) :
                    nomCategorieTarif = dictCategoriesTarifs[IDcategorie_tarif]
                listeNomsCategories.append(nomCategorieTarif)
            
            dictTemp = {
                    "IDtarif" : IDtarif, "IDactivite" : IDactivite, 
                    "IDnom_tarif" : IDnom_tarif, "nomTarif" : nomTarif, "date_debut" : date_debut,
                    "date_fin" : date_fin, "methode" : methode, "categories_tarifs":categories_tarifs, "groupes":groupes,
                    "listeNomsCategories" : listeNomsCategories, "nomPrecisTarif":description,
                    }
            
            if self.IDcategorie_tarif in listeCategoriesTarifs or self.IDcategorie_tarif == None :
                listeTarifs.append(dictTemp)
        return listeTarifs
    
    def MAJ(self):
        self.listeTarifs = self.Importation() 
        listeItems = []
        for dictTarif in self.listeTarifs :
            IDtarif = dictTarif["IDtarif"]
            nom = dictTarif["nomTarif"]
            date_debut = dictTarif["date_debut"]
            date_fin = dictTarif["date_fin"]
            if date_debut == None and date_fin == None : label = _(u"%s (Sans période de validité)") % nom
            if date_debut == None and date_fin != None : label = _(u"%s (Jusqu'au %s)") % (nom, UTILS_Dates.DateDDEnFr(date_fin))
            if date_debut != None and date_fin == None : label = _(u"%s (A partir du %s)") % (nom, UTILS_Dates.DateDDEnFr(date_debut))
            if date_debut != None and date_fin != None : label = _(u"%s (Du %s au %s)") % (nom, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin))
            
            description = dictTarif["nomPrecisTarif"] + " --- " + " ou ".join(dictTarif["listeNomsCategories"])
            listeItems.append({"label" : label, "description" : description})
        self.SetDonnees(listeItems)
    
    def SetID(self, ID=None):
        index = 0
        for dictTarif in self.listeTarifs :
            IDtarif = dictTarif["IDtarif"]
            if IDtarif == ID :
                 self.SetSelection2(index)
            index += 1

    def GetID(self):
        index = self.GetSelection2()
        if index == -1 or index == None : return None
        return self.listeTarifs[index]["IDtarif"]
    
    def GetDictTarif(self):
        index = self.GetSelection2()
        if index == -1 : return None
        return self.listeTarifs[index]

# ------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None, IDinscription=None, IDcontrat=None, IDmodele=None, mode_modele=False, IDactivite=None, copie=None, copie_conso=True):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_contrat", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDinscription = IDinscription
        self.IDcontrat = IDcontrat
        self.mode_modele = mode_modele
        self.IDmodele = IDmodele
        self.listePeriodesInitiale = []
        self.listeSuppressionConso = []
        
        # Récupération de l'activité
        if mode_modele == True :
            DB = GestionDB.DB()
            req = """SELECT IDactivite, nom
            FROM activites
            WHERE IDactivite=%d; """ % IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            self.IDactivite, self.nomActivite = listeDonnees[0]
            self.IDcompte_payeur, self.IDfamille, self.IDcategorie_tarif, self.IDgroupe, self.nomGroupe = None, None, None, None, None
        else :
            DB = GestionDB.DB()
            req = """SELECT inscriptions.IDactivite, activites.nom, inscriptions.IDcompte_payeur, inscriptions.IDfamille, inscriptions.IDcategorie_tarif, inscriptions.IDgroupe, groupes.nom
            FROM inscriptions
            LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite 
            LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
            WHERE IDinscription=%d; """ % IDinscription
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            self.IDactivite, self.nomActivite, self.IDcompte_payeur, self.IDfamille, self.IDcategorie_tarif, self.IDgroupe, self.nomGroupe = listeDonnees[0]
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        
        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom du modèle :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.label_nom.Show(self.mode_modele)
        self.ctrl_nom.Show(self.mode_modele)

        self.label_dates = wx.StaticText(self, wx.ID_ANY, _(u"Dates du contrat :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.label_observations = wx.StaticText(self, wx.ID_ANY, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)

        self.label_tarif = wx.StaticText(self, wx.ID_ANY, _(u"Tarif de base :"))
        self.ctrl_tarif = CTRL_Tarif(self, IDactivite=self.IDactivite, IDcategorie_tarif=self.IDcategorie_tarif)

        # Périodes
        self.box_periodes_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Périodes de facturation"))

        self.listviewAvecFooter = OL_Contrats_periodes.ListviewAvecFooter(self, kwargs={"IDactivite" : self.IDactivite}) 
        self.ctrl_periodes = self.listviewAvecFooter.GetListview()
        
        self.bouton_assistant = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Magique.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_ajouter_periode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_periode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_periode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_consommations = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer des consommations"), cheminImage="Images/32x32/Magique.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Assistant, self.bouton_assistant)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Ajouter, self.bouton_ajouter_periode)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Modifier, self.bouton_modifier_periode)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Supprimer, self.bouton_supprimer_periode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonConsommations, self.bouton_consommations)

        # Init contrôles
        if self.mode_modele == True :
            # Modèle de contrat
            if self.IDmodele == None :
                self.SetTitle(_(u"Saisie d'un modèle de contrat pour l'activité '%s'") % self.nomActivite)
            else :
                self.SetTitle(_(u"Modification d'un modèle de contrat pour l'activité '%s'") % self.nomActivite)
                self.Importation_modele() 
        
        else :
            # Contrat
            if self.IDcontrat == None :
                self.SetTitle(_(u"Saisie d'un contrat pour l'activité '%s'") % self.nomActivite)
                if copie != None :
                    self.Importation(IDcontrat=copie, mode_copie=True, copie_conso=copie_conso) 
                if self.IDmodele != None :
                    self.Importation_modele() 
            else :
                self.SetTitle(_(u"Modification d'un contrat pour l'activité '%s'") % self.nomActivite)
                self.Importation(IDcontrat=self.IDcontrat) 
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour ce modèle de contrat"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de contrat"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin de contrat"))
        self.ctrl_observations.SetToolTipString(_(u"Saisissez des observations sur ce contrat"))
        self.ctrl_tarif.SetToolTipString(_(u"Sélectionnez un tarif de base dans cette liste des tarifs de type 'forfait crédit' disponibles"))
        self.bouton_assistant.SetToolTipString(_(u"Cliquez ici pour générer automatiquement les périodes"))
        self.bouton_ajouter_periode.SetToolTipString(_(u"Cliquez ici pour ajouter une période"))
        self.bouton_modifier_periode.SetToolTipString(_(u"Cliquez ici pour modifier la période sélectionnée"))
        self.bouton_supprimer_periode.SetToolTipString(_(u"Cliquez ici pour supprimer la période sélectionnée"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.bouton_consommations.SetToolTipString(_(u"Cliquez ici pour générer automatiquement des consommations"))
        self.SetMinSize((800, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(4, 2, 10, 10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_dates, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates = wx.FlexGridSizer(1, 4, 5, 5)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_tarif, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_tarif, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Périodes
        box_periodes = wx.StaticBoxSizer(self.box_periodes_staticbox, wx.VERTICAL)
        grid_sizer_periodes = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_periodes.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        grid_sizer_boutons_periodes = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_boutons_periodes.Add(self.bouton_assistant, 0, 0, 0)
        grid_sizer_boutons_periodes.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_ajouter_periode, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_modifier_periode, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_supprimer_periode, 0, 0, 0)
        grid_sizer_periodes.Add(grid_sizer_boutons_periodes, 1, wx.EXPAND, 0)
        grid_sizer_periodes.AddGrowableRow(0)
        grid_sizer_periodes.AddGrowableCol(0)
        box_periodes.Add(grid_sizer_periodes, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_periodes, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_consommations, 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide(u"Contrats")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)
    
    def OnBoutonConsommations(self, event):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        listePeriodes = self.ctrl_periodes.GetDonnees() 
        import DLG_Saisie_contrat_conso
        dlg = DLG_Saisie_contrat_conso.Dialog(self, IDactivite=self.IDactivite, date_debut=date_debut, date_fin=date_fin, IDgroupe=self.IDgroupe, listePeriodes=listePeriodes)
        if dlg.ShowModal() == wx.ID_OK:
            listePeriodes = dlg.GetListePeriodes()
            self.ctrl_periodes.SetDonnees(listePeriodes)
        dlg.Destroy()
        
    def OnBoutonOk(self, event):  
        if self.Sauvegarde() == False :
            return
        self.EndModal(wx.ID_OK)
    
    def Importation_modele(self):
        DB = GestionDB.DB()
        req = """SELECT nom, IDactivite, date_debut, date_fin, observations, IDtarif, donnees
        FROM modeles_contrats 
        WHERE IDmodele=%d; """ % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        if len(listeDonnees) == 0 : return
        nom, IDactivite, date_debut, date_fin, observations, IDtarif, donnees = listeDonnees[0]
        self.ctrl_nom.SetValue(nom)
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        self.ctrl_observations.SetValue(observations)
        self.ctrl_tarif.SetID(IDtarif)
        listePeriodes = cPickle.loads(str(donnees))
        self.listePeriodesInitiale = copy.deepcopy(listePeriodes)
        self.ctrl_periodes.SetDonnees(listePeriodes)
        
    def Importation(self, IDcontrat=None, mode_copie=False, copie_conso=True):
        """ Importation des données """
        DB = GestionDB.DB()
        
        # Importation des contrats
        req = """SELECT date_debut, date_fin, observations, IDtarif
        FROM contrats 
        WHERE IDcontrat=%d; """ % IDcontrat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            DB.Close()
            return
        date_debut, date_fin, observations, IDtarif = listeDonnees[0]
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        self.ctrl_observations.SetValue(observations)
        self.ctrl_tarif.SetID(IDtarif)

        # Importation des consommations liées au contrat
        req = """SELECT IDconso, consommations.IDindividu, IDinscription, consommations.IDactivite, consommations.date, IDunite, IDgroupe, heure_debut, heure_fin, etat, verrouillage, date_saisie, IDutilisateur, quantite, consommations.IDcategorie_tarif, consommations.IDcompte_payeur, consommations.IDprestation
        FROM consommations
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation 
        WHERE prestations.IDcontrat=%d; """ % IDcontrat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictConso = {}
        for IDconso, IDindividu, IDinscription, IDactivite, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, verrouillage, date_saisie, IDutilisateur, quantite, IDcategorie_tarif, IDcompte_payeur, IDprestation in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            date_saisie = UTILS_Dates.DateEngEnDateDD(date_saisie)
            dictTemp = {
                "IDconso" : IDconso, "IDindividu" : IDindividu, "IDinscription" : IDinscription, "IDactivite" : IDactivite, "date" : date, "IDunite" : IDunite, "IDgroupe" : IDgroupe, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "quantite" : quantite,
                "etat" : etat, "verrouillage" : verrouillage, "date_saisie" : date_saisie, "IDutilisateur" : IDutilisateur, "IDcategorie_tarif" : IDcategorie_tarif, "IDcompte_payeur" : IDcompte_payeur, "IDprestation" : IDprestation, 
                }
            if dictConso.has_key(IDprestation) == False :
                dictConso[IDprestation] = []
            if mode_copie == True :
                dictTemp["IDconso"] = None
                dictTemp["etat"] = "reservation"
            dictConso[IDprestation].append(dictTemp)

        # Importation des périodes de contrat
        req = """SELECT prestations.IDprestation, forfait_date_debut, forfait_date_fin, label, montant, prestations.date,
        prestations.IDfacture, factures.IDprefixe, factures_prefixe.prefixe, factures.numero,
        COUNT(consommations.IDconso)
        FROM prestations 
        LEFT JOIN consommations ON consommations.IDprestation = prestations.IDprestation
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        WHERE IDcontrat=%d
        GROUP BY prestations.IDprestation
        ORDER BY forfait_date_debut;""" % IDcontrat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listePeriodes = []
        for IDprestation, date_debut, date_fin, label, montant, date_prestation, IDfacture, IDprefixe, prefixe, numFacture, nbreConso in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            date_prestation = UTILS_Dates.DateEngEnDateDD(date_prestation)

            if IDprefixe != None :
                numFacture = u"%s-%06d" % (prefixe, numFacture)
            else :
                numFacture = u"%06d" % numFacture

            if dictConso.has_key(IDprestation) and copie_conso == True :
                listeConso = dictConso[IDprestation]
            else :
                listeConso = []
            dictTemp = {
                "IDprestation" : IDprestation, "date_debut" : date_debut, "date_fin" : date_fin, "listeConso" : listeConso,
                "label_prestation" : label, "montant_prestation" : montant, "date_prestation" : date_prestation, "IDfacture" : IDfacture, "numFacture" : numFacture,
                }
            if mode_copie == True :
                dictTemp["IDprestation"] = None
                dictTemp["IDfacture"] = None
            listePeriodes.append(dictTemp)
        self.listePeriodesInitiale = copy.deepcopy(listePeriodes)
        self.ctrl_periodes.SetDonnees(listePeriodes)

        DB.Close()

    def GetIDcontrat(self):
        return self.IDcontrat
    
    def GetIDmodele(self):
        return self.IDmodele
    
    def Sauvegarde(self):
        """ Sauvegarde des données """
        nom = self.ctrl_nom.GetValue()
        if self.mode_modele == True and nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le nom du modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
            
        date_debut = self.ctrl_date_debut.GetDate() 
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus() 
            return False
        
        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"La date de début ne doit pas être supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        IDtarif = self.ctrl_tarif.GetID()
        if IDtarif == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un tarif dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        observations = self.ctrl_observations.GetValue() 
        IDtarif = self.ctrl_tarif.GetID() 
        
        listePeriodes = self.ctrl_periodes.GetDonnees() 
        if len(listePeriodes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir au moins une période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Vérifie que les périodes sont bien dans la période de validité du contrat
        for dictPeriode in listePeriodes :
            if dictPeriode["date_debut"] < date_debut :
                dlg = wx.MessageDialog(self, _(u"La période '%s' comporte une date de début antérieure à la date de début du contrat !") % dictPeriode["label_prestation"], _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if dictPeriode["date_fin"] > date_fin :
                dlg = wx.MessageDialog(self, _(u"La période '%s' comporte une date de fin supérieure à la date de fin du contrat !") % dictPeriode["label_prestation"], _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
        # Vérifie que les consommations sont bien enregistrables
        if self.mode_modele == False :
            if self.VerifieConsommations(listePeriodes) == False :
                return False


        # ------------- SAUVEGARDE -------------------------------------------------------------------------------------------------------------------

        if self.mode_modele == True :
            # Sauvegarde du modèle de contrat
            donneesStr = cPickle.dumps(listePeriodes)

            DB = GestionDB.DB()
            listeDonnees = [
                ("nom", nom ),
                ("IDactivite", self.IDactivite),
                ("date_debut", date_debut),
                ("date_fin", date_fin ),
                ("observations", observations),
                ("IDtarif", IDtarif),
                ]
            if self.IDmodele == None :
                self.IDmodele = DB.ReqInsert("modeles_contrats", listeDonnees)
            else :
                DB.ReqMAJ("modeles_contrats", listeDonnees, "IDmodele", self.IDmodele)
            
            # Sauvegarde des données BLOB
            DB.MAJimage(table="modeles_contrats", key="IDmodele", IDkey=self.IDmodele, blobImage=donneesStr, nomChampBlob="donnees")
            
            DB.Close() 
        
        # --------------------------------------------------------------------------------------------------------------------------------
        else :
            # Sauvegarde du contrat
            DB = GestionDB.DB()
            
            # Sauvegarde des contrats
            listeDonnees = [
                ("IDinscription", self.IDinscription ),
                ("IDindividu", self.IDindividu ),
                ("date_debut", date_debut ),
                ("date_fin", date_fin ),
                ("observations", observations),
                ("IDtarif", IDtarif),
                ]
            if self.IDcontrat == None :
                self.IDcontrat = DB.ReqInsert("contrats", listeDonnees)
            else :
                DB.ReqMAJ("contrats", listeDonnees, "IDcontrat", self.IDcontrat)
                
            # Sauvegarde des périodes du contrat
            listeID = []
            index = 0
            for dictPeriode in listePeriodes :
                IDprestation = dictPeriode["IDprestation"]
                
                # Sauvegarde de la prestation
                listeDonnees = [
                    ("IDcompte_payeur", self.IDcompte_payeur ),
                    ("date", dictPeriode["date_prestation"] ),
                    ("categorie", "consommation" ),
                    ("label", dictPeriode["label_prestation"]),
                    ("montant_initial", dictPeriode["montant_prestation"]),
                    ("montant", dictPeriode["montant_prestation"]),
                    ("IDactivite", self.IDactivite),
                    ("IDtarif", IDtarif),
                    ("IDfamille", self.IDfamille),
                    ("IDindividu", self.IDindividu),
                    ("IDcategorie_tarif", self.IDcategorie_tarif),
                    ("forfait_date_debut", dictPeriode["date_debut"]),
                    ("forfait_date_fin", dictPeriode["date_fin"]),
                    ("IDcontrat", self.IDcontrat),
                    ]
                if IDprestation == None :
                    listeDonnees.append(("date_valeur", str(datetime.date.today())))
                    IDprestation = DB.ReqInsert("prestations", listeDonnees)
                else :
                    DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)
                listeID.append(IDprestation)
                listePeriodes[index]["IDprestation"] = IDprestation
                index += 1
            
            # Suppression des périodes supprimées
            for dictPeriode in self.listePeriodesInitiale :
                if dictPeriode["IDprestation"] not in listeID and dictPeriode["IDprestation"] != None :
                    DB.ReqDEL("prestations", "IDprestation", dictPeriode["IDprestation"])
                    DB.ReqMAJ("consommations", [("IDprestation", None),], "IDprestation", dictPeriode["IDprestation"])

            # Suppression des conso supprimées
            for IDconso in self.listeSuppressionConso :
                if IDconso != None :
                    DB.ReqDEL("consommations", "IDconso", IDconso)

            # Saisie des consommations générées
            listeAjouts = []
            for dictPeriode in listePeriodes :
                listeConso = dictPeriode["listeConso"]
                for dictConso in listeConso :
                    if dictConso["IDconso"] == None :
                        dictConsoTemp = {
                            "IDindividu" : self.IDindividu,
                            "IDinscription" : self.IDinscription,
                            "IDactivite" : self.IDactivite,
                            "date" : dictConso["date"],
                            "IDunite" : dictConso["IDunite"],
                            "IDgroupe" : self.IDgroupe,
                            "heure_debut" : dictConso["heure_debut"],
                            "heure_fin" : dictConso["heure_fin"],
                            "etat" : dictConso["etat"],
                            "verrouillage" : 0,
                            "date_saisie" : datetime.date.today(),
                            "IDutilisateur" : UTILS_Identification.GetIDutilisateur(),
                            "IDcategorie_tarif" : self.IDcategorie_tarif,
                            "IDcompte_payeur" : self.IDcompte_payeur,
                            "IDprestation" : dictPeriode["IDprestation"],
                            "forfait" : None,
                            "quantite" : dictConso["quantite"],
                            }
                        listeAjouts.append(dictConsoTemp)

            if len(listeAjouts) > 0 :
                listeChamps = listeAjouts[0].keys() 
                listeDonnees = []
                listeInterrogations = []
                for champ in listeChamps :
                    listeInterrogations.append("?")
                for dictConso in listeAjouts :
                    listeTemp = []
                    for champ in listeChamps :
                        listeTemp.append(dictConso[champ])
                    listeDonnees.append(listeTemp)
                    
                DB.Executermany("INSERT INTO consommations (%s) VALUES (%s)" % (", ".join(listeChamps), ", ".join(listeInterrogations)), listeDonnees, commit=True)
                
            DB.Close()
    
    def VerifieCompatibilitesUnites(self, dictUnites={}, IDunite1=None, IDunite2=None):
        listeIncompatibilites = dictUnites[IDunite1]["unites_incompatibles"]
        if IDunite2 in listeIncompatibilites :
            return False
        return True

    def VerifieConsommations(self, listePeriodes=[]):
        # Récupération des unités
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        dictUnites = {}
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            dictUnites[IDunite] = {"nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "unites_incompatibles" : []}

        # Récupère les incompatibilités entre unités
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if dictUnites.has_key(IDunite) : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if dictUnites.has_key(IDunite_incompatible) : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)
        
        # Récupération des ouvertures des unités
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite=%d
        ORDER BY date; """ % self.IDactivite 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictOuvertures = {}
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictOuvertures[(date, IDunite, IDgroupe)] = IDouverture

        # Récupération des consommations
        req = """SELECT IDconso, date, IDunite, heure_debut, heure_fin, etat
        FROM consommations 
        WHERE IDactivite=%d AND IDindividu=%d
        ORDER BY date; """ % (self.IDactivite, self.IDindividu)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictConsommations = {}
        for IDconso, date, IDunite, heure_debut, heure_fin, etat in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if IDconso not in self.listeSuppressionConso :
                if dictConsommations.has_key(date) == False :
                    dictConsommations[date] = []
                dictConsommations[date].append({"IDconso" : IDconso, "IDunite" : IDunite, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "etat" : etat})
        
        DB.Close()
        
        listeAnomalies = []
        for dictPeriode in listePeriodes :
            for dictConso in dictPeriode["listeConso"] :
                if dictConso["IDconso"] == None :
                    dateFr = UTILS_Dates.DateDDEnFr(dictConso["date"])
                    valide = True
                    
                    # Vérifie si unité ouverte
                    if dictOuvertures.has_key((dictConso["date"], dictConso["IDunite"], self.IDgroupe)) == False :
                        listeAnomalies.append(_(u"%s : Unité %s fermée pour le groupe %s") % (dateFr, dictUnites[dictConso["IDunite"]]["nom"], self.nomGroupe))
                        valide = False
                    
                    # Recherche si pas d'incompatibilités avec les conso déjà saisies
                    if dictConsommations.has_key(dictConso["date"]) :
                        for dictConsoTemp in dictConsommations[dictConso["date"]] :
                            nomUnite1 = dictUnites[dictConso["IDunite"]]["nom"]
                            nomUnite2 = dictUnites[dictConsoTemp["IDunite"]]["nom"]
                            
                            if self.VerifieCompatibilitesUnites(dictUnites, dictConsoTemp["IDunite"], dictConso["IDunite"]) == False :
                                listeAnomalies.append(_(u"%s : Unité %s incompatible avec unité %s déjà présente") % (dateFr, nomUnite1, nomUnite2))
                                valide = False
                                
                            if dictConso["IDunite"] == dictConsoTemp["IDunite"] :
                                if dictUnites[dictConso["IDunite"]]["type"] == "Multihoraire" :
                                    if dictConso["heure_fin"] > dictConsoTemp["heure_debut"] and dictConso["heure_debut"] < dictConsoTemp["heure_fin"] :
                                        listeAnomalies.append(_(u"%s : L'unité multihoraires %s chevauche une consommation d'une unité identique") % (dateFr, nomUnite1))
                                        valide = False
                                else :
                                    listeAnomalies.append(_(u"%s : Unité %s déjà présente") % (dateFr, nomUnite1))
                                    valide = False
                    
        # Signalement des anomalies
        if len(listeAnomalies) :
            message1 = _(u"Validation du contrat impossible.\n\nLes %d anomalies suivantes ont été trouvées :") % len(listeAnomalies)
            message2 = u"\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, message1, caption = _(u"Génération des consommations"), msg2=message2, style = wx.ICON_EXCLAMATION | wx.YES|wx.YES_DEFAULT, btnLabels={wx.ID_YES : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True
    
##    def VerifieOuverturesConso(self, listePeriodes=[]):
##        DB = GestionDB.DB()
##        
##        # Récupération des ouvertures
##        req = """SELECT IDouverture, IDunite, IDgroupe, date
##        FROM ouvertures 
##        WHERE IDactivite=%d
##        ORDER BY date; """ % self.IDactivite 
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        dictOuvertures = {}
##        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
##            date = UTILS_Dates.DateEngEnDateDD(date)
##            dictOuvertures[(date, IDunite, IDgroupe)] = IDouverture
##        
##        # Récupération des unités
##        req = """SELECT IDunite, nom 
##        FROM unites; """
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        dictUnites = {}
##        for IDunite, nom in listeDonnees :
##            dictUnites[IDunite] = {"nom" : nom}
##        DB.Close()
##        
##        listeAnomalies = []
##        for dictPeriode in listePeriodes :
##            for dictConso in dictPeriode["listeConso"] :
##                if dictOuvertures.has_key((dictConso["date"], dictConso["IDunite"], self.IDgroupe)) == False :
##                    listeAnomalies.append(_(u"%s : Unité %s fermée pour le groupe %s") % (UTILS_Dates.DateDDEnFr(dictConso["date"]), dictUnites[dictConso["IDunite"]]["nom"], self.nomGroupe))
##
##        # Signalement des anomalies
##        if len(listeAnomalies) :
##            message1 = _(u"Impossible de créer ce contrat : Les %d anomalies suivantes ont été trouvées :") % len(listeAnomalies)
##            message2 = u"\n".join(listeAnomalies)
##            dlg = dialogs.MultiMessageDialog(self, message1, caption = _(u"Génération de consommations"), msg2=message2, style = wx.ICON_EXCLAMATION | wx.YES|wx.YES_DEFAULT, btnLabels={wx.ID_YES : _(u"Ok")})
##            reponse = dlg.ShowModal() 
##            dlg.Destroy() 
##            return False
##        
##        return True
    
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog_selection_activite(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.SetTitle(_(u"Sélection d'une activité"))
        
        self.label_intro = wx.StaticText(self, wx.ID_ANY, _(u"Sélectionnez l'activité pour laquelle vous souhaitez créer un modèle de contrat puis cliquez sur OK :"))
        self.ctrl_activites = OL_Activites.ListView(self, modificationAutorisee=False, id=-1, style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_activites.SetMinSize((150, 50))
        self.ctrl_activites.MAJ() 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((600, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        grid_sizer_base.Add(self.label_intro, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        grid_sizer_base.Add(self.ctrl_activites, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Contrats")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):  
        if len(self.ctrl_activites.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.EndModal(wx.ID_OK)

    def GetActivite(self):
        return self.ctrl_activites.Selection()[0].IDactivite
        
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDindividu=46, IDinscription=41, IDcontrat=None, IDmodele=4)
##    dialog_1 = Dialog(None, mode_modele=True, IDmodele=1, IDactivite=1)
##    dialog_1 = Dialog_selection_activite(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
