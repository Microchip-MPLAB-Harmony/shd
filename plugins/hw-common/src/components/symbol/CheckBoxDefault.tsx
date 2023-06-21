import { CheckboxProps } from 'primereact/checkbox';
import CheckBox from './CheckBox';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import useBooleanSymbol from '../../symbol/hook/useBooleanSymbol';
import { UpdateProps } from './util';
import { BooleanSymbol } from '../../symbol/api/BooleanSymbolApi';

function CheckBoxDefault<D>(props: SymbolProps & CheckboxProps & UpdateProps<BooleanSymbol, D>) {
  const booleanSymbolHook = useBooleanSymbol(props);
  const { componentId, symbolId, ...exceptSymbolProps } = props;

  return (
    <CheckBox
      booleanSymbolHook={booleanSymbolHook}
      {...exceptSymbolProps}
    />
  );
}

export default CheckBoxDefault;
