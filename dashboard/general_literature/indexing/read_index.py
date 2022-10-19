from whoosh import index

ix = index.open_dir('indexdir', indexname='en')

with ix.searcher() as searcher:
    for fields in searcher.all_stored_fields():
        print(fields['file_name'], fields['language'])


ix = index.open_dir('indexdir', indexname='hu')

with ix.searcher() as searcher:
    for fields in searcher.all_stored_fields():
        print(fields['file_name'], fields['language'])