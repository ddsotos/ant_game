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
    "army_ant_march": ("軍隊アリの行軍", "軍隊アリの大群が生息地を横切り、成熟したコロニーへ迫る。"),
    "fungus_garden_collapse": ("菌園崩壊", "病原体の波が菌園へ広がり、栽培環境を一斉に揺るがす。"),
    "extreme_heat_peak": ("極端熱波", "最後の熱波が露出した体と細胞の働きを同時に追い詰める。"),
    "great_flood": ("大洪水", "広い土地が水没し、地上の経路と低い巣がすべて失われる。"),
}

OPTIMIZATION_NAMES = {
    "flood": "ヒアリの生体いかだ／カメアリの樹冠退避",
    "desert_heat_wave": "サハラギンアリの銀毛放熱／サハラギンアリの熱ショック応答",
    "prolonged_drought": "収穫アリの地下穀倉／ミツツボアリの貯蔵個体",
    "habitat_instability": "ムネボソアリの定足数移住／ツムギアリの樹冠再建",
    "landmark_loss": "砂漠アリの天空コンパス／アリのフェロモン経路網",
    "army_ant_march": "オオズアリの社会的迎撃／アリの深巣退避",
    "fungus_garden_collapse": "ヒメハキリアリの抗菌腺防衛／ハキリアリの資源転換",
    "extreme_heat_peak": "サハラギンアリの反射体表／サハラギンアリの熱ショック保護",
    "great_flood": "ヒアリの生体いかだ／ツムギアリの樹冠の巣",
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
    "myrmecia_antimicrobial_gland": "ウシアリの抗菌腺",
    "crematogaster_sticky_gland": "シリアゲアリの粘着腺",
    "oecophylla_venom_spray": "ツムギアリの毒液噴霧",
    "formica_acid_resin": "樹脂アリの酸性樹脂",
    "polyrhachis_polarized_eye": "ウミトゲアリの偏光眼",
    "odontomachus_night_vision": "アギトアリの夜間視",
    "pseudomyrmex_slender_legs": "アカシアリの細脚",
    "myrmecia_visual_hunt": "ウシアリの視覚狩り",
    "lasius_trophallaxis": "黒庭アリの口移し",
    "azteca_domatia": "アズテカの空洞巣",
    "formica_self_medication": "クロアリの自己投薬",
    "atta_acid_pharmacy": "ケファロテスハキリアリの抗菌酸",
    "camponotus_saliva_care": "オオアリの唾液治療",
    "acromyrmex_phenylacetic_acid": "ハキリアリのフェニル酢酸",
    "atta_hard_mandible": "ハキリアリの硬質顎",
    "pheidole_bite_muscle": "オオズアリの咬合筋",
    "melophorus_ocelli": "砂走アリの単眼航法",
    "temnothorax_worker_size": "ムネボソアリの体格分業",
    "pogonomyrmex_seed_sorting": "収穫アリの種子選別",
    "camponotus_amputation": "オオアリの断脚治療",
    "melissotarsus_living_wood_galleries": "メリソタルスの生木坑道",
    "allomerus_fungal_trap_gallery": "アロメルスの菌糸トラップ回廊",
    "formica_thatch_thermostat": "ヤマアリの茅葺き温室巣",
    "atta_large_colony_worker_polymorphism": "ハキリアリの巨大コロニー分業",
}

CARD_TEXTS = {
    "trail_pheromone": "地面へフェロモンを残し、仲間を採餌経路へ導く。",
    "earthwork_nest": "働きアリが土を掘り、温度と湿度の安定した室を維持する。",
    "collective_foraging": "仲間を食料源へ動員し、見つけた資源を巣へ運ぶ。",
    "oecophylla_silkworks": "幼虫の絹と協同作業で、生きた葉の巣を織る。",
    "oecophylla_living_chain": "多数の働きアリが体をつなぎ、葉を引き寄せる鎖を作る。",
    "cephalotes_aerialis": "落下を操り、捕食者から離れる方向へ滑空する。",
    "cephalotes_living_gate": "盾形の頭を持つ兵隊が、狭い巣口をふさぐ生きた門になる。",
    "odontomachus_tension_lock": "ばね仕掛けの顎を、攻撃にも緊急脱出にも使う。",
    "pheidole_supermajor_program": "特大の頭部を持つ兵隊が生まれ、巣口で侵入者を押し返す。",
    "pheidole_seed_miller": "大型兵の顎を、硬い種子の加工へ転用する。",
    "myrmecocystus_reserve": "膨らんだ腹部を持つ働きアリが、液体食料を体内に長期間蓄える。",
    "megaponera_field_medicine": "働きアリが抗菌分泌物を負傷個体の傷へ塗り、感染を抑える。",
    "megaponera_rescue_column": "負傷した仲間を巣へ運び、働き手を将来へ残す。",
    "colobopsis_last_defense": "粘着性の分泌物を放つ自己犠牲で侵入者を止め、巣を守る。",
    "paraponera_poneratoxin": "毒液中の成分がナトリウムチャネルへ作用し、長く続く激痛を生む。",
    "apterostigma_dentigerumycin": "共生微生物の抗菌物質が菌園寄生者を抑える。",
    "acromyrmex_antibiotic_garden": "共生細菌と腺分泌物が、菌園へ侵入する病原菌の増殖を抑える。",
    "atta_fungus_garden": "切り取った葉を菌類へ与え、菌の栄養体を食料として利用する。",
    "attine_infrabuccal_pocket": "感染物を隔離・除去する口器構造で菌園を衛生化する。",
    "cataglyphis_silver_hair": "三角形の銀毛が日射を反射し、体温上昇を抑える。",
    "cataglyphis_sky_compass": "偏光した空と歩数の積算を手がかりに、目印のない砂漠から帰還する。",
    "pheidole_raid_wall": "大型兵と働きアリが巣口に集まり、侵入する軍隊アリを段階的に迎え撃つ。",
    "harpegnathos_gamergate": "ワーカーが繁殖個体へ移行できる柔軟なカーストを持つ。",
    "temnothorax_quorum_nest": "偵察個体の情報を集め、中央指揮なしで新居を決める。",
    "pogonomyrmex_granary": "地中の乾いた室へ種子を運び、湿度を調整しながら貯蔵する。発芽した種子も加工し、硬い種子を利用する。",
    "paltothyreus_distress_signal": "閉じ込められた個体の化学信号が仲間の救助を呼ぶ。",
    "solenopsis_dry_store": "ヒアリは獲物の断片を乾かし、巣内へ運んで後で利用する。",
    "solenopsis_raft_cycling": "筏の位置を交代しながら、長い洪水を耐え抜く。",
    "atta_leaf_cache": "運搬した葉片を巣口の外へ一時的に集め、入口が塞がっても菌園への供給を続ける。",
    "acromyrmex_spore_removal": "胞子と汚染部を物理的に取り除き、化学防御を補う。",
    "cataglyphis_heatshock_proteins": "分子シャペロンが、高温下の細胞機能を守る。",
    "megaponera_termite_raid": "分業した隊列が防御性の高いシロアリを襲い、獲物を巣へ運ぶ。",
    "temnothorax_emergency_emigration": "傷んだ巣を捨て、危険が迫る前に移住する。",
    "lasius_sealed_foundation": "女王が最初の巣室を閉じ、蓄えだけで初期ワーカーを育てる。",
    "diacamma_gemma_inheritance": "胸部のジェンマを残したワーカーが、繁殖個体へ成長する。",
    "platythyrea_clone_watch": "クローンのワーカーが、同じ繁殖系統の幼虫を守り続ける。",
    "ooceraea_synchronized_brood": "繁殖相と幼虫養育・採餌相が、コロニー全体で同期して切り替わる。",
    "mycocepurus_clonal_garden": "無性生殖する女王の子である働きアリが、菌園を継続して育てる。",
    "cardiocondyla_dual_males": "巣に残って争う無翅雄と、飛び立つ有翅雄を同じコロニーで作る。",
    "vollenhovia_three_lineage": "異なる三つの系統を、ひとつの社会の中で維持する。",
    "pristomyrmex_worker_queens": "女王のいない巣で、単型の雌が単為生殖により次の雌を産む。",
    "formica_resin_pharmacy": "樹脂を巣材に混ぜ、微生物の増殖を抑える。",
    "myrmica_funeral_workers": "死骸を見つけた個体が運び出し、腐敗の広がりを防ぐ。",
    "myrmecia_antimicrobial_gland": "腺から出る抗菌分泌物を巣材や幼虫の周囲へ塗り、微生物の増殖を抑える。",
    "crematogaster_sticky_gland": "粘着性の腺分泌物を攻撃者へ付着させ、動きを妨げる。",
    "oecophylla_venom_spray": "噛みついた相手へ毒液を吹きかけ、巣へ近づけない。",
    "formica_acid_resin": "針葉樹の樹脂を巣へ運び、働きアリの防御性分泌物と組み合わせる。",
    "polyrhachis_polarized_eye": "空の偏光と視覚情報を使い、樹冠の枝を移動する。",
    "odontomachus_night_vision": "発達した複眼で、薄暗い林床でも獲物と障害物を見分ける。",
    "pseudomyrmex_slender_legs": "細長い脚で細い植物の茎をすばやく走る。",
    "myrmecia_visual_hunt": "大きな眼で獲物と目印を追い、視覚的な追跡狩りを行う。",
    "lasius_trophallaxis": "働きアリ同士が口移しで液体食料を分配する。",
    "azteca_domatia": "植物が作る中空の膨らんだ葉柄を巣室として利用し、宿主植物と共生する。",
    "formica_self_medication": "病原性の菌にさらされた働きアリが、抗菌性の物質を自ら摂取する。",
    "atta_acid_pharmacy": "腺分泌物と菌園由来の抗菌物質を使い分け、病原菌の増殖を抑える。",
    "camponotus_saliva_care": "働きアリが抗菌性のある口腔分泌物を仲間の傷へ塗る。",
    "acromyrmex_phenylacetic_acid": "後胸腺からフェニル酢酸を分泌し、菌園の病原菌へ作用させる。",
    "atta_hard_mandible": "分化した大顎で葉を切り、菌園へ運べる大きさに加工する。",
    "pheidole_bite_muscle": "兵隊の大きな頭部と咬筋が、強い噛みつきの力を生む。",
    "melophorus_ocelli": "発達した単眼で偏光した空を読み、開けた地面を進む。",
    "temnothorax_worker_size": "体格の異なる働きアリが、採餌や育児など異なる仕事を分担する。",
    "pogonomyrmex_seed_sorting": "集めた種子を大きさや硬さで選り分け、発芽した種子も加工する。",
    "camponotus_amputation": "重い傷を負った脚を仲間が処置し、感染が広がる前に切断することがある。",
    "melissotarsus_living_wood_galleries": "生きた樹木の樹皮下へ坑道を掘り、外界から隔てられた生活空間を作る。",
    "allomerus_fungal_trap_gallery": "菌糸で補強した回廊の穴から獲物を待ち伏せし、集団で拘束する。",
    "formica_thatch_thermostat": "巣を覆う茅が昼の過熱と夜の放熱を抑え、内部温度を安定させる。",
    "atta_large_colony_worker_polymorphism": "体格の異なる働きアリが、大規模な巣で採餌・加工・育児を分担する。",
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
    for vulnerability in option.vulnerabilities:
        problem = PROBLEM_NAMES.get(vulnerability.problem_id, vulnerability.problem_id)
        parts.append(f"{problem}脆弱性 +{vulnerability.amount}")
    if option.draw_cards:
        parts.append(f"カードを今すぐ{option.draw_cards}枚引く")
    if option.retention_bonus:
        parts.append(f"次ラウンドの保持上限 +{option.retention_bonus}")
    if option.next_candidate_bonus:
        parts.append(f"次ラウンドの公開候補 +{option.next_candidate_bonus}枚")
    if option.candidate_bonus_when_reduce_retention_for_more_candidates:
        parts.append(
            "次ラウンドに保持上限を減らして候補を増やす時、公開候補 +"
            f"{option.candidate_bonus_when_reduce_retention_for_more_candidates}枚"
        )
    if option.environment_prosperity_loss_reduction:
        parts.append(f"環境による繁栄損失を{option.environment_prosperity_loss_reduction}軽減")
    for effect in option.size_effects:
        details: list[str] = []
        if effect.prosperity:
            details.append(f"繁栄 +{effect.prosperity}")
        details.extend(shield_text(shield) for shield in effect.shields)
        if effect.environment_prosperity_loss_reduction:
            details.append(f"環境による繁栄損失を{effect.environment_prosperity_loss_reduction}軽減")
        for vulnerability in effect.vulnerabilities:
            problem = PROBLEM_NAMES.get(vulnerability.problem_id, vulnerability.problem_id)
            details.append(f"{problem}脆弱性 +{vulnerability.amount}")
        parts.append(f"{SIZE_LABELS.get(effect.size.name, effect.size.name)}なら" + "・".join(details))
    if option.recover_lower_card:
        parts.append("同じ列の下段カード1枚を手札へ戻す")
    for tag, coefficient in option.tag_prosperity:
        detail = f"盤面の{TAG_NAMES.get(tag, tag)}1つごとに繁栄 +{coefficient}"
        if option.tag_prosperity_divisor > 1:
            detail += f"、合計を{option.tag_prosperity_divisor}で割って切り捨て"
        detail += f"、上限{option.tag_prosperity_cap}" if option.tag_prosperity_cap is not None else "（上限なし）"
        parts.append(detail)
    if getattr(option, "store_hand_card", False):
        income = getattr(option, "storage_income_per_card", 0)
        parts.append(f"手札1枚を伏せて貯蔵（次ラウンド以降、毎ラウンド繁栄 +{income}）")
    return "／".join(parts) or "数値効果なし"
