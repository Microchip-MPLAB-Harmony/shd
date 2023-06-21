import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
type StringSymbol = ConfigSymbol<string>;
declare class StringSymbolApi extends ConfigSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getValue: (componentId: string, symbolId: string) => Promise<string>;
    setValue: (componentId: string, symbolId: string, value: string) => Promise<void>;
    getStringSymbol: (componentId: string, symbolId: string) => Promise<StringSymbol>;
}
export declare const stringSymbolApi: StringSymbolApi;
export type { StringSymbol };
export default stringSymbolApi;
