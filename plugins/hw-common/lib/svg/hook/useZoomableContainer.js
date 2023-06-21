"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const MIN_ZOOM_LEVEL = 0.4;
const MAX_ZOOM_LEVEL = 2;
function useZoomableContainer() {
    const containerRef = (0, react_1.useRef)(null);
    const [scaleSize, setScaleSize] = (0, react_1.useState)(1);
    (0, react_1.useEffect)(() => {
        if (containerRef.current) {
            containerRef.current.style.transformOrigin = 'top left';
        }
    }, [containerRef]);
    const resetZoom = () => {
        setScaleSize(1);
        if (containerRef.current) {
            const style = containerRef.current.style;
            style.transform = `scale(1)`;
            style.overflow = `hidden`;
            setTimeout(() => (style.overflow = `auto`));
        }
    };
    const zoomIn = (value) => {
        if (scaleSize > MAX_ZOOM_LEVEL) {
            return;
        }
        const newScaleSize = value || scaleSize + 0.02;
        setScaleSize(newScaleSize);
        if (containerRef.current) {
            containerRef.current.style.transform = `scale(${newScaleSize})`;
        }
    };
    const zoomOut = (value) => {
        if (scaleSize < MIN_ZOOM_LEVEL) {
            return;
        }
        const newScaleSize = value || scaleSize - 0.02;
        setScaleSize(newScaleSize);
        if (containerRef.current) {
            containerRef.current.style.transform = `scale(${newScaleSize})`;
        }
    };
    const handleWheel = (event) => {
        if (event.altKey) {
            event.preventDefault();
            event.stopPropagation();
            if (event.deltaY > 0) {
                zoomOut();
            }
            else {
                zoomIn();
            }
        }
    };
    function handleMouseDown(event) {
        if (event.altKey &&
            event.button === 1) {
            resetZoom();
        }
    }
    return {
        ref: containerRef,
        zoomIn,
        zoomOut,
        resetZoom,
        props: {
            onWheel: handleWheel,
            onMouseDown: handleMouseDown
        }
    };
}
exports.default = useZoomableContainer;
