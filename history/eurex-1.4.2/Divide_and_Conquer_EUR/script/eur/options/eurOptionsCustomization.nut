// Campaign choices remain saved in game_options/build_forts and in the upgrade rosters.
// They are independent of the campaign's chosen difficulty preset.
::EUR.ensureCustomizationDefaults <- function() {
    local defaults = { auto_culture_conversion = false, player_revival = true, ai_extra_gold = 0 }
    foreach (key, value in defaults) {
        if (!(key in ::EUR.game_options)) ::EUR.game_options[key] <- value
    }
}
::EUR.ensureCustomizationDefaults()

// These fields may override a locked mode without replacing its other balance settings.
::EUR.customizationBindings <- [
    ["build_forts"], ["options_general_large_army"],
    ["game_options", "auto_culture_conversion"], ["game_options", "convert_buildings"],
    ["game_options", "global_waystation_req"], ["game_options", "global_waystation_inc_max"],
    ["game_options", "player_revival"], ["game_options", "airevive"],
    ["game_options", "unlimited_revival"], ["game_options", "revival_cost"],
    ["game_options", "revival_disposition_ignored"], ["game_options", "ai_extra_gold"],
    ["options_gen_upgrades"], ["game_options", "BG_T2"], ["bg_t2_rank"], ["bg_t3_rank"],
    ["bg_swap_cooldown"], ["options_gen_bg_size"], ["bg_min_size_multi"],
    ["options_unit_upgrades"], ["unit_upgrades_multi"], ["restricted_upgrades"], ["ai_unit_upgrades"],
]
::EUR.captureCustomization <- function() {
    local out = []
    foreach (binding in ::EUR.customizationBindings) {
        local container = binding.len() == 1 ? ::EUR : ::EUR[binding[0]]
        out.append(::EUR.deepCopyValue(container[binding[binding.len()-1]]))
    }
    return out
}
::EUR.restoreCustomization <- function(values) {
    foreach (i, binding in ::EUR.customizationBindings) {
        local container = binding.len() == 1 ? ::EUR : ::EUR[binding[0]]
        container[binding[binding.len()-1]] = ::EUR.deepCopyValue(values[i])
    }
}

local function changed(value) {
    ::EUR.presetSettingsRevision++
    ::game.runScriptCommand("play_sound_event", "BUTTON_DOWN")
}

local function recruitmentChanged(value) {
    if (!::EUR.options_first_run && ("eurGlobalRecruitment" in ::EUR)) {
        ::EUR.eurGlobalRecruitment.recruitCheckGlobal()
    }
    changed(value)
}

::EUR.applyCustomAiIncome <- function(faction) {
    if (::EUR.options_first_run || faction == null || faction.isPlayerControlled != 0
        || faction.name == "slave" || faction.characterCount == 0) return
    local amount = ::EUR.game_options.ai_extra_gold
    if (amount <= 0) return
    // A turn grant avoids permanently changing kingsPurse: turning it off stops the grant.
    faction.money += amount.tointeger()
}
::events.on("FactionTurnStart", function(eventData) { ::EUR.applyCustomAiIncome(eventData.faction) })

// Settlements descr_strat deliberately starts on another faction's town plan (unique strat models,
// e.g. Minas Tirith on the norway plan). On M2EX, writing planFactionId re-stamps the strat model,
// so converting these while their starting owner still holds them strips the unique model.
// name -> starting owner. Generated from descr_strat (non-rebel owners only; 47 towns, regenerated 2026-10-14
// with a parser that also reads 'settlement ;comment' headers - the first pass missed 24 of them).
::EUR.startPlanOverrides <- {
    ["Anorien"] = "sicily",
    ["Arthedain"] = "barrow_wights",
    ["Belfalas"] = "sicily",
    ["Cair_Andros"] = "sicily",
    ["Caranost"] = "barrow_wights",
    ["Carn_Dum"] = "portugal",
    ["Celebrant"] = "ireland",
    ["Celondim"] = "denmark",
    ["Central_Mountains"] = "hre",
    ["Cirith_Ungol"] = "england",
    ["Dale"] = "scotland",
    ["East_Moria"] = "norway",
    ["Edhellond_Haven"] = "sicily",
    ["Ered_Luin"] = "hungary",
    ["Forlindon"] = "denmark",
    ["Forodwaith"] = "papal_states",
    ["Gorgoroth"] = "england",
    ["Harlindon"] = "denmark",
    ["Haudh_Nogbenn"] = "barrow_wights",
    ["Helms_Deep"] = "milan",
    ["Hollin"] = "hre",
    ["Imladris"] = "saxons",
    ["Iron_Hills"] = "moors",
    ["Kings_Land"] = "milan",
    ["Litash"] = "portugal",
    ["Lower_Anduin_Vale"] = "timurids",
    ["Lowest_Anduin_Vale"] = "timurids",
    ["Lune_North"] = "hungary",
    ["Metraith"] = "turks",
    ["Mithlond"] = "denmark",
    ["Morgai"] = "england",
    ["Morgul_Vale"] = "england",
    ["Mt_Gundabad"] = "gundabad",
    ["Nan_Curunir"] = "france",
    ["Nan_i_Naugrim"] = "hungary",
    ["Orc"] = "barrow_wights",
    ["Rhudaur"] = "saxons",
    ["Shire_South"] = "normans",
    ["Talsir"] = "teutonic_order",
    ["Tolfalas"] = "sicily",
    ["Trestlebridge"] = "turks",
    ["Udun"] = "england",
    ["Umbar"] = "russia",
    ["Weather_Hills"] = "turks",
    ["West_Moria"] = "hre",
    ["West_Osgiliath"] = "sicily",
    ["Wilderland"] = "poland",
}

// Towns whose look is repainted by the good/evil swap scripts in eurCasLoad. These may convert on
// conquest; every other custom-look town keeps its original plan for good.
::EUR.cultureSwapTowns <- {
    ["Anorien"] = true, ["East_Osgiliath"] = true, ["West_Osgiliath"] = true, ["Cair_Andros"] = true,
    ["Nan_Curunir"] = true, ["Morgul_Vale"] = true, ["Deep_Mirkwood"] = true, ["Helms_Deep"] = true,
    ["Celebrant"] = true,
}

::EUR.hasCustomLook <- function(name) {
    return (name in ::EUR.startPlanOverrides) || (name in ::EUR.strat_cas_setts)
}

::EUR.applyAutomaticCultureConversion <- function(settlement) {
    if (!::EUR.game_options.auto_culture_conversion || settlement == null) return
    local owner = settlement.owner
    if (owner == null || owner.name == "slave" || settlement.isMinorSettlement) return
    local name = settlement.name
    // Never convert a custom-look town while its starting owner still holds it.
    if ((name in ::EUR.startPlanOverrides) && ::EUR.startPlanOverrides[name] == owner.name) return
    // After conquest: only the good/evil swap towns convert; other custom-look towns never do.
    if (::EUR.hasCustomLook(name) && !(name in ::EUR.cultureSwapTowns)) return
    if (settlement.planFactionId != owner.id) settlement.planFactionId = owner.id
}
::events.on("SettlementTurnStart", function(eventData) {
    ::EUR.applyAutomaticCultureConversion(eventData.settlement)
})

::EUR.EUR_OPTION_TABS.append({
    title = "Customization",
    customization = true,
    sections = [
        [
            { text = "Changes are saved with this campaign." },
            { text = "Edit unit and bodyguard rosters in the Upgrades tab." },
            { label = "Forts and settlement appearance" },
            { check = "Constructable forts", bind = ["build_forts"],
              tip = "Allow new forts to be built. Disabling construction leaves existing forts in place.",
              onChange = function(v) { ::EUR.build_forts = v ? true : false; ::EUR.eurFortCreationToggle.sync(); changed(v) } },
            { check = "Automatic culture conversion", bind = ["game_options", "auto_culture_conversion"],
              tip = "Convert captured towns and castles to their owner's appearance at settlement turn start. Off preserves their current appearance. Previously converted settlements are not reverted; minor settlements are unchanged.", onChange = changed },
            { check = "Convert building artwork", bind = ["game_options", "convert_buildings"],
              tip = "Convert compatible building artwork to the owner's culture. Separate from town and castle models.", onChange = changed },
        ],
        [
            { sep = true }, { label = "Global recruitment" },
            { check = "Waystation required in settlement", bind = ["game_options", "global_waystation_req"],
              tip = "Require a Waystation at the receiving settlement for global recruits.", onChange = recruitmentChanged },
            { check = "Waystation increases global queue size", bind = ["game_options", "global_waystation_inc_max"],
              tip = "Use Waystations to expand the global queue. Off uses the configured maximum queue size.", onChange = recruitmentChanged },
        ],
        [
            { sep = true }, { label = "Faction revival" },
            { check = "Player revivals", bind = ["game_options", "player_revival"],
              tip = "Allow the player to revive defeated factions from their capitals.",
              onChange = function(v) {
                  if (!v) { ::EUR.show_revive_choice = false }
                  changed(v)
              } },
            { check = "AI revivals", bind = ["game_options", "airevive"],
              tip = "Allow defeated AI factions to revive when their capital is not owned by the player.", onChange = changed },
            { check = "Unlimited revivals", bind = ["game_options", "unlimited_revival"],
              tip = "Allow repeated revivals, including factions already revived once.", onChange = changed },
            { stepper = "Revival cost", bind = ["game_options", "revival_cost"], min = 1000, max = 50000, step = 1000,
              tip = "Gold paid for player revivals.", onChange = changed },
            { check = "Ignore disposition", bind = ["game_options", "revival_disposition_ignored"],
              tip = "Allow any faction alignment to revive another faction.",
              onChange = function(v) {
                  foreach (key, original in ::EUR.faction_disposition_default) {
                      ::EUR.faction_disposition[key] = v ? "neutral" : original
                  }
                  changed(v)
              } },
        ],
        [
            { sep = true }, { label = "Extra AI support" },
            { stepper = "Extra AI gold per turn", bind = ["game_options", "ai_extra_gold"], min = 0, max = 20000, step = 500,
              tip = "Give this much extra gold to each living AI faction at the start of its turn. Zero disables it. Excludes rebels and all human players. Available in every difficulty preset.", onChange = changed },
            { check = "Add generals to large AI armies", bind = ["options_general_large_army"],
              tip = "Allow EUR to give medium and large AI armies a general. Available independently of Legendary.", onChange = changed },
        ],
    ],
})
