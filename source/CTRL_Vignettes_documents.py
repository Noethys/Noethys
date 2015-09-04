#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
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
import FonctionsPerso

from Outils import thumbnailctrl as TC

import GestionDB

try: import psyco; psyco.full()
except: pass

ID_AJOUTER = wx.NewId() 
ID_ROTATION_GAUCHE = wx.NewId() 
ID_ROTATION_DROITE = wx.NewId() 
ID_MODIFIER_LABEL = wx.NewId() 
ID_SUPPRIMER = wx.NewId() 
ID_VISUALISER = wx.NewId() 


DICT_TYPES = {
    "pdf" : "Images/128x128/pdf.png",
    "doc" : "Images/128x128/doc.png",
    "docx" : "Images/128x128/docx.png",
    "xls" : "Images/128x128/xls.png",
    "xlsx" : "Images/128x128/xlsx.png",
    "zip" : "Images/128x128/zip.png",
    "txt" : "Images/128x128/txt.png",
    }
    
    
def ChargeImage(fichier):
    """Read a file into PIL Image object. Return the image and file size"""
    buf=cStringIO.StringIO()
    f=open(fichier,"rb")
    while 1:
        rdbuf=f.read(8192)
        if not rdbuf: break
        buf.write(rdbuf)
    f.close()
    buf.seek(0)
    image = Image.open(buf).convert("RGB")
    return image, len(buf.getvalue())

##def wxtopil(image):
##    """Convert wx.Image to PIL Image."""
##    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
##    pil.fromstring(image.GetData())
##    return pil

##def piltowx(image):
##    """Convert a PIL image to wx image format"""
##    largeur, hauteur = image.size
##    imagewx = wx.EmptyImage(largeur, hauteur)
##    imagewx.SetData(image.tostring('raw', 'RGB'))
##    imagewx.SetAlphaData(image.convert("RGBA").tostring()[3::4])
##    return imagewx        

def wxtopil(wxImage, wantAlpha=True):  
    pilImage = Image.new( 'RGB', (wxImage.GetWidth(), wxImage.GetHeight()), color=(255, 255, 255) )
    pilImage.fromstring(wxImage.GetData())
    if wxImage.HasAlpha() and wantAlpha :  
        pilImage.convert( 'RGBA' )            
        wxAlphaStr = wxImage.GetAlphaData()    
        pilAlphaImage = Image.new( 'L', (wxImage.GetWidth(), wxImage.GetHeight()) )
        pilAlphaImage = Image.fromstring( 'L', (wxImage.GetWidth(), wxImage.GetHeight()), wxAlphaStr )
        pilImage.putalpha(pilAlphaImage) 
    return pilImage


class Track(object):
    def __init__(self, IDdocument=None, IDpiece=None, IDreponse=None, buffer=None, type=None, image=None, label=u""):
        self.IDdocument = IDdocument
        self.IDpiece = IDpiece
        self.IDreponse = IDreponse
        self.buffer = buffer
        self.type = type
        self.isImage = None
        self.image = image
        self.label = label
        
        if self.label == None :
            self.label = u""
        
        if image == None :
            self.image =self.GetImage() 

    def GetImage(self):
        # Si c'est une image :
        if self.type in ("jpg", "jpeg", "bmp", "png", "gif", None) :
            io = cStringIO.StringIO(self.buffer)
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
            img = wxtopil(img)
            self.isImage = True
            return img
        # Si c'est un document :
        if DICT_TYPES.has_key(self.type) :        
            cheminImage = DICT_TYPES[self.type]
            img = Image.open(cheminImage)
            self.isImage = False
            return img
        return None

    def GetInfobulle(self):
        if self.isImage == True :
            typeDoc = _(u"Image")
        else:
            typeDoc = _(u"Document")
        if self.label == "" :
            titre = u""
        else:
            titre = u"'%s'" % self.label
        if self.type != None :
            typeTemp = self.type.upper()
        else :
            typeTemp = u""
        texte = _(u"%s %s\n%s\n\nDouble-cliquez pour visualiser ce document") % (typeDoc, typeTemp, titre)
        return texte


class CTRL(TC.ThumbnailCtrl):
    def __init__(self, parent, IDpiece=None, IDreponse=None, 
                                         afficheLabels=True, tailleVignette=128,
                                         style=0):
        TC.ThumbnailCtrl.__init__(self, parent, style=style)
        self.SetThumbOutline(TC.THUMB_OUTLINE_IMAGE)
        self.IDpiece = IDpiece
        self.IDreponse = IDreponse
        
        self.listePages = []
        self.listePagesInitiale = []
        
        # Paramètres du Ctrl
        self.ShowFileNames(afficheLabels)
        self.EnableToolTips(True)
        contextMenu = self.ContextMenu()
        self.SetPopupMenu(contextMenu)
        self.SetThumbSize(tailleVignette, tailleVignette, 6)
        
        # Importation initiale des images
        self.ImportationImages()
        self.MAJ() 
        
        # Binds
        self.Bind(TC.EVT_THUMBNAILS_DCLICK, self.OnDoubleClick)

    def SetIDreponse(self, IDreponse=None):
        self.IDreponse = IDreponse
        self.ImportationImages()
        self.MAJ() 
        
    def OnDoubleClick(self, event):
        self.VisualiserPage(None)        
        
    def ImportationImages(self):
        self.listePages = []
        listeDonnees = []
        # Recherche des images dans la base de données
        if self.IDpiece != None :
            req = "SELECT IDdocument, IDpiece, IDreponse, document, type, label FROM documents WHERE IDpiece=%d AND document IS NOT NULL;" % self.IDpiece
        elif self.IDreponse != None :
            req = "SELECT IDdocument, IDpiece, IDreponse, document, type, label FROM documents WHERE IDreponse=%d AND document IS NOT NULL;" % self.IDreponse
        else:
            return
        db = GestionDB.DB(suffixe="DOCUMENTS")
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDdocument, IDpiece, IDreponse, buffer, type, label in listeDonnees :
            track = Track(IDdocument=IDdocument, IDpiece=IDpiece, IDreponse=IDreponse, buffer=buffer, type=type, label=label)
            self.listePages.append(track)
            self.listePagesInitiale.append(track)
    
    def MAJ(self):
        self.AfficheImages(self.listePages)
        
    def AjouterPage(self, event=None):
        """ Ajouter une page """
        import DLG_Importation_page
        dlg = DLG_Importation_page.Dialog(self) 
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == 100 :
            # Importer depuis un dossier
            self.ImportationDossier() 
        elif reponse == 200 :
            # Importer depuis un scanner
            self.ImportationScanner()
        else:
            pass
    
    def SaisirLabel(self, label=u"", nomFichier=None):
        if nomFichier == None :
            message = _(u"Vous pouvez saisir un titre pour ce document (optionnel) :")
        else:
            message = _(u"Vous pouvez saisir un titre pour le document '%s' (optionnel) :") % nomFichier
        dlg = wx.TextEntryDialog(self, message, _(u"Titre du document"), label)
        if dlg.ShowModal() == wx.ID_OK:
            valeur = dlg.GetValue()
            return valeur
        dlg.Destroy()
        return None

    def ImportationDossier(self):
        # Sélection des documents
        self.repCourant = os.getcwd()
        wildcard = "Tous les documents|*.bmp; *.gif; *.jpg; *.png; *.pdf; *.zip, *.txt; *.doc; *.docx; *.xls; *.xlsx| \
Images JPEG (*.jpg)|*.jpg| \
Images PNG (*.png)|*.png| \
Images GIF (*.gif)|*.gif| \
Documents PDF (*.pdf)|*.pdf| \
Documents MS Word (*.doc, *.docx)|*.doc; *.docx| \
Documents MS Excel (*.xls, *.xlsx)|*.xls; *.xlsx| \
Archives ZIP (*.zip)|*.zip| \
Fichiers Texte (*.txt)|*.txt| \
Tous les fichiers (*.*)|*.*"

        # Récupération du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        
        # Ouverture de la fenêtre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Sélectionnez un ou plusieurs documents"),
            defaultDir=cheminDefaut, 
            defaultFile="", 
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE
            )
        if dlg.ShowModal() == wx.ID_OK:
            listeFichiers = dlg.GetPaths()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Recadre l'image
        for fichier in listeFichiers :
            extension = os.path.splitext(fichier)[1].replace(".", "")
            nomFichierCourt = os.path.basename(fichier)
            
            if extension in ("jpeg", "jpg", "png", "bmp", "gif"):
                # Si c'est une image :
                imgPIL, poidsImg = ChargeImage(fichier)
                blob = self.GetBufferImage(imgPIL)
            
            else :
                # Si c'est un document :
                file = open(fichier, "rb")
                data = file.read()
                file.close() 
                
                # Met le fichier dans un buffer
                buffer = cStringIO.StringIO(data)
                blob = buffer.read()
        
            # Demande le titre du document
            label = self.SaisirLabel(nomFichier=nomFichierCourt)
            
            # Conserve l'image en mémoire
            track = Track(IDdocument=0, IDpiece=self.IDpiece, buffer=blob, type=extension, label=label)
            self.listePages.append(track)
        
        # MAJ de l'affichage
        self.MAJ() 
    
    def GetBufferImage(self, imgPIL=None):
        # Redimensionne l'image si besoin
        tailleMaxi = 1000
        largeur, hauteur = imgPIL.size
        if max(largeur, hauteur) > tailleMaxi :
            if largeur > hauteur :
                hauteur = hauteur * tailleMaxi / largeur
                largeur = tailleMaxi
            else:
                largeur = largeur * tailleMaxi / hauteur
                hauteur = tailleMaxi
            imgPIL = imgPIL.resize((largeur, hauteur), Image.ANTIALIAS) #.Rescale(width=largeur, height=hauteur, quality=qualite) 
        
        # Met l'image dans un buffer
        buffer = cStringIO.StringIO()
        imgPIL.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        blob = buffer.read()
        return blob
    
    def GetNbreDocuments(self):
        return len(self.listePages)
    
    def Sauvegarde(self, IDpieceFinal=None, IDreponseFinal=None):
        nbreDocuments = len(self.listePages)
        if len(self.listePages) == 0 and len(self.listePagesInitiale) == 0 : 
            return nbreDocuments
        
        # Insère les nouvelles images dans la base de données
        DB = GestionDB.DB(suffixe="DOCUMENTS")
        for track in self.listePages :
            if track.IDdocument == 0 :
                # Crée un document
                if IDpieceFinal != None :
                    listeDonnees = [("IDpiece", IDpieceFinal), ("type", track.type), ("label", track.label)]
                else:
                    listeDonnees = [("IDreponse", IDreponseFinal), ("type", track.type), ("label", track.label)]
                IDdocument = DB.ReqInsert("documents", listeDonnees)
                DB.MAJimage(table="documents", key="IDdocument", IDkey=IDdocument, blobImage=track.buffer, nomChampBlob="document")
        
        # Suppression dans la base de données
        for track in self.listePagesInitiale :
            if track not in self.listePages :
                DB.ReqDEL("documents", "IDdocument", track.IDdocument)
        
        DB.Close()
        return nbreDocuments
    
    def ImportationScanner(self):
        dlg = wx.MessageDialog(self, _(u"Désolé, cette fonction n'est pas encore disponible !"), _(u"Fonction indisponible"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def SupprimerPage(self, event):
        index = self.GetSelection()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un document !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        thumb = self.GetItem(index)
        track = thumb.track
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la suppression de ce document ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
                return
        
        self.listePages.remove(track)
        self.MAJ() 
        
    def ContextMenu(self):
        menu = wx.Menu()

        item = wx.MenuItem(menu, ID_AJOUTER, _(u"Ajouter des documents"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AjouterPage, id=ID_AJOUTER)
        
        menu.AppendSeparator()
        
        item = wx.MenuItem(menu, ID_ROTATION_GAUCHE, _(u"Pivoter à gauche"))
        item.SetBitmap(wx.Bitmap("Images/Teamword/annuler.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.RotationGauche, id=ID_ROTATION_GAUCHE)
        
        item = wx.MenuItem(menu, ID_ROTATION_DROITE, _(u"Pivoter à droite"))
        item.SetBitmap(wx.Bitmap("Images/Teamword/repeter.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.RotationDroite, id=ID_ROTATION_DROITE)
        
        menu.AppendSeparator()
        
        item = wx.MenuItem(menu, ID_VISUALISER, _(u"Visualiser"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.VisualiserPage, id=ID_VISUALISER)
        
        menu.AppendSeparator()

        item = wx.MenuItem(menu, ID_MODIFIER_LABEL, _(u"Modifier le titre"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ModifierLabel, id=ID_MODIFIER_LABEL)

        item = wx.MenuItem(menu, ID_SUPPRIMER, _(u"Supprimer"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SupprimerPage, id=ID_SUPPRIMER)

        return menu
    
    def OnContextMenu(self):
        menu = self.ContextMenu() 
        self.PopupMenu(menu)
        menu.Destroy()
        
    def RotationGauche(self, event):
        index = self.GetSelection()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une image !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        thumb = self.GetItem(index)
        track = thumb.track
        if track.isImage == False : 
            dlg = wx.MessageDialog(self, _(u"Ce document n'est pas une image !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self._scrolled.Rotate(90)
    
    def RotationDroite(self, event):
        index = self.GetSelection()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une image !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        thumb = self.GetItem(index)
        track = thumb.track
        if track.isImage == False : 
            dlg = wx.MessageDialog(self, _(u"Ce document n'est pas une image !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self._scrolled.Rotate(-90)
    
    def ModifierLabel(self, event):
        index = self.GetSelection()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un document !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        thumb = self.GetItem(index)
        track = thumb.track
        # Demande le nouveau titre du document
        label = self.SaisirLabel(label=track.label)
        if label == None : 
            return
        track.label = label
        self.MAJ() 
        
    def VisualiserPage(self, event):
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un document !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        thumb = self.GetItem(index)
        track = thumb.track
        
        if track.isImage == True :
            # Ouvrir Editeur Photo
            import DLG_Visualiseur_image
            dlg = DLG_Visualiseur_image.MyFrame(None, imgPIL=track.image)
            dlg.Show(True)
        else:
            # Création du doc dans le répertoire Temp et ouverture
            nomFichier = _(u"Temp/document.%s") % track.type
            buffer = track.buffer
            file = open(nomFichier,"wb")
            file.write(buffer)
            file.close()
            FonctionsPerso.LanceFichierExterne(nomFichier)
    
    def ZoomPlus(self):
        self.ZoomIn()
        
    def ZoomMoins(self):
        self.ZoomOut()
        
    def Test1(self):
        self.AjouterPage() 
        
    def Test2(self):
        index = self.GetSelection()
        thumb = self.GetItem(index)
        track = thumb.track
        imgPIL = track.image
        
        buffer = track.buffer
        file = open ("Temp/test.%s" % track.type,"wb")
        file.write(buffer.getvalue())
        file.close()

##        print "taille pour sauvegarde : ", imgPIL.size
##        imgPIL.save("testScan.jpg", "JPEG", quality=100)
##        print "Image sauvegardee dans le repertoire en cours..."


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, IDpiece=18)
        self.bouton_1 = CTRL_Bouton_image.CTRL(panel, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_2 = CTRL_Bouton_image.CTRL(panel, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.EXPAND|wx.ALL, 10)
        sizer_2.Add(self.bouton_1, 0, wx.EXPAND|wx.ALL, 10)
        sizer_2.Add(self.bouton_2, 0, wx.EXPAND|wx.ALL, 10)
        panel.SetSizer(sizer_2)
        self.SetSize((550, 550))
        self.Layout()
        self.CenterOnScreen() 
        
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton_1)
        self.Bind(wx.EVT_BUTTON, self.OnBouton2, self.bouton_2)
        
    def OnBouton1(self, event):
        self.ctrl.Test1()

    def OnBouton2(self, event):
        self.ctrl.Test2()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", name="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
