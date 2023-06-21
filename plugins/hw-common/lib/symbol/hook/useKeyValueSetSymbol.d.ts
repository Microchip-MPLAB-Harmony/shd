import { SymbolProps } from '../api/SymbolApi';
import { DisplayMode, OptionPair } from '../api/KeyValueSetSymbolApi';
declare const useKeyValueSetSymbol: ({ componentId, symbolId }: SymbolProps) => KeyValueSetSymbolHook;
export interface KeyValueSetSymbolHook {
    componentId: string;
    symbolId: string;
    value: number;
    writeValue: (newValue: string) => void;
    visible: boolean;
    label: string;
    description: string;
    readOnly: boolean;
    optionPairs: OptionPair[];
    options: string[];
    selectedOptionPair: OptionPair | undefined;
    selectedOption: string;
    displayMode: DisplayMode;
}
export default useKeyValueSetSymbol;
