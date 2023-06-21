"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processDBEvent = exports.processUiEvent = void 0;
const harmony_plugin_core_service_1 = require("@mplab_harmony/harmony-plugin-core-service");
function processUiEvent(uiValue, syncValue) {
    if (syncValue === undefined) {
        syncValue = uiValue;
        return uiValue;
    }
}
exports.processUiEvent = processUiEvent;
function processDBEvent(dbValue, syncValue, valueBackup) {
    if (syncValue === undefined) {
        valueBackup = dbValue;
        return null;
    }
    else if (syncValue === dbValue) {
        if (valueBackup !== syncValue) {
            syncValue = valueBackup;
            return valueBackup;
        }
        else {
            syncValue = undefined;
        }
    }
    else {
        (0, harmony_plugin_core_service_1.error)(`Event Sync Issue: Expected Value: ${JSON.stringify(syncValue)}, Received: ${JSON.stringify(dbValue)}`);
    }
}
exports.processDBEvent = processDBEvent;
class EventSynchronizer {
    constructor(_valueBackup) {
        this._valueBackup = _valueBackup;
        this.syncValue = undefined;
    }
    get valueBackup() {
        return this._valueBackup;
    }
    set valueBackup(value) {
        this._valueBackup = value;
    }
    processUiEvent(uiValue) {
        if (this.syncValue === undefined) {
            this.syncValue = uiValue;
            return uiValue;
        }
    }
    processDBEvent(dbValue) {
        if (this.syncValue === undefined) {
            this.valueBackup = dbValue;
            return null;
        }
        else if (this.syncValue === dbValue) {
            if (this.valueBackup !== this.syncValue) {
                this.syncValue = this.valueBackup;
                return this.valueBackup;
            }
            else {
                this.syncValue = undefined;
            }
        }
        else {
            (0, harmony_plugin_core_service_1.error)(`Event Sync Issue: Expected Value: ${JSON.stringify(this.syncValue)}, Received: ${JSON.stringify(dbValue)}`);
        }
    }
}
exports.default = EventSynchronizer;
