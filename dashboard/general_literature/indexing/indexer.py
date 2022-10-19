import os
import config_ix
import time
from processor import Processor, ProcessorPDF, ProcessorPPT, ProcessorDOC
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, STORED, NUMERIC
from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer
from whoosh.qparser import QueryParser


class Indexer:
    """Docstring"""

    def __init__(self):
        self.processors = {
            'PDF': ProcessorPDF(),
            # 'PPTX': ProcessorPPT(),
            # 'DOCX': ProcessorDOC()
        }
        
        self.indexes = {
            'en': self.create_index('en'),
            'hu': self.create_index('hu')
        }

        self.writers = {lang:index.writer() for (lang,index) in self.indexes.items()}

        self._new_hashes = set()     # Required for duplicate searching
        self._deleted_hashes = set()    # Required for tracking file moves

        if self.new_indexing == False:
            self.check_indexes()

    def index_document(self, path):
        """Docstring"""

        if self.in_index(path) == True:
            return

        extension = os.path.basename(path).split('.')[-1].upper()
        processor = self.processors.get(extension)

        try: 
            document = processor.process_document(path)
        except Exception as e:
            with open('error.txt', 'a') as error_txt:
                error_txt.write(f"{path}\n{str(e)}\n\n")
            ProcessorPDF.empty_workdir()
            return
        
        writer = self.writers.get(document.language, None)
        if writer is None:
            return

        writer.add_document(file_name=document.file_name,
                            path=document.path,
                            date=document.creation_date,
                            language=document.language,
                            page_count=document.page_count,
                            file_size=document.file_size,
                            hash = document.hash,
                            content=document.content)

    def commit(self):
        print("\nCommiting changes...")
        for writer in self.writers.values():
            writer.commit()

    def create_index(self, language):
        schema = self.get_schema(language)
        indexdir = config_ix.INDEXDIR

        if exists_in(indexdir, indexname=language):
            whoosh_indexer = open_dir(indexdir, schema=schema, indexname=language)
            self.new_indexing = False
        else:
            whoosh_indexer = create_in(indexdir, schema=schema, indexname=language)
            self.new_indexing = True
        
        return whoosh_indexer

    def get_schema(self, language):
        analyzers = {
            'en': StemmingAnalyzer(),
            'hu': StandardAnalyzer(),
        }

        # TODO ide még az extensiont
        schema = Schema(file_name=TEXT(stored=True), 
                    path=ID(stored=True),
                    date=NUMERIC(stored=True, sortable=True),
                    language=STORED(),
                    page_count=NUMERIC(stored=True, sortable=True),
                    file_size=NUMERIC(stored=True, sortable=True),
                    hash=TEXT(stored=True),
                    content=TEXT(analyzer=analyzers[language]))

        return schema

    def in_index(self, path):
        file_hash = Processor.generate_hash(path)
        in_index = False

        if file_hash in self._new_hashes:
            in_index = True
        elif self.new_indexing == False:
            for language in self.indexes.keys():
                hits = self.search_index(language, 'hash', file_hash)
                if len(hits) == 1:
                    in_index = True

        if file_hash in self._deleted_hashes:
            in_index = False
            if file_hash in self._new_hashes:
                in_index = True

        if in_index == False:
            self._new_hashes.add(file_hash)

        return in_index

    def search_index(self, language, field, search_term):
        schema = self.indexes[language].schema
        qp = QueryParser(field, schema=schema)
        query = qp.parse(search_term)
        with self.indexes[language].searcher() as searcher:
            hits = searcher.search(query)
        return hits

    def check_indexes(self):
        """Looking for documents that has been deleted/moved 
        from the indexed path and delete them.
        """

        print("Checking indexes...\n")

        for language in self.indexes.keys():
            with self.indexes[language].searcher() as searcher:
                for fields in searcher.all_stored_fields():
                    indexed_path = fields['path']
                    if not os.path.exists(indexed_path):
                        hash = fields['hash']
                        self.writers[language].delete_by_term('path', indexed_path)
                        self._deleted_hashes.add(hash)
                        thumbnail = os.path.join(config_ix.THUMBNAILDIR, hash)
                        os.remove(f'{thumbnail}.png')

        print(f'Deleted hashes: {self._deleted_hashes}\n')


def main(root_folder):
    if not isinstance(root_folder, (str, int, bytes)):
        raise TypeError("Root folder should be string, bytes or integer.")
    if not os.path.exists(root_folder):
        raise FileNotFoundError("Given root folder does not exist.")

    # Itt legyen a logika: preprocess (duplikátumok keresése)
    print("\nIndexing started...\n")
    indexer = Indexer()

    for (root,dirs,files) in os.walk(root_folder):
        for name in files:
            path = os.path.join(root,name)
            extension = os.path.basename(path).split('.')[-1]
            if extension.upper() in ['PDF']:
                print(path)
                indexer.index_document(path)
    indexer.commit()


if __name__ == '__main__':
    
    t1 = time.perf_counter()

    root_folder = r"C:\Users\ext-nagyle\Documents\Programming\Search_engine\misc_english_pdfs\search_engine\corpus"
    main(root_folder)

    t2 = time.perf_counter()
    print(f"\nElapsed time: {t2-t1:.4f} secs")

    # indexer = Indexer()
    # indexer.index_document(r"C:\Users\ext-nagyle\Documents\Programming\Search_engine\Analytical mechanics - Hand, Finch.pdf")
    # indexer.commit()