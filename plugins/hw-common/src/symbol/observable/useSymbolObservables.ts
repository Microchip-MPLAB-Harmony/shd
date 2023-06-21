import { createContext, useEffect, useRef, useState } from 'react';
import { ISymbol } from '../api';
import { BooleanSymbolObservable, SymbolMark } from './BooleanSymbolObservable';
import { EventAgent } from '../../txrx';

const useSymbolObservables = () => {
  const [symbols, setSymbols] = useState<SymbolMark[]>([]);

  const reff = useRef(new EventAgent());

  useEffect(() => {
    return () => {
      reff.current.destroy();
    };
  }, []);

  const getSymbol = (componentId: string, symbolId: string) => {
    let symbol = symbols.find((e) => e.symbolId == symbolId);

    if (!symbol) {
      symbol = new BooleanSymbolObservable(componentId, symbolId, reff.current) as SymbolMark;

      setSymbols([...symbols, symbol]);
    }

    return symbol;
  };

  return { getSymbol };
};

export default useSymbolObservables;

createContext({});
