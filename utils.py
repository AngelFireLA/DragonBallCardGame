import csv

from engine.fighter import Fighter
from engine.support import Support

initial_hand_size = 3
max_active_fighters = 3
initial_ki_amount = 4
ki_gained_per_turn = 4
cards_drawn_per_turn = 2

fighters_file = 'data/fighters.csv'
supports_file = 'data/supports.csv'


def load_fighters():
    fighters = []
    try:
        with open(fighters_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                #print(row)
                fighters.append(
                    Fighter(
                        name=row['name'],
                        image_path=row['image_path'],
                        health=int(row['health']),
                        attack_power=int(row['attack_power']),
                        effects=row['effects'].split(';') if row['effects'] else [],
                        tags=row['tags'].split(';') if row['tags'] else [],
                        previous_form=row.get('previous_form', None),
                        form_level=int(row['form_level']) if row['form_level'] else 0,
                        cost=int(row['cost']),
                        fusion_members=row['fusion_members'].split(';') if row['fusion_members'] else []
                    )
                )
    except FileNotFoundError:
        print(f"Error: The file {fighters_file} was not found.")
    return fighters


def load_supports():
    supports = []
    try:
        with open(supports_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                #print(row)
                supports.append(
                    Support(
                        name=row['name'],
                        image_path=row['image_path'],
                        category=row['category'],
                        effect=row['effect'],
                        cost=int(row['cost']),
                    )
                )
    except FileNotFoundError:
        print(f"Error: The file {supports_file} was not found.")
    return supports


all_fighters = load_fighters()
all_support = load_supports()
