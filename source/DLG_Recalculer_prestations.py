#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import decimal

import CTRL_Bandeau
import CTRL_Saisie_date

import GestionDB
import OL_Recalculer_prestations
import UTILS_Identification

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import DLG_Badgeage_grille
from threading import Thread 
import time



class Abort(Exception): 
    pass 

class Traitement(Thread): 
    def __init__(self, parent, IDactivite=None, date_debut=None, date_fin=None, tracks=[]): 
        Thread.__init__(self) 
        self.parent = parent
        self.IDactivite = IDactivite
        self.date_debut = date_debut
        self.date_fin = date_fin
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
                self.parent.ctrl_grille.InitGrille(IDindividu=track.IDindividu, IDfamille=track.IDfamille, IDactivite=self.IDactivite, periode=(self.date_debut, self.date_fin))
                time.sleep(0.2)
                
                # Recalcul des prestations
                self.parent.ctrl_grille.RecalculerToutesPrestations() 
                time.sleep(0.2)
                
                # Sauvegarde de la grille des conso + Ecrit log
                self.parent.ctrl_grille.Sauvegarde()
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

        # Bandeau
        titre = _(u"Recalculer les prestations")
        intro = _(u"Vous pouvez ici recalculer le montant des prestations déduits des consommations pour un ensemble d'individus. Sélectionnez l'activité et la période à recalculer, cochez les individus souhaités puis cliquez sur le bouton Commencer pour lancer le traitement.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Prestations
        self.box_prestations_staticbox = wx.StaticBox(self, -1, _(u"Sélection des prestations"))
        self.label_periode = wx.StaticText(self, -1, u"Période :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, "au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.label_activite = wx.StaticText(self, -1, u"Activité :")
        self.ctrl_activite = CTRL_Activite(self)
        
        self.bouton_actualiser = wx.Button(self, -1, _(u"Actualiser la liste"))

        self.listviewAvecFooter = OL_Recalculer_prestations.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_individus = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Recalculer_prestations.CTRL_Outils(self, listview=self.ctrl_individus, afficherCocher=True)

        # Grille des conso
        self.box_grille_staticbox = wx.StaticBox(self, -1, _(u"Journal"))
        self.ctrl_log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.ctrl_log.SetMinSize((-1, 80))
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
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        self.ctrl_individus.MAJ() 
        wx.CallLater(0, self.Layout)

    def __set_properties(self):
        self.ctrl_activite.SetToolTipString(_(u"Sélectionnez l'activité pour laquelle vous souhaitez recalculer les prestations"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez une date de début"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez une date de fin"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser la liste"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((720, 800))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Prestations
        box_prestations = wx.StaticBoxSizer(self.box_prestations_staticbox, wx.VERTICAL)
        grid_sizer_prestations = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Paramètres
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)

        grid_sizer_parametres.Add(self.label_activite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_activite, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(1)
        
        grid_sizer_parametres.Add(self.label_periode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add((10, 10), 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_actualiser, 1, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableCol(4)
        grid_sizer_parametres.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        
        grid_sizer_prestations.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        
        # Liste individus
        grid_sizer_prestations.Add(self.listviewAvecFooter, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_prestations.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_prestations.AddGrowableRow(1)
        grid_sizer_prestations.AddGrowableCol(0)
        box_prestations.Add(grid_sizer_prestations, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.Add(box_prestations, 1, wx.EXPAND, 0)

        # Grille des conso
        box_grille = wx.StaticBoxSizer(self.box_grille_staticbox, wx.VERTICAL)
        grid_sizer_grille = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_grille.Add(self.ctrl_log, 1, wx.EXPAND, 0)
        grid_sizer_grille.Add(self.ctrl_gauge, 1, wx.EXPAND, 0)
        grid_sizer_grille.Add(self.ctrl_grille, 1, wx.EXPAND, 0)
        grid_sizer_grille.AddGrowableRow(0)
        grid_sizer_grille.AddGrowableCol(0)
        
        box_grille.Add(grid_sizer_grille, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_grille, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
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
        self.ctrl_individus.SetActivite(IDactivite)
        self.ctrl_individus.MAJ() 

    def OnBoutonActualiser(self, event): 
        IDactivite = self.ctrl_activite.GetID()
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_activite.SetFocus() 
            return False

        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus() 
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus() 
            return False
        
        self.ctrl_individus.SetPeriode(date_debut, date_fin)
        self.ctrl_individus.SetActivite(IDactivite)
        self.ctrl_individus.MAJ() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
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
            date_debut = self.ctrl_date_debut.GetDate()
            date_fin = self.ctrl_date_fin.GetDate()
            tracks = self.ctrl_individus.GetTracksCoches() 

            if len(tracks) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un individu dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Demande confirmation de lancement
            dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous lancer le recalcul des prestations pour les %d individus sélectionnés ?\n\nLe traitement peut prendre quelques minutes...") % len(tracks), _(u"Confirmation"), wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
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
            self.traitement = Traitement(self, IDactivite=IDactivite, date_debut=date_debut, date_fin=date_fin, tracks=tracks) 
            self.traitement.start()
        
        

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ctrl_date_debut.SetDate(datetime.date(2015, 1, 1))
    dlg.ctrl_date_fin.SetDate(datetime.date(2015, 06, 30))
    dlg.ctrl_activite.SetID(1)
    dlg.OnBoutonActualiser(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
