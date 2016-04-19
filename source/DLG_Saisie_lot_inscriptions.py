#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import CTRL_Bandeau
import OL_Saisie_lot_inscriptions
import UTILS_Dates
import datetime



class CTRL_Choix(wx.Choice):
    def __init__(self, parent, id=-1, mode="activites"):
        wx.Choice.__init__(self, parent, id) 
        self.mode = mode
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, IDactivite=0):
        self.listeID = []
        DB = GestionDB.DB()
        if IDactivite == None :
            IDactivite = 0
        if self.mode == "activites" : req = """SELECT IDactivite, nom FROM activites ORDER BY date_fin DESC;"""
        if self.mode == "groupes" : req = """SELECT IDgroupe, nom FROM groupes WHERE IDactivite=%d ORDER BY ordre;""" % IDactivite
        if self.mode == "categories" : req = """SELECT IDcategorie_tarif, nom FROM categories_tarifs WHERE IDactivite=%d ORDER BY nom;""" % IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeLabels = []
        for ID, nom in listeDonnees :
            if nom == None : nom = _(u"Activité inconnue")
            listeLabels.append(nom)
            self.listeID.append(ID)
        self.SetItems(listeLabels)
        self.Enable(len(listeLabels))
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    

    
    
# ------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez saisir ici un lot d'inscriptions. Sélectionnez les paramètres de l'inscription, cochez les individus à inscrire puis cliquez sur le bouton Ok. Utilisez la commande de Filtrage de liste pour effectuer une sélection rapide des individus.")
        titre = _(u"Saisir un lot d'inscriptions")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")

        # Paramètres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres de l'inscription"))

        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = CTRL_Choix(self, id=999, mode="activites")
        self.ctrl_activite.SetMinSize((60, -1))

        self.label_groupe = wx.StaticText(self, -1, _(u"Groupe :"))
        self.ctrl_groupe = CTRL_Choix(self, mode="groupes")
        self.ctrl_groupe.SetMinSize((150, -1))

        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie de tarif :"))
        self.ctrl_categorie = CTRL_Choix(self, mode="categories")
        self.ctrl_categorie.SetMinSize((150, -1))
                
        # Liste
        self.staticbox_individus_staticbox = wx.StaticBox(self, -1, _(u"Individus à inscrire"))
        
        self.ctrl_listview = OL_Saisie_lot_inscriptions.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_recherche = OL_Saisie_lot_inscriptions.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_activite)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_groupe)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_categorie)
        
        # Init contrôles
        self.ctrl_listview.MAJ()

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour inscrire les individus cochés"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.label_activite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_activite, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add( (5, 5), 0, 0, 0)
        grid_sizer_parametres.Add(self.label_groupe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_groupe, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add( (5, 5), 0, 0, 0)
        grid_sizer_parametres.Add(self.label_categorie, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(1)
        
        staticbox_parametres.Add(grid_sizer_parametres, 0, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(staticbox_parametres, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Contenu
        staticbox_individus = wx.StaticBoxSizer(self.staticbox_individus_staticbox, wx.VERTICAL)

        grid_sizer_individus = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_individus.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_individus.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_individus.AddGrowableRow(0)
        grid_sizer_individus.AddGrowableCol(0)
        
        staticbox_individus.Add(grid_sizer_individus, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(staticbox_individus, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def OnChoix(self, event=None):
        IDactivite = self.ctrl_activite.GetID()
        if event.GetId() == 999 :
            self.ctrl_groupe.MAJ(IDactivite=IDactivite)
            self.ctrl_categorie.MAJ(IDactivite=IDactivite)
            self.ctrl_listview.SetIDactivite(IDactivite)
            self.ctrl_listview.Filtrer()

    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)

    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)
        
    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)
        
    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Saisirunlotdinscriptions")
    
    def OnBoutonOk(self, event):
        IDactivite = self.ctrl_activite.GetID() 
        nomActivite = self.ctrl_activite.GetStringSelection()
        IDgroupe = self.ctrl_groupe.GetID() 
        nomGroupe = self.ctrl_groupe.GetStringSelection()
        IDcategorie_tarif = self.ctrl_categorie.GetID() 
        nomCategorie = self.ctrl_categorie.GetStringSelection()
        
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une activité dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if IDgroupe == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un groupe dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if IDcategorie_tarif == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une catégorie de tarif dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.ctrl_listview.Inscrire(IDactivite, nomActivite, IDgroupe, nomGroupe, IDcategorie_tarif, nomCategorie) 
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
