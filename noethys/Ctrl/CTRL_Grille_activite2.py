#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image

if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC

import sys

import GestionDB


LARGEUR_COLONNE_ACTIVITE = 140
LARGEUR_COLONNE_GROUPE = 80


class Choice_groupe(wx.Choice):
    def __init__(self, parent, IDactivite=None, IDindividu=None, listeGroupes=[], IDdefaut=None):
        """ typeIndividu = "A" ou "E" (adulte ou enfant) """
        """ sexeIndividu = "M" ou "F" (masculin ou féminin) """
        """ Lien = ID type lien par défaut """
        wx.Choice.__init__(self, parent, id=-1, size=(LARGEUR_COLONNE_GROUPE-2, -1)) 
        self.parent = parent

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.IDactivite = IDactivite
        self.IDindividu = IDindividu
        self.listeGroupes = listeGroupes
        self.IDdefaut = IDdefaut
        self.MAJ()
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.SetToolTip(wx.ToolTip(
u"""Le groupe par défaut est signalé par une *.\n 
Vous pouvez sélectionner ponctuellement 
un autre groupe dans la liste. Le groupe par 
défaut n'en sera pas pour autant modifié."""))
        
    def MAJ(self):
        index = 0
        for ordreGroupe, nomGroupe, IDgroupe in self.listeGroupes :
            if self.IDdefaut == IDgroupe :
                self.Append(nomGroupe + "*", IDgroupe)
                self.SetSelection(index)
            else:
                self.Append(nomGroupe, IDgroupe)
            index += 1
                            
    def OnChoice(self, event):
        """ Met à jour la grille """
        self.parent.GetGrandParent().panel_grille.grille.MAJ() 
    
    def GetIDgroupe(self):
        if self.GetSelection() == -1 :
            return None
        else:
            return self.listeGroupes[self.GetSelection()][2]
    
    def SetIDgroupe(self, IDgroupe=None):
        index = 0
        for ordreGroupe, nomGroupe, IDgroupeTemp in self.listeGroupes :
            if IDgroupeTemp == IDgroupe :
                self.SetSelection(index)
                return
            index += 1
                


class CTRL_Activites(ULC.UltimateListCtrl):
    def __init__(self, parent, dictIndividus={}, dictActivites={}, dictGroupes={}, listeSelectionIndividus=[]):
        ULC.UltimateListCtrl.__init__(self, parent, -1, agwStyle=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES| ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.parent = parent

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.dictIndividus = dictIndividus
        self.dictActivites = dictActivites 
        self.dictGroupes = dictGroupes
        self.listeSelectionIndividus = listeSelectionIndividus
        self.listeActivites = []
        self.dictControles = {}
        self.dictInscriptions = {}
        # Binds
        self.Bind(ULC.EVT_LIST_ITEM_CHECKED, self.OnCheck)
        # Commandes
##        self.MAJ()
        
    def MAJ(self):
        self.ClearAll()
        self.listeActivites = self.Importation()
        self.Remplissage()
        self.MAJaffichage() 
##        self.CocheTout()
        
    def SetListeSelectionIndividus(self, listeSelectionIndividus):
        self.listeSelectionIndividus = listeSelectionIndividus
        self.MAJ() 
        try :
            listeSelections = self.GetIDcoches()
            self.GetGrandParent().SetListeSelectionActivites(listeSelections)
        except :
            print "Erreur dans le SetListeSelectionIndividus du ultimatelistctrl."
    
    def Importation(self, listeIDindividus=[]):
        # Récupération des activités
        listeActivites = []
        for IDindividu, dictIndividu in self.dictIndividus.iteritems() :
            if IDindividu in self.listeSelectionIndividus :
                listeInscriptions = dictIndividu["inscriptions"]
                for dictInscription in listeInscriptions :
                    IDactivite = dictInscription["IDactivite"]
                    nomActivite = self.dictActivites[IDactivite]["nom"]
                    if (nomActivite, IDactivite) not in listeActivites :
                        listeActivites.append((nomActivite, IDactivite))
        listeActivites.sort()
        return listeActivites

    def Remplissage(self):
        listeNomsIndividus = self.GetListeIndividus() 
        self.dictInscriptions = self.GetDictInscriptions()
        
        # Création des colonnes
        self.InsertColumn(0, u"", width=LARGEUR_COLONNE_ACTIVITE)
        indexCol = 1
        for nomIndividu, IDindividu in listeNomsIndividus :
            self.InsertColumn(indexCol, nomIndividu, width=LARGEUR_COLONNE_GROUPE, format=ULC.ULC_FORMAT_CENTRE)
            indexCol +=1
        
        # Format : (nomItem, date_debut, date_fin)
        listeItems = []
        index = 0
        for nom, IDactivite in self.listeActivites :
            # Ecrit le nom de l'activité
            self.InsertStringItem(index, nom, it_kind=1)
            self.SetItemPyData(index, IDactivite)
            # Ecrit le wx.Choice pour chaque individu
            indexCol = 1
            for nomIndividu, IDindividu in listeNomsIndividus :
                listeGroupes = self.GetListeGroupes(IDactivite)
                if IDindividu in self.dictInscriptions[IDactivite] :
                    if len(listeGroupes) > 0 :
                        IDdefaut = self.GetGroupeDefautIndividu(IDactivite, IDindividu)
                        item = self.GetItem(index, indexCol)
                        choice = Choice_groupe(self, IDactivite, IDindividu, listeGroupes, IDdefaut)
                        self.dictControles[(IDactivite, IDindividu)] = choice
                        item.SetWindow(choice)
                        self.SetItem(item)
                    else:
                        self.SetStringItem(index, indexCol, label=_(u"Groupe unique"))
                else:
                    # Si pas d'inscription pour cette activite : Coloration de la case en gris
                    self.SetStringItem(index, indexCol, label=u"")
                    item = self.GetItem(index, indexCol)
                    item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
                    item.SetBackgroundColour(wx.Colour(220, 220, 220))
                    self.SetItem(item)
                    
                indexCol += 1
            index += 1
    
    def MAJaffichage(self):
        # Correction du bug d'affichage du ultimatelistctrl
        self.Layout() 
        self._mainWin.RecalculatePositions()
    
    def GetIDgroupe(self, IDactivite=None, IDindividu=None):
        """ Permet de récupérer l'IDgroupe de l'individu à partir de la grille """
        if self.dictControles.has_key((IDactivite, IDindividu)) :
            controle = self.dictControles[(IDactivite, IDindividu)]
            return controle.GetIDgroupe() 
        else:
            return None
    
    def GetListeGroupes(self, IDactivite=None):
        listeGroupes = []
        for IDgroupe, dictGroupe in self.dictGroupes.iteritems():
            if dictGroupe["IDactivite"] == IDactivite :
                listeGroupes.append( (dictGroupe["ordre"], dictGroupe["nom"], IDgroupe) )
        listeGroupes.sort() 
        return listeGroupes
    
    def GetListeIndividus(self):
        listeNomsIndividus = []
        for IDindividu, dictInfos in self.dictIndividus.iteritems() :
            if IDindividu in self.listeSelectionIndividus :
                if len(dictInfos["inscriptions"]) > 0  :
                    nomIndividu = dictInfos["prenom"]
                    listeNomsIndividus.append( (nomIndividu, IDindividu) )
        listeNomsIndividus.sort()
        return listeNomsIndividus
    
    def GetDictInscriptions(self):
        dictInscriptions = {}
        for IDindividu, dictInfos in self.dictIndividus.iteritems() :
            listeInscriptions = dictInfos["inscriptions"]
            for dictInscription in listeInscriptions :
                IDactivite = dictInscription["IDactivite"]
                if dictInscriptions.has_key(IDactivite) == False :
                    dictInscriptions[IDactivite] = []
                dictInscriptions[IDactivite].append(IDindividu)
        return dictInscriptions

    def GetGroupeDefautIndividu(self, IDactivite, IDindividu):
        for dictInscriptions in self.dictIndividus[IDindividu]["inscriptions"] :
            if dictInscriptions["IDactivite"] == IDactivite :
                return dictInscriptions["IDgroupe"]
        return None

    def OnCheck(self, event=None):
        """ Quand une sélection d'activités est effectuée... """
        listeSelections = self.GetIDcoches()
        try :
            self.GetGrandParent().SetListeSelectionActivites(listeSelections)
            self.GetGrandParent().MAJ_grille(autoCocheActivites=False)
        except :
            print "Erreur dans le Check du ultimatelistctrl.", listeSelections
        # Déselectionne l'item après la coche
        if event != None :
            itemIndex = event.m_itemIndex
            self.Select(itemIndex, False)

    def CocheTout(self):
        for index in range(0, len(self.listeActivites)):
            item = self.GetItem(index, 0)
            item.Check(True)
            self.SetItem(item)

    def GetIDcoches(self):
        listeIDcoches = []
        for index in range(0, len(self.listeActivites)):
            item = self.GetItem(index, 0)
            if item.IsChecked() :
                listeIDcoches.append(self.listeActivites[index][1])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        for index in range(0, len(self.listeActivites)):
            item = self.GetItem(index, 0)
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                item.Check(True)
    
    def CocheActivitesOuvertes(self, date_min=None, date_max=None):
        """ Coche uniquement les activités ouvertes """
        listeIDactivites = []
        for index in range(0, len(self.listeActivites)):
            item = self.GetItem(index, 0)
            IDactivite = self.listeActivites[index][1]
            date_debut_activite = self.dictActivites[IDactivite]["date_debut"]
            date_fin_activite = self.dictActivites[IDactivite]["date_fin"]
            if date_debut_activite <= date_max and date_fin_activite >= date_min :
                item.Check(True)
                listeIDactivites.append(IDactivite)
            else :
                item.Check(False)
            self.SetItem(item)
        return listeIDactivites
        
        
        
        
        
##class CTRL(wx.CheckListBox):
##    def __init__(self, parent, dictIndividus={}, dictActivites={}):
##        wx.CheckListBox.__init__(self, parent, -1)
##        self.parent = parent
##        self.data = []
##        self.dictIndividus = dictIndividus
##        self.dictActivites = dictActivites
##        self.SetToolTip(wx.ToolTip(_(u"Cochez les activités à afficher")))
##        self.listeActivites = []
##        # Binds
##        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
##        # Commandes
##        self.MAJ()
##
##    def MAJ(self):
##        self.listeActivites = self.Importation()
##        self.SetListeChoix()
##    
##    def Importation(self, listeIDindividus=[]):
##        # Récupération des activités
##        listeActivites = []
##        for IDindividu, dictIndividu in self.dictIndividus.iteritems() :
##            listeInscriptions = dictIndividu["inscriptions"]
##            for dictInscription in listeInscriptions :
##                IDactivite = dictInscription["IDactivite"]
##                nomActivite = self.dictActivites[IDactivite]["nom"]
##                if (nomActivite, IDactivite) not in listeActivites :
##                    listeActivites.append((nomActivite, IDactivite))
##        listeActivites.sort()
##        return listeActivites
##
##    def SetListeChoix(self):
##        # Format : (nomItem, date_debut, date_fin)
##        listeItems = []
##        index = 0
##        for nom, IDactivite in self.listeActivites :
##            self.Append(nom)
##            index += 1
##                            
##    def GetIDcoches(self):
##        listeIDcoches = []
##        NbreItems = len(self.listeActivites)
##        for index in range(0, NbreItems):
##            if self.IsChecked(index):
##                listeIDcoches.append(self.listeActivites[index][1])
##        return listeIDcoches
##    
##    def CocheTout(self):
##        index = 0
##        for index in range(0, len(self.listeActivites)):
##            self.Check(index)
##            index += 1
##
##    def SetIDcoches(self, listeIDcoches=[]):
##        index = 0
##        for index in range(0, len(self.listeActivites)):
##            ID = self.listeActivites[index][1]
##            if ID in listeIDcoches :
##                self.Check(index)
##            index += 1
##
##    def OnCheck(self, event):
##        """ Quand une sélection d'activités est effectuée... """
##        listeSelections = self.GetIDcoches()
##        try :
##            self.parent.SetListeSelectionActivites(listeSelections)
##            self.parent.MAJ_grille()
##        except :
##            print listeSelections

##class CTRL_Mode(wx.Panel):
##    def __init__(self, parent):
##        wx.Panel.__init__(self, parent, -1)
##        self.parent = parent
##        
##        self.label_mode = wx.StaticText(self, -1, _(u"Mode de saisie :"))
##        self.radio_reservation = wx.RadioButton(self, -1, _(u"Réservation"), style = wx.RB_GROUP )
##        self.radio_attente = wx.RadioButton(self, -1, _(u"Attente") )
##        self.radio_refus = wx.RadioButton(self, -1, _(u"Refus") )
##        self.radio_reservation.SetValue(True)
##        
##        self.radio_reservation.SetToolTip(wx.ToolTip(_(u"Le mode Réservation permet de saisir une réservation")))
##        self.radio_attente.SetToolTip(wx.ToolTip(_(u"Le mode Attente permet de saisir une place sur liste d'attente")))
##        self.radio_refus.SetToolTip(wx.ToolTip(_(u"Le mode de refus permet de saisir une place sur liste d'attente qui a été refusée par l'individu. Cette saisie est juste utilisée à titre statistique")))
##        
##        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
##        grid_sizer_base.Add(self.label_mode, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.radio_reservation, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.radio_attente, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.radio_refus, 0, wx.EXPAND, 0)
##        self.SetSizer(grid_sizer_base)
##        self.Layout()
##
##        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_reservation)
##        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_attente)
##        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_refus)
##    
##    def OnRadioMode(self, event):
##        pass
##    
##    def GetMode(self):
##        if self.radio_reservation.GetValue() == True : return "reservation"
##        if self.radio_attente.GetValue() == True : return "attente"
##        if self.radio_refus.GetValue() == True : return "refus"
        
        
        
        
class CTRL(wx.Panel):
    def __init__(self, parent, dictIndividus={}, dictActivites={}, dictGroupes={}, listeSelectionIndividus=[]):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        self.ctrl_activites = CTRL_Activites(self, dictIndividus, dictActivites, dictGroupes, listeSelectionIndividus)
##        self.ctrl_mode = CTRL_Mode(self)
        
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_activites, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.ctrl_mode, 0, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()


# --------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= CTRL(panel)
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


