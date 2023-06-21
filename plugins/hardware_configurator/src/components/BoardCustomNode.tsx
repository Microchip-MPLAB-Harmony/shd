import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';

import './components.css';

const BoardCustomNode = ({ data, isConnectable }) => {
  return (
    <div id='divCustomNode'>
      <div>{data.title}</div>
      <Handle
        id='rt0'
        type='source'
        position={Position.Right}
        style={{ top: 10, background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='rb0'
        type='source'
        position={Position.Right}
        style={{ bottom: 20, top: 'auto', background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='rb1'
        type='source'
        position={Position.Right}
        style={{ bottom: 10, top: 'auto', background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='rb2'
        type='source'
        position={Position.Right}
        style={{ bottom: 20, top: 'auto', background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='rb3'
        type='source'
        position={Position.Right}
        style={{ bottom: 30, top: 'auto', background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='rb4'
        type='source'
        position={Position.Right}
        style={{ bottom: 40, top: 'auto', background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='rb5'
        type='source'
        position={Position.Right}
        style={{ bottom: 50, top: 'auto', background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='bl0'
        type='source'
        position={Position.Bottom}
        style={{ left: 30, background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='bl1'
        type='source'
        position={Position.Bottom}
        style={{ left: 40, background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='br0'
        type='source'
        position={Position.Bottom}
        style={{ left: 50, background: '#555' }}
        isConnectable={isConnectable}
      />
      <Handle
        id='br1'
        type='source'
        position={Position.Bottom}
        style={{ left: 60, background: '#555' }}
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default memo(BoardCustomNode);
