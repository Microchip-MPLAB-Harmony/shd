import {
  SetComponentId,
  clearSymbol,
  UpdateSymbolValue
} from '@mplab_harmony/harmony-plugin-core-service/build/database-access/SymbolAccess';
import { globalSymbolSStateData } from '@mplab_harmony/harmony-plugin-ui/build/components/Components';
import { convertToBoolean } from '@mplab_harmony/harmony-plugin-ui/build/utils/CommonUtil';

import {
  ChangeClassNameState,
  ChangeComponentState
} from '@mplab_harmony/harmony-plugin-ui/build/utils/ComponentStateChangeUtils';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Controls,
  Background,
  BackgroundVariant,
  Panel,
  useNodesState,
  useEdgesState,
  addEdge,
  Position,
  SmoothStepEdge
} from 'reactflow';

import { log, info } from '@mplab_harmony/harmony-plugin-core-service';

import Sidebar from '../components/Sidebar';

import BoardCustomNode from '../components/BoardCustomNode';

import { pluginSHDService } from '../service/PluginSHDService';

import 'reactflow/dist/style.css';
import './MainBlock.css';
import { string } from 'yaml/dist/schema/common/string';

let id = 0;
const getId = () => `board_${id++}`;

const nodeTypes = {
  boardSelectorNode: BoardCustomNode
};

const MainBlock = () => {
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const initBgColor = 'LightGrey';
  const [bgColor, setBgColor] = useState(initBgColor);

  const boardList = pluginSHDService.initArgs;

  const onConnect = useCallback(
    (connection) =>
      setEdges((eds) => addEdge({ ...connection, animated: false, type: 'smoothstep' }, eds)),
    [setEdges]
  );

  useEffect(() => {
    info('Nodes: ' + nodes);
  }, []);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const stringNodeData = event.dataTransfer.getData('application/reactflow');
      const nodeData = JSON.parse(stringNodeData);

      // check if the dropped element is valid
      if (typeof nodeData.type === 'undefined' || !nodeData.type) {
        return;
      }

      // reactFlowInstance.project was renamed to reactFlowInstance.screenToFlowPosition
      // and you don't need to subtract the reactFlowBounds.left/top anymore
      // details: https://reactflow.dev/whats-new/2023-11-10
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY
      });

      const newNode = {
        id: getId(),
        type: nodeData.type,
        position,
        data: { title: `${nodeData.name}` }
      };

      info('onDrop newNode: ' + JSON.stringify(newNode));

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance]
  );

  return (
    <div>
      <div className='main_view'>
        <ReactFlowProvider>
          <div className='contentbox'>
            <Sidebar />
            <div
              className='reactflow-wrapper'
              ref={reactFlowWrapper}
              style={{ width: '50vw', height: '100vh' }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onInit={setReactFlowInstance}
                onDrop={onDrop}
                onDragOver={onDragOver}
                style={{ background: bgColor }}
                nodeTypes={nodeTypes}
                fitView>
                <Controls />
                <Background
                  variant={BackgroundVariant.Dots}
                  gap={10}
                  size={1}
                />
                <Panel position='top-right'>
                  <div>
                    <button>Button 1</button>
                    <button>Button 2</button>
                    <button>Button 3</button>
                  </div>
                </Panel>
              </ReactFlow>
            </div>
          </div>
        </ReactFlowProvider>
      </div>
    </div>
  );
};

export default MainBlock;
