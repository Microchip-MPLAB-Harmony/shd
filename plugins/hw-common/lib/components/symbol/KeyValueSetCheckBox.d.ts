import { CheckboxProps } from 'primereact/checkbox';
import { KeyValueSetSymbolHook } from '../../symbol/hook/useKeyValueSetSymbol';
declare const KeyValueSetCheckBox: (props: CheckboxProps & {
    keyValueSetSymbolHook: KeyValueSetSymbolHook;
} & {
    trueOption: string;
    falseOption: string;
}) => JSX.Element;
export default KeyValueSetCheckBox;
