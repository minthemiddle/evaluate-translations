import os
import json
import click

def check_translations(json_data):
    translations = {}
    original_lang = json_data.get('language', 'en')  # Annahme: Standardsprache ist Englisch
    
    def update_translations(trans_dict, source=''):
        for lang, value in trans_dict.items():
            if isinstance(value, str) and lang != original_lang:
                translations.setdefault(lang, set()).add((value, source))
    
    # Check translations in description
    if 'description' in json_data and 'translations' in json_data['description']:
        update_translations(json_data['description']['translations'], 'description')
    
    # Check translations in media
    if 'media' in json_data:
        for item in json_data['media']:
            if 'content' in item and 'translations' in item['content']:
                update_translations(item['content']['translations'], 'media')
    
    # Check translations in shortDescription
    if 'shortDescription' in json_data:
        update_translations(json_data['shortDescription'], 'shortDescription')
    
    # Check translations in longDescription
    if 'longDescription' in json_data:
        update_translations(json_data['longDescription'], 'longDescription')
    
    # Check for duplicates
    for lang, lang_translations in translations.items():
        unique_translations = set(value for value, _ in lang_translations)
        if len(lang_translations) > len(unique_translations):
            # Check if duplicates are not in the original language
            duplicates = [value for value, _ in lang_translations if lang_translations.count((value, _)) > 1]
            if any(duplicate not in json_data.get(field, {}).get(original_lang, '') 
                   for duplicate in duplicates 
                   for field in ['description', 'shortDescription', 'longDescription']):
                return False  # There are duplicate translations not in the original language
    return True  # All translations are unique or duplicates are in the original language

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
                    if not check_translations(json_data):
                        click.echo(f'Duplicate translations found in {filename}')
                except json.JSONDecodeError:
                    click.echo(f'Error decoding JSON in {filename}')

if __name__ == '__main__':
    check_json_translations()
