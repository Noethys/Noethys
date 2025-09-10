#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Bandeau
from Ol import OL_Modeles_docs
import wx.lib.agw.hyperlink as Hyperlink
import webbrowser

LISTE_CATEGORIES = [
    ("facture", _(u"Facture")),
    ("rappel", _(u"Rappel")),
    ("attestation", _(u"Attestation de présence")),
    ("attestation_fiscale", _(u"Attestation fiscale")),
    ("reglement", _(u"Règlement")),
    ("individu", _(u"Individu")),
    ("famille", _(u"Famille")),
    ("inscription", _(u"Inscription")),
    ("cotisation", _(u"Cotisation")),
    ("location", _(u"Location")),
    ("location_demande", _(u"Demande de location")),
    ("devis", _(u"Devis")),
    ]


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if self.URL == "telecharger" :
            webbrowser.open("http://www.noethys.com/index.php?option=com_phocadownload&view=category&id=1:modeles-de-documents&Itemid=21")
        
        if self.URL == "proposer" :
            webbrowser.open("http://www.noethys.com/index.php?option=com_phocadownload&view=user&Itemid=21")
        
        self.UpdateLink()
        

class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        listeItems = []
        index = 0
        for code, label in LISTE_CATEGORIES :
            listeItems.append(label)
            index += 1
        return listeItems

    def SetCategorie(self, categorie=""):
        index = 0
        for code, label in LISTE_CATEGORIES :
            if code == categorie :
                 self.SetSelection(index)
            index += 1

    def GetCategorie(self):
        index = self.GetSelection()
        return LISTE_CATEGORIES[index][0]
    
# ------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_modeles_docs", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        titre = _(u"Modèles de documents")
        intro = _(u"Vous pouvez ici paramétrer les modèles de documents PDF. Noethys dispose d'un outil de mise en page qui vous permet de créer rapidement et facilement des documents assortis à la charte graphique de votre établissement.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document.png")
        
        # Catégorie
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"Catégorie"))
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self)
        if categorie != None :
            self.ctrl_categorie.SetCategorie(categorie)
        
        # Modèles
        self.staticbox_modeles_staticbox = wx.StaticBox(self, -1, _(u"Modèles disponibles"))
        self.ctrl_modeles = OL_Modeles_docs.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_dupliquer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_defaut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_importer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_import.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_exporter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_export.png"), wx.BITMAP_TYPE_ANY))
        
        self.hyper_telecharger = Hyperlien(self, label=_(u"Télécharger de nouveaux modèles"), infobulle=_(u"Cliquez ici pour télécharger de nouveaux modèles de documents sur internet"), URL="telecharger")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_proposer = Hyperlien(self, label=_(u"Proposer un modèle"), infobulle=_(u"Cliquez ici pour proposer un modèle à la communauté"), URL="proposer")
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fonds = CTRL_Bouton_image.CTRL(self, texte=_(u"Fonds de page"), cheminImage="Images/32x32/Document_fond.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorie, self.ctrl_categorie)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDupliquer, self.bouton_dupliquer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImporter, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExporter, self.bouton_exporter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDefaut, self.bouton_defaut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFonds, self.bouton_fonds)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init contrôle
        self.OnChoixCategorie(None)

    def __set_properties(self):
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une catégorie")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un nouveau modèle")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le modèle sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le modèle sélectionné dans la liste")))
        self.bouton_dupliquer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour dupliquer le modèle sélectionné dans la liste")))
        self.bouton_importer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer un modèle de document (.ndc)")))
        self.bouton_exporter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter le modèle sélectionné dans la liste (.ndc)")))
        self.bouton_defaut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour définir ce modèle par défaut pour cette catégorie")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fonds.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder au paramétrage des fonds de page")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((650, 560))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Catégorie
        staticbox_categorie = wx.StaticBoxSizer(self.staticbox_categorie_staticbox, wx.VERTICAL)
        grid_sizer_categorie = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_categorie.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_categorie.AddGrowableCol(1)
        staticbox_categorie.Add(grid_sizer_categorie, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_categorie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Modèles
        staticbox_modeles = wx.StaticBoxSizer(self.staticbox_modeles_staticbox, wx.VERTICAL)
        grid_sizer_modeles = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_modeles.Add(self.ctrl_modeles, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_dupliquer, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_defaut, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_importer, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_exporter, 0, 0, 0)
        grid_sizer_modeles.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_hyper = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_hyper.Add(self.hyper_telecharger, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_hyper.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_hyper.Add(self.hyper_proposer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modeles.Add(grid_sizer_hyper, 1, wx.EXPAND, 0)
        
        grid_sizer_modeles.AddGrowableRow(0)
        grid_sizer_modeles.AddGrowableCol(0)
        staticbox_modeles.Add(grid_sizer_modeles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_modeles, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fonds, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnChoixCategorie(self, event): 
        categorie = self.ctrl_categorie.GetCategorie()
        self.ctrl_modeles.MAJ(categorie=categorie)
    
    def SelectCategorie(self, categorie=""):
        self.ctrl_categorie.SetCategorie(categorie)
        self.OnChoixCategorie(None)
        
    def OnBoutonAjouter(self, event): 
        self.ctrl_modeles.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_modeles.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_modeles.Supprimer(None)

    def OnBoutonDupliquer(self, event): 
        self.ctrl_modeles.Dupliquer(None)

    def OnBoutonImporter(self, event): 
        self.ctrl_modeles.Importer(None)

    def OnBoutonExporter(self, event): 
        self.ctrl_modeles.Exporter(None)

    def OnBoutonDefaut(self, event): 
        self.ctrl_modeles.SetDefaut(None)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Modlesdedocuments")

    def OnBoutonFonds(self, event): 
        from Dlg import DLG_Modeles_fonds
        dlg = DLG_Modeles_fonds.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_modeles.MAJ() 

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_CANCEL)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
