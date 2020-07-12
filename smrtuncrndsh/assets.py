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
    select2_css = Bundle(
        'css/select2/select2.css',  # _3-5-4
        filters='cssmin', output='gen/select2.css'
    )
    select2_js = Bundle(
        'js/select2/select2.js',  # _3-5-4.min
        filters='jsmin', output='gen/select2.js'
    )
    chosen_css = Bundle(
        'css/chosen/chosen.min.css',
        filters='cssmin', output='gen/chosen.css'
    )
    chosen_js = Bundle(
        'js/chosen/chosen.jquery.js',
        filters='jsmin', output='gen/chosen.js'
    )
    jquery = Bundle(
        'js/jquery/jquery.min.js',
        filters='jsmin', output='gen/jquery.js'
    )
    bundles = {
        'js_all': js,
        'css_all': css,
        'select2_css': select2_css,
        'select2_js': select2_js,
        'chosen_css': chosen_css,
        'chosen_js': chosen_js,
        'jquery': jquery,
    }

    assets.register(bundles)
    # assets.register('css_all', css)
    return assets
