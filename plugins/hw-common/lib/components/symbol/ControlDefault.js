"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DefaultControls = exports.DefaultControl = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const api_1 = require("../../symbol/api");
const CheckBoxDefault_1 = __importDefault(require("./CheckBoxDefault"));
const InputNumberDefault_1 = __importDefault(require("./InputNumberDefault"));
const react_1 = require("react");
const DropDownDefault_1 = __importDefault(require("./DropDownDefault"));
const ComboBoxDefault_1 = __importDefault(require("./ComboBoxDefault"));
const InputTextDefault_1 = __importDefault(require("./InputTextDefault"));
const DefaultControl = (props) => {
    const { componentId, symbolId, symbolType } = props.symbol;
    switch (symbolType) {
        case 'BooleanSymbol': {
            return ((0, jsx_runtime_1.jsx)(CheckBoxDefault_1.default, { componentId: componentId, symbolId: symbolId, className: props.className }));
        }
        case 'IntegerSymbol': {
            return ((0, jsx_runtime_1.jsx)(InputNumberDefault_1.default, { componentId: componentId, symbolId: symbolId, className: props.className }));
        }
        case 'KeyValueSetSymbol': {
            return ((0, jsx_runtime_1.jsx)(DropDownDefault_1.default, { componentId: componentId, symbolId: symbolId, className: props.className }));
        }
        case 'CommentSymbol': {
            return ((0, jsx_runtime_1.jsx)("label", { children: "Comment Symbol UI Control not yet implamented" }));
        }
        case 'ComboSymbol': {
            return ((0, jsx_runtime_1.jsx)(ComboBoxDefault_1.default, { componentId: componentId, symbolId: symbolId, className: props.className }));
        }
        case 'StringSymbol': {
            return ((0, jsx_runtime_1.jsx)(InputTextDefault_1.default, { componentId: componentId, symbolId: symbolId, className: props.className }));
        }
        default:
            return (0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, {});
    }
};
exports.DefaultControl = DefaultControl;
const DefaultControls = (props) => {
    const [symbols, setSymbols] = (0, react_1.useState)([]);
    (0, react_1.useEffect)(() => {
        api_1.symbolUtilApi.getSymbolTypes(props.componentId, props.symbolIds).then((e) => {
            setSymbols(e);
        });
    }, []);
    return ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, { children: symbols.map((symbol) => ((0, jsx_runtime_1.jsx)(DefaultControl, { symbol: symbol }, symbol.symbolId))) }));
};
exports.DefaultControls = DefaultControls;
