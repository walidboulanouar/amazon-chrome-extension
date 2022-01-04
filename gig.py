from selenium import webdriver
from selenium.webdriver import Chrome
from openpyxl import Workbook, load_workbook
import requests, html2text, re, urllib.parse

op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = Chrome(options=op)

def solve_recaptcha_if_existing(driver,domain):
	if "sorry" in driver.current_url and driver.current_url.find('?') != -1:
		print(f'Captcha in {driver.current_url}')
		print(f'Try to solve with 2Captcha.com')

		recaptcha = driver.find_element_by_id('recaptcha')
		googlekey = recaptcha.get_attribute('data-sitekey')
		data_s = recaptcha.get_attribute('data-s')
		pageurl = driver.current_url

		while True:
			res = captcha_solver.solve('07f68a4f5ea655428271e560adf87489', googlekey, pageurl, data_s)

			if res == 'ERROR_CAPTCHA_UNSOLVABLE' or res == 'ERROR':
				driver.get(driver.current_url)
				time.sleep(1)
			elif res == 'ERROR_ZERO_BALANCE':
				print('\n\n')
				print("!!!   ERROR   !!!")
				print('You don\'t have enough balance to solve the captcha!')
				choose = int(input('Top up your balance and enter 1 or everything else for close script: '))
				if choose == 1:
					driver.get(driver.current_url)
					time.sleep(3)
					continue
				else:
					driver.close()
					exit()
			else:
				g_recaptcha_response = driver.find_element_by_id('g-recaptcha-response')
				driver.execute_script("arguments[0].style.display = 'block';", g_recaptcha_response)
				#print('done1')
				time.sleep(1)

				driver.execute_script(f'arguments[0].innerHTML="{res}";', g_recaptcha_response)
				#print('done2')
				time.sleep(1)

				driver.find_element_by_id('captcha-form').submit()
				#print('done3')
				time.sleep(1)
				return
	elif "sorry" in driver.current_url and driver.current_url.find('?') == -1:
	   driver.get(domain)
	   return
	else:
		return

def product_link_image(text, page=1):
	driver.get(f'https://www.amazon.com/s?k={"+".join(list(map(urllib.parse.quote, text.split())))}&page={page}')
	solve_recaptcha_if_existing(driver, urllib.parse.quote(f'https://www.amazon.com/s?k={"+".join(list(map(urllib.parse.quote, text.split())))}&page={page}'))

	body = driver.find_element_by_tag_name('body').text
	if 'Showing results for' in body:
		match = re.findall(r'Showing results for (.+)', body)[0]
		return product_link_image(match)

	products = driver.find_elements_by_class_name('s-result-item')

	links, images = [], []
	stop = False
	for product in products:
		if 'Sponsored' not in product.text:
			imgs = product.find_elements_by_class_name('s-image')
			for link in product.find_elements_by_tag_name('a'):
				href = link.get_attribute('href')
				if href!=None and len(imgs)==1:
					if f'keywords={"+".join(list(map(urllib.parse.quote, text.split())))}' in href:
						links.append(href)
						images.append(imgs[0].get_attribute('src'))
						return links[0], images[0]

def product_image(text):
	return product_link_image(text)[1]


w = Workbook()
ws = w.active
ws.append(['Name', 'Info', 'Image URL'])

with open('keywords.txt') as f:
	content = f.read()
	if content[-1] == '\n': content = content[:-1]
	content = content.split('\n')
	total = len(content)

	for i, line in enumerate(content):
		print(f'--- --- Current keyword checking [{"-".join(line.split())}]: {i+1} of {total}')
		ws.append([line.title(), f'[amazon bestseller="{line}" items="10"]',product_image(line)])

w.save('results.xlsx')
driver.quit()
