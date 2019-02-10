#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ol import OL_Badgeage_log
from Dlg import DLG_Badgeage_interface
from Utils import UTILS_Vocal
import wx.lib.agw.hyperlink as Hyperlink
from Utils import UTILS_Parametres
from Dlg import DLG_Messagebox


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        if self.URL == "consommations" :
            from Dlg import DLG_Badgeage_consommations
            dlg = DLG_Badgeage_consommations.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()

        if self.URL == "historique" :
            from Dlg import DLG_Badgeage_journal
            dlg = DLG_Badgeage_journal.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()

        if self.URL == "purger" :
            self.parent.PurgerJournal() 
        
        self.UpdateLink()
        
        

class CTRL_Procedure(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(150, -1)) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        db = GestionDB.DB()
        req = """SELECT IDprocedure, nom, defaut
        FROM badgeage_procedures
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        indexDefaut = None
        for IDprocedure, nom, defaut in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDprocedure, "nom" : nom}
            listeItems.append(nom)
            if defaut == 1 :
                indexDefaut = index
            index += 1
        
        # Remplissage
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
        
        # Sélectionne le défaut
        if indexDefaut != None :
            self.Select(indexDefaut)


    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetNom(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["nom"]

# ---------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, mode_debug=False):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.mode_debug = mode_debug
        
        # Bandeau
        intro = _(u"Vous pouvez ici effectuer des procédures de badgeage. Commencez par sélectionner la procédure souhaitée dans la liste pour cliquez sur le bouton 'Ok' pour lancer la procédure. Vous pourrez interrompre celle-ci en appuyant sur CTRL+SHIFT+Q.")
        titre = _(u"Badgeage")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Badgeage.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        
        self.label_procedure = wx.StaticText(self, -1, _(u"Procédure :"))
        self.ctrl_procedure = CTRL_Procedure(self)
        self.bouton_procedures = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())
        
        self.check_dateauto = wx.CheckBox(self, -1, _(u"Date auto."))

        # Log
        self.box_log_staticbox = wx.StaticBox(self, -1, _(u"Journal"))
        
        self.ctrl_log = OL_Badgeage_log.ListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_VRULES)
        self.log = self.ctrl_log
        self.ctrl_log.SetMinSize((100, 100))
        self.ctrl_recherche = OL_Badgeage_log.CTRL_Outils(self, listview=self.ctrl_log)

        self.bouton_log_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_log_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_log_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_log_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Texte.png"), wx.BITMAP_TYPE_ANY))

        self.hyper_consommations = Hyperlien(self, label=_(u"Consulter la liste des consommations badgées"), infobulle=_(u"Cliquez ici pour consulter la liste des consommations badgées"), URL="consommations")
        self.label_separation1 = wx.StaticText(self, -1, u"|")
        self.hyper_journal = Hyperlien(self, label=_(u"Consulter l'historique du journal"), infobulle=_(u"Cliquez ici pour consulter l'historique du journal"), URL="historique")
        self.label_separation2 = wx.StaticText(self, -1, u"|")
        self.hyper_purger = Hyperlien(self, label=_(u"Purger l'historique"), infobulle=_(u"Cliquez ici pour purger l'historique du journal"), URL="purger")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_vocal = CTRL_Bouton_image.CTRL(self, texte=_(u"Synthèse vocale"), cheminImage="Images/32x32/Vocal.png")
        self.bouton_importation = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Commencer le badgeage"), cheminImage="Images/32x32/Badgeage.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixProcedure, self.ctrl_procedure)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDateauto, self.check_dateauto)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonProcedures, self.bouton_procedures)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLogApercu, self.bouton_log_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLogImprimer, self.bouton_log_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLogExcel, self.bouton_log_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLogTexte, self.bouton_log_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonVocal, self.bouton_vocal)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImportation, self.bouton_importation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
##        wx.CallAfter(self.AfficheAvertissement)
        
        
    def __set_properties(self):
        self.ctrl_procedure.SetToolTip(wx.ToolTip(_(u"Sélectionnez une procédure")))
        self.bouton_procedures.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des procédures")))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date (Par défaut la date du jour)")))
        self.check_dateauto.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour que Noethys sélectionne automatiquement la date du jour (A minuit, la date changera automatiquement)")))
        self.bouton_log_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression")))
        self.bouton_log_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer")))
        self.bouton_log_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_log_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_vocal.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder au paramétrage de la synthèse vocale")))
        self.bouton_importation.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer des badgeages manuellement")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la procédure de badgeage en temps réél")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((950, 750))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_parametres.Add(self.label_procedure, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_procedure = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_procedure.Add(self.ctrl_procedure, 0, wx.EXPAND, 0)
        grid_sizer_procedure.Add(self.bouton_procedures, 0, 0, 0)
        grid_sizer_procedure.Add( (10, 10), 0, 0, 0)
        grid_sizer_procedure.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_procedure.Add(self.ctrl_date, 0, wx.EXPAND, 0)
        grid_sizer_procedure.Add( (10, 10), 0, 0, 0)
        grid_sizer_procedure.Add(self.check_dateauto, 0, wx.EXPAND, 0)
        grid_sizer_procedure.AddGrowableCol(0)
        grid_sizer_parametres.Add(grid_sizer_procedure, 1, wx.EXPAND, 0)
        
        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Log
        box_log = wx.StaticBoxSizer(self.box_log_staticbox, wx.VERTICAL)
        grid_sizer_log = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_log.Add(self.ctrl_log, 1, wx.EXPAND, 0)

        # Commandes
        grid_sizer_log_commandes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_log_commandes.Add(self.bouton_log_apercu, 0, 0, 0)
        grid_sizer_log_commandes.Add(self.bouton_log_imprimer, 0, 0, 0)
        grid_sizer_log_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_log_commandes.Add(self.bouton_log_excel, 0, 0, 0)
        grid_sizer_log_commandes.Add(self.bouton_log_texte, 0, 0, 0)
        grid_sizer_log.Add(grid_sizer_log_commandes, 1, wx.EXPAND, 0)

        grid_sizer_log.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_log.Add( (5, 5), 1, wx.EXPAND, 0)

        grid_sizer_log_options = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_log_options.Add(self.hyper_consommations, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_log_options.Add(self.label_separation1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_log_options.Add(self.hyper_journal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_log_options.Add(self.label_separation2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_log_options.Add(self.hyper_purger, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_log.Add(grid_sizer_log_options, 0, 0, 0)

        grid_sizer_log.AddGrowableRow(0)
        grid_sizer_log.AddGrowableCol(0)
        box_log.Add(grid_sizer_log, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_log, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_vocal, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_importation, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()  
        
        wx.CallLater(0, self.Layout) # Contre pb d'affichage du wx.Choice
    
    def OnChoixProcedure(self, event=None):
        pass
    
    def OnCheckDateauto(self, event):
        etat = self.check_dateauto.GetValue()
        self.ctrl_date.Enable(not etat)   
        if etat == True :
            self.ctrl_date.SetDate(datetime.date.today())
        
    def OnBoutonProcedures(self, event): 
        IDprocedure = self.ctrl_procedure.GetID()
        from Dlg import DLG_Badgeage_procedures
        dlg = DLG_Badgeage_procedures.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_procedure.MAJ() 
        if IDprocedure == None : IDprocedure = 0
        self.ctrl_procedure.SetID(IDprocedure)

    def OnBoutonLogApercu(self, event): 
        self.ctrl_log.Apercu(None)

    def OnBoutonLogImprimer(self, event): 
        self.ctrl_log.Imprimer(None)

    def OnBoutonLogExcel(self, event): 
        self.ctrl_log.ExportExcel(None)

    def OnBoutonLogTexte(self, event): 
        self.ctrl_log.ExportTexte(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Badgeage")
    
    def OnBoutonVocal(self, event):
        from Dlg import DLG_Vocal
        dlg = DLG_Vocal.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def PurgerJournal(self):
        OL_Badgeage_log.Purger() 
        
    def OnBoutonFermer(self, event): 
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event): 
        """ Lancement de la procédure de badgeage """
        self.LancementProcedure() 
        
    def LancementProcedure(self, importationManuelle=False) :
        if self.mode_debug == True or wx.GetKeyState(307):
            modeDebug = True # CONSERVER LA TOUCHE ALT ENFONCEE POUR LE MODE DEBUG
        else :
            modeDebug = False

        # Validation des données
        IDprocedure = self.ctrl_procedure.GetID() 
        if IDprocedure == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une procédure !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_procedure.SetFocus()
            return False
        
        date = self.ctrl_date.GetDate()
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False
        
        if date != datetime.date.today() :
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné une date différente d'aujourd'hui. Confirmez-vous ce choix ?"), _(u"Date"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return False

        # Vérifie si voix française disponible
        try :
            vocal = UTILS_Vocal.Vocal() 
            if vocal.VerifieSiVirginieInstallee() == False :
                if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="voix_virginie", valeur=False) == False:
                    introduction = _(u"Souhaitez-vous installer la voix française Virginie pour la synthèse vocale ?")
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Avertissement"), introduction=introduction, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Pas maintenant"), _(u"Ne plus demander")], defaut=0)
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse == 0:
                        self.OnBoutonVocal(None)
                    if reponse == 2:
                        UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="voix_virginie", valeur=True)
            else :
                if vocal.VerifieSiVirginieDefaut() == False :
                    dlg = wx.MessageDialog(self, _(u"La voix française Virginie est bien installée sur votre ordinateur mais n'a pas été sélectionnée comme voix par défaut.\n\nSouhaitez-vous le faire maintenant (conseillé) ?"), _(u"Synthèse vocale"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse == wx.ID_YES:
                        self.OnBoutonVocal(None)
        except Exception as err:
            print("Erreur dans module vocal depuis badgeage :", err)
        
        # Envoi l'info de lancement au log
        nomProcedure = self.ctrl_procedure.GetNom() 
        self.log.AjouterAction(action=_(u"Lancement de la procédure '%s'") % nomProcedure)
        
        # Rappel de la combinaison de touches pour quitter la fenêtre
        if importationManuelle == False and modeDebug == False :
            dlg = wx.MessageDialog(self, _(u"Appuyez sur CTRL+SHIFT+Q pour\nquitter l'interface de badgeage."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        # Ouvre la fenêtre de badgeage
        if modeDebug == True :
            style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX # CONSERVER LA TOUCHE ALT ENFONCEE POUR EVITER L'AFFICHAGE PLEIN ECRAN
        else :
            style = wx.BORDER_NONE
        dlg = DLG_Badgeage_interface.Dialog(self, log=self.ctrl_log, IDprocedure=IDprocedure, date=date, dateauto=self.check_dateauto.GetValue(), importationManuelle=importationManuelle, style=style, mode_debug=modeDebug)
        if modeDebug == False : 
            dlg.ShowFullScreen(wx.FULLSCREEN_ALL)
        dlg.ShowModal() 
        try :
            dlg.Destroy()
        except :
            pass

        # Envoi l'info de l'arrêt au log
        self.log.AjouterAction(action=_(u"Arrêt de la procédure '%s'") % nomProcedure)
    
    def OnBoutonImportation(self, event):
        """ Importation de badgeages """
        # Vérifie si procédure de badgeage sélectionnée
        nomProcedure = self.ctrl_procedure.GetNom() 
        IDprocedure = self.ctrl_procedure.GetID() 

        if IDprocedure == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une procédure de badgeage !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Recherche des badgeages à importer
        from Dlg import DLG_Badgeage_importation
        dlg = DLG_Badgeage_importation.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            listeDonnees = dlg.GetDonnees()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return
        
        # Vérifie si procédure compatible avec importation de badgeages
        DB = GestionDB.DB() 
        req = """SELECT IDaction, ordre, action, action_demande, action_message, action_question
        FROM badgeage_actions 
        WHERE IDprocedure=%d
        ORDER BY ordre
        ;""" % IDprocedure
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        DB.Close() 
        
        nbreMessages = 0
        for IDaction, ordre, action, action_demande, action_message, action_question in listeActions :
            
            if action == "message" or action_message != None : 
                nbreMessages += 1
                    
            if action_demande == "1" : 
                dlg = wx.MessageDialog(self, _(u"Une des actions de cette procédure contient une question de type 'Heure de début ou heure de fin ?' incompatible avec le processus d'importation."), _(u"Information"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
    
        if nbreMessages > 0 : 
            dlg = wx.MessageDialog(self, _(u"Notez que les messages ou questions programmées dans les actions ne seront pas prises en compte (%d actions).") % nbreMessages, _(u"Remarque"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment importer les %d badgeages sélectionnés avec la procédure '%s' ?") % (len(listeDonnees), nomProcedure), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        dlg.Destroy()
        
        # Lancement de la procédure
        self.LancementProcedure(importationManuelle=listeDonnees)
        
        
        
    
    def AfficheAvertissement(self):
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="infos_badgeage", valeur=False) == True :
            return
        
        from Dlg import DLG_Message_html
        texte = u"""
<CENTER><IMG SRC="%s">
<BR><BR>
<FONT SIZE=2>
<B>Avertissement</B>
<BR><BR>
Cette fonctionnalité étant très récente, il est conseillé de multiplier les tests avant une utilisation en situation réelle. Si vous constatez un bug, n'hésitez pas à le signaler sur le forum de Noethys.
<BR><BR>
Vous pouvez découvrir un petit aperçu des nombreuses possibilités offertes par ce module sur le forum :
<A HREF="http://www.noethys.com/index.php?option=com_kunena&Itemid=7&func=view&catid=5&id=965#965">Cliquez ici</A>
<BR><BR>
<I>Pensez à configurer la synthèse vocale pour bénéficier au maximum de l'interface de badgeage !</I>
</FONT>
</CENTER>
""" % Chemins.GetStaticPath("Images/32x32/Information.png")
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), nePlusAfficher=True)
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="infos_badgeage", valeur=nePlusAfficher)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None, mode_debug=True)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()