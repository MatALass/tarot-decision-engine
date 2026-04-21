import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { RouterLink } from 'vue-router';
import SeatStatusCard from '@/components/game/SeatStatusCard.vue';
import StateMetricCard from '@/components/game/StateMetricCard.vue';
import TrickTable from '@/components/game/TrickTable.vue';
import TrickTimeline from '@/components/game/TrickTimeline.vue';
import CardTokenPill from '@/components/setup/CardTokenPill.vue';
import SectionHeader from '@/components/ui/SectionHeader.vue';
import { useGameSetupStore } from '@/stores/gameSetup';
const setupStore = useGameSetupStore();
const { remainingHand, contract, playerIndex, takerIndex, partnerIndex, nextPlayerIndex, currentTrick, completedTricks, lastRecommendation, isSubmitting, } = storeToRefs(setupStore);
function normalizeEntries(entries) {
    return entries.filter((entry) => entry.playerIndex !== null && entry.card !== null);
}
const currentTrickRows = computed(() => normalizeEntries(currentTrick.value.entries).map((entry, index) => ({
    seat: entry.playerIndex,
    card: entry.card,
    lead: index === 0,
    winner: false,
})));
const completedTrickViews = computed(() => completedTricks.value.map((trick, trickIndex) => {
    const entries = normalizeEntries(trick.entries);
    return {
        id: trick.id,
        trickNumber: trickIndex + 1,
        leadSeat: entries[0]?.playerIndex ?? null,
        winnerSeat: entries.length === 5 ? entries[entries.length - 1].playerIndex : null,
        cards: entries.map((entry) => ({ seat: entry.playerIndex, card: entry.card })),
    };
}));
const playedCardCount = computed(() => currentTrickRows.value.length +
    completedTrickViews.value.reduce((total, trick) => total + trick.cards.length, 0));
const observedPlayedCount = computed(() => {
    const inCurrent = currentTrickRows.value.filter((row) => row.seat === playerIndex.value).length;
    const inHistory = completedTrickViews.value.reduce((total, trick) => total + trick.cards.filter((card) => card.seat === playerIndex.value).length, 0);
    return inCurrent + inHistory;
});
const seatSummaries = computed(() => Array.from({ length: 5 }, (_, seat) => {
    const roles = [];
    if (seat === playerIndex.value)
        roles.push('Main observée');
    if (seat === takerIndex.value)
        roles.push('Preneur');
    if (partnerIndex.value !== null && seat === partnerIndex.value)
        roles.push('Partenaire');
    if (roles.length === 0)
        roles.push('Adversaire');
    let status = 'Main inconnue.';
    if (seat === playerIndex.value)
        status = `${remainingHand.value.length} cartes connues, ${observedPlayedCount.value} jouées.`;
    else if (seat === nextPlayerIndex.value)
        status = 'Prochain à jouer.';
    return {
        seat,
        role: roles.join(' · '),
        status,
        highlighted: seat === playerIndex.value || seat === nextPlayerIndex.value,
        cards: seat === playerIndex.value ? remainingHand.value : [],
        meta: seat === nextPlayerIndex.value ? 'À jouer' : '',
    };
}));
const recommendationSummary = computed(() => {
    if (!lastRecommendation.value)
        return null;
    const best = lastRecommendation.value.evaluations.find((item) => item.action.card === lastRecommendation.value?.recommended_action.card);
    return {
        card: lastRecommendation.value.recommended_action.card,
        rationale: lastRecommendation.value.rationale,
        expectedScore: best?.expected_score ?? null,
        winRate: best?.win_rate ?? null,
    };
});
const isEmpty = computed(() => remainingHand.value.length === 0 &&
    completedTricks.value.length === 0 &&
    currentTrickRows.value.length === 0);
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "animate-fade-in" },
});
/** @type {[typeof SectionHeader, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(SectionHeader, new SectionHeader({
    eyebrow: "État de partie",
    title: "Cockpit observable",
    description: "Vue synchronisée de l'état courant : pli en jeu, historique, rôles des sièges et dernière recommandation.",
}));
const __VLS_1 = __VLS_0({
    eyebrow: "État de partie",
    title: "Cockpit observable",
    description: "Vue synchronisée de l'état courant : pli en jeu, historique, rôles des sièges et dernière recommandation.",
}, ...__VLS_functionalComponentArgsRest(__VLS_0));
if (__VLS_ctx.isEmpty) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex flex-col items-center gap-4 rounded-2xl border border-dashed border-border py-20 text-center" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "text-4xl opacity-20 font-display" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "text-sm text-subtle" },
    });
    const __VLS_3 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    const __VLS_4 = __VLS_asFunctionalComponent(__VLS_3, new __VLS_3({
        to: "/setup",
        ...{ class: "btn-gold rounded-xl px-6 py-2.5 text-sm" },
    }));
    const __VLS_5 = __VLS_4({
        to: "/setup",
        ...{ class: "btn-gold rounded-xl px-6 py-2.5 text-sm" },
    }, ...__VLS_functionalComponentArgsRest(__VLS_4));
    __VLS_6.slots.default;
    var __VLS_6;
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "space-y-5" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid gap-3 sm:grid-cols-2 xl:grid-cols-4" },
    });
    /** @type {[typeof StateMetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_7 = __VLS_asFunctionalComponent(StateMetricCard, new StateMetricCard({
        label: "Main observée",
        value: (`${__VLS_ctx.remainingHand.length} cartes`),
        hint: (`Joueur ${__VLS_ctx.playerIndex} · ${__VLS_ctx.observedPlayedCount} déjà jouées`),
    }));
    const __VLS_8 = __VLS_7({
        label: "Main observée",
        value: (`${__VLS_ctx.remainingHand.length} cartes`),
        hint: (`Joueur ${__VLS_ctx.playerIndex} · ${__VLS_ctx.observedPlayedCount} déjà jouées`),
    }, ...__VLS_functionalComponentArgsRest(__VLS_7));
    /** @type {[typeof StateMetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_10 = __VLS_asFunctionalComponent(StateMetricCard, new StateMetricCard({
        label: "Cartes jouées",
        value: (`${__VLS_ctx.playedCardCount}`),
        hint: "Pli courant + historique",
    }));
    const __VLS_11 = __VLS_10({
        label: "Cartes jouées",
        value: (`${__VLS_ctx.playedCardCount}`),
        hint: "Pli courant + historique",
    }, ...__VLS_functionalComponentArgsRest(__VLS_10));
    /** @type {[typeof StateMetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_13 = __VLS_asFunctionalComponent(StateMetricCard, new StateMetricCard({
        label: "Contrat",
        value: (__VLS_ctx.contract),
        hint: (`Preneur: J${__VLS_ctx.takerIndex}${__VLS_ctx.partnerIndex !== null ? ` · Partenaire: J${__VLS_ctx.partnerIndex}` : ''}`),
    }));
    const __VLS_14 = __VLS_13({
        label: "Contrat",
        value: (__VLS_ctx.contract),
        hint: (`Preneur: J${__VLS_ctx.takerIndex}${__VLS_ctx.partnerIndex !== null ? ` · Partenaire: J${__VLS_ctx.partnerIndex}` : ''}`),
    }, ...__VLS_functionalComponentArgsRest(__VLS_13));
    /** @type {[typeof StateMetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_16 = __VLS_asFunctionalComponent(StateMetricCard, new StateMetricCard({
        label: "Prochain joueur",
        value: (`Joueur ${__VLS_ctx.nextPlayerIndex}`),
        hint: "Prochain à jouer dans l'état synchronisé",
    }));
    const __VLS_17 = __VLS_16({
        label: "Prochain joueur",
        value: (`Joueur ${__VLS_ctx.nextPlayerIndex}`),
        hint: "Prochain à jouer dans l'état synchronisé",
    }, ...__VLS_functionalComponentArgsRest(__VLS_16));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid gap-5 xl:grid-cols-[1fr_1fr]" },
    });
    /** @type {[typeof TrickTable, ]} */ ;
    // @ts-ignore
    const __VLS_19 = __VLS_asFunctionalComponent(TrickTable, new TrickTable({
        title: "Pli courant",
        subtitle: "Cartes déjà jouées dans ce pli, dans l'ordre d'entame.",
        rows: (__VLS_ctx.currentTrickRows),
        emptyMessage: "Aucune carte jouée dans le pli courant.",
    }));
    const __VLS_20 = __VLS_19({
        title: "Pli courant",
        subtitle: "Cartes déjà jouées dans ce pli, dans l'ordre d'entame.",
        rows: (__VLS_ctx.currentTrickRows),
        emptyMessage: "Aucune carte jouée dans le pli courant.",
    }, ...__VLS_functionalComponentArgsRest(__VLS_19));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "rounded-2xl panel-base overflow-hidden" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex items-center justify-between px-5 py-4" },
        ...{ style: {} },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({
        ...{ class: "font-display text-sm font-semibold tracking-wider text-gold-light" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[10px] font-medium" },
        ...{ class: (__VLS_ctx.isSubmitting
                ? 'border-amber/25 bg-amber/8 text-amber'
                : 'border-emerald/25 bg-emerald/8 text-emerald') },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "h-1.5 w-1.5 rounded-full" },
        ...{ class: (__VLS_ctx.isSubmitting ? 'bg-amber animate-pulse' : 'bg-emerald') },
    });
    (__VLS_ctx.isSubmitting ? 'Évaluation…' : 'Synchronisé');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "px-5 py-4 space-y-4" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "rounded-xl border border-border bg-deep p-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "text-[10px] tracking-[0.25em] text-subtle uppercase mb-2" },
    });
    if (__VLS_ctx.remainingHand.length === 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "text-xs text-muted italic" },
        });
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "flex flex-wrap gap-1.5" },
        });
        for (const [card] of __VLS_getVForSourceType((__VLS_ctx.remainingHand))) {
            /** @type {[typeof CardTokenPill, ]} */ ;
            // @ts-ignore
            const __VLS_22 = __VLS_asFunctionalComponent(CardTokenPill, new CardTokenPill({
                key: (card),
                token: (card),
                compact: true,
            }));
            const __VLS_23 = __VLS_22({
                key: (card),
                token: (card),
                compact: true,
            }, ...__VLS_functionalComponentArgsRest(__VLS_22));
        }
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "rounded-xl border p-3" },
        ...{ class: (__VLS_ctx.recommendationSummary
                ? 'border-gold/25 bg-gold/5'
                : 'border-border bg-deep') },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "text-[10px] tracking-[0.25em] text-subtle uppercase mb-2" },
    });
    if (__VLS_ctx.recommendationSummary) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "space-y-2" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "flex items-center gap-2.5" },
        });
        /** @type {[typeof CardTokenPill, ]} */ ;
        // @ts-ignore
        const __VLS_25 = __VLS_asFunctionalComponent(CardTokenPill, new CardTokenPill({
            token: (__VLS_ctx.recommendationSummary.card),
            compact: true,
            active: (true),
        }));
        const __VLS_26 = __VLS_25({
            token: (__VLS_ctx.recommendationSummary.card),
            compact: true,
            active: (true),
        }, ...__VLS_functionalComponentArgsRest(__VLS_25));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "text-xs text-subtle flex-1" },
        });
        (__VLS_ctx.recommendationSummary.rationale);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "grid grid-cols-2 gap-2" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "rounded-lg border border-border bg-deep px-3 py-2" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "text-[10px] text-subtle" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "font-mono text-sm font-semibold metric-gold" },
        });
        (__VLS_ctx.recommendationSummary.expectedScore !== null
            ? (__VLS_ctx.recommendationSummary.expectedScore > 0 ? '+' : '') + __VLS_ctx.recommendationSummary.expectedScore.toFixed(2)
            : '—');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "rounded-lg border border-border bg-deep px-3 py-2" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "text-[10px] text-subtle" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "font-mono text-sm font-semibold text-emerald" },
        });
        (__VLS_ctx.recommendationSummary.winRate !== null
            ? `${(__VLS_ctx.recommendationSummary.winRate * 100).toFixed(1)}%`
            : '—');
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "text-xs text-muted italic" },
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid grid-cols-2 gap-2" },
    });
    const __VLS_28 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    const __VLS_29 = __VLS_asFunctionalComponent(__VLS_28, new __VLS_28({
        to: "/setup",
        ...{ class: "rounded-xl border border-border py-2.5 text-center text-xs font-medium text-subtle transition hover:border-rim hover:text-text" },
    }));
    const __VLS_30 = __VLS_29({
        to: "/setup",
        ...{ class: "rounded-xl border border-border py-2.5 text-center text-xs font-medium text-subtle transition hover:border-rim hover:text-text" },
    }, ...__VLS_functionalComponentArgsRest(__VLS_29));
    __VLS_31.slots.default;
    var __VLS_31;
    const __VLS_32 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    const __VLS_33 = __VLS_asFunctionalComponent(__VLS_32, new __VLS_32({
        to: "/recommendation",
        ...{ class: "btn-gold rounded-xl py-2.5 text-center text-xs" },
    }));
    const __VLS_34 = __VLS_33({
        to: "/recommendation",
        ...{ class: "btn-gold rounded-xl py-2.5 text-center text-xs" },
    }, ...__VLS_functionalComponentArgsRest(__VLS_33));
    __VLS_35.slots.default;
    var __VLS_35;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid gap-5 xl:grid-cols-[1fr_1fr]" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid grid-cols-2 gap-3 content-start" },
    });
    for (const [seat] of __VLS_getVForSourceType((__VLS_ctx.seatSummaries))) {
        /** @type {[typeof SeatStatusCard, ]} */ ;
        // @ts-ignore
        const __VLS_36 = __VLS_asFunctionalComponent(SeatStatusCard, new SeatStatusCard({
            key: (seat.seat),
            seat: (seat.seat),
            role: (seat.role),
            status: (seat.status),
            highlighted: (seat.highlighted),
            cards: (seat.cards),
            meta: (seat.meta),
        }));
        const __VLS_37 = __VLS_36({
            key: (seat.seat),
            seat: (seat.seat),
            role: (seat.role),
            status: (seat.status),
            highlighted: (seat.highlighted),
            cards: (seat.cards),
            meta: (seat.meta),
        }, ...__VLS_functionalComponentArgsRest(__VLS_36));
    }
    /** @type {[typeof TrickTimeline, ]} */ ;
    // @ts-ignore
    const __VLS_39 = __VLS_asFunctionalComponent(TrickTimeline, new TrickTimeline({
        tricks: (__VLS_ctx.completedTrickViews),
    }));
    const __VLS_40 = __VLS_39({
        tricks: (__VLS_ctx.completedTrickViews),
    }, ...__VLS_functionalComponentArgsRest(__VLS_39));
}
/** @type {__VLS_StyleScopedClasses['animate-fade-in']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-4']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-dashed']} */ ;
/** @type {__VLS_StyleScopedClasses['border-border']} */ ;
/** @type {__VLS_StyleScopedClasses['py-20']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-4xl']} */ ;
/** @type {__VLS_StyleScopedClasses['opacity-20']} */ ;
/** @type {__VLS_StyleScopedClasses['font-display']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-gold']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-5']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-2']} */ ;
/** @type {__VLS_StyleScopedClasses['xl:grid-cols-4']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-5']} */ ;
/** @type {__VLS_StyleScopedClasses['xl:grid-cols-[1fr_1fr]']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['panel-base']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['px-5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['font-display']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['tracking-wider']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gold-light']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['h-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-4']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-border']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-deep']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
/** @type {__VLS_StyleScopedClasses['tracking-[0.25em]']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['uppercase']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-muted']} */ ;
/** @type {__VLS_StyleScopedClasses['italic']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
/** @type {__VLS_StyleScopedClasses['tracking-[0.25em]']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['uppercase']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-2']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-2']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-border']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-deep']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['font-mono']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-gold']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-border']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-deep']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['font-mono']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-emerald']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-muted']} */ ;
/** @type {__VLS_StyleScopedClasses['italic']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-2']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-border']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['transition']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:border-rim']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-text']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-gold']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-5']} */ ;
/** @type {__VLS_StyleScopedClasses['xl:grid-cols-[1fr_1fr]']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-2']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['content-start']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            RouterLink: RouterLink,
            SeatStatusCard: SeatStatusCard,
            StateMetricCard: StateMetricCard,
            TrickTable: TrickTable,
            TrickTimeline: TrickTimeline,
            CardTokenPill: CardTokenPill,
            SectionHeader: SectionHeader,
            remainingHand: remainingHand,
            contract: contract,
            playerIndex: playerIndex,
            takerIndex: takerIndex,
            partnerIndex: partnerIndex,
            nextPlayerIndex: nextPlayerIndex,
            isSubmitting: isSubmitting,
            currentTrickRows: currentTrickRows,
            completedTrickViews: completedTrickViews,
            playedCardCount: playedCardCount,
            observedPlayedCount: observedPlayedCount,
            seatSummaries: seatSummaries,
            recommendationSummary: recommendationSummary,
            isEmpty: isEmpty,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
