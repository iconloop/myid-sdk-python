import requests

from myid.vo.result_response import ResultResponse


class HttpUtil:
    @staticmethod
    def get(url: str) -> ResultResponse:
        try:
            with requests.Session() as session:
                response: requests.Response = session.get(url=url)
            return ResultResponse(status=(response.status_code == requests.codes.ok),
                                  result=response.json().get('result'))
        except Exception as e:
            return ResultResponse(status=False, result=str(e))

    @staticmethod
    def post(url: str, json: dict):
        try:
            with requests.Session() as session:
                response: requests.Response = session.post(url=url, json=json)
            return ResultResponse(status=(response.status_code == requests.codes.ok),
                                  result=response.json().get('result'))
        except Exception as e:
            return ResultResponse(status=False, result=str(e))
