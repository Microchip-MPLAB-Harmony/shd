"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const useBooleanSymbol_1 = __importDefault(require("../../symbol/hook/useBooleanSymbol"));
const react_1 = require("react");
function BooleanFragment(props) {
    const booleanSymbolHook = (0, useBooleanSymbol_1.default)(props);
    const { onStateUpdate, userData } = props;
    (0, react_1.useEffect)(() => {
        onStateUpdate === null || onStateUpdate === void 0 ? void 0 : onStateUpdate(booleanSymbolHook, userData);
    }, [booleanSymbolHook.value]);
    return (0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, {});
}
exports.default = BooleanFragment;
