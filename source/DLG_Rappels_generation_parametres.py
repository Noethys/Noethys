#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime

import CTRL_Saisie_date
import CTRL_Selection_activites
import UTILS_Titulaires
import UTILS_Utilisateurs

from DLG_Factures_generation_parametres import CTRL_Lot_factures

import GestionDB



class CTRL_Lot_rappels(wx.Choice):
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
        FROM lots_rappels
        ORDER BY IDlot;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [_(u"Aucun lot"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDlot, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDlot, "nom " : nom}
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
        for IDfamille, dictTemp in titulaires.iteritems() :
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
        for index, values in self.dictDonnees.iteritems():
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
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Rappels_generation_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.box_date_reference_staticbox = wx.StaticBox(self, -1, _(u"Date de référence"))
        self.label_date_reference = wx.StaticText(self, -1, _(u"Jusqu'au"))
        self.ctrl_date_reference = CTRL_Saisie_date.Date2(self)
        
        # Lot
        self.box_lot_staticbox = wx.StaticBox(self, -1, _(u"Lot de lettres de rappel"))
        self.label_lot = wx.StaticText(self, -1, _(u"Lot :"))
        self.ctrl_lot = CTRL_Lot_rappels(self)
        self.bouton_lots = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.label_date_emission = wx.StaticText(self, -1, _(u"Date d'émission :"))
        self.ctrl_date_emission = CTRL_Saisie_date.Date2(self)
        
        # Elements
        self.box_elements_staticbox = wx.StaticBox(self, -1, _(u"Prestations à rechercher"))
        self.check_consommations = wx.CheckBox(self, -1, _(u"Consommations"))
        self.check_cotisations = wx.CheckBox(self, -1, _(u"Cotisations"))
        self.check_autres = wx.CheckBox(self, -1, _(u"Autres"))
        
        # Familles
        self.box_familles_staticbox = wx.StaticBox(self, -1, _(u"Sélection des familles"))
        
        self.radio_familles_toutes = wx.RadioButton(self, -1, _(u"Toutes les familles"), style=wx.RB_GROUP)
        
        self.radio_familles_unique = wx.RadioButton(self, -1, _(u"Uniquement la famille suivante :"))
        self.ctrl_famille = CTRL_Famille(self)
        
        self.radio_familles_prestations = wx.RadioButton(self, -1, _(u"Les familles qui n'ont aucune prestation :"))
        self.label_familles_prestations_min = wx.StaticText(self, -1, u"du")
        self.ctrl_familles_prestations_min = CTRL_Saisie_date.Date2(self)
        self.label_familles_prestations_max = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_familles_prestations_max = CTRL_Saisie_date.Date2(self)
        
        self.radio_familles_lot = wx.RadioButton(self, -1, _(u"Les familles qui n'ont aucune facture dans le lot de factures :"))
        self.ctrl_familles_lot = CTRL_Lot_factures(self)

        # Activités
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonLots, self.bouton_lots)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_unique)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_prestations)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_lot)
        
        # Init contrôles
        self.ctrl_date_reference.SetDate(datetime.date.today())
        self.ctrl_date_emission.SetDate(datetime.date.today())
        self.check_consommations.SetValue(True)
        self.check_cotisations.SetValue(True)
        self.check_autres.SetValue(True)
        self.OnRadioFamilles(None)        
        

    def __set_properties(self):
        self.ctrl_lot.SetToolTipString(_(u"Sélectionnez un lot de lettres de rappel à associer : Janvier 2013, Février, 2013, etc... Ce nom vous permettra de retrouver vos rappels facilement [Optionnel]"))
        self.bouton_lots.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des lots"))
        self.ctrl_date_emission.SetToolTipString(_(u"Saisissez ici la date d'émission la date des lettres de rappel (Par défaut la date du jour)"))
        self.ctrl_date_reference.SetToolTipString(_(u"Saisissez la date de référence avant laquelle Noethys recherchera des impayés"))
        self.check_consommations.SetToolTipString(_(u"Cochez cette case pour inclure les prestations de consommations"))
        self.check_cotisations.SetToolTipString(_(u"Cochez cette case pour inclure les prestations de cotisations"))
        self.check_autres.SetToolTipString(_(u"Cochez cette case pour inclure les autres types de prestations"))
        self.radio_familles_toutes.SetToolTipString(_(u"Cliquez ici pour rechercher les lettres de rappel de toutes les familles (par défaut)"))
        self.radio_familles_unique.SetToolTipString(_(u"Cliquez ici pour rechercher les lettres de rappel d'une seule famille"))
        self.ctrl_famille.SetToolTipString(_(u"Sélectionnez ici une famille"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_gauche = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Date de référence
        box_date_reference = wx.StaticBoxSizer(self.box_date_reference_staticbox, wx.VERTICAL)
        grid_sizer_date_reference = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_date_reference.Add(self.label_date_reference, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_reference.Add(self.ctrl_date_reference, 0, 0, 0)
        box_date_reference.Add(grid_sizer_date_reference, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_date_reference, 1, wx.EXPAND, 0)
        
        # Lot
        box_lot = wx.StaticBoxSizer(self.box_lot_staticbox, wx.VERTICAL)
        grid_sizer_lot = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_lot.Add(self.label_lot, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lot.Add(self.ctrl_lot, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lot.Add(self.bouton_lots, 0, 0, 0)
        grid_sizer_lot.AddGrowableCol(1)
        box_lot.Add(grid_sizer_lot, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_lot, 1, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.label_date_emission, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_date_emission, 0, 0, 0)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_parametres, 1, wx.EXPAND, 0)

        # Elements
        box_elements = wx.StaticBoxSizer(self.box_elements_staticbox, wx.VERTICAL)
        grid_sizer_elements = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_elements.Add(self.check_consommations, 0, 0, 0)
        grid_sizer_elements.Add(self.check_cotisations, 0, 0, 0)
        grid_sizer_elements.Add(self.check_autres, 0, 0, 0)
        grid_sizer_gauche.Add(box_elements, 1, wx.EXPAND, 0)
        box_elements.Add(grid_sizer_elements, 1, wx.ALL|wx.EXPAND, 10)
        
        # Familles
        box_familles = wx.StaticBoxSizer(self.box_familles_staticbox, wx.VERTICAL)
        grid_sizer_familles = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_familles.Add(self.radio_familles_toutes, 0, 0, 0)
        grid_sizer_familles.Add(self.radio_familles_unique, 0, 0, 0)
        grid_sizer_familles.Add(self.ctrl_famille, 0, wx.LEFT|wx.EXPAND, 18)
        
        grid_sizer_familles.Add(self.radio_familles_prestations, 0, wx.EXPAND, 0)

        grid_sizer_prestations = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_prestations.Add(self.label_familles_prestations_min, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestations.Add(self.ctrl_familles_prestations_min, 0, 0, 0)
        grid_sizer_prestations.Add(self.label_familles_prestations_max, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestations.Add(self.ctrl_familles_prestations_max, 0, 0, 0)

        grid_sizer_familles.Add(grid_sizer_prestations, 0, wx.LEFT|wx.EXPAND, 18)

        grid_sizer_familles.Add(self.radio_familles_lot, 0, wx.EXPAND, 0)
        grid_sizer_familles.Add(self.ctrl_familles_lot, 0, wx.LEFT|wx.EXPAND, 18)

        grid_sizer_familles.AddGrowableCol(0)
        box_familles.Add(grid_sizer_familles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_familles, 1, wx.EXPAND, 0)
        
        # Activités
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        grid_sizer_gauche.AddGrowableRow(4)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        box_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_activites, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnBoutonLots(self, event):
        IDlot = self.ctrl_lot.GetID()
        import DLG_Lots_rappels
        dlg = DLG_Lots_rappels.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_lot.MAJ() 
        if IDlot == None : IDlot = 0
        self.ctrl_lot.SetID(IDlot)

    def OnRadioFamilles(self, event):
        self.ctrl_famille.Enable(self.radio_familles_unique.GetValue())
        self.ctrl_familles_prestations_min.Enable(self.radio_familles_prestations.GetValue())
        self.ctrl_familles_prestations_max.Enable(self.radio_familles_prestations.GetValue())
        self.ctrl_familles_lot.Enable(self.radio_familles_lot.GetValue())

    def Validation(self):
        """ Validation des données saisies """
        # Vérifie date de référence
        date_reference = self.ctrl_date_reference.GetDate()
        if self.ctrl_date_reference.FonctionValiderDate() == False or date_reference == None :
            dlg = wx.MessageDialog(self, _(u"La date de référence ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_reference.SetFocus()
            return False

        # Vérifier si lot de lettres de rappel
        IDlot = self.ctrl_lot.GetID()
        if IDlot == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné de lot de lettres de rappel à associer. \n\nSouhaitez-vous quand même continuer ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            resultat = dlg.ShowModal()
            dlg.Destroy()
            if resultat != wx.ID_YES :
                return False
            
        # Date d'émission
        date_emission = self.ctrl_date_emission.GetDate()
        if self.ctrl_date_emission.FonctionValiderDate() == False or date_emission == None :
            dlg = wx.MessageDialog(self, _(u"La date d'émission ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_emission.SetFocus()
            return False

        # Vérifier si types de prestations indiquées
        prestations = []
        if self.check_consommations.GetValue() == True : prestations.append("consommation")
        if self.check_cotisations.GetValue() == True : prestations.append("cotisation")
        if self.check_autres.GetValue() == True : prestations.append("autre")
        if len(prestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un type de prestation à facturer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Familles
        IDcompte_payeur_unique = None
        if self.radio_familles_unique.GetValue() == True :
            IDcompte_payeur_unique = self.ctrl_famille.GetIDcompte_payeur() 
            if IDcompte_payeur_unique == None :
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné l'option 'famille unique' mais sans sélectionner de famille dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Vérifie les activités sélectionnées
        listeActivites = self.ctrl_activites.GetActivites() 
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Vérification droits utilisateurs
        for IDactivite in listeActivites :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_rappels", "creer", IDactivite=IDactivite, afficheMessage=False) == False : 
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas l'autorisation de générer des rappels pour l'ensemble des activités sélectionnées !"), _(u"Action non autorisée"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Recherche des exclusions de familles
        listeExclusions = []
        
        if self.radio_familles_prestations.GetValue() == True :
            date_debut = self.ctrl_familles_prestations_min.GetDate() 
            if self.ctrl_familles_prestations_min.FonctionValiderDate() == False or date_debut == None :
                dlg = wx.MessageDialog(self, _(u"La date de début de prestation ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_familles_prestations_min.SetFocus()
                return False

            date_fin = self.ctrl_familles_prestations_max.GetDate() 
            if self.ctrl_familles_prestations_max.FonctionValiderDate() == False or date_fin == None :
                dlg = wx.MessageDialog(self, _(u"La date de fin de prestation ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_familles_prestations_max.SetFocus()
                return False

            DB = GestionDB.DB()
            req = """SELECT IDcompte_payeur
            FROM prestations
            WHERE date>='%s' AND date<='%s'
            GROUP BY IDcompte_payeur;""" % (date_debut, date_fin)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            for IDcompte_payeur, in listeDonnees :
                listeExclusions.append(IDcompte_payeur)
            
        if self.radio_familles_lot.GetValue() == True :
            IDlot = self.ctrl_familles_lot.GetID()
            if IDlot == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné de lot de factures dans le filtre familles !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            DB = GestionDB.DB()
            req = """SELECT IDcompte_payeur
            FROM factures
            WHERE IDlot=%d
            GROUP BY IDcompte_payeur;""" % IDlot
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            for IDcompte_payeur, in listeDonnees :
                listeExclusions.append(IDcompte_payeur)


        # Envoi des données à DLG_Rappels_generation
        self.parent.dictParametres = {
            "date_reference" : date_reference,
            "IDlot" : IDlot,
            "date_edition" : date_emission,
            "prestations" : prestations,
            "IDcompte_payeur" : IDcompte_payeur_unique,
            "listeActivites" : listeActivites,
            "listeExceptionsComptes" : listeExclusions,
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
        self.radio_familles_prestations.Enable(False)
        self.label_familles_prestations_min.Enable(False)
        self.ctrl_familles_prestations_min.Enable(False)
        self.label_familles_prestations_max.Enable(False)
        self.ctrl_familles_prestations_max.Enable(False)
        self.radio_familles_lot.Enable(False)
        self.ctrl_familles_lot.Enable(False)



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
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        self.ctrl.Validation()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

