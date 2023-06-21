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
const ComboBox_1 = __importDefault(require("./ComboBox"));
const useComboSymbol_1 = __importDefault(require("../../symbol/hook/useComboSymbol"));
const ComboBoxDefault = (props) => {
    const comboSymbolHook = (0, useComboSymbol_1.default)(props);
    const { componentId, symbolId } = props, onlyDropdownProps = __rest(props, ["componentId", "symbolId"]);
    return ((0, jsx_runtime_1.jsx)(ComboBox_1.default, Object.assign({ comboSymbolHook: comboSymbolHook }, onlyDropdownProps)));
};
exports.default = ComboBoxDefault;
