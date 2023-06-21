import { CommentSymbolHook } from '../../symbol/hook/useCommentSymbol';
import { HTMLAttributes } from 'react';
declare const CommentLabel: (props: HTMLAttributes<HTMLDivElement> & {
    commentSymbolHook: CommentSymbolHook;
}) => JSX.Element;
export default CommentLabel;
