from .models import Payment
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model.
    This serializer handles the conversion of Payment model instances to JSON
    and vice versa, including validation of fields.
    """
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('transaction_id', 'created_at', 'updated_at')

    def validate_amount(self, value):
        """Ensure that the payment amount is positive."""
        if value < 0:
            raise serializers.ValidationError(
                "Amount must be a positive number."
                )
        return value

    def validate_status(self, value):
        """Ensure that the status is one of the allowed values."""
        valid_statuses = ['pending', 'completed', 'failed', 'refunded']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of {valid_statuses}."
                )
        return value

    def validate_currency(self, value):
        """Ensure that the currency is a valid 3-character code."""
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError(
                "Currency must be a 3-letter code."
                )
        return value.upper()

    def validate_payment_method(self, value):
        """Ensure that the payment method is one of the allowed values."""
        valid_methods = [
            'credit_card', 'mpesa',
            'Airtel Money', 'bank_transfer'
            ]
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Payment method must be one of {valid_methods}."
                )
        return value
