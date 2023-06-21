"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createDefaultSymbol = void 0;
const KeyValueSetSymbolApi_1 = require("./KeyValueSetSymbolApi");
const defaultSymbol = {
    componentId: 'defaultComponentId',
    symbolId: 'defaultSymbolId',
    symbolType: 'StringSymbol',
    visible: false,
    label: 'defaultLabel',
    description: 'defaultDescription',
    readOnly: true,
    value: 'defaultValue',
    options: [],
    min: 0,
    max: 0,
    optionPairs: [],
    displayMode: KeyValueSetSymbolApi_1.DisplayMode.Description,
    selectedOptionPair: {
        description: 'defaultDescription',
        key: 'defaultKey',
        value: 'defaultValue'
    }
};
function createDefaultSymbol() {
    return JSON.parse(JSON.stringify(defaultSymbol));
}
exports.createDefaultSymbol = createDefaultSymbol;
