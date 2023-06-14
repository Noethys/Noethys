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
from Ol import OL_Liste_cotisations 
import GestionDB
from Utils import UTILS_Utilisateurs


class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_cotisations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.staticbox_cotisations = wx.StaticBox(self, -1, _(u"Cotisations familiales et individuelles"))
        
        # OL Cotisations
        codesColonnes = ["IDcotisation", "date_debut", "date_fin", "beneficiaires", "nom", "numero", "date_creation_carte", "depot_nom", "activites", "observations"]
        checkColonne = True
        triColonne = "date_debut"
        self.listviewAvecFooter = OL_Liste_cotisations.ListviewAvecFooter(self, kwargs={"IDfamille" : IDfamille, "mode" : "famille", "codesColonnes" : codesColonnes, "checkColonne" : checkColonne, "triColonne" : triColonne}) 
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Liste_cotisations.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)
        self.ctrl_recherche.SetBackgroundColour((255, 255, 255))
        
        # Commandes boutons
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        
        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une cotisation")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la cotisation sélectionnée")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la cotisation sélectionnée")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer un document")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        staticbox_cotisations = wx.StaticBoxSizer(self.staticbox_cotisations, wx.VERTICAL)
        grid_sizer_cotisations = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_cotisations.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_boutons.Add( (5, 5), 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, wx.ALL, 0)
        grid_sizer_cotisations.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        
        grid_sizer_cotisations.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        
        grid_sizer_cotisations.AddGrowableCol(0)
        grid_sizer_cotisations.AddGrowableRow(0)
        staticbox_cotisations.Add(grid_sizer_cotisations, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_cotisations, 1, wx.EXPAND|wx.ALL, 5)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def OnBoutonAjouter(self, event):
        self.ctrl_listview.Ajouter(None)

    def OnBoutonModifier(self, event):
        self.ctrl_listview.Modifier(None)

    def OnBoutonSupprimer(self, event):
        self.ctrl_listview.Supprimer(None)

    def OnBoutonImprimer(self, event):
        if len(self.ctrl_listview.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.ctrl_listview.Selection()[0].IDcotisation
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Imprimer cotisation
        item = wx.MenuItem(menuPop, 40, _(u"Imprimer la cotisation"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Reedition, id=40)
        if noSelection == True : item.Enable(False)

        # Item Recu Dons aux oeuvres
        item = wx.MenuItem(menuPop, 10, _(u"Editer un reçu Dons aux Oeuvres (PDF)"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ImpressionRecu, id=10)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 20, _(u"Aperçu avant impression de la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=20)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 30, _(u"Imprimer la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Reedition(self, event):
        self.ctrl_listview.Reedition(None)

    def ImpressionRecu(self, event):
        self.ctrl_listview.RecuCotisation(None)

    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)

    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_cotisations", "consulter", afficheMessage=False) == False : 
            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.ctrl_listview.MAJ() 
        self.Refresh()
                
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        pass
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDfamille=3)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((200, 300))
##        self.Layout()
##        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()