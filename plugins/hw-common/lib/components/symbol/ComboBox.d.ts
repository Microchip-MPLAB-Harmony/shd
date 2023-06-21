import { DropdownProps } from 'primereact/dropdown';
import { ComboSymbolHook } from '../../symbol/hook/useComboSymbol';
declare const ComboBox: (props: DropdownProps & {
    comboSymbolHook: ComboSymbolHook;
}) => JSX.Element;
export default ComboBox;
