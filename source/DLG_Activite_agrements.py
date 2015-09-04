#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

import OL_Agrements
import GestionDB

try: import psyco; psyco.full()
except: pass

class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panel_agrements", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        
        self.staticbox_agrements_staticbox = wx.StaticBox(self, -1, _(u"Agr�ments de l'activit�"))
        self.radio_aucun = wx.RadioButton(self, -1, u"")
        self.radio_aucun.SetValue(True)
        self.label_aucun = wx.StaticText(self, -1, _(u"Aucun agr�ment"))
        self.radio_unique = wx.RadioButton(self, -1, u"")
        self.label_unique = wx.StaticText(self, -1, _(u"Agr�ment unique :"))
        self.ctrl_agrement_unique = wx.TextCtrl(self, -1, u"")
        self.radio_multiples = wx.RadioButton(self, -1, u"")
        self.label_multiples = wx.StaticText(self, -1, _(u"Agr�ments multiples :"))
        
        self.ctrl_agrements = OL_Agrements.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_agrements", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_agrements.MAJ() 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_aucun)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_unique)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_multiples)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        # Importation
        if self.IDactivite != None :
            self.Importation() 
            
        self.OnRadio(None)
        
        

    def __set_properties(self):
        self.radio_unique.SetToolTipString(_(u"S�lectionnez 'Agr�ment unique' si l'activit� poss�de un agr�ment unique"))
        self.ctrl_agrement_unique.SetMinSize((120, -1))
        self.ctrl_agrement_unique.SetToolTipString(_(u"Saisissez ici le num�ro d'agr�ment unique"))
        self.radio_multiples.SetToolTipString(_(u"S�lectionnez 'Agr�ments multiples' si l'activit� peut avoir plusieurs agr�ments"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un agr�ment"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'agr�ment selectionn� dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'agr�ment selectionnn� dans la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=1, vgap=10, hgap=10)
        staticbox_agrements = wx.StaticBoxSizer(self.staticbox_agrements_staticbox, wx.VERTICAL)
        grid_sizer_agrements = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_multiples = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_unique = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_agrements.Add(self.radio_aucun, 0, 0, 0)
        grid_sizer_agrements.Add(self.label_aucun, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_agrements.Add(self.radio_unique, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unique.Add(self.label_unique, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unique.Add(self.ctrl_agrement_unique, 0, 0, 0)
        grid_sizer_agrements.Add(grid_sizer_unique, 1, wx.EXPAND, 0)
        grid_sizer_agrements.Add(self.radio_multiples, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_agrements.Add(self.label_multiples, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_agrements.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_multiples.Add(self.ctrl_agrements, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_multiples.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_multiples.AddGrowableRow(0)
        grid_sizer_multiples.AddGrowableCol(0)
        grid_sizer_agrements.Add(grid_sizer_multiples, 1, wx.EXPAND, 0)
        grid_sizer_agrements.AddGrowableRow(3)
        grid_sizer_agrements.AddGrowableCol(1)
        staticbox_agrements.Add(grid_sizer_agrements, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_agrements, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadio(self, event): 
        if self.radio_aucun.GetValue() == 1 :
            self.ctrl_agrement_unique.Enable(False)
            self.ctrl_agrements.Enable(False)
            self.bouton_ajouter.Enable(False)
            self.bouton_modifier.Enable(False)
            self.bouton_supprimer.Enable(False)
        if self.radio_unique.GetValue() == 1 :
            self.ctrl_agrement_unique.Enable(True)
            self.ctrl_agrements.Enable(False)
            self.bouton_ajouter.Enable(False)
            self.bouton_modifier.Enable(False)
            self.bouton_supprimer.Enable(False)
            self.ctrl_agrement_unique.SetFocus()
        if self.radio_multiples.GetValue() == 1 :
            self.ctrl_agrement_unique.Enable(False)
            self.ctrl_agrements.Enable(True)
            self.bouton_ajouter.Enable(True)
            self.bouton_modifier.Enable(True)
            self.bouton_supprimer.Enable(True)

    def OnBoutonAjouter(self, event): 
        self.ctrl_agrements.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_agrements.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_agrements.Supprimer(None)

    def Importation(self):
        """ Importation des donn�es """
        db = GestionDB.DB()
        req = """SELECT IDagrement, agrement, date_debut, date_fin 
        FROM agrements WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        # Unique
        if len(listeDonnees) == 1 :
            activite = listeDonnees[0]
            if activite[2] == "1977-01-01" and activite[3] == "2999-01-01" :
                self.radio_unique.SetValue(True)
                self.ctrl_agrement_unique.SetValue(activite[1])
                return
        # Multiples
        if len(listeDonnees) >= 1 :
            self.radio_multiples.SetValue(True)
    
    def Validation(self):
        # Aucun
        if self.radio_aucun.GetValue() == True :
            DB = GestionDB.DB()
            req = """SELECT IDagrement, IDactivite, agrement, date_debut, date_fin
            FROM agrements 
            WHERE IDactivite=%d; """ % self.IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Vous avez s�lectionn� 'Aucun agr�ment' pour cette activit�. Souhaitez-vous vraiment supprimer le ou les agr�ments pr�c�demment saisis pour cette activit� ?"), _(u"Suppression d'agr�ments"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                if dlg.ShowModal() != wx.ID_YES :
                    dlg.Destroy()
                    return False
                else:
                    dlg.Destroy()
        # Unique
        if self.radio_unique.GetValue() == True :
            if self.ctrl_agrement_unique.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Vous avez s�lectionn� 'Agr�ment unique' sans saisir de num�ro d'agr�ment !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_agrement_unique.SetFocus() 
                return False
        # Multiples
        if self.radio_multiples.GetValue() == True :
            nbreAgrements = len(self.ctrl_agrements.donnees)
            if nbreAgrements == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous avez s�lectionn� 'Agr�ments multiples' sans saisir aucun num�ro d'agr�ment !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        # Validation
        return True

    def Sauvegarde(self):
        # Aucun
        if self.radio_aucun.GetValue() == True :
            DB = GestionDB.DB()
            req = """SELECT IDagrement, IDactivite, agrement, date_debut, date_fin
            FROM agrements 
            WHERE IDactivite=%d; """ % self.IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                # Effacement des agr�ments existants
                DB.ReqDEL("agrements", "IDactivite", self.IDactivite)
            DB.Close()
        # Unique
        if self.radio_unique.GetValue() == True :
            # Effacement des num�ros d'agr�ments multiples existants
            DB = GestionDB.DB()
            req = """SELECT IDagrement, IDactivite, agrement, date_debut, date_fin
            FROM agrements 
            WHERE date_debut<>'1977-01-01' AND date_fin<>'2999-01-01' AND IDactivite=%d; """ % self.IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                # Effacement des agr�ments uniques existants
                for IDagrement, IDactivite, agrement, date_debut, date_fin in listeDonnees :
                    DB.ReqDEL("agrements", "IDagrement", IDagrement)
            # Enregistrement de l'agr�ment unique
            req = """SELECT IDagrement, IDactivite, agrement, date_debut, date_fin
            FROM agrements 
            WHERE date_debut='1977-01-01' AND date_fin='2999-01-01' AND IDactivite=%d; """ % self.IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                IDagrement = listeDonnees[0][0]
            else:
                IDagrement = None
            listeDonneesSave = [
                ("IDactivite", self.IDactivite ),
                ("agrement", self.ctrl_agrement_unique.GetValue() ),
                ("date_debut", "1977-01-01"),
                ("date_fin", "2999-01-01"),
                ]
            if IDagrement == None :
                IDagrement = DB.ReqInsert("agrements", listeDonneesSave)
            else:
                DB.ReqMAJ("agrements", listeDonneesSave, "IDagrement", IDagrement)
            DB.Close() 
        # Multiples
        if self.radio_multiples.GetValue() == True :
            DB = GestionDB.DB()
            req = """SELECT IDagrement, IDactivite, agrement, date_debut, date_fin
            FROM agrements 
            WHERE date_debut='1977-01-01' AND date_fin='2999-01-01' AND IDactivite=%d; """ % self.IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                # Effacement des agr�ments uniques existants
                for IDagrement, IDactivite, agrement, date_debut, date_fin in listeDonnees :
                    DB.ReqDEL("agrements", "IDagrement", IDagrement)
            DB.Close()
            

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=1)
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