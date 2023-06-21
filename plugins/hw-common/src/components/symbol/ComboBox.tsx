import { DropdownProps, Dropdown as PrimeDropDown } from 'primereact/dropdown';
import { ComboSymbolHook } from '../../symbol/hook/useComboSymbol';

const ComboBox = (props: DropdownProps & { comboSymbolHook: ComboSymbolHook }) => {
  const { symbolId, value, options, readOnly, visible, writeValue } = props.comboSymbolHook;
  const { comboSymbolHook, ...onlyDropdownProps } = props;

  return !(props.hidden ?? !visible) ? (
    <PrimeDropDown
      value={value}
      options={options}
      disabled={readOnly}
      onChange={(e) => writeValue(e.value)}
      {...onlyDropdownProps}
    />
  ) : (
    <></>
  );
};

export default ComboBox;
