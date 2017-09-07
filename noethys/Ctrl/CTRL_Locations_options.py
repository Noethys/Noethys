#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Choix_modele
import GestionDB
import os
from Utils import UTILS_Questionnaires
from Utils import UTILS_Identification
from Utils import UTILS_Config



class CTRL_Question(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.SetListe()

    def SetListe(self):
        # Initialisation des questionnaires
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type="location", avec_filtre=False)
        self.Clear()
        self.dictDonnees = {}
        index = 0
        for dictQuestion in self.liste_questions:
            if dictQuestion["controle"] == "documents" :
                self.Append(dictQuestion["label"])
                self.dictDonnees[index] = dictQuestion["IDquestion"]
                index += 1
        self.SetSelection(0)

    def SetID(self, ID=None):
        for indexTemp, IDtemp in self.dictDonnees.iteritems():
            if IDtemp == ID:
                self.SetSelection(indexTemp)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]




class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie="location")
        self.bouton_modele = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.label_repertoire = wx.StaticText(self, -1, _(u"Copie :"))
        self.checkbox_repertoire = wx.CheckBox(self, -1, _(u"Enregistrer une copie unique dans le répertoire :"))
        self.ctrl_repertoire = wx.TextCtrl(self, -1, u"")
        self.ctrl_repertoire.SetMinSize((270, -1))
        self.bouton_repertoire = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Repertoire.png"), wx.BITMAP_TYPE_ANY))

        self.label_questionnaire = wx.StaticText(self, -1, _(u"Stockage :"))
        self.checkbox_questionnaire = wx.CheckBox(self, -1, _(u"Enregistrer une copie unique dans un porte-documents :"))
        self.ctrl_questionnaire = CTRL_Question(self)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModele, self.bouton_modele)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRepertoire, self.checkbox_repertoire)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckQuestionnaire, self.checkbox_questionnaire)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRepertoire, self.bouton_repertoire)
        
        # Récupération des paramètres dans le CONFIG
        param = UTILS_Config.GetParametre("impression_locations_repertoire", defaut="")
        if param != "" :
            self.checkbox_repertoire.SetValue(True)
            self.ctrl_repertoire.SetValue(param)

        param = UTILS_Config.GetParametre("impression_locations_questionnaire", defaut="")
        if param != "" :
            self.checkbox_questionnaire.SetValue(True)
            self.ctrl_questionnaire.SetID(param)

        # Init contrôles
        self.OnCheckRepertoire(None)
        self.OnCheckQuestionnaire(None)

    def __set_properties(self):
        self.ctrl_modele.SetToolTip(wx.ToolTip(_(u"Sélectionnez le modèle")))
        self.bouton_modele.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des modèles")))
        self.checkbox_repertoire.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour enregistrer un exemplaire de chaque location au format PDF dans le répertoire indiqué")))
        self.bouton_repertoire.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un répertoire de destination")))
        self.checkbox_questionnaire.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour enregistrer un exemplaire de chaque document au format PDF dans un porte-document du questionnaire")))
        self.ctrl_questionnaire.SetToolTip(wx.ToolTip(_(u"Sélectionnez la question de type 'porte-document' dans laquelle sera stocké le document")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)

        # Modèle + Coupon + Codebarre
        grid_sizer_base.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_modele = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.Add(self.bouton_modele, 0, 0, 0)
        grid_sizer_modele.AddGrowableCol(0)
        
        grid_sizer_base.Add(grid_sizer_modele, 1, wx.EXPAND, 0)

        # Répertoire
        grid_sizer_base.Add(self.label_repertoire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_repertoire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_repertoire.Add(self.checkbox_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.ctrl_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.bouton_repertoire, 0, 0, 0)
        grid_sizer_repertoire.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_repertoire, 1, wx.EXPAND, 0)

        # Questionnaire
        grid_sizer_base.Add(self.label_questionnaire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_questionnaire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_questionnaire.Add(self.checkbox_questionnaire, 0, wx.EXPAND, 0)
        grid_sizer_questionnaire.Add(self.ctrl_questionnaire, 0, wx.EXPAND, 0)
        grid_sizer_questionnaire.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_questionnaire, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
                    
    def OnBoutonModele(self, event): 
        from Dlg import DLG_Modeles_docs
        dlg = DLG_Modeles_docs.Dialog(self, categorie="location")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_modele.MAJ() 

    def OnCheckRepertoire(self, event):
        etat = self.checkbox_repertoire.GetValue()
        self.ctrl_repertoire.Enable(etat)
        self.bouton_repertoire.Enable(etat)

    def OnCheckQuestionnaire(self, event):
        etat = self.checkbox_questionnaire.GetValue()
        self.ctrl_questionnaire.Enable(etat)

    def OnBoutonRepertoire(self, event): 
        if self.ctrl_repertoire.GetValue != "" : 
            cheminDefaut = self.ctrl_repertoire.GetValue()
            if os.path.isdir(cheminDefaut) == False :
                cheminDefaut = ""
        else:
            cheminDefaut = ""
        dlg = wx.DirDialog(self, _(u"Veuillez sélectionner un répertoire de destination :"), defaultPath=cheminDefaut, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_repertoire.SetValue(dlg.GetPath())
        dlg.Destroy()
                
    def MemoriserParametres(self):
        if self.checkbox_repertoire.GetValue() == True :
            UTILS_Config.SetParametre("impression_locations_repertoire", self.ctrl_repertoire.GetValue())
        else :
            UTILS_Config.SetParametre("impression_locations_repertoire", "")
        if self.checkbox_questionnaire.GetValue() == True :
            UTILS_Config.SetParametre("impression_locations_questionnaire", self.ctrl_questionnaire.GetID())
        else :
            UTILS_Config.SetParametre("impression_locations_questionnaire", "")


    def GetOptions(self):
        dictOptions = {} 
        
        # Répertoire
        if self.checkbox_repertoire.GetValue() == True :
            repertoire = self.ctrl_repertoire.GetValue() 
            # Vérifie qu'un répertoire a été saisie
            if repertoire == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un répertoire de destination !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_repertoire.SetFocus()
                return False
            # Vérifie que le répertoire existe
            if os.path.isdir(repertoire) == False :
                dlg = wx.MessageDialog(self, _(u"Le répertoire de destination que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_repertoire.SetFocus()
                return False
        else:
            repertoire = None

        # Questionnaire
        if self.checkbox_questionnaire.GetValue() == True :
            questionnaire = self.ctrl_questionnaire.GetID()
            if questionnaire == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une question !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_questionnaire.SetFocus()
                return False
        else:
            questionnaire = None

        # Récupération du modèle
        IDmodele = self.ctrl_modele.GetID() 
        if IDmodele == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        nomModele = self.ctrl_modele.GetStringSelection()

        # Constitution du dictOptions
##        dictOptions["coupon"] = self.checkbox_coupon.GetValue()
        dictOptions["IDmodele"] = IDmodele
        dictOptions["repertoire"] = repertoire
        dictOptions["nomModele"] = nomModele
        dictOptions["questionnaire"] = questionnaire

        return dictOptions


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)        
        self.ctrl = CTRL(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        print self.ctrl.GetOptions() 

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


