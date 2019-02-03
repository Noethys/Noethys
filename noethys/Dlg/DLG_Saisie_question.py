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
import GestionDB
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Ctrl import CTRL_Questionnaire
import DLG_Saisie_choix_question



def ConvertCouleur(couleur=None):
    if couleur == None or len(couleur) == 0 : return None
    couleur = couleur[1:-1].split(",")
    couleur = (int(couleur[0]), int(couleur[1]), int(couleur[2]) )
    return couleur


class Track(object):
    def __init__(self, donnees):
        self.IDchoix = donnees[0]
        self.IDquestion = donnees[1]
        self.ordre = donnees[2]
        self.visible = donnees[3]
        self.label = donnees[4]
    
    def GetDictValeurs(self):
        dictTemp = {"IDchoix":self.IDchoix, "IDquestion":self.IDquestion, "ordre":self.ordre, "visible":self.visible, "label":self.label}
        return dictTemp
    
    

class CTRL_Choix(FastObjectListView):
    def __init__(self, parent, IDquestion=None):
        FastObjectListView.__init__(self, parent, -1, style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.parent = parent
        self.IDquestion = IDquestion
        self.listeChoix = self.Importation()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def Importation(self):
        self.listeSuppressions = []
        if self.IDquestion == None :
            return []
        DB = GestionDB.DB()
        req = """SELECT IDchoix, IDquestion, ordre, visible, label
        FROM questionnaire_choix
        WHERE IDquestion=%d
        ORDER BY ordre;""" % self.IDquestion
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        listeChoix = []   
        for item in listeTemp :
            track = listeChoix.append(Track(item))
        return listeChoix
    
    def MAJ(self):
        listeLabels = []
        index = 0
        for dictChoix in self.listeChoix :
            listeLabels.append(dictChoix["label"])
            index += 1
        self.SetItems(listeLabels)

    def OnItemActivated(self,event):
        self.Modifier()
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            if track.visible == 0 :
                listItem.SetTextColour((200, 200, 200))

        liste_Colonnes = [
            ColumnDefn(_(u"IDchoix"), "left", 0, "IDchoix"),
            ColumnDefn(_(u"Label"), 'left', 410, "label", isSpaceFilling=True),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun choix"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetObjects(self.listeChoix)
       
    def MAJ(self):
        self.InitObjectListView()
        self.GetParent().MAJ_apercu() 

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """      
        if self.GetSelectedObject() == None :
            noSelection = True
        else:
            noSelection = False
          
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()
    
        # Item Monter
        item = wx.MenuItem(menuPop, 40, _(u"Monter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)
        if noSelection == True : item.Enable(False)
        
        # Item Descendre
        item = wx.MenuItem(menuPop, 50, _(u"Descendre"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        if noSelection == True : item.Enable(False)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event=None):
        dlg = DLG_Saisie_choix_question.Dialog(self)
        if dlg.ShowModal()  == wx.ID_OK :
            label = dlg.GetLabel() 
            visible = dlg.GetVisible() 
            track = Track((None, self.IDquestion, None, visible, label))
            self.listeChoix.append(track)        
            self.MAJ() 
        dlg.Destroy()

    def Modifier(self, event=None):
        track = self.GetSelectedObject() 
        if track == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun choix dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = DLG_Saisie_choix_question.Dialog(self)
        dlg.SetLabel(track.label)
        dlg.SetVisible(track.visible)
        if dlg.ShowModal()  == wx.ID_OK :
            track.label = dlg.GetLabel() 
            track.visible = dlg.GetVisible() 
            self.MAJ() 
        dlg.Destroy()

    def Supprimer(self, event=None):
        track = self.GetSelectedObject() 
        if track == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun choix dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        index = self.GetIndexOf(track)
        self.listeSuppressions.append(track)
        self.listeChoix.pop(index)
        self.MAJ() 

    def Monter(self, event=None):
        track = self.GetSelectedObject() 
        if track == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun choix dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        index = self.GetIndexOf(track)
        if index == 0 : return
        self.listeChoix.pop(index)
        self.listeChoix.insert(index-1, track)
        self.MAJ() 

    def Descendre(self, event=None):
        track = self.GetSelectedObject() 
        if track == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun choix dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        index = self.GetIndexOf(track)
        if index == len(self.listeChoix) : return
        self.listeChoix.pop(index)
        self.listeChoix.insert(index+1, track)
        self.MAJ() 
    
    def GetListeChoix(self):
        """ Renvoie la liste des valeurs """
        listeValeurs = []
        for track in self.listeChoix :
            dictValeurs = track.GetDictValeurs()
            listeValeurs.append(dictValeurs)
        return listeValeurs
    
    def GetListeSuppressionChoix(self):
        return self.listeSuppressions


# -----------------------------------------------------------------------------------------------------------------


class CTRL_Categorie(wx.Choice):
    def __init__(self, parent, type="individu"):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.type = type
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix)
    
    def MAJ(self, listeActivites=[] ):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        # Importation des catégories
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, ordre, visible, type, couleur, label
        FROM questionnaire_categories
        WHERE type='%s'
        ORDER BY ordre
        ;""" % self.type
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        self.dictCategories = {}
        index = 0
        for IDcategorie, ordre, visible, type, couleur, label in listeCategories :
            couleur = ConvertCouleur(couleur)
            dictTemp = {"IDcategorie":IDcategorie, "ordre":ordre, "visible":visible, "couleur":couleur, "label":label, "questions":[]}
            self.dictDonnees[index] = dictTemp
            self.dictCategories[IDcategorie] = dictTemp
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["IDcategorie"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["IDcategorie"]
    
    def OnChoix(self, event):
        self.parent.MAJ_apercu() 
        
            
            
# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Controle(BitmapComboBox):
    def __init__(self, parent, size=(-1,  -1)):
        BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        self.parent = parent
        self.MAJlisteDonnees() 
        self.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.OnChoix)

    def MAJlisteDonnees(self):
        for dictControle in CTRL_Questionnaire.LISTE_CONTROLES :
            label = dictControle["label"]
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % dictControle["image"]), wx.BITMAP_TYPE_ANY)
            code = dictControle["code"]
            self.Append(label, bmp, code)

    def SetCode(self, code=""):
        index = 0
        for dictControle in CTRL_Questionnaire.LISTE_CONTROLES :
            if dictControle["code"] == code :
                 self.SetSelection(index)
            index += 1

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        dictControle = CTRL_Questionnaire.LISTE_CONTROLES[index]
        return dictControle["code"]
    
    def GetDictOptions(self):
        index = self.GetSelection()
        if index == -1 : return {}
        dictControle = CTRL_Questionnaire.LISTE_CONTROLES[index]
        if "options" in dictControle :
            return dictControle["options"]
        else:
            return {}
        
    def OnChoix(self, event=None, MAJ=True, insereValeursDefaut=True):
        dictOptions = self.GetDictOptions() 
        if "hauteur" in dictOptions :
            self.parent.ctrl_hauteur.Enable(True) 
            if insereValeursDefaut == True :
                self.parent.ctrl_hauteur.SetValue(dictOptions["hauteur"])
        else:
            self.parent.ctrl_hauteur.Enable(False) 
        if "min" in dictOptions :
            self.parent.ctrl_valmin.Enable(True) 
            if insereValeursDefaut == True :
                self.parent.ctrl_valmin.SetValue(dictOptions["min"])
        else:
            self.parent.ctrl_valmin.Enable(False) 
        if "max" in dictOptions :
            self.parent.ctrl_valmax.Enable(True) 
            if insereValeursDefaut == True :
                self.parent.ctrl_valmax.SetValue(dictOptions["max"])
        else:
            self.parent.ctrl_valmax.Enable(False) 
        if "choix" in dictOptions :
            self.parent.ActiveCtrlChoix(True)
        else:
            self.parent.ActiveCtrlChoix(False)

        if MAJ == True :
            self.parent.MAJ_apercu() 


# -----------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, type="individu", IDquestion=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent    
        self.type = type
        self.IDquestion = IDquestion  
        self.ordre = None
        self.defaut = None
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self, type=type)
        self.label_controle = wx.StaticText(self, -1, _(u"Contrôle :"))
        self.ctrl_controle = CTRL_Controle(self)
        self.label_visible = wx.StaticText(self, -1, _(u"Visible :"))
        self.ctrl_visible = wx.CheckBox(self, -1, u"")
        self.ctrl_visible.SetValue(True) 
        
        # Apercu
        self.box_apercu_staticbox = wx.StaticBox(self, -1, _(u"Valeurs par defaut"))
        self.ctrl_apercu = CTRL_Questionnaire.CTRL(self, type=type, mode="apercu", afficherInvisibles=True, largeurQuestion=0)
        self.ctrl_apercu.SetMinSize((325, 90))

        # Choix
        self.box_choix_staticbox = wx.StaticBox(self, -1, _(u"Liste de choix"))
        self.ctrl_choix = CTRL_Choix(self, IDquestion=IDquestion)
        self.bouton_ajouter_choix = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_choix = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))        
        self.bouton_supprimer_choix = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter_choix = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre_choix = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_hauteur = wx.StaticText(self, -1, _(u"Hauteur du contrôle :"))
        self.ctrl_hauteur = wx.SpinCtrl(self, -1, "")
        self.ctrl_hauteur.SetRange(-1, 500)
        self.label_valmin = wx.StaticText(self, -1, _(u"Valeur minimale :"))
        self.ctrl_valmin = wx.SpinCtrl(self, -1, "")
        self.ctrl_valmin.SetRange(0, 99999)
        self.label_valmax = wx.StaticText(self, -1, _(u"Valeur maximale :"))
        self.ctrl_valmax = wx.SpinCtrl(self, -1, "")
        self.ctrl_valmax.SetRange(1, 99999)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixHauteur, self.ctrl_hauteur)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixValmin, self.ctrl_valmin)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixValmax, self.ctrl_valmax)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouterChoix, self.bouton_ajouter_choix)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifierChoix, self.bouton_modifier_choix)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimerChoix, self.bouton_supprimer_choix)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMonterChoix, self.bouton_monter_choix)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDescendreChoix, self.bouton_descendre_choix)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Importation
        if self.IDquestion != None :
            self.Importation() 
            self.ctrl_controle.OnChoix(MAJ=False, insereValeursDefaut=False)
        else:
            self.ctrl_controle.OnChoix(MAJ=False)
            
        # Initialisation des contrôles
        self.ctrl_choix.MAJ() 
        self.ctrl_label.SetFocus()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une question"))
        self.ctrl_label.SetToolTip(wx.ToolTip(_(u"Saisissez ici le label de la question")))
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la catégorie de la question")))
        self.ctrl_controle.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici le type de contrôle souhaité")))
        self.ctrl_visible.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour rendre visible cette question")))
        self.bouton_ajouter_choix.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une nouvelle question")))
        self.bouton_modifier_choix.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la ligne sélectionnée dans la liste")))
        self.bouton_supprimer_choix.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la ligne sélectionnée dans la liste")))
        self.bouton_monter_choix.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter la ligne sélectionnée dans la liste")))
        self.bouton_descendre_choix.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre la ligne sélectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.ctrl_hauteur.SetToolTip(wx.ToolTip(_(u"Saisissez ici la hauteur du contrôle (en pixels)\nIndiquez '-1' pour définir une taille automatiquement")))
        self.ctrl_valmin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la valeur minimale du contrôle")))
        self.ctrl_valmax.SetToolTip(wx.ToolTip(_(u"Saisissez ici la valeur maximale du contrôle")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((650, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Colonne gauche
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Box Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_controle, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_controle, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_visible, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_visible, 0, 0, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(box_generalites, 1, wx.EXPAND, 0)
        
        # Box Apercu
        box_apercu = wx.StaticBoxSizer(self.box_apercu_staticbox, wx.VERTICAL)
        grid_sizer_apercu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_apercu.Add(self.ctrl_apercu, 0, wx.EXPAND, 0)
        grid_sizer_apercu.AddGrowableRow(0)
        grid_sizer_apercu.AddGrowableCol(0)
        box_apercu.Add(grid_sizer_apercu, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(box_apercu, 1, wx.EXPAND, 0)
        
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Colonne droite
        grid_sizer_droite = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        
        # Box choix
        box_choix = wx.StaticBoxSizer(self.box_choix_staticbox, wx.VERTICAL)
        grid_sizer_choix = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_choix.Add(self.ctrl_choix, 0, wx.EXPAND, 0)

        grid_sizer_boutons_choix = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_choix.Add(self.bouton_ajouter_choix, 0, 0, 0)
        grid_sizer_boutons_choix.Add(self.bouton_modifier_choix, 0, 0, 0)
        grid_sizer_boutons_choix.Add(self.bouton_supprimer_choix, 0, 0, 0)
        grid_sizer_boutons_choix.Add( (5, 5) , 0, 0, 0)
        grid_sizer_boutons_choix.Add(self.bouton_monter_choix, 0, 0, 0)
        grid_sizer_boutons_choix.Add(self.bouton_descendre_choix, 0, 0, 0)
        grid_sizer_choix.Add(grid_sizer_boutons_choix, 1, wx.EXPAND, 0)
        
        grid_sizer_choix.AddGrowableRow(0)
        grid_sizer_choix.AddGrowableCol(0)
        box_choix.Add(grid_sizer_choix, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_choix, 1, wx.EXPAND, 0)
        
        # Box Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_options.Add(self.label_hauteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_hauteur, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_valmin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_valmin, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_valmax, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_valmax, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(1)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_options, 1, wx.EXPAND, 0)
        grid_sizer_droite.AddGrowableRow(0)
        grid_sizer_droite.AddGrowableCol(0)
        
        grid_sizer_contenu.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def ActiveCtrlChoix(self, etat=True):
        #self.ctrl_choix.Enable(etat) 
        self.bouton_ajouter_choix.Enable(etat) 
        self.bouton_modifier_choix.Enable(etat) 
        self.bouton_supprimer_choix.Enable(etat) 
        self.bouton_monter_choix.Enable(etat) 
        self.bouton_descendre_choix.Enable(etat) 

    def OnBoutonAjouterChoix(self, event): 
        self.ctrl_choix.Ajouter() 

    def OnBoutonModifierChoix(self, event): 
        self.ctrl_choix.Modifier() 

    def OnBoutonSupprimerChoix(self, event): 
        self.ctrl_choix.Supprimer() 

    def OnBoutonMonterChoix(self, event): 
        self.ctrl_choix.Monter() 

    def OnBoutonDescendreChoix(self, event): 
        self.ctrl_choix.Descendre() 
    
    def OnChoixHauteur(self, event):
        self.MAJ_apercu() 
        
    def OnChoixValmin(self, event):
        self.MAJ_apercu() 
        
    def OnChoixValmax(self, event):
        self.MAJ_apercu() 
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Questionnaires")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def GetLabel(self):
        return self.ctrl_label.GetValue() 
    
    def GetCategorie(self):
        return self.ctrl_categorie.GetID() 
    
    def GetControle(self):
        return self.ctrl_controle.GetCode()
    
    def GetVisible(self):
        return int(self.ctrl_visible.GetValue())
    
    def GetListeChoix(self):
        return self.ctrl_choix.GetListeChoix() 
    
    def GetDictOptions(self):
        dictOptions = {}
        if self.ctrl_hauteur.IsEnabled() : dictOptions["hauteur"] = self.ctrl_hauteur.GetValue()
        if self.ctrl_valmin.IsEnabled() : dictOptions["min"] = self.ctrl_valmin.GetValue()
        if self.ctrl_valmax.IsEnabled() : dictOptions["max"] = self.ctrl_valmax.GetValue()
        return dictOptions
    
    def GetDictOptionsStr(self):
        """ Récupère les options au format str pour l'enregistrement dans la base """
        listeOptions = []
        dictOptions = self.GetDictOptions() 
        for code, valeur in dictOptions.items() :
            listeOptions.append("%s=%s" % (code, str(valeur)))
        texte = ";".join(listeOptions) 
        return texte
        
    def MAJ_apercu(self):
        label = self.GetLabel() 
        IDcategorie = self.GetCategorie() 
        controle = self.GetControle()
        visible = self.GetVisible() 
        listeChoix = self.GetListeChoix() 
        dictCategories = self.ctrl_categorie.dictCategories
        defaut = self.defaut
        options = self.GetDictOptionsStr() 
        
        dictChoix = {10000 : listeChoix}
        item = (10000, IDcategorie, 0, 1, label, controle, defaut, options)
        track = CTRL_Questionnaire.Track(item, dictChoix)
        
        dictCategories[IDcategorie]["questions"] = [track,]
        
        # MAJ du questionnaire
        self.ctrl_apercu.dictCategories = dictCategories
        self.ctrl_apercu.listeIDcategorie = [IDcategorie,]
        self.ctrl_apercu.MAJ(importation=False)
    
    def Importation(self):
        DB = GestionDB.DB() 
        req = """SELECT IDcategorie, ordre, visible, label, controle, defaut, options
        FROM questionnaire_questions
        WHERE IDquestion=%d;""" % self.IDquestion
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        if len(listeDonnees) == 0 : return
        IDcategorie, ordre, visible, label, controle, defaut, options = listeDonnees[0]
        # Catégorie
        self.ctrl_categorie.SetID(IDcategorie)
        # Ordre
        self.ordre = ordre
        # Visible
        self.ctrl_visible.SetValue(visible)
        # label
        self.ctrl_label.SetValue(label)
        # Contrôle
        self.ctrl_controle.SetCode(controle)
        # Defaut
        self.defaut = defaut
        # Options
        dictOptions = {}
        if options != None and options != "" :
            listeOptions = options.split(";")
            for option in listeOptions :
                codeOption, valeurOption = option.split("=")
                dictOptions[codeOption] = valeurOption
        if "hauteur" in dictOptions : self.ctrl_hauteur.SetValue(int(dictOptions["hauteur"]))
        if "min" in dictOptions : self.ctrl_valmin.SetValue(int(dictOptions["min"]))
        if "max" in dictOptions : self.ctrl_valmax.SetValue(int(dictOptions["max"]))
    
    def GetIDquestion(self):
        return self.IDquestion 
    
    def OnBoutonOk(self, event): 
        # Récupération des valeurs
        label = self.GetLabel() 
        IDcategorie = self.GetCategorie() 
        controle = self.GetControle()
        visible = self.GetVisible() 
        listeChoix = self.GetListeChoix() 
        defaut = self.ctrl_apercu.GetValeurs()[10000]
        options = self.GetDictOptionsStr() 
        
        # Vérification des valeurs
        if label == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun label !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Recherche de l'ordre de la question
        DB = GestionDB.DB()
        if self.ordre == None :
            req = """SELECT max(ordre)
            FROM questionnaire_questions
            WHERE IDcategorie=%d
            ;""" % IDcategorie
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            ordre = listeTemp[0][0]
            if ordre == None :
                ordre = 0
            ordre += 1
        else:
            ordre = self.ordre

        # Sauvegarde des questions
        listeDonnees = [    
            ("IDcategorie", IDcategorie),
            ("ordre", ordre),
            ("visible", visible),
            ("label", label),
            ("controle", controle),
            ("defaut", defaut),
            ("options", options),
            ]
        if self.IDquestion == None :
            self.IDquestion = DB.ReqInsert("questionnaire_questions", listeDonnees)
        else:
            DB.ReqMAJ("questionnaire_questions", listeDonnees, "IDquestion", self.IDquestion)
        
        # Sauvegarde des choix
        indexChoix = 0
        for dictChoix in listeChoix :
            listeDonnees = [    
                ("IDquestion", self.IDquestion),
                ("ordre", indexChoix),
                ("visible", dictChoix["visible"]),
                ("label", dictChoix["label"]),
                ]
            if dictChoix["IDchoix"] == None :
                IDchoix = DB.ReqInsert("questionnaire_choix", listeDonnees)
            else:
                DB.ReqMAJ("questionnaire_choix", listeDonnees, "IDchoix", dictChoix["IDchoix"])
            indexChoix += 1
        
        # Suppression de choix
        for track in self.ctrl_choix.GetListeSuppressionChoix() :
            if track.IDchoix != None :
                DB.ReqDEL("questionnaire_choix", "IDchoix", track.IDchoix)
        
        DB.Close()
        
        # Fermeture
        self.EndModal(wx.ID_OK)

        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, type="famille", IDquestion=15)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
