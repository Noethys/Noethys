#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Utils import UTILS_Dates
import GestionDB
from Ol import OL_Contrats_conso


class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, track=None, listeTracks=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_contrat_periode", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDactivite = IDactivite
        self.track = track
        self.listeTracks = listeTracks

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_dates = wx.StaticText(self, wx.ID_ANY, _(u"Dates :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Prestation
        self.box_prestation_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Prestation"))
        self.label_label_prestation = wx.StaticText(self, wx.ID_ANY, _(u"Label :"))
        self.ctrl_label_prestation = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_date_prestation = wx.StaticText(self, wx.ID_ANY, _(u"Date :"))
        self.ctrl_date_prestation = CTRL_Saisie_date.Date2(self)
        self.label_montant_prestation = wx.StaticText(self, wx.ID_ANY, _(u"Montant :"))
        self.ctrl_montant_prestation = CTRL_Saisie_euros.CTRL(self)

        # Consommations
        self.box_conso_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Consommations"))

        self.listviewAvecFooter = OL_Contrats_conso.ListviewAvecFooter(self, kwargs={"IDactivite" : self.IDactivite}) 
        self.ctrl_conso = self.listviewAvecFooter.GetListview()
        
##        self.bouton_generer_conso = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Magique.png"), wx.BITMAP_TYPE_ANY))
##        self.bouton_ajouter_conso = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
##        self.bouton_modifier_conso = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_conso = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_cocher_conso = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Cocher.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_decocher_conso = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Decocher.png"), wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
##        self.Bind(wx.EVT_BUTTON, self.ctrl_conso.Generer, self.bouton_generer_conso)
##        self.Bind(wx.EVT_BUTTON, self.ctrl_conso.Ajouter, self.bouton_ajouter_conso)
##        self.Bind(wx.EVT_BUTTON, self.ctrl_conso.Modifier, self.bouton_modifier_conso)
        self.Bind(wx.EVT_BUTTON, self.ctrl_conso.Supprimer, self.bouton_supprimer_conso)
        self.Bind(wx.EVT_BUTTON, self.ctrl_conso.CocheTout, self.bouton_cocher_conso)
        self.Bind(wx.EVT_BUTTON, self.ctrl_conso.CocheRien, self.bouton_decocher_conso)
        
        # Init
        if self.track == None :
            self.SetTitle(_(u"Saisie d'une période de facturation"))
        else :
            self.SetTitle(_(u"Modification d'une période de facturation"))
            self.Importation()
        
        if self.track != None :
            self.ctrl_conso.SetDonnees(self.track.listeConso)

        self.__set_properties()
        self.__do_layout()


    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de la période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de la période")))
        self.ctrl_label_prestation.SetToolTip(wx.ToolTip(_(u"Saisissez le label de la prestation")))
        self.ctrl_date_prestation.SetToolTip(wx.ToolTip(_(u"Saisissez la date de la prestation")))
        self.ctrl_montant_prestation.SetToolTip(wx.ToolTip(_(u"Saisissez le montant de la prestation")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
##        self.bouton_generer_conso.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour générer automatiquement des consommations")))
##        self.bouton_ajouter_conso.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une consommation")))
##        self.bouton_modifier_conso.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la consommation sélectionnée")))
        self.bouton_supprimer_conso.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer les consommations sélectionnées ou cochées")))
        self.bouton_cocher_conso.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour tout cocher")))
        self.bouton_decocher_conso.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour tout décocher")))
        self.SetMinSize((500, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(2, 2, 10, 10)
        grid_sizer_dates = wx.FlexGridSizer(1, 4, 5, 5)
        grid_sizer_generalites.Add(self.label_dates, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Prestation
        box_prestation = wx.StaticBoxSizer(self.box_prestation_staticbox, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(3, 2, 5, 10)
        grid_sizer_prestation.Add(self.label_label_prestation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_label_prestation, 0, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_date_prestation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_prestation2 = wx.FlexGridSizer(1, 5, 5, 10)
        grid_sizer_prestation2.Add(self.ctrl_date_prestation, 0, 0, 0)
        grid_sizer_prestation2.Add( (20, 5), 0, 0, 0)
        grid_sizer_prestation2.Add(self.label_montant_prestation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation2.Add(self.ctrl_montant_prestation, 0, 0, 0)
        
        grid_sizer_prestation.Add(grid_sizer_prestation2, 0, 0, 0)
        grid_sizer_prestation.AddGrowableCol(1)
        box_prestation.Add(grid_sizer_prestation, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_prestation, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Consommations
        box_conso = wx.StaticBoxSizer(self.box_conso_staticbox, wx.VERTICAL)
        grid_sizer_conso = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_conso.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        grid_sizer_boutons_conso = wx.FlexGridSizer(5, 1, 5, 5)
##        grid_sizer_boutons_conso.Add(self.bouton_generer_conso, 0, 0, 0)
##        grid_sizer_boutons_conso.Add((10, 10), 0, wx.EXPAND, 0)
##        grid_sizer_boutons_conso.Add(self.bouton_ajouter_conso, 0, 0, 0)
##        grid_sizer_boutons_conso.Add(self.bouton_modifier_conso, 0, 0, 0)
        grid_sizer_boutons_conso.Add(self.bouton_supprimer_conso, 0, 0, 0)
        grid_sizer_boutons_conso.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_conso.Add(self.bouton_cocher_conso, 0, 0, 0)
        grid_sizer_boutons_conso.Add(self.bouton_decocher_conso, 0, 0, 0)        
        grid_sizer_conso.Add(grid_sizer_boutons_conso, 1, wx.EXPAND, 0)
        grid_sizer_conso.AddGrowableRow(0)
        grid_sizer_conso.AddGrowableCol(0)
        box_conso.Add(grid_sizer_conso, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_conso, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def Importation(self):
        self.ctrl_date_debut.SetDate(self.track.date_debut)
        self.ctrl_date_fin.SetDate(self.track.date_fin)
        self.ctrl_label_prestation.SetValue(self.track.label_prestation)
        self.ctrl_date_prestation.SetDate(self.track.date_prestation)
        self.ctrl_montant_prestation.SetMontant(self.track.montant_prestation)
    
    def GetDonnees(self):
        if self.track == None :
            IDprestation, IDfacture, numFacture = None, None, None
        else :
            IDprestation, IDfacture, numFacture = self.track.IDprestation, self.track.IDfacture, self.track.numFacture
        dictValeurs = {
            "IDprestation" : IDprestation,
            "date_debut" : self.ctrl_date_debut.GetDate(),
            "date_fin" : self.ctrl_date_fin.GetDate(),
            "label_prestation" : self.ctrl_label_prestation.GetValue(),
            "date_prestation" : self.ctrl_date_prestation.GetDate(),
            "montant_prestation" : self.ctrl_montant_prestation.GetMontant(),
            "IDfacture" : IDfacture,
            "numFacture" : numFacture,
            "listeConso" : self.ctrl_conso.GetDonnees(),
            }   
        return dictValeurs
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Contrats")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):  
        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"La date de début ne doit pas être supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.ctrl_label_prestation.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le label de la prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.ctrl_date_prestation.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de la prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.ctrl_montant_prestation.GetMontant() == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment appliquer un montant de 0.00 ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse != wx.ID_YES :
                return
        
        # Vérifie que cette période ne chevauche pas une autre période
        for track in self.listeTracks :
            if track != self.track and date_fin >= track.date_debut and date_debut <= track.date_fin :
                dlg = wx.MessageDialog(self, _(u"Création impossible !\n\nCette période chevauche la période existante '%s' (du %s au %s).") % (track.label_prestation, UTILS_Dates.DateDDEnFr(track.date_debut), UTILS_Dates.DateDDEnFr(track.date_fin)), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Fermeture
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
