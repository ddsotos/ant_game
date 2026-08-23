const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[character]));
let catalog = {cards: [], tags: [], roles: []};

function tagHTML(tag, amount = tag.count) {
  return `<span class="tag" style="--tag-color:${esc(tag.color)}"><svg aria-hidden="true"><use href="#symbol-${esc(tag.symbol)}"></use></svg>${esc(tag.name)}${amount > 1 ? ` ×${amount}` : ""}</span>`;
}

function requirementsHTML(requirements) {
  if (!requirements.length) return "<span>条件なし</span>";
  return requirements.map((requirement) => `<span class="requirement">${tagHTML(requirement)} ×${requirement.required}</span>`).join(" ");
}

function effectText(effect) {
  const parts = [];
  if (effect.prosperity) parts.push(`繁栄 +${effect.prosperity}`);
  if (effect.draw_cards) parts.push(`カードを${effect.draw_cards}枚ドロー`);
  if (effect.retention_bonus) parts.push(`次ラウンドの保持 +${effect.retention_bonus}`);
  if (effect.next_candidate_bonus) parts.push(`次ラウンドの公開 +${effect.next_candidate_bonus}枚`);
  if (effect.recover_lower_card) parts.push("同じ列の下段カードを1枚回収");
  if (effect.store_hand_card) parts.push(`手札1枚を貯蔵（次ラウンド以降、毎ラウンド繁栄 +${effect.storage_income_per_card}）`);
  (effect.tag_prosperity || []).forEach((bonus) => {
    const divisor = effect.tag_prosperity_divisor > 1 ? `。合計を${effect.tag_prosperity_divisor}で割って切り捨て` : "";
    const cap = effect.tag_prosperity_cap == null ? "（上限なし）" : `（上限${effect.tag_prosperity_cap}）`;
    parts.push(`盤面の${bonus.name || bonus.tag}1つごとに繁栄 +${bonus.coefficient}${divisor}${cap}`);
  });
  (effect.shields || []).forEach((shield) => parts.push(`${shield.name}シールド +${shield.amount}`));
  return parts.join("／") || "効果なし";
}

function optionHTML(option, index, weak = false) {
  const label = weak ? `弱効果 ${index + 1}` : `起動効果 ${index + 1}`;
  return `<div class="option"><span class="label">${label}</span><span class="effect">${esc(effectText(option))}</span></div>`;
}

function cardBand(tags) {
  if (!tags.length) return "#777";
  const stop = 100 / tags.length;
  const colors = tags.flatMap((tag, index) => [`${tag.color} ${index * stop}%`, `${tag.color} ${(index + 1) * stop}%`]);
  return `linear-gradient(90deg,${colors.join(",")})`;
}

function cardHTML(card) {
  const strong = card.options.map((option, index) => optionHTML(option, index)).join("");
  const weak = card.fallback_options.length
    ? `<div class="fallback">${card.fallback_options.map((option, index) => optionHTML(option, index, true)).join("")}</div>`
    : "";
  const source = card.biology_source
    ? `<a class="source" href="${esc(card.biology_source)}" target="_blank" rel="noopener noreferrer">生物学的な出典を開く</a>`
    : "";
  return `<article class="card catalog-card" style="--tag-band:${cardBand(card.tags)}">
    <div class="meta">${esc(card.role)}</div>
    <h3>${esc(card.name)}</h3>
    <p>${esc(card.text)}</p>
    ${card.subject_taxon ? `<small class="biology">題材：${esc(card.subject_taxon)}</small>` : ""}
    <div class="self-tags"><span class="label">カードのタグ</span><div class="tag-row">${card.tags.map((tag) => tagHTML(tag)).join("") || "なし"}</div></div>
    <div class="required-tags condition"><span class="label">起動条件（自身のタグは数えない）</span>${requirementsHTML(card.requirements)}</div>
    <div class="effect-row">${strong || "<span class='effect'>起動効果なし</span>"}</div>
    ${weak}${source}
  </article>`;
}

function render() {
  const query = $("#search").value.trim().toLocaleLowerCase("ja");
  const tag = $("#tag-filter").value;
  const role = $("#role-filter").value;
  const cards = catalog.cards.filter((card) => {
    const haystack = [card.name, card.text, card.subject_taxon, card.role].join(" ").toLocaleLowerCase("ja");
    return (!query || haystack.includes(query)) && (!tag || card.tags.some((item) => item.id === tag)) && (!role || card.role === role);
  });
  $("#card-count").textContent = `${cards.length} / ${catalog.count}枚`;
  $("#catalog").innerHTML = cards.length ? cards.map(cardHTML).join("") : `<p class="catalog-empty">条件に合うカードはありません。</p>`;
}

async function loadCatalog() {
  const response = await fetch("/api/cards");
  if (!response.ok) throw new Error("カード一覧を読み込めませんでした。");
  catalog = await response.json();
  $("#tag-filter").insertAdjacentHTML("beforeend", catalog.tags.map((tag) => `<option value="${esc(tag.id)}">${esc(tag.name)}</option>`).join(""));
  $("#role-filter").insertAdjacentHTML("beforeend", catalog.roles.map((role) => `<option value="${esc(role)}">${esc(role)}</option>`).join(""));
  render();
}

$("#search").addEventListener("input", render);
$("#tag-filter").addEventListener("change", render);
$("#role-filter").addEventListener("change", render);
loadCatalog().catch((error) => { $("#catalog").innerHTML = `<p class="warning">${esc(error.message)}</p>`; });
