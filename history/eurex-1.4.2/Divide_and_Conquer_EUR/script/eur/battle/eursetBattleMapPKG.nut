// Picks a custom battle-map package by the defender tile's coordinates.
// custom_maps is populated in eurCasLoad (keyed "x,y").
::EUR.onSelectWorldpkgdesc <- function(selectedRecord, selectedRecordGroup) {
    local battle = ::battle.current()
    if (battle == null) { return selectedRecord }

    local xCoord = battle.defenderX
    local yCoord = battle.defenderY
    if (xCoord == 0 || yCoord == 0) { return selectedRecord }

    local coordKey = xCoord + "," + yCoord
    if (coordKey in ::EUR.custom_maps) {
        selectedRecord = ::EUR.custom_maps[coordKey]
    }
    return selectedRecord
}

// Hotfix: the picker above was never registered with M2EX, so no custom
// battle map ever loaded. Hook it to the engine's selectWorldpkgdesc event.
::events.on("selectWorldpkgdesc", function(...) {
    local rec = vargv.len() > 0 ? vargv[0] : null
    local grp = vargv.len() > 1 ? vargv[1] : null
    local picked = rec
    try {
        picked = ::EUR.onSelectWorldpkgdesc(rec, grp)
        local b = ::battle.current()
        local where = b == null ? "?" : (b.defenderX + "," + b.defenderY)
        ::game.log("[EUR maps] tile " + where + " engine=" + rec + " group=" + grp + " -> " + picked)
    } catch (e) {
        ::game.log("[EUR maps] error: " + e)
        return null
    }
    return picked == rec ? null : picked
})
