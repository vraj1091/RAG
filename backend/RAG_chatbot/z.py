"""
Tally XML Generator - Creates 5000+ entries for Demo_500 company
Run this script to generate: demo_500_tally_import.xml
"""

import random
from datetime import datetime, timedelta

# Configuration
COMPANY_NAME = "Demo_500"
START_DATE = datetime(2024, 4, 1)  # Financial Year 2024-25
END_DATE = datetime(2025, 3, 31)

# Sample data
CUSTOMERS = [f"Customer_{i:03d}" for i in range(1, 101)]
SUPPLIERS = [f"Supplier_{i:03d}" for i in range(1, 101)]
PRODUCTS = [f"Product_{i:03d}" for i in range(1, 101)]
EXPENSE_HEADS = ["Rent", "Electricity", "Salaries", "Marketing", "Travel", "Office Supplies", 
                 "Insurance", "Repairs", "Telephone", "Internet", "Legal Fees", "Bank Charges"]

def generate_xml():
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<ENVELOPE>')
    xml.append('<HEADER>')
    xml.append('<TALLYREQUEST>Import Data</TALLYREQUEST>')
    xml.append('</HEADER>')
    xml.append('<BODY>')
    xml.append('<IMPORTDATA>')
    xml.append('<REQUESTDESC>')
    xml.append('<REPORTNAME>All Masters</REPORTNAME>')
    xml.append('<STATICVARIABLES>')
    xml.append(f'<SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>')
    xml.append('</STATICVARIABLES>')
    xml.append('</REQUESTDESC>')
    xml.append('<REQUESTDATA>')
    
    print("🔨 Generating 200 Ledgers...")
    # Generate Ledgers (200)
    
    # Banks (10)
    banks = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Bank", 
             "PNB", "BOB", "Canara Bank", "Union Bank", "IDBI Bank"]
    for bank in banks:
        xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
        xml.append('<LEDGER NAME="' + bank + '" RESERVEDNAME="">')
        xml.append('<PARENT>Bank Accounts</PARENT>')
        xml.append(f'<OPENINGBALANCE>{random.randint(50000, 500000)}</OPENINGBALANCE>')
        xml.append('<ISBILLWISEON>No</ISBILLWISEON>')
        xml.append('</LEDGER>')
        xml.append('</TALLYMESSAGE>')
    
    # Customers (100)
    for customer in CUSTOMERS:
        xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
        xml.append(f'<LEDGER NAME="{customer}" RESERVEDNAME="">')
        xml.append('<PARENT>Sundry Debtors</PARENT>')
        xml.append(f'<OPENINGBALANCE>{random.randint(-100000, 50000)}</OPENINGBALANCE>')
        xml.append('<ISBILLWISEON>Yes</ISBILLWISEON>')
        xml.append('</LEDGER>')
        xml.append('</TALLYMESSAGE>')
    
    # Suppliers (100)
    for supplier in SUPPLIERS:
        xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
        xml.append(f'<LEDGER NAME="{supplier}" RESERVEDNAME="">')
        xml.append('<PARENT>Sundry Creditors</PARENT>')
        xml.append(f'<OPENINGBALANCE>-{random.randint(10000, 200000)}</OPENINGBALANCE>')
        xml.append('<ISBILLWISEON>Yes</ISBILLWISEON>')
        xml.append('</LEDGER>')
        xml.append('</TALLYMESSAGE>')
    
    # Expense Heads (20)
    for i, expense in enumerate(EXPENSE_HEADS, 1):
        xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
        xml.append(f'<LEDGER NAME="{expense}" RESERVEDNAME="">')
        xml.append('<PARENT>Indirect Expenses</PARENT>')
        xml.append('<OPENINGBALANCE>0</OPENINGBALANCE>')
        xml.append('</LEDGER>')
        xml.append('</TALLYMESSAGE>')
    
    print("📦 Generating 100 Stock Items...")
    # Stock Items (100)
    for product in PRODUCTS:
        xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
        xml.append(f'<STOCKITEM NAME="{product}" RESERVEDNAME="">')
        xml.append('<PARENT>Primary</PARENT>')
        xml.append('<BASEUNITS>Nos</BASEUNITS>')
        xml.append(f'<OPENINGBALANCE>{random.randint(10, 500)}</OPENINGBALANCE>')
        xml.append(f'<OPENINGRATE>{random.randint(100, 5000)}</OPENINGRATE>')
        xml.append('</STOCKITEM>')
        xml.append('</TALLYMESSAGE>')
    
    print("📝 Generating 5000+ Vouchers...")
    # Vouchers (5000+)
    voucher_count = 0
    current_date = START_DATE
    
    while current_date <= END_DATE:
        # Sales Vouchers (15 per day = ~5400/year)
        for i in range(15):
            voucher_count += 1
            customer = random.choice(CUSTOMERS)
            product = random.choice(PRODUCTS)
            qty = random.randint(1, 50)
            rate = random.randint(500, 5000)
            amount = qty * rate
            
            date_str = current_date.strftime('%Y%m%d')
            
            xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml.append(f'<VOUCHER VCHTYPE="Sales" ACTION="Create">')
            xml.append(f'<DATE>{date_str}</DATE>')
            xml.append(f'<VOUCHERNUMBER>S{voucher_count:05d}</VOUCHERNUMBER>')
            xml.append(f'<PARTYLEDGERNAME>{customer}</PARTYLEDGERNAME>')
            xml.append(f'<NARRATION>Sale of {product}</NARRATION>')
            xml.append('<ALLLEDGERENTRIES.LIST>')
            xml.append(f'<LEDGERNAME>{customer}</LEDGERNAME>')
            xml.append(f'<AMOUNT>{amount}</AMOUNT>')
            xml.append('</ALLLEDGERENTRIES.LIST>')
            xml.append('<ALLINVENTORYENTRIES.LIST>')
            xml.append(f'<STOCKITEMNAME>{product}</STOCKITEMNAME>')
            xml.append(f'<RATE>{rate}</RATE>')
            xml.append(f'<AMOUNT>-{amount}</AMOUNT>')
            xml.append('</ALLINVENTORYENTRIES.LIST>')
            xml.append('</VOUCHER>')
            xml.append('</TALLYMESSAGE>')
        
        # Purchase Vouchers (10 per day)
        for i in range(10):
            voucher_count += 1
            supplier = random.choice(SUPPLIERS)
            product = random.choice(PRODUCTS)
            qty = random.randint(10, 100)
            rate = random.randint(300, 3000)
            amount = qty * rate
            
            date_str = current_date.strftime('%Y%m%d')
            
            xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml.append(f'<VOUCHER VCHTYPE="Purchase" ACTION="Create">')
            xml.append(f'<DATE>{date_str}</DATE>')
            xml.append(f'<VOUCHERNUMBER>P{voucher_count:05d}</VOUCHERNUMBER>')
            xml.append(f'<PARTYLEDGERNAME>{supplier}</PARTYLEDGERNAME>')
            xml.append(f'<NARRATION>Purchase of {product}</NARRATION>')
            xml.append('<ALLLEDGERENTRIES.LIST>')
            xml.append(f'<LEDGERNAME>{supplier}</LEDGERNAME>')
            xml.append(f'<AMOUNT>-{amount}</AMOUNT>')
            xml.append('</ALLLEDGERENTRIES.LIST>')
            xml.append('<ALLINVENTORYENTRIES.LIST>')
            xml.append(f'<STOCKITEMNAME>{product}</STOCKITEMNAME>')
            xml.append(f'<RATE>{rate}</RATE>')
            xml.append(f'<AMOUNT>{amount}</AMOUNT>')
            xml.append('</ALLINVENTORYENTRIES.LIST>')
            xml.append('</VOUCHER>')
            xml.append('</TALLYMESSAGE>')
        
        # Payment Vouchers (5 per day)
        for i in range(5):
            voucher_count += 1
            expense = random.choice(EXPENSE_HEADS)
            bank = random.choice(banks)
            amount = random.randint(5000, 50000)
            
            date_str = current_date.strftime('%Y%m%d')
            
            xml.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml.append(f'<VOUCHER VCHTYPE="Payment" ACTION="Create">')
            xml.append(f'<DATE>{date_str}</DATE>')
            xml.append(f'<VOUCHERNUMBER>PMT{voucher_count:05d}</VOUCHERNUMBER>')
            xml.append(f'<NARRATION>Payment for {expense}</NARRATION>')
            xml.append('<ALLLEDGERENTRIES.LIST>')
            xml.append(f'<LEDGERNAME>{expense}</LEDGERNAME>')
            xml.append(f'<AMOUNT>{amount}</AMOUNT>')
            xml.append('</ALLLEDGERENTRIES.LIST>')
            xml.append('<ALLLEDGERENTRIES.LIST>')
            xml.append(f'<LEDGERNAME>{bank}</LEDGERNAME>')
            xml.append(f'<AMOUNT>-{amount}</AMOUNT>')
            xml.append('</ALLLEDGERENTRIES.LIST>')
            xml.append('</VOUCHER>')
            xml.append('</TALLYMESSAGE>')
        
        current_date += timedelta(days=1)
        
        if voucher_count % 1000 == 0:
            print(f"✅ Generated {voucher_count} vouchers...")
    
    xml.append('</REQUESTDATA>')
    xml.append('</IMPORTDATA>')
    xml.append('</BODY>')
    xml.append('</ENVELOPE>')
    
    print(f"\n🎉 Total vouchers generated: {voucher_count}")
    print(f"📊 Total entries: {200 + 100 + voucher_count}")
    
    return '\n'.join(xml)

# Generate and save
print("🚀 Starting Tally XML generation for Demo_500...\n")
xml_content = generate_xml()

filename = "demo_500_tally_import.xml"
with open(filename, 'w', encoding='utf-8') as f:
    f.write(xml_content)

print(f"\n✅ SUCCESS! File saved: {filename}")
print(f"📁 File size: {len(xml_content) / 1024 / 1024:.2f} MB")
print("\n📥 Import Instructions:")
print("1. Open TallyPrime")
print("2. Go to Gateway of Tally > Import > Vouchers")
print(f"3. Select file: {filename}")
print("4. Press Enter to import")
print("\n🎯 Your dashboard will show 5000+ transactions!")
