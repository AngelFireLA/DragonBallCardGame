class Support:
    def __init__(self, name, image_path, category, effect, cost):
        self.name: str = name
        self.image_path: str = image_path
        self.category: str = category
        self.effect: str = effect
        self.cost: int = cost