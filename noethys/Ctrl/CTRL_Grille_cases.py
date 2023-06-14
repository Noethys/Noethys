#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""

import wx
from Ctrl import CTRL_Bouton_image
import wx.grid as gridlib
import datetime
import copy
import time
import textwrap
import operator

from Data import DATA_Touches as Touches
from Ctrl import CTRL_Grille_renderers
#from Ctrl import CTRL_Grille
CTRL_Grille = UTILS_Adaptations.Import("Ctrl.CTRL_Grille")
from Utils import UTILS_Dates
from Utils import UTILS_Identification
from Utils import UTILS_Divers
from Utils import UTILS_Utilisateurs

from Ctrl.CTRL_Saisie_transport import DICT_CATEGORIES as DICT_CATEGORIES_TRANSPORTS


class CTRL_Couleur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.couleurs = [
            {"code": None, "label": _(u"Noir (par d�faut)")},
            {"code": "red", "label": _(u"Rouge")},
            {"code": "blue", "label": _(u"Bleu")},
            {"code": "green", "label": _(u"Vert")},
            {"code": "purple", "label": _(u"Violet")},
            {"code": "yellow", "label": _(u"Jaune")},
            {"code": "pink", "label": _(u"Rose")},
            {"code": "gray", "label": _(u"Gris")},
            {"code": "orange", "label": _(u"Orange")},
            {"code": "brown", "label": _(u"Marron")},
        ]
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictCouleur in self.couleurs:
            self.dictDonnees[index] = {"code": dictCouleur["code"], "label": dictCouleur["label"]}
            listeItems.append(dictCouleur["label"])
            index += 1
        self.SetItems(listeItems)

    def SetCode(self, code=None):
        for index, values in self.dictDonnees.items():
            if values["code"] == code:
                self.SetSelection(index)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["code"]


class DLG_Saisie_memo(wx.Dialog):
    def __init__(self, parent, texte="", couleur=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        self.label_texte = wx.StaticText(self, wx.ID_ANY, _(u"Texte :"))
        self.ctrl_texte = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_PROCESS_ENTER)
        self.ctrl_texte.SetMinSize((300, -1))

        self.label_couleur = wx.StaticText(self, wx.ID_ANY, _(u"Couleur :"))
        self.ctrl_couleur = CTRL_Couleur(self)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.ctrl_texte.Bind(wx.EVT_KEY_DOWN, self.OnKey)

        # Init contr�les
        if texte:
            self.SetTitle(_(u"Modification d'un m�mo journalier"))
            self.ctrl_texte.SetValue(texte)
            self.ctrl_couleur.SetCode(couleur)
        else:
            self.SetTitle(_(u"Saisie d'un m�mo journalier"))
        self.ctrl_texte.SetFocus()

    def __set_properties(self):
        self.ctrl_texte.SetToolTip(wx.ToolTip(_(u"Saisissez le texte du m�mo")))
        self.ctrl_couleur.SetToolTip(wx.ToolTip(_(u"S�lectionnez une couleur (Noir par d�faut). Cette couleur sera utilis�e dans l'�dition de la liste des consommations au format PDF).")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(3, 2, 10, 10)

        grid_sizer_haut.Add(self.label_texte, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_texte, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_couleur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_couleur, 0, 0, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnKey(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.OnBoutonOk()
        event.Skip()

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event=None):
        self.texte = self.ctrl_texte.GetValue()
        self.couleur = self.ctrl_couleur.GetCode()
        self.EndModal(wx.ID_OK)


class CaseSeparationDate():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, couleurFond=(255, 255, 255)):
        self.typeCase = "date"
        grid.SetReadOnly(numLigne, numColonne, True)
        grid.SetCellBackgroundColour(numLigne, numColonne, couleurFond)

    def GetTypeUnite(self):
        return "separationDate"

    def OnClick(self):
        pass
    
    def OnContextMenu(self):
        pass
    
    def GetTexteInfobulle(self):
        return None

    def GetStatutTexte(self, x, y):
        return None


class CaseSeparationActivite():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDactivite=None, estMemo=False):
        self.typeCase = "activite"
        self.IDactivite = IDactivite
        self.couleurFond = CTRL_Grille.COULEUR_COLONNE_ACTIVITE
        
        # Dessin de la case
        self.renderer = CTRL_Grille_renderers.CaseActivite(self)
        if self.IDactivite != None :
            if grid.dictActivites != None :
                if IDactivite in grid.dictActivites :
                    labelActivite = grid.dictActivites[IDactivite]["nom"]
                else :
                    labelActivite = _(u"Activit� inconnue")
            else:
                labelActivite = _(u"Activit� ID%d") % IDactivite
        if estMemo == True :
            labelActivite = _(u"Informations")
        grid.SetCellValue(numLigne, numColonne, labelActivite)
        grid.SetCellAlignment(numLigne, numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        grid.SetCellRenderer(numLigne, numColonne, self.renderer)
        grid.SetReadOnly(numLigne, numColonne, True)

    def GetTypeUnite(self):
        return "separationActivite"

    def OnClick(self):
        pass
    
    def OnContextMenu(self):
        pass

    def GetTexteInfobulle(self):
        return None

    def GetStatutTexte(self, x, y):
        return None



class CaseMemo():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDindividu=None, date=None, texte="", IDmemo=None, couleur=None):
        self.typeCase = "memo"
        self.grid = grid
        self.ligne = ligne
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.IDindividu = IDindividu
        self.date = date
        self.texte = texte
        self.IDmemo = IDmemo
        self.statut = None
        self.couleur = couleur

        # Dessin de la case
        self.renderer = CTRL_Grille_renderers.CaseMemo(self)
##        self.renderer = gridlib.GridCellAutoWrapStringRenderer()
        self.editor = gridlib.GridCellTextEditor()
        self.grid.SetCellValue(self.numLigne, self.numColonne, self.texte)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.grid.SetCellEditor(self.numLigne, self.numColonne, self.editor)

    def GetTypeUnite(self):
        return "memo"

    def GetTexte(self):
        return self.grid.GetCellValue(self.numLigne, self.numColonne)
    
    def MemoriseValeurs(self):
        texte = self.grid.GetCellValue(self.numLigne, self.numColonne)
        # Cr�ation
        if texte != "" and self.IDmemo == None : self.statut = "ajout"
        # Modification
        if texte != "" and self.IDmemo != None : self.statut = "modification"
        # Suppression
        if texte == "" and self.IDmemo == None : self.statut = None
        if texte == "" and self.IDmemo != None : self.statut = "suppression"
        self.texte = texte
        if (self.IDindividu, self.date) in self.grid.dictMemos :
            self.grid.dictMemos[(self.IDindividu, self.date)]["texte"] = self.texte
            self.grid.dictMemos[(self.IDindividu, self.date)]["statut"] = self.statut
            self.grid.dictMemos[(self.IDindividu, self.date)]["couleur"] = self.couleur
        else:
            self.grid.dictMemos[(self.IDindividu, self.date)] = {"texte" : self.texte, "IDmemo" : None, "statut" : self.statut, "couleur": self.couleur}

    def OnClick(self):
        pass
    
    def OnContextMenu(self):
        pass

    def GetTexteInfobulle(self):
        dictDonnees = {}
        
        # Formatage du texte
        if self.texte != "" :
            listeLignes = textwrap.wrap(self.texte, 45)
            texte = '\n'.join(listeLignes) + u"\n\n"
        else :
            texte = _(u"Aucun m�mo\n\n")
            
        dictDonnees["titre"] = _(u"M�mo journalier")
        dictDonnees["texte"] = texte
        dictDonnees["pied"] = _(u"Double-cliquez sur la case pour modifier")
        dictDonnees["bmp"] = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY) 
        return dictDonnees
    
    def OnDoubleClick(self):
        # R�cup�ration du m�mo
        texte = self.grid.GetCellValue(self.numLigne, self.numColonne)
        
        # Bo�te de dialogue pour modification du m�mo
        dlg = DLG_Saisie_memo(None, texte=texte, couleur=self.couleur)
        if dlg.ShowModal() == wx.ID_OK:
            self.texte = dlg.texte
            self.couleur = dlg.couleur
            dlg.Destroy()
        else:
            dlg.Destroy()

        # M�morisation du m�mo
        self.grid.SetCellValue(self.numLigne, self.numColonne, self.texte)
        self.MemoriseValeurs()
        
    def GetStatutTexte(self, x, y):
        return _(u"Double-cliquez sur la case 'M�mo' pour ajouter, modifier ou supprimer un m�mo")
    
    def SetTexte(self, texte=""):
        """ Modification manuelle du m�mo """
        self.grid.SetCellValue(self.numLigne, self.numColonne, texte)
        self.MemoriseValeurs()
        
        

class CaseTransports():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDindividu=None, date=None):
        self.typeCase = "transports"
        self.grid = grid
        self.ligne = ligne
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.IDindividu = IDindividu
        self.date = date
        self.statut = None
        
        self.couleurFond = (230, 230, 255)
        
        # Dessin de la case
        self.renderer = CTRL_Grille_renderers.CaseTransports(self)
        self.grid.SetCellValue(self.numLigne, self.numColonne, u"")
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)
        
        self.MAJ() 

    def GetTypeUnite(self):
        return "transports"

    def MAJ(self):
        self.dictTransports = self.grid.RechercheTransports(IDindividu=self.IDindividu, date=self.date)
        self.grid.Refresh()
    
    def OnClick(self):
        # R�cup�re la liste des IDtransport actuels
        listeIDinitiale = list(self.dictTransports.keys())
        
        # Label de la ligne
        if self.ligne.modeLabel == "date" :
            label = u"du %s" % self.ligne.labelLigne
        else :
            label = _(u"de %s") % self.ligne.labelLigne
        
        # Dialog
        from Dlg import DLG_Transports_grille
        dlg = DLG_Transports_grille.Dialog(None, grid=self.grid, label=label, IDindividu=self.IDindividu, date=self.date, dictTransports=copy.deepcopy(self.dictTransports))  
        if dlg.ShowModal() == wx.ID_OK:
            dictTransports = dlg.GetDictTransports()
            # Actualise la liste des transports de la grille
            listeNewID = []
            for IDtransport, dictTemp in dictTransports.items() :
                listeNewID.append(IDtransport)
                if (self.IDindividu in self.grid.dict_transports) == False :
                    self.grid.dict_transports[self.IDindividu] = {}
                self.grid.dict_transports[self.IDindividu][IDtransport] = dictTemp
            self.dictTransports = dictTransports
            
            # Supprime les suppressions
            for IDtransport in listeIDinitiale :
                if IDtransport not in listeNewID :
                    del self.grid.dict_transports[self.IDindividu][IDtransport]
            
            # MAJ case
            self.MAJ() 
        
        dlg.Destroy() 
    
    def OnContextMenu(self):
        pass

    def GetTexteInfobulle(self):
        """ Texte pour info-bulle """
        dictDonnees = {}
        dictDonnees["titre"] = _(u"Transports")
        dictDonnees["bmp"] = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Transport.png"), wx.BITMAP_TYPE_ANY) 
        dictDonnees["pied"] = _(u"Cliquez sur la case pour modifier")
        dictDonnees["couleur"] = self.couleurFond
        
        dictTransports = {}
        for IDtransport in CTRL_Grille_renderers.TriTransports(self.dictTransports) :
            dictTemp = self.dictTransports[IDtransport]
            categorie = dictTemp["categorie"]
            labelCategorie = DICT_CATEGORIES_TRANSPORTS[categorie]["label"]
                
            # Analyse du d�part
            depart_nom = u""
            if dictTemp["depart_IDarret"] != None and dictTemp["depart_IDarret"] in CTRL_Grille.DICT_ARRETS :
                depart_nom = CTRL_Grille.DICT_ARRETS[dictTemp["depart_IDarret"]]
            if dictTemp["depart_IDlieu"] != None and dictTemp["depart_IDlieu"] in CTRL_Grille.DICT_LIEUX :
                depart_nom = CTRL_Grille.DICT_LIEUX[dictTemp["depart_IDlieu"]]
            if dictTemp["depart_localisation"] != None :
                depart_nom = self.AnalyseLocalisation(dictTemp["depart_localisation"])
            
            depart_heure = u""
            if dictTemp["depart_heure"] != None :
                depart_heure = dictTemp["depart_heure"].replace(":", "h")

            # Analyse de l'arriv�e
            arrivee_nom = u""
            if dictTemp["arrivee_IDarret"] != None and dictTemp["arrivee_IDarret"] in CTRL_Grille.DICT_ARRETS :
                arrivee_nom = CTRL_Grille.DICT_ARRETS[dictTemp["arrivee_IDarret"]]
            if dictTemp["arrivee_IDlieu"] != None and dictTemp["arrivee_IDlieu"] in CTRL_Grille.DICT_LIEUX :
                arrivee_nom = CTRL_Grille.DICT_LIEUX[dictTemp["arrivee_IDlieu"]]
            if dictTemp["arrivee_localisation"] != None :
                arrivee_nom = self.AnalyseLocalisation(dictTemp["arrivee_localisation"])
            
            arrivee_heure = u""
            if dictTemp["arrivee_heure"] != None :
                arrivee_heure = dictTemp["arrivee_heure"].replace(":", "h")
                
            # Cr�ation du label du schedule
            label = u"%s %s > %s %s" % (depart_heure, depart_nom, arrivee_heure, arrivee_nom)
            
            if (labelCategorie in dictTransports) == False :
                dictTransports[labelCategorie] = []
            dictTransports[labelCategorie].append(label)
        
        # Regroupement par moyen de transport
        texte = u""
        for labelCategorie, listeTextes in dictTransports.items() :
            texte += u"</b>%s\n" % labelCategorie
            for texteLigne in listeTextes :
                texte += u"%s\n" % texteLigne
            texte += u"\n"
        
        dictDonnees["texte"] = texte

        if len(dictTransports) == 0 :
            dictDonnees["texte"] = _(u"Aucun transport\n\n")

        return dictDonnees

    def AnalyseLocalisation(self, texte=""):
        code = texte.split(";")[0]
        if code == "DOMI" :
            return _(u"Domicile")
        if code == "ECOL" :
            IDecole = int(texte.split(";")[1])
            if IDecole in CTRL_Grille.DICT_ECOLES:
                return CTRL_Grille.DICT_ECOLES[IDecole]
        if code == "ACTI" :
            IDactivite = int(texte.split(";")[1])
            if IDactivite in CTRL_Grille.DICT_ACTIVITES:
                return CTRL_Grille.DICT_ACTIVITES[IDactivite]
        if code == "AUTR" :
            code, nom, rue, cp, ville = texte.split(";")
            return u"%s %s %s %s" % (nom, rue, cp, ville)
        return u""

    def GetStatutTexte(self, x, y):
        return _(u"Double-cliquez sur la case 'Transports' pour ajouter, modifier ou supprimer un transport")





class Case():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDindividu=None, IDfamille=None, date=None, IDunite=None, IDactivite=None, verrouillage=0):
        self.typeCase = "consommation"
        self.grid = grid
        self.ligne = ligne
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.date = date
        self.IDunite = IDunite
        self.IDactivite = IDactivite
        self.IDinscription = None
        self.IDgroupe = None
        self.badgeage_debut = None
        self.badgeage_fin = None

        # R�cup�ration du groupe en mode INDIVIDU
        if self.IDindividu in grid.dictInfosInscriptions :
            if self.IDactivite in grid.dictInfosInscriptions[self.IDindividu] :
                if self.grid.mode == "individu" :
                    self.IDgroupe = grid.GetGrandParent().panel_activites.ctrl_activites.GetIDgroupe(self.IDactivite, self.IDindividu)
                if self.IDgroupe == None :
                    self.IDgroupe = grid.dictInfosInscriptions[self.IDindividu][self.IDactivite]["IDgroupe"]

        # Recherche si l'activit� est ouverte
        self.ouvert = self.EstOuvert()

        # R�cup�ration des infos sur l'inscription
        self.dictInfosInscriptions = self.GetInscription() 
        if self.dictInfosInscriptions != None :
            self.IDcategorie_tarif = self.dictInfosInscriptions["IDcategorie_tarif"] 
            
    def GetTypeUnite(self):
        return self.grid.dictUnites[self.IDunite]["type"]

    def EstOuvert(self):
        """ Recherche si l'unit� est ouverte � cette date """
        ouvert = False
        if self.date in self.grid.dictOuvertures:
            if self.IDgroupe in self.grid.dictOuvertures[self.date]:
                if self.IDunite in self.grid.dictOuvertures[self.date][self.IDgroupe]:
                    ouvert = True
        return ouvert

    def GetInscription(self):
        """ Recherche s'il y a une conso pour cette case """
        try :
            dictInfosInscriptions = self.grid.dictInfosInscriptions[self.IDindividu][self.IDactivite]
        except : 
            dictInfosInscriptions = None
        return dictInfosInscriptions

    def MAJ_facturation(self, modeSilencieux=False, evenement=None, action="saisie"):
        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        listeEtiquettes = []
        for conso in self.GetListeConso() :
            if evenement == None or conso.IDevenement == evenement.IDevenement :
                IDprestation = conso.IDprestation
                listeEtiquettes.extend(conso.etiquettes)
                if IDprestation in self.grid.dictPrestations :
                    prestation = self.grid.dictPrestations[IDprestation]
                    if prestation["IDfacture"] and not prestation["forfait_date_debut"]:
                        nomUnite = self.grid.dictUnites[self.IDunite]["nom"]
                        dateComplete = UTILS_Dates.DateComplete(self.date)
                        if self.IDindividu in self.grid.dictInfosIndividus :
                            nom = self.grid.dictInfosIndividus[self.IDindividu]["nom"]
                            prenom = self.grid.dictInfosIndividus[self.IDindividu]["prenom"]
                            if prenom == None :
                                prenom = u""
                        else :
                            nom = u"?"
                            prenom = u"?"
                        nomCase = _(u"%s du %s pour %s %s") % (nomUnite, dateComplete, nom, prenom)
                        if modeSilencieux == False :
                            dlg = wx.MessageDialog(self.grid, _(u"La prestation correspondant � cette consommation appara�t d�j� sur une facture.\n\nIl est donc impossible de la modifier ou de la supprimer."), nomCase, wx.OK | wx.ICON_ERROR)
                            dlg.ShowModal()
                            dlg.Destroy()
                        return False

            if conso.verrouillage == 1 :
                return False

        self.grid.Facturation(self.IDactivite, self.IDindividu, self.IDfamille, self.date, self.IDcategorie_tarif, IDgroupe=self.IDgroupe, case=self, etiquettes=listeEtiquettes, modeSilencieux=modeSilencieux, action=action)
        self.grid.ProgrammeTransports(self.IDindividu, self.date, self.ligne)

    def GetTexteInfobulleConso(self, conso=None, evenement=None):
        """ Renvoie le texte pour l'infobulle de la case """
        dictDonnees = {}
        
        # Titre
        nomUnite = self.grid.dictUnites[self.IDunite]["nom"]
        dateComplete = UTILS_Dates.DateComplete(self.date)
        dictDonnees["titre"] = _(u"%s du %s\n\n") % (nomUnite, dateComplete)
        
        # Image
        dictDonnees["bmp"] = None
        
        texte = u""

        if evenement != None:
            texte += u"===== %s =====\n\n" % evenement.GetStatutTexte()
        
        if conso != None :
            
            # Etiquettes
            nbreEtiquettes = len(conso.etiquettes)
            if nbreEtiquettes > 0 :
                if nbreEtiquettes == 1 :
                    texte += _(u"1 �tiquette : \n")
                else :
                    texte += _(u"%d �tiquettes : \n" % nbreEtiquettes)
                for IDetiquette in conso.etiquettes :
                    if IDetiquette in self.grid.dictEtiquettes :
                        dictEtiquette = self.grid.dictEtiquettes[IDetiquette]
                        texte += u"   - %s \n" % dictEtiquette["label"]
                texte += u"\n"
                
            # Heures de la consommation
            if conso.etat in ("reservation", "attente", "present") :
                if conso.heure_debut == None or conso.heure_fin == None :
                    texte += _(u"Horaire de la consommation non sp�cifi�\n")
                else:
                    texte += _(u"De %s � %s\n") % (conso.heure_debut.replace(":","h"), conso.heure_fin.replace(":","h"))
                if conso.IDgroupe in self.grid.dictGroupes :
                    texte += _(u"Sur le groupe %s \n") % self.grid.dictGroupes[conso.IDgroupe]["nom"]
                else:
                    texte += _(u"Groupe non sp�cifi�\n")
            
            # Quantit�
            if conso.quantite != None :
                texte += _(u"Quantit� : %d\n") % conso.quantite
        
            texte += u"\n"
        
        # Si unit� ferm�e
        if self.ouvert == False :
            return None

        # Recherche nbre places �v�nements
        dictPlacesEvenement = None
        if evenement != None :
            dictPlacesEvenement = evenement.GetPlacesEvenement()
            if dictPlacesEvenement != None :
                if dictPlacesEvenement["nbrePlacesInitial"] != None:
                    texte += _(u"Nbre maximal de places  : %d \n") % dictPlacesEvenement["nbrePlacesInitial"]
                else:
                    texte += _(u"Aucune limitation du nbre de places\n")

                if dictPlacesEvenement["nbrePlacesPrises"] != None:
                    nbrePlacesPrises = dictPlacesEvenement["nbrePlacesPrises"]
                else :
                    nbrePlacesPrises = 0
                texte += _(u"Nbre de places prises : %d \n") % nbrePlacesPrises

                if dictPlacesEvenement["nbrePlacesInitial"] != None :
                    if dictPlacesEvenement["nbrePlacesRestantes"] == None :
                        nbrePlacesRestantes = dictPlacesEvenement["nbrePlacesInitial"]
                    else :
                        nbrePlacesRestantes = dictPlacesEvenement["nbrePlacesRestantes"]
                    texte += _(u"Nbre de places disponibles : %d \n") % nbrePlacesRestantes

                if dictPlacesEvenement["nbreAttente"] != None:
                    texte += _(u"Nbre d'individus sur liste d'attente : %d \n") % dictPlacesEvenement["nbreAttente"]

        # Nbre de places remplissage
        if dictPlacesEvenement == None :

            dictInfosPlaces = self.GetInfosPlaces()
            if dictInfosPlaces != None :
                listeUnitesRemplissage = []
                hasHoraires = False
                for IDunite_remplissage in self.grid.dictUnitesRemplissage[self.IDunite] :
                    nom = self.grid.dictRemplissage[IDunite_remplissage]["nom"]
                    heure_min = UTILS_Dates.HeureStrEnTime(self.grid.dictRemplissage[IDunite_remplissage]["heure_min"])
                    heure_max = UTILS_Dates.HeureStrEnTime(self.grid.dictRemplissage[IDunite_remplissage]["heure_max"])
                    if str(heure_min) not in ("None", "00:00:00") or str(heure_max) not in ("None", "00:00:00") :
                        hasHoraires = True
                    listeUnitesRemplissage.append((IDunite_remplissage, nom, heure_min, heure_max))


                if hasHoraires == True :
                    # Version pour unit�s de remplissage AVEC horaires :
                    nbrePlacesRestantes = None
                    for IDunite_remplissage, nom, heure_min, heure_max in listeUnitesRemplissage :

                        nbrePlacesInitial = dictInfosPlaces[IDunite_remplissage]["nbrePlacesInitial"]
                        nbrePlacesPrises = dictInfosPlaces[IDunite_remplissage]["nbrePlacesPrises"]
                        nbrePlacesRestantes = dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"]
                        nbreAttente = dictInfosPlaces[IDunite_remplissage]["nbreAttente"]
                        seuil_alerte = dictInfosPlaces[IDunite_remplissage]["seuil_alerte"]

                        if str(heure_min) not in ("None", "00:00:00") and str(heure_max) not in ("None", "00:00:00") :
                            texte += _(u"%s (de %s � %s) : \n") % (nom, UTILS_Dates.DatetimeTimeEnStr(heure_min), UTILS_Dates.DatetimeTimeEnStr(heure_max))
                        else :
                            texte += u"%s : \n" % nom
                        if nbrePlacesInitial not in (None, 0) :
                            texte += _(u"   - Nbre maximal de places  : %d \n") % nbrePlacesInitial
                        else:
                            texte += _(u"   - Aucune limitation du nbre de places\n")
                        texte += _(u"   - Nbre de places prises : %d \n") % nbrePlacesPrises
                        if nbrePlacesRestantes != None and nbrePlacesInitial not in (None, 0) :
                            texte += _(u"   - Nbre de places disponibles : %d \n") % nbrePlacesRestantes
                        # texte += _(u"   - Seuil d'alerte : %d \n") % seuil_alerte
                        texte += _(u"   - Nbre d'individus sur liste d'attente : %d \n") % nbreAttente

                if hasHoraires == False :
                    # Version pour unit�s de remplissage SANS horaires :
                    nbrePlacesRestantes = None
                    for IDunite_remplissage, nom, heure_min, heure_max in listeUnitesRemplissage :
                        if nbrePlacesRestantes == None or dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"] < nbrePlacesRestantes :
                            nbrePlacesInitial = dictInfosPlaces[IDunite_remplissage]["nbrePlacesInitial"]
                            nbrePlacesPrises = dictInfosPlaces[IDunite_remplissage]["nbrePlacesPrises"]
                            nbrePlacesRestantes = dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"]
                            nbreAttente = dictInfosPlaces[IDunite_remplissage]["nbreAttente"]
                            seuil_alerte = dictInfosPlaces[IDunite_remplissage]["seuil_alerte"]

                    if nbrePlacesInitial not in (None, 0) :
                        texte += _(u"Nbre maximal de places  : %d \n") % nbrePlacesInitial
                    else:
                        texte += _(u"Aucune limitation du nbre de places\n")
                    texte += _(u"Nbre de places prises : %d \n") % nbrePlacesPrises
                    if nbrePlacesRestantes != None and nbrePlacesInitial not in (None, 0) :
                        texte += _(u"Nbre de places disponibles : %d \n") % nbrePlacesRestantes
                    # texte += _(u"Seuil d'alerte : %d \n") % seuil_alerte
                    texte += _(u"Nbre d'individus sur liste d'attente : %d \n") % nbreAttente

            else:
                texte += _(u"Aucune limitation du nombre de places\n")

            
        # Etat de la case
        texte += "\n"
        if conso != None and conso.etat in ("reservation", "attente", "refus", "present") :
            date_saisie_FR = UTILS_Dates.DateComplete(conso.date_saisie)
            if conso.etat == "reservation" or conso.etat == "present" : texte += _(u"Consommation r�serv�e le %s\n") % date_saisie_FR
            if conso.etat == "attente" : texte += _(u"Consommation mise en attente le %s\n") % date_saisie_FR
            if conso.etat == "refus" : texte += _(u"Consommation refus�e le %s\n") % date_saisie_FR
            if conso.IDutilisateur != None :
                dictUtilisateur = UTILS_Identification.GetAutreDictUtilisateur(conso.IDutilisateur)
                if dictUtilisateur != None :
                    texte += _(u"Par %s %s\n") % (dictUtilisateur["prenom"], dictUtilisateur["nom"])
                else:
                    texte += _(u"Par l'utilisateur ID%d\n") % conso.IDutilisateur
            texte += "\n"
        # Infos Individu
        if self.IDindividu in self.grid.dictInfosIndividus :
            nom = self.grid.dictInfosIndividus[self.IDindividu]["nom"]
            prenom = self.grid.dictInfosIndividus[self.IDindividu]["prenom"]
        else :
            nom = u"?"
            prenom = u"?"
        texte += _(u"Informations sur %s %s : \n") % (prenom, nom)
        date_naiss = self.grid.dictInfosIndividus[self.IDindividu]["date_naiss"]
        if date_naiss != None :
            ageActuel = UTILS_Dates.CalculeAge(datetime.date.today(), date_naiss)
            texte += _(u"   - Age actuel : %d ans \n") % ageActuel
            if conso != None and conso.etat != None :
                ageConso = UTILS_Dates.CalculeAge(self.date, date_naiss)
                texte += _(u"   - Age lors de la consommation : %d ans \n") % ageConso
        else:
            texte += _(u"   - Date de naissance inconnue ! \n")
        # Infos inscription :
        nom_categorie_tarif = self.dictInfosInscriptions["nom_categorie_tarif"]
        if conso != None and conso.etat in ("reservation", "absenti", "absentj", "present") :
            texte += "\n"
            texte += _(u"Cat�gorie de tarif : '%s'\n") % nom_categorie_tarif
        # D�ductions
        if conso != None :
            if conso.IDprestation in self.grid.dictDeductions :
                listeDeductions = self.grid.dictDeductions[conso.IDprestation]
                if len(listeDeductions) == 1 :
                    texte += _(u"1 d�duction sur la prestation :\n")
                else:
                    texte += _(u"%d d�ductions sur la prestation :\n") % len(listeDeductions)
                for dictDeduction in listeDeductions :
                    texte += u"   > %.2f � (%s)\n" % (dictDeduction["montant"], dictDeduction["label"])
        
        if texte.endswith("\n") : 
            texte = texte[:-1]
        dictDonnees["texte"] = texte
        
        # Pied
        dictDonnees["pied"] = _(u"Cliquez sur le bouton droit de la souris pour plus d'infos")
        
        # Couleur
        if conso == None and self.CategorieCase == "multihoraires" :
            dictDonnees["couleur"] = wx.Colour(255, 255, 255)
        elif self.CategorieCase == "evenement" :
            if evenement != None :
                dictDonnees["couleur"] = evenement.GetCouleur()
            else :
                dictDonnees["couleur"] = wx.Colour(255, 255, 255)
        else :
            dictDonnees["couleur"] = self.renderer.GetCouleur(conso)
            
        return dictDonnees

    def ContextMenu(self, conso=None):
        if self.ouvert == False :
            return
        
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item IDENTIFICATION DE LA CASE
        nomUnite = self.grid.dictUnites[self.IDunite]["nom"]
        dateComplete = UTILS_Dates.DateComplete(self.date)
        texteItem = u"- %s du %s -" % (nomUnite, dateComplete)
        item = wx.MenuItem(menuPop, 10, texteItem)
        menuPop.AppendItem(item)
        item.Enable(False)

        # Commandes sp�cifiques
        if self.grid.tarifsForfaitsCreditsPresents == True :
            menuPop.AppendSeparator()

            item = wx.MenuItem(menuPop, 200, _(u"Appliquer un forfait cr�dit"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Forfait.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.AppliquerForfaitCredit, id=200)            

        # Etiquettes
        if conso != None and conso.etat != None :
            menuPop.AppendSeparator()
            
            item = wx.MenuItem(menuPop, 300, _(u"S�lectionner des �tiquettes"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SelectionnerEtiquettes, id=300)            
        
        if conso == None or conso.etat == None :
            menuPop.AppendSeparator()

            item = wx.MenuItem(menuPop, 210, _(u"Ajouter"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.Ajouter, id=210)            

        if conso != None and conso.etat != None :
            menuPop.AppendSeparator()
            
            if self.grid.dictUnites[conso.case.IDunite]["type"] != "Unitaire" and conso.case.CategorieCase != "evenement" :
                item = wx.MenuItem(menuPop, 220, _(u"Modifier"))
                item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
                menuPop.AppendItem(item)
                self.grid.Bind(wx.EVT_MENU, self.Modifier, id=220)            

            item = wx.MenuItem(menuPop, 230, _(u"Supprimer"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.Supprimer, id=230)            
        
        # Etat de la consommation
        if conso != None and conso.etat in ("reservation", "present", "absenti", "absentj") :
            menuPop.AppendSeparator()
            
            item = wx.MenuItem(menuPop, 60, _(u"Pointage en attente"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "reservation" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=60)
            
            item = wx.MenuItem(menuPop, 70, _(u"Pr�sent"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "present" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=70)
            
            item = wx.MenuItem(menuPop, 80, _(u"Absence justifi�e"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "absentj" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=80)
            
            item = wx.MenuItem(menuPop, 90, _(u"Absence injustif�e"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "absenti" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=90)
        
        if conso != None and conso.etat in ("reservation", "attente", "refus") and conso.forfait == None :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 30, _(u"R�servation"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "reservation" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=30)
            item = wx.MenuItem(menuPop, 40, _(u"Attente"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "attente" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=40)
            item = wx.MenuItem(menuPop, 50, _(u"Refus"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if conso.etat == "refus" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=50)
        
        # Changement de Groupe
        listeGroupes = []
        for IDgroupe, dictGroupe in self.grid.dictGroupes.items():
            if dictGroupe["IDactivite"] == self.IDactivite :
                listeGroupes.append( (dictGroupe["ordre"], dictGroupe["nom"], IDgroupe) )
        listeGroupes.sort() 
        if conso != None and len(listeGroupes) > 0 and conso.etat in ("reservation", "attente", "refus") and conso.case.CategorieCase != "evenement" :
            menuPop.AppendSeparator()
            for ordreGroupe, nomGroupe, IDgroupe in listeGroupes :
                IDitem = 10000 + IDgroupe
                item = wx.MenuItem(menuPop, IDitem, nomGroupe, kind=wx.ITEM_RADIO)
                menuPop.AppendItem(item)
                if conso.IDgroupe == IDgroupe : item.Check(True)
                self.grid.Bind(wx.EVT_MENU, self.SetGroupe, id=IDitem)
                
        # D�tail de la consommation
        if conso != None and conso.etat in ("reservation", "present", "absenti", "absentj", "attente", "refus") :
            menuPop.AppendSeparator()
            
            item = wx.MenuItem(menuPop, 100, _(u"Recalculer la prestation"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.MAJ_facturation_menu, id=100)            
            
            item = wx.MenuItem(menuPop, 20, _(u"D�tail de la consommation"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_zoom.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.DLG_detail, id=20)
                            
        self.grid.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def MAJ_facturation_menu(self, event):
        self.MAJ_facturation() 
        
    def AppliquerForfaitCredit(self, event=None):
        try:
            self.grid.GetGrandParent().panel_forfaits.Ajouter(date_debut=self.date, IDfamille=self.IDfamille)
        except:
            self.grid.GetGrandParent().GetParent().panel_forfaits.Ajouter(date_debut=self.date, IDfamille=self.IDfamille)
        
    def GetInfosPlaces(self):
        if (self.IDunite in self.grid.dictUnitesRemplissage) == False :
            return None
        
        try :
            etiquettesCoches = self.grid.GetGrandParent().panel_etiquettes.GetCoches(self.IDactivite)
        except :
            etiquettesCoches = []
            
        # Recherche des nbre de places
        dictInfosPlaces = {}
        for IDunite_remplissage in self.grid.dictUnitesRemplissage[self.IDunite] :
            
            etiquettesRemplissage = self.grid.dictRemplissage[IDunite_remplissage]["etiquettes"]
            
            # R�cup�re le nombre de places restantes pour le groupe
            nbrePlacesInitial = 0
            try :
                nbrePlacesInitial = self.grid.dictRemplissage[IDunite_remplissage][self.date][self.IDgroupe]
            except :
                nbrePlacesInitial = 0
            
            # Filtre �tiquettes
            if len(etiquettesRemplissage) > 0 :
                etiquettesCommunes = set(etiquettesRemplissage) & set(etiquettesCoches)
                if len(etiquettesCommunes) == 0 :
                    nbrePlacesInitial = 0
                
            nbrePlacesPrises = 0
            nbreAttente = 0
            try :
                d = self.grid.dictRemplissage2[IDunite_remplissage][self.date][self.IDgroupe]
                if "reservation" in d : nbrePlacesPrises += d["reservation"]
                if "present" in d : nbrePlacesPrises += d["present"]
                if "attente" in d : nbreAttente += d["attente"]
            except :
                nbrePlacesPrises = 0
                nbreAttente = 0
            
            if nbrePlacesInitial == None : nbrePlacesInitial = 0
            if nbrePlacesPrises == None : nbrePlacesPrises = 0
            nbrePlacesRestantes = nbrePlacesInitial - nbrePlacesPrises
            
            # R�cup�re le nombre de places restantes pour l'ensemble des groupes
            nbrePlacesInitialTousGroupes = 0
            try :
                nbrePlacesInitialTousGroupes = self.grid.dictRemplissage[IDunite_remplissage][self.date][None]
            except :
                nbrePlacesInitialTousGroupes = 0
            
            if nbrePlacesInitialTousGroupes > 0 :
                nbrePlacesPrisesTousGroupes = 0
                try :
                    for IDgroupe, d in self.grid.dictRemplissage2[IDunite_remplissage][self.date].items() :
                        if "reservation" in d : nbrePlacesPrisesTousGroupes += d["reservation"]
                        if "present" in d : nbrePlacesPrisesTousGroupes += d["present"]
                except :
                    nbrePlacesPrisesTousGroupes = 0
                
                nbrePlacesRestantesTousGroupes = nbrePlacesInitialTousGroupes - nbrePlacesPrisesTousGroupes
                if nbrePlacesRestantesTousGroupes < nbrePlacesRestantes or nbrePlacesInitial == 0 :
                    nbrePlacesInitial = nbrePlacesInitialTousGroupes
                    nbrePlacesPrises = nbrePlacesPrisesTousGroupes
                    nbrePlacesRestantes = nbrePlacesRestantesTousGroupes
                    
            # R�cup�re le seuil_alerte
            seuil_alerte = self.grid.dictRemplissage[IDunite_remplissage]["seuil_alerte"]
            if seuil_alerte == None :
                seuil_alerte = 0
                        
            # Cr�ation d'un dictionnaire de r�ponses
            dictInfosPlaces[IDunite_remplissage] = {
                "nbrePlacesInitial" : nbrePlacesInitial, 
                "nbrePlacesPrises" : nbrePlacesPrises, 
                "nbrePlacesRestantes" : nbrePlacesRestantes, 
                "seuil_alerte" : seuil_alerte,
                "nbreAttente" : nbreAttente,
                }
        
        return dictInfosPlaces

    def GetRect(self):
        return self.grid.CellToRect(self.numLigne, self.numColonne)

    def Refresh(self):
        rect = self.GetRect()
        x, y = self.grid.CalcScrolledPosition(rect.GetX(), rect.GetY())
        rect = wx.Rect(x, y, rect.GetWidth(), rect.GetHeight())
        self.grid.GetGridWindow().Refresh(False, rect)

    def MAJremplissage(self):
        # Recalcule tout le remplissage de la grille
        self.grid.CalcRemplissage()
        # Modifie la couleur des autres cases de la ligne ou de toute la grille en fonction du remplissage + MAJ Totaux Gestionnaire de conso
        if self.grid.mode == "date" :
            self.grid.MAJcouleurCases(saufLigne=None)
            self.grid.GetGrandParent().MAJ_totaux_contenu()
        else:
            #self.ligne.MAJcouleurCases(saufCase=self) # Cette ligne ne mettait pas � jour si fraterie affich�e

            # Met � jour l'affichage de toutes les lignes de la m�me date (pour prendre en charge les frateries)
            for numLigne, ligne in self.grid.dictLignes.items() :
                if ligne.estSeparation == False and ligne.date == self.date :
                    ligne.MAJcouleurCases()


    def VerifieCompatibilitesUnites(self):
        listeIncompatibilites = self.grid.dictUnites[self.IDunite]["unites_incompatibles"]
        for numCol, case in self.ligne.dictCases.items():
            if case.typeCase == "consommation" :
                IDunite = case.IDunite
                for conso in case.GetListeConso() :
                    if conso.etat in ["reservation", "present"] and IDunite in listeIncompatibilites :
                        return IDunite
        return None

    def ProtectionsModifSuppr(self, conso=None, modeSilencieux=False):
        """ Protections anti modif et suppression de conso """
        # Si la conso est dans une facture, on annule la suppression
        if conso.IDfacture != None :
            dlg = wx.MessageDialog(self.grid, _(u"Cette consommation appara�t sur une facture d�j� �dit�e.\nIl est donc impossible de la supprimer !\n\n(Pour la supprimer, il faut d'abord annuler la facture)"), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Si la conso est dans un forfait non supprimable
        if conso.forfait == 2 :
            dlg = wx.MessageDialog(self.grid, _(u"Cette consommation fait partie d'un forfait qui ne peut �tre supprim� !\n\n(Pour le supprimer, il faut d�sinscrire l'individu de cette activit�)"), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Si la conso est verrouill�e, on annule l'action
        if conso.verrouillage == 1 :
            if modeSilencieux == False :
                dlg = wx.MessageDialog(self.grid, _(u"Vous ne pouvez pas modifier une consommation verrouill�e !"), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
            return False

        # Si la conso est "present", on annule l'action
        if conso.etat == "present" and modeSilencieux == False :
            dlg = wx.MessageDialog(self.grid, _(u"Vous ne pouvez pas modifier une consommation point�e 'pr�sent' !"), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Si la conso est "absent", on annule l'action
        if (conso.etat == "absenti" or conso.etat == "absentj") and modeSilencieux == False :
            dlg = wx.MessageDialog(self.grid, _(u"Vous ne pouvez pas supprimer une consommation point�e 'absent' !"), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Regarde si la prestation appara�t d�j� sur une facture
        if conso.IDprestation in self.grid.dictPrestations :
            prestation = self.grid.dictPrestations[conso.IDprestation]
            if prestation["IDfacture"] and not prestation["forfait_date_debut"]:
                dlg = wx.MessageDialog(self.grid, _(u"La prestation correspondant � cette consommation appara�t d�j� sur une facture.\n\nIl est donc impossible de la modifier ou de la supprimer."), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Regarde si la prestation correspondante est d�ja pay�e
        if conso.IDprestation in self.grid.dictPrestations and modeSilencieux == False :
            montantPrestation = self.grid.dictPrestations[conso.IDprestation]["montant"]
            montantVentilation = self.grid.dictPrestations[conso.IDprestation]["montantVentilation"]
            if montantVentilation > 0.0 :
                message = _(u"La prestation correspondant � cette consommation a d�j� �t� ventil�e sur un r�glement.\n\nSouhaitez-vous quand-m�me modifier ou supprimer cette consommation ? \n\n(Dans ce cas, la ventilation sera supprim�e)")
                dlg = wx.MessageDialog(self.grid, message, _(u"Suppression"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal() 
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    return False
            
        return True
    
    def OnTouchesRaccourcisPerso(self):
        for code, IDunite in self.grid.listeTouchesRaccourcis :
            if IDunite != self.IDunite :
                if wx.GetKeyState(Touches.DICT_TOUCHES[code][1]) == True :
                    # Cr�ation d'une conso supp
                    for numColonne, case in self.ligne.dictCases.items() :
                        if case.typeCase == "consommation" :
                            if case.IDunite == IDunite :
                                if case.CategorieCase == "multihoraires" :
                                    case.SaisieBarre(case.heure_min, case.heure_max, TouchesRaccourciActives=False)
                                else :
                                    case.OnClick(TouchesRaccourciActives=False)

    def SupprimeForfaitDate(self, IDprestationForfait=None):
        """ Suppression de toutes les conso d'un forfait """
        listeCases = []
        for IDindividu, dictDates in self.grid.dictConsoIndividus.items() :
            for date, dictUnites in dictDates.items() :
                for IDunite, listeConso in dictUnites.items() :
                    for conso in listeConso :
                        case = conso.case
                        if case != None : 
                            if conso.IDprestation == IDprestationForfait :
                                # Suppression conso multihoraires
                                if case.CategorieCase == "multihoraires" :
                                    conso.etat = None
                                    conso.forfait = None
                                    if conso.IDconso != None : 
                                        conso.statut = "suppression"
                                        self.grid.listeConsoSupprimees.append(conso)
                                    if conso.IDconso == None : 
                                        conso.statut = "suppression"
                                    case.MAJ_facturation(action="suppression")
                                    case.listeBarres.remove(conso.barre)
                                    self.grid.dictConsoIndividus[case.IDindividu][case.date][case.IDunite].remove(conso)
                                    self.Refresh() 
                                else :
                                    # Suppression conso standard
                                    if conso.etat != None :
                                        case.etat = None
                                        case.forfait = None
                                        if case.IDconso != None : case.statut = "suppression"
                                        if case.IDconso == None : case.statut = None
                                        case.MemoriseValeurs()
                                        case.Refresh()
                                        case.grid.listeHistorique.append((IDindividu, date, IDunite, _(u"Suppression d'une conso forfait")))
                                        if case not in listeCases :
                                            listeCases.append(case)
        
        for case in listeCases :
            case.MAJ_facturation(action="suppression")
                                            
        self.MAJremplissage()

                        




class CaseStandard(Case):
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDindividu=None, IDfamille=None, date=None, IDunite=None, IDactivite=None, verrouillage=0):
        Case.__init__(self, ligne, grid, numLigne, numColonne, IDindividu, IDfamille, date, IDunite, IDactivite, verrouillage)
        self.CategorieCase = "standard"
        self.ligne = ligne

        self.statut = None # statuts possibles = None, ajout, modification, suppression
        self.IDconso = None
        self.heure_debut = None
        self.heure_fin = None
        self.etat = None
        self.verrouillage = verrouillage
        self.date_saisie = None
        self.IDutilisateur = None
        self.IDcategorie_tarif = None
        self.IDcompte_payeur = None
        self.IDprestation = None
        self.forfait = None
        self.IDfacture = None
        self.quantite = None
        self.etiquettes = []
        self.badgeage_debut = None
        self.badgeage_fin = None

        # Recherche s'il y a des conso pour cette case
        self.conso = self.GetConso() 

        # Importation des donn�es de la conso
        if self.conso != None :
            self.IDconso = self.conso.IDconso
            self.heure_debut = self.conso.heure_debut
            self.heure_fin = self.conso.heure_fin
            self.etat = self.conso.etat
            self.date_saisie = self.conso.date_saisie
            self.IDutilisateur = self.conso.IDutilisateur
            self.IDcategorie_tarif = self.conso.IDcategorie_tarif
            self.IDcompte_payeur = self.conso.IDcompte_payeur
            self.IDprestation = self.conso.IDprestation
            self.forfait = self.conso.forfait
            #self.IDfamille = self.conso.IDfamille
            self.statut = self.conso.statut
            self.quantite = self.conso.quantite
            self.IDgroupe = self.conso.IDgroupe
            self.IDinscription = self.conso.IDinscription
            self.etiquettes = self.conso.etiquettes
            self.verrouillage = verrouillage

            if self.IDprestation != None and self.IDprestation in self.grid.dictPrestations :
                self.IDfacture = self.grid.dictPrestations[self.IDprestation]["IDfacture"]
            
            self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite][0].case = self
        
        else :
            self.conso = CTRL_Grille.Conso()
                    
        # Dessin de la case
        self.renderer = CTRL_Grille_renderers.CaseStandard(self)
        self.grid.SetCellValue(self.numLigne, self.numColonne, u"")
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)
    
            
    def GetConso(self):
        """ Recherche s'il y a une conso pour cette case """
        try :
            conso = self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite][0]
        except : 
            conso = None
        return conso
    
    def GetListeConso(self):
        return [self.conso,]
                        
    def OnClick(self, TouchesRaccourciActives=True, saisieHeureDebut=None, saisieHeureFin=None, saisieQuantite=None, modeSilencieux=False, ForcerSuppr=False, etiquettes=None, badgeage_debut=None, badgeage_fin=None):
        """ Lors d'un clic sur la case """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
        action = None

        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        # R�cup�ration du mode de saisie
        mode = self.grid.GetGrandParent().panel_grille.GetMode()
        
        # R�cup�ration des �tiquettes
        if etiquettes != None :
            self.etiquettes = etiquettes
        else :
            self.etiquettes = self.grid.GetGrandParent().panel_etiquettes.GetCoches(self.IDactivite)
        
        # Si l'unit� est ferm�e
        if self.ouvert == False : 
            return
        
        # Quantit� actuelle
        if self.quantite != None :
            quantiteTemp = self.quantite
        else:
            quantiteTemp = 1
        
        # Touches de commandes rapides
        if wx.GetKeyState(97) == True : # Touche "a" pour Pointage en attente...
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.etat in ("present", "absenti", "absentj") :
                self.ModifieEtat(etat="reservation")
            return
        if wx.GetKeyState(112) == True : # Touche "p" pour Pr�sent
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.etat in ("reservation", "absenti", "absentj") :
                self.ModifieEtat(etat="present")
            return
        if wx.GetKeyState(105) == True : # Touche "i" pour Absence injustif�e
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.etat in ("reservation", "present", "absentj") :
                self.ModifieEtat(etat="absenti")
            return
        if wx.GetKeyState(106) == True : # Touche "j" pour Absence justifi�e
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.etat in ("reservation", "present", "absenti") :
                self.ModifieEtat(etat="absentj")
            return

        # Protections anti modification et suppression
        conso = self.GetConso()
        if conso != None and self.ProtectionsModifSuppr(conso, modeSilencieux) == False :
            return
        if self.verrouillage == 1 :
            return

        # Touches de raccourci
        if TouchesRaccourciActives == True :
            self.OnTouchesRaccourcisPerso() 
            
        # ------------- Suppression d'un forfait supprimable ----------------
        if self.etat != None and self.forfait == 1 :
            
            # Demande la confirmation de la suppression du forfait
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
            
            dlg = wx.MessageDialog(self.grid, _(u"Cette consommation fait partie d'un forfait supprimable.\n\nSouhaitez-vous supprimer le forfait et toutes les consommations rattach�es ?"), _(u"Suppression"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                self.SupprimeForfaitDate(self.IDprestation)
            return


        elif self.etat != None and self.forfait != 2 :
            
            # ----- Suppression ou modification de la consommation -----
            
            typeUnite = self.grid.dictUnites[self.IDunite]["type"]
            heure_debut_fixe = self.grid.dictUnites[self.IDunite]["heure_debut_fixe"]
            heure_fin_fixe = self.grid.dictUnites[self.IDunite]["heure_fin_fixe"]
                        
            # Si c'est une unit� HORAIRE -> Propose une modification ou une suppression
            if typeUnite == "Horaire" :
                
                if saisieHeureDebut != None or saisieHeureFin!= None :
                    # Envoi direct des heures � saisir
                    if saisieHeureDebut != None :
                        heure_debut = saisieHeureDebut
                    else :
                        heure_debut = self.heure_debut
                    if saisieHeureFin != None :
                        heure_fin = saisieHeureFin
                    else :
                        heure_fin = self.heure_fin
                    reponse = wx.ID_OK

                elif wx.GetKeyState(99) == True :
                    # Raccourci touche C pour copier les horaires
                    if self.IDunite in self.grid.memoireHoraires :
                        heure_debut = self.grid.memoireHoraires[self.IDunite]["heure_debut"]
                        heure_fin = self.grid.memoireHoraires[self.IDunite]["heure_fin"]
                        reponse = wx.ID_OK
                    else:
                        reponse = None
                    
                elif wx.GetKeyState(115) == True or ForcerSuppr == True :
                    # Raccourci touche S pour supprimer les horaires
                    reponse = 3
                    
                else :
                    # Demande l'horaire
                    from Dlg import DLG_Saisie_conso_horaire
                    dlg = DLG_Saisie_conso_horaire.Dialog(None, nouveau=False)
                    dlg.SetHeureDebut(self.heure_debut, heure_debut_fixe)
                    dlg.SetHeureFin(self.heure_fin, heure_fin_fixe)
                    reponse = dlg.ShowModal()
                    heure_debut = dlg.GetHeureDebut()
                    heure_fin = dlg.GetHeureFin()
                    dlg.Destroy()
                
                if reponse == wx.ID_OK:
                    # Modification des heures saisies
                    if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
                    self.heure_debut = heure_debut
                    self.heure_fin = heure_fin
                    if self.IDconso != None : self.statut = "modification"
                    self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Modification d'une consommation horaire")))
                    
                    # M�morisation des horaires pour le raccourci
                    self.grid.memoireHoraires[self.IDunite] = {"heure_debut":heure_debut, "heure_fin":heure_fin}
                    action = "modification"
                    
                elif reponse == 3 :
                    # Suppression de la conso horaire
                    if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
                    self.etat = None
                    if self.IDconso != None : self.statut = "suppression"
                    if self.IDconso == None : self.statut = None
                    self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Suppression d'une consommation horaire")))
                    action = "suppression"
                   
                else:
                    # Annulation de la modification
                    return


            # Si c'est une unit� QUANTITE -> Propose une modification ou une suppression
            if typeUnite == "Quantite" :
                
                if saisieQuantite != None :
                    # Envoi direct de la quantit� � saisir
                    quantite = saisieQuantite
                    reponse = wx.ID_OK

                elif wx.GetKeyState(99) == True :
                    # Raccourci touche C pour copier
                    if self.IDunite in self.grid.memoireHoraires :
                        quantite = self.grid.memoireHoraires[self.IDunite]["quantite"]
                        reponse = wx.ID_OK
                    else:
                        reponse = None
                    
                elif wx.GetKeyState(115) == True or ForcerSuppr == True:
                    # Raccourci touche S pour supprimer
                    reponse = 3
                    
                else :
                    # Demande la quantit�
                    from Dlg import DLG_Saisie_conso_quantite
                    dlg = DLG_Saisie_conso_quantite.Dialog(None, nouveau=False)
                    dlg.SetQuantite(self.quantite)
                    reponse = dlg.ShowModal()
                    quantite = dlg.GetQuantite()
                    dlg.Destroy()
                
                if reponse == wx.ID_OK:
                    # Modification de la quantit�
                    if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
                    self.quantite = quantite
                    if self.IDconso != None : self.statut = "modification"
                    self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Modification d'une consommation quantit�")))
                    action = "modification"

                    # M�morisation des horaires pour le raccourci
                    self.grid.memoireHoraires[self.IDunite] = {"quantite":quantite}
                    
                elif reponse == 3 :
                    # Suppression de la conso quantit�
                    if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
                    self.etat = None
                    if self.IDconso != None : self.statut = "suppression"
                    if self.IDconso == None : self.statut = None
                    self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Suppression d'une consommation quantit�")))
                    action = "suppression"

                else:
                    # Annulation de la modification
                    return


            if typeUnite == "Unitaire" :
                # Si c'est une unit� STANDARD :   Suppression
                if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
                self.etat = None
                if self.IDconso != None : self.statut = "suppression"
                if self.IDconso == None : self.statut = None
                self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Suppression d'une consommation")))
                action = "suppression"

        else:

            # R�servation
            if self.etat == None and mode in ("reservation", "attente", "refus"):
                self.etat = mode
                action = "saisie"

                if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "creer", IDactivite=self.IDactivite) == False : return
                
                # V�rifie d'abord qu'il n'y a aucune incompatibilit�s entre unit�s
                if mode == "reservation" :
                    incompatibilite = self.VerifieCompatibilitesUnites()
                    if incompatibilite != None :
                        nomUniteCase = self.grid.dictUnites[self.IDunite]["nom"]
                        nomUniteIncompatible = self.grid.dictUnites[incompatibilite]["nom"]
                        dlg = wx.MessageDialog(self.grid, _(u"L'unit� %s est incompatible avec l'unit� %s d�j� s�lectionn�e !") % (nomUniteCase, nomUniteIncompatible), _(u"Incompatibilit�s d'unit�s"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return
                
                # Demande les heures de d�but et de fin si c'est une unit� horaire
                self.heure_debut = self.grid.dictUnites[self.IDunite]["heure_debut"]
                self.heure_fin = self.grid.dictUnites[self.IDunite]["heure_fin"]
                typeUnite = self.grid.dictUnites[self.IDunite]["type"]
                heure_debut_fixe = self.grid.dictUnites[self.IDunite]["heure_debut_fixe"]
                heure_fin_fixe = self.grid.dictUnites[self.IDunite]["heure_fin_fixe"]
                
                if saisieHeureDebut != None or saisieHeureFin != None :
                    # Envoi direct des heures � saisir
                    if saisieHeureDebut != None :
                        heure_debut = saisieHeureDebut
                    else :
                        heure_debut = self.heure_debut
                    if saisieHeureFin != None :
                        heure_fin = saisieHeureFin
                    else :
                        heure_fin = self.heure_fin
                    reponse = wx.ID_OK
                    self.heure_debut = heure_debut
                    self.heure_fin = heure_fin
                    
                if saisieQuantite != None :
                    # Envoi direct de la quantit� � saisir
                    quantite = saisieQuantite
                    reponse = wx.ID_OK
                    self.quantite = quantite
                    
                if typeUnite == "Horaire" :

                    if wx.GetKeyState(99) == True :
                        # Raccourci touche C pour copier les horaires
                        if self.IDunite in self.grid.memoireHoraires :
                            heure_debut = self.grid.memoireHoraires[self.IDunite]["heure_debut"]
                            heure_fin = self.grid.memoireHoraires[self.IDunite]["heure_fin"]
                            reponse = wx.ID_OK
                        else:
                            reponse = None
                            
                    else :
                        
                        if saisieHeureDebut == None and saisieHeureFin == None :
                            # Demande la saisie de l'horaire
                            from Dlg import DLG_Saisie_conso_horaire
                            dlg = DLG_Saisie_conso_horaire.Dialog(None, nouveau=True)
                            dlg.SetHeureDebut(self.heure_debut, heure_debut_fixe)
                            dlg.SetHeureFin(self.heure_fin, heure_fin_fixe)
                            reponse = dlg.ShowModal()
                            heure_debut = dlg.GetHeureDebut()
                            heure_fin = dlg.GetHeureFin()
                            dlg.Destroy()
                    
                    if reponse == wx.ID_OK:
                        self.heure_debut = heure_debut
                        self.heure_fin = heure_fin

                        # M�morisation des horaires pour le raccourci
                        self.grid.memoireHoraires[self.IDunite] = {"heure_debut":heure_debut, "heure_fin":heure_fin}
                    
                    else:
                        return

                if typeUnite == "Quantite" :

                    if wx.GetKeyState(99) == True :
                        # Raccourci touche C pour copier la quantit�
                        if self.IDunite in self.grid.memoireHoraires :
                            quantite = self.grid.memoireHoraires[self.IDunite]["quantite"]
                            reponse = wx.ID_OK
                        else:
                            reponse = None
                            
                    else :
                        
                        if saisieQuantite == None :
                            # Demande la saisie de la quantit�
                            from Dlg import DLG_Saisie_conso_quantite
                            dlg = DLG_Saisie_conso_quantite.Dialog(None, nouveau=True)
                            dlg.SetQuantite(self.quantite)
                            reponse = dlg.ShowModal()
                            quantite = dlg.GetQuantite()
                            dlg.Destroy()
                    
                    if reponse == wx.ID_OK:
                        self.quantite = quantite

                        # M�morisation de la quantit� pour le raccourci
                        self.grid.memoireHoraires[self.IDunite] = {"quantite":quantite}
                    
                    else :
                        return
                
                # V�rifie qu'il y a de la place
                if mode == "reservation":
                    if self.grid.blocageSiComplet == True and self.HasPlaceDisponible() == False :
                        if modeSilencieux == True :
                            return False
                        dlg = wx.MessageDialog(None, _(u"Il n'y a plus de places disponibles.\n\nSouhaitez-vous quand m�me saisir une consommation ?"), _(u"Complet !"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                        reponse = dlg.ShowModal()
                        dlg.Destroy()
                        if reponse != wx.ID_YES :
                            return
                    
                # Modifie l'�tat de la case
                #self.etat = "reservation"
                self.date_saisie = datetime.date.today()
                self.IDcategorie_tarif = self.dictInfosInscriptions["IDcategorie_tarif"] 
                self.IDcompte_payeur = self.dictInfosInscriptions["IDcompte_payeur"]
                self.IDinscription = self.dictInfosInscriptions["IDinscription"]
                self.IDutilisateur = self.grid.IDutilisateur
                if self.IDactivite in self.grid.dictInfosInscriptions[self.IDindividu] :
                    if self.grid.mode == "individu" :
                        self.IDgroupe = self.grid.GetGrandParent().panel_activites.ctrl_activites.GetIDgroupe(self.IDactivite, self.IDindividu)
                    if self.IDgroupe == None :
                        self.IDgroupe = self.grid.dictInfosInscriptions[self.IDindividu][self.IDactivite]["IDgroupe"]
                else:
                    self.IDgroupe = None

                if mode == "reservation" :
                    texte = _(u"Saisie d'une r�servation de consommation")
                elif mode == "attente" :
                    texte = _(u"Saisie d'une consommation en attente")
                else :
                    texte = _(u"Saisie d'une consommation refus�e")
                self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, texte))

            # Modifie le statut de la case
            if self.IDconso == None :
                self.statut = "ajout"
            if self.IDconso != None :
                self.statut = "modification"

        # M�moire badgeage
        if badgeage_debut != None :
            self.badgeage_debut = badgeage_debut
        if badgeage_fin != None :
            self.badgeage_fin = badgeage_fin

        # Sauvegarde des donn�es dans le dictConsoIndividus
        self.MemoriseValeurs()
                
        # Facturation
        self.MAJ_facturation(action=action, modeSilencieux=modeSilencieux)

        # Change l'apparence de la case
        self.Refresh()

        # MAJ Donn�es remplissage
        self.MAJremplissage()

        # Autog�n�ration
        self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)
        
        
    def MemoriseValeurs(self):
        if self.IDconso != None and self.statut != "suppression" : 
            self.statut = "modification"

        if (self.IDindividu in self.grid.dictConsoIndividus) == False :
            self.grid.dictConsoIndividus[self.IDindividu] = {}
        if (self.date in self.grid.dictConsoIndividus[self.IDindividu]) == False :
            self.grid.dictConsoIndividus[self.IDindividu][self.date] = {}
        if (self.IDunite in self.grid.dictConsoIndividus[self.IDindividu][self.date]) == False :
            self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite] = []
        listeConso = self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite]
        
        index = None
        i = 0
        for conso in listeConso :
            if conso == self.conso :
                self.conso = conso
                index = i
            i += 1
        if index == None :
            self.conso = CTRL_Grille.Conso() 
                
        self.conso.IDconso = self.IDconso
        self.conso.IDactivite = self.IDactivite
        self.conso.IDinscription = self.IDinscription
        self.conso.IDgroupe = self.IDgroupe
        self.conso.heure_debut = self.heure_debut
        self.conso.heure_fin = self.heure_fin
        self.conso.etat = self.etat
        self.conso.verrouillage = self.verrouillage
        self.conso.IDfamille = self.IDfamille
        self.conso.IDcompte_payeur = self.IDcompte_payeur
        self.conso.date_saisie = self.date_saisie
        self.conso.IDutilisateur = self.IDutilisateur
        self.conso.IDcategorie_tarif = self.IDcategorie_tarif
        self.conso.IDprestation = self.IDprestation
        self.conso.forfait = self.forfait
        self.conso.quantite = self.quantite
        self.conso.statut = self.statut
        self.conso.case = self
        self.conso.IDindividu = self.IDindividu
        self.conso.IDfamille = self.IDfamille
        self.conso.date = self.date
        self.conso.IDunite = self.IDunite
        self.conso.IDactivite = self.IDactivite
        self.conso.etiquettes = self.etiquettes
        self.conso.badgeage_debut = self.badgeage_debut
        self.conso.badgeage_fin = self.badgeage_fin

        if index != None :
            self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite][index] = self.conso
        else :
            self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite].append(self.conso)
        
                        
    def GetTexteInfobulle(self):
        try :
            texte = self.GetTexteInfobulleConso(self.conso)
        except Exception as err :
            print(err)
            texte = ""
        return texte
    
    def OnContextMenu(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False : return False
        return self.ContextMenu(self.conso)
        
    def SetGroupe(self, event):
        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        IDgroupe = event.GetId() - 10000
        self.IDgroupe = IDgroupe
        self.MemoriseValeurs()
        self.Refresh()
        self.MAJremplissage() 
                    
    def SetEtat(self, event):
        ID = event.GetId()
        if ID == 30 or ID == 60 : 
            self.ModifieEtat(etat="reservation")
        if ID == 40 : 
            self.ModifieEtat(etat="attente")
        if ID == 50 : 
            self.ModifieEtat(etat="refus")
        if ID == 70 : 
            self.ModifieEtat(etat="present")
        if ID == 80 : 
            self.ModifieEtat(etat="absentj")
        if ID == 90 : 
            self.ModifieEtat(etat="absenti")

    def ModifieEtat(self, conso=None, etat="reservation"):
        ancienEtat = self.etat

        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        # V�rifie si prestation correspondante d�j� factur�e
        if self.IDprestation in self.grid.dictPrestations :
            prestation = self.grid.dictPrestations[self.IDprestation]
            if prestation["IDfacture"] and not prestation["forfait_date_debut"]:
                changementPossible = True
                if etat in ("reservation", "present", "absenti") and ancienEtat in ("attente", "refus", "absentj") : 
                    changementPossible = False
                if etat in (None, "attente", "refus", "absentj") and ancienEtat in ("reservation", "present", "absenti") : 
                    changementPossible = False
                if changementPossible == False :
                    dlg = wx.MessageDialog(self.grid, _(u"La prestation correspondant � cette consommation appara�t d�j� sur une facture.\n\nIl est donc impossible de la modifier ou de la supprimer."), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        
        # Modifier �tat
        self.etat = etat
        self.MemoriseValeurs()

        if self.forfait == 0 or self.forfait == None :
            self.MAJ_facturation(action="modification_etat")
        
        self.Refresh()
        self.MAJremplissage() 
        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Modification de l'�tat d'une consommation")))
        self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

    def Verrouillage(self, event):
        self.verrouillage = 1
        if self.statut == None : self.statut = "modification"
        self.MemoriseValeurs()
        self.Refresh()

    def Deverrouillage(self, event):
        self.verrouillage = 0
        if self.statut == None : self.statut = "modification"
        self.MemoriseValeurs()
        self.Refresh()
    
    def DLG_detail(self, event):
        from Dlg import DLG_Detail_conso
        dictConso = self.GetConso() 
        texteInfoBulle = self.GetTexteInfobulle()
        typeUnite = self.grid.dictUnites[dictConso.case.IDunite]["type"]
        dlg = DLG_Detail_conso.Dialog(self.grid, dictConso, texteInfoBulle)
        if typeUnite == "Horaire" :
            dlg.ctrl_heure_debut.Enable(False)
            dlg.ctrl_heure_fin.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            self.IDgroupe = dlg.GetIDgroupe()
            self.heure_debut = dlg.GetHeureDebut()
            self.heure_fin = dlg.GetHeureFin()
            self.MemoriseValeurs()
            if self.IDconso != None : 
                self.statut = "modification"
            self.Refresh()
            self.MAJremplissage()
            self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

        dlg.Destroy()
    
    def Ajouter(self, event=None):
        self.OnClick()
        
    def Modifier(self, event=None):
        """ Modifier la consommation s�lectionn�e """
        self.OnClick()
    
    def Supprimer(self, event=None):
        """ Supprimer la consommation s�lectionn�e """
        for conso in self.GetListeConso() :
            if conso.etat != None :
                self.OnClick()

    def IsCaseDisponible(self, heure_debut=None, heure_fin=None):
        """ Regarde si conso existe d�j� sur ce cr�neau """
        for conso in self.GetListeConso() :
            if conso.etat == None :
                return True
            else :
                return False

    def HasPlaceDisponible(self, heure_debut=None, heure_fin=None):
        """ Regarde si place disponible selon le remplissage """
        dictInfosPlaces = self.GetInfosPlaces()
        if dictInfosPlaces != None :
            nbrePlacesRestantes = None
            for IDunite_remplissage in self.grid.dictUnitesRemplissage[self.IDunite] :
                if (nbrePlacesRestantes == None or dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"] < nbrePlacesRestantes) and dictInfosPlaces[IDunite_remplissage]["nbrePlacesInitial"] not in (0, None) :
                    nbrePlacesRestantes = dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"]
            if nbrePlacesRestantes != None and nbrePlacesRestantes <= 0 :
                return False
        return True

    def GetStatutTexte(self, x, y):
        if self.IsCaseDisponible() == False :
            texte = _(u"Cliquez sur cette case pour modifier ou supprimer la consommation")
        else :
            texte = _(u"Cliquez sur cette case pour ajouter une consommation")
        return texte

    def SelectionnerEtiquettes(self, event):
        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        listeCoches = self.conso.etiquettes
        from Ctrl import CTRL_Etiquettes
        dlg = CTRL_Etiquettes.DialogSelection(self.grid, listeActivites=[self.IDactivite,])
        dlg.SetCoches(listeCoches)
        if dlg.ShowModal() == wx.ID_OK :
            listeCoches = dlg.GetCoches() 
            self.etiquettes = listeCoches
            self.MemoriseValeurs()
            self.MAJ_facturation(action="modification")
            self.Refresh()
            self.MAJremplissage() 
        dlg.Destroy()
        

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Barre():
    def __init__(self, case=None, calque=0, conso=None):
        self.case = case
        self.calque = calque
        self.conso = conso
        self.conso.case = self.case
        self.conso.barre = self
        
        # Attributs
        self.readOnly = False
        self.rectBarre = None
    
    def SetHeures(self, heure_debut=None, heure_fin=None) :
        if heure_debut != None :
            self.conso.heure_debut = UTILS_Dates.DatetimeTimeEnStr(heure_debut, separateur=":")
        if heure_fin != None :
            self.conso.heure_fin = UTILS_Dates.DatetimeTimeEnStr(heure_fin, separateur=":")
        self.MemoriseValeurs() 
        self.case.grid.memoireHoraires[self.case.IDunite] = {"heure_debut":self.conso.heure_debut, "heure_fin":self.conso.heure_fin}


    def UpdateRect(self):
        rectCase = self.case.GetRect()
        # v�rifie que les heures sont ok
        self.heure_debut = UTILS_Dates.HeureStrEnTime(self.conso.heure_debut)
        self.heure_fin = UTILS_Dates.HeureStrEnTime(self.conso.heure_fin)
        # Recherche des positions
        posG = self.case.HeureEnPos(self.heure_debut)
        posD = self.case.HeureEnPos(self.heure_fin)
        # Cr�ation du wx.rect
        x = CTRL_Grille_renderers.PADDING_MULTIHORAIRES["horizontal"] + posG
        largeur = posD - posG
        y = CTRL_Grille_renderers.PADDING_MULTIHORAIRES["vertical"]
        hauteur = rectCase.GetHeight() -  CTRL_Grille_renderers.PADDING_MULTIHORAIRES["vertical"] * 2
        self.rectBarre = wx.Rect(x, y, largeur, hauteur)

    def GetRect(self, mode="case"):
        """ Modes : 
        case = les coordonn�es dans la case
        grid = les coordonn�es dans la grid
        """
        if self.rectBarre == None :
            return None
        if mode == "case" :
            return self.rectBarre
        if mode == "grid" :
            return wx.Rect(self.rectBarre.x + self.case.GetRect().x, self.rectBarre.y + self.case.GetRect().y, self.rectBarre.GetWidth(), self.rectBarre.GetHeight())
    
    def Refresh(self):
        self.case.Refresh()
        
    def MemoriseValeurs(self):
        self.conso.case = self.case
        self.conso.barre = self

        ajout = False
        if (self.case.IDindividu in self.case.grid.dictConsoIndividus) == False :
            self.case.grid.dictConsoIndividus[self.case.IDindividu] = {}
        if (self.case.date in self.case.grid.dictConsoIndividus[self.case.IDindividu]) == False :
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date] = {}
        if (self.case.IDunite in self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date]) == False :
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite] = []
        
        listeConso = self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite]
        position = None
        index = 0
        for conso in listeConso :
            if self.conso == conso :
                position = index
            index += 1
        
        if position == None :
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite].append(self.conso)
        else :
            if self.conso.statut not in ("ajout", "suppression") : 
                self.conso.statut = "modification"
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite][position] = self.conso
        
    def MAJ_facturation(self, action=None):
        self.case.MAJ_facturation(action=action)
        
        

class CaseMultihoraires(Case):
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDindividu=None, IDfamille=None, date=None, IDunite=None, IDactivite=None, verrouillage=0, heure_min=None, heure_max=None):
        Case.__init__(self, ligne, grid, numLigne, numColonne, IDindividu, IDfamille, date, IDunite, IDactivite, verrouillage)
        self.CategorieCase = "multihoraires"
        self.verrouillage = verrouillage
        
        # Plage horaire
        self.heure_min = heure_min
        self.heure_max = heure_max
        
        # Dessin de la case
        self.renderer = CTRL_Grille_renderers.CaseMultihoraires(self)
        self.grid.SetCellValue(self.numLigne, self.numColonne, u"")
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)
        
        # Cr�ation des barres
        self.listeBarres = self.GetListeBarres()
        
    def GetListeConso(self):
        listeConso = []
        for barre in self.listeBarres :
            listeConso.append(barre.conso) 
        return listeConso

    def HeureEnPos(self, heure):
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.heure_max, self.heure_min)
        return 1.0 * UTILS_Dates.SoustractionHeures(heure, self.heure_min).seconds / tempsAffichable.seconds * self.GetLargeurMax() 

    def PosEnHeure(self, x, arrondir=False):
        tempsAffichable = UTILS_Dates.SoustractionHeures(self.heure_max, self.heure_min)
        pos = x - self.GetRect().GetX() - CTRL_Grille_renderers.PADDING_MULTIHORAIRES["horizontal"]
        temp = datetime.timedelta(seconds=1.0 * pos / self.GetLargeurMax() * tempsAffichable.seconds)
        if arrondir == True :
            temp = UTILS_Dates.DeltaEnTime(temp)
            minutes = temp.strftime("%M")
            if int(minutes[1]) < 5 : minutes = "%s%d" % (minutes[0], 0)
            if int(minutes[1]) > 5 : minutes = "%s%d" % (minutes[0], 5)
            temp = datetime.time(int(temp.strftime("%H")), int(minutes))
        heure = UTILS_Dates.AdditionHeures(self.heure_min, temp)
        return UTILS_Dates.DeltaEnTime(heure)

    def GetLargeurMax(self):
        return self.GetRect().GetWidth() - CTRL_Grille_renderers.PADDING_MULTIHORAIRES["horizontal"] * 2
        
    def ContraintesCalque(self, barreCible, heure_debut, heure_fin):
        """ V�rifie si un calque ne se superpose sur un autre du m�me calque """
        numCalque = barreCible.calque 
        for barre in self.listeBarres :
            if barre.calque == numCalque and barre != barreCible :
                if heure_debut < barre.heure_fin and heure_fin > barre.heure_debut :
                    return True
        return False
    
    def GetListeBarres(self):
        listeBarres = []
        if self.IDindividu in self.grid.dictConsoIndividus :
            if self.date in self.grid.dictConsoIndividus[self.IDindividu] :
                if self.IDunite in self.grid.dictConsoIndividus[self.IDindividu][self.date] :
                    for conso in self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite] :
                        barre = Barre(case=self, calque=1, conso=conso)
                        listeBarres.append(barre)
        return listeBarres

    def GetTexteInfobulle(self):
        barre = self.RechercheBarreMousePosition() 
        if barre != None :
            conso = barre.conso
        else :
            conso = None
        return self.GetTexteInfobulleConso(conso)

    def OnContextMenu(self):
        barre = self.RechercheBarreMousePosition() 
        if barre != None :
            self.barreContextMenu = barre
            return self.ContextMenu(barre.conso)
        else :
            return self.ContextMenu()
    
    def RechercheBarreMousePosition(self):
        x, y = self.grid.CalcUnscrolledPosition(self.grid.ScreenToClient(wx.GetMousePosition()))
        x = x - self.grid.GetRowLabelSize()
        y = y - self.grid.GetColLabelSize()
        barre = self.RechercheBarre(x, y)
        if barre == None :
            return None
        else :
            barre, region, x, y, ecart = barre
            return barre
        
    def RechercheBarre(self, x, y, readOnlyInclus=True):
        for barre in self.listeBarres :
            if readOnlyInclus == True or (readOnlyInclus == False and barre.readOnly == False) :
                rectBarre = barre.GetRect("grid")
                if rectBarre != None :
                    if 'phoenix' in wx.PlatformInfo:
                        contains = rectBarre.Contains(x, y)
                    else:
                        contains = rectBarre.ContainsXY(x, y)
                    if contains == True :
                        # R�gion
                        if x < rectBarre.width / 4.0 + rectBarre.x :
                            region = "gauche"
                            ecart = x - rectBarre.x
                        elif x > rectBarre.width / 4.0 * 3 + rectBarre.x :
                            region = "droite"
                            ecart = rectBarre.width + rectBarre.x - x
                        else :
                            region = "milieu"
                            ecart = x - rectBarre.x
                        return barre, region, x, y, ecart
        return None

    def SetGroupe(self, event):
        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        barre = self.barreContextMenu
        barre.conso.IDgroupe = event.GetId() - 10000
        barre.MemoriseValeurs()
        if barre.conso.IDconso != None : 
            barre.conso.statut = "modification"
        barre.Refresh()
        self.MAJremplissage() 
    
    def SetEtat(self, event):
        barre = self.barreContextMenu
        ID = event.GetId()
        if ID == 30 or ID == 60 : 
            self.ModifieEtat(barre.conso, "reservation")
        if ID == 40 : 
            self.ModifieEtat(barre.conso, "attente")
        if ID == 50 : 
            self.ModifieEtat(barre.conso, "refus")
        if ID == 70 : 
            self.ModifieEtat(barre.conso, "present")
        if ID == 80 : 
            self.ModifieEtat(barre.conso, "absentj")
        if ID == 90 : 
            self.ModifieEtat(barre.conso, "absenti")

    def ModifieEtat(self, conso=None, etat="reservation"):
        ancienEtat = conso.etat

        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        # V�rifie si prestation correspondante d�j� factur�e
        if conso.IDprestation in self.grid.dictPrestations :
            prestation = self.grid.dictPrestations[conso.IDprestation]
            if prestation["IDfacture"] and not prestation["forfait_date_debut"]:
                changementPossible = True
                if etat in ("reservation", "present", "absenti") and ancienEtat in ("attente", "refus", "absentj") : 
                    changementPossible = False
                if etat in (None, "attente", "refus", "absentj") and ancienEtat in ("reservation", "present", "absenti") : 
                    changementPossible = False
                if changementPossible == False :
                    dlg = wx.MessageDialog(self.grid, _(u"La prestation correspondant � cette consommation appara�t d�j� sur une facture.\n\nIl est donc impossible de la modifier ou de la supprimer."), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        barre = conso.barre
        barre.conso.etat = etat
        barre.MemoriseValeurs() 
        
        if barre.conso.forfait == 0 or barre.conso.forfait == None :
            if etat in ("reservation", "present", "absenti") and ancienEtat in ("attente", "refus", "absentj") : 
                self.MAJ_facturation(action="modification_etat")
            if etat in ("attente", "refus", "absentj") and ancienEtat in ("reservation", "present", "absenti") : 
                self.MAJ_facturation(action="modification_etat")
            
        barre.Refresh()
        self.MAJremplissage() 
        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Modification de l'�tat d'une consommation multihoraires")))
        
    def Verrouillage(self, event):
        pass
##        self.verrouillage = 1
##        if self.statut == None : self.statut = "modification"
##        self.MemoriseValeurs()
##        self.renderer.MAJ()

    def Deverrouillage(self, event):
        pass
##        self.verrouillage = 0
##        if self.statut == None : self.statut = "modification"
##        self.MemoriseValeurs()
##        self.renderer.MAJ()
    
    def DLG_detail(self, event):
        barre = self.barreContextMenu
        from Dlg import DLG_Detail_conso
        texteInfoBulle = self.GetTexteInfobulleConso(barre.conso)
        dlg = DLG_Detail_conso.Dialog(self.grid, barre.conso, texteInfoBulle)
        if dlg.ShowModal() == wx.ID_OK:
            barre.conso.IDgroupe = dlg.GetIDgroupe()
            barre.conso.heure_debut = dlg.GetHeureDebut()
            barre.conso.heure_fin = dlg.GetHeureFin()
            barre.MemoriseValeurs()
            if barre.conso.IDconso != None : 
                barre.conso.statut = "modification"
            barre.Refresh()
            self.MAJremplissage()
            self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)
        dlg.Destroy()
    
    def SaisieBarre(self, heure_debut=None, heure_fin=None, modeSilencieux=False, TouchesRaccourciActives=True, etiquettes=None, badgeage_debut=None, badgeage_fin=None):
        """ Cr�ation d'une barre + conso """        
        # V�rifie d'abord qu'il n'y a aucune incompatibilit�s entre unit�s
        incompatibilite = self.VerifieCompatibilitesUnites()
        if incompatibilite != None :
            nomUniteCase = self.grid.dictUnites[self.IDunite]["nom"]
            nomUniteIncompatible = self.grid.dictUnites[incompatibilite]["nom"]
            dlg = wx.MessageDialog(self.grid, _(u"L'unit� %s est incompatible avec l'unit� %s d�j� s�lectionn�e !") % (nomUniteCase, nomUniteIncompatible), _(u"Incompatibilit�s d'unit�s"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que la case n'est pas d�j� occup�e
        if self.IsCaseDisponible(heure_debut, heure_fin) == False :
            if modeSilencieux == True : 
                return False
            dlg = wx.MessageDialog(None, _(u"Une consommation existe d�j� sur ce cr�neau horaire !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # V�rifie qu'il y a de la place
        if self.grid.blocageSiComplet == True and self.HasPlaceDisponible(heure_debut, heure_fin) == False :
            if modeSilencieux == True : 
                return False
            dlg = wx.MessageDialog(None, _(u"Il n'y a plus de places disponibles sur cette tranche horaire.\n\nSouhaitez-vous quand m�me saisir une consommation ?"), _(u"Complet !"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES : 
                return 

        # Touches de raccourci
        if TouchesRaccourciActives == True :
            self.OnTouchesRaccourcisPerso() 

        # Cr�ation d'une conso
        conso = CTRL_Grille.Conso() 
        conso.IDconso = None
        conso.IDactivite = self.IDactivite
        conso.IDinscription = self.dictInfosInscriptions["IDinscription"]
        conso.IDgroupe = self.IDgroupe
        conso.heure_debut = UTILS_Dates.DatetimeTimeEnStr(heure_debut, ":") # self.grid.dictUnites[self.IDunite]["heure_debut"]
        conso.heure_fin = UTILS_Dates.DatetimeTimeEnStr(heure_fin, ":") # self.grid.dictUnites[self.IDunite]["heure_fin"]
        if badgeage_debut != None : conso.badgeage_debut = badgeage_debut
        if badgeage_fin != None: conso.badgeage_fin = badgeage_fin
        
        # Mode de saisie
        conso.etat = self.grid.GetGrandParent().panel_grille.GetMode()

        # R�cup�ration des �tiquettes
        if etiquettes != None :
            conso.etiquettes = etiquettes
        else :
            conso.etiquettes = self.grid.GetGrandParent().panel_etiquettes.GetCoches(self.IDactivite)
        
        # Autres param�tres
        conso.verrouillage = 0
        conso.IDfamille = self.IDfamille
        conso.IDcompte_payeur = self.dictInfosInscriptions["IDcompte_payeur"]
        conso.date_saisie = datetime.date.today()
        conso.IDutilisateur = self.grid.IDutilisateur
        conso.IDcategorie_tarif = self.dictInfosInscriptions["IDcategorie_tarif"] 
        conso.IDprestation = None
        conso.forfait = None
        conso.quantite = None
        conso.statut = "ajout"
        conso.IDunite = self.IDunite

        if self.IDactivite in self.grid.dictInfosInscriptions[self.IDindividu] :
            if self.grid.mode == "individu" :
                IDgroupe_temp = self.grid.GetGrandParent().panel_activites.ctrl_activites.GetIDgroupe(self.IDactivite, self.IDindividu)
                if IDgroupe_temp:
                    conso.IDgroupe = IDgroupe_temp
            if self.IDgroupe == None :
                conso.IDgroupe = self.grid.dictInfosInscriptions[self.IDindividu][self.IDactivite]["IDgroupe"]

        self.grid.memoireHoraires[self.IDunite] = {"heure_debut":conso.heure_debut, "heure_fin":conso.heure_fin}

        barre = Barre(case=self, calque=1, conso=conso)
        barre.MemoriseValeurs() 
        self.listeBarres.append(barre)
        self.MAJremplissage()
        
        # Facturation
        self.MAJ_facturation(action="saisie")
        
        barre.Refresh()
        
        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Ajout d'une consommation multihoraires")))        
        
        # Si les heures saisies d�passent les heures min et max, on �largit la colonne Multihoraires
        if (heure_debut < self.heure_min) or (heure_fin > self.heure_max) : 
            self.grid.MAJ_affichage()

        # Autog�n�ration
        self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

        return barre
        
    def AjouterBarre(self, position=None):
        """ Ajouter une barre """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "creer", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False

        # Recherche des horaires � appliquer
        heure_cliquee = self.PosEnHeure(position[0], arrondir=True)
        
        # Recherche d'un emplacement disponible dans la case
        heure_debut = self.heure_min
        heure_fin = self.heure_max
        self.listeBarres.sort(key=operator.attrgetter("heure_debut"))
        for barre in self.listeBarres :
            if heure_cliquee > barre.heure_debut and heure_cliquee > barre.heure_fin :
                heure_debut = barre.heure_fin
            if heure_cliquee < barre.heure_debut and heure_cliquee < barre.heure_fin :
                heure_fin = barre.heure_debut

        # Copie de la conso pr�c�demment saisie
        if wx.GetKeyState(99) == True : 
            if self.IDunite in self.grid.memoireHoraires :
                heure_debut = UTILS_Dates.HeureStrEnTime(self.grid.memoireHoraires[self.IDunite]["heure_debut"])
                heure_fin = UTILS_Dates.HeureStrEnTime(self.grid.memoireHoraires[self.IDunite]["heure_fin"])

        self.SaisieBarre(heure_debut, heure_fin)

    def Ajouter(self, event=None):
        """ Ajouter une barre avec dialog de saisie des heures """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "creer", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False

        heure_debut = self.grid.dictUnites[self.IDunite]["heure_debut"]
        heure_fin = self.grid.dictUnites[self.IDunite]["heure_fin"]
        
        heure_debut_fixe = self.grid.dictUnites[self.IDunite]["heure_debut_fixe"]
        heure_fin_fixe = self.grid.dictUnites[self.IDunite]["heure_fin_fixe"]

        from Dlg import DLG_Saisie_conso_horaire
        dlg = DLG_Saisie_conso_horaire.Dialog(None, nouveau=True, heure_min=heure_debut, heure_max=heure_fin)
        dlg.SetHeureDebut(heure_debut, heure_debut_fixe)
        dlg.SetHeureFin(heure_fin, heure_fin_fixe)
        reponse = dlg.ShowModal()
        heure_debut = UTILS_Dates.HeureStrEnTime(dlg.GetHeureDebut())
        heure_fin = UTILS_Dates.HeureStrEnTime(dlg.GetHeureFin())
        dlg.Destroy()

        if reponse == wx.ID_OK:
            self.SaisieBarre(heure_debut, heure_fin)

    def Modifier(self, event=None):
        """ Modifier la consommation s�lectionn�e """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False
        self.ModifierBarre(self.barreContextMenu)     
    
    def Supprimer(self, event=None):
        """ Supprimer la consommation s�lectionn�e """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False
        self.SupprimerBarre(self.barreContextMenu)
        
    def ModifierBarre(self, barre=None, horaires=None, etiquettes=None, badgeage_debut=None, badgeage_fin=None):
        """ Horaires = None ou (heure_debut, heure_fin) """
        # Protections anti modification et suppression
        if self.ProtectionsModifSuppr(barre.conso) == False :
            return

        if horaires == None :
            heure_debut = UTILS_Dates.DatetimeTimeEnStr(barre.heure_debut, ":")
            heure_fin = UTILS_Dates.DatetimeTimeEnStr(barre.heure_fin, ":")
            heure_debut_fixe = self.grid.dictUnites[self.IDunite]["heure_debut_fixe"]
            heure_fin_fixe = self.grid.dictUnites[self.IDunite]["heure_fin_fixe"]

            from Dlg import DLG_Saisie_conso_horaire
            dlg = DLG_Saisie_conso_horaire.Dialog(None, nouveau=False)
            dlg.SetHeureDebut(heure_debut, heure_debut_fixe)
            dlg.SetHeureFin(heure_fin, heure_fin_fixe)
            reponse = dlg.ShowModal()
            heure_debut = dlg.GetHeureDebut()
            heure_fin = dlg.GetHeureFin()
            dlg.Destroy()
        else :
            heure_debut, heure_fin = horaires
            reponse = wx.ID_OK
            
        if reponse == wx.ID_OK:
            barre.conso.heure_debut = heure_debut
            barre.conso.heure_fin = heure_fin
            barre.conso.badgeage_debut = badgeage_debut
            barre.conso.badgeage_fin = badgeage_fin
            if etiquettes != None :
                barre.conso.etiquettes = etiquettes
            barre.MemoriseValeurs()
            if barre.conso.IDconso != None : 
                barre.conso.statut = "modification"
            self.MAJremplissage()
            self.MAJ_facturation(action="modification")
            barre.Refresh()
            self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Modification d'une consommation multihoraires")))        

            # Si les heures saisies d�passent les heures min et max, on �largit la colonne Multihoraires
            if (heure_debut < str(self.heure_min)) or (heure_fin > str(self.heure_max)) : 
                self.grid.MAJ_affichage()

            # Autog�n�ration
            self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

        elif reponse == 3 :
            # Suppression
            self.SupprimerBarre(barre)


            
    def SupprimerBarre(self, barre=None):
        # Protections anti modification et suppression
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False

        if self.ProtectionsModifSuppr(barre.conso) == False :
            return

        # -Suppression d'un forfait supprimable
        if barre.conso.etat != None and barre.conso.forfait == 1 :
            # Demande la confirmation de la suppression du forfait
            dlg = wx.MessageDialog(self.grid, _(u"Cette consommation fait partie d'un forfait supprimable.\n\nSouhaitez-vous supprimer le forfait et toutes les consommations rattach�es ?"), _(u"Suppression"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                self.SupprimeForfaitDate(barre.conso.IDprestation)
            return

        if barre.conso.etat != None and barre.conso.forfait == 2 :
            print("forfait 2")
            return

        # Suppression
        barre.conso.etat = None
        if barre.conso.IDconso != None : 
            barre.conso.statut = "suppression"
            self.grid.listeConsoSupprimees.append(barre.conso)
        if barre.conso.IDconso == None : 
            barre.conso.statut = "suppression"
        self.MAJ_facturation(action="suppression")
        self.listeBarres.remove(barre)
        self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite].remove(barre.conso)
        self.MAJremplissage()
        self.Refresh() 
        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Suppression d'une consommation multihoraires")))   

        # Autog�n�ration
        self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

    def ToucheRaccourci(self, barre):
        """ Applique une touche raccourci � une barre """
        if wx.GetKeyState(97) == True : # Touche "a" pour Pointage en attente...
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if barre.conso.etat in ("present", "absenti", "absentj") :
                self.ModifieEtat(barre.conso, "reservation")
                
        if wx.GetKeyState(112) == True : # Touche "p" pour Pr�sent
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if barre.conso.etat in ("reservation", "absenti", "absentj") :
                self.ModifieEtat(barre.conso, "present")
                
        if wx.GetKeyState(105) == True : # Touche "i" pour Absence injustif�e
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if barre.conso.etat in ("reservation", "present", "absentj") :
                self.ModifieEtat(barre.conso, "absenti")
                
        if wx.GetKeyState(106) == True : # Touche "j" pour Absence justifi�e
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if barre.conso.etat in ("reservation", "present", "absenti") :
                self.ModifieEtat(barre.conso, "absentj")

        if wx.GetKeyState(115) == True : # Suppression de la conso
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False : return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            self.SupprimerBarre(barre)
            

    def IsCaseDisponible(self, heure_debut=None, heure_fin=None):
        """ Regarde si conso existe d�j� sur ce cr�neau """
        self.listeBarres.sort(key=operator.attrgetter("conso.heure_debut"))
        if type(heure_debut) == datetime.time : heure_debut = UTILS_Dates.DatetimeTimeEnStr(heure_debut, ":")
        if type(heure_fin) == datetime.time : heure_fin = UTILS_Dates.DatetimeTimeEnStr(heure_fin, ":")
        for conso in self.GetListeConso() :
            if str(conso.heure_debut) < str(heure_fin) and str(conso.heure_fin) > str(heure_debut) :
                return False
        return True

    def HasPlaceDisponible(self, heure_debut=None, heure_fin=None):
        """ Regarde si place disponible selon le remplissage """
        dictInfosPlaces = self.GetInfosPlaces()
        if dictInfosPlaces != None :
            for IDunite_remplissage, valeurs in dictInfosPlaces.items() :
                heure_min_remplissage = self.grid.dictRemplissage[IDunite_remplissage]["heure_min"] or ""
                heure_max_remplissage = self.grid.dictRemplissage[IDunite_remplissage]["heure_max"] or ""
                nbrePlacesInitial = valeurs["nbrePlacesInitial"]
                nbrePlacesRestantes = valeurs["nbrePlacesRestantes"]
                if heure_min_remplissage < str(heure_fin) and heure_max_remplissage > str(heure_debut) and nbrePlacesRestantes <= 0 and nbrePlacesInitial not in (0, None) :
                    return False
        return True
        
    def GetStatutTexte(self, x=None, y=None):
        if self.grid.barreMoving != None :
            barre = self.grid.barreMoving["barre"]
        else :
            barre = self.RechercheBarre(x, y, readOnlyInclus=False)
            if barre != None :
                barre, region, xTemp, yTemp, ecart = barre
        if barre != None :
            heure_debut = UTILS_Dates.DatetimeTimeEnStr(barre.heure_debut)
            heure_fin = UTILS_Dates.DatetimeTimeEnStr(barre.heure_fin)
            texte = _(u"Consommation horaire : %s > %s") % (heure_debut, heure_fin)
        else :
            texte = _(u"Double-cliquez pour ajouter une nouvelle consommation horaire")
        return texte

    def SelectionnerEtiquettes(self, event):
        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        barre = self.barreContextMenu
        listeCoches = barre.conso.etiquettes
        from Ctrl import CTRL_Etiquettes
        dlg = CTRL_Etiquettes.DialogSelection(self.grid, listeActivites=[self.IDactivite,])
        dlg.SetCoches(listeCoches)
        if dlg.ShowModal() == wx.ID_OK :
            listeCoches = dlg.GetCoches() 
            barre.conso.etiquettes = listeCoches
            barre.MemoriseValeurs()
            if barre.conso.IDconso != None : 
                barre.conso.statut = "modification"
            self.MAJ_facturation(action="modification")
            barre.Refresh()
            self.MAJremplissage() 
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------

class Evenement():
    def __init__(self, case=None, dict_evenement=None):
        self.case = case

        # Caract�ristiques de l'�v�nement
        self.IDevenement = dict_evenement["IDevenement"]
        self.IDactivite = dict_evenement["IDactivite"]
        self.IDunite = dict_evenement["IDunite"]
        self.IDgroupe = dict_evenement["IDgroupe"]
        self.date = dict_evenement["date"]
        self.nom = dict_evenement["nom"]
        self.capacite_max = dict_evenement["capacite_max"]
        self.heure_debut = dict_evenement["heure_debut"]
        self.heure_fin = dict_evenement["heure_fin"]
        self.montant = dict_evenement["montant"]

        # Rattachement d'une conso
        self.conso = None

    def SetConso(self, conso=None):
        self.conso = conso
        if self.conso != None :
            self.conso.IDevenement = self.IDevenement
            self.conso.evenement = self
            self.conso.case = self.case

    def GetTexteInfobulle(self):
        return self.case.GetTexteInfobulleConso(self.conso, evenement=self)

    def GetStatutTexte(self, x=None, y=None):
        heure_debut = UTILS_Dates.DatetimeTimeEnStr(self.heure_debut)
        heure_fin = UTILS_Dates.DatetimeTimeEnStr(self.heure_fin)
        if heure_debut != "00h00" and heure_fin != "00h00" :
            texte = _(u"%s : %s > %s") % (self.nom, heure_debut, heure_fin)
        else:
            texte = _(u"%s") % self.nom
        return texte

    def Refresh(self):
        self.case.Refresh()

    def MemoriseValeurs(self):
        if (self.case.IDindividu in self.case.grid.dictConsoIndividus) == False:
            self.case.grid.dictConsoIndividus[self.case.IDindividu] = {}
        if (self.case.date in self.case.grid.dictConsoIndividus[self.case.IDindividu]) == False:
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date] = {}
        if (self.case.IDunite in self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date]) == False:
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite] = []

        listeConso = self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite]
        position = None
        index = 0
        for conso in listeConso:
            if self.conso == conso:
                position = index
            index += 1

        if position == None:
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite].append(self.conso)
        else:
            if self.conso.statut not in ("ajout", "suppression"):
                self.conso.statut = "modification"
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite][position] = self.conso

    def MAJ_facturation(self, action=None):
        self.case.MAJ_facturation(evenement=self, action=None)

    def GetCouleur(self):
        """ Retourn la couleur de fond du bouton """
        # Si une conso existe
        if self.conso != None :
            if self.conso.etat in ("reservation", "present", "absenti", "absentj"):
                return CTRL_Grille.COULEUR_RESERVATION
            if self.conso.etat == "attente":
                return CTRL_Grille.COULEUR_ATTENTE
            if self.conso.etat == "refus":
                return CTRL_Grille.COULEUR_REFUS

        # Recherche nbre places �v�nements
        dictPlacesEvenement = self.GetPlacesEvenement()
        if dictPlacesEvenement != None :
            if dictPlacesEvenement["nbrePlacesInitial"] != None:
                if dictPlacesEvenement["nbrePlacesRestantes"] == None or dictPlacesEvenement["nbrePlacesRestantes"] > 0 :
                    return CTRL_Grille.COULEUR_DISPONIBLE
                else :
                    return CTRL_Grille.COULEUR_COMPLET

        # Sinon on retourne la couleur de remplissage
        dictInfosPlaces = self.case.GetInfosPlaces()
        if dictInfosPlaces != None:
            nbrePlacesRestantes = None
            for IDunite_remplissage in self.case.grid.dictUnitesRemplissage[self.case.IDunite]:
                if (nbrePlacesRestantes == None or dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"] < nbrePlacesRestantes) and dictInfosPlaces[IDunite_remplissage]["nbrePlacesInitial"] not in (0, None):
                    nbrePlacesRestantes = dictInfosPlaces[IDunite_remplissage]["nbrePlacesRestantes"]
                    seuil_alerte = dictInfosPlaces[IDunite_remplissage]["seuil_alerte"]

            if nbrePlacesRestantes != None:
                if nbrePlacesRestantes > seuil_alerte: return CTRL_Grille.COULEUR_DISPONIBLE
                if nbrePlacesRestantes > 0 and nbrePlacesRestantes <= seuil_alerte: return CTRL_Grille.COULEUR_ALERTE
                if nbrePlacesRestantes <= 0: return CTRL_Grille.COULEUR_COMPLET

        # Si aucun remplissage, on retourne du blanc
        return wx.WHITE


    def GetPlacesEvenement(self):
        nbrePlacesRestantes, nbrePlacesPrises = None, None

        if self.capacite_max != None:
            if self.IDevenement in self.case.grid.dictRemplissageEvenements :
                nbrePlacesPrises = self.case.grid.dictRemplissageEvenements[self.IDevenement]["reservation"] + self.case.grid.dictRemplissageEvenements[self.IDevenement]["present"]
                nbrePlacesRestantes = self.capacite_max - nbrePlacesPrises

        if self.IDevenement in self.case.grid.dictRemplissageEvenements :
            nbrePlacesAttente = self.case.grid.dictRemplissageEvenements[self.IDevenement]["attente"]
        else :
            nbrePlacesAttente = 0

        return {"nbrePlacesPrises" : nbrePlacesPrises, "nbrePlacesInitial" : self.capacite_max, "nbrePlacesRestantes" : nbrePlacesRestantes, "nbreAttente" : nbrePlacesAttente}





class CaseEvenement(Case):
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDindividu=None, IDfamille=None, date=None, IDunite=None, IDactivite=None, verrouillage=0):
        Case.__init__(self, ligne, grid, numLigne, numColonne, IDindividu, IDfamille, date, IDunite, IDactivite, verrouillage)
        self.CategorieCase = "evenement"
        self.verrouillage = verrouillage

        # Cr�ation des �v�nements
        self.liste_evenements = self.CreationEvenements()

        # Dessin de la case
        self.renderer = CTRL_Grille_renderers.CaseEvenement(self)
        self.grid.SetCellValue(self.numLigne, self.numColonne, u"")
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

    def CreationEvenements(self):
        """ G�n�re les �v�nements """
        try :
            liste_donnees = self.grid.dictOuvertures[self.date][self.IDgroupe][self.IDunite]["liste_evenements"]
        except :
            liste_donnees = []
        liste_evenements = []
        for dict_evenement in liste_donnees :
            # Cr�ation de l'�v�nement
            evenement = Evenement(case=self, dict_evenement=dict_evenement)
            # Recherche si une conso associ�e est d�j� m�moris�e
            conso = self.RechercheConsoMemorisee(evenement)
            evenement.SetConso(conso)
            liste_evenements.append(evenement)
        return liste_evenements

    def RechercheConsoMemorisee(self, evenement=None):
        if self.IDindividu in self.grid.dictConsoIndividus:
            if self.date in self.grid.dictConsoIndividus[self.IDindividu]:
                if self.IDunite in self.grid.dictConsoIndividus[self.IDindividu][self.date]:
                    for conso in self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite]:
                        if conso.IDevenement == evenement.IDevenement :
                            return conso
        return None

    def GetListeConso(self):
        listeConso = []
        for evenement in self.liste_evenements :
            if evenement.conso != None :
                listeConso.append(evenement.conso)
        return listeConso

    def RechercheEvenement(self, x, y):
        """ Recherche un �v�nement � la position x, y """
        for evenement, rect in self.renderer.dict_boutons.items():
            rect = wx.Rect(rect.x + self.GetRect().x, rect.y + self.GetRect().y, rect.GetWidth(), rect.GetHeight())
            if 'phoenix' in wx.PlatformInfo:
                contains = rect.Contains(x, y)
            else :
                contains = rect.ContainsXY(x, y)
            if contains == True :
                return evenement
        return None

    def RechercheEvenementPositionSouris(self):
        """ Recherche un �v�nement � la position de la souris """
        x, y = self.grid.CalcUnscrolledPosition(self.grid.ScreenToClient(wx.GetMousePosition()))
        x = x - self.grid.GetRowLabelSize()
        y = y - self.grid.GetColLabelSize()
        return self.RechercheEvenement(x, y)

    def OnClick(self):
        evenement = self.RechercheEvenementPositionSouris()

        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        if evenement != None :

            # Recherche si des touches raccourcis sont enfonc�es
            if evenement.conso != None :
                if wx.GetKeyState(97) or wx.GetKeyState(112) or wx.GetKeyState(105) or wx.GetKeyState(106) or wx.GetKeyState(99) or wx.GetKeyState(115):
                    self.ToucheRaccourci(evenement)
                    return

            # Saisie d'une conso
            if evenement.conso == None :
                self.Ajouter_evenement(evenement)

            # Suppression d'une conso
            else :
                self.Supprimer_evenement(evenement)

    def Ajouter_evenement(self, evenement=None, modeSilencieux=False, TouchesRaccourciActives=True, etiquettes=None):
        """ Cr�ation d'une conso """
        mode = self.grid.GetGrandParent().panel_grille.GetMode()

        if self.grid.gestion.Verification("consommations", self.date) == False: return False

        # V�rifie d'abord qu'il n'y a aucune incompatibilit�s entre unit�s
        incompatibilite = self.VerifieCompatibilitesUnites()
        if incompatibilite != None:
            nomUniteCase = self.grid.dictUnites[self.IDunite]["nom"]
            nomUniteIncompatible = self.grid.dictUnites[incompatibilite]["nom"]
            dlg = wx.MessageDialog(self.grid, _(u"L'unit� %s est incompatible avec l'unit� %s d�j� s�lectionn�e !") % (nomUniteCase, nomUniteIncompatible), _(u"Incompatibilit�s d'unit�s"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie qu'il y a de la place
        if mode == "reservation":
            if self.grid.blocageSiComplet == True and self.HasPlaceDisponible(evenement) == False:
                if modeSilencieux == True:
                    return False
                dlg = wx.MessageDialog(None, _(u"Il n'y a plus de places disponibles sur cet �v�nement.\n\nSouhaitez-vous quand m�me saisir une consommation ?"), _(u"Complet !"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse != wx.ID_YES:
                    return

        # Touches de raccourci
        if TouchesRaccourciActives == True:
            self.OnTouchesRaccourcisPerso()

        # Cr�ation d'une conso
        conso = CTRL_Grille.Conso()
        conso.IDconso = None
        conso.IDactivite = self.IDactivite
        conso.IDinscription = self.dictInfosInscriptions["IDinscription"]
        conso.IDgroupe = self.IDgroupe
        conso.heure_debut = UTILS_Dates.DatetimeTimeEnStr(evenement.heure_debut, ":")
        conso.heure_fin = UTILS_Dates.DatetimeTimeEnStr(evenement.heure_fin, ":")

        # Mode de saisie
        conso.etat = mode

        # R�cup�ration des �tiquettes
        if etiquettes != None:
            conso.etiquettes = etiquettes
        else:
            conso.etiquettes = self.grid.GetGrandParent().panel_etiquettes.GetCoches(self.IDactivite)

        # Autres param�tres
        conso.verrouillage = 0
        conso.IDfamille = self.IDfamille
        conso.IDcompte_payeur = self.dictInfosInscriptions["IDcompte_payeur"]
        conso.date_saisie = datetime.date.today()
        conso.IDutilisateur = self.grid.IDutilisateur
        conso.IDcategorie_tarif = self.dictInfosInscriptions["IDcategorie_tarif"]
        conso.IDprestation = None
        conso.forfait = None
        conso.quantite = None
        conso.statut = "ajout"
        conso.IDunite = self.IDunite

        if self.IDactivite in self.grid.dictInfosInscriptions[self.IDindividu]:
            if self.grid.mode == "individu":
                IDgroupe = self.grid.GetGrandParent().panel_activites.ctrl_activites.GetIDgroupe(self.IDactivite, self.IDindividu)
                if IDgroupe:
                    conso.IDgroupe = IDgroupe
            if self.IDgroupe == None:
                conso.IDgroupe = self.grid.dictInfosInscriptions[self.IDindividu][self.IDactivite]["IDgroupe"]
        else:
            conso.IDgroupe = None

        self.grid.memoireHoraires[self.IDunite] = {"heure_debut": conso.heure_debut, "heure_fin": conso.heure_fin}

        # Associe la conso � l'�v�nement
        evenement.SetConso(conso)
        evenement.MemoriseValeurs()
        self.Refresh()

        # MAJ remplissage
        self.MAJremplissage()

        # Facturation
        self.MAJ_facturation(evenement=evenement, action="saisie")

        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Ajout d'une consommation �v�nement")))

        # Autog�n�ration
        self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

    def Supprimer_evenement(self, evenement=None, TouchesRaccourciActives=True):
        # Protections anti modification et suppression
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False: return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False

        if self.ProtectionsModifSuppr(evenement.conso) == False:
            return

        # Suppression d'un forfait supprimable
        if evenement.conso.etat != None and evenement.conso.forfait == 1:
            # Demande la confirmation de la suppression du forfait
            dlg = wx.MessageDialog(self.grid, _(u"Cette consommation fait partie d'un forfait supprimable.\n\nSouhaitez-vous supprimer le forfait et toutes les consommations rattach�es ?"), _(u"Suppression"), wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES:
                self.SupprimeForfaitDate(evenement.conso.IDprestation)
            return

        if evenement.conso.etat != None and evenement.conso.forfait == 2:
            print("forfait 2")
            return

        # Suppression
        evenement.conso.etat = None
        if evenement.conso.IDconso != None:
            evenement.conso.statut = "suppression"
            self.grid.listeConsoSupprimees.append(evenement.conso)
        if evenement.conso.IDconso == None:
            evenement.conso.statut = "suppression"

        # Touches de raccourci
        if TouchesRaccourciActives == True:
            self.OnTouchesRaccourcisPerso()

        self.MAJ_facturation(evenement=evenement, action="suppression")
        self.grid.dictConsoIndividus[self.IDindividu][self.date][self.IDunite].remove(evenement.conso)
        evenement.conso = None
        self.MAJremplissage()
        self.Refresh()
        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Suppression d'une consommation �v�nement")))

        # Autog�n�ration
        self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)

    def IsCaseDisponible(self, evenement=None):
        if evenement.conso != None:
            return False
        else :
            return True

    def HasPlaceDisponible(self, evenement=None):
        """ Regarde si place disponible selon le remplissage """
        if evenement and evenement.GetCouleur() == CTRL_Grille.COULEUR_COMPLET :
            return False
        return True

    def Ajouter(self, event=None):
        """ Modifier la consommation s�lectionn�e """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "creer", IDactivite=self.IDactivite) == False: return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False
        self.Ajouter_evenement(self.evenementContextMenu)

    def Modifier(self, event=None):
        """ Modifier la consommation s�lectionn�e """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False : return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False
        # Todo : Modifier evenement
        # self.ModifierBarre(self.barreContextMenu)

    def Supprimer(self, event=None):
        """ Supprimer la consommation s�lectionn�e """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False: return
        if self.grid.gestion.Verification("consommations", self.date) == False: return False
        self.Supprimer_evenement(self.evenementContextMenu)


    def ToucheRaccourci(self, evenement):
        """ Applique une touche raccourci � un �v�nement """
        if wx.GetKeyState(97) == True:  # Touche "a" pour Pointage en attente...
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False: return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if evenement.conso.etat in ("present", "absenti", "absentj"):
                self.ModifieEtat(evenement.conso, "reservation")

        if wx.GetKeyState(112) == True:  # Touche "p" pour Pr�sent
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False: return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if evenement.conso.etat in ("reservation", "absenti", "absentj"):
                self.ModifieEtat(evenement.conso, "present")

        if wx.GetKeyState(105) == True:  # Touche "i" pour Absence injustif�e
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False: return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if evenement.conso.etat in ("reservation", "present", "absentj"):
                self.ModifieEtat(evenement.conso, "absenti")

        if wx.GetKeyState(106) == True:  # Touche "j" pour Absence justifi�e
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier", IDactivite=self.IDactivite) == False: return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            if evenement.conso.etat in ("reservation", "present", "absenti"):
                self.ModifieEtat(evenement.conso, "absentj")

        if wx.GetKeyState(115) == True:  # Suppression de la conso
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "supprimer", IDactivite=self.IDactivite) == False: return
            if self.grid.gestion.Verification("consommations", self.date) == False: return False
            self.Supprimer(evenement)

    def ModifieEtat(self, conso=None, etat="reservation"):
        ancienEtat = conso.etat

        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        # V�rifie si prestation correspondante d�j� factur�e
        if conso.IDprestation in self.grid.dictPrestations:
            prestation = self.grid.dictPrestations[conso.IDprestation]
            if prestation["IDfacture"] and not prestation["forfait_date_debut"]:
                changementPossible = True
                if etat in ("reservation", "present", "absenti") and ancienEtat in ("attente", "refus", "absentj"):
                    changementPossible = False
                if etat in (None, "attente", "refus", "absentj") and ancienEtat in ("reservation", "present", "absenti"):
                    changementPossible = False
                if changementPossible == False:
                    dlg = wx.MessageDialog(self.grid, _(u"La prestation correspondant � cette consommation appara�t d�j� sur une facture.\n\nIl est donc impossible de la modifier ou de la supprimer."), _(u"Consommation verrouill�e"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        conso.etat = etat
        conso.evenement.MemoriseValeurs()

        if conso.forfait == 0 or conso.forfait == None:
            if etat in ("reservation", "present", "absenti") and ancienEtat in ("attente", "refus", "absentj"):
                self.MAJ_facturation(evenement=conso.evenement, action="modification_etat")
            if etat in ("attente", "refus", "absentj") and ancienEtat in ("reservation", "present", "absenti"):
                self.MAJ_facturation(evenement=conso.evenement, action="modification_etat")

        conso.evenement.Refresh()
        self.MAJremplissage()
        self.grid.listeHistorique.append((self.IDindividu, self.date, self.IDunite, _(u"Modification de l'�tat d'une consommation �v�nement")))

    def OnContextMenu(self):
        evenement = self.RechercheEvenementPositionSouris()
        if evenement != None:
            self.evenementContextMenu = evenement
            return self.ContextMenu(evenement.conso)
        else:
            return False

    def SelectionnerEtiquettes(self, event):
        # V�rifie la p�riode de gestion
        if self.grid.gestion.Verification("consommations", self.date) == False : return False

        evenement = self.evenementContextMenu
        listeCoches = evenement.conso.etiquettes
        from Ctrl import CTRL_Etiquettes
        dlg = CTRL_Etiquettes.DialogSelection(self.grid, listeActivites=[self.IDactivite, ])
        dlg.SetCoches(listeCoches)
        if dlg.ShowModal() == wx.ID_OK:
            listeCoches = dlg.GetCoches()
            evenement.conso.etiquettes = listeCoches
            evenement.MemoriseValeurs()
            if evenement.conso.IDconso != None:
                evenement.conso.statut = "modification"
            self.MAJ_facturation(action="modification")
            evenement.Refresh()
            self.MAJremplissage()
        dlg.Destroy()

    def SetEtat(self, event):
        evenement = self.evenementContextMenu
        ID = event.GetId()
        if ID == 30 or ID == 60:
            self.ModifieEtat(evenement.conso, "reservation")
        if ID == 40:
            self.ModifieEtat(evenement.conso, "attente")
        if ID == 50:
            self.ModifieEtat(evenement.conso, "refus")
        if ID == 70:
            self.ModifieEtat(evenement.conso, "present")
        if ID == 80:
            self.ModifieEtat(evenement.conso, "absentj")
        if ID == 90:
            self.ModifieEtat(evenement.conso, "absenti")

    def Verrouillage(self, event):
        pass


    def Deverrouillage(self, event):
        pass

    def DLG_detail(self, event):
        evenement = self.evenementContextMenu
        from Dlg import DLG_Detail_conso
        texteInfoBulle = self.GetTexteInfobulleConso(evenement.conso)
        dlg = DLG_Detail_conso.Dialog(self.grid, evenement.conso, texteInfoBulle)
        if dlg.ShowModal() == wx.ID_OK:
            evenement.conso.IDgroupe = dlg.GetIDgroupe()
            evenement.conso.heure_debut = dlg.GetHeureDebut()
            evenement.conso.heure_fin = dlg.GetHeureFin()
            evenement.MemoriseValeurs()
            if evenement.conso.IDconso != None:
                evenement.conso.statut = "modification"
                evenement.Refresh()
            self.MAJremplissage()
            self.grid.Autogeneration(ligne=self.ligne, IDactivite=self.IDactivite, IDunite=self.IDunite)
        dlg.Destroy()

    def GetStatutTexte(self, x=None, y=None):
        return None














if __name__ == '__main__':
    app = wx.App(0)
    from Dlg import DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=791, selectionIndividus=[2187,])
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
