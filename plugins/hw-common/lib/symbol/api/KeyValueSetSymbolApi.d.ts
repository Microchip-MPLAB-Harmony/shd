import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
interface KeyValueSetSymbol extends ConfigSymbol<number> {
    optionPairs: OptionPair[];
    displayMode: DisplayMode;
    selectedOptionPair: OptionPair;
}
interface OptionPair {
    key: string;
    value: string;
    description: string;
}
export declare enum DisplayMode {
    Key = "Key",
    Value = "Value",
    Description = "Description"
}
declare class KeyValueSetSymbolApi extends ConfigSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getValue: (componentId: string, symbolId: string) => Promise<number>;
    setValue: (componentId: string, symbolId: string, value: number) => Promise<void>;
    getOptionPairs: (componentId: string, symbolId: string) => Promise<OptionPair[]>;
    getSelectedOptionPair: (componentId: string, symbolId: string) => Promise<OptionPair>;
    getDisplayMode: (componentId: string, symbolId: string) => Promise<string>;
    setDisplayMode: (componentId: string, symbolId: string, displayMode: DisplayMode) => Promise<void>;
    getKeyValueSetSymbol: (componentId: string, symbolId: string) => Promise<KeyValueSetSymbol>;
}
export declare const keyValueSetSymbolApi: KeyValueSetSymbolApi;
export type { KeyValueSetSymbol, OptionPair };
export default KeyValueSetSymbolApi;
