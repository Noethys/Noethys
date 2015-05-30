#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import UTILS_Dates
import CTRL_Saisie_date
import datetime
import CTRL_Saisie_euros
import CTRL_Saisie_releve_bancaire



class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
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
        req = """SELECT IDcompte, nom
        FROM comptes_bancaires
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDcompte, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompte }
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
    def __init__(self, parent, IDvirement=None, IDoperation=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent 
        self.IDoperation = IDoperation
        self.IDvirement = IDvirement
        self.IDoperation_debit = None
        self.IDoperation_credit = None
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        
        self.label_date = wx.StaticText(self, wx.ID_ANY, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())

        self.label_compte_debit = wx.StaticText(self, wx.ID_ANY, _(u"Compte débiteur :"))
        self.ctrl_compte_debit = CTRL_Compte(self)
        
        self.label_compte_credit = wx.StaticText(self, wx.ID_ANY, _(u"Compte créditeur :"))
        self.ctrl_compte_credit = CTRL_Compte(self)
        
        self.label_montant = wx.StaticText(self, wx.ID_ANY, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Options"))

        self.label_releve_debit = wx.StaticText(self, wx.ID_ANY, _(u"Relevé débiteur :"))
        self.ctrl_releve_debit = CTRL_Saisie_releve_bancaire.CTRL(self)
        
        self.label_releve_credit = wx.StaticText(self, wx.ID_ANY, _(u"Relevé créditeur :"))
        self.ctrl_releve_credit = CTRL_Saisie_releve_bancaire.CTRL(self)
        
        self.label_observations = wx.StaticText(self, wx.ID_ANY, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        self.ctrl_observations.SetMinSize((200, -1))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixDebit, self.ctrl_compte_debit)
        self.Bind(wx.EVT_CHOICE, self.OnChoixCredit, self.ctrl_compte_credit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Importation de l'opération
        if self.IDvirement != None :
            self.Importation()
            titre = _(u"Modification d'un virement")
        else :
            titre = _(u"Saisie d'un virement")
        self.SetTitle(titre)
        
        # Focus
        self.ctrl_date.SetFocus() 
        wx.CallAfter(self.ctrl_date.SetInsertionPoint, 0)
                

    def __set_properties(self):
        self.ctrl_date.SetToolTipString(_(u"Saisissez la date de l'opération"))
        self.ctrl_compte_debit.SetToolTipString(_(u"Sélectionnez le compte à débiter"))
        self.ctrl_compte_credit.SetToolTipString(_(u"Sélectionnez le compte à créditer"))
        self.ctrl_montant.SetToolTipString(_(u"Saisissez le montant du virement"))
        self.ctrl_observations.SetToolTipString(_(u"Saisissez des observations"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((500, 430))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(7, 2, 10, 10)
        
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_date, 0, 0, 0)
        
        grid_sizer_generalites.Add(self.label_compte_debit, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_compte_debit, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_compte_credit, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_compte_credit, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_montant, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_montant, 0, 0, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(5, 2, 10, 10)
        
        grid_sizer_options.Add(self.label_releve_debit, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_releve_debit, 0, wx.EXPAND, 0)

        grid_sizer_options.Add(self.label_releve_credit, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_releve_credit, 0, wx.EXPAND, 0)

        grid_sizer_options.Add(self.label_observations, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        
        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_options.AddGrowableRow(2)
        box_options.Add(grid_sizer_options, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
                
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

    def OnChoixDebit(self, event):  
        IDcompte_bancaire = self.ctrl_compte_debit.GetID() 
        self.ctrl_releve_debit.SetIDcompte_bancaire(IDcompte_bancaire)
        self.ctrl_releve_debit.MAJ()
    
    def OnChoixCredit(self, event):  
        IDcompte_bancaire = self.ctrl_compte_credit.GetID() 
        self.ctrl_releve_credit.SetIDcompte_bancaire(IDcompte_bancaire)
        self.ctrl_releve_credit.MAJ()
        
    def OnBoutonOk(self, event): 
        etat = self.Sauvegarde() 
        if etat == False :
            return
        self.EndModal(wx.ID_OK)
        
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDoperation, type, date, libelle, IDtiers, IDmode, num_piece, ref_piece, IDcompte_bancaire, IDreleve, montant, observations
        FROM compta_operations WHERE IDvirement=%d;""" % self.IDvirement
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        for IDoperation, typeOperation, date, libelle, IDtiers, IDmode, num_piece, ref_piece, IDcompte_bancaire, IDreleve, montant, observations in listeTemp :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if typeOperation == "debit" :
                self.IDoperation_debit = IDoperation
                self.ctrl_compte_debit.SetID(IDcompte_bancaire)
                self.ctrl_releve_debit.SetIDcompte_bancaire(IDcompte_bancaire)
                self.ctrl_releve_debit.MAJ()
                self.ctrl_releve_debit.SetID(IDreleve)
            if typeOperation == "credit" :
                self.IDoperation_credit = IDoperation
                self.ctrl_compte_credit.SetID(IDcompte_bancaire)
                self.ctrl_releve_credit.SetIDcompte_bancaire(IDcompte_bancaire)
                self.ctrl_releve_credit.MAJ()
                self.ctrl_releve_credit.SetID(IDreleve)
        self.ctrl_date.SetDate(date)
        self.ctrl_montant.SetMontant(montant)
        self.ctrl_observations.SetValue(observations) 

    def Sauvegarde(self):
        date = self.ctrl_date.GetDate()
        IDcompte_debit = self.ctrl_compte_debit.GetID() 
        IDcompte_credit = self.ctrl_compte_credit.GetID() 
        observations = self.ctrl_observations.GetValue()
        IDreleve_debit = self.ctrl_releve_debit.GetID() 
        IDreleve_credit = self.ctrl_releve_credit.GetID() 
        montant = self.ctrl_montant.GetMontant()
        
        # Validation des données saisies
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False

        if IDcompte_debit == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte débiteur !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_compte_debit.SetFocus()
            return False

        if IDcompte_credit == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte créditeur !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_compte_credit.SetFocus()
            return False

        if montant == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False
        
        nomCompteDebit = self.ctrl_compte_debit.GetStringSelection()
        nomCompteCredit = self.ctrl_compte_credit.GetStringSelection()
        libelle = _(u"Virement %s -> %s") % (nomCompteDebit, nomCompteCredit)

        # Sauvegarde de l'opération
        DB = GestionDB.DB()
        
        # DEBIT
        listeDonnees = [ 
            ("type", "debit"),
            ("date", date),
            ("libelle", libelle),
            ("IDcompte_bancaire", IDcompte_debit),
            ("IDreleve", IDreleve_debit),
            ("montant", montant),
            ("observations", observations),
            ]
        if self.IDoperation_debit == None :
            self.IDoperation_debit = DB.ReqInsert("compta_operations", listeDonnees)
        else :
            DB.ReqMAJ("compta_operations", listeDonnees, "IDoperation", self.IDoperation_debit)
            
        # CREDIT
        listeDonnees = [ 
            ("type", "credit"),
            ("date", date),
            ("libelle", libelle),
            ("IDcompte_bancaire", IDcompte_credit),
            ("IDreleve", IDreleve_credit),
            ("montant", montant),
            ("observations", observations),
            ]
        if self.IDoperation_credit == None :
            self.IDoperation_credit = DB.ReqInsert("compta_operations", listeDonnees)
        else :
            DB.ReqMAJ("compta_operations", listeDonnees, "IDoperation", self.IDoperation_credit)

        # VIREMENT
        listeDonnees = [ 
            ("IDoperation_debit", self.IDoperation_debit),
            ("IDoperation_credit", self.IDoperation_credit),
            ]
        if self.IDvirement == None :
            self.IDvirement = DB.ReqInsert("compta_virements", listeDonnees)
            DB.ReqMAJ("compta_operations", [("IDvirement", self.IDvirement),], "IDoperation", self.IDoperation_debit)
            DB.ReqMAJ("compta_operations", [("IDvirement", self.IDvirement),], "IDoperation", self.IDoperation_credit)
        
        DB.Close()

        return True
    
    def GetIDvirement(self):
        return self.IDvirement
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDvirement=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
