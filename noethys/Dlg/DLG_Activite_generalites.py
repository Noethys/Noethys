#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_tel
from Ctrl import CTRL_Saisie_mail
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Logo
from Ol import OL_Responsables_activite

import GestionDB



class CTRL_Public(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 80))
        self.parent = parent
        self.data = []
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
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

# --------------------------------------------------------------------------------------------------------

class CTRL_Groupes_activite(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.Importation() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDtype_groupe_activite, nom, observations
        FROM types_groupes_activites
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeValeurs = []
        for IDtype_groupe_activite, nom, observations in listeDonnees :
            listeValeurs.append((IDtype_groupe_activite, nom, False)) 
        self.SetData(listeValeurs)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
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


# --------------------------------------------------------------------------------------------------------

class CTRL_Regie_facturation(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDregie, nom
        FROM factures_regies
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [_(u"Aucune régie"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDregie, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDregie, "nom" : nom}
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

    def GetNom(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["nom"]

# --------------------------------------------------------------------------------------------------------


class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panel_generalites", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        
        self.listeInitialeGroupes = []
        
        # Nom Activité
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de l'activité"))
        self.label_nom_complet = wx.StaticText(self, -1, _(u"Nom complet :"))
        self.ctrl_nom_complet = wx.TextCtrl(self, -1, u"")
        self.label_nom_abrege = wx.StaticText(self, -1, _(u"Nom abrégé :"))
        self.ctrl_nom_abrege = wx.TextCtrl(self, -1, u"")
        
        # Coords
        self.staticbox_coords_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.radio_coords_org = wx.RadioButton(self, -1, u"", style=wx.RB_GROUP)
        self.label_coords_org = wx.StaticText(self, -1, _(u"Identique à l'organisateur"))
        self.radio_coords_autres = wx.RadioButton(self, -1, u"")
        self.label_coords_autres = wx.StaticText(self, -1, _(u"Autres coordonnées :"))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_ville = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.label_tel = wx.StaticText(self, -1, _(u"Tél :"))
        self.ctrl_tel = CTRL_Saisie_tel.Tel(self, intitule=_(u"contact pour cette activité"))
        self.label_mail = wx.StaticText(self, -1, _(u"Email :"))
        self.ctrl_mail = CTRL_Saisie_mail.Mail(self)
        self.label_fax = wx.StaticText(self, -1, _(u"Fax :"))
        self.ctrl_fax = CTRL_Saisie_tel.Tel(self, intitule=_(u"fax"))
        self.label_site = wx.StaticText(self, -1, _(u"Site internet :"))
        self.ctrl_site = wx.TextCtrl(self, -1, u"")
        
        # Responsables
        self.staticbox_responsables_staticbox = wx.StaticBox(self, -1, _(u"Responsables de l'activité"))
        self.ctrl_responsables = OL_Responsables_activite.ListView(self, IDactivite=IDactivite, id=-1, name="OL_responsables", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_responsables.SetMinSize((-1, 40))
        self.ctrl_responsables.MAJ() 
        self.bouton_ajouter_responsable = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_responsable = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_responsable = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_defaut_responsable = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok.png"), wx.BITMAP_TYPE_ANY))

        # Code comptable
        self.staticbox_code_comptable_staticbox = wx.StaticBox(self, -1, _(u"Code comptable"))
        self.ctrl_code_comptable = wx.TextCtrl(self, -1, "")

        # Régie de facturation
        self.staticbox_regie_facturation_staticbox = wx.StaticBox(self, -1, _(u"Régie de facturation"))
        self.ctrl_regie_facturation = CTRL_Regie_facturation(self)

        # Groupes d'activités
        self.staticbox_groupes_staticbox = wx.StaticBox(self, -1, _(u"Regroupement d'activités"))
        self.ctrl_groupes = CTRL_Groupes_activite(self)
        self.ctrl_groupes.SetMinSize((320, 80))
        
        # Logo
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Logo"))
        self.radio_logo_org = wx.RadioButton(self, -1, u"Identique à l'organisateur", style=wx.RB_GROUP)
        self.radio_logo_autre = wx.RadioButton(self, -1, u"Autre logo :")
        self.bouton_modifier_logo = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_logo = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser_logo = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=self.bouton_modifier_logo.GetSize())

        # Validité
        self.staticbox_validite_staticbox = wx.StaticBox(self, -1, _(u"Dates de validité"))
        self.radio_illimitee = wx.RadioButton(self, -1, u"", style=wx.RB_GROUP)
        self.label_illimitee = wx.StaticText(self, -1, _(u"Illimitée"))
        self.radio_limitee = wx.RadioButton(self, -1, u"")
        self.label_validite_du = wx.StaticText(self, -1, u"Du")
        self.ctrl_validite_du = CTRL_Saisie_date.Date(self)
        self.label_validite_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_validite_au = CTRL_Saisie_date.Date(self)
        
        # Public
        self.staticbox_public_staticbox = wx.StaticBox(self, -1, _(u"Public"))
        self.ctrl_public = CTRL_Public(self)
        listePublic = [(1, _(u"Représentants"), False), (2, _(u"Enfants"), False),]
        self.ctrl_public.SetData(listePublic)
        self.ctrl_public.SetMinSize((-1, 40))
        self.staticbox_public_staticbox.Show(False)
        self.ctrl_public.Show(False)

        # Nombre max d'inscrits
        self.staticbox_limitation_inscrits_staticbox = wx.StaticBox(self, -1, _(u"Limitation du nombre d'inscrits"))
        self.check_limitation_inscrits = wx.CheckBox(self, -1, _(u"Nombre d'inscrits max. :"))
        self.ctrl_limitation_inscrits = wx.SpinCtrl(self, -1, size=(80, -1), min=1, max=99999)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCoords, self.radio_coords_org)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCoords, self.radio_coords_autres)
        self.Bind(wx.EVT_BUTTON, self.OnAjouterResponsable, self.bouton_ajouter_responsable)
        self.Bind(wx.EVT_BUTTON, self.OnModifierResponsable, self.bouton_modifier_responsable)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerResponsable, self.bouton_supprimer_responsable)
        self.Bind(wx.EVT_BUTTON, self.OnResponsableDefaut, self.bouton_defaut_responsable)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLogo, self.radio_logo_org)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLogo, self.radio_logo_autre)
        self.Bind(wx.EVT_BUTTON, self.OnModifierLogo, self.bouton_modifier_logo)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerLogo, self.bouton_supprimer_logo)
        self.Bind(wx.EVT_BUTTON, self.OnVisualiserLogo, self.bouton_visualiser_logo)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_illimitee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_limitee)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckLimitationInscrits, self.check_limitation_inscrits)
        
        # Importation
        if nouvelleActivite == False :
            self.Importation() 
        
        # Initialisation des contrôles
        self.OnRadioCoords(None) 
        self.OnRadioLogo(None) 
        self.OnRadioValidite(None) 
        self.OnCheckLimitationInscrits(None)
        

    def __set_properties(self):
        self.ctrl_nom_complet.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom complet de l'activité")))
        self.ctrl_nom_abrege.SetMinSize((60, -1))
        self.ctrl_nom_abrege.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom abrégé de l'activité")))
        self.radio_coords_org.SetToolTip(wx.ToolTip(_(u"Selectionnez 'Autres coordonnées' si vous souhaitez attribuer des coordonnées différentes de celles de l'organisateur")))
        self.radio_coords_autres.SetToolTip(wx.ToolTip(_(u"Selectionnez 'Autres coordonnées' si vous souhaitez attribuer des coordonnées différentes de celles de l'organisateur")))
        self.ctrl_rue.SetToolTip(wx.ToolTip(_(u"Saisissez l'adresse de l'activité")))
        self.ctrl_site.SetToolTip(wx.ToolTip(_(u"Saisissez l'adresse du site internet de l'activité")))
        self.ctrl_responsables.SetToolTip(wx.ToolTip(_(u"Liste des responsables de l'activité")))
        self.bouton_ajouter_responsable.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un nom de responsable")))
        self.bouton_modifier_responsable.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le nom sélectionné dans la liste")))
        self.bouton_supprimer_responsable.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le nom sélectionné dans la liste")))
        self.bouton_defaut_responsable.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour définir le responsable sélectionné dans la liste par défaut")))
        self.radio_logo_org.SetToolTip(wx.ToolTip(_(u"Selectionnez 'Autre logo' pour attribuer à l'activité un logo différent de celui de l'organisateur")))
        self.radio_logo_autre.SetToolTip(wx.ToolTip(_(u"Selectionnez 'Autre logo' pour attribuer à l'activité un logo différent de celui de l'organisateur")))
        self.bouton_modifier_logo.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter ou modifier un logo pour cette activité")))
        self.bouton_supprimer_logo.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le logo")))
        self.bouton_visualiser_logo.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser le logo en taille réelle")))
        self.radio_illimitee.SetToolTip(wx.ToolTip(_(u"Selectionnez 'Illimitee' si l'activité est un accueil de loisirs")))
        self.radio_limitee.SetToolTip(wx.ToolTip(_(u"Saisissez une periode de validité si l'activite fonctionne uniquement sur une période donnée")))
        self.ctrl_validite_du.SetToolTip(wx.ToolTip(_(u"Saisissez une date de debut de validité")))
        self.ctrl_validite_au.SetToolTip(wx.ToolTip(_(u"Saisissez ici une date de fin de validité")))
        self.ctrl_public.SetToolTip(wx.ToolTip(_(u"Cochez les publics autorisés à être inscrit à cette activité")))
        self.check_limitation_inscrits.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour définir un nombre maximal d'inscrits pour cette activité (Utile uniquement pour les activités à durée limitée)")))
        self.ctrl_limitation_inscrits.SetToolTip(wx.ToolTip(_(u"Saisissez le nombre maximal d'inscrits de cette activité (Utile uniquement pour les activités à durée limitée)")))
        self.ctrl_code_comptable.SetToolTip(wx.ToolTip(_(u"Saisissez un code comptable si vous souhaitez utiliser l'export des écritures comptables vers des logiciels de compta")))
        self.ctrl_regie_facturation.SetToolTip(wx.ToolTip(_(u"Sélectionnez une régie de facturation")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # ----------- Sizer gauche ----------------

        grid_sizer_gauche = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)

        # Nom activité
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom_complet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom_complet, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_nom_abrege, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom_abrege, 0, 0, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_nom, 1, wx.EXPAND, 0)

        # Validité
        staticbox_validite = wx.StaticBoxSizer(self.staticbox_validite_staticbox, wx.VERTICAL)
        grid_sizer_validite = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_validite_limitee = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_validite.Add(self.radio_illimitee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.label_illimitee, 0, 0, 0)
        grid_sizer_validite.Add(self.radio_limitee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite_limitee.Add(self.label_validite_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite_limitee.Add(self.ctrl_validite_du, 0, 0, 0)
        grid_sizer_validite_limitee.Add(self.label_validite_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite_limitee.Add(self.ctrl_validite_au, 0, 0, 0)
        grid_sizer_validite.Add(grid_sizer_validite_limitee, 1, wx.EXPAND, 0)
        staticbox_validite.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_validite, 1, wx.EXPAND, 0)

        # Regroupement d'activités
        staticbox_groupes = wx.StaticBoxSizer(self.staticbox_groupes_staticbox, wx.VERTICAL)
        staticbox_groupes.Add(self.ctrl_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_groupes, 1, wx.EXPAND, 0)

        # Limitation nombre inscrits
        staticbox_limitation_inscrits = wx.StaticBoxSizer(self.staticbox_limitation_inscrits_staticbox, wx.HORIZONTAL)
        staticbox_limitation_inscrits.Add(self.check_limitation_inscrits, 0, wx.ALL|wx.EXPAND, 5)
        staticbox_limitation_inscrits.Add(self.ctrl_limitation_inscrits, 0, wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_limitation_inscrits, 1, wx.EXPAND, 0)

        # Régie de facturation
        staticbox_regie_facturation = wx.StaticBoxSizer(self.staticbox_regie_facturation_staticbox, wx.HORIZONTAL)
        staticbox_regie_facturation.Add(self.ctrl_regie_facturation, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_regie_facturation, 1, wx.EXPAND, 0)

        # Code comptable
        staticbox_code_comptable = wx.StaticBoxSizer(self.staticbox_code_comptable_staticbox, wx.HORIZONTAL)
        staticbox_code_comptable.Add(self.ctrl_code_comptable, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_code_comptable, 1, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(2)
        
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        
        # ----------- Sizer droit ----------------

        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Responsables
        staticbox_responsables = wx.StaticBoxSizer(self.staticbox_responsables_staticbox, wx.VERTICAL)
        grid_sizer_responsables = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_responsables_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_responsables.Add(self.ctrl_responsables, 1, wx.EXPAND, 0)
        grid_sizer_responsables_boutons.Add(self.bouton_ajouter_responsable, 0, 0, 0)
        grid_sizer_responsables_boutons.Add(self.bouton_modifier_responsable, 0, 0, 0)
        grid_sizer_responsables_boutons.Add(self.bouton_supprimer_responsable, 0, 0, 0)
        grid_sizer_responsables_boutons.Add(self.bouton_defaut_responsable, 0, 0, 0)
        grid_sizer_responsables.Add(grid_sizer_responsables_boutons, 1, wx.EXPAND, 0)
        grid_sizer_responsables.AddGrowableRow(0)
        grid_sizer_responsables.AddGrowableCol(0)
        staticbox_responsables.Add(grid_sizer_responsables, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_responsables, 1, wx.EXPAND, 0)


        # Public
        staticbox_public = wx.StaticBoxSizer(self.staticbox_public_staticbox, wx.VERTICAL)
        staticbox_public.Add(self.ctrl_public, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_public, 1, wx.EXPAND, 0)

        # Logo
        staticbox_logo = wx.StaticBoxSizer(self.staticbox_logo_staticbox, wx.VERTICAL)
        grid_sizer_logo = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_logo.Add(self.radio_logo_org, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_logo.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_logo.Add(self.radio_logo_autre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_logo.Add(self.ctrl_logo, 0, wx.EXPAND, 0)
        grid_sizer_logo.Add(self.bouton_modifier_logo, 0, 0, 0)
        grid_sizer_logo.Add(self.bouton_supprimer_logo, 0, 0, 0)
        grid_sizer_logo.Add(self.bouton_visualiser_logo, 0, 0, 0)
        staticbox_logo.Add(grid_sizer_logo, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_logo, 1, wx.EXPAND, 0)

        # Coordonnées
        staticbox_coords = wx.StaticBoxSizer(self.staticbox_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_coords_autres = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_fax = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_tel = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_coords.Add(self.radio_coords_org, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.label_coords_org, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.radio_coords_autres, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.label_coords_autres, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_coords_autres.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords_autres.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_coords_autres.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords_autres.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_coords_autres.Add(self.label_tel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_tel, 0, 0, 0)
        grid_sizer_tel.Add(self.label_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_mail, 0, wx.EXPAND, 0)
        grid_sizer_tel.AddGrowableCol(2)
        grid_sizer_coords_autres.Add(grid_sizer_tel, 1, wx.EXPAND, 0)
        grid_sizer_coords_autres.Add(self.label_fax, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fax.Add(self.ctrl_fax, 0, 0, 0)
        grid_sizer_fax.Add(self.label_site, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fax.Add(self.ctrl_site, 0, wx.EXPAND, 0)
        grid_sizer_fax.AddGrowableCol(2)
        grid_sizer_coords_autres.Add(grid_sizer_fax, 1, wx.EXPAND, 0)
        grid_sizer_coords_autres.AddGrowableCol(1)
        grid_sizer_coords.Add(grid_sizer_coords_autres, 1, wx.EXPAND, 0)
        grid_sizer_coords.AddGrowableCol(1)
        staticbox_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_coords, 1, wx.EXPAND, 0)



        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadioCoords(self, event):
        if self.radio_coords_org.GetValue() == True :
            etat = False
        else:
            etat = True
        self.ctrl_rue.Enable(etat)
        self.label_rue.Enable(etat)
        self.ctrl_ville.Enable(etat)
        self.label_ville.Enable(etat)
        self.ctrl_tel.Enable(etat)
        self.label_tel.Enable(etat)
        self.ctrl_fax.Enable(etat)
        self.label_fax.Enable(etat)
        self.ctrl_mail.Enable(etat)
        self.label_mail.Enable(etat)
        self.ctrl_site.Enable(etat)
        self.label_site.Enable(etat)

    def OnAjouterResponsable(self, event): 
        self.ctrl_responsables.Ajouter(None)

    def OnModifierResponsable(self, event): 
        self.ctrl_responsables.Modifier(None)

    def OnSupprimerResponsable(self, event): 
        self.ctrl_responsables.Supprimer(None)

    def OnResponsableDefaut(self, event): 
        self.ctrl_responsables.SetDefaut(None)

    def OnRadioLogo(self, event): 
        if self.radio_logo_org.GetValue() == True :
            etat = False
        else:
            etat = True
        self.ctrl_logo.Enable(etat)
        self.bouton_modifier_logo.Enable(etat)
        self.bouton_supprimer_logo.Enable(etat)
        self.bouton_visualiser_logo.Enable(etat)

    def OnModifierLogo(self, event): 
        self.ctrl_logo.Ajouter()

    def OnSupprimerLogo(self, event): 
        self.ctrl_logo.Supprimer()

    def OnVisualiserLogo(self, event): 
        self.ctrl_logo.Visualiser()

    def OnRadioValidite(self, event): 
        if self.radio_illimitee.GetValue() == True :
            etat = False
        else:
            etat = True
        self.ctrl_validite_du.Enable(etat)
        self.label_validite_du.Enable(etat)
        self.ctrl_validite_au.Enable(etat)
        self.label_validite_au.Enable(etat)
    
    def OnCheckLimitationInscrits(self, event):
        self.ctrl_limitation_inscrits.Enable(self.check_limitation_inscrits.GetValue())
        
    def Importation(self):
        """ Importation des données """
        db = GestionDB.DB()
        req = """SELECT nom, abrege, coords_org, rue, cp, ville, tel, fax, mail, site, 
        logo_org, logo, date_debut, date_fin, public, nbre_inscrits_max, code_comptable, regie
        FROM activites 
        WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        activite = listeDonnees[0]
        
        # Nom
        self.ctrl_nom_complet.SetValue(activite[0])
        if activite[1] != None : self.ctrl_nom_abrege.SetValue(activite[1])
        
        # Coords
        if activite[2] == 1 :
            self.radio_coords_org.SetValue(True)
        else: 
            self.radio_coords_autres.SetValue(True)
            if activite[3] != None : self.ctrl_rue.SetValue(activite[3])
            self.ctrl_ville.SetValueCP(activite[4])
            self.ctrl_ville.SetValueVille(activite[5])
            self.ctrl_tel.SetNumero(activite[6])
            self.ctrl_fax.SetNumero(activite[7])
            self.ctrl_mail.SetMail(activite[8])
            if activite[9] != None : self.ctrl_site.SetValue(activite[9])
            
        # Regroupement d'activités
        DB = GestionDB.DB()
        req = """SELECT IDgroupe_activite, IDtype_groupe_activite
        FROM groupes_activites
        WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeRegroupements = DB.ResultatReq()
        DB.Close()
        listeIDgroupes = []
        for IDgroupe_activite, IDtype_groupe_activite in listeRegroupements :
            listeIDgroupes.append(IDtype_groupe_activite)
        self.ctrl_groupes.SetIDcoches(listeIDgroupes)
        self.listeInitialeGroupes = list(listeIDgroupes)
        
        # Logos
        if activite[10] == 1 :
            self.radio_logo_org.SetValue(True)
        else:
            self.radio_logo_autre.SetValue(True)
            img = activite[11]
            if img != None :
                self.ctrl_logo.ChargeFromBuffer(img)
                
        # Validité
        date_debut = activite[12]
        date_fin = activite[13]
        if date_debut == "1977-01-01" and date_fin == "2999-01-01" :
            self.radio_illimitee.SetValue(True)
        else:
            self.radio_limitee.SetValue(True)
            self.ctrl_validite_du.SetDate(date_debut)
            self.ctrl_validite_au.SetDate(date_fin)
            
        # Public
        publicTemp = activite[14]
        if publicTemp != None and publicTemp != "" :
            listePublic = publicTemp.split("-")
            listePublic2 = []
            for ID in listePublic :
                listePublic2.append(int(ID))
            self.ctrl_public.SetIDcoches(listePublic2)
            
        # Nbre inscrits max
        nbre_inscrits_max = activite[15]
        if nbre_inscrits_max != None :
            self.check_limitation_inscrits.SetValue(True)
            self.ctrl_limitation_inscrits.SetValue(nbre_inscrits_max)
            
        # Code comptable
        code_comptable = activite[16]
        if code_comptable != None :
            self.ctrl_code_comptable.SetValue(code_comptable)
            
        # Régie de facturation
        regie = activite[17]
        if regie != None :
            self.ctrl_regie_facturation.SetID(regie)
        
    def Validation(self):
        # Nom
        if self.ctrl_nom_complet.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Le nom de l'activité doit être obligatoirement saisi !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom_complet.SetFocus() 
            return False
        if self.ctrl_nom_abrege.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Le nom abrégé de l'activité doit être obligatoirement saisi !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom_abrege.SetFocus() 
            return False
        # Public
        public = self.ctrl_public.GetIDcoches()
        # if len(public) == 0 :
        #     dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un type de public !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
        #     dlg.ShowModal()
        #     dlg.Destroy()
        #     return False
        # Dates de validité
        if self.radio_limitee.GetValue() == True :
            if self.ctrl_validite_du.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"La date de début de validité ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_validite_du.SetFocus()
                return False
            if self.ctrl_validite_du.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"La date de début de validité n'a pas été spécifiée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_validite_du.SetFocus()
                return False
            if self.ctrl_validite_au.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"La date de fin de validité ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_validite_au.SetFocus()
                return False
            if self.ctrl_validite_au.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"La date de fin de validité n'a pas été spécifiée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_validite_au.SetFocus()
                return False
            if self.ctrl_validite_du.GetDate() > self.ctrl_validite_au.GetDate() :
                dlg = wx.MessageDialog(self, _(u"La date de validité de début ne peut pas être supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_validite_du.SetFocus()
                return False

        # Logo
        logo_org = int(self.radio_logo_org.GetValue())
        if logo_org == 0 :
            if self.ctrl_logo.GetBuffer() == None :
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné un logo personnalisé pour cette activité mais vous n'en avez sélectionné aucun !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        # Sauvegarde
        self.Sauvegarde() 
        
        return True
    
    def Sauvegarde(self):
        DB = GestionDB.DB()
        nom = self.ctrl_nom_complet.GetValue()
        abrege = self.ctrl_nom_abrege.GetValue()
        coords_org = int(self.radio_coords_org.GetValue())
        if coords_org == 0 :
            rue = self.ctrl_rue.GetValue() 
            cp = self.ctrl_ville.GetValueCP()
            ville = self.ctrl_ville.GetValueVille()
            tel = self.ctrl_tel.GetNumero()
            fax = self.ctrl_fax.GetNumero()
            mail = self.ctrl_mail.GetMail()
            site = self.ctrl_site.GetValue()
        else:
            rue = None
            cp = None
            ville = None
            tel = None
            fax = None
            mail = None
            site = None
        logo_org = int(self.radio_logo_org.GetValue())
        validiteIllimitee = int(self.radio_illimitee.GetValue())
        if validiteIllimitee == 1 :
            date_debut = "1977-01-01"
            date_fin = "2999-01-01"
        else:
            date_debut = self.ctrl_validite_du.GetDate()
            date_fin =self.ctrl_validite_au.GetDate()
        
        # Regroupements d'activités
        listeIDGroupes = self.ctrl_groupes.GetIDcoches()
        for IDtype_groupe_activite in listeIDGroupes :
            if IDtype_groupe_activite not in self.listeInitialeGroupes :
                DB.ReqInsert("groupes_activites", [("IDtype_groupe_activite", IDtype_groupe_activite), ("IDactivite", self.IDactivite),])
        for IDtype_groupe_activite in self.listeInitialeGroupes :
            if IDtype_groupe_activite not in listeIDGroupes :
                req = """
                DELETE FROM groupes_activites 
                WHERE IDactivite=%d AND IDtype_groupe_activite=%d
                ;""" % (self.IDactivite, IDtype_groupe_activite)
                DB.ExecuterReq(req)
        self.listeInitialeGroupes = listeIDGroupes
        
        # Public
        listePublic = self.ctrl_public.GetIDcoches()
        listePublic2 = []
        for ID in listePublic :
            listePublic2.append(str(ID))
        public = "-".join(listePublic2)
        
        # Nbre inscrits max
        if self.check_limitation_inscrits.GetValue() == True :
            nbre_inscrits_max = self.ctrl_limitation_inscrits.GetValue()
        else :
            nbre_inscrits_max = None
        
        # Code comptable
        code_comptable = self.ctrl_code_comptable.GetValue() 
        
        # Régie de facturation
        regie = self.ctrl_regie_facturation.GetID()
        
        # Enregistrement
        listeDonnees = [    
                ("nom", nom),
                ("abrege", abrege),
                ("coords_org", coords_org),
                ("rue", rue),
                ("cp", cp),
                ("ville", ville),
                ("tel", tel),
                ("fax", fax),
                ("mail", mail),
                ("site", site),
                ("logo_org", logo_org),
                ("date_debut", date_debut),
                ("date_fin", date_fin),
                ("public", public),
                ("nbre_inscrits_max", nbre_inscrits_max),
                ("code_comptable", code_comptable),
                ("regie", regie),
            ]
        DB.ReqMAJ("activites", listeDonnees, "IDactivite", self.IDactivite)
        
        # Sauvegarde du logo
        if logo_org == 0 :
            if self.ctrl_logo.estModifie == True :
                bmp = self.ctrl_logo.GetBuffer() 
                if bmp != None :
                    DB.MAJimage(table="activites", key="IDactivite", IDkey=self.IDactivite, blobImage=bmp, nomChampBlob="logo")
                else:
                    DB.ReqMAJ("activites", [("logo", None),], "IDactivite", self.IDactivite)
        else:
            DB.ReqMAJ("activites", [("logo", None),], "IDactivite", self.IDactivite)
            
        DB.Close()



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=1)
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