from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        # Import signals to ensure they are registered
        import products.signals
        # Import managers to ensure they are available
        import products.models
        # Import admin to ensure admin configurations are loaded
        import products.admin
        # Import migrations to ensure they are applied
        import products.migrations
        # Import views to ensure they are registered
        import products.views
        # Import serializers to ensure they are available for API usage
        import products.serializers
