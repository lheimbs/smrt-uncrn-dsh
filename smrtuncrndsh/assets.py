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
    tablesorter_css = Bundle(
        'css/tablesorter/*.css',
        filters='cssmin', output='gen/tablesorter.css'
    )
    tablesorter_js = Bundle(
        'js/tablesorter/*.js',
        filters='jsmin', output='gen/tablesorter.js'
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
        'tablesorter_css': tablesorter_css,
        'tablesorter_js': tablesorter_js,
        'chosen_css': chosen_css,
        'chosen_js': chosen_js,
        'jquery': jquery,
    }

    assets.register(bundles)
    # assets.register('css_all', css)
    return assets
