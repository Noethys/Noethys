#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import os
import time
import datetime
from threading import Thread, Lock
import GestionDB
from Utils import UTILS_Parametres
from Utils import UTILS_Fichiers
from Utils import UTILS_Customize
from Utils import UTILS_Portail_synchro
from Dlg.DLG_Portail_config import LISTE_DELAIS_SYNCHRO
import six
CUSTOMIZE = UTILS_Customize.Customize()

class Abort(Exception):
    pass

class Serveur(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.start_synchro = False
        self.synchro_en_cours = False
        self.active = False

    def Start(self):
        if self.IsRunning() == False :
            self.keepGoing = self.active = True
            self.start()

    def Stop(self):
        self.keepGoing = False

    def Pause(self):
        self.active = False

    def Reprise(self):
        self.active = True

    def IsRunning(self):
        if hasattr(self, "keepGoing") and self.keepGoing == True:
            return True
        else :
            return False

    def Start_synchro(self, event=None):
        if self.synchro_en_cours == False :
            self.start_synchro = True

    def HasSynchroEnCours(self):
        return self.synchro_en_cours

    def GetHeureProchaineSynchro(self):
        return self.parent.last_synchro + datetime.timedelta(minutes=self.parent.delai)

    def run(self):
        while self.keepGoing:

            if self.active == True :
                try :

                    if self.parent.last_synchro == None :
                        # Lance une synchro quelques secondes après le démarrage
                        if self.parent.synchro_ouverture == True :
                            self.parent.last_synchro = datetime.datetime.now()
                            time.sleep(30)
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
                        self.parent.MAJ_bouton()

                except Exception as err :
                    if not str(err).startswith("The C++ part"):
                        raise

            # Attends 1 seconde
            time.sleep(1)


    def abort(self):
        self.stop = True






class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.lock = Lock()
        self.parent = parent
        self.last_synchro = None
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/48x48/Sync_off.png"), wx.BITMAP_TYPE_ANY))



        if CUSTOMIZE.GetValeur("connecthys_log", "type", "panel") == "panel" :
            self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
            self.log.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.gauge = wx.Gauge(self, -1, range=100, size=(-1, 8))

        self.bouton_traiter = wx.Button(self, -1, _(u"Traiter les\ndemandes"))
        self.bouton_traiter.SetToolTip(wx.ToolTip(_(u"traiter les demandes")))
        self.couleur_defaut = self.bouton_traiter.GetBackgroundColour()

        self.bouton_synchroniser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_synchroniser.SetToolTip(wx.ToolTip(_(u"Synchroniser maintenant les données entre Noethys et Connecthys")))

        self.bouton_outils = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Outils")))

        self.__do_layout()
        self.MAJ_bouton()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTraiter, self.bouton_traiter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSynchroniser, self.bouton_synchroniser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)

        # Init
        self.SetGauge(0)
        self.SetImage("on")

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer.Add(self.ctrl_image, 0, wx.ALL, 0)

        if CUSTOMIZE.GetValeur("connecthys_log", "type", "panel") == "panel" :
            sizer_log = wx.BoxSizer(wx.VERTICAL)
            sizer_log.Add(self.log, 1, wx.EXPAND|wx.ALL, 0)
            sizer_log.Add(self.gauge, 0, wx.EXPAND|wx.ALL, 0)
            grid_sizer.Add(sizer_log, 1, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_commandes.Add(self.bouton_traiter, 1, wx.EXPAND, 0)

        grid_sizer_commandes2 = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=2)
        grid_sizer_commandes2.Add(self.bouton_synchroniser, 1, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.bouton_outils, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.AddGrowableCol(0)

        grid_sizer_commandes.Add(grid_sizer_commandes2, 0, wx.EXPAND, 0)

        grid_sizer_commandes.AddGrowableRow(0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer.Add(grid_sizer_commandes, 0, wx.EXPAND|wx.ALL, 0)

        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(1)
        sizer_base.Add(grid_sizer, 1, wx.EXPAND|wx.ALL, 10)

        self.lock.acquire(True)
        try:
            self.SetSizer(sizer_base)
        except Exception as e:
            self.lock.release()
            raise e
        else:
            self.lock.release()
        self.Layout()

    def MAJ(self, block=True):
        """ MAJ du bouton Demandes """
        # Paramètres

        if self.lock.acquire(block) == True:
            try:
                index = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="client_synchro_portail_delai", valeur=1)
                self.delai = LISTE_DELAIS_SYNCHRO[index][0]
                self.synchro_ouverture = UTILS_Parametres.Parametres(mode="get", categorie="portail", nom="client_synchro_portail_ouverture", valeur=True)
            except Exception as e:
                self.lock.release()
                raise e
            else:
                self.lock.release()
            self.MAJ_bouton()
            return True
        else:
            return False


    def MAJ_bouton(self, block=True):
        # Recherche le nombre d'actions enregistrées non traitées
        DB = GestionDB.DB()
        req = """SELECT IDaction, horodatage
        FROM portail_actions
        WHERE etat <> 'validation';"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        nbre_actions_attente = len(listeDonnees)

        # MAJ du bouton Analyser
        if self.lock.acquire(block) == True:
            try:
                if nbre_actions_attente == 0 :
                    texte = _(u"Aucune\ndemande")
                    self.bouton_traiter.SetBackgroundColour(self.couleur_defaut)
                    #self.bouton_traiter.Enable(False)
                elif nbre_actions_attente == 1 :
                    texte = _(u"1 demande\nà traiter")
                    self.bouton_traiter.SetBackgroundColour((150, 255, 150))
                    #self.bouton_traiter.Enable(True)
                else :
                    texte = _(u"%d demandes\nà traiter") % nbre_actions_attente
                    self.bouton_traiter.SetBackgroundColour((150, 255, 150))
                    #self.bouton_traiter.Enable(True)

                self.bouton_traiter.SetLabel(texte)

                # TaskBarIcon
                self.parent.taskBarIcon.Connecthys(nbre=nbre_actions_attente, texte=texte)

            except Exception as e:
                self.lock.release()
                raise e
            else:
                self.lock.release()
            return True
        else:
            return False

    def StartServeur(self, block=True):
        if not hasattr(self, "serveur") :
            if self.lock.acquire(block) == True:
                try:
                    self.serveur = Serveur(self)
                except Exception as e:
                    self.lock.release()
                    raise e
                else:
                    self.lock.release()
            else:
                return False
            self.serveur.Start()
            return self.EcritLog(_(u"Client de synchronisation prêt"))
        else :
            self.serveur.Start()

    def PauseServeur(self):
        if hasattr(self, "serveur") :
            self.serveur.Pause()

    def RepriseServeur(self):
        if hasattr(self, "serveur") :
            self.serveur.Reprise()

    def StopServeur(self):
        if hasattr(self, "serveur") :
            self.serveur.Stop()

    def HasSynchroEnCours(self):
        if hasattr(self, "serveur") :
            return self.serveur.HasSynchroEnCours()
        return False

    def OnBoutonTraiter(self, event=None):
        from Dlg import DLG_Portail_demandes
        dlg = DLG_Portail_demandes.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ()
        try :
            self.parent.ctrl_remplissage.MAJ()
        except :
            pass

    def OnBoutonSynchroniser(self, event=None):
        self.serveur.Start_synchro()

    def OnBoutonOutils(self, event=None):
        """ Création du menu Outils """
        menuPop = UTILS_Adaptations.Menu()

        # Afficher heure prochaine synchro
        id = wx.Window.NewControlId()
        texte_next_synchro = _(u"Prochaine synchronisation prévue à %s") % self.serveur.GetHeureProchaineSynchro().strftime("%Hh%M")
        item = wx.MenuItem(menuPop, id, texte_next_synchro, texte_next_synchro)
        menuPop.AppendItem(item)
        item.Enable(False)

        menuPop.AppendSeparator()

        # Synchroniser maintenant les données
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menuPop, id, _(u"Synchroniser maintenant"), _(u"Synchroniser maintenant les données entre Noethys et Connecthys"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)

        self.lock.acquire(True)
        try:
            self.Bind(wx.EVT_MENU, self.serveur.Start_synchro, id=id)
        except Exception as e:
            self.lock.release()
            raise e
        else:
            self.lock.release()

        # Configuration du portail
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menuPop, id, _(u"Configuration"), _(u"Accéder à la configuration de Connecthys"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)

        self.lock.acquire(True)
        try:
            self.Bind(wx.EVT_MENU, self.OnMenuConfiguration, id=id)
        except Exception as e:
            self.lock.release()
            raise e
        else:
            self.lock.release()

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnMenuConfiguration(self, event):
        from Dlg import DLG_Portail_config
        dlg = DLG_Portail_config.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ()
        try:
            self.parent.AfficherServeurConnecthys()
            self.parent.ctrl_remplissage.MAJ()
        except AttributeError:
            pass

    def SetImage(self, etat="on", block=True):
        if self.lock.acquire(block) == True:
            try:
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
                wx.CallAfter(self.ctrl_image.SetBitmap, wx.Bitmap(Chemins.GetStaticPath("Images/48x48/%s" % nomImage), wx.BITMAP_TYPE_ANY))
            except Exception as e:
                self.lock.release()
                raise e
            else:
                self.lock.release()
            return True
        else:
            return False

    def EcritLog(self, message="", block=True):
        horodatage = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        if CUSTOMIZE.GetValeur("connecthys_log", "type", "panel") == "panel" :
            if self.lock.acquire(block) == True:
                if len(self.log.GetValue()) > 0 :
                    texte = u"\n"
                else :
                    texte = u""
                try :
                    texte += u"[%s] %s" % (horodatage, message)
                except :
                    texte += u"[%s] %s" % (horodatage, str(message).decode('UTF-8'))
                wx.CallAfter(self.log.AppendText, texte)
                self.lock.release()
                return True
            else:
                return False
        elif CUSTOMIZE.GetValeur("connecthys_log", "type", "panel") == "file" :
            file_log = open(UTILS_Fichiers.GetRepUtilisateur(CUSTOMIZE.GetValeur("connecthys_log", "file_name", "connecthys_synchro.log")), "a")
            texte = u"\n"
            if self.lock.acquire(block) == True:
                try :
                    texte += u"[%s] %s" % (horodatage, message)
                    file_log.write(six.text_type(texte).encode('UTF-8'))
                except :
                    texte += u"[%s] %s" % (horodatage, str(message).decode('UTF-8'))
                    file_log.write(six.text_type(texte).encode('UTF-8'))

                file_log.close()
                self.lock.release()
                return True
            else:
                return False

    def SetGauge(self, valeur=0, block=True):
        if self.lock.acquire(block) == True:
            try:
                if valeur == 0 :
                    if self.gauge.IsShown() :
                        wx.CallAfter(self.gauge.Show, False)
                else :
                    if not self.gauge.IsShown() :
                        wx.CallAfter(self.gauge.Show, True)
                self.Layout()
                wx.CallAfter(self.gauge.SetValue, valeur)
            except Exception as e:
                self.lock.release()
                raise e
            else:
                self.lock.release()
            return True
        else:
            return False

    def OnClose(self, evt):
        self.serveur.Stop()
        time.sleep(0.1)
        self.Destroy()

    def OnDestroy(self, evt):
        self.serveur.Stop()

    def SetLastSynchro(self, last_synchro, block=True):
        if self.lock.acquire(block) == True:
            try:
                self.last_synchro = last_synchro
            except Exception as e:
                self.lock.release()
                raise e
            else:
                self.lock.release()
            return True
        else:
            return False

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