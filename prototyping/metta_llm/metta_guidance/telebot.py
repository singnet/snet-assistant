from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from pathlib import Path
from collections import deque
from datetime import datetime
import time
import threading
import requests
import yaml
import logging
import os
from motto.agents import DialogAgent

class AskSNetAgent(threading.Thread):

    def __init__(self, user_log, send_message_func):
        super().__init__(name='snet assistant', daemon=False)
        self.queue = deque()
        self.user_log = user_log
        # A callback to send messages, when the response is available
        self.send_message_func = send_message_func
        self._lock = threading.Lock()
        self._stop = False
        metta_motto_path = os.environ["METTAMOTOPATH"] if "METTAMOTOPATH" in os.environ else "."
        assistant_dir = str(Path(__file__).parent.resolve().parent.parent.parent)
        self.agent = DialogAgent(path="prototyping/metta_llm/metta_guidance/chat_process.msa",
            include_paths=[metta_motto_path, assistant_dir])
        self.dia_log("============= START =============")

    def queue_message(self, message):
        with self._lock:
            # TODO: max length?
            self.queue.appendleft(message)
        return len(self.queue)-1

    def dia_log(self, text):
        with self._lock:
            with open(self.user_log, "a") as f:
                f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {text}\n')

    def run(self):
        while not self._stop:
            while self.queue:
                if self._stop:
                    break
                # keep the job in the queue until complete
                with self._lock:
                    data = self.queue[-1]
                self.dia_log("USER: " + data)
                result = self.agent(f'(user "{data}")').content
                with self._lock:
                    self.queue.pop()
                result = result[-1] if len(result) > 0 else "Sorry, I'm having trouble answering"
                self.dia_log("SNET: " + str(result))
                self.send_message_func(result)
            time.sleep(0.2)


def get_user_str(update: Update) -> str:
    user = update.effective_user
    return str(user.id) + "_" + str(user.username)

class AskSNetBot():

    def __init__(self, cfg_file="config.yaml"):
        # Config
        cfg_file = Path(cfg_file)
        self.cwd = cfg_file.parent
        with open(cfg_file, "r") as f:
            self.config = yaml.safe_load(f)
        self.users_dir = self.cwd/self.config['users_dir']
        # default.yaml should exist there together with the folder
        # self.users_dir.mkdir(parents=True, exist_ok=True)
        with open(self.users_dir / "default.yaml", "r") as f:
            self.user_default_info = yaml.safe_load(f)
        self.config['bot_key'] = os.environ.get('ASKSNET_BOT_KEY')
        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        if 'logging_dir' in self.config:
            log_dir = self.cwd/self.config['logging_dir']
            log_dir.mkdir(parents=True, exist_ok=True)
            logname = log_dir/(datetime.today().strftime('%Y-%m-%d') + ".log")
            logging.basicConfig(filename=logname)
        # The rest of init
        self.users = {}
        self.app = None

    def run(self):
        self.app = Application.builder().token(self.config['bot_key']).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("echo", self.echo, has_args=True))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message))
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            user_info = self.get_user_info(update)
            # TODO: ignore, refuse, or other modes can be added
            if user_info is None or user_info['mode'] != 'respond':
                return
            user_info = self.get_user_info(update)
            num = user_info['agent'].queue_message(update.message.text)
            if num > 0:
                response = "[Still working on the previous message. This one is queued.]"
            else:
                return
        except Exception as e:
            self.logger.error("EXCEPTION: " + repr(e))
            response = "I'm experiencing problems"
        await update.effective_chat.send_message(response)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(' '.join(context.args))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user.is_bot:
            await update.message.reply_text("I don't talk to other bots atm")
        else:
            self.get_user_info(update)
            await update.message.reply_html(
                rf"Hello {update.effective_user.mention_html()}!\n" +
                  "You don't need to use commands. Just ask me about the SingularityNET platform and services.")

    def save_user_info(self, user) -> None:
        if user not in self.users:
            return
        user_file = self.users_dir / (user + ".yaml")
        user_info = {**self.users[user]}
        user_info.pop('agent', None)
        with open(user_file, "w") as f:
            yaml.safe_dump(user_info, f)

    def get_user_info(self, update: Update):
        user = get_user_str(update)
        if user in self.users:
            return self.users[user]
        user_file = self.users_dir / (user + ".yaml")
        if user_file.exists():
            with open(user_file, "r") as f:
                self.users[user] = yaml.safe_load(f)
        else:
            self.logger.info("NEW USER: " + user)
            self.send_direct_msg(self.config['admin_chat'], f"ADMIN: new AskSNet user {user}")
            user_info = {**self.user_default_info}
            user_info['chat_id'] = update.effective_chat.id
            if update.effective_user.is_bot:
                user_info['mode'] = 'ignore'
            self.users[user] = user_info
            self.save_user_info(user)
        self.users[user]['agent'] = AskSNetAgent(
            self.cwd/self.config['logging_dir']/(user+"_"+datetime.today().strftime('%Y-%m-%d')+".log"),
            lambda msg: self.send_direct_msg(self.users[user]['chat_id'], msg))
        self.users[user]['agent'].start()
        return self.users[user]

    def _get_url(self):
        return f'https://api.telegram.org/bot{self.config["bot_key"]}'

    def send_direct_msg(self, chat_id, text):
        ret = requests.post(self._get_url() + '/sendMessage',
            data = {'chat_id': chat_id, 'text': text})
        return ret.json()


if __name__ == '__main__':
    bot = AskSNetBot(Path(__file__).resolve().parent/"config.yaml")
    bot.run()

