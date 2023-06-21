import VisibleSymbolApi, { VisibleSymbol } from './VisibleSymbolApi';
interface CommentSymbol extends VisibleSymbol {
    label: string;
}
declare class CommentSymbolApi extends VisibleSymbolApi {
    readonly path: string;
    constructor(path?: string);
    getLabel: (componentId: string, symbolId: string) => Promise<string>;
    getCommentSymbol: (componentId: string, symbolId: string) => Promise<CommentSymbol>;
}
export declare const commentSymbolApi: CommentSymbolApi;
export { CommentSymbol };
export default CommentSymbolApi;
