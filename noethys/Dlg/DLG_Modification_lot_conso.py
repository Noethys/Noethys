#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Selection_lot_conso



# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, IDactivite=None):
        self.Importation(IDactivite) 
        listeItems = []
        self.Clear() 
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["nom"]
                listeItems.append(label)
            self.Set(listeItems)
            self.Select(0)
        
    def Importation(self, IDactivite):
        self.listeDonnees = []
        if IDactivite == None : return
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom
        FROM groupes 
        WHERE IDactivite=%d
        ORDER BY nom; """ % IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.listeDonnees.append( {"ID" : None, "nom" : _(u"Aucune modification")} )
        for ID, nom in listeDonnees :
            valeurs = { "ID" : ID, "nom" : nom }
            self.listeDonnees.append(valeurs)
            
    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["ID"] :
                self.SetSelection(index)
                return
            index += 1
        
    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["ID"]
        return ID

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Modes(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, IDactivite=None):
        self.Importation(IDactivite) 
        listeItems = []
        self.Clear() 
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["nom"]
                listeItems.append(label)
            self.Set(listeItems)
            self.Select(0)
        
    def Importation(self, IDactivite=None):
        self.listeDonnees = []
        if IDactivite == None : return
        self.listeDonnees = [
            {"ID" : None, "nom" : _(u"Aucune modification")},
            {"ID" : "reservation", "nom" : _(u"Réservation")},
            {"ID" : "attente", "nom" : _(u"Attente")},
            {"ID" : "refus", "nom" : _(u"Refus")},
        ]
            
    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["ID"] :
                self.SetSelection(index)
                return
            index += 1
        
    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["ID"]
        return ID

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Etats(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, IDactivite=None):
        self.Importation(IDactivite) 
        listeItems = []
        self.Clear() 
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["nom"]
                listeItems.append(label)
            self.Set(listeItems)
            self.Select(0)
        
    def Importation(self, IDactivite=None):
        self.listeDonnees = []
        if IDactivite == None : return
        self.listeDonnees = [
            {"ID" : None, "nom" : _(u"Aucune modification")},
            {"ID" : "reservation", "nom" : _(u"Pointage en attente")},
            {"ID" : "present", "nom" : _(u"Présent")},
            {"ID" : "absentj", "nom" : _(u"Absence justifiée")},
            {"ID" : "absenti", "nom" : _(u"Absence injustifiée")},
        ]
            
    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["ID"] :
                self.SetSelection(index)
                return
            index += 1
        
    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["ID"]
        return ID

# ---------------------------------------------------------------------------------------------------------------


class CTRL_Modifications(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.box_groupe_staticbox = wx.StaticBox(self, -1, _(u"Groupe"))
        self.ctrl_groupe = CTRL_Groupes(self)
        
        self.box_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode"))
        self.ctrl_mode = CTRL_Modes(self)

        self.box_etat_staticbox = wx.StaticBox(self, -1, _(u"Etat"))
        self.ctrl_etat = CTRL_Etats(self)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        box_etat = wx.StaticBoxSizer(self.box_etat_staticbox, wx.VERTICAL)
        box_mode = wx.StaticBoxSizer(self.box_mode_staticbox, wx.VERTICAL)
        box_groupe = wx.StaticBoxSizer(self.box_groupe_staticbox, wx.VERTICAL)
        box_groupe.Add(self.ctrl_groupe, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_groupe, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        box_mode.Add(self.ctrl_mode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_mode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        box_etat.Add(self.ctrl_etat, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_etat, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
    
    def SetActivite(self, IDactivite=None):
        self.ctrl_groupe.MAJ(IDactivite)
        self.ctrl_mode.MAJ(IDactivite)
        self.ctrl_etat.MAJ(IDactivite)
    
    def GetGroupe(self):
        return self.ctrl_groupe.GetID()

    def GetMode(self):
        return self.ctrl_mode.GetID()

    def GetEtat(self):
        return self.ctrl_etat.GetID()


class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, selectionPeriode=[], selectionIndividus=[], selectionActivite=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Modification_lot_conso", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.dictResultats = {}
        
        # Bandeau
        intro = _(u"Vous pouvez ici modifier un lot de consommations. Commencez par définir les paramètres de sélection des consommations puis sélectionnez un ou plusieurs paramètres à modifier. Remarquez que les modifications ne seront validées définitivement que lorsque vous vous quitterez la grille des consommations.")
        titre = _(u"Modification d'un lot de consommations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Forfait.png")

        # Panel Selection
        self.box_selection_staticbox = wx.StaticBox(self, -1, _(u"Sélection des consommations"))
        self.ctrl_selection = CTRL_Selection_lot_conso.CTRL(self, IDfamille=self.IDfamille, mode="modification", listeDates=selectionPeriode, selectionIndividus=selectionIndividus, selectionActivite=selectionActivite)
        self.ctrl_selection.SetMinSize((500, -1))
        # Panel Modifications
        self.box_modifications_staticbox = wx.StaticBox(self, -1, _(u"Modifications à appliquer"))
        self.ctrl_modifications = CTRL_Modifications(self)
        self.ctrl_modifications.SetBackgroundColour("#F0FBED")
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init Contrôles
        self.ctrl_selection.OnChoixActivite(None)

    def __set_properties(self):
        self.SetTitle(_(u"Modification des consommations par lot"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer les modifications")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((800, 640))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        box_modifications = wx.StaticBoxSizer(self.box_modifications_staticbox, wx.VERTICAL)
        box_selection = wx.StaticBoxSizer(self.box_selection_staticbox, wx.VERTICAL)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        box_selection.Add(self.ctrl_selection, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_selection, 1, wx.EXPAND, 0)
        box_modifications.Add(self.ctrl_modifications, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_contenu.Add(box_modifications, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
##        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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
    
    def SetActivite(self, IDactivite=None):
        self.ctrl_modifications.SetActivite(IDactivite)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
    
    def GetDictResultats(self):
        return self.dictResultats

    def OnBoutonOk(self, event): 
        self.dictResultats = {}
        
        # Récupération des paramètres de sélection
        selectionPeriodes = self.ctrl_selection.GetPeriodes()
        selectionIndividus = self.ctrl_selection.GetIndividus()
        selectionActivite = self.ctrl_selection.GetActivite()
        selectionGroupes = self.ctrl_selection.GetGroupes()
        selectionUnites = self.ctrl_selection.GetUnites()
        selectionModes = self.ctrl_selection.GetModes()
        selectionEtats = self.ctrl_selection.GetEtats()
        
        self.dictResultats["selection"] = {
            "periodes" : selectionPeriodes,
            "individus" : selectionIndividus,
            "activite" : selectionActivite,
            "groupes" : selectionGroupes,
            "unites" : selectionUnites,
            "modes" : selectionModes,
            "etats" : selectionEtats,
            }
        
        print "selectionPeriodes =", selectionPeriodes
        print "selectionIndividus =", selectionIndividus
        print "selectionActivite =", selectionActivite
        print "selectionGroupes =", selectionGroupes
        print "selectionUnites =", selectionUnites
        print "selectionModes =", selectionModes
        print "selectionEtats =", selectionEtats
        print "--------------------"
        
        # Récupération des paramètres de modification
        modificationGroupe = self.ctrl_modifications.GetGroupe()
        modificationMode = self.ctrl_modifications.GetMode()
        modificationEtat = self.ctrl_modifications.GetEtat()
        
        self.dictResultats["modification"] = {
            "groupe" : modificationGroupe,
            "mode" : modificationMode,
            "etat" : modificationEtat,
            }
            
        print "modificationGroupe =", modificationGroupe
        print "modificationMode =", modificationMode
        print "modificationEtat =", modificationEtat
        
        print "--------------------------------------------------------------------------------------------------"
        
        
        
        
        
        
        
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=7)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
