#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB

import CTRL_Droits



class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None, defaut=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.defaut = defaut
        self.IDmodele = IDmodele
        
        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Droits
        self.staticbox_droits_staticbox = wx.StaticBox(self, -1, _(u"Droits"))
        self.ctrl_droits = CTRL_Droits.CTRL(self, IDmodele=IDmodele)
        self.ctrl_droits.MAJ() 
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()


        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDmodele != None :
            self.SetTitle(_(u"Modification d'un modèle de droits"))
            self.Importation()
        else:
            self.SetTitle(_(u"Saisie d'un modèle de droits"))

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour ce modèle"))
        self.ctrl_description.SetToolTipString(_(u"Saisissez une description pour ce modèle"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((670, 580))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_description, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Droits
        staticbox_droits = wx.StaticBoxSizer(self.staticbox_droits_staticbox, wx.VERTICAL)
        staticbox_droits.Add(self.ctrl_droits, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_droits, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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
                
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Modelesdedroits")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):     
        # Vérification des données
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce modèle !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return        
        
        # Description
        description = self.ctrl_description.GetValue()
        if description == "" :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir saisir de description pour ce modèle ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return
            dlg.Destroy()
                
        # Sauvegarde du modèle
        DB = GestionDB.DB()
        listeDonnees = [("nom", nom), ("observations", description), ("defaut", self.defaut)]
        if self.IDmodele == None :
            self.IDmodele = DB.ReqInsert("modeles_droits", listeDonnees)
        else:
            DB.ReqMAJ("modeles_droits", listeDonnees, "IDmodele", self.IDmodele)
        DB.Close()
        
        # Sauvegarde des droits
        self.ctrl_droits.Sauvegarde(IDmodele=self.IDmodele) 
        
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDmodele(self):
        return self.IDmodele

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, observations, defaut
        FROM modeles_droits
        WHERE IDmodele=%d;
        """ % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDmodele, nom, observations, defaut = listeDonnees[0]

        self.ctrl_nom.SetValue(nom)
        self.ctrl_description.SetValue(observations)
        self.defaut = defaut
        
    
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
