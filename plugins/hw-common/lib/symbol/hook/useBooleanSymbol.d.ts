import { BooleanSymbol } from '../api/BooleanSymbolApi';
import { SymbolProps } from '../api/SymbolApi';
declare const useBooleanSymbol: ({ componentId, symbolId }: SymbolProps) => BooleanSymbolHook;
export type BooleanSymbolHook = BooleanSymbol & {
    writeValue: (newValue: boolean) => void;
};
export default useBooleanSymbol;
