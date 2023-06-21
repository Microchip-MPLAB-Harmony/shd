import { SymbolProps, symbolApi } from '../api/SymbolApi';
import { useContext, useEffect, useState } from 'react';
import {
  toSymbolStateListener,
  toSymbolValueListener,
  toSymbolVisibleListener
} from '../../event/EventListenerFactory';
import { EventFilter } from '../../event/EventInterfaces';
import { EventAgentContext } from '../../txrx/EventService';
import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { createDefaultSymbol } from '../api/util';

function useSymbol({ componentId, symbolId }: SymbolProps) {
  const eventAgent = useContext(EventAgentContext);
  const [symbol, setSymbol] = useState<SymbolProps>(() => {
    const defaultSymbol = createDefaultSymbol();
    defaultSymbol.componentId = componentId;
    defaultSymbol.symbolId = symbolId;
    return defaultSymbol;
  });

  useEffect(() => {
    symbolApi.getSymbol(componentId, symbolId).then(setSymbol);
    const valueListener = toSymbolValueListener(onSymbolChanged, {
      componentId,
      symbolId
    } as EventFilter);
    const visibilityListener = toSymbolVisibleListener(onSymbolChanged, {
      componentId,
      symbolId
    } as EventFilter);
    const stateListener = toSymbolStateListener(onSymbolChanged, {
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
  }, [symbolId]);

  const onSymbolChanged = (event: any) => {
    setSymbol(event.data.symbol);
  };

  return symbol as unknown;
}

export default useSymbol;
