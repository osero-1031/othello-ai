import streamlit as st
import copy

EMPTY = "×"
HUMAN = "■"
AI = "□"

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]

WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, 5, 1, 1, 5, -2, 10],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [10, -2, 5, 1, 1, 5, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100]
]


class Othello:
    def __init__(self):
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]

        self.board[3][3] = AI
        self.board[3][4] = HUMAN
        self.board[4][3] = HUMAN
        self.board[4][4] = AI

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def opponent(self, player):
        return AI if player == HUMAN else HUMAN

    def can_flip(self, r, c, player):
        if self.board[r][c] != EMPTY:
            return False

        enemy = self.opponent(player)

        for dr, dc in DIRECTIONS:
            nr = r + dr
            nc = c + dc

            if not self.inside(nr, nc):
                continue

            if self.board[nr][nc] != enemy:
                continue

            nr += dr
            nc += dc

            while self.inside(nr, nc):
                if self.board[nr][nc] == EMPTY:
                    break

                if self.board[nr][nc] == player:
                    return True

                nr += dr
                nc += dc

        return False

    def valid_moves(self, player):
        moves = []

        for r in range(8):
            for c in range(8):
                if self.can_flip(r, c, player):
                    moves.append((r, c))

        return moves

    def make_move(self, r, c, player):
        enemy = self.opponent(player)
        self.board[r][c] = player

        for dr, dc in DIRECTIONS:
            nr = r + dr
            nc = c + dc
            to_flip = []

            while self.inside(nr, nc) and self.board[nr][nc] == enemy:
                to_flip.append((nr, nc))
                nr += dr
                nc += dc

            if self.inside(nr, nc) and self.board[nr][nc] == player:
                for fr, fc in to_flip:
                    self.board[fr][fc] = player

    def game_over(self):
        return (
            len(self.valid_moves(HUMAN)) == 0
            and len(self.valid_moves(AI)) == 0
        )

    def score(self):
        human = sum(row.count(HUMAN) for row in self.board)
        ai = sum(row.count(AI) for row in self.board)
        return human, ai


def evaluate(game):
    score = 0

    for r in range(8):
        for c in range(8):
            if game.board[r][c] == AI:
                score += WEIGHTS[r][c]
            elif game.board[r][c] == HUMAN:
                score -= WEIGHTS[r][c]

    return score


def minimax(game, depth, maximizing):
    if depth == 0 or game.game_over():
        return evaluate(game), None

    player = AI if maximizing else HUMAN
    moves = game.valid_moves(player)

    if not moves:
        return minimax(game, depth - 1, not maximizing)

    best_move = None

    if maximizing:
        best_score = -10**9

        for move in moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(move[0], move[1], AI)

            score, _ = minimax(
                new_game,
                depth - 1,
                False
            )

            if score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    else:
        best_score = 10**9

        for move in moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(move[0], move[1], HUMAN)

            score, _ = minimax(
                new_game,
                depth - 1,
                True
            )

            if score < best_score:
                best_score = score
                best_move = move

        return best_score, best_move


st.title("♟️ オセロAI")

if "game" not in st.session_state:
    st.session_state.game = Othello()

game = st.session_state.game

st.write("### 盤面")

symbols = {
    EMPTY: "🟩",
    HUMAN: "⚫",
    AI: "⚪"
}

st.write("### 盤面")

for r in range(8):
    cols = st.columns(8)

    for c in range(8):
        with cols[c]:
            st.button(
                symbols[game.board[r][c]],
                key=f"cell_{r}_{c}"
            )

human_score, ai_score = game.score()
st.write(f"あなた(■)：{human_score}")
st.write(f"AI(□)：{ai_score}")

if game.game_over():
    st.success("ゲーム終了！")

    if human_score > ai_score:
        st.success("あなたの勝ち！")
    elif ai_score > human_score:
        st.success("AIの勝ち！")
    else:
        st.success("引き分け！")

else:
    moves = game.valid_moves(HUMAN)

    st.write("置ける場所:", moves)

    r = st.number_input(
        "行",
        min_value=0,
        max_value=7,
        step=1
    )

    c = st.number_input(
        "列",
        min_value=0,
        max_value=7,
        step=1
    )

    if st.button("置く"):
        if (r, c) in moves:
            game.make_move(int(r), int(c), HUMAN)

            ai_moves = game.valid_moves(AI)

            if ai_moves:
                _, move = minimax(game, 5, True)
                game.make_move(move[0], move[1], AI)

            st.rerun()

        else:
            st.error("そこには置けません！")

if st.button("最初から"):
    st.session_state.game = Othello()
    st.rerun()
