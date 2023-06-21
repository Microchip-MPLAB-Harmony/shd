import { useEffect, useRef, useState } from 'react';
import { BooleanSymbol, booleanSymbolApi } from '../api/BooleanSymbolApi';
import { useContext } from 'react';
import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
import { toSymbolValueListener, toSymbolVisibleListener } from '../../event/EventListenerFactory';
import { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { ISymbol, SymbolProps } from '../api/SymbolApi';
import EventSynchronizer from '../api/EventSynchronizer';
import { symbolUtilApi } from '../api/SymbolUtilApi';
import {
  IntegerSymbol,
  KeyValueSetSymbol,
  CommentSymbol,
  ComboSymbol,
  StringSymbol,
  ConfigSymbol
} from '../api';
import useBooleanSymbol from './useBooleanSymbol';

const useGetSymbolAsType = (symbol: ISymbol) => {
  const { componentId, symbolId } = symbol;
  const { symbolType } = symbol;
  switch (symbolType) {
    case 'BooleanSymbol': {
      return useBooleanSymbol(symbol);
    }
    case 'IntegerSymbol': {
      return symbol as IntegerSymbol;
    }
    case 'KeyValueSetSymbol': {
      return symbol as KeyValueSetSymbol;
    }
    case 'CommentSymbol': {
      return symbol as CommentSymbol;
    }
    case 'ComboSymbol': {
      return symbol as ComboSymbol;
    }
    case 'StringSymbol': {
      return symbol as StringSymbol;
    }
    default:
      throw new Error('symbol type is not supported!');
  }
};

const useSymbols = (props: { componentId: string; symbolIds: string[] }) => {
  const { componentId, symbolIds } = props;
  const eventAgent = useContext(EventAgentContext);

  const [symbols, setSymbols] = useState<ConfigSymbol<any>[]>([]);

  const symbolHooks = Array.from(symbolIds, (symbol, index) => ({
    symbol,
    hook: useBooleanSymbol({ componentId, symbolId: symbol }) // Call your custom input hook
  }));

  // const [value, setValue] = useState(false);
  // const eventSynchronizer = useRef(new EventSynchronizer(value));
  // const [visible, setVisible] = useState(false);
  // const [label, setLabel] = useState('');
  // const [description, setDescription] = useState('');
  // const [readOnly, setReadOnly] = useState(false);

  useEffect(() => {
    initFromDB();

    const valueListener = toSymbolValueListener(onSymbolValueChanged);
    eventAgent.addEventListener(valueListener);
    return () => {
      eventAgent.removeEventListener(valueListener);
    };
  }, []);

  const initFromDB = () => {
    symbolUtilApi.getSymbols(componentId, symbolIds).then(setSymbols);
  };

  // const writeValue = (symbolId: string, newValue: boolean) => {
  //   if (newValue === value) {
  //     return;
  //   }

  //   eventSynchronizer.current.valueBackup = newValue;
  //   setValue(newValue);
  //   const result = eventSynchronizer.current.processUiEvent(newValue);
  //   if (typeof result === 'boolean') {
  //     // use the result to trigger the DB task.
  //     booleanSymbolApi.setValue(componentId, symbolId, result);
  //   }
  // };

  // const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
  //   event.data.symbol
  //   const result = eventSynchronizer.current.processDBEvent(
  //     event.data.symbol.value
  //   );
  //   if (result === null) {
  //     // accept the event value and set it in local state
  //     setValue(event.data.symbol.value);
  //   } else if (typeof result === 'boolean') {
  //     // use the result to trigger the DB task again.
  //     booleanSymbolApi.setValue(componentId, symbolId, result);
  //   }
  // };

  const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
    const { componentId, symbolId, value } = event.data.symbol;
    const foundSymbol = symbols.find((e) => e.componentId == componentId && e.symbolId == symbolId);

    symbols.map((e) =>
      e.componentId == componentId && e.symbolId == symbolId ? (e.value = value) : e
    );
  };

  const onSymbolVisualChanged = (event: SymbolValueChangedEvent) => {
    // setVisible(event.visibe);
  };

  const onSymbolStateChanged = (event: SymbolValueChangedEvent) => {
    // setValue(event.value);
  };

  return {
    componentId,
    symbols
  };
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
