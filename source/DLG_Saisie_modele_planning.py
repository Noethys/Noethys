#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import OL_Contrats_planning_elements
import OL_Activites


class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDmodele = IDmodele
        
        # Init activité
        if self.IDmodele != None :
            DB = GestionDB.DB()
            req = """SELECT IDmodele, IDactivite, nom, donnees 
            FROM modeles_plannings
            WHERE IDmodele=%d;""" % self.IDmodele
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                IDactivite = listeDonnees[0][1]

        self.IDactivite = IDactivite

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Planning
        self.box_planning_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Planning"))
        self.ctrl_planning = OL_Contrats_planning_elements.ListView(self, id=-1, IDactivite=self.IDactivite, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init
        self.ctrl_planning.MAJ() 
        
        # Importation
        if self.IDmodele == None :
            self.SetTitle(_(u"Saisie d'un modèle de planning"))
        else :
            self.SetTitle(_(u"Modification d'un modèle de planning"))
            self.Importation() 


    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour ce modèle"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un paramètre"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier un paramètre"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer un paramètre"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((600, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(2, 2, 10, 10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)

        # Planning
        box_planning = wx.StaticBoxSizer(self.box_planning_staticbox, wx.VERTICAL)
        grid_sizer_planning = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_planning.Add(self.ctrl_planning, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_planning.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_planning.AddGrowableRow(0)
        grid_sizer_planning.AddGrowableCol(0)
        box_planning.Add(grid_sizer_planning, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_planning, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnRadioPlanning(self, event):
        self.ctrl_modele.Enable(self.radio_modele.GetValue())
        self.bouton_modele.Enable(self.radio_modele.GetValue())
        self.ctrl_planning_detail.Enable(self.radio_planning_detail.GetValue())
        self.bouton_ajouter.Enable(self.radio_planning_detail.GetValue())
        self.bouton_modifier.Enable(self.radio_planning_detail.GetValue())
        self.bouton_supprimer.Enable(self.radio_planning_detail.GetValue())
        
    def OnBoutonModele(self, event):  
        print "Event handler 'OnBoutonModele' not implemented!"
        event.Skip()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)   

    def OnBoutonOk(self, event):
        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.ctrl_planning.GetDonnees()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un élément de planning !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Sauvegarde
        self.Sauvegarde() 
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDmodele(self):
        return self.IDmodele
    
    def Sauvegarde(self):
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDactivite", self.IDactivite ),
            ("nom", self.ctrl_nom.GetValue()),
            ("donnees", self.ctrl_planning.GetElementsStr() ),
            ]
        if self.IDmodele == None :
            self.IDmodele = DB.ReqInsert("modeles_plannings", listeDonnees)
        else :
            DB.ReqMAJ("modeles_plannings", listeDonnees, "IDmodele", self.IDmodele)
        DB.Close() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT nom, donnees 
        FROM modeles_plannings
        WHERE IDmodele=%d;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return
        nom, donnees = listeDonnees[0]
        self.ctrl_nom.SetValue(nom)
        self.ctrl_planning.SetElementsStr(donnees)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog_selection_activite(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.SetTitle(_(u"Sélection d'une activité"))
        
        self.label_intro = wx.StaticText(self, wx.ID_ANY, _(u"Sélectionnez l'activité pour laquelle vous souhaitez créer un modèle de planning puis cliquez sur OK :"))
        self.ctrl_activites = OL_Activites.ListView(self, modificationAutorisee=False, id=-1, style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_activites.SetMinSize((150, 50))
        self.ctrl_activites.MAJ() 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((600, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        grid_sizer_base.Add(self.label_intro, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        grid_sizer_base.Add(self.ctrl_activites, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide(u"")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):  
        if len(self.ctrl_activites.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.EndModal(wx.ID_OK)

    def GetActivite(self):
        return self.ctrl_activites.Selection()[0].IDactivite

        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=1, IDactivite=1)
##    dialog_1 = Dialog_selection_activite(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    print dialog_1.GetResultats() 
    app.MainLoop()
