# quantopian_templates

### Templates for Quantopian


[Quantopian Help](https://www.quantopian.com/help)

#### Best Practices for a Fast Algorithm
* Access context as infrequently as possible.
* Bunch all of the algorithms data look ups:
  * data.history
  * data.current
  * data.can_trade
  * data.is_stale
* Only record data at the end of each day.
* Access account and portfolio data only when needed (calculated daily or on demand).
* Logging is limited to 2 logs per call of `initialize` and `handle_data`.

### Factors

#### 1. Slippage Models
Slippage must be defined in the initalize method. If you do not specify a slippage model it defaults to:
```python
# You can take up to 2.5% of the minute's trading volume
VolumeShareSlippage(volume_limit=0.25, price_impact=0.1)
```
To set **slippage**, use:
```python
# set_slippage can take FixedSlippage, VolumeShareSlippage, or a custom slippage model.
set_slippage() <-- slippage.FixedSlippage or slippage.VolumeShareSlippage
```
*slippage.VolumeShareSlippage(volume_limit, price_impact)*

**volume_limit**: limits the proportion of volume that your order can take up per bar.
<br />
**price_impact**: constant (defaults to 0.1) defines how large of an impact your order will
have on the backtesters price calculation.

*slippage.FixedSlippage(spread)*

**spread**: Typical bid/ask spread
<br />



#### 2. Commission Models
* You can set commission by trade or share
```python
set_commission() <-- commission.PerShare or commission.PerTrade
```

#### 3. Trading Guards