"use strict";
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
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
const isAnyUndefined = (...values) => {
    return values.some((e) => e === undefined);
};
const useBooleanSymbolLight = (_a) => {
    var { componentId, symbolId } = _a, symbol = __rest(_a, ["componentId", "symbolId"]);
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [value, setValue] = (0, react_1.useState)(symbol.value);
    const eventSynchronizer = (0, react_1.useRef)(new EventSynchronizer_1.default(symbol.value));
    const [visible] = (0, react_1.useState)(symbol.visible);
    const [label] = (0, react_1.useState)(symbol.label);
    const [description] = (0, react_1.useState)(symbol.description);
    const [readOnly] = (0, react_1.useState)(symbol.readOnly);
    const valueListenerRef = (0, react_1.useRef)((0, EventListenerFactory_1.toSymbolValueListener)(onSymbolValueChanged, {
        componentId,
        symbolId
    }));
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
    function onSymbolValueChanged(event) {
        const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
        if (result === null) {
            setValue(event.data.symbol.value);
        }
        else if (typeof result === 'boolean') {
            BooleanSymbolApi_1.booleanSymbolApi.setValue(componentId, symbolId, result);
        }
    }
    const onSymbolVisualChanged = (event) => {
    };
    const onSymbolStateChanged = (event) => {
        setValue(event.value);
    };
    const registerListener = () => {
        eventAgent.addEventListener(valueListenerRef.current);
    };
    const deregisterListener = () => {
        eventAgent.removeEventListener(valueListenerRef.current);
    };
    return {
        componentId,
        symbolId,
        value,
        writeValue,
        visible,
        label,
        description,
        readOnly,
        registerListener,
        deregisterListener
    };
};
exports.default = useBooleanSymbolLight;
