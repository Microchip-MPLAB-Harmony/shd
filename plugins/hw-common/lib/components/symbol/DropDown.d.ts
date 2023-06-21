import { DropdownProps } from 'primereact/dropdown';
import { KeyValueSetSymbolHook } from '../../symbol/hook/useKeyValueSetSymbol';
declare const DropDown: (props: DropdownProps & {
    keyValueSetSymbolHook: KeyValueSetSymbolHook;
}) => JSX.Element;
export default DropDown;
