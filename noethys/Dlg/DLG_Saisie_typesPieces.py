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
from Ctrl import CTRL_Saisie_date


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.SetTitle(_(u"Saisie d'un type de pièce"))  
        
        self.sizer_nom_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.label_public = wx.StaticText(self, -1, _(u"Public :"))
        self.ctrl_public = wx.Choice(self, -1, (100, -1), choices = ("Individu", "Famille"))
        self.ctrl_rattachement = wx.CheckBox(self, -1, u"")
        self.label_rattachement = wx.StaticText(self, -1, _(u"Cochez cette case si, lorsqu'un individu est rattaché à plusieurs \nfamilles, cette pièce est valable pour toutes les familles rattachée."))
        
        self.sizer_duree_staticbox = wx.StaticBox(self, -1, _(u"Validité par défaut"))
        
        self.radio_duree_1 = wx.RadioButton(self, -1, _(u"Validité illimitée"), style=wx.RB_GROUP)
        
        self.radio_duree_2 = wx.RadioButton(self, -1, _(u"La durée suivante : "))
        self.label_jours = wx.StaticText(self, -1, _(u"Jours :"))
        self.spin_jours = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.spin_mois = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_annees = wx.StaticText(self, -1, _(u"Années :"))
        self.spin_annees = wx.SpinCtrl(self, -1, "", min=0, max=100)
        
        self.radio_duree_3 = wx.RadioButton(self, -1, _(u"La date suivante : "))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoice_public, self.ctrl_public)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_3)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
    
        self.OnChoice_public(None)
        self.OnRadioDuree(None)
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici un nom de pièce. Par exemple : 'Fiche sanitaire'"))
        self.ctrl_public.SetToolTipString(_(u"Sélectionnez le public auquel cette pièce s'adresse"))
        self.radio_duree_1.SetToolTipString(_(u"Sélectionnez 'Illimitée' si la pièce est valable à vie"))
        self.radio_duree_2.SetToolTipString(_(u"Sélectionnez 'Durée' si vous souhaitez définir une durée de validité pour cette pièce"))
        self.radio_duree_3.SetToolTipString(_(u"Sélectionnez 'Date' si la pièce n'est valable que jusqu'à une date précise"))
        self.spin_jours.SetMinSize((60, -1))
        self.spin_mois.SetMinSize((60, -1))
        self.spin_annees.SetMinSize((60, -1))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))
        self.SetMinSize((440, 340))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        
        sizer_nom = wx.StaticBoxSizer(self.sizer_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_public, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_public, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add((10, 10), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_rattachement = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_rattachement.Add(self.ctrl_rattachement, 0, wx.EXPAND, 0)
        grid_sizer_rattachement.Add(self.label_rattachement, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(grid_sizer_rattachement, 0, wx.EXPAND, 0)
        
        grid_sizer_nom.AddGrowableCol(1)
        sizer_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        sizer_duree = wx.StaticBoxSizer(self.sizer_duree_staticbox, wx.VERTICAL)
        
        # Illimitée
        grid_sizer_duree1 = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_duree1.Add(self.radio_duree_1, 0, 0, 0)
                
        # Durée
        grid_sizer_duree2 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree2.Add(self.radio_duree_2, 0, 0, 0)
        grid_sizer_duree1.Add(grid_sizer_duree2, 1, wx.EXPAND, 0)

        grid_sizer_duree3 = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_duree3.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree3.Add(self.spin_jours, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_mois, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_annees, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_annees, 0, 0, 0)
        
        grid_sizer_duree2.Add(grid_sizer_duree3, 1, wx.LEFT|wx.EXPAND, 20)
        
        # Date
        grid_sizer_duree4 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree4.Add(self.radio_duree_3, 0, 0, 0)
        grid_sizer_duree1.Add(grid_sizer_duree4, 1, wx.EXPAND, 0)
        
        grid_sizer_duree4.Add(self.ctrl_date, 1, wx.LEFT|wx.EXPAND, 20)

        
        sizer_duree.Add(grid_sizer_duree1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_duree, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
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
    
    def OnChoice_public(self, event):
        if self.ctrl_public.GetSelection() == 0 :
            self.ctrl_rattachement.Enable(True)
            self.label_rattachement.Enable(True)
        else:
            self.ctrl_rattachement.Enable(False)
            self.label_rattachement.Enable(False)
        
    def OnRadioDuree(self, event):
        self.label_jours.Enable(self.radio_duree_2.GetValue())
        self.spin_jours.Enable(self.radio_duree_2.GetValue())
        self.label_mois.Enable(self.radio_duree_2.GetValue())
        self.spin_mois.Enable(self.radio_duree_2.GetValue())
        self.label_annees.Enable(self.radio_duree_2.GetValue())
        self.spin_annees.Enable(self.radio_duree_2.GetValue())
        self.ctrl_date.Enable(self.radio_duree_3.GetValue())
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Typesdepices")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement donner un nom à cette pièce !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        if self.ctrl_public.GetSelection() == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner le public !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_public.SetFocus()
            return

        jours = int(self.spin_jours.GetValue())
        mois = int(self.spin_mois.GetValue())
        annees = int(self.spin_annees.GetValue())
        date = self.ctrl_date.GetDate() 

        if jours == 0 and mois == 0 and annees == 0 and self.radio_duree_2.GetValue() == True:
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné une durée de pièce limitée. \nVous devez donc saisir un nombre de jours et/ou de mois et/ou d'années."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.spin_jours.SetFocus()
            return

        if date == None and self.radio_duree_3.GetValue() == True:
            dlg = wx.MessageDialog(self, _(u"La date de fin de validité n'est pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetNom(self):
        return self.ctrl_nom.GetValue()

    def SetNom(self, nom=""):
        self.ctrl_nom.SetValue(nom)
        
    def GetValidite(self):
        if self.radio_duree_1.GetValue() == True:
            return None
        if self.radio_duree_2.GetValue() == True:
            return "j%d-m%d-a%d" % (int(self.spin_jours.GetValue()), int(self.spin_mois.GetValue()), int(self.spin_annees.GetValue()),)
        if self.radio_duree_3.GetValue() == True:
            return "d%s" % str(self.ctrl_date.GetDate())

    def SetValidite(self, validite=None):
        if validite == None or validite == "j0-m0-a0" :
            self.radio_duree_1.SetValue(True)

        elif validite != None and validite.startswith("j") :
            posM = validite.find("m")
            posA = validite.find("a")
            self.spin_jours.SetValue(int(validite[1:posM-1]))
            self.spin_mois.SetValue(int(validite[posM+1:posA-1]))
            self.spin_annees.SetValue(int(validite[posA+1:]))
            self.radio_duree_2.SetValue(True)

        elif validite != None and validite.startswith("d") :
            self.ctrl_date.SetDate(validite[1:])
            self.radio_duree_3.SetValue(True)
        
##        if validite != None :
##            posM = validite.find("m")
##            posA = validite.find("a")
##            jours = int(validite[1:posM-1])
##            mois = int(validite[posM+1:posA-1])
##            annees = int(validite[posA+1:])
##        if validite == None or (jours == 0 and mois == 0 and annees == 0) :
##            self.radio_duree_1.SetValue(True)
##            self.radio_duree_2.SetValue(False)
##        else:
##            self.radio_duree_1.SetValue(False)
##            self.radio_duree_2.SetValue(True)
##            self.spin_jours.SetValue(jours)
##            self.spin_mois.SetValue(mois)
##            self.spin_annees.SetValue(annees)
            
        self.OnRadioDuree(None)
    
    def GetPublic(self):
        if self.ctrl_public.GetSelection() == 0 : return "individu"
        if self.ctrl_public.GetSelection() == 1 : return "famille"
        return None

    def SetPublic(self, public):
        if public == "individu" : self.ctrl_public.SetSelection(0)
        if public == "famille" : self.ctrl_public.SetSelection(1)
        self.OnChoice_public(None)
    
    def GetRattachement(self):
        if self.GetPublic() == "individu" :
            return int(self.ctrl_rattachement.GetValue())
        else:
            return None

    def SetRattachement(self, valeur):
        if valeur == 1 :
            self.ctrl_rattachement.SetValue(True)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    
    dlg.SetNom("Test")
    dlg.SetPublic("famille")
    #dlg.SetValidite("j1-m2-a10")
    dlg.SetValidite("d2003-05-06")
    
    dlg.ShowModal()
    app.MainLoop()
