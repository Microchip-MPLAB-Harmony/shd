import { transceiver } from '../../txrx/Transceiver';

class ShortNamesApi {
  readonly path: string = 'ShortNames';

  generateShortNamesTemplate = async (componentId: string, symbolId: string): Promise<any> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'generateShortNamesTemplate',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.shortNames;
  };

  getResolvedShortNamesTemplate = async (fileName: string): Promise<any> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getResolvedShortNamesTemplate',
      data: {
        fileName
      }
    });
    return response.data.shortNames;
  };

  applyShortNames = async (
    componentId: string,
    symbolId: string,
    shortNames: any
  ): Promise<void> => {
    transceiver.send({
      path: this.path,
      method: 'applyShortNames',
      data: {
        componentId,
        symbolId,
        shortNames
      }
    });
    return;
  };
}

export const shortNamesApi = new ShortNamesApi();

export default ShortNamesApi;
