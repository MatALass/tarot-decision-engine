import type { TrickDraft } from '@/stores/gameSetup';
type __VLS_Props = {
    title: string;
    description: string;
    modelValue: TrickDraft;
    usedTokens: string[];
    allowPartial: boolean;
    removable?: boolean;
};
declare const _default: import("vue").DefineComponent<__VLS_Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {
    updatePlayer: (index: number, playerIndex: number | null) => any;
    updateCard: (index: number, token: string | null) => any;
    remove: () => any;
}, string, import("vue").PublicProps, Readonly<__VLS_Props> & Readonly<{
    onUpdatePlayer?: ((index: number, playerIndex: number | null) => any) | undefined;
    onUpdateCard?: ((index: number, token: string | null) => any) | undefined;
    onRemove?: (() => any) | undefined;
}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
