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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Questionnaire
import GestionDB


class Panel(wx.Panel):
    def __init__(self, parent, IDindividu=None, dictFamillesRattachees={}):
        wx.Panel.__init__(self, parent, id=-1, name="panel_questionnaire", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        self.majEffectuee = False
        
        # Questionnaire
        self.staticbox_inscriptions = wx.StaticBox(self, -1, _(u"Questionnaire"))
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="individu", IDdonnee=IDindividu)
        self.ctrl_questionnaire.SetMinSize((20, 20)) 
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        # Inscriptions
        staticbox_inscriptions = wx.StaticBoxSizer(self.staticbox_inscriptions, wx.VERTICAL)
        grid_sizer_inscriptions = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_inscriptions.Add(self.ctrl_questionnaire, 1, wx.EXPAND, 0)
                
        grid_sizer_inscriptions.AddGrowableCol(0)
        grid_sizer_inscriptions.AddGrowableRow(0)
        staticbox_inscriptions.Add(grid_sizer_inscriptions, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_inscriptions, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.SetSizer(grid_sizer_base)
        self.Layout() 
        grid_sizer_base.Fit(self)


    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.majEffectuee == True :
            return
        self.ctrl_questionnaire.MAJ() 
        self.majEffectuee = True
        
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        valeurs = self.ctrl_questionnaire.GetValeurs() 
        dictReponses = self.ctrl_questionnaire.GetDictReponses() 
        dictValeursInitiales = self.ctrl_questionnaire.GetDictValeursInitiales()
        
        # Sauvegarde
        DB = GestionDB.DB()
        for IDquestion, reponse in valeurs.iteritems() :            
            # Si la réponse est différente de la réponse initiale
            if reponse != dictValeursInitiales[IDquestion] or reponse == "##DOCUMENTS##" :

                if dictReponses.has_key(IDquestion):
                    IDreponse = dictReponses[IDquestion]["IDreponse"]
                else:
                    IDreponse = None
                
                # Si c'est un document, on regarde s'il y a des docs à sauver
                sauvegarder = True
                if reponse == "##DOCUMENTS##" :
                    nbreDocuments = self.ctrl_questionnaire.GetNbreDocuments(IDquestion)
                    if nbreDocuments == 0 :
                        sauvegarder = False
                
                # Sauvegarde la réponse
                if sauvegarder == True :
                    listeDonnees = [    
                        ("IDquestion", IDquestion),
                        ("IDindividu", self.IDindividu),
                        ("reponse", reponse),
                        ]
                    if IDreponse == None :
                        IDreponse = DB.ReqInsert("questionnaire_reponses", listeDonnees)
                    else:
                        DB.ReqMAJ("questionnaire_reponses", listeDonnees, "IDreponse", IDreponse)
                
                # Sauvegarde du contrôle Porte-documents
                if reponse == "##DOCUMENTS##" :
                    nbreDocuments = self.ctrl_questionnaire.SauvegardeDocuments(IDquestion, IDreponse)
                    if nbreDocuments == 0 and IDreponse != None :
                        DB.ReqDEL("questionnaire_reponses", "IDreponse", IDreponse)
                
        DB.Close()
        
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.IDindividu = 20
        self.ctrl = Panel(panel, IDindividu=self.IDindividu)
##        self.ctrl.MAJ() 
        self.bouton_1 = CTRL_Bouton_image.CTRL(panel, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_1, 0, wx.EXPAND|wx.ALL, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton_1)
        
    def OnBouton1(self, event):
        self.ctrl.Sauvegarde()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()