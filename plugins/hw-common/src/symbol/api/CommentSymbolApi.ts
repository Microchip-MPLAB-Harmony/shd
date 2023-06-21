import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { transceiver } from '../../txrx/Transceiver';
import VisibleSymbolApi, { VisibleSymbol } from './VisibleSymbolApi';

interface CommentSymbol extends VisibleSymbol {
  label: string;
}

class CommentSymbolApi extends VisibleSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'CommentSymbol';
  }

  getLabel = async (componentId: string, symbolId: string): Promise<string> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getLabel',
      data: {
        componentId,
        symbolId,
      },
    });
    return response.data.label;
  };

  getCommentSymbol = async (
    componentId: string,
    symbolId: string
  ): Promise<CommentSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getCommentSymbol',
      data: {
        componentId,
        symbolId,
      },
    });
    return response.data as CommentSymbol;
  };
}

export const commentSymbolApi = new CommentSymbolApi();

export { CommentSymbol };

export default CommentSymbolApi;
