from flask_assets import Environment, Bundle


def compile_assets(app):
    assets = Environment(app)

    js = Bundle(
        'js/*.js', 'home_bp/static/js/*.js', 'admin_bp/static/js/*.js','auth_bp/static/js/*.js',
        filters='jsmin', output='gen/packed.js'
    )
    css = Bundle(
        'css/*.css', 'home_bp/css/*.css', 'admin_bp/css/*.css', 'auth_bp/css/*.css',
        filters='cssmin', output='gen/packed.css'
    )

    assets.register('js_all', js)
    assets.register('css_all', css)
    return assets
