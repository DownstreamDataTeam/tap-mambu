from .generator import TapGenerator
from ..helpers import transform_datetime, get_bookmark


class LoanProductsGenerator(TapGenerator):
    def _init_endpoint_config(self):
        super(LoanProductsGenerator, self)._init_endpoint_config()
        self.endpoint_path = "loanproducts"
        self.endpoint_api_method = "GET"
        self.endpoint_params["sortBy"] = "id:ASC"
        self.endpoint_bookmark_field = "lastModifiedDate"