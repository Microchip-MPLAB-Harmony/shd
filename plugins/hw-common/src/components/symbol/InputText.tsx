import { InputTextProps, InputText as PrimeInputText } from 'primereact/inputtext';
import { StringSymbolHook } from '../../symbol/hook/useStringSymbol';

const InputText = (props: InputTextProps & { stringSymbolHook: StringSymbolHook }) => {
  const { symbolId, value, readOnly, visible, writeValue } = props.stringSymbolHook;
  const { stringSymbolHook, ...onlyInputTextProps } = props;

  return !(props.hidden ?? !visible) ? (
    <PrimeInputText
      id={symbolId}
      value={value}
      disabled={readOnly}
      onChange={(e) => writeValue(e.target.value)}
      {...onlyInputTextProps}
    />
  ) : (
    <></>
  );
};

export default InputText;
