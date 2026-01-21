import csv
import random

from engine.fighter import Fighter
from engine.support import Support

initial_hand_size = 4
max_active_fighters = 4
initial_ki_amount = 2
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

def generate_interesting_decks(fighters, supports, n=10):
    # pick n fighter that are base form and aren't fusions
    base_fighters = [f for f in fighters if f.previous_form == "" and not f.fusion_members]
    random.shuffle(base_fighters)
    selected_fighters = base_fighters[:n]
    # get all fusions whom all components are amongst selected fighters
    fusion_fighters = [f for f in fighters if f.fusion_members]
    for i in range(3):
        for fighter in fusion_fighters:
            if all(any(member in sf.name for sf in selected_fighters) for member in fighter.fusion_members):
                selected_fighters.append(fighter)

    # get all fighters who are evolutions of the selected fighters
    evolution_fighters = [f for f in fighters if f.previous_form != ""]
    for fighter in selected_fighters:
        evolutions = [f for f in evolution_fighters if f.previous_form in fighter.name and f not in selected_fighters]
        selected_fighters.extend(evolutions)
        selected_fighters = list(set(selected_fighters))

    # pick n random supports
    random.shuffle(supports)
    selected_supports = supports[:n]
    return selected_fighters + selected_supports

all_fighters = load_fighters()
all_support = load_supports()
