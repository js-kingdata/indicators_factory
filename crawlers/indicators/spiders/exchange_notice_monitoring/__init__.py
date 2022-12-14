import html

from crawlers.utils import rds
from crawlers.utils.translate import UniversalTranslation


@rds.thing_lock('exchange_announcement')
def added_id_check(exchange_name, announcement_id):
    key = f'exchange_announcement:{exchange_name}'
    return rds.set_sismember_check(key, announcement_id)

def announcement_push(new_save, origin_url: str = None):
    new_save['title'], new_save['body'] = html.unescape(new_save['title']), html.unescape(new_save['body'])
    translation = UniversalTranslation()
    return {
        'template_id': 727,
        'origin_url': origin_url,
        'params': translation.dict_translation(
            data={
                'exchange_name': new_save['exchange'],
                'title': new_save['title'],
                'content': new_save['body'],
                'origin_url': origin_url,
            },
            need_translation_key=['title', 'content']
        )
    }

