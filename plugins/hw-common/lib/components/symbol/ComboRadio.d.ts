import { RadioButtonProps } from 'primereact/radiobutton';
import { ComboSymbolHook } from '../../symbol/hook/useComboSymbol';
declare const ComboRadio: (props: RadioButtonProps & {
    comboSymbolHook: ComboSymbolHook;
} & {
    classPrefix: string;
    classResolver?: ((className: string) => string) | undefined;
}) => JSX.Element;
export default ComboRadio;
