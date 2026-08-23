let gameId = null;
let state = null;
let retained = new Set();
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

async function api(path, data = null) {
  const options = data ? {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)} : {};
  const response = await fetch(path, options); const result = await response.json();
  if (!response.ok) throw new Error(result.error || "通信に失敗しました。");
  return result;
}
function notice(message, error = false) { const box = $("#notice"); box.textContent = message || ""; box.className = message ? (error ? "error" : "message") : ""; }
function tagHTML(tag, count = null) { const value = count ?? tag.count; return `<span class="tag" style="--tag-color:${esc(tag.color)}"><svg aria-hidden="true"><use href="#symbol-${esc(tag.symbol)}"></use></svg>${esc(tag.name)}${value != null && value > 1 ? ` ×${value}` : ""}</span>`; }
function requirementsHTML(items, progress = false) {
  if (!items || !items.length) return "<span>条件なし</span>";
  return items.map((item) => { const numbers = progress && item.actual != null ? `${item.actual}/${item.required}` : item.required; return `<span class="requirement ${item.missing > 0 ? "missing" : ""}">${tagHTML(item)} ×${numbers}${item.missing > 0 ? `（あと${item.missing}）` : ""}</span>`; }).join(" ");
}
function effectHTML(effect) {
  if (!effect) return ""; const parts = [];
  if (effect.prosperity) parts.push(`繁栄 +${effect.prosperity}`);
  if (effect.draw_cards) parts.push(`カードを${effect.draw_cards}枚ドロー`);
  if (effect.retention_bonus) parts.push(`次ラウンドの保持 +${effect.retention_bonus}`);
  if (effect.store_hand_card) parts.push(`手札1枚を貯蔵（次ラウンド以降、毎ラウンド繁栄 +${effect.storage_income_per_card}）`);
  (effect.tag_prosperity || []).forEach((bonus) => parts.push(`盤面の${esc(bonus.name || bonus.tag)}1つごとに繁栄 +${bonus.coefficient}（合計上限${effect.tag_prosperity_cap}）`));
  (effect.shields || []).forEach((shield) => parts.push(`${esc(shield.name)}シールド +${shield.amount}`));
  return parts.map((part) => `<span class="effect">${part}</span>`).join(" ") || "<span class='effect'>効果なし</span>";
}
function cardBand(tags) {
  if (!tags.length) return "#777"; const stop = 100 / tags.length;
  const colors = tags.flatMap((tag, index) => [`${tag.color} ${index * stop}%`, `${tag.color} ${(index + 1) * stop}%`]);
  return `linear-gradient(90deg,${colors.join(",")})`;
}
function cardHTML(card, selectable = false) {
  const biology = card.subject_taxon ? `<small class="biology">題材：${esc(card.subject_taxon)}</small>` : "";
  const fallback = card.fallback_options?.length ? `<div class="fallback"><span class="label">条件未達時の弱効果</span>${card.fallback_options.map(effectHTML).join("")}</div>` : "";
  return `<article class="card" style="--tag-band:${cardBand(card.tags)}" ${selectable ? `data-keep="${esc(card.id)}" tabindex="0" role="button"` : ""}><div class="meta">${esc(card.role)}</div><h3>${esc(card.name)}</h3><p>${esc(card.text)}</p>${biology}<div class="self-tags"><span class="label">カードのタグ</span><div class="tag-row">${card.tags.map((tag) => tagHTML(tag)).join("") || "なし"}</div></div><div class="required-tags condition"><span class="label">起動条件</span>${requirementsHTML(card.requirements)}</div><div class="effect-row">${card.options.map(effectHTML).join("") || "<span class='effect'>起動効果なし</span>"}</div>${fallback}</article>`;
}
function handCardHTML(card) {
  const actions = state.columns.map((column) => { const option = (card.placement_options || [])[column.index]; const status = option?.status || "other"; const title = status === "ready" ? "配置後すぐ強効果を起動できます" : status === "one-short" ? "配置後、強効果まであと1タグです" : "配置後も強効果の条件が不足します"; const stores = (column.activations || []).filter((activation) => activation.requires_storage_target && activation.enabled).map((activation) => `<button class="storage-placement" onclick="act('activate',{column:${column.index},option:${activation.option},target_card_id:'${esc(card.id)}'})">列${column.index + 1}に貯蔵して起動</button>`).join(""); return `<button class="play-placement placement-${status}" title="${title}" onclick="act('play',{card_id:'${esc(card.id)}',column:${column.index}})">列${column.index + 1}へ配置</button><button class="support-placement" onclick="act('support',{card_id:'${esc(card.id)}',column:${column.index}})">列${column.index + 1}の支援</button>${stores}`; }).join("");
  return cardHTML(card).replace("</article>", `<div class="hand-actions">${actions}</div></article>`);
}
function problemsHTML(problems) {
  return problems.map((problem) => { const raw = problem.raw_rolls?.length ? problem.raw_rolls.join(", ") : "?"; const rule = problem.raw_rolls?.length > 1 ? `出目 ${raw} → 高い方 ${problem.selected_roll}` : `出目 ${raw}`; const modifier = problem.modifier ? ` +${problem.modifier}` : ""; return `<article class="problem"><strong>${esc(problem.name)}</strong><span>${rule}${modifier} = <b>${problem.effective_roll ?? problem.roll ?? "?"}</b></span><span>シールド：${problem.defense ?? problem.shield ?? 0}</span><span>未防御：${problem.unblocked ?? "?"}</span>${problem.penalty != null ? `<span class="${problem.penalty ? "warning" : "success"}">問題ペナルティ：${problem.penalty}</span>` : ""}</article>`; }).join("");
}
function optimizationHTML(items, progress = false) {
  if (!items || !items.length) return `<div class="optimization"><strong>最適化なし</strong><p>この環境では独立問題が強化されています。</p></div>`;
  return `<div class="optimization"><strong>最適化（いずれか1つ）</strong>${items.map((item) => `<div class="optimization-option"><b>${esc(item.name)}</b><div>${requirementsHTML(item.requirements, progress)}</div>${item.met != null ? `<span class="${item.met ? "success" : "warning"}">${item.met ? "達成" : "未達"}</span>` : ""}</div>`).join("")}</div>`;
}
function problemRulesHTML(rules) {
  const entries = Object.entries(rules || {});
  if (!entries.length) return "";
  const names = {raid: "襲撃", sanitation: "衛生"};
  return `<p class="problem-rule">独立問題の強化：${entries.map(([id, rule]) => `${names[id] || id} ${rule.rolls > 1 ? `${rule.rolls}d4（高い方）` : "1d4"}${rule.bonus ? ` +${rule.bonus}` : ""}`).join(" ／ ")}</p>`;
}
function resultHTML(result) {
  if (!result) return "";
  const opts = result.optimizations?.length ? result.optimizations.map((item) => ({...item, requirements: item.requirements || []})) : [];
  const gain = result.gain_breakdown || {};
  return `<div class="result"><strong>ラウンド ${result.round}「${esc(result.environment_name)}」の結果</strong><div class="result-steps"><div>開始 ${result.score_before} → 繁栄後 ${result.score_after_prosperity}（問題後プール ${gain.pool_after_problems ?? result.prosperity_base} × サイズ ${result.size_multiplier}）</div><div class="gain-breakdown">繁栄内訳：開始分 ${gain.base ?? "－"}／カード起動 ${(gain.activation ?? 0) + (gain.card ?? 0)}／貯蔵 ${gain.storage ?? "－"}／タグ ${gain.tag ?? "－"}<br>倍率前プール：${gain.pool_before_problems ?? result.prosperity_base} − 問題 ${gain.problem_penalty ?? result.problem_penalty} ＝ ${gain.pool_after_problems ?? "－"} → 実得点 +${gain.delta ?? result.prosperity_delta}</div><div class="problem-grid">${problemsHTML(result.problems)}</div><div class="${result.optimization_met ? "success" : "warning"}">${opts.length ? `最適化：${result.optimization_met ? "いずれか達成" : `全て未達・${result.optimization_half_loss}点減`}` : "最適化なし"}</div><div><strong>精算後の繁栄：${result.total_prosperity}</strong></div></div></div>`;
}
function renderForecast() { $("#forecast").innerHTML = `<h2>公開された5ラウンドの環境変化予報</h2><div class="forecast-grid">${state.forecast.map((environment) => `<article class="forecast-card ${environment.current ? "current" : ""} ${environment.completed ? "completed" : ""}"><div class="meta">ラウンド ${environment.round}${environment.current ? "・現在" : ""}</div><h3>${esc(environment.name)}</h3><p>${esc(environment.text)}</p>${optimizationHTML(environment.optimizations)}${problemRulesHTML(environment.problem_roll_rules)}</article>`).join("")}</div>`; }
function renderOverview() { const environment = state.environment; $("#overview").innerHTML = `${resultHTML(state.last_result)}<h2>ラウンド ${state.round}/5・${esc(environment.name)}</h2><p>${esc(environment.text)}</p><div class="stats"><div class="stat">繁栄<strong>${state.prosperity}</strong></div><div class="stat">サイズ<strong>${esc(state.size_name)}</strong></div><div class="stat">今ラウンドの繁栄<strong>${state.round_prosperity_base}</strong></div><div class="stat">サイズ倍率<strong>×${state.round_prosperity_multiplier}</strong></div><div class="stat">今ラウンド獲得予定<strong>+${state.round_prosperity_delta}</strong></div><div class="stat">手札<strong>${state.hand.length}/${state.hand_limit}</strong></div><div class="stat">次ラウンド保持<strong>+${state.pending_retention_bonus || 0}</strong></div></div><h3>毎ラウンド独立の2問題（各1d4）</h3><div class="problem-grid">${problemsHTML(state.problems)}</div>${optimizationHTML(state.optimizations, true)}${problemRulesHTML(environment.problem_roll_rules)}`; }
function bindCandidateSelection() { document.querySelectorAll("[data-keep]").forEach((element) => { element.addEventListener("click", () => toggleKeep(element.dataset.keep)); element.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); toggleKeep(element.dataset.keep); } }); }); $("#keep-button").addEventListener("click", () => act("retain", {card_ids: [...retained]})); }
function renderDecision() {
  const box = $("#decision"); if (state.finished) { box.innerHTML = `<h2>5ラウンド終了</h2><p>最終繁栄 <strong>${state.prosperity}</strong></p>`; return; }
  if (state.phase === "size") { box.innerHTML = `<h2>1. サイズを選ぶ</h2><p class="phase-help">大きいほど繁栄は増えますが、保持できるカードは減ります。</p><div class="button-row">${state.legal_sizes.map((size) => `<button onclick="act('size',{size:'${size.id}'})"><strong>${esc(size.name)}</strong><br>繁栄 ×${size.multiplier}・保持 ${size.retention}枚</button>`).join("")}</div>`; return; }
  if (state.phase === "retain") { const hand = state.hand.length ? `<div class="cards">${state.hand.map((card) => cardHTML(card)).join("")}</div>` : "<p>手札はありません。</p>"; box.innerHTML = `<h2>2. 公開カードを保持 <span id="keep-count">0/${state.retention_limit}</span></h2><p class="phase-help">カードを選び、保持上限まで手札に加えます。</p><h3>今回の候補</h3><div class="cards">${state.candidates.map((card) => cardHTML(card, true)).join("")}</div><h3 class="hand-heading">現在の手札</h3>${hand}<div class="button-row"><button class="primary" id="keep-button">保持して進む</button></div>`; bindCandidateSelection(); return; }
  box.innerHTML = `<h2>3. 配置・起動</h2><p class="phase-help">緑は配置後すぐ強効果を起動可能、黄は強効果まであと1タグです。満杯列は押し出し後の状態で判定します。</p><h3>手札</h3>${state.hand.length ? `<div class="cards">${state.hand.map(handCardHTML).join("")}</div>` : "<p>手札はありません。</p>"}<div class="button-row"><button class="primary danger" onclick="act('resolve')">このラウンドを解決</button></div>`;
}
function toggleKeep(id) { if (retained.has(id)) retained.delete(id); else if (retained.size < state.retention_limit) retained.add(id); else { notice(`保持できるのは${state.retention_limit}枚までです。`, true); return; } document.querySelectorAll("[data-keep]").forEach((element) => element.classList.toggle("selected", retained.has(element.dataset.keep))); $("#keep-count").textContent = `${retained.size}/${state.retention_limit}`; }
function columnHTML(column) { const cards = column.cards.map((card) => `<div class="stack-card ${card.top ? "top" : ""} ${card.support ? "support" : ""}"><strong>${esc(card.name)}</strong><br><small>${card.top ? "最上段" : card.support ? "支援" : "下段"}${card.activated ? "・起動済み" : ""}${card.stored_count ? `・伏せ貯蔵 ${card.stored_count}枚（次回以降、毎ラウンド繁栄 +${card.storage_income_next_round}）` : ""}</small><div class="tag-row">${card.tags.map((tag) => tagHTML(tag)).join("")}</div></div>`).join(""); const activations = column.activations.map((activation) => { const click = activation.requires_storage_target ? "" : `onclick="act('activate',{column:${column.index},option:${activation.option}})"`; return `<div><button ${activation.enabled && !activation.requires_storage_target ? "" : "disabled"} ${click} title="${esc(activation.reason)}">${activation.tier === "fallback" ? "弱効果：" : activation.requires_storage_target ? "手札から貯蔵：" : "起動："}${effectHTML(activation.effect)}</button>${activation.requirements.length ? `<div class="condition">条件：${requirementsHTML(activation.requirements, true)}</div>` : ""}${activation.requires_storage_target ? "<small>手札のカードから「貯蔵して起動」を選択</small>" : ""}</div>`; }).join(""); return `<article class="column"><h3>${esc(column.name)} <small>${column.cards.length}/${column.capacity}</small></h3><span class="label">列の全タグ（最適化）</span><div class="tag-row">${column.tags.map((tag) => tagHTML(tag)).join("") || "なし"}</div><span class="label">起動に使うタグ</span><div class="tag-row">${column.activation_tags.map((tag) => tagHTML(tag)).join("") || "なし"}</div><div class="stack">${cards || "空"}</div>${column.next_pushed ? `<p class="warning">次に押し出されるカード：${esc(column.next_pushed)}</p>` : ""}<div class="button-row">${activations}</div></article>`; }
function gainBreakdownHTML(gain, problems) { if (!gain) return ""; const shields = (problems || []).map((problem) => `${esc(problem.name)} ${problem.shield || 0}`).join("／"); return `<div class="gain-breakdown"><strong>今ラウンドの繁栄・シールド</strong><span>開始分 ${gain.base} ＋ カード起動 ${gain.activation + gain.card} ＋ 貯蔵 ${gain.storage} ＋ タグ ${gain.tag} ＝ 倍率前 ${gain.pool_before_problems}</span><span>現在のシールド：${shields || "なし"}</span><span>問題 ${gain.problem_penalty} を差し引き → ${gain.pool_after_problems} × サイズ倍率 ${gain.multiplier} ＝ 実得点 +${gain.delta}</span></div>`; }
function renderBoard() { $("#board").innerHTML = `<h2>進化列</h2><p class="phase-help">列のタグは最適化、最上段を除くタグは起動条件に使います。</p>${gainBreakdownHTML(state.round_gain_breakdown, state.problems)}<div class="columns">${state.columns.map(columnHTML).join("")}</div>`; }
function render() { renderForecast(); renderOverview(); renderDecision(); renderBoard(); const undo = $("#undo"); undo.classList.remove("hidden"); undo.disabled = !state.can_undo; }
async function act(kind, extra = {}) { try { const result = await api("/api/action", {game_id: gameId, kind, ...extra}); state = result.state; retained.clear(); notice(kind === "undo" ? "一手戻しました。" : ""); render(); } catch (error) { notice(error.message, true); } }
$("#start").addEventListener("click", async () => { try { const result = await api("/api/new", {seed: Number($("#seed").value || 0)}); gameId = result.game_id; state = result.state; retained.clear(); $("#setup").classList.add("hidden"); $("#game").classList.remove("hidden"); $("#restart").classList.remove("hidden"); notice("ゲームを開始しました。まずサイズを選んでください。"); render(); } catch (error) { notice(error.message, true); } });
$("#undo").addEventListener("click", () => act("undo"));
$("#restart").addEventListener("click", () => { gameId = null; state = null; retained.clear(); $("#game").classList.add("hidden"); $("#setup").classList.remove("hidden"); $("#restart").classList.add("hidden"); $("#undo").classList.add("hidden"); });
