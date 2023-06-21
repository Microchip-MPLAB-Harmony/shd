import SymbolApi, { ISymbol } from './SymbolApi';
interface VisibleSymbol extends ISymbol {
    visible: boolean;
}
declare class VisibleSymbolApi extends SymbolApi {
    readonly path: string;
    constructor(path?: string);
    getVisible: (componentId: string, symbolId: string) => Promise<boolean>;
}
export type { VisibleSymbol };
export declare const visibleSymbolApi: VisibleSymbolApi;
export default VisibleSymbolApi;
