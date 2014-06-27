#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os
import sys


def AdaptePolice(ctrl):
    """ Adapte la taille de la police du ctrl donné """
    taille = 8
    if "linux" in sys.platform :
        ft = ctrl.GetFont()
        ft.SetPointSize(taille)
        ctrl.SetFont(ft)


def AdaptationsDemarrage():
    """ Adaptations au démarrage de Noethys """
    # Vérifie que le chemin est ok
    os.chdir(sys.path[0])
    # Vérifie que les répertoires vides sont bien là
    for rep in ("Temp", "Updates", "Aide") :
        if os.path.isdir(rep) == False :
            os.remove(rep)
            try :
                os.mkdir(rep)
            except Exception, err:
                pass


if __name__ == "__main__":
    AdaptationsDemarrage()