#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import wx.html as html

import CTRL_Saisie_date
import UTILS_Dates
import OL_Operations_releve



class CTRL_Informations(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=30,  couleurFond="#F0FBED"):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.html.HW_NO_SELECTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(4)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
            
    def SetTexte(self, texte=""):
        self.SetPage(u"<FONT SIZE=2>%s</FONT>""" % texte)
        self.SetBackgroundColour(self.couleurFond)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [u"",]
        self.dictDonnees = { 0 : {"ID":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom
        FROM comptes_bancaires
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDcompte, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompte }
            label = nom
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDreleve=None, IDcompte_bancaire=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.IDreleve = IDreleve
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Généralités")
        
        self.label_compte = wx.StaticText(self, wx.ID_ANY, u"Compte :")
        self.ctrl_compte = CTRL_Compte(self)

        self.label_nom = wx.StaticText(self, wx.ID_ANY, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_du = wx.StaticText(self, wx.ID_ANY, u"Du :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Informations
        self.box_informations_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Détail du relevé")
        self.ctrl_informations = CTRL_Informations(self)

        # Opérations
        self.box_operations_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Opérations")
        self.ctrl_operations = OL_Operations_releve.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_operations.SetMinSize((50, 50))
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixCompte, self.ctrl_compte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        self.ctrl_compte.SetID(IDcompte_bancaire)
        
        if self.IDreleve != None :
            self.SetTitle(u"Modification d'un relevé bancaire")
            self.Importation() 
        else :
            self.SetTitle(u"Saisie d'un relevé bancaire")
            
        self.ctrl_operations.SetCompteBancaire(IDcompte_bancaire)
        self.ctrl_operations.SetReleve(IDreleve)
        self.ctrl_operations.MAJ() 

    def __set_properties(self):
        self.ctrl_compte.SetToolTipString(u"Sélectionnez le compte bancaire associé")
        self.ctrl_nom.SetToolTipString(u"Saisissez le nom du relevé bancaire (Ex : 'Janvier 2014')")
        self.ctrl_date_debut.SetToolTipString(u"Saisissez la date de début du relevé")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez la date de fin du relevé")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((800, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(3, 2, 10, 10)
        grid_sizer_generalites.Add(self.label_compte, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_compte, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_du, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_periode = wx.FlexGridSizer(1, 3, 5, 5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_generalites, 1, wx.EXPAND, 0)
        
        # Informations
        box_informations = wx.StaticBoxSizer(self.box_informations_staticbox, wx.VERTICAL)
        box_informations.Add(self.ctrl_informations, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_haut.Add(box_informations, 1, wx.EXPAND, 0)
        
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Opérations
        box_operations = wx.StaticBoxSizer(self.box_operations_staticbox, wx.VERTICAL)
        box_operations.Add(self.ctrl_operations, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_operations, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 


    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide(u"")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def OnChoixCompte(self, event):
        IDcompte_bancaire = self.ctrl_compte.GetID() 
        self.ctrl_operations.SetCompteBancaire(IDcompte_bancaire)
        self.ctrl_operations.MAJ() 
        
    def OnBoutonOk(self, event): 
        if self.Sauvegarde()  == False :
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        """ Sauvegarde des données """
        nom = self.ctrl_nom.GetValue() 
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        IDcompte = self.ctrl_compte.GetID() 
        listeOperations = self.ctrl_operations.GetTracksCoches() 
        
        # Validation des données saisies
        if IDcompte == None : 
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un compte bancaire !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_compte.SetFocus()
            return False

        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if date_debut == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de début !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        if date_fin == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de fin !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de fin supérieure à la date de début !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        if len(listeOperations) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez rapproché aucune opération.\n\nSouhaitez-vous tout de même valider ?", u"Avertissement", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Sauvegarde
        DB = GestionDB.DB()
        
        # Sauvegarde du relevé
        listeDonnees = [ 
            ("nom", nom ),
            ("date_debut", date_debut ),
            ("date_fin", date_fin ),
            ("IDcompte_bancaire", IDcompte),
            ]
        if self.IDreleve == None :
            self.IDreleve = DB.ReqInsert("compta_releves", listeDonnees)
        else :
            DB.ReqMAJ("compta_releves", listeDonnees, "IDreleve", self.IDreleve)
            
        # Sauvegarde des opérations
        listeIDoperations = []
        for track in listeOperations :
            DB.ReqMAJ("compta_operations", [("IDreleve", self.IDreleve),], "IDoperation", track.IDoperation)
            listeIDoperations.append(track.IDoperation)
        
        # Suppression des anciennes opérations cochées
        req = """SELECT IDoperation, date
        FROM compta_operations 
        WHERE IDreleve=%d;""" % self.IDreleve
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        for IDoperation, date in listeTemp :
            if IDoperation not in listeIDoperations :
                DB.ReqMAJ("compta_operations", [("IDreleve", None),], "IDoperation", IDoperation)

        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT nom, date_debut, date_fin, compta_releves.IDcompte_bancaire, COUNT(IDoperation)
        FROM compta_releves 
        LEFT JOIN compta_operations ON compta_operations.IDreleve = compta_releves.IDreleve
        WHERE compta_releves.IDreleve=%d;""" % self.IDreleve
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, date_debut, date_fin, IDcompte_bancaire, nbreOperations = listeTemp[0]
        if nom == None : nom = ""
        date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
        date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)        
        self.ctrl_compte.SetID(IDcompte_bancaire)
        
        if nbreOperations > 0 :
            self.ctrl_compte.Enable(False)
        
    def GetIDreleve(self):
        return self.IDreleve

    def SetInformations(self, texte=""):
        self.ctrl_informations.SetTexte(texte)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
