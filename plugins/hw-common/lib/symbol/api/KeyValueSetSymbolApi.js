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
exports.keyValueSetSymbolApi = exports.DisplayMode = void 0;
const Transceiver_1 = require("../../txrx/Transceiver");
const ConfigSymbolApi_1 = __importDefault(require("./ConfigSymbolApi"));
var DisplayMode;
(function (DisplayMode) {
    DisplayMode["Key"] = "Key";
    DisplayMode["Value"] = "Value";
    DisplayMode["Description"] = "Description";
})(DisplayMode = exports.DisplayMode || (exports.DisplayMode = {}));
class KeyValueSetSymbolApi extends ConfigSymbolApi_1.default {
    constructor(path) {
        super(path);
        this.getValue = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getValue',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.value;
        });
        this.setValue = (componentId, symbolId, value) => __awaiter(this, void 0, void 0, function* () {
            Transceiver_1.transceiver.send({
                path: this.path,
                method: 'setValue',
                data: {
                    componentId,
                    symbolId,
                    value
                }
            });
            return;
        });
        this.getOptionPairs = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getOptionPairs',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.optionPairs;
        });
        this.getSelectedOptionPair = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getSelectedOptionPair',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.selectedOptionPair;
        });
        this.getDisplayMode = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getDisplayMode',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.displayMode;
        });
        this.setDisplayMode = (componentId, symbolId, displayMode) => __awaiter(this, void 0, void 0, function* () {
            Transceiver_1.transceiver.send({
                path: this.path,
                method: 'setDisplayMode',
                data: {
                    componentId,
                    symbolId,
                    displayMode
                }
            });
            return;
        });
        this.getKeyValueSetSymbol = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getKeyValueSetSymbol',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data;
        });
        this.path = path || 'KeyValueSetSymbol';
    }
}
exports.keyValueSetSymbolApi = new KeyValueSetSymbolApi();
exports.default = KeyValueSetSymbolApi;
