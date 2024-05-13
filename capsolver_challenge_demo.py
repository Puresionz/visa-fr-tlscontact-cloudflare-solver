# -*- coding: utf-8 -*-
import time
import requests
import tls_client

API_KEY = "CAI-..."  # TODO: your api key
page_url = ''  # TODO: your page url 'https://example.com
proxy = ""  # TODO: your proxy


def call_capsolver():
    data = {
        "clientKey": API_KEY,
        "task": {
            "type": 'AntiCloudflareTask',
            "websiteURL": page_url,
            "proxy": proxy,
        }
    }
    uri = 'https://api.capsolver.com/createTask'
    res = requests.post(uri, json=data)
    resp = res.json()
    task_id = resp.get('taskId')
    if not task_id:
        print("no get taskId:", res.text)
        return
    print('created taskId:', task_id)

    while True:
        time.sleep(1)
        data = {
            "clientKey": API_KEY,
            "taskId": task_id
        }
        response = requests.post('https://api.capsolver.com/getTaskResult', json=data)
        resp = response.json()
        status = resp.get('status', '')
        if status == "ready":
            print("successfully => ", response.text)
            return resp.get('solution')
        if status == "failed" or resp.get("errorId"):
            print("failed! => ", response.text)
            return


def request_site(solution):
    # TODO if you want to use tls_client
    session = tls_client.Session(
         client_identifier="chrome_120",
        random_tls_extension_order=True
    )
    return session.get(
        page_url,
        headers=solution.get('headers'),
        cookies=solution.get('cookies'),
        proxy=proxy,
        allow_redirects=True,
    )


def main():
    # first request:
    res = request_site({})
    print('1. response status code:', res.status_code)
    if res.status_code != 403:
        print("your proxy is good and didn't get the cloudflare challenge")
        return
    elif 'window._cf_chl_opt' not in res.text:
        print('==== proxy blocked ==== ')
        return

    # call capSolver:
    solution = call_capsolver()
    if not solution:
        return

    # second request (verify solution):
    res = request_site(solution)
    print('2. response status code:', res.status_code)
    if res.status_code == 200:
        print("2. response text:\n", res.text)


if __name__ == '__main__':
    main()
