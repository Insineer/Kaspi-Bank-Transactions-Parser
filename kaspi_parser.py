#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
import datetime
import csv
import re
from typing import Generator, List
import pdfplumber
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s\t%(message)s")
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    date: datetime.date
    payee: str
    memo: str
    amount: float

    def __str__(self):
        return f"Transaction[{self.date.strftime('%Y.%m.%d')}, {self.amount}, \"{self.payee}\"]"

TRANSACTION_TABLE_HEADER_VARIANTS = [
    ["Date", "Amount", "Transaction", "Details"],
    ["Дата", "Сумма", "Операция", "Детали"],
    ["Күні", "Сомасы", "Операция", "Толығырақ"]
]
AMOUNT_PATTERN = r"^(?P<sign>[+-])\s*(?P<amount>[\d, ]+) (?P<currency>\S+)$"  # e.g. "+ 20,93 ₸"
EXPECTED_CURRENCY = "₸"

def parse_amount(amount_str: str) -> float:
    first_line = amount_str.split('\n')[0]
    match = re.match(AMOUNT_PATTERN, first_line)
    if not match:
        raise ValueError(f"Failed to parse amount: {amount_str}")
    if match.group("currency") != EXPECTED_CURRENCY:
        raise ValueError(f"Unexpected currency: {match.group('currency')}, expected: {EXPECTED_CURRENCY}")

    amount = float(match.group("amount").replace(",", ".").replace(" ", ""))
    return amount if match.group("sign") == "+" else -amount

def get_transactions(table) -> Generator[Transaction, None, None]:
    for line in table:
        try:
            date, amount, operation_type, details = line
            transaction = Transaction(
                date=datetime.datetime.strptime(date, "%d.%m.%y"),
                payee=details,
                memo="",
                amount=parse_amount(amount))
            logger.info(f"\t{transaction}")
            yield transaction
        except Exception as e:
            logger.error(f"Failed to parse transaction {line}, Reason: {e}")

def get_transaction_tables(pages):
    header_is_found = False
    for i, page in enumerate(pages):
        logger.info(f"Parsing page {i+1}...")
        for table in page.extract_tables():
            if header_is_found:
                yield table
            elif table[0] in TRANSACTION_TABLE_HEADER_VARIANTS:
                header_is_found = True
                yield table[1:]
    if not header_is_found:
        raise ValueError("Failed to find the transaction table header")

def parse_statement(pdf_file) -> List[Transaction]:
    transactions = []

    try:
        total_change = 0
        total_inflow = 0
        total_outflow = 0
        with pdfplumber.open(pdf_file) as pdf:
            logger.info(f"Parsing Kaspi statement (Number of pages: {len(pdf.pages)})...")
            for transaction_table in get_transaction_tables(pdf.pages):
                for transaction in get_transactions(transaction_table):
                    transactions.append(transaction)
                    total_change += transaction.amount
                    if transaction.amount > 0:
                        total_inflow += transaction.amount
                    else:
                        total_outflow += transaction.amount
        logger.info(f"Total transactions: {len(transactions)}")
        logger.info(f"Total change: {total_change:.2f}")
        logger.info(f"Total inflow: {total_inflow:.2f}")
        logger.info(f"Total outflow: {total_outflow:.2f}")
    except Exception as e:
        logger.error(f"Parsing error: {e}")
    
    return transactions

def export_to_csv(transactions: List[Transaction], output_csv):
    try:
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Date", "Payee", "Memo", "Amount"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

            writer.writeheader()
            for transaction in transactions:
                writer.writerow({
                    "Date": transaction.date.strftime("%Y-%m-%d"),
                    "Payee": transaction.payee,
                    "Memo": transaction.memo,
                    "Amount": round(transaction.amount)
                })
        logger.info(f"Transactions exported to \"{output_csv}\"")
    except Exception as e:
        print(f"Exporting to CSV error: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parse Kaspi statement PDF and export transactions to CSV."
    )
    parser.add_argument("statement", help="Input PDF file path")
    parser.add_argument("--output", help="Output CSV file path (default: input file's name with a .csv extension)", default=None)
    return parser.parse_args()

def main():
    args = parse_arguments()

    input_pdf = args.statement
    output_csv = args.output or input_pdf.rsplit(".", 1)[0] + ".csv"

    transactions = parse_statement(input_pdf)
    export_to_csv(transactions, output_csv)

if __name__ == "__main__":
    main()
