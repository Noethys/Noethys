#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        anciens_coches = set(self.GetCoches()) if self.GetChildrenCount(self.root, recursively=False) > 0 else None
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Objets"))
        
        for dictRubrique in self.liste_objets :
            if dictRubrique.get("visible", True) == False :
                continue
            # Rubriques
            brancheRubrique = self.AppendItem(self.root, dictRubrique["nom"], ct_type=1)
            self.SetPyData(brancheRubrique, {"categorie":"rubrique", "code":dictRubrique["code"]})
            self.SetItemBold(brancheRubrique)
            self.SetItemImage(brancheRubrique, self.dictImages["rubrique"]["index"])
            brancheRubrique.Check() 
                
            for dictPage in dictRubrique["pages"] :
                if dictPage.get("visible", True) == False :
                    continue
                # Pages
                branchePage = self.AppendItem(brancheRubrique, dictPage["nom"], ct_type=1)
                self.SetPyData(branchePage, {"categorie":"page", "code":dictPage["code"]})
                self.SetItemImage(branchePage, self.dictImages["page"]["index"])
                branchePage.Check() 

                for objet in dictPage["objets"] :
                    # Objets
                    nomObjet = objet.nom
                    nomObjet = nomObjet.replace("<BR>", "")
                    brancheObjet = self.AppendItem(branchePage, nomObjet, ct_type=1)
                    self.SetItemFont(brancheObjet, wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
                    self.SetPyData(brancheObjet, {"categorie":"objet", "code":objet.code})
                    self.SetItemImage(brancheObjet, self.dictImages[objet.categorie]["index"])
                    # Si l'objet est masqué, il est obligatoirement décoché
                    if getattr(objet, "visible", True) == False :
                        brancheObjet.Check(False)
                    elif anciens_coches is not None :
                        brancheObjet.Check(objet.code in anciens_coches)
                    else :
                        brancheObjet.Check(True)
            
        self.ExpandAll() 

    def DecocherCode(self, code):
        """ Décoche un élément précis par son code """
        def chercher(branche):
            for i in range(self.GetChildrenCount(branche, recursively=False)):
                enfant = self.GetNextChild(branche, i)[0]
                data = self.GetItemPyData(enfant)
                if data and data.get("code") == code:
                    self.CheckItem(enfant, False)
                    return True
                if chercher(enfant):
                    return True
            return False
        chercher(self.root)

    def OnCheck(self, event):
        item = event.GetItem()
        categorie = self.GetPyData(item)["categorie"]
        code = self.GetPyData(item)["code"]
        etat = self.IsItemChecked(item)
        
    def GetCoches(self):
        """ Obtient la liste des éléments cochés """
        listeCodes = []
        if self.GetChildrenCount(self.root, recursively=False) == 0:
            return listeCodes
        
        brancheRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            rub_has_coches = False
            branchePage = self.GetFirstChild(brancheRubrique)[0]
            for index2 in range(self.GetChildrenCount(brancheRubrique, recursively=False)) :
                page_has_coches = False
                brancheObjet = self.GetFirstChild(branchePage)[0]
                for index3 in range(self.GetChildrenCount(branchePage, recursively=False)) :
                    if self.IsItemChecked(brancheObjet) :
                        code = self.GetItemPyData(brancheObjet)["code"]
                        listeCodes.append(code)
                        page_has_coches = True
                        rub_has_coches = True
                    brancheObjet = self.GetNextChild(branchePage, index3+1)[0]
                
                if page_has_coches:
                    codePage = self.GetItemPyData(branchePage)["code"]
                    listeCodes.append(codePage)
                branchePage = self.GetNextChild(brancheRubrique, index2+1)[0]
            
            if rub_has_coches:
                codeRubrique = self.GetItemPyData(brancheRubrique)["code"]
                listeCodes.append(codeRubrique)
            brancheRubrique = self.GetNextChild(self.root, index1+1)[0]
                        
        return listeCodes
    
    def Coche(self, etat=True):
        if self.GetChildrenCount(self.root, recursively=False) == 0:
            return
        brancheRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            self.CheckItem(brancheRubrique, etat)
            
            branchePage = self.GetFirstChild(brancheRubrique)[0]
            for index2 in range(self.GetChildrenCount(brancheRubrique, recursively=False)) :
                self.CheckItem(branchePage, etat)
                
                brancheObjet = self.GetFirstChild(branchePage)[0]
                for index3 in range(self.GetChildrenCount(branchePage, recursively=False)) :
                    if etat:
                        # Si on coche tout, ne cocher que les objets visibles
                        codeObj = self.GetItemPyData(brancheObjet).get("code")
                        est_visible = True
                        for r in self.liste_objets:
                            for p in r.get("pages", []):
                                for o in p.get("objets", []):
                                    if getattr(o, "code", None) == codeObj:
                                        est_visible = getattr(o, "visible", True)
                                        break
                        self.CheckItem(brancheObjet, est_visible)
                    else:
                        self.CheckItem(brancheObjet, False)
            
                    brancheObjet = self.GetNextChild(branchePage, index3+1)[0]
                branchePage = self.GetNextChild(brancheRubrique, index2+1)[0]
            brancheRubrique = self.GetNextChild(self.root, index1+1)[0]
    def SetCoches(self, listeCodes=[]):
        """ Coche les éléments dont le code est dans listeCodes """
        self.Coche(False)
        if not listeCodes:
            return
        brancheRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            codeRubrique = self.GetItemPyData(brancheRubrique)["code"]
            if codeRubrique in listeCodes:
                self.CheckItem(brancheRubrique, True)

            branchePage = self.GetFirstChild(brancheRubrique)[0]
            for index2 in range(self.GetChildrenCount(brancheRubrique, recursively=False)) :
                codePage = self.GetItemPyData(branchePage)["code"]
                if codePage in listeCodes:
                    self.CheckItem(branchePage, True)

                brancheObjet = self.GetFirstChild(branchePage)[0]
                for index3 in range(self.GetChildrenCount(branchePage, recursively=False)) :
                    codeObjet = self.GetItemPyData(brancheObjet)["code"]
                    if codeObjet in listeCodes:
                        self.CheckItem(brancheObjet, True)

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
