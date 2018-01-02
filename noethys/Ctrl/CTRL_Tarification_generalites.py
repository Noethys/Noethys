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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

import CTRL_Saisie_date
from Utils import UTILS_Dates
from Utils import UTILS_Texte

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
        if self.IDactivite != None :
            IDactivite = self.IDactivite
        else :
            IDactivite = 0
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom;""" % IDactivite
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

class CTRL_Label_prestation(wx.Panel):
    def __init__(self, parent, listeChoix=[]):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listeChoix = listeChoix
        self.listeChoix.append(("autre:", _(u"Le label suivant")))

        choices = []
        for code, label in self.listeChoix:
            choices.append(label)
        self.ctrl_choix = wx.Choice(self, -1, choices=choices)
        self.ctrl_choix.SetToolTip(wx.ToolTip(_(u"Sélectionnez le label de la prestation")))
        self.ctrl_autre = wx.TextCtrl(self, -1, "")

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_choix, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_autre, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_choix)

        self.OnChoix()

    def OnChoix(self, event=None):
        code = self.GetCodeSelection()
        if code != None and code.startswith("autre:"):
            self.ctrl_autre.Enable(True)
            if self.ctrl_autre.GetValue() == "":
                self.ctrl_autre.SetFocus()
        else:
            self.ctrl_autre.Enable(False)

    def GetCodeSelection(self):
        index = self.ctrl_choix.GetSelection()
        if index == -1: return None
        code = self.listeChoix[index][0]
        if code == "autre:":
            texte = self.ctrl_autre.GetValue()
            code = u"autre:%s" % texte
        return code

    def SetCodeSelection(self, code=""):
        index = 0
        for codeTemp, label in self.listeChoix:
            if code != None :
                if codeTemp == code or (codeTemp == "autre:" and code.startswith("autre:")):
                    self.ctrl_choix.Select(index)
                    if code.startswith("autre:"):
                        self.ctrl_autre.SetValue(code[6:])
            index += 1
        self.OnChoix()

    def Validation(self):
        if self.GetCodeSelection() == "autre:":
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné un label de prestation personnalisé mais sans saisir le label souhaité !"),_(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_autre.SetFocus()
            return False
        return True


# --------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, cacher_dates=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.cacher_dates = cacher_dates

        # Validité
        self.label_date_debut = wx.StaticText(self, -1, _(u"A partir du :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.check_date_fin = wx.CheckBox(self, -1, _(u"Jusqu'au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        if cacher_dates :
            self.label_date_debut.Show(False)
            self.ctrl_date_debut.Show(False)
            self.check_date_fin.Show(False)
            self.ctrl_date_fin.Show(False)

        # Description
        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self, -1, u"") 

        # Observations
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE) 

        # Catégories de tarifs
        self.label_categories = wx.StaticText(self, -1, _(u"Catégories :"))
        self.ctrl_categories = CTRL_Categories(self, IDactivite)
        self.ctrl_categories.SetMinSize((150, 50))

        # Label de la prestation
        self.label_label_prestation = wx.StaticText(self, -1, _(u"Label prestation :"))
        listeChoix = [
            ("nom_tarif", _(u"Nom du tarif (Par défaut)")),
            ("description_tarif", _(u"Description du tarif")),
            ]
        self.ctrl_label_prestation = CTRL_Label_prestation(self, listeChoix=listeChoix)
        self.ctrl_label_prestation.SetCodeSelection("nom_tarif")

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

        grid_sizer_base.Add(self.label_label_prestation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_label_prestation, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(self.label_tva, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_tva, 1, 0, 0)

        grid_sizer_base.Add(self.label_code_comptable, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_code_comptable, 1, 0, 0)

        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(1)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)

        self.grid_sizer_base = grid_sizer_base
                
        # Tooltips
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de validité")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de validité")))
        self.ctrl_description.SetToolTip(wx.ToolTip(_(u"Saisissez une description explicite pour ce tarif [Optionnel]")))
        self.ctrl_categories.SetToolTip(wx.ToolTip(_(u"Cochez les catégories de tarifs à rattacher à ce tarif")))
        self.ctrl_tva.SetToolTip(wx.ToolTip(_(u"Saisissez le taux de TVA inclus [Optionnel]")))
        self.ctrl_code_comptable.SetToolTip(wx.ToolTip(_(u"Saisissez le code comptable de cette prestation si vous souhaitez utiliser l'export vers les logiciels de comptabilité [Optionnel]")))

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDateFin, self.check_date_fin)

        # Init
        self.OnCheckDateFin(None)
        self.ctrl_date_debut.SetDate(datetime.date.today())

    
    def OnCheckDateFin(self, event):
        if self.check_date_fin.GetValue() == True :
            self.ctrl_date_fin.Enable(True)
            self.ctrl_date_fin.SetFocus()
        else:
            self.ctrl_date_fin.Enable(False)

    def MasqueCategories(self):
        self.label_categories.Show(False)
        self.ctrl_categories.Show(False)
        self.grid_sizer_base.Layout()

    def SetDateDebut(self, date):
        self.ctrl_date_debut.SetDate(date)
        
    def SetDateFin(self, date):
        if date != None :
            self.check_date_fin.SetValue(True)
            self.ctrl_date_fin.SetDate(date)
        self.OnCheckDateFin(None)
        
    def SetCategories(self, categories_tarifs):
        if categories_tarifs != None :
            listeCategories = UTILS_Texte.ConvertStrToListe(categories_tarifs)
            self.ctrl_categories.SetIDcoches(listeCategories)

    def SetLabelPrestation(self, label_prestation=""):
        self.ctrl_label_prestation.SetCodeSelection(label_prestation)

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

    def GetLabelPrestation(self):
        return self.ctrl_label_prestation.GetCodeSelection()

    def GetDescription(self):
        return self.ctrl_description.GetValue() 

    def GetObservations(self):
        return self.ctrl_observations.GetValue()
    
    def GetTVA(self):
        return self.ctrl_tva.GetValue() 
    
    def GetCodeComptable(self):
        return self.ctrl_code_comptable.GetValue() 
    
    def Validation(self):
        # Vérification des dates de validité
        if not self.cacher_dates :

            validation = self.ctrl_date_debut.FonctionValiderDate()
            if validation == False :
                return False
            if self.ctrl_date_debut.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début de validité !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False

            if self.check_date_fin.GetValue() == True :
                validation = self.ctrl_date_fin.FonctionValiderDate()
                if validation == False :
                    return False
                if self.ctrl_date_fin.GetDate() == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin de validité !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_date_fin.SetFocus()
                    return False
                if self.ctrl_date_fin.GetDate() < self.ctrl_date_debut.GetDate() :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin supérieure à la date de début !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_date_fin.SetFocus()
                    return False

        # Vérifie que des catégories de tarifs ont été cochées
        listeCategories = self.ctrl_categories.GetIDcoches()
        if self.ctrl_categories.IsShown() and len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune catégorie de tarifs.\nCe tarif sera donc inactif pour le moment...\n\nVoulez-vous quand-même continuer ?") , _(u"Erreur"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Vérifie la valeur du label de prestation
        if self.ctrl_label_prestation.Validation() == False :
            return False

        if self.GetLabelPrestation() == "description_tarif" and self.GetDescription() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné un label de prestation 'Description du tarif' mais sans saisir de description !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_description.SetFocus()
            return False

        return True

    def Sauvegarde(self):
        pass

    def MAJ(self):
        pass





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel, IDactivite=9, IDtarif=29)
        #self.ctrl.MasqueCategories()
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