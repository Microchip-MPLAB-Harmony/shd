"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const api_1 = require("../api");
class DatabaseCache {
    constructor(_componentId) {
        this._componentId = _componentId;
        this._symbolIds = [];
        this._symbols = new Map();
    }
    registerSymbol(symbolId) {
        this._symbolIds.push(symbolId);
    }
    registerSymbols(symbolIds) {
        api_1.symbolUtilApi.getSymbols(this._componentId, symbolIds).then((symbols) => {
            symbols.forEach((symbol) => this._symbols.set(symbol.symbolId, symbol));
        });
        this._symbolIds.concat(symbolIds);
    }
    findSymbol(componentId, symbolId) {
        if (componentId !== this._componentId)
            return;
        return undefined;
    }
    get componentId() {
        return this._componentId;
    }
}
