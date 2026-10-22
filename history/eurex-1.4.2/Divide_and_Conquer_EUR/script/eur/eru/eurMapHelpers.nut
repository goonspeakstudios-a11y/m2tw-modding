// eurMapHelpers - static campaign map data (from eurMapHelpers.lua): extra settlement seeds,
// custom battle-map assignments by coordinate, strat-model .cas paths, and standalone map props
// with their tooltips. Mostly data; onClickAtTile is a debug click logger.
// FLAG: tile/region lookups via eur_sMap.getTile / getRegion - verify accessor names.

::EUR.new_EUR_setts <- {
    ["1"]=
    {["name"]="Hobbiton",["x"]=134,["y"]=386,["castle"]=false,["level"]=0,["faction"]="turks",["culture"]="portugal",["expandAI"]="turks",["population"]="285",
    ["bu"]=
        ["green_book_shire", "dragon_inn", "hobbit", "farms",],
    ["units"]=
        ["Watch Shirriffs"],
    },
    ["2"]=
    {["name"]="Longbottom",["x"]=144,["y"]=375,["castle"]=false,["level"]=0,["faction"]="turks",["culture"]="portugal",["expandAI"]="turks",["population"]="350",
    ["bu"]=
        ["green_book_shire", "hobbit", "farms",],
    ["units"]=
        ["Watch Shirriffs"],
    },
    ["3"]=
    {["name"]="Emyn-Nu-Fuin",["x"]=322,["y"]=399,["castle"]=false,["level"]=1,["faction"]="slave",["culture"]="ireland",["expandAI"]="mongols",["population"]="550",
    ["bu"]=
        ["town_hall", "farms"],
    ["units"]=
        ["Mirkwood Bodyguard", "Dol Guldur Host", "Dol Guldur Scouts", "Dol Guldur Scouts", "Goblin Headhunters", "Goblin Headhunters", "Mirkwood Goblins", "Mirkwood Goblins"],
    },
    ["4"]=
    {["name"]="Cirith Ungol",["x"]=342,["y"]=222,["castle"]=true,["level"]=4,["faction"]="england",["culture"]="aztecs",["expandAI"]="england",["population"]="450",
    ["bu"]=
        ["c_town_hall", "garrison_quarters", "c_practice_range", "farms"],
    ["units"]=
        ["Orc Host", "Orc Host"],
    },
    ["5"]=
    {["name"]="Cerin Amroth",["x"]=260,["y"]=324,["castle"]=true,["level"]=1,["faction"]="ireland",["culture"]="ireland",["expandAI"]="ireland",["population"]="550",
    ["bu"]=
        ["c_town_hall", "farms"],
    ["units"]=
        ["Lorien Warders", "Lorien Archers"],
    },
    ["6"]=
    {["name"]="Thirduin",["x"]=205,["y"]=365,["castle"]=false,["level"]=0,["faction"]="turks",["culture"]="turks",["expandAI"]="turks",["population"]="510",
    ["bu"]=
        ["town_hall", "farms"],
    ["units"]=
        ["Dunedain Wardens", "Dunedain Rangers"],
    },
    ["7"]=
    {["name"]="Ghazabul",["x"]=376,["y"]=424,["castle"]=false,["level"]=1,["faction"]="moors",["culture"]="moors",["expandAI"]="moors",["population"]="330",
    ["bu"]=
        ["town_hall", "farms"],
    ["units"]=
        ["Iron Hills Mattocks"],
    },
    ["8"]=
    {["name"]="Edhellond",["x"]=251,["y"]=202,["castle"]=false,["level"]=0,["faction"]="sicily",["culture"]="scripts",["expandAI"]="sicily",["population"]="355",
    ["bu"]=
        ["town_hall", "farms", "corn_exchange", "brothel"],
    ["units"]=
        ["Territorial Swordsmen"],
    },
    ["9"]=
    {["name"]="Luinond",["x"]=28,["y"]=415,["castle"]=false,["level"]=0,["faction"]="slave",["culture"]="normans",["expandAI"]="slave",["population"]="450",
    ["bu"]=
        ["farms"],
    ["units"]=
        [""],
    },
    ["10"]=
    {["name"]="Yrch Estolad",["x"]=346,["y"]=232,["castle"]=false,["level"]=0,["faction"]="england",["culture"]="england",["expandAI"]="england",["population"]="1610",
    ["bu"]=
        ["town_hall", "garrison_quarters", "practice_range", "farms"],
    ["units"]=
        ["Orc Host", "Orc Archers"],
    },
    ["11"]=
    {["name"]="Bâr Nírnaeth",["x"]=353,["y"]=240,["castle"]=false,["level"]=0,["faction"]="england",["culture"]="england",["expandAI"]="england",["population"]="1100",
    ["bu"]=
        ["town_hall", "garrison_quarters", "practice_range", "farms"],
    ["units"]=
        ["Orc Host", "Orc Archers"],
    },
    ["12"]=
    {["name"]="Eorlstone",["x"]=260,["y"]=431,["castle"]=false,["level"]=1,["faction"]="slave",["culture"]="moors",["expandAI"]="slave",["population"]="230",
    ["bu"]=
        ["town_hall", "farms"],
    ["units"]=
        ["Snow-Orc Spearmen", "Snow-Orc Spearmen", "Snow-Orc Scouts", "Snow-Orc Scouts", "Snow-Orc Raiders", "Snow-Orc Raiders"],
    },
    ["13"]=
    {["name"]="Morva Tarth",["x"]=239,["y"]=411,["castle"]=false,["level"]=0,["faction"]="slave",["culture"]="england",["expandAI"]="slave",["population"]="551",
    ["bu"]=
        ["green_book_ettenmoors","town_hall", "farms"],
    ["units"]=
        ["Warg Riders", "Trolls", "Goblin Band", "Goblin Band", "Goblin Band","Goblin Archers", "Goblin Archers", "Goblin Archers"],
    },
	["14"]=
    {["name"]="Erech",["x"]=244,["y"]=236,["castle"]=false,["level"]=0,["faction"]="sicily",["culture"]="sicily",["expandAI"]="sicily",["population"]="210",
    ["bu"]=
        ["town_hall", "farms"],
    ["units"]=
        ["Territorial Swordsmen"],
    },
	["15"]=
    {["name"]="Amon Hen",["x"]=300,["y"]=251,["castle"]=false,["level"]=1,["faction"]="sicily",["culture"]="sicily",["expandAI"]="sicily",["population"]="115",
    ["bu"]=
        ["town_hall"],
    ["units"]=
        ["Territorial Swordsmen"],
    },
	["16"]=
    {["name"]="Caras Gelebren",["x"]=209,["y"]=345,["castle"]=true,["level"]=1,["faction"]="slave",["culture"]="ireland",["expandAI"]="slave",["population"]="650",
    ["bu"]=
        ["c_town_hall", "farms"],
    ["units"]=
        [""],
    },
}

//table of maps, coordinates on left, file name on right
::EUR.custom_maps <- {
	["121,380"] = "longbottom_a",              //(Michel_Derving)
	["133,385"] = "hobbiton_a",                //(Hobiton) tile corrected 2026-10-14: town sits at 133,385 on the current map
	["166,380"] = "bree_a",                    //(Bree) added 2026-10-14: package is tagged normans, town now runs on the Bree_Folk plan
	["144,375"] = "hobbit_village_a",          //(Lomgbotom)
	["169,358"] = "hobbit_village_a", // Underhill
	["147,380"] = "hobbit_village_a",              //(Buckland)
    ["194,380"] = "weathertop_a",              //(Amon_Sul)
	["442,338"] = "Caras Sant",                //(Caras_Sant)
	["323,119"] = "Faen_obel",                 //(Faen_obel)
	["300,251"] = "gondor_fort",               //(Amon_Hen)
	["88,356"] = "buzra_dum_a",                //(Burza_dum)
	["75,380"] = "Mithlond",                   //(mithlond)
	//["330,219"] = "osgiliath_east_repaired_a",  //(Osgiliath_E_GOOD REBUILD)
	//["328,219"] = "osgiliath_west_repaired_a",  //(Osgiliath_W_GOOD REBUILD)
	//
	["330,219"] = "osgiliath_east_a",    //(Osgiliath_E_GOOD)
	//["330,219"] = "osgiliath_east_aev",    //(Osgiliath_E_EVIL)
	//
	["186,333"] = "North Tharbad",       //(Tharbad north battle map)	
	//
	["188,333"] = "South Tharbad",       //(Tharbad south battle map)
	//
	["328,219"] = "osgiliath_west_a",    //(Osgiliath_W_GOOD)
	//["328,219"] = "osgiliath_west_aev",    //(Osgiliath_W_EVIL)
	//
	["324,217"] = "minas_tirith_a",      //(Minas_Tirith_GOOD)
	//["324,217"] = "minas_tirith_aev",      //(Minas_Tirith_EVIL)
	//
	["327,229"] = "cair_andros_a",       //(Cair_Andros_GOOD)
	["333,232"] = "henneth_a",                 //(Henneth Annun)
	//["327,229"] = "cair_andros_aev",       //(Cair_Andros_EVIL)
	//
    ["339,221"] = "minas_morgul_a",        //(Minas_Morgul)
	//["339,221"] = "Minas Ithil",           //(Minas_Ithil)
	//
	["224,279"] = "isengard_a",        //(Isengard_EVIL)
	//["224,279"] = "isengard_ag",       //(Isengard_GOOD)
}

::EUR.strat_models <- {
	[54] = "unique_ruined_city/unique_ruined_city.cas", // Caranost

    [1] = "Eru/Men/extension_pelargir.cas",
    [2] = "Eru/Other/burza_dum.cas",
    [3] = "Eru/Other/erech_stone.cas", 
    [4] = "Eru/Other/Mumakil_eur.cas", 
    [5] = "Eru/Other/pontkd.cas", 
    [6] = "Eru/Other/ravenhill.cas", 
	[7] = "Eru/Other/smaug.cas",
	[8] = "Eru/Other/Tharbad_N.cas",                                              //(Tharbad_N_REBUILD)
	[9] = "Eru/Other/Tharbad_S.cas",                                              //(Tharbad_S_REBUILD)
	[10] = "Eru/Men/Gondorian_village.cas",
	[11] = "Eru/Mistrand/amon_hen.cas",	 
	[12] = "Eru/Other/troll.cas",
	[13] = "Eru/Men/cameth_brin.cas",
    [14] = "Eru/Men/caras_sant.cas",
	[15] = "Eru/Mistrand/khand.cas",
	[16] = "Eru/Men/fenas_drunin.cas",
	[17] = "Eru/Men/isengard_good.cas",
	[18] = "Eru/Men/minas_ithil.cas",
	[19] = "Eru/Pelargir/pelargir.cas",
	[20] = "Eru/Other/Tharbad_N_RUINED.cas",                                       //(Tharbad_N_RUINED)
	[21] = "Eru/Special/dol_amroth_good.cas",
	[22] = "Eru/Evil/faenobel.cas",
	[23] = "Eru/Evil/umbar.cas",
	[24] = "Eru/Elve/amon_lanc.cas",	
	[25] = "Eru/Elve/amon_luine.cas",	
	[26] = "Eru/Elve/caras_galadhon_good.cas",	
	[27] = "Eru/Elve/iron_hill.cas",	
	[28] = "Eru/Elve/mitlond.cas",
	[29] = "Eru/Mistrand/mistrand.cas",	 	
	[30] = "Eru/Corupted/cair_andros_evil.cas",		
	[31] = "Eru/Corupted/caras_galadhon_evil.cas",	
	[32] = "Eru/Corupted/East_osghiliath_ruin_evil.cas",	
	[33] = "Eru/Corupted/helm_deep_evil.cas",	
	[34] = "Eru/Corupted/minas_thirith_evil.cas",	
	[35] = "Eru/Other/londaer.cas",	
	[36] = "Eru/Corupted/West_osghiliath_ruin_evil.cas",	
	[37] = "faction_variants/milan/northern_european_fortress.cas",	             //(Cair_andros)
	[38] = "faction_variants/poland/eastern_european_fortress.cas",	             //(Dol guldur)  
	[39] = "faction_variants/norway/southern_european_fortress.cas",	         //(Helm deep)
	[40] = "faction_variants/byzantium/northmen_t5_citadel.cas",	             //(Isengard)        
	[41] = "faction_variants/hungary/dwarf_t5_citadel.cas",	                     //(Minas Morgul)
	[42] = "faction_variants/norway/southern_european_huge_city.cas",	         //(Minas tirith) 
	[43] = "faction_variants/united/gondor_large_city.cas",	                     //(East Osgiliath) 
	[44] = "faction_variants/united/gondor_large_castle.cas",	                 //(West Osgiliath) 
	[45] = "Eru/Other/Tharbad_S_RUINED.cas",                                     //(Tharbad_S_RUINED)
	[46] = "Eru/Men/amon_sul_rebuild.cas",	                                     //(Amon_sul Rebuild)   
	[47] = "Eru/Men/amon_sul.cas",
	[48] = "gondor_t6_huge_city.cas",	                                         //(East Osgiliath REBUILD) 
	[49] = "gondor_t5_citadel.cas",	                                             //(West Osgiliath REBUILD) 	
	[50] = "faction_variants/united/gondor_t1_village.cas",	                     //(Hobbiton) 	
	[51] = "fort_henneth_annun.cas",
	[52] = "faction_variants/normans/northmen_t6_huge_city.cas", // City of Bree
	[53] = "faction_variants/normans/northmen_t1_village.cas", // Hobbit village
}

::EUR.strat_cas_setts <- {
	["Underhill"] = 53,
	["Caranost"] = 54,
	// Current map settlements; retain eursett_* aliases below for older saves.
	["Bree"] = 52,
	["Hobbiton"] = 50,
	["Shire_West"] = 53, // Michel Delving
	["Longbottom"] = 53,
	["Buckland"] = 50,
	["Henneth_Annun"] = 51,
	["eursett_1"] = 50,          //(Hobbiton)
	["eursett_2"] = 53,          //(Longbottom)
	["Amon_Hen"] = 11,           //(Amon Hen) current map name; alias kept below
	["eursett_15"] = 11,         //(Amon Hen)
	["Umbar"] = 23,              //(Umbar)
	["Iron_Hills"] = 27,         //(Iron hills)
	["Gobel_Ancalimon"] = 22,    //(Faenobel)
	["South_Ered_Luin"] = 2,     //(Burza dum)
	["Dorwinion"] = 14,          //(Caras sant)
	["Mithlond"] = 28,           //(Mithlond)
	["Mitheithel"] = 13,         //(Cameth brin)
	["Lebennin"] = 19,           //(Pelargir)
	["Belfalas"] = 21,           //(Dol amroth)
	["Angle"] = 16, 	         //(Fenas druin)
	["Mistrand"] = 29, 	         //(Mistrand)
	["Harad"] = 15, 	         //(Khand)
	["Druwaith_Iaur"] = 35, 	 //(Londaer)
	["Tharbad"] = 44,            //44 ruin/8 rebuild   (N tharbad)
    ["Ettenmoors"] = 45,         //45 ruin/9 rebuild   (S tharbad)
	["Weather_Hills"] = 47,      //47 ruin/46 rebuild   (Amon_Sul)
	["Celebrant"] = 26,          //26 good/31 evil      (Caras galadon)
    //["Anorien"] = xx,            //42 good/34 evil    (Minas tirith)
    //["Cair_Andros"] = xx,        //37 good/30 evil    (Cair_andros)
    //["West_Osgiliath"] = xx,     //44 good/36 evil    (West Osgiliath)
	//["East_Osgiliath"] = xx,     //43 good/32 evil    (East Osgiliath)
	//["Nan_Curunir"] = xx,        //17 good/40 evil    (Isengard)
    //["Morgul_Vale"] = xx,        //18 good/41 evil    (Minas Morgul)
	//["Deep_Mirkwood"] = xx,      //24 good/38 evil    (Dol guldur)
	//["Helms_Deep"] = xx,         //39 good/33 evil    (Helm deep)
}

::EUR.strat_cas_standalone <- {
	["troll"] = { 
        modelID = 12,
        scale = 1,
        xCoord = 209,
        yCoord = 373,
        appearing = true,
		tooltip = 
        @"Stone-trolls

Stone-trolls were huge trolls who turned into stone in direct sunlight.",
    },
	["erech"] = { 
        modelID = 3,
        scale = 1,
        xCoord = 246,
        yCoord = 237,
        appearing = true,
		tooltip = 
        @"The Stone of Erech

The Stone of Erech, also known as the Black Stone, was a large unearthly stone upon which the king of the mountains swore an oath to Isildur.",
    },
    ["smaug"] = { 
        modelID = 7,
        scale = 1,
        xCoord = 341,
        yCoord = 412,
        appearing = true,
		tooltip = 
        @"The skeleton of Smaug

Smaug left the mountain to wreak havoc on Esgaroth, razing it almost entirely before being killed by Bard the Bowman.",
    },
	["Scatha"] = { 
        modelID = 7,
        scale = 1,
        xCoord = 272,
        yCoord = 427,
        appearing = true,
		tooltip = 
        @"The skeleton of Scatha

He was killed by the lord of the Éothéod, Fram, son of Frumgar, an ancestor of Eorl the Younger.",
    },
	["Ravenhil"] = { 
        modelID = 6, 
        scale = 1,
        xCoord = 336,
        yCoord = 419,
        appearing = true,
		tooltip = 
        @"Ravenhil

The Dwarves built a guard-post there, above which the Ravens resided, led by Roäc.",
    },
	["Pontkd"] = { 
        modelID = 5, 
        scale = 1,
        xCoord = 238,
        yCoord = 342,
        appearing = true,
		tooltip = 
        @"The main road to Khazad-dum

A great road connected Ost-in-Edhil to Khazad-dûm, and an unprecedented friendship was born between the two nations.",
    },
    ["PelargirEX"] = { // Pelargir sud
        modelID = 1,
        scale = 1,
        xCoord = 316,
        yCoord = 180,
        appearing = true,
		tooltip = "",
    },
    ["graveyard1"] = { // Mumak
        modelID = 4,
        scale = 2,
        xCoord = 326,
        yCoord = 81,
        appearing = true,
		tooltip = 
        @"Mumakil graveyard

Indicates the presence of these creatures allowing their training in nearby settlements.",
    },
	["graveyard2"] = { // Mumak
        modelID = 4,
        scale = 2,
        xCoord = 361,
        yCoord = 95,
        appearing = true,
		tooltip =
        @"Mumakil graveyard

Indicates the presence of these creatures allowing their training in nearby settlements.",
    },
	["Village1"] = { // V1
        modelID = 10,
        scale = 1,
        xCoord = 312,
        yCoord = 199,
        appearing = true,
		tooltip = "",
    },
	["Village2"] = { // V2
        modelID = 10,
        scale = 1,
        xCoord = 289,
        yCoord = 209,
        appearing = true,
		tooltip = "",
    },
	["Village3"] = { // V3
        modelID = 10,
        scale = 1,
        xCoord = 266,
        yCoord = 186,
        appearing = true,
		tooltip = "",
    },
	["Village4"] = { // V4
        modelID = 10,
        scale = 1,
        xCoord = 263,
        yCoord = 203,
        appearing = true,
		tooltip = "",
    },
	["Village5"] = { // V5
        modelID = 10,
        scale = 1,
        xCoord = 251,
        yCoord = 229,
        appearing = true,
		tooltip = "",
    },
	["Village6"] = { // V6
        modelID = 10,
        scale = 1,
        xCoord = 236,
        yCoord = 208,
        appearing = true,
		tooltip = "",
    },
	["Village7"] = { // V7
        modelID = 10,
        scale = 1,
        xCoord = 222,
        yCoord = 230,
        appearing = true,
		tooltip = "",
    },
	["Village8"] = { // V8
        modelID = 10,
        scale = 1,
        xCoord = 196,
        yCoord = 202,
        appearing = true,
		tooltip = "",
    },
	["Village9"] = { // V9
        modelID = 10,
        scale = 1,
        xCoord = 176,
        yCoord = 216,
        appearing = true,
		tooltip = "",
    },
	["Village10"] = { // V10
        modelID = 10,
        scale = 1,
        xCoord = 327,
        yCoord = 188,
        appearing = true,
		tooltip = "",
    },
	["Village11"] = { // V11
        modelID = 10,
        scale = 1,
        xCoord = 291,
        yCoord = 231,
        appearing = true,
		tooltip = "",
    },
    ["Village12"] = { // V12
        modelID = 10,
        scale = 1,
        xCoord = 199,
        yCoord = 219,
        appearing = true,
		tooltip = "",
    },
}

::EUR.char_models <- {
    //
}

// debug helper: log the tile / region / settlement under a clicked map coordinate.
::EUR.onClickAtTile <- function(x, y) {
    println("it's a tile: " + x + ", " + y)
    local tile = ::EUR.eur_sMap.tile(x, y)
    local region = ::EUR.eur_sMap.region(tile.regionId)
    if (tile.settlement) { println(tile.settlement.name) }
    println(region.name)
}
