#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import CTRL_Bandeau
import OL_Historique
import UTILS_Historique

try: import psyco; psyco.full()
except: pass



class CTRL_Utilisateur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
        self.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix)
    
    def OnChoix(self, event):
        self.parent.SetUtilisateur(self.GetID())
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [ _(u"<< Tous les utilisateurs >>"),]
        self.dictDonnees = { 0 : {"ID":None}, }
        db = GestionDB.DB()
        req = """SELECT IDutilisateur, nom, prenom
        FROM utilisateurs
        ORDER BY nom, prenom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        index = 1
        for IDutilisateur, nom, prenom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDutilisateur }
            listeItems.append(u"%s %s" % (nom, prenom))
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
        self.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix)
    
    def OnChoix(self, event):
        self.parent.SetCategorie(self.GetID())
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [ _(u"<< Toutes les catégories >>"),]
        self.dictDonnees = { 0 : {"ID":None}, }
        index = 1
        for IDcategorie, label in UTILS_Historique.CATEGORIES.iteritems() :
            self.dictDonnees[index] = { "ID" : IDcategorie }
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Famille(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
        self.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix)
    
    def OnChoix(self, event):
        self.parent.SetFamille(self.GetID())
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [ _(u"<< Toutes les familles >>"),]
        self.dictDonnees = { 0 : {"ID":None}, }
        index = 1
        listeTitulaires = []
        for IDfamille, dictFamille in self.parent.ctrl_listview.titulaires.iteritems() :
            nomsTitulaires = dictFamille["titulairesSansCivilite"]
            listeTitulaires.append((nomsTitulaires, IDfamille))
        listeTitulaires.sort()
        for nomsTitulaires, IDfamille in listeTitulaires :
            self.dictDonnees[index] = { "ID" : IDfamille }
            listeItems.append(nomsTitulaires)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Individu(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
        self.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix)
    
    def OnChoix(self, event):
        self.parent.SetIndividu(self.GetID())
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [ _(u"<< Tous les individus >>"),]
        self.dictDonnees = { 0 : {"ID":None}, }
        db = GestionDB.DB()
        req = """SELECT IDindividu, nom, prenom
        FROM individus
        ORDER BY nom, prenom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        index = 1
        for IDindividu, nom, prenom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDindividu }
            listeItems.append(u"%s %s" % (nom, prenom))
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

# -------------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDutilisateur=None, IDfamille=None, IDindividu=None, IDcategorie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici consulter l'historique des actions effectuées dans Noethys.")
        titre = _(u"Historique")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Historique.png")
        
        # Liste
        self.ctrl_listview = OL_Historique.ListView(self, id=-1, IDutilisateur=IDutilisateur, IDfamille=IDfamille, IDindividu=IDindividu, IDcategorie=IDcategorie, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((100, 100))
        self.ctrl_listview.MAJ()
        self.ctrl_recherche = OL_Historique.CTRL_Outils(self, listview=self.ctrl_listview)
        
        # Filtres
        self.staticbox_filtres_staticbox = wx.StaticBox(self, -1, _(u"Filtres"))
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"))
        self.ctrl_utilisateur = CTRL_Utilisateur(self)
        self.label_famille = wx.StaticText(self, -1, _(u"Famille :"))
        self.ctrl_famille = CTRL_Famille(self)
        self.label_individu = wx.StaticText(self, -1, _(u"Individu :"))
        self.ctrl_individu = CTRL_Individu(self)
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self)
        
        if IDutilisateur != None : 
            self.ctrl_utilisateur.SetID(IDutilisateur)
            self.ctrl_utilisateur.Enable(False)
##            self.label_utilisateur.Show(False)
##            self.ctrl_utilisateur.Show(False)
        if IDfamille != None : 
            self.ctrl_famille.SetID(IDfamille)
            self.ctrl_famille.Enable(False)
##            self.label_famille.Show(False)
##            self.ctrl_famille.Show(False)
        if IDindividu != None : 
            self.ctrl_individu.SetID(IDindividu)
            self.ctrl_individu.Enable(False)
##            self.label_individu.Show(False)
##            self.ctrl_individu.Show(False)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
    def __set_properties(self):
        self.SetTitle(_(u"Historique"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((1000, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Filtres
        staticbox_filtres = wx.StaticBoxSizer(self.staticbox_filtres_staticbox, wx.VERTICAL)
        grid_sizer_filtres = wx.FlexGridSizer(rows=1, cols=11, vgap=5, hgap=5)
        
        grid_sizer_filtres.Add(self.label_utilisateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_utilisateur, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add( (5, 5), 0, 0, 0)
        grid_sizer_filtres.Add(self.label_famille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_famille, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add( (5, 5), 0, 0, 0)
        grid_sizer_filtres.Add(self.label_individu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_individu, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add( (5, 5), 0, 0, 0)
        grid_sizer_filtres.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)

        staticbox_filtres.Add(grid_sizer_filtres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_filtres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Liste
        grid_sizer_base.Add(self.ctrl_listview, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_recherche, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def Ajouter(self, event):
        self.ctrl_listview.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)
    
    def SetUtilisateur(self, IDutilisateur=None):
        self.ctrl_listview.SetUtilisateur(IDutilisateur)

    def SetCategorie(self, IDcategorie=None):
        self.ctrl_listview.SetCategorie(IDcategorie)

    def SetFamille(self, IDfamille=None):
        self.ctrl_listview.SetFamille(IDfamille)

    def SetIndividu(self, IDindividu=None):
        self.ctrl_listview.SetIndividu(IDindividu)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Historique")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
