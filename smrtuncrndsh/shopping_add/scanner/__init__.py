import os
import re
import dateutil
from difflib import get_close_matches
from fuzzywuzzy import process, utils

from pdftotext import PDF
from sqlalchemy import func
from flask import flash, request, redirect, render_template, current_app, \
    render_template_string, Markup, safe_join, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from smrtuncrndsh import get_base_dir
from .. import shopping_add_bp
from ..forms import PdfForm, ReceiptForm
from ...models.Shopping import Item, Shop, Category, Liste
from ...models.Users import User

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
# capitalisation is not considered for markets
MARKETS = {
    'Penny': ['penny', 'p e n n y'],
    'REWE': ['rewe', 'r e w e'],
    'Real': ['real', 'r e a l'],
    'Netto': ['netto-online', 'netto', 'n e t t o'],
    'Aldi': ['aldi', 'a l d i'],
    'Lidl': ['lidl'],
    'Edeka': ['edeka'],
    'Amazon': ['amazon', 'a m a z o n']
}
BASE_DIR = get_base_dir()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clear_user_uploads():
    upload_dir = safe_join(current_app.config['UPLOAD_FOLDER_PATH'], str(current_user.get_id()))
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, file)
            if os.path.isdir(file_path):
                continue
            current_app.logger.debug(f"Removing file '{file_path}' from uploads folder!")
            os.remove(file_path)


def save_file(file):
    # save pdf file
    filename = ''
    if not file.filename:
        flash("No file selected!", 'error')
        return None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_basepath = safe_join(
            current_app.config['UPLOAD_FOLDER_PATH'],
            str(current_user.get_id())
        )
        if not os.path.exists(file_basepath):
            os.mkdir(file_basepath)
        file_path = safe_join(
            file_basepath,
            filename
        )
        current_app.logger.debug(f"Saving file '{file_path}'.")
        file.save(file_path)
    else:
        file_path = None
    return file_path, filename


@shopping_add_bp.route("/scan", methods=['GET', 'POST'])
def scan_reciept():
    # @after_this_request
    # def remove_upload(request):
    #     clear_upload()
    #     return request

    pdf_form = PdfForm(prefix="pdf-form")

    if current_user.is_admin:
        current_app.logger.info("User is admin! Letting admin decide who is the owner of the added Receipt.")

        class AdminReceiptForm(ReceiptForm):
            pass

        AdminReceiptForm.user = QuerySelectField(
            query_factory=lambda: User.query,
            get_label='username',
            allow_blank=False,
            blank_text="Select a user",
            description="User",
        )
        receipt_form = AdminReceiptForm(prefix="receipt-form")
        # form.user = current_user
    else:
        receipt_form = ReceiptForm(prefix="receipt-form")

    if request.method == 'POST':
        if pdf_form.reciept.data and pdf_form.validate_on_submit():
            file = pdf_form.reciept.data

            if file.mimetype == "application/pdf":
                file_path, filename = save_file(file)
                if not file_path:
                    return redirect(request.url)

                try:
                    with open(file_path, 'rb') as pdf_file:
                        pdf = PDF(pdf_file)
                except Exception:
                    current_app.logger.exception(
                        "Can not read file! Please make sure that the uploaded file is a valid pdf file!"
                    )
                    flash("Can not read file! Please make sure that the uploaded file is a valid pdf file!", 'error')
                    clear_user_uploads()
                    return redirect(request.url)

                lines = [line.lstrip().lower() for line in pdf[0].split('\n')]
                del pdf

                dates, sums, shop_objs, items = get_receipt_data_from_pdf(lines)
                receipt_form = populate_receipt_form(receipt_form, dates, sums, shop_objs, items)
                return render_template(
                    'show_pdf.html',
                    title='Scan Shopping List',
                    template='shopping-scan',
                    form=receipt_form,
                    pdf_filename=filename,
                )
            flash("Filetype must be pdf!", 'error')
            return redirect(request.url)

        elif receipt_form.user.data and receipt_form.validate_on_submit():
            clear_user_uploads()

            date = receipt_form.date.data
            dates = receipt_form.dates.data
            summ = receipt_form.sums.data
            price = float(receipt_form.price.data)
            category = receipt_form.category.data if receipt_form.category.data is not None else ''

            shops = receipt_form.shops.data
            items = receipt_form.items.data
            # filter out removed or invalid
            items = [
                item for item in items if item['item'] and item['amount'] and item['price']
            ]
            if hasattr(receipt_form, "user") and receipt_form.user.data and current_user.is_admin:
                user = receipt_form.user.data
            else:
                user = current_user

            ret_val, list_id = save_receipt(date, dates, summ, price, shops, items, category, user)
            if ret_val and list_id >= 0:
                link = render_template_string(
                    f"<a href=\"{{{{ url_for('shopping_view_bp.shopping_view_list', "
                    f"id={list_id}) }}}}\">here</a>"
                )
                flash(Markup(f"Receipt added successfully! See it's details {link}."), 'success')
            else:
                flash("Something failed saving the receipt. Try again!", 'error')
            return redirect(url_for('shopping_add_bp.add'))
        else:
            current_app.logger.debug("No form submitted or both weren't verified!")
            # flash("No form submitted!", 'error')
            if receipt_form.errors:
                current_app.logger.debug(f"Errors: {receipt_form.errors}")
            return redirect(url_for('.add'))
    return render_template(
        'load_pdf.html',
        title='Scan Shopping List',
        template='shopping-add',
        form=pdf_form,
    )


def populate_receipt_form(receipt_form, dates, sums, shop_objs, items):
    if len(dates) == 1:
        receipt_form.date.data = dates[0]
    receipt_form.dates.choices = [
        (str(date.strftime("%d.%m.%Y")), date.strftime("%d.%m.%Y")) for date in dates
    ]
    if len(sums) == 1:
        receipt_form.price.data = sums[0]
    else:
        receipt_form.sums.choices = [(float(sum), sum) for sum in sums]

    if shop_objs:
        receipt_form.shops.pop_entry()
    for shop in shop_objs:
        receipt_form.shops.append_entry({'shop': shop.name, 'category': shop.category.name})

    if items:
        receipt_form.items.pop_entry()
        items.append({
            'item': '',
            'price': 0,
            'amount': 0,
            'volume': '',
            'ppv': '',
        })
    for item in items:
        receipt_form.items.append_entry(item)
    return receipt_form


def get_dates(lines):
    """ Matches dates like 19.08.15 and 19. 08. 2015 WITH WHITESPACE AFTER DATE

        return:
            list of unique date objects
            empty list if no dates found
    """
    dates_found = []
    date_format = r'(?P<date>(\d{2,4}((\.|\/|-)\s?|[^a-zA-Z\d])\d{2}((\.|\/|-)\s?|[^a-zA-Z\d])(19|20)?\d\d)\s+)'
    for line in lines:
        m = re.search(date_format, line)
        if m:
            date_str = m.group(1)
            date_str = date_str.replace(" ", "")
            try:
                dates_found.append(dateutil.parser.parse(date_str, dayfirst=True))
            except dateutil.parser.ParserError:
                pass
    return list(set(dates_found))


def get_shop(lines):
    finds = []
    for market, spellings in MARKETS.items():
        for line in lines:
            if not utils.full_process(line):
                continue
            highest = process.extractOne(line, spellings)
            if highest[1] >= 90:
                finds.append(market)
    return list(set([market.lower() for market in finds]))


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
    found_sums = []

    for sum_key in sum_keys:
        sum_line = fuzzy_find(lines, sum_key)
        if sum_line:
            # Replace all commas with a dot to make
            # finding and parsing the sum easier
            sum_line = sum_line.replace(",", ".")
            # Parse the sum
            sum_float = re.search(sum_format, sum_line)
            if sum_float:
                try:
                    found_sums.append(float(sum_float.group(0)))
                except ValueError:
                    pass
    return list(set(found_sums))


def get_item(line, next_line):
    # items regex's
    item_format = r'(?:\d{3,})?(?P<item>[\w. !-]+)[ ]{4,}(?P<price>[\d,]+) [ba]'
    amount_format = r'(?P<amount>\d{1,3}) stk x[ ]+(?P<amount_price>\d{1,5},?\d*)'
    volume_format = r'(?P<volume>\d{0,3}(,|.)?\d{1,4} (kg|g|mg|l|ml)) x\s+(?P<ppv>\d{1,3},\d{2} eur\/(kg|g|mg|l|ml))'

    item_match = re.match(item_format, line)
    if item_match:
        item = item_match.group('item').strip()
        amount = 1
        price = float(item_match.group('price').replace(',', '.'))
        volume = ppv = ''

        if next_line:
            amount_match = re.match(amount_format, next_line)
            volume_match = re.match(volume_format, next_line)

            if amount_match:
                amount = int(amount_match.group('amount'))
                price = price / amount
            elif volume_match:
                volume = volume_match.group('volume').replace(' ', '')
                ppv = volume_match.group('ppv').replace('eur', '€')
        return {
            'item': item.title(),
            'price': price,
            'amount': amount,
            'volume': volume.replace(" ", '').replace('$', '').replace('€', '').replace(',', '.'),
            'ppv': ppv.replace(" ", '').replace('$', '').replace('€', '').replace(',', '.'),
        }
    return {}


def handle_duplicate_items(items):
    seen = set()
    new_items = []
    for item_dict in items:
        item_tuple = tuple(item_dict.items())
        if item_tuple not in seen:
            seen.add(item_tuple)
            new_items.append(item_dict)
        else:
            # increase amount of existing item by one
            for item in new_items:
                if item == item_dict:
                    item['amount'] += 1
    return new_items


def get_receipt_data_from_pdf(lines):
    dates = get_dates(lines)
    sums = get_sum(lines)

    shops = get_shop(lines)
    shop_objs = []
    for shop in shops:
        shop_objs += Shop.query.filter(func.lower(Shop.name) == shop.lower()).all()

    items = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            item = get_item(line, lines[i + 1])
            if item:
                items.append(item)
    items = handle_duplicate_items(items)

    return dates, sums, shop_objs, items


def get_receipt_category(category):
    category_obj = Category.get_category(category)
    if category and not category_obj:
        category_obj = Category(name=category)
        category_obj.save_to_db()
        current_app.logger.debug(f"Created new category '{category_obj}'")
    return category_obj


def get_receipt_shop(shops):
    shops = Shop.get_shop(shops[0]['shop'], category_name=shops[0]['category'])
    if shops:
        shop = shops[0]
        if len(shops) > 1:
            flash(f"Multiple shops found. Using '{shop.name}'.")
    else:
        category = Category.get_category(shops[0]['category'])
        if not category:
            category = Category(shops[0]['category'])
            category.save_to_db()
            current_app.logger.debug(f"Created new shop's category '{category}'")

        shop = Shop(shops[0]['shop'], category=category)
        shop.save_to_db()
        current_app.logger.debug(f"Created new shop '{shop}'")
    return shop


def get_receipt_items(items):
    items_list = []
    for item in items:
        volume = "" if not item['volume'] else item['volume']
        ppv = "" if not item['ppv'] else item['ppv']
        item_objs = Item.get_item(
            name=item['item'],
            price=item['price'],
            volume=volume,
            price_per_volume=ppv,
        )
        if len(item_objs) >= 1:
            item_obj = item_objs[0]
        else:
            item_obj = Item(
                name=item['item'],
                price=item['price'],
                volume=volume,
                price_per_volume=ppv,
                sale=item['sale'],
            )
            item_obj.save_to_db()
            current_app.logger.debug(f"Created new item '{item_obj}'")

        for _ in range(item['amount']):
            items_list.append(item_obj)
    return items_list


def save_receipt(date, dates, summ, price, shops, items, category, user):
    ret_val, list_id = True, -1

    if summ and not price:
        price = summ
    elif not price and not summ:
        ret_val = False
        flash("Please enter a price for the receipt!", 'error')
    else:
        ret_val = False
        flash("Please choose either a RadioButton price option OR enter the price in the input field!", 'error')

    if dates and not date:
        date = dates
    elif not dates and not date:
        ret_val = False
        flash("Please enter a date for the receipt!", 'error')
    else:
        ret_val = False
        flash("Please choose either a RadioButton date option OR enter the date in the input field!", 'error')

    if len(shops) > 1:
        ret_val = False
        flash("Please leave only ONE shop, remove all other!")

    if ret_val:
        category_obj = get_receipt_category(category)
        shop = get_receipt_shop(shops)
        items = get_receipt_items(items)

        liste = Liste(date=date, price=price, shop=shop, category=category_obj)
        liste.user = user
        for item in items:
            liste.items.append(item)

        liste.save_to_db()
        current_app.logger.debug(f"Created new liste '{liste}'")
        list_id = liste.id

    return ret_val, list_id
