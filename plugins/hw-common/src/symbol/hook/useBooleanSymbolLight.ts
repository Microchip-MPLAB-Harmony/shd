import { useEffect, useRef, useState } from 'react';
import { BooleanSymbol, booleanSymbolApi } from '../api/BooleanSymbolApi';
import { useContext } from 'react';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import { toSymbolValueListener, toSymbolVisibleListener } from '../../event/EventListenerFactory';
import { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { SymbolProps } from '../api/SymbolApi';
import EventSynchronizer from '../api/EventSynchronizer';
import { EventListener } from '../../event/EventInterfaces';

interface BooleanLightProps {
  componentId: string;
  symbolId: string;
  symbolType: string;
  visible: boolean;
  label: string;
  description: string;
  readOnly: boolean;
  value: boolean;
}

const isAnyUndefined = (...values: any[]): boolean => {
  return values.some((e) => e === undefined);
};

const useBooleanSymbolLight = ({ componentId, symbolId, ...symbol }: BooleanSymbol) => {
  const eventAgent = useContext(EventAgentContext);

  const [value, setValue] = useState(symbol.value);
  const eventSynchronizer = useRef(new EventSynchronizer(symbol.value));
  const [visible] = useState(symbol.visible);
  const [label] = useState(symbol.label);
  const [description] = useState(symbol.description);
  const [readOnly] = useState(symbol.readOnly);

  const valueListenerRef = useRef<EventListener>(
    toSymbolValueListener(onSymbolValueChanged, {
      componentId,
      symbolId
    } as EventFilter)
  );

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

  function onSymbolValueChanged(event: SymbolValueChangedEvent) {
    const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
    if (result === null) {
      // accept the event value and set it in local state
      setValue(event.data.symbol.value);
    } else if (typeof result === 'boolean') {
      // use the result to trigger the DB task again.
      booleanSymbolApi.setValue(componentId, symbolId, result);
    }
  }

  const onSymbolVisualChanged = (event: SymbolValueChangedEvent) => {
    // setVisible(event.visibe);
  };

  const onSymbolStateChanged = (event: SymbolValueChangedEvent) => {
    setValue(event.value);
  };

  const registerListener = () => {
    eventAgent.addEventListener(valueListenerRef.current);
  };
  const deregisterListener = () => {
    eventAgent.removeEventListener(valueListenerRef.current);
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
    registerListener,
    deregisterListener
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

export default useBooleanSymbolLight;
