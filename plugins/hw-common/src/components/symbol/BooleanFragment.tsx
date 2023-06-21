import { SymbolProps } from '../../symbol/api/SymbolApi';
import useBooleanSymbol from '../../symbol/hook/useBooleanSymbol';
import { UpdateProps } from './util';
import { BooleanSymbol } from '../../symbol/api/BooleanSymbolApi';
import { useEffect } from 'react';

function BooleanFragment<D>(props: SymbolProps & UpdateProps<BooleanSymbol, D>) {
  const booleanSymbolHook = useBooleanSymbol(props);
  const { onStateUpdate, userData } = props;

  useEffect(() => {
    onStateUpdate?.(booleanSymbolHook as BooleanSymbol, userData);
  }, [booleanSymbolHook.value]);

  return <></>;
}

export default BooleanFragment;
