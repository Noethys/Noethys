#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import six
import datetime
import decimal
import GestionDB
from PIL import Image
import os
from Utils import UTILS_Titulaires
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter




def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
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
        self.imageDefaut = Chemins.GetStaticPath("Images/Special/Image_non_disponible.png")

        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)

        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def OnClickColonne(self, indexColonne=None, ascendant=True):
        if self.inclus == False :
            try :
                self.GetGrandParent().ctrl_tri.Select(indexColonne)
                if ascendant :
                    self.GetGrandParent().ctrl_ordre.Select(0)
                else :
                    self.GetGrandParent().ctrl_ordre.Select(1)
            except :
                pass

    def OnItemActivated(self,event):
        if self.selectionPossible == True :
            self.Deplacer()
    
    def Deplacer(self):
        if len(self.Selection()) == 0 :
            if self.inclus == True :
                message = _(u"Vous devez d'abord s�lectionner un r�glement � retirer du d�p�t !")
            else:
                message = _(u"Vous devez d'abord s�lectionner un r�glement disponible � ajouter au d�p�t !")
            dlg = wx.MessageDialog(self, message, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        tracks = self.Selection()
        for track in tracks:
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
        self.GetGrandParent().MAJListes(self.tracks, selectionTrack=tracks, nextTrack=nextTrack)
        
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
    
    def GetLabelListe(self, texte=_(u"r�glements")):
        """ R�cup�re le nombre de r�glements et le montant total de la liste """
        nbre = 0
        montant = 0.0
        for track in self.donnees :
            nbre += 1
            montant += track.montant or 0.0
        # Label de staticbox
        label = u"%d %s (%.2f %s)" % (nbre, texte, montant, SYMBOLE)
        return label          

    def GetImagefromBuffer(self, buffer=None, taille=None):
        """ R�cup�re une image mode ou �metteur depuis un buffer """            
        # Recherche de l'image
        if buffer != None :
            io = six.BytesIO(buffer)
            if 'phoenix' in wx.PlatformInfo:
                img = wx.Image(io, wx.BITMAP_TYPE_JPEG)
            else :
                img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
            bmp = img.Rescale(width=taille[0], height=taille[1], quality=wx.IMAGE_QUALITY_HIGH) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        else:
            # Si aucune image est trouv�e, on prend l'image par d�faut
            if os.path.isfile(self.imageDefaut):
                bmp = wx.Bitmap(self.imageDefaut, wx.BITMAP_TYPE_ANY)
                bmp = bmp.ConvertToImage()
                bmp = bmp.Rescale(width=taille[0], height=taille[1], quality=wx.IMAGE_QUALITY_HIGH) 
                bmp = bmp.ConvertToBitmap()
                return bmp
            return None
    
    def ConvertTailleImage(self, bitmap=None, taille=None):
        """ Convertit la taille d'une image """
        if 'phoenix' in wx.PlatformInfo:
            img = wx.Image(taille[0], taille[1], True)
            img.SetRGB((0, 0, taille[0], taille[1]), 255, 255, 255)
        else :
            img = wx.EmptyImage(taille[0], taille[1], True)
            img.SetRGBRect((0, 0, taille[0], taille[1]), 255, 255, 255)
        bmp = img.ConvertToBitmap()
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.DrawBitmap(bitmap, int(taille[0]/2.0-bitmap.GetSize()[0]/2.0), int(taille[1]/2.0-bitmap.GetSize()[1]/2.0))
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # R�gle la taille des images
        self.afficheImages = UTILS_Config.GetParametre("depots_afficher_images", defaut=True)
        if self.afficheImages == True :
            taille = self.tailleImagesMaxi
        else :
            taille = self.tailleImagesMini

        # Image list
        dictImages = {"standard":{}, "modes":{}, "emetteurs":{} }
        imageList = wx.ImageList(taille[0], taille[1])

        # Images standard
        dictImages["standard"]["vert"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["orange"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["rouge"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["ok"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["erreur"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["attente"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attente.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["avis_depot_oui"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG), taille))
        dictImages["standard"]["avis_depot_non"] = imageList.Add(self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp_gris.png"), wx.BITMAP_TYPE_PNG), taille))

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

            DB.Close()

        self.SetImageLists(imageList, imageList)

        # Fl�ches tri
        bmp_haut = self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut_2.png"), wx.BITMAP_TYPE_PNG), taille)
        bmp_bas = self.ConvertTailleImage(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas_2.png"), wx.BITMAP_TYPE_PNG), taille)
        self.RegisterSortIndicators(bmp_haut, bmp_bas)


        def GetImageMode(track):
            if track.IDmode in dictImages["modes"] :
                return dictImages["modes"][track.IDmode]
            else :
                return None

        def GetImageEmetteur(track):
            if track.IDemetteur in dictImages["emetteurs"] :
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
            # Si date diff�r� est sup�rieure � la date d'aujourd'hui
            if track.date_differe != None :
                if track.date_differe > datetime.date.today() :
                    listItem.SetTextColour((255, 0, 0))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDreglement", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 80, "date", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Mode"), 'left', 120, "nom_mode", typeDonnee="texte", imageGetter=GetImageMode),
            ColumnDefn(_(u"Emetteur"), 'left', 145, "nom_emetteur", typeDonnee="texte", imageGetter=GetImageEmetteur),
            ColumnDefn(_(u"Num�ro"), 'left', 60, "numero_piece", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), 'left', 160, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Payeur"), 'left', 160, "nom_payeur", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Avis"), 'left', 110, "avis_depot", typeDonnee="date", stringConverter=FormateDateCourt, imageGetter=GetImageAvisDepot),
            ColumnDefn(_(u"Compte"), 'left', 100, "nom_compte", typeDonnee="texte"),
            ColumnDefn(_(u"Diff�r�"), 'left', 85, "date_differe", typeDonnee="date", stringConverter=FormateDateCourt), #, imageGetter=GetImageDiffere),
            ColumnDefn(_(u"Attente"), 'left', 65, "encaissement_attente", typeDonnee="texte", stringConverter=FormateAttente), #, imageGetter=GetImageAttente),
            ColumnDefn(_(u"Quittancier"), 'left', 75, "numero_quittancier", typeDonnee="texte"),
            ColumnDefn(_(u"Observations"), 'left', 200, "observations", typeDonnee="texte"),
            ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        if self.inclus == True :
            self.SetEmptyListMsg(_(u"Aucun r�glement dans ce d�p�t"))
        else:
            self.SetEmptyListMsg(_(u"Aucun r�glement disponible"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self, tracks=None, ID=None, selectionTrack=None, nextTrack=None, IDcompte=None, IDmode=None):
        # Save sorting
        self.InitModel(tracks, IDcompte, IDmode)
        self.InitObjectListView()
        # S�lection d'un item
        if selectionTrack != None :
            self.SelectObjects(selectionTrack, deselectOthers=True)
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
                
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # G�n�ration automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        if self.GetGrandParent().GetName() == "DLG_Saisie_depot" :
            intro = self.GetGrandParent().GetLabelParametres()
        else :
            intro = u""
        # R�cup�re le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        total = self.GetDetailReglements()

        dictParametres = {
            "titre" : _(u"Liste des r�glements"),
            "intro" : intro,
            "total" : total,
            "orientation" : wx.LANDSCAPE,
            }
        return dictParametres

    def GetDetailReglements(self):
        # R�cup�ration des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.donnees :
            if track.inclus == True or self.inclus == False :
                # Montant total
                nbreTotal += 1
                # Nbre total
                montantTotal += track.montant
                # D�tail
                if (track.IDmode in dictDetails) == False :
                    dictDetails[track.IDmode] = { "label" : track.nom_mode, "nbre" : 0, "montant" : 0.0}
                dictDetails[track.IDmode]["nbre"] += 1
                dictDetails[track.IDmode]["montant"] += track.montant
        # Cr�ation du texte
        listeDetails = []
        texte = _(u"%d r�glements (%.2f �)") % (nbreTotal, montantTotal)
        for IDmode, dictDetail in dictDetails.items() :
            texteDetail = u"%d %s (%.2f �)" % (dictDetail["nbre"], dictDetail["label"], dictDetail["montant"])
            listeDetails.append(texteDetail)
        if len(listeDetails) > 0 :
            texte += " : "
            texte += ", ".join(listeDetails) + "."
        return texte

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun r�glement � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDreglement = track.IDreglement
        from Dlg import DLG_Saisie_reglement
        dlg = DLG_Saisie_reglement.Dialog(self, IDcompte_payeur=None, IDreglement=IDreglement)      
        if dlg.ShowModal() == wx.ID_OK:
            if self.GetGrandParent().GetName() == "DLG_Saisie_depot" :
                self.MAJ(selectionTrack=track) 
            if self.GetGrandParent().GetName() == "DLG_Saisie_depot_ajouter" :
                self.GetGrandParent().MAJListes(self.tracks, selectionTrack=track)
        dlg.Destroy() 

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun r�glement � supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDreglement = self.Selection()[0].IDreglement
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce r�glement ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("reglements", "IDreglement", IDreglement)
            DB.ReqDEL("ventilation", "IDreglement", IDreglement)
            DB.Close() 
            self.GetGrandParent().MAJListes(self.tracks)
        dlg.Destroy()

    def GetListeIDreglement(self):
        listeID = []
        for track in self.GetFilteredObjects():
            listeID.append(track.IDreglement)
        return listeID









# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un r�glement..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
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
            "nom_mode" : {"mode" : "nombre", "singulier" : _(u"r�glement"), "pluriel" : _(u"r�glements"), "alignement" : wx.ALIGN_CENTER},
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
        self.myOlv = ListView(panel, id=-1, inclus=False, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
