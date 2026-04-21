import { computed, reactive, ref } from 'vue';
import { defineStore } from 'pinia';
import { recommendMove } from '@/lib/api';
import { CARD_LOOKUP, sortCardTokens } from '@/lib/cards';
export const useGameSetupStore = defineStore('gameSetup', () => {
    const remainingHand = ref([]);
    const contract = ref('GARDE');
    const playerIndex = ref(0);
    const takerIndex = ref(0);
    const partnerIndex = ref(null);
    const nextPlayerIndex = ref(0);
    const nSamples = ref(200);
    const seed = ref(0);
    const policy = ref('expected_score');
    const currentTrick = reactive(createEmptyTrick('current'));
    const completedTricks = ref([]);
    const isSubmitting = ref(false);
    const apiError = ref(null);
    const lastRecommendation = ref(null);
    const lastSubmittedPayload = ref(null);
    const selectedCardSet = computed(() => {
        const cards = new Set(remainingHand.value);
        for (const entry of currentTrick.entries) {
            if (entry.card)
                cards.add(entry.card);
        }
        for (const trick of completedTricks.value) {
            for (const entry of trick.entries) {
                if (entry.card)
                    cards.add(entry.card);
            }
        }
        return cards;
    });
    const validationErrors = computed(() => {
        const errors = [];
        const allUsedCards = [];
        if (remainingHand.value.length === 0) {
            errors.push('Sélectionne la main restante du joueur observé.');
        }
        const ownPlayedCards = collectEntries([currentTrick, ...completedTricks.value])
            .filter((entry) => entry.playerIndex === playerIndex.value)
            .map((entry) => entry.card);
        if (remainingHand.value.length + ownPlayedCards.length !== 15) {
            errors.push('La main restante plus les cartes déjà jouées par le joueur observé doivent reconstituer exactement 15 cartes.');
        }
        if (partnerIndex.value !== null && partnerIndex.value === takerIndex.value) {
            errors.push('Le partenaire ne peut pas être identique au preneur.');
        }
        const currentEntries = normalizeEntries(currentTrick.entries);
        if (currentEntries.length > 4) {
            errors.push('Le pli courant ne peut pas contenir plus de 4 cartes.');
        }
        if (new Set(currentEntries.map((entry) => entry.playerIndex)).size !== currentEntries.length) {
            errors.push('Le pli courant contient des joueurs dupliqués.');
        }
        if (currentEntries.some((entry) => entry.playerIndex === nextPlayerIndex.value)) {
            errors.push('Le joueur suivant ne peut pas avoir déjà joué dans le pli courant.');
        }
        for (const trick of completedTricks.value) {
            const entries = normalizeEntries(trick.entries);
            if (entries.length !== 5) {
                errors.push('Chaque pli complété doit contenir exactement 5 cartes.');
            }
            if (new Set(entries.map((entry) => entry.playerIndex)).size !== entries.length) {
                errors.push('Un pli complété contient des joueurs dupliqués.');
            }
        }
        for (const token of remainingHand.value) {
            allUsedCards.push(token);
        }
        for (const entry of currentEntries) {
            allUsedCards.push(entry.card);
        }
        for (const trick of completedTricks.value) {
            for (const entry of normalizeEntries(trick.entries)) {
                allUsedCards.push(entry.card);
            }
        }
        if (new Set(allUsedCards).size !== allUsedCards.length) {
            errors.push('Une même carte est utilisée plusieurs fois dans l’état saisi.');
        }
        for (const token of allUsedCards) {
            if (!CARD_LOOKUP.has(token)) {
                errors.push(`Carte inconnue détectée: ${token}.`);
            }
        }
        return errors;
    });
    const canSubmit = computed(() => validationErrors.value.length === 0 && !isSubmitting.value);
    function toggleRemainingHandCard(token) {
        const current = new Set(remainingHand.value);
        if (current.has(token)) {
            current.delete(token);
        }
        else {
            current.add(token);
        }
        remainingHand.value = sortCardTokens([...current]);
    }
    function setEntryCard(target, index, token) {
        target.entries[index].card = token;
    }
    function setEntryPlayer(target, index, playerIndexValue) {
        target.entries[index].playerIndex = playerIndexValue;
    }
    function addCompletedTrick() {
        completedTricks.value.push(createEmptyTrick(`completed-${completedTricks.value.length + 1}`));
    }
    function removeCompletedTrick(id) {
        completedTricks.value = completedTricks.value.filter((trick) => trick.id !== id);
    }
    function resetAll() {
        remainingHand.value = [];
        contract.value = 'GARDE';
        playerIndex.value = 0;
        takerIndex.value = 0;
        partnerIndex.value = null;
        nextPlayerIndex.value = 0;
        nSamples.value = 200;
        seed.value = 0;
        policy.value = 'expected_score';
        Object.assign(currentTrick, createEmptyTrick('current'));
        completedTricks.value = [];
        apiError.value = null;
    }
    async function submitRecommendation() {
        apiError.value = null;
        if (!canSubmit.value) {
            return false;
        }
        const payload = buildPayload();
        isSubmitting.value = true;
        try {
            lastRecommendation.value = await recommendMove(payload);
            lastSubmittedPayload.value = payload;
            return true;
        }
        catch (error) {
            apiError.value = extractApiErrorMessage(error);
            return false;
        }
        finally {
            isSubmitting.value = false;
        }
    }
    function buildPayload() {
        return {
            remaining_hand: remainingHand.value.join(','),
            contract: contract.value,
            player_index: playerIndex.value,
            taker_index: takerIndex.value,
            partner_index: partnerIndex.value,
            current_trick: serializeTrick(currentTrick),
            completed_tricks: completedTricks.value.map((trick) => serializeTrick(trick)),
            next_player_index: nextPlayerIndex.value,
            n_samples: nSamples.value,
            seed: seed.value,
            policy: policy.value,
        };
    }
    return {
        remainingHand,
        contract,
        playerIndex,
        takerIndex,
        partnerIndex,
        nextPlayerIndex,
        nSamples,
        seed,
        policy,
        currentTrick,
        completedTricks,
        isSubmitting,
        apiError,
        lastRecommendation,
        lastSubmittedPayload,
        selectedCardSet,
        validationErrors,
        canSubmit,
        toggleRemainingHandCard,
        setEntryCard,
        setEntryPlayer,
        addCompletedTrick,
        removeCompletedTrick,
        resetAll,
        submitRecommendation,
    };
});
function createEmptyTrick(id) {
    return {
        id,
        entries: Array.from({ length: 5 }, () => ({ playerIndex: null, card: null })),
    };
}
function normalizeEntries(entries) {
    return entries
        .filter((entry) => entry.playerIndex !== null && entry.card !== null)
        .map((entry) => ({ playerIndex: entry.playerIndex, card: entry.card }));
}
function collectEntries(tricks) {
    return tricks.flatMap((trick) => normalizeEntries(trick.entries));
}
function serializeTrick(trick) {
    return normalizeEntries(trick.entries)
        .map((entry) => `${entry.playerIndex}:${entry.card}`)
        .join('|');
}
function extractApiErrorMessage(error) {
    if (typeof error === 'object' && error !== null && 'response' in error) {
        const response = error.response;
        return response?.data?.detail ?? 'La requête API a échoué.';
    }
    return 'La requête API a échoué.';
}
