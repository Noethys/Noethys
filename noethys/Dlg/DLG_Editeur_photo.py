#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activitï¿œs
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from PIL import Image
import six


def pil2wx(image):
    """Convert a PIL image to wx image format"""
    if 'phoenix' in wx.PlatformInfo:
        imagewx = wx.Image(image.size[0], image.size[1])
    else :
        imagewx = wx.EmptyImage(image.size[0], image.size[1])
    imagewx.SetData(image.tobytes('raw', 'RGB'))
    return imagewx

def load_image(fn):
    """Read a file into PIL Image object. Return the image and file size"""
    buf = six.BytesIO()
    f=open(fn,"rb")
    while 1:
        rdbuf=f.read(8192)
        if not rdbuf: break
        buf.write(rdbuf)
    f.close()
    buf.seek(0)
    image=Image.open(buf).convert("RGB")
    return image

def save_image_buf(image,q=wx.IMAGE_QUALITY_HIGH):
    """Save a PIL Image into a byte buffer as a JPEG with the given quality.
    Return the buffer and file size.
    """
    buf = six.BytesIO()
    image.save(buf, format='JPEG',quality=q)
    buf.seek(0)
    return buf,len(buf.getvalue())

def save_image_file(fn,buf):
    """Save a byte buffer to a file"""
    f=open(fn,"wb")
    while 1:
        rdbuf=buf.read(8192)
        if not rdbuf: break
        f.write(rdbuf)
    f.close()

def wxtopil(image):
    """Convert wx.Image to PIL Image."""
    data = image.GetData()
    if 'phoenix' in wx.PlatformInfo:
        data = bytes(data)
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.frombytes(data)
    return pil



class ImgBox(wx.Window):
    def __init__(self, parent, id=-1, image=None, tailleCadre=(384, 384)):
        wx.Window.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.NO_FULL_REPAINT_ON_RESIZE |wx.SUNKEN_BORDER)
        self.tailleCadre = tailleCadre
        
        self.fichierImageSource = image
        self.InitImage()

        # Binds
        self.Bind(wx.EVT_PAINT, self.evt_paint)
        self.Bind(wx.EVT_SIZE, self.evt_size)
        self.Bind(wx.EVT_KEY_DOWN, self.evt_key)
        self.Bind(wx.EVT_LEFT_DOWN, self.evt_mouse)
        self.Bind(wx.EVT_LEFT_UP, self.evt_mouse)
        self.Bind(wx.EVT_MOTION, self.evt_mouse)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        
    def InitImage(self):
        # Chargement de l'image source
        if type(self.fichierImageSource) == str or type(self.fichierImageSource) == six.text_type :
            self.sourcePIL = load_image(self.fichierImageSource)
        else :
            self.sourcePIL = self.fichierImageSource
        
        # Transforme l'image PIL en wx.Image
        self.source = pil2wx(self.sourcePIL)
##        print self.source.GetSize()
        
        # Initialise les valeurs
        self.posxPhoto = None
        self.posyPhoto = None
        self.zoom = None
        self.dragging = False
        self.largeurDC = None
        self.hauteurDC = None
        
        
    def ReinitImage(self):
        self.InitImage()
        self.evt_size(None)
        
    def InitValeursPhoto(self):
        """ Calcule la position et la taille initiale de la photo (au milieu) """
        if 'phoenix' in wx.PlatformInfo:
            largeurDC, hauteurDC = self.GetClientSize()
        else :
            largeurDC, hauteurDC = self.GetClientSizeTuple()
        largeurImg, hauteurImg = self.source.GetSize()
        # Calcule le zoom en fonction de la taille de la photo
        largeurMax = max(self.tailleCadre) * 1.0 #min(largeurDC, hauteurDC) / 2.0
        margeSupp = 0
        zoomTmp = (largeurMax+margeSupp) / min(largeurImg, hauteurImg)
        # Transmet la valeur du zoom au slider
        valeurSliderZoom = round(zoomTmp*1000)
        self.GetParent().slider_zoom.SetValue(int(valeurSliderZoom))
        self.zoom = valeurSliderZoom / 1000.0
        # Calcule la position de la photo au centre du dc
        self.ResizePhoto()
        self.posxPhoto = (largeurDC / 2.0) 
        self.posyPhoto = (hauteurDC / 2.0)



    def Draw(self,dc):
        """Draw the image bitmap and decoration on the buffered DC"""
        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        # Dessin de la photo
        largeurImg, hauteurImg = self.bmp.GetSize()
        dc.DrawBitmap(self.bmp, int(self.posxPhoto - (largeurImg / 2.0)), int(self.posyPhoto - (hauteurImg / 2.0)), 0)
        
        # Dï¿œfinit la position et la taille du cadre de sï¿œlection
        coeffReduction = 2.0
        if 'phoenix' in wx.PlatformInfo:
            largeurDC, hauteurDC = self.GetClientSize()
        else :
            largeurDC, hauteurDC = self.GetClientSizeTuple()
        self.posxCadre = (largeurDC / 2.0) - (self.tailleCadre[0] / 2.0)
        self.posyCadre = (hauteurDC / 2.0) - (self.tailleCadre[1] / 2.0)
        
        # Mï¿œmorise la sï¿œlection de la photo avant de dessiner le cadre
        self.selection = dc.GetAsBitmap((self.posxCadre, self.posyCadre, self.tailleCadre[0], self.tailleCadre[1]))
                
        # Dessine le cadre de sï¿œlection
        dc.SetPen(wx.CYAN_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(self.posxCadre, self.posyCadre, self.tailleCadre[0], self.tailleCadre[1])
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        dc.SetTextForeground("CYAN")
        dc.DrawText(_(u"Cadre de sï¿œlection"), self.posxCadre+3, self.posyCadre+1) 
        
        # Dessine l'aperï¿œu
        largeurApercu = 100.0
        tailleApercu = (largeurApercu, largeurApercu * self.tailleCadre[1] / self.tailleCadre[0])
        posxApercu, posyApercu = (10, 10)
        self.apercu = self.selection.ConvertToImage()
        self.apercu = self.apercu.Rescale(width=tailleApercu[0], height=tailleApercu[1], quality=wx.IMAGE_QUALITY_HIGH) 
        self.apercu = self.apercu.ConvertToBitmap()
        dc.DrawBitmap(self.apercu, int(posxApercu), int(posyApercu), 0)
        dc.SetTextForeground("RED")
        texteApercu = _(u"Aperï¿œu")
        dc.DrawText(texteApercu, posxApercu+3, posyApercu+1) 
        
        # Dessine le cadre de l'aperï¿œu
        dc.SetPen(wx.RED_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(posxApercu, posyApercu, tailleApercu[0], tailleApercu[1])

    def evt_paint(self, event):
        """Paint event handler with double buffering"""
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def evt_size(self,event):
        """ OnSize """
        ancLargeurDC, ancHauteurDC = self.largeurDC, self.hauteurDC
        if 'phoenix' in wx.PlatformInfo:
            self.largeurDC, self.hauteurDC = self.GetClientSize()
        else :
            self.largeurDC, self.hauteurDC = self.GetClientSizeTuple()
        # Initialise la taille et la position initiale de la photo
        if self.posxPhoto == None : 
            self.InitValeursPhoto()
        else :
        # Redimensionne la photo 
            self.ResizePhoto()
            # Dï¿œtermine le nouveau point central de la photo
            self.posxPhoto = self.posxPhoto + (self.largeurDC-ancLargeurDC)/2
            self.posyPhoto = self.posyPhoto + (self.hauteurDC-ancHauteurDC)/2
        # Redessine toute l'image
        if 'phoenix' in wx.PlatformInfo:
            self._Buffer = wx.Bitmap(self.largeurDC, self.hauteurDC)
        else :
            self._Buffer = wx.EmptyBitmap(self.largeurDC, self.hauteurDC)
        self.UpdateDrawing()


    def ResizePhoto(self):
        """ Redimensionne la photo"""
        largeurImg, hauteurImg = self.source.GetSize()
        # Rï¿œduction de l'image
        newLargeur = largeurImg * self.zoom
        newHauteur = hauteurImg * self.zoom
        # Redimensionne l'image
        if newLargeur > 1 and newHauteur > 1 :
            source = self.source.Scale(newLargeur, newHauteur)
            if 'phoenix' in wx.PlatformInfo:
                self.bmp = wx.Bitmap(source)
            else:
                self.bmp = wx.BitmapFromImage(source)
    
    def UpdateDrawing(self):
        """Create the device context and draw the window contents"""
        dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        if 'phoenix' not in wx.PlatformInfo:
            dc.BeginDrawing()
        self.Draw(dc)
        if 'phoenix' not in wx.PlatformInfo:
            dc.EndDrawing()

    def Zoom(self, valeurZoom):
        """ Zoom """
        self.zoom = valeurZoom
        self.ResizePhoto()
        self.UpdateDrawing()
        
    def Rotation(self, VersDroite=True):
        """ Rotation de la photo """
        # Rotation
        self.source = self.source.Rotate90(VersDroite)
        # Rï¿œduction de l'image
        largeurImg, hauteurImg = self.source.GetSize()
        newLargeur = largeurImg * self.zoom
        newHauteur = hauteurImg * self.zoom
        source = self.source.Scale(newLargeur, newHauteur)
        if 'phoenix' in wx.PlatformInfo:
            self.bmp = wx.Bitmap(source)
        else:
            self.bmp = wx.BitmapFromImage(source)
        # MAJ de l'affichage de la photo
        self.UpdateDrawing()

    def evt_mouse(self,event):
        """ Gestion du dï¿œplacement de la photo """
        if 'phoenix' in wx.PlatformInfo:
            cursor = wx.Cursor
        else :
            cursor = wx.StockCursor

        eventType=event.GetEventType()
        posx, posy = event.GetPosition()
        # Left Down
        if eventType == wx.wxEVT_LEFT_DOWN:
            self.dragging = True
            self.posxDrag, self.posyDrag = self.posxPhoto - posx, self.posyPhoto - posy
            self.SetCursor(cursor(wx.CURSOR_SIZING))
        # Left Up
        elif eventType == wx.wxEVT_LEFT_UP:
            self.dragging = False
            self.SetCursor(cursor(wx.CURSOR_ARROW))
        # Motion
        elif eventType == wx.wxEVT_MOTION:
            if self.dragging == True :
                self.posxPhoto = posx + self.posxDrag
                self.posyPhoto = posy + self.posyDrag
                self.UpdateDrawing()

    def OnLeaveWindow(self, event):
        pass #self.dragging = False

    def evt_key(self, event):
        """ Touches clavier """
        keyCode = event.GetKeyCode()
        print(keyCode)

    def GetBuffer(self):
        # Rï¿œcupï¿œration de l'image dans le cadre de sï¿œlection
        tailleImg = self.selection.GetSize()
        imgTemp = self.selection.GetSubBitmap( (0, 0, tailleImg[0], tailleImg[1]) ) 
        imgFinale = wxtopil(imgTemp.ConvertToImage())
        buffer = six.BytesIO()
        imgFinale.save(buffer, format="JPEG", quality=100)
        buffer.seek(0)
        return buffer


    def AjusteVisage(self, listeVisages=[]):
        pass
##        largeur, hauteur = self.source.GetSize()
##        ((x, y, w, h), n) = listeVisages[0]
##        print x, y, w, h
##        # Ajuste le zoom
##        self.zoom = 1.0 * self.tailleCadre[0] / w
##        self.ResizePhoto()
##        self.UpdateDrawing()
##
##        # Ajuste la position pour centrer sur le visage
##        print self.posxPhoto, self.posyPhoto, self.posxCadre, self.posyCadre, self.bmp.GetSize() 
##        self.posxPhoto = self.posxPhoto + x
##        self.posyPhoto =  y
##        self.UpdateDrawing()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------



class Dialog(wx.Dialog):
    def __init__(self, parent, image=None, tailleCadre=(384, 384), titre=_(u"Editeur photo"), listeVisages=[]):
        wx.Dialog.__init__(self, parent, -1, title=titre, name="frm_photo", size=(700, 600))
        
        # Widgets
        self.imgbox = ImgBox(self,-1, image=image, tailleCadre=tailleCadre)
        
        self.staticBox_rotation = wx.StaticBox(self, -1, _(u"Rotation"))
        self.bouton_rotation_gauche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/RotationGauche.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_rotation_droite = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/RotationDroite.png"), wx.BITMAP_TYPE_PNG))
        
        self.staticBox_zoom = wx.StaticBox(self, -1, _(u"Zoom"))
        self.slider_zoom = wx.Slider(self, -1,  500, 1, 1000, size=(-1, -1), style=wx.SL_HORIZONTAL)
        self.img_loupe_plus = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/ZoomPlus.png"), wx.BITMAP_TYPE_ANY))
        self.img_loupe_moins = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/ZoomMoins.png"), wx.BITMAP_TYPE_ANY))
                
        self.staticBox_reinit = wx.StaticBox(self, -1, _(u"Rï¿œinitialisation"))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Photo.png"), wx.BITMAP_TYPE_ANY), size=(70, -1))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRotationGauche, self.bouton_rotation_gauche)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRotationDroite, self.bouton_rotation_droite)
        self.Bind(wx.EVT_SCROLL, self.OnScrollSlider, self.slider_zoom)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Ajuste sur le 1er visage
        if len(listeVisages) > 0 :
            self.imgbox.AjusteVisage(listeVisages) 
            
            
    def __set_properties(self):
        self.SetTitle(_(u"Editeur de photo"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider l'image")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        
        self.bouton_rotation_gauche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effectuer une rotation de 90ï¿œ\n dans le sens inverse des aiguilles d'une montre")))
        self.bouton_rotation_droite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effectuer une rotation de 90ï¿œ\n dans le sens des aiguilles d'une montre")))
        self.slider_zoom.SetToolTip(wx.ToolTip(_(u"Ajustez avec cette fonction zoom\nla taille de la photo")))
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour rï¿œinitialiser la position\net la taille de la photo initiale")))
        
        self.SetMinSize((700, 600))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # DC
        grid_sizer_base.Add(self.imgbox, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        
        # Panneau de contrï¿œle
        sizer_commandes = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        
        # Rotation
        staticBox_rotation = wx.StaticBoxSizer(self.staticBox_rotation, wx.HORIZONTAL)
        staticBox_rotation.Add(self.bouton_rotation_gauche, 0, wx.ALL, 2)
        staticBox_rotation.Add(self.bouton_rotation_droite, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_rotation, 1, wx.EXPAND, 0)
        
        # Zoom
        staticBox_zoom = wx.StaticBoxSizer(self.staticBox_zoom, wx.HORIZONTAL)
        staticBox_zoom.Add(self.img_loupe_moins, 0, wx.ALL, 2)
        staticBox_zoom.Add(self.slider_zoom, 1, wx.EXPAND | wx.ALL, 2)
        staticBox_zoom.Add(self.img_loupe_plus, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_zoom, 1, wx.EXPAND, 0)
        
        # Reinit
        staticBox_reinit = wx.StaticBoxSizer(self.staticBox_reinit, wx.HORIZONTAL)
        staticBox_reinit.Add(self.bouton_reinit, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_reinit, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(sizer_commandes, 1, wx.EXPAND | wx.ALL, 10)
        
        sizer_commandes.AddGrowableRow(0)
        sizer_commandes.AddGrowableCol(1)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)

        self.Layout()
        self.Centre()
                        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Photo")

    def GetBmp(self, qualite=wx.IMAGE_QUALITY_HIGH):
        buffer = self.GetBuffer()
        img = wx.ImageFromStream(buffer, wx.BITMAP_TYPE_ANY)
##        img = img.Rescale(width=taillePhoto[0], height=taillePhoto[1], quality=qualite) 
        bmp = img.ConvertToBitmap()
        return bmp
    
    def GetBuffer(self):
        # Rï¿œcupï¿œration de l'image dans le cadre de sï¿œlection
        return self.imgbox.GetBuffer()
    
    def OnBoutonOk(self, event):        
        # Ferme la boï¿œte de dialogue
        self.EndModal(wx.ID_OK) 
        
    def OnBoutonRotationGauche(self, event):
        self.imgbox.Rotation(False)

    def OnBoutonRotationDroite(self, event):
        self.imgbox.Rotation(True)

    def OnScrollSlider(self, event):
        """ On Slider """
        valeurZoom = self.slider_zoom.GetValue()/1000.0
        self.imgbox.Zoom(valeurZoom)
    
    def OnBoutonReinit(self, event):
        self.imgbox.ReinitImage()        
        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = Dialog(None, image="C:/Users/Ivan/Desktop/bandeau_mailjet.jpg", tailleCadre=(220, 100))
    frm.ShowModal()
    app.MainLoop()
