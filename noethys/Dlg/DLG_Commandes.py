#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
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
import GestionDB
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Commandes



class CTRL_Modele(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        # Importation des catégories
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, defaut
        FROM modeles_commandes
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        self.dictModeles = {}
        index = 0
        selection_defaut = None
        for IDmodele, nom, defaut in listeCategories:
            dictTemp = {"IDmodele": IDmodele, "nom": nom}
            self.dictDonnees[index] = dictTemp
            self.dictModeles[IDmodele] = dictTemp
            listeItems.append(nom)
            if defaut == 1 :
                selection_defaut = index
            index += 1

        self.SetItems(listeItems)
        if len(self.dictDonnees) > 0:
            self.Enable(True)
            if selection_defaut != None :
                self.Select(selection_defaut)
        else :
            self.Enable(False)

    def GetListeDonnees(self):
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["IDmodele"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["IDmodele"]



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Commandes_docs", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        titre = _(u"Commandes des repas")
        intro = _(u"Vous pouvez ici créer des commandes de repas. Sélectionnez un modèle de commande puis cliquez sur le bouton Ajouter pour créer une nouvelle commande. Si aucun modèle de commande n'existe, vous devez obligatoirement commencer par en créer un avant de saisir une commande.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Repas.png")
        
        # Modèle
        self.staticbox_modele_staticbox = wx.StaticBox(self, -1, _(u"Modèle de commande"))
        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = CTRL_Modele(self)
        self.bouton_modeles = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Commandes
        self.staticbox_commandes_staticbox = wx.StaticBox(self, -1, _(u"Commandes"))
        self.ctrl_commandes = OL_Commandes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixModele, self.ctrl_modele)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_modeles)
        self.Bind(wx.EVT_BUTTON, self.ctrl_commandes.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_commandes.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_commandes.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

        # Init contrôle
        self.OnChoixModele(None)

    def __set_properties(self):
        self.ctrl_modele.SetToolTip(wx.ToolTip(_(u"Sélectionnez un modèle de commandes")))
        self.bouton_modeles.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer des modèles de commandes")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une nouvelle commande")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la commande sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la commande sélectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((780, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Modèle
        staticbox_modele = wx.StaticBoxSizer(self.staticbox_modele_staticbox, wx.VERTICAL)
        grid_sizer_modele = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=5)
        grid_sizer_modele.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_modele.Add(self.bouton_modeles, 0, wx.EXPAND, 0)
        grid_sizer_modele.AddGrowableCol(1)
        staticbox_modele.Add(grid_sizer_modele, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_modele, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Commandes
        staticbox_commandes = wx.StaticBoxSizer(self.staticbox_commandes_staticbox, wx.VERTICAL)
        grid_sizer_commandes = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.ctrl_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add(grid_sizer_commandes_commandes, 1, wx.EXPAND, 0)

        grid_sizer_commandes.AddGrowableRow(0)
        grid_sizer_commandes.AddGrowableCol(0)
        staticbox_commandes.Add(grid_sizer_commandes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_commandes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
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

    def OnChoixModele(self, event=None):
        IDmodele = self.ctrl_modele.GetID()
        self.ctrl_commandes.SetIDmodele(IDmodele)
        self.ctrl_commandes.MAJ()
        if IDmodele == None :
            actif = False
        else :
            actif = True
        self.ctrl_commandes.Activation(actif)
        self.bouton_ajouter.Enable(actif)
        self.bouton_modifier.Enable(actif)
        self.bouton_supprimer.Enable(actif)

    def OnBoutonModeles(self, event):
        IDmodele = self.ctrl_modele.GetID()
        from Dlg import DLG_Modeles_commandes
        dlg = DLG_Modeles_commandes.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_modele.MAJ()
        self.ctrl_modele.SetID(IDmodele)
        self.OnChoixModele()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Commandesdesrepas")

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
