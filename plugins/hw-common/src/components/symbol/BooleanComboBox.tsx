import { DropdownProps, Dropdown as PrimeDropDown } from 'primereact/dropdown';
import { BooleanSymbolHook } from '../../symbol/hook/useBooleanSymbol';

const BooleanComboBox = (
  props: DropdownProps & { booleanSymbolHook: BooleanSymbolHook } & {
    trueOption: string;
    falseOption: string;
  }
) => {
  const { symbolId, value, readOnly, visible, writeValue } = props.booleanSymbolHook;
  const { booleanSymbolHook, trueOption, falseOption, ...onlyDropdownProps } = props;

  return !(props.hidden ?? !visible) ? (
    <PrimeDropDown
      value={value === true ? trueOption : falseOption}
      options={[trueOption, falseOption]}
      disabled={readOnly}
      onChange={(e) => writeValue(e.value === trueOption ? true : false)}
      {...onlyDropdownProps}
    />
  ) : (
    <></>
  );
};

export default BooleanComboBox;
