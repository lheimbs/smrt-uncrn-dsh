from flask_assets import Environment, Bundle


def compile_assets(app):
    assets = Environment(app)

    js = Bundle(
        'js/*.js', 'home_bp/js/*.js', 'admin_bp/js/*.js',
        filters='jsmin', output='gen/packed.js'
    )
    css = Bundle(
        'css/*.css', 'css/dash/*.css',
        'home_bp/css/*.css', 'admin_bp/css/*.css', 'auth_bp/css/*.css',
        filters='cssmin', output='gen/packed.css'
    )

    assets.register('js_all', js)
    assets.register('css_all', css)
    return assets
