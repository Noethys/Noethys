#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import datetime

from Ctrl import CTRL_Saisie_date


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text



class CTRL_Ecole(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDecole, nom, rue, cp, ville
        FROM ecoles ORDER BY nom; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictEcoles = {}
        index = 0
        for IDecole, nom, rue, cp, ville in listeDonnees :
            if ville != None and ville != "" :
                label = u"%s - %s" % (nom, ville)
            else :
                label = nom
            listeItems.append(label)
            self.dictEcoles[index] = IDecole
            index += 1
        return listeItems

    def SetEcole(self, IDecole=None):
        for index, IDecoleTemp in self.dictEcoles.items() :
            if IDecoleTemp == IDecole :
                self.SetSelection(index)

    def GetEcole(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.dictEcoles[index]

# -------------------------------------------------------------------------------------------------------------------------


class CTRL_Classe(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.Enable(False)
        self.IDecole = None
        self.date_debut = None
        self.date_fin = None
        self.dictClasses = {}
    
    def MAJ(self, IDecole=None, date_debut=None, date_fin=None):
        selection = self.GetClasse() 
        
        self.IDecole = IDecole
        self.date_debut = date_debut
        self.date_fin = date_fin
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
            self.SetClasse(selection)
                                        
    def GetListeDonnees(self):
        if self.date_debut == None or self.date_fin == None :
            return [] 
        
        DB = GestionDB.DB()
        req = """SELECT IDclasse, nom, date_debut, date_fin, niveaux
        FROM classes 
        WHERE IDecole=%d 
        AND date_debut<='%s' AND date_fin>='%s'
        ORDER BY nom; """ % (self.IDecole, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        # Tri des classes par niveau scolaire
        listeClasses = []
        for IDclasse, nom, date_debut, date_fin, niveaux in listeDonnees :
            
            # Formatage des dates de la saison
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            saison = (date_debut, date_fin) 
            
            # Formatage du nom
            nom = _(u"%s   (Du %s au %s)") % (nom, DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
            
            # Formatage des niveaux
            listeNiveaux = []
            listeOrdresNiveaux = []
            txtNiveaux = u""
            if niveaux != None and niveaux != "" and niveaux != " " :
                listeTemp = niveaux.split(";")
                txtTemp = []
                for niveau in listeTemp :
                    IDniveau = int(niveau)
                    if IDniveau in self.parent.dictNiveaux :
                        nomNiveau = self.parent.dictNiveaux[IDniveau]["abrege"]
                        ordreNiveau = self.parent.dictNiveaux[IDniveau]["ordre"]
                        listeNiveaux.append(IDniveau)
                        txtTemp.append(nomNiveau)
                        listeOrdresNiveaux.append(ordreNiveau)
                txtNiveaux = ", ".join(txtTemp)
            
            donnees = (listeOrdresNiveaux, nom, txtNiveaux, listeNiveaux, IDclasse) 
            listeClasses.append(donnees)
        
        listeClasses.sort()
        
        # Création des items de liste
        listeItems = []
        self.dictClasses = {}
        index = 0
        for listeOrdresNiveaux, nom, txtNiveaux, listeNiveaux, IDclasse in listeClasses :
            listeItems.append(nom)
            self.dictClasses[index] = {"IDclasse" : IDclasse, "nom" : nom, 
                                                    "listeOrdresNiveaux" : listeOrdresNiveaux,
                                                    "txtNiveaux" : txtNiveaux,
                                                    "listeNiveaux" : listeNiveaux,}
            index += 1

        return listeItems

    def SetClasse(self, IDclasse=None):
        for index, dictClasse in self.dictClasses.items() :
            if dictClasse["IDclasse"] == IDclasse :
                self.SetSelection(index)

    def GetClasse(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.dictClasses[index]["IDclasse"]
    
    def GetNiveauxClasse(self):
        """ Retourne les niveaux disponibles dans la classe sélectionnée """
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            dictClasse = self.dictClasses[index]
            return dictClasse["listeNiveaux"]
        
        
# -------------------------------------------------------------------------------------------------------------------------

class CTRL_Niveau(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.Enable(False)
        self.listeNiveaux = []
        self.dictNiveaux = {}
    
    def MAJ(self, listeNiveaux=[]):
        selection = self.GetNiveau() 
        
        self.listeNiveaux = listeNiveaux
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        elif len(listeItems) == 1 :
            self.Select(0)
            self.Enable(False)
            self.SetNiveau(selection)
        else :
            self.Enable(True)
            self.SetNiveau(selection)
                                        
    def GetListeDonnees(self):
        if self.listeNiveaux == None :
            return []
            
        # Tri des niveaux par ordre
        listeTemp = []
        for IDniveau in self.listeNiveaux :
            nomNiveau = self.parent.dictNiveaux[IDniveau]["abrege"]
            ordreNiveau = self.parent.dictNiveaux[IDniveau]["ordre"]
            listeTemp.append((ordreNiveau, nomNiveau, IDniveau))
        listeTemp.sort() 
        
        # Affichage des items
        listeItems = []
        self.dictNiveaux = {}
        index = 0
        for ordreNiveau, nomNiveau, IDniveau in listeTemp :
            listeItems.append(nomNiveau)
            self.dictNiveaux[index] = IDniveau
            index += 1
        return listeItems

    def SetNiveau(self, IDniveau=None):
        for index, IDniveauTemp in self.dictNiveaux.items() :
            if IDniveauTemp == IDniveau :
                self.SetSelection(index)

    def GetNiveau(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.dictNiveaux[index]

# -------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDscolarite=None, donneesScolarite=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.donneesScolarite = donneesScolarite
        self.IDscolarite = IDscolarite
        
        self.dictNiveaux = self.ImportationNiveaux() 
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.label_du = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Classe
        self.box_scolarite_staticbox = wx.StaticBox(self, -1, _(u"Classe"))
        self.label_ecole = wx.StaticText(self, -1, _(u"Ecole :"))
        self.ctrl_ecole = CTRL_Ecole(self)
        self.label_classe = wx.StaticText(self, -1, _(u"Classe :"))
        self.ctrl_classe = CTRL_Classe(self)
        self.label_niveau = wx.StaticText(self, -1, _(u"Niveau :"))
        self.ctrl_niveau = CTRL_Niveau(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixEcole, self.ctrl_ecole)
        self.Bind(wx.EVT_CHOICE, self.OnChoixClasse, self.ctrl_classe)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une étape de la scolarité"))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de debut")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin")))
        self.ctrl_ecole.SetToolTip(wx.ToolTip(_(u"Sélectionnez une école")))
        self.ctrl_classe.SetToolTip(wx.ToolTip(_(u"Sélectionnez une classe")))
        self.ctrl_niveau.SetToolTip(wx.ToolTip(_(u"Sélectionnez un niveau scolaire")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((500, 200))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        box_scolarite = wx.StaticBoxSizer(self.box_scolarite_staticbox, wx.VERTICAL)
        grid_sizer_scolarite = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_periode, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_scolarite.Add(self.label_ecole, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_scolarite.Add(self.ctrl_ecole, 0, wx.EXPAND, 0)
        grid_sizer_scolarite.Add(self.label_classe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_scolarite.Add(self.ctrl_classe, 0, wx.EXPAND, 0)
        grid_sizer_scolarite.Add(self.label_niveau, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_scolarite.Add(self.ctrl_niveau, 0, wx.EXPAND, 0)
        grid_sizer_scolarite.AddGrowableCol(1)
        box_scolarite.Add(grid_sizer_scolarite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_scolarite, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnChoixDate(self):
        """ Si changement de dates... """
        self.OnChoixEcole()         
        
    def ImportationNiveaux(self):
        dictNiveaux = {}
        DB = GestionDB.DB()
        req = """SELECT IDniveau, ordre, nom, abrege
        FROM niveaux_scolaires
        ORDER BY ordre; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDniveau, ordre, nom, abrege in listeDonnees :
            dictNiveaux[IDniveau] = {"nom" : nom, "abrege" : abrege, "ordre" : ordre}
        return dictNiveaux

    def OnChoixEcole(self, event=None): 
        IDecole = self.ctrl_ecole.GetEcole() 
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        self.ctrl_classe.MAJ(IDecole=IDecole, date_debut=date_debut, date_fin=date_fin)
        self.OnChoixClasse()
        
    def OnChoixClasse(self, event=None): 
        listeNiveaux = self.ctrl_classe.GetNiveauxClasse()
        self.ctrl_niveau.MAJ(listeNiveaux=listeNiveaux)

    def OnBoutonAide(self, event=None): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Scolarit1")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def SetDateDebut(self, date=None):
        self.ctrl_date_debut.SetDate(date)

    def SetDateFin(self, date=None):
        self.ctrl_date_fin.SetDate(date)

    def SetEcole(self, IDecole=None):
        self.ctrl_ecole.SetEcole(IDecole)
        self.OnChoixEcole() 

    def SetClasse(self, IDclasse=None):
        self.ctrl_classe.SetClasse(IDclasse)
        self.OnChoixClasse() 

    def SetNiveau(self, IDniveau=None):
        self.ctrl_niveau.SetNiveau(IDniveau)


    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()

    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate()

    def GetEcole(self):
        return self.ctrl_ecole.GetEcole()

    def GetClasse(self):
        return self.ctrl_classe.GetClasse()

    def GetNiveau(self):
        return self.ctrl_niveau.GetNiveau()
    
    def GetNomEcole(self):
        return self.ctrl_ecole.GetStringSelection() 
    
    def GetNomClasse(self):
        return self.ctrl_classe.GetStringSelection() 

    def GetNomNiveau(self):
        return self.ctrl_niveau.GetStringSelection() 

    def OnBoutonOk(self, event): 
        # Vérification de la saisie
        date_debut = self.GetDateDebut() 
        date_fin = self.GetDateFin() 
        
        if date_debut == None or self.ctrl_date_debut.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        if date_fin == None or self.ctrl_date_fin.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return

        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de début ne peut pas être supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        if self.ctrl_ecole.GetEcole() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une école !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_ecole.SetFocus()
            return

        if self.ctrl_classe.GetClasse() == None and self.ctrl_classe.IsEnabled() :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun classe. \nVoulez-vous quand même valider la saisie ?"), _(u"Attention"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                return

        if self.ctrl_niveau.GetNiveau() == None and self.ctrl_niveau.IsEnabled() :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun niveau scolaire. \nVoulez-vous quand même valider la saisie ?"), _(u"Attention"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                return

        # Vérifie que l'individu n'est pas déjà inscrit dans une classe sur cette période
        for track in self.donneesScolarite :
            if track.IDscolarite != self.IDscolarite and date_debut <= track.dateFinDD and date_fin >= track.dateDebutDD :
                date_debut = DateEngFr(track.date_debut)
                date_fin = DateEngFr(track.date_fin)
                nomEcole = track.nomEcole
                nomClasse = track.nomClasse
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette inscription scolaire car\ncet individu est déjà inscrit sur une classe sur cette période :\n\nPériode : Du %s au %s\nEcole : %s\nClasse : %s") % (date_debut, date_fin, nomEcole, nomClasse), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Valide la saisie
        self.EndModal(wx.ID_OK)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
