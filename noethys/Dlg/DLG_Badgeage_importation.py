#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import sys
import datetime
from Ctrl import CTRL_Bandeau
import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.filebrowsebutton as filebrowse

try :
    import xlrd
except :
    pass

try:
    import unicodecsv as csv
except:
    from Outils import unicodecsvpy2 as csv

import GestionDB
from Ctrl import CTRL_Saisie_date


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try :
    from Utils import UTILS_CS1504
except:
    pass
from Utils import UTILS_Config


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def Purger():
    """ Purge de l'archivage """
    texte = _(u"La purge des archives de badgeages imprtés vous permet de réduire la taille de la base de données. Il est conseillé d'y procéder une fois que vous n'avez plus besoin des archives (soit quelques mois après).\n\nCommencez par sélectionner une date maximale de badgeage.")
    dlg = wx.MessageDialog(None, texte, _(u"Purge du journal de badgeage"), wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
    reponse = dlg.ShowModal()
    dlg.Destroy()
    if reponse != wx.ID_OK:
        return False

    # Sélection d'une date
    from Dlg import DLG_calendrier_simple
    dlg = DLG_calendrier_simple.Dialog(None)
    if dlg.ShowModal() == wx.ID_OK :
        date = dlg.GetDate()
        dlg.Destroy()
    else :
        dlg.Destroy()
        return False
    
    # Demande de confirmation
    dlg = wx.MessageDialog(None, _(u"Confirmez-vous la purge des archives de badgeage jusqu'au %s inclus ?") % DateEngFr(str(date)), _(u"Purge des archives de badgeage"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal()
    dlg.Destroy()
    if reponse != wx.ID_YES:
        return False
    
    # Suppression
    DB = GestionDB.DB()
    req = """DELETE FROM badgeage_archives WHERE date<='%s';""" % str(date)
    DB.ExecuterReq(req)
    DB.Commit()
    DB.Close() 
    
    # Fin
    dlg = wx.MessageDialog(None, _(u"Purge des archives de badgeage terminée."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()



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
        if self.URL == "tout" :
            self.parent.ctrl_donnees.CocheTout() 
        if self.URL == "rien" :
            self.parent.ctrl_donnees.CocheRien() 
        self.UpdateLink()
        
# -------------------------------------------------------------------------------------------------------------------------


class Track(object):
    def __init__(self, dictDonnees):
        self.codebarres = dictDonnees["codebarres"]
        self.date = dictDonnees["date"] # Au format Datetime
        self.heure = dictDonnees["heure"]
    
class CTRL_Donnees(FastObjectListView):
    def __init__(self, *args, **kwds):
        FastObjectListView.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def InitModel(self, listeDonnees=[]):
        self.donnees = []
        for codebarres, date, heure in listeDonnees :
            self.donnees.append(Track({"codebarres":codebarres, "date":date, "heure":heure}))
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(dateDD):
            return DateComplete(dateDD)
            
        liste_Colonnes = [
            ColumnDefn(_(u"Code-barres"), 'center', 135, "codebarres"),
            ColumnDefn(_(u"Date"), 'center', 200, "date", stringConverter=FormateDate),
            ColumnDefn(_(u"Heure"), 'center', 80, "heure"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune donnée"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, listeDonnees=[]):
        self.InitModel(listeDonnees)
        self.InitObjectListView()
        self.CocheTout() 

    def CocheTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)

        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 60, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 70, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des données"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des données"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des données"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des données"))


# ---------------------------------------------------------------------------------------------------------------------------
class CTRL_Choix_port(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        if "linux" in sys.platform :
            listeDonnees = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB4", "/dev/ttyUSB5", "/dev/ttyUSB6", "/dev/ttyUSB7", "/dev/ttyUSB8", "/dev/ttyUSB9"]
        else :
            if "darwin" in sys.platform :
                listeDonnees = ["/dev/cu.usbserial"]
            else :
                listeDonnees = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"]
        listeItems = []
        self.dictDonnees = {}
        index = 0
        indexDefaut = None
        for label in listeDonnees :
            code = label
            self.dictDonnees[index] = { "code" : code, "label" : label}
            listeItems.append(label)
            index += 1
        
        # Remplissage
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)

    def SetID(self, code=None):
        if code == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["code"] == code :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["code"]
    
    def GetNom(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["label"]

# -------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_appareil(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeDonnees = [
            ("cs1504", _(u"Symbol CS1504")),
            ("opn-2001", _(u"Opticon OPN-2001")),
            ]
        listeItems = []
        self.dictDonnees = {}
        index = 0
        indexDefaut = None
        for code, label in listeDonnees :
            self.dictDonnees[index] = { "code" : code, "label" : label}
            listeItems.append(label)
            index += 1
        
        # Remplissage
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)

    def SetID(self, code=None):
        if code == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["code"] == code :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["code"]
    
    def GetNom(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["label"]

# -------------------------------------------------------------------------------------------------------------------------




class Page_scanner(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.label_port = wx.StaticText(self, -1, _(u"Port :"))
        self.ctrl_port = CTRL_Choix_port(self)
        self.check_vider = wx.CheckBox(self, -1, _(u"Vider après importation"))
        self.bouton_outils = wx.Button(self, -1, _(u"Outils"))
        self.label_appareil = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_appareil = CTRL_Choix_appareil(self)
        self.check_heure_auto = wx.CheckBox(self, -1, _(u"Réglage de l'heure auto."))
        self.check_heure_auto.SetValue(True) 
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        
        # Propriétés
        self.ctrl_port.SetToolTip(wx.ToolTip(_(u"Sélectionnez le port sur lequel est branché le scanner")))
        self.check_vider.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour vider l'appareil après l'importation")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux commandes spéciales du scanner")))
        self.ctrl_appareil.SetToolTip(wx.ToolTip(_(u"Sélectionnez le nom du scanner")))
        self.check_heure_auto.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour que le réglage de l'heure de l'appareil soit automatique")))

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=10)
        grid_sizer_base.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_port, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_vider, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_base.Add(self.label_appareil, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_appareil, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_heure_auto, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.AddGrowableCol(3)
        sizer.Add(grid_sizer_base, 0, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer)
        grid_sizer_base.Fit(self)
        
        # Init
        port = UTILS_Config.GetParametre("scanner_memoire_port", None)
        modele = UTILS_Config.GetParametre("scanner_memoire_appareil", None)
        vidage = UTILS_Config.GetParametre("scanner_memoire_vidage", False)
        heure_auto = UTILS_Config.GetParametre("scanner_memoire_heure_auto", True)
        self.ctrl_port.SetID(port)
        self.ctrl_appareil.SetID(modele)
        self.check_vider.SetValue(vidage)
        self.check_heure_auto.SetValue(heure_auto)

    def OnBoutonOutils(self, event): 
        # Création du menu Outils
        menuPop = UTILS_Adaptations.Menu()

        ID_VIDER_MEMOIRE = wx.Window.NewControlId()
        menuPop.AppendItem(wx.MenuItem(menuPop, ID_VIDER_MEMOIRE, _(u"Vider la mémoire"), _(u"Vider la mémoire du scanner")))
        self.Bind(wx.EVT_MENU, self.OnOutil, id=ID_VIDER_MEMOIRE)

        ID_REGLER_HEURE = wx.Window.NewControlId()
        menuPop.AppendItem(wx.MenuItem(menuPop, ID_REGLER_HEURE, _(u"Régler l'horloge du scanner"), _(u"Régler l'horloge du scanner")))
        self.Bind(wx.EVT_MENU, self.OnOutil, id=ID_REGLER_HEURE)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def OnOutil(self, event):
        ID = event.GetId() 

        # Init scanner
        scanner = self.Connexion() 
        if scanner == False :
            return False
        
        if ID == ID_VIDER_MEMOIRE :
            self.ViderMemoire(scanner) 
            
        if ID == ID_REGLER_HEURE :
            self.ReglerHeure(scanner)
        
        # Déconnecte scanner
        self.Deconnexion(scanner)
        
    def Lire(self):
        """ Lecture des données """
        scanner = self.Connexion() 
        if scanner == False :
            return False
        
        # Lecture de l'heure
        try :
            scanner.get_time()
        except Exception as err:
            pass
        
        # Réglage de l'heure du scanner
        if self.check_heure_auto.GetValue() == True :
            resultat = self.ReglerHeure(scanner)
            if resultat == False :
                self.Deconnexion(scanner)

        # Lecture des codes-barres
        try :
            listeBarcodes = scanner.get_barcodes()
        except Exception as err:
            print("Erreur de lecture du scanner :", err)
            dlg = wx.MessageDialog(self, _(u"Noethys n'arrive pas à lire les données du scanner. Essayez de le déconnecter et le reconnecter...\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            scanner.close() 
            return False
        
        listeDonnees = []
        index = 0
        for symbology, codebarres, timestamp in listeBarcodes :
            try :
                date = datetime.date(timestamp.year, timestamp.month, timestamp.day) 
                heure = u"%02d:%02d" % (timestamp.hour, timestamp.minute)
                listeDonnees.append((codebarres, date, heure))
            except Exception as err:
                print("Erreur de lecture du code-barres %d :" % index+1, err)
                dlg = wx.MessageDialog(None, _(u"Erreur de lecture du code-barres %d : %s\n\nVoulez-vous quand-même continuer ?") % (index+1, err), _(u"Erreur"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)
                if dlg.ShowModal() != wx.ID_YES :
                    dlg.Destroy()
                    return False
                dlg.Destroy()
                self.Deconnexion(scanner)
                return False
            
            index += 1
                
        # Vidage de la mémoire
        if self.check_vider.GetValue() == True and len(listeBarcodes) > 0 :
            self.ViderMemoire(scanner) 
            
        # Déconnecte le scanner
        self.Deconnexion(scanner)
        return listeDonnees
        
    def Connexion(self):
        """ Connexion au scanner """
        port = self.ctrl_port.GetID() 
        if port == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un port dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        appareil = self.ctrl_appareil.GetID() 
        if appareil == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un appareil dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Connexion à l'appareil
        if (appareil == "cs1504") or (appareil == "opn-2001") :
            try :
                scanner = UTILS_CS1504.CS1504(port)
                scanner.interrogate()
            except Exception as err:
                dlg = wx.MessageDialog(self, _(u"Noethys n'arrive pas à se connecter à l'appareil."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        return scanner
    
    def Deconnexion(self, scanner):
        try :
            scanner.power_down()
            del scanner
        except Exception as err :
            print(err)
    
    def ReglerHeure(self, scanner=None):
        try :
            scanner.set_time()
        except Exception as err:
            dlg = wx.MessageDialog(self, _(u"Noethys n'arrive pas à se régler l'heure du scanner.\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def ViderMemoire(self, scanner=None):
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment vider la mémoire du scanner ?"), _(u"Vider le scanner"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES :
            try :
                scanner.clear_barcodes()
            except Exception as err:
                dlg = wx.MessageDialog(self, _(u"Noethys n'arrive pas à vider l'appareil.\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
        dlg.Destroy()

    def MemoriseParametres(self):
        UTILS_Config.SetParametre("scanner_memoire_port", self.ctrl_port.GetID())
        UTILS_Config.SetParametre("scanner_memoire_appareil", self.ctrl_appareil.GetID())
        UTILS_Config.SetParametre("scanner_memoire_vidage", self.check_vider.GetValue())
        UTILS_Config.SetParametre("scanner_memoire_heure_auto", self.check_heure_auto.GetValue())


class Page_excel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.label_fichier = wx.StaticText(self, -1, _(u"Fichier :"))
        wildcard = _(u"Fichiers Excel (*.xls)|*.xls|All files (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        self.ctrl_fichier = filebrowse.FileBrowseButton(self, -1, labelText=u"", buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier de données"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard, startDirectory=cheminDefaut)
        self.label_infos = wx.StaticText(self, -1, _(u"Versions acceptées : 2003, 2002, XP, 2000, 97, 95, 5.0, 4.0, 3.0."))
        self.label_infos.SetForegroundColour((130, 130, 130))
        
        # Propriétés
        self.ctrl_fichier.SetToolTip(wx.ToolTip(_(u"Sélectionnez le fichier source")))
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=3)
        grid_sizer_base.Add(self.label_fichier, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_fichier, 0, wx.EXPAND, 0)
        grid_sizer_base.Add( (5, 5), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.label_infos, 0, wx.LEFT, 8)
        grid_sizer_base.AddGrowableCol(1)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def Lire(self):
        """ Lecture des données """
        nomFichier = self.ctrl_fichier.GetValue()
        if len(nomFichier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un fichier de données à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if os.path.isfile(nomFichier) == False :
            dlg = wx.MessageDialog(self, _(u"L'emplacement fichier que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Lecture du fichier XLS
        try :
            classeur = xlrd.open_workbook(nomFichier)
        except :
            dlg = wx.MessageDialog(self, _(u"Le fichier Excel ne semble pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Sélection de la feuille
        feuille = None
        feuilles = classeur.sheet_names()
        if len(feuilles) == 1 :
            feuille = classeur.sheet_by_index(0)
        else :
            # Demande la feuille à ouvrir
            dlg = wx.SingleChoiceDialog(None, _(u"Veuillez sélectionner la feuille du classeur qui comporte les données à importer :"), _(u"Sélection d'une feuille"), feuilles, wx.CHOICEDLG_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                feuille = classeur.sheet_by_index(dlg.GetSelection())
            dlg.Destroy()
        
        # Lecture des données de la feuille
        listeDonnees = []
        try :
            for num_ligne in range(feuille.nrows):
                # Codebarres
                codebarres = feuille.cell(rowx=num_ligne, colx=0).value
                # Date
                dateTuple = xlrd.xldate_as_tuple(feuille.cell(rowx=num_ligne, colx=1).value, classeur.datemode)
                date = datetime.date(*dateTuple[:3])
                # Heure
                dateTuple = xlrd.xldate_as_tuple(feuille.cell(rowx=num_ligne, colx=2).value, classeur.datemode)
                heure = u"%02d:%02d" % (dateTuple[3], dateTuple[4])
                # Mémorisation
                listeDonnees.append((codebarres, date, heure))
        except Exception as err :
            listeDonnees = []
            dlg = wx.MessageDialog(self, _(u"Noethys n'a pas réussi à lire les données !\n\nErreur : %s.\n\nNotez que les colonnes du fichier Excel doivent être les suivantes : 1. Code-barres 2. Date, 3. Heure.") % err, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        return listeDonnees
        
        


class Page_csv(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.label_fichier = wx.StaticText(self, -1, _(u"Fichier :"))
        wildcard = _(u"Fichiers CSV ou TXT|*.csv;*.txt|Tous les fichiers (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        self.ctrl_fichier = filebrowse.FileBrowseButton(self, -1, labelText=u"", buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier de données"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard, startDirectory=cheminDefaut)
        self.label_delimiteur = wx.StaticText(self, -1, _(u"Délimiteur :"))
        self.ctrl_delimiteur = wx.Choice(self, -1, choices=[_(u"Virgule (,)"), _(u"Point-virgule (;)"), _(u"Tabulation")])
        self.listeDelimiteurs = [",", ";", "\t"]
        
        self.label_format = wx.StaticText(self, -1, _(u"Format :"))
        self.ctrl_format = wx.TextCtrl(self, -1, "")
        
        # Propriétés
        self.ctrl_fichier.SetToolTip(wx.ToolTip(_(u"Sélectionnez le fichier source")))
        self.ctrl_delimiteur.SetToolTip(wx.ToolTip(_(u"Sélectionnez le symbole délimiteur des champs")))
        self.ctrl_delimiteur.SetSelection(1)
        self.ctrl_format.SetToolTip(wx.ToolTip(_(u"Saisissez le format de la ligne de la source : \n\n- CODE : Code-barre\n- AAAA : Année\n- MM : Mois\n- JJ : Jour\n- HH : Heures\n- MN : Minutes\n- SS : Secondes\n- X : Autre\n\nExemple : 'CODE;AAAA-MM-JJ HH:MN:SS;' \n")))
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=3)
        grid_sizer_base.Add(self.label_fichier, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_fichier, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_delimiteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_2 = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=3)
        grid_sizer_2.Add(self.ctrl_delimiteur, 0, 0, 0)
        grid_sizer_2.Add( (5, 5), 0, wx.LEFT, 8)
        grid_sizer_2.Add(self.label_format, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.ctrl_format, 1, wx.EXPAND, 0)
        grid_sizer_2.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_2, 0, wx.LEFT|wx.EXPAND, 8)
        
        grid_sizer_base.AddGrowableCol(1)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        # Init contrôles
        self.ctrl_delimiteur.SetStringSelection(UTILS_Config.GetParametre("badgeage_importation_csv_delimiteur", defaut=";"))
        self.ctrl_format.SetValue(UTILS_Config.GetParametre("badgeage_importation_csv_format", defaut=u"CODE;AAAA-MM-JJ HH:MN:SS;"))
        

    def Lire(self):
        """ Lecture des données """
        nomFichier = self.ctrl_fichier.GetValue()
        if len(nomFichier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un fichier de données à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if os.path.isfile(nomFichier) == False :
            dlg = wx.MessageDialog(self, _(u"L'emplacement fichier que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        selectionDelimiteur = self.ctrl_delimiteur.GetSelection() 
        if selectionDelimiteur == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un symbole délimiteur pour ce fichier !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        delimiteur = self.listeDelimiteurs[selectionDelimiteur]

        format = self.ctrl_format.GetValue()
        if len(format) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un format !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Décodage du format
        champs = [ ("AAAA", _(u"l'année")), ("MM", _(u"le mois")), ("JJ", _(u"le jour")), ("CODE", _(u"le code-barres")), ("HH", _(u"les heures")), ("MN", _(u"les minutes")) ]
        dictFormat = {}
        for code, label in champs :
            if code not in format :
                dlg = wx.MessageDialog(self, _(u"Le format doit obligatoirement comporter l'expression '%s' afin d'identifier %s dans les lignes !") % (code, label), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            indexColonne = 0
            for texteColonne in format.split(delimiteur) :
                try :
                    position = texteColonne.index(code)
                    dictFormat[code] = (indexColonne, position)
                except :
                    pass
                indexColonne += 1        
        
        # Lecture du fichier CSV
        try :
            fichier = csv.reader(open(nomFichier,"rb"), encoding="iso-8859-15", delimiter=delimiteur)
        except :
            dlg = wx.MessageDialog(self, _(u"Le fichier CSV ne semble pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False        
        
        # Lecture des données
        listeDonnees = []
        try :
            for ligne in fichier :

                def Decodage(code):
                    col, pos = dictFormat[code]
                    if code == "CODE" :
                        valeur = ligne[col]
                    else :
                        taille = len(code)
                        valeur = ligne[col][pos:pos+taille]
                    return valeur           

                # Code-barres
                codebarres = Decodage("CODE")
                # Date
                date = datetime.date(int(Decodage("AAAA")), int(Decodage("MM")), int(Decodage("JJ")))
                # Heure
                heure = u"%02d:%02d" % (int(Decodage("HH")), int(Decodage("MN")))
                # Mémorisation
                listeDonnees.append((codebarres, date, heure))
        except Exception as err :
            listeDonnees = []
            dlg = wx.MessageDialog(self, _(u"Noethys n'a pas réussi à lire les données !\n\nVérifiez peut-être le format de la ligne.\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        return listeDonnees

    def MemoriseParametres(self):
        UTILS_Config.SetParametre("badgeage_importation_csv_delimiteur", self.ctrl_delimiteur.GetStringSelection())
        UTILS_Config.SetParametre("badgeage_importation_csv_format", self.ctrl_format.GetValue())




class Page_archives(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.label_date_archivage = wx.StaticText(self, -1, _(u"Date de l'archivage :"))
        self.ctrl_date_archivage = CTRL_Saisie_date.Date2(self)
        self.label_date_badgeage = wx.StaticText(self, -1, _(u"Date du badgeage :"))
        self.ctrl_date_badgeage = CTRL_Saisie_date.Date2(self)
                
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=5)
        grid_sizer_base.Add(self.label_date_archivage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_date_archivage, 0, 0, 0)
        grid_sizer_base.Add(self.label_date_badgeage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_date_badgeage, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(1)
        sizer.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def Lire(self):
        """ Lecture des données """
        date_archivage = self.ctrl_date_archivage.GetDate() 
        date_badgeage = self.ctrl_date_badgeage.GetDate() 
        
        if date_archivage != None and date_badgeage == None :
            conditions = "WHERE date_archivage='%s'" % str(date_archivage)
        elif date_archivage == None and date_badgeage != None :
            conditions = "WHERE date='%s'" % str(date_badgeage)
        elif date_archivage != None and date_badgeage != None :
            conditions = "WHERE date='%s' AND date_archivage='%s'" % (str(date_badgeage), str(date_archivage))
        else :
            conditions = ""
        
        # Lecture des archives
        DB = GestionDB.DB()
        req = """SELECT date_archivage, codebarres, date, heure
        FROM badgeage_archives 
        %s
        ORDER BY date, heure; """ % conditions
        DB.ExecuterReq(req)
        listeBadgeages = DB.ResultatReq()
        listeDonnees = []
        for date_archivage, codebarres, date, heure in listeBadgeages :
            date = DateEngEnDateDD(date)
            listeDonnees.append((codebarres, date, heure))
        DB.Close() 
                
        return listeDonnees


class Notebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT) 
        self.dictPages = {}

        self.listePages = [
            (_(u"scanner"), _(u"Scanner à mémoire"), _(u"Page_scanner(self)"), "Scanner_memoire.png"),
            (_(u"excel"), _(u"Fichier Excel"), _(u"Page_excel(self)"), "Excel.png"),
            (_(u"csv"), _(u"Fichier CSV"), _(u"Page_csv(self)"), "Facture.png"),
            (_(u"archives"), _(u"Archives"), _(u"Page_archives(self)"), "Database.png"),
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            setattr(self, "img%d" % index, il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s') % imgPage, wx.BITMAP_TYPE_PNG)))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            setattr(self, "page%s" % index, eval(ctrlPage))
            self.AddPage(getattr(self, "page%s" % index), labelPage)
            self.SetPageImage(index, getattr(self, "img%d" % index))
            self.dictPages[codePage] = {'ctrl': getattr(self, "page%d" % index), 'index': index}
            index += 1
    
    def GetPageActive(self):
        index = self.GetSelection() 
        return self.GetPage(self.listePages[index][0])
        
    def GetPage(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

# ---------------------------------------------------------------------------------------------------------------------------------------------
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Pour importer des badgeages, commencez par sélectionner une source, cliquez sur le bouton 'Lire les données' puis sur le bouton 'Importer' pour importer les données cochées.")
        titre = _(u"Importation de badgeages")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Badgeage.png")
        
        # Source
        self.box_source_staticbox = wx.StaticBox(self, -1, _(u"Source des données"))
        self.box_donnees_staticbox = wx.StaticBox(self, -1, _(u"Données"))
        self.ctrl_source = Notebook(self)
        self.bouton_lire = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Lire_source_badgeage.png"), wx.BITMAP_TYPE_ANY))

        # Données
        self.ctrl_donnees = CTRL_Donnees(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_ANY))
        self.check_archiver = wx.CheckBox(self, -1, _(u"Archiver les données avant importation"))
        self.check_archiver.SetValue(True)
        
        self.hyper_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, "|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonLire, self.bouton_lire)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init
        self.ctrl_donnees.MAJ() 

    def __set_properties(self):
        self.bouton_lire.SetToolTip(wx.ToolTip(_(u"Cliquer ici pour lire la source des données")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu avant impression de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour faire un export Excel de la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour faire un export Texte de la liste")))
        self.check_archiver.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour archiver les données")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer l'importation")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((570, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Source
        box_source = wx.StaticBoxSizer(self.box_source_staticbox, wx.VERTICAL)
        box_source.Add(self.ctrl_source, 1, wx.ALL|wx.EXPAND, 10)
        box_source.Add(self.bouton_lire, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_base.Add(box_source, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Données
        box_donnees = wx.StaticBoxSizer(self.box_donnees_staticbox, wx.VERTICAL)
        grid_sizer_donnees = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_donnees.Add(self.ctrl_donnees, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_donnees.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.check_archiver, 0, 0, 0)
        grid_sizer_options.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_options.Add(self.label_separation, 0, 0, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_donnees.Add(grid_sizer_options, 1, wx.EXPAND, 0)
        grid_sizer_donnees.AddGrowableRow(0)
        grid_sizer_donnees.AddGrowableCol(0)
        box_donnees.Add(grid_sizer_donnees, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_donnees, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()  

    def OnBoutonLire(self, event): 
        listeDonnees = self.ctrl_source.GetPageActive().Lire()
        if listeDonnees == False :
            return
        # Envoi des données au Listview
        self.ctrl_donnees.MAJ(listeDonnees)

    def OnBoutonApercu(self, event): 
        self.ctrl_donnees.Apercu(None)

    def OnBoutonImprimer(self, event): 
        self.ctrl_donnees.Imprimer(None)

    def OnBoutonExcel(self, event): 
        self.ctrl_donnees.ExportExcel(None)

    def OnBoutonTexte(self, event): 
        self.ctrl_donnees.ExportTexte(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Importerdesbadgeages")

    def OnBoutonAnnuler(self, event):
        self.MemoriseParametres() 
        self.EndModal(wx.ID_CANCEL)
    
    def MemoriseParametres(self):
        self.ctrl_source.GetPage("scanner").MemoriseParametres()
        self.ctrl_source.GetPage("csv").MemoriseParametres()
    
    def ArchiverBadgeages(self):
        """ Archiver les badgeages importés """
        DB = GestionDB.DB()
        
        # Vérifie si les badgeages ne sont pas déjà saisis
        req = """SELECT date_archivage, codebarres, date, heure
        FROM badgeage_archives 
        ORDER BY date, heure; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeBadgeagesExistants = []
        for date_archivage, codebarres, date, heure in listeDonnees :
            date = DateEngEnDateDD(date)
            listeBadgeagesExistants.append((codebarres, date, heure))
        
        listeTracksValides = []
        listeTracksNonValides = [] 
        
        listeTracks = self.GetDonnees() 
        for track in listeTracks :
            if (track.codebarres, track.date, track.heure) in listeBadgeagesExistants :
                listeTracksNonValides.append(track)
            else :
                listeTracksValides.append(track)

        # Enregistrement
        listeAjouts = []
        for track in listeTracksValides :
            listeAjouts.append((str(datetime.date.today()), track.codebarres, str(track.date), track.heure))
        DB.Executermany("INSERT INTO badgeage_archives (date_archivage, codebarres, date, heure) VALUES (?, ?, ?, ?)", listeAjouts, commit=True)
        DB.Close() 
        
        # Confirmation
        texte = _(u"%d codes-barres ont été archivés avec succès.") % len(listeTracksValides)
        if len(listeTracksNonValides) > 0 :
            texte += _(u"\n\nMais %d codes-barres déjà archivés ont été exclus.") % len(listeTracksNonValides)
        dlg = wx.MessageDialog(self, texte, _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def OnBoutonOk(self, event): 
        """ Validation """
        # Récupération des données à importer sous forme de tracks
        listeTracks = self.ctrl_donnees.GetTracksCoches() 
        if len(listeTracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune donnée à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Archivage
        if self.check_archiver.GetValue() == True :
            self.ArchiverBadgeages() 
            
        # Fermeture
        self.MemoriseParametres() 
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        """ Renvoie les données au format Tracks """
        return self.ctrl_donnees.GetTracksCoches() 


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()