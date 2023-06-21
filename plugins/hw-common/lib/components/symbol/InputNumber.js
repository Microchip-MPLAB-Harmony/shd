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
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const inputnumber_1 = require("primereact/inputnumber");
const InputNumber = (props) => {
    var _a;
    const { symbolId, value, min, max, readOnly, visible, writeValue } = props.integerSymbolHook;
    const { integerSymbolHook } = props, onlyInputNumberProps = __rest(props, ["integerSymbolHook"]);
    return !((_a = props.hidden) !== null && _a !== void 0 ? _a : !visible) ? ((0, jsx_runtime_1.jsx)(inputnumber_1.InputNumber, Object.assign({ id: symbolId, showButtons: true, mode: 'decimal', value: value, min: min, max: max, disabled: readOnly, onValueChange: (e) => writeValue(e.value, e.originalEvent !== null) }, onlyInputNumberProps))) : ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, {}));
};
exports.default = InputNumber;
