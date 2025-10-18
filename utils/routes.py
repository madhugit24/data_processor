from controllers.data_processor import data_processor


def register_routes(app):
    app.register_blueprint(data_processor, url_prefix="/data_processor")