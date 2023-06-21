import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { EventFilter, EventListener } from '../../event/EventInterfaces';
import { toSymbolValueListener } from '../../event/EventListenerFactory';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import { EventAgent } from '../../txrx';
import EventSynchronizer from '../api/EventSynchronizer';
import { booleanSymbolApi } from '../api/BooleanSymbolApi';

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

class BooleanSymbolViewModel {
  private valueListener: EventListener;
  private eventSynchronizer: EventSynchronizer<boolean>;

  constructor(
    private _eventAgent: EventAgent,
    private _componentId: string,
    private _symbolId: string,
    private _symbolType: string,
    private _visible: boolean,
    private _label: string,
    private _description: string,
    private _readOnly: boolean,
    private _value: boolean
  ) {
    this.eventSynchronizer = new EventSynchronizer(_value);

    this.valueListener = toSymbolValueListener(this.onSymbolValueChanged, {
      _componentId,
      _symbolId
    } as EventFilter);

    _eventAgent.addEventListener(this.valueListener);
  }

  destroy() {
    this._eventAgent.removeEventListener(this.valueListener);
  }

  get componentId(): string {
    return this._componentId;
  }

  get symbolId(): string {
    return this._symbolId;
  }

  get symbolType(): string {
    return this._symbolType;
  }

  get visible(): boolean {
    return this._visible;
  }

  get label(): string {
    return this._label;
  }

  get description(): string {
    return this._description;
  }

  get value(): boolean {
    return this._value;
  }

  get readOnly(): boolean {
    return this._readOnly;
  }

  onSymbolValueChanged(event: SymbolValueChangedEvent) {
    const result = this.eventSynchronizer.processDBEvent(event.data.symbol.value);
    if (result === null) {
      // accept the event value and set it in local state
      this._value = event.data.symbol.value;
    } else if (typeof result === 'boolean') {
      // use the result to trigger the DB task again.
      booleanSymbolApi.setValue(this._componentId, this._symbolId, result);
    }
  }

  registerValueChangedListener() {
    return null;
  }
}

export type { BooleanSymbolModel, BooleanSymbolViewModel };
