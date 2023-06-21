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
const checkbox_1 = require("primereact/checkbox");
const react_1 = require("react");
function CheckBox(props) {
    var _a;
    const { value, readOnly, visible, writeValue } = props.booleanSymbolHook;
    const { booleanSymbolHook, onStateUpdate, userData } = props, onlyCheckBoxProps = __rest(props, ["booleanSymbolHook", "onStateUpdate", "userData"]);
    (0, react_1.useEffect)(() => {
        onStateUpdate === null || onStateUpdate === void 0 ? void 0 : onStateUpdate(booleanSymbolHook, userData);
    }, [booleanSymbolHook.value]);
    return !((_a = props.hidden) !== null && _a !== void 0 ? _a : !visible) ? ((0, jsx_runtime_1.jsx)(checkbox_1.Checkbox, Object.assign({ inputId: 'binary', checked: value, disabled: readOnly, onChange: (e) => writeValue(e.checked) }, onlyCheckBoxProps))) : ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, {}));
}
exports.default = CheckBox;
