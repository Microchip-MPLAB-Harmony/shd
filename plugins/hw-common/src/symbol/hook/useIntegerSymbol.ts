import { useEffect, useRef, useState } from 'react';
import { useContext } from 'react';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import { toSymbolValueListener, toSymbolVisibleListener } from '../../event/EventListenerFactory';
import { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { error, log } from '@mplab_harmony/harmony-plugin-core-service';
import { SymbolProps } from '../api/SymbolApi';
import { integerSymbolApi } from '../api/IntegerSymbolApi';
import EventSynchronizer from '../api/EventSynchronizer';

const useIntegerSymbol = ({ componentId, symbolId }: SymbolProps) => {
  const eventAgent = useContext(EventAgentContext);

  const [value, setValue] = useState(0);
  const eventSynchronizer = useRef(new EventSynchronizer(value));
  const [min, setMin] = useState(0);
  const [max, setMax] = useState(0);
  const [visible, setVisible] = useState(false);
  const [label, setLabel] = useState('');
  const [description, setDescription] = useState('');
  const [readOnly, setReadOnly] = useState(false);

  useEffect(() => {
    initFromDB();
    const valueListener = toSymbolValueListener(onSymbolValueChanged, {
      componentId,
      symbolId
    } as EventFilter);

    eventAgent.addEventListener(valueListener);

    return () => {
      eventAgent.removeEventListener(valueListener);
    };
  }, []);

  const initFromDB = () => {
    integerSymbolApi
      .getIntegerSymbol(componentId, symbolId)
      .then(({ value, min, max, visible, label, description, readOnly }) => {
        setValue(value);
        setMin(min);
        setMax(max);
        setVisible(visible);
        setLabel(label);
        setDescription(description);
        setReadOnly(readOnly);
      });
  };

  const writeValue = (newValue: number | null, isOriginalEvent?: boolean) => {
    if (newValue === null || newValue === value) {
      return;
    }

    // Workaround for PrimeReact issue:
    // PrimeReact InputNumber is calling onValueChange function initially with value zero.
    // Though we can ignore this event, the text box still contains zero.
    // So we accept the zero and reload the value from DB
    if (newValue === 0 && isOriginalEvent === false) {
      eventSynchronizer.current.valueBackup = newValue;
      setValue(newValue);
      setTimeout(() => integerSymbolApi.getValue(componentId, symbolId).then(setValue));
      return;
    }
    eventSynchronizer.current.valueBackup = newValue;
    setValue(newValue);
    const result = eventSynchronizer.current.processUiEvent(newValue);
    if (typeof result === 'number') {
      // use the result to trigger the DB task.
      integerSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
    const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
    if (result === null) {
      // accept the event value and set it in local state
      setValue(event.data.symbol.value);
    } else if (typeof result === 'number') {
      // use the result to trigger the DB task again.
      integerSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolVisualChanged = (event: SymbolValueChangedEvent) => {
    // setVisible(event.visibe);
  };

  const onSymbolStateChanged = (event: SymbolValueChangedEvent) => {
    setValue(event.value);
  };

  return {
    value,
    min,
    max,
    writeValue,
    visible,
    label,
    description,
    readOnly
  } as IntegerSymbolHook;
};

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
