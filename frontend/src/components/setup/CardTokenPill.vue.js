import { computed } from 'vue';
import { CARD_LOOKUP } from '@/lib/cards';
const props = defineProps();
const cardData = computed(() => CARD_LOOKUP.get(props.token));
const SUIT_SYMBOL = {
    SPADES: '♠',
    HEARTS: '♥',
    DIAMONDS: '♦',
    CLUBS: '♣',
    TRUMPS: '★',
    SPECIAL: '✦',
};
const suitSymbol = computed(() => {
    const suit = cardData.value?.suit;
    return suit ? SUIT_SYMBOL[suit] : '';
});
const isRed = computed(() => {
    const suit = cardData.value?.suit;
    return suit === 'HEARTS' || suit === 'DIAMONDS';
});
const isTrump = computed(() => cardData.value?.suit === 'TRUMPS');
const isSpecial = computed(() => cardData.value?.suit === 'SPECIAL');
// Short display: just rank part
const shortToken = computed(() => {
    if (!props.token)
        return '';
    if (props.token === 'EXCUSE')
        return '☽';
    // Remove suit suffix for colored suits
    return props.token.replace(/[SHDC]$/, '');
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "relative overflow-hidden rounded-lg border transition-all duration-150 select-none" },
    ...{ class: ([
            __VLS_ctx.compact ? 'px-2.5 py-1.5' : 'px-3 py-2.5',
            __VLS_ctx.active
                ? __VLS_ctx.isTrump
                    ? 'border-gold/60 bg-gold/15 shadow-glow-gold'
                    : __VLS_ctx.isSpecial
                        ? 'border-purple-400/50 bg-purple-400/10'
                        : __VLS_ctx.isRed
                            ? 'border-ruby/50 bg-ruby/10'
                            : 'border-sapphire/50 bg-sapphire/10'
                : 'border-border bg-card hover:border-rim hover:bg-card/80',
        ]) },
});
if (__VLS_ctx.rank !== undefined) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold" },
        ...{ class: (__VLS_ctx.rank === 1 ? 'bg-gold text-deep' : 'bg-border text-subtle') },
    });
    (__VLS_ctx.rank);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex items-center gap-1.5" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "text-xs font-bold leading-none" },
    ...{ class: ([
            __VLS_ctx.isRed ? 'text-ruby' : '',
            __VLS_ctx.isTrump ? 'text-gold' : '',
            __VLS_ctx.isSpecial ? 'text-purple-400' : '',
            !__VLS_ctx.isRed && !__VLS_ctx.isTrump && !__VLS_ctx.isSpecial ? 'text-sapphire' : '',
        ]) },
});
(__VLS_ctx.suitSymbol);
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "font-mono font-semibold leading-none" },
    ...{ class: ([
            __VLS_ctx.compact ? 'text-xs' : 'text-sm',
            __VLS_ctx.active
                ? __VLS_ctx.isTrump ? 'text-gold-light' : __VLS_ctx.isRed ? 'text-red-200' : 'text-blue-200'
                : 'text-text',
        ]) },
});
(__VLS_ctx.shortToken);
if (!__VLS_ctx.compact && __VLS_ctx.cardData) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "mt-1 text-[10px] text-subtle leading-none truncate" },
    });
    (__VLS_ctx.cardData.label);
}
/** @type {__VLS_StyleScopedClasses['relative']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-all']} */ ;
/** @type {__VLS_StyleScopedClasses['duration-150']} */ ;
/** @type {__VLS_StyleScopedClasses['select-none']} */ ;
/** @type {__VLS_StyleScopedClasses['absolute']} */ ;
/** @type {__VLS_StyleScopedClasses['-right-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['-top-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['h-4']} */ ;
/** @type {__VLS_StyleScopedClasses['w-4']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[9px]']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-none']} */ ;
/** @type {__VLS_StyleScopedClasses['font-mono']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-none']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
/** @type {__VLS_StyleScopedClasses['text-subtle']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-none']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            cardData: cardData,
            suitSymbol: suitSymbol,
            isRed: isRed,
            isTrump: isTrump,
            isSpecial: isSpecial,
            shortToken: shortToken,
        };
    },
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
