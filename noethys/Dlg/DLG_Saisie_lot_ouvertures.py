#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date




class CTRL_Jours(wx.Panel):
    def __init__(self, parent, periode="scolaire"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.periode = periode
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        for jour in self.liste_jours :
            exec("self.check_%s = wx.CheckBox(self, -1, u'%s')" % (jour, jour[0].upper()) )
            exec("self.check_%s.SetToolTip(wx.ToolTip(u'%s'))" % (jour, jour.capitalize()) )
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        for jour in self.liste_jours :
            exec("grid_sizer_base.Add(self.check_%s, 0, 0, 0)" % jour)
                        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def GetJours(self):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            exec("etat = self.check_%s.GetValue()" % jour)
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
    
    def SetJours(self, texteJours=""):
        if texteJours == None or len(texteJours) == 0 :
            return

        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = "True"
            else :
                etat = "False"
            exec("self.check_%s.SetValue(%s)" % (jour, etat))
            index += 1
            
        
        
        
# ---------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, afficheElements=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.afficheElements = afficheElements
        
        # Action
        self.box_action_staticbox = wx.StaticBox(self, -1, _(u"Action"))
        
        self.label_action = wx.StaticText(self, -1, _(u"Action :"))
        self.radio_date = wx.RadioButton(self, -1, _(u"Copier le"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.radio_renitialisation = wx.RadioButton(self, -1, _(u"Réinitialisation"))
        
        self.label_elements = wx.StaticText(self, -1, _(u"Eléments :"))
        self.check_ouvertures = wx.CheckBox(self, -1, _(u"Ouvertures"))
        self.check_places = wx.CheckBox(self, -1, _(u"Nbre de places max."))
        self.check_evenements = wx.CheckBox(self, -1, _(u"Evènements"))

        if self.afficheElements == False :
            self.label_elements.Show(False)
            self.check_ouvertures.Show(False)
            self.check_places.Show(False)
            self.check_evenements.Show(False)
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période d'application"))
        
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Jours
        self.box_jours_staticbox = wx.StaticBox(self, -1, _(u"Jours"))
        
        self.label_scolaires = wx.StaticText(self, -1, _(u"Scolaires :"))
        self.ctrl_scolaires = CTRL_Jours(self, "scolaire")
        self.label_vacances = wx.StaticText(self, -1, _(u"Vacances :"))
        self.ctrl_vacances = CTRL_Jours(self, "vacances")
        self.label_feries = wx.StaticText(self, -1, _(u"Fériés :"))
        self.ctrl_feries = wx.CheckBox(self, -1, _(u"Inclure les jours fériés"))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_date)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_renitialisation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init
        self.check_ouvertures.SetValue(True)
        self.check_places.SetValue(True)
        self.check_evenements.SetValue(True)
##        self.ctrl_scolaires.SetJours("0;1;2;3;4")
##        self.ctrl_vacances.SetJours("0;1;2;3;4")
        self.ctrl_date.SetFocus()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie et suppression par lot"))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date modèle. Les éléments de cette date seront copiés vers les dates cibles")))
        self.radio_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour copier les éléments d'une date donnée")))
        self.radio_renitialisation.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour réinitialiser les éléments des dates cibles")))
        self.check_ouvertures.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier les ouvertures")))
        self.check_places.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier les nbres de places max. (remplissage)")))
        self.check_evenements.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier les évènements (uniquement pour les unités de type évènementielles")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de début de période cible")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de fin de période cible")))
        self.ctrl_feries.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier également les jours fériés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Action
        box_action = wx.StaticBoxSizer(self.box_action_staticbox, wx.VERTICAL)
        grid_sizer_action = wx.FlexGridSizer(rows=2, cols=2, vgap=15, hgap=15)
        grid_sizer_elements = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_action2 = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_action.Add(self.label_action, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_date.Add(self.radio_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_action2.Add(grid_sizer_date, 1, wx.EXPAND, 0)
        grid_sizer_action2.Add(self.radio_renitialisation, 0, 0, 0)
        grid_sizer_action2.AddGrowableCol(0)
        grid_sizer_action.Add(grid_sizer_action2, 1, wx.EXPAND, 0)
        grid_sizer_action.Add(self.label_elements, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_elements.Add(self.check_ouvertures, 0, 0, 0)
        grid_sizer_elements.Add(self.check_places, 0, 0, 0)
        grid_sizer_elements.Add(self.check_evenements, 0, 0, 0)
        grid_sizer_elements.AddGrowableCol(0)
        grid_sizer_action.Add(grid_sizer_elements, 1, wx.EXPAND, 0)
        grid_sizer_action.AddGrowableCol(1)
        box_action.Add(grid_sizer_action, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_action, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Périodes
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_periode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Jours
        box_jours = wx.StaticBoxSizer(self.box_jours_staticbox, wx.VERTICAL)
        grid_sizer_jours = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_jours.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_scolaires, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_vacances, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_feries, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_feries, 0, wx.EXPAND, 0)
        grid_sizer_jours.AddGrowableCol(1)
        box_jours.Add(grid_sizer_jours, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_jours, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioAction(self, event):
        self.ctrl_date.Enable(self.radio_date.GetValue())

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Calendrier")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        # Validation des données
        if self.radio_date.GetValue() == True :
            date = self.ctrl_date.GetDate()
            if date == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une date modèle !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date.SetFocus() 
                return
        
        # Elements
        elements = []
        if self.check_ouvertures.GetValue() == True : elements.append("ouvertures")
        if self.check_places.GetValue() == True : elements.append("places")
        if self.check_evenements.GetValue() == True: elements.append("evenements")
        if len(elements) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un élément à modifier (ouvertures/places) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Période
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de début ne peut pas être supérieure à la date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        # Jours
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        if len(jours_scolaires) == 0 and len(jours_vacances) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un jour scolaire ou de vacances !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def SetDate(self, date=None):
        try :
            self.ctrl_date.SetDate(date)
        except :
            pass
        
    def GetMode(self):
        if self.radio_date.GetValue() == True :
            return "date"
        else :
            return "reinit"
    
    def GetDate(self):
        if self.radio_date.GetValue() == True :
            return self.ctrl_date.GetDate()
        else :
            return None
    
    def GetElements(self):
        elements = []
        if self.check_ouvertures.GetValue() == True : elements.append("ouvertures")
        if self.check_places.GetValue() == True : elements.append("places")
        if self.check_evenements.GetValue() == True: elements.append("evenements")
        return elements

    def GetPeriode(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        return date_debut, date_fin

    def GetJours(self):
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        return jours_scolaires, jours_vacances

    def GetFeries(self):
        return self.ctrl_feries.GetValue() 

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, afficheElements=True)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
