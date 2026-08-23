"""人間向けUI専用の日本語表示。ゲーム内部IDとルールには影響しない。"""

from __future__ import annotations

from .models import ActionOption, ShieldSpec


TAG_NAMES = {
    "Morphology": "形態", "Chemistry": "化学", "Sociality": "社会性",
    "Nesting": "巣作り",
    "Resource Ecology": "資源生態",
}
TAG_COLORS = {
    "Morphology": "#0072B2", "Chemistry": "#E69F00", "Sociality": "#009E73",
    "Nesting": "#CC79A7",
    "Resource Ecology": "#F0E442",
}
TAG_SYMBOLS = {
    "Morphology": "mandibles", "Chemistry": "droplet", "Sociality": "linked-ants",
    "Nesting": "nest",
    "Resource Ecology": "leaf-seed",
}
PROBLEM_NAMES = {
    "raid": "襲撃", "sanitation": "衛生",
}
SIZE_NAMES = {"SMALL": "小型", "MEDIUM": "中型", "LARGE": "大型", "GIANT": "超大型"}
ROLE_NAMES = {"Foundation": "基盤", "Payoff": "完成形", "Bridge": "橋渡し"}

EVENT_NAMES = {
    "flood": ("洪水", "洪水が地上の経路を押し流し、樹冠を分断する。"),
    "desert_heat_wave": ("砂漠熱波", "強い日射と乾いた地表が巣外活動を危険にする。"),
    "prolonged_drought": ("長期乾燥", "長い乾季が地表の食料を失わせる。"),
    "habitat_instability": ("居住地不安定化", "巣の空間と基盤が劣化し、現在の居住地が危うくなる。"),
    "landmark_loss": ("目印消失", "風と地表変化が採餌路の目印を消す。"),
    "dry_savanna": ("乾季サバンナ", "資源が集中し、近隣コロニーとの競争が激しくなる。"),
    "wet_tropical_floor": ("湿潤熱帯林床", "高温多湿の落葉層が衛生維持を難しくする。"),
    "urban_disturbance": ("都市攪乱地", "混雑、侵入者、廃棄物、壊れた営巣地が重なる。"),
}

OPTIMIZATION_NAMES = {
    "flood": "生体いかだ／樹冠退避",
    "desert_heat_wave": "銀毛放熱／熱ショック応答",
    "prolonged_drought": "地下穀倉／貯蔵個体",
    "habitat_instability": "定足数移住／樹冠再建",
    "landmark_loss": "天空コンパス／フェロモン経路網",
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
    "lasius_sealed_foundation": "黒庭アリの密閉創設",
    "diacamma_gemma_inheritance": "トゲオオハリアリのジェンマ継承",
    "platythyrea_clone_watch": "無王アリのクローン監視",
    "ooceraea_synchronized_brood": "複製狩アリの同期繁殖",
    "mycocepurus_clonal_garden": "菌農アリの無性菌園",
    "cardiocondyla_dual_males": "放浪アリの二型雄",
    "vollenhovia_three_lineage": "ウメマツアリの三系統繁殖",
    "pristomyrmex_worker_queens": "アミメアリの単為生殖ワーカー",
    "formica_resin_pharmacy": "樹脂アリの抗菌巣材",
    "myrmica_funeral_workers": "欧州赤アリの葬送分業",
}

CARD_TEXTS = {
    "trail_pheromone": "化学の道標で、新しい採餌経路を今すぐ見つける。",
    "earthwork_nest": "維持された土中空間を探り、別の選択肢を今すぐ見つける。",
    "collective_foraging": "仲間を食料へ動員し、繁栄へつなげる。",
    "oecophylla_silkworks": "幼虫の絹と協同作業で、生きた葉の巣を織る。",
    "oecophylla_living_chain": "多数の体を一時的な橋へ変え、道を広げて新しい選択肢を得る。",
    "cephalotes_aerialis": "落下を操り、捕食者から離れる方向へ滑空する。",
    "cephalotes_living_gate": "盾形の頭を持つ兵隊が、狭い巣口そのものになる。守りながら繁栄を生む。",
    "odontomachus_tension_lock": "ばね仕掛けの顎を、攻撃にも緊急脱出にも使う。",
    "pheidole_supermajor_program": "大きな投資で、目立つ超大型防衛個体を生み出し、繁栄も守りも得る。",
    "pheidole_seed_miller": "大型兵の顎を、硬い種子の加工へ転用する。",
    "myrmecocystus_reserve": "手札を生体貯蔵へ変え、以後のラウンドに少しずつ繁栄を生む。",
    "megaponera_field_medicine": "抗菌分泌物で負傷個体を治療し、繁栄を守りながら損失を抑える。",
    "megaponera_rescue_column": "負傷した仲間を巣へ運び、働き手を将来へ残す。",
    "colobopsis_last_defense": "粘着性の分泌物を放つ自己犠牲で侵入者を止め、巣を守る。",
    "paraponera_poneratoxin": "強烈な毒が、攻撃と抑止の両方を担い、繁栄か防衛へ転じる。",
    "apterostigma_dentigerumycin": "共生微生物の抗菌物質が菌園寄生者を抑える。",
    "acromyrmex_antibiotic_garden": "成熟した菌園を、微生物と分泌物で専門的に守り、繁栄も支える。",
    "atta_fungus_garden": "葉を菌類の作物へ変え、安定した食料を得る。",
    "attine_infrabuccal_pocket": "感染物を隔離・除去する口器構造で菌園を衛生化する。",
    "cataglyphis_silver_hair": "三角形の銀毛が日射を反射し、体温上昇を抑える。",
    "cataglyphis_sky_compass": "偏光と経路積算で帰還し、繁栄を得ながら別の経路を見つける。",
    "pheidole_raid_wall": "大型兵とワーカーを巣口へ集め、繁栄を生みながら侵入隊を阻む。",
    "harpegnathos_gamergate": "ワーカーが繁殖個体へ移行できる柔軟なカーストを持つ。",
    "temnothorax_quorum_nest": "偵察個体の情報を集め、中央指揮なしで新居を決める。",
    "pogonomyrmex_granary": "手札を地下の種子庫へ伏せ、将来の繁栄と次ラウンドの保持余力を得る。",
    "paltothyreus_distress_signal": "閉じ込められた個体の化学信号が仲間の救助を呼ぶ。",
    "solenopsis_dry_store": "手札を乾燥保存へ変え、今の繁栄と将来の小さな収入を得る。",
    "solenopsis_raft_cycling": "筏の位置を交代しながら、長い洪水を耐え抜く。",
    "atta_leaf_cache": "葉片の仮置き場へ手札を伏せ、今の繁栄と次の収入を確保する。",
    "acromyrmex_spore_removal": "胞子と汚染部を物理的に取り除き、化学防御を補う。",
    "cataglyphis_heatshock_proteins": "分子シャペロンが、高温下の細胞機能を守る。",
    "megaponera_termite_raid": "危険な集団狩りで、大きな食料収入を狙う。",
    "temnothorax_emergency_emigration": "傷んだ巣を捨て、危険が迫る前に移住する。",
    "lasius_sealed_foundation": "女王が最初の巣室を閉じ、蓄えだけで初期ワーカーを育てる。",
    "diacamma_gemma_inheritance": "胸のジェンマを保ったワーカーが次の繁殖個体となり、次の保持余力も残す。",
    "platythyrea_clone_watch": "クローンのワーカーが、同じ繁殖系統の幼虫を守り続ける。",
    "ooceraea_synchronized_brood": "繁殖相と採餌相を同期し、次の採餌期に使える選択肢を見つける。",
    "mycocepurus_clonal_garden": "無性生殖のワーカーが菌園を安定して育て、資源生態の厚みを繁栄へ変える。",
    "cardiocondyla_dual_males": "巣に残る雄と飛び立つ雄を使い分け、繁栄か新しい選択肢へ転じる。",
    "vollenhovia_three_lineage": "異なる三つの系統を、ひとつの社会の中で維持する。",
    "pristomyrmex_worker_queens": "ワーカー自身が雌を産み、女王一個体への依存を減らして保持余力を残す。",
    "formica_resin_pharmacy": "樹脂を巣材に混ぜ、微生物の増殖を抑える。",
    "myrmica_funeral_workers": "死骸を見つけた個体が運び出し、腐敗の広がりを防ぐ。",
}


def card_name(card_id: str, fallback: str = "") -> str:
    return CARD_NAMES.get(card_id, fallback or card_id)


def event_name(event_id: str, fallback: str = "") -> str:
    return EVENT_NAMES.get(event_id, (fallback or event_id, ""))[0]


def optimization_name(disaster_id: str, fallback: str = "") -> str:
    return OPTIMIZATION_NAMES.get(disaster_id, fallback or disaster_id)


def tags_text(tags) -> list[str]:
    return [TAG_NAMES.get(tag, tag) for tag in sorted(tags)]


def requirement_text(requirements) -> str:
    if not requirements:
        return "条件なし"
    return "・".join(f"{TAG_NAMES.get(tag, tag)} {amount}" for tag, amount in sorted(requirements.items()))


def shield_text(shield: ShieldSpec) -> str:
    problem = PROBLEM_NAMES.get(shield.problem_id, shield.problem_id)
    return f"{problem}シールド +{shield.amount}"


def option_text(option: ActionOption) -> str:
    parts: list[str] = []
    if option.prosperity:
        parts.append(f"繁栄 +{option.prosperity}")
    parts.extend(shield_text(shield) for shield in option.shields)
    if option.draw_cards:
        parts.append(f"カードを今すぐ{option.draw_cards}枚引く")
    if option.retention_bonus:
        parts.append(f"次ラウンドの保持上限 +{option.retention_bonus}")
    for tag, coefficient in option.tag_prosperity:
        parts.append(f"盤面の{TAG_NAMES.get(tag, tag)}1つごとに繁栄 +{coefficient}")
    if getattr(option, "store_hand_card", False):
        income = getattr(option, "storage_income_per_card", 0)
        parts.append(f"手札1枚を伏せて貯蔵（次ラウンド以降、毎ラウンド繁栄 +{income}）")
    return "／".join(parts) or "数値効果なし"
