#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import datetime


class CTRL(wx.SearchCtrl):
    def __init__(self, parent, listeUtilisateurs=[], size=(-1,20), modeDLG=False):
        wx.SearchCtrl.__init__(self, parent, size=size, style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD)
        self.parent = parent
        self.listeUtilisateurs = listeUtilisateurs
        self.modeDLG = modeDLG
        self.SetDescriptiveText(u"   ")
        
        # Options
        self.ShowSearchButton(True)
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Cadenas.png", wx.BITMAP_TYPE_PNG))
        
        # Binds
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, event):
        self.Recherche()
        event.Skip() 
            
    def OnCancel(self, event):
        self.SetValue("")
        self.Recherche()
        event.Skip() 

    def OnDoSearch(self, event):
        self.Recherche()
        event.Skip() 
    
    def GetPasse(self, txtSearch=""):
        passe = str(int(datetime.datetime.today().strftime("%d%m%Y"))/3)
        return passe
        
    def Recherche(self):
        txtSearch = self.GetValue()
        #self.ShowCancelButton(len(txtSearch))
        if self.modeDLG == True :
            listeUtilisateurs = self.listeUtilisateurs
        else:
            listeUtilisateurs = self.GetGrandParent().listeUtilisateurs
        # Recherche de l'utilisateur
        for dictUtilisateur in listeUtilisateurs :
            IDutilisateur = dictUtilisateur["IDutilisateur"]
            if txtSearch == dictUtilisateur["mdp"] or (txtSearch == self.GetPasse(txtSearch) and dictUtilisateur["profil"] == "administrateur") :
                # Version pour la DLG du dessous
                if self.modeDLG == True :
                    self.GetParent().ChargeUtilisateur(dictUtilisateur)
                    self.SetValue("")
                    break
                # Version pour la barre Identification de la page d'accueil
                if self.modeDLG == False :
                    mainFrame = self.GetGrandParent()
                    if mainFrame.GetName() == "general" :
                        mainFrame.ChargeUtilisateur(dictUtilisateur)
                        self.SetValue("")
                        break
        self.Refresh() 
    



# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel)
        self.myOlv2 = wx.TextCtrl(panel, -1, "test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 0, wx.ALL|wx.EXPAND, 10)
        sizer_2.Add(self.myOlv2, 0, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.SetSize((500, 150))
        self.Layout()
        self.CenterOnScreen()

# --------------------------- DLG de saisie de mot de passe ----------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, id=-1, title=u"Identification", listeUtilisateurs=[], nomFichier=None):
        wx.Dialog.__init__(self, parent, id, title, name="DLG_mdp")
        self.parent = parent
        self.listeUtilisateurs = listeUtilisateurs
        self.nomFichier = nomFichier
        self.dictUtilisateur = None
        
        if self.nomFichier != None :
            self.SetTitle(u"Ouverture du fichier %s" % self.nomFichier)
            
        self.staticbox = wx.StaticBox(self, -1, "")
        self.label = wx.StaticText(self, -1, u"Veuillez saisir votre code d'identification personnel :")
        self.ctrl_mdp = CTRL(self, listeUtilisateurs=self.listeUtilisateurs, modeDLG=True)
        
        # Texte pour rappeller mot de passe du fichier Exemple
        self.label_exemple = wx.StaticText(self, -1, u"Le mot de passe des fichiers exemples est 'aze'")
        self.label_exemple.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.label_exemple.SetForegroundColour((130, 130, 130))
        if nomFichier == None or nomFichier.startswith("EXEMPLE_") == False :
            self.label_exemple.Show(False)
        
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.ctrl_mdp.SetFocus() 
        
    def __set_properties(self):
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.ctrl_mdp.SetMinSize((300, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # Intro
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)
        
        # Staticbox
        staticbox = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_contenu.Add(self.ctrl_mdp, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_exemple, 1, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.AddGrowableCol(0)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def ChargeUtilisateur(self, dictUtilisateur={}):
        self.dictUtilisateur = dictUtilisateur
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetDictUtilisateur(self):
        return self.dictUtilisateur
    


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, "GroupListView")
    dlg = Dialog(None, listeUtilisateurs=[])
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    print dlg.GetDictUtilisateur()
    app.MainLoop()
