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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Selection_activites
from Ol import OL_Etat_nomin_selections
import DLG_Etat_nomin_resultats
from Utils import UTILS_Parametres


class CTRL_Periode(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        # Contrôles
        self.label_date_debut = wx.StaticText(self, -1, u"Du :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au :"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        # Layout
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer)
        self.Layout()
        # Init Contrôles
        dateDuJour = datetime.date.today()
        self.ctrl_date_debut.SetDate(datetime.date(dateDuJour.year, 1, 1))
        self.ctrl_date_fin.SetDate(datetime.date(dateDuJour.year, 12, 31))
    
    def Validation(self):
        if self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de validité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut
            return False
        if self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de validité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut
            return False
        return True
    
    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()
    
    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate()
        
# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeGroupes = []
        self.dictGroupes = {}
        
    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeGroupes, self.dictGroupes = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeGroupes = []
        dictGroupes = {}
        if len(self.listeActivites) == 0 :
            return listeGroupes, dictGroupes 

        # Condition Activités
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        DB = GestionDB.DB()
        req = """SELECT IDgroupe, groupes.IDactivite, groupes.nom, activites.abrege
        FROM groupes
        LEFT JOIN activites ON activites.IDactivite = groupes.IDactivite
        WHERE groupes.IDactivite IN %s
        ORDER BY groupes.nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDgroupe, IDactivite, nom, abregeActivite in listeDonnees :
            label = u"%s (%s)" % (nom, abregeActivite)
            dictTemp = { "nom" : label, "IDactivite" : IDactivite}
            dictGroupes[IDgroupe] = dictTemp
            listeGroupes.append((label, IDgroupe))
        listeGroupes.sort()
        return listeGroupes, dictGroupes

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDgroupe in self.listeGroupes :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeGroupes)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeGroupes[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            ID = self.listeGroupes[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeGroupes(self):
        return self.GetIDcoches() 
    
    def GetDictGroupes(self):
        return self.dictGroupes
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeCategories = []
        self.dictCategories = {}
        
    def SetActivites(self, listeActivites=None):
        self.listeActivites = listeActivites
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeCategories, self.dictCategories = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeCategories = []
        dictCategories = {}
        if len(self.listeActivites) == 0 :
            return listeCategories, dictCategories 

        # Condition Activités
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, categories_tarifs.IDactivite, categories_tarifs.nom, activites.abrege
        FROM categories_tarifs
        LEFT JOIN activites ON activites.IDactivite = categories_tarifs.IDactivite
        WHERE categories_tarifs.IDactivite IN %s
        ORDER BY categories_tarifs.nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDcategorie_tarif, IDactivite, nom, abregeActivite in listeDonnees :
            label = u"%s (%s)" % (nom, abregeActivite)
            dictTemp = { "nom" : label, "IDactivite" : IDactivite}
            dictCategories[IDcategorie_tarif] = dictTemp
            listeCategories.append((label, IDcategorie_tarif))
        listeCategories.sort()
        return listeCategories, dictCategories

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDcategorie_tarif in self.listeCategories :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeCategories)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeCategories[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeCategories)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeCategories)):
            ID = self.listeCategories[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeCategories(self):
        return self.GetIDcoches() 
    
    def GetDictCategories(self):
        return self.dictCategories
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Caisses(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeCaisses = []
        self.dictCaisses = {}
        self.MAJ() 
        self.CocheTout() 

    def MAJ(self):
        self.listeCaisses, self.dictCaisses = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeCaisses = [(_(u"Caisse non spécifiée"), 0),]
        dictCaisses = {"nom":_(u"Caisse non spécifiée"), "IDcaisse":0}

        DB = GestionDB.DB()
        req = """SELECT IDcaisse, nom
        FROM caisses
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDcaisse, nom in listeDonnees :
            dictTemp = { "nom" : nom, "IDcaisse" : IDcaisse}
            dictCaisses[IDcaisse] = dictTemp
            listeCaisses.append((nom, IDcaisse))
        listeCaisses.sort()
        return listeCaisses, dictCaisses

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 1
        for nom, IDcaisse in self.listeCaisses :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeCaisses)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeCaisses[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeCaisses)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeCaisses)):
            ID = self.listeCaisses[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeCaisses(self):
        return self.GetIDcoches() 
    
    def GetDictCaisses(self):
        return self.dictCaisses

        
# ---------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Age(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent

        self.radio_tous = wx.RadioButton(self, -1, _(u"Tous les individus"), style=wx.RB_GROUP)
        self.radio_dates = wx.RadioButton(self, -1, _(u"Nés entre le"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.label_separation1 = wx.StaticText(self, -1, _(u"et le"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        self.radio_age = wx.RadioButton(self, -1, _(u"Age entre"))
        self.ctrl_age_min = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.ctrl_age_min.SetMinSize((60, -1))

        self.label_separation2 = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_age_max = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.ctrl_age_max.SetMinSize((60, -1))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_age = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.radio_tous, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.radio_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_separation1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        grid_sizer_age.Add(self.radio_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_age.Add(self.ctrl_age_min, 0, 0, 0)
        grid_sizer_age.Add(self.label_separation2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_age.Add(self.ctrl_age_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_age, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_dates)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_age)
        
        # Init contrôles
        self.OnRadio(None)

    def OnRadio(self, event): 
        self.ctrl_date_debut.Enable(self.radio_dates.GetValue())
        self.ctrl_date_fin.Enable(self.radio_dates.GetValue())
        self.ctrl_age_min.Enable(self.radio_age.GetValue())
        self.ctrl_age_max.Enable(self.radio_age.GetValue())
    
    def Validation(self):
        if self.radio_dates.GetValue() == True :
            if self.ctrl_date_debut.GetDate() == None or self.ctrl_date_fin.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"L'intervalle de dates de naissance semble incorrect !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True
    
    def GetCondition(self):
        if self.radio_tous.GetValue() == True :
            return None
        if self.radio_dates.GetValue() == True :
            return ("DATES", self.ctrl_date_debut.GetDate(), self.ctrl_date_fin.GetDate())
        if self.radio_age.GetValue() == True :
            return ("AGES", self.ctrl_age_min.GetValue(), self.ctrl_age_max.GetValue())


# --------------------------------------------------------------------------------------------------------------------------




class CTRL_QF(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        # Contrôles
        self.radio_tous = wx.RadioButton(self, -1, _(u"Tous les quotients"), style=wx.RB_GROUP)
        self.radio_sans = wx.RadioButton(self, -1, _(u"Sans quotient"))
        self.radio_qf = wx.RadioButton(self, -1, _(u"Entre"))
        self.ctrl_qf_min = wx.SpinCtrl(self, -1, "", min=0, max=99999)
        self.ctrl_qf_min.SetMinSize((70, -1))
        self.label_separation = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_qf_max = wx.SpinCtrl(self, -1, "", min=0, max=99999)
        self.ctrl_qf_max.SetMinSize((70, -1))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_qf = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.radio_tous, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.radio_sans, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_qf.Add(self.radio_qf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_qf.Add(self.ctrl_qf_min, 0, 0, 0)
        grid_sizer_qf.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_qf.Add(self.ctrl_qf_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_qf, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sans)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_qf)
        
        # Init contrôles
        self.OnRadio(None)

    def OnRadio(self, event): 
        self.ctrl_qf_min.Enable(self.radio_qf.GetValue())
        self.ctrl_qf_max.Enable(self.radio_qf.GetValue())

    def GetCondition(self):
        if self.radio_tous.GetValue() == True :
            return None
        if self.radio_sans.GetValue() == True :
            return "SANS"
        if self.radio_qf.GetValue() == True :
            return (self.ctrl_qf_min.GetValue(), self.ctrl_qf_max.GetValue())


# --------------------------------------------------------------------------------------------------------------------------

class CTRL_Profil(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.Select(0)
        
    def MAJ(self):
        selectionActuelle = self.GetID()
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        # Re-sélection après MAJ
        if selectionActuelle != None :
            self.SetID(selectionActuelle)
                                        
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDprofil, label
        FROM etat_nomin_profils
        ORDER BY label;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 0
        for IDprofil, label in listeDonnees :
            listeItems.append(label)
            self.dictDonnees[index] = {"ID" : IDprofil}
            index += 1
        return listeItems

    def SetID(self, ID=None):
        for index, values in self.dictDonnees.iteritems():
            if values != None and values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
            
# -------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Commencez par créer un profil de liste afin de constituer une liste de champs persistante. Vous pouvez sélectionner les champs prédéfinis ou paramétrer des champs personnalisés en fonction de vos besoins. Sélectionnez enfin des paramètres conditionnels avant de lancer la création de la liste de données.")
        titre = _(u"Etat nominatif des consommations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Tableaux.png")
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.ctrl_periode = CTRL_Periode(self)
        
        # Activités
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        self.ctrl_activites.SetMinSize((240, -1))

        # Groupes
        self.box_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_Groupes(self)

        # Age
        self.box_age_staticbox = wx.StaticBox(self, -1, _(u"Age"))
        self.ctrl_age = CTRL_Age(self)

        # Caisse
        self.box_caisses_staticbox = wx.StaticBox(self, -1, _(u"Caisses"))
        self.ctrl_caisses = CTRL_Caisses(self)

        # QF
        self.box_qf_staticbox = wx.StaticBox(self, -1, _(u"Quotient familial"))
        self.ctrl_qf = CTRL_QF(self)
        
        # Catégories de tarifs
        self.box_categories_staticbox = wx.StaticBox(self, -1, _(u"Catégories de tarifs"))
        self.ctrl_categories = CTRL_Categories(self)
        
        # Champs
        self.box_champs_staticbox = wx.StaticBox(self, -1, _(u"Champs"))
        
        self.label_profil = wx.StaticText(self, -1, _(u"Profil :"))
        self.ctrl_profil = CTRL_Profil(self)
        self.bouton_profils = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.label_champs = wx.StaticText(self, -1, _(u"Champs :"))
        self.ctrl_champs = OL_Etat_nomin_selections.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixProfil, self.ctrl_profil)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonProfils, self.bouton_profils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMonter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDescendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init
        self.OnChoixProfil(None)
        
        wx.CallAfter(self.AfficheAvertissement)

    def __set_properties(self):
        self.ctrl_profil.SetToolTipString(_(u"Selectionnez un profil de liste"))
        self.bouton_profils.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des profils"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la liste des champs"))
        self.bouton_monter.SetToolTipString(_(u"Cliquez ici pour monter le champ sélectionné"))
        self.bouton_descendre.SetToolTipString(_(u"Cliquez ici pour descendre le champ sélectionné"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour afficher les resultats"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((800, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_haut = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_haut_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_haut_milieu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_haut_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Période
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        box_periode.Add(self.ctrl_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_periode, 1, wx.EXPAND, 0)
        
        # Activités
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        box_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_activites, 1, wx.EXPAND, 0)
        
        # Groupes
        box_groupes = wx.StaticBoxSizer(self.box_groupes_staticbox, wx.VERTICAL)
        box_groupes.Add(self.ctrl_groupes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_groupes, 1, wx.EXPAND, 0)
        
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Caisses
        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        box_categories.Add(self.ctrl_categories, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut_gauche.Add(box_categories, 1, wx.EXPAND, 0)

        # Age
        box_age = wx.StaticBoxSizer(self.box_age_staticbox, wx.VERTICAL)
        box_age.Add(self.ctrl_age, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut_gauche.Add(box_age, 1, wx.EXPAND, 0)
        
        grid_sizer_haut_gauche.AddGrowableRow(0)
        grid_sizer_haut_gauche.AddGrowableCol(0)
        grid_sizer_haut_contenu.Add(grid_sizer_haut_gauche, 1, wx.EXPAND, 0)
        
        # QF
        box_qf = wx.StaticBoxSizer(self.box_qf_staticbox, wx.VERTICAL)
        box_qf.Add(self.ctrl_qf, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut_milieu.Add(box_qf, 1, wx.EXPAND, 0)
        
        # Catégories
        box_caisses = wx.StaticBoxSizer(self.box_caisses_staticbox, wx.VERTICAL)
        box_caisses.Add(self.ctrl_caisses, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut_milieu.Add(box_caisses, 1, wx.EXPAND, 0)


        grid_sizer_haut_milieu.AddGrowableRow(1)
        grid_sizer_haut_milieu.AddGrowableCol(0)
        grid_sizer_haut_contenu.Add(grid_sizer_haut_milieu, 1, wx.EXPAND, 0)
        grid_sizer_haut_contenu.AddGrowableRow(0)
        grid_sizer_haut_contenu.AddGrowableCol(0)
        grid_sizer_haut_contenu.AddGrowableCol(1)
        grid_sizer_haut_contenu.AddGrowableCol(2)
        grid_sizer_haut.Add(grid_sizer_haut_contenu, 1, wx.EXPAND, 0)
        
        # Champs
        box_champs = wx.StaticBoxSizer(self.box_champs_staticbox, wx.VERTICAL)
        grid_sizer_champs = wx.FlexGridSizer(rows=2, cols=3, vgap=10, hgap=5)

        grid_sizer_champs.Add(self.label_profil, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_champs.Add(self.ctrl_profil, 0, wx.EXPAND, 0)
        grid_sizer_champs.Add(self.bouton_profils, 0, 0, 0)
        grid_sizer_champs.Add(self.label_champs, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_champs.Add(self.ctrl_champs, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_descendre, 0, 0, 0)

        grid_sizer_champs.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_champs.AddGrowableRow(1)
        grid_sizer_champs.AddGrowableCol(1)
        box_champs.Add(grid_sizer_champs, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_champs, 1, wx.EXPAND, 0)
        
        grid_sizer_haut.AddGrowableRow(1)
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def MAJlisteChamps(self):
        IDprofil = self.ctrl_profil.GetID()
        if IDprofil == None : IDprofil = 0
        date_debut = self.ctrl_periode.GetDateDebut() 
        date_fin = self.ctrl_periode.GetDateFin() 
        listeActivites = self.ctrl_activites.GetActivites()
        self.ctrl_champs.SetParametres(IDprofil=IDprofil, dateMin=date_debut, dateMax=date_fin, listeActivites=listeActivites)
        self.ctrl_champs.MAJ()

    def OnChoixProfil(self, event): 
        if self.ctrl_profil.GetID() == None :
            actif = False
        else:
            actif = True
        self.ctrl_champs.Enable(actif)
        self.bouton_modifier.Enable(actif)
        self.bouton_monter.Enable(actif)
        self.bouton_descendre.Enable(actif)
        self.MAJlisteChamps() 

    def OnBoutonProfils(self, event): 
        import DLG_Etat_nomin_profils
        dlg = DLG_Etat_nomin_profils.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_profil.MAJ() 
        self.OnChoixProfil(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_champs.Modifier(None)

    def OnBoutonMonter(self, event): 
        self.ctrl_champs.Monter(None)

    def OnBoutonDescendre(self, event): 
        self.ctrl_champs.Descendre(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Etatnominatif")

    def OnBoutonFermer(self, event): 
        try :
            self.EndModal(wx.ID_CANCEL)
        except :
            pass

    def OnCheckActivites(self, event=None):
        listeActivites = self.ctrl_activites.GetActivites()
        self.ctrl_groupes.SetActivites(listeActivites)
        self.ctrl_categories.SetActivites(listeActivites)
        self.MAJlisteChamps() 

    def OnBoutonOk(self, event): 
        dictParametres = {}
        
        # Récupération de la période
        if self.ctrl_periode.Validation() == False : return
        dictParametres["date_debut"] = self.ctrl_periode.GetDateDebut()
        dictParametres["date_fin"] = self.ctrl_periode.GetDateFin()
        
        # Récupération des activités
        listeActivites = self.ctrl_activites.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        dictParametres["activites"] = listeActivites
        
        # Récupération des groupes
        listeGroupes = self.ctrl_groupes.GetIDcoches()
        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        dictParametres["groupes"] = listeGroupes
        
        # Récupération des catégories de tarifs
        listeCategories = self.ctrl_categories.GetIDcoches()
        if len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune catégorie de tarif !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        dictParametres["categories"] = listeCategories
        
        # Récupération des caisses
        listeCaisses = self.ctrl_caisses.GetIDcoches()
        dictParametres["caisses"] = listeCaisses

        # Récupération de l'âge
        if self.ctrl_age.Validation() == False : return
        age = self.ctrl_age.GetCondition()
        dictParametres["age"] = age
        
        # Récupération du QF
        QF = self.ctrl_qf.GetCondition()
        dictParametres["qf"] = QF
        
        # Récupération des champs sélectionnés
        listeChamps = self.ctrl_champs.GetTracksSelections()
        if len(listeChamps) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun champ !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        dictParametres["champs"] = listeChamps
        
        # Vérifie si les champs sont bien disponibles avec les activités sélectionnées
        listeChampsIndisponibles = []
        for champ in dictParametres["champs"] :
            if champ.type == None :
                listeChampsIndisponibles.append(champ.code)
        if len(listeChampsIndisponibles) > 0 :
            message = _(u"Attention, les %d champs suivants ne sont pas disponibles avec les activités sélectionnées : %s. Ils seront donc exclus des résultats.\n\nSouhaitez-vous quand même continuer ?") % (len(listeChampsIndisponibles), ", ".join(listeChampsIndisponibles))
            dlg = wx.MessageDialog(self, message, _(u"Avertissement"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Récupération de tous les champs disponibles
        listeChampsDispo = self.ctrl_champs.GetListeChampsDispo()
        dictParametres["champsDispo"] = listeChampsDispo
        
        # Affichage des résultats
        dlg = DLG_Etat_nomin_resultats.Dialog(self, dictParametres=dictParametres)
        dlg.ShowModal() 
        dlg.Destroy() 
        
        
        
    def AfficheAvertissement(self):
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="infos_etat_nomin", valeur=False) == True :
            return

        import DLG_Message_html
        texte = u"""
<CENTER><IMG SRC="Images/32x32/Information.png">
<BR><BR>
<FONT SIZE=2>
<B>Avertissement</B>
<BR><BR>
La fonctionnalité 'Etat nominatif des consommations' étant très récente, je ne peux que vous conseiller de bien vérifier les résultats obtenus. Si vous constatez un bug, n'hésitez pas à le signaler sur le forum de Noethys.
<BR><BR>
D'autre part, cette fonctionnalité peut être ardue à appréhender en raison de ses nombreuses possibilités. Je vous propose de découvrir sur le forum un mode d'emploi complet sur son utilisation :
<BR>
<A HREF="http://www.noethys.com/index.php?option=com_kunena&Itemid=7&func=view&catid=5&id=772#772">Cliquez ici pour accéder au mode d'emploi</A>
</FONT>
</CENTER>
"""
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), nePlusAfficher=True)
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="infos_etat_nomin", valeur=nePlusAfficher)
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
