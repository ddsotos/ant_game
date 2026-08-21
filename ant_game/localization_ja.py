"""人間向けUI専用の日本語表示。ゲーム内部IDとルールには影響しない。"""

from __future__ import annotations

from .models import ActionOption, ShieldSpec


TAG_NAMES = {
    "Morphology": "形態", "Chemistry": "化学", "Cooperation": "協同",
    "Caste": "カースト", "Nesting": "巣作り", "Movement": "移動",
    "Resource Ecology": "資源生態",
}
HAZARD_NAMES = {
    "flood": "洪水", "heat": "暑熱", "drought": "乾燥",
    "fungal": "菌害", "raid": "襲撃",
}
SIZE_NAMES = {"SMALL": "小型", "MEDIUM": "中型", "LARGE": "大型", "GIANT": "超大型"}
ROLE_NAMES = {"Foundation": "基盤", "Payoff": "完成形", "Bridge": "橋渡し", "Extreme": "切り札"}

EVENT_NAMES = {
    "flood_front": ("洪水前線", "増水が、筏と樹冠への退避経路を試す。"),
    "desert_heat_wave": ("砂漠熱波", "熱と乾燥した地表が、巣外活動を危険にする。"),
    "garden_blight": ("菌園病害", "菌園に特化した寄生菌が、栽培食料を脅かす。"),
    "army_ant_raid": ("軍隊アリ襲撃", "統率された侵入群が、巣口防衛と救護能力を試す。"),
}

CARD_NAMES = {
    "trail_pheromone": "道しるべフェロモン",
    "earthwork_nest": "土中の巣",
    "collective_foraging": "集団採餌",
    "oecophylla_silkworks": "ツムギアリの絹建築",
    "oecophylla_living_chain": "ツムギアリの生きた鎖",
    "cephalotes_aerialis": "カメアリの滑空",
    "cephalotes_living_gate": "カメアリの生体門",
    "odontomachus_tension_lock": "トラップジョーの弾性顎",
    "pheidole_supermajor_program": "オオズアリの超大型兵隊",
    "pheidole_seed_miller": "オオズアリの種子粉砕兵",
    "myrmecocystus_reserve": "ミツツボアリの生体貯蔵",
    "megaponera_field_medicine": "マタベレアリの野戦治療",
    "megaponera_rescue_column": "マタベレアリの救護隊列",
    "colobopsis_last_defense": "爆発アリの最終防衛",
    "paraponera_poneratoxin": "サシハリアリの強毒",
    "apterostigma_dentigerumycin": "菌栽培アリの共生抗菌物質",
    "acromyrmex_antibiotic_garden": "ハキリアリの抗菌菌園",
    "atta_fungus_garden": "ハキリアリの菌類農業",
    "attine_infrabuccal_pocket": "菌栽培アリの口腔下ポケット",
    "cataglyphis_silver_hair": "サハラギンアリの銀毛",
    "cataglyphis_sky_compass": "砂漠アリの天空コンパス",
    "pheidole_raid_wall": "オオズアリの迎撃壁",
    "harpegnathos_gamergate": "ハリアリの繁殖ワーカー",
    "temnothorax_quorum_nest": "ムネボソアリの定足数決定",
    "pogonomyrmex_granary": "収穫アリの地下穀倉",
    "paltothyreus_distress_signal": "救助を呼ぶ遭難信号",
    "solenopsis_dry_store": "ヒアリの乾燥貯蔵",
    "solenopsis_raft_cycling": "ヒアリ筏の交代運用",
    "atta_leaf_cache": "ハキリアリの葉片仮置場",
    "acromyrmex_spore_removal": "ハキリアリの胞子除去",
    "cataglyphis_heatshock_proteins": "砂漠アリの熱ショック応答",
    "megaponera_termite_raid": "マタベレアリのシロアリ襲撃",
    "temnothorax_emergency_emigration": "ムネボソアリの緊急引越し",
    "solenopsis_ark": "ヒアリの生きた方舟",
    "canopy_escape": "カメアリの樹冠退避",
    "silver_thermal_coat": "サハラギンアリの銀色断熱毛",
    "deep_granary": "収穫アリの深層穀倉",
    "microbial_garden_partner": "菌園を守る微生物共生",
    "selective_antibiotic_pocket": "選別抗菌ポケット",
    "head_barricade": "カメアリの頭部バリケード",
    "rescue_scouts": "マタベレアリの救助斥候",
}

CARD_TEXTS = {
    "trail_pheromone": "化学の道標で、新しい採餌経路を今すぐ見つける。",
    "earthwork_nest": "維持された土中空間へ、次に使える選択肢を蓄える。",
    "collective_foraging": "仲間を食料へ動員し、繁栄へつなげる。",
    "oecophylla_silkworks": "幼虫の絹と協同作業で、生きた葉の巣を織る。",
    "oecophylla_living_chain": "多数の体を一時的な橋へ変える。",
    "cephalotes_aerialis": "落下を操り、捕食者から離れる方向へ滑空する。",
    "cephalotes_living_gate": "盾形の頭を持つ兵隊が、狭い巣口そのものになる。",
    "odontomachus_tension_lock": "ばね仕掛けの顎を、攻撃にも緊急脱出にも使う。",
    "pheidole_supermajor_program": "大きな投資で、目立つ超大型防衛個体を生み出す。",
    "pheidole_seed_miller": "大型兵の顎を、硬い種子の加工へ転用する。",
    "myrmecocystus_reserve": "液体食料を蓄える個体が、未来の選択肢を保存する。",
    "megaponera_field_medicine": "抗菌分泌物で負傷個体を治療し、狩りの損失を抑える。",
    "megaponera_rescue_column": "負傷した仲間を巣へ運び、働き手を将来へ残す。",
    "colobopsis_last_defense": "粘着性の分泌物を放つ自己犠牲で侵入者を止める。",
    "paraponera_poneratoxin": "強烈な毒が、攻撃と抑止の両方を担う。",
    "apterostigma_dentigerumycin": "共生微生物の抗菌物質が菌園寄生者を抑える。",
    "acromyrmex_antibiotic_garden": "成熟した菌園を、微生物と分泌物で専門的に守る。",
    "atta_fungus_garden": "葉を菌類の作物へ変え、安定した食料を得る。",
    "attine_infrabuccal_pocket": "感染物を隔離・除去する口器構造で菌園を衛生化する。",
    "cataglyphis_silver_hair": "三角形の銀毛が日射を反射し、体温上昇を抑える。",
    "cataglyphis_sky_compass": "偏光と経路積算で、目印のない砂漠から帰還する。",
    "pheidole_raid_wall": "大型兵とワーカーを巣口へ集め、侵入隊を段階的に阻む。",
    "harpegnathos_gamergate": "ワーカーが繁殖個体へ移行できる柔軟なカーストを持つ。",
    "temnothorax_quorum_nest": "偵察個体の情報を集め、中央指揮なしで新居を決める。",
    "pogonomyrmex_granary": "地下室の種子備蓄が、欠乏前の準備を報いる。",
    "paltothyreus_distress_signal": "閉じ込められた個体の化学信号が仲間の救助を呼ぶ。",
    "solenopsis_dry_store": "食料を乾燥保存し、今の収穫を未来の余裕へ変える。",
    "solenopsis_raft_cycling": "筏の位置を交代しながら、長い洪水を耐え抜く。",
    "atta_leaf_cache": "混雑時に葉片を仮置きし、採餌の流れを止めない。",
    "acromyrmex_spore_removal": "胞子と汚染部を物理的に取り除き、化学防御を補う。",
    "cataglyphis_heatshock_proteins": "分子シャペロンが、高温下の細胞機能を守る。",
    "megaponera_termite_raid": "危険な集団狩りで、大きな食料収入を狙う。",
    "temnothorax_emergency_emigration": "傷んだ巣を捨て、危険が迫る前に移住する。",
    "solenopsis_ark": "働きアリが体を連結し、幼虫ごと水面を渡る。",
    "canopy_escape": "水に耐える代わりに、樹上経路へ逃れる。",
    "silver_thermal_coat": "特殊な銀毛が、熱波の頂点を直接しのぐ。",
    "deep_granary": "深い地下備蓄が、乾燥した地表から資源を守る。",
    "microbial_garden_partner": "共生細菌の抗菌作用で、菌園病害を抑え込む。",
    "selective_antibiotic_pocket": "病原体を隔離して殺菌し、広がる前に処理する。",
    "head_barricade": "盾形の頭を巣口にはめ込み、侵入者を遮断する。",
    "rescue_scouts": "危険へ出ながら負傷者を回収し、働き手を守る。",
}


def card_name(card_id: str, fallback: str = "") -> str:
    return CARD_NAMES.get(card_id, fallback or card_id)


def event_name(event_id: str, fallback: str = "") -> str:
    return EVENT_NAMES.get(event_id, (fallback or event_id, ""))[0]


def tags_text(tags) -> list[str]:
    return [TAG_NAMES.get(tag, tag) for tag in sorted(tags)]


def requirement_text(requirements) -> str:
    if not requirements:
        return "条件なし"
    return "・".join(f"{TAG_NAMES.get(tag, tag)} {amount}" for tag, amount in sorted(requirements.items()))


def shield_text(shield: ShieldSpec) -> str:
    hazards = "・".join(HAZARD_NAMES.get(tag, tag) for tag in sorted(shield.hazard_tags))
    return f"{hazards}シールド +{shield.amount}"


def option_text(option: ActionOption) -> str:
    parts: list[str] = []
    if option.prosperity:
        parts.append(f"繁栄 +{option.prosperity}")
    parts.extend(shield_text(shield) for shield in option.shields)
    if option.draw_cards:
        parts.append(f"カードを今すぐ{option.draw_cards}枚引く")
    if option.retain_bonus:
        parts.append(f"次ラウンドの保持上限 +{option.retain_bonus}")
    return "／".join(parts) or "数値効果なし"
