#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import copy
import datetime
import time
import GestionDB
from Utils import UTILS_Config
from Utils import UTILS_Interface



if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC


COULEUR_TRAIT = wx.Colour(200, 200, 200)
COULEUR_TEXTE = "BLACK"
COULEUR_DISPONIBLE = "#E3FEDB"
COULEUR_ALERTE = "#FEFCDB"
COULEUR_COMPLET = "#F7ACB2"
COULEUR_GAUGE_FOND = "WHITE"



class Renderer_gauge(object):
    def __init__(self, parent):
        self.parent = parent
        self.hauteurGauge = 18
        self.seuil_alerte = self.parent.seuil_alerte
        self.nbre_inscrits = 0
        self.nbre_inscrits_max = 0
        self.mode = "activite"

    def DrawSubItem(self, dc, rect, line, highlighted, enabled):
        canvas = wx.EmptyBitmap(rect.width, rect.height)
        mdc = wx.MemoryDC()
        mdc.SelectObject(canvas)
        
        # Dessin du fond
        # if highlighted:
        #     mdc.SetBackground(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)))
        # else:
        #     couleurFond = self.parent.couleurFond
        #     mdc.SetBackground(wx.Brush(couleurFond))

        if self.couleur_fond != None :
            couleur_fond = self.couleur_fond
        else:
            couleur_fond = self.parent.couleurFond
        mdc.SetBackground(wx.Brush(couleur_fond))
        mdc.Clear()
        
        # Dessin de la gauge
        if self.nbre_inscrits_max > 0 :
            self.DrawGauge(mdc, 0, 0, rect.width, rect.height)
        
        # Dessin du texte
        mdc.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        if self.nbre_inscrits == 1 :
            texte = _(u"1 inscrit")
        else :
            texte = _(u"%d inscrits") % self.nbre_inscrits
        #if self.nbrePlacesAttente > 0 :
        #    texte += _(u" + %d en attente") % self.nbrePlacesAttente
        if self.nbre_inscrits_max > 0 :
            texte += _(u" / %d places") % self.nbre_inscrits_max
        #else :
        #    texte += _(u" / places illimitées")
        textWidth, dummy = mdc.GetTextExtent(texte)
        mdc.SetTextForeground(COULEUR_TEXTE)
        x = rect.width/2 - textWidth/2
        x = 0 + 4
        mdc.DrawText(texte, x, rect.height/2 - dummy/2)
        
        # Double buffering
        dc.SetClippingRegion(rect.x, rect.y, rect.width, rect.height)
        dc.Blit(rect.x+3, rect.y, rect.width-6, rect.height, mdc, 0, 0)
        dc.DestroyClippingRegion()
        
    def GetLineHeight(self):
        return self.hauteurGauge + 3

    def GetSubItemWidth(self):
        return 10

    def DrawGauge(self, dc, x, y, w, h):
        w -= 8

        # Gauge de fond
        dc.SetBrush(wx.Brush(COULEUR_GAUGE_FOND))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0, (h-self.hauteurGauge)/2 , w, self.hauteurGauge)

        # Gauge d'inscriptions
        if self.nbre_inscrits_max != 0 :
            largeurGauge = 1.0 * self.nbre_inscrits / self.nbre_inscrits_max * w
        else :
            largeurGauge = w
        if largeurGauge > w :
            largeurGauge = w
        
        etat = "disponible"
        if self.nbre_inscrits_max == 0 :
            couleur = COULEUR_DISPONIBLE
        else :
            nbrePlacesRestantes = self.nbre_inscrits_max - self.nbre_inscrits
            if nbrePlacesRestantes > self.seuil_alerte : 
                etat = "disponible"
                couleur = COULEUR_DISPONIBLE
            if nbrePlacesRestantes > 0 and nbrePlacesRestantes <= self.seuil_alerte : 
                etat = "alerte"
                couleur = COULEUR_ALERTE
            if nbrePlacesRestantes <= 0 : 
                etat = "complet"
                couleur = COULEUR_COMPLET

        dc.SetBrush(wx.Brush(couleur))
        dc.SetPen(wx.Pen(COULEUR_TRAIT, 1))
        dc.DrawRectangle(0, (h-self.hauteurGauge)/2 , largeurGauge, self.hauteurGauge)
        
        if etat == "alerte" :
            tailleImage = 16
            dc.DrawBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_ANY) , largeurGauge-tailleImage-2, (h-tailleImage)/2)

    def SetValeurs(self, mode="activite", couleur_fond=None, nbre_inscrits=0, nbre_inscrits_max=0):
        self.mode = mode
        self.couleur_fond = couleur_fond
        self.nbre_inscrits = nbre_inscrits
        self.nbre_inscrits_max = nbre_inscrits_max

        
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
class CTRL(ULC.UltimateListCtrl):
    def __init__(self, parent, style=ULC.ULC_SINGLE_SEL | ULC.ULC_REPORT | ULC.ULC_NO_HEADER | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT):
        ULC.UltimateListCtrl.__init__(self, parent, -1, agwStyle=style)
        self.parent = parent
        self.listeActivites = []
        self.filtre = None
        
        self.couleurFond = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        # self.couleurFond = wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK)
        self.SetBackgroundColour(self.couleurFond)

        # Création des colonnes
        self.InsertColumn(0, _(u"Nom de l'activité"), width=200, format=ULC.ULC_FORMAT_RIGHT)
        self.InsertColumn(1, _(u"Nbre inscrits"), width=200, format=ULC.ULC_FORMAT_CENTRE)
        
        # Binds
        self.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    def OnLeftDown(self, event):
        pass

    def OnContextMenu(self, event):
        # Sélection de l'item cliqué
        item, flags = self.HitTest((event.GetX(), event.GetY()))
        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            self.Select(item)

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Actualiser
        item = wx.MenuItem(menuPop, 10, _(u"Consulter les tarifs de l'activité"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirTarifs, id=10)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnItemActivated(self, event):
        self.OuvrirTarifs()

    def OuvrirTarifs(self, event=None):
        index = self.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        data = self.GetItemPyData(index)
        IDactivite = data["IDactivite"]
        from Dlg import DLG_Liste_tarifs
        dlg = DLG_Liste_tarifs.DLG_Tarifs(self, IDactivite=IDactivite)
        dlg.ShowModal()
        dlg.Destroy()


    def MAJ(self, forcerActualisation=False):
        condition = ""

        DB = GestionDB.DB()

        # Recherche des paramètres
        parametres = UTILS_Config.GetParametre("nbre_inscrits_parametre_activites", defaut=None)
        if parametres != None :
            code, liste = parametres.split("###")
            if liste != "" :
                listeID = []
                for ID in liste.split(";") :
                    listeID.append(int(ID))
                if code == "liste_groupes_activites" :
                    req = """SELECT IDtype_groupe_activite, IDactivite
                    FROM groupes_activites
                    WHERE IDtype_groupe_activite IN %s
                    ;""" % GestionDB.ConvertConditionChaine(listeID)
                    DB.ExecuterReq(req)
                    listeDonnees = DB.ResultatReq()
                    listeActivites = []
                    for IDtype_groupe_activite, IDactivite in listeDonnees :
                        listeActivites.append(IDactivite)
                    condition = "AND activites.IDactivite IN %s" % GestionDB.ConvertConditionChaine(listeActivites)

                if code == "liste_activites" :
                    condition = "AND activites.IDactivite IN %s" % GestionDB.ConvertConditionChaine(listeID)

        # Tri
        tri = UTILS_Config.GetParametre("nbre_inscrits_parametre_tri", 3)
        if tri == 0 :
            tri = "activites.nom"
        elif tri == 1 :
            tri = "activites.date_debut"
        elif tri == 2 :
            tri = "activites.date_fin"
        else :
            tri = "activites.nom"
        
        # Sens
        sens = UTILS_Config.GetParametre("nbre_inscrits_parametre_sens", 1)
        if sens == 0 :
            sens = ""
        else :
            sens = "DESC"
        
        # Seuil d'alerte
        self.seuil_alerte = UTILS_Config.GetParametre("nbre_inscrits_parametre_alerte", 5)

        # Récupération des groupes
        req = """SELECT groupes.IDgroupe, groupes.IDactivite, groupes.nom, groupes.nbre_inscrits_max,
        COUNT(inscriptions.IDinscription) as nbre_inscriptions
        FROM groupes
        LEFT JOIN activites ON activites.IDactivite = groupes.IDactivite
        LEFT JOIN inscriptions ON inscriptions.IDgroupe = groupes.IDgroupe
        WHERE inscriptions.statut='ok' %s
        GROUP BY groupes.IDgroupe
        ORDER BY groupes.ordre
        ;""" % condition
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()

        dictGroupes = {}
        for IDgroupe, IDactivite, nom, nbre_inscrits_max, nbre_inscrits in listeGroupes :
            if nbre_inscrits_max == None : nbre_inscrits_max = 0
            if nbre_inscrits == None : nbre_inscrits = 0
            if nom == None : nom = _(u"Sans nom !")

            if (IDactivite in dictGroupes) == False :
                dictGroupes[IDactivite] = []
            dictGroupes[IDactivite].append({"IDgroupe" : IDgroupe, "nom" : nom, "nbre_inscrits_max" : nbre_inscrits_max, "nbre_inscrits" : nbre_inscrits, "IDactivite" : IDactivite})

        # Récupération des activités
        activite_ouverte = UTILS_Config.GetParametre("nbre_inscrits_parametre_ouvert", 1)
        if activite_ouverte == 1 :
            if condition == "" :
                condition = "WHERE activites.date_fin>='%s'" % str(datetime.date.today())
            else :
                condition += " AND activites.date_fin>='%s'" % str(datetime.date.today())

        req = """SELECT activites.IDactivite, activites.nom, activites.nbre_inscrits_max
        FROM activites
        %s
        GROUP BY activites.IDactivite
        ;""" % condition
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()

        DB.Close()

        listeActivitesTemp = []
        for IDactivite, nom, nbre_inscrits_max in listeActivites :
            if nbre_inscrits_max == None : nbre_inscrits_max = 0
            if nom == None : nom = _(u"Sans nom !")

            liste_groupes = []
            if IDactivite in dictGroupes :
                liste_groupes = dictGroupes[IDactivite]
            nbre_inscrits = 0
            liste_infos = [nom,]
            for dictGroupe in liste_groupes :
                nbre_inscrits += dictGroupe["nbre_inscrits"]
                liste_infos.append(dictGroupe["nom"])

            listeActivitesTemp.append({"IDactivite" : IDactivite, "nom" : nom, "nbre_inscrits_max" : nbre_inscrits_max, "nbre_inscrits" : nbre_inscrits, "liste_groupes" : liste_groupes, "infos" : " ".join(liste_infos)})
        
        # Pour éviter l'actualisation de l'affichage si aucune modification des données
        if self.listeActivites != listeActivitesTemp or forcerActualisation == True :
            self.listeActivites = listeActivitesTemp
        else :
            return

        # MAJ du contrôle
        self.Freeze()
        self.DeleteAllItems()

        self.dictRenderers = {}
        index = 0
        for dictActivite in self.listeActivites :

            if self.filtre == None or (self.filtre.lower() in dictActivite["infos"].lower()) :

                couleur_fond = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(214, 250, 199))

                # Colonne Activité
                label = u" " + dictActivite["nom"]
                self.InsertStringItem(index, label)
                self.SetItemPyData(index, dictActivite)
                self.SetItemBackgroundColour(index, couleur_fond)

                item = self.GetItem(index, 0)
                font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
                font.SetWeight(wx.BOLD)
                item.SetFont(font)
                self.SetItem(item)

                # Colonne Gauge
                renderer = Renderer_gauge(self)
                renderer.SetValeurs(mode="activite", couleur_fond=couleur_fond, nbre_inscrits=dictActivite["nbre_inscrits"], nbre_inscrits_max=dictActivite["nbre_inscrits_max"])
                self.dictRenderers[index] = renderer
                self.SetItemCustomRenderer(index, 1, renderer)

                index += 1

                for dictGroupe in dictActivite["liste_groupes"] :

                    label = u" " + dictGroupe["nom"]
                    self.InsertStringItem(index, label)
                    self.SetItemPyData(index, dictGroupe)

                    # Colonne Gauge
                    renderer = Renderer_gauge(self)
                    renderer.SetValeurs(mode="groupe", nbre_inscrits=dictGroupe["nbre_inscrits"], nbre_inscrits_max=dictGroupe["nbre_inscrits_max"])
                    self.dictRenderers[index] = renderer
                    self.SetItemCustomRenderer(index, 1, renderer)

                    index += 1

        # Ajuste la taille des colonnes
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, ULC.ULC_AUTOSIZE_FILL)
        
        # Actualiser l'affichage pour éviter bug de positionnement
        try :
            self.DoLayout()
        except :
            pass

        self.Thaw()

    def SetFiltre(self, filtre=""):
        self.filtre = filtre
        self.MAJ(forcerActualisation=True)

    def Tests(self):
        """ UNIQUEMENT POUR TESTS : Test de mise à jour des gauges sur 50 """
        import random
        for index in range(0, self.GetItemCount()) :
            renderer = self.dictRenderers[index]
            nbrePlacesDispo = random.randint(0, 10)
            nbrePlacesPrises = random.randint(0, nbrePlacesDispo+1)
            nbrePlacesAttente = 0#random.randint(0, 1)
            renderer.SetValeurs(nbrePlacesPrises=nbrePlacesPrises, nbrePlacesDispo=nbrePlacesDispo, nbrePlacesAttente=nbrePlacesAttente)
            self.RefreshItem(index)
    




# ----------------------------------------------------------------------------------------------------------------------        

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Messages
        self.ctrl_inscriptions = CTRL(self)
        
        # Commandes
        self.bouton_parametres = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_parametres.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier les paramètres d'affichage")))
        self.bouton_outils = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux outils")))
        self.bouton_tarifs = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_tarifs.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour consulter les tarifs de l'activité sélectionnée (ou double-cliquez sur une activité dans la liste)")))

        # Barre de recherche
        self.ctrl_recherche = BarreRecherche(self, ctrl=self.ctrl_inscriptions)

        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonParametres, self.bouton_parametres)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTarifs, self.bouton_tarifs)

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_inscriptions, 1, wx.EXPAND|wx.TOP|wx.LEFT, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_parametres, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_tarifs, 0, 0, 0)
        grid_sizer.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 10)
        grid_sizer.Add(self.ctrl_recherche, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 10)
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        self.Layout()
    
    def MAJ(self):
        self.ctrl_inscriptions.MAJ()

    def OnBoutonParametres(self, event):
        from Dlg import DLG_Parametres_nbre_inscrits
        dlg = DLG_Parametres_nbre_inscrits.Dialog(self)
        reponse = dlg.ShowModal()
        if reponse == wx.ID_OK :
            self.ctrl_inscriptions.MAJ(forcerActualisation=True) 
        
    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Actualiser
        item = wx.MenuItem(menuPop, 10, _(u"Actualiser"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Actualiser, id=10)

        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, 20, _(u"Aide"), _(u"Aide"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Aide, id=20)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnBoutonTarifs(self, event=None):
        self.ctrl_inscriptions.OuvrirTarifs()

    def Actualiser(self, event):
        self.ctrl_inscriptions.MAJ(forcerActualisation=True) 
    
    def Aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, ctrl=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.ctrl = ctrl
        self.rechercheEnCours = False

        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)

        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

        # HACK pour avoir le EVT_CHAR
        for child in self.GetChildren():
            if isinstance(child, wx.TextCtrl):
                child.Bind(wx.EVT_CHAR, self.OnKeyDown)
                break

    def OnKeyDown(self, event):
        """ Efface tout si touche ECHAP """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE :
            self.OnCancel(None)
        event.Skip()

    def OnSearch(self, evt):
        self.Recherche()

    def OnCancel(self, evt):
        self.SetValue("")

    def OnDoSearch(self, evt):
        self.Recherche()

    def Recherche(self):
        filtre = self.GetValue()
        self.ShowCancelButton(len(filtre))
        self.ctrl.SetFiltre(filtre)
        self.Refresh()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        t1 = time.time()
        self.ctrl.MAJ()
        print("Temps MAJ =", time.time() - t1)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()