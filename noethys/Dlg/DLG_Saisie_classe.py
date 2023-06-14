#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Dates


class CTRL_Niveaux(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.listeNiveaux, self.dictNiveaux = self.Importation()
        self.SetListeChoix()

    def Importation(self):
        listeNiveaux = []
        dictNiveaux = {}
        DB = GestionDB.DB()
        req = """SELECT IDniveau, ordre, nom, abrege FROM niveaux_scolaires ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDniveau, ordre, nom, abrege in listeDonnees :
            nom =u" %s (%s)" % (nom, abrege)
            dictTemp = { "nom" : nom, "IDniveau" : IDniveau, "ordre" : ordre}
            dictNiveaux[IDniveau] = dictTemp
            listeNiveaux.append((nom, IDniveau))
        return listeNiveaux, dictNiveaux

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDniveau in self.listeNiveaux :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self, modeTexte=False):
        listeIDcoches = []
        NbreItems = len(self.listeNiveaux)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                if modeTexte == False :
                    ID = self.listeNiveaux[index][1]
                else:
                    ID = str(self.listeNiveaux[index][1])
                listeIDcoches.append(ID)
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeNiveaux)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeNiveaux)):
            ID = self.listeNiveaux[index][1]
            if ID in listeIDcoches or str(ID) in listeIDcoches :
                self.Check(index)
            index += 1
    

# ----------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDecole=None, IDclasse=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDecole = IDecole
        self.IDclasse = IDclasse
        self.niveaux_bloques = {}

        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"), style=wx.ALIGN_RIGHT)
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        self.label_saison = wx.StaticText(self, -1, _(u"Saison :"), style=wx.ALIGN_RIGHT)
        self.label_du = wx.StaticText(self, -1, u"Du", style=wx.ALIGN_RIGHT)
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"), style=wx.ALIGN_RIGHT)
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.label_niveaux = wx.StaticText(self, -1, _(u"Niveaux :"), style=wx.ALIGN_RIGHT)
        self.ctrl_niveaux = CTRL_Niveaux(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Importation
        if self.IDclasse == None:
            self.SetTitle(_(u"Saisie d'une classe"))
            DB = GestionDB.DB()
            req = """SELECT date_debut, date_fin
            FROM classes 
            ORDER BY IDclasse DESC LIMIT 1;"""
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                self.ctrl_date_debut.SetDate(UTILS_Dates.DateEngEnDateDD(listeDonnees[0][0]))
                self.ctrl_date_fin.SetDate(UTILS_Dates.DateEngEnDateDD(listeDonnees[0][1]))
        else:
            self.SetTitle(_(u"Modification d'une classe"))
            self.Importation()

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de la classe. Ex : 'CP - Mme PICHON'...")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de saison")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de saison")))
        self.ctrl_niveaux.SetToolTip(wx.ToolTip(_(u"Cochez les niveaux scolaires de la classe")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((400, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_saison = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_saison, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_saison.Add(self.label_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_saison.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_saison.Add(self.label_au, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_saison.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_saison, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_niveaux, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_niveaux, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(2)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Classes")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT nom, date_debut, date_fin, niveaux
        FROM classes 
        WHERE IDclasse=%d;""" % self.IDclasse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        nom = listeDonnees[0][0]
        date_debut = listeDonnees[0][1]
        date_fin = listeDonnees[0][2]
        niveaux = listeDonnees[0][3]

        self.ctrl_nom.SetValue(nom)
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        self.ctrl_niveaux.SetIDcoches(niveaux.split(";"))

        # Vérifie que cette classe n'a pas été attribuée à un individu
        req = """SELECT IDscolarite, niveaux_scolaires.IDniveau, niveaux_scolaires.abrege
        FROM scolarite 
        LEFT JOIN niveaux_scolaires ON niveaux_scolaires.IDniveau = scolarite.IDniveau
        WHERE IDclasse=%d
        ;""" % self.IDclasse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.niveaux_bloques = {}
        for IDscolarite, IDniveau, nom_niveau in listeDonnees:
            if IDniveau not in self.niveaux_bloques:
                self.niveaux_bloques[IDniveau] = {"nom": nom_niveau, "nombre": 0}
            self.niveaux_bloques[IDniveau]["nombre"] += 1

        if len(listeDonnees) > 0:
            liste_noms_niveaux = [niveau["nom"] for IDniveau, niveau in self.niveaux_bloques.items()]
            dlg = wx.MessageDialog(self, _(u"Cette classe a déjà été attribuée à %d individus.\n\nVous ne pourrez donc pas modifier la période ni les niveaux suivants : %s.") % (len(listeDonnees), ", ".join(liste_noms_niveaux)), _(u"Avertissement"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()

            # Blocage des dates
            self.ctrl_date_debut.Enable(False)
            self.ctrl_date_fin.Enable(False)

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        listeNiveaux = self.ctrl_niveaux.GetIDcoches(modeTexte=False) 
        
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette classe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une date de début de saison !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une date de fin de saison !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return

        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de début ne peut pas être supérieure à celle de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        
        if len(listeNiveaux) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun niveau scolaire pour cette classe. \n\nEtes-vous sûr de vouloir tout de même valider cette saisie ?"), _(u"Attention"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            if dlg.ShowModal() != wx.ID_YES :
                return
            dlg.Destroy()

        if len(self.niveaux_bloques):
            for IDniveau, niveau in self.niveaux_bloques.items():
                if IDniveau not in listeNiveaux:
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas décocher le niveau '%s' car il est déjà utilisé par un individu !") % niveau["nom"], _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        niveaux = ";".join(self.ctrl_niveaux.GetIDcoches(modeTexte=True))

        # Sauvegarde
        listeDonnees = [
            ("IDecole", self.IDecole),
            ("nom", nom),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("niveaux", niveaux),
        ]
        DB = GestionDB.DB()
        if self.IDclasse == None:
            self.IDclasse = DB.ReqInsert("classes", listeDonnees)
        else:
            DB.ReqMAJ("classes", listeDonnees, "IDclasse", self.IDclasse)
        DB.Close()

        # Valide la saisie
        self.EndModal(wx.ID_OK)

    def GetIDecole(self):
        return self.IDecole

    def GetIDclasse(self):
        return self.IDclasse



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
