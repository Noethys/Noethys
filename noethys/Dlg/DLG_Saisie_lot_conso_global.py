#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date

import GestionDB
from Ol import OL_Saisie_lot_conso_global
import DLG_Saisie_lot_conso
from Utils import UTILS_Identification
from Utils import UTILS_Dates
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import DLG_Badgeage_grille
from threading import Thread 
import time



def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None :
        return None
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats


class Abort(Exception): 
    pass 

class Traitement(Thread): 
    def __init__(self, parent, IDactivite=None, dictAction={}, tracks=[]): 
        Thread.__init__(self) 
        self.parent = parent
        self.IDactivite = IDactivite
        self.dictAction = dictAction
        self.tracks = tracks
        self.succes = False
        self.stop = False 
        self.index = 0
        self.parent.ctrl_gauge.SetRange(len(self.tracks))
        self.parent.ctrl_gauge.SetValue(0)

    def run(self): 
        try: 
            
            listeAnomalies = []
            for track in self.tracks :
                
                # Affichage
                texte = u"[%d/%d] %s..." % (self.index+1, len(self.tracks), track.nomCompletIndividu)
                self.parent.EcritLog(texte) 
                self.parent.ctrl_gauge.SetValue(self.index+1)
                
                # Initialisation de la grille
                self.parent.ctrl_grille.InitGrille(IDindividu=track.IDindividu, IDfamille=track.IDfamille, IDactivite=self.IDactivite, periode=(self.dictAction["date_debut"], self.dictAction["date_fin"]))
                time.sleep(0.2)
                grille = self.parent.ctrl_grille.grille
                
                # Application du traitement par lot
                journal = self.parent.ctrl_grille.TraitementLot_processus(resultats=self.dictAction) 
                time.sleep(0.2)

                # Affichage du journal d'erreur
                if journal.has_key(track.IDindividu) :
                    nbreErreurs = len(journal[track.IDindividu])
                else :
                    nbreErreurs = 0
                if nbreErreurs > 0 :
                    for date, nomUnite, erreur in journal[track.IDindividu] :
                        self.parent.EcritLog(u"Erreur sur %s du %s : %s" % (nomUnite, UTILS_Dates.DateDDEnFr(date), erreur))
                    self.parent.SetStatutTrack(track, "erreur")
                
                # Sauvegarde de la grille des conso
                self.parent.ctrl_grille.Sauvegarde()
                if nbreErreurs == 0 :
                    self.parent.SetStatutTrack(track, "ok")

                # Arrête le traitement si bouton arrêter enfoncé
                if self.stop: 
                    raise Abort
                
                time.sleep(0.2)
                self.index += 1
            
            # Si fin 
            self.succes = True
            raise Abort
        
        except Abort, KeyBoardInterrupt: 
            if self.succes == True :
                self.parent.EcritLog(_(u"Traitement terminé")) 
                self.parent.Arreter(forcer=True) 

            self.parent.bouton_ok.SetImageEtTexte(cheminImage="Images/32x32/Valider.png", texte=u"Commencer")
            self.parent.bouton_fermer.Enable(True)
            self.parent.Layout()
            
        except Exception, err : 
            self.parent.EcritLog("Erreur : " + str(err))
            self.stop = True 
            self.parent.bouton_ok.SetImageEtTexte(cheminImage="Images/32x32/Valider.png", texte=u"Commencer")
            self.parent.bouton_fermer.Enable(True)
            self.parent.Layout()
            raise 
        
    def abort(self): 
        self.stop = True


# ----------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDactivite, nom, abrege in listeDonnees :
            if nom == None : nom = u"Activité inconnue"
            self.dictDonnees[index] = {"ID" : IDactivite, "nom" : nom, "abrege" : abrege}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfos(self):
        """ Récupère les infos sur le compte sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.dictAction = None

        # Bandeau
        titre = _(u"Traitement par lot")
        intro = _(u"Vous pouvez ici saisir, modifier ou supprimer des consommations pour un ensemble d'individus. Sélectionnez une activité ainsi que les paramètres de l'action à appliquer. Cochez les individus souhaités puis cliquez sur le bouton Commencer pour lancer le traitement.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_modifier.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.label_activite = wx.StaticText(self, -1, u"Activité :")
        self.ctrl_activite = CTRL_Activite(self)
        self.label_action = wx.StaticText(self, -1, u"Action :")
        self.ctrl_action = wx.TextCtrl(self, -1, u"")
        self.ctrl_action.Enable(False)
        self.bouton_action = wx.Button(self, -1, _(u"Sélectionner une action"))
        
        # Individus
        self.box_individus_staticbox = wx.StaticBox(self, -1, _(u"Sélection des individus"))
        self.listviewAvecFooter = OL_Saisie_lot_conso_global.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_individus = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Saisie_lot_conso_global.CTRL_Outils(self, listview=self.ctrl_individus, afficherCocher=True)

        # Grille des action
        self.box_grille_staticbox = wx.StaticBox(self, -1, _(u"Journal"))
        self.ctrl_log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.ctrl_log.SetMinSize((-1, 60))
        self.ctrl_gauge = wx.Gauge(self, -1, style=wx.GA_SMOOTH)
        self.ctrl_grille = DLG_Badgeage_grille.CTRL(self)
        self.ctrl_grille.Show(False)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Commencer"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAction, self.bouton_action)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        self.OnChoixActivite(None)
        self.ctrl_individus.MAJ() 
        wx.CallLater(0, self.Layout)

    def __set_properties(self):
        self.ctrl_activite.SetToolTipString(_(u"Sélectionnez l'activité pour laquelle vous souhaitez recalculer les prestations"))
        self.bouton_action.SetToolTipString(_(u"Cliquez ici pour sélectionner les paramètres des actions"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((750, 750))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_parametres.Add(self.label_activite, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_parametres.Add(self.ctrl_activite, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(1)

        grid_sizer_parametres.Add(self.label_action, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        
        grid_sizer_action = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_action.Add(self.ctrl_action, 1, wx.EXPAND, 0)
        grid_sizer_action.Add(self.bouton_action, 1, wx.EXPAND, 0)
        grid_sizer_action.AddGrowableCol(0)
        grid_sizer_parametres.Add(grid_sizer_action, 1, wx.EXPAND, 0)
        
        box_parametres.Add(grid_sizer_parametres, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_contenu.Add(box_parametres, 1, wx.EXPAND, 0)
        
        # Individus
        box_individus = wx.StaticBoxSizer(self.box_individus_staticbox, wx.VERTICAL)
        grid_sizer_individus = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        grid_sizer_individus.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        grid_sizer_individus.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_individus.AddGrowableCol(0)
        grid_sizer_individus.AddGrowableRow(0)
        box_individus.Add(grid_sizer_individus, 1, wx.EXPAND | wx.ALL, 10)
        
        grid_sizer_contenu.Add(box_individus, 1, wx.EXPAND, 0)

        # Grille des action
        box_grille = wx.StaticBoxSizer(self.box_grille_staticbox, wx.VERTICAL)
        grid_sizer_grille = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_grille.Add(self.ctrl_log, 1, wx.EXPAND, 0)
        grid_sizer_grille.Add(self.ctrl_gauge, 1, wx.EXPAND, 0)
        grid_sizer_grille.Add(self.ctrl_grille, 1, wx.EXPAND, 0)
        grid_sizer_grille.AddGrowableRow(0)
        grid_sizer_grille.AddGrowableCol(0)
        
        box_grille.Add(grid_sizer_grille, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_grille, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(0)

        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
    def OnChoixActivite(self, event=None):
        IDactivite = self.ctrl_activite.GetID() 
        
        # Reinit du dictAction
        if self.ctrl_individus.IDactivite != IDactivite :
            self.dictAction = None
            self.ctrl_action.SetValue("")
        if IDactivite != None :
            self.bouton_action.Enable(True)
        else :
            self.bouton_action.Enable(False)
            
        # Actualisation de la liste des individus
        self.ctrl_individus.SetActivite(IDactivite)
        self.ctrl_individus.SetAction(None)
        self.ctrl_individus.MAJ() 
    
    def OnBoutonAction(self, event):
        IDactivite = self.ctrl_activite.GetID() 
        dlg = DLG_Saisie_lot_conso.Dialog(self, listeIndividus=[], date_debut=None, date_fin=None, IDactivite=IDactivite, mode_parametres=True)
        dlg.SetValeursDefaut(self.dictAction)
        if dlg.ShowModal() == wx.ID_OK :
            self.dictAction = dlg.GetResultats()
            self.ctrl_action.SetValue(self.dictAction["description"])

            # Actualisation de la liste des individus
            self.ctrl_individus.SetAction(self.dictAction)
            self.ctrl_individus.MAJ()

        dlg.Destroy()
    
    def SetActivite(self, IDactivite=None):
        self.ctrl_activite.SetID(IDactivite)
        self.OnChoixActivite(None) 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        if self.Arreter() == True :
            return
        self.EndModal(wx.ID_CANCEL)        

    def EcritLog(self, texte="", saut=True):
        if saut == True and len(self.ctrl_log.GetValue()) > 0 :
            texte = u"\n" + texte
        try :
            self.ctrl_log.AppendText(texte)
        except :
            pass

    def SetStatutTrack(self, track=None, statut=None):
        track.statut = statut
        try :
            self.ctrl_individus.EnsureCellVisible(self.ctrl_individus.GetIndexOf(track)+1, 0)
        except :
            try :
                self.ctrl_individus.EnsureCellVisible(self.ctrl_individus.GetIndexOf(track), 0)
            except :
                pass

        self.ctrl_individus.RefreshObject(track)
        if statut == "ok" :
            self.ctrl_individus.Uncheck(track)
    
    def Arreter(self, forcer=False):
        try:
            TraitmentEnCours = self.traitement.isAlive()
        except AttributeError :
            TraitmentEnCours = False
            
        if TraitmentEnCours:
            if forcer == True :
                self.traitement.abort()
                return True
            else :
                # Demande la confirmation de l'arrêt
                dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment arrêter le traitement ?"), _(u"Confirmation d'arrêt"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                reponse = dlgConfirm.ShowModal()
                dlgConfirm.Destroy()
                if reponse == wx.ID_NO:
                    return True
                # Si le traitement est en cours, on le stoppe :
                self.traitement.abort()
                time.sleep(0.2)
                self.EcritLog(_(u"Vous avez interrompu le traitement."))
                return True

    def OnBoutonOk(self, event): 
        try:
            TraitmentEnCours = self.traitement.isAlive()
        except AttributeError :
            TraitmentEnCours = False
            
        if TraitmentEnCours:
            # Stopper traitement
            self.Arreter() 
        else :
            # Récupération des paramètres de sélection
            IDactivite = self.ctrl_activite.GetID()
            tracks = self.ctrl_individus.GetTracksCoches() 

            if IDactivite == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une activité dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if self.dictAction == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une action en cliquant sur le bouton 'Sélectionner une action' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if len(tracks) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un individu dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Demande confirmation de lancement
            dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous appliquer le traitement par lot pour les %d individus cochés ?\n\nLe processus peut prendre quelques minutes...") % len(tracks), _(u"Confirmation"), wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse != wx.ID_YES :
                return False
            
            # Lancer traitement
            self.EcritLog(_(u"Lancement du traitement"))
            self.bouton_ok.SetImageEtTexte(cheminImage="Images/32x32/Arreter.png", texte=u"Arrêter")
            self.bouton_fermer.Enable(False)
            self.Layout()
            
            # Traitement
            # Ajout de la liste des individus dans l'action sinon problème dans CTRL_Grille.TraitementLot_processus
            for track in tracks :
                self.dictAction["individus"].append(dict((key, value) for key, value in track.__dict__.iteritems() 
                                                         if not callable(value) and not key.startswith('__')))
            self.traitement = Traitement(self, IDactivite=IDactivite, dictAction=self.dictAction, tracks=tracks) 
            self.traitement.start()
        
        

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.SetActivite(1)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
