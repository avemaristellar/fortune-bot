import os
import discord
from discord.ext import commands
from discord import app_commands
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TEST_GUILD_ID = 1535370230640152626

SIGN_MAP = {
    "양자리": "aries",
    "황소자리": "taurus",
    "쌍둥이자리": "gemini",
    "게자리": "cancer",
    "사자자리": "leo",
    "처녀자리": "virgo",
    "천칭자리": "libra",
    "전갈자리": "scorpio",
    "사수자리": "sagittarius",
    "염소자리": "capricorn",
    "물병자리": "aquarius",
    "물고기자리": "pisces"
}
def translate_to_korean(text):
    try:
        if len(text) <= 400:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text,
                "langpair": "en|ko"
            }
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            return data["responseData"]["translatedText"]

        parts = []
        current = ""

        for sentence in text.split(". "):
            if len(current) + len(sentence) + 2 <= 400:
                if current:
                    current += ". " + sentence
                else:
                    current = sentence
            else:
                parts.append(current)
                current = sentence

        if current:
            parts.append(current)

        translated_parts = []

        for part in parts:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": part,
                "langpair": "en|ko"
            }
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            translated_parts.append(data["responseData"]["translatedText"])

        return " ".join(translated_parts)

    except Exception as e:
        print("번역 오류:", e)
        return "운세 번역에 실패했어요. 잠시 후 다시 시도해 주세요."

SIGN_CHOICES = [
    app_commands.Choice(name="양자리", value="양자리"),
    app_commands.Choice(name="황소자리", value="황소자리"),
    app_commands.Choice(name="쌍둥이자리", value="쌍둥이자리"),
    app_commands.Choice(name="게자리", value="게자리"),
    app_commands.Choice(name="사자자리", value="사자자리"),
    app_commands.Choice(name="처녀자리", value="처녀자리"),
    app_commands.Choice(name="천칭자리", value="천칭자리"),
    app_commands.Choice(name="전갈자리", value="전갈자리"),
    app_commands.Choice(name="사수자리", value="사수자리"),
    app_commands.Choice(name="염소자리", value="염소자리"),
    app_commands.Choice(name="물병자리", value="물병자리"),
    app_commands.Choice(name="물고기자리", value="물고기자리"),
]

def get_horoscope(sign_kr, period="daily"):
    sign_en = SIGN_MAP.get(sign_kr)
    if not sign_en:
        return None

    if period == "daily":
        url = f"https://freehoroscopeapi.com/api/v1/get-horoscope/daily?sign={sign_en}"
    elif period == "weekly":
        url = f"https://freehoroscopeapi.com/api/v1/get-horoscope/weekly?sign={sign_en}"
    else:
        return None

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()["data"]
        return {
            "sign": data["sign"],
            "date": data["date"],
            "period": data["period"],
            "horoscope": translate_to_korean(data["horoscope"])
        }
    except Exception as e:
        print("운세 API 오류:", e)
        return None

class FortuneBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.test_guild = discord.Object(id=TEST_GUILD_ID)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self.test_guild)
        await self.tree.sync(guild=self.test_guild)

bot = FortuneBot()

@bot.event
async def on_ready():
    print(f"로그인 완료: {bot.user}")

@bot.tree.command(name="오늘운세", description="오늘의 별자리 운세를 알려줘요")
@app_commands.choices(별자리=SIGN_CHOICES)
async def today_fortune(interaction: discord.Interaction, 별자리: app_commands.Choice[str]):
    await interaction.response.defer()

    result = get_horoscope(별자리.value, "daily")

    if result:
        embed = discord.Embed(
            title=f"{별자리.value} 오늘운세",
            description=result["horoscope"],
            color=discord.Color.gold()
        )
        embed.add_field(name="별자리", value=별자리.value, inline=True)
        embed.add_field(name="기준 날짜", value=result["date"], inline=True)
        embed.set_footer(text=f"{interaction.user.display_name}님을 위한 참고용 운세")
    else:
        embed = discord.Embed(
            title=f"{별자리.value} 오늘운세",
            description="운세 정보를 불러오지 못했어요.",
            color=discord.Color.red()
        )
        embed.add_field(name="별자리", value=별자리.value, inline=True)
        embed.set_footer(text=f"{interaction.user.display_name}님을 위한 참고용 운세")

    await interaction.edit_original_response(embed=embed)

@bot.tree.command(name="주간운세", description="이번 주 별자리 운세를 알려줘요")
@app_commands.choices(별자리=SIGN_CHOICES)
async def weekly_fortune(interaction: discord.Interaction, 별자리: app_commands.Choice[str]):
    await interaction.response.defer()

    result = get_horoscope(별자리.value, "weekly")

    if result:
        embed = discord.Embed(
            title=f"{별자리.value} 주간운세",
            description=result["horoscope"],
            color=discord.Color.blue()
        )
        embed.add_field(name="별자리", value=별자리.value, inline=True)
        embed.add_field(name="기준 날짜", value=result["date"], inline=True)
        embed.set_footer(text=f"{interaction.user.display_name}님을 위한 참고용 운세")
    else:
        embed = discord.Embed(
            title=f"{별자리.value} 주간운세",
            description="운세 정보를 불러오지 못했어요.",
            color=discord.Color.red()
        )
        embed.add_field(name="별자리", value=별자리.value, inline=True)
        embed.set_footer(text=f"{interaction.user.display_name}님을 위한 참고용 운세")

    await interaction.edit_original_response(embed=embed)

bot.run(DISCORD_TOKEN)
