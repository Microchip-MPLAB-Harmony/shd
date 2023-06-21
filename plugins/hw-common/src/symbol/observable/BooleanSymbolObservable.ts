import { useEffect, useRef, useState } from 'react';
import { useContext } from 'react';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import { toSymbolValueListener } from '../../event/EventListenerFactory';
import EventAgent, { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { SymbolProps } from '../api/SymbolApi';
import EventSynchronizer from '../api/EventSynchronizer';
import { booleanSymbolApi } from '../api/BooleanSymbolApi';

interface SymbolMark {
  readonly componentId: string;
  readonly symbolId: string;
  readonly symbolType: string;
}

class BooleanSymbolObservable implements SymbolMark {
  private _symbolType: string = '';
  private value: boolean = false;
  private visible: boolean = false;
  private label: string = '';
  private description: string = '';
  private readOnly: boolean = false;

  private eventSynchronizer: EventSynchronizer<boolean> | undefined = undefined;

  private valueListener;

  constructor(
    private readonly _componentId: string,
    private readonly _symbolId: string,
    private readonly eventAgent: EventAgent
  ) {
    booleanSymbolApi
      .getBooleanSymbol(this._componentId, this._symbolId)
      .then(({ value, visible, label, description, readOnly }) => {
        this.value = value;
        this.eventSynchronizer = new EventSynchronizer(value);
        this.visible = visible;
        this.label = label;
        this.description = description;
        this.readOnly = readOnly;
      });

    this.valueListener = toSymbolValueListener(this.onSymbolValueChanged, {
      componentId: _componentId,
      symbolId: _symbolId,
    } as EventFilter);
    eventAgent.addEventListener(this.valueListener);
  }

  destroy() {
    this.eventAgent.removeEventListener(this.valueListener);
  }

  writeValue(newValue: boolean) {
    if (newValue === this.value) {
      return;
    }

    if (this.eventSynchronizer != null) {
      this.eventSynchronizer.valueBackup = newValue;
    }
    this.value = newValue;
    const result = this.eventSynchronizer?.processUiEvent(newValue);
    if (typeof result === 'boolean') {
      // use the result to trigger the DB task.
      booleanSymbolApi.setValue(this._componentId, this._symbolId, result);
    }
  }

  onSymbolValueChanged(event: SymbolValueChangedEvent) {
    const result = this.eventSynchronizer?.processDBEvent(
      event.data.symbol.value
    );
    if (result === null) {
      // accept the event value and set it in local state
      this.value = event.data.symbol.value;
    } else if (typeof result === 'boolean') {
      // use the result to trigger the DB task again.
      booleanSymbolApi.setValue(this._componentId, this._symbolId, result);
    }
  }

  onSymbolVisualChanged(event: SymbolValueChangedEvent) {
    // setVisible(event.visibe);
  }

  onSymbolStateChanged(event: SymbolValueChangedEvent) {
    this.value = event.value;
  }

  get _value() {
    return this.value;
  }

  get componentId() {
    return this._componentId;
  }

  get symbolId() {
    return this._symbolId;
  }
  get symbolType() {
    return this._symbolType;
  }
}

const useBooleanSymbol = ({ componentId, symbolId }: SymbolProps) => {
  const eventAgent = useContext(EventAgentContext);

  const [value, setValue] = useState(false);
  const eventSynchronizer = useRef(new EventSynchronizer(value));
  const [visible, setVisible] = useState(false);
  const [label, setLabel] = useState('');
  const [description, setDescription] = useState('');
  const [readOnly, setReadOnly] = useState(false);

  useEffect(() => {
    initFromDB();

    const valueListener = toSymbolValueListener(onSymbolValueChanged, {
      componentId,
      symbolId,
    } as EventFilter);
    eventAgent.addEventListener(valueListener);
    return () => {
      eventAgent.removeEventListener(valueListener);
    };
  }, []);

  const initFromDB = () => {
    booleanSymbolApi
      .getBooleanSymbol(componentId, symbolId)
      .then(({ value, visible, label, description, readOnly }) => {
        setValue(value);
        setVisible(visible);
        setLabel(label);
        setDescription(description);
        setReadOnly(readOnly);
      });
  };

  const writeValue = (newValue: boolean) => {
    if (newValue === value) {
      return;
    }

    eventSynchronizer.current.valueBackup = newValue;
    setValue(newValue);
    const result = eventSynchronizer.current.processUiEvent(newValue);
    if (typeof result === 'boolean') {
      // use the result to trigger the DB task.
      booleanSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
    const result = eventSynchronizer.current.processDBEvent(
      event.data.symbol.value
    );
    if (result === null) {
      // accept the event value and set it in local state
      setValue(event.data.symbol.value);
    } else if (typeof result === 'boolean') {
      // use the result to trigger the DB task again.
      booleanSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolVisualChanged = (event: SymbolValueChangedEvent) => {
    // setVisible(event.visibe);
  };

  const onSymbolStateChanged = (event: SymbolValueChangedEvent) => {
    setValue(event.value);
  };

  return {
    componentId,
    symbolId,
    value,
    writeValue,
    visible,
    label,
    description,
    readOnly,
  } as BooleanSymbolHook;
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

export default useBooleanSymbol;

export { BooleanSymbolObservable };

export type { SymbolMark };
