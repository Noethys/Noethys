#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import six

if 'phoenix' in wx.PlatformInfo:
    from wx import Control
else :
    from wx import PyControl as Control


class Footer(Control):
    def __init__(self, 
            parent, 
            id=-1, 
            pos=wx.DefaultPosition, 
            size=wx.DefaultSize, 
            style=wx.NO_BORDER, 
            name="footer",
        ):
        self.hauteur = 24
        self.afficherColonneDroite = True
        
        self.listview = None
        self.dictColonnes = {}
        self.dictTotaux = {}
        self.listeImpression = []
        Control.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)
        self.SetInitialSize(size)
                    
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.MAJ_affichage)
    
    def MAJ_affichage(self, event=None):
        self.Refresh() 
    
    def MAJ_totaux(self):
        self.dictTotaux = {}
        for track in self.listview.innerList :
            for nomColonne, dictColonne in self.dictColonnes.items() :
                if dictColonne["mode"] == "total" :
                    if hasattr(track, nomColonne) :
                        total = getattr(track, nomColonne)
                        if (nomColonne in self.dictTotaux) == False :
                            # Format classique (numérique)
                            self.dictTotaux[nomColonne] = 0
                            # Autre format
                            if "format" in dictColonne :
                                if dictColonne["format"] in ("temps", "duree") :
                                    self.dictTotaux[nomColonne] = datetime.timedelta(0)
                        if total != None :
                            self.dictTotaux[nomColonne] += total
    
    def MAJ(self):
        self.MAJ_totaux()
        self.MAJ_affichage() 
        
    def DrawColonne(self, dc, x, largeur, label="", alignement=None, couleur=None, font=None):
        """ Dessine une colonne """
        render = wx.RendererNative.Get()
        options = wx.HeaderButtonParams()
        options.m_labelText = label
        if alignement : options.m_labelAlignment = alignement
        if couleur : options.m_labelColour = couleur
        if font : options.m_labelFont = font
        render.DrawHeaderButton(self, dc, (x, 1, largeur, self.hauteur), params=options)
        
    def Paint(self, dc):
        """Draws the ticker text at the current offset using the provided DC"""
        defaultFont = self.GetFont()
        dc.SetFont(defaultFont)
        
        x = 0 - self.listview.GetScrollPos(wx.HORIZONTAL) 
        self.listeImpression = []
        dernierTexte = ""
        for (indexColonne, col) in enumerate(self.listview.columns):
            texte = ""
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
            couleur = wx.Colour(140, 140, 140)
            largeur = col.width
            #largeur = self.listview.GetColumnWidth(indexColonne)
            converter = col.stringConverter
            nom = col.valueGetter
            if col.align == "left" : alignement = wx.ALIGN_LEFT
            if col.align == "centre" : alignement = wx.ALIGN_CENTER
            if col.align == "right" : alignement = wx.ALIGN_RIGHT
            
            # Recherche infos personnalisées à afficher dans la colonne
            mode = None
            if nom in self.dictColonnes :
                infoColonne = self.dictColonnes[nom]
                mode = infoColonne["mode"]
                
                # Valeur : TOTAL
                if mode == "total" :
                    if nom in self.dictTotaux :
                        texte = self.dictTotaux[nom]
                    else :
                        # Total format classique (numérique)
                        texte = 0
                        # Autres formats de total
                        if "format" in infoColonne :
                            if infoColonne["format"] in ("temps", "duree") :
                                texte = datetime.timedelta(0)
                    if converter != None :
                        texte = converter(texte)
                    if six.PY2:
                        liste_types = (int, float, long)
                    else :
                        liste_types = (int, float)
                    if type(texte) in liste_types :
                        texte = str(texte)
                
                # Valeur : NOMBRE
                if mode == "nombre" :
                    nombre = len(self.listview.innerList)
                    if nombre > 1 :
                        texte = u"%d %s" % (nombre, infoColonne["pluriel"])
                    else :
                        texte = u"%d %s" % (nombre, infoColonne["singulier"])
                        
                # Valeur : TEXTE
                if mode == "texte" :
                    texte = infoColonne["texte"]

                # Paramètres personnalisés
                if "alignement" in infoColonne : alignement = infoColonne["alignement"]
                if "font" in infoColonne : font = infoColonne["font"]
                if "couleur" in infoColonne : couleur = infoColonne["couleur"]
            
            # Pour éviter les bords si les cases sont vides
            ajustement = 0
            if mode != "total" and dernierTexte == "" :
                ajustement = 5
                
            self.DrawColonne(dc, x-ajustement, largeur+ajustement, texte, alignement, couleur, font)
            x += largeur
            
            # Mémorisation pour impression
            self.listeImpression.append({"texte" : texte, "alignement" : alignement})
            
            if mode == "total" :
                dernierTexte = texte
            else :
                dernierTexte = ""
        
        # Dernière colonne de remplissage
        if self.afficherColonneDroite :
            self.DrawColonne(dc, x, self.GetSize()[0]-x)

    def GetDonneesImpression(self, typeInfo="texte"):
        """ Renvoie infos pour impression """
        """ typeInfo = "texte" ou "alignement" """
        listeDonnees = []
        for info in self.listeImpression :
            listeDonnees.append(info[typeInfo])
        return listeDonnees[1:]
    
    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        self.Paint(dc)
        
    def OnErase(self, evt):
        """Noop because of double buffering"""
        pass

    def AcceptsFocus(self):
        """Non-interactive, so don't accept focus"""
        return False
        
    def DoGetBestSize(self):
        """Width we don't care about, height is either -1, or the character
        height of our text with a little extra padding
        """
        return (100, self.hauteur-1)

    def ShouldInheritColours(self): 
        """Don't get colours from our parent..."""
        return False
        


if __name__ == '__main__':
    """ DEMO FRAME"""
    app = wx.App()
    f = wx.Frame(None)
    p = wx.Panel(f)
    t = Footer(p)
    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(t, flag=wx.GROW, proportion=1)
    p.SetSizer(s)
    f.Show()
    app.MainLoop()
    
    
