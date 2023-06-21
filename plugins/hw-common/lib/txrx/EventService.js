"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventAgentContext = void 0;
const react_1 = __importDefault(require("react"));
const Transceiver_1 = require("./Transceiver");
const uuid_1 = require("uuid");
class EventAgent {
    constructor() {
        this._eventListeners = new Map();
        this._eventAgentId = (0, uuid_1.v4)();
        this.registerFilters = (filters) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: 'event',
                method: 'registerFilters',
                data: {
                    eventFilterCacheId: this._eventAgentId,
                    filters,
                },
            });
            return response.data;
        });
    }
    get id() {
        return this._eventAgentId;
    }
    receive(event) {
        var _a, _b, _c, _d;
        if (!event.eventName) {
            return;
        }
        const filterListenerMap = this._eventListeners.get(event.eventName);
        if (!filterListenerMap)
            return;
        const { componentId, symbolId } = event.data.symbol || event.data.component;
        (_a = filterListenerMap
            .get(this.toHash({}))) === null || _a === void 0 ? void 0 : _a.forEach((eventConsumer) => eventConsumer(event));
        componentId &&
            ((_b = filterListenerMap
                .get(this.toHash({ componentId }))) === null || _b === void 0 ? void 0 : _b.forEach((eventConsumer) => eventConsumer(event)));
        symbolId &&
            ((_c = filterListenerMap
                .get(this.toHash({ symbolId }))) === null || _c === void 0 ? void 0 : _c.forEach((eventConsumer) => eventConsumer(event)));
        if (componentId && symbolId) {
            (_d = filterListenerMap
                .get(this.toHash({ componentId, symbolId }))) === null || _d === void 0 ? void 0 : _d.forEach((eventConsumer) => eventConsumer(event));
        }
    }
    addEventListener(eventListener) {
        const { eventName } = eventListener;
        let filterListenerMap = this._eventListeners.get(eventName);
        if (!filterListenerMap) {
            filterListenerMap = new Map();
            this._eventListeners.set(eventName, filterListenerMap);
        }
        const eventFilter = eventListener.eventFilter || {};
        let listeners = filterListenerMap.get(this.toHash(eventFilter));
        if (!listeners) {
            listeners = new Set();
            filterListenerMap.set(this.toHash(eventFilter), listeners);
        }
        listeners.add(eventListener.eventConsumer);
        this.registerFilters([Object.assign({ eventName }, eventFilter)]);
    }
    removeEventListener(eventListener) {
        const { eventName } = eventListener;
        const filterListenerMap = this._eventListeners.get(eventName);
        if (filterListenerMap) {
            const eventFilter = eventListener.eventFilter || {};
            const listeners = filterListenerMap.get(this.toHash(eventFilter));
            const isDeleted = listeners === null || listeners === void 0 ? void 0 : listeners.delete(eventListener.eventConsumer);
            isDeleted &&
                (listeners === null || listeners === void 0 ? void 0 : listeners.size) === 0 &&
                Transceiver_1.transceiver.send({
                    path: 'event',
                    method: 'deregisterFilters',
                    data: {
                        eventFilterCacheId: this._eventAgentId,
                        filters: [Object.assign({ eventName }, eventFilter)],
                    },
                });
        }
    }
    destroy() {
        Transceiver_1.transceiver.send({
            path: 'event',
            method: 'destroyEventFilterCache',
            data: {
                eventFilterCacheId: this._eventAgentId,
            },
        });
        this._eventListeners.clear();
    }
    toHash(eventFilter) {
        if (!eventFilter) {
            return ':';
        }
        const componentId = eventFilter.componentId || '';
        const symbolId = eventFilter.symbolId || '';
        return `${componentId}:${symbolId}`;
    }
    fromHash(hash) {
        if (hash === ':') {
            return {};
        }
        const abc = hash.split(':');
        return { componentId: abc[0] || '', symbolId: abc[1] || '' };
    }
}
exports.EventAgentContext = react_1.default.createContext(new EventAgent());
exports.default = EventAgent;
