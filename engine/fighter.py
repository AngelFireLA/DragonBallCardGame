class Fighter:
    def __init__(self, name, image_path, health, attack_power, effects, tags, previous_form, form_level, cost, fusion_members):
        self.name: str = name
        self.image_path: str = image_path
        self.max_health: int = health
        self.current_health: int = health
        self.attack_power: int = attack_power
        self.effects: list[str] = effects
        self.tags: list[str] = tags
        self.previous_form: str = previous_form
        self.form_level = form_level
        self.cost: int = cost
        self.fusion_members: list[str] = fusion_members
        self.reduced_cost = False
        self.temporary_health_shield = 0
        self.temporary_attack_boost = 1
        self.temporary_tags: list[str] = []
        self.is_ozaru = False

    def reset(self):
        self.current_health = self.max_health

    def is_alive(self) -> bool:
        return self.current_health > 0

    def __repr__(self):
        text= f"Fighter({self.name}, HP: {self.current_health}, AP: {self.attack_power}, Cost: {self.cost}"
        if self.is_ozaru:
            text += ", Ozaru"
        if self.reduced_cost:
            text += ", Reduced Cost"
        if self.temporary_health_shield > 1:
            text += f", Temp Shield: {self.temporary_health_shield}"
        if self.temporary_attack_boost != 1:
            text += f", Temp AP Boost: x{self.temporary_attack_boost}"
        text += ")"
        return text

