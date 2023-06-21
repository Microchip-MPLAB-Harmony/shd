import { useState, useEffect, useRef, MouseEvent } from 'react';

type Point = {
  x: number;
  y: number;
};

interface PannableContainer {
  ref: React.RefObject<HTMLDivElement>;
  props: {
    onMouseDown: (e: MouseEvent<HTMLDivElement>) => void;
    onMouseMove: (e: MouseEvent<HTMLDivElement>) => void;
    onMouseUp: () => void;
    onMouseOut: () => void;
    style: React.CSSProperties;
  };
}

function usePannableContainer(): PannableContainer {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [isPanning, setIsPanning] = useState(false);
  const [startPoint, setStartPoint] = useState<Point>({ x: 0, y: 0 });
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.overflow = 'auto';
    }
  }, [containerRef]);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) return;

    // Check content is overflowing
    const isScrollbarVisible =
      container.scrollHeight > container.clientHeight ||
      container.scrollWidth > container.clientWidth;

    if (!isScrollbarVisible) {
      setIsPanning(false);
      setStartPoint({ x: 0, y: 0 });
    }
  }, [isPanning]);

  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    setIsPanning(true);
    const x = e.clientX + (containerRef.current?.scrollLeft || 0);
    const y = e.clientY + (containerRef.current?.scrollTop || 0);
    setStartPoint({ x, y });
  };

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!isPanning) return;
    const newX = startPoint.x - e.clientX;
    const newY = startPoint.y - e.clientY;

    containerRef.current?.scrollTo(newX, newY);
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  return {
    ref: containerRef,
    props: {
      onMouseDown: handleMouseDown,
      onMouseMove: handleMouseMove,
      onMouseUp: handleMouseUp,
      onMouseOut: handleMouseUp,
      style: {
        cursor: isPanning ? 'grabbing' : 'default'
      }
    }
  };
}

export default usePannableContainer;
