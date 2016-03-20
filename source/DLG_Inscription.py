#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Bandeau
import DLG_Inscription_activite

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
    def __init__(self, parent, type="groupes"):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.listeDonnees = []
        self.type = type

    def MAJ(self):
        selection_actuelle = self.GetID()
        self.listeDonnees = []
        if self.type == "groupes" : self.Importation_groupes()
        if self.type == "categories" : self.Importation_categories() 
        listeItems = []
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["label"]
                if label == None :
                    label = "Inconnu (ID%d)" % dictValeurs["ID"]
                listeItems.append(label)
        self.Set(listeItems)
        # Si un seul item dans la liste, le sélectionne...
        if len(self.listeDonnees) == 1 :
            self.Select(0)
        if selection_actuelle != None :
            self.SetID(selection_actuelle)

    def Importation_groupes(self):
        for dictGroupe in self.parent.dictActivite["groupes"] :
            ID = dictGroupe["IDgroupe"]
            label = dictGroupe["nom"]
            self.listeDonnees.append({"ID" : ID, "label" : label})

    def Importation_categories(self):
        for dictCategorie in self.parent.dictActivite["categories_tarifs"] :
            self.listeDonnees.append({"ID" : dictCategorie["IDcategorie_tarif"], "label" : dictCategorie["nom"], "listeVilles" : dictCategorie["listeVilles"]})
            
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
    
    def SelectCategorieSelonVille(self, cp=None, ville=None):
        if cp == None or ville == None :
            return False
        for dictTemp in self.listeDonnees :
            IDcategorie_tarif = dictTemp["ID"]
            for cpTemp, villeTemp in dictTemp["listeVilles"] :
                if cp == cpTemp and ville == villeTemp :
                    self.SetID(IDcategorie_tarif)
                    return True
        return False



        
class CTRL_Activite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.BORDER_THEME|wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = None
        self.SetBackgroundColour('White')

        self.ctrl_activite = wx.StaticText(self, -1, "")
        self.ctrl_activite.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_activite, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

    def MAJ(self):
        self.IDactivite = self.parent.dictActivite["IDactivite"]
        label = self.parent.dictActivite["nom"]
        self.ctrl_activite.SetLabel(label)
        self.Layout()

    def GetID(self):
        return self.IDactivite

    def GetNomActivite(self):
        return self.ctrl_activite.GetLabel()

# -----------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, mode="saisie", cp=None, ville=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent     
        self.cp = cp
        self.ville = ville
        self.dictActivite = None
        self.IDgroupe = None
        self.mode = mode
        
        intro = _(u"Pour inscrire un individu à une activité, vous devez sélectionner une activité, un groupe et une catégorie de tarifs.")
        if self.mode == "saisie" :
            titre = _(u"Saisie d'une inscription")
        else :
            titre = _(u"Modification d'une inscription")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")
        
        self.ctrl_famille = Choix_famille(self)
        
        self.staticbox_activite_staticbox = wx.StaticBox(self, -1, _(u"1. Sélectionnez une activité"))
        self.ctrl_activite = CTRL_Activite(self)
        self.bouton_activites = CTRL_Bouton_image.CTRL(self, texte=_(u"Rechercher"), cheminImage="Images/32x32/Loupe.png")

        self.staticbox_groupe_staticbox = wx.StaticBox(self, -1, _(u"2. Sélectionnez un groupe"))
        self.ctrl_groupes = ListBox(self, type="groupes")
        self.ctrl_groupes.SetMinSize((-1, 80))
        
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"3. Sélectionnez une catégorie de tarif"))
        self.ctrl_categories = ListBox(self, type="categories")
        self.ctrl_categories.SetMinSize((-1, 80))
        
        self.ctrl_parti = wx.CheckBox(self, -1, _(u"Est parti"))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonActivites, self.bouton_activites)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init contrôles
        if self.mode != "saisie" :
            self.bouton_activites.Enable(False)


    def __set_properties(self):
        self.SetTitle(_(u"Inscription à une activité"))
        self.ctrl_famille.SetToolTipString(_(u"Sélectionnez une famille"))
        self.ctrl_activite.SetToolTipString(_(u"Activité sélectionnée"))
        self.bouton_activites.SetToolTipString(_(u"Cliquez ici pour sélectionner une activité"))
        self.ctrl_groupes.SetToolTipString(_(u"Sélectionnez un groupe"))
        self.ctrl_parti.SetToolTipString(_(u"Cochez cette case si l'individu ne fréquente plus cette activité"))
        self.ctrl_categories.SetToolTipString(_(u"Sélectionnez une catégorie de tarif"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((500, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Famille + Parti
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=30)
        grid_sizer_options.Add(self.ctrl_famille, 1, wx.EXPAND, 0)
        grid_sizer_options.Add(self.ctrl_parti, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Activités
        staticbox_activite = wx.StaticBoxSizer(self.staticbox_activite_staticbox, wx.VERTICAL)
        grid_sizer_activite = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_activite.Add(self.ctrl_activite, 1, wx.EXPAND, 0)
        grid_sizer_activite.Add(self.bouton_activites, 1, wx.EXPAND, 0)
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
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableRow(4)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_activite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_groupes.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_categories.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie de tarifs !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérification du nombre d'inscrits max de l'activité
        if self.mode == "saisie" and self.dictActivite["nbre_places_disponibles"] != None :
            if self.dictActivite["nbre_places_disponibles"] <= 0 :
                dlg = wx.MessageDialog(None, _(u"Le nombre maximal d'inscrits autorisé pour cette activité (%d places max) a été atteint !\n\nSouhaitez-vous tout de même inscrire cet individu ?") % self.dictActivite["nbre_inscrits_max"], _(u"Nbre d'inscrit maximal atteint"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    return

        # Vérification du nombre d'inscrits max du groupe
        IDgroupe = self.ctrl_groupes.GetID()
        if IDgroupe != self.IDgroupe :
            for dictGroupe in self.dictActivite["groupes"] :
                if dictGroupe["IDgroupe"] == IDgroupe and dictGroupe["nbre_places_disponibles"] != None :
                    if dictGroupe["nbre_places_disponibles"] <= 0 :
                        dlg = wx.MessageDialog(None, _(u"Le nombre maximal d'inscrits autorisé sur ce groupe (%d places max) a été atteint !\n\nSouhaitez-vous tout de même inscrire cet individu ?") % dictGroupe["nbre_inscrits_max"], _(u"Nbre d'inscrit maximal atteint"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                        reponse = dlg.ShowModal()
                        dlg.Destroy()
                        if reponse != wx.ID_YES :
                            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonActivites(self, event):
        dlg = DLG_Inscription_activite.Dialog(self)
        dlg.SetIDactivite(self.GetIDactivite())
        if dlg.ShowModal() == wx.ID_OK:
            IDactivite = dlg.GetIDactivite()
            self.SetIDactivite(IDactivite)
        dlg.Destroy()

    def SetIDactivite(self, IDactivite=None):
        self.dictActivite = self.GetDictActivite(IDactivite)
        self.ctrl_activite.MAJ()
        self.ctrl_groupes.MAJ()
        self.ctrl_categories.MAJ()
        self.ctrl_categories.SelectCategorieSelonVille(self.cp, self.ville)

    def GetDictActivite(self, IDactivite=None):
        dictActivite = {}

        DB = GestionDB.DB()

        # Recherche des activités
        req = """SELECT nom, abrege, date_debut, date_fin, nbre_inscrits_max
        FROM activites
        WHERE IDactivite=%d;""" % IDactivite
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()

        nom, abrege, date_debut, date_fin, nbre_inscrits_max = listeActivites[0]
        dictActivite = {"IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "nbre_inscrits_max" : nbre_inscrits_max}

        # Recherche des inscriptions existantes
        req = """SELECT IDgroupe, COUNT(IDinscription)
        FROM inscriptions
        WHERE IDactivite=%d
        GROUP BY IDgroupe;""" % IDactivite
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        dictActivite["inscriptions"] = {}
        for IDgroupe, nbre_inscrits in listeInscriptions :
            dictActivite["inscriptions"][IDgroupe] = nbre_inscrits

        # Recherche des groupes
        req = """SELECT IDgroupe, nom, nbre_inscrits_max
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % IDactivite
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        dictActivite["groupes"] = []
        for IDgroupe, nom, nbre_inscrits_max in listeGroupes :

            # Recherche le nombre d'inscrits sur chaque groupe
            if dictActivite["inscriptions"].has_key(IDgroupe) :
                nbre_inscrits = dictActivite["inscriptions"][IDgroupe]
            else :
                nbre_inscrits = 0

            # Recherche du nombre de places disponibles sur le groupe
            if nbre_inscrits_max not in (None, 0) :
                nbre_places_disponibles = nbre_inscrits_max - nbre_inscrits
            else :
                nbre_places_disponibles = None

            # Mémorise le groupe
            dictActivite["groupes"].append({"IDgroupe" : IDgroupe, "nom" : nom, "nbre_places_disponibles" : nbre_places_disponibles, "nbre_inscrits" : nbre_inscrits, "nbre_inscrits_max" : nbre_inscrits_max})

        # Recherche le nombre d'inscrits total de l'activité
        dictActivite["nbre_inscrits"] = 0
        for IDgroupe, nbre_inscrits in dictActivite["inscriptions"].iteritems() :
            dictActivite["nbre_inscrits"] += nbre_inscrits

        # Recherche du nombre de places disponibles sur l'activité
        if dictActivite["nbre_inscrits_max"] not in (None, 0) :
            dictActivite["nbre_places_disponibles"] = dictActivite["nbre_inscrits_max"] - dictActivite["nbre_inscrits"]
        else :
            dictActivite["nbre_places_disponibles"] = None

        # Recherche des catégories de tarifs
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom; """ % IDactivite
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()

        # Recherche des villes rattachées à la catégorie de tarif
        req = """SELECT IDville, IDcategorie_tarif, cp, nom
        FROM categories_tarifs_villes; """
        DB.ExecuterReq(req)
        listeVilles = DB.ResultatReq()

        dictVilles = {}
        for IDville, IDcategorie_tarif, cp, nom in listeVilles :
            if dictVilles.has_key(IDcategorie_tarif) == False :
                dictVilles[IDcategorie_tarif] = []
            dictVilles[IDcategorie_tarif].append((cp, nom))

        dictActivite["categories_tarifs"] = []
        for IDcategorie_tarif, nom in listeCategories :
            if dictVilles.has_key(IDcategorie_tarif) :
                listeVilles = dictVilles[IDcategorie_tarif]
            else:
                listeVilles = []
            dictActivite["categories_tarifs"].append({"IDcategorie_tarif" : IDcategorie_tarif, "nom" : nom, "listeVilles" : listeVilles})

        DB.Close()

        return dictActivite

    def SetDonnees(self, IDactivite=None, IDgroupe=None, IDcategorie=None, parti=0):
        self.SetIDactivite(IDactivite)
        self.ctrl_groupes.SetID(IDgroupe)
        self.IDgroupe = IDgroupe
        self.ctrl_categories.SetID(IDcategorie)
        if parti == None : parti = 0
        self.ctrl_parti.SetValue(parti)


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
        if self.dictActivite != None :
            return self.dictActivite["IDactivite"]
        else :
            return None
    
    def GetNomActivite(self):
        return self.ctrl_activite.GetNomActivite()
    
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

    def GetParti(self):
        return self.ctrl_parti.GetValue()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
