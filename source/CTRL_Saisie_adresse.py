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
import wx.lib.masked as masked
import sqlite3
import sys
import UTILS_Config
import GestionDB

    
def Importation_donnees():
    # Importation de la base par défaut
    con = sqlite3.connect("Geographie.dat")
    cur = con.cursor()
    cur.execute("SELECT IDville, nom, cp FROM villes")
    listeVillesTmp = cur.fetchall()
    cur.execute("SELECT num_dep, num_region, departement FROM departements")
    listeDepartements = cur.fetchall()
    cur.execute("SELECT num_region, region FROM regions")
    listeRegions = cur.fetchall()
    con.close()
    
    # Importation des corrections de villes et codes postaux
    DB = GestionDB.DB()
    req = """SELECT IDcorrection, mode, IDville, nom, cp
    FROM corrections_villes; """ 
    DB.ExecuterReq(req)
    listeCorrections = DB.ResultatReq()
    DB.Close()
    
    # Ajout des corrections
    dictCorrections = {}
    for IDcorrection, mode, IDville, nom, cp in listeCorrections :
        if mode == "ajout" :
            listeVillesTmp.append((None, nom, cp))
        else :
            dictCorrections[IDville] = {"mode":mode, "nom":nom, "cp":cp}

    listeNomsVilles = []
    listeVilles = []
    for IDville, nom, cp in listeVillesTmp:
        valide = True
        
        # Traitement des corrections
        if dictCorrections.has_key(IDville) :
            if dictCorrections[IDville]["mode"] == "modif" :
                nom = dictCorrections[IDville]["nom"]
                cp = dictCorrections[IDville]["cp"]
            if dictCorrections[IDville]["mode"] == "suppr" :
                valide = False
        
        # Mémorisation
        if valide == True :
            cp = int(cp)
            listeVilles.append((nom, "%05d" % cp))
            listeNomsVilles.append(nom)
        
    dictRegions = {}
    for num_region, region in listeRegions :
        dictRegions[num_region] = region
    
    dictDepartements = {}
    for num_dep, num_region, departement in listeDepartements :
        dictDepartements[num_dep] = (departement, num_region)

    return listeNomsVilles, listeVilles, dictRegions, dictDepartements


class TextCtrlCp(masked.TextCtrl):
    def __init__(self, parent, id=-1, value=None, ctrlVille=None, listeVilles=None, activeAutoComplete=True, **par):
        masked.TextCtrl.__init__(self, parent, id, value, **par)
        self.parent = parent
        self.ctrlVille = ctrlVille
        self.listeVilles = listeVilles
        self.autoComplete = True
        
        # Binds
        if activeAutoComplete == True :
            self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnKillFocus(self, event):
        """ Quand le contrôle Code perd le focus """
        if self.autoComplete == False :
            event.Skip()
            return
        textCode = self.GetValue()
        # On vérifie que la ville n'est pas déjà dans la case ville
        villeSelect = self.ctrlVille.GetValue()
        if villeSelect != '':
            for ville, cp in self.listeVilles:
                if ville == villeSelect and cp == textCode :
                    event.Skip()
                    return
        
        # On recherche si plusieurs villes ont ce même code postal
        ReponsesVilles = []
        for ville, cp in self.listeVilles:
            if cp == textCode :
                ReponsesVilles.append(ville)
        nbreReponses = len(ReponsesVilles)
        
        # Code postal introuvable
        if nbreReponses == 0:
            if textCode.strip() != '':
                dlg = wx.MessageDialog(self, _(u"Ce code postal n'est pas répertorié dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            event.Skip()
            return
        
        if nbreReponses == 1:
            resultat = ReponsesVilles[0]
            self.ctrlVille.SetValue(resultat)

        # Fenêtre de choix entre plusieurs codes postau
        if nbreReponses > 1:
            resultat = self.ChoixVilles(textCode, ReponsesVilles)
            if resultat != '':
                self.ctrlVille.SetValue(resultat)

        # Sélection du texte de la case ville pour l'autocomplete
        self.ctrlVille.SetSelection(0, len(resultat))
        
        event.Skip()

    def ChoixVilles(self, cp, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant un code postal identique """
        resultat = ""
        titre = _(u"Sélection d'une ville")
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + _(u" villes possèdent le code postal ") + str(cp) + _(u". Double-cliquez sur\nle nom d'une ville pour la sélectionner :")
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat

    def SetInfobulleVille(self):
        """ Créé une info-bulle pour les cp et villes pour indiquer les régions et départements """
        cp = self.GetValue()
        if cp == "" or cp == "     " :
            controle.SetToolTipString(_(u"Saisissez un code postal"))
        else:
            try :
                num_dep = cp[:2]
                nomDepartement, num_region = self.dictDepartements[num_dep]
                nomRegion = self.dictRegions[num_region]
                texte = _(u"Département : %s (%s)\nRégion : %s") % (nomDepartement, num_dep, nomRegion)
                self.SetToolTipString(texte)
            except :
                self.SetToolTipString(_(u"Le code postal saisi ne figure pas dans la base de données"))


class TextCtrlVille(wx.TextCtrl):
    def __init__(self, parent, id=-1, value=None, ctrlCp=None, listeVilles=None, listeNomsVilles=None, activeAutoComplete=True, **par):
        wx.TextCtrl.__init__(self, parent, id, value, **par)
        self.parent = parent
        self.ctrlCp = ctrlCp
        self.listeVilles = listeVilles
        self.listeNomsVilles = listeNomsVilles
        self.ignoreEvtText = False
        self.autoComplete = True
        
        # Binds
        if activeAutoComplete == True :
            self.Bind(wx.EVT_TEXT, self.OnText)
            self.Bind(wx.EVT_CHAR, self.OnChar)
            self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)


    def OnKillFocus(self, event):
        """ Quand le contrôle ville perd le focus """
        if self.autoComplete == False :
            event.Skip()
            return
        villeSelect = self.GetValue()
        if villeSelect == '':
            event.Skip()
            return

        # On recherche le nombre de villes ayant un nom identique
        nbreCodes = self.listeNomsVilles.count(villeSelect)

        if nbreCodes > 1:
            listeCodes = []
            for ville, cp in self.listeVilles :
                if villeSelect == ville:
                    listeCodes.append(cp)
                    
            # Chargement de la fenêtre de choix des codes
            resultat = self.ChoixCodes(villeSelect, listeCodes)
            if resultat != '':
                self.ctrlCp.SetValue(resultat)

        # Si la ville saisie n'existe pas
        if nbreCodes == 0:
            dlg = wx.MessageDialog(self, _(u"Cette ville n'est pas répertoriée dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        event.Skip()

    def OnChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def OnText(self, event):
        """ A chaque frappe de texte -> analyse """
        if self.autoComplete == False :
            event.Skip()
            return
        
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            event.Skip()
            return
        currentText = event.GetString().upper()
        found = False
        for ville, cp in self.listeVilles :
            if ville.startswith(currentText):
                self.ignoreEvtText = True
                self.SetValue(ville)
                self.SetInsertionPoint(len(currentText))
                self.SetSelection(len(currentText), len(ville))
                self.ctrlCp.SetValue(cp)
                found = True
                break
        
        if not found:
            self.ctrlCp.SetValue('')
            event.Skip()

    def ChoixCodes(self, ville, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant le même nom """
        resultat = ""
        titre = _(u"Sélection d'une ville")
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + _(u" villes portent le nom ") + str(ville) + _(u". Double-cliquez sur\nle code postal d'une ville pour la sélectionner :")
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat
    
# -----------------------------------------------------------------------------------------------------
    
class Adresse(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)        
        self.listeNomsVilles, self.listeVilles, self.dictRegions, self.dictDepartements = Importation_donnees()
        
        activeAutoComplete = UTILS_Config.GetParametre("adresse_autocomplete", True)
        mask_cp = UTILS_Config.GetParametre("mask_cp", "#####")
        
        self.ctrl_cp = TextCtrlCp(self, value="", listeVilles=self.listeVilles, activeAutoComplete=activeAutoComplete, size=(55, -1), style=wx.TE_CENTRE, mask=mask_cp) 
        self.label_ville = wx.StaticText(self, -1, _(u"Ville :"))
        self.ctrl_ville = TextCtrlVille(self, value="", ctrlCp=self.ctrl_cp, listeVilles=self.listeVilles, listeNomsVilles=self.listeNomsVilles, activeAutoComplete=activeAutoComplete)
        self.ctrl_cp.ctrlVille = self.ctrl_ville
        self.bouton_options = wx.Button(self, -1, "...", size=(20, 20))
        
        # Pour désactiver l'autocomplete du controle VILLE qui ne fonctionne pas sous Linux
        if "linux" in sys.platform :
            self.ctrl_ville.Enable(False)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnOptionsVille, self.bouton_options)

    def __set_properties(self):
        self.ctrl_cp.SetMinSize((50, -1))
        self.ctrl_cp.SetToolTipString(_(u"Saisissez ici le code postal de la ville"))
        self.ctrl_ville.SetToolTipString(_(u"Saisissez ici le nom de la ville"))
        self.bouton_options.SetToolTipString(_(u"Cliquez ici pour rechercher une ville ou pour saisir \nmanuellement une ville non présente dans la base\nde données du logiciel"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_cp, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_base.Add(self.label_ville, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_ville, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_base.Add(self.bouton_options, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(2)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        
    def GetValueCP(self):
        cp = self.ctrl_cp.GetValue()
        if cp == "     " :
            cp = None
        return cp

    def GetValueVille(self):
        ville = self.ctrl_ville.GetValue()
        if ville == "" :
            ville = None
        return ville
    
    def SetValueCP(self, cp=""):
        if cp != None :
            try :
                self.ctrl_cp.SetValue(cp)
            except : 
                pass
    
    def SetValueVille(self, ville=""):
        if ville != None :
            self.ctrl_ville.autoComplete = False
            self.ctrl_ville.SetValue(ville)
            self.ctrl_ville.autoComplete = True

    def OnOptionsVille(self, event): 
        import DLG_Villes
        dlg = DLG_Villes.Dialog(None, modeImportation=True)
        if dlg.ShowModal() == wx.ID_OK:
            cp, ville = dlg.GetVille()
            self.SetValueCP(cp)
            self.SetValueVille(ville)
        dlg.Destroy()
        
        # MAJ des données dans les contrôles
        self.listeNomsVilles, self.listeVilles, self.dictRegions, self.dictDepartements = Importation_donnees()
        self.ctrl_cp.listeVilles=self.listeVilles
        self.ctrl_ville.listeVilles=self.listeVilles
        self.ctrl_ville.listeNomsVilles=self.listeNomsVilles




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Adresse(panel)
        self.ctrl.SetValueCP("69380")
        self.ctrl.SetValueVille("CHASSELAY")
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