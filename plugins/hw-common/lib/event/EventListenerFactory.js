"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.toSymbolStateListener = exports.toSymbolVisibleListener = exports.toSymbolValueListener = void 0;
const toSymbolValueListener = (eventConsumer, eventFilter) => {
    return {
        eventName: 'SymbolValueChangedEvent',
        eventFilter,
        eventConsumer
    };
};
exports.toSymbolValueListener = toSymbolValueListener;
const toSymbolVisibleListener = (eventConsumer, eventFilter) => {
    return {
        eventName: 'SymbolVisualChangedEvent',
        eventFilter,
        eventConsumer
    };
};
exports.toSymbolVisibleListener = toSymbolVisibleListener;
const toSymbolStateListener = (eventConsumer, eventFilter) => {
    return {
        eventName: 'SymbolStateChangedEvent',
        eventFilter,
        eventConsumer
    };
};
exports.toSymbolStateListener = toSymbolStateListener;
