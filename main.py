import logging
from queue import Queue

import cherrypy
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher

from settings import NAME, PORT, TOKEN, CHAT_ID


class SimpleWebsite:
    @cherrypy.expose
    def index(self):
        return """<H1>Welcome!</H1>"""


class BotComm:
    exposed = True

    def __init__(self, TOKEN, NAME):
        super(BotComm, self).__init__()
        self.TOKEN = TOKEN
        self.NAME = NAME
        self.bot = telegram.Bot(self.TOKEN)
        try:
            self.bot.setWebhook(
                "https://{}.herokuapp.com/{}".format(self.NAME, self.TOKEN))
        except:
            raise RuntimeError("Failed to set the webhook")

        self.update_queue = Queue()
        self.dp = Dispatcher(self.bot, self.update_queue)

        self.dp.add_handler(CommandHandler("start", self._start))
        self.dp.add_handler(MessageHandler(Filters.text, self._process_update))
        self.dp.add_error_handler(self._error)

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _error(self, error):
        cherrypy.log("Error occurred - {}".format(error))

    def _start(self, bot, update):
        update.effective_message.reply_text('Милые девушки. Этот бот создан специально для вас. Сделайте заказ, например, "латте без сахара" или "черный чай с одним кусочком сахара и печенькой". А мы обеспечим оперативную доставку вашего желания прямо на ваше рабочее место')

    def _accept_order(self, bot, update):
        order_text = update.effective_message.text
        order_user = update.effective_message.from_user
        order_user_first_name = order_user.first_name
        order_user_last_name = order_user.last_name
        order_user_username = order_user.username
        text = "{first_name} {last_name} ({username}) " \
               "желает: {order}".format(first_name=order_user_first_name,
                                        last_name=order_user_last_name,
                                        username=order_user_username,
                                        order=order_text)
        self.bot.send_message(chat_id=CHAT_ID, text=text)
        update.effective_message.reply_text("Ваш заказ принят!")

    def _process_update(self, bot, update):
        chat_id = update.effective_message.chat.id
        if not chat_id == CHAT_ID:
            self._accept_order(bot, update)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the cherrypy configuration
    cherrypy.config.update({"server.socket_host": "0.0.0.0", })
    cherrypy.config.update({"server.socket_port": int(PORT), })
    cherrypy.tree.mount(SimpleWebsite(), "/")
    cherrypy.tree.mount(
        BotComm(TOKEN, NAME),
        "/{}".format(TOKEN),
        {"/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
