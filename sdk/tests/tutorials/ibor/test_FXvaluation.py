import unittest
from datetime import datetime
from datetime import timedelta

import pytz

import lusid
import lusid.models as models
from utilities import TestDataUtilities
from collections import defaultdict
import json
import pandas as pd


# # Cocoon
from lusidtools import cocoon as lpt
from lusidtools.pandas_utils.lusid_pandas import lusid_response_to_data_frame
from lusidtools.cocoon.cocoon_printer import format_instruments_response, format_portfolios_response, format_transactions_response, format_quotes_response



#from xml.etree import ElementTree
import xml.dom.minidom

class Valuation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create a configured API client
        cls.api_client = TestDataUtilities.api_client()
        cls.api_factory = lusid.utilities.api_client_factory.ApiClientFactory(api_secrets_filename="../../secrets.json")
        cls.transaction_portfolios_api = lusid.TransactionPortfoliosApi(cls.api_client)
        cls.instruments_api = lusid.InstrumentsApi(cls.api_client)
        cls.aggregation_api = lusid.AggregationApi(cls.api_client)
        cls.quotes_api = lusid.QuotesApi(cls.api_client)
        cls.SMD_api = lusid.StructuredMarketDataApi(cls.api_client)
        cls.start_GBPUSD_FX_price = 1.3044
        cls.start_USDJPY_FX_price = 109.106
        cls.start_EURGBP_FX_price = 0.84247

        cls.GBPUSDpip_1y = 119
        cls.GBPUSDpip_2y = 209
        cls.GBPUSDpip_3y = 302
        cls.GBPUSDpip_5y = 489
        cls.GBPUSDpip_10y = 1100
        cls.USDJPYpip_3m = 53
        cls.USDJPYpip_6m = 107
        cls.USDJPYpip_9m = 157.5
        cls.USDJPYpip_12m = 211

    def test_portfolio_aggregation(self):

        effective_date = datetime(2019, 4, 15, tzinfo=pytz.utc)

        portfolio_code = self.test_data_utilities.create_transaction_portfolio(TestDataUtilities.tutorials_scope)

        transactions = [
            self.test_data_utilities.build_transaction_request(instrument_id=self.instrument_ids[0],
                                                               units=100,
                                                               price=101,
                                                               currency="GBP",
                                                               trade_date=effective_date,
                                                               transaction_type="StockIn"),
            self.test_data_utilities.build_transaction_request(instrument_id=self.instrument_ids[1],
                                                               units=100,
                                                               price=102,
                                                               currency="GBP",
                                                               trade_date=effective_date,
                                                               transaction_type="StockIn"),
            self.test_data_utilities.build_transaction_request(instrument_id=self.instrument_ids[2],
                                                               units=100,
                                                               price=103,
                                                               currency="GBP",
                                                               trade_date=effective_date,
                                                               transaction_type="StockIn")
        ]

        self.transaction_portfolios_api.upsert_transactions(scope=TestDataUtilities.tutorials_scope,
                                                            code=portfolio_code,
                                                            transactions=transactions)

        prices = [
            (self.instrument_ids[0], 100),
            (self.instrument_ids[1], 200),
            (self.instrument_ids[2], 300)
        ]

        requests = [
            models.UpsertQuoteRequest(
                quote_id=models.QuoteId(
                    models.QuoteSeriesId(
                        provider="DataScope",
                        instrument_id=price[0],
                        instrument_id_type="LusidInstrumentId",
                        quote_type="Price",
                        field="mid"
                    ),
                    effective_at=effective_date
                ),
                metric_value=models.MetricValue(
                    value=price[1],
                    unit="GBP"
                )
            )
            for price in prices
        ]

        self.quotes_api.upsert_quotes(TestDataUtilities.tutorials_scope,
                                      quotes={"quote" + str(request_number): requests[request_number]
                                              for request_number in range(len(requests))})

        inline_recipe = models.ConfigurationRecipe(
            code='quotes_recipe',
            market=models.MarketContext(
                market_rules=[],
                suppliers=models.MarketContextSuppliers(
                    equity='DataScope'
                ),
                options=models.MarketOptions(
                    default_supplier='DataScope',
                    default_instrument_code_type='LusidInstrumentId',
                    default_scope=TestDataUtilities.tutorials_scope)
            )
        )

        aggregation_request = models.AggregationRequest(
            inline_recipe=inline_recipe,
            metrics=[
                models.AggregateSpec("Instrument/default/Name", "Value"),
                models.AggregateSpec("Holding/default/PV", "Proportion"),
                models.AggregateSpec("Holding/default/PV", "Sum")
            ],
            group_by=["Instrument/default/Name"],
            effective_at=effective_date
        )

        #   do the aggregation
        aggregation = self.aggregation_api.get_aggregation_by_portfolio(scope=TestDataUtilities.tutorials_scope,
                                                                        code=portfolio_code,
                                                                        request=aggregation_request)

        for item in aggregation.data:
            print("\t{}\t{}\t{}".format(item["Instrument/default/Name"], item["Proportion(Holding/default/PV)"],
                                        item["Sum(Holding/default/PV)"]))

        # Asserts
        self.assertEqual(len(aggregation.data),3)
        self.assertEqual(aggregation.data[0]["Sum(Holding/default/PV)"], 10000)
        self.assertEqual(aggregation.data[1]["Sum(Holding/default/PV)"], 20000)
        self.assertEqual(aggregation.data[2]["Sum(Holding/default/PV)"], 30000)


    ################################################
    # Test: FXFwds, returning the PV from 3 different models:
    # QPS, Tracs and VolMaster, showing the simplicity of revaluing with different vendor models
    # Maturities are 3, 5, and 10 years
    # GBPUSD FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EGBPUSD/forward-rates
    # Spot FX is global, taken from the same site
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FX_FWD(self):

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date

        end_date_3y = start_date.replace(year=start_date.year + 3)
        end_date_5y = start_date.replace(year=start_date.year + 5)
        end_date_10y = start_date.replace(year=start_date.year + 10)

        dom_amount = 100000000

        # Use mkt fwd pips to generate fwd FX prices for foreign leg (USD)

        fwd_FX_price_3y = self.start_GBPUSD_FX_price + self.GBPUSDpip_3y / 10000
        fwd_FX_price_5y = self.start_GBPUSD_FX_price + self.GBPUSDpip_5y / 10000
        fwd_FX_price_10y = self.start_GBPUSD_FX_price + self.GBPUSDpip_10y / 10000

        # use foreign fwd FX price to generate foreign cash leg
        fgn_amount_3y = dom_amount * -fwd_FX_price_3y
        fgn_amount_5y = dom_amount * -fwd_FX_price_5y
        fgn_amount_10y = dom_amount * -fwd_FX_price_10y

        #The market data scope refers to the user partition into which market data is stored
        #The supplier denotes the owner of the market data (not the price source)
        #This *must* match the recipe ruleset that is used to retrieve the data or it will not be found.

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for spot FX GBP/USD
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=self.start_GBPUSD_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        #create the FX forward instruments

        instrument_definition_3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_3y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=self.start_GBPUSD_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_3y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition_5y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_5y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=self.start_GBPUSD_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_5y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition_10y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_10y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=self.start_GBPUSD_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_10y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        print(response)

        #set up a simple list of the 3 vendor models we will be applying

        vendorModel=[]

        vendorModel.append(models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))


        #next we take the fwd instruments and add them to an inline weighted instrument list for pricing

        weightedInstrumentFXFwd_3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3y",
                                                            instrument=instrument_definition_3y)

        weightedInstrumentFXFwd_5y = models.WeightedInstrument(quantity=1, holding_identifier="myholding5y",
                                                              instrument=instrument_definition_5y)

        weightedInstrumentFXFwd_10y = models.WeightedInstrument(quantity=1, holding_identifier="myholding10y",
                                                              instrument=instrument_definition_10y)

        weightedInstrumentList = [weightedInstrumentFXFwd_3y, weightedInstrumentFXFwd_5y, weightedInstrumentFXFwd_10y]

        # finally we loop through each vendor model in our list and call the aggregation

        for model in vendorModel:

            # to create the recipe, in this case we will need a pricing and a market context.
            # the former attaches the pricing model used and parameters around its usage
            # the latter contains instructions on the market data source and rules
            pricingContext = models.PricingContext(model_rules=[model])
            marketContext = models.MarketContext(
                options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

            # the recipe then binds together these constituents
            RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

            if model.supplier == "RefinitivTracsWeb":
                pricing_date = trade_date - timedelta(days=1)
            else:
                pricing_date = trade_date

            # the aggregation is a powerful mechanism for producing a result set, we will show later how the cashflow
            # output can be pushed straight back into the movements engine. It can also persist external results
            # and will shortly combine with Honeycomb for reporting
            aggregationRequestResource = models.AggregationRequest(
                inline_recipe=RecipeId,
                effective_at=pricing_date.isoformat(),
                metrics=[
                    models.AggregateSpec(key='Analytic/default/ValuationDate',
                                         op='Value'),
                    models.AggregateSpec(key='Holding/default/PV',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/DomCcy',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/FgnCcy',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/StartDate',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/MaturityDate',
                                         op='Value')
                ]
            )
            inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                                 instruments=weightedInstrumentList)

            # Call LUSID to perform the aggregation, print the result

            response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                    inline_request=inlineRequestFXFwd)

            print(response)

    ################################################
    # Test: FXOptions, returning the PV from 3 different models:
    # QPS, Tracs and VolMaster, showing the simplicity of revaluing with different vendor models
    # Maturities are 1, 2, and 3 years
    # GBPUSD FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EGBPUSD/forward-rates
    # Strike is set as the fwd FX level to approximate ATM
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FX_OPT(self):

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date

        end_date_1y = start_date.replace(year=start_date.year + 1)
        end_date_2y = start_date.replace(year=start_date.year + 2)
        end_date_3y = start_date.replace(year=start_date.year + 3)

        dom_amount = 100000000

        fwd_FX_price_1y = self.start_GBPUSD_FX_price + self.GBPUSDpip_1y / 10000
        fwd_FX_price_2y = self.start_GBPUSD_FX_price + self.GBPUSDpip_2y / 10000
        fwd_FX_price_3y = self.start_GBPUSD_FX_price + self.GBPUSDpip_3y / 10000

        fgn_amount_1y = dom_amount * -fwd_FX_price_1y
        fgn_amount_2y = dom_amount * -fwd_FX_price_2y
        fgn_amount_3y = dom_amount * -fwd_FX_price_3y

        '''
            The market data scope and supplier refer to (effectively) two fields in the database that describe who 'supplied' the data 
            and the user 'scope' into which it is put. This *must* match the rule that is used to retrieve it or it simply will not be found. 
        '''
        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for the FX GBP/USD for today
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=self.start_GBPUSD_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition_1y = models.FxOption(
            start_date=start_date.isoformat(),
            option_maturity_date=end_date_1y.isoformat(),
            option_settlement_date=end_date_1y.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_FX_price_1y,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption"
        )

        instrument_definition_2y = models.FxOption(
            start_date=start_date.isoformat(),
            option_maturity_date=end_date_2y.isoformat(),
            option_settlement_date=end_date_2y.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_FX_price_2y,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption"
        )

        instrument_definition_3y = models.FxOption(
            start_date=start_date.isoformat(),
            option_maturity_date=end_date_3y.isoformat(),
            option_settlement_date=end_date_3y.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_FX_price_3y,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption"
        )

        print(response)

        vendorModel = []
        vendorModel.append(models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                                  instrument_type="FxOption", parameters="{}"))

        # vendorModel.append(models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
        #                                           instrument_type="FxOption", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                                  instrument_type="FxOption", parameters="{}"))



        notional =100000000
        weightedInstrumentFXOpt_1y = models.WeightedInstrument(
            quantity=notional, holding_identifier="myholding1y",
            instrument=instrument_definition_1y
        )
        weightedInstrumentFXOpt_2y = models.WeightedInstrument(
            quantity=notional, holding_identifier="myholding2y",
            instrument=instrument_definition_2y
        )
        weightedInstrumentFXOpt_3y = models.WeightedInstrument(
            quantity=notional, holding_identifier="myholding3y",
            instrument=instrument_definition_3y
        )

        weightedInstrumentList = [weightedInstrumentFXOpt_1y, weightedInstrumentFXOpt_2y, weightedInstrumentFXOpt_3y]

        for model in vendorModel:
            pricingContext = models.PricingContext(model_rules=[model])
            marketContext = models.MarketContext(
                options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

            RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

            if model.supplier == "RefinitivTracsWeb":
                pricing_date = trade_date - timedelta(days=1)
            else:
                pricing_date = trade_date

            aggregationRequestResource = models.AggregationRequest(
                inline_recipe=RecipeId,
                effective_at=pricing_date.isoformat(),
                metrics=[
                    models.AggregateSpec(key='Analytic/default/ValuationDate',
                                         op='Value'),
                    models.AggregateSpec(key='Holding/default/PV',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/DomCcy',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/FgnCcy',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/StartDate',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/MaturityDate',
                                         op='Value')
                ]
            )
            inlineRequestFXOpt = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                                 instruments=weightedInstrumentList)

            # Call LUSID to perform the aggregation

            response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                    inline_request=inlineRequestFXOpt)

            print(response)

    ################################################
    # Test: Show bump and value delta with a series of 4 FXFwds
    # Maturities are 3m, 6m, 9m, 1y
    # Test creates FRA curves for USD and JPY out to 1 year with flat rates
    # Risk can be compared across maturities...rerun manually to show risk down the curve
    # USDJPY FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EUSDJPY/forward-rates
    # Spot FX is global, taken from the same site
    # Models tested - LUSID
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_delta_lusid(self):


        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date


        end_date_3m = start_date.replace(month=start_date.month + 3)
        end_date_6m = start_date.replace(month=start_date.month + 6)
        end_date_9m = start_date.replace(month=start_date.month + 9)
        end_date_12m = start_date.replace(year=start_date.year + 1)

        ccyList=['USD', 'JPY']

        # call the curve load and creation. note the market data scope passed determines the loaction
        # and is used later for retrieval
        response = self.create_structure_market_data(ccyList,effectiveAt, marketDataScope)

        dom_amount = 100000000
        fgn_amount_3m = dom_amount * -(self.start_USDJPY_FX_price - self.USDJPYpip_3m / 100)
        fgn_amount_6m = dom_amount * -(self.start_USDJPY_FX_price - self.USDJPYpip_6m /100)
        fgn_amount_9m = dom_amount * -(self.start_USDJPY_FX_price - self.USDJPYpip_9m / 100)
        fgn_amount_12m = dom_amount * -(self.start_USDJPY_FX_price - self.USDJPYpip_12m / 100)

        # Create a quote for the FX USD/JPY for effective date
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=effectiveAt,
            ),
            metric_value=models.MetricValue(
                value=self.start_USDJPY_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition_3m = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_3m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=effectiveAt.isoformat(),
            maturity_date=end_date_3m.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_6m = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=effectiveAt.isoformat(),
            maturity_date=end_date_6m.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_9m = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_9m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=effectiveAt.isoformat(),
            maturity_date=end_date_9m.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_12m = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_12m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=effectiveAt.isoformat(),
            maturity_date=end_date_12m.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        pricingContext = models.PricingContext(
            options=models.PricingOptions(produce_separate_result_for_linear_otc_legs=False),
            model_rules=[
                models.VendorModelRule(supplier="Lusid", model_name="Discounting", instrument_type="FxForward",
                                       parameters="{}")
            ]
        )
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope),
            market_rules=[
                models.MarketDataKeyRule(key="Fx.*.*", data_scope=marketDataScope, supplier=marketSupplier,
                                         quote_type='Price', field='mid'),
                models.MarketDataKeyRule(key="Rates.*.*", data_scope=marketDataScope, supplier=marketSupplier,
                                         quote_type='Rate', field='mid')
            ]
        )
        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXFwd_3m = models.WeightedInstrument(quantity=1, holding_identifier="myholding3m",
                                                               instrument=instrument_definition_3m)
        weightedInstrumentFXFwd_6m = models.WeightedInstrument(quantity=1, holding_identifier="myholding6m",
                                                               instrument=instrument_definition_6m)
        weightedInstrumentFXFwd_9m = models.WeightedInstrument(quantity=1, holding_identifier="myholding9m",
                                                               instrument=instrument_definition_9m)
        weightedInstrumentFXFwd_12m = models.WeightedInstrument(quantity=1, holding_identifier="myholding12m",
                                                               instrument=instrument_definition_12m)
        weightedInstrumentList = [weightedInstrumentFXFwd_6m]

        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/Delta',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/ParallelDelta',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)
        print(response)

    def loadFile(name):
        with open(name, "r") as myfile:
            data = myfile.read()
        return data

    def create_structure_market_data(self, ccyList, effectiveAt, scope):

        # load set of structured market data description files.
        # Note that the examples have hard-coded rates. However, these can be RIC references, instrument definitions etc..
        # Please refer to online documentation for full details.
        # Upsert the curves into the same scope as the earlier FX quote

        smdRequestDictionary = {}
        for ccy in ccyList:
            # load doc
            fileName = 'Lusid_MktData_Rates_Fra_%s_20190101.xml' % ccy
            xmlDoc = Valuation.loadFile(fileName)
            # create request
            structuredDoc = models.StructuredMarketData(document_format="Xml", version="1.0.0",
                                                        name="%sRatesCurve" % ccy, document=xmlDoc)
            structuredId = models.StructuredMarketDataId(provider="Lusid",price_source=None,            #price source to be added when rules can pick up
                                                         lineage="MyDemoData", effective_at=effectiveAt,
                                                         market_element_type="ZeroCurve",
                                                         market_asset="%s/%sOIS" % (ccy, ccy))
            smdRequest = models.UpsertStructuredMarketDataRequest(market_data_id=structuredId,
                                                                  market_data=structuredDoc)
            smdRequestDictionary[ccy] = smdRequest

        # Call LUSID to upsert structured market data
        response = self.SMD_api.upsert_structured_market_data(
            scope=scope,
            structured_data=smdRequestDictionary
        )

        return response


    ################################################
    # Test: Show option expiry ladder with a series of 9 aged FXFwds
    # Expiries are in the next few days, so we must be aware of imminent actions required
    # Result set shows events and cashflows
    # The events connect to cashflow management, visualisation, workflow triggers
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FXOption_expiry_schedule(self):

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_1d = start_date + timedelta(days=1)
        end_date_2d = start_date + timedelta(days=2)
        end_date_3d = start_date + timedelta(days=3)

        start_date_1d1y = end_date_1d.replace(year=end_date_1d.year -1)
        start_date_2d1y = end_date_2d.replace(year=end_date_1d.year -1)
        start_date_3d1y = end_date_3d.replace(year=end_date_1d.year -1)

        start_date_1d2y = end_date_1d.replace(year=end_date_1d.year - 2)
        start_date_2d2y = end_date_2d.replace(year=end_date_1d.year - 2)
        start_date_3d2y = end_date_3d.replace(year=end_date_1d.year - 2)

        start_date_1d3y = end_date_1d.replace(year=end_date_1d.year - 3)
        start_date_2d3y = end_date_2d.replace(year=end_date_1d.year - 3)
        start_date_3d3y = end_date_3d.replace(year=end_date_1d.year - 3)

        ccyList=['USD', 'JPY']

        response = self.create_structure_market_data(ccyList,effectiveAt, marketDataScope)

        dom_amount = 100000000
        fwd_6m = self.start_USDJPY_FX_price - self.USDJPYpip_6m / 100
        fgn_amount_6m = dom_amount * - fwd_6m

        # Create a quote for the FX USD/JPY for effective date
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=effectiveAt,
            ),
            metric_value=models.MetricValue(
                value=self.start_USDJPY_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition_1d1y = models.FxOption(
            start_date=start_date_1d1y.isoformat(),
            option_maturity_date=end_date_1d.isoformat(),
            option_settlement_date=end_date_1d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )
        instrument_definition_2d1y = models.FxOption(
            start_date=start_date_2d1y.isoformat(),
            option_maturity_date=end_date_2d.isoformat(),
            option_settlement_date=end_date_2d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )

        instrument_definition_3d1y = models.FxOption(
            start_date=start_date_3d1y.isoformat(),
            option_maturity_date=end_date_3d.isoformat(),
            option_settlement_date=end_date_3d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )
        instrument_definition_1d2y = models.FxOption(
            start_date=start_date_1d2y.isoformat(),
            option_maturity_date=end_date_1d.isoformat(),
            option_settlement_date=end_date_1d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )
        instrument_definition_2d2y = models.FxOption(
            start_date=start_date_2d2y.isoformat(),
            option_maturity_date=end_date_2d.isoformat(),
            option_settlement_date=end_date_2d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )

        instrument_definition_3d2y = models.FxOption(
            start_date=start_date_3d2y.isoformat(),
            option_maturity_date=end_date_3d.isoformat(),
            option_settlement_date=end_date_3d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )

        instrument_definition_1d3y = models.FxOption(
            start_date=start_date_1d3y.isoformat(),
            option_maturity_date=end_date_1d.isoformat(),
            option_settlement_date=end_date_1d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )
        instrument_definition_2d3y = models.FxOption(
            start_date=start_date_2d3y.isoformat(),
            option_maturity_date=end_date_2d.isoformat(),
            option_settlement_date=end_date_2d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )

        instrument_definition_3d3y = models.FxOption(
            start_date=start_date_3d3y.isoformat(),
            option_maturity_date=end_date_3d.isoformat(),
            option_settlement_date=end_date_3d.isoformat(),
            is_delivery_not_cash=True,
            is_call_not_put=True,
            strike=fwd_6m,
            dom_ccy="USD",
            fgn_ccy="JPY",
            instrument_type="FxOption"
        )

        pricingContext = models.PricingContext(
            options=models.PricingOptions(
                allow_any_instruments_with_sec_uid_to_price_off_lookup=True,
                allow_partially_successful_evaluation=True
            ),
        )

        # marketContext = models.MarketContext(
        #     options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope),
        #     market_rules=[
        #         models.MarketDataKeyRule(key="Fx.*.*", data_scope=marketDataScope, supplier=marketSupplier,
        #                                  quote_type='Price', field='mid'),
        #         models.MarketDataKeyRule(key="Rates.*.*", data_scope=marketDataScope, supplier=marketSupplier,
        #                                  quote_type='Rate', field='mid')
        #     ]
        # )
        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext) #, market=marketContext)

        weightedInstrumentFXOpt_1d1y = models.WeightedInstrument(quantity=1, holding_identifier="myholding1d1y",
                                                               instrument=instrument_definition_1d1y)
        weightedInstrumentFXOpt_2d1y = models.WeightedInstrument(quantity=1, holding_identifier="myholding2d1y",
                                                               instrument=instrument_definition_2d1y)
        weightedInstrumentFXOpt_3d1y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3d1y",
                                                               instrument=instrument_definition_3d1y)

        weightedInstrumentFXOpt_1d2y = models.WeightedInstrument(quantity=1, holding_identifier="myholding1d2y",
                                                               instrument=instrument_definition_1d2y)
        weightedInstrumentFXOpt_2d2y = models.WeightedInstrument(quantity=1, holding_identifier="myholding2d2y",
                                                               instrument=instrument_definition_2d2y)
        weightedInstrumentFXOpt_3d2y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3d2y",
                                                               instrument=instrument_definition_3d2y)

        weightedInstrumentFXOpt_1d3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding1d3y",
                                                               instrument=instrument_definition_1d3y)
        weightedInstrumentFXOpt_2d3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding2d3y",
                                                               instrument=instrument_definition_2d3y)
        weightedInstrumentFXOpt_3d3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3d3y",
                                                               instrument=instrument_definition_3d3y)



        weightedInstrumentList = [weightedInstrumentFXOpt_1d1y,weightedInstrumentFXOpt_2d1y,weightedInstrumentFXOpt_3d1y,
                                  weightedInstrumentFXOpt_1d2y,weightedInstrumentFXOpt_2d2y,weightedInstrumentFXOpt_3d2y,
                                  weightedInstrumentFXOpt_1d3y,weightedInstrumentFXOpt_2d3y,weightedInstrumentFXOpt_3d3y]

        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEvent',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEventType',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/HoldingCashflows',
                                     op='Value')
            ]
        )
        inlineRequestFXOpt = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXOpt)

        cf2=defaultdict(float)

        # for options we should see NaN for cashflows
        for i in response.data:
            (dt,dtv) = next(iter(i['Analytic/default/HoldingCashflows']['slices']['USD']['labelsY'].items()))
            (cash,v2) = next(iter(i['Analytic/default/HoldingCashflows']['slices']['USD']['values'].items()))
            cf2[dt] += v2
        print(cf2)

        # check for nextEventType = Exercise and collect nextEvent dates as a unique set
        eventList = set()
        for i in response.data:
            if i['Analytic/default/NextEventType']=="Exercise":
                eventList.add(i['Analytic/default/NextEvent'])

        print(eventList)

    ################################################
    # Test: Single FXFwd bi-temporal audit of an incorrect spot rate
    # Maturity is 3 years
    # An erroneous (fat finger) USDJPY spot is entered.
    # Even though time elapsed is milliseconds until correction is entered,
    # LUSID is able to recreate aggregation from both versions of the quote
    # This is immensely powerful for P&L audit
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_bi_temporal_PV_erroneous_FX(self):
        # A test that demonstrates how to
        # (1) Upload sample complex market data to Lusid, namely a pair of curves
        # (2) Define an fx-forward instrument
        # (3) Call Lusid to evaluate the Fx-Forward PV and its rates delta

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_12m = start_date.replace(year=start_date.year + 1)

        dom_amount = 100000000
        fgn_amount_12m = dom_amount * -(self.start_USDJPY_FX_price - self.USDJPYpip_12m / 100)

        # set an erroneous FX rate

        erroneous_FX = self.start_USDJPY_FX_price * 1.25

        # first, by mistake we save the erroneous FX rate as the real one
        # Create a quote for the FX USD/JPY for effective date
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=effectiveAt,
            ),
            metric_value=models.MetricValue(
                value=erroneous_FX,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        # let's capture the as at time to show we can retrieve the result later

        added_quote_time1 = response.values['1']._as_at

        # now we spot the error and correct
        # Create a quote for the FX USD/JPY for effective date
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=effectiveAt,
            ),
            metric_value=models.MetricValue(
                value=self.start_USDJPY_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        # let's save this as at  time too
        added_quote_time2 = response.values['1']._as_at
        instrument_definition_12m = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_12m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=effectiveAt.isoformat(),
            maturity_date=end_date_12m.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        pricingContext = models.PricingContext(
            options=models.PricingOptions(produce_separate_result_for_linear_otc_legs=False),
            model_rules=[
                models.VendorModelRule(supplier="Lusid", model_name="SimpleStatic", instrument_type="FxForward",
                                       parameters="{}")
            ]
        )
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope),
            market_rules=[
                models.MarketDataKeyRule(key="Fx.*.*", data_scope=marketDataScope, supplier=marketSupplier,
                                         quote_type='Price', field='mid'),
                models.MarketDataKeyRule(key="Rates.*.*", data_scope=marketDataScope, supplier=marketSupplier,
                                         quote_type='Rate', field='mid')
            ]
        )
        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXFwd_12m = models.WeightedInstrument(quantity=1,
                                                                holding_identifier="myholding12m",
                                                                instrument=instrument_definition_12m)
        weightedInstrumentList = [weightedInstrumentFXFwd_12m]

        # let's call the aggregation twice, to prove that we can see the erroneous PV and the correct PV

        aggregationRequestResource_erroneous = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            as_at=added_quote_time1.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd_erroneous = models.InlineAggregationRequest(request=aggregationRequestResource_erroneous,
                                                                       instruments=weightedInstrumentList)

        aggregationRequestResource_correct = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            as_at=added_quote_time2.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd_correct = models.InlineAggregationRequest(request=aggregationRequestResource_correct,
                                                                     instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd_erroneous)
        print(response)
        print("erroneous as at", added_quote_time1)
        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd_correct)
        print(response)
        print("corrected as at", added_quote_time2)

    ################################################
    # Test: Show fwd cashflows from a set of 9 aged FXFwds
    # Maturity for all is in the next few days
    # NB there are cash amounts in the slices unlike options, where the cash is unknown
    # and there is nothing in NextEvent, because known cashflows are not regarded as events
    # Therefore cash amounts can be aggregated
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FXFwd_expiry_schedule(self):

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_1d = start_date + timedelta(days=1)
        end_date_2d = start_date + timedelta(days=2)
        end_date_3d = start_date + timedelta(days=3)

        start_date_1d1y = end_date_1d.replace(year=end_date_1d.year - 1)
        start_date_2d1y = end_date_2d.replace(year=end_date_1d.year - 1)
        start_date_3d1y = end_date_3d.replace(year=end_date_1d.year - 1)

        start_date_1d2y = end_date_1d.replace(year=end_date_1d.year - 2)
        start_date_2d2y = end_date_2d.replace(year=end_date_1d.year - 2)
        start_date_3d2y = end_date_3d.replace(year=end_date_1d.year - 2)

        start_date_1d3y = end_date_1d.replace(year=end_date_1d.year - 3)
        start_date_2d3y = end_date_2d.replace(year=end_date_1d.year - 3)
        start_date_3d3y = end_date_3d.replace(year=end_date_1d.year - 3)

        ccyList = ['USD', 'JPY']

        dom_amount = 100000000
        fwd_6m = self.start_USDJPY_FX_price - self.USDJPYpip_6m / 100
        fgn_amount_6m = dom_amount * - fwd_6m

        # Create a quote for the FX USD/JPY for effective date
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=effectiveAt,
            ),
            metric_value=models.MetricValue(
                value=self.start_USDJPY_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})


        instrument_definition_1d1y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_1d1y.isoformat(),
            maturity_date=end_date_1d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_2d1y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_2d1y.isoformat(),
            maturity_date=end_date_2d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_3d1y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_3d1y.isoformat(),
            maturity_date=end_date_3d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_1d2y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_1d2y.isoformat(),
            maturity_date=end_date_1d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_2d2y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_2d2y.isoformat(),
            maturity_date=end_date_2d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")
        instrument_definition_3d2y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_3d2y.isoformat(),
            maturity_date=end_date_3d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_1d3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_1d3y.isoformat(),
            maturity_date=end_date_1d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")
        instrument_definition_2d3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_2d3y.isoformat(),
            maturity_date=end_date_2d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        instrument_definition_3d3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=self.start_USDJPY_FX_price,
            start_date=start_date_3d3y.isoformat(),
            maturity_date=end_date_3d.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        pricingContext = models.PricingContext(
            options=models.PricingOptions(
                allow_any_instruments_with_sec_uid_to_price_off_lookup=True,
                allow_partially_successful_evaluation=True
            ),
        )

        # marketContext = models.MarketContext(
        #     options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope),
        #     market_rules=[
        #         models.MarketDataKeyRule(key="Fx.*.*", data_scope=marketDataScope, supplier=marketSupplier,
        #                                  quote_type='Price', field='mid'),
        #         models.MarketDataKeyRule(key="Rates.*.*", data_scope=marketDataScope, supplier=marketSupplier,
        #                                  quote_type='Rate', field='mid')
        #     ]
        # )
        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext)  # , market=marketContext)

        weightedInstrumentFXFwd_1d1y = models.WeightedInstrument(quantity=1, holding_identifier="myholding1d1y",
                                                                 instrument=instrument_definition_1d1y)
        weightedInstrumentFXFwd_2d1y = models.WeightedInstrument(quantity=1, holding_identifier="myholding2d1y",
                                                                 instrument=instrument_definition_2d1y)
        weightedInstrumentFXFwd_3d1y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3d1y",
                                                                 instrument=instrument_definition_3d1y)

        weightedInstrumentFXFwd_1d2y = models.WeightedInstrument(quantity=1, holding_identifier="myholding1d2y",
                                                                 instrument=instrument_definition_1d2y)
        weightedInstrumentFXFwd_2d2y = models.WeightedInstrument(quantity=1, holding_identifier="myholding2d2y",
                                                                 instrument=instrument_definition_2d2y)
        weightedInstrumentFXFwd_3d2y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3d2y",
                                                                 instrument=instrument_definition_3d2y)

        weightedInstrumentFXFwd_1d3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding1d3y",
                                                                 instrument=instrument_definition_1d3y)
        weightedInstrumentFXFwd_2d3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding2d3y",
                                                                 instrument=instrument_definition_2d3y)
        weightedInstrumentFXFwd_3d3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3d3y",
                                                                 instrument=instrument_definition_3d3y)

        weightedInstrumentList = [weightedInstrumentFXFwd_1d1y, weightedInstrumentFXFwd_2d1y,
                                  weightedInstrumentFXFwd_3d1y,
                                  weightedInstrumentFXFwd_1d2y, weightedInstrumentFXFwd_2d2y,
                                  weightedInstrumentFXFwd_3d2y,
                                  weightedInstrumentFXFwd_1d3y, weightedInstrumentFXFwd_2d3y,
                                  weightedInstrumentFXFwd_3d3y]

        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEvent',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEventType',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/HoldingCashflows',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)

        cf2 = defaultdict(float)

        # for options we should see nonsense cashflows
        for i in response.data:
            (dt, dtv) = next(iter(i['Analytic/default/HoldingCashflows']['slices']['USD']['labelsY'].items()))
            (cash, v2) = next(iter(i['Analytic/default/HoldingCashflows']['slices']['USD']['values'].items()))
            cf2[dt] += v2
        print(cf2)

        # or check for nextEventType = Exercise and collect nextEvent dates as a unique set
        eventList = set()
        for i in response.data:
            if i['Analytic/default/NextEventType'] == "Exercise":
                eventList.add(i['Analytic/default/NextEvent'])

        print(eventList)

    ################################################
    # Test: Show 10yr IRS cashflows
    # Maturity 10y, semi bond 6s EUR IRS
    # Test will only show (for now) known (set) cashflows
    # NB there are cash amounts in the slices unlike options, where the cash is unknown
    # and there is nothing in NextEvent, because known cashflows are not regarded as events
    # Models tested - LUSID
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_IRS_schedule(self):

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_10y = start_date.replace(year=start_date.year + 10)

        swapCCY = "EUR"

        dom_amount = 75000000

        #create the flow convention for each leg

        flow_conventionFixed= models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6,unit="M"),
            day_count_convention="ThirtyU360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )
        flow_conventionFloat = models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6, unit="M"),
            day_count_convention="Act360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )

        # create the swap legs themselves

        #irs_legs=[]
        instrument_definition_leg1 = models.InstrumentLeg(
            conventions=flow_conventionFixed,
            is_pay_not_receive=True,
            is_float_not_fixed=False,
            fixed_rate=0.01
        )
        instrument_definition_leg2 = models.InstrumentLeg(
            conventions=flow_conventionFloat,
            is_pay_not_receive=False,
            is_float_not_fixed=True,
            fixed_rate=0.0
        )
        irs_legs = [
            instrument_definition_leg1,
            instrument_definition_leg2
        ]

        #create the swap
        instrument_definition_10yEURIRS = models.SwapInstrument(
            start_date=start_date.isoformat(),
            maturity_date=end_date_10y.isoformat(),
            notional=dom_amount,
            legs=irs_legs,
            is_amortizing=False,
            notional_exchange_type="None",
            instrument_type="InterestRateSwap")

        pricingContext = models.PricingContext(
            options=models.PricingOptions(
                allow_any_instruments_with_sec_uid_to_price_off_lookup=True,
                allow_partially_successful_evaluation=True
            ),
        )

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext)  # , market=marketContext)

        weightedInstrument_10yEURIRS = models.WeightedInstrument(quantity=1, holding_identifier="myholding_10yEURIRS",
                                                                 instrument=instrument_definition_10yEURIRS)
        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEvent',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEventType',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/HoldingCashflows',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=[weightedInstrument_10yEURIRS])

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)

        print(response)

    ################################################
    # Test: Demonstrate the process of rolling FXFwds
    # We take 3 fx forwards, upsert them as fwd cash transactions in a different base and transaction ccy (to mimick FXFwds)
    # Then price using LUSID and QPS.
    # Then we tearup and book new fx positions.
    # This script uses cocoon for mapping
    def test_FXforward_price_from_portfolio_and_roll(self):


        transactionScope = "Finbourne-Examples"
        transactionPortfolio = "Test16"
        spotGBPEUR = 1.2021
        portfolioRequest = models.CreateTransactionPortfolioRequest(
            display_name="test portfolio",
            code=transactionPortfolio,
            description="to test FX rolls",
            base_currency="GBP",
            created=datetime(2019, 1, 1, tzinfo=pytz.utc)
        )
        try:
            self.transaction_portfolios_api.create_portfolio(transactionScope, portfolioRequest)
        except:
            pass  # will fail on subsequent runs..


        fx_transactions = pd.read_csv('txn.csv')
        fx_transactions["fund_code"] = transactionPortfolio
        sum_units = sum(fx_transactions["txn_units"])
        sum_consideration = sum(fx_transactions["txn_consideration"])
        max_settle = max(fx_transactions["txn_settle_date"])
        txn_ids = fx_transactions.loc[:,"txn_id"]

        mapping = {
            "transactions": {
                "identifier_mapping": {
                    "Instrument/default/Currency": "txn_instrument_id",

                },
                "required": {
                    "code": "fund_code",
                    "transaction_id": "txn_id",
                    "type": "txn_type",
                    "transaction_price.price": "txn_price",
                    "transaction_price.type": "$Price",
                    "total_consideration.amount": "txn_consideration",
                    "units": "txn_units",
                    "transaction_date": "txn_trade_date",
                    "total_consideration.currency": "sm_currency",
                    "settlement_date": "txn_settle_date"
                },
                "optional": {
                    "source": "$lusid_security_services",
                    "exchange_rate": "exchange_rate",
                },
                "properties": [
                    "PortionClass",
                    "PortionSubClass",
                    "PortionRegion",
                ]
            },

        }

        result = lpt.cocoon.load_from_data_frame(
            api_factory=self.api_factory,
            scope=transactionScope,
            data_frame=fx_transactions,
            mapping_required=mapping["transactions"]["required"],
            mapping_optional=mapping["transactions"]["optional"],
            file_type="transactions",
            identifier_mapping=mapping["transactions"]["identifier_mapping"],
            property_columns=mapping["transactions"]["properties"],
            properties_scope=transactionScope
        )

        succ, failed = format_transactions_response(result)
        print(f"number of successful portfolios requests: {len(succ)}")
        print(f"number of failed portfolios requests    : {len(failed)}")



        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        # use the duration of the remaining FX forwards and the total notional to calculate
        # a rough pv01. lets assume a 5bps charge for the tearup
        duration = (datetime.strptime(max_settle,"%d/%m/%Y") - (start_date.replace(tzinfo=None))).days/365.25
        approx_pv01 = sum_units*duration/10000
        charge= 5* approx_pv01
        marketDataScope = "FinbourneMarketData"
        marketSupplier = 'Lusid'

        # We are going to need a market quote for the new role fx forward. Let's save that down so that we can retrieve it later
        # Create a quote for forward FX GBPEUR (saved as a spread, so the forward pips)
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="GBP/EUR",
                    instrument_id_type='CurrencyPair',
                    quote_type='Spread',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=146,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        # There is a saved recipe, accessed via the resource ID that prices using QPS
        # We can access this by switching from inline recipe to recipe ID in the aggrgation request
        ResourceId = models.ResourceId(
            scope='default',
            code='refinitiv-qps'
        )
        # this is the construction of an in-lin recipe
        vendorModel = []

        # vendorModel.append(models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
        #                                           instrument_type="FxForward", parameters="{}"))
        #
        vendorModel.append(models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                                  instrument_type="FxForward", parameters="{}"))

        # vendorModel.append(models.VendorModelRule(supplier="Lusid", model_name="SimpleStatic",
        #                                           instrument_type="FxBuy", parameters="{}"))

        # vendorModel.append(models.VendorModelRule(supplier="Lusid", model_name="SimpleStatic",
        #                                           instrument_type="FxCash", parameters="{}"))

        pricingContext = models.PricingContext(
            options=models.PricingOptions(produce_separate_result_for_linear_otc_legs=True), #,
                                          #model_selection=models.ModelSelection(library="Lusid",model="SimpleStatic")),

            model_rules=vendorModel)

        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))


        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        # Create the aggregation request
        aggregationRequest = models.AggregationRequest(
            inline_recipe=RecipeId,
            #recipe_id=ResourceId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Instrument/default/Name',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ])

        # Call LUSID to perform the aggregation
        response = self.aggregation_api.get_aggregation_by_portfolio(
            scope=transactionScope,
            code=transactionPortfolio,
            request=aggregationRequest)

        aggregateOfForwards =0
        for i in range(len(response.data)):
            aggregateOfForwards += response.data[i]['Holding/default/PV']

        # To tearup the current FX forwards, we need the overall PV, and the charge.
        # The PV is above. A reasonable charge has been calculated as 5bps
        # So we can cancel the current transactions, provided we book a cash receipt of the PV less the charge
        # (assuming the PV is +ve, otherwise its a payment)

        cashPayment  = aggregateOfForwards - charge

        # Cancel transactions - nothing is ever deleted from an immutable system

        response = self.transaction_portfolios_api.cancel_transactions(transactionScope, transactionPortfolio, txn_ids.values.tolist())

        # bring in the second file with the new FX forward and the cash txn. we will need to configure these to reflect the market/calculated values

        fx_new_transactions = pd.read_csv('txn_new.csv', dtype={"txn_units": float,"txn_consideration": float})
        fx_new_transactions["fund_code"] = transactionPortfolio

        # for the  cash payment, we need to adjust the amount. (the csv has a unitised booking)
        # for the new FX forward, we need to set the FX rate from the spot and the forward quote
        # for the notional, we are assuming the EUR amount is unchanged and infering the GBP fwd

        # Retrieve the quote for the new 1yr fwd FX

        fwd_pips = self.quotes_api.get_quotes(
            scope=marketDataScope,
            effective_at=start_date,
            quote_ids={
                'CurrencyPair': models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id='GBP/EUR',
                    instrument_id_type='CurrencyPair',
                    quote_type='Spread',
                    field='mid')
            }).values['CurrencyPair'].metric_value.value

        # The fwd fx and the far GBP leg notional need to be calculated and edited in the file
        # Of course you could just as easily do this in memory

        fwdFX = spotGBPEUR - fwd_pips/10000
        # far GBP leg is the far EUR leg / fwdFX
        farGBPLeg= fx_new_transactions[fx_new_transactions['txn_id']=='trd_FXRoll_01']['txn_consideration'].item() / fwdFX

        fx_new_transactions.loc[fx_new_transactions['txn_id'] == 'trd_FXRoll_01','txn_units']  = farGBPLeg
        fx_new_transactions.loc[fx_new_transactions['txn_id'] == 'trd_FXRoll_01', 'exchange_rate'] = fwdFX
        fx_new_transactions.loc[fx_new_transactions['txn_id'] == 'trd_tearup_01', 'txn_consideration'] = cashPayment


        # Book the new FX forward ( buying GBPEUR for the sum of the EUR position)



        mapping = {
            "transactions": {
                "identifier_mapping": {
                    "Instrument/default/Currency": "txn_instrument_id",

                },
                "required": {
                    "code": "fund_code",
                    "transaction_id": "txn_id",
                    "type": "txn_type",
                    "transaction_price.price": "txn_price",
                    "transaction_price.type": "$Price",
                    "total_consideration.amount": "txn_consideration",
                    "units": "txn_units",
                    "transaction_date": "txn_trade_date",
                    "total_consideration.currency": "sm_currency",
                    "settlement_date": "txn_settle_date"
                },
                "optional": {
                    "source": "$lusid_security_services",
                    "exchange_rate": "exchange_rate",
                },
                "properties": [
                    "PortionClass",
                    "PortionSubClass",
                    "PortionRegion",
                ]
            },

        }

        result = lpt.cocoon.load_from_data_frame(
            api_factory=self.api_factory,
            scope=transactionScope,
            data_frame=fx_new_transactions,
            mapping_required=mapping["transactions"]["required"],
            mapping_optional=mapping["transactions"]["optional"],
            file_type="transactions",
            identifier_mapping=mapping["transactions"]["identifier_mapping"],
            property_columns=mapping["transactions"]["properties"],
            properties_scope=transactionScope
        )

        succ, failed = format_transactions_response(result)
        print(f"number of successful portfolios requests: {len(succ)}")
        print(f"number of failed portfolios requests    : {len(failed)}")

        response = self.transaction_portfolios_api.get_transactions(
            scope=transactionScope,
            code=transactionPortfolio,
            from_transaction_date=start_date)
        # where are my results.....!!

        print(aggregateOfForwards)



    ################################################
    # Test: show a variety of instruments, with a set of recipes to price in different ways
    # Then we show how recipes can supersede each other
    # At first, we will do this in-line, then add the ability to upsert the recipes and instruments/transactions

    def test_recipe_order(self):

        #create a portfolio to book our cash, otc instruments
        transactionScope = "Finbourne-Examples"
        transactionPortfolio = "RecipeTest"

        portfolioRequest = models.CreateTransactionPortfolioRequest(
            display_name="test portfolio",
            code=transactionPortfolio,
            description="to test FX rolls",
            base_currency="GBP",
            created=datetime(2019, 1, 1, tzinfo=pytz.utc)
        )
        try:
            self.transaction_portfolios_api.create_portfolio(transactionScope, portfolioRequest)
        except:
            pass  # will fail on subsequent runs..

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date

        end_date_3y = start_date.replace(year=start_date.year + 3)
        end_date_5y = start_date.replace(year=start_date.year + 5)
        end_date_10y = start_date.replace(year=start_date.year + 10)

        dom_amount = 100000000

        # Use mkt fwd pips to generate fwd FX prices for foreign leg (USD)

        fwd_FX_price_3y = self.start_GBPUSD_FX_price + self.GBPUSDpip_3y / 10000
        fwd_FX_price_5y = self.start_GBPUSD_FX_price + self.GBPUSDpip_5y / 10000
        fwd_FX_price_10y = self.start_GBPUSD_FX_price + self.GBPUSDpip_10y / 10000

        # use foreign fwd FX price to generate foreign cash leg
        fgn_amount_3y = dom_amount * -fwd_FX_price_3y
        fgn_amount_5y = dom_amount * -fwd_FX_price_5y
        fgn_amount_10y = dom_amount * -fwd_FX_price_10y

        #The market data scope refers to the user partition into which market data is stored
        #The supplier denotes the owner of the market data (not the price source)
        #This *must* match the recipe ruleset that is used to retrieve the data or it will not be found.

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for spot FX GBP/USD
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider=marketSupplier,
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=self.start_GBPUSD_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        #create the FX forward instruments

        instrument_definition_3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_3y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=self.start_GBPUSD_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_3y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition_5y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_5y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=self.start_GBPUSD_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_5y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition_10y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_10y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=self.start_GBPUSD_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_10y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        print(response)
        #book these 3 FX fwds
        #
        #
        #
        #

        # create a 'book' of 3 IRS trades
        # to create current cashflow events, we will create swaps starting 3m & 6m ago,
        # so the first fix is happening now
        # swap1 - start - 3m and a day in the past, for 5y (quarterly EURIBOR)
        swap1_start_date = start_date.replace(month=start_date.month -3)
        swap1_start_date = swap1_start_date.replace(day=swap1_start_date.day - 1)
        swap1_end_date = swap1_start_date.replace(year=swap1_start_date.year + 5)

        # swap2 - start - 6m in the past, for 7y
        swap2_start_date = start_date.replace(month=start_date.month - 6)
        swap2_end_date = swap2_start_date.replace(year=swap2_start_date.year + 7)

        # swap3 - start - 12m and a day in the past, for 3y
        swap3_start_date = start_date.replace(year=start_date.year - 12)
        swap3_start_date = swap3_start_date.replace(day=swap3_start_date.day - 2)
        swap3_end_date = swap3_start_date.replace(year=swap3_start_date.year + 3)


        # ccy = EUR
        swapCCY = "EUR"
        dom1 = 75000000
        dom2 = 55000000
        dom3 =125500000
        pay1 = True
        pay2 = False
        pay3 = True
        rate1 =0.01
        rate2 = 0.0125
        rate3 = 0.005


        # create the flow convention for each leg

        flow_conventionFixed = models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=1, unit="Y"),
            day_count_convention="ThirtyU360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )
        flow_conventionFloat_semi = models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6, unit="M"),
            day_count_convention="Act360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )
        flow_conventionFloat_quarterly = models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=3, unit="M"),
            day_count_convention="Act360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )
        # create the swap legs themselves
        instrument_definition_leg1 = models.InstrumentLeg(
            conventions=flow_conventionFixed,
            is_pay_not_receive=pay1,
            is_float_not_fixed=False,
            fixed_rate=rate1
        )
        instrument_definition_leg2 = models.InstrumentLeg(
            conventions=flow_conventionFloat_quarterly,
            is_pay_not_receive=not(pay1),
            is_float_not_fixed=True,
            fixed_rate=0.0
        )
        instrument_definition_leg3 = models.InstrumentLeg(
            conventions=flow_conventionFixed,
            is_pay_not_receive=pay2,
            is_float_not_fixed=False,
            fixed_rate=rate2
        )
        instrument_definition_leg4 = models.InstrumentLeg(
            conventions=flow_conventionFloat_semi,
            is_pay_not_receive=not(pay2),
            is_float_not_fixed=True,
            fixed_rate=0.0
        )
        instrument_definition_leg5 = models.InstrumentLeg(
            conventions=flow_conventionFixed,
            is_pay_not_receive=pay3,
            is_float_not_fixed=False,
            fixed_rate=rate3
        )
        instrument_definition_leg6 = models.InstrumentLeg(
            conventions=flow_conventionFloat_semi,
            is_pay_not_receive=not(pay3),
            is_float_not_fixed=True,
            fixed_rate=0.0
        )
        irs_legs1 = [
            instrument_definition_leg1,
            instrument_definition_leg2
        ]
        irs_legs2 = [
            instrument_definition_leg3,
            instrument_definition_leg4
        ]
        irs_legs3 = [
            instrument_definition_leg5,
            instrument_definition_leg6
        ]

        # create the swaps
        swap1 = models.SwapInstrument(
            start_date=swap1_start_date.isoformat(),
            maturity_date=swap1_end_date.isoformat(),
            notional=dom1,
            legs=irs_legs1,
            is_amortizing=False,
            notional_exchange_type="None",
            instrument_type="InterestRateSwap")
        # 2
        swap2 = models.SwapInstrument(
            start_date=swap2_start_date.isoformat(),
            maturity_date=swap2_end_date.isoformat(),
            notional=dom2,
            legs=irs_legs2,
            is_amortizing=False,
            notional_exchange_type="None",
            instrument_type="InterestRateSwap")
        #3
        swap3 = models.SwapInstrument(
            start_date=swap3_start_date.isoformat(),
            maturity_date=swap3_end_date.isoformat(),
            notional=dom3,
            legs=irs_legs3,
            is_amortizing=False,
            notional_exchange_type="None",
            instrument_type="InterestRateSwap")

        # now we book these swaps into the portfolio

        # create instruments and book a unitised txn (the details are all in the swap inst)


        # when it comes to the recipe, we need something that describes what to do with swaps and FX forwards
        # at first, we'll value with the recipe set to simple static.
        # then we can change to discount and add the VolMaster model just for fx fwds
        # finally we can add XXXX for swaps??



        vendorModelQPs = models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")

        vendorModelTW = models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")

        vendorModelVM = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")


        #next we take the fwd instruments and add them to an inline weighted instrument list for pricing

        weightedInstrumentFXFwd_3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3y",
                                                               instrument=instrument_definition_3y)

        weightedInstrumentFXFwd_5y = models.WeightedInstrument(quantity=1, holding_identifier="myholding5y",
                                                               instrument=instrument_definition_5y)

        weightedInstrumentFXFwd_10y = models.WeightedInstrument(quantity=1, holding_identifier="myholding10y",
                                                                instrument=instrument_definition_10y)

        weightedInstrumentIRS1 = models.WeightedInstrument(quantity=1, holding_identifier="swap1",
                                                           instrument=swap1)

        weightedInstrumentIRS2 = models.WeightedInstrument(quantity=1, holding_identifier="swap2",
                                                           instrument=swap2)

        weightedInstrumentIRS3 = models.WeightedInstrument(quantity=1, holding_identifier="swap3",
                                                           instrument=swap3)


        weightedInstrumentList = [weightedInstrumentFXFwd_3y, weightedInstrumentFXFwd_5y, weightedInstrumentFXFwd_10y,
                                  weightedInstrumentIRS1, weightedInstrumentIRS2, weightedInstrumentIRS3]


        # 1 show the results with a lusid simple static model...will return quotes x q
        # upsert tw recipes, two different scopes
        # inherited recipe section + additional rule
        # 2 upload a cm data doc..show different ccys
        # 3 add in a pricing context for fx fwds...VM?
        # add in something for swaps?


        # to create the recipe, in this case we will need a pricing and a market context.
        # the former attaches the pricing model used and parameters around its usage
        # the latter contains instructions on the market data source and rules

        pricingContext = models.PricingContext(
            options=models.PricingOptions(produce_separate_result_for_linear_otc_legs=False),
            model_rules=[
                models.VendorModelRule(supplier="Lusid", model_name="SimpleStatic", instrument_type="FxForward",
                                       parameters="{}"),
                models.VendorModelRule(supplier="Lusid", model_name="SimpleStatic", instrument_type="InterestRateSwap",
                                       parameters="{}")
            ]
        )
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope),
            market_rules=[
                models.MarketDataKeyRule(key="Fx.*.*", data_scope="some-other-scope", supplier=marketSupplier,
                                         quote_type='Price', field='mid'),
                models.MarketDataKeyRule(key="Fx.*.*", data_scope=marketDataScope, supplier=marketSupplier,
                                         quote_type='Price', field='mid'),
                models.MarketDataKeyRule(key="Rates.*.*", data_scope=marketDataScope, supplier=marketSupplier,
                                         quote_type='Rate', field='mid')
            ]
        )
        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)



        # pricingContext = models.PricingContext(model_rules=[vendorModelVM])
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

        # the recipe then binds together these constituents
        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        pricing_date = trade_date
        # the aggregation is a powerful mechanism for producing a result set, we will show later how the cashflow
        # output can be pushed straight back into the movements engine. It can also persist external results
        # and will shortly combine with Honeycomb for reporting
        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=pricing_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/DomCcy',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/FgnCcy',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/StartDate',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/MaturityDate',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation, print the result

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)

        print(response)



    ################################################
    # Test: create a 5yr CDS on XXXX
    # Maturity 5y, semi bond 6s EUR IRS
    # Test will only show (for now) known (set) cashflows
    # NB there are cash amounts in the slices unlike options, where the cash is unknown
    # and there is nothing in NextEvent, because known cashflows are not regarded as events
    # Models tested - LUSID
    # LUSID aggregation in inline, using weighted instruments which are not persisted
    def test_CDS(self):

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_5y = start_date.replace(year=start_date.year + 5)

        dom_amount = 50000000 #50mil

        #create the flow convention for each leg

        flow_conventionFixed= models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6,unit="M"),
            day_count_convention="ThirtyU360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )
        flow_conventionFloat = models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6, unit="M"),
            day_count_convention="Act360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )

        CDS_detail_spec = models.CdsDetailSpecification(
            seniority="SNR",
            restructuring_type="CR",
            protect_start_day=True,
            pay_accrued_interest_on_default=True,
            roll_frequency=models.Tenor(value=6,unit="M")
        )

        #create the CDS
        instrument_definition_5yEURCDS = models.CdsInstrument(
            ticker="myticker",
            flow_conventions=[flow_conventionFloat,flow_conventionFixed],
            coupon_rate=0.01,
            detail_specification=CDS_detail_spec,
            start_date=start_date.isoformat(),
            maturity_date=end_date_5y.isoformat(),
            dom_ccy="EUR",
            instrument_type="CreditDefaultSwap")



        pricingContext = models.PricingContext(
            options=models.PricingOptions(
                allow_any_instruments_with_sec_uid_to_price_off_lookup=True,
                allow_partially_successful_evaluation=True
            ),
        )

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext)  # , market=marketContext)

        weightedInstrument_5yEURCDS = models.WeightedInstrument(quantity=1, holding_identifier="myholding_5yEURCDS",
                                                                 instrument=instrument_definition_5yEURCDS)
        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEvent',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEventType',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/HoldingCashflows',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=[weightedInstrument_5yEURCDS])

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)

        print(response)



    ################################################
    # Test: Show 10yr IRS cashflows
    # Maturity 10y, semi bond 6s EUR IRS
    # Test will only show (for now) known (set) cashflows
    # NB there are cash amounts in the slices unlike options, where the cash is unknown
    # and there is nothing in NextEvent, because known cashflows are not regarded as events
    # Models tested - LUSID
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_SWOPT_expiry_and_exercise(self):

        marketDataScope = "MarketDataDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_10y = start_date.replace(year=start_date.year + 10)

        swapCCY = "EUR"

        dom_amount = 75000000

        #create the flow convention for each leg

        flow_conventionFixed= models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6,unit="M"),
            day_count_convention="ThirtyU360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )
        flow_conventionFloat = models.FlowConventions(
            currency="EUR",
            payment_frequency=models.Tenor(value=6, unit="M"),
            day_count_convention="Act360",
            roll_convention="ModifiedFollowing",
            holiday_calendars=[]
        )

        # create the swap legs themselves

        #irs_legs=[]
        instrument_definition_leg1 = models.InstrumentLeg(
            conventions=flow_conventionFixed,
            is_pay_not_receive=True,
            is_float_not_fixed=False,
            fixed_rate=0.01
        )
        instrument_definition_leg2 = models.InstrumentLeg(
            conventions=flow_conventionFloat,
            is_pay_not_receive=False,
            is_float_not_fixed=True,
            fixed_rate=0.0
        )
        irs_legs = [
            instrument_definition_leg1,
            instrument_definition_leg2
        ]

        #create the swap
        instrument_definition_10yEURIRS = models.SwapInstrument(
            start_date=start_date.isoformat(),
            maturity_date=end_date_10y.isoformat(),
            notional=dom_amount,
            legs=irs_legs,
            is_amortizing=False,
            notional_exchange_type="None",
            instrument_type="InterestRateSwap")


        swopt_inst_def = models


        pricingContext = models.PricingContext(
            options=models.PricingOptions(
                allow_any_instruments_with_sec_uid_to_price_off_lookup=True,
                allow_partially_successful_evaluation=True
            ),
        )

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext)  # , market=marketContext)

        weightedInstrument_10yEURIRS = models.WeightedInstrument(quantity=1, holding_identifier="myholding_10yEURIRS",
                                                                 instrument=instrument_definition_10yEURIRS)
        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEvent',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/NextEventType',
                                     op='Value'),
                models.AggregateSpec(key='Analytic/default/HoldingCashflows',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=[weightedInstrument_10yEURIRS])

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)

        print(response)






