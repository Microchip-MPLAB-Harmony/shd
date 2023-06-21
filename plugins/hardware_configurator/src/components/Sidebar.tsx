import { useEffect, useState } from 'react';
import './Sidebar.css';

import { pluginSHDService } from '../service/PluginSHDService';
import { info } from '@mplab_harmony/harmony-plugin-core-service';

const Likes = () => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (count === 0) return;
    console.log('useEffect - Counter: ', count);
  }, [count]);

  return (
    <div>
      <h1>{count}</h1>
      <button onClick={() => setCount(count + 1)}>{count} likes</button>
    </div>
  );
};

const BoardComponentList = () => {
  const onDragStart = (event, nodeData) => {
    const stringNodeData = JSON.stringify(nodeData);

    info('BoardComponentList stringNodeData: ' + stringNodeData);

    event.dataTransfer.setData('application/reactflow', stringNodeData);
    event.dataTransfer.effectAllowed = 'move';
  };

  const [mainBoardList, setMainBoardList] = useState(pluginSHDService.mainBoardNames);
  const [clickBoardList, setClickBoardList] = useState(pluginSHDService.clickBoardNames);

  useEffect(() => {
    info('Main Board List: ');
    mainBoardList.forEach(function (mainBoard, index) {
      info(mainBoard);
    });
    info('Click Board List: ');
    clickBoardList.forEach(function (clickBoard, index) {
      info(clickBoard);
    });
  }, []);

  const nodeMainBoardList = mainBoardList.map((mainBoardName) => {
    const nodeData = { name: mainBoardName, type: 'boardSelectorNode' };
    return (
      <div
        className='boardnode'
        onDragStart={(event) => onDragStart(event, nodeData)}
        draggable>
        {mainBoardName}
      </div>
    );
  });

  const nodeClickBoardList = clickBoardList.map((clickBoardName) => {
    const nodeData = { name: clickBoardName, type: 'boardSelectorNode' };
    return (
      <div
        className='boardnode'
        onDragStart={(event) => onDragStart(event, nodeData)}
        draggable>
        {clickBoardName}
      </div>
    );
  });

  return (
    <>
      {nodeMainBoardList}
      {nodeClickBoardList}
    </>
  );
};

export default () => {
  return (
    <aside>
      {/* <Likes /> */}
      <div className='description'>You can drag these nodes to the panel on the right.</div>
      <BoardComponentList />
    </aside>
  );
};
