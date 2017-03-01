#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Droits
import wx.lib.agw.hyperlink as Hyperlink
from Crypto.Hash import SHA256


LISTE_IMAGES = [

    [_(u"Hommes"), [
        (_(u"Homme 1"), "Homme1"),
        (_(u"Homme 2"), "Hommechic"),
        (_(u"Pilote"), "Hommepilote"),
        (_(u"Barbare"), "Barbare"),
        (_(u"Cowboy"), "Cowboy"),
        (_(u"Mari�"), "Marie"),
        (_(u"P�re No�l"), "Perenoel"),
        (_(u"Ouvrier"), "Ouvrier"),
        (_(u"Gar�on"), "Garcon"),
        ]],
        
    [_(u"Femmes"), [
        (_(u"Femme 1"), "Femme1"),
        (_(u"Femme 2"), "Femme2"),
        (_(u"Femme 3"), "Femme3"),
        (_(u"Cowgirl"), "Cowgirl"),
        (_(u"Viking"), "Viking"),
        (_(u"Mari�e"), "Mariee"),
        (_(u"Pilote"), "Femmepilote"),
        (_(u"Secr�taire"), "Femmesecretaire"),
        (_(u"M�re No�l"), "Merenoel"),
        (_(u"Ouvri�re"), "Ouvriere"),
        (_(u"Fille"), "Fille"),
        ]],
        
    [_(u"Animaux"), [
        (_(u"Oiseau 1"), "Oiseau1"),
        (_(u"Oiseau 2"), "Oiseau2"),
        (_(u"Oiseau 3"), "Oiseau3"),
        (_(u"Poisson"), "Poisson1"),
        (_(u"Lion"), "Lion"),
        ]],

    [_(u"Sports"), [
        (_(u"Basket-ball"), "Basket"),
        (_(u"Rugby"), "Rugby"),
        (_(u"Tennis"), "Tennis"),
        (_(u"Foot-ball"), "Foot"),
        ]],

    [_(u"Abstrait"), [
        (_(u"Abstrait 1"), "Abstrait1"),
        (_(u"Abstrait 2"), "Abstrait2"),
        (_(u"Abstrait 3"), "Abstrait3"),
        (_(u"Abstrait 4"), "Abstrait4"),
        ]],

    [_(u"Divers"), [
        (_(u"Bonhomme de neige"), "Bonhommedeneige"),
        (_(u"Boussole"), "Boussole"),
        (_(u"Cadeau"), "Cadeau"),
        (_(u"Chine"), "Chine"),
        ]],

    ]




class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
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
        self.parent.ctrl_image.ContextMenu()
        self.UpdateLink()


# ---------------------------------------------------------------------------------------------------------------------------------

class CTRL_Image(wx.StaticBitmap):
    def __init__(self, parent, nomImage="Automatique", style=wx.SUNKEN_BORDER):
        wx.StaticBitmap.__init__(self, parent, id=-1, style=style)
        self.parent = parent
        self.tailleImage = (128, 128)
        self.nomImage = nomImage
        self.SetMinSize(self.tailleImage) 
        self.SetSize(self.tailleImage) 
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.SetToolTipString(_(u"Cliquez sur le bouton droit de votre souris\npour s�lectionner un avatar"))
        
        self.Bind(wx.EVT_LEFT_DOWN, self.ContextMenu)
        self.Bind(wx.EVT_RIGHT_DOWN, self.ContextMenu)
        
        self.MAJ() 

    def ContextMenu(self, event=None):
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()
        
        # Automatique
        item = wx.MenuItem(menuPop, 999, _(u"Automatique (D�faut)"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnItemMenu, id=999)
        
        menuPop.AppendSeparator()
                    
        # Item Modifier
        tailleImage = (60, 60)
        numCategorie = 1000
        for labelSousMenu, listeItems in LISTE_IMAGES :
            
            sousMenu = wx.Menu()
            numItem = 0
            for label, nomImage in listeItems :
                id = numCategorie + numItem
                item = wx.MenuItem(menuPop, id, label)
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Avatars/128x128/%s.png" % nomImage), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(self.ConvertTailleImage(bmp, tailleImage))
                sousMenu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnItemMenu, id=id)
                numItem += 1
        
            menuPop.AppendMenu(numCategorie, labelSousMenu, sousMenu)
            numCategorie += 1000

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def OnItemMenu(self, event):
        id = event.GetId() 
        if id == 999 :
            nomImage = "automatique"
        else :
            numCategorie = int((str(id))[0]) - 1
            numItem = id - ((numCategorie+1)*1000)
            nomImage = LISTE_IMAGES[numCategorie][1][numItem][1]
        self.SetImage(nomImage)
    
    def MAJ(self):
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Avatars/128x128/%s.png" % self.nomImage), wx.BITMAP_TYPE_PNG)
        self.SetBitmap(bmp)
        
    def ConvertTailleImage(self, bitmap=None, taille=None):
        """ Convertit la taille d'une image """
        # R�duction de l'image
        bitmap = bitmap.ConvertToImage()
        bitmap = bitmap.Rescale(width=taille[0], height=taille[1], quality=wx.IMAGE_QUALITY_HIGH) 
        bitmap = bitmap.ConvertToBitmap()
        
        # Insertion de l'image sur un fond noir
        img = wx.EmptyImage(taille[0], taille[1], True)
        img.SetRGBRect((0, 0, taille[0], taille[1]), 0, 0, 0)
        bmp = img.ConvertToBitmap()
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.DrawBitmap(bitmap, taille[0]/2.0-bitmap.GetSize()[0]/2.0, taille[1]/2.0-bitmap.GetSize()[1]/2.0)
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def SetImage(self, nomImage="Automatique"):
        if nomImage == None :
            nomImage = "Automatique"
        self.nomImage = nomImage
        self.MAJ() 
        
    def GetImage(self):
        return self.nomImage
    
    
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Modeles_droits(wx.Choice):
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
        req = """SELECT IDmodele, nom, observations
        FROM modeles_droits ORDER BY nom; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDmodele, nom, observations in listeDonnees :
            listeItems.append(nom)
            self.dictDonnees[index] = IDmodele
            index += 1
        return listeItems

    def SetID(self, IDmodele=None):
        for index, IDmodeleTemp in self.dictDonnees.iteritems() :
            if IDmodeleTemp == IDmodele :
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.dictDonnees[index]

# -------------------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent, IDutilisateur=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.IDutilisateur = IDutilisateur
        self.mdp = None
        self.mdpcrypt = None
        
        # Identit�
        self.staticbox_identite_staticbox = wx.StaticBox(self, -1, _(u"Identit�"))
        self.label_sexe = wx.StaticText(self, -1, _(u"Sexe :"))
        self.ctrl_sexe = wx.Choice(self, -1, choices=[_(u"Homme"), _(u"Femme")])
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_prenom = wx.StaticText(self, -1, _(u"Pr�nom :"))
        self.ctrl_prenom = wx.TextCtrl(self, -1, u"")
        
        # Image
        self.staticbox_image_staticbox = wx.StaticBox(self, -1, _(u"Avatar"))
        self.ctrl_image = CTRL_Image(self)
        self.hyper_image = Hyperlien(self, label=_(u"Choisir un avatar"), infobulle=_(u"Cliquez ici pour modifier l'avatar de l'utilisateur"), URL="")
        
        # Acc�s
        self.staticbox_acces_staticbox = wx.StaticBox(self, -1, _(u"Acc�s"))
        self.ctrl_actif = wx.CheckBox(self, -1, u"Utilisateur actif")
        self.ctrl_actif.SetValue(True)
        self.bouton_modif_mdp = CTRL_Bouton_image.CTRL(self, texte="", cheminImage="Images/32x32/Cle.png")
        
        # Droits
        self.staticbox_droits_staticbox = wx.StaticBox(self, -1, _(u"Droits"))
        self.radio_droits_admin = wx.RadioButton(self, -1, _(u"Administrateur"), style=wx.RB_GROUP)
        self.radio_droits_modele = wx.RadioButton(self, -1, _(u"Le mod�le de droits suivant :"))
        self.ctrl_modele_droits = CTRL_Modeles_droits(self)
        self.radio_droits_perso = wx.RadioButton(self, -1, _(u"Les droits personnalis�s suivants :"))
        self.ctrl_droits = CTRL_Droits.CTRL(self, IDutilisateur=self.IDutilisateur)
        self.ctrl_droits.MAJ()
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifMdp, self.bouton_modif_mdp)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDroits, self.radio_droits_admin)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDroits, self.radio_droits_modele)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDroits, self.radio_droits_perso)
        
        if self.IDutilisateur == None :
            self.SetTitle(_(u"Saisie d'un utilisateur"))
        else:
            self.SetTitle(_(u"Modification d'un utilisateur"))
            self.Importation()
        
        self.OnRadioDroits(None)
        self.MAJboutonMdp()

    def __set_properties(self):
        self.ctrl_sexe.SetToolTipString(_(u"S�lectionnez le sexe de l'utilisateur"))
        self.ctrl_sexe.SetSelection(0)
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom de famille de l'utilisateur"))
        self.ctrl_prenom.SetToolTipString(_(u"Saisissez ici le pr�nom de l'utilisateur"))
        self.radio_droits_admin.SetToolTipString(_(u"S�lectionnez l'option 'Administrateur' pour donner tous les droits � cet utilisateur"))
        self.radio_droits_modele.SetToolTipString(_(u"S�lectionnez cette option pour attribuer un mod�le de droits � cet utilisateur"))
        self.radio_droits_perso.SetToolTipString(_(u"S�lectionnez cette option pour attribuer des droits personnalis�s � cet utilisateur"))
        self.ctrl_actif.SetToolTipString(_(u"D�cochez cette case pour d�sactiver l'utilisateur. L'utilisateur n'aura plus acc�s � ce fichier de donn�es."))
        self.bouton_modif_mdp.SetToolTipString(_(u"Cliquez ici pour saisir un nouveau mot de passe pour cet utilisateur"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((690, 750))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_haut_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Identit�
        staticbox_identite = wx.StaticBoxSizer(self.staticbox_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        grid_sizer_identite.Add(self.label_sexe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_sexe, 0, 0, 0)
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        
        grid_sizer_identite.AddGrowableCol(1)
        staticbox_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut_gauche.Add(staticbox_identite, 1, wx.EXPAND, 0)
        
        # Acc�s
        staticbox_acces = wx.StaticBoxSizer(self.staticbox_acces_staticbox, wx.VERTICAL)
        self.grid_sizer_acces = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        self.grid_sizer_acces.Add(self.ctrl_actif, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_sizer_acces.Add( (5, 5), 0, wx.EXPAND, 0)
        self.grid_sizer_acces.Add(self.bouton_modif_mdp, 0, 0, 0)
        self.grid_sizer_acces.AddGrowableCol(1)

        staticbox_acces.Add(self.grid_sizer_acces, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut_gauche.Add(staticbox_acces, 1, wx.EXPAND, 0)
        grid_sizer_haut_gauche.AddGrowableCol(0)
        
        grid_sizer_haut.Add(grid_sizer_haut_gauche, 1, wx.EXPAND, 0)
        
        # Image
        staticbox_image = wx.StaticBoxSizer(self.staticbox_image_staticbox, wx.VERTICAL)
        staticbox_image.Add(self.ctrl_image, 0, wx.ALL|wx.EXPAND, 10)
        staticbox_image.Add(self.hyper_image, 0, wx.ALIGN_CENTER|wx.ALL, 0)
        grid_sizer_haut.Add(staticbox_image, 1, wx.EXPAND, 0)
        
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL|wx.EXPAND, 10)
        
        # Droits
        staticbox_droits = wx.StaticBoxSizer(self.staticbox_droits_staticbox, wx.VERTICAL)
        grid_sizer_droits = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_droits.Add(self.radio_droits_admin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_droits.Add(self.radio_droits_modele, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_droits.Add(self.ctrl_modele_droits, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_droits.Add(self.radio_droits_perso, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_droits.Add(self.ctrl_droits, 1, wx.LEFT|wx.EXPAND, 20)
        
        grid_sizer_droits.AddGrowableCol(0)
        grid_sizer_droits.AddGrowableRow(4)
        staticbox_droits.Add(grid_sizer_droits, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_droits, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Commandes
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.CenterOnScreen()

    def MAJboutonMdp(self, event=None):
        if self.mdpcrypt == None :
            texte = _(u"Saisir le mot de passe")
        else :
            texte = _(u"Modifier le mot de passe")
        self.bouton_modif_mdp.SetTexte(texte)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Utilisateurs")

    def OnRadioDroits(self, event):
        self.ctrl_modele_droits.Enable(self.radio_droits_modele.GetValue())
        self.ctrl_droits.Enable(self.radio_droits_perso.GetValue())
        if self.radio_droits_perso.GetValue() == True :
            self.ctrl_droits.SetModeDisable(False)
        else :
            if self.ctrl_droits.modeDisable == False :
                self.ctrl_droits.SetModeDisable(True)

    def OnBoutonModifMdp(self, event):
        if self.mdpcrypt == None :
            titre = _(u"Saisie du mot de passe")
            intro = _(u"Veuillez saisir un mot de passe :")
        else :
            titre = _(u"Modification du mot de passe")
            intro = _(u"Veuillez saisir un nouveau mot de passe :")
        dlg = DLG_Saisie_mdp(self, titre=titre, intro=intro)
        if dlg.ShowModal() == wx.ID_OK:
            self.mdp = dlg.GetMdp()
            self.mdpcrypt = dlg.GetMdpCrypt()
        dlg.Destroy()
        self.MAJboutonMdp()
        self.grid_sizer_acces.Layout()

    def OnBoutonOk(self, event): 
        # V�rification des donn�es
        if len(self.ctrl_nom.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if self.mdpcrypt == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un mot de passe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que le code d'acc�s n'est pas d�j� utilis�
        if self.IDutilisateur == None :
            IDutilisateurTmp = 0
        else:
            IDutilisateurTmp = self.IDutilisateur
        DB = GestionDB.DB()
        req = """SELECT IDutilisateur, sexe, nom, prenom, mdp, mdpcrypt, profil, actif
        FROM utilisateurs 
        WHERE mdpcrypt='%s' AND IDutilisateur<>%d
        ;""" % (self.mdpcrypt, IDutilisateurTmp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Le code d'acc�s que vous avez saisi est d�j� attribu� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # V�rifie qu'il reste au moins un administrateur dans la base de donn�es
        if self.radio_droits_admin.GetValue() == False :
            DB = GestionDB.DB()
            req = """SELECT IDutilisateur, profil
            FROM utilisateurs
            WHERE profil='administrateur' AND IDutilisateur!=%d;""" % IDutilisateurTmp
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                dlg = wx.MessageDialog(self, _(u"Il doit rester au moins un administrateur dans le fichier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # V�rifie qu'il reste au moins un administrateur ACTIF dans la base de donn�es
        if self.ctrl_actif.GetValue() == False :
            DB = GestionDB.DB()
            req = """SELECT IDutilisateur, profil, actif
            FROM utilisateurs
            WHERE profil='administrateur' AND actif=1 AND IDutilisateur!=%d;""" % IDutilisateurTmp
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                dlg = wx.MessageDialog(self, _(u"Il doit rester au moins un administrateur ACTIF dans le fichier ! Cochez la case Actif."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Droits
        if self.radio_droits_modele.GetValue() == True :
            if self.ctrl_modele_droits.GetID() == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun mod�le de droits !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
                
        # Sauvegarde
        self.Sauvegarde()
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def GetIDutilisateur(self):
        return self.IDutilisateur

    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT sexe, nom, prenom, mdp, mdpcrypt, profil, actif, image
        FROM utilisateurs 
        WHERE IDutilisateur=%d;""" % self.IDutilisateur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        sexe, nom, prenom, mdp, mdpcrypt, profil, actif, image = listeDonnees[0]
        # Identit�
        if sexe == "M" :
            self.ctrl_sexe.Select(0)
        else:
            self.ctrl_sexe.Select(1)
        self.ctrl_nom.SetValue(nom)
        self.ctrl_prenom.SetValue(prenom)
        # Acc�s
        self.mdp = mdp
        self.mdpcrypt = mdpcrypt
        if actif == 1 :
            self.ctrl_actif.SetValue(True)
        else:
            self.ctrl_actif.SetValue(False)
        # Droits
        if profil != None :
            if profil.startswith("administrateur") :
                self.radio_droits_admin.SetValue(True) 
            if profil.startswith("modele") :
                self.radio_droits_modele.SetValue(True) 
                IDmodele = int(profil.split(":")[1])
                self.ctrl_modele_droits.SetID(IDmodele)
            if profil.startswith("perso") :
                self.radio_droits_perso.SetValue(True)
        # Avatar
        self.ctrl_image.SetImage(image)
        
        

    def Sauvegarde(self):
        """ Sauvegarde """
        # Identit�
        if self.ctrl_sexe.GetSelection() == 0 :
            sexe = "M"
        else:
            sexe = "F"
        nom = self.ctrl_nom.GetValue() 
        prenom = self.ctrl_prenom.GetValue() 
        
        # Acc�s
        if self.ctrl_actif.GetValue() == True :
            actif = 1
        else:
            actif = 0
            
        # Droits
        if self.radio_droits_admin.GetValue() == True : 
            profil = "administrateur"
        if self.radio_droits_modele.GetValue() == True : 
            profil = "modele:%d" % self.ctrl_modele_droits.GetID() 
        if self.radio_droits_perso.GetValue() == True : 
            profil = "perso"
        
        # Avatar
        nomImage = self.ctrl_image.GetImage()
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("sexe", sexe),
                ("nom", nom),
                ("prenom", prenom),
                ("mdp", self.mdp),
                ("mdpcrypt", self.mdpcrypt),
                ("profil", profil),
                ("actif", actif),
                ("image", nomImage),
            ]
        if self.IDutilisateur == None :
            self.IDutilisateur = DB.ReqInsert("utilisateurs", listeDonnees)
        else:
            DB.ReqMAJ("utilisateurs", listeDonnees, "IDutilisateur", self.IDutilisateur)
        DB.Close()
    
        # Droits
        self.ctrl_droits.Sauvegarde(IDutilisateur=self.IDutilisateur)


# --------------------------- DLG de saisie du nouveau mot de passe ----------------------------

class DLG_Saisie_mdp(wx.Dialog):
    def __init__(self, parent, titre="", intro=""):
        wx.Dialog.__init__(self, parent, id=-1, name="DLG_nouveau_mdp_utilisateur")
        self.parent = parent
        self.SetTitle(titre)

        self.staticbox = wx.StaticBox(self, -1, "")
        self.label = wx.StaticText(self, -1, intro)
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.label_confirmation = wx.StaticText(self, -1, _(u"Confirmation :"))
        self.ctrl_confirmation = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        self.ctrl_mdp.SetFocus()

    def __set_properties(self):
        self.ctrl_mdp.SetToolTipString(_(u"Saisissez un mot de passe"))
        self.ctrl_confirmation.SetToolTipString(_(u"Confirmez le mot de passe en le saisissant une nouvelle fois"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.ctrl_mdp.SetMinSize((300, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        # Intro
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)

        # Staticbox
        staticbox = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_confirmation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_confirmation, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def GetMdpCrypt(self):
        return SHA256.new(self.ctrl_mdp.GetValue().encode('utf-8')).hexdigest()

    def GetMdp(self):
        return self.ctrl_mdp.GetValue()

    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """
        if len(self.ctrl_mdp.GetValue()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un mot de passe valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_mdp.SetFocus()
            return False

        if len(self.ctrl_confirmation.GetValue()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir la confirmation du mot de passe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_confirmation.SetFocus()
            return False

        if self.ctrl_mdp.GetValue() != self.ctrl_confirmation.GetValue():
            dlg = wx.MessageDialog(self, _(u"La confirmation du mot de passe ne correspond pas au mot de passe saisi !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_confirmation.SetFocus()
            return False

        # Fermeture
        self.EndModal(wx.ID_OK)





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDutilisateur=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
