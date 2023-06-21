"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const BooleanSymbolApi_1 = require("../api/BooleanSymbolApi");
const react_2 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const EventSynchronizer_1 = __importDefault(require("../api/EventSynchronizer"));
const useBooleanSymbol = ({ componentId, symbolId }) => {
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [value, setValue] = (0, react_1.useState)(false);
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
        eventAgent.addEventListener(valueListener);
        return () => {
            eventAgent.removeEventListener(valueListener);
        };
    }, []);
    const initFromDB = () => {
        BooleanSymbolApi_1.booleanSymbolApi
            .getBooleanSymbol(componentId, symbolId)
            .then(({ value, visible, label, description, readOnly }) => {
            setValue(value);
            setVisible(visible);
            setLabel(label);
            setDescription(description);
            setReadOnly(readOnly);
        });
    };
    const writeValue = (newValue) => {
        if (newValue === value) {
            return;
        }
        eventSynchronizer.current.valueBackup = newValue;
        setValue(newValue);
        const result = eventSynchronizer.current.processUiEvent(newValue);
        if (typeof result === 'boolean') {
            BooleanSymbolApi_1.booleanSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolValueChanged = (event) => {
        const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
        if (result === null) {
            setValue(event.data.symbol.value);
        }
        else if (typeof result === 'boolean') {
            BooleanSymbolApi_1.booleanSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolVisualChanged = (event) => {
    };
    const onSymbolStateChanged = (event) => {
        setValue(event.value);
    };
    return {
        componentId,
        symbolId,
        symbolType: 'BooleanSymbol',
        value,
        writeValue,
        visible,
        label,
        description,
        readOnly
    };
};
exports.default = useBooleanSymbol;
