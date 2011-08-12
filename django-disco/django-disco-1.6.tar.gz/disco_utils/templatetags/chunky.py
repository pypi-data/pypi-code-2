from native_tags.decorators import function

from disco_utils.models import Chunk


def chunk(slug):
    try:
        chunk = Chunk.objects.get(slug=slug)
        return chunk.text
    except Chunk.DoesNotExist:
        return ''
chunk.function = True
