import os
import json
import click
import sqlite3
from typing import Dict, Any

def init_db():
    conn = sqlite3.connect('translation_review.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviewed_files
                 (filename TEXT PRIMARY KEY, reviewed INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (filename TEXT, field TEXT, comment TEXT)''')
    conn.commit()
    conn.close()

def check_translations(json_data):
    translations = {}
    original_lang = json_data.get('language', 'en')  # Annahme: Standardsprache ist Englisch
    duplicates = []
    empty_translations = []
    
    def update_translations(trans_dict, source=''):
        for lang, value in trans_dict.items():
            if isinstance(value, str) and value.strip():  # Only add non-empty strings
                translations.setdefault(lang, set()).add((value, source))
            elif isinstance(value, dict):
                # Handle nested dictionaries
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str) and nested_value.strip():
                        translations.setdefault(lang, set()).add((nested_value, f"{source}.{nested_key}"))
    
    def check_empty_translations(trans_dict, source=''):
        for lang, value in trans_dict.items():
            if isinstance(value, str) and not value.strip():
                empty_translations.append((lang, source))
            elif isinstance(value, dict):
                # Handle nested dictionaries
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str) and not nested_value.strip():
                        empty_translations.append((lang, f"{source}.{nested_key}"))
    
    # Check translations in description
    if 'description' in json_data:
        original_desc = json_data['description'].get(original_lang, '')
        update_translations({original_lang: original_desc}, 'description')
        if 'translations' in json_data['description']:
            update_translations(json_data['description']['translations'], 'description')
            if original_desc:
                check_empty_translations(json_data['description']['translations'], 'description')
    
    # Check translations in media
    if 'media' in json_data:
        for item in json_data['media']:
            if 'content' in item and 'translations' in item['content']:
                original_content = item['content'].get(original_lang, '')
                update_translations(item['content']['translations'], 'media')
                if original_content:
                    check_empty_translations(item['content']['translations'], 'media')
    
    # Check for duplicates across all languages
    all_translations = {}
    for lang, lang_translations in translations.items():
        for value, source in lang_translations:
            if value in all_translations and lang != original_lang:
                duplicates.append((value, lang, all_translations[value], source))
            else:
                all_translations[value] = (lang, source)
    
    return duplicates, empty_translations

def interactive_review(json_data: Dict[str, Any], filename: str, trans_lang: str):
    conn = sqlite3.connect('translation_review.db')
    c = conn.cursor()

    # Get the original language, default to 'en' if not present
    original_lang = json_data.get('language', 'en')

    def review_field(field_name: str, original: str, translation: str):
        click.echo(f"\nField: {field_name}")
        click.echo(f"Original ({original_lang}): {original}")
        click.echo(f"Translation ({trans_lang}): {translation}")
        
        while True:
            action = click.prompt("Actions: [n]ext, [c]omment, [q]uit", type=click.Choice(['n', 'c', 'q']), show_choices=False)
            if action == 'n':
                break
            elif action == 'c':
                comment = click.prompt("Enter your comment")
                c.execute("INSERT INTO comments (filename, field, comment) VALUES (?, ?, ?)", (filename, field_name, comment))
                conn.commit()
            elif action == 'q':
                return False
        return True

    def review_translations(data: Dict[str, Any], prefix: str = ''):
        if 'description' in data:
            original = data['description'].get(original_lang, '')
            translation = data['description'].get('translations', {}).get(trans_lang, '')
            if original or translation:
                if not review_field(f"{prefix}description", original, translation):
                    return False

        if 'media' in data:
            for i, item in enumerate(data['media']):
                if 'content' in item:
                    original = item['content'].get(original_lang, '')
                    translation = item['content'].get('translations', {}).get(trans_lang, '')
                    if original or translation:
                        if not review_field(f"{prefix}media[{i}].content", original, translation):
                            return False
        return True

    review_translations(json_data)
    
    c.execute("INSERT OR REPLACE INTO reviewed_files (filename, reviewed) VALUES (?, 1)", (filename,))
    conn.commit()
    conn.close()

@click.command()
@click.argument('folder_path', type=click.Path(exists=True, file_okay=False))
@click.option('--interactive', '-i', is_flag=True, help="Enable interactive mode")
@click.option('--lang', '-l', default='en', help="Translation language to review")
def check_json_translations(folder_path, interactive, lang):
    """Check translations in JSON files in the specified folder."""
    if interactive:
        init_db()
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    json_data = json.load(file)
                    duplicates, empty_translations = check_translations(json_data)
                    
                    if interactive:
                        conn = sqlite3.connect('translation_review.db')
                        c = conn.cursor()
                        c.execute("SELECT reviewed FROM reviewed_files WHERE filename = ?", (filename,))
                        result = c.fetchone()
                        conn.close()
                        
                        if result is None or result[0] == 0:
                            click.echo(f"\nReviewing {filename}:")
                            interactive_review(json_data, filename, lang)
                        else:
                            click.echo(f"\nSkipping {filename} (already reviewed)")
                    else:
                        if duplicates:
                            click.echo(f'Duplicate translations found in {filename}:')
                            for value, lang, (orig_lang, orig_source), source in duplicates:
                                click.echo(f'  Value: "{value}"')
                                click.echo(f'    Found in: {lang} ({source})')
                                click.echo(f'    Original: {orig_lang} ({orig_source})')
                                click.echo('')
                        if empty_translations:
                            click.echo(f'Empty translations found in {filename}:')
                            for lang, source in empty_translations:
                                click.echo(f'  Language: {lang}')
                                click.echo(f'  Source: {source}')
                                click.echo('')
                except json.JSONDecodeError:
                    click.echo(f'Error decoding JSON in {filename}')

if __name__ == '__main__':
    check_json_translations()
