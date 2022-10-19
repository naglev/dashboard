import os
from whoosh.qparser import QueryParser, PhrasePlugin, SequencePlugin
from whoosh.index import open_dir


def search_index(search_text, pagenum):

    basedir = os.path.dirname(__file__)
    indexdir = os.path.join(basedir, "indexing", "indexdir")

    ix = open_dir(indexdir)

    with ix.searcher() as searcher:

        qp = QueryParser("content", ix.schema)
        qp.remove_plugin_class(PhrasePlugin)
        qp.add_plugin(SequencePlugin())
        query = qp.parse(search_text)

        # print(query.normalize())

        # Get the paginated results
        result_page = searcher.search_page(query, pagenum=pagenum, pagelen=10)

        # Document hits to list
        hits = [hit.fields() for hit in result_page]

        # Values for pagination
        navbar = iter_pages(result_page.pagenum, result_page.pagecount)
        pagination = {
            "current_page": result_page.pagenum,
            "pagecount": result_page.pagecount,
            "pagelen": result_page.pagelen,
            "offset": result_page.offset,
            "total": result_page.total,
            "navbar": navbar
        }

    return (hits, pagination)


def iter_pages(pagenum, pagecount):
        """ Pagination """

        left_edge = 1
        right_edge = 1
        left_current = 1
        right_current = 2
        last = 0
        for num in range(1, pagecount + 1):
            if num <= left_edge or \
               (num > pagenum - left_current - 1 and
                num < pagenum + right_current) or \
               num > pagecount - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


if __name__ == '__main__':

    search_index('file_size:[50 TO 120]', 10)
