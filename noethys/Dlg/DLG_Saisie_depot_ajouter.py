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
import datetime

from Ol import OL_Reglements_depots

import GestionDB


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text



class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.dictNumeros = {}
        self.SetListeDonnees() 
        self.SetID(None)
    
    def SetListeDonnees(self):
        self.listeNoms = [_(u"Tous les comptes")]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero
        FROM comptes_bancaires 
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        for IDcompte, nom, numero in listeDonnees :
            self.listeNoms.append(nom)
            self.listeID.append(IDcompte)
            self.dictNumeros[IDcompte] = numero
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
    def GetNumero(self):
        IDcompte = self.GetID() 
        if IDcompte != None :
            return self.dictNumeros[IDcompte]
        else:
            return None

# ------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Modes(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.SetListeDonnees() 
        self.SetID(None)
    
    def SetListeDonnees(self):
        self.listeNoms = [_(u"Tous les modes")]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDmode, label
        FROM modes_reglements 
        ORDER BY label;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        for IDmode, nom in listeDonnees :
            self.listeNoms.append(nom)
            self.listeID.append(IDmode)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
# ------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, tracks=[], IDcompte=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_depot_ajouter", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.tracks= tracks
        self.IDcompte = IDcompte
        
        self.label_intro = wx.StaticText(self, -1, _(u"Double-cliquez sur un règlement pour l'affecter ou non au dépôt."), style=wx.ALIGN_CENTER)

        self.label_compte = wx.StaticText(self, -1, _(u"Compte :"))
        self.ctrl_compte = CTRL_Compte(self)
        self.ctrl_compte.SetMinSize((130, -1))
        self.ctrl_compte.SetID(self.IDcompte)

        self.label_mode = wx.StaticText(self, -1, _(u"Mode :"))
        self.ctrl_mode = CTRL_Modes(self)
        self.ctrl_mode.SetMinSize((130, -1))

        self.label_tri = wx.StaticText(self, -1, _(u"Tri :"))
        self.ctrl_tri = wx.Choice(self, -1, choices = (_(u"Ordre de saisie"), _(u"Date"), _(u"Mode de règlement"), _(u"Emetteur"), _(u"Numéro de pièce"), _(u"Nom de payeur"), "Montant"))
        self.ctrl_tri.Select(0) 
        
        self.label_ordre = wx.StaticText(self, -1, _(u"Ordre :"))
        self.ctrl_ordre = wx.Choice(self, -1, choices = (_(u"Ascendant"), _(u"Descendant")))
        self.ctrl_ordre.Select(0) 
        
        # Reglements disponibles
        self.staticbox_reglements_disponibles_staticbox = wx.StaticBox(self, -1, _(u"Règlements disponibles"))
##        self.ctrl_reglements_disponibles = OL_Reglements_depots.ListView(self, id=-1, inclus=False, name="OL_reglements_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listviewAvecFooter1 = OL_Reglements_depots.ListviewAvecFooter(self, kwargs={"inclus" : False}) 
        self.ctrl_reglements_disponibles = self.listviewAvecFooter1.GetListview()

        # Commandes
        self.bouton_bas_tout = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_double_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut_rouge.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_haut_tout = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_double_haut_rouge.png"), wx.BITMAP_TYPE_ANY))

        # Reglements du dépôt
        self.staticbox_reglements_depot_staticbox = wx.StaticBox(self, -1, _(u"Règlements du dépôt"))
##        self.ctrl_reglements_depot = OL_Reglements_depots.ListView(self, id=-1, inclus=True, name="OL_reglements_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listviewAvecFooter2 = OL_Reglements_depots.ListviewAvecFooter(self, kwargs={"inclus" : True}) 
        self.ctrl_reglements_depot = self.listviewAvecFooter2.GetListview()

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBasTout, self.bouton_bas_tout)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBas, self.bouton_bas)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHaut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHautTout, self.bouton_haut_tout)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoixCompte, self.ctrl_compte)
        self.Bind(wx.EVT_CHOICE, self.OnChoixMode, self.ctrl_mode)
        self.Bind(wx.EVT_CHOICE, self.OnChoixTri, self.ctrl_tri)
        self.Bind(wx.EVT_CHOICE, self.OnChoixOrdre, self.ctrl_ordre)
        
        # Initialisation des contrôles
        self.OnChoixTri(None)
        self.OnChoixOrdre(None)
        self.MAJListes(tracks=self.tracks) 
        

    def __set_properties(self):
        self.SetTitle(_(u"Ajouter ou retirer des règlements"))
        self.ctrl_compte.SetToolTipString(_(u"Sélectionnez un filtre de compte"))
        self.ctrl_mode.SetToolTipString(_(u"Sélectionnez un filtre de mode de règlement"))
        self.ctrl_tri.SetToolTipString(_(u"Sélectionnez le critère de tri"))
        self.ctrl_ordre.SetToolTipString(_(u"Sélectionnez l'ordre de tri"))
        self.bouton_bas_tout.SetToolTipString(_(u"Cliquez ici pour ajouter tous les règlements dans le dépôt"))
        self.bouton_bas.SetToolTipString(_(u"Cliquez ici pour ajouter le règlement disponible selectionné dans le dépôt"))
        self.bouton_bas_tout.SetMinSize((80, -1))
        self.bouton_bas.SetMinSize((150, -1))
        self.bouton_haut.SetMinSize((150, -1))
        self.bouton_haut_tout.SetMinSize((80, -1))
        self.bouton_haut.SetToolTipString(_(u"Cliquez ici pour retirer le règlement sélectionné du dépôt"))
        self.bouton_haut_tout.SetToolTipString(_(u"Cliquez ici pour retirer tous les règlements du dépôt"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((910, 710))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Intro
        grid_sizer_intro = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_intro.Add(self.label_intro, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 0)
        grid_sizer_intro.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_intro, 1, wx.ALL|wx.EXPAND, 10)
        
        # Règlements disponibles
        staticbox_reglements_disponibles = wx.StaticBoxSizer(self.staticbox_reglements_disponibles_staticbox, wx.VERTICAL)
        grid_sizer_dispo = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=13, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_compte, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_compte, 0, wx.EXPAND, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_mode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_mode, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_tri, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_tri, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_ordre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_ordre, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_dispo.Add(grid_sizer_options, 0, wx.EXPAND, 0)
        
        grid_sizer_dispo.Add(self.listviewAvecFooter1, 0, wx.EXPAND, 0)
        
        grid_sizer_dispo.AddGrowableRow(1)
        grid_sizer_dispo.AddGrowableCol(0)
        staticbox_reglements_disponibles.Add(grid_sizer_dispo, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reglements_disponibles, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Commandes de transfert
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_bas_tout, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_haut_tout, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_commandes.AddGrowableCol(5)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Règlements déposés
        staticbox_reglements_depot = wx.StaticBoxSizer(self.staticbox_reglements_depot_staticbox, wx.VERTICAL)
        staticbox_reglements_depot.Add(self.listviewAvecFooter2, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reglements_depot, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def MAJListes(self, tracks=None, selectionTrack=None, nextTrack=None):
        if tracks != None :
            self.tracks = tracks
        # MAJ Liste règlements disponibles
        IDcompte = self.ctrl_compte.GetID() 
        IDmode = self.ctrl_mode.GetID() 
        self.ctrl_reglements_disponibles.MAJ(self.tracks, selectionTrack=selectionTrack, nextTrack=nextTrack, IDcompte=IDcompte, IDmode=IDmode) 
        self.staticbox_reglements_disponibles_staticbox.SetLabel(self.ctrl_reglements_disponibles.GetLabelListe(_(u"règlements disponibles")))
        # MAJ Liste règlements du dépôt
        self.ctrl_reglements_depot.MAJ(self.tracks, selectionTrack=selectionTrack, nextTrack=nextTrack) 
        self.staticbox_reglements_depot_staticbox.SetLabel(self.ctrl_reglements_depot.GetLabelListe(_(u"règlements dans ce dépôt")))
    
    def DeplacerTout(self, inclus=True):
        listeTracks = []
        for track in self.tracks :
            track.inclus = inclus
            listeTracks.append(track)
        self.MAJListes(listeTracks)
        
    def GetTracks(self):
        return self.tracks
    
    def OnChoixCompte(self, event):
        self.MAJListes()
        
    def OnChoixMode(self, event):
        self.MAJListes()
        
    def OnChoixTri(self, event):
        selection = self.ctrl_tri.GetSelection() 
        self.ctrl_reglements_disponibles.numColonneTri = selection
        #self.ctrl_reglements_depot.numColonneTri = selection
        self.MAJListes()

    def OnChoixOrdre(self, event):
        selection = self.ctrl_ordre.GetSelection() 
        self.ctrl_reglements_disponibles.ordreAscendant = selection
        #self.ctrl_reglements_depot.ordreAscendant = selection
        self.MAJListes()

    def OnBoutonBas(self, event): 
        self.ctrl_reglements_disponibles.Deplacer()

    def OnBoutonHaut(self, event):
        self.ctrl_reglements_depot.Deplacer()

    def OnBoutonBasTout(self, event): 
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment ajouter tous les règlements ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse ==  wx.ID_YES :
            self.DeplacerTout(inclus=True)

    def OnBoutonHautTout(self, event):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer tous les règlements ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse ==  wx.ID_YES :
            self.DeplacerTout(inclus=False)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Gestiondesdpts")

    def OnBoutonOk(self, event): 
        # Validation des règlements sélectionnés
        for track in self.tracks :
            if track.inclus == True :
                # Création d'un label pour ce règlement en cas de message à afficher
                label = _(u"Règlement ID%d du %s payé en %s par %s") % (track.IDreglement, DateEngFr(str(track.date)), track.nom_mode, track.nom_payeur)
                
                # Vérifie si pas de règlement en attente
                if track.encaissement_attente == True :
                    dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné le règlement suivant alors qu'il a été saisi avec l'option 'Encaissement en attente' :\n\n> %s\n\nIl vous est donc impossible de l'inclure dans ce dépôt !") % label, _(u"Règlement en attente"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                    
                # Vérifie si règlement différé
                if track.date_differe != None :
                    if track.date_differe > datetime.date.today() :
                        dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné le règlement suivant alors qu'il comporte une date d'encaissement différé supérieure à la date du jour :\n\n> %s\n\nSouhaitez-vous tout de même l'inclure dans ce dépôt ?") % label, _(u"Attention !"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                        reponse = dlg.ShowModal()
                        dlg.Destroy()
                        if reponse !=  wx.ID_YES :
                            return False
        
        # Fermeture
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
