from .models import Payment
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model.
    This serializer handles the conversion of Payment model instances to JSON
    and vice versa, including validation of fields.
    """
    phone_number = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Payment
        fields = (
            'transaction_id', 'amount', 'currency',
            'payment_method', 'order', 'user', 'status',
            'phone_number', 'created_at', 'updated_at',
            'chapa_tx_ref'
        )
        read_only_fields = ('transaction_id', 'user', 'chapa_tx_ref', 'created_at', 'updated_at')
        extra_kwargs = {
            'status': {'default': 'pending'},
            'currency': {'default': 'ETB'},
            'payment_method': {'default': 'chapa_mobile'},
        }

    def create(self, validated_data):
        """Override create method to handle custom logic."""
        validated_data.pop('phone_number', None)  # Remove the non-model field
        return super().create(validated_data)

    def validate(self, data):
        if data.get('payment_method') == 'mpesa':
            if not data.get('phone_number'):
                raise serializers.ValidationError("Phone number is required for M-Pesa payments.")

            phone = data['phone_number']
            if not (phone.startswith('07') or phone.startswith('+254')) or len(phone) < 10:
                raise serializers.ValidationError("Invalid phone number format for M-Pesa.")
        return data


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
        valid_methods = {
            'chapa_card': 'Chapa Card',
            'chapa_mobile': 'Chapa Mobile',
        }
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Payment method must be one of {list(valid_methods.keys())}."
            )
        return value
