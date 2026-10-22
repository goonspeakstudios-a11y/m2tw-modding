MOD = r"D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"
import shutil, os
def backup(rel, suffix):
    p = MOD + "/" + rel
    if not os.path.exists(p + suffix): shutil.copy2(p, p + suffix); print("backup", rel + suffix)
def edit(rel, pairs):
    path = MOD + "/" + rel
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    s = raw.decode("utf-8-sig").replace("\r\n", "\n")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:70], s.count(old))
        s = s.replace(old, new)
    out = s.replace("\n", "\r\n").encode("utf-8")
    if bom: out = b"\xef\xbb\xbf" + out
    open(path, "wb").write(out)
    print("edited", rel, "(%d edits)" % len(pairs))

backup("script/eur/eru/eurMapHelpers.nut", ".bak_15fix")
edit("script/eur/eru/eurMapHelpers.nut", [
 ('\t["134,386"] = "hobbiton_a",                //(Hobiton)\n',
  '\t["133,385"] = "hobbiton_a",                //(Hobiton) tile on the current map (was 134,386)\n'
  '\t["166,380"] = "bree_a",                    //(Bree) package tagged normans; town runs on the Bree_Folk plan, engine may ignore\n'),
 ('\t["eursett_15"] = 11,         //(Amon Hen)\n',
  '\t["Amon_Hen"] = 11,           //(Amon Hen) current settlement name\n'
  '\t["eursett_15"] = 11,         //(Amon Hen) old alias for older saves\n'),
])

backup("script/helper/eurCampaignTriggers.nut", ".bak_15fix")
edit("script/helper/eurCampaignTriggers.nut", [
 ('''    if (!::EUR.cas_standalone_set_already) {
        ::EUR.loadStratCAS()
        ::EUR.setCasStandalone()
        ::EUR.cas_standalone_set_already = true
    }
''',
  '''    // The M2EX script VM survives leaving a campaign, so a once-per-process guard left every
    // campaign after the first (load or new) with the engine's default city models (Bree etc.).
    // Stamp on every campaign boot; the model re-add is harmless when the models already exist.
    if (!::EUR.cas_standalone_set_already) {
        ::EUR.loadStratCAS()
        ::EUR.cas_standalone_set_already = true
    } else {
        try { ::EUR.loadStratCAS() } catch (e) { ::game.log("[EUR cas] model re-add skipped: " + e) }
    }
    ::EUR.setCasStandalone()
    try { ::game.log("[EUR cas] settlement models applied") } catch (e) {}
'''),
 ('''    ::EUR.eur_numberOfFactions = ::game.factionCount()
    ::EUR.eur_playerFactionId = ::game.localFactionId()
    ::EUR.eur_player_faction = ::game.localFaction()
    // Before anything can build a widget''',
  '''    ::EUR.eur_numberOfFactions = ::game.factionCount()
    ::EUR.eur_playerFactionId = ::game.localFactionId()
    ::EUR.eur_player_faction = ::game.localFaction()
    try { ::game.log("[EUR boot] campaignBoot start, first_run=" + ::EUR.options_first_run
        + " show_options=" + ::EUR.show_options_window + " cas_done=" + ::EUR.cas_standalone_set_already) } catch (e) {}
    // Before anything can build a widget'''),
 ('''    ::events.on("campaignMapLoaded", function() {
        ::EUR.campaignBoot()
    })
''',
  '''    ::events.on("campaignMapLoaded", function() {
        try { ::game.log("[EUR boot] campaignMapLoaded") } catch (e) {}
        ::EUR.campaignBoot()
        try { ::game.log("[EUR boot] campaignBoot done, in_map=" + ::EUR.in_campaign_map
            + " first_run=" + ::EUR.options_first_run + " show_options=" + ::EUR.show_options_window
            + " presets=" + ::EUR.campaignPresets.len()) } catch (e) {}
    })
'''),
 ('''    ::events.on("exitToMenu", function() {
        ::EUR.in_campaign_map = false
    })
''',
  '''    ::events.on("exitToMenu", function() {
        try { ::game.log("[EUR boot] exitToMenu") } catch (e) {}
        ::EUR.in_campaign_map = false
    })
'''),
 ('''    ::events.on("newGameStart", function() {
        if (!::EUR.options_first_run) {
''',
  '''    ::events.on("newGameStart", function() {
        try { ::game.log("[EUR boot] newGameStart, first_run=" + ::EUR.options_first_run) } catch (e) {}
        if (!::EUR.options_first_run) {
'''),
 ('''        ::EUR.preparePresetChoice()
        //::EUR.show_genenabled = true
''',
  '''        ::EUR.preparePresetChoice()
        try { ::game.log("[EUR boot] newGameLoaded: preset choice prepared") } catch (e) {}
        //::EUR.show_genenabled = true
'''),
 ('''    ::events.on("unloadCampaign", function() {
        if (::EUR.to_log) { println("EUR SCRIPT: " + "onUnloadCampaign") }
''',
  '''    ::events.on("unloadCampaign", function() {
        try { ::game.log("[EUR boot] unloadCampaign") } catch (e) {}
        if (::EUR.to_log) { println("EUR SCRIPT: " + "onUnloadCampaign") }
'''),
])

# Reclaiming Moria (Durin's Folk) southern route: Emyn_Nu_Fuin_Province is new on the 1.5 map and the
# step-2 pointer (327,392) lies inside it, but the clickable whitelists never name it -> "Restricted area".
CS = "data/world/maps/campaign/imperial_campaign/campaign_script.txt"
backup(CS, ".bak_moriaroute")
edit(CS, [
 ("restrict_clickable_area Central_Mirkwood_Province Elven_Mirkwood_Province Esgaroth_Province\n",
  "restrict_clickable_area Central_Mirkwood_Province Elven_Mirkwood_Province Esgaroth_Province Emyn_Nu_Fuin_Province\n"),
 ("restrict_clickable_area Central_Mirkwood_Province Middle_Mirkwood_Province Deep_Mirkwood_Province\n",
  "restrict_clickable_area Central_Mirkwood_Province Middle_Mirkwood_Province Deep_Mirkwood_Province Emyn_Nu_Fuin_Province Elven_Mirkwood_Province\n"),
 ("restrict_clickable_area Middle_Mirkwood_Province Central_Mirkwood_Province Central_Vale_Province Woodsmen_Province Deep_Mirkwood_Province\n",
  "restrict_clickable_area Middle_Mirkwood_Province Central_Mirkwood_Province Central_Vale_Province Woodsmen_Province Deep_Mirkwood_Province Emyn_Nu_Fuin_Province\n"),
])
