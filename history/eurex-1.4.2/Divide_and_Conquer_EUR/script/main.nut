::EUR <- {}
// Squirrel load order, mirroring eopData/eopScripts/luaPluginScript.lua's require list.
// Helpers first (luaCompat, then the eurGlobal split: styles / vars / temp vars / helpers),
// then the plugin-script order. eur.helpers.eurGlobal is intentionally NOT here - its content
// was split into helper.eurStyles / eurVars / eurVarsTemp / eurHelpers.
// Missing files fail soft (try/catch below) - not everything is ported yet.

::EUR.to_log <- false
::EUR.dev_enabled <- false


// eurOverrides split into per-category trigger files (eur*Triggers.nut); each file's event
// registrations are gated on its flag here. All on by default.
::EUR.EUR_EVENT_TRIGGERS <- {
    campaign   = true,
    battle     = true,
    character  = true,
    settlement = true,
    ui         = true,
    counter    = true,
    other      = true,
}

//auto_turn <- false
//auto_turn_number <- 74

::EUR.chris_stuff <- false

local MODULES = [
    // Register the difficulty lock before campaign systems read or cache the level.
    "eur.options.eurCampaignDifficultyLock",
    // The shared art and tooltip sheets, which the base main.nut would load if a mod had not
    // replaced it. First, because the scroll helper draws with them.
    "core.styles",
    "core.images",
    "core.scale",
    "core.fonts",
    // ::fonts and ::virtualScale, which used to come from the base script tree. First, because
    // everything below draws with them.
    "helper.eurBaseGlobals",
    "eur.audio.elfHeroes",
    "eur.audio.nazgulHeroes",
    "eur.audio.missedExactUnits",
    "eur.audio.dolGuldurUnits",
    "eur.audio.ereborUnits",
    "eur.audio.voiceMixerGenerated",
    "eur.audio.mountainGiant",
    "eur.audio.fireDrake",
    "eur.audio.haradScorpions",
    "eur.audio.aotrRoster",
    "eur.audio.coldDrakes",
    "eur.audio.tomBombadil",
    "eur.audio.chetwoodHunters",
    "eur.audio.breelandMilitia",
    "eur.campaign.chetwoodHunters",
    "helper.luaCompat",
    "helper.eurUndeclared",
    "helper.eurScroll",
    "helper.eurStyles",
    "helper.eurVars",
    "helper.eurVarsTemp",
    "helper.eurHelpers",
    "helper.eurText",
    "helper.eurGlobalVars",
    "helper.eurSaveLoadValues",
    "helper.eurSaveLoadOptions",
    "helper.eurSaveLoadDefaults",
    "helper.eurUpgradeSave",
    // last: it names every window instance, so they all have to exist first
    "helper.eurRecalibrate",

    "eur.dev.chrisDev",
    // parked - the layout/UI editor debug window is off for now
    //"eur.dev.eurLayoutEditor",
    "eur.chris_setts.chrisAddResBU",
    "helper.EopLuaHelpers",
    "eur.confed.eurRK",
    "eur.upgrades.eurUnitCardLoc",

    "eur.eru.eurMapHelpers",

    "eur.loaded.eurImgLoad",
    "eur.loaded.eurCasLoad",
    "eur.loaded.eurSoundLoad",
    "eur.loaded.eurFontLoad",

    "eur.rebels.eurRebelSetup",
    "eur.campaign.eurUniqueNames",

    "eur.upgrades.eurPlayerUnitsCut",
    "eur.options.eurGameOptions",
    "eur.options.eurOptions",
    "eur.options.eurOptionsWelcome",
    "eur.options.eurOptionsCampaign",
    "eur.options.eurOptionsCampaignExtra",
    "eur.options.eurOptionsBattle",
    "eur.options.eurOptionsDifficulty",
    "eur.options.eurOptionsGeneralADV",
    "eur.options.eurOptionsUnitADV",
    "eur.options.eurOptionsUpgrades",
    "eur.options.eurOptionsAA",
    "eur.options.eurOptionsCredits",
    "eur.options.eurOptionsPreferences",
    "eur.options.eurOptionsCustomization",
    "eur.options.eurOptionsNotices",

    "eur.upgrades.eurUnitUpgradeDefault",
    "eur.upgrades.eurUnitUpgradeList",
    "eur.upgrades.eurUnitUpgrades",

    "eur.eurEvent.eurEventsVars",
    "eur.eurEvent.eurEventsFunc",


    "eur.upgrades.eurGeneralBGSwapDefault",
    "eur.upgrades.eurGeneralBGSwapList",
    "eur.upgrades.eurGeneralBGSwapDefault2",
    "eur.upgrades.eurGeneralBGSwapList2",
    "eur.upgrades.eurGeneralBGSwapData",
    "eur.upgrades.eurGeneralBGSwap",
    "eur.upgrades.eurLeaderHeirSwap",
    "eur.global_recruitment.eurGlobalRecruitment",
    "eur.spoils.eurAltLoot",
    "eur.campaign.eurAddCustomBGUnits",
    "eur.campaign.eurDifficulty",
    "eur.campaign.eurForeverWars",
    "eur.campaign.eurCustomGenerals",
    "eur.campaign.eurEvolvingFactions",
    "eur.battle.eursetBattleMapPKG",
    "eur.campaign.eurRevealAllied",
    "eur.campaign.eurWatchtowers",
    "eur.campaign.eurForts",
    "eur.campaign.eurSpawnGeneral",
    "eur.campaign.eurAssignFactionTraits",
    "eur.campaign.eurReviveFactions",
    "eur.campaign.eurBuildFort",
    "eur.campaign.eurStatusIcons",

    // Native battle-AI integration and related campaign behavior.
    "eur.battle.eurBattleAI",
    "eur.battle.caveTrollSiege",
    "eur.battle.monsterAbilityConfig",
    "eur.battle.trollMaceCombat",
    "eur.battle.monsterAttackAreas",
    "eur.battle.trollCarry",
    "eur.battle.mountainGiant",
    "eur.battle.fireDrake",
    "eur.battle.haradScorpions",
    "eur.battle.aotrRoster",
    "eur.battle.coldDrakes",
    "eur.battle.tomBombadil",
    "eur.battle.warbandSwordShield",

    "eur.helmsbrick.eurHelmsBrick",
    "eur.campaign.eurGuilds",

    "eur.army sort-merge.eurMergeArmies",
    "eur.confed.eurSwapUnits",
    "eur.replenishment.eurReplenishment",
    "eur.spoils.eurAddSpoils",
    "eur.confed.eurEregion",
    "eur.confed.eurReunitedKingdom",
    "eur.confed.eurElvenUnion",
    "eur.army sort-merge.eurSortStack",
    "eur.temp.EDU",

    "eur.garrisons.eurGarrisonsList",
    "eur.garrisons.eurGarrisons",

    // Resolve the three presets after all option defaults and tab schemas exist.
    "eur.options.eurPresets",

    // Event-trigger helpers used by campaign systems, including AI inputs.
    "helper.eurCampaignTriggers",
    "helper.eurBattleTriggers",
    "helper.eurCharacterTriggers",
    "helper.eurSettlementTriggers",
    "helper.eurUiTriggers",
    "helper.eurCounterTriggers",
    "helper.eurOtherTriggers",

    // Historical EUR campaign-AI rule program. Registers the Squirrel LTGD hook.
    "eur.campaign.eurBreeland",
    "eur.campaign.namedHeroBodyguards",
    // Hotfix: M2EX never fires the EDCT region triggers behind Aragorn's journey.
    "eur.campaign.eurAragornJourneyFix",
    "eur_ai.main",
]

// Plugin-script binding-form requires (eurHelmsBrick = require(...), eurMerge = ..., etc.) that
// captured the module's return into a global still need that binding when ported - they are loaded
// for side effects above; add the return-value capture as each is ported.

local failed = []
::EUR.moduleErrors <- []
// Entry scripts run before EDB parses. Apply these rules once the database is ready,
// independently of the optional campaign AI; also handle a reload in a live campaign.
local buildingProtectionApplied = false
local applyBuildingProtection = function() {
    if (buildingProtectionApplied) return
    try {
        let protectedCount = require("eur_ai.hinterland_protection").apply()
        if (protectedCount == 0) throw "No EUR building chains were protected"
        buildingProtectionApplied = true
        println("eur: protected " + protectedCount + " building chains from demolition")
    }
    catch (e) {
        ::EUR.moduleErrors.append("eur_ai.hinterland_protection -> " + e)
        println("eur: BUILDING PROTECTION FAILED " + e)
    }
}
::events.on("gameInit", applyBuildingProtection)
::events.on("campaignMapLoaded", applyBuildingProtection)
if (::buildings.count() > 0) { applyBuildingProtection() }
foreach (name in MODULES) {
    try {
        require(name)
    }
    catch (e) {
        failed.append(name)
        ::EUR.moduleErrors.append(name + " -> " + e)
        println("eur: MODULE FAILED [" + name + "] " + e)
    }
}

if (failed.len() == 0) {
    println("eur: loaded")
} else {
    local list = ""
    foreach (i, name in failed) list += (i == 0 ? "" : ", ") + name
    println("eur: loaded with " + failed.len() + " module(s) SKIPPED: " + list)
}

::EUR.reload <- function() {
    if (!("campaignBoot" in ::EUR)) { return false }
    ::EUR.campaignBoot()
    return true
}

try {
    if (::game.campaign() != null) { ::EUR.reload() }
}
catch (e) {
}
