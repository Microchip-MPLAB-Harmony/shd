import { CommentSymbolHook } from '../../symbol/hook/useCommentSymbol';
import { HTMLAttributes } from 'react';

const CommentLabel = (
  props: HTMLAttributes<HTMLDivElement> & { commentSymbolHook: CommentSymbolHook }
) => {
  const { symbolId, label, visible } = props.commentSymbolHook;
  const { commentSymbolHook, ...onlyHTMLAttributes } = props;

  return !(props.hidden ?? !visible) ? <div {...onlyHTMLAttributes}>{label}</div> : <></>;
};

export default CommentLabel;
