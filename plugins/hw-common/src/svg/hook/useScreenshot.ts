import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { useEffect, useRef, useState, WheelEvent, MouseEvent } from 'react';
import domtoimage from 'dom-to-image-more';

interface ScreenshotContainer {
  ref: React.MutableRefObject<HTMLDivElement | null>;
  copyAsBlob: () => Promise<void>;
  copyAsPng: () => Promise<void>;
  copyAsSvg: () => Promise<void>;
  downloadAsSvg: (fileName: string) => Promise<void>;
}

function useScreehshot(): ScreenshotContainer {
  const containerRef = useRef<HTMLDivElement | null>(null);

  async function getHtmlElement(imageType: 'png' | 'svg' | 'blob'): Promise<any> {
    if (!containerRef.current) return;

    const divElement = containerRef.current;

    const prevTransform = divElement.style.transform;

    divElement.style.transform = '';

    let elementScreenshot = null;

    switch (imageType) {
      case 'png': {
        elementScreenshot = await domtoimage.toPng(divElement);
        break;
      }
      case 'svg': {
        elementScreenshot = await domtoimage.toSvg(divElement);
        break;
      }
      case 'blob': {
        elementScreenshot = await domtoimage.toBlob(divElement);
        break;
      }
    }
    divElement.style.transform = prevTransform;
    // log('Blob Type : ' + JSON.stringify(Object.keys(elementScreenshot)));
    return elementScreenshot;

    // return domtoimage
    //   .toBlob(divElement, {
    //     style: {
    //       transform: 'scale(1)'
    //     }
    //   })
    //   .then((blob: any) => {
    //     divElement.style.transform = prevTransform;
    //     return blob;
    //   });
  }

  function downloadAsSvg(fileName: string) {
    return getHtmlElement('svg')
      .then((blob: any) => {
        const link = document.createElement('a');
        link.href = blob;
        link.download = fileName.endsWith('.svg') ? fileName : `${fileName}.svg`;
        link.click();
      })
      .then((e) => window.location.reload());
  }

  function copyAsBlob() {
    return getHtmlElement('blob')
      .then((blob: any) =>
        navigator.clipboard.write([
          new ClipboardItem({
            [blob.type]: blob
          })
        ])
      )
      .then((e) => window.location.reload());
  }

  function copyAsPng() {
    return getHtmlElement('blob')
      .then((blob: any) =>
        navigator.clipboard.write([
          new ClipboardItem({
            [blob.type]: blob
          })
        ])
      )
      .then((e) => window.location.reload());
  }

  function copyAsSvg() {
    return getHtmlElement('svg')
      .then((blob: any) => navigator.clipboard.writeText(blob))
      .then((e) => window.location.reload());
  }

  // function captureAndSave(imageName: string) {
  //   getHtmlElementBlob()
  //     .then((blob: any) => {
  //       (window as any).saveAs(blob, imageName);
  //     })
  //     .then((e) => window.location.reload());
  // }

  return {
    ref: containerRef,
    copyAsBlob,
    copyAsPng,
    copyAsSvg,
    downloadAsSvg
  };
}

export default useScreehshot;
