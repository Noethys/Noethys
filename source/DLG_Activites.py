#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import CTRL_Bandeau
import OL_Activites
import wx.lib.agw.hyperlink as Hyperlink
import webbrowser



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
            webbrowser.open("http://www.noethys.com/index.php?option=com_phocadownload&view=category&id=4:parametrages-dactivites&Itemid=21")
        self.UpdateLink()



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = u"Vous pouvez ici saisir, modifier ou supprimer des activités. Une activité peut être un Accueil de Loisirs, un séjour de vacances, une cantine scolaire, une garderie périscolaire, une crèche, une activité sportive ou culturelle, etc..."
        titre = u"Gestion des activités"
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")
        self.ctrl_listview = OL_Activites.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.MAJ()
        self.ctrl_recherche = OL_Activites.CTRL_Outils(self, listview=self.ctrl_listview)
    
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_dupliquer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_importer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Document_import.png", wx.BITMAP_TYPE_ANY))
        self.bouton_exporter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Document_export.png", wx.BITMAP_TYPE_ANY))

        # Commande télécharger
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(u"Images/16x16/Updater.png", wx.BITMAP_TYPE_ANY))
        self.hyper_telecharger = Hyperlien(self, label=u"Télécharger des paramétrages d'activités", infobulle=u"Cliquez ici pour télécharger et importer des paramétrages d'activités", URL="telecharger")

        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDupliquer, self.bouton_dupliquer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImporter, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExporter, self.bouton_exporter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(u"Gestion des activités")
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une activité")
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier l'activité sélectionnée dans la liste")
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer l'activité sélectionnée dans la liste")
        self.bouton_dupliquer.SetToolTipString(u"Cliquez ici pour dupliquer l'activité sélectionnée dans la liste")
        self.bouton_importer.SetToolTipString(u"Cliquez ici pour importer un paramétrage d'activité (.nxa)")
        self.bouton_exporter.SetToolTipString(u"Cliquez ici pour exporter un ou plusieurs paramétrages d'activités (.nxa)")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((700, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)

##        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_dupliquer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_importer, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_exporter, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=4, vgap=3, hgap=3)
        grid_sizer_commandes.Add(self.ctrl_image, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_telecharger, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add( (70, 10), 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.ctrl_recherche, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableCol(3)
        grid_sizer_contenu.Add(grid_sizer_commandes, 1, wx.EXPAND, 10)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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

    def Ajouter(self, event):
        self.ctrl_listview.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)

    def OnBoutonDupliquer(self, event): 
        self.ctrl_listview.Dupliquer(None)

    def OnBoutonImporter(self, event): 
        self.ctrl_listview.Importer(None)

    def OnBoutonExporter(self, event): 
        self.ctrl_listview.Exporter(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Activits")
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
