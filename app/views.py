from collections import namedtuple
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound
from django.core.mail import send_mail
import settings
import threading
import time
planned_message = namedtuple('planned_message', ['id', 'email', 'message', 'date', 'sec'])

# test1 = planned_message(id=1, email="usikovone@gmail.com", message="olol1", date="2020/06/20T01:05:20", sec="10")
# test2 = planned_message(id=2, email="usikovone@gmail.com", message="olol2", date="2020/06/20T01:05:40", sec="60")
# test3 = planned_message(id=3, email="usikovone@gmail.com", message="olol3", date=0, sec="80")

scheduled = []
# scheduled = [test1, test2, test3]

threads = []
too_many_messages = False

def mail_sender(planned_msg):
    time.sleep(planned_msg.sec)
    send_mail(
        'Message', 
        planned_msg.message, 
        settings.EMAIL_SENDER, 
        [planned_msg.email,],
        fail_silently = False
        )
def create_and_run_thread(planned_msg):
    t = threading.Thread(target=mail_sender, args=(planned_msg,), daemon=True)
    t.start()


@require_http_methods(["GET", "POST"])
def index(request):
    """Вывод списка поставленных сообщений по GET, добавление по POST"""
    global too_many_messages
    if request.method == "POST":        
        new_item = planned_message(
            id=int(request.POST['id']),
            email=request.POST['email'],
            message = request.POST['message'],
            sec=int(request.POST['sec']),
            date=datetime.now()
        )
        if len(threads) < 30: # ограничение на всякий случай
            scheduled.insert(0, new_item) # для удобства использования slice при выводе списка
            threads.append(create_and_run_thread(new_item))
        else:
            too_many_messages = True
        return redirect(reverse_lazy('index'))

        
    data = {
        'messages': scheduled[:10], # вывод десяти последних
        'too_many': too_many_messages
    }
    return render(request, template_name="app/index.html", context=data)


def message_update(request, search_id):
    sch = {item.id: item for item in scheduled}
    if not search_id in sch:
        return HttpResponseNotFound('<h1>Item not found</h1>')
    data = {
        'id': search_id,
        'message': sch[search_id].message,
        'email': sch[search_id].email,
        'sec': sch[search_id].sec
    }

    return render(request, template_name="app/edit_message.html", context=data)

def message_create(request):
    new_id = max([msg.id for msg in scheduled]) + 1 if len(scheduled) else 1
    return render(request, template_name="app/edit_message.html", context={"id": new_id})