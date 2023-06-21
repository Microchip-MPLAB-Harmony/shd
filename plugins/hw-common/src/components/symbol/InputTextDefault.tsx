import { InputTextProps } from 'primereact/inputtext';
import InputText from './InputText';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import useStringSymbol from '../../symbol/hook/useStringSymbol';

const InputTextDefault = (props: SymbolProps & InputTextProps) => {
  const StringSymbolHook = useStringSymbol(props);
  const { componentId, symbolId, ...onlyDropdownProps } = props;

  return (
    <InputText
      stringSymbolHook={StringSymbolHook}
      {...onlyDropdownProps}
    />
  );
};

export default InputTextDefault;
