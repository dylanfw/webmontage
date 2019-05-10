# webmontage
A tool for producing a montage depicting the development and design of a web page via its git commit history.

**requirements**
This library uses the `selenium` Python library to drive the headless Chrome browser to load the static web page. This requires that the proper ChromeDriver be downloaded and placed somewhere in the PATH. Download ChromeDriver for your installed version of Google Chrome here: https://sites.google.com/a/chromium.org/chromedriver/downloads

**usage:**
```
$ webmontage [-h] [-f FILE] [--browser-width BROWSER_WIDTH]
                  [--browser-height BROWSER_HEIGHT]
                  [--video-width VIDEO_WIDTH] [--video-height VIDEO_HEIGHT]
                  repository index_page

WebMontage - Static site montage generator using git history

positional arguments:
  repository            The absolute path to the root of the git repository
                        for the web page
  index_page             The index file relative to the root of the repo, i.e.
                        'index.html'

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  If given, only commits that affect this file will be
                        considered, i.e. 'main.css'
  --browser-width BROWSER_WIDTH
                        Width of the browser window to load the web page in
  --browser-height BROWSER_HEIGHT
                        Height of the browser window to load the web page in
  --video-width VIDEO_WIDTH
                        Width of the slideshow window to display the montage
                        in
  --video-height VIDEO_HEIGHT
                        Height of the slideshow window to display the montage
                        in```
