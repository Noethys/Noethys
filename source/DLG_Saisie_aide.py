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
import GestionDB

import CTRL_Saisie_date
import CTRL_Saisie_euros
import OL_Aides_montants


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
            # Pour les mod�les
            req = """SELECT IDactivite, nom
            FROM activites
            ORDER BY activites.nom;"""
        else:
            # Pour les aides aux familles
            req = """SELECT inscriptions.IDactivite, activites.nom
            FROM inscriptions
            LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
            GROUP BY inscriptions.IDactivite
            ORDER BY activites.nom;"""
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
        for index, values in self.dictDonnees.iteritems():
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
        self.dictDonnees[0] = { "ID" : None, "nom " : _(u"---------------- Aucune caisse ----------------") }
        listeItems.append(_(u"---------------- Aucune caisse ---------------"))
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
        for index, values in self.dictDonnees.iteritems():
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
        req = """SELECT rattachements.IDindividu, individus.nom, individus.prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        LEFT JOIN inscriptions ON inscriptions.IDindividu = rattachements.IDindividu
        WHERE rattachements.IDfamille=%d AND IDcategorie IN (1, 2)
        AND inscriptions.IDactivite=%d
        ORDER BY individus.nom, individus.prenom;""" % (self.IDfamille, IDactivite)
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
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent 
        self.IDaide = IDaide
        self.IDfamille = IDfamille
        
        self.listeInitialeBeneficiaires = []
        self.listeInitialeMontants = []
        self.listeInitialeCombi = []
        self.listeInitialeUnites = []
                
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de l'aide"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Activit�
        self.staticbox_activite_staticbox = wx.StaticBox(self, -1, _(u"Activit�"))
        self.ctrl_activite = CTRL_Activite(self, IDfamille=self.IDfamille)
        
        # Caisse
        self.staticbox_caisse_staticbox = wx.StaticBox(self, -1, _(u"Caisse"))
        self.ctrl_caisse = CTRL_Caisse(self, IDfamille=self.IDfamille)
        
        # P�riode
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"P�riode de validit�"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # B�n�ficiaires
        self.staticbox_beneficiaires_staticbox = wx.StaticBox(self, -1, _(u"B�n�ficiaires"))
        self.ctrl_beneficiaires = CTRL_Beneficiaires(self, IDfamille=self.IDfamille, IDactivite=None)
        
        # Plafonds
        self.staticbox_plafonds_staticbox = wx.StaticBox(self, -1, _(u"Plafonds"))
        self.checkbox_montant_max = wx.CheckBox(self, -1, _(u"Montant max. :"))
        self.ctrl_montant_max = CTRL_Saisie_euros.CTRL(self, size=(65, -1))
        self.checkbox_dates_max = wx.CheckBox(self, -1, _(u"Nbre dates max. :"))
        self.ctrl_dates_max = wx.SpinCtrl(self, -1, u"", min=0, max=1000, size=(60, -1))
        
        # Montants
        self.staticbox_montants_staticbox = wx.StaticBox(self, -1, _(u"Montants"))
        self.ctrl_montants = OL_Aides_montants.ListView(self, id=-1, name="OL_montants", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_importer = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer un mod�le"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_montant_max, self.checkbox_montant_max)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_dates_max, self.checkbox_dates_max)
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
                self.SetTitle(_(u"Modification d'un mod�le d'aide"))
            else:
                self.SetTitle(_(u"Modification d'une aide"))
            self.Importation()
        else:
            if self.IDfamille == None :
                self.SetTitle(_(u"Saisie d'un mod�le d'aide"))
            else:
                self.SetTitle(_(u"Saisie d'une aide"))
            self.ctrl_montants.MAJ() 
        
        # Init contr�les
        self.OnCheckbox_montant_max(None)
        self.OnCheckbox_dates_max(None) 
        
        if self.IDfamille == None :
            self.staticbox_beneficiaires_staticbox.Show(False)
            self.ctrl_beneficiaires.Show(False)
            self.bouton_importer.Show(False)
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom de l'aide"))
        self.ctrl_activite.SetToolTipString(_(u"S�lectionnez ici l'activit�"))
        self.ctrl_caisse.SetToolTipString(_(u"S�lectionnez ici une caisse"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez ici la date de d�but de validit�"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici la date de fin de validit�"))
        self.ctrl_beneficiaires.SetToolTipString(_(u"Cochez ici les b�n�ficiaires de l'aide"))
        self.checkbox_montant_max.SetToolTipString(_(u"Cliquez ici pour appliquer un montant maximal"))
        self.ctrl_montant_max.SetToolTipString(_(u"Saisissez ici le montant maximal"))
        self.checkbox_dates_max.SetToolTipString(_(u"Cliquez ici pour appliquer un nombre de dates maximal"))
        self.ctrl_dates_max.SetToolTipString(_(u"Cliquez ici le nombre maximal de dates"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un montant"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le montant s�lectionn� dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le montant s�lectionn� dans la liste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_importer.SetToolTipString(_(u"Cliquez ici pour importer un mod�le d'aide pr�d�fini"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))
        self.SetMinSize((600, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        staticbox_montants = wx.StaticBoxSizer(self.staticbox_montants_staticbox, wx.VERTICAL)
        grid_sizer_montants = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_montants = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_param = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_droit = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        staticbox_plafonds = wx.StaticBoxSizer(self.staticbox_plafonds_staticbox, wx.VERTICAL)
        grid_sizer_plafonds = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_dates_max = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_montant_max = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        staticbox_beneficiaires = wx.StaticBoxSizer(self.staticbox_beneficiaires_staticbox, wx.VERTICAL)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche2 = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        staticbox_caisse = wx.StaticBoxSizer(self.staticbox_caisse_staticbox, wx.VERTICAL)
        staticbox_activite = wx.StaticBoxSizer(self.staticbox_activite_staticbox, wx.VERTICAL)
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        staticbox_activite.Add(self.ctrl_activite, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_activite, 1, wx.EXPAND, 0)
        staticbox_caisse.Add(self.ctrl_caisse, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche2.Add(staticbox_caisse, 1, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche2.Add(staticbox_periode, 1, wx.EXPAND, 0)
        grid_sizer_gauche2.AddGrowableCol(0)
        grid_sizer_gauche.Add(grid_sizer_gauche2, 1, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_param.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        staticbox_beneficiaires.Add(self.ctrl_beneficiaires, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_beneficiaires, 1, wx.EXPAND, 0)
        grid_sizer_montant_max.Add(self.checkbox_montant_max, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montant_max.Add(self.ctrl_montant_max, 0, 0, 0)
        grid_sizer_plafonds.Add(grid_sizer_montant_max, 1, wx.EXPAND, 0)
        grid_sizer_dates_max.Add(self.checkbox_dates_max, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates_max.Add(self.ctrl_dates_max, 0, 0, 0)
        grid_sizer_plafonds.Add(grid_sizer_dates_max, 1, wx.EXPAND, 0)
        grid_sizer_plafonds.AddGrowableCol(0)
        staticbox_plafonds.Add(grid_sizer_plafonds, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_plafonds, 1, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_param.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_param.AddGrowableCol(0)
        grid_sizer_param.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_param, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_montants.Add(self.ctrl_montants, 1, wx.EXPAND, 0)
        grid_sizer_boutons_montants.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_montants.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_montants.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_montants.Add(grid_sizer_boutons_montants, 1, wx.EXPAND, 0)
        grid_sizer_montants.AddGrowableRow(0)
        grid_sizer_montants.AddGrowableCol(0)
        staticbox_montants.Add(grid_sizer_montants, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_montants, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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
        self.CenterOnScreen() 
    
    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activite.GetID()
        if self.IDfamille != None :
            self.ctrl_beneficiaires.SetIDactivite(IDactivite)
        self.ctrl_montants.SetIDactivite(IDactivite)
        
    def OnCheckbox_montant_max(self, event): 
        if self.checkbox_montant_max.GetValue() == True :
            self.ctrl_montant_max.Enable(True)
        else:
            self.ctrl_montant_max.Enable(False)

    def OnCheckbox_dates_max(self, event): 
        if self.checkbox_dates_max.GetValue() == True :
            self.ctrl_dates_max.Enable(True)
        else:
            self.ctrl_dates_max.Enable(False)

    def OnBoutonAjouter(self, event): 
        self.ctrl_montants.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_montants.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_montants.Supprimer(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Caisse")

    def OnBoutonImporter(self, event): 
        """ Importer un mod�le d'aide """
        import DLG_Choix_modele_aide
        dlg = DLG_Choix_modele_aide.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.IDaide = dlg.GetIDaide()
            self.Importation(modele=True) 
            self.IDaide = None
        dlg.Destroy()


    
    def Importation(self, modele=False):
        # Importation des donn�es sur l'aide
        DB = GestionDB.DB()
        req = """SELECT IDaide, IDfamille, IDactivite, nom, date_debut, date_fin, IDcaisse, montant_max, nbre_dates_max
        FROM aides
        WHERE IDaide=%d
        ;""" % self.IDaide
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : 
            DB.Close()
            return None
        IDaide, IDfamille, IDactivite, nom, date_debut, date_fin, IDcaisse, montant_max, nbre_dates_max = listeDonnees[0]
        
        # Activit�
        self.ctrl_activite.SetID(IDactivite)
        if self.IDfamille != None :
            self.ctrl_beneficiaires.SetIDactivite(IDactivite)
        self.ctrl_montants.SetIDactivite(IDactivite)
        
        # Caisse
        self.ctrl_caisse.SetID(IDcaisse)
        
        # Nom
        self.ctrl_nom.SetValue(nom)
        
        # Dates de validit�
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        
        # Plafonds
        if montant_max != None :
            self.ctrl_montant_max.SetMontant(montant_max)
            self.checkbox_montant_max.SetValue(True)
        if nbre_dates_max != None :
            self.ctrl_dates_max.SetValue(nbre_dates_max)
            self.checkbox_dates_max.SetValue(True) 
        
        # B�n�ficiaires
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
            if dictCombinaisons.has_key(IDaide_montant) == False :
                dictCombinaisons[IDaide_montant] = {}
            if dictCombinaisons[IDaide_montant].has_key(IDaide_combi) == False :
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
            if dictCombinaisons.has_key(IDaide_montant) :
                for IDaide_combi, dictCombi in dictCombinaisons[IDaide_montant].iteritems() :
                    listeCombinaisons.append(dictCombi)
            dictMontant = { "IDaide_montant" : IDaide_montant, "montant" : montant , "combinaisons" : listeCombinaisons }
            listeMontants.append(dictMontant)
        self.listeInitialeMontants = list(listeMontants)
        
        # Si on vient d'importer un mod�le, on supprime les ID de chaque champ
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
        # R�cup�ration des donn�es
        
        # Nom
        nom = self.ctrl_nom.GetValue()
        if nom == u"" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        # Activit�
        IDactivite = self.ctrl_activite.GetID()
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
        
        # Dates de validit�
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de d�but de validit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de validit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"Vous avez saisi une date de d�but sup�rieure � la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Plafonds
        if self.checkbox_montant_max.GetValue() == True :
            montant_max = self.ctrl_montant_max.GetMontant()
            if montant_max == None or montant_max == 0.0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant plafond !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        else:
            montant_max = None
        if self.checkbox_dates_max.GetValue() == True :
            nbre_dates_max = int(self.ctrl_dates_max.GetValue())
            if nbre_dates_max == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un de nombre de dates maximal !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        else:
            nbre_dates_max = None
            
##        if nbre_dates_max != None :
##            self.ctrl_dates_max.SetValue(str(nbre_dates_max))
##            self.checkbox_dates_max.SetValue(True) 
        
        # B�n�ficiaires
        listeBeneficiaires = self.ctrl_beneficiaires.GetIDcoches()
        if self.IDfamille != None :
            if len(listeBeneficiaires) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous s�lectionner au moins un b�n�ficiaire dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
            ("montant_max", montant_max),
            ("nbre_dates_max", nbre_dates_max),
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
##                {"IDaide_combi_unite" : None, "IDunite" : 35}, # Apr�s-midi
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 34}, # Matin�e
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
                # Enregistrement d'un montant modifi�
                for dictMontantInitial in self.listeInitialeMontants :
                    if dictMontantInitial["IDaide_montant"] == IDaide_montant :
                        if dictMontantInitial["montant"] != montant :
                            DB.ReqMAJ("aides_montants", [("montant", montant),], "IDaide_montant", IDaide_montant)
                listeIDmontant.append(IDaide_montant)
            
            # Sauvegarde des unit�s de combi
            for dictCombi in listeCombinaisons :
                IDaide_combi = dictCombi["IDaide_combi"]
                listeUnites = dictCombi["listeUnites"]
                
                # Nouvelles combinaisons
                if IDaide_combi == None :
                    listeDonnees = [ ("IDaide_montant", IDaide_montant), ("IDaide", self.IDaide), ]
                    IDaide_combi = DB.ReqInsert("aides_combinaisons", listeDonnees)
                else:
                    listeIDcombi.append(IDaide_combi)
                    
                # Nouvelles unit�s
                for dictUnite in listeUnites :
                    IDaide_combi_unite = dictUnite["IDaide_combi_unite"]
                    IDunite = dictUnite["IDunite"]
                    
                    # Nouvelles combinaisons
                    if IDaide_combi_unite == None :
                        listeDonnees = [ ("IDunite", IDunite), ("IDaide_combi", IDaide_combi), ("IDaide", self.IDaide), ]
                        IDaide_combi_unite = DB.ReqInsert("aides_combi_unites", listeDonnees)
                    else:
                        listeIDunites.append(IDaide_combi_unite)
        
        # Suppression des montants supprim�s
        for dictMontantInitial in self.listeInitialeMontants :
            if dictMontantInitial["IDaide_montant"] not in listeIDmontant and dictMontantInitial["IDaide_montant"] != None :
                DB.ReqDEL("aides_montants", "IDaide_montant", dictMontantInitial["IDaide_montant"])
        
        
        # Suppression des combinaisons supprim�es :
        for IDaide_combi in self.listeInitialeCombi :
            if IDaide_combi not in listeIDcombi and IDaide_combi != None :
                DB.ReqDEL("aides_combinaisons", "IDaide_combi", IDaide_combi)
                
        # Suppression des unit�s de combi supprim�es
        for IDaide_combi_unite in self.listeInitialeUnites :
            if IDaide_combi_unite not in listeIDunites and IDaide_combi_unite != None :
                DB.ReqDEL("aides_combi_unites", "IDaide_combi_unite", IDaide_combi_unite)
                
        DB.Close()
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDaide=1, IDfamille=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
