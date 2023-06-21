"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const button_1 = require("primereact/button");
const slidemenu_1 = require("primereact/slidemenu");
const react_1 = require("react");
const PluginToolbar = ({ menuItems, title }) => {
    const menu = (0, react_1.useRef)(null);
    return ((0, jsx_runtime_1.jsxs)("div", Object.assign({ style: {
            height: '45px',
            padding: '0 15px 0 15px',
            backgroundColor: '#f0f2f3',
            borderBottom: '1px solid rgb(200, 200, 200)',
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            columnGap: '10px'
        } }, { children: [(0, jsx_runtime_1.jsx)(slidemenu_1.SlideMenu, { className: 'p-menuitem-icon', style: { width: 190 }, menuWidth: 190, ref: menu, model: menuItems, popup: true }), (0, jsx_runtime_1.jsx)(button_1.Button, { className: 'p-button-outlined p-button-lg p-button-primary', icon: 'pi pi-bars', onClick: (event) => {
                    var _a;
                    (_a = menu.current) === null || _a === void 0 ? void 0 : _a.toggle(event);
                } }), (0, jsx_runtime_1.jsx)("label", Object.assign({ style: {
                    fontWeight: '500',
                    fontSize: '1.5rem',
                    whiteSpace: 'nowrap'
                } }, { children: title }))] })));
};
exports.default = PluginToolbar;
