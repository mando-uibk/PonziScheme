// Script to make chosen market full opacity
let chosen_market = js_vars.chosen_market
let market_head_id = 'market_head_'+ chosen_market
let market_payoff_id = 'market_payoff_' + chosen_market

document.getElementById(market_head_id).setAttribute('style', 'opacity: 1 !important')
document.getElementById(market_payoff_id).setAttribute('style', 'opacity: 1 !important')
