"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const react_2 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const SymbolUtilApi_1 = require("../api/SymbolUtilApi");
const useBooleanSymbol_1 = __importDefault(require("./useBooleanSymbol"));
const useGetSymbolAsType = (symbol) => {
    const { componentId, symbolId } = symbol;
    const { symbolType } = symbol;
    switch (symbolType) {
        case 'BooleanSymbol': {
            return (0, useBooleanSymbol_1.default)(symbol);
        }
        case 'IntegerSymbol': {
            return symbol;
        }
        case 'KeyValueSetSymbol': {
            return symbol;
        }
        case 'CommentSymbol': {
            return symbol;
        }
        case 'ComboSymbol': {
            return symbol;
        }
        case 'StringSymbol': {
            return symbol;
        }
        default:
            throw new Error('symbol type is not supported!');
    }
};
const useSymbols = (props) => {
    const { componentId, symbolIds } = props;
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [symbols, setSymbols] = (0, react_1.useState)([]);
    const symbolHooks = Array.from(symbolIds, (symbol, index) => ({
        symbol,
        hook: (0, useBooleanSymbol_1.default)({ componentId, symbolId: symbol })
    }));
    (0, react_1.useEffect)(() => {
        initFromDB();
        const valueListener = (0, EventListenerFactory_1.toSymbolValueListener)(onSymbolValueChanged);
        eventAgent.addEventListener(valueListener);
        return () => {
            eventAgent.removeEventListener(valueListener);
        };
    }, []);
    const initFromDB = () => {
        SymbolUtilApi_1.symbolUtilApi.getSymbols(componentId, symbolIds).then(setSymbols);
    };
    const onSymbolValueChanged = (event) => {
        const { componentId, symbolId, value } = event.data.symbol;
        const foundSymbol = symbols.find((e) => e.componentId == componentId && e.symbolId == symbolId);
        symbols.map((e) => e.componentId == componentId && e.symbolId == symbolId ? (e.value = value) : e);
    };
    const onSymbolVisualChanged = (event) => {
    };
    const onSymbolStateChanged = (event) => {
    };
    return {
        componentId,
        symbols
    };
};
exports.default = useSymbols;
