import { SymbolProps } from '../api/SymbolApi';
declare const useStringSymbol: ({ componentId, symbolId }: SymbolProps) => StringSymbolHook;
export interface StringSymbolHook {
    componentId: string;
    symbolId: string;
    value: string;
    writeValue: (newValue: string) => void;
    visible: boolean;
    label: string;
    description: string;
    readOnly: boolean;
}
export default useStringSymbol;
