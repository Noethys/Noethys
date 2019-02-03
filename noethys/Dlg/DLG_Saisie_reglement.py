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
import os
import sys
import datetime
import decimal
import wx.html as html
import wx.lib.agw.hyperlink as Hyperlink
import FonctionsPerso
import six

from Utils import UTILS_Historique
from Utils import UTILS_Identification
from Utils import UTILS_Config
from Utils import UTILS_Titulaires
from Utils import UTILS_Gestion
import GestionDB

SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Ctrl import CTRL_Ventilation

from Dlg import DLG_Messagebox

ID_OPTION_BLOQUER_VENTILATION = wx.NewId() 



def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))




class CTRL_Image(wx.StaticBitmap):
    def __init__(self, parent, style=0):
        wx.StaticBitmap.__init__(self, parent, id=-1, style=style)
        self.parent = parent
        self.tailleImage = (132, 72)
        self.SetMinSize(self.tailleImage) 
        self.SetSize(self.tailleImage) 
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        self.SetPhotoMode()
        
    
    def SetPhotoMode(self, IDmode=None):
        bmp = self.GetPhoto("modes_reglements", "IDmode", IDmode, Chemins.GetStaticPath("Images/Special/Image_non_disponible.png"))
        self.SetBitmap(bmp)

    def SetPhotoEmetteur(self, IDemetteur=None):
        bmp = self.GetPhoto("emetteurs", "IDemetteur", IDemetteur, Chemins.GetStaticPath("Images/Special/Image_non_disponible.png"))
        self.SetBitmap(bmp)    

    def GetPhoto(self, table="", key="", IDkey=None, imageDefaut=None):
        """ Récupère une image """            
        # Recherche de l'image
        if IDkey != None : 
            DB = GestionDB.DB()
            req = "SELECT image FROM %s WHERE %s=%d;" % (table, key, IDkey)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                # Si une image est trouvée
                bmpBuffer = listeDonnees[0][0]
                if bmpBuffer != None :
                    io = six.BytesIO(bmpBuffer)
                    if 'phoenix' in wx.PlatformInfo:
                        img = wx.Image(io, wx.BITMAP_TYPE_JPEG)
                    else :
                        img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
                    bmp = img.Rescale(width=self.tailleImage[0], height=self.tailleImage[1], quality=wx.IMAGE_QUALITY_HIGH) 
                    bmp = bmp.ConvertToBitmap()
                    return bmp
        
        # Si aucune image est trouvée, on prend l'image par défaut
        if imageDefaut != None :
            bmp = self.GetImageDefaut(imageDefaut) 
            return bmp
        
        return None
    
    def GetImageDefaut(self, imageDefaut):
        if os.path.isfile(imageDefaut):
            bmp = wx.Bitmap(Chemins.GetStaticPath(imageDefaut), wx.BITMAP_TYPE_ANY) 
            bmp = bmp.ConvertToImage()
            bmp = bmp.Rescale(width=self.tailleImage[0], height=self.tailleImage[1], quality=wx.IMAGE_QUALITY_HIGH) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        return None
    
# ---------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Infos(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=32,  couleurFond=(255, 255, 255), style=0):
        html.HtmlWindow.__init__(self, parent, -1, style=style)#, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(5)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetLabel(texte)
    
    def SetLabel(self, texte=""):
        self.SetPage(u"""<BODY TEXT='#B2B2B2' LINK='#B2B2B2' VLINK='#B2B2B2' ALINK='#B2B2B2'><FONT SIZE=1 COLOR='#777777'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)
    
    def OnLinkClicked(self, linkinfo):
        IDfamille = int(linkinfo.GetHref())


# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Emetteur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
    
    def MAJ(self, IDmode=None):
        listeItems = self.GetListeDonnees(IDmode)
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self, IDmode=None):
        self.dictDonnees = {}
        listeItems = []
        if IDmode == None :
            return listeItems
        db = GestionDB.DB()
        req = """SELECT IDemetteur, nom
        FROM emetteurs
        WHERE IDmode=%d
        ORDER BY nom;""" % IDmode
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        index = 0
        for IDemetteur, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDemetteur }
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Payeurs(wx.ListBox):
    def __init__(self, parent, IDcompte_payeur=None, IDreglement=None):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.IDcompte_payeur = IDcompte_payeur
        self.IDreglement = IDreglement
        self.MAJ()

    def MAJ(self, IDpayeur=None):
        self.listeDonnees = []
        self.Importation() 
        listeItems = []
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["nom"]
                listeItems.append(label)
        self.Set(listeItems)
        if IDpayeur != None :
            self.SetID(IDpayeur)
        
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDpayeur, nom
        FROM payeurs 
        WHERE IDcompte_payeur=%d
        ORDER BY nom; """ % self.IDcompte_payeur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDpayeur, nom in listeDonnees :
            valeurs = { "ID" : IDpayeur, "nom" : nom }
            self.listeDonnees.append(valeurs)
            
    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["ID"] :
                self.SetSelection(index)
                return
            index += 1
        
    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["ID"]
        return ID

    def Ajouter(self, event=None):
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouveau payeur :"), _(u"Saisie d'un payeur"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("IDcompte_payeur", self.IDcompte_payeur), ("nom", nom), ]
                IDpayeur = DB.ReqInsert("payeurs", listeDonnees)
                DB.Close()
                self.MAJ(IDpayeur)
        dlg.Destroy()

    def Modifier(self, event=None):
        IDpayeur = self.GetID()
        if IDpayeur == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun payeur à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie si payeur rattaché
        nbreReglements = self.GetNbreReglements(IDpayeur)
        if nbreReglements > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce payeur a déjà été associé à %d règlement(s).\n\nSouhaitez-vous tout de même le modifier ?") % nbreReglements, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return
            else :
                dlg.Destroy()

        nom = self.listeDonnees[self.GetSelection()]["nom"]
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le nom du payeur :"), _(u"Modification d'un payeur"), nom)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("nom", nom ), ]
                DB.ReqMAJ("payeurs", listeDonnees, "IDpayeur", IDpayeur)
                DB.Close()
                self.MAJ(IDpayeur)
        dlg.Destroy()

    def Supprimer(self, event=None):
        IDpayeur = self.GetID()
        if IDpayeur == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun payeur à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie si payeur rattaché
        nbreReglements = self.GetNbreReglements(IDpayeur)
        if nbreReglements > 0 :
            dlg = wx.MessageDialog(self, _(u"Impossible de supprimer ce payeur.\n\n Il a déjà été attribué à %d règlement(s) !") % nbreReglements, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce payeur ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("payeurs", "IDpayeur", IDpayeur)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def GetNbreReglements(self, IDpayeur=None):
        DB = GestionDB.DB()
        req = """SELECT IDreglement, date
        FROM reglements
        WHERE IDpayeur=%d
        ;""" % IDpayeur
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()
        DB.Close()
        nbreReglements = 0
        for IDreglement, date in listeReglements :
            if IDreglement != self.IDreglement :
                nbreReglements += 1
        return nbreReglements

class CTRL_Mode(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDmode, label, numero_piece, nbre_chiffres, 
        frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label
        FROM modes_reglements
        ORDER BY label;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDmode, label, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label in listeDonnees :
            self.dictDonnees[index] = { 
                "ID" : IDmode, "label" : label, "numero_piece" : numero_piece, "nbre_chiffres" : nbre_chiffres,
                "frais_gestion" : frais_gestion, "frais_montant" : frais_montant, "frais_pourcentage" : frais_pourcentage, 
                "frais_arrondi" : frais_arrondi, "frais_label" : frais_label, 
                }
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfosMode(self):
        """ Récupère les infos sur le mode sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Frais(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.dictFrais = {}
        self.labelPrestation = u""
        self.montantPrestation = 0.0
        self.IDprestationFrais = None

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
        import DLG_Saisie_frais_gestion
        dlg = DLG_Saisie_frais_gestion.Dialog(self, self.dictFrais)
        if dlg.ShowModal() == wx.ID_OK :
            self.dictFrais = dlg.GetDictFrais()
            self.MAJ() 
        dlg.Destroy()
        self.UpdateLink()

    def GetDictFrais(self):
        return self.dictFrais
    
    def SetPrestationFrais(self, IDprestationFrais=None, montant=None, labelPrestation=None):
        self.IDprestationFrais = IDprestationFrais
        self.dictFrais = {  
            "frais_gestion" : "FIXE",
            "frais_montant" : montant,
            "frais_pourcentage" : None,
            "frais_arrondi" : None,
            "frais_label" : labelPrestation,
            }
        self.MAJ()

    def SetDictFrais(self, dictFrais={}):
        self.dictFrais = dictFrais
        self.MAJ()
    
    def MAJ(self):
        if len(self.dictFrais) == 0 :
            self.SetLabel("Aucun frais")
            self.montantPrestation = 0.0
            self.labelPrestation = ""
            return       
         
        typeFrais = self.dictFrais["frais_gestion"]
        montant = self.dictFrais["frais_montant"]
        pourcentage = self.dictFrais["frais_pourcentage"]
        arrondi = self.dictFrais["frais_arrondi"]
        labelPrestation = self.dictFrais["frais_label"]
        label = _(u"Aucun frais")
        
        # Calcul du montant
        montantReglement = self.parent.ctrl_montant.GetMontant()
        if montantReglement == None :
            montantReglement = 0.0
            
        # Aucun frais
        if typeFrais == None :
            self.montantPrestation = 0.0
            label = _(u"Aucun frais")

        # Montant libre
        if typeFrais == "LIBRE" :
            label = _(u"Aucun frais")

        # Montant fixe
        if typeFrais == "FIXE" :
            self.montantPrestation = montant
            label = u"%.2f %s" % (self.montantPrestation, SYMBOLE)
        
        # Prorata
        if typeFrais == "PRORATA" :
            self.montantPrestation = 1.0 * montantReglement * pourcentage / 100.0
            x = decimal.Decimal(str(self.montantPrestation))
            if arrondi == "centimesup" : typeArrondi = decimal.ROUND_UP
            if arrondi == "centimeinf" : typeArrondi = decimal.ROUND_DOWN
            self.montantPrestation = float(x.quantize(decimal.Decimal('0.01'), typeArrondi))
            label = u"%.2f %s (%s %%)" % (self.montantPrestation, SYMBOLE, pourcentage)
            
        # Recherche label prestation
        if labelPrestation != None :
            self.labelPrestation = labelPrestation
        else:
            self.labelPrestation = u""
        
        # Affiche label du hyperlien
        self.SetLabel(label)
    
    def GetDonnees(self):
        """ Récupère données sur frais de gestion saisis """
        typeFrais = self.dictFrais["frais_gestion"]
        if typeFrais == None :
            # Aucun
            return (None, None, self.IDprestationFrais)
        else :
            # Autres types : Fixe et prorata
            return (self.montantPrestation, self.labelPrestation, self.IDprestationFrais)
        

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDdefaut = None
        self.MAJ()             
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        if self.IDdefaut != None :
            self.SetID(self.IDdefaut)
    
    def GetListeDonnees(self):
        self.dictDonnees = {}
        listeItems = []
        db = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero, defaut
        FROM comptes_bancaires
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        index = 0
        for IDcompte, nom, numero, defaut in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompte }
            listeItems.append(nom)
            if defaut == 1 :
                self.IDdefaut = IDcompte
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]



# -----------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte_payeur=None, IDreglement=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Emetteurs", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDcompte_payeur = IDcompte_payeur
        self.IDreglement = IDreglement
        self.dernierRecu = None
        self.avis_depot = None

        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)

        if self.IDreglement != None :
            DB = GestionDB.DB()
            
            # Recherche du IDcompte_payeur si on vient pas de la fiche famille
            req = """SELECT IDcompte_payeur
            FROM reglements
            WHERE IDreglement=%d
            """ % self.IDreglement
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            self.IDcompte_payeur = listeDonnees[0][0]
            
            # Recherche si reçu édité
            req = """SELECT numero, date_edition, IDutilisateur
            FROM recus
            WHERE IDreglement=%d
            ORDER BY date_edition""" % self.IDreglement
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                numero, date_edition, IDutilisateur = listeDonnees[-1]
                self.dernierRecu = {"numero" : numero, "date_edition" : date_edition, "IDutilisateur" : IDutilisateur}

            DB.Close()
        
        self.date_saisie = datetime.date.today()
        self.IDutilisateur = UTILS_Identification.GetIDutilisateur()
        self.IDdepot = None
        
        # Bandeau
        intro = _(u"Vous pouvez ici saisir un règlement pour une famille. Commencez par saisir la date, sélectionnez le mode de règlement et si besoin l'émetteur associé, saisissez le numéro de pièce (si chèque) puis le montant et sélectionnez un nom de payeur. Enfin, vous devez obligatoirement ventiler le règlement sur les différentes prestations disponibles ci-dessous.")
        titre = _(u"Saisie d'un règlement")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Reglement.png")
        
        # Infos
        self.staticbox_infos_staticbox = wx.StaticBox(self, -1, _(u"Informations"))
##        self.panel_infos = wx.Panel(self, -1, style=wx.TAB_TRAVERSAL)
##        self.panel_infos.SetBackgroundColour("#F0FBED")
        self.ctrl_image = CTRL_Image(self, style=wx.SUNKEN_BORDER)
        self.ctrl_infos = CTRL_Infos(self, couleurFond="#FFFFFF", style=wx.SUNKEN_BORDER ) #F0FBED
        
        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralites"))
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date(self)
        self.ctrl_date.SetDate(datetime.date.today())
        self.label_mode = wx.StaticText(self, -1, _(u"Mode :"))
        self.ctrl_mode = CTRL_Mode(self)
        self.label_emetteur = wx.StaticText(self, -1, _(u"Emetteur :"))
        self.ctrl_emetteur = CTRL_Emetteur(self)
        self.label_numero = wx.StaticText(self, -1, _(u"N° Pièce :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, u"")
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD, 0, u"")
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, font)
        self.label_payeur = wx.StaticText(self, -1, _(u"Payeur :"))
        self.ctrl_payeur = CTRL_Payeurs(self, self.IDcompte_payeur, IDreglement=self.IDreglement)
        self.ctrl_payeur.SetMinSize((50, 50))
        self.bouton_ajouter_payeur = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_payeur = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_payeur = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_calendrier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_mode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_emetteur = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_quittancier = wx.StaticText(self, -1, _(u"N° Quittancier :"))
        self.ctrl_quittancier = wx.TextCtrl(self, -1, u"")
        self.label_recu = wx.StaticText(self, -1, _(u"Edition reçu :"))
        self.ctrl_recu = wx.CheckBox(self, -1, u"")
        self.label_frais = wx.StaticText(self, -1, _(u"Frais de gestion :"))
        self.hyperlien_frais = CTRL_Frais(self, label=_(u"Aucun frais"), infobulle=_(u"Cliquez ici pour appliquer des frais de gestion"), URL="")
        
        # Encaissement
        self.staticbox_encaissement_staticbox = wx.StaticBox(self, -1, _(u"Encaissement"))
        self.label_compte = wx.StaticText(self, -1, _(u"Compte :"))
        self.ctrl_compte = CTRL_Compte(self)
        self.label_differe = wx.StaticText(self, -1, _(u"Différé :"))
        self.ctrl_check_differe = wx.CheckBox(self, -1, u"")
        self.label_differe_2 = wx.StaticText(self, -1, _(u"A partir du"))
        self.ctrl_differe = CTRL_Saisie_date.Date(self)
        self.label_attente = wx.StaticText(self, -1, _(u"Attente :"))
        self.ctrl_attente = wx.CheckBox(self, -1, u"")
        
        self.bouton_calendrier_differe = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))

        # Ventilation
        self.staticbox_ventilation_staticbox = wx.StaticBox(self, -1, _(u"Ventilation"))
        self.ctrl_ventilation = CTRL_Ventilation.CTRL(self, IDcompte_payeur=self.IDcompte_payeur, IDreglement=self.IDreglement)

        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_calculatrice = CTRL_Bouton_image.CTRL(self, texte=_(u"Calculatrice"), cheminImage="Images/32x32/Calculatrice.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixEmetteur, self.ctrl_emetteur)
        self.Bind(wx.EVT_CHOICE, self.OnChoixMode, self.ctrl_mode)
        self.ctrl_numero.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNumero)
        self.ctrl_montant.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusMontant)
        self.ctrl_montant.Bind(wx.EVT_TEXT, self.OnTextMontant)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrier, self.bouton_calendrier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMode, self.bouton_mode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmetteur, self.bouton_emetteur)
        self.Bind(wx.EVT_BUTTON, self.OnAjouterPayeur, self.bouton_ajouter_payeur)
        self.Bind(wx.EVT_BUTTON, self.OnModifierPayeur, self.bouton_modifier_payeur)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerPayeur, self.bouton_supprimer_payeur)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDiffere, self.ctrl_check_differe)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrierDiffere, self.bouton_calendrier_differe)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalculatrice, self.bouton_calculatrice)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Récupération du nom des titulaires
        try :
            dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille=[self.IDcompte_payeur,])
            nomsTitulaires = dictTitulaires[self.IDcompte_payeur]["titulairesSansCivilite"]
        except :
            nomsTitulaires = None
        
        # Importation des données
        if nomsTitulaires != None and nomsTitulaires != "" :
            titreFamille = _(u"pour la famille de %s") % nomsTitulaires
        else:
            titreFamille = u""
        if self.IDreglement != None :
            self.Importation() 
            self.SetTitle(_(u"Saisie d'un règlement %s") % titreFamille)
        else:
            self.SetTitle(_(u"Modification d'un règlement %s") % titreFamille)

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(None)

        # Initialisation des contrôles
        self.OnCheckDiffere(None)
        self.MAJinfos() 
##        self.ctrl_ventilation.MAJ() 
        
        if self.IDreglement == None :
            self.OnChoixMode(None)
            # Importe les dernières valeurs
            self.ImportationDernierReglement() 

        # Verrouillage
        self.Verrouillage()
        
        # Paramètres
        self.ctrl_ventilation.ctrl_ventilation.bloquer_ventilation = UTILS_Config.GetParametre("ventilation_bloquer", True)
        
        # Focus
        self.ctrl_date.SetFocus() 
        wx.CallAfter(self.ctrl_date.SetInsertionPoint, 0)
                

    def __set_properties(self):
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez la date d'émission du règlement")))
        self.ctrl_mode.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode de règlement")))
        self.ctrl_emetteur.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'émetteur du règlement (banque ou organisme)")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de la pièce")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant en %s") % SYMBOLE))
        self.bouton_calendrier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la date dans un calendrier")))
        self.bouton_mode.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer un mode de règlement")))
        self.bouton_emetteur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer un émetteur de règlement")))
        self.ctrl_attente.SetToolTip(wx.ToolTip(_(u"Cochez cette case si vous souhaitez laisser l'encaissement en attente")))
        self.ctrl_compte.SetToolTip(wx.ToolTip(_(u"Sélectionner le compte bancaire sur lequel encaisser ce règlement")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici les observations de votre choix")))
        self.ctrl_quittancier.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro de quittancier si vous en utilisez un")))
        self.ctrl_recu.SetToolTip(wx.ToolTip(_(u"Cochez cette case si vous souhaitez éditer un reçu pour ce règlement juste après la validation de celui-ci")))
        self.bouton_ajouter_payeur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un payeur")))
        self.bouton_modifier_payeur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le payeur sélectionné")))
        self.bouton_supprimer_payeur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le payeur sélectionné")))
        self.ctrl_check_differe.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour préciser une date d'encaissement ultérieure")))
        self.bouton_calendrier_differe.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner une date d'encaissement différé dans un calendrier")))
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux options")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_calculatrice.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la calculatrice installée par défaut sur votre ordinateur")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.ctrl_differe.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date d'encaissement souhaitée")))
        self.ctrl_mode.SetMinSize((200, -1))
        self.ctrl_montant.SetMinSize((-1, 30))
        self.ctrl_compte.SetMinSize((200, 21))
        self.SetMinSize((850, 730))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_haut_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Infos
        staticbox_infos = wx.StaticBoxSizer(self.staticbox_infos_staticbox, wx.VERTICAL)
        grid_sizer_infos = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_infos.Add(self.ctrl_image, 0, wx.ALL, 5)
        grid_sizer_infos.Add(self.ctrl_infos, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP|wx.EXPAND, 5)
##        self.panel_infos.SetSizer(grid_sizer_infos)
        grid_sizer_infos.AddGrowableRow(1)
        staticbox_infos.Add(grid_sizer_infos, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_haut.Add(staticbox_infos, 1, wx.EXPAND, 0)
        
        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Date
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_date.Add(self.ctrl_date, 0, wx.EXPAND, 0)
        grid_sizer_date.Add(self.bouton_calendrier, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_date, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_mode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Mode
        grid_sizer_mode = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_mode.Add(self.ctrl_mode, 0, wx.EXPAND, 0)
        grid_sizer_mode.Add(self.bouton_mode, 0, 0, 0)
        grid_sizer_mode.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_mode, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_emetteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Emetteur
        grid_sizer_emetteur = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_emetteur.Add(self.ctrl_emetteur, 0, wx.EXPAND, 0)
        grid_sizer_emetteur.Add(self.bouton_emetteur, 0, 0, 0)
        grid_sizer_emetteur.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_emetteur, 1, wx.EXPAND, 0)
        
        # Numéro
        grid_sizer_generalites.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_numero, 0, 0, 0)
        
        # Montant
        grid_sizer_generalites.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_generalites.Add(self.label_payeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Payeurs
        grid_sizer_payeur = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_payeurs = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_payeur.Add(self.ctrl_payeur, 0, wx.EXPAND, 0)
        grid_sizer_boutons_payeurs.Add(self.bouton_ajouter_payeur, 0, 0, 0)
        grid_sizer_boutons_payeurs.Add(self.bouton_modifier_payeur, 0, 0, 0)
        grid_sizer_boutons_payeurs.Add(self.bouton_supprimer_payeur, 0, 0, 0)
        grid_sizer_payeur.Add(grid_sizer_boutons_payeurs, 1, wx.EXPAND, 0)
        grid_sizer_payeur.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_payeur, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticbox_generalites, 1, wx.EXPAND, 0)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_quittancier, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_quittancier, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_recu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_recu, 0, 0, 0)
        grid_sizer_options.Add(self.label_frais, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Frais
        grid_sizer_frais = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_frais.Add(self.hyperlien_frais, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(grid_sizer_frais, 1, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableRow(0)
        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(staticbox_options, 1, wx.EXPAND, 0)
        
        # Encaissement
        staticbox_encaissement = wx.StaticBoxSizer(self.staticbox_encaissement_staticbox, wx.VERTICAL)
        grid_sizer_encaissement = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_encaissement.Add(self.label_compte, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_encaissement.Add(self.ctrl_compte, 0, wx.EXPAND, 0)
        grid_sizer_encaissement.Add(self.label_differe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_differe = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_differe.Add(self.ctrl_check_differe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_differe.Add(self.label_differe_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_differe.Add(self.ctrl_differe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_differe.Add(self.bouton_calendrier_differe, 0, 0, 0)
        grid_sizer_encaissement.Add(grid_sizer_differe, 0, 0, 0)
        
        grid_sizer_encaissement.Add(self.label_attente, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_encaissement.Add(self.ctrl_attente, 0, 0, 0)
        grid_sizer_encaissement.AddGrowableCol(1)
        staticbox_encaissement.Add(grid_sizer_encaissement, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(staticbox_encaissement, 1, wx.EXPAND, 0)
        grid_sizer_haut_droit.AddGrowableRow(0)
        
        grid_sizer_haut.Add(grid_sizer_haut_droit, 1, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Ventilation
        staticbox_ventilation = wx.StaticBoxSizer(self.staticbox_ventilation_staticbox, wx.VERTICAL)
        grid_sizer_ventilation = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_ventilation.Add(self.ctrl_ventilation, 0, wx.EXPAND, 0)
        grid_sizer_ventilation.AddGrowableRow(0)
        grid_sizer_ventilation.AddGrowableCol(0)
        staticbox_ventilation.Add(grid_sizer_ventilation, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_ventilation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=7, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_calculatrice, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        
        # Détermine la taille de la fenêtre
        taille_fenetre = UTILS_Config.GetParametre("taille_fenetre_reglement")
        if taille_fenetre == None :
            self.SetSize((840, 700))
        else :
            if taille_fenetre == (0, 0) :
                self.Maximize(True)
            else:
                self.SetSize(taille_fenetre)
        self.CenterOnScreen() 
        
        wx.CallLater(0, self.Layout) # Contre pb d'affichage du wx.Choice
    
    def Verrouillage(self):
        verrou = False

        # Verrou si période de gestion verrouillée
        if self.IDreglement != None and self.gestion.Verification("reglements", self.ctrl_date.GetDate()) == False:
            verrou = True

        # Verrou si règlement dans dépôt
        if self.IDdepot != None :
            verrou = True

        if verrou == True :
            self.ctrl_date.Enable(False)
            self.ctrl_mode.Enable(False)
            #self.ctrl_emetteur.Enable(False)
            #self.ctrl_numero.Enable(False)
            self.ctrl_montant.Enable(False)
            #self.ctrl_payeur.Enable(False)
            self.bouton_ajouter_payeur.Enable(False)
            self.bouton_modifier_payeur.Enable(False)
            self.bouton_supprimer_payeur.Enable(False)
            self.bouton_calendrier.Enable(False)
            self.bouton_mode.Enable(False)
            self.bouton_emetteur.Enable(False)
            self.ctrl_compte.Enable(False)
            self.ctrl_check_differe.Enable(False)
            self.ctrl_differe.Enable(False)
            self.ctrl_attente.Enable(False)
            self.bouton_calendrier_differe.Enable(False)

    
    def MAJinfos(self):
        texte = u""
        # IDrèglement
        if self.IDreglement != None :
            texte += _(u"Règlement n°%d<BR>") % self.IDreglement
        else:
            DB = GestionDB.DB()
            prochainID = DB.GetProchainID("reglements")
            DB.Close()
            if prochainID != None :
                texte += _(u"Règlement n°%d<BR>") % prochainID
        # Date saisie
        texte += _(u"Saisi le %s<BR>") % DateEngFr(str(self.date_saisie))
        # Nom Utilisateur
        if self.IDutilisateur != None :
            dictUtilisateur = UTILS_Identification.GetAutreDictUtilisateur(self.IDutilisateur)
            if dictUtilisateur != None :
                nomUtilisateur = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
            else:
                nomUtilisateur = u"n°%d" % self.IDutilisateur
        else:
            nomUtilisateur = _(u"Utilisateur inconnu")
        texte += _(u"Par l'utilisateur %s<BR>") % nomUtilisateur
        # Compte payeur
        texte += _(u"Compte payeur n°%d<BR>") % self.IDcompte_payeur
        # Dépôt
        if self.IDdepot != None :
            texte += _(u"Dépôt n°%d<BR>") % self.IDdepot
        else :
            texte += _(u"Non déposé<BR>")
        # Dernier reçu
        if self.dernierRecu == None :
            texte += _(u"Aucun reçu édité<BR>")
        else :
            numero = self.dernierRecu["numero"]
            date_edition = DateEngFr(str(self.dernierRecu["date_edition"]))
            if self.IDutilisateur != None :
                dictUtilisateur = UTILS_Identification.GetAutreDictUtilisateur(self.dernierRecu["IDutilisateur"])
                if dictUtilisateur != None :
                    nomUtilisateur = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
                else:
                    nomUtilisateur = u"n°%d" % self.IDutilisateur
            else:
                nomUtilisateur = _(u"Utilisateur inconnu")
            texte += _(u"Reçu n°%s édité le %s par %s<BR>") % (numero, date_edition, nomUtilisateur)
        # Avis de dépôt
        if self.avis_depot != None :
            texte += _(u"Avis de dépôt envoyé par Email le %s<BR>") % DateEngFr(str(self.avis_depot))
            
        self.ctrl_infos.SetLabel(texte)

    def OnChoixMode(self, event): 
        IDmode = self.ctrl_mode.GetID()
        self.ctrl_emetteur.MAJ(IDmode)
        self.ctrl_image.SetPhotoMode(IDmode)
        self.FormateNumPiece() 
        self.SetFraisGestion() 

    def OnChoixEmetteur(self, event): 
        IDemetteur = self.ctrl_emetteur.GetID()
        self.ctrl_image.SetPhotoEmetteur(IDemetteur)
        
    def OnBoutonCalendrier(self, event): 
        import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date.SetDate(date)
        dlg.Destroy()

    def OnBoutonMode(self, event): 
        IDmode = self.ctrl_mode.GetID()
        import DLG_Modes_reglements
        dlg = DLG_Modes_reglements.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_mode.MAJ()
        self.ctrl_mode.SetID(IDmode)
        self.OnChoixMode(None)

    def OnBoutonEmetteur(self, event): 
        IDemetteur = self.ctrl_emetteur.GetID()
        IDmode = self.ctrl_mode.GetID()
        import DLG_Emetteurs
        dlg = DLG_Emetteurs.Dialog(self)
        dlg.SelectMode(IDmode)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_emetteur.MAJ(IDmode)
        self.ctrl_emetteur.SetID(IDemetteur)
        self.OnChoixEmetteur(None)
    
    def OnKillFocusNumero(self, event):
        self.FormateNumPiece() 
        event.Skip()

    def OnKillFocusMontant(self, event):
        montant = self.ctrl_montant.GetMontant()
        if montant == None :
            self.ctrl_montant.SetMontant(0.0)
        # MAJ des frais de gestion
        self.hyperlien_frais.MAJ() 
        # MAJ de la ventilation
        if montant != None :
            self.ctrl_ventilation.SetMontantReglement(montant)
        event.Skip()
    
    def OnTextMontant(self, event):
        montant = self.ctrl_montant.GetMontant()
        self.hyperlien_frais.MAJ() 
        self.ctrl_ventilation.SetMontantReglement(montant)
##        self.ctrl_ventilation.Show(montant >= 0.0)
        event.Skip()
        
    def FormateNumPiece(self):
        """ Formate le numéro de pièce en fonction du paramétrage du mode de règlement """
        dictInfosMode = self.ctrl_mode.GetInfosMode()
        if dictInfosMode == None : return
        numero_piece = dictInfosMode["numero_piece"]
        nbre_chiffres = dictInfosMode["nbre_chiffres"]
        # Si aucun numéro de pièce
        if numero_piece == None : 
            self.ctrl_numero.Enable(False)
        # Si alphanumérique :
        if numero_piece == "ALPHA" :
            self.ctrl_numero.Enable(True)
        # Si numérique
        if numero_piece == "NUM" :
            self.ctrl_numero.Enable(True)
            if nbre_chiffres != None:
                try :
                    numero = int(self.ctrl_numero.GetValue())
                    exec("self.ctrl_numero.SetValue('%0" + str(nbre_chiffres) + "d' % numero)")
                except :
                    pass

    def SetFraisGestion(self):
        # Récupération des infos par défaut du règlement
        dictInfosMode = self.ctrl_mode.GetInfosMode()
        if dictInfosMode == None : return
        dictFrais = {  
            "frais_gestion" : dictInfosMode["frais_gestion"],
            "frais_montant" : dictInfosMode["frais_montant"],
            "frais_pourcentage" : dictInfosMode["frais_pourcentage"],
            "frais_arrondi" : dictInfosMode["frais_arrondi"],
            "frais_label" : dictInfosMode["frais_label"],
            }
        self.hyperlien_frais.SetDictFrais(dictFrais)

    def OnAjouterPayeur(self, event): 
        self.ctrl_payeur.Ajouter()

    def OnModifierPayeur(self, event): 
        self.ctrl_payeur.Modifier()

    def OnSupprimerPayeur(self, event): 
        self.ctrl_payeur.Supprimer()
        
    def OnCheckDiffere(self, event): 
        if self.ctrl_check_differe.GetValue() == True and self.IDdepot == None :
            etat = True
        else:
            etat = False
        self.label_differe_2.Enable(etat) 
        self.ctrl_differe.Enable(etat) 
        self.bouton_calendrier_differe.Enable(etat) 
        if etat == True :
            self.ctrl_differe.SetFocus()
            self.ctrl_differe.SetInsertionPoint(0)

    def OnBoutonCalendrierDiffere(self, event): 
        import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_differe.SetDate(date)
        dlg.Destroy()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Rglements1")

    def OnBoutonOptions(self, event):
        # Création du menu Options
        menuPop = UTILS_Adaptations.Menu()
    
        item = wx.MenuItem(menuPop, ID_OPTION_BLOQUER_VENTILATION, _(u"Bloquer la ventilation lorsque le crédit est épuisé"), _(u"Bloquer la ventilation lorsque le crédit est épuisé"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_option_bloquer_ventilation, id=ID_OPTION_BLOQUER_VENTILATION)
        if self.ctrl_ventilation.ctrl_ventilation.bloquer_ventilation == True : item.Check(True)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def On_option_bloquer_ventilation(self, event):
        self.ctrl_ventilation.ctrl_ventilation.bloquer_ventilation = not self.ctrl_ventilation.ctrl_ventilation.bloquer_ventilation
        
    def OnBoutonCalculatrice(self, event):
        FonctionsPerso.OuvrirCalculatrice() 
        
    def OnBoutonOk(self, event): 
        # Sauvegarde des données
        valide = self.Sauvegarde()
        if valide == False :
            return
        
        # Recherche si la famille est abonnée à l'envoi du reçu par Email
        email_envoye = False
        DB = GestionDB.DB()
        req = """SELECT familles.IDfamille, email_recus 
        FROM familles 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        WHERE comptes_payeurs.IDcompte_payeur=%d;""" % self.IDcompte_payeur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        IDfamille, email_recus = listeDonnees[0]
        if email_recus != None and self.nouveauReglement == True :

            icone = wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Emails_exp.png"), wx.BITMAP_TYPE_ANY)
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Envoi du reçu par Email"), introduction=_(u"Cette famille est abonnée au service d'envoi automatique des reçus de règlements par Email."), conclusion=_(u"Confirmez-vous l'envoi du reçu maintenant ?"), icone=icone, boutons=[_(u"Envoyer"), _(u"Accéder aux paramètres d'envoi"), _(u"Ne pas envoyer")])
            reponse = dlg.ShowModal()
            dlg.Destroy()

            if reponse != 2 :
                
                # Recherche de l'adresse d'envoi
                DB = GestionDB.DB()
                req = """SELECT individus.IDindividu, mail, travail_mail
                FROM individus
                LEFT JOIN rattachements ON rattachements.IDindividu = individus.IDindividu
                WHERE rattachements.IDfamille=%d;""" % IDfamille
                DB.ExecuterReq(req)
                listeAdressesIndividus = DB.ResultatReq()
                DB.Close() 
                dictAdressesIndividus = {}
                for IDindividu, mail, travail_mail in listeAdressesIndividus :
                    dictAdressesIndividus[IDindividu] = {"perso" : mail, "travail" : travail_mail}
            
                IDindividu, categorie, adresse = email_recus.split(";")
                if IDindividu != "" :
                    try :
                        if int(IDindividu) in dictAdressesIndividus :
                            adresse = dictAdressesIndividus[int(IDindividu)][categorie]
                    except :
                        pass
                
                if adresse == None :
                    dlg = wx.MessageDialog(self, _(u"L'adresse Email enregistrée ne semble pas valide. Renseignez une nouvelle adresse valide pour cette famille..."), _(u"Erreur d'adresse Email"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    #return False

                else :
                    
                    # Ouverture du Mailer
                    import DLG_Impression_recu
                    dlg1 = DLG_Impression_recu.Dialog(self, IDreglement=self.IDreglement) 
                    dlg1.listeAdresses = [adresse,]
                    
                    if reponse == 1 :
                        # Accès aux paramètres
                        dlg1.ShowModal() 
                        dlg1.Destroy() 
                    
                    if reponse == 0 :
                        # Envoi direct
                        nomDoc=FonctionsPerso.GenerationNomDoc("RECU", "pdf")
                        categorie="recu_reglement"
                        dictChamps = dlg1.CreationPDF(nomDoc=nomDoc, afficherDoc=False)
                        if dictChamps == False :
                            dlg1.Destroy()
                            #return False

                        try :
                            listeDonnees = [{"adresse" : adresse, "pieces" : [nomDoc,], "champs" : dictChamps,}]
                            import DLG_Mailer
                            dlg2 = DLG_Mailer.Dialog(self, categorie=categorie, afficher_confirmation_envoi=False)
                            dlg2.SetDonnees(listeDonnees, modificationAutorisee=False)
                            dlg2.ChargerModeleDefaut()
                            dlg2.OnBoutonEnvoyer(None)
                            if len(dlg2.listeAnomalies) == 0 :
                                succes = True
                            else :
                                succes = False
                            dlg2.Destroy()
                        except :
                            pass

                        try :
                            os.remove(nomDoc)     
                        except :
                            pass
                        
                        # Mémorisation de l'édition du reçu
                        if succes == True :
                            dlg1.Sauvegarder(demander=False)
                        dlg1.Destroy() 

        # Mémorisation du paramètre de la taille d'écran
        UTILS_Config.SetParametre("ventilation_bloquer", self.ctrl_ventilation.ctrl_ventilation.bloquer_ventilation)

        # Edition d'un reçu
        if self.ctrl_recu.GetValue() == True and email_envoye == False :
            import DLG_Impression_recu
            dlg = DLG_Impression_recu.Dialog(self, IDreglement=self.IDreglement) 
            dlg.ShowModal()
            dlg.Destroy()
            
        # Fermeture
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event):
        try :
            self.EndModal(wx.ID_CANCEL)
        except :
            pass
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT 
        IDcompte_payeur, date, IDmode, IDemetteur, numero_piece, montant, IDpayeur,
        observations, numero_quittancier, IDprestation_frais, IDcompte, date_differe, 
        encaissement_attente, IDdepot, date_saisie, IDutilisateur, avis_depot
        FROM reglements
        WHERE IDreglement=%d;
        """ % self.IDreglement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : 
            DB.Close()
            return
        
        IDcompte_payeur, date, IDmode, IDemetteur, numero_piece, montant, IDpayeur, observations, numero_quittancier, IDprestation_frais, IDcompte, date_differe, encaissement_attente, IDdepot, date_saisie, IDutilisateur, avis_depot = listeDonnees[0]
        
        # Généralités
        self.ctrl_date.SetDate(date)
        self.ctrl_mode.SetID(IDmode)
        self.OnChoixMode(None)
        if self.ctrl_emetteur.IsEnabled() == True :
            self.ctrl_emetteur.SetID(IDemetteur)
            self.OnChoixEmetteur(None)
        if numero_piece != None :
            self.ctrl_numero.SetValue(numero_piece)
        self.ctrl_montant.SetMontant(montant)
        self.ctrl_ventilation.SetMontantReglement(montant)
        self.ctrl_payeur.SetID(IDpayeur)
        self.avis_depot = avis_depot
        
        # Options
        if observations != None :
            self.ctrl_observations.SetValue(observations)
        if numero_quittancier != None :
            self.ctrl_quittancier.SetValue(numero_quittancier)
        
        # JE N'AI PAS PROGRAMME LA RECUP DE LA PRESTATION FRAIS DE GESTION !!!!!
        
        # Encaissement
        self.ctrl_compte.SetID(IDcompte)
        if date_differe != None :
            self.ctrl_differe.SetDate(date_differe)
            self.ctrl_check_differe.SetValue(True)
        if encaissement_attente == 1 :
            self.ctrl_attente.SetValue(True)
        if IDdepot != None :
            self.ctrl_compte.Enable(False)
            self.ctrl_check_differe.Enable(False)
            self.ctrl_attente.Enable(False)
        
        # Autres
        self.date_saisie = DateEngEnDateDD(date_saisie)
        self.IDutilisateur = IDutilisateur
        self.IDdepot = IDdepot
        
        # Frais de gestion
        req = """SELECT IDprestation, montant_initial, label
        FROM prestations
        WHERE reglement_frais=%d;
        """ % self.IDreglement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 : 
            IDprestationFrais, montant, labelPrestation = listeDonnees[0]
            self.hyperlien_frais.SetPrestationFrais(IDprestationFrais, montant, labelPrestation)
        else :
            self.hyperlien_frais.SetDictFrais({  
                    "frais_gestion" : None,
                    "frais_montant" : None,
                    "frais_pourcentage" : None,
                    "frais_arrondi" : None,
                    "frais_label" : None,
                    })

    
    def GetIDreglement(self):
        return self.IDreglement
    
    def Sauvegarde(self):
        # Date
        date = self.ctrl_date.GetDate()
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date d'émission du règlement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False

        # Vérifie que le règlement n'est pas dans une période de gestion
        if self.gestion.Verification("reglements", date) == False: return False

        # Mode
        IDmode = self.ctrl_mode.GetID()
        if IDmode == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un mode de règlement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_mode.SetFocus()
            return False
        
        # Emetteur
        IDemetteur = self.ctrl_emetteur.GetID()
        if self.ctrl_emetteur.IsEnabled() and IDemetteur == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un émetteur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_emetteur.SetFocus()
            return False
        
        # Numéro de pièce
        numero_piece = self.ctrl_numero.GetValue()
        if self.ctrl_numero.IsEnabled() :
            if numero_piece == "" :
                dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir saisir de numéro de pièce ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    return False
        else:
            numero_piece = ""
        
        # Montant
        montant = self.ctrl_montant.GetMontant()
        if self.ctrl_montant.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Le montant que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        if montant == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de vouloir conserver un montant nul ?"), _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return False

        # Payeur
        IDpayeur = self.ctrl_payeur.GetID() 
        if IDpayeur == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un payeur dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_payeur.SetFocus()
            return False
        
        # Observations
        observations = self.ctrl_observations.GetValue()
        numero_quittancier = self.ctrl_quittancier.GetValue()
        
        # Compte d'encaissement
        IDcompte = self.ctrl_compte.GetID()
        if IDcompte == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte bancaire dans la liste ! S'il n'y en aucun, vous devez en paramétrer un à partir du menu Paramétrage de la fenêtre d'accueil..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_compte.SetFocus()
            return False
        
        # Encaissement différé
        date_differe = None
        if self.ctrl_check_differe.GetValue() == True :
            date_differe = self.ctrl_differe.GetDate()
            if date_differe == None :
                dlg = wx.MessageDialog(self, _(u"La date d'encaissement différé n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_differe.SetFocus()
                return False
        
        # Attente d'encaissement
        encaissement_attente = 0
        if self.ctrl_attente.GetValue() == True :
            encaissement_attente = 1
        
        # Ventilation
        if self.ctrl_ventilation.Validation() == False :
            return False
        
        # Date de saisie
        date_saisie = self.date_saisie
        
        # Utilisateur
        IDutilisateur = self.IDutilisateur
        
        # Récupère IDfamille
        DB = GestionDB.DB()
        req = """SELECT IDfamille
        FROM comptes_payeurs
        WHERE IDcompte_payeur=%d
        """ % self.IDcompte_payeur
        DB.ExecuterReq(req)
        IDfamille = DB.ResultatReq()[0][0]

        # Récupère des frais de gestion
        donneesFrais = self.hyperlien_frais.GetDonnees() 
        if donneesFrais[0] != None and donneesFrais[0] != 0.0 :
            dlg = wx.MessageDialog(self, _(u"Confirmez-vous pour ce règlement la facturation de frais de gestion d'un montant de %.2f %s ?") % (donneesFrais[0], SYMBOLE), _(u"Avertissement"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                DB.Close()
                return False

        # --- Sauvegarde du règlement ---
        listeDonnees = [    
                ("IDcompte_payeur", self.IDcompte_payeur),
                ("date", date),
                ("IDmode", IDmode),
                ("IDemetteur", IDemetteur),
                ("numero_piece", numero_piece),
                ("montant", montant),
                ("IDpayeur", IDpayeur),
                ("observations", observations),
                ("numero_quittancier", numero_quittancier),
                ("IDcompte", IDcompte),
                ("date_differe", date_differe),
                ("encaissement_attente", encaissement_attente),
                ("date_saisie", date_saisie),
                ("IDutilisateur", IDutilisateur),
            ]
        if self.IDreglement == None :
            self.nouveauReglement = True
            self.IDreglement = DB.ReqInsert("reglements", listeDonnees)
        else:
            self.nouveauReglement = False
            DB.ReqMAJ("reglements", listeDonnees, "IDreglement", self.IDreglement)
        
        # --- Sauvegarde de la ventilation ---
        self.ctrl_ventilation.Sauvegarde(self.IDreglement, DB)
        
        # --- Sauvegarde les frais de gestion ---
        montantFrais, labelFrais, IDprestationFrais = donneesFrais
        
        # Si ajout d'un frais
        if montantFrais != None and montantFrais != 0.0 :
            listeDonnees = [    
                    ("IDcompte_payeur", self.IDcompte_payeur),
                    ("date", date),
                    ("categorie", "autre"),
                    ("label", labelFrais),
                    ("montant_initial", montantFrais),
                    ("montant", montantFrais),
                    ("IDfamille", IDfamille),
                    ("reglement_frais", self.IDreglement),
                ]
            if IDprestationFrais == None :
                listeDonnees.append(("date_valeur", str(datetime.date.today())))
                IDprestationFrais = DB.ReqInsert("prestations", listeDonnees)
            else:
                DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestationFrais)
                DB.ReqDEL("ventilation", "IDprestation", IDprestationFrais)
        
        # Si suppression d'un frais
        if montantFrais == None and IDprestationFrais != None :
            DB.ReqDEL("prestations", "IDprestation", IDprestationFrais)
            DB.ReqDEL("ventilation", "IDprestation", IDprestationFrais)
        
        DB.Close() 
        
        # --- Mémorise l'action dans l'historique ---
        if self.nouveauReglement == True :
            IDcategorie = 6
            categorie = "Saisie"
        else:
            IDcategorie = 7
            categorie = "Modification"
        texteMode = self.ctrl_mode.GetStringSelection() 
        if IDemetteur != None :
            texteEmetteur = self.ctrl_emetteur.GetStringSelection() 
        else:
            texteEmetteur = u""
        if self.ctrl_numero.GetValue() != "" :
            texteNumpiece = u" n°%s" % self.ctrl_numero.GetValue()
        else:
            texteNumpiece = u""
        if texteEmetteur == "" and texteNumpiece == "" :
            texteDetail = u""
        else:
            texteDetail = u"- %s%s - " % (texteEmetteur, texteNumpiece)
        montant = u"%.2f %s" % (self.ctrl_montant.GetMontant(), SYMBOLE)
        textePayeur = self.ctrl_payeur.GetStringSelection()  
        UTILS_Historique.InsertActions([{
            "IDfamille" : IDfamille,
            "IDcategorie" : IDcategorie, 
            "action" : _(u"%s du règlement ID%d : %s en %s %spayé par %s") % (categorie, self.IDreglement, montant, texteMode, texteDetail, textePayeur),
            },])
        
        return True
        
    def OnClose(self, event):
        self.MemoriseTailleFenetre() 
        event.Skip() 
        
    def MemoriseTailleFenetre(self):
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        UTILS_Config.SetParametre("taille_fenetre_reglement", taille_fenetre)

    def ImportationDernierReglement(self):
        DB = GestionDB.DB()
        req = """SELECT IDmode, IDemetteur, IDpayeur
        FROM reglements
        WHERE IDcompte_payeur=%d
        ORDER BY IDreglement DESC
        LIMIT 1
        ;""" % self.IDcompte_payeur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDmode, IDemetteur, IDpayeur = listeDonnees[0]
        self.ctrl_mode.SetID(IDmode)
        self.OnChoixMode(None)
        if self.ctrl_emetteur.IsEnabled() == True :
            self.ctrl_emetteur.SetID(IDemetteur)
            self.OnChoixEmetteur(None)
        self.ctrl_payeur.SetID(IDpayeur)
    
    def SelectionneFacture(self, IDfacture=None, liste_IDfacture=[]):
        if len(liste_IDfacture) > 0 :
            for ID in liste_IDfacture :
                self.ctrl_ventilation.SelectionneFacture(ID)
        if IDfacture != None :
            self.ctrl_ventilation.SelectionneFacture(IDfacture)
        montant = self.ctrl_ventilation.ctrl_ventilation.GetTotalVentile()
        self.ctrl_ventilation.SetMontantReglement(montant)
        self.ctrl_montant.SetMontant(montant)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    dialog_1 = Dialog(None, IDcompte_payeur=71, IDreglement=None)
    print("Temps de chargement =", time.time() - heure_debut)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
