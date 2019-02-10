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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Utils import UTILS_Dates
from Ctrl import CTRL_Saisie_date
import datetime

from Ol import OL_Ventilation_operation
from Ctrl import CTRL_Saisie_releve_bancaire
from Ctrl import CTRL_Combobox_autocomplete




    

class CTRL_Mode(CTRL_Combobox_autocomplete.CTRL):
    def __init__(self, parent):
        CTRL_Combobox_autocomplete.CTRL.__init__(self, parent) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDmode, label, numero_piece, nbre_chiffres, 
        frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label
        FROM modes_reglements
        ORDER BY label;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDmode, label, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label in listeDonnees :
            self.dictDonnees[index] = { 
                "ID" : IDmode, "label" : label, "numero_piece" : numero_piece, "nbre_chiffres" : nbre_chiffres,
                "frais_gestion" : frais_gestion, "frais_montant" : frais_montant, "frais_pourcentage" : frais_pourcentage, 
                "frais_arrondi" : frais_arrondi, "frais_label" : frais_label, 
                }
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfosMode(self):
        """ Récupère les infos sur le mode sélectionné """
        index = self.GetValeur() #self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Tiers(CTRL_Combobox_autocomplete.CTRL):
    def __init__(self, parent):
        CTRL_Combobox_autocomplete.CTRL.__init__(self, parent) 
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
        req = """SELECT IDtiers, nom
        FROM compta_tiers
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDtiers, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDtiers }
            label = nom
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte_bancaire=None, typeOperation="credit", IDoperation=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_operation_tresorerie", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent 
        self.IDcompte_bancaire = IDcompte_bancaire
        self.typeOperation = typeOperation  
        self.IDoperation = IDoperation
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_date = wx.StaticText(self, wx.ID_ANY, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())
        self.label_libelle = wx.StaticText(self, wx.ID_ANY, _(u"Libellé :"))
        self.ctrl_libelle = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_tiers = wx.StaticText(self, wx.ID_ANY, _(u"Tiers :"))
        self.ctrl_tiers = CTRL_Tiers(self)
        self.label_mode = wx.StaticText(self, wx.ID_ANY, _(u"Mode :"))
        self.ctrl_mode = CTRL_Mode(self)
        self.label_num_cheque = wx.StaticText(self, wx.ID_ANY, _(u"N° Chq. :"))
        self.ctrl_num_cheque = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctrl_num_cheque.Enable(False) 
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Options"))
        self.label_releve = wx.StaticText(self, wx.ID_ANY, _(u"Relevé :"))
        self.ctrl_releve = CTRL_Saisie_releve_bancaire.CTRL(self, IDcompte_bancaire=self.IDcompte_bancaire, afficherBouton=False)
        self.label_num_piece = wx.StaticText(self, wx.ID_ANY, _(u"N° Pièce :"))
        self.ctrl_num_piece = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_observations = wx.StaticText(self, wx.ID_ANY, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        self.ctrl_observations.SetMinSize((200, -1))

        # Ventilation
        self.box_ventilation_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Ventilation"))
        self.listviewAvecFooter = OL_Ventilation_operation.ListviewAvecFooter(self, kwargs={"typeOperation" : self.typeOperation}) 
        self.ctrl_ventilation = self.listviewAvecFooter.GetListview()
        
        self.bouton_ajouter_ventilation = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_ventilation = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_ventilation = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.bouton_tiers = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_mode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTiers, self.bouton_tiers)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModes, self.bouton_mode)
        self.Bind(wx.EVT_BUTTON, self.ctrl_ventilation.Ajouter, self.bouton_ajouter_ventilation)
        self.Bind(wx.EVT_BUTTON, self.ctrl_ventilation.Modifier, self.bouton_modifier_ventilation)
        self.Bind(wx.EVT_BUTTON, self.ctrl_ventilation.Supprimer, self.bouton_supprimer_ventilation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.ctrl_num_cheque.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNumero)
        self.ctrl_mode.Bind(wx.EVT_COMBOBOX, self.OnChoixMode)
        self.ctrl_mode.Bind(wx.EVT_TEXT, self.OnChoixMode)
        
        # Importation de l'opération
        if self.IDoperation != None :
            self.Importation()
            titre = _(u"Modification d'une opération")
        else :
            titre = _(u"Saisie d'une opération")
        if self.typeOperation == "credit" : titre += _(u" au crédit")
        if self.typeOperation == "debit" : titre += _(u" au débit")
        self.SetTitle(titre)
        
        # Importation de la ventilation
        self.tracksInitial = []
        if self.IDoperation != None :
            self.tracksInitial = OL_Ventilation_operation.Importation(self.IDoperation)
            self.ctrl_ventilation.SetTracks(self.tracksInitial)
        self.ctrl_ventilation.MAJ() 
        
        # Focus
        self.ctrl_date.SetFocus() 
        wx.CallAfter(self.ctrl_date.SetInsertionPoint, 0)
                

    def __set_properties(self):
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez la date de l'opération")))
        self.ctrl_libelle.SetToolTip(wx.ToolTip(_(u"Saisissez un libellé")))
        self.ctrl_tiers.SetToolTip(wx.ToolTip(_(u"Sélectionnez un tiers")))
        self.bouton_tiers.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des tiers")))
        self.ctrl_mode.SetToolTip(wx.ToolTip(_(u"Sélectionnez un mode")))
        self.bouton_mode.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des modes")))
        self.ctrl_num_cheque.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de chèque")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez des observations")))
        self.ctrl_num_piece.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de pièce")))
        self.bouton_ajouter_ventilation.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une ventilation")))
        self.bouton_modifier_ventilation.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la ventilation sélectionnée")))
        self.bouton_supprimer_ventilation.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la ventilation sélectionnée")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((750, 520))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)

        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(5, 2, 10, 10)
        
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_date, 0, 0, 0)
        
        grid_sizer_generalites.Add(self.label_libelle, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_libelle, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_tiers, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_tiers = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_tiers.Add(self.ctrl_tiers, 0, wx.EXPAND, 0)
        grid_sizer_tiers.Add(self.bouton_tiers, 0, 0, 0)
        grid_sizer_tiers.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_tiers, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_mode, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_mode = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_mode.Add(self.ctrl_mode, 0, wx.EXPAND, 0)
        grid_sizer_mode.Add(self.bouton_mode, 0, 0, 0)
        grid_sizer_mode.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_mode, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_num_cheque, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_num_cheque, 0, 0, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_generalites, 1, wx.EXPAND, 0)
        
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(5, 2, 10, 10)
                
        grid_sizer_options.Add(self.label_releve, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_releve, 0, wx.EXPAND, 0)
        
        grid_sizer_options.Add(self.label_num_piece, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_num_piece, 0, wx.EXPAND, 0)

        grid_sizer_options.Add(self.label_observations, 0, wx.ALIGN_RIGHT , 0)
        grid_sizer_options.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        
        grid_sizer_options.AddGrowableRow(2)
        grid_sizer_options.AddGrowableCol(1)
        box_options.Add(grid_sizer_options, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_options, 1, wx.EXPAND, 0)
        
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Ventilation
        box_ventilation = wx.StaticBoxSizer(self.box_ventilation_staticbox, wx.VERTICAL)
        grid_sizer_ventilation = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_ventilation.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_ventilation = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_boutons_ventilation.Add(self.bouton_ajouter_ventilation, 0, 0, 0)
        grid_sizer_boutons_ventilation.Add(self.bouton_modifier_ventilation, 0, 0, 0)
        grid_sizer_boutons_ventilation.Add(self.bouton_supprimer_ventilation, 0, 0, 0)
        grid_sizer_ventilation.Add(grid_sizer_boutons_ventilation, 1, wx.EXPAND, 0)
        
        grid_sizer_ventilation.AddGrowableRow(0)
        grid_sizer_ventilation.AddGrowableCol(0)
        box_ventilation.Add(grid_sizer_ventilation, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_ventilation, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
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
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesoperationsdetresorerie")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonTiers(self, event): 
        IDtiers = self.ctrl_tiers.GetID()
        from Dlg import DLG_Tiers
        dlg = DLG_Tiers.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_tiers.MAJ()
        self.ctrl_tiers.SetID(IDtiers)

    def OnBoutonModes(self, event):  
        IDmode = self.ctrl_mode.GetID()
        from Dlg import DLG_Modes_reglements
        dlg = DLG_Modes_reglements.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_mode.MAJ()
        self.ctrl_mode.SetID(IDmode)
        self.OnChoixMode(None)

    def OnChoixMode(self, event): 
        self.FormateNumCheque()
        if event != None : 
            event.Skip() 

    def OnKillFocusNumero(self, event):
        self.FormateNumCheque() 
        if event != None : 
            event.Skip()

    def FormateNumCheque(self):
        """ Formate le numéro de chèque en fonction du paramétrage du mode de règlement """
        dictInfosMode = self.ctrl_mode.GetInfosMode()
        if dictInfosMode == None : return
        numero_piece = dictInfosMode["numero_piece"]
        nbre_chiffres = dictInfosMode["nbre_chiffres"]
        # Si aucun numéro de pièce
        if numero_piece == None : 
            self.ctrl_num_cheque.Enable(False)
        # Si alphanumérique :
        if numero_piece == "ALPHA" :
            self.ctrl_num_cheque.Enable(True)
        # Si numérique
        if numero_piece == "NUM" :
            self.ctrl_num_cheque.Enable(True)
            if nbre_chiffres != None:
                try :
                    numero = int(self.ctrl_num_cheque.GetValue())
                    self.ctrl_num_cheque.SetValue(("%0" + str(nbre_chiffres) + "d") % numero)
                except :
                    pass

    def OnBoutonReleves(self, event):  
        IDreleve = self.ctrl_releve.GetID()
        from Dlg import DLG_Releves_compta
        dlg = DLG_Releves_compta.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_releve.MAJ()
        self.ctrl_releve.SetID(IDreleve)

    def OnBoutonOk(self, event): 
        etat = self.Sauvegarde() 
        if etat == False :
            return
        self.EndModal(wx.ID_OK)
        
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT type, date, libelle, IDtiers, IDmode, num_piece, ref_piece, IDcompte_bancaire, IDreleve, montant, observations
        FROM compta_operations WHERE IDoperation=%d;""" % self.IDoperation
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        typeOperation, date, libelle, IDtiers, IDmode, num_piece, ref_piece, IDcompte_bancaire, IDreleve, montant, observations = listeTemp[0]
        date = UTILS_Dates.DateEngEnDateDD(date)
        
        self.ctrl_date.SetDate(date)
        self.ctrl_libelle.SetValue(libelle)
        self.ctrl_tiers.SetID(IDtiers)
        self.ctrl_mode.SetID(IDmode)
        self.OnChoixMode(None)
        self.ctrl_num_cheque.SetValue(num_piece)
        self.ctrl_num_piece.SetValue(ref_piece)
        self.ctrl_releve.SetID(IDreleve)
        self.ctrl_observations.SetValue(observations) 
        
        self.IDcompte_bancaire = IDcompte_bancaire
        self.typeOperation = typeOperation

    def Sauvegarde(self):
        date = self.ctrl_date.GetDate()
        libelle = self.ctrl_libelle.GetValue()
        IDtiers = self.ctrl_tiers.GetID()
        IDmode = self.ctrl_mode.GetID()
        IDreleve = self.ctrl_releve.GetID() 
        num_piece = self.ctrl_num_cheque.GetValue()
        ref_piece = self.ctrl_num_piece.GetValue()
        observations = self.ctrl_observations.GetValue()
        tracksVentilation = self.ctrl_ventilation.GetTracks() 
        
        # Validation des données saisies
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False

        if libelle == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un libellé pour cette opération !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_libelle.SetFocus()
            return False

        if IDtiers == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le tiers.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                self.ctrl_tiers.SetFocus()
                return False

        if IDmode == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le mode.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                self.ctrl_mode.SetFocus()
                return False

        if self.ctrl_num_cheque.IsEnabled() :
            if num_piece == "" :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le numéro de chèque.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    return False
        else :
            num_piece = ""
        
        # Calcul le montant total de la ventilation
        totalVentilation = 0.0
        for track in tracksVentilation :
            totalVentilation += track.montant

        if totalVentilation == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Le montant de cette opération est de 0.00 €.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return False

        # Sauvegarde de l'opération
        DB = GestionDB.DB()
        
        listeDonnees = [ 
            ("type", self.typeOperation),
            ("date", date),
            ("libelle", libelle),
            ("IDtiers", IDtiers),
            ("IDmode", IDmode),
            ("num_piece", num_piece),
            ("ref_piece", ref_piece),
            ("IDcompte_bancaire", self.IDcompte_bancaire),
            ("IDreleve", IDreleve),
            ("montant", totalVentilation),
            ("observations", observations),
            ]
        if self.IDoperation == None :
            self.IDoperation = DB.ReqInsert("compta_operations", listeDonnees)
        else :
            DB.ReqMAJ("compta_operations", listeDonnees, "IDoperation", self.IDoperation)
            
        # Sauvegarde des ventilations
        listeIDventilation = []
        for track in tracksVentilation :
            listeDonnees = [ 
                ("IDoperation", self.IDoperation),
                ("date_budget", track.date_budget),
                ("IDcategorie", track.IDcategorie),
                ("IDanalytique", track.IDanalytique),
                ("libelle", track.libelle),
                ("montant", track.montant),
                ]
            if track.IDventilation == None :
                IDventilation = DB.ReqInsert("compta_ventilation", listeDonnees)
            else :
                DB.ReqMAJ("compta_ventilation", listeDonnees, "IDventilation", track.IDventilation)
            listeIDventilation.append(track.IDventilation) 
            
        # Supprime les ventilations supprimées
        for track in self.tracksInitial :
            if track.IDventilation not in listeIDventilation :
                DB.ReqDEL("compta_ventilation", "IDventilation", track.IDventilation)
        
        DB.Close()

        return True
    
    def GetIDoperation(self):
        return self.IDoperation 
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcompte_bancaire=1, typeOperation="debit", IDoperation=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
