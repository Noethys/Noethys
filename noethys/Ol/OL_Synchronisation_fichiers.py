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

import GestionDB
import FonctionsPerso
from Utils import UTILS_Dates
from Utils import UTILS_Fichiers

from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, donnees):
        self.nom_fichier = donnees["nom_fichier"]
        self.taille_fichier = donnees["taille_fichier"]
        self.horodatage = donnees["horodatage"]
        self.nom_appareil = donnees["nom_appareil"]
        self.ID_appareil = donnees["ID_appareil"]
        self.detail_actions = donnees["detail_actions"]
        
        self.appareil = u"%s (%s)" % (self.nom_appareil, self.ID_appareil) 
        
        if self.nom_fichier.endswith("archive") :
            self.archive = True
        else :
            self.archive = False
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.inclure_archives = False
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Récupération du IDfichier
        IDfichier = FonctionsPerso.GetIDfichier()
        
        # Lecture des fichiers du répertoire SYNC
        listeFichiers = os.listdir(UTILS_Fichiers.GetRepSync())
        
        listeListeView = []
        for nomFichier in listeFichiers :
            if nomFichier.startswith("actions_%s" % IDfichier) and (nomFichier.endswith(".dat") or (nomFichier.endswith(".archive") and self.inclure_archives == True)) :
                nomFichierCourt = nomFichier.replace(".dat", "").replace(".archive", "")
                
                # Taille fichier
                tailleFichier = os.path.getsize(UTILS_Fichiers.GetRepSync(nomFichier))
                
                # Horodatage
                horodatage = nomFichierCourt.split("_")[2]
                horodatage = UTILS_Dates.HorodatageEnDatetime(horodatage)
                                
                # Lecture du contenu du fichier
                DB = GestionDB.DB(suffixe=None, nomFichier=UTILS_Fichiers.GetRepSync(nomFichier), modeCreation=False)
                req = """SELECT IDparametre, nom, valeur 
                FROM parametres;"""
                DB.ExecuterReq(req)
                listeParametres = DB.ResultatReq()
                dictParametres = {}
                for IDparametre, nom, valeur in listeParametres :
                    dictParametres[nom] = valeur
                
                if dictParametres.has_key("nom_appareil") == False :
                    dictParametres["nom_appareil"] = "Appareil inconnu"
                if dictParametres.has_key("ID_appareil") == False :
                    dictParametres["ID_appareil"] = "IDAppareil inconnu"

                liste_details_actions = []
                
                req = """SELECT IDconso, horodatage, action
                FROM consommations;"""
                DB.ExecuterReq(req)
                listeConsommations = DB.ResultatReq()
                if len(listeConsommations) > 0 :
                    liste_details_actions.append(_(u"%d actions sur les consommations") % len(listeConsommations))
                
                req = """SELECT IDmemo, horodatage, action
                FROM memo_journee;"""
                DB.ExecuterReq(req)
                listeMemosJournees = DB.ResultatReq()
                if len(listeMemosJournees) > 0 :
                    liste_details_actions.append(_(u"%d actions sur les mémos journaliers") % len(listeMemosJournees))

                DB.Close() 
                
                detail_actions = ", ".join(liste_details_actions)
                if detail_actions == "" :
                    detail_actions = _(u"Aucune action")
                    
                dictTemp = {"nom_fichier" : nomFichier, "taille_fichier" : tailleFichier, "nom_appareil" : dictParametres["nom_appareil"], "ID_appareil" : dictParametres["ID_appareil"], "horodatage" : horodatage, "detail_actions" : detail_actions}
                listeListeView.append(Track(dictTemp))

        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            if track.archive == True :
                listItem.SetTextColour((180, 180, 180))

        def FormateHorodatage(horodatage):
            return horodatage.strftime("%d/%m/%Y  %H:%M:%S")
        
        def FormateTailleFichier(taille):
            return FonctionsPerso.Formate_taille_octets(taille)
            
        liste_Colonnes = [
            ColumnDefn(_(u"Date génération"), "left", 130, "horodatage", typeDonnee="texte", stringConverter=FormateHorodatage),
            ColumnDefn(_(u"Appareil (ID)"), "left", 130, "appareil", typeDonnee="texte"),
            ColumnDefn(_(u"Contenu du fichier"), "left", 285, "detail_actions", typeDonnee="texte"),
            ColumnDefn(_(u"Nom du fichier"), "left", 285, "nom_fichier", typeDonnee="texte"),
            ColumnDefn(_(u"Taille"), "left", 70, "taille_fichier", typeDonnee="entier", stringConverter=FormateTailleFichier),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucun fichier"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
        self.CocheListeTout()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Archiver
        item = wx.MenuItem(menuPop, 10, _(u"Archiver le fichier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Poubelle.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Archiver, id=10)
        if len(self.GetSelectedObjects()) == 0 :
            item.Enable(False)

        menuPop.AppendSeparator()

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
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Archiver(self, event):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment archiver ce fichier ?"), _(u"Archivage"), wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_YES :
            track = self.GetSelectedObjects()[0]
            nomFichier = track.nom_fichier
            IDappareil = track.ID_appareil
            
            DB = GestionDB.DB()
            # Renommage des fichiers
            os.rename(UTILS_Fichiers.GetRepSync(nomFichier), UTILS_Fichiers.GetRepSync(nomFichier.replace(".dat", ".archive")))
            # Mémorisation de l'archivage dans la base
            nomFichierTemp = nomFichier.replace(".dat", "").replace(".archive", "")
            IDarchive = DB.ReqInsert("nomade_archivage", [("nom_fichier", nomFichierTemp), ("ID_appareil", IDappareil), ("date", datetime.date.today())])
            DB.Close()
            
        # Actualisation de la liste
        self.MAJ() 
        
    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des fichiers à synchroniser"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des fichiers à synchroniser"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des fichiers à synchroniser"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des fichiers à synchroniser"))
    
    def GetTracksCoches(self):
        return self.GetCheckedObjects()
        
        
        

# -------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
