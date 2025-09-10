#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import re
import json
import socket 
import time
from six.moves.urllib.request import urlopen
from threading import Thread 
import FonctionsPerso
from Utils import UTILS_Fichiers
from Utils import UTILS_Config
from Utils import UTILS_Export_nomade
import six
from Dlg.DLG_Synchronisation import AnalyserFichier



PORT_DEFAUT = 8000
IP_AUTORISEES = None
IP_INTERDITES = None


class Erreur:
    pass
    
try :
    from twisted.internet import wxreactor
    wxreactor.install()
    from twisted.internet import reactor, protocol
    Protocol = protocol.Protocol
    IMPORT_TWISTED = True
except Exception as err :
    print("Erreur d'importation de Twisted : ", err)
    IMPORT_TWISTED = False
    Protocol = Erreur
    
    


class Abort(Exception): 
    pass 

class GenerationFichier(Thread): 
    def __init__(self, parent): 
        Thread.__init__(self) 
        self.parent = parent
        self.stop = False 

    def run(self): 
        self.parent.log.SetImage("upload")
        self.parent.EcritLog(_(u"Génération du fichier de données"))
        try: 
            export = UTILS_Export_nomade.Export()
            nomFichier = export.Run() 
            self.parent.EnvoyerInfosSurFichierAEnvoyer(nomFichier) 
            self.parent.log.SetImage("on")
        except: 
            self.stop = True 
            self.parent.log.SetImage("on")
            raise 

    def abort(self): 
        self.stop = True



class Echo(Protocol):
    dictFichierReception = None
    log = None
    
    def EcritLog(self, texte=""):
        if self.log != None :
            self.log.EcritLog(texte)
            
    def connectionMade(self):
        ip = self.transport.getPeer().host
        self.EcritLog("Connexion depuis le client " + ip)

        # Validation de l'IP
        if IP_AUTORISEES not in (None, "") :
            if self.IsIPinListe(IP_AUTORISEES, ip) == False :
                self.EcritLog(_(u"Adresse IP non autorisée"))
                self.transport.loseConnection()

        if IP_INTERDITES not in (None, "") :
            if self.IsIPinListe(IP_INTERDITES, ip) == True :
                self.EcritLog(_(u"Adresse IP interdite"))
                self.transport.loseConnection()

    def IsIPinListe(self, listeStr="", ip=""):
        liste_ip = listeStr.split(";")
        for ipTemp in liste_ip :
            ipTemp = ipTemp.replace(".", "\.")
            ipTemp = ipTemp.replace("*", ".*")
            if re.match(ipTemp, ip) != None :
                return True
        return False

    def GenerationFichierAEnvoyer(self):
        self.generateur = GenerationFichier(self) 
        self.generateur.start()
        self.log.SetImage("on")
    
    def EnvoyerInfosSurFichierAEnvoyer(self, nomFichier=""):
        self.nomFichierAEnvoyer = nomFichier
        self.log.SetImage("upload")
        tailleFichier = os.path.getsize(nomFichier)
        texte = json.dumps({"action": "envoyer", "nom": os.path.basename(nomFichier), "taille": tailleFichier})
        if six.PY3:
            texte = texte.encode('utf-8')
        self.transport.write(texte)
        self.EcritLog(_(u"Envoi du fichier (%s)") % FonctionsPerso.Formate_taille_octets(tailleFichier))
        self.log.SetImage("on")
        
    def dataReceived(self, data):
        # Envoi d'un fichier - init
        if data in ("recevoir", b"recevoir"):
            self.GenerationFichierAEnvoyer() 
            return

        # Envoi du fichier si client pret a recevoir
        if data in ("pret_pour_reception", b"pret_pour_reception"):
            self.Envoyer()
            return
        
        # Fin de l'envoi
        if data in ("fin_envoi", b"fin_envoi"):
            self.FinEnvoi() 
            return
        
        # Si JSON : Réception d'un fichier
        if self.IdentificationJSON(data) :
            message = json.loads(data)

            # Reception d'un fichier - init
            if message["action"] == "envoyer" :
                nom_appareil = message["nom_appareil"]
                tailleFichier = message["taille"]
                nomInitial = message["nom"]
                nomFinal = UTILS_Fichiers.GetRepSync(nomInitial)
                self.EcritLog(_(u"Prêt à recevoir de l'appareil ") + nom_appareil + " le fichier " + nomInitial + " (" + FonctionsPerso.Formate_taille_octets(tailleFichier) + ")")
                fichier = open(nomFinal, "wb")
                self.dictFichierReception = {
                    "nom_initial" : nomInitial,
                    "nom_final" : nomFinal,
                    "taille_totale" : tailleFichier,
                    "taille_actuelle" : 0,
                    "fichier" : fichier,
                    }
                texte = "pret_pour_reception"
                if six.PY3:
                    texte = texte.encode('utf-8')
                self.transport.write(texte)
                self.EcritLog(_(u"Réception en cours")) 
                self.log.SetImage("download")
                return
        
        # Réception des données d'un fichier
        if self.dictFichierReception != None :
            self.dictFichierReception["fichier"].write(data)
        
            # Calcule de la taille de la partie telechargee
            self.dictFichierReception["taille_actuelle"] += len(data)
            pourcentage = int(100.0 * self.dictFichierReception["taille_actuelle"] / self.dictFichierReception["taille_totale"])
            #self.EcritLog(_(u"Réception en cours...  ") + str(pourcentage) + u" %")
            self.log.SetGauge(pourcentage)
            return

        # Si aucune data valide, on déconnecte
        self.EcritLog(_(u"Aucune donnée valide reçue"))
        self.transport.loseConnection()
    
    def IdentificationJSON(self, data):
        try :
            message = json.loads(data)
            return True
        except :
            return False

    def Envoyer(self):
        self.log.SetImage("upload")
        self.EcritLog(_(u"Envoi en cours"))
        f = open(self.nomFichierAEnvoyer, "rb")
        self.transport.write(f.read())
        f.close()
        
    def FinEnvoi(self):
        self.EcritLog(_(u"Fin de l'envoi"))
        self.log.SetImage("on")
        self.log.SetGauge(0)
        self.transport.loseConnection()
        
    def connectionLost(self, reason):
        self.EcritLog(_(u"Fin de connexion du client ") + self.transport.getPeer().host)
        if self.dictFichierReception != None:
            wx.CallLater(1000, self.log.SetGauge, 0)
            self.log.SetImage("on")
            self.EcritLog(_(u"Clôture du fichier de réception"))
            nomFichier = self.dictFichierReception["nom_initial"]
            self.dictFichierReception["fichier"].close()
            self.dictFichierReception = None
            
            # Analyse du fichier
            resultat = AnalyserFichier(nomFichier)
            self.log.MAJ()

            

def StartServer(log=None):
    if IMPORT_TWISTED == False :
        log.EcritLog(_(u"Erreur : Problème d'importation de Twisted"))
        return
    
    try :
        factory = protocol.ServerFactory()
        factory.protocol = Echo
        factory.protocol.log = log
        reactor.registerWxApp(wx.GetApp())
        port = int(UTILS_Config.GetParametre("synchro_serveur_port", defaut=PORT_DEFAUT))
        reactor.listenTCP(port, factory)
    except Exception as err:
        print(("Erreur lancement serveur Nomadhys :", err))
        log.EcritLog(_(u"Erreur dans le lancement du serveur Nomadhys [factory] :") )
        log.EcritLog(err)

    try :
        # IP locale
        #ip_local = socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('jsonip.com', 80))
        ip_local = s.getsockname()[0]
        s.close()
        log.EcritLog(_(u"IP locale : %s") % ip_local)
    except Exception as err:
        print(("Erreur lancement serveur Nomadhys :", err))
        log.EcritLog(_(u"Erreur dans le lancement du serveur Nomadhys [IP locale] :"))
        log.EcritLog(err)

    try :
        # IP internet
        ip_internet = json.loads(urlopen("https://jsonip.com", timeout=1).read())["ip"]
        log.EcritLog(_(u"IP internet : %s") % ip_internet)
    except Exception as err:
        print(("Erreur lancement serveur Nomadhys :", err))
        log.EcritLog(_(u"Erreur dans le lancement du serveur Nomadhys [IP internet] :"))
        log.EcritLog(err)

    log.EcritLog(_(u"Serveur prêt sur le port %d") % port)
    log.SetImage("on")

    # Démarrage serveur
    try :
        reactor.run()
    except Exception as err :
        print(("Erreur lancement serveur Nomadhys :", err))
        log.EcritLog(_(u"Erreur dans le lancement du serveur Nomadhys [reactor] :") )
        log.EcritLog(err)


def StopServer():
    try :
        reactor.stop()
    except Exception as err :
        pass
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/48x48/Sync_off.png"), wx.BITMAP_TYPE_ANY))
    
        self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.log.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        self.gauge = wx.Gauge(self, -1, range=100, size=(-1, 8))
        
        self.bouton_analyse = wx.Button(self, -1, _(u"Analyser"))
        self.couleur_defaut = self.bouton_analyse.GetBackgroundColour()

        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnalyse, self.bouton_analyse)

        # Init
        self.SetGauge(0)
        

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
        # Paramètres liste blanche et liste noire d'IP
        global IP_AUTORISEES, IP_INTERDITES
        IP_AUTORISEES = UTILS_Config.GetParametre("synchro_serveur_ip_autorisees", defaut=None)
        IP_INTERDITES = UTILS_Config.GetParametre("synchro_serveur_ip_interdites", defaut=None)

        # Lecture des fichiers du répertoire SYNC
        IDfichier = FonctionsPerso.GetIDfichier()
        listeFichiers = os.listdir(UTILS_Fichiers.GetRepSync())
        nbreFichiers = 0
        for nomFichier in listeFichiers :
            if nomFichier.startswith("actions_%s" % IDfichier) and nomFichier.endswith(".dat") :
                nbreFichiers += 1

        # MAJ du bouton Analyser
        if nbreFichiers == 0 :
            self.bouton_analyse.SetToolTip(wx.ToolTip(_(u"Aucun fichier à importer")))
            self.bouton_analyse.SetBackgroundColour(self.couleur_defaut)
            self.bouton_analyse.Enable(False)            
        elif nbreFichiers == 1 :
            self.bouton_analyse.SetToolTip(wx.ToolTip(_(u"1 fichier à importer")))
            self.bouton_analyse.SetBackgroundColour((150, 255, 150))
            self.bouton_analyse.Enable(True)
        else :
            self.bouton_analyse.SetToolTip(wx.ToolTip(_(u"%d fichiers à importer") % nbreFichiers))
            self.bouton_analyse.SetBackgroundColour((150, 255, 150))
            self.bouton_analyse.Enable(True)
        
    def StartServeur(self):
        StartServer(log=self)
        
    def OnBoutonAnalyse(self, event=None):
        from Dlg import DLG_Synchronisation
        dlg = DLG_Synchronisation.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.MAJ() 

    def OnBoutonOptions(self, event=None):
        print("options")
    
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
            texte += u"[%s] %s" % (horodatage, str(message).decode("utf8"))
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