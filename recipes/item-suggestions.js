'use strict';

const DB_PATH = '/db.json';
const CARD_COUNT = 5;

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
        database = await loadDatabase(DB_PATH);
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

    const picks = pickRandomEntries(database, CARD_COUNT, lastShownRecipes);
    lastShownRecipes = picks.map((entry) => entry.recipe);

    cardsWrapper.innerHTML = '';

    picks.forEach((entry) => {
        const card = document.createElement('div');
        card.className = 'item-suggestions__card';

        const title = document.createElement('span');
        title.className = 'item-suggestions__card-title';
        title.textContent = entry.recipe;

        card.appendChild(title);
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
