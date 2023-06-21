"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const api_1 = require("../../symbol/api");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
function useSymbols({ componentId, symbolIds }) {
    const eventAgent = (0, react_1.useContext)(EventService_1.EventAgentContext);
    const [symbols, setSymbols] = (0, react_1.useState)([]);
    (0, react_1.useEffect)(() => {
        api_1.symbolUtilApi.getSymbols(componentId, symbolIds).then(setSymbols);
        const valueListeners = symbolIds.map((symbolId) => (0, EventListenerFactory_1.toSymbolValueListener)(onSymbolChanged, {
            componentId,
            symbolId
        }));
        const visibilityListeners = symbolIds.map((symbolId) => (0, EventListenerFactory_1.toSymbolVisibleListener)(onSymbolChanged, {
            componentId,
            symbolId
        }));
        const stateListeners = symbolIds.map((symbolId) => (0, EventListenerFactory_1.toSymbolStateListener)(onSymbolChanged, {
            componentId,
            symbolId
        }));
        valueListeners.map((listener) => eventAgent.addEventListener(listener));
        visibilityListeners.map((listener) => eventAgent.addEventListener(listener));
        stateListeners.map((listener) => eventAgent.addEventListener(listener));
        return () => {
            valueListeners.map((listener) => eventAgent.removeEventListener(listener));
            visibilityListeners.map((listener) => eventAgent.removeEventListener(listener));
            stateListeners.map((listener) => eventAgent.removeEventListener(listener));
        };
    }, [symbolIds]);
    const onSymbolChanged = (event) => {
        const newSymbol = event.data.symbol;
        setSymbols((symbols) => symbols.map((symbol) => (symbol.symbolId === newSymbol.symbolId ? newSymbol : symbol)));
    };
    return symbols;
}
exports.default = useSymbols;
