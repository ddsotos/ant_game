let gameId = null;
let state = null;
let retained = new Set();

const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

async function api(path, data = null) {
  const options = data ? {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)} : {};
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "通信に失敗しました。");
  return result;
}

function notice(message, error = false) {
  const box = $("#notice");
  box.textContent = message || "";
  box.className = message ? (error ? "error" : "message") : "";
}

async function boot() {
  const config = await api("/api/config");
  const select = $("#environment");
  for (const event of config.environments) {
    const option = document.createElement("option");
    option.value = event.id;
    option.textContent = `${event.name}（${event.forecast.join(" → ")}ダメージ）`;
    select.appendChild(option);
  }
}

$("#start").addEventListener("click", async () => {
  try {
    const result = await api("/api/new", {
      seed: Number($("#seed").value || 0),
      environment_id: $("#environment").value || null,
    });
    gameId = result.game_id;
    state = result.state;
    $("#setup").classList.add("hidden");
    $("#game").classList.remove("hidden");
    $("#restart").classList.remove("hidden");
    notice("ゲームを開始しました。まず今ラウンドのサイズを選んでください。");
    render();
  } catch (error) { notice(error.message, true); }
});

$("#restart").addEventListener("click", () => {
  gameId = null; state = null; retained.clear();
  $("#game").classList.add("hidden");
  $("#setup").classList.remove("hidden");
  $("#restart").classList.add("hidden");
});

async function act(kind, extra = {}) {
  try {
    const result = await api("/api/action", {game_id: gameId, kind, ...extra});
    state = result.state;
    retained.clear();
    notice(messageFor(kind));
    render();
  } catch (error) { notice(error.message, true); }
}

function messageFor(kind) {
  return ({size:"サイズを決めました。残すカードを選んでください。", retain:"カードを保持しました。配置と起動を行えます。", play:"列の先頭に配置しました。", support:"支援として下層に配置しました。", activate:"カードを起動しました。", resolve:"環境を解決しました。"})[kind] || "操作しました。";
}

function render() {
  renderOverview();
  renderDecision();
  renderBoard();
  renderExtremes();
}

function renderOverview() {
  const e = state.environment;
  const result = state.last_result && `<div class="result"><strong>直前の結果:</strong> R${state.last_result.round}　基礎ダメージ ${state.last_result.raw_damage} − シールド ${state.last_result.shield} = <strong>${state.last_result.damage}</strong> ／ 繁栄 +${state.last_result.prosperity}</div>`;
  $("#overview").innerHTML = `
    ${result || ""}<h2>${esc(e.name)} — ラウンド ${state.round}/5・Stage ${state.stage}</h2>
    <p>${esc(e.text)}</p>
    <div class="stats">
      <div class="stat">繁栄<strong>${state.prosperity}</strong></div>
      <div class="stat">累積ダメージ<strong>${state.damage} / ${state.damage_limit}</strong></div>
      <div class="stat">現在サイズ<strong>${state.size_name}</strong></div>
      <div class="stat">今Rの繁栄<strong>${state.round_prosperity}</strong></div>
      <div class="stat">今Rのシールド<strong>${state.round_shield}</strong></div>
      <div class="stat">手札<strong>${state.hand.length} / ${state.hand_limit}</strong></div>
    </div>
    <div class="forecast">${e.forecast.map(f => `<span class="${f.round === state.round ? "current" : ""}">R${f.round}・${f.stage}: ${f.damage}ダメージ</span>`).join("")}</div>`;
}

function renderDecision() {
  const box = $("#decision");
  if (state.finished) {
    box.innerHTML = `<h2>${state.extinct ? "種は絶滅しました" : "5ラウンド終了"}</h2><p class="${state.extinct ? "warning" : ""}">最終繁栄: <strong>${state.prosperity}</strong>　累積ダメージ: <strong>${state.damage}</strong></p><button class="primary" onclick="document.querySelector('#restart').click()">もう一度遊ぶ</button>`;
    return;
  }
  if (state.phase === "size") {
    box.innerHTML = `<h2>1. サイズを選ぶ</h2><p class="phase-help">大きいほど起動した繁栄が増えますが、カードを残せる枚数が減ります。毎ラウンド1段階だけ変更できます。</p><div class="button-row">${state.legal_sizes.map(s => `<button onclick="act('size',{size:'${s.id}'})"><strong>${s.name}</strong><br>繁栄×${s.multiplier}・保持${s.retention}枚</button>`).join("")}</div>`;
  } else if (state.phase === "retain") {
    const cards = [...state.candidates, ...state.extremes.filter(x => x.eligible)];
    box.innerHTML = `<h2>2. カードを保持する <span id="keep-count">0 / ${state.retention_limit}</span></h2><p class="phase-help">欲しいカードを選びます。切り札も同じ保持枠を使います。0枚でも進めます。</p><div class="cards">${cards.map(c => cardHTML(c, true)).join("")}</div><div class="button-row" style="margin-top:12px"><button class="primary" id="keep-button">選んだカードを保持して進む</button></div>`;
    document.querySelectorAll("[data-keep]").forEach(el => el.addEventListener("click", () => toggleKeep(el.dataset.keep)));
    $("#keep-button").addEventListener("click", () => act("retain", {card_ids: [...retained]}));
  } else {
    box.innerHTML = `<h2>3. 配置・支援・起動</h2><p class="phase-help">先頭カードだけが起動できます。先頭を起動してから別カードで覆い、新しい先頭も起動できます。準備が終わったら環境を解決してください。</p><h3>手札</h3>${state.hand.length ? `<div class="cards">${state.hand.map(c => handCardHTML(c)).join("")}</div>` : "<p>手札はありません。</p>"}<div class="button-row" style="margin-top:14px"><button class="primary danger" onclick="act('resolve')">このラウンドの環境を解決する</button></div>`;
  }
}

function toggleKeep(id) {
  if (retained.has(id)) retained.delete(id);
  else if (retained.size < state.retention_limit) retained.add(id);
  else { notice(`保持できるのは${state.retention_limit}枚までです。`, true); return; }
  document.querySelectorAll("[data-keep]").forEach(el => el.classList.toggle("selected", retained.has(el.dataset.keep)));
  $("#keep-count").textContent = `${retained.size} / ${state.retention_limit}`;
}

function cardHTML(card, selectable = false) {
  return `<article class="card" ${selectable ? `data-keep="${esc(card.id)}"` : ""}>
    <div class="meta">${esc(card.role)}</div>
    <h3>${esc(card.name)}</h3><p>${esc(card.text)}</p>
    <div class="tags">${card.tags.map(t => `<span class="tag">${esc(t)}</span>`).join("")}</div>
    <div class="condition">起動条件: ${esc(card.requirements)}</div>
    <div class="effects">${card.options.map(o => `<span class="effect">${esc(o)}</span>`).join("") || "<span class='effect'>起動効果なし</span>"}</div>
  </article>`;
}

function handCardHTML(card) {
  const actions = state.columns.map(col => `<button onclick="act('play',{card_id:'${card.id}',column:${col.index}})">先頭→列${col.index + 1}</button><button onclick="act('support',{card_id:'${card.id}',column:${col.index}})">支援→列${col.index + 1}</button>`).join("");
  return `<article class="card"><div class="meta">${esc(card.role)}</div><h3>${esc(card.name)}</h3><p>${esc(card.text)}</p><div class="tags">${card.tags.map(t => `<span class="tag">${esc(t)}</span>`).join("")}</div><div class="condition">起動条件: ${esc(card.requirements)}</div><div class="effects">${card.options.map(o => `<span class="effect">${esc(o)}</span>`).join("")}</div><div class="hand-actions">${actions}</div></article>`;
}

function renderBoard() {
  const box = $("#board");
  box.innerHTML = `<h2>進化列</h2><div class="columns">${state.columns.map(columnHTML).join("")}</div>`;
}

function columnHTML(col) {
  const cards = col.cards.map(c => `<div class="stack-card ${c.top ? "top" : ""} ${c.support ? "support" : ""}"><strong>${esc(c.name)}</strong><br><small>${c.top ? "先頭" : c.support ? "支援（タグのみ）" : "下層（タグのみ）"}${c.activated ? "・起動済み" : ""}</small></div>`).join("");
  const acts = col.activations.map(a => `<button ${a.enabled ? "" : "disabled"} title="${esc(a.reason)}" onclick="act('activate',{column:${col.index},option:${a.option}})">起動: ${esc(a.text)}</button>`).join("");
  return `<article class="column"><h3>${col.name} <small>${col.cards.length}/${col.capacity}</small></h3><div class="tags">${col.tags.map(t => `<span class="tag">${esc(t.name)} ${t.count}</span>`).join("")}</div><div class="stack">${cards || "<span>空</span>"}</div>${col.next_pushed ? `<p class="warning">次に押し出す: ${esc(col.next_pushed)}</p>` : ""}<div class="button-row">${acts}</div></article>`;
}

function renderExtremes() {
  $("#extreme-list").innerHTML = state.extremes.length ? `<div class="cards">${state.extremes.map(c => `<div>${cardHTML(c)}<p class="${c.eligible ? "" : "warning"}">${c.eligible ? "現在取得可能" : "条件未達"}</p></div>`).join("")}</div>` : "<p>取得可能な切り札はありません。</p>";
}

boot().catch(error => notice(error.message, true));
