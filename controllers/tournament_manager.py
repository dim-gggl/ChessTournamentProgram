from utils.pairing import generate_pairs, generate_pairs_by_points
from models.match import Match
from models.round import Round


class TournamentManager:
    """
    Gère la “vie” d’un tournoi donné : ajout de joueurs,
    génération de rounds, saisie de résultats...
    On évite de faire la sauvegarde JSON directement ici,
    on délègue ça au TournamentController après chaque update.
    """

    def __init__(self, tournament, player_controller, tournament_view, tournament_controller=None):
        self.tournament = tournament
        self.player_controller = player_controller
        self.view = tournament_view
        self.tournament_controller = tournament_controller

    def manage(self):
        """
        Boucle d’options pour gérer le tournoi sélectionné :
        ajouter des joueurs, lancer rounds, etc.
        """
        while True:
            choice = self.view.display_tournament_menu(self.tournament)
            if choice == "1":
                self.add_players()
            elif choice == "2":
                self.start_next_round()
            elif choice == "3":
                self.enter_results()
            elif choice == "4":
                self.view.display_tournament_summary(self.tournament)
            elif choice == "q":
                break
            else:
                self.view.show_error_message("Choix invalide.")

    def add_players(self):
        """
        Ajoute des joueurs au tournoi. Vérifie que le joueur existe
        dans la liste globale (PlayerController) et qu’il n’est pas déjà dans le tournoi.
        """
        while True:
            print("\n=== Ajout de joueurs au tournoi ===")
            player = self.view.get_player_to_add()
            if not player:
                print("[INFO] Fin de l'ajout de joueurs.")
                break

            if any(p.chess_id == player.chess_id for p in self.tournament.players):
                self.view.show_error_message("Ce joueur est déjà dans le tournoi.")
            elif not any(p.chess_id == player.chess_id for p in self.player_controller.players):
                self.view.show_error_message("Ce joueur n'existe pas dans le fichier.")
            else:
                self.tournament.players.append(player)
                self.view.show_success_message(
                    "Joueur ajouté : " f"{player.first_name} {player.last_name} ({player.chess_id})"
                )

        if self.tournament_controller:
            for i, t in enumerate(self.tournament_controller.tournaments):
                if t.name == self.tournament.name:
                    self.tournament_controller.tournaments[i] = self.tournament
                    break
            self.tournament_controller.save_tournaments()

    def start_next_round(self):
        """
        Lance le prochain round. Pour le 1er round, on fait un random shuffle.
        Pour les rounds suivants, on appuie sur le ranking (points).
        """
        if self.tournament.current_round >= self.tournament.num_rounds :
            print("C'était le dernier tour !")
        elif self.tournament.rankings is not None:
            print("[INFO] Le tournoi est déjà terminé.")
            self.tournament_controller.close_tournament(self.tournament)
            return

        if self.tournament.current_round == 0:
            pairs = generate_pairs(self.tournament.players)
        else:
            # On collecte tous les matches passés pour éviter les répétitions
            previous_matches = {(m.player1, m.player2) for rnd in self.tournament.rounds for m in rnd.matches}
            pairs = generate_pairs_by_points(self.tournament.players, previous_matches)

        round_name = f"Round {int(self.tournament.current_round) + 1}"
        new_round = Round(round_name)

        for p1, p2 in pairs:
            new_match = Match(p1, p2)
            new_round.matches.append(new_match)

        self.tournament.current_round += 1
        self.tournament.rounds.append(new_round.name)
        self.view.show_success_message(f"{round_name} démarré avec succès.")

        if self.tournament_controller:
            self.tournament_controller.save_tournaments()

    def enter_results(self):
        """
        Saisit les résultats (scores) du dernier round.
        Met à jour les points de chaque joueur.
        """
        if  self.tournament.currend_round >= 0:
            self.view.show_error_message("Aucun match à mettre à jour.")
            return

        current_round = self.tournament.rounds[-1]
        for match in current_round.matches:
            print(f"Match : {str(match)}")
            score1 = self.get_score_for_player(match.player1)
            score2 = self.get_score_for_player(match.player2)
            match.score1 = score1
            match.score2 = score2
            match.player1.points += score1
            match.player2.points += score2

            round_details = f"{current_round.name} :" + str(match)
            self.tournament.rounds.append(round_details)

        current_round.end_round()
        print("[SUCCÈS] Résultats enregistrés.")

        if self.tournament_controller:
            self.tournament_controller.save_tournaments()

    def get_score_for_player(self, player):
        """Demande à l'utilisateur de saisir un score float et gère les exceptions."""
        while True:
            try:
                val = float(input(f"Score de {player.last_name} : "))
                return val
            except ValueError:
                self.view.show_error_message("Score invalide : 0 ou 1 (0.5 si match nul).")

            if self.tournament_controller:
                self.tournament_controller.save_tournaments()
