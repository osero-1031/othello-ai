import streamlit as st
import copy
import time
import random
import base64

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


def get_depth(difficulty):
    if difficulty == "よわよわ":
        return 0
    elif difficulty == "かんたん":
        return 1
    elif difficulty == "ふつう":
        return 3
    elif difficulty == "むずかしい":
        return 4
    else:
        return 5

def get_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_base64("background.png")

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)
st.title("♟️ オセロAI")

# 初期設定
if "game" not in st.session_state:
    st.session_state.game = Othello()

if "started" not in st.session_state:
    st.session_state.started = False

if "human_turn" not in st.session_state:
    st.session_state.human_turn = True

game = st.session_state.game

if "first_win" not in st.session_state:
    st.session_state.first_win = False

if "ten_wins" not in st.session_state:
    st.session_state.ten_wins = False

if "hundred_games" not in st.session_state:
    st.session_state.hundred_games = False

if "best_score" not in st.session_state:
    st.session_state.best_score = 0

if "win_streak" not in st.session_state:
    st.session_state.win_streak = 0

if "max_win_streak" not in st.session_state:
    st.session_state.max_win_streak = 0

if "play_count" not in st.session_state:
    st.session_state.play_count = 0

if "result_saved" not in st.session_state:
    st.session_state.result_saved = False
    
# ゲーム開始前の画面
if not st.session_state.started:

    difficulty = st.selectbox(
        "難易度を選んでください",
        ["よわよわ", "かんたん", "ふつう", "むずかしい", "さいきょう"]
    )

    order = st.radio(
        "先攻・後攻を選んでください",
        ["先攻", "後攻"]
    )

    if st.button("ゲーム開始"):
        st.session_state.difficulty = difficulty
        st.session_state.human_turn = (order == "先攻")
        st.session_state.started = True

        # 後攻なら最初にAIが打つ
        if not st.session_state.human_turn:
            ai_moves = game.valid_moves(AI)

            if ai_moves:
                if difficulty == "よわよわ":
                    move = random.choice(ai_moves)
                else:
                    depth = get_depth(difficulty)
                    _, move = minimax(game, depth, True)

                if move is not None:
                    game.make_move(move[0], move[1], AI)

            st.session_state.human_turn = True

        st.rerun()

    st.stop()

difficulty = st.session_state.difficulty

symbols = {
    EMPTY: "🟩",
    HUMAN: "⚫",
    AI: "⚪"
}
st.write("### 盤面")

moves = game.valid_moves(HUMAN)

for r in range(8):
    cols = st.columns(8)

    for c in range(8):
        with cols[c]:

            label = symbols[game.board[r][c]]

            if (
                game.board[r][c] == EMPTY
                and (r, c) in moves
                and st.session_state.human_turn
            ):
                label = "🟢"

            if st.button(label, key=f"cell_{r}_{c}"):

                if (
                    st.session_state.human_turn
                    and (r, c) in moves
                ):
                    game.make_move(r, c, HUMAN)
                    st.session_state.human_turn = False

                    ai_moves = game.valid_moves(AI)

                    if ai_moves:
                        st.write("🤖 AI考え中...")
                        time.sleep(1)

                        if difficulty == "よわよわ":
                            move = random.choice(ai_moves)
                        else:
                            depth = get_depth(difficulty)
                            _, move = minimax(game, depth, True)

                        if move is not None:
                            game.make_move(move[0], move[1], AI)

                    st.session_state.human_turn = True
                    st.rerun()

human_score, ai_score = game.score()

st.write(f"あなた（⚫）：{human_score}")
st.write(f"AI（⚪）：{ai_score}")
st.write(f"🏆 最高得点：{st.session_state.best_score}点")
st.write(f"🔥 最大連勝：{st.session_state.max_win_streak}")
st.write(f"🎮 プレイ回数：{st.session_state.play_count}回")
st.write("## 🏅 実績")

st.write(
    "🏆 初勝利！"
    if st.session_state.first_win
    else "🔒 初勝利！"
)

st.write(
    "🔥 10連勝達成！"
    if st.session_state.ten_wins
    else "🔒 10連勝達成！"
)

st.write(
    "🎮 100回プレイ！"
    if st.session_state.hundred_games
    else "🔒 100回プレイ！"
)

if not st.session_state.result_saved:
    st.session_state.play_count += 1

    # 100回プレイ実績
    if (
        st.session_state.play_count >= 100
        and not st.session_state.hundred_games
    ):
        st.session_state.hundred_games = True
        st.balloons()
        st.success("🏆 実績解除！『100回プレイ！』")

    if human_score > ai_score:
        st.success("🎉 あなたの勝ち！")

        st.session_state.win_streak += 1

        # 初勝利
        if not st.session_state.first_win:
            st.session_state.first_win = True
            st.balloons()
            st.success("🏆 実績解除！『初勝利！』")

        # 最高得点更新
        if human_score > st.session_state.best_score:
            st.session_state.best_score = human_score

        # 最大連勝更新
        if (
            st.session_state.win_streak
            > st.session_state.max_win_streak
        ):
            st.session_state.max_win_streak = (
                st.session_state.win_streak
            )

        # 10連勝実績
        if (
            st.session_state.max_win_streak >= 10
            and not st.session_state.ten_wins
        ):
            st.session_state.ten_wins = True
            st.balloons()
            st.success("🏆 実績解除！『10連勝達成！』")

    elif ai_score > human_score:
        st.success("🤖 AIの勝ち！")
        st.session_state.win_streak = 0

    else:
        st.success("🤝 引き分け！")
        st.session_state.win_streak = 0

    st.session_state.result_saved = True
if st.button("最初から"):
    st.session_state.game = Othello()
    st.session_state.started = False
    st.session_state.human_turn = True
    st.session_state.result_saved = False
    st.rerun()
