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
import sys
import wx.html as html
import GestionDB
import datetime
import os
import six
import webbrowser
import shutil
import random, codecs
from Utils import UTILS_Fichiers



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
    return text

# --------------------------------------------------------------------------------------------------------

def BoucleFrameOuverte(nom, WindowEnCours) :
    """ Est utilisée dans FrameOuverte """
    for children in WindowEnCours.GetChildren():
        if children.GetName() == nom : return children
        if len(children.GetChildren()) > 0 :
            tmp = BoucleFrameOuverte(nom, children)
            if tmp != None : return tmp
    return None

def FrameOuverte(nom) :
    """ Permet de savoir si une frame est ouverte ou pas..."""
    topWindow = wx.GetApp().GetTopWindow() 
    # Analyse le TopWindow
    if topWindow.GetName() == nom : return True
    # Analyse les enfants de topWindow
    reponse = BoucleFrameOuverte(nom, topWindow)
    return reponse

def SetModalFrameParente(frameActuelle):
    """ Rend modale la frame parente """
    try :
        frameActuelle.GetParent().GetTopLevelParent().MakeModal(True)
    except : 
        pass

# -------------------------------------------------------------------------------------------------------
# Fonction qui modifie le wx.StaticText pour gérer le redimensionnement des StaticText

class StaticWrapText(wx.StaticText):
    """A StaticText-like widget which implements word wrapping."""
    
    def __init__(self, *args, **kwargs):
        wx.StaticText.__init__(self, *args, **kwargs)

        # store the initial label
        self.__label = super(StaticWrapText, self).GetLabel()

        # listen for sizing events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def SetLabel(self, newLabel):
        """Store the new label and recalculate the wrapped version."""
        self.__label = newLabel
        self.__wrap()

    def GetLabel(self):
        """Returns the label (unwrapped)."""
        return self.__label
    
    def __wrap(self):
        """Wraps the words in label."""
        words = self.__label.split()
        lines = []

        # get the maximum width (that of our parent)
        max_width = self.GetParent().GetVirtualSizeTuple()[0]-20 # J'ai ajouté le -20 ici
        
        index = 0
        current = []

        for word in words:
            current.append(word)

            if self.GetTextExtent(" ".join(current))[0] > max_width:
                del current[-1]
                lines.append(" ".join(current))

                current = [word]

        # pick up the last line of text
        lines.append(" ".join(current))

        # set the actual label property to the wrapped version
        super(StaticWrapText, self).SetLabel("\n".join(lines))

        # refresh the widget
        self.Refresh()
        
    def OnSize(self, event):
        # dispatch to the wrap method which will 
        # determine if any changes are needed
        self.__wrap()
        self.GetParent().Layout()
        

# -------------------------------------------------------------------------------------------------------



class TexteHtml(wx.Panel):
    def __init__(self, parent, texte="", Enabled=False, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
            
        # Création du widget HTML
        self.pageHtml = html.HtmlWindow(self, -1)
        self.pageHtml.SetPage(texte)

        # Paramètres du widget HTML
        #self.couleurFond = self.getRGB(win32api.GetSysColor(15)) # Pour archive
        self.couleurFond = wx.SystemSettings.GetColour(30)
        self.pageHtml.SetBackgroundColour(self.couleurFond)
        if Enabled == False : self.pageHtml.Enable(False)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.pageHtml, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)

    def getRGB(self, winColor):
        b = winColor >> 16
        g = winColor >> 8 & 255
        r = winColor & 255
        return (r,g,b)

    def SetText(self, texte ="") :
        self.pageHtml.SetPage(texte)
        self.pageHtml.SetBackgroundColour(self.couleurFond)


# ---------------------------------------------------------------------------------------------------------

##def Recup_liste_pb_personnes(recalc=False):
##    """ Récupération de la liste des problèmes des personnes """
##    try :
##        topWindow = wx.GetApp().GetTopWindow()
##        nomWindow = topWindow.GetName()
##    except :
##        nomWindow = None
##    if nomWindow == "general" : 
##        # Si la frame 'General' est chargée, on y récupère la liste des problemes
##        if recalc == True :
##            topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes = Creation_liste_pb_personnes()
##        return topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes
##    else:
##        # On créée la liste
##        dictNomsPersonnes, dictProblemesPersonnes = Creation_liste_pb_personnes()
##        return dictNomsPersonnes, dictProblemesPersonnes


def Recup_liste_pb_personnes(recalc=False):
    """ Récupération de la liste des problèmes des personnes """
    
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
##    print ">>>", nomWindow
    # Si Recalcul des données obligatoire :
    if recalc == True :
        print(_(u"Recalcul obligatoire des donnees"))
        topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes = Creation_liste_pb_personnes()
        return topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes
    
    # Si ce n'est qu'une récupération des données :
    try :
        # On essaie de récupérer les dictionnaires dans la topWindow
        dictNomsPersonnes = topWindow.dictNomsPersonnes
        dictProblemesPersonnes = topWindow.dictProblemesPersonnes
##        print _(u"Recuperation dans le topWindow")
        return dictNomsPersonnes, dictProblemesPersonnes
    except :
        topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes = Creation_liste_pb_personnes()
##        print _(u"Recuperation dans la topWindow impossible : on calcule les donnees")
        return topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes

    
    
def Creation_liste_pb_personnes():
    """ Création de la liste des problèmes des personnes """
    listeIDpersonne = Recherche_ContratsEnCoursOuAVenir()
    dictNomsPersonnes, dictProblemesPersonnes = Recherche_problemes_personnes(listeIDpersonnes = tuple(listeIDpersonne))
    return dictNomsPersonnes, dictProblemesPersonnes
                
def Recherche_problemes_personnes(listeIDpersonnes = (), infosPersonne=[]):
    """ Recherche les problèmes dans les dossiers des personnes """
    
    dictProblemes = {}
    dictNoms = {}
    
    #
    # Analyse des fiches individuelles
    #
    
    if len(listeIDpersonnes) == 0 : listeIDpersonnesTmp = "(100000)"
    elif len(listeIDpersonnes) == 1 : listeIDpersonnesTmp = "(%d)" % listeIDpersonnes[0]
    else : listeIDpersonnesTmp = str(tuple(listeIDpersonnes))
    
    DB = GestionDB.DB()        
    req = """SELECT IDpersonne, civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, pays_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation
    FROM personnes WHERE IDpersonne IN %s ORDER BY nom; """ % listeIDpersonnesTmp
    DB.executerReq(req)
    listePersonnes = DB.resultatReq()
    
    # Récupère ici les infos directement dans les contrôles de la fiche individuelle
    if len(infosPersonne) != 0 :
        listePersonnes = infosPersonne

    for personne in listePersonnes :
        IDpersonne = personne[0]
        civilite = personne[1]
        nom = personne[2]
        nom_jfille = personne[3]
        prenom = personne[4]
        date_naiss = personne[5]
        cp_naiss = personne[6]
        ville_naiss = personne[7]
        pays_naiss = personne[8]
        nationalite = personne[9]
        num_secu = personne[10]
        adresse_resid = personne[11]
        cp_resid = personne[12]
        ville_resid = personne[13]
        IDsituation = personne[14]
        
        dictNoms[IDpersonne] = nom + " " + prenom
        problemesFiche = []
        
        # Civilité
        if civilite == "" or civilite == None : problemesFiche.append( (_(u"Civilité")) )
        # Nom
        if nom == "" or nom == None : problemesFiche.append( (_(u"Nom de famille")) )
        # Nom de jeune fille
        if civilite == "Mme" :
            if nom_jfille == "" or nom_jfille == None : problemesFiche.append( (_(u"Nom de jeune fille")) )
        # Prénom
        if prenom == "" or prenom == None : problemesFiche.append( (_(u"Prénom")) )
        # Date de naissance
        if str(date_naiss).strip(" ") == "" or date_naiss == None : problemesFiche.append( (_(u"Date de naissance")) )
        # CP_naissance
        if str(cp_naiss).strip(" ") == "" or cp_naiss == None : problemesFiche.append( (_(u"Code postal de la ville de naissance")) )
        # Ville de naissance
        if ville_naiss == "" or ville_naiss == None : problemesFiche.append( (_(u"Ville de naissance")) )
        # Pays de naissance
        if pays_naiss == "" or pays_naiss == None or pays_naiss == 0 : problemesFiche.append( (_(u"Pays de naissance")) )
        # Nationalite
        if nationalite == "" or nationalite == None or nationalite == 0 : problemesFiche.append( (_(u"Nationalité")) )
        # Num Sécu
        if str(num_secu).strip(" ") == "" or num_secu == None : problemesFiche.append( (_(u"Numéro de sécurité sociale")) )
        # Adresse résidence
        if adresse_resid == "" or adresse_resid == None : problemesFiche.append( (_(u"Adresse de résidence")) )
        # Code postal résidence
        if str(cp_resid).strip(" ") == "" or cp_resid == None : problemesFiche.append( (_(u"Code postal de résidence")) )
        # Ville résidence
        if ville_resid == "" or ville_resid == None : problemesFiche.append( (_(u"Ville de résidence")) )
        # Situation
        if IDsituation == "" or IDsituation == None or IDsituation == 0 : problemesFiche.append( (_(u"Situation sociale")) )

    
        # Analyse des coordonnées
        req = """SELECT IDcoord
        FROM coordonnees
        WHERE IDpersonne=%d;
        """ % IDpersonne
        DB.executerReq(req)
        listeCoords = DB.resultatReq()
        
        if len(listeCoords) == 0 : 
            problemesFiche.append( (_(u"Coordonnées téléphoniques")) )
        
        # Met les données dans le dictionnaire
        if len(problemesFiche) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(problemesFiche) == 1 : 
                categorie = _(u"1 information manquante")
            else:
                categorie = str(len(problemesFiche))  + _(u" informations manquantes")
            dictProblemes[IDpersonne][categorie] = problemesFiche
            
    
    #
    # Analyse des pièces à fournir
    #
    
    date_jour = datetime.date.today()
    
    # Initialisation de la base de données
    DB = GestionDB.DB()
        
    for IDpersonne in listeIDpersonnes :
        piecesManquantes = []
        piecesPerimees = []
        DictPieces = {}
        
        # Recherche des pièces SPECIFIQUES que la personne doit fournir...
        req = """
        SELECT types_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes INNER JOIN diplomes_pieces ON diplomes.IDtype_diplome = diplomes_pieces.IDtype_diplome INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes.IDpersonne=%d;
        """ % IDpersonne
        DB.executerReq(req)
        listePiecesAFournir = DB.resultatReq()
        
        if type(listePiecesAFournir) != list :
            listePiecesAFournir = list(listePiecesAFournir)
        
        # Recherche des pièces BASIQUES que la personne doit fournir...
        req = """
        SELECT diplomes_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes_pieces INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes_pieces.IDtype_diplome=0;
        """ 
        DB.executerReq(req)
        listePiecesBasiquesAFournir = DB.resultatReq()
        
        listePiecesAFournir.extend(listePiecesBasiquesAFournir)
        
        # Recherche des pièces que la personne possède
        req = """
        SELECT types_pieces.IDtype_piece, pieces.date_debut, pieces.date_fin
        FROM types_pieces LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        WHERE (pieces.IDpersonne=%d AND pieces.date_debut<='%s' AND pieces.date_fin>='%s')
        ORDER BY pieces.date_fin;
        """ % (IDpersonne, date_jour, date_jour)
        DB.executerReq(req)
        listePieces = DB.resultatReq()
        dictTmpPieces = {}
        for IDtype_piece, date_debut, date_fin in listePieces :
            dictTmpPieces[IDtype_piece] = (date_debut, date_fin)
        
        # Passe en revue toutes les pièces à fournir et regarde si la personne possède les pièces correspondantes
        for IDtype_piece, nom_piece in listePiecesAFournir :
            if (IDtype_piece in dictTmpPieces) == True :
                date_debut = dictTmpPieces[IDtype_piece][0]
                date_fin = dictTmpPieces[IDtype_piece][1]
                # Recherche la validité
                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
                reste = str(date_fin - date_jour)
                if reste != "0:00:00":
                    jours = int(reste[:reste.index("day")])
                    if jours < 15  and jours > 0:
                        etat = "Attention"
                    elif jours <= 0:
                        etat = "PasOk"
                    else:
                        etat = "Ok"
                else:
                    etat = "Attention"
            else:
                etat = "PasOk"
            DictPieces[IDtype_piece] = (etat, nom_piece)
        

        for IDtype_piece, donnees in DictPieces.items() :
            etat, nom_piece = donnees
            if etat == "Ok": continue
            if etat == "PasOk" :
                piecesManquantes.append(nom_piece)
            if etat == "Attention" :
                piecesPerimees.append(nom_piece)

    
        # Met les listes de problèmes dans un dictionnaire
        if len(piecesManquantes) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(piecesManquantes) == 1 : 
                categorie = _(u"1 pièce manquante")
            else:
                categorie = str(len(piecesManquantes))  + _(u" pièces manquantes")
            dictProblemes[IDpersonne][categorie] = piecesManquantes

        if len(piecesPerimees) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(piecesPerimees) == 1 : 
                categorie = _(u"1 pièce bientôt périmée")
            else:
                categorie = str(len(piecesPerimees))  + _(u" pièces bientôt périmées")
            dictProblemes[IDpersonne][categorie] = piecesPerimees
        
        
        # Analyse des contrats
        problemesContrats = []
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, signature, due
        FROM contrats 
        WHERE IDpersonne = %d
        ORDER BY date_debut;""" % IDpersonne
        DB.executerReq(req)
        listeContrats = DB.resultatReq()
        
        for contrat in listeContrats :
            signature = contrat[1]
            due = contrat[2]
            # Signature
            if signature == "" or signature == "Non" : 
                txt = _(u"Contrat non signé")
                problemesContrats.append( (txt) )
            # DUE
            if due == "" or due == "Non" : 
                txt = _(u"DUE à faire")
                problemesContrats.append( (txt) )
        
        # Met les données dans le dictionnaire
        if len(problemesContrats) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(problemesContrats) == 1 : 
                categorie = _(u"1 contrat à voir")
            else:
                categorie = str(len(problemesContrats))  + _(u" contrats à voir")
            dictProblemes[IDpersonne][categorie] = problemesContrats
    

    # Fin de la fonction    
    DB.close()
    
##    print dictProblemes

    return dictNoms, dictProblemes


def Recherche_ContratsEnCoursOuAVenir() :
    """ Renvoie la liste des personnes qui ont ou vont avoir un contrat """
    # Recherche des contrats
    dateDuJour = str(datetime.date.today())
    DB = GestionDB.DB()        
    req = """SELECT contrats.IDpersonne, contrats_class.nom, contrats.date_debut, contrats.date_fin, contrats.date_rupture, contrats_types.duree_indeterminee
    FROM contrats INNER JOIN contrats_class ON contrats.IDclassification = contrats_class.IDclassification INNER JOIN contrats_types ON contrats.IDtype = contrats_types.IDtype
    WHERE contrats.date_fin>='%s'
    ORDER BY contrats.date_debut;""" % dateDuJour
    DB.executerReq(req)
    listeContrats = DB.resultatReq()
    DB.close()
    # Retourne la liste des IDpersonne
    if len(listeContrats) == 0 :
        return []
    else:
        listeIDpersonne = []
        for contrat in listeContrats :
            listeIDpersonne.append(contrat[0])
        return listeIDpersonne



class BarreTitre(wx.Panel):
    def __init__(self, parent, titre=_(u"Titre"), infoBulle="", arrondis=False, couleurFondPanel=None):
        wx.Panel.__init__(self, parent, -1, size=(-1, 80))
        couleurFond = (70, 70, 70)
        # Contrôles
        self.barreTitre = wx.StaticText(self, -1, " " + titre)
        self.barreTitre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.barreTitre.SetBackgroundColour(couleurFond)
        self.barreTitre.SetForegroundColour('White')
        # Panel
        self.SetBackgroundColour(couleurFond)
        self.SetToolTip(wx.ToolTip(infoBulle))
        self.barreTitre.SetToolTip(wx.ToolTip(infoBulle))
        # Positionnement
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(self.barreTitre, 0, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(sizer_base)
        
        if arrondis == True :
            # Crée des coins arrondis
            self.couleurFondPanel = couleurFondPanel
            self.espaceBord = 0
            self.coinArrondi = 5
            self.hauteurTitre = 40
            self.couleurFondTitre = couleurFond
            # Bind pour dessin
            self.Bind(wx.EVT_PAINT, self.OnPaint)
            self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
   
         
    def OnPaint(self, event):
        dc= wx.PaintDC(self)
        dc= wx.BufferedDC(dc)
        largeurDC, hauteurDC= self.GetSizeTuple()
        dc.SetBackground(wx.Brush(self.couleurFondPanel))
        dc.Clear()       
        dc.SetBrush(wx.Brush(self.couleurFondTitre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), self.hauteurTitre, self.coinArrondi)

    def OnEraseBackground(self, event):
        pass 
        

# ---------------------------------------------------------------------------------------------------------------------------------------------------------


class PanelArrondi(wx.Panel):
    def __init__(self, parent, ID=-1, name="gadget", texteTitre=""):
        wx.Panel.__init__(self, parent, ID, name=name)
        self.texteTitre = texteTitre
        
        self.SetBackgroundColour((122, 161, 230))
        
        # Création fond
        self.espaceBord = 10
        self.coinArrondi = 5
        self.hauteurTitre = 17
        self.couleurFondDC = self.GetBackgroundColour()
        self.couleurFondCadre = (214, 223, 247)
        self.couleurFondTitre = (70, 70, 70)
        self.couleurBord = (70, 70, 70)
        self.couleurDegrade = (130, 190, 235)
        self.couleurTexteTitre = (255, 255, 255)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)      
        self.Bind(wx.EVT_SIZE, self.OnSize)
         
    def OnPaint(self, event):
        dc= wx.PaintDC(self)
        dc= wx.BufferedDC(dc)
        largeurDC, hauteurDC= self.GetSizeTuple()
        
        # paint le fond
        dc.SetBackground(wx.Brush(self.couleurFondDC))
        dc.Clear()       
        
        # Cadre du groupe
        dc.SetBrush(wx.Brush(self.couleurFondCadre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), hauteurDC-(self.espaceBord*2), self.coinArrondi)
        # Barre de titre
        dc.SetBrush(wx.Brush(self.couleurFondTitre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), self.hauteurTitre+self.coinArrondi, self.coinArrondi)
        # Dégradé
        dc.GradientFillLinear((self.espaceBord+1, self.espaceBord+7, largeurDC-(self.espaceBord*2)-2, self.hauteurTitre-2), (214, 223, 247), (0, 0, 0), wx.NORTH)
        # Cache pour enlever l'arrondi inférieur de la barre de titre
        dc.SetBrush(wx.Brush(self.couleurFondCadre))
        dc.SetPen(wx.Pen(self.couleurFondCadre, 0))
        dc.DrawRectangle(self.espaceBord+1, self.espaceBord+self.hauteurTitre+1, largeurDC-(self.espaceBord*2)-2, self.coinArrondi+5)
        # Titre
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD) 
        dc.SetFont(font)
        dc.SetTextForeground(self.couleurTexteTitre)
        dc.DrawText(self.texteTitre, self.espaceBord+7, self.espaceBord+2)

    def OnEraseBackground(self, event):
        pass   
        
    def OnSize(self, event):
        self.Refresh() 
        event.Skip()
                        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------
        
def sendTextMail():
    """ Envoyer un mail avec smtp """
    import smtplib
    try:
        addressTarget = ("test@wanadoo.fr",)
        smtpServer = 'smtp.orange.fr'
        sourceAddress = 'test@fPython.fr'
        MAIL_SUBJECT="sujet du mail"
        MAIL_CONTENT = _(u"ceci est le contenu du mail")
        
        server = smtplib.SMTP( smtpServer, '25', 'localhost' )
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % ( sourceAddress, ", ".join( addressTarget ), MAIL_SUBJECT))
        msg = msg + MAIL_CONTENT
        server.sendmail( sourceAddress, addressTarget, msg )
        server.quit()
        print("Envoi mail Ok")
    except smtplib.SMTPException as msg:
        print(msg)


def EnvoyerMail(adresses = [], sujet="", message=""):
    """ Envoyer un Email avec le client de messagerie par défaut """
    if len(adresses) == 1 :
        commande = "mailto:%s" % adresses[0]
    else:
        commande = "mailto:%s" % adresses[0] + "?"
        if len(adresses) > 1 :
            commande+= "bcc=%s" % adresses[1]
        for adresse in adresses[2:] :
            commande+= "&bcc=%s" % adresse
    if sujet != "" : 
        if len(adresses) == 1 : 
            commande += "?"
        else :
            commande += "&"
        commande += "subject=%s" % sujet
    if message != "" : 
        if len(adresses) == 1 and sujet == "" : 
            commande += "?"
        else:
            commande += "&"
        commande += "body=%s" % message
    #print commande
    webbrowser.open(commande)


# -----------------------------------------  Affiche l'aide -----------------------------------------------------------------------------------



def Aide(numItem=None):
    """ Appel du module d'aide de Windows """
    
##    # Demande le nom du fichier
##    import Aide
##    frm = Aide.Aide(None)
##    frm.ShowModal()
##    return
    
##    # ------- TEMPORAIRE : ---------------
##    txtMessage = _(u"Le système d'aide n'est pas encore fonctionnel (actuellement en cours de rédaction).\n\nVous pouvez tout de même trouver actuellement de l'aide sur le forum de TeamWorks à l'adresse suivante : \nhttp://teamworks.forumactif.com (ou cliquez dans la barre de menu sur 'Aide' puis 'Accéder au Forum').")
##    dlg = wx.MessageDialog(None, txtMessage, _(u"Aide"), wx.OK | wx.ICON_INFORMATION)
##    dlg.ShowModal()
##    dlg.Destroy()
##    return

    
    # -----------------------------------------------    
    nomPage = ""
    nomAncre = ""
    
    dictAide = {
        1 : ("Leplanning", "", _(u"planning")),
        2 : ("ImprimeruneDUE", "", _(u"Edition DUE")),
        3 : ("Envoyerunmailgroup", "", _(u"Envoi mail groupé")),
        4 : ("Creerunnouveaufichier", "", _(u"Créer un nouveau fichier")),
        5 : ("Imprimerunelistedeprsences", "", _(u"Impression d'une liste de présences")),
        6 : ("Lescontrats", "", _(u"Impression d'un contrat ou d'une DUE")),
        7 : ("Laprotectionparmotdepasse", "", _(u"Saisie du mot de passe d'ouverture")),
        8 : ("Lescatgoriesdeprsences", "", _(u"Config Catégories de présences")),
        9 : ("Lespriodesdevacances", "", _(u"Saisie d'une période de vacances")),
        10 : ("Lestypesdecontrats", "", _(u"Config types de contrats")),
        11 : ("Lescatgoriesdeprsences", "", _(u"Saisie d'une cat de présences")),
        12 : ("Personnes", "", _(u"Panneau Personnes")),
        13 : ("Lesvaleursdepoints", "", _(u"Saisie val point")),
        14 : ("Appliquerunmodledeprsences", "creer_modele", _(u"Saisie d'un modèle")),
        15 : ("Lespaysetnationalits", "", _(u"Config pays")),
        16 : ("Lestypesdepices", "", _(u"Config types pièces")),
        17 : ("Lasauvegardeautomatique", "", _(u"Panel sauvegarde automatique")),
        18 : ("Creerunesauvegarde", "", _(u"Créer une sauvegarde occasionnelle")),
        19 : ("Restaurerunesauvegarde", "", _(u"Restaurer une sauvegarde")),
        20 : ("Leschampsdecontrats", "", _(u"Saisie champs contrats")),
        21 : ("Ladresse", "", _(u"Gestion des villes")),
        22 : ("Imprimerunefichedefrais", "", _(u"Impression frais")),
        23 : ("Lespaysetnationalits", "", _(u"Saisir un pays")),
        24 : ("Lestypesdesituations", "", _(u"Config situations")),
        25 : ("Gestiondesfraisdedplacements", "", _(u"Gestion des frais")),
        26 : ("Laprotectionparmotdepasse", "", _(u"Config Password")),
        27 : ("Lesvaleursdepoints", "", _(u"Config val_point")),
        28 : ("Rechercherdesmisesjour", "", _(u"Updater")),
        29 : ("Crerunepice", "", _(u"Saisie pièces")),
        30 : ("Imprimerdesphotosdepersonnes", "", _(u"Impression_photo")),
        31 : ("Lesmodlesdecontrats", "", u"wiz création modele contrat"),
        32 : ("Laprotectionparmotdepasse", "", _(u"Saisie pwd")),
        33 : ("Saisirunetcheunique", "", _(u"Saisie d'une présence")),
        34 : ("Lesjoursfris", "", _(u"Config jours fériés")),
        35 : ("Leschampsdecontrats", "", _(u"Config champs contrats")),
        36 : ("Enregistrerunremboursement", "", _(u"Saisie remboursement")),
        37 : ("Imprimeruncontrat", "", u"wiz édition contrat"),
        38 : ("Lesclassifications", "", _(u"Config classifications")),
        39 : ("Lesjoursfris", "", _(u"Saisie jour férié")),
        40 : ("Appliquerunmodledeprsences", "", _(u"Application modèle de présences")),
        41 : ("Lestypesdecontrats", "", _(u"Saisie types contrats")),
        42 : ("Attribuerunephoto", "", _(u"Editeur photo")),
        43 : ("Lespriodesdevacances", "", _(u"Config périodes vacances")),
        44 : ("Enregistrerundplacement", "", _(u"Saisie déplacement")),
        45 : ("Lesgadgets", "", _(u"Config gadgets")),
        46 : ("ExporterlespersonnesdansMSOutl", "", _(u"Export Outlook")),
        47 : ("Ouvrirunfichier", "", _(u"Ouvrir un fichier")),
        48 : ("Lestypesdequalifications", "", _(u"Config types diplomes")),
        49 : ("Assistantdemarrage", "", _(u"Assistant démarrage")),
        50 : ("Lestypesdepices", "", _(u"Saisie types pièces")),
        51 : ("Lecalendrier", "", _(u"Le calendrier")),
        52 : ("Lesmodlesdecontrats", "", _(u"Config modeles contrats")),
        53 : ("Lalistedespersonnes", "Options", _(u"Config liste personnes")),
        54 : ("Creruncontrat", "", u"wiz creation contrats"),
        55 : ("Lalistedespersonnes", "export_liste", _(u"export liste personnes")),
        56 : ("Lalistedespersonnes", "Imprimer_liste", _(u"Imprimer liste Personnes")),
        57 : ("Laficheindividuelle", "", _(u"Fiche individuelle")),
        58 : ("Lagestiondesscnarios", "", _(u"Les scénarios")),
        59 : ("Lesstatistiques", "", _(u"Les statistiques")),
        60 : ("Lagestiondesutilisateurs", "", _(u"La gestion des utilisateurs réseau")),
        } # NumItem : nomPage, nomAncre, Description
    
    if numItem != None :
        nomPage, nomAncre, description = dictAide[numItem]
    
    if "linux" in sys.platform :
        
        # Aide LINUX : sur internet
        
        # Préparation du fichier chm
        nomFichier = "http://www.clsh-lannilis.com/teamworks/aide/tw.htm"
        # Préparation de la page HTML
        if nomPage != "" :
            page = "?" + nomPage + ".html"
        else:
            page = ""
        # Préparation de l'ancre
        if nomAncre != "" :
            ancre = "#" + nomAncre
        else:
            ancre = ""
        # Ouverture de la page internet
        LanceFichierExterne(nomFichier + page + ancre)
            
    else:
        # Aide WINDOWS avec le CHM
        
        # Préparation du fichier chm
        nomFichier = "Aide/teamworks.chm"
        # Préparation de la page HTML
        if nomPage != "" :
            page = "::/" + nomPage + ".html"
        else:
            page = ""
        # Préparation de l'ancre
        if nomAncre != "" :
            ancre = "#" + nomAncre
        else:
            ancre = ""
        # Ouverture du module d'aide
        commande = 'hh.exe "'+ nomFichier  + page + ancre + '"'
        from subprocess import Popen
        Popen(commande)



class Aide_archive():
    def __init__(self, frameParente, sujet=""):
        self.frameParente = frameParente
        
        # Création du widget
        self.frameParente.frmAide = wx.html.HtmlHelpController()
        
        # Création des pages
        self.CreationPages()
            
        # Choix de la page affichée
        if sujet == "" : self.frameParente.frmAide.DisplayContents()
        else: self.frameParente.frmAide.Display(sujet)
        
        # Réglages des propriétés de la frame Help
        self.frameAide = self.frameParente.frmAide.GetFrame()
        self.Proprietes()
        
        # Bind
        self.frameAide.Bind(wx.EVT_CLOSE, self.OnClose )
    
    def Proprietes(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.frameAide.SetIcon(_icon)
        self.frameAide.SetTitle(_(u"Aide de TeamWorks"))
        self.frameParente.frmAide.SetTitleFormat(_(u"Aide de TeamWorks"))
        self.frameAide.MakeModal(True)
        
    def CreationPages(self):
        self.frameParente.frmAide.AddBook("Aide/testing.hhp")
        self.frameParente.frmAide.AddBook("Aide/another.hhp")
        
    def OnClose(self, event):
        self.frameAide.MakeModal(False)
        self.frameParente.MakeModal(True)
        event.Skip()


def CompareVersions(versionApp="", versionMaj=""):
    """ Compare 2 versions """
    """ Return True si la version MAJ est plus récente """
    a,b = [[int(n) for n in version.split(".")] for version in [versionMaj, versionApp]]
    return a>b


def GetListeCadresPhotos():
    """ Récupère la liste des noms des cadres photos dispo sur le DD """
    listeNomCadres = []
    listeFichiers = os.listdir("Images/CadresPhotos")
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".png"):
            listeNomCadres.append(nomFichier[:-4])
    listeNomCadres.sort()
    listeNomCadres.insert(0, _(u"Aucun"))
    return listeNomCadres

def RecupNomCadrePersonne(IDpersonne):
    """ Récupère le nom du cadre de décoration pour une personne donnée """
    DB = GestionDB.DB()        
    req = "SELECT cadre_photo FROM personnes WHERE IDpersonne=%d;" % IDpersonne
    DB.executerReq(req)
    donnees = DB.resultatReq()
    DB.close()
    if len(donnees) == 0 : return None
    cadre_photo = donnees[0][0]
    if cadre_photo == "" : return None
    return cadre_photo

def RecupTextePhotoPersonne(IDpersonne):
    """ Récupère le contenu du texte photo pour une personne donnée """
    DB = GestionDB.DB()        
    req = "SELECT texte_photo FROM personnes WHERE IDpersonne=%d;" % IDpersonne
    DB.executerReq(req)
    donnees = DB.resultatReq()
    DB.close()
    if len(donnees) == 0 : return ""
    texte_photo = donnees[0][0]
    if texte_photo == None : texte_photo = ""
    return texte_photo

def CreationPhotoPersonne(IDpersonne=0, nomFichierPhoto="", tailleFinale = None, qualiteBmp = 50):
    """ Création des photos avec cadre de décoration """
    # Récupération de la photo
    if os.path.isfile(nomFichierPhoto) == False : return None
    photo = wx.Bitmap(nomFichierPhoto, wx.BITMAP_TYPE_ANY)
    tailleInitiale = photo.GetSize()
    # Création du dc temporaire
    bmp = wx.EmptyBitmap(tailleInitiale[0], tailleInitiale[1])
    dc = wx.MemoryDC()
    dc.SelectObject(bmp)
    dc.SetBackground(wx.Brush("black"))
    dc.Clear()
    # Dessin de la photo
    dc.DrawBitmap(photo, 0, 0, 0)
    # Dessin du cadre de décoration
    nomCadre = RecupNomCadrePersonne(IDpersonne)
    if nomCadre != None :
        masque = wx.Bitmap("Images/CadresPhotos/" + nomCadre + ".png", wx.BITMAP_TYPE_PNG)
        dc.DrawBitmap(masque, 0, 0)
    # Redimensionne et retourne l'image bmp
    if tailleFinale != None :
        bmp = bmp.ConvertToImage()
        bmp = bmp.Rescale(width=tailleFinale[0], height=tailleFinale[1], quality=qualiteBmp) 
        bmp = bmp.ConvertToBitmap()
    return bmp


def RecupIDfichier():
    """ Récupère le code identifiant unique du fichier """
    DB = GestionDB.DB()        
    req = "SELECT codeIDfichier FROM divers WHERE IDdivers=1;"
    DB.executerReq(req)
    donnees = DB.resultatReq()
    DB.close()
    codeIDfichier = donnees[0][0]
    return codeIDfichier

def VideRepertoireTemp():
    """ Supprimer tous les fichiers du répertoire TEMP """
    for rep in ("Temp/", UTILS_Fichiers.GetRepTemp()) :
        if os.path.isdir(rep) :
            for nomFichier in os.listdir(rep) :
                nomComplet = os.path.join(rep, nomFichier)
                try :
                    if os.path.isdir(nomComplet) :
                        shutil.rmtree(nomComplet)
                    else :
                        os.remove(nomComplet)
                except Exception as err :
                    print(err)

def VideRepertoireUpdates(forcer=False):
    """ Supprimer les fichiers temporaires du répertoire Updates """
    try :
        listeReps = UTILS_Fichiers.GetRepUpdates()
        numVersionActuelle = GetVersionLogiciel()
        for nomRep in os.listdir(listeReps) :
            resultat = CompareVersions(versionApp=numVersionActuelle, versionMaj=nomRep)
            if resultat == False or forcer == True :
                # Le rep est pour une version égale ou plus ancienne
                if numVersionActuelle != nomRep or forcer == True :
                    # Si la version est ancienne, suppression du répertoire
                    shutil.rmtree(UTILS_Fichiers.GetRepUpdates(nomRep))
                else:
                    # La version est égale : on la laisse pour l'instant
                    pass
    except Exception as err:
        print(err)
        pass
        
def ListeImprimantes():
    """ Recherche les imprimantes installées """
    if sys.platform.startswith("win") :
        import win32print
        
    listeImprimantesLocales = []
    listeImprimantesReseau = []
    listeToutesImprimantes = []

    try:
        for (Flags,pDescription,pName,pComment) in list(win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,None,1)):
            listeImprimantesLocales.append(pName)
            listeToutesImprimantes.append(pName)
    except : pass
        
    try:   
        for (Flags,pDescription,pName,pComment) in list(win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS,None,1)):
            listeImprimantesReseau.append(pName)
            listeToutesImprimantes.append(pName)
    except : pass
    
    nomImprimanteDefaut = ""
    try :
        nomImprimanteDefaut = win32print.GetDefaultPrinter()
    except : pass

    return nomImprimanteDefaut, listeToutesImprimantes, listeImprimantesLocales, listeImprimantesReseau

def EnleveAccents(chaineUnicode):
    """ Enlève les accents d'une chaine unicode """
    import unicodedata
    if type(chaineUnicode) == str :
        if six.PY2:
            chaineUnicode = chaineUnicode.decode("iso-8859-15")
    resultat = unicodedata.normalize('NFKD', chaineUnicode).encode('ascii','ignore')
    return resultat

def AfficheStatsProgramme():
    """ Affiche des stats du programme """
    listeResultats = []
    nbreDialogs = 0
    nbreFrames = 0
    nbreImpressionsOL = 0
    nbreImpressionsPDF = 0
    nbreLignesTotal = 0
    nbreBoitesDialogue = 0
    nbreFonctions = 0
    
    # Recherche les fichiers python
    print("Lancement de l'analyse...")

    listeFichiers = {}
    for rep in ("Dlg", "Ctrl", "Ol", "Utils"):
        if rep not in listeFichiers:
            listeFichiers[rep] = []
        listeFichiers[rep] = os.listdir(os.getcwd() + "/" + rep)

    for rep, liste in listeFichiers.items() :
        for nomFichier in liste:
            if nomFichier.endswith(".py") :
                fichier = open(rep + "/" + nomFichier, 'r')
                nbreLignes = 0
                for line in fichier :
                    # Compte le nombre de lignes
                    nbreLignes += 1
                    # Recherche d'un wx.Dialog
                    if "wx.Dialog.__init__" in line : nbreDialogs += 1
                    # Recherche une impression ObjectListview
                    if "prt.Print()" in line : nbreImpressionsOL += 1
                    # Recherche une impression PDF avec reportlab
                    if "doc.build(story)" in line : nbreImpressionsPDF += 1
                    # Recherche des boîtes de dialogue
                    if "wx.MessageDialog(" in line : nbreBoitesDialogue += 1
                    # Recherche le nbre de fonctions
                    if " def " in line : nbreFonctions += 1

                fichier.close()
                # Mémorise les résultats
                listeResultats.append((nomFichier, nbreLignes))
                nbreLignesTotal += nbreLignes
    
    # Nbre tables
    from DATA_Tables import DB_DATA
    nbreTables = len(list(DB_DATA.keys())) + 2
    
    # Affiche les résultats
    for nomFichier, nbreLignes in listeResultats :
        print("%s ---> %d lignes" % (nomFichier, nbreLignes))
    print("----------------------------------------")
    print("Nbre total de lignes = %d lignes" % nbreLignesTotal)
    print("Nbre total de modules = %s modules" % len(listeResultats))
    print("Nbre total de fonctions = %d" % nbreFonctions) 
    print("----------------------------------------")
    print("Nbre total de wx.Dialog = %d" % nbreDialogs)
    print("Nbre total d'impressions ObjectlistView = %d" % nbreImpressionsOL) 
    print("Nbre total d'impressions PDF = %d" % nbreImpressionsPDF) 
    print("Nbre total de boites de dialogue = %d" % nbreBoitesDialogue) 
    print("----------------------------------------")
    print("Nbre tables de données = %d" % nbreTables)

def GetRepertoireProjet(fichier=""):
    frozen = getattr(sys, 'frozen', '')
    if not frozen:
        chemin = os.path.dirname(os.path.abspath(__file__))
    else :
        chemin = os.path.dirname(sys.executable)
    return os.path.join(chemin, fichier)

def GetVersionLogiciel():
    """ Recherche du numéro de version du logiciel """
    fichierVersion = codecs.open(GetRepertoireProjet("Versions.txt"), encoding='utf-8', mode='r')
    txtVersion = fichierVersion.readlines()[0]
    fichierVersion.close() 
    pos_debut_numVersion = txtVersion.find("n")
    pos_fin_numVersion = txtVersion.find("(")
    numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
    return numVersion

def LanceFichierExterne(nomFichier) :
    """ Ouvre un fichier externe sous windows ou linux """
    nomSysteme = sys.platform
    if nomSysteme.startswith("win") : 
        nomFichier = nomFichier.replace("/", "\\")
        os.startfile(nomFichier)
    if "linux" in nomSysteme : 
        os.system("xdg-open " + nomFichier)

def GetNomDB():
    """ Renvoie le nom simple du fichier """
    nom = ""
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est chargée, on y récupère le dict de config
        nom = topWindow.userConfig["nomFichier"]
    else:
        # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
        cfg = FichierConfig()
        nom = cfg.GetItemConfig("nomFichier")
    return nom


def supprime_accent(mot):
    """ supprime les accents du texte source """
    out = ""
    for c in mot:
        if c == u'é' or c == u'è' or c == u'ê':
            c = 'e'
        elif c == u'à':
            c = 'a'
        elif c == u'ù' or c == u'û':
            c = 'u'
        elif c == u'î':
            c = 'i'
        elif c == u'ç':
            c = 'c'
        out += c
    return str(out)

def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"), (u"/", u""), (u"\\", u""), ]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def Supprime_accent2(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"), ]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def OuvrirCalculatrice():
    if sys.platform.startswith("win") : LanceFichierExterne("calc.exe")
    if "linux" in sys.platform : os.system("gcalctool")

def RemplacerContenuFichier():
    listeRemplacements = [
##        ("ColumnDefn, Filter", "ColumnDefn, Filter, CTRL_Outils"),
        ("wx.SearchCtrl.__init__(self, parent, size=(-1,20)", "wx.SearchCtrl.__init__(self, parent, size=(-1, -1)"),
        ]
    #listeFichiers = os.listdir("C:\Users\Ivan\Documents\GitHub\Noethys\source")
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") :
            fichier = open(nomFichier, 'r')
            
            # Recherche si fichier concerné ou non
            trouve = False
            for old, new in listeRemplacements :
                for line in fichier :
                    if old in line :
                        trouve = True
                        break
            
            fichier.close()
            
            # Effectue les remplacements
            if trouve == True :
                nouveauFichier = open("New/%s" % nomFichier, 'w')
                fichier = open(nomFichier, 'r')
                for line in fichier :
                    for old, new in listeRemplacements :
                        if old in line :
                            print(nomFichier)
                            line = line.replace(old, new)
                    nouveauFichier.write(line)
                nouveauFichier.close()
                fichier.close()
            

def PreparationFichierDefaut(nomFichier=""):
    """ Prépare le fichier de données par défaut """
    import DATA_Tables as Tables
    import sqlite3
    listeTablesObligatoires = []
    # Récupère les tables optionnelles
    for nom, listeTablesTmp, select in Tables.TABLES_IMPORTATION_OPTIONNELLES :
        for table in listeTablesTmp :
            listeTablesObligatoires.append(table)
    # Récupère les tables optionnelles
    for table in Tables.TABLES_IMPORTATION_OBLIGATOIRES :
        listeTablesObligatoires.append(table)
    
    # Ouverture du fichier de référence
    connexion = sqlite3.connect(nomFichier.encode('utf-8'))
    cursor = connexion.cursor()
    
    # Recherche les tables de la base
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    listeTablesBase = cursor.fetchall()
    for nomTable, in listeTablesBase :
        # Supprime les tables non nécessaires
        if nomTable not in listeTablesObligatoires and nomTable != "sqlite_sequence"  :
            cursor.execute("DROP TABLE %s;" % nomTable)
    connexion.commit()
    # Fermeture base
    connexion.close() 
    print("Procedure terminee.")

##if __name__ == "__main__":
##    RemplacerContenuFichier()


def Formate_taille_octets(size):
    """
    fonction qui prend en argument un nombre d'octets
    et renvoie la taille la plus adapté
    """
    seuil_Kio = 1024
    seuil_Mio = 1024 * 1024
    seuil_Gio = 1024 * 1024 * 1024

    if size > seuil_Gio:
        return "%.2f Go" % (size/float(seuil_Gio))
    elif size > seuil_Mio:
        return "%.2f Mo" % (size/float(seuil_Mio))
    elif size > seuil_Kio:
        return "%.2f Ko" % (size/float(seuil_Kio))
    else:
        return "%i o" % size

def RechercheImports():
    """ Renvoie la liste de tous les modules importés du logiciel """
    listeImports = []
    listeFichiers = os.listdir(os.getcwd())
    listeExclusions = ("wx", "DLG", "OL", "CTRL", "UTILS", "DATA")
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") :
            fichier = open(nomFichier, 'r')
            for line in fichier :
                if line.startswith("import") :
                    nomImport = line[7:-1]
                    if nomImport not in listeImports :
                        valide = True
                        for exclusion in listeExclusions :
                            if nomImport.startswith(exclusion) :
                                valide = False
                        if valide == True :
                            listeImports.append(nomImport)
            fichier.close()
    listeImports.sort()
    return listeImports

def RechercherAideManquante():
    listeFichiers = os.listdir(os.getcwd())
    listeFichiersTrouves = []
    fichierResultats = open(UTILS_Fichiers.GetRepTemp(fichier="resultats.txt"), 'w')
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") :
            fichier = open(nomFichier, 'r')
            boutonAidePresent = False
            fonctionAidePresente = False
            for line in fichier :
                if "self.bouton_aide" in line :
                    boutonAidePresent = True
                if "Aide(self" in line :
                    fonctionAidePresente = True
            if boutonAidePresent == True and fonctionAidePresente == False :
                listeFichiersTrouves.append(nomFichier)
                fichierResultats.write(u"%s\n" % nomFichier)
                
            fichier.close()
    fichierResultats.close()
    print(len(listeFichiersTrouves), "fichier trouves.")


def RemplacerDeprecatedWxpython():
    listeFichiers = os.listdir(os.getcwd())
    listeFichiersTrouves = []
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") and "FonctionsPerso.py" not in nomFichier :
            print("%s..." % nomFichier)
            fichier = open(nomFichier, 'r')
            nouveauFichier = open("New/%s" % nomFichier, 'w')
            numLigne = 1
            try :
                for ligne in fichier :
                    # ----- Remplacement de lignes ------ 
                    
                    # wx.FlexGridSizer
                    for chaine in ("wx.FlexGridSizer(", "wx.GridSizer(") :
                        if chaine in ligne and "rows=" not in ligne :
                            positionDebut = ligne.index(chaine)
                            positionFin = ligne.index(")", positionDebut) + 1
                            valeurs = ligne[positionDebut + len(chaine) : positionFin-1]
                            
                            if len(valeurs.split(", ")) == 4 :
                                newValeurs = "rows=%s, cols=%s, vgap=%s, hgap=%s" % tuple(valeurs.split(", "))
                                ligne = ligne.replace(valeurs, newValeurs)
                                #print nomFichier, ligne
                            else :
                                newValeurs = valeurs
                                print("ERREUR !!!!!!!! ---------> ", nomFichier, numLigne, valeurs, "-->", newValeurs)
                    
                    # wx.PySimpleApp
                    chaine = "wx.PySimpleApp"
                    if chaine in ligne :
                        ligne = ligne.replace(chaine, "wx.App")
                    
                    # wx.InitAllImageHandlers()
                    chaine = " wx.InitAllImageHandlers()"
                    if chaine in ligne :
                        ligne = ligne.replace(chaine, " #wx.InitAllImageHandlers()")
                    
                    # Ecriture
                    nouveauFichier.write(ligne)
                    numLigne += 1
            except Exception as err:
                print(nomFichier, err)
            fichier.close()
            nouveauFichier.close()
            print("fini !!!!!!!!!!!!!!!!!")


def ReplacementChaine(chaine="", avant="", apres="", remplacement=""):
    """ Remplacement de chaine avec regex """
    """ Exemple : print ReplacementChaine(chaine=u'<FONT facename="Segoe UI">Bonjour</FONT>', avant='facename="', apres='"', remplacement="ARIAL") """
    import re
    return re.sub(r'%s.*?%s' % (avant, apres), '%s%s%s' % (avant, remplacement, apres), chaine)

def PrepareFichierBIC():
    fichier = open("liste_bic_france.txt", 'r')
    nouveauFichier = open(UTILS_Fichiers.GetRepTemp(fichier="liste_bic_france_new.txt"), 'w')
    for ligne in fichier :
        ID, nom, ville, divers, bic = ligne.split("\t")
        nouvelleLigne = """("%s", "%s", "%s")\n""" % (nom, ville, bic[:-1])
        nouveauFichier.write(nouvelleLigne)
    nouveauFichier.close()
    fichier.close()

def RechercheModules(nomFichier="Noethys.py") :
    """ Recherche les modules dépendants d'un script """
    from modulefinder import ModuleFinder
    finder = ModuleFinder()
    finder.run_script(nomFichier)
    listeModules = []
    for nom, mod in finder.modules.items():
        cheminFichier = mod.__file__
        if cheminFichier != None and "Noethys" in cheminFichier :
            cheminFichier = cheminFichier.replace(os.getcwd(), "")
            if cheminFichier.startswith("\\") :
                cheminFichier = cheminFichier[1:]
            listeModules.append(cheminFichier)
    listeModules.sort() 
    return listeModules

def GetIDfichier():
    try :
        DB = GestionDB.DB()
        req = """SELECT IDparametre, nom, parametre 
        FROM parametres WHERE nom='IDfichier';"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        IDfichier = listeTemp[0][2]
    except :
        IDfichier = ""
    return IDfichier

def GenerationIDdoc():
    """ Génération d'un ID unique à base de la date, de l'heure de l'IDfichier et d'un numéro aléatoire """
    IDfichier = GetIDfichier()[14:17]
    numAleatoire = random.randint(100, 999)
    horodatage = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
    IDdoc = "%s%s%d" % (horodatage, IDfichier, numAleatoire)
    return IDdoc

def GenerationNomDoc(prefixe="", extension="pdf"):
    """ Génération d'un nom de document dans le répertoire Temp"""
    nomDoc = "%s%s.%s" % (prefixe, GenerationIDdoc() , extension)
    return UTILS_Fichiers.GetRepTemp(nomDoc)

def InsertUnicodeLiterals():
    """ Pour insérer  dans tous les fichiers """
    # Get fichiers
    listeFichiers = os.listdir(os.getcwd())
    indexFichier = 0
    for nomFichier in listeFichiers :
        if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False :
            #print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)
            
            # Ouverture des fichiers
            fichier = open(nomFichier, "r")
            dirty = False
            
            listeLignes = []
            for ligne in fichier :
                # Insertion de l'import
                if "from Utils.UTILS_Traduction import _" in ligne :
                    listeLignes.append("\n")
                    dirty = True
                
                listeLignes.append(ligne) 
                
            # Clôture des fichiers
            fichier.close()
            
            # Ecriture du nouveau fichier
            if dirty == True :
                nouveauFichier = open("New/%s" % nomFichier, "w")
                for ligne in listeLignes :
                    nouveauFichier.write(ligne)
                nouveauFichier.close()
            
        indexFichier += 1
            
    print("Fini !!!!!!!!!!!!!!!!!")


def InsertThemeDansOL():
    """ Pour insérer la prise en charge des thèmes dans les OL """
    # Get fichiers
    listeFichiers = os.listdir(os.getcwd())
    indexFichier = 0
    for nomFichier in listeFichiers :
        if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False :
            #print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)

            # Ouverture des fichiers
            fichier = open(nomFichier, "r")
            dirty = False

            listeLignes = []
            for ligne in fichier :

                # Insertion de l'import
                if "from ObjectListView" in ligne :
                    listeLignes.append("\n")
                    listeLignes.append("import UTILS_Interface\n")
                    dirty = True

                # Insertion de l'import
                if "self.oddRowsBackColor =" in ligne :
                    ligne = """        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))\n"""
                    dirty = True

                listeLignes.append(ligne)

            # Clôture des fichiers
            fichier.close()

            # Ecriture du nouveau fichier
            if dirty == True :
                nouveauFichier = open("New/%s" % nomFichier, "w")
                for ligne in listeLignes :
                    nouveauFichier.write(ligne)
                nouveauFichier.close()

        indexFichier += 1

    print("Fini !!!!!!!!!!!!!!!!!")


def RechercheWhere():
    """ Pour rechercher les clauses WHERE dans tous les fichiers """
    # Get fichiers
    listeFichiers = os.listdir(os.getcwd())
    for nomFichier in listeFichiers :
        if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False :
            # Ouverture du fichier
            fichier = open(nomFichier, "r")
            for ligne in fichier :
                # Insertion de l'import
                if "WHERE" in ligne :
                    ligne = ligne.replace("\n", "")
                    ligne = ligne.replace("  ", "")
                    print(ligne)
                
            # Clôture des fichiers
            fichier.close()
            
    print("Fini !!!!!!!!!!!!!!!!!")


def CreerDonneesVirtuelles(nbreFamilles=0):
    """ Pour remplir la base artificiellement avec des données familles virtuelles """
    DB = GestionDB.DB()
    for x in range(0, nbreFamilles) :
        
        print("Creation de la famille %d/%d..." % (x+1, nbreFamilles))
        
        # Famille
        IDfamille = DB.ReqInsert("familles", [("date_creation", datetime.date.today()), ("IDcompte_payeur", None)])
        
        # Compte payeur
        IDcompte_payeur = DB.ReqInsert("comptes_payeurs", [("IDfamille", IDfamille),])
        DB.ReqMAJ("familles", [("IDcompte_payeur", IDcompte_payeur),], "IDfamille", IDfamille)
        
        # Individus
        IDpere = DB.ReqInsert("individus", [("IDcivilite", 1), ("nom", u"PERE%d" % IDfamille), ("prenom", u"Père%d" % IDfamille), ("rue_resid", u"10 rue des oiseaux"), ("cp_resid", "29200"), ("ville_resid", u"BREST"), ("date_creation", datetime.date.today())])
        IDmere = DB.ReqInsert("individus", [("IDcivilite", 3), ("nom", u"MERE%d" % IDfamille), ("prenom", u"Mère%d" % IDfamille), ("rue_resid", u"10 rue des oiseaux"), ("cp_resid", "29200"), ("ville_resid", u"BREST"), ("date_creation", datetime.date.today())])
        IDenfant = DB.ReqInsert("individus", [("IDcivilite", 4), ("nom", u"ENFANT%d" % IDfamille), ("prenom", u"Enfant%d" % IDfamille), ("rue_resid", u"10 rue des oiseaux"), ("cp_resid", "29200"), ("ville_resid", u"BREST"), ("date_creation", datetime.date.today())])
        
        # Rattachements
        IDrattachement = DB.ReqInsert("rattachements", [("IDindividu", IDpere), ("IDfamille", IDfamille), ("IDcategorie", 1), ("titulaire", 1)])
        IDrattachement = DB.ReqInsert("rattachements", [("IDindividu", IDmere), ("IDfamille", IDfamille), ("IDcategorie", 1), ("titulaire", 1)])
        IDrattachement = DB.ReqInsert("rattachements", [("IDindividu", IDenfant), ("IDfamille", IDfamille), ("IDcategorie", 2), ("titulaire", 0)])
        
        # Liens
        IDlien = DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", IDmere), ("IDtype_lien", 10), ("IDindividu_objet", IDpere)])
        IDlien = DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", IDpere), ("IDtype_lien", 10), ("IDindividu_objet", IDmere)])
        IDlien = DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", IDenfant), ("IDtype_lien", 2), ("IDindividu_objet", IDpere)])
        IDlien = DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", IDenfant), ("IDtype_lien", 2), ("IDindividu_objet", IDmere)])
        IDlien = DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", IDpere), ("IDtype_lien", 1), ("IDindividu_objet", IDenfant)])
        IDlien = DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", IDmere), ("IDtype_lien", 1), ("IDindividu_objet", IDenfant)])
        
        # Inscriptions
        IDinscription = DB.ReqInsert("inscriptions", [("IDindividu", IDenfant), ("IDfamille", IDfamille), ("IDactivite", 1), ("IDgroupe", 1), ("IDcategorie_tarif", 1), ("IDcompte_payeur", IDcompte_payeur), ("date_inscription", datetime.date.today()), ("parti", 0)])
        
        # Prestations et consommations
        date = datetime.date(2015, 6, 3)
        IDprestation = DB.ReqInsert("prestations", [("IDcompte_payeur", IDcompte_payeur), ("date", date), ("categorie", "consommation"), ("label", u"Journée avec repas"), ("montant_initial", 13.0), ("montant", 13.0), ("IDactivite", 1), ("IDtarif", 33), ("IDfamille", IDfamille), ("IDindividu", IDenfant), ("temps_facture", "11:00"), ("IDcategorie_tarif", 1), ("date_valeur", str(datetime.date.today()))])
        for IDunite in (1, 2) :
            IDconso = DB.ReqInsert("consommations", [("IDindividu", IDenfant), ("IDinscription", IDinscription), ("IDactivite", 1), ("date", date), ("IDunite", IDunite), ("IDgroupe", 1), ("etat", "reservation"), ("verrouillage", 0), ("date_saisie", datetime.date.today()), ("IDutilisateur", 1), ("IDcategorie_tarif", 1), ("IDcompte_payeur", IDcompte_payeur), ("IDprestation", IDprestation)])
        
        
    DB.Close()


def CreerDonneesVirtuellesLocations(nbreFamilles=0):
    """ Pour remplir la base artificiellement avec des données familles virtuelles """
    DB = GestionDB.DB()

    # Lecture des produits
    req = """SELECT IDproduit, nom, IDcategorie FROM produits;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeProduits = []
    for IDproduit, nom, IDcategorie in listeDonnees :
        listeProduits.append({"IDproduit" : IDproduit, "nom" : nom, "IDcategorie" : IDcategorie})

    # Saisie des données
    for x in range(0, nbreFamilles):

        print("-----  Creation de la famille %d/%d... -----" % (x + 1, nbreFamilles))

        # Famille
        IDfamille = DB.ReqInsert("familles", [("date_creation", datetime.date.today()), ("IDcompte_payeur", None)])
        print("IDfamille = %d" % IDfamille)

        # Compte payeur
        IDcompte_payeur = DB.ReqInsert("comptes_payeurs", [("IDfamille", IDfamille), ])
        DB.ReqMAJ("familles", [("IDcompte_payeur", IDcompte_payeur), ], "IDfamille", IDfamille)

        # Individus
        IDindividu = DB.ReqInsert("individus", [("IDcivilite", 1), ("nom", u"NOM%d" % IDfamille), ("prenom", u"Prenom%d" % IDfamille), ("rue_resid", u"10 rue des oiseaux"), ("cp_resid", "29200"), ("ville_resid", u"BREST"), ("date_creation", datetime.date.today())])

        # Rattachements
        IDrattachement = DB.ReqInsert("rattachements", [("IDindividu", IDindividu), ("IDfamille", IDfamille), ("IDcategorie", 1), ("titulaire", 1)])

        # Saisie de locations ou de demandes
        d = datetime.datetime.now()
        aujourdhui = datetime.datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, minute=d.minute)

        if x < len(listeProduits) :
            # Création d'une location
            IDproduit = listeProduits[x]["IDproduit"]
            IDlocation = DB.ReqInsert("locations", [("IDfamille", IDfamille), ("IDproduit", IDproduit), ("observations", ""), ("date_saisie", datetime.date.today()), ("date_debut", aujourdhui)])
            print("Location ID%d du produit ID%d" % (IDlocation, IDproduit))
        else :

            # Création d'une demande de location
            dictProduit = random.choice(listeProduits)
            categories = str(dictProduit["IDcategorie"])
            produits = None #str(dictProduit["IDproduit"])
            statut = "attente"
            motif_refus = ""
            IDdemande = DB.ReqInsert("locations_demandes", [("date", aujourdhui),("IDfamille", IDfamille), ("observations", ""), ("categories", categories), ("produits", produits), ("statut", statut), ("motif_refus", motif_refus)])
            print("Demande ID%d" % IDdemande)

            # Création d'un filtre pour la demande
            liste_choix = ["6", "12", "18", "24", "30", "36", "48"]
            listeDonnees = [
                ("IDquestion", 5),
                ("categorie", "location_demande"),
                ("choix", "EGAL"),
                ("criteres", random.choice(liste_choix)),
                ("IDdonnee", IDdemande),
                ]
            IDfiltre = DB.ReqInsert("questionnaire_filtres", listeDonnees)

    DB.Close()


def InsertCode():
    """ Pour insérer  dans tous les fichiers """
    import re
    x = re.compile(r'(wx.Bitmap\()(.*?)(,)')

    for repertoire in ("Ctrl", "Dlg", "Ol", "Utils") :
    #for repertoire in ("",) :
        # Création du répertoire temporaire
        if not os.path.isdir("%s/New" % repertoire):
            os.mkdir("%s/New" % repertoire)

        # Get fichiers
        listeFichiers = os.listdir(os.path.join(os.getcwd(), repertoire))
        indexFichier = 0
        for nomFichier in listeFichiers :
            if nomFichier.endswith("py") :
                #print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)

                # Ouverture des fichiers
                fichier = open(os.path.join(repertoire, nomFichier), "r")
                dirty = False

                listeLignes = []
                for ligne in fichier :

                    # Insertion de l'import Chemins
                    if "import Chemins" in ligne :
                        ligne = "import Chemins\nfrom Utils import UTILS_Adaptations\n"
                        dirty = True

                    # Remplacement de wx.Menu
                    if "wx.Menu()" in ligne :
                        ligne = ligne.replace("wx.Menu()", "UTILS_Adaptations.Menu()")
                        dirty = True

                    # # Modification de UTILS_Traduction
                    # if "UTILS_Traduction" in ligne and repertoire != "Utils" :
                    #     ligne = ligne.replace("UTILS_Traduction", "Utils.UTILS_Traduction")
                    #     dirty = True
                    #     print "Traduction:", ligne
                    #
                    # # Modification from ... import
                    # for rep in ("CTRL", "DATA", "DLG", "OL", "UTILS") :
                    #     chaine = "from %s_" % rep
                    #     if chaine in ligne and rep.capitalize() != repertoire and "UTILS_Traduction" not in ligne :
                    #         ligne = ligne.replace(chaine, "from %s.%s_" % (rep.capitalize(), rep))
                    #         dirty = True
                    #         print "from:", ligne
                    #
                    # # Modification import
                    # for rep in ("CTRL", "DATA", "DLG", "OL", "UTILS") :
                    #     chaine = "import %s_" % rep
                    #     if chaine in ligne and rep.capitalize() != repertoire and "from" not in ligne and "UTILS_Traduction" not in ligne :
                    #         ligne = ligne.replace(chaine, "from %s import %s_" % (rep.capitalize(), rep))
                    #         dirty = True
                    #         print "Import:", ligne

                    # Modification chemin Images
                    # m = x.search(ligne)
                    # if m:
                    #     chaine = m.group(2)
                    #     ligne = ligne.replace(chaine, 'Chemins.GetStaticPath(%s)' % chaine)
                    #     dirty = True
                    #     print "Images:", ligne

                    listeLignes.append(ligne)

                # Clôture des fichiers
                fichier.close()

                # Ecriture du nouveau fichier
                if dirty == True :
                    nouveauFichier = open(os.path.join(repertoire, "New", nomFichier), "w")
                    for ligne in listeLignes :
                        nouveauFichier.write(ligne)
                    nouveauFichier.close()

            indexFichier += 1

    print("Fini !!!!!!!!!!!!!!!!!")


def InsertCodeToolTip():
    """ Pour insérer  dans tous les fichiers """
    import re
    #x = re.compile(r'\.SetToolTipString\((.*?\))')
    x = re.compile(r'\.SetToolTip\(')

    for repertoire in ("Ctrl", "Dlg", "Ol", "Utils") :
        # Création du répertoire temporaire
        if not os.path.isdir("%s/New" % repertoire):
            os.mkdir("%s/New" % repertoire)

        # Get fichiers
        listeFichiers = os.listdir(os.path.join(os.getcwd(), repertoire))
        indexFichier = 0
        for nomFichier in listeFichiers :
            if nomFichier.endswith("py") :
                print("%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier))

                # Ouverture des fichiers
                fichier = open(os.path.join(repertoire, nomFichier), "r")
                dirty = False

                listeLignes = []
                for ligne in fichier :

                    # Modification chemin Images
                    #m = x.search(ligne)
                    if ".SetToolTip(" in ligne and '))"))' in ligne :
                        #chaine = m.group(1)
                        ligne = ligne.replace('))"))', ')")))')
                        dirty = True
                        print(("      > ", ligne))

                    listeLignes.append(ligne)

                # Clôture des fichiers
                fichier.close()

                # Ecriture du nouveau fichier
                if dirty == True :
                    nouveauFichier = open(os.path.join(repertoire, "New", nomFichier), "w")
                    for ligne in listeLignes :
                        nouveauFichier.write(ligne)
                    nouveauFichier.close()

            indexFichier += 1

    print("Fini !!!!!!!!!!!!!!!!!")





if __name__ == "__main__":
    # ------- Affiche les stats -------
    AfficheStatsProgramme()
    
##    InsertUnicodeLiterals() 

    # Adaptation wxPython 2.9
    #RemplacerDeprecatedWxpython()
    
##    app = wx.App(0)
##    import wx.lib.dialogs as dialogs
##    image = wx.Bitmap("Images/32x32/Activite.png", wx.BITMAP_TYPE_ANY)
##    message2 = _(u"Ceci est un message super méga long qui doit prendre pas mal de place !\n") * 50
##    dlg = dialogs.MultiMessageDialog(None, _(u"Ceci est le message 1"), caption = "Message Box", msg2=message2, style = wx.ICON_EXCLAMATION | wx.OK | wx.CANCEL, icon=None, btnLabels={wx.ID_OK : _(u"Ok"), wx.ID_CANCEL : _(u"Annuler")})
##    dlg.ShowModal() 
##    dlg.Destroy() 
##    app.MainLoop()
    
    # Recherche de modules
##    listeModules = RechercheModules("OL_Liste_comptes.py")
##    for x in listeModules :
##        print x
##    print "-------------------- Modules trouves : %d --------------------" % len(listeModules) 
    
    # Créer des données virtuelles dans DB
    #InsertThemeDansOL()

    # Génération d'un nom de document
    #print GenerationNomDoc("document", "pdf")
    
    #VideRepertoireUpdates(forcer=True)

    #InsertCodeToolTip()
    #CreerDonneesVirtuellesLocations(1000)

    #InsertCode()

    pass
