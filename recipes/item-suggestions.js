const ROOT_URL = "https://jtachan.github.io/masalazafran";

let database = [];
let lastShownRecipes = [];

document.addEventListener('DOMContentLoaded', init);

async function init() {
    const container = document.querySelector('div.item-suggestions');
    if (!container) {
        // No target element on this page; nothing to do.
        return;
    }

    try {
        database = await loadDatabase("db.json");
    } catch (err) {
        console.error('item-suggestions: failed to load db.json', err);
        renderError(container);
        return;
    }

    if (!Array.isArray(database) || database.length === 0) {
        console.error('item-suggestions: db.json did not contain a non-empty array');
        renderError(container);
        return;
    }

    buildUI(container);
}

async function loadDatabase(path) {
    const response = await fetch(path, {cache: 'no-store'});
    if (!response.ok) {
        throw new Error(`Failed to fetch ${path}: ${response.status} ${response.statusText}`);
    }
    return response.json();
}

function buildUI(container) {
    container.innerHTML = '';
    container.classList.add('item-suggestions--initialized');

    const toolbar = document.createElement('div');
    toolbar.className = 'item-suggestions__toolbar';

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'item-suggestions__button';
    button.textContent = 'new suggestions';
    button.addEventListener('click', () => renderCards(container));

    toolbar.appendChild(button);
    container.appendChild(toolbar);

    const cardsWrapper = document.createElement('div');
    cardsWrapper.className = 'item-suggestions__cards';
    container.appendChild(cardsWrapper);

    renderCards(container);
}

function renderCards(container) {
    const cardsWrapper = container.querySelector('.item-suggestions__cards');
    if (!cardsWrapper) return;

    const picks = pickRandomEntries(database, 5, lastShownRecipes);
    lastShownRecipes = picks.map((entry) => entry.recipe);

    // Removing any previous contents, so when the button is clicked again the cards don't stack up.
    cardsWrapper.innerHTML = '';

    picks.forEach((entry) => {
        let recipe_html_name = entry.recipe.toLowerCase().replace("'s", "").replaceAll(" ", "_")
        let singular_section = entry.section.endsWith("s") ? entry.section.slice(0, -1) : entry.section;

        const card = document.createElement('div');
        card.className = 'item-suggestions__card';
        if (entry.image !== "") {
            card.style.backgroundImage = `url("${ROOT_URL}/_imgs/${entry.image}")`;
            card.style.backgroundSize = "cover";       // scales image to fill the div
            card.style.backgroundPosition = "center";  // centers the image
            card.style.backgroundRepeat = "no-repeat"; // prevents tiling
        }

        const title = document.createElement('a');
        title.className = 'item-suggestions__card-title';
        title.textContent = entry.recipe;
        title.href = `${ROOT_URL}/${entry.section}/${recipe_html_name}`;

        const tags = document.createElement("span");
        tags.className = "item-suggestions__card-tags";
        tags.textContent = `${entry.nationality} ${singular_section}`
        tags.style.fontStyle = "italic"

        card.appendChild(title);
        card.appendChild(tags);
        cardsWrapper.appendChild(card);
    });
}

/**
 * Picks `count` random, distinct entries from `pool`.
 * Tries to avoid returning the exact same set as `previousRecipes`
 * (by re-shuffling once if the new picks are identical to the
 * previous ones). This is a best-effort avoidance, not a guarantee,
 * since with small pools an exact repeat may be unavoidable.
 */
function pickRandomEntries(pool, count, previousRecipes) {
    let picks = shuffleAndTake(pool, count);

    if (previousRecipes.length === count && sameRecipeSet(picks, previousRecipes)) {
        picks = shuffleAndTake(pool, count);
    }

    return picks;
}

function shuffleAndTake(pool, count) {
    const copy = pool.slice();
    // Fisher-Yates shuffle
    for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy.slice(0, Math.min(count, copy.length));
}

function sameRecipeSet(picksA, previousRecipes) {
    const setA = new Set(picksA.map((entry) => entry.recipe));
    const setB = new Set(previousRecipes);
    if (setA.size !== setB.size) return false;
    for (const value of setA) {
        if (!setB.has(value)) return false;
    }
    return true;
}

function renderError(container) {
    container.innerHTML = '';
    const msg = document.createElement('p');
    msg.className = 'item-suggestions__error';
    msg.textContent = 'Suggestions could not be loaded.';
    container.appendChild(msg);
}
