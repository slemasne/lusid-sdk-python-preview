import lusid
import lusid.models as models
import pytz
from datetime import datetime
import uuid
import unittest

from utilities import TestDataUtilities, PortfolioLoader, InstrumentLoader

class BaseValuationUtilities(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a configured API client
        api_client = TestDataUtilities.api_client()

        # Setup required LUSID APIs
        cls.transaction_portfolios_api = lusid.TransactionPortfoliosApi(api_client)
        cls.portfolios_api = lusid.PortfoliosApi(api_client)
        cls.instruments_api = lusid.InstrumentsApi(api_client)
        cls.aggregation_api = lusid.AggregationApi(api_client)
        cls.quotes_api = lusid.QuotesApi(api_client)
        cls.recipes_api = lusid.ConfigurationRecipeApi(api_client)

        # Setup test parameters
        cls.effective_date = datetime(2019, 4, 15, tzinfo=pytz.utc)

        # Setup test data from utilities
        cls.test_data_utilities = TestDataUtilities(cls.transaction_portfolios_api)

        # Setup test portfolios
        cls.portfolio_scope = TestDataUtilities.tutorials_scope
        cls.portfolio_code = cls.test_data_utilities.create_transaction_portfolio(
            TestDataUtilities.tutorials_scope
        )
        cls.xccy_portfolio_code = cls.test_data_utilities.create_transaction_portfolio(
            TestDataUtilities.tutorials_scope
        )
        # Load transactions to test portfolio
        portfolio_loader = PortfolioLoader(
            cls.transaction_portfolios_api, cls.instruments_api
        )
        portfolio_loader.setup_gbp_portfolio(
            cls.portfolio_scope, cls.portfolio_code, cls.effective_date
        )
        portfolio_loader.setup_xccy_portfolio(
            cls.portfolio_scope, cls.xccy_portfolio_code, cls.effective_date
        )

        # Required instruments
        instrument_loader = InstrumentLoader(cls.instruments_api)
        cls.instrument_ids = instrument_loader.load_instruments()

        # Setup scopes for recipe tests
        cls.recipe_scope = "TestIdentifiers"
        cls.recipe_code = "SimpleQuotes"

        # Set market data scope to be used with quotes and recipes
        cls.market_data_provider = "Lusid"
        cls.market_data_scope = "Test-" + str(uuid.uuid4())

        # Set valuation key
        cls.valuation_key = "Sum(Valuation/PV)"
        cls.valuation_portfolio_key = "Sum(Valuation/PvInPortfolioCcy)"


    @classmethod
    def upsert_recipe_request(cls, configuration_recipe) -> None:
        """
        Structures a recipe request and upserts it into LUSID
        :param ConfigurationRecipe configuration_recipe: Recipe configuration
        :return: None
        """

        upsert_recipe_request = models.UpsertRecipeRequest(configuration_recipe)
        cls.recipes_api.upsert_configuration_recipe(upsert_recipe_request)

    @classmethod
    def create_valuation_request(
        cls, portfolio_scope, portfolio_code, recipe_scope, recipe_code
    ) -> lusid.models.ValuationRequest:
        """
        Creates a valuation request that can be used to return results based on
        an upserted recipe for the selected portfolio. The selected key in this
        example will return valuation in the portfolio currency (see 'Valuation/PV'
        for results in domestic currency). Additionally, the 'op' parameter will
        allow for use of arithmetic operators on a given metric. For more info on
        the set of available metrics, see the 'get_queryable_keys()' call under
        LUSID API docs, part of the Aggregation endpoint.
        :param str recipe_scope: The scope for an already upserted recipe
        :param str recipe_code: The code for an already upserted recipe
        :return: ValuationRequest
        """

        recipe_id = models.ResourceId(scope=recipe_scope, code=recipe_code)

        return models.ValuationRequest(
            recipe_id=recipe_id,
            metrics=[
                models.AggregateSpec("Instrument/default/Name", "Value"),
                models.AggregateSpec("Valuation/PvInPortfolioCcy", "Proportion"),
                models.AggregateSpec("Valuation/PvInPortfolioCcy", "Sum"),
                models.AggregateSpec("Valuation/PV", "Proportion"),
                models.AggregateSpec("Valuation/PV", "Sum"),
            ],
            group_by=["Instrument/default/Name"],
            portfolio_entity_ids=[
                models.PortfolioEntityId(
                    scope=portfolio_scope,
                    code=portfolio_code,
                    portfolio_entity_type="SinglePortfolio",
                )
            ],
            valuation_schedule=models.ValuationSchedule(
                effective_from=cls.effective_date, effective_at=cls.effective_date
            ),
        )

    @classmethod
    def tearDownClass(cls):
        # Delete Portfolios once tests are finished
        portfolio_codes = [
            cls.portfolio_code,
            cls.xccy_portfolio_code,
        ]

        # Delete portfolio once tests are concluded
        for code in portfolio_codes:
            cls.portfolios_api.delete_portfolio(TestDataUtilities.tutorials_scope, code)