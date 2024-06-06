import os
import rumps
from dotenv import load_dotenv
import google.generativeai as genai

class GeminiMenuBarApp(rumps.App):
    def __init__(self):
        super(GeminiMenuBarApp, self).__init__("Gemini", icon="image/google-gemini-icon.svg")
        self.api_token = None  # APIトークンを保存するための変数
        self.chat_session = None  # チャットセッションを保存するための変数
        self.history = []  # 会話履歴を保持するリスト

        # .envファイルの読み込み
        load_dotenv()
        self.api_token = os.getenv('GEMINI_API_KEY')

        # メニュー項目を追加
        self.menu = [
            rumps.MenuItem("質問を入力", callback=self.ask_question),
            None,  # 仕切り
            rumps.MenuItem("API設定", callback=self.settings),
        ]

        # 質問と回答のウィンドウ
        self.question_window = rumps.Window(title="質問を入力してください", message="", ok="送信", cancel="キャンセル", dimensions=(320, 160))
        self.answer_window = rumps.Window(title="Geminiの回答", message="", ok="閉じる", cancel=None, dimensions=(320, 160))

    def ask_question(self, _):
        if not self.api_token:
            rumps.alert(title="エラー", message="まずAPIトークンを設定してください。")
            return

        response = self.question_window.run()
        if response.clicked:
            question = response.text.strip()
            if question:
                self.history.append({"role": "user", "parts": [question]})
                answer = self.query_gemini(question)
                self.history.append({"role": "model", "parts": [answer]})
                self.display_answer(question, answer)

    @rumps.clicked("API設定")
    def settings(self, _):
        response = rumps.Window(title="APIトークンを入力してください", message="Gemini APIトークンを入力してください。", ok="保存", cancel="キャンセル").run()
        if response.clicked:
            self.api_token = response.text
            rumps.alert(title="設定", message="APIトークンが保存されました。")
            # .envファイルにAPIトークンを保存
            with open('.env', 'w') as f:
                f.write(f'GEMINI_API_KEY={self.api_token}')
            # .envファイルの変更を反映
            load_dotenv()

    def query_gemini(self, question):
        genai.configure(api_key=self.api_token)

        # Model configuration
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        if not self.chat_session:
            self.chat_session = model.start_chat(history=self.history)

        try:
            response = self.chat_session.send_message(question)
            return response.text
        except Exception as e:
            return f"エラーが発生しました: {e}"

    def display_answer(self, question, answer):
        self.answer_window.message = f"質問: {question}\n\n回答: {answer}"
        self.answer_window.run()

if __name__ == "__main__":
    GeminiMenuBarApp().run()