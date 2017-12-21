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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Questionnaire
from Ctrl import CTRL_Logo
from Ctrl import CTRL_Saisie_euros
import GestionDB
from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES
from Dlg.DLG_Ouvertures import Track_tarif
from Ol import OL_Produits_tarifs



class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()
        if len(self.dictDonnees) > 0:
            self.SetSelection(0)

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        # Importation des catégories
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM produits_categories
        ORDER BY nom
        ;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        self.dictCategories = {}
        index = 0
        for IDcategorie, nom in listeCategories:
            dictTemp = {"IDcategorie": IDcategorie, "nom": nom}
            self.dictDonnees[index] = dictTemp
            self.dictCategories[IDcategorie] = dictTemp
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["IDcategorie"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["IDcategorie"]



# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent, IDproduit=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}
        self.IDproduit = IDproduit

        self.listePages = [
            {"code": "questionnaire", "ctrl": Page_Questionnaire(self, self.IDproduit), "label": _(u"Questionnaire"), "image": "Questionnaire.png"},
            {"code": "stock", "ctrl": Page_Stock(self, self.IDproduit), "label": _(u"Stock"), "image": "Stock.png"},
            {"code": "tarification", "ctrl": Page_Tarification(self, self.IDproduit), "label": _(u"Tarification"), "image": "Euro.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        if event.GetOldSelection() == -1: return
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        self.Freeze()
        wx.CallLater(1, page.Refresh)
        self.Thaw()
        event.Skip()

    def Validation(self):
        for dictPage in self.listePages :
            if dictPage["ctrl"].Validation() == False :
                return False
        return True

    def GetDonnees(self):
        dictDonnees = {}
        for dictPage in self.listePages :
            for key, valeur in dictPage["ctrl"].GetDonnees().iteritems() :
                dictDonnees[key] = valeur
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        for dictPage in self.listePages :
            dictPage["ctrl"].SetDonnees(dictDonnees)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------


class Page_Questionnaire(wx.Panel):
    def __init__(self, parent, IDproduit=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDproduit = IDproduit
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="produit", IDdonnee=self.IDproduit)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_questionnaire, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def Validation(self):
        return True

    def GetDonnees(self):
        return {}

    def SetDonnees(self, dictDonnees={}):
        pass



class Page_Stock(wx.Panel):
    def __init__(self, parent, IDproduit=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDproduit = IDproduit

        self.label_quantite = wx.StaticText(self, -1, _(u"Quantité fixe :"))
        self.ctrl_quantite = wx.SpinCtrl(self, -1, min=0, max=99999)
        self.ctrl_quantite.SetToolTip(wx.ToolTip(_(u"Saisissez une quantité")))
        self.ctrl_quantite.SetValue(1)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.label_quantite, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_quantite, 1, wx.EXPAND, 0)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def Validation(self):
        return True

    def GetDonnees(self):
        dictDonnees = {"quantite" : int(self.ctrl_quantite.GetValue())}
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        if dictDonnees.has_key("quantite"):
            if dictDonnees["quantite"] != None :
                self.ctrl_quantite.SetValue(dictDonnees["quantite"])



class Page_Tarification(wx.Panel):
    def __init__(self, parent, IDproduit=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDproduit = IDproduit

        # Aucune
        self.radio_tarification_aucune = wx.RadioButton(self, -1, _(u"Aucune"), style=wx.RB_GROUP)

        # Tarification simple
        self.radio_tarification_montant = wx.RadioButton(self, -1, _(u"Tarification simple :"))
        self.label_montant = wx.StaticText(self, -1, _(u"Montant fixe :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)

        # Tarification avancée
        self.radio_tarification_tarif = wx.RadioButton(self, -1, _(u"Tarification avancée :"))
        self.ctrl_tarifs = OL_Produits_tarifs.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_tarifs.SetMinSize((50, 50))
        self.ctrl_tarifs.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Properties
        self.radio_tarification_aucune.SetToolTip(wx.ToolTip(_(u"Aucune tarification spécifique pour ce produit")))
        self.radio_tarification_montant.SetToolTip(wx.ToolTip(_(u"Un montant fixe est associé à ce produit")))
        self.radio_tarification_tarif.SetToolTip(wx.ToolTip(_(u"Un ou plusieurs tarifs avancés sont associés à ce produit")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant fixe pour ce produit")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un tarif")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le tarif sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le tarif sélectionné dans la liste")))

        # Bind
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTarification, self.radio_tarification_aucune)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTarification, self.radio_tarification_montant)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTarification, self.radio_tarification_tarif)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Supprimer, self.bouton_supprimer)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)

        # Aucune tarification
        grid_sizer_base.Add(self.radio_tarification_aucune, 0, wx.BOTTOM, 5)

        # Tarification simple
        grid_sizer_base.Add(self.radio_tarification_montant, 0, 0, 0)

        grid_sizer_tarification_simple = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_tarification_simple.Add( (12, 12), 0, 0, 0)
        grid_sizer_tarification_simple.Add(self.label_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarification_simple.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_tarification_simple, 0, 0, 0)

        # Tarification avancée
        grid_sizer_base.Add(self.radio_tarification_tarif, 0, 0, 0)

        grid_sizer_tarification_avancee = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_tarification_avancee.Add( (12, 12), 0, 0, 0)
        grid_sizer_tarification_avancee.Add(self.ctrl_tarifs, 0, wx.EXPAND, 0)
        grid_sizer_tarification_avancee_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_tarification_avancee_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_tarification_avancee_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_tarification_avancee_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_tarification_avancee.Add(grid_sizer_tarification_avancee_boutons, 0, 0, 0)
        grid_sizer_tarification_avancee.AddGrowableCol(1)
        grid_sizer_tarification_avancee.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_tarification_avancee, 0, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(4)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.OnRadioTarification()

    def OnRadioTarification(self, event=None):
        self.label_montant.Enable(self.radio_tarification_montant.GetValue())
        self.ctrl_montant.Enable(self.radio_tarification_montant.GetValue())
        self.ctrl_tarifs.Activation(self.radio_tarification_tarif.GetValue())
        self.bouton_ajouter.Enable(self.radio_tarification_tarif.GetValue())
        self.bouton_modifier.Enable(self.radio_tarification_tarif.GetValue())
        self.bouton_supprimer.Enable(self.radio_tarification_tarif.GetValue())

    def Validation(self):
        # Tarification simple
        montant = None
        if self.radio_tarification_montant.GetValue() == True :
            montant = self.ctrl_montant.GetMontant()

        # Tarification avancée
        liste_tarifs = []
        if self.radio_tarification_tarif.GetValue() == True :
            liste_tarifs = self.ctrl_tarifs.GetTracksTarifs()
            if len(liste_tarifs) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins un tarif !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def GetDonnees(self):
        montant = None
        if self.radio_tarification_montant.GetValue() == True :
            montant = self.ctrl_montant.GetMontant()

        tarifs = []
        if self.radio_tarification_tarif.GetValue() == True :
            tarifs = self.ctrl_tarifs.GetTracksTarifs()

        dictDonnees = {"montant" : montant, "tarifs" : tarifs}
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        if dictDonnees.has_key("montant") and dictDonnees["montant"] != None :
            self.ctrl_montant.SetMontant(dictDonnees["montant"])
            self.radio_tarification_montant.SetValue(True)
        if dictDonnees.has_key("tarifs") and len(dictDonnees["tarifs"]) > 0 :
            self.ctrl_tarifs.SetTarifs(dictDonnees["tarifs"])
            self.radio_tarification_tarif.SetValue(True)
        self.OnRadioTarification()



class Dialog(wx.Dialog):
    def __init__(self, parent, IDproduit=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDproduit = IDproduit
        self.logo = None

        if self.IDproduit == None :
            self.SetTitle(_(u"Saisie d'un produit"))
        else :
            self.SetTitle(_(u"Modification d'un produit"))

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self)
        self.bouton_categories = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.label_observations = wx.StaticText(self, -1, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Logo
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Image"))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=(110, 110) )
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))

        # Paramètres
        self.ctrl_parametres = CTRL_Parametres(self, self.IDproduit)
        self.ctrl_parametres.SetMinSize((650, 270))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.Ajouter, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.MAJ, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.Visualiser, self.bouton_visualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)

        self.dict_donnees_initiales = {"tarifs": [], "tarifs_lignes": []}
        if self.IDproduit != None :
            self.Importation()
        else :
            self.ImportationDernierProduit()

        self.ctrl_parametres.GetPageAvecCode("questionnaire").ctrl_questionnaire.MAJ()
        self.ctrl_nom.SetFocus()

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du produit")))
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez la catégorie associée au produit")))
        self.bouton_categories.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des catégories de produits")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations éventuelles")))
        self.ctrl_logo.SetToolTip(wx.ToolTip(_(u"Image du produit")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter ou modifier l'image")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'image actuelle")))
        self.bouton_visualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser l'image actuelle en taille réelle")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_categorie = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categories, 0, 0, 0)
        grid_sizer_categorie.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_categorie, 1, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(2)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_generalites, 1, wx.EXPAND, 10)

        # Logo
        staticbox_logo = wx.StaticBoxSizer(self.staticbox_logo_staticbox, wx.VERTICAL)
        grid_sizer_logo = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_logo_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_logo.Add(self.ctrl_logo, 0, wx.EXPAND, 0)
        grid_sizer_logo_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_logo_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_logo_boutons.Add(self.bouton_visualiser, 0, 0, 0)
        grid_sizer_logo.Add(grid_sizer_logo_boutons, 1, wx.EXPAND, 0)
        grid_sizer_logo.AddGrowableRow(0)
        grid_sizer_logo.AddGrowableCol(0)
        staticbox_logo.Add(grid_sizer_logo, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_logo, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Paramètres
        grid_sizer_base.Add(self.ctrl_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonCategories(self, event):
        IDcategorie = self.ctrl_categorie.GetID()
        import DLG_Categories_produits
        dlg = DLG_Categories_produits.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_categorie.MAJ()
        self.ctrl_categorie.SetID(IDcategorie)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        observations = self.ctrl_observations.GetValue()
        IDcategorie = self.ctrl_categorie.GetID()

        if len(nom) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if IDcategorie == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie pour ce produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_categorie.SetFocus()
            return

        # Validation du notebook
        if self.ctrl_parametres.Validation() == False :
            return

        # Récupération des données
        dictParametres = self.ctrl_parametres.GetDonnees()

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
            ("nom", nom),
            ("IDcategorie", IDcategorie),
            ("observations", observations),
            ("quantite", dictParametres["quantite"]),
            ("montant", dictParametres["montant"]),
            ]

        if self.IDproduit == None :
            self.IDproduit = DB.ReqInsert("produits", listeDonnees)
        else:
            DB.ReqMAJ("produits", listeDonnees, "IDproduit", self.IDproduit)
        
        # Sauvegarde du logo
        if self.ctrl_logo.estModifie == True :
            bmp = self.ctrl_logo.GetBuffer() 
            if bmp != None :
                DB.MAJimage(table="produits", key="IDproduit", IDkey=self.IDproduit, blobImage=bmp, nomChampBlob="image")
            else:
                DB.ReqMAJ("produits", [("image", None),], "IDproduit", self.IDproduit)

        # Sauvegarde du ctrl_parametres
        self.ctrl_parametres.GetPageAvecCode("questionnaire").ctrl_questionnaire.Sauvegarde(DB=DB, IDdonnee=self.IDproduit)

        # Sauvegarde des tarifs
        tarifs = dictParametres["tarifs"]

        # Récupération du prochain IDtarif
        prochainIDtarif = DB.GetProchainID("tarifs")

        # Pour contrer bug sur table tarifs_lignes
        if DB.isNetwork == False:
            req = """SELECT max(IDligne) FROM tarifs_lignes;"""
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if listeTemp[0][0] == None:
                prochainIDligne = 1
            else:
                prochainIDligne = listeTemp[0][0] + 1

        # ------------- Evenements ---------------
        dict_suppressions = {
            "tarifs": {"champ_cle": "IDtarif", "listeID": []},
            "tarifs_lignes": {"champ_cle": "IDligne", "listeID": []},
        }

        dict_requetes = {
            "tarifs": {"ajout": [], "modification": []},
            "tarifs_lignes": {"ajout": [], "modification": []},
        }


        # ---------------- Tarifs --------------------
        for track_tarif in tarifs :
            dict_suppressions["tarifs"]["listeID"].append(track_tarif.IDtarif)

            # Ajout
            if track_tarif.IDtarif == None :
                track_tarif.MAJ({"IDproduit": self.IDproduit, "IDtarif" : int(prochainIDtarif)})
                prochainIDtarif += 1
                dict_requetes[track_tarif.nom_table]["ajout"].append(track_tarif)
                #print "ajouter", track_tarif, "avec ID", track_tarif.IDtarif

            # Modification
            else :
                if track_tarif.dirty == True:
                    dict_requetes[track_tarif.nom_table]["modification"].append(track_tarif)
                    #print "modifier", track_tarif

            # ---------------- Lignes --------------------
            for track_ligne in track_tarif.lignes :
                dict_suppressions["tarifs_lignes"]["listeID"].append(track_ligne.IDligne)

                # Ajout
                if track_ligne.IDligne == None:
                    track_ligne.MAJ({"IDtarif" : track_tarif.IDtarif})
                    if DB.isNetwork == False:
                        track_ligne.MAJ({"IDligne": int(prochainIDligne)})
                        prochainIDligne += 1
                    dict_requetes[track_ligne.nom_table]["ajout"].append(track_ligne)
                    #print "ajouter", track_ligne

                # Modification
                else:
                    if track_ligne.dirty == True:
                        track_ligne.MAJ({"IDtarif": track_tarif.IDtarif})
                        dict_requetes[track_ligne.nom_table]["modification"].append(track_ligne)
                        #print "modifier", track_ligne

        for nom_table in ("tarifs", "tarifs_lignes"):

            # Ajout
            if len(dict_requetes[nom_table]["ajout"]) > 0:
                listeDonnees = []
                for track in dict_requetes[nom_table]["ajout"]:
                    ligne = track.Get_variables_pour_db()
                    if DB.isNetwork == False and nom_table == "tarifs_lignes":
                        ligne.append(track.IDligne)
                    listeDonnees.append(ligne)

                liste_champs = track.Get_champs_pour_db()
                liste_interro = track.Get_interrogations_pour_db()
                if DB.isNetwork == False and nom_table == "tarifs_lignes":
                    liste_champs += ", IDligne"
                    liste_interro += ", ?"

                DB.Executermany("INSERT INTO %s (%s) VALUES (%s)" % (track.nom_table, liste_champs, liste_interro), listeDonnees, commit=False)

            # Modification
            if len(dict_requetes[nom_table]["modification"]) > 0:
                listeDonnees = []
                for track in dict_requetes[nom_table]["modification"]:
                    listeTemp = track.Get_variables_pour_db()
                    listeTemp.append(track.GetValeurCle())
                    listeDonnees.append(listeTemp)
                DB.Executermany("UPDATE %s SET %s WHERE %s=?" % (track.nom_table, track.Get_interrogations_et_variables_pour_db(), track.champ_cle), listeDonnees, commit=False)

        # Recherche les suppressions à effectuer
        for nom_table, dictTemp in dict_suppressions.iteritems():
            liste_suppressions = []
            for ID in self.dict_donnees_initiales[nom_table]:
                if ID not in dictTemp["listeID"]:
                    liste_suppressions.append(ID)
                    # print "Suppression ID", ID, "de la table", nom_table
            if len(liste_suppressions) > 0:
                if len(liste_suppressions) == 1:
                    condition = "(%d)" % liste_suppressions[0]
                else:
                    condition = str(tuple(liste_suppressions))
                DB.ExecuterReq("DELETE FROM %s WHERE %s IN %s" % (nom_table, dictTemp["champ_cle"], condition))

        DB.Commit()

        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDproduit(self):
        return self.IDproduit

    def Importation(self):
        """ Importation des données """
        DB = GestionDB.DB()
        req = """SELECT nom, observations, image, IDcategorie, quantite, montant
        FROM produits WHERE IDproduit=%d;""" % self.IDproduit
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            DB.Close()
            return
        nom, observations, image, IDcategorie, quantite, montant = listeDonnees[0]

        # Généralités
        self.ctrl_nom.SetValue(nom)
        self.ctrl_categorie.SetID(IDcategorie)
        self.ctrl_observations.SetValue(observations)

        # Importation des tarifs
        liste_tarifs = []

        req = """SELECT IDtarif, IDactivite, date_debut, date_fin, methode, type, categories_tarifs, groupes, etiquettes, cotisations, 
        caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, 
        IDtype_quotient, label_prestation, IDproduit
        FROM tarifs WHERE IDproduit=%d;""" % self.IDproduit
        DB.ExecuterReq(req)
        listeDonneesTarifs = DB.ResultatReq()
        listeIDtarif = []
        for temp in listeDonneesTarifs:
            listeIDtarif.append(temp[0])
            self.dict_donnees_initiales["tarifs"].append(temp[0])

        # Importation des filtres de questionnaire
        if len(listeIDtarif) == 0:
            condition = "()"
        elif len(listeIDtarif) == 1:
            condition = "(%d)" % listeIDtarif[0]
        else:
            condition = str(tuple(listeIDtarif))

        req = """SELECT IDtarif, IDfiltre, IDquestion, categorie, choix, criteres FROM questionnaire_filtres WHERE IDtarif IN %s;""" % condition
        DB.ExecuterReq(req)
        listeDonneesFiltres = DB.ResultatReq()
        dictFiltres = {}
        for IDtarif, IDfiltre, IDquestion, categorie, choix, criteres in listeDonneesFiltres:
            if dictFiltres.has_key(IDtarif) == False:
                dictFiltres[IDtarif] = []
            dictTemp = {"IDfiltre": IDfiltre, "IDquestion": IDquestion, "categorie": categorie, "choix": choix, "criteres": criteres, "IDtarif": IDtarif}
            dictFiltres[IDtarif].append(dictTemp)
            self.dict_donnees_initiales["questionnaire_filtres"].append(IDfiltre)

        # Importation des lignes de tarifs
        req = """SELECT %s FROM tarifs_lignes WHERE IDtarif IN %s ORDER BY num_ligne;""" % (", ".join(CHAMPS_TABLE_LIGNES), condition)
        DB.ExecuterReq(req)
        listeDonneesLignes = DB.ResultatReq()
        dictLignes = {}
        for ligne in listeDonneesLignes:
            index = 0
            dictLigne = {}
            for valeur in ligne:
                dictLigne[CHAMPS_TABLE_LIGNES[index]] = valeur
                index += 1
            if dictLignes.has_key(dictLigne["IDtarif"]) == False:
                dictLignes[dictLigne["IDtarif"]] = []
            dictLignes[dictLigne["IDtarif"]].append(dictLigne)
            self.dict_donnees_initiales["tarifs_lignes"].append(dictLigne["IDligne"])

        # Mémorisation des tarifs
        for IDtarif, IDactivite, date_debut, date_fin, methode, type, categories_tarifs, groupes, etiquettes, cotisations, caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, IDtype_quotient, label_prestation, IDproduit in listeDonneesTarifs:

            # Récupération des filtres du tarif
            if dictFiltres.has_key(IDtarif):
                liste_filtres = dictFiltres[IDtarif]
            else:
                liste_filtres = []

            # Récupération des lignes du tarif
            if dictLignes.has_key(IDtarif):
                liste_lignes = dictLignes[IDtarif]
            else:
                liste_lignes = []

            dictTarif = {
                "IDtarif": IDtarif, "IDactivite": IDactivite, "date_debut": date_debut, "date_fin": date_fin, "methode": methode, "type": type, "categories_tarifs": categories_tarifs,
                "groupes": groupes, "etiquettes": etiquettes, "cotisations": cotisations, "caisses": caisses, "description": description,
                "jours_scolaires": jours_scolaires, "jours_vacances": jours_vacances, "observations": observations, "tva": tva,
                "code_compta": code_compta, "IDtype_quotient": IDtype_quotient, "label_prestation": label_prestation, "IDproduit": IDproduit,
                "filtres": liste_filtres, "lignes": liste_lignes,
            }

            liste_tarifs.append(Track_tarif(dictTarif))

        DB.Close()

        # Paramètres
        dictDonnees = {"quantite" : quantite, "montant" : montant, "tarifs" : liste_tarifs}
        self.ctrl_parametres.SetDonnees(dictDonnees)

        # Logo
        if image != None :
            self.ctrl_logo.ChargeFromBuffer(image)

    def ImportationDernierProduit(self):
        DB = GestionDB.DB()
        req = """SELECT IDproduit, IDcategorie
        FROM produits
        ORDER BY IDproduit DESC
        LIMIT 1
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDproduit, IDcategorie = listeDonnees[0]
        self.ctrl_categorie.SetID(IDcategorie)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDproduit=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


