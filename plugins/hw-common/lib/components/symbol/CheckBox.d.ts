import { CheckboxProps } from 'primereact/checkbox';
import { BooleanSymbolHook } from '../../symbol/hook/useBooleanSymbol';
import { BooleanSymbol } from '../../symbol/api';
import { UpdateProps } from './util';
declare function CheckBox<D>(props: CheckboxProps & {
    booleanSymbolHook: BooleanSymbolHook;
} & UpdateProps<BooleanSymbol, D>): JSX.Element;
export default CheckBox;
