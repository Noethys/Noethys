#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Selection_activites
import UTILS_Config



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Activit�s
        self.box_activites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"S�lection des activit�s"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self, afficheToutes=True)
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Options"))
        self.label_tri = wx.StaticText(self, wx.ID_ANY, _(u"Crit�re de tri :"))
        self.ctrl_tri = wx.Choice(self, wx.ID_ANY, choices=[_(u"Nom d'activit�"), _(u"Nombre d'inscrits"), _(u"Nombre de places max"), _(u"Date de d�but d'activit�"), _(u"Date de fin d'activit�")])
        self.ctrl_tri.SetSelection(0)

        self.label_sens = wx.StaticText(self, wx.ID_ANY, _(u"Sens de tri :"))
        self.ctrl_sens = wx.Choice(self, wx.ID_ANY, choices=[_(u"Croissant"), _(u"D�croissant")])
        self.ctrl_sens.SetSelection(0)

        self.label_alerte = wx.StaticText(self, wx.ID_ANY, _(u"Seuil d'alerte :"))
        self.ctrl_alerte = wx.SpinCtrl(self, wx.ID_ANY, "", min=0, max=100)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Importation
        self.Importation() 

    def __set_properties(self):
        self.SetTitle(_(u"Param�tres d'affichage des inscriptions"))
        self.ctrl_tri.SetToolTipString(_(u"S�lectionner un crit�re de tri"))
        self.ctrl_sens.SetToolTipString(_(u"S�lectionner un sens de tri"))
        self.ctrl_alerte.SetToolTipString(_(u"Saisissez une valeur de seuil d'alerte. Noethys signale ainsi lorsque le nombre de places restantes est �gal ou inf�rieur � cette valeur"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((500, 570))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        box_activites.Add(self.ctrl_activites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_activites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)

        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(3, 2, 10, 10)
        grid_sizer_options.Add(self.label_tri, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_tri, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_sens, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_sens, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_alerte, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_alerte, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(1)
        box_options.Add(grid_sizer_options, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):  
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)
    
    def Importation(self):
        # Activit�s
        parametres = UTILS_Config.GetParametre("nbre_inscrits_parametre_activites", defaut=None)
        if parametres != None :
            code, liste = parametres.split("###")
            if liste != "" :
                listeID = []
                for ID in liste.split(";") :
                    listeID.append(int(ID))
                if code == "liste_groupes_activites" :
                    self.ctrl_activites.SetValeurs("groupes", listeID) 
                if code == "liste_activites" :
                    self.ctrl_activites.SetValeurs("activites", listeID) 
        
        # Options
        self.ctrl_tri.SetSelection(UTILS_Config.GetParametre("nbre_inscrits_parametre_tri", 3))
        self.ctrl_sens.SetSelection(UTILS_Config.GetParametre("nbre_inscrits_parametre_sens", 1))
        self.ctrl_alerte.SetValue(UTILS_Config.GetParametre("nbre_inscrits_parametre_alerte", 5))

    def OnBoutonOk(self, event):  
        if self.ctrl_activites.Validation() == False :
            return
        
        # M�morisation des activit�s
        mode, listeIDtemp = self.ctrl_activites.GetValeurs() 
        listeID = []
        for ID in listeIDtemp :
            listeID.append(str(ID))
        if mode == "toutes" : 
            parametre = None
        if mode == "groupes" : 
            parametre = "liste_groupes_activites###%s" % ";".join(listeID)
        if mode == "activites" : 
            parametre = "liste_activites###%s" % ";".join(listeID)
        UTILS_Config.SetParametre("nbre_inscrits_parametre_activites", parametre)
        
        # Options
        UTILS_Config.SetParametre("nbre_inscrits_parametre_tri", self.ctrl_tri.GetSelection())
        UTILS_Config.SetParametre("nbre_inscrits_parametre_sens", self.ctrl_sens.GetSelection())
        UTILS_Config.SetParametre("nbre_inscrits_parametre_alerte", int(self.ctrl_alerte.GetValue()))
        
        self.EndModal(wx.ID_OK)
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()


