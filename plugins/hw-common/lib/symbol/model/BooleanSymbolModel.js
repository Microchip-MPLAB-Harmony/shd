"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventSynchronizer_1 = __importDefault(require("../api/EventSynchronizer"));
const BooleanSymbolApi_1 = require("../api/BooleanSymbolApi");
class BooleanSymbolViewModel {
    constructor(_eventAgent, _componentId, _symbolId, _symbolType, _visible, _label, _description, _readOnly, _value) {
        this._eventAgent = _eventAgent;
        this._componentId = _componentId;
        this._symbolId = _symbolId;
        this._symbolType = _symbolType;
        this._visible = _visible;
        this._label = _label;
        this._description = _description;
        this._readOnly = _readOnly;
        this._value = _value;
        this.eventSynchronizer = new EventSynchronizer_1.default(_value);
        this.valueListener = (0, EventListenerFactory_1.toSymbolValueListener)(this.onSymbolValueChanged, {
            _componentId,
            _symbolId
        });
        _eventAgent.addEventListener(this.valueListener);
    }
    destroy() {
        this._eventAgent.removeEventListener(this.valueListener);
    }
    get componentId() {
        return this._componentId;
    }
    get symbolId() {
        return this._symbolId;
    }
    get symbolType() {
        return this._symbolType;
    }
    get visible() {
        return this._visible;
    }
    get label() {
        return this._label;
    }
    get description() {
        return this._description;
    }
    get value() {
        return this._value;
    }
    get readOnly() {
        return this._readOnly;
    }
    onSymbolValueChanged(event) {
        const result = this.eventSynchronizer.processDBEvent(event.data.symbol.value);
        if (result === null) {
            this._value = event.data.symbol.value;
        }
        else if (typeof result === 'boolean') {
            BooleanSymbolApi_1.booleanSymbolApi.setValue(this._componentId, this._symbolId, result);
        }
    }
    registerValueChangedListener() {
        return null;
    }
}
