# Item Section Names

Every spawnable item in Anomaly has a **section name** — the key used to identify it in LTX configs,
`alife_create_item`, `alife_create`, and inventory lookups. This page lists all 1,030 spawnable
sections from Anomaly 1.5.3, grouped by category.

Section names are verified by the presence of a `$spawn` key in the configs under
`configs/items/items/`, `configs/items/weapons/`, and `configs/items/outfits/`.

---

## Using section names

```lua
-- Spawn an item at the player's position
local pos  = db.actor:position()
local lvid = db.actor:level_vertex_id()
local gvid = db.actor:game_vertex_id()
alife_create_item("medkit_army", db.actor, {pos=pos, lvid=lvid, gvid=gvid})

-- Check what section an object belongs to
local function actor_on_item_take(obj)
    if obj:section() == "af_gravi" then
        -- player picked up a Gravi artifact
    end
end
```

---

## Weapons

### Rifles and SMGs

Sections with `weapon_class = assault_rifle` in the configs.

| Section | Notes |
|---------|-------|
| `wpn_9a91` | 9A-91 compact assault rifle (9x39) |
| `wpn_abakan` | AN-94 Abakan |
| `wpn_aek` | AEK-971 |
| `wpn_ak` | AK (generic base) |
| `wpn_ak101` | AK-101 (5.56x45) |
| `wpn_ak102` | AK-102 (5.56x45) |
| `wpn_ak103` | AK-103 (7.62x39) |
| `wpn_ak104` | AK-104 (7.62x39) |
| `wpn_ak105` | AK-105 (5.45x39) |
| `wpn_ak12` | AK-12 |
| `wpn_ak74` | AK-74 |
| `wpn_ak74m` | AK-74M |
| `wpn_ak74u` | AKS-74U |
| `wpn_akm` | AKM (7.62x39) |
| `wpn_aks74` | AKS-74 |
| `wpn_ash12` | ASh-12.7 (12.7x55) |
| `wpn_aug` | AUG A1 |
| `wpn_aug_a3` | AUG A3 |
| `wpn_bizon` | PP-19 Bizon (9x18) |
| `wpn_fal` | FN FAL (7.62x51) |
| `wpn_famas3` | FAMAS G2 (5.56x45) |
| `wpn_fn2000` | FN F2000 (5.56x45) |
| `wpn_fnc` | FNC (5.56x45) |
| `wpn_g36` | G36 (5.56x45) |
| `wpn_g3sg1` | G3SG1 (7.62x51) |
| `wpn_g43` | Gewehr 43 (7.62x54, WW2) |
| `wpn_galil` | Galil (5.56x45) |
| `wpn_groza` | OTs-14 Groza (9x39) |
| `wpn_hk416` | HK416 (5.56x45) |
| `wpn_hk417` | HK417 (7.62x51) |
| `wpn_k98` | Karabiner 98k (7.62x54, WW2) |
| `wpn_kiparis` | PP-01 Kiparis (9x18) |
| `wpn_l85` | L85A2 (5.56x45) |
| `wpn_lr300` | LR-300 (5.56x45) |
| `wpn_m16` | M16A4 (5.56x45) |
| `wpn_m4` | M4 Carbine (5.56x45) |
| `wpn_m4a1` | M4A1 (5.56x45) |
| `wpn_m60` | M60 LMG (7.62x51) |
| `wpn_mk14` | Mk 14 EBR (7.62x51) |
| `wpn_mp5` | MP5 (9x19) |
| `wpn_mp7` | MP7 (4.6x30) |
| `wpn_oc33` | OTs-33 Pernach (9x18) |
| `wpn_p90` | FN P90 (5.7x28) |
| `wpn_pkm` | PKM LMG (7.62x54) |
| `wpn_pp2000` | PP-2000 (9x19) |
| `wpn_ppsh41` | PPSh-41 (7.62x25, WW2) |
| `wpn_rpd` | RPD LMG (7.62x39) |
| `wpn_rpk` | RPK LMG (7.62x39) |
| `wpn_scar` | FN SCAR (7.62x51) |
| `wpn_sig550` | SG 550 (5.56x45) |
| `wpn_sig552` | SG 552 (5.56x45) |
| `wpn_sr25` | SR-25 (7.62x51) |
| `wpn_ump45` | UMP45 (.45 ACP) |
| `wpn_val` | AS Val (9x39) |
| `wpn_vihr` | PP-19-01 Vityaz (9x19) — see also `wpn_vityaz` |
| `wpn_vityaz` | PP-19-01 Vityaz variant |
| `wpn_vsk94` | VSK-94 (9x39) |
| `wpn_vz61` | Vz. 61 Skorpion (7.62x25) |
| `wpn_xm8` | XM8 (5.56x45) |

### Shotguns

Sections with `weapon_class = shotgun`.

| Section | Notes |
|---------|-------|
| `wpn_bm16` | IZh-58 double-barrel (12x70) |
| `wpn_fort500` | Fort-500 pump-action (12x70) |
| `wpn_mossberg590` | Mossberg 590 (12x70) |
| `wpn_mp133` | MP-133 (12x70) |
| `wpn_mp153` | MP-153 semi-auto (12x70) |
| `wpn_protecta` | Armsel Protecta revolver shotgun (12x70) |
| `wpn_remington870` | Remington 870 (12x70) |
| `wpn_saiga12s` | Saiga-12S semi-auto (12x70) |
| `wpn_spas12` | SPAS-12 (12x70) |
| `wpn_toz34` | TOZ-34 double-barrel (12x70) |
| `wpn_usas12` | USAS-12 semi-auto (12x76) |
| `wpn_vepr` | Vepr-12 semi-auto (12x70) |
| `wpn_wincheaster1300` | Winchester 1300 (12x70) |

### Sniper Rifles

Sections with `weapon_class = sniper_rifle`.

| Section | Notes |
|---------|-------|
| `wpn_gauss` | Gauss rifle (special ammo) |
| `wpn_l96a1` | L96A1 (7.62x51) |
| `wpn_m24` | M24 SWS (7.62x51) |
| `wpn_m82` | M82 Barrett (12.7x55) |
| `wpn_m98b` | M98B (12.7x55) |
| `wpn_mosin` | Mosin-Nagant (7.62x54, WW2) |
| `wpn_remington700` | Remington 700 (7.62x51) |
| `wpn_sv98` | SV-98 (7.62x54) |
| `wpn_svd` | SVD Dragunov (7.62x54) |
| `wpn_svt40` | SVT-40 semi-auto (7.62x54, WW2) |
| `wpn_svu` | SVU bullpup Dragunov (7.62x54) |
| `wpn_trg` | TRG-42 (7.62x51) |
| `wpn_vintorez` | VSS Vintorez (9x39) |
| `wpn_vssk` | VSSK Vychlop (12.7x55) |
| `wpn_wa2000` | Walther WA 2000 (7.62x51) |

### Heavy Weapons and Launchers

Sections with `weapon_class = heavy_weapon` or standalone launcher C++ class.

| Section | Notes |
|---------|-------|
| `wpn_m249` | M249 SAW LMG (5.56x45) |
| `wpn_m79` | M79 grenade launcher (40mm) |
| `wpn_rg-6` | RG-6 revolver launcher (VOG-25) |
| `wpn_rpg7` | RPG-7 rocket launcher (OG-7B) |

### Pistols

| Section | Notes |
|---------|-------|
| `wpn_aps` | Stechkin APS (9x18) |
| `wpn_beretta` | Beretta 92 (9x19) |
| `wpn_colt1911` | Colt 1911 (.45 ACP) |
| `wpn_cz52` | CZ 52 (7.62x25) |
| `wpn_cz75` | CZ 75 (9x19) |
| `wpn_desert_eagle` | Desert Eagle (.357 Magnum) |
| `wpn_fn57` | FN Five-seveN (5.7x28) |
| `wpn_fnp45` | FNP-45 (.45 ACP) |
| `wpn_fort` | Fort-12 (9x18) |
| `wpn_glock` | Glock 17 (9x19) |
| `wpn_gsh18` | GSh-18 (9x19) |
| `wpn_hpsa` | Browning HP (9x19) |
| `wpn_mp412` | MP-412 REX revolver (.357 Magnum) |
| `wpn_mp443` | MP-443 Grach (9x19) |
| `wpn_pb` | PB suppressed pistol (9x18) |
| `wpn_pm` | Makarov PM (9x18) |
| `wpn_sig220` | SIG P220 (.45 ACP) |
| `wpn_tt33` | Tokarev TT-33 (7.62x25) |
| `wpn_usp` | HK USP (.45 ACP) |
| `wpn_walther` | Walther P99 (9x19) |

### Melee

| Section | Notes |
|---------|-------|
| `wpn_knife` | Combat knife |
| `wpn_knife2` | Hunting knife |
| `wpn_knife3` | Machete |
| `wpn_knife4` | Cleaver |
| `wpn_knife5` | Kukri |
| `wpn_axe` | Fire axe |

### Weapon Attachments

Standalone attachment items that can be added to compatible weapons.

| Section | Notes |
|---------|-------|
| `wpn_addon_grenade_launcher` | GP-25 underbarrel launcher |
| `wpn_addon_grenade_launcher_m203` | M203 underbarrel launcher |
| `wpn_addon_silencer` | Universal suppressor |
| `wpn_addon_scope` | Iron sights / basic scope |
| `wpn_addon_scope_acog` | ACOG 4x scope |
| `wpn_addon_scope_acog_night` | ACOG night scope |
| `wpn_addon_scope_acog_trijicon` | Trijicon ACOG |
| `wpn_addon_scope_detector` | Detector scope |
| `wpn_addon_scope_g43` | Gewehr 43 scope |
| `wpn_addon_scope_galil` | Galil scope |
| `wpn_addon_scope_m24` | M24 scope |
| `wpn_addon_scope_moist` | Weathered scope |
| `wpn_addon_scope_mosin` | Mosin PU scope |
| `wpn_addon_scope_night` | Night vision scope |
| `wpn_addon_scope_po4x34` | PO 4x34 scope |
| `wpn_addon_scope_pu` | PU 3.5x scope (WW2) |
| `wpn_addon_scope_susat` | SUSAT 4x scope |
| `wpn_addon_scope_susat_custom` | SUSAT custom variant |
| `wpn_addon_scope_susat_dusk` | SUSAT dusk variant |
| `wpn_addon_scope_susat_moist` | SUSAT weathered |
| `wpn_addon_scope_susat_night` | SUSAT night |
| `wpn_addon_scope_susat_worn` | SUSAT worn |
| `wpn_addon_scope_susat_x1.6` | SUSAT 1.6x |
| `wpn_addon_scope_sv98` | SV-98 scope |
| `wpn_addon_scope_vsk` | VSK scope |
| `wpn_addon_scope_worn` | Worn generic scope |
| `wpn_addon_scope_ww2` | WW2 scope |
| `wpn_addon_scope_ww2_moist` | WW2 scope weathered |
| `wpn_addon_scope_ww2_worn` | WW2 scope worn |
| `wpn_addon_scope_x2.7` | 2.7x scope |
| `wpn_addon_scope_zf4` | ZF 4 scope (WW2) |
| `wpn_addon_scope_zf4_moist` | ZF 4 weathered |
| `wpn_addon_scope_zf4_worn` | ZF 4 worn |

### Preset Variants

These sections are pre-configured weapon variants — either pre-upgraded ("nimble") or
shipped with a specific scope attached. They use the same underlying weapon stats but
start with a different condition or loadout. Spawn them the same way as the base weapon.

**Nimble (pre-upgraded) variants:**
`wpn_desert_eagle_nimble`, `wpn_fn2000_nimble`, `wpn_g36_nimble`, `wpn_groza_nimble`,
`wpn_mp5_nimble`, `wpn_protecta_nimble`, `wpn_sig220_nimble`, `wpn_spas12_nimble`,
`wpn_svd_nimble`, `wpn_svu_nimble`, `wpn_usp_nimble`, `wpn_vintorez_nimble`

**Scoped/configured variants:**
`wpn_ak74u_snag`, `wpn_ash12_ac10632`, `wpn_ash12_acog`, `wpn_ash12_c-more`,
`wpn_ash12_eot`, `wpn_aug_a3_ac10632`, `wpn_aug_a3_acog`, `wpn_aug_a3_c-more`,
`wpn_aug_a3_eot`, `wpn_fal_ac10632`, `wpn_fal_acog`, `wpn_fal_c-more`, `wpn_fal_eot`,
`wpn_famas3_eot`, `wpn_fort_snag`, `wpn_mk14_ac10632`, `wpn_mk14_acog`,
`wpn_mk14_c-more`, `wpn_mk14_eot`, `wpn_pkm_zulus`, `wpn_remington870_ac10632`,
`wpn_remington870_c-more`, `wpn_remington870_eot`, `wpn_sig550_luckygun`,
`wpn_wincheaster1300_trapper`

---

## Ammunition

Each base calibre has `_fmj`/`_ap`/`_hp` grade variants. Every grade also has `_bad`
(worn) and `_verybad` (nearly spent) quality suffixes — e.g. `ammo_5.45x39_fmj_bad`.
The table below lists only the base-quality sections; append `_bad` or `_verybad` as
needed.

| Calibre | Sections |
|---------|---------|
| 5.45×39 | `ammo_5.45x39_fmj`, `ammo_5.45x39_ap`, `ammo_5.45x39_ep` |
| 5.56×45 | `ammo_5.56x45_fmj`, `ammo_5.56x45_ap`, `ammo_5.56x45_ss190` |
| 5.7×28 | `ammo_5.7x28_ss190`, `ammo_5.7x28_ss195` |
| 4.6×30 | `ammo_4.6x30_fmj` |
| 7.62×25 | `ammo_7.62x25_p`, `ammo_7.62x25_ps` |
| 7.62×39 | *(loaded from weapons via magazine; use 5.45×39 sections for AKM family unless a mod adds explicit 7.62x39 ammo)* |
| 7.62×51 | `ammo_7.62x51_fmj`, `ammo_7.62x51_ap` |
| 7.62×54 | `ammo_7.62x54_7h1`, `ammo_7.62x54_7h14`, `ammo_7.62x54_ap` |
| 9×18 | `ammo_9x18_fmj`, `ammo_9x18_ap`, `ammo_9x18_pmm` |
| 9×19 | `ammo_9x19_fmj`, `ammo_9x19_ap`, `ammo_9x19_pbp` |
| 9×39 | `ammo_9x39_pab9`, `ammo_9x39_ap` |
| .45 ACP (11.43×23) | `ammo_11.43x23_fmj`, `ammo_11.43x23_hydro` |
| .357 Magnum | `ammo_357_hp_mag`, `ammo_magnum_300` |
| 12.7×55 | `ammo_12.7x55_fmj`, `ammo_12.7x55_ap` |
| .50 BMG | `ammo_50_bmg` |
| 12×70 (buckshot) | `ammo_12x70_buck`, `ammo_12x70_buck_self` |
| 12×76 (slug) | `ammo_12x76_zhekan`, `ammo_12x76_dart`, `ammo_12x76_bull` |
| 40mm grenade | `ammo_m209`, `ammo_vog-25` |
| Rocket | `ammo_og-7b` |
| Gauss cell | `ammo_gauss`, `ammo_gauss_cardan` |
| PKM belt | `ammo_pkm_100` |
| Batteries | `ammo_batteries`, `ammo_batteries_ccell`, `ammo_batteries_dead` |

---

## Armour

### Suits

=== "Loner / Stalker"
    `novice_outfit`, `novice_outfit_camo`, `novice_outfit_tourist`,
    `stalker_outfit`, `stalker_autumn_outfit`, `stalker_bear_outfit`,
    `stalker_drought_outfit`, `stalker_graphite_outfit`, `stalker_predator_outfit`,
    `stalker_proto_exo_outfit`, `stalker_salamander_outfit`, `stalker_tigerstripe_outfit`,
    `light_loner_outfit`, `travel_outfit`, `hybrid_outfit`, `ghillie_outfit`,
    `trenchcoat_outfit`, `trenchcoat_brown_outfit`, `trenchcoat_green_outfit`

=== "Military"
    `army_outfit`, `army_nosorog_outfit`, `military_outfit`, `military_exo_outfit`,
    `military_exolight_outfit`, `military_freedom_outfit`, `military_merc_outfit`,
    `military_monolit_outfit`, `military_proto_exo_outfit`, `military_sky_outfit`,
    `military_bandit_outfit`, `specops_outfit`

=== "Duty"
    `dolg_novice_outfit`, `dolg_outfit`, `dolg_voin_outfit`, `dolg_scout_outfit`,
    `dolg_heavy_outfit`, `dolg_red_outfit`, `dolg_scientific_outfit`,
    `dolg_exo_outfit`, `dolg_exolight_outfit`, `dolg_nosorog_outfit`,
    `dolg_proto_exo_outfit`, `dolg_heavy_proto_exo_outfit`,
    `dolg_specops_red_outfit`, `light_dolg_outfit`,
    `dolg_heavy_redline_outfit`, `dolg_scientific_red_outfit`,
    `dolg_scientific_wood_outfit`, `dolg_pantsir_outfit`,
    `nbc_dolg_outfit`, `specops_dolg_outfit`

=== "Freedom"
    `svoboda_novice_outfit`, `svoboda_light_outfit`, `svoboda_heavy_outfit`,
    `svoboda_heavy_outfit_2`, `svoboda_scientific_outfit`, `svoboda_exo_outfit`,
    `svoboda_exolight_outfit`, `svoboda_light_proto_exo_outfit`,
    `freedom_nosorog_outfit`, `freedom_exo_vineleaf_outfit`,
    `light_freedom_outfit`, `nbc_freedom_outfit`, `military_freedom_outfit`

=== "Bandit / Mercenary"
    `bandit_novice_outfit`, `bandit_novice_outfit_alt`, `bandit_sun_outfit`,
    `bandit_scientific_outfit`, `bandit_scientific_dark_outfit`,
    `bandit_nbc_outfit`, `bandit_ps5_outfit`, `bandit_exo_outfit`,
    `bandit_exolight_outfit`, `banditmerc_outfit`,
    `merc_outfit`, `merc_scout_outfit`, `merc_fighter_outfit`,
    `merc_scientific_outfit`, `merc_sun_outfit`, `merc_exo_outfit`,
    `merc_exolight_outfit`, `merc_nosorog_outfit`, `light_merc_outfit`,
    `nbc_merc_outfit`, `specops_merc_outfit`,
    `merc_ace_outfit`, `merc_coyote_outfit`, `merc_jackal_outfit`,
    `merc_nighthunter_outfit`, `merc_wolven_outfit`, `merc_sunset_outfit`,
    `merc_combat_scientific_outfit`, `merc_scientific_armored_outfit`,
    `renegade_scientific_outfit`, `renegademerc_outfit`,
    `exo_merc_grass_outfit`, `exo_merc_urban_outfit`, `exo_merc_wood_outfit`

=== "Ecologist / Scientific"
    `scientific_outfit`, `ecolog_outfit_blue`, `ecolog_outfit_green`,
    `ecolog_outfit_orange`, `ecolog_outfit_red`, `ecolog_outfit_white`,
    `ecolog_outfit_yello`, `ecolog_guard_outfit`, `ecolog_exo_outfit`,
    `ecolog_proto_exo_outfit`, `nbc_outfit`

=== "Clear Sky"
    `cs_novice_outfit`, `cs_light_novice_outfit`, `cs_light_outfit`,
    `cs_medium_outfit`, `cs_heavy_outfit`, `cs_stalker_outfit`,
    `cs_scientific_outfit`, `cs_scientific_outfit_good`, `cs_nbc_outfit`,
    `cs_exo_outfit`, `cs_exolight_outfit`, `cs_stalker_proto_exo_outfit`

=== "Monolith"
    `monolith_outfit`, `monolith_nbc_outfit`, `monolith_trenchcoat_outfit`,
    `monolith_scientific_outfit`, `monolith_scientific_light_outfit`,
    `monolith_exo_outfit`, `monolith_exolight_outfit`,
    `monolith_nosorog_outfit`, `monolith_proto_exo_outfit`,
    `light_monolit_outfit`

=== "ISG / Other factions"
    `isg_outfit`, `isg_camo_outfit`, `isg_lcs_outfit`, `isg_lcs_camo_outfit`,
    `isg_lcs_urban_outfit`, `isg_scientific_outfit`, `isg_exo_outfit`,
    `isg_exolight_outfit`, `isg_nosorog_outfit`, `isg_proto_exo_outfit`,
    `light_isg_outfit`,
    `greh_armored_outfit`, `greh_armored_camo_outfit`, `greh_trenchcoat_outfit`,
    `greh_exo_outfit`, `greh_ps5_outfit`,
    `nomad_outfit`, `wastelander_outfit`, `redline_novice_outfit`,
    `exo_outfit`, `exolight_outfit`, `exo_wood_outfit`,
    `exo_dolg_outfit`, `exo_dolg_red_outfit`, `exo_dolg_urban_outfit`,
    `exo_dolg_wood_outfit`

### Helmets

| Section | Notes |
|---------|-------|
| `helm_bandana` | Bandana |
| `helm_cloth_mask` | Cloth mask |
| `helm_resp` | Basic respirator |
| `helm_respirator` | Full respirator |
| `helm_respirator_gp5` | GP-5 gas mask |
| `helm_respirator_old` | Worn gas mask |
| `helm_rp_bala` | Balaclava |
| `helm_hardhat` | Hard hat |
| `helm_hardhat_snag` | Hard hat variant |
| `helm_tactic` | Tactical helmet |
| `helm_battle` | Battle helmet |
| `helm_ranger` | Ranger helmet |
| `helm_spartan` | Spartan helmet |
| `helm_m40` | M40 gas mask |
| `helm_m50` | M50 gas mask |
| `helm_metro` | Metro gas mask |
| `helm_ppm88` | PPM-88 |
| `helm_protective` | Protective helmet |
| `helm_ach7` | ACH-7 ballistic helmet |
| `helm_ach7ex` | ACH-7 extended |
| `helm_exo` | Exoskeleton helmet |

---

## Artefacts

All artefact sections use the `af_` prefix.

| Section | Notes |
|---------|-------|
| `af_aac` | |
| `af_aam` | |
| `af_atom` | Atom |
| `af_ball` | Ball of Fire |
| `af_baloon` | Balloon |
| `af_bat` | Bat |
| `af_black` | Black |
| `af_black_angel` | Black Angel |
| `af_black_spray` | Black Spray |
| `af_blood` | Blood |
| `af_bracelet` | Bracelet |
| `af_camelbak` | Camelbak |
| `af_camelbak_up` | Camelbak (upgraded) |
| `af_cell` | Cell |
| `af_chelust` | |
| `af_cocoon` | Cocoon |
| `af_compass` | Compass |
| `af_cooler` | Cooler |
| `af_cooler_up` | Cooler (upgraded) |
| `af_cristall` | Crystal |
| `af_cristall_flower` | Crystal Flower |
| `af_death_lamp` | Death Lamp |
| `af_dragon_eye` | Dragon Eye |
| `af_dummy_battery` | Battery (generic) |
| `af_dummy_dummy` | Dummy |
| `af_dummy_glassbeads` | Glass Beads |
| `af_ear` | Ear |
| `af_electra_flash` | Electra Flash |
| `af_electra_moonlight` | Electra Moonlight |
| `af_electra_sparkler` | Electra Sparkler |
| `af_elektron` | Elektron |
| `af_empty` | Empty artefact |
| `af_eye` | Eye |
| `af_fire` | Fire |
| `af_fire_loop` | Fire Loop |
| `af_fireball` | Fireball |
| `af_fonar` | Flashlight |
| `af_fountain` | Fountain |
| `af_frames` | Frames |
| `af_frames_up` | Frames (upgraded) |
| `af_freon` | Freon |
| `af_freon_up` | Freon (upgraded) |
| `af_fuzz_kolobok` | Fuzz Kolobok |
| `af_geliy` | Geliy |
| `af_generator` | Generator |
| `af_gimlet` | Gimlet |
| `af_glass` | Glass |
| `af_gold_fish` | Gold Fish |
| `af_grapes` | Grapes |
| `af_gravi` | Gravi |
| `af_grid` | Grid |
| `af_grid_up` | Grid (upgraded) |
| `af_iam` | |
| `af_ice` | Ice |
| `af_itcher` | Itcher |
| `af_kevlar` | Kevlar |
| `af_kevlar_up` | Kevlar (upgraded) |
| `af_kislushka` | |
| `af_kogot` | Claw |
| `af_lighthouse` | Lighthouse |
| `af_lobster_eyes` | Lobster Eyes |
| `af_medallion` | Medallion |
| `af_medusa` | Medusa |
| `af_mincer_meat` | Mincer Meat |
| `af_misery_bread` | Bread |
| `af_moh` | Moh |
| `af_monolith` | Monolith |
| `af_night_star` | Night Star |
| `af_oasis_heart` | Oasis Heart |
| `af_peas` | Peas |
| `af_pin` | Pin |
| `af_plates` | Plates |
| `af_plates_up` | Plates (upgraded) |
| `af_quest_b14_twisted` | Twisted (quest) |
| `af_repei` | Repei |
| `af_ring` | Ring |
| `af_sandstone` | Sandstone |
| `af_serofim` | Serofim |
| `af_signet` | Signet |
| `af_skull_miser` | Skull Miser |
| `af_soul` | Soul |
| `af_spaika` | Spaika |
| `af_sponge` | Sponge |
| `af_star_phantom` | Star Phantom |
| `af_sun` | Sun |
| `af_surge` | Surge |
| `af_surge_up` | Surge (upgraded) |
| `af_tapeworm` | Tapeworm |
| `af_vaselisk` | |
| `af_vyvert` | Vyvert |
| `af_zhelch` | |
| `af_ameba_mica` | Ameba Mica |
| `af_ameba_slime` | Ameba Slime |
| `af_ameba_slug` | Ameba Slug |
| `af_drops` | Drops |
| `af_dummy_pellicle` | Pellicle |
| `af_dummy_spring` | Spring |
| `af_full_empty` | Full Empty |
| `af_rusty_kristall` | Rusty Crystal |
| `af_rusty_sea` | Rusty Sea |
| `af_rusty_thorn` | Rusty Thorn |

### Mutant hides (artefact category)

| Section | Notes |
|---------|-------|
| `hide_bloodsucker` | Bloodsucker hide |
| `hide_boar` | Boar hide |
| `hide_burer` | Burer hide |
| `hide_chimera` | Chimera hide |
| `hide_controller` | Controller hide |
| `hide_flesh` | Flesh hide |
| `hide_lurker` | Lurker hide |
| `hide_pseudodog` | Pseudodog hide |
| `hide_pseudogiant` | Pseudogiant hide |
| `hide_psy_dog` | Psy-dog hide |
| `hide_psysucker` | Psysucker hide |
| `fieldcraft_plate_attch` | Fieldcraft plate attachment |

---

## Medical and Consumables

### Medical

| Section | Notes |
|---------|-------|
| `medkit` | Standard medkit |
| `medkit_army` | Army medkit |
| `medkit_scientic` | Scientific medkit |
| `medkit_ai1` | AI medkit tier 1 |
| `medkit_ai2` | AI medkit tier 2 |
| `medkit_ai3` | AI medkit tier 3 |
| `bandage` | Bandage |
| `survival_kit` | Survival kit |
| `stimpack` | Stimpack |
| `stimpack_army` | Army stimpack |
| `stimpack_scientic` | Scientific stimpack |
| `antirad` | Antirad |
| `antirad_cystamine` | Antirad (cystamine) |
| `antirad_kalium` | Antirad (potassium iodide) |
| `drug_radioprotector` | Radioprotector |
| `drug_anabiotic` | Anabiotic (used for emissions) |
| `drug_antidot` | Antidote |
| `drug_booster` | Booster |
| `drug_coagulant` | Coagulant |
| `drug_psy_blockade` | Psy blockade |
| `drug_sleepingpills` | Sleeping pills |
| `analgetic` | Analgesic |
| `adrenalin` | Adrenaline |
| `antibio_chlor` | Antibiotic (chloramphenicol) |
| `antibio_sulfad` | Antibiotic (sulfadiazine) |
| `antiemetic` | Antiemetic |
| `akvatab` | Purification tablet |
| `caffeine` | Caffeine |
| `glucose` | Glucose |
| `glucose_s` | Glucose shot |
| `morphine` | Morphine |
| `rebirth` | Rebirth |
| `tetanus` | Tetanus shot |
| `yadylin` | |

### Food and Drink

| Section | Notes |
|---------|-------|
| `vodka` | Vodka |
| `vodka2` | Vodka variant |
| `vodka_quality` | Quality vodka |
| `beer` | Beer |
| `energy_drink` | Energy drink |
| `mineral_water` | Mineral water |
| `water_drink` | Water |
| `flask` | Flask |
| `tea` | Tea |
| `bread` | Bread |
| `breadold` | Stale bread |
| `kolbasa` | Sausage |
| `sausage` | Sausage |
| `tushonka` | Canned meat |
| `conserva` | Canned food |
| `beans` | Beans |
| `corn` | Corn |
| `nuts` | Nuts |
| `raisins` | Raisins |
| `salmon` | Canned salmon |
| `tomato` | Tomato |
| `chocolate` | Chocolate |
| `chili` | Chili |
| `mre` | MRE ration |
| `ration_ru` | Russian ration |
| `ration_ukr` | Ukrainian ration |
| `protein` | Protein bar |
| `mint` | Mint |
| `jgut` | |

### Cooked/prepared food (fieldcooker system)

| Section | Notes |
|---------|-------|
| `meat_bloodsucker` | Bloodsucker meat |
| `meat_boar` | Boar meat |
| `meat_chimera` | Chimera meat |
| `meat_dog` | Dog meat |
| `meat_flesh` | Flesh meat |
| `meat_lurker` | Lurker meat |
| `meat_pseudodog` | Pseudodog meat |
| `meat_psysucker` | Psysucker meat |
| `meat_snork` | Snork meat |
| `meat_tushkano` | Tushkano meat |

### Cigarettes and Recreational

| Section | Notes |
|---------|-------|
| `cigarettes` | Cigarettes |
| `cigarettes_lucky` | Lucky Strike cigarettes |
| `cigarettes_russian` | Russian cigarettes |
| `cigar` | Cigar |
| `cigar1` | Cigar variant |
| `cigar2` | Cigar variant |
| `cigar3` | Cigar variant |
| `tobacco` | Loose tobacco |
| `hand_rolling_tobacco` | Hand-rolling tobacco |
| `joint` | Joint |
| `marijuana` | Marijuana |
| `cocaine` | Cocaine |
| `guitar_a` | Guitar |
| `harmonica_a` | Harmonica |

---

## Equipment and Devices

### Anomaly Detectors

| Section | Notes |
|---------|-------|
| `detector_simple` | Simple detector (Bear) |
| `detector_advanced` | Advanced detector (Veles) |
| `detector_elite` | Elite detector (Svarog) |
| `detector_scientific` | Scientific detector |
| `detector_geiger` | Geiger counter |
| `anomaly_scaner` | Anomaly scanner |

### PDAs and Communication

| Section | Notes |
|---------|-------|
| `device_pda` | Abstract base / NPC PDA — the section NPCs carry. The player never holds this section directly. |
| `device_pda_1` | Player PDA tier 1 — the starting PDA given at new game. |
| `device_pda_2` | Player PDA tier 2 — crafted from `device_pda_1`. Unlocks allied squad visibility. |
| `device_pda_3` | Player PDA tier 3 — crafted from `device_pda_2`. Extended squad features. |
| `device_flashlight` | Standalone flashlight — the item players carry in inventory (class `D_FLALIT`). |
| `device_torch` | Abstract base torch (class `TORCH_S`) — used by NPCs and as base for NV variants. The player does not hold this section directly. |
| `device_torch_nv_1` | NV torch tier 1 — night vision attachment, inherits from `device_torch`. |
| `device_torch_nv_2` | NV torch tier 2 — improved night vision. |
| `device_torch_nv_3` | NV torch tier 3 — best night vision. |
| `dev_flash_1` | Flash drive 1 |
| `dev_flash_2` | Flash drive 2 |
| `itm_pda_personal` | Personal PDA |
| `radio2` | Radio |

### Repair Kits

| Section | Notes |
|---------|-------|
| `light_repair_kit` | Light repair kit (weapons) |
| `medium_repair_kit` | Medium repair kit |
| `heavy_repair_kit` | Heavy repair kit |
| `armor_repair_fa` | Armour repair kit |
| `helmet_repair_kit` | Helmet repair kit |
| `exo_repair_kit` | Exoskeleton repair kit |
| `cleaning_kit_p` | Cleaning kit (pistols) |
| `cleaning_kit_r5` | Cleaning kit (rifles, 5.45) |
| `cleaning_kit_r7` | Cleaning kit (rifles, 7.62) |
| `cleaning_kit_s` | Cleaning kit (shotguns) |
| `cleaning_kit_u` | Cleaning kit (universal) |
| `gun_oil` | Gun oil |
| `gun_oil_ru` | Gun oil (Russian) |
| `gun_oil_ru_d` | Gun oil variant |

### Tools and Crafting

| Section | Notes |
|---------|-------|
| `toolkit_1` | Toolkit tier 1 |
| `toolkit_2` | Toolkit tier 2 |
| `toolkit_3` | Toolkit tier 3 |
| `toolkit_p` | Toolkit (pistols) |
| `toolkit_r5` | Toolkit (rifles, 5.45) |
| `toolkit_r7` | Toolkit (rifles, 7.62) |
| `toolkit_s` | Toolkit (shotguns) |
| `itm_basickit` | Basic crafting kit |
| `itm_gunsmith_toolkit` | Gunsmith toolkit |
| `leatherman_tool` | Leatherman multi-tool |
| `swiss_knife` | Swiss army knife |
| `sharpening_stones` | Sharpening stones |
| `sewing_kit_a` | Sewing kit (armour) |
| `sewing_kit_b` | Sewing kit (boots) |
| `sewing_kit_h` | Sewing kit (helmet) |
| `charcoal` | Charcoal (filter material) |
| `glue_a` | Glue (armour) |
| `glue_b` | Glue (boots) |
| `glue_e` | Glue (electronics) |
| `solvent` | Solvent |
| `salicidic_acid` | Salicylic acid |
| `fieldcooker` | Fieldcooker |
| `cooking` | Cooking item |
| `box_matches` | Box of matches |
| `matches` | Matches |
| `kerosene` | Kerosene |
| `compression_bag` | Compression bag |

### Backpacks and Containers

| Section | Notes |
|---------|-------|
| `itm_backpack` | Backpack (stash container) |
| `itm_actor_backpack` | Actor backpack |
| `itm_actor_backpack_mlr` | Backpack (MLR variant) |
| `inventory_box` | Inventory box container |
| `equ_small_pack` | Small pack |
| `equ_small_military_pack` | Small military pack |
| `equ_military_pack` | Military pack |
| `equ_tourist_pack` | Tourist pack |
| `kit_hunt` | Hunting kit |

### Fuel and Explosives Containers

| Section | Notes |
|---------|-------|
| `explo_jerrycan_fuel` | Fuel jerrycan (full) |
| `explo_jerrycan_fuel_empty` | Fuel jerrycan (empty) |
| `explo_balon_gas` | Gas canister (full) |
| `explo_balon_gas_empty` | Gas canister (empty) |

### Misc Devices

| Section | Notes |
|---------|-------|
| `addon` | Addon item |
| `ammo_box` | Ammo box |
| `tch_detector` | **Base class** — parent for `detector_geiger`. Do not spawn directly. |
| `tch_quest` | **Base class** — parent for all quest items. Do not spawn directly. |
| `tch_money` | **Base class** — parent for all money denominations. Do not spawn directly. |
| `tch_junk` | **Base class** — parent for `radio2` and similar junk items. Do not spawn directly. |
| `decoder` | Decoder device |
| `stitch_decoder` | Stitch decoder |
| `decryption_radio` | Decryption radio |
| `monolith_shard` | Monolith shard |
| `itm_tent` | Tent |
| `itm_tent_bag` | Tent bag |
| `itm_sleepbag` | Sleeping bag |
| `itm_deployable_mgun` | Deployable machine gun |

---

## Mutant Parts

Sold to traders and used in crafting. All use the `mutant_part_` prefix.

| Section | Mutant |
|---------|--------|
| `mutant_part_boar_chop` | Boar |
| `mutant_part_boar_leg` | Boar |
| `mutant_part_tusk_boar` | Boar |
| `mutant_part_dog_heart` | Dog |
| `mutant_part_dog_liver` | Dog |
| `mutant_part_dog_meat` | Dog |
| `mutant_part_dog_tail` | Dog |
| `mutant_part_flesh_eye` | Flesh |
| `mutant_part_flesh_meat` | Flesh |
| `mutant_part_fang_psevdodog` | Pseudodog |
| `mutant_part_psevdodog_meat` | Pseudodog |
| `mutant_part_psevdodog_tail` | Pseudodog |
| `mutant_part_brain_burer` | Burer |
| `mutant_part_burer_hand` | Burer |
| `mutant_part_fracture_hand` | Poltergeist |
| `mutant_part_heart_bloodsucker` | Bloodsucker |
| `mutant_part_krovosos_jaw` | Bloodsucker |
| `mutant_part_krovosos_meat` | Bloodsucker |
| `mutant_part_controller_glass` | Controller |
| `mutant_part_controller_hand` | Controller |
| `mutant_part_cat_claw` | Cat |
| `mutant_part_cat_tail` | Cat |
| `mutant_part_cat_thyroid` | Cat |
| `mutant_part_lurker_eye` | Lurker |
| `mutant_part_lurker_meat` | Lurker |
| `mutant_part_lurker_tail` | Lurker |
| `mutant_part_chimera_claw` | Chimera |
| `mutant_part_chimera_kogot` | Chimera |
| `mutant_part_chimera_meat` | Chimera |
| `mutant_part_heart_chimera` | Chimera |
| `mutant_part_snork_hand` | Snork |
| `mutant_part_snork_leg` | Snork |
| `mutant_part_snork_mask` | Snork |
| `mutant_part_pseudogigant_eye` | Pseudogiant |
| `mutant_part_pseudogigant_hand` | Pseudogiant |
| `mutant_part_psysucker_hand` | Psysucker |
| `mutant_part_psysucker_meat` | Psysucker |
| `mutant_part_tushkano_head` | Tushkano |
| `mutant_part_tushkano_meat` | Tushkano |
| `mutant_part_zombi_hand` | Zombie |
| `mutant_part_crow_beak` | Crow |
| `mutant_part_general` | **Base class** — parent for most specific mutant parts. Do not spawn directly. |
| `mutant_part_general_add` | **Base class** — parent for secondary parts (claws, thyroid, etc.). Do not spawn directly. |
| `mutant_part_general_meat` | **Base class** — parent for meat parts. Do not spawn directly. |
| `mutant_part_general_mlr` | **Base class** — MLR variant base. Do not spawn directly. |
| `powder_poltergeist` | Poltergeist |

---

## Grenades and Explosives

| Section | Notes |
|---------|-------|
| `grenade_f1` | F1 fragmentation grenade |
| `grenade_rgd5` | RGD-5 grenade |
| `grenade_gd-05` | GD-05 grenade |
| `grenade_smoke` | Smoke grenade |
| `mine` | TM-46 anti-personnel mine |
| `mine_new` | Updated mine |
| `mine_proximity` | Proximity mine |
| `ied` | IED |
| `ied_new` | Updated IED |
| `ied_rpg` | RPG IED |
| `ied_rpg_new` | RPG IED updated |
| `explosive_dinamit` | Dynamite |
| `explo_metalcan_powder` | Metal can powder |
| `explosive_barrel` | **Base class / world object** — parent for IED blow states and world barrels. Do not spawn as an inventory item. |
| `explosive_fuelcan` | **Base class / world object** — parent for `explosive_gaz_balon`. Do not spawn as an inventory item. |
| `explosive_grenade` | **Base class / world object** — parent for scripted grenade objects. Do not spawn as an inventory item. |

---

## Money

Currency items used in the in-game economy.

| Section | Value |
|---------|-------|
| `money_10` | 10 RU |
| `money_50` | 50 RU |
| `money_100` | 100 RU |
| `money_500` | 500 RU |
| `money_1000` | 1,000 RU |
| `money_5000` | 5,000 RU |
| `cash` | Cash (generic) |
| `tch_money` | Trader Caravan money |

---

## Quest Items and Documents

These sections are used in specific quests. They typically cannot be sold and have
no combat or utility value outside their quest context.

```
broken_pda              chernobog_notes         cit_doctors_pda
cit_doctors_key         drekavac_notes          drx_sl_quest_item_1
drx_sl_quest_item_2     drx_sl_quest_item_3     jup_a9_conservation_info
jup_a9_delivery_info    jup_a9_evacuation_info  jup_a9_losses_info
jup_a9_meeting_info     jup_a9_power_info       jup_a9_way_info
jup_b1_half_artifact    jup_b10_notes_01        jup_b10_notes_02
jup_b10_notes_03        jup_b10_ufo_memory      jup_b10_ufo_memory_2
jup_b200_tech_materials_wire                    jup_b200_tech_materials_acetone
jup_b200_tech_materials_capacitor               jup_b200_tech_materials_textolite
jup_b200_tech_materials_transistor              jup_b202_bandit_pda
jup_b205_sokolov_note   jup_b206_plant          jup_b207_merc_pda_with_contract
jup_b209_monster_scanner jup_b32_scanner_device jup_b46_duty_founder_pda
jup_b47_jupiter_products_info jup_b47_merc_pda  jup_b9_blackbox
main_story_1_quest_case main_story_2_lab_x18_documents
main_story_3_lab_x16_documents main_story_4_lab_x10_documents
main_story_5_lab_x8_documents  main_story_6_jup_ug_documents
main_story_7_mon_con_documents
mar_base_owl_stalker_trader_task_1_pda
mlr_strelok_item_01     mlr_x8_copybook         mlr_x8_copybook_2
mlr_x8_documents        quest_package_1         quest_package_2
quest_package_3         quest_package_4         quest_package_5
quest_package_6         quest_package_7         quest_package_8
radio_connections_pda   special_delivery_case   strelok_notes
vodnik_notes            wpn_gauss_quest         yantar_deployable_mgun
zat_a23_access_card     zat_a23_gauss_rifle_docs zat_a23_labx8_key
zat_b12_documents_1     zat_b12_documents_2     zat_b12_key_1
zat_b12_key_2           zat_b20_noah_pda        zat_b22_medic_pda
zat_b33_safe_container  zat_b39_joker_pda       zat_b40_notebook
zat_b40_pda_1           zat_b40_pda_2           zat_b40_sarge_pda
zat_b44_barge_pda       zat_b57_gas             pri_a15_documents
pri_a19_american_experiment_info pri_a19_lab_x10_info
pri_a19_lab_x16_info    pri_a19_lab_x18_info    pri_a19_lab_x7_info
pri_b35_lab_x8_key      pri_b36_monolith_hiding_place_pda
lx8_service_instruction lx8_history_documents    lx8_history_2_documents
lx8_history_3_documents x8_documents             jupiter_documents
pri_decoder_documents   drx_agr_u_documents      drx_jup_u_documents
drx_x16_documents       drx_x18_documents        drx_x19_documents
drx_x8_documents        chernobog_notes          strelok_pendrive
army_isg_spy_pendrive   hb_isg_dushman_intel
```

### Letters and lore items

```
letter_ecologist_report_1_of_3    letter_ecologist_report_2_of_3
letter_ecologist_report_3_of_3    letter_freedom_manual_1_of_2
letter_freedom_manual_2_of_2      letter_letter_to_outside
letter_memoirs_1_of_2             letter_memoirs_2_of_2
letter_mercenary                  letter_military_log
letter_military_stalker           letter_monolith_prayer_1_of_3
letter_monolith_prayer_2_of_3     letter_monolith_prayer_3_of_3
letter_monolithian_thoughts       letter_stalker_letter_1_of_2
letter_stalker_letter_2_of_2      letter_stalker_letter_3
journal
```

---

## Faction Patches and Miscellaneous

| Section | Notes |
|---------|-------|
| `csky_patch` | Clear Sky faction patch |
| `army_bowler` | Army mess tin |
| `bad_psy_helmet` | Psy-resistance helmet (degraded) |
| `good_psy_helmet` | Psy-resistance helmet |
| `grooming` | Grooming kit |
| `wpn_binoc` | Binoculars |
| `wpn_dynamo_hand` | Hand dynamo (power generator) |
| `wpn_upd` | UPD device |
| `tch_junk` | Trader Caravan junk |
| `tch_part` | Trader Caravan part |
| `tch_repair` | Trader Caravan repair item |
| `tch_repair0` | Trader Caravan repair item (base) |
| `tch_upgr` | Trader Caravan upgrade item |
| `tch_upgr_ico` | Trader Caravan upgrade (icon) |
| `blackbox_mlr` | Blackbox (MLR) |
| `item_pda_map_mlr` | PDA map (MLR) |
