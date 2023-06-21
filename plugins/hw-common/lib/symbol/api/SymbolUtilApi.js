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
Object.defineProperty(exports, "__esModule", { value: true });
exports.symbolUtilApi = void 0;
const Transceiver_1 = require("../../txrx/Transceiver");
class SymbolUtilApi {
    constructor(path) {
        this.getSymbolTypes = (componentId, symbolIds) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getSymbolTypes',
                data: {
                    componentId,
                    symbolIds
                }
            });
            return response.data;
        });
        this.getSymbols = (componentId, symbolIds) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getSymbols',
                data: {
                    componentId,
                    symbolIds
                }
            });
            return response.data;
        });
        this.getChildCount = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getChildCount',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.childCount;
        });
        this.getChildren = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getChildren',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.children;
        });
        this.path = path || 'SymbolUtil';
    }
}
exports.symbolUtilApi = new SymbolUtilApi();
exports.default = SymbolUtilApi;
