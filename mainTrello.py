import sys
import time

import requests

key = input('Enter your Trello API key: ')
token = input('Enter your Trello API token: ')
user_border_id = input('Enter your Trello border id (In url before table name): ')

auth_params = {
    'key': key,
    'token': token,
}

base_url = 'https://api.trello.com/1/{}'
board_id = user_border_id
long_id = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()['id']

column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()


def findTask(to_find: str):
    for column in column_data:
        column_tasks = requests.request('GET', base_url.format('lists') + '/' + column['id'] + '/cards',
                                        params=auth_params).json()
        for task in column_tasks:
            if to_find == task['name']:
                print('"{}" is in "{}" table'.format(to_find, column['name']))
                return True
            else:
                return False


def read():
    for column in column_data:
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print('\n', column['name'], '-' * 30 + '> Items in this table:', len(task_data))
        if not task_data:
            print('\t' + 'There are no tasks!')
            continue
        for task in task_data:
            print('\t' + task['name'])


def create(name: str, column_name: str):
    if not findTask(name):
        print('shit')
        read()
        exit()
    for column in column_data:
        if column['name'] == column_name:
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            read()
            break
        else:
            print('Column "{}" was not found'.format(column_name))


def move(name: str, column_name: str):
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                task_id = task['id']
                break
        if task_id:
            break
    for column in column_data:
        if column['name'] == column_name:
            requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                         data={'value': column['id'], **auth_params})
            read()
            break
        else:
            print('Column "{}" was not found'.format(column_name))


def delete(name: str, column_name: str):
    for column in column_data:
        if column['name'] == column_name:
            column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards',
                                        params=auth_params).json()
            for task in column_tasks:
                if task['name'] == name:
                    requests.request("DELETE", base_url.format('cards') + '/' + task['id'], params=auth_params)
                    print('\n' + task['name'] + ' was deleted\n')
                    read()
                    break
                else:
                    print('Task "{}" was not found'.format(name))


def addTable(column_name):
    column_check = 0
    for column in column_data:
        if column['name'] == column_name:
            column_check += 1
    if column_check > 0:
        print('Column {} is already exist on table'.format(column_name))
    else:
        response = requests.post(base_url.format('lists'), params={
            'name': column_name,
            'idBoard': long_id,
            **auth_params
        })
        print('Column {} successfully created'.format(column_name))
        print(response.text)
        read()


def checkArguments():
    try:
        if (sys.argv[2] or sys.argv[3]) is not None:
            print('Wait please...')
            time.sleep(0.4)
        else:
            print('Error! Unknown command. Try to use another arguments!')
            exit(1)
    except IndexError:
        print('Error! Arguments not found!')
        exit(-1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        read()
    else:
        checkArguments()
        if sys.argv[1] == 'create':
            create(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'move':
            move(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'delete':
            delete(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'addTable':
            addTable(sys.argv[2])
        else:
            print("Unknown command: {}".format(sys.argv[1]))
