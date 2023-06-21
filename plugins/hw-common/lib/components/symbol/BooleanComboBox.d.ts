import { DropdownProps } from 'primereact/dropdown';
import { BooleanSymbolHook } from '../../symbol/hook/useBooleanSymbol';
declare const BooleanComboBox: (props: DropdownProps & {
    booleanSymbolHook: BooleanSymbolHook;
} & {
    trueOption: string;
    falseOption: string;
}) => JSX.Element;
export default BooleanComboBox;
