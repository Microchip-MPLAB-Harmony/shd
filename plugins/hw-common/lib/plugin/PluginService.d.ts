import React from 'react';
declare class PluginConfig {
    readonly pluginId: string;
    readonly initArgs: any;
    readonly componentId?: string;
    constructor(pluginId: string, initArgs: any);
}
declare class PluginService {
    private readonly _pluginConfig;
    constructor();
    private readJSONAsync;
    absolutePath(relativePath: string): string;
    frameworkRoot(): string;
    private readJSON;
    get pluginConfig(): PluginConfig;
}
declare const pluginService: PluginService;
declare const PluginConfigContext: React.Context<PluginConfig>;
export { PluginService, pluginService, PluginConfig, PluginConfigContext };
