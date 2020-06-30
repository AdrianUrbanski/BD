Adrian Urbański

Projekt pisałem na Debianie.
Używałem pakietów:
 - __Python 3.8.3__
 - __PostGIS 2.5.1__
 - __PostgreSQL 12.3__
 
Do uruchomienia programu powinien wystarczyć moduł
__psycopg2 2.8.5__, który można zainstalować poleceniem  
_python3 -m pip install psycopg2-binary~=2.8.5_

Ja korzystałem z wirtualnego środowiska Pythona, aby je
utworzyć wydałem następujące polecenia w katalogu projektu:
- _python3 -m pip install virtualenv_
- _python3 -m virtualenv .venv_
- _source .venv/bin/activate_
- _pip install -r requirements.txt_

Teraz można uruchamiać program poleceniem  
_python(3) app.py [--init]_

Zrealizowałem wszystkie części projektu z opisu punktacji.

Model konceptualny zrealizowałem w formie diagramu E-R,
znajduje się on w pliku ERD.png.
