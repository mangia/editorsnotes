from django import template
import re
import json

register = template.Library()

# Maps to translate json from Zotero's API to CSL or human-readable form,
# see http://gsl-nagoya-u.net/http/pub/csl-fields/

field_map = {'manuscript': {'csl': {'numPages': 'number-of-pages', 'callNumber': 'call-number', 'url': 'URL', 'manuscriptType': 'genre', 'extra': 'note', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'numPages': '# of Pages', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'manuscriptType': 'Type', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'accessDate': 'Accessed', 'place': 'Place', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'radioBroadcast': {'csl': {'episodeNumber': 'number', 'programTitle': 'container-title', 'network': 'publisher', 'audioRecordingFormat': 'medium', 'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'audioRecordingFormat': 'Format', 'programTitle': 'Program Title', 'accessDate': 'Accessed', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'title': 'Title', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'runningTime': 'Running Time', 'place': 'Place', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'episodeNumber': 'Episode Number', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number', 'network': 'Network'}}, 'dictionaryEntry': {'csl': {'volume': 'volume', 'publisher': 'publisher', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'series': 'collection-title', 'extra': 'note', 'pages': 'page', 'edition': 'edition', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'title': 'title', 'dictionaryTitle': 'container-title', 'archiveLocation': 'archive_location', 'seriesNumber': 'collection-number', 'abstractNote': 'abstract', 'archive': 'archive', 'numberOfVolumes': 'number-of-volumes'}, 'readable': {'ISBN': 'ISBN', 'extra': 'Extra', 'series': 'Series', 'edition': 'Edition', 'seriesNumber': 'Series Number', 'numberOfVolumes': '# of Volumes', 'abstractNote': 'Abstract', 'title': 'Title', 'archive': 'Archive', 'archiveLocation': 'Loc. in Archive', 'dictionaryTitle': 'Dictionary Title', 'accessDate': 'Accessed', 'libraryCatalog': 'Library Catalog', 'volume': 'Volume', 'callNumber': 'Call Number', 'date': 'Date', 'pages': 'Pages', 'publisher': 'Publisher', 'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'place': 'Place'}}, 'hearing': {'csl': {'publisher': 'publisher', 'extra': 'note', 'url': 'URL', 'title': 'title', 'pages': 'page', 'accessDate': 'accessed', 'documentNumber': 'number', 'place': 'event-place and<br/>publisher-place', 'abstractNote': 'abstract', 'numberOfVolumes': 'number-of-volumes', 'history': 'references'}, 'readable': {'publisher': 'Publisher', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'title': 'Title', 'extra': 'Extra', 'pages': 'Pages', 'accessDate': 'Accessed', 'documentNumber': 'Document Number', 'session': 'Session', 'legislativeBody': 'Legislative Body', 'committee': 'Committee', 'date': 'Date', 'place': 'Place', 'abstractNote': 'Abstract', 'numberOfVolumes': '# of Volumes', 'history': 'History'}}, 'thesis': {'csl': {'numPages': 'number-of-pages', 'thesisType': 'genre', 'callNumber': 'call-number', 'url': 'URL', 'university': 'publisher', 'extra': 'note', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'numPages': '# of Pages', 'thesisType': 'Type', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'university': 'University', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'accessDate': 'Accessed', 'place': 'Place', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'film': {'csl': {'callNumber': 'call-number', 'url': 'URL', 'distributor': 'publisher', 'extra': 'note', 'accessDate': 'accessed', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'videoRecordingFormat': 'medium', 'genre': 'genre', 'archive': 'archive'}, 'readable': {'accessDate': 'Accessed', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'distributor': 'Distributor', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'runningTime': 'Running Time', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'videoRecordingFormat': 'Format', 'genre': 'Genre', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'conferencePaper': {'csl': {'publisher': 'publisher', 'DOI': 'DOI', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'series': 'collection-title', 'extra': 'note', 'pages': 'page', 'volume': 'volume', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'proceedingsTitle': 'container-title', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'conferenceName': 'event', 'archive': 'archive'}, 'readable': {'DOI': 'DOI', 'ISBN': 'ISBN', 'extra': 'Extra', 'series': 'Series', 'conferenceName': 'Conference Name', 'abstractNote': 'Abstract', 'archive': 'Archive', 'title': 'Title', 'proceedingsTitle': 'Proceedings Title', 'archiveLocation': 'Loc. in Archive', 'accessDate': 'Accessed', 'libraryCatalog': 'Library Catalog', 'volume': 'Volume', 'callNumber': 'Call Number', 'date': 'Date', 'pages': 'Pages', 'publisher': 'Publisher', 'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'place': 'Place'}}, 'journalArticle': {'csl': {'seriesTitle': 'collection-title', 'DOI': 'DOI', 'callNumber': 'call-number', 'url': 'URL', 'series': 'collection-title', 'extra': 'note', 'pages': 'page', 'volume': 'volume', 'accessDate': 'accessed', 'publicationTitle': 'container-title', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'issue': 'issue', 'archive': 'archive'}, 'readable': {'DOI': 'DOI', 'extra': 'Extra', 'seriesText': 'Series Text', 'series': 'Series', 'abstractNote': 'Abstract', 'archive': 'Archive', 'title': 'Title', 'ISSN': 'ISSN', 'archiveLocation': 'Loc. in Archive', 'journalAbbreviation': 'Journal Abbr', 'issue': 'Issue', 'seriesTitle': 'Series Title', 'accessDate': 'Accessed', 'libraryCatalog': 'Library Catalog', 'volume': 'Volume', 'callNumber': 'Call Number', 'date': 'Date', 'pages': 'Pages', 'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'publicationTitle': 'Publication'}}, 'patent': {'csl': {'patentNumber': 'number', 'extra': 'note', 'url': 'URL', 'title': 'title', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'references': 'references', 'abstractNote': 'abstract', 'issueDate': 'issued', 'pages': 'page'}, 'readable': {'patentNumber': 'Patent Number', 'accessDate': 'Accessed', 'filingDate': 'Filing Date', 'language': 'Language', 'rights': 'Rights', 'applicationNumber': 'Application Number', 'country': 'Country', 'extra': 'Extra', 'shortTitle': 'Short Title', 'pages': 'Pages', 'assignee': 'Assignee', 'issuingAuthority': 'Issuing Authority', 'place': 'Place', 'priorityNumbers': 'Priority Numbers', 'url': 'URL', 'references': 'References', 'legalStatus': 'Legal Status', 'issueDate': 'Issue Date', 'abstractNote': 'Abstract', 'title': 'Title'}}, 'webpage': {'csl': {'extra': 'note', 'url': 'URL', 'title': 'title', 'accessDate': 'accessed', 'websiteType': 'genre', 'abstractNote': 'abstract', 'websiteTitle': 'container-title'}, 'readable': {'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'accessDate': 'Accessed', 'websiteType': 'Website Type', 'date': 'Date', 'title': 'Title', 'abstractNote': 'Abstract', 'websiteTitle': 'Website Title'}}, 'book': {'csl': {'numPages': 'number-of-pages', 'publisher': 'publisher', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'series': 'collection-title', 'extra': 'note', 'edition': 'edition', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'title': 'title', 'archiveLocation': 'archive_location', 'seriesNumber': 'collection-number', 'abstractNote': 'abstract', 'archive': 'archive', 'numberOfVolumes': 'number-of-volumes', 'volume': 'volume'}, 'readable': {'ISBN': 'ISBN', 'extra': 'Extra', 'series': 'Series', 'edition': 'Edition', 'seriesNumber': 'Series Number', 'numberOfVolumes': '# of Volumes', 'abstractNote': 'Abstract', 'title': 'Title', 'archive': 'Archive', 'archiveLocation': 'Loc. in Archive', 'accessDate': 'Accessed', 'libraryCatalog': 'Library Catalog', 'volume': 'Volume', 'callNumber': 'Call Number', 'date': 'Date', 'numPages': '# of Pages', 'publisher': 'Publisher', 'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'place': 'Place'}}, 'instantMessage': {'csl': {'title': 'title', 'url': 'URL', 'extra': 'note', 'accessDate': 'accessed', 'abstractNote': 'abstract'}, 'readable': {'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'accessDate': 'Accessed', 'date': 'Date', 'title': 'Title', 'abstractNote': 'Abstract'}}, 'interview': {'csl': {'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'accessDate': 'accessed', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'interviewMedium': 'medium', 'archive': 'archive'}, 'readable': {'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'accessDate': 'Accessed', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'interviewMedium': 'Medium', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'presentation': {'csl': {'meetingName': 'event', 'extra': 'note', 'url': 'URL', 'title': 'title', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'presentationType': 'genre', 'abstractNote': 'abstract'}, 'readable': {'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'accessDate': 'Accessed', 'place': 'Place', 'presentationType': 'Type', 'title': 'Title', 'abstractNote': 'Abstract', 'meetingName': 'Meeting Name'}}, 'email': {'csl': {'extra': 'note', 'url': 'URL', 'accessDate': 'accessed', 'abstractNote': 'abstract', 'subject': 'title'}, 'readable': {'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'accessDate': 'Accessed', 'date': 'Date', 'abstractNote': 'Abstract', 'subject': 'Subject'}}, 'forumPost': {'csl': {'extra': 'note', 'url': 'URL', 'title': 'title', 'accessDate': 'accessed', 'postType': 'genre', 'abstractNote': 'abstract', 'forumTitle': 'container-title'}, 'readable': {'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'accessDate': 'Accessed', 'postType': 'Post Type', 'date': 'Date', 'title': 'Title', 'abstractNote': 'Abstract', 'forumTitle': 'Forum/Listserv Title'}}, 'map': {'csl': {'seriesTitle': 'collection-title', 'publisher': 'publisher', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'edition': 'edition', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'mapType': 'genre', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'seriesTitle': 'Series Title', 'publisher': 'Publisher', 'scale': 'Scale', 'ISBN': 'ISBN', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'edition': 'Edition', 'accessDate': 'Accessed', 'place': 'Place', 'mapType': 'Type', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'videoRecording': {'csl': {'seriesTitle': 'collection-title', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'title': 'title', 'extra': 'note', 'volume': 'volume', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'studio': 'publisher', 'abstractNote': 'abstract', 'videoRecordingFormat': 'medium', 'archive': 'archive', 'numberOfVolumes': 'number-of-volumes'}, 'readable': {'seriesTitle': 'Series Title', 'ISBN': 'ISBN', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'title': 'Title', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'numberOfVolumes': '# of Volumes', 'volume': 'Volume', 'runningTime': 'Running Time', 'accessDate': 'Accessed', 'place': 'Place', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'studio': 'Studio', 'abstractNote': 'Abstract', 'videoRecordingFormat': 'Format', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'blogPost': {'csl': {'blogTitle': 'container-title', 'url': 'URL', 'extra': 'note', 'accessDate': 'accessed', 'websiteType': 'genre', 'title': 'title', 'abstractNote': 'abstract'}, 'readable': {'extra': 'Extra', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'blogTitle': 'Blog Title', 'accessDate': 'Accessed', 'websiteType': 'Website Type', 'date': 'Date', 'title': 'Title', 'abstractNote': 'Abstract'}}, 'newspaperArticle': {'csl': {'callNumber': 'call-number', 'url': 'URL', 'title': 'title', 'section': 'section', 'extra': 'note', 'pages': 'page', 'edition': 'edition', 'accessDate': 'accessed', 'publicationTitle': 'container-title', 'archiveLocation': 'archive_location', 'place': 'event-place and<br/>publisher-place', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'extra': 'Extra', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'title': 'Title', 'section': 'Section', 'ISSN': 'ISSN', 'libraryCatalog': 'Library Catalog', 'pages': 'Pages', 'edition': 'Edition', 'accessDate': 'Accessed', 'publicationTitle': 'Publication', 'archiveLocation': 'Loc. in Archive', 'place': 'Place', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'letter': {'csl': {'letterType': 'genre', 'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'accessDate': 'accessed', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'letterType': 'Type', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'accessDate': 'Accessed', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'artwork': {'csl': {'artworkSize': 'genre', 'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'artworkMedium': 'medium', 'accessDate': 'accessed', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'artworkSize': 'Artwork Size', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'accessDate': 'Accessed', 'artworkMedium': 'Medium', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'report': {'csl': {'seriesTitle': 'collection-title', 'institution': 'publisher', 'callNumber': 'call-number', 'url': 'URL', 'title': 'title', 'extra': 'note', 'pages': 'page', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'reportNumber': 'number', 'archiveLocation': 'archive_location', 'reportType': 'genre', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'seriesTitle': 'Series Title', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'title': 'Title', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'institution': 'Institution', 'pages': 'Pages', 'accessDate': 'Accessed', 'place': 'Place', 'reportNumber': 'Report Number', 'archiveLocation': 'Loc. in Archive', 'reportType': 'Report Type', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'podcast': {'csl': {'seriesTitle': 'collection-title', 'episodeNumber': 'number', 'extra': 'note', 'url': 'URL', 'audioFileType': 'medium', 'accessDate': 'accessed', 'title': 'title', 'abstractNote': 'abstract'}, 'readable': {'seriesTitle': 'Series Title', 'episodeNumber': 'Episode Number', 'accessDate': 'Accessed', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'audioFileType': 'File Type', 'runningTime': 'Running Time', 'title': 'Title', 'abstractNote': 'Abstract', 'extra': 'Extra'}}, 'audioRecording': {'csl': {'seriesTitle': 'collection-title', 'ISBN': 'ISBN', 'audioRecordingFormat': 'medium', 'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'label': 'publisher', 'volume': 'volume', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive', 'numberOfVolumes': 'number-of-volumes'}, 'readable': {'seriesTitle': 'Series Title', 'audioRecordingFormat': 'Format', 'ISBN': 'ISBN', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'numberOfVolumes': '# of Volumes', 'label': 'Label', 'volume': 'Volume', 'runningTime': 'Running Time', 'accessDate': 'Accessed', 'place': 'Place', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'case': {'csl': {'court': 'authority', 'caseName': 'title', 'reporter': 'container-title', 'url': 'URL', 'extra': 'note', 'firstPage': 'page', 'accessDate': 'accessed', 'reporterVolume': 'volume', 'docketNumber': 'number', 'abstractNote': 'abstract', 'dateDecided': 'issued', 'history': 'references'}, 'readable': {'extra': 'Extra', 'court': 'Court', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'caseName': 'Case Name', 'reporter': 'Reporter', 'firstPage': 'First Page', 'accessDate': 'Accessed', 'reporterVolume': 'Reporter Volume', 'docketNumber': 'Docket Number', 'abstractNote': 'Abstract', 'dateDecided': 'Date Decided', 'history': 'History'}}, 'statute': {'csl': {'code': 'container-title', 'extra': 'note', 'url': 'URL', 'section': 'section', 'dateEnacted': 'issued', 'accessDate': 'accessed', 'publicLawNumber': 'number', 'abstractNote': 'abstract', 'nameOfAct': 'title', 'pages': 'page', 'history': 'references'}, 'readable': {'code': 'Code', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'codeNumber': 'Code Number', 'extra': 'Extra', 'dateEnacted': 'Date Enacted', 'accessDate': 'Accessed', 'session': 'Session', 'publicLawNumber': 'Public Law Number', 'section': 'Section', 'abstractNote': 'Abstract', 'nameOfAct': 'Name of Act', 'pages': 'Pages', 'history': 'History'}}, 'computerProgram': {'csl': {'seriesTitle': 'collection-title', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'company': 'publisher', 'extra': 'note', 'accessDate': 'accessed', 'version': 'version', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'archive': 'archive'}, 'readable': {'seriesTitle': 'Series Title', 'ISBN': 'ISBN', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'programmingLanguage': 'Language', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'system': 'System', 'accessDate': 'Accessed', 'version': 'Version', 'place': 'Place', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'company': 'Company', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'bill': {'csl': {'billNumber': 'number', 'code': 'container-title', 'extra': 'note', 'url': 'URL', 'section': 'section', 'title': 'title', 'codeVolume': 'volume', 'accessDate': 'accessed', 'abstractNote': 'abstract', 'codePages': 'page', 'history': 'references'}, 'readable': {'billNumber': 'Bill Number', 'code': 'Code', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'section': 'Section', 'extra': 'Extra', 'codeVolume': 'Code Volume', 'accessDate': 'Accessed', 'session': 'Session', 'legislativeBody': 'Legislative Body', 'date': 'Date', 'title': 'Title', 'abstractNote': 'Abstract', 'codePages': 'Code Pages', 'history': 'History'}}, 'bookSection': {'csl': {'volume': 'volume', 'publisher': 'publisher', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'series': 'collection-title', 'bookTitle': 'container-title', 'extra': 'note', 'pages': 'page', 'edition': 'edition', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'title': 'title', 'archiveLocation': 'archive_location', 'seriesNumber': 'collection-number', 'abstractNote': 'abstract', 'archive': 'archive', 'numberOfVolumes': 'number-of-volumes'}, 'readable': {'ISBN': 'ISBN', 'extra': 'Extra', 'series': 'Series', 'edition': 'Edition', 'seriesNumber': 'Series Number', 'numberOfVolumes': '# of Volumes', 'abstractNote': 'Abstract', 'title': 'Title', 'archive': 'Archive', 'archiveLocation': 'Loc. in Archive', 'accessDate': 'Accessed', 'bookTitle': 'Book Title', 'libraryCatalog': 'Library Catalog', 'volume': 'Volume', 'callNumber': 'Call Number', 'date': 'Date', 'pages': 'Pages', 'publisher': 'Publisher', 'shortTitle': 'Short Title', 'language': 'Language', 'rights': 'Rights', 'url': 'URL', 'place': 'Place'}}, 'tvBroadcast': {'csl': {'episodeNumber': 'number', 'programTitle': 'container-title', 'network': 'publisher', 'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'videoRecordingFormat': 'medium', 'archive': 'archive'}, 'readable': {'episodeNumber': 'Episode Number', 'programTitle': 'Program Title', 'accessDate': 'Accessed', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'extra': 'Extra', 'libraryCatalog': 'Library Catalog', 'runningTime': 'Running Time', 'place': 'Place', 'date': 'Date', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'videoRecordingFormat': 'Format', 'archive': 'Archive', 'callNumber': 'Call Number', 'network': 'Network'}}, 'magazineArticle': {'csl': {'callNumber': 'call-number', 'url': 'URL', 'extra': 'note', 'pages': 'page', 'volume': 'volume', 'accessDate': 'accessed', 'publicationTitle': 'container-title', 'archiveLocation': 'archive_location', 'title': 'title', 'abstractNote': 'abstract', 'issue': 'issue', 'archive': 'archive'}, 'readable': {'extra': 'Extra', 'date': 'Date', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'ISSN': 'ISSN', 'libraryCatalog': 'Library Catalog', 'pages': 'Pages', 'volume': 'Volume', 'accessDate': 'Accessed', 'publicationTitle': 'Publication', 'archiveLocation': 'Loc. in Archive', 'title': 'Title', 'abstractNote': 'Abstract', 'issue': 'Issue', 'archive': 'Archive', 'callNumber': 'Call Number'}}, 'encyclopediaArticle': {'csl': {'volume': 'volume', 'publisher': 'publisher', 'ISBN': 'ISBN', 'callNumber': 'call-number', 'url': 'URL', 'series': 'collection-title', 'extra': 'note', 'pages': 'page', 'edition': 'edition', 'accessDate': 'accessed', 'place': 'event-place and<br/>publisher-place', 'title': 'title', 'archiveLocation': 'archive_location', 'seriesNumber': 'collection-number', 'abstractNote': 'abstract', 'encyclopediaTitle': 'container-title', 'archive': 'archive', 'numberOfVolumes': 'number-of-volumes'}, 'readable': {'ISBN': 'ISBN', 'extra': 'Extra', 'series': 'Series', 'edition': 'Edition', 'seriesNumber': 'Series Number', 'numberOfVolumes': '# of Volumes', 'abstractNote': 'Abstract', 'title': 'Title', 'archive': 'Archive', 'archiveLocation': 'Loc. in Archive', 'accessDate': 'Accessed', 'libraryCatalog': 'Library Catalog', 'volume': 'Volume', 'callNumber': 'Call Number', 'date': 'Date', 'pages': 'Pages', 'publisher': 'Publisher', 'language': 'Language', 'shortTitle': 'Short Title', 'rights': 'Rights', 'url': 'URL', 'place': 'Place', 'encyclopediaTitle': 'Encyclopedia Title'}}}
type_map = {'manuscript': 'manuscript', 'radioBroadcast': 'broadcast', 'dictionaryEntry': 'chapter', 'hearing': 'bill', 'thesis': 'thesis', 'film': 'motion_picture', 'conferencePaper': 'paper-conference', 'journalArticle': 'article-journal', 'patent': 'patent', 'webpage': 'webpage', 'book': 'book', 'instantMessage': 'personal_communication', 'interview': 'interview', 'presentation': 'speech', 'email': 'personal_communication', 'forumPost': 'webpage', 'map': 'map', 'videoRecording': 'motion_picture', 'blogPost': 'webpage', 'newspaperArticle': 'article-newspaper', 'letter': 'personal_communication', 'artwork': 'graphic', 'report': 'report', 'podcast': 'song', 'audioRecording': 'song', 'case': 'legal_case', 'statute': 'bill', 'computerProgram': 'book', 'bill': 'bill', 'bookSection': 'chapter', 'tvBroadcast': 'broadcast', 'magazineArticle': 'article-magazine', 'encyclopediaArticle': 'chapter'}
contrib_map = {'author': 'author', 'contributor' : 'author', 'bookAuthor': 'container-author', 'seriesEditor': 'collection-editor', 'translator': 'translator', 'editor': 'editor', 'interviewer': 'interviewer', 'recipient': 'recipient'}

def translate(z, opt):
    # Meant to translate a Zotero json string to a csl compatible one,
    # where z is a json string taken from the zotero API and opt is
    # either 'csl' or 'readable', corresponding to dict values
    # TODO: seperate 'csl' and 'readable' options
    genre = z['itemType']
    m = field_map[genre][opt]
    n = {}
    n['type'] = type_map[genre]
    if z['date']:
        n['issued'] = { 'raw' : z['date'] }
    if z['creators']:
        names = get_names(z)
        for contrib_type in names.keys():
            n[contrib_type] = names[contrib_type]
    for old, new in m.items():
        n[new] = z[old]
    return json.dumps(n)

def get_names(z):
    # where z is the same as above
    contribs = {}
    for c in z['creators']:
        name = { "family" : c['lastName'], "given" : c['firstName'] }
        contribs.setdefault(contrib_map[c['creatorType']], []).append(name)
    return contribs
