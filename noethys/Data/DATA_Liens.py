#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


DICT_TYPES_LIENS = {
    1 : { "M" : u"p�re", "F" : u"m�re", "public" : "A", "lien" : 2, "type" : "parent", "texte" : { "M" : u"est son p�re", "F" : u"est sa m�re"} },
    2 : { "M" : u"fils", "F" : u"fille", "public" : "E", "lien" : 1, "type" : "enfant", "texte" : { "M" : u"est son fils", "F" : u"est sa fille"} },
    
    3 : { "M" : u"fr�re", "F" : u"soeur", "public" : "AE", "lien" : 3, "type" : None, "texte" : { "M" : u"est son fr�re", "F" : u"est sa soeur"} },
    
    4 : { "M" : u"grand-p�re", "F" : u"grand-m�re", "public" : "A", "lien" : 5, "type" : None, "texte" : { "M" : u"est son grand-p�re", "F" : u"est sa grand-m�re"} },
    5 : { "M" : u"petit-fils", "F" : u"petite-fille", "public" : "E", "lien" : 4, "type" : None, "texte" : { "M" : u"est son petit-fils", "F" : u"est sa petite-fille"} },
    
    6 : { "M" : u"oncle", "F" : u"tante", "public" : "A", "lien" : 7, "type" : None, "texte" : { "M" : u"est son oncle", "F" : u"est sa tante"} },
    7 : { "M" : u"neveu", "F" : u"ni�ce", "public" : "E", "lien" : 6, "type" : None, "texte" : { "M" : u"est son neveu", "F" : u"est sa ni�ce"} },
    
##    8 : { "M" : u"parrain", "F" : u"marraine", "public" : "AE", "lien" : 9 },
##    9 : { "M" : u"filleul", "F" : u"filleule", "public" : "AE", "lien" : 8 },
    
    10 : { "M" : u"mari", "F" : u"femme", "public" : "A", "lien" : 10, "type" : "couple", "texte" : { "M" : u"est son mari", "F" : u"est sa femme"} },
    
    11 : { "M" : u"concubin", "F" : u"concubine", "public" : "A", "lien" : 11, "type" : "couple", "texte" : { "M" : u"est son concubin", "F" : u"est sa concubine"} },
    
    12 : { "M" : u"veuf", "F" : u"veuve", "public" : "A", "lien" : 12, "type" : "couple", "texte" : { "M" : u"est son veuf", "F" : u"est sa veuve"}},

    13 : { "M" : u"beau-p�re", "F" : u"belle-m�re", "public" : "A", "lien" : 14, "type" : None, "texte" : { "M" : u"est son beau-p�re", "F" : u"est sa belle-m�re"} },
    14 : { "M" : u"beau-fils", "F" : u"belle-fille", "public" : "E", "lien" : 13, "type" : None, "texte" : { "M" : u"est son beau-fils", "F" : u"est sa belle-fille"} },    
    
    15 : { "M" : u"pacs�", "F" : u"pacs�e", "public" : "A", "lien" : 15, "type" : "couple", "texte" : { "M" : u"est son pacs�", "F" : u"est sa pacs�e"} },
    
    16 : { "M" : u"ex-mari", "F" : u"ex-femme", "public" : "A", "lien" : 16, "type" : "ex-couple", "texte" : { "M" : u"est son ex-mari", "F" : u"est son ex-femme"} },
    
    17 : { "M" : u"ex-concubin", "F" : u"ex-concubine", "public" : "A", "lien" : 17, "type" : "ex-couple", "texte" : { "M" : u"est son ex-concubin", "F" : u"est son ex-concubine"} },
    
    18 : { "M" : u"tuteur", "F" : u"tutrice", "public" : "A", "lien" : 19, "type" : None, "texte" : { "M" : u"est son tuteur", "F" : u"est sa tutrice"} },
    19 : { "M" : u"sous sa tutelle", "F" : u"sous sa tutelle", "public" : "E", "lien" : 18, "type" : None, "texte" : { "M" : u"est sous sa tutelle", "F" : u"est sous sa tutelle"} },

    20: {"M": u"assistant maternel", "F": u"assistante maternelle", "public": "A", "lien": 21, "type": None, "texte": {"M": u"est son assistant maternel", "F": u"est son assistante maternelle"}},
    21: {"M": u"sous sa garde", "F": u"sous sa garde", "public": "E", "lien": 20, "type": None, "texte": {"M": u"est sous sa garde", "F": u"est sous sa garde"}},

    22: {"M": u"ami", "F": u"amie", "public": "AE", "lien": 22, "type": None, "texte": {"M": u"est son ami", "F": u"est son amie"}},

    23: {"M": u"voisin", "F": u"voisine", "public": "AE", "lien": 23, "type": None, "texte": {"M": u"est son voisin", "F": u"est sa voisine"}},

    24: {"M": u"assistant familial", "F": u"assistante familiale", "public": "A", "lien": 25, "type": None, "texte": {"M": u"est son assistant familial", "F": u"est son assistante familiale"}},
    25: {"M": u"sous sa garde", "F": u"sous sa garde", "public": "E", "lien": 24, "type": None, "texte": {"M": u"est sous sa garde", "F": u"est sous sa garde"}},

}


DICT_AUTORISATIONS = {
    1 : { "M" : u"Responsable l�gal", "F" : u"Responsable l�gale", "img" : "Responsable_legal.png"},
    2 : { "M" : u"Contacter en cas d'urgence", "F" : u"Contacter en cas d'urgence", "img" : "Telephone.png"},
    3 : { "M" : u"Raccompagnement autoris�", "F" : u"Raccompagnement autoris�", "img" : "Sortir.png"},
    4 : { "M" : u"Raccompagnement interdit", "F" : u"Raccompagnement interdit", "img" : "Interdit2.png"},
    }

