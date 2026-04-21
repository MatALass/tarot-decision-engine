export interface TrickRow {
    seat: number;
    card: string;
    winner?: boolean;
    lead?: boolean;
}
type __VLS_Props = {
    title: string;
    subtitle: string;
    rows: TrickRow[];
    emptyMessage: string;
};
declare const _default: import("vue").DefineComponent<__VLS_Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<__VLS_Props> & Readonly<{}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
