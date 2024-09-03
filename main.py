import os
import json
import click

def check_translations(json_data):
    translations = {}
    original_lang = json_data.get('language', 'en')  # Annahme: Standardsprache ist Englisch
    duplicates = []
    
    def update_translations(trans_dict, source=''):
        for lang, value in trans_dict.items():
            if isinstance(value, str):
                translations.setdefault(lang, set()).add((value, source))
    
    # Check translations in description
    if 'description' in json_data:
        update_translations({original_lang: json_data['description'].get(original_lang, '')}, 'description')
        if 'translations' in json_data['description']:
            update_translations(json_data['description']['translations'], 'description')
    
    # Check translations in media
    if 'media' in json_data:
        for item in json_data['media']:
            if 'content' in item and 'translations' in item['content']:
                update_translations(item['content']['translations'], 'media')
    
    # Check for duplicates across all languages
    all_translations = {}
    for lang, lang_translations in translations.items():
        for value, source in lang_translations:
            if value in all_translations and lang != original_lang:
                duplicates.append((value, lang, all_translations[value], source))
            else:
                all_translations[value] = (lang, source)
    
    return duplicates

@click.command()
@click.argument('folder_path', type=click.Path(exists=True, file_okay=False))
def check_json_translations(folder_path):
    """Check translations in JSON files in the specified folder."""
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    json_data = json.load(file)
                    duplicates = check_translations(json_data)
                    if duplicates:
                        click.echo(f'Duplicate translations found in {filename}:')
                        for value, lang, (orig_lang, orig_source), source in duplicates:
                            click.echo(f'  Value: "{value}"')
                            click.echo(f'    Found in: {lang} ({source})')
                            click.echo(f'    Original: {orig_lang} ({orig_source})')
                            click.echo('')
                except json.JSONDecodeError:
                    click.echo(f'Error decoding JSON in {filename}')

if __name__ == '__main__':
    check_json_translations()
