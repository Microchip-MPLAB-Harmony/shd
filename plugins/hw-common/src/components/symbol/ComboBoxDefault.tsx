import { DropdownProps } from 'primereact/dropdown';
import ComboBox from './ComboBox';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import useComboSymbol from '../../symbol/hook/useComboSymbol';

const ComboBoxDefault = (props: SymbolProps & DropdownProps) => {
  const comboSymbolHook = useComboSymbol(props);
  const { componentId, symbolId, ...onlyDropdownProps } = props;

  return (
    <ComboBox
      comboSymbolHook={comboSymbolHook}
      {...onlyDropdownProps}
    />
  );
};

export default ComboBoxDefault;
