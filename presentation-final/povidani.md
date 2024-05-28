
Vážená komise, dnes bych vám rád představil výsledky mé bakalářské práce.

V rámci této práce jsem navrhl a vyrobil senzor vlhkosti půdy, který využívá bezdrátové rozhraní LoRa. Dovolte mi Vás hned na úvod vtáhnout do děje. Tento QR kód vas převede na webovou stránku, kde uvidíte živě data měřená senzorem před vámi. Případně využijte odkazu ze záhlaví.

Primární motivací této bakalářské práce byl můj osobní projekt, ve kterém jsem potřeboval komunikační LoRa modul se specifickými požadavky. Z komerčně dostupných součástek žádná tyto požadavky nesplňovala. Konkrétně potřebuji platformu, která bude ideálně postavena na STM32, bude mít velmi nízkou spotřebu, lze kole ní lehce stavět a bude mít dostatek prostředků pro složitější aplikace.

Poté už stačilo pouze najít použití takového modulu, které by dobře demonstrovala jeho schopnosti, což nás přivádí k tématu této bakalářské práce. Práce se zabývá třemi dílčími pod-úkoly 
- specifikace, návrh, výroba a ověření funkčnosti modulu LoRa, který podporuje tzv over the air aktualizace,
- problematika snímaní vlhkosti půdy, návrh a výroba senzoru vlhkosti půdy a
- spojení těchto dvou zařízení v minimum viable product a demonstrace jeho funkčnosti

Nyní se pojďme podívat jak se tyto cíle podařilo naplnit. Začal jsem kompilací požadavků na základě typických aplikací, včetně právě aplikace senzoru vlhkosti půdy. Na základě toho vznikl seznam požadavků na modul, který najdete v práci na straně 15, sekce 3.2.3. V zásadě jde pouze o upřesnění toho, o čem jsem hovořil v motivaci.

Na základě těchto požadavků jsem začal kreslit schema v KiCADu. Zde můžeme vidět top level stránku, kde uprostřed máme blok abstrahující stm32, blok s RF obvody a blok paměti.

Při návrhu jsem vycházel hlavně z referenčního návrhu, který nejlépe odpovídal mým požadavkům a ze schemat Nuclea, na kterém jsem i testoval firmware v době, kdy jsem ještě neměl svůj hardware.

Všechny požadavky kladené na modul se mi podařilo naplnit - kromě zabudované antény, protože nebylo možné zaručit funkčnost pro všechny případy nasazení modulu. Tudíž jsem se rozhodl osadit běžný UF.L konektor. Změřený vysílací výkon modulu činí 13dBm na konektoru při nastavených 15. Modul má zabudovanou 1 MB FLASH paměť, do které se odkládá firmware při aktualizaci, je postavený na 4 vrstvém PCB a i přesto se povedlo dosáhnout rozměrů 20*22 mm bez použití drahých výrobních procesů. Deska byla vyráběna u PCBWay v číně a vyšla na 500 kč v množství 5 ks, odhaduji výrobní cenu 220 kč v množstvích 100ks.

(tady by se dalo navázat s performance testováním a grafy kdyby zbyl čas)

Tímto bych rád shrnul část o LoRa modulu. Říkal jsem v úvodu, že se mi nepodařilo najít vhodný LoRa modul. Nejblíže se dostal Seeedstudio E5. Abych shrnul rozdíly, E5 je navrhnut na vysoké produkční várky, ten můj spíše na menší. Jediný rozdíl mezi nimi je absence FLASH a konektoru RF u W5. Pokud počítáte s návrhem jednoho produktu s LoRa připojením, přidat tyto dva komponenty není problém. Pokud ale chcete navrhovat desítky takových aplikací, začne být tento detail podstatný a podle mě už dává smysl navrhnout vlastní řešení.

Tento přístup nás přenese od specifické aplikace k systému na vyšší úrovni abstrakce. Na modul se potom můžeme dívat jako na hlavní řídicí člen, který obsahuje zmíněná rozhraní.

...

Takto pak může vypadat nasazený senzor v akci, ale to předbíhám, jelikož prvně na něj musíme nějak dostat firmware.

Říct něco o OTA, je to inspirované selective repeat... Podstatný je tento status paket, který odesílá Node. Ten místo jednoho indexu bloku může obsahovat až 32 indexů, což umožňuje snížit frekvenci odesílání těchto paketů.


