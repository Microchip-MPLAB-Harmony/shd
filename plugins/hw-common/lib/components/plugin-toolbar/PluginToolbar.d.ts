import { MenuItem } from 'primereact/menuitem';
export type PluginToolbarProps = {
    menuItems: MenuItem[];
    title: string;
};
declare const PluginToolbar: ({ menuItems, title }: PluginToolbarProps) => JSX.Element;
export default PluginToolbar;
