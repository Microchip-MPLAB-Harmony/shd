import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import EventAgent from '../../txrx/EventService';
import { SymbolProps } from '../api/SymbolApi';
interface SymbolMark {
    readonly componentId: string;
    readonly symbolId: string;
    readonly symbolType: string;
}
declare class BooleanSymbolObservable implements SymbolMark {
    private readonly _componentId;
    private readonly _symbolId;
    private readonly eventAgent;
    private _symbolType;
    private value;
    private visible;
    private label;
    private description;
    private readOnly;
    private eventSynchronizer;
    private valueListener;
    constructor(_componentId: string, _symbolId: string, eventAgent: EventAgent);
    destroy(): void;
    writeValue(newValue: boolean): void;
    onSymbolValueChanged(event: SymbolValueChangedEvent): void;
    onSymbolVisualChanged(event: SymbolValueChangedEvent): void;
    onSymbolStateChanged(event: SymbolValueChangedEvent): void;
    get _value(): boolean;
    get componentId(): string;
    get symbolId(): string;
    get symbolType(): string;
}
declare const useBooleanSymbol: ({ componentId, symbolId }: SymbolProps) => BooleanSymbolHook;
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
export default useBooleanSymbol;
export { BooleanSymbolObservable };
export type { SymbolMark };
