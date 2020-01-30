# Memestagram

- Jim Nuchelmans, Juriaan Wagenaar & Tommy van de Logt


 ![](https://github.com/Jimnuch99/project/blob/master/docs/login.jpg)


 ![](https://github.com/Jimnuch99/project/blob/master/docs/feed.jpg)


## Handleiding

Zodra u bent ingelogd op de website zult u op de feed pagina komen. Dit is de centrale plek waarop alle memes van alle gebruikers worden weergegeven. In de menubalk links op de website ziet u de verschillende opties die de website te bieden heeft. Op zich spreekt alles voor zich. Om u beter op weg te helpen wordt hieronder uitgelegd wat de verschillende functies doen en hoe ze tot stand zijn gekomen.


* repository


In de repository staan de mappen static en templates. In static kunt u de afbeeldingen vinden die gebruikt zijn tijdens het maken van de site. Ook de css bestanden zijn te vinden in de static map. In templates staan alle html templates die we gemaakt hebben.

Buiten deze mappen is het bestand meme.db belangrijk. Hierin staan de tabellen die gebruikt worden voor de website.


## Features/taakverdeling

- taakverdeling


Jim en Tommy hebben zich meer gericht op het python gedeelte en het schrijven van de routes. Ook zijn er python delen waar we alle drie aan gewerkt hebben. Jim heeft zich hierbij vooral gericht op het implementeren van de API key en de sql queries.

Juriaan en Tommy hebben het meeste bijgedragen aan het html gedeelte.



* login


Een functie om in te loggen. Gebruikersnaam en wachtwoord worden gecontroleerd en bij juiste invoering gaat een gebruiker door naar de feed pagina


* register


Registreer functie, minstens 8 tekens een speciaal teken en een cijfer zijn nodig voor gebruikersnaam en wachtwoord


* upload


Via een giffy api is het mogelijk om op de site een zoekterm in te typen. Dit geeft resultaten weer van de site giffy.com die gebruikers hierna kunnen posten op de feed.


* feed


Op de feedworden alle geplaatste memes weergegeven. Dit is dus een verzameling van alle memes van alle gebruikers. Deze worden opgeslagen in de database. Hiervoor is de tabel memes gemaakt.


* account


Op het account kan een ingelogde gebruiker de memes zien die hij zelf gepost heeft. Dit wordt gedaan met behulp van de memes tabel in de database. In die tabel staan namelijk de user ID en de url van de giffy. Zo worden per gebruiker de memes weergegeven die hij of zij geplaatst heeft.


* search


Door de zoekterm te vergelijken met de gebruikersnamen in de database worden gebruikers weergegeven die dezelfde volgorde in letters bevatten als de zoekterm. Dit gebeurt met behulp van de functie search_term. Op deze manier kan een gebruiker zien welke gebruiksernamen al bezet zijn en of er misschien leuke originele namen tussen zitten.


* saved memes


Op de feed is een button gemaakt onder elke post die doorverbindt naar de route save meme. Saved memes gaat er om dat gebruikers een verzameling kunnen maken met memes die zij vaker willen bekijken. Voor saved memes is ook een nieuwe tabel gemaakt waarin per gebruiker de memes worden geplaatst die een gebruiker heeft opgeslagen. Zo is er per gebruiker een pagina met een persoonlijk gecreëerde verzameling van memes.


* follow/personal feed


Met een follow button kan een gebruiker een andere gebruiker volgen waarvan hij een meme ziet op de feed pagina. Alle memes die verbonden zijn aan de user_id van degene die gevolgd wordt worden nu opgeslagen in een nieuwe tabel followedusers. Met behulp van Flash wordt er een foutmelding gegeven als een gebruiker twee keer dezelfde gebruiker probeert te volgen. Ook als de gebruiker zichzelf probeert te volgen komt er een foutmelding met behulp van Flash. Alle memes van de gevolgde gebruiker worden nu weergegeven op de pagina personal feed. Op deze manier heeft elke gebruiker ook een feed waar alleen de memes komen te staan van gebruikers die hij/zij volgt.


* unfollow


De unfollow functie is gemaakt om ervoor te zorgen dat als een gebruiker de memes van een andere gebruiker toch niet zo leuk vond als hij dacht, hij deze gebruiker weer kan ontvolgen. Met behulp van een button unfollow die verbonden is met de route unfollowUser kan een gevolgde gebruiker weer verwijdert worden uit de tabel followedusers.


* logout


Door de hele session te ‘clearen’ ga je terug naar het register scherm. Dit is handig voor als iemand toevallig heeft ingelogd met het verkeerde account.


## Helpers


- login_required


## Hulpbronnen

- Giffy API

