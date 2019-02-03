#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import six
from Utils import UTILS_Interface
from Utils import UTILS_Dates
from Ctrl import CTRL_Editeur_email
from Ctrl import CTRL_Bouton_image
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Ctrl import CTRL_Saisie_date



class Track(object):
    def __init__(self, parent, index=None, donnees=None):
        self.parent = parent
        self.index = index
        self.donnees = donnees

        self.IDelement = donnees["IDelement"]
        self.titre = donnees["titre"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]
        self.texte_xml = donnees["texte_xml"]
        self.texte_html = donnees["texte_html"]

        # Période
        if isinstance(self.date_debut, str) or isinstance(self.date_debut, six.text_type) :
            self.date_debut = datetime.datetime.strptime(self.date_debut, "%Y-%m-%d %H:%M:%S")

        if isinstance(self.date_fin, str) or isinstance(self.date_fin, six.text_type) :
            self.date_fin = datetime.datetime.strptime(self.date_fin, "%Y-%m-%d %H:%M:%S")

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.listeDonnees = []
        self.newID = 0
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetDonnees(self):
        return self.listeDonnees

    def SetDonnees(self, listeDonnees=[]):
        self.listeDonnees = listeDonnees
        self.MAJ()

    def GetTracks(self):
        """ Récupération des données """
        listeListeView = []
        index = 0
        for item in self.listeDonnees :
            track = Track(self, index, item)
            listeListeView.append(track)
            index += 1
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDate(date):
            if date == None :
                return _(u"Non définie")
            else :
                return datetime.datetime.strftime(date, "%d/%m/%Y - %Hh%M")

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDelement", typeDonnee="texte"),
            ColumnDefn(_(u"Du"), "left", 120, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Au"), "left", 120, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Titre"), "left", 230, "titre", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun article"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SortBy(1, ascending=False)
        self.SetObjects(self.donnees)
       
    def MAJ(self, index=None):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if index != None :
            self.SelectObject(self.GetObjectAt(index), deselectOthers=True, ensureVisible=True)
        self._ResizeSpaceFillingColumns()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
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

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetIDprovisoire(self):
        """ Création d'un ID négatif provisoire """
        self.newID -= 1
        return int(self.newID)

    def Ajouter(self, event):
        dlg = DLG_Saisie_element(self)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees()
            dictDonnees["IDelement"] = self.GetIDprovisoire()
            self.listeDonnees.append(dictDonnees)
            self.MAJ(len(self.listeDonnees)-1)
        dlg.Destroy()
        
    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun article à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_element(self)
        dlg.SetDonnees(track.donnees)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees()
            self.listeDonnees[track.index] = dictDonnees
            self.MAJ(track.index)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun article à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cet article ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listeDonnees.pop(track.index)
            self.MAJ()
        dlg.Destroy()



# -------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Saisie_element(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictDonnees = {}

        # Titre
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_titre = wx.StaticText(self, -1, _(u"Titre de l'article :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, "")

        # Dates
        self.label_date_debut = wx.StaticText(self, -1, _(u"Publication du :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self, heure=True)
        self.ctrl_date_debut.SetDate(datetime.datetime.now())
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self, heure=True)

        # Editeur
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, _(u"Texte"))
        self.ctrl_editeur = CTRL_Editeur_email.CTRL(self)

        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un article"))
        self.ctrl_titre.SetToolTip(wx.ToolTip(_(u"Saisissez ici le titre de l'article")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((700, 580))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_titre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_titre, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(grid_sizer_dates, 0, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_generalites, 0, wx.EXPAND | wx.ALL, 10)

        # Editeur
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        staticbox_texte.Add(self.ctrl_editeur, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_texte, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        # Validation
        if len(self.ctrl_titre.GetValue()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre pour cet article !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return

        if self.ctrl_date_debut.Validation() == False or self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de publication !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        if self.ctrl_date_fin.GetDate() != None and self.ctrl_date_fin.Validation() == False :
            self.ctrl_date_fin.SetFocus()
            return

        if self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir saisir de date de fin de publication ?"), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        if len(self.ctrl_editeur.GetValue()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return

        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        self.dictDonnees["titre"] = self.ctrl_titre.GetValue()
        self.dictDonnees["date_debut"] = self.ctrl_date_debut.GetDate()
        self.dictDonnees["date_fin"] = self.ctrl_date_fin.GetDate()
        self.dictDonnees["texte_xml"] = self.ctrl_editeur.GetXML()
        self.dictDonnees["texte_html"] = self.ctrl_editeur.GetHTML_base64()
        return self.dictDonnees

    def SetDonnees(self, dictDonnees={}):
        self.dictDonnees = dictDonnees
        self.SetTitle(_(u"Modification d'un article"))
        if "titre" in self.dictDonnees :
            self.ctrl_titre.SetValue(self.dictDonnees["titre"])
        if "date_debut" in self.dictDonnees :
            self.ctrl_date_debut.SetDate(self.dictDonnees["date_debut"])
        if "date_fin" in self.dictDonnees :
            self.ctrl_date_fin.SetDate(self.dictDonnees["date_fin"])
        if "texte_xml" in self.dictDonnees :
            self.ctrl_editeur.SetXML(self.dictDonnees["texte_xml"])





# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        listeParametres = [
            {"IDelement" : 1, "titre" : u"Article 1", "date_debut" : None, "date_fin" : None, "texte_xml" : "", "texte_html" : ""},
            {"IDelement" : 2, "titre" : u"Article 2", "date_debut" : None, "date_fin" : None, "texte_xml" : "", "texte_html" : ""},
        ]
        self.myOlv.SetDonnees(listeParametres)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
