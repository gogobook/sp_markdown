## Where it came from ?

This package is came from [Spirit](https://github.com/nitely/Spirit), and remove poll and mention features.  
The tests also came from [Spirit](https://github.com/nitely/Spirit).

## How to use it ?

Most examples can find in tests_markdown.py  
settings.py need follow code:  
```
ST_ALLOWED_URL_PROTOCOLS = {
    'http', 'https', 'mailto', 'ftp', 'ftps',
    'git', 'svn', 'magnet', 'irc', 'ircs'}

ST_MENTIONS_PER_COMMENT = 30
```
