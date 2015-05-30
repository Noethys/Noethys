#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import OL_Inscriptions 
import OL_Contrats
import UTILS_Utilisateurs


class Panel(wx.Panel):
    def __init__(self, parent, IDindividu=None, dictFamillesRattachees={}):
        wx.Panel.__init__(self, parent, id=-1, name="panel_inscriptions", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        # Inscriptions
        self.staticbox_inscriptions = wx.StaticBox(self, -1, _(u"Inscriptions"))
        self.ctrl_inscriptions = OL_Inscriptions.ListView(self, IDindividu=IDindividu, dictFamillesRattachees=self.dictFamillesRattachees, id=-1, name="OL_inscriptions", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_inscriptions.SetMinSize((150, 50))
        
        self.bouton_ajouter_inscription = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_inscription = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_inscription = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_forfait = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Forfait.png", wx.BITMAP_TYPE_ANY))

        # Contrats
        self.staticbox_contrats = wx.StaticBox(self, -1, _(u"Contrats"))
        self.ctrl_contrats = OL_Contrats.ListView(self, IDindividu=IDindividu, dictFamillesRattachees=self.dictFamillesRattachees, id=-1, name="OL_contrats", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_contrats.SetMinSize((150, 90))
        
        self.bouton_ajouter_contrat = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_contrat = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_contrat = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_inscriptions.Ajouter, self.bouton_ajouter_inscription)
        self.Bind(wx.EVT_BUTTON, self.ctrl_inscriptions.Modifier, self.bouton_modifier_inscription)
        self.Bind(wx.EVT_BUTTON, self.ctrl_inscriptions.Supprimer, self.bouton_supprimer_inscription)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonForfait, self.bouton_forfait)
        self.Bind(wx.EVT_BUTTON, self.ctrl_contrats.Ajouter, self.bouton_ajouter_contrat)
        self.Bind(wx.EVT_BUTTON, self.ctrl_contrats.Modifier, self.bouton_modifier_contrat)
        self.Bind(wx.EVT_BUTTON, self.ctrl_contrats.Supprimer, self.bouton_supprimer_contrat)

        # Propriétés
        self.bouton_ajouter_inscription.SetToolTipString(_(u"Cliquez ici pour inscrire l'individu à une activité"))
        self.bouton_modifier_inscription.SetToolTipString(_(u"Cliquez ici pour modifier l'inscription sélectionnée"))
        self.bouton_supprimer_inscription.SetToolTipString(_(u"Cliquez ici pour supprimer l'inscription sélectionnée"))
        self.bouton_forfait.SetToolTipString(_(u"Cliquez ici pour saisir manuellement un forfait daté"))
        self.bouton_ajouter_contrat.SetToolTipString(_(u"Cliquez ici pour créer un contrat pour cet individu"))
        self.bouton_modifier_contrat.SetToolTipString(_(u"Cliquez ici pour modifier le contrat sélectionné"))
        self.bouton_supprimer_contrat.SetToolTipString(_(u"Cliquez ici pour supprimer le contrat sélectionné"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        # Inscriptions
        staticbox_inscriptions = wx.StaticBoxSizer(self.staticbox_inscriptions, wx.VERTICAL)
        grid_sizer_inscriptions = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_inscriptions.Add(self.ctrl_inscriptions, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter_inscription, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier_inscription, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer_inscription, 0, wx.ALL, 0)
        grid_sizer_boutons.Add( (5, 5), 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_forfait, 0, wx.ALL, 0)
        grid_sizer_inscriptions.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        
        grid_sizer_inscriptions.AddGrowableCol(0)
        grid_sizer_inscriptions.AddGrowableRow(0)
        staticbox_inscriptions.Add(grid_sizer_inscriptions, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_inscriptions, 1, wx.EXPAND|wx.ALL, 5)

        # Contrats
        staticbox_contrats = wx.StaticBoxSizer(self.staticbox_contrats, wx.VERTICAL)
        grid_sizer_contrats = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_contrats.Add(self.ctrl_contrats, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter_contrat, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier_contrat, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer_contrat, 0, wx.ALL, 0)
        grid_sizer_contrats.Add(grid_sizer_boutons, 1, wx.ALL, 0)

        grid_sizer_contrats.AddGrowableCol(0)
        grid_sizer_contrats.AddGrowableRow(0)
        staticbox_contrats.Add(grid_sizer_contrats, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_contrats, 1, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Fit(self)

    def OnBoutonImprimer(self, event):
        if len(self.ctrl_inscriptions.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.ctrl_inscriptions.Selection()[0].IDinscription
                
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        # Item Recu 
        item = wx.MenuItem(menuPop, 10, _(u"Editer une confirmation d'inscription (PDF)"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_inscriptions.EditerConfirmation, id=10)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 20, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_inscriptions.Apercu, id=20)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 30, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_inscriptions.Imprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
    def OnBoutonForfait(self, event):
        """ Saisir un forfait daté """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "creer") == False : return
        
        # Recherche si l'individu est rattaché à d'autres familles
        listeNoms = []
        listeFamille = []
        # Vérifie que l'individu est rattaché comme REPRESENTANT ou ENFANT à une famille
        if self.dictFamillesRattachees != None :
            valide = False
            for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
                if dictFamille["IDcategorie"] in (1, 2) :
                    valide = True
            if valide == False :
                dlg = wx.MessageDialog(self, _(u"Pour être inscrit à une activité, un individu doit obligatoirement être rattaché comme représentant ou enfant à une fiche famille !"), _(u"Inscription impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        if len(self.dictFamillesRattachees) == 1 :
            IDfamille = self.dictFamillesRattachees.keys()[0]
            listeFamille.append(IDfamille)
            listeNoms.append(self.dictFamillesRattachees[IDfamille]["nomsTitulaires"])
        else:
            # Si rattachée à plusieurs familles
            for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
                IDcategorie = dictFamille["IDcategorie"]
                if IDcategorie in (1, 2) :
                    listeFamille.append(IDfamille)
                    listeNoms.append(dictFamille["nomsTitulaires"])
                
            if len(listeFamille) == 1 :
                IDfamille = listeFamille[0]
            else:
                # On demande à quelle famille rattacher cette inscription
                dlg = wx.SingleChoiceDialog(self, _(u"Cet individu est rattaché à %d familles.\nA quelle famille souhaitez-vous rattacher cette inscription ?") % len(listeNoms), _(u"Rattachements multiples"), listeNoms, wx.CHOICEDLG_STYLE)
                if dlg.ShowModal() == wx.ID_OK:
                    indexSelection = dlg.GetSelection()
                    IDfamille = listeFamille[indexSelection]
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return
        
        # Récupère la liste des activités sur lesquelle l'individu est inscrit
        listeActivites = self.ctrl_inscriptions.GetListeActivites()
        
        # Affiche la fenêtre de saisie d'un forfait daté
        import DLG_Appliquer_forfait
        dlg = DLG_Appliquer_forfait.Dialog(self, IDfamille=IDfamille, listeActivites=listeActivites, listeIndividus=[self.IDindividu,])
        if dlg.ShowModal() == wx.ID_OK :
            pass
        dlg.Destroy()
    
    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.IDindividu = self.GetGrandParent().IDindividu
        if self.IDindividu == None :
            print "pas de IDindividu !"
            return
        self.ctrl_inscriptions.MAJ() 
        self.ctrl_contrats.MAJ() 
        
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
        self.IDindividu = 46
        self.ctrl = Panel(panel, IDindividu=self.IDindividu)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()