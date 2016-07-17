#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import os
import time
import datetime
from threading import Thread
import FonctionsPerso
from Utils import UTILS_Parametres
from Utils import UTILS_Fichiers
from Utils import UTILS_Portail_synchro
from Dlg.DLG_Portail_config import LISTE_DELAIS_SYNCHRO


class Abort(Exception):
    pass

class Serveur(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.start_synchro = False
        self.synchro_en_cours = False

    def Start(self):
        self.keepGoing = self.running = True
        self.start()

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Start_synchro(self, event=None):
        if self.synchro_en_cours == False :
            self.start_synchro = True

    def GetHeureProchaineSynchro(self):
        return self.parent.last_synchro + datetime.timedelta(minutes=self.parent.delai)

    def run(self):
        while self.keepGoing:

            try :

                if self.parent.last_synchro == None :
                    # Lance une synchro quelques secondes après le démarrage
                    if self.parent.synchro_ouverture == True :
                        self.parent.last_synchro = datetime.datetime.now()
                        time.sleep(3)
                        self.start_synchro = True
                    else :
                        self.parent.last_synchro = datetime.datetime.now()
                else :
                    # Vérifie si une synchro est nécessaire selon le délai choisi
                    if datetime.datetime.now() >= self.GetHeureProchaineSynchro() :
                        self.start_synchro = True

                # Lancement de la procédure de synchronisation
                if self.start_synchro == True and self.synchro_en_cours == False :

                    self.start_synchro = False

                    # Mémorise l'heure de la dernière synchro
                    self.parent.last_synchro = datetime.datetime.now()

                    # Effectue la synchro
                    self.parent.SetImage("upload")
                    self.synchro_en_cours = True
                    synchro = UTILS_Portail_synchro.Synchro(log=self.parent)
                    synchro.Synchro_totale()
                    self.synchro_en_cours = False
                    self.parent.SetImage("on")

            except Exception, err :
                if not str(err).startswith("The C++ part"):
                    raise

            # Attends 1 seconde
            time.sleep(1)

        self.running = False

    def abort(self):
        self.stop = True






class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/48x48/Sync_off.png"), wx.BITMAP_TYPE_ANY))
    
        self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.log.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        self.gauge = wx.Gauge(self, -1, range=100, size=(-1, 8))
        
        self.bouton_analyse = wx.Button(self, -1, _(u"Traiter les\ndemandes"))
        self.couleur_defaut = self.bouton_analyse.GetBackgroundColour()
        self.bouton_outils = wx.Button(self, -1, _(u"Outils"))
        
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnalyse, self.bouton_analyse)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        self.SetGauge(0)
        self.last_synchro = None
        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer.Add(self.ctrl_image, 0, wx.ALL, 0)
        
        sizer_log = wx.BoxSizer(wx.VERTICAL)
        sizer_log.Add(self.log, 1, wx.EXPAND|wx.ALL, 0)
        sizer_log.Add(self.gauge, 0, wx.EXPAND|wx.ALL, 0)
        grid_sizer.Add(sizer_log, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_analyse, 1, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_outils, 0, wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableRow(0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer.Add(grid_sizer_commandes, 0, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(1)
        sizer_base.Add(grid_sizer, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()
    
    def MAJ(self):
        """ MAJ du bouton Analyser """
        # Paramètres
        index = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="serveur_synchro_delai", valeur=2)
        self.delai = LISTE_DELAIS_SYNCHRO[index][0]
        self.synchro_ouverture = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="serveur_synchro_ouverture", valeur=True)

        return


        IDfichier = FonctionsPerso.GetIDfichier()
        listeFichiers = os.listdir(UTILS_Fichiers.GetRepSync())
        nbreFichiers = 0
        for nomFichier in listeFichiers :
            if nomFichier.startswith("actions_%s" % IDfichier) and nomFichier.endswith(".dat") :
                nbreFichiers += 1
        
        # MAJ du bouton Analyser
        if nbreFichiers == 0 :
            self.bouton_analyse.SetToolTipString(_(u"Aucun fichier à importer"))
            self.bouton_analyse.SetBackgroundColour(self.couleur_defaut)
            self.bouton_analyse.Enable(False)            
        elif nbreFichiers == 1 :
            self.bouton_analyse.SetToolTipString(_(u"1 fichier à importer"))
            self.bouton_analyse.SetBackgroundColour((150, 255, 150))
            self.bouton_analyse.Enable(True)
        else :
            self.bouton_analyse.SetToolTipString(_(u"%d fichiers à importer") % nbreFichiers)
            self.bouton_analyse.SetBackgroundColour((150, 255, 150))
            self.bouton_analyse.Enable(True)
        
    def StartServeur(self):
        #StartServer(log=self)
        self.serveur = Serveur(self)
        self.serveur.Start()
        self.EcritLog(_(u"Serveur prêt"))

        # Lance une première synchro après le démarrage
        #self.serveur.Start_synchro()

    def OnBoutonAnalyse(self, event=None):
        from Dlg import DLG_Synchronisation
        dlg = DLG_Synchronisation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.MAJ() 

    def OnBoutonOutils(self, event=None):
        """ Création du menu Outils """
        menuPop = wx.Menu()

        # Afficher heure prochaine synchro
        id = wx.NewId()
        texte_next_synchro = _(u"Prochaine synchronisation prévue à %s") % self.serveur.GetHeureProchaineSynchro().strftime("%Hh%M")
        item = wx.MenuItem(menuPop, id, texte_next_synchro, texte_next_synchro)
        menuPop.AppendItem(item)
        item.Enable(False)

        menuPop.AppendSeparator()

        # Synchroniser maintenant les données
        id = wx.NewId()
        item = wx.MenuItem(menuPop, id, _(u"Synchroniser maintenant"), _(u"Synchroniser maintenant les données entre Noethys et Connecthys"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.serveur.Start_synchro, id=id)

        # Configuration du portail
        id = wx.NewId()
        item = wx.MenuItem(menuPop, id, _(u"Configuration"), _(u"Accéder à la configuration de Connecthys"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnMenuConfiguration, id=id)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnMenuConfiguration(self, event):
        from Dlg import DLG_Portail_config
        dlg = DLG_Portail_config.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ()

    def SetImage(self, etat="on"):
        if etat == "upload" : 
            nomImage = "Sync_upload.png"
        elif etat == "download" : 
            nomImage = "Sync_download.png"
        elif etat == "off" : 
            nomImage = "Sync_off.png"
        elif etat == "on" : 
            nomImage = "Sync_on.png"
        else :
            nomImage = "Sync_on.png"
        self.ctrl_image.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/48x48/%s" % nomImage), wx.BITMAP_TYPE_ANY))
        
    def EcritLog(self, message=""):
        horodatage = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        if len(self.log.GetValue()) >0 :
            texte = u"\n"
        else :
            texte = u""
        try :
            texte += u"[%s] %s" % (horodatage, message)
        except :
            texte += u"[%s] %s" % (horodatage, str(message).decode("iso-8859-15"))
        self.log.AppendText(texte)
        
    def SetGauge(self, valeur=0):
        if valeur == 0 :
            if self.gauge.IsShown() :
                self.gauge.Show(False)
                self.Layout() 
        else :
            if not self.gauge.IsShown() :
                self.gauge.Show(True)
                self.Layout() 
        self.gauge.SetValue(valeur)
        
    def OnClose(self, evt):
        self.serveur.Stop()
        time.sleep(0.1)
        self.Destroy()

        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        self.ctrl.MAJ() 
        wx.CallLater(10, self.ctrl.StartServeur)
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