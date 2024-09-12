import os
import json
import click
import sqlite3
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

def init_db():
    conn = sqlite3.connect('processed_files.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processed_files
    (filename TEXT PRIMARY KEY)
    ''')
    conn.commit()
    conn.close()

def mark_as_processed(filename):
    conn = sqlite3.connect('processed_files.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO processed_files (filename) VALUES (?)', (filename,))
    conn.commit()
    conn.close()

def is_processed(filename):
    conn = sqlite3.connect('processed_files.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM processed_files WHERE filename = ?', (filename,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def load_json_files(folder_path):
    json_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                json_files.append((filename, json_data))
    return json_files

def get_translations(json_data, target_langs):
    translations = []

    if 'media' in json_data:  # SupplierFact case
        # Media translations
        for media in json_data.get('media', []):
            content = media.get('content', {})
            for lang, data in content.items():
                if lang != 'translations' and 'title' in data:
                    original = data['title']
                    trans = {tl: content.get('translations', {}).get(tl, {}).get('title') for tl in target_langs}
                    if any(trans.values()):
                        translations.append(('Media', original, trans))

        # Description translation
        description = json_data.get('description', {})
        for lang, original in description.items():
            if lang != 'translations':
                trans = {tl: description.get('translations', {}).get(tl) for tl in target_langs}
                if any(trans.values()):
                    translations.append(('Description', original, trans))

    elif 'data' in json_data:  # SupplierOffer case
        data = json_data['data']
        
        # Description translation
        original = data.get('description', '')
        translations = data.get('translations', {})
        trans = {tl: translations.get('description', {}).get(tl) if translations is not None else None for tl in target_langs}
        if any(trans.values()):
            translations.append(('Description', original, trans))
        
        # Keywords translation
        if 'keywords' in data and data['keywords']:
            original = data['keywords'][0]
            translations = data.get('translations', {})
            trans = {tl: translations.get('keywords', [{}])[0].get(tl) if translations is not None else None for tl in target_langs}
            if any(trans.values()):
                translations.append(('Keywords', original, trans))
        
        # Name translation
        original = data.get('name', '')
        translations = data.get('translations', {})
        trans = {tl: translations.get('name', {}).get(tl) if translations is not None else None for tl in target_langs}
        if any(trans.values()):
            translations.append(('Name', original, trans))

    return translations

def review_translations(translations, filename, target_langs, reviewer=None):
    total = len(translations)
    current = 0

    while current < total:
        click.clear()
        translation_type, original, trans = translations[current]
        review_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        click.echo(f"{Fore.CYAN}File: {Style.RESET_ALL}{filename}")
        click.echo(f"{Fore.CYAN}Type: {Style.RESET_ALL}{translation_type}")
        click.echo(f"{Fore.CYAN}Review: {Style.RESET_ALL}{current + 1} of {total}")
        if reviewer:
            click.echo(f"{Fore.CYAN}Reviewer: {Style.RESET_ALL}{reviewer}")
        click.echo(f"{Fore.CYAN}Review Time: {Style.RESET_ALL}{review_time}")
        click.echo(f"\n{Fore.GREEN}Original: {Style.RESET_ALL}{original}")
        click.echo()  # Empty line between original and translations
        for lang in target_langs:
            click.echo(f"{Fore.YELLOW}Translation ({lang}): {Style.RESET_ALL}{trans.get(lang, 'N/A')}")
            click.echo()  # Empty line between different translations
        
        choice = click.prompt(f"\n{Fore.MAGENTA}Press Enter for next, or enter 'p' for previous, 'c' for next company, or 'q' to quit{Style.RESET_ALL}", 
                              type=click.Choice(['', 'n', 'p', 'c', 'q']), default='', show_default=False)
        
        if choice in ['', 'n']:
            current = min(current + 1, total - 1)
        elif choice == 'p':
            current = max(current - 1, 0)
        elif choice == 'c':
            return 'next_company'
        elif choice == 'q':
            return 'quit'

@click.command()
@click.option('--folder', required=True, help='Path to the folder containing JSON files')
@click.option('--to', required=True, multiple=True, help='Target language code(s) (e.g., "en", "fr", "de"). Up to 3 languages.')
@click.option('--reviewer', help='Name of the person doing the review')
def main(folder, to, reviewer):
    if len(to) > 3:
        click.echo(f"{Fore.RED}Error: You can select up to 3 target languages.{Style.RESET_ALL}")
        return

    init_db()
    json_files = load_json_files(folder)
    
    for filename, json_data in json_files:
        if is_processed(filename):
            click.echo(f"{Fore.YELLOW}Skipping processed file: {Style.RESET_ALL}{filename}")
            continue

        translations = get_translations(json_data, to)
        if translations:
            result = review_translations(translations, filename, to, reviewer)
            if result == 'quit':
                break
            elif result == 'next_company':
                mark_as_processed(filename)
                continue
        else:
            click.echo(f"{Fore.RED}No translations found for {Style.RESET_ALL}{filename}")
        
        mark_as_processed(filename)
        
        if not click.confirm(f"{Fore.CYAN}Continue to the next file?{Style.RESET_ALL}"):
            break

    click.echo(f"{Fore.GREEN}Review completed.{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
