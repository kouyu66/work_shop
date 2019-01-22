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
		'barcode_scan' : '',
		'expense_request' : '',
		'approvals' : '',
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
	day = trace['day']
	current_year = int(time.strftime('%Y',time.localtime()))
	current_month = int(time.strftime('%m',time.localtime()))
	current_day = int(time.strftime('%d',time.localtime()))
	current_hour = int(time.strftime('%H',time.localtime()))
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
	welcome = '请将如下材料粘贴在A4纸上并扫描到EDM备用:\n{0}'format(file_name)
	type = trace['type']
	selected_file = basic_file[type]
	
	elif 'sep' in type:
		if credit_card_paid is not 'y':
			barcode = '张贴barcode并扫描到现金报销系统'
			selected_file.append(barcode)
	
	return selected_file

def approval_prep(trace):
	
	approvals = trace['approval']
	
# def wait_prep(trace):
# def expense_prep(trace):
# def mail_prep(trace):
# def multi_task_cordinate():
# def 
	'''根据当前进度罗列下一步动作'''

		
# def biz_action(trace):
	# ''''''
	# biz_file = '出租车小票\n登机牌/火车票\n酒店专票\n酒店流水单\n酒店刷卡单'
	# expense_path = 'GERP - Business Travel - Expense Request'
	# action_indicator = trace['actions']	
	# approval = trace['approval']
	# next_one = ''
	# next_two = ''
	# standard_biz_action_list = [
	# '0将如下材料粘贴在A4纸上,标注时间,地点及金额, 并扫描至EDM备用.'.format(biz_file),
	# '1请编写跨月禀议,审批路径为{0}, 提交'.format(approval_line),
	# '2请编写出租车超规禀议, 审批路径为{0}, 提交.'.format(approval_line),
	# '3请编写机票/车票改签禀议, 审批路径为{0}, 提交.'.formant(approval_line),
	# '4编写报销申请, 路径为{0}, 并*保存*.'.format(expense_path),
	# '5等待所有禀议审批完成\n{0}'.format('\n'.join(approval)),
	# '6提交报销申请并等待完成.'
	# '7将所有材料(打印禀议)左上角粘贴',
	# '8打印顺丰标签.',
	# '9联系快递邮寄文件.'
	# ]
	
	# # 根据报销进度, 判断接下来两步需要做什么
	# if not action_indicator['file_prep']:
		# next_one = standard_biz_action_list[0]
		# next_two = ''
		# if not approval:
			# next_two = standard_biz_action_list[4]
		# else:
			# next_two = '\n'.join(approval)
	# elif not action_indicator['approvals']:
		# if not approval:
			# next_one = standard_biz_action_list[4]
			# next_two = standard_biz_action_list[6]
		# else:
			# next_one = 
# -----------------------------------------------
	# if not action_indicator['file_prep']:
		# hint_str = ''
		# biz_file = '出租车小票\n登机牌/火车票\n酒店专票\n酒店流水单\n酒店刷卡单'
		# pub_file = '出租车小票\n火车票\n'
		# sep_file = '原始单据\n发票\n刷卡单(转账记录)\nBarCode'
		# if 'biz' in trace['type']:
			# hint_str = biz_file
		# elif 'pub' in trace['type']:
			# hint_str = pub_file
		# elif 'sep' in trace['type']:
			# hint_str = sep_file
		# next_one = '请将如下材料粘贴在A4纸上并扫描到EDM备用\n{0}'.format(biz_file)
		# if not trace['approval']:
			# next_two = '请编写 {0} 报销申请并录入相关凭据'.formant(trace['title'])
		# else:
			# next_two = '请编写 {0} 如下禀议, 以原始凭据扫描件作为附件, 并提交:\n{1}'.formant(trace['title'], trace['approval'])

		
'''	# 根据当前日期, 提醒不同的事项
# ------ Danger Zone ------#

=(COUNTIF(D2:D901, ">"&0.9*G3)-COUNTIF(D2:D901, ">"&1.1*G3))/900




































	