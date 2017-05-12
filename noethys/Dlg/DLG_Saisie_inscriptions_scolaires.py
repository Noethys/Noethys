#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
import wx.lib.agw.pybusyinfo as PBI

from Ctrl import CTRL_Saisie_date
from Ol import OL_Inscriptions_scolaires_2
from Utils import UTILS_Historique

try: import psyco; psyco.full()
except: pass


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
            self.Select(0)
                                        
    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDecole, nom, rue, cp, ville
        FROM ecoles ORDER BY nom; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            listeItems = [_(u"-- Toutes les écoles --")]
            self.dictEcoles = {0 : None}
            index = 1
            for IDecole, nom, rue, cp, ville in listeDonnees :
                if ville != None and ville != "" :
                    label = u"%s - %s" % (nom, ville)
                else :
                    label = nom
                listeItems.append(label)
                self.dictEcoles[index] = IDecole
                index += 1
        else:
            listeItems = []
            self.dictEcoles = {}
        return listeItems

    def SetEcole(self, IDecole=None):
        for index, IDecoleTemp in self.dictEcoles.iteritems() :
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
            if selection == None :
                self.Select(0)
            else:
                self.SetClasse(selection)
                                        
    def GetListeDonnees(self):
        if self.IDecole == None or self.date_debut == None or self.date_fin == None :
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
                    if self.parent.dictNiveaux.has_key(IDniveau) :
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
        if len(listeClasses) > 0 :
            listeItems = [_(u"-- Toutes les classes --")]
            self.dictClasses = {0 : None}
            index = 1
            for listeOrdresNiveaux, nom, txtNiveaux, listeNiveaux, IDclasse in listeClasses :
                listeItems.append(nom)
                self.dictClasses[index] = {"IDclasse" : IDclasse, "nom" : nom, "listeOrdresNiveaux" : listeOrdresNiveaux,
                                                        "txtNiveaux" : txtNiveaux, "listeNiveaux" : listeNiveaux,}
                index += 1
        else:
            listeItems = []
            self.dictClasses = {}
        return listeItems

    def SetClasse(self, IDclasse=None):
        for index, dictClasse in self.dictClasses.iteritems() :
            if dictClasse != None :
                if dictClasse["IDclasse"] == IDclasse :
                    self.SetSelection(index)

    def GetClasse(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            if self.dictClasses[index] == None :
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
            if dictClasse == None :
                return None
            else :
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
            self.Enable(False)
        elif len(listeItems) == 2 :
            self.Enable(False)
            self.Select(1)
        else :
            self.Enable(True)
            if selection == None :
                self.Select(0)
            else:
                etat = self.SetNiveau(selection)
                if etat == False :
                    self.Select(0)
                                        
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
        if len(listeTemp) > 0 :
            listeItems = [_(u"-- Tous les niveaux --")]
            self.dictNiveaux = {0 : None}
            index = 1
            for ordreNiveau, nomNiveau, IDniveau in listeTemp :
                listeItems.append(nomNiveau)
                self.dictNiveaux[index] = IDniveau
                index += 1
        else :
            listeItems = []
            self.dictNiveaux = {}
        return listeItems

    def SetNiveau(self, IDniveau=None):
        for index, IDniveauTemp in self.dictNiveaux.iteritems() :
            if IDniveauTemp == IDniveau :
                self.SetSelection(index)
                return True
        return False

    def GetNiveau(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.dictNiveaux[index]

# -------------------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent, IDecole=None, IDclasse=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.IDecole = IDecole
        self.IDclasse = IDclasse
        self.dictNiveaux = self.ImportationNiveaux() 
        
        # Paramètres d'inscription
        self.box_param_staticbox = wx.StaticBox(self, -1, _(u"Paramètres de l'inscription"))
        self.label_periode = wx.StaticText(self, -1, _(u"Période :"))
        self.label_du = wx.StaticText(self, -1, u"du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self, activeCallback=False)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self, activeCallback=False)
        self.label_niveau = wx.StaticText(self, -1, _(u"Niveau :"))
        self.ctrl_niveau = CTRL_Niveau(self)

        # Individus
        self.box_individus_staticbox = wx.StaticBox(self, -1, _(u"Sélection des individus"))
        
        self.label_filtre_periode = wx.StaticText(self, -1, _(u"Période :"))
        self.label_filtre_du = wx.StaticText(self, -1, u"du")
        self.ctrl_filtre_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_filtre_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_filtre_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.label_filtre_ecole = wx.StaticText(self, -1, _(u"Ecole :"))
        self.ctrl_filtre_ecole = CTRL_Ecole(self)
        self.label_filtre_classe = wx.StaticText(self, -1, _(u"Classe :"))
        self.ctrl_filtre_classe = CTRL_Classe(self)
        self.label_filtre_niveau = wx.StaticText(self, -1, _(u"Niveau :"))
        self.ctrl_filtre_niveau = CTRL_Niveau(self)
        
        self.ctrl_individus = OL_Inscriptions_scolaires_2.ListView(self, id=-1, name="OL_Inscriptions_scolaires_2", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_individus.MAJ(forceMAJ=True) 
        self.ctrl_recherche = OL_Inscriptions_scolaires_2.CTRL_Outils(self, listview=self.ctrl_individus, afficherCocher=True)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnFiltreEcole, self.ctrl_filtre_ecole)
        self.Bind(wx.EVT_CHOICE, self.OnFiltreClasse, self.ctrl_filtre_classe)
        self.Bind(wx.EVT_CHOICE, self.OnFiltreNiveau, self.ctrl_filtre_niveau)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Inscrire des individus"))
        self.ctrl_niveau.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici le niveau scolaire")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de scolarisation")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de scolarisation")))
        self.ctrl_filtre_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici un filtre de période")))
        self.ctrl_filtre_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici un filtre de période")))
        self.ctrl_filtre_ecole.SetToolTip(wx.ToolTip(_(u"Vous pouvez sélectionner ici un filtre sur les écoles")))
        self.ctrl_filtre_classe.SetToolTip(wx.ToolTip(_(u"Vous pouvez sélectionner ici un filtre sur les classes")))
        self.ctrl_filtre_niveau.SetToolTip(wx.ToolTip(_(u"Vous pouvez sélectionner ici un filtre sur les niveaux scolaires")))
        self.ctrl_individus.SetToolTip(wx.ToolTip(_(u"Cochez les individus à inscrire")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((660, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Paramètres
        box_param = wx.StaticBoxSizer(self.box_param_staticbox, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_param.Add(self.label_periode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_param.Add(grid_sizer_periode, 1, wx.EXPAND, 0)

        grid_sizer_param.Add(self.label_niveau, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_niveau, 0, wx.EXPAND, 0)

        grid_sizer_param.AddGrowableCol(1)
        box_param.Add(grid_sizer_param, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(box_param, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Individus
        box_individus = wx.StaticBoxSizer(self.box_individus_staticbox, wx.VERTICAL)
        grid_sizer_individus = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        # Filtres Individus
        grid_sizer_filtres = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)

        grid_sizer_filtres.Add(self.label_filtre_periode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_filtre_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_filtre_periode.Add(self.label_filtre_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtre_periode.Add(self.ctrl_filtre_date_debut, 0, 0, 0)
        grid_sizer_filtre_periode.Add(self.label_filtre_au, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtre_periode.Add(self.ctrl_filtre_date_fin, 0, 0, 0)
        grid_sizer_filtres.Add(grid_sizer_filtre_periode, 1, wx.EXPAND, 0)

        grid_sizer_filtres.Add(self.label_filtre_ecole, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_filtre_ecole, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.label_filtre_classe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_filtre_classe, 0, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.label_filtre_niveau, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_filtre_niveau, 0, wx.EXPAND, 0)
        grid_sizer_filtres.AddGrowableCol(1)
        grid_sizer_individus.Add(grid_sizer_filtres, 1, wx.EXPAND, 0)
        
        # CTRL individus
        grid_sizer_individus.Add(self.ctrl_individus, 0, wx.TOP|wx.EXPAND, 10)
        
        # Hyperliens
        grid_sizer_hyperliens = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_hyperliens.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_hyperliens.AddGrowableCol(0)
        grid_sizer_individus.Add(grid_sizer_hyperliens, 1, wx.EXPAND, 0)
        
        grid_sizer_individus.AddGrowableRow(1)
        grid_sizer_individus.AddGrowableCol(0)
        box_individus.Add(grid_sizer_individus, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_individus, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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

    def OnChoixDate(self):
        """ Si changement de dates... """
        self.OnFiltreEcole()         

    def OnFiltreEcole(self, event=None): 
        IDecole = self.ctrl_filtre_ecole.GetEcole() 
        date_debut = self.ctrl_filtre_date_debut.GetDate() 
        date_fin = self.ctrl_filtre_date_fin.GetDate() 
        self.ctrl_filtre_classe.MAJ(IDecole=IDecole, date_debut=date_debut, date_fin=date_fin)
        self.OnFiltreClasse()
        self.MAJlisteIndividus() 

    def OnFiltreClasse(self, event=None): 
        listeNiveaux = self.ctrl_filtre_classe.GetNiveauxClasse()
        self.ctrl_filtre_niveau.MAJ(listeNiveaux=listeNiveaux)
        self.MAJlisteIndividus() 

    def OnFiltreNiveau(self, event=None): 
        self.MAJlisteIndividus() 
    
    def MAJlisteIndividus(self):
        IDecole = self.ctrl_filtre_ecole.GetEcole() 
        IDclasse = self.ctrl_filtre_classe.GetClasse() 
        IDniveau = self.ctrl_filtre_niveau.GetNiveau() 
        self.ctrl_individus.MAJ(IDecole=IDecole, IDclasse=IDclasse, IDniveau=IDniveau)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Inscriptionsscolaires")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def SetNomClasse(self, nom=""):
        self.SetTitle(_(u"Inscription d'individus dans la classe de %s") % nom)
        
    def SetDateDebut(self, date):
        self.ctrl_date_debut.SetDate(date)
        
    def SetDateFin(self, date):
        self.ctrl_date_fin.SetDate(date)
    
    def SetListeNiveaux(self, listeNiveaux=[]):
        self.ctrl_niveau.MAJ(listeNiveaux=listeNiveaux)
        
    def SetNiveau(self, IDniveau=None):
        self.ctrl_niveau.SetNiveau(IDniveau)        
        
    def OnBoutonOk(self, event): 
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        IDniveau = self.ctrl_niveau.GetNiveau() 
        listeIndividus = self.ctrl_individus.GetCoches() 
        
        # Vérification de la saisie
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus() 
            return

        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus() 
            return

        if IDniveau == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un niveau scolaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_niveau.SetFocus() 
            return

        if len(listeIndividus) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation d'enregistrement
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous l'inscription de %d individus ?") % len(listeIndividus), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        dlg.Destroy()
        
        # Fenêtre d'attente
        dlgAttente = PBI.PyBusyInfo(_(u"Veuillez patienter durant la procédure d'inscription..."), parent=None, title=_(u"Inscriptions scolaires"), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 

        # Récupère infos pour historique
        DB = GestionDB.DB()
        req = """SELECT ecoles.nom, classes.nom, classes.date_debut, classes.date_fin
        FROM classes 
        LEFT JOIN ecoles ON ecoles.IDecole = classes.IDecole
        WHERE classes.IDclasse=%d
        ;""" % self.IDclasse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        nomEcole = listeDonnees[0][0]
        nomClasse = listeDonnees[0][1]
        date_debut_classe = listeDonnees[0][2]
        date_fin_classe = listeDonnees[0][3]
        nomClasse = _(u"%s (Du %s au %s)") % (nomClasse, DateEngFr(date_debut_classe), DateEngFr(date_fin_classe))
        nomNiveau = self.ctrl_niveau.GetStringSelection()

        # Init Sauvegarde
        listeProblemes = []
        nbreValides = 0
        DB = GestionDB.DB()
        for IDindividu in listeIndividus :
            
            # Vérifie que l'individu n'est pas déjà inscrit dans une classe sur cette période
            donneesScolarite = self.parent.GetScolariteIndividu(IDindividu)
            valide = True
            for track in donneesScolarite :
                if date_debut <= track.dateFinDD and date_fin >= track.dateDebutDD :
                    date_debut_temp = DateEngFr(track.date_debut)
                    date_fin_temp = DateEngFr(track.date_fin)
                    nomEcole_temp = track.nomEcole
                    nomClasse_temp = track.nomClasse
                    nomIndividu_temp = u"%s %s" % (track.prenom, track.nom)
                    listeProblemes.append(_(u"- %s (déjà dans la classe de %s du %s au %s)\n") % (nomIndividu_temp, nomClasse_temp, date_debut_temp, date_fin_temp))
                    valide = False
                    break
            
            if valide == True :
                nbreValides += 1
                
                # Sauvegarde
                listeDonnees = [
                    ("IDindividu", IDindividu),
                    ("date_debut", date_debut),
                    ("date_fin", date_fin),
                    ("IDecole", self.IDecole),
                    ("IDclasse", self.IDclasse),
                    ("IDniveau", IDniveau),
                    ]
                IDscolarite = DB.ReqInsert("scolarite", listeDonnees)
                
                # Mémorisation dans l'historique
                UTILS_Historique.InsertActions([{
                    "IDindividu" : IDindividu,
                    "IDfamille" : None,
                    "IDcategorie" : 30, 
                    "action" : _(u"Inscription scolaire du %s au %s. Ecole : '%s'. Classe : '%s'. Niveau : '%s'") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, nomNiveau)
                    },])
        
        DB.Close()
        
        del dlgAttente
        
        # Informations
        if len(listeProblemes) > 0 :
            message = _(u"%d inscriptions ont été enregistrées sauf pour les individus suivants :\n\n%s") % (nbreValides, "".join(listeProblemes))
        else:
            message = _(u"%d inscriptions ont été enregistrées avec succès.") % nbreValides
        dlg = wx.MessageDialog(self, message, _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
        # Fermeture
        self.EndModal(wx.ID_OK)
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
