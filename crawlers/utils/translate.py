import requests
import langid

from crawlers.config import DEEPL_AUTO_KEY
"""
翻译工具：DEEPL官方接口

"""

platforms = {
    'deepl': {'en': 'EN', 'cn': 'ZH'},
    # 'google': {'en': '', 'cn': ''},
    # 'baidu': {'en': '', 'cn': ''},
}


def translation_check(platform):
    """
    翻译原文语言校验：如果需要的语言与原文相同则不翻译，反之依然。
    :param platform:原文
    :return:
    """

    def outer(func):
        def wrapper(*args, **kwargs):
            if langid.classify(kwargs['text'])[0] == kwargs['to_language']:
                return kwargs['text']
            kwargs['to_language'] = platforms[platform][kwargs['to_language']]
            return func(*args, **kwargs)

        return wrapper

    return outer


class UniversalTranslation:
    def __init__(self, platform: str = None):
        self.platform = platform
        if platform not in platforms:
            self.platform = list(platforms)[0]
        self.__language_tag = platforms[self.platform]

    def dict_translation(self, data: dict, need_translation_key, languages: list = None):
        """
        对字典指定的多个key进行多语言翻译
        :param data: 原字典
        :param need_translation_key: 需要翻译的key
        :param languages:需要的语言类型
        :return: 例：{'en':{}, 'cn': {},...}
        """
        if languages is None:
            languages = ['en', 'cn']
        return {
            language: {
                key: getattr(self, f'{self.platform}_translation')(text=v, to_language=language)
                if key in need_translation_key else v
                for key, v in data.items()
            } for language in languages
        }

    @translation_check('deepl')
    def deepl_translation(self, text: str = '', to_language: str = '', text_language=''):
        response = requests.get(
            'https://api.deepl.com/v2/translate',
            params={
                "auth_key": DEEPL_AUTO_KEY,
                "target_lang": to_language,
                "text": text[:4000],
            }
        )
        if response.status_code == 200:
            return response.json()["translations"][0]["text"]
        return text
