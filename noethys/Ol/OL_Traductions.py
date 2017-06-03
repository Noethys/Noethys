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
import os
import shelve
from Utils import UTILS_Fichiers
from Utils import UTILS_Interface
from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter




class Track(object):
    def __init__(self, dictDonnees={}):
        self.texte = dictDonnees["texte"]
        self.traduction_initiale = dictDonnees["traduction_initiale"]
        self.traduction_perso = dictDonnees["traduction_perso"]
        self.listeFichiers = dictDonnees["listeFichiers"]
        self.nbreFichiers = len(self.listeFichiers)
        self.listeFichiersStr = ", ".join(self.listeFichiers)
        
        self.dirty = False
    
    def MAJ(self):
        self.traduction = ""
        if self.traduction_initiale != "" :
            self.traduction = self.traduction_initiale
        if self.traduction_perso != "" :
            self.traduction = self.traduction_perso
            
            

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.code = kwds.pop("code", None)
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        # Image list
        self.imgDirty = self.AddNamedImages("valide", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))


    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def GetTraductionsExistantes(self):
        """ Recherche le fichier de langage par défaut ".lang" puis un éventuel fichier perso ".xlang" """
        if self.code == None : return {}, {}
        dictTraductionsInitiales = {}
        dictTraductionsPerso = {}

        for extension, rep, dictTemp in [("lang", Chemins.GetStaticPath("Lang"), dictTraductionsInitiales), ("xlang", UTILS_Fichiers.GetRepLang(), dictTraductionsPerso)] :
            nomFichier = os.path.join(rep, u"%s.%s" % (self.code, extension))
            if os.path.isfile(nomFichier) :
                fichier = shelve.open(nomFichier, "r")
                for key, valeur in fichier.iteritems() :
                    dictTemp[key] = valeur
                fichier.close()
        return dictTraductionsInitiales, dictTraductionsPerso

    def GetTracks(self):
        """ Récupération des données """
        # Récupération des textes originaux
        dictTextes = {}
        fichier = shelve.open(Chemins.GetStaticPath("Databases/Textes.dat"), "r")
        for texte, listeFichiers in fichier.iteritems() :
            dictTextes[texte] = listeFichiers
        fichier.close()
        
        # Récupération des traductions existantes
        dictTraductionsInitiales, dictTraductionsPerso = self.GetTraductionsExistantes() 
        
        # Regroupement des prestations par label
        listeListeView = []
        for texte, listeFichiers in dictTextes.iteritems() :
            traduction_initiale = ""
            traduction_perso = ""
            if dictTraductionsInitiales.has_key(texte) : 
                traduction_initiale = dictTraductionsInitiales[texte]
            if dictTraductionsPerso.has_key(texte) : 
                traduction_perso = dictTraductionsPerso[texte]
            dictDonnees = {"texte" : texte, "traduction_initiale" : traduction_initiale, "traduction_perso" : traduction_perso, "listeFichiers" : listeFichiers}
            track = Track(dictDonnees)
            track.MAJ() 
            listeListeView.append(track)
        return listeListeView

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def GetImageDirty(track):
            if track.traduction_perso != "" : 
                return self.imgDirty
            return None

        liste_Colonnes = [
            ColumnDefn("", "left", 0, "", typeDonnee="texte"), 
            ColumnDefn(_(u"Texte original"), "left", 200, "texte", typeDonnee="texte", isSpaceFilling=True), 
            ColumnDefn(_(u"Traduction"), "left", 200, "traduction", typeDonnee="texte", imageGetter=GetImageDirty, isSpaceFilling=True), 
            ColumnDefn(_(u"Nbre Fichiers"), "left", 85, "nbreFichiers", typeDonnee="entier"), 
            ColumnDefn(_(u"Fichiers associés"), "left", 200, "listeFichiersStr", typeDonnee="texte"),
            ]
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun texte"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()
            
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Création du menu contextuel
        menuPop = wx.Menu()
                
        # Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=10)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donnée à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des traductions"), intro="", total="", format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des traductions"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des traductions"))
    
    def Modifier(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ligne dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Saisie_texte_traduction
        dlg = DLG_Saisie_texte_traduction.Dialog(self, texte=track.texte, traduction=track.traduction)      
        if dlg.ShowModal() == wx.ID_OK:
            traduction = dlg.GetTraduction() 
            track.traduction_perso = traduction
            track.MAJ() 
            self.RefreshObject(track)
        dlg.Destroy() 
        
    def GetDictTraductionsPerso(self):
        dictTraductions = {}
        for track in self.donnees :
            if track.traduction_perso != "" :
                dictTraductions[track.texte] = track.traduction_perso
        return dictTraductions
        
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, code="en_GB", name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ()
        self.bouton1 = wx.Button(panel, -1, "Go")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton1, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton1)

    def OnBouton1(self, event):
        # Get chaines
        tracks = self.myOlv.GetTracksCoches() 
        
        dictFichiers = {}
        for track in tracks :
            for nomFichier in track.listeFichiers :
                if dictFichiers.has_key(nomFichier) == False :
                    dictFichiers[nomFichier] = []
                if track.chaine not in dictFichiers[nomFichier] :
                    dictFichiers[nomFichier].append(track.chaine)
        
        indexFichier = 0
        for nomFichier, listeChaines in dictFichiers.iteritems() :
            print "%d/%d  : %s..." % (indexFichier, len(dictFichiers), nomFichier)
                
            # Ouverture des fichiers
            fichier = open(nomFichier, "r")
            nouveauFichier = open("New/%s" % nomFichier, "w")
            
            for ligne in fichier :
                # Remplacement des chaines
                for chaine in listeChaines :
                    if chaine in ligne : 
                        nouvelleChaine = "_(%s)" % chaine
                        ligne = ligne.replace(chaine, nouvelleChaine)
                    
                # Ecriture du nouveau fichier
                nouveauFichier.write(ligne)
                                    
            # Clôture des fichiers
            fichier.close()
            nouveauFichier.close()
            
            indexFichier += 1
            
        print "fini !!!!!!!!!!!!!!!!!"



def AjoutImport():
    listeFichiers = os.listdir(os.getcwd() + "/New")
    indexFichier = 0
    for nomFichier in listeFichiers :
        if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier not in ("CreateurMAJ.py", "CreateurANNONCES.py") :
            print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)
            
            # Ouverture des fichiers
            fichier = open("New/" + nomFichier, "r")
            nouveauFichier = open("New/New/%s" % nomFichier, "w")
            
            idx = None
            indexLigne = 0
            for ligne in fichier :
                nouveauFichier.write(ligne)
                
                # Insertion de l'import
                if "Licence GNU GPL" in ligne :
                    idx = indexLigne + 2
                
                if idx == indexLigne :
                    nouveauFichier.write("from Utils.UTILS_Traduction import _\n")

                indexLigne += 1
                
                
            # Clôture des fichiers
            fichier.close()
            nouveauFichier.close()
            
        indexFichier += 1
            
    print "fini !!!!!!!!!!!!!!!!!"

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "texte" : {"mode" : "nombre", "singulier" : "texte", "pluriel" : "textes", "alignement" : wx.ALIGN_CENTER},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)
    
if __name__ == '__main__':
##    AjoutImport() 
    
    app = wx.App(0)
    frame_1 = MyFrame(None)
    frame_1.SetSize((900, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
