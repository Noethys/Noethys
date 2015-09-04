#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import CTRL_Bouton_image
import wx.html as html
import datetime
import sqlite3
import urllib
import urllib2
import FonctionsPerso

COULEUR_FOND = wx.Colour(240, 251, 237)


def ConvertVersionTuple(texteVersion=""):
    """ Convertit un numéro de version texte en tuple """
    tupleTemp = []
    for num in texteVersion.split(".") :
        tupleTemp.append(int(num))
    return tuple(tupleTemp)

def GetAnnonce():
    """ Fonction de récupération de l'annonce à afficher """
    dateJour = datetime.date.today() 
    dictAnnonce = None
    found = False
    
    # Recherche Annonce Internet
    try :
        fichierAnnonce = urllib2.urlopen('http://www.noethys.com/fichiers/annonce.txt', timeout=5)
        texteFichier = fichierAnnonce.read()
        fichierAnnonce.close()
        if "404 Not Found" not in texteFichier and len(texteFichier) > 10 :
            image, titre, texte_html, date_debut, date_fin, version = texteFichier.split(";")
            if date_debut <= str(dateJour) and date_fin >= str(dateJour) :
                if version != "" :
                    versionLogiciel = ConvertVersionTuple("1.0.5.6")#FonctionsPerso.GetVersionLogiciel())
                    version = ConvertVersionTuple(version)
                    if versionLogiciel < version :
                        dictAnnonce = {"IDannonce":None, "image":image, "titre":titre.decode("iso-8859-15"), "texte_html":texte_html.decode("iso-8859-15")}
                        found = True
                else :
                    dictAnnonce = {"IDannonce":None, "image":image, "titre":titre.decode("iso-8859-15"), "texte_html":texte_html.decode("iso-8859-15")}
                    found = True
    except :
        pass
        
    # Recherche Annonces stockées dans la base de données
    if found == False :
        
        try :
            
            # Init base de données
            con = sqlite3.connect("Annonces.dat")
            cur = con.cursor()
            
            def ListeEnDict(donnees):
                IDannonce, image, titre, texte_html = donnees
                dictAnnonce = {"IDannonce":IDannonce, "image":image, "titre":titre, "texte_html":texte_html}
                return dictAnnonce
                
            # Recherche dans les annonces DATES
            if found == False :
                req = """SELECT IDannonce, image, titre, texte_html FROM annonces_dates
                WHERE date_debut<='%s' AND date_fin>='%s'
                ORDER BY date_debut
                ;""" % (dateJour, dateJour)
                cur.execute(req)
                listeAnnonces = cur.fetchall()
                if len(listeAnnonces) > 0 :
                    dictAnnonce = ListeEnDict(listeAnnonces[0])
                    found = True
            
            # Recherche dans les annonces PERIODES
            if found == False :
                req = """SELECT IDannonce, image, titre, texte_html FROM annonces_periodes
                WHERE jour_debut<=%d AND mois_debut<=%d AND jour_fin>=%d AND mois_fin>=%d
                ORDER BY jour_debut, mois_debut
                ;""" % (dateJour.day, dateJour.month, dateJour.day, dateJour.month)
                cur.execute(req)
                listeAnnonces = cur.fetchall()
                if len(listeAnnonces) > 0 :
                    dictAnnonce = ListeEnDict(listeAnnonces[0])
                    found = True

            # Recherche dans les annonces ALEATOIRES
            if found == False :
                req = """SELECT IDannonce, image, titre, texte_html FROM annonces_aleatoires
                ORDER BY RANDOM() LIMIT 1
                ;"""
                cur.execute(req)
                listeAnnonces = cur.fetchall()
                if len(listeAnnonces) > 0 :
                    dictAnnonce = ListeEnDict(listeAnnonces[0])
                    found = True

            con.close()
        
        except :
            return None
    
    return dictAnnonce
    
    
    

class CTRL_html(html.HtmlWindow):
    def __init__(self, parent):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER )
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((368, 160))
    
    def SetTexte(self, texte=""):
        try :
            self.SetPage(u"""<BODY'><FONT SIZE=2>%s</FONT></BODY>""" % texte)
            self.SetBackgroundColour(COULEUR_FOND)
        except :
            pass
            

class Panel_Annonce(wx.Panel):
    def __init__(self, parent, size=(380, 210)):
        wx.Panel.__init__(self, parent, name="panel_annonce", id=-1, size=size, style=wx.TAB_TRAVERSAL)

        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Vide.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_titre = wx.StaticText(self, -1, u"")
        self.ctrl_texte = CTRL_html(self)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.ctrl_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=8, hgap=8)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_haut.Add(self.ctrl_image, 0, 0, 0)
        grid_sizer_haut.Add(self.ctrl_titre, 0, 0, 0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_texte, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def MAJannonce(self):
        try :
            dictAnnonce = GetAnnonce() 
            if dictAnnonce != None :
                
                # Affiche l'image
                nomImage = dictAnnonce["image"]
                bmp = wx.Bitmap("Images/16x16/%s.png" % nomImage, wx.BITMAP_TYPE_ANY)
                self.ctrl_image.SetBitmap(bmp)
                
                # Affiche le titre
                titre = dictAnnonce["titre"]
                self.ctrl_titre.SetLabel(titre)
                
                # Affiche le texte
                texte_html = dictAnnonce["texte_html"]
                self.ctrl_texte.SetTexte(texte_html)
            
            else :
                self.ctrl_texte.SetTexte(u"") 
                
        except :
            pass



class Panel_Titre(wx.Panel):
    def __init__(self, parent, size=(380, 210)):
        wx.Panel.__init__(self, parent, name="panel_titre", id=-1, size=size, style=wx.TAB_TRAVERSAL)
        
        self.image_titre = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/Accueil_titre.png", wx.BITMAP_TYPE_ANY), pos=(0, 0))
        anneeActuelle = str(datetime.date.today().year)
        texte = u"Copyright © 2010-%s Ivan LUCAS" % anneeActuelle[2:]
        
        self.SetForegroundColour("#6e933a")
        self.label_copyright = wx.StaticText(self, -1, texte, pos=(155, 105))
        self.label_copyright.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))



class Panel(wx.Panel):
    def __init__(self, parent, size=(-1, -1)):
        wx.Panel.__init__(self, parent, name="panel_accueil", id=-1, size=size, style=wx.TAB_TRAVERSAL)

        self.image_gauche_haut = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/Accueil_gauche_haut.png", wx.BITMAP_TYPE_ANY))
        self.image_gauche_bas = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/Accueil_gauche_bas.png", wx.BITMAP_TYPE_ANY))
        self.image_titre = Panel_Titre(self) # wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/Accueil_titre.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_annonce = Panel_Annonce(self) #wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/Accueil_annonce.png", wx.BITMAP_TYPE_ANY))
        self.image_droit_bas = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/Accueil_droit_bas.png", wx.BITMAP_TYPE_ANY))
        
        
        self.__set_properties()
        self.__do_layout()
        
        # Init contrôles
        self.MAJannonce() 

    def __set_properties(self):
        self.SetBackgroundColour(COULEUR_FOND)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_haut.Add(self.image_gauche_haut, 0, 0, 0)
        grid_sizer_haut.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_base.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.image_gauche_bas, 0, 0, 0)
        grid_sizer_bas.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.image_titre, 0, 0, 0)
        grid_sizer_bas.Add(self.ctrl_annonce, 0, wx.LEFT | wx.TOP, 12)
        grid_sizer_bas.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.image_droit_bas, 0, 0, 0)
        grid_sizer_bas.AddGrowableCol(1)
        grid_sizer_bas.AddGrowableCol(4)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def MAJannonce(self):
        self.ctrl_annonce.MAJannonce()



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((1100, 900))
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()