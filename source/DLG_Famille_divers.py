#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import UTILS_Utilisateurs
import wx.propgrid as wxpg


LISTE_CATEGORIES_TIERS = [
    ("01", _(u"Personne physique")),
    ("20", _(u"Etat ou �tablissement public national")),
    ("21", _(u"R�gion")),
    ("22", _(u"D�partement")),
    ("23", _(u"Commune")),
    ("24", _(u"Groupement de collectivit�s")),
    ("25", _(u"Caisse des �coles")),
    ("26", _(u"CCAS")),
    ("27", _(u"Etablissement public de sant�")),
    ("28", _(u"Ecole nationale de la sant� publique")),
    ("29", _(u"Autre �tablissement publique ou organisme international")),
    ("50", _(u"Personne morale de droit priv� autre qu'organisme social")),
    ("60", _(u"Caisse de s�curit� sociale r�gime g�n�ral")),
    ("61", _(u"Caisse de s�curit� sociale r�gime agricole")),
    ("62", _(u"S�curit� sociale des travailleurs non salari�s et professions non agricoles")),
    ("63", _(u"Autre r�gime obligatoire de s�curit� sociale")),
    ("64", _(u"Mutuelle ou organisme d'assurance")),
    ("65", _(u"Autre tiers payant")),
    ("70", _(u"CNRACL")),
    ("71", _(u"IRCANTEC")),
    ("72", _(u"ASSEDIC")),
    ("73", _(u"Caisse mutualiste de retraite compl�mentaire")),
    ("74", _(u"Autre organisme social")),
    ]

LISTE_NATURES_JURIDIQUES = [
    ("00", _(u"Inconnu")),
    ("01", _(u"Particulier")),
    ("02", _(u"Artisan / commer�ant / agriculteur")),
    ("03", _(u"Soci�t�")),
    ("04", _(u"CAM ou Caisse appliquant les m�mes r�gles")),
    ("05", _(u"Caisse compl�mentaire")),
    ("06", _(u"Association")),
    ("07", _(u"Etat ou organisme d'�tat")),
    ("08", _(u"Etablissement public national")),
    ("09", _(u"Collectivit� territoriale / EPL / EPS")),
    ("10", _(u"Etat �tranger")),
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
        
        # D�finition des �diteurs personnalis�s
##        if not getattr(sys, '_PropGridEditorsRegistered', False):
##            self.RegisterEditor(EditeurComboBoxAvecBoutons)
##            # ensure we only do it once
##            sys._PropGridEditorsRegistered = True
                
##        self.SetVerticalSpacing(3) 
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        
        # Donn�es Tiers pour H�lios
        self.Append( wxpg.PropertyCategory(_(u"Donn�es tiers pour H�lios")) )
        
        propriete = wxpg.EnumProperty(label=_(u"Titulaire"), name="titulaire_helios")
        propriete.SetHelpString(_(u"S�lectionnez le titulaire du compte pour H�lios (Tr�sor Public)"))
        self.Append(propriete)
        self.MAJ_titulaire_helios() 

        propriete = wxpg.StringProperty(label=_(u"Identifiant national"), name="idtiers_helios", value=u"")
        propriete.SetHelpString(_(u"[Facultatif] Saisissez l'identifiant national (SIRET ou SIREN ou FINESS ou NIR)")) 
        self.Append(propriete)

        listeLabels, listeID = GetDonneesListe(LISTE_TYPES_ID_TIERS)
        propriete = wxpg.EnumProperty(label=_(u"Type d'identifiant national"), name="natidtiers_helios", labels=listeLabels, values=listeID, value=9999)
        propriete.SetHelpString(_(u"[Facultatif] S�lectionnez le type d'identifiant national du tiers pour H�lios (Tr�sor Public)"))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"R�f�rence locale"), name="reftiers_helios", value="")
        propriete.SetHelpString(_(u"[Facultatif] Saisissez la r�f�rence locale du tiers")) 
        self.Append(propriete)

        listeLabels, listeID = GetDonneesListe(LISTE_CATEGORIES_TIERS)
        propriete = wxpg.EnumProperty(label=_(u"Cat�gorie"), name="cattiers_helios", labels=listeLabels, values=listeID, value=1)
        propriete.SetHelpString(_(u"S�lectionnez la cat�gorie de tiers pour H�lios (Tr�sor Public)"))
        self.Append(propriete)

        listeLabels, listeID = GetDonneesListe(LISTE_NATURES_JURIDIQUES)
        propriete = wxpg.EnumProperty(label=_(u"Nature juridique"), name="natjur_helios", labels=listeLabels, values=listeID, value=1)
        propriete.SetHelpString(_(u"S�lectionnez la nature juridique du tiers pour H�lios (Tr�sor Public)"))
        self.Append(propriete)

        # Comptabilit�
        self.Append( wxpg.PropertyCategory(_(u"Comptabilit�")) )

        propriete = wxpg.StringProperty(label=_(u"Code comptable"), name="code_comptable", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code comptable de la famille (Utilis� pour les exports vers logiciels de compta)")) 
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
        self.staticBox_param = wx.StaticBox(self, -1, _(u"Param�tres du compte internet"))
        self.label_activation = wx.StaticText(self, -1, _(u"Activation :"))
        self.check_activation = wx.CheckBox(self, -1, u"")
        self.label_identifiant = wx.StaticText(self, -1, _(u"Identifiant : "))
        self.ctrl_identifiant = wx.TextCtrl(self, -1, "", size=(80, -1))
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe : "))
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", size=(60, -1))
        self.MAJaffichage()

        # Param�tres divers
        self.staticBox_divers = wx.StaticBox(self, -1, _(u"Param�tres divers"))
        self.ctrl_parametres = CTRL_Parametres(self, IDfamille=IDfamille)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.check_activation)
                

    def __set_properties(self):
        self.check_activation.SetToolTipString(_(u"Cochez cette case pour activer le compte internet"))
        self.ctrl_identifiant.SetToolTipString(_(u"Code identifiant"))
        self.ctrl_mdp.SetToolTipString(_(u"Mot de passe"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Compte internet
        sizer_staticBox_param = wx.StaticBoxSizer(self.staticBox_param, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
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
        grid_sizer_base.Add(sizer_staticBox_param, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        
        # Param�tres divers
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

    def IsLectureAutorisee(self):
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_questionnaires", "consulter", afficheMessage=False) == False : 
##            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.majEffectuee == False :
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
        """ Return True si les donn�es sont valides et pretes � �tre sauvegard�es """
        # Titulaire H�lios
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
                    dlg = wx.MessageDialog(self, _(u"Attention, le titulaire H�lios doit �tre obligatoirement un titulaire du dossier !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
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

