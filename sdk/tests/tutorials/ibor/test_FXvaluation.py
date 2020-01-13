import unittest
from datetime import datetime

import pytz

import lusid
import lusid.models as models
from utilities import InstrumentLoader
from utilities import TestDataUtilities
import json


class Valuation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create a configured API client
        api_client = TestDataUtilities.api_client()

        cls.transaction_portfolios_api = lusid.TransactionPortfoliosApi(api_client)
        cls.instruments_api = lusid.InstrumentsApi(api_client)
        cls.aggregation_api = lusid.AggregationApi(api_client)
        cls.quotes_api = lusid.QuotesApi(api_client)
        cls.SMD_api = lusid.StructuredMarketDataApi(api_client)
        instrument_loader = InstrumentLoader(cls.instruments_api)
        cls.instrument_ids = instrument_loader.load_instruments()

        cls.test_data_utilities = TestDataUtilities(cls.transaction_portfolios_api)

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
    def test_FX_FWD_aggregation_inline_weighted(self):
        #price simple fx fwds..demonstrate sensible PV.
        #can update dates etc
        trade_date = datetime(2020, 1, 9, tzinfo=pytz.utc)    #change to today?
        start_date = datetime(2020, 1, 11, tzinfo=pytz.utc)    #change to spot?
        end_date3y = datetime(2023, 1, 11, tzinfo=pytz.utc)    #3yr
        end_date5y = datetime(2025, 1, 11, tzinfo=pytz.utc)    #5yr
        end_date10y = datetime(2030, 1, 11, tzinfo=pytz.utc)    #10yr

        dom_amount = 100000000
        fgn_amount_3y = -133900000
        fgn_amount_5y = -135680000
        fgn_amount_10y = -141750000
        start_FX_price = 1.2975


        #The market data scope and supplier refer to the user 'scope' into which market data is stored and the supplier
        #or owner of that data (not the source of it) respectively.
        #This *must* match the rule that is used to retrieve it or it will not be found.

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'



        # Create a quote for the FX GBP/USD for 21/11/19
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='marketSupplier',
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=start_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_3y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date3y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition5y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_5y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date5y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition10y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_10y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date10y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        print(response)

        #vendorModel = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
        #                                     instrument_type="FxForward", parameters="{}")

        vendorModel = models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")

        pricingContext = models.PricingContext(model_rules=[vendorModel])
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXFwd_3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3y",
                                                            instrument=instrument_definition3y)

        weightedInstrumentFXFwd_5y = models.WeightedInstrument(quantity=1, holding_identifier="myholding5y",
                                                              instrument=instrument_definition5y)

        weightedInstrumentFXFwd_10y = models.WeightedInstrument(quantity=1, holding_identifier="myholding10y",
                                                              instrument=instrument_definition10y)

        weightedInstrumentList = [weightedInstrumentFXFwd_3y, weightedInstrumentFXFwd_5y, weightedInstrumentFXFwd_10y]

        aggregationRequestResource = models.AggregationRequest(
            # recipe_id=ResourceId,
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
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

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)
        print(response.data[0])
        print(response)

        print(response)

    ####################################################
    def test_FX_OPT_aggregation_inline_weighted(self):
        #price simple fx opts..demonstrate sensible pvs.
        #can update dates etc
        trade_date = datetime(2019, 11, 19, tzinfo=pytz.utc)    #change to today?
        start_date = datetime(2019, 11, 21, tzinfo=pytz.utc)    #change to spot?
        end_date_1y = datetime(2020, 11, 21, tzinfo=pytz.utc)    #1yr
        end_date_2y = datetime(2021, 11, 21, tzinfo=pytz.utc)    #2yr
        end_date_3y = datetime(2022, 11, 21, tzinfo=pytz.utc)    #3yr

        dom_amount = 100000000
        fgn_amount_1y = -131175000
        fgn_amount_2y = -132350000
        fgn_amount_3y = -133900000
        #Use mkt fwd to generate close to 0 PV? or use 5y and have over and under
        start_FX_price = 1.2975
        fwd_FX_price_1y = 1.31175
        fwd_FX_price_2y = 1.3235
        fwd_FX_price_3y = 1.339
        '''
            The market data scope and supplier refer to (effectively) two fields in the database that describe who 'supplied' the data 
            and the user 'scope' into which it is put. This *must* match the rule that is used to retrieve it or it simply will not be found. 
        '''
        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for the FX GBP/USD for 21/11/19
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='marketSupplier',
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=start_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition_1y = models.FxOption(
            start_date=start_date.isoformat(),
            option_maturity_date=end_date_1y.isoformat(),
            option_settlement_date=start_date.isoformat(),
            is_delivery_not_cash=False,
            is_call_not_put=True,
            strike=fwd_FX_price_1y,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption"
            )

        instrument_definition_2y = models.FxOption(
            start_date=start_date.isoformat(),
            option_maturity_date=end_date_2y.isoformat(),
            option_settlement_date=start_date.isoformat(),
            is_delivery_not_cash=False,
            is_call_not_put=True,
            strike=fwd_FX_price_2y,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption"
            )

        instrument_definition_3y = models.FxOption(
            start_date=start_date.isoformat(),
            option_maturity_date=end_date_3y.isoformat(),
            option_settlement_date=start_date.isoformat(),
            is_delivery_not_cash=False,
            is_call_not_put=True,
            strike=fwd_FX_price_3y,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption"
            )


        print(response)

        vendorModel = models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxOption", parameters="{}")

        pricingContext = models.PricingContext(model_rules=[vendorModel])
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXOpt_1y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding1y",
            instrument=instrument_definition_1y
        )
        weightedInstrumentFXOpt_2y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding2y",
            instrument=instrument_definition_2y
        )
        weightedInstrumentFXOpt_3y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding3y",
            instrument=instrument_definition_3y
        )


        weightedInstrumentList = [weightedInstrumentFXOpt_1y, weightedInstrumentFXOpt_2y, weightedInstrumentFXOpt_3y]

        aggregationRequestResource = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
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
                                     op='Value')
                #models.AggregateSpec(key='Analytic/default/MaturityDate',
                #                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)
        print(response.data[0])
        print(response)

        print(response)


    ################################################
    def test_FX_FWD_CUTDOWN_aggregation_inline_weighted(self):
        # price simple fx fwds..demonstrate sensible PV.
        # can update dates etc
        trade_date = datetime(2020, 1, 9, tzinfo=pytz.utc)  # change to today?
        start_date = datetime(2020, 1, 11, tzinfo=pytz.utc)  # change to spot?
        end_date5y = datetime(2025, 1, 11, tzinfo=pytz.utc)  # 5yr

        dom_amount = 100000000
        fgn_amount_5y = dom_amount *-98.7
        start_FX_price = 109.935

        # The market data scope and supplier refer to the user 'scope' into which market data is stored and the supplier
        # or owner of that data (not the source of it) respectively.
        # This *must* match the rule that is used to retrieve it or it will not be found.

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for the FX GBP/USD for 21/11/19
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='marketSupplier',
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=start_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition5y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_5y,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date5y.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")


        print(response)

        # vendorModel = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
        #                                     instrument_type="FxForward", parameters="{}")

        vendorModel = models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")

        pricingContext = models.PricingContext(model_rules=[vendorModel])
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXFwd_5y = models.WeightedInstrument(quantity=1, holding_identifier="myholding5y",
                                                               instrument=instrument_definition5y)

        weightedInstrumentList = [weightedInstrumentFXFwd_5y]

        aggregationRequestResource = models.AggregationRequest(
            # recipe_id=ResourceId,
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
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

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)
        print(response.data[0])
        print(response)

        print(response)

    ################################################
    #no plans to use this in demo
    def test_FX_FWD_portfolio_aggregation(self):

        #not going to demo this until swagger 3

        #price simple fx fwds..demonstrate sensible PV.
        #can update dates etc
        trade_date = datetime(2020, 1, 9, tzinfo=pytz.utc)    #change to today?
        start_date = datetime(2020, 1, 11, tzinfo=pytz.utc)    #change to spot?
        end_date3y = datetime(2023, 1, 11, tzinfo=pytz.utc)    #3yr
        end_date5y = datetime(2025, 1, 11, tzinfo=pytz.utc)    #5yr
        end_date10y = datetime(2030, 1, 11, tzinfo=pytz.utc)    #10yr

        dom_amount = 100000000
        fgn_amount = -136035000                                 #Use mkt fwd to generate close to 0 PV? or use 5y and have over and under
        start_FX_price = 1.30485


        '''
            The market data scope and supplier refer to (effectively) two fields in the database that describe who 'supplied' the data 
            and the user 'scope' into which it is put. This *must* match the rule that is used to retrieve it or it simply will not be found. 
        '''
        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'



        # Create a quote for the FX GBP/USD for 21/11/19
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='marketSupplier',
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=start_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition3y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date3y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition5y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date5y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition10y = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date10y.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")



        weightedInstrumentFXFwd3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3y",
                                                            instrument=instrument_definition3y)

        weightedInstrumentFXFwd5y = models.WeightedInstrument(quantity=1, holding_identifier="myholding5y",
                                                              instrument=instrument_definition5y)

        weightedInstrumentFXFwd10y = models.WeightedInstrument(quantity=1, holding_identifier="myholding10y",
                                                              instrument=instrument_definition10y)

        weightedInstrumentList = [weightedInstrumentFXFwd3y, weightedInstrumentFXFwd5y, weightedInstrumentFXFwd10y]



        # Create the aggregation request
        aggregationRequest = models.AggregationRequest(
            # inline_recipe=inline_recipe,
            recipe_id=ResourceId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ])

        # Call LUSID to perform the aggregation
        response = self.aggregation_api.get_aggregation_by_portfolio(
            scope=scope,
            code=portfolio,
            request=aggregationRequest)

        print(response)


    def test_FX_aggregation_all_options(self):

        trade_date = datetime(2019, 11, 19, tzinfo=pytz.utc)
        start_date = datetime(2019, 11, 21, tzinfo=pytz.utc)
        end_date = datetime(2024, 11, 21, tzinfo=pytz.utc)
        dom_amount = 100000000
        fgn_amount = -133650000
        start_FX_price = 1.289
        optionMatDate = end_date = datetime(2020, 5, 21, tzinfo=pytz.utc)
        # start_date = datetime(2019, 11, 21, tzinfo=pytz.utc)
        # end_date = datetime(2019, 11, 22, tzinfo=pytz.utc)
        # dom_amount = 1000
        # fgn_amount = -1291.5

        scope = "TRRiskDomain"
        portfolio = "FXFwd1GBP"

        # Create a quote for the FX GBP/USD for 21/11/19
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='Lusid',
                    instrument_id="GBP/USD",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=start_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=scope,
            quotes={"1":FX_quote})




        instrument_definition1 = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="USD",
            ref_spot_rate=1.2915,
            start_date=start_date.isoformat(),
            maturity_date=end_date.isoformat(),
            dom_ccy="GBP",
            instrument_type="FxForward")

        instrument_definition2 = models.FxOption(
            start_date=start_date,
            option_maturity_date=optionMatDate,
            option_settlement_date=start_date,
            is_delivery_not_cash=False,
            is_call_not_put=True,
            strike=100,
            dom_ccy="GBP",
            fgn_ccy="USD",
            instrument_type="FxOption")




        #instrument_definition3 = models.LusidInstrument(instrument_type="FxForward")
        #print(json.dumps(instrument_definition3.__dict__))
        FX_FWD_details = {
            "domAmount": 100000000,
            "domCcy": 'GBP',
            "fgnAmount": -128863000,
            "fgnCcy": 'USD',
            "fixingDate": start_date.isoformat(),
            "instrumentType": "FxForward",
            "isNdf": False,
            "maturityDate": end_date.isoformat(),
            "refSpotRate": 1.28863,
            "startDate": start_date.isoformat()
        }

        # Create the definition for your instrument, attaching the bespoke contract
        FX_FWD_instrument = models.InstrumentDefinition(
            name='FXFWD1',
            identifiers={
                'ClientInternal': models.InstrumentIdValue(
                    value="FXFWD0001", effective_at=start_date.isoformat())},
            definition=models.InstrumentEconomicDefinition(
                instrument_format='Lusid',
                content=json.dumps(FX_FWD_details)
            )
        )

        print(json.dumps(FX_FWD_details))

        response = self.instruments_api.upsert_instruments(
            instruments={"FXsomething": FX_FWD_instrument})

        FX_FWD_details = {
            "domAmount": 50000000,
            "domCcy": 'GBP',
            "fgnAmount": -64431500,
            "fgnCcy": 'USD',
            "fixingDate": start_date.isoformat(),
            "instrumentType": "FxForward",
            "isNdf": False,
            "maturityDate": end_date.isoformat(),
            "refSpotRate": 1.28863,
            "startDate": start_date.isoformat()
        }

        # Create the definition for your instrument, attaching the bespoke contract
        FX_FWD_instrument = models.InstrumentDefinition(
            name='FXFWD2',
            identifiers={
                'ClientInternal': models.InstrumentIdValue(
                    value="FXFWD0002")},
            definition=models.InstrumentEconomicDefinition(
                instrument_format='Lusid',
                content=json.dumps(FX_FWD_details)
            )
        )

        print(json.dumps(FX_FWD_details))

        response = self.instruments_api.upsert_instruments(
            instruments={"FXsomething1": FX_FWD_instrument})

        self.assertEqual(len(response.values), 1, response.failed)

        # Initialse a list to hold the hedging transaction
        hedge_transactions = []
        # Build and add the hedge transaction for this currency to the list of transactions
        hedge_transactions.append(
            models.TransactionRequest(
                transaction_id="TXNFXFWD0001",
                type='Buy',
                instrument_identifiers={
                    'Instrument/default/ClientInternal': "FXFWD0001"},
                transaction_date=trade_date.isoformat(),
                settlement_date=start_date.isoformat(),
                units=1,
                transaction_price=models.TransactionPrice(
                    price=0,
                    type='Price'),
                total_consideration=models.CurrencyAndAmount(
                    amount=0,
                    currency="GBP"),
                transaction_currency='GBP',
                source='Client',
            )
        )
        hedge_transactions.append(
            models.TransactionRequest(
                transaction_id="TXNFXFWD0002",
                type='Buy',
                instrument_identifiers={
                    'Instrument/default/ClientInternal': "FXFWD0002"},
                transaction_date=trade_date.isoformat(),
                settlement_date=start_date.isoformat(),
                units=1,
                transaction_price=models.TransactionPrice(
                    price=0,
                    type='Price'),
                total_consideration=models.CurrencyAndAmount(
                    amount=0,
                    currency="GBP"),
                transaction_currency='GBP',
                source='Client',
            )
        )
        # Upsert the transaction into LUSID
        response = self.transaction_portfolios_api.upsert_transactions(
            scope=scope,
            code=portfolio,
            transactions=hedge_transactions
        )
        print(response)
        # recipeId = models.ResourceId(scope=scope,code=portfolio)
        ResourceId = models.ResourceId(
            scope='default',
            code='refinitiv-qps'
        )

        vendorModel = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault", instrument_type="FxOption", parameters="{}")
        pricingContext = models.PricingContext(model_rules=[vendorModel])
        RecipeId = models.ConfigurationRecipe(code="volmaster",pricing=pricingContext)

        weightedInstrumentFXFwd = models.WeightedInstrument(quantity=1, holding_identifier="myholding",
                                                       instrument=instrument_definition1)

        weightedInstrumentFXOpt = models.WeightedInstrument(quantity=1, holding_identifier="myholding",
                                                       instrument=instrument_definition2)

        aggregationRequestResource = models.AggregationRequest(
            # recipe_id=ResourceId,
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ]
        )
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource, instruments=[weightedInstrumentFXFwd])

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(scope, inline_request=inlineRequestFXFwd)
        print(response.data[0])
        print(response)

        aggregationRequestInLine = models.AggregationRequest(
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ]
        )
        inlineRequestFXOpt = models.InlineAggregationRequest(request=aggregationRequestInLine,
                                                             instruments=[weightedInstrumentFXOpt])

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(scope,
                                                                                inline_request=inlineRequestFXOpt)
        print(response.data[0])
        print(response)


        # Create the aggregation request
        aggregationRequest = models.AggregationRequest(
            # inline_recipe=inline_recipe,
            recipe_id=ResourceId,
            effective_at=start_date.isoformat(),
            metrics=[
                models.AggregateSpec(key='Analytic/default/ValuationDate',
                                     op='Value'),
                models.AggregateSpec(key='Holding/default/PV',
                                     op='Value')
            ])

        # Call LUSID to perform the aggregation
        response = self.aggregation_api.get_aggregation_by_portfolio(
            scope=scope,
            code=portfolio,
            request=aggregationRequest)

        print(response)

    def test_delta(self):


        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'


        SMD_JPY_curve = models.StructuredMarketData(
            {"LusidInstrumentSet": {
                "instruments": {
                    "instrument": [
                        {
                            "-type": "fra",
                            "ccy": "JPY",
                            "startTenor": "0M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                                }
                            },
                        {
                            "-type": "fra",
                            "ccy": "JPY",
                            "startTenor": "3M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                                }
                            },
                        {
                            "-type": "fra",
                            "ccy": "JPY",
                            "startTenor": "6M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                                }
                            },
                        {
                            "-type": "fra",
                            "ccy": "JPY",
                            "startTenor": "9M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                                }
                            }
                        ]
                    }
                }
                })

        SMD_USD_curve = models.StructuredMarketData(
            {"LusidInstrumentSet": {
                "instruments": {
                    "instrument": [
                        {
                            "-type": "fra",
                            "ccy": "USD",
                            "startTenor": "0M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                            }
                        },
                        {
                            "-type": "fra",
                            "ccy": "USD",
                            "startTenor": "3M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                            }
                        },
                        {
                            "-type": "fra",
                            "ccy": "USD",
                            "startTenor": "6M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                            }
                        },
                        {
                            "-type": "fra",
                            "ccy": "USD",
                            "startTenor": "9M",
                            "fraTenor": "3M",
                            "quote": {
                                "-type": "rate",
                                "#text": "0.01"
                            }
                        }
                    ]
                }
            }
            })

        SMDquote1 = models.UpsertStructuredMarketDataRequest(
            market_data_id="SMD_id_1",
            market_data=SMD_JPY_curve
        )
        SMDquote2 = models.UpsertStructuredMarketDataRequest(
            market_data_id="SMD_id_2",
            market_data=SMD_USD_curve
        )

        # Call LUSID to upsert structured market data
        response = self.SMD_api.upsert_structured_market_data(
            scope=marketDataScope,
            structured_data={"1": SMDquote1, "2": SMDquote2}
        )

        trade_date = datetime(2020, 1, 9, tzinfo=pytz.utc)  # change to today?
        start_date = datetime(2020, 1, 11, tzinfo=pytz.utc)  # change to spot?
        end_date_6m = datetime(2020, 7, 11, tzinfo=pytz.utc)  # 3yr

        dom_amount = 100000000
        fgn_amount_6m = dom_amount * -108.835
        start_FX_price = 109.943

        # Create a quote for the FX GBP/USD for 21/11/19
        FX_quote = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='marketSupplier',
                    instrument_id="USD/JPY",
                    instrument_id_type='CurrencyPair',
                    quote_type='Price',
                    field='mid'),
                effective_at=start_date,
            ),
            metric_value=models.MetricValue(
                value=start_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

        instrument_definition_6m = models.FxForwardInstrument(
            dom_amount=dom_amount,
            fgn_amount=-fgn_amount_6m,
            is_ndf=False,
            fixing_date=trade_date.isoformat(),
            fgn_ccy="JPY",
            ref_spot_rate=start_FX_price,
            start_date=start_date.isoformat(),
            maturity_date=end_date_6m.isoformat(),
            dom_ccy="USD",
            instrument_type="FxForward")

        print(response)

        vendorModel = models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")

        pricingContext = models.PricingContext(model_rules=[vendorModel])
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXFwd_6m = models.WeightedInstrument(quantity=1, holding_identifier="myholding6m",
                                                               instrument=instrument_definition_6m)

        weightedInstrumentList = [weightedInstrumentFXFwd_6m]

        aggregationRequestResource = models.AggregationRequest(
            # recipe_id=ResourceId,
            inline_recipe=RecipeId,
            effective_at=start_date.isoformat(),
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

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)
        print(response.data[0])
        print(response)

        print(response)