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

import CTRL_Saisie_euros
import CTRL_Combobox_autocomplete



class CTRL_Exercice(CTRL_Combobox_autocomplete.CTRL):
    def __init__(self, parent):
        CTRL_Combobox_autocomplete.CTRL.__init__(self, parent) 
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


class CTRL_Analytique(CTRL_Combobox_autocomplete.CTRL):
    def __init__(self, parent):
        CTRL_Combobox_autocomplete.CTRL.__init__(self, parent) 
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
        req = """SELECT IDanalytique, nom, abrege, defaut
        FROM compta_analytiques
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDanalytique, nom, abrege, defaut in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDanalytique }
            label = nom
            listeItems.append(label)
            if defaut == 1 :
                self.IDdefaut = IDanalytique
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


class CTRL_Categorie(CTRL_Combobox_autocomplete.CTRL):
    def __init__(self, parent, typeOperation="debit"):
        CTRL_Combobox_autocomplete.CTRL.__init__(self, parent) 
        self.parent = parent
        self.typeOperation = typeOperation
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [u"",]
        self.dictDonnees = { 0 : {"ID":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, type, nom, abrege, journal, IDcompte
        FROM compta_categories
        WHERE type='%s'
        ORDER BY nom; """ % self.typeOperation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDcategorie, typeCategorie, nom, abrege, journal, IDcompte in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcategorie }
            label = nom
            listeItems.append(label)
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
    def __init__(self, parent, typeOperation="credit", track=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent  
        self.typeOperation = typeOperation 
        self.track = track
        self.IDventilation = None

        self.label_exercice = wx.StaticText(self, wx.ID_ANY, u"Exercice :")
        self.ctrl_exercice = CTRL_Exercice(self)
        self.ctrl_exercice.SetMinSize((300, -1)) 
        
        self.label_analytique = wx.StaticText(self, wx.ID_ANY, u"Analytique :")
        self.ctrl_analytique = CTRL_Analytique(self)
        
        self.label_categorie = wx.StaticText(self, wx.ID_ANY, u"Catégorie :")
        self.ctrl_categorie = CTRL_Categorie(self, typeOperation=typeOperation)
        
        self.label_libelle = wx.StaticText(self, wx.ID_ANY, u"Libellé :")
        self.ctrl_libelle = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_montant = wx.StaticText(self, wx.ID_ANY, u"Montant :")
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        
        self.bouton_aide = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.bouton_exercice = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.bouton_analytiques = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.bouton_categories = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonExercices, self.bouton_exercice)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnalytiques, self.bouton_analytiques)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        if self.typeOperation == "credit" : 
            titre = u"Ventilation d'une opération au crédit"
        elif self.typeOperation == "debit" : 
            titre = u"Ventilation d'une opération au débit"
        else :
            titre = u""
        self.SetTitle(titre)
        
        if self.track != None :
            self.Importation()

    def __set_properties(self):
        self.ctrl_exercice.SetToolTipString(u"Sélectionnez un exercice")
        self.bouton_exercice.SetToolTipString(u"Cliquez ici pour accéder à la gestion des exercices")
        self.ctrl_categorie.SetToolTipString(u"Sélectionnez une catégorie")
        self.bouton_categories.SetToolTipString(u"Cliquez ici pour accéder à la gestion des catégories")
        self.ctrl_analytique.SetToolTipString(u"Sélectionnez un poste analytique")
        self.bouton_analytiques.SetToolTipString(u"Cliquez ici pour accéder à la gestion des postes analytiques")
        self.ctrl_libelle.SetToolTipString(u"Saisissez un libellé (Optionnel)")
        self.ctrl_montant.SetToolTipString(u"Saisissez un montant")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(5, 2, 10, 10)
        
        grid_sizer_haut.Add(self.label_exercice, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_exercice = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_exercice.Add(self.ctrl_exercice, 0, wx.EXPAND, 0)
        grid_sizer_exercice.Add(self.bouton_exercice, 0, 0, 0)
        grid_sizer_exercice.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_exercice, 1, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_analytique, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_analytique = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_analytique.Add(self.ctrl_analytique, 0, wx.EXPAND, 0)
        grid_sizer_analytique.Add(self.bouton_analytiques, 0, 0, 0)
        grid_sizer_analytique.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_analytique, 1, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_categorie, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_categorie = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categories, 0, 0, 0)
        grid_sizer_categorie.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_categorie, 1, wx.EXPAND, 0)
                
        grid_sizer_haut.Add(self.label_libelle, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_libelle, 0, wx.EXPAND, 0)
        
        grid_sizer_haut.Add(self.label_montant, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_montant, 0, 0, 0)
        
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonExercices(self, event):  
        IDexercice = self.ctrl_exercice.GetID()
        import DLG_Exercices
        dlg = DLG_Exercices.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_exercice.MAJ()
        self.ctrl_exercice.SetID(IDexercice)

    def OnBoutonCategories(self, event):  
        IDcategorie = self.ctrl_categorie.GetID()
        import DLG_Categories_operations
        dlg = DLG_Categories_operations.Dialog(self)
        dlg.SetType(self.typeOperation, verrouillage=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_categorie.MAJ()
        self.ctrl_categorie.SetID(IDcategorie)

    def OnBoutonAnalytiques(self, event):  
        IDanalytique = self.ctrl_analytique.GetID()
        import DLG_Analytiques
        dlg = DLG_Analytiques.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_analytique.MAJ()
        self.ctrl_analytique.SetID(IDanalytique)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide(u"")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        IDventilation = self.IDventilation
        IDexercice = self.ctrl_exercice.GetID()
        IDanalytique = self.ctrl_analytique.GetID()
        IDcategorie = self.ctrl_categorie.GetID()
        libelle = self.ctrl_libelle.GetValue()
        montant = self.ctrl_montant.GetMontant()
        
        if IDexercice == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un exercice !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_exercice.SetFocus()
            return False
        
        if IDanalytique == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un code analytique !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_analytique.SetFocus()
            return False
        
        if IDcategorie == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner une catégorie !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_categorie.SetFocus()
            return False

        if montant == 0.0 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un montant !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        self.EndModal(wx.ID_OK)
    
    def Importation(self):
        """ Importation depuis un track """
        self.IDventilation = self.track.IDventilation
        self.ctrl_exercice.SetID(self.track.IDexercice)
        self.ctrl_analytique.SetID(self.track.IDanalytique)
        self.ctrl_categorie.SetID(self.track.IDcategorie)
        self.ctrl_libelle.SetValue(self.track.libelle)
        self.ctrl_montant.SetMontant(self.track.montant)
    
    def GetDictDonnees(self):
        dictDonnees = {
            "IDventilation" : self.IDventilation, 
            "IDexercice" : self.ctrl_exercice.GetID(),
            "IDanalytique" : self.ctrl_analytique.GetID(),
            "IDcategorie" : self.ctrl_categorie.GetID(),
            "libelle" : self.ctrl_libelle.GetValue(),
            "montant" : self.ctrl_montant.GetMontant(),
            }
        return dictDonnees


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, typeOperation="debit")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
