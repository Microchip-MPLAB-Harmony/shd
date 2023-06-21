import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
type BooleanSymbol = ConfigSymbol<boolean> & {
    symbolType: 'BooleanSymbol';
};
declare class BooleanSymbolApi extends ConfigSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getValue: (componentId: string, symbolId: string) => Promise<boolean>;
    setValue: (componentId: string, symbolId: string, value: boolean) => Promise<void>;
    getBooleanSymbol: (componentId: string, symbolId: string) => Promise<BooleanSymbol>;
}
export declare const booleanSymbolApi: BooleanSymbolApi;
export type { BooleanSymbol };
export default BooleanSymbolApi;
