# Smrt-Uncrn-Dsh

Smrt-Uncrn-Dsh is my personal homepage and a Project I use to educate myself on building a webpage using Python.

## Usage

Clone the repository, install required python packages and run the application:
```bash
git clone https://github.com/lheimbs/smrt-uncrn-dsh.git
cd smrt-uncrn-dsh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
./start.sh
```

## TODO
 - [ ] make page dsgvo compliant
 - [x] ngix or apache deployment w/ gunicorn?
 - [ ] security [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/), [OWASP Developer Guide](https://github.com/OWASP/DevGuide), [OWASP Testing Guide](https://wiki.owasp.org/index.php/OWASP_Testing_Guide_v4_Table_of_Contents)
 - [x] https
 - [ ] max_content_length validation [uploads](https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask)
 - [ ] mask ids (url, upload folder, ...)
 - [ ] fix jrange not resizing (minor)
 - [ ] unify input design (minor)
 - [ ] automatic shopping categories
    - [] Detect category by item and list based on previous entries
 - [x] multiselect in admin panel (admin panel) [currently items only]
 - [x] get lists containing item (admin panel)
 - [x] change item - replace changed if new already exists (admin panel)
 - [ ] user settings (major)

## License
[GNU General Public License v3.0](/LICENSE)
