from datetime import datetime
from models.match import Match
import random
from utils.ansify import ansify


class Round:
    def __init__(self, tournament, number: int = 0, **kwargs):
        self.tournament = tournament
        self.number = number
        self.name = f"Round {self.number}"
        self.matches = kwargs.get("matches", [])
        self.start_time = kwargs.get("start_time", datetime.now().strftime("%x - %X"))
        self.end_time = kwargs.get("end_time", None)

    @property
    def is_first(self):
        """Returns True when the round is the first one"""
        return self.number == 1

    @property
    def is_last(self):
        """Returns True when the round is the last one"""
        return self.number == self.tournament.num_rounds

    @property
    def is_finished(self):
        """Returns True when the round is finished"""
        return self.end_time and all(match.is_over for match in self.matches)

    def match_players(self):
        """Public method: simply delegates to private methods."""
        if self.is_first:
            return self._as_first_round()
        else:
            return self._while_not_first()

    def _as_first_round(self):
        """Logic reserved for the first round."""
        shuffled = self.tournament.players[:]
        random.shuffle(shuffled)
        if len(shuffled) % 2 != 0:
            exempt_player = shuffled.pop(0)
            exempt_player.points += 1
            print("\n" * 100)
            print(
                ansify(
                    f"\n\n\n\n\t\t\tch_up([INFO]) "
                    f"\n\t\tbld({exempt_player.name}) n'a pas d'adversaire. "
                    f"\n\t\tbld(1 point pour le premier round !)\n\n"
                )
            )
            input("\tAppuyez sur ENTRÉE pour continuer")

        matches = []
        for i in range(0, len(shuffled), 2):
            matches.append(Match(shuffled[i], shuffled[i + 1]))
        self.matches = matches
        return self.matches

    def _while_not_first(self):
        """Logical for all subsequent rounds."""
        players_sorted = self.tournament.rank_players()[:]
        matches = []
        previous_matches = {(m.player1, m.player2) for rnd in self.tournament.rounds for m in rnd.matches}
        while players_sorted:
            p1 = players_sorted.pop(0)
            paired = False
            for i, p2 in enumerate(players_sorted):
                if (p1, p2) not in previous_matches and (p2, p1) not in previous_matches:
                    p2 = players_sorted.pop(i)
                    matches.append(Match(p1, p2))
                    paired = True
                    break
                elif ((p1, p2) in previous_matches or (p2, p1) in previous_matches) and len(players_sorted) == 1:
                    p2 = players_sorted.pop(i)
                    matches.append(Match(p1, p2))
                    paired = True

            if not paired:
                p1.points += 1
                print("\n" * 100)
                print(
                    ansify(
                        f"\n\t\t\tch_up([INFO]) "
                        f"\n\t\tbld({p1.name}) n'a pas d'adversaire. "
                        f"\n\t\tbld(1 point !)\n\n"
                    )
                )
                input("\tAppuyez sur ENTRÉE pour continuer")

        self.matches = matches
        return self.matches

    def __str__(self):
        description = ""
        if self.is_finished:
            description += f"\t\t\tttl_blu({self.name}) :\n\t\tbld_it(Matches) : \n"
            for i, match in enumerate(self.matches):
                description += f"\nttl_blu({i + 1}) ~ {str(match)}"
            return ansify(description)
        else:
            description += f"\tb_blue({self.name}) en cours. " f"\n\tEn attente des résultats.\n\n"
            for match in self.matches:
                description += f"\n\t~ {str(match)}"
            return ansify(description)
