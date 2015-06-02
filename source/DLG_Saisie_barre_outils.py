#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import random
import wx.lib.agw.customtreectrl as CT


# Liste d'"l"ments pour les tests uniquement :
LISTE_ITEMS_TESTS = [
    # Fichier
    {"code" : "menu_fichier", "label" : _(u"Fichier"), "items" : [
            {"code" : "nouveau_fichier", "label" : _(u"Créer un nouveau fichier\tCtrl+N"), "infobulle" : _(u"Créer un nouveau fichier"), "image" : "Images/16x16/Fichier_nouveau.png", "action" : None},
            {"code" : "ouvrir_fichier", "label" : _(u"Ouvrir un fichier\tCtrl+O"), "infobulle" : _(u"Ouvrir un fichier existant"), "image" : "Images/16x16/Fichier_ouvrir.png", "action" : None},
            {"code" : "fermer_fichier", "label" : _(u"Fermer le fichier\tCtrl+F"), "infobulle" : _(u"Fermer le fichier ouvert"), "image" : "Images/16x16/Fichier_fermer.png", "action" : None, "actif" : False},
            ],
    },
    # Paramétrage
    {"code" : "menu_parametrage", "label" : _(u"Paramétrage"), "items" : [
            {"code" : "preferences", "label" : _(u"Préférences"), "infobulle" : _(u"Préférences"), "image" : "Images/16x16/Mecanisme.png", "action" : None},
            {"code" : "enregistrement", "label" : _(u"Enregistrement"), "infobulle" : _(u"Enregistrement"), "image" : "Images/16x16/Cle.png", "action" : None},
        ],
    },
    ]


def GetListeItemsMenu():
    """ Renvoie tous les items menu de type action sous forme de liste """
    # Récupère la liste dans la frame principale
    topWindow = wx.GetApp().GetTopWindow() 
    if topWindow.GetName() == "general" :
        listeItemsMenu = topWindow.listeItemsMenu
    else :
        listeItemsMenu = LISTE_ITEMS_TESTS
    # Analyse des éléments
    listeItemsFinale = []
    def AnalyseItem(listeItems):
        for item in listeItems :
            if type(item) == dict :
                if item.has_key("action") :
                    listeItemsFinale.append(item)
                if item.has_key("items") :
                    AnalyseItem(item["items"])
    AnalyseItem(listeItemsMenu)
    return listeItemsFinale



class CTRL_elements(wx.TreeCtrl):
    def __init__(self, parent): 
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS)
        self.parent = parent

        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
        
        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
        
        # Données
        self.listeElements = [
            {"code" : "elements_speciaux", "label" : _(u"Eléments spéciaux"), "elements" : [
                {"code" : "|", "infobulle" : u"<Séparateur>", "image" : "Images/16x16/Barreoutils_separator.png"},
                {"code" : "-", "infobulle" : u"<Espace>", "image" : "Images/16x16/Barreoutils_spacer.png"},
                ]},
            {"code" : "elements_menus", "label" : _(u"Eléments du menu"), "elements" : 
                GetListeItemsMenu()
                },
            ]
        
        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        
        # Image catégorie
        self.dictImages["categorie"] = il.Add(wx.Bitmap("Images/16x16/Dossier.png", wx.BITMAP_TYPE_PNG))
        
        # Images des éléments
        for dictCategorie in self.listeElements :
            for dictItem in dictCategorie["elements"] :
                if dictItem.has_key("image") :
                    self.dictImages[dictItem["code"]] = il.Add(wx.Bitmap(dictItem["image"], wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création de la racine
        self.root = self.AddRoot("Racine")
    
    def OnDoubleClick(self):
        event.Skip() 
        
# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_elements_dispo(CTRL_elements):
    def __init__(self, parent): 
        CTRL_elements.__init__(self, parent)
        self.parent = parent
        self.listeElementsPris = []
        self.Remplissage() 
    
    def Remplissage(self):
        # Remplissage des éléments
        self.dictItems = {}
        for dictCategorie in self.listeElements :
            categorie = self.AppendItem(self.root, dictCategorie["label"])
            self.SetItemImage(categorie, self.dictImages["categorie"], which=wx.TreeItemIcon_Normal)
            self.SetItemBold(categorie, True)
            for dictItem in dictCategorie["elements"] :
                dictItem["categorie"] = dictCategorie["code"]
                item = self.AppendItem(categorie, dictItem["infobulle"])
                self.SetPyData(item, dictItem)
                if dictItem.has_key("image") :
                    self.SetItemImage(item, self.dictImages[dictItem["code"]], which=wx.TreeItemIcon_Normal)
                self.dictItems[dictItem["code"]] = item
        self.ExpandAll() 
        self.EnsureVisible(self.GetFirstChild(self.root)[0])
        
    def MAJ(self):
        for code, item in self.dictItems.iteritems() :
            if code in self.listeElementsPris and code not in ("|", "-") :
                self.SetItemTextColour(item, "red")
                self.SetItemBold(item)
            else :
                self.SetItemTextColour(item, "black")
                self.SetItemBold(item, False)

    def OnDoubleClick(self, event):
        item = event.GetItem()
        dictItem = self.GetPyData(item)
        if dictItem != None :
            self.Ajouter(dictItem["code"])
    
    def GetSelection(self):
        pass
        
    def Ajouter(self, code=""):
        if code not in self.listeElementsPris or code in ("|", "-") :
            self.listeElementsPris.append(code)
            self.parent.ctrl_elements_barre.Ajouter(code)
        self.MAJ() 
    
    def Retirer(self, code=""):
        self.listeElementsPris.remove(code)
        self.MAJ() 

# ----------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_elements_barre(CTRL_elements):
    def __init__(self, parent): 
        CTRL_elements.__init__(self, parent)
        self.parent = parent
        self.listeElementsBarre = []
        self.dictItems = {}
    
    def GetInfosItem(self, code=""):
        for dictCategorie in self.listeElements :
            for dictItem in dictCategorie["elements"] :
                if dictItem["code"] == code :
                    return  dictItem
        
    def MAJ(self, codeSelectionItem=None):
        self.dictItems = {}
        self.DeleteChildren(self.root)
        for code in self.listeElementsBarre :
            if codeSelectionItem == code :
                selectionItem = True
            else :
                selectionItem = False
            self.Ajouter(code, enregistrer=False, selectionItem=selectionItem)
    
    def OnDoubleClick(self, event):
        item = event.GetItem()
        dictItem = self.GetPyData(item)
        if dictItem != None :
            self.Retirer(dictItem["code"])
    
    def Ajouter(self, code="", enregistrer=True, selectionItem=False):
        dictItem = self.GetInfosItem(code)
        if dictItem != None :
            item = self.AppendItem(self.root, dictItem["infobulle"])
            self.SetPyData(item, dictItem)
            if dictItem.has_key("image") :
                self.SetItemImage(item, self.dictImages[dictItem["code"]], which=wx.TreeItemIcon_Normal)
            self.dictItems[dictItem["code"]] = item
            if enregistrer == True :
                self.listeElementsBarre.append(code)
            if selectionItem == True :
                self.SelectItem(item, True)
                self.SetFocus() 
    
    def Retirer(self, code=""):
        self.listeElementsBarre.remove(code)
        self.Delete(self.dictItems[code])
        self.parent.ctrl_elements_dispo.Retirer(code)

    def GetElements(self):
        return self.listeElementsBarre
    
    def Monter(self, event=None):
        self.Deplacer(-1)
        
    def Descendre(self, event=None):
        self.Deplacer(+1)

    def Deplacer(self, sens=-1):
        if self.GetFocusedItem().IsOk() :
            dictItem = self.GetPyData(self.GetFocusedItem())
            if dictItem != None :
                code = dictItem["code"]
                index = self.listeElementsBarre.index(code)
                # Vérifie si pas au début ou à la fin de la liste
                if (index == 0 and sens == -1) or (index == self.GetChildrenCount(self.root)-1 and sens ==+1) :
                    return
                # Déplacement
                self.listeElementsBarre.pop(index)
                self.listeElementsBarre.insert(index + sens, code)
                self.MAJ(codeSelectionItem=code) 
                
# ----------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Style(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeStyles = [
            {"code" : "textedroite", "label" : _(u"Icône + texte à droite")},
            {"code" : "textedessous", "label" : _(u"Icône + texte dessous")},
            {"code" : "texteseul", "label" : _(u"Texte uniquement")},
            {"code" : "imageseule", "label" : _(u"Icône uniquement")},            
            ]
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeLabels = []
        for dictItem in self.listeStyles :
            listeLabels.append(dictItem["label"])
        self.SetItems(listeLabels)

    def SetCode(self, code=""):
        index = 0
        for dictItem in self.listeStyles :
            if dictItem["code"] == code :
                 self.SetSelection(index)
            index += 1

    def GetCode(self):
        index = self.GetSelection()
        return self.listeStyles[index]["code"]
    
# ------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, texte=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_observations = wx.StaticText(self, wx.ID_ANY, _(u"Observations :"))
        self.label_style = wx.StaticText(self, wx.ID_ANY, _(u"Style :"))
        self.ctrl_style = CTRL_Style(self)
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        
        # Elements
        self.box_elements_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Eléments"))

        self.label_elements_dispo = wx.StaticText(self, wx.ID_ANY, _(u"Eléments disponibles"))
        self.ctrl_elements_dispo = CTRL_elements_dispo(self)
        self.ctrl_elements_dispo.SetMinSize((250, 50))

        self.bouton_droite = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Avancer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_gauche = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Reculer.png", wx.BITMAP_TYPE_ANY))

        self.label_elements_barre = wx.StaticText(self, wx.ID_ANY, _(u"Eléments de la barre"))
        self.ctrl_elements_barre = CTRL_elements_barre(self)
        self.ctrl_elements_barre.SetMinSize((250, 50))

##        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonDroite, self.bouton_droite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGauche, self.bouton_gauche)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMonter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDescendre, self.bouton_descendre)
##        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.ctrl_elements_dispo.MAJ() 
        if texte == None :
            self.SetTitle(_(u"Saisie d'une barre d'outils"))
            self.code = self.GetCodeUnique() 
        else :
            self.SetTitle(_(u"Modification d'une barre d'outils"))
            self.Importation(texte)

    def __set_properties(self):
        self.ctrl_nom.SetMinSize((300, 21))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour cette barre d'outils"))
        self.ctrl_style.SetToolTipString(_(u"Sélectionnez un style d'affichage pour cette barre d'outils"))
        self.ctrl_observations.SetToolTipString(_(u"Saisissez des observations (optionnel)"))
        self.label_elements_dispo.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_elements_barre.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_droite.SetToolTipString(_(u"Cliquez ici pour insérer l'élément sélectionné dans la barre d'outils (Vous pouvez également double-cliquer dessus)"))
        self.bouton_gauche.SetToolTipString(_(u"Cliquez ici pour retirer l'élément sélectionné de la barre d'outils (Vous pouvez également double-cliquer dessus)"))
        self.bouton_monter.SetToolTipString(_(u"Cliquez ici pour déplacer cet élément"))
        self.bouton_descendre.SetToolTipString(_(u"Cliquez ici pour déplacer cet élément"))
##        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier cet élément"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((800, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        self.box_elements_staticbox.Lower()
        box_elements = wx.StaticBoxSizer(self.box_elements_staticbox, wx.VERTICAL)
        grid_sizer_elements = wx.FlexGridSizer(2, 4, 5, 5)
        grid_sizer_boutons_elements = wx.FlexGridSizer(4, 1, 5, 5)
        grid_sizer_boutons_deplacer = wx.FlexGridSizer(2, 1, 5, 5)
        self.box_generalites_staticbox.Lower()
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_generalites_gauche = wx.FlexGridSizer(2, 4, 10, 10)
        grid_sizer_generalites_gauche.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites_gauche.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites_gauche.Add((10, 20), 0, wx.EXPAND, 0)
        grid_sizer_generalites_gauche.Add(self.label_observations, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites_gauche.Add(self.label_style, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites_gauche.Add(self.ctrl_style, 0, wx.EXPAND, 0)
        grid_sizer_generalites_gauche.Add((10, 20), 0, 0, 0)
        grid_sizer_generalites_gauche.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(grid_sizer_generalites_gauche, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableRow(0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_elements.Add(self.label_elements_dispo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_elements.Add((20, 5), 0, wx.EXPAND, 0)
        grid_sizer_elements.Add(self.label_elements_barre, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_elements.Add((20, 5), 0, wx.EXPAND, 0)
        grid_sizer_elements.Add(self.ctrl_elements_dispo, 1, wx.EXPAND, 0)
        grid_sizer_boutons_deplacer.Add(self.bouton_droite, 0, 0, 0)
        grid_sizer_boutons_deplacer.Add(self.bouton_gauche, 0, 0, 0)
        grid_sizer_elements.Add(grid_sizer_boutons_deplacer, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_elements.Add(self.ctrl_elements_barre, 1, wx.EXPAND, 0)
##        grid_sizer_boutons_elements.Add(self.bouton_modifier, 0, 0, 0)
##        grid_sizer_boutons_elements.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_elements.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons_elements.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_elements.Add(grid_sizer_boutons_elements, 1, wx.EXPAND, 0)
        grid_sizer_elements.AddGrowableRow(1)
        grid_sizer_elements.AddGrowableCol(0)
        grid_sizer_elements.AddGrowableCol(2)
        box_elements.Add(grid_sizer_elements, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_elements, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):  
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonDroite(self, event):  
        if self.ctrl_elements_dispo.GetFocusedItem().IsOk() :
            dictItem = self.ctrl_elements_dispo.GetPyData(self.ctrl_elements_dispo.GetFocusedItem())
            if dictItem != None :
                self.ctrl_elements_dispo.Ajouter(dictItem["code"])
        
    def OnBoutonGauche(self, event):  
        if self.ctrl_elements_barre.GetFocusedItem().IsOk() :
            dictItem = self.ctrl_elements_barre.GetPyData(self.ctrl_elements_barre.GetFocusedItem())
            if dictItem != None :
                self.ctrl_elements_barre.Retirer(dictItem["code"])

    def OnBoutonMonter(self, event):  
        self.ctrl_elements_barre.Monter()

    def OnBoutonDescendre(self, event):  
        self.ctrl_elements_barre.Descendre()

    def OnBoutonModifier(self, event):  
        pass
    
    def GetElements(self):
        return self.ctrl_elements_barre.GetElements()
    
    def SetElements(self, listeCodes=[]):
        for code in listeCodes :
            self.ctrl_elements_dispo.Ajouter(code)
    
    def GetCodeUnique(self):
        """ Création d'un code d'identification unique """
        code = ""
        for x in range(0, 10) :
            code += random.choice("abcdefghijkmnopqrstuvwxyz123456789ABCDEFGHJKLMNOPQRSTUVWXYZ")
        return code
    
    def Importation(self, texte=""):
        # Lecture du texte
        codeBarre, label, observations, style, contenu = texte.split("###")
        listeElements = contenu.split(";")
        
        # Remplissage des contrôles
        self.code = codeBarre
        self.ctrl_nom.SetValue(label)
        self.ctrl_observations.SetValue(observations)
        self.ctrl_style.SetCode(style)
        self.SetElements(listeElements)
    
    def GetTexte(self):
        """ Renvoie les données de la barre au format texte """
        nom = self.ctrl_nom.GetValue() 
        observations = self.ctrl_observations.GetValue() 
        style = self.ctrl_style.GetCode()         
        listeElements = self.GetElements() 
        texteElements = ";".join(listeElements)
        
        listeTemp = [self.code, nom, observations, style, texteElements]
        texte = "###".join(listeTemp)
        return texte
    
    def GetCode(self):
        return self.code 
    
    def OnBoutonOk(self, event):  
        nom = self.ctrl_nom.GetValue() 
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le nom de la barre d'outils !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        listeElements = self.GetElements() 
        if len(listeElements) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez insérer au moins un élément dans cette barre d'outils !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, texte=u"barre_perso_111###Ma barre 1###observations barre 1###textedessous###nouveau_fichier;|;fermer_fichier;-;tutoriels_videos")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
