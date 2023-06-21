import { useEffect, useRef, useState } from 'react';
import { useContext } from 'react';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import {
  toSymbolValueListener,
  toSymbolVisibleListener,
  toSymbolStateListener
} from '../../event/EventListenerFactory';
import { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { SymbolProps } from '../api/SymbolApi';
import { comboSymbolApi } from '../api/ComboSymbolApi';
import EventSynchronizer from '../api/EventSynchronizer';
import { Response } from '../../txrx/Transceiver';

const useComboSymbol = ({ componentId, symbolId }: SymbolProps) => {
  const eventAgent = useContext(EventAgentContext);

  const [value, setValue] = useState('');
  const eventSynchronizer = useRef(new EventSynchronizer(value));

  const [visible, setVisible] = useState(false);
  const [label, setLabel] = useState('');
  const [description, setDescription] = useState('');
  const [readOnly, setReadOnly] = useState(false);

  const [options, setOptions] = useState<string[]>([]);

  useEffect(() => {
    initFromDB();
    const valueListener = toSymbolValueListener(onSymbolValueChanged, {
      componentId,
      symbolId
    } as EventFilter);
    const visibilityListener = toSymbolVisibleListener(onSymbolVisualChanged, {
      componentId,
      symbolId
    } as EventFilter);
    const stateListener = toSymbolStateListener(onSymbolStateChanged, {
      componentId,
      symbolId
    } as EventFilter);

    eventAgent.addEventListener(valueListener);
    eventAgent.addEventListener(visibilityListener);
    eventAgent.addEventListener(stateListener);

    return () => {
      eventAgent.removeEventListener(valueListener);
      eventAgent.removeEventListener(visibilityListener);
      eventAgent.removeEventListener(stateListener);
    };
  }, []);

  const initFromDB = () => {
    comboSymbolApi.getComboSymbol(componentId, symbolId).then((symbol) => {
      setValue(symbol.value);
      setVisible(symbol.visible);
      setLabel(symbol.label);
      setDescription(symbol.description);
      setReadOnly(symbol.readOnly);
      setOptions(symbol.options);
    });
  };

  const writeValue = (newValue: string) => {
    eventSynchronizer.current.valueBackup = newValue;
    setValue(newValue);
    const result = eventSynchronizer.current.processUiEvent(newValue);
    if (typeof result === 'string') {
      // use the result to trigger the DB task.
      comboSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
    const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
    if (result === null) {
      // accept the event value and set it in local state
      setValue(event.data.symbol.value);
    } else if (typeof result === 'string') {
      // use the result to trigger the DB task again.
      comboSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolVisualChanged = (event: Response) => {
    setVisible(event.data.symbol.visible);
  };

  const onSymbolStateChanged = (event: Response) => {
    setValue(event.data.symbol.value); // State means display type and others.
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
    options
  } as ComboSymbolHook;
};

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
