// Aragorn's journey (the "Aragorn" trait, shown in-game as "Biography") is advanced by
// EDCT triggers AragornRPG_ii_iv / iii / v / vi / vii / viii in export_descr_character_traits.txt.
// Under M2EX those region-based triggers never fire, so the chain sticks at level 1 and the
// campaign_script popups (letter, Gollum, Narsil, Anduril, ...) never come. This re-implements
// the six triggers on CharacterTurnStart, one level per stop, and leaves the popups to
// campaign_script.txt exactly as before (they key off the trait level at the next FactionTurnStart).
//
// If the engine's own trigger ever starts working again this cannot double-advance: every level
// has exactly one target region, and whichever runs first makes the other's level check fail.

local TRAIT = "Aragorn"
local STAY_COUNTER = "eur_aragorn_fix_stay"   // turns in a row spent in the current target region
local BREELAND = ["Bree_Province", "Combe_Province", "Archet_Province", "Trestlebridge_Province"]

// trait level now -> where Aragorn must START his turn, how many turns in a row, extra conditions
local STEPS = {}
STEPS[1] <- { regions = BREELAND,                   stay = 1, minTurn = 5, turksOnly = true }  // Bree: letter
STEPS[2] <- { regions = ["Mitheithel_Province"],    stay = 1 }                                 // Cameth Brin: Gollum
STEPS[3] <- { regions = BREELAND,                   stay = 1, minTurn = 5, turksOnly = true }  // Bree again: reforge Narsil
STEPS[4] <- { regions = ["Imladris_Province"],      stay = 2 }                                 // Rivendell: Anduril
STEPS[5] <- { regions = ["Weather_Hills_Province"], stay = 1 }                                 // Amon Sul
STEPS[6] <- { regions = ["Kings_Land_Province"],    stay = 2 }                                 // Edoras
STEPS[7] <- { regions = ["Anorien_Province"],       stay = 4 }                                 // Minas Tirith

::EUR.aragornFix <- {
    enabled = true,
    testMoves = false,   // true = refill Aragorn's movement every turn (testing aid only)
    memStay = 0,         // fallback when the event counter cannot be used
}

local contains = function(list, value) {
    foreach (item in list) { if (item == value) return true }
    return false
}

local readStay = function(campaign) {
    try {
        local v = campaign.getEventCounter(STAY_COUNTER)
        if (v != null) return v
    }
    catch (e) {}
    return ::EUR.aragornFix.memStay
}

local writeStay = function(campaign, value) {
    ::EUR.aragornFix.memStay = value
    try { campaign.setEventCounter(STAY_COUNTER, value) }
    catch (e) {}
}

local refillMoves = function(character) {
    try {
        local max = null
        try { max = character.movePointsMax } catch (e) { max = null }
        character.movePoints = (max != null && max > 0) ? max : 9999
    }
    catch (e) {
        println("eur: aragorn journey - cannot set movePoints: " + e)
    }
}

local onCharacterTurnStart = function(eventData) {
    if (!::EUR.aragornFix.enabled) return
    local record = eventData.characterRecord
    if (record == null || record.character == null) return

    local level = record.traitLevel(TRAIT)
    if (level <= 0) return                      // only Aragorn carries this trait

    local character = record.character
    if (::EUR.aragornFix.testMoves) { refillMoves(character) }

    if (!(level in STEPS)) return               // journey finished
    local step = STEPS[level]
    local faction = eventData.faction
    if (faction == null || faction.isPlayerControlled != 1) return
    if (("turksOnly" in step) && faction.name != "turks") return

    local campaign = ::game.campaign()
    if (campaign == null) return
    if (("minTurn" in step) && campaign.turnNumber < step.minTurn) return

    local region = ::stratMap.region(character.regionId)
    local here = region == null ? "" : region.name
    if (!contains(step.regions, here)) {
        writeStay(campaign, 0)
        return
    }

    local stay = readStay(campaign) + 1
    if (stay < step.stay) {
        writeStay(campaign, stay)
        return
    }

    record.addTraitPoints(TRAIT, 1)
    writeStay(campaign, 0)
    println("eur: aragorn journey - " + here + " reached, level " + level + " -> " + (level + 1))
}

::events.on("CharacterTurnStart", onCharacterTurnStart)

// Squirrel console: ::EUR.aragornFix.status()
::EUR.aragornFix.status <- function() {
    local campaign = ::game.campaign()
    if (campaign == null) { println("eur: aragorn journey - no campaign"); return }
    local rec = campaign.findCharacterByLabel("aragorn_1")
    if (rec == null || rec.character == null) { println("eur: aragorn journey - aragorn_1 not found"); return }
    local level = rec.traitLevel(TRAIT)
    local region = ::stratMap.region(rec.character.regionId)
    local here = region == null ? "?" : region.name
    local want = (level in STEPS) ? STEPS[level].regions[0] + " x" + STEPS[level].stay : "done"
    println("eur: aragorn journey - turn " + campaign.turnNumber + ", level " + level
        + ", in " + here + ", next stop " + want + ", stayed " + readStay(campaign))
}

println("eur: aragorn journey fix loaded")
