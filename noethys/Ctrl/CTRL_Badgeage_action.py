#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime

import GestionDB
import wx.combo
import CTRL_Saisie_heure


DICT_LABELS_ACTIONS = {
    "enregistrer" : _(u"Enregistrer une consommation"),
    "reserver" : _(u"Réserver des consommations"),
    "message" : _(u"Afficher des messages"),
    }


def GetDetailAction(dictDonnees):
    """ Crée un texte de détail de l'action pour l'OL_Badgeage_actions """
    texte = u""
    action = dictDonnees["action"]
    
    # Enregistrer
    if action == "enregistrer" :
        IDunite = int(dictDonnees["action_unite"])
        db = GestionDB.DB()
        req = """SELECT unites.nom, activites.nom
        FROM unites
        LEFT JOIN activites ON unites.IDactivite = activites.IDactivite
        WHERE IDunite=%d;""" % IDunite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        nomUnite, nomActivite = listeDonnees[0]
        texte = u"%s (%s)" % (nomUnite, nomActivite)
        
    # Réserver
    if action == "reserver" :
        listeUnites = []
        for IDunite in dictDonnees["action_unite"].split(";") :
            listeUnites.append(int(IDunite))
        if len(listeUnites) == 0 : conditionActivites = "()"
        elif len(listeUnites) == 1 : conditionActivites = "(%d)" % listeUnites[0]
        else : conditionActivites = str(tuple(listeUnites))
        db = GestionDB.DB()
        req = """SELECT unites.nom, activites.nom
        FROM unites
        LEFT JOIN activites ON unites.IDactivite = activites.IDactivite
        WHERE IDunite IN %s;""" % conditionActivites
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeUnites = []
        for IDunite, nomActivite in listeDonnees :
            listeUnites.append(IDunite)
        texte = u"%s (%s)" % (", ".join(listeUnites), nomActivite)

    # Message
    if action == "message" :
        # Message unique
        if dictDonnees["action_message"] != None :
            texte = _(u"1 message unique : '%s'") % dictDonnees["action_message"]
        else :
            listeMessages = [] 
            for IDmessage, message in dictDonnees["action_messages"] :
                listeMessages.append("'%s'" % message)
            if len(listeMessages) == 1 :
                texte = _(u"1 message aléatoire : %s") % listeMessages[0]
            else :
                texte = _(u"%d messages aléatoires : %s") % (len(listeMessages), ", ".join(listeMessages))
        
    return texte


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))




# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Icone(wx.combo.BitmapComboBox):
    def __init__(self, parent, size=(-1,  -1)):
        wx.combo.BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        self.parent = parent
        
        # MAJ
        self.listeIcones = [
            ("commentaire", _(u"Commentaire"), "Images/Badgeage/Commentaire_24x24.png"),
            ("information", _(u"Information"), "Images/Badgeage/Information_24x24.png"),
            ("exclamation", _(u"Exclamation"), "Images/Badgeage/Exclamation_24x24.png"),
            ("question", _(u"Question"), "Images/Badgeage/Question_24x24.png"),
            ("erreur", _(u"Erreur"), "Images/Badgeage/Erreur_24x24.png"),
        ]
        for code, label, image in self.listeIcones :
            self.Append(label, wx.Bitmap(Chemins.GetStaticPath(image), wx.BITMAP_TYPE_ANY), code)
        self.SetSelection(0)
    
    def SetID(self, code=""):
        index = 0
        for codeTemp, label, image in self.listeIcones :            
            if code == codeTemp :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.GetClientData(index)


# ---------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Liste_messages(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.listeValeurs = []
    
    def SetValeur(self, valeur=None):
        if valeur == None :
            return
        self.listeValeurs = valeur
        self.MAJ() 
        
    def GetValeur(self):
        return self.listeValeurs
    
    def MAJ(self):
        self.listeValeurs.sort()
        listeLabels = []
        for IDmessage, message in self.listeValeurs :
            listeLabels.append(message)
        self.Set(listeLabels)
    
    def Ajouter(self):
        dlg = wx.TextEntryDialog(self, _(u"Saisissez un message :"), _(u"Saisie"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le message que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                self.listeValeurs.append((None, nom))
                self.MAJ()
        dlg.Destroy()
        
    def Modifier(self):
        valeur = self.GetStringSelection()
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le message :"), _(u"Modification"), valeur)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le message que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                self.listeValeurs[index] = (self.listeValeurs[index][0], nom)
                self.MAJ()
        dlg.Destroy()

    def Supprimer(self):
        valeur = self.GetStringSelection()
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce message ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
                self.listeValeurs.pop(index)
                self.MAJ()
        dlg.Destroy()

        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Message(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent

        self.label_messages = wx.StaticText(self, -1, _(u"Messages :"))
        
        self.radio_unique = wx.RadioButton(self, -1, _(u"Message unique :"), style=wx.RB_GROUP)
        self.ctrl_unique = wx.TextCtrl(self, -1, "")
        
        self.radio_aleatoires = wx.RadioButton(self, -1, _(u"Messages aléatoires :"))
        self.ctrl_aleatoires = CTRL_Liste_messages(self)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        self.label_icone = wx.StaticText(self, -1, _(u"Icône :"))
        self.ctrl_icone = CTRL_Icone(self)

        self.label_duree = wx.StaticText(self, -1, _(u"Durée :"))
        self.ctrl_duree = wx.SpinCtrl(self, -1, "", min=1, max=60, initial=2, size=(80, -1))
        
        self.label_frequence = wx.StaticText(self, -1, _(u"Fréquence :"))
        self.label_pourcentage = wx.StaticText(self, -1, u"100 %")
        
        self.label_pourcentage.SetMinSize((40, -1))
        self.ctrl_frequence = wx.Slider(self, -1, 100, 1, 100, size=(-1, 28), style=wx.SL_HORIZONTAL)
        self.label_audio = wx.StaticText(self, -1, _(u"Audio :"))
        self.ctrl_vocal = wx.CheckBox(self, -1, _(u"Activer la synthèse vocale"))
        
        self.label_audio.Show(False)
        self.ctrl_vocal.Show(False)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.OnChoixFrequence, self.ctrl_frequence)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMessage, self.radio_unique)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMessage, self.radio_aleatoires)
        
        # Init
        self.OnChoixMessage(None)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un message"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le message sélectionné"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le message sélectionné"))
        self.ctrl_icone.SetToolTipString(_(u"Sélectionnez l'icône à afficher dans la boîte de dialogue"))
        self.ctrl_duree.SetToolTipString(_(u"Sélectionnez la durée d'affichage du message (en secondes)"))
        self.ctrl_frequence.SetToolTipString(_(u"Sélectionnez la fréquence de diffusion (en %)"))
        self.ctrl_vocal.SetToolTipString(_(u"Cochez cette case pour activer la synthèse vocale"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=2, vgap=5, hgap=5)
        
        # Messages
        grid_sizer_base.Add(self.label_messages, 0, wx.LEFT|wx.TOP|wx.ALIGN_RIGHT, 10)
        
        grid_sizer_messages = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        
        grid_sizer_messages.Add(self.radio_unique, 0, wx.EXPAND, 0)
        grid_sizer_messages.Add(self.ctrl_unique, 0, wx.EXPAND|wx.LEFT, 20)
        
        grid_sizer_messages.Add(self.radio_aleatoires, 0, wx.EXPAND, 0)
        
        grid_sizer_aleatoires = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_aleatoires.Add(self.ctrl_aleatoires, 0, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_aleatoires.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_aleatoires.AddGrowableRow(0)
        grid_sizer_aleatoires.AddGrowableCol(0)
        grid_sizer_messages.Add(grid_sizer_aleatoires, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 20)

        grid_sizer_messages.AddGrowableRow(3)
        grid_sizer_messages.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_messages, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Icone
        grid_sizer_base.Add(self.label_icone, 0, wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_base.Add(self.ctrl_icone, 0, wx.RIGHT, 10)

        # Durée
        grid_sizer_base.Add(self.label_duree, 0, wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_base.Add(self.ctrl_duree, 0, wx.RIGHT, 10)

        # Fréquence
        grid_sizer_base.Add(self.label_frequence, 0, wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        
        grid_sizer_frequence = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=2)
        grid_sizer_frequence.Add(self.label_pourcentage, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_frequence.Add(self.ctrl_frequence, 0, wx.EXPAND|wx.RIGHT, 20)
        grid_sizer_frequence.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_frequence, 0, wx.RIGHT|wx.EXPAND, 10)
        
        # Vocal
        grid_sizer_base.Add(self.label_audio, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_base.Add(self.ctrl_vocal, 0, wx.RIGHT|wx.BOTTOM, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
    
    def OnChoixMessage(self, event):
        self.ctrl_unique.Enable(self.radio_unique.GetValue())
        self.ctrl_aleatoires.Enable(self.radio_aleatoires.GetValue())
        self.bouton_ajouter.Enable(self.radio_aleatoires.GetValue())
        self.bouton_modifier.Enable(self.radio_aleatoires.GetValue())
        self.bouton_supprimer.Enable(self.radio_aleatoires.GetValue())
        
    def OnChoixFrequence(self, event): 
        valeur = self.ctrl_frequence.GetValue() 
        self.label_pourcentage.SetLabel(u"%d %%" % valeur)

    def OnBoutonAjouter(self, event): 
        self.ctrl_aleatoires.Ajouter()

    def OnBoutonModifier(self, event): 
        self.ctrl_aleatoires.Modifier()

    def OnBoutonSupprimer(self, event): 
        self.ctrl_aleatoires.Supprimer()

    def Validation(self):
        if self.radio_aleatoires.GetValue() == True :
            if len(self.ctrl_aleatoires.GetValeur()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins un message !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        if self.radio_unique.GetValue() == True :
            if len(self.ctrl_unique.GetValue()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un message !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
        return True

    def SetValeur(self, valeur=None):
        # Valeur = None ou valeur = dict{"activite":"12...}
        if valeur == None :
            return
        # Message unique
        if valeur["message"] != None :
            self.ctrl_unique.SetValue(valeur["message"])
            self.radio_unique.SetValue(True)
        # Messages aleatoires
        if len(valeur["messages"]) > 0 :
            self.ctrl_aleatoires.SetValeur(valeur["messages"])
            self.radio_aleatoires.SetValue(True)
        # Icone
        self.ctrl_icone.SetID(valeur["icone"])
        # Durée
        if valeur["duree"] != None :
            self.ctrl_duree.SetValue(int(valeur["duree"]))
        # Fréquence
        self.ctrl_frequence.SetValue(int(valeur["frequence"]))
        self.OnChoixFrequence(None)
        # Vocal
        self.ctrl_vocal.SetValue(int(valeur["vocal"]))
        self.OnChoixMessage(None)
        
    def GetValeur(self):
        dictValeurs = {}
        # Message unique
        dictValeurs["message"] = None
        if self.radio_unique.GetValue() == True :
            dictValeurs["message"] = self.ctrl_unique.GetValue()
        # Messages aleatoires
        dictValeurs["messages"] = []
        if self.radio_aleatoires.GetValue() == True :
            dictValeurs["messages"] = self.ctrl_aleatoires.GetValeur()
        # Icone
        dictValeurs["icone"] = self.ctrl_icone.GetID()
        # Durée
        dictValeurs["duree"] = str(self.ctrl_duree.GetValue())
        # Fréquence
        dictValeurs["frequence"] = str(self.ctrl_frequence.GetValue())
        # Vocal
        dictValeurs["vocal"] = int(self.ctrl_vocal.GetValue())
        # Renvoie
        return dictValeurs

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Choix_activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY date_fin DESC;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDactivite, nom in listeDonnees :
            if nom == None : nom = _(u"Activité inconnue")
            self.dictDonnees[index] = { "ID" : IDactivite, "nom " : nom}
            listeItems.append(nom)
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


class CTRL_Choix_unite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, IDactivite=None):
        listeItems = self.GetListeDonnees(IDactivite)
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self, IDactivite=None):
        listeItems = []
        if IDactivite == None :
            return listeItems
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, type
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.dictDonnees = {}
        index = 0
        for IDunite, nom, type in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDunite, "nom " : nom}
            listeItems.append(nom)
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



class CTRL_Choix_etat(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.listeEtats = [
            #(None, _(u"Ne pas modifier")),
            ("reservation", _(u"Pointage en attente")),
            ("present", _(u"Présence")),
            ("absentj", _(u"Absence justifiée")),
            ("absenti", _(u"Absence injustifiée")),
            ]
        self.MAJ() 
    
    def MAJ(self):
        listeItems = []
        for code, label in self.listeEtats :
            listeItems.append(label)
        self.SetItems(listeItems)
        self.Select(0)
                                        
    def SetValeur(self, valeur=None):
        index = 0
        for code, label in self.listeEtats :
            if code == valeur :
                 self.SetSelection(index)
            index += 1

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]



class CTRL_Choix_ticket(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        listeItems = []
        db = GestionDB.DB()
        req = """SELECT IDmodele, nom
        FROM modeles_tickets
        WHERE categorie='badgeage_enregistrer';"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.dictDonnees = {}
        index = 0
        for IDmodele, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDmodele, "nom " : nom}
            listeItems.append(nom)
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



class CTRL_Enregistrer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        # Unité
        self.box_unite_staticbox = wx.StaticBox(self, -1, _(u"Unité de consommation"))
        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = CTRL_Choix_activite(self)
        self.label_unite = wx.StaticText(self, -1, _(u"Unité :"))
        self.ctrl_unite = CTRL_Choix_unite(self)
        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"))
        self.ctrl_etat = CTRL_Choix_etat(self)

        # Demander
        self.check_demander = wx.CheckBox(self, -1, _(u"Demander s'il s'agit du début ou de la fin"))

        # Début
        self.box_debut_staticbox = wx.StaticBox(self, -1, _(u"Heure de début"))
        self.radio_debut_defaut = wx.RadioButton(self, -1, _(u"Heure par défaut"), style=wx.RB_GROUP)
        self.radio_debut_pointee = wx.RadioButton(self, -1, _(u"Heure du badgeage"))
        self.radio_debut_autre = wx.RadioButton(self, -1, _(u"Autre heure :"))
        self.ctrl_debut_autre = CTRL_Saisie_heure.Heure(self)

        # Fin
        self.box_fin_staticbox = wx.StaticBox(self, -1, _(u"Heure de fin"))
        self.radio_fin_defaut = wx.RadioButton(self, -1, _(u"Heure par défaut"), style=wx.RB_GROUP)
        self.radio_fin_pointee = wx.RadioButton(self, -1, _(u"Heure du badgeage"))
        self.radio_fin_autre = wx.RadioButton(self, -1, _(u"Autre heure :"))
        self.ctrl_fin_autre = CTRL_Saisie_heure.Heure(self)
        
        # Message de confirmation
        self.box_message_staticbox = wx.StaticBox(self, -1, _(u"Message de confirmation"))
        self.label_message_actif = wx.StaticText(self, -1, _(u"Activé :"))
        self.check_message_actif = wx.CheckBox(self, -1, u"")
        self.label_message_texte = wx.StaticText(self, -1, _(u"Texte :"))
        self.ctrl_message_texte = wx.TextCtrl(self, -1, u"")
        self.label_audio = wx.StaticText(self, -1, _(u"Audio :"))
        self.ctrl_vocal = wx.CheckBox(self, -1, _(u"Activer la synthèse vocale"))

        # Impression de ticket
        self.box_ticket_staticbox = wx.StaticBox(self, -1, _(u"Impression d'un ticket"))
        self.label_ticket_actif = wx.StaticText(self, -1, _(u"Activé :"))
        self.check_ticket_actif = wx.CheckBox(self, -1, u"")
        self.label_ticket_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_ticket_modele = CTRL_Choix_ticket(self)

        self.label_audio.Show(False)
        self.ctrl_vocal.Show(False)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDemander, self.check_demander)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckMessage, self.check_message_actif)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckTicket, self.check_ticket_actif)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixDebut, self.radio_debut_defaut)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixDebut, self.radio_debut_pointee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixDebut, self.radio_debut_autre)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixFin, self.radio_fin_defaut)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixFin, self.radio_fin_pointee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixFin, self.radio_fin_autre)
        
        # Init
        self.OnChoixActivite(None)
        self.OnChoixDebut(None)
        self.OnChoixFin(None)
        self.OnCheckDemander(None)
        self.OnCheckMessage(None)
        self.OnCheckTicket(None)

    def __set_properties(self):
        self.ctrl_activite.SetToolTipString(_(u"Sélectionnez une activité"))
        self.ctrl_unite.SetToolTipString(_(u"Sélectionnez une unité de consommation"))
        self.ctrl_etat.SetToolTipString(_(u"Sélectionnez un état"))
        self.check_demander.SetToolTipString(_(u"Cochez cette case pour que Noethys demande s'il s'agit du début ou de la fin de la consommation. Utile quand l'unité de consommation n'a pas d'heure fixe de début ou de fin (ex : crèche, accueil de loisirs)"))
        self.radio_debut_defaut.SetToolTipString(_(u"Heure par défaut définie dans le paramétrage de l'unité"))
        self.radio_debut_pointee.SetToolTipString(_(u"Heure pointée"))
        self.radio_debut_autre.SetToolTipString(_(u"Autre heure"))
        self.ctrl_debut_autre.SetToolTipString(_(u"Saisissez une heure"))
        self.radio_fin_defaut.SetToolTipString(_(u"Heure par défaut définie dans le paramétrage de l'unité"))
        self.radio_fin_pointee.SetToolTipString(_(u"Heure pointée"))
        self.radio_fin_autre.SetToolTipString(_(u"Autre heure"))
        self.ctrl_fin_autre.SetToolTipString(_(u"Saisissez une heure"))
        self.check_message_actif.SetToolTipString(_(u"Cochez cette case pour activer l'affichage d'un message de confirmation"))
        self.ctrl_message_texte.SetToolTipString(_(u"Saisissez un message de confirmation"))
        self.ctrl_vocal.SetToolTipString(_(u"Cochez cette case pour activer la synthèse vocale"))
        self.check_ticket_actif.SetToolTipString(_(u"Cochez cette case pour activer l'impression d'un ticket"))
        self.ctrl_ticket_modele.SetToolTipString(_(u"Sélectionnez le modèle de ticket à utiliser"))
        self.ctrl_debut_autre.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        self.ctrl_fin_autre.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        # Unité
        box_unite = wx.StaticBoxSizer(self.box_unite_staticbox, wx.VERTICAL)
        grid_sizer_unite = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_unite.Add(self.label_activite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.ctrl_activite, 0, wx.EXPAND, 0)
        grid_sizer_unite.Add(self.label_unite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.ctrl_unite, 0, wx.EXPAND, 0)
        grid_sizer_unite.Add(self.label_etat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.ctrl_etat, 0, 0, 0)
        grid_sizer_unite.AddGrowableCol(1)
        box_unite.Add(grid_sizer_unite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_unite, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Demander
        grid_sizer_base.Add(self.check_demander, 0, wx.ALL, 10)
        
        grid_sizer_heures = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Début
        box_debut = wx.StaticBoxSizer(self.box_debut_staticbox, wx.VERTICAL)
        grid_sizer_debut = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_debut.Add(self.radio_debut_defaut, 0, 0, 0)
        grid_sizer_debut.Add(self.radio_debut_pointee, 0, 0, 0)
        grid_sizer_debut_autre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_debut_autre.Add(self.radio_debut_autre, 0, 0, 0)
        grid_sizer_debut_autre.Add(self.ctrl_debut_autre, 0, 0, 0)
        grid_sizer_debut.Add(grid_sizer_debut_autre, 1, wx.EXPAND, 0)
        box_debut.Add(grid_sizer_debut, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_heures.Add(box_debut, 1, wx.EXPAND, 0)
        
        # Fin
        box_fin = wx.StaticBoxSizer(self.box_fin_staticbox, wx.VERTICAL)
        grid_sizer_fin = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_fin.Add(self.radio_fin_defaut, 0, 0, 0)
        grid_sizer_fin.Add(self.radio_fin_pointee, 0, 0, 0)
        grid_sizer_fin_autre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_fin_autre.Add(self.radio_fin_autre, 0, 0, 0)
        grid_sizer_fin_autre.Add(self.ctrl_fin_autre, 0, 0, 0)
        grid_sizer_fin.Add(grid_sizer_fin_autre, 1, wx.EXPAND, 0)
        box_fin.Add(grid_sizer_fin, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_heures.Add(box_fin, 1, wx.EXPAND, 0)
        
        grid_sizer_heures.AddGrowableCol(0)
        grid_sizer_heures.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_heures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Message de confirmation
        box_message = wx.StaticBoxSizer(self.box_message_staticbox, wx.VERTICAL)
        grid_sizer_message = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_message.Add(self.label_message_actif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_message.Add(self.check_message_actif, 0, 0, 0)
        grid_sizer_message.Add(self.label_message_texte, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_message.Add(self.ctrl_message_texte, 0, wx.EXPAND, 0)
        grid_sizer_message.Add(self.label_audio, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_message.Add(self.ctrl_vocal, 0, 0, 0)
        grid_sizer_message.AddGrowableCol(1)
        box_message.Add(grid_sizer_message, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_message, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Impression de ticket
        box_ticket = wx.StaticBoxSizer(self.box_ticket_staticbox, wx.VERTICAL)
        grid_sizer_ticket = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_ticket.Add(self.label_ticket_actif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ticket.Add(self.check_ticket_actif, 0, 0, 0)
        grid_sizer_ticket.Add(self.label_ticket_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ticket.Add(self.ctrl_ticket_modele, 0, wx.EXPAND, 0)
        grid_sizer_ticket.AddGrowableCol(1)
        box_ticket.Add(grid_sizer_ticket, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_ticket, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)


        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activite.GetID()
        self.ctrl_unite.MAJ(IDactivite)

    def OnCheckDemander(self, event): 
        etat = self.check_demander.GetValue()
        if etat == True :
            self.box_debut_staticbox.SetLabel(_(u"Heure de début par défaut"))
            self.box_fin_staticbox.SetLabel(_(u"Heure de fin par défaut"))
        else :
            self.box_debut_staticbox.SetLabel(_(u"Heure de début "))
            self.box_fin_staticbox.SetLabel(_(u"Heure de fin"))
            
        self.radio_debut_pointee.Enable(not etat)
        if etat == True and self.radio_debut_pointee.GetValue() == True :
            self.radio_debut_defaut.SetValue(True)
        self.radio_fin_pointee.Enable(not etat)
        if etat == True and self.radio_fin_pointee.GetValue() == True :
            self.radio_fin_defaut.SetValue(True)

    def OnChoixDebut(self, event): 
        self.ctrl_debut_autre.Enable(self.radio_debut_autre.GetValue())

    def OnChoixFin(self, event): 
        self.ctrl_fin_autre.Enable(self.radio_fin_autre.GetValue())
    
    def OnCheckMessage(self, event):
        self.ctrl_message_texte.Enable(self.check_message_actif.GetValue())
        self.ctrl_vocal.Enable(self.check_message_actif.GetValue())

    def OnCheckTicket(self, event):
        self.ctrl_ticket_modele.Enable(self.check_ticket_actif.GetValue())

    def Validation(self):
        if self.ctrl_activite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        if self.ctrl_unite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une unité de consommation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.radio_debut_autre.GetValue() == True and self.ctrl_debut_autre.GetHeure() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_debut_autre.SetFocus()
            return False

        if self.radio_fin_autre.GetValue() == True and self.ctrl_fin_autre.GetHeure() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_fin_autre.SetFocus()
            return False

        if self.check_message_actif.GetValue() and len(self.ctrl_message_texte.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun texte de confirmation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_message_texte.SetFocus()
            return False

        if self.check_ticket_actif.GetValue() and self.ctrl_ticket_modele.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun modèle de ticket dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_ticket_modele.SetFocus()
            return False

        return True

    def SetValeur(self, valeur=None):
        # Valeur = None ou valeur = dict{"activite":"12...}
        if valeur == None :
            return
        # Activité
        self.ctrl_activite.SetID(int(valeur["activite"]))
        self.OnChoixActivite(None)
        # Unité
        self.ctrl_unite.SetID(int(valeur["unite"]))
        # Etat
        self.ctrl_etat.SetValeur(valeur["etat"])
        # Demande
        self.check_demander.SetValue(int(valeur["demande"]))
        self.OnCheckDemander(None)
        # Heure debut
        if valeur["heure_debut"] == "defaut" : 
            self.radio_debut_defaut.SetValue(True)
        elif valeur["heure_debut"] == "pointee" : 
            self.radio_debut_pointee.SetValue(True)
        else : 
            self.radio_debut_autre.SetValue(True)
            self.ctrl_debut_autre.SetHeure(valeur["heure_debut"])
        self.OnChoixDebut(None)
        # Heure fin
        if valeur["heure_fin"] == "defaut" : 
            self.radio_fin_defaut.SetValue(True)
        elif valeur["heure_fin"] == "pointee" : 
            self.radio_fin_pointee.SetValue(True)
        else : 
            self.radio_fin_autre.SetValue(True)
            self.ctrl_fin_autre.SetHeure(valeur["heure_fin"])
        self.OnChoixFin(None)
        # Message de confirmation
        if valeur["message"] != None : 
            self.check_message_actif.SetValue(True) 
            self.ctrl_message_texte.SetValue(valeur["message"])
            self.ctrl_vocal.SetValue(int(valeur["vocal"]))
        # Ticket
        if valeur["ticket"] != None : 
            self.check_ticket_actif.SetValue(True) 
            self.ctrl_ticket_modele.SetID(int(valeur["ticket"]))
            
        self.OnCheckMessage(None)
        self.OnCheckTicket(None)
        
    def GetValeur(self):
        dictValeurs = {}
        # Activité
        dictValeurs["activite"] = str(self.ctrl_activite.GetID())
        # Unité
        dictValeurs["unite"] = str(self.ctrl_unite.GetID())
        # Etat
        dictValeurs["etat"] = self.ctrl_etat.GetValeur()
        # Demande
        dictValeurs["demande"] = str(int(self.check_demander.GetValue()))
        # Heure debut
        if self.radio_debut_defaut.GetValue() == True : dictValeurs["heure_debut"] = "defaut"
        if self.radio_debut_pointee.GetValue() == True : dictValeurs["heure_debut"] = "pointee"
        if self.radio_debut_autre.GetValue() == True : dictValeurs["heure_debut"] = str(self.ctrl_debut_autre.GetHeure())
        # Heure fin
        if self.radio_fin_defaut.GetValue() == True : dictValeurs["heure_fin"] = "defaut"
        if self.radio_fin_pointee.GetValue() == True : dictValeurs["heure_fin"] = "pointee"
        if self.radio_fin_autre.GetValue() == True : dictValeurs["heure_fin"] = str(self.ctrl_fin_autre.GetHeure())
        # Message de confirmation
        if self.check_message_actif.GetValue() == True :
            dictValeurs["message"] = self.ctrl_message_texte.GetValue() 
        else :
            dictValeurs["message"] = None
        dictValeurs["vocal"] = int(self.ctrl_vocal.GetValue())
        # Message de confirmation
        if self.check_ticket_actif.GetValue() == True :
            dictValeurs["ticket"] = str(self.ctrl_ticket_modele.GetID())
        else :
            dictValeurs["ticket"] = None
        # Renvoie
        return dictValeurs
        
    
# ---------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Liste_unites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.data = []
        self.MAJ() 

    def MAJ(self, IDactivite=None):
        if IDactivite == None :
            self.Clear() 
            self.Enable(False)
            return
        else:
            self.Enable(True)
        db = GestionDB.DB()
        req = """SELECT IDunite, nom
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeValeurs = []
        for IDunite, nom in listeDonnees :
            checked = False
            listeValeurs.append((IDunite, nom, checked))
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
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
    
# -----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_date(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.listeEtats = [
            ("date_actuelle", _(u"Le jour-même")),
            ("prochaine_ouverture", _(u"La prochaine date d'ouverture de l'activité")),
            ]
        self.MAJ() 
    
    def MAJ(self):
        listeItems = []
        for code, label in self.listeEtats :
            listeItems.append(label)
        self.SetItems(listeItems)
        self.Select(0)
                                        
    def SetValeur(self, valeur=None):
        index = 0
        for code, label in self.listeEtats :
            if code == valeur :
                 self.SetSelection(index)
            index += 1

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]

# -----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Reserver(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        # Unité
        self.box_unite_staticbox = wx.StaticBox(self, -1, _(u"Unités de consommation à proposer"))
        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = CTRL_Choix_activite(self)
        self.label_unite = wx.StaticText(self, -1, _(u"Unités :"))
        self.ctrl_unite = CTRL_Liste_unites(self)
        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"))
        self.ctrl_etat = CTRL_Choix_etat(self)
        self.label_attente = wx.StaticText(self, -1, _(u"Attente :"))
        self.check_attente = wx.CheckBox(self, -1, _(u"Proposer place sur liste d'attente si complet"))
        
        self.label_attente.Show(False)
        self.check_attente.Show(False)
        
        # Date
        self.box_date_staticbox = wx.StaticBox(self, -1, _(u"Date à proposer"))
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Choix_date(self)

        # Messages
        self.box_message_staticbox = wx.StaticBox(self, -1, _(u"Messages"))
        self.label_question = wx.StaticText(self, -1, _(u"Question :"))
        self.ctrl_question = wx.TextCtrl(self, -1, u"")
        self.label_confirmation = wx.StaticText(self, -1, _(u"Confirmation :"))
        self.check_confirmation_actif = wx.CheckBox(self, -1, u"")
        self.ctrl_confirmation = wx.TextCtrl(self, -1, u"")
        self.label_audio = wx.StaticText(self, -1, _(u"Audio :"))
        self.ctrl_vocal = wx.CheckBox(self, -1, _(u"Activer la synthèse vocale"))

        self.label_audio.Show(False)
        self.ctrl_vocal.Show(False)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckConfirmation, self.check_confirmation_actif)
        
        # Init
        self.OnChoixActivite(None)
        self.OnCheckConfirmation(None)

    def __set_properties(self):
        self.ctrl_activite.SetToolTipString(_(u"Sélectionnez une activité"))
        self.ctrl_unite.SetToolTipString(_(u"Sélectionnez les unités de consommation à proposer"))
        self.ctrl_etat.SetToolTipString(_(u"Sélectionnez un état"))
        self.check_attente.SetToolTipString(_(u"Cochez cette case pour que Noethys propose une place sur liste d'attente sur il n'y a plus de places"))
        self.ctrl_date.SetToolTipString(_(u"Sélectionnez la date à proposer"))
        self.ctrl_question.SetToolTipString(_(u"Saisissez le texte de la question"))
        self.check_confirmation_actif.SetToolTipString(_(u"Cochez cette case pour activer l'affichage d'un message de confirmation"))
        self.ctrl_confirmation.SetToolTipString(_(u"Saisissez un message de confirmation"))
        self.ctrl_vocal.SetToolTipString(_(u"Cochez cette case pour activer la synthèse vocale"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        
        # Unités
        box_unite = wx.StaticBoxSizer(self.box_unite_staticbox, wx.VERTICAL)
        grid_sizer_unite = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_unite.Add(self.label_activite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.ctrl_activite, 0, wx.EXPAND, 0)
        grid_sizer_unite.Add(self.label_unite, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_unite.Add(self.ctrl_unite, 0, wx.EXPAND, 0)
        grid_sizer_unite.Add(self.label_etat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.ctrl_etat, 0, 0, 0)
        grid_sizer_unite.Add(self.label_attente, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.check_attente, 0, 0, 0)
        grid_sizer_unite.AddGrowableCol(1)
        grid_sizer_unite.AddGrowableRow(1)
        box_unite.Add(grid_sizer_unite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_unite, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Date
        box_date = wx.StaticBoxSizer(self.box_date_staticbox, wx.VERTICAL)
        grid_sizer_date = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_date.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_date, 0, wx.EXPAND, 0)
        grid_sizer_date.AddGrowableCol(1)
        box_date.Add(grid_sizer_date, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_date, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Messages
        box_message = wx.StaticBoxSizer(self.box_message_staticbox, wx.VERTICAL)
        grid_sizer_message = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_message.Add(self.label_question, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_message.Add(self.ctrl_question, 0, wx.EXPAND, 0)
        grid_sizer_message.Add(self.label_confirmation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer_confirmation = wx.BoxSizer(wx.HORIZONTAL)
        sizer_confirmation.Add(self.check_confirmation_actif, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_confirmation.Add(self.ctrl_confirmation, 1, wx.LEFT|wx.EXPAND, 10)
        
        grid_sizer_message.Add(sizer_confirmation, 0, wx.EXPAND, 0)
        grid_sizer_message.Add(self.label_audio, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_message.Add(self.ctrl_vocal, 0, 0, 0)
        grid_sizer_message.AddGrowableCol(1)
        box_message.Add(grid_sizer_message, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_message, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activite.GetID()
        self.ctrl_unite.MAJ(IDactivite)
    
    def OnCheckConfirmation(self, event):
        self.ctrl_confirmation.Enable(self.check_confirmation_actif.GetValue())
        
    def Validation(self):
        if self.ctrl_activite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        if len(self.ctrl_unite.GetIDcoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une unité de consommation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(self.ctrl_unite.GetIDcoches()) > 9 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas proposer plus de 9 unités de consommation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(self.ctrl_question.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une question !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_question.SetFocus()
            return False

        if self.check_confirmation_actif.GetValue() and len(self.ctrl_confirmation.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun texte de confirmation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_confirmation.SetFocus()
            return False

        return True

    def SetValeur(self, valeur=None):
        # Valeur = None ou valeur = dict{"activite":"12...}
        if valeur == None :
            return
        # Activité
        self.ctrl_activite.SetID(int(valeur["activite"]))
        self.OnChoixActivite(None)
        # Unités
        listeUnites = []
        for IDunite in valeur["unite"].split(";") :
            listeUnites.append(int(IDunite))
        self.ctrl_unite.SetIDcoches(listeUnites)
        # Etat
        self.ctrl_etat.SetValeur(valeur["etat"])
        # Attente
        self.check_attente.SetValue(int(valeur["attente"]))
        # Date
        self.ctrl_date.SetValeur(valeur["date"])
        # Messages
        self.ctrl_question.SetValue(valeur["question"])
        if valeur["message"] != None : 
            self.check_confirmation_actif.SetValue(True) 
            self.ctrl_confirmation.SetValue(valeur["message"])
        self.ctrl_vocal.SetValue(int(valeur["vocal"]))
        self.OnCheckConfirmation(None)
        
    def GetValeur(self):
        dictValeurs = {}
        # Activité
        dictValeurs["activite"] = str(self.ctrl_activite.GetID())
        # Unités
        listeUnites = []
        for IDunite in self.ctrl_unite.GetIDcoches() :
            listeUnites.append(str(IDunite))
        dictValeurs["unite"] = str(";".join(listeUnites))
        # Etat
        dictValeurs["etat"] = self.ctrl_etat.GetValeur()
        # Attente
        dictValeurs["attente"] = str(int(self.check_attente.GetValue()))
        # Date
        dictValeurs["date"] = self.ctrl_date.GetValeur() 
        # Messages
        dictValeurs["question"] = self.ctrl_question.GetValue() 
        if self.check_confirmation_actif.GetValue() == True :
            dictValeurs["message"] = self.ctrl_confirmation.GetValue() 
        else :
            dictValeurs["message"] = None
        dictValeurs["vocal"] = int(self.ctrl_vocal.GetValue())
        # Renvoie
        return dictValeurs
        
        


# ---------------------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listePages = [] 
        
        self.ctrl = wx.Choicebook(self, id=-1, style=wx.BK_DEFAULT)
        
        # Binds
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.ctrl, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 0)
        self.SetSizer(box)
        box.Fit(self)
        
        # Init contrôles
        self.CreationPages() 

    def CreationPages(self):
        self.liste_pages = [
            ("enregistrer", CTRL_Enregistrer(self.ctrl) ),
            ("reserver", CTRL_Reserver(self.ctrl) ),
            ("message", CTRL_Message(self.ctrl) ),
            ]
        self.dictPages = {}
        index = 0
        for code, ctrl in self.liste_pages :
            label = DICT_LABELS_ACTIONS[code]
            self.ctrl.AddPage(ctrl, label)
            self.dictPages[code] = {"index":index, "ctrl":ctrl}
            index += 1
    
    def SelectPage(self, code=""):
        """ Sélection d'une page d'après son code """
        if self.dictPages.has_key(code):
            self.ctrl.SetSelection(self.dictPages[code]["index"])
    
    def GetCodePage(self):
        """ Retourne le code de la page sélectionnée """
        selection = self.ctrl.GetSelection()
        for code, dictTemp in self.dictPages.iteritems() :
            if dictTemp["index"] == selection :
                return code
        return None        
    
    def GetPage(self):
        """ Retourne le CTRL de la page actuelle """
        code = self.GetCodePage() 
        ctrl = self.dictPages[code]["ctrl"]
        return ctrl        
        
    def Validation(self):
        # Validation des paramètres du type
        validation = self.GetPage().Validation()
        return validation
        
    def SetValeur(self, codePage="", valeur=None):
        """ Attribue la valeur à la page donnée """
        self.SelectPage(codePage)
        self.GetPage().SetValeur(valeur)
        
    def GetValeur(self):
        """ Récupère la valeur de la page actuellement sélectionnée """
        return self.GetPage().GetValeur()
    
    def GetDonnees(self):
        dictDonnees = {}
        for code, valeur in self.GetValeur().iteritems() :
            dictDonnees["action_%s" % code] = valeur
        dictDonnees["action"] = self.GetCodePage() 
        return dictDonnees
        
    def SetDonnees(self, action="", parametres={}):
        self.SetValeur(action, parametres)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

        # Test ENREGISTRER CONSO
##        self.ctrl.SetValeur("reserver", {"activite":"1", "unite":"1", "etat":"present", "demande":"0", "heure_debut":"pointee", "heure_fin":"16:30", "message":_(u"coucou"), "vocal":"1"})
##        print self.ctrl.GetValeur()
        
        # Test MESSAGES
        self.ctrl.SelectPage("reserver")
##        self.ctrl.SetValeur("message", {"message1":"message1", "message2":"message2", "frequence":"70", "vocal":"1"})
##        print "Messages =", self.ctrl.GetValeur()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()