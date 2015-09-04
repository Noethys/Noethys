#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Choix_modele
import GestionDB
import os

import UTILS_Identification
import UTILS_Config
import DLG_Filtres_rappels



class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.label_modele = wx.StaticText(self, -1, _(u"Mod�le :"))
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie="rappel")
        self.bouton_modele = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.checkbox_coupon = wx.CheckBox(self, -1, _(u"Ins�rer le coupon-r�ponse"))
        self.checkbox_codeBarre = wx.CheckBox(self, -1, _(u"Ins�rer les codes-barres"))

        self.label_repertoire = wx.StaticText(self, -1, _(u"Copie :"))
        self.checkbox_repertoire = wx.CheckBox(self, -1, _(u"Enregistrer une copie unique dans le r�pertoire :"))
        self.ctrl_repertoire = wx.TextCtrl(self, -1, u"")
        self.ctrl_repertoire.SetMinSize((270, -1))
        self.bouton_repertoire = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Repertoire.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModele, self.bouton_modele)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRepertoire, self.checkbox_repertoire)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRepertoire, self.bouton_repertoire)
        
        # R�cup�ration des param�tres dans le CONFIG
        self.checkbox_coupon.SetValue(UTILS_Config.GetParametre("impression_rappels_coupon", defaut=1))
        self.checkbox_codeBarre.SetValue(UTILS_Config.GetParametre("impression_rappels_codeBarre", defaut=1))
        param = UTILS_Config.GetParametre("impression_rappels_repertoire", defaut="")
        if param != "" :
            self.checkbox_repertoire.SetValue(True)
            self.ctrl_repertoire.SetValue(param)

        # Init contr�les
        self.OnCheckRepertoire(None)

    def __set_properties(self):
        self.ctrl_modele.SetToolTipString(_(u"S�lectionnez le mod�le"))
        self.bouton_modele.SetToolTipString(_(u"Cliquez ici pour acc�der � la gestion des mod�les"))
        self.checkbox_coupon.SetToolTipString(_(u"Cochez cette case pour ins�rer un coupon � d�couper"))
        self.checkbox_codeBarre.SetToolTipString(_(u"Cochez cette case pour ins�rer un code-barre pour le num�ro de lettre"))
        self.checkbox_repertoire.SetToolTipString(_(u"Cochez cette case pour enregistrer un exemplaire de chaque lettre de rappel au format PDF dans le r�pertoire indiqu�"))
        self.bouton_repertoire.SetToolTipString(_(u"Cliquez ici pour s�lectionner un r�pertoire de destination"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        # Mod�le + Coupon + Codebarre
        grid_sizer_base.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_modele = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.Add(self.bouton_modele, 0, 0, 0)
        grid_sizer_modele.Add( (10, 10), 0, 0, 0)
        grid_sizer_modele.Add(self.checkbox_coupon, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.Add( (10, 10), 0, 0, 0)
        grid_sizer_modele.Add(self.checkbox_codeBarre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.AddGrowableCol(0)
        
        grid_sizer_base.Add(grid_sizer_modele, 1, wx.EXPAND, 0)

        # R�pertoire
        grid_sizer_base.Add(self.label_repertoire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_repertoire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_repertoire.Add(self.checkbox_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.ctrl_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.bouton_repertoire, 0, 0, 0)
        grid_sizer_repertoire.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_repertoire, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
                    
    def OnBoutonModele(self, event): 
        import DLG_Modeles_docs
        dlg = DLG_Modeles_docs.Dialog(self, categorie="rappel")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_modele.MAJ() 

    def OnCheckRepertoire(self, event):
        etat = self.checkbox_repertoire.GetValue()
        self.ctrl_repertoire.Enable(etat)
        self.bouton_repertoire.Enable(etat)
        
    def OnBoutonRepertoire(self, event): 
        if self.ctrl_repertoire.GetValue != "" : 
            cheminDefaut = self.ctrl_repertoire.GetValue()
            if os.path.isdir(cheminDefaut) == False :
                cheminDefaut = ""
        else:
            cheminDefaut = ""
        dlg = wx.DirDialog(self, _(u"Veuillez s�lectionner un r�pertoire de destination :"), defaultPath=cheminDefaut, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_repertoire.SetValue(dlg.GetPath())
        dlg.Destroy()
                
    def MemoriserParametres(self):
        UTILS_Config.SetParametre("impression_rappels_coupon", int(self.checkbox_coupon.GetValue()))
        UTILS_Config.SetParametre("impression_rappels_codeBarre", int(self.checkbox_codeBarre.GetValue()))
        if self.checkbox_repertoire.GetValue() == True :
            UTILS_Config.SetParametre("impression_rappels_repertoire", self.ctrl_repertoire.GetValue())
        else :
            UTILS_Config.SetParametre("impression_rappels_repertoire", "")
    
    def GetOptions(self):
        dictOptions = {} 
        
        # R�pertoire
        if self.checkbox_repertoire.GetValue() == True :
            repertoire = self.ctrl_repertoire.GetValue() 
            # V�rifie qu'un r�pertoire a �t� saisie
            if repertoire == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un r�pertoire de destination !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_repertoire.SetFocus()
                return False
            # V�rifie que le r�pertoire existe
            if os.path.isdir(repertoire) == False :
                dlg = wx.MessageDialog(self, _(u"Le r�pertoire de destination que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_repertoire.SetFocus()
                return False
        else:
            repertoire = None
                
        # R�cup�ration du mod�le
        IDmodele = self.ctrl_modele.GetID() 
        if IDmodele == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un mod�le !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Constitution du dictOptions
        dictOptions["codeBarre"] = self.checkbox_codeBarre.GetValue()
        dictOptions["coupon"] = self.checkbox_coupon.GetValue()
        dictOptions["IDmodele"] = IDmodele
        dictOptions["repertoire"] = repertoire
        
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


