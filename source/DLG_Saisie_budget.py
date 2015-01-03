#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import UTILS_Dates
import datetime

import OL_Categories_budgetaires



class CTRL_Analytiques(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.SetMinSize((-1, 60))
        self.MAJ() 
    
    def MAJ(self):
        listeTmp = []
        db = GestionDB.DB()
        req = """SELECT IDanalytique, nom 
        FROM compta_analytiques 
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 : 
            for IDanalytique, nom in listeDonnees :
                listeTmp.append((IDanalytique, nom, False))
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
    
    def GetCochesStr(self):
        listeID = self.GetIDcoches() 
        listeTexte = []
        for ID in listeID :
            listeTexte.append(str(ID))
        return ";".join(listeTexte)
    
    def SetCochesStr(self, texte=""):
        listeTexte = texte.split(";")
        listeID = []
        if len(listeTexte) > 0 :
            for ID in listeTexte :
                listeID.append(int(ID)) 
        self.SetIDcoches(listeID)
        
# ----------------------------------------------------------------------------------------------------------------------------

class Panel_OL(wx.Panel):
    def __init__(self, parent, typeCategorie=None):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        self.ctrl = OL_Categories_budgetaires.ListView(self, id=-1, typeCategorie=typeCategorie, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.Layout()
    

class CTRL_Exercice(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDdefaut = None
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
        self.SetID(self.IDdefaut)
    
    def GetListeDonnees(self):
        listeItems = [u"",]
        self.dictDonnees = { 0 : {"ID":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDexercice, nom, date_debut, date_fin, defaut
        FROM compta_exercices
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDexercice, nom, date_debut, date_fin, defaut in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDexercice }
            label = nom
            listeItems.append(label)
            if defaut == 1 :
                self.IDdefaut = IDexercice
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



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDbudget=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent 
        self.IDbudget = IDbudget
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Généralités")
        self.label_nom = wx.StaticText(self, wx.ID_ANY, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_exercice = wx.StaticText(self, wx.ID_ANY, u"Exercice :")
        self.ctrl_exercice = CTRL_Exercice(self)
        self.bouton_exercice = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.label_observations = wx.StaticText(self, wx.ID_ANY, u"Notes :")
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        self.ctrl_observations.SetMinSize((270, -1))
        
        # Postes analytiques
        self.box_analytiques_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Postes analytiques")
        self.ctrl_analytiques = CTRL_Analytiques(self)

        # Catégories
        self.box_categories_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Catégories budgétaires")
        self.notebook = wx.Notebook(self, -1, style=wx.BK_BOTTOM)
        
        self.ctrl_categories_debit = Panel_OL(self.notebook, "debit")
        self.ctrl_categories_credit = Panel_OL(self.notebook, "credit")

##        self.ctrl_categories_debit = OL_Categories_budgetaires.ListView(self.notebook, id=-1, typeCategorie="debit", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
##        self.ctrl_categories_credit = OL_Categories_budgetaires.ListView(self.notebook, id=-1, typeCategorie="credit", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.notebook.AddPage(self.ctrl_categories_debit, u"Débit")
        self.notebook.AddPage(self.ctrl_categories_credit, u"Crédit")
        
        self.bouton_ajouter_categories = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_categories = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_categories = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExercices, self.bouton_exercice)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter, self.bouton_ajouter_categories)
        self.Bind(wx.EVT_BUTTON, self.OnModifier, self.bouton_modifier_categories)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer, self.bouton_supprimer_categories)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Importation de l'opération
        if self.IDbudget != None :
            self.Importation()
            titre = u"Modification d'un budget"
        else :
            titre = u"Saisie d'un budget"
        self.SetTitle(titre)
        
        # Importation des catégories
        self.tracksDebitInitial = []
        self.tracksCreditInitial = []
        self.tracksInitial = []
        if self.IDbudget != None :
            self.tracksDebitInitial = OL_Categories_budgetaires.Importation(self.IDbudget, "debit")
            self.ctrl_categories_debit.ctrl.SetTracks(self.tracksDebitInitial)
            self.tracksCreditInitial = OL_Categories_budgetaires.Importation(self.IDbudget, "credit")
            self.ctrl_categories_credit.ctrl.SetTracks(self.tracksCreditInitial)
            for listeTracks in (self.tracksDebitInitial, self.tracksCreditInitial) :
                for track in listeTracks :
                    self.tracksInitial.append(track)
        self.ctrl_categories_debit.ctrl.MAJ() 
        self.ctrl_categories_credit.ctrl.MAJ() 
                

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(u"Saisissez un nom pour ce budget (Ex : Année 2015)")
        self.ctrl_exercice.SetToolTipString(u"Sélectionnez un exercice")
        self.ctrl_observations.SetToolTipString(u"Saisissez des observations")
        self.bouton_ajouter_categories.SetToolTipString(u"Cliquez ici pour ajouter une catégorie budgétaire")
        self.bouton_modifier_categories.SetToolTipString(u"Cliquez ici pour modifier la catégorie budgétaire sélectionnée")
        self.bouton_supprimer_categories.SetToolTipString(u"Cliquez ici pour supprimer la catégorie budgétaire sélectionnée")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((700, 620))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(5, 2, 10, 10)
                
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_exercice, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_exercice = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_exercice.Add(self.ctrl_exercice, 0, wx.EXPAND, 0)
        grid_sizer_exercice.Add(self.bouton_exercice, 0, 0, 0)
        grid_sizer_exercice.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_exercice, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_generalites, 1, wx.EXPAND, 0)

        # Analytiques
        box_analytiques = wx.StaticBoxSizer(self.box_analytiques_staticbox, wx.VERTICAL)
        box_analytiques.Add(self.ctrl_analytiques, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_analytiques, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)

        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Catégories
        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        grid_sizer_categories = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_categories.Add(self.notebook, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_categories = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_boutons_categories.Add(self.bouton_ajouter_categories, 0, 0, 0)
        grid_sizer_boutons_categories.Add(self.bouton_modifier_categories, 0, 0, 0)
        grid_sizer_boutons_categories.Add(self.bouton_supprimer_categories, 0, 0, 0)
        grid_sizer_categories.Add(grid_sizer_boutons_categories, 1, wx.EXPAND, 0)
        
        grid_sizer_categories.AddGrowableRow(0)
        grid_sizer_categories.AddGrowableCol(0)
        box_categories.Add(grid_sizer_categories, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_categories, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
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
        import UTILS_Aide
        UTILS_Aide.Aide(u"")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonExercices(self, event):  
        IDexercice = self.ctrl_exercice.GetID()
        import DLG_Exercices
        dlg = DLG_Exercices.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_exercice.MAJ()
        self.ctrl_exercice.SetID(IDexercice)
    
    def OnAjouter(self, event):
        if self.notebook.GetSelection() == 0 :
            self.ctrl_categories_debit.ctrl.Ajouter()
        else :
            self.ctrl_categories_credit.ctrl.Ajouter()
        
    def OnModifier(self, event):
        if self.notebook.GetSelection() == 0 :
            self.ctrl_categories_debit.ctrl.Modifier()
        else :
            self.ctrl_categories_credit.ctrl.Modifier()

    def OnSupprimer(self, event):
        if self.notebook.GetSelection() == 0 :
            self.ctrl_categories_debit.ctrl.Supprimer()
        else :
            self.ctrl_categories_credit.ctrl.Supprimer()
        
    def OnBoutonOk(self, event): 
        etat = self.Sauvegarde() 
        if etat == False :
            return
        self.EndModal(wx.ID_OK)
        
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT nom, IDexercice, observations, analytiques
        FROM compta_budgets WHERE IDbudget=%d;""" % self.IDbudget
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, IDexercice, observations, analytiques = listeTemp[0]
        self.ctrl_nom.SetValue(nom)
        self.ctrl_exercice.SetID(IDexercice)
        self.ctrl_observations.SetValue(observations) 
        self.ctrl_analytiques.SetCochesStr(analytiques)

    def Sauvegarde(self):
        nom = self.ctrl_nom.GetValue()
        IDexercice = self.ctrl_exercice.GetID()
        observations = self.ctrl_observations.GetValue()
        analytiques = self.ctrl_analytiques.GetCochesStr()
        tracksCategoriesDebit = self.ctrl_categories_debit.ctrl.GetTracks() 
        tracksCategoriesCredit = self.ctrl_categories_credit.ctrl.GetTracks() 

        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom pour ce budget !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if IDexercice == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un exercice pour ce budget !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_exercice.SetFocus()
            return False

        if analytiques == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement cocher au moins un poste analytique !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Sauvegarde de l'opération
        DB = GestionDB.DB()
        
        listeDonnees = [ 
            ("nom", nom),
            ("IDexercice", IDexercice),
            ("observations", observations),
            ("analytiques", analytiques),
            ]
        if self.IDbudget == None :
            self.IDbudget = DB.ReqInsert("compta_budgets", listeDonnees)
        else :
            DB.ReqMAJ("compta_budgets", listeDonnees, "IDbudget", self.IDbudget)

        # Sauvegarde des catégories
        listeID = []
        for listeTracks in (tracksCategoriesDebit, tracksCategoriesCredit) :
            for track in listeTracks :
                listeDonnees = [ 
                    ("IDbudget", self.IDbudget),
                    ("type", track.typeCategorie),
                    ("IDcategorie", track.IDcategorie),
                    ("valeur", track.valeur),
                    ]
                if track.IDcategorie_budget == None :
                    IDcategorie_budget = DB.ReqInsert("compta_categories_budget", listeDonnees)
                else :
                    DB.ReqMAJ("compta_categories_budget", listeDonnees, "IDcategorie_budget", track.IDcategorie_budget)
                listeID.append(track.IDcategorie_budget) 
                
        # Supprime les catégories supprimées
        for track in self.tracksInitial :
            if track.IDcategorie_budget not in listeID :
                DB.ReqDEL("compta_categories_budget", "IDcategorie_budget", track.IDcategorie_budget)
        
        DB.Close()

        return True
    
    def GetIDbudget(self):
        return self.IDbudget 
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDbudget=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
