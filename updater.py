import tkinter
import json


def news_process():
    
    with open('current.json', 'w') as current:
        current_project = json.load(current)
    news = input("What's the news?")

    for item in current_project:
        print(current_project.index(item) + ' ' + item)
    selection = input('Select one of the project or type "c" to creat a new one')

    if selection is 'c':
        project_name = input('Please input new project name:\n >')
        change_plan(project_name)
        log_wirter(project_name)
    else:
        project_name = current_project.index(selection)
        log_wirter(project_name)
        peek_plan(project_name)

    return

def change_plan(project_name):
    plan_file = project_name + '.pln'
    with open(plan_file, 'a') as plan:
        


    # info = input('Anything new?')   # 从用户输入获取当前新闻
    # if selection is 'c':
    #     project_name = input('please input new project name: \n>')
    #     change_plan(new_project_name)
    # else:
    #     project_name = current_issue_list[selection]
    #     log_wirter(project_name, info)


# def show_current_project():
#     pass

# def change_plan():
#   write_main_log()  
#   pass

# def archive():
#     pass

# def log_wirter():
#     pass
while True:
    mode = input('Press Enter to input news, or "p" for peeking\n >')
    if not mode:
        news_process()
    elif mode is 'p':
        peek_process()