#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import GestionDB

import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, ListCtrlPrinter

import Image
import cStringIO
import numpy as np
import cv2
import OL_Individus_grille_ajouter
import wx.lib.agw.pybusyinfo as PBI

TAILLE_IMAGE = (128, 128)
TAILLE_IMAGE_ORIGINALE = (300, 200)


class Track(object):
    def __init__(self, parent, bmp=None, index=None):
        self.bmp = bmp
        self.index = index
        self.IDindividu = None
        self.nomIndividu = ""
            


    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.listePhotos = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.Modifier)
            
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeListeView = []
        index = 0
        for bmp in self.listePhotos :
            track = Track(self, bmp, index)
            listeListeView.append(track)
            index += 1
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Création du imageList avec une taille personnalisée
        dictImages = {}
        imageList = wx.ImageList(TAILLE_IMAGE[0], TAILLE_IMAGE[1])
        for track in self.donnees :
            indexImg = imageList.Add(track.bmp)            
        self.SetImageLists(imageList, imageList)
        
        def GetImage(track):
            return track.index 
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDinscription"),
            ColumnDefn(_(u"Photo"), 'center', TAILLE_IMAGE[0]+1, "", imageGetter=GetImage),
            ColumnDefn(_(u"Individu"), 'center', 100, "nomIndividu", isSpaceFilling=True),
            ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun visage détecté"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[0])
        self.SetObjects(self.donnees)
       
    def MAJ(self, listePhotos=[], ID=None):
        self.listePhotos = listePhotos
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        self._ResizeSpaceFillingColumns() 
    
    def Selection(self):
        return self.GetSelectedObjects()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune photo à identifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Rechercher_individu(self, bmp=track.bmp)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees()
            nom = dictDonnees["nom"]
            prenom = dictDonnees["prenom"]
            if prenom == None : prenom = ""
            track.nomIndividu = u"%s %s" % (nom, prenom)
            track.IDindividu = dictDonnees["IDindividu"]
            self.RefreshObject(track)
        dlg.Destroy()
        
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Rechercher_individu(wx.Dialog):
    def __init__(self, parent, bmp=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.bmp = bmp
        
        self.ctrl_image = wx.StaticBitmap(self, -1, bitmap=self.bmp, size=TAILLE_IMAGE, style=wx.SUNKEN_BORDER)
        
        self.ctrl_listview = OL_Individus_grille_ajouter.ListView(self, id=-1, name="OL_individus", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.MAJ() 
        self.ctrl_recherche = OL_Individus_grille_ajouter.CTRL_Outils(self, listview=self.ctrl_listview)
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.SetTitle(_(u"Identifier un individu"))
        self.SetMinSize((550, 460))
        
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.ctrl_image, 1, wx.ALIGN_TOP, 0)
        grid_sizer_contenu.Add(self.ctrl_listview, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add( (0, 0), 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND, 10)
        grid_sizer_boutons.Add( (1, 1), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.BOTTOM|wx.RIGHT|wx.LEFT|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        self.ctrl_recherche.SetFocus()
    
    def OnSelection(self):
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        track = self.ctrl_listview.GetSelection()
        if track == None :
            return None
        return {"IDindividu":track.IDindividu, "nom":track.nom, "prenom":track.prenom}
        
    def OnBoutonOk(self, event):
        if self.GetDonnees() == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.EndModal(wx.ID_OK)
        

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.nom_fichier = None
        
        intro = _(u"Vous pouvez ici importer un lot de photos individuelles depuis une photo de groupe. Chargez la photo et Noethys se chargera de détecter les visages. Vous devrez ensuite identifier chaque photo : Double-cliquez sur une photo pour l'associer à un individu. Cliquez sur Enregistrer pour terminer.")
        titre = _(u"Importer des photos individuelles")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Photos.png")
        
        self.ctrl_image = wx.StaticBitmap(self, -1, bitmap=wx.NullBitmap, size=TAILLE_IMAGE_ORIGINALE, style=wx.SUNKEN_BORDER)
        self.bouton_image = wx.Button(self, -1, _(u"Charger une image"))
        self.bouton_sauvegarder = wx.Button(self, -1, _(u"Enregistrer les photos identifiées"))
        self.label_infos = wx.StaticText(self, -1, _(u"Cliquez le bouton Charger\npour rechercher la photo de\ngroupe à analyser."), style=wx.ALIGN_CENTER)

        self.ctrl_listview = ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.MAJ() 
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFichier, self.bouton_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnregistrer, self.bouton_sauvegarder)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.AnalysePhoto() 

    def __set_properties(self):
        self.bouton_image.SetToolTipString(_(u"Cliquez ici pour charger une image"))
        self.bouton_sauvegarder.SetToolTipString(_(u"Cliquez ici pour enregistrer les images identifiées dans les fiches individuelles correspondantes"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((820, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Gauche
        grid_sizer_droite = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.ctrl_image, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.bouton_image, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.bouton_sauvegarder, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.label_infos, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gauche.AddGrowableRow(3)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Droite
        grid_sizer_droite.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_droite.AddGrowableRow(0)
        grid_sizer_droite.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def Ajouter(self, event):
        self.ctrl_listview.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Importerdesphotosindividuelles")
    
    def OnBoutonFichier(self, event):
        """ Charger un fichier """
        nbreIdentifiees = len(self.GetPhotosIdentifiees())
        if nbreIdentifiees > 0 :
            dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment charger une nouvelle image ?\n\nAttention, les %d photo(s) identifiée(s) non enregistrées seront annulées.") % nbreIdentifiees, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        wildcard = "Toutes les images|*.bmp; *.gif; *.jpg; *.png|Image JPEG (*.jpg)|*.jpg|Image PNG (*.png)|*.png|Image GIF (*.gif)|*.gif|Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une image"),
            defaultDir=cheminDefaut, 
            defaultFile="", 
            wildcard=wildcard,
            style=wx.OPEN
            )
        nomFichier = None
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetPath()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return
        self.AnalysePhoto(nomFichier)
        
    def GetPhotosIdentifiees(self):
        listeIdentifiees = []
        for track in self.ctrl_listview.donnees :
            if track.IDindividu != None :
                listeIdentifiees.append(track)
        return listeIdentifiees
        
    def AnalysePhoto(self, nom_fichier=None):
        if nom_fichier == None :
            self.ctrl_listview.MAJ()
            img = wx.EmptyImage(TAILLE_IMAGE_ORIGINALE[0], TAILLE_IMAGE_ORIGINALE[1])
            img.SetRGBRect((0, 0, TAILLE_IMAGE_ORIGINALE[0], TAILLE_IMAGE_ORIGINALE[1]), 0, 0, 0)
            self.AfficheImageOriginale(img.ConvertToBitmap())
            return False
        
        self.label_infos.SetLabel(_(u"Analyse de l'image en cours..."))
        self.Layout()
        
        dlgAttente = PBI.PyBusyInfo(_(u"Analyse de l'image en cours..."), parent=self, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        cascade = cv2.CascadeClassifier('Outils/haarcascade_frontalface_alt2.xml')
        img = cv2.imread(nom_fichier.encode("iso-8859-15"))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        bmp = wx.BitmapFromBuffer(width, height, frame)
##        print "Photo originale =", bmp, bmp.GetSize() 
        
        listePhotos = []
        faces = cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            bmpVisage = bmp.GetSubBitmap((x, y, w, h))
            
            # Ajuste taille de l'image
            imgVisage = wx.ImageFromBitmap(bmpVisage)
            imgVisage.Rescale(width=TAILLE_IMAGE[0], height=TAILLE_IMAGE[1], quality=wx.IMAGE_QUALITY_HIGH)
            bmpVisage = imgVisage.ConvertToBitmap()
            
            # Ajoute la photo à la liste
            listePhotos.append(bmpVisage) 
            
            # Tracé du cadre rouge
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)
        
        # Envoie les visages au ListView
        self.ctrl_listview.MAJ(listePhotos)
        
        # Envoie l'image originale vers le staticbitmap
        bmp = wx.BitmapFromBuffer(width, height, frame)
        self.AfficheImageOriginale(bmp)
        
        # MAJ Label_infos
        texte = _(u"Noethys a détecté %d visages.\n\nDouble-cliquez sur les lignes\nde la liste pour les associer\nà des individus.") % len(listePhotos)
        self.label_infos.SetLabel(texte)
        self.Layout()
        
        del dlgAttente
        
    
    def AfficheImageOriginale(self, bmp=None):
        """ Affiche l'image originale dans le staticbitmap """
        # Ajuste la taille
        img = wx.ImageFromBitmap(bmp)
        largeur1, hauteur1 = img.GetSize()
        if largeur1 > hauteur1 :
            largeur = TAILLE_IMAGE_ORIGINALE[0]
            hauteur = hauteur1 * TAILLE_IMAGE_ORIGINALE[0] / largeur1
        else :
            hauteur = TAILLE_IMAGE_ORIGINALE[1]
            largeur = largeur1 * TAILLE_IMAGE_ORIGINALE[1] / hauteur1
        img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
        position = (((TAILLE_IMAGE_ORIGINALE[0]/2.0) - (largeur/2.0)), ((TAILLE_IMAGE_ORIGINALE[1]/2.0) - (hauteur/2.0)))
        img.Resize(TAILLE_IMAGE_ORIGINALE, position, 0, 0, 0)
        bmp = wx.BitmapFromImage(img)
        
        # Affichage de l'image
        self.ctrl_image.SetBitmap(bmp)

    def OnBoutonEnregistrer(self, event):
        """ Enregistre les photos identifiées """
        tracks = self.GetPhotosIdentifiees()
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez identifié aucune photo dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        DB = GestionDB.DB(suffixe="PHOTOS")
        if DB.echec == 1 : 
            dlg = wx.MessageDialog(self, _(u"La base de données PHOTOS n'a pas été trouvée !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close() 
            return False
        
        for track in tracks :
            
            # Transforme l'image en buffer
            image = track.bmp.ConvertToImage()
            pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
            pil.frombytes(image.GetData())
            buffer = cStringIO.StringIO()
            pil.save(buffer, format="JPEG", quality=100)
            buffer.seek(0)
            buffer = buffer.read()

            # Enregistre le buffer dans la base
            req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%d;" % track.IDindividu 
            DB.ExecuterReq(req)
            listePhotos = DB.ResultatReq()
            if len(listePhotos) == 0 :
                IDphoto = DB.InsertPhoto(IDindividu=track.IDindividu, blobPhoto=buffer)
            else:
                IDphoto = DB.MAJPhoto(IDphoto=listePhotos[0][0], IDindividu=track.IDindividu, blobPhoto=buffer)
                
        DB.Close()
        
        # Message de confirmation
        dlg = wx.MessageDialog(self, _(u"Les %d photos identifiées ont été enregistrées avec succès dans les fiches individuelles !") % len(tracks), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
