# dashboard

This is a public version of the project, hence the lack of commits.
## About the project
A website that is meant to make engineers’ daily work easier. It serves as a collection of engineering tools. Currently it contains two pages: License status, General literature, (Home).

Languages, libraries and frameworks used for
* Frontend: HTML, CSS, jQuery, Bootstrap
* Backend: Python, Flask, Whoosh

## General literature
There is a large collection (20,000+) of documents (books, articles, documentations etc.) on a server in a complex folder structure. They differ not only in file type but also in language. As this collection grows it becomes less useable because the users have to browse numerous folders until they find relevant document(s). General literature delivers a solution for this problem which is based on a search engine and provides full-text search.

![General literature](media/general_literature_1000x1000.png)

This application can be split into three main parts by functionality:
* Indexer
* Index (database)
* Index query

### Indexer
The <code>indexer.py</code> and the <code>processor.py</code> are responsible for processing the documents, creating the language dependent indexes and maintaining the indexes automatically. In order to run the program the user needs to enter the path of a root directory whose documents need to be indexed and then use a task scheduler to execute indexer.py periodically.
Features of the Indexer:
-	Handles duplicates so documents can only appear once in the database
-	Detects the language of the documents and sorts them accordingly
-	Currently one file type (pdf) and two languages are handled (English, Hungarian), but the list can be easily extended due to the modular structure of the Indexer
-	Can process scanned pdfs with OCR and multithreading
-	If an indexed document has been moved since the last indexing, it updates the path
-	If an indexed document has been deleted since the last indexing, it deletes the document from the database
-	If an index already exists, then only newly added/modified/deleted documents are processed
-	Basically it ensures that the index is always up-to-date
-	The program was built by taking into account object-oriented design principles
-	Future features: pptx and docx processing

### Index (database)
Search engines store data in a form of index to provide fast searchability. The database is maintained by the Indexer and accessed by the Index query.
### Index query:
The user make queries from the UI and gets back the relevant and ranked results in a structured way.

## License status
Provides a user interface to display license status of different engineering softwares that use FlexLM servers. The server’s response is plain text, so the extraction of the necessary information is done by using regular expressions and some logic.

As it is mentioned, it is a public version of the project so only the placeholders are being shown in the screenshot below.

![License_status](media/license_status_1000.png)
