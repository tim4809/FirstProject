import threading
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

# 設置 Channel Access Token
channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN  # 從 Django 設定檔中取得 Channel Access Token
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)  # 從 Django 設定檔中取得 Channel Secret

def send_push_message(user_id, message):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        print("訊息推播成功！->"+message)
    except Exception as e:
        print("訊息推播失敗，錯誤訊息：", e)

def listen_terminal_input():
    while True:
        user_input = input("")
        if user_input.lower() == 'exit':
            break
        else:
            user_id = 'U6273701bdea0ff27b9952b4572594f63'  # 用戶的 Line ID
            send_push_message(user_id, user_input)

# 啟動監聽終端機輸入的線程
terminal_input_thread = threading.Thread(target=listen_terminal_input)
terminal_input_thread.start()

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()



        for event in events:
            if isinstance(event, MessageEvent):
                print(event.source.user_id)
                print("已接收:"+event.message.text)
                line_bot_api.reply_message(event.reply_token, TextSendMessage("已接收"))

        # 等待終端機輸入線程結束
        terminal_input_thread.join()

        return HttpResponse()
    else:
        return HttpResponseBadRequest()