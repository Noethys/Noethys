#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import time
import os

import PIL.Image as Image
import PIL.ImageOps as ImageOps



def PILtoWx(image):
    """Convert a PIL image to wx image format"""
    largeur, hauteur = image.size
    imagewx = wx.EmptyImage(largeur, hauteur)
    imagewx.SetData(image.tostring('raw', 'RGB'))
    imagewx.SetAlphaData(image.convert("RGBA").tostring()[3::4])
    return imagewx        


class CTRL(wx.Button):
    def __init__(self, parent, id=-1, texte="", cheminImage=None, tailleImage=(20, 20), margesImage=(4, 0, 0, 0), positionImage=wx.LEFT, margesTexte=(0, 1)):
        wx.Button.__init__(self, parent, id=id, label=texte)
        self.parent = parent   
        self.texte = texte
        self.cheminImage = cheminImage
        self.tailleImage = tailleImage
        self.margesImage = margesImage
        self.positionImage = positionImage
        self.margesTexte = margesTexte
        self.MAJ() 
    
    def MAJ(self):
        # Redimensionne et ajoute des marges autour de l'image
        if self.cheminImage not in ("", None) :
            img = Image.open(self.cheminImage)
            img = img.resize(self.tailleImage, Image.ANTIALIAS)
            img = ImageOps.expand(img, border=self.margesImage)
            img = PILtoWx(img) 
            bmp = img.ConvertToBitmap()
        else :
            bmp = wx.NullBitmap
            
        # MAJ du bouton
        self.SetBitmap(bmp, self.positionImage)
        if self.cheminImage not in ("", None) :
            self.SetBitmapMargins(self.margesTexte)
        self.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.SetInitialSize() 
        
    def SetImage(self, cheminImage=""):
        self.SetBitmap(wx.NullBitmap)
        self.cheminImage = cheminImage
        self.MAJ() 
        
    def SetTexte(self, texte=""):
        self.texte = texte
        self.SetLabel(texte)
        self.MAJ() 
        
        
        
        
# -------------------------------------------- DLG de test -----------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        t1 = time.time() 
        
        self.label_test = wx.StaticText(self, wx.ID_ANY, _(u"Test :"))
        self.ctrl_test = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        
        self.bouton_aide1 = CTRL(self, texte=_(u"Transmettre\npar Email"), tailleImage=(32, 32), margesImage=(4, 4, 0, 0), margesTexte=(0, 1), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_aide2 = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok1 = CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_ok2 = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler1 = CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Fermer.png")
        self.bouton_annuler2 = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        print "Temps d'affichage =", time.time() - t1
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_aide1)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une traduction"))
        self.SetMinSize((670, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(4, 2, 10, 10)
        grid_sizer_haut.Add(self.label_test, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_haut.Add(self.ctrl_test, 0, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableRow(1)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 8, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide1, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide2, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok1, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok2, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler1, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler2, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnBoutonTest(self, event):
        self.bouton_aide1.SetImage("Images/32x32/Fermer.png")
        self.bouton_aide1.SetTexte("Coucou")
        
def ModifieFichiers():
    listeTextes = [
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")"""),
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")"""),
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")"""),
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")"""),
        ("""wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")"""),
        ("""wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")"""),
        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Imprimer_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")"""),
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Apercu_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")"""),        
        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Envoyer_par_email.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")"""),        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Envoyer_mail.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer l'Email"), cheminImage="Images/32x32/Emails_exp.png")"""),        
        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Rafraichir_liste.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")"""),        
        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Options_L72.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration.png")"""),        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Options.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")"""),        
        ("""wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Outils.png", wx.BITMAP_TYPE_ANY))""", """CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")"""),        
        
        
        ]
        
    # Get fichiers
    listeFichiers = os.listdir(os.getcwd())
    indexFichier = 0
    for nomFichier in listeFichiers :
        if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier != "CTRL_Bouton_image.py" :
            print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)
            
            # Ouverture des fichiers
            fichier = open(nomFichier, "r")
            dirty = False
            
            listeLignes = []
            for ligne in fichier :
                
                # Corrections diverses
                if "wx.BitmapButton(" in ligne :
                    if "wx.ID_ANY" in ligne : 
                        ligne = ligne.replace("wx.ID_ANY", "-1")
                        dirty = True
                    if """u"Images/BoutonsImages""" in ligne :
                        ligne = ligne.replace("""(u"Images/BoutonsImages""", """("Images/BoutonsImages""")
                        dirty = True
                        
                # Remplacement des chaines
                for texteAncien, texteNouveau in listeTextes :
                    if texteAncien in ligne : 
                        ligne = ligne.replace(texteAncien, texteNouveau)
                        dirty = True
                    
                # Ecriture du nouveau fichier
                listeLignes.append(ligne)
                
                # Insertion de l'import
##                if "import wx\n" in ligne :
##                    listeLignes.append("import CTRL_Bouton_image\n")
##                    dirty = True
                
            # Clôture des fichiers
            fichier.close()
            
            # Ecriture du nouveau fichier
            if dirty == True :
                nouveauFichier = open("New/%s" % nomFichier, "w")
                for ligne in listeLignes :
                    nouveauFichier.write(ligne)
                nouveauFichier.close()
            
        indexFichier += 1
            
    print "Fini !!!!!!!!!!!!!!!!!"



if __name__ == u"__main__":
##    ModifieFichiers() 
    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
