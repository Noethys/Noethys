Noethys
==================
Logiciel de gestion libre et gratuit de gestion multi-activités pour 
les accueils de loisirs, crèches, garderies périscolaires, cantines, 
TAP ou NAP, clubs sportifs et culturels...

Plus d'infos sur www.noethys.com


Procédure d'installation
------------------

Si vous souhaitez installer manuellement Noethys sur
Windows, Mac OS ou Linux, il vous suffit de copier
l'intégralité du répertoire sur votre disque dur et
d'installer toutes les dépendances listées ci-dessous.


Dépendances pour Windows
------------------
Sur Windows, vous devez aller sur les sites des auteurs pour 
rechercher et installer les bibliothèques suivantes.

- Python 2.7 (http://www.python.org/)
- wxPython 3.0 - version unicode (http://www.wxpython.org/)
- dateutil (http://pypi.python.org/pypi/python-dateutil)
- MySQLdb (http://sourceforge.net/projects/mysql-python/)
- NumPy (http://new.scipy.org/download.html)
- PIL (http://www.pythonware.com/products/pil/)
- PyCrypto (https://www.dlitz.net/software/pycrypto/)
- PyCrypt (https://sites.google.com/site/reachmeweb/pycrypt)
- ReportLab (http://www.reportlab.com/software/opensource/rl-toolkit/download/)
- MatPlotLib (http://matplotlib.sourceforge.net/)
- ObjectListView (http://objectlistview.sourceforge.net/python/)
- pyExcelerator (http://sourceforge.net/projects/pyexcelerator/)
- videoCapture (http://videocapture.sourceforge.net/)
- Pyttsx (http://pypi.python.org/pypi/pyttsx)
- Appdirs (https://pypi.python.org/pypi/appdirs)
- Psutil (https://pypi.python.org/pypi/psutil)
- Paramiko (https://pypi.python.org/pypi/paramiko)
- Lxml (https://pypi.python.org/pypi/lxml)


Dépendances pour Linux
------------------


- python 2.7 (Installé en principe par défaut sous ubuntu)
- python-wxgtk3.0 (Bibliothèque graphique wxPython)
- python-mysqldb (Pour l'utilisation en mode réseau)
- python-dateutil (Manipulation des dates)
- python-numpy (Calculs avancés)
- python-pil (Traitement des photos)
- python-reportlab (Création des PDF)
- python-matplotlib (Création de graphes)
- python-xlrd (Traitement de fichiers Excel)
- python-crypto (pour crypter les sauvegardes)
- python-excelerator (pour les exports format excel)
- python-pyscard (pour pouvoir configurer les procédures de badgeage)
- python-opencv (pour la détection automatique des visages)
- python-pip (qui permet d'installer pyttsx et icalendar)
- python-espeak (pour la synthèse vocale, associé à pyttsx)
- python-appdirs (pour rechercher les répertoires de stockage des données)
- python-psutil (infos système)
- python-paramiko (Prise en charge SSH)
- python-lxml (Validation XSD des bordereaux PES)

Ils s'installent depuis le terminal tout simplement avec la commande (**à exécuter si besoin avec sudo**):

```
apt-get install python-mysqldb python-dateutil python-numpy python-pil python-reportlab python-matplotlib 
python-xlrd python-excelerator python-pip python-espeak python-pyscard python-opencv python-crypto python-appdirs
python-wxgtk3.0 python-sqlalchemy libcanberra-gtk-module python-psutil python-paramiko python-lxml
```

Et pour pyttsx et icalendar il faut avoir installé python-pip (ce qui a ét fait dans l'étape précédente) et les installer par:
```
pip install pyttsx
pip install icalendar
```


Pour lancer Noethys, lancez le terminal de Linux, placez-vous dans le répertoire d'installation de Noethys, puis saisissez la commande "python Noethys.py"



- - - -



## Obsolète: instructions à suivre uniquement sur d'anciennes versions de debian ou ubuntu ##

Dans le cas où votre version de debian ou d'ubuntu ne proposerait pas python-wxgtk3.0 (ce qui est le cas pour ubuntu LTS 14.04 et toute distribution basée sur cette version), la commande précédente retourne une erreur.

Exécutez alors la commande suivante:
```
apt-get install python-wxgtk2.8 libjpeg62 libwxgtk3.0-0
```

Puis téléchargez les paquets de la bibliothèque graphique correspondant à votre architecture (32 ou 64 bits), wxpython et wxwidgets, ainsi que libtiff4.

Vous trouverez ces fichiers sur le site de Noethys : **Menu Assistance > Ressources communautaires > Liste des ressources > Divers**.

Puis exécutez la commande suivante:
```
dpkg -i dossier/wxwidget*****.deb dossier/wxpython*****.deb dossier/libtiff4*****.deb
```

**dossier**: le dossier dans lequel vous avez téléchargé la bibliothèque
**wxwidget\*****.deb, wxpython\*****.deb et libtiff4\*****.deb** sont les fichiers correspondant à votre architecture que vous avez téléchargés.

**Vérifiez que vous avez choisi la version correspondant à votre architecture (32 ou 64 bits).**



