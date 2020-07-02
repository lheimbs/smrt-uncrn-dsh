from flask_assets import Environment, Bundle


def compile_assets(app):
    assets = Environment(app)

    js = Bundle('js/*.js', 'home_bp/static/js/*.js', filters='jsmin', output='gen/packed.js')
    # js_home = Bundle('home_bp/static/js/js/*.js', filters='jsmin', output='gen/packed_home.js')
    css = Bundle('css/*.css', 'home_bp/css/*.css', filters='cssmin', output='gen/packed.css')

    assets.register('js_all', js)
    assets.register('css_all', css)
    return assets
