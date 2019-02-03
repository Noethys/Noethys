#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB

from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Dlg.DLG_Saisie_lot_conso import CTRL_Jours
from Ol import OL_Aides_montants


class CTRL_Activite(wx.Choice):
    def __init__(self, parent, IDfamille=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        if self.IDfamille == None :
            # Pour les modèles
            req = """SELECT IDactivite, nom
            FROM activites
            ORDER BY activites.nom;"""
        else:
            # Pour les aides aux familles
            req = """SELECT inscriptions.IDactivite, activites.nom
            FROM inscriptions
            LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
            WHERE inscriptions.statut='ok'
            GROUP BY inscriptions.IDactivite
            ORDER BY activites.date_fin DESC;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDactivite, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDactivite, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
            

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Caisse(wx.Choice):
    def __init__(self, parent, IDfamille=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : None, "nom " : _(u"- Aucune caisse -") }
        listeItems.append(_(u"- Aucune caisse -"))
        db = GestionDB.DB()
        req = """SELECT IDcaisse, nom
        FROM caisses
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        index = 1
        for IDcaisse, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcaisse, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Beneficiaires(wx.CheckListBox):
    def __init__(self, parent, IDfamille=None, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDactivite = IDactivite
        self.data = []
        if self.IDfamille == None :
            self.Enable(False)
        else:
            self.MAJ() 

    def MAJ(self):
        if self.IDactivite == None :
            IDactivite = 0
        else:
            IDactivite = self.IDactivite
        db = GestionDB.DB()
        # req = """SELECT rattachements.IDindividu, individus.nom, individus.prenom
        # FROM rattachements
        # LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        # LEFT JOIN inscriptions ON inscriptions.IDindividu = rattachements.IDindividu
        # WHERE rattachements.IDfamille=%d AND IDcategorie IN (1, 2)
        # AND inscriptions.IDactivite=%d
        # ORDER BY individus.nom, individus.prenom;""" % (self.IDfamille, IDactivite)
        req = """SELECT rattachements.IDindividu, individus.nom, individus.prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE rattachements.IDfamille=%d AND IDcategorie IN (1, 2)
        ORDER BY individus.nom, individus.prenom;""" % self.IDfamille

        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeValeurs = []
        for IDindividu, nom, prenom in listeDonnees :
            if prenom == None : prenom = u""
            listeValeurs.append((IDindividu, u"%s %s" % (nom, prenom), False))
        self.SetData(listeValeurs)
    
    def SetIDactivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
# -----------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent, IDaide=None, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent 
        self.IDaide = IDaide
        self.IDfamille = IDfamille
        
        self.listeInitialeBeneficiaires = []
        self.listeInitialeMontants = []
        self.listeInitialeCombi = []
        self.listeInitialeUnites = []
                
        # Nom
        self.label_nom = wx.StaticText(self, -1, _(u"Nom de l'aide :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))

        # Activité
        self.label_activite = wx.StaticText(self, -1, _(u"Activité associée :"))
        self.ctrl_activite = CTRL_Activite(self, IDfamille=self.IDfamille)

        # Caisse
        self.label_caisse = wx.StaticText(self, -1, _(u"Caisse associée :"))
        self.ctrl_caisse = CTRL_Caisse(self, IDfamille=self.IDfamille)

        # Période
        self.label_periode = wx.StaticText(self, -1, _(u"Période de validité :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Jours
        self.label_scolaires = wx.StaticText(self, -1, _(u"Jours scolaires :"))
        self.ctrl_scolaires = CTRL_Jours(self, "scolaires")
        self.label_vacances = wx.StaticText(self, -1, _(u"Jours de vacances :"))
        self.ctrl_vacances = CTRL_Jours(self, "vacances")
        self.ctrl_scolaires.SetJoursStr("0;1;2;3;4;5;6")
        self.ctrl_vacances.SetJoursStr("0;1;2;3;4;5;6")

        # Plafonds
        self.label_plafonds = wx.StaticText(self, -1, _(u"Plafonds :"))
        self.checkbox_plafond_montant = wx.CheckBox(self, -1, _(u"Montant :"))
        self.ctrl_plafond_montant = CTRL_Saisie_euros.CTRL(self, size=(65, -1))
        self.checkbox_plafond_quantite = wx.CheckBox(self, -1, _(u"Quantité :"))
        self.ctrl_plafond_quantite = wx.SpinCtrl(self, -1, u"", min=0, max=1000, size=(60, -1))

        # Bénéficiaires
        self.staticbox_beneficiaires_staticbox = wx.StaticBox(self, -1, _(u"Bénéficiaires"))
        self.ctrl_beneficiaires = CTRL_Beneficiaires(self, IDfamille=self.IDfamille, IDactivite=None)
        self.ctrl_beneficiaires.SetMinSize((50, 80))

        # Montants
        self.staticbox_montants_staticbox = wx.StaticBox(self, -1, _(u"Montants"))
        self.ctrl_montants = OL_Aides_montants.ListView(self, id=-1, name="OL_montants", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_montants.SetMinSize((50, 100))
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_importer = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer un modèle"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_plafond_montant, self.checkbox_plafond_montant)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_plafond_quantite, self.checkbox_plafond_quantite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImporter, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        
        # Importation
        if self.IDaide != None :
            if self.IDfamille == None :
                self.SetTitle(_(u"Modification d'un modèle d'aide"))
            else:
                self.SetTitle(_(u"Modification d'une aide"))
            self.Importation()
        else:
            if self.IDfamille == None :
                self.SetTitle(_(u"Saisie d'un modèle d'aide"))
            else:
                self.SetTitle(_(u"Saisie d'une aide"))
            self.ctrl_montants.MAJ() 
        
        # Init contrôles
        self.OnCheckbox_plafond_montant(None)
        self.OnCheckbox_plafond_quantite(None) 
        
        if self.IDfamille == None :
            self.staticbox_beneficiaires_staticbox.Show(False)
            self.ctrl_beneficiaires.Show(False)
            self.bouton_importer.Show(False)
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de l'aide (Exemple : 'Bons vacances CAF 2017')")))
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici l'activité")))
        self.ctrl_caisse.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une caisse")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de validité")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de validité")))
        self.ctrl_beneficiaires.SetToolTip(wx.ToolTip(_(u"Cochez ici les bénéficiaires de l'aide")))
        self.checkbox_plafond_montant.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer un montant maximal")))
        self.ctrl_plafond_montant.SetToolTip(wx.ToolTip(_(u"Saisissez ici le montant maximal")))
        self.checkbox_plafond_quantite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer un nombre de dates maximal")))
        self.ctrl_plafond_quantite.SetToolTip(wx.ToolTip(_(u"Cliquez ici le nombre maximal de dates")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un montant")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le montant sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le montant sélectionné dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_importer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer un modèle d'aide prédéfini")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Généralites
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=7, cols=2, vgap=10, hgap=10)

        # Nom de l'aide
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 1, wx.EXPAND, 0)

        # Activité
        grid_sizer_generalites.Add(self.label_activite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_activite, 1, wx.EXPAND, 0)

        # Caisse
        grid_sizer_generalites.Add(self.label_caisse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_caisse, 1, wx.EXPAND, 0)

        # Période
        grid_sizer_generalites.Add(self.label_periode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 0)

        # Jours
        grid_sizer_generalites.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_scolaires, 0, 0, 0)
        grid_sizer_generalites.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_vacances, 0, 0, 0)

        # Plafonds
        grid_sizer_generalites.Add(self.label_plafonds, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_plafonds = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
        grid_sizer_plafonds.Add(self.checkbox_plafond_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_plafonds.Add(self.ctrl_plafond_montant, 0, 0, 0)
        grid_sizer_plafonds.Add((20, 20), 0, 0, 0)
        grid_sizer_plafonds.Add(self.checkbox_plafond_quantite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_plafonds.Add(self.ctrl_plafond_quantite, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_plafonds, 0, 0, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Bénéficiaires
        staticbox_beneficiaires = wx.StaticBoxSizer(self.staticbox_beneficiaires_staticbox, wx.VERTICAL)
        staticbox_beneficiaires.Add(self.ctrl_beneficiaires, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_beneficiaires, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Montants
        staticbox_montants = wx.StaticBoxSizer(self.staticbox_montants_staticbox, wx.VERTICAL)
        grid_sizer_montants = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_montants = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_montants.Add(self.ctrl_montants, 1, wx.EXPAND, 0)
        grid_sizer_boutons_montants.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_montants.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_montants.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_montants.Add(grid_sizer_boutons_montants, 1, wx.EXPAND, 0)
        grid_sizer_montants.AddGrowableRow(0)
        grid_sizer_montants.AddGrowableCol(0)
        staticbox_montants.Add(grid_sizer_montants, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_montants, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_importer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 
    
    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activite.GetID()
        if self.IDfamille != None :
            self.ctrl_beneficiaires.SetIDactivite(IDactivite)
        self.ctrl_montants.SetIDactivite(IDactivite)
        
    def OnCheckbox_plafond_montant(self, event): 
        if self.checkbox_plafond_montant.GetValue() == True :
            self.ctrl_plafond_montant.Enable(True)
        else:
            self.ctrl_plafond_montant.Enable(False)

    def OnCheckbox_plafond_quantite(self, event): 
        if self.checkbox_plafond_quantite.GetValue() == True :
            self.ctrl_plafond_quantite.Enable(True)
        else:
            self.ctrl_plafond_quantite.Enable(False)

    def OnBoutonAjouter(self, event): 
        self.ctrl_montants.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_montants.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_montants.Supprimer(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Caisse")

    def OnBoutonImporter(self, event): 
        """ Importer un modèle d'aide """
        import DLG_Choix_modele_aide
        dlg = DLG_Choix_modele_aide.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.IDaide = dlg.GetIDaide()
            self.Importation(modele=True) 
            self.IDaide = None
        dlg.Destroy()


    
    def Importation(self, modele=False):
        # Importation des données sur l'aide
        DB = GestionDB.DB()
        req = """SELECT IDaide, IDfamille, IDactivite, nom, date_debut, date_fin, IDcaisse, montant_max, nbre_dates_max, jours_scolaires, jours_vacances
        FROM aides
        WHERE IDaide=%d
        ;""" % self.IDaide
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : 
            DB.Close()
            return None
        IDaide, IDfamille, IDactivite, nom, date_debut, date_fin, IDcaisse, plafond_montant, nbre_plafond_quantite, jours_scolaires, jours_vacances = listeDonnees[0]
        
        # Activité
        self.ctrl_activite.SetID(IDactivite)
        if self.IDfamille != None :
            self.ctrl_beneficiaires.SetIDactivite(IDactivite)
        self.ctrl_montants.SetIDactivite(IDactivite)
        
        # Caisse
        self.ctrl_caisse.SetID(IDcaisse)
        
        # Nom
        self.ctrl_nom.SetValue(nom)
        
        # Dates de validité
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)

        # Jours
        self.ctrl_scolaires.SetJoursStr(jours_scolaires)
        self.ctrl_vacances.SetJoursStr(jours_vacances)

        # Plafonds
        if plafond_montant != None :
            self.ctrl_plafond_montant.SetMontant(plafond_montant)
            self.checkbox_plafond_montant.SetValue(True)
        if nbre_plafond_quantite != None :
            self.ctrl_plafond_quantite.SetValue(nbre_plafond_quantite)
            self.checkbox_plafond_quantite.SetValue(True) 
        
        # Bénéficiaires
        listeIDindividus = []
        if self.IDfamille != None : 
            req = """SELECT IDaide_beneficiaire, IDindividu
            FROM aides_beneficiaires
            WHERE IDaide=%d;""" % self.IDaide
            DB.ExecuterReq(req)
            listeBeneficiaires = DB.ResultatReq()
            for IDaide_beneficiaire, IDindividu in listeBeneficiaires :
                listeIDindividus.append(IDindividu)
            self.ctrl_beneficiaires.SetIDcoches(listeIDindividus)
        self.listeInitialeBeneficiaires = list(listeIDindividus)

        # Combinaisons
        req = """SELECT 
        aides_combi_unites.IDaide_combi_unite, aides_combi_unites.IDaide_combi, aides_combi_unites.IDunite,
        aides_combinaisons.IDaide_montant
        FROM aides_combi_unites
        LEFT JOIN aides_combinaisons ON aides_combinaisons.IDaide_combi = aides_combi_unites.IDaide_combi
        LEFT JOIN aides_montants ON aides_montants.IDaide_montant = aides_combinaisons.IDaide_montant
        WHERE aides_montants.IDaide=%d;""" % self.IDaide
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        dictCombinaisons = {}
        for IDaide_combi_unite, IDaide_combi, IDunite, IDaide_montant in listeUnites :
            dictUnite = {"IDaide_combi_unite" : IDaide_combi_unite, "IDunite" : IDunite}
            if (IDaide_montant in dictCombinaisons) == False :
                dictCombinaisons[IDaide_montant] = {}
            if (IDaide_combi in dictCombinaisons[IDaide_montant]) == False :
                dictCombinaisons[IDaide_montant][IDaide_combi] = { "IDaide_combi" : IDaide_combi, "listeUnites" : [] }
            if dictUnite not in dictCombinaisons[IDaide_montant][IDaide_combi]["listeUnites"] :
                dictCombinaisons[IDaide_montant][IDaide_combi]["listeUnites"].append(dictUnite)
            
            if IDaide_combi not in self.listeInitialeCombi : self.listeInitialeCombi.append(IDaide_combi)
            if IDaide_combi_unite not in self.listeInitialeUnites : self.listeInitialeUnites.append(IDaide_combi_unite)
        
        # Montants
        req = """SELECT IDaide_montant, montant
        FROM aides_montants
        WHERE IDaide=%d;""" % self.IDaide
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeMontants = []
        for IDaide_montant, montant in listeDonnees :
            listeCombinaisons = []
            if IDaide_montant in dictCombinaisons :
                for IDaide_combi, dictCombi in dictCombinaisons[IDaide_montant].items() :
                    listeCombinaisons.append(dictCombi)
            dictMontant = { "IDaide_montant" : IDaide_montant, "montant" : montant , "combinaisons" : listeCombinaisons }
            listeMontants.append(dictMontant)
        self.listeInitialeMontants = list(listeMontants)
        
        # Si on vient d'importer un modèle, on supprime les ID de chaque champ
        if modele == True :
            
            self.listeInitialeMontants = [] 
            self.listeInitialeCombi = []
            self.listeInitialeUnites = []
            for dictMontant in listeMontants :
                dictMontant["IDaide_montant"] = None
                for dictCombi in dictMontant["combinaisons"] :
                    dictCombi["IDaide_combi"] = None
                    for dictUnite in dictCombi["listeUnites"] :
                        dictUnite["IDaide_combi_unite"] = None
        
        # Envoie les montants au listCtrl
        self.ctrl_montants.SetListeMontants(listeMontants)

        DB.Close()
        
    def GetIDaide(self):
        return self.IDaide
        
    def OnBoutonOk(self, event):
        # Récupération des données
        
        # Nom
        nom = self.ctrl_nom.GetValue()
        if nom == u"" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        # Activité
        IDactivite = self.ctrl_activite.GetID()
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_activite.SetFocus()
            return
        
        # Caisse
        IDcaisse = self.ctrl_caisse.GetID()
##        if IDcaisse == None :
##            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une caisse !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_caisse.SetFocus()
##            return
        
        # Dates de validité
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de validité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de validité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"Vous avez saisi une date de début supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Jours
        jours_scolaires = self.ctrl_scolaires.GetJoursStr()
        jours_vacances = self.ctrl_vacances.GetJoursStr()

        # Plafonds
        if self.checkbox_plafond_montant.GetValue() == True :
            plafond_montant = self.ctrl_plafond_montant.GetMontant()
            if plafond_montant == None or plafond_montant == 0.0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant plafond !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        else:
            plafond_montant = None
        if self.checkbox_plafond_quantite.GetValue() == True :
            nbre_plafond_quantite = int(self.ctrl_plafond_quantite.GetValue())
            if nbre_plafond_quantite == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un de nombre de dates maximal !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        else:
            nbre_plafond_quantite = None
            
##        if nbre_plafond_quantite != None :
##            self.ctrl_plafond_quantite.SetValue(str(nbre_plafond_quantite))
##            self.checkbox_plafond_quantite.SetValue(True) 
        
        # Bénéficiaires
        listeBeneficiaires = self.ctrl_beneficiaires.GetIDcoches()
        if self.IDfamille != None :
            if len(listeBeneficiaires) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous sélectionner au moins un bénéficiaire dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Montants
        listeMontants = self.ctrl_montants.GetListeMontants()
        if len(listeMontants) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun montant !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Sauvegarde de l'aide
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDfamille", self.IDfamille ),
            ("IDactivite", IDactivite ),
            ("nom", nom ),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("IDcaisse", IDcaisse),
            ("montant_max", plafond_montant),
            ("nbre_dates_max", nbre_plafond_quantite),
            ("jours_scolaires", jours_scolaires),
            ("jours_vacances", jours_vacances),
        ]
        
        if self.IDaide == None :
            self.IDaide = DB.ReqInsert("aides", listeDonnees)
        else:
            DB.ReqMAJ("aides", listeDonnees, "IDaide", self.IDaide)
        
        # Sauvegarde des utilisateurs
        for IDindividu in listeBeneficiaires :
            if IDindividu not in self.listeInitialeBeneficiaires :
                listeDonnees = [("IDaide", self.IDaide ), ("IDindividu", IDindividu ),]
                DB.ReqInsert("aides_beneficiaires", listeDonnees)
        for IDindividu in self.listeInitialeBeneficiaires :
            if IDindividu not in listeBeneficiaires :
                req = """DELETE FROM aides_beneficiaires 
                WHERE IDaide=%d AND IDindividu=%d;""" % (self.IDaide, IDindividu)
                DB.ExecuterReq(req)
                DB.Commit()
        
        # Sauvegarde des montants
        
##    DONNEES_TEST = {
##    "IDaide_montant" : None,
##    "montant" : 20.0,
##    "combinaisons" : [
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 35}, # Après-midi
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 34}, # Matinée
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##        ],
##    }
        
        listeIDmontant = []
        listeIDcombi = []
        listeIDunites = []
        
        for dictMontant in listeMontants :
            IDaide_montant = dictMontant["IDaide_montant"]
            montant = dictMontant["montant"]
            listeCombinaisons = dictMontant["combinaisons"]
            
            # Sauvegarde des nouveau montants
            if IDaide_montant == None :
                listeDonnees = [ ("IDaide", self.IDaide), ("montant", montant), ]
                IDaide_montant = DB.ReqInsert("aides_montants", listeDonnees)
            else:
                # Enregistrement d'un montant modifié
                for dictMontantInitial in self.listeInitialeMontants :
                    if dictMontantInitial["IDaide_montant"] == IDaide_montant :
                        if dictMontantInitial["montant"] != montant :
                            DB.ReqMAJ("aides_montants", [("montant", montant),], "IDaide_montant", IDaide_montant)
                listeIDmontant.append(IDaide_montant)
            
            # Sauvegarde des unités de combi
            for dictCombi in listeCombinaisons :
                IDaide_combi = dictCombi["IDaide_combi"]
                listeUnites = dictCombi["listeUnites"]
                
                # Nouvelles combinaisons
                if IDaide_combi == None :
                    listeDonnees = [ ("IDaide_montant", IDaide_montant), ("IDaide", self.IDaide), ]
                    IDaide_combi = DB.ReqInsert("aides_combinaisons", listeDonnees)
                else:
                    listeIDcombi.append(IDaide_combi)
                    
                # Nouvelles unités
                for dictUnite in listeUnites :
                    IDaide_combi_unite = dictUnite["IDaide_combi_unite"]
                    IDunite = dictUnite["IDunite"]
                    
                    # Nouvelles combinaisons
                    if IDaide_combi_unite == None :
                        listeDonnees = [ ("IDunite", IDunite), ("IDaide_combi", IDaide_combi), ("IDaide", self.IDaide), ]
                        IDaide_combi_unite = DB.ReqInsert("aides_combi_unites", listeDonnees)
                    else:
                        listeIDunites.append(IDaide_combi_unite)
        
        # Suppression des montants supprimés
        for dictMontantInitial in self.listeInitialeMontants :
            if dictMontantInitial["IDaide_montant"] not in listeIDmontant and dictMontantInitial["IDaide_montant"] != None :
                DB.ReqDEL("aides_montants", "IDaide_montant", dictMontantInitial["IDaide_montant"])
        
        
        # Suppression des combinaisons supprimées :
        for IDaide_combi in self.listeInitialeCombi :
            if IDaide_combi not in listeIDcombi and IDaide_combi != None :
                DB.ReqDEL("aides_combinaisons", "IDaide_combi", IDaide_combi)
                
        # Suppression des unités de combi supprimées
        for IDaide_combi_unite in self.listeInitialeUnites :
            if IDaide_combi_unite not in listeIDunites and IDaide_combi_unite != None :
                DB.ReqDEL("aides_combi_unites", "IDaide_combi_unite", IDaide_combi_unite)
                
        DB.Close()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDaide=1, IDfamille=205)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
