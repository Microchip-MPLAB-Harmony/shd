"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const SymbolApi_1 = require("../api/SymbolApi");
const react_1 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const util_1 = require("../api/util");
function useSymbol({ componentId, symbolId }) {
    const eventAgent = (0, react_1.useContext)(EventService_1.EventAgentContext);
    const [symbol, setSymbol] = (0, react_1.useState)(() => {
        const defaultSymbol = (0, util_1.createDefaultSymbol)();
        defaultSymbol.componentId = componentId;
        defaultSymbol.symbolId = symbolId;
        return defaultSymbol;
    });
    (0, react_1.useEffect)(() => {
        SymbolApi_1.symbolApi.getSymbol(componentId, symbolId).then(setSymbol);
        const valueListener = (0, EventListenerFactory_1.toSymbolValueListener)(onSymbolChanged, {
            componentId,
            symbolId
        });
        const visibilityListener = (0, EventListenerFactory_1.toSymbolVisibleListener)(onSymbolChanged, {
            componentId,
            symbolId
        });
        const stateListener = (0, EventListenerFactory_1.toSymbolStateListener)(onSymbolChanged, {
            componentId,
            symbolId
        });
        eventAgent.addEventListener(valueListener);
        eventAgent.addEventListener(visibilityListener);
        eventAgent.addEventListener(stateListener);
        return () => {
            eventAgent.removeEventListener(valueListener);
            eventAgent.removeEventListener(visibilityListener);
            eventAgent.removeEventListener(stateListener);
        };
    }, [symbolId]);
    const onSymbolChanged = (event) => {
        setSymbol(event.data.symbol);
    };
    return symbol;
}
exports.default = useSymbol;
