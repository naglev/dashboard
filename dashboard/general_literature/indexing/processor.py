import os
import glob
import fitz
import hashlib
from langdetect import detect
from pdf2image import convert_from_path
from abc import ABCMeta, abstractmethod
import config_ix


class Processor(metaclass=ABCMeta):
    """_summary_"""

    @abstractmethod
    def extract_metadata(self):
        """
        file_name, page_count, file_size, creation_date
        """
        raise NotImplementedError

    @abstractmethod
    def extract_content(self):
        raise NotImplementedError

    @abstractmethod
    def save_cover_img(self):
        raise NotImplementedError

    def extract_file_data(self, path):
        file_name = os.path.basename(path).split('.')
        file_name.pop(-1)
        file_name = '.'.join(file_name)

        size_float = os.path.getsize(path)/(1024**2)    # megabytes
        return file_name, size_float

    @staticmethod
    def generate_hash(path):
        with open(path, 'rb') as file:
            binary_content = file.read()
            file_hash = hashlib.md5()
            file_hash.update(binary_content)
            return file_hash.hexdigest()
            
    def process_document(self, path):
        """_summary_"""

        document = Document(path)
        file_name, file_size, page_count, creation_date = self.extract_metadata(path)
        content, language = self.extract_content(path)
        document.add_metadata(file_name, file_size, page_count, creation_date)
        document.add_content(content, language)
        document.extension = self.type
        document.hash = self.generate_hash(path)
        if document.language in ['en','hu']:
            self.save_cover_img(path, document.hash)
        document.create_txt()
        return document


class ProcessorPDF(Processor):
    """_summary_"""

    type = 'PDF'

    def extract_metadata(self, path):
        file_name, file_size = self.extract_file_data(path)
        
        with fitz.open(path) as file:
            page_count = file.page_count

            date_raw = file.metadata['creationDate']
            if date_raw:
                creation_date = int(date_raw[2:6])
            else:
                creation_date = 0

        return file_name, file_size, page_count, creation_date

    def extract_content(self, path):
        with fitz.open(path) as file:
            content = ''
            for page in file:
                content += page.get_text('text')

        if len(content)>200:       # It is a non-scanned PDF
            # Detecting PDF language
            language = detect(content)
        else:                       # It is a scanned PDF
            language, content = self.process_scanned_pdf(path)

        return content, language

    @staticmethod
    def save_cover_img(path, file_name):
        convert_from_path(pdf_path=path,
                        dpi=50, fmt="png", 
                        thread_count=1, 
                        output_folder=config_ix.THUMBNAILDIR, 
                        output_file=file_name, 
                        single_file=True, 
                        grayscale=False, 
                        poppler_path=config_ix.POPPLER_PATH)
    
    def process_scanned_pdf(self, pdf_path):
        """_summary_"""

        from PIL import Image
        import concurrent.futures
        from pytesseract import pytesseract
        pytesseract.tesseract_cmd = config_ix.TESSERACT

        # PDF pages to images
        convert_from_path(pdf_path=pdf_path, 
                            dpi=300, fmt="png", 
                            thread_count=config_ix.MAX_WORKERS, 
                            output_folder=config_ix.WORKDIR, 
                            output_file="page", 
                            grayscale=True, 
                            poppler_path=config_ix.POPPLER_PATH)

        # List of images in workdir with folder name
        pdf_pages = glob.glob(os.path.join(config_ix.WORKDIR, '*'))
        # Detecting PDF language
        if len(pdf_pages) <= 6:
            lang_pages = pdf_pages
        else:
            middle = len(pdf_pages)//2
            lang_pages = pdf_pages[middle-3 : middle+3]

        lang_text = ''
        for lang_page in lang_pages:
            # Language 'hun' because this way unicode characters can be recognized
            lang_page_text = pytesseract.image_to_string(lang_page, lang='hun')
            lang_text += lang_page_text
        language = detect(lang_text)

        language_eq = {
            'en': 'eng',
            'hu': 'hun',
            'de': 'deu'
        }

        # TODO Ide kell egy break, ha language nincs a dictionary kulcsok között return None, None
        if language not in language_eq.keys():
            self.empty_workdir()
            return language, str()

        # Content of the images to a string variable
        text_per_page = {}  # eg. {'page08': 'text', 'page04': 'text', ...}

        # Function for multithreading
        def process_image(image_path):
            page = Image.open(image_path)
            page_text = pytesseract.image_to_string(page, lang=language_eq[language])
            page_name_full = os.path.basename(image_path)
            page_name = page_name_full.split('.')[0]    # image name without extension
            text_per_page[page_name] = page_text

        # Run process_image PARALLEL
        with concurrent.futures.ThreadPoolExecutor(max_workers=config_ix.MAX_WORKERS) as executor:
            executor.map(process_image, pdf_pages)

        # Sort the dict because items not in order due to parallel execution; gives back a list of tuples
        sorted_dict = sorted(text_per_page.items())
        # Read all texts in text_per_page dictionary into a variable and update the output dictionary with content
        extracted_text = ''
        for page, text in sorted_dict:
            extracted_text = ' '.join([extracted_text, text])
        content = extracted_text

        self.empty_workdir()

        return language, content

    @staticmethod
    def empty_workdir():
        # Delete all files in working directory
        del_files = glob.glob(os.path.join(config_ix.WORKDIR, '*'))
        for del_file in del_files:
            os.remove(del_file)



class ProcessorPPT(Processor):
    """_summary_"""

    type = 'PPTX'


class ProcessorDOC(Processor):
    """_summary_"""

    type = 'DOCX'


class Document:
    """_summary_"""

    def __init__(self, path):
        self.path = path
        self.file_name = None
        self.file_size = None
        self.extension = None         
        self.creation_date = str()
        self.page_count = None
        self.language = None
        self.hash = None
        self.content = None

    def add_metadata(self, file_name, file_size, page_count, creation_date):
        self.page_count = page_count
        self.creation_date = creation_date
        self.file_name = file_name
        self.file_size = file_size

    def add_content(self, content, language):
        self.content = content
        self.language = language

    def create_txt(self):
        """ This method only required during testing """

        with open(f"txts/{self.file_name}.txt",'w', encoding='utf-8') as test_txt:
            lst = [self.file_name,
                    self.path,
                    str(self.file_size),
                    self.extension,
                    str(self.page_count),
                    self.language, 
                    str(self.creation_date),
                    self.hash,
                    self.content]

            test_txt.write('\n'.join(lst))



if __name__ == '__main__':
    path = r"C:\Users\ext-nagyle\Documents\Programming\Search_engine\misc_english_pdfs\search_engine\abc\5pages_eng.pdf"
    processor = ProcessorPDF()
    document = processor.process_document(path)

    # 5/11/2005 14:12:16 'str'
    # D:20110421211818-04'00' 'str'
    # Wednesday, September 22, 1999   8:40 PM GMT 'str'
