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
import datetime
import os
import sys
import traceback
import GestionDB
from Ctrl import CTRL_Choix_modele
from Ctrl import CTRL_Attestations_selection

from Utils import UTILS_Identification
from Utils import UTILS_Historique
from Utils import UTILS_Impression_facture
from Ctrl import CTRL_Attestations_options

import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.agw.pybusyinfo as PBI




def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def GetTexteNoms(listeNoms=[]):
    """ Récupère les noms sous la forme David DUPOND et Maxime DURAND... """
    texteNoms = u""
    nbreIndividus = len(listeNoms)
    if nbreIndividus == 0 : texteNoms = u""
    if nbreIndividus == 1 : texteNoms = listeNoms[0]
    if nbreIndividus == 2 : texteNoms = _(u"%s et %s") % (listeNoms[0], listeNoms[1])
    if nbreIndividus > 2 :
        for texteNom in listeNoms[:-2] :
            texteNoms += u"%s, " % texteNom
        texteNoms += _(u"%s et %s") % (listeNoms[-2], listeNoms[-1])
    return texteNoms

def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte


# ----------------------------------------------------------------------------------------------------------------------------------

##class CTRL_Signataires(wx.Choice):
##    def __init__(self, parent):
##        wx.Choice.__init__(self, parent, -1) 
##        self.parent = parent
##        self.listeActivites = []
##        self.MAJ() 
##        if len(self.dictDonnees) > 0 :
##            self.SetSelection(0)
##    
##    def MAJ(self, listeActivites=[] ):
##        self.listeActivites = listeActivites
##        listeItems, indexDefaut = self.GetListeDonnees()
##        if len(listeItems) == 0 :
##            self.Enable(False)
##        else:
##            self.Enable(True)
##        self.SetItems(listeItems)
##        if indexDefaut != None :
##            self.Select(indexDefaut)
##                                        
##    def GetListeDonnees(self):
##        if len(self.listeActivites) == 0 : conditionActivites = "()"
##        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
##        else : conditionActivites = str(tuple(self.listeActivites))
##        db = GestionDB.DB()
##        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
##        FROM responsables_activite
##        WHERE IDactivite IN %s
##        ORDER BY nom;""" % conditionActivites
##        db.ExecuterReq(req)
##        listeDonnees = db.ResultatReq()
##        db.Close()
##        listeItems = []
##        self.dictDonnees = {}
##        indexDefaut = None
##        index = 0
##        for IDresponsable, IDactivite, nom, fonction, defaut, sexe in listeDonnees :
##            if indexDefaut == None and defaut == 1 : indexDefaut = index
##            self.dictDonnees[index] = { 
##                "ID" : IDresponsable, "IDactivite" : IDactivite,
##                "nom" : nom, "fonction" : fonction,
##                "defaut" : defaut, "sexe" : sexe, 
##                }
##            listeItems.append(nom)
##            index += 1
##        return listeItems, indexDefaut
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
##    
##    def GetInfos(self):
##        """ Récupère les infos sur le signataire sélectionné """
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        
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
        if self.URL == "payes" : self.parent.CochePayes() 
        if self.URL == "tout" : self.parent.CocheTout() 
        if self.URL == "rien" : self.parent.DecocheTout() 
        self.UpdateLink()
        


class Dialog(wx.Dialog):
    def __init__(self, parent, date_debut=None, date_fin=None, dateNaiss=None, listeActivites=[], listePrestations=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Attestations_selection", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.dateNaiss = dateNaiss
        self.listeActivites = listeActivites
        self.listePrestations = listePrestations
        
        self.impressionEffectuee = False
        self.donnees = {}
        
        # Attestations
        self.staticbox_attestations_staticbox = wx.StaticBox(self, -1, _(u"Attestations à créer"))
        self.ctrl_attestations = CTRL_Attestations_selection.CTRL(self, date_debut=self.date_debut, date_fin=self.date_fin, dateNaiss=self.dateNaiss, listeActivites=self.listeActivites, listePrestations=self.listePrestations)
        
        self.hyper_payes = Hyperlien(self, label=_(u"Sélectionner uniquement les payés"), infobulle=_(u"Cliquez ici pour sélectionner uniquement les payés"), URL="payes")
        self.label_separation_1 = wx.StaticText(self, -1, u"|")
        self.hyper_tout = Hyperlien(self, label=_(u"Tout sélectionner"), infobulle=_(u"Cliquez ici pour tout sélectionner"), URL="tout")
        self.label_separation_2 = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout désélectionner"), infobulle=_(u"Cliquez ici pour tout désélectionner"), URL="rien")

        # Options des documents
        self.ctrl_parametres = CTRL_Attestations_options.CTRL(self, listeActivites=listeActivites)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_liste = CTRL_Bouton_image.CTRL(self, texte=_(u"Liste"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonListe, self.bouton_liste)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)

        self.__set_properties()
        self.__do_layout()

        # Init contrôles
        self.ctrl_attestations.MAJ() 

    def __set_properties(self):
        self.SetTitle(_(u"Sélection des attestations à éditer"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_liste.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste affichée")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer l'aperçu des attestations (PDF)")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((600, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Attestations
        staticbox_attestations = wx.StaticBoxSizer(self.staticbox_attestations_staticbox, wx.VERTICAL)
        grid_sizer_attestations = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=10)
        grid_sizer_attestations.Add(self.ctrl_attestations, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_commandes.Add( (5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_payes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.AddGrowableCol(0)
        
        grid_sizer_attestations.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_attestations.AddGrowableCol(0)
        grid_sizer_attestations.AddGrowableRow(0)
        
        staticbox_attestations.Add(grid_sizer_attestations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_attestations, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)        

        # Options
        grid_sizer_base.Add(self.ctrl_parametres, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_liste, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def EcritStatusbar(self, texte=u""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass
    
    def OnChoixIntitules(self, event=None):
        typeLabel = self.ctrl_intitules.GetID()
        self.ctrl_attestations.typeLabel = typeLabel
        self.ctrl_attestations.MAJ() 

    def CochePayes(self):
        self.ctrl_attestations.SelectPayes() 
        
    def CocheTout(self):
        self.ctrl_attestations.CocheTout()

    def DecocheTout(self):
        self.ctrl_attestations.DecocheTout()
    
    def OnBoutonListe(self, event):
        self.ctrl_attestations.ImpressionListe() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Gnration2")

    def OnBoutonAnnuler(self, event):
        if self.impressionEffectuee == True :
            self.Sauvegarder() 
        # Fermeture de la fenêtre
        self.EndModal(200)

    def OnBoutonOk(self, event):
        # Récupération du dictOptions
        dictOptions = self.ctrl_parametres.GetOptions() 
        if dictOptions == False :
            return False
        
        # Récupération du signataire
        infosSignataire = self.ctrl_parametres.ctrl_parametres.GetInfosSignataire() 
        if infosSignataire == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun signataire !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
                
        # Création du PDF
        dictComptes = self.ctrl_attestations.GetDonnees(dictOptions=dictOptions, infosSignataire=infosSignataire) 
    
        # Si aucune attestation à créer
        if len(dictComptes) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune attestation à créer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Préparation des commentaires
        dictCommentaires = {}
        for track in self.listePrestations :
            if track["commentaire"] != "" :
                dictCommentaires[(track["label"], track["IDactivite"])] = track["commentaire"]
        dictOptions["dictCommentaires"] = dictCommentaires

        # Détail
        if dictOptions["affichage_prestations"] == 0 :
            detail = True
        else:
            detail = False

        # Création des PDF à l'unité
        repertoire = dictOptions["repertoire_copie"]
        if repertoire not in (None, "") :
            dlgAttente = PBI.PyBusyInfo(_(u"Génération des attestations à l'unité au format PDF..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            try :
                index = 0
                for IDcompte_payeur, dictCompte in dictComptes.iteritems() :
                    IDattestation = dictCompte["num_attestation"]
                    nomTitulaires = Supprime_accent(dictCompte["nomSansCivilite"])
                    nomFichier = _(u"Attestation %d - %s") % (IDattestation, nomTitulaires)
                    cheminFichier = u"%s/%s.pdf" % (repertoire, nomFichier)
                    dictComptesTemp = {IDcompte_payeur : dictCompte}
                    self.EcritStatusbar(_(u"Génération de l'attestation %d/%d : %s") % (index, len(dictComptes), nomFichier))
                    UTILS_Impression_facture.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], mode="attestation", ouverture=False, nomFichier=cheminFichier)
                    index += 1
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la génération des attestations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Fabrication du PDF global
        dlgAttente = PBI.PyBusyInfo(_(u"Génération du lot d'attestations au format PDF..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        self.EcritStatusbar(_(u"Génération du lot d'attestations de rappel en cours... veuillez patienter..."))
        try :
            UTILS_Impression_facture.Impression(dictComptes, dictOptions, IDmodele=dictOptions["IDmodele"], mode="attestation")
            self.EcritStatusbar("")
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la génération des attestations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        self.impressionEffectuee = True
        self.donnees = dictComptes
        
    def Sauvegarder(self):
        """ Sauvegarde des attestations """
        # Demande la confirmation de sauvegarde
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous mémoriser les attestations ?\n\n(Cliquez NON si c'était juste un test sinon cliquez OUI)"), _(u"Sauvegarde"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        dlgAttente = PBI.PyBusyInfo(_(u"Sauvegarde des attestations en cours..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 

        DB = GestionDB.DB()
        
        try :
            for IDcompte_payeur, dictCompte in self.donnees.iteritems() :
                if dictCompte["select"] == True :
                    numero = dictCompte["num_attestation"]
                    IDfamille = dictCompte["IDfamille"] 
                    listePrestations = dictCompte["listePrestations"] 
                    total = dictCompte["total"] 
                    regle = dictCompte["ventilation"] 
                    solde = total - regle

                    # Liste des activités
                    texteActivites = ""
                    for IDactivite in self.listeActivites :
                        texteActivites += "%d;" % IDactivite
                    if len(self.listeActivites) > 0 :
                        texteActivites = texteActivites[:-1]
                    # Liste des individus
                    texteIndividus = ""
                    for IDindividu in dictCompte["individus"].keys() :
                        texteIndividus += "%d;" % IDindividu
                    if len(dictCompte["individus"].keys()) > 0 :
                        texteIndividus = texteIndividus[:-1]
                    
                    IDutilisateur = UTILS_Identification.GetIDutilisateur()
                    
                    # Sauvegarde de la facture
                    listeDonnees = [ 
                        ("numero", numero), 
                        ("IDfamille", IDfamille), 
                        ("date_edition", str(datetime.date.today())), 
                        ("activites", texteActivites), 
                        ("individus", texteIndividus), 
                        ("IDutilisateur", IDutilisateur), 
                        ("date_debut", str(self.date_debut)), 
                        ("date_fin", str(self.date_fin)), 
                        ("total", float(total)), 
                        ("regle", float(regle)), 
                        ("solde", float(solde)), 
                        ]

                    IDattestation = DB.ReqInsert("attestations", listeDonnees)
                                        
                    # Mémorisation de l'action dans l'historique
                    UTILS_Historique.InsertActions([{
                            "IDfamille" : IDfamille,
                            "IDcategorie" : 27, 
                            "action" : _(u"Edition d'une attestation de présence pour la période du %s au %s pour un total de %.02f € et un solde de %.02f €") % (DateEngFr(str(self.date_debut)), DateEngFr(str(self.date_fin)), total, solde),
                            },])

            DB.Close() 
            del dlgAttente

        except Exception, err:
            DB.Close() 
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la sauvegarde des attestations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Mémorisation des paramètres
        self.ctrl_parametres.MemoriserParametres() 
    



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None,
        date_debut = datetime.date(2014, 1, 15),
        date_fin = datetime.date(2014, 7, 30),
        dateNaiss = None,
        listeActivites = [1, 2, 3, 4, 5],
        listePrestations = [
            {"commentaire" : u"", "IDactivite" : 1, "label" : _(u"Journée avec repas")},
            {"commentaire" : u"", "IDactivite" : 1, "label" : _(u"Demi-journée avec repas")},
            {"commentaire" : u"", "IDactivite" : 1, "label" : _(u"Demi-journée")},
            ],
        )
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
