import { InputNumberProps, InputNumber as PrimeInputNumber } from 'primereact/inputnumber';
import { IntegerSymbolHook } from '../../symbol/hook/useIntegerSymbol';

const InputNumber = (props: InputNumberProps & { integerSymbolHook: IntegerSymbolHook }) => {
  const { symbolId, value, min, max, readOnly, visible, writeValue } = props.integerSymbolHook;
  const { integerSymbolHook, ...onlyInputNumberProps } = props;

  return !(props.hidden ?? !visible) ? (
    <PrimeInputNumber
      id={symbolId}
      showButtons
      mode='decimal'
      value={value}
      min={min}
      max={max}
      disabled={readOnly}
      onValueChange={(e) => writeValue(e.value, e.originalEvent !== null)}
      {...onlyInputNumberProps}
    />
  ) : (
    <></>
  );
};

export default InputNumber;
