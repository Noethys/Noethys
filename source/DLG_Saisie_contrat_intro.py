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
import OL_Inscriptions
import GestionDB
import cPickle
import UTILS_Dates
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")




class CTRL_Modeles(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDactivite = None
        self.MAJ() 
    
    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 
        
    def MAJ(self, IDligne=0):
        ID = self.GetID() 
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        self.SetID(ID)
                                        
    def GetListeDonnees(self):
        self.dictDonnees = {}
        if self.IDactivite == None : 
            return []
        db = GestionDB.DB()
        req = """SELECT IDmodele, modeles_contrats.nom, modeles_contrats.IDactivite, modeles_contrats.date_debut, modeles_contrats.date_fin, IDtarif, donnees
        FROM modeles_contrats
        LEFT JOIN activites ON activites.IDactivite = modeles_contrats.IDactivite
        WHERE modeles_contrats.IDactivite=%d
        ORDER BY modeles_contrats.date_debut;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        index = 0
        for IDmodele, nom, IDactivite, date_debut, date_fin, IDtarif, donnees in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            donnees = cPickle.loads(str(donnees))
            self.dictDonnees[index] = { "ID" : IDmodele, "nom " : nom, "IDactivite" : IDactivite, "date_debut" : date_debut, "date_fin" : date_fin, "IDtarif" : IDtarif, "donnees" : donnees}
            label = _(u"%s - du %s au %s") % (nom, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin))
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetDonnees(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["donnees"]



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Contrats(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDactivite = None
        self.MAJ() 
        self.Select(0)
    
    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 
        
    def MAJ(self, IDligne=0):
        ID = self.GetID() 
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        self.SetID(ID)
                                        
    def GetListeDonnees(self):
        self.dictDonnees = {}
        if self.IDactivite == None : 
            return []
        DB = GestionDB.DB()
        req = """SELECT contrats.IDcontrat, contrats.date_debut, contrats.date_fin, activites.nom, SUM(prestations.montant) as total, individus.nom, individus.prenom
        FROM contrats 
        LEFT JOIN inscriptions ON inscriptions.IDinscription=contrats.IDinscription
        LEFT JOIN activites ON activites.IDactivite=inscriptions.IDactivite
        LEFT JOIN prestations ON prestations.IDcontrat = contrats.IDcontrat
        LEFT JOIN individus ON individus.IDindividu = contrats.IDindividu
        WHERE inscriptions.IDactivite=%d
        GROUP BY contrats.IDcontrat
        ORDER BY contrats.date_debut; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        index = 0
        for IDcontrat, date_debut, date_fin, nomActivite, montant, nomIndividu, prenomIndividu in listeDonnees :
            if prenomIndividu == None : prenomIndividu = ""
            nomIndividu = u"%s %s" % (nomIndividu, prenomIndividu)
            if type(montant) != float :
                montant = 0.0
            montantStr = u"%.2f %s" % (montant, SYMBOLE)
            self.dictDonnees[index] = { "ID" : IDcontrat, "nomIndividu " : nomIndividu}
            label = _(u"%s - %s - %s - du %s au %s") % (nomIndividu, nomActivite, montantStr, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin))
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None, dictFamillesRattachees=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_contrat_intro", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        
        # Activité
        self.box_activite_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Sélection de l'activité"))
        self.ctrl_inscriptions = OL_Inscriptions.ListView(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees, activeDoubleclick=False, id=-1, name="OL_inscriptions", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_inscriptions.SetMinSize((20, 20)) 
        self.ctrl_inscriptions.MAJ() 

        # Options
        self.box_options_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Options"))
        self.radio_vierge = wx.RadioButton(self, wx.ID_ANY, _(u"Contrat vierge"), style=wx.RB_GROUP)
        self.radio_modele = wx.RadioButton(self, wx.ID_ANY, _(u"Utiliser le modèle de contrat :"))
        self.ctrl_modele = CTRL_Modeles(self)
        self.bouton_modeles = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.radio_contrat = wx.RadioButton(self, wx.ID_ANY, _(u"Copier le contrat :"))
        self.ctrl_contrat = CTRL_Contrats(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_vierge)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_modele)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_modeles)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_contrat)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectionActivite, self.ctrl_inscriptions)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnSelectionActivite, self.ctrl_inscriptions)
        
        # Init
        self.OnRadio(None)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un nouveau contrat"))
        self.ctrl_inscriptions.SetToolTipString(_(u"Sélectionnez une activité pour laquelle créer le contrat"))
        self.radio_vierge.SetToolTipString(_(u"Cliquez ici pour créer un contrat vierge"))
        self.radio_modele.SetToolTipString(_(u"Cliquez ici pour créer un contrat basé sur un modèle de contrat"))
        self.ctrl_modele.SetToolTipString(_(u"Sélectionnez un modèle de contrat dans la liste"))
        self.bouton_modeles.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des contrats"))
        self.radio_contrat.SetToolTipString(_(u"Cliquez ici pour créer un contrat basé sur un autre contrat"))
        self.ctrl_contrat.SetToolTipString(_(u"Sélectionnez le contrat à copier"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((600, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        # Activité
        box_activite = wx.StaticBoxSizer(self.box_activite_staticbox, wx.VERTICAL)
        box_activite.Add(self.ctrl_inscriptions, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_activite, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(6, 1, 10, 10)
        grid_sizer_modele = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_options.Add(self.radio_vierge, 0, 0, 0)
        grid_sizer_options.Add(self.radio_modele, 0, 0, 0)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_modele.Add(self.bouton_modeles, 0, 0, 0)
        grid_sizer_modele.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_modele, 1, wx.LEFT | wx.EXPAND, 18)
        grid_sizer_options.Add(self.radio_contrat, 0, 0, 0)
        grid_sizer_options.Add(self.ctrl_contrat, 0, wx.LEFT | wx.EXPAND, 18)
        grid_sizer_options.AddGrowableCol(0)
        box_options.Add(grid_sizer_options, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Contrats")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnRadio(self, event): 
        self.ctrl_modele.Enable(self.radio_modele.GetValue())
        self.bouton_modeles.Enable(self.radio_modele.GetValue())
        self.ctrl_contrat.Enable(self.radio_contrat.GetValue())

    def OnBoutonModeles(self, event):  # wxGlade: MyDialog.<event_handler>
        ID = self.ctrl_modele.GetID() 
        import DLG_Modeles_contrats
        dlg = DLG_Modeles_contrats.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_modele.MAJ() 
        self.ctrl_modele.SetID(ID)
    
    def OnSelectionActivite(self, event):
        IDactivite = self.ctrl_inscriptions.Selection()[0].IDactivite
        self.ctrl_modele.SetActivite(IDactivite)
        self.ctrl_contrat.SetActivite(IDactivite)
        if IDactivite == None :
            self.radio_vierge.SetValue(False)
        
    def OnBoutonOk(self, event): 
        if len(self.ctrl_inscriptions.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.radio_modele.GetValue() == True and self.ctrl_modele.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.radio_contrat.GetValue() == True and self.ctrl_contrat.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un contrat dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.EndModal(wx.ID_OK)

    def GetInscription(self):
        IDinscription = self.ctrl_inscriptions.Selection()[0].IDinscription
        return IDinscription
    
    def GetOptions(self):
        if self.radio_vierge.GetValue() == True :
            return None
        if self.radio_modele.GetValue() == True :
            return {"type" : "modele", "IDmodele" : self.ctrl_modele.GetID()}
        if self.radio_contrat.GetValue() == True :
            return {"type" : "contrat", "IDcontrat" : self.ctrl_contrat.GetID()}
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDindividu=46)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
