#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime

import GestionDB
import CTRL_Bandeau
import OL_Liste_nominative_soldes
import CTRL_Saisie_date
import CTRL_Selection_activites

try: import psyco; psyco.full()
except: pass



class CTRL_Activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.dictDonnees = {}
        self.MAJ() 
    
    def MAJ(self):
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY nom
        ;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()      
        DB.Close() 
        if len(listeActivites) == 0 :
            self.Enable(False)
        listeLabels = []
        index = 0
        for IDactivite, nom in listeActivites :
            self.dictDonnees[index] = IDactivite
            listeLabels.append(nom)
            index += 1
        self.SetItems(listeLabels)

    def SetActivite(self, IDactivite=None):
        for index, IDactiviteTmp in self.dictDonnees.iteritems() :
            if IDactiviteTmp == IDactivite :
                self.SetSelection(index)

    def GetActivite(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeGroupes = []
        self.dictGroupes = {}
        
    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeGroupes, self.dictGroupes = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeGroupes = []
        dictGroupes = {}
        if len(self.listeActivites) == 0 :
            return listeGroupes, dictGroupes 

        # Condition Activités
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        DB = GestionDB.DB()
        req = """SELECT IDgroupe, groupes.IDactivite, groupes.nom, activites.abrege
        FROM groupes
        LEFT JOIN activites ON activites.IDactivite = groupes.IDactivite
        WHERE groupes.IDactivite IN %s
        ORDER BY groupes.nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDgroupe, IDactivite, nom, abregeActivite in listeDonnees :
            label = u"%s (%s)" % (nom, abregeActivite)
            dictTemp = { "nom" : label, "IDactivite" : IDactivite}
            dictGroupes[IDgroupe] = dictTemp
            listeGroupes.append((label, IDgroupe))
        listeGroupes.sort()
        return listeGroupes, dictGroupes

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDgroupe in self.listeGroupes :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeGroupes)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeGroupes[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            ID = self.listeGroupes[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeGroupes(self):
        return self.GetIDcoches() 
    
    def GetDictGroupes(self):
        return self.dictGroupes
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeCategories = []
        self.dictCategories = {}
        
    def SetActivites(self, listeActivites=None):
        self.listeActivites = listeActivites
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeCategories, self.dictCategories = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeCategories = []
        dictCategories = {}
        if len(self.listeActivites) == 0 :
            return listeCategories, dictCategories 

        # Condition Activités
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, categories_tarifs.IDactivite, categories_tarifs.nom, activites.abrege
        FROM categories_tarifs
        LEFT JOIN activites ON activites.IDactivite = categories_tarifs.IDactivite
        WHERE categories_tarifs.IDactivite IN %s
        ORDER BY categories_tarifs.nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDcategorie_tarif, IDactivite, nom, abregeActivite in listeDonnees :
            label = u"%s (%s)" % (nom, abregeActivite)
            dictTemp = { "nom" : label, "IDactivite" : IDactivite}
            dictCategories[IDcategorie_tarif] = dictTemp
            listeCategories.append((label, IDcategorie_tarif))
        listeCategories.sort()
        return listeCategories, dictCategories

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDcategorie_tarif in self.listeCategories :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeCategories)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeCategories[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeCategories)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeCategories)):
            ID = self.listeCategories[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeCategories(self):
        return self.GetIDcoches() 
    
    def GetDictCategories(self):
        return self.dictCategories
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Presents(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_presents", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.radio_inscrits = wx.RadioButton(self, -1, _(u"Toutes les prestations"), style=wx.RB_GROUP)
        self.radio_presents = wx.RadioButton(self, -1, _(u"Uniquement les prestations"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inscrits)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_presents)
        
        self.OnRadio(None)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez ici une date de début"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici une date de fin"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        grid_sizer_base.Add(self.radio_inscrits, 0, 0, 0)
        grid_sizer_base.Add(self.radio_presents, 0, 0, 0)
        
        grid_sizer_dates = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_dates, 1, wx.LEFT|wx.EXPAND, 18)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadio(self, event): 
        if self.radio_inscrits.GetValue() == True :
            etat = False
        else:
            etat = True
        self.label_date_debut.Enable(etat)
        self.label_date_fin.Enable(etat)
        self.ctrl_date_debut.Enable(etat)
        self.ctrl_date_fin.Enable(etat)

    def GetPresents(self):
        if self.radio_inscrits.GetValue() == True :
            # Tous les inscrits
            return None
        else:
            # Uniquement les présents
            date_debut = self.ctrl_date_debut.GetDate()
            if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
                dlg = wx.MessageDialog(self, _(u"La date de début ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False
            
            date_fin = self.ctrl_date_fin.GetDate()
            if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
                dlg = wx.MessageDialog(self, _(u"La date de fin ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
            
            if date_debut > date_fin :
                dlg = wx.MessageDialog(self, _(u"La date de début est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
            
            return (date_debut, date_fin)

# -------------------------------------------------------------------------------------------------------------------------

class Parametres(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listview = listview
        
        # Activité
        self.box_activite_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activite = CTRL_Selection_activites.CTRL(self)
        self.ctrl_activite.SetMinSize((240, -1))
        
        # Groupes
        self.box_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((-1, 50))
        
        # Catégories
        self.box_categories_staticbox = wx.StaticBox(self, -1, _(u"Catégories"))
        self.ctrl_categories = CTRL_Categories(self)
        self.ctrl_categories.SetMinSize((-1, 50))
        
        # Présents
        self.staticbox_presents_staticbox = wx.StaticBox(self, -1, _(u"Prestations"))
        self.ctrl_presents = CTRL_Presents(self)
        
        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)

    def __set_properties(self):
        self.ctrl_activite.SetToolTipString(_(u"Sélectionnez une activité"))
        self.ctrl_groupes.SetToolTipString(_(u"Cochez les groupes à afficher"))
        self.ctrl_categories.SetToolTipString(_(u"Cochez les catégories à afficher"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        # Activité
        box_activite = wx.StaticBoxSizer(self.box_activite_staticbox, wx.VERTICAL)
        box_activite.Add(self.ctrl_activite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_activite, 1, wx.EXPAND, 0)
        
        # Groupes
        box_groupes = wx.StaticBoxSizer(self.box_groupes_staticbox, wx.VERTICAL)
        box_groupes.Add(self.ctrl_groupes, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_groupes, 1, wx.EXPAND, 0)
        
        # Catégories
        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        box_categories.Add(self.ctrl_categories, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_categories, 1, wx.EXPAND, 0)
        
        # Inscrits / Présents
        staticbox_presents = wx.StaticBoxSizer(self.staticbox_presents_staticbox, wx.VERTICAL)
        staticbox_presents.Add(self.ctrl_presents, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_presents, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Bouton Actualiser
        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnCheckActivites(self, event=None):
        listeActivites = self.ctrl_activite.GetActivites()
        self.ctrl_groupes.SetActivites(listeActivites)
        self.ctrl_categories.SetActivites(listeActivites)
        
    def OnBoutonActualiser(self, event): 
        # Récupération des paramètres
        listeActivites = self.ctrl_activite.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        listeGroupes = self.ctrl_groupes.GetListeGroupes()
        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        listeCategories = self.ctrl_categories.GetListeCategories()
        if len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        presents = self.ctrl_presents.GetPresents()
        if presents == False :
            return
        
        # MAJ du listview
        self.parent.ctrl_listview.MAJ(listeActivites=listeActivites, listeGroupes=listeGroupes, listeCategories=listeCategories, presents=presents)





# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter et imprimer la liste des soldes individuels pour les activités et la période de votre choix. Sélectionnez vos paramètres avant de cliquer sur le bouton 'Rafraîchir la liste' pour afficher les résultats. Les données peuvent être ensuite imprimées ou exportées au format Texte ou Excel.")
        titre = _(u"Liste des soldes individuels")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")

        self.listviewAvecFooter = OL_Liste_nominative_soldes.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Liste_nominative_soldes.CTRL_Outils(self, listview=self.ctrl_listview)
        self.ctrl_parametres = Parametres(self, listview=self.ctrl_listview)
        
        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init contrôles
        self.ctrl_listview.MAJ() 

    def __set_properties(self):
        self.bouton_ouvrir_fiche.SetToolTipString(_(u"Cliquez ici pour ouvrir la fiche de la famille sélectionnée dans la liste"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Texte"))
        self.bouton_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND | wx.LEFT, 5)
        
        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OuvrirFiche(self, event):
        self.ctrl_listview.OuvrirFicheFamille(None)

    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)
        
    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)

    def ExportTexte(self, event):
        self.ctrl_listview.ExportTexte(None)

    def ExportExcel(self, event):
        self.ctrl_listview.ExportExcel(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedessoldesindividuels")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
