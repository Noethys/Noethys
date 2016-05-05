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
import os
import datetime

import GestionDB
import FonctionsPerso
import UTILS_Dates
import UTILS_Fichiers
import UTILS_Interface
from ObjectListView import GroupListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, donnees={}, dictIndividus=None, dictUnites=None, dictParametres=None, nomFichier=""):
        self.nomFichier = nomFichier
        self.categorie = donnees["categorie"]
        self.nom_appareil = dictParametres["nom_appareil"]
        self.ID_appareil = dictParametres["ID_appareil"]
        self.statut = None
        self.appareil = u"%s (%s)" % (self.nom_appareil, self.ID_appareil) 
        
        # Consommations
        if self.categorie == "consommation" :
            self.IDconso = donnees["IDconso"]
            self.horodatage = donnees["horodatage"]
            self.action = donnees["action"]
            self.IDindividu = donnees["IDindividu"]
            self.IDactivite = donnees["IDactivite"]
            self.IDinscription = donnees["IDinscription"]
            self.date = donnees["date"]
            self.IDunite = donnees["IDunite"]
            self.IDgroupe = donnees["IDgroupe"]
            self.heure_debut = donnees["heure_debut"]
            self.heure_fin = donnees["heure_fin"]
            self.etat = donnees["etat"]
            self.date_saisie = donnees["date_saisie"]
            self.IDutilisateur = donnees["IDutilisateur"]
            self.IDcategorie_tarif = donnees["IDcategorie_tarif"]
            self.IDcompte_payeur = donnees["IDcompte_payeur"]
            self.quantite = donnees["quantite"]
            self.IDfamille = donnees["IDfamille"]
            self.nomUnite = dictUnites[self.IDunite]
            self.nomIndividu = dictIndividus[self.IDindividu]
            self.detail = _(u"%s %s le %s pour %s") % (self.action.capitalize(), self.nomUnite, UTILS_Dates.DateDDEnFr(self.date), self.nomIndividu)

        # Consommations
        if self.categorie == "memo_journee" :
            self.IDmemo = donnees["IDmemo"]
            self.horodatage = donnees["horodatage"]
            self.action = donnees["action"]
            self.IDindividu = donnees["IDindividu"]
            self.date = donnees["date"]
            self.texte = donnees["texte"]
            self.nomIndividu = dictIndividus[self.IDindividu]
            self.detail = _(u"%s le %s pour %s le texte '%s'") % (self.action.capitalize(), UTILS_Dates.DateDDEnFr(self.date), self.nomIndividu, self.texte)
    
    
    
class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.listeFichiers = kwds.pop("listeFichiers", [])
        self.listeFichiersTrouves = []
        self.dictIDappareil = {}
        self.cacher_doublons = True
        self.index_regroupement = 4
        GroupListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        
        # Lecture Individus
        req = """SELECT IDindividu, nom, prenom
        FROM individus;"""
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        dictIndividus = {}
        for IDindividu, nom, prenom in listeIndividus :
            if prenom == None : prenom = ""
            dictIndividus[IDindividu] = u"%s %s" % (nom, prenom)
        
        # Lecture unités
        req = """SELECT IDunite, nom, abrege
        FROM unites
        ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        dictUnites = {}
        for IDunite, nom, abrege in listeUnites :
            dictUnites[IDunite] = nom
        
        DB.Close() 
        
        
        # Récupération du IDfichier
        IDfichier = FonctionsPerso.GetIDfichier()
        
        # Lecture des fichiers du répertoire SYNC
        listeFichiers = os.listdir(UTILS_Fichiers.GetRepSync())
        
        listeListeView = []
        listeDictTempTraites = []
        for nomFichier in listeFichiers :
            if nomFichier.startswith("actions_%s" % IDfichier) and (nomFichier.endswith(".dat") and self.listeFichiers == None) or (self.listeFichiers != None and nomFichier in self.listeFichiers) :
                nomFichierCourt = nomFichier.replace(".dat", "").replace(".archive", "")
                
                if nomFichier not in self.listeFichiersTrouves :
                    self.listeFichiersTrouves.append(nomFichier) 
                    
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
                
                # Mémorise l'IDappareil
                self.dictIDappareil[nomFichierCourt] = dictParametres["ID_appareil"]
                
                # Lecture des consommations
                req = """SELECT IDconso, horodatage, action, IDindividu, IDactivite, IDinscription, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, date_saisie, IDutilisateur, IDcategorie_tarif, IDcompte_payeur, quantite, IDfamille
                FROM consommations;"""
                DB.ExecuterReq(req)
                listeConsommations = DB.ResultatReq()
                for IDconso, horodatage, action, IDindividu, IDactivite, IDinscription, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, date_saisie, IDutilisateur, IDcategorie_tarif, IDcompte_payeur, quantite, IDfamille in listeConsommations :
                    horodatage = UTILS_Dates.HorodatageEnDatetime(horodatage, separation="-")
                    date = UTILS_Dates.DateEngEnDateDD(date) 
                    date_saisie = UTILS_Dates.DateEngEnDateDD(date_saisie) 
                    dictTemp = {
                        "categorie" : "consommation", 
                        "IDconso" : IDconso, "horodatage" : horodatage, "action" : action, "IDindividu" : IDindividu, "IDactivite" : IDactivite, "IDinscription" : IDinscription, 
                        "date" : date, "IDunite" : IDunite, "IDgroupe" : IDgroupe, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "etat" : etat, "quantite" : quantite,
                        "date_saisie" : date_saisie, "IDutilisateur" : IDutilisateur, "IDcategorie_tarif" : IDcategorie_tarif, "IDcompte_payeur" : IDcompte_payeur, "IDfamille" : IDfamille, 
                        }
                        
                    # Vérifie que cette action n'est pas déjà dans la liste
                    if dictTemp not in listeDictTempTraites :
                        listeListeView.append(Track(dictTemp, dictIndividus=dictIndividus, dictUnites=dictUnites, dictParametres=dictParametres, nomFichier=nomFichier))
                        if self.cacher_doublons == True :
                            listeDictTempTraites.append(dictTemp)
                    
                # Lecture des mémos journaliers
                req = """SELECT IDmemo, horodatage, action, IDindividu, date, texte
                FROM memo_journee;"""
                DB.ExecuterReq(req)
                listeMemosJournees = DB.ResultatReq()
                for IDmemo, horodatage, action, IDindividu, date, texte in listeMemosJournees :
                    horodatage = UTILS_Dates.HorodatageEnDatetime(horodatage, separation="-")
                    date = UTILS_Dates.DateEngEnDateDD(date) 
                    dictTemp = {
                        "categorie" : "memo_journee", 
                        "IDmemo" : IDmemo, "horodatage" : horodatage, "action" : action, "IDindividu" : IDindividu, 
                        "date" : date, "texte" : texte, 
                        }
                    
                    # Vérifie que cette action n'est pas déjà dans la liste
                    if dictTemp not in listeDictTempTraites :
                        listeListeView.append(Track(dictTemp, dictIndividus=dictIndividus, dictParametres=dictParametres, nomFichier=nomFichier))
                        if self.cacher_doublons == True :
                            listeDictTempTraites.append(dictTemp)
                        
                DB.Close() 

        return listeListeView
      
    def InitObjectListView(self):          
        # Images
        self.imageOk = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imageErreur = self.AddNamedImages("erreur", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))

        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def GetImageStatut(track):
            if track.statut == "ok" : 
                return self.imageOk
            if track.statut == "erreur" : 
                return self.imageErreur
            return None

        def FormateHorodatage(horodatage):
            return horodatage.strftime("%d/%m/%Y  %H:%M:%S")
        
        def Capitalize(texte):
            return texte.capitalize() 
        
        def FormateCategorie(categorie):
            if categorie == "consommation" : return _(u"Consommation")
            if categorie == "memo_journee" : return _(u"Mémo journalier")
            return "?"
        
        liste_Colonnes = [
            ColumnDefn(_(u"Horodatage"), "left", 130, "horodatage", typeDonnee="texte", stringConverter=FormateHorodatage),
            ColumnDefn(_(u"Statut"), "left", 50, "statut", typeDonnee="texte", imageGetter=GetImageStatut),
            ColumnDefn(_(u"Catégorie"), "left", 120, "categorie", typeDonnee="texte", stringConverter=FormateCategorie),
            ColumnDefn(_(u"Action"), "left", 100, "action", typeDonnee="texte", stringConverter=Capitalize),
            ColumnDefn(_(u"Individu"), "left", 150, "nomIndividu", typeDonnee="texte"),
            ColumnDefn(_(u"Détail"), "left", 300, "detail", typeDonnee="texte"),
            ColumnDefn(_(u"Appareil (ID)"), "left", 130, "appareil", typeDonnee="texte"),
            ColumnDefn(_(u"Nom du fichier"), "left", 290, "nomFichier", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        
        # Regroupement
        self.SetAlwaysGroupByColumn(self.index_regroupement)
        self.SetShowGroups(True)
        self.useExpansionColumn = False
        self.showItemCounts = False

        self.SetEmptyListMsg(_(u"Aucune action"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[2])
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
        menuPop = wx.Menu()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)

        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des données à synchroniser"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des données à synchroniser"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des données à synchroniser"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des données à synchroniser"))
    
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
        self.myOlv = ListView(panel, id=-1, listeFichiers=None, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
