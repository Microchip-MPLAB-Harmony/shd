import { CheckboxProps, Checkbox as PrimeCheckBox } from 'primereact/checkbox';
import { BooleanSymbolHook } from '../../symbol/hook/useBooleanSymbol';
import { useEffect } from 'react';
import { BooleanSymbol } from '../../symbol/api';
import { UpdateProps } from './util';

function CheckBox<D>(
  props: CheckboxProps & { booleanSymbolHook: BooleanSymbolHook } & UpdateProps<BooleanSymbol, D>
) {
  const { value, readOnly, visible, writeValue } = props.booleanSymbolHook;
  const { booleanSymbolHook, onStateUpdate, userData, ...onlyCheckBoxProps } = props;

  useEffect(() => {
    onStateUpdate?.(booleanSymbolHook as BooleanSymbol, userData);
  }, [booleanSymbolHook.value]);

  return !(props.hidden ?? !visible) ? (
    <PrimeCheckBox
      inputId='binary'
      checked={value}
      disabled={readOnly}
      onChange={(e) => writeValue(e.checked)}
      {...onlyCheckBoxProps}
    />
  ) : (
    <></>
  );
}

export default CheckBox;
