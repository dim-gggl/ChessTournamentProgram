class Player:
    def __init__(self, first_name, last_name, birth_date, chess_id, points=0, rank=0):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.chess_id = chess_id
        self.points = points
        self.rank = rank

    def to_dict(self):
        """
        Génère un dict contenant les infos du joueur.
        """
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date,
            "chess_id": self.chess_id,
            "points": self.points,
            "rank": self.rank,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Génère yne instance de la classe Player à partir d'un dict passé
        par la méthode load_players de la classe PlayerController.
        """
        return cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            birth_date=data["birth_date"],
            chess_id=data["chess_id"],
            points=data.get("points", 0),
            rank=data.get("rank", 0),
        )
