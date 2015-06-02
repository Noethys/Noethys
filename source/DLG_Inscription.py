#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Bandeau

import GestionDB



class Choix_famille(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeDonnees = []
    
    def SetListeDonnees(self, listeDonnees=[]):
        self.listeNoms = []
        self.listeDonnees = listeDonnees
        for dictTemp in listeDonnees :
            IDfamille = dictTemp["IDfamille"]
            nom = _(u"Famille de %s") % dictTemp["nom"]
            self.listeNoms.append(nom)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for dictTemp in self.listeDonnees :
            IDfamille = dictTemp["IDfamille"]
            if IDfamille == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]["IDfamille"]

# ------------------------------------------------------------------------------------------------------------------------------------------



class ListBox(wx.ListBox):
    def __init__(self, parent, type="activites", IDcondition=None, cp=None, ville=None):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.listeDonnees = []
        self.type = type
        self.IDcondition = IDcondition
        self.cp = cp
        self.ville = ville
        self.Bind(wx.EVT_LISTBOX, self.OnSelection,)
    
    def MAJ(self, IDcondition=None):
        if IDcondition != None : 
            self.IDcondition = IDcondition
        self.listeDonnees = []
        if self.type == "activites" : self.Importation_activites() 
        if self.type == "groupes" : self.Importation_groupes() 
        if self.type == "categories" : self.Importation_categories() 
        listeItems = []
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["nom"]
                if label == None :
                    label = "Inconnu (ID%d)" % dictValeurs["ID"]
                listeItems.append(label)
        self.Set(listeItems)
        # Si un seul item dans la liste, le sélectionne...
        if self.type != "activites" and len(self.listeDonnees) == 1 :
            self.Select(0)
    
    def OnSelection(self, event):
        if self.type == "activites" : 
            IDactivite = self.GetID()
            self.parent.ctrl_groupes.MAJ(IDactivite)
            self.parent.ctrl_categories.MAJ(IDactivite)
            self.parent.ctrl_categories.SelectCategorieSelonVille()
        
    def Importation_activites(self):
        if self.GetParent().ctrl_activites_valides.GetValue() == True :
            dateDuJour = str(datetime.date.today())
            conditionDate = "WHERE date_fin >= '%s' " % dateDuJour
        else:
            conditionDate = ""
        db = GestionDB.DB()
        req = """SELECT activites.IDactivite, nom, nbre_inscrits_max, COUNT(inscriptions.IDinscription)
        FROM activites
        LEFT JOIN inscriptions ON inscriptions.IDactivite = activites.IDactivite
        %s
        GROUP BY activites.IDactivite
        ORDER BY nom; """ % conditionDate
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDactivite, nom, nbre_inscrits_max, nbre_inscrits in listeDonnees :
            valeurs = { "ID" : IDactivite, "nom" : nom, "nbre_inscrits_max" : nbre_inscrits_max, "nbre_inscrits" : nbre_inscrits }
            self.listeDonnees.append(valeurs)

    def Importation_groupes(self):
        if self.IDcondition == None : return
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom
        FROM groupes 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDcondition
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDgroupe, nom in listeDonnees :
            valeurs = { "ID" : IDgroupe, "nom" : nom }
            self.listeDonnees.append(valeurs)

    def Importation_categories(self):
        if self.IDcondition == None : return
        DB = GestionDB.DB()
        
        # Recherche des catégories
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs 
        WHERE IDactivite=%d
        ORDER BY nom; """ % self.IDcondition
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        
        # Recherche des villes rattachées
        req = """SELECT IDville, IDcategorie_tarif, cp, nom
        FROM categories_tarifs_villes
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeVilles = DB.ResultatReq()
        DB.Close()
        dictVilles = {}
        for IDville, IDcategorie_tarif, cp, nom in listeVilles :
            if dictVilles.has_key(IDcategorie_tarif) == False :
                dictVilles[IDcategorie_tarif] = []
            dictVilles[IDcategorie_tarif].append((cp, nom))
            
        for IDcategorie_tarif, nom in listeCategories :
            if dictVilles.has_key(IDcategorie_tarif) :
                listeVilles = dictVilles[IDcategorie_tarif]
            else:
                listeVilles = []
            valeurs = { "ID" : IDcategorie_tarif, "nom" : nom, "listeVilles" : listeVilles }
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
    
    def GetInfosSelection(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]
    
    def SelectCategorieSelonVille(self):
        if self.cp == None or self.ville == None : 
            return False
        for dictTemp in self.listeDonnees :
            IDcategorie_tarif = dictTemp["ID"]
            for cpTemp, villeTemp in dictTemp["listeVilles"] :
                if self.cp == cpTemp and self.ville == villeTemp :
                    self.SetID(IDcategorie_tarif)
                    return True
        return False
            
        


# -----------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, cp=None, ville=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent     
        self.cp = cp
        self.ville = ville 
        
        intro = _(u"Pour inscrire un individu à une activité, vous devez sélectionner une activité, un groupe et une catégorie de tarifs.")
        titre = _(u"Inscription à une activité")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")
        
        self.ctrl_famille = Choix_famille(self)
        
        self.staticbox_activite_staticbox = wx.StaticBox(self, -1, _(u"1. Sélectionnez une activité"))
        self.ctrl_activites = ListBox(self, type="activites")
        self.ctrl_activites.SetMinSize((-1, 80))
        
        self.ctrl_activites_valides = wx.CheckBox(self, -1, _(u"Afficher uniquement les activités ouvertes"))
        self.ctrl_activites_valides.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.ctrl_activites_valides.SetValue(True) 
        
        self.staticbox_groupe_staticbox = wx.StaticBox(self, -1, _(u"2. Sélectionnez un groupe"))
        self.ctrl_groupes = ListBox(self, type="groupes", IDcondition=None)
        self.ctrl_groupes.SetMinSize((-1, 80))
        
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"3. Sélectionnez une catégorie de tarif"))
        self.ctrl_categories = ListBox(self, type="categories", IDcondition=None, cp=cp, ville=ville)
        self.ctrl_categories.SetMinSize((-1, 80))
        
        self.ctrl_parti = wx.CheckBox(self, -1, _(u"Est parti"))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHECKBOX, self.OnCocheActivitesValides, self.ctrl_activites_valides)
        
        # Init contrôles
        self.ctrl_activites.MAJ() 

    def __set_properties(self):
        self.SetTitle(_(u"Inscription à une activité"))
        self.ctrl_famille.SetToolTipString(_(u"Sélectionnez une famille"))
        self.ctrl_activites.SetToolTipString(_(u"Sélectionnez une activité"))
        self.ctrl_activites_valides.SetToolTipString(_(u"Cochez cette case pour afficher uniquement les activités encore ouvertes à ce jour"))
        self.ctrl_groupes.SetToolTipString(_(u"Sélectionnez un groupe"))
        self.ctrl_parti.SetToolTipString(_(u"Cochez cette case si l'individu ne fréquente plus cette activité"))
        self.ctrl_categories.SetToolTipString(_(u"Sélectionnez une catégorie de tarif"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((380, 590))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Famille
        grid_sizer_base.Add(self.ctrl_famille, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Activités
        staticbox_activite = wx.StaticBoxSizer(self.staticbox_activite_staticbox, wx.VERTICAL)
        grid_sizer_activite = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_activite.Add(self.ctrl_activites, 1, wx.EXPAND, 0)
        grid_sizer_activite.Add(self.ctrl_activites_valides, 1, wx.ALIGN_RIGHT, 0)
        grid_sizer_activite.AddGrowableRow(0)
        grid_sizer_activite.AddGrowableCol(0)
        staticbox_activite.Add(grid_sizer_activite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activite, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Groupes
        staticbox_groupe = wx.StaticBoxSizer(self.staticbox_groupe_staticbox, wx.VERTICAL)
        staticbox_groupe.Add(self.ctrl_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_groupe, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Catégories de tarifs
        staticbox_categorie = wx.StaticBoxSizer(self.staticbox_categorie_staticbox, wx.VERTICAL)
        staticbox_categorie.Add(self.ctrl_categories, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_categorie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_base.Add(self.ctrl_parti, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
##        grid_sizer_base.AddGrowableRow(3)
##        grid_sizer_base.AddGrowableRow(4)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_activites.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_groupes.GetID() == None and len(self.ctrl_groupes.listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_categories.GetID() == None and len(self.ctrl_categories.listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie de tarifs !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérification du nombre d'inscrits max de l'activité
        infosActivite = self.ctrl_activites.GetInfosSelection()
        nbre_inscrits_max = infosActivite["nbre_inscrits_max"]
        nbre_inscrits = infosActivite["nbre_inscrits"]
        if nbre_inscrits_max != None and nbre_inscrits != None :
            nbrePlacesRestantes = nbre_inscrits_max - nbre_inscrits
            if nbrePlacesRestantes <= 0 :
                dlg = wx.MessageDialog(None, _(u"Le nombre maximal d'inscrits autorisé pour cette activité a été atteint !\n\nSouhaitez-vous tout de même inscrire cet individu ?"), _(u"Nbre d'inscrit maximal atteint"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal() 
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def OnCocheActivitesValides(self, event):
        self.ctrl_activites.MAJ()
        self.ctrl_groupes.Clear()
        self.ctrl_categories.Clear()
        
    def SetFamille(self, listeNoms=[], listeIDfamille=[], IDfamille=None, verrouillage=False) :
        listeDonnees = []
        for index in range(0, len(listeNoms)) :
            dictTemp = {"IDfamille" : listeIDfamille[index], "nom" : listeNoms[index] }
            listeDonnees.append(dictTemp)
        self.ctrl_famille.SetListeDonnees(listeDonnees)
        self.ctrl_famille.SetID(IDfamille)
        if len(listeIDfamille) < 2 or verrouillage == True :
            self.ctrl_famille.Enable(False)
            
    def GetIDfamille(self):
        return self.ctrl_famille.GetID() 

    def GetIDactivite(self):
        IDactivite = self.ctrl_activites.GetID()
        return IDactivite
    
    def GetNomActivite(self):
        return self.ctrl_activites.GetStringSelection() 
    
    def GetIDgroupe(self):
        IDgroupe = self.ctrl_groupes.GetID()
        return IDgroupe

    def GetNomGroupe(self):
        return self.ctrl_groupes.GetStringSelection() 

    def GetIDcategorie(self):
        IDcategorie = self.ctrl_categories.GetID()
        return IDcategorie

    def GetNomCategorie(self):
        return self.ctrl_categories.GetStringSelection() 
    
    def SetIDactivite(self, IDactivite=None):
        if IDactivite != None :
            self.ctrl_activites_valides.SetValue(False)
            self.ctrl_activites_valides.Enable(False)
            self.ctrl_activites.MAJ() 
            self.ctrl_activites.SetID(IDactivite)
            self.ctrl_groupes.MAJ(IDactivite)
            self.ctrl_categories.MAJ(IDactivite)
            
    def SetIDgroupe(self, IDgroupe=None):
        self.ctrl_groupes.SetID(IDgroupe)

    def SetIDcategorie(self, IDcategorie=None):
        self.ctrl_categories.SetID(IDcategorie)
    
    def SetParti(self, parti=0):
        if parti == None : parti = 0
        self.ctrl_parti.SetValue(parti)
    
    def GetParti(self):
        return self.ctrl_parti.GetValue()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
