"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const api_1 = require("../api");
const api_2 = require("../api");
const hook_1 = require("../hook");
const useSymbolCache = () => {
    const [symbols, setSymbols] = (0, react_1.useState)([]);
    const addOneSymbol = (symbol) => {
        switch (symbol.symbolType) {
            case 'BooleanSymbol': {
                setSymbols((prev) => [...prev, (0, hook_1.useBooleanSymbol)(symbol)]);
                break;
            }
            case 'IntegerSymbol': {
                setSymbols((prev) => [...prev, (0, hook_1.useIntegerSymbol)(symbol)]);
                break;
            }
            case 'KeyValueSetSymbol': {
                setSymbols((prev) => [...prev, (0, hook_1.useKeyValueSetSymbol)(symbol)]);
                break;
            }
            case 'CommentSymbol': {
                setSymbols((prev) => [...prev, (0, hook_1.useCommentSymbol)(symbol)]);
                break;
            }
            case 'ComboSymbol': {
                setSymbols((prev) => [...prev, (0, hook_1.useComboSymbol)(symbol)]);
                break;
            }
            case 'StringSymbol': {
                setSymbols((prev) => [...prev, (0, hook_1.useStringSymbol)(symbol)]);
                break;
            }
        }
    };
    const addSymbol = (componentId, symbolId) => {
        api_2.symbolApi.getSymbol(componentId, symbolId).then(addOneSymbol);
    };
    const addSymbols = (componentId, symbolIds) => {
        api_1.symbolUtilApi.getSymbols(componentId, symbolIds).then((symbols) => {
            symbols.forEach(addOneSymbol);
        });
    };
    return {
        addSymbol
    };
};
exports.default = useSymbolCache;
