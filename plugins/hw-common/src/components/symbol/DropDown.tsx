import { DropdownProps, Dropdown as PrimeDropDown } from 'primereact/dropdown';
import { KeyValueSetSymbolHook } from '../../symbol/hook/useKeyValueSetSymbol';

const DropDown = (props: DropdownProps & { keyValueSetSymbolHook: KeyValueSetSymbolHook }) => {
  const { symbolId, selectedOption, options, readOnly, visible, writeValue } =
    props.keyValueSetSymbolHook;
  const { keyValueSetSymbolHook, ...onlyDropdownProps } = props;

  return !(props.hidden ?? !visible) ? (
    <PrimeDropDown
      value={selectedOption}
      options={options}
      disabled={readOnly}
      onChange={(e) => writeValue(e.value)}
      {...onlyDropdownProps}
    />
  ) : (
    <></>
  );
};

export default DropDown;
