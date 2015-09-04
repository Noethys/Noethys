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
import datetime
import GestionDB

import CTRL_Saisie_date
import UTILS_Dates

import wx.lib.agw.floatspin as FS


# --------------------------------------------------------------------------------------------------------

class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.IDactivite = IDactivite
        self.data = []
        self.Importation() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeValeurs = []
        for IDcategorie_tarif, nom in listeDonnees :
            listeValeurs.append((IDcategorie_tarif, nom, False)) 
        self.SetData(listeValeurs)
        
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
    
    def GetTexteCoches(self):
        listeIDcoches = []
        listeTemp = self.GetIDcoches() 
        if len(listeTemp) == 0 : return None
        for ID in listeTemp :
            listeIDcoches.append(str(ID))
        texte = ";".join(listeIDcoches)
        return texte

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1


# --------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Validit�
        self.label_date_debut = wx.StaticText(self, -1, _(u"A partir du :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.check_date_fin = wx.CheckBox(self, -1, _(u"Jusqu'au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Description
        self.label_description = wx.StaticText(self, -1, _(u"Nom du tarif :"))
        self.ctrl_description = wx.TextCtrl(self, -1, u"") 

        # Observations
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE) 

        # Cat�gories de tarifs
        self.label_categories = wx.StaticText(self, -1, _(u"Cat�gories :"))
        self.ctrl_categories = CTRL_Categories(self, IDactivite)
        self.ctrl_categories.SetMinSize((150, 100))
        
        # TVA
        self.label_tva = wx.StaticText(self, -1, _(u"Taux TVA :"))
        self.ctrl_tva = FS.FloatSpin(self, -1, min_val=0, max_val=100, increment=0.1, agwStyle=FS.FS_RIGHT)
        self.ctrl_tva.SetFormat("%f")
        self.ctrl_tva.SetDigits(2)
        
        # Code comptable
        self.label_code_comptable = wx.StaticText(self, -1, _(u"Code compta :"))
        self.ctrl_code_comptable = wx.TextCtrl(self, -1, u"") 

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_validite = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_validite.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_validite.Add( (5, 5), 0, 0, 0)
        grid_sizer_validite.Add(self.check_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_fin, 0, 0, 0)   
             
        grid_sizer_base.Add(grid_sizer_validite, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_description, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_observations, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(self.label_categories, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_categories, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(self.label_tva, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_tva, 1, 0, 0)

        grid_sizer_base.Add(self.label_code_comptable, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_code_comptable, 1, 0, 0)

        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(1)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
                
        # Tooltips
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez ici la date de d�but de validit�"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici la date de fin de validit�"))
        self.ctrl_description.SetToolTipString(_(u"Saisissez une description explicite pour ce tarif [Optionnel]"))
        self.ctrl_categories.SetToolTipString(_(u"Cochez les cat�gories de tarifs � rattacher � ce tarif"))
        self.ctrl_tva.SetToolTipString(_(u"Saisissez le taux de TVA inclus [Optionnel]"))
        self.ctrl_code_comptable.SetToolTipString(_(u"Saisissez le code comptable de cette prestation si vous souhaitez utiliser l'export vers les logiciels de comptabilit� [Optionnel]"))

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDateFin, self.check_date_fin)

        # Init
        self.OnCheckDateFin(None)

    
    def OnCheckDateFin(self, event):
        if self.check_date_fin.GetValue() == True :
            self.ctrl_date_fin.Enable(True)
            self.ctrl_date_fin.SetFocus()
        else:
            self.ctrl_date_fin.Enable(False)

    def SetDateDebut(self, date):
        self.ctrl_date_debut.SetDate(date)
        
    def SetDateFin(self, date):
        if date != None :
            self.check_date_fin.SetValue(True)
            self.ctrl_date_fin.SetDate(date)
        self.OnCheckDateFin(None)
        
    def SetCategories(self, categories_tarifs):
        if categories_tarifs != None :
            listeCategories = []
            listeTemp = categories_tarifs.split(";")
            for IDcategorie_tarif in listeTemp :
                listeCategories.append(int(IDcategorie_tarif))
            self.ctrl_categories.SetIDcoches(listeCategories)
    
    def SetDescription(self, description=""):
        if description != None :
            self.ctrl_description.SetValue(description)        

    def SetObservations(self, observations=""):
        if observations != None :
            self.ctrl_observations.SetValue(observations)        
    
    def SetTVA(self, tva=0.00):
        if tva != None :
            self.ctrl_tva.SetValue(tva)        

    def SetCodeComptable(self, code=""):
        if code != None :
            self.ctrl_code_comptable.SetValue(code)        

    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()
        
    def GetDateFin(self):
        if self.check_date_fin.GetValue() == True :
            if self.ctrl_date_fin.GetDate() != None :
                date_fin = self.ctrl_date_fin.GetDate()
            else:
                date_fin = None
        else:
            date_fin = None
        return date_fin
    
    def GetCategories(self):
        return self.ctrl_categories.GetTexteCoches()

    def GetDescription(self):
        return self.ctrl_description.GetValue() 

    def GetObservations(self):
        return self.ctrl_observations.GetValue()
    
    def GetTVA(self):
        return self.ctrl_tva.GetValue() 
    
    def GetCodeComptable(self):
        return self.ctrl_code_comptable.GetValue() 
    
    def Validation(self):
        # V�rification des dates de validit�
        validation = self.ctrl_date_debut.FonctionValiderDate() 
        if validation == False : 
            return False
        if self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de d�but de validit� !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        
        if self.check_date_fin.GetValue() == True :
            validation = self.ctrl_date_fin.FonctionValiderDate() 
            if validation == False : 
                return False
            if self.ctrl_date_fin.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin de validit� !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
            if self.ctrl_date_fin.GetDate() < self.ctrl_date_debut.GetDate() :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin sup�rieure � la date de d�but !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
        
        # V�rifie que des cat�gories de tarifs ont �t� coch�es
        listeCategories = self.ctrl_categories.GetIDcoches()
        if len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coch� aucune cat�gorie de tarifs.\nCe tarif sera donc inactif pour le moment...\n\nVoulez-vous quand-m�me continuer ?") , _(u"Erreur"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False
        
        return True

    def Sauvegarde(self):
        pass






class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=9, IDtarif=29)
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