import { SymbolMark } from './BooleanSymbolObservable';
declare const useSymbolObservables: () => {
    getSymbol: (componentId: string, symbolId: string) => SymbolMark;
};
export default useSymbolObservables;
