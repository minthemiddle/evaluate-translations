import os
import json
import click

def load_json_files(folder_path):
    json_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                json_files.append((filename, json_data))
    return json_files

def get_translations(json_data, target_lang):
    translations = []

    # Media translations
    for media in json_data.get('media', []):
        content = media.get('content', {})
        for lang, data in content.items():
            if lang != 'translations' and 'title' in data:
                original = data['title']
                translation = content.get('translations', {}).get(target_lang, {}).get('title')
                if translation:
                    translations.append(('Media', original, translation))

    # Description translation
    description = json_data.get('description', {})
    for lang, original in description.items():
        if lang != 'translations':
            translation = description.get('translations', {}).get(target_lang)
            if translation:
                translations.append(('Description', original, translation))

    return translations

def review_translations(translations, filename):
    total = len(translations)
    current = 0

    while current < total:
        click.clear()
        translation_type, original, translation = translations[current]
        click.echo(f"File: {filename}")
        click.echo(f"Type: {translation_type}")
        click.echo(f"Review {current + 1} of {total}")
        click.echo(f"\nOriginal: {original}")
        click.echo(f"Translation: {translation}")
        
        choice = click.prompt("\nEnter 'n' for next, 'p' for previous, or 'q' to quit", type=click.Choice(['n', 'p', 'q']))
        
        if choice == 'n':
            current = min(current + 1, total - 1)
        elif choice == 'p':
            current = max(current - 1, 0)
        else:
            return

@click.command()
@click.option('--folder', required=True, help='Path to the folder containing JSON files')
@click.option('--to', required=True, help='Target language code (e.g., "en")')
def main(folder, to):
    json_files = load_json_files(folder)
    
    for filename, json_data in json_files:
        translations = get_translations(json_data, to)
        if translations:
            review_translations(translations, filename)
        
        if not click.confirm("Continue to the next file?"):
            break

    click.echo("Review completed.")

if __name__ == '__main__':
    main()
