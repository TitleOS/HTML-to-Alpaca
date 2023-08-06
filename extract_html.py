import os
from bs4 import BeautifulSoup

def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(["script", "style", "meta", "link", "head", "noscript", "footer", "header", "nav"]):
            tag.extract()
        
        return " ".join(soup.stripped_strings)

def process_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                text_content = extract_text_from_html(file_path)
                with open(file_path + ".txt", 'w', encoding='utf-8') as text_file:
                    text_file.write(text_content)

if __name__ == "__main__":
    directory_path = input("Enter the directory path: ")
    process_directory(directory_path)
