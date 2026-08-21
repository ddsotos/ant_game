"""Data-driven ant evolution cards and forecastable disasters.

The engine owns all resolution rules. This module only describes cards,
options, and the eight forecastable disasters. Normal cards deliberately
use the seven evolutionary root tags; hazard tags occur only on shields and
environment cards.
"""

from __future__ import annotations

from types import MappingProxyType

from .models import ActionOption, CardRole, DisasterCard, OptimizationRequirement, ShieldSpec, TraitCard


ROOT_TAGS = frozenset({"Morphology", "Chemistry", "Cooperation", "Caste", "Nesting", "Movement", "Resource Ecology"})


def _shield(hazard: str, *, amount: int) -> ShieldSpec:
    return ShieldSpec(hazard, amount)


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
    _starter("trail_pheromone", "Trail Pheromone", frozenset({"Chemistry", "Movement"}),
             (ActionOption(draw_cards=1, text="Discover another route for the current foraging wave."),),
             "Formicidae (ordinary trail-laying ants)", "Many ants recruit nestmates with pheromone trails during foraging.",
             "https://pmc.ncbi.nlm.nih.gov/articles/PMC3772619/", "An ordinary chemical trail gives the species its first route to food."),
    _starter("earthwork_nest", "Earthwork Nest", frozenset({"Nesting"}),
             (ActionOption(draw_cards=1, text="Explore another option from maintained soil chambers."),),
             "Formicidae (soil-nesting ants)", "Ant colonies excavate and maintain underground chambers and entrances.",
             "https://pmc.ncbi.nlm.nih.gov/articles/PMC528881/", "A basic soil nest is a recognizably ordinary starting foundation."),
    _starter("collective_foraging", "Collective Foraging", frozenset({"Cooperation", "Resource Ecology"}),
             (ActionOption(prosperity=1, text="Bring a shared food find back to the nest."),),
             "Formicidae (social foraging ants)", "Workers recruit nestmates and jointly exploit food resources.",
             "https://pmc.ncbi.nlm.nih.gov/articles/PMC4267257/", "The initial species can already forage together without specialization."),
)


# Thirty normal cards. All are ACTION cards; strong options are gated by
# accumulated roots rather than by new currencies or bespoke effect ids.
NORMAL_TRAITS: tuple[TraitCard, ...] = (
    _action("oecophylla_silkworks", "Oecophylla Silkworks", frozenset({"Nesting", "Cooperation"}), {"Nesting": 1, "Cooperation": 1}, (ActionOption(prosperity=1, shields=(_shield("flood", amount=1),), text="Weave a protected canopy."),), "Oecophylla smaragdina", "Workers pull leaves together with silk produced by their larvae.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4896424/", "Foundation", "Larval silk turns cooperation into a living canopy nest."),
    _action("oecophylla_living_chain", "Oecophylla Living Chain", frozenset({"Cooperation", "Movement"}), {"Cooperation": 1, "Movement": 1}, (ActionOption(draw_cards=1, text="Form a chain and extend the route."),), "Oecophylla smaragdina", "Workers form pulling and bridging chains to move across gaps and bend leaves.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3997362/", "Bridge", "A chain converts many bodies into a temporary bridge."),
    _action("cephalotes_aerialis", "Cephalotes Aerialis", frozenset({"Movement", "Morphology"}), {"Movement": 1, "Morphology": 1}, (ActionOption(shields=(_shield("raid", amount=1),), text="Steer a fall away from a hunter."),), "Cephalotes atratus", "Wingless workers steer their descent while falling from the canopy.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2880152/", "Foundation", "Aerial steering turns a fall into an escape route."),
    _action("cephalotes_living_gate", "Cephalotes Living Gate", frozenset({"Morphology", "Nesting"}), {"Caste": 3, "Nesting": 1}, (ActionOption(shields=(_shield("raid", amount=2),), text="Seal the entrance with a shield-shaped head."),), "Cephalotes varians", "Soldiers use shield-shaped heads as living barricades at nest entrances.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6436684/", "Payoff", "A specialized soldier becomes a door for a narrow nest entrance."),
    _action("odontomachus_tension_lock", "Odontomachus Tension Lock", frozenset({"Morphology", "Movement"}), {"Morphology": 2, "Movement": 2}, (ActionOption(prosperity=1, text="Snap at prey or rivals."), ActionOption(shields=(_shield("raid", amount=1),), text="Use the snap to launch away.")), "Odontomachus bauri and O. brunneus", "A latch-spring mandible strikes prey and can propel an ant away from danger.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1568925/", "Payoff", "One mechanical innovation supports both attack and escape."),
    _action("pheidole_supermajor_program", "Pheidole Supermajor Program", frozenset({"Caste", "Morphology"}), {"Caste": 3, "Cooperation": 1}, (ActionOption(shields=(_shield("raid", amount=2),), text="Deploy an oversized defender."),), "Pheidole rhea and P. obtusospinosa", "Some species produce a third, supersoldier worker caste with specialized defenses.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3334560/", "Payoff", "A costly caste program creates a conspicuous defender."),
    _action("pheidole_seed_miller", "Pheidole Seed Miller", frozenset({"Caste", "Morphology", "Resource Ecology"}), {"Caste": 2, "Resource Ecology": 2}, (ActionOption(prosperity=2, text="Process a hard seed harvest."),), "Pheidole tepicana", "Supersoldiers in this species specialize in seed milling.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3334560/", "Payoff", "The same caste root can branch from defense into food processing."),
    _action("myrmecocystus_reserve", "Myrmecocystus Reserve", frozenset({"Caste", "Resource Ecology"}), {}, (ActionOption(draw_cards=1, shields=(_shield("drought", amount=1),), text="Release liquid stores during scarcity and discover another option."),), "Myrmecocystus spp.", "Replete workers store liquid food in their crops for long periods.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Foundation", "A specialized storage caste makes waiting strategically viable."),
    _action("megaponera_field_medicine", "Megaponera Field Medicine", frozenset({"Chemistry", "Cooperation"}), {"Movement": 3, "Chemistry": 1}, (ActionOption(shields=(_shield("fungal", amount=2),), text="Treat an infected wound."),), "Megaponera analis", "Workers apply antimicrobial gland secretions to infected wounds and sharply reduce mortality.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10756881/", "Payoff", "Chemical care turns group hunting into recoverable risk."),
    _action("megaponera_rescue_column", "Megaponera Rescue Column", frozenset({"Cooperation", "Movement"}), {"Cooperation": 1, "Movement": 1}, (ActionOption(draw_cards=1, shields=(_shield("raid", amount=1),), text="Carry an injured nestmate home."),), "Megaponera analis", "Returning raiders carry injured nestmates back to the nest after termite fights.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "Bridge", "A moving group preserves the value of experienced workers."),
    _action("colobopsis_last_defense", "Colobopsis Last Defense", frozenset({"Chemistry", "Morphology"}), {"Nesting": 3, "Chemistry": 1}, (ActionOption(shields=(_shield("raid", amount=2),), text="Rupture a gland to stop an intruder."),), "Colobopsis explodens", "Minor workers can rupture enlarged gland reservoirs and repel rivals with sticky irritant secretions.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5919914/", "Payoff", "The strongest defense is a deliberately terminal commitment."),
    _action("paraponera_poneratoxin", "Paraponera Poneratoxin", frozenset({"Chemistry"}), {"Morphology": 3, "Chemistry": 1}, (ActionOption(prosperity=2, text="Make a rival pay for approaching."), ActionOption(shields=(_shield("raid", amount=2),), text="Deter an attack with venom.")), "Paraponera clavata", "Its venom contains poneratoxin-like sodium-channel toxins causing intense prolonged pain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10206162/", "Payoff", "Venom is an expensive but memorable chemical weapon."),
    _action("apterostigma_dentigerumycin", "Apterostigma Dentigerumycin", frozenset({"Chemistry", "Resource Ecology"}), {"Chemistry": 1, "Resource Ecology": 1}, (ActionOption(shields=(_shield("fungal", amount=2),), text="Suppress the garden parasite."),), "Apterostigma dentigerum", "A Pseudonocardia symbiont produces dentigerumycin that inhibits the garden parasite Escovopsis.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2748230/", "Bridge", "A microbial partner joins chemistry to cultivated resources."),
    _action("acromyrmex_antibiotic_garden", "Acromyrmex Antibiotic Garden", frozenset({"Chemistry", "Resource Ecology"}), {"Nesting": 3, "Chemistry": 1}, (ActionOption(shields=(_shield("fungal", amount=2),), text="Protect the cultivated crop."),), "Acromyrmex octospinosus and related leafcutters", "Leafcutting ants use Pseudonocardia and gland secretions against Escovopsis.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3418327/", "Payoff", "A mature garden makes disease resistance powerful but specialized."),
    _action("atta_fungus_garden", "Atta Fungus Garden", frozenset({"Resource Ecology"}), {}, (ActionOption(prosperity=2, text="Harvest cultivated fungal food."),), "Atta colombica", "Workers provision a fungal cultivar with leaves and consume its nutrient-rich structures.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9019514/", "Foundation", "Fungiculture converts plant biomass into dependable prosperity."),
    _action("attine_infrabuccal_pocket", "Attine Infrabuccal Pocket", frozenset({"Chemistry", "Morphology"}), {}, (ActionOption(draw_cards=1, shields=(_shield("fungal", amount=1),), text="Sterilize and remove infected material."),), "Fungus-growing ants (Attini)", "The infrabuccal pocket helps sequester and sterilize Escovopsis material.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1617182/", "Bridge", "Sanitation links mouthpart morphology to chemical defense."),
    _action("cataglyphis_silver_hair", "Cataglyphis Silver Hair", frozenset({"Morphology"}), {"Movement": 3, "Morphology": 1}, (ActionOption(shields=(_shield("heat", amount=2),), text="Reflect and radiate desert heat."),), "Cataglyphis bombycina", "Triangular reflective hairs reduce internal heating under intense sunlight.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4830450/", "Payoff", "A visible body adaptation directly answers heat."),
    _action("cataglyphis_sky_compass", "Cataglyphis Sky Compass", frozenset({"Movement", "Resource Ecology"}), {}, (ActionOption(draw_cards=1, text="Discover another option by the shortest known route."),), "Cataglyphis fortis", "Desert foragers use path integration and polarized skylight to return across featureless terrain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1567920/", "Bridge", "Navigation preserves a resource route when landmarks disappear."),
    _action("pheidole_raid_wall", "Pheidole Raid Wall", frozenset({"Caste", "Cooperation"}), {"Nesting": 3, "Morphology": 1}, (ActionOption(shields=(_shield("raid", amount=2),), text="Coordinate supermajors at the entrance."),), "Pheidole obtusospinosa", "Supermajors and workers use multiple defensive phases against invading army ants.", "https://academic.oup.com/jinsectscience/article/10/1/1/820704", "Payoff", "Caste and collective defense combine against a known rival route."),
    _action("harpegnathos_gamergate", "Harpegnathos Gamergate", frozenset({"Caste", "Cooperation"}), {"Caste": 1, "Cooperation": 1}, (ActionOption(draw_cards=1, text="Let a worker become a reproductive option."),), "Harpegnathos saltator", "Workers can reversibly enter a reproductive gamergate caste after queen loss.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7919410/", "Bridge", "Caste is a social decision and can remain flexible."),
    _action("temnothorax_quorum_nest", "Temnothorax Quorum Nest", frozenset({"Cooperation", "Nesting"}), {"Cooperation": 1, "Nesting": 1}, (ActionOption(draw_cards=1, text="Recruit toward the best available cavity."),), "Temnothorax albipennis and T. curvispinosus", "Scouts recruit nestmates and use quorum-like feedback to choose new nest sites.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2817311/", "Bridge", "Collective information makes a nest choice without central control."),
    _action("pogonomyrmex_granary", "Pogonomyrmex Granary", frozenset({"Resource Ecology", "Nesting"}), {}, (ActionOption(draw_cards=1, shields=(_shield("drought", amount=2),), text="Use a protected seed chamber during scarcity and discover another option."),), "Pogonomyrmex badius", "Workers store seeds in damp subterranean chambers and use germination to process large seeds.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5125654/", "Foundation", "A granary rewards preparing before scarcity arrives."),
    _action("paltothyreus_distress_signal", "Paltothyreus Distress Signal", frozenset({"Chemistry", "Cooperation"}), {"Chemistry": 1, "Cooperation": 1}, (ActionOption(draw_cards=1, shields=(_shield("raid", amount=1),), text="Call nestmates to a trapped worker."),), "Paltothyreus tarsatus", "Mandibular-gland compounds released by trapped workers attract nestmates to dig and rescue them.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5731505/", "Bridge", "A chemical alarm converts an individual hazard into a group response."),
    _action("solenopsis_dry_store", "Solenopsis Dry Store", frozenset({"Resource Ecology"}), {"Cooperation": 3, "Resource Ecology": 1}, (ActionOption(prosperity=1, draw_cards=1, text="Dry food and discover an option for a later shortage."),), "Solenopsis invicta", "Fire ants dry and store insect pieces for later use; honeypot-like storage is an ant adaptation.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Payoff", "Immediate prosperity can be converted into a future option."),
    _action("solenopsis_raft_cycling", "Solenopsis Raft Cycling", frozenset({"Cooperation", "Movement"}), {}, (ActionOption(draw_cards=1, shields=(_shield("flood", amount=1),), text="Cycle workers through a living raft."),), "Solenopsis invicta", "Workers cycle through floating rafts and protect brood during prolonged flooding.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3462402/", "Bridge", "Collective buoyancy makes a flood survivable without permanent safety."),
    _action("atta_leaf_cache", "Atta Leaf Cache", frozenset({"Resource Ecology"}), {}, (ActionOption(draw_cards=1, text="Cache leaf fragments and discover another option."),), "Atta cephalotes and A. colombica", "Foragers can deposit leaf fragments outside a temporarily blocked nest entrance as a cache.", "https://www.sciencedirect.com/science/article/pii/S0003347299913325", "Bridge", "A short-term cache preserves a harvest while access is constrained."),
    _action("acromyrmex_spore_removal", "Acromyrmex Spore Removal", frozenset({"Chemistry", "Cooperation"}), {"Chemistry": 1, "Cooperation": 1}, (ActionOption(shields=(_shield("fungal", amount=1),), text="Remove spores and contaminated garden material."),), "Acromyrmex leafcutter ants", "Workers physically remove Escovopsis spores and mycelium alongside chemical defenses.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3418327/", "Bridge", "A behavioral sanitation route can complement microbial antibiotics."),
    _action("cataglyphis_heatshock_proteins", "Cataglyphis Heatshock Proteins", frozenset({"Chemistry"}), {"Movement": 3, "Chemistry": 1}, (ActionOption(prosperity=1, shields=(_shield("heat", amount=1),), text="Protect cellular machinery during a hot run."),), "Cataglyphis bombycina", "Heat-adapted ants show constitutive and inducible molecular chaperone responses to thermal stress.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6003908/", "Payoff", "A less visible thermal route trades maintenance for resilience."),
    _action("megaponera_termite_raid", "Megaponera Termite Raid", frozenset({"Cooperation", "Resource Ecology"}), {"Movement": 3, "Cooperation": 1}, (ActionOption(prosperity=2, text="Bring home a coordinated termite harvest."), ActionOption(shields=(_shield("raid", amount=1),), text="Keep the raid column together.")), "Megaponera analis", "This species performs group raids on highly defensive termites, with specialized task division.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "Payoff", "A profitable raid is tempting even when it exposes the colony to injury."),
    _action("temnothorax_emergency_emigration", "Temnothorax Emergency Emigration", frozenset({"Movement", "Nesting"}), {"Cooperation": 3, "Movement": 1}, (ActionOption(draw_cards=1, shields=(_shield("raid", amount=1),), text="Move before the cavity becomes unsafe."),), "Temnothorax albipennis", "Colonies emigrate from fragile cavities when their current nest is damaged or deteriorates.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3101226/", "Payoff", "Movement and nesting together allow a costly but timely escape."),
)


DISASTERS: tuple[DisasterCard, ...] = (
    DisasterCard("flood_torrent", "Flood Torrent", frozenset({"flood"}), OptimizationRequirement("Living Raft", {"Cooperation": 3, "Morphology": 1}, "Solenopsis invicta", "Fire-ant workers interlock into buoyant rafts and protect brood during floods.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3462402/", "A coordinated living surface distributes buoyancy."), "Muddy floodwater tears through ground routes."),
    DisasterCard("canopy_fragmentation", "Canopy Fragmentation", frozenset({"flood"}), OptimizationRequirement("Canopy Retreat", {"Movement": 3, "Nesting": 1, "Resource Ecology": 1}, "Cephalotes atratus and arboreal ants", "Gliding workers steer back to trunks, while arboreal nesting and foraging keep colonies above inundated ground.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2880152/", "A complete arboreal route avoids the flooded forest floor."), "Floodwater separates the remaining canopy refuges."),
    DisasterCard("desert_heat_wave", "Desert Heat Wave", frozenset({"heat", "drought"}), OptimizationRequirement("Silver-Hair Cooling", {"Morphology": 4, "Chemistry": 1}, "Cataglyphis bombycina", "Triangular silver hairs reflect sunlight and radiate heat; molecular heat responses protect cells.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4830450/", "Body structure and cellular protection sustain a brief hot run."), "Radiant heat and dry ground punish exposed foragers."),
    DisasterCard("prolonged_drought", "Prolonged Drought", frozenset({"drought"}), OptimizationRequirement("Underground Granary", {"Nesting": 3, "Resource Ecology": 2}, "Pogonomyrmex badius", "Workers store and process seeds in protected subterranean chambers.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5125654/", "A deep granary separates stored food from the dry surface."), "A long dry spell removes easy surface food."),
    DisasterCard("garden_epidemic", "Garden Epidemic", frozenset({"fungal"}), OptimizationRequirement("Symbiotic Fungus Garden", {"Chemistry": 3, "Resource Ecology": 2}, "Attine fungus-growing ants and Pseudonocardia", "Ant-associated bacteria inhibit Escovopsis parasites in cultivated fungus gardens.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3097832/", "Chemical symbionts protect a valuable cultivated resource."), "A specialist pathogen spreads through cultivated fungus."),
    DisasterCard("spore_contamination", "Spore Contamination", frozenset({"fungal"}), OptimizationRequirement("Infrabuccal Isolation", {"Morphology": 3, "Chemistry": 2}, "Fungus-growing ants (Attini)", "The infrabuccal pocket sequesters and helps sterilize fungal contaminants.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1617182/", "Mouthpart structure isolates spores for chemical treatment."), "Airborne spores contaminate workers and garden material."),
    DisasterCard("army_ant_raid", "Army Ant Raid", frozenset({"raid"}), OptimizationRequirement("Living Nest Gate", {"Caste": 3, "Morphology": 1, "Nesting": 1}, "Cephalotes varians", "Shield-headed soldiers fit narrow nest entrances and block intruders.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6436684/", "A specialized soldier caste turns nest architecture into a barricade."), "A coordinated rival column presses into the nest."),
    DisasterCard("post_raid_injuries", "Post-Raid Injuries", frozenset({"raid"}), OptimizationRequirement("Rescue Column", {"Cooperation": 4, "Movement": 1}, "Megaponera analis", "Workers carry injured nestmates home and treat infected wounds after termite raids.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "A coordinated mobile rescue route preserves experienced workers."), "Scattered injuries threaten the colony after combat."),
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
