import { RadioButtonProps } from 'primereact/radiobutton';
import { KeyValueSetSymbolHook } from '../../symbol/hook/useKeyValueSetSymbol';
declare const KeyValueSetRadio: (props: RadioButtonProps & {
    keyValueSetSymbolHook: KeyValueSetSymbolHook;
} & {
    classPrefix: string;
    classResolver?: ((className: string) => string) | undefined;
}) => JSX.Element;
export default KeyValueSetRadio;
