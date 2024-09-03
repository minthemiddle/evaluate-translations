import os
import json
import click

def check_translations(json_data):
    translations = {}
    
    # Check translations in description
    if 'description' in json_data and 'translations' in json_data['description']:
        translations.update(json_data['description']['translations'])
    
    # Check translations in media
    if 'media' in json_data:
        for item in json_data['media']:
            if 'content' in item and 'translations' in item['content']:
                translations.update(item['content']['translations'])
    
    # Check translations in shortDescription
    if 'shortDescription' in json_data and 'de' in json_data['shortDescription']:
        translations['de'] = json_data['shortDescription']['de']
    
    # Check translations in longDescription
    if 'longDescription' in json_data and 'de' in json_data['longDescription']:
        translations['de'] = json_data['longDescription']['de']
    
    # Check for duplicates
    translation_values = list(translations.values())
    if len(translation_values) != len(set(translation_values)):
        return False  # There are duplicate translations
    return True  # All translations are unique

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
