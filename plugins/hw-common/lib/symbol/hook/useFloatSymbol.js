"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const react_2 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const FloatSymbolApi_1 = require("../api/FloatSymbolApi");
const EventSynchronizer_1 = __importDefault(require("../api/EventSynchronizer"));
const useFloatSymbol = ({ componentId, symbolId }) => {
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [value, setValue] = (0, react_1.useState)(0);
    const eventSynchronizer = (0, react_1.useRef)(new EventSynchronizer_1.default(value));
    const [min, setMin] = (0, react_1.useState)(0);
    const [max, setMax] = (0, react_1.useState)(0);
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
        FloatSymbolApi_1.floatSymbolApi
            .getFloatSymbol(componentId, symbolId)
            .then(({ value, min, max, visible, label, description, readOnly }) => {
            setValue(value);
            setMin(min);
            setMax(max);
            setVisible(visible);
            setLabel(label);
            setDescription(description);
            setReadOnly(readOnly);
        });
    };
    const writeValue = (newValue, isOriginalEvent) => {
        if (newValue === null || newValue === value) {
            return;
        }
        if (newValue === 0 && isOriginalEvent === false) {
            eventSynchronizer.current.valueBackup = newValue;
            setValue(newValue);
            setTimeout(() => FloatSymbolApi_1.floatSymbolApi.getValue(componentId, symbolId).then(setValue));
            return;
        }
        eventSynchronizer.current.valueBackup = newValue;
        setValue(newValue);
        const result = eventSynchronizer.current.processUiEvent(newValue);
        if (typeof result === 'number') {
            FloatSymbolApi_1.floatSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolValueChanged = (event) => {
        const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
        if (result === null) {
            setValue(event.data.symbol.value);
        }
        else if (typeof result === 'number') {
            FloatSymbolApi_1.floatSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolVisualChanged = (event) => {
    };
    const onSymbolStateChanged = (event) => {
        setValue(event.value);
    };
    return {
        value,
        min,
        max,
        writeValue,
        visible,
        label,
        description,
        readOnly
    };
};
exports.default = useFloatSymbol;
