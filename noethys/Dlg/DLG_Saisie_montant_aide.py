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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB

from Ctrl import CTRL_Saisie_euros

    
    ##    DONNEES_TEST = {
##    "IDaide_montant" : None,
##    "montant" : 20.0,
##    "combinaisons" : [
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 35}, # Après-midi
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 34}, # Matinée
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##        ],
##    }




class ListBoxCombinaisons(wx.ListBox):
    def __init__(self, parent, IDactivite=None, dictMontant=None):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.IDactivite = IDactivite
        self.dictMontant = dictMontant
        self.listeAnciennesCombi = []
        self.listeAnciennesUnites = []
        self.dictUnites = self.ImportationUnites()
        self.MAJ() 
    

    def MAJ(self):
        self.Clear()
        if self.dictMontant == None : return
        index = 0
        for dictCombinaison in self.dictMontant["combinaisons"] :
            IDaide_combi = dictCombinaison["IDaide_combi"]
            listeUnites = dictCombinaison["listeUnites"]
            label = u""
            for dictUnite in listeUnites :
                IDaide_combi_unite = dictUnite["IDaide_combi_unite"]
                IDunite = dictUnite["IDunite"]
                if self.dictUnites.has_key(IDunite) :
                    label += self.dictUnites[IDunite]["nom"] + " + "
                else :
                    label += _(u"[Unité ID%d inconnue]") % IDunite + " + "
            if len(label) > 0 : label = label[:-2]
            self.Insert(label, self.GetCount(), index) 
            index += 1
    
    def ImportationUnites(self):
        # Recherche des unités disponibles de l'activité
        db = GestionDB.DB()
        req = """SELECT IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        dictUnites = {}
        for IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin in listeUnites :
            dictUnites[IDunite] = {"ordre":ordre, "nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "date_debut":date_debut, "date_fin":date_fin}
        return dictUnites
    
    def Ajouter(self):
        listeIDunites = self.Saisie() 
        if listeIDunites == None : return
        listeUnitesTmp = []
        for IDunite in listeIDunites :
            listeUnitesTmp.append( {"IDaide_combi_unite" : None, "IDunite" : IDunite} )
        self.dictMontant["combinaisons"].append( {"IDaide_combi" : None, "listeUnites" : listeUnitesTmp} )
        self.MAJ() 
    
    def Modifier(self):
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune combinaison à modifier dans la liste !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        index = self.GetClientData(index)
        # Récupération des anciennes IDunites
        listeAnciennesIDunites = []
        listeUnites = self.dictMontant["combinaisons"][index]["listeUnites"]
        for dictUnite in listeUnites :
            IDunite = dictUnite["IDunite"]
            listeAnciennesIDunites.append(IDunite)
        listeAnciennesIDunites.sort()
        # Fenêtre de saisie
        listeIDunites = self.Saisie(listeAnciennesIDunites) 
        if listeIDunites == None : return
        # Modification de la liste de données
        listeValeurs = []
        listeTemp = []
        for IDunite in listeIDunites :
            found = False
            for dictUniteTmp in self.dictMontant["combinaisons"][index]["listeUnites"] :
                IDaide_combi_unite = dictUnite["IDaide_combi_unite"]
                IDuniteTmp = dictUniteTmp["IDunite"]
                if IDuniteTmp == IDunite :
                    listeTemp.append({"IDaide_combi_unite" : IDaide_combi_unite, "IDunite" : IDunite})
                    found = True
            if found == False :
                listeTemp.append({"IDaide_combi_unite" : None, "IDunite" : IDunite})
        self.dictMontant["combinaisons"][index]["listeUnites"] = listeTemp
        self.MAJ() 
    
    def Supprimer(self):
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune combinaison à supprimer dans la liste !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        index = self.GetClientData(index)
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette combinaison ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            # Suppression
            self.dictMontant["combinaisons"].pop(index)
            self.MAJ() 
        dlg.Destroy()

    def Saisie(self, listeAnciennesIDunites=None):                
        # Recherche des unités disponibles de l'activité
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        if len(listeUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'existe aucune unité pour cette activité !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return None
        
        listeAnciennesSelections = []
        listeItems = []
        index = 0
        for valeurs in listeUnites :
            if listeAnciennesIDunites != None :
                if valeurs[0] in listeAnciennesIDunites :
                    listeAnciennesSelections.append(index)
            listeItems.append(valeurs[1])
            index += 1
            
        # Boîte de dialogue pour choisir les combinaisons
        dlg = wx.MultiChoiceDialog(self, _(u"Cochez les unités à combiner :"), _(u"Combinaisons d'unités"), listeItems)
        if len(listeAnciennesSelections) > 0 :
            dlg.SetSelections(listeAnciennesSelections)
        if dlg.ShowModal() == wx.ID_OK :
            listeSelections = dlg.GetSelections()
            if len(listeSelections) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune unité !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
            # Vérifie que les unités sélectionnées sont compatibles entre elles
            db = GestionDB.DB()
            req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
            FROM unites_incompat;"""
            db.ExecuterReq(req)
            listeIncompatibilites = db.ResultatReq()
            db.Close()
            if len(listeIncompatibilites) > 0 :
                for indexSelection1 in listeSelections :
                    IDunite1 = listeUnites[indexSelection1][0]
                    nomUnite1 = listeUnites[indexSelection1][1]
                    for indexSelection2 in listeSelections : 
                        IDunite2 = listeUnites[indexSelection2][0]
                        nomUnite2 = listeUnites[indexSelection2][1]
                        if IDunite1 != IDunite2 :
                            for IDunite_incompat, IDunite, IDunite_incompatible in listeIncompatibilites :
                                if (IDunite == IDunite1 and IDunite_incompatible == IDunite2) or (IDunite == IDunite2 and IDunite_incompatible == IDunite1) :
                                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas créer cette combinaison car les\nunités '%s' et '%s' sont incompatibles entre elles !") % (nomUnite1, nomUnite2), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    return None
            dlg.Destroy()
        else:
            dlg.Destroy()
            return None
        
        # Crée une liste des IDunités sélectionnés
        listeIDunites = []
        for selection in listeSelections :
            listeIDunites.append(listeUnites[selection][0])
        listeIDunites.sort()
        
        # Si c'est une modification, vérifie qu'une modification a été faite
        if listeAnciennesIDunites != None :
            if listeAnciennesIDunites == listeIDunites :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez effectué aucune modification !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
        
        # Vérifie que la combinaison n'existe pas déjà
        for dictCombinaison in self.dictMontant["combinaisons"] :
            IDaide_combi = dictCombinaison["IDaide_combi"]
            listeUnites = dictCombinaison["listeUnites"]

            listeUnitesTmp = []
            for dictUnite in listeUnites :
                IDaide_combi_uniteTmp = dictUnite["IDaide_combi_unite"]
                IDuniteTmp = dictUnite["IDunite"]
                listeUnitesTmp.append(IDuniteTmp)
                
            listeUnitesTmp.sort()
            if (listeUnitesTmp == listeIDunites)  :
                dlg = wx.MessageDialog(self, _(u"Cette combinaison existe déjà !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None


        return listeIDunites
        
# -----------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, dictMontant={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent 
        self.IDactivite = IDactivite
        self.dictMontant = dictMontant
        
        if self.dictMontant == None :
            self.dictMontant = { "IDaide_montant" : None, "montant" : 0.0, "combinaisons" : [] }
        
        # Contrôles
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, size=(70, -1))
        self.ctrl_montant.SetMontant(self.dictMontant["montant"])
        self.label_combinaisons = wx.StaticText(self, -1, _(u"Combinaisons :"))
        self.ctrl_combinaisons = ListBoxCombinaisons(self, IDactivite=self.IDactivite, dictMontant=self.dictMontant)
        
        # Boutons
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un montant"))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez ici un montant en euros")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une combinaisons d'unités")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la combinaison d'unités sélectionnées dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la combinaison d'unités sélectionnées dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))
        self.SetMinSize((380, 250))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_combinaisons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_combi = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_contenu.Add(self.label_combinaisons, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_combinaisons.Add(self.ctrl_combinaisons, 0, wx.EXPAND, 0)
        grid_sizer_boutons_combi.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_combinaisons.Add(grid_sizer_boutons_combi, 1, wx.EXPAND, 0)
        grid_sizer_combinaisons.AddGrowableRow(0)
        grid_sizer_combinaisons.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_combinaisons, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(1)
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

    def OnBoutonAjouter(self, event): 
        self.ctrl_combinaisons.Ajouter()

    def OnBoutonModifier(self, event): 
        self.ctrl_combinaisons.Modifier()

    def OnBoutonSupprimer(self, event): 
        self.ctrl_combinaisons.Supprimer()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
    
    def GetDictMontant(self):
        self.ctrl_combinaisons.dictMontant["montant"] = self.ctrl_montant.GetMontant() 
        return self.ctrl_combinaisons.dictMontant

    def OnBoutonOk(self, event): 
        montant = self.ctrl_montant.GetMontant()
        if montant == None or montant == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus() 
            return
        
        dictMontant = self.GetDictMontant() 
        if len(dictMontant["combinaisons"]) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez créer obligatoirement une combinaison d'unités !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.EndModal(wx.ID_OK)


# ----------------------------------------------------------------------------------------------------------------

DONNEES_TEST = {
    "IDaide_montant" : None,
    "montant" : 20.0,
    "combinaisons" : [
            { "IDaide_combi" : None, "listeUnites" : 
                [
                {"IDaide_combi_unite" : None, "IDunite" : 35}, # Après-midi
                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
                ],
            },
            { "IDaide_combi" : None, "listeUnites" : 
                [
                {"IDaide_combi_unite" : None, "IDunite" : 34}, # Matinée
                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
                ],
            },
        ],
    }


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1, dictMontant=DONNEES_TEST)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
