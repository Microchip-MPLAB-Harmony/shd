import { ISymbol } from '../../symbol/api';
declare const DefaultControl: (props: {
    symbol: ISymbol;
    className?: string;
}) => JSX.Element;
declare const DefaultControls: (props: {
    componentId: string;
    symbolIds: string[];
}) => JSX.Element;
export { DefaultControl, DefaultControls };
