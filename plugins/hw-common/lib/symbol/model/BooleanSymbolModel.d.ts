import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import { EventAgent } from '../../txrx';
interface BooleanSymbolModel {
    componentId: string;
    symbolId: string;
    symbolType: string;
    visible: boolean;
    label: string;
    description: string;
    readOnly: boolean;
    value: boolean;
}
declare class BooleanSymbolViewModel {
    private _eventAgent;
    private _componentId;
    private _symbolId;
    private _symbolType;
    private _visible;
    private _label;
    private _description;
    private _readOnly;
    private _value;
    private valueListener;
    private eventSynchronizer;
    constructor(_eventAgent: EventAgent, _componentId: string, _symbolId: string, _symbolType: string, _visible: boolean, _label: string, _description: string, _readOnly: boolean, _value: boolean);
    destroy(): void;
    get componentId(): string;
    get symbolId(): string;
    get symbolType(): string;
    get visible(): boolean;
    get label(): string;
    get description(): string;
    get value(): boolean;
    get readOnly(): boolean;
    onSymbolValueChanged(event: SymbolValueChangedEvent): void;
    registerValueChangedListener(): null;
}
export type { BooleanSymbolModel, BooleanSymbolViewModel };
