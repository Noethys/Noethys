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
import os
import datetime
import GestionDB
import  wx.lib.filebrowsebutton as filebrowse

import OL_Badgeage_actions
from DLG_Badgeage_interface import LISTE_STYLES, LISTE_THEMES
from DATA_Tables import DB_DATA as DICT_TABLES



class CTRL_Style(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictStyle in LISTE_STYLES :
            listeItems.append(dictStyle["label"])
            self.dictDonnees[index] = dictStyle["code"]
            index += 1
        self.SetItems(listeItems)
        self.Select(0)

    def SetID(self, code=""):
        for index, codeTemp in self.dictDonnees.iteritems():
            if codeTemp == code :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

# -----------------------------------------------------------------------------------------------------------------------------

class CTRL_Theme(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.SetMinSize((100, 70))
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictTheme in LISTE_THEMES :
            listeItems.append(dictTheme["label"])
            self.dictDonnees[index] = dictTheme["code"]
            index += 1
        self.SetItems(listeItems)
        self.Select(0)

    def SetID(self, code=""):
        for index, codeTemp in self.dictDonnees.iteritems():
            if codeTemp == code :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

# -----------------------------------------------------------------------------------------------------------------------------


class CTRL_Activite(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((100, 70))
        self.data = []
        self.Importation() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeValeurs = []
        for IDactivite, nom, abrege in listeDonnees :
            listeValeurs.append((IDactivite, nom, False)) 
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


class CTRL_Interface(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Interface
        self.box_interface_staticbox = wx.StaticBox(self, -1, _(u"Interface"))
        self.label_style = wx.StaticText(self, -1, _(u"Style :"))
        self.ctrl_style = CTRL_Style(self)
        self.label_theme = wx.StaticText(self, -1, _(u"Thème :"))
        self.ctrl_theme = CTRL_Theme(self)
        self.label_image = wx.StaticText(self, -1, _(u"Image :"))
        self.ctrl_image = wx.TextCtrl(self, -1, u"")
        self.bouton_image = wx.Button(self, -1, u"...", size=(20, 20))
        
        # Identification
        self.box_identification_staticbox = wx.StaticBox(self, -1, _(u"Système d'identification"))
        self.radio_barre = wx.RadioButton(self, -1, _(u"Barre numérique"), style=wx.RB_GROUP)
        self.radio_clavier = wx.RadioButton(self, -1, _(u"Barre et clavier numérique"))
        self.radio_liste = wx.RadioButton(self, -1, _(u"Liste des individus"))
        self.check_activites = wx.CheckBox(self, -1, _(u"Afficher uniquement les inscrits aux activités :"))
        self.ctrl_activites = CTRL_Activite(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixIdentification, self.radio_barre)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixIdentification, self.radio_clavier)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixIdentification, self.radio_liste)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckActivites, self.check_activites)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImage, self.bouton_image)
        self.Bind(wx.EVT_LISTBOX, self.OnChoixTheme, self.ctrl_theme)
        
        # Init contrôles
        self.OnChoixTheme(None)
        self.OnChoixIdentification(None)

    def __set_properties(self):
        self.ctrl_style.SetToolTipString(_(u"Sélectionnez un style d'interface"))
        self.ctrl_theme.SetToolTipString(_(u"Sélectionnez un thème"))
        self.radio_barre.SetToolTipString(_(u"Recommandé pour la saisie avec lecteur de code-barres"))
        self.radio_clavier.SetToolTipString(_(u"Recommandé pour la saisie avec écrans tactiles"))
        self.radio_liste.SetToolTipString(_(u"Recommandé pour la saisie avec écrans tactiles"))
        self.check_activites.SetToolTipString(_(u"Cochez cette case pour afficher uniquement les inscrits aux activités sélectionnées"))
        self.ctrl_activites.SetToolTipString(_(u"Cochez les activités"))
        self.bouton_image.SetToolTipString(_(u"Cliquez ici pour sélectionner une image personnalisée"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Interface
        box_interface = wx.StaticBoxSizer(self.box_interface_staticbox, wx.VERTICAL)
        grid_sizer_interface = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_interface.Add(self.label_style, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_interface.Add(self.ctrl_style, 0, wx.EXPAND, 0)
        grid_sizer_interface.Add(self.label_theme, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_interface.Add(self.ctrl_theme, 0, wx.EXPAND, 0)
        grid_sizer_interface.Add(self.label_image, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_image = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_image.Add(self.ctrl_image, 1, wx.EXPAND, 0)
        grid_sizer_image.Add(self.bouton_image, 0, wx.EXPAND, 0)
        grid_sizer_interface.Add(grid_sizer_image, 0, wx.EXPAND, 0)
        
        grid_sizer_interface.AddGrowableRow(1)
        grid_sizer_interface.AddGrowableCol(1)
        box_interface.Add(grid_sizer_interface, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_interface, 1, wx.EXPAND, 0)
        
        # Identification
        sizer_identification = wx.StaticBoxSizer(self.box_identification_staticbox, wx.VERTICAL)
        grid_sizer_identification = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_identification.Add(self.radio_barre, 0, 0, 0)
        grid_sizer_identification.Add(self.radio_clavier, 0, 0, 0)
        grid_sizer_identification.Add(self.radio_liste, 0, 0, 0)
        grid_sizer_identification.Add(self.check_activites, 0, wx.LEFT, 20)
        grid_sizer_identification.Add(self.ctrl_activites, 0, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_identification.AddGrowableRow(4)
        grid_sizer_identification.AddGrowableCol(0)
        sizer_identification.Add(grid_sizer_identification, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_identification, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableCol(1)
    
    def OnChoixTheme(self, event):
        if self.ctrl_theme.GetID() == "personnalise" :
            etat = True
        else :
            etat = False
        self.ctrl_image.Enable(etat)
        self.bouton_image.Enable(etat)

    def OnBoutonImage(self, event):
        # Sélection d'une image
        wildcard = "Toutes les images (*.jpg, *.png, *.gif)|*.jpg;*.png;*.gif|"     \
                        "Images JPEG (*.jpg)|*.jpg|"     \
                        "Images PNG (*.png)|*.png|"     \
                        "Images GIF (*.gif)|*.gif|"     \
                        "All files (*.*)|*.*"
        # Récupération du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture de la fenêtre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une image"),
            defaultDir=cheminDefaut, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            chemin = dlg.GetPath()
            self.ctrl_image.SetValue(chemin)
            dlg.Destroy()
        else:
            dlg.Destroy()

    def OnChoixIdentification(self, event): 
        self.check_activites.Enable(self.radio_liste.GetValue())
        self.OnCheckActivites(None)

    def OnCheckActivites(self, event): 
        if self.radio_liste.GetValue() == True and self.check_activites.GetValue() == True :
            self.ctrl_activites.Enable(True)
        else :
            self.ctrl_activites.Enable(False)

    def Validation(self):
        if self.ctrl_theme.GetID() == "personnalise" :
            chemin = self.ctrl_image.GetValue()
            if chemin == "" :
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné le thème 'personnalisé' mais vous n'avez sélectionné aucune image !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
##            try :
##                testBmp = wx.Bitmap(chemin, wx.BITMAP_TYPE_ANY)
##            except :
##                dlg = wx.MessageDialog(self, _(u"L'image personnalisée que vous avez sélectionné ne semble pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return False
        
        if self.radio_liste.GetValue() and self.check_activites.GetValue() :
            if len(self.ctrl_activites.GetIDcoches()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné l'affichage des inscrits mais sans sélectionner d'activités !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        return True
            

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDprocedure=None, defaut=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDprocedure = IDprocedure
        self.defaut = defaut
        
        self.listeInitialeActions = []
        self.listeInitialeMessages = []
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")

        # Interface
        self.ctrl_interface = CTRL_Interface(self)

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.check_vocal = wx.CheckBox(self, -1, _(u"Activer la synthèse vocale"))
        self.check_vocal.SetValue(True)
        self.check_tutoiement = wx.CheckBox(self, -1, _(u"Activer le tutoiement"))
        self.check_confirmation = wx.CheckBox(self, -1, _(u"Demander une confirmation de l'identité"))

        # Actions
        self.box_actions_staticbox = wx.StaticBox(self, -1, _(u"Actions"))
        self.ctrl_actions = OL_Badgeage_actions.ListView(self, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_actions.MAJ() 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMonter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDescendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init
        if self.IDprocedure != None :
            self.Importation() 

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une procédure"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour cette procédure"))
        self.check_vocal.SetToolTipString(_(u"Cochez cette case pour activer la synthèse vocale dans cette procédure"))
        self.check_tutoiement.SetToolTipString(_(u"Cochez cette case pour utiliser le tutoiement au lieu du vouvoiement"))
        self.check_confirmation.SetToolTipString(_(u"Noethys demandera la confirmation de l'identité de l'individu après son identification"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter une action"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'action sélectionnée"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'action sélectionnée"))
        self.bouton_monter.SetToolTipString(_(u"Cliquez ici pour faire monter l'action sélectionnée"))
        self.bouton_descendre.SetToolTipString(_(u"Cliquez ici pour faire descendre l'action sélectionnée"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((750, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Interface
        grid_sizer_base.Add(self.ctrl_interface, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_options.Add(self.check_vocal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.check_tutoiement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.check_confirmation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Actions
        box_actions = wx.StaticBoxSizer(self.box_actions_staticbox, wx.VERTICAL)
        grid_sizer_actions = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_actions.Add(self.ctrl_actions, 1, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_actions.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_actions.AddGrowableRow(0)
        grid_sizer_actions.AddGrowableCol(0)
        box_actions.Add(grid_sizer_actions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_actions, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAjouter(self, event): 
        self.ctrl_actions.Ajouter()

    def OnBoutonModifier(self, event): 
        self.ctrl_actions.Modifier()

    def OnBoutonSupprimer(self, event): 
        self.ctrl_actions.Supprimer()

    def OnBoutonMonter(self, event): 
        self.ctrl_actions.Monter()

    def OnBoutonDescendre(self, event): 
        self.ctrl_actions.Descendre()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Paramtreruneprocdure")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # Vérification de la saisie
        nom_procedure = self.ctrl_nom.GetValue()
        if nom_procedure == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de procédure !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
        
        etat = self.ctrl_interface.Validation() 
        if etat == False :
            return False
        
        # Actions
        listeActions = self.ctrl_actions.GetDonnees()
        if len(listeActions) == 0 :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir saisir d'action ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return False
        
        # Sauvegarde
        etat = self.Sauvegarde() 
        if etat == False :
            return False
        
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)

    def Importation(self):
        """Importation des données """
        DB = GestionDB.DB()
        
        # Importation de la procédure
        req = """SELECT nom, style, theme, image, systeme, activites, confirmation, vocal, tutoiement
        FROM badgeage_procedures
        WHERE IDprocedure=%d;
        """ % self.IDprocedure
        DB.ExecuterReq(req)
        listeProcedures = DB.ResultatReq()
        if len(listeProcedures) == 0 : return
        nom, style, theme, image, systeme, activites, confirmation, vocal, tutoiement = listeProcedures[0]
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_interface.ctrl_style.SetID(style)
        self.ctrl_interface.ctrl_theme.SetID(theme)
        self.ctrl_interface.OnChoixTheme(None)
        if image != None :
            self.ctrl_interface.ctrl_image.SetValue(image) 
        if systeme == "barre_numerique" : self.ctrl_interface.radio_barre.SetValue(True) 
        if systeme == "clavier_numerique" : self.ctrl_interface.radio_clavier.SetValue(True) 
        if systeme == "liste_individus" : self.ctrl_interface.radio_liste.SetValue(True) 
        self.ctrl_interface.OnChoixIdentification(None)
        if activites != None :
            listeTemp = activites.split(";")
            listeActivites = []
            for IDactivite in listeTemp :
                listeActivites.append(int(IDactivite))
            self.ctrl_interface.check_activites.SetValue(True)
            self.ctrl_interface.ctrl_activites.SetIDcoches(listeActivites)
        self.check_confirmation.SetValue(confirmation)
        self.ctrl_interface.OnCheckActivites(None)
        self.check_vocal.SetValue(vocal)
        self.check_tutoiement.SetValue(tutoiement)

        # Importation des actions
        listeChamps = []
        for nom, type, info in DICT_TABLES["badgeage_actions"] :
            listeChamps.append(nom)
        req = """SELECT %s
        FROM badgeage_actions 
        WHERE IDprocedure=%d
        ORDER BY ordre
        ;""" % (", ".join(listeChamps), self.IDprocedure)
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        
        listeDonnees = []
        ordre = 1
        for ligne in listeActions :
            index = 0
            dictTemp = {}
            for valeur in ligne :
                nomChamp = listeChamps[index]
                dictTemp[nomChamp] = valeur
                index += 1
            dictTemp["ordre"] = ordre
            
            # Importation des messages
            if dictTemp["action"] == "message" :
                req = """SELECT IDmessage, message
                FROM badgeage_messages
                WHERE IDaction=%d
                ;""" % dictTemp["IDaction"]
                DB.ExecuterReq(req)
                listeTemp = DB.ResultatReq()
                listeMessages = []
                for IDmessage, message in listeTemp :
                    listeMessages.append((IDmessage, message))
                    self.listeInitialeMessages.append(IDmessage)
                dictTemp["action_messages"] = listeMessages
            
            self.listeInitialeActions.append(dictTemp["IDaction"])
            listeDonnees.append(dictTemp)
            ordre += 1
        
        self.ctrl_actions.SetDonnees(listeDonnees)
        
        DB.Close()


    def Sauvegarde(self):
        """ Sauvegarde de la procédure et des actions """
        DB = GestionDB.DB()

        nom = self.ctrl_nom.GetValue()
        style = self.ctrl_interface.ctrl_style.GetID() 
        theme = self.ctrl_interface.ctrl_theme.GetID() 
        if theme == "personnalise" :
            image = self.ctrl_interface.ctrl_image.GetValue() 
        else :
            image = None
        if self.ctrl_interface.radio_barre.GetValue() : systeme = "barre_numerique"
        if self.ctrl_interface.radio_clavier.GetValue() : systeme = "clavier_numerique"
        if self.ctrl_interface.radio_liste.GetValue() : systeme = "liste_individus"
        if self.ctrl_interface.radio_liste.GetValue() == True and self.ctrl_interface.check_activites.GetValue() == True :
            activites = self.ctrl_interface.ctrl_activites.GetTexteCoches() 
        else :
            activites = None
        confirmation = int(self.check_confirmation.GetValue())
        vocal = int(self.check_vocal.GetValue())
        tutoiement = int(self.check_tutoiement.GetValue())
        
        # Sauvegarde de la procédure
        listeDonnees = [    
                ("nom", nom),
                ("defaut", self.defaut),
                ("style", style),
                ("theme", theme),
                ("image", image),
                ("systeme", systeme),
                ("activites", activites),
                ("confirmation", confirmation),
                ("vocal", vocal),
                ("tutoiement", tutoiement),
            ]
        if self.IDprocedure == None :
            self.IDprocedure = DB.ReqInsert("badgeage_procedures", listeDonnees)
        else:
            DB.ReqMAJ("badgeage_procedures", listeDonnees, "IDprocedure", self.IDprocedure)
            
        # Sauvegarde des actions
        listeActions = self.ctrl_actions.GetDonnees()
        
        listeChamps = []
        for nom, type, info in DICT_TABLES["badgeage_actions"] :
            listeChamps.append(nom)
        
        ordre = 1
        listeIDaction = []
        listeIDmessage = []
        for dictAction in listeActions :
            IDaction = dictAction["IDaction"]
            
            # Création de l'enregistrement
            listeDonnees = [("IDprocedure", self.IDprocedure), ("ordre", ordre), ]
            for code in listeChamps :
                if code not in ("IDaction", "IDprocedure", "ordre") :
                    if dictAction.has_key(code) :
                        valeur = dictAction[code]
                    else :
                        valeur = None
                    listeDonnees.append((code, valeur))
            
            # Sauvegarde de l'action
            if IDaction == None :
                IDaction = DB.ReqInsert("badgeage_actions", listeDonnees)
            else:
                DB.ReqMAJ("badgeage_actions", listeDonnees, "IDaction", IDaction)
            
            # Sauvegarde des messages
            if dictAction.has_key("action_messages") :
                listeMessages = dictAction["action_messages"]
                for IDmessage, message in listeMessages :
                    if IDmessage == None :
                        IDmessage = DB.ReqInsert("badgeage_messages", [("IDprocedure", self.IDprocedure), ("IDaction", IDaction), ("message", message)])
                    else:
                        DB.ReqMAJ("badgeage_messages", [("message", message),], "IDmessage", IDmessage)
                    listeIDmessage.append(IDmessage) 
                    
            listeIDaction.append(IDaction) 
            
            ordre += 1
            
        # Suppression des actions et des messages supprimés
        for IDaction in self.listeInitialeActions :
            if IDaction not in listeIDaction :
                DB.ReqDEL("badgeage_actions", "IDaction", IDaction)
        
        for IDmessage in self.listeInitialeMessages :
            if IDmessage not in listeIDmessage :
                DB.ReqDEL("badgeage_messages", "IDmessage", IDmessage)
        
        DB.Close()
        return True
    
    def GetIDprocedure(self):
        return self.IDprocedure
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None, IDprocedure=1)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()