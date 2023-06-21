import { CheckboxProps, Checkbox as PrimeCheckBox } from 'primereact/checkbox';
import { KeyValueSetSymbolHook } from '../../symbol/hook/useKeyValueSetSymbol';

const KeyValueSetCheckBox = (
  props: CheckboxProps & { keyValueSetSymbolHook: KeyValueSetSymbolHook } & {
    trueOption: string;
    falseOption: string;
  }
) => {
  const { symbolId, selectedOption, readOnly, visible, writeValue } = props.keyValueSetSymbolHook;
  const { keyValueSetSymbolHook, trueOption, falseOption, ...onlyCheckBoxProps } = props;

  return !(props.hidden ?? !visible) ? (
    <PrimeCheckBox
      id={symbolId}
      inputId='binary'
      checked={selectedOption === trueOption}
      disabled={readOnly}
      onChange={(e) => writeValue(e.checked ? trueOption : falseOption)}
      {...onlyCheckBoxProps}
    />
  ) : (
    <></>
  );
};

export default KeyValueSetCheckBox;
