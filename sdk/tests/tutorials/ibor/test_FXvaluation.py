import unittest
from datetime import datetime

import pytz

import lusid
import lusid.models as models
from utilities import TestDataUtilities
from collections import defaultdict
import json
#from xml.etree import ElementTree
import xml.dom.minidom

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
        cls.start_GBPUSD_FX_price = 1.305700
        cls.start_USDJPY_FX_price = 109.021
        cls.GBPUSDpip_1y = 149
        cls.GBPUSDpip_2y = 273
        cls.GBPUSDpip_3y = 392
        cls.GBPUSDpip_5y = 621
        cls.GBPUSDpip_10y = 1200
        cls.USDJPYpip_6m = 106.7


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
    # Test: FXFwds
    # Maturities are 3, 5, and 10 years
    # GBPUSD FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EGBPUSD/forward-rates
    # Which are a rough market mid
    # Spot FX is global, taken from the same site
    # Models tested/compared are QPS, Tracs and VolMaster
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FX_FWD(self):

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date  # change to spot?

        end_date_3y = start_date.replace(year=start_date.year + 3)
        end_date_5y = start_date.replace(year=start_date.year + 5)
        end_date_10y = start_date.replace(year=start_date.year + 10)

        dom_amount = 100000000
        # Use mkt fwd to generate close to 0 PV? or use 5y and have over and under

        fwd_FX_price_3y = self.start_GBPUSD_FX_price + self.GBPUSDpip_3y / 10000
        fwd_FX_price_5y = self.start_GBPUSD_FX_price + self.GBPUSDpip_5y / 10000
        fwd_FX_price_10y = self.start_GBPUSD_FX_price + self.GBPUSDpip_10y / 10000

        fgn_amount_3y = dom_amount * -fwd_FX_price_3y
        fgn_amount_5y = dom_amount * -fwd_FX_price_5y
        fgn_amount_10y = dom_amount * -fwd_FX_price_10y

         #The market data scope and supplier refer to the user 'scope' into which market data is stored and the supplier
        #or owner of that data (not the source of it) respectively.
        #This *must* match the rule that is used to retrieve it or it will not be found.

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for the FX GBP/USD for today
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
                value=self.start_GBPUSD_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

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

        vendorModel=[]

        vendorModel.append(models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        weightedInstrumentFXFwd_3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3y",
                                                            instrument=instrument_definition_3y)

        weightedInstrumentFXFwd_5y = models.WeightedInstrument(quantity=1, holding_identifier="myholding5y",
                                                              instrument=instrument_definition_5y)

        weightedInstrumentFXFwd_10y = models.WeightedInstrument(quantity=1, holding_identifier="myholding10y",
                                                              instrument=instrument_definition_10y)

        weightedInstrumentList = [weightedInstrumentFXFwd_3y, weightedInstrumentFXFwd_5y, weightedInstrumentFXFwd_10y]


        for model in vendorModel:
            pricingContext = models.PricingContext(model_rules=[model])
            marketContext = models.MarketContext(
                options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

            RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)



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

            print(response)

    ################################################
    # Test: FXOptions
    # Maturities are 1, 2, and 3 years
    # GBPUSD FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EGBPUSD/forward-rates
    # Which are a rough market mid
    # Spot FX is global, taken from the same site
    # Strike is set as the fwd FX level to approximate ATM
    # Models tested/compared are QPS, Tracs and VolMaster
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

        vendorModel.append(models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                                  instrument_type="FxOption", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
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
    # Test: Show bump and value delta with a series of 3 FXFwds
    # Maturities are 1, 2, and 3 years
    # USDJPY FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EUSDJPY/forward-rates
    # Which are a rough market mid
    # Spot FX is global, taken from the same site
    # Strike is set as the fwd FX level to approximate ATM
    # Models tested - LUSID
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_delta_lusid(self):
        # A test that demonstrates how to
        #(1) Upload sample complex market data to Lusid, namely a pair of curves
        #(2) Define an fx-forward instrument
        #(3) Call Lusid to evaluate the Fx-Forward PV and its rates delta

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_2m = start_date.replace(month=start_date.month + 2)
        end_date_4m = start_date.replace(month=start_date.month + 4)
        end_date_6m = start_date.replace(month=start_date.month + 6)

        ccyList=['USD', 'JPY']

        response = self.create_structure_market_data(ccyList,effectiveAt, marketDataScope)

        dom_amount = 100000000
        fgn_amount_6m = dom_amount * -(self.start_USDJPY_FX_price - self.USDJPYpip_6m/100)


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

        weightedInstrumentFXFwd_6m = models.WeightedInstrument(quantity=1, holding_identifier="myholding6m",
                                                               instrument=instrument_definition_6m)

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
    # Test: Show option expiry ladder with a series of 10 FXFwds
    # Maturities are in the next few days
    # USDJPY FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EUSDJPY/forward-rates
    # Which are a rough market mid
    # Spot FX is global, taken from the same site
    # Strike is set as the fwd FX level to approximate ATM
    # Models tested - LUSID
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FXOption_expiry_schedule(self):

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date
        effectiveAt = start_date

        end_date_1d = start_date.replace(day=start_date.day + 1)
        end_date_2d = start_date.replace(day=start_date.day + 2)
        end_date_3d = start_date.replace(day=start_date.day + 3)

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
            #options=models.PricingOptions(allowAnyInstrumentsWithSecUidToPriceOffLookup=True),
            model_choice="SimpleStatic",
            model_rules=[
                models.VendorModelRule(supplier="Lusid", model_name="Discounting", instrument_type="FxOption",
                                       parameters="{}")
            ]
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
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=weightedInstrumentList)

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                inline_request=inlineRequestFXFwd)

        cf2=defaultdict(float)

        for i in response.data:
            (dt,dtv) = next(iter(i['Analytic/default/HoldingCashflows']['slices']['USD']['labelsY'].items()))
            (cash,v2) = next(iter(i['Analytic/default/HoldingCashflows']['slices']['USD']['values'].items()))
            cf2[dt] += v2
        print(cf2)



    ################################################
    # Test: Single FXFwd - can we show bi-temporal changes? unlikely given everything is in-line
    # Maturities are 3, 5, and 10 years
    # GBPUSD FX fwds, with pips taken from https://www.barchart.com/forex/quotes/%5EGBPUSD/forward-rates
    # Which are a rough market mid
    # Spot FX is global, taken from the same site
    # Models tested/compared are QPS, Tracs and VolMaster
    # LUSID aggregation in inline, using weighted instruments which are not persisted

    def test_FX_FWD_single_bi_temp(self):

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date  # change to spot?

        end_date_3y = start_date.replace(year=start_date.year + 3)
        end_date_5y = start_date.replace(year=start_date.year + 5)
        end_date_10y = start_date.replace(year=start_date.year + 10)

        dom_amount = 100000000
        # Use mkt fwd to generate close to 0 PV? or use 5y and have over and under

        fwd_FX_price_3y = self.start_GBPUSD_FX_price + self.GBPUSDpip_3y / 10000

        fgn_amount_3y = dom_amount * -fwd_FX_price_3y

         #The market data scope and supplier refer to the user 'scope' into which market data is stored and the supplier
        #or owner of that data (not the source of it) respectively.
        #This *must* match the rule that is used to retrieve it or it will not be found.

        marketDataScope = "TRRiskDomain"
        marketSupplier = 'Lusid'

        # Create a quote for the FX GBP/USD for today
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
                value=self.start_GBPUSD_FX_price,
                unit='rate'),
            lineage='InternalSystem')

        # Call LUSID to upsert the quote
        response = self.quotes_api.upsert_quotes(
            scope=marketDataScope,
            quotes={"1": FX_quote})

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

        print(response)

        vendorModel=[]

        vendorModel.append(models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        vendorModel.append(models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}"))

        weightedInstrumentFXFwd_3y = models.WeightedInstrument(quantity=1, holding_identifier="myholding3y",
                                                            instrument=instrument_definition_3y)

        weightedInstrumentList = [weightedInstrumentFXFwd_3y] #, weightedInstrumentFXFwd_5y, weightedInstrumentFXFwd_10y]


        for model in vendorModel:
            pricingContext = models.PricingContext(model_rules=[model])
            marketContext = models.MarketContext(
                options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

            RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

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

            print(response)


    def test_FX_FWD_aggregation_inline_weightedVM(self):
        # price simple fx fwd..demonstrate sensible pvs.
        # can update dates etc
        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date  # change to spot?

        end_date_3y = start_date.replace(year=start_date.year + 3)
        end_date_5y = start_date.replace(year=start_date.year + 5)
        end_date_10y = start_date.replace(year=start_date.year + 10)

        dom_amount = 100000000
        # Use mkt fwd to generate close to 0 PV? or use 5y and have over and under

        fwd_FX_price_3y = self.start_GBPUSD_FX_price + self.GBPUSDpip_3y / 10000
        fwd_FX_price_5y = self.start_GBPUSD_FX_price + self.GBPUSDpip_5y / 10000
        fwd_FX_price_10y = self.start_GBPUSD_FX_price + self.GBPUSDpip_10y / 10000

        fgn_amount_3y = dom_amount * -fwd_FX_price_3y
        fgn_amount_5y = dom_amount * -fwd_FX_price_5y
        fgn_amount_10y = dom_amount * -fwd_FX_price_10y

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



        vendorModel = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                             instrument_type="FxForward", parameters="{}")

        pricingContext = models.PricingContext(model_rules=[vendorModel])
        marketContext = models.MarketContext(
            options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

        RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

        weightedInstrumentFXFwd_3y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding3y",
            instrument=instrument_definition_3y
        )
        weightedInstrumentFXFwd_5y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding5y",
            instrument=instrument_definition_5y
        )
        weightedInstrumentFXFwd_10y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding10y",
            instrument=instrument_definition_10y
        )

        weightedInstrumentList = [weightedInstrumentFXFwd_3y, weightedInstrumentFXFwd_5y, weightedInstrumentFXFwd_10y]

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

        print(response)

    ################################################
    def test_FX_FWD_CUTDOWN_aggregation_inline_weighted(self):
        # price simple fx fwds..demonstrate sensible PV.
        # can update dates etc
        trade_date = datetime(2020, 1, 9, tzinfo=pytz.utc)  # change to today?
        start_date = datetime(2020, 1, 11, tzinfo=pytz.utc)  # change to spot?
        end_date5y = datetime(2025, 1, 11, tzinfo=pytz.utc)  # 5yr

        dom_amount = 100000000
        fgn_amount_5y = dom_amount * -98.7
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
    # no plans to use this in demo
    def test_FX_FWD_portfolio_aggregation(self):
        # not going to demo this until swagger 3

        # price simple fx fwds..demonstrate sensible PV.
        # can update dates etc
        trade_date = datetime(2020, 1, 9, tzinfo=pytz.utc)  # change to today?
        start_date = datetime(2020, 1, 11, tzinfo=pytz.utc)  # change to spot?
        end_date3y = datetime(2023, 1, 11, tzinfo=pytz.utc)  # 3yr
        end_date5y = datetime(2025, 1, 11, tzinfo=pytz.utc)  # 5yr
        end_date10y = datetime(2030, 1, 11, tzinfo=pytz.utc)  # 10yr

        dom_amount = 100000000
        fgn_amount = -136035000  # Use mkt fwd to generate close to 0 PV? or use 5y and have over and under
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
            quotes={"1": FX_quote})

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

        # instrument_definition3 = models.LusidInstrument(instrument_type="FxForward")
        # print(json.dumps(instrument_definition3.__dict__))
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

        vendorModel = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                             instrument_type="FxOption", parameters="{}")
        pricingContext = models.PricingContext(model_rules=[vendorModel])
        RecipeId = models.ConfigurationRecipe(code="volmaster", pricing=pricingContext)

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
        inlineRequestFXFwd = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                             instruments=[weightedInstrumentFXFwd])

        # Call LUSID to perform the aggregation

        response = self.aggregation_api.get_aggregation_of_weighted_instruments(scope,
                                                                                inline_request=inlineRequestFXFwd)
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

    ####################################################
    def test_FX_OPT_aggregation_inline_weighted_LUSID_event_retrieval(self):
        # price simple fx opts..demonstrate sensible pvs.
        # can update dates etc
        trade_date = datetime.today().replace(tzinfo=pytz.utc)  # change to today for VolMaster
        start_date = trade_date  # change to spot?

        end_date_1y = start_date.replace(year=start_date.year + 1)  # 1yr
        end_date_2y = start_date.replace(year=start_date.year + 2)  # 2yr
        end_date_3y = start_date.replace(year=start_date.year + 3)  # 3yr

        dom_amount = 100000000
        fgn_amount_1y = -131175000
        fgn_amount_2y = -132350000
        fgn_amount_3y = -133900000
        # Use mkt fwd to generate close to 0 PV? or use 5y and have over and under
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
                    provider=marketSupplier,
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

        vendorModelQPS = models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                                instrument_type="FxOption", parameters="{}")

        vendorModelTracs = models.VendorModelRule(supplier="RefinitivTracsWeb", model_name="VendorDefault",
                                                  instrument_type="FxOption", parameters="{}")

        vendorModelVM = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
                                               instrument_type="FxOption", parameters="{}")

        vendorModelLD = models.VendorModelRule(supplier="Lusid", model_name="simpleStatic",
                                               instrument_type="FxOption", parameters="{}")

        vendorModel = vendorModelTracs

        pricingContext = models.PricingContext(model_rules=[
            vendorModel])  # ,options = models.PricingOptions(allow_any_instruments_with_sec_uid_to_price_off_lookup=True)) # for LUSID VM
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

        weightedInstrumentList = [weightedInstrumentFXOpt_1y, weightedInstrumentFXOpt_2y,
                                  weightedInstrumentFXOpt_3y]

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
                # models.AggregateSpec(key='Analytic/default/NextEvent',      #Lusid only
                #                      op='Value'),
                # models.AggregateSpec(key='Analytic/default/NextEventType',      #Lusid only
                #                      op='Value'),
                # models.AggregateSpec(key='Analytic/default/HoldingCashflows',       #Lusid only
                #                      op='Value')
                # models.AggregateSpec(key='Analytic/default/MaturityDate',
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


        ####################################################

    def test_FX_OPT_aggregation_inline_weightedVM(self):
        # price simple fx opts..demonstrate sensible pvs.
        # can update dates etc
        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date

        end_date_1y = start_date.replace(year=start_date.year + 1)
        end_date_2y = start_date.replace(year=start_date.year + 2)
        end_date_3y = start_date.replace(year=start_date.year + 3)

        dom_amount = 100000000
        # Use mkt fwd to generate close to 0 PV? or use 5y and have over and under

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

        # Create a quote for the FX GBP/USD for 21/11/19
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

        vendorModel = models.VendorModelRule(supplier="VolMaster", model_name="VendorDefault",
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

        print(response)

    def test_FX_OPT_QPS_multiexpiry(self):

        trade_date = datetime.today().replace(tzinfo=pytz.utc)
        start_date = trade_date

        end_date_1y = start_date.replace(year=start_date.year + 1)

        dom_amount = 100000000

        fwd_FX_price_1y = self.start_GBPUSD_FX_price + self.GBPUSDpip_1y / 10000

        fgn_amount_1y = dom_amount * -fwd_FX_price_1y

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

        print(response)

        vendorModel = []
        vendorModel.append(models.VendorModelRule(supplier="RefinitivQps", model_name="VendorDefault",
                                                  instrument_type="FxOption", parameters="{}"))


        weightedInstrumentFXOpt_1y = models.WeightedInstrument(
            quantity=1, holding_identifier="myholding1y",
            instrument=instrument_definition_1y
        )


        weightedInstrumentList = [weightedInstrumentFXOpt_1y]

        for model in vendorModel:
            pricingContext = models.PricingContext(model_rules=[model])
            marketContext = models.MarketContext(
                options=models.MarketOptions(default_supplier=marketSupplier, default_scope=marketDataScope))

            RecipeId = models.ConfigurationRecipe(code="Recipe1", pricing=pricingContext, market=marketContext)

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
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/MaturityDate',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/NextEvent',
                                         op='Value'),
                    models.AggregateSpec(key='Analytic/default/NextEventType',
                                         op='Value')
                ]
            )
            inlineRequestFXOpt = models.InlineAggregationRequest(request=aggregationRequestResource,
                                                                 instruments=weightedInstrumentList)

            # Call LUSID to perform the aggregation

            response = self.aggregation_api.get_aggregation_of_weighted_instruments(marketDataScope,
                                                                                    inline_request=inlineRequestFXOpt)

            print(response)
