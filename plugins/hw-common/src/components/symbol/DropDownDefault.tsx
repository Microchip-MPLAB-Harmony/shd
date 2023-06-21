import { DropdownProps } from 'primereact/dropdown';
import DropDown from './DropDown';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import useKeyValueSetSymbol from '../../symbol/hook/useKeyValueSetSymbol';

const DropDownDefault = (props: SymbolProps & DropdownProps) => {
  const keyValueSetSymbolHook = useKeyValueSetSymbol(props);
  const { componentId, symbolId, ...onlyDropdownProps } = props;

  return (
    <DropDown
      keyValueSetSymbolHook={keyValueSetSymbolHook}
      {...onlyDropdownProps}
    />
  );
};

export default DropDownDefault;
