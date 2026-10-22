// Authoritative monster AOE configuration (metres): melee, missiles and fire breath.
// Native defaults, named attacks, projectiles and their secondary effects live here.
// Restart the game after editing. Debug changes only drawing, never damage or geometry.
// descr_monsters/EDU values remain engine defaults for units outside this table.
::EUR.monsterAbilities <- {
    debugAoeOutline = false,   // was true in 1.5: drew green debug outlines under monster area attacks

    // Native radial splash keeps its exponential damage/falloff/shape curve.
    // meleeArea, when present, replaces radial splash with an actor-relative shape.
    native = [
        {
            units = ["Sauron", "Giant Bats"],
            radius = 2.5, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Troll Drummers", "Cave Troll Drummers", "Trolls of the White Hand", "Troll Avengers", "Mordor Trolls", "Mirkwood Trolls", "Forest Trolls", "Trolls", "Black Trolls of Angmar", "Snow Trolls", "Olog-hai", "Crag Trolls", "Armoured Crag Trolls", "Blue Crag Troll Hurlers", "Cave Trolls", "Crag Trolls Garrison"],
            radius = 2, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Goblin King"],
            radius = 1.0, damage = 1, falloff = 3, shape = 1, meleeArea = "melee_aoe_sweep_0_13_65"
        },
        {
            units = ["Balrog"],
            radius = 1.1, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Moria Balrog", "Armored Balrog"],
            radius = 5, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Ents"],
            radius = 2, damage = 1, falloff = 1.3862943611, shape = 1.7382596216
        },
        {
            units = ["Giant Spiders"],
            radius = 2.2, damage = 1, falloff = 3, shape = 1, meleeArea = "melee_aoe_rect_0_4_2.2"
        },
        {
            units = ["Beorning Bears"],
            radius = 2.2, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Crag Siege Trolls"],
            radius = 1.0, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Mountain Giants", "Tom Bombadil"],
            radius = 0, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Giant Scorpions", "AOTR Ents", "Corrupted Entwives", "Snow Troll Stalkers", "AOTR Wild Hill Trolls", "AOTR Jungle Trolls", "AOTR Wild Snow Trolls", "AOTR Stone Trolls", "AOTR Hill Troll Banner Bearers", "AOTR Snow Troll Banner Bearers", "AOTR Angmar Hill Trolls", "AOTR Rogash", "AOTR Angmar Snow Trolls", "AOTR Angmar Troll Stone-Thrower", "AOTR Snow Troll Despoilers", "AOTR Gorg", "AOTR Undead Trolls", "AOTR Isengard Trolls", "AOTR Olog-hai", "AOTR Drummer Trolls", "AOTR Mollok", "AOTR Mountain Trolls", "AOTR Olog Reapers", "AOTR Gundabad Trolls", "AOTR Catapult Trolls", "AOTR Cave Trolls", "AOTR Moria Troll Stone-Thrower", "AOTR Snow Troll Spearmen", "AOTR Troll Destroyers", "AOTR Bert", "AOTR Tom", "AOTR William", "AOTR Troll Pack"],
            radius = 1.5, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Aragorn - Gondor Summon"],
            radius = 1.133999669, damage = 1.000000000, falloff = 0.000000000, shape = 1
        },
        {
            units = ["Aragorn - Imladris"],
            radius = 0.572023377, damage = 1.000000000, falloff = 0.000000000, shape = 1
        },
        {
            units = ["Dread Matriarch"],
            radius = 0.5, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Witch King - Angmar"],
            radius = 2.156563103, damage = 1.000000000, falloff = 0.000000000, shape = 1
        },
        {
            units = ["Witch King - Mordor"],
            radius = 2.277807282, damage = 1.000000000, falloff = 0.000000000, shape = 1
        },
        {
            units = ["AOTR Khamul", "AOTR Boromir", "AOTR Faramir"],
            radius = 0.000000000, damage = 1.000000000, falloff = 0.000000000, shape = 1
        },
        {
            units = ["Witch King on Fell Beast"],
            radius = 5.0, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Corrupted Mammoth"],
            radius = 1.5, damage = 1, falloff = 3, shape = 1, meleeArea = "melee_aoe_sweep_0_11.431121_15"
        },
        {
            units = ["Fire Drake"],
            radius = 1.8, damage = 1, falloff = 3, shape = 1
        },
        {
            units = ["Cold Drakes"],
            radius = 1.5, damage = 1, falloff = 3, shape = 1, meleeArea = "melee_aoe_sweep_0_6_85"
        },
    ],

    // Projectile damage radius and its separate impulse ring; effect values retain XML names.
    ranged = [
        {
            units = ["Goblin King"],
            projectiles = [{ name = "fart", radius = 3.0, blastScale = 1.35 }],
            effects = [{ name = "ae_cow_carcass", radius = 10.0, duration = 300, morale_max = 16 }],
        },
        {
            units = ["Moria Balrog"],
            projectiles = [{ name = "fireball", radius = 8, blastScale = 1.35 }],
            effects = [{ name = "fireball_area", impulse_radius = 50, impulse_force = 50, effective_radius = 3.0, effective_damage = 20.0, kill_radius = 3.0, kill_damage = 200.0, fiery = 1 }],
        },
        {
            units = ["Blue Crag Troll Hurlers"],
            projectiles = [{ name = "cragboulder", radius = 1.0, blastScale = 1.35 }],
        },
        {
            units = ["Crag Siege Trolls", "AOTR Angmar Troll Stone-Thrower", "AOTR Catapult Trolls", "AOTR Moria Troll Stone-Thrower"],
            projectiles = [{ name = "troll_rock", radius = 1.8, blastScale = 1.35 }],
            effects = [{ name = "troll_rock_shot", impulse_radius = 2.5, impulse_force = 250.0, effective_radius = 0.7, effective_damage = 1.0, kill_radius = 1.0, kill_damage = 100.0, fiery = 0 }],
        },
        {
            units = ["Mountain Giants"],
            projectiles = [{ name = "mountain_giant_boulder", radius = 4.5, blastScale = 1.35 }],
        },
        {
            units = ["AOTR Ents", "Corrupted Entwives"],
            // Their original weapon lacks the area attribute: retain single-target impacts.
            // Set a positive radius here to enable splash without editing the EDU.
            projectiles = [{ name = "aotr_ent_boulder", radius = 0.0, blastScale = 1.35 }],
        },
        {
            units = ["Aragorn - Imladris", "AOTR Faramir"],
            projectiles = [{ name = "elven_ranger_arrow", radius = 0, blastScale = 1.35 }],
        },
        {
            units = ["Snow Troll Stalkers"],
            projectiles = [{ name = "snow_troll_stalker_arrow", radius = 0, blastScale = 1.35 }],
        },
        {
            units = ["Fire Drake"],
            projectiles = [{ name = "aotr_drake_fire", radius = 3, blastScale = 1.35 }],
            breath = { radius = 9.75, arc = 90, height = 1.3, speed = 26, duration = 1.4, cooldown = 10 },
        },
    ],

    // Engine fallback actions used by monsters without authored direct-control attacks.
    core = [
        { id = "core:monster_lunge", splashRadius = 2.5, splashBodyScale = 0.5, splashFalloff = 1.25, splashOrigin = "impact", splashForwardScale = 0.45 },
        { id = "core:monster_sweep", splashRadius = 3.5, splashBodyScale = 1.0, splashFalloff = 0.75, splashOrigin = "actor", splashForwardScale = 0.0 },
        { id = "core:monster_smash", splashRadius = 3.0, splashBodyScale = 0.75, splashFalloff = 1.0, splashOrigin = "impact", splashForwardScale = 0.0 }
    ],

    // Per-animation overrides. Animation modules reference these entries.
    areas = {
        balrog_sword_sweep = { meleeArea = "melee_aoe_sweep_0_3_70" },
        moria_balrog_sword_sweep = { meleeArea = "melee_aoe_sweep_0_7_70" },
        armored_balrog_sword_sweep = { meleeArea = "melee_aoe_sweep_0_5.5_70" },
        sauron_mace_sweep = { meleeArea = "melee_aoe_sweep_0.5_4_75" },
        sauron_mace_backswing = { meleeArea = "melee_aoe_sweep_0.5_4_75" },
        sauron_high_mace_sweep = { meleeArea = "melee_aoe_sweep_0.5_7_35" },
        goblin_king_royal_cleave = { meleeArea = "melee_aoe_sweep_0_3_65" },
        goblin_king_crushing_kick = { meleeArea = "melee_aoe_pierce_3_0.9" },
        ent_branch_sweep = { meleeArea = "melee_aoe_sweep_0.5_4.5_80" },
        ent_overhead_crush = { meleeArea = "melee_aoe_rect_0.5_5_1.5" },
        ent_driving_punch = { meleeArea = "melee_aoe_pierce_4.5_1.25" },
        rock_troll_sweep = { meleeArea = "melee_aoe_sweep_0.5_3.5_70" },
        rock_troll_overhead_crush = { meleeArea = "melee_aoe_rect_0.5_4_1" },
        rock_troll_driving_thrust = { meleeArea = "melee_aoe_pierce_3.5_1" },
        siege_troll_kick = { meleeArea = "melee_aoe_pierce_3.5_1" },
        giant_spider_bite = { meleeArea = "melee_aoe_rect_0_4_2.2" },
        troll_mace_sweep = { meleeArea = "melee_aoe_sweep_0.5_3.5_70" },
        troll_overhead_slam = { meleeArea = "melee_aoe_rect_0.5_4_1" },
        troll_driving_punch = { meleeArea = "melee_aoe_pierce_3.5_1" },
        giant_right_kick = { meleeArea = "melee_aoe_pierce_5_1.5" },
        giant_left_kick = { meleeArea = "melee_aoe_rect_0.5_5_1.6" },
        giant_stomp = { meleeArea = "melee_aoe_circle_0_5" },
        cold_drake_strike = { meleeArea = "melee_aoe_sweep_0_6_85" },
        cold_drake_sweep = { meleeArea = "melee_aoe_sweep_0_6_100" },
        bombadil_punch = { meleeArea = "melee_aoe_sweep_0_2.4_45" },
        aragorn_gondor = { splashRadius = 1.1339996687390586, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target" },
        aragorn_imladris = { splashRadius = 0.5720233768224716, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target" },
        witch_king_angmar = { splashRadius = 2.156563103199005, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target" },
        witch_king_mordor = { splashRadius = 2.2778072817759076, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target" },
        khamul = { splashRadius = 0.0, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target" },
        giant_bats = { meleeArea = "melee_aoe_circle_0_2.5" },
        witch_king_fellbeast = { meleeArea = "melee_aoe_circle_0_5" },
        corrupted_mammoth = { meleeArea = "melee_aoe_sweep_0_11.431121_15" },
        boromir = { splashRadius = 1.25, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target", splashNonlethal = true },
        faramir = { splashRadius = 0.0, splashFalloff = 0.0, splashBodyScale = 0.0, splashOrigin = "target" },
        no_splash = { splashRadius = 0.0 },
        drake_fire = { splashRadius = 0.0, splashFalloff = 0.0, splashBodyScale = 0.0 },
    }
};

// Merge before registering/cloning so AI and direct-control copies share identical AOE.
::EUR.monsterAbilities.withArea <- function(key, definition) {
    if (!(key in this.areas)) throw "Unknown monster AOE configuration: " + key;
    local result = clone definition;
    foreach (field, value in this.areas[key]) result[field] <- value;
    return result;
};

// The engine applies native defaults and draws the actual resolved shapes/radii.
// Fail explicitly on an old engine instead of silently giving partial debug coverage.
::animations.configureMonsterAoe(::EUR.monsterAbilities.native, ::EUR.monsterAbilities.core,
    ::EUR.monsterAbilities.ranged, ::EUR.monsterAbilities.debugAoeOutline);
