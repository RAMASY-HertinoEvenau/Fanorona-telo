import tkinter as tk
from tkinter import messagebox

class Noeud:
    def __init__(self, positions, joueur):
        self.positions = positions
        self.joueur = joueur

    def get_successors(self):
        successeurs = []
        for row in range(3):
            for col in range(3):
                if self.positions[(row, col)] is None:
                    new_positions = self.positions.copy()
                    new_positions[(row, col)] = self.joueur
                    successeurs.append(Noeud(new_positions, "blanc" if self.joueur == "noir" else "noir"))
        return successeurs

def minimax(noeud, profondeur, alpha, beta, maximizing_player):
    if profondeur == 0 or verifier_victoire(noeud.positions):
        return evaluer_position(noeud.positions)

    if maximizing_player:
        max_eval = float('-inf')
        for successeur in noeud.get_successors():
            eval = minimax(successeur, profondeur - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for successeur in noeud.get_successors():
            eval = minimax(successeur, profondeur - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def evaluer_position(positions):
    score = 0
    for joueur in ["noir", "blanc"]:
        # Bonus pour les alignements (plus ils sont proches de 3, plus le bonus est élevé)
        for i in range(3):
            if positions[(i, 0)] == joueur and positions[(i, 1)] == joueur:
                score += 5 if joueur == "noir" else -5
            if positions[(i, 1)] == joueur and positions[(i, 2)] == joueur:
                score += 5 if joueur == "noir" else -5
            if positions[(0, i)] == joueur and positions[(1, i)] == joueur:
                score += 5 if joueur == "noir" else -5
            if positions[(1, i)] == joueur and positions[(2, i)] == joueur:
                score += 5 if joueur == "noir" else -5
        # Bonus pour les menaces de victoire (2 pions alignés)
        if verifier_victoire(positions, joueur):
            score += 100 if joueur == "noir" else -100
    return score

def verifier_victoire(positions, joueur=None):
    """ Vérifie si un joueur a gagné (version améliorée). """
    joueurs = ["noir", "blanc"] if joueur is None else [joueur]  # Vérifie pour tous ou un seul joueur
    for joueur_actuel in joueurs:
        for i in range(3):
            if positions[(i, 0)] == joueur_actuel and positions[(i, 1)] == joueur_actuel and positions[(i, 2)] == joueur_actuel:
                return joueur_actuel
            if positions[(0, i)] == joueur_actuel and positions[(1, i)] == joueur_actuel and positions[(2, i)] == joueur_actuel:
                return joueur_actuel
        if positions[(0, 0)] == joueur_actuel and positions[(1, 1)] == joueur_actuel and positions[(2, 2)] == joueur_actuel:
            return joueur_actuel
        if positions[(0, 2)] == joueur_actuel and positions[(1, 1)] == joueur_actuel and positions[(2, 0)] == joueur_actuel:
            return joueur_actuel
    return None

class FanoronaTelo:
    def __init__(self, root):
        self.root = root
        self.root.title("Fanorona Telo")
        self.joueur_actuel = "noir"
        self.positions = {}
        self.pions_places = {"noir": 0, "blanc": 0}
        self.pions_max = 3
        self.pion_selectionne = None
        self.selection_oval = None
        self.init_ui()

    def init_ui(self):
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.canvas.grid(row=0, column=0)
        self.dessiner_grille()
        self.canvas.bind("<Button-1>", self.gerer_clic)

        self.status_label = tk.Label(self.root, text="Joueur Noir, à vous de jouer!", font=("Arial", 14))
        self.status_label.grid(row=1, column=0)

    def dessiner_grille(self):
        for i in range(3):
            x = 50 + i * 100
            self.canvas.create_line(x, 50, x, 250, fill="black")
            self.canvas.create_line(50, x, 250, x, fill="black")
        self.canvas.create_line(50, 50, 250, 250, fill="black")
        self.canvas.create_line(50, 250, 250, 50, fill="black")

        for i in range(3):
            for j in range(3):
                self.positions[(i, j)] = None

    def gerer_clic(self, event):
        x, y = event.x, event.y
        col, row = round((x - 50) / 100), round((y - 50) / 100)

        if (row, col) in self.positions:
            if self.pions_places[self.joueur_actuel] < self.pions_max:
                if self.positions[(row, col)] is None: 
                    self.placer_pion(row, col)
                    if self.joueur_actuel == "blanc": 
                        self.jouer_ia()
            else:
                self.deplacer_pion(row, col)
                
    def placer_pion(self, row, col):
        if self.positions[(row, col)] is None:
            couleur = "black" if self.joueur_actuel == "noir" else "white"
            self.canvas.create_oval(50 + col * 100 - 10, 50 + row * 100 - 10,
                                    50 + col * 100 + 10, 50 + row * 100 + 10,
                                    fill=couleur, outline="black", tags="pions")
            self.positions[(row, col)] = self.joueur_actuel
            self.pions_places[self.joueur_actuel] += 1
            self.changer_joueur()  # Switch players AFTER placing the piece

    def deplacer_pion(self, row, col):
        if self.pion_selectionne is None:
            if self.positions[(row, col)] == self.joueur_actuel:
                self.pion_selectionne = (row, col)
                self.afficher_selection(row, col)
        else:
            if self.positions[(row, col)] is None and self.est_adjacent(self.pion_selectionne, (row, col)):
                self.positions[row, col] = self.joueur_actuel
                self.positions[self.pion_selectionne] = None
                self.pion_selectionne = None

                self.canvas.delete("pions")
                self.canvas.delete(self.selection_oval)
                self.redessiner_pions()
                self.changer_joueur()

                gagnant = verifier_victoire(self.positions)
                if gagnant:
                    self.fin_de_partie(gagnant)

            else:
                self.pion_selectionne = None
                self.canvas.delete(self.selection_oval)

    def afficher_selection(self, row, col):
        """ Entoure le pion sélectionné avec un cercle rouge. """
        if self.selection_oval:  # Supprime l'ancien cercle de sélection s'il existe
            self.canvas.delete(self.selection_oval)
        self.selection_oval = self.canvas.create_oval(
            50 + col * 100 - 15, 50 + row * 100 - 15,
            50 + col * 100 + 15, 50 + row * 100 + 15,
            outline="red", width=2, tags="selection"
        )
    def redessiner_pions(self):
        for (row, col), joueur in self.positions.items():
            if joueur is not None:
                couleur = "black" if joueur == "noir" else "white"
                self.canvas.create_oval(50 + col * 100 - 10, 50 + row * 100 - 10,
                                        50 + col * 100 + 10, 50 + row * 100 + 10,
                                        fill=couleur, outline="black", tags="pions")

    def est_adjacent(self, pos1, pos2):
        row1, col1 = pos1
        row2, col2 = pos2
        return abs(row1 - row2) <= 1 and abs(col1 - col2) <= 1

    def changer_joueur(self):
        self.joueur_actuel = "blanc" if self.joueur_actuel == "noir" else "noir"
        self.status_label.config(text=f"Joueur {self.joueur_actuel}, à vous!")

    def jouer_ia(self):
        meilleur_coup = None
        meilleur_score = float('-inf')

        # Pour chaque pion de l'IA
        for (row_initial, col_initial), joueur in self.positions.items():
            if joueur == self.joueur_actuel:  # Si c'est un pion de l'IA

                # Pour chaque case adjacente
                for row_final in range(max(0, row_initial - 1), min(3, row_initial + 2)):
                    for col_final in range(max(0, col_initial - 1), min(3, col_initial + 2)):
                        if (row_final, col_final) != (row_initial, col_initial) and self.positions[(row_final, col_final)] is None:  # Si la case est libre et adjacente
                            # Simule le coup
                            positions_temp = self.positions.copy()
                            positions_temp[(row_final, col_final)] = self.joueur_actuel
                            positions_temp[(row_initial, col_initial)] = None

                            # Evalue le coup
                            score = evaluer_position(positions_temp)

                            # Met à jour le meilleur coup si nécessaire
                            if score > meilleur_score:
                                meilleur_score = score
                                meilleur_coup = ((row_initial, col_initial), (row_final, col_final))

        # Si un meilleur coup a été trouvé
        if meilleur_coup:
            (row_initial, col_initial), (row_final, col_final) = meilleur_coup

            # Effectue le déplacement
            self.positions[(row_final, col_final)] = self.joueur_actuel
            self.positions[(row_initial, col_initial)] = None

            # Met à jour l'affichage
            self.canvas.delete("pions")
            self.redessiner_pions()
            self.changer_joueur()

            # Vérifie la victoire
            gagnant = verifier_victoire(self.positions)
            if gagnant:
                self.fin_de_partie(gagnant)

    def fin_de_partie(self, gagnant):
        if gagnant:
            messagebox.showinfo("Victoire !", f"Le joueur {gagnant} a gagné !")
        else:
            messagebox.showinfo("Égalité", "Match nul !")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    jeu = FanoronaTelo(root)
    root.mainloop()