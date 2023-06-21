"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.transceiver = void 0;
const harmony_plugin_core_service_1 = require("@mplab_harmony/harmony-plugin-core-service");
const JxBrowserConnector_1 = require("./JxBrowserConnector");
class Transceiver {
    constructor() {
        this._sequencePromiseMap = new Map();
        this.requestCounter = 1;
        this._eventAgents = new Map();
        (0, harmony_plugin_core_service_1.log)('Client Transceiver : Constructor');
    }
    send(request) {
        request.sequenceNumber = this.requestCounter++;
        const promise = new Promise((resolve, reject) => {
            const promiseHolder = {
                resolve,
                reject
            };
            request.sequenceNumber && this._sequencePromiseMap.set(request.sequenceNumber, promiseHolder);
        });
        JxBrowserConnector_1.jxBrowserConnector.send(request);
        return promise;
    }
    receive(response) {
        var _a;
        const { status, sequenceNumber, eventName, eventFilterCacheId } = response;
        if (status === 'event') {
            if (!eventFilterCacheId || !eventName) {
                (0, harmony_plugin_core_service_1.error)('Invalid Event : Event Filter Cache Id or Event Name is empty. Response: ' +
                    JSON.stringify(response));
            }
            else {
                (_a = this._eventAgents.get(eventFilterCacheId)) === null || _a === void 0 ? void 0 : _a.receive(response);
            }
        }
        else if (sequenceNumber && this._sequencePromiseMap.has(sequenceNumber)) {
            const promiseHolder = this._sequencePromiseMap.get(sequenceNumber);
            this._sequencePromiseMap.delete(sequenceNumber);
            this.verifyAndResetSequenceNumber();
            if (status === 'success') {
                promiseHolder && promiseHolder.resolve(response);
            }
            else if (status === 'error') {
                promiseHolder && promiseHolder.reject(response);
            }
        }
    }
    verifyAndResetSequenceNumber() {
        if (this._sequencePromiseMap.size === 0) {
            if (this.requestCounter > 1000000000000000) {
                this.requestCounter = 1;
            }
        }
    }
    registerEventAgent(eventAgent) {
        this._eventAgents.set(eventAgent.id, eventAgent);
    }
    deregisterEventAgent(eventAgent) {
        return this._eventAgents.delete(eventAgent.id);
    }
}
exports.transceiver = new Transceiver();
