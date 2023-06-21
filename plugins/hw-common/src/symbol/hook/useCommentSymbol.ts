import { useEffect, useRef, useState } from 'react';
import { commentSymbolApi } from '../api/CommentSymbolApi';
import { useContext } from 'react';
import { toSymbolVisibleListener } from '../../event/EventListenerFactory';
import { EventAgentContext } from '../../txrx/EventService';
import { EventFilter } from '../../event/EventInterfaces';
import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { SymbolProps } from '../api/SymbolApi';
import { Response } from '../../txrx/Transceiver';

const useCommentSymbol = ({ componentId, symbolId }: SymbolProps) => {
  const eventAgent = useContext(EventAgentContext);

  const [visible, setVisible] = useState(false);
  const [label, setLabel] = useState('');

  useEffect(() => {
    initFromDB();

    const visibilityListener = toSymbolVisibleListener(onSymbolVisualChanged, {
      componentId,
      symbolId
    } as EventFilter);
    eventAgent.addEventListener(visibilityListener);
    return () => {
      eventAgent.removeEventListener(visibilityListener);
    };
  }, []);

  const initFromDB = () => {
    commentSymbolApi.getCommentSymbol(componentId, symbolId).then(({ visible, label }) => {
      setVisible(visible);
      setLabel(label);
    });
  };

  const onSymbolVisualChanged = (event: Response) => {
    setLabel(event.data.symbol.label);
    setVisible(event.data.symbol.visible);
  };

  return {
    componentId,
    symbolId,
    visible,
    label
  } as CommentSymbolHook;
};

export interface CommentSymbolHook {
  componentId: string;
  symbolId: string;
  visible: boolean;
  label: string;
}

export default useCommentSymbol;
