import { InputNumberProps } from 'primereact/inputnumber';
import { IntegerSymbolHook } from '../../symbol/hook/useIntegerSymbol';
declare const InputNumber: (props: InputNumberProps & {
    integerSymbolHook: IntegerSymbolHook;
}) => JSX.Element;
export default InputNumber;
