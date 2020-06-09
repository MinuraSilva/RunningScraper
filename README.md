# RunningScraper

## How to Run Scraper
More info [here](https://github.com/MinuraSilva/RunningScraper/blob/master/other/scrapy_commands.py)

`scrapy crawl adidas_ca -o quotes.json`
adidas_ca is the name assigned to the scraper. Remember to change the start URL to be the last page in Outlet items to avoid scraping too many items during testing.

## Finding CSS selectors quickly:
- Use the scrapy shell (see the 'More info' link above for headers to spoof a browser.<br>
`$ scrapy shell`<br>
`>>> from scrapy import Request`<br>
`>>> req = Request('yoururl.com', headers={"header1":"value1"})`<br>
`>>> fetch(req)`<br>
`>>> response.css('...')`<br>
- Use Chrome to test the selector.<br>
`Chrome Dev Tools -> ELements tab -> click on HTML and press Ctrl +F` You can now type in a selector in the search box. <br>
e.g. `div[class*=item] img[src$=jpg]`<br>
Note: Chrome will not work with `::text` or `::attr(attr_name)` extractors. Also, remember not to use the .get() method used by Scrapy in Chrome.

## Tips on Scraping Dynamic Content:
- Scrapy information on how to Scrape [Dynamic Content](https://docs.scrapy.org/en/latest/topics/dynamic-content.html)
- See the [New Features](https://github.com/MinuraSilva/RunningScraper/projects/1#card-39618818) tab in Projects for more info.<br><br>

If a value is updated by javascript, then it will not be possible to extract that value simply by using a CSS selector on the HTML. There are two main ways the dynamic data is stored:
#### 1. Data stored in block of JavaScript in the HTML file:
- This is what most of the sites do.
- The main HTML may only have a reference to a variable, but the data referred to by the variable will be in the same HTML file inside a <script> tag. To find the location inside the JS code, it may be necessary to use regex by copying the entire source to Notepad++. Extracting this data will either require a regex search by treating the entire JS code as a string, or parsing the JSON object and then accessing it as an object.
- Oftentimes there will be multiple JS blocks in a HTML. An easy way to look at each of these blocks properly formatted is to use the QuickSourceViewer Chrome extension.

#### 2. AJAX call:
- The site will make an API call to a completely different route to get the data that should be updated dynamically. This is what adidas.ca does to get info on stock availability. To extract the data that is got from this AJAX call, you will need to identify the route that it hits using `Chrome Dev Tools -> Network Tab -> XHR`. Search for all of the resources until you find the data that you want. To determine the exact route to hit you will have to analyse the contents/url of the page that requests this resource and the url of the API call.

#### 3. Infinite Scroll:
- Infinite may require using both of these techniques. Usually infinite scroll includes making an AJAX  request whose route is formed by using the code of the last item on the current page plus the number of next items to get. The code of the last item on the current page may be stored in a JS block.
- Nike.ca: Looks like the infinite scroll XHR url is made of `<authorization_code>+<last_item_code>+<number_of_next_items>` and the url for the next page is at the bottom of each xhr. The URLs are url encoded. Use this [tool to deode](https://www.url-encode-decode.com/). Note: the authorization code seems to be unnecessary.
  
