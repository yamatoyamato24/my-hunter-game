import json
import platform

# ブラウザ環境かどうかを判定
is_web = platform.system() == "Emscripten"

# 波線を防ぐための書き方
try:
    from js import window
except ImportError:
    # PCで実行している時はここを通る（jsがなくてもエラーにならない）
    window = None

def load_scores():
    """保存されたスコアを読み込む"""
    if is_web and window:
        # ブラウザのLocalStorageから取得
        try:
            data = window.localStorage.getItem("my_game_scores")
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"LocalStorage Load Error: {e}")
    else:
        # PC環境ならファイルから読み込む
        try:
            with open("scores.json", "r") as f:
                return json.load(f)
        except:
            pass
    return []

def save_scores(scores):
    """スコアを保存する"""
    if is_web and window:
        # ブラウザのLocalStorageに保存
        try:
            window.localStorage.setItem("my_game_scores", json.dumps(scores))
        except Exception as e:
            print(f"LocalStorage Save Error: {e}")
    else:
        # PC環境ならファイルに保存
        try:
            with open("scores.json", "w") as f:
                json.dump(scores, f)
        except:
            pass

def update_ranking(new_score):
    """新しいスコアを追加して上位5つを返す"""
    scores = load_scores()
    
    if new_score > 0:
        scores.append(new_score)
    
    # 重複を消したい場合は list(set(scores)) なども検討
    scores.sort(reverse=True)
    top_five = scores[:5]
    
    save_scores(top_five)
    return top_five
