
Vážená komise, dnes bych vám rád představil výsledky mé bakalářské práce.

V rámci této práce jsem navrhl a vyrobil senzor vlhkosti půdy, který využívá bezdrátové rozhraní LoRa. Dovolte mi Vás hned na úvod vtáhnout do děje. Pokud si naskenujete tento QR kód, nebo vyhledáte odkaz, který bude po celou dobu prezentace v záhlaví, dostanete se na stránku, kde uvidíte živě data z tohoto senzoru před vámi.

Primární motivací této bakalářské práce byl můj osobní projekt, ve kterém jsem potřeboval komunikační LoRa modul se specifickými požadavky. Z komerčně dostupných součástek žádná tyto požadavky nesplňovala. Konkrétně potřebuji platformu, kolem které se jednoduše staví aplikace, má pro ně dostatečné prostředky, má velmi nízkou spotřebu a je ideálně postavena na STM32.

Poté už stačilo pouze najít použití takového modulu, které by dobře demonstrovala jeho schopnosti, což nás přivádí k tématu této bakalářské práce. Ta se skládá ze tří dílčích částí. První je modul samotný, tedy jeho specifikace, návrh a oživení, druhý je problematika měření vlhkosti půdy a návrh řešení a třetí je spojení těchto dílčí částí v minimum-viable-product, který je možné dlouhodobě udržovat a dále vylepšovat.

Nyní se pojďme podívat jak se tyto cíle podařilo naplnit. Začal jsem kompilací požadavků na základě typických aplikací, včetně právě aplikace senzoru vlhkosti půdy. Na základě toho vznikl seznam požadavků, zde mám jeho zkrácenou verzi, která je uvedena v bakalářské práci. V zásadě jde pouze o upřesnění toho, o čem jsem hovořil v motivaci a budu se k těmto požadavkům vracet v průběhu prezentace.

Na základě těchto požadavků jsem začal tvořit schema v KiCADu. Zde můžeme vidět top level stránku, kde uprostřed máme blok abstrahující stm32wle. Tento mikroprocesor integruje STM32L4 a Semtech LoRa rádio v jednom pouzdře, což pomáhá naplnit cíl minimálních rozměrů modulu a jeho spotřeby. Dále jsou tam bloky paměti a bezdrátového front-endu s připojením U.FL.

Při návrhu jsem vycházel hlavně z referenčního návrhu od firmy ST, který nejlépe odpovídal mým požadavkům a ze schemat Nuclea, na kterém jsem i testoval firmware v době, kdy jsem ještě neměl svůj hardware.

Všechny požadavky kladené na modul se mi podařilo naplnit - kromě zabudované antény, protože nebylo možné zaručit funkčnost pro všechny případy nasazení modulu. Tudíž jsem se rozhodl osadit běžný U.FL konektor. Změřený vysílací výkon modulu činí 13dBm na konektoru při nastavených 15. Modul má zabudovanou 1 MB FLASH paměť, do které se odkládá firmware při aktualizaci, je postavený na 4 vrstvém PCB a i přesto se povedlo dosáhnout rozměrů 20*22 mm bez použití drahých výrobních procesů. Deska byla vyráběna u PCBWay v číně a vyšla na 500 kč v množství 5 ks, odhaduji výrobní cenu 220 kč v množstvích 100ks.

(tady by se dalo navázat s performance testováním a grafy kdyby zbyl čas)

Tímto bych rád shrnul část o LoRa modulu. Říkal jsem v úvodu, že se mi nepodařilo najít vhodný LoRa modul. Nejblíže se dostal Seeedstudio E5. Abych shrnul rozdíly, E5 je navrhnut na vysoké produkční várky, ten můj spíše na menší. Jediný rozdíl mezi nimi je absence FLASH a konektoru RF u W5. Pokud počítáte s návrhem jednoho produktu s LoRa připojením, přidat tyto dva komponenty není problém. Pokud ale chcete navrhovat desítky takových aplikací, začne být tento detail podstatný a podle mě už dává smysl navrhnout vlastní řešení.

Tento přístup nás přenese od specifické aplikace k systému na vyšší úrovni abstrakce. Na modul se potom můžeme dívat jako na hlavní řídicí člen, který obsahuje zmíněná rozhraní.

Několikrát jsem již zmínil aktualizace firmware, takže bych tomuto tématu věnoval tento slide. Logika příjmu nového obrazu firmware je zabudována v každé aplikaci skrze právě zmíněný runtime. Obraz se pro přenos musí fragmentovat na bloky, každý blok má svoje pořadové číslo a úlohou systému je přijmout a složit celý obraz na druhé straně, proto je potřeba dostatečná kapacita paměti. Způsob přenosu je inspirován selective repeat s tím, že místo jednotlivých ACK paketů jsou odesílány příjemcem status pakety, které mohou obsahovat až 32 naposledy přijatých pořadových čísel, jako potvrzení jejich přijetí. To dovoluje snížit frekvenci odesílání těchto potvrzovacích paketů.

Nyní k senzoru samotnému. 


