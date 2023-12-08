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
from Ctrl import CTRL_CheckListBox
from Ol import OL_Liste_inscriptions
from Dlg import DLG_Selection_activite



class CTRL_Regroupement(wx.Choice):
    def __init__(self, parent, listview=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listview = listview
        self.listeLabels = []

    def MAJ(self):
        self.listeLabels = [_(u"Aucun"),]
        for colonne in self.listview.columns :
            if colonne.visible == True :
                self.listeLabels.append(colonne.title)

        # listeChamps = self.listview.GetListeChamps()
        # for dictTemp in listeChamps :
        #     if dictTemp["afficher"] == True :
        #         self.listeLabels.append(dictTemp["label"])

        self.SetItems(self.listeLabels)
        self.Select(0)

    def GetRegroupement(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.GetSelection()-1



# -------------------------------------------------------------------------------------------------------------------------------------------------

class Parametres(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listview = listview
        
        # Activité
        self.box_activite_staticbox = wx.StaticBox(self, -1, _(u"Activité"))
        self.ctrl_activite = DLG_Selection_activite.Panel_Activite(self, callback=self.OnSelectionActivite)

        self.check_partis = wx.CheckBox(self, -1, _(u"Afficher les individus partis"))
        self.check_partis.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Groupes
        self.box_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_CheckListBox.Panel(self)
        
        # Catégories
        self.box_categories_staticbox = wx.StaticBox(self, -1, _(u"Catégories"))
        self.ctrl_categories = CTRL_CheckListBox.Panel(self)
        
        # Regroupement
        self.box_regroupement_staticbox = wx.StaticBox(self, -1, _(u"Regroupement"))
        self.ctrl_regroupement = CTRL_Regroupement(self, listview=listview)

        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_actualiser.SetMinSize((250, 40))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixRegroupement, self.ctrl_regroupement)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)

    def __set_properties(self):
        self.check_partis.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure dans la liste des individus partis")))
        self.ctrl_groupes.SetToolTip(wx.ToolTip(_(u"Cochez les groupes à afficher")))
        self.ctrl_categories.SetToolTip(wx.ToolTip(_(u"Cochez les catégories à afficher")))
        self.ctrl_regroupement.SetToolTip(wx.ToolTip(_(u"Sélectionnez un regroupement")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        # Activité
        box_activite = wx.StaticBoxSizer(self.box_activite_staticbox, wx.VERTICAL)
        box_activite.Add(self.ctrl_activite, 1, wx.ALL|wx.EXPAND, 5)
        box_activite.Add(self.check_partis, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        grid_sizer_base.Add(box_activite, 1, wx.EXPAND, 0)
        
        # Groupes
        box_groupes = wx.StaticBoxSizer(self.box_groupes_staticbox, wx.VERTICAL)
        box_groupes.Add(self.ctrl_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_groupes, 1, wx.EXPAND, 0)
        
        # Catégories
        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        box_categories.Add(self.ctrl_categories, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_categories, 1, wx.EXPAND, 0)
        
        # Regroupement
        box_regroupement = wx.StaticBoxSizer(self.box_regroupement_staticbox, wx.VERTICAL)
        box_regroupement.Add(self.ctrl_regroupement, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_regroupement, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

    def OnSelectionActivite(self):
        self.MAJ_Groupes()
        self.MAJ_Categories()

    def MAJ_Groupes(self):
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, IDactivite, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.ctrl_activite.GetID()
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        DB.Close()

        # Formatage des données
        listeDonnees = []
        for IDgroupe, IDactivite, nom in listeGroupes:
            dictTemp = {"ID": IDgroupe, "label": nom, "IDactivite": IDactivite}
            listeDonnees.append(dictTemp)

        # Envoi des données à la liste
        self.ctrl_groupes.SetDonnees(listeDonnees, cocher=True)

    def MAJ_Categories(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, IDactivite, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.ctrl_activite.GetID()
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()

        # Formatage des données
        listeDonnees = []
        for IDcategorie_tarif, IDactivite, nom in listeCategories:
            dictTemp = {"ID": IDcategorie_tarif, "label": nom, "IDactivite": IDactivite}
            listeDonnees.append(dictTemp)

        # Envoi des données à la liste
        self.ctrl_categories.SetDonnees(listeDonnees, cocher=True)

    def OnChoixRegroupement(self, event): 
        pass

    def OnBoutonActualiser(self, event): 
        # Récupération des paramètres
        IDactivite = self.ctrl_activite.GetID()
        partis = self.check_partis.GetValue() 
        listeGroupes = self.ctrl_groupes.GetIDcoches()
        listeCategories = self.ctrl_categories.GetIDcoches()
        regroupement = self.ctrl_regroupement.GetRegroupement()

        # Vérifications
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        labelParametres = self.GetLabelParametres() 
        
        # MAJ du listview
        self.parent.ctrl_listview.MAJ(IDactivite=IDactivite, partis=partis, listeGroupes=listeGroupes, listeCategories=listeCategories, 
                                                    regroupement=regroupement, labelParametres=labelParametres)

    def GetLabelParametres(self):
        listeParametres = []
        
        activite = self.ctrl_activite.GetNomActivite()
        listeParametres.append(_(u"Activité : %s") % activite)

        groupes = self.ctrl_groupes.GetLabelsCoches()
        listeParametres.append(_(u"Groupes : %s") % groupes)

        categories = self.ctrl_categories.GetLabelsCoches()
        listeParametres.append(_(u"Catégories : %s") % categories)

        labelParametres = " | ".join(listeParametres)
        return labelParametres


# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter et imprimer la liste des inscriptions. Commencez par sélectionner une activité avant de cliquer sur le bouton 'Rafraîchir la liste' pour afficher les résultats. Vous pouvez également regrouper les données par type d'informations et sélectionner les colonnes à afficher. Les données peuvent être ensuite imprimées ou exportées au format Texte ou Excel.")
        titre = _(u"Liste des inscriptions à une activité")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")

        self.listviewAvecFooter = OL_Liste_inscriptions.ListviewAvecFooter(self, kwargs={"nomListe": "OL_Liste_inscriptions"})
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Liste_inscriptions.CTRL_Outils(self, listview=self.ctrl_listview)
        self.ctrl_parametres = Parametres(self, listview=self.ctrl_listview)
        self.ctrl_listview.ctrl_regroupement = self.ctrl_parametres.ctrl_regroupement

        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_configuration = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.MenuConfigurerListe, self.bouton_configuration)

        # Init contrôles
        self.ctrl_listview.MAJ()
        self.ctrl_parametres.ctrl_regroupement.MAJ()

    def __set_properties(self):
        self.bouton_ouvrir_fiche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la fiche de la famille sélectionnée dans la liste")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_configuration.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour configurer la liste")))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND | wx.LEFT, 5)
        
        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_configuration, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
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
        self.CenterOnScreen()

    def OuvrirFiche(self, event):
        self.ctrl_listview.OuvrirFicheFamille(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesinscriptions")




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
