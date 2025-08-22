import discord
from discord.ext import commands
import asyncio

# --- İNTENTS ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# --- ROL VE KANAL ID'LERİ ---
ROL_KAYITCI   = 1408437459057901631
ROL_ERKEK     = 1408437459007705171
ROL_KIZ       = 1408437459007705172
ROL_KAYITSIZ  = 1408437458999181421

ROL_CHAT_MUTED = 1408437458999181424  # Chat mute rolü

KANAL_REGISTER = 1408437459079139477  # Hoşgeldin mesajı buraya gelecek
KANAL_SOHBET   = 1408437459918000235  # Sohbet kanalı

# --- JAIL ---
ROL_JAIL = 1408437458999181422       # Jail rolü
KANAL_JAIL_LOG = 1408438315476058203 # Jail log kanalı

# --- BOT HAZIR ---
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

# --- HOŞGELDİN ---
@bot.event
async def on_member_join(member):
    guild = member.guild
    kayitsiz = guild.get_role(ROL_KAYITSIZ)
    if kayitsiz:
        await member.add_roles(kayitsiz)

    # 🔹 Sunucuya giren kişiye "Kayıtsız" ismi verilecek
    try:
        await member.edit(nick="Kayıtsız")
    except discord.Forbidden:
        print(f"{member} için isim değiştirilemedi (yetki yetersiz).")

    kanal = guild.get_channel(KANAL_REGISTER)
    if kanal:
        rol_kayitci = guild.get_role(ROL_KAYITCI)
        embed = discord.Embed(
            title="👋 Hoşgeldin!",
            description=f"{member.mention}, sunucumuza hoş geldin!\n"
                        f"Kayıt olmak için yetkililer seninle ilgilenecektir.\n\n"
                        f"{rol_kayitci.mention}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await kanal.send(embed=embed)

# --- KAYIT KOMUTLARI ---
@bot.command()
async def e(ctx, member: discord.Member, *, isim_yas=None):
    if ROL_KAYITCI not in [r.id for r in ctx.author.roles]:
        return await ctx.send("❌ Bu komutu sadece **Kayıtçı** rolü kullanabilir.")

    await member.add_roles(ctx.guild.get_role(ROL_ERKEK))
    await member.remove_roles(ctx.guild.get_role(ROL_KAYITSIZ))
    if isim_yas:
        await member.edit(nick=isim_yas)
    await ctx.send(f"✅ {member.mention} erkek olarak kayıt edildi!")

    # 🔹 Sohbet kanalına embedli hoşgeldin mesajı
    sohbet = ctx.guild.get_channel(KANAL_SOHBET)
    if sohbet:
        embed = discord.Embed(
            title="🎉 Yeni Üye Katıldı!",
            description=f"👋 Aramıza hoş geldin {member.mention}!\nSunucumuzda keyifli vakit geçir!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await sohbet.send(embed=embed)

@bot.command()
async def k(ctx, member: discord.Member, *, isim_yas=None):
    if ROL_KAYITCI not in [r.id for r in ctx.author.roles]:
        return await ctx.send("❌ Bu komutu sadece **Kayıtçı** rolü kullanabilir.")

    await member.add_roles(ctx.guild.get_role(ROL_KIZ))
    await member.remove_roles(ctx.guild.get_role(ROL_KAYITSIZ))
    if isim_yas:
        await member.edit(nick=isim_yas)
    await ctx.send(f"✅ {member.mention} kız olarak kayıt edildi!")

    # 🔹 Sohbet kanalına embedli hoşgeldin mesajı
    sohbet = ctx.guild.get_channel(KANAL_SOHBET)
    if sohbet:
        embed = discord.Embed(
            title="🎉 Yeni Üye Katıldı!",
            description=f"👋 Aramıza hoş geldin {member.mention}!\nSunucumuzda keyifli vakit geçir!",
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await sohbet.send(embed=embed)

@bot.command()
async def kayıtsız(ctx, member: discord.Member):
    if ROL_KAYITCI not in [r.id for r in ctx.author.roles]:
        return await ctx.send("❌ Bu komutu sadece **Kayıtçı** rolü kullanabilir.")

    await member.add_roles(ctx.guild.get_role(ROL_KAYITSIZ))
    await member.remove_roles(ctx.guild.get_role(ROL_ERKEK))
    await member.remove_roles(ctx.guild.get_role(ROL_KIZ))
    try:
        await member.edit(nick="Kayıtsız")
    except discord.Forbidden:
        await ctx.send("⚠️ Bu kullanıcının ismini değiştiremiyorum (rolüm aşağıda olabilir).")

    await ctx.send(f"↩️ {member.mention} kayıtsıza atıldı ve ismi **Kayıtsız** yapıldı!")

# --- CHAT MUTE ---
@bot.command(name="mute")
@commands.has_permissions(manage_roles=True, manage_channels=True)
async def mute(ctx, member: discord.Member, süre: int = 0, *, reason: str = "Sebep belirtilmedi"):
    guild = ctx.guild
    role = guild.get_role(ROL_CHAT_MUTED)
    if not role:
        return await ctx.send("❌ Chat mute rolü bulunamadı.")

    await member.add_roles(role, reason=reason)
    await ctx.send(f"💬🔇 {member.mention} chat mute yedi. Sebep: **{reason}**")

    if süre > 0:
        await asyncio.sleep(süre * 60)
        if role in member.roles:
            await member.remove_roles(role, reason="Chat mute süresi doldu")
            await ctx.send(f"💬🔊 {member.mention} chat mute kaldırıldı.")

@bot.command()
@commands.has_permissions(manage_roles=True, manage_channels=True)
async def cunmute(ctx, member: discord.Member):
    role = ctx.guild.get_role(ROL_CHAT_MUTED)
    if role not in member.roles:
        return await ctx.send("ℹ️ Kullanıcı chat mute değil.")
    await member.remove_roles(role, reason="Chat mute kaldırıldı")
    await ctx.send(f"💬🔊 {member.mention} chat mute kaldırıldı.")

# --- VOICE FORCE MUTE ---
@bot.command(name="vmute")
@commands.has_permissions(mute_members=True)
async def vmute(ctx, member: discord.Member, süre: int = 0, *, reason: str = "Sebep belirtilmedi"):
    if not member.voice or not member.voice.channel:
        return await ctx.send("❌ Kullanıcı ses kanalında değil.")

    try:
        await member.edit(mute=True, reason=reason)
        await ctx.send(f"🎙️🔇 {member.mention} ses kanalında susturuldu. Sebep: **{reason}**")

        if süre > 0:
            await asyncio.sleep(süre * 60)
            await member.edit(mute=False, reason="Voice mute süresi doldu")
            await ctx.send(f"🎙️🔊 {member.mention} voice mute kaldırıldı.")
    except discord.Forbidden:
        await ctx.send("❌ Botun 'Üyeleri Sustur' yetkisi yok veya rolü aşağıda.")
    except Exception as e:
        await ctx.send(f"⚠️ Hata: {e}")

@bot.command()
@commands.has_permissions(mute_members=True)
async def vunmute(ctx, member: discord.Member):
    if not member.voice or not member.voice.channel:
        return await ctx.send("❌ Kullanıcı ses kanalında değil.")

    try:
        await member.edit(mute=False, reason="Mute kaldırıldı")
        await ctx.send(f"🎙️🔊 {member.mention} voice mute kaldırıldı.")
    except discord.Forbidden:
        await ctx.send("❌ Botun 'Üyeleri Sustur' yetkisi yok veya rolü aşağıda.")
    except Exception as e:
        await ctx.send(f"⚠️ Hata: {e}")

# --- MODERASYON KOMUTLARI ---
@bot.command()
async def kick(ctx, member: discord.Member, *, sebep=None):
    if not ctx.author.guild_permissions.kick_members:
        return await ctx.send("❌ Kick yetkin yok.")
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member} sunucudan atıldı.")

@bot.command()
async def ban(ctx, member: discord.Member, *, sebep=None):
    if not ctx.author.guild_permissions.ban_members:
        return await ctx.send("❌ Ban yetkin yok.")
    await member.ban(reason=sebep)
    await ctx.send(f"⛔ {member} sunucudan banlandı.")

@bot.command()
async def clear(ctx, miktar: int):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.send("❌ Mesaj silme yetkin yok.")
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 {miktar} mesaj silindi.", delete_after=5)

# --- JAIL KOMUTLARI ---
@bot.command()
@commands.has_permissions(manage_roles=True)
async def jail(ctx, member: discord.Member, süre: int = 0, *, reason: str = "Sebep belirtilmedi"):
    role = ctx.guild.get_role(ROL_JAIL)
    if not role:
        return await ctx.send("❌ Jail rolü bulunamadı.")

    await member.add_roles(role, reason=reason)
    await ctx.send(f"🔒 {member.mention} jail'e atıldı. Sebep: **{reason}**")

    kanal = ctx.guild.get_channel(KANAL_JAIL_LOG)
    if kanal:
        embed = discord.Embed(
            title="🚨 Kullanıcı Jail'e Atıldı",
            description=f"👤 {member.mention}\n🔧 Yetkili: {ctx.author.mention}\n📝 Sebep: {reason}\n⏳ Süre: {süre} dakika" if süre > 0 else f"👤 {member.mention}\n🔧 Yetkili: {ctx.author.mention}\n📝 Sebep: {reason}\n⏳ Süre: Süresiz",
            color=discord.Color.red()
        )
        await kanal.send(embed=embed)

    if süre > 0:
        await asyncio.sleep(süre * 60)
        if role in member.roles:
            await member.remove_roles(role, reason="Jail süresi doldu")
            await ctx.send(f"🔓 {member.mention} jail'den çıkarıldı (süre doldu).")
            if kanal:
                embed = discord.Embed(
                    title="✅ Jail Süresi Doldu",
                    description=f"👤 {member.mention} otomatik olarak jail'den çıkarıldı.",
                    color=discord.Color.green()
                )
                await kanal.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unjail(ctx, member: discord.Member):
    role = ctx.guild.get_role(ROL_JAIL)
    if role not in member.roles:
        return await ctx.send("ℹ️ Kullanıcı jail'de değil.")

    await member.remove_roles(role, reason="Jail kaldırıldı")
    await ctx.send(f"🔓 {member.mention} jail'den çıkarıldı.")

    kanal = ctx.guild.get_channel(KANAL_JAIL_LOG)
    if kanal:
        embed = discord.Embed(
            title="🔓 Jail Kaldırıldı",
            description=f"👤 {member.mention}\n🔧 Yetkili: {ctx.author.mention}",
            color=discord.Color.green()
        )
        await kanal.send(embed=embed)

# --- BOTU BAŞLAT ---
bot.run("MTQwODUxMTc0MzU0NTU3NzQ4Mg.G6yYqx.uORfmLYPUEVZyxcNF3mOhhmH7bkRp7bt2BPgf8")
