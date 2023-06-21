"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const CommentSymbolApi_1 = require("../api/CommentSymbolApi");
const react_2 = require("react");
const EventListenerFactory_1 = require("../../event/EventListenerFactory");
const EventService_1 = require("../../txrx/EventService");
const useCommentSymbol = ({ componentId, symbolId }) => {
    const eventAgent = (0, react_2.useContext)(EventService_1.EventAgentContext);
    const [visible, setVisible] = (0, react_1.useState)(false);
    const [label, setLabel] = (0, react_1.useState)('');
    (0, react_1.useEffect)(() => {
        initFromDB();
        const visibilityListener = (0, EventListenerFactory_1.toSymbolVisibleListener)(onSymbolVisualChanged, {
            componentId,
            symbolId
        });
        eventAgent.addEventListener(visibilityListener);
        return () => {
            eventAgent.removeEventListener(visibilityListener);
        };
    }, []);
    const initFromDB = () => {
        CommentSymbolApi_1.commentSymbolApi.getCommentSymbol(componentId, symbolId).then(({ visible, label }) => {
            setVisible(visible);
            setLabel(label);
        });
    };
    const onSymbolVisualChanged = (event) => {
        setLabel(event.data.symbol.label);
        setVisible(event.data.symbol.visible);
    };
    return {
        componentId,
        symbolId,
        visible,
        label
    };
};
exports.default = useCommentSymbol;
