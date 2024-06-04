
Vážená komise, dnes bych vám rád představil výsledky mé bakalářské práce.

(důrazně, pomalu) V tomto projektu jsem se zabýval návrhem komunikačního modulu s rozhraním LoRa a výrobou senzoru vlhkosti půdy postaveném na tomto modulu.

Cílem práce bylo navrhnout pilotní řešení problému cenově dostupného distribuovaného měření vlhkosti půdy na určitém území tak, aby to obnášelo minimální lidský zásah. Řešení je založeno na technologii LoRa pro svoji nízkou spotřebu a vysoký dosah. Řešení též počítá s možností budoucího rozšíření sítě.

Jak jsem již zmínil, pro komunikaci mezi senzory a stanicí je použita LoRa. LoRa je způsob modulace, který je navržen pro vysoký dosah a dobrou penetraci prostředí při minimálním výkonu. Rozhodl jsem se nevyužívat komerčně dostupných poskytovatelů LoRaWAN sítě pro její nízké pokrytí v odlehlých oblastech a dlouhodobé náklady s ní spojené.

Požadavek samostatnosti v kombinaci se zamýšleným prostředím nasazení, tedy potenciálně odlehlé oblasti bez infrastruktury, vyžaduje aby byly senzory napájeny nezávislým zdrojem energie. Zde se jako jediná možnost nabízí solární energie. (pauza) V dnešní době je možnost vzdálené aktualizace firmware nedílnou součástí mnohých zařízení. Aktualizace by v tomto případě mohly přinést senzorům podporu meshingu, vylepšit jejich výdrž a přesnost měření. Tato funkce není běžná pro uzly LoRa sítí, projekt je v tomto ohledu inovativní.

Senzor je postaven na plošném spoji, který integruje zmíněný komunikační modul LoRa a měřící obvody. (pauza) Vlhkost snímají 4 kapacitní plochy, které jsou zasunuty v zemi. (pauza) Mimo měřící obvody senzor obsahuje obvody ochrany baterie a dva teploměry. Jeden je umístěn na špičce senzoru v největší hloubce a druhý je těsně nad zemí.

Senzor měří kapacitu na základě časové konstanty RC obvodu, zde můžeme vidět zjednodušené schema zapojení. (pauza) Neznámý kapacitor C_X je nejprve vybíjen rezistorem R_DIS a poté připojen k referenci skrze rezistor R_CHG dokud napětí na svorkách kapacitoru C_X nedosáhne mezní hodnoty určené napěťovým děličem.

Aby byla elektronika ochráněna a bylo možné připevnit solární panel a anténu, navrhl jsem a vytiskl třídílný kryt, který se nasune na horní část senzoru. Pro finální nasazení by senzor byl vyroben z 3.2 plošného spoje pro větší pevnost a horní část by byla vylita zalévacím tmelem.

Modul, který jsem v rámci této práce navrhl a vyrobil, slouží jako dobrá platforma pro široké spektrum dalších senzorů a smart aplikací. Modul je založen na STM32WLE, což je MCU, které kombinuje LoRa rádio s STM32L4 v jednom pouzdru. Tato volba byla ideální, jelikož dovolila velmi hustou míru integrace, výsledný modul zaujímá pouze 500 mm^2.

I při zachování takto malých rozměrů se mi podařilo dosáhnout stabilního přenosu na více než kilometr v členitém terénu, což předčilo má očekávání.
