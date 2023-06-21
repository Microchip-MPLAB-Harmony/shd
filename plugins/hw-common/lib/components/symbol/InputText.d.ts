import { InputTextProps } from 'primereact/inputtext';
import { StringSymbolHook } from '../../symbol/hook/useStringSymbol';
declare const InputText: (props: InputTextProps & {
    stringSymbolHook: StringSymbolHook;
}) => JSX.Element;
export default InputText;
