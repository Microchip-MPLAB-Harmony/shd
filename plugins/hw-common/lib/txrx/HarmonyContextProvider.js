"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const EventService_1 = __importStar(require("./EventService"));
const PluginService_1 = require("../plugin/PluginService");
const Transceiver_1 = require("./Transceiver");
function HarmonyContextProvider({ children }) {
    const eventAgent = (0, react_1.useRef)(new EventService_1.default());
    const pluginConfig = (0, react_1.useRef)(PluginService_1.pluginService.pluginConfig);
    (0, react_1.useEffect)(() => {
        Transceiver_1.transceiver.registerEventAgent(eventAgent.current);
        return () => {
            if (eventAgent.current) {
                eventAgent.current.destroy();
                Transceiver_1.transceiver.deregisterEventAgent(eventAgent.current);
            }
        };
    }, []);
    return ((0, jsx_runtime_1.jsx)(EventService_1.EventAgentContext.Provider, Object.assign({ value: eventAgent.current }, { children: (0, jsx_runtime_1.jsx)(PluginService_1.PluginConfigContext.Provider, Object.assign({ value: pluginConfig.current }, { children: children })) })));
}
exports.default = HarmonyContextProvider;
