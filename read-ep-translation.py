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

def get_translations(json_data, target_langs):
    translations = []

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

    return translations

def review_translations(translations, filename, target_langs):
    total = len(translations)
    current = 0

    while current < total:
        click.clear()
        translation_type, original, trans = translations[current]
        click.echo(f"File: {filename}")
        click.echo(f"Type: {translation_type}")
        click.echo(f"Review {current + 1} of {total}")
        click.echo(f"\nOriginal: {original}")
        for lang in target_langs:
            click.echo(f"Translation ({lang}): {trans.get(lang, 'N/A')}")
        
        choice = click.prompt("\nEnter 'n' for next, 'p' for previous, 'c' for next company, or 'q' to quit", type=click.Choice(['n', 'p', 'c', 'q']))
        
        if choice == 'n':
            current = min(current + 1, total - 1)
        elif choice == 'p':
            current = max(current - 1, 0)
        elif choice == 'c':
            return 'next_company'
        else:
            return 'quit'

@click.command()
@click.option('--folder', required=True, help='Path to the folder containing JSON files')
@click.option('--to', required=True, multiple=True, help='Target language code(s) (e.g., "en", "fr", "de"). Up to 3 languages.')
def main(folder, to):
    if len(to) > 3:
        click.echo("Error: You can select up to 3 target languages.")
        return

    json_files = load_json_files(folder)
    
    for filename, json_data in json_files:
        translations = get_translations(json_data, to)
        if translations:
            result = review_translations(translations, filename, to)
            if result == 'quit':
                break
            elif result == 'next_company':
                continue
        
        if not click.confirm("Continue to the next file?"):
            break

    click.echo("Review completed.")

if __name__ == '__main__':
    main()
