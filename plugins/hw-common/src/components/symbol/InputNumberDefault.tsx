import { InputNumberProps } from 'primereact/inputnumber';
import InputNumber from './InputNumber';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import useIntegerSymbol from '../../symbol/hook/useIntegerSymbol';

const InputNumberDefault = (props: SymbolProps & InputNumberProps) => {
  const integerSymbolHook = useIntegerSymbol(props);
  const { symbolId, componentId, ...onlyInputNumberProps } = props;

  return (
    <InputNumber
      integerSymbolHook={integerSymbolHook}
      {...onlyInputNumberProps}
    />
  );
};

export default InputNumberDefault;
