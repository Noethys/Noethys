#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import time
import sys
import math

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Selection_activites
from Ctrl import CTRL_Saisie_date
from Ol import OL_Attestations_prestations
from Ol import OL_Liste_regimes
import DLG_Attestations_selection

import FonctionsPerso
from Utils import UTILS_Utilisateurs


def ArrondirHeureSup(heures, minutes, pas): 
    """ Arrondi l'heure au pas supérieur """
    for x in range(0, 60, pas):
        if x >= minutes :
            return (heures, x)
    return (heures+1, 0)

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def FormateValeur(valeur, mode="decimal"):
    if mode == "decimal" :
        return valeur
    if mode == "heure" :
        hr, dec = str(valeur).split(".")
        if len(dec) == 1 : 
            mn = int(dec) * 0.1
        else:
            mn = int(dec) * 0.01
        mn = mn * 60 #int(dec)*60/100.0
        mn = math.ceil(mn)
        return u"%sh%02d" % (hr, mn)
        
##    if valeur == None or valeur == "" and mode == "decimal" : return 0.00
##    if valeur == None or valeur == "" and mode != "decimal" : return "0h00"
##    if type(valeur) == float and mode == "decimal" : return valeur
##    if type(valeur) == str :
##        hr, mn = valeur[1:].split(":")
##    if type(valeur) == datetime.timedelta :
##        hr, mn, sc = str(valeur).split(":")
##    if mode == "decimal" :
##        # Mode décimal
##        minDecimal = int(mn)*100/60
##        texte = "%s.%s" % (hr, minDecimal)
##        resultat = float(texte)
##    else:
##        # Mode Heure
##        if hr == "00" : hr = "0"
##        resultat = u"%s:%s" % (hr, mn)
##    return resultat



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
        self.check_dateNaiss = wx.CheckBox(self, -1, _(u"Date de naiss. :"))
        self.ctrl_dateNaiss = CTRL_Saisie_date.Date(self)
        
        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAge, self.check_dateNaiss)
        
        # Init Contrôles
        self.OnCheckAge(None)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))
        self.ctrl_dateNaiss.SetToolTip(wx.ToolTip(_(u"Saisissez une date de naissance maximale")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
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
        self.MAJprestations() 
    
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
        listeActivites = self.ctrl_activites.GetActivites() 
        self.parent.ctrl_prestations.MAJ(date_debut, date_fin, dateNaiss, listeActivites) 
    
    def GetActivites(self):
        return self.ctrl_activites.GetActivites() 
    

# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Pour éditer une attestation de présence, vous pouvez utiliser la fonction dédiée depuis une fiche famille. Mais pour éditer tout un lot d'attestations (Les attestations annuelles pour les impôts par exemple), il est plus rapide d'utiliser cette fonction. Commencez par définir vos paramètres de sélection puis cliquez sur Ok.")
        titre = _(u"Edition d'attestations de présence")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Generation.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # CTRL Prestations
        self.staticbox_prestations_staticbox = wx.StaticBox(self, -1, _(u"Prestations"))
        self.label_commentaires = wx.StaticText(self, -1, _(u"Double-cliquez dans la colonne 'Commentaire' pour afficher une information complémentaire sur la prestation."))
        self.ctrl_prestations = OL_Attestations_prestations.ListView(self, id=-1, name="OL_attestations_prestations", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Données Test
        anneeActuelle = datetime.date.today().year
        self.ctrl_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle, 1, 1))
        self.ctrl_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle, 12, 31))
        
        # Init contrôles
        self.ctrl_parametres.MAJprestations()

    def __set_properties(self):
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Ctrl des prestations
        staticbox_prestations = wx.StaticBoxSizer(self.staticbox_prestations_staticbox, wx.VERTICAL)
        staticbox_prestations.Add(self.label_commentaires, 0, wx.ALL|wx.EXPAND, 5)
        staticbox_prestations.Add(self.ctrl_prestations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(staticbox_prestations, 1, wx.RIGHT|wx.EXPAND, 5)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonOk(self, event):
        # Validation de la période
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate() 
        if self.ctrl_parametres.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de période semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate() 
        if self.ctrl_parametres.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de période semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"La date de début de période est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Validation de la date de naissance limite
        dateNaiss = None 
        if self.ctrl_parametres.check_dateNaiss.GetValue() == True :
            dateNaiss = self.ctrl_parametres.ctrl_dateNaiss.GetValue()
            if self.ctrl_parametres.ctrl_dateNaiss.FonctionValiderDate() == False or dateNaiss == None :
                dlg = wx.MessageDialog(self, _(u"La date de naissance semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_parametres.ctrl_dateNaiss.SetFocus()
                return
            else :
                dateNaiss = self.ctrl_parametres.ctrl_dateNaiss.GetDate()
        
        # Validation des activités
        listeActivites = self.ctrl_parametres.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérification droits utilisateurs
        for IDactivite in listeActivites :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_attestations", "creer", IDactivite=IDactivite, afficheMessage=False) == False : 
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas l'autorisation de générer des attestations pour l'ensemble des activités sélectionnées !"), _(u"Action non autorisée"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Validation des prestations
        listePrestations = self.ctrl_prestations.GetDonnees() 
        if len(listePrestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Ouvrir la DLG de sélection
        dlg = DLG_Attestations_selection.Dialog(self, date_debut=date_debut, date_fin=date_fin, dateNaiss=dateNaiss, listeActivites=listeActivites, listePrestations=listePrestations)
        reponse = dlg.ShowModal() 
        dlg.Destroy()

        if reponse == 200 :
            self.EndModal(wx.ID_OK)
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
