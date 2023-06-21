import { SymbolProps } from '../../symbol/api/SymbolApi';
import { UpdateProps } from './util';
import { BooleanSymbol } from '../../symbol/api/BooleanSymbolApi';
declare function BooleanFragment<D>(props: SymbolProps & UpdateProps<BooleanSymbol, D>): JSX.Element;
export default BooleanFragment;
