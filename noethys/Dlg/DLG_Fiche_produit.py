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
import wx.html as html
import datetime
import GestionDB
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Questionnaires
from Utils import UTILS_Locations
from Utils import UTILS_Dates
from Ctrl import CTRL_Logo
from Ol import OL_Locations
from Ctrl import CTRL_Timeline
from Utils import UTILS_TL_db as TL
from Utils import UTILS_Titulaires



class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte=""):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SIMPLE_BORDER | wx.html.HW_NO_SELECTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetPage(texte)

class Page_Locations(wx.Panel):
    def __init__(self, parent, IDproduit=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDproduit = IDproduit

        self.ctrl_locations = OL_Locations.ListView(self, IDproduit=self.IDproduit, id=-1, name="OL_locations", style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.ctrl_locations.SetMinSize((500, 200))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Properties
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une location")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la location sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la location sélectionnée dans la liste")))

        # Bind
        self.Bind(wx.EVT_BUTTON, self.ctrl_locations.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_locations.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_locations.Supprimer, self.bouton_supprimer)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_locations, 0, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def MAJ(self):
        self.ctrl_locations.MAJ()

    def Validation(self):
        return True




class Timeline(TL.TimelinePerso):
    def __init__(self, IDproduit=None):
        self.IDproduit = IDproduit
        TL.TimelinePerso.__init__(self)

    def _load_data(self):
        """ Importation des données """
        self.preferred_period = None
        self.categories = []
        self.events = []

        # Période préférée
        dateDuJour = datetime.datetime.today()
        dateDebut = dateDuJour - datetime.timedelta(6)
        dateFin = dateDuJour + datetime.timedelta(1)
        self.preferred_period = TL.TimePeriod(dateDebut, dateFin)

        # Récupération des events LOCATIONS
        DB = GestionDB.DB()
        req = """SELECT IDlocation, IDfamille, date_debut, date_fin, quantite
        FROM locations
        WHERE IDproduit=%d;""" % self.IDproduit
        DB.ExecuterReq(req)
        listeLocations = DB.ResultatReq()
        DB.Close()

        listeIDfamille = []
        for IDlocation, IDfamille, date_debut, date_fin, quantite in listeLocations:
            listeIDfamille.append(IDfamille)

        dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille)

        categorie = TL.Category(_(u"Location"), (156, 205, 255), True)
        for IDlocation, IDfamille, date_debut, date_fin, quantite in listeLocations :
            date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
            if date_fin == None :
                date_fin = datetime.datetime(2999, 1, 1)

            if quantite == None :
                quantite = 1

            if IDfamille in dictTitulaires :
                nomTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
            else :
                nomTitulaires = _(u"Famille inconnue")

            texte = u"%s - Quantité : %d" % (nomTitulaires, quantite)
            date_debut_str = datetime.datetime.strftime(date_debut, "%d/%m/%Y-%Hh%M")
            if date_fin.year == 2999:
                date_fin_str = _(u"Illimité")
            else:
                date_fin_str = datetime.datetime.strftime(date_fin, "%d/%m/%Y-%Hh%M")

            description = _(u"Loueur : %s\nQuantité : %d\nDébut : %s\nFin : %s") % (nomTitulaires, quantite, date_debut_str, date_fin_str)
            icon = None

            evt = TL.Event(date_debut, date_fin, texte, categorie)
            if description != None: evt.set_data("description", description)
            if icon != None: evt.set_data("icon", icon)
            self.events.append(evt)


        # Récupération des events STOCK DISPONIBLE
        dictPeriodes = UTILS_Locations.GetStockDisponible(IDproduit=self.IDproduit, date_debut=None, date_fin=None)

        categorie_disponible = TL.Category(_(u"Stock disponible"), (233, 255, 156), True)
        categorie_loue = TL.Category(_(u"Quantité louée"), (204, 227, 250), True)
        for periode, valeurs in dictPeriodes.items():
            date_debut = periode[0]

            evt = TL.Event(date_debut, date_debut, str(valeurs["loue"]), categorie_loue)
            self.events.append(evt)

            evt = TL.Event(date_debut, date_debut, str(valeurs["disponible"]), categorie_disponible)
            self.events.append(evt)



class Page_Chronologie(wx.Panel):
    def __init__(self, parent, IDproduit=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDproduit = IDproduit

        # Timeline
        self.ctrl_timeline = CTRL_Timeline.CTRL(self,
                            afficheSidebar=False, modele=Timeline(IDproduit),
                            afficheToolbar=True, positionToolbar="bas",
                            lectureSeule=True,
                            )
        self.ctrl_timeline.SetPositionVerticale(35)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_timeline, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def MAJ(self):
        if self.GetGrandParent().IsDirty():
            self.ctrl_timeline.MAJ(reimporterdata=True)

    def Validation(self):
        return True


# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Onglets(wx.Notebook):
    def __init__(self, parent, IDlocation=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}
        self.IDlocation = IDlocation

        self.listePages = [
            {"code": "locations", "ctrl": Page_Locations(self, self.IDlocation), "label": _(u"Locations"), "image": "Location.png"},
            {"code": "chronologie", "ctrl": Page_Chronologie(self, self.IDlocation), "label": _(u"Chronologie"), "image": "Timeline.png"},
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
        wx.CallLater(1, page.MAJ)
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
            for key, valeur in dictPage["ctrl"].GetDonnees().items() :
                dictDonnees[key] = valeur
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        for dictPage in self.listePages :
            dictPage["ctrl"].SetDonnees(dictDonnees)

    def SetTexteOnglet(self, code, texte=""):
        index = 0
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                self.SetPageText(index, texte)
            index += 1




class Dialog(wx.Dialog):
    def __init__(self, parent, IDproduit=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDproduit = IDproduit
        self.logo = None
        self.SetTitle(_(u"Fiche produit"))

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))
        self.ctrl_produit = MyHtml(self)

        # Logo
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Image"))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=(110, 110) )
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))

        # Onglets
        self.ctrl_onglets = CTRL_Onglets(self, self.IDproduit)
        self.ctrl_onglets.SetMinSize((750, 400))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.Visualiser, self.bouton_visualiser)

        # Init
        if self.IDproduit != None :
            self.Importation()

        self.ctrl_onglets.GetPageAvecCode("locations").MAJ()
        self.ctrl_onglets.GetPageAvecCode("chronologie").ctrl_timeline.MAJ()

    def __set_properties(self):
        self.ctrl_logo.SetToolTip(wx.ToolTip(_(u"Image du produit")))
        self.bouton_visualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser l'image actuelle en taille réelle")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer la fiche produit")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        staticbox_generalites.Add(self.ctrl_produit, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_generalites, 1, wx.EXPAND, 10)

        # Logo
        staticbox_logo = wx.StaticBoxSizer(self.staticbox_logo_staticbox, wx.VERTICAL)
        grid_sizer_logo = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_logo_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_logo.Add(self.ctrl_logo, 0, wx.EXPAND, 0)
        grid_sizer_logo_boutons.Add(self.bouton_visualiser, 0, 0, 0)
        grid_sizer_logo.Add(grid_sizer_logo_boutons, 1, wx.EXPAND, 0)
        grid_sizer_logo.AddGrowableRow(0)
        grid_sizer_logo.AddGrowableCol(0)
        staticbox_logo.Add(grid_sizer_logo, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_logo, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Locations
        grid_sizer_base.Add(self.ctrl_onglets, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Produits")

    def GetIDproduit(self):
        return self.IDproduit

    def Importation(self):
        """ Importation des données """
        DB = GestionDB.DB()
        req = """SELECT produits.nom, produits.observations, produits.image, produits.IDcategorie, produits.quantite,
        produits_categories.nom
        FROM produits 
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDproduit=%d;""" % self.IDproduit
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        nomProduit, observations, image, IDcategorie, quantite, nomCategorie = listeDonnees[0]

        if len(observations) > 0 :
            texte_observations = _(u"<BR>Notes : %s") % observations
        else :
            texte_observations = ""

        if quantite == None :
            quantite = 1

        # Questionnaire
        questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="produit")
        liste_questions_temp = []
        for dictQuestion in questionnaires.GetDonnees(ID=self.IDproduit):
            liste_questions_temp.append(u"%s : %s" % (dictQuestion["label"], dictQuestion["reponse"]))

        # Caractéristiques
        texte = _(u"""
        <FONT SIZE=5><B>%s</B><BR></FONT>
        <BR>
        Catégorie : %s <BR>
        Stock initial : %d <BR>
        %s
        %s
        """) % (nomProduit, nomCategorie, quantite, texte_observations, "<BR>".join(liste_questions_temp))
        self.ctrl_produit.SetPage(texte)

        # Logo
        if image != None :
            self.ctrl_logo.ChargeFromBuffer(image)

    def IsDirty(self):
        return self.ctrl_onglets.GetPageAvecCode("locations").ctrl_locations.dirty



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDproduit=2)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


