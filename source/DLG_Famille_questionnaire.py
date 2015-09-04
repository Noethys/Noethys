#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Questionnaire
import GestionDB
import UTILS_Utilisateurs


class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_questionnaire", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.majEffectuee = False
        
        # Questionnaire
        self.staticbox_questionnaire = wx.StaticBox(self, -1, _(u"Questionnaire"))
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="famille", IDfamille=IDfamille)
        self.ctrl_questionnaire.SetMinSize((620, -1))

        # Mémo
        self.staticbox_memo = wx.StaticBox(self, -1, _(u"Mémo"))
        self.ctrl_memo = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        
        staticbox_questionnaire = wx.StaticBoxSizer(self.staticbox_questionnaire, wx.VERTICAL)
        grid_sizer_questionnaire = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_questionnaire.Add(self.ctrl_questionnaire, 1, wx.EXPAND, 0)
        grid_sizer_questionnaire.AddGrowableCol(0)
        grid_sizer_questionnaire.AddGrowableRow(0)
        staticbox_questionnaire.Add(grid_sizer_questionnaire, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_questionnaire, 1, wx.EXPAND|wx.ALL, 5)

        staticbox_memo = wx.StaticBoxSizer(self.staticbox_memo, wx.VERTICAL)
        grid_sizer_memo = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_memo.Add(self.ctrl_memo, 1, wx.EXPAND, 0)
        grid_sizer_memo.AddGrowableCol(0)
        grid_sizer_memo.AddGrowableRow(0)
        staticbox_memo.Add(grid_sizer_memo, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_memo, 1, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(1)
        grid_sizer_base.AddGrowableRow(0)
    
    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_questionnaires", "consulter", afficheMessage=False) == False : 
            return False
        return True
    
    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.majEffectuee == True :
            return
        self.ctrl_questionnaire.MAJ() 

        DB = GestionDB.DB()
        req = """SELECT memo FROM familles WHERE IDfamille=%d;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            memo = listeDonnees[0][0]
            if memo != None : 
                self.ctrl_memo.SetValue(memo)

        self.majEffectuee = True
        
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        valeurs = self.ctrl_questionnaire.GetValeurs() 
        dictReponses = self.ctrl_questionnaire.GetDictReponses() 
        dictValeursInitiales = self.ctrl_questionnaire.GetDictValeursInitiales()
        dirty = False
        
        DB = GestionDB.DB()
        
        # Sauvegarde du questionnaire
        for IDquestion, reponse in valeurs.iteritems():
            # Si la réponse est différente de la réponse initiale
            if reponse != dictValeursInitiales[IDquestion] or reponse == "##DOCUMENTS##" :
                dirty = True
                
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
                        ("IDfamille", self.IDfamille),
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

        # Sauvegarde du mémo
        memo = self.ctrl_memo.GetValue() 
        DB.ReqMAJ("familles", [("memo", memo),], "IDfamille", self.IDfamille)

        DB.Close()
        
        # Sauvegarde les données si nouveautés
        if dirty == True :
            self.ctrl_questionnaire.MAJ(importation=True)
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.IDfamille = 1
        self.ctrl = Panel(panel, IDfamille=self.IDfamille)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()