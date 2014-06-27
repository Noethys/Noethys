#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import CTRL_Saisie_date




class CTRL_Jours(wx.Panel):
    def __init__(self, parent, periode="scolaire"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.periode = periode
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        for jour in self.liste_jours :
            exec("self.check_%s = wx.CheckBox(self, -1, u'%s')" % (jour, jour[0].upper()) )
            exec("self.check_%s.SetToolTipString(u'%s')" % (jour, jour.capitalize()) )
        
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
        self.box_action_staticbox = wx.StaticBox(self, -1, u"Action")
        
        self.label_action = wx.StaticText(self, -1, u"Action :")
        self.radio_date = wx.RadioButton(self, -1, u"Copier le")
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.radio_renitialisation = wx.RadioButton(self, -1, u"Réinitialisation")
        
        self.label_elements = wx.StaticText(self, -1, u"Eléments :")
        self.check_ouvertures = wx.CheckBox(self, -1, u"Ouvertures")
        self.check_places = wx.CheckBox(self, -1, u"Nbre de places max.")
        
        if self.afficheElements == False :
            self.label_elements.Show(False)
            self.check_ouvertures.Show(False)
            self.check_places.Show(False)
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, u"Période d'application")
        
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Jours
        self.box_jours_staticbox = wx.StaticBox(self, -1, u"Jours")
        
        self.label_scolaires = wx.StaticText(self, -1, u"Scolaires :")
        self.ctrl_scolaires = CTRL_Jours(self, "scolaire")
        self.label_vacances = wx.StaticText(self, -1, u"Vacances :")
        self.ctrl_vacances = CTRL_Jours(self, "vacances")
        self.label_feries = wx.StaticText(self, -1, u"Fériés :")
        self.ctrl_feries = wx.CheckBox(self, -1, u"Inclure les jours fériés")

        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

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
        self.ctrl_scolaires.SetJours("0;1;2;3;4")
        self.ctrl_vacances.SetJours("0;1;2;3;4")
        self.ctrl_date.SetFocus()

    def __set_properties(self):
        self.SetTitle(u"Saisie et suppression par lot")
        self.ctrl_date.SetToolTipString(u"Sélectionnez une date modèle. Les éléments de cette date seront copiés vers les dates cibles")
        self.radio_date.SetToolTipString(u"Sélectionnez ce mode pour copier les éléments d'une date donnée")
        self.radio_renitialisation.SetToolTipString(u"Sélectionnez ce mode pour réinitialiser les éléments des dates cibles")
        self.check_ouvertures.SetToolTipString(u"Cochez cette case pour modifier les ouvertures")
        self.check_places.SetToolTipString(u"Cochez cette case pour modifier les nbres de places max. (remplissage)")
        self.ctrl_date_debut.SetToolTipString(u"Sélectionnez une date de début de période cible")
        self.ctrl_date_fin.SetToolTipString(u"Sélectionnez une date de fin de période cible")
        self.ctrl_feries.SetToolTipString(u"Cochez cette case pour modifier également les jours fériés")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Action
        box_action = wx.StaticBoxSizer(self.box_action_staticbox, wx.VERTICAL)
        grid_sizer_action = wx.FlexGridSizer(rows=2, cols=2, vgap=15, hgap=15)
        grid_sizer_elements = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
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
        import UTILS_Aide
        UTILS_Aide.Aide("Calendrier")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        # Validation des données
        if self.radio_date.GetValue() == True :
            date = self.ctrl_date.GetDate()
            if date == None :
                dlg = wx.MessageDialog(self, u"Vous devez sélectionner une date modèle !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date.SetFocus() 
                return
        
        # Elements
        elements = []
        if self.check_ouvertures.GetValue() == True : elements.append("ouvertures")
        if self.check_places.GetValue() == True : elements.append("places")
        if len(elements) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez cocher au moins un élément à modifier (ouvertures/places) !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Période
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, u"Vous devez saisir une date de début de période !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if date_fin == None :
            dlg = wx.MessageDialog(self, u"Vous devez saisir une date de fin de période !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, u"La date de début ne peut pas être supérieure à la date de fin !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        # Jours
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        if len(jours_scolaires) == 0 and len(jours_vacances) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez cocher au moins un jour scolaire ou de vacances !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
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
