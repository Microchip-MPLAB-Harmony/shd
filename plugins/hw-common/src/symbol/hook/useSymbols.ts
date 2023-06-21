import { ISymbol } from '../../symbol/api/SymbolApi';
import { useContext, useEffect, useState } from 'react';
import { symbolUtilApi } from '../../symbol/api';
import {
  toSymbolStateListener,
  toSymbolValueListener,
  toSymbolVisibleListener
} from '../../event/EventListenerFactory';
import { EventFilter } from '../../event/EventInterfaces';
import { EventAgentContext } from '../../txrx/EventService';

function useSymbols({ componentId, symbolIds }: { componentId: string; symbolIds: string[] }) {
  const eventAgent = useContext(EventAgentContext);
  const [symbols, setSymbols] = useState<ISymbol[]>([]);

  useEffect(() => {
    symbolUtilApi.getSymbols(componentId, symbolIds).then(setSymbols);

    const valueListeners = symbolIds.map((symbolId) =>
      toSymbolValueListener(onSymbolChanged, {
        componentId,
        symbolId
      } as EventFilter)
    );
    const visibilityListeners = symbolIds.map((symbolId) =>
      toSymbolVisibleListener(onSymbolChanged, {
        componentId,
        symbolId
      } as EventFilter)
    );
    const stateListeners = symbolIds.map((symbolId) =>
      toSymbolStateListener(onSymbolChanged, {
        componentId,
        symbolId
      } as EventFilter)
    );
    valueListeners.map((listener) => eventAgent.addEventListener(listener));
    visibilityListeners.map((listener) => eventAgent.addEventListener(listener));
    stateListeners.map((listener) => eventAgent.addEventListener(listener));
    return () => {
      valueListeners.map((listener) => eventAgent.removeEventListener(listener));
      visibilityListeners.map((listener) => eventAgent.removeEventListener(listener));
      stateListeners.map((listener) => eventAgent.removeEventListener(listener));
    };
  }, [symbolIds]);

  const onSymbolChanged = (event: any) => {
    const newSymbol = event.data.symbol;
    setSymbols((symbols) =>
      symbols.map((symbol) => (symbol.symbolId === newSymbol.symbolId ? newSymbol : symbol))
    );
  };

  return symbols as unknown[];
}

export default useSymbols;
