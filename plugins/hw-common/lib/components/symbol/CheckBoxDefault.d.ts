import { CheckboxProps } from 'primereact/checkbox';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import { UpdateProps } from './util';
import { BooleanSymbol } from '../../symbol/api/BooleanSymbolApi';
declare function CheckBoxDefault<D>(props: SymbolProps & CheckboxProps & UpdateProps<BooleanSymbol, D>): JSX.Element;
export default CheckBoxDefault;
