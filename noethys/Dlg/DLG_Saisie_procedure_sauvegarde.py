#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import socket
import six

from Dlg import DLG_Sauvegarde
from Ctrl import CTRL_Saisie_heure
from Utils import UTILS_Identification
import GestionDB

from Utils.UTILS_Divers import ConvertChaineEnListe, ConvertListeEnChaine




class CTRL_Utilisateurs(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((50, 50))
        self.dictDonnees = {}
        self.dictIndex = {}
        self.MAJ() 
        
    def MAJ(self):
        self.listeDonnees = self.Importation()
        self.Clear()
        self.dictIndex = {}
        if self.listeDonnees == None : return
        self.listeDonnees.sort()
        index = 0
        for nom, IDutilisateur in self.listeDonnees :
            self.Append(nom) 
            self.dictIndex[index] = IDutilisateur
            index += 1
    
    def Importation(self):
        """ Récupère la liste des utilisateurs dans la base """
        listeUtilisateurs = []
        DB = GestionDB.DB()
        req = """SELECT IDutilisateur, sexe, nom, prenom, mdp, profil, actif
        FROM utilisateurs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDutilisateur, sexe, nom, prenom, mdp, profil, actif in listeDonnees :
            nomComplet = u"%s %s" % (nom, prenom)
            listeUtilisateurs.append((nomComplet, IDutilisateur))
        listeUtilisateurs.sort()
        return listeUtilisateurs

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                IDutilisateur = self.dictIndex[index]
                listeIDcoches.append(IDutilisateur)
        listeIDcoches.sort() 
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetDonneesStr(self):
        listeID = self.GetIDcoches() 
        return ConvertListeEnChaine(listeID)
        
    def SetDonneesStr(self, texte="") :
        listeID = ConvertChaineEnListe(texte)
        self.SetIDcoches(listeID)
            
            
            

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Conditions(wx.Panel) :
    def __init__(self, parent) :
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        # Jour
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        self.box_jour_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Jour"))
        self.check_jour = wx.CheckBox(self, wx.ID_ANY, _(u"Si le jour est parmi les jours cochés :"))
        self.label_jours_scolaire = wx.StaticText(self, wx.ID_ANY, _(u"Sem. scolaires : "))
        self.check_scolaire_lundi = wx.CheckBox(self, wx.ID_ANY, u"L")
        self.check_scolaire_mardi = wx.CheckBox(self, wx.ID_ANY, u"M")
        self.check_scolaire_mercredi = wx.CheckBox(self, wx.ID_ANY, u"M")
        self.check_scolaire_jeudi = wx.CheckBox(self, wx.ID_ANY, u"J")
        self.check_scolaire_vendredi = wx.CheckBox(self, wx.ID_ANY, u"V")
        self.check_scolaire_samedi = wx.CheckBox(self, wx.ID_ANY, u"S")
        self.check_scolaire_dimanche = wx.CheckBox(self, wx.ID_ANY, u"D")
        self.label_jours_vacances = wx.StaticText(self, wx.ID_ANY, _(u"Sem. vacances : "))
        self.check_vacances_lundi = wx.CheckBox(self, wx.ID_ANY, u"L")
        self.check_vacances_mardi = wx.CheckBox(self, wx.ID_ANY, u"M")
        self.check_vacances_mercredi = wx.CheckBox(self, wx.ID_ANY, u"M")
        self.check_vacances_jeudi = wx.CheckBox(self, wx.ID_ANY, u"J")
        self.check_vacances_vendredi = wx.CheckBox(self, wx.ID_ANY, u"V")
        self.check_vacances_samedi = wx.CheckBox(self, wx.ID_ANY, u"S")
        self.check_vacances_dimanche = wx.CheckBox(self, wx.ID_ANY, u"D")
        
        # Heure
        self.box_heure_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Heure"))
        self.check_heure = wx.CheckBox(self, wx.ID_ANY, _(u"Si l'heure est comprise entre"))
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.label_heure_et = wx.StaticText(self, wx.ID_ANY, _(u"et"))
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)

        # Poste
        self.box_poste_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Poste"))
        self.check_poste = wx.CheckBox(self, wx.ID_ANY, _(u"Si le poste est :"))
        try :
            if six.PY2:
                labelPoste = _(u"Ce poste (%s)") % socket.gethostname().decode("utf8")
            else :
                labelPoste = _(u"Ce poste (%s)") % socket.gethostname()
        except :
            labelPoste = _(u"Ce poste")
        self.radio_poste_1 = wx.RadioButton(self, wx.ID_ANY, labelPoste, style=wx.RB_GROUP)
        self.radio_poste_2 = wx.RadioButton(self, wx.ID_ANY, _(u"Parmi les postes suivants :"))
        self.ctrl_postes = wx.TextCtrl(self, wx.ID_ANY, u"")#, style=wx.TE_MULTILINE)

        # Dernière sauvegarde
        self.box_derniere_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Dernière sauvegarde"))
        self.check_derniere = wx.CheckBox(self, wx.ID_ANY, _(u"Si dernière sauv. date de plus de"))
        self.listeDelais = [(1, _(u"1 jour")), ]
        for x in range(2, 31) :
            self.listeDelais.append((x, _(u"%d jours") % x))
        listeLabels = []
        for valeur, label in self.listeDelais :
            listeLabels.append(label)
        self.ctrl_derniere = wx.Choice(self, wx.ID_ANY, choices=listeLabels)
        self.ctrl_derniere.SetSelection(0)
        
        # Utilisateur
        self.box_utilisateur_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Utilisateur"))
        self.check_utilisateur = wx.CheckBox(self, wx.ID_ANY, _(u"Si l'utilisateur est :"))
        self.radio_utilisateur_1 = wx.RadioButton(self, wx.ID_ANY, _(u"Moi (%s)") % self.GetUtilisateur()[1], style=wx.RB_GROUP)
        self.radio_utilisateur_2 = wx.RadioButton(self, wx.ID_ANY, _(u"Parmi les utilisateurs cochés :"))
        self.ctrl_utilisateurs = CTRL_Utilisateurs(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckJour, self.check_jour)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckHeure, self.check_heure)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPoste, self.check_poste)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDerniere, self.check_derniere)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckUtilisateur, self.check_utilisateur)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPoste, self.radio_poste_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPoste, self.radio_poste_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioUtilisateur, self.radio_utilisateur_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioUtilisateur, self.radio_utilisateur_2)
        
        # Init contrôles
        self.OnCheckJour(None)
        self.OnCheckHeure(None)
        self.OnCheckPoste(None)
        self.OnCheckDerniere(None)
        self.OnCheckUtilisateur(None)


    def __set_properties(self):
        self.check_jour.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer une condition de jour")))
        self.check_scolaire_lundi.SetToolTip(wx.ToolTip(_(u"Lundi")))
        self.check_scolaire_mardi.SetToolTip(wx.ToolTip(_(u"Mardi")))
        self.check_scolaire_mercredi.SetToolTip(wx.ToolTip(_(u"Mercredi")))
        self.check_scolaire_jeudi.SetToolTip(wx.ToolTip(_(u"Jeudi")))
        self.check_scolaire_vendredi.SetToolTip(wx.ToolTip(_(u"Vendredi")))
        self.check_scolaire_samedi.SetToolTip(wx.ToolTip(_(u"Samedi")))
        self.check_scolaire_dimanche.SetToolTip(wx.ToolTip(_(u"Dimanche")))
        self.check_vacances_lundi.SetToolTip(wx.ToolTip(_(u"Lundi")))
        self.check_vacances_mardi.SetToolTip(wx.ToolTip(_(u"Mardi")))
        self.check_vacances_mercredi.SetToolTip(wx.ToolTip(_(u"Mercredi")))
        self.check_vacances_jeudi.SetToolTip(wx.ToolTip(_(u"Jeudi")))
        self.check_vacances_vendredi.SetToolTip(wx.ToolTip(_(u"Vendredi")))
        self.check_vacances_samedi.SetToolTip(wx.ToolTip(_(u"Samedi")))
        self.check_vacances_dimanche.SetToolTip(wx.ToolTip(_(u"Dimanche")))
        self.check_heure.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer une condition d'heure")))
        self.ctrl_heure_debut.SetToolTip(wx.ToolTip(_(u"Saisissez une heure minimale")))
        self.ctrl_heure_fin.SetToolTip(wx.ToolTip(_(u"Saisissez une heure maximale")))
        self.check_poste.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer une condition de poste")))
        self.radio_poste_1.SetToolTip(wx.ToolTip(_(u"Uniquement pour ce poste")))
        self.radio_poste_2.SetToolTip(wx.ToolTip(_(u"Uniquement parmi une liste de postes cochés")))
        self.ctrl_postes.SetToolTip(wx.ToolTip(_(u"Saisissez les noms de poste du réseau séparés par des points-virgules (;)")))
        self.check_derniere.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer une condition de délai")))
        self.ctrl_derniere.SetToolTip(wx.ToolTip(_(u"Sélectionnez un délai")))
        self.check_utilisateur.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer une condition d'utilisateur")))
        self.radio_utilisateur_1.SetToolTip(wx.ToolTip(_(u"Uniquement cet utilisateur")))
        self.radio_utilisateur_2.SetToolTip(wx.ToolTip(_(u"Uniquement parmi une liste d'utilisateurs cochés")))
        self.ctrl_utilisateurs.SetToolTip(wx.ToolTip(_(u"Cochez les utilisateurs")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(1, 2, 10, 10)
        
        grid_sizer_droite = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_gauche = wx.FlexGridSizer(3, 1, 10, 10)
        
        # Jour
        box_jour = wx.StaticBoxSizer(self.box_jour_staticbox, wx.VERTICAL)
        grid_sizer_jour = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_liste_jours = wx.FlexGridSizer(2, 9, 5, 0)
        grid_sizer_jour.Add(self.check_jour, 0, 0, 0)
        grid_sizer_liste_jours.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_liste_jours.Add(self.label_jours_scolaire, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_lundi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_mardi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_mercredi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_jeudi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_vendredi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_samedi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_scolaire_dimanche, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_liste_jours.Add(self.label_jours_vacances, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_lundi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_mardi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_mercredi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_jeudi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_vendredi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_samedi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_liste_jours.Add(self.check_vacances_dimanche, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jour.Add(grid_sizer_liste_jours, 1, wx.EXPAND, 0)
        grid_sizer_jour.AddGrowableCol(0)
        box_jour.Add(grid_sizer_jour, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_gauche.Add(box_jour, 1, wx.EXPAND, 0)
        
        # heure
        box_heure = wx.StaticBoxSizer(self.box_heure_staticbox, wx.VERTICAL)
        grid_sizer_heure = wx.FlexGridSizer(1, 5, 2, 2)
        grid_sizer_heure.Add(self.check_heure, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure.Add(self.ctrl_heure_debut, 0, 0, 0)
        grid_sizer_heure.Add(self.label_heure_et, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        grid_sizer_heure.Add(self.ctrl_heure_fin, 0, 0, 0)
        box_heure.Add(grid_sizer_heure, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_gauche.Add(box_heure, 1, wx.EXPAND, 0)
        
        # Poste
        box_poste = wx.StaticBoxSizer(self.box_poste_staticbox, wx.VERTICAL)
        grid_sizer_poste = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_poste.Add(self.check_poste, 0, 0, 0)
        grid_sizer_poste_1 = wx.FlexGridSizer(1, 2, 2, 2)
        grid_sizer_poste_1.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_poste_1.Add(self.radio_poste_1, 0, 0, 0)
        grid_sizer_poste.Add(grid_sizer_poste_1, 1, wx.EXPAND, 0)
        grid_sizer_poste_2 = wx.FlexGridSizer(2, 3, 2, 2)
        grid_sizer_poste_2.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_poste_2.Add(self.radio_poste_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_poste_2.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_poste_2.Add(self.ctrl_postes, 0, wx.LEFT | wx.EXPAND, 0)
        grid_sizer_poste_2.AddGrowableRow(1)
        grid_sizer_poste_2.AddGrowableCol(2)
        grid_sizer_poste.Add(grid_sizer_poste_2, 1, wx.EXPAND, 0)
        grid_sizer_poste.AddGrowableRow(2)
        grid_sizer_poste.AddGrowableCol(0)
        box_poste.Add(grid_sizer_poste, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_gauche.Add(box_poste, 1, wx.EXPAND, 0)
        
        # Dernière sauvegarde
        box_derniere = wx.StaticBoxSizer(self.box_derniere_staticbox, wx.VERTICAL)
        grid_sizer_derniere = wx.FlexGridSizer(1, 2, 2, 2)
        grid_sizer_derniere.Add(self.check_derniere, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_derniere.Add(self.ctrl_derniere, 0, wx.EXPAND, 0)
        grid_sizer_derniere.AddGrowableCol(1)
        box_derniere.Add(grid_sizer_derniere, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_droite.Add(box_derniere, 1, wx.EXPAND, 0)        
        
        # Utilisateur
        box_utilisateur = wx.StaticBoxSizer(self.box_utilisateur_staticbox, wx.VERTICAL)
        grid_sizer_utilisateur = wx.FlexGridSizer(3, 1, 5, 5)
        
        grid_sizer_utilisateur.Add(self.check_utilisateur, 0, 0, 0)
        
        grid_sizer_utilisateur_1 = wx.FlexGridSizer(1, 2, 2, 2)
        grid_sizer_utilisateur_1.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_utilisateur_1.Add(self.radio_utilisateur_1, 0, 0, 0)
        grid_sizer_utilisateur.Add(grid_sizer_utilisateur_1, 1, wx.EXPAND, 0)
        grid_sizer_utilisateur_2 = wx.FlexGridSizer(2, 2, 2, 2)
        grid_sizer_utilisateur_2.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_utilisateur_2.Add(self.radio_utilisateur_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_utilisateur_2.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_utilisateur_2.Add(self.ctrl_utilisateurs, 0, wx.LEFT | wx.EXPAND, 15)
        grid_sizer_utilisateur_2.AddGrowableRow(1)
        grid_sizer_utilisateur_2.AddGrowableCol(1)
        grid_sizer_utilisateur.Add(grid_sizer_utilisateur_2, 1, wx.EXPAND, 0)
        grid_sizer_utilisateur.AddGrowableRow(2)
        grid_sizer_utilisateur.AddGrowableCol(0)
        box_utilisateur.Add(grid_sizer_utilisateur, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_droite.Add(box_utilisateur, 1, wx.EXPAND, 0)
        
        # Finalisation
        grid_sizer_gauche.AddGrowableRow(2)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_droite.AddGrowableRow(1)
        grid_sizer_droite.AddGrowableCol(0)
        
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT, 10)
        grid_sizer_base.Add(grid_sizer_droite, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnCheckJour(self, event):  
        for periode in ("scolaire", "vacances") :
            for jour in self.liste_jours :
                getattr(self, "check_%s_%s" % (periode, jour)).Enable(self.check_jour.GetValue())

    def OnCheckHeure(self, event):  
        self.ctrl_heure_debut.Enable(self.check_heure.GetValue())
        self.ctrl_heure_fin.Enable(self.check_heure.GetValue())

    def OnCheckPoste(self, event):  
        self.ctrl_postes.Enable(self.check_poste.GetValue())
        self.radio_poste_1.Enable(self.check_poste.GetValue())
        self.radio_poste_2.Enable(self.check_poste.GetValue())
        self.OnRadioPoste(None)

    def OnCheckDerniere(self, event):  
        self.ctrl_derniere.Enable(self.check_derniere.GetValue())

    def OnCheckUtilisateur(self, event):  
        self.ctrl_utilisateurs.Enable(self.check_utilisateur.GetValue())
        self.radio_utilisateur_1.Enable(self.check_utilisateur.GetValue())
        self.radio_utilisateur_2.Enable(self.check_utilisateur.GetValue())
        self.OnRadioUtilisateur(None)

    def GetJours(self, periode="scolaire"):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            etat = getattr(self, "check_%s_%s" % (periode, jour)).GetValue()
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp

    def SetJours(self, periode="scolaire", texteJours=""):
        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            if jour != "" :
                listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = True
            else :
                etat = False
            getattr(self, "check_%s_%s" % (periode, jour)).SetValue(etat)
            index += 1

    def OnRadioPoste(self, event):
        if self.check_poste.GetValue() == True :
            self.ctrl_postes.Enable(self.radio_poste_2.GetValue())
        
    def OnRadioUtilisateur(self, event):
        if self.check_utilisateur.GetValue() == True :
            self.ctrl_utilisateurs.Enable(self.radio_utilisateur_2.GetValue())

    def GetUtilisateur(self):
        IDutilisateur = UTILS_Identification.GetIDutilisateur()
        if IDutilisateur != None :
            dictUtilisateur = UTILS_Identification.GetAutreDictUtilisateur(IDutilisateur)
            if dictUtilisateur != None :
                nomUtilisateur = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
            else:
                nomUtilisateur = u"n°%d" % self.IDutilisateur
        else:
            nomUtilisateur = _(u"Utilisateur inconnu")
        return IDutilisateur, nomUtilisateur

    def GetDonnees(self):
        dictDonnees = {}
        
        # Jours
        jours_scolaires, jours_vacances = None, None
        if self.check_jour.GetValue() == True :
            jours_scolaires = ConvertListeEnChaine(self.GetJours("scolaire"))
            jours_vacances = ConvertListeEnChaine(self.GetJours("vacances"))
            if jours_scolaires == None and jours_vacances == None :
                dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'jour' mais vous n'avez coché aucun jour !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        
        # Heure
        heures = None
        if self.check_heure.GetValue() == True :
            heure_min = self.ctrl_heure_debut.GetHeure()
            heure_max = self.ctrl_heure_fin.GetHeure()
            if heure_min == None or heure_max == None :
                dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'heure' mais les heures saisies ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            heures = u"%s;%s" % (heure_min, heure_max)
        
        # Poste
        poste = None
        if self.check_poste.GetValue() == True :
            if self.radio_poste_1.GetValue() == True :
                poste = socket.gethostname()
            if self.radio_poste_2.GetValue() == True :
                poste = self.ctrl_postes.GetValue() 
                if poste == "" :
                    dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'poste' mais sans saisir de noms de postes !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        
        # Dernière sauvegarde
        derniere = None
        if self.check_derniere.GetValue() == True :
            derniere = str(self.listeDelais[self.ctrl_derniere.GetSelection()][0])
        
        # Utilisateur
        utilisateur = None
        if self.check_utilisateur.GetValue() == True :
            if self.radio_utilisateur_1.GetValue() == True :
                utilisateur = self.GetUtilisateur()[0]
            if self.radio_utilisateur_2.GetValue() == True :
                listeUtilisateurs = self.ctrl_utilisateurs.GetIDcoches()
                if len(listeUtilisateurs) == 0 :
                    dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'utilisateur' mais sans cocher d'utilisateurs dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                utilisateur = ConvertListeEnChaine(listeUtilisateurs)
        
        # Création du dictDonnées
        dictDonnees["condition_jours_scolaires"] = jours_scolaires
        dictDonnees["condition_jours_vacances"] = jours_vacances
        dictDonnees["condition_heure"] = heures
        dictDonnees["condition_poste"] = poste
        dictDonnees["condition_derniere"] = derniere
        dictDonnees["condition_utilisateur"] = utilisateur
        return dictDonnees
    
    def SetDonnees(self, dictDonnees={}):
        """ Importation des données dans les contrôles """
        # Jours
        jours_scolaires = dictDonnees["condition_jours_scolaires"]
        if jours_scolaires != None :
            self.SetJours("scolaire", jours_scolaires)
        
        jours_vacances = dictDonnees["condition_jours_vacances"]
        if jours_vacances != None :
            self.SetJours("vacances", jours_vacances)
        
        if jours_scolaires != None or jours_vacances != None :
            self.check_jour.SetValue(True)
            
        # Heures
        heures = dictDonnees["condition_heure"]
        if heures != None :
            heure_min, heure_max = heures.split(";")
            self.ctrl_heure_debut.SetHeure(heure_min) 
            self.ctrl_heure_fin.SetHeure(heure_max) 
            self.check_heure.SetValue(True)
        
        # Poste
        poste = dictDonnees["condition_poste"]
        if poste != None :
            if poste == socket.gethostname() :
                self.radio_poste_1.SetValue(True) 
            else :
                self.radio_poste_2.SetValue(True)
                self.ctrl_postes.SetValue(poste)
                self.OnRadioPoste(None)
            self.check_poste.SetValue(True)
        
        # Dernière sauvegarde
        derniere = dictDonnees["condition_derniere"]
        if derniere != None :
            self.ctrl_derniere.SetSelection(int(derniere)-1)
            self.check_derniere.SetValue(True)
        
        # Utilisateur
        utilisateur = dictDonnees["condition_utilisateur"]
        if utilisateur != None :
            if utilisateur == six.text_type(self.GetUtilisateur()[1]) :
                self.radio_utilisateur_1.SetValue(True) 
            else :
                self.radio_utilisateur_2.SetValue(True)
                self.ctrl_utilisateurs.SetDonneesStr(utilisateur)
                self.OnRadioUtilisateur(None)
            self.check_utilisateur.SetValue(True)
        
        # Actualisation de l'affichage
        self.OnCheckJour(None)
        self.OnCheckHeure(None)
        self.OnCheckPoste(None)
        self.OnCheckDerniere(None)
        self.OnCheckUtilisateur(None)



# --------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Options(wx.Panel) :
    def __init__(self, parent) :
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        # Interface
        self.box_interface_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Interface utilisateur"))
        self.check_demander = wx.CheckBox(self, wx.ID_ANY, _(u"Demander à l'utilisateur la confirmation du lancement de la sauvegarde"))
        self.check_demander.SetValue(True)
        self.check_confirmation = wx.CheckBox(self, wx.ID_ANY, _(u"Afficher un message de confirmation si sauvegarde réussie"))
        self.check_interface = wx.CheckBox(self, wx.ID_ANY, _(u"Afficher l'interface du module de sauvegarde"))

        # Suppression
        self.box_suppression_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Sauvegardes obsolètes"))
        self.check_suppression = wx.CheckBox(self, wx.ID_ANY, _(u"Supprimer les sauvegardes présentes dans le répertoire datant de plus de"))
        self.listeAnciennete = [(2, _(u"2 jours")), (5, _(u"5 jours")), (7, _(u"1 semaine")), (14, _(u"2 semaines")), (21, _(u"3 semaines")), (30, _(u"1 mois")), (60, _(u"2 mois")), (90, _(u"3 mois")), (180, _(u"6 mois")), (365, _(u"1 année")), (730, _(u"2 années")), (1095, _(u"3 années")),]
        listeLabels = []
        for nbre, label in self.listeAnciennete :
            listeLabels.append(label)
        self.ctrl_suppression = wx.Choice(self, wx.ID_ANY, choices=listeLabels)
        self.ctrl_suppression.SetSelection(0) 
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckSuppression, self.check_suppression)
        
        self.OnCheckSuppression(None) 
        
    def __set_properties(self):
        self.check_demander.SetToolTip(wx.ToolTip(_(u"Noethys affichera une boîte de dialogue proposant la sauvegarde. A défaut, la sauvegarde sera réalisée automatiquement sans demander l'avis de l'utilisateur.")))
        self.check_interface.SetToolTip(wx.ToolTip(_(u"Pour afficher l'interface utilisateur avant la sauvegarde afin de permettre à l'utilisateur de modifier certains paramètres.")))
        self.check_confirmation.SetToolTip(wx.ToolTip(_(u"Pour afficher un message de confirmation si la sauvegarde a été réussie.")))
        self.check_suppression.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer la suppression automatique des sauvegardes les plus anciennes")))
        self.ctrl_suppression.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'ancienneté des sauvegardes à supprimer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        box_interface = wx.StaticBoxSizer(self.box_interface_staticbox, wx.VERTICAL)
        grid_sizer_interface = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_interface.Add(self.check_demander, 0, 0, 0)
        grid_sizer_interface.Add(self.check_confirmation, 0, 0, 0)
        grid_sizer_interface.Add(self.check_interface, 0, 0, 0)
        box_interface.Add(grid_sizer_interface, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_interface, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        box_suppression = wx.StaticBoxSizer(self.box_suppression_staticbox, wx.VERTICAL)
        grid_sizer_suppression = wx.FlexGridSizer(1, 3, 2, 2)
        grid_sizer_suppression.Add(self.check_suppression, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_suppression.Add(self.ctrl_suppression, 0, 0, 0)
        box_suppression.Add(grid_sizer_suppression, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_suppression, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def OnCheckSuppression(self, event):  
        self.ctrl_suppression.Enable(self.check_suppression.GetValue())
        
    def GetDonnees(self):
        option_demander = str(int(self.check_demander.GetValue()))
        option_afficher_interface = str(int(self.check_interface.GetValue()))
        option_confirmation = str(int(self.check_confirmation.GetValue()))
        if self.check_suppression.GetValue() == True :
            option_suppression = self.listeAnciennete[self.ctrl_suppression.GetSelection()][0]
        else :
            option_suppression = None
            
        dictDonnees = {
            "option_demander" : option_demander,
            "option_afficher_interface" : option_afficher_interface,
            "option_confirmation" : option_confirmation,
            "option_suppression" : option_suppression,
            }
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        """ Importation des données dans les contrôles """
        if dictDonnees["option_demander"] == "1" : 
            self.check_demander.SetValue(True)
        else :
            self.check_demander.SetValue(False)
        
        if dictDonnees["option_afficher_interface"] == "1" : 
            self.check_interface.SetValue(True)

        if dictDonnees["option_confirmation"] == "1" : 
            self.check_confirmation.SetValue(True)

        option_suppression = dictDonnees["option_suppression"]
        if option_suppression != None :
            index = 0
            for valeur, label in self.listeAnciennete :
                if str(valeur) == option_suppression :
                    self.ctrl_suppression.SetSelection(index)
                    self.check_suppression.SetValue(True)
                index += 1
        
        self.OnCheckSuppression(None) 
        
# --------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, -1, style= wx.BK_DEFAULT) 
        self.dictPages = {}
        
        listePages = [
            (_(u"sauvegarde"), _(u"Sauvegarde"), DLG_Sauvegarde.CTRL_Parametres(self, labelControleNom=_(u"Préfixe")), "Sauvegarder_param.png"),
            (_(u"conditions"), _(u"Conditions"), CTRL_Conditions(self), "Cocher.png"),
            (_(u"options"), _(u"Options"), CTRL_Options(self), "Options.png"),
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        dictImages = {}
        for codePage, labelPage, ctrlPage, imgPage in listePages :
            dictImages[index] = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s' % imgPage), wx.BITMAP_TYPE_PNG))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in listePages :
            self.AddPage(ctrlPage, labelPage)
            self.SetPageImage(index, dictImages[index])
            self.dictPages[codePage] = {'ctrl' : ctrlPage, 'index' : index}
            index += 1

##        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        page.Layout()
        event.Skip()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDsauvegarde=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDsauvegarde = IDsauvegarde

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralites"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom de la procédure :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        if self.IDsauvegarde != None :
            self.Importation() 
            self.SetTitle(_(u"Modification d'une procédure de sauvegarde automatique"))
        else:
            self.ctrl_parametres.GetPageAvecCode("sauvegarde").ctrl_nom.SetValue("Noethys")

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une procédure de sauvegarde automatique"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour cette procédure de sauvegarde (Ex : 'Ma sauvegarde 1')")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Vous pouvez saisir des observations [Optionnel]")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
                
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(2, 2, 10, 10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Paramèters
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        self.SetMinSize(self.GetSize())

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Sauvegardesautomatiques")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def Importation(self):
        """ Importation des données """
        listeChamps = [
            "nom", "observations", "date_derniere", 
            "sauvegarde_nom", "sauvegarde_motdepasse", "sauvegarde_repertoire", "sauvegarde_emails", "sauvegarde_fichiers_locaux", "sauvegarde_fichiers_reseau",
            "condition_jours_scolaires", "condition_jours_vacances", "condition_heure", "condition_poste", "condition_derniere", "condition_utilisateur",
            "option_afficher_interface", "option_demander", "option_confirmation", "option_suppression", 
            ]
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM sauvegardes_auto
        WHERE IDsauvegarde=%d;
        """ % (",".join(listeChamps), self.IDsauvegarde)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        dictDonnees = {}
        index = 0
        for valeur in listeDonnees[0] :
            dictDonnees[listeChamps[index]] = valeur
            index += 1
            
        self.ctrl_nom.SetValue(dictDonnees["nom"])
        self.ctrl_observations.SetValue(dictDonnees["observations"])
        for code in ("sauvegarde", "conditions", "options") :
            self.ctrl_parametres.GetPageAvecCode(code).SetDonnees(dictDonnees)
            
    
    def Sauvegarde(self):
        """ Sauvegarde des données """
        # Récupération et validation des données
        dictDonnees = {}
        
        nom = self.ctrl_nom.GetValue() 
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour cette procédure de sauvegarde !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
        dictDonnees["nom"] = nom
        
        observations = self.ctrl_observations.GetValue() 
        dictDonnees["observations"] = observations
        
        for code in ("sauvegarde", "conditions", "options") :
            donnees = self.ctrl_parametres.GetPageAvecCode(code).GetDonnees()
            if donnees == False :
                self.ctrl_parametres.AffichePage(code)
                self.ctrl_parametres.GetPageAvecCode(code).SetFocus()
                return False
            dictDonnees.update(donnees)

        # Sauvegarde
        listeDonnees = []
        for key, valeur in dictDonnees.items() :
            listeDonnees.append((key, valeur))
        
        DB = GestionDB.DB()
        if self.IDsauvegarde == None :
            self.IDsauvegarde = DB.ReqInsert("sauvegardes_auto", listeDonnees)
        else:
            DB.ReqMAJ("sauvegardes_auto", listeDonnees, "IDsauvegarde", self.IDsauvegarde)
        DB.Close()
        
        return True
    
    def GetIDsauvegarde(self):
        return self.IDsauvegarde       
        
    def OnBoutonOk(self, event): 
        if self.Sauvegarde() == False :
            return
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDsauvegarde=3)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
