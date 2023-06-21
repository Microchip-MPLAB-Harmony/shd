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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PluginConfigContext = exports.PluginConfig = exports.pluginService = exports.PluginService = void 0;
const harmony_plugin_core_service_1 = require("@mplab_harmony/harmony-plugin-core-service");
const react_1 = __importDefault(require("react"));
class PluginConfig {
    constructor(pluginId, initArgs) {
        this.pluginId = pluginId;
        this.initArgs = initArgs;
        this.componentId = this.initArgs.componentId;
    }
}
exports.PluginConfig = PluginConfig;
class PluginService {
    constructor() {
        const pluginId = window.pluginConfig.pluginID();
        const initArgs = window.pluginConfig.initArgs();
        this._pluginConfig = new PluginConfig(pluginId, Object.fromEntries(initArgs.entries()));
    }
    readJSONAsync(url) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield fetch(url);
                const json = yield response.json();
                (0, harmony_plugin_core_service_1.log)('Successfully read JSON from ' + url);
                return json;
            }
            catch (err) {
                (0, harmony_plugin_core_service_1.error)('Unable to fetch URL : ' + url + '\n' + err);
            }
        });
    }
    absolutePath(relativePath) {
        return this.frameworkRoot() + '/' + relativePath;
    }
    frameworkRoot() {
        const { protocol, host } = document.location;
        return protocol + '//' + host;
    }
    readJSON(path) {
        const request = new XMLHttpRequest();
        request.open('GET', path, false);
        request.send(null);
        if (request.status === 200) {
            return JSON.parse(request.responseText);
        }
        else {
            throw new Error('Unable to read url : ' + path);
        }
    }
    get pluginConfig() {
        return this._pluginConfig;
    }
}
exports.PluginService = PluginService;
const pluginService = new PluginService();
exports.pluginService = pluginService;
const PluginConfigContext = react_1.default.createContext(pluginService.pluginConfig);
exports.PluginConfigContext = PluginConfigContext;
