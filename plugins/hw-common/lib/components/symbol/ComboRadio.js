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
const radiobutton_1 = require("primereact/radiobutton");
const ComboRadio = (props) => {
    var _a;
    const { value, options, readOnly, visible, writeValue } = props.comboSymbolHook;
    const { comboSymbolHook, classPrefix, classResolver } = props, onlyRadioButtonProps = __rest(props, ["comboSymbolHook", "classPrefix", "classResolver"]);
    return !((_a = props.hidden) !== null && _a !== void 0 ? _a : !visible) ? ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, { children: options.map((option, i) => ((0, jsx_runtime_1.jsx)(radiobutton_1.RadioButton, Object.assign({ inputId: option, name: classPrefix, disabled: readOnly, value: option, onChange: (e) => writeValue(option), checked: option === value }, onlyRadioButtonProps, { className: classResolver ? classResolver(`${classPrefix}${i}`) : `${classPrefix}${i}` }), option))) })) : ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, {}));
};
exports.default = ComboRadio;
