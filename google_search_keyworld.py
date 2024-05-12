
import requests


def search_google(keyword, api_key):

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=013036536707430787589:_pqjad5hr1a&q={keyword}&cr=countryTW&num=5"
    response = requests.get(url)
    if response.status_code == 200:
        search_results = response.json()
        links = [item['link'] for item in search_results.get('items', [])]
        return links
    else:
        print("Error occurred while fetching search results")
        return []


api_key = ""

keyword = input("Please enter a keyword：")
search_results = search_google(keyword, api_key)

if search_results:
    print("Search results link：")
    for link in search_results:
        print(link)
else:
    print("No relevant search results found.")


search_results_array = search_results if search_results else []
print("Search results are stored in array:", search_results_array)
