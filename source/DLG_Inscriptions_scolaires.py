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
import CTRL_Bandeau
import CTRL_Classes
import OL_Inscriptions_scolaires

import GestionDB

try: import psyco; psyco.full()
except: pass


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
        for index, IDecoleTemp in self.dictEcoles.iteritems() :
            if IDecoleTemp == IDecole :
                self.SetSelection(index)

    def GetEcole(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.dictEcoles[index]
    
# ------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   

        # Bandeau
        intro = _(u"Vous pouvez ici consulter la liste des inscriptions scolaires par classe. La liste des inscrits peut être imprimée ou exportée. Pour inscrire un ou plusieurs individus, sélectionnez une classe dans la liste de gauche puis cliquez sur le bouton Ajouter. Cette fonction est particulièrement utile à la rentrée pour inscrire tous les enfants d'une classe dans la classe suivante.")
        titre = _(u"Inscriptions scolaires")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Classe.png")
        
        # Classes
        self.box_classes_staticbox = wx.StaticBox(self, -1, _(u"Classes"))
        self.ctrl_ecole = CTRL_Ecole(self)
        self.ctrl_classes = CTRL_Classes.CTRL(self, modeSelection=True)
        self.ctrl_classes.MAJ() 
        self.ctrl_classes.SetMinSize((300, -1))
        
        # Inscrits
        self.box_inscrits_staticbox = wx.StaticBox(self, -1, _(u"Aucun inscrit"))
        self.ctrl_inscrits = OL_Inscriptions_scolaires.ListView(self, id=-1, name="OL_Inscriptions_scolaires", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_inscrits.MAJ() 
        
        self.ctrl_recherche = OL_Inscriptions_scolaires.CTRL_Outils(self, listview=self.ctrl_inscrits)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixEcole, self.ctrl_ecole)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        self.ActiveControles() 
        self.OnChoixEcole(None)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour inscrire un ou plusieurs individus"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'inscription sélectionnée"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'inscription sélectionnée"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un apercu avant impression"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste des inscrits"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((990, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        box_inscrits = wx.StaticBoxSizer(self.box_inscrits_staticbox, wx.VERTICAL)
        grid_sizer_inscrits = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_inscrits = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        box_classes = wx.StaticBoxSizer(self.box_classes_staticbox, wx.VERTICAL)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        box_classes.Add(self.ctrl_ecole, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        box_classes.Add(self.ctrl_classes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(box_classes, 1, wx.EXPAND, 0)
        grid_sizer_inscrits.Add(self.ctrl_inscrits, 0, wx.EXPAND, 0)
        grid_sizer_boutons_inscrits.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_inscrits.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_inscrits.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons_inscrits.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons_inscrits.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons_inscrits.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons_inscrits.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_inscrits.Add(grid_sizer_boutons_inscrits, 1, wx.EXPAND, 0)
        grid_sizer_inscrits.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)

        grid_sizer_inscrits.AddGrowableRow(0)
        grid_sizer_inscrits.AddGrowableCol(0)
        box_inscrits.Add(grid_sizer_inscrits, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(box_inscrits, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
##        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
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

    def OnChoixEcole(self, event): 
        IDecole = self.ctrl_ecole.GetEcole()
        self.ctrl_classes.MAJ(IDecole=IDecole)

    def OnChoixClasse(self):
        IDclasse = self.ctrl_classes.GetClasse()
        self.ctrl_inscrits.MAJ(IDclasse=IDclasse) 
        self.ActiveControles() 
    
    def SetLabelBoxInscrits(self, nbre=0):
        if nbre == 0 : label = _(u"Aucun inscrit")
        elif nbre == 1 : label = _(u"1 inscrit")
        else : label = _(u"%d inscrits") % nbre
        self.box_inscrits_staticbox.SetLabel(label)
    
    def ActiveControles(self):
        IDclasse = self.ctrl_classes.GetClasse()
        if IDclasse == None :
            etat = False
        else:
            etat = True
        self.ctrl_inscrits.Activation(etat)
        self.bouton_ajouter.Enable(etat)
        self.bouton_modifier.Enable(etat)
        self.bouton_supprimer.Enable(etat)
        self.bouton_apercu.Enable(etat)
        self.bouton_imprimer.Enable(etat)
        
    def OnBoutonAjouter(self, event): 
        self.ctrl_inscrits.Ajouter()

    def OnBoutonModifier(self, event): 
        self.ctrl_inscrits.Modifier()

    def OnBoutonSupprimer(self, event):
        self.ctrl_inscrits.Supprimer()

    def OnBoutonApercu(self, event): 
        self.ctrl_inscrits.Apercu()

    def OnBoutonImprimer(self, event): 
        self.ctrl_inscrits.Imprimer()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Inscriptionsscolaires")
        
    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
