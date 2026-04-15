# CurrencyNotification

### plan  

1.set Telegeam token & chatid
2. fetch currency history if 3 years,maybe fetch from yfinance
3. define const currencies, AUD2CNY, GBP2CNY, which used to fetch. 
4. calculate averages of every month, and put averages into an array and sort them by value.
5. if the currency like AUD2CNY price is greater than maximum in the array or only greater than 3rd max in the array. send msg to telegram
6. if the currency price is smaller than minimum or only smaller than 3rn minium in the array. send msg to telegram.


