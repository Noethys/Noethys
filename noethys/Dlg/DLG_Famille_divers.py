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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Utils import UTILS_Utilisateurs
import wx.propgrid as wxpg
import wx.lib.platebtn as platebtn



LISTE_CATEGORIES_TIERS = [
    ("01", _(u"Personne physique")),
    ("20", _(u"Etat ou établissement public national")),
    ("21", _(u"Région")),
    ("22", _(u"Département")),
    ("23", _(u"Commune")),
    ("24", _(u"Groupement de collectivités")),
    ("25", _(u"Caisse des écoles")),
    ("26", _(u"CCAS")),
    ("27", _(u"Etablissement public de santé")),
    ("28", _(u"Ecole nationale de la santé publique")),
    ("29", _(u"Autre établissement publique ou organisme international")),
    ("50", _(u"Personne morale de droit privé autre qu'organisme social")),
    ("60", _(u"Caisse de sécurité sociale régime général")),
    ("61", _(u"Caisse de sécurité sociale régime agricole")),
    ("62", _(u"Sécurité sociale des travailleurs non salariés et professions non agricoles")),
    ("63", _(u"Autre régime obligatoire de sécurité sociale")),
    ("64", _(u"Mutuelle ou organisme d'assurance")),
    ("65", _(u"Autre tiers payant")),
    ("70", _(u"CNRACL")),
    ("71", _(u"IRCANTEC")),
    ("72", _(u"ASSEDIC")),
    ("73", _(u"Caisse mutualiste de retraite complémentaire")),
    ("74", _(u"Autre organisme social")),
    ]

LISTE_NATURES_JURIDIQUES = [
    ("00", _(u"Inconnu")),
    ("01", _(u"Particulier")),
    ("02", _(u"Artisan / commerçant / agriculteur")),
    ("03", _(u"Société")),
    ("04", _(u"CAM ou Caisse appliquant les mêmes règles")),
    ("05", _(u"Caisse complémentaire")),
    ("06", _(u"Association")),
    ("07", _(u"Etat ou organisme d'état")),
    ("08", _(u"Etablissement public national")),
    ("09", _(u"Collectivité territoriale / EPL / EPS")),
    ("10", _(u"Etat étranger")),
    ("11", _(u"CAF")),
    ]

LISTE_TYPES_ID_TIERS = [
    ("9999", _(u"Aucun")),
    ("01", _(u"SIRET")),
    ("02", _(u"SIREN")),
    ("03", _(u"FINESS")),
    ("04", _(u"NIR")),
    ]

def GetDonneesListe(liste):
        listeLabels, listeID = [], []
        for ID, label in liste :
            listeID.append(int(ID))
            if ID == "9999" :
                listeLabels.append(label)
            else :
                listeLabels.append(u"%s - %s" % (ID, label))
        return listeLabels, listeID


class CTRL_Parametres(wxpg.PropertyGrid) :
    def __init__(self, parent, IDfamille=None):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=wxpg.PG_SPLITTER_AUTO_CENTER)
        self.IDfamille = IDfamille
        
        # Définition des éditeurs personnalisés
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        
        # Données Tiers pour Hélios
        self.Append( wxpg.PropertyCategory(_(u"Données tiers pour Hélios")) )
        
        propriete = wxpg.EnumProperty(label=_(u"Titulaire"), name="titulaire_helios")
        propriete.SetHelpString(_(u"Sélectionnez le titulaire du compte pour Hélios (Trésor Public)"))
        self.Append(propriete)
##        self.MAJ_titulaire_helios() 

        propriete = wxpg.StringProperty(label=_(u"Identifiant national"), name="idtiers_helios", value=u"")
        propriete.SetHelpString(_(u"[Facultatif] Saisissez l'identifiant national (SIRET ou SIREN ou FINESS ou NIR)")) 
        self.Append(propriete)

        listeLabels, listeID = GetDonneesListe(LISTE_TYPES_ID_TIERS)
        propriete = wxpg.EnumProperty(label=_(u"Type d'identifiant national"), name="natidtiers_helios", labels=listeLabels, values=listeID, value=9999)
        propriete.SetHelpString(_(u"[Facultatif] Sélectionnez le type d'identifiant national du tiers pour Hélios (Trésor Public)"))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Référence locale"), name="reftiers_helios", value="")
        propriete.SetHelpString(_(u"[Facultatif] Saisissez la référence locale du tiers")) 
        self.Append(propriete)

        listeLabels, listeID = GetDonneesListe(LISTE_CATEGORIES_TIERS)
        propriete = wxpg.EnumProperty(label=_(u"Catégorie"), name="cattiers_helios", labels=listeLabels, values=listeID, value=1)
        propriete.SetHelpString(_(u"Sélectionnez la catégorie de tiers pour Hélios (Trésor Public)"))
        self.Append(propriete)

        listeLabels, listeID = GetDonneesListe(LISTE_NATURES_JURIDIQUES)
        propriete = wxpg.EnumProperty(label=_(u"Nature juridique"), name="natjur_helios", labels=listeLabels, values=listeID, value=1)
        propriete.SetHelpString(_(u"Sélectionnez la nature juridique du tiers pour Hélios (Trésor Public)"))
        self.Append(propriete)

        # Comptabilité
        self.Append( wxpg.PropertyCategory(_(u"Comptabilité")) )

        propriete = wxpg.StringProperty(label=_(u"Code comptable"), name="code_comptable", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code comptable de la famille (Utilisé pour les exports vers logiciels de compta)")) 
        self.Append(propriete)


        # TESTS ---------------------
##        self.SetPropertyValues({"code_budget":12345, "date_emission":"2014-02-03", "compte":2})
##        self.SetPropertyValue("code_collectivite", u"456")
##        print self.GetPropertyValues()

                            
    def MAJ_titulaire_helios(self):
        propriete = self.GetPropertyByName("titulaire_helios")
        ancienneValeur = propriete.GetValue() 
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, nom, prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille=%d AND IDcategorie=1
        GROUP BY individus.IDindividu
        ORDER BY nom, prenom;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        choix = wxpg.PGChoices()
        ancienChoixValide = False
        for IDindividu, nom, prenom in listeDonnees :
            if prenom == None : prenom = ""
            nomIndividu = u"%s %s" % (nom, prenom)
            if IDindividu == ancienneValeur :
                ancienChoixValide = True
            choix.Add(nomIndividu, IDindividu)
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete) 
        if ancienChoixValide == False :
            ancienneValeur = None
        try :
            propriete.SetValue(ancienneValeur)
        except :
            pass
    
    def MAJ(self):
        self.MAJ_titulaire_helios() 
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Famille_divers", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.majEffectuee = False
        
        # Compte internet
        self.staticBox_param = wx.StaticBox(self, -1, _(u"Compte internet"))
        self.label_activation = wx.StaticText(self, -1, _(u"Activation :"))
        self.check_activation = wx.CheckBox(self, -1, u"")
        self.label_identifiant = wx.StaticText(self, -1, _(u"Identifiant : "))
        self.ctrl_identifiant = wx.TextCtrl(self, -1, "", size=(80, -1))
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe : "))
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", size=(60, -1))
        self.bouton_mdp_renew = platebtn.PlateButton(self, -1, u" Générer un nouveau mot de passe", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_envoi_mail = platebtn.PlateButton(self, -1, u" Envoyer les codes par Email", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_historique = platebtn.PlateButton(self, -1, u" Consulter et traiter les demandes", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Historique.png"), wx.BITMAP_TYPE_ANY))
        self.MAJaffichage()

        self.bouton_mdp_renew.SetBackgroundColour(self.GetParent().GetThemeBackgroundColour())
        self.bouton_envoi_mail.SetBackgroundColour(self.GetParent().GetThemeBackgroundColour())
        self.bouton_historique.SetBackgroundColour(self.GetParent().GetThemeBackgroundColour())

        # Paramètres divers
        self.staticBox_divers = wx.StaticBox(self, -1, _(u"Paramètres divers"))
        self.ctrl_parametres = CTRL_Parametres(self, IDfamille=IDfamille)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.check_activation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMdpRenew, self.bouton_mdp_renew)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoiEmail, self.bouton_envoi_mail)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHistorique, self.bouton_historique)

    def __set_properties(self):
        self.check_activation.SetToolTipString(_(u"Cochez cette case pour activer le compte internet"))
        self.ctrl_identifiant.SetToolTipString(_(u"Code identifiant du compte internet"))
        self.ctrl_mdp.SetToolTipString(_(u"Mot de passe du compte internet"))
        self.bouton_mdp_renew.SetToolTipString(_(u"Générer un nouveau mot de passe"))
        self.bouton_envoi_mail.SetToolTipString(_(u"Envoyer un couriel à la famille avec les codes d'accès au portail Internet"))
        self.bouton_historique.SetToolTipString(_(u"Consulter et traiter les demandes de la famille"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        # Compte internet
        sizer_staticBox_param = wx.StaticBoxSizer(self.staticBox_param, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=5)
        grid_sizer_param.Add(self.label_activation, 1, wx.ALIGN_RIGHT, 0)
        grid_sizer_param.Add(self.check_activation, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add( (0, 0), 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add( (0, 0), 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_identifiant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_identifiant, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_mdp, 1, wx.ALL|wx.EXPAND, 0)

        grid_sizer_param.AddGrowableCol(1)
        sizer_staticBox_param.Add(grid_sizer_param, 1, wx.ALL|wx.EXPAND, 10)

        sizer_staticBox_param.Add(self.bouton_envoi_mail, 0, wx.ALL|wx.EXPAND, 0)
        sizer_staticBox_param.Add(self.bouton_mdp_renew, 0, wx.ALL|wx.EXPAND, 0)
        sizer_staticBox_param.Add(self.bouton_historique, 0, wx.ALL|wx.EXPAND, 0)

        grid_sizer_base.Add(sizer_staticBox_param, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 5)

        # Paramètres divers
        sizer_staticBox_divers = wx.StaticBoxSizer(self.staticBox_divers, wx.VERTICAL)
        sizer_staticBox_divers.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_staticBox_divers, 1, wx.RIGHT|wx.BOTTOM|wx.TOP|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)

    def MAJaffichage(self):
        self.ctrl_identifiant.Enable(self.check_activation.GetValue())
        self.ctrl_mdp.Enable(self.check_activation.GetValue())
        self.Refresh() 
        
    def EvtCheckBox(self, event):
        self.MAJaffichage()

    def OnBoutonMdpRenew(self, event):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment générer un nouveau mot de passe pour ce compte internet ? \n\nAttention, l'ancien mot de passe sera remplacé."), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        from Utils import UTILS_Internet
        self.ctrl_mdp.SetValue(UTILS_Internet.CreationMDP(nbreCaract=5))
        self.MAJaffichage()

    def OnBoutonEnvoiEmail(self, event):
        # Envoyer un email à la famille
        from Utils import UTILS_Envoi_email
        listeAdresses = UTILS_Envoi_email.GetAdresseFamille(self.IDfamille)
        if len(listeAdresses) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune adresse email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        from Utils import UTILS_Titulaires
        listefamilles = []
        listefamilles.append(self.IDfamille)
        titulaires = UTILS_Titulaires.GetTitulaires(listefamilles)
        nom_famille = None
        for id in titulaires:
            if titulaires[id].has_key("titulairesAvecCivilite"):
                nom_famille = titulaires[id]["titulairesAvecCivilite"]
                break
        if nom_famille == None:
            raise
        import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie = "portail")
        listeDonnees = []
        champs = {
            "{IDENTIFIANT_INTERNET}" : self.ctrl_identifiant.GetValue(),
            "{MOTDEPASSE_INTERNET}" : self.ctrl_mdp.GetValue(),
            "{NOM_FAMILLE}" : nom_famille,
        }
        for adresse in listeAdresses :
            listeDonnees.append({"adresse" : adresse, "pieces" : [], "champs" : champs})
        dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
        dlg.ChargerModeleDefaut()
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonHistorique(self, event):
        from Dlg import DLG_Portail_demandes
        dlg = DLG_Portail_demandes.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def IsLectureAutorisee(self):
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_questionnaires", "consulter", afficheMessage=False) == False : 
##            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.majEffectuee == False :
            self.ctrl_parametres.MAJ() 
            DB = GestionDB.DB()
            req = """SELECT internet_actif, internet_identifiant, internet_mdp, titulaire_helios, code_comptable, idtiers_helios, natidtiers_helios, reftiers_helios, cattiers_helios, natjur_helios
            FROM familles
            WHERE IDfamille=%d;""" % self.IDfamille
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                internet_activation, internet_identifiant, internet_mdp, titulaire_helios, code_comptable, idtiers_helios, natidtiers_helios, reftiers_helios, cattiers_helios, natjur_helios = listeDonnees[0]
                if internet_activation != None : self.check_activation.SetValue(internet_activation)
                if internet_identifiant != None : self.ctrl_identifiant.SetValue(internet_identifiant)
                if internet_mdp != None : self.ctrl_mdp.SetValue(internet_mdp)
                self.ctrl_parametres.SetPropertyValue("titulaire_helios", titulaire_helios)
                if idtiers_helios != None : self.ctrl_parametres.SetPropertyValue("idtiers_helios", idtiers_helios)
                if natidtiers_helios != None : self.ctrl_parametres.SetPropertyValue("natidtiers_helios", natidtiers_helios)
                if reftiers_helios != None : self.ctrl_parametres.SetPropertyValue("reftiers_helios", reftiers_helios)
                if cattiers_helios != None : self.ctrl_parametres.SetPropertyValue("cattiers_helios", cattiers_helios)
                if natjur_helios != None : self.ctrl_parametres.SetPropertyValue("natjur_helios", natjur_helios)
                self.ctrl_parametres.SetPropertyValue("code_comptable", code_comptable)
            self.MAJaffichage()
        
        else :
            self.ctrl_parametres.MAJ() 
        
        # Droits utilisateurs
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_compte_internet", "modifier", afficheMessage=False) == False : 
            self.check_activation.Enable(False)
            self.ctrl_identifiant.Enable(False)
            self.ctrl_mdp.Enable(False)
        
        self.majEffectuee = True
                
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        # Titulaire Hélios
        titulaire_helios = self.ctrl_parametres.GetPropertyValue("titulaire_helios")
        if titulaire_helios != None :
            DB = GestionDB.DB()
            req = """SELECT IDrattachement, IDindividu, IDcategorie, titulaire
            FROM rattachements WHERE IDfamille=%d;""" % self.IDfamille
            DB.ExecuterReq(req)
            listeRattachements = DB.ResultatReq()
            DB.Close()
            for IDrattachement, IDindividu, IDcategorie, titulaire in listeRattachements:
                if titulaire_helios == IDindividu and titulaire == 0 :
                    dlg = wx.MessageDialog(self, _(u"Attention, le titulaire Hélios doit être obligatoirement un titulaire du dossier !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        # Compte internet
        if self.check_activation.GetValue() == True :
            if self.ctrl_identifiant.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"L'identifiant internet saisi n'est pas valide !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if self.ctrl_mdp.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Le mot de passe internet saisi n'est pas valide !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True
    
    def Sauvegarde(self):
        internet_activation = int(self.check_activation.GetValue())
        internet_identifiant = self.ctrl_identifiant.GetValue() 
        internet_mdp = self.ctrl_mdp.GetValue() 
        titulaire_helios = self.ctrl_parametres.GetPropertyValue("titulaire_helios")
        idtiers_helios = self.ctrl_parametres.GetPropertyValue("idtiers_helios")
        natidtiers_helios = self.ctrl_parametres.GetPropertyValue("natidtiers_helios")
        reftiers_helios = self.ctrl_parametres.GetPropertyValue("reftiers_helios")
        cattiers_helios = self.ctrl_parametres.GetPropertyValue("cattiers_helios")
        natjur_helios = self.ctrl_parametres.GetPropertyValue("natjur_helios")
        code_comptable = self.ctrl_parametres.GetPropertyValue("code_comptable")
        DB = GestionDB.DB()
        listeDonnees = [    
                ("internet_actif", internet_activation),
                ("internet_identifiant", internet_identifiant),
                ("internet_mdp", internet_mdp),
                ("titulaire_helios", titulaire_helios),
                ("code_comptable", code_comptable),
                ("idtiers_helios", idtiers_helios),
                ("natidtiers_helios", natidtiers_helios),
                ("reftiers_helios", reftiers_helios),
                ("cattiers_helios", cattiers_helios),
                ("natjur_helios", natjur_helios),
                ]
        DB.ReqMAJ("familles", listeDonnees, "IDfamille", self.IDfamille)
        DB.Close()
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDfamille=3)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

