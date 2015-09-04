#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime

import CTRL_Saisie_date
import CTRL_Selection_activites
import UTILS_Titulaires
import UTILS_Utilisateurs

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
        ORDER BY IDlot;"""
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
        for index, values in self.dictDonnees.iteritems():
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
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Factures_generation_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # P�riode
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"P�riode"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Lot
        self.box_lot_staticbox = wx.StaticBox(self, -1, _(u"Lot de factures"))
        self.label_lot = wx.StaticText(self, -1, _(u"Lot :"))
        self.ctrl_lot = CTRL_Lot_factures(self)
        self.bouton_lots = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        # Param�tres
        self.label_prochain_numero = wx.StaticText(self, -1, _(u"Prochain num�ro :"))
        self.ctrl_prochain_numero = wx.TextCtrl(self, -1, u"", size=(95, -1))
        self.bouton_prochain_numero = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Actualiser2.png", wx.BITMAP_TYPE_ANY))
        self.check_numero_auto = wx.CheckBox(self, -1, _(u"Auto."))
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.label_date_emission = wx.StaticText(self, -1, _(u"Date d'�mission :"))
        self.ctrl_date_emission = CTRL_Saisie_date.Date2(self)
        self.label_date_echeance = wx.StaticText(self, -1, _(u"Date d'�ch�ance :"))
        self.ctrl_date_echeance = CTRL_Saisie_date.Date2(self)
        
        # Elements
        self.box_elements_staticbox = wx.StaticBox(self, -1, _(u"Prestations � facturer"))
        self.check_consommations = wx.CheckBox(self, -1, _(u"Consommations"))
        self.check_cotisations = wx.CheckBox(self, -1, _(u"Cotisations"))
        self.check_autres = wx.CheckBox(self, -1, _(u"Autres"))
        
        # Familles
        self.box_familles_staticbox = wx.StaticBox(self, -1, _(u"S�lection des familles"))
        self.radio_familles_toutes = wx.RadioButton(self, -1, _(u"Toutes les familles"), style=wx.RB_GROUP)
        self.radio_familles_unique = wx.RadioButton(self, -1, _(u"Uniquement la famille suivante :"))
        self.ctrl_famille = CTRL_Famille(self)
        
        # Activit�s
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activit�s"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonLots, self.bouton_lots)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckNumeroAuto, self.check_numero_auto)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFamilles, self.radio_familles_unique)
        self.Bind(wx.EVT_BUTTON, self.AfficheProchainNumeroDefaut, self.bouton_prochain_numero)
        
        # Init contr�les
        self.ctrl_date_emission.SetDate(datetime.date.today())
        self.check_consommations.SetValue(True)
        self.check_cotisations.SetValue(True)
        self.check_autres.SetValue(True)
        self.OnRadioFamilles(None)
                
        # Recherche du prochain num�ro de facture
        DB = GestionDB.DB()
        req = """SELECT MAX(numero) FROM factures;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()  
        DB.Close() 
        if listeDonnees[0][0] == None :
            self.prochain_numero_defaut = 1
        else:
            self.prochain_numero_defaut = listeDonnees[0][0] + 1
        self.AfficheProchainNumeroDefaut()
        self.check_numero_auto.SetValue(True)
        self.OnCheckNumeroAuto()

    def __set_properties(self):
        self.ctrl_lot.SetToolTipString(_(u"S�lectionnez un nom de lot � associer aux factures g�n�r�es. Ex : Janvier 2013, F�vrier, 2013, etc... Ce nom vous permettra de retrouver vos factures facilement [Optionnel]"))
        self.bouton_lots.SetToolTipString(_(u"Cliquez ici pour acc�der � la gestion des lots"))
        self.ctrl_prochain_numero.SetToolTipString(_(u"Num�ro de la prochaine facture g�n�r�e. Vous pouvez modifier ce num�ro si vous souhaitez par exemple modifier la num�rotation en d�but d'ann�e"))
        self.bouton_prochain_numero.SetToolTipString(_(u"Cliquez ici pour s�lectionner automatiquement le prochain num�ro de facture"))
        self.check_numero_auto.SetToolTipString(_(u"Cochez cette case pour laisser Noethys s�lectionner automatiquement le prochain num�ro de facture"))
        self.ctrl_date_emission.SetToolTipString(_(u"Saisissez ici la date d'�mission la date des factures (Par d�faut la date du jour)"))
        self.ctrl_date_echeance.SetToolTipString(_(u"Saisissez la date d'�ch�ance de paiement qui appara�tra sur la facture [Optionnel]"))
        self.check_consommations.SetToolTipString(_(u"Cochez cette case pour inclure les prestations de consommations"))
        self.check_cotisations.SetToolTipString(_(u"Cochez cette case pour inclure les prestations de cotisations"))
        self.check_autres.SetToolTipString(_(u"Cochez cette case pour inclure les autres types de prestations"))
        self.radio_familles_toutes.SetToolTipString(_(u"Cliquez ici pour rechercher les factures de toutes les familles (par d�faut)"))
        self.radio_familles_unique.SetToolTipString(_(u"Cliquez ici pour rechercher les factures d'une seule famille"))
        self.ctrl_famille.SetToolTipString(_(u"S�lectionnez ici une famille"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_gauche = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)


        # P�riode
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

        # Param�tres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        
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
        grid_sizer_familles = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_familles.Add(self.radio_familles_toutes, 0, 0, 0)
        grid_sizer_familles.Add(self.radio_familles_unique, 0, 0, 0)
        grid_sizer_familles.Add(self.ctrl_famille, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_familles.AddGrowableRow(2)
        grid_sizer_familles.AddGrowableCol(0)
        box_familles.Add(grid_sizer_familles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_familles, 1, wx.EXPAND, 0)
        
        # Activit�s
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        grid_sizer_gauche.AddGrowableRow(4)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        box_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_activites, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)

    def OnBoutonLots(self, event):
        IDlot = self.ctrl_lot.GetID()
        import DLG_Lots_factures
        dlg = DLG_Lots_factures.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_lot.MAJ() 
        if IDlot == None : IDlot = 0
        self.ctrl_lot.SetID(IDlot)

    def OnRadioFamilles(self, event):
        self.ctrl_famille.Enable(self.radio_familles_unique.GetValue())
    
    def OnCheckNumeroAuto(self, event=None):
        etat = self.check_numero_auto.GetValue()
        self.ctrl_prochain_numero.Enable(not etat)
        self.bouton_prochain_numero.Enable(not etat)
        
    def Validation(self):
        """ Validation des donn�es saisies """
        # V�rifie date d�but
        date_debut = self.ctrl_date_debut.GetDate()
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de d�but de p�riode ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        
        # V�rifie date fin
        date_fin = self.ctrl_date_fin.GetDate()
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de p�riode ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        # V�rifie les deux dates
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de d�but de p�riode est sup�rieure � la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        # V�rifier si lot de factures
        IDlot = self.ctrl_lot.GetID()
        nomLot = self.ctrl_lot.GetNom()
        if IDlot == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas s�lectionn� de lot de factures � associer.\n\nSouhaitez-vous quand m�me continuer ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            resultat = dlg.ShowModal()
            dlg.Destroy()
            if resultat != wx.ID_YES :
                return False
        
        # Prochain num�ro de facture
        if self.check_numero_auto.GetValue() == True :
            # Num�ro auto
            prochain_numero = None
        else :
            # Num�ro perso
            try :
                prochain_numero = int(self.ctrl_prochain_numero.GetValue())
            except :
                prochain_numero = None
            if prochain_numero in (None, "") :
                dlg = wx.MessageDialog(self, _(u"Le prochain num�ro de facture ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_prochain_numero.SetFocus()
                return False
            
            if prochain_numero < self.prochain_numero_defaut :
                dlg = wx.MessageDialog(self, _(u"Le prochain num�ro de facture n'est pas valide : une facture g�n�r�e porte d�j� un num�ro �gal ou sup�rieur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_prochain_numero.SetFocus()
                return False
        
        # Date d'�mission
        date_emission = self.ctrl_date_emission.GetDate()
        if self.ctrl_date_emission.FonctionValiderDate() == False or date_emission == None :
            dlg = wx.MessageDialog(self, _(u"La date d'�mission ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_emission.SetFocus()
            return False

        # Date d'�ch�ance
        date_echeance = self.ctrl_date_echeance.GetDate()
        if date_echeance == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas saisi de date d'�ch�ance. \n\nSouhaitez-vous quand m�me continuer ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            resultat = dlg.ShowModal()
            dlg.Destroy()
            if resultat != wx.ID_YES :
                return False

        # V�rifier si lot de factures
        prestations = []
        if self.check_consommations.GetValue() == True : prestations.append("consommation")
        if self.check_cotisations.GetValue() == True : prestations.append("cotisation")
        if self.check_autres.GetValue() == True : prestations.append("autre")
        if len(prestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un type de prestation � facturer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Familles
        if self.radio_familles_toutes.GetValue() == True :
            IDcompte_payeur_unique = None
        else :
            IDcompte_payeur_unique = self.ctrl_famille.GetIDcompte_payeur() 
            if IDcompte_payeur_unique == None :
                dlg = wx.MessageDialog(self, _(u"Vous avez s�lectionn� l'option 'famille unique' mais sans s�lectionner de famille dans la liste propos�e !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # V�rifie les activit�s s�lectionn�es
        listeActivites = self.ctrl_activites.GetActivites() 
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # V�rification droits utilisateurs
        for IDactivite in listeActivites :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_factures", "creer", IDactivite=IDactivite, afficheMessage=False) == False : 
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas l'autorisation de g�n�rer des factures pour l'ensemble des activit�s s�lectionn�es !"), _(u"Action non autoris�e"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Envoi des donn�es � DLG_Factures_generation
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
        """ Recherche num�ro de facture suivant """
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
        print self.panel.dictParametres

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

