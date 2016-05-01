#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _

import wx
import CTRL_Bouton_image
if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC

import sys
import os
import time
import datetime
import operator
import sqlite3
import cStringIO
import GestionDB
import UTILS_Utilisateurs
import UTILS_Fichiers

TAILLE_IMAGE = (32, 32)



def FormatFileSize(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0:
            return "%3.2f %s" % (size, x)
        size /= 1024.0


def RecadreImg(img=None):
    tailleMaxi = max(TAILLE_IMAGE)
    largeur, hauteur = img.GetSize()
    if max(largeur, hauteur) > tailleMaxi :
        if largeur > hauteur :
            hauteur = hauteur * tailleMaxi / largeur
            largeur = tailleMaxi
        else:
            largeur = largeur * tailleMaxi / hauteur
            hauteur = tailleMaxi
    img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
    position = (((TAILLE_IMAGE[0]/2.0) - (largeur/2.0)), ((TAILLE_IMAGE[1]/2.0) - (hauteur/2.0)))
    img.Resize(TAILLE_IMAGE, position, 255, 255, 255)
    return img



class FirstColumnRenderer(object):
    def __init__(self, parent, titre=u"", image=None, description=u""):
        self.parent = parent

        self.normalFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.normalFont.SetPointSize(self.normalFont.GetPointSize() + 2)        
        self.smallerFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        self.greyColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

        self.text = titre
        self.icon = image
        self.description = description
        

    def DrawSubItem(self, dc, rect, line, highlighted, enabled):
        """Draw a custom progress bar using double buffering to prevent flicker"""
        if self.icon != None :
            bmpWidth, bmpHeight = self.icon.GetWidth(), self.icon.GetHeight()        
            dc.DrawBitmap(self.icon, rect.x+5, rect.y+(rect.height-bmpHeight)/2)
        else :
            bmpWidth, bmpHeight = TAILLE_IMAGE
            
        dc.SetFont(self.normalFont)
                        
        textWidth, textHeight = dc.GetTextExtent(self.text)
        dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT))
        dc.DrawText(self.text, rect.x+bmpWidth+10, rect.y+(rect.height - textHeight)/4)

        if not self.description:
            return
        
        dc.SetFont(self.smallerFont)

        textWidth, textHeight = dc.GetTextExtent(self.description)
        dc.SetTextForeground(self.greyColour)
        dc.DrawText(self.description, rect.x+bmpWidth+10, rect.y+3*(rect.height - textHeight)/4)
        

    def GetLineHeight(self):
        dc = wx.MemoryDC()
        dc.SelectObject(wx.EmptyBitmap(100, 20))
        
        if self.icon != None :
            bmpWidth, bmpHeight = self.icon.GetWidth(), self.icon.GetHeight()
        else :
            bmpWidth, bmpHeight = TAILLE_IMAGE
        
        dc.SetFont(self.normalFont)
        
        textWidth, textHeight = dc.GetTextExtent(self.text)

        dc.SetFont(self.smallerFont)
        textWidth, textHeight = dc.GetTextExtent(self.description)

        dc.SelectObject(wx.NullBitmap)
        
        return max(2*textHeight, bmpHeight) + 20
    

    def GetSubItemWidth(self):
        return 250
    


class SecondColumnRenderer(object):
    def __init__(self, parent, dateModif=None, taille=None):
        self.parent = parent
        self.date = dateModif
        self.size = taille
        
        self.smallerFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.greyColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
                

    def DrawSubItem(self, dc, rect, line, highlighted, enabled):
        """Draw a custom progress bar using double buffering to prevent flicker"""
        dc.SetFont(self.smallerFont)
        
        if self.date != None :
            dummy1, dummy2= dc.GetTextExtent(_(u"Date modif.: "))
            textWidth, textHeight = dc.GetTextExtent(self.date)
            dc.SetTextForeground(self.greyColour)
            dc.DrawText("Date modif.: ", rect.x+5, rect.y+(rect.height - textHeight)/4)
            dc.SetTextForeground(wx.BLACK)
            dc.DrawText(self.date, rect.x+dummy1+5, rect.y+(rect.height - textHeight)/4)
        else :
            textWidth, textHeight = 0, 0

        if self.size :
            dummy1, dummy2= dc.GetTextExtent("Taille: ")
            dc.SetTextForeground(self.greyColour)
            dc.DrawText("Taille: ", rect.x+5, rect.y+3*(rect.height - textHeight)/4)
            dc.SetTextForeground(wx.BLACK)
            dc.DrawText(self.size, rect.x+dummy1+5, rect.y+3*(rect.height - textHeight)/4)
        

    def GetLineHeight(self):
        dc = wx.MemoryDC()
        dc.SelectObject(wx.EmptyBitmap(100, 20))
        textWidth, textHeight, d1, d2 = dc.GetFullTextExtent("xx", self.smallerFont)
        dc.SelectObject(wx.NullBitmap)
        return 2*textHeight + 20
    

    def GetSubItemWidth(self):
        dc = wx.MemoryDC()
        dc.SelectObject(wx.EmptyBitmap(100, 20))
        
        if self.date != None :
            texte = _(u"Date modif.:") + self.date
        else :
            texte = "Taille : 888.88 MB"
        textWidth, textHeight, d1, d2 = dc.GetFullTextExtent(texte, self.smallerFont)
        dc.SelectObject(wx.NullBitmap)
        return textWidth+10
    
        
        
        
        
class CTRL(ULC.UltimateListCtrl):
    def __init__(self, parent, prefixe=None, details=True, mode="local", codesReseau=None):
        ULC.UltimateListCtrl.__init__(self, parent, -1, style=wx.BORDER_THEME, agwStyle=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.prefixe = prefixe
        self.details = details
        self.mode = mode
        self.codesReseau = codesReseau
        
        self.EnableSelectionVista()
        self.Remplissage()
    
    def SetMode(self, mode="local", codesReseau=None):
        self.mode = mode
        self.codesReseau = codesReseau
        self.Remplissage() 

    def Remplissage(self):
        """ Remplissage du contrôle """
        wx.BeginBusyCursor()
        self.Freeze()
        
        self.ClearAll()
        if self.mode == "local" :
            self.listeFichiers = self.GetListeFichiersLocal() 
        else :
            self.listeFichiers = self.GetListeFichiersReseau() 

        self.InsertColumn(0, "Column 1") 
        self.InsertColumn(1, "Column 2") 
        
        for dictFichier in self.listeFichiers :
            index = self.InsertStringItem(sys.maxint, "")

            klass = FirstColumnRenderer(self, titre=dictFichier["titre"], image=dictFichier["image"], description=dictFichier["description"])
            self.SetItemCustomRenderer(index, 0, klass)
            
            if self.details == True and self.mode != "reseau" :
                self.SetStringItem(index, 1, "")
                klass = SecondColumnRenderer(self, dateModif=dictFichier["dateModif"], taille=dictFichier["taille"])
                self.SetItemCustomRenderer(index, 1, klass)
            
            self.SetItemPyData(index, dictFichier)

        self.SetColumnWidth(0, ULC.ULC_AUTOSIZE_FILL)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        self.Thaw()
        self.SendSizeEvent()
        wx.EndBusyCursor()
    
    def GetListeFichiersLocal(self) :
        """ Récupère la liste des fichiers locaux à afficher """
        # Lit le répertoire
        chemin = UTILS_Fichiers.GetRepData()
        fichiers = os.listdir(chemin)
        fichiers.sort()
        
        listeFichiers = []
        for fichier in fichiers :
            nomFichier = os.path.split(fichier)[1]
            titre = nomFichier[:-9]
            cheminFichier = chemin + "/" + fichier
            
            if (self.prefixe == None and nomFichier.endswith("_DATA.dat")) or (self.prefixe != None and nomFichier.endswith("_DATA.dat") and nomFichier.startswith(self.prefixe)) :
            
                # Taille des 3 bases de données
                taille = 0
                for suffixe in ("DATA", "DOCUMENTS", "PHOTOS") :
                    fichierTemp = u"%s/%s_%s.dat" % (chemin, titre, suffixe)
                    if os.path.isfile(fichierTemp) :
                        taille += os.path.getsize(fichierTemp)
                taille = FormatFileSize(taille)
                
                # Date dernière modification
                t = os.path.getmtime(cheminFichier)
                date = datetime.datetime.fromtimestamp(t)
                dateModif = date.strftime("%d/%m/%Y %H:%M")
                
                # Ouverture de la base de données pour récupérer les infos sur le fichier
                logo = None
                description = u""
                try :
                    connexion = sqlite3.connect(cheminFichier.encode('utf-8'))
                    cursor = connexion.cursor()
                    req = "SELECT nom, logo FROM organisateur WHERE IDorganisateur=1;"
                    cursor.execute(req)
                    description, logo = cursor.fetchone()
                    connexion.close()
                except :
                    pass

                if logo != None :
                    io = cStringIO.StringIO(logo)
                    img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
                    img = RecadreImg(img)
                    image = img.ConvertToBitmap()
                else :
                    image = None

                # Mémorisation
                listeFichiers.append({"titre" : titre, "image" : image, "description" : description, "taille" : taille, "dateModif" : dateModif})
        
        return listeFichiers
    
    def TestConnexionReseau(self):
        hote = self.codesReseau["hote"]
        utilisateur = self.codesReseau["utilisateur"]
        motdepasse = self.codesReseau["motdepasse"]
        port = self.codesReseau["port"]

        DB = GestionDB.DB(nomFichier=u"%s;%s;%s;%s[RESEAU]" % (port, hote, utilisateur, motdepasse))
        if DB.echec == 1 :
            DB.Close()
            return DB.erreur
        DB.Close()
        return True
    
##        try :
##            connexion = MySQLdb.connect(host=hote, user=utilisateur, passwd=motdepasse, port=int(port), use_unicode=True) 
##            connexion.set_character_set('utf8')
##            cursor = connexion.cursor()
##            connexion.close()
##        except Exception, err :
##            return err
##        return True

    def GetListeFichiersReseau(self) :
        """ Récupère la liste des fichiers réseau à afficher """
        listeFichiers = []
        
        # Connexion au réseau MySQL
        hote = self.codesReseau["hote"]
        utilisateur = self.codesReseau["utilisateur"]
        motdepasse = self.codesReseau["motdepasse"]
        port = self.codesReseau["port"]
        
        if hote == "" or utilisateur == "" :
            return listeFichiers
        
        DB = GestionDB.DB(nomFichier=u"%s;%s;%s;%s[RESEAU]" % (port, hote, utilisateur, motdepasse))
        if DB.echec == 1 :
            DB.Close()
            return listeFichiers
        
        # Test de connexion à une base de données
        listeDatabases = []
        DB.ExecuterReq("SHOW DATABASES;")
        listeValeurs = DB.ResultatReq()
        for valeurs in listeValeurs :
            listeDatabases.append(valeurs[0])
        
        # Récupération des infos
        for nomFichier in listeDatabases :
            if (self.prefixe == None and nomFichier.endswith("_data")) or (self.prefixe != None and nomFichier.endswith("_data") and nomFichier.startswith(self.prefixe)) :
                
                titre = nomFichier[:-5]
                
                # Taille des 3 bases de données
                taille = 0
##                for suffixe in ("data", "documents", "photos") :
##                    base = u"%s_%s" % (titre, suffixe)
##                    try :
##                        cursor.execute("""SELECT table_schema, sum( data_length + index_length) /1024 FROM information_schema.TABLES WHERE table_schema = "%s";""" % base) 
##                        nom, tailleBase = cursor.fetchone()
##                        taille += tailleBase
##                    except :
##                        pass
                taille = FormatFileSize(float(taille))
                
                # Date de dernière modification
                dateModif = None
                
                # Ouverture de la base de données pour récupérer les infos sur le fichier
                nom = u""
                logo = None
                description = u""
                try :
                    DB.ExecuterReq("""USE %s_data;""" % titre)
                    DB.ExecuterReq("""SELECT nom, logo FROM organisateur WHERE IDorganisateur=1;""")
                    description, logo = DB.ResultatReq()[0]
                except :
                    pass

                if logo != None :
                    io = cStringIO.StringIO(logo)
                    img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
                    img = RecadreImg(img)
                    image = img.ConvertToBitmap()
                else :
                    image = None

                # Mémorisation
                listeFichiers.append({"titre" : titre, "image" : None, "image" : image, "description" : description, "taille" : taille, "dateModif" : dateModif})

        # Fermeture connexion
        DB.Close()
        
        return listeFichiers
    
    def ModifierFichier(self, titre=""):
        """ Modifier un fichier """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_fichier", "modifier") == False : return
        
        if self.mode == "reseau" :
            dlg = wx.MessageDialog(self, _(u"Il est impossible de modifier le nom d'un fichier réseau !"), _(u"Désolé"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation 1
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment modifier le nom du fichier '%s' ?") % titre.decode("iso-8859-15"), _(u"Modifier un fichier"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        
        # Demande le nouveau nom du fichier
        dlg = wx.TextEntryDialog(self, _(u"Saisissez un nouveau nom pour le fichier '%s' :") % titre.decode("iso-8859-15"), _(u"Modifier le nom"), titre)
        if dlg.ShowModal() == wx.ID_OK:
            nouveauTitre = dlg.GetValue()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        if nouveauTitre == "" :
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation 2
        dlg = wx.MessageDialog(None, _(u"Vous êtes vraiment sûr de vouloir changer le nom du fichier '%s' en '%s' ?") % (titre, nouveauTitre), _(u"Modifier un fichier"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        
        # Modifier un fichier local
        for suffixe in ("DATA", "DOCUMENTS", "PHOTOS") :
            try :
                source = UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (titre, suffixe))
                destination = UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (nouveauTitre, suffixe))
                os.rename(source, destination)
            except Exception, err :
                print "Erreur dans le renommage de fichier : " + err
        self.Remplissage() 
        

    def SupprimerFichier(self, titre=""):
        """ Supprimer un fichier """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_fichier", "supprimer") == False : return
        
        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment supprimer le fichier '%s' ?") % titre.decode("iso-8859-15"), _(u"Supprimer un fichier"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        
        dlg = wx.MessageDialog(None, _(u"Attention, la suppression est irreversible !!! \n\n Vous êtes vraiment sûr de vouloir supprimer le fichier '%s' ?") % titre.decode("iso-8859-15"), _(u"Supprimer un fichier"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        
        # Supprimer un fichier local
        if self.mode == "local" :
            for suffixe in ("DATA", "DOCUMENTS", "PHOTOS") :
                try :
                    os.remove(UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (titre, suffixe)))
                except Exception, err :
                    pass
        
        # Supprime un fichier réseau
        if self.mode == "reseau" :
            hote = self.codesReseau["hote"]
            utilisateur = self.codesReseau["utilisateur"]
            motdepasse = self.codesReseau["motdepasse"]
            port = self.codesReseau["port"]

            DB = GestionDB.DB(nomFichier=u"%s;%s;%s;%s[RESEAU]" % (port, hote, utilisateur, motdepasse))
            if DB.echec == 1 :
                dlg = wx.MessageDialog(self, _(u"Erreur de connexion MySQL !\n\n%s") % DB.erreur, _(u"Erreur de connexion"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            for suffixe in ("data", "documents", "photos") :
                DB.ExecuterReq("""DROP DATABASE IF EXISTS %s_%s;""" % (titre, suffixe))
                
            DB.Close()
        
        self.Remplissage() 
        
        
# ----------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl = CTRL(panel, prefixe="", details=True, mode="local", codesReseau={}) # Test mode local
##        self.ctrl = CTRL(panel, prefixe="", details=True, mode="reseau", codesReseau={"port":3306, "hote" : "locahost", "utilisateur" : "root", "motdepasse" : "XXXX"}) # Test mode réseau
        self.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.OnSelection, self.ctrl)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
    
    def OnSelection(self, event):
        index = self.ctrl.GetFirstSelected()
        print self.ctrl.GetItemPyData(index)
        
        

if __name__ == '__main__':
    app = wx.App(0)
    frame_1 = MyFrame(None, -1, "TEST", size=(600, 600))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()