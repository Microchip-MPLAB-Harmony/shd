"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const react_2 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const KeyValueSetSymbolApi_1 = require("../api/KeyValueSetSymbolApi");
const EventSynchronizer_1 = __importDefault(require("../api/EventSynchronizer"));
const useKeyValueSetSymbol = ({ componentId, symbolId }) => {
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [value, setValue] = (0, react_1.useState)(0);
    const eventSynchronizer = (0, react_1.useRef)(new EventSynchronizer_1.default(value));
    const [visible, setVisible] = (0, react_1.useState)(false);
    const [label, setLabel] = (0, react_1.useState)('');
    const [description, setDescription] = (0, react_1.useState)('');
    const [readOnly, setReadOnly] = (0, react_1.useState)(false);
    const [optionPairs, setOptionPairs] = (0, react_1.useState)([]);
    const [selectedOptionPair, setSelectedOptionPair] = (0, react_1.useState)(undefined);
    const [displayMode, setDisplayMode] = (0, react_1.useState)(KeyValueSetSymbolApi_1.DisplayMode.Key);
    const [options, setOptions] = (0, react_1.useState)([]);
    const [selectedOption, setSelectedOption] = (0, react_1.useState)('');
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
    (0, react_1.useEffect)(() => {
        setSelectedOptionPair(optionPairs.at(value));
    }, [value, optionPairs]);
    (0, react_1.useEffect)(() => {
        var _a;
        const getDisplayString = (pair) => {
            switch (displayMode) {
                case KeyValueSetSymbolApi_1.DisplayMode.Key:
                    return pair.key;
                case KeyValueSetSymbolApi_1.DisplayMode.Value:
                    return pair.value;
                case KeyValueSetSymbolApi_1.DisplayMode.Description:
                    return pair.description;
            }
        };
        setOptions((_a = optionPairs.map((e) => getDisplayString(e))) !== null && _a !== void 0 ? _a : []);
        setSelectedOption(selectedOptionPair ? getDisplayString(selectedOptionPair) : '');
    }, [displayMode, optionPairs, selectedOptionPair, value]);
    const initFromDB = () => {
        KeyValueSetSymbolApi_1.keyValueSetSymbolApi.getKeyValueSetSymbol(componentId, symbolId).then((symbol) => {
            setValue(symbol.value);
            setVisible(symbol.visible);
            setLabel(symbol.label);
            setDescription(symbol.description);
            setReadOnly(symbol.readOnly);
            setOptionPairs(symbol.optionPairs);
            setDisplayMode(symbol.displayMode);
            setSelectedOptionPair(symbol.selectedOptionPair);
        });
    };
    const getDisplayString = (pair) => {
        switch (displayMode) {
            case KeyValueSetSymbolApi_1.DisplayMode.Key:
                return pair.key;
            case KeyValueSetSymbolApi_1.DisplayMode.Value:
                return pair.value;
            case KeyValueSetSymbolApi_1.DisplayMode.Description:
                return pair.description;
        }
    };
    const displayStringToValue = (displayString) => {
        return optionPairs.map((e) => getDisplayString(e)).indexOf(displayString);
    };
    const valueToDisplayString = (value) => {
        return getDisplayString(optionPairs.at(value) || optionPairs[0]);
    };
    const writeValue = (newValue) => {
        const temp = displayStringToValue(newValue);
        if (temp === value) {
            return;
        }
        eventSynchronizer.current.valueBackup = temp;
        setValue(temp);
        const result = eventSynchronizer.current.processUiEvent(temp);
        if (typeof result === 'number') {
            KeyValueSetSymbolApi_1.keyValueSetSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolValueChanged = (event) => {
        const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
        if (result === null) {
            setValue(event.data.symbol.value);
        }
        else if (typeof result === 'number') {
            KeyValueSetSymbolApi_1.keyValueSetSymbolApi.setValue(componentId, symbolId, result);
        }
    };
    const onSymbolVisualChanged = (event) => {
        setVisible(event.data.symbol.visible);
    };
    const onSymbolStateChanged = (event) => {
        setValue(event.data.symbol.value);
        setDisplayMode(event.data.symbol.displayMode);
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
        optionPairs,
        options,
        selectedOptionPair,
        selectedOption,
        displayMode
    };
};
exports.default = useKeyValueSetSymbol;
