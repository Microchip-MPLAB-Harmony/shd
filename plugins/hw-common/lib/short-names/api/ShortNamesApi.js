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
exports.shortNamesApi = void 0;
const Transceiver_1 = require("../../txrx/Transceiver");
class ShortNamesApi {
    constructor() {
        this.path = 'ShortNames';
        this.generateShortNamesTemplate = (componentId, symbolId) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'generateShortNamesTemplate',
                data: {
                    componentId,
                    symbolId
                }
            });
            return response.data.shortNames;
        });
        this.getResolvedShortNamesTemplate = (fileName) => __awaiter(this, void 0, void 0, function* () {
            const response = yield Transceiver_1.transceiver.send({
                path: this.path,
                method: 'getResolvedShortNamesTemplate',
                data: {
                    fileName
                }
            });
            return response.data.shortNames;
        });
        this.applyShortNames = (componentId, symbolId, shortNames) => __awaiter(this, void 0, void 0, function* () {
            Transceiver_1.transceiver.send({
                path: this.path,
                method: 'applyShortNames',
                data: {
                    componentId,
                    symbolId,
                    shortNames
                }
            });
            return;
        });
    }
}
exports.shortNamesApi = new ShortNamesApi();
exports.default = ShortNamesApi;
