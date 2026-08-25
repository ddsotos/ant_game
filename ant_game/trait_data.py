"""Load the canonical v0.16 trait-card snapshot into engine models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .models import ActionOption, CardRole, ShieldSpec, Size, SizeEffectSpec, TraitCard


TRAIT_DATA_PATH = Path(__file__).with_name("data") / "trait_cards_v0.16.json"

_ROLE_BY_LABEL = {
    "初期形質": (CardRole.STARTER, "Foundation"),
    "基盤": (CardRole.ACTION, "Foundation"),
    "完成形": (CardRole.ACTION, "Payoff"),
    "橋渡し": (CardRole.ACTION, "Bridge"),
}
_SIZE_BY_LABEL = {
    "Small": Size.SMALL,
    "Medium": Size.MEDIUM,
    "Large": Size.LARGE,
    "Giant": Size.GIANT,
}


def _shields(values: list[Mapping[str, Any]] | None) -> tuple[ShieldSpec, ...]:
    return tuple(ShieldSpec(str(item["problem_id"]), int(item["amount"])) for item in values or ())


def _size_effects(values: Mapping[str, Mapping[str, Any]] | None) -> tuple[SizeEffectSpec, ...]:
    effects: list[SizeEffectSpec] = []
    for label, raw in (values or {}).items():
        if label not in _SIZE_BY_LABEL:
            raise ValueError(f"unknown size label in trait data: {label}")
        effects.append(
            SizeEffectSpec(
                size=_SIZE_BY_LABEL[label],
                prosperity=int(raw.get("prosperity", 0)),
                shields=_shields(raw.get("shields")),
                environment_prosperity_loss_reduction=int(
                    raw.get("environment_prosperity_loss_reduction", 0)
                ),
                vulnerabilities=_shields(raw.get("vulnerabilities")),
                next_candidate_bonus=int(raw.get("next_candidate_bonus", 0)),
            )
        )
    return tuple(effects)


def _option(raw: Mapping[str, Any], *, size_effects: tuple[SizeEffectSpec, ...] = ()) -> ActionOption:
    return ActionOption(
        prosperity=int(raw.get("prosperity", 0)),
        shields=_shields(raw.get("shields")),
        draw_cards=int(raw.get("draw_cards", 0)),
        retention_bonus=int(raw.get("retention_bonus", 0)),
        recover_lower_card=bool(raw.get("recover_lower_card", False)),
        next_candidate_bonus=int(raw.get("next_candidate_bonus", 0)),
        store_hand_card=bool(raw.get("store_hand_card", False)),
        storage_income_per_card=int(raw.get("storage_income_per_card", 0)),
        tag_prosperity=tuple(
            (str(item["tag"]), int(item["coefficient"]))
            for item in raw.get("tag_prosperity", ())
        ),
        tag_prosperity_cap=(
            None if raw.get("tag_prosperity_cap") is None else int(raw["tag_prosperity_cap"])
        ),
        tag_prosperity_divisor=int(raw.get("tag_prosperity_divisor", 1)),
        environment_prosperity_loss_reduction=int(
            raw.get("environment_prosperity_loss_reduction", 0)
        ),
        vulnerabilities=_shields(raw.get("vulnerabilities")),
        size_effects=size_effects,
        candidate_bonus_when_reduce_retention_for_more_candidates=int(
            raw.get("candidate_bonus_when_reduce_retention_for_more_candidates", 0)
        ),
        prosperity_if_environment_has_no_optimizations=(
            None
            if raw.get("prosperity_if_environment_has_no_optimizations") is None
            else int(raw["prosperity_if_environment_has_no_optimizations"])
        ),
        text=str(raw.get("text", "")),
    )


def load_trait_cards(path: Path = TRAIT_DATA_PATH) -> tuple[TraitCard, ...]:
    """Parse and validate the complete trait-card data file."""

    document = json.loads(path.read_text(encoding="utf-8"))
    cards: list[TraitCard] = []
    for raw in document["cards"]:
        card_id = str(raw["id"])
        if raw.get("card_id", card_id) != card_id:
            raise ValueError(f"card_id does not match id: {card_id}")
        try:
            role, design_role = _ROLE_BY_LABEL[str(raw["role"])]
        except KeyError as exc:
            raise ValueError(f"unknown card role: {raw['role']}") from exc
        tags = frozenset(str(item["id"]) for item in raw["tags"])
        size_effects = _size_effects(raw.get("size_effects"))
        options = tuple(_option(item, size_effects=size_effects) for item in raw["options"])
        cards.append(
            TraitCard(
                id=card_id,
                name=str(raw["name"]),
                root_tags=tags,
                role=role,
                activation_requirements={
                    str(item["id"]): int(item["required"]) for item in raw["requirements"]
                },
                options=options,
                fallback_options=tuple(_option(item) for item in raw.get("fallback_options", ())),
                source_taxon=str(raw["subject_taxon"]),
                biology_basis=str(raw["biology_basis"]),
                biology_source=str(raw["biology_source"]),
                design_role=design_role,
                text=str(raw["text"]),
                root_tag_counts={str(item["id"]): int(item.get("count", 1)) for item in raw["tags"]},
                on_pushed_out=(
                    _option(raw["on_pushed_out"]) if raw.get("on_pushed_out") else None
                ),
            )
        )
    if len(cards) != int(document["count"]):
        raise ValueError("trait-card count does not match the data header")
    if len({card.id for card in cards}) != len(cards):
        raise ValueError("trait-card ids must be unique")
    return tuple(cards)


__all__ = ["TRAIT_DATA_PATH", "load_trait_cards"]
