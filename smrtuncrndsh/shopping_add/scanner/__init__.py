import re
import dateutil
from datetime import datetime
from difflib import get_close_matches
from fuzzywuzzy import process, utils

from sqlalchemy import func
from flask import flash, request, redirect, url_for, render_template, jsonify
# from werkzeug.utils import secure_filename
# from flask_uploads import UploadSet, IMAGES, PDFS

from pdftotext import PDF

from ...models.Shopping import Item, Shop, Category
from .. import shopping_add_bp
from ..forms import PdfForm, ReceiptForm

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@shopping_add_bp.route("/scan", methods=['GET', 'POST'])
def scan_reciept():
    result = {'status': 'success', 'text': ""}
    pdf_form = PdfForm()

    if request.method == 'POST':
        if pdf_form.validate_on_submit():
            f = pdf_form.reciept.data

            if f.content_type == "application/pdf":
                pdf = PDF(f)
                lines = [line.strip().lower() for line in pdf[0].split('\n')]

                shop_objs = shop = get_shop(lines)
                if shop:
                    shop_objs = Shop.query.filter(func.lower(Shop.name) == shop.lower()).all()
                print("Shop: ", shop, " Shop obj: ", shop_objs)

                date = get_date(lines)
                print("Date: ", date)
                sum = get_sum(lines)
                print("Sum:  ", sum)

                items = []
                for i, line in enumerate(lines):
                    if i < len(lines) - 1:
                        item = get_item(line, lines[i + 1])
                        if item:
                            items.append(item)
                            print(item)
                
                receipt_form = ReceiptForm()
                receipt_form.date.data = date
                receipt_form.price.data = sum
                receipt_form.shop.data = 

            # result['status'] = 'error'
            return jsonify(result)
    return render_template(
        'scanner.html',
        title='Scan Shopping List',
        template='shopping-scan',
        pdf_form=pdf_form,
    )


def get_date(lines):
    # Matches dates like 19.08.15 and 19. 08. 2015
    date_format = r'(?P<date>(\d{2,4}(\.\s?|[^a-zA-Z\d])\d{2}(\.\s?|[^a-zA-Z\d])(19|20)?\d\d)\s+)'
    # parse date
    for line in lines:
        m = re.match(date_format, line)
        if m:
            date_str = m.group(1)
            date_str = date_str.replace(" ", "")
            dateutil.parser.parse(date_str)
            return datetime.strptime(date_str, "%d.%m.%Y")
    return None


def get_shop(lines):
    markets = {
        'Penny': ['penny', 'p e n n y'],
        'REWE': ['rewe', 'r e w e'],
        'Real': ['real', 'r e a l'],
        'Netto': ['netto-online'],
        'Aldi': ['aldi'],
        'Lidl': ['lidl'],
        'Edeka': ['edeka'],
    }
    for market, spellings in markets.items():
        for line in lines:
            if not utils.full_process(line):
                continue
            highest = process.extractOne(line, spellings)
            if highest[1] > 90:
                return market
    return ""


def fuzzy_find(lines, keyword):
    for line in lines:
        words = line.split()
        # Get the single best match in line
        matches = get_close_matches(keyword, words, 1)
        if matches:
            return line


def get_sum(lines):
    sum_keys = ['summe', 'gesamtbetrag', 'gesamt', 'total', 'sum', 'zwischensumme', 'bar', 'te betalen']
    sum_format = r'\d+(\.\s?|,\s?|[^a-zA-Z\d])\d{2}'

    for sum_key in sum_keys:
        sum_line = fuzzy_find(lines, sum_key)
        if sum_line:
            # Replace all commas with a dot to make
            # finding and parsing the sum easier
            sum_line = sum_line.replace(",", ".")
            # Parse the sum
            sum_float = re.search(sum_format, sum_line)
            if sum_float:
                return sum_float.group(0)
    return 0


def get_item(line, next_line):
    # items regex's
    item_format = r'(?P<item>[\w. ]+)[ ]{4,}(?P<price>[\d,]+) [ba]'
    amount_format = r'(?P<amount>\d{1,3}) stk x[ ]+(?P<amount_price>\d{1,5},?\d*)'
    volume_format = r'(?P<volume>\d{0,3},?\d{1,4} (kg|g|mg|l|ml)) x\s+(?P<ppv>\d{1,3},\d{2} eur\/(kg|g|mg|l|ml))'

    item_match = re.match(item_format, line)
    if item_match:
        item = item_match.group('item').strip()
        amount = 1
        price = amount_price = float(item_match.group('price').replace(',', '.'))
        volume = ppv = ''

        if next_line:
            amount_match = re.match(amount_format, next_line)
            volume_match = re.match(volume_format, next_line)

            if amount_match:
                amount = int(amount_match.group('amount'))
                amount_price = float(amount_match.group('amount_price').replace(',','.'))
            elif volume_match:
                volume = volume_match.group('volume').replace(' ', '')
                ppv = volume_match.group('ppv').replace('eur', '€')
        return {'name': item, 'price_per_piece': price, 'total_price': amount_price, 'amount': amount, 'volume': volume, 'ppv': ppv}
    return {}
