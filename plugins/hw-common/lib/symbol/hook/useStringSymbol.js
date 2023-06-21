"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const react_2 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const StringSymbolApi_1 = require("../api/StringSymbolApi");
const EventSynchronizer_1 = __importDefault(require("../api/EventSynchronizer"));
const useStringSymbol = ({ componentId, symbolId }) => {
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [value, setValue] = (0, react_1.useState)('');
    const eventSynchronizer = (0, react_1.useRef)(new EventSynchronizer_1.default(value));
    const [visible, setVisible] = (0, react_1.useState)(false);
    const [label, setLabel] = (0, react_1.useState)('');
    const [description, setDescription] = (0, react_1.useState)('');
    const [readOnly, setReadOnly] = (0, react_1.useState)(false);
    (0, react_1.useEffect)(() => {
        initFromDB();
        const valueListener = (0, EventListenerFactory_1.toSymbolValueListener)(onSymbolValueChanged, {
            componentId,
            symbolId
        });
        const visibilityListener = (0, EventListenerFactory_1.toSymbolVisibleListener)(onSymbolVisualChanged, {
            componentId,
            symbolId
        });
        const stateListener = (0, EventListenerFactory_1.toSymbolStateListener)(onSymbolStateChanged, {
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
    }, []);
    const initFromDB = () => {
        StringSymbolApi_1.stringSymbolApi.getStringSymbol(componentId, symbolId).then((symbol) => {
            setValue(symbol.value);
            setVisible(symbol.visible);
            setLabel(symbol.label);
            setDescription(symbol.description);
            setReadOnly(symbol.readOnly);
        });
    };
    const writeValue = (newValue) => {
        eventSynchronizer.current.valueBackup = newValue;
        setValue(newValue);
        const result = eventSynchronizer.current.processUiEvent(newValue);
        if (typeof result === 'string') {
            StringSymbolApi_1.stringSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolValueChanged = (event) => {
        const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
        if (result === null) {
            setValue(event.data.symbol.value);
        }
        else if (typeof result === 'string') {
            StringSymbolApi_1.stringSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolVisualChanged = (event) => {
        setVisible(event.data.symbol.visible);
    };
    const onSymbolStateChanged = (event) => {
        setValue(event.data.symbol.value);
    };
    return {
        componentId,
        symbolId,
        value,
        writeValue,
        visible,
        label,
        description,
        readOnly
    };
};
exports.default = useStringSymbol;
