#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os, sys
import time
import datetime
import GestionDB

try :
    import smartcard
except :
    pass

if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC

from Data import DATA_Civilites as Civilites
from Ctrl import CTRL_Photo
from Dlg import DLG_Badgeage_dlg as DIALOGUES

DICT_CIVILITES = Civilites.GetDictCivilites()



class CTRL_Barre_numerique(wx.SearchCtrl):
    def __init__(self, interface):
        wx.SearchCtrl.__init__(self, interface, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.interface = interface
        self.timer = wx.Timer(self, -1)
        self.dernierRFID = None
        self.delai = 0

        # Importation des individus
        listeActivites = self.interface.dictProcedure["parametres"]["activites"]
        if listeActivites != None :
            if len(listeActivites) == 0 : conditionActivites = "()"
            elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
            else : conditionActivites = str(tuple(listeActivites))
            req = """SELECT individus.IDindividu, nom, prenom 
                    FROM individus 
                    LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
                    WHERE inscriptions.statut='ok'
                    AND inscriptions.IDactivite IN %s
                    AND (date_desinscription IS NULL OR date_desinscription>='%s')
                    GROUP BY individus.IDindividu
                    ORDER BY nom, prenom;""" % (conditionActivites, self.interface.date)
            DB = GestionDB.DB()
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            DB.Close()
            self.listeIndividus = []
            for IDindividu, nom, prenom in listeTemp :
                self.listeIndividus.append(IDindividu)
        else :
            self.listeIndividus = None

        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
                
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Remove_32x32.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Loupe_32x32.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        
        # HACK pour avoir le EVT_CHAR
        for child in self.GetChildren(): 
            if isinstance(child, wx.TextCtrl): 
                self.ctrl_texte = child
                child.Bind(wx.EVT_CHAR, self.OnKeyDown) 
                break 

        # Init Détection RFID
        self.InitialisationRFID()
    
    def Activer(self):
        self.Start() 
        
    def OnDestroy(self, event):
        self.Stop() 
        
    def Stop(self):
        self.timer.Stop()
        
    def Start(self):
        if not self.timer.IsRunning():
            self.timer.Start(500)
    
    def InitialisationRFID(self):
        self.connexion = None
        try :
            self.lecteurs = smartcard.System.readers()
            if len(self.lecteurs) > 0 :
                self.lecteur = self.lecteurs[0]
                self.connexion = self.lecteur.createConnection()
        except :
            pass
                
        
    def OnTimer(self, event):
        self.delai += 0.5
        if self.delai > 8 :
            self.delai = 0
            self.dernierRFID = None
        if self.connexion != None :
            try :
                self.connexion.connect()
                apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = self.connexion.transmit(apdu)
                if sw1 == 144 :
                    IDbadge = self.ListToHex(data)
                    self.connexion.disconnect()
                    if self.dernierRFID != IDbadge :
                        self.dernierRFID = IDbadge
                        IDindividu = self.interface.IdentificationCodebarre(IDbadge)
                        self.Stop() 
                        if IDindividu != None :
                            self.ValidationIdentification(IDindividu, mode="RFID")
                        else :
                            DIALOGUES.DLG_Message(self.interface, message=_(u"Ce numéro de badge RFID n'est pas répertorié !"), icone="erreur")
                            self.Start() 
            except Exception as err :
                #print err
                pass

    def ListToHex(self, data):
        string= ''
        for d in data:
            string += '%02X' % d
        return string

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE :
            self.EnvoiTouche("Efface")
            self.OnCancel(None) 
            return
        if keycode == wx.WXK_RETURN :
            self.EnvoiTouche("Validation")
        # Vérifie que les caractères saisis sont autorisés
        if keycode in (wx.WXK_RETURN, wx.WXK_BACK, wx.WXK_DELETE) or keycode > 255 :
            event.Skip()
            return
        if 1 : #chr(keycode) in "I0123456789" :
            self.EnvoiTouche(str(chr(keycode)))
            event.Skip()
            return
        # Sinon Cloche !
        wx.Bell()
        return

    def OnEnter(self, evt):
        txtSearch = self.GetValue()
        if len(txtSearch) == 0 : 
            return
        if txtSearch.startswith("I") :
            txtSearch = txtSearch[1:]
        for x in ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPKRSTUVWXYZ-_") :
            txtSearch = txtSearch.replace(x, "")
        try :
            IDindividu = int(txtSearch)
        except :
            DIALOGUES.DLG_Message(self.interface, message=_(u"Ce numéro de badge ne semble pas valide !"), icone="erreur")
            return False
        self.ValidationIdentification(IDindividu, mode="CLAVIER")
        
    def OnSearch(self, evt):
        pass
        #self.Recherche(self.GetValue())
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche(self.GetValue())
    
    def Reset(self):
        self.OnCancel(None)
        
    def OnText(self, evt):
        # Si code-barres individu saisi
        txtSearch = self.GetValue()
        # Analyse le CB
        IDindividu = self.interface.IdentificationCodebarre(txtSearch)
        if IDindividu != None :
            self.ValidationIdentification(IDindividu, mode="CB")
##        if len(txtSearch) > 6 and txtSearch.startswith("I") :
##            try :
##                IDindividu = int(txtSearch[1:])
##            except :
##                return
##            self.ValidationIdentification(IDindividu, mode="CB")
        # Filtre la liste normalement
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        self.ShowCancelButton(len(txtSearch))
    
    def EnvoiTouche(self, touche=""):
        """ Envoi touche au clavier virtuel """
        txtSearch = self.GetValue()
        if txtSearch.startswith("I") == False :
            if self.interface.clavierNum.EstVisible() :
                self.interface.clavierNum.EnfonceBouton(touche)
    
    def ReceptionTouche(self, touche=""):
        """ Recoit une touche du clavier virtuel """
        # Envoie touche à la barre de recherche
        texte = self.GetValue()
        self.SetFocus()
        if touche == "Efface" :
            self.OnCancel(None)
        elif touche == "Validation" :
            self.OnEnter(None)
        else :
            self.SetValue(texte+touche)
            self.SetInsertionPoint(len(texte)+1)
        
    def ValidationIdentification(self, IDindividu=None, mode="CLAVIER"):
        """ Vérification de l'identification """
        # On vide la barre de recherche
        self.OnCancel(None)
        # Lancement de la procédure si IDindividu correct
        resultat = self.interface.ValidationIdentification(IDindividu)
        if resultat == False :
            DIALOGUES.DLG_Message(self.interface, message=_(u"Ce numéro de badge n'existe pas !"), icone="erreur")
            return False
        else :
            # Vérification que l'individu est inscrit
            if self.listeIndividus != None :
                if IDindividu not in self.listeIndividus :
                    DIALOGUES.DLG_Message(self.interface, message=_(u"Il n'y a pas d'inscription valide !"), icone="erreur")
                    return False
            # Lance la procédure
            self.interface.Procedure(IDindividu)


# ---------------------------------------------------------------------------------------------------------------------------------


class CTRL_Liste_individus(ULC.UltimateListCtrl):
    def __init__(self, interface):
        ULC.UltimateListCtrl.__init__(self, interface, -1, agwStyle=ULC.ULC_SINGLE_SEL | ULC.ULC_REPORT | ULC.ULC_HRULES | ULC.ULC_NO_HEADER | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.interface = interface
    
    def Initialisation(self):
        # Importation des individus
        listeActivites = self.interface.dictProcedure["parametres"]["activites"]
        if listeActivites != None :
            if len(listeActivites) == 0 : conditionActivites = "()"
            elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
            else : conditionActivites = str(tuple(listeActivites))
            req = """SELECT individus.IDindividu, IDcivilite, nom, prenom 
                        FROM individus 
                        LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
                        WHERE inscriptions.statut='ok' AND inscriptions.IDactivite IN %s
                        AND (date_desinscription IS NULL OR date_desinscription>='%s')
                        GROUP BY individus.IDindividu
                        ORDER BY nom, prenom;""" % (conditionActivites, self.interface.date)
        else :
            req = """SELECT IDindividu, IDcivilite, nom, prenom FROM individus ORDER BY nom, prenom;"""
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        DB.Close()

        # liste images
        self.dictPhotos = {}
        taillePhoto = 64
        il = wx.ImageList(taillePhoto, taillePhoto, True)
        for IDindividu, IDcivilite, nom, prenom in listeIndividus :
            nomFichier = Chemins.GetStaticPath("Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"])
            IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
            img = il.Add(bmp)
            self.dictPhotos[IDindividu] = img
        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)
        
        self.InsertColumn(0, _(u"Nom de l'individu"), width=400, format=ULC.ULC_FORMAT_LEFT)
        
        # Création des items
        index = 0
        for IDindividu, IDcivilite, nom, prenom in listeIndividus :
            label = u"  %s %s" % (nom, prenom)
            self.InsertImageStringItem(index, label, self.dictPhotos[IDindividu])
            self.SetItemData(index, IDindividu)
            self.SetItemFont(index, wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
            
            index += 1
        
        self.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.Valider)
            
    def GetSelections(self):
        listeSelections = []
        for index in range(0, self.GetItemCount()):
            if self.IsSelected(index) :
                listeSelections.append((index, self.GetItemData(index)))
        return listeSelections
    
    def Monter(self, event=None):
        self.Scrolling("monter")
        
    def Descendre(self, event=None):
        self.Scrolling("descendre")
    
    def Scrolling(self, valeur=""):
        if self.GetItemCount() == 0 :
            return
        top, bottom = self._mainWin.GetVisibleLinesRange()
        nbreLignesAffichees = bottom-top
        if valeur == "monter" :
            try :
                self.EnsureVisible(top-nbreLignesAffichees)
            except :
                self.EnsureVisible(0)
        else :
            try :
                self.EnsureVisible(bottom+nbreLignesAffichees)
            except :
                self.EnsureVisible(self.GetItemCount()-1)
        self._mainWin.RecalculatePositions(True)

    def Effacer(self, event=None):
        for index, IDindividu in self.GetSelections() :
            self.Select(index, False)
        try :
            self.EnsureVisible(0)
        except :
            pass
        self._mainWin.RecalculatePositions(True)
    
    def Reset(self):
        self.Effacer(None) 
        
    def Valider(self, event=None):
        selections = self.GetSelections()
        if len(selections) == 0 :
            DIALOGUES.DLG_Message(self.interface, message=_(u"Vous devez d'abord sélectionner un individu dans la liste !"), icone="exclamation")
            return
        index, IDindividu = selections[0]
        
        # Lancement de la procédure si IDindividu correct
        resultat = self.interface.ValidationIdentification(IDindividu)
        if resultat == False :
            DIALOGUES.DLG_Message(self.interface, message=_(u"Ce numéro de badge n'existe pas !"), icone="erreur")
            return False
        else :
            self.Reset() 
            self.interface.Procedure(IDindividu)

        

# ----------------------------------------------------------------------------------------------------------------------        

class CTRL_Importation(wx.Panel):
    def __init__(self, interface):
        wx.Panel.__init__(self, interface, id=-1, style=wx.TAB_TRAVERSAL)
        self.interface = interface
        
        # Contrôles
        self.boutonTest = wx.Button(self, -1, _(u"Test"))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
            
    def OnBoutonTest(self, event):
        self.interface.ImportationBadgeage()
    

# ----------------------------------------------------------------------------------------------------------------------        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL_Liste_individus(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()