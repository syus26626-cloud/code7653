import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ==========================================
# 1. Renderをエラー停止させないためのWebサーバー
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Botは正常に稼働しています！"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# ==========================================
# 2. Discord Botのメイン処理（募集機能）
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 応募入力フォーム（モーダル）
class RecruitmentModal(discord.ui.Modal):
    def __init__(self, role_name):
        super().__init__(title=f'{role_name}への応募')
        self.role_name = role_name

        self.name = discord.ui.TextInput(
            label='お名前（またはニックネーム）',
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.name)

        self.pr = discord.ui.TextInput(
            label='自己PR・実績など',
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.pr)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f'🎉 ありがとうございます！\n**{self.role_name}**にご応募いただきました。',
            ephemeral=True # 本人にしか見えないメッセージ
        )
        # Renderのログ画面に表示させる
        print(f"【新規応募】職種: {self.role_name} | 名前: {self.name.value} | PR: {self.pr.value}")

# 職種選択プルダウン
class RecruitmentSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='デベロッパー', description='システム開発とを作る担当', emoji='💻'),
            discord.SelectOption(label='運営スタッフ', description='コミュニティの運営', emoji='🤝'),
            discord.SelectOption(label='管理者', description='プロジェクト全体の管理', emoji='👑')
        ]
        super().__init__(placeholder='希望する職種を選んでください', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # 選択された職種の入力フォームを開く
        await interaction.response.send_modal(RecruitmentModal(self.values[0]))

class RecruitmentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RecruitmentSelect())

@bot.event
async def on_ready():
    print(f'ログイン完了: {bot.user}')

# !recruit と打つとパネルが出るコマンド
@bot.command()
async def recruit(ctx):
    embed = discord.Embed(
        title="✨ スタッフ募集 ✨",
        description="下のメニューから希望する職種を選択してご応募ください。",
        color=0x00b0f4
    )
    await ctx.send(embed=embed, view=RecruitmentView())

# ==========================================
# 3. プログラムの起動
# ==========================================
if __name__ == '__main__':
    # Webサーバーを裏で動かす
    keep_alive()
    
    # Discord Botを起動する
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("エラー: DISCORD_TOKENが設定されていません。")
