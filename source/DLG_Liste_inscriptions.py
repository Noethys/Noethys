#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime

import GestionDB
import CTRL_Bandeau
import OL_Liste_inscriptions




class CTRL_Activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.dictDonnees = {}
        self.MAJ() 
    
    def MAJ(self):
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY nom
        ;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()      
        DB.Close() 
        if len(listeActivites) == 0 :
            self.Enable(False)
        listeLabels = []
        index = 0
        for IDactivite, nom in listeActivites :
            self.dictDonnees[index] = IDactivite
            listeLabels.append(nom)
            index += 1
        self.SetItems(listeLabels)

    def SetActivite(self, IDactivite=None):
        for index, IDactiviteTmp in self.dictDonnees.iteritems() :
            if IDactiviteTmp == IDactivite :
                self.SetSelection(index)

    def GetActivite(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
    
    def GetLabelActivite(self):
        if self.GetActivite() == None :
            return u"Aucune"
        else :
            return self.GetStringSelection()

# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeGroupes = []
        self.dictGroupes = {}
        
    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeGroupes, self.dictGroupes = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeGroupes = []
        dictGroupes = {}
        if self.IDactivite == None :
            return listeGroupes, dictGroupes 
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, IDactivite, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDgroupe, IDactivite, nom in listeDonnees :
            dictTemp = { "nom" : nom, "IDactivite" : IDactivite}
            dictGroupes[IDgroupe] = dictTemp
            listeGroupes.append((nom, IDgroupe))
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
    
    def GetLabelsGroupes(self):
        listeLabels = []
        for IDgroupe in self.GetListeGroupes() :
            listeLabels.append(self.dictGroupes[IDgroupe]["nom"])
        return ", ".join(listeLabels)
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeCategories = []
        self.dictCategories = {}
        
    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeCategories, self.dictCategories = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeCategories = []
        dictCategories = {}
        if self.IDactivite == None :
            return listeCategories, dictCategories 
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, IDactivite, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDcategorie_tarif, IDactivite, nom in listeDonnees :
            dictTemp = { "nom" : nom, "IDactivite" : IDactivite}
            dictCategories[IDcategorie_tarif] = dictTemp
            listeCategories.append((nom, IDcategorie_tarif))
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

    def GetLabelsCategories(self):
        listeLabels = []
        for IDcategorie in self.GetListeCategories() :
            listeLabels.append(self.dictCategories[IDcategorie]["nom"])
        return ", ".join(listeLabels)

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Regroupement(wx.Choice):
    def __init__(self, parent, listview=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listview = listview
        self.listeLabels = []
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        self.listeLabels = [u"Aucun",]
        listeChamps = self.listview.GetListeChamps() 
        for dictTemp in listeChamps :
            if dictTemp["afficher"] == True :
                self.listeLabels.append(dictTemp["label"])
        self.SetItems(self.listeLabels)

    def GetRegroupement(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.GetStringSelection() 

# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Colonnes(wx.CheckListBox):
    def __init__(self, parent, listview=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listview = listview
        self.listeCodes = []
        self.SetMinSize((-1, 50))
        self.MAJ() 

    def MAJ(self, selectCode=None):
        self.listeCodes = []
        self.Clear()
        listeChamps = self.listview.GetListeChamps() 
        index = 0
        selection = None
        for dictTemp in listeChamps :
            if dictTemp["actif"] == True :
                self.listeCodes.append(dictTemp["code"])
                self.Append(dictTemp["label"])
                if dictTemp["afficher"] == True :
                    self.Check(index)
                if selectCode == dictTemp["code"] :
                    selection = index
                index += 1
                
        # Sélection
        if selection != None :
            self.Select(selection)
            self.EnsureVisible(selection)
    
    def GetListeColonnes(self):
        listeLabels = []
        nbreItems = self.GetCount() 
        for index in range(0, nbreItems):
            if self.IsChecked(index):
                label = self.GetString(index) 
                listeLabels.append(label)
        return listeLabels
        
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
    
    def Monter(self):
        index = self.GetSelection() 
        if index == -1 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune colonne à déplacer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if index == 0 :
            dlg = wx.MessageDialog(self, u"Cette colonne est déjà la première de la liste !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        self.DeplacerColonne(index, -1) 
            
    def Descendre(self):
        index = self.GetSelection() 
        if index == -1 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune colonne à déplacer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if index == len(self.listeCodes)-1 :
            dlg = wx.MessageDialog(self, u"Cette colonne est déjà la dernière de la liste !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        self.DeplacerColonne(index, 1) 

    def DeplacerColonne(self, index=None, sens=1):
        code = self.listeCodes[index]
        code2 = self.listeCodes[index + sens]
        
        # Récupération des colonnes
        listeChamps = self.listview.GetListeChamps() 
        index = 0
        for dictTemp in listeChamps :
            if dictTemp["code"] == code : 
                indexCode = index
                dictCode = dictTemp
            if dictTemp["code"] == code2 : 
                indexCode2 = index
                dictCode2 = dictTemp
            index += 1
        
        # Déplacement des colonnes
        listeChamps[indexCode] = dictCode2
        listeChamps[indexCode2] = dictCode
        self.MAJ(selectCode=dictCode["code"]) 
        
# ----------------------------------------------------------------------------------------------------------------------------------

class Parametres(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listview = listview
        
        # Activité
        self.box_activite_staticbox = wx.StaticBox(self, -1, u"Activité")
        self.ctrl_activite = CTRL_Activite(self)
        self.ctrl_activite.SetMinSize((200, -1))
        self.check_partis = wx.CheckBox(self, -1, u"Afficher les individus partis")
        self.check_partis.SetValue(True) 
        
        # Groupes
        self.box_groupes_staticbox = wx.StaticBox(self, -1, u"Groupes")
        self.ctrl_groupes = CTRL_Groupes(self)
        
        # Catégories
        self.box_categories_staticbox = wx.StaticBox(self, -1, u"Catégories")
        self.ctrl_categories = CTRL_Categories(self)
        
        # Regroupement
        self.box_regroupement_staticbox = wx.StaticBox(self, -1, u"Regroupement")
        self.ctrl_regroupement = CTRL_Regroupement(self, listview=listview)
        
        # Colonnes
        self.box_colonnes_staticbox = wx.StaticBox(self, -1, u"Colonnes")
        self.ctrl_colonnes = CTRL_Colonnes(self, listview=listview)
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        
        # Actualiser
        self.bouton_actualiser = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Rafraichir_liste.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_CHOICE, self.OnChoixRegroupement, self.ctrl_regroupement)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHaut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBas, self.bouton_bas)

    def __set_properties(self):
        self.ctrl_activite.SetToolTipString(u"Sélectionnez une activité")
        self.check_partis.SetToolTipString(u"Cochez cette case pour inclure dans la liste des individus partis")
        self.ctrl_groupes.SetToolTipString(u"Cochez les groupes à afficher")
        self.ctrl_categories.SetToolTipString(u"Cochez les catégories à afficher")
        self.ctrl_regroupement.SetToolTipString(u"Sélectionnez un regroupement")
        self.ctrl_colonnes.SetToolTipString(u"Cochez les colonnes souhaitées")
        self.bouton_actualiser.SetToolTipString(u"Cliquez ici pour actualiser la liste")
        self.bouton_haut.SetToolTipString(u"Cliquez ici pour monter la colonne")
        self.bouton_bas.SetToolTipString(u"Cliquez ici pour descendre la colonne")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        # Activité
        box_activite = wx.StaticBoxSizer(self.box_activite_staticbox, wx.VERTICAL)
        box_activite.Add(self.ctrl_activite, 0, wx.ALL|wx.EXPAND, 5)
        box_activite.Add(self.check_partis, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        grid_sizer_base.Add(box_activite, 1, wx.EXPAND, 0)
        
        # Groupes
        box_groupes = wx.StaticBoxSizer(self.box_groupes_staticbox, wx.VERTICAL)
        box_groupes.Add(self.ctrl_groupes, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_groupes, 1, wx.EXPAND, 0)
        
        # Catégories
        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        box_categories.Add(self.ctrl_categories, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_categories, 1, wx.EXPAND, 0)
        
        # Regroupement
        box_regroupement = wx.StaticBoxSizer(self.box_regroupement_staticbox, wx.VERTICAL)
        box_regroupement.Add(self.ctrl_regroupement, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_regroupement, 1, wx.EXPAND, 0)
        
        # Colonnes
        box_colonnes = wx.StaticBoxSizer(self.box_colonnes_staticbox, wx.VERTICAL)
        grid_sizer_colonnes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_colonnes.Add(self.ctrl_colonnes, 0, wx.EXPAND, 0)
        
        grid_sizer_boutons_colonnes = wx.FlexGridSizer(rows=2, cols=1, vgap= 5, hgap=5)
        grid_sizer_boutons_colonnes.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_boutons_colonnes.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_colonnes.Add(grid_sizer_boutons_colonnes, 0, wx.EXPAND, 0)
        
        grid_sizer_colonnes.AddGrowableRow(0)
        grid_sizer_colonnes.AddGrowableCol(0)
        box_colonnes.Add(grid_sizer_colonnes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_colonnes, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(4)
        grid_sizer_base.AddGrowableCol(0)

    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activite.GetActivite()
        self.ctrl_groupes.SetActivite(IDactivite)
        self.ctrl_categories.SetActivite(IDactivite)

    def OnChoixRegroupement(self, event): 
        pass
    
    def OnBoutonHaut(self, event):
        self.ctrl_colonnes.Monter()
        
    def OnBoutonBas(self, event):
        self.ctrl_colonnes.Descendre()
        
    def OnBoutonActualiser(self, event): 
        # Récupération des paramètres
        IDactivite = self.ctrl_activite.GetActivite()
        partis = self.check_partis.GetValue() 
        listeGroupes = self.ctrl_groupes.GetListeGroupes()
        listeCategories = self.ctrl_categories.GetListeCategories()
        regroupement = self.ctrl_regroupement.GetRegroupement()
        listeColonnes = self.ctrl_colonnes.GetListeColonnes() 
        
        # Vérifications
        if IDactivite == None :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune activité !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez sélectionner au moins un groupe !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez sélectionner au moins une catégorie !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeColonnes) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez cocher au moins une colonne !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        labelParametres = self.GetLabelParametres() 
        
        # MAJ du listview
        self.parent.ctrl_listview.MAJ(IDactivite=IDactivite, partis=partis, listeGroupes=listeGroupes, listeCategories=listeCategories, 
                                                    regroupement=regroupement, listeColonnes=listeColonnes, labelParametres=labelParametres)

    def GetLabelParametres(self):
        listeParametres = []
        
        activite = self.ctrl_activite.GetLabelActivite()
        listeParametres.append(u"Activité : %s" % activite)

        groupes = self.ctrl_groupes.GetLabelsGroupes()
        listeParametres.append(u"Groupes : %s" % groupes)

        categories = self.ctrl_categories.GetLabelsCategories()
        listeParametres.append(u"Catégories : %s" % categories)

        labelParametres = " | ".join(listeParametres)
        return labelParametres


# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = u"Vous pouvez ici consulter et imprimer la liste des inscriptions. Commencez par sélectionner une activité avant de cliquer sur le bouton 'Rafraîchir la liste' pour afficher les résultats. Vous pouvez également regrouper les données par type d'informations et sélectionner les colonnes à afficher. Les données peuvent être ensuite imprimées ou exportées au format Texte ou Excel."
        titre = u"Liste des inscriptions"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")

        self.listviewAvecFooter = OL_Liste_inscriptions.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Liste_inscriptions.CTRL_Outils(self, listview=self.ctrl_listview)
        self.ctrl_parametres = Parametres(self, listview=self.ctrl_listview)
        
        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init contrôles
        listeColonnes = self.ctrl_parametres.ctrl_colonnes.GetListeColonnes() 
        self.ctrl_listview.MAJ(listeColonnes=listeColonnes) 

    def __set_properties(self):
        self.bouton_ouvrir_fiche.SetToolTipString(u"Cliquez ici pour ouvrir la fiche de la famille sélectionnée dans la liste")
        self.bouton_apercu.SetToolTipString(u"Cliquez ici pour créer un aperçu de la liste")
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour imprimer la liste")
        self.bouton_texte.SetToolTipString(u"Cliquez ici pour exporter la liste au format Texte")
        self.bouton_excel.SetToolTipString(u"Cliquez ici pour exporter la liste au format Excel")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND | wx.LEFT, 5)
        
        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OuvrirFiche(self, event):
        self.ctrl_listview.OuvrirFicheFamille(None)

    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)
        
    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)

    def ExportTexte(self, event):
        self.ctrl_listview.ExportTexte(None)

    def ExportExcel(self, event):
        self.ctrl_listview.ExportExcel(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesinscriptions")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
