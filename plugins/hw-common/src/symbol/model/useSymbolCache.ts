import { useState } from 'react';
import { symbolUtilApi } from '../api';
import { symbolApi } from '../api';
import {
  useBooleanSymbol,
  useComboSymbol,
  useCommentSymbol,
  useIntegerSymbol,
  useKeyValueSetSymbol,
  useStringSymbol
} from '../hook';

const useSymbolCache = () => {
  const [symbols, setSymbols] = useState<any[]>([]);

  const addOneSymbol = (symbol: any) => {
    switch (symbol.symbolType) {
      case 'BooleanSymbol': {
        setSymbols((prev) => [...prev, useBooleanSymbol(symbol)]);
        break;
      }
      case 'IntegerSymbol': {
        setSymbols((prev) => [...prev, useIntegerSymbol(symbol)]);
        break;
      }
      case 'KeyValueSetSymbol': {
        setSymbols((prev) => [...prev, useKeyValueSetSymbol(symbol)]);
        break;
      }
      case 'CommentSymbol': {
        setSymbols((prev) => [...prev, useCommentSymbol(symbol)]);
        break;
      }
      case 'ComboSymbol': {
        setSymbols((prev) => [...prev, useComboSymbol(symbol)]);
        break;
      }
      case 'StringSymbol': {
        setSymbols((prev) => [...prev, useStringSymbol(symbol)]);
        break;
      }
    }
  };

  const addSymbol = (componentId: string, symbolId: string) => {
    symbolApi.getSymbol(componentId, symbolId).then(addOneSymbol);
  };

  const addSymbols = (componentId: string, symbolIds: string[]) => {
    symbolUtilApi.getSymbols(componentId, symbolIds).then((symbols: any[]) => {
      symbols.forEach(addOneSymbol);
    });
  };

  return {
    addSymbol
  };
};

export default useSymbolCache;
