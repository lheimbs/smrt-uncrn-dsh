from flask import flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

# from flask_uploads import UploadSet, IMAGES, PDFS
from wtforms import TextField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from pdftotext import PDF

from .. import shopping_add_bp

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


class RecieptForm(FlaskForm):
    reciept = FileField(validators=[FileRequired()])
    shop = TextField("Shop", validators=[DataRequired()])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@shopping_add_bp.route("/scan", methods=['GET', 'POST'])
def scan_reciept():
    form = RecieptForm()
    if form.validate_on_submit():
        f = form.reciept.data

        if f.content_type == "application/pdf":
            pdf = PDF(f)
            print(pdf[0])

        print(f, f.content_type)
        # print(f.read())



        # # check if the post request has the file part
        # if 'file' not in request.files:
        #     flash('error', 'No file part')
        #     return redirect(request.url)
        # file = request.files['file']
        # # if user does not select file, browser also submit an empty part without filename
        # if file.filename == '':
        #     flash('error', 'No selected file')
        #     return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     print(file.read())
        #     return "test"
    return render_template(
        'scanner.html',
        title='Scan Shopping List',
        template='shopping-scan',
        form=form,
    )
