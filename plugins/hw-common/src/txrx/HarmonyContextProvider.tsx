import { ReactNode, useEffect, useRef } from 'react';
import EventAgent, { EventAgentContext } from './EventService';
import { PluginConfig, PluginConfigContext, pluginService } from '../plugin/PluginService';
import { transceiver } from './Transceiver';

function HarmonyContextProvider({ children }: { children: ReactNode }) {
  const eventAgent = useRef<EventAgent>(new EventAgent());
  const pluginConfig = useRef<PluginConfig>(pluginService.pluginConfig);

  useEffect(() => {
    transceiver.registerEventAgent(eventAgent.current);
    return () => {
      if (eventAgent.current) {
        eventAgent.current.destroy();
        transceiver.deregisterEventAgent(eventAgent.current);
      }
    };
  }, []);

  return (
    <EventAgentContext.Provider value={eventAgent.current}>
      <PluginConfigContext.Provider value={pluginConfig.current}>
        {children}
      </PluginConfigContext.Provider>
    </EventAgentContext.Provider>
  );
}

export default HarmonyContextProvider;
