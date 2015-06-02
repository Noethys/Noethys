#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import time
import sys
import math

import GestionDB
import CTRL_Bandeau
import CTRL_Selection_activites
import CTRL_Saisie_date
import OL_Attestations_fiscales_prestations
import DLG_Attestations_fiscales_selection

import FonctionsPerso
import UTILS_Utilisateurs

import wx.lib.agw.pybusyinfo as PBI



class CTRL_Modes_reglements(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeModes, self.dictModes = self.Importation()
        self.SetListeChoix()
        self.SetMinSize((-1, 80))

    def Importation(self):
        listeModes = []
        dictModes = {}
        DB = GestionDB.DB()
        req = """SELECT IDmode, label FROM modes_reglements ORDER BY label;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDmode, label in listeDonnees :
            dictModes[IDmode] = label
            listeModes.append((label, IDmode))
        return listeModes, dictModes

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for label, IDmode in self.listeModes :
            self.Append(label)
            index += 1
        self.CocheTout() 
        
    def GetIDcoches(self, modeTexte=False):
        listeIDcoches = []
        NbreItems = len(self.listeModes)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                if modeTexte == False :
                    ID = self.listeModes[index][1]
                else:
                    ID = str(self.listeModes[index][1])
                listeIDcoches.append(ID)
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeModes)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeModes)):
            ID = self.listeModes[index][1]
            if ID in listeIDcoches or str(ID) in listeIDcoches :
                self.Check(index)
            index += 1
    
# ----------------------------------------------------------------------------------------------------------------------------------




class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de référence"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Séparation
        self.staticbox_dateNaiss_staticbox = wx.StaticBox(self, -1, _(u"Limite d'âge"))
        self.check_dateNaiss = wx.CheckBox(self, -1, _(u"Date de naissance min. :"))
        self.ctrl_dateNaiss = CTRL_Saisie_date.Date(self)
        
        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)

        # Modes de règlements
        self.staticbox_modes_staticbox = wx.StaticBox(self, -1, _(u"Modes de règlement"))
        self.ctrl_modes = CTRL_Modes_reglements(self)

        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAge, self.check_dateNaiss)
        
        # Init Contrôles
        self.OnCheckAge(None)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de période"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin de période"))
        self.ctrl_dateNaiss.SetToolTipString(_(u"Saisissez une date de naissance maximale"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=4, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Date de naissance max
        staticbox_dateNaiss = wx.StaticBoxSizer(self.staticbox_dateNaiss_staticbox, wx.VERTICAL)        
        grid_sizer_dateNaiss = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_dateNaiss.Add(self.check_dateNaiss, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dateNaiss.Add(self.ctrl_dateNaiss, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_dateNaiss.Add(grid_sizer_dateNaiss, 0, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_dateNaiss, 1, wx.RIGHT|wx.EXPAND, 5)
                
        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)

        # Modess de règlements
        staticbox_modes = wx.StaticBoxSizer(self.staticbox_modes_staticbox, wx.VERTICAL)
        staticbox_modes.Add(self.ctrl_modes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_modes, 1, wx.RIGHT|wx.EXPAND, 5)

        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND|wx.RIGHT, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnCheckAge(self, event):
        etat = self.check_dateNaiss.GetValue()
        self.ctrl_dateNaiss.Enable(etat)
        if etat == True :
            self.ctrl_dateNaiss.SetFocus()

    def OnBoutonActualiser(self, event): 
        # Validation de la période
        date_debut = self.ctrl_date_debut.GetDate() 
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de période semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        date_fin = self.ctrl_date_fin.GetDate() 
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de période semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"La date de début de période est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Validation de la date de naissance limite
        dateNaiss = None 
        if self.check_dateNaiss.GetValue() == True :
            dateNaiss = self.ctrl_dateNaiss.GetValue()
            if self.ctrl_dateNaiss.FonctionValiderDate() == False or dateNaiss == None :
                dlg = wx.MessageDialog(self, _(u"La date de naissance semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_dateNaiss.SetFocus()
                return False
            else :
                dateNaiss = self.ctrl_dateNaiss.GetDate()
        
        # Validation des activités
        listeActivites = self.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Validation des modes de règlement
        listeModes = self.GetModes()
        if len(listeModes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un mode de règlement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Vérification droits utilisateurs
        for IDactivite in listeActivites :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_attestations", "creer", IDactivite=IDactivite, afficheMessage=False) == False : 
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas l'autorisation de générer des attestations pour l'ensemble des activités sélectionnées !"), _(u"Action non autorisée"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # MAJ de la liste des prestations
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des données..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        try :
            self.MAJprestations() 
            del dlgAttente
        except Exception, err :
            print err
            del dlgAttente
    
    def OnCheckActivites(self):
##        self.MAJprestations() 
        pass
    
    def MAJprestations(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if self.check_dateNaiss.GetValue() == True :
            dateNaiss = self.ctrl_dateNaiss.GetDate()
        else:
            dateNaiss = None
        listeActivites = self.GetActivites() 
        listeModes = self.GetModes() 
        self.parent.ctrl_prestations.MAJ(date_debut, date_fin, dateNaiss, listeActivites, listeModes) 
    
    def GetActivites(self):
        return self.ctrl_activites.GetActivites() 
    
    def GetModes(self):
        return self.ctrl_modes.GetIDcoches() 
    
    

# --------------------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
                
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # CTRL Prestations
        self.staticbox_prestations_staticbox = wx.StaticBox(self, -1, _(u"Prestations"))
        self.label_commentaires = wx.StaticText(self, -1, _(u"Double-cliquez dans la colonne 'Ajustement' pour créer un ajustement sur chaque prestation (Ex : '+3.5' ou '-2.5')."))
        self.ctrl_prestations = OL_Attestations_fiscales_prestations.ListView(self, id=-1, name="OL_attestations_prestations", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.__do_layout()
        
        # Données par défaut
        anneeActuelle = datetime.date.today().year
        self.ctrl_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle-1, 1, 1))
        self.ctrl_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle-1, 12, 31))
        self.ctrl_parametres.ctrl_dateNaiss.SetDate(datetime.date(anneeActuelle-7, 1, 1))
        
        # Init contrôles
        self.ctrl_parametres.MAJprestations()

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Ctrl des prestations
        staticbox_prestations = wx.StaticBoxSizer(self.staticbox_prestations_staticbox, wx.VERTICAL)
        staticbox_prestations.Add(self.label_commentaires, 0, wx.ALL|wx.EXPAND, 5)
        staticbox_prestations.Add(self.ctrl_prestations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(staticbox_prestations, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout() 

    def Validation(self):
        # Validation des prestations
        listePrestations = self.ctrl_prestations.GetTracksCoches() 
        if len(listePrestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Validation des ajustements
        for track in listePrestations :
            if track.ajustement not in ("", None) :
                try :
                    ajustement = float(track.ajustement)
                except :
                    dlg = wx.MessageDialog(self, _(u"L'ajustement que vous avez paramétré pour la prestation '%s' semble erroné !\n\nVous pouvez uniquement saisir des valeurs du type '-2.5' ou '+5'.") % track.label, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False


        return True
    
    def GetPeriode(self):
        return self.ctrl_parametres.ctrl_date_debut.GetDate(), self.ctrl_parametres.ctrl_date_fin.GetDate() 
    
    def GetPrestations(self):
        return self.ctrl_prestations.GetTracksCoches() 

    def GetActivites(self):
        return self.ctrl_parametres.GetActivites()

    def MAJ(self):
        pass



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1)
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
        # Test d'affichage des résultats
        listePrestations = self.ctrl.GetPrestations()
        import OL_Attestations_fiscales_selection
        frm = OL_Attestations_fiscales_selection.MyFrame(self, listePrestations)
        frm.SetSize((900, 500))
        frm.Show()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    frame_1.SetSize((980, 650))
    frame_1.CenterOnScreen() 
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
