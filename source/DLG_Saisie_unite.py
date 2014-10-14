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
import CTRL_Saisie_date
import CTRL_Saisie_heure
import CTRL_Ultrachoice
import UTILS_Dates

import DATA_Touches as Touches
import GestionDB


class CTRL_Restaurateur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
    
    def MAJlisteDonnees(self):
        self.SetItems(self.GetListeDonnees())
        self.Select(0)
    
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDrestaurateur, nom
        FROM restaurateurs
        ORDER BY nom;""" 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [ u"-------- Aucun --------", ]
        self.dictDonnees = { 0 : { "ID" : None } }
        index = 1
        for IDrestaurateur, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDrestaurateur }
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
            

# -------------------------------------------------------------------------------------------------------

class CTRL_Raccourci(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
    
    def MAJlisteDonnees(self):
        self.SetItems(self.GetListeDonnees())
        self.Select(0)
    
    def GetListeDonnees(self):
        listeTouches = Touches.LISTE_TOUCHES
        dictTouches = Touches.DICT_TOUCHES
        listeItems = [ u"------------- Aucune touche de raccourci -------------", ]
        self.dictDonnees = { 0 : { "code" : None } }
        index = 1
        for code in listeTouches :
            label = dictTouches[code][0]
            self.dictDonnees[index] = { "code" : code }
            listeItems.append(label)
            index += 1
        return listeItems

    def SetCode(self, code=None):
        for index, values in self.dictDonnees.iteritems():
            if values["code"] == code :
                 self.SetSelection(index)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["code"]

# -----------------------------------------------------------------------------------------

class CTRL_Type(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent):
        donnees=[ 
            {"label" : u"Standard", "description" : u"Pour saisir une conso simple par case", "image" : wx.Bitmap(u"Images/Special/Unite_standard.png", wx.BITMAP_TYPE_ANY)},
            {"label" : u"Horaire", "description" : u"Pour saisir un horaire dans chaque case", "image" : wx.Bitmap(u"Images/Special/Unite_horaire.png", wx.BITMAP_TYPE_ANY)},
            {"label" : u"Multi-horaires", "description" : u"Pour saisir plusieurs conso horaires par case", "image" : wx.Bitmap(u"Images/Special/Unite_multihoraires.png", wx.BITMAP_TYPE_ANY)},
            {"label" : u"Quantité", "description" : u"Pour attribuer une quantité à une conso", "image" : wx.Bitmap(u"Images/Special/Unite_quantite.png", wx.BITMAP_TYPE_ANY)},
            ]
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees=donnees) 
        self.parent = parent
        self.SetDonnees(donnees)
        self.Select(0)
                                        
    def SetType(self, code=None):
        if code == "Unitaire" : self.SetSelection2(0) 
        if code == "Horaire" : self.SetSelection2(1) 
        if code == "Multihoraires" : self.SetSelection2(2) 
        if code == "Quantite" : self.SetSelection2(3) 

    def GetType(self):
        if self.GetSelection2() == 0 : return "Unitaire"
        if self.GetSelection2() == 1 : return "Horaire"
        if self.GetSelection2() == 2 : return "Multihoraires"
        if self.GetSelection2() == 3 : return "Quantite"


# -----------------------------------------------------------------------------------------


class CheckListBoxGroupes(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None, IDunite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.IDactivite = IDactivite
        self.IDunite = IDunite
        self.SetMinSize((-1, 60))
    
    def MAJ(self):
        listeTmp = []
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom 
        FROM groupes 
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 : 
            for IDgroupe, nom in listeDonnees :
                listeTmp.append((IDgroupe, nom, False))
        self.SetData(listeTmp)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.Clear()
        self.data = []
        index = 0
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
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDunite_groupe, IDgroupe 
        FROM unites_groupes WHERE IDunite=%d;""" % self.IDunite
        db.ExecuterReq(req)
        listeTemp = db.ResultatReq()
        db.Close()
        if len(listeTemp) > 0 : 
            listeID = []
            for IDunite_groupe, IDgroupe in listeTemp :
                listeID.append(IDgroupe)
            self.SetIDcoches(listeID)

    def Sauvegarde(self):
        liste_nouvelle = self.GetIDcoches()
        liste_ancienne = []
        DB = GestionDB.DB()
        req = """SELECT IDunite_groupe, IDgroupe 
        FROM unites_groupes WHERE IDunite=%d;""" % self.IDunite        
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        if len(listeTemp) > 0 : 
            listeID = []
            for IDunite_groupe, IDgroupe in listeTemp :
                liste_ancienne.append(IDgroupe)
        # On enregistre les nouveaux
        for IDgroupe in liste_nouvelle :
            if IDgroupe not in liste_ancienne :
                listeDonnees = [ ("IDunite", self.IDunite ), ("IDgroupe", IDgroupe ), ]
                IDunite_groupe = DB.ReqInsert("unites_groupes", listeDonnees)
        # On enlève les anciens
        for IDgroupe in liste_ancienne :
            if IDgroupe not in liste_nouvelle :
                DB.ReqDEL("unites_groupes", "IDgroupe", IDgroupe)
        DB.Close()


# --------------------------------------------------------------------------------------------------------------------

class CheckListBoxIncompat(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None, IDunite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.IDactivite = IDactivite
        self.IDunite = IDunite
        self.SetMinSize((-1, 80))
    
    def MAJ(self):
        listeTmp = []
        db = GestionDB.DB()
        req = """SELECT IDunite, nom
        FROM unites 
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 : 
            for IDunite, nom in listeDonnees :
                if IDunite != self.IDunite :
                    listeTmp.append((IDunite, nom, False))
        self.SetData(listeTmp)    
            
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.Clear()
        self.data = []
        index = 0
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
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDunite_incompat, IDunite_incompatible 
        FROM unites_incompat WHERE IDunite=%d;""" % self.IDunite
        db.ExecuterReq(req)
        listeTemp = db.ResultatReq()
        db.Close()
        if len(listeTemp) > 0 : 
            listeID = []
            for IDunite_incompat, IDunite_incompatible in listeTemp :
                listeID.append(IDunite_incompatible)
            self.SetIDcoches(listeID)

    def Sauvegarde(self):
        liste_nouvelle = self.GetIDcoches()
        liste_ancienne = []
        DB = GestionDB.DB()
        req = """SELECT IDunite_incompat, IDunite_incompatible 
        FROM unites_incompat WHERE IDunite=%d;""" % self.IDunite        
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        if len(listeTemp) > 0 : 
            listeID = []
            for IDunite_incompat, IDunite_incompatible in listeTemp :
                liste_ancienne.append(IDunite_incompatible)
        # On enregistre les nouveaux
        for IDunite_incompatible in liste_nouvelle :
            if IDunite_incompatible not in liste_ancienne :
                listeDonnees = [ ("IDunite", self.IDunite ), ("IDunite_incompatible", IDunite_incompatible ), ]
                IDunite_incompatible = DB.ReqInsert("unites_incompat", listeDonnees)
        # On enlève les anciens
        for IDunite_incompatible in liste_ancienne :
            if IDunite_incompatible not in liste_nouvelle :
                DB.ReqDEL("unites_incompat", "IDunite_incompatible", IDunite_incompatible)
        DB.Close()

# ------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, IDunite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDunite = IDunite
        self.typeUnite = None
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, u"Nom de l'unité")
        self.label_nom = wx.StaticText(self, -1, u"Nom complet :")
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_abrege = wx.StaticText(self, -1, u"Nom abrégé :")
        self.ctrl_abrege = wx.TextCtrl(self, -1, u"")
        
        # Caractéristiques
        self.staticbox_caract_staticbox = wx.StaticBox(self, -1, u"Caractéristiques")
        self.label_type = wx.StaticText(self, -1, u"Type d'unité :")
        self.ctrl_type = CTRL_Type(self)

        self.label_horaires = wx.StaticText(self, -1, u"Amplitude horaire :")
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.ctrl_heure_debut_fixe = wx.CheckBox(self, -1, u"Fixe")
        self.label_a = wx.StaticText(self, -1, u"à")
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)
        self.ctrl_heure_fin_fixe = wx.CheckBox(self, -1, u"Fixe")
        
        self.label_groupes = wx.StaticText(self, -1, u"Groupes :")
        self.radio_groupes_tous = wx.RadioButton(self, -1, u"Tous les groupes", style=wx.RB_GROUP)
        self.radio_groupes_suivants = wx.RadioButton(self, -1, u"Uniquement les groupes suivants :")
        self.ctrl_groupes = CheckListBoxGroupes(self, self.IDactivite, self.IDunite)
        self.ctrl_groupes.MAJ() 
        
        self.label_repas = wx.StaticText(self, -1, u"Repas :")
        self.ctrl_repas = wx.CheckBox(self, -1, u"Repas inclus")
        self.label_restaurateur = wx.StaticText(self, -1, u"Restaurateur :")
        self.ctrl_restaurateur = CTRL_Restaurateur(self)
        self.bouton_restaurateur = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.label_incompat = wx.StaticText(self, -1, u"Incompatibilités :")
        self.ctrl_incompat = CheckListBoxIncompat(self, self.IDactivite, self.IDunite)
        self.ctrl_incompat.MAJ() 
        
        self.label_raccourci = wx.StaticText(self, -1, u"Touche raccourci :")
        self.ctrl_raccourci = CTRL_Raccourci(self)
        
        # Validité
        self.staticbox_validite_staticbox = wx.StaticBox(self, -1, u"Validité")
        self.radio_illimitee = wx.RadioButton(self, -1, u"Durant la période de validité de l'activité", style=wx.RB_GROUP)
        self.radio_limitee = wx.RadioButton(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.label_au = wx.StaticText(self, -1, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioGroupes, self.radio_groupes_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioGroupes, self.radio_groupes_suivants)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRepas, self.ctrl_repas)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRestaurateur, self.bouton_restaurateur)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_illimitee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_limitee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDunite != None :
            self.Importation() 
        
        self.OnRadioGroupes(None)
        self.OnCheckRepas(None)
        self.OnRadioValidite(None)

    def __set_properties(self):
        self.SetTitle(u"Saisie d'une unité")
        self.SetSize((650, -1))
        self.ctrl_nom.SetToolTipString(u"Saisissez ici le nom complet de l'unité")
        self.ctrl_abrege.SetMinSize((80, -1))
        self.ctrl_abrege.SetToolTipString(u"Saisissez ici le nom abrégé de l'unité")
        self.ctrl_type.SetToolTipString(u"Sélectionnez un type d'unité")
        self.ctrl_heure_debut.SetToolTipString(u"Saisissez l'heure minimale (Ex : 08:30)")
        self.ctrl_heure_fin.SetToolTipString(u"Saisissez l'heure maximale (Ex : 09:30)")
        self.ctrl_heure_debut_fixe.SetToolTipString(u"Cochez cette case si l'heure de début est obligatoirement celle-ci")
        self.ctrl_heure_fin_fixe.SetToolTipString(u"Cochez cette case si l'heure de fin est obligatoirement celle-ci")
        self.radio_groupes_tous.SetToolTipString(u"Cochez ici pour que tous les groupes bénéficient de cette unité")
        self.radio_groupes_suivants.SetToolTipString(u"Cochez ici pour sélectionner certains groupes")
        self.ctrl_repas.SetToolTipString(u"Cochez cette case si cette unité est ou comporte un repas")
        self.ctrl_restaurateur.SetToolTipString(u"Selectionnez un restaurateur")
        self.bouton_restaurateur.SetToolTipString(u"Cliquez ici pour accéder à la gestion des restaurateurs")
        self.ctrl_incompat.SetToolTipString(u"Cochez les unités qui sont incompatibles avec cette unité")
        self.radio_illimitee.SetToolTipString(u"Cochez ici si l'unité est valable sur toute la durée de validité de l'activité")
        self.radio_limitee.SetToolTipString(u"Cliquez ici pour définir une période de validité précise")
        self.ctrl_date_debut.SetToolTipString(u"Saisissez une date de début")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez une date de fin")
        self.ctrl_raccourci.SetToolTipString(u"La touche de raccourci est utile dans la grille de saisie des \nconsommations : Lorsque cette touche est maintenue enfoncée,\nune consommation de cette unité est automatiquement créée.")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")


    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_validite = wx.StaticBoxSizer(self.staticbox_validite_staticbox, wx.VERTICAL)
        grid_sizer_validite = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        staticbox_caract = wx.StaticBoxSizer(self.staticbox_caract_staticbox, wx.VERTICAL)
        grid_sizer_caract = wx.FlexGridSizer(rows=7, cols=2, vgap=15, hgap=5)
        grid_sizer_repas = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_restaurateur = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_groupes = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_horaires = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_abrege, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_abrege, 0, 0, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_caract.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.ctrl_type, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.label_horaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_debut, 0, 0, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_debut_fixe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.label_a, 0, wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer_horaires.Add(self.ctrl_heure_fin, 0, 0, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_fin_fixe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(grid_sizer_horaires, 1, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.label_groupes, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_groupes.Add(self.radio_groupes_tous, 0, 0, 0)
        grid_sizer_groupes.Add(self.radio_groupes_suivants, 0, 0, 0)
        grid_sizer_groupes.Add(self.ctrl_groupes, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_groupes.AddGrowableCol(0)
        grid_sizer_caract.Add(grid_sizer_groupes, 1, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.label_repas, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_repas.Add(self.ctrl_repas, 0, 0, 0)
        grid_sizer_restaurateur.Add((18, 18), 0, wx.EXPAND, 0)
        grid_sizer_restaurateur.Add(self.label_restaurateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_restaurateur.Add(self.ctrl_restaurateur, 0, wx.EXPAND, 0)
        grid_sizer_restaurateur.Add(self.bouton_restaurateur, 0, 0, 0)
        grid_sizer_restaurateur.AddGrowableCol(2)
        grid_sizer_repas.Add(grid_sizer_restaurateur, 1, wx.EXPAND, 0)
        grid_sizer_repas.AddGrowableCol(0)
        grid_sizer_caract.Add(grid_sizer_repas, 1, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.label_incompat, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_caract.Add(self.ctrl_incompat, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.label_raccourci, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.ctrl_raccourci, 0, wx.EXPAND, 0)
        grid_sizer_caract.AddGrowableCol(1)
        grid_sizer_caract.AddGrowableRow(4)
        staticbox_caract.Add(grid_sizer_caract, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_caract, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_validite.Add(self.radio_illimitee, 0, 0, 0)
        grid_sizer_dates.Add(self.radio_limitee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_validite.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        staticbox_validite.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_validite, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
        self.SetMinSize(self.GetSize())
        

    def OnRadioGroupes(self, event): 
        if self.radio_groupes_tous.GetValue() == True :
            self.ctrl_groupes.Enable(False)
        else:
            self.ctrl_groupes.Enable(True)

    def OnCheckRepas(self, event):
        if self.ctrl_repas.GetValue() == False :
            self.ctrl_restaurateur.Enable(False)
            self.bouton_restaurateur.Enable(False)
        else:
            self.ctrl_restaurateur.Enable(True)
            self.bouton_restaurateur.Enable(True)

    def OnBoutonRestaurateur(self, event): 
        import DLG_Restaurateurs
        dlg = DLG_Restaurateurs.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_restaurateur.MAJlisteDonnees() 

    def OnRadioValidite(self, event):
        if self.radio_illimitee.GetValue() == True :
            self.ctrl_date_debut.Enable(False)
            self.ctrl_date_fin.Enable(False)
        else:
            self.ctrl_date_debut.Enable(True)
            self.ctrl_date_fin.Enable(True)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Units")
    
    def GetIDunite(self):
        return self.IDunite
    
    def OnBoutonOk(self, event): 
        # Vérifie que la conversion de type est possible
        if self.IDunite != None :
            DB = GestionDB.DB()
            req = """SELECT IDindividu, date, COUNT(IDconso)
            FROM consommations 
            WHERE IDunite=%d
            GROUP BY IDindividu, date
            ;""" % self.IDunite
            DB.ExecuterReq(req)
            listeConsommations = DB.ResultatReq()
            DB.Close()
            listeDates = []
            for IDindividu, date, nbreConso in listeConsommations :
                if nbreConso > 1 :
                    dateDD = UTILS_Dates.DateEngEnDateDD(date)
                    listeDates.append(dateDD)
            listeDates.sort() 
            
            if len(listeDates) > 0 and self.typeUnite == "Multihoraires" and self.ctrl_type.GetType() != "Multihoraires" :
                periode = u"entre le %s et le %s" % (UTILS_Dates.DateDDEnFr(listeDates[0]), UTILS_Dates.DateDDEnFr(listeDates[-1]))
                dlg = wx.MessageDialog(self, u"Des consommations multiples ont déjà été saisies sur %d dates (%s) !\n\nIl est donc impossible de convertir cette unité multihoraire en un autre type d'unité." % (len(listeDates), periode), u"Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Sauvegarde
        etat = self.Sauvegarde() 
        if etat == False :
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def Sauvegarde(self):
        # Nom
        nom = self.ctrl_nom.GetValue() 
        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        abrege = self.ctrl_abrege.GetValue()
        if abrege == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom abrégé !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        type = self.ctrl_type.GetType()
        repas = int(self.ctrl_repas.GetValue())
        if repas == 1 :
            IDrestaurateur = self.ctrl_restaurateur.GetID()
        else:
            IDrestaurateur = None
        
        # Vérification des heures saisies
        heure_debut = self.ctrl_heure_debut.GetHeure()
        heure_fin = self.ctrl_heure_fin.GetHeure()

        if heure_debut != None and self.ctrl_heure_debut.Validation() == False :
            dlg = wx.MessageDialog(self, u"L'heure de début n'est pas valide !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_debut.SetFocus() 
            return False

        if heure_fin != None and self.ctrl_heure_fin.Validation() == False :
            dlg = wx.MessageDialog(self, u"L'heure de fin n'est pas valide !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_fin.SetFocus() 
            return False
        
        if type == "Multihoraires" and (heure_debut == None or heure_fin == False) :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement spécifier une heure de début et une heure de fin pour les unités de type 'Multihoraire' !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Validité
        if self.radio_illimitee.GetValue() == True :
            date_debut = "1977-01-01"
            date_fin = "2999-01-01"
        else:
            date_debut = self.ctrl_date_debut.GetDate()
            if date_debut == None :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de début de validité !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            date_fin = self.ctrl_date_fin.GetDate()
            if date_fin == None :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de fin de validité !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        touche_raccourci = self.ctrl_raccourci.GetCode()
        heure_debut_fixe = int(self.ctrl_heure_debut_fixe.GetValue())
        heure_fin_fixe = int(self.ctrl_heure_fin_fixe.GetValue())
    
        # Enregistrement
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("IDactivite", self.IDactivite ),
            ("nom", nom ),
            ("abrege", abrege ),
            ("type", type),
            ("heure_debut", heure_debut),
            ("heure_fin", heure_fin),
            ("repas", repas),
            ("IDrestaurateur", IDrestaurateur),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("touche_raccourci", touche_raccourci),
            ("heure_debut_fixe", heure_debut_fixe),
            ("heure_fin_fixe", heure_fin_fixe),
            ]

        if self.IDunite == None :
            # Recherche le numéro d'ordre
            req = """SELECT IDunite, ordre
            FROM unites WHERE IDactivite=%d
            ORDER BY ordre DESC LIMIT 1
            ;""" % self.IDactivite
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if len(listeTemp) == 0 : 
                ordre = 1
            else:
                ordre = listeTemp[0][1] + 1
            listeDonnees.append(("ordre", ordre ))
            self.IDunite = DB.ReqInsert("unites", listeDonnees)
            self.ctrl_groupes.IDunite = self.IDunite
            self.ctrl_incompat.IDunite = self.IDunite
        else:
            DB.ReqMAJ("unites", listeDonnees, "IDunite", self.IDunite)
        
        # Groupes
        if self.radio_groupes_tous.GetValue() == False :
            self.ctrl_groupes.Sauvegarde()
        else:
            DB.ReqDEL("unites_groupes", "IDunite", self.IDunite)
        
        # Incompatibilités
        self.ctrl_incompat.Sauvegarde() 
        
        DB.Close()
        return True

    def Importation(self):
        """ Importation des valeurs """
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin, 
        repas, IDrestaurateur, date_debut, date_fin, touche_raccourci, heure_debut_fixe, heure_fin_fixe
        FROM unites WHERE IDunite=%d;""" % self.IDunite
        db.ExecuterReq(req)
        listeTemp = db.ResultatReq()
        db.Close()
        if len(listeTemp) == 0 : return
        listeTemp = listeTemp[0]
        
        nom = listeTemp[1]
        abrege = listeTemp[2]
        type = listeTemp[3]
        self.typeUnite = type
        heure_debut = listeTemp[4]
        heure_fin = listeTemp[5]
        repas = listeTemp[6]
        IDrestaurateur = listeTemp[7]
        date_debut = listeTemp[8]
        date_fin = listeTemp[9]
        touche_raccourci = listeTemp[10]
        heure_debut_fixe = listeTemp[11]
        heure_fin_fixe = listeTemp[12]
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_abrege.SetValue(abrege)
        self.ctrl_type.SetType(type)
        self.ctrl_heure_debut.SetHeure(heure_debut)
        self.ctrl_heure_fin.SetHeure(heure_fin)
        self.ctrl_repas.SetValue(repas)
        self.ctrl_restaurateur.SetID(IDrestaurateur)
        if date_debut != "1977-01-01" and date_fin != "2999-01-01" :
            self.ctrl_date_debut.SetDate(date_debut)
            self.ctrl_date_fin.SetDate(date_fin)
            self.radio_limitee.SetValue(True)
            
        self.ctrl_groupes.Importation() 
        if len(self.ctrl_groupes.GetIDcoches()) > 0 :
            self.radio_groupes_suivants.SetValue(True)
            
        self.ctrl_incompat.Importation() 
        
        self.ctrl_raccourci.SetCode(touche_raccourci)
        
        self.ctrl_heure_debut_fixe.SetValue(heure_debut_fixe)
        self.ctrl_heure_fin_fixe.SetValue(heure_fin_fixe)
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1, IDunite=3)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
