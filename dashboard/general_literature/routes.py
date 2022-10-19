import os
from flask import Blueprint, render_template, send_from_directory, send_file, request
from .index_query import search_index


basedir = os.path.dirname(__file__)
thumbnaildir = os.path.join(basedir, "thumbnails")


general_literature = Blueprint('general_literature', __name__)

@general_literature.route('/general_literature', methods=['GET'])
def main():

    # Query string keys
    qs_dict_keys = ['q','year_from','year_to','pages_from','pages_to','size_from','size_to']
    # Initializing objects
    # Create dict with the same value for all keys
    qs_dict = {k:'' for k in qs_dict_keys}
    hits = []
    pagination = {}

    if request.args.get('q'):
        for key in qs_dict.keys():
            qs_dict[key] = request.args.get(key)
        print(qs_dict)
        search_text = build_search_text(qs_dict)
        print(search_text)

        pagenum = request.args.get('page', 1, type=int)
        hits, pagination = search_index(search_text=search_text, pagenum=pagenum)

    return render_template('general_literature.html',
                            hits=hits, 
                            qs_dict=qs_dict,
                            pagination=pagination)


@general_literature.route('/thumbnails/<path:filename>')
def send_thumbnail(filename):
    return send_from_directory(thumbnaildir, filename)


@general_literature.route('/docs/<path:doc_path>')
def send_document(doc_path):
    if doc_path[:2] != r'\\':
        doc_path = '//' + doc_path

    return send_file(doc_path)


def build_search_text(qs_dict):
    search_list = []

    search_list.append(qs_dict['q'])
    if qs_dict['year_from'] or qs_dict['year_to']:
        search_list.append(f"date:[{qs_dict['year_from']}TO{qs_dict['year_to']}]")
    if qs_dict['pages_from'] or qs_dict['pages_to']:
        search_list.append(f"page_count:[{qs_dict['pages_from']}TO{qs_dict['pages_to']}]")
    if qs_dict['size_from'] or qs_dict['size_to']:
        search_list.append(f"file_size:[{qs_dict['size_from']}TO{qs_dict['size_to']}]")

    search_text = ' '.join(search_list)
    return search_text