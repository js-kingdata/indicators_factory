import html

from crawlers.utils.translate import UniversalTranslation


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

