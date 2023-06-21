import { useEffect, useMemo, useRef, useState } from 'react';
import { useContext } from 'react';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import {
  toSymbolValueListener,
  toSymbolVisibleListener,
  toSymbolStateListener
} from '../../event/EventListenerFactory';
import { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { error, log } from '@mplab_harmony/harmony-plugin-core-service';
import { SymbolProps } from '../api/SymbolApi';
import { DisplayMode, keyValueSetSymbolApi, OptionPair } from '../api/KeyValueSetSymbolApi';
import EventSynchronizer from '../api/EventSynchronizer';
import { Response } from '../../txrx/Transceiver';

const useKeyValueSetSymbol = ({ componentId, symbolId }: SymbolProps) => {
  const eventAgent = useContext(EventAgentContext);

  const [value, setValue] = useState(0);
  const eventSynchronizer = useRef(new EventSynchronizer(value));

  const [visible, setVisible] = useState(false);
  const [label, setLabel] = useState('');
  const [description, setDescription] = useState('');
  const [readOnly, setReadOnly] = useState(false);

  const [optionPairs, setOptionPairs] = useState<OptionPair[]>([]);
  const [selectedOptionPair, setSelectedOptionPair] = useState<OptionPair | undefined>(undefined);
  const [displayMode, setDisplayMode] = useState<DisplayMode>(DisplayMode.Key);

  const [options, setOptions] = useState<string[]>([]);
  const [selectedOption, setSelectedOption] = useState<string>('');

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

  useEffect(() => {
    setSelectedOptionPair(optionPairs.at(value));
  }, [value, optionPairs]);

  useEffect(() => {
    const getDisplayString = (pair: OptionPair) => {
      switch (displayMode) {
        case DisplayMode.Key:
          return pair.key;
        case DisplayMode.Value:
          return pair.value;
        case DisplayMode.Description:
          return pair.description;
      }
    };

    setOptions(optionPairs.map((e) => getDisplayString(e)) ?? []);
    setSelectedOption(selectedOptionPair ? getDisplayString(selectedOptionPair) : '');
  }, [displayMode, optionPairs, selectedOptionPair, value]);

  const initFromDB = () => {
    keyValueSetSymbolApi.getKeyValueSetSymbol(componentId, symbolId).then((symbol) => {
      setValue(symbol.value);
      setVisible(symbol.visible);
      setLabel(symbol.label);
      setDescription(symbol.description);
      setReadOnly(symbol.readOnly);
      setOptionPairs(symbol.optionPairs);
      setDisplayMode(symbol.displayMode);
      setSelectedOptionPair(symbol.selectedOptionPair);
    });
  };

  const getDisplayString = (pair: OptionPair) => {
    switch (displayMode) {
      case DisplayMode.Key:
        return pair.key;
      case DisplayMode.Value:
        return pair.value;
      case DisplayMode.Description:
        return pair.description;
    }
  };

  const displayStringToValue = (displayString: string) => {
    return optionPairs.map((e) => getDisplayString(e)).indexOf(displayString);
  };

  const valueToDisplayString = (value: number) => {
    return getDisplayString(optionPairs.at(value) || optionPairs[0]);
  };

  const writeValue = (newValue: string) => {
    const temp = displayStringToValue(newValue);

    if (temp === value) {
      return;
    }

    eventSynchronizer.current.valueBackup = temp;
    setValue(temp);
    const result = eventSynchronizer.current.processUiEvent(temp);
    if (typeof result === 'number') {
      // use the result to trigger the DB task.
      keyValueSetSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
    const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
    if (result === null) {
      // accept the event value and set it in local state
      setValue(event.data.symbol.value);
    } else if (typeof result === 'number') {
      // use the result to trigger the DB task again.
      keyValueSetSymbolApi.setValue(componentId, symbolId, result);
    }
  };

  const onSymbolVisualChanged = (event: Response) => {
    setVisible(event.data.symbol.visible);
  };

  const onSymbolStateChanged = (event: Response) => {
    setValue(event.data.symbol.value); // State means display type and others.
    setDisplayMode(event.data.symbol.displayMode);
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
    optionPairs,
    options,
    selectedOptionPair,
    selectedOption,
    displayMode
  } as KeyValueSetSymbolHook;
};

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
