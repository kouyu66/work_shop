# Biz Process Helper
# 开机启动,用于提醒应处理的报销事务
# 应答式助手

version = '0.0.1'
author = 'xinyu.kou@samsung.com'

'''
display_module() 用于显示当前事务, 包括项目以及to do
check_uncheck_module() 标记/取消标记完成项
re_calculat() 标记完成后重新排列事项
input_module() 从用户处收集信息,存入主字典
	根据用户输入时间生成索引键, 键值为属性字典{titile:'xxx', 'start_year':2019, 'start_month':'1'等等}
'''

import time
import json
import calendar

issue_file = 'expense_issue.txt'
finance_guy = 'jane.wang'
approval_line = 'TH(approve) - MS(approve) - Pu Tian(approve) - Honglae Cho(consent) - Jane Wang(noti)'
main_dict = {}	# 用于存储用户数据的主字典, {'填写日期浮点数':{'title':'', 'start_year':'',...}}

def input_module():
	'''交互界面, 将用户报销信息保存到主字典
		输入main_dict{} 输出main_dict{}
	'''
	
	continue_input = 'y'
	
	while continue_input == 'y':
		staff_key = str(time.time())
		trace = {}
		level_one_info = input("请输入待追踪报销事项基本信息, 格式为 发生日期 类型 标题 如 '0129 biz NewCommerTraining'\n> ")
		if not level_one_info:
			return
		
		staff_date,type,title = level_one_info.split(' ')
		# --构建主字典键名--
		month = int(''.join(list(staff_date)[:2]))
		day = int(''.join(list(staff_date)[2:]))
		taxi_out_of_range = ''
		ticket_change = ''
		credit_card_paid = ''
		done = ''
		wait = ''
		approval = []
		actions = {
		'file_prep' : '',
		'expense_save' : '',
		'expense_submit' : '',
		'approval_submit' : '',
		'approval_done' : '',
		'print_paste' : '',
		'sf_label' : '',
		'send_mail': ''
		}
		# ------------------
		if 'biz' in type:
			taxi_out_of_range = input('是否有出租车票据超过150/次? <y/n>\n> ')
			ticket_change = input('是否有出差日程变更导致的车票/机票改签? <y/n>\n> ')
			# if ticket_change is 'y':
				# credit_card_paid = input('用公司信用卡支付的这笔交易吗? <y/n>\n> ')
		elif 'pub' in type:
			taxi_out_of_range = input('是否有出租车单程票据超过150? <y/n>\n> ')
		elif 'sep' in type:
			credit_card_paid = input('用公司信用卡支付的这笔交易吗? <y/n>\n> ')
		save_input = input('确认如下信息,按y保存\nTitle: {0}\nType: {1}\nMonth: {2}\nDay: {3}\nTaxiOutOfRange: {4}\nTicketChange: {5}\nCreditCardPaid: {6}\n>'.format(title,type,month,day,taxi_out_of_range,ticket_change,credit_card_paid))
		if save_input == 'y':
			trace['title'] = title
			trace['type'] = type
			trace['month'] = month
			trace['day'] = day
			trace['taxi_out_of_range'] = taxi_out_of_range
			trace['ticket_change'] = ticket_change
			trace['credit_card_paid'] = credit_card_paid
			trace['done'] = done
			trace['wait'] = wait
			trace['approval'] = approval
			trace['actions'] = actions
			trace = general_process(trace)	# 对trace进行基本逻辑处理
			main_dict[staff_key] = trace
		continue_input = input('继续新增一项报销? <y/n>\n> ')
	return


def general_process(trace):
	'''处理禀议'''

	approval = trace['approval']
	# cross_month_approval:
	month = trace['month']
	# day = trace['day']
	current_year = int(time.strftime('%Y',time.localtime()))
	current_month = int(time.strftime('%m',time.localtime()))
	current_day = int(time.strftime('%d',time.localtime()))
	# current_hour = int(time.strftime('%H',time.localtime()))
	month_cap = calendar.monthrange(current_year, current_month)
	threshold = 3	# 月末可能由于材料邮寄不及时导致的报销退回的危险时间段
	
	if month == current_month and current_day <= (month_cap - threshold):
		pass
	else:
		approval.append('cross_month_approval')
	# out_of_range_approval:
	if trace['taxi_out_of_range'] is 'y':
		approval.append('taxi_out_of_range_approval')
	# ticket_change_approval:
	if trace['ticket_change'] is 'y':
		approval.append('ticket_change_approval')
	# cash_expsens_approval:
	if trace['credit_card_paid'] is not 'y':
		approval.append('cash_expense_approval')
	# attendance_approval:
	if trace['type'] is 'pub':
		approval.append('attendance_approval')
	trace.update({'approval' : approval})
	
	return trace


def file_prep(trace):
	
	
	basic_file = {
	'biz' : ['出租车小票', '登机牌/火车票', '酒店专票', '酒店流水单', '酒店刷卡单'],
	'sep' : ['刷卡单', '发票'],
	'pub' : ['出租车小票', '火车票']
	}
	credit_card_paid = trace['credit_card_paid']
	# welcome = '请将如下材料粘贴在A4纸上并扫描到EDM备用:\n{0}'format(file_name)
	type = trace['type']
	selected_file = basic_file[type]
	
	if 'sep' in type:
		if credit_card_paid is not 'y':
			barcode = '张贴barcode并扫描到现金报销系统'
			selected_file.append(barcode)

	print('请将如下材料粘贴在A4纸上并扫描到EDM备用:\n{0}'.format('\n'.join*(selected_file)))
	
	return

def approval_prep(trace):
	
	approvals_cn = []
	approvals = trace['approval']
	if not approvals:
		return
	if 'cross_month_approval' in approvals:
		approvals_cn.append('跨月禀议')
	if 'taxi_out_of_range_approval' in approvals:
		approvals_cn.append('出租车超程禀议')
	if 'ticket_change_approval' in approvals:
		approvals_cn.append('改签禀议')
	if 'cash_expense_approval' in approvals:
		approvals_cn.append('现金报销禀议')
	if 'attendance_approval' in approvals:
		approvals_cn.append('考勤申请')
	print('请编写如下禀议/申请并等待审批，审批路径为：{0}\n{1}'.format(approval_line, approvals_cn))
	
	return

def expense_save(trace):
	
	expense_path = {
	'biz' : 'G-ERP => Business Travel => Expense Request',
	'cash' : 'G-ERP => MyFinance => Cash',
	'card' : 'G-ERP => MyFinance => Credit Card'
	}
	expense_type = trace['type']
	if 'biz' in expense_type:
		general_message = '请在如下路径编写出差报销申请，并录入相关票据\n{0}'.format(expense_path['biz'])
	elif 'pub' in expense_type:
		general_message = '请在如下路径下编写公出报销申请，并录入相关票据\n{0}'.format(expense_path['cash'])
	else:
		if 'y' in trace['credit_card_paid']:
			general_message = '请在如下路径下编写特殊事项报销申请，并录入相关票据\n{0}'.format(expense_path['card'])
		else:
			general_message = '请在如下路径下编写特殊事项报销申请，并录入相关票据\n{0}'.format(expense_path['cash'])

	return general_message

def expense_submit(trace):
	general_message = '提交已保存的报销申请，并打印封面，等待至少一位老板审批'
	return general_message

def mail_prep():
	general_message = '请将所有报销材料粘贴左上角，SF LABEL 打印顺丰快递单，singleID初始账号密码\n联系快递小哥准备邮寄'
	return general_message

def wait_for_cash():
	general_process = '等待报销审批完批'
	return general_process

def multi_task_cordinate():
	'''将除最新的trace以外的trace标记为等待状态'''	
	if len(main_dict) <= 1:
		return
	key_list = []
	for trace_number, trace in main_dict.keys():
		if trace['done']:
			continue
		key_list.append(int(trace_number))
	key_list.sort()
	staff_number = key_list[:]
	active_trace_number = str(key_list.pop(0))
	active_trace = main_dict[active_trace_number]
	active_trace.update({'wait' : ''})
	main_dict.update({active_trace_number : active_trace})
	for idle_trace_number in key_list:
		idle_trace = main_dict[idle_trace_number]
		idle_trace.update({'wait' : 'y'})
		main_dict.update({idle_trace_number : idle_trace})

	return staff_number

def middle_gule():
	# 忽略已完成的trace
	# 处理最新的trace
	# 根据trace的indicator来生成接下来的行动
	staff_num = multi_task_cordinate()
	if not staff_num:
		start_input = input('暂无需要处理的报销，需要新建报销事项吗？<y/n>\n> ')
		if start_input is 'y':
			input_module()
		else:
			exit()
	else:
		pass

	return
