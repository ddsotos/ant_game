"""人間が5ラウンドを最後まで遊べる最小CLI。"""

from __future__ import annotations

import argparse
from collections.abc import Callable

from .content import DISASTERS, TRAITS
from .engine import GameEngine, InvalidDecision
from .localization_ja import ROLE_NAMES, TAG_NAMES, card_name, event_name
from .models import GameState, Size


class HumanPolicy:
    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.ask = input_fn
        self.say = output_fn

    def choose_size(self, state: GameState, engine: GameEngine) -> Size:
        self._show_last_round(state)
        context = state.current_round
        assert context is not None
        environment = engine.current_disaster(state)
        self.say("\n" + "=" * 68)
        self.say(
            f"ラウンド {context.round_number}/5  環境変化: {event_name(environment.id, environment.name)}  "
            f"問題の実効出目 {context.problem_rolls}"
        )
        for problem, raw in context.problem_raw_rolls.items():
            selected = context.problem_selected_rolls[problem]
            bonus = context.problem_modifiers[problem]
            suffix = f" +{bonus}" if bonus else ""
            self.say(f"  {problem}: {list(raw)} → {selected}{suffix} = {context.problem_rolls[problem]}")
        forecast = " / ".join(
            f"R{number}:{event_name(item, engine.disasters[item].name)}"
            for number, item in enumerate(state.disaster_ids, start=1)
        )
        self.say(f"予報: {forecast}")
        self.say(
            f"繁栄 {state.prosperity}  手札 {len(state.hand)}/{engine.hand_limit}"
        )
        if environment.optimizations:
            self.say("最適化（いずれか1つ）:")
            for optimization in environment.optimizations:
                self.say(
                    "  " + optimization.name + " [" +
                    self._requirements(optimization.required_root_tags) + "]"
                )
        else:
            self.say("最適化なし（問題強化環境）")

        legal = engine.legal_sizes(state)
        self.say("\nサイズを選択:")
        for size in legal:
            self.say(
                f"  {size.name.lower():6}  繁栄倍率×{size.prosperity_multiplier}  "
                f"通常保持{engine.retention_curve[size]}枚"
            )
        by_name = {size.name.lower(): size for size in legal}
        while True:
            answer = self.ask("size> ").strip().lower()
            if answer in by_name:
                return by_name[answer]
            self.say("次から選択: " + ", ".join(by_name))

    def choose_retained(
        self,
        state: GameState,
        candidates: tuple[str, ...],
        engine: GameEngine,
    ) -> tuple[str, ...]:
        self.say("\n公開された通常カード:")
        for instance_id in candidates:
            self._show_card(engine.traits[instance_id], prefix=f"  {instance_id}")

        available = set(candidates)
        limit = min(engine.retention_limit(state), engine.hand_limit - len(state.hand))
        while True:
            raw = self.ask(
                f"保持するIDを最大{limit}枚、カンマ区切りで入力（空欄=0枚）> "
            ).strip()
            chosen = tuple(item.strip().lower() for item in raw.split(",") if item.strip())
            if (
                len(chosen) <= limit
                and len(chosen) == len(set(chosen))
                and set(chosen) <= available
            ):
                return chosen
            self.say("ID、重複、保持上限のいずれかが不正です。")

    def take_actions(self, state: GameState, engine: GameEngine) -> None:
        self.say("\n進化アクション。回数制限なし。`help`でコマンドを表示します。")
        self.show_status(state, engine)
        aliases = {
            "置く": "play",
            "支援": "support",
            "起動": "activate",
            "状態": "status",
            "カード": "card",
            "ヘルプ": "help",
            "終了": "done",
        }
        while True:
            parts = self.ask("action> ").strip().lower().split()
            if not parts:
                continue
            parts[0] = aliases.get(parts[0], parts[0])
            command = parts[0]
            try:
                if command == "done":
                    return
                if command == "help":
                    self._show_help()
                elif command == "status":
                    self.show_status(state, engine)
                elif command == "card" and len(parts) == 2:
                    if parts[1] not in engine.traits:
                        raise InvalidDecision("不明なカードIDです")
                    self._show_card(engine.traits[parts[1]], prefix=parts[1])
                elif command == "play" and len(parts) == 3:
                    pushed = engine.play_card(state, parts[1], int(parts[2]) - 1)
                    if pushed:
                        self.say("押し出し: " + ", ".join(pushed))
                    self._show_compact_state(state, engine)
                elif command == "support" and len(parts) == 3:
                    engine.insert_support(state, parts[1], int(parts[2]) - 1)
                    self._show_compact_state(state, engine)
                elif command == "activate" and len(parts) in (2, 3):
                    option = int(parts[2]) - 1 if len(parts) == 3 else 0
                    resolved = engine.activate(state, int(parts[1]) - 1, option)
                    self.say("起動: " + self._option_summary(resolved))
                    self._show_compact_state(state, engine)
                else:
                    self.say("コマンド形式が違います。`help`で確認してください。")
            except (InvalidDecision, ValueError) as exc:
                self.say(f"実行できません: {exc}")

    def show_status(self, state: GameState, engine: GameEngine) -> None:
        self._show_compact_state(state, engine)
        self.say("\n手札詳細:")
        if not state.hand:
            self.say("  （なし）")
        for instance in state.hand:
            self._show_card(engine.traits[instance.card_id], prefix=f"  {instance.instance_id}")

    def _show_compact_state(self, state: GameState, engine: GameEngine) -> None:
        context = state.current_round
        shield = sum(item.amount for item in context.shields) if context else 0
        round_prosperity = context.prosperity_base if context else 0
        self.say(
            f"\n手札: {', '.join(item.instance_id for item in state.hand) or 'なし'}  "
            f"今R繁栄={round_prosperity}  今Rシールド={shield}"
        )
        for column_index, column in enumerate(state.columns):
            entries = []
            for index, played in enumerate(column.cards):
                if index == len(column.cards) - 1:
                    marker = "先頭"
                elif played.is_support:
                    marker = "支援"
                else:
                    marker = "下層"
                entries.append(f"{played.instance_id}({marker})")
            tags = engine.column_tags(state, column_index)
            tag_text = ", ".join(
                f"{tag}:{count}" for tag, count in sorted(tags.items())
            ) or "なし"
            oldest = column.cards[0].instance_id if len(column.cards) >= engine.column_capacity else "—"
            self.say(
                f"  C{column_index + 1} [{len(column.cards)}/{engine.column_capacity}] "
                f"{' > '.join(entries) or '空'}"
            )
            self.say(f"     tags: {tag_text}  次の押し出し: {oldest}")
            top = column.top
            if top:
                card = engine.traits[top.card_id]
                activation_tags = engine.activation_tags(state, column_index)
                requirements_met = all(
                    activation_tags[tag] >= amount
                    for tag, amount in card.activation_requirements.items()
                )
                options = card.options if requirements_met else card.fallback_options
                tier = "強効果" if requirements_met else "条件未達・弱効果"
                for option_index, option in enumerate(options, start=1):
                    self.say(
                        f"     起動{option_index}（{tier}）: {self._option_summary(option)} "
                        f"条件[{self._requirements(card.activation_requirements)}]"
                    )

    def _show_last_round(self, state: GameState) -> None:
        if not state.history:
            return
        row = state.history[-1]
        self.say("\n前ラウンド結果:")
        self.say(
            f"  R{row.round_number} {event_name(row.disaster_id, row.disaster_id)} size={row.size.name}  "
            f"問題減点={row.problem_penalty} 最適化={'達成' if row.optimization_met else '未達'}  "
            f"繁栄=+{row.prosperity_delta}  total={row.total_prosperity}"
        )
        if row.pushed_out:
            self.say("  押し出されたカード: " + ", ".join(row.pushed_out))

    def _show_card(self, card, *, prefix: str) -> None:
        self.say(
            f"{prefix}: {card_name(card.id, card.name)}  {ROLE_NAMES.get(card.design_role, card.design_role)}  "
            f"tags[{', '.join(TAG_NAMES.get(tag, tag) for tag in sorted(card.root_tags))}]  "
            f"条件[{self._requirements(card.activation_requirements)}]"
        )
        for option_index, option in enumerate(card.options, start=1):
            self.say(f"     強効果{option_index}: {self._option_summary(option)}")
        for option_index, option in enumerate(card.fallback_options, start=1):
            self.say(f"     未達時{option_index}: {self._option_summary(option)}")
        self.say(f"     題材: {card.source_taxon}")
        self.say(f"     {card.text}")

    def _show_help(self) -> None:
        self.say("  play CARD COLUMN       カードを列の先頭へ置く（例: play card_id 1）")
        self.say("  support CARD COLUMN    効果を捨て、タグだけを列へ差し込む")
        self.say("  activate COLUMN [N]    先頭カードのN番目の効果を起動")
        self.say("  card CARD              カード詳細を再表示")
        self.say("  status                 手札・列・タグ・起動効果を表示")
        self.say("  done                   環境解決へ進む")
        self.say("  日本語別名: 置く / 支援 / 起動 / カード / 状態 / 終了")

    @staticmethod
    def _requirements(requirements) -> str:
        return ", ".join(
            f"{TAG_NAMES.get(tag, tag)} {amount}" for tag, amount in sorted(requirements.items())
        ) or "なし"

    @staticmethod
    def _option_summary(option) -> str:
        effects = []
        if option.prosperity:
            effects.append(f"繁栄+{option.prosperity}")
        for shield in option.shields:
            effects.append(
                f"{('襲撃' if shield.problem_id == 'raid' else '衛生' if shield.problem_id == 'sanitation' else shield.problem_id)}シールド+{shield.amount}"
            )
        if option.draw_cards:
            effects.append(f"即時ドロー+{option.draw_cards}")
        if option.retention_bonus:
            effects.append(f"次ラウンド保持+{option.retention_bonus}")
        for tag, coefficient in option.tag_prosperity:
            effects.append(f"盤面の{TAG_NAMES.get(tag, tag)}1つごとに繁栄+{coefficient}")
        if getattr(option, "store_hand_card", False):
            income = getattr(option, "storage_income_per_card", 0)
            effects.append(f"手札1枚を伏せて貯蔵（次ラウンド以降、毎ラウンド繁栄+{income}）")
        return " / ".join(effects) or "数値効果なし"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--list-disasters",
        action="store_true",
        help="環境変化IDを表示して終了",
    )
    args = parser.parse_args(argv)
    if args.list_disasters:
        for environment in DISASTERS:
            print(f"{environment.id}: {event_name(environment.id, environment.name)}")
        return 0

    engine = GameEngine(TRAITS, DISASTERS, seed=args.seed)
    state = engine.new_game()
    policy = HumanPolicy()
    print("アリ進化ゲーム v0.9 — 5ラウンド試作")
    print("開始時に全5ラウンドの環境と、複数最適化または問題強化が公開されます。")
    engine.run(policy, state)
    policy._show_last_round(state)
    print(
        f"\n最終結果: 繁栄={state.prosperity}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["HumanPolicy", "main"]
