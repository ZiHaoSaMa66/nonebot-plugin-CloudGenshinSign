import httpx
from typing import Dict, Optional, Any, Union, Tuple
from pathlib import Path
from PIL import Image
from io import BytesIO
from ssl import SSLCertVerificationError

class aiorequests:
    @staticmethod
    async def get(url: str,
                  *,
                  headers: Optional[Dict[str, str]] = None,
                  params: Optional[Dict[str, Any]] = None,
                  timeout: Optional[int] = 20,
                  **kwargs) -> httpx.Response:
        """
        说明：
            httpx的get请求封装
        参数：
            :param url: url
            :param headers: 请求头
            :param params: params
            :param timeout: 超时时间
        """
        async with httpx.AsyncClient() as client:
            return await client.get(url,
                                    headers=headers,
                                    params=params,
                                    timeout=timeout,
                                    **kwargs)

    @staticmethod
    async def post(url: str,
                   *,
                   headers: Optional[Dict[str, str]] = None,
                   params: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None,
                   json: Optional[Dict[str, Union[Any, str]]] = None,
                   timeout: Optional[int] = 20,
                   **kwargs) -> httpx.Response:
        """
        说明：
            httpx的post请求封装
        参数：
            :param url: url
            :param headers: 请求头
            :param params: params
            :param data: data
            :param json: json
            :param timeout: 超时时间
        """
        async with httpx.AsyncClient() as client:
            return await client.post(url,
                                     headers=headers,
                                     params=params,
                                     data=data,
                                     json=json,
                                     timeout=timeout,
                                     **kwargs)

    @staticmethod
    async def get_img(url: str,
                      *,
                      headers: Optional[Dict[str, str]] = None,
                      params: Optional[Dict[str, Any]] = None,
                      timeout: Optional[int] = 20,
                      save_path: Optional[Union[str, Path]] = None,
                      size: Optional[Union[Tuple[int, int], float]] = None,
                      mode: Optional[str] = None,
                      crop: Optional[Tuple[int, int, int, int]] = None,
                      **kwargs) -> Union[None, Image.Image]:
        """
        说明：
            httpx的get请求封装，获取图片
        参数：
            :param url: url
            :param headers: 请求头
            :param params: params
            :param timeout: 超时时间
            :param save_path: 保存路径，为空则不保存
            :param size: 图片尺寸，为空则不做修改
            :param mode: 图片模式，为空则不做修改
            :param crop: 图片裁剪，为空则不做修改
        """
        if save_path and Path(save_path).exists():
            img = Image.open(save_path)
        else:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url,
                                            headers=headers,
                                            params=params,
                                            timeout=timeout,
                                            **kwargs)
                    # 不保存安柏计划的问号图标
                    if resp.headers.get('etag') == 'W/"6363798a-13c7"' or resp.headers.get(
                            'content-md5') == 'JeG5b/z8SpViMmO/E9eayA==':
                        # save_path = False
                        return None
                    if resp.headers.get('Content-Type') not in ['image/png', 'image/jpeg']:
                        # return 'No Such File'
                        return None
                    resp = resp.read()
                    img = Image.open(BytesIO(resp))
            except SSLCertVerificationError:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url.replace('https', 'http'),
                                            headers=headers,
                                            params=params,
                                            timeout=timeout,
                                            **kwargs)
                    if resp.headers.get('etag') == 'W/"6363798a-13c7"' or resp.headers.get(
                            'content-md5') == 'JeG5b/z8SpViMmO/E9eayA==':
                        # save_path = False
                        return None
                    if resp.headers.get('Content-Type') not in ['image/png', 'image/jpeg']:
                        # return 'No Such File'
                        return None
                    resp = resp.read()
                    img = Image.open(BytesIO(resp))
        if size:
            if isinstance(size, float):
                img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.LANCZOS)
            elif isinstance(size, tuple):
                img = img.resize(size, Image.LANCZOS)
        if mode:
            img = img.convert(mode)
        if crop:
            img = img.crop(crop)
        if save_path and not Path(save_path).exists():
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path)
        return img
