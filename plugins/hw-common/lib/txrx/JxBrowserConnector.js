"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.jxBrowserConnector = void 0;
const Transceiver_1 = require("./Transceiver");
const CustomConsole_1 = require("@mplab_harmony/harmony-plugin-core-service/build/log/CustomConsole");
class JxBrowserConnector {
    constructor() {
        this._uuid = 'defaultUUID';
        (0, CustomConsole_1.log)('ClientJxBrowserConnector : Constructor');
        window.clientJxBrowserConnectorReceive = this.receive;
    }
    send(request) {
        request.uuid = this._uuid;
        window.serverJxBrowserConnector.receive(JSON.stringify(request));
    }
    receive(response) {
        try {
            Transceiver_1.transceiver.receive(JSON.parse(response));
        }
        catch (e) {
            (0, CustomConsole_1.error)(`Client JxBrowser Connector : Parsing Response Failed. ${response}`);
        }
    }
}
exports.jxBrowserConnector = new JxBrowserConnector();
