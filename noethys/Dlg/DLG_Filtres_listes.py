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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Profil
from Ol import OL_Utilisateurs
from Ol import OL_Filtres_listes



class CTRL_profil_perso(CTRL_Profil.CTRL):
    def __init__(self, parent, categorie="", dlg=None):
        CTRL_Profil.CTRL.__init__(self, parent, categorie=categorie)
        self.dlg = dlg

    def Envoyer_parametres(self, dictParametres={}):
        """ Envoi des paramètres du profil sélectionné à la fenêtre """
        listeFiltres = []
        if dictParametres != None :
            for index, dictFiltreStr in dictParametres.iteritems() :
                exec ("dictFiltre = " + dictFiltreStr)
                listeFiltres.append(dictFiltre)
        self.dlg.SetDonnees(listeFiltres)

    def Recevoir_parametres(self):
        """ Récupération des paramètres pour la sauvegarde du profil """
        listeFiltres = self.dlg.GetDonnees()
        dictParametres = {}
        index = 0
        for dictFiltre in listeFiltres :
            dictParametres["filtre%d" % index] = str(dictFiltre)
            index += 1
        # Vide le profil des éventuels précédents paramètres
        self.ViderProfil()
        # Puis enregistre les nouveaux paramètres du profil
        self.Enregistrer(dictParametres)



# ---------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, ctrl_listview=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.ctrl_listview = ctrl_listview
        
        intro = _(u"Cliquez sur le bouton Ajouter situé à droite de la liste pour saisir de nouveaux filtres. Si le profil de configuration est disponible, utilisez-le pour mémoriser vos filtres préférés.")
        titre = _(u"Filtrer")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Filtre.png")

        # Filtres
        self.staticbox_filtres_staticbox = wx.StaticBox(self, -1, _(u"Liste des filtres"))
        self.ctrl_filtres = OL_Filtres_listes.ListView(self, ctrl_listview=ctrl_listview, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_filtres.MAJ() 

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_tout_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Filtre_supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Profil
        if self.ctrl_listview != None :
            nom_liste = self.ctrl_listview.GetNomModule()
        else :
            nom_liste = None
        self.staticbox_profil_staticbox = wx.StaticBox(self, -1, _(u"Profil de configuration"))
        self.ctrl_profil = CTRL_profil_perso(self, categorie=nom_liste, dlg=self)
        self.ctrl_profil.SetMinSize((100, -1))
        if nom_liste == None :
            self.staticbox_profil_staticbox.Show(False)
            self.ctrl_profil.Show(False)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.ctrl_filtres.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_filtres.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_filtres.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_filtres.ToutSupprimer, self.bouton_tout_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un filtre")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le filtre sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le filtre sélectionné dans la liste")))
        self.bouton_tout_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer TOUS les filtres de cette liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((600, 430))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Filtres
        staticbox_filtres = wx.StaticBoxSizer(self.staticbox_filtres_staticbox, wx.VERTICAL)
        grid_sizer_filtres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.ctrl_filtres, 0, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_filtres.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_tout_supprimer, 0, 0, 0)

        grid_sizer_filtres.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_filtres.AddGrowableRow(0)
        grid_sizer_filtres.AddGrowableCol(0)

        staticbox_filtres.Add(grid_sizer_filtres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_filtres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Profil
        staticbox_profil = wx.StaticBoxSizer(self.staticbox_profil_staticbox, wx.VERTICAL)
        staticbox_profil.Add(self.ctrl_profil, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_profil, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        return self.ctrl_filtres.GetDonnees()

    def SetDonnees(self, listeFiltres=[]):
        self.ctrl_filtres.SetDonnees(listeFiltres)
    



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
