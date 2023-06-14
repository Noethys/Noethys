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
import datetime
import GestionDB

from Ol import OL_Unites_cotisations



def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class Dialog(wx.Dialog):
    def __init__(self, parent, IDtype_cotisation=None, premiereCotisation=False):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_type_cotisation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDtype_cotisation = IDtype_cotisation
        self.dictUnites = {}
        if premiereCotisation == True :
            self.defaut = 1
        else:
            self.defaut = 0

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.ctrl_type = wx.Choice(self, -1, choices=[_(u"Cotisation familiale"), _(u"Cotisation individuelle")])
        self.ctrl_type.Select(0)
        self.ctrl_carte = wx.CheckBox(self, -1, _(u"Est représentée par une carte d'adhérent"))

        # Unités
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, _(u"Unités"))
        self.ctrl_unites = OL_Unites_cotisations.ListView(self, IDtype_cotisation=self.IDtype_cotisation, id=-1, name="OL_Unites_cotisations", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.bouton_ajouter_unite = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_unite = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_unite = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_defaut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_ANY))

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_code_comptable = wx.StaticText(self, -1, _(u"Code comptable :"))
        self.ctrl_code_comptable = wx.TextCtrl(self, -1, u"")
        self.label_code_produit_local = wx.StaticText(self, -1, _(u"Code produit local :"))
        self.ctrl_code_produit_local = wx.TextCtrl(self, -1, "")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnAjouterUnite, self.bouton_ajouter_unite)
        self.Bind(wx.EVT_BUTTON, self.OnModifierUnite, self.bouton_modifier_unite)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerUnite, self.bouton_supprimer_unite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.SetDefaut, self.bouton_defaut)
        
        if self.IDtype_cotisation == None :
            self.SetTitle(_(u"Saisie d'un type de cotisation"))
            self.ctrl_unites.MAJ() 
        else:
            self.SetTitle(_(u"Modification d'un type de cotisation"))
            self.Importation()
            
            

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de la cotisation")))
        self.ctrl_type.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici le type de la cotisation")))
        self.ctrl_carte.SetToolTip(wx.ToolTip(_(u"Cochez cette case si la cotisation est représentée par une carte d'adhérent")))
        self.bouton_ajouter_unite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une unité")))
        self.bouton_modifier_unite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'unité sélectionnée dans la liste")))
        self.bouton_supprimer_unite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'unité sélectionnée dans la liste")))
        self.bouton_defaut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour définir l'unité de cotisation sélectionnée comme celle par défaut")))
        self.ctrl_code_comptable.SetToolTip(wx.ToolTip(_(u"Saisissez un code comptable pour cette cotisation si vous souhaitez exporter les écritures comptables vers des logiciels de compta")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((510, 590))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_type, 0, 0, 0)
        grid_sizer_generalites.Add( (5, 5), 0, 0, 0)
        grid_sizer_generalites.Add(self.ctrl_carte, 0, 0, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites_staticbox, wx.VERTICAL)
        grid_sizer_unites = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_unites = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_unites.Add(self.ctrl_unites, 1, wx.EXPAND, 0)
        grid_sizer_boutons_unites.Add(self.bouton_ajouter_unite, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_modifier_unite, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_supprimer_unite, 0, 0, 0)
        grid_sizer_boutons_unites.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_defaut, 0, 0, 0)
        grid_sizer_unites.Add(grid_sizer_boutons_unites, 1, wx.EXPAND, 0)
        grid_sizer_unites.AddGrowableRow(0)
        grid_sizer_unites.AddGrowableCol(0)
        staticbox_unites.Add(grid_sizer_unites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_unites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_code_comptable, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_code_comptable, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        grid_sizer_options.Add((5, 5), 0, 0, 0)
        grid_sizer_options.Add(self.label_code_produit_local, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_code_produit_local, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_options.AddGrowableCol(4)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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

    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT nom, type, carte, defaut, code_comptable, code_produit_local
        FROM types_cotisations 
        WHERE IDtype_cotisation=%d;""" % self.IDtype_cotisation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return
        nom, type, carte, defaut, code_comptable, code_produit_local = listeDonnees[0]
        # Insertion du nom
        self.ctrl_nom.SetValue(nom)
        # Insertion du type
        if type == "famille" : self.ctrl_type.Select(0)
        if type == "individu" : self.ctrl_type.Select(1)
        # Checkox carte
        if carte == 1 : self.ctrl_carte.SetValue(True)
        # Code comptable
        if code_comptable != None :
            self.ctrl_code_comptable.SetValue(code_comptable)
        # Code produit local
        if code_produit_local != None :
            self.ctrl_code_produit_local.SetValue(code_produit_local)
        # Mémorisation du DEFAUT
        self.defaut = defaut
        
        # Importation des unités de pièces
        req = """SELECT IDunite_cotisation, date_debut, date_fin, 
        defaut, nom, montant, label_prestation, duree
        FROM unites_cotisations 
        WHERE IDtype_cotisation=%d;""" % self.IDtype_cotisation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.listeUnites = []
        for IDunite_cotisation, date_debut, date_fin, defaut, nom, montant, label_prestation, duree in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            dictTemp = {
                "IDunite_cotisation" : IDunite_cotisation,
                "date_debut" : date_debut,
                "date_fin" : date_fin,
                "defaut" : defaut,
                "nom" : nom,
                "montant" : montant,
                "label_prestation" : label_prestation,
                "etat" : None,
                "duree" : duree,
                }
            self.listeUnites.append(dictTemp)
        self.ctrl_unites.SetListeDonnees(self.listeUnites)
        self.ctrl_unites.MAJ() 

    def OnAjouterUnite(self, event): 
        self.ctrl_unites.Ajouter(None)

    def OnModifierUnite(self, event): 
        self.ctrl_unites.Modifier(None)

    def OnSupprimerUnite(self, event): 
        self.ctrl_unites.Supprimer(None)

    def SetDefaut(self, event):
        self.ctrl_unites.SetDefaut(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Cotisations")
    
    def GetIDtype_cotisation(self):
        return self.IDtype_cotisation

    def OnBoutonOk(self, event):
        # Récupération des données
        nom = self.ctrl_nom.GetValue()
        if self.ctrl_type.GetSelection() == 0 :
            type = "famille"
        else:
            type = "individu"
        carte = int(self.ctrl_carte.GetValue())
        listeUnites = self.ctrl_unites.GetListeDonnees() 
        
        # Vérification des données
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce type de cotisation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
        
        nbreUnites = 0
        for dictUnite in listeUnites :
            if dictUnite["etat"] != "SUPPR" :
                nbreUnites += 1
        if nbreUnites == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir au moins une unité de cotisation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        code_comptable = self.ctrl_code_comptable.GetValue() 
        code_produit_local = self.ctrl_code_produit_local.GetValue()

        # Sauvegarde du type de cotisation
        DB = GestionDB.DB()
        listeDonnees = [    
                ("nom", nom),
                ("type", type),
                ("carte", carte),
                ("defaut", self.defaut),
                ("code_comptable", code_comptable),
                ("code_produit_local", code_produit_local),
            ]
        if self.IDtype_cotisation == None :
            self.IDtype_cotisation = DB.ReqInsert("types_cotisations", listeDonnees)
        else:
            DB.ReqMAJ("types_cotisations", listeDonnees, "IDtype_cotisation", self.IDtype_cotisation)
            
        # Sauvegarde des unités de cotisation
        for dictUnite in listeUnites :
            IDunite_cotisation = dictUnite["IDunite_cotisation"]
            date_debut = dictUnite["date_debut"]
            date_fin = dictUnite["date_fin"]
            defaut = dictUnite["defaut"]
            nom = dictUnite["nom"]
            montant = dictUnite["montant"]
            label_prestation = dictUnite["label_prestation"]
            etat = dictUnite["etat"]
            duree = dictUnite["duree"]
            
            listeDonnees = [    
                ("IDtype_cotisation", self.IDtype_cotisation),
                ("date_debut", date_debut),
                ("date_fin", date_fin),
                ("defaut", defaut),
                ("nom", nom),
                ("montant", montant),
                ("label_prestation", label_prestation),
                ("duree", duree),
            ]
            
            # Ajout
            if etat == "MODIF" and IDunite_cotisation == None :
                IDunite_cotisation = DB.ReqInsert("unites_cotisations", listeDonnees)
            # Modification
            if etat == "MODIF" and IDunite_cotisation != None :
                DB.ReqMAJ("unites_cotisations", listeDonnees, "IDunite_cotisation", IDunite_cotisation)
            # Suppression
            if etat == "SUPPR" and IDunite_cotisation != None :
                DB.ReqDEL("unites_cotisations", "IDunite_cotisation", IDunite_cotisation)
        
        DB.Close()
        
        # Fermeture
        self.EndModal(wx.ID_OK)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDtype_cotisation=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()

