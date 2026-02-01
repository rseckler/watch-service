# Uhren Suchen Service  
  
Plane mir folgende Idee.  
  
## Art des Service  
Ich möchte einen Service, der täglich (stündlich) im Internet nach neu verfügbaren bestimmten Uhren Modellen im Graumarkt sucht. Ich möchte schnell auf neue Angebote reagieren können, um zum günstigsten Preis eine Uhr zu erwerben. Schnelligkeit ist hier wichtig. Die Angebote sollen zentral in einer Notion DB gespeichert werden.   
  
Bei jedem stündlichen Update soll überprüft werden, ob die bereits gefundenen Uhren noch verfügbar sind. Wenn nicht, soll ein Eintrag in der DB gemacht werden, dass diese verkauft wurde mit dem Datum und der Uhrzeit der Festellung.   
  
## Graumarkt sind z.B. - nicht abschließende Liste:   
Uhren Foren:  
[https://uhrforum.de/forums/angebote.11/](https://uhrforum.de/forums/angebote.11/)  
[https://forum.watchlounge.com](https://forum.watchlounge.com)  
[https://uhr-forum.org/forum/](https://uhr-forum.org/forum/)  
  
### Websites von Graumarkthändlern:  
[https://www.colognewatch.de/collections/uhren](https://www.colognewatch.de/collections/uhren)  
[https://watchvice.de](https://watchvice.de)  
Watch.de  
[https://marks-uhren.de](https://marks-uhren.de)  
[https://rothfuss-watches.de](https://rothfuss-watches.de)  
[https://karmannwatches.de](https://karmannwatches.de)  
[https://eupenfeineuhren.de](https://eupenfeineuhren.de)  
[https://www.g-abriel.de](https://www.g-abriel.de)  
[https://www.bachmann-scher.de](https://www.bachmann-scher.de/gebrauchte-luxusuhren-kaufen.html?tx_bswatches_watches%5B%40widget_0%5D%5BcurrentPage%5D=42&cHash=b5bd1bb0ebf32e2803161337d2b92f7e)  
  
Hier eine Quelle für Graunmarkthändler: [https://uhrforum.de/threads/grauhaendler-fragen-kontakte-und-informationen.293496/page-6](https://uhrforum.de/threads/grauhaendler-fragen-kontakte-und-informationen.293496/page-6)  
  
### Ebay.de  
### Kleinanzeigen.de  
### Chrono24.de  
### [https://www.chronext.de](https://www.chronext.de)  
### [https://www.uhrinstinkt.de](https://www.uhrinstinkt.de)  
   
Suche noch nach weiteren Quellen. Sowohl Foren, als auch sonstige Quellen.  
  
## Meine Idee für den Ablauf. Bitte kritisch hinterfragen.  
  
1. Anlegen in Notion einer DB mit meinen gesuchten Uhren Modellen mit folgenden Informationen.  
  
    1. Uhrenhersteller  
    2. Uhrenmodell  
    3. Referenznummer  
    4. Jahr  
    5. Länder aus denen die Uhr angeboten werden darf  
  
2. Agent sucht in den Quellen für Graumarkt Uhren (siehe Liste #Graumarktquellen) 1 x die Stunde  
	Der Agent trägt die Ergebnisse in eine weitere Notion Datenbank mit den aktuellen angebotenen Uhren ein  
  
	Die Suche soll sich nach den Informationen aus der Suchen-DB richten. Wobei der Hersteller und das Modell mindestens angegeben sein müssen.  
  
	Folgende Informationen sollen mittels des Agents und meines OpenAI Accounts ermittelt werden. Openai soll helfen, die Treffergenauigkeit zu verbessern.   
  
	- Datum des Eintrags  
	- Hersteller  
	- Modell  
	- Referenznummer  
	- Herstellungsjahr  
	- Zustand  
	- Preis  
	- Standort  
	- Link zur Uhr oder zum Angebot. Link soll direkt z.b. dein Eintrag im Forum oder auf einer Website zeigen  
	- Anbieter Name  
	- Anbieter URL  
	- Verfügbarkeit: ja oder nein  
	- Verkauft am: Datum und Uhrzeit  
  
  
## Zugänge  
Siehe unter /Users/robin/Documents/4_AI/Passwords
  
[https://uhrforum.de](https://uhrforum.de):  
User: robin@seckler.de  
Password: P@KP3BuzDoBY_mDAq-  
  
Kleinanzeigen.de:  
User: seckler@seckler.de  
Password: a3Rs@*MMw  
  
Ebay.de:  
User: smc_001  
Password: *Haus2017#  
  
## Setup  
Meine anderen Claude Clode Projekte laufen auf einem bestehendem Setup. Siehe unter /Users/robin/Documents/4_AI und den Unterordnern.  
  
  
  
  
  
  
