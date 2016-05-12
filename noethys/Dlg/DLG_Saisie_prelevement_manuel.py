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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Titulaires
import GestionDB
from Ctrl import CTRL_Saisie_euros


class CTRL_Famille(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.SetMinSize((100, -1))
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        titulaires = UTILS_Titulaires.GetTitulaires() 
        listeFamilles = []
        for IDfamille, dictTemp in titulaires.iteritems() :
            listeFamilles.append((dictTemp["titulairesSansCivilite"], IDfamille, dictTemp["IDcompte_payeur"]))
        listeFamilles.sort()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "IDfamille" : 0, "nom" : _(u"Inconnue"), "IDcompte_payeur" : 0 }
        index = 1
        for nom, IDfamille, IDcompte_payeur in listeFamilles :
            self.dictDonnees[index] = { "IDfamille" : IDfamille, "nom " : nom, "IDcompte_payeur" : IDcompte_payeur}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetIDfamille(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["IDfamille"] == ID :
                 self.SetSelection(index)

    def GetIDfamille(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["IDfamille"]
    
    def GetIDcompte_payeur(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["IDcompte_payeur"]

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, libelle=u"", montant=0.0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent   
        
##        self.label_intro = wx.StaticText(self, -1, _(u"Remarque : Les prélèvements manuels ne peuvent pas être réglés automatiquement."))
##        self.label_intro.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
##        self.label_intro.SetForegroundColour((100, 100, 100)) 
        
        # Famille
        self.staticbox_famille_staticbox = wx.StaticBox(self, -1, _(u"Famille"))
        self.label_famille = wx.StaticText(self, -1, _(u"Titulaires :"))
        self.ctrl_famille = CTRL_Famille(self)
        
        # Paramètres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.label_libelle = wx.StaticText(self, -1, _(u"Libellé :"))
        self.ctrl_libelle = wx.TextCtrl(self, -1, u"")
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init contrôles
        self.ctrl_famille.SetIDfamille(IDfamille)
        self.ctrl_libelle.SetValue(libelle)
        self.ctrl_montant.SetMontant(montant)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un prélèvement manuel"))
        self.ctrl_famille.SetToolTipString(_(u"Sélectionnez la famille"))
        self.ctrl_libelle.SetToolTipString(_(u"Saisissez ici le libellé du prélèvement"))
        self.ctrl_montant.SetToolTipString(_(u"Saisissez ici le montant du prélèvement"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
##        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        staticbox_famille = wx.StaticBoxSizer(self.staticbox_famille_staticbox, wx.VERTICAL)
        grid_sizer_famille = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_famille.Add(self.label_famille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_famille.Add(self.ctrl_famille, 0, wx.EXPAND, 0)
        grid_sizer_famille.AddGrowableCol(1)
        staticbox_famille.Add(grid_sizer_famille, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_famille, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_parametres.Add(self.label_libelle, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_libelle, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_parametres.AddGrowableCol(1)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        self.SetSize((500, -1))
        self.Layout()
        self.CenterOnScreen() 
    
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
    
    def GetIDfamille(self):
        return self.ctrl_famille.GetIDfamille()
    
    def GetIDcompte_payeur(self):
        return self.ctrl_famille.GetIDcompte_payeur()
    
    def GetLibelle(self):
        return self.ctrl_libelle.GetValue() 
    
    def GetMontant(self):
        return self.ctrl_montant.GetMontant()     
    
    def OnBoutonOk(self, event): 
        if self.GetIDfamille() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_famille.SetFocus()
            return
        if self.GetLibelle() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un libellé pour ce prélèvement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_libelle.SetFocus()
            return
        if self.GetMontant() == None or self.GetMontant() == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant pour ce prélèvement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
