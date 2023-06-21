import { ISymbol } from './SymbolApi';
declare class SymbolUtilApi {
    readonly path: string;
    constructor(path?: string);
    getSymbolTypes: (componentId: string, symbolIds: string[]) => Promise<ISymbol[]>;
    getSymbols: (componentId: string, symbolIds: string[]) => Promise<any[]>;
    getChildCount: (componentId: string, symbolId: string) => Promise<number>;
    getChildren: (componentId: string, symbolId: string) => Promise<string[]>;
}
export declare const symbolUtilApi: SymbolUtilApi;
export default SymbolUtilApi;
