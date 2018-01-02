#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import copy
from Ctrl import CTRL_Questionnaire
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Utils import UTILS_Locations
from Utils import UTILS_Customize
import GestionDB
from Ol import OL_Filtres_questionnaire
from Ol import OL_Produits
import wx.html as html



class CTRL_Loueur(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.IDfamille = None

    def SetIDfamille(self, IDfamille=None):
        self.IDfamille = IDfamille

        # Recherche du nom des titulaires
        if self.IDfamille != None :
            dictNomsTitulaires = UTILS_Titulaires.GetTitulaires([self.IDfamille, ])
            nomsTitulaires = dictNomsTitulaires[self.IDfamille]["titulairesSansCivilite"]
            self.SetValue(nomsTitulaires)
        else :
            self.SetValue("")

    def GetIDfamille(self):
        return self.IDfamille



class CTRL_Categories(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.liste_donnees = []
        self.liste_categories = []

    def SetListeCategories(self, liste_categories=[]):
        self.liste_categories = liste_categories

        if len(self.liste_categories) == 0: condition = "()"
        elif len(self.liste_categories) == 1: condition = "(%d)" % self.liste_categories[0]
        else: condition = str(tuple(self.liste_categories))

        # Recherche des caractéristiques des catégories
        db = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM produits_categories 
        WHERE IDcategorie IN %s;""" % condition
        db.ExecuterReq(req)
        self.listeDonnees = db.ResultatReq()
        db.Close()
        liste_labels = []
        for IDcategorie, nomCategorie in self.listeDonnees :
            liste_labels.append(nomCategorie)

        if len(liste_labels) > 0 :
            label = ", ".join(liste_labels)
            couleur = wx.BLACK
        else :
            label = _(u"Indifférent")
            couleur = wx.LIGHT_GREY
        self.SetForegroundColour(couleur)

        # Nom
        self.SetValue(label)

    def GetListeCategories(self):
        return self.liste_categories




class CTRL_Produits(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.liste_donnees = []
        self.liste_produits = []

    def SetListeProduits(self, liste_produits=[]):
        self.liste_produits = liste_produits

        if len(self.liste_produits) == 0: condition = "()"
        elif len(self.liste_produits) == 1: condition = "(%d)" % self.liste_produits[0]
        else: condition = str(tuple(self.liste_produits))

        # Recherche des caractéristiques des produits
        db = GestionDB.DB()
        req = """SELECT produits.IDproduit, produits.nom, produits.IDcategorie, produits.observations, produits_categories.nom
        FROM produits 
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDproduit IN %s;""" % condition
        db.ExecuterReq(req)
        self.listeDonnees = db.ResultatReq()
        db.Close()
        liste_labels = []
        for IDproduit, nomProduit, IDcategorie, observations, nomCategorie in self.listeDonnees :
            label = u"%s (%s)" % (nomProduit, nomCategorie)
            liste_labels.append(label)

        if len(liste_labels) > 0 :
            label = ", ".join(liste_labels)
            couleur = wx.BLACK
        else :
            label = _(u"Indifférent")
            couleur = wx.LIGHT_GREY
        self.SetForegroundColour(couleur)

        # Nom
        self.SetValue(label)

    def GetListeProduits(self):
        return self.liste_produits

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class PAGE_Criteres(wx.Panel):
    def __init__(self, parent, IDdemande=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDdemande = IDdemande

        self.label_categories = wx.StaticText(self, -1, _(u"Catégories :"))
        self.ctrl_categories = CTRL_Categories(self)
        self.bouton_categories = wx.Button(self, -1, _(u"Sélectionner"))

        self.label_produits = wx.StaticText(self, -1, _(u"Produits :"))
        self.ctrl_produits = CTRL_Produits(self)
        self.bouton_produits = wx.Button(self, -1, _(u"Sélectionner"))

        self.label_filtres = wx.StaticText(self, -1, _(u"Questions :"), style=wx.ALIGN_RIGHT)
        self.ctrl_filtres = OL_Filtres_questionnaire.ListView(self, listeDonnees=[], listeTypes=["produit",], CallFonctionOnMAJ=self.MAJListePropositions, id=-1, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_filtres.SetMinSize((400, 50))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Properties
        self.ctrl_categories.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner des catégories")))
        self.bouton_categories.SetToolTip(wx.ToolTip(_(u"Choix de catégories")))
        self.ctrl_produits.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner des produits")))
        self.bouton_produits.SetToolTip(wx.ToolTip(_(u"Choix de catégories")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un filtre sur les questionnaires")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le filtre sélectionné")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le filtre sélectionné")))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.Ajouter_filtre, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier_filtre, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer_filtre, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonProduits, self.bouton_produits)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_criteres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_criteres.Add(self.label_categories, 0, wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_categories = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_categories.Add(self.ctrl_categories, 0, wx.EXPAND, 0)
        grid_sizer_categories.Add(self.bouton_categories, 0, 0, 0)
        grid_sizer_categories.AddGrowableCol(0)
        grid_sizer_criteres.Add(grid_sizer_categories, 1, wx.EXPAND, 0)

        grid_sizer_criteres.Add(self.label_produits, 0, wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_produits = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_produits.Add(self.ctrl_produits, 0, wx.EXPAND, 0)
        grid_sizer_produits.Add(self.bouton_produits, 0, 0, 0)
        grid_sizer_produits.AddGrowableCol(0)
        grid_sizer_criteres.Add(grid_sizer_produits, 1, wx.EXPAND, 0)

        grid_sizer_criteres.Add(self.label_filtres, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_filtres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_filtres.Add(self.ctrl_filtres, 1, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_filtres.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        grid_sizer_filtres.AddGrowableCol(0)
        grid_sizer_filtres.AddGrowableRow(0)

        grid_sizer_criteres.Add(grid_sizer_filtres, 1, wx.EXPAND, 0)

        grid_sizer_criteres.AddGrowableCol(1)
        grid_sizer_criteres.AddGrowableRow(2)

        sizer_base.Add(grid_sizer_criteres, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

    def OnBoutonCategories(self, event):
        from Dlg import DLG_Selection_categorie_produit
        dlg = DLG_Selection_categorie_produit.Dialog(self, liste_categories=self.ctrl_categories.GetListeCategories(), selection_multiple=True, selection_obligatoire=False)
        if dlg.ShowModal() == wx.ID_OK:
            liste_produits = dlg.GetListeCategories()
            self.ctrl_categories.SetListeCategories(liste_produits)
            self.MAJListePropositions()
        dlg.Destroy()

    def OnBoutonProduits(self, event):
        from Dlg import DLG_Selection_produit
        dlg = DLG_Selection_produit.Dialog(self, liste_produits=self.ctrl_produits.GetListeProduits(), selection_multiple=True, selection_obligatoire=False)
        if dlg.ShowModal() == wx.ID_OK:
            liste_produits = dlg.GetListeProduits()
            self.ctrl_produits.SetListeProduits(liste_produits)
            self.MAJListePropositions()
        dlg.Destroy()

    def Ajouter_filtre(self, event=None):
        self.ctrl_filtres.Ajouter()
        #self.MAJListePropositions()

    def Modifier_filtre(self, event=None):
        self.ctrl_filtres.Modifier()
        #self.MAJListePropositions()

    def Supprimer_filtre(self, event=None):
        self.ctrl_filtres.Supprimer()
        #self.MAJListePropositions()

    def MAJListePropositions(self):
        # Récupération de la liste des filtres actuelle
        dictFiltres = {self.IDdemande : []}
        for track in self.ctrl_filtres.GetTracks() :
            dictFiltres[self.IDdemande].append({"IDfiltre":track.IDfiltre, "IDquestion":track.IDquestion, "choix":track.choix, "criteres":track.criteres, "controle":track.controle})

        # Récupération des paramètres de la demande
        dictDemande = {"IDdemande": self.IDdemande, "categories": self.ctrl_categories.GetListeCategories(), "produits": self.ctrl_produits.GetListeProduits()}

        # Recherche les produits disponibles à proposer
        dictPropositions = UTILS_Locations.GetPropositionsLocations(dictFiltresSelection=dictFiltres, dictDemandeSelection=dictDemande, uniquement_disponibles=False)
        texte = self.GetGrandParent().ctrl_statut.GetPageByCode("attente").ctrl_propositions.SetDictPropositions(dictPropositions, IDdemande=self.IDdemande)
        self.GetGrandParent().ctrl_statut.GetPageByCode("attente").label_propositions.SetLabel(texte)



class PAGE_Questionnaire(wx.Panel):
    def __init__(self, parent, IDdemande=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Questionnaire
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="location_demande", IDdonnee=IDdemande)
        self.ctrl_questionnaire.SetMinSize((620, 80))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_questionnaire, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()




class Notebook(wx.Notebook):
    def __init__(self, parent, IDdemande=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT)
        self.dictPages = {}

        self.listePages = [
            ("criteres", _(u"Critères"), PAGE_Criteres(self, IDdemande=IDdemande)),
            ("questionnaire", _(u"Questionnaire"), PAGE_Questionnaire(self, IDdemande=IDdemande)),
        ]

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage in self.listePages:
            page = ctrlPage
            self.AddPage(page, labelPage)
            self.dictPages[codePage] = {'ctrl': page, 'index': index}
            index += 1

    def GetPageActive(self):
        index = self.GetSelection()
        return self.GetPage(self.listePages[index][0])

    def GetPage(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]

    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def Validation(self):
        for codePage, dictPage in self.dictPages.iteritems():
            if dictPage["ctrl"].Validation() == False:
                self.AffichePage(codePage)
                return False
        return True





# ---------------------------------------------------------------------------------------------

class PAGE_Statut_attente(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Propositions
        self.label_propositions = wx.StaticText(self, -1, _(u"Produits proposés :"))
        self.ctrl_propositions = OL_Produits.ListView(self, id=-1, afficher_detail_location=False, on_double_click="consultation", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_propositions.SetMinSize((100, 50))
        self.ctrl_propositions.afficher_uniquement_disponibles = True

        # Options
        self.radio_produits_disponibles = wx.RadioButton(self, -1, _(u"Les produits disponibles"), style=wx.RB_GROUP)
        self.radio_produits_possibles = wx.RadioButton(self, -1, _(u"Les produits potentiels"))

        self.radio_produits_disponibles.SetToolTip(wx.ToolTip(_(u"Afficher les produits disponibles répondant aux critères")))
        self.radio_produits_possibles.SetToolTip(wx.ToolTip(_(u"Afficher tous les produits répondant aux critères donnés")))

        # Bouton Attribuer
        self.bouton_attribuer = CTRL_Bouton_image.CTRL(self, texte=_(u"Attribuer le produit sélectionné"), cheminImage="Images/32x32/Location.png")
        self.bouton_attribuer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour attribuer le produit sélectionné dans la liste")))

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioProduits, self.radio_produits_disponibles)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioProduits, self.radio_produits_possibles)

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAttribuer, self.bouton_attribuer)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_propositions, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_propositions, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.radio_produits_disponibles, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_commandes.Add(self.radio_produits_possibles, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_commandes.Add( (10, 10), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_commandes.Add(self.bouton_attribuer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_commandes.AddGrowableCol(2)

        grid_sizer_base.Add(grid_sizer_commandes, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnRadioProduits(self, event=None):
        self.ctrl_propositions.afficher_uniquement_disponibles = self.radio_produits_disponibles.GetValue()
        self.GetGrandParent().notebook.GetPage("criteres").MAJListePropositions()

    def Validation(self):
        return True

    def OnBoutonAttribuer(self, event):
        IDproduit = self.ctrl_propositions.GetID()
        if IDproduit == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un produit disponible dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Création d'une location
        self.GetGrandParent().Attribution(IDproduit)


class PAGE_Statut_refusee(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.label_motif = wx.StaticText(self, -1, _(u"Motif du refus :"))
        self.ctrl_motif = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_motif, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_motif, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def Validation(self):
        return True



class CTRL_Attribution(html.HtmlWindow):
    def __init__(self, parent, texte=""):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SIMPLE_BORDER | wx.html.HW_NO_SELECTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetPage(texte)
        self.IDlocation = None

    def SetTexte(self, texte=""):
        self.SetPage(texte)

    def SetIDlocation(self, IDlocation):
        self.IDlocation = IDlocation

        # Importation des données de la location
        DB = GestionDB.DB()
        req = """SELECT IDfamille, locations.IDproduit, locations.observations, date_debut, date_fin,
        produits.nom, produits_categories.nom
        FROM locations 
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDlocation=%d;""" % self.IDlocation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDfamille, IDproduit, observations, date_debut, date_fin, nomProduit, nomCategorie = listeDonnees[0]

        date_debut_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_debut), "%d/%m/%Y")
        heure_debut_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_debut), "%Hh%M")
        texte_debut = _(u"%s à %s") % (date_debut_temp, heure_debut_temp)

        if date_fin != None :
            date_fin_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_fin), "%d/%m/%Y")
            heure_fin_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_fin), "%Hh%M")
            texte_fin = _(u"%s à %s") % (date_fin_temp, heure_fin_temp)
        else :
            texte_fin = _(u"Non définie")

        if len(observations) > 0 :
            texte_observations = _(u"<BR>Notes : %s") % observations
        else :
            texte_observations = ""

        texte = _(u"""
        <FONT SIZE=5><B>Demande satisfaite</B><BR></FONT>
        <BR>
        Produit : <b>%s</b><BR>
        Catégorie : %s <BR>
        <BR>
        Début de location : %s <BR>
        Fin de location : %s <BR>
        %s
        """) % (nomProduit, nomCategorie, texte_debut, texte_fin, texte_observations)
        self.SetTexte(texte)

    def GetIDlocation(self):
        return self.IDlocation

    def Validation(self):
        return True


class PAGE_Statut_attribuee(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDlocation = None

        self.label_attribution = wx.StaticText(self, -1, _(u"Location attribuée :"))
        self.ctrl_attribution = MyHtml(self)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_attribution, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_attribution, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def SetIDlocation(self, IDlocation):
        self.IDlocation = IDlocation

        # Importation des données de la location
        DB = GestionDB.DB()
        req = """SELECT IDfamille, locations.IDproduit, locations.observations, date_debut, date_fin,
        produits.nom, produits_categories.nom
        FROM locations 
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDlocation=%d;""" % self.IDlocation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDfamille, IDproduit, observations, date_debut, date_fin, nomProduit, nomCategorie = listeDonnees[0]

        date_debut_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_debut), "%d/%m/%Y")
        heure_debut_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_debut), "%Hh%M")
        texte_debut = _(u"%s à %s") % (date_debut_temp, heure_debut_temp)

        if date_fin != None :
            date_fin_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_fin), "%d/%m/%Y")
            heure_fin_temp = datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_fin), "%Hh%M")
            texte_fin = _(u"%s à %s") % (date_fin_temp, heure_fin_temp)
        else :
            texte_fin = _(u"Non définie")

        if len(observations) > 0 :
            texte_observations = _(u"<BR>Notes : %s") % observations
        else :
            texte_observations = ""

        texte = _(u"""
        Produit : <b>%s</b><BR>
        Catégorie : %s <BR>
        <BR>
        Début de location : %s <BR>
        Fin de location : %s <BR>
        %s
        """) % (nomProduit, nomCategorie, texte_debut, texte_fin, texte_observations)
        self.ctrl_attribution.SetPage(texte)

    def GetIDlocation(self):
        return self.IDlocation

    def Validation(self):
        return True


class CTRL_Statut(wx.Choicebook):
    """ Choicebook Statut """
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent, id=-1)
        self.parent = parent
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici le statut de la demande")))

        self.listePanels = [
            ("attente", _(u"En attente"), PAGE_Statut_attente(self)),
            ("refusee", _(u"Demande refusée"), PAGE_Statut_refusee(self)),
            #("attribuee", _(u"Demande satisfaite"), PAGE_Statut_attribuee(self)),
        ]

        for code, label, ctrl in self.listePanels:
            self.AddPage(ctrl, label)

        # Sélection par défaut
        self.SetSelection(0)

    def GetPageByCode(self, code=""):
        index = 0
        for codeTemp, label, ctrl in self.listePanels:
            if code == codeTemp:
                return ctrl
            index += 1
        return None

    def SetPageByCode(self, code=""):
        index = 0
        for codeTemp, label, ctrl in self.listePanels:
            if code == codeTemp:
                self.SetSelection(index)
            index += 1

    def GetPageActive(self):
        return self.listePanels[self.GetSelection()][2]

    def GetCodePageActive(self):
        return self.listePanels[self.GetSelection()][0]

    def Validation(self):
        ctrl = self.listePanels[self.GetSelection()][2]
        return ctrl.Validation()



# -----------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDdemande=None, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDdemande = IDdemande
        self.listeInitialeFiltres = []

        if self.IDdemande == None :
            self.SetTitle(_(u"Saisie d'une demande"))
        else :
            self.SetTitle(_(u"Modification d'une demande"))

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_loueur = wx.StaticText(self, -1, _(u"Loueur :"))
        self.ctrl_loueur = CTRL_Loueur(self)
        self.ctrl_loueur.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial'))
        self.bouton_loueur = wx.Button(self, -1, _(u"Sélectionner"))

        self.label_date_demande = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date_demande = CTRL_Saisie_date.Date2(self)
        self.ctrl_heure_demande = CTRL_Saisie_heure.Heure(self)

        self.label_observations = wx.StaticText(self, -1, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Notebook
        self.notebook = Notebook(self, IDdemande=IDdemande)

        # Statut
        self.staticbox_statut_staticbox = wx.StaticBox(self, -1, _(u"Statut"))
        self.ctrl_statut = CTRL_Statut(self)
        self.ctrl_statut.SetMinSize((50, 100))

        # Attribution
        self.ctrl_attribution = CTRL_Attribution(self)
        self.ctrl_attribution.SetMinSize((50, 50))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonLoueur, self.bouton_loueur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init contrôles
        maintenant = datetime.datetime.now()
        self.ctrl_date_demande.SetDate(datetime.datetime.strftime(maintenant, "%Y-%m-%d"))
        self.ctrl_heure_demande.SetHeure(datetime.datetime.strftime(maintenant, "%H:%M"))

        if IDfamille != None :
            self.ctrl_loueur.SetIDfamille(IDfamille)
            self.bouton_loueur.Show(False)

        self.Importation()
        self.notebook.GetPage("questionnaire").ctrl_questionnaire.MAJ()

    def __set_properties(self):
        self.ctrl_loueur.SetToolTip(wx.ToolTip(_(u"Nom du loueur")))
        self.ctrl_date_demande.SetToolTip(wx.ToolTip(_(u"Date de la demande")))
        self.ctrl_heure_demande.SetToolTip(wx.ToolTip(_(u"Heure de la demande")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations éventuelles")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux outils")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        # Date
        grid_sizer_generalites.Add(self.label_date_demande, 0, wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_date = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_date.Add(self.ctrl_date_demande, 0, wx.EXPAND, 0)
        grid_sizer_date.Add(self.ctrl_heure_demande, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_date, 1, wx.EXPAND, 0)

        # Loueur
        grid_sizer_generalites.Add(self.label_loueur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_loueur = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_loueur.Add(self.ctrl_loueur, 0, wx.EXPAND, 0)
        grid_sizer_loueur.Add(self.bouton_loueur, 0, 0, 0)
        grid_sizer_loueur.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_loueur, 1, wx.EXPAND, 0)

        # Observations
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(2)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_generalites, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Notebook
        grid_sizer_base.Add(self.notebook, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Statut
        staticbox_statut = wx.StaticBoxSizer(self.staticbox_statut_staticbox, wx.VERTICAL)
        staticbox_statut.Add(self.ctrl_statut, 1, wx.ALL|wx.EXPAND, 10)
        staticbox_statut.Add(self.ctrl_attribution, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_statut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonLoueur(self, event):
        from Dlg import DLG_Selection_famille
        dlg = DLG_Selection_famille.Dialog(self, IDfamille=self.ctrl_loueur.GetIDfamille())
        if dlg.ShowModal() == wx.ID_OK:
            IDfamille = dlg.GetIDfamille()
            self.ctrl_loueur.SetIDfamille(IDfamille)
        dlg.Destroy()


    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Actualiser
        item = wx.MenuItem(menuPop, 10, _(u"Mesurer une distance"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Transport.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Mesurer_distance, id=10)

        # Contrôle
        if UTILS_Customize.GetValeur("referentiel", "url", None, ajouter_si_manquant=False) != None:
            item = wx.MenuItem(menuPop, 20, _(u"Contrôle référentiel"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Personnes.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Controle_referentiel, id=20)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Mesurer_distance(self, event):
        # Recherche la destination
        categories = self.notebook.GetPage("criteres").ctrl_categories.listeDonnees
        produits = self.notebook.GetPage("criteres").ctrl_produits.listeDonnees

        # Si aucune catégorie sélectionnée
        if len(categories) == 0 and len(produits) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner renseigner une catégorie ou un produit dans les critères !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Si une seule catégorie sélectionnée
        if len(categories) == 1 :
            IDcategorie = categories[0][0]
        else :
            IDcategorie = None

        # Si un seul produit sélectionné
        if len(produits) == 1 :
            IDproduit = produits[0][0]
        else :
            IDproduit = None

        if len(categories) > 1 or len(produits) > 1 :
            liste_donnees = []
            liste_labels = []
            for donnees in categories :
                liste_donnees.append(("categories", donnees[0], donnees))
                liste_labels.append(u"%s (categorie de produits)" % donnees[1])
            for donnees in produits :
                liste_donnees.append(("produits", donnees[0], donnees))
                liste_labels.append(u"%s (produit)" % donnees[1])

            dlg = wx.SingleChoiceDialog(self, _(u"Sélectionnez la donnée qui vous intéresse :"), _(u"Sélection d'une donnée"), liste_labels, wx.CHOICEDLG_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
                donnees = liste_donnees[dlg.GetSelection()]
                if donnees[0] == "categories" :
                    IDcategorie = donnees[1]
                if donnees[0] == "produits" :
                    IDproduit = donnees[1]
                    IDcategorie = donnees[2][2]
            else :
                dlg.Destroy()
                return False

        # DLG Mesure de la distance
        from Dlg import DLG_Mesure_distance
        dictParametres = {
            "IDfamille" : self.ctrl_loueur.GetIDfamille(),
            "IDcategorie": IDcategorie,
            "IDproduit": IDproduit,
        }
        dlg = DLG_Mesure_distance.Dialog(self, dictParametres=dictParametres)
        dlg.ShowModal()
        dlg.Destroy()

    def Controle_referentiel(self, event):
        from Dlg import DLG_Controle_referentiel
        dictParametres = {
            "IDfamille" : self.ctrl_loueur.GetIDfamille(),
        }
        dlg = DLG_Controle_referentiel.Dialog(self, dictParametres=dictParametres)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonOk(self, event):
        # Date et heure de la demande
        date_demande = self.ctrl_date_demande.GetDate()
        if date_demande == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date pour cette demande !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_demande.SetFocus()
            return

        heure_demande = self.ctrl_heure_demande.GetHeure()
        if heure_demande == None or self.ctrl_heure_demande.Validation() == False:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure pour cette demande !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_demande.SetFocus()
            return

        date_demande = datetime.datetime(year=date_demande.year, month=date_demande.month, day=date_demande.day, hour=int(heure_demande[:2]), minute=int(heure_demande[3:]))

        # Loueur
        IDfamille = self.ctrl_loueur.GetIDfamille()
        if IDfamille == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un loueur pour cette demande !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Observations
        observations = self.ctrl_observations.GetValue()

        # Critères
        categories = UTILS_Texte.ConvertListeToStr(self.notebook.GetPage("criteres").ctrl_categories.GetListeCategories())
        produits = UTILS_Texte.ConvertListeToStr(self.notebook.GetPage("criteres").ctrl_produits.GetListeProduits())

        # Statut
        statut = self.ctrl_statut.GetCodePageActive()
        motif_refus = self.ctrl_statut.GetPageByCode("refusee").ctrl_motif.GetValue()
        IDlocation = self.ctrl_attribution.GetIDlocation()# self.ctrl_statut.GetPageByCode("attribuee").GetIDlocation()
        if IDlocation != None :
            statut = "attribuee"

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
            ("date", date_demande),
            ("IDfamille", IDfamille),
            ("observations", observations),
            ("categories", categories),
            ("produits", produits),
            ("statut", statut),
            ("motif_refus", motif_refus),
            ("IDlocation", IDlocation),
            ]

        if self.IDdemande == None :
            self.IDdemande = DB.ReqInsert("locations_demandes", listeDonnees)
        else:
            DB.ReqMAJ("locations_demandes", listeDonnees, "IDdemande", self.IDdemande)

        # Sauvegarde des filtres
        listeID = []
        for dictFiltre in self.notebook.GetPage("criteres").ctrl_filtres.GetDonnees() :
            listeID.append(dictFiltre["IDfiltre"])
            listeDonnees = [
                ("IDquestion", dictFiltre["IDquestion"]),
                ("categorie", "location_demande"),
                ("choix", dictFiltre["choix"]),
                ("criteres", dictFiltre["criteres"]),
                ("IDdonnee", self.IDdemande),
                ]

            # Sauvegarde dans DB
            if dictFiltre["IDfiltre"] == None :
                IDfiltre = DB.ReqInsert("questionnaire_filtres", listeDonnees)
            else :
                DB.ReqMAJ("questionnaire_filtres", listeDonnees, "IDfiltre", dictFiltre["IDfiltre"])

        for dictInitialFiltre in self.listeInitialeFiltres :
            if dictInitialFiltre["IDfiltre"] not in listeID :
                DB.ReqDEL("questionnaire_filtres", "IDfiltre", dictInitialFiltre["IDfiltre"])

        # Sauvegarde du questionnaire
        self.notebook.GetPage("questionnaire").ctrl_questionnaire.Sauvegarde(DB=DB, IDdonnee=self.IDdemande)

        # Fermeture de la base
        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDdemande(self):
        return self.IDdemande

    def Importation(self):
        """ Importation des données """
        if self.IDdemande != None :
            DB = GestionDB.DB()
            req = """SELECT date, IDfamille, observations, categories, produits, statut, motif_refus, IDlocation
            FROM locations_demandes WHERE IDdemande=%d;""" % self.IDdemande
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            date, IDfamille, observations, categories, produits, statut, motif_refus, IDlocation = listeDonnees[0]

            req = """SELECT IDfiltre, IDquestion, categorie, choix, criteres FROM questionnaire_filtres WHERE categorie='location_demande' AND IDdonnee=%d;""" % self.IDdemande
            DB.ExecuterReq(req)
            listeFiltres = DB.ResultatReq()
            DB.Close()

        else :
            date = None
            IDfamille = None
            observations = ""
            categories = ""
            produits = ""
            statut = "attente"
            motif_refus = ""
            IDlocation = None
            listeFiltres = []

        # Généralités
        if date != None :
            self.ctrl_date_demande.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date), "%Y-%m-%d"))
            self.ctrl_heure_demande.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date), "%H:%M"))

        if IDfamille != None :
            self.ctrl_loueur.SetIDfamille(IDfamille)

        if observations != None :
            self.ctrl_observations.SetValue(observations)

        # Critères
        self.notebook.GetPage("criteres").ctrl_categories.SetListeCategories(UTILS_Texte.ConvertStrToListe(categories))
        self.notebook.GetPage("criteres").ctrl_produits.SetListeProduits(UTILS_Texte.ConvertStrToListe(produits))

        # Filtres
        listeDonnees = []
        for IDfiltre, IDquestion, categorie, choix, criteres in listeFiltres :
            listeDonnees.append( {"IDfiltre":IDfiltre, "IDquestion":IDquestion, "choix":choix, "criteres":criteres} )
        self.notebook.GetPage("criteres").ctrl_filtres.SetDonnees(listeDonnees)
        self.listeInitialeFiltres = copy.deepcopy(listeDonnees)

        # Statut
        self.ctrl_statut.SetPageByCode(statut)
        if motif_refus != None :
            self.ctrl_statut.GetPageByCode("refusee").ctrl_motif.SetValue(motif_refus)
            self.ctrl_statut.Show(True)
            self.ctrl_attribution.Show(False)
        if IDlocation != None :
            #self.ctrl_statut.GetPageByCode("attribuee").SetIDlocation(IDlocation)
            #self.ctrl_statut.GetChoiceCtrl().Enable(False)
            self.SetAttribution(IDlocation)

    def SetAttribution(self, IDlocation=None):
        self.ctrl_statut.Show(False)
        self.ctrl_attribution.Show(True)
        self.ctrl_attribution.SetIDlocation(IDlocation)

    def Attribution(self, IDproduit=None):
        # Création d'une location
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDfamille=self.ctrl_loueur.GetIDfamille(), IDproduit=IDproduit)
        IDlocation = None
        if dlg.ShowModal() == wx.ID_OK:
            IDlocation = dlg.GetIDlocation()
            self.SetAttribution(IDlocation)
        dlg.Destroy()
        if IDlocation != None :
            self.OnBoutonOk(None)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDdemande=3610, IDfamille=4560)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


