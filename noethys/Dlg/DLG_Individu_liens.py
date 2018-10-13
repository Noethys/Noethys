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
import wx.aui
import wx.lib.agw.hypertreelist as HTL
import wx.lib.agw.hyperlink as Hyperlink
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox

from Ctrl import CTRL_Bandeau

from Data import DATA_Civilites as Civilites
import GestionDB
from Data import DATA_Liens as Liens

from Utils import UTILS_Utilisateurs


DICT_TYPES_LIENS = Liens.DICT_TYPES_LIENS
DICT_AUTORISATIONS = Liens.DICT_AUTORISATIONS


class GetValeurs() :
    def __init__(self, IDindividu_fiche=None, IDfamille=None):
        """ IDindividu_fiche : pour trouver toutes les familles rattachées à cet individu """
        """ OU IDfamille : pour obtenir uniquement les liens de la famille donnée """
        self.IDindividu_fiche = IDindividu_fiche
        self.IDfamille = IDfamille
        
    def InitValeurs(self):
        self.DB = GestionDB.DB()
        if self.IDfamille != None :
            self.listeIDfamillesRattachees = [self.IDfamille,]
        else:
            self.listeIDfamillesRattachees = self.GetFamillesRattachees()
        self.dictCategories = self.GetDictCategories()
        self.listeTousLiens = self.GetListeTousLiens()
        self.listeIndividusRattaches = self.GetListeIndividusRattaches()
        self.dictTitulairesFamilles = self.GetTitulairesFamilles()
        self.listeIDindividusRattaches = self.GetListeIDindividusRattaches()
        self.dictInfosIndividus = self.GetDictInfosIndividus()
        self.dictLiens = self.GetDictLiens()
        self.DB.Close() 
    
    def GetDictCategories(self):
        # Dict des catégories :
        dictCategories = {
            1 : _(u"Représentants"),
            2 : _(u"Enfants"),
            3 : _(u"Contacts"),
##            4 : _(u"Hors famille"),
            }
        return dictCategories
            
    def GetFamillesRattachees(self):
        # REQ > Recherche les familles rattachées à cet individu
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements WHERE IDindividu=%d;""" % self.IDindividu_fiche
        self.DB.ExecuterReq(req)
        listefamillesRattachees = self.DB.ResultatReq()
        # Récupère les ID des familles de l'individus : Ex : listeIDfamille = [1, 2]
        listeIDfamille = []
        for valeurs in listefamillesRattachees :
            if valeurs[2] not in listeIDfamille :
                listeIDfamille.append(valeurs[2])
        listeIDfamille.sort()
        return listeIDfamille
    
    def GetListeTousLiens(self):
        # Recherche des liens existants dans la base
        if len(self.listeIDfamillesRattachees) == 1 : condition = "(%d)" % self.listeIDfamillesRattachees[0]
        else : condition = str(tuple(self.listeIDfamillesRattachees))
        req = """SELECT IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, IDautorisation
        FROM liens WHERE IDfamille IN %s;""" % condition
        self.DB.ExecuterReq(req)
        listeTousLiens = self.DB.ResultatReq()
        return listeTousLiens
    
    def FindLien(self, IDindividu_sujet, IDindividu_objet):
        for IDlien, IDfamille, IDindividu_sujetTmp, IDtype_lien, IDindividu_objetTmp, IDautorisation in self.listeTousLiens :
            if IDindividu_sujet == IDindividu_sujetTmp and IDindividu_objet == IDindividu_objetTmp :
                return {"IDlien" : IDlien, "IDtypeLien" : IDtype_lien, "IDautorisation" : IDautorisation}
        return None
        
    def GetListeIndividusRattaches(self):
        if len(self.listeIDfamillesRattachees) == 1 : condition = "(%d)" % self.listeIDfamillesRattachees[0]
        else : condition = str(tuple(self.listeIDfamillesRattachees))
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements WHERE IDfamille IN %s;""" % condition
        self.DB.ExecuterReq(req)
        listeIndividusRattaches = self.DB.ResultatReq()
        return listeIndividusRattaches

    def GetInfoIndividuRattache(self, IDindividu, IDfamille):
        for IDrattachement, IDindividuTmp, IDfamilleTmp, IDcategorie, titulaire in self.listeIndividusRattaches :
            if IDindividu == IDindividuTmp and IDfamille == IDfamilleTmp :
                return IDcategorie, titulaire
        return None, None
    
    def GetTitulairesFamilles(self):
        dictTitulaires = {}
        for IDfamille in self.listeIDfamillesRattachees :
            dictTitulaires[IDfamille] = []
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in self.listeIndividusRattaches :
            if titulaire == 1 :
                dictTitulaires[IDfamille].append(IDindividu)
        return dictTitulaires
    
    def GetNomsTitulairesFamille(self, IDfamille):
        listeNoms = []
        for IDindividu in self.dictTitulairesFamilles[IDfamille]  :
            IDcivilite = self.dictInfosIndividus[IDindividu]["IDcivilite"]
            if IDcivilite != None :
                civiliteAbrege = Civilites.GetDictCivilites()[IDcivilite]["civiliteAbrege"]
            else:
                civiliteAbrege = u""
            if civiliteAbrege == None : civiliteAbrege = u""
            nom = self.dictInfosIndividus[IDindividu]["nom"]
            prenom = self.dictInfosIndividus[IDindividu]["prenom"]
            listeNoms.append(u"%s %s %s" % (civiliteAbrege, nom, prenom))
        if len(listeNoms) == 1 : return listeNoms[0]
        if len(listeNoms) == 2 : return _(u"%s et %s") % (listeNoms[0], listeNoms[1])
        if len(listeNoms) > 2 :
            texteNoms = ""
            for nom in listeNoms[:-2] :
                texteNoms += u"%s, " % nom
            texteNoms += _(u" et ") + listeNoms[-1]
            return texteNoms
    
    def GetListeIDindividusRattaches(self, IDfamille=None):
        """ Si IDfamille = None : prend toutes les familles rattachées """
        listeIDindividusRattaches = []
        for IDrattachement, IDindividu, IDfamilleTmp, IDcategorie, titulaire in self.listeIndividusRattaches :
            if IDindividu not in listeIDindividusRattaches :
                if IDfamille == None or (IDfamille != None and IDfamille == IDfamilleTmp) :
                    listeIDindividusRattaches.append(IDindividu)
        return listeIDindividusRattaches
        
    def GetDictInfosIndividus(self):
        # Création du dictionnaire d'infos sur chaque individus rattachés :
        dictInfosIndividus = {}
        if len(self.listeIDindividusRattaches) == 1 : condition = "(%d)" % self.listeIDindividusRattaches[0]
        else : condition = str(tuple(self.listeIDindividusRattaches))
        req = """SELECT IDindividu, IDcivilite, nom, prenom
        FROM individus WHERE IDindividu IN %s;""" % condition
        self.DB.ExecuterReq(req)
        listeIndividus = self.DB.ResultatReq()
        for IDindividu, IDcivilite, nom, prenom in listeIndividus :
            dictInfosIndividus[IDindividu] = { "nom" : nom, "prenom" : prenom, "IDcivilite" : IDcivilite }
        return dictInfosIndividus
    
    def GetDictLiens(self):
        # Création du dictionnaire de liens pour tous les individus rattachés
        dictLiens = {}
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in self.listeIndividusRattaches :
            
            # Création de la clé IDfamille
            if dictLiens.has_key(IDfamille) == False :
                dictLiens[IDfamille] = {}
            # Création de la clé IDindividu
            if dictLiens[IDfamille].has_key(IDindividu) == False :
                dictLiens[IDfamille][IDindividu] = {}
            # Création de la catégorie de rattachement
            for IDcategorieTmp, labelCategorie in self.dictCategories.iteritems():
                dictLiens[IDfamille][IDindividu][IDcategorieTmp] = {}
                
            for IDindividu_sujet in self.GetListeIDindividusRattaches(IDfamille) :
                IDcategorie_sujet, titulaire = self.GetInfoIndividuRattache(IDindividu_sujet, IDfamille)
                lienExistant = self.FindLien(IDindividu_sujet, IDindividu)
                if IDindividu != IDindividu_sujet :
                    if self.FindLien(IDindividu_sujet, IDindividu) == None :
                        # Si pas de lien existant, on créé une ligne vierge
                        lien = {"IDlien" : None, "IDfamille" : IDfamille, "IDindividu_sujet" : IDindividu_sujet, "IDindividu_objet" : IDindividu, "modif" : False, "IDtypeLien" : None, "titulaire" : 0, "IDautorisation" : None}
                    else :
                        # Si un lien existe, on l'importe ici
                        lien = {"IDlien" : lienExistant["IDlien"], "IDfamille" : IDfamille, "IDindividu_sujet" : IDindividu_sujet, "IDindividu_objet" : IDindividu, "modif" : False, "IDtypeLien" : lienExistant["IDtypeLien"], "titulaire" : titulaire, "IDautorisation" : lienExistant["IDautorisation"]}
                    dictLiens[IDfamille][IDindividu][IDcategorie_sujet][IDindividu_sujet] = lien
            
        return dictLiens
 
    def GetDataPourSauvegarde(self):
        listeLiensAsauver = []
        for IDfamille, dictIndividusObjet in self.dictLiens.iteritems() :
            for IDindividu_objet, dictCategorieSujet in dictIndividusObjet.iteritems() :
                for IDcategorieSujet, dictIndividusCategorie in dictCategorieSujet.iteritems() :
                    for IDindividu_sujet, dictIndividusSujet in dictIndividusCategorie.iteritems() :
                        if dictIndividusSujet["modif"] == True :
                            dictAsauver = {
                                "IDlien" : dictIndividusSujet["IDlien"], 
                                "IDfamille" : dictIndividusSujet["IDfamille"], 
                                "IDindividu_sujet" : dictIndividusSujet["IDindividu_sujet"], 
                                "IDtype_lien" : dictIndividusSujet["IDtypeLien"], 
                                "IDindividu_objet" : dictIndividusSujet["IDindividu_objet"], 
                                "IDautorisation" : dictIndividusSujet["IDautorisation"], 
                                }
                            listeLiensAsauver.append(dictAsauver)
        return listeLiensAsauver
    
    def Sauvegarde(self):
        """ Sauvegarde dans la base de données """
        listeLiensAsauver = self.GetDataPourSauvegarde() 
        DB = GestionDB.DB()
        for dictDonnees in listeLiensAsauver :
            listeDonnees = [    
                                ("IDfamille", dictDonnees["IDfamille"]),
                                ("IDindividu_sujet", dictDonnees["IDindividu_sujet"]),
                                ("IDtype_lien", dictDonnees["IDtype_lien"]),
                                ("IDindividu_objet", dictDonnees["IDindividu_objet"]),
                                ("IDautorisation", dictDonnees["IDautorisation"]),
                            ]
            if dictDonnees["IDlien"] == None :
                # Création du lien
                IDlien = DB.ReqInsert("liens", listeDonnees)
            else:
                # Modification du lien
                DB.ReqMAJ("liens", listeDonnees, "IDlien", dictDonnees["IDlien"])
        DB.Close()
        
        
                

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", IDfamille=None, IDindividu=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille

        # Construit l'hyperlink
        self.SetBackgroundColour((255, 255, 255))
        self.AutoBrowse(False)
        if IDfamille == None :
            self.SetColours("BLACK", "BLACK", "BLUE")
            self.SetUnderlines(False, False, True)
            self.SetBold(False)
        else:
            self.SetColours("BLACK", "BLACK", "BLUE")
            self.SetUnderlines(True, True, True)
            self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        self.UpdateLink()
##        if self.IDindividu != None :
##            import DLG_Individu
##            dlg = DLG_Individu.Dialog(None, IDindividu=self.IDindividu)
##            if dlg.ShowModal() == wx.ID_OK:
##                pass
##            dlg.Destroy()
##            self.GetGrandParent().MAJ() 
##            self.GetGrandParent().MAJnotebook() 


class Hyperlien_LiensFamille(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", IDfamille=None, IDindividu=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        
        if self.GetGrandParent().GetName() == "notebook_individu" :
            self.SetBackgroundColour(self.GetGrandParent().GetThemeBackgroundColour())

        # Construit l'hyperlink
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
        dlg = Dialog_liens(None, IDindividu=self.IDindividu, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            donnees = dlg.GetDonnees() 
            self.GetParent().ctrl_liens.SetDonnees(donnees)
            self.GetParent().ctrl_liens.MAJ_ctrl()
        dlg.Destroy()
        self.UpdateLink()
        
class Choice_liens(wx.Choice):
    def __init__(self, parent, id=-1, IDfamille=None, IDindividu_objet=None, IDcategorie=None, IDindividu_sujet=None, nomIndividu="", typeIndividu="" , sexeIndividu="", IDtypeLien=None, infobulle="" ):
        """ typeIndividu = "A" ou "E" (adulte ou enfant) """
        """ sexeIndividu = "M" ou "F" (masculin ou féminin) """
        """ Lien = ID type lien par défaut """
        wx.Choice.__init__(self, parent, id=id, size=(160, -1))
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu_objet = IDindividu_objet
        self.IDcategorie = IDcategorie
        self.IDindividu_sujet = IDindividu_sujet
        self.typeIndividu = typeIndividu
        self.sexeIndividu = sexeIndividu
        choices=self.GetListeTypesLiens()
        self.SetItems(choices)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.SetIDtypeLien(IDtypeLien)
                
    def GetListeTypesLiens(self):
        listeChoix = []
        self.dictChoix = {}
        for IDtypeLien, valeurs in DICT_TYPES_LIENS.iteritems() :
            if self.typeIndividu in valeurs["public"] :
                if self.sexeIndividu != None :
                    texte = valeurs["texte"][self.sexeIndividu]
##                    typeLien = valeurs[self.sexeIndividu]
##                    if self.sexeIndividu == "M" :
##                        texte = _(u"est son %s") % typeLien
##                    else:
##                        texte = _(u"est sa %s") % typeLien
                    listeChoix.append((texte, IDtypeLien))
        listeChoix.sort()
        # Création de la liste de choix pour le wx.choice après le tri
        listeChoix2 = []
        index = 0
        listeChoix2.append(_(u"n'a aucun lien"))
        self.dictChoix[index] = None
        index += 1
        for texte, IDtypeLien in listeChoix :
            listeChoix2.append(texte)
            self.dictChoix[index] = IDtypeLien
            index += 1
        return listeChoix2
            
    def OnChoice(self, event):
        self.GetGrandParent().OnMAJvaleur(IDfamille=self.IDfamille, IDindividu_objet=self.IDindividu_objet, IDcategorie=self.IDcategorie, IDindividu_sujet=self.IDindividu_sujet, nomDonnee="IDtypeLien", valeur=self.GetIDtypeLien())
    
    def GetIDtypeLien(self):
        if self.GetSelection() == -1 :
            return None
        else:
            return self.dictChoix[self.GetSelection()]
    
    def SetIDtypeLien(self, IDtypeLien=None):
        for index, IDtypeLienTmp in self.dictChoix.iteritems() :
            if IDtypeLien == IDtypeLienTmp :
                self.SetSelection(index)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

class Choice_autorisations(BitmapComboBox):
    def __init__(self, parent, id=-1, IDfamille=None, IDindividu_objet=None, IDcategorie=None, IDindividu_sujet=None, nomIndividu="", typeIndividu="" , sexeIndividu="", IDautorisation=None, infobulle="" ):
        """ typeIndividu = "A" ou "E" (adulte ou enfant) """
        """ sexeIndividu = "M" ou "F" (masculin ou féminin) """
        """ Lien = ID type lien par défaut """
        BitmapComboBox.__init__(self, parent, id=id, size=(190, -1), style=wx.CB_READONLY )
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu_objet = IDindividu_objet
        self.IDcategorie = IDcategorie
        self.IDindividu_sujet = IDindividu_sujet
        self.typeIndividu = typeIndividu
        self.sexeIndividu = sexeIndividu
        listeChoix = self.GetListe()
        for texte, img, IDautorisationTmp in listeChoix :
            self.Append(texte, img, IDautorisationTmp)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.Bind(wx.EVT_COMBOBOX, self.OnChoice)
        self.SetIDautorisation(IDautorisation)
                
    def GetListe(self):
        listeChoix = []
        self.dictChoix = {}
        for IDautorisation, valeurs in DICT_AUTORISATIONS.iteritems() :
            if self.sexeIndividu == None : 
                texte = valeurs["M"] # Si c'est un organisme
            else:
                texte = valeurs[self.sexeIndividu]
            img = valeurs["img"]
            listeChoix.append((IDautorisation, texte, img))
        listeChoix.sort()
        # Création de la liste de choix pour le wx.choice après le tri
        listeChoix2 = []
        index = 0
        listeChoix2.append((u"- - - - - - - - - - - - - - - - - - -", wx.NullBitmap, None))
        self.dictChoix[index] = None
        index += 1
        for IDautorisation, texte, img in listeChoix :
            listeChoix2.append((texte, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % img), wx.BITMAP_TYPE_ANY), IDautorisation))
            self.dictChoix[index] = IDautorisation
            index += 1
        return listeChoix2
            
    def OnChoice(self, event):
        self.GetGrandParent().OnMAJvaleur(IDfamille=self.IDfamille, IDindividu_objet=self.IDindividu_objet, IDcategorie=self.IDcategorie, IDindividu_sujet=self.IDindividu_sujet, nomDonnee="IDautorisation", valeur=self.GetIDautorisation())
    
    def GetIDautorisation(self):
        if self.GetSelection() == -1 :
            return None
        else:
            return self.dictChoix[self.GetSelection()]
    
    def SetIDautorisation(self, IDautorisation=None):
        for index, IDautorisationTmp in self.dictChoix.iteritems() :
            if IDautorisation == IDautorisationTmp :
                self.SetSelection(index)
                
                
# ---------------------------------------------------------------------------------------------------------------------------------------------------------


class Choice_autorisations_archive(wx.Choice):
    def __init__(self, parent, id=-1, IDfamille=None, IDindividu_objet=None, IDcategorie=None, IDindividu_sujet=None, nomIndividu="", typeIndividu="" , sexeIndividu="", IDautorisation=None, infobulle="" ):
        """ typeIndividu = "A" ou "E" (adulte ou enfant) """
        """ sexeIndividu = "M" ou "F" (masculin ou féminin) """
        """ Lien = ID type lien par défaut """
        wx.Choice.__init__(self, parent, id=id, size=(190, -1) ) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu_objet = IDindividu_objet
        self.IDcategorie = IDcategorie
        self.IDindividu_sujet = IDindividu_sujet
        self.typeIndividu = typeIndividu
        self.sexeIndividu = sexeIndividu
        choices=self.GetListe()
        self.SetItems(choices)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.SetIDautorisation(IDautorisation)
                
    def GetListe(self):
        listeChoix = []
        self.dictChoix = {}
        for IDautorisation, valeurs in DICT_AUTORISATIONS.iteritems() :
            if self.sexeIndividu == None : 
                texte = valeurs["M"] # Si c'est un organisme
            else:
                texte = valeurs[self.sexeIndividu]
            listeChoix.append((IDautorisation, texte))
        listeChoix.sort()
        # Création de la liste de choix pour le wx.choice après le tri
        listeChoix2 = []
        index = 0
        listeChoix2.append(u"  ")
        self.dictChoix[index] = None
        index += 1
        for IDautorisation, texte in listeChoix :
            listeChoix2.append(texte)
            self.dictChoix[index] = IDautorisation
            index += 1
        return listeChoix2
            
    def OnChoice(self, event):
        self.GetGrandParent().OnMAJvaleur(IDfamille=self.IDfamille, IDindividu_objet=self.IDindividu_objet, IDcategorie=self.IDcategorie, IDindividu_sujet=self.IDindividu_sujet, nomDonnee="IDautorisation", valeur=self.GetIDautorisation())
    
    def GetIDautorisation(self):
        if self.GetSelection() == -1 :
            return None
        else:
            return self.dictChoix[self.GetSelection()]
    
    def SetIDautorisation(self, IDautorisation=None):
        for index, IDautorisationTmp in self.dictChoix.iteritems() :
            if IDautorisation == IDautorisationTmp :
                self.SetSelection(index)
                
                
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

class CheckboxAvecImage(wx.Panel):
    def __init__(self, parent, IDfamille=None, IDindividu_objet=None, IDcategorie=None, IDindividu_sujet=None, img=None, label="", infobulle="", typeDonnee="IDautorisation"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu_objet = IDindividu_objet
        self.IDcategorie = IDcategorie
        self.IDindividu_sujet = IDindividu_sujet
        self.typeDonnee = typeDonnee
        self.SetBackgroundColour((255, 255, 255))
        self.SetToolTip(wx.ToolTip(infobulle))
        self.cb = wx.CheckBox(self, id=-1, label=label) 
        self.cb.SetToolTip(wx.ToolTip(infobulle))
        if img != None :
            self.img = wx.StaticBitmap(self, -1, img)
            self.img.SetToolTip(wx.ToolTip(infobulle))
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.cb, 1, wx.EXPAND|wx.ALL, 0)
        if img != None :
            grid_sizer_base.Add(self.img, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        # Binds
        self.cb.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def OnCheck(self, event):
        self.GetGrandParent().OnMAJvaleur(IDfamille=self.IDfamille, IDindividu_objet=self.IDindividu_objet, IDcategorie=self.IDcategorie, IDindividu_sujet=self.IDindividu_sujet, nomDonnee=self.typeDonnee, valeur=int(self.cb.GetValue()))
       
    def SetEtat(self, etat=False):
        if etat != None :
            self.cb.SetValue(etat)
        


class CTRL_Saisie_Liens(HTL.HyperTreeList):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style= wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT,
                 IDindividu=None,
                 IDfamille=None,
                 donnees={}
                 ):
        HTL.HyperTreeList.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.donnees = donnees
        
        # Création de l'ImageList (Récupère les images attribuées aux civilités)
        il = wx.ImageList(16, 16)
        index = 0
        self.dictImages = {}
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, label, abrege, img, sexe in civilites :
                exec("self.img%d = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s'), wx.BITMAP_TYPE_PNG))" % (index, img))
                exec("self.dictImages[%d] = self.img%d" % (IDcivilite, index))
                index += 1
        self.AssignImageList(il)
        
        # Creation des colonnes
        self.AddColumn(_(u"Individu"))
        self.SetColumnWidth(0, 230)
        self.AddColumn(_(u"Type de lien"))
        self.SetColumnWidth(1, 170)
        self.AddColumn(_(u"Niveau d'autorisation"))
        self.SetColumnWidth(2, 200)
        self.SetMainColumn(0)
                        
        # Création des branches
        self.root = self.AddRoot(_(u"Les liens"))
##        self.CreationBranches()
        
        self.SetSpacing(10)
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_FULL_ROW_HIGHLIGHT |wx.TR_HAS_VARIABLE_ROW_HEIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
    
    def SetDonnees(self, donnees):
        self.donnees = donnees
        
    def MAJ_ctrl(self):
        """ Met à jour (redessine) tout le contrôle """
        nbreBranches = self.GetChildrenCount(self.root)
        if nbreBranches > 1 :
            self.DeleteChildren(self.root)
##        self.DeleteAllItems()
        self.CreationBranches()
    
    def MAJ_contenu(self):
        """ Met uniquement à jour le contenu du contrôle """
        for IDfamille in self.donnees.listeIDfamillesRattachees :
            IDindividu_objet = self.IDindividu
            IDcategorie_individu_objet, titulaireTmp = self.donnees.GetInfoIndividuRattache(IDindividu_objet, IDfamille)
            
            listeIndividusRattaches = self.donnees.GetListeIDindividusRattaches(IDfamille)
            for IDindividu_sujet in listeIndividusRattaches :
                if IDindividu_sujet != IDindividu_objet :
                    
                    # Récupération du controle LIENS
                    IDcategorie, titulaireTmp = self.donnees.GetInfoIndividuRattache(IDindividu_sujet, IDfamille)                
                    ctrl_lien = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["ctrl_lien"]
                    # Recherche la valeur dans le dict et l'applique
                    IDtypeLien = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["IDtypeLien"]
                    ctrl_lien.SetIDtypeLien(IDtypeLien)
                    
##                    if IDcategorie_individu_objet == 2 : # and IDcategorie == 1 
##                        # Récupération du controle AUTORISATIONS
##                        IDcategorie, titulaireTmp = self.donnees.GetInfoIndividuRattache(IDindividu_sujet, IDfamille)
##                        ctrl_autorisations = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["ctrl_autorisations"]
##                        # Recherche la valeur dans le dict et l'applique
##                        IDautorisation = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["IDautorisation"]
##                        ctrl_autorisations.SetIDautorisation(IDautorisation)
##                        
##                    if IDcategorie_individu_objet == 1 and IDcategorie == 2 :
##                        # Récupération du controle AUTORISATIONS
##                        IDcategorie, titulaireTmp = self.donnees.GetInfoIndividuRattache(IDindividu_sujet, IDfamille)
##                        ctrl_autorisations = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["ctrl_autorisations"]
##                        # Recherche la valeur dans le dict et l'applique
##                        IDautorisation = self.donnees.dictLiens[IDfamille][IDindividu_sujet][1][IDindividu_objet]["IDautorisation"]
##                        ctrl_autorisations.SetIDautorisation(IDautorisation)
                    
                    # Récupération du controle AUTORISATIONS
                    IDcategorie, titulaireTmp = self.donnees.GetInfoIndividuRattache(IDindividu_sujet, IDfamille)
                    ctrl_autorisations = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["ctrl_autorisations"]
                    # Recherche la valeur dans le dict et l'applique
                    IDautorisation = self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["IDautorisation"]
                    ctrl_autorisations.SetIDautorisation(IDautorisation)
                                
        
    def CreationBranches(self):
        # Création des branche FAMILLES
        for IDfamille in self.donnees.listeIDfamillesRattachees :
            # Intégration de l'hyperlien NOM DE LA FAMILLE
            label = _(u"Famille de %s") % self.donnees.GetNomsTitulairesFamille(IDfamille)
            hl = Hyperlien(self.GetMainWindow(), label=label, URL="", IDfamille=IDfamille, IDindividu=None, infobulle=u"")
            famille = self.AppendItem(self.root, "", wnd=hl)
            self.SetPyData(famille, IDfamille)
            
            # Création des branche CATEGORIES
            for IDcategorie in range(1, len(self.donnees.dictCategories)+1):
                txt = self.donnees.dictCategories[IDcategorie]
                categorie = self.AppendItem(famille, txt)
                self.SetPyData(categorie, IDcategorie)
                self.SetItemBold(categorie, True)
                
                # Création des branche INDIVIDUS
                if self.donnees.dictLiens[IDfamille].has_key(self.IDindividu) :
                    if self.donnees.dictLiens[IDfamille][self.IDindividu].has_key(IDcategorie) :
                        dictIndividus = self.donnees.dictLiens[IDfamille][self.IDindividu][IDcategorie]

                        for IDindividu, dictIndividu in dictIndividus.iteritems()  :
                            IDlien = dictIndividu["IDlien"]
                            nom = self.donnees.dictInfosIndividus[IDindividu]["nom"]
                            prenom = self.donnees.dictInfosIndividus[IDindividu]["prenom"]
                            IDcivilite = self.donnees.dictInfosIndividus[IDindividu]["IDcivilite"]
                            if IDcivilite == None : IDcivilite = 1
                            categorieCivilite = Civilites.GetDictCivilites()[IDcivilite]["categorie"]
                            if categorieCivilite == "ENFANT" :
                                type = "E"
                            else:
                                type = "A"
                            IDtypeLien = dictIndividu["IDtypeLien"]
                            sexe = Civilites.GetDictCivilites()[IDcivilite]["sexe"]
                            IDautorisation = dictIndividu["IDautorisation"]
                            titulaire = dictIndividu["titulaire"]
                                            
                            if IDcategorie == 4 and IDindividu == None:
                                # Intégration de l'hyperlien AJOUTER UN INDIVIDU
                                hl = Hyperlien(self.GetMainWindow(), label=_(u"Ajouter un individu..."), URL="", IDindividu=None, infobulle=u"")#_(u"Cliquez sur ce lien pour ajouter \n un individu hors famille"))
                                individu = self.AppendItem(categorie, "", wnd=hl)
                                self.SetPyData(individu, IDindividu)
                                
                            else:
                                # Intégration de l'hyperlien NOM INDIVIDU
                                individu = self.AppendItem(categorie, u"%s %s" % (nom, prenom))#, wnd=hl)
                                self.SetPyData(individu, IDindividu)
                            
                                # Intégration du Choice LIENS
                                infobulle = _(u"Sélectionnez le lien de %s vis-à-vis \nde %s") % (prenom, self.donnees.dictInfosIndividus[self.IDindividu]["prenom"])
                                ctrl_lien = Choice_liens(self.GetMainWindow(), -1, IDfamille, self.IDindividu, IDcategorie, IDindividu, prenom, type, sexe, IDtypeLien, infobulle)
                                self.SetItemWindow(individu, ctrl_lien, 1)
                                # Mémorisation du controle LIENS
                                self.donnees.dictLiens[IDfamille][self.IDindividu][IDcategorie][IDindividu]["ctrl_lien"] = ctrl_lien
                                
                                # Intégration de la case à cocher AUTORISATIONS
                                IDcategorie_individu_objet, titulaire_individu_objet = self.donnees.GetInfoIndividuRattache(self.IDindividu, IDfamille) 

                                infobulle = _(u"Sélectionnez le niveau d'autorisation de %s vis-à-vis de %s") % (prenom, self.donnees.dictInfosIndividus[self.IDindividu]["prenom"])
                                ctrl_autorisations = Choice_autorisations(self.GetMainWindow(), -1, IDfamille, self.IDindividu, IDcategorie, IDindividu, prenom, type, sexe, IDautorisation, infobulle)
                                self.SetItemWindow(individu, ctrl_autorisations, 2)
                                self.donnees.dictLiens[IDfamille][self.IDindividu][IDcategorie][IDindividu]["ctrl_autorisations"] = ctrl_autorisations

                                # Images de l'individu
                                self.SetItemImage(individu, self.dictImages[IDcivilite], which=wx.TreeItemIcon_Normal)
                                self.SetItemImage(individu, self.dictImages[IDcivilite], which=wx.TreeItemIcon_Expanded)
            
                self.Expand(categorie) 
            
            self.Expand(famille)
            
    def OnMAJvaleur(self, IDfamille=None, IDindividu_objet=None, IDcategorie=None, IDindividu_sujet=None, nomDonnee=None, valeur=None):
        """ Modifie une valeur donnée dans le self.dictIndividus """
        # ctrl AUTORISATIONS
        if nomDonnee == "IDautorisation" :
##            if self.donnees.dictLiens[IDfamille][IDindividu_sujet][IDcategorie].has_key(IDindividu_objet) == False :
##                lien = {"IDlien" : None, "IDfamille" : IDfamille, "IDindividu_sujet" : IDindividu_sujet, "IDindividu_objet" : IDindividu_objet, "modif" : True, "IDtypeLien" : None, "titulaire" : 0, "IDautorisation" : valeur}
##                self.donnees.dictLiens[IDfamille][IDindividu_sujet][IDcategorie][IDindividu_objet] = lien
##            else:
            self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["IDautorisation"] = valeur
            self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["modif"] = True
                
##            if IDcategorie == 2 : 
##                # Si on clique la case RESPONSABLE d'une ligne REPRESENTANTS
####                self.donnees.dictLiens[IDfamille][IDindividu_sujet][1][IDindividu_objet]["IDautorisation"] = valeur
####                self.donnees.dictLiens[IDfamille][IDindividu_sujet][1][IDindividu_objet]["modif"] = True
##                self.donnees.dictLiens[IDfamille][IDindividu_sujet][IDcategorie][IDindividu_objet]["IDautorisation"] = valeur
##                self.donnees.dictLiens[IDfamille][IDindividu_sujet][IDcategorie][IDindividu_objet]["modif"] = True
##            if IDcategorie == 1 : 
##                # Si on clique la case RESPONSABLE d'une ligne ENFANTS
##                self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["IDautorisation"] = valeur
##                self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["modif"] = True
                
        # CHOICE IDtypeLien
        if nomDonnee == "IDtypeLien" :
            # Enregistrement de la valeur
            self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["IDtypeLien"] = valeur
            self.donnees.dictLiens[IDfamille][IDindividu_objet][IDcategorie][IDindividu_sujet]["modif"] = True
            
            #
            # ----------------------- Modification en cascade des liens -----------------------
            #
            
            # Application du lien inverse à l'autre individu :
            IDcategorieTmp, titulaireTmp = self.donnees.GetInfoIndividuRattache(IDindividu_objet, IDfamille)
            if valeur == None :
                IDtypeLien = None
            else:
                IDtypeLien = DICT_TYPES_LIENS[valeur]["lien"]
            self.donnees.dictLiens[IDfamille][IDindividu_sujet][IDcategorieTmp][IDindividu_objet]["IDtypeLien"] = IDtypeLien
            self.donnees.dictLiens[IDfamille][IDindividu_sujet][IDcategorieTmp][IDindividu_objet]["modif"] = True
            # Déduction de liens : 
            
            # Si individu_objet est une femme : on recherche les enfants de individu_objet 
            # et on leur applique entre eux le lien FRERES/SOEUR
            IDcivilite = self.donnees.dictInfosIndividus[IDindividu_objet]["IDcivilite"]
            if IDcivilite == 2 or IDcivilite == 3 :
                # C'est une femme , alors on recherche ses enfants
                listeFreresSoeurs = []
                dictEnfants = self.donnees.dictLiens[IDfamille][IDindividu_objet][2]
                for IDindividu_enfant, dictEnfants in dictEnfants.iteritems() :
                    # On vérifie que c'est son enfant :
                    if dictEnfants["IDtypeLien"] == 2 :
                        listeFreresSoeurs.append(IDindividu_enfant)
                # On applique le lien 2 (freres/soeur) aux enfants trouvés
                if len(listeFreresSoeurs) > 1 : 
                    for IDenfant_sujet in listeFreresSoeurs :
                        for IDenfant_objet in listeFreresSoeurs :
                            if IDenfant_sujet != IDenfant_objet :
                                self.donnees.dictLiens[IDfamille][IDenfant_sujet][2][IDenfant_objet]["IDtypeLien"] = 3
                                self.donnees.dictLiens[IDfamille][IDenfant_sujet][2][IDenfant_objet]["modif"] = True
        
        
        
        # Met à jour en cascade les autres lignes du HyperTreeList
        if self.parent.GetName() == "panel_liens" :
            self.MAJ_contenu()
        else:
            self.parent.MAJ(IDindividu_selection=IDindividu_objet)
            

# -----------------------------------------------------------------------------------------------------------------------------------------

class Panel_liens(wx.Panel):
    def __init__(self, parent, id=-1, IDindividu=None, IDfamille=None):
        wx.Panel.__init__(self, parent, id=id, name="panel_liens", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        
        self.majEffectuee = False
        
##        self.donnees = GetValeurs(self.IDindividu, self.IDfamille)
##        self.donnees.InitValeurs()
        
        self.staticbox_liens = wx.StaticBox(self, -1, _(u"Liens"))
        self.ctrl_liens = CTRL_Saisie_Liens(self, IDindividu=self.IDindividu, IDfamille=self.IDfamille)#, donnees=self.donnees)
        self.ctrl_liens.SetMinSize((20, 20))
        
        self.hyperlien_liensFamille = Hyperlien_LiensFamille(self, label=_(u"Afficher tous les liens de la famille"), IDindividu=self.IDindividu, IDfamille=self.IDfamille, URL="", infobulle=_(u"Cliquez sur ce lien pour afficher tous les liens de la famille"))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        staticbox_liens = wx.StaticBoxSizer(self.staticbox_liens, wx.VERTICAL)
        grid_sizer_liens = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_liens.Add(self.ctrl_liens, 1, wx.EXPAND, 0)
        grid_sizer_liens.Add(self.hyperlien_liensFamille, 0, wx.EXPAND, 0) 
        grid_sizer_liens.AddGrowableCol(0)
        grid_sizer_liens.AddGrowableRow(0)
        staticbox_liens.Add(grid_sizer_liens, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_liens, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)        
        
    def Set_Header(self, nomLigne, texte):
        try :
            self.ficheIndividu = self.Parent.GetParent()
            if self.ficheIndividu.GetName() != "fiche_liens" :
                self.ficheIndividu = None
        except : 
            self.ficheIndividu = None
        if self.ficheIndividu != None :
            self.ficheIndividu.Set_Header(nomLigne, texte)
    
    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.majEffectuee == False :
            
            # MAJ du contrôle
            self.donnees = GetValeurs(self.IDindividu, self.IDfamille)
            self.donnees.InitValeurs()
            self.ctrl_liens.SetDonnees(self.donnees)
            self.ctrl_liens.MAJ_ctrl()
            
            # Vérification des droits utilisateurs
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_liens", "modifier", afficheMessage=False) == False : 
                self.ctrl_liens.Enable(False)
            
            self.majEffectuee = True
            
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        if self.majEffectuee == True :
            self.donnees.Sauvegarde()

# --------------------------------------------------------------------------------------------------------------------------


class Notebook(wx.aui.AuiNotebook):
    def __init__(self, parent, IDindividu=None, IDfamille=None):
        wx.aui.AuiNotebook.__init__(self, parent, style=wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_TAB_MOVE | wx.aui.AUI_NB_SCROLL_BUTTONS) 
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.dictPages = {}
                    
    def MAJ(self, IDindividu_selection=None):
        
        # MAJ Globale
        if IDindividu_selection == None :
            
            # Supprime les pages déjà crées
            if self.GetPageCount() > 0 :
                for index in range(self.GetPageCount()-1, -1, -1) :
                    self.DeletePage(index)
            
            self.dictPages = {}
            
            # Récupération des données
            self.donnees = GetValeurs(IDindividu_fiche=self.IDindividu, IDfamille=self.IDfamille)
            self.donnees.InitValeurs()
            listeIDindividus = self.donnees.GetListeIDindividusRattaches(self.IDfamille)
            dictCivilites = Civilites.GetDictCivilites()        
            
            #Création du notebook aui
            indexPage = 0
            for IDindividu in listeIDindividus :
                # Création de la page
                page = CTRL_Saisie_Liens(self, IDindividu=IDindividu, IDfamille=self.IDfamille, donnees=self.donnees)
                page.MAJ_ctrl()
                self.dictPages[IDindividu] = indexPage
                nomIndividu = self.donnees.dictInfosIndividus[IDindividu]["nom"] + " " + self.donnees.dictInfosIndividus[IDindividu]["prenom"]
                self.AddPage(page, nomIndividu)
                # Intégration de l'image dans l'onglet
                IDcivilite = self.donnees.dictInfosIndividus[IDindividu]["IDcivilite"]
                if IDcivilite != None :
                    nomImage = dictCivilites[IDcivilite]["nomImage"]
                    self.SetPageBitmap(indexPage, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_PNG))
                indexPage += 1
        
        # MAJ des pages
        else :
            for indexPage in range(0, self.GetPageCount()):
                if indexPage != self.dictPages[IDindividu_selection] :
                    ctrl_liens = self.GetPage(indexPage)
                    ctrl_liens.MAJ_contenu()
            self.Sauvegarde()
        
    def Sauvegarde(self):
        self.donnees.Sauvegarde()
    
    def GetDonnees(self):
        return self.donnees



# ------------------------------------------------------------------------------------------------------------------------------
                 
class Dialog_liens(wx.Dialog):
    def __init__(self, parent, IDindividu=None, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        
        intro = _(u"Vous bénéficiez ici d'une vue d'ensemble des liens unissant les membres de la famille sélectionnée. Vous pouvez utiliser un glisser-déposer avec votre souris sur chaque onglet pour afficher plusieurs individus à la fois.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=_(u"Définition des liens"), texte=intro, hauteurHtml=30, nomImage="Images/32x32/Famille.png")
        
        self.ctrl_notebook = Notebook(self, IDindividu=IDindividu, IDfamille=IDfamille)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.ctrl_notebook.MAJ() 

    def __set_properties(self):
        self.SetTitle(_(u"Définition des liens"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))
        self.SetMinSize((650, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_notebook, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonOk(self, event):
        #self.ctrl_notebook.Sauvegarde()
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        return self.ctrl_notebook.GetDonnees()
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Compositiondelafamille")


class Frame_individu_liens(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.nouvelleFiche = False
        self.IDindividu = 1
        self.ctrl = Panel_liens(self, IDindividu=self.IDindividu)
        self.ctrl.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    test = "tous"

    if test == "tous" :

        # DLG tous les liens
        dialog_1 = Dialog_liens(None, IDindividu=None, IDfamille=4)
        Frame_individu_liens
        app.SetTopWindow(dialog_1)
        dialog_1.ShowModal()

    else :

        # Frame pour test DLG_individu onglet Liens
        frame_1 = Frame_individu_liens(None, -1, "TEST", size=(800, 400))
        app.SetTopWindow(frame_1)
        frame_1.Show()

    app.MainLoop()
    