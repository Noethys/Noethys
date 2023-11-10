#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
from Utils import UTILS_Parametres
from Ol import OL_Selection_sms
from Dlg import DLG_Messagebox
import wx.propgrid as wxpg
import copy
from Utils import UTILS_Envoi_email
from Utils import UTILS_Fichiers
import requests, json



class Page_Message(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="Page_Message", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Message
        self.staticbox_message_staticbox = wx.StaticBox(self, -1, _(u"3. Tapez le message"))
        self.label_objet = wx.StaticText(self, -1, _(u"Objet :"))
        self.ctrl_objet = wx.TextCtrl(self, -1, "")
        self.label_message = wx.StaticText(self, -1, _(u"Message :"))
        self.ctrl_message = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.label_nbre_caracteres = wx.StaticText(self, -1, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnTexte)


    def __set_properties(self):
        self.ctrl_objet.SetToolTip(wx.ToolTip(_(u"Saisissez l'objet du message. Il s'agit d'une donnée interne qui permet la tracabilité du message envoyé.")))
        self.ctrl_message.SetToolTip(wx.ToolTip(_(u"Saisissez le texte du message")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        box_message = wx.StaticBoxSizer(self.staticbox_message_staticbox, wx.VERTICAL)
        grid_sizer_message = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_message.Add(self.label_objet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_message.Add(self.ctrl_objet, 0, wx.EXPAND, 0)
        grid_sizer_message.Add(self.label_message, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_message.Add(self.ctrl_message, 0, wx.EXPAND, 0)
        grid_sizer_message.Add( (5, 5), 0, 0, 0)
        grid_sizer_message.Add(self.label_nbre_caracteres, 0, 0, 0)
        grid_sizer_message.AddGrowableRow(1)
        grid_sizer_message.AddGrowableCol(1)
        box_message.Add(grid_sizer_message, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_base.Add(box_message, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnTexte(self, event=None):
        nbre_caracteres_max = self.clsbase.GetValeur("nbre_caracteres_max", 0)
        texte = _(u"%d / %d caractères") % (len(self.ctrl_message.GetValue()), nbre_caracteres_max)
        self.label_nbre_caracteres.SetLabel(texte)

    def MAJ(self):
        self.OnTexte()

    def Validation(self):
        if len(self.ctrl_objet.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir l'objet du message !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_objet.SetFocus()
            return False

        texte = self.ctrl_message.GetValue()

        if len(texte) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir le texte du message !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_message.SetFocus()
            return False

        nbre_caracteres_max = self.clsbase.GetValeur("nbre_caracteres_max", 0)
        if len(texte) > nbre_caracteres_max :
            dlg = wx.MessageDialog(self, _(u"Vous avez dépassé le nombre de caractères autorisé !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        alphabet_gsm = u" 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZÄäàÅåÆæßÇèéÉìÖöòÑñÜüù#%&()*+,-./:;<>=§$!?£¿¡@_'"
        for caractere in texte :
            if caractere not in alphabet_gsm and caractere != "\n" :
                dlg = wx.MessageDialog(self, _(u"Le caractère '%s' n'est pas pris en charge dans les SMS !") % caractere, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def Sauvegarde(self):
        self.clsbase.SetValeur("objet", self.ctrl_objet.GetValue())
        self.clsbase.SetValeur("message", self.ctrl_message.GetValue())
        return True


# ------------------------------------------------------------------------------------------------------------------------------------



class Page_Saisie_manuelle(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.ctrl = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self.ctrl.SetMinSize((10, 10))
        self.Bind(wx.EVT_TEXT, self.OnCheck, self.ctrl)
        self.ctrl.SetToolTip(wx.ToolTip(_(u"Saisissez manuellement des numéros de téléphones en les séparant par des points-virgules (;)")))

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Layout()

    def OnCheck(self, event):
        self.parent.SetInfos("saisie_manuelle", self.GetDonnees())

    def GetNumeros(self):
        listeTemp = self.ctrl.GetValue().split(";")
        listeNumeros = []
        for texte in listeTemp:
            listeNumeros.append(texte)
        return listeNumeros

    def GetDonnees(self):
        texte = self.ctrl.GetValue()
        liste_telephones = self.GetNumeros()
        dictDonnees = {
            "liste_telephones": liste_telephones,
            "texte": texte,
        }
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        self.ctrl.SetValue(dictDonnees["texte"])
        self.OnCheck(None)

# -------------------------------------------------------------------------------------------------------------------------------------------

class Page_Familles_individus(wx.Panel):
    def __init__(self, parent, categorie="familles"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie

        # Contrôles
        self.listview = OL_Selection_sms.ListView(self, id=-1, categorie=categorie, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.listview.SetMinSize((10, 10))
        self.barre_recherche = OL_Selection_sms.CTRL_Outils(self, listview=self.listview, afficherCocher=True)
        self.barre_recherche.SetBackgroundColour((255, 255, 255))
        self.listview.MAJ()

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.listview, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_base.Add(self.barre_recherche, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

    def OnCheck(self, track):
        self.parent.SetInfos(self.categorie, self.GetDonnees())

    def GetDonnees(self):
        listeID = []
        listeTelephones = []
        for track in self.listview.GetCheckedObjects():
            if track.tel not in (None, ""):
                if self.categorie == "familles":
                    ID = track.IDfamille
                else:
                    ID = track.IDindividu
                listeID.append(ID)
                listeTelephones.append(track.tel)
        listeFiltres = self.listview.listeFiltresColonnes
        dictDonnees = {
            "liste_telephones": listeTelephones,
            "liste_ID": listeID,
            "liste_filtres": listeFiltres,
        }
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        self.barre_recherche.SetFiltres(dictDonnees["liste_filtres"])
        self.listview.SetIDcoches(dictDonnees["liste_ID"])
        self.OnCheck(None)


# ----------------------------------------------------------------------------------------------------------------------------------

def AjouteTexteImage(image=None, texte="", alignement="droite-bas", padding=0, taille_police=9):
    """ Ajoute un texte sur une image bitmap """
    # Création du bitmap
    largeurImage, hauteurImage = image.GetSize()
    if 'phoenix' in wx.PlatformInfo:
        bmp = wx.Bitmap(largeurImage, hauteurImage)
    else:
        bmp = wx.EmptyBitmap(largeurImage, hauteurImage)
    mdc = wx.MemoryDC(bmp)
    dc = wx.GCDC(mdc)
    mdc.SetBackgroundMode(wx.TRANSPARENT)
    mdc.Clear()

    # Paramètres
    dc.SetBrush(wx.Brush(wx.RED))
    dc.SetPen(wx.TRANSPARENT_PEN)
    dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
    dc.SetTextForeground(wx.WHITE)

    # Calculs
    largeurTexte, hauteurTexte = dc.GetTextExtent(texte)

    # Image
    mdc.DrawBitmap(image, 0, 0)

    # Rond rouge
    hauteurRond = hauteurTexte + padding * 2
    largeurRond = largeurTexte + padding * 2 + hauteurRond / 2.0
    if largeurRond < hauteurRond:
        largeurRond = hauteurRond

    if "gauche" in alignement: xRond = 1
    if "droite" in alignement: xRond = largeurImage - largeurRond - 1
    if "haut" in alignement: yRond = 1
    if "bas" in alignement: yRond = hauteurImage - hauteurRond - 1

    if 'phoenix' in wx.PlatformInfo:
        dc.DrawRoundedRectangle(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)
    else:
        dc.DrawRoundedRectangleRect(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)

    # Texte
    xTexte = xRond + largeurRond / 2.0 - largeurTexte / 2.0
    yTexte = yRond + hauteurRond / 2.0 - hauteurTexte / 2.0 - 1
    dc.DrawText(texte, xTexte, yTexte)

    mdc.SelectObject(wx.NullBitmap)
    return bmp


class CTRL_Destinataires(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1)
        self.parent = parent
        self.donnees = {}
        self.SetPadding((10, 8))

        self.listePages = [
            {"code": "familles", "label": _(u"Familles"), "page": Page_Familles_individus(self, "familles"), "image": wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Famille.png"), wx.BITMAP_TYPE_PNG)},
            {"code": "individus", "label": _(u"Individus"), "page": Page_Familles_individus(self, "individus"), "image": wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Personnes.png"), wx.BITMAP_TYPE_PNG)},
            {"code": "saisie_manuelle", "label": _(u"Saisie manuelle"), "page": Page_Saisie_manuelle(self), "image": wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Contrat.png"), wx.BITMAP_TYPE_PNG)},
        ]

        # Images
        self.imageList = wx.ImageList(32, 32)
        for dictPage in self.listePages:
            self.imageList.Add(dictPage["image"])
        self.AssignImageList(self.imageList)

        # Création des pages
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["page"], dictPage["label"], imageId=index)
            index += 1

    def GetIndexPageByCode(self, code=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == code:
                return index
            index += 1
        return None

    def GetPageByCode(self, code=""):
        for dictPage in self.listePages:
            if dictPage["code"] == code:
                return dictPage["page"]
        return None

    def SetImage(self, code="", nbre=0):
        index = self.GetIndexPageByCode(code)
        bmp = self.listePages[index]["image"]
        if nbre > 0:
            bmp = AjouteTexteImage(bmp, str(nbre))
        self.imageList.Replace(index, bmp)
        self.SetPageImage(index, index)

    def SetInfos(self, code="", dictDonnees={}):
        self.donnees[code] = dictDonnees
        # MAJ de l'image de la page
        nbreTelephones = len(dictDonnees["liste_telephones"])
        self.SetImage(code, nbreTelephones)

    def GetListeTelephonesUniques(self):
        listeTelephonesUniques = []
        for code, dictDonnees in self.donnees.items():
            for adresse in dictDonnees["liste_telephones"]:
                if adresse not in listeTelephonesUniques:
                    listeTelephonesUniques.append(adresse)
        return listeTelephonesUniques

    def Validation(self):
        for dictPage in self.listePages:
            if dictPage["page"].Validation() == False:
                return False
        return True

    def GetDonnees(self):
        return self.donnees, self.GetListeTelephonesUniques()

    def SetDonnees(self, donnees={}):
        for code, dictDonnees in donnees.items():
            page = self.GetPageByCode(code)
            page.SetDonnees(dictDonnees)

    def SetAfficherUniquementSMS(self, etat=False):
        self.GetPageByCode("individus").listview.afficher_uniquement_sms = etat
        self.GetPageByCode("individus").listview.MAJ()
        self.GetPageByCode("individus").OnCheck(None)
        self.GetPageByCode("familles").listview.afficher_uniquement_sms = etat
        self.GetPageByCode("familles").listview.MAJ()
        self.GetPageByCode("familles").OnCheck(None)




class Page_Destinataires(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="Page_Destinataires", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Destinataires
        self.staticbox_destinataires_staticbox = wx.StaticBox(self, -1, _(u"2. Cochez les destinataires"))
        self.ctrl_destinataires = CTRL_Destinataires(self)
        self.check_avec_sms = wx.CheckBox(self, -1, _(u"Afficher uniquement les numéros de téléphones dont l'option SMS est activée"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckSMS, self.check_avec_sms)

    def __set_properties(self):
        self.check_avec_sms.SetToolTip(wx.ToolTip(_(u"Cochez cette option pour afficher uniquemement les numéros de téléphones dont l'option SMS a été activée dans la fiche individuelle")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        box_destinataires = wx.StaticBoxSizer(self.staticbox_destinataires_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.ctrl_destinataires, 1, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.check_avec_sms, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_destinataires.Add(grid_sizer_parametres, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_base.Add(box_destinataires, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnCheckSMS(self, event=None):
        self.ctrl_destinataires.SetAfficherUniquementSMS(self.check_avec_sms.GetValue())

    def MAJ(self):
        pass

    def Validation(self):
        listeTelephones = self.ctrl_destinataires.GetDonnees()[1]
        if len(listeTelephones) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un numéro de téléphone !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def Sauvegarde(self):
        listeTelephones = self.ctrl_destinataires.GetDonnees()[1]
        self.clsbase.SetValeur("liste_telephones", listeTelephones)
        return True


# ------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(CTRL_Propertygrid.CTRL):
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)
        self.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    def Remplissage(self):
        # Plateforme
        self.Append(wxpg.PropertyCategory(_(u"Paramètres")))

        liste_choix = [
            ("contact_everyone", _(u"Contact Everyone By Orange Business")),
            ("cleversms", _(u"Clever SMS")),
            ("clevermultimedias", _(u"Clever Multimedias")),
            ("mailjet", _(u"Mailjet")),
            ("ovh", _(u"OVH")),
            ("brevo", _(u"BREVO")),
            ]

        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Plateforme"), name="plateforme", liste_choix=liste_choix, valeur=None)
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez une plateforme"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse envoi d'email
        DB = GestionDB.DB()
        req = """SELECT IDadresse, adresse FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        liste_adresses = DB.ResultatReq()
        DB.Close()
        liste_adresses.insert(0, (0, _(u"Aucune")))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Adresse d'expédition d'email"), name="adresse_expedition_email", liste_choix=liste_adresses, valeur=0)
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'adresse d'expédition de l'email. Cette adresse doit être référencée sur votre compte Contact Everyone."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Adresse de destination
        propriete = wxpg.StringProperty(label=_(u"Adresse de destination"), name="orange_adresse_destination_email", value="diffusion@contact-everyone.fr")
        propriete.SetHelpString(_(u"Saisissez l'adresse de destination de l'email"))
        self.Append(propriete)

        # Adresse de destination
        propriete = wxpg.StringProperty(label=_(u"Adresse de destination"), name="cleversms_adresse_destination_email", value="cleversmslight@cleversaas.fr")
        propriete.SetHelpString(_(u"Saisissez l'adresse de destination de l'email"))
        self.Append(propriete)

        # Adresse de destination
        propriete = wxpg.StringProperty(label=_(u"Adresse de destination"), name="clevermultimedias_adresse_destination_email", value="multimediasattachedfile@cleversaas.fr")
        propriete.SetHelpString(_(u"Saisissez l'adresse de destination de l'email"))
        self.Append(propriete)

        # Token Mailjet
        propriete = wxpg.StringProperty(label=_(u"Token Mailjet"), name="token_sms_mailjet", value="")
        propriete.SetHelpString(_(u"Saisissez le token que vous avez généré sur votre compte Mailjet"))
        self.Append(propriete)

        # Sender ID Mailjet
        propriete = wxpg.StringProperty(label=_(u"Nom de l'expéditeur"), name="sender_sms_mailjet", value="")
        propriete.SetHelpString(_(u"Saisissez le nom de l'expéditeur. Exemples : 'MJC', 'ALSH', 'MAIRIE'..."))
        self.Append(propriete)

        # Nom exp OVH
        propriete = wxpg.StringProperty(label=_(u"Nom de l'expéditeur"), name="ovh_nom_exp", value="")
        propriete.SetHelpString(_(u"Saisissez le nom de l'expéditeur. Exemples : 'MJC', 'ALSH', 'MAIRIE'..."))
        self.Append(propriete)

        # Nom du compte
        propriete = wxpg.StringProperty(label=_(u"Nom du compte"), name="ovh_nom_compte", value="")
        propriete.SetHelpString(_(u"Saisissez le nom du compte"))
        self.Append(propriete)

        # Identifiant
        propriete = wxpg.StringProperty(label=_(u"Identifiant"), name="ovh_identifiant", value="")
        propriete.SetHelpString(_(u"Saisissez l'identifiant"))
        self.Append(propriete)

        # Mot de passe
        propriete = wxpg.StringProperty(label=_(u"Mot de passe"), name="ovh_mot_passe", value="")
        propriete.SetHelpString(_(u"Saisissez le mot de passe"))
        self.Append(propriete)

        # Token BREVO
        propriete = wxpg.StringProperty(label=_(u"Token Brevo"), name="token_sms_brevo", value="")
        propriete.SetHelpString(_(u"Saisissez le token que vous avez généré sur votre compte Brevo"))
        self.Append(propriete)

        # Sender BREVO
        propriete = wxpg.StringProperty(label=_(u"Nom de l'expéditeur"), name="sender_sms_brevo", value="")
        propriete.SetHelpString(_(u"Saisissez le nom de l'expéditeur. Exemples : 'MJC', 'ALSH', 'MAIRIE'..."))
        self.Append(propriete)

        # Nbre caractères max
        propriete = wxpg.IntProperty(label=_(u"Nombre maximal de caractères du message"), name="nbre_caracteres_max", value=160)
        propriete.SetHelpString(_(u"Nombre maximal de caractères du message"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("nbre_caracteres_max", "SpinCtrl")

    def OnPropGridChange(self, event):
        self.Switch()
        event.Skip()

    def Switch(self):
        dict_switch = {
            "plateforme" : {
                None : [
                    ],
                "contact_everyone" : [
                    {"propriete" : "adresse_expedition_email", "obligatoire" : True},
                    {"propriete" : "orange_adresse_destination_email", "obligatoire" : True},
                    {"propriete" : "nbre_caracteres_max", "obligatoire" : True},
                    ],
                "cleversms": [
                    {"propriete": "adresse_expedition_email", "obligatoire": True},
                    {"propriete": "cleversms_adresse_destination_email", "obligatoire": True},
                    {"propriete": "nbre_caracteres_max", "obligatoire": True},
                ],
                "clevermultimedias": [
                    {"propriete": "adresse_expedition_email", "obligatoire": True},
                    {"propriete": "clevermultimedias_adresse_destination_email", "obligatoire": True},
                    {"propriete": "nbre_caracteres_max", "obligatoire": True},
                ],
                "mailjet": [
                    {"propriete": "token_sms_mailjet", "obligatoire": True},
                    {"propriete": "sender_sms_mailjet", "obligatoire": True},
                    {"propriete": "nbre_caracteres_max", "obligatoire": True},
                ],
                "ovh": [
                    {"propriete": "ovh_nom_exp", "obligatoire": True},
                    {"propriete": "ovh_nom_compte", "obligatoire": True},
                    {"propriete": "ovh_identifiant", "obligatoire": True},
                    {"propriete": "ovh_mot_passe", "obligatoire": True},
                    {"propriete": "nbre_caracteres_max", "obligatoire": True},
                ],
                "brevo": [
                    {"propriete": "token_sms_brevo", "obligatoire": True},
                    {"propriete": "sender_sms_brevo", "obligatoire": True},
                    {"propriete": "nbre_caracteres_max", "obligatoire": True},
                ],
            }
        }

        # Cache toutes les propriétés
        for nom_property, dict_conditions in dict_switch.items():
            for condition, liste_proprietes in dict_conditions.items():
                for dict_propriete in liste_proprietes :
                    propriete = self.GetPropertyByName(dict_propriete["propriete"])
                    propriete.Hide(True)
                    propriete.SetAttribute("obligatoire", False)

        # Affiche que les propriétés souhaitées
        for nom_property, dict_conditions in dict_switch.items() :
            propriete = self.GetProperty(nom_property)
            valeur = propriete.GetValue()
            for condition, liste_proprietes in dict_conditions.items() :
                for dict_propriete in liste_proprietes :
                    propriete = self.GetPropertyByName(dict_propriete["propriete"])
                    if valeur == condition :
                        propriete.Hide(False)
                        propriete.SetAttribute("obligatoire", dict_propriete["obligatoire"])

        if 'phoenix' in wx.PlatformInfo:
            self.Refresh()
        else :
            self.RefreshGrid()


    def Validation(self):
        """ Validation des données saisies """
        # Vérifie que les données obligatoires ont été saisies
        for nom, valeur in self.GetPropertyValues().items():
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True:
                if valeur == "" or valeur == None:
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % self.GetPropertyLabel(nom), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        # if self.GetPropertyByName("adresse_expedition_email").GetValue() == 0 :
        #     dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une adresse d'expédition !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
        #     dlg.ShowModal()
        #     dlg.Destroy()
        #     return False

        self.Sauvegarde()

        return True

    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Recherche les paramètres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="envoi_sms", dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.items():
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue()
            propriete.SetValue(valeur)
        self.Switch()

    def Sauvegarde(self, forcer=False):
        """ Mémorisation des valeurs du contrôle """
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="envoi_sms", dictParametres=dictValeurs)

    def GetParametres(self):
        return copy.deepcopy(self.GetPropertyValues())





class Page_Parametres(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="Page_Parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Paramètres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"1. Renseignez les paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.Importation()
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        box_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinitialisation, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_sauvegarde, 0, 0, 0)

        grid_sizer_parametres.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_parametres.Add(grid_sizer_parametres, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.EXPAND|wx.ALL, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def MAJ(self):
        self.ctrl_parametres.Importation()

    def Validation(self):
        if self.ctrl_parametres.Validation() == False :
            return False

        return True

    def Sauvegarde(self):
        for nom, valeur in self.ctrl_parametres.GetParametres().items() :
            self.clsbase.SetValeur(nom, valeur)
        return True




class Base(object) :
    """ Classe commune à l'assistant et au notebook """
    def __init__(self):
        self.dictDonnees = {}

    def InitPages(self, parent=None):
        """ Initialisation des pages """
        self.listePages = [
            {"code" : "parametres", "label" : _(u"Paramètres"), "ctrl" : Page_Parametres(parent, clsbase=self), "image" : "Maison.png"},
            {"code" : "destinataires", "label": _(u"Destinataires"), "ctrl": Page_Destinataires(parent, clsbase=self), "image": "Maison.png"},
            {"code" : "message", "label": _(u"Message"), "ctrl": Page_Message(parent, clsbase=self), "image": "Maison.png"},
        ]
        return self.listePages

    def GetPage(self, code=""):
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                return dictPage["ctrl"]
        return None

    def SetValeur(self, nom="", valeur=None):
        self.dictDonnees[nom] = valeur

    def GetValeurs(self):
        return self.dictDonnees

    def GetValeur(self, nom="", defaut=None):
        if nom in self.dictDonnees:
            return self.dictDonnees[nom]
        return defaut


class Dialog(wx.Dialog, Base):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Envoi_sms", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        Base.__init__(self)
        self.parent = parent

        titre = _(u"Envoi de SMS")
        intro = _(u"Vous pouvez envoyer ici des SMS aux individus ou familles à condition que votre plateforme d'envoi ait été intégrée à cette fonctionnalité. Consultez la liste des prestataires pris en charge dans la liste déroulante Plateforme de la page des paramètres.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Sms.png")

        # Initialisation des pages
        self.InitPages(self)

        self.static_line = wx.StaticLine(self, -1)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_retour = CTRL_Bouton_image.CTRL(self, texte=_(u"Retour"), cheminImage="Images/32x32/Fleche_gauche.png")
        self.bouton_suite = CTRL_Bouton_image.CTRL(self, texte=_(u"Suite"), cheminImage="Images/32x32/Fleche_droite.png", margesImage=(0, 0, 4, 0), positionImage=wx.RIGHT)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 0
                        
        # Création des pages
        self.Creation_Pages()
        self.GetPage("parametres").MAJ()

    def Creation_Pages(self):
        """ Creation des pages """
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages :
            self.sizer_pages.Add(dictPage["ctrl"], 1, wx.EXPAND, 0)
            if index > 0 :
                dictPage["ctrl"].Show(False)
            index += 1
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_retour.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour revenir à la page précédente")))
        self.bouton_suite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour passer à l'étape suivante")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler")))
        self.SetMinSize((770, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        
        self.sizer_pages = sizer_pages

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("EnvoideSMS")

    def AfficherPage(self, numPage=0):
        # rend invisible la page affichée
        page = self.listePages[self.pageVisible]["ctrl"]
        page.Sauvegarde()
        page.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible = numPage
        page = self.listePages[self.pageVisible]["ctrl"]
        page.MAJ()
        page.Show(True)
        self.sizer_pages.Layout()

    def Onbouton_retour(self, event):
        # Affiche nouvelle page
        self.AfficherPage(self.pageVisible - 1)
        # Si on quitte l'avant-dernière page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages-1:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage(Chemins.GetStaticPath("Images/32x32/Valider.png"))
            self.bouton_suite.SetTexte(_(u"Valider"))
        else:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage(Chemins.GetStaticPath("Images/32x32/Fleche_droite.png"))
            self.bouton_suite.SetTexte(_(u"Suite"))
        # Si on revient à la première page, on désactive le bouton Retour
        if self.pageVisible == 0 :
            self.bouton_retour.Enable(False)

    def Onbouton_suite(self, event):
        # Vérifie que les données de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est déjà sur la dernière page : on termine
        if self.pageVisible == self.nbrePages-1 :
            self.listePages[self.pageVisible]["ctrl"].Sauvegarde()
            self.Terminer()
            return
        # Affiche nouvelle page
        self.AfficherPage(self.pageVisible + 1)
        # Si on arrive à la dernière page, on désactive le bouton Suivant
        if self.pageVisible == self.nbrePages-1 :
            self.bouton_suite.SetImage(Chemins.GetStaticPath("Images/32x32/Valider.png"))
            self.bouton_suite.SetTexte(_(u"Envoyer"))
        # Si on quitte la première page, on active le bouton Retour
        if self.pageVisible > 0 :
            self.bouton_retour.Enable(True)

    def OnClose(self, event):
        self.OnBoutonAnnuler()

    def OnBoutonAnnuler(self, event=None):
        self.Annuler()

    def Annuler(self):
        """ Annulation des modifications """
        self.EndModal(wx.ID_CANCEL)

    def ValidationPages(self) :
        """ Validation des données avant changement de pages """
        return self.listePages[self.pageVisible]["ctrl"].Validation()

    def Terminer(self):
        # Envoi du message
        if self.Envoyer() != True :
            return False

        # Fermeture
        self.EndModal(wx.ID_OK)

    def Envoyer(self):
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous l'envoi du message vers %d numéros ?") % len(self.dictDonnees["liste_telephones"]), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # --------------------- CONTACT EVERYONE BY ORANGE BUSINESS ---------------------
        if self.dictDonnees["plateforme"] == "contact_everyone" :

            # Récupération adresse d'expédition
            IDadresse = self.dictDonnees["adresse_expedition_email"]
            dictAdresse = UTILS_Envoi_email.GetAdresseExp(IDadresse=IDadresse)

            # Génération de la pièce jointe
            liste_lignes = []

            for ligne in self.dictDonnees["message"].split("\n") :
                liste_lignes.append(u"T-%s" % ligne)

            for numero in self.dictDonnees["liste_telephones"] :
                numero = numero.replace(".", "")
                liste_lignes.append(u"#-%s" % numero)

            texte = "\n".join(liste_lignes)

            cheminFichier = UTILS_Fichiers.GetRepTemp(fichier="sms.txt")
            fichier = open(cheminFichier, 'w')
            fichier.write(texte.encode("iso-8859-15"))
            fichier.close()

            # Préparation du message
            message = UTILS_Envoi_email.Message(destinataires=[self.dictDonnees["orange_adresse_destination_email"],],
                                                sujet=self.dictDonnees["objet"], texte_html=_(u"Envoi de SMS"), fichiers=[cheminFichier,])

            # Envoi de l'email
            resultat = self.EnvoyerEmail(message=message, dictAdresse=dictAdresse)
            if resultat == False:
                return False

        # --------------------- CLEVER SMS ---------------------
        if self.dictDonnees["plateforme"] == "cleversms" :

            # Récupération adresse d'expédition
            IDadresse = self.dictDonnees["adresse_expedition_email"]
            dictAdresse = UTILS_Envoi_email.GetAdresseExp(IDadresse=IDadresse)

            # Génération de la pièce jointe
            liste_lignes = []

            message = self.dictDonnees["message"].replace("\n", "")
            for numero in self.dictDonnees["liste_telephones"] :
                numero = numero.replace(".", "")
                liste_lignes.append(u"%s;%s" % (numero, message))

            texte = "\n".join(liste_lignes)

            cheminFichier = UTILS_Fichiers.GetRepTemp(fichier="sms.txt")
            fichier = open(cheminFichier, 'w')
            fichier.write(texte.encode("iso-8859-15"))
            fichier.close()

            # Préparation du message
            message = UTILS_Envoi_email.Message(destinataires=[self.dictDonnees["cleversms_adresse_destination_email"],],
                                                sujet=self.dictDonnees["objet"], texte_html=_(u"Envoi de SMS"), fichiers=[cheminFichier,])
            # Envoi de l'email
            resultat = self.EnvoyerEmail(message=message, dictAdresse=dictAdresse)
            if resultat == False:
                return False

        # --------------------- CLEVER MULTIMEDIAS ---------------------
        if self.dictDonnees["plateforme"] == "clevermultimedias" :

            # Récupération adresse d'expédition
            IDadresse = self.dictDonnees["adresse_expedition_email"]
            dictAdresse = UTILS_Envoi_email.GetAdresseExp(IDadresse=IDadresse)

            # Génération de la pièce jointe
            liste_lignes = ["NUM;MESSAGE",]

            message = self.dictDonnees["message"].replace("\n", "")
            for numero in self.dictDonnees["liste_telephones"] :
                numero = numero.replace(".", "")
                numero = "+33" + numero[1:]
                liste_lignes.append(u"%s;%s" % (numero, message))

            texte = "\n".join(liste_lignes)

            cheminFichier = UTILS_Fichiers.GetRepTemp(fichier="sms.txt")
            fichier = open(cheminFichier, 'w')
            fichier.write(texte.encode("iso-8859-15"))
            fichier.close()

            # Préparation du message
            message = UTILS_Envoi_email.Message(destinataires=[self.dictDonnees["clevermultimedias_adresse_destination_email"],],
                                                sujet=self.dictDonnees["objet"], texte_html=_(u"Envoi de SMS"), fichiers=[cheminFichier,])
            # Envoi de l'email
            resultat = self.EnvoyerEmail(message=message, dictAdresse=dictAdresse)
            if resultat == False:
                return False

        # --------------------- MAILJET ---------------------
        if self.dictDonnees["plateforme"] == "mailjet":

            # Récupération token
            api_token = self.dictDonnees["token_sms_mailjet"]
            sender_id = self.dictDonnees["sender_sms_mailjet"]

            # Préparation de l'envoi
            headers = {
                "Authorization": "Bearer {api_token}".format(api_token=api_token),
                "Content-Type": "application/json"
            }
            api_url = "https://api.mailjet.com/v4/sms-send"

            # Envoi des SMS
            message = self.dictDonnees["message"].replace("\n", "")
            nbre_envois_reussis = 0
            for numero in self.dictDonnees["liste_telephones"]:
                numero = numero.replace(".", "")
                numero = "+33" + numero[1:]

                # Création du message JSON
                message_data = {
                    "From": sender_id,
                    "To": numero,
                    "Text": message
                }
                reponse = requests.post(api_url, headers=headers, json=message_data)
                if reponse.ok:
                    nbre_envois_reussis += 1
                else:
                    print("Erreur envoi SMS :", reponse.text)
                    dict_erreur = json.loads(reponse.text)
                    texte_erreur = u"Code erreur : %s. Erreur : %s" % (dict_erreur["ErrorCode"], dict_erreur["ErrorMessage"])
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Envoi de SMS"), introduction=_(u"L'envoi du SMS vers le numéro %s a rencontré une erreur :") % numero,
                                                detail=texte_erreur, conclusion=_(u"Que souhaitez-vous faire ?"),
                                                icone=wx.ICON_ERROR, boutons=[_(u"Continuer l'envoi"), _(u"Arrêter")])
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse == 1:
                        return False

        # Confirmation d'envoi
        dlg = wx.MessageDialog(self, _(u"Envoi des SMS terminé."), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        # --------------------- OVH ---------------------
        if self.dictDonnees["plateforme"] == "ovh":

            # Envoi des SMS
            message = self.dictDonnees["message"].replace("\n", "")
            nbre_envois_reussis = 0
            for numero in self.dictDonnees["liste_telephones"]:
                numero = numero.replace(".", "")
                numero = "+33" + numero[1:]

                # Création du message JSON
                params = {"account": self.dictDonnees["ovh_nom_compte"], "login": self.dictDonnees["ovh_identifiant"],
                          "password": self.dictDonnees["ovh_mot_passe"], "from": self.dictDonnees["ovh_nom_exp"], "to": numero,
                          "message": message, "noStop": 1, "contentType": "text/json"}
                r = requests.get("https://www.ovh.com/cgi-bin/sms/http2sms.cgi", params=params)
                reponse = r.json()
                if reponse["status"] == 100:
                    nbre_envois_reussis += 1
                else:
                    print("Erreur envoi SMS :", reponse["message"])
                    texte_erreur = u"Erreur SMS : %s" % reponse["message"]
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Envoi de SMS"), introduction=_(u"L'envoi du SMS vers le numéro %s a rencontré une erreur :") % numero,
                                                detail=texte_erreur, conclusion=_(u"Que souhaitez-vous faire ?"),
                                                icone=wx.ICON_ERROR, boutons=[_(u"Continuer l'envoi"), _(u"Arrêter")])
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse == 1:
                        return False

        # --------------------- BREVO ---------------------
        if self.dictDonnees["plateforme"] == "brevo":

            # Envoi des SMS
            message = self.dictDonnees["message"].replace("\n", "")
            nbre_envois_reussis = 0
            for numero in self.dictDonnees["liste_telephones"]:
                numero = numero.replace(".", "")
                numero = "+33" + numero[1:]

                # Création du message
                headers = {"accept": "application/json", "api-key": self.dictDonnees["token_sms_brevo"], "Content-Type": "application/json"}
                data = {"sender": self.dictDonnees["sender_sms_brevo"], "recipient": numero, "content": message, "type": "transactional"}
                reponse = requests.post("https://api.brevo.com/v3/transactionalSMS/sms", headers=headers, json=data)
                dict_reponse = reponse.json()
                if reponse.status_code == 201:
                    nbre_envois_reussis += 1
                else:
                    print("Erreur envoi SMS :", dict_reponse["message"])
                    texte_erreur = "%s : %s" % (dict_reponse["code"], dict_reponse["message"])
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Envoi de SMS"), introduction=_(u"L'envoi du SMS vers le numéro %s a rencontré une erreur :") % numero,
                                                detail=texte_erreur, conclusion=_(u"Que souhaitez-vous faire ?"), icone=wx.ICON_ERROR, boutons=[_(u"Continuer l'envoi"), _(u"Arrêter")])
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse == 1:
                        return False

        # Confirmation d'envoi
        dlg = wx.MessageDialog(self, _(u"Envoi des SMS terminé."), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        return True


    def EnvoyerEmail(self, message=None, dictAdresse={}):
        # Envoi de l'email
        try:
            messagerie = UTILS_Envoi_email.Messagerie(backend=dictAdresse["moteur"], hote=dictAdresse["smtp"],
                                                      port=dictAdresse["port"], utilisateur=dictAdresse["utilisateur"],
                                                      motdepasse=dictAdresse["motdepasse"],
                                                      email_exp=dictAdresse["adresse"], use_tls=dictAdresse["startTLS"],
                                                      parametres=dictAdresse["parametres"])
            messagerie.Connecter()
            messagerie.Envoyer(message)
            messagerie.Fermer()
        except Exception as err:
            print((err,))
            err = str(err).decode("iso-8859-15")
            dlgErreur = wx.MessageDialog(None, _(u"Une erreur a été détectée dans l'envoi de l'Email !\n\nErreur : %s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal()
            dlgErreur.Destroy()
            return False

        return True


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
