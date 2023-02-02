#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Selection_activites
from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Gestion

import GestionDB



class CTRL_Lot_factures(wx.Choice):
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
        req = """SELECT IDlot, nom
        FROM lots_factures
        ORDER BY IDlot DESC;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [_(u"Aucun lot"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDlot, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDlot, "nom" : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
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
        

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Prefixe_factures(wx.Choice):
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
        req = """SELECT IDprefixe, nom, prefixe
        FROM factures_prefixes
        ORDER BY prefixe;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [_(u"Aucun préfixe"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : None, "nom" : _(u"Aucun préfixe"), "prefixe" : None}
        index = 1
        for IDprefixe, nom, prefixe in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDprefixe, "nom" : nom, "prefixe" : prefixe}
            label = u"%s - %s" % (prefixe, nom)
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
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

    def GetPrefixe(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["prefixe"]

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Famille(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.SetMinSize((100, -1))
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
        titulaires = UTILS_Titulaires.GetTitulaires() 
        listeFamilles = []
        for IDfamille, dictTemp in titulaires.items() :
            listeFamilles.append((dictTemp["titulairesSansCivilite"], IDfamille, dictTemp["IDcompte_payeur"]))
        listeFamilles.sort()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "IDfamille" : 0, "nom" : _(u"Inconnue"), "IDcompte_payeur" : 0 }
        index = 1
        for nom, IDfamille, IDcompte_payeur in listeFamilles :
            self.dictDonnees[index] = { "IDfamille" : IDfamille, "nom " : nom, "IDcompte_payeur" : IDcompte_payeur}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetIDfamille(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["IDfamille"] == ID :
                 self.SetSelection(index)

    def GetIDfamille(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["IDfamille"]
    
    def GetIDcompte_payeur(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["IDcompte_payeur"]
            

# -----------------------------------------------------------------------------------------------------------------------


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Factures_generation_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Lot
        self.box_lot_staticbox = wx.StaticBox(self, -1, _(u"Lot de factures"))
        self.label_lot = wx.StaticText(self, -1, _(u"Lot :"))
        self.ctrl_lot = CTRL_Lot_factures(self)
        self.bouton_lots = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        # Paramètres
        self.label_prefixe = wx.StaticText(self, -1, _(u"Préfixe de numéro :"))
        self.ctrl_prefixe = CTRL_Prefixe_factures(self)
        self.bouton_prefixes = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.label_prochain_numero = wx.StaticText(self, -1, _(u"Prochain numéro :"))
        self.ctrl_prochain_numero = wx.TextCtrl(self, -1, u"", size=(95, -1))
        self.bouton_prochain_numero = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_ANY))
        self.check_numero_auto = wx.CheckBox(self, -1, _(u"Auto."))
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.label_date_emission = wx.StaticText(self, -1, _(u"Date d'émission :"))
        self.ctrl_date_emission = CTRL_Saisie_date.Date2(self)
        self.label_date_echeance = wx.StaticText(self, -1, _(u"Date d'échéance :"))
        self.ctrl_date_echeance = CTRL_Saisie_date.Date2(self)
        self.label_mention1 = wx.StaticText(self, -1, _(u"Mention 1 :"))
        self.ctrl_mention1 = wx.TextCtrl(self, -1, u"")
        self.label_mention2 = wx.StaticText(self, -1, _(u"Mention 2 :"))
        self.ctrl_mention2 = wx.TextCtrl(self, -1, u"")
        self.label_mention3 = wx.StaticText(self, -1, _(u"Mention 3 :"))
        self.ctrl_mention3 = wx.TextCtrl(self, -1, u"")

        # Elements
        self.box_elements_staticbox = wx.StaticBox(self, -1, _(u"Prestations à facturer"))
        self.check_consommations = wx.CheckBox(self, -1, _(u"Consommations"))
        self.check_cotisations = wx.CheckBox(self, -1, _(u"Cotisations"))
        self.check_locations = wx.CheckBox(self, -1, _(u"Locations"))
        self.check_autres = wx.CheckBox(self, -1, _(u"Autres"))
        
        # Familles
        self.box_familles_staticbox = wx.StaticBox(self, -1, _(u"Sélection des familles"))
        self.radio_familles_toutes = wx.RadioButton(self, -1, _(u"Toutes les familles"), style=wx.RB_GROUP)
        self.radio_familles_unique = wx.RadioButton(self, -1, _(u"Uniquement la famille suivante :"))
        self.ctrl_famille = CTRL_Famille(self)
        
        # Activités
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)

        # Inclure prestations antérieures non facturées
        self.box_anterieures_staticbox = wx.StaticBox(self, -1, _(u"Prestations antérieures non facturées"))
        self.check_prestations_anterieures = wx.CheckBox(self, -1, _(u"Inclure les prestations antérieures depuis le"))
        self.ctrl_date_anterieures = CTRL_Saisie_date.Date2(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonLots, self.bouton_lots)
        self.Bind(wx.EVT_CHOICE, self.OnChoixPrefixe, self.ctrl_prefixe)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonPrefixes, self.bouton_prefixes)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckNumeroAuto, self.check_numero_auto)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_unique)
        self.Bind(wx.EVT_BUTTON, self.AfficheProchainNumeroDefaut, self.bouton_prochain_numero)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAnterieures, self.check_prestations_anterieures)


        # Init contrôles
        self.ctrl_date_emission.SetDate(datetime.date.today())
        self.check_consommations.SetValue(True)
        self.check_cotisations.SetValue(True)
        self.check_locations.SetValue(True)
        self.check_autres.SetValue(True)
        self.OnRadioFamilles(None)
        self.OnCheckAnterieures(None)
                
        self.AfficheProchainNumeroDefaut()
        self.check_numero_auto.SetValue(True)
        self.OnCheckNumeroAuto()

        wx.CallLater(1, self.SendSizeEvent)

    def __set_properties(self):
        self.ctrl_prefixe.SetToolTip(wx.ToolTip(_(u"Sélectionnez un préfixe de numéro de factures dans la liste proposée. Cet paramètre permet d'obtenir des numéros de facture de type 'ABC-00001'.")))
        self.bouton_prefixes.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des préfixes de factures")))
        self.ctrl_lot.SetToolTip(wx.ToolTip(_(u"Sélectionnez un nom de lot à associer aux factures générées. Ex : Janvier 2013, Février, 2013, etc... Ce nom vous permettra de retrouver vos factures facilement [Optionnel]")))
        self.bouton_lots.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des lots")))
        self.ctrl_prochain_numero.SetToolTip(wx.ToolTip(_(u"Numéro de la prochaine facture générée. Vous pouvez modifier ce numéro si vous souhaitez par exemple modifier la numérotation en début d'année")))
        self.bouton_prochain_numero.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner automatiquement le prochain numéro de facture")))
        self.check_numero_auto.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour laisser Noethys sélectionner automatiquement le prochain numéro de facture")))
        self.ctrl_date_emission.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date d'émission la date des factures (Par défaut la date du jour)")))
        self.ctrl_date_echeance.SetToolTip(wx.ToolTip(_(u"Saisissez la date d'échéance de paiement qui apparaîtra sur la facture [Optionnel]")))
        self.ctrl_mention1.SetToolTip(wx.ToolTip(_(u"Saisissez une mention libre")))
        self.ctrl_mention2.SetToolTip(wx.ToolTip(_(u"Saisissez une mention libre")))
        self.ctrl_mention3.SetToolTip(wx.ToolTip(_(u"Saisissez une mention libre")))
        self.check_consommations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure les prestations de consommations")))
        self.check_cotisations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure les prestations de cotisations")))
        self.check_locations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure les prestations de locations")))
        self.check_autres.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure les autres types de prestations")))
        self.radio_familles_toutes.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour rechercher les factures de toutes les familles (par défaut)")))
        self.radio_familles_unique.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour rechercher les factures d'une seule famille")))
        self.ctrl_famille.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une famille")))
        self.check_prestations_anterieures.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure les prestations antérieures à la date de début non facturées depuis la date souhaitée")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_gauche = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_droit = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Période
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)

        # Lot
        box_lot = wx.StaticBoxSizer(self.box_lot_staticbox, wx.VERTICAL)
        grid_sizer_lot = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_gauche.Add(box_periode, 1, wx.EXPAND, 0)
        grid_sizer_lot.Add(self.label_lot, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lot.Add(self.ctrl_lot, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lot.Add(self.bouton_lots, 0, 0, 0)
        grid_sizer_lot.AddGrowableCol(1)
        box_lot.Add(grid_sizer_lot, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_lot, 1, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=7, cols=2, vgap=5, hgap=5)

        grid_sizer_parametres.Add(self.label_prefixe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_prefixe = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_prefixe.Add(self.ctrl_prefixe, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prefixe.Add(self.bouton_prefixes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prefixe.AddGrowableCol(0)
        grid_sizer_parametres.Add(grid_sizer_prefixe, 1, wx.EXPAND, 0)

        grid_sizer_parametres.Add(self.label_prochain_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_numero = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_numero.Add(self.ctrl_prochain_numero, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_numero.Add(self.bouton_prochain_numero, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_numero.Add(self.check_numero_auto, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_parametres.Add(grid_sizer_numero, 0, 0, 0)
        
        grid_sizer_parametres.Add(self.label_date_emission, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_date_emission, 0, 0, 0)
        grid_sizer_parametres.Add(self.label_date_echeance, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_date_echeance, 0, 0, 0)
        grid_sizer_parametres.Add(self.label_mention1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_mention1, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_mention2, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_mention2, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_mention3, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_mention3, 0, wx.EXPAND, 0)

        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_parametres, 1, wx.EXPAND, 0)

        # Familles
        box_familles = wx.StaticBoxSizer(self.box_familles_staticbox, wx.VERTICAL)
        grid_sizer_familles = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_familles.Add(self.radio_familles_toutes, 0, 0, 0)
        grid_sizer_familles.Add(self.radio_familles_unique, 0, 0, 0)
        grid_sizer_familles.Add(self.ctrl_famille, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_familles.AddGrowableCol(0)
        box_familles.Add(grid_sizer_familles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_familles, 1, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(4)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Activités
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)

        box_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(box_activites, 1, wx.EXPAND, 0)

        # Elements
        box_elements = wx.StaticBoxSizer(self.box_elements_staticbox, wx.VERTICAL)
        grid_sizer_elements = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_elements.Add(self.check_consommations, 0, 0, 0)
        grid_sizer_elements.Add(self.check_cotisations, 0, 0, 0)
        grid_sizer_elements.Add(self.check_locations, 0, 0, 0)
        grid_sizer_elements.Add(self.check_autres, 0, 0, 0)
        box_elements.Add(grid_sizer_elements, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(box_elements, 1, wx.EXPAND, 0)

        # Inclure prestations antérieures
        box_anterieures = wx.StaticBoxSizer(self.box_anterieures_staticbox, wx.VERTICAL)
        grid_sizer_anterieures = wx.FlexGridSizer(rows=1, cols=3, vgap=2, hgap=2)
        grid_sizer_anterieures.Add(self.check_prestations_anterieures, 0, wx.EXPAND, 0)
        grid_sizer_anterieures.Add(self.ctrl_date_anterieures, 0, wx.EXPAND, 0)
        box_anterieures.Add(grid_sizer_anterieures, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(box_anterieures, 1, wx.EXPAND, 0)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetMinSize(self.GetSize())

    def OnBoutonLots(self, event):
        IDlot = self.ctrl_lot.GetID()
        from Dlg import DLG_Lots_factures
        dlg = DLG_Lots_factures.Dialog(self)
        dlg.ShowModal()
        dernierLotCree = dlg.GetDernierLotCree()
        dlg.Destroy()
        self.ctrl_lot.MAJ() 
        if IDlot == None : IDlot = 0
        self.ctrl_lot.SetID(IDlot)
        if dernierLotCree != None :
            self.ctrl_lot.SetID(dernierLotCree)


    def OnChoixPrefixe(self, event=None):
        self.AfficheProchainNumeroDefaut()

    def OnBoutonPrefixes(self, event):
        IDprefixe = self.ctrl_prefixe.GetID()
        from Dlg import DLG_Prefixes_factures
        dlg = DLG_Prefixes_factures.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_prefixe.MAJ()
        self.ctrl_prefixe.SetID(IDprefixe)
        self.AfficheProchainNumeroDefaut()

    def OnRadioFamilles(self, event):
        self.ctrl_famille.Enable(self.radio_familles_unique.GetValue())
    
    def OnCheckNumeroAuto(self, event=None):
        etat = self.check_numero_auto.GetValue()
        self.ctrl_prochain_numero.Enable(not etat)
        self.bouton_prochain_numero.Enable(not etat)

    def OnCheckAnterieures(self, event=None):
        self.ctrl_date_anterieures.Enable(self.check_prestations_anterieures.GetValue())
        self.ctrl_date_anterieures.SetFocus()

    def Validation(self):
        """ Validation des données saisies """
        # Vérifie date début
        date_debut = self.ctrl_date_debut.GetDate()
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        
        # Vérifie date fin
        date_fin = self.ctrl_date_fin.GetDate()
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        # Vérifie les deux dates
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de début de période est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        # Vérifie que la période sélectionnée n'est pas dans une période de gestion
        gestion = UTILS_Gestion.Gestion(None)
        if gestion.IsPeriodeinPeriodes("factures", date_debut, date_fin) == False: return False

        # Vérifier si lot de factures
        IDlot = self.ctrl_lot.GetID()
        nomLot = self.ctrl_lot.GetNom()
        if IDlot == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné de lot de factures à associer.\n\nSouhaitez-vous quand même continuer ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            resultat = dlg.ShowModal()
            dlg.Destroy()
            if resultat != wx.ID_YES :
                return False

        # Préfixe de facture
        IDprefixe = self.ctrl_prefixe.GetID()
        prefixe = self.ctrl_prefixe.GetPrefixe()

        # Prochain numéro de facture
        if self.check_numero_auto.GetValue() == True :
            # Numéro auto
            prochain_numero = None
        else :
            # Numéro perso
            try :
                prochain_numero = int(self.ctrl_prochain_numero.GetValue())
            except :
                prochain_numero = None
            if prochain_numero in (None, "") :
                dlg = wx.MessageDialog(self, _(u"Le prochain numéro de facture ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_prochain_numero.SetFocus()
                return False
            
            if prochain_numero < self.prochain_numero_defaut :
                dlg = wx.MessageDialog(self, _(u"Le prochain numéro de facture n'est pas valide : une facture générée porte déjà un numéro égal ou supérieur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_prochain_numero.SetFocus()
                return False
        
        # Date d'émission
        date_emission = self.ctrl_date_emission.GetDate()
        if self.ctrl_date_emission.FonctionValiderDate() == False or date_emission == None :
            dlg = wx.MessageDialog(self, _(u"La date d'émission ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_emission.SetFocus()
            return False

        # Date d'échéance
        date_echeance = self.ctrl_date_echeance.GetDate()
        if date_echeance == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas saisi de date d'échéance. \n\nSouhaitez-vous quand même continuer ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            resultat = dlg.ShowModal()
            dlg.Destroy()
            if resultat != wx.ID_YES :
                return False

        # Vérifier si lot de factures
        prestations = []
        if self.check_consommations.GetValue() == True : prestations.append("consommation")
        if self.check_cotisations.GetValue() == True : prestations.append("cotisation")
        if self.check_locations.GetValue() == True: prestations.append("location")
        if self.check_autres.GetValue() == True : prestations.append("autre")
        if len(prestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un type de prestation à facturer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Familles
        if self.radio_familles_toutes.GetValue() == True :
            IDcompte_payeur_unique = None
        else :
            IDcompte_payeur_unique = self.ctrl_famille.GetIDcompte_payeur() 
            if IDcompte_payeur_unique == None :
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné l'option 'famille unique' mais sans sélectionner de famille dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Vérifie les activités sélectionnées
        listeActivites = self.ctrl_activites.GetActivites() 
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité.\n\nSouhaitez-vous quand même continuer ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            resultat = dlg.ShowModal()
            dlg.Destroy()
            if resultat != wx.ID_YES :
                return False

        # Date antérieure
        date_anterieure = None
        if self.check_prestations_anterieures.GetValue() == True :
            date_anterieure = self.ctrl_date_anterieures.GetDate()
            if self.ctrl_date_anterieures.FonctionValiderDate() == False or date_anterieure == None:
                dlg = wx.MessageDialog(self, _(u"La date antérieure ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_anterieures.SetFocus()
                return False

        # Vérification droits utilisateurs
        for IDactivite in listeActivites :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_factures", "creer", IDactivite=IDactivite, afficheMessage=False) == False : 
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas l'autorisation de générer des factures pour l'ensemble des activités sélectionnées !"), _(u"Action non autorisée"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Vérifie la compatibilité des régies des activités sélectionnées
        IDregie = None
        if len(listeActivites) >= 1 :
            listeAllRegies = []
            for IDactivite in listeActivites :
                DB=GestionDB.DB()
                req = """SELECT regie
                FROM activites
                WHERE IDactivite = %d""" % IDactivite
                DB.ExecuterReq(req)
                listeresult = DB.ResultatReq()
                result = listeresult[0]
                listeAllRegies.append(result[0])
                DB.Close()
            listeRegies = list(set(listeAllRegies))
            if len(listeRegies) > 1 :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas générer des factures pour l'ensemble des activités sélectionnées !\n\nCertaines activités sont liées à des régies différentes"), _(u"Régies différentes"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else :
                IDregie = listeRegies[0]

        # Envoi des données à DLG_Factures_generation
        self.parent.dictParametres = {
            "date_debut" : date_debut,
            "date_fin" : date_fin,
            "IDlot" : IDlot,
            "nomLot" : nomLot,
            "date_emission" : date_emission,
            "date_echeance" : date_echeance,
            "prochain_numero" : prochain_numero,
            "prestations" : prestations,
            "IDcompte_payeur" : IDcompte_payeur_unique,
            "listeActivites" : listeActivites,
            "IDprefixe" : IDprefixe,
            "prefixe" : prefixe,
            "date_anterieure" : date_anterieure,
            "IDregie" : IDregie,
            "mention1" : self.ctrl_mention1.GetValue(),
            "mention2" : self.ctrl_mention2.GetValue(),
            "mention3" : self.ctrl_mention3.GetValue(),
            }

        return True
    
    def MAJ(self):
        pass

    def SetFamille(self, IDfamille=None):
        self.radio_familles_unique.SetValue(True)
        self.ctrl_famille.SetIDfamille(IDfamille)
        self.OnRadioFamilles(None)
        self.radio_familles_toutes.Enable(False)
        self.radio_familles_unique.Enable(False)
        self.ctrl_famille.Enable(False)
    
    def AfficheProchainNumeroDefaut(self, event=None):
        """ Recherche numéro de facture suivant """
        # Recherche du prochain numéro de facture
        IDprefixe = self.ctrl_prefixe.GetID()
        if IDprefixe == None :
            conditions = "WHERE IDprefixe IS NULL"
        else :
            conditions = "WHERE IDprefixe=%d" % IDprefixe
        DB = GestionDB.DB()
        req = """SELECT MAX(numero)
        FROM factures
        %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if listeDonnees[0][0] == None :
            self.prochain_numero_defaut = 1
        else:
            self.prochain_numero_defaut = listeDonnees[0][0] + 1

        # Affichage du numéro trouvé
        self.ctrl_prochain_numero.SetValue(str(self.prochain_numero_defaut))





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.panel = panel
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        self.ctrl.Validation()
        print(self.panel.dictParametres)

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

