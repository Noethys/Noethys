#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
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
from Ol import OL_Archivage
from dateutil import relativedelta

CHOIX_DELAIS = [
    ("mois", 1, _(u"1 mois")),
    ("mois", 2, _(u"2 mois")),
    ("mois", 3, _(u"3 mois")),
    ("mois", 6, _(u"6 mois")),
    ("annees", 1, _(u"1 an")),
    ("annees", 2, _(u"2 ans")),
    ("annees", 3, _(u"3 ans")),
    ("annees", 4, _(u"4 ans")),
    ("annees", 5, _(u"5 ans")),
    ("annees", 6, _(u"6 ans")),
    ]



class Page(wx.Panel):
    def __init__(self, parent, mode="familles"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.mode = mode

        if self.mode == "familles" :
            texte1 = _(u"Toutes les familles")
            texte2 = _(u"Les familles inactives depuis plus de")
            texte3 = _(u"Les familles actives depuis")
        else :
            texte1 = _(u"Tous les individus")
            texte2 = _(u"Les individus inactifs depuis plus de")
            texte3 = _(u"Les individus actifs depuis")

        self.radio_tous = wx.RadioButton(self, -1, texte1, style=wx.RB_GROUP)
        self.radio_sans_activite = wx.RadioButton(self, -1, texte2)
        self.ctrl_date_sans_activite = wx.Choice(self, -1, choices=[x[2] for x in CHOIX_DELAIS])
        self.ctrl_date_sans_activite.Select(5)
        self.radio_avec_activite = wx.RadioButton(self, -1, texte3)
        self.ctrl_date_avec_activite = wx.Choice(self, -1, choices=[x[2] for x in CHOIX_DELAIS])
        self.ctrl_date_avec_activite.Select(5)

        self.listviewAvecFooter = OL_Archivage.ListviewAvecFooter(self, kwargs={"mode": self.mode})
        self.listviewAvecFooter.SetMinSize((50, 300))
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Archivage.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)

        self.ctrl_recherche.bouton_filtrer.SetBackgroundColour(wx.WHITE)
        self.ctrl_recherche.bouton_cocher.SetBackgroundColour(wx.WHITE)

        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        # Properties
        self.bouton_ouvrir_fiche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la fiche famille correspondante")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelection, self.radio_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelection, self.radio_sans_activite)
        self.Bind(wx.EVT_CHOICE, self.OnRadioSelection, self.ctrl_date_sans_activite)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelection, self.radio_avec_activite)
        self.Bind(wx.EVT_CHOICE, self.OnRadioSelection, self.ctrl_date_avec_activite)

        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.OuvrirFicheFamille, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportExcel, self.bouton_excel)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_haut.Add(self.radio_tous, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.radio_sans_activite, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.ctrl_date_sans_activite, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.radio_avec_activite, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.ctrl_date_avec_activite, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_haut, 0, wx.EXPAND, 0)

        grid_sizer_base.Add( (10, 10), 1, wx.EXPAND, 0)

        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add((5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add((5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

        sizer_base.Add(grid_sizer_base, 1, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.OnRadioSelection()
        self.ctrl_listview.MAJ()

    def OnRadioSelection(self, event=None):
        date_jour = datetime.date.today()
        self.ctrl_date_sans_activite.Enable(self.radio_sans_activite.GetValue())
        self.ctrl_date_avec_activite.Enable(self.radio_avec_activite.GetValue())

        if self.radio_tous.GetValue() == True :
            filtre = None
        else :
            if self.radio_sans_activite.GetValue() == True :
                index = self.ctrl_date_sans_activite.GetSelection()
                type_filtre = "sans"

            if self.radio_avec_activite.GetValue() == True :
                index = self.ctrl_date_avec_activite.GetSelection()
                type_filtre = "avec"

            type_valeur, valeur, label = CHOIX_DELAIS[index]
            if type_valeur == "mois" :
                date_limite = date_jour - relativedelta.relativedelta(months=+valeur)
            if type_valeur == "annees":
                date_limite = date_jour - relativedelta.relativedelta(years=+valeur)
            filtre = (type_filtre, date_limite)

        self.ctrl_listview.SetFiltre(filtre)




class CTRL_Notebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}

        self.listePages = [
            {"code": "familles", "ctrl": Page(self, mode="familles"), "label": _(u"Familles"), "image": "Famille.png"},
            {"code": "individus", "ctrl": Page(self, mode="individus"), "label": _(u"Individus"), "image": "Personnes.png"},
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

    def GetPageActive(self):
        indexPage = self.GetSelection()
        page = self.GetPage(indexPage)
        return page

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
            for key, valeur in dictPage["ctrl"].GetDonnees().items() :
                dictDonnees[key] = valeur
        return dictDonnees




# --------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Sélectionnez le mode Familles ou Individus, cochez les lignes à traiter, puis cliquez sur le bouton Action souhaité. L'archivage permet de cacher les familles ou individus de certaines listes. L'effacement est une action non réversible qui supprime toutes les données personnelles.")
        titre = _(u"Archiver et effacer")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Archiver.png")

        # Liste des données
        self.staticbox_donnees = wx.StaticBox(self, -1, _(u"Liste des données"))
        self.ctrl_notebook = CTRL_Notebook(self)

        # Boutons actions
        self.staticbox_actions = wx.StaticBox(self, -1, _(u"Actions sur les lignes cochées"))
        self.bouton_archiver = CTRL_Bouton_image.CTRL(self, texte=_(u"Archiver"), cheminImage="Images/32x32/Archiver.png")
        self.bouton_desarchiver = CTRL_Bouton_image.CTRL(self, texte=_(u"Désarchiver"), cheminImage="Images/32x32/Desarchiver.png")
        self.bouton_effacer = CTRL_Bouton_image.CTRL(self, texte=_(u"Effacer"), cheminImage="Images/32x32/Gomme.png")

        # Boutons fenêtre
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonArchiver, self.bouton_archiver)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDesarchiver, self.bouton_desarchiver)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEffacer, self.bouton_effacer)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_archiver.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour archiver les lignes cochées. L'archivage permet de cacher des individus ou des familles dans certaines listes du logiciel.")))
        self.bouton_desarchiver.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour désarchiver les lignes cochées")))
        self.bouton_effacer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effacer définitivement les lignes cochées. L'effacement est une action irréversible qui supprime les données personnelles (anonymisation) mais sans affecter certaines données telles que la facturation ou les consommations.")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Liste de données
        sizer_donnees = wx.StaticBoxSizer(self.staticbox_donnees, wx.VERTICAL)
        sizer_donnees.Add(self.ctrl_notebook, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_donnees, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons d'action
        sizer_actions = wx.StaticBoxSizer(self.staticbox_actions, wx.VERTICAL)
        grid_sizer_actions = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_actions.Add(self.bouton_archiver, 1, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.bouton_desarchiver, 1, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.bouton_effacer, 1, wx.EXPAND, 0)
        grid_sizer_actions.AddGrowableCol(0)
        grid_sizer_actions.AddGrowableCol(1)
        grid_sizer_actions.AddGrowableCol(2)
        sizer_actions.Add(grid_sizer_actions, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_base.Add(sizer_actions, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Archivereteffacerdesindividus")

    def OnBoutonArchiver(self, event=None):
        self.ctrl_notebook.GetPageActive().ctrl_listview.Archiver()

    def OnBoutonDesarchiver(self, event=None):
        self.ctrl_notebook.GetPageActive().ctrl_listview.Desarchiver()

    def OnBoutonEffacer(self, event=None):
        self.ctrl_notebook.GetPageActive().ctrl_listview.Effacer()







if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
