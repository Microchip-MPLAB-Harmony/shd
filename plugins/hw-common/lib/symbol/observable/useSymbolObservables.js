"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const BooleanSymbolObservable_1 = require("./BooleanSymbolObservable");
const txrx_1 = require("../../txrx");
const useSymbolObservables = () => {
    const [symbols, setSymbols] = (0, react_1.useState)([]);
    const reff = (0, react_1.useRef)(new txrx_1.EventAgent());
    (0, react_1.useEffect)(() => {
        return () => {
            reff.current.destroy();
        };
    }, []);
    const getSymbol = (componentId, symbolId) => {
        let symbol = symbols.find((e) => e.symbolId == symbolId);
        if (!symbol) {
            symbol = new BooleanSymbolObservable_1.BooleanSymbolObservable(componentId, symbolId, reff.current);
            setSymbols([...symbols, symbol]);
        }
        return symbol;
    };
    return { getSymbol };
};
exports.default = useSymbolObservables;
(0, react_1.createContext)({});
