#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _

import wx
import CTRL_Bouton_image
import sys
import datetime

import wx.lib.agw.supertooltip as STT
import wx.lib.agw.hypertreelist as HTL

import GestionDB
import DATA_Civilites as Civilites
import DATA_Liens as Liens
import CTRL_Photo
import DLG_Individu

##import DLG_Individu_liens
import UTILS_Utilisateurs

DICT_TYPES_LIENS = Liens.DICT_TYPES_LIENS


class GetValeurs() :
    def __init__(self, IDfamille=None):
        self.IDfamille = IDfamille
        
        self.listeIDindividus, self.dictInfosIndividus = self.GetInfosIndividus()
        
    def GetLiensCadres(self):
        """ Retourne les liens de filiation ou de couple """
        self.listeLiens = self.GetLiens() 
        dictRelations = {}
        for numCol in [1, 2, 3] :
            dictRelations[numCol] = { "filiation" : {}, "couple" : [], "ex-couple" : [] }
            for IDindividu in self.listeIDindividus:
                if self.dictInfosIndividus[IDindividu]["categorie"] == numCol :
                    listeLiensIndividus = self.RechercheLien(IDindividu)
                    for IDindividu_objet, IDtype_lien, typeRelation in listeLiensIndividus :
                        if self.dictInfosIndividus.has_key(IDindividu_objet) :
                            # Relations de couple
                            if (typeRelation == "couple" or typeRelation == "ex-couple") and (IDindividu_objet, IDindividu) not in dictRelations[numCol][typeRelation] :
                                dictRelations[numCol][typeRelation].append( (IDindividu, IDindividu_objet) )
                            # Relations de filiation
                            if typeRelation == "enfant" :
                                IDenfant = IDindividu
                                IDparent = IDindividu_objet
                                if dictRelations[numCol]["filiation"].has_key(IDenfant) == False :
                                    dictRelations[numCol]["filiation"][IDenfant] = [IDparent,]
                                else:
                                    if IDparent not in dictRelations[numCol]["filiation"][IDenfant] :
                                        dictRelations[numCol]["filiation"][IDenfant].append(IDparent)
                                    
##        for numCol in [1, 2, 3] :
##            print numCol
##            print dictRelations[numCol]
        
        return dictRelations
        
    
    def RechercheLien(self, IDindividu):
        listeLiens = []
        for IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable in self.listeLiens :
            if IDindividu == IDindividu_sujet :
                if IDtype_lien != None :
                    typeRelation = DICT_TYPES_LIENS[IDtype_lien]["type"]
                    listeLiens.append((IDindividu_objet, IDtype_lien, typeRelation))
        return listeLiens
        
    def GetLiens(self):
        # Recherche des liens existants dans la base
        db = GestionDB.DB()
        if len(self.listeIDindividus) == 1 : condition = "(%d)" % self.listeIDindividus[0]
        else : condition = str(tuple(self.listeIDindividus))
        req = """SELECT IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable
        FROM liens WHERE IDindividu_sujet IN %s;""" % condition
        db.ExecuterReq(req)
        listeTousLiens = db.ResultatReq()
        db.Close()
        return listeTousLiens
        
    def GetInfosIndividus(self):
        dictInfos = {} 
        listeIDindividus = []
        # Recherche des individus rattachés
        db = GestionDB.DB()
        req = """SELECT IDrattachement, IDindividu, IDcategorie, titulaire
        FROM rattachements WHERE IDfamille=%d;""" % self.IDfamille
        db.ExecuterReq(req)
        listeRattachements = db.ResultatReq()
        db.Close()
        if len(listeRattachements) == 0 : return listeIDindividus, dictInfos
        # Intégration de ces premières valeurs dans le dictValeurs
        for IDrattachement, IDindividu, IDcategorie, titulaire in listeRattachements :
            listeIDindividus.append(IDindividu)
            dictInfos[IDindividu] = {"categorie" : IDcategorie, "titulaire" : titulaire, "IDrattachement" : IDrattachement}
        
        # Recherche des inscriptions des membres de la famille
        dictInscriptions = {}
        db = GestionDB.DB()
        req = """SELECT 
        IDinscription, IDindividu, date_inscription, parti,
        activites.nom, activites.date_debut, activites.date_fin,
        groupes.nom, categories_tarifs.nom
        FROM inscriptions
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        WHERE IDfamille=%d;""" % self.IDfamille
        db.ExecuterReq(req)
        listeInscriptions = db.ResultatReq()
        db.Close()
        for IDinscription, IDindividu, dateInscription, parti, nomActivite, activiteDebut, activiteFin, nomGroupe, nomCategorie in listeInscriptions :
            if dictInscriptions.has_key(IDindividu) == False :
                dictInscriptions[IDindividu] = []
            dictTemp = {
                "IDinscription":IDinscription, "dateInscription":dateInscription, "parti":parti, 
                "nomActivite":nomActivite, "activiteDebut":activiteDebut, "activiteFin":activiteFin, 
                "nomGroupe":nomGroupe, "nomCategorie":nomCategorie
                } 
            dictInscriptions[IDindividu].append(dictTemp) 
            
        # Recherche des infos détaillées sur chaque individu
        dictCivilites = Civilites.GetDictCivilites()
        db = GestionDB.DB()
        listeChamps = (
            "IDcivilite", "nom", "prenom", "num_secu","IDnationalite", 
            "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
            "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
            "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
            "tel_domicile", "tel_mobile", "tel_fax", "mail"
            )
        for IDindividu in listeIDindividus :
            # Infos de la table Individus
            req = """SELECT %s
            FROM individus WHERE IDindividu=%d;""" % (",".join(listeChamps), IDindividu)
            db.ExecuterReq(req)
            listeIndividus = db.ResultatReq()
            for index in range(0, len(listeChamps)) :
                nomChamp = listeChamps[index]
                dictInfos[IDindividu][nomChamp] = listeIndividus[0][index]
            # Infos sur la civilité
            if dictInfos[IDindividu]["IDcivilite"] != None and dictInfos[IDindividu]["IDcivilite"] != "" :
                dictInfos[IDindividu]["genre"] = dictCivilites[dictInfos[IDindividu]["IDcivilite"]]["sexe"]
                dictInfos[IDindividu]["categorieCivilite"] = dictCivilites[dictInfos[IDindividu]["IDcivilite"]]["categorie"]
                dictInfos[IDindividu]["civiliteLong"] = dictCivilites[dictInfos[IDindividu]["IDcivilite"]]["civiliteLong"]
                dictInfos[IDindividu]["civiliteAbrege"] = dictCivilites[dictInfos[IDindividu]["IDcivilite"]]["civiliteAbrege"]
                dictInfos[IDindividu]["nomImage"]  = dictCivilites[dictInfos[IDindividu]["IDcivilite"]]["nomImage"]
            else:
                dictInfos[IDindividu]["genre"] = ""
                dictInfos[IDindividu]["categorieCivilite"] = ""
                dictInfos[IDindividu]["civiliteLong"] = ""
                dictInfos[IDindividu]["civiliteAbrege"] = ""
                dictInfos[IDindividu]["nomImage"]  = None

        db.Close()
        
        #----------------------------------------------
        # 2ème tournée : Infos détaillées
        #----------------------------------------------
        
        for IDindividu in listeIDindividus :

            # Nom
            nomComplet1 = u"%s %s" % (dictInfos[IDindividu]["nom"], dictInfos[IDindividu]["prenom"])
            dictInfos[IDindividu]["nomComplet1"] = nomComplet1
            if dictInfos[IDindividu]["categorieCivilite"] == "ADULTE" :
                nomComplet2 = u"%s %s %s" % (dictInfos[IDindividu]["civiliteAbrege"], dictInfos[IDindividu]["nom"], dictInfos[IDindividu]["prenom"])
            else:
                nomComplet2 = nomComplet1
            dictInfos[IDindividu]["nomComplet2"] = nomComplet2
            
            # Date de naissance
            datenaissComplet = self.GetTxtDateNaiss(dictInfos, IDindividu)
            dictInfos[IDindividu]["datenaissComplet"] = datenaissComplet
            
            # Adresse
            adresse_auto = dictInfos[IDindividu]["adresse_auto"] 
            if adresse_auto != None and dictInfos.has_key(adresse_auto) :
                rue_resid = dictInfos[adresse_auto]["rue_resid"] 
                cp_resid = dictInfos[adresse_auto]["cp_resid"] 
                ville_resid = dictInfos[adresse_auto]["ville_resid"] 
            else:
                rue_resid = dictInfos[IDindividu]["rue_resid"] 
                cp_resid = dictInfos[IDindividu]["cp_resid"] 
                ville_resid = dictInfos[IDindividu]["ville_resid"] 
            if cp_resid == None : cp_resid = ""
            if ville_resid == None : ville_resid = ""
            dictInfos[IDindividu]["adresse_ligne1"] = rue_resid
            dictInfos[IDindividu]["adresse_ligne2"] = u"%s %s" % (cp_resid, ville_resid)
            
            # Coordonnées
            tel_domicile = dictInfos[IDindividu]["tel_domicile"] 
            if tel_domicile != None :
                dictInfos[IDindividu]["tel_domicile_complet"] = _(u"Tél. domicile : %s") % tel_domicile
            else:
                dictInfos[IDindividu]["tel_domicile_complet"] = None
            tel_mobile = dictInfos[IDindividu]["tel_mobile"] 
            if tel_mobile != None :
                dictInfos[IDindividu]["tel_mobile_complet"] = _(u"Tél. mobile : %s") % tel_mobile
            else:
                dictInfos[IDindividu]["tel_mobile_complet"] = None
            mail = dictInfos[IDindividu]["mail"] 
            if mail != None :
                dictInfos[IDindividu]["mail_complet"] = _(u"Email : %s") % mail
            else:
                dictInfos[IDindividu]["mail_complet"] = None
            travail_tel = dictInfos[IDindividu]["travail_tel"] 
            if travail_tel != None :
                dictInfos[IDindividu]["travail_tel_complet"] = _(u"Tél. travail : %s") % travail_tel
            else:
                dictInfos[IDindividu]["travail_tel_complet"] = None
            
            # Infos sur les liens
            
            
            # Infos sur les activités inscrites
            if dictInscriptions.has_key(IDindividu) == True :
                dictInfos[IDindividu]["inscriptions"] = True
                dictInfos[IDindividu]["listeInscriptions"] = dictInscriptions[IDindividu]
            else:
                dictInfos[IDindividu]["inscriptions"] = False
                dictInfos[IDindividu]["listeInscriptions"] = []
        
        return listeIDindividus, dictInfos
    
    
    def GetDictCadres(self):
        """ Crée le dictionnaire spécial pour l'affichage des cadres individus """
        dictCadres = {}
        for IDindividu in self.listeIDindividus :
            listeLignes = []
            # Ligne NOM
            nomComplet1 = self.dictInfosIndividus[IDindividu]["nomComplet1"]
            listeLignes.append((nomComplet1, 8, "bold"))
            # Ligne Date de naissance
            if self.dictInfosIndividus[IDindividu]["categorie"] == 2 :
                txtDatenaiss = self.dictInfosIndividus[IDindividu]["datenaissComplet"]
                listeLignes.append((txtDatenaiss, 7, "normal"))
            # Spacer
            listeLignes.append((u"#SPACER#", 1, "normal"))
            # Adresse de résidence
            adresse_ligne1 = self.dictInfosIndividus[IDindividu]["adresse_ligne1"]
            adresse_ligne2 = self.dictInfosIndividus[IDindividu]["adresse_ligne2"]
            if adresse_ligne1 != None and adresse_ligne1 != "" : listeLignes.append((adresse_ligne1, 7, "light"))
            if adresse_ligne2 != None and adresse_ligne2 != ""  : listeLignes.append((adresse_ligne2, 7, "light"))
            # Spacer
            listeLignes.append((u"#SPACER#", 1, "normal"))
            # Téléphones
            tel_domicile_complet = self.dictInfosIndividus[IDindividu]["tel_domicile_complet"]
            tel_mobile_complet = self.dictInfosIndividus[IDindividu]["tel_mobile_complet"]
            travail_tel_complet = self.dictInfosIndividus[IDindividu]["travail_tel_complet"]
            
            if tel_domicile_complet != None :
                listeLignes.append((tel_domicile_complet, 7, "light"))
            elif tel_mobile_complet != None :
                listeLignes.append((tel_mobile_complet, 7, "light"))
            elif travail_tel_complet != None :
                listeLignes.append((travail_tel_complet, 7, "light"))
            else:
                pass
            
            # Création du dictionnaire spécial
            dictCadres[IDindividu] = {}
            dictCadres[IDindividu]["textes"] = listeLignes
            dictCadres[IDindividu]["nomImage"] = self.dictInfosIndividus[IDindividu]["nomImage"]
            dictCadres[IDindividu]["genre"] = self.dictInfosIndividus[IDindividu]["genre"]
            dictCadres[IDindividu]["categorie"] = self.dictInfosIndividus[IDindividu]["categorie"]
            dictCadres[IDindividu]["ctrl"] = None
            dictCadres[IDindividu]["titulaire"] = self.dictInfosIndividus[IDindividu]["titulaire"]
            dictCadres[IDindividu]["IDrattachement"] = self.dictInfosIndividus[IDindividu]["IDrattachement"]
            dictCadres[IDindividu]["inscriptions"] = self.dictInfosIndividus[IDindividu]["inscriptions"]
        
        return dictCadres
    
    def GetDictInfoBulles(self):
        dictInfoBulles = {}
        for IDindividu in self.listeIDindividus :
            txtInfoBulle = u""
            # Ligne NOM
            nomComplet2 = self.dictInfosIndividus[IDindividu]["nomComplet2"]
            txtInfoBulle += u"----------- %s -----------\n\n" % nomComplet2
            # Ligne Date de naissance
            if self.dictInfosIndividus[IDindividu]["date_naiss"] != None :
                txtDatenaiss = self.dictInfosIndividus[IDindividu]["datenaissComplet"]
                txtInfoBulle += txtDatenaiss + "\n\n"
            # Adresse de résidence
            adresse_ligne1 = self.dictInfosIndividus[IDindividu]["adresse_ligne1"]
            adresse_ligne2 = self.dictInfosIndividus[IDindividu]["adresse_ligne2"]
            if adresse_ligne1 != None and adresse_ligne1 != "" : txtInfoBulle += adresse_ligne1 + "\n"
            if adresse_ligne2 != None and adresse_ligne2 != ""  : txtInfoBulle += adresse_ligne2 + "\n"
            # Spacer
            txtInfoBulle += "\n"
            # Téléphones
            tel_domicile_complet = self.dictInfosIndividus[IDindividu]["tel_domicile_complet"]
            tel_mobile_complet = self.dictInfosIndividus[IDindividu]["tel_mobile_complet"]
            travail_tel_complet = self.dictInfosIndividus[IDindividu]["travail_tel_complet"]
            mail_complet = self.dictInfosIndividus[IDindividu]["mail_complet"]
            if tel_domicile_complet != None :
                txtInfoBulle += tel_domicile_complet + "\n"
            if tel_mobile_complet != None :
                txtInfoBulle += tel_mobile_complet + "\n"
            if travail_tel_complet != None :
                txtInfoBulle += travail_tel_complet + "\n"
            if mail_complet != None :
                txtInfoBulle += mail_complet + "\n"
            
            # Création du dictionnaire spécial
            dictInfoBulles[IDindividu] = txtInfoBulle
        
        return dictInfoBulles
    
    def GetTxtDateNaiss(self, dictInfos, IDindividu):
        datenaiss = dictInfos[IDindividu]["date_naiss"]
        txtDatenaiss = _(u"Date de naissance inconnue")
        if datenaiss != None :
            try :
                datenaissDD = datetime.date(year=int(datenaiss[:4]), month=int(datenaiss[5:7]), day=int(datenaiss[8:10]))
                datenaissFR = str(datenaiss[8:10]) + "/" + str(datenaiss[5:7]) + "/" + str(datenaiss[:4])
                datedujour = datetime.date.today()
                age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
                if dictInfos[IDindividu]["genre"] == "M" :
                    txtDatenaiss = _(u"Né le %s (%d ans)") % (datenaissFR, age)
                else:
                    txtDatenaiss = _(u"Née le %s (%d ans)") % (datenaissFR, age)
            except :
                pass
        return txtDatenaiss
        



class CadreIndividu():
    def __init__(self, parent, dc, IDindividu=None, listeTextes=[], genre="M", nomImage=None, xCentre=None, yCentre=None, largeur=None, hauteur=None, numCol=None, titulaire=0, calendrierActif=False):
        self.parent = parent
        self.zoom = 1
        self.zoomContenu = True
        
        self.selectionCadre = False
        self.survolCadre = False
        self.calendrierActif = calendrierActif
        self.survolCalendrier = False
        
        self.IDindividu = IDindividu
        self.dc = dc
        self.IDobjet = wx.NewId()
        self.listeTextes = listeTextes
        self.genre = genre
        self.nomImage = nomImage
        self.bmp = None
        self.numCol = numCol
        self.titulaire = titulaire
        self.xCentre = xCentre
        self.yCentre = yCentre
        self.largeur = largeur
        self.hauteur = hauteur
        
        self.Draw()
    
    def Draw(self):
        largeur = self.largeur
        hauteur = self.hauteur
        
        # Création de l'ID pour le dictionnaire d'objets
        if self.parent.dictIDs.has_key(self.IDobjet) : 
            self.dc.RemoveId(self.IDobjet)
        self.dc.SetId(self.IDobjet)
        
        # Zoom Cadre
        if self.zoom != 1 :
            largeur, hauteur = largeur*self.zoom, hauteur*self.zoom
            
        # Zoom Contenu
        if self.zoomContenu == True :
            self.zoomContenuRatio = self.zoom
        else:
            self.zoomContenuRatio = 1
            
        # Paramètres du cadre
        x, y = self.xCentre-(largeur/2.0), self.yCentre-(hauteur/2.0)
        self.x, self.y = x, y
        if self.genre == "M" :
            couleurFondHautCadre = (217, 212, 251)
            couleurFondBasCadre = (196, 188, 252)
        else:
            couleurFondHautCadre = (251, 212, 239)
            couleurFondBasCadre = (253, 193, 235)
        couleurBordCadre = (0, 0, 0)
        couleurSelectionCadre = (133, 236, 90)
        paddingCadre = 8*self.zoomContenuRatio
        taillePhoto = (self.hauteur-(paddingCadre*2))*self.zoomContenuRatio
        
        # Dessin du cadre de sélection
        if self.selectionCadre == True :
            ecart = 5
            self.dc.SetBrush(wx.Brush((0, 0, 0), style=wx.TRANSPARENT))
            self.dc.SetPen(wx.Pen(couleurSelectionCadre, 1, wx.DOT))
            self.dc.DrawRoundedRectangleRect(wx.Rect(x-ecart, y-ecart, largeur+(ecart*2), hauteur+(ecart*2)), radius=5*self.zoom)
        
        # Dessin du cadre
        self.dc.SetBrush(wx.Brush(couleurFondBasCadre))
        self.dc.SetPen(wx.Pen(couleurBordCadre, 1))
        self.dc.DrawRoundedRectangleRect(wx.Rect(x, y, largeur, hauteur), radius=5*self.zoom)
        
        coordsSpline = [(x+1, y+(hauteur/3)), (x+(largeur/2.5), y+(hauteur/4.1)), (x+largeur-1, y+(hauteur/1.8))]
        self.dc.DrawSpline(coordsSpline)
        
        self.dc.SetBrush(wx.Brush(couleurFondHautCadre) )
        self.dc.FloodFill(x+5, y+5, couleurBordCadre, style=wx.FLOOD_BORDER )
        
        self.dc.SetPen(wx.Pen(couleurFondBasCadre, 1))
        self.dc.DrawSpline(coordsSpline)
        
        # Intégration de la photo
        if self.nomImage == None : self.nomImage = "Personne.png"
        nomFichier = "Images/128x128/%s" % self.nomImage
        IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=self.IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=wx.IMAGE_QUALITY_HIGH)
        self.dc.DrawBitmap(bmp, x+paddingCadre, y+paddingCadre)
        self.bmp = bmp
        
        # Dessin du texte
        largeurMaxiTexte = largeur - paddingCadre*3- taillePhoto
        hauteurMaxiTexte = hauteur - paddingCadre
        posXtexte = x + paddingCadre*2 + taillePhoto -2
        posYtexte = y + paddingCadre -2
        for texte, tailleFont, styleFont in self.listeTextes :
            # Font
            font = self.parent.GetFont()
            font.SetPointSize(tailleFont*self.zoomContenuRatio)
            if styleFont == "normal" : font.SetWeight(wx.FONTWEIGHT_NORMAL)
            if styleFont == "light" : font.SetWeight(wx.FONTWEIGHT_LIGHT)
            if styleFont == "bold" : font.SetWeight(wx.FONTWEIGHT_BOLD)
            self.parent.SetFont(font)
            self.dc.SetFont(font)
            # Texte
            largeurTexte, hauteurTexte = self.parent.GetTextExtent(texte)
            if (posYtexte - y + hauteurTexte) < hauteurMaxiTexte :
                if largeurTexte > largeurMaxiTexte :
                    texte = self.AdapteLargeurTexte(self.dc, texte, largeurMaxiTexte)
                if texte == "#SPACER#" : texte = " "
                self.dc.DrawText(texte, posXtexte, posYtexte)
                posYtexte += hauteurTexte + 1
        
        # Dessin du cadre Accès aux consommations
        if self.calendrierActif == True and self.zoom > 1 :
            # Image de calendrier
            if self.survolCalendrier == True :
                bmpConso = wx.Bitmap("Images/32x32/Calendrier_modifier.png", wx.BITMAP_TYPE_ANY) 
            else:
                bmpConso = wx.Bitmap("Images/32x32/Calendrier.png", wx.BITMAP_TYPE_ANY) 
            xBmpConso, yBmpConso = x+largeur-5-32, y+5
            self.dc.DrawBitmap(bmpConso, xBmpConso, yBmpConso)
        
        # Dessin du symbole TITULAIRE
        if self.titulaire == 1 :
            bmpTitulaire = wx.Bitmap("Images/16x16/Titulaire.png", wx.BITMAP_TYPE_ANY) 
            xBmpTitulaire, yBmpTitulaire = x+largeur-5-32, y+5
            self.dc.DrawBitmap(bmpTitulaire, x+paddingCadre, y+paddingCadre+2)
            
        # Mémorisation dans le dictionnaire d'objets
        self.dc.SetIdBounds(self.IDobjet, wx.Rect(x, y, largeur, hauteur)) 
        self.parent.dictIDs[self.IDobjet] = ("individu", self.IDindividu)
    
    def SurvolCalendrier(self, x, y):
        largeurCadre, hauteurCadre = self.largeur*self.zoom, self.hauteur*self.zoom
        xBmpConso, yBmpConso = self.x+largeurCadre-5-32, self.y+5
        if (y >= self.y+4 and y <= self.y+6+32) and (x >= xBmpConso-1 and x <= xBmpConso+32+1) :
            return True
        else:
            return False
        
    def AdapteLargeurTexte(self, dc, texte, tailleMaxi):
        """ Raccourcit le texte en fonction de la taille donnée """
        tailleTexte = self.parent.GetTextExtent(texte)[0]
        texteTemp, texteTemp2 = "", ""
        for lettre in texte :
            texteTemp += lettre
            if self.parent.GetTextExtent(texteTemp +"...")[0] <= tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..."
    
    def Selectionne(self, etat=True):
        if etat == True :
            self.selectionCadre = True
        else:
            self.selectionCadre = False
        self.Draw()
        self.parent.Refresh()
        self.parent.Update()
    
    def ActiveCalendrier(self, etat):
        self.survolCalendrier = etat
        self.Draw()
        self.parent.Refresh()
        self.parent.Update()
        
    def ZoomAvant(self, coef=2, vitesse=1):
        if self.zoom == 1 :
            for x in range(10, int(coef*10)):
                self.zoom = (x*0.1)+0.1
                wx.Usleep(vitesse)
                self.Draw()
                self.parent.Refresh()
                self.parent.Update()
    
    def ZoomArriere(self, vitesse=0.5):
        if self.zoom > 1 :
            for x in range(int(self.zoom*10), 10-1, -1):
                self.zoom = (x*0.1)
                wx.Usleep(vitesse)
                self.Draw()
                self.parent.Refresh()
                self.parent.Update()


class LienCadreFiliation():
    def __init__(self, parent, IDobjetLien, dc, IDenfant, listeParents, nbreLiensFiliation):
        self.parent = parent
        self.dc = dc
        self.IDobjetLien = IDobjetLien
        self.IDobjet = wx.NewId()
        self.dictCadres = self.parent.dictCadres
        self.IDenfant = IDenfant
        self.listeParents = listeParents
        self.nbreLiensFiliation = nbreLiensFiliation
        self.posSeparationBlocs = self.parent.posSeparationCol1
        
        self.Draw()
    
    def Draw(self):
        # Création de l'ID pour le dictionnaire d'objets
        if self.parent.dictIDs.has_key(self.IDobjet) : 
            self.dc.RemoveId(self.IDobjet)
        self.dc.SetId(self.IDobjet)
        
        posXLigneParents = self.posSeparationBlocs-5
        posXLigneEnfants = self.posSeparationBlocs+5
        
        # Dessine la ligne qui part du cadre ENFANT
        xCadreEnfant = self.dictCadres[self.IDenfant]["ctrl"].xCentre
        yCadreEnfant = self.dictCadres[self.IDenfant]["ctrl"].yCentre
        largeurCadreEnfant = self.dictCadres[self.IDenfant]["ctrl"].largeur*self.dictCadres[self.IDenfant]["ctrl"].zoom
        bordCadreEnfant = (xCadreEnfant-largeurCadreEnfant/2.0, yCadreEnfant)
        extremiteLigneEnfant = (posXLigneEnfants, yCadreEnfant)
        self.dc.SetPen(wx.Pen((0, 0, 0), 1))
        self.dc.DrawLinePoint(bordCadreEnfant, extremiteLigneEnfant)
        
        # Dessine la ligne qui part de chaque cadre PARENT
        listePointsParents = []
        for IDparent in self.listeParents :
            xCentre = self.dictCadres[IDparent]["ctrl"].xCentre
            yCentre = self.dictCadres[IDparent]["ctrl"].yCentre
            largeur = self.dictCadres[IDparent]["ctrl"].largeur*self.dictCadres[IDparent]["ctrl"].zoom
            bordCadre = (xCentre+largeur/2.0, yCentre)
            extremiteLigne = (posXLigneParents, yCentre)
            self.dc.SetPen(wx.Pen((0, 0, 0), 1))
            self.dc.DrawLinePoint(bordCadre, extremiteLigne)
            listePointsParents.append(extremiteLigne)
        
        # Barre qui relient les parents
        pointBas, pointHaut = listePointsParents[0][0], listePointsParents[0][1]
        for x, y in listePointsParents :
            print "x=", x, "y=", y
            if y < pointBas : pointBas = y
            if y > pointHaut : pointHaut = y
        print pointBas, pointHaut
        self.dc.DrawLine(posXLigneParents, pointBas, posXLigneParents, pointHaut)

        # Mémorisation dans le dictionnaire d'objets
        self.parent.dictIDs[self.IDobjet] = ("lien", self.IDobjetLien)


class CTRL_Graphique(wx.ScrolledWindow):
    def __init__(self, parent, IDfamille=None):
        wx.ScrolledWindow.__init__(self, parent, -1, (0, 0), size=wx.DefaultSize, name="famille", style=wx.SUNKEN_BORDER)
        self.parent = parent
        self.IDfamille = IDfamille
        self.selectionCadre = None
        
        # Initialisation du tooltip
##        self.SetToolTipString("")
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip après 10 secs
        self.tip.IDindividu = None
        
        # Paramètres
        self.zoomActif = True # Active ou non le zoom sur une case
        self.espaceVerticalDefaut = 22 # Hauteur entre 2 cases
        self.espaceHorizontalDefautCol1 = 40 # Espace après col 1
        self.espaceHorizontalDefautCol2 = 80 # Espace après col 2
        self.hauteurCaseDefaut = 75 #70 # Hauteur par défaut d'une case
        self.largeurCaseDefaut = 210 # Largeur par défaut d'une case
        
        self.couleurFondCol1 = (238, 253, 252)
        self.couleurFondCol2 = (238, 253, 252)
        self.couleurFondCol3 = (214, 250, 199)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        
        
        # create a PseudoDC to record our drawing
        self.pdc = wx.PseudoDC()
        self.dictIDs = {}
##        self.DoDrawing(self.pdc)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.MAJ()
        event.Skip()

    def MAJ(self):
        self.DoDrawing(self.pdc)
        self.Refresh()
                   
    def OnPaint(self, event):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  
        dc = wx.BufferedPaintDC(self)
        # use PrepateDC to set position correctly
        if wx.VERSION < (2, 9, 0, 0) :
            self.PrepareDC(dc)
        # we need to clear the dc BEFORE calling PrepareDC
        colFond = wx.SystemSettings.GetColour(30) #self.GetBackgroundColour()
        bg = wx.Brush(colFond)
        dc.SetBackground(bg)
        dc.Clear()
        # create a clipping rect from our position and size
        # and the Update Region
        xv, yv = self.GetViewStart()
        dx, dy = self.GetScrollPixelsPerUnit()
        x, y   = (xv * dx, yv * dy)
        rgn = self.GetUpdateRegion()
        rgn.Offset(x,y)
        r = rgn.GetBox()
        # draw to the dc using the calculated clipping rect
        self.pdc.DrawToDCClipped(dc,r)
        
    def DoDrawing(self, dc):
        """ Creation du dessin dans le PseudoDC """
        dc.RemoveAll()
        dc.BeginDrawing()
        tailleDC = self.GetSizeTuple()[0], self.GetSizeTuple()[1]      
        
        # Récupération des valeurs        
        valeurs = GetValeurs(self.IDfamille)
        self.dictValeurs = valeurs
        self.dictCadres = valeurs.GetDictCadres()
        self.dictInfoBulles = valeurs.GetDictInfoBulles()
        self.dictLiensCadres = valeurs.GetLiensCadres()
        
        # Calcul des positions horizontales des cases
        largeurCase = self.largeurCaseDefaut
        largeurBloc = (3*largeurCase)+self.espaceHorizontalDefautCol1+self.espaceHorizontalDefautCol2
        xBloc = (tailleDC[0]/2.0) - (largeurBloc/2.0)
        xBloc1 = xBloc + (largeurCase/2.0)
        
        posSeparationCol1 = xBloc1+(largeurCase/2.0)+(self.espaceHorizontalDefautCol1/2.0)
        posSeparationCol2 = posSeparationCol1 +(self.espaceHorizontalDefautCol1/2.0) + largeurCase + (self.espaceHorizontalDefautCol2/2.0)
        
        self.posSeparationCol1 = posSeparationCol1
        self.posSeparationCol2 = posSeparationCol2
        
        # Création des colonnes
        dictColonnes = { 1 : [], 2 : [], 3 : [] }
        for IDindividu, valeurs in self.dictCadres.iteritems() :
            if valeurs["categorie"] == 1 : dictColonnes[1].append(IDindividu)
            if valeurs["categorie"] == 2 : dictColonnes[2].append(IDindividu)
            if valeurs["categorie"] == 3 : dictColonnes[3].append(IDindividu)
        
        xCentre = xBloc1
        
        for numCol in [1, 2, 3] :
            nbreCases = len(dictColonnes[numCol])
            espaceVertical = self.espaceVerticalDefaut
            dc.SetId(numCol)
            
            # Diminue la hauteur des cases si la fenêtre est trop petite
            hauteurBloc = (nbreCases*self.hauteurCaseDefaut)+(nbreCases-1)*espaceVertical
            coef = (tailleDC[1]-60) * 1.0 / hauteurBloc
            if coef < 1 :
                hauteurCase = self.hauteurCaseDefaut * coef
                if hauteurCase < 28 : 
                    hauteurCase = 28
                if hauteurCase < 70 : 
                    espaceVertical = self.espaceVerticalDefaut * coef
            else:
                hauteurCase = self.hauteurCaseDefaut
            
            # Calcul des positions verticales des cases
            hauteurBloc = (nbreCases*hauteurCase)+(nbreCases-1)*espaceVertical
            yBloc = (tailleDC[1]/2.0) - (hauteurBloc/2.0)
            yBloc1 = yBloc + (hauteurCase/2.0) + 10
            
            # Dessin du fond de couleur
            paramFond = {
                1 : { "couleurFond" : self.couleurFondCol1, "x" : 0, "width" : posSeparationCol1, "nomImage" : "GeneaResponsables.png"},
                2 : { "couleurFond" : self.couleurFondCol2, "x" : posSeparationCol1, "width" : posSeparationCol2-posSeparationCol1, "nomImage" : "GeneaEnfants.png"},
                3 : { "couleurFond" : self.couleurFondCol3, "x" : posSeparationCol2, "width" : tailleDC[0]-posSeparationCol2, "nomImage" : "GeneaContacts.png"},
            }
            if paramFond.has_key(numCol) : 
                dc.SetBrush(wx.Brush(paramFond[numCol]["couleurFond"]))
                dc.SetPen(wx.Pen(paramFond[numCol]["couleurFond"], 0))
                dc.DrawRectangle(x=paramFond[numCol]["x"], y=0, width=paramFond[numCol]["width"], height=tailleDC[1])
                bmp = wx.Bitmap("Images/Special/%s" % paramFond[numCol]["nomImage"], wx.BITMAP_TYPE_PNG)
                dc.DrawBitmap(bmp, xCentre-(bmp.GetSize()[0]/2.0), 10)
            
            # Création des cases
            yCentre = yBloc1
            for IDindividu in dictColonnes[numCol] :
                listeTextes = self.dictCadres[IDindividu]["textes"]
                genre = self.dictCadres[IDindividu]["genre"]
                nomImage = self.dictCadres[IDindividu]["nomImage"]
                titulaire = self.dictCadres[IDindividu]["titulaire"] 
                calendrierActif = self.dictCadres[IDindividu]["inscriptions"]
                cadre = CadreIndividu(self, dc, IDindividu, listeTextes, genre, nomImage, xCentre, yCentre, largeurCase, hauteurCase, numCol, titulaire, calendrierActif)
                self.dictCadres[IDindividu]["ctrl"] = cadre
                yCentre += hauteurCase + espaceVertical
            
            if numCol == 1 : xCentre += largeurCase + self.espaceHorizontalDefautCol1
            if numCol == 2 : xCentre += largeurCase + self.espaceHorizontalDefautCol2
        
        # Dessin des liens de cadres
        dc.SetId(wx.NewId())
        self.DrawLiens(dc)
        
        dc.EndDrawing()
    
    def DrawLiensCouple(self, dc, listeLiensCouple, type=""):
        nbreLiensCouple = len(listeLiensCouple)
        for IDindividu1, IDindividu2 in listeLiensCouple :
            if self.dictCadres.has_key(IDindividu1) and self.dictCadres.has_key(IDindividu2) :
                dc.SetId(wx.NewId())
                decalage = 20 # Décalage de la ligne de lien par rapport au bord du cadre
                listePoints = []
                for IDindividu in (IDindividu1, IDindividu2) :
                    xCentre = self.dictCadres[IDindividu]["ctrl"].xCentre
                    yCentre = self.dictCadres[IDindividu]["ctrl"].yCentre
                    largeur = self.dictCadres[IDindividu]["ctrl"].largeur*self.dictCadres[IDindividu]["ctrl"].zoom
                    bordCadre = (xCentre-largeur/2.0-1, yCentre)
                    extremiteLigne = (xCentre-largeur/2.0-decalage, yCentre)
                    dc.SetPen(wx.Pen((123, 241, 131), 1, wx.DOT))
                    dc.DrawLinePoint(bordCadre, extremiteLigne)
                    listePoints.append(extremiteLigne)
                # Barre qui relie
                dc.DrawLinePoint(listePoints[0], listePoints[1])
                # Dessin d'un bitmap
                if type == "ex-couple" :
                    bmpCouple = wx.Bitmap("Images/16x16/Divorce.png", wx.BITMAP_TYPE_PNG) 
                    dc.DrawBitmap(bmpCouple, extremiteLigne[0]-8, (listePoints[0][1]-listePoints[1][1])/2.0+listePoints[1][1]-8)
                
            
    def DrawLiens(self, dc):
        for numCol in [1, 2, 3] :
            # Dessin des liens de couple
            listeLiensCouple = self.dictLiensCadres[numCol]["couple"]
            if len(listeLiensCouple) > 0 :
                self.DrawLiensCouple(dc, listeLiensCouple, type="couple")
            listeLiensCouple = self.dictLiensCadres[numCol]["ex-couple"]
            if len(listeLiensCouple) > 0 :
                self.DrawLiensCouple(dc, listeLiensCouple, type="ex-couple")
            
            # Recherche des liens de filiation
            dictLiensFiliation = self.dictLiensCadres[numCol]["filiation"]            
            dictParents = {}
            for IDenfant, listeParents in dictLiensFiliation.iteritems() :
                listeParents = tuple(listeParents)
                if dictParents.has_key(listeParents) == False :
                    dictParents[listeParents] = [IDenfant,]
                else:
                    dictParents[listeParents].append(IDenfant)

            nbreLiensFiliation = len(dictParents)
            
            if nbreLiensFiliation == 1 : posCentrale = [self.posSeparationCol1,]
            if nbreLiensFiliation == 2 : posCentrale = [self.posSeparationCol1-2, self.posSeparationCol1+2]
            if nbreLiensFiliation == 3 : posCentrale = [self.posSeparationCol1-4, self.posSeparationCol1, self.posSeparationCol1+4]
            if nbreLiensFiliation == 4 : posCentrale = [self.posSeparationCol1-6, self.posSeparationCol1-2, self.posSeparationCol1+2, self.posSeparationCol1+6]
            if nbreLiensFiliation == 5 : posCentrale = [self.posSeparationCol1-8, self.posSeparationCol1-4, self.posSeparationCol1, self.posSeparationCol1+4, self.posSeparationCol1+8]
            
            # Dessin des liens de filiation
            index = 0
            for listeParents, listeEnfants in dictParents.iteritems() :
                posXLigneParents = posCentrale[index]
                posXLigneEnfants = posXLigneParents
                
                # Dessine les liens ENFANTS
                listeYenfants = []
                for IDenfant in listeEnfants :
                    xCadreEnfant = self.dictCadres[IDenfant]["ctrl"].xCentre
                    yCadreEnfant = self.dictCadres[IDenfant]["ctrl"].yCentre
                    largeurCadreEnfant = self.dictCadres[IDenfant]["ctrl"].largeur*self.dictCadres[IDenfant]["ctrl"].zoom
                    bordCadreEnfant = (xCadreEnfant-largeurCadreEnfant/2.0, yCadreEnfant)
                    extremiteLigneEnfant = (posXLigneEnfants, yCadreEnfant)
                    listeYenfants.append(yCadreEnfant)
                    dc.SetPen(wx.Pen((0, 0, 0), 1))
                    dc.DrawLinePoint(bordCadreEnfant, extremiteLigneEnfant)
                # Relient les enfants par une ligne VERTICALE
                if len(listeYenfants) > 0 :
                    dc.DrawLine(posXLigneEnfants, min(listeYenfants), posXLigneEnfants, max(listeYenfants))
                centreYenfants = sum(listeYenfants)/len(listeYenfants)
                
                # Dessine les liens PARENTS
                listeYparents = []
                for IDparent in listeParents :
                    xCentre = self.dictCadres[IDparent]["ctrl"].xCentre
                    yCentre = self.dictCadres[IDparent]["ctrl"].yCentre
                    largeur = self.dictCadres[IDparent]["ctrl"].largeur*self.dictCadres[IDparent]["ctrl"].zoom
                    bordCadre = (xCentre+largeur/2.0, yCentre)
                    extremiteLigneParent = (posXLigneParents, yCentre)
                    listeYparents.append(yCentre)
                    dc.SetPen(wx.Pen((0, 0, 0), 1))
                    dc.DrawLinePoint(bordCadre, extremiteLigneParent)
                # Relient les parents par une ligne VERTICALE
                if len(listeYparents) > 0 :
                    dc.DrawLine(posXLigneParents, min(listeYparents), posXLigneParents, max(listeYparents))
                centreYparents = sum(listeYparents)/len(listeYparents)
                
                # Relie la barre ENFANTS à la barre PARENTS
                hauteurBarreHorizontale = centreYenfants
                dc.DrawLine(posXLigneParents, hauteurBarreHorizontale, posXLigneEnfants, hauteurBarreHorizontale)
                
                # Rallonge de la barre verticale adulte
                dc.DrawLine(posXLigneParents, hauteurBarreHorizontale, posXLigneParents, max(listeYparents))
                dc.DrawLine(posXLigneParents, hauteurBarreHorizontale, posXLigneParents, min(listeYparents))
        
                index += 1
        
    def RechercheCadre(self, x, y):
        """ Recherche le cadre présent sur x, y """
        listeObjets = self.pdc.FindObjectsByBBox(x, y)
        if len(listeObjets) != 0 :
            IDobjet = listeObjets[0]
            if self.dictIDs.has_key(IDobjet) :
                if self.dictIDs[IDobjet][0] == "individu" :
                    IDindividu = self.dictIDs[IDobjet][1]
                    return IDindividu
        return None
    
    def DeselectionneTout(self, ExcepteIDindividu=None):
        """ Désélectionne tous les cadres du dc """
        for IDindividuTmp, valeurs in self.dictCadres.iteritems() :
            if ExcepteIDindividu != IDindividuTmp :
                cadre = self.dictCadres[IDindividuTmp]["ctrl"]
                if cadre.selectionCadre == True :
                    cadre.Selectionne(False)

    def DezoomTout(self, ExcepteIDindividu=None):
        """ Désélectionne tous les cadres du dc """
        for IDindividuTmp, valeurs in self.dictCadres.iteritems() :
            if ExcepteIDindividu != IDindividuTmp :
                cadre = self.dictCadres[IDindividuTmp]["ctrl"]
                if cadre.zoom != 1 :
                    cadre.ZoomArriere(vitesse=0.1)
    
    def OnLeftDown(self, event):
        """ Sélection d'un cadre """
        x, y = event.GetPosition()
        IDindividu = self.RechercheCadre(x, y)
        self.ActiveTooltip(False) 
        if IDindividu != None :
            cadre = self.dictCadres[IDindividu]["ctrl"]
            # Si le calendrier est pointé, on l'ouvre
            if cadre.survolCalendrier == True :
                self.OuvrirCalendrier(IDindividu)
            else:
                # Sélectionne le cadre pointé
                self.DeselectionneTout(ExcepteIDindividu=IDindividu)
                if cadre.selectionCadre == False :
                    cadre.Selectionne(True)
                    self.selectionCadre = IDindividu
                else:
                    cadre.Selectionne(False)
                    self.selectionCadre = None
        else:
            # On désélectionne tout si on clique à côté
            self.selectionCadre = None
            self.DeselectionneTout()
        
    def OnDLeftDown(self, event):
        """ Un double-clic ouvre la fiche pointée """
        x, y = event.GetPosition()
        IDindividu = self.RechercheCadre(x, y)
        self.ActiveTooltip(False) 
        if IDindividu != None :
            self.Modifier(IDindividu)        
        
    def OnMotion(self, event):
        x, y = event.GetPosition()
        IDindividu = self.RechercheCadre(x, y)
        if IDindividu != None :
            cadre = self.dictCadres[IDindividu]["ctrl"]
            # On met le tooltip
            self.ActiveTooltip(actif=True, IDindividu=IDindividu)
            
            # Modification de la taille du cadre
            if self.zoomActif == True :
                self.DezoomTout(ExcepteIDindividu=IDindividu) 
                cadre.ZoomAvant(coef=1.1, vitesse=0.5)
                # Recherche si l'image calendrier est survolée
                if cadre.calendrierActif == True :
                    survolCalendrier = cadre.SurvolCalendrier(x, y)
                    if survolCalendrier == True :
                        cadre.ActiveCalendrier(True)
                        self.SetCursor(wx.StockCursor(wx.CURSOR_MAGNIFIER))
                    else:
                        cadre.ActiveCalendrier(False)
                        # Change le curseur de la souris
                        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
                else:
                    # Change le curseur de la souris
                    self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else:
            # Désactivation du toolTip
            self.ActiveTooltip(actif=False)
            
            # Change le curseur de la souris
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            # Dézoom tous les cadres
            self.DezoomTout() 
    
            
    def OnLeaveWindow(self, event):
        """ Rétablit le zoom normal pour tous les cadres si le focus quitte la fenêtre """
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        self.DezoomTout()
        self.ActiveTooltip(False) 

    def AfficheTooltip(self):
        styleTooltip = "Office 2007 Blue"
        taillePhoto = 30
        font = self.GetFont()
        
        # Récupération des infos sur l'individu
        IDindividu = self.tip.IDindividu
        cadreIndividu = self.dictCadres[IDindividu]["ctrl"]
        dictInfoIndividu = self.dictValeurs.dictInfosIndividus[IDindividu]
        
        # Paramétrage du tooltip
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        if dictInfoIndividu["genre"] == "F" :
            # Couleur du toolTip version FILLE
            self.tip.SetTopGradientColour(wx.Colour(255,255,255))
            self.tip.SetMiddleGradientColour(wx.Colour(251,229,243))
            self.tip.SetBottomGradientColour(wx.Colour(255,210,226))
            self.tip.SetTextColor(wx.Colour(76,76,76))
        else:
            # Couleur du toolTip version GARCON
            self.tip.SetTopGradientColour(wx.Colour(255,255,255))
            self.tip.SetMiddleGradientColour(wx.Colour(242,246,251))
            self.tip.SetBottomGradientColour(wx.Colour(202,218,239))
            self.tip.SetTextColor(wx.Colour(76,76,76))
        
        # Adaptation pour wxPython >= 2.9
        if wx.VERSION > (2, 9, 0, 0) :
            qualite = wx.IMAGE_QUALITY_BICUBIC
        else :
            qualite = 100
            
        # Titre du tooltip
        bmp = cadreIndividu.bmp
        bmp = bmp.ConvertToImage()

        bmp = bmp.Rescale(width=taillePhoto, height=taillePhoto, quality=qualite) 
        bmp = bmp.ConvertToBitmap()
        self.tip.SetHeaderBitmap(bmp)
        self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetHeader(dictInfoIndividu["nomComplet2"])
        self.tip.SetDrawHeaderLine(True)
        
        # Corps du tooltip
        message = u""
        if dictInfoIndividu["datenaissComplet"] != None : message += u"%s\n" % dictInfoIndividu["datenaissComplet"]
        
        adresse = u""
        if dictInfoIndividu["adresse_ligne1"] not in (None, u"") : adresse += u"</b>%s\n" % dictInfoIndividu["adresse_ligne1"]
        if dictInfoIndividu["adresse_ligne2"] not in (None, u"") : adresse += u"</b>%s\n" % dictInfoIndividu["adresse_ligne2"]
        if len(adresse) > 3 : 
            message += "\n" + adresse
        
        coords = u""
        if dictInfoIndividu["tel_domicile_complet"] not in (None, u"") : coords += u"%s\n" % dictInfoIndividu["tel_domicile_complet"] 
        if dictInfoIndividu["tel_mobile_complet"] not in (None, u"") : coords += u"%s\n" % dictInfoIndividu["tel_mobile_complet"] 
        if dictInfoIndividu["travail_tel_complet"] not in (None, u"") : coords += u"%s\n" % dictInfoIndividu["travail_tel_complet"]
        if len(coords) > 3 : 
            message += "\n" + coords
        if dictInfoIndividu["mail_complet"] != None : message += u"\n%s \n" % dictInfoIndividu["mail_complet"]
        
        # Liste des inscriptions de l'individu
        if dictInfoIndividu["genre"] == "F" :
            lettreGenre = "e"
        else:
            lettreGenre = ""
        if dictInfoIndividu["prenom"] != None :
            prenom = dictInfoIndividu["prenom"]
        else:
            prenom = u""
        if dictInfoIndividu["inscriptions"] == True :
            nbreInscriptions = len(dictInfoIndividu["listeInscriptions"])
            message += "\n"
            if nbreInscriptions == 1 :
                message += _(u"%s est inscrit%s à 1 activité : \n") % (prenom, lettreGenre)
            else:
                message += _(u"%s est inscrit%s à %d activités : \n") % (prenom, lettreGenre, nbreInscriptions)
            for dictInscription in dictInfoIndividu["listeInscriptions"] :
                message += "> %s (%s - %s) \n" % (dictInscription["nomActivite"], dictInscription["nomGroupe"], dictInscription["nomCategorie"])

        self.tip.SetMessage(message)
        
        # Pied du tooltip
        self.tip.SetDrawFooterLine(True)
        self.tip.SetFooterBitmap(wx.Bitmap(u"Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        self.tip.SetFooterFont(wx.Font(7, font.GetFamily(), font.GetStyle(), wx.LIGHT, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetFooter(_(u"Double-cliquez pour ouvrir sa fiche"))
        
        # Affichage du Frame tooltip
        self.tipFrame = STT.ToolTipWindow(self, self.tip)
        self.tipFrame.CalculateBestSize()
        x, y = wx.GetMousePosition()
        self.tipFrame.SetPosition((x+15, y+17))
        self.tipFrame.DropShadow(True)
        self.tipFrame.StartAlpha(True) # ou .Show() pour un affichage immédiat
        
        # Arrêt du timer
        self.timerTip.Stop()
        del self.timerTip
                    
    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try :
                self.tipFrame.Destroy()
            except :
                pass
            del self.tipFrame
            self.tip.IDindividu = None
        
    def ActiveTooltip(self, actif=True, IDindividu=None):
        # Pour éviter que l'utilisateur bouge la souris trop vite
        if self.tip.IDindividu != None and self.tip.IDindividu != IDindividu :
            actif = False
            
        if actif == True :
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False :
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(1500)
                self.tip.IDindividu = IDindividu
        else:
            # Désactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.IDindividu = None
            self.CacheTooltip() 

    def OuvrirCalendrier(self, IDindividu=None):
        """ Ouverture du calendrier de l'individu """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "consulter") == False : return
        self.parent.Sauvegarde()
        import DLG_Grille
        dlg = DLG_Grille.Dialog(self, IDfamille=self.IDfamille, selectionIndividus=[IDindividu,])
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJnotebook()
        dlg.Destroy()
    
    def Calendrier_selection(self):
        IDindividu = self.selectionCadre

        if IDindividu == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans le cadre Composition !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   

        if self.dictValeurs.dictInfosIndividus[IDindividu]["inscriptions"] == False :
            dlg = wx.MessageDialog(self, _(u"L'individu sélectionné n'est inscrit à aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   

        self.OuvrirCalendrier(IDindividu)

    def OnContextMenu(self, event):
        x, y = event.GetPosition()
        self.ActiveTooltip(False) 
        
        # Recherche si un cadre est survolé
        IDindividu = self.RechercheCadre(x, y)
        self.IDindividu_menu = IDindividu
        
        # Désélectionne tous les cadres déjà sélectionnés
        self.DeselectionneTout() 
        
        # Création du menu
        menu = wx.Menu()
                        
        # Ajouter
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Rattacher un individu"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=id)
        
        if IDindividu != None :
            
            menu.AppendSeparator()
            
            # Modifier
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"Modifier"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier_menu, id=id)
            
            # Détacher ou supprimer
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"Détacher ou supprimer"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer_menu, id=id)
            
            menu.AppendSeparator()
            
            # Changer de catégorie
            sousMenuCategorie = wx.Menu()
            
            item = wx.MenuItem(sousMenuCategorie, 601, _(u"Représentant"), kind=wx.ITEM_RADIO)
            sousMenuCategorie.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Changer_categorie, id=601)
            if self.dictCadres[self.IDindividu_menu]["categorie"] == 1 : item.Check(True)
            
            item = wx.MenuItem(sousMenuCategorie, 602, _(u"Enfant"), kind=wx.ITEM_RADIO)
            sousMenuCategorie.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Changer_categorie, id=602)
            if self.dictCadres[self.IDindividu_menu]["categorie"] == 2 : item.Check(True)
            
            item = wx.MenuItem(sousMenuCategorie, 603, _(u"Contact"), kind=wx.ITEM_RADIO)
            sousMenuCategorie.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Changer_categorie, id=603)
            if self.dictCadres[self.IDindividu_menu]["categorie"] == 3 : item.Check(True)
            
            menu.AppendMenu(wx.NewId(), _(u"Changer de catégorie"), sousMenuCategorie)
            
            # Définir comme titulaire
            if self.dictCadres[self.IDindividu_menu]["categorie"] == 1 :
                id = wx.NewId()
                item = wx.MenuItem(menu, id, _(u"Définir comme titulaire"), kind=wx.ITEM_CHECK)
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.On_SetTitulaire, id=id)
                if self.dictCadres[self.IDindividu_menu]["titulaire"] == 1 :
                    item.Check(True)
               
        # Finalisation du menu
        self.PopupMenu(menu)           
        menu.Destroy()
        self.IDindividu_menu = None
    
    def Changer_categorie(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "modifier") == False : return
        IDcategorie = event.GetId() - 600
        IDrattachement = self.dictCadres[self.IDindividu_menu]["IDrattachement"]
        if IDcategorie != self.dictCadres[self.IDindividu_menu]["categorie"] :
            dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment modifier la catégorie de rattachement de cet individu ?"), _(u"Changement de catégorie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES :
                DB = GestionDB.DB()
                DB.ReqMAJ("rattachements", [("IDcategorie", IDcategorie),], "IDrattachement", IDrattachement)
                DB.Close()
                self.MAJ() 
                self.MAJnotebook() 
            dlg.Destroy()
        
    def On_SetTitulaire(self, event):
        if self.dictCadres[self.IDindividu_menu]["titulaire"] == 1 :
            # Recherche s'il restera au moins un titulaire dans cette famille
            nbreTitulaires = 0
            for IDindividu, dictCadre in self.dictCadres.iteritems() :
                if dictCadre["titulaire"] == 1 : 
                    nbreTitulaires += 1
            if nbreTitulaires == 1 :
                dlg = wx.MessageDialog(self, _(u"Vous devez avoir au moins un titulaire de dossier dans une famille !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return   
            etat = 0
            self.dictCadres[self.IDindividu_menu]["titulaire"] = 0
        else:
            etat = 1
            self.dictCadres[self.IDindividu_menu]["titulaire"] = 1
        DB = GestionDB.DB()
        req = "UPDATE rattachements SET titulaire=%d WHERE IDindividu=%d AND IDfamille=%d;" % (etat, self.IDindividu_menu, self.IDfamille)
        DB.ExecuterReq(req)
        DB.Commit()
        DB.Close()
        self.MAJ() 
        self.MAJnotebook() 
        
    def Ajouter(self, event=None):
        """ Rattacher un nouvel individu """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "creer") == False : return
        import DLG_Rattachement
        dlg = DLG_Rattachement.Dialog(None, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            mode, IDcategorie, titulaire, IDindividu, nom, prenom = dlg.GetData()
            dlg.Destroy()
            if mode == "creation" :
                # Création d'un nouvel individu rattaché
                dictInfosNouveau = {
                    "IDfamille" : self.IDfamille,
                    "IDcategorie" : IDcategorie,
                    "titulaire" : titulaire,
                    "nom" : nom,
                    "prenom" : prenom,
                    }
                dlg = DLG_Individu.Dialog(None, IDindividu=None, dictInfosNouveau=dictInfosNouveau)
                if dlg.ShowModal() == wx.ID_OK:
                    IDindividu = dlg.IDindividu #print "Nouvelle fiche creee et deja rattachee."
                else:
                    self.SupprimerFamille() 
                dlg.Destroy()
            else:
                # Rattachement d'un individu existant
                succes = self.RattacherIndividu(IDindividu, IDcategorie, titulaire)
            # MAJ de l'affichage
            self.MAJ() 
            self.MAJnotebook() 
            return IDindividu
        else:
            dlg.Destroy()
            self.SupprimerFamille() 
            return None
    
    def SupprimerFamille(self):
        # Supprime la fiche famille lorsqu'on annule le rattachement du premier titulaire
        DB = GestionDB.DB()
        req = """SELECT IDrattachement, IDfamille FROM rattachements 
        WHERE IDfamille=%d""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            self.GetParent().SupprimerFicheFamille()
    
    def RattacherIndividu(self, IDindividu=None, IDcategorie=None, titulaire=0):            
        # Saisie dans la base d'un rattachement
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDindividu", IDindividu),
            ("IDfamille", self.IDfamille),
            ("IDcategorie", IDcategorie),
            ("titulaire", titulaire),
            ]
        IDrattachement = DB.ReqInsert("rattachements", listeDonnees)
        DB.Close()
        return True
    
    def Modifier_menu(self, event):
        """ Modifier une fiche à partir du menu contextuel """
        IDindividu = self.IDindividu_menu
        self.Modifier(IDindividu)
        self.IDindividu_menu = None
    
    def Modifier_selection(self, event=None):
        """ Modifier une fiche à partir du bouton Modifier """
        IDindividu = self.selectionCadre
        self.selectionCadre = None
        if IDindividu == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans le cadre Composition !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        else:
            self.Modifier(IDindividu)

    def Supprimer_menu(self, event):
        IDindividu = self.IDindividu_menu
        self.Supprimer(IDindividu)
        self.IDindividu_menu = None


    def Supprimer_selection(self, event=None):
        """ Supprimer ou detacher """
        IDindividu = self.selectionCadre
        self.selectionCadre = None
        if IDindividu == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans le cadre Composition !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        else:
            self.Supprimer(IDindividu)

    def Modifier(self, IDindividu=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "modifier") == False : return
        dlg = DLG_Individu.Dialog(None, IDindividu=IDindividu)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ() 
        dlg.Destroy()
        self.MAJ() 
        self.MAJnotebook() 
    
    def Supprimer(self, IDindividu=None):
        """ Supprimer un individu """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "supprimer") == False : return
        import DLG_Supprimer_fiche
        dlg = DLG_Supprimer_fiche.Dialog(self, IDindividu=IDindividu, IDfamille=self.IDfamille)
        reponse = dlg.ShowModal()
        dlg.Destroy()

        # MAJ de la fiche famille
        if reponse  == 1 or reponse == 2 :
            self.MAJ() 
            self.MAJnotebook() 
        
        # Suppression de la fiche famille
        if reponse == 3 :
            self.GetParent().SupprimerFicheFamille()
            
    
    def MAJnotebook(self):
        """ MAJ la page active du notebook de la fenêtre famille """
        self.parent.MAJpageActive()
        self.parent.MAJpage("caisse")
        self.parent.MAJpage("divers")

# --------------------------------------------------------------------------------------------------------------------------



class CTRL_Liste(HTL.HyperTreeList):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style= wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT,
                 IDfamille=None,
                 ):
        HTL.HyperTreeList.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.IDfamille = IDfamille
        
        # Initialisation du tooltip
        self.tip = STT.SuperToolTip(u"")
        self.tip.SetEndDelay(10000) # Fermeture auto du tooltip après 10 secs
        self.tip.IDindividu = None

        # Création de l'ImageList (Récupère les images attribuées aux civilités)
        il = wx.ImageList(16, 16)
        index = 0
        self.dictImages = {}
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, label, abrege, img, sexe in civilites :
                exec("self.img%d = il.Add(wx.Bitmap('Images/16x16/%s', wx.BITMAP_TYPE_PNG))" % (index, img))
                exec("self.dictImages[%d] = self.img%d" % (IDcivilite, index))
                index += 1
        self.dictImages[100] = il.Add(wx.Bitmap("Images/16x16/Titulaire.png", wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Creation des colonnes
        self.AddColumn(_(u"Individu"))
        self.SetColumnWidth(0, 260)
        
        self.AddColumn(u"", flag=wx.ALIGN_CENTRE, image=self.dictImages[100])
        self.SetColumnWidth(1, 20)
        
        self.AddColumn(_(u"Date de naissance"))
        self.SetColumnWidth(2, 155)
        
        self.AddColumn(_(u"Adresse"))
        self.SetColumnWidth(3, 200)

        self.AddColumn(_(u"Téléphones"))
        self.SetColumnWidth(4, 180)

        # Création des branches
        self.SetMainColumn(0)
        self.root = self.AddRoot(_(u"Composition"))
        
        self.SetSpacing(10)
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_COLUMN_LINES | wx.TR_ROW_LINES ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
        
        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.Modifier) 
        self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnContextMenu)
        self.GetMainWindow().Bind(wx.EVT_MOTION, self.OnMotion)
        self.GetMainWindow().Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

    def SetDonnees(self, donnees):
        self.donnees = donnees
        
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.donnees = GetValeurs(self.IDfamille) 
        nbreBranches = self.GetChildrenCount(self.root)
        if nbreBranches > 1 :
            self.DeleteChildren(self.root)
        self.CreationBranches()
        
    def CreationBranches(self):
        """ Création des branches """
        dictCategories = {1 : [], 2 : [], 3:[] }
        for IDindividu, dictIndividu in self.donnees.dictInfosIndividus.iteritems() :
            dictCategories[dictIndividu["categorie"]].append((IDindividu, dictIndividu))
            
        # Création des branche CATEGORIES
        for IDcategorie in (1, 2, 3) :
            if IDcategorie == 1 : label = _(u"Représentants")
            if IDcategorie == 2 : label = _(u"Enfants")
            if IDcategorie == 3 : label = _(u"Contacts")
            brancheCategorie = self.AppendItem(self.root, label)
            self.SetPyData(brancheCategorie, {"type" : "categorie", "IDcategorie" : IDcategorie} )
            self.SetItemBold(brancheCategorie, True)
            self.SetItemBackgroundColour(brancheCategorie, wx.Colour(227, 227, 227))
            
            # Création des branche INDIVIDUS
            for IDindividu, dictIndividu in dictCategories[IDcategorie] :

                nom = dictIndividu["nom"]
                prenom = dictIndividu["prenom"]
                IDcivilite = dictIndividu["IDcivilite"]
                categorieCivilite = Civilites.GetDictCivilites()[IDcivilite]["categorie"]
                if categorieCivilite == "ENFANT" :
                    type = "E"
                else:
                    type = "A"
                sexe = Civilites.GetDictCivilites()[IDcivilite]["sexe"]

                brancheIndividu = self.AppendItem(brancheCategorie, u"%s %s" % (nom, prenom))
                self.SetPyData(brancheIndividu, {"type" : "individu", "IDindividu" : IDindividu} )
##                if Civilites.GetDictCivilites()[dictIndividu["IDcivilite"]]["sexe"] == "M" :
##                    self.SetItemBackgroundColour(brancheIndividu, wx.Colour(217, 212, 251))
##                else :
##                    self.SetItemBackgroundColour(brancheIndividu, wx.Colour(251, 212, 239))

                # Images de l'individu
                self.SetItemImage(brancheIndividu, self.dictImages[IDcivilite], which=wx.TreeItemIcon_Normal)
                self.SetItemImage(brancheIndividu, self.dictImages[IDcivilite], which=wx.TreeItemIcon_Expanded)
                
                # Titulaire
                if dictIndividu["titulaire"] == 1 :
                    self.SetItemText(brancheIndividu, u"T", 1)
                
                # Date de naissance
                texte = self.donnees.GetTxtDateNaiss(self.donnees.dictInfosIndividus, IDindividu)
                if _(u"inconnue") in texte : texte = u""
                self.SetItemText(brancheIndividu, texte, 2)
                
                # Adresse
                ligne1 = dictIndividu["adresse_ligne1"]
                ligne2 = dictIndividu["adresse_ligne2"]
                self.SetItemText(brancheIndividu, u"%s\n%s" % (ligne1, ligne2), 3)
                
                # Téléphones
                listeTelephones = []
                if dictIndividu["tel_domicile_complet"] != None : listeTelephones.append(dictIndividu["tel_domicile_complet"])
                if dictIndividu["tel_mobile_complet"] != None : listeTelephones.append(dictIndividu["tel_mobile_complet"])
                if dictIndividu["travail_tel_complet"] != None : listeTelephones.append(dictIndividu["travail_tel_complet"])
                self.SetItemText(brancheIndividu, u"\n".join(listeTelephones), 4)

            self.Expand(brancheCategorie) 
        
    def GetSelectionIndividu(self, event):
        pt = event.GetPosition()
        item = self.HitTest(pt)[0]
        if item :
            self.SelectItem(item)
            dictItem = self.GetMainWindow().GetItemPyData(item)
            if dictItem["type"] == "individu" :
                return dictItem["IDindividu"]
        self.UnselectAll()
        return None

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        IDindividu = self.GetSelectionIndividu(event) 
        
        # Création du menu contextuel
        menu = wx.Menu()

        # Ajouter
        id = wx.NewId()
        item = wx.MenuItem(menu, id, _(u"Rattacher un individu"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=id)
        
        if IDindividu != None :
            
            menu.AppendSeparator()
            
            # Modifier
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"Modifier"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=id)
            
            # Détacher ou supprimer
            id = wx.NewId()
            item = wx.MenuItem(menu, id, _(u"Détacher ou supprimer"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=id)

            menu.AppendSeparator()
            
            # Changer de catégorie
            sousMenuCategorie = wx.Menu()
            
            item = wx.MenuItem(sousMenuCategorie, 601, _(u"Représentant"), kind=wx.ITEM_RADIO)
            sousMenuCategorie.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Changer_categorie, id=601)
            if self.donnees.dictInfosIndividus[IDindividu]["categorie"] == 1 : item.Check(True)
            
            item = wx.MenuItem(sousMenuCategorie, 602, _(u"Enfant"), kind=wx.ITEM_RADIO)
            sousMenuCategorie.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Changer_categorie, id=602)
            if self.donnees.dictInfosIndividus[IDindividu]["categorie"] == 2 : item.Check(True)
            
            item = wx.MenuItem(sousMenuCategorie, 603, _(u"Contact"), kind=wx.ITEM_RADIO)
            sousMenuCategorie.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Changer_categorie, id=603)
            if self.donnees.dictInfosIndividus[IDindividu]["categorie"] == 3 : item.Check(True)
            
            menu.AppendMenu(wx.NewId(), _(u"Changer de catégorie"), sousMenuCategorie)

            # Définir comme titulaire
            if self.donnees.dictInfosIndividus[IDindividu]["categorie"] == 1 :
                id = wx.NewId()
                item = wx.MenuItem(menu, id, _(u"Définir comme titulaire"), kind=wx.ITEM_CHECK)
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnSetTitulaire, id=id)
                if self.donnees.dictInfosIndividus[IDindividu]["titulaire"] == 1 :
                    item.Check(True)
        
            if self.donnees.dictInfosIndividus[IDindividu]["inscriptions"] == True :
                menu.AppendSeparator()
                
                id = wx.NewId()
                item = wx.MenuItem(menu, id, _(u"Grille des consommations"))
                item.SetBitmap(wx.Bitmap("Images/16x16/Calendrier.png", wx.BITMAP_TYPE_PNG))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OuvrirCalendrier, id=id)

        # Finalisation du menu
        self.PopupMenu(menu)
        menu.Destroy()

    def Calendrier_selection(self):
        self.OuvrirCalendrier()

    def OuvrirCalendrier(self, IDindividu=None):
        """ Ouverture du calendrier de l'individu """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "consulter") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        type = dictItem["type"]
        if type != "individu" : 
            return
        IDindividu = dictItem["IDindividu"]
        self.parent.Sauvegarde()
        import DLG_Grille
        dlg = DLG_Grille.Dialog(self, IDfamille=self.IDfamille, selectionIndividus=[IDindividu,])
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJnotebook()
        dlg.Destroy()

    def Ajouter(self, event=None):
        """ Rattacher un nouvel individu """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "creer") == False : return
        import DLG_Rattachement
        dlg = DLG_Rattachement.Dialog(None, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            mode, IDcategorie, titulaire, IDindividu, nom, prenom = dlg.GetData()
            dlg.Destroy()
            if mode == "creation" :
                # Création d'un nouvel individu rattaché
                dictInfosNouveau = {
                    "IDfamille" : self.IDfamille,
                    "IDcategorie" : IDcategorie,
                    "titulaire" : titulaire,
                    "nom" : nom,
                    "prenom" : prenom,
                    }
                dlg = DLG_Individu.Dialog(None, IDindividu=None, dictInfosNouveau=dictInfosNouveau)
                if dlg.ShowModal() == wx.ID_OK:
                    pass #print "Nouvelle fiche creee et deja rattachee."
                else:
                    self.SupprimerFamille() 
                dlg.Destroy()
            else:
                # Rattachement d'un individu existant
                succes = self.RattacherIndividu(IDindividu, IDcategorie, titulaire)
            # MAJ de l'affichage
            self.MAJ() 
            self.MAJnotebook() 
        else:
            dlg.Destroy()
            self.SupprimerFamille() 
    
    def SupprimerFamille(self):
        # Supprime la fiche famille lorsqu'on annule le rattachement du premier titulaire
        DB = GestionDB.DB()
        req = """SELECT IDrattachement, IDfamille FROM rattachements 
        WHERE IDfamille=%d""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            self.GetParent().SupprimerFicheFamille()
    
    def RattacherIndividu(self, IDindividu=None, IDcategorie=None, titulaire=0):            
        # Saisie dans la base d'un rattachement
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDindividu", IDindividu),
            ("IDfamille", self.IDfamille),
            ("IDcategorie", IDcategorie),
            ("titulaire", titulaire),
            ]
        IDrattachement = DB.ReqInsert("rattachements", listeDonnees)
        DB.Close()
        return True
    
    def Modifier_selection(self, event=None):
        self.Modifier(event)
        
    def Modifier(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "modifier") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        type = dictItem["type"]
        if type != "individu" : 
            return
        IDindividu = dictItem["IDindividu"]
        if IDindividu == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        import DLG_Individu
        dlg = DLG_Individu.Dialog(None, IDindividu=IDindividu)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ() 
        dlg.Destroy()
        self.MAJ() 
        self.MAJnotebook() 

    def Supprimer_selection(self, event=None):
        self.Supprimer(event)

    def Supprimer(self, event=None):
        """ Supprimer un individu """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "supprimer") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        type = dictItem["type"]
        if type != "individu" : 
            return
        IDindividu = dictItem["IDindividu"]
        import DLG_Supprimer_fiche
        dlg = DLG_Supprimer_fiche.Dialog(self, IDindividu=IDindividu, IDfamille=self.IDfamille)
        reponse = dlg.ShowModal()
        dlg.Destroy()

        # MAJ de la fiche famille
        if reponse  == 1 or reponse == 2 :
            self.MAJ() 
            self.MAJnotebook() 
        
        # Suppression de la fiche famille
        if reponse == 3 :
            self.GetParent().SupprimerFicheFamille()

    def Changer_categorie(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "modifier") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        if type != "individu" : 
            return
        IDindividu = dictItem["IDindividu"]

        IDcategorie = event.GetId() - 600
        IDrattachement = self.donnees.dictInfosIndividus[IDindividu]["IDrattachement"]
        if IDcategorie != self.donnees.dictInfosIndividus[IDindividu]["categorie"] :
            dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment modifier la catégorie de rattachement de cet individu ?"), _(u"Changement de catégorie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES :
                DB = GestionDB.DB()
                DB.ReqMAJ("rattachements", [("IDcategorie", IDcategorie),], "IDrattachement", IDrattachement)
                DB.Close()
                self.MAJ() 
                self.MAJnotebook() 
            dlg.Destroy()

    def OnSetTitulaire(self, event):
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        if type != "individu" : 
            return
        IDindividu = dictItem["IDindividu"]

        if self.donnees.dictInfosIndividus[IDindividu]["titulaire"] == 1 :
            # Recherche s'il restera au moins un titulaire dans cette famille
            nbreTitulaires = 0
            for IDindividu, dictIndividu in self.donnees.dictInfosIndividus.iteritems() :
                if dictIndividu["titulaire"] == 1 : 
                    nbreTitulaires += 1
            if nbreTitulaires == 1 :
                dlg = wx.MessageDialog(self, _(u"Vous devez avoir au moins un titulaire de dossier dans une famille !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return   
            etat = 0
        else:
            etat = 1
        DB = GestionDB.DB()
        req = "UPDATE rattachements SET titulaire=%d WHERE IDindividu=%d AND IDfamille=%d;" % (etat, IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        DB.Commit()
        DB.Close()
        self.MAJ() 

    def MAJnotebook(self):
        """ MAJ la page active du notebook de la fenêtre """
        self.parent.MAJpageActive()
        self.parent.MAJpage("caisse")
        self.parent.MAJpage("divers")

    def OnMotion(self, event):
        item = self.HitTest(event.GetPosition())[0]
        IDindividu = None
        if item :
            dictItem = self.GetMainWindow().GetItemPyData(item)
            if dictItem["type"] == "individu" :
                IDindividu = dictItem["IDindividu"]
        if IDindividu != None :
            # On met le tooltip
            self.ActiveTooltip(actif=True, IDindividu=IDindividu)
        else:
            # Désactivation du toolTip
            self.ActiveTooltip(actif=False)
        event.Skip()
        
    def OnLeaveWindow(self, event):
        self.ActiveTooltip(False) 

    def AfficheTooltip(self):
        styleTooltip = "Office 2007 Blue"
        taillePhoto = 30
        font = self.GetFont()
        
        # Récupération des infos sur l'individu
        IDindividu = self.tip.IDindividu
        dictInfoIndividu = self.donnees.dictInfosIndividus[IDindividu]
        
        # Paramétrage du tooltip
        self.tip.SetHyperlinkFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        if dictInfoIndividu["genre"] == "F" :
            # Couleur du toolTip version FILLE
            self.tip.SetTopGradientColour(wx.Colour(255,255,255))
            self.tip.SetMiddleGradientColour(wx.Colour(251,229,243))
            self.tip.SetBottomGradientColour(wx.Colour(255,210,226))
            self.tip.SetTextColor(wx.Colour(76,76,76))
        else:
            # Couleur du toolTip version GARCON
            self.tip.SetTopGradientColour(wx.Colour(255,255,255))
            self.tip.SetMiddleGradientColour(wx.Colour(242,246,251))
            self.tip.SetBottomGradientColour(wx.Colour(202,218,239))
            self.tip.SetTextColor(wx.Colour(76,76,76))
        
        # Adaptation pour wxPython >= 2.9
        if wx.VERSION > (2, 9, 0, 0) :
            qualite = wx.IMAGE_QUALITY_BICUBIC
        else :
            qualite = 100
            
        # Titre du tooltip
        nomImage = Civilites.GetDictCivilites()[self.donnees.dictInfosIndividus[IDindividu]["IDcivilite"]]["nomImage"]
        if nomImage == None : nomImage = "Personne.png"
        nomFichier = "Images/128x128/%s" % nomImage
        IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
        bmp = bmp.ConvertToImage()
        bmp = bmp.Rescale(width=taillePhoto, height=taillePhoto, quality=qualite) 
        bmp = bmp.ConvertToBitmap()
        self.tip.SetHeaderBitmap(bmp)
        self.tip.SetHeaderFont(wx.Font(10, font.GetFamily(), font.GetStyle(), wx.BOLD, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetHeader(dictInfoIndividu["nomComplet2"])
        self.tip.SetDrawHeaderLine(True)
        
        # Corps du tooltip
        message = u""
        if dictInfoIndividu["datenaissComplet"] != None : message += u"%s\n" % dictInfoIndividu["datenaissComplet"]
        
        adresse = u""
        if dictInfoIndividu["adresse_ligne1"] not in (None, u"") : adresse += u"</b>%s\n" % dictInfoIndividu["adresse_ligne1"]
        if dictInfoIndividu["adresse_ligne2"] not in (None, u"") : adresse += u"</b>%s\n" % dictInfoIndividu["adresse_ligne2"]
        if len(adresse) > 3 : 
            message += "\n" + adresse
        
        coords = u""
        if dictInfoIndividu["tel_domicile_complet"] not in (None, u"") : coords += u"%s\n" % dictInfoIndividu["tel_domicile_complet"] 
        if dictInfoIndividu["tel_mobile_complet"] not in (None, u"") : coords += u"%s\n" % dictInfoIndividu["tel_mobile_complet"] 
        if dictInfoIndividu["travail_tel_complet"] not in (None, u"") : coords += u"%s\n" % dictInfoIndividu["travail_tel_complet"]
        if len(coords) > 3 : 
            message += "\n" + coords
        if dictInfoIndividu["mail_complet"] != None : message += u"\n%s \n" % dictInfoIndividu["mail_complet"]
        
        # Liste des inscriptions de l'individu
        if dictInfoIndividu["genre"] == "F" :
            lettreGenre = "e"
        else:
            lettreGenre = ""
        if dictInfoIndividu["prenom"] != None :
            prenom = dictInfoIndividu["prenom"]
        else:
            prenom = u""
        if dictInfoIndividu["inscriptions"] == True :
            nbreInscriptions = len(dictInfoIndividu["listeInscriptions"])
            message += "\n"
            if nbreInscriptions == 1 :
                message += _(u"%s est inscrit%s à 1 activité : \n") % (prenom, lettreGenre)
            else:
                message += _(u"%s est inscrit%s à %d activités : \n") % (prenom, lettreGenre, nbreInscriptions)
            for dictInscription in dictInfoIndividu["listeInscriptions"] :
                message += "> %s (%s - %s) \n" % (dictInscription["nomActivite"], dictInscription["nomGroupe"], dictInscription["nomCategorie"])

        self.tip.SetMessage(message)
        
        # Pied du tooltip
        self.tip.SetDrawFooterLine(True)
        self.tip.SetFooterBitmap(wx.Bitmap(u"Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        self.tip.SetFooterFont(wx.Font(7, font.GetFamily(), font.GetStyle(), wx.LIGHT, font.GetUnderlined(), font.GetFaceName()))
        self.tip.SetFooter(_(u"Double-cliquez pour ouvrir sa fiche"))
        
        # Affichage du Frame tooltip
        self.tipFrame = STT.ToolTipWindow(self, self.tip)
        self.tipFrame.CalculateBestSize()
        x, y = wx.GetMousePosition()
        self.tipFrame.SetPosition((x+15, y+17))
        self.tipFrame.DropShadow(True)
        self.tipFrame.StartAlpha(True) # ou .Show() pour un affichage immédiat
        
        # Arrêt du timer
        self.timerTip.Stop()
        del self.timerTip
                    
    def CacheTooltip(self):
        # Fermeture du tooltip
        if hasattr(self, "tipFrame"):
            try :
                self.tipFrame.Destroy()
            except :
                pass
            del self.tipFrame
            self.tip.IDindividu = None
        
    def ActiveTooltip(self, actif=True, IDindividu=None):
        # Pour éviter que l'utilisateur bouge la souris trop vite
        if self.tip.IDindividu != None and self.tip.IDindividu != IDindividu :
            actif = False
            
        if actif == True :
            # Active le tooltip
            if hasattr(self, "tipFrame") == False and hasattr(self, "timerTip") == False :
                self.timerTip = wx.PyTimer(self.AfficheTooltip)
                self.timerTip.Start(1500)
                self.tip.IDindividu = IDindividu
        else:
            # Désactive le tooltip
            if hasattr(self, "timerTip"):
                if self.timerTip.IsRunning():
                    self.timerTip.Stop()
                    del self.timerTip
                    self.tip.IDindividu = None
            self.CacheTooltip() 


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Notebook(wx.Notebook):
    def __init__(self, parent, IDfamille=None):
        if "linux" in sys.platform :
            style = wx.NB_BOTTOM
        else :
            style = wx.BK_LEFT
        wx.Notebook.__init__(self, parent, id=-1, style=style)
        self.parent = parent
        self.IDfamille = IDfamille
        self.dictPages = {}
        
        listePages = [
            (_(u"graphique"), _(u"  Graphique  "), u"CTRL_Graphique(self, IDfamille=IDfamille)", None),
            (_(u"liste"), _(u"  Liste  "), u"CTRL_Liste(self, IDfamille=IDfamille)", None),
##            (_(u"liens"), _(u"  Liens  "), u"DLG_Individu_liens.Notebook(self, IDfamille=IDfamille)", None),
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in listePages :
            if imgPage != None :
                exec("self.img%d = il.Add(wx.Bitmap('Images/16x16/%s', wx.BITMAP_TYPE_PNG))" % (index, imgPage))
                index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in listePages :
            exec("self.page%d = %s" % (index, ctrlPage))
            exec("self.AddPage(self.page%d, u'%s')" % (index, labelPage))
            if imgPage != None :
                exec("self.SetPageImage(%d, self.img%d)" % (index, index))
            exec("self.dictPages['%s'] = {'ctrl' : self.page%d, 'index' : %d}" % (codePage, index, index))
            index += 1
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        page.MAJ() 
        event.Skip()
    
##    def MAJpageActive(self):
##        """ MAJ la page active du notebook """
##        indexPage = self.GetSelection()
##        page = self.GetPage(indexPage)
##        page.MAJ() 

    def Sauvegarde(self):
        self.parent.Sauvegarde()

    def MAJpageActive(self):
        self.parent.MAJpageActive()

    def MAJpage(self, codePage=""):
        self.parent.MAJpage(codePage)

    def Ajouter(self, event=None):
        page = self.GetPage(self.GetSelection())
        IDindividu = page.Ajouter(None)
        return IDindividu

    def Modifier_selection(self, event=None):
        page = self.GetPage(self.GetSelection())
        page.Modifier_selection()

    def Modifier_individu(self, IDindividu=None):
        page = self.GetPage(self.GetSelection())
        page.Modifier(IDindividu)

    def Supprimer_selection(self, event=None):
        page = self.GetPage(self.GetSelection())
        page.Supprimer_selection()
        
    def Calendrier_selection(self, event=None):
        page = self.GetPage(self.GetSelection())
        page.Calendrier_selection()

    def MAJ(self, event=None):
        page = self.GetPage(self.GetSelection())
        page.MAJ()
    
    def SupprimerFicheFamille(self):
        self.parent.SupprimerFicheFamille()
        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = Notebook(panel, IDfamille=7)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "ObjectListView", size=(900, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()