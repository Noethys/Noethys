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
import GestionDB

from Ctrl import CTRL_Saisie_euros
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Combobox_autocomplete



##class CTRL_Exercice(CTRL_Combobox_autocomplete.CTRL):
##    def __init__(self, parent):
##        CTRL_Combobox_autocomplete.CTRL.__init__(self, parent) 
##        self.parent = parent
##        self.IDdefaut = None
##        self.MAJ() 
##    
##    def MAJ(self):
##        listeItems = self.GetListeDonnees()
##        if len(listeItems) == 0 :
##            self.Enable(False)
##        self.SetItems(listeItems)
##        self.SetID(self.IDdefaut)
##    
##    def GetListeDonnees(self):
##        listeItems = [u"",]
##        self.dictDonnees = { 0 : {"ID":None}, }
##        DB = GestionDB.DB()
##        req = """SELECT IDexercice, nom, date_debut, date_fin, defaut
##        FROM compta_exercices
##        ORDER BY date_debut; """
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        index = 1
##        for IDexercice, nom, date_debut, date_fin, defaut in listeDonnees :
##            self.dictDonnees[index] = { "ID" : IDexercice }
##            label = nom
##            listeItems.append(label)
##            if defaut == 1 :
##                self.IDdefaut = IDexercice
##            index += 1
##        return listeItems
##
##    def SetID(self, ID=0):
##        for index, values in self.dictDonnees.iteritems():
##            if values["ID"] == ID :
##                 self.SetSelection(index)
##
##    def GetID(self):
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]["ID"]



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
    def __init__(self, parent, typeOperation="credit", track=None, dateOperation=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent  
        self.typeOperation = typeOperation 
        self.track = track
        self.IDventilation = None

        self.label_date_budget = wx.StaticText(self, wx.ID_ANY, _(u"Date budget :"))
        self.ctrl_date_budget = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_budget.SetDate(dateOperation) 
        
        self.label_analytique = wx.StaticText(self, wx.ID_ANY, _(u"Analytique :"))
        self.ctrl_analytique = CTRL_Analytique(self)
        self.ctrl_analytique.SetMinSize((300, -1)) 
        
        self.label_categorie = wx.StaticText(self, wx.ID_ANY, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self, typeOperation=typeOperation)
        
        self.label_libelle = wx.StaticText(self, wx.ID_ANY, _(u"Libellé :"))
        self.ctrl_libelle = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_montant = wx.StaticText(self, wx.ID_ANY, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.bouton_analytiques = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_categories = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnalytiques, self.bouton_analytiques)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        if self.typeOperation == "credit" : 
            titre = _(u"Ventilation d'une opération au crédit")
        elif self.typeOperation == "debit" : 
            titre = _(u"Ventilation d'une opération au débit")
        else :
            titre = u""
        self.SetTitle(titre)
        
        if self.track != None :
            self.Importation()
        
        wx.CallAfter(self.ctrl_date_budget.SetInsertionPoint, 0)

    def __set_properties(self):
        self.ctrl_date_budget.SetToolTipString(_(u"Saisissez la date d'impact budgétaire"))
        self.ctrl_categorie.SetToolTipString(_(u"Sélectionnez une catégorie"))
        self.bouton_categories.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des catégories"))
        self.ctrl_analytique.SetToolTipString(_(u"Sélectionnez un poste analytique"))
        self.bouton_analytiques.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des postes analytiques"))
        self.ctrl_libelle.SetToolTipString(_(u"Saisissez un libellé (Optionnel)"))
        self.ctrl_montant.SetToolTipString(_(u"Saisissez un montant"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(5, 2, 10, 10)
        
        grid_sizer_haut.Add(self.label_date_budget, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_date_budget, 1, wx.EXPAND, 0)

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
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesoperationsdetresorerie")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        IDventilation = self.IDventilation
        date_budget = self.ctrl_date_budget.GetDate()
        IDanalytique = self.ctrl_analytique.GetID()
        IDcategorie = self.ctrl_categorie.GetID()
        libelle = self.ctrl_libelle.GetValue()
        montant = self.ctrl_montant.GetMontant()
        
        if date_budget == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date d'impact budgétaire !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_budget.SetFocus()
            return False
        
        if IDanalytique == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un code analytique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_analytique.SetFocus()
            return False
        
        if IDcategorie == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_categorie.SetFocus()
            return False

        if montant == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        self.EndModal(wx.ID_OK)
    
    def Importation(self):
        """ Importation depuis un track """
        self.IDventilation = self.track.IDventilation
        self.ctrl_date_budget.SetDate(self.track.date_budget)
        self.ctrl_analytique.SetID(self.track.IDanalytique)
        self.ctrl_categorie.SetID(self.track.IDcategorie)
        self.ctrl_libelle.SetValue(self.track.libelle)
        self.ctrl_montant.SetMontant(self.track.montant)
    
    def GetDictDonnees(self):
        dictDonnees = {
            "IDventilation" : self.IDventilation, 
            "date_budget" : self.ctrl_date_budget.GetDate(),
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
