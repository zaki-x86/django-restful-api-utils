

__all__ = ['Linker']

class Linker:
    @staticmethod
    def self_link(request, *args, **kwds):
        return {
            'href': request.build_absolute_uri()
        }