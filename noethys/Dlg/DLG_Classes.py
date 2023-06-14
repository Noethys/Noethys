#!/usr/bin/env python
# -*- coding: utf8 -*-
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
from Ctrl import CTRL_Classes
import GestionDB


class CTRL_Ecole(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.SetItems(listeItems)
            self.SetSelection(0)
                                        
    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDecole, nom, rue, cp, ville
        FROM ecoles ORDER BY nom; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictEcoles = {}
        index = 0
        for IDecole, nom, rue, cp, ville in listeDonnees :
            if ville != None and ville != "" :
                label = u"%s - %s" % (nom, ville)
            else :
                label = nom
            listeItems.append(label)
            self.dictEcoles[index] = IDecole
            index += 1
        return listeItems

    def SetEcole(self, IDecole=None):
        for index, IDecoleTemp in self.dictEcoles.items() :
            if IDecoleTemp == IDecole :
                self.SetSelection(index)

    def GetEcole(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else:
            return self.dictEcoles[index]
    
# ------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Classes", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        titre = _(u"Gestion des classes")
        intro = _(u"Vous pouvez ici paramétrer les classes pour chaque école. Vous devez obligatoirement indiquer pour chacune un nom, les dates de la saison et les niveaux scolaires concernés. Vous devez créer de nouvelles classes à chaque saison.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Classe.png")
        
        # Ecole
        self.staticbox_ecole_staticbox = wx.StaticBox(self, -1, _(u"Ecole"))
        self.label_ecole = wx.StaticText(self, -1, _(u"Ecole :"))
        self.ctrl_ecole = CTRL_Ecole(self)
        
        # Classes
        self.staticbox_classes_staticbox = wx.StaticBox(self, -1, _(u"Classes"))
        self.ctrl_classes = CTRL_Classes.CTRL(self)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixEcole, self.ctrl_ecole)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init contrôles
        self.OnChoixEcole(None)
        self.ActivationControles()

    def __set_properties(self):
        self.ctrl_ecole.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une école")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une classe")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la classe sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la classe sélectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((620, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Catégorie
        staticbox_ecole = wx.StaticBoxSizer(self.staticbox_ecole_staticbox, wx.VERTICAL)
        grid_sizer_ecole = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_ecole.Add(self.label_ecole, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ecole.Add(self.ctrl_ecole, 0, wx.EXPAND, 0)
        grid_sizer_ecole.AddGrowableCol(1)
        staticbox_ecole.Add(grid_sizer_ecole, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_ecole, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Modèles
        staticbox_classes = wx.StaticBoxSizer(self.staticbox_classes_staticbox, wx.VERTICAL)
        grid_sizer_classes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_classes.Add(self.ctrl_classes, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_classes.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_classes.AddGrowableRow(0)
        grid_sizer_classes.AddGrowableCol(0)
        staticbox_classes.Add(grid_sizer_classes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_classes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        
    def ActivationControles(self):
        if self.ctrl_ecole.GetEcole() == None :
            etat = False
        else:
            etat = True
        self.bouton_ajouter.Enable(etat)
        self.bouton_modifier.Enable(etat)
        self.bouton_supprimer.Enable(etat)
        self.ctrl_classes.Enable(etat)

    def OnChoixEcole(self, event): 
        IDecole = self.ctrl_ecole.GetEcole()
        self.ctrl_classes.MAJ(IDecole=IDecole)

    def OnBoutonAjouter(self, event): 
        self.ctrl_classes.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_classes.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_classes.Supprimer(None)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Classes")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
