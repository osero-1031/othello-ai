import streamlit as st
import copy
import time
import random
import json
import os

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
        self.board = [
            [EMPTY for _ in range(8)]
            for _ in range(8)
        ]

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

            while (
                self.inside(nr, nc)
                and self.board[nr][nc] == enemy
            ):
                to_flip.append((nr, nc))

                nr += dr
                nc += dc

            if (
                self.inside(nr, nc)
                and self.board[nr][nc] == player
            ):

                for fr, fc in to_flip:
                    self.board[fr][fc] = player

    def game_over(self):

        return (
            len(self.valid_moves(HUMAN)) == 0
            and len(self.valid_moves(AI)) == 0
        )

    def score(self):

        human = sum(
            row.count(HUMAN)
            for row in self.board
        )

        ai = sum(
            row.count(AI)
            for row in self.board
        )

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

    # 打てる場所がない場合
    if not moves:
        return minimax(
            game,
            depth - 1,
            not maximizing
        )

    best_move = None

    if maximizing:

        best_score = -10**9

        for move in moves:

            new_game = copy.deepcopy(game)

            new_game.make_move(
                move[0],
                move[1],
                AI
            )

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

            new_game.make_move(
                move[0],
                move[1],
                HUMAN
            )

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

CHEAT_CODES = {
    "WINNER": "次のゲームで勝利扱い",
    "MAX": "最高得点を最大化",
    "RANKUP": "ランクアップ",
    "100GAMES": "100回プレイ達成",
    "RESET": "データをリセット"
}

def use_cheat_code(code):

    if code == "WINNER":
        st.session_state.cheat_win = True
        return "🏆 次のゲームで勝利扱いになります！"

    elif code == "MAX":
        st.session_state.best_score = 64
        save_data()
        return "🏆 最高得点が64点になりました！"

    elif code == "RANKUP":
        st.session_state.cheat_rankup = True
        save_data()
        return "⬆️ ランクアップしました！"

    elif code == "100GAMES":
        st.session_state.play_count = 100
        st.session_state.hundred_games = True
        save_data()
        return "🎮 100回プレイ実績を解除しました！"

    elif code == "RESET":
        return "⚠️ リセットはまだ使えません"

    else:
        return "❌ チートコードが違います"

# =========================
# データ保存
# =========================

DATA_FILE = "othello_data.json"


def save_data():

    data = {
        "player_name": st.session_state.get(
            "player_name",
            "プレイヤー"
        ),

        "best_score": st.session_state.get(
            "best_score",
            0
        ),

        "win_count": st.session_state.get(
            "win_count",
            0
        ),

        "play_count": st.session_state.get(
            "play_count",
            0
        ),

        "win_streak": st.session_state.get(
            "win_streak",
            0
        ),

        "max_win_streak": st.session_state.get(
            "max_win_streak",
            0
        ),

        "first_win": st.session_state.get(
            "first_win",
            False
        ),

        "ten_wins": st.session_state.get(
            "ten_wins",
            False
        ),

        "hundred_games": st.session_state.get(
            "hundred_games",
            False
        ),

        "rank_level": st.session_state.get(
            "rank_level",
            0
        )
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_data():

    if os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return {}

# =========================
# 初期データ読み込み
# =========================

saved_data = load_data()


if "player_name" not in st.session_state:

    st.session_state.player_name = saved_data.get(
        "player_name",
        "プレイヤー"
    )


if "best_score" not in st.session_state:

    st.session_state.best_score = saved_data.get(
        "best_score",
        0
    )


if "win_count" not in st.session_state:

    st.session_state.win_count = saved_data.get(
        "win_count",
        0
    )


if "play_count" not in st.session_state:

    st.session_state.play_count = saved_data.get(
        "play_count",
        0
    )


if "win_streak" not in st.session_state:

    st.session_state.win_streak = saved_data.get(
        "win_streak",
        0
    )


if "max_win_streak" not in st.session_state:

    st.session_state.max_win_streak = saved_data.get(
        "max_win_streak",
        0
    )


if "first_win" not in st.session_state:

    st.session_state.first_win = saved_data.get(
        "first_win",
        False
    )


if "ten_wins" not in st.session_state:

    st.session_state.ten_wins = saved_data.get(
        "ten_wins",
        False
    )
    if "ten_games" not in st.session_state:

    st.session_state.ten_games = saved_data.get(
        "ten_games",
        False
    )


if "five_wins" not in st.session_state:

    st.session_state.five_wins = saved_data.get(
        "five_wins",
        False
    )


if "hundred_games" not in st.session_state:

    st.session_state.hundred_games = saved_data.get(
        "hundred_games",
        False
    )


if "rank_level" not in st.session_state:

    st.session_state.rank_level = saved_data.get(
        "rank_level",
        0
    )


if "cheat_win" not in st.session_state:

    st.session_state.cheat_win = False


if "cheat_rankup" not in st.session_state:

    st.session_state.cheat_rankup = False

# =========================
# ランク
# =========================

RANKS = [
    "初心者",
    "ルーキー",
    "プロ",
    "マスター",
    "オセロ名人"
]


def get_rank():

    level = st.session_state.rank_level

    if level < 0:
        level = 0

    if level >= len(RANKS):
        level = len(RANKS) - 1

    return RANKS[level]

# =========================
# プレイヤー情報
# =========================

st.write("## 👤 プレイヤー情報")

st.write(
    f"👤 名前：{st.session_state.player_name}"
)

st.write(
    f"🏆 ランク：{get_rank()}"
)

st.write(
    f"🎮 プレイ回数：{st.session_state.play_count}回"
)

st.write(
    f"🏆 勝利数：{st.session_state.win_count}"
)

st.write(
    f"🔥 最大連勝：{st.session_state.max_win_streak}"
)

st.write(
    f"⭐ 最高得点：{st.session_state.best_score}点"
)

# =========================
# プレイヤー名登録
# =========================

st.title("♟️ オセロAI")


if "player_name_set" not in st.session_state:

    st.session_state.player_name_set = False


if not st.session_state.player_name_set:

    st.write("## 👤 プレイヤー名を登録")

    player_name = st.text_input(
        "プレイヤー名を入力してください",
        value=st.session_state.player_name
    )

    if st.button("名前を決定"):

        if player_name.strip() != "":

            st.session_state.player_name = player_name

            st.session_state.player_name_set = True

            save_data()

            st.success(
                f"ようこそ、{player_name}さん！"
            )

            st.rerun()

        else:

            st.error(
                "プレイヤー名を入力してください"
            )

    st.stop()

# =========================
# 初期設定
# =========================

if "game" not in st.session_state:

    st.session_state.game = Othello()


if "started" not in st.session_state:

    st.session_state.started = False


if "human_turn" not in st.session_state:

    st.session_state.human_turn = True


if "result_saved" not in st.session_state:

    st.session_state.result_saved = False


game = st.session_state.game


if not st.session_state.started:

    st.write(
        f"👤 {st.session_state.player_name}さん、ゲームを始めよう！"
    )

    difficulty = st.selectbox(
        "難易度を選んでください",
        [
            "よわよわ",
            "かんたん",
            "ふつう",
            "むずかしい",
            "さいきょう"
        ]
    )

    order = st.radio(
        "先攻・後攻を選んでください",
        [
            "先攻",
            "後攻"
        ]
    )


    if st.button("🎮 ゲーム開始"):

        st.session_state.difficulty = difficulty

        st.session_state.human_turn = (
            order == "先攻"
        )

        st.session_state.started = True

        st.session_state.result_saved = False


        # 後攻ならAIが先に打つ

        if not st.session_state.human_turn:

            ai_moves = game.valid_moves(AI)


            if ai_moves:

                if difficulty == "よわよわ":

                    move = random.choice(
                        ai_moves
                    )

                else:

                    depth = get_depth(
                        difficulty
                    )

                    _, move = minimax(
                        game,
                        depth,
                        True
                    )


                if move is not None:

                    game.make_move(
                        move[0],
                        move[1],
                        AI
                    )


            st.session_state.human_turn = True


        st.rerun()


    st.stop()

difficulty = st.session_state.difficulty

# =========================
# チートコード
# =========================

with st.expander("🔐 隠しコマンド"):

    cheat_code = st.text_input(
        "チートコードを入力してください",
        type="password"
    )


    if st.button("チートコードを実行"):

        result = use_cheat_code(
            cheat_code.upper()
        )

        st.success(result)

        st.rerun()

# =========================
# オセロ盤
# =========================

symbols = {
    EMPTY: "🟩",
    HUMAN: "⚫",
    AI: "⚪"
}

st.write("## 🎮 オセロ盤")

moves = game.valid_moves(HUMAN)

for r in range(8):

    cols = st.columns(8)

    for c in range(8):

        with cols[c]:

            label = symbols[game.board[r][c]]

            # 打てる場所を緑の丸で表示
            if (
                game.board[r][c] == EMPTY
                and (r, c) in moves
                and st.session_state.human_turn
            ):

                label = "🟢"


            if st.button(
                label,
                key=f"cell_{r}_{c}"
            ):

                if (
                    st.session_state.human_turn
                    and (r, c) in moves
                ):

                    # プレイヤーの手
                    game.make_move(
                        r,
                        c,
                        HUMAN
                    )

                    st.session_state.human_turn = False


                    # AIの手
                    ai_moves = game.valid_moves(AI)


                    if ai_moves:

                        st.write(
                            "🤖 AI考え中..."
                        )

                        time.sleep(1)


                        if (
                            difficulty
                            == "よわよわ"
                        ):

                            move = random.choice(
                                ai_moves
                            )

                        else:

                            depth = get_depth(
                                difficulty
                            )

                            _, move = minimax(
                                game,
                                depth,
                                True
                            )


                        if move is not None:

                            game.make_move(
                                move[0],
                                move[1],
                                AI
                            )


                    st.session_state.human_turn = True

                    st.rerun()

# =========================
# スコア
# =========================

human_score, ai_score = game.score()

st.write(
    f"⚫ {st.session_state.player_name}："
    f"{human_score}個"
)

st.write(
    f"⚪ AI：{ai_score}個"
)

# =========================
# ゲーム終了
# =========================

if game.game_over():

    st.success("🎮 ゲーム終了！")


    # 1ゲームにつき1回だけ保存
    if not st.session_state.result_saved:

        # プレイ回数を増やす
        st.session_state.play_count += 1


        # プレイヤーの勝利
        if human_score > ai_score:

            st.success(
                "🎉 あなたの勝ち！"
            )

            st.session_state.win_count += 1

            st.session_state.win_streak += 1


            # 初勝利
            if not st.session_state.first_win:

                st.session_state.first_win = True

                st.balloons()

                st.success(
                    "🏆 実績解除！初勝利！"
                )


            # 最大連勝更新
            if (
                st.session_state.win_streak
                > st.session_state.max_win_streak
            ):

                st.session_state.max_win_streak = (
                    st.session_state.win_streak
                )


            # 10連勝
            if (
                st.session_state.win_streak >= 10
                and not st.session_state.ten_wins
            ):

                st.session_state.ten_wins = True

                st.balloons()

                st.success(
                    "🔥 実績解除！10連勝達成！"
                )


            # ランクアップ
            if (
                st.session_state.win_count >= 5
                and st.session_state.rank_level < 1
            ):

                st.session_state.rank_level = 1


            if (
                st.session_state.win_count >= 15
                and st.session_state.rank_level < 2
            ):

                st.session_state.rank_level = 2


            if (
                st.session_state.win_count >= 30
                and st.session_state.rank_level < 3
            ):

                st.session_state.rank_level = 3


            if (
                st.session_state.win_count >= 50
                and st.session_state.rank_level < 4
            ):

                st.session_state.rank_level = 4


        # AIの勝利
        elif ai_score > human_score:

            st.error(
                "🤖 AIの勝ち！"
            )

            st.session_state.win_streak = 0


        # 引き分け
        else:

            st.warning(
                "🤝 引き分け！"
            )

            st.session_state.win_streak = 0


        # 最高得点更新
        if human_score > st.session_state.best_score:

            st.session_state.best_score = human_score


        # 100回プレイ
        if (
            st.session_state.play_count >= 100
            and not st.session_state.hundred_games
        ):

            st.session_state.hundred_games = True

            st.balloons()

            st.success(
                "🏆 実績解除！100回プレイ！"
            )


        # データ保存
        save_data()


        # 保存済みにする
        st.session_state.result_saved = True

st.write("## 🏅 実績")

st.write(
    "🏆 初勝利"
    if st.session_state.first_win
    else "🔒 初勝利"
)

st.write(
    "🎮 10回プレイ"
    if st.session_state.ten_games
    else "🔒 10回プレイ"
)

st.write(
    "🔥 5連勝"
    if st.session_state.five_wins
    else "🔒 5連勝"
)

st.write(
    "🎮 100回プレイ"
    if st.session_state.hundred_games
    else "🔒 100回プレイ"
)

st.write(
    "🔥 10連勝"
    if st.session_state.ten_wins
    else "🔒 10連勝"
)

# =========================
# 最初から
# =========================

if st.button("🔄 最初から"):

    st.session_state.game = Othello()

    st.session_state.started = False

    st.session_state.human_turn = True

    st.session_state.result_saved = False

    st.rerun()
