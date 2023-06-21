import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
interface IntegerSymbol extends ConfigSymbol<number> {
    value: number;
    min: number;
    max: number;
}
declare class IntegerSymbolApi extends ConfigSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getValue: (componentId: string, symbolId: string) => Promise<number>;
    setValue: (componentId: string, symbolId: string, value: number) => Promise<void>;
    getIntegerSymbol: (componentId: string, symbolId: string) => Promise<IntegerSymbol>;
}
export declare const integerSymbolApi: IntegerSymbolApi;
export type { IntegerSymbol };
export default IntegerSymbolApi;
