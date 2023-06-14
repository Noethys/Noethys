#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ol import OL_Contratspsu_previsions
from Ol import OL_Contrats_planning_elements
from Ctrl import CTRL_Saisie_duree
from Utils import UTILS_Dates
from Ctrl import CTRL_Bouton_image
import GestionDB


class Page_planning(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="page_planning", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        if self.clsbase != None :
            IDactivite = self.clsbase.GetValeur("IDactivite")
            IDunite_prevision = self.clsbase.GetValeur("IDunite_prevision")
        else :
            IDactivite = 0
            IDunite_prevision = 0

        self.ctrl_planning = OL_Contrats_planning_elements.ListView(self, id=-1, IDactivite=IDactivite, IDunite=IDunite_prevision, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_planning.SetMinSize((50, 50))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_generer = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer les consommations"), cheminImage="Images/32x32/Magique.png")

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.Generer, self.bouton_generer)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un paramètre de planning")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le paramètre de planning sélectionné")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le paramètre de planning sélectionné")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_generer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour générer les consommations selon le planning")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_planning, 1, wx.EXPAND|wx.LEFT|wx.TOP, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.RIGHT|wx.TOP, 10)

        grid_sizer_base.Add(self.bouton_generer, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def Generer(self, event):
        date_debut = self.clsbase.GetValeur("date_debut")
        date_fin = self.clsbase.GetValeur("date_fin")
        listeConso = self.ctrl_planning.GetConso(date_debut, date_fin)
        self.parent.page_consommations.ctrl_consommations.GenerationSelonPlanning(listeConso)



class Page_consommations(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="page_consommations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        self.listviewAvecFooter = OL_Contratspsu_previsions.ListviewAvecFooter(self, kwargs={"clsbase" : clsbase})
        self.ctrl_consommations = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Contratspsu_previsions.CTRL_Outils(self, listview=self.ctrl_consommations, afficherCocher=True)
        if self.GetGrandParent().GetParent().GetName() == "notebook" :
            self.ctrl_recherche.SetBackgroundColour(self.GetGrandParent().GetParent().GetThemeBackgroundColour())

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_consommations.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_consommations.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_consommations.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_consommations.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_consommations.Imprimer, self.bouton_imprimer)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une consommation")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la consommation sélectionnée")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la consommation sélectionnée")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.listviewAvecFooter, 1, wx.EXPAND|wx.LEFT|wx.TOP, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.RIGHT|wx.TOP, 10)

        grid_sizer_base.Add(self.ctrl_recherche, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)






class Notebook(wx.Notebook):
    def __init__(self, parent, clsbase=None):
        wx.Notebook.__init__(self, parent, id=-1, name="notebook_calendrier", style=wx.BK_LEFT)
        self.clsbase = clsbase

        # Page planning
        self.page_planning = Page_planning(self, clsbase)
        self.AddPage(self.page_planning, _(u"Planning"))

        # Page consommations
        self.page_consommations = Page_consommations(self, clsbase)
        self.AddPage(self.page_consommations, _(u"Consommations"))


    def SetLabelPage(self, numPage=0, label=""):
        self.SetPageText(numPage, label)






class Panel(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_calendrier", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Prévisions
        self.staticbox_previsions_staticbox = wx.StaticBox(self, -1, _(u"Présences prévisionnelles"))
        self.ctrl_previsions = Notebook(self, clsbase)
        try :
            self.ctrl_previsions.SetBackgroundColour(self.GetParent().GetThemeBackgroundColour())
        except :
            pass

        # Absences
        self.staticbox_absences_staticbox = wx.StaticBox(self, -1, _(u"Absences RTT"))
        self.label_absences_prevues = wx.StaticText(self, -1, _(u"Prévues :"))
        self.ctrl_absences_prevues = CTRL_Saisie_duree.CTRL(self, size=(50, -1))
        self.label_absences_prises = wx.StaticText(self, -1, _(u"Prises :"))
        self.ctrl_absences_prises = CTRL_Saisie_duree.CTRL(self, size=(50, -1))
        self.ctrl_absences_prises.Enable(False)
        self.label_absences_solde = wx.StaticText(self, -1, _(u"Restantes :"))
        self.ctrl_absences_solde = CTRL_Saisie_duree.CTRL(self, size=(50, -1))
        self.ctrl_absences_solde.Enable(False)

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_arrondi = wx.StaticText(self, -1, _(u"Arrondi :"))
        self.liste_arrondi_type = [(None, _(u"Aucun")), ("tranche_horaire", _(u"Tranche horaire")), ("duree", _(u"Durée"))]
        self.liste_arrondi_delta = [(10, _(u"10 min")), (15, _(u"15 min")), (30, _(u"30 min")), (60, _(u"60 min"))]
        self.ctrl_arrondi_type = wx.Choice(self, -1, choices=[label for code, label in self.liste_arrondi_type])
        self.ctrl_arrondi_delta = wx.Choice(self, -1, choices=[label for code, label in self.liste_arrondi_delta])

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_TEXT, self.OnChangeAbsencesPrevues, self.ctrl_absences_prevues)
        self.Bind(wx.EVT_CHOICE, self.OnChoixArrondi, self.ctrl_arrondi_type)
        self.Bind(wx.EVT_CHOICE, self.OnChoixArrondi, self.ctrl_arrondi_delta)

        # Init
        self.OnChangeAbsencesPrevues()
        self.ctrl_arrondi_type.SetSelection(0)
        self.ctrl_arrondi_delta.SetSelection(0)
        # self.OnChoixArrondi()
        self.ctrl_arrondi_delta.Enable(self.ctrl_arrondi_type.GetSelection() != 0)

    def __set_properties(self):
        self.ctrl_absences_prevues.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nombre d'heures d'absences prévues (RTT)")))
        self.ctrl_arrondi_type.SetToolTip(wx.ToolTip(_(u"Sélectionnez un type d'arrondi")))
        self.ctrl_arrondi_delta.SetToolTip(wx.ToolTip(_(u"Sélectionnez le deltade l'arrondi")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Prévisions
        staticbox_previsions = wx.StaticBoxSizer(self.staticbox_previsions_staticbox, wx.VERTICAL)
        staticbox_previsions.Add(self.ctrl_previsions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_previsions, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Absences
        staticbox_absences = wx.StaticBoxSizer(self.staticbox_absences_staticbox, wx.VERTICAL)
        grid_sizer_absences = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_absences.Add(self.label_absences_prevues, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add(self.ctrl_absences_prevues, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add( (5, 5), 0, 0, 0)
        grid_sizer_absences.Add(self.label_absences_prises, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add(self.ctrl_absences_prises, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add( (5, 5), 0, 0, 0)
        grid_sizer_absences.Add(self.label_absences_solde, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add(self.ctrl_absences_solde, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.AddGrowableCol(1)
        grid_sizer_absences.AddGrowableCol(4)
        grid_sizer_absences.AddGrowableCol(7)
        staticbox_absences.Add(grid_sizer_absences, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_absences, 1, wx.EXPAND, 0)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_arrondi, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_arrondi_type, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_arrondi_delta, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_options, 1, wx.EXPAND, 0)

        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnChangeAbsencesPrevues(self, event=None):
        solde = self.ctrl_absences_prevues.GetValue() - self.ctrl_absences_prises.GetValue()
        self.ctrl_absences_solde.SetValue(solde)

    def OnChoixArrondi(self, event=None):
        self.ctrl_arrondi_delta.Enable(self.ctrl_arrondi_type.GetSelection() != 0)
        arrondi_type = self.GetArrondiType()
        arrondi_delta = self.GetArrondiDelta()
        self.clsbase.SetValeur("arrondi_type", arrondi_type)
        self.clsbase.SetValeur("arrondi_delta", arrondi_delta)
        self.ctrl_previsions.page_consommations.ctrl_consommations.MAJtracks()
        self.clsbase.SetValeur("tracks_previsions", self.ctrl_previsions.page_consommations.ctrl_consommations.GetTracks())
        self.clsbase.Calculer()

    def GetArrondiType(self):
        return self.liste_arrondi_type[self.ctrl_arrondi_type.GetSelection()][0]

    def GetArrondiDelta(self):
        return self.liste_arrondi_delta[self.ctrl_arrondi_delta.GetSelection()][0]

    def SetArrondiType(self, arrondi_type=None):
        index = 0
        for code, label in self.liste_arrondi_type :
            if code == arrondi_type :
                self.ctrl_arrondi_type.SetSelection(index)
            index += 1
        self.ctrl_arrondi_delta.Enable(self.ctrl_arrondi_type.GetSelection() != 0)

    def SetArrondiDelta(self, arrondi_delta=10):
        index = 0
        for code, label in self.liste_arrondi_delta :
            if code == arrondi_delta :
                self.ctrl_arrondi_delta.SetSelection(index)
            index += 1

    def Validation(self):
        nbreConso = len(self.ctrl_previsions.page_consommations.ctrl_consommations.GetTracks())
        if nbreConso == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune consommation prévisionnelle ! Souhaitez-vous tout de même continuer ?\n\nPour saisir des consommations, vous avez deux possibilités : Soit vous créez un planning dans l'onglet 'Planning' puis cliquez sur 'Générer les consommations', soit vous saisissez manuellement les consommations souhaitées depuis l'onglet 'Consommations'."), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Recalcul de toutes les données du contrat
        if self.clsbase.Calculer(mode_test=True) == False :
            return False

        return True

    def Sauvegarde(self):
        self.clsbase.SetValeur("planning", self.ctrl_previsions.page_planning.ctrl_planning.GetElementsStr())
        self.clsbase.SetValeur("tracks_previsions", self.ctrl_previsions.page_consommations.ctrl_consommations.GetTracks())
        self.clsbase.SetValeur("duree_absences_prevues", self.ctrl_absences_prevues.GetValue())
        self.clsbase.SetValeur("duree_absences_prises", self.ctrl_absences_prises.GetValue())
        self.clsbase.SetValeur("duree_absences_solde", self.ctrl_absences_solde.GetValue())
        self.clsbase.SetValeur("arrondi_type", self.GetArrondiType())
        self.clsbase.SetValeur("arrondi_delta", self.GetArrondiDelta())

    def MAJ(self):
        self.clsbase.Calculer()

        if self.MAJ_effectuee == False :

            # Planning
            self.ctrl_previsions.page_planning.ctrl_planning.SetElementsStr(self.clsbase.GetValeur("planning"))

            # Consommations
            self.ctrl_previsions.page_consommations.ctrl_consommations.IDunite_prevision = self.clsbase.GetValeur("IDunite_prevision")
            self.ctrl_previsions.page_consommations.ctrl_consommations.SetTracks(self.clsbase.GetValeur("tracks_previsions", []))

            # Absences
            duree_absences_prevues = self.clsbase.GetValeur("duree_absences_prevues")
            if duree_absences_prevues != None :
                self.ctrl_absences_prevues.SetValue(duree_absences_prevues)
            duree_absences_prises = self.clsbase.GetValeur("duree_absences_prises")
            if duree_absences_prises != None :
                self.ctrl_absences_prises.SetValue(duree_absences_prises)
            self.OnChangeAbsencesPrevues()

            # Options
            arrondi_type = self.clsbase.GetValeur("arrondi_type", "duree")
            self.SetArrondiType(arrondi_type)
            arrondi_delta = self.clsbase.GetValeur("arrondi_delta", 30)
            self.SetArrondiDelta(arrondi_delta)

        self.MAJ_effectuee = True


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        # Chargement d'un contrat pour les tests
        from Dlg.DLG_Saisie_contratpsu import Base
        self.clsbase = Base(IDcontrat=8)

        self.ctrl = Panel(panel, clsbase=self.clsbase)
        self.bouton_test = wx.Button(panel, -1, "Test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)

    def OnBoutonTest(self, event):
        self.clsbase.CalculerTotaux()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()