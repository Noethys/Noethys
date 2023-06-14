#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import Chemins
from Utils import UTILS_Adaptations
from Ctrl import CTRL_Bouton_image

def RedimensionneImage(bmp, largeur, hauteur):
    image = bmp.ConvertToImage()
    image = image.Scale(largeur, hauteur, quality=wx.IMAGE_QUALITY_HIGH)
    bmp = image.ConvertToBitmap() 
    return bmp



##---MODELES

class Objet():
    def __init__(self, interface, id=None, nom=None, categorie=None, position=None, taille=None, bmp=None, bmp_survol=None, bmp_enfonce=None, donnees={}):
        self.interface = interface
        self.dc = interface.pdc
        self.id = None
        self.nom = nom
        self.categorie = categorie
        self.position = position
        self.taille = taille
        self.donnees = donnees
        
        # Autres variables
        self.onLeftDown = False
        self.onLeftUp = False
        self.onMotion = False
        self.bmp = bmp
        self.bmp_survol = bmp_survol
        self.bmp_enfonce = bmp_enfonce
        self.objetImageSurvol = None
        self.objetImageEnfonce = None
            
    def Afficher(self):
        if self.id == None :
            if 'phoenix' not in wx.PlatformInfo:
                self.dc.BeginDrawing()
            # Init objet pseudoDC
            self.id = wx.Window.NewControlId()
            self.dc.SetId(self.id)
            # Dessine l'objet
            self.Draw() 
            # M�morise l'objet
            self.dc.SetIdBounds(self.id, wx.Rect(int(self.position[0]), int(self.position[1]), int(self.taille[0]), int(self.taille[1])))
            self.interface.dictObjets[self.id] = self
            if 'phoenix' not in wx.PlatformInfo:
                self.dc.EndDrawing()
            self.interface.Refresh() 
    
    def Cacher(self):
        self.EffaceSurvol() 
        self.EffaceEnfonce() 
        if self.id != None :
            # Supprime l'objet
            self.dc.RemoveId(self.id)
            del self.interface.dictObjets[self.id]
            self.id = None
            # Supprime �galement les images de survole ou enfonce
            if self.objetImageSurvol != None : 
                self.dc.RemoveId(self.objetImageSurvol)
                self.objetImageSurvol = None
            if self.objetImageEnfonce != None : 
                self.dc.RemoveId(self.objetImageEnfonce)
                self.objetImageEnfonce = None
            # MAJ Affichage
            self.interface.Refresh() 
    
    def EstVisible(self):
        if self.id == None :
            return False
        else: 
            return True
    
    def Centrer(self, orientation=wx.HORIZONTAL):
        """ Centre l'objet au milieu de la fen�tre parente """
        if self.id == None : return
        tailleDC = self.interface.GetSize() 
        x, y = self.position
        if orientation == wx.HORIZONTAL : x = (tailleDC[0]-self.taille[0])/2.0
        if orientation == wx.VERTICAL: y = (tailleDC[1]-self.taille[1])/2.0
        dx, dy = x-self.position[0], y-self.position[1]
        self.Deplacer(dx, dy)
        
    def Draw(self):
        pass
        
    def OnLeftDown(self):
        pass    
        
    def OnLeftUp(self):
        """ Efface l'image enfonc�e """
        pass
        
    def OnMotion(self):
        pass
    
    def EffaceSurvol(self):
        """ Efface l'image de survol """
        if self.objetImageSurvol != None :
            self.dc.RemoveId(self.objetImageSurvol)
            self.objetImageSurvol = None
    
    def EffaceEnfonce(self):
        if self.objetImageEnfonce != None :
            self.dc.RemoveId(self.objetImageEnfonce)
            self.objetImageEnfonce = None
            self.OnMotion() 
    
    def Deplacer(self, dx=0, dy=0):
        if self.id == None : return
        self.position = self.position[0]+dx, self.position[1]+dy
        self.dc.TranslateId(self.id, dx, dy)
        self.interface.Refresh() 
        
    def Action(self):
        pass



class Bouton(Objet):
    def __init__(self, parent, *args, **kwds):
        Objet.__init__(self, parent, *args, **kwds)
        self.onLeftDown = True
        self.onLeftUp = True
        self.onMotion = True
        
    def Draw(self):
        # Dessin de l'image
        self.dc.DrawBitmap(self.bmp, int(self.position[0]), int(self.position[1]))
    
    def DessineImagesRemplacement(self, bmp):
        # Dessin de l'image
        if 'phoenix' not in wx.PlatformInfo:
            self.dc.BeginDrawing()
        id = wx.Window.NewControlId()
        self.dc.SetId(id)
        
        self.dc.DrawBitmap(bmp, int(self.position[0]), int(self.position[1]))
        self.dc.SetIdBounds(id, wx.Rect(int(self.position[0]), int(self.position[1]), self.taille[0], self.taille[1]))
        if 'phoenix' not in wx.PlatformInfo:
            self.dc.EndDrawing()
        return id
        
    def OnLeftDown(self, actionActive=True):
        if self.onLeftDown == True :
            self.EffaceSurvol() 
            id = self.DessineImagesRemplacement(self.bmp_enfonce)
            self.objetImageEnfonce = id
            self.interface.Refresh()        
            if actionActive == True :    
                self.Action() 

    def OnLeftUp(self):
        """ Efface l'image enfonc�e """
        if self.onLeftUp == True :
            self.EffaceEnfonce() 

    def OnMotion(self):
        if self.onMotion == True and self.objetImageSurvol == None :
            id = self.DessineImagesRemplacement(self.bmp_survol)
            self.objetImageSurvol = id
            self.interface.Refresh()

    def Action(self):
        pass

    def EnfonceBouton(self, actionActive=True):
        self.OnLeftDown(actionActive)
        wx.CallLater(200, self.ReleveBouton)
    
    def ReleveBouton(self):
        self.EffaceEnfonce()
        self.EffaceSurvol()




class Groupe():
    def __init__(self, interface=None, nom="", position=None, donnees={}):
        self.interface = interface
        self.nom = nom
        self.position = position
        self.donnees = donnees
        self.listeObjets = []
        self.listeControles = [] # Contr�les r�els rattach�s
        
    def Ajouter(self, objetDC=None):
        """ Ajoute un objet dans le groupe """
        self.listeObjets.append(objetDC)
        
    def RattacherControle(self, ctrl=None):
        # Pour rattacher une contr�les r�el
        self.listeControles.append(ctrl)
        
    def Afficher(self):
        for objet in self.listeObjets :
            objet.Afficher()
        for ctrl in self.listeControles :
            ctrl.Show(True)
            try :
                ctrl.Activer()
            except :
                pass
        
    def Cacher(self):
        for objet in self.listeObjets :
            objet.Cacher()
        for ctrl in self.listeControles :
            ctrl.Show(False)
    
    def EstVisible(self):
        for objet in self.listeObjets :
            if objet.EstVisible() :
                return True
        return False
    
    def Centrer(self, orientation=wx.HORIZONTAL):
        if self.EstVisible() == False : return
        # Recherche de la taille du groupe
        largeur, hauteur = 0, 0
        for objet in self.listeObjets :
            if objet.taille[0] > largeur : largeur = objet.taille[0]
            if objet.taille[1] > hauteur : hauteur = objet.taille[1]
        
        # Calcul de la nouvelle position
        tailleDC = self.interface.GetSize() 
        x, y = self.position
        if orientation == wx.HORIZONTAL : x = (tailleDC[0]-largeur)/2.0
        if orientation == wx.VERTICAL: y = (tailleDC[1]-hauteur)/2.0
        dx, dy = x-self.position[0], y-self.position[1]

        self.Deplacer(dx, dy)

##        for objet in self.listeObjets :
##            objet.Centrer()
##        for ctrl in self.listeControles :
##            tailleCtrl = ctrl.GetSize() 
##            positionCtrl = ctrl.GetPosition()
##            x, y = positionCtrl
##            if orientation == wx.HORIZONTAL : x = (tailleDC[0]-tailleCtrl[0])/2.0
##            if orientation == wx.VERTICAL: y = (tailleDC[1]-tailleCtrl[1])/2.0
##            ctrl.SetPosition((x, y))
        
    def Deplacer(self, dx=0, dy=0):
        self.position = self.position[0]+dx, self.position[1]+dy
        for objet in self.listeObjets :
            objet.Deplacer(dx, dy)
        for ctrl in self.listeControles :
            x, y = ctrl.GetPosition() 
            ctrl.SetPosition((x+dx, y+dy))
            
# ---------------------------------------------------------------------------------------------------------------------------------

##---OBJETS
class Barre_numerique(Objet):
    def __init__(self, parent, *args, **kwds):
        Objet.__init__(self, parent, *args, **kwds)
    def Draw(self):
        self.bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s_barrenum.png" % self.interface.GetStyle()))
        self.taille = self.bmp.GetSize() 
        x, y = self.position
        
        # Dessin du fond de la barre num�rique
        self.dc.DrawBitmap(self.bmp, int(x), int(y))
        

class Groupe_barre_numerique(Groupe):
    """ Tout le clavier num�rique """
    def __init__(self, parent, *args, **kwds):
        Groupe.__init__(self, parent, *args, **kwds)
        x, y, = self.position
        
        # Dessin du fond de la barre
        barreNum = Barre_numerique(self.interface, nom="fond", categorie="clavier_numerique", position=self.position)
        self.Ajouter(barreNum)
        
        # Rattachement du CTRL_Barre_numerique
        ctrl_barre = self.interface.ctrl_barre_numerique
        ctrl_barre.SetPosition((x+35, y+27))
        ctrl_barre.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL))
        ctrl_barre.SetSize((278, 38))
        self.RattacherControle(ctrl_barre)


# ---------------------------------------------------------------------------------------------------------------------------------

class Fond_clavier_numerique(Objet):
    def __init__(self, parent, *args, **kwds):
        Objet.__init__(self, parent, *args, **kwds)
    def Draw(self):
        # Dessin du fond du clavier num�rique
        self.bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s_claviernum.png" % self.interface.GetStyle()))
        self.taille = self.bmp.GetSize()
        self.dc.DrawBitmap(self.bmp, int(self.position[0]), int(self.position[1]))
        
        
# ---------------------------------------------------------------------------------------------------------------------------------

class Touche_clavier_numerique(Bouton):
    def __init__(self, parent, *args, **kwds):
        Bouton.__init__(self, parent, *args, **kwds)
        
    def Action(self):
        self.interface.ctrl_barre_numerique.ReceptionTouche(self.nom)


class Groupe_clavier_numerique(Groupe):
    """ Tout le clavier num�rique """
    def __init__(self, parent, *args, **kwds):
        Groupe.__init__(self, parent, *args, **kwds)
        
        # Dessin du fond
        clavierNum = Fond_clavier_numerique(self.interface, nom="fond", categorie="clavier_numerique", position=self.position)
        self.Ajouter(clavierNum)
        
        clavierNum.Afficher()
        clavierNum.Cacher()
        
        # Dessin des touches
        self.listeTouches = ("Efface", "0", "Validation", "1", "2", "3", "4", "5", "6", "7", "8", "9")
        espace = 5
        marge = 20
        
        tailleTouche = (clavierNum.taille[0]-(espace*2.0)-(marge*2.0))/3.0
        xClavier, yClavier = clavierNum.position
        x, y = xClavier+marge, yClavier+clavierNum.taille[1]-marge-tailleTouche
        self.dictTouches = {}
        for nomTouche in self.listeTouches :
            
            # Cr�ation image normale
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s.png" % nomTouche), wx.BITMAP_TYPE_PNG)
            image = bmp.ConvertToImage()
    
            # Image survol
            image = image.AdjustChannels(1.0, 1.0, 2.9, 1.0) # (1.4, 1.0, 1.0, 1.0)
            bmp_survol = image.ConvertToBitmap() 
            
            # Image Enfoncee
            image = image.AdjustChannels(0.7, 0.7, 0.7, 1.0)
            bmp_enfonce = image.ConvertToBitmap() 
            
            # Cr�ation Touche du clavier
            toucheNum = Touche_clavier_numerique(self.interface, nom=nomTouche, categorie="clavier_numerique", position=(x, y), taille=(tailleTouche, tailleTouche), bmp=bmp, bmp_survol=bmp_survol, bmp_enfonce=bmp_enfonce)
            self.Ajouter(toucheNum)
            self.dictTouches[nomTouche] = toucheNum
            
            x += tailleTouche + espace
            if x >= xClavier + clavierNum.taille[0] - (marge*2.0) :
                x = xClavier+marge
                y -= tailleTouche + espace

    def EnfonceBouton(self, touche=""):
        if touche in self.dictTouches :
            self.dictTouches[touche].EnfonceBouton(actionActive=False)




# ------------------------------------------------------------------------------------------------------------------------------------

class Fond_liste_individus(Objet):
    def __init__(self, parent, *args, **kwds):
        Objet.__init__(self, parent, *args, **kwds)
    def Draw(self):
        # Dessin du fond du clavier num�rique
        self.bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s_listeindividus.png" % self.interface.GetStyle()))
        self.taille = self.bmp.GetSize() 
        self.dc.DrawBitmap(self.bmp, int(self.position[0]), int(self.position[1]))
        

class Touche_liste_individus(Bouton):
    def __init__(self, parent, *args, **kwds):
        Bouton.__init__(self, parent, *args, **kwds)
        
    def Action(self):
        if self.nom == "Haut" : self.interface.ctrl_liste_individus.Monter()
        if self.nom == "Bas" : self.interface.ctrl_liste_individus.Descendre()
        if self.nom == "Efface" : self.interface.ctrl_liste_individus.Effacer()
        if self.nom == "Validation" : self.interface.ctrl_liste_individus.Valider()


class Groupe_liste_individus(Groupe):
    """ Liste des individus """
    def __init__(self, parent, *args, **kwds):
        Groupe.__init__(self, parent, *args, **kwds)
        x, y, = self.position

        # Dessin du fond
        fond = Fond_liste_individus(self.interface, nom="fond", categorie="liste_individus", position=self.position)
        self.Ajouter(fond)
        
        fond.Afficher()
        fond.Cacher() 

        tailleTouche = 73
        marge = 23
        xFond, yFond = fond.position
        largeurFond, hauteurFond = fond.taille

        # Cr�ation des boutons
        posxTouche = xFond+largeurFond-marge-tailleTouche
        listeTouches = [
            ("Haut", (posxTouche, yFond+marge) ),
            ("Bas", (posxTouche, yFond+marge+tailleTouche+10) ),
            ("Efface", (posxTouche, yFond+hauteurFond-marge-(tailleTouche*2)-10) ),
            ("Validation", (posxTouche, yFond+hauteurFond-marge-tailleTouche) ),
            ]

        self.dictTouches = {}
        for nomTouche, posTouche in listeTouches :
            
            # Cr�ation image normale
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s.png" % nomTouche), wx.BITMAP_TYPE_PNG)
            image = bmp.ConvertToImage()
    
            # Image survol
            image = image.AdjustChannels(2.0, 1.0, 1.0, 1.0) # (1.4, 1.0, 1.0, 1.0)
            bmp_survol = image.ConvertToBitmap() 
            
            # Image Enfoncee
            image = image.AdjustChannels(0.7, 0.7, 0.7, 1.0)
            bmp_enfonce = image.ConvertToBitmap() 
            
            # Cr�ation Touche du clavier
            toucheNum = Touche_liste_individus(self.interface, nom=nomTouche, categorie="liste_individus", position=posTouche, taille=(tailleTouche, tailleTouche), bmp=bmp, bmp_survol=bmp_survol, bmp_enfonce=bmp_enfonce)
            self.Ajouter(toucheNum)
            self.dictTouches[nomTouche] = toucheNum
            
        # Rattachement du CTRL_Barre_numerique
        ctrl = self.interface.ctrl_liste_individus
        ctrl.SetPosition((x+marge, y+marge))
        ctrl.SetSize((largeurFond-160, hauteurFond-(marge*2.0)))
        self.RattacherControle(ctrl)



# ------------------------------------------------------------------------------------------------------------------------------------

class Groupe_importation(Groupe):
    """ Liste des individus """
    def __init__(self, parent, *args, **kwds):
        Groupe.__init__(self, parent, *args, **kwds)
        x, y, = self.position

        # Dessin du fond
        fond = Fond_liste_individus(self.interface, nom="fond", categorie="liste_individus", position=self.position)
        self.Ajouter(fond)
        
        fond.Afficher()
        fond.Cacher() 

        tailleTouche = 73
        marge = 23
        xFond, yFond = fond.position
        largeurFond, hauteurFond = fond.taille
            
        # Rattachement du CTRL_Barre_numerique
        ctrl = self.interface.ctrl_importation
        ctrl.SetPosition((x+marge, y+marge))
        ctrl.SetSize((largeurFond-160, hauteurFond-(marge*2.0)))
        self.RattacherControle(ctrl)






if __name__ == u"__main__":
    from Dlg import DLG_Badgeage_interface
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = DLG_Badgeage_interface.Dialog(None, log=None, IDprocedure=1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
