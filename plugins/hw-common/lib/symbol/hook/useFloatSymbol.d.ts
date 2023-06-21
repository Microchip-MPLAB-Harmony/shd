import { SymbolProps } from '../api/SymbolApi';
declare const useFloatSymbol: ({ componentId, symbolId }: SymbolProps) => FloatSymbolHook;
export interface FloatSymbolHook {
    componentId: string;
    symbolId: string;
    value: number;
    min: number;
    max: number;
    writeValue: (newValue: number | null, isOriginalEvent?: boolean) => void;
    visible: boolean;
    label: string;
    description: string;
    readOnly: boolean;
}
export default useFloatSymbol;
