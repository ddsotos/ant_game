"""Data-driven ant evolution cards and forecastable disasters.

 The engine owns all resolution rules. This module only describes cards,
 options, and the five forecastable environmental changes. Normal cards use
 five evolutionary root tags; recurring problems are limited to raid, fungal,
 and nest-damage pressures.
"""

from __future__ import annotations

from types import MappingProxyType

from .models import ActionOption, CardRole, DisasterCard, OptimizationRequirement, ShieldSpec, TraitCard


ROOT_TAGS = frozenset({"Morphology", "Chemistry", "Sociality", "Nesting", "Resource Ecology"})


def _shield(problem_id: str, *, amount: int) -> ShieldSpec:
    return ShieldSpec(problem_id, amount)


def _action(card_id, name, tags, requirements, options, source_taxon, biology_basis, biology_source, design_role, text):
    # Foundation and Bridge cards are immediately usable. Payoffs alone ask
    # the rest of the column to establish a deliberately asymmetric build.
    if design_role != "Payoff":
        requirements = {}
    return TraitCard(id=card_id, name=name, root_tags=tags, role=CardRole.ACTION,
                     activation_requirements=requirements, options=options,
                     source_taxon=source_taxon, biology_basis=biology_basis,
                     biology_source=biology_source, design_role=design_role, text=text)


def _starter(card_id, name, tags, options, source_taxon, biology_basis, biology_source, text):
    return TraitCard(id=card_id, name=name, root_tags=tags, role=CardRole.STARTER,
                     activation_requirements={}, options=options,
                     source_taxon=source_taxon, biology_basis=biology_basis,
                     biology_source=biology_source, design_role="Foundation", text=text)


STARTERS: tuple[TraitCard, ...] = (
    _starter("trail_pheromone", "Trail Pheromone", frozenset({"Chemistry"}),
             (ActionOption(prosperity=1, text="Mark a reliable route for the current foraging wave."),),
             "Formicidae (ordinary trail-laying ants)", "Many ants recruit nestmates with pheromone trails during foraging.",
             "https://pmc.ncbi.nlm.nih.gov/articles/PMC3772619/", "An ordinary chemical trail gives the species its first route to food."),
    _starter("earthwork_nest", "Earthwork Nest", frozenset({"Nesting"}),
             (ActionOption(prosperity=1, text="Maintain a safe chamber for the colony."),),
             "Formicidae (soil-nesting ants)", "Ant colonies excavate and maintain underground chambers and entrances.",
             "https://pmc.ncbi.nlm.nih.gov/articles/PMC528881/", "A basic soil nest is a recognizably ordinary starting foundation."),
    _starter("collective_foraging", "Collective Foraging", frozenset({"Sociality", "Resource Ecology"}),
             (ActionOption(prosperity=1, text="Bring a shared food find back to the nest."),),
             "Formicidae (social foraging ants)", "Workers recruit nestmates and jointly exploit food resources.",
             "https://pmc.ncbi.nlm.nih.gov/articles/PMC4267257/", "The initial species can already forage together without specialization."),
)


# Thirty normal cards. All are ACTION cards; strong options are gated by
# accumulated roots rather than by new currencies or bespoke effect ids.
NORMAL_TRAITS: tuple[TraitCard, ...] = (
    _action("oecophylla_silkworks", "Oecophylla Silkworks", frozenset({"Nesting", "Sociality"}), {}, (ActionOption(prosperity=1, shields=(_shield("nest_damage", amount=1),), text="Weave a protected canopy."),), "Oecophylla smaragdina", "Workers pull leaves together with silk produced by their larvae.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4896424/", "Foundation", "Larval silk turns sociality into a living canopy nest."),
    _action("oecophylla_living_chain", "Oecophylla Living Chain", frozenset({"Sociality"}), {"Sociality": 2}, (ActionOption(draw_cards=1, text="Form a chain and extend the route."),), "Oecophylla smaragdina", "Workers form pulling and bridging chains to move across gaps and bend leaves.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3997362/", "Payoff", "A chain is treated as coordinated social labor; the temporary route is its consequence."),
    _action("cephalotes_aerialis", "Cephalotes Aerialis", frozenset({"Morphology"}), {}, (ActionOption(shields=(_shield("raid", amount=1),), text="Steer a fall away from a hunter."),), "Cephalotes atratus", "Wingless workers steer their descent while falling from the canopy.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2880152/", "Foundation", "The distinctive adaptation is a flattened, steerable body; descent is not a separate root."),
    _action("cephalotes_living_gate", "Cephalotes Living Gate", frozenset({"Morphology", "Nesting"}), {"Sociality": 3, "Nesting": 1}, (ActionOption(shields=(_shield("raid", amount=3),), text="Seal the entrance with a shield-shaped head."),), "Cephalotes varians", "Soldiers use shield-shaped heads as living barricades at nest entrances.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6436684/", "Payoff", "A specialized social caste becomes a door for a narrow nest entrance."),
    _action("odontomachus_tension_lock", "Odontomachus Tension Lock", frozenset({"Morphology"}), {}, (ActionOption(prosperity=1, text="Snap at prey or rivals."), ActionOption(shields=(_shield("raid", amount=1),), text="Use the snap to launch away.")), "Odontomachus bauri and O. brunneus", "A latch-spring mandible strikes prey and can propel an ant away from danger.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1568925/", "Bridge", "The latch-spring mandible is a single morphological innovation; its launch effect is incidental."),
    _action("pheidole_supermajor_program", "Pheidole Supermajor Program", frozenset({"Sociality", "Morphology"}), {"Sociality": 3, "Morphology": 1}, (ActionOption(shields=(_shield("raid", amount=3),), text="Deploy an oversized defender."),), "Pheidole rhea and P. obtusospinosa", "Some species produce a third, supersoldier worker caste with specialized defenses.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3334560/", "Payoff", "A costly social program creates a conspicuous defender."),
    _action("pheidole_seed_miller", "Pheidole Seed Miller", frozenset({"Sociality", "Morphology", "Resource Ecology"}), {"Sociality": 2, "Resource Ecology": 2}, (ActionOption(prosperity=2, text="Process a hard seed harvest."),), "Pheidole tepicana", "Supersoldiers in this species specialize in seed milling.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3334560/", "Payoff", "The same social root can branch from defense into food processing."),
    _action("myrmecocystus_reserve", "Myrmecocystus Reserve", frozenset({"Sociality", "Resource Ecology"}), {"Sociality": 1, "Resource Ecology": 1}, (ActionOption(draw_cards=1, text="Release liquid stores during scarcity and discover another option."),), "Myrmecocystus spp.", "Replete workers store liquid food in their crops for long periods.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Payoff", "A specialized storage caste makes waiting strategically viable."),
    _action("megaponera_field_medicine", "Megaponera Field Medicine", frozenset({"Chemistry", "Sociality"}), {"Sociality": 3, "Chemistry": 1}, (ActionOption(shields=(_shield("fungal", amount=3),), text="Treat an infected wound."),), "Megaponera analis", "Workers apply antimicrobial gland secretions to infected wounds and sharply reduce mortality.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10756881/", "Payoff", "Chemical treatment becomes reliable only when a coordinated care group can deliver it."),
    _action("megaponera_rescue_column", "Megaponera Rescue Column", frozenset({"Sociality"}), {}, (ActionOption(shields=(_shield("raid", amount=1),), text="Carry an injured nestmate home."),), "Megaponera analis", "Returning raiders carry injured nestmates back to the nest after termite fights.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "Bridge", "The adaptation is collective rescue; travel is merely the context in which cooperation matters."),
    _action("colobopsis_last_defense", "Colobopsis Last Defense", frozenset({"Chemistry", "Morphology"}), {"Nesting": 3, "Chemistry": 1}, (ActionOption(shields=(_shield("raid", amount=3),), text="Rupture a gland to stop an intruder."),), "Colobopsis explodens", "Minor workers can rupture enlarged gland reservoirs and repel rivals with sticky irritant secretions.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5919914/", "Payoff", "The strongest defense is a deliberately terminal commitment."),
    _action("paraponera_poneratoxin", "Paraponera Poneratoxin", frozenset({"Chemistry"}), {"Morphology": 3, "Chemistry": 1}, (ActionOption(prosperity=2, text="Make a rival pay for approaching."), ActionOption(shields=(_shield("raid", amount=3),), text="Deter an attack with venom.")), "Paraponera clavata", "Its venom contains poneratoxin-like sodium-channel toxins causing intense prolonged pain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10206162/", "Payoff", "Venom is an expensive but memorable chemical weapon."),
    _action("apterostigma_dentigerumycin", "Apterostigma Dentigerumycin", frozenset({"Chemistry", "Resource Ecology"}), {}, (ActionOption(shields=(_shield("fungal", amount=1),), text="Suppress the garden parasite."),), "Apterostigma dentigerum", "A Pseudonocardia symbiont produces dentigerumycin that inhibits the garden parasite Escovopsis.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2748230/", "Bridge", "A microbial partner joins chemistry to cultivated resources."),
    _action("acromyrmex_antibiotic_garden", "Acromyrmex Antibiotic Garden", frozenset({"Chemistry", "Resource Ecology"}), {"Nesting": 3, "Chemistry": 1}, (ActionOption(shields=(_shield("fungal", amount=3),), text="Protect the cultivated crop."),), "Acromyrmex octospinosus and related leafcutters", "Leafcutting ants use Pseudonocardia and gland secretions against Escovopsis.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3418327/", "Payoff", "A mature garden makes disease resistance powerful but specialized."),
    _action("atta_fungus_garden", "Atta Fungus Garden", frozenset({"Resource Ecology"}), {}, (ActionOption(prosperity=2, text="Harvest cultivated fungal food."),), "Atta colombica", "Workers provision a fungal cultivar with leaves and consume its nutrient-rich structures.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9019514/", "Foundation", "Fungiculture converts plant biomass into dependable prosperity."),
    _action("attine_infrabuccal_pocket", "Attine Infrabuccal Pocket", frozenset({"Chemistry", "Morphology"}), {}, (ActionOption(shields=(_shield("fungal", amount=1),), text="Sterilize and remove infected material."),), "Fungus-growing ants (Attini)", "The infrabuccal pocket helps sequester and sterilize Escovopsis material.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1617182/", "Bridge", "Sanitation links mouthpart morphology to chemical defense."),
    _action("cataglyphis_silver_hair", "Cataglyphis Silver Hair", frozenset({"Morphology"}), {}, (ActionOption(prosperity=1, text="Reflect and radiate desert heat."),), "Cataglyphis bombycina", "Triangular reflective hairs reduce internal heating under intense sunlight.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4830450/", "Bridge", "A visible body adaptation supports the thermal optimization."),
    _action("cataglyphis_sky_compass", "Cataglyphis Sky Compass", frozenset({"Resource Ecology"}), {"Resource Ecology": 2}, (ActionOption(draw_cards=1, text="Discover another option by the shortest known route."),), "Cataglyphis fortis", "Desert foragers use path integration and polarized skylight to return across featureless terrain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1567920/", "Payoff", "The compass preserves access to a food route, so it is represented as resource ecology rather than a movement axis."),
    _action("pheidole_raid_wall", "Pheidole Raid Wall", frozenset({"Sociality", "Morphology"}), {"Nesting": 3, "Morphology": 1}, (ActionOption(shields=(_shield("raid", amount=3),), text="Coordinate supermajors at the entrance."),), "Pheidole obtusospinosa", "Supermajors and workers use multiple defensive phases against invading army ants.", "https://academic.oup.com/jinsectscience/article/10/1/1/820704", "Payoff", "Sociality and collective defense combine against a known rival route."),
    _action("harpegnathos_gamergate", "Harpegnathos Gamergate", frozenset({"Sociality"}), {}, (ActionOption(prosperity=1, text="Let a worker become a reproductive option."),), "Harpegnathos saltator", "Workers can reversibly enter a reproductive gamergate caste after queen loss.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7919410/", "Bridge", "Social state can remain flexible without a separate caste tag."),
    _action("temnothorax_quorum_nest", "Temnothorax Quorum Nest", frozenset({"Sociality", "Nesting"}), {}, (ActionOption(prosperity=1, text="Recruit toward the best available cavity."),), "Temnothorax albipennis and T. curvispinosus", "Scouts recruit nestmates and use quorum-like feedback to choose new nest sites.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2817311/", "Bridge", "Collective information makes a nest choice without central control."),
    _action("pogonomyrmex_granary", "Pogonomyrmex Granary", frozenset({"Resource Ecology", "Nesting"}), {"Nesting": 2, "Resource Ecology": 2}, (ActionOption(draw_cards=1, text="Use a protected seed chamber during scarcity and discover another option."),), "Pogonomyrmex badius", "Workers store seeds in damp subterranean chambers and use germination to process large seeds.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5125654/", "Payoff", "A granary rewards preparing before scarcity arrives."),
    _action("paltothyreus_distress_signal", "Paltothyreus Distress Signal", frozenset({"Chemistry", "Sociality"}), {}, (ActionOption(shields=(_shield("raid", amount=1),), text="Call nestmates to a trapped worker."),), "Paltothyreus tarsatus", "Mandibular-gland compounds released by trapped workers attract nestmates to dig and rescue them.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5731505/", "Bridge", "A chemical alarm converts an individual incident into a group response."),
    _action("solenopsis_dry_store", "Solenopsis Dry Store", frozenset({"Resource Ecology"}), {"Sociality": 3, "Resource Ecology": 1}, (ActionOption(prosperity=1, draw_cards=1, text="Dry food and discover an option for a later shortage."),), "Solenopsis invicta", "Fire ants dry and store insect pieces for later use; honeypot-like storage is an ant adaptation.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Payoff", "Immediate prosperity can be converted into a future option."),
    _action("solenopsis_raft_cycling", "Solenopsis Raft Cycling", frozenset({"Sociality"}), {}, (ActionOption(shields=(_shield("nest_damage", amount=1),), text="Cycle workers through a living raft."),), "Solenopsis invicta", "Workers cycle through floating rafts and protect brood during prolonged flooding.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3462402/", "Bridge", "Collective buoyancy is a social organization of bodies; cycling is not a separate root."),
    _action("atta_leaf_cache", "Atta Leaf Cache", frozenset({"Resource Ecology"}), {"Resource Ecology": 1, "Nesting": 1}, (ActionOption(draw_cards=1, text="Cache leaf fragments and discover another option."),), "Atta cephalotes and A. colombica", "Foragers can deposit leaf fragments outside a temporarily blocked nest entrance as a cache.", "https://www.sciencedirect.com/science/article/pii/S0003347299913325", "Payoff", "A short-term cache preserves a harvest while access is constrained."),
    _action("acromyrmex_spore_removal", "Acromyrmex Spore Removal", frozenset({"Chemistry", "Sociality"}), {}, (ActionOption(shields=(_shield("fungal", amount=1),), text="Remove spores and contaminated garden material."),), "Acromyrmex leafcutter ants", "Workers physically remove Escovopsis spores and mycelium alongside chemical defenses.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3418327/", "Bridge", "A behavioral sanitation route can complement microbial antibiotics."),
    _action("cataglyphis_heatshock_proteins", "Cataglyphis Heatshock Proteins", frozenset({"Chemistry"}), {}, (ActionOption(prosperity=1, text="Protect cellular machinery during a hot run."),), "Cataglyphis bombycina", "Heat-adapted ants show constitutive and inducible molecular chaperone responses to thermal stress.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6003908/", "Bridge", "A less visible thermal route contributes to the environmental optimization."),
    _action("megaponera_termite_raid", "Megaponera Termite Raid", frozenset({"Sociality", "Resource Ecology"}), {}, (ActionOption(prosperity=2, text="Bring home a coordinated termite harvest."), ActionOption(shields=(_shield("raid", amount=1),), text="Keep the raid column together.")), "Megaponera analis", "This species performs group raids on highly defensive termites, with specialized task division.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "Bridge", "A profitable raid is tempting even when it exposes the colony to injury."),
    _action("temnothorax_emergency_emigration", "Temnothorax Emergency Emigration", frozenset({"Nesting"}), {}, (ActionOption(shields=(_shield("nest_damage", amount=1),), text="Move before the cavity becomes unsafe."),), "Temnothorax albipennis", "Colonies emigrate from fragile cavities when their current nest is damaged or deteriorates.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3101226/", "Bridge", "The decision is about preserving a viable nest; relocation is the response, not a root tag."),
)


DISASTERS: tuple[DisasterCard, ...] = (
    DisasterCard("flood", "Flood", OptimizationRequirement("Flood Adaptation", {"Sociality": 3, "Morphology": 1, "Nesting": 1, "Resource Ecology": 1}, "Solenopsis invicta; Cephalotes atratus and arboreal ants", "Fire ants interlock into buoyant rafts, while arboreal ants use gliding and canopy routes above inundated ground.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3462402/", "A single flood adaptation combines collective buoyancy, body form, canopy shelter, and preserved food access."), "Floodwater tears through ground routes and separates canopy refuges."),
    DisasterCard("desert_heat_wave", "Desert Heat Wave", OptimizationRequirement("Silver-Hair Heatshock Protection", {"Morphology": 3, "Chemistry": 2}, "Cataglyphis bombycina", "Triangular reflective hairs reduce solar heating, while constitutive and inducible heat-shock responses protect cellular machinery.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4830450/", "Body structure and cellular protection sustain a brief hot run."), "Radiant heat and dry ground punish exposed foragers."),
    DisasterCard("prolonged_drought", "Prolonged Drought", OptimizationRequirement("Underground Granary", {"Nesting": 3, "Resource Ecology": 2}, "Pogonomyrmex badius", "Workers store and process seeds in protected subterranean chambers.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5125654/", "A deep granary separates stored food from the dry surface."), "A long dry spell removes easy surface food."),
    DisasterCard("habitat_instability", "Habitat Instability", OptimizationRequirement("Emergency Emigration", {"Sociality": 2, "Nesting": 2}, "Temnothorax albipennis", "Colonies use collective nest-site decisions and emigrate when fragile cavities are damaged or deteriorate.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3101226/", "A colony that can choose and establish a sound nest before its cavity fails retains a viable home."), "Nest cavities become unsafe as substrate and shelter deteriorate."),
    DisasterCard("landmark_loss", "Landmark Loss", OptimizationRequirement("Sky Compass Navigation", {"Resource Ecology": 3}, "Cataglyphis fortis", "Desert foragers use path integration and polarized skylight to return across featureless terrain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1567920/", "A celestial route preserves access to foraging when familiar landmarks disappear."), "Wind and shifting substrate erase the routes used to reach food."),
)


TRAITS: tuple[TraitCard, ...] = STARTERS + NORMAL_TRAITS
TRAIT_CARDS = TRAITS
DISASTER_CARDS = DISASTERS
EVENTS = DISASTERS
EVENT_CARDS = DISASTERS
TRAIT_BY_ID = MappingProxyType({card.id: card for card in TRAITS})
DISASTER_BY_ID = MappingProxyType({card.id: card for card in DISASTERS})
EVENT_BY_ID = DISASTER_BY_ID


__all__ = ["DISASTERS", "DISASTER_CARDS", "DISASTER_BY_ID", "EVENTS", "EVENT_CARDS", "EVENT_BY_ID", "NORMAL_TRAITS", "ROOT_TAGS", "STARTERS", "TRAITS", "TRAIT_CARDS", "TRAIT_BY_ID"]
