#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import Image
import os
import cStringIO

import GestionDB
import UTILS_Utilisateurs


def GetPhoto(IDindividu=None, nomFichier=None, taillePhoto=(128, 128), qualite=wx.IMAGE_QUALITY_HIGH):
    """ Retourne la photo d'un individu """    
    qualite=wx.IMAGE_QUALITY_HIGH
    if IDindividu != None :
        # Recherche d'une image dans la base de donn�es
        DB = GestionDB.DB(suffixe="PHOTOS")
        if DB.echec != 1 : 
            req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%d;" % IDindividu 
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                IDphoto, bufferPhoto = listeDonnees[0]
                # Transformation du buffer en wx.bitmap
                io = cStringIO.StringIO(bufferPhoto)
                img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
                img = img.Rescale(width=taillePhoto[0], height=taillePhoto[1], quality=qualite) 
                bmp = img.ConvertToBitmap()
                return (IDphoto, bmp)
            
    if nomFichier != None :
        # Recherche d'une image sur le disque dur
        if os.path.isfile(nomFichier):
            bmp = wx.Bitmap(nomFichier, wx.BITMAP_TYPE_ANY) # "Images/128x128/Femme.png"
            img = bmp.ConvertToImage()
            img = img.Rescale(width=taillePhoto[0], height=taillePhoto[1], quality=qualite) 
            bmp = img.ConvertToBitmap()
            return (None, bmp)
    
    return (None, None)
        

class CTRL_Photo(wx.StaticBitmap):
    def __init__(self, parent, IDindividu=None, style=0):
        wx.StaticBitmap.__init__(self, parent, id=-1, style=style)
        self.parent = parent
        self.IDphoto = None
        self.IDindividu = IDindividu
        
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.SetToolTipString(_(u"Cliquez sur le bouton droit de votre souris\npour acc�der aux fonctions photo"))
        
        self.Bind(wx.EVT_LEFT_DOWN, self.MenuPhoto)
        self.Bind(wx.EVT_RIGHT_DOWN, self.MenuPhoto)
        
##        self.SetPhoto(IDindividu=1)

    
    def SetPhoto(self, IDindividu=None, nomFichier=None, taillePhoto=(128, 128), qualite=wx.IMAGE_QUALITY_HIGH) :
        self.IDindividu = IDindividu
        IDphoto, bmp = GetPhoto(IDindividu, nomFichier, taillePhoto, qualite)
        if bmp != None :
            self.SetBitmap(bmp)
            self.IDphoto = IDphoto
    
    def GetIDphoto(self):
        return self.IDphoto

    def MenuPhoto(self, event):
        """Ouverture du menu contextuel de la photo """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_photo", "modifier") == False : return
        
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Importer une photo"))
        bmp = wx.Bitmap("Images/16x16/Importer_photo.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        # Item Capturer � partir d'une cam�ra
        item = wx.MenuItem(menuPop, 20, _(u"Capturer une photo � partir d'une webcam"))
        bmp = wx.Bitmap("Images/16x16/Webcam.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Capturer, id=20)
        
        menuPop.AppendSeparator() 
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        if self.IDphoto == None : item.Enable(False)
        
##        menuPop.AppendSeparator()
##        
##         # Item Imprimer
##        item = wx.MenuItem(menuPop, 40, _(u"Imprimer la photo"))
##        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Menu_Imprimer, id=40)
##        if self.IDphoto == None : item.Enable(False)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Menu_Ajouter(self, event):
        self.Ajoute_image()

    def Ajoute_image(self):
        """ Permet la s�lection et le retouchage d'une photo pour la personne """
        # S�lection d'une image
        self.repCourant = os.getcwd()

        wildcard = "Toutes les images|*.bmp; *.gif; *.jpg; *.png|Image JPEG (*.jpg)|*.jpg|Image PNG (*.png)|*.png|Image GIF (*.gif)|*.gif|Tous les fichiers (*.*)|*.*"
                
        # R�cup�ration du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture dela fen�tre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une photo"),
            defaultDir=cheminDefaut, 
            defaultFile="", 
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        self.ChargeEditeurPhoto(nomFichierLong)
        
    def ChargeEditeurPhoto(self, nomFichierLong="", listeVisages=[]):
        # Recadre la photo
        import DLG_Editeur_photo
        dlg = DLG_Editeur_photo.Dialog(None, image=nomFichierLong, tailleCadre=(128, 128), listeVisages=listeVisages)
        if dlg.ShowModal() == wx.ID_OK:
            buffer = dlg.GetBuffer()
            bmp = buffer.read()
            tailleBmp = len(buffer.getvalue())
            dlg.Destroy()
            # Recherche si une photo existe d�j� pour cet individu
            DB = GestionDB.DB(suffixe="PHOTOS")
            if DB.echec != 1 : 
                req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%d;" % self.IDindividu 
                DB.ExecuterReq(req)
                listePhotos = DB.ResultatReq()
                if len(listePhotos) == 0 :
                    IDphoto = DB.InsertPhoto(IDindividu=self.IDindividu, blobPhoto=bmp)
                else:
                    IDphoto = DB.MAJPhoto(IDphoto=listePhotos[0][0], IDindividu=self.IDindividu, blobPhoto=bmp)
                DB.Close()
            # Applique la photo
            self.SetPhoto(self.IDindividu)
        else:
            dlg.Destroy()
            return

    def Menu_Capturer(self, event):
        self.Capture_image()

    def Capture_image(self):
        """ Capture la photo � partir d'une cam�ra """
        import DLG_Capture_video_opencv_2 as dlg
        image = None
        dlg = dlg.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            image = dlg.GetImage()
            listeVisages = dlg.GetListeVisages() 
        dlg.Destroy()
        if image != None :
            fichier = "Temp/capture_video.jpg"
            image.SaveFile(fichier, type=wx.BITMAP_TYPE_JPEG)
            self.ChargeEditeurPhoto(fichier, listeVisages=listeVisages)

    def Menu_Supprimer(self, event):
        """ Suppression de la photo """
        txtMessage = _(u"Souhaitez-vous vraiment supprimer cette photo ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        # Suppression de la photo 
        DB = GestionDB.DB(suffixe="PHOTOS")
        DB.ReqDEL("photos", "IDindividu", self.IDindividu)
        DB.Close()
        # Recherche la civilit� de l'individu
        DB = GestionDB.DB()
        req = "SELECT IDcivilite FROM individus WHERE IDindividu=%d;" % self.IDindividu 
        DB.ExecuterReq(req)
        IDcivilite = DB.ResultatReq()[0][0]
        if IDcivilite == None : return
        DB.Close()
        import DATA_Civilites as Civilites
        listeCivilites = Civilites.LISTE_CIVILITES
        for rubrique, civilites in listeCivilites :
            for civilite in civilites :
                if civilite[0] == IDcivilite :
                    nomFichier = civilite[3]
                    break
        nomFichier=u"Images/128x128/%s" % nomFichier
        # Applique l'image par d�faut
        self.SetPhoto(self.IDindividu, nomFichier)
        
    def Menu_Imprimer(self, event):
        """ Impression de la photo de la personne """
        # R�cup�ration de la liste des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, nom, prenom FROM personnes WHERE IDpersonne=%d; """ % self.IDpersonne
        DB.executerReq(req)
        donnees = DB.resultatReq()[0]
        DB.close()
        # Ouverture de la frame d'impression des photos  
        import Impression_photo
        frame = Impression_photo.MyFrame(None, listePersonnes=[[self.IDpersonne, donnees[1], donnees[2], None],])
        frame.Show()

    def wxtopil(self, image):
        """Convert wx.Image to PIL Image."""
        pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
        pil.fromstring(image.GetData())
        return pil




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= CTRL_Photo(panel)
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