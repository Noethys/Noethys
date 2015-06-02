#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import decimal
import GestionDB
import Image
import os
import cStringIO

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

try: import psyco; psyco.full()
except: pass




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


        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.inclus = kwds.pop("inclus", True)
        self.selectionPossible = kwds.pop("selectionPossible", True)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.tracks = []
        self.numColonneTri = 1
        self.ordreAscendant = True
        
        self.tailleImagesMaxi = (132/4.0, 72/4.0) #(132/2.0, 72/2.0)
        self.tailleImagesMini = (16, 16)
        self.afficheImages = True
        self.imageDefaut = "Images/Special/Image_non_disponible.png"

        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        if self.selectionPossible == True :
            self.Deplacer()
    
    def Deplacer(self):
        if len(self.Selection()) == 0 :
            if self.inclus == True :
                message = _(u"Vous devez d'abord sélectionner un règlement à retirer du dépôt !")
            else:
                message = _(u"Vous devez d'abord sélectionner un règlement disponible à ajouter au dépôt !")
            dlg = wx.MessageDialog(self, message, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if self.inclus == True :
            track.inclus = False
        else:
            track.inclus = True
        index = self.GetIndexOf(track)
        if index == len(self.donnees)-1 :
            if len(self.donnees) > 1 :
                nextTrack = self.GetObjectAt(index-1)
            else:
                nextTrack = None
        else:
            nextTrack = self.GetObjectAt(index+1)
        self.GetGrandParent().MAJListes(self.tracks, selectionTrack=track, nextTrack=nextTrack)
        
    def InitModel(self, tracks=None, IDcompte=None, IDmode=None):
        if tracks != None :
            self.tracks = tracks
        listeTracks = []
        for track in self.tracks :
            valide = True
            if track.inclus != self.inclus :
                valide = False
            # Filtre compte
            if IDcompte != None and track.IDcompte != IDcompte :
                valide = False
            # Filtre Mode
            if IDmode != None and track.IDmode != IDmode :
                valide = False
                
            if valide == True :
                listeTracks.append(track)
        self.donnees = listeTracks
    
    def GetLabelListe(self, texte=_(u"règlements")):
        """ Récupère le nombre de règlements et le montant total de la liste """
        nbre = 0
        montant = 0.0
        for track in self.donnees :
            nbre += 1
            montant += track.montant
        # Label de staticbox
        label = u"%d %s (%.2f %s)" % (nbre, texte, montant, SYMBOLE)
        return label          

    def GetImagefromBuffer(self, buffer=None, taille=None):
        """ Récupère une image mode ou émetteur depuis un buffer """            
        # Recherche de l'image
        if buffer != None :
            io = cStringIO.StringIO(buffer)
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
            bmp = img.Rescale(width=taille[0], height=taille[1], quality=wx.IMAGE_QUALITY_HIGH) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        else:
            # Si aucune image est trouvée, on prend l'image par défaut
            if os.path.isfile(self.imageDefaut):
                bmp = wx.Bitmap(self.imageDefaut, wx.BITMAP_TYPE_ANY) 
                bmp = bmp.ConvertToImage()
                bmp = bmp.Rescale(width=taille[0], height=taille[1], quality=wx.IMAGE_QUALITY_HIGH) 
                bmp = bmp.ConvertToBitmap()
                return bmp
            return None
    
    def ConvertTailleImage(self, bitmap=None, taille=None):
        """ Convertit la taille d'une image """
        img = wx.EmptyImage(taille[0], taille[1], True)
        img.SetRGBRect((0, 0, taille[0], taille[1]), 255, 255, 255)
        bmp = img.ConvertToBitmap()
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.DrawBitmap(bitmap, taille[0]/2.0-bitmap.GetSize()[0]/2.0, taille[1]/2.0-bitmap.GetSize()[1]/2.0)
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Règle la taille des images
        self.afficheImages = UTILS_Config.GetParametre("depots_afficher_images", defaut=True)
        if self.afficheImages == True :
            taille = self.tailleImagesMaxi
        else :
            taille = self.tailleImagesMini
        
        # Image list
        dictImages = {"standard":{}, "modes":{}, "emetteurs":{} }
        imageList = wx.ImageList(taille[0], taille[1])
        
        # Images standard
        dictImages["standard"]["vert"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG), taille))    
        dictImages["standard"]["orange"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG), taille))   
        dictImages["standard"]["rouge"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG), taille))    
        dictImages["standard"]["ok"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG), taille))    
        dictImages["standard"]["erreur"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG), taille))    
        dictImages["standard"]["attente"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Attente.png", wx.BITMAP_TYPE_PNG), taille))    
        dictImages["standard"]["avis_depot_oui"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG), taille))    
        dictImages["standard"]["avis_depot_non"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap("Images/16x16/Emails_exp_gris.png", wx.BITMAP_TYPE_PNG), taille))    

        # Images Modes
        if self.afficheImages == True :
            
            DB = GestionDB.DB()
            req = """SELECT modes_reglements.IDmode, modes_reglements.image FROM modes_reglements"""
            DB.ExecuterReq(req)
            listeModes = DB.ResultatReq()
            for IDmode, buffer in listeModes :
                bmp = self.GetImagefromBuffer(buffer, taille)
                dictImages["modes"][IDmode] = imageList.Add(bmp)            

            # Images Emetteurs
            req = """SELECT emetteurs.IDemetteur, emetteurs.image FROM emetteurs"""
            DB.ExecuterReq(req)
            listeEmetteurs = DB.ResultatReq()
            for IDemetteur, buffer in listeEmetteurs :
                bmp = self.GetImagefromBuffer(buffer, taille)
                dictImages["emetteurs"][IDemetteur] = imageList.Add(bmp)            
            
            self.SetImageLists(imageList, imageList)
            DB.Close()
        
        def GetImage(track):
            return dictImages[track.IDmode]
        
        def GetImageMode(track):
            if dictImages["modes"].has_key(track.IDmode) :
                return dictImages["modes"][track.IDmode]
            else :
                return None

        def GetImageEmetteur(track):
            if dictImages["emetteurs"].has_key(track.IDemetteur) :
                return dictImages["emetteurs"][track.IDemetteur]
            else :
                return None

        def GetImageVentilation(track):
            if track.montant_ventilation == None :
                return dictImages["standard"]["rouge"]
            resteAVentiler = decimal.Decimal(str(track.montant)) - decimal.Decimal(str(track.montant_ventilation))
            if resteAVentiler == decimal.Decimal(str("0.0")) :
                return dictImages["standard"]["vert"]
            if resteAVentiler > decimal.Decimal(str("0.0")) :
                return dictImages["standard"]["orange"]
            if resteAVentiler < decimal.Decimal(str("0.0")) :
                return dictImages["standard"]["rouge"]

        def GetImageDepot(track):
            if track.IDdepot == None :
                if track.encaissement_attente == 1 :
                    return dictImages["standard"]["attente"]
                else:
                    return dictImages["standard"]["erreur"]
            else:
                return dictImages["standard"]["ok"]

        def GetImageDiffere(track):
            if track.date_differe == None :
                return None
            if track.date_differe <= datetime.date.today() :
                return dictImages["standard"]["ok"]
            else:
                return dictImages["standard"]["erreur"]

        def GetImageAttente(track):
            if track.encaissement_attente == True :
                return dictImages["standard"]["attente"]
            return None

        def GetImageAvisDepot(track):
            if track.avis_depot != None :
                return dictImages["standard"]["avis_depot_oui"]
            if track.email_depots!= None :
                return dictImages["standard"]["avis_depot_non"]
            return None

        def FormateDateLong(dateDD):
            return DateComplete(dateDD)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)
        
        def FormateAttente(attente):
            if attente == True :
                return _(u"Attente !")
            return ""

        def rowFormatter(listItem, track):
            # Si Observations
            if track.observations != "" :
                listItem.SetTextColour((0, 102, 205))
            # Si en attente
            if track.encaissement_attente == True :
                listItem.SetTextColour((255, 0, 0))
            # Si date différé est supérieure à la date d'aujourd'hui
            if track.date_differe != None :
                if track.date_differe > datetime.date.today() :
                    listItem.SetTextColour((255, 0, 0))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDreglement", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 80, "date", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Mode"), 'left', 120, "nom_mode", typeDonnee="texte", imageGetter=GetImageMode),
            ColumnDefn(_(u"Emetteur"), 'left', 145, "nom_emetteur", typeDonnee="texte", imageGetter=GetImageEmetteur),
            ColumnDefn(_(u"Numéro"), 'left', 60, "numero_piece", typeDonnee="texte"),
            ColumnDefn(_(u"Quittancier"), 'left', 65, "numero_quittancier", typeDonnee="texte"),
            ColumnDefn(_(u"Payeur"), 'left', 160, "nom_payeur", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            #ColumnDefn(_(u"Ventilé"), 'right', 80, "montant_ventilation", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            ColumnDefn(_(u"Avis"), 'left', 35, "avis_depot", typeDonnee="date", stringConverter=FormateDateCourt, imageGetter=GetImageAvisDepot),
            ColumnDefn(_(u"Compte"), 'left', 100, "nom_compte", typeDonnee="texte"),
            ColumnDefn(_(u"Différé"), 'left', 85, "date_differe", typeDonnee="date", stringConverter=FormateDateCourt), #, imageGetter=GetImageDiffere),
            ColumnDefn(_(u"Attente"), 'left', 65, "encaissement_attente", typeDonnee="texte", stringConverter=FormateAttente), #, imageGetter=GetImageAttente),
            ColumnDefn(_(u"Observations"), 'left', 200, "observations", typeDonnee="texte"),
            ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        if self.inclus == True :
            self.SetEmptyListMsg(_(u"Aucun règlement dans ce dépôt"))
        else:
            self.SetEmptyListMsg(_(u"Aucun règlement disponible"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self, tracks=None, ID=None, selectionTrack=None, nextTrack=None, IDcompte=None, IDmode=None):
        self.InitModel(tracks, IDcompte, IDmode)
        self.InitObjectListView()
        # Sélection d'un item
        if selectionTrack != None :
            self.SelectObject(selectionTrack, deselectOthers=True, ensureVisible=True)
            if self.GetSelectedObject() == None :
                self.SelectObject(nextTrack, deselectOthers=True, ensureVisible=True)
                
##        if ID == None :
##            self.DefileDernier() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDreglement
                
        # Création du menu contextuel
        menuPop = wx.Menu()

##        # Item Modifier
##        item = wx.MenuItem(menuPop, 10, _(u"Modifier"))
##        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Modifier, id=10)
##        if noSelection == True : item.Enable(False)
##                
##        # Item Supprimer
##        item = wx.MenuItem(menuPop, 20, _(u"Supprimer"))
##        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
##        if noSelection == True : item.Enable(False)
##                
##        menuPop.AppendSeparator()
    
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

    def GetDetailReglements(self):
        # Récupération des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.donnees :
            if track.inclus == True or self.inclus == False :
                # Montant total
                nbreTotal += 1
                # Nbre total
                montantTotal += track.montant
                # Détail
                if dictDetails.has_key(track.IDmode) == False :
                    dictDetails[track.IDmode] = { "label" : track.nom_mode, "nbre" : 0, "montant" : 0.0}
                dictDetails[track.IDmode]["nbre"] += 1
                dictDetails[track.IDmode]["montant"] += track.montant
        # Création du texte
        texte = _(u"%d règlements (%.2f €) : ") % (nbreTotal, montantTotal)
        for IDmode, dictDetail in dictDetails.iteritems() :
            texteDetail = u"%d %s (%.2f €), " % (dictDetail["nbre"], dictDetail["label"], dictDetail["montant"])
            texte += texteDetail
        if len(dictDetails) > 0 :
            texte = texte[:-2] + u"."
        else:
            texte = texte[:-7] 
        return texte

    def Impression(self):
        # Récupère l'intitulé du compte
        if self.GetGrandParent().GetName() == "DLG_Saisie_depot" :
            txtIntro = self.GetGrandParent().GetLabelParametres()
        else :
            txtIntro = u""
        # Récupère le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetDetailReglements() 
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des règlements"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
        return prt
        
    def Apercu(self, event):
        self.Impression().Preview()

    def Imprimer(self, event):
        self.Impression().Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des règlements"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des règlements"))

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun règlement à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDreglement = track.IDreglement
        import DLG_Saisie_reglement
        dlg = DLG_Saisie_reglement.Dialog(self, IDcompte_payeur=None, IDreglement=IDreglement)      
        if dlg.ShowModal() == wx.ID_OK:
            if self.GetGrandParent().GetName() == "DLG_Saisie_depot" :
                self.MAJ(selectionTrack=track) 
            if self.GetGrandParent().GetName() == "DLG_Saisie_depot_ajouter" :
                self.GetGrandParent().MAJListes(self.tracks, selectionTrack=track)
        dlg.Destroy() 

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun règlement à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDreglement = self.Selection()[0].IDreglement
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce règlement ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("reglements", "IDreglement", IDreglement)
            DB.ReqDEL("ventilation", "IDreglement", IDreglement)
            DB.Close() 
            self.GetGrandParent().MAJListes(self.tracks)
        dlg.Destroy()












# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un règlement..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nom_mode" : {"mode" : "nombre", "singulier" : _(u"règlement"), "pluriel" : _(u"règlements"), "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, inclus=True, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
