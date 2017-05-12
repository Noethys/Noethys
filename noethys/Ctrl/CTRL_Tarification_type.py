#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import CTRL_Saisie_date

import CTRL_Tarification_journ
import CTRL_Tarification_forfait
import CTRL_Tarification_credit
import CTRL_Tarification_calcul



class CTRL_Date_facturation(wx.Panel):
    def __init__(self, parent, listeChoix=[]):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listeChoix = listeChoix
        self.listeChoix.append(("date:", _(u"La date suivante")))
        
        choices = []
        for code, label in self.listeChoix :
            choices.append(label)
        self.ctrl_choix = wx.Choice(self, -1, choices=choices)
        self.ctrl_choix.SetToolTip(wx.ToolTip(_(u"Sélectionnez la date de facturation de la prestation")))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_choix, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_choix)
        
        self.OnChoix() 
        
    def OnChoix(self, event=None):
        code = self.GetCodeSelection()
        if code !=None and code.startswith("date:") :
            self.ctrl_date.Enable(True)
            if self.ctrl_date.GetDate() == None :
                self.ctrl_date.SetFocus() 
        else :
            self.ctrl_date.Enable(False)
    
    def GetCodeSelection(self):
        index = self.ctrl_choix.GetSelection()
        if index == -1 : return None
        code = self.listeChoix[index][0]
        if code == "date:" :
            date = self.ctrl_date.GetDate() 
            code = "date:%s" % date
        return code
    
    def SetCodeSelection(self, code=""):
        index = 0
        for codeTemp, label in self.listeChoix :
            if codeTemp == code or (codeTemp == "date:" and code.startswith("date:")) :
                self.ctrl_choix.Select(index)
                if code.startswith("date:") :
                    self.ctrl_date.SetDate(code[5:])
            index += 1
        self.OnChoix() 

    def Validation(self):
        if self.GetCodeSelection() == "date:None" :
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné la date de facturation 'La date suivante' mais sans sélectionner de date valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False
        return True






class Panel_type_sans_parametres(wx.Panel):
    def __init__(self, parent, nouveauTarif=False, texte=_(u"Aucun paramètre à renseigner.")):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        st = wx.StaticText(self, -1, texte, (0, 0))

    def Validation(self):
        return True
    
    def Sauvegarde(self):
        pass




##class Choicebook(wx.Choicebook):
##    def __init__(self, parent, IDactivite, IDtarif, nouveauTarif=False):
##        wx.Choicebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT)
##        self.IDactivite = IDactivite
##        self.IDtarif = IDtarif
##        self.nouveauTarif = nouveauTarif
##        
##        # Création des pages
##        self.dictPages = {}
##        self.CreationPages()
##    
##    def CreationPages(self):
##        liste_pages = [
##            ("SIMPLE", _(u"Prestation simple"), Panel_type_sans_parametres(self, self.nouveauTarif)),
##            ("JOURN", _(u"Prestation journalière"), CTRL_Tarification_journ.Panel(self, self.IDactivite, self.IDtarif, self.nouveauTarif)),
##            ("FORFAIT", _(u"Forfait daté"), CTRL_Tarification_forfait.Panel(self, self.IDactivite, self.IDtarif, self.nouveauTarif)),
##            ("CREDIT", _(u"Forfait crédit"), CTRL_Tarification_credit.Panel(self, self.IDactivite, self.IDtarif, self.nouveauTarif)),
##            ]
##        self.dictPages = {}
##        index = 0
##        for code, label, ctrl in liste_pages :
##            self.AddPage(ctrl, label)
##            self.dictPages[code] = {"index":index, "ctrl":ctrl}
##            index += 1
##    
##    def SetType(self, code="JOURN"):
##        """ Sélection d'une page d'après son code """
##        if self.dictPages.has_key(code):
##            self.SetSelection(self.dictPages[code]["index"])
##    
##    def GetType(self):
##        """ Retourne le code de la page sélectionnée """
##        selection = self.GetSelection()
##        for code, dictTemp in self.dictPages.iteritems() :
##            if dictTemp["index"] == selection :
##                return code
##        return None        
##    
##    def GetPage(self):
##        """ Retourne le CTRL de la page actuelle """
##        code = self.GetType() 
##        ctrl = self.dictPages[code]["ctrl"]
##        return ctrl        
##        
##    def Validation(self):
##        # Validation des paramètres du type
##        validation = self.GetPage().Validation()
##        return validation
##        
##    def Sauvegarde(self):
##        # Validation des paramètres du type
##        self.GetPage().Sauvegarde()

# --------------------------------------------------------------------------------------------------------------------------------------------------

class Choix_type(wx.Choice):
    def __init__(self, parent, liste_pages=[]):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.liste_pages = liste_pages
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeLabels = []
        for code, label, ctrl in self.liste_pages :
            listeLabels.append(label)
        self.SetItems(listeLabels)
    
    def SetType(self, code="SIMPLE"):
        index = 0
        for codeTemp, label, ctrl in self.liste_pages :
            if code == codeTemp :
                self.SetSelection(index)
            index += 1

    def GetType(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.liste_pages[index][0]

# --------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.liste_pages = [
            ("JOURN", _(u"Prestation journalière"), CTRL_Tarification_journ.Panel(self, IDactivite, IDtarif, nouveauTarif)),
            ("FORFAIT", _(u"Forfait daté"), CTRL_Tarification_forfait.Panel(self, IDactivite, IDtarif, nouveauTarif)),
            ("CREDIT", _(u"Forfait crédit"), CTRL_Tarification_credit.Panel(self, IDactivite, IDtarif, nouveauTarif)),
            ("BAREME", _(u"Barême de contrat"), Panel_type_sans_parametres(self, nouveauTarif)),
            ]

        # Création des pages
        self.grid_sizer_pages = wx.FlexGridSizer(len(self.liste_pages), 1, 10, 10)
        self.dictPages = {}
        index = 0
        for code, label, ctrl in self.liste_pages :
            self.grid_sizer_pages.Add(ctrl, 1, wx.EXPAND, 0)
            self.grid_sizer_pages.AddGrowableRow(index)
            ctrl.Show(False)
            self.dictPages[code] = {"index":index, "ctrl":ctrl}
            index += 1
        
        # Layout
        self.grid_sizer_pages.AddGrowableCol(0)
        self.SetSizer(self.grid_sizer_pages)

    def AffichePage(self, code=""):
        for codeTemp, valeurs in self.dictPages.iteritems() :
            if code == codeTemp :
                valeurs["ctrl"].Show(True)
            else :
                valeurs["ctrl"].Show(False)
        self.grid_sizer_pages.Layout()

    def GetPage(self):
        """ Retourne le CTRL de la page actuelle """
        for code, label, ctrl in self.liste_pages :
            if ctrl.IsShown() == True :
                return ctrl
        return None        
        
    def Validation(self):
        validation = self.GetPage().Validation()
        return validation
        
    def Sauvegarde(self):
        self.GetPage().Sauvegarde()


# -------------------------------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.label_parametres = wx.StaticText(self, -1, _(u"Paramètres :"))
        self.ctrl_parametres = CTRL_Parametres(self, IDactivite=IDactivite, IDtarif=IDtarif, nouveauTarif=nouveauTarif)
        
        self.label_type = wx.StaticText(self, -1, _(u"Type de tarif :"))
        self.ctrl_type = Choix_type(self, liste_pages=self.ctrl_parametres.liste_pages)
        
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_type, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_parametres, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(1)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixType, self.ctrl_type)
        
        # Init contrôles
        self.SetType(code="JOURN")
    
    def OnChoixType(self, event=None):
        code = self.ctrl_type.GetType() 
        self.ctrl_parametres.AffichePage(code)
        
    def Validation(self):
        return self.ctrl_parametres.Validation()
    
    def Sauvegarde(self):
        self.ctrl_parametres.Sauvegarde()

    def SetType(self, code="JOURN"):
        """ Sélection d'une page d'après son code """
        self.ctrl_type.SetType(code)
        self.ctrl_parametres.AffichePage(code)
    
    def GetType(self):
        """ Retourne le code de la page sélectionnée """
        return self.ctrl_type.GetType()        
    







class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=9, IDtarif=29, nouveauTarif=False)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()