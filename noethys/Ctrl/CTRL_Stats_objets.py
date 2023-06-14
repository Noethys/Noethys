#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.customtreectrl as CT



class CTRL_Objets(CT.CustomTreeCtrl):
    def __init__(self, parent, liste_objets=[], id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SUNKEN_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.liste_objets = liste_objets
        self.root = self.AddRoot(_(u"Objets"))
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_PARENT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True)

        # Création de l'ImageList
        self.dictImages = {
            "rubrique" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Rubrique.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            "page" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Page.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            "texte" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Texte2.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            "tableau" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Tableau.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            "graphe" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Barres2.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            }
        
        il = wx.ImageList(16, 16)
        index =0
        for code, dictImage in self.dictImages.items() :
            il.Add(dictImage["img"])
            dictImage["index"] = index
            index += 1
        self.AssignImageList(il)

        # Binds
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnCheck)
    
    def MAJ(self):
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Objets"))
        
        for dictRubrique in self.liste_objets :
            # Rubriques
            brancheRubrique = self.AppendItem(self.root, dictRubrique["nom"], ct_type=1)
            self.SetPyData(brancheRubrique, {"categorie":"rubrique", "code":dictRubrique["code"]})
            self.SetItemBold(brancheRubrique)
            self.SetItemImage(brancheRubrique, self.dictImages["rubrique"]["index"])
            if dictRubrique["visible"] == True :
                brancheRubrique.Check() 
                
            for dictPage in dictRubrique["pages"] :
                # Pages
                branchePage = self.AppendItem(brancheRubrique, dictPage["nom"], ct_type=1)
                self.SetPyData(branchePage, {"categorie":"page", "code":dictPage["code"]})
                self.SetItemImage(branchePage, self.dictImages["page"]["index"])
                if dictPage["visible"] == True :
                    branchePage.Check() 

                for objet in dictPage["objets"] :
                    # Objets
                    nomObjet = objet.nom
                    nomObjet = nomObjet.replace("<BR>", "")
                    brancheObjet = self.AppendItem(branchePage, nomObjet, ct_type=1)
                    self.SetItemFont(brancheObjet, wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                    self.SetPyData(brancheObjet, {"categorie":"objet", "code":objet.code})
                    self.SetItemImage(brancheObjet, self.dictImages[objet.categorie]["index"])
                    if objet.visible == True :
                        brancheObjet.Check() 
            
        self.ExpandAll() 

    def OnCheck(self, event):
        item = event.GetItem()
        categorie = self.GetPyData(item)["categorie"]
        code = self.GetPyData(item)["code"]
        etat = self.IsItemChecked(item)
        
    def GetCoches(self):
        """ Obtient la liste des éléments cochés """
        listeCodes = []
        
        def hasEnfantsCoches(branche):
            hasCoches = False
            brancheEnfant = self.GetFirstChild(branche)[0]
            for indexTemp in range(self.GetChildrenCount(branche, recursively=False)) :
                if self.IsItemChecked(brancheEnfant) :
                    hasCoches = True
                brancheEnfant = self.GetNextChild(branche, indexTemp+1)[0]
            return hasCoches
        
        brancheRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            if self.IsItemChecked(brancheRubrique) and hasEnfantsCoches(brancheRubrique) :
                code = self.GetItemPyData(brancheRubrique)["code"]
                listeCodes.append(code)
            
                branchePage = self.GetFirstChild(brancheRubrique)[0]
                for index2 in range(self.GetChildrenCount(brancheRubrique, recursively=False)) :
                    if self.IsItemChecked(branchePage) and hasEnfantsCoches(branchePage) :
                        code = self.GetItemPyData(branchePage)["code"]
                        listeCodes.append(code)
                    
                        brancheObjet = self.GetFirstChild(branchePage)[0]
                        for index3 in range(self.GetChildrenCount(branchePage, recursively=False)) :
                            if self.IsItemChecked(brancheObjet) :
                                code = self.GetItemPyData(brancheObjet)["code"]
                                listeCodes.append(code)
                    
                            brancheObjet = self.GetNextChild(branchePage, index3+1)[0]
                    branchePage = self.GetNextChild(brancheRubrique, index2+1)[0]
            brancheRubrique = self.GetNextChild(self.root, index1+1)[0]
                        
        return listeCodes
    
    def Coche(self, etat=True):
        brancheRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            self.CheckItem(brancheRubrique, etat)
            
            branchePage = self.GetFirstChild(brancheRubrique)[0]
            for index2 in range(self.GetChildrenCount(brancheRubrique, recursively=False)) :
                self.CheckItem(branchePage, etat)
                
                brancheObjet = self.GetFirstChild(branchePage)[0]
                for index3 in range(self.GetChildrenCount(branchePage, recursively=False)) :
                    self.CheckItem(branchePage, etat)
            
                    brancheObjet = self.GetNextChild(branchePage, index3+1)[0]
                branchePage = self.GetNextChild(brancheRubrique, index2+1)[0]
            brancheRubrique = self.GetNextChild(self.root, index1+1)[0]



# ------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        from Dlg.DLG_Stats import LISTE_OBJETS as liste_objets
        self.myOlv = CTRL_Objets(panel, liste_objets=liste_objets)
        self.myOlv.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
