from flask_assets import Environment, Bundle


def compile_assets(app):
    assets = Environment(app)

    js = Bundle(
        'js/*.js', 'home_bp/js/*.js',  # 'admin_bp/js/*.js',
        filters='jsmin', output='gen/packed.js'
    )
    css = Bundle(
        'css/*.css', 'css/dash/*.css',
        'home_bp/css/*.css', 'admin_bp/css/*.css', 'auth_bp/css/*.css',
        'shopping_add_bp/css/*.css',
        filters='cssmin', output='gen/packed.css'
    )
    jquery = Bundle(
        'js/jquery/jquery.min.js',
        filters='jsmin', output='gen/jquery.js'
    )
    chosen_css = Bundle(
        'css/chosen/chosen.min.css',
        filters='cssmin', output='gen/chosen.css'
    )
    chosen_js = Bundle(
        'js/chosen/chosen.jquery.js',
        filters='jsmin', output='gen/chosen.js'
    )
    jrange_css = Bundle(
        'css/jrange/jquery.range.css',
        filters='cssmin', output='gen/jrange.css'
    )
    jrange_js = Bundle(
        'js/jrange/jquery.range.js',
        filters='jsmin', output='gen/jrange.js'
    )
    datatables_css = Bundle(
        'css/datatables/jquery.dataTables.css',
        filters='cssmin', output='gen/datatables.css'
    )
    datatables_js = Bundle(
        'js/datatables/jquery.dataTables.js',
        filters='jsmin', output='gen/datatables.js'
    )
    daterangepicker_css = Bundle(
        'css/daterangepicker/daterangepicker.css',
        filters='cssmin', output='gen/daterangepicker.css'
    )
    daterangepicker_js = Bundle(
        'js/daterangepicker/moment.min.js', 'js/daterangepicker/daterangepicker.js',
        filters='jsmin', output='gen/daterangepicker.js'
    )
    flexdatalist_css = Bundle(
        'css/flexdatalist/jquery.flexdatalist.css',
        filters='cssmin', output='gen/flexdatalist.css'
    )
    flexdatalist_js = Bundle(
        'js/flexdatalist/jquery.flexdatalist.js',
        filters='jsmin', output='gen/flexdatalist.js'
    )

    plotly_js = Bundle(
        'js/plotly/plotly.basic.js',
        filters='jsmin', output='gen/plotly.js'
    )

    bundles = {
        'js_all': js,
        'css_all': css,
        'chosen_css': chosen_css,
        'chosen_js': chosen_js,
        'jrange_css': jrange_css,
        'jrange_js': jrange_js,
        'jquery': jquery,
        'datatables_js': datatables_js,
        'datatables_css': datatables_css,
        'daterangepicker_js': daterangepicker_js,
        'daterangepicker_css': daterangepicker_css,
        'flexdatalist_js': flexdatalist_js,
        'flexdatalist_css': flexdatalist_css,
        'plotly_js': plotly_js,
    }

    assets.register(bundles)
    # assets.register('css_all', css)
    return assets
