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
const react_1 = require("react");
const dom_to_image_more_1 = __importDefault(require("dom-to-image-more"));
function useScreehshot() {
    const containerRef = (0, react_1.useRef)(null);
    function getHtmlElement(imageType) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!containerRef.current)
                return;
            const divElement = containerRef.current;
            const prevTransform = divElement.style.transform;
            divElement.style.transform = '';
            let elementScreenshot = null;
            switch (imageType) {
                case 'png': {
                    elementScreenshot = yield dom_to_image_more_1.default.toPng(divElement);
                    break;
                }
                case 'svg': {
                    elementScreenshot = yield dom_to_image_more_1.default.toSvg(divElement);
                    break;
                }
                case 'blob': {
                    elementScreenshot = yield dom_to_image_more_1.default.toBlob(divElement);
                    break;
                }
            }
            divElement.style.transform = prevTransform;
            return elementScreenshot;
        });
    }
    function downloadAsSvg(fileName) {
        return getHtmlElement('svg')
            .then((blob) => {
            const link = document.createElement('a');
            link.href = blob;
            link.download = fileName.endsWith('.svg') ? fileName : `${fileName}.svg`;
            link.click();
        })
            .then((e) => window.location.reload());
    }
    function copyAsBlob() {
        return getHtmlElement('blob')
            .then((blob) => navigator.clipboard.write([
            new ClipboardItem({
                [blob.type]: blob
            })
        ]))
            .then((e) => window.location.reload());
    }
    function copyAsPng() {
        return getHtmlElement('blob')
            .then((blob) => navigator.clipboard.write([
            new ClipboardItem({
                [blob.type]: blob
            })
        ]))
            .then((e) => window.location.reload());
    }
    function copyAsSvg() {
        return getHtmlElement('svg')
            .then((blob) => navigator.clipboard.writeText(blob))
            .then((e) => window.location.reload());
    }
    return {
        ref: containerRef,
        copyAsBlob,
        copyAsPng,
        copyAsSvg,
        downloadAsSvg
    };
}
exports.default = useScreehshot;
