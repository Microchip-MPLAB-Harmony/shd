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
exports.symbolApi = void 0;
const Transceiver_1 = require("../../txrx/Transceiver");
class SymbolApi {
    constructor(path) {
        this.getSymbolType = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getSymbolType',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.symbolType;
        });
        this.getSymbol = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getSymbol',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data;
        });
        this.path = path || 'Symbol';
    }
}
exports.symbolApi = new SymbolApi();
exports.default = SymbolApi;
