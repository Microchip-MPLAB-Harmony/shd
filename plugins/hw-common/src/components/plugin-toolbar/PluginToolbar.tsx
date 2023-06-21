import { Button } from 'primereact/button';
import { MenuItem } from 'primereact/menuitem';
import { SlideMenu } from 'primereact/slidemenu';
import { useRef } from 'react';

export type PluginToolbarProps = {
  menuItems: MenuItem[];
  title: string;
};

const PluginToolbar = ({ menuItems, title }: PluginToolbarProps) => {
  const menu = useRef<SlideMenu>(null);
  return (
    <div
      style={{
        height: '45px',
        padding: '0 15px 0 15px',
        backgroundColor: '#f0f2f3',
        borderBottom: '1px solid rgb(200, 200, 200)',
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        columnGap: '10px'
      }}>
      <SlideMenu
        className='p-menuitem-icon'
        style={{ width: 190 }}
        menuWidth={190}
        ref={menu}
        model={menuItems}
        popup></SlideMenu>
      <Button
        className='p-button-outlined p-button-lg p-button-primary'
        icon='pi pi-bars'
        onClick={(event) => {
          menu.current?.toggle(event);
        }}></Button>

      <label
        style={{
          fontWeight: '500',
          fontSize: '1.5rem',
          whiteSpace: 'nowrap'
        }}>
        {title}
      </label>
    </div>
  );
};

export default PluginToolbar;
