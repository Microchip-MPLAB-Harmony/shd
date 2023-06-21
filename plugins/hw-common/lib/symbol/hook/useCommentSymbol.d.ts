import { SymbolProps } from '../api/SymbolApi';
declare const useCommentSymbol: ({ componentId, symbolId }: SymbolProps) => CommentSymbolHook;
export interface CommentSymbolHook {
    componentId: string;
    symbolId: string;
    visible: boolean;
    label: string;
}
export default useCommentSymbol;
