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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import datetime
from Ctrl import CTRL_Bandeau
import DLG_Saisie_email_exp
from Utils import UTILS_Utilisateurs


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL, name="config_adresses_mail")
        
        intro = _(u"Vous pouvez ici créer, modifier ou supprimer les adresses d'expéditions d'Emails. Celles-ci sont obligatoires pour pouvoir envoyer des Emails à partir du système de messagerie intégré à Noethys.")
        titre = _(u"Gestion des adresses d'expédition d'Emails")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Emails_exp.png")
        
        self.listCtrl = ListCtrl(self)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_defaut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDefaut, self.bouton_defaut)

        self.bouton_modifier.Enable(False)
        self.bouton_supprimer.Enable(False)
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une nouvelle adresse d'expéditeur")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'adresse sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'adresse sélectionnée dans la liste")))
        self.bouton_defaut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour définir l'adresse sélectionnée dans la liste comme adresse par défaut")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_boutons = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=10)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_defaut, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(5)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emails_exp", "creer") == False : return
        dlg = DLG_Saisie_email_exp.Dialog(self, IDadresse=None)
        dlg.ShowModal() 
        dlg.Destroy()
        self.listCtrl.MAJListeCtrl()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emails_exp", "modifier") == False : return
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une adresse à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        dlg = DLG_Saisie_email_exp.Dialog(self, IDadresse=ID)
        dlg.ShowModal() 
        dlg.Destroy()
        self.listCtrl.MAJListeCtrl()
        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emails_exp", "supprimer") == False : return
        index = self.listCtrl.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une adresse à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        Adresse = self.listCtrl.GetItem(index, 1).GetText()
        
        # Demande de confirmation
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer cette adresse ? \n\n> ") + Adresse))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Recherche si l'adresse supprimée est celle par défaut
        DB = GestionDB.DB()
        req = """SELECT IDadresse, defaut
        FROM adresses_mail WHERE IDadresse=%d; """ % ID
        DB.ExecuterReq(req)
        listeServeurs = DB.ResultatReq()
        IDadresseTmp, defaut = listeServeurs[0]
        
        # Suppression du type de pièce
        DB.ReqDEL("adresses_mail", "IDadresse", ID)
        
        # Attribue la valeur par défaut à une autre adresse
        if defaut == 1 :
            req = """SELECT IDadresse, adresse
            FROM adresses_mail ORDER BY adresse; """
            DB.ExecuterReq(req)
            listeServeurs = DB.ResultatReq()
            if len(listeServeurs)>0 :
                IDadresse, adresse = listeServeurs[0]
                listeDonnees = [ ("defaut", 1), ]
                DB.ReqMAJ("adresses_mail", listeDonnees, "IDadresse", IDadresse)
        DB.Close()

        # MàJ du ListCtrl
        self.listCtrl.MAJListeCtrl()
        
    def MAJ_ListCtrl(self):
        self.listCtrl.MAJListeCtrl()    

    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl() 
    
    def OnBoutonDefaut(self, event):
        self.SetDefaut() 
        
    def SetDefaut(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emails_exp", "modifier") == False : return
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune adresse dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, nom_adresse, smtp, port, defaut, connexionAuthentifiee, startTLS
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeServeurs = DB.ResultatReq()
        
        for IDadresse, adresse, nom_adresse, smtp, port, defaut, connexionAuthentifiee, startTLS in listeServeurs :
            if IDadresse == ID :
                etat = True
            else:
                etat = False
            listeDonnees = [ ("defaut", etat), ]
            DB.ReqMAJ("adresses_mail", listeDonnees, "IDadresse", IDadresse)
        DB.Close()
        
        self.listCtrl.MAJListeCtrl() 


class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.criteres = ""
        self.parent = parent
        self.valeurActuelle = None

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        self.imgActuel = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        if self.GetGrandParent().GetName() != "treebook_configuration" :
            self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 7
        self.InsertColumn(0, u"")
        self.SetColumnWidth(0, 30)
        self.InsertColumn(1, _(u"Adresse"))
        self.SetColumnWidth(1, 150)
        self.InsertColumn(2, _(u"Nom"))
        self.SetColumnWidth(2, 150)
        self.InsertColumn(3, _(u"Serveur SMTP"))
        self.SetColumnWidth(3, 150) 
        self.InsertColumn(4, _(u"Port"))
        self.SetColumnWidth(4, 50) 
        self.InsertColumn(5, _(u"Defaut"))
        self.SetColumnWidth(5, 0) 
        self.InsertColumn(6, _(u"Connexion authentifiée"))
        self.SetColumnWidth(6, 150) 
        

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = self.donnees.keys()
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(1, 1)

    def OnItemSelected(self, event):
        self.parent.bouton_modifier.Enable(True)
        self.parent.bouton_supprimer.Enable(True)
        
    def OnItemDeselected(self, event):
        self.parent.bouton_modifier.Enable(False)
        self.parent.bouton_supprimer.Enable(False)
        
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, nom_adresse, smtp, port, defaut, connexionAuthentifiee, startTLS
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(liste)
        # Création du dictionnaire de données
        self.donnees = self.listeEnDict(liste)
        
##        # Recherche de la valeur actuelle :
##        dateJour = str(datetime.date.today())
##        for ID, valeur, dateDebut in liste :
##            if dateJour >= dateDebut :
##                self.valeurActuelle = ID
            
    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

    def listeEnDict(self, liste):
        dictio = {}
        x = 1
        for ligne in liste:
            index = x # Donne un entier comme clé
            dictio[index] = ligne
            x += 1
        return dictio
           
    def OnItemActivated(self, event):
        self.parent.Modifier()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index=self.itemIndexMap[item]
        valeur = unicode(self.itemDataMap[index][col])
        
        # Port
        if col == 4 : 
            if valeur == "None" : 
                valeur = ""
        
        # SSL
        if col == 6 : 
            if valeur == "1" : 
                valeur = _(u"Oui")
            else:
                valeur = _(u"Non")
    
        # Adresse par défaut
        if col == 5 : 
            if valeur == "1" : 
                valeur = _(u"Oui")
            else:
                valeur = _(u"Non")
            
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        index=self.itemIndexMap[item]
        defaut =self.itemDataMap[index][5]
        if defaut == 1 :
            return self.imgActuel
        else:
            return -1

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Création d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #-----------------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.imgTriAz, self.imgTriZa)

    # ---------------------------------------------------------

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 0))
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        menuPop.AppendSeparator()

        # Item Défaut
        item = wx.MenuItem(menuPop, 40, _(u"Définir comme adresse par défaut"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Defaut, id=40)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.Ajouter()
        
    def Menu_Modifier(self, event):
        self.parent.Modifier()

    def Menu_Supprimer(self, event):
        self.parent.Supprimer()

    def Menu_Defaut(self, event):
        self.parent.SetDefaut()


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.panel_contenu = Panel(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)


    def __set_properties(self):
        self.SetTitle(_(u"Gestion des adresses d'expédition d'Emails"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((650, 480))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        grid_sizer_base.Add(self.panel_contenu, 1, wx.ALL|wx.EXPAND, 0)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Adressesdexpditiondemails")
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
