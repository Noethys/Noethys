#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Traductions
import os
from Utils import UTILS_Json
from Utils import UTILS_Fichiers


class Dialog(wx.Dialog):
    def __init__(self, parent, code="", nom=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.code = code
        self.nom = nom
        
        intro = _(u"Double-cliquez sur une ligne pour saisir ou modifier la traduction correspondante. Il est possible de traduire uniquement une partie du logiciel en utilisant la barre de recherche qui appliquera un filtre sur les résultats (Exemple : Tapez 'facture' pour sélectionner uniquement les textes qui concernent les factures).")
        titre = _(u"Saisie d'une traduction")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Traduction.png")
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom_langue = wx.StaticText(self, -1, _(u"Nom de la langue :"))
        self.ctrl_nom_langue = wx.TextCtrl(self, -1, self.nom)
        self.ctrl_nom_langue.SetMinSize((300, -1))
        self.ctrl_nom_langue.Enable(False) 
        self.label_code_langue = wx.StaticText(self, -1, _(u"Code ISO :"))
        self.ctrl_code_langue = wx.TextCtrl(self, -1, self.code)
        self.ctrl_code_langue.Enable(False) 
                
        # Liste des traductions
        self.box_traductions_staticbox = wx.StaticBox(self, -1, _(u"Traductions"))
        self.listviewAvecFooter = OL_Traductions.ListviewAvecFooter(self, kwargs={"code":self.code}) 
        self.ctrl_traductions = self.listviewAvecFooter.GetListview()
        self.ctrl_outils = OL_Traductions.CTRL_Outils(self, listview=self.ctrl_traductions)
        
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.ctrl_traductions.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_traductions.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_traductions.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_traductions.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_traductions.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        self.ctrl_traductions.MAJ() 
        

    def __set_properties(self):
        self.ctrl_nom_langue.SetToolTip(wx.ToolTip(_(u"Saisissez le nom de la langue (Exemple : 'Anglais'")))
        self.ctrl_code_langue.SetToolTip(wx.ToolTip(_(u"Saisissez un code alpha pour cette langue sans espaces ni majuscules ni caractères spéciaux (Exemple : 'anglais')")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une traduction pour la ligne sélectionnée dans la liste")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.SetMinSize((950, 750))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom_langue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom_langue, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_code_langue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_code_langue, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableCol(4)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Liste
        box_traductions = wx.StaticBoxSizer(self.box_traductions_staticbox, wx.VERTICAL)
        grid_sizer_traductions = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_outils, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_traductions.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_traductions.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_traductions.AddGrowableRow(0)
        grid_sizer_traductions.AddGrowableCol(0)
        box_traductions.Add(grid_sizer_traductions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_traductions, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Traduirelelogiciel")
        
    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def OnBoutonOk(self, event): 
        # Récupération des paramètres
        nom_langue = self.ctrl_nom_langue.GetValue()
        code_langue = self.ctrl_code_langue.GetValue()
        
        # Récupération des traductions perso
        dictTraductions = self.ctrl_traductions.GetDictTraductionsPerso() 
        
        # Création du fichier de traduction perso
        nomFichier = UTILS_Fichiers.GetRepLang(u"%s.xlang" % code_langue)
        data = {}
        data["###INFOS###"] = {"nom_langue" : nom_langue, "code_langue" : code_langue}
        for texte, traduction in dictTraductions.items():
            data[texte] = traduction
        UTILS_Json.Ecrire(nomFichier, data=data)
        
        # Fermeture
        self.EndModal(wx.ID_OK)
    
    def OnBoutonImporter(self, event):
        from Dlg import DLG_Traduction_importer
##        dlg = DLG_Traduction_importer.Dialog(self, texte=track.texte, traduction=track.traduction)      
##        if dlg.ShowModal() == wx.ID_OK:
##            traduction = dlg.GetTraduction() 
##            track.traduction_perso = traduction
##            track.MAJ() 
##            self.RefreshObject(track)
##        dlg.Destroy() 
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, code="en_GB", nom="English")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
