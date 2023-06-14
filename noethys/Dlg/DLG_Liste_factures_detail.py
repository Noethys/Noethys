#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Liste_factures_detail
import GestionDB
from Utils import UTILS_Dates


class CTRL_Annee(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.SetListeDonnees() 
    
    def SetListeDonnees(self):
        self.listeNoms = [_(u"Toutes")]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDfacture, date_edition
        FROM factures;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        dictAnnees = {}
        for IDfacture, date in listeDonnees :
            dateDD = UTILS_Dates.DateEngEnDateDD(date)
            if dateDD != None :
                if (dateDD.year in dictAnnees) == False :
                    dictAnnees[dateDD.year] = 0
                dictAnnees[dateDD.year] += 1
        listeAnnees = list(dictAnnees.keys()) 
        listeAnnees.sort() 
        for annee in listeAnnees :
            nbre = dictAnnees[annee]
            self.listeNoms.append(u"%s (%d)" % (annee, nbre))
            self.listeID.append(annee)
        self.SetItems(self.listeNoms)
        self.SetSelection(len(listeAnnees))
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
# ------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter la liste détaillée des factures. Il est possible d'afficher pour chaque facture le montant des prestations regroupées par label ou par activité.")
        titre = _(u"Liste détaillée des factures")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Facture.png")

        # Paramètres
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Filtres"))

        self.label_annee = wx.StaticText(self, -1, _(u"Année d'édition :"))
        self.ctrl_annee = CTRL_Annee(self)
        self.ctrl_annee.SetMinSize((120, -1))

        self.label_tri = wx.StaticText(self, -1, _(u"Tri :"))
        self.ctrl_tri = wx.Choice(self, -1, choices = (_(u"Ordre de saisie"), _(u"Date d'édition"), _(u"Date début"), _(u"Date fin"), _(u"Numéro"), _(u"Famille"), _(u"Montant")))
        self.ctrl_tri.Select(1) 
        
        self.label_ordre = wx.StaticText(self, -1, _(u"Ordre :"))
        self.ctrl_ordre = wx.Choice(self, -1, choices = (_(u"Ascendant"), _(u"Descendant")))
        self.ctrl_ordre.Select(0) 
        
        # Liste
        self.listviewAvecFooter = OL_Liste_factures_detail.ListviewAvecFooter(self)
        self.ctrl_factures = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Liste_factures_detail.CTRL_Outils(self, listview=self.ctrl_factures)

        self.label_regroupement = wx.StaticText(self, -1, _(u"Détail :"))
        self.choix_regroupements = [("label", _(u"Nom de prestation")), ("IDactivite", _(u"Nom de l'activité"))]
        self.ctrl_regroupement = wx.Choice(self, -1, choices=[label for code, label in self.choix_regroupements])
        self.ctrl_regroupement.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoixRegroupement, self.ctrl_regroupement)

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.ctrl_factures.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_factures.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_factures.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_factures.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_annee)
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_tri)
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_ordre)
        
        # Init contrôles
        self.OnParametre()

    def __set_properties(self):
        self.ctrl_tri.SetToolTip(wx.ToolTip(_(u"Sélectionnez le critère de tri")))
        self.ctrl_ordre.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'ordre de tri")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((1030, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Paramètres
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=16, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_annee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_annee, 0, wx.EXPAND, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_tri, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_tri, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_ordre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_ordre, 0, 0, 0)
        staticbox_options.Add(grid_sizer_options, 0, wx.EXPAND|wx.ALL, 10)
        
        grid_sizer_base.Add(staticbox_options, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Liste
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=4, vgap=3, hgap=3)
        grid_sizer_commandes.Add(self.ctrl_recherche, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.label_regroupement, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 30)
        grid_sizer_commandes.Add(self.ctrl_regroupement, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_gauche.Add(grid_sizer_commandes, 1, wx.EXPAND, 10)

        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnChoixRegroupement(self, event=None):
        self.ctrl_factures.detail = self.choix_regroupements[self.ctrl_regroupement.GetSelection()][0]
        self.ctrl_factures.MAJ()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnParametre(self, event=None):
        listeFiltres = []
        
        # Année
        annee = self.ctrl_annee.GetID() 
        if annee != None :
            listeFiltres.append("factures.date_edition>='%d-01-01' and factures.date_edition<='%d-12-31' " % (annee, annee))

        # Tri
        tri = self.ctrl_tri.GetSelection() 
        if tri == 0 : numColonneTri = 0
        elif tri == 1 : numColonneTri = 1
        elif tri == 2 : numColonneTri = 2
        elif tri == 3 : numColonneTri = 3
        elif tri == 4 : numColonneTri = 4
        elif tri == 5 : numColonneTri = 5
        elif tri == 6 : numColonneTri = 6
        else : numColonneTri = 0
        
        # Ordre
        ordre = self.ctrl_ordre.GetSelection() 
        if ordre == 0 :
            ordreAscendant = True
        else :
            ordreAscendant = False
        
        # Envoi des paramètres au listview
        self.ctrl_factures.numColonneTri = numColonneTri
        self.ctrl_factures.ordreAscendant = ordreAscendant
        self.ctrl_factures.listeFiltres = listeFiltres
        self.ctrl_factures.MAJ()
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
