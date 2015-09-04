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


TAILLE_IMAGE = (132, 72)


class CTRL(wx.StaticBitmap):
    def __init__(self, parent, table="", key="", IDkey=None, imageDefaut=None, tailleImage=TAILLE_IMAGE, style=0):
        wx.StaticBitmap.__init__(self, parent, id=-1, style=style)
        self.parent = parent
        self.SetMinSize(tailleImage) 
        self.SetSize(tailleImage) 
        
        # Pour la sauvegarde diff�r�e de l'image :
        self.bmpBuffer = None
        
        self.table = table
        self.key = key
        self.IDkey = IDkey
        self.imageDefaut = imageDefaut
        self.tailleImage = tailleImage

        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        self.SetBitmap(self.GetPhoto())

    def GetPhoto(self):
        """ R�cup�re une image """            
        # Recherche de l'image
        if self.IDkey != None : 
            DB = GestionDB.DB()
            req = "SELECT image FROM %s WHERE %s=%d;" % (self.table, self.key, self.IDkey)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                # Si une image est trouv�e
                self.bmpBuffer = listeDonnees[0][0]
                if self.bmpBuffer != None :
                    io = cStringIO.StringIO(self.bmpBuffer)
                    img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
                    bmp = img.Rescale(width=self.tailleImage[0], height=self.tailleImage[1], quality=wx.IMAGE_QUALITY_HIGH) 
                    bmp = bmp.ConvertToBitmap()
                    self.modeDefaut = False
                    return bmp
        
        # Si aucune image est trouv�e, on prend l'image par d�faut
        if self.imageDefaut != None :
            bmp = self.GetImageDefaut() 
            self.bmpBuffer = None
            return bmp
        
        self.bmpBuffer = None
        self.modeDefaut = False
        return None
    
    def GetImageDefaut(self):
        if os.path.isfile(self.imageDefaut):
            bmp = wx.Bitmap(self.imageDefaut, wx.BITMAP_TYPE_ANY) 
            bmp = bmp.ConvertToImage()
            bmp = bmp.Rescale(width=self.tailleImage[0], height=self.tailleImage[1], quality=wx.IMAGE_QUALITY_HIGH) 
            bmp = bmp.ConvertToBitmap()
            self.modeDefaut = True
            return bmp
        return None

    def Ajouter(self, sauvegarder=True):
        """ Permet la s�lection et le retouchage d'une image """
        # S�lection d'une image
        self.repCourant = os.getcwd()

        wildcard = "Toutes les images|*.jpg;*.png;*.gif|"     \
            "Image JPEG (*.jpg)|*.jpg|"     \
            "Image PNG (*.png)|*.png|"     \
            "Image GIF (*.gif)|*.gif|"     \
            "Tous les fichiers (*.*)|*.*"
                
        # R�cup�ration du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        
        # Ouverture dela fen�tre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une image"),
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
        
        # Recadre la photo
        import DLG_Editeur_photo
        dlg = DLG_Editeur_photo.Dialog(None, image=nomFichierLong, tailleCadre=TAILLE_IMAGE)
        if dlg.ShowModal() == wx.ID_OK:
            buffer = dlg.GetBuffer()
            tailleBmp = len(buffer.getvalue())
            self.bmpBuffer = buffer.read()
            bmp = dlg.GetBmp()
            dlg.Destroy()
            # Sauvegarde
            if sauvegarder == True :
                DB = GestionDB.DB()
                DB.MAJimage(self.table, self.key, self.IDkey, self.bmpBuffer)
                DB.Close()
            # Applique l'image
            self.SetBitmap(bmp)
        else:
            dlg.Destroy()
            return
    
    def Supprimer(self, sauvegarder=True):
        """ Suppression de l'image """
        if self.modeDefaut == True :
            dlg = wx.MessageDialog(self, _(u"Aucune image n'est enregistr�e !"), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        txtMessage = _(u"Souhaitez-vous vraiment supprimer cette image ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        # Suppression de l'image
        if sauvegarder == True :
            DB = GestionDB.DB()
            DB.ReqMAJ(self.table, [("image", None),], self.key, self.IDkey)
            DB.Close()
            
        # Applique l'image par d�faut
        self.SetBitmap(self.GetImageDefaut())
        self.bmpBuffer = None
    
    def Sauvegarder(self):
        """ Permet de sauvegarder ult�rieurement l'image """
        if self.bmpBuffer != None :
            # Sauvegarde d'une nouvelle image
            DB = GestionDB.DB()
            DB.MAJimage(self.table, self.key, self.IDkey, self.bmpBuffer)
            DB.Close()
        else:
            # Suppression d'une image
            DB = GestionDB.DB()
            DB.ReqMAJ(self.table, [("image", None),], self.key, self.IDkey)
            DB.Close()






class Dialog(wx.Dialog):
    def __init__(self, parent, IDmode=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        
        self.ctrl_image = CTRL(self, table="modes_reglements", key="IDmode", IDkey=1, imageDefaut="Images/Special/Image_non_disponible.png", style=wx.BORDER_SUNKEN)
        self.bouton_ajouter_image = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_image = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.ctrl_image, 0, wx.ALL, 4)
        sizer.Add(self.bouton_ajouter_image, 0, wx.ALL, 4)
        sizer.Add(self.bouton_supprimer_image, 0, wx.ALL, 4)
        self.SetSizer(sizer)
        self.Layout()
        self.CentreOnScreen()

        self.Bind(wx.EVT_BUTTON, self.OnAjouterImage, self.bouton_ajouter_image)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerImage, self.bouton_supprimer_image)

    def OnAjouterImage(self, event): 
        self.ctrl_image.Ajouter(sauvegarder=False)

    def OnSupprimerImage(self, event): 
        self.ctrl_image.Supprimer(sauvegarder=False)


if __name__ == u"__main__":
    app = wx.App(0)
    dialog_1 = Dialog(None, IDmode=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
