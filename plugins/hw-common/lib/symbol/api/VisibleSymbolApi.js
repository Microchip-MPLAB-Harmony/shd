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
exports.visibleSymbolApi = void 0;
const Transceiver_1 = require("../../txrx/Transceiver");
const SymbolApi_1 = __importDefault(require("./SymbolApi"));
class VisibleSymbolApi extends SymbolApi_1.default {
    constructor(path) {
        super(path);
        this.getVisible = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getVisible',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.visible;
        });
        this.path = path || 'VisibleSymbol';
    }
}
exports.visibleSymbolApi = new VisibleSymbolApi();
exports.default = VisibleSymbolApi;
