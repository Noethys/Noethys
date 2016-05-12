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
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os, sys
import datetime
import GestionDB
from Data import DATA_Civilites as Civilites
import CTRL_Photo

if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC
    
import wx.html as html


DICT_CIVILITES = Civilites.GetDictCivilites()

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def CalculeAge(dateReference, date_naiss):
    # Calcul de l'age de la personne
    age = (dateReference.year - date_naiss.year) - int((dateReference.month, dateReference.day) < (date_naiss.month, date_naiss.day))
    return age


class CTRL_famille(html.HtmlWindow):
    def __init__(self, parent, IDfamille, dictIndividus, texte="", hauteur=24,  couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(4)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
        self.IDfamille = IDfamille
        self.dictIndividus = dictIndividus
        
        texte = _(u"Famille de %s") % self.GetNomsTitulaires()
        self.SetTexte(texte)
    
    def SetTexte(self, texte=""):
        self.SetPage(u"<B><FONT SIZE=3 COLOR='WHITE'>%s</FONT></B>""" % texte)
        self.SetBackgroundColour(self.couleurFond)
    
    def GetNomsTitulaires(self):
        listeTitulaires = []
        nbreTitulaires = 0
        for IDindividu, dictIndividu in self.dictIndividus.iteritems():
            if dictIndividu["titulaire"] == 1 :
                nom = dictIndividu["nom"]
                prenom = dictIndividu["prenom"]
                listeTitulaires.append(u"%s %s" % (nom, prenom))
                nbreTitulaires += 1
        if nbreTitulaires == 1 : return listeTitulaires[0]
        if nbreTitulaires == 2 : return _(u"%s et %s") % (listeTitulaires[0], listeTitulaires[1])
        if nbreTitulaires > 2 :
            texteNoms = ""
            for nomTitulaire in listeTitulaires[:-2] :
                texteNoms += u"%s, " % nom
            texteNoms += listeTitulaires[-1]
            return texteNoms
        return u""

##class CTRL_famille(wx.Choice):
##    def __init__(self, parent):
##        wx.Choice.__init__(self, parent, -1) 
##        self.parent = parent
##        self.MAJlisteDonnees() 
##    
##    def MAJlisteDonnees(self):
##        self.SetItems(self.GetListeDonnees())
##        self.Select(0)
##    
##    def GetListeDonnees(self):
##        db = GestionDB.DB()
##        req = """SELECT IDrestaurateur, nom
##        FROM restaurateurs
##        ORDER BY nom;""" 
##        db.ExecuterReq(req)
##        listeDonnees = db.ResultatReq()
##        db.Close()
##        listeItems = [ _(u"-------- Aucun --------"), ]
##        self.dictDonnees = { 0 : { "ID" : None } }
##        index = 1
##        for IDrestaurateur, nom in listeDonnees :
##            self.dictDonnees[index] = { "ID" : IDrestaurateur }
##            listeItems.append(nom)
##            index += 1
##        return listeItems
##
##    def SetID(self, ID=0):
##        for index, values in self.dictDonnees.iteritems():
##            if values["ID"] == ID :
##                 self.SetSelection(index)
##
##    def GetID(self):
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]["ID"]
    

class CTRL_individus(ULC.UltimateListCtrl):
    def __init__(self, parent, IDfamille=None, dictIndividus={}, listeSelectionIndividus=[], selectionTous=False):
        ULC.UltimateListCtrl.__init__(self, parent, -1, agwStyle=wx.LC_ICON | wx.LC_ALIGN_LEFT)
        self.parent = parent
        self.IDfamille = IDfamille
        self.dictIndividus = dictIndividus 
        
##        self.EnableSelectionVista(True)
        self.SetFirstGradientColour(None)
        self.SetSecondGradientColour(None) #"#316AC5")
        self.EnableSelectionGradient(True)
        
        # Création de la liste d'individus à afficher
        listeIndividus = []
        for IDindividu, dictIndividu in self.dictIndividus.iteritems() :
            nbreInscriptions = len(dictIndividu["inscriptions"])
            age = dictIndividu["age"]
            prenom = dictIndividu["prenom"]
            if nbreInscriptions > 0 :
                listeIndividus.append((prenom, IDindividu))
        listeIndividus.sort()

        # liste images
        self.dictPhotos = {}
        taillePhoto = 64
        il = wx.ImageList(taillePhoto, taillePhoto, True)
        for age, IDindividu in listeIndividus :
            dictIndividu = self.dictIndividus[IDindividu]
            IDcivilite = dictIndividu["IDcivilite"]
            nom  = dictIndividu["nom"]
            prenom  = dictIndividu["prenom"]
            nomFichier = Chemins.GetStaticPath("Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"])
            IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
            img = il.Add(bmp)
            self.dictPhotos[IDindividu] = img
        self.AssignImageList(il, wx.IMAGE_LIST_NORMAL)
                
        # Création des items
        index = 0
        for age, IDindividu in listeIndividus :
            dictIndividu = self.dictIndividus[IDindividu]
            IDcivilite = dictIndividu["IDcivilite"]
            nom  = dictIndividu["nom"]
            prenom  = dictIndividu["prenom"]
            label = prenom
            if label == "" :
                label = " "
            self.InsertImageStringItem(index, label, self.dictPhotos[IDindividu])
            self.SetItemData(index, IDindividu)
            if IDindividu in listeSelectionIndividus or selectionTous == True :
                self.Select(index)
            self.SetDisabledTextColour(wx.Colour(255, 0, 0))
            index += 1
            
##        self.Bind(ULC.EVT_LIST_ITEM_LEFT_CLICK, self.OnSelect)
##        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
##        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselect)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        
##        self.SetSelections([28, 31])
    
    def OnLeftUp(self, event):
        x = event.GetX()
        y = event.GetY()
        item, flags = self.HitTest((x, y))
        self.OnSelection()
##        event.Skip()
    
##    def OnSelect(self, event):
##        self.OnSelection()
##
##    def OnDeselect(self, event):
##        print "deselect"
##        self.OnSelection()
    
    def OnSelection(self):
        """ Quand une sélection d'individus est effectuée... """
        listeSelections = self.GetSelections()
##        try :
        self.GetGrandParent().SetListeSelectionIndividus(listeSelections)
        self.GetGrandParent().MAJ_grille()
##        except :
##            print listeSelections
        
    def SetSelections(self, listeIDindividus = []):
        for IDindividu in listeIDindividus :
            index = self.FindItemData(-1, IDindividu)
            if index != -1 :
                self.Select(index)
    
    def DeselectTout(self):
        for index in range(0, self.GetItemCount()):
            self.Select(index, False)
        
    def GetSelections(self):
        listeIDselections = []
        for index in range(0, self.GetItemCount()):
            if self.IsSelected(index) :
                listeIDselections.append(self.GetItemData(index))
        return listeIDselections
    
##    def Importation(self):
##        DB = GestionDB.DB()
##        
##        # Recherche des individus
##        req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss, rattachements.IDfamille, IDcategorie, titulaire
##        FROM  individus
##        LEFT JOIN rattachements ON individus.IDindividu = rattachements.IDindividu
##        WHERE rattachements.IDfamille = %d AND IDcategorie IN (1, 2)
##        ORDER BY nom, prenom;""" % self.IDfamille
##        DB.ExecuterReq(req)
##        listeIndividus = DB.ResultatReq()
##        
##        # Recherche des inscriptions
##        req = """SELECT IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif
##        FROM inscriptions 
##        WHERE IDfamille = %d ;""" % self.IDfamille
##        DB.ExecuterReq(req)
##        listeInscriptions = DB.ResultatReq()
##        DB.Close()
##        dictInscriptions = {}
##        for IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif in listeInscriptions :
##            dictInscriptions[IDindividu] = True
##            
##        listeDictIndividus = []
##        dictTitulairesFamille = {}
##        for IDindividu, IDcivilite, nom, prenom, date_naiss, IDfamille, IDcategorie, titulaire in listeIndividus :
##            if date_naiss != None :
##                date_naiss = DateEngEnDateDD(date_naiss)
##                age = CalculeAge(datetime.date.today(), date_naiss)
##            else:
##                age = None
##            dictTemp = {"IDindividu" : IDindividu, "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "age" : age}
##            if dictInscriptions.has_key(IDindividu) :
##                listeDictIndividus.append(dictTemp)
##            if titulaire == 1 :
##                dictTitulairesFamille[IDindividu] = dictTemp
##
##        return listeDictIndividus

class CTRL(wx.Panel):
    def __init__(self, parent, IDfamille=None, dictIndividus={}, selectionIndividus=[], selectionTous=False):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        self.ctrl_famille = CTRL_famille(self, IDfamille, dictIndividus, couleurFond="#316AC5")
        self.ctrl_individus = CTRL_individus(self, IDfamille, dictIndividus, selectionIndividus, selectionTous)
        
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_famille, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_individus, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
    
    def SetSelections(self, listeIDindividus = []):
        self.ctrl_individus.SetSelections(listeIDindividus)
    
    def GetSelections(self):
        return self.ctrl_individus.GetSelections()
    
    def DeselectTout(self):
        self.ctrl_individus.DeselectTout() 

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel, IDfamille=209)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
