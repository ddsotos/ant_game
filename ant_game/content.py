"""Data-driven ant evolution cards and forecastable disasters.

 The engine owns all resolution rules. This module only describes cards,
 options, and the forecastable environmental changes. Normal cards use five
 evolutionary root tags; recurring problems are limited to raid and sanitation.
"""

from __future__ import annotations

from types import MappingProxyType

from .models import (
    ActionOption,
    CardRole,
    DisasterCard,
    EnvironmentCard,
    OptimizationRequirement,
    ProblemRollRule,
    ShieldSpec,
    TraitCard,
)


ROOT_TAGS = frozenset({"Morphology", "Chemistry", "Sociality", "Nesting", "Resource Ecology"})


def _shield(problem_id: str, *, amount: int) -> ShieldSpec:
    return ShieldSpec(problem_id, amount)


def _action(
    card_id,
    name,
    tags,
    requirements,
    options,
    source_taxon,
    biology_basis,
    biology_source,
    design_role,
    text,
    fallback_options=(),
):
    # Foundation and Bridge cards are immediately usable. Payoffs alone ask
    # the rest of the column to establish a deliberately asymmetric build.
    if design_role != "Payoff":
        requirements = {}
    return TraitCard(id=card_id, name=name, root_tags=tags, role=CardRole.ACTION,
                     activation_requirements=requirements, options=options,
                     fallback_options=fallback_options,
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


# Forty normal cards. All are ACTION cards; strong options are gated by
# accumulated roots rather than by new currencies or bespoke effect ids.
NORMAL_TRAITS: tuple[TraitCard, ...] = (
    _action("oecophylla_silkworks", "Oecophylla Silkworks", frozenset({"Nesting", "Sociality"}), {}, (ActionOption(prosperity=1, text="Weave a protected canopy."),), "Oecophylla smaragdina", "Workers pull leaves together with silk produced by their larvae.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4896424/", "Foundation", "Larval silk turns sociality into a living canopy nest."),
    _action("oecophylla_living_chain", "Oecophylla Living Chain", frozenset({"Sociality"}), {"Sociality": 2}, (ActionOption(prosperity=5, draw_cards=1, text="Form a chain and extend the route."),), "Oecophylla smaragdina", "Workers form pulling and bridging chains to move across gaps and bend leaves.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3997362/", "Payoff", "A chain is treated as coordinated social labor; the temporary route is its consequence.", (ActionOption(prosperity=1, text="Gather a small group at the route."),)),
    _action("cephalotes_aerialis", "Cephalotes Aerialis", frozenset({"Morphology"}), {}, (ActionOption(shields=(_shield("raid", amount=1),), text="Steer a fall away from a hunter."),), "Cephalotes atratus", "Wingless workers steer their descent while falling from the canopy.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2880152/", "Foundation", "The distinctive adaptation is a flattened, steerable body; descent is not a separate root."),
    _action("cephalotes_living_gate", "Cephalotes Living Gate", frozenset({"Morphology", "Nesting"}), {"Sociality": 3, "Nesting": 1}, (ActionOption(prosperity=5, shields=(_shield("raid", amount=3),), text="Seal the entrance with a shield-shaped head."),), "Cephalotes varians", "Soldiers use shield-shaped heads as living barricades at nest entrances.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6436684/", "Payoff", "A specialized social caste becomes a door for a narrow nest entrance.", (ActionOption(shields=(_shield("raid", amount=1),), text="Partly seal the entrance."),)),
    _action("odontomachus_tension_lock", "Odontomachus Tension Lock", frozenset({"Morphology"}), {}, (ActionOption(prosperity=1, text="Snap at prey or rivals."), ActionOption(shields=(_shield("raid", amount=1),), text="Use the snap to launch away.")), "Odontomachus bauri and O. brunneus", "A latch-spring mandible strikes prey and can propel an ant away from danger.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1568925/", "Bridge", "The latch-spring mandible is a single morphological innovation; its launch effect is incidental."),
    _action("pheidole_supermajor_program", "Pheidole Supermajor Program", frozenset({"Sociality", "Morphology"}), {"Sociality": 3, "Morphology": 1}, (ActionOption(prosperity=5, shields=(_shield("raid", amount=3),), text="Deploy an oversized defender."),), "Pheidole rhea and P. obtusospinosa", "Some species produce a third, supersoldier worker caste with specialized defenses.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3334560/", "Payoff", "A costly social program creates a conspicuous defender.", (ActionOption(shields=(_shield("raid", amount=1),), text="Deploy a smaller defender."),)),
    _action("pheidole_seed_miller", "Pheidole Seed Miller", frozenset({"Sociality", "Morphology", "Resource Ecology"}), {"Sociality": 2, "Resource Ecology": 2}, (ActionOption(prosperity=5, tag_prosperity=(("Resource Ecology", 1),), text="Process a hard seed harvest."),), "Pheidole tepicana", "Supersoldiers in this species specialize in seed milling.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3334560/", "Payoff", "The same social root can branch from defense into food processing.", (ActionOption(prosperity=1, text="Process a small seed harvest."),)),
    _action("myrmecocystus_reserve", "Myrmecocystus Reserve", frozenset({"Sociality", "Resource Ecology"}), {"Sociality": 1, "Resource Ecology": 1}, (ActionOption(prosperity=5, store_hand_card=True, storage_income_per_card=1, text="Hide one hand card in a living reserve."),), "Myrmecocystus spp.", "Replete workers store liquid food in their crops for long periods.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Payoff", "A specialized storage caste makes waiting strategically viable.", (ActionOption(prosperity=1, text="Release a small liquid reserve."),)),
    _action("megaponera_field_medicine", "Megaponera Field Medicine", frozenset({"Chemistry", "Sociality"}), {"Sociality": 3, "Chemistry": 1}, (ActionOption(prosperity=5, shields=(_shield("sanitation", amount=3),), text="Treat an infected wound."),), "Megaponera analis", "Workers apply antimicrobial gland secretions to infected wounds and sharply reduce mortality.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10756881/", "Payoff", "Chemical treatment becomes reliable only when a coordinated care group can deliver it.", (ActionOption(shields=(_shield("sanitation", amount=1),), text="Apply a limited wound treatment."),)),
    _action("megaponera_rescue_column", "Megaponera Rescue Column", frozenset({"Sociality"}), {}, (ActionOption(shields=(_shield("raid", amount=1),), text="Carry an injured nestmate home."),), "Megaponera analis", "Returning raiders carry injured nestmates back to the nest after termite fights.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "Bridge", "The adaptation is collective rescue; travel is merely the context in which cooperation matters."),
    _action("colobopsis_last_defense", "Colobopsis Last Defense", frozenset({"Chemistry", "Morphology"}), {"Nesting": 3, "Chemistry": 1}, (ActionOption(prosperity=5, shields=(_shield("raid", amount=3),), text="Rupture a gland to stop an intruder."),), "Colobopsis explodens", "Minor workers can rupture enlarged gland reservoirs and repel rivals with sticky irritant secretions.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5919914/", "Payoff", "The strongest defense is a deliberately terminal commitment.", (ActionOption(shields=(_shield("raid", amount=1),), text="Release a smaller irritant burst."),)),
    _action("paraponera_poneratoxin", "Paraponera Poneratoxin", frozenset({"Chemistry"}), {"Morphology": 3, "Chemistry": 1}, (ActionOption(prosperity=5, text="Make a rival pay for approaching."), ActionOption(prosperity=5, shields=(_shield("raid", amount=3),), text="Deter an attack with venom.")), "Paraponera clavata", "Its venom contains poneratoxin-like sodium-channel toxins causing intense prolonged pain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10206162/", "Payoff", "Venom is an expensive but memorable chemical weapon.", (ActionOption(prosperity=1, text="Threaten a rival."), ActionOption(shields=(_shield("raid", amount=1),), text="Deter part of an attack."))),
    _action("apterostigma_dentigerumycin", "Apterostigma Dentigerumycin", frozenset({"Chemistry", "Resource Ecology"}), {}, (ActionOption(shields=(_shield("sanitation", amount=1),), text="Suppress the garden parasite."),), "Apterostigma dentigerum", "A Pseudonocardia symbiont produces dentigerumycin that inhibits the garden parasite Escovopsis.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2748230/", "Bridge", "A microbial partner joins chemistry to cultivated resources."),
    _action("acromyrmex_antibiotic_garden", "Acromyrmex Antibiotic Garden", frozenset({"Chemistry", "Resource Ecology"}), {"Nesting": 3, "Chemistry": 1}, (ActionOption(prosperity=5, shields=(_shield("sanitation", amount=3),), text="Protect the cultivated crop."),), "Acromyrmex octospinosus and related leafcutters", "Leafcutting ants use Pseudonocardia and gland secretions against Escovopsis.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3418327/", "Payoff", "A mature garden makes disease resistance powerful but specialized.", (ActionOption(shields=(_shield("sanitation", amount=1),), text="Protect one garden patch."),)),
    _action("atta_fungus_garden", "Atta Fungus Garden", frozenset({"Resource Ecology"}), {}, (ActionOption(prosperity=2, text="Harvest cultivated fungal food."),), "Atta colombica", "Workers provision a fungal cultivar with leaves and consume its nutrient-rich structures.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9019514/", "Foundation", "Fungiculture converts plant biomass into dependable prosperity."),
    _action("attine_infrabuccal_pocket", "Attine Infrabuccal Pocket", frozenset({"Chemistry", "Morphology"}), {}, (ActionOption(shields=(_shield("sanitation", amount=1),), text="Sterilize and remove infected material."),), "Fungus-growing ants (Attini)", "The infrabuccal pocket helps sequester and sterilize Escovopsis material.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1617182/", "Bridge", "Sanitation links mouthpart morphology to chemical defense."),
    _action("cataglyphis_silver_hair", "Cataglyphis Silver Hair", frozenset({"Morphology"}), {}, (ActionOption(prosperity=1, text="Reflect and radiate desert heat."),), "Cataglyphis bombycina", "Triangular reflective hairs reduce internal heating under intense sunlight.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4830450/", "Bridge", "A visible body adaptation supports the thermal optimization."),
    _action("cataglyphis_sky_compass", "Cataglyphis Sky Compass", frozenset({"Resource Ecology"}), {"Resource Ecology": 2}, (ActionOption(prosperity=5, draw_cards=1, text="Discover another option by the shortest known route."),), "Cataglyphis fortis", "Desert foragers use path integration and polarized skylight to return across featureless terrain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1567920/", "Payoff", "The compass preserves access to a food route, so it is represented as resource ecology rather than a movement axis.", (ActionOption(prosperity=1, text="Follow a remembered route."),)),
    _action("pheidole_raid_wall", "Pheidole Raid Wall", frozenset({"Sociality", "Morphology"}), {"Nesting": 3, "Morphology": 1}, (ActionOption(prosperity=5, shields=(_shield("raid", amount=3),), text="Coordinate supermajors at the entrance."),), "Pheidole obtusospinosa", "Supermajors and workers use multiple defensive phases against invading army ants.", "https://academic.oup.com/jinsectscience/article/10/1/1/820704", "Payoff", "Sociality and collective defense combine against a known rival route.", (ActionOption(shields=(_shield("raid", amount=1),), text="Coordinate a smaller defensive line."),)),
    _action("harpegnathos_gamergate", "Harpegnathos Gamergate", frozenset({"Sociality"}), {}, (ActionOption(prosperity=1, text="Let a worker become a reproductive option."),), "Harpegnathos saltator", "Workers can reversibly enter a reproductive gamergate caste after queen loss.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7919410/", "Bridge", "Social state can remain flexible without a separate caste tag."),
    _action("temnothorax_quorum_nest", "Temnothorax Quorum Nest", frozenset({"Sociality", "Nesting"}), {}, (ActionOption(prosperity=1, text="Recruit toward the best available cavity."),), "Temnothorax albipennis and T. curvispinosus", "Scouts recruit nestmates and use quorum-like feedback to choose new nest sites.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2817311/", "Bridge", "Collective information makes a nest choice without central control."),
    _action("pogonomyrmex_granary", "Pogonomyrmex Granary", frozenset({"Resource Ecology", "Nesting"}), {"Nesting": 2, "Resource Ecology": 2}, (ActionOption(prosperity=5, store_hand_card=True, storage_income_per_card=1, retention_bonus=1, text="Hide one hand card in a protected seed chamber."),), "Pogonomyrmex badius", "Workers store seeds in damp subterranean chambers and use germination to process large seeds.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5125654/", "Payoff", "A granary rewards preparing before scarcity arrives.", (ActionOption(prosperity=1, text="Use a small seed reserve."),)),
    _action("paltothyreus_distress_signal", "Paltothyreus Distress Signal", frozenset({"Chemistry", "Sociality"}), {}, (ActionOption(shields=(_shield("raid", amount=1),), text="Call nestmates to a trapped worker."),), "Paltothyreus tarsatus", "Mandibular-gland compounds released by trapped workers attract nestmates to dig and rescue them.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5731505/", "Bridge", "A chemical alarm converts an individual incident into a group response."),
    _action("solenopsis_dry_store", "Solenopsis Dry Store", frozenset({"Resource Ecology"}), {"Sociality": 3, "Resource Ecology": 1}, (ActionOption(prosperity=5, store_hand_card=True, storage_income_per_card=1, text="Dry and hide one hand card for a later shortage."),), "Solenopsis invicta", "Fire ants dry and store insect pieces for later use; honeypot-like storage is an ant adaptation.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Payoff", "Immediate prosperity can be converted into a future option.", (ActionOption(prosperity=1, text="Dry a modest food store."),)),
    _action("solenopsis_raft_cycling", "Solenopsis Raft Cycling", frozenset({"Sociality"}), {}, (ActionOption(prosperity=1, text="Cycle workers through a living raft."),), "Solenopsis invicta", "Workers cycle through floating rafts and protect brood during prolonged flooding.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3462402/", "Bridge", "Collective buoyancy is a social organization of bodies; cycling is not a separate root."),
    _action("atta_leaf_cache", "Atta Leaf Cache", frozenset({"Resource Ecology"}), {"Resource Ecology": 1, "Nesting": 1}, (ActionOption(prosperity=5, store_hand_card=True, storage_income_per_card=1, text="Hide one hand card beside the blocked entrance."),), "Atta cephalotes and A. colombica", "Foragers can deposit leaf fragments outside a temporarily blocked nest entrance as a cache.", "https://www.sciencedirect.com/science/article/pii/S0003347299913325", "Payoff", "A short-term cache preserves a harvest while access is constrained.", (ActionOption(prosperity=1, text="Preserve a small leaf cache."),)),
    _action("acromyrmex_spore_removal", "Acromyrmex Spore Removal", frozenset({"Chemistry", "Sociality"}), {}, (ActionOption(shields=(_shield("sanitation", amount=1),), text="Remove spores and contaminated garden material."),), "Acromyrmex leafcutter ants", "Workers physically remove Escovopsis spores and mycelium alongside chemical defenses.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3418327/", "Bridge", "A behavioral sanitation route can complement microbial antibiotics."),
    _action("cataglyphis_heatshock_proteins", "Cataglyphis Heatshock Proteins", frozenset({"Chemistry"}), {}, (ActionOption(prosperity=1, text="Protect cellular machinery during a hot run."),), "Cataglyphis bombycina", "Heat-adapted ants show constitutive and inducible molecular chaperone responses to thermal stress.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6003908/", "Bridge", "A less visible thermal route contributes to the environmental optimization."),
    _action("megaponera_termite_raid", "Megaponera Termite Raid", frozenset({"Sociality", "Resource Ecology"}), {}, (ActionOption(prosperity=2, text="Bring home a coordinated termite harvest."), ActionOption(shields=(_shield("raid", amount=1),), text="Keep the raid column together.")), "Megaponera analis", "This species performs group raids on highly defensive termites, with specialized task division.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5389746/", "Bridge", "A profitable raid is tempting even when it exposes the colony to injury."),
    _action("temnothorax_emergency_emigration", "Temnothorax Emergency Emigration", frozenset({"Nesting"}), {}, (ActionOption(prosperity=1, text="Move before the cavity becomes unsafe."),), "Temnothorax albipennis", "Colonies emigrate from fragile cavities when their current nest is damaged or deteriorates.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3101226/", "Bridge", "The decision is about preserving a viable nest; relocation is the response, not a root tag."),
    _action("lasius_sealed_foundation", "Lasius Sealed Foundation", frozenset({"Nesting", "Resource Ecology"}), {}, (ActionOption(prosperity=1, text="Seal a new colony's first chamber."),), "Lasius niger", "Claustral Lasius niger queens raise their first worker generation from stored reserves without foraging.", "https://academic.oup.com/biolinnean/article/142/4/397/7342048", "Foundation", "A sealed founding chamber turns stored reserves into the first generation."),
    _action("diacamma_gemma_inheritance", "Diacamma Gemma Inheritance", frozenset({"Morphology", "Sociality"}), {"Nesting": 2}, (ActionOption(prosperity=5, retention_bonus=1, text="Pass reproductive potential to a successor worker."),), "Diacamma sp.", "All newly emerged females bear thoracic gemmae; the reproductive worker removes them from nestmates, leaving a future successor with reproductive potential.", "https://pubmed.ncbi.nlm.nih.gov/15647944/", "Payoff", "A physical reproductive reserve makes succession possible without a queen.", (ActionOption(prosperity=1, text="Protect a possible successor."),)),
    _action("platythyrea_clone_watch", "Platythyrea Clone Watch", frozenset({"Sociality"}), {}, (ActionOption(prosperity=1, text="Guard a clonal brood line."),), "Platythyrea punctata", "Clonal workers reproduce by thelytokous parthenogenesis, while policing limits the number of simultaneous reproductives.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC240705/", "Foundation", "Clonal reproduction makes social continuity a direct colony investment."),
    _action("ooceraea_synchronized_brood", "Ooceraea Synchronized Brood", frozenset({"Chemistry", "Sociality"}), {"Resource Ecology": 2}, (ActionOption(prosperity=5, draw_cards=1, retention_bonus=1, text="Synchronize reproduction and reveal another route."),), "Ooceraea biroi", "Clonal raider ant colonies alternate synchronized reproductive and brood-care or foraging phases.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8244912/", "Payoff", "A colony-wide reproductive rhythm makes the next foraging window predictable.", (ActionOption(prosperity=1, text="Keep the brood cycle together."),)),
    _action("mycocepurus_clonal_garden", "Mycocepurus Clonal Garden", frozenset({"Sociality", "Resource Ecology"}), {"Nesting": 2}, (ActionOption(prosperity=5, tag_prosperity=(("Resource Ecology", 1),), text="Harvest a garden maintained by clonal workers."),), "Mycocepurus smithii", "Documented asexual Mycocepurus smithii populations combine thelytokous queen reproduction with obligate fungus farming.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2686657/", "Payoff", "Clonal continuity and fungus cultivation reinforce a specialized food base.", (ActionOption(prosperity=1, text="Harvest a small clonal garden."),)),
    _action("cardiocondyla_dual_males", "Cardiocondyla Dual Males", frozenset({"Morphology", "Sociality"}), {"Resource Ecology": 2}, (ActionOption(prosperity=5, retention_bonus=1, text="Use winged and wingless males for two reproductive routes."), ActionOption(prosperity=5, draw_cards=1, text="Open a reproductive alternative.")), "Cardiocondyla obscurior", "Cardiocondyla obscurior produces wingless fighter males that remain in the nest and peaceful winged males that can disperse.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3066177/", "Payoff", "Two male morphs preserve both local competition and dispersal.", (ActionOption(prosperity=1, text="Keep one reproductive route open."),)),
    _action("vollenhovia_three_lineage", "Vollenhovia Three Lineage", frozenset({"Sociality"}), {}, (ActionOption(prosperity=1, text="Maintain three reproductive lineages in one colony."),), "Vollenhovia emeryi", "Queens and males can be clonally produced from maternal and paternal genomes, while workers are predominantly sexually produced.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1686177/", "Bridge", "Lineage diversity turns a colony into a living reproductive network."),
    _action("pristomyrmex_worker_queens", "Pristomyrmex Worker Queens", frozenset({"Sociality"}), {"Nesting": 2}, (ActionOption(prosperity=5, retention_bonus=1, text="Let a worker carry the colony's reproductive future."),), "Pristomyrmex punctatus", "Queenless colonies contain monomorphic females that first reproduce thelytokously and later perform cooperative work.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2664351/", "Payoff", "Reproduction is distributed through the worker force rather than held by one queen.", (ActionOption(prosperity=1, text="Keep a worker reproductive option."),)),
    _action("formica_resin_pharmacy", "Formica Resin Pharmacy", frozenset({"Chemistry", "Nesting"}), {}, (ActionOption(shields=(_shield("sanitation", amount=1),), text="Line the nest with antimicrobial resin."),), "Formica paralugubris", "Formica paralugubris collects conifer resin and places it in the nest, reducing microbial growth.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2275180/", "Bridge", "A nest material doubles as a chemical sanitation system."),
    _action("myrmica_funeral_workers", "Myrmica Funeral Workers", frozenset({"Sociality", "Nesting"}), {}, (ActionOption(shields=(_shield("sanitation", amount=1),), text="Remove a dead nestmate before decay spreads."),), "Myrmica rubra", "Myrmica rubra workers detect and remove corpses, limiting the time dead nestmates remain in the colony.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11632371/", "Bridge", "Division of corpse removal keeps sanitation from depending on one specialist."),
)


DISASTERS: tuple[DisasterCard, ...] = (
    EnvironmentCard(
        "flood", "Flood", (
            OptimizationRequirement("生体いかだ", {"Sociality": 4, "Morphology": 2}, "Solenopsis invicta", "Fire ants interlock into buoyant rafts and cycle workers through the water.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3462402/", "Collective buoyancy keeps brood above floodwater."),
            OptimizationRequirement("樹冠退避", {"Nesting": 4, "Morphology": 2, "Resource Ecology": 2}, "Cephalotes atratus and arboreal ants", "Arboreal ants steer falls and use canopy routes above inundated ground.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2880152/", "A high refuge avoids the flooded ground entirely."),
        ), {}, "Floodwater tears through ground routes and separates canopy refuges."),
    EnvironmentCard(
        "desert_heat_wave", "Desert Heat Wave", (
            OptimizationRequirement("銀毛放熱", {"Morphology": 5}, "Cataglyphis bombycina", "Triangular reflective hairs reduce solar heating under intense sunlight.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4830450/", "Reflective body structure sustains a hot run."),
            OptimizationRequirement("熱ショック応答", {"Chemistry": 5}, "Cataglyphis bombycina", "Constitutive and inducible heat-shock responses protect cellular machinery.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6003908/", "Cellular protection supports activity at extreme temperature."),
        ), {}, "Radiant heat and dry ground punish exposed foragers."),
    EnvironmentCard(
        "prolonged_drought", "Prolonged Drought", (
            OptimizationRequirement("地下穀倉", {"Nesting": 4, "Resource Ecology": 3}, "Pogonomyrmex badius", "Workers store and process seeds in protected subterranean chambers.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5125654/", "A deep granary separates stored food from the dry surface."),
            OptimizationRequirement("貯蔵個体", {"Sociality": 4, "Resource Ecology": 3}, "Myrmecocystus spp.", "Replete workers store liquid food in their crops for long periods.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127378/", "Living storage buffers a colony through a dry spell."),
        ), {}, "A long dry spell removes easy surface food."),
    EnvironmentCard(
        "habitat_instability", "Habitat Instability", (
            OptimizationRequirement("定足数移住", {"Sociality": 4, "Nesting": 3}, "Temnothorax albipennis", "Scouts use quorum-like feedback to choose a new cavity before the old one fails.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2817311/", "Collective site choice makes emigration timely."),
            OptimizationRequirement("樹冠再建", {"Nesting": 4, "Sociality": 2, "Morphology": 2}, "Oecophylla smaragdina", "Workers pull leaves together with larval silk to rebuild a living canopy nest.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4896424/", "A rebuilt canopy replaces a failing ground shelter."),
        ), {}, "Substrate and shelter deteriorate while colonies compete for safe cavities."),
    EnvironmentCard(
        "landmark_loss", "Landmark Loss", (
            OptimizationRequirement("天空コンパス", {"Resource Ecology": 5, "Morphology": 1}, "Cataglyphis fortis", "Desert foragers use path integration and polarized skylight to return across featureless terrain.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1567920/", "A celestial route preserves access when familiar landmarks disappear."),
            OptimizationRequirement("フェロモン経路網", {"Chemistry": 4, "Sociality": 3}, "Formicidae", "Ants reinforce chemical trails and recruit nestmates to preserve routes.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3772619/", "A redundant chemical network replaces erased visual landmarks."),
        ), {}, "Wind and shifting substrate erase the routes used to reach food."),
    EnvironmentCard(
        "dry_savanna", "Dry Savanna", (), {"raid": ProblemRollRule(rolls=2, bonus=0), "sanitation": ProblemRollRule(rolls=1, bonus=0)}, "Seasonal resource concentration intensifies competition between neighboring colonies."),
    EnvironmentCard(
        "wet_tropical_floor", "Wet Tropical Forest Floor", (), {"raid": ProblemRollRule(rolls=1, bonus=0), "sanitation": ProblemRollRule(rolls=1, bonus=2)}, "Warm, wet litter and dense organic matter make colony sanitation unusually difficult."),
    EnvironmentCard(
        "urban_disturbance", "Urban Disturbance", (), {"raid": ProblemRollRule(rolls=1, bonus=1), "sanitation": ProblemRollRule(rolls=1, bonus=1)}, "Crowding, invasive neighbors, waste, and broken nesting sites amplify both recurring problems."),
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
