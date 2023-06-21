import { ConfigSymbol } from '../api';
declare const useSymbols: (props: {
    componentId: string;
    symbolIds: string[];
}) => {
    componentId: string;
    symbols: ConfigSymbol<any>[];
};
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
export default useSymbols;
