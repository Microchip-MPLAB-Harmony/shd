"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
function usePannableContainer() {
    const containerRef = (0, react_1.useRef)(null);
    const [isPanning, setIsPanning] = (0, react_1.useState)(false);
    const [startPoint, setStartPoint] = (0, react_1.useState)({ x: 0, y: 0 });
    (0, react_1.useEffect)(() => {
        if (containerRef.current) {
            containerRef.current.style.overflow = 'auto';
        }
    }, [containerRef]);
    (0, react_1.useEffect)(() => {
        const container = containerRef.current;
        if (!container)
            return;
        const isScrollbarVisible = container.scrollHeight > container.clientHeight ||
            container.scrollWidth > container.clientWidth;
        if (!isScrollbarVisible) {
            setIsPanning(false);
            setStartPoint({ x: 0, y: 0 });
        }
    }, [isPanning]);
    const handleMouseDown = (e) => {
        var _a, _b;
        setIsPanning(true);
        const x = e.clientX + (((_a = containerRef.current) === null || _a === void 0 ? void 0 : _a.scrollLeft) || 0);
        const y = e.clientY + (((_b = containerRef.current) === null || _b === void 0 ? void 0 : _b.scrollTop) || 0);
        setStartPoint({ x, y });
    };
    const handleMouseMove = (e) => {
        var _a;
        if (!isPanning)
            return;
        const newX = startPoint.x - e.clientX;
        const newY = startPoint.y - e.clientY;
        (_a = containerRef.current) === null || _a === void 0 ? void 0 : _a.scrollTo(newX, newY);
    };
    const handleMouseUp = () => {
        setIsPanning(false);
    };
    return {
        ref: containerRef,
        props: {
            onMouseDown: handleMouseDown,
            onMouseMove: handleMouseMove,
            onMouseUp: handleMouseUp,
            onMouseOut: handleMouseUp,
            style: {
                cursor: isPanning ? 'grabbing' : 'default'
            }
        }
    };
}
exports.default = usePannableContainer;
