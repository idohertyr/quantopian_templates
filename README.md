# quantopian_templates
Templates for Quantopian

[##### Best Practices For a Fast Algorithm](https://www.quantopian.com/help)
* Bunch all of the algorithms data look ups
 * data.history
 * data.current
 * data.can_trade
 * data.is_stale
* Only record data daily
* Access account and portfolio data only when needed
 * Account information is calculated daily or on demand
* Logging is rate-limited, 2 logs per call of initialize and handle_data
* Set a custom benchmark with set_benchmark(symb)
