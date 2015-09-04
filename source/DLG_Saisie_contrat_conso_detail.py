#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Saisie_date
import CTRL_Saisie_heure
import UTILS_Parametres
import datetime
import calendar
import GestionDB

import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED



LISTE_SEMAINES = [
    (1, _(u"Toutes les semaines")),
    (2, _(u"Une semaine sur deux")),
    (3, _(u"Une semaine sur trois")),
    (4, _(u"Une semaine sur quatre")),
    ]



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
        
    def SetJours(self, listeJours=[]):
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = "True"
            else :
                etat = "False"
            exec("self.check_%s.SetValue(%s)" % (jour, etat))
            index += 1
        
    def SetJoursStr(self, texteJours=""):
        if texteJours == None or len(texteJours) == 0 :
            return
        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            listeJours.append(int(jour))
        self.SetJours(listeJours)
        
# ---------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Semaines(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeEtats = LISTE_SEMAINES
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
    
    def SetValeur(self, valeur=None):
        index = 0
        for valeurTemp, label in self.listeEtats :
            if valeur == valeurTemp :
                self.Select(index)
            index += 1

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Horaire(wx.Panel):
    def __init__(self, parent, treeListMainWindow=None, item=None, niveauUnite=None, labelUnite="", multihoraires=False):
        wx.Panel.__init__(self, parent, id=-1, name="horaire", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.treeListMainWindow = treeListMainWindow
        self.item = item
        self.niveauUnite = niveauUnite
        self.labelUnite = labelUnite
        self.multihoraires = multihoraires
        
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
        self.ctrl_quantite.SetValue(quantite)
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
    def __init__(self, parent, IDactivite=None): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.activation = True
        self.IDactivite = IDactivite
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
        
        # Importation
        self.listeUnites = self.Importation_unites()
    
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

    def MAJ(self):
        """ Met � jour (redessine) tout le contr�le """
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation_unites(self):
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
            
            # CTRL Horaire
            if type == "Horaire" :
                niveauHoraire = self.AppendItem(niveauUnite, u"")
                ctrl = CTRL_Horaire(self.GetMainWindow(), item=niveauHoraire, labelUnite=label)
                listeControles.append(ctrl)
                ctrl.SetHeureDebut(dictUnite["heure_debut"])
                ctrl.SetHeureFin(dictUnite["heure_fin"])
                self.SetItemWindow(niveauHoraire, ctrl, 0)

            # CTRL Multihoraires
            if type == "Multihoraires" :
                niveauHoraire = self.AppendItem(niveauUnite, u"")
                ctrl = CTRL_Horaire(self, self.GetMainWindow(), item=niveauHoraire, niveauUnite=niveauUnite, labelUnite=label, multihoraires=True)
                listeControles.append(ctrl)
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
    
    def AjouterHoraires(self, niveauUnite=None, heure_debut=None, heure_fin=None):
        niveauHoraire = self.AppendItem(niveauUnite, u"")
        ctrl = CTRL_Horaire(self, self.GetMainWindow(), item=niveauHoraire, niveauUnite=niveauUnite, labelUnite="", multihoraires=True)
        data = self.GetPyData(niveauUnite)
        dictUnite = data["dictUnite"]
        data["controles"].append(ctrl)
        self.SetPyData(niveauUnite, data)
        if heure_debut == None :
            ctrl.SetHeureDebut(dictUnite["heure_debut"])
        else :
            ctrl.SetHeureDebut(heure_debut)
        if heure_fin == None :
            ctrl.SetHeureFin(dictUnite["heure_fin"])
        else :
            ctrl.SetHeureFin(heure_fin)
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
    
    def RechercheItem(self, IDunite):
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.IsItemEnabled(item) and self.GetPyData(item)["branche"] == "unite" :
                if self.GetPyData(item)["ID"] == IDunite :
                    return item
        return None

    def SetDonnees(self, listeUnites=[]):
        for dictUnite in listeUnites :
            IDunite = dictUnite["IDunite"]
            options = dictUnite["options"]
        
            # Coche l'item
            item = self.RechercheItem(IDunite)
            item.Check()
            
            # Options
            itemData = self.GetPyData(item)

            if itemData["type"] == "Quantite" :
                itemData["controles"][0].SetQuantite(options["quantite"])
                self.EnableChildren(item, True)

            if itemData["type"] == "Horaire" :
                itemData["controles"][0].SetHeureDebut(options["heure_debut"])
                itemData["controles"][0].SetHeureFin(options["heure_fin"])
                self.EnableChildren(item, True)

            if itemData["type"] == "Multihoraires" :
                if itemData["controles"][0].GetHeureDebut() == None :
                    itemData["controles"][0].SetHeureDebut(options["heure_debut"])
                    itemData["controles"][0].SetHeureFin(options["heure_fin"])
                else :
                    self.AjouterHoraires(niveauUnite=item, heure_debut=options["heure_debut"], heure_fin=options["heure_fin"])
                self.EnableChildren(item, True)
    

            

# -----------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        
        # Jours
        self.box_jours_staticbox = wx.StaticBox(self, -1, _(u"Conditions"))
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
        self.ctrl_unites = CTRL_Unites(self, IDactivite=IDactivite)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init
        self.ctrl_scolaires.SetJours((0, 1, 2, 3, 4))
        self.ctrl_vacances.SetJours((0, 1, 2, 3, 4))
        self.ctrl_unites.MAJ() 

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un param�tre de planning"))
        self.ctrl_semaines.SetToolTipString(_(u"S�lectionnez une fr�quence"))
        self.ctrl_feries.SetToolTipString(_(u"Cochez cette case pour inclure les jours f�ri�s"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((400, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
                
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
        grid_sizer_base.Add(box_jours, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Unit�s
        box_unites = wx.StaticBoxSizer(self.box_unites_staticbox, wx.VERTICAL)
        box_unites.Add(self.ctrl_unites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_unites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def GetJours(self):
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        return jours_scolaires, jours_vacances

    def GetFeries(self):
        return self.ctrl_feries.GetValue() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Contrats")

    def OnBoutonOk(self, event): 
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
            
            if typeUnite == "Unitaire" :
                # Si unit� sans options (Standard)
                listeUnites.append({"IDunite":IDunite, "options":{}})
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

                    listeUnites.append({"IDunite":IDunite, "options":dictOptions})
                                    
        # M�morisation des donn�es
        self.resultats = {}
        self.resultats["jours_scolaires"] = jours_scolaires
        self.resultats["jours_vacances"] = jours_vacances
        self.resultats["feries"] = feries
        self.resultats["semaines"] = semaines
        self.resultats["unites"] = listeUnites
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)   

    def GetDonnees(self):
        return self.resultats

    def SetDonnees(self, donnees={}):
        """ Importation des donn�es """
##        self.ctrl_scolaires.SetJours("0;1;2;3;4")
##        self.ctrl_vacances.SetJours("0;1;2;3;4")
##        self.ctrl_semaines.SetValeur("2sem-2") 
##        self.ctrl_feries.SetValue(True)
##        listeUnites = [ 
##            {"IDunite" : 1, "options" : {}}, 
##            {"IDunite" : 2, "options" : {}}, 
##            {"IDunite" : 24, "options" : {"heure_debut" : "09:00", "heure_fin" : "10:00"}},
##            {"IDunite" : 24, "options" : {"heure_debut" : "10:00", "heure_fin" : "11:00"}},
##            ]
##        self.ctrl_unites.SetDonnees(listeUnites) 
        
        if donnees.has_key("jours_scolaires") : self.ctrl_scolaires.SetJours(donnees["jours_scolaires"])
        if donnees.has_key("jours_vacances") : self.ctrl_vacances.SetJours(donnees["jours_vacances"])
        if donnees.has_key("semaines") : self.ctrl_semaines.SetValeur(donnees["semaines"]) 
        if donnees.has_key("feries") : self.ctrl_feries.SetValue(donnees["feries"])
        if donnees.has_key("unites") : self.ctrl_unites.SetDonnees(donnees["unites"]) 


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDactivite=1)
    dlg.SetDonnees() 
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    print dlg.GetDonnees() 
    app.MainLoop()
