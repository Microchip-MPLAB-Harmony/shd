import { SymbolProps } from '../api/SymbolApi';
declare const useIntegerSymbol: ({ componentId, symbolId }: SymbolProps) => IntegerSymbolHook;
export interface IntegerSymbolHook {
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
export default useIntegerSymbol;
