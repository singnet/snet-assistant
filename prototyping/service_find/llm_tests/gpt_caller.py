import itertools
from enum import Enum
from typing import Dict, Any
import json
import logging
import os
import openai
import sys
import time
import openai.error
logger = logging.getLogger()
#gpt_model_name = 'text-davinci-003'  # 'gpt-3.5-turbo'#
gpt_model_name = 'gpt-3.5-turbo'


class AgentOutputParser:

    def parse(self, text: str) -> Any:
        cleaned_output = text.strip()
        cleaned_output = cleaned_output.replace('AI: ', '')
        cleaned_output = cleaned_output.replace("```", "").replace("```", "")
        cleaned_output = cleaned_output.strip()
        # chatgpt might forget about json when answering
        if '{' in cleaned_output:
            response = json.loads(cleaned_output)
        else:
            return {"action": "Answer", "action_input": cleaned_output}
        return response

class MessageType(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"

    def to_dict(self, content: str) -> Dict[str, str]:
        return {"role": self.value, "content": content}


class Message:
    def __init__(self, message_type: MessageType, content: str):
        self.type = message_type
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.type.value, "content": self.content}


class OpenAIChat:
    def __init__(self, model_name, temperature):
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.model_name = model_name
        self.temperature = temperature
        self.response_timeout = 20

    def __run_chat_completion_insist(self, prompt, temperature):
        response = None
        t1 = time.time()
        while response is None:
            try:
                self.log.debug("__run_chat_completion_insist run: {prompt}")
                response = openai.ChatCompletion.create(model=self.model_name, messages=prompt, temperature=temperature)
            except openai.error.RateLimitError as e:
                if time.time() - t1 > self.response_timeout:
                    self.log.debug("__run_chat_completion_insist ERROR, TIMEOUT")
                    return None
                self.log.debug("__run_chat_completion_insist RETRY")
                response = None
        self.log.debug(f"__run_chat_completion_insist Processing time: {time.time() - t1}")
        return response

    def __get_chat_completion_response(self, prompt, temperature=0.5):
        try:
            prompt = [m.to_dict() for m in prompt]
            self.log.info(f" __get_chat_completion_response call")
            response = self.__run_chat_completion_insist(prompt, temperature)
            if response is not None and "choices" in response and len(response["choices"]) > 0 and "message" in response["choices"][0]:
                return response['choices'][0]['message']['content']
            else:
                return ''
        except Exception as ex:
            self.log.info(f"get_response error: {ex}")
            return ''

    def __run_completion_insist(self, prompt, temperature):
        response = None
        t1 = time.time()
        while response is None:
            try:
                response = openai.Completion.create(model=self.model_name, prompt=prompt,
                                                    request_timeout=self.response_timeout,
                                                    temperature=temperature, max_tokens=256)
            except openai.error.RateLimitError as e:
                if time.time() - t1 > self.response_timeout:
                    self.log.debug("__run_completion_insist ERROR, TIMEOUT")
                    return None
                self.log.debug("__run_completion_insist RETRY")
                response = None
        self.log.debug(f"__run_completion_insist Processing time: {time.time() - t1}")
        return response

    def __get_completion_response(self, prompt, temperature=0.5):
        try:
            new_prompt = []
            for m in prompt:
                prefix = f"{m.type.value}:"
                if m.type == MessageType.ASSISTANT and m.content.strip().find(prefix) != 0:
                    new_prompt.append(prefix + m.content.strip())
                else:
                    new_prompt.append(m.content)
            prompt = "\n".join(new_prompt)
            logger.info(f" __get_completion_response call: {prompt}")
            response = self.__run_completion_insist(prompt, temperature)
            if response is not None and "choices" in response and len(response["choices"]) > 0 and "text" in response["choices"][0]:
                return response["choices"][0]["text"]
            else:
                return ''

        except Exception as ex:
            logger.info(f"get_response error: {ex}")
            return ''

    def __call__(self, *message: Message) -> Message:
        # convert messages to dicts
        logger.debug("passing to chatgpt: %s", message)
        if self.model_name == "gpt-3.5-turbo":
            text = self.__get_chat_completion_response(message, self.temperature)
        else:
            text = self.__get_completion_response(message, self.temperature)
        logger.debug('chatgpt response %s', text)
        return Message(MessageType.ASSISTANT, text)


class ChatHistory:
    def __init__(self, chatbot: OpenAIChat):
        self.chatbot = chatbot
        self.history = []

    def add_history(self, msg: Message):
        self.history.append(msg)

    def __call__(self, add_to_history: bool, *message: Message) -> Message:
        if add_to_history:
            self.history.extend(message)
            reply = self.chatbot(*self.history)
        else:
            reply = self.chatbot(*(self.history + [*message]))
        self.history.append(reply)
        return reply


def sys_exit(*args, **kwargs):
    sys.exit(0)


def to_dict(self, content: str) -> Dict[str, str]:
    return {"role": self.value, "content": content}


class OpenAIChatCaller:


    def __init__(self):
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)


        self.info = ""
        self.items = []

        self.ch = OpenAIChat(temperature=0, model_name=gpt_model_name)
        # self.resp = self.ch(Message(MessageType.SYSTEM, self.template_guide.format(info=self.info))).content
        self.history = ChatHistory(self.ch)
        self.parser = AgentOutputParser()
        self.has_stop_action = False

    def __send_message(self, message, add_to_history=True):
        self.log.info(f"send_message called with arg: {message}")
        ai_resp = self.history(add_to_history, message)
        v = ai_resp.content.strip()
        return v



    def get_response(self, sentence):
        result = {"reply": None}
        try:
            message = Message(MessageType.USER, sentence)
            reply = self.__send_message(message)
            self.log.info(f"get_response got result: {reply}")
            result.update({"reply": reply})
        except Exception as ex:
            self.log.info(f"get_response error: {ex}")
            result.update({"reply": "I have some problems during response generation. Please repeat"})
        return result



