import {Position} from 'reactflow';

const DefaultNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Input Node' },
    position: { x: 250, y: 25 },
    style: { backgroundColor: '#6ede87', color: 'white' },
    sourcePosition: Position.Right,
  },
  {
    id: '2',
    // you can also pass a React component as a label
    data: { label: 'Middle Node' },
    position: { x: 100, y: 125 },
    style: { backgroundColor: '#ff0072', color: 'white' },
  },
  {
    id: '3',
    type: 'output',
    data: { label: 'Output Node' },
    position: { x: 250, y: 250 },
    style: { backgroundColor: '#6865A5', color: 'white' },
    targetPosition: Position.Left,
  },
  {
    id: '4',
    height: 300,
    type: 'selectorNode',
    data: { color: 'LightBlue' },
    style: { border: '1px solid #777', padding: 10 },
    position: { x: 300, y: 50 }
  }
];
  
export default DefaultNodes; 