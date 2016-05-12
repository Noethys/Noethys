#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import time
import threading
##from PIL import Image
import cv2
import cv2.cv as cv

from Ctrl import CTRL_Bandeau



CAMERA = None
CASCADE = None
DEFAULT_DEVICE_WIDTH = 0
DEFAULT_DEVICE_HEIGHT = 0

def InitCamera(port=0):
    """ Initialisation de la webcam """
    global CAMERA, CASCADE, DEFAULT_DEVICE_WIDTH, DEFAULT_DEVICE_HEIGHT
    try :
        CAMERA = cv.CreateCameraCapture(port)
        frame = cv.QueryFrame(CAMERA)
        if frame == None :
            return False
        DEFAULT_DEVICE_WIDTH = frame.width
        DEFAULT_DEVICE_HEIGHT = frame.height
        CASCADE = cv.Load(Chemins.GetStaticPath("Divers/haarcascade_frontalface_alt2.xml"))
        return True
    except Exception, err :
        print err
        return False




##class VideoCaptureThread(threading.Thread):
##    def __init__(self, control):
##        self.width = DEFAULT_DEVICE_WIDTH
##        self.height = DEFAULT_DEVICE_HEIGHT
##        self.control = control
##        self.isRunning =True
##        self.bmp = wx.NullBitmap
##
##        threading.Thread.__init__(self)
##
##    def stop(self):
##        self.isRunning = False
##
##    def run(self):
##        while self.isRunning:
##            
##            # Capture de l'image
##            frame = cv.QueryFrame(CAMERA)
##            cv.CvtColor(frame, frame, cv.CV_BGR2RGB)
##            Img = wx.EmptyImage(frame.width, frame.height)
##            Img.SetData(frame.tobytes())
##            self.bmp = wx.BitmapFromImage(Img)
##            width, height = frame.width, frame.height
##            
##            # Détection des visages
##            min_size = (20, 20)
##            image_scale = 2
##            haar_scale = 1.2
##            min_neighbors = 2
##            haar_flags = 0
##
##            gray = cv.CreateImage((frame.width, frame.height), 8, 1)
##            small_img = cv.CreateImage((cv.Round(frame.width / image_scale), cv.Round (frame.height / image_scale)), 8, 1)
##            cv.CvtColor(frame, gray, cv.CV_BGR2GRAY)
##            cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
##            cv.EqualizeHist(small_img, small_img)
##            
##            listeVisages = cv.HaarDetectObjects(small_img, CASCADE, cv.CreateMemStorage(0), haar_scale, min_neighbors, haar_flags, min_size)
##
##            # Affichage de l'image
##            x, y = (0, 0)
##            try:
##                width, height = self.control.GetSize()
##                if width > self.width:
##                    x = (width - self.width) / 2
##                if height > self.height:
##                    y = (height - self.height) / 2
##                dc = wx.BufferedDC(wx.ClientDC(self.control), wx.NullBitmap, wx.BUFFER_VIRTUAL_AREA)
##        
##                try :
##                    dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0)))
##                except :
##                    pass
##                dc.Clear()
##                dc.DrawBitmap(self.bmp, x, y)
##                
##                # Dessin des rectangles des visages
##                if listeVisages :
##                    for ((x, y, w, h), n) in listeVisages :
##                        dc.SetBrush(wx.TRANSPARENT_BRUSH)
##                        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
##                        dc.DrawRectangle(x* image_scale, y* image_scale, w* image_scale, h* image_scale)
##                    
##                del dc
##                del Img
##                
##            except TypeError:
##                pass
##            except wx.PyDeadObjectError:
##                pass
##                
##        self.isRunning = False


# -----------------------------------------------------------------------------------------------------------------------------

class CTRL_Video(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SUNKEN_BORDER):
        wx.Panel.__init__(self, parent, id, pos, size, style)
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.timer = wx.Timer(self, -1)
        self.fps = 30
        self.width = DEFAULT_DEVICE_WIDTH
        self.height = DEFAULT_DEVICE_HEIGHT
        self.bmp = wx.NullBitmap
        self.listeVisages = []
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)

    def OnClose(self, event):
        try : self.StopVideo()
        except : pass
    
    def IsRunning(self):
        return self.timer.IsRunning()

    def StopVideo(self):
        """Stop moving the text"""
        if self.timer.IsRunning() :
            self.timer.Stop()
    
    def SetFPS(self, fps=30):
        if self.timer.IsRunning():
            self.StopVideo() 
        self.fps = fps
        self.StartVideo() 
        
    def StartVideo(self):
        """Starts the text moving"""
        if not self.timer.IsRunning():
            self.timer.Start(1000 / self.fps)
    
    def OnTimer(self, event):
        self.Refresh() 
        
    def OnPaint(self, evt):
        if not self.timer.IsRunning() :
            dc = wx.BufferedDC(wx.ClientDC(self), wx.NullBitmap, wx.BUFFER_VIRTUAL_AREA)
            dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0)))
            return
            
        # Capture de l'image
        frame = cv.QueryFrame(CAMERA)
        cv.CvtColor(frame, frame, cv.CV_BGR2RGB)
        Img = wx.EmptyImage(frame.width, frame.height)
        Img.SetData(frame.tostring())
        self.bmp = wx.BitmapFromImage(Img)
        width, height = frame.width, frame.height
        
        # Détection des visages
        min_size = (20, 20)
        image_scale = 2
        haar_scale = 1.2
        min_neighbors = 2
        haar_flags = 0

        gray = cv.CreateImage((frame.width, frame.height), 8, 1)
        small_img = cv.CreateImage((cv.Round(frame.width / image_scale), cv.Round (frame.height / image_scale)), 8, 1)
        cv.CvtColor(frame, gray, cv.CV_BGR2GRAY)
        cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
        cv.EqualizeHist(small_img, small_img)
        
        listeVisages = cv.HaarDetectObjects(small_img, CASCADE, cv.CreateMemStorage(0), haar_scale, min_neighbors, haar_flags, min_size)

        # Affichage de l'image
        x, y = (0, 0)
        try:
            dc = wx.BufferedDC(wx.ClientDC(self), wx.NullBitmap, wx.BUFFER_VIRTUAL_AREA)
            try :
                dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0)))
            except :
                pass
            dc.Clear()
            dc.DrawBitmap(self.bmp, x, y)
            
            # Dessin des rectangles des visages
            if listeVisages :
                for ((x, y, w, h), n) in listeVisages :
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
                    dc.DrawRectangle(x* image_scale, y* image_scale, w* image_scale, h* image_scale)
            
            self.listeVisages = listeVisages
            del dc
            del Img
            
        except TypeError:
            pass
        except wx.PyDeadObjectError:
            pass

    def OnErase(self, evt):
        """Noop because of double buffering"""
        pass


# -----------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Depots", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.port = 0
        self.image = None

        # Bandeau
        intro = _(u"Vous pouvez ici capturer une photo à partir d'une webcam connectée. Cliquez sur le bouton 'Prendre une photo' pour capturer l'image puis sur 'Ok' pour valider et ouvrir l'éditeur photo qui vous permettra d'effectuer un recadrage avant l'insertion dans la fiche individuelle.")
        titre = _(u"Capture d'une photo")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Webcam.png")
        
        # Vidéo
        self.ctrl_video = CTRL_Video(self, -1)
        self.bouton_capture = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Capturer_photo.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.ctrl_ligne = wx.StaticLine(self, -1)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.bouton_ok.Enable(False)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCapture, self.bouton_capture)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Lancement de la capture vidéo
        wx.CallLater(10, self.Initialisation)
        
    def SetPort(self, port=0):
        self.port = port
    
    def Initialisation(self):
        self.ctrl_video.StopVideo()
        etat = InitCamera(self.port)
        if etat == True :
            self.ctrl_video.StartVideo()
        else:
            dlg = wx.MessageDialog(self, _(u"Noethys n'a pas réussi à se connecter à la caméra.\nVeuillez vérifier que celle-ci est bien installée..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def __set_properties(self):
        self.bouton_capture.SetToolTipString(_(u"Cliquez ici pour prendre la photo"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_options.SetToolTipString(_(u"Cliquez ici pour définir les propriétés de la capture vidéo"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((670, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_video, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.bouton_capture, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_ligne, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonCapture(self, event): 
        """ Capture de la photo """
        if self.ctrl_video.IsRunning() :
            self.ctrl_video.StopVideo()
            self.image = self.ctrl_video.bmp
            self.listeVisages = self.ctrl_video.listeVisages
            self.bouton_capture.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Capturer_photo2.png"), wx.BITMAP_TYPE_ANY))
            self.bouton_ok.Enable(True)
        else:
            self.ctrl_video.StartVideo()
            self.bouton_capture.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Capturer_photo.png"), wx.BITMAP_TYPE_ANY))
            self.bouton_ok.Enable(False)
    
    def GetImage(self):
        return self.image
    
    def GetListeVisages(self):
        return self.listeVisages
    
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Photo")

    def OnBoutonOptions(self, event): 
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        sousMenuPort = wx.Menu()
        for index in range(0, 10) :
            id = 10000 + index
            item = wx.MenuItem(sousMenuPort, id, _(u"Port n°%d") % index, _(u"Port n°%d") % index, wx.ITEM_CHECK)
            sousMenuPort.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_port, id=id)
            if self.port == index : item.Check(True)
        menuPop.AppendMenu(10, _(u"Port de connexion"), sousMenuPort)

        sousMenuFPS = wx.Menu()
        for index in (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100) :
            id = 20000 + index
            item = wx.MenuItem(sousMenuFPS, id, u"%d" % index, _(u"%d images par secondes") % index, wx.ITEM_CHECK)
            sousMenuFPS.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_fps, id=id)
            if self.ctrl_video.fps == index : item.Check(True)
        menuPop.AppendMenu(20, _(u"Nombres d'images par secondes"), sousMenuFPS)

##        menuPop.AppendSeparator()
        
##        menuPop.AppendItem(wx.MenuItem(menuPop, 10, _(u"Propriétés du flux vidéo")))
##        self.Bind(wx.EVT_MENU, self.Menu_proprietes_pin, id=10)
        
##        menuPop.AppendItem(wx.MenuItem(menuPop, 20, _(u"Propriétés de la capture vidéo")))
##        self.Bind(wx.EVT_MENU, self.Menu_proprietes_filter, id=20)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Menu_port(self, event):
        id = event.GetId() - 10000
        self.SetPort(id)
        self.Initialisation()

    def Menu_fps(self, event):
        id = event.GetId() - 20000
        self.ctrl_video.SetFPS(id)

    def Menu_proprietes_pin(self, event):
        if self.ctrl_video.IsRunning() == False :
            dlg = wx.MessageDialog(self, _(u"La caméra n'est pas connectée !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        CAMERA.displayCapturePinProperties() 
    
    def Menu_proprietes_filter(self, event):
        if self.ctrl_video.IsRunning() == False :
            dlg = wx.MessageDialog(self, _(u"La caméra n'est pas connectée !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        CAMERA.displayCaptureFilterProperties() 
    
    def FermeVideo(self):
        self.ctrl_video.StopVideo()
        time.sleep(1)
        global CAMERA
        if CAMERA != None :
            del CAMERA

    def OnBoutonOk(self, event): 
        if self.image == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord capturer une image !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        self.FermeVideo() 
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event): 
        self.FermeVideo() 
        self.EndModal(wx.ID_CANCEL)

    def OnClose(self, event):
        self.OnBoutonAnnuler(None)
    
    
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
