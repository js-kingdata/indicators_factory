import functools
import traceback
import time
from logging import DEBUG
import requests

def catch_except(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            error_info = traceback.format_exc()
            if DEBUG:
                print(error_info)
    return wrapper


def send_feishu_group(token, data):
    requests.post(
        url=f'https://open.feishu.cn/open-apis/bot/v2/hook/{token}',
        json=data
    )

enter = '\n'

def information_flow_synchronization(tmp_name, chart_id, params, origin_url, start=True):
    """
    信息流推送飞书群同步
    :param chart_id: 模板ID
    :param tmp_name: 模板名称
    :param params: 信息
    :param origin_url:原文链接
    :param start:推送状态
    :return:None
    """
    data = {
        "msg_type": "interactive",
        "card": {
            "elements": [
                {
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**📅 消息推送时间：{'' if start else '<at id=all>'}**\n{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**📄 模板ID：**\n{tmp_name}({chart_id})",
                                "tag": "lark_md"
                            }
                        }
                    ],
                    "tag": "div"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"</at>**🇨🇳 中文数据：**\n{enter.join([f'**{k}**:{v}' for k, v in params.get('cn', params).items()])}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**🇬🇧 English data：**\n{enter.join([f'**{k}**:{v}' for k, v in params.get('en', params).items()])}"
                            }
                        }
                    ]
                }
            ],
            "header": {
                "template": "green" if start else 'red',
                "title": {
                    "content": f"{'✅ 【爬虫】消息推送成功' if start else '❌ 【爬虫】消息推送失败'}！",
                    "tag": "plain_text"
                }
            }
        }
    }
    if origin_url:
        data['card']['elements'].extend([
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"原文链接：{origin_url}"
                },
                "extra": {
                    "tag": "button",
                    "text": {
                        "tag": "lark_md",
                        "content": "点击查看"
                    },
                    "type": "primary",
                    "url": origin_url
                }
            }])
    send_feishu_group('5a09573d-4d73-4f61-a056-55885f773eee', data)

