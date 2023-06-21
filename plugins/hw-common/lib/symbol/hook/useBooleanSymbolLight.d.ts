import { BooleanSymbol } from '../api/BooleanSymbolApi';
declare const useBooleanSymbolLight: ({ componentId, symbolId, ...symbol }: BooleanSymbol) => BooleanSymbolHook;
export interface BooleanSymbolHook {
    componentId: string;
    symbolId: string;
    value: boolean;
    writeValue: (newValue: boolean) => void;
    visible: boolean;
    label: string;
    description: string;
    readOnly: boolean;
}
export default useBooleanSymbolLight;
