#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import decimal
import wx.lib.agw.hyperlink as Hyperlink

import CTRL_Bandeau
import CTRL_Saisie_date

import GestionDB
import OL_Solder_impayes
import UTILS_Identification

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")




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
        if self.URL == "tout" :
            self.parent.ctrl_prestations.CocheTout() 
        if self.URL == "rien" :
            self.parent.ctrl_prestations.CocheRien() 
        self.UpdateLink()


# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.SetDefaut() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne
        FROM comptes_bancaires
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne in listeDonnees :
            self.dictDonnees[index] = { 
                "ID" : IDcompte, "nom" : nom, "numero" : numero, "defaut" : defaut,
                "raison" : raison, "code_etab" : code_etab, "code_guichet" : code_guichet, 
                "code_nne" : code_nne, 
                }
            listeItems.append(nom)
            index += 1
        return listeItems
    
    def SetDefaut(self):
        for index, dictTemp in self.dictDonnees.iteritems() :
            if dictTemp["code_nne"] not in (None, "") :
                self.SetID(dictTemp["ID"])
                return

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfos(self):
        """ Récupère les infos sur le compte sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Mode(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
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
        for index, values in self.dictDonnees.iteritems():
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

class CTRL_Emetteur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDmode = None
        self.MAJ() 
    
    def MAJ(self, IDmode=None):
        self.IDmode = IDmode
        listeItems = self.GetListeDonnees()
        if len(listeItems) < 2 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        if self.IDmode == None :
            return []
        db = GestionDB.DB()
        req = """SELECT IDemetteur, IDmode, nom
        FROM emetteurs
        WHERE IDmode=%d
        ORDER BY nom;""" % self.IDmode
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = ["",]
        self.dictDonnees = { 0 : { "ID" : None, "nom" : "", "IDmode" : None } }
        index = 1
        for IDemetteur, IDmode, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDemetteur, "nom" : nom, "IDmode" : IDmode }
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfosEmetteur(self):
        """ Récupère les infos sur l'émetteur sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   

        # Bandeau
        titre = u"Solder les impayés"
        intro = u"Cette fonctionnalité vous permet de laisser Noethys créer des règlements pour les prestations impayées d'une période donnée. Utile pour remettre les comptes à zéro par exemple."
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Impayes.png")

        # Règlement
        self.box_reglement_staticbox = wx.StaticBox(self, -1, u"Paramètres des règlements")
        self.label_compte = wx.StaticText(self, -1, u"Compte :")
        self.ctrl_compte = CTRL_Compte(self)
        self.bouton_compte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.label_mode = wx.StaticText(self, -1, u"Mode :")
        self.ctrl_mode = CTRL_Mode(self)
        self.bouton_mode = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.label_emetteur = wx.StaticText(self, -1, u"Emetteur :")
        self.ctrl_emetteur = CTRL_Emetteur(self)
        self.bouton_emetteur = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        # Prestations
        self.box_prestations_staticbox = wx.StaticBox(self, -1, u"Sélection des prestations")
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, "au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.bouton_actualiser = wx.Button(self, -1, u"Actualiser la liste")
        
        self.ctrl_prestations = OL_Solder_impayes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_recherche = OL_Solder_impayes.BarreRecherche(self)
        
        self.hyper_tout = Hyperlien(self, label=u"Tout cocher", infobulle=u"Cliquez ici pour tout cocher", URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=u"Tout décocher", infobulle=u"Cliquez ici pour tout décocher", URL="rien")
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixMode, self.ctrl_mode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCompte, self.bouton_compte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMode, self.bouton_mode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmetteur, self.bouton_emetteur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        self.ctrl_prestations.MAJ() 
        wx.CallLater(0, self.Layout)

    def __set_properties(self):
        self.ctrl_compte.SetToolTipString(u"Sélectionnez un compte bancaire à créditer")
        self.bouton_compte.SetToolTipString(u"Cliquez ici pour accéder à la gestion des comptes bancaires")
        self.ctrl_mode.SetToolTipString(u"Sélectionnez un mode de règlement")
        self.bouton_mode.SetToolTipString(u"Cliquez ici pour accéder à la gestion des modes de règlements")
        self.ctrl_emetteur.SetToolTipString(u"Sélectionnez un émetteur de règlement")
        self.bouton_emetteur.SetToolTipString(u"Cliquez ici pour accéder à la gestion des modes de règlements")
        self.ctrl_date_debut.SetToolTipString(u"Saisissez une date de début")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez une date de fin")
        self.bouton_actualiser.SetToolTipString(u"Cliquez ici pour actualiser la liste")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((530, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Règlement
        box_reglement = wx.StaticBoxSizer(self.box_reglement_staticbox, wx.VERTICAL)
        grid_sizer_reglement = wx.FlexGridSizer(rows=3, cols=3, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_reglement.Add(self.label_compte, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reglement.Add(self.ctrl_compte, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reglement.Add(self.bouton_compte, 0, 0, 0)
        grid_sizer_reglement.Add(self.label_mode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reglement.Add(self.ctrl_mode, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reglement.Add(self.bouton_mode, 0, 0, 0)
        grid_sizer_reglement.Add(self.label_emetteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reglement.Add(self.ctrl_emetteur, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reglement.Add(self.bouton_emetteur, 0, 0, 0)
        grid_sizer_reglement.AddGrowableCol(1)
        box_reglement.Add(grid_sizer_reglement, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_reglement, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Prestations
        box_prestations = wx.StaticBoxSizer(self.box_prestations_staticbox, wx.VERTICAL)
        grid_sizer_prestations = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add((20, 20), 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_actualiser, 1, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableCol(5)
        grid_sizer_prestations.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_prestations.Add(self.ctrl_prestations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_options.Add((20, 20), 0, 0, 0)
        grid_sizer_options.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_prestations.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_prestations.AddGrowableRow(1)
        grid_sizer_prestations.AddGrowableCol(0)
        box_prestations.Add(grid_sizer_prestations, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(box_prestations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonCompte(self, event): 
        IDcompte = self.ctrl_compte.GetID()
        import DLG_Comptes_bancaires
        dlg = DLG_Comptes_bancaires.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_compte.MAJ()
        self.ctrl_compte.SetID(IDcompte)

    def OnBoutonMode(self, event):
        IDmode = self.ctrl_mode.GetID()
        import DLG_Modes_reglements
        dlg = DLG_Modes_reglements.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_mode.MAJ()
        self.ctrl_mode.SetID(IDmode)

    def OnBoutonEmetteur(self, event): 
        IDemetteur = self.ctrl_emetteur.GetID()
        import DLG_Emetteurs
        dlg = DLG_Emetteurs.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_emetteur.MAJ()
        self.ctrl_emetteur.SetID(IDemetteur)
    
    def OnChoixMode(self, event=None):
        IDmode = self.ctrl_mode.GetID() 
        self.ctrl_emetteur.MAJ(IDmode)
        

    def OnBoutonActualiser(self, event): 
        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de début !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus() 
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date de fin !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus() 
            return False
        
        self.ctrl_prestations.SetPeriode(date_debut, date_fin)
        self.ctrl_prestations.MAJ() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Solderlesimpays")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)        
        
    def OnBoutonOk(self, event): 
        # compte
        IDcompte = self.ctrl_compte.GetID() 
        if IDcompte == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un compte à créditer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Mode
        IDmode = self.ctrl_mode.GetID() 
        if IDmode == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un mode de règlement !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Emetteur
        IDemetteur = self.ctrl_emetteur.GetID() 
        
        # Tracks
        tracks = self.ctrl_prestations.GetTracksCoches() 
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez cocher au moins une ligne dans la liste !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Confirmation
        montantTotal = decimal.Decimal(0.0)
        for track in tracks : 
            montantTotal += track.impaye
        dlg = wx.MessageDialog(self, u"Confirmez-vous la création automatique de %d règlements pour un total de %.2f %s ?" % (len(tracks), montantTotal, SYMBOLE), u"Demande de confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False
        
        # ----------------------------- Création des règlements -----------------------------------------------------------
        DB = GestionDB.DB()
        
        # Recherche des payeurs
        req = """SELECT IDpayeur, IDcompte_payeur, nom
        FROM payeurs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPayeurs = {}
        for IDpayeur, IDcompte_payeur, nom in listeDonnees :
            if dictPayeurs.has_key(IDcompte_payeur) == False :
                dictPayeurs[IDcompte_payeur] = []
            dictPayeurs[IDcompte_payeur].append({"nom" : nom, "IDpayeur" : IDpayeur})

                                
        # Sauvegarde des règlements + ventilation
        for track in tracks :
                
            # Recherche du payeur
            IDpayeur = None
            if dictPayeurs.has_key(track.IDcompte_payeur) :
                IDpayeur = dictPayeurs[track.IDcompte_payeur][0]["IDpayeur"]
            else :
                nomTitulaire = u"%s %s" % (track.listeTitulaires[0]["nom"], track.listeTitulaires[0]["prenom"])
                IDpayeur = DB.ReqInsert("payeurs", [("IDcompte_payeur", track.IDcompte_payeur), ("nom", nomTitulaire)])
                
            # Création des données à sauvegarder
            listeDonnees = [
                ("IDcompte_payeur", track.IDcompte_payeur),
                ("date", str(datetime.date.today())),
                ("IDmode", IDmode),
                ("IDemetteur", IDemetteur),
                ("numero_piece", None),
                ("montant", float(track.impaye)),
                ("IDpayeur", IDpayeur),
                ("observations", u"Règlement créé avec la fonction 'Solder les impayés'"),
                ("numero_quittancier", None),
                ("IDcompte", IDcompte),
                ("date_differe", None),
                ("encaissement_attente", 0),
                ("date_saisie", str(datetime.date.today())),
                ("IDutilisateur", UTILS_Identification.GetIDutilisateur() ),
                ]
            
            # Ajout
            IDreglement = DB.ReqInsert("reglements", listeDonnees)
                            
            # ----------- Sauvegarde de la ventilation ---------
            for dictPrestation in track.listePrestations :
                listeDonnees = [    
                        ("IDreglement", IDreglement),
                        ("IDcompte_payeur", track.IDcompte_payeur),
                        ("IDprestation", dictPrestation["IDprestation"]),
                        ("montant", float(dictPrestation["impaye"])),
                    ]
                IDventilation = DB.ReqInsert("ventilation", listeDonnees)        
                    
        DB.Close() 

        dlg = wx.MessageDialog(self, u"Les %d règlements ont été créés avec succès." % len(tracks), u"Confirmation", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        # Fermeture
        self.EndModal(wx.ID_OK)
        
        
        

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ctrl_date_debut.SetDate(datetime.date(2013, 1, 1))
    dlg.ctrl_date_fin.SetDate(datetime.date(2013, 12, 31))
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
