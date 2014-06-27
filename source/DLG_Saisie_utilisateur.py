#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import CTRL_Droits
import wx.lib.agw.hyperlink as Hyperlink



LISTE_IMAGES = [

    [u"Hommes", [
        (u"Homme 1", "Homme1"),
        (u"Homme 2", "Hommechic"),
        (u"Pilote", "Hommepilote"),
        (u"Barbare", "Barbare"),
        (u"Cowboy", "Cowboy"),
        (u"Marié", "Marie"),
        (u"Père Noël", "Perenoel"),
        (u"Ouvrier", "Ouvrier"),
        (u"Garçon", "Garcon"),
        ]],
        
    [u"Femmes", [
        (u"Femme 1", "Femme1"),
        (u"Femme 2", "Femme2"),
        (u"Femme 3", "Femme3"),
        (u"Cowgirl", "Cowgirl"),
        (u"Viking", "Viking"),
        (u"Mariée", "Mariee"),
        (u"Pilote", "Femmepilote"),
        (u"Secrétaire", "Femmesecretaire"),
        (u"Mère Noël", "Merenoel"),
        (u"Ouvrière", "Ouvriere"),
        (u"Fille", "Fille"),
        ]],
        
    [u"Animaux", [
        (u"Oiseau 1", "Oiseau1"),
        (u"Oiseau 2", "Oiseau2"),
        (u"Oiseau 3", "Oiseau3"),
        (u"Poisson", "Poisson1"),
        (u"Lion", "Lion"),
        ]],

    [u"Sports", [
        (u"Basket-ball", "Basket"),
        (u"Rugby", "Rugby"),
        (u"Tennis", "Tennis"),
        (u"Foot-ball", "Foot"),
        ]],

    [u"Abstrait", [
        (u"Abstrait 1", "Abstrait1"),
        (u"Abstrait 2", "Abstrait2"),
        (u"Abstrait 3", "Abstrait3"),
        (u"Abstrait 4", "Abstrait4"),
        ]],

    [u"Divers", [
        (u"Bonhomme de neige", "Bonhommedeneige"),
        (u"Boussole", "Boussole"),
        (u"Cadeau", "Cadeau"),
        (u"Chine", "Chine"),
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
        self.SetToolTipString(u"Cliquez sur le bouton droit de votre souris\npour sélectionner un avatar")
        
        self.Bind(wx.EVT_LEFT_DOWN, self.ContextMenu)
        self.Bind(wx.EVT_RIGHT_DOWN, self.ContextMenu)
        
        self.MAJ() 

    def ContextMenu(self, event=None):
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        # Automatique
        item = wx.MenuItem(menuPop, 999, u"Automatique (Défaut)")
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
                bmp = wx.Bitmap("Images/Avatars/128x128/%s.png" % nomImage, wx.BITMAP_TYPE_PNG)
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
        bmp = wx.Bitmap("Images/Avatars/128x128/%s.png" % self.nomImage, wx.BITMAP_TYPE_PNG)
        self.SetBitmap(bmp)
        
    def ConvertTailleImage(self, bitmap=None, taille=None):
        """ Convertit la taille d'une image """
        # Réduction de l'image
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
        
        # Identité
        self.staticbox_identite_staticbox = wx.StaticBox(self, -1, u"Identité")
        self.label_sexe = wx.StaticText(self, -1, u"Sexe :")
        self.ctrl_sexe = wx.Choice(self, -1, choices=[u"Homme", u"Femme"])
        self.label_nom = wx.StaticText(self, -1, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_prenom = wx.StaticText(self, -1, u"Prénom :")
        self.ctrl_prenom = wx.TextCtrl(self, -1, u"")
        
        # Image
        self.staticbox_image_staticbox = wx.StaticBox(self, -1, u"Avatar")
        self.ctrl_image = CTRL_Image(self)
        self.hyper_image = Hyperlien(self, label=u"Choisir un avatar", infobulle=u"Cliquez ici pour modifier l'avatar de l'utilisateur", URL="")
        
        # Accès
        self.staticbox_acces_staticbox = wx.StaticBox(self, -1, u"Accès")
        self.label_code = wx.StaticText(self, -1, u"Code :")
        self.ctrl_code = wx.TextCtrl(self, -1, u"")
        self.label_actif = wx.StaticText(self, -1, u"Actif :")
        self.ctrl_actif = wx.CheckBox(self, -1, u"")
        self.ctrl_actif.SetValue(True)
        
        # Droits
        self.staticbox_droits_staticbox = wx.StaticBox(self, -1, u"Droits")
        self.radio_droits_admin = wx.RadioButton(self, -1, u"Administrateur", style=wx.RB_GROUP)
        self.radio_droits_modele = wx.RadioButton(self, -1, u"Le modèle de droits suivant :")
        self.ctrl_modele_droits = CTRL_Modeles_droits(self)
        self.radio_droits_perso = wx.RadioButton(self, -1, u"Les droits personnalisés suivants :")
        self.ctrl_droits = CTRL_Droits.CTRL(self, IDutilisateur=self.IDutilisateur)
        self.ctrl_droits.MAJ()
        
        # Commandes
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDroits, self.radio_droits_admin)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDroits, self.radio_droits_modele)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDroits, self.radio_droits_perso)
        
        if self.IDutilisateur == None :
            self.SetTitle(u"Saisie d'un utilisateur")
        else:
            self.SetTitle(u"Modification d'un utilisateur")
            self.Importation()
        
        self.OnRadioDroits(None)

    def __set_properties(self):
        self.ctrl_sexe.SetToolTipString(u"Sélectionnez le sexe de l'utilisateur")
        self.ctrl_sexe.SetSelection(0)
        self.ctrl_nom.SetToolTipString(u"Saisissez ici le nom de famille de l'utilisateur")
        self.ctrl_prenom.SetToolTipString(u"Saisissez ici le prénom de l'utilisateur")
        self.radio_droits_admin.SetToolTipString(u"Sélectionnez l'option 'Administrateur' pour donner tous les droits à cet utilisateur")
        self.radio_droits_modele.SetToolTipString(u"Sélectionnez cette option pour attribuer un modèle de droits à cet utilisateur")
        self.radio_droits_perso.SetToolTipString(u"Sélectionnez cette option pour attribuer des droits personnalisés à cet utilisateur")
        self.ctrl_actif.SetToolTipString(u"Décochez cette case si l'utilisateur est inactif. L'utilisateur n'aura plus accès à ce fichier de données.")
        self.ctrl_code.SetToolTipString(u"Saisissez ici le code d'accès personnel de l'individu")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((690, 750))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_haut_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Identité
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
        
        # Accès
        staticbox_acces = wx.StaticBoxSizer(self.staticbox_acces_staticbox, wx.VERTICAL)
        grid_sizer_acces = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_acces.Add(self.label_code, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_acces.Add(self.ctrl_code, 0, 0, 0)
        grid_sizer_acces.Add(self.label_actif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_acces.Add(self.ctrl_actif, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        staticbox_acces.Add(grid_sizer_acces, 1, wx.ALL|wx.EXPAND, 10)
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

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Utilisateurs")

    def OnRadioDroits(self, event):
        self.ctrl_modele_droits.Enable(self.radio_droits_modele.GetValue())
        self.ctrl_droits.Enable(self.radio_droits_perso.GetValue())
        if self.radio_droits_perso.GetValue() == True :
            self.ctrl_droits.SetModeDisable(False)
        else :
            if self.ctrl_droits.modeDisable == False :
                self.ctrl_droits.SetModeDisable(True)
        
    def OnBoutonOk(self, event): 
        # Vérification des données
        if len(self.ctrl_nom.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        if len(self.ctrl_code.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un code d'accès personnel !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code.SetFocus()
            return
        
        # Vérifie que le code d'accès n'est pas déjà utilisé
        if self.IDutilisateur == None :
            IDutilisateurTmp = 0
        else:
            IDutilisateurTmp = self.IDutilisateur
        DB = GestionDB.DB()
        req = """SELECT IDutilisateur, sexe, nom, prenom, mdp, profil, actif
        FROM utilisateurs 
        WHERE mdp='%s' AND IDutilisateur<>%d
        ;""" % (self.ctrl_code.GetValue(), IDutilisateurTmp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, u"Le code d'accès que vous avez saisi est déjà attribué !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code.SetFocus()
            return
        
        # Vérifie qu'il reste au moins un administrateur dans la base de données
        if self.radio_droits_admin.GetValue() == False : 
            DB = GestionDB.DB()
            req = """SELECT IDutilisateur, profil
            FROM utilisateurs 
            WHERE profil='administrateur' AND IDutilisateur!=%d;""" % IDutilisateurTmp
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                dlg = wx.MessageDialog(self, u"Il doit rester au moins un administrateur dans le fichier !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Droits
        if self.radio_droits_modele.GetValue() == True :
            if self.ctrl_modele_droits.GetID() == None :
                dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun modèle de droits !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
                
        # Sauvegarde
        self.Sauvegarde()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDutilisateur(self):
        return self.IDutilisateur

    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT sexe, nom, prenom, mdp, profil, actif, image
        FROM utilisateurs 
        WHERE IDutilisateur=%d;""" % self.IDutilisateur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        sexe, nom, prenom, mdp, profil, actif, image = listeDonnees[0]
        # Identité
        if sexe == "M" :
            self.ctrl_sexe.Select(0)
        else:
            self.ctrl_sexe.Select(1)
        self.ctrl_nom.SetValue(nom)
        self.ctrl_prenom.SetValue(prenom)
        # Accès
        self.ctrl_code.SetValue(mdp)
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
        # Identité
        if self.ctrl_sexe.GetSelection() == 0 :
            sexe = "M"
        else:
            sexe = "F"
        nom = self.ctrl_nom.GetValue() 
        prenom = self.ctrl_prenom.GetValue() 
        
        # Accès
        code = self.ctrl_code.GetValue() 
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
                ("mdp", code),
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
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDutilisateur=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
