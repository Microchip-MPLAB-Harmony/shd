import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
interface ComboSymbol extends ConfigSymbol<string> {
    options: string[];
}
declare class ComboSymbolApi extends ConfigSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getValue: (componentId: string, symbolId: string) => Promise<string>;
    setValue: (componentId: string, symbolId: string, value: string) => Promise<void>;
    getOptions: (componentId: string, symbolId: string) => Promise<string[]>;
    getComboSymbol: (componentId: string, symbolId: string) => Promise<ComboSymbol>;
}
export declare const comboSymbolApi: ComboSymbolApi;
export type { ComboSymbol };
export default ComboSymbolApi;
