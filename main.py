import requests
import json

server_url = 'http://localhost:8080'

Stream = False
# False for chat/completions
Completions_form = False

# Определяем системный промпт, который будет использоваться для модели
system_prompt = "I am an assistant, ready to help the user."
assistant_message = "Hello, how can I help?"
user_message = ""

system_form = "<|im_start|>system\n" + system_prompt + "<|im_end|>"
assistant_form = "\n<|im_start|>assistant\n" + assistant_message + "<|im_end|>"
user_form = "\n<|im_start|>user\n" + user_message + "<|im_end|>"

# Форма чата, которая содержит системный промпт и первое сообщение ассистента
chat_form = [
    {"role": "system", "content": system_prompt},
    {"role": "assistant", "content": assistant_message},
]

all_prompt = [system_form, assistant_form]

params = {
    "max_context_length": 2048,
    "max_length": 300,
    "prompt": "",
    'stream': Stream,
    "temperature": 0.7,
    "stop_sequence": ["<|im_end|>\n<|im_start|>user", "<|im_end|>\n<|im_start|>", "<|im_end|>\n<|im_start|>assistant"]
}
chat_request = {
    "max_context_length": 2048,
    "max_length": 300,
    'messages': chat_form,
    "temperature": 0.7,
    'stream': Stream
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer no-key"
}

def model_api_request():
    # Отправляем GET-запрос на сервер
    response = requests.get(server_url + "/models")
    # Выводим ID первой модели, которая вернулась от сервера
    print("Модель: " + response.json()['data'][0]['id'])


def read_stream(response):
    print("assistant: ", end="")
    text = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8").replace("data: ", "")
            try:
                if data != "[DONE]":
                    chunk = json.loads(data)  # Парсим JSON
                    if "choices" in chunk:
                        content = chunk["choices"][0]["delta"].get("content")
                    else:
                        content = chunk.get("content")
                    if content:
                        text += content
                        print(content, end="")
            except Exception as e:
                print(f"Ошибка при обработке чанка: {e}")
    print()
    return text


def api_request(user_input):
    if Completions_form:
        user_message = "\n<|im_start|>user\n" + user_input + "<|im_end|>\n<|im_start|>assistant\n"
        all_prompt.append(user_message)
        params['prompt'] = "".join(all_prompt)
        response = requests.post(server_url + "/completions", json=params, stream=Stream)
        if Stream:
            text = read_stream(response)
        else:
            request = response.json()
            text = request['content']
            print("assistant: " + text)

        all_prompt.append(text + "<|im_end|>")
    else:
        chat_form.append({"role": "user", "content": user_input})
        response = requests.post(server_url + "/v1/chat/completions", headers=headers, json=chat_request, stream=Stream)
        if Stream:
            text = read_stream(response)
        else:
            request = response.json()["choices"][0]['message']
            text = request['content']
            print("assistant: " + text)

        chat_form.append({"role": "assistant", "content": text})


def main():
    # Вызываем функцию для запроса списка моделей
    model_api_request()
    if Stream:
        print("Stream включен")
    else:
        print("Stream отключен")
    if Completions_form:
        print("Используется api /completions")
    else:
        print("Используется api /v1/chat/completions")
    # Выводим сообщение об команде окончании работы программы
    print("Выход = q")
    print()
    # Печатаем начальные сообщения чата
    for message in chat_form:
        print(message['role'] + ": " + message['content'])
    # Запускаем бесконечный цикл для обработки запросов пользователя
    while 1:
        user_input = input("user: ")
        # Если пользователь ввел 'q' или 'й', завершаем программу
        if user_input == 'q' or user_input == 'й':
            print("Выход.")
            break
        api_request(user_input)

if __name__ == '__main__':
    main()
