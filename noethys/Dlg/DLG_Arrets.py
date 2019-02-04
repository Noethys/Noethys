#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Arrets
import GestionDB

try: import psyco; psyco.full()
except: pass

DICT_CATEGORIES = {
    "bus" : {"singulier":_(u"arrêt de bus"), "pluriel":_(u"arrêts de bus"), "image":"Bus"},
    "car" : {"singulier":_(u"arrêt de cars"), "pluriel":_(u"arrêts de cars"), "image":"Car"},
    "navette" : {"singulier":_(u"arrêt de navettes"), "pluriel":_(u"arrêts de navettes"), "image":"Navette"},
    "bateau" : {"singulier":_(u"arrêt maritime"), "pluriel":_(u"arrêts maritimes"), "image":"Bateau"},
    "metro" : {"singulier":_(u"arrêt de métros"), "pluriel":_(u"arrêts de métro"), "image":"Metro"},
    "pedibus" : {"singulier":_(u"arrêt de pédibus"), "pluriel":_(u"arrêts de pédibus"), "image":"Pedibus"},
    }


class CTRL_Choix_ligne(wx.Choice):
    def __init__(self, parent, categorie="bus"):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.categorie = categorie
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.Enable(len(listeItems))
        self.SetItems(listeItems)
        if len(listeItems) > 0 :
            self.Select(0)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDligne, nom
        FROM transports_lignes
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDligne, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDligne, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
# ------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="bus"):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Arrets", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.categorie = categorie
        
        # Recherche les caractéristiques de la catégorie
        self.categorieSingulier = DICT_CATEGORIES[self.categorie]["singulier"]
        self.categoriePluriel = DICT_CATEGORIES[self.categorie]["pluriel"]
        self.nomImage = DICT_CATEGORIES[self.categorie]["image"]
        
        # Affichage des textes d'intro
        intro = _(u"Vous pouvez ici saisir, modifier ou supprimer des %s.") % self.categoriePluriel
        titre = _(u"Gestion des %s") % self.categoriePluriel
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/%s.png" % self.nomImage)
        
        # Ligne
        self.staticbox_ligne_staticbox = wx.StaticBox(self, -1, _(u"Ligne"))
        self.label_ligne = wx.StaticText(self, -1, _(u"Ligne :"))
        self.ctrl_ligne = CTRL_Choix_ligne(self, self.categorie)
        self.bouton_gestion = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        # Arrêts
        self.staticbox_arrets_staticbox = wx.StaticBox(self, -1, _(u"Arrêts"))
        self.ctrl_arrets = OL_Arrets.ListView(self, id=-1, categorie=self.categorie, IDligne=0, categorieSingulier=self.categorieSingulier, categoriePluriel=self.categoriePluriel, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixLigne, self.ctrl_ligne)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMonter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDescendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGestion, self.bouton_gestion)
        
        # Init contrôle
        self.OnChoixLigne(None)

    def __set_properties(self):
        self.ctrl_ligne.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une ligne")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un nouvel arrêt")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'arrêt sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'arrêt sélectionné dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter l'arrêt sélectionné dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre l'arrêt sélectionné dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_gestion.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des lignes")))
        self.SetMinSize((650, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Catégorie
        staticbox_ligne = wx.StaticBoxSizer(self.staticbox_ligne_staticbox, wx.VERTICAL)
        grid_sizer_ligne = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_ligne.Add(self.label_ligne, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ligne.Add(self.ctrl_ligne, 0, wx.EXPAND, 0)
        grid_sizer_ligne.Add(self.bouton_gestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_ligne.AddGrowableCol(1)
        staticbox_ligne.Add(grid_sizer_ligne, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_ligne, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Modèles
        staticbox_arrets = wx.StaticBoxSizer(self.staticbox_arrets_staticbox, wx.VERTICAL)
        grid_sizer_arrets = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_arrets.Add(self.ctrl_arrets, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_arrets.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_arrets.AddGrowableRow(0)
        grid_sizer_arrets.AddGrowableCol(0)
        staticbox_arrets.Add(grid_sizer_arrets, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_arrets, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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

    def OnBoutonGestion(self, event): 
        IDligne = self.ctrl_ligne.GetID()
        from Dlg import DLG_Lignes
        dlg = DLG_Lignes.Dialog(self, categorie=self.categorie, mode="gestion")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_ligne.MAJ() 
        if IDligne == None : IDligne = 0
        self.ctrl_ligne.SetID(IDligne)
        self.OnChoixLigne(None)

    def OnChoixLigne(self, event): 
        IDligne = self.ctrl_ligne.GetID()
        if IDligne == None : IDligne = 0
        self.ctrl_arrets.MAJ(IDligne=IDligne)
        self.ctrl_arrets.Enable(IDligne)
        self.bouton_ajouter.Enable(IDligne)
        self.bouton_modifier.Enable(IDligne)
        self.bouton_supprimer.Enable(IDligne)
        self.bouton_monter.Enable(IDligne)
        self.bouton_descendre.Enable(IDligne)

    def OnBoutonAjouter(self, event): 
        self.ctrl_arrets.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_arrets.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_arrets.Supprimer(None)

    def OnBoutonMonter(self, event): 
        self.ctrl_arrets.Monter(None)
        
    def OnBoutonDescendre(self, event): 
        self.ctrl_arrets.Descendre(None)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Arrts")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
