export interface CompletedTrickView {
    id: string;
    trickNumber: number;
    leadSeat: number | null;
    winnerSeat: number | null;
    cards: Array<{
        seat: number;
        card: string;
    }>;
}
type __VLS_Props = {
    tricks: CompletedTrickView[];
};
declare const _default: import("vue").DefineComponent<__VLS_Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<__VLS_Props> & Readonly<{}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
