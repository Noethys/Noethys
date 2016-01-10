#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import datetime
import sqlite3
import urllib2
import UTILS_Interface
from wx.lib.wordwrap import wordwrap


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
    # try :
    #     fichierAnnonce = urllib2.urlopen('http://www.noethys.com/fichiers/annonce.txt', timeout=5)
    #     texteFichier = fichierAnnonce.read()
    #     fichierAnnonce.close()
    #     if "404 Not Found" not in texteFichier and len(texteFichier) > 10 :
    #         image, titre, texte_html, date_debut, date_fin, version = texteFichier.split(";")
    #         if date_debut <= str(dateJour) and date_fin >= str(dateJour) :
    #             if version != "" :
    #                 versionLogiciel = ConvertVersionTuple("1.0.5.6")#FonctionsPerso.GetVersionLogiciel())
    #                 version = ConvertVersionTuple(version)
    #                 if versionLogiciel < version :
    #                     dictAnnonce = {"IDannonce":None, "image":image, "titre":titre.decode("iso-8859-15"), "texte_html":texte_html.decode("iso-8859-15")}
    #                     found = True
    #             else :
    #                 dictAnnonce = {"IDannonce":None, "image":image, "titre":titre.decode("iso-8859-15"), "texte_html":texte_html.decode("iso-8859-15")}
    #                 found = True
    # except :
    #     pass
        
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
    


class Panel(wx.Panel):
    def __init__(self, parent, size=(-1, -1)):
        wx.Panel.__init__(self, parent, name="panel_accueil", id=-1, size=size, style=wx.TAB_TRAVERSAL)

        # Récupération des données de l'interface
        theme = UTILS_Interface.GetTheme()
        self.image_fond = wx.Bitmap("Images/Interface/%s/Fond.jpg" % theme, wx.BITMAP_TYPE_ANY)

        # Binds
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.Refresh()

    def OnPaint(self, event):
        """ Préparation du DC """
        dc = wx.BufferedPaintDC(self)
        if wx.VERSION < (2, 9, 0, 0) :
            self.PrepareDC(dc)
        bg = wx.Brush(self.GetBackgroundColour())
        dc.SetBackground(bg)
        dc.Clear()

        # Dessine le fond
        dc.DrawBitmap(self.image_fond, 0, 0)

        # Récupère l'annonce
        dictAnnonce = GetAnnonce()
        if dictAnnonce != None :

            nomImage = dictAnnonce["image"]
            bmp = wx.Bitmap("Images/16x16/%s.png" % nomImage, wx.BITMAP_TYPE_ANY)
            titre = dictAnnonce["titre"]
            texte_html = dictAnnonce["texte_html"]

            # Préparation du dessin
            x, y = 20, 20
            taille_police = 8
            largeurTexte = 300
            dc.SetTextForeground((255, 255, 255))

            # Dessine l'image
            dc.DrawBitmap(bmp, x, y)

            # Dessine le titre
            dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
            dc.DrawText(titre, x+22, y)

            # Dessine le texte
            dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
            texte = wordwrap(texte_html, largeurTexte, dc, breakLongWords=True)
            largeur, hauteur, hauteurLigne = dc.GetMultiLineTextExtent(texte)
            dc.DrawLabel(texte, wx.Rect(x, y + 22, largeurTexte, hauteur))



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