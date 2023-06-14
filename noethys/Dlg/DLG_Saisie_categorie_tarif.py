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
import GestionDB


class CTRL_Villes(wx.ListBox):
    def __init__(self, parent, IDcategorie_tarif=None):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.IDcategorie_tarif = IDcategorie_tarif
        self.listeInitiale = []
        self.listeDonnees = []
        if self.IDcategorie_tarif != None :
            self.Importation() 
            self.MAJ() 
    
    def MAJ(self):
        listeItems = []
        for dictValeurs in self.listeDonnees :
            label = u"%s (%s)" % (dictValeurs["nom"], dictValeurs["cp"])
            listeItems.append(label)
        self.Set(listeItems)
    
    def Ajouter(self):
        from Dlg import DLG_Villes
        dlg = DLG_Villes.Dialog(None, modeImportation=True)
        if dlg.ShowModal() == wx.ID_OK:
            cp, nom = dlg.GetVille()
            valeurs = { "IDville" : None, "cp" : cp, "nom" : nom}
            self.listeDonnees.append(valeurs)
            self.MAJ() 
        dlg.Destroy()

    def Supprimer(self):
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une ville dans la liste !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.listeDonnees.pop(index)
        self.MAJ() 
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDville, cp, nom
        FROM categories_tarifs_villes 
        WHERE IDcategorie_tarif=%d
        ORDER BY nom; """ % self.IDcategorie_tarif
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.listeDonnees = []
        self.listeInitiale = []
        for IDville, cp, nom in listeDonnees :
            valeurs = { "IDville" : IDville, "cp" : cp, "nom" : nom }
            self.listeDonnees.append(valeurs)
            self.listeInitiale.append(IDville)
            
    def Sauvegarde(self):
        DB = GestionDB.DB()
        listeIDvilles = []
        # Enregistrement d'une nouvelle ville :
        for dictValeurs in self.listeDonnees :
            if dictValeurs["IDville"] == None :
                listeDonnees = [
                        ("IDcategorie_tarif", self.IDcategorie_tarif ),
                        ("cp", dictValeurs["cp"]),
                        ("nom", dictValeurs["nom"]),
                        ]
                IDville = DB.ReqInsert("categories_tarifs_villes", listeDonnees)
            else:
                listeIDvilles.append(dictValeurs["IDville"])
        # Suppression des anciennes villes :
        for IDville in self.listeInitiale :
            if IDville not in listeIDvilles :
                DB.ReqDEL("categories_tarifs_villes", "IDville", IDville)
        DB.Close() 
        


class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, IDcategorie_tarif=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDcategorie_tarif = IDcategorie_tarif
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de la catégorie"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.ctrl_checkVille = wx.CheckBox(self, -1, u"")
        self.label_ville = wx.StaticText(self, -1, _(u"Lors d'une inscription, attribuer par défaut cette catégorie aux\nindividus dont la ville de résidence figure dans la liste suivante :"))
        self.ctrl_villes = CTRL_Villes(self, self.IDcategorie_tarif)
        self.bouton_villes_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_villes_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckVille, self.ctrl_checkVille)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonVilles_Ajouter, self.bouton_villes_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonVilles_Supprimer, self.bouton_villes_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDcategorie_tarif != None :
            self.Importation() 
            
        self.OnCheckVille(None)
        

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une catégorie de tarif"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour cette catégorie")))
        self.bouton_villes_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une ville dans la liste")))
        self.bouton_villes_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour enlever la ville sélectionnée de la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((420, 350))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_villes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_villes = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_options.Add(self.ctrl_checkVille, 0, 0, 0)
        grid_sizer_options.Add(self.label_ville, 0, 0, 0)
        grid_sizer_options.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_villes.Add(self.ctrl_villes, 0, wx.EXPAND, 0)
        grid_sizer_boutons_villes.Add(self.bouton_villes_ajouter, 0, 0, 0)
        grid_sizer_boutons_villes.Add(self.bouton_villes_supprimer, 0, 0, 0)
        grid_sizer_villes.Add(grid_sizer_boutons_villes, 1, wx.EXPAND, 0)
        grid_sizer_villes.AddGrowableRow(0)
        grid_sizer_villes.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_villes, 1, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableRow(1)
        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnCheckVille(self, event): 
        if self.ctrl_checkVille.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_villes.Enable(etat)
        self.bouton_villes_ajouter.Enable(etat)
        self.bouton_villes_supprimer.Enable(etat)

    def OnBoutonVilles_Ajouter(self, event):
        self.ctrl_villes.Ajouter()

    def OnBoutonVilles_Supprimer(self, event):
        self.ctrl_villes.Supprimer() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Tarification")
    
    def GetIDcategorieTarif(self):
        return self.IDcategorie_tarif

    def OnBoutonOk(self, event):
        # Vérification des données
        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette catégorie !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        if self.ctrl_checkVille.GetValue() == True :
            if len(self.ctrl_villes.listeDonnees) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez saisie aucune ville !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [("IDactivite", self.IDactivite), ("nom", self.ctrl_nom.GetValue()), ]
        if self.IDcategorie_tarif == None :
            self.IDcategorie_tarif = DB.ReqInsert("categories_tarifs", listeDonnees)
            self.ctrl_villes.IDcategorie_tarif = self.IDcategorie_tarif
        else:
            DB.ReqMAJ("categories_tarifs", listeDonnees, "IDcategorie_tarif", self.IDcategorie_tarif)
        DB.Close() 
        self.ctrl_villes.Sauvegarde()
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT nom
        FROM categories_tarifs 
        WHERE IDcategorie_tarif=%d; """ % self.IDcategorie_tarif
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        # Nom
        nom = listeDonnees[0][0]
        self.ctrl_nom.SetValue(nom)
        # Villes associées
        self.ctrl_villes.Importation() 
        if len(self.ctrl_villes.listeDonnees) > 0 :
            self.ctrl_checkVille.SetValue(True)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1, IDcategorie_tarif=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
