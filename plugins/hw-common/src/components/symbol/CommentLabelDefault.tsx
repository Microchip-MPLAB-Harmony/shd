import { HTMLAttributes } from 'react';
import { SymbolProps } from '../../symbol/api/SymbolApi';
import CommentLabel from './CommentLabel';
import { useCommentSymbol } from '../../symbol/hook';

const CommentLabelDefault = (props: SymbolProps & HTMLAttributes<HTMLDivElement>) => {
  const commentSymbolHook = useCommentSymbol(props);
  const { componentId, symbolId, ...onlyHTMLAttributes } = props;

  return (
    <CommentLabel
      commentSymbolHook={commentSymbolHook}
      {...onlyHTMLAttributes}
    />
  );
};

export default CommentLabelDefault;
