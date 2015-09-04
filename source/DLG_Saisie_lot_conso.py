#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Saisie_date
import CTRL_Saisie_heure
import CTRL_Bandeau
import UTILS_Parametres
import datetime
import calendar
import GestionDB

import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED




class CTRL_Individus(wx.CheckListBox):
    def __init__(self, parent, listeIndividus=[]):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.listeIndividus = listeIndividus
        self.data = []
        self.MAJ() 

    def MAJ(self):
        # Importation
        if len(self.listeIndividus) == 0 : condition="()"
        elif len(self.listeIndividus) == 1 : condition = "(%d)" % self.listeIndividus[0]
        else : condition = str(tuple(self.listeIndividus))
        
        DB = GestionDB.DB()
        
        # Get individus
        req = """SELECT IDindividu, nom, prenom
        FROM individus
        WHERE IDindividu IN %s
        ORDER BY nom, prenom;""" % condition
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        
        # Get Inscriptions
        req = """SELECT IDinscription, IDactivite, IDindividu
        FROM inscriptions
        WHERE IDindividu IN %s;""" % condition
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        dictInscriptions = {}
        for IDinscription, IDactivite, IDindividu in listeInscriptions :
            if dictInscriptions.has_key(IDindividu) == False :
                dictInscriptions[IDindividu] = []
            if IDindividu not in dictInscriptions[IDindividu] :
                dictInscriptions[IDindividu].append(IDactivite)
        
        DB.Close()
        listeValeurs = []
        for IDindividu, nom, prenom in listeIndividus :
            if prenom == None : prenom = u""
            if dictInscriptions.has_key(IDindividu) :
                inscriptions = dictInscriptions[IDindividu]
            else :
                inscriptions = []
            listeValeurs.append({"IDindividu":IDindividu, "label": u"%s %s" % (nom, prenom), "inscriptions":inscriptions, "selection":False})
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for dictIndividu in listeValeurs:
            self.data.append(dictIndividu)
            self.Append(dictIndividu["label"])
            if dictIndividu["selection"] == True :
                self.Check(index)
            index += 1
    
    def GetCoches(self):
        listeCoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeCoches.append(self.data[index])
        return listeCoches

    def SetCoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
# -----------------------------------------------------------------------------------------------------------------

class CTRL_Jours(wx.Panel):
    def __init__(self, parent, periode="scolaire"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.periode = periode
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        for jour in self.liste_jours :
            exec("self.check_%s = wx.CheckBox(self, -1,u'%s')" % (jour, jour[0].upper()) )
            exec("self.check_%s.SetToolTipString(u'%s')" % (jour, jour.capitalize()) )
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        for jour in self.liste_jours :
            exec("grid_sizer_base.Add(self.check_%s, 0, 0, 0)" % jour)
                        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def GetJours(self):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            exec("etat = self.check_%s.GetValue()" % jour)
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
    
    def GetJoursStr(self):
        listeTemp = []
        for num in self.GetJours()  :
            listeTemp.append(str(num))
        return ";".join(listeTemp)
        
    def SetJours(self, texteJours=""):
        if texteJours == None or len(texteJours) == 0 :
            return

        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = "True"
            else :
                etat = "False"
            exec("self.check_%s.SetValue(%s)" % (jour, etat))
            index += 1
            
        
# ---------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Semaines(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeEtats = [
            (1, _(u"Toutes les semaines")),
            (2, _(u"Une semaine sur deux")),
            (3, _(u"Une semaine sur trois")),
            (4, _(u"Une semaine sur quatre")),
            ]
        self.MAJ() 
    
    def MAJ(self):
        listeLabels = []
        for code, label in self.listeEtats :
            listeLabels.append(label)
        self.SetItems(listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]
    
    def GetLabel(self):
        return self.GetStringSelection()

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.dictDonnees = {}
        self.MAJ() 
        
        if len(self.dictDonnees) > 0 :
            self.Select(0)
    
    def MAJ(self):
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY date_fin DESC
        ;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()      
        DB.Close() 
        if len(listeActivites) == 0 :
            self.Enable(False)
        listeLabels = []
        index = 0
        for IDactivite, nom in listeActivites :
            self.dictDonnees[index] = IDactivite
            listeLabels.append(nom)
            index += 1
        self.SetItems(listeLabels)

    def SetActivite(self, IDactivite=None):
        for index, IDactiviteTmp in self.dictDonnees.iteritems() :
            if IDactiviteTmp == IDactivite :
                self.SetSelection(index)

    def GetActivite(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
    
    def GetNomActivite(self):
        return self.GetStringSelection()

# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Horaire(wx.Panel):
    def __init__(self, parent, treeListMainWindow=None, item=None, niveauUnite=None, labelUnite="", multihoraires=False, action=None):
        wx.Panel.__init__(self, parent, id=-1, name="horaire", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.treeListMainWindow = treeListMainWindow
        self.item = item
        self.niveauUnite = niveauUnite
        self.labelUnite = labelUnite
        self.multihoraires = multihoraires
        self.action = action
        
        self.SetSize((260, 30))
        self.SetMinSize((220, 30))
        self.SetBackgroundColour((255, 255, 255))
                
        # Contr�les
        self.label_heure_debut = wx.StaticText(self, -1, _(u"Horaire :"))
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.label_heure_fin = wx.StaticText(self, -1, u"�")
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)
        
        if self.multihoraires == True :
            self.bouton_ajouter = wx.Button(self, -1, "+", size=(20, 20))
            self.bouton_retirer = wx.Button(self, -1, "-", size=(20, 20))
            
            self.Bind(wx.EVT_BUTTON, self.AjouterHoraires, self.bouton_ajouter)
            self.Bind(wx.EVT_BUTTON, self.RetirerHoraires, self.bouton_retirer)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_heure_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_heure_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.label_heure_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_heure_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        if self.multihoraires == True :
            grid_sizer_base.Add(self.bouton_ajouter, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_base.Add(self.bouton_retirer, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.grid_sizer_contenu = grid_sizer_base
        
        self.MAJ() 
                
    def MAJ(self):
        self.grid_sizer_contenu.Layout()
        self.Refresh() 
    
    def SetHeureDebut(self, heure=None):
        self.ctrl_heure_debut.SetHeure(heure)
        self.MAJ() 

    def SetHeureFin(self, heure=None):
        self.ctrl_heure_fin.SetHeure(heure)
        self.MAJ() 
    
    def GetHeureDebut(self):
        return self.ctrl_heure_debut.GetHeure()
    
    def GetHeureFin(self):
        return self.ctrl_heure_fin.GetHeure()
    
    def Validation(self):
        if self.action not in ("saisie", "modification") :
            return True
        heure_debut = self.GetHeureDebut() 
        heure_fin = self.GetHeureFin() 
        if heure_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une heure de d�but pour l'unit� '%s' !") % self.labelUnite, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_debut.SetFocus() 
            return False
        if heure_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une heure de fin pour l'unit� '%s' !") % self.labelUnite, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_fin.SetFocus() 
            return False
        return True
    
    def GetDonnees(self):
        heure_debut = self.GetHeureDebut() 
        heure_fin = self.GetHeureFin() 
        return {"heure_debut":heure_debut, "heure_fin":heure_fin}
    
    def AjouterHoraires(self, event=None):
        self.parent.AjouterHoraires(niveauUnite=self.niveauUnite)
        
    def RetirerHoraires(self, event=None):
        self.parent.RetirerHoraires(self.niveauUnite, self, self.item)
        
        
# -------------------------------------------------------------------------------------------------------------------

class CTRL_Quantite(wx.Panel):
    def __init__(self, parent, item=None, labelUnite=""):
        wx.Panel.__init__(self, parent, id=-1, name="quantite", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.item = item
        self.labelUnite = labelUnite
        
        self.SetSize((220, 30))
        self.SetMinSize((220, 30))
        self.SetBackgroundColour((255, 255, 255))
                
        # Contr�les
        self.label_quantite = wx.StaticText(self, -1, _(u"Quantit� :"))
        self.ctrl_quantite = wx.SpinCtrl(self, -1, "1", min=1, max=500, size=(70, -1))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_quantite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_quantite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.grid_sizer_contenu = grid_sizer_base
        
        self.MAJ() 
                
    def MAJ(self):
        self.grid_sizer_contenu.Layout()
        self.Refresh() 
    
    def SetQuantite(self, quantite=None):
        self.ctrl_quantite.SetValeur(quantite)
        self.MAJ() 
    
    def GetQuantite(self):
        return self.ctrl_quantite.GetValue()

    def Validation(self):
        return True

    def GetDonnees(self):
        quantite = self.GetQuantite() 
        return {"quantite":quantite}

# -------------------------------------------------------------------------------------------------------------------

class CTRL_Unites(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.activation = True
        self.IDactivite = None
        self.data = []
        self.MAJenCours = False
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.EnableSelectionVista(True)
        
        # Cr�ation des colonnes
        self.AddColumn(_(u"Unit�s"))
        self.SetColumnWidth(0, 300)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
    
    def Activation(self, etat=True):
        """ Active ou d�sactive le contr�le """
        self.activation = etat
        
    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            # Active ou non les branches enfants
            if self.IsItemChecked(item) :
                self.EnableChildren(item, True)
            else:
                self.EnableChildren(item, False)

    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 

    def MAJ(self):
        """ Met � jour (redessine) tout le contr�le """
        self.listeUnites = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation(self):
        listeUnites = []
        if self.IDactivite == None :
            return listeUnites
                
        # R�cup�ration des unit�s
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            listeUnites.append({"IDunite":IDunite, "nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin})
            
        return listeUnites

    def Remplissage(self):
        # Remplissage
        for dictUnite in self.listeUnites :
            label = dictUnite["nom"]
            type = dictUnite["type"]
            listeControles = []
            
            # Niveau Ecole
            niveauUnite = self.AppendItem(self.root, label, ct_type=1)
            self.SetItemBold(niveauUnite, True)                
            
            # Branches Options
            if self.parent.action not in ("suppression", "etat") :
            
                # CTRL Horaire
                if type == "Horaire" :
                    niveauHoraire = self.AppendItem(niveauUnite, u"")
                    ctrl = CTRL_Horaire(self.GetMainWindow(), item=niveauHoraire, labelUnite=label)
                    listeControles.append(ctrl)
                    if self.parent.action == "saisie" :
                        ctrl.SetHeureDebut(dictUnite["heure_debut"])
                        ctrl.SetHeureFin(dictUnite["heure_fin"])
                    self.SetItemWindow(niveauHoraire, ctrl, 0)

                # CTRL Horaire
                if type == "Multihoraires" :
                    niveauHoraire = self.AppendItem(niveauUnite, u"")
                    ctrl = CTRL_Horaire(self, self.GetMainWindow(), item=niveauHoraire, niveauUnite=niveauUnite, labelUnite=label, multihoraires=True, action=self.parent.action)
                    listeControles.append(ctrl)
                    if self.parent.action == "saisie" :
                        ctrl.SetHeureDebut(dictUnite["heure_debut"])
                        ctrl.SetHeureFin(dictUnite["heure_fin"])
                    self.SetItemWindow(niveauHoraire, ctrl, 0)

                # CTRL Quantit�
                if type == "Quantite" :
                    niveauQuantite = self.AppendItem(niveauUnite, u"")
                    ctrl = CTRL_Quantite(self.GetMainWindow(), item=niveauQuantite, labelUnite=label)
                    listeControles.append(ctrl)
                    self.SetItemWindow(niveauQuantite, ctrl, 0)
            
            self.SetPyData(niveauUnite, {"branche" : "unite", "type" : type, "dictUnite" : dictUnite, "ID" : dictUnite["IDunite"], "nom" : label, "controles" : listeControles})

            self.EnableChildren(niveauUnite, False)
        self.ExpandAllChildren(self.root)

        if self.activation == False :
            self.EnableChildren(self.root, False)

        # Pour �viter le bus de positionnement des contr�les
        self.GetMainWindow().CalculatePositions() 
    
    def AjouterHoraires(self, niveauUnite=None):
        niveauHoraire = self.AppendItem(niveauUnite, u"")
        ctrl = CTRL_Horaire(self, self.GetMainWindow(), item=niveauHoraire, niveauUnite=niveauUnite, labelUnite="", multihoraires=True)
        data = self.GetPyData(niveauUnite)
        dictUnite = data["dictUnite"]
        data["controles"].append(ctrl)
        self.SetPyData(niveauUnite, data)
        if self.parent.action == "saisie" :
            ctrl.SetHeureDebut(dictUnite["heure_debut"])
            ctrl.SetHeureFin(dictUnite["heure_fin"])
        self.SetItemWindow(niveauHoraire, ctrl, 0)
    
    def RetirerHoraires(self, niveauUnite=None, ctrl=None, item=None):
        data = self.GetPyData(niveauUnite)
        if len(data["controles"]) == 1 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas retirer le dernier horaire !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        data["controles"].remove(ctrl)
        self.SetPyData(niveauUnite, data)
        self.Delete(item)
    
    def GetCoches(self):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.IsItemChecked(item) and self.IsItemEnabled(item):
                if self.GetPyData(item)["branche"] == "unite" :
                    listeCoches.append(self.GetPyData(item))
        return listeCoches
    
    
# -----------------------------------------------------------------------------------------------------------------------------


class CTRL_Etat(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeEtats = [
            ("reservation", _(u"R�servation - Pointage en attente")),
            ("present", _(u"R�servation - Pr�sent")),
            ("absentj", _(u"R�servation - Absence justifi�e")),
            ("absenti", _(u"R�servation - Absence injustifi�e")),
            ("attente", _(u"Attente")),
            ("refus", _(u"Refus")),
            ]
        self.MAJ() 
    
    def MAJ(self):
        listeLabels = []
        for code, label in self.listeEtats :
            listeLabels.append(label)
        self.SetItems(listeLabels)
        self.Select(0)
        
        if self.parent.action in ("suppression", "modification") :
            self.Enable(False)
        else :
            self.Enable(True)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]
    
    def GetLabel(self):
        return self.GetStringSelection()

# ----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, listeIndividus=[], date_debut=None, date_fin=None, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.action = None
        self.listeIndividus = listeIndividus
        self.resultats = {}

        # Bandeau
        titre = _(u"Traitement par lot")
        intro = _(u"Vous pouvez ici saisir, modifier ou supprimer un lot de consommations selon les crit�res de votre choix. S�lectionnez un type d'action puis renseignez les param�tres demand�s.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_modifier.png")

        # Action
        self.box_action_staticbox = wx.StaticBox(self, -1, _(u"Action"))
        self.radio_saisie = wx.RadioButton(self, -1, _(u"Saisie"), style=wx.RB_GROUP)
        self.radio_modification = wx.RadioButton(self, -1, _(u"Modification"))
        self.radio_suppression = wx.RadioButton(self, -1, _(u"Suppression"))
        self.radio_etat = wx.RadioButton(self, -1, _(u"Changement d'�tat"))

        # Individus
        self.box_individus_staticbox = wx.StaticBox(self, -1, _(u"Individus"))
        self.ctrl_individus = CTRL_Individus(self, listeIndividus)
        
        # Periode
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"P�riode"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Jours
        self.box_jours_staticbox = wx.StaticBox(self, -1, _(u"Jours"))
        self.label_scolaires = wx.StaticText(self, -1, _(u"Scolaires :"))
        self.ctrl_scolaires = CTRL_Jours(self, "scolaires")
        self.label_vacances = wx.StaticText(self, -1, _(u"Vacances :"))
        self.ctrl_vacances = CTRL_Jours(self, "vacances")
        self.label_semaines = wx.StaticText(self, -1, _(u"Semaines :"))
        self.ctrl_semaines = CTRL_Semaines(self)
        self.label_feries = wx.StaticText(self, -1, _(u"F�ri�s :"))
        self.ctrl_feries = wx.CheckBox(self, -1, _(u"Inclure les jours f�ri�s"))

        # Unites
        self.box_unites_staticbox = wx.StaticBox(self, -1, _(u"Unit�s"))
        self.label_activite = wx.StaticText(self, -1, _(u"Activit� :"))
        self.ctrl_activite = CTRL_Activite(self)
        self.label_unites = wx.StaticText(self, -1, _(u"Unit�s :"))
        self.ctrl_unites = CTRL_Unites(self)
        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"))
        self.ctrl_etat = CTRL_Etat(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_saisie)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_modification)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_suppression)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_etat)
        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init
        self.listeVacances = self.GetListeVacances()
        self.listeFeries = self.GetListeFeries() 
        
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        self.ctrl_scolaires.SetJours(UTILS_Parametres.Parametres(mode="get", categorie="dlg_saisie_lot_conso", nom="jours_scolaires", valeur="0;1;2;3;4"))
        self.ctrl_vacances.SetJours(UTILS_Parametres.Parametres(mode="get", categorie="dlg_saisie_lot_conso", nom="jours_vacances", valeur="0;1;2;3;4"))
        IDactivite = UTILS_Parametres.Parametres(mode="get", categorie="dlg_saisie_lot_conso", nom="activite", valeur=None)
        if IDactivite != None :
            try :
                self.ctrl_activite.SetActivite(int(IDactivite))
            except :
                pass
        self.OnRadioAction(None)
        self.OnChoixActivite(None)

    def __set_properties(self):
        self.radio_saisie.SetToolTipString(_(u"Cochez ici pour saisir un lot de consommations"))
        self.radio_modification.SetToolTipString(_(u"Cochez ici pour modifier un lot de consommations"))
        self.radio_suppression.SetToolTipString(_(u"Cochez ici pour supprimer un lot de consommations"))
        self.radio_etat.SetToolTipString(_(u"Cochez ici pour modifier l'�tat d'un lot de consommations"))
        self.ctrl_individus.SetToolTipString(_(u"S�lectionnez les individus vis�s"))
        self.ctrl_date_debut.SetToolTipString(_(u"S�lectionnez une date de d�but"))
        self.ctrl_date_fin.SetToolTipString(_(u"S�lectionnez une date de fin"))
        self.ctrl_semaines.SetToolTipString(_(u"S�lectionnez une fr�quence"))
        self.ctrl_feries.SetToolTipString(_(u"Cochez cette case pour inclure les jours f�ri�s dans le processus"))
        self.ctrl_activite.SetToolTipString(_(u"S�lectionnez une activit�"))
        self.ctrl_etat.SetToolTipString(_(u"S�lectionnez une �tat pour les consommations"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((800, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Action
        box_action = wx.StaticBoxSizer(self.box_action_staticbox, wx.VERTICAL)
        grid_sizer_action = wx.FlexGridSizer(rows=1, cols=4, vgap=20, hgap=20)
        grid_sizer_action.Add(self.radio_saisie, 0, 0, 0)
        grid_sizer_action.Add(self.radio_modification, 0, 0, 0)
        grid_sizer_action.Add(self.radio_suppression, 0, 0, 0)
        grid_sizer_action.Add(self.radio_etat, 0, 0, 0)
        box_action.Add(grid_sizer_action, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_action, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_colonnes = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_droite = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Individus
        box_individus = wx.StaticBoxSizer(self.box_individus_staticbox, wx.VERTICAL)
        box_individus.Add(self.ctrl_individus, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_individus, 1, wx.EXPAND, 0)

        # P�riode
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_periode, 1, wx.EXPAND, 0)
        
        # Jours
        box_jours = wx.StaticBoxSizer(self.box_jours_staticbox, wx.VERTICAL)
        grid_sizer_jours = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_jours.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_scolaires, 0, 0, 0)
        grid_sizer_jours.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_vacances, 0, 0, 0)
        grid_sizer_jours.Add(self.label_semaines, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_semaines, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_feries, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_feries, 0, 0, 0)
        box_jours.Add(grid_sizer_jours, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_jours, 1, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_colonnes.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Unit�s
        box_unites = wx.StaticBoxSizer(self.box_unites_staticbox, wx.VERTICAL)
        grid_sizer_unites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_unites.Add(self.label_activite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unites.Add(self.ctrl_activite, 0, wx.EXPAND, 0)
        grid_sizer_unites.Add(self.label_unites, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_unites.Add(self.ctrl_unites, 1, wx.EXPAND, 0)
        grid_sizer_unites.Add(self.label_etat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unites.Add(self.ctrl_etat, 0, wx.EXPAND, 0)
        grid_sizer_unites.AddGrowableRow(1)
        grid_sizer_unites.AddGrowableCol(1)
        box_unites.Add(grid_sizer_unites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droite.Add(box_unites, 1, wx.EXPAND, 0)
        
        grid_sizer_droite.AddGrowableRow(0)
        grid_sizer_droite.AddGrowableCol(0)
        grid_sizer_colonnes.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        grid_sizer_colonnes.AddGrowableRow(0)
        grid_sizer_colonnes.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_colonnes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioAction(self, event): 
        if self.radio_saisie.GetValue() == True : self.action = "saisie"
        if self.radio_modification.GetValue() == True : self.action = "modification"
        if self.radio_suppression.GetValue() == True : self.action = "suppression"
        if self.radio_etat.GetValue() == True : self.action = "etat"
        
        self.ctrl_unites.MAJ() 
        self.ctrl_etat.MAJ() 
        
    def OnChoixActivite(self, event): 
        self.ctrl_unites.SetActivite(self.ctrl_activite.GetActivite())

    def GetPeriode(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        return date_debut, date_fin

    def GetJours(self):
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        return jours_scolaires, jours_vacances

    def GetFeries(self):
        return self.ctrl_feries.GetValue() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Traitementparlot")

    def OnBoutonOk(self, event): 
        # Individus
        listeIndividus = self.ctrl_individus.GetCoches() 
        if len(listeIndividus) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner au moins un individu !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
                
        # P�riode
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de d�but de p�riode !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin de p�riode !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de d�but ne peut pas �tre sup�rieure � la date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        # Jours
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        if len(jours_scolaires) == 0 and len(jours_vacances) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un jour scolaire ou de vacances !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Semaines
        semaines = self.ctrl_semaines.GetValeur() 
        
        # F�ri�s
        feries = self.ctrl_feries.GetValue() 

        # Activit�
        IDactivite = self.ctrl_activite.GetActivite()
        nomActivite = self.ctrl_activite.GetNomActivite() 
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner une activit� !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_activite.SetFocus() 
            return
        
        # V�rifie si individus inscrits � l'activit� :
        for dictIndividu in listeIndividus :
            if IDactivite not in dictIndividu["inscriptions"] :
                dlg = wx.MessageDialog(self, _(u"%s n'est pas inscrit � l'activit� '%s' !") % (dictIndividu["label"], nomActivite), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
        # Unit�s
        listeCoches = self.ctrl_unites.GetCoches() 
        if len(listeCoches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner au moins une unit� !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        listeUnites = []
        for dictItem in listeCoches :
            IDunite = dictItem["ID"]
            typeUnite = dictItem["type"]
            nom = dictItem["nom"]
            
            if typeUnite == "Unitaire" or self.action not in ("saisie", "modification") :
                # Si unit� sans options (Standard)
                listeUnites.append({"IDunite":IDunite, "nom":nom, "type":typeUnite, "options":{}})
            else :
                # Si unit� avec Options (Quantit�, Horaire, multihoraires...)
                for ctrl in dictItem["controles"] :
                    
                    # Validation de la saisie
                    if ctrl.Validation() == False :
                        return
                    
                    # R�cup�ration des donn�es
                    dictOptions = {}
                    for key, valeur in ctrl.GetDonnees().iteritems() :
                        dictOptions[key] = valeur

                    listeUnites.append({"IDunite":IDunite, "nom":nom, "type":typeUnite, "options":dictOptions})
                            
        # Etat
        etat = self.ctrl_etat.GetValeur()         
        if self.ctrl_etat.IsEnabled() == False :
            etat = None

        # Recherche des dates valides
        listeDates = []
        date = date_debut
        numSemaine = semaines
        dateTemp = date
        while date < (date_fin + datetime.timedelta(days=1)) :
                        
            # V�rifie p�riode et jour
            valide = False
            if self.EstEnVacances(date) :
                if date.weekday() in jours_vacances :
                    valide = True
            else :
                if date.weekday() in jours_scolaires :
                    valide = True
            
            # V�rifie si f�ri�
            if feries == False and self.EstFerie(date) == True :
                valide = False

            # Calcul le num�ro de semaine
            if len(listeDates) > 0 :
                if date.weekday() < dateTemp.weekday() :
                    numSemaine += 1

            # Fr�quence semaines
            if semaines != 1 :
                if numSemaine % semaines != 0 :
                    valide = False
            
            # Ajout de la date � la liste
            if valide == True :
                listeDates.append(date)
            
            dateTemp = date
            date += datetime.timedelta(days=1)
        
        # M�morisation des donn�es
        self.resultats = {}
        self.resultats["action"] = self.action
        self.resultats["individus"] = listeIndividus
        self.resultats["date_debut"] = date_debut
        self.resultats["date_fin"] = date_fin
        self.resultats["jours_scolaires"] = jours_scolaires
        self.resultats["jours_vacances"] = jours_vacances
        self.resultats["feries"] = feries
        self.resultats["IDactivite"] = IDactivite
        self.resultats["unites"] = listeUnites
        self.resultats["etat"] = etat
        self.resultats["dates"] = listeDates
        
        # M�morisation param�tres
        UTILS_Parametres.Parametres(mode="set", categorie="dlg_saisie_lot_conso", nom="jours_scolaires", valeur=self.ctrl_scolaires.GetJoursStr())
        UTILS_Parametres.Parametres(mode="set", categorie="dlg_saisie_lot_conso", nom="jours_vacances", valeur=self.ctrl_vacances.GetJoursStr())
        UTILS_Parametres.Parametres(mode="set", categorie="dlg_saisie_lot_conso", nom="activite", valeur=self.ctrl_activite.GetActivite())
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)   

    def GetResultats(self):
        return self.resultats

    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def EstFerie(self, dateDD):
        jour = dateDD.day
        mois = dateDD.month
        annee = dateDD.year        
        for type, nom, jourTmp, moisTmp, anneeTmp in self.listeFeries :
            jourTmp = int(jourTmp)
            moisTmp = int(moisTmp)
            anneeTmp = int(anneeTmp)
            if type == "fixe" :
                if jourTmp == jour and moisTmp == mois :
                    return True
            else:
                if jourTmp == jour and moisTmp == mois and anneeTmp == annee :
                    return True
        return False

    def GetListeVacances(self):
        db = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def GetListeFeries(self):
        db = GestionDB.DB()
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries 
        ; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, listeIndividus=[46,], date_debut=datetime.date(2013, 6, 1), date_fin=datetime.date(2013, 6, 2), IDactivite="")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    print dialog_1.GetResultats() 
    app.MainLoop()
