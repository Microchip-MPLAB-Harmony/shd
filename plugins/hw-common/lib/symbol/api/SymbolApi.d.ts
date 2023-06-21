interface SymbolProps {
    componentId: string;
    symbolId: string;
}
interface ISymbol {
    componentId: string;
    symbolId: string;
    symbolType: string;
}
declare class SymbolApi {
    readonly path: string;
    constructor(path?: string);
    getSymbolType: (componentId: string, symbolId: string) => Promise<string>;
    getSymbol: (componentId: string, symbolId: string) => Promise<any>;
}
export declare const symbolApi: SymbolApi;
export type { SymbolProps, ISymbol };
export default SymbolApi;
