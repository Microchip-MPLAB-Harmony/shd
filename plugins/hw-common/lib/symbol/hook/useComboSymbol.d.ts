import { SymbolProps } from '../api/SymbolApi';
declare const useComboSymbol: ({ componentId, symbolId }: SymbolProps) => ComboSymbolHook;
export interface ComboSymbolHook {
    componentId: string;
    symbolId: string;
    value: string;
    writeValue: (newValue: string) => void;
    visible: boolean;
    label: string;
    description: string;
    readOnly: boolean;
    options: string[];
}
export default useComboSymbol;
