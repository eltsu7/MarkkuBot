# MarkkuBot

TT-kameroiden virtuaalinen maskotti.

## MongoDB

Nykyinen Mongo-setti ei ole kovin tietoturvallinen, mutta defaulttina ei myöskään salli ulkopuolisia yhteyksiä vaan pelkät localhost-yhteydet.

### Uuden MongoDB:n pystytys

* Asenna MongoDB 4.0.0 (stable): https://docs.mongodb.com/manual/installation/#tutorials
* Varmista, että voit ajaa `mongod` komennon termiksestä.
* Asenna python-riippuvuudet. Kehitysympäristössä voi olla fiksua luoda virtuaaliympäristö esim. `virtualenv`-komennolla riippuvuuksia varten.
* Käynnistä Mongo-serveri `mongod`-komennolla. Serverille voi määrittää tietokannan sijainnin, defaulttina `/data/db` mutta db:n voi laittaa vaikka projektikansioon:
```
mongod --dbpath <projektikansion polku>/db
```
* Laita Markku päälle. Markku yhdistää Mongoon Mongon default-portin `localhost:27017` kautta.
* Mongon tietokannan ja collectionin nimet haetaan `settings.json`:ista.
* Tietokantaa voi tökkiä termiksestä ajamalla `mongo`. Komento yhdistää default-asetuksilla pystytettyyn kantaan ja avaa Mongon oman konsolin termiksen sisälle.

### Yleistä infoa Mongo-toteutuksesta

Esimerkki MongoDB-dokumentista löytyy `data-template.json`:sta. Tämän mallin toteutumista
ei kuitenkaan valvota koodissa, joten ole skarppina datan tallennusoperaatioissa

## Uuden Markun pystytys

* Nimeä `settings-template.json` -> `settings.json` ja päivitä asetukset
* Asenna MongoDB ja varmista, että se pyörähtää koneella. Markku ei ole vastuussa Mongon käynnistämisestä, vaan tietokannan tulee olla käynnissä Markun käynnistyessä.
* Asenna python-rippuvuudet `requirements.txt`:n avulla

## Huomattavaa

Tyhjän data.jsonin pitää olla muodossa '{}'