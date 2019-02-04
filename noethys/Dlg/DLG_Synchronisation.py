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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import datetime
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Ultrachoice
import GestionDB
import base64
import ftplib
import shutil
import zipfile

from Utils import UTILS_Export_nomade
from Utils import UTILS_Dates
from Utils import UTILS_Parametres
import FonctionsPerso
from Utils import UTILS_Fichiers
from Utils import UTILS_Config
from Utils import UTILS_Cryptage_fichier

from Ol import OL_Synchronisation_fichiers






def AnalyserFichier(nomFichier="", tailleFichier=None, typeTransfert=None):
    cheminFichier = UTILS_Fichiers.GetRepSync(nomFichier)
    listeAnomalies = []
    
    # Vérification de la taille du fichier
    if tailleFichier != None :
        tailleFinaleFichier = os.path.getsize(cheminFichier)
        if tailleFichier != tailleFinaleFichier :
            listeAnomalies.append((nomFichier, _(u"Le fichier n'a pas été téléchargé en intégralité (%d/%d)") % (tailleFichier, tailleFinaleFichier)))
            os.remove(cheminFichier)
            return False
        
    # Décryptage du fichier
    if nomFichier.endswith(UTILS_Export_nomade.EXTENSION_CRYPTE) :
        nouveauCheminFichier = cheminFichier.replace(UTILS_Export_nomade.EXTENSION_CRYPTE, UTILS_Export_nomade.EXTENSION_DECRYPTE)
        mdp = base64.b64decode(UTILS_Config.GetParametre("synchro_cryptage_mdp", defaut=""))
        resultat = UTILS_Cryptage_fichier.DecrypterFichier(cheminFichier, nouveauCheminFichier, mdp)
        os.remove(cheminFichier)
    else :
        nouveauCheminFichier = cheminFichier
        
    # Décompression du fichier
    if zipfile.is_zipfile(nouveauCheminFichier) == False :
        listeAnomalies.append((nomFichier, _(u"Le fichier compressé ne semble pas valide.")))
        return False        
    
    fichierZip = zipfile.ZipFile(nouveauCheminFichier, "r")
    buffer = fichierZip.read("database.dat")
    f = open(nouveauCheminFichier.replace(UTILS_Export_nomade.EXTENSION_DECRYPTE, ".dat"), "wb")
    #print "Ecriture du fichier ", nouveauCheminFichier.replace(UTILS_Export_nomade.EXTENSION_DECRYPTE, ".dat")
    f.write(buffer)
    f.close()
    fichierZip.close()
    os.remove(nouveauCheminFichier)
        
    #print "listeAnomalies=", listeAnomalies
    
    return True





class CTRL_Mode(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent):
        donnees=[ 
            {"label" : _(u"Transfert par FTP"), "description" : _(u"Pour transférer les données par FTP depuis ou vers un hébergement internet"), "image" : wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Ftp.png"), wx.BITMAP_TYPE_ANY)},
            {"label" : _(u"Transfert manuel"), "description" : _(u"Pour sélectionner un fichier sur un support physique (disque dur, clé USB, etc...)"), "image" : wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Sauvegarde_param.png"), wx.BITMAP_TYPE_ANY)},
            ]
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees=donnees) 
        self.parent = parent
        self.SetDonnees(donnees)
        self.Select(0)
                                        
    def SetMode(self, code=None):
        if code == "ftp" : self.SetSelection2(0) 
        if code == "fichier" : self.SetSelection2(1) 

    def GetMode(self):
        if self.GetSelection2() == 0 : return "ftp"
        if self.GetSelection2() == 1 : return "fichier"


# ---------------------------------------------------------------------------------------------------------------------------

class Page_serveur(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        self.label_activer = wx.StaticText(self, -1, _(u"Activer :"))
        self.check_activer = wx.CheckBox(self, -1, u"")
        self.label_info = wx.StaticText(self, -1, _(u"(Relancez Noethys pour appliquer les modifications)"))
        self.label_info.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.label_info.SetForegroundColour(wx.Colour(150, 150, 150))
        self.label_port = wx.StaticText(self, -1, _(u"Port :"))
        self.ctrl_port = wx.TextCtrl(self, -1, u"8000", size=(50, -1))
        self.label_ip_autorisees = wx.StaticText(self, -1, _(u"IP autorisées :"))
        self.ctrl_ip_autorisees = wx.TextCtrl(self, -1, u"")
        self.label_ip_interdites = wx.StaticText(self, -1, _(u"IP interdites :"))
        self.ctrl_ip_interdites = wx.TextCtrl(self, -1, u"")

        # Propriétés
        self.check_activer.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer/désactiver le serveur WIFI/Direct au prochain démarrage de Noethys")))
        self.ctrl_port.SetToolTip(wx.ToolTip(_(u"Sélectionnez le port de communication")))
        legende_texte_ip = _(u"""
        
Vous pouvez utiliser le symbole * comme caractère de substitution.

Exemples de saisies possibles : 
'192.168.1.1;192.128.1.2'
'192.168.1.12'
'192.168.1.*;192.*;192.168.*.*;192.*.1'     
        """)
        self.ctrl_ip_autorisees.SetToolTip(wx.ToolTip(_(u"Saisissez une suite d'adresses IP autorisées à se connecter (séparées par des points-virgules). Laissez vide pour tout autoriser.  %s") % legende_texte_ip))
        self.ctrl_ip_interdites.SetToolTip(wx.ToolTip(_(u"Saisissez une suite d'adresses IP interdites de se connecter (séparées par des points-virgules). Laissez vide pour tout autoriser.  %s") % legende_texte_ip))

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_activer, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer2.Add(self.check_activer, 0, wx.LEFT, 10)
        sizer2.Add(self.label_info, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_base.Add(sizer2, 0, wx.EXPAND, 0)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)

        grid_sizer_bas.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_bas.Add(self.ctrl_port, 0, 0, 0)
        grid_sizer_bas.Add( (1, 1), 0, 0, 0)
        grid_sizer_bas.Add(self.label_ip_autorisees, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_bas.Add(self.ctrl_ip_autorisees, 0, wx.EXPAND, 0)
        grid_sizer_bas.Add( (1, 1), 0, 0, 0)
        grid_sizer_bas.Add(self.label_ip_interdites, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_bas.Add(self.ctrl_ip_interdites, 0, wx.EXPAND, 0)

        grid_sizer_bas.AddGrowableCol(4)
        grid_sizer_bas.AddGrowableCol(7)

        grid_sizer_base.Add(grid_sizer_bas, 0, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(0)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def GetParametres(self):
        return {"synchro_serveur_activer" : self.check_activer.GetValue(), "synchro_serveur_port" : self.ctrl_port.GetValue(),
                "synchro_serveur_ip_autorisees" : self.ctrl_ip_autorisees.GetValue(), "synchro_serveur_ip_interdites" : self.ctrl_ip_interdites.GetValue()}
    
    def SetParametres(self, dictDonnees={}):
        if "synchro_serveur_activer" in dictDonnees : 
            self.check_activer.SetValue(dictDonnees["synchro_serveur_activer"])
        if "synchro_serveur_port" in dictDonnees : 
            self.ctrl_port.SetValue(dictDonnees["synchro_serveur_port"])
        if "synchro_serveur_ip_autorisees" in dictDonnees :
            self.ctrl_ip_autorisees.SetValue(dictDonnees["synchro_serveur_ip_autorisees"])
        if "synchro_serveur_ip_interdites" in dictDonnees :
            self.ctrl_ip_interdites.SetValue(dictDonnees["synchro_serveur_ip_interdites"])

    def Validation(self):
        if self.check_activer.GetValue() == True and self.ctrl_port.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un numéro de port !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_port.SetFocus()
            return False
        return True
        
# ---------------------------------------------------------------------------------------------------------------------------

class Page_ftp(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        self.label_hote = wx.StaticText(self, -1, _(u"Adresse hôte :"))
        self.ctrl_hote = wx.TextCtrl(self, -1, u"")
        self.label_identifiant = wx.StaticText(self, -1, _(u"Identifiant :"))
        self.ctrl_identifiant = wx.TextCtrl(self, -1, u"")
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.label_repertoire = wx.StaticText(self, -1, _(u"Répertoire :"))
        self.ctrl_repertoire = wx.TextCtrl(self, -1, u"www/")
        self.bouton_test = wx.Button(self, -1, _(u"Tester la\nconnexion"))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        # Propriétés
        self.ctrl_hote.SetToolTip(wx.ToolTip(_(u"Saisissez l'adresse de l'hôte")))
        self.ctrl_identifiant.SetToolTip(wx.ToolTip(_(u"Saisissez l'identifiant")))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Saisissez le mot de passe")))
        self.ctrl_repertoire.SetToolTip(wx.ToolTip(_(u"Saisissez le chemin du répertoire. Exemple : 'www/mesfichiers")))
        self.bouton_test.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour tester les paramètres de connexion"))) 
        
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.label_hote, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_hote, 0, wx.EXPAND, 0)
        grid_sizer_base.Add( (5, 5), 0, 0, 0)
        grid_sizer_base.Add(self.label_identifiant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_identifiant, 0, wx.EXPAND, 0)

        grid_sizer_base.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_base.Add( (5, 5), 0, 0, 0)
        grid_sizer_base.Add(self.label_repertoire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_repertoire, 0, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        grid_sizer_base.AddGrowableCol(4)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        
        sizer.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def OnBoutonTest(self, event):
        dictParametres = self.GetParametres(encoder_mdp=False)
        try :
            ftp = ftplib.FTP(dictParametres["synchro_ftp_hote"], dictParametres["synchro_ftp_identifiant"], dictParametres["synchro_ftp_mdp"])
            ftp.cwd(dictParametres["synchro_ftp_repertoire"])
            ftp.quit()
        except Exception as err :
            dlg = wx.MessageDialog(self, _(u"La connexion n'a pas pu être établie !\n\nVérifiez les paramètres de connexion FTP dans les paramètres de synchronisation."), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(None, _(u"La connexion a été établie avec succès !\n\nLes paramètres de connexion saisis sont valides."), u"Succès", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def GetParametres(self, encoder_mdp=True):
        mdp = self.ctrl_mdp.GetValue()
        if encoder_mdp == True :
            mdp = base64.b64encode(mdp)
        return {"synchro_ftp_hote" : self.ctrl_hote.GetValue(), "synchro_ftp_identifiant" : self.ctrl_identifiant.GetValue(), "synchro_ftp_mdp" : mdp, "synchro_ftp_repertoire" : self.ctrl_repertoire.GetValue()}
    
    def SetParametres(self, dictDonnees={}):
        if "synchro_ftp_hote" in dictDonnees : 
            self.ctrl_hote.SetValue(dictDonnees["synchro_ftp_hote"])
        if "synchro_ftp_identifiant" in dictDonnees : 
            self.ctrl_identifiant.SetValue(dictDonnees["synchro_ftp_identifiant"])
        if "synchro_ftp_mdp" in dictDonnees : 
            mdp = base64.b64decode(dictDonnees["synchro_ftp_mdp"])
            self.ctrl_mdp.SetValue(mdp)
        if "synchro_ftp_repertoire" in dictDonnees : 
            self.ctrl_repertoire.SetValue(dictDonnees["synchro_ftp_repertoire"])

    def Validation(self):
        return True

# ---------------------------------------------------------------------------------------------------------------------------

class Page_cryptage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        self.label_activer = wx.StaticText(self, -1, _(u"Activer :"))
        self.check_activer = wx.CheckBox(self, -1, u"")
        self.label_info = wx.StaticText(self, -1, _(u"(Les données envoyées seront cryptées avec le mot de passe)"))
        self.label_info.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.label_info.SetForegroundColour(wx.Colour(150, 150, 150))
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, u"")
        self.ctrl_mdp.SetMinSize((200, -1)) 
        
        # Propriétés
        self.check_activer.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer/désactiver le cryptage des données envoyées")))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Saisissez le mot de passe qui sera utiliser pour crypter les données envoyées et décrypter les données reçues. Recommandé si transfert sur internet.")))
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_activer, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.check_activer, 0, 0, 0)
        sizer2.Add(self.label_info, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_base.Add(sizer2, 0, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_mdp, 0, 0, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def GetParametres(self):
        mdp = base64.b64encode(self.ctrl_mdp.GetValue())
        return {"synchro_cryptage_activer" : self.check_activer.GetValue(), "synchro_cryptage_mdp" : mdp}
    
    def SetParametres(self, dictDonnees={}):
        if "synchro_cryptage_activer" in dictDonnees : 
            self.check_activer.SetValue(dictDonnees["synchro_cryptage_activer"])
        if "synchro_cryptage_mdp" in dictDonnees : 
            mdp = base64.b64decode(dictDonnees["synchro_cryptage_mdp"])
            self.ctrl_mdp.SetValue(mdp)

    def Validation(self):
        if self.check_activer.GetValue() == True and self.ctrl_mdp.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un mot de passe valide pour le cryptage !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_mdp.SetFocus()
            return False
        return True
    
    
# ---------------------------------------------------------------------------------------------------------------------------

class Page_archivage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        self.label_activer = wx.StaticText(self, -1, _(u"Activer :"))
        self.check_activer = wx.CheckBox(self, -1, u"")
        self.label_info = wx.StaticText(self, -1, _(u"(Au-delà du nombre de jours indiqués, les fichiers de synchronisation archivés seront supprimés)"))
        self.label_info.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.label_info.SetForegroundColour(wx.Colour(150, 150, 150))
        self.label_delai = wx.StaticText(self, -1, _(u"Nbre jours :"))
        self.ctrl_delai = wx.SpinCtrl(self, -1, "30")
        
        # Propriétés
        self.check_activer.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour activer la suppression automatique des fichiers de synchronisation archivés obsolètes")))
        self.ctrl_delai.SetToolTip(wx.ToolTip(_(u"Sélectionnez un nombre de jours")))
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_activer, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.check_activer, 0, 0, 0)
        sizer2.Add(self.label_info, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_base.Add(sizer2, 0, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.label_delai, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_delai, 0, 0, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def GetParametres(self):
        return {"synchro_archivage_activer" : self.check_activer.GetValue(), "synchro_archivage_delai" : self.ctrl_delai.GetValue()}
    
    def SetParametres(self, dictDonnees={}):
        if "synchro_archivage_activer" in dictDonnees : 
            self.check_activer.SetValue(dictDonnees["synchro_archivage_activer"])
        if "synchro_archivage_delai" in dictDonnees : 
            self.ctrl_delai.SetValue(dictDonnees["synchro_archivage_delai"])
    
    def Validation(self):
        if self.check_activer.GetValue() == True and self.ctrl_delai.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nombe de jours !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_delai.SetFocus()
            return False
        return True
        

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Notebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT) 
        self.dictPages = {}

        self.listePages = [
            (_(u"serveur"), _(u"Serveur WIFI/Internet"), _(u"Page_serveur(self)"), "Server.png"),
            (_(u"ftp"), _(u"FTP"), _(u"Page_ftp(self)"), "Ftp.png"),
            (_(u"cryptage"), _(u"Cryptage"), _(u"Page_cryptage(self)"), "Cle.png"),
            (_(u"archivage"), _(u"Archivage"), _(u"Page_archivage(self)"), "Poubelle.png"),
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            exec("self.img%d = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s'), wx.BITMAP_TYPE_PNG))" % (index, imgPage))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            exec("self.page%d = %s" % (index, ctrlPage))
            exec("self.AddPage(self.page%d, u'%s')" % (index, labelPage))
            exec("self.SetPageImage(%d, self.img%d)" % (index, index))
            exec("self.dictPages['%s'] = {'ctrl' : self.page%d, 'index' : %d}" % (codePage, index, index))
            index += 1
    
    def GetPageActive(self):
        index = self.GetSelection() 
        return self.GetPage(self.listePages[index][0])
        
    def GetPage(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)
    
    def GetParametres(self):
        dictParametres = {}
        for codePage, dictPage in self.dictPages.items() :
            for key, valeur in dictPage["ctrl"].GetParametres().items() :
                dictParametres[key] = valeur
        return dictParametres
    
    def SetParametres(self, dictParametres={}):
        for codePage, dictPage in self.dictPages.items() :
            dictPage["ctrl"].SetParametres(dictParametres)

    def ImportationParametres(self):
        dictDefaut = self.GetParametres() 
        dictParametres = UTILS_Config.GetParametres(dictDefaut)
        self.SetParametres(dictParametres)
    
    def Validation(self):
        for codePage, dictPage in self.dictPages.items() :
            if dictPage["ctrl"].Validation() == False :
                self.AffichePage(codePage)
                return False
        return True


# ---------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici synchroniser les données avec Nomadhys, l'application nomade pour Noethys. Choisissez une méthode de synchronisation (Serveur direct WIFI/Internet ou FTP ou Manuel) puis renseignez les paramètres. Cliquez sur le bouton 'Lire les données' pour importer les données.")
        titre = _(u"Synchroniser Nomadhys")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Nomadhys.png")
        
        # Paramètres
        self.box_parametres = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = Notebook(self)

        # Transfert
        self.box_transfert = wx.StaticBox(self, -1, _(u"Transfert manuel"))
        self.ctrl_mode = CTRL_Mode(self)
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer"), cheminImage="Images/32x32/Fleche_haut.png")
        self.bouton_recevoir = CTRL_Bouton_image.CTRL(self, texte=_(u"Recevoir"), cheminImage="Images/32x32/Fleche_bas.png")

        # Lecture
        self.box_lecture = wx.StaticBox(self, -1, _(u"Importation des données"))
        self.ctrl_fichiers = OL_Synchronisation_fichiers.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_recherche = OL_Synchronisation_fichiers.CTRL_Outils(self, listview=self.ctrl_fichiers, afficherCocher=True)
        self.check_archives = wx.CheckBox(self, -1, _(u"Afficher les archives"))
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_lecture = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Lire_donnees.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_googleplay = CTRL_Bouton_image.CTRL(self, texte=_(u"Télécharger Nomadhys"), cheminImage="Images/32x32/Googleplay.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckArchives, self.check_archives)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRecevoir, self.bouton_recevoir)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLecture, self.bouton_lecture)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGoogleplay, self.bouton_googleplay)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Init
        self.SuppressionArchives() 
        
        self.ctrl_parametres.ImportationParametres()
        self.ctrl_mode.SetMode(UTILS_Config.GetParametre("synchro_mode_favori", defaut="ftp"))
        self.ctrl_fichiers.MAJ() 
        
        wx.CallAfter(self.AfficheAvertissement)

    def __set_properties(self):
        self.ctrl_mode.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode de transfert souhaité pour envoyer/recevoir des données manuellement")))
        self.check_archives.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher également dans la liste les fichiers de synchronisation archivés")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer manuellement le fichier de données")))
        self.bouton_recevoir.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour recevoir manuellement un fichier de données")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste des fichiers à synchroniser")))
        self.bouton_lecture.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lire le contenu des fichiers sélectionnés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_googleplay.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la page de téléchargement de Nomadhys sur Google Play")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à des outils")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((700, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Transfert
        box_transfert = wx.StaticBoxSizer(self.box_transfert, wx.VERTICAL)
        grid_sizer_transfert = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_transfert.Add(self.ctrl_mode, 1, wx.EXPAND, 0)
        grid_sizer_transfert.Add(self.bouton_envoyer, 0, wx.EXPAND, 0)
        grid_sizer_transfert.Add(self.bouton_recevoir, 0, wx.EXPAND, 0)
        grid_sizer_transfert.AddGrowableCol(0)
        box_transfert.Add(grid_sizer_transfert, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_transfert, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # lecture
        box_donnees = wx.StaticBoxSizer(self.box_lecture, wx.VERTICAL)
        grid_sizer_lecture = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_lecture.Add(self.ctrl_fichiers, 1, wx.EXPAND, 0)
        
        grid_sizer_outils = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_outils.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_outils.Add(self.check_archives, 0, wx.EXPAND | wx.LEFT, 10)
        
        grid_sizer_lecture.Add(grid_sizer_outils, 1, wx.EXPAND, 0)
        grid_sizer_lecture.Add( (0, 0), 1, wx.EXPAND, 0)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)
        sizer2.Add(self.bouton_lecture, 1, wx.EXPAND|wx.LEFT, 10)
        
        grid_sizer_lecture.Add(sizer2, 1, wx.EXPAND, 0)
        grid_sizer_lecture.AddGrowableRow(0)
        grid_sizer_lecture.AddGrowableCol(0)
        box_donnees.Add(grid_sizer_lecture, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_donnees, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_googleplay, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()  
    
    def OnCheckArchives(self, event=None):
        self.ctrl_fichiers.inclure_archives = self.check_archives.GetValue()
        self.ctrl_fichiers.MAJ() 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("SynchroniserNomadhys")
    
    def OnBoutonGoogleplay(self, event):
        import webbrowser 
        webbrowser.open("http://play.google.com/store/apps/details?id=org.nomadhys.nomadhys&hl=fr")
        
    def OnBoutonOutils(self, event):
        menuPop = UTILS_Adaptations.Menu()
        
        item = wx.MenuItem(menuPop, 10, _(u"Purger le répertoire FTP"), _(u"Supprimer uniquement les fichiers liés à ce fichier de données du répertoire FTP"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_purger_ftp, id=10)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def On_outils_purger_ftp(self, event):
        """ Supprime tous les fichiers du répertoire FTP """
        hote = UTILS_Config.GetParametre("synchro_ftp_hote", defaut="")
        identifiant = UTILS_Config.GetParametre("synchro_ftp_identifiant", defaut="")
        mdp = base64.b64decode(UTILS_Config.GetParametre("synchro_ftp_mdp", defaut=""))
        repertoire = UTILS_Config.GetParametre("synchro_ftp_repertoire", defaut="")
        IDfichier = FonctionsPerso.GetIDfichier()
        
        nbreFichiersSupprimes = 0
        try :
            ftp = ftplib.FTP(hote, identifiant, mdp)
            ftp.cwd(repertoire)
            # Récupère la liste des fichiers de synchronisation présents sur le répertoire FTP
            for nomFichier in ftp.nlst() :
                if IDfichier in nomFichier and (nomFichier.endswith(UTILS_Export_nomade.EXTENSION_CRYPTE) or nomFichier.endswith(UTILS_Export_nomade.EXTENSION_DECRYPTE)) :
                    ftp.delete(nomFichier)
                    nbreFichiersSupprimes += 1
            ftp.quit()
        except Exception as err :
            print(err)
            dlg = wx.MessageDialog(self, _(u"La connexion FTP n'a pas pu être établie !\n\nVérifiez les paramètres de connexion FTP dans les paramètres de synchronisation."), "Erreur ", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        dlg = wx.MessageDialog(self, _(u"%d fichiers ont été supprimés dans le répertoire FTP !") % nbreFichiersSupprimes, "Suppression ", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
    def OnBoutonFermer(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        self.MemoriseParametres() 
        self.EndModal(wx.ID_CANCEL)
    
    def OnClose(self, event):
        if self.ctrl_parametres.Validation() == False :
            return False
        self.MemoriseParametres() 
        event.Skip()
        
    def MemoriseParametres(self):
        # Paramètres
        dictParametres = self.ctrl_parametres.GetParametres()
        UTILS_Config.SetParametres(dictParametres)
        # Mode favori
        UTILS_Config.SetParametre("synchro_mode_favori", self.ctrl_mode.GetMode())
    
    def OnBoutonEnvoyer(self, event):
        self.MemoriseParametres() 
        export = UTILS_Export_nomade.Export()
        nomFichier = export.Run(afficherDlgAttente=True)
        if nomFichier == None :
            return False
        if self.ctrl_mode.GetMode() == "ftp" :
            export.EnvoyerVersFTP(nomFichier)
        if self.ctrl_mode.GetMode() == "fichier" :
            export.EnvoyerVersRepertoire(nomFichier)
        
    def OnBoutonRecevoir(self, event):
        self.MemoriseParametres() 
        if self.ctrl_mode.GetMode() == "ftp" :
            self.RecevoirFTP() 
        if self.ctrl_mode.GetMode() == "fichier" :
            self.RecevoirFichier() 

    def RecevoirFichier(self):
        """ Réception des fichiers manuels """
        standardPath = wx.StandardPaths.Get()
        wildcard = _(u"Fichiers de synchronisation (*%s, *%s)|*%s;*%s|Tous les fichiers (*.*)|*.*") % (UTILS_Export_nomade.EXTENSION_CRYPTE, UTILS_Export_nomade.EXTENSION_DECRYPTE, UTILS_Export_nomade.EXTENSION_CRYPTE, UTILS_Export_nomade.EXTENSION_DECRYPTE)
        dlg = wx.FileDialog(None, message=_(u"Sélectionnez un fichier de synchronisation"), defaultDir=standardPath.GetDocumentsDir(),  wildcard=wildcard, style=wx.FD_OPEN)
        chemin = None
        if dlg.ShowModal() == wx.ID_OK:
            chemin = dlg.GetPath()
        dlg.Destroy()
        if chemin != None :
            nomFichier = os.path.basename(chemin)
            shutil.copyfile(chemin, UTILS_Fichiers.GetRepSync(nomFichier))
            # Analyse du fichier
            dlgAttente = wx.BusyInfo(_(u"Analyse du fichier synchronisation..."), self)
            resultat = AnalyserFichier(nomFichier, typeTransfert="manuel") 
            del dlgAttente
            if resultat == True :
                dlg = wx.MessageDialog(self, _(u"Le fichier a été réceptionné avec succès !"), u"Succès", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

        # MAJ de la liste des fichiers
        self.ctrl_fichiers.MAJ()

    def RecevoirFTP(self):
        """ Réception des fichiers FTP """
        # Récupération des paramètres
        hote = UTILS_Config.GetParametre("synchro_ftp_hote", defaut="")
        identifiant = UTILS_Config.GetParametre("synchro_ftp_identifiant", defaut="")
        mdp = base64.b64decode(UTILS_Config.GetParametre("synchro_ftp_mdp", defaut=""))
        repertoire = UTILS_Config.GetParametre("synchro_ftp_repertoire", defaut="")
        IDfichier = FonctionsPerso.GetIDfichier()
        
        # Récupération des fichiers
        listeFichiersRecus = []
        dlgAttente = wx.BusyInfo(_(u"Récupération des fichiers de synchronisation depuis un répertoire FTP..."), self)
        try :
            ftp = ftplib.FTP(hote, identifiant, mdp)
            ftp.cwd(repertoire)
            # Récupère la liste des fichiers de synchronisation présents sur le répertoire FTP
            for nomFichier in ftp.nlst() :
                if nomFichier.startswith("actions_%s" % IDfichier) and (nomFichier.endswith(UTILS_Export_nomade.EXTENSION_CRYPTE) or nomFichier.endswith(UTILS_Export_nomade.EXTENSION_DECRYPTE)) :
                    try :
                        tailleFichier = ftp.size(nomFichier)
                    except :
                        ftp.voidcmd('TYPE I')
                        tailleFichier = ftp.size(nomFichier)
                    ftp.retrbinary("RETR %s" % nomFichier, open(UTILS_Fichiers.GetRepSync(nomFichier), "wb").write)
                    listeFichiersRecus.append((nomFichier, tailleFichier))
            ftp.quit()
        except Exception as err :
            print(err)
            del dlgAttente
            dlg = wx.MessageDialog(self, _(u"La connexion FTP n'a pas pu être établie !\n\nVérifiez les paramètres de connexion FTP dans les paramètres de synchronisation."), "Erreur ", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        del dlgAttente
            
        # Analyse du fichier
        ftp = ftplib.FTP(hote, identifiant, mdp)
        ftp.cwd(repertoire)

        for nomFichier, tailleFichier in listeFichiersRecus :
            
            # Analyse du fichier
            dlgAttente = wx.BusyInfo(_(u"Analyse du fichier synchronisation..."), self)
            resultat = AnalyserFichier(nomFichier=nomFichier, tailleFichier=tailleFichier, typeTransfert="ftp") 
            del dlgAttente
            
            # Suppression du fichier dans le répertoire FTP
            ftp.delete(nomFichier) 
            
        ftp.quit()
        
        # MAJ de la liste des fichiers
        self.ctrl_fichiers.MAJ()
        
    
    def OnBoutonActualiser(self, event):
        self.ctrl_fichiers.MAJ()
        
    def OnBoutonLecture(self, event):
        tracks = self.ctrl_fichiers.GetTracksCoches() 
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun fichier de synchronisation à lire !"), "Erreur ", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        listeFichiers = []
        for track in tracks :
            listeFichiers.append(track.nom_fichier)
            
        from Dlg import DLG_Synchronisation_donnees
        dlg = DLG_Synchronisation_donnees.Dialog(self, listeFichiers=listeFichiers)
        dlg.ShowModal() 
        dlg.Destroy()
        
        # MAJ de la liste des fichiers
        self.ctrl_fichiers.MAJ()
        
    def SuppressionArchives(self):
        """ Supprime les archives obsolètes du répertoire Sync """
        synchro_archivage_activer = UTILS_Config.GetParametre("synchro_archivage_activer", defaut=0)
        synchro_archivage_delai = UTILS_Config.GetParametre("synchro_archivage_delai", defaut=30)
        
        # Vérifie que la suppression auto de l'archivage est activé
        if synchro_archivage_activer == 0 :
            return False
        
        # Lecture des fichiers du répertoire SYNC
        for nomFichier in os.listdir(UTILS_Fichiers.GetRepSync()) :
            if nomFichier.startswith("actions_") and nomFichier.endswith(".archive") :
                nomFichierCourt = nomFichier.replace(".dat", "").replace(".archive", "")
                
                # Lecture Horodatage
                horodatage = nomFichierCourt.split("_")[2]
                horodatage = UTILS_Dates.HorodatageEnDatetime(horodatage)
                dateDuJour = datetime.datetime.now() 
                nbreJours = (dateDuJour - horodatage).days
                
                # Suppression
                if nbreJours > synchro_archivage_delai :
                    os.remove(UTILS_Fichiers.GetRepSync(nomFichier))
    
    def AfficheAvertissement(self):
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="synchronisation_nomadhys", valeur=False) == True :
            return

        from Dlg import DLG_Message_html
        texte = u"""
<CENTER><IMG SRC="Static/Images/32x32/Information.png">
<BR><BR>
<FONT SIZE=2>
<B>Avertissement</B>
<BR><BR>
Cette nouvelle fonctionnalité est expérimentale.
<BR><BR>
Il est conseillé de tester son efficacité et sa stabilité dans un fichier test avant de l'utiliser dans votre fichier de données. 
<BR><BR>
Merci de signaler tout bug rencontré dans la rubrique "Signaler un bug " du forum de Noethys.
</FONT>
</CENTER>
"""
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Information"), nePlusAfficher=True)
        dlg.ShowModal()
        nePlusAfficher = dlg.GetEtatNePlusAfficher()
        dlg.Destroy()
        if nePlusAfficher == True :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="synchronisation_nomadhys", valeur=nePlusAfficher)
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()