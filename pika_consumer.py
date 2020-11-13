import pika
from pprint import pprint
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import json 

driver = ''

def initiate_selenium():
    url = "https://money.gocompare.com/loans/#/"
    options = Options()
    options.headless = True
    remoteGeckoPath = "/usr/bin/geckodriver"
    print('init driver')
    global driver
    driver = webdriver.Firefox(executable_path=remoteGeckoPath,options=options)
    driver.get(url)
    time.sleep(2)

def callback(ch, method, props, body):
    print('entered callback')
    quotes_from_bank_loan_criterias = {}
    global driver
    body_str = body.decode()
    json_acceptable_string = body_str.replace("'", "\"")
    body_dict = json.loads(json_acceptable_string)
    loantype = body_dict['Loantype']
    interval_amount = body_dict['Borrow period years count']
    borrow_amount = body_dict['borrow ammount']
    #print('loantype: ', loantype, ' interval_amount: ', interval_amount)
    borrow_text_field = driver.find_element_by_xpath('//input[@class="text-input u-input--xsmall-small u-text-right ng-pristine ng-valid ng-valid-required"]')
    borrow_text_field.send_keys(Keys.CONTROL + "a")
    borrow_text_field.send_keys(Keys.DELETE)
    borrow_text_field.send_keys(borrow_amount)
    borrow_text_field.submit()
    driver.find_element_by_xpath('//div[@id="sticky-palm-top"]/div/div/div/div').click() #clicking slide down div
    driver.find_element_by_xpath(f"""//div[contains(text(), '{loantype}')]""").click()
    interval_text_field = driver.find_element_by_xpath('//div[@class="layout__item filter__fieldset u-hidden-palm"]/ul/li/input')
    interval_text_field.send_keys(Keys.CONTROL + "a")
    interval_text_field.send_keys(Keys.DELETE)
    interval_text_field.send_keys(interval_amount)
    interval_text_field.submit()
    time.sleep(0.75)
    results_found = driver.find_element_by_xpath('//div[@class="results-tile results-tile--left"]/span').text
    time.sleep(1.75)
    results_list = driver.find_elements_by_xpath('//ul[@class="results-list"]/li')
    scraped_offers = {}
    scraped_offers['results_found'] = results_found
    index = 0
    for element in results_list:
        print('index: ', index)
        print('element: ', element.text)
        str_element = element.text
        str_element = str_element.replace('\n', '')
        scraped_offers[str(index)] = str_element
        index+= 1
    
    print('sending: \n', scraped_offers)
    ch.basic_publish(exchange='', routing_key=props.reply_to, 
                        properties=pika.BasicProperties(correlation_id=props.correlation_id), body=f"""{scraped_offers}""")
    ch.basic_ack(delivery_tag = method.delivery_tag)


def main():
    initiate_selenium()
    with pika.BlockingConnection(pika.ConnectionParameters('localhost')) as connection:
        try: 
            channel = connection.channel()
            channel.queue_declare(queue='loan-request1', durable=True)
            channel.basic_qos(prefetch_count=1) #tells only one message per worker, instead assigns message to a free worker
            channel.basic_consume(queue='loan-request1', on_message_callback=callback)
            print('accepting incomming now')
            channel.start_consuming()
        finally:
            global driver
            driver.quit()

if __name__ == "__main__":
    main()
