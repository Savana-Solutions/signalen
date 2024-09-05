import json
import requests
from django.conf import settings
from django.core import validators
from requests import ConnectTimeout
from signals.apps.api.generics.exceptions import GatewayTimeoutException

class MLToolClient:
    timeout = (10.0, 10.0)
    endpoint = "{}/predict".format(settings.ML_TOOL_ENDPOINT)
    predict_validators = [
        validators.MinLengthValidator(limit_value=1),
    ]

    def predict(self, text):
        for validator in self.predict_validators:
            validator(text)

        try:
            data = json.dumps({"text": text})
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                self.endpoint, data=data, headers=headers, timeout=self.timeout
            )
        except ConnectTimeout:
            raise GatewayTimeoutException()
        else:
            return response
