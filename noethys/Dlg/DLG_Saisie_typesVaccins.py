#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB


class CheckListBox(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
# -----------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.SetTitle(_(u"Saisie d'un vaccin"))  
        
        self.sizer_nom_staticbox = wx.StaticBox(self, -1, _(u"1. Nom du vaccin"))
        self.sizer_duree_staticbox = wx.StaticBox(self, -1, _(u"2. Durée de validité"))
        self.sizer_maladies_staticbox = wx.StaticBox(self, -1, _(u"3. Maladies associées"))
        
        self.label_nom = wx.StaticText(self, -1, "Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.radio_duree_1 = wx.RadioButton(self, -1, _(u"Validité illimitée"), style=wx.RB_GROUP)
        self.radio_duree_2 = wx.RadioButton(self, -1, _(u"Validité limitée : "))
        self.label_jours = wx.StaticText(self, -1, _(u"Jours :"))
        self.spin_jours = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.spin_mois = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_annees = wx.StaticText(self, -1, _(u"Années :"))
        self.spin_annees = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.ctrl_maladies = CheckListBox(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_2)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        self.OnRadioDuree(None)
        
        self.RemplirCtrlMaladies()


    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici un nom de vaccin. Par exemple : 'DT Polio'"))
        self.radio_duree_1.SetToolTipString(_(u"Sélectionnez 'Illimitée' si le vaccin est valable à vie"))
        self.radio_duree_2.SetToolTipString(_(u"Sélectionnez 'Limitée' si vous pouvez définir une durée pour ce vaccin"))
        self.spin_jours.SetMinSize((60, -1))
        self.spin_mois.SetMinSize((60, -1))
        self.spin_annees.SetMinSize((60, -1))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))
        self.SetMinSize((400, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        sizer_diplomes = wx.StaticBoxSizer(self.sizer_maladies_staticbox, wx.VERTICAL)
        grid_sizer_diplomes = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        sizer_duree = wx.StaticBoxSizer(self.sizer_duree_staticbox, wx.VERTICAL)
        grid_sizer_duree1 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree2 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree3 = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        sizer_nom = wx.StaticBoxSizer(self.sizer_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        sizer_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_duree1.Add(self.radio_duree_1, 0, 0, 0)
        grid_sizer_duree2.Add(self.radio_duree_2, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree3.Add(self.spin_jours, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_mois, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_annees, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_annees, 0, 0, 0)
        grid_sizer_duree2.Add(grid_sizer_duree3, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_duree1.Add(grid_sizer_duree2, 1, wx.EXPAND, 0)
        sizer_duree.Add(grid_sizer_duree1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_duree, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_diplomes.Add(self.ctrl_maladies, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_diplomes.AddGrowableRow(0)
        grid_sizer_diplomes.AddGrowableCol(0)
        sizer_diplomes.Add(grid_sizer_diplomes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_diplomes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def OnRadioDuree(self, event):
        if self.radio_duree_1.GetValue() == True:
            self.label_jours.Enable(False)
            self.spin_jours.Enable(False)
            self.label_mois.Enable(False)
            self.spin_mois.Enable(False)
            self.label_annees.Enable(False)
            self.spin_annees.Enable(False)
        else:
            self.label_jours.Enable(True)
            self.spin_jours.Enable(True)
            self.label_mois.Enable(True)
            self.spin_mois.Enable(True)
            self.label_annees.Enable(True)
            self.spin_annees.Enable(True)

    def RemplirCtrlMaladies(self):
        db = GestionDB.DB()
        req = """SELECT IDtype_maladie, nom, vaccin_obligatoire
        FROM types_maladies ORDER BY nom; """ 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listesMaladies = []
        for IDtype_maladie, nom, vaccin_obligatoire in listeDonnees :
            listesMaladies.append( (IDtype_maladie, nom, False) )
        self.ctrl_maladies.SetData(listesMaladies)
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Vaccins")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        textNom = self.ctrl_nom.GetValue()
        if textNom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement donner un nom à ce vaccin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        jours = int(self.spin_jours.GetValue())
        mois = int(self.spin_mois.GetValue())
        annees = int(self.spin_annees.GetValue())

        if jours == 0 and mois == 0 and annees == 0 and self.radio_duree_2.GetValue() == True:
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné une durée de validité limitée. \nVous devez donc saisir un nombre de jours et/ou de mois et/ou d'années."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.spin_jours.SetFocus()
            return
        
        if self.ctrl_maladies.GetIDcoches() == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez associer des maladies à ce vaccin"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetNom(self):
        return self.ctrl_nom.GetValue()

    def GetValidite(self):
        if self.radio_duree_1.GetValue() == True:
            validite = "j0-m0-a0"
        else:
            validite = "j%d-m%d-a%d" % (int(self.spin_jours.GetValue()), int(self.spin_mois.GetValue()), int(self.spin_annees.GetValue()),)
        return validite
    
    def GetMaladiesAssociees(self):
        return self.ctrl_maladies.GetIDcoches()
            
    def SetNom(self, nom=""):
        self.ctrl_nom.SetValue(nom)

    def SetValidite(self, validite=None):
        if validite != None :
            posM = validite.find("m")
            posA = validite.find("a")
            jours = int(validite[1:posM-1])
            mois = int(validite[posM+1:posA-1])
            annees = int(validite[posA+1:])
        if validite == None or (jours == 0 and mois == 0 and annees == 0) :
            self.radio_duree_1.SetValue(True)
            self.radio_duree_2.SetValue(False)
        else:
            self.radio_duree_1.SetValue(False)
            self.radio_duree_2.SetValue(True)
            self.spin_jours.SetValue(jours)
            self.spin_mois.SetValue(mois)
            self.spin_annees.SetValue(annees)
        self.OnRadioDuree(None)
    
    def SetMaladiesAssociees(self, listeIDmaladies=[]):
        self.ctrl_maladies.SetIDcoches(listeIDmaladies)
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
