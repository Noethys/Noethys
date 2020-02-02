#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
from Utils import UTILS_Parametres



COULEURS = [
    {"label": _(u"Gris"), "code": "gray", "couleur": "#d2d6de"},
    {"label": _(u"Rouge"), "code": "danger", "couleur": "#dd4b39"},
    {"label": _(u"Orange"), "code": "warning", "couleur": "#f39c12"},
    {"label": _(u"Bleu foncé"), "code": "primary", "couleur": "#3c8dbc"},
    {"label": _(u"Bleu clair"), "code": "info", "couleur": "#00c0ef"},
    {"label": _(u"Vert"), "code": "success", "couleur": "#00a65a"},
]



class CTRL_Couleur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictCouleur in COULEURS:
            self.dictDonnees[index] = {"ID": dictCouleur["code"], "label": dictCouleur["label"], "couleur": dictCouleur["couleur"]}
            listeItems.append(dictCouleur["label"])
            index += 1
        self.SetItems(listeItems)

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

    def GetCouleur(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["couleur"]

    def SetCouleur(self, couleur=""):
        for index, values in self.dictDonnees.items():
            if values["couleur"] == couleur:
                self.SetSelection(index)





class CTRL(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.BORDER_THEME | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.parent = parent
        self.dictItems = {}

        # Binds
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.Modifier)

    def CreationImage(self, tailleImages, couleur=(255, 255, 255), type_element="page"):
        """ Création des images pour le TreeCtrl """
        if couleur == None :
            return None
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(tailleImages[0], tailleImages[1])
        else :
            bmp = wx.EmptyBitmap(tailleImages[0], tailleImages[1])
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(dc)
        gc.PushState()
        if type_element == "page" :
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(couleur, 2, wx.SOLID))
            gc.DrawEllipse(2, 3, 8, 8)
        if type_element == "bloc" :
            gc.SetBrush(wx.Brush(couleur, wx.SOLID))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(2, 3, tailleImages[0]-2, tailleImages[1]-6)
        gc.PopState()
        del dc
        return bmp

    def Importation(self):
        """ Importation des pages et des blocs """
        DB = GestionDB.DB()

        # Importation des blocs
        req = """
        SELECT IDbloc, IDpage, titre, couleur, ordre
        FROM portail_blocs
        ORDER BY ordre
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictBlocsParPage = {}
        for IDbloc, IDpage, titre, couleur, ordre in listeDonnees :
            dictTemp = {"IDbloc" : IDbloc, "titre" : titre, "couleur" : couleur, "ordre" : ordre}
            if (IDpage in dictBlocsParPage) == False :
                dictBlocsParPage[IDpage] = []
            dictBlocsParPage[IDpage].append(dictTemp)

        # Importation des pages
        req = """
        SELECT IDpage, titre, couleur, ordre
        FROM portail_pages
        ORDER BY ordre
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        DB.Close()
        listePages = []
        for IDpage, titre, couleur, ordre in listeDonnees:
            if IDpage in dictBlocsParPage :
                listeBlocs = dictBlocsParPage[IDpage]
            else :
                listeBlocs = []
            dictTemp = {"IDpage": IDpage, "titre": titre, "couleur": couleur, "ordre": ordre, "listeBlocs" : listeBlocs}
            listePages.append(dictTemp)

        return listePages

    def RechercheCouleur(self, code=""):
        for dictCouleur in COULEURS :
            if code == dictCouleur["code"] :
                return dictCouleur["couleur"]
        return None

    def Remplissage(self):
        """ Remplissage """
        self.dictItems = {"pages" : {}, "blocs" : {}}

        # Importation
        self.listePages = self.Importation()

        # Imagelist
        tailleImages = (11,16)
        self.il = wx.ImageList(tailleImages[0], tailleImages[1])
        if 'phoenix' in wx.PlatformInfo:
            self.imgRoot = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))
        else :
            self.imgRoot = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))

        self.dictImages = {"pages" : {}, "blocs" : {}}
        for dictPage in self.listePages :
            couleur = self.RechercheCouleur(code=dictPage["couleur"])
            if couleur != None :
                self.dictImages["pages"][dictPage["IDpage"]] = self.il.Add(self.CreationImage(tailleImages, couleur, "page"))
            for dictBloc in dictPage["listeBlocs"] :
                couleur = self.RechercheCouleur(code=dictBloc["couleur"])
                if couleur != None :
                    self.dictImages["blocs"][dictBloc["IDbloc"]] = self.il.Add(self.CreationImage(tailleImages, couleur, "bloc"))

        self.SetImageList(self.il)
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Pages"))
        
        # Création des branches activités
        for dictPage in self.listePages :
            item_page = self.AppendItem(self.root, dictPage["titre"])
            self.SetItemBold(item_page)
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(item_page, {"type" : "page", "ID" : dictPage["IDpage"], "ordre" : dictPage["ordre"]})
            else:
                self.SetPyData(item_page, {"type" : "page", "ID" : dictPage["IDpage"], "ordre" : dictPage["ordre"]})
            if dictPage["IDpage"] in self.dictImages["pages"]:
                self.SetItemImage(item_page, self.dictImages["pages"][dictPage["IDpage"]], wx.TreeItemIcon_Normal)
            self.dictItems["pages"][dictPage["IDpage"]] = item_page

            # Création des branches blocs
            for dictBloc in dictPage["listeBlocs"]:
                item_bloc = self.AppendItem(item_page, dictBloc["titre"])
                if 'phoenix' in wx.PlatformInfo:
                    self.SetItemData(item_bloc, {"type": "bloc", "ID": dictBloc["IDbloc"], "ordre": dictBloc["ordre"]})
                else:
                    self.SetPyData(item_bloc, {"type": "bloc", "ID": dictBloc["IDbloc"], "ordre": dictBloc["ordre"]})
                if dictBloc["IDbloc"] in self.dictImages["blocs"]:
                    self.SetItemImage(item_bloc, self.dictImages["blocs"][dictBloc["IDbloc"]], wx.TreeItemIcon_Normal)
                self.dictItems["blocs"][dictBloc["IDbloc"]] = item_bloc

        self.ExpandAll()

    def MAJ(self, IDpage=None, IDbloc=None):
        self.Freeze()
        self.DeleteAllItems()
        self.Remplissage()
        self.Thaw()
        self.SetID(IDpage=IDpage, IDbloc=IDbloc)

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Recherche et sélection de l'item pointé avec la souris
        item = self.FindTreeItem(event.GetPosition())
        if item != None:
            dictData = self.GetPyData(item)
            self.SelectItem(item, True)
        else :
            dictData = None

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        itemx = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
        itemx = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if item == None : itemx.Enable(False)

        # Item Supprimer
        itemx = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if item == None : itemx.Enable(False)

        menuPop.AppendSeparator()

        # Item Deplacer vers le haut
        itemx = wx.MenuItem(menuPop, 40, _(u"Déplacer vers le haut"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)
        if item == None : itemx.Enable(False)

        # Item Déplacer vers le bas
        itemx = wx.MenuItem(menuPop, 50, _(u"Déplacer vers le bas"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        if item == None : itemx.Enable(False)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def FindTreeItem(self, position):
        """ Permet de retrouver l'item pointé dans le TreeCtrl """
        item, flags = self.HitTest(position)
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL |
                             wx.TREE_HITTEST_ONITEMICON):
            return item
        return None
    
    def Ajouter(self, event):
        """ Ajouter une page ou un bloc """
        # Demande quel élément créer
        dlg = DLG_Choix_creation(self)
        if len(self.listePages) == 0 :
            dlg.bouton_bloc.Enable(False)
        reponse = dlg.ShowModal()
        dlg.Destroy()

        # Création d'une page
        if reponse == 100 :
            dlg = DLG_Saisie_page(self, IDpage=None)
            if dlg.ShowModal() == wx.ID_OK:
                self.MAJ(IDpage=dlg.GetID())
                self.MemoriseDateModification()
            dlg.Destroy()

        # Création d'un bloc
        if reponse == 200 :
            from Dlg import DLG_Saisie_portail_bloc
            dlg = DLG_Saisie_portail_bloc.Dialog(self, IDbloc=None)
            if dlg.ShowModal() == wx.ID_OK:
                self.MAJ(IDbloc=dlg.GetID())
                self.MemoriseDateModification()
            dlg.Destroy()

    def Modifier(self, event):
        """ Modifier une page ou un bloc """
        item = self.GetSelection()
        if 'phoenix' in wx.PlatformInfo:
            dictData = self.GetItemData(item)
        else:
            dictData = self.GetPyData(item)
        if item == None or dictData == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une page ou un bloc à modifier !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Modification d'une page
        if dictData["type"] == "page" :
            dlg = DLG_Saisie_page(self, IDpage=dictData["ID"])
            if dlg.ShowModal() == wx.ID_OK:
                self.MAJ(IDpage=dlg.GetID())
                self.MemoriseDateModification()
            dlg.Destroy()

        # Modification d'un bloc
        if dictData["type"] == "bloc":
            from Dlg import DLG_Saisie_portail_bloc
            dlg = DLG_Saisie_portail_bloc.Dialog(self, IDbloc=dictData["ID"])
            if dlg.ShowModal() == wx.ID_OK:
                self.MAJ(IDbloc=dlg.GetID())
                self.MemoriseDateModification()
            dlg.Destroy()

    def GetItemsEnfants(self, liste=[], item=None, recursif=True):
        itemTemp, cookie = self.GetFirstChild(item)
        for index in range(0, self.GetChildrenCount(item, recursively=False)) :
            if 'phoenix' in wx.PlatformInfo:
                dictDataTemp = self.GetItemData(itemTemp)
            else:
                dictDataTemp = self.GetPyData(itemTemp)
            liste.append(dictDataTemp)
            if recursif == True and self.GetChildrenCount(itemTemp, recursively=False) > 0 :
                self.GetItemsEnfants(liste, itemTemp, recursif)
            itemTemp, cookie = self.GetNextChild(item, cookie)

    def Supprimer(self, event):
        item = self.GetSelection()
        dictData = self.GetPyData(item)
        if item == None or dictData == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une page ou un bloc à supprimer !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dictData = self.GetPyData(item)

        # Suppression d'une page
        if dictData["type"] == "page" :

            # Confirmation de suppression des blocs
            listeTousEnfants = []
            if self.GetChildrenCount(item, recursively=True) > 0 :

                # Récupère la liste des tous les items enfants (récursif)
                self.GetItemsEnfants(listeTousEnfants, item)

                # Demande de confirmation
                dlg = wx.MessageDialog(self, _(u"Attention, cette page comporte des blocs.\n\nSouhaitez-vous vraiment supprimer cette page ? Les blocs seront également supprimées !"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    return

            # Confirmation de suppression
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette page ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES :
                DB = GestionDB.DB()

                # Suppression de la page
                DB.ReqDEL("portail_pages", "IDpage", dictData["ID"])

                # Suppression des blocs également
                for dictTemp in listeTousEnfants :
                    DB.ReqDEL("portail_blocs", "IDbloc", dictTemp["ID"])
                    DB.ReqDEL("portail_elements", "IDbloc", dictTemp["ID"])

                # Modification de l'ordre des pages
                itemParent = self.GetItemParent(item)
                listeItemsSoeurs = []
                self.GetItemsEnfants(liste=listeItemsSoeurs, item=itemParent, recursif=False)
                ordre = 1
                for dictDataTemp in listeItemsSoeurs :
                    if dictDataTemp["ID"] != dictData["ID"] :
                        DB.ReqMAJ("portail_pages", [("ordre", ordre),], "IDpage", dictDataTemp["ID"])
                        ordre += 1

                DB.Close()
                self.MAJ()

            dlg.Destroy()
        

        # Suppression d'un bloc
        if dictData["type"] == "bloc" :

            # Confirmation de suppression
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce bloc ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES :
                DB = GestionDB.DB()

                # Suppression du bloc
                DB.ReqDEL("portail_blocs", "IDbloc", dictData["ID"])
                DB.ReqDEL("portail_elements", "IDbloc", dictData["ID"])

                # Modification de l'ordre des blocs
                itemParent = self.GetItemParent(item)
                listeItemsSoeurs = []
                self.GetItemsEnfants(liste=listeItemsSoeurs, item=itemParent, recursif=False)
                ordre = 1
                for dictDataTemp in listeItemsSoeurs :
                    if dictDataTemp["ID"] != dictData["ID"] :
                        DB.ReqMAJ("portail_blocs", [("ordre", ordre),], "IDbloc", dictDataTemp["ID"])
                        ordre += 1

                DB.Close()
                self.MAJ()

            dlg.Destroy()

        # Mémorise la date de la modification
        self.MemoriseDateModification()

    def Monter(self, event):
        """ Déplacer vers le haut """
        self.Deplacer(-1)

    def Descendre(self, event):
        self.Deplacer(1)

    def Deplacer(self, sens=-1) :
        item = self.GetSelection()
        if item == None or self.GetPyData(item) == None :
            return
        
        # Recherche l'item à remplacer
        if sens == -1 :
            itemRemplace = self.GetPrevSibling(item)
        else :
            itemRemplace = self.GetNextSibling(item)
        if itemRemplace == None or itemRemplace.IsOk() == False :
            return
        
        dictData = self.GetPyData(item)
        dictDataRemplace = self.GetPyData(itemRemplace)
        
        DB = GestionDB.DB()
        if dictData["type"] == "page" :
            DB.ReqMAJ("portail_pages", [("ordre", dictData["ordre"] + sens),], "IDpage", dictData["ID"])
            DB.ReqMAJ("portail_pages", [("ordre", dictData["ordre"]),], "IDpage", dictDataRemplace["ID"])
        if dictData["type"] == "bloc" :
            DB.ReqMAJ("portail_blocs", [("ordre", dictData["ordre"] + sens),], "IDbloc", dictData["ID"])
            DB.ReqMAJ("portail_blocs", [("ordre", dictData["ordre"]),], "IDbloc", dictDataRemplace["ID"])
        DB.Commit()
        DB.Close()
        
        # MAJ du contrôle
        if dictData["type"] == "page":
            self.MAJ(IDpage=dictData["ID"])
        if dictData["type"] == "bloc":
            self.MAJ(IDbloc=dictData["ID"])

        # Mémorise la date de la modification
        self.MemoriseDateModification()

    def SetID(self, IDpage=None, IDbloc=None):
        item = None
        if IDpage != None :
            if IDpage in self.dictItems["pages"] :
                item = self.dictItems["pages"][IDpage]
        if IDbloc != None :
            if IDbloc in self.dictItems["blocs"] :
                item = self.dictItems["blocs"][IDbloc]
        if item != None :
            self.EnsureVisible(item)
            self.SelectItem(item)
    
    def SelectPremierItem(self):
        item, cookie = self.GetFirstChild(self.root)
        self.SelectItem(item)

    def GetItem(self, IDetiquette=None, IDactivite=None):
        if IDetiquette in self.dictItems :
            return self.dictItems[IDetiquette]
        else :
            item, cookie = self.GetFirstChild(self.root)
            for index in range(0, self.GetChildrenCount(self.root, recursively=False)) :
                dictData = self.GetPyData(item)
                if dictData["IDetiquette"] == IDetiquette and dictData["IDactivite"] == IDactivite :
                    return item
                item, cookie = self.GetNextChild(item, cookie)
        return None
        
    def GetNbreEnfants(self, item):
        nbre = self.GetChildrenCount(item, recursively=False)
        return nbre

    def MemoriseDateModification(self):
        UTILS_Parametres.Parametres(mode="set", categorie="portail", nom="last_update_pages", valeur=str(datetime.datetime.now()))




# -------------------------------------------------------------------------------------------------------------------------------------------


class DLG_Choix_creation(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.bouton_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Nouvelle_page.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_bloc = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Nouveau_bloc.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.bouton_page.SetMinSize((140, 120))
        self.bouton_bloc.SetMinSize((140, 120))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonPage, self.bouton_page)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBloc, self.bouton_bloc)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Choix de l'élément à créer"))
        self.bouton_page.SetToolTip(wx.ToolTip(_(u"Créer une nouvelle page.\n\nUne page est vide lors de sa création. Vous devez donc ensuite la remplir avec un ou plusieurs blocs.")))
        self.bouton_bloc.SetToolTip(wx.ToolTip(_(u"Créer un nouveau bloc pour une page.\n\nChaque page est constituée d'un ou plusieurs bloc. Il existe plusieurs types de blocs. Exemples : Texte, onglets, calendrier, etc...")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler")))
        self.SetMinSize((340, 230))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.bouton_page, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.Add(self.bouton_bloc, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonPage(self, event):
        self.EndModal(100)

    def OnBoutonBloc(self, event):
        self.EndModal(200)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")


# --------------------------------------------------------------------------------------------------------------------

class DLG_Saisie_page(wx.Dialog):
    def __init__(self, parent, IDpage=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDpage = IDpage

        self.label_titre = wx.StaticText(self, wx.ID_ANY, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.label_couleur = wx.StaticText(self, wx.ID_ANY, _(u"Couleur :"))
        self.ctrl_couleur = CTRL_Couleur(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        if self.IDpage != None:
            self.SetTitle(_(u"Modification d'une page"))
            self.Importation()
        else:
            self.SetTitle(_(u"Saisie d'une page"))

    def __set_properties(self):
        self.ctrl_titre.SetToolTip(wx.ToolTip(_(u"Saisissez le titre de la page")))
        self.ctrl_couleur.SetToolTip(wx.ToolTip(_(u"Sélectionnez une couleur")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)

        grid_sizer_haut = wx.FlexGridSizer(3, 2, 10, 10)

        grid_sizer_haut.Add(self.label_titre, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_titre, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_couleur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_couleur, 0, 0, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        if self.Sauvegarde() == False:
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        """ Sauvegarde des données """
        titre = self.ctrl_titre.GetValue()
        couleur = self.ctrl_couleur.GetID()

        # Validation des données saisies
        if titre == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return False

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("titre", titre),
            ("couleur", couleur),
        ]

        # Recherche l'ordre pour la création d'une nouvelle page
        if self.IDpage == None :
            req = """SELECT MAX(ordre) FROM portail_pages;"""
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if len(listeTemp) == 0 or listeTemp[0][0] == None :
                ordre = 1
            else :
                ordre = listeTemp[0][0] + 1
            listeDonnees.append(("ordre", ordre))

        # Sauvegarde
        if self.IDpage == None:
            self.IDpage = DB.ReqInsert("portail_pages", listeDonnees)
        else:
            DB.ReqMAJ("portail_pages", listeDonnees, "IDpage", self.IDpage)

        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT titre, couleur
        FROM portail_pages
        WHERE IDpage=%d;""" % self.IDpage
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0: return
        titre, couleur = listeTemp[0]
        if titre == None: titre = ""
        if couleur == None: couleur = ""
        self.ctrl_titre.SetValue(titre)
        self.ctrl_couleur.SetID(couleur)

    def GetID(self):
        return self.IDpage








# --------------------------------------------------------------------------------------------------------------------

class DLG_Saisie_bloc(wx.Dialog):
    def __init__(self, parent, IDbloc=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDbloc = IDbloc

        self.label_titre = wx.StaticText(self, wx.ID_ANY, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.label_couleur = wx.StaticText(self, wx.ID_ANY, _(u"Couleur :"))
        self.ctrl_couleur = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        if self.IDbloc != None:
            self.SetTitle(_(u"Modification d'un bloc"))
            self.Importation()
        else:
            self.SetTitle(_(u"Saisie d'un bloc"))

    def __set_properties(self):
        self.ctrl_titre.SetToolTip(wx.ToolTip(_(u"Saisissez le titre du bloc")))
        self.ctrl_couleur.SetToolTip(wx.ToolTip(_(u"Sélectionnez une couleur")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)

        grid_sizer_haut = wx.FlexGridSizer(3, 2, 10, 10)

        grid_sizer_haut.Add(self.label_titre, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_titre, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_couleur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_couleur, 0, 0, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        if self.Sauvegarde() == False:
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        """ Sauvegarde des données """
        titre = self.ctrl_titre.GetValue()
        couleur = self.ctrl_couleur.GetValue()
        IDpage = 1 # PROVISOIRE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Validation des données saisies
        if titre == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return False

        if couleur == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une couleur !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_couleur.SetFocus()
            return False

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDpage", IDpage),
            ("titre", titre),
            ("couleur", couleur),
        ]

        # Recherche l'ordre pour la création d'une nouvelle page
        if self.IDbloc == None :
            req = """SELECT MAX(ordre) FROM portail_blocs WHERE IDpage=%d;""" % IDpage
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if len(listeTemp) == 0 or listeTemp[0][0] == None :
                ordre = 1
            else :
                ordre = listeTemp[0][0] + 1
            listeDonnees.append(("ordre", ordre))

        # Sauvegarde
        if self.IDbloc == None:
            self.IDbloc = DB.ReqInsert("portail_blocs", listeDonnees)
        else:
            DB.ReqMAJ("portail_blocs", listeDonnees, "IDbloc", self.IDbloc)

        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT titre, couleur
        FROM portail_blocs
        WHERE IDbloc=%d;""" % self.IDbloc
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0: return
        titre, couleur = listeTemp[0]
        if titre == None: titre = ""
        if couleur == None: couleur = ""
        self.ctrl_titre.SetValue(titre)
        self.ctrl_couleur.SetValue(couleur)

    def GetID(self):
        return self.IDbloc



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    
    # Test Dialog de sélection d'étiquettes
    # frame_1 = DialogSelection(None, listeActivites=[1,])
    # app.SetTopWindow(frame_1)
    # frame_1.ShowModal()
    # app.MainLoop()
