/*******************************************************************************
 * Copyright (C) 2024 Microchip Technology Inc. and its subsidiaries.
 *
 * Subject to your compliance with these terms, you may use Microchip software
 * and any derivatives exclusively with Microchip products. It is your
 * responsibility to comply with third party license terms applicable to your
 * use of third party software (including open source software) that may
 * accompany Microchip software.
 *
 * THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
 * EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
 * WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
 * PARTICULAR PURPOSE.
 *
 * IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
 * INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
 * WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
 * BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
 * FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
 * ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
 * THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
 *******************************************************************************/
import { info } from '@mplab_harmony/harmony-plugin-core-service/build/log/CustomConsole';
import ShdConfig from './ShdConfig';
import YAML from 'yaml';

export class PluginSHDService {
  private readonly pluginConfig: any;
  private readonly _initArgs: Map<string, object>;
  private _shdConfig!: ShdConfig;
  private _mainBoardConfig: any[];
  private _clickBoardConfig: any[];

  constructor() {
    this.pluginConfig = (window as any).pluginConfig;

    try {
      this._initArgs = this.pluginConfig.initArgs();
    } catch (errr) {
      info('PlugIn DBG -> init args error : ' + errr);
      this._initArgs = new Map();
      return;
    }

    const symbolConfigSHD = YAML.parse(YAML.stringify(this.initArgs.get('shd_config'))) as string;
    this._shdConfig = this.readYAML(this.absolutePath(symbolConfigSHD)) as ShdConfig;

    this.printSHDConfig();

    this._mainBoardConfig = this._shdConfig.mainboards.map((mainBoardPath) =>
      this.readYAML(this.absoluteBoardPath(mainBoardPath))
    );

    this._clickBoardConfig = this._shdConfig.clickboards.map((clickBoardPath) =>
      this.readYAML(this.absoluteBoardPath(clickBoardPath))
    );
  }

  private printSHDConfig(): void {
    info('PlugIn DBG -> SHD Mainboards config : ' + YAML.stringify(this._shdConfig.mainboards));
    info('PlugIn DBG -> SHD Clickboards config : ' + YAML.stringify(this._shdConfig.clickboards));
  }

  private readYAML(path: string): object {
    const request = new XMLHttpRequest();
    request.open('GET', path, false);
    request.send(null);

    if (request.status === 200) {
      return YAML.parse(request.responseText);
    } else {
      throw new Error('Unable to read url : ' + path);
    }
  }

  public absolutePath(relativePath: string): string {
    return this.frameworkRoot() + '/' + relativePath;
  }

  public absoluteBoardPath(relativeBoardPath: string): string {
    return this.frameworkRoot() + '/shd/' + relativeBoardPath;
  }

  public frameworkRoot(): string {
    const { protocol, host } = document.location;
    return protocol + '//' + host;
  }

  get shdConfig(): ShdConfig {
    return this._shdConfig;
  }

  get mainBoards(): string[] {
    return this._shdConfig.mainboards;
  }

  get mainBoardNames(): string[] {
    const nameList = this._mainBoardConfig.map((config) => config.name.toUpperCase());
    return nameList;
  }

  get clickBoards(): string[] {
    return this._shdConfig.clickboards;
  }

  get clickBoardNames(): string[] {
    const nameList = this._clickBoardConfig.map((config) => config.name.toUpperCase());
    return nameList;
  }

  get initArgs(): Map<string, object> {
    return this._initArgs;
  }
}

export const pluginSHDService = new PluginSHDService();
