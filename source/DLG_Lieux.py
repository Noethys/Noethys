#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import OL_Lieux

try: import psyco; psyco.full()
except: pass


DICT_CATEGORIES = {
    "gare" : {"singulier":_(u"gare"), "pluriel":_(u"gares"), "masculinFeminin":"e", "image":"Train"},
    "aeroport" : {"singulier":_(u"a�roport"), "pluriel":_(u"a�roports"), "masculinFeminin":"", "image":"Avion"},
    "port" : {"singulier":_(u"port"), "pluriel":_(u"ports"), "masculinFeminin":"", "image":"Bateau"},
    "station" : {"singulier":_(u"station de m�tro"), "pluriel":_(u"stations de m�tro"), "masculinFeminin":"e", "image":"Metro"},
    }



class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="aeroport", mode="gestion"):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Lieux", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.mode = mode
        self.categorie = categorie
        
        # Recherche les caract�ristiques de la cat�gorie
        self.categorieSingulier = DICT_CATEGORIES[self.categorie]["singulier"]
        self.categoriePluriel = DICT_CATEGORIES[self.categorie]["pluriel"]
        self.masculinFeminin = DICT_CATEGORIES[self.categorie]["masculinFeminin"]
        self.nomImage = DICT_CATEGORIES[self.categorie]["image"]
        
        # Affichage des textes d'intro
        if self.mode == "selection" :
            intro = _(u"Vous pouvez ici s�lectionner un%s %s. Double-cliquez sur une ligne pour effectuer rapidement la s�lection.") % (self.masculinFeminin, self.categorieSingulier)
            titre = _(u"S�lection d'un%s %s") % (self.masculinFeminin, self.categorieSingulier)
            
        else:
            intro = _(u"Vous pouvez ici saisir, modifier ou supprimer des %s.") % self.categoriePluriel
            titre = _(u"Gestion des %s") % self.categoriePluriel
        self.SetTitle(titre)
        
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/%s.png" % self.nomImage)
        self.ctrl_listview = OL_Lieux.ListView(self, id=-1, categorie=self.categorie, categorieSingulier=self.categorieSingulier, categoriePluriel=self.categoriePluriel, masculinFeminin=self.masculinFeminin, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.MAJ()
        self.ctrl_recherche = OL_Lieux.BarreRecherche(self, categorieSingulier=self.categorieSingulier, masculinFeminin=self.masculinFeminin)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        
        if self.mode == "selection" :
            imgFermer = "Images/BoutonsImages/Annuler_L72.png"
        else:
            imgFermer = "Images/BoutonsImages/Fermer_L72.png"
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(imgFermer, wx.BITMAP_TYPE_ANY))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        if self.mode != "selection" :
            self.bouton_ok.Show(False)
            
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un%s %s") % (self.masculinFeminin, self.categorieSingulier))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le lieu s�lectionn� dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le lieu s�lectionn� dans la liste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer"))
        self.SetMinSize((600, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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

    def Ajouter(self, event):
        self.ctrl_listview.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)
    
    def GetIDcompagnie(self):
        selection = self.ctrl_listview.Selection()
        if len(selection) == 0 :
            return None
        else:
            return selection[0].IDlieu
        
    def OnBouton_ok(self, event):
        IDlieu = self.GetIDcompagnie()
        if IDlieu == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun%s %s dans la liste") % (self.masculinFeminin, self.categorieSingulier), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Lieux")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, mode="gestion")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
