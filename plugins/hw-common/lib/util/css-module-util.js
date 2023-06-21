"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createClassResolver = void 0;
function createClassResolver(...classMaps) {
    return function (...classNames) {
        return classNames
            .map((className) => classMaps
            .map((classMap) => classMap[className])
            .filter(Boolean)
            .join(' '))
            .join(' ');
    };
}
exports.createClassResolver = createClassResolver;
