#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import six



def ChargeImage(fichier):
    """Read a file into PIL Image object. Return the image and file size"""
##    buf=cStringIO.StringIO()
##    f=open(fichier,"rb")
##    while 1:
##        rdbuf=f.read(8192)
##        if not rdbuf: break
##        buf.write(rdbuf)
##    f.close()
##    buf.seek(0)
##    image = Image.open(buf).convert("RGBA")
    image = wx.Image(fichier, wx.BITMAP_TYPE_ANY)
    return image

def wxtopil( image):
    """Convert wx.Image to PIL Image."""
    data = image.GetData()
    if 'phoenix' in wx.PlatformInfo:
        data = bytes(data)
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.paste(pil.frombytes(data), (10, 10))
    return pil

def piltowx(image):
    """Convert a PIL image to wx image format"""
    largeur, hauteur = image.size
    imagewx = wx.EmptyImage(largeur, hauteur)
    imagewx.SetData(image.tobytes('raw', 'RGB'))
    imagewx.SetAlphaData(image.convert("RGBA").tobytes()[3::4])
    return imagewx        
        
        
        
class CTRL(wx.StaticBitmap):
    def __init__(self, parent, qualite=100, couleurFond=(255, 255, 255), tailleMaxi=1000, size=(83, 83), mode="ecriture", style=wx.SUNKEN_BORDER):
        wx.StaticBitmap.__init__(self, parent, id=-1, size=size, style=style)
        self.parent = parent
        self.qualite = qualite
        self.couleurFond = couleurFond
        self.tailleMaxi = tailleMaxi
        self.estModifie = False
        self.mode = mode
        
        self.imagewx = None
        
        # Propriétés
        self.SetMinSize(size)
        self.SetBackgroundColour(self.couleurFond)
        self.SetToolTip(wx.ToolTip(_(u"Cliquez sur le bouton droit de votre souris\npour accéder aux fonctions")))
        
        #Binds
        self.Bind(wx.EVT_LEFT_DOWN, self.Menu)
        self.Bind(wx.EVT_RIGHT_DOWN, self.Menu)
        self.Bind(wx.EVT_SIZE, self.OnSize)
    
    def OnSize(self, event):
        self.Refresh() 
        
    def Menu(self, event):
        """Ouverture du menu contextuel"""
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        if self.mode == "ecriture" :

            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Importer une image"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)

            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
            if self.imagewx == None : item.Enable(False)

        # Item Visualiser
        item = wx.MenuItem(menuPop, 40, _(u"Visualiser"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Visualiser, id=40)
        if self.imagewx == None : item.Enable(False)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Menu_Ajouter(self, event):
        self.Ajouter()
            
    def Menu_Supprimer(self, event):
        self.Supprimer()
    
    def Ajouter(self, event=None):
        """ Importer Image """
        wildcard = "Toutes les images (*.bmp; *.gif; *.jpg; *.png)|*.bmp;*.gif;*.jpg;*.png|Image JPEG (*.jpg)|*.jpg|Image PNG (*.png)|*.png|Image GIF (*.gif)|*.gif|Tous les fichiers (*.*)|*.*"
                
        # Récupération du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        
        # Ouverture dela fenêtre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Sélectionnez une image"),
            defaultDir=cheminDefaut, 
            defaultFile="", 
            wildcard=wildcard,
            style=wx.FD_OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Charge l'image
        img = ChargeImage(nomFichier)
        
        # Recadre l'image
        tailleMaxi = self.tailleMaxi
        largeur, hauteur = img.GetSize()
        if max(largeur, hauteur) > tailleMaxi :
            if largeur > hauteur :
                hauteur = hauteur * tailleMaxi / largeur
                largeur = tailleMaxi
            else:
                largeur = largeur * tailleMaxi / hauteur
                hauteur = tailleMaxi
##            imgPIL = imgPIL.resize((largeur, hauteur), Image.ANTIALIAS)
            img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
        
        # Conserve l'image en mémoire
        self.imagewx = img
        self.MAJ() 
        self.estModifie = True
    
    def MAJ(self, event=None):
        if self.imagewx == None :
            self.SetBitmap(wx.NullBitmap)
            return
        # Recadre l'image en fonction de la taille du staticBitmap
        img = self.imagewx.Copy()       
        largeurCadre, hauteurCadre = self.GetSize()
        largeurImage, hauteurImage = img.GetSize()
        ratioCadre = 1.0 * largeurCadre / hauteurCadre
        ratioImage = 1.0 * largeurImage / hauteurImage
        espace = 8
        # Adaptation à la hauteur
        hauteurImage = hauteurCadre - espace
        largeurImage = hauteurImage * ratioImage
        # Adaptation à la largeur
        if largeurImage > largeurCadre :
            largeurImage = largeurCadre - espace
            hauteurImage = largeurImage / ratioImage
        
        img.Rescale(width=largeurImage, height=hauteurImage, quality=wx.IMAGE_QUALITY_HIGH)
        position = (((largeurCadre/2.0) - (largeurImage/2.0)), ((hauteurCadre/2.0) - (hauteurImage/2.0)))
        img.Resize(self.GetSize(), position, 255, 255, 255)
        # Affiche l'image
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(img)
        else :
            bmp = wx.BitmapFromImage(img)
        self.SetBitmap(bmp)
    
    def Supprimer(self, event=None):
        if self.imagewx == None :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune image à supprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la suppression de cette image ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
                return
        # Suppression
        self.imagewx = None
        self.MAJ() 
        self.estModifie = True
    
    def ChargeFromBuffer(self, buffer=None):
        """ Charge l'image à partir d'un buffer """
        if buffer == None :
            self.imagewx = None
        else :
            io = six.BytesIO(buffer)
            if 'phoenix' in wx.PlatformInfo:
                self.imagewx = wx.Image(io, wx.BITMAP_TYPE_PNG)
            else :
                self.imagewx = wx.ImageFromStream(io, wx.BITMAP_TYPE_PNG)
        self.MAJ() 

    def GetBuffer(self):
        """ Récupère le buffer de l'image """
        if self.imagewx == None : return None
        buffer = six.BytesIO()
        self.imagewx.SaveStream(buffer, wx.BITMAP_TYPE_PNG)
        buffer.seek(0)
        blob = buffer.read()
        return blob
    
    def Visualiser(self, event=None):
        if self.imagewx == None :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune image à visualiser !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Dlg import DLG_Visualiseur_image
        dlg = DLG_Visualiseur_image.MyFrame(None, imgWX=self.imagewx)
        dlg.Show(True)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, size=(83, 83))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(83, 83))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()