#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime

import GestionDB
import CTRL_Bandeau
import OL_Transports
import UTILS_Dates
import operator





class CTRL_Filtre(wx.Choice):
    def __init__(self, parent, listeDonnees=[], labelDefaut=_(u"Tous")):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeDonnees = listeDonnees
        self.labelDefaut = labelDefaut
        self.MAJ() 
        self.Bind(wx.EVT_CHOICE, self.parent.OnChoixFiltre)
    
    def MAJ(self):
        listeLabels = [self.labelDefaut,]
        for ID, label in self.listeDonnees :
            listeLabels.append(label)
        if len(listeLabels) == 1 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeLabels)
        self.SetSelection(0)

    def GetID(self):
        index = self.GetSelection()
        if index == 0 : return None
        return self.listeDonnees[index-1][0]
    
    def GetLabel(self):
        return self.GetStringSelection() 
    
    def SetDonnees(self, listeDonnees=[]):
        self.listeDonnees = listeDonnees
        self.MAJ() 



class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        
        self.box_liste_staticbox = wx.StaticBox(self, -1, _(u"Liste des transports"))

        # Filtres
        self.box_filtres_staticbox = wx.StaticBox(self, -1, _(u"Filtres"))
        
        self.label_individu = wx.StaticText(self, -1, _(u"Individu :"))
        self.ctrl_individu = CTRL_Filtre(self, labelDefaut=_(u"Tous les individus"))
        
        self.label_depart = wx.StaticText(self, -1, _(u"Départ :"))
        self.ctrl_depart_date = CTRL_Filtre(self, labelDefaut=_(u"Toutes les dates"))
        self.ctrl_depart_heure = CTRL_Filtre(self, labelDefaut=_(u"Tous les horaires"))
        self.ctrl_depart_lieu = CTRL_Filtre(self, labelDefaut=_(u"Tous les lieux"))

        self.label_transport = wx.StaticText(self, -1, _(u"Transport :"))
        self.ctrl_transport = CTRL_Filtre(self, labelDefaut=_(u"Tous les transports"))

        self.label_arrivee = wx.StaticText(self, -1, _(u"Arrivée :"))
        self.ctrl_arrivee_date = CTRL_Filtre(self, labelDefaut=_(u"Toutes les dates"))
        self.ctrl_arrivee_heure = CTRL_Filtre(self, labelDefaut=_(u"Tous les horaires"))
        self.ctrl_arrivee_lieu = CTRL_Filtre(self, labelDefaut=_(u"Tous les lieux"))
        
        # Liste
        self.ctrl_liste = OL_Transports.ListView(self,id=-1, name="OL_liste_transports", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_liste.SetMinSize((150, 20))

        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))

        self.ctrl_recherche = OL_Transports.CTRL_Outils(self, listview=self.ctrl_liste, afficherCocher=True)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportTexte, self.bouton_export_texte)
        
        # Init contrôles
        self.MAJ() 
        
    def __set_properties(self):
        self.ctrl_individu.SetToolTipString(_(u"Filtrer par individu"))
        self.ctrl_depart_date.SetToolTipString(_(u"Filtrer par date de départ"))
        self.ctrl_depart_heure.SetToolTipString(_(u"Filtrer par heure de départ"))
        self.ctrl_depart_lieu.SetToolTipString(_(u"Filtrer par lieu de départ"))
        self.ctrl_arrivee_date.SetToolTipString(_(u"Filtrer par date d'arrivée"))
        self.ctrl_arrivee_heure.SetToolTipString(_(u"Filtrer par heure d'arrivée"))
        self.ctrl_arrivee_lieu.SetToolTipString(_(u"Filtrer par lieu d'arrivée"))
        self.bouton_modifier.SetToolTipString(_(u"Modifier le transport sélectionné dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Supprimer le transport sélectionné dans la liste"))
        self.bouton_apercu.SetToolTipString(_(u"Afficher un aperçu avant impression de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Imprimer la liste"))
        self.bouton_export_excel.SetToolTipString(_(u"Exporter la liste au format Excel"))
        self.bouton_export_texte.SetToolTipString(_(u"Exporter la liste au format Texte"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        # Filtres
        box_filtres = wx.StaticBoxSizer(self.box_filtres_staticbox, wx.VERTICAL)
        grid_sizer_filtres = wx.FlexGridSizer(2, 7, 5, 5)
        
        grid_sizer_filtres.Add(self.label_individu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_individu, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.label_depart, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_depart_date, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.ctrl_depart_heure, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.ctrl_depart_lieu, 0, wx.EXPAND, 0)
        
        grid_sizer_filtres.Add(self.label_transport, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_transport, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.label_arrivee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_arrivee_date, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.ctrl_arrivee_heure, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.ctrl_arrivee_lieu, 0, wx.EXPAND, 0)

        box_filtres.Add(grid_sizer_filtres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_filtres, 1, wx.EXPAND, 0)
        
        # Liste
        box_liste = wx.StaticBoxSizer(self.box_liste_staticbox, wx.VERTICAL)
        grid_sizer_liste = wx.FlexGridSizer(2, 2, 5, 5)
        grid_sizer_liste.Add(self.ctrl_liste, 1, wx.EXPAND, 0)
        grid_sizer_boutons_liste = wx.FlexGridSizer(12, 1, 5, 5)
        grid_sizer_boutons_liste.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons_liste.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_liste.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons_liste.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_liste.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_liste.Add(grid_sizer_boutons_liste, 1, wx.EXPAND, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_liste.Add(grid_sizer_options, 1, wx.EXPAND, 10)

        grid_sizer_liste.AddGrowableRow(0)
        grid_sizer_liste.AddGrowableCol(0)
        box_liste.Add(grid_sizer_liste, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_liste, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
    
    def MAJ(self):
        self.ctrl_liste.MAJ() 
        
        listeIndividu = []
        listeTransport = []
        listeDepartDate = []
        listeDepartHeure = []
        listeDepartLieu = []
        listeArriveeDate = []
        listeArriveeHeure = []
        listeArriveeLieu = []
        
        for track in self.ctrl_liste :
            
            if track.IDindividu != None :
                individu = (track.IDindividu, track.individu_nom_complet)
                if individu not in listeIndividu : listeIndividu.append(individu)
            
            if track.categorie != None :
                transport = (track.categorie, track.labelTransport)
                if transport not in listeTransport : listeTransport.append(transport)
            
            if track.depart_dateDD != None :
                depart_date = (track.depart_dateDD, UTILS_Dates.DateEngFr(str(track.depart_dateDD)))
                if depart_date not in listeDepartDate : listeDepartDate.append(depart_date)
            
            if track.depart_heure != None :
                depart_heure = (track.depart_heure, track.depart_heure)
                if depart_heure not in listeDepartHeure : listeDepartHeure.append(depart_heure)
            
            if track.depart_nom != None :
                depart_lieu = (track.depart_nom, track.depart_nom)
                if depart_lieu not in listeDepartLieu : listeDepartLieu.append(depart_lieu)
            
            if track.arrivee_dateDD != None :
                arrivee_date = (track.arrivee_dateDD, UTILS_Dates.DateEngFr(str(track.arrivee_dateDD)))
                if arrivee_date not in listeArriveeDate : listeArriveeDate.append(arrivee_date)
            
            if track.arrivee_heure != None :
                arrivee_heure = (track.arrivee_heure, track.arrivee_heure)
                if arrivee_heure not in listeArriveeHeure : listeArriveeHeure.append(arrivee_heure)
            
            if track.arrivee_nom != None :
                arrivee_lieu = (track.arrivee_nom, track.arrivee_nom)
                if arrivee_lieu not in listeArriveeLieu : listeArriveeLieu.append(arrivee_lieu)
        
        listeIndividu = sorted(listeIndividu, key=operator.itemgetter(1))
        listeTransport = sorted(listeTransport, key=operator.itemgetter(1))
        listeDepartDate = sorted(listeDepartDate, key=operator.itemgetter(0))
        listeDepartHeure = sorted(listeDepartHeure, key=operator.itemgetter(0))
        listeDepartLieu = sorted(listeDepartLieu, key=operator.itemgetter(1))
        listeArriveeDate = sorted(listeArriveeDate, key=operator.itemgetter(0))
        listeArriveeHeure = sorted(listeArriveeHeure, key=operator.itemgetter(0))
        listeArriveeLieu = sorted(listeArriveeLieu, key=operator.itemgetter(1))
        
        # MAJ des contrôles
        self.ctrl_individu.SetDonnees(listeIndividu) 
        self.ctrl_transport.SetDonnees(listeTransport) 
        self.ctrl_depart_date.SetDonnees(listeDepartDate) 
        self.ctrl_depart_heure.SetDonnees(listeDepartHeure) 
        self.ctrl_depart_lieu.SetDonnees(listeDepartLieu) 
        self.ctrl_arrivee_date.SetDonnees(listeArriveeDate) 
        self.ctrl_arrivee_heure.SetDonnees(listeArriveeHeure) 
        self.ctrl_arrivee_lieu.SetDonnees(listeArriveeLieu) 


    def OnChoixFiltre(self, event): 
        individu = self.ctrl_individu.GetID()
        transport = self.ctrl_transport.GetID()
        depart_date = self.ctrl_depart_date.GetID()
        depart_heure = self.ctrl_depart_heure.GetID()
        depart_lieu = self.ctrl_depart_lieu.GetID()
        arrivee_date = self.ctrl_arrivee_date.GetID()
        arrivee_heure = self.ctrl_arrivee_heure.GetID()
        arrivee_lieu = self.ctrl_arrivee_lieu.GetID()
        
        dictFiltres = {}
        if individu != None : dictFiltres["individu"] = individu
        if transport != None : dictFiltres["transport"] = transport
        if depart_date != None : dictFiltres["depart_date"] = depart_date
        if depart_heure != None : dictFiltres["depart_heure"] = depart_heure
        if depart_lieu != None : dictFiltres["depart_lieu"] = depart_lieu
        if arrivee_date != None : dictFiltres["arrivee_date"] = arrivee_date
        if arrivee_heure != None : dictFiltres["arrivee_heure"] = arrivee_heure
        if arrivee_lieu != None : dictFiltres["arrivee_lieu"] = arrivee_lieu
        self.ctrl_liste.SetFiltres(dictFiltres)
        
    def OnBoutonModifier(self, event): 
        self.ctrl_liste.Modifier(None) 

    def OnBoutonSupprimer(self, event): 
        self.ctrl_liste.Supprimer(None) 

    def OnBoutonApercu(self, event): 
        self.ctrl_liste.Apercu(None) 

    def OnBoutonImprimer(self, event):
        self.ctrl_liste.Imprimer(None) 

    def OnBoutonExportTexte(self, event): 
        self.ctrl_liste.ExportTexte(None) 

    def OnBoutonExportExcel(self, event): 
        self.ctrl_liste.ExportExcel(None) 




    


# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Utilisez les filtres pour afficher les transports souhaités et imprimer ou exportez la liste affichée.")
        titre = _(u"Liste détaillée des transports")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        self.panel = Panel(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((830, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.panel, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
                
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedestransports")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
