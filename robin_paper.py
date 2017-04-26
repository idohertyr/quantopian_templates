"""
This is a template algorithm on Quantopian for live trading.
"""

from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.filters.morningstar import Q1500US

# Possible imported classes for setting trading guards
from zipline.finance.asset_restrictions import (
    StaticRestrictions,
    HistoricalRestrictions,
    Restriction,
    RESTRICTION_STATES as states
)

 
def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))
     
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())
     
    # Create our dynamic stock selector.
    attach_pipeline(make_pipeline(), 'my_pipeline')

    #Trading Guards
    
    # set_asset_restrictions(security_lists.restrict_leveraged_etfs)
    # Prevent the algorithm from trading specific assets.
    # If an asset is restricted trading is stopped and an exception is thrown.
    # Use can_trade() to determine if an asset is restricted.
    # StaticRestrictions() can be used to restrict assets during the whole simulation.
    # HistoricalRestrictions can be used to group Restriction objects. 
    # set_long_only() - Needed for Robinhood

    # Prevents any short positions from being opened.
    set_long_only()

    # Limits the amount of trade the alogorithm can execute in one day
    set_max_order_count(50)

    # Limits the order size of any single order.
    set_max_order_size(symbol('AAPL'), max_shares=10, max_notional=1000.0)

    # Limits the absolute magnitude of any position held by the algorithm
    set_max_position_size(symbol('APPL'), max_shares=30, max_notional=2000.0)

    # Gets starting balance
    context.principle = get_environment('capital_base')

    # Keep track of last sale
    context.last_sale = None

    # Just a simple variable to demonstate `context.last_sale`,
    # `cash_settlement_date`, and `check_last_sale`
    context.trading_days = 0

    # Reference stocks by sid.
    context.appl = sid(24)

def make_pipeline():
    """
    A function to create our dynamic stock selector (pipeline). Documentation on
    pipeline can be found here: https://www.quantopian.com/help#pipeline-title
    """
    
    # Base universe set to the Q500US
    base_universe = Q1500US()

    # Factor of yesterday's close price.
    yesterday_close = USEquityPricing.close.latest
     
    pipe = Pipeline(
        screen = base_universe,
        columns = {
            'close': yesterday_close,
        }
    )
    return pipe
 
def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = pipeline_output('my_pipeline')
  
    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index
     
def my_assign_weights(context, data):
    """
    Assign weights to securities that we want to order.
    """
    pass
 
def my_rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """

    # Only trade when using robinhood
    if (get_environment('arena') == 'ROBINHOOD'):
        pass

    # Only trade when paper trading
    if (get_environment('arena') == 'live'):
        pass

    pass
 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass
 
def handle_data(context,data):
    """
    Called every minute.
    """

    # Checks if Account Fields have been provided by the broker.
    if (context.account.buying_power is None or context.account.buying_power < 1000):
        return
    else:
        print 'Account fields have been reported.'
        # Make transactions or calculate data.


        # For living trading only
        if (do_unsettled_funds_exist(context)):
            return

        if (cash_settlement_date(context)):
            log.info('Unsettled Cash Simlated')
        # Always use the can_trade function before a trade.
        elif data.can_trade(context.appl):
            # You can see the simulation in prgoress here.
            # On day 0, it will order 5 shares of AAPL
            # On day 1, it will order -1 shares and the proceeds
            # from the sale will be unsettled till day 4.
            # On day 4, you will be able to place another sale.
            if context.trading_days == 0:
                log.info("Day 0")
                order(context.aapl, 5)
            if context.trading_days == 1:
                log.info("Day 1")
                order(context.aapl, -1)
            if context.trading_days == 2:
                # Day 2 should not log.
                log.info("Day 2")
                order(context.aapl, -1)
            if context.trading_days == 4:
                log.info("Day 4")
                order(context.aapl, -1)

        context.trading_days += 1

        # `check_last_sale` is what `cash_settlement_date` needs in
        # order to work properly. Only for backtesting purposes!
        check_last_sale(context)

    pass

def do_unsettled_funds_exist(context):
    """
    For Robinhood users. In order to prevent you from attempting
    to trade on unsettled cash (settlement dates are T+3) from
    sale of proceeds. You can use this snippet of code which
    checks for whether or not you currently have unsettled funds

    To only be used for live trading!
    """
    if context.portfolio.cash != context.account.settled_cash:
        return True

def check_last_sale(context):
    """
    To be used at the end of each bar. This checks if there were
    any sales made and sets that to `context.last_sale`.
    `context.last_sale` is then used in `cash_settlement_date` to
    simulate a T+3 Cash Settlement date

    To only be used for backtesting!
    """
    open_orders = get_open_orders()
    most_recent_trade = []
    # If there are open orders check for the most recent sale
    if open_orders:
        for sec, order in open_orders.iteritems():
            for oo in order:
                if oo.amount < 0:
                    most_recent_trade.append(oo.created)
    if len(most_recent_trade) > 0:
        context.last_sale = max(most_recent_trade)

def cash_settlement_date(context):
    """
    This will simulate Robinhood's T+3 cash settlement. If the 
    most recent sale is less than 3 trading days from the current
    day, assume we have unsettled funds and exit

    To only be used for backtesting!
    """
    if context.last_sale and (get_datetime() - context.last_sale).days < 3:
        return True