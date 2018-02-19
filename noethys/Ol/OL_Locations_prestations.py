#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from Utils import UTILS_Dates
from Utils import UTILS_Gestion
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")




class Track_prestation(object):
    def __init__(self, donnees={}):
        self.dirty = False

        champs = [
            ("IDprestation", None),
            ("label", ""),
            ("date", None),
            ("montant", 0.0),
            ("code_compta", None),
            ("tva", None),
            ("IDfacture", None)
            ]

        # Insertion des données
        for nom, defaut in champs :
            if donnees.has_key(nom):
                valeur = donnees[nom]
            else:
                valeur = defaut
            setattr(self, nom, valeur)




class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.dlg_saisie_location = kwds.pop("dlg_saisie_location", None)
        self.donnees = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)

    def SetPrestations(self, prestations=[]):
        self.donnees = prestations
        self.MAJ()

    def InitModel(self):
        pass

    def GetTracks(self):
        """ Récupération des données """
        return self.donnees

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        def FormateFacture(IDfacture):
            if IDfacture != None :
                return _(u"Oui")
            return ""

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDprestation", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 100, "date", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Label"), "left", 280, "label", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), "right", 100, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Facturé"), "right", 80, "IDfacture", typeDonnee="entier", stringConverter=FormateFacture),
            ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune prestation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, track=None):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if track != None :
            self.SelectObject(track, deselectOthers=True, ensureVisible=True)
        self.MAJtexteOnglet()

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

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetDictInfosLocation(self):
        return self.dlg_saisie_location.GetDictInfosLocation()

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_location_prestation
        dlg = DLG_Saisie_location_prestation.Dialog(self, track=Track_prestation(), dictInfosLocation=self.GetDictInfosLocation())
        if dlg.ShowModal() == wx.ID_OK:
            track = dlg.GetTrack()
            self.donnees.append(track)
            self.MAJ(track)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune prestation à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track_prestation = self.Selection()[0]

        if track_prestation.IDfacture != None :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas modifier cette prestation car elle apparaît déjà sur une facture !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        gestion = UTILS_Gestion.Gestion(None)
        if gestion.Verification("prestations", track_prestation.date) == False: return False

        from Dlg import DLG_Saisie_location_prestation
        dlg = DLG_Saisie_location_prestation.Dialog(self, track=track_prestation, dictInfosLocation=self.GetDictInfosLocation())
        if dlg.ShowModal() == wx.ID_OK:
            track_prestation = dlg.GetTrack()
            track_prestation.dirty = True
            self.MAJ(track_prestation)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune prestation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track_prestation = self.Selection()[0]

        if track_prestation.IDfacture != None :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette prestation car elle apparaît déjà sur une facture !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        gestion = UTILS_Gestion.Gestion(None)
        if gestion.Verification("prestations", track_prestation.date) == False: return False

        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette prestation ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.donnees.remove(track_prestation)
            self.MAJ()
        dlg.Destroy()

    def MAJtexteOnglet(self):
        texte = _(u"Prestations")
        total = 0.0
        for track_prestation in self.GetTracks() :
            total += track_prestation.montant
        if total > 0.0 :
            texte = u"Prestations (%.2f %s)" % (total, SYMBOLE)
        self.dlg_saisie_location.ctrl_parametres.SetTexteOnglet("facturation", texte)

# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date" : {"mode" : "nombre", "singulier" : "prestation", "pluriel" : "prestations", "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
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
