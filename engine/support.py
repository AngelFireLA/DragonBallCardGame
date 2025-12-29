from engine.fighter import Fighter


class Support:
    def __init__(self, name, image_path, category, effect, cost):
        self.name: str = name
        self.image_path: str = image_path
        self.category: str = category
        self.effect: str = effect
        self.cost: int = cost

    def apply_effect(self, battle, owner):
        if self.name == "Chichi":
            for fighter in owner.active_fighters:
                if "Goku" in fighter.name:
                    fighter.attack_power = int(fighter.attack_power * 1.5)
            for card in owner.hand:
                if "Gohan" in card.name or "Goten" in card.name:
                    card.reduced_cost = True
        elif self.name == "Bulma":
            for fighter in owner.active_fighters:
                if "Vegeta" in fighter.name:
                    fighter.attack_power *= 2
            for card in owner.hand:
                if "Trunks" in card.name in card.name:
                    card.reduced_cost = True
        elif self.name == "SSJ2":
            possible_boosted = [fighter for fighter in owner.active_fighters if "saiyan" in fighter.tags and fighter.form_level < 2 and not fighter.is_ozaru]
            chosen_fighter: Fighter = owner.get_chosen_card("permanent_stat_multiplier_ssj2", possible_boosted)
            chosen_fighter.form_level = 2
            chosen_fighter.current_health *= 2
            chosen_fighter.attack_power *= 2
        elif self.name == "SSB":
            possible_boosted = [fighter for fighter in owner.active_fighters if "saiyan" in fighter.tags and fighter.form_level < 2 and not fighter.is_ozaru]
            if not possible_boosted:
                return
            chosen_fighter: Fighter = owner.get_chosen_card("permanent_stat_multiplier_ssb", possible_boosted)
            chosen_fighter.form_level = 5
            chosen_fighter.current_health *= 4
            chosen_fighter.attack_power *= 4
        elif self.name == "Kaioken":
            chosen_fighter: Fighter = owner.get_chosen_card("temporary_stat_multiplier_kaioken", owner.active_fighters)
            chosen_fighter.temporary_attack_boost = 2
        elif self.name == "Kaioken x10":
            chosen_fighter: Fighter = owner.get_chosen_card("temporary_stat_multiplier_kaiokenx10", owner.active_fighters)
            chosen_fighter.temporary_attack_boost = 4
            chosen_fighter.current_health -= chosen_fighter.attack_power*2
        elif self.name == "Trio de Renard":
            renards = [fighter for fighter in owner.active_fighters if "Fox" in fighter.name]
            compte_renard = len(renards)
            if compte_renard == 2:
                master_fox = owner.deck.get_card_of_name("Master Fox")
                if master_fox is not None:
                    owner.active_fighters.append(master_fox)
                    owner.deck.remove(master_fox)
                    for renard in renards:
                        owner.active_fighters.remove(renard)
        elif self.name == "Ozaru":
            saiyan_fighters = [fighter for fighter in owner.active_fighters if "saiyan" in fighter.tags and fighter.form_level == 1]
            if not saiyan_fighters:
                return
            chosen_fighter: Fighter = owner.get_chosen_card("transform_ozaru", saiyan_fighters)
            chosen_fighter.is_ozaru = True
            chosen_fighter.temporary_health_shield = 25000
            chosen_fighter.temporary_attack_boost = 10000 // chosen_fighter.attack_power
            chosen_fighter.tags.append("berserk")
            chosen_fighter.temporary_tags.append("berserk")
        elif self.name == "Golden Ozaru":
            saiyan_fighters = [fighter for fighter in owner.active_fighters if "saiyan" in fighter.tags and fighter.form_level <=3]
            if not saiyan_fighters:
                return
            chosen_fighter: Fighter = owner.get_chosen_card("transform_ozaru", saiyan_fighters)
            if chosen_fighter.is_ozaru:
                owner.remaining_ki += 2
            chosen_fighter.temporary_health_shield = 30000
            chosen_fighter.temporary_attack_boost = 20000 // chosen_fighter.attack_power
            chosen_fighter.tags.append("berserk")
            chosen_fighter.temporary_tags.append("berserk")
        elif self.name == "Epée de Genki-dama":
            trunks = None
            for fighter in owner.active_fighters:
                if fighter.name == "Miraï Trunks SSJ2++":
                    trunks = fighter
                    break
            if not trunks:
                return

            trunks_max = None
            for card in owner.hand:
                if card.name == "Miraï Trunks Max":
                    trunks_max = card
                    break
            if not trunks_max:
                return

            owner.active_fighters.remove(trunks)
            owner.active_fighters.append(trunks_max)
            owner.hand.remove(trunks_max)

    def __repr__(self):
        return f"Support({self.name}, Effect: {self.effect}, Cost: {self.cost})"
