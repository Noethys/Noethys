#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import GestionDB
import OL_Mandats


class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDfamille = IDfamille
                
        # Bandeau
        intro = _(u"Saisissez ici les coordonnées bancaires du compte de la famille à débiter afin d'activer le prélèvement automatique.")
        titre = _(u"Prélèvement automatique")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Prelevement.png")
        
        # Activation
        self.box_activation_staticbox = wx.StaticBox(self, -1, _(u"Activation"))
        self.label_activation = wx.StaticText(self, -1, _(u"Prélèvement activé :"))
        self.radio_activation_oui = wx.RadioButton(self, -1, _(u"Oui"), style=wx.RB_GROUP)
        self.radio_activation_non = wx.RadioButton(self, -1, _(u"Non"))
        self.radio_activation_non.SetValue(True) 

        # Mandats
        self.box_mandats_staticbox = wx.StaticBox(self, -1, _(u"Mandats SEPA"))
        self.ctrl_listview = OL_Mandats.ListView(self, id=-1, IDfamille=self.IDfamille, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((20, 20))
        self.ctrl_listview.MAJ()
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_rib = wx.Button(self, -1, _(u"Saisie d'un RIB (Prélèvements nationaux)"))
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRib, self.bouton_rib)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)
        
        # Init contrôles
        self.Importation()

    def __set_properties(self):
        self.radio_activation_oui.SetToolTipString(_(u"Cliquez ici pour activer le prélèvement"))
        self.radio_activation_non.SetToolTipString(_(u"Cliquez ici pour désactiver le prélèvement"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un mandat"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le mandat sélectionné dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le mandat sélectionné dans la iste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_rib.SetToolTipString(_(u"Cliquez ici pour paramétrer un RIB pour les prélèvements nationaux (jusqu'au 1er février 2014)"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((680, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Activation
        box_activation = wx.StaticBoxSizer(self.box_activation_staticbox, wx.VERTICAL)
        grid_sizer_activation = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_activation.Add(self.label_activation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_activation.Add(self.radio_activation_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_activation.Add(self.radio_activation_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_activation.Add(grid_sizer_activation, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_activation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Mandats
        box_mandats = wx.StaticBoxSizer(self.box_mandats_staticbox, wx.VERTICAL)
        grid_sizer_mandats = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_mandats.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_mandats.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_mandats.AddGrowableRow(0)
        grid_sizer_mandats.AddGrowableCol(0)
        box_mandats.Add(grid_sizer_mandats, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_mandats, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_rib, 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, wx.EXPAND, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Rglements1")

    def Ajouter(self, event):
        self.ctrl_listview.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)

    def Importation(self):
        """ Importation des données """
        if self.IDfamille == None :
            return
        DB = GestionDB.DB()
        req = """SELECT IDfamille, prelevement_activation
        FROM familles 
        WHERE IDfamille=%d;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        temp, activation = listeDonnees[0]
        
        if activation == 1 :
            self.radio_activation_oui.SetValue(True)
        

    def OnBoutonFermer(self, event):
        # Récupération des données
        activation = self.radio_activation_oui.GetValue()

        # Vérification des données saisies
        if activation == True :
            if len(self.ctrl_listview.donnees) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins un mandat pour pouvoir activer le prélèvement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        else :
            # Pas d'activation
            dlg = wx.MessageDialog(None, _(u"Vous confirmez que vous ne souhaitez pas activer le prélèvement automatique ?"), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Sauvegarde
        if activation == True :
            activation = 1
        else :
            activation = None
            
        DB = GestionDB.DB()
        DB.ReqMAJ("familles", [("prelevement_activation", activation),], "IDfamille", self.IDfamille)
        DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)

    def OnBoutonRib(self, event):
        import DLG_Saisie_rib
        dlg = DLG_Saisie_rib.Dialog(self, IDfamille=self.IDfamille) 
        dlg.ShowModal() 
        dlg.Destroy()
        
        
        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=14)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
