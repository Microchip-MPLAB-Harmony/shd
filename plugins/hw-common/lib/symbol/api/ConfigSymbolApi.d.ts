import VisibleSymbolApi, { VisibleSymbol } from './VisibleSymbolApi';
interface ConfigSymbol<T> extends VisibleSymbol {
    label: string;
    description: string;
    readOnly: boolean;
    value: T;
}
declare class ConfigSymbolApi extends VisibleSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getLabel: (componentId: string, symbolId: string) => Promise<string>;
    getDescription: (componentId: string, symbolId: string) => Promise<string>;
    getReadOnly: (componentId: string, symbolId: string) => Promise<boolean>;
    getValue: (componentId: string, symbolId: string) => Promise<any>;
}
export declare const configSymbolApi: ConfigSymbolApi;
export type { ConfigSymbol };
export default ConfigSymbolApi;
