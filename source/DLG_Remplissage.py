#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import os
import CTRL_Remplissage
import CTRL_Ticker_presents
import UTILS_Config

AFFICHE_PRESENTS = 1

ID_MODE_PLACES_INITIALES = wx.NewId()
ID_MODE_PLACES_PRISES = wx.NewId()
ID_MODE_PLACES_RESTANTES = wx.NewId()
ID_MODE_PLACES_ATTENTE = wx.NewId()
ID_LISTE_ATTENTE = wx.NewId()
ID_PARAMETRES = wx.NewId()
ID_OUTILS = wx.NewId()

ID_ACTUALISER = wx.NewId()
ID_IMPRIMER = wx.NewId()
ID_APERCU = wx.NewId()
ID_EXPORT_EXCEL = wx.NewId()
ID_EXPORT_TEXTE = wx.NewId()
ID_AIDE = wx.NewId()


class ToolBar(wx.ToolBar):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TB_FLAT|wx.TB_TEXT
        wx.ToolBar.__init__(self, *args, **kwds)
        
        # Boutons
        self.AddLabelTool(ID_MODE_PLACES_INITIALES, _(u"Places max."), wx.Bitmap("Images/32x32/Places_max.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Afficher le nombre de places maximal initial"), "")
        self.AddLabelTool(ID_MODE_PLACES_PRISES, _(u"Places prises"), wx.Bitmap("Images/32x32/Places_prises.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Afficher le nombre de places prises"), "")
        self.AddLabelTool(ID_MODE_PLACES_RESTANTES, _(u"Places dispo."), wx.Bitmap("Images/32x32/Places_dispo.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Afficher le nombre de places restantes"), "")
        self.AddLabelTool(ID_MODE_PLACES_ATTENTE, _(u"Places attente"), wx.Bitmap("Images/32x32/Places_attente.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Afficher le nombre de places en attente"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_LISTE_ATTENTE, _(u"Liste d'attente"), wx.Bitmap("Images/32x32/Liste_attente.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Afficher la liste d'attente"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_PARAMETRES, _(u"Param�tres"), wx.Bitmap("Images/32x32/Configuration2.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"S�lectionner les param�tres d'affichage"), "")
        self.AddLabelTool(ID_OUTILS, _(u"Outils"), wx.Bitmap("Images/32x32/Configuration.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Outils"), "")
        
        # Binds
        self.Bind(wx.EVT_TOOL, self.Mode_places_initiales, id=ID_MODE_PLACES_INITIALES)
        self.Bind(wx.EVT_TOOL, self.Mode_places_prises, id=ID_MODE_PLACES_PRISES)
        self.Bind(wx.EVT_TOOL, self.Mode_places_restantes, id=ID_MODE_PLACES_RESTANTES)
        self.Bind(wx.EVT_TOOL, self.Mode_places_attente, id=ID_MODE_PLACES_ATTENTE)
        self.Bind(wx.EVT_TOOL, self.Liste_attente, id=ID_LISTE_ATTENTE)
        self.Bind(wx.EVT_TOOL, self.Parametres, id=ID_PARAMETRES)
        self.Bind(wx.EVT_TOOL, self.MenuOutils, id=ID_OUTILS)
        
        self.SetToolBitmapSize((32, 32))
        self.Realize()
    
    def Mode_places_initiales(self, event):
        self.GetParent().dictDonnees["modeAffichage"] = "nbrePlacesInitial"
        self.GetParent().SetDictDonnees(self.GetParent().dictDonnees)
        self.GetParent().MAJ()

    def Mode_places_prises(self, event):
        self.GetParent().dictDonnees["modeAffichage"] = "nbrePlacesPrises"
        self.GetParent().SetDictDonnees(self.GetParent().dictDonnees)
        self.GetParent().MAJ()

    def Mode_places_restantes(self, event):
        self.GetParent().dictDonnees["modeAffichage"] = "nbrePlacesRestantes"
        self.GetParent().SetDictDonnees(self.GetParent().dictDonnees)
        self.GetParent().MAJ()
        
    def Mode_places_attente(self, event):
        self.GetParent().dictDonnees["modeAffichage"] = "nbreAttente"
        self.GetParent().SetDictDonnees(self.GetParent().dictDonnees)
        self.GetParent().MAJ()

    def Liste_attente(self, event):
        self.GetParent().OuvrirListeAttente()

    def Parametres(self, event):
        global AFFICHE_PRESENTS
        import DLG_Parametres_remplissage
        dictDonnees = self.GetParent().dictDonnees
        if dictDonnees.has_key("modeAffichage") :
            modeAffichage = dictDonnees["modeAffichage"]
        else:
            modeAffichage = "nbrePlacesPrises"
        largeurColonneUnites = self.GetParent().ctrl_remplissage.GetLargeurColonneUnite()
        abregeGroupes = self.GetParent().ctrl_remplissage.GetAbregeGroupes()
        affichePresents = AFFICHE_PRESENTS
        dlg = DLG_Parametres_remplissage.Dialog(None, dictDonnees, largeurColonneUnites, abregeGroupes=abregeGroupes, affichePresents=affichePresents)
        if dlg.ShowModal() == wx.ID_OK:
            # Mise � jour des param�tres du tableau
            listeActivites = dlg.GetListeActivites()
            listePeriodes = dlg.GetListePeriodes()
            dictDonnees = dlg.GetDictDonnees() 
            largeurColonnesUnites = dlg.GetLargeurColonneUnite()
            abregeGroupes = dlg.GetAbregeGroupes()
            # Mise � jour du tableau de remplissage
            self.GetParent().ctrl_remplissage.SetListeActivites(listeActivites)
            self.GetParent().ctrl_remplissage.SetListePeriodes(listePeriodes)
            self.GetParent().ctrl_remplissage.SetLargeurColonneUnite(largeurColonnesUnites)
            self.GetParent().ctrl_remplissage.SetAbregeGroupes(abregeGroupes)
            self.GetParent().ctrl_remplissage.MAJ()
            dictDonnees["modeAffichage"] = modeAffichage
            self.GetParent().SetDictDonnees(dictDonnees)
            # Affiche ticker des pr�sents
            AFFICHE_PRESENTS = dlg.GetAffichePresents()
            UTILS_Config.SetParametre("remplissage_affiche_presents", int(AFFICHE_PRESENTS))
            # MAJ
            self.GetParent().MAJ()
        dlg.Destroy()

    def MenuOutils(self, event):
        # Cr�ation du menu Outils
        menuPop = wx.Menu()
            
        item = wx.MenuItem(menuPop, ID_APERCU, _(u"Aper�u avant impression"), _(u"Imprimer la liste des effectifs affich�e"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=ID_APERCU)
        
        item = wx.MenuItem(menuPop, ID_IMPRIMER, _(u"Imprimer"), _(u"Imprimer la liste des effectifs affich�e"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=ID_IMPRIMER)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_EXPORT_TEXTE, _(u"Exporter au format Texte"), _(u"Exporter au format Texte"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().ctrl_remplissage.ExportTexte, id=ID_EXPORT_TEXTE)
        
        item = wx.MenuItem(menuPop, ID_EXPORT_EXCEL, _(u"Exporter au format Excel"), _(u"Exporter au format Excel"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().ctrl_remplissage.ExportExcel, id=ID_EXPORT_EXCEL)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_ACTUALISER, _(u"Actualiser"), _(u"Actualiser l'affichage"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Actualiser2.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Actualiser, id=ID_ACTUALISER)

        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_AIDE, _(u"Aide"), _(u"Aide"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Aide, id=ID_AIDE)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
    def Actualiser(self, event):
        self.GetParent().ctrl_remplissage.MAJ()

    def Imprimer(self, event):
        self.GetParent().Imprimer()

    def Apercu(self, event):
        self.GetParent().Apercu()

    def Aide(self, event):
        self.GetParent().Aide()


    
class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, name="panel_remplissage", id=-1, style=wx.TAB_TRAVERSAL)
        
        # R�cup�ration des param�tres d'affichage
        self.dictDonnees = self.GetParametres() 
        
        # Cr�ation des contr�les
        self.toolBar = ToolBar(self)
        self.ctrl_remplissage = CTRL_Remplissage.CTRL(self, self.dictDonnees)
        
        self.ctrl_presents = CTRL_Ticker_presents.CTRL(self, delai=60, listeActivites=[15,])
        self.ctrl_presents.Show(False) 

        global AFFICHE_PRESENTS
        AFFICHE_PRESENTS = UTILS_Config.GetParametre("remplissage_affiche_presents", 1) 

        if self.dictDonnees.has_key("modeAffichage") :
            if self.dictDonnees["modeAffichage"] == "nbrePlacesInitial" : self.toolBar.ToggleTool(ID_MODE_PLACES_INITIALES, True)
            if self.dictDonnees["modeAffichage"] == "nbrePlacesPrises" : self.toolBar.ToggleTool(ID_MODE_PLACES_PRISES, True)
            if self.dictDonnees["modeAffichage"] == "nbrePlacesRestantes" : self.toolBar.ToggleTool(ID_MODE_PLACES_RESTANTES, True)
            if self.dictDonnees["modeAffichage"] == "nbreAttente" : self.toolBar.ToggleTool(ID_MODE_PLACES_ATTENTE, True)
            
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        self.grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        self.grid_sizer_base.Add(self.toolBar, 1, wx.EXPAND|wx.ALL, 0)
        self.grid_sizer_base.Add(self.ctrl_presents, 1, wx.EXPAND|wx.ALL, 0)
        self.grid_sizer_base.Add(self.ctrl_remplissage, 1, wx.EXPAND|wx.ALL, 0)
        self.grid_sizer_base.AddGrowableRow(2)
        self.grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(self.grid_sizer_base)
        self.Layout()
    
    def GetParametres(self):
        defaut = {
            'listeActivites': [], 
            'listeSelections': (), 
            'listePeriodes': [], 
            'modeAffichage': 'nbrePlacesPrises', 
            'dateDebut': None, 
            'dateFin': None, 
            'annee': 2010, 
            'page': 0,
            }
        dictDonnees = UTILS_Config.GetParametre("dict_selection_periodes_activites", defaut)
        return dictDonnees
    
    def SetDictDonnees(self, dictDonnees={}):
        if len(dictDonnees) != 0 :
            self.dictDonnees = dictDonnees
        # M�morisation du dict de Donn�es de s�lection
        self.ctrl_remplissage.SetDictDonnees(self.dictDonnees)
        # M�morisation du dict de donn�es dans le config.dat
        UTILS_Config.SetParametre("dict_selection_periodes_activites", self.dictDonnees)
    
    def MAJ(self):
        self.ctrl_remplissage.MAJ() 
        self.MAJpresents() 
    
    def MAJpresents(self):
        """ MAJ du Ticker des pr�sents """
        listeActivites = self.dictDonnees["listeActivites"]
        self.ctrl_presents.SetActivites(listeActivites)
        self.ctrl_presents.MAJ() 
    
    def AffichePresents(self, etat=True):
        """ Affiche ou cache le Ticker des pr�sents """
        if AFFICHE_PRESENTS == 0 :
            etat = 0
        self.ctrl_presents.Show(etat)
        self.grid_sizer_base.Layout()

    def Imprimer(self):
        self.ctrl_remplissage.Imprimer() 

    def Apercu(self):
        self.ctrl_remplissage.Apercu() 

    def Aide(self):
        import UTILS_Aide
        UTILS_Aide.Aide("Leseffectifs")

    def OuvrirListeAttente(self):
        dictEtatPlaces = self.ctrl_remplissage.GetEtatPlaces()
        dictUnitesRemplissage = self.ctrl_remplissage.dictUnitesRemplissage
        import DLG_Attente
        dlg = DLG_Attente.Dialog(self, dictDonnees=self.dictDonnees, dictEtatPlaces=dictEtatPlaces, dictUnitesRemplissage=dictUnitesRemplissage)
        dlg.ShowModal()
        dlg.Destroy() 

    def OuvrirListeRefus(self):
        dictEtatPlaces = self.ctrl_remplissage.GetEtatPlaces()
        dictUnitesRemplissage = self.ctrl_remplissage.dictUnitesRemplissage
        import DLG_Refus
        dlg = DLG_Refus.Dialog(self, dictDonnees=self.dictDonnees, dictEtatPlaces=dictEtatPlaces, dictUnitesRemplissage=dictUnitesRemplissage)
        dlg.ShowModal()
        dlg.Destroy() 


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        self.ctrl.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()