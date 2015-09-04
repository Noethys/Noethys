#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB

import CTRL_Saisie_euros
import CTRL_Combobox_autocomplete
import CTRL_Saisie_date
import UTILS_Dates



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
    def __init__(self, parent, typeOperation="credit", IDoperation_budgetaire=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent  
        self.typeOperation = typeOperation 
        self.IDoperation_budgetaire = IDoperation_budgetaire

        self.label_date_budget = wx.StaticText(self, wx.ID_ANY, _(u"Date budget :"))
        self.ctrl_date_budget = CTRL_Saisie_date.Date2(self)
        
        self.label_analytique = wx.StaticText(self, wx.ID_ANY, _(u"Analytique :"))
        self.ctrl_analytique = CTRL_Analytique(self)
        self.ctrl_analytique.SetMinSize((300, -1))
        
        self.label_categorie = wx.StaticText(self, wx.ID_ANY, _(u"Cat�gorie :"))
        self.ctrl_categorie = CTRL_Categorie(self, typeOperation=typeOperation)
        
        self.label_libelle = wx.StaticText(self, wx.ID_ANY, _(u"Libell� :"))
        self.ctrl_libelle = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_montant = wx.StaticText(self, wx.ID_ANY, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.bouton_analytiques = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.bouton_categories = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnalytiques, self.bouton_analytiques)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        if self.typeOperation == "credit" : 
            titre = _(u"Ventilation d'une op�ration budg�taire au cr�dit")
        elif self.typeOperation == "debit" : 
            titre = _(u"Ventilation d'une op�ration budg�taire au d�bit")
        else :
            titre = u""
        self.SetTitle(titre)
        
        if self.IDoperation_budgetaire != None :
            self.Importation()

    def __set_properties(self):
        self.ctrl_date_budget.SetToolTipString(_(u"Saisissez la date d'impact budg�taire"))
        self.ctrl_categorie.SetToolTipString(_(u"S�lectionnez une cat�gorie"))
        self.bouton_categories.SetToolTipString(_(u"Cliquez ici pour acc�der � la gestion des cat�gories"))
        self.ctrl_analytique.SetToolTipString(_(u"S�lectionnez un poste analytique"))
        self.bouton_analytiques.SetToolTipString(_(u"Cliquez ici pour acc�der � la gestion des postes analytiques"))
        self.ctrl_libelle.SetToolTipString(_(u"Saisissez un libell� (Optionnel)"))
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
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesoperationsbudgetaires")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        etat = self.Sauvegarde() 
        if etat == False :
            return
        self.EndModal(wx.ID_OK)
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT type, date_budget, IDanalytique, IDcategorie, libelle, montant
        FROM compta_operations_budgetaires WHERE IDoperation_budgetaire=%d;""" % self.IDoperation_budgetaire
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        typeOperation, date_budget, IDanalytique, IDcategorie, libelle, montant = listeTemp[0]
        date_budget = UTILS_Dates.DateEngEnDateDD(date_budget)
        
        self.ctrl_date_budget.SetDate(date_budget)
        self.ctrl_analytique.SetID(IDanalytique)
        self.ctrl_categorie.SetID(IDcategorie)
        self.ctrl_libelle.SetValue(libelle)
        self.ctrl_montant.SetMontant(montant)
        self.typeOperation = typeOperation

    def Sauvegarde(self):
        date_budget = self.ctrl_date_budget.GetDate()
        IDanalytique = self.ctrl_analytique.GetID()
        IDcategorie = self.ctrl_categorie.GetID()
        libelle = self.ctrl_libelle.GetValue()
        montant = self.ctrl_montant.GetMontant()
        
        if date_budget == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date d'impact budg�taire !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_budget.SetFocus()
            return False
        
        if IDanalytique == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un code analytique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_analytique.SetFocus()
            return False
        
        if IDcategorie == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une cat�gorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
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

        # Sauvegarde de l'op�ration
        DB = GestionDB.DB()
        
        listeDonnees = [ 
            ("type", self.typeOperation),
            ("date_budget", date_budget),
            ("IDanalytique", IDanalytique),
            ("IDcategorie", IDcategorie),
            ("libelle", libelle),
            ("montant", montant),
            ]
        if self.IDoperation_budgetaire == None :
            self.IDoperation_budgetaire = DB.ReqInsert("compta_operations_budgetaires", listeDonnees)
        else :
            DB.ReqMAJ("compta_operations_budgetaires", listeDonnees, "IDoperation_budgetaire", self.IDoperation_budgetaire)
        DB.Close()

        return True
    
    def GetIDoperation_budgetaire(self):
        return self.IDoperation_budgetaire
    


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, typeOperation="debit", IDoperation_budgetaire=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
