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
import wx.lib.agw.hyperlink as Hyperlink

import GestionDB
import DATA_Renseignements as Renseignements

try: import psyco; psyco.full()
except: pass


LISTE_TYPES_RENSEIGNEMENTS = Renseignements.LISTE_TYPES_RENSEIGNEMENTS


class CheckListBoxPieces(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.IDactivite = IDactivite
    
    def MAJ(self):
        listeCoches = self.GetIDcoches() 
        listePieces = []
        db = GestionDB.DB()
        req = """SELECT IDtype_piece, nom, public, duree_validite, valide_rattachement 
        FROM types_pieces ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 : 
            for IDtype_piece, nom, public, duree_validite, valide_rattachement in listeDonnees :
                if IDtype_piece in listeCoches :
                    etat = True
                else:
                    etat = False
                listePieces.append((IDtype_piece, nom, etat))
        self.SetData(listePieces)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.Clear()
        self.data = []
        index = 0
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDpiece_activite, IDtype_piece 
        FROM pieces_activites WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listePieces = db.ResultatReq()
        db.Close()
        if len(listePieces) > 0 : 
            listeID = []
            for IDpiece_activite, IDtype_piece in listePieces :
                listeID.append(IDtype_piece)
            self.SetIDcoches(listeID)

    def Sauvegarde(self):
        # Sauvegarde des pièces à fournir
        liste_nouvelle = self.GetIDcoches()
        liste_ancienne = []
        DB = GestionDB.DB()
        req = """SELECT IDpiece_activite, IDtype_piece 
        FROM pieces_activites WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()
        if len(listePieces) > 0 : 
            listeID = []
            for IDpiece_activite, IDtype_piece in listePieces :
                liste_ancienne.append(IDtype_piece)
        # On rattache les nouveaux type de pièces
        for IDtype_piece in liste_nouvelle :
            if IDtype_piece not in liste_ancienne :
                listeDonnees = [ ("IDactivite", self.IDactivite ), ("IDtype_piece", IDtype_piece ), ]
                IDpiece_activite = DB.ReqInsert("pieces_activites", listeDonnees)
        # On enlève les anciens types de pièces
        for IDtype_piece in liste_ancienne :
            if IDtype_piece not in liste_nouvelle :
                DB.ReqDEL("pieces_activites", "IDtype_piece", IDtype_piece)
        DB.Close()
        
# -----------------------------------------------------------------------------------------------------------------------

class CheckListBoxCotisations(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.IDactivite = IDactivite
    
    def MAJ(self):
        listeCoches = self.GetIDcoches() 
        listeCotisations = []
        db = GestionDB.DB()
        req = """SELECT IDtype_cotisation, nom, type, carte, defaut 
        FROM types_cotisations ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 : 
            for IDtype_cotisation, nom, type, carte, defaut in listeDonnees :
                if IDtype_cotisation in listeCoches :
                    etat = True
                else:
                    etat = False
                listeCotisations.append((IDtype_cotisation, nom, etat))
        self.SetData(listeCotisations)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.Clear()
        self.data = []
        index = 0
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDcotisation_activite, IDtype_cotisation
        FROM cotisations_activites WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeCotisations = db.ResultatReq()
        db.Close()
        if len(listeCotisations) > 0 : 
            listeID = []
            for IDcotisation_activite, IDtype_cotisation in listeCotisations :
                listeID.append(IDtype_cotisation)
            self.SetIDcoches(listeID)
        return len(listeCotisations)

    def Sauvegarde(self):
        # Sauvegarde des cotisations à fournir
        liste_nouvelle = self.GetIDcoches()
        liste_ancienne = []
        DB = GestionDB.DB()
        req = """SELECT IDcotisation_activite, IDtype_cotisation
        FROM cotisations_activites WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeCotisations = DB.ResultatReq()
        if len(listeCotisations) > 0 : 
            listeID = []
            for IDcotisation_activite, IDtype_cotisation in listeCotisations :
                liste_ancienne.append(IDtype_cotisation)
        # On rattache les nouveaux type de cotisations
        for IDtype_cotisation in liste_nouvelle :
            if IDtype_cotisation not in liste_ancienne :
                listeDonnees = [ ("IDactivite", self.IDactivite ), ("IDtype_cotisation", IDtype_cotisation ), ]
                IDcotisation_activite = DB.ReqInsert("cotisations_activites", listeDonnees)
        # On enlève les anciens types de cotisations
        for IDtype_cotisation in liste_ancienne :
            if IDtype_cotisation not in liste_nouvelle :
                DB.ReqDEL("cotisations_activites", "IDtype_cotisation", IDtype_cotisation)
        DB.Close()
        
# -----------------------------------------------------------------------------------------------------------------------

class CheckListBoxRenseignements(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.IDactivite = IDactivite
    
    def MAJ(self):
        listeDonnees = []
        for ID, label in LISTE_TYPES_RENSEIGNEMENTS :
            listeDonnees.append((ID, label, False))
        self.SetData(listeDonnees)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.Clear()
        self.data = []
        index = 0
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDrenseignement, IDtype_renseignement
        FROM renseignements_activites WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeRenseignements = db.ResultatReq()
        db.Close()
        if len(listeRenseignements) > 0 : 
            listeID = []
            for IDrenseignement, IDtype_renseignement in listeRenseignements :
                listeID.append(IDtype_renseignement)
            self.SetIDcoches(listeID)

    def Sauvegarde(self):
        # Sauvegarde des infos à renseigner
        liste_nouvelle = self.GetIDcoches()
        liste_ancienne = []
        DB = GestionDB.DB()
        req = """SELECT IDrenseignement, IDtype_renseignement 
        FROM renseignements_activites WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeRenseignements = DB.ResultatReq()
        if len(listeRenseignements) > 0 : 
            listeID = []
            for IDrenseignement, IDtype_renseignement  in listeRenseignements :
                liste_ancienne.append(IDtype_renseignement)
        # On rattache les nouveaux types de renseignements
        for IDtype_renseignement in liste_nouvelle :
            if IDtype_renseignement not in liste_ancienne :
                listeDonnees = [ ("IDactivite", self.IDactivite ), ("IDtype_renseignement", IDtype_renseignement ), ]
                IDrenseignement = DB.ReqInsert("renseignements_activites", listeDonnees)
        # On enlève les anciens types de renseignements
        for IDtype_renseignement in liste_ancienne :
            if IDtype_renseignement not in liste_nouvelle :
                DB.ReqDEL("renseignements_activites", "IDtype_renseignement", IDtype_renseignement)
        DB.Close()
        
# -----------------------------------------------------------------------------------------------------------------------



class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        
        if self.GetGrandParent().GetName() == "notebook" :
            self.SetBackgroundColour(self.GetGrandParent().GetThemeBackgroundColour())
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        if self.URL == "pieces" :
            import DLG_Types_pieces
            dlg = DLG_Types_pieces.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()
            self.parent.ctrl_pieces.MAJ()
        if self.URL == "vaccins" :
            import DLG_Types_vaccins
            dlg = DLG_Types_vaccins.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()
        if self.URL == "maladies" :
            import DLG_Types_maladies
            dlg = DLG_Types_maladies.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()
        if self.URL == "cotisations" :
            import DLG_Types_cotisations
            dlg = DLG_Types_cotisations.Dialog(self)
            dlg.ShowModal() 
            dlg.Destroy()
            self.parent.ctrl_cotisations.MAJ()
        self.UpdateLink()


# -----------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panel_obligations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        
        # Pièces
        self.staticbox_pieces_staticbox = wx.StaticBox(self, -1, u"Pièces à fournir")
        self.ctrl_pieces = CheckListBoxPieces(self, IDactivite=IDactivite)
        self.ctrl_pieces.SetMinSize((-1, 55))
        self.ctrl_pieces.MAJ()
        self.hyper_pieces = Hyperlien(self, label=u"Accéder au paramétrage des pièces", infobulle=u"Cliquez ici pour accéder au paramétrage des pièces", URL="pieces")
        
        # Cotisations
        self.staticbox_cotisations_staticbox = wx.StaticBox(self, -1, u"Cotisations")
        self.ctrl_check_cotisations = wx.CheckBox(self, -1, u"L'individu inscrit doit avoir à jour au moins l'une des cotisations suivantes :")
        self.ctrl_cotisations = CheckListBoxCotisations(self, IDactivite=IDactivite)
        self.ctrl_cotisations.SetMinSize((-1, 55))
        self.ctrl_cotisations.MAJ()
        self.hyper_cotisations = Hyperlien(self, label=u"Accéder au paramétrage des cotisations", infobulle=u"Cliquez ici pour accéder au paramétrage des cotisations", URL="cotisations")

        # Vaccins
        self.staticbox_vaccins_staticbox = wx.StaticBox(self, -1, u"Vaccins obligatoires")
        self.ctrl_vaccins = wx.CheckBox(self, -1, u"L'individu inscrit doit avoir ses vaccins à jour")
        self.label_vaccins_1 = wx.StaticText(self, -1, u"(Accéder au paramètrage ")
        self.hyper_vaccins = Hyperlien(self, label=u"des vaccins", infobulle=u"Cliquez ici pour accéder au paramétrage des vaccins", URL="vaccins")
        self.label_vaccins_2 = wx.StaticText(self, -1, u" et ")
        self.hyper_maladies = Hyperlien(self, label=u"des maladies", infobulle=u"Cliquez ici pour accéder au paramétrage des maladies", URL="maladies")
        self.label_vaccins_3 = wx.StaticText(self, -1, u")")
        
        # Infos
        self.staticbox_infos_staticbox = wx.StaticBox(self, -1, u"Informations à renseigner")
        self.ctrl_infos = CheckListBoxRenseignements(self, IDactivite=IDactivite)
        self.ctrl_infos.SetMinSize((50, 50))
        self.ctrl_infos.MAJ()
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCotisations, self.ctrl_check_cotisations)
        
        # Importation
        if self.IDactivite != None :
            self.Importation() 
        
        # Init contrôles
        self.OnCheckCotisations(None)
            

    def __set_properties(self):
        self.ctrl_pieces.SetToolTipString(u"Cochez les pièces que l'individu inscrit à cette activité doit fournir")
        self.ctrl_vaccins.SetToolTipString(u"Cochez cette case si l'individu inscrit à cette activité doit obligatoirement justifier de ses vaccins à jour")
        self.ctrl_infos.SetToolTipString(u"Cochez les informations que l'individu inscrit à cette activité doit obligatoirement renseigner dans son dossier")
        self.ctrl_cotisations.SetToolTipString(u"Cochez les cotisations que l'individu inscrit à cette activité doit avoir à jour (au moins l'une d'elle)")
        self.ctrl_pieces.SetMinSize((-1, 90))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Pièces
        staticbox_pieces = wx.StaticBoxSizer(self.staticbox_pieces_staticbox, wx.VERTICAL)
        grid_sizer_pieces = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_pieces.Add(self.ctrl_pieces, 1, wx.EXPAND, 0)
        grid_sizer_pieces.Add(self.hyper_pieces, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_pieces.AddGrowableRow(0)
        grid_sizer_pieces.AddGrowableCol(0)
        staticbox_pieces.Add(grid_sizer_pieces, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_pieces, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Cotisations
        staticbox_cotisations = wx.StaticBoxSizer(self.staticbox_cotisations_staticbox, wx.VERTICAL)
        grid_sizer_cotisations = wx.FlexGridSizer(rows=4, cols=1, vgap=2, hgap=2)
        grid_sizer_cotisations.Add(self.ctrl_check_cotisations, 1, wx.EXPAND, 0)
        grid_sizer_cotisations.Add( (4, 4), 0, wx.EXPAND, 0)
        grid_sizer_cotisations.Add(self.ctrl_cotisations, 1, wx.EXPAND|wx.LEFT, 15)
        grid_sizer_cotisations.Add(self.hyper_cotisations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_cotisations.AddGrowableRow(0)
        grid_sizer_cotisations.AddGrowableCol(0)
        staticbox_cotisations.Add(grid_sizer_cotisations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_cotisations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Vaccins
        staticbox_vaccins = wx.StaticBoxSizer(self.staticbox_vaccins_staticbox, wx.VERTICAL)
        grid_sizer_vaccins = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_vaccins.Add(self.ctrl_vaccins, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_vaccins.Add(self.label_vaccins_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_vaccins.Add(self.hyper_vaccins, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_vaccins.Add(self.label_vaccins_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_vaccins.Add(self.hyper_maladies, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_vaccins.Add(self.label_vaccins_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_vaccins.Add(grid_sizer_vaccins, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_vaccins, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Infos
        staticbox_infos = wx.StaticBoxSizer(self.staticbox_infos_staticbox, wx.VERTICAL)
        staticbox_infos.Add(self.ctrl_infos, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_infos, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnCheckCotisations(self, event):
        if self.ctrl_check_cotisations.GetValue() == True :
            self.ctrl_cotisations.Enable(True)
            self.hyper_cotisations.Enable(True)
        else:
            self.ctrl_cotisations.Enable(False)
            self.hyper_cotisations.Enable(False)

    def Importation(self):
        # Importation des pièces à fournir
        self.ctrl_pieces.Importation()
        
        # Importation des cotisations
        nbreCoches = self.ctrl_cotisations.Importation()
        if nbreCoches > 0 : 
            self.ctrl_check_cotisations.SetValue(True)
        
        # Importation des vaccins obligatoires
        DB = GestionDB.DB()
        req = """SELECT vaccins_obligatoires 
        FROM activites WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 : 
            vaccins = listeDonnees[0][0]
            if vaccins != None :
                self.ctrl_vaccins.SetValue(vaccins)
        
        # Importation des infos obligatoires
        self.ctrl_infos.Importation()
    
    def Validation(self):
        # Vérifie qu'une cotisation au moins a été cochée
        if self.ctrl_check_cotisations.GetValue() == True :
            if len(self.ctrl_cotisations.GetIDcoches()) == 0 :
                dlg = wx.MessageDialog(self, u"Vous avez coché 'Cotisation obligatoire' mais sans cocher de cotisation dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
        return True
    
    def Sauvegarde(self): 
        # Sauvegarde des pièces à fournir
        self.ctrl_pieces.Sauvegarde()
        
        # Sauvegarde des cotisations à avoir
        if self.ctrl_check_cotisations.GetValue() == True :
            self.ctrl_cotisations.Sauvegarde()
        else:
            DB = GestionDB.DB()
            DB.ReqDEL("cotisations_activites", "IDactivite", self.IDactivite)
            DB.Close()
        
        # Sauvegarde des vaccins
        DB = GestionDB.DB()
        listeDonnees = [ ("vaccins_obligatoires", int(self.ctrl_vaccins.GetValue())),]
        DB.ReqMAJ("activites", listeDonnees, "IDactivite", self.IDactivite)
        DB.Close()

        # Sauvegarde des infos obligatoires
        self.ctrl_infos.Sauvegarde()





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=1)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, u"TEST", size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


