::EUR.cas_set_already <- {}
::EUR.cas_standalone_set_already <- false

// custom character models: name (also the .cas basename) + body-texture basename (some share one).
local CHAR_CAS = [
    { name = "tauriel",        tex = "tauriel_body_diff" },
    { name = "galadriel",      tex = "galadriel" },
    { name = "noldor_general", tex = "noldor_general" },
    { name = "noldor_captain", tex = "noldor_general" },
    { name = "sharku",         tex = "sharku" },
]

::EUR.loadCharCAS <- function() {
    ::EUR.logHelper("loadCharCAS")
    local diskBase = ::game.modPath() + "\\data\\models_strat\\"
    local modBase = "mods/Divide_and_Conquer_EUR/data/models_strat/"
    foreach (c in CHAR_CAS) {
        if (::EUR.file_exists(diskBase + c.name + ".cas") && ::EUR.file_exists(diskBase + "textures\\" + c.tex + ".tga")) {
            local casPath = modBase + c.name + ".cas"
            ::game.models.addCharacter("strat_named_with_army", casPath, casPath, c.name,
                modBase + "textures/" + c.tex + ".tga", 0.7)
            ::EUR.custom_cas[c.name] <- true
        }
    }
    ::EUR.logHelper("loadCharCAS end")
}

::EUR.loadStratCAS <- function() {
    ::EUR.logHelper("loadStratCAS")
    // Settlement overrides need alpha rendering and model intersection; map props do not.
    local settlementModels = {}
    foreach (name, modelID in ::EUR.strat_cas_setts) { settlementModels[modelID] <- true }
    // Both Carn Dum states are residence models, including the later restoration.
    settlementModels[57] <- true
    settlementModels[58] <- true
    foreach (modelID, path in ::EUR.strat_models) {
        if (path != "") {
            ::game.models.add("data/models_strat/residences/" + path, modelID, modelID in settlementModels)
        }
    }
    ::EUR.logHelper("loadStratCAS end")
}

::EUR.setCasStandalone <- function() {
    ::EUR.logHelper("setCasStandalone")
    // campaignMapLoaded fires after every battle as well, so take each map prop down before
    // drawing it again; otherwise every battle would add another copy of every prop.
    foreach (key, prop in ::EUR.strat_cas_standalone) {
        try { ::game.models.stopDrawing(prop.modelID) } catch (e) {}
    }
    foreach (key, prop in ::EUR.strat_cas_standalone) {
        if (prop.appearing) { ::game.models.drawAt(prop.modelID, prop.xCoord, prop.yCoord, prop.scale.tofloat()) }
    }
    foreach (name, modelID in ::EUR.strat_cas_setts) {
        local sett = ::EUR.eur_sMap.findSettlement(name)
        if (sett != null) { ::EUR.setCasSett(sett) }
        else { try { ::game.log("[EUR cas] not found: " + name) } catch (e) {} }
    }
    ::EUR.logHelper("setCasStandalone end")
}

::EUR.setCasSett <- function(sett) {
    ::EUR.logHelper("setCasSett")
    if (sett != null && sett.name in ::EUR.strat_cas_setts) {
        // Derive restoration from the saved settlement tier; no cross-save latch.
        if (sett.name == "Carn_Dum") {
            ::EUR.strat_cas_setts[sett.name] = sett.level >= 3 ? 58 : 57
        }
        local modelID = ::EUR.strat_cas_setts[sett.name]
        try { ::game.log("[EUR cas] " + sett.name + " tile " + sett.tileX + "," + sett.tileY + " model " + modelID) } catch (e) {}
        ::game.models.setOnTile(sett.tileX, sett.tileY, modelID, modelID)
    }
    ::EUR.logHelper("setCasSett end")
}

::EUR.good_factions <- [
    "byzantium", "denmark", "hungary", "ireland", "milan", "mongols", "moors",
    "norway", "saxons", "scotland", "sicily", "teutonic_order", "timurids", "turks",
]
::EUR.elf_factions <- ["denmark", "ireland", "mongols", "saxons"]
::EUR.evil_factions <- ["england", "france", "gundabad", "hre", "normans", "poland", "portugal"]

::EUR.anorien_swap <- {
    anorien_good = true, mordor_takeover = false, gondor_takeover = false,
    mordor_timer = 5, gondor_timer = 5,
    isengard_good = false, isengard_takeover = false, isengard_timer = 5,
    dg_good = false, dg_takeover = false, dg_timer = 5,
    helm_good = true, helm_takeover = false, helm_timer = 5,
    minasmorgul_good = false, minasmorgul_takeover = false, minasmorgul_timer = 5,
    carasg_good = true, carasg_takeover = false, carasg_timer = 5,
    tharbad_restored = false, amonsul_restored = false,
    tauriel_spawned = false, galadriel_spawned = false, NDCASset = false, sharku_spawned = false,
}

::EUR.isengardSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (::EUR.anorien_swap.isengard_good) return
    if (::EUR.tableContains(::EUR.evil_factions, ::EUR.eur_sMap.findSettlement("Nan_Curunir").owner.name)) {
        ::EUR.anorien_swap.isengard_takeover = false
        ::EUR.anorien_swap.isengard_timer = 5
        return
    }
    ::EUR.anorien_swap.isengard_takeover = true
    if (::EUR.anorien_swap.isengard_timer == 1) {
        ::game.models.setOnTile(224, 279, 17, 17)   // Isengard (good)
        ::EUR.custom_maps["224,279"] = "isengard_ag"
        ::game.showHistoricEvent("isengard_cleansed", ::EUR.isengard_cleansed_title, ::EUR.isengard_cleansed_body)
        ::EUR.anorien_swap.isengard_takeover = false
        ::EUR.anorien_swap.isengard_good = true
        ::EUR.anorien_swap.isengard_timer = 5
    } else {
        ::EUR.anorien_swap.isengard_timer = ::EUR.anorien_swap.isengard_timer - 1
    }
}

::EUR.amonlancSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (::EUR.anorien_swap.dg_good) return
    if (!::EUR.tableContains(::EUR.elf_factions, ::EUR.eur_sMap.findSettlement("Deep_Mirkwood").owner.name)) {
        ::EUR.anorien_swap.dg_takeover = false
        ::EUR.anorien_swap.dg_timer = 5
        return
    }
    ::EUR.anorien_swap.dg_takeover = true
    if (::EUR.anorien_swap.dg_timer == 1) {
        ::EUR.eur_sMap.findSettlement("Deep_Mirkwood").displayName = "Amon Lanc"
        ::game.campaign().setEventCounter("lanc_cleared", 1)
        ::game.models.setOnTile(299, 329, 24, 24)
        ::game.showHistoricEvent("amon_lanc_cleansed", ::EUR.amon_lanc_cleansed_title, ::EUR.amon_lanc_cleansed_body)
        ::EUR.anorien_swap.dg_takeover = false
        ::EUR.anorien_swap.dg_good = true
        ::EUR.anorien_swap.dg_timer = 5
    } else {
        ::EUR.anorien_swap.dg_timer = ::EUR.anorien_swap.dg_timer - 1
    }
}

::EUR.helmSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (!::EUR.anorien_swap.helm_good) return
    if (::EUR.eur_sMap.findSettlement("Helms_Deep").owner.name != "france") {
        ::EUR.anorien_swap.helm_takeover = false
        ::EUR.anorien_swap.helm_timer = 5
        return
    }
    ::EUR.anorien_swap.helm_takeover = true
    if (::EUR.anorien_swap.helm_timer == 1) {
        ::EUR.eur_sMap.findSettlement("Helms_Deep").displayName = "Ost-Curunír"
        ::game.models.setOnTile(230, 260, 33, 33)   // Helm's Deep (corrupted)
        ::game.showHistoricEvent("helms_deep_corrupted", ::EUR.helms_deep_corrupted_title, ::EUR.helms_deep_corrupted_body)
        ::EUR.anorien_swap.helm_takeover = false
        ::EUR.anorien_swap.helm_good = false
        ::EUR.anorien_swap.helm_timer = 5
    } else {
        ::EUR.anorien_swap.helm_timer = ::EUR.anorien_swap.helm_timer - 1
    }
}

::EUR.carasSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (::EUR.anorien_swap.carasg_good) return
    if (!::EUR.tableContains(::EUR.evil_factions, ::EUR.eur_sMap.findSettlement("Celebrant").owner.name)) {
        ::EUR.anorien_swap.carasg_takeover = false
        ::EUR.anorien_swap.carasg_timer = 5
        return
    }
    ::EUR.anorien_swap.carasg_takeover = true
    if (::EUR.anorien_swap.carasg_timer == 1) {
        ::game.models.setOnTile(268, 327, 31, 31)   // Caras Galadhon (corrupted)
        ::game.showHistoricEvent("caras_galadhon_corrupted", ::EUR.caras_galadhon_corrupted_title, ::EUR.caras_galadhon_corrupted_body)
        ::EUR.anorien_swap.carasg_takeover = false
        ::EUR.anorien_swap.carasg_good = true
        ::EUR.anorien_swap.carasg_timer = 5
    } else {
        ::EUR.anorien_swap.carasg_timer = ::EUR.anorien_swap.carasg_timer - 1
    }
}

::EUR.minasIthilSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (::EUR.anorien_swap.minasmorgul_good) return
    local owner = ::EUR.eur_sMap.findSettlement("Morgul_Vale").owner.name
    if (!(owner == "sicily" || owner == "turks" || owner == "russia")) {
        ::EUR.anorien_swap.minasmorgul_takeover = false
        ::EUR.anorien_swap.minasmorgul_timer = 5
        return
    }
    ::EUR.anorien_swap.minasmorgul_takeover = true
    if (::EUR.anorien_swap.minasmorgul_timer == 1) {
        ::EUR.eur_sMap.findSettlement("Morgul_Vale").displayName = "Minas Ithil"
        ::game.models.setOnTile(339, 221, 18, 18)
        ::EUR.custom_maps["339,221"] = "Minas Ithil"
        ::game.showHistoricEvent("minas_ithil_cleansed", ::EUR.minas_ithil_cleansed_title, ::EUR.minas_ithil_cleansed_body)
        ::EUR.anorien_swap.minasmorgul_takeover = false
        ::EUR.anorien_swap.minasmorgul_good = true
        ::EUR.anorien_swap.minasmorgul_timer = 5
    } else {
        ::EUR.anorien_swap.minasmorgul_timer = ::EUR.anorien_swap.minasmorgul_timer - 1
    }
}

::EUR.tharbadSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (::EUR.anorien_swap.tharbad_restored) return
    local tharbad = ::EUR.eur_sMap.findSettlement("Tharbad")
    local owner = tharbad.owner.name
    if (!(owner == "turks" || owner == "sicily" || owner == "russia" || owner == "teutonic_order")) return
    if (!tharbad.hasBuildingLevel("rebuilt_bridge", true)) return

    ::EUR.strat_cas_setts["Tharbad"] = 8
    ::EUR.strat_cas_setts["Ettenmoors"] = 9
    ::game.models.setOnTile(186, 333, 8, 8)   // Tharbad north
    ::game.models.setOnTile(188, 333, 9, 9)   // Tharbad south
    ::EUR.custom_maps["188,333"] = "South Tharbad"
    ::EUR.custom_maps["186,333"] = "North Tharbad"
    ::game.showHistoricEvent("tharbad_rebuilt", ::EUR.tharbad_restored_title, ::EUR.tharbad_restored_body)
    ::EUR.anorien_swap.tharbad_restored = true
}

::EUR.amonSulSwapCheck <- function(faction) {
    if (faction.name != "slave") return
    if (::EUR.anorien_swap.amonsul_restored) return
    local weatherHills = ::EUR.eur_sMap.findSettlement("Weather_Hills")
    local owner = weatherHills.owner.name
    if (!(owner == "turks" || owner == "sicily" || owner == "russia")) return
    if (!::EUR.checkCounter("arnor_restored")) return

    ::EUR.strat_cas_setts["Weather_Hills"] = 46
    ::game.models.setOnTile(194, 380, 46, 46)   // Amon Sul (restored)
    ::game.showHistoricEvent("amon_sul_rebuilt", ::EUR.amon_sul_restored_title, ::EUR.amon_sul_restored_body)
    ::EUR.anorien_swap.amonsul_restored = true
}

::EUR.mordorAnorienCheck <- function(faction) {
    local gondorSide = function(name) { return name == "sicily" || name == "turks" || name == "russia" }

    if (faction.name == "england") {
        if (!::EUR.anorien_swap.anorien_good) return
        local holdsAll = ::EUR.eur_sMap.findSettlement("Anorien").owner.name == "england"
            && ::EUR.eur_sMap.findSettlement("East_Osgiliath").owner.name == "england"
            && ::EUR.eur_sMap.findSettlement("West_Osgiliath").owner.name == "england"
            && ::EUR.eur_sMap.findSettlement("Cair_Andros").owner.name == "england"
        if (!holdsAll) {
            ::EUR.anorien_swap.mordor_takeover = false
            ::EUR.anorien_swap.mordor_timer = 5
            return
        }
        ::EUR.anorien_swap.gondor_takeover = false
        ::EUR.anorien_swap.gondor_timer = 5
        ::EUR.anorien_swap.mordor_takeover = true
        if (::EUR.anorien_swap.mordor_timer == 1) {
            ::EUR.eur_sMap.findSettlement("Anorien").displayName = "Amon Dûr"
            ::game.models.setOnTile(324, 217, 34, 34)   // Minas Tirith (evil)
            ::game.models.setOnTile(328, 219, 36, 36)   // West Osgiliath
            ::game.models.setOnTile(330, 219, 32, 32)   // East Osgiliath
            ::game.models.setOnTile(327, 229, 30, 30)   // Cair Andros
            ::EUR.custom_maps["330,219"] = "osgiliath_east_aev"
            ::EUR.custom_maps["328,219"] = "osgiliath_west_aev"
            ::EUR.custom_maps["324,217"] = "minas_tirith_aev"
            ::EUR.custom_maps["327,229"] = "cair_andros_aev"
            ::game.showHistoricEvent("anorien_corrupted", ::EUR.anorien_corrupted_title, ::EUR.anorien_corrupted_body)
            ::EUR.anorien_swap.mordor_takeover = false
            ::EUR.anorien_swap.anorien_good = false
            ::EUR.anorien_swap.mordor_timer = 5
        } else {
            ::EUR.anorien_swap.mordor_timer = ::EUR.anorien_swap.mordor_timer - 1
        }
    } else if (faction.name == "sicily") {
        if (::EUR.anorien_swap.anorien_good) return
        local holdsAll = gondorSide(::EUR.eur_sMap.findSettlement("Anorien").owner.name)
            && gondorSide(::EUR.eur_sMap.findSettlement("East_Osgiliath").owner.name)
            && gondorSide(::EUR.eur_sMap.findSettlement("West_Osgiliath").owner.name)
            && gondorSide(::EUR.eur_sMap.findSettlement("Cair_Andros").owner.name)
        if (!holdsAll) {
            ::EUR.anorien_swap.gondor_takeover = false
            ::EUR.anorien_swap.gondor_timer = 5
            return
        }
        ::EUR.anorien_swap.mordor_takeover = false
        ::EUR.anorien_swap.mordor_timer = 5
        ::EUR.anorien_swap.gondor_takeover = true
        if (::EUR.anorien_swap.gondor_timer == 1) {
            ::EUR.eur_sMap.findSettlement("Anorien").displayName = "Minas Tirith"
            ::game.models.setOnTile(324, 217, 42, 42)   // Minas Tirith (good)
            if (::EUR.eur_sMap.findSettlement("East_Osgiliath").level == 5) {
                ::game.models.setOnTile(330, 219, 48, 48)
                ::EUR.custom_maps["330,219"] = "osgiliath_east_repaired_a"
            } else {
                ::game.models.setOnTile(330, 219, 43, 43)
                ::EUR.custom_maps["330,219"] = "osgiliath_east_a"
            }
            if (::EUR.eur_sMap.findSettlement("West_Osgiliath").level == 4) {
                ::game.models.setOnTile(328, 219, 49, 49)
                ::EUR.custom_maps["328,219"] = "osgiliath_west_repaired_a"
            } else {
                ::game.models.setOnTile(328, 219, 44, 44)
                ::EUR.custom_maps["328,219"] = "osgiliath_west_a"
            }
            ::game.models.setOnTile(327, 229, 37, 37)   // Cair Andros (good)
            ::EUR.custom_maps["324,217"] = "minas_tirith_a"
            ::EUR.custom_maps["327,229"] = "cair_andros_a"
            ::game.showHistoricEvent("anorien_cleansed", ::EUR.anorien_cleansed_title, ::EUR.anorien_cleansed_body)
            ::EUR.anorien_swap.gondor_takeover = false
            ::EUR.anorien_swap.anorien_good = true
            ::EUR.anorien_swap.gondor_timer = 5
        } else {
            ::EUR.anorien_swap.gondor_timer = ::EUR.anorien_swap.gondor_timer - 1
        }
    }

    // keep the Osgiliath map variants in step with their upgrade tier while Anorien is good
    if (::EUR.anorien_swap.anorien_good) {
        if (gondorSide(::EUR.eur_sMap.findSettlement("East_Osgiliath").owner.name)
            && ::EUR.eur_sMap.findSettlement("East_Osgiliath").level == 5) {
            ::EUR.custom_maps["330,219"] = "osgiliath_east_repaired_a"
        }
        if (gondorSide(::EUR.eur_sMap.findSettlement("West_Osgiliath").owner.name)
            && ::EUR.eur_sMap.findSettlement("West_Osgiliath").level == 4) {
            ::EUR.custom_maps["328,219"] = "osgiliath_west_repaired_a"
        }
    }
}

::EUR.coord_lookup <- {}
foreach (key, data in ::EUR.strat_cas_standalone) {
    if (!(data.xCoord in ::EUR.coord_lookup)) { ::EUR.coord_lookup[data.xCoord] <- {} }
    ::EUR.coord_lookup[data.xCoord][data.yCoord] <- key
}

::EUR.supplyTooltip <- function() {}

::EUR.tooltipAtCoord <- function() {
    if ((::UI.context() & ::Enum.UiContext.campaignLive) == 0) return
    if (::UI.cursorOverGameUi()) return

    local tile = ::stratMap.hoveredTile()
    if (tile == null) return
    if (!(tile.x in ::EUR.coord_lookup)) return
    local column = ::EUR.coord_lookup[tile.x]
    if (!(tile.y in column)) return

    local prop = ::EUR.strat_cas_standalone[column[tile.y]]
    if (prop == null || !("tooltip" in prop) || prop.tooltip == "") return

    local pad = 6
    local mouse = ::UI.mouse.pos()
    ::UI.tooltipAt(mouse[0] - pad, mouse[1] - pad, pad * 2, pad * 2)
    ::UI.tooltip(0, prop.tooltip)
}

::UI.onFrame(function() { ::EUR.tooltipAtCoord() })
