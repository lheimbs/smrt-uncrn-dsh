from flask_assets import Environment, Bundle

def compile_assets(app):
    assets = Environment(app)

    js = Bundle('js/*.js', filters='jsmin', output='gen/packed.js')
    css = Bundle('css/*.css', filters='cssmin', output='gen/packed.css')

    assets.register('js_all', js)
    assets.register('css_all', css)
    return assets
