System integration assignment Messagel oriented middleware

Assignment 2 banking operation

step 1: Make virtual environment -> virtualenv venv -> source venv/bin/activate

step 2: Install python client for consumer and producer -> pip3 install -r requirements.txt

step 3: Install GeckoDriver -> https://github.com/mozilla/geckodriver/releases -> remoteGeckoPath variable should be folder where you have the driver

step 4: launch producer and consumer -> ./run_consumer.sh ./run_producer.sh

note: both producer and consumer can initiate the channel que with queue_declare(queue='').
modify the json.loan. Options for loantypes: Car Loan, All Loans, Personal Loan, Guarantor Loan, peer to peer loan
options for secured loan: 1, 0
currency can actually only be british sterling on example from assignment 2


