import ConfigSymbolApi from './ConfigSymbolApi';
import { IntegerSymbol } from './IntegerSymbolApi';
type FloatSymbol = IntegerSymbol;
declare class FloatSymbolApi extends ConfigSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getValue: (componentId: string, symbolId: string) => Promise<number>;
    setValue: (componentId: string, symbolId: string, value: number) => Promise<void>;
    getFloatSymbol: (componentId: string, symbolId: string) => Promise<FloatSymbol>;
}
export declare const floatSymbolApi: FloatSymbolApi;
export type { FloatSymbol };
export default FloatSymbolApi;
