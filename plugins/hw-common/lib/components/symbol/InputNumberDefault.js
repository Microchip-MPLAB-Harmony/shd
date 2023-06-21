"use strict";
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const InputNumber_1 = __importDefault(require("./InputNumber"));
const useIntegerSymbol_1 = __importDefault(require("../../symbol/hook/useIntegerSymbol"));
const InputNumberDefault = (props) => {
    const integerSymbolHook = (0, useIntegerSymbol_1.default)(props);
    const { symbolId, componentId } = props, onlyInputNumberProps = __rest(props, ["symbolId", "componentId"]);
    return ((0, jsx_runtime_1.jsx)(InputNumber_1.default, Object.assign({ integerSymbolHook: integerSymbolHook }, onlyInputNumberProps)));
};
exports.default = InputNumberDefault;
